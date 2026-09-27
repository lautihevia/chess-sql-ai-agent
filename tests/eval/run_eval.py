"""Runner de evaluación del agente (T032).

Corre el agente sobre el dataset (`dataset.py`), calcula las métricas de
`docs/quality/evaluation.md` y las imprime. Si LangSmith está configurado, además registra un
experimento formal (dataset + evaluadores) para dejar evidencia comparable entre versiones.

Uso:
    uv run python -m tests.eval.run_eval            # eval local + experimento en LangSmith
    uv run python -m tests.eval.run_eval --local    # solo métricas locales (sin subir)
"""

from __future__ import annotations

import sys
import time

from chess_agent.config import configure_langsmith, get_settings
from chess_agent.graph import run
from tests.eval.dataset import CASES, _gold_value, score_case


def evaluate_local() -> None:
    """Corre el agente sobre todos los casos e imprime métricas agregadas."""
    configure_langsmith()
    por_check: dict[str, list[bool]] = {}
    latencias: list[float] = []
    fallos: list[str] = []

    print(f"Evaluando {len(CASES)} casos…\n")
    for case in CASES:
        t0 = time.perf_counter()
        state = run(case.pregunta)
        latencias.append(time.perf_counter() - t0)
        checks = score_case(case, state)
        estado_ok = all(v for v in checks.values() if v is not None)
        marca = "✓" if estado_ok else "✗"
        print(f"  {marca} [{case.categoria:7s}] {case.id}")
        if not estado_ok:
            fallos.append(f"{case.id}: {checks}")
        for key, val in checks.items():
            if val is not None:
                por_check.setdefault(key, []).append(val)

    def pct(vals: list[bool]) -> str:
        return f"{100 * sum(vals) / len(vals):.0f}% ({sum(vals)}/{len(vals)})"

    nombres = {
        "routing": "Exactitud de enrutamiento",
        "sql": "Exactitud SQL",
        "rag_grounded": "Fidelidad RAG (con cita)",
        "refusal": "Tasa de rehúso correcto",
    }
    print("\n=== Métricas ===")
    for key, vals in por_check.items():
        print(f"  {nombres.get(key, key):32s}: {pct(vals)}")
    print(f"  {'Latencia media':32s}: {sum(latencias) / len(latencias):.2f} s")

    if fallos:
        print("\n=== Casos con checks fallidos ===")
        for f in fallos:
            print("  -", f)


def evaluate_langsmith() -> None:
    """Registra un experimento en LangSmith (dataset + evaluadores)."""
    if not get_settings().langsmith_tracing:
        print("\nLangSmith desactivado; se omite el experimento.")
        return
    configure_langsmith()
    from langsmith import Client, evaluate

    client = Client()
    dataset_name = "chess-agent-eval"

    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception:
        dataset = client.create_dataset(dataset_name=dataset_name)
        for case in CASES:
            gold = _gold_value(case.gold_sql) if case.gold_sql else None
            client.create_example(
                inputs={"pregunta": case.pregunta},
                outputs={
                    "ruta_esperada": case.ruta_esperada,
                    "categoria": case.categoria,
                    "gold_value": None if gold is None else str(gold),
                    "expect_source": case.expect_source,
                    "must_refuse": case.must_refuse,
                },
                dataset_id=dataset.id,
                metadata={"id": case.id, "idioma": case.idioma},
            )

    def target(inputs: dict) -> dict:
        state = run(inputs["pregunta"])
        return {
            "ruta": state.get("ruta"),
            "respuesta": state.get("respuesta") or "",
            "fundamentada": state.get("fundamentada"),
            "fuentes": state.get("fuentes") or [],
        }

    def ev_routing(run, example) -> dict:  # noqa: A002 (firma de LangSmith)
        ok = run.outputs.get("ruta") == example.outputs.get("ruta_esperada")
        return {"key": "routing", "score": int(ok)}

    def ev_correct(run, example) -> dict:  # noqa: A002
        cat = example.outputs.get("categoria")
        out = run.outputs
        if cat in ("sql", "mixta"):
            gv = example.outputs.get("gold_value")
            return {"key": "sql_correct", "score": int(bool(gv) and gv in out.get("respuesta", ""))}
        if cat == "rag":
            src = example.outputs.get("expect_source")
            fu = " ".join(out.get("fuentes") or []).lower()
            ok = bool(out.get("fundamentada")) and (src is None or src in fu)
            return {"key": "rag_grounded", "score": int(ok)}
        if cat == "refusal":
            return {"key": "refusal_correct", "score": int(out.get("fundamentada") is False)}
        return {"key": "correct", "score": 1}

    evaluate(
        target,
        data=dataset_name,
        evaluators=[ev_routing, ev_correct],
        experiment_prefix="chess-agent",
        client=client,
    )
    print("\nExperimento registrado en LangSmith (dataset 'chess-agent-eval').")


if __name__ == "__main__":
    evaluate_local()
    if "--local" not in sys.argv:
        try:
            evaluate_langsmith()
        except Exception as exc:  # no romper la eval local si la API difiere
            print(f"\n[aviso] No se pudo registrar el experimento en LangSmith: {exc}")
