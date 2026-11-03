"""T09: EDA reproducible de la cohorte T08, con agregados y cuatro figuras."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from acquire_meituan import REVISION, verify_file
from prepare_meituan import DEFAULT_OUTPUT as DEFAULT_PROCESSED, file_hash
from delivery_ml.exploration import TARGET, summarize_orders


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "reports" / "meituan" / REVISION / "t09"
FIGURES = ["duracion.png", "contexto_utc.png", "fechas_utc.png", "correlaciones.png"]


def save_figure(fig, output: Path, filename: str) -> None:
    fig.savefig(output / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_eda(orders: pd.DataFrame, report: dict, output: Path) -> None:
    target = orders[TARGET]
    p99 = report["duration_minutes"]["p99"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    axes[0].hist(target, bins=80, color="#27648c", log=True)
    axes[0].set(title="Duración completa: se conserva la cola", xlabel="Minutos", ylabel="Pedidos (escala log)")
    axes[1].hist(target.loc[target.le(p99)], bins=50, color="#278579")
    excluded = report["tail_diagnostics"]["above_p99"]
    axes[1].set(title=f"Detalle hasta P99: {p99:.2f} min", xlabel="Minutos", ylabel="Pedidos")
    fig.suptitle(f"n={len(orders):,}; panel derecho omite visualmente {excluded:,} pedidos; dataset intacto")
    save_figure(fig, output, FIGURES[0])

    fig, axes = plt.subplots(2, 2, figsize=(12, 7), layout="constrained")
    for column, (key, field, label) in enumerate([
        ("by_hour_utc", "request_hour_utc", "Hora de solicitud (UTC)"),
        ("by_weekday_utc", "request_weekday_utc", "Día de solicitud (UTC; lunes=0)"),
    ]):
        groups = pd.DataFrame(report[key])
        axes[0, column].bar(groups[field], groups["count"], color="#27648c")
        axes[0, column].set(xlabel=label, ylabel="Pedidos observados")
        axes[1, column].plot(groups[field], groups["median"], "o-", color="#278579", label="Mediana")
        axes[1, column].fill_between(groups[field], groups["p10"], groups["p90"], color="#278579", alpha=0.2, label="P10–P90 observado")
        axes[1, column].set(xlabel=label, ylabel="Duración (minutos)")
        axes[1, column].legend()
    fig.suptitle("Contexto UTC: conteos sin normalizar por exposición; no equivalen a demanda local")
    save_figure(fig, output, FIGURES[1])

    days = pd.DataFrame(report["by_date_utc"])
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), layout="constrained", sharex=True)
    axes[0].bar(days["request_date_utc"], days["count"], color="#27648c")
    axes[0].set(ylabel="Pedidos", title="Cobertura por fecha de creación UTC (bordes potencialmente parciales)")
    axes[1].plot(days["request_date_utc"], days["median"], "o-", color="#278579")
    axes[1].set(xlabel="Fecha UTC", ylabel="Mediana de duración (min)")
    axes[1].tick_params(axis="x", rotation=30)
    save_figure(fig, output, FIGURES[2])

    matrix = pd.DataFrame(report["spearman_raw_coordinates"]).astype(float)
    labels = [name.replace("_raw", "") for name in matrix.columns]
    fig, axis = plt.subplots(figsize=(8, 6), layout="constrained")
    heat = axis.imshow(matrix, vmin=-1, vmax=1, cmap="RdBu_r")
    axis.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    axis.set_yticks(range(len(labels)), labels)
    for row in range(len(labels)):
        for column in range(len(labels)):
            axis.text(column, row, f"{matrix.iloc[row, column]:.2f}", ha="center", va="center", fontsize=9)
    fig.colorbar(heat, ax=axis, label="Spearman (rangos)")
    axis.set_title("Coordenadas originales: asociación descriptiva, sin inferir kilómetros\nIDs, eventos futuros y contexto cíclico excluidos")
    save_figure(fig, output, FIGURES[3])


def findings(report: dict) -> list:
    duration = report["duration_minutes"]
    tail = report["tail_diagnostics"]
    dates = report["by_date_utc"]
    hours = report["by_hour_utc"]
    peak = max(hours, key=lambda group: group["count"])
    lower = min(hours, key=lambda group: group["median"])
    upper = max(hours, key=lambda group: group["median"])
    return [
        f"Cohorte: {report['rows']:,} pedidos; {sum(report['quality']['missing_by_column'].values())} celdas ausentes y {report['quality']['duplicate_orders']} IDs de pedido duplicados.",
        f"Duración media {duration['mean']:.2f} min, mediana {duration['p50']:.2f}, P95 {duration['p95']:.2f}, P99 {duration['p99']:.2f} y máximo {duration['max']:.2f}.",
        f"Cola superior: {tail['above_upper_fence']:,} pedidos por encima de {tail['upper_fence_minutes']:.2f} min (Q3+1.5*IQR). Es señal de revisión, no error confirmado ni regla comercial; no se eliminan filas.",
        f"Mayor volumen observado a las {peak['request_hour_utc']:02d}:00 UTC: {peak['count']:,} pedidos. Son pedidos de la cohorte, no toda la demanda de la plataforma.",
        f"Medianas por hora entre {lower['median']:.2f} min a las {lower['request_hour_utc']:02d}:00 UTC (n={lower['count']:,}) y {upper['median']:.2f} a las {upper['request_hour_utc']:02d}:00 UTC (n={upper['count']:,}); asociación sin inferencia causal.",
        f"Cobertura UTC: {dates[0]['request_date_utc']} a {dates[-1]['request_date_utc']} ({len(dates)} fechas); los bordes pueden ser parciales. No demuestra estacionalidad ni generalización fuera del período.",
        f"Fechas observadas por día semanal (lunes=0): {report['dates_per_weekday_utc']}. Exposición desigual: los conteos brutos semanales no demuestran mayor demanda por día.",
        "Las relaciones con coordenadas se muestran en rangos originales; no confirman unidades geográficas, distancia vial ni utilidad predictiva.",
        "Sesgo de selección: solo pedidos inmediatos completados, inequívocos y con cotización estable. Reservas y entregas no completadas quedan fuera; no se extrapola a ellas.",
        "Origen chino, período corto y sin vehículo validado: no acredita tiempos de El Salvador, bicicleta/moto ni rendimiento de un modelo. No se seleccionan features ni se ajustan umbrales/modelos con este EDA.",
    ]


def explore(processed: Path, output: Path) -> dict:
    manifest_path = processed / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    csv_path = processed / "orders.csv"
    integrity = verify_file(csv_path, manifest["bytes"], manifest["sha256"])
    if manifest["source_revision"] != REVISION:
        raise ValueError("Revisión de datos distinta de la aprobada")
    orders = pd.read_csv(csv_path, dtype={"order_id": "string", "source_waybill_id": "string"})
    if len(orders) != manifest["rows"] or list(orders.columns) != manifest["columns"]:
        raise ValueError("La tabla no coincide con el manifiesto T08")
    report = summarize_orders(orders)
    report["provenance"] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_revision": REVISION, "processed_sha256": integrity["sha256"],
        "manifest_sha256": file_hash(manifest_path),
        "implementation": {name: file_hash(path) for name, path in {
            "exploration.py": ROOT / "ml/src/delivery_ml/exploration.py", "explore_meituan.py": Path(__file__),
        }.items()},
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "matplotlib": matplotlib.__version__},
    }
    report["findings"] = findings(report)
    report["figures"] = FIGURES
    # No permitir que --output escriba sobre la entrada preparada.
    output = output.resolve()
    if output == processed.resolve() or output in processed.resolve().parents or processed.resolve() in output.parents:
        raise ValueError("La salida del EDA debe estar separada del dataset")
    output.mkdir(parents=True, exist_ok=True)
    plot_eda(orders, report, output)
    (output / "t09_eda.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    markdown = "# T09 — EDA de Meituan\n\n" + "\n\n".join(report["findings"])
    markdown += "\n\n## Figuras\n\n" + "\n\n".join(f"![{name}]({name})" for name in FIGURES)
    markdown += "\n\n## Reproducción\n\n`uv run --locked python ml/data/explore_meituan.py`\n\n"
    markdown += f"CSV SHA-256: `{integrity['sha256']}`. Detalle, calidad y procedencia en `t09_eda.json`.\n\n"
    markdown += "La vista hasta P99 omite visualmente la cola; el histograma completo y el CSV la conservan. P10–P90 describe dispersión, no un intervalo de confianza.\n\n"
    markdown += "Tukey: [NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/boxplot.htm). Correlaciones: [Pandas](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html).\n"
    (output / "t09_eda.md").write_text(markdown, encoding="utf-8")
    verify_file(csv_path, manifest["bytes"], manifest["sha256"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed", type=Path, default=DEFAULT_PROCESSED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = explore(args.processed.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"EDA no completado: {error}\n")
    print(f"EDA: {args.output}; {report['rows']:,} pedidos; {len(FIGURES)} figuras")
    for item in report["findings"]:
        print(item)


if __name__ == "__main__":
    main()
