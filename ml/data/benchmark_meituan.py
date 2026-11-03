"""T12: mediciones locales repetidas con equivalencia verificada por ejecución."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
import tempfile
from time import perf_counter

from acquire_meituan import CSV_NAME, DEFAULT_OUTPUT as DEFAULT_DATASET, EXPECTED, REVISION, verify_file


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "data/processed/meituan" / REVISION / "t08-v1"
AUDIT = ROOT / "data/reports/meituan" / REVISION / "t07_audit.json"
DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t12"
ENGINES = ("pandas", "dask", "spark")


def worker(engine: str, source: Path, reference: Path, output: Path) -> None:
    """Un proceso nuevo por muestra; incluye todas las acciones del pipeline."""
    start = perf_counter()
    import pandas as pd
    from pandas.testing import assert_frame_equal
    from prepare_meituan import file_hash
    spark = None
    if engine == "pandas":
        from delivery_ml.preparation import prepare_orders
    elif engine == "dask":
        import dask
        import dask.dataframe as dd
        from delivery_ml.preparation_dask import prepare_orders_dask
    else:
        from delivery_ml.preparation_spark import local_spark, prepare_orders_spark
        spark = local_spark()
    startup = perf_counter() - start
    try:
        start = perf_counter()
        if engine == "pandas":
            raw = pd.read_csv(source, dtype={"order_id": "string", "waybill_id": "string"})
            partitions = 1
            result = prepare_orders(raw)
        elif engine == "dask":
            with dask.config.set({"scheduler": "threads", "num_workers": 2, "dataframe.convert-string": False}):
                raw = dd.read_csv(str(source), blocksize=16 * 1024 * 1024,
                                  dtype={"order_id": "string", "waybill_id": "string"})
                partitions = raw.npartitions
                result = prepare_orders_dask(raw).compute()
        else:
            raw = spark.read.options(header=True, inferSchema=False, mode="FAILFAST").csv(str(source))
            partitions = raw.rdd.getNumPartitions()
            prepared = prepare_orders_spark(raw)
            result = pd.DataFrame.from_records(prepared.collect(), columns=prepared.columns)
        result = result.sort_values("order_id", kind="stable").reset_index(drop=True)
        for name in ("order_id", "source_waybill_id"):
            result[name] = result[name].astype("string[python]")
        pipeline = perf_counter() - start

        # Verificar y serializar queda fuera del tiempo comparable del pipeline.
        start = perf_counter()
        expected = pd.read_csv(reference / "orders.csv", float_precision="round_trip",
                               dtype={"order_id": "string[python]", "source_waybill_id": "string[python]"})
        assert_frame_equal(result, expected, check_dtype=False, check_exact=True)
        manifest = json.loads((reference / "manifest.json").read_text())
        with tempfile.TemporaryDirectory(prefix="delivery-t12-csv-") as temporary:
            csv = Path(temporary) / "orders.csv"
            result.to_csv(csv, index=False, lineterminator="\n")
            digest = file_hash(csv)
        if digest != manifest["sha256"]:
            raise ValueError("El resultado no coincide con el hash de la referencia")
        validation = perf_counter() - start
        sample = {
            "engine": engine, "startup_seconds": startup, "pipeline_seconds": pipeline,
            "startup_pipeline_seconds": startup + pipeline, "validation_seconds": validation,
            "rows": len(result), "columns": len(result.columns), "partitions": partitions,
            "equivalent": True, "normalized_csv_sha256": digest,
        }
        output.write_text(json.dumps(sample, indent=2) + "\n")
    finally:
        if spark is not None:
            spark.stop()


def machine_context() -> dict:
    def read_optional(name):
        path = Path(name)
        return path.read_text().strip() if path.is_file() else None
    model = platform.processor()
    cpuinfo = read_optional("/proc/cpuinfo")
    if cpuinfo:
        model = next((line.split(":", 1)[1].strip() for line in cpuinfo.splitlines() if line.startswith("model name")), model)
    ram = None
    if hasattr(os, "sysconf"):
        ram = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return {
        "os": platform.system(), "kernel": platform.release(), "architecture": platform.machine(),
        "cpu_model": model, "logical_cpus": os.cpu_count(),
        "affinity_cpus": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "ram_bytes": ram, "cgroup_memory_max": read_optional("/sys/fs/cgroup/memory.max"),
        "cgroup_cpu_max": read_optional("/sys/fs/cgroup/cpu.max"),
        "python": platform.python_version(),
        "versions": {name: importlib.metadata.version(name) for name in ("pandas", "dask", "pyspark", "numpy", "pyarrow")},
        "java_version_output": subprocess.run(["java", "-version"], capture_output=True, text=True, check=True).stderr.strip(),
    }


def write_artifacts(report: dict, output: Path) -> None:
    import csv
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    summary = report["summary"]
    lines = ["# T12 — Comparación local de motores", "",
             "Tiempos en segundos; medianas de procesos nuevos. Equivalencia comprobada en cada ejecución.", "",
             "| Motor | Arranque | Pipeline mediana | Pipeline mínimo–máximo | Arranque + pipeline |",
             "|---|---:|---:|---:|---:|"]
    for name in ENGINES:
        item = summary[name]
        lines.append(f"| {name} | {item['startup_median_seconds']:.3f} | {item['pipeline_median_seconds']:.3f} | {item['pipeline_min_seconds']:.3f}–{item['pipeline_max_seconds']:.3f} | {item['startup_pipeline_median_seconds']:.3f} |")
    lines += ["", "## Interpretación y límites", "", *report["conclusions"], "",
              "## Entorno", "", "```json", json.dumps(report["signature"]["machine"], ensure_ascii=False, indent=2), "```", "",
              "![Medianas y rango observado](t12_tiempos.png)", "",
              "Reproducir: `uv run --locked python ml/data/benchmark_meituan.py`.", "",
              "Muestras, hashes y protocolo completos en `t12_benchmark.json` y `t12_muestras.csv`.", "",
              "Métodos: [perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter), [ejecución de Spark](https://spark.apache.org/docs/3.5.7/rdd-programming-guide.html#rdd-operations)."]
    (output / "t12_benchmark.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (output / "t12_muestras.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(report["samples"][0]))
        writer.writeheader()
        writer.writerows(report["samples"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    centers = [summary[name]["pipeline_median_seconds"] for name in ENGINES]
    errors = [[centers[i] - summary[name]["pipeline_min_seconds"] for i, name in enumerate(ENGINES)],
              [summary[name]["pipeline_max_seconds"] - centers[i] for i, name in enumerate(ENGINES)]]
    axes[0].bar(ENGINES, centers, yerr=errors, capsize=5, color=["#27648c", "#278579", "#b96c28"])
    axes[0].set(title="Pipeline: mediana y rango observado", ylabel="Segundos; menor es más rápido")
    axes[1].bar(ENGINES, [summary[name]["startup_pipeline_median_seconds"] for name in ENGINES], color=["#27648c", "#278579", "#b96c28"])
    axes[1].set(title="Arranque + pipeline: mediana", ylabel="Segundos")
    fig.suptitle(f"Misma fuente y reglas; {report['repeats']} muestras por motor; el rango no es un intervalo de confianza")
    fig.savefig(output / "t12_tiempos.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    (output / "t12_benchmark.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def benchmark(output: Path, repeats: int, reuse: bool) -> dict:
    from prepare_meituan import prepare, file_hash
    if repeats < 1:
        raise ValueError("Se requiere al menos una repetición; el experimento usa tres por defecto")
    for protected in (DEFAULT_DATASET, REFERENCE):
        if output == protected or output in protected.parents or protected in output.parents:
            raise ValueError("El benchmark debe escribirse separado de los datasets")
    source = DEFAULT_DATASET / CSV_NAME
    integrity = verify_file(source, *EXPECTED[CSV_NAME])
    manifest = prepare(DEFAULT_DATASET, AUDIT, REFERENCE)
    paths = [Path(__file__), ROOT / "uv.lock", ROOT / "pyproject.toml", ROOT / "ml/data/prepare_meituan.py"]
    paths += [ROOT / "ml/src/delivery_ml" / name for name in ("preparation.py", "preparation_dask.py", "preparation_spark.py")]
    signature = {
        "source_sha256": integrity["sha256"], "reference_sha256": manifest["sha256"],
        "reference_manifest_sha256": file_hash(REFERENCE / "manifest.json"), "audit_sha256": file_hash(AUDIT),
        "files": {str(path.relative_to(ROOT)): file_hash(path) for path in paths}, "machine": machine_context(),
    }
    previous = output / "t12_benchmark.json"
    if reuse and previous.is_file():
        report = json.loads(previous.read_text())
        if report["signature"] == signature and report["repeats"] == repeats:
            print(f"Se reutiliza medición vigente de {report['created_at_utc']}; no es una medición nueva.")
            write_artifacts(report, output)
            return report
    samples = []
    with tempfile.TemporaryDirectory(prefix="delivery-t12-workers-") as temporary:
        for round_index in range(repeats):
            order = ENGINES[round_index % 3:] + ENGINES[:round_index % 3]
            for position, engine in enumerate(order):
                print(f"Ronda {round_index+1}/{repeats}: {engine}", flush=True)
                sample_path = Path(temporary) / "sample.json"
                start = perf_counter()
                child = subprocess.run([sys.executable, str(Path(__file__)), "--worker", engine,
                                        "--sample-output", str(sample_path)], capture_output=True, text=True)
                wall = perf_counter() - start
                if child.returncode:
                    raise RuntimeError(f"Falló {engine}:\n{child.stderr}\n{child.stdout}")
                sample = json.loads(sample_path.read_text())
                if not sample["equivalent"] or sample["normalized_csv_sha256"] != manifest["sha256"]:
                    raise ValueError("Muestra sin equivalencia; no se acepta el benchmark")
                sample.update(round=round_index+1, position=position+1, process_wall_seconds=wall)
                samples.append(sample)
                print(f"  pipeline {sample['pipeline_seconds']:.3f}s; resultado equivalente", flush=True)
    summary = {}
    for engine in ENGINES:
        values = [sample for sample in samples if sample["engine"] == engine]
        times = [sample["pipeline_seconds"] for sample in values]
        summary[engine] = {
            "samples": len(values), "pipeline_median_seconds": median(times),
            "pipeline_min_seconds": min(times), "pipeline_max_seconds": max(times),
            "startup_median_seconds": median(sample["startup_seconds"] for sample in values),
            "startup_pipeline_median_seconds": median(sample["startup_pipeline_seconds"] for sample in values),
        }
    fastest = min(ENGINES, key=lambda name: summary[name]["pipeline_median_seconds"])
    report = {
        "task": "T12", "created_at_utc": datetime.now(timezone.utc).isoformat(), "signature": signature,
        "source_bytes": integrity["bytes"], "source_rows": json.loads(AUDIT.read_text())["raw"]["rows"],
        "result_rows": manifest["rows"], "repeats": repeats, "samples": samples, "summary": summary,
        "conclusions": [
            f"Menor mediana de pipeline observada: {fastest}, {summary[fastest]['pipeline_median_seconds']:.3f} s; solo aplica a este dataset, equipo y configuración.",
            "Mismas reglas T08 y datos originales; todas las salidas comparadas exactamente y con hash de CSV normalizado idéntico.",
            "Pipeline incluye lectura, validaciones, agrupación, filtrado, derivación UTC, materialización y ordenación común. compute/collect y sus acciones se ejecutan dentro del cronómetro.",
            "Arranque mide imports del motor y creación de sesión Spark. Comparación, escritura CSV de verificación y cierre quedan fuera del pipeline; process_wall_seconds incluye todo el subproceso.",
            "Procesos nuevos por muestra; orden rotativo. Sin persist/cache explícito de Dask/Spark, sin descartar calentamiento y sin vaciar la caché del sistema operativo. JIT, caché de archivos y carga del equipo pueden influir.",
            "Dask y Spark usan dos hilos y bloques de 16 MiB, con siete/ocho particiones reales; Spark usa cuatro particiones de shuffle. No se iguala el algoritmo interno ni se fija afinidad de CPU.",
            "Se comparan implementaciones locales equivalentes, no escalabilidad distribuida ni precisión ML. La salida completa se reúne en memoria. Tres muestras no son una prueba estadística de superioridad general.",
        ],
    }
    verify_file(source, *EXPECTED[CSV_NAME])
    verify_file(REFERENCE / "orders.csv", manifest["bytes"], manifest["sha256"])
    output.mkdir(parents=True, exist_ok=True)
    write_artifacts(report, output)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--reuse", action="store_true", help="Mostrar medición previa solo si coinciden código, datos y entorno")
    parser.add_argument("--worker", choices=ENGINES, help=argparse.SUPPRESS)
    parser.add_argument("--sample-output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.sample_output is None:
            parser.error("El worker requiere archivo de muestra")
        worker(args.worker, DEFAULT_DATASET / CSV_NAME, REFERENCE, args.sample_output)
        return
    report = benchmark(args.output.resolve(), args.repeats, args.reuse)
    for name, item in report["summary"].items():
        print(f"{name}: mediana pipeline {item['pipeline_median_seconds']:.3f}s; arranque+pipeline {item['startup_pipeline_median_seconds']:.3f}s")
    print(f"Informe: {args.output}")


if __name__ == "__main__":
    main()
