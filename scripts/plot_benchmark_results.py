#!/usr/bin/env python3
"""
Publication-Quality Benchmark Visualizations for Chapter 5 (Results & Discussion).
Reads data/benchmark_results.csv and generates academic figures:
1. Domain Performance (Hit Rate & Precision)
2. Multilingual Grounding Comparison (English vs Bemba vs Nyanja vs Shona)
3. Cross-Country Modularity Comparison (Zambia vs Zimbabwe)
4. System Latency Distribution
"""

import csv
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np


def load_csv_data(csv_path: Path) -> List[Dict[str, str]]:
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def plot_all_figures(csv_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_csv_data(csv_path)

    if not rows:
        print(f"No rows found in {csv_path}")
        return

    # Style settings for academic publication
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 14,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
    })

    # =========================================================================
    # Figure 1: Performance by Domain (Hit Rate & Precision)
    # =========================================================================
    domains = ["government", "education", "utilities", "health", "general"]
    domain_data = {d: {"hit": [], "prec": []} for d in domains}

    for r in rows:
        d = r.get("domain", "").lower()
        if d in domain_data:
            domain_data[d]["hit"].append(float(r.get("hit_rate", 0)))
            domain_data[d]["prec"].append(float(r.get("precision", 0)))

    d_names = [d.capitalize() for d in domains if domain_data[d]["hit"]]
    hit_means = [np.mean(domain_data[d]["hit"]) * 100 for d in domains if domain_data[d]["hit"]]
    prec_means = [np.mean(domain_data[d]["prec"]) * 100 for d in domains if domain_data[d]["prec"]]

    x = np.arange(len(d_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, hit_means, width, label="Hit Rate (Recall@3)", color="#2563eb", alpha=0.9)
    rects2 = ax.bar(x + width/2, prec_means, width, label="Retrieval Precision", color="#10b981", alpha=0.9)

    ax.set_ylabel("Score (%)")
    ax.set_title("Information Retrieval Performance Across Domains (Zambia & Zimbabwe)")
    ax.set_xticks(x)
    ax.set_xticklabels(d_names)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True)

    # Label bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    fig1_path = output_dir / "figure1_domain_performance.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"[+] Saved Figure 1 to: {fig1_path}")

    # =========================================================================
    # Figure 2: Multilingual Grounding Comparison
    # =========================================================================
    lang_labels = {"en": "English", "bem": "Bemba", "ny": "Nyanja", "sn": "Shona"}
    lang_data = {l: {"hit": [], "recall": []} for l in lang_labels}

    for r in rows:
        l = r.get("language", "").lower()
        if l in lang_data:
            lang_data[l]["hit"].append(float(r.get("hit_rate", 0)))
            lang_data[l]["recall"].append(float(r.get("keyword_recall", 0)))

    active_langs = [l for l in lang_labels if lang_data[l]["hit"]]
    l_names = [lang_labels[l] for l in active_langs]
    l_hits = [np.mean(lang_data[l]["hit"]) * 100 for l in active_langs]
    l_recalls = [np.mean(lang_data[l]["recall"]) * 100 for l in active_langs]

    x = np.arange(len(l_names))
    fig, ax = plt.subplots(figsize=(8, 5))
    r1 = ax.bar(x - width/2, l_hits, width, label="Retrieval Hit Rate", color="#3b82f6", alpha=0.9)
    r2 = ax.bar(x + width/2, l_recalls, width, label="Answer Grounding Recall", color="#8b5cf6", alpha=0.9)

    ax.set_ylabel("Score (%)")
    ax.set_title("Cross-Lingual Retrieval & Grounding Performance by Language")
    ax.set_xticks(x)
    ax.set_xticklabels(l_names)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True)

    for r in r1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for r in r2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    fig2_path = output_dir / "figure2_multilingual_performance.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    print(f"[+] Saved Figure 2 to: {fig2_path}")

    # =========================================================================
    # Figure 3: Country Modularity Comparison
    # =========================================================================
    country_data = {"zm": {"hit": [], "prec": []}, "zw": {"hit": [], "prec": []}}
    for r in rows:
        c = r.get("country", "").lower()
        if c in country_data:
            country_data[c]["hit"].append(float(r.get("hit_rate", 0)))
            country_data[c]["prec"].append(float(r.get("precision", 0)))

    c_labels = ["Zambia (Full)", "Zimbabwe (Modular PoC)"]
    c_keys = ["zm", "zw"]
    c_hits = [np.mean(country_data[k]["hit"]) * 100 if country_data[k]["hit"] else 0 for k in c_keys]
    c_precs = [np.mean(country_data[k]["prec"]) * 100 if country_data[k]["prec"] else 0 for k in c_keys]

    x = np.arange(len(c_labels))
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    cr1 = ax.bar(x - width/2, c_hits, width, label="Retrieval Hit Rate", color="#059669", alpha=0.9)
    cr2 = ax.bar(x + width/2, c_precs, width, label="Retrieval Precision", color="#d97706", alpha=0.9)

    ax.set_ylabel("Score (%)")
    ax.set_title("System Modularity: Zambia vs. Zimbabwe Instance")
    ax.set_xticks(x)
    ax.set_xticklabels(c_labels)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True)

    for r in cr1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for r in cr2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    fig3_path = output_dir / "figure3_country_modularity.png"
    plt.savefig(fig3_path, dpi=300)
    plt.close()
    print(f"[+] Saved Figure 3 to: {fig3_path}")


if __name__ == "__main__":
    csv_file = Path("data/benchmark_results.csv")
    out_dir = Path("docs/figures")
    plot_all_figures(csv_file, out_dir)
