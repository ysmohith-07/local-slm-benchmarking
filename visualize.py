import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_charts():
    os.makedirs("results", exist_ok=True)

    # ── Load data ─────────────────────────────────────────────────────────
    base  = pd.read_csv("results/benchmark_results.csv")
    quant = pd.read_csv("results/quantized_benchmark_results.csv")

    # ── Filter to only the correct models in each file ────────────────────
    base_model_names  = ["llama3.2:3b", "phi3.5", "mistral"]
    quant_model_names = [
        "llama3.2:3b-instruct-q4_K_M",
        "phi3.5:3.8b-mini-instruct-q5_K_M",
        "mistral:7b-instruct-q4_K_M",
    ]

    base  = base[base["model"].isin(base_model_names)].copy()
    quant = quant[quant["model"].isin(quant_model_names)].copy()

    # ── Friendly short names ──────────────────────────────────────────────
    name_map = {
        "llama3.2:3b":                       "Llama 3.2",
        "phi3.5":                            "Phi 3.5",
        "mistral":                           "Mistral 7B",
        "llama3.2:3b-instruct-q4_K_M":      "Llama 3.2",
        "phi3.5:3.8b-mini-instruct-q5_K_M": "Phi 3.5",
        "mistral:7b-instruct-q4_K_M":       "Mistral 7B",
    }

    base["model_label"]  = base["model"].map(name_map).fillna(base["model"])
    quant["model_label"] = quant["model"].map(name_map).fillna(quant["model"])

    base["type"]  = "Base"
    quant["type"] = "Quantized"

    combined = pd.concat([base, quant], ignore_index=True)

    # Shared model labels in correct order
    model_labels = ["Llama 3.2", "Phi 3.5", "Mistral 7B"]

    COLORS_BASE  = "#2E5F8A"
    COLORS_QUANT = "#E07B39"

    width = 0.35
    x = range(len(model_labels))

    # ── Helper to get ordered values ──────────────────────────────────────
    def get_ordered(df, col):
        grouped = df.groupby("model_label")[col].mean()
        return [grouped.get(m, 0) for m in model_labels]

    # ── Chart 1: Average Latency ──────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))

    base_vals  = get_ordered(base,  "response_time_s")
    quant_vals = get_ordered(quant, "response_time_s")

    bars1 = ax.bar([i - width/2 for i in x], base_vals,  width, label="Base",      color=COLORS_BASE)
    bars2 = ax.bar([i + width/2 for i in x], quant_vals, width, label="Quantized", color=COLORS_QUANT)

    ax.set_title("Average Response Latency by Model (Base vs Quantized)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Latency (seconds)")
    ax.set_xlabel("Model")
    ax.set_xticks(list(x))
    ax.set_xticklabels(model_labels)
    ax.legend()

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}s", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}s", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("results/chart_latency.png", dpi=150)
    plt.close()
    print("✓ Chart 1 saved: results/chart_latency.png")

    # ── Chart 2: Words Per Second ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))

    base_vals  = get_ordered(base,  "words_per_second")
    quant_vals = get_ordered(quant, "words_per_second")

    bars1 = ax.bar([i - width/2 for i in x], base_vals,  width, label="Base",      color=COLORS_BASE)
    bars2 = ax.bar([i + width/2 for i in x], quant_vals, width, label="Quantized", color=COLORS_QUANT)

    ax.set_title("Average Words Per Second by Model (Base vs Quantized)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Words Per Second")
    ax.set_xlabel("Model")
    ax.set_xticks(list(x))
    ax.set_xticklabels(model_labels)
    ax.legend()

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("results/chart_wps.png", dpi=150)
    plt.close()
    print("✓ Chart 2 saved: results/chart_wps.png")

    # ── Chart 3: Memory Usage ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))

    base_vals  = get_ordered(base,  "memory_mb")
    quant_vals = get_ordered(quant, "memory_mb")

    bars1 = ax.bar([i - width/2 for i in x], base_vals,  width, label="Base",      color=COLORS_BASE)
    bars2 = ax.bar([i + width/2 for i in x], quant_vals, width, label="Quantized", color=COLORS_QUANT)

    ax.set_title("Average Memory Usage by Model (Base vs Quantized)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Memory (MB)")
    ax.set_xlabel("Model")
    ax.set_xticks(list(x))
    ax.set_xticklabels(model_labels)
    ax.legend()

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("results/chart_memory.png", dpi=150)
    plt.close()
    print("✓ Chart 3 saved: results/chart_memory.png")

    # ── Chart 4: Performance by Category ─────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 7))

    # Use combined data, label base vs quantized clearly
    combined["display_label"] = combined["model_label"] + " (" + combined["type"] + ")"
    category_perf = combined.groupby(
        ["category", "display_label"]
    )["words_per_second"].mean().unstack()

    category_perf.plot(kind="bar", ax=ax, colormap="tab10", width=0.75)

    ax.set_title("Words Per Second by Category and Model", fontsize=14, fontweight="bold")
    ax.set_ylabel("Words Per Second")
    ax.set_xlabel("Category")
    ax.set_xticklabels(category_perf.index, rotation=15, ha="right")
    ax.legend(title="Model", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.savefig("results/chart_category.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ Chart 4 saved: results/chart_category.png")

    print("\nAll 4 charts generated successfully in results/")


if __name__ == "__main__":
    generate_charts()