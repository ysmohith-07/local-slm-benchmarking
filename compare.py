import pandas as pd
import os

def compare():
    # ── Load both CSVs ────────────────────────────────────────────────────
    base  = pd.read_csv("results/benchmark_results.csv")
    quant = pd.read_csv("results/quantized_benchmark_results.csv")

    # Keep only base models in base CSV (filter out quantized if mixed)
    base_model_names  = ["llama3.2:3b", "phi3.5", "mistral"]
    quant_model_names = [
        "llama3.2:3b-instruct-q4_K_M",
        "phi3.5:3.8b-mini-instruct-q5_K_M",
        "mistral:7b-instruct-q4_K_M",
    ]
    base  = base[base["model"].isin(base_model_names)]
    quant = quant[quant["model"].isin(quant_model_names)]

    # ── Group by model and calculate averages ─────────────────────────────
    base_stats = base.groupby("model").agg({
        "response_time_s":  "mean",
        "words_per_second": "mean",
        "memory_mb":        "mean",
        "word_count":       "mean",
    }).round(3)

    quant_stats = quant.groupby("model").agg({
        "response_time_s":  "mean",
        "words_per_second": "mean",
        "memory_mb":        "mean",
        "word_count":       "mean",
    }).round(3)

    print("\n=== BASE MODELS ===")
    print(base_stats.to_string())

    print("\n=== QUANTIZED MODELS ===")
    print(quant_stats.to_string())

    # ── Calculate latency improvement per model pair ──────────────────────
    print("\n=== IMPROVEMENT SUMMARY ===")

    pairs = [
        ("llama3.2:3b",  "llama3.2:3b-instruct-q4_K_M"),
        ("phi3.5",       "phi3.5:3.8b-mini-instruct-q5_K_M"),
        ("mistral",      "mistral:7b-instruct-q4_K_M"),
    ]

    summary_rows = []
    for base_name, quant_name in pairs:
        if base_name not in base_stats.index or quant_name not in quant_stats.index:
            print(f"  Skipping {base_name} — data missing")
            continue

        b = base_stats.loc[base_name]
        q = quant_stats.loc[quant_name]

        time_change = ((q["response_time_s"] - b["response_time_s"]) / b["response_time_s"]) * 100
        wps_change  = ((q["words_per_second"] - b["words_per_second"]) / b["words_per_second"]) * 100
        mem_change  = ((q["memory_mb"] - b["memory_mb"]) / b["memory_mb"]) * 100 if b["memory_mb"] != 0 else 0

        direction = "faster" if time_change < 0 else "slower"
        print(f"\n  {base_name}  →  {quant_name}")
        print(f"    Response time : {b['response_time_s']:.3f}s  →  {q['response_time_s']:.3f}s  ({time_change:+.1f}%  {direction})")
        print(f"    Words/second  : {b['words_per_second']:.1f}   →  {q['words_per_second']:.1f}   ({wps_change:+.1f}%)")
        print(f"    Memory delta  : {b['memory_mb']:.2f}MB →  {q['memory_mb']:.2f}MB  ({mem_change:+.1f}%)")

        summary_rows.append({
            "base_model":        base_name,
            "quant_model":       quant_name,
            "base_time_s":       b["response_time_s"],
            "quant_time_s":      q["response_time_s"],
            "time_change_pct":   round(time_change, 2),
            "base_wps":          b["words_per_second"],
            "quant_wps":         q["words_per_second"],
            "wps_change_pct":    round(wps_change, 2),
            "base_memory_mb":    b["memory_mb"],
            "quant_memory_mb":   q["memory_mb"],
            "memory_change_pct": round(mem_change, 2),
        })

    # ── Save comparison summary ───────────────────────────────────────────
    os.makedirs("results", exist_ok=True)
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv("results/comparison_summary.csv", index=False)
    print("\nComparison saved to results/comparison_summary.csv")


if __name__ == "__main__":
    compare()