
import time
import tracemalloc
from pathlib import Path

import pandas as pd

from src.validation import validate
from src.analytics import build_metrics
from src.anomaly_detection import detect
from src.identity_stitching import run_identity_stitching
from src.evaluate_anomalies import evaluate_anomalies


OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def measure_task(task_name, task_function):
    """Measure execution time and Python memory usage."""

    print(f"\nRunning: {task_name}")

    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        task_function()
        status = "SUCCESS"
        error_message = ""

    except Exception as error:
        status = "FAILED"
        error_message = str(error)

    end_time = time.perf_counter()

    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    execution_time = end_time - start_time

    result = {
        "module": task_name,
        "execution_time_seconds": round(execution_time, 4),
        "peak_memory_mb": round(peak_memory / (1024 * 1024), 4),
        "status": status,
        "error": error_message
    }

    print(f"Status: {status}")
    print(f"Execution time: {execution_time:.4f} seconds")
    print(f"Peak Python memory: {peak_memory / (1024 * 1024):.4f} MB")

    if error_message:
        print(f"Error: {error_message}")

    return result


def run_benchmark():
    print("=" * 55)
    print("JOURNEYIQ PERFORMANCE BENCHMARK")
    print("=" * 55)

    tasks = [
        ("Data Validation", validate),
        ("Funnel and Channel Analytics", build_metrics),
        ("Anomaly Detection", detect),
        ("Identity Stitching", run_identity_stitching),
        ("Anomaly Evaluation", evaluate_anomalies)
    ]

    results = []
    total_start = time.perf_counter()

    for task_name, task_function in tasks:
        result = measure_task(task_name, task_function)
        results.append(result)

        if result["status"] == "FAILED":
            print("\nBenchmark stopped because a module failed.")
            break

    total_time = time.perf_counter() - total_start

    results_df = pd.DataFrame(results)

    output_file = OUTPUT_DIR / "benchmark_results.csv"
    results_df.to_csv(output_file, index=False)

    print("\n" + "=" * 55)
    print("BENCHMARK SUMMARY")
    print("=" * 55)

    print(results_df.to_string(index=False))
    print(f"\nTotal pipeline execution time: {total_time:.4f} seconds")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    run_benchmark()
