"""Plot the computed observations in Figures 4--8.

These are portable data plots, not pixel-identical copies of the manuscript.
Straight segments join computed observations; fitted display curves are omitted.
The crossed-bootstrap band in Figure 7(d) needs the underlying paired records
and is not estimated from the ten plotted trial averages.

Usage: python "Analysis/Plot figure data.py" --output "Plots"
"""
from pathlib import Path
import argparse
import csv
import importlib.util
import statistics
import sys

sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Figure data"
RED, BLUE = "#A63D40", "#285F8F"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "pdf.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 200})


def read(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def model(branch):
    if branch.startswith("qnn"):
        return "QNN", RED
    return ("Periodic CNN" if "sin2" in branch else "Sign CNN"), BLUE


def draw(ax, rows, xkey, ykey, label, color, *, scale=1, marker="o", interval=None):
    rows = sorted(rows, key=lambda row: float(row[xkey]))
    x = [float(row[xkey]) for row in rows]
    y = [scale * float(row[ykey]) for row in rows]
    ax.plot(x, y, marker=marker, markersize=3, linewidth=.8, label=label, color=color)
    if interval:
        ax.fill_between(x, [scale * float(row[interval[0]]) for row in rows],
                        [scale * float(row[interval[1]]) for row in rows], color=color, alpha=.15)


def loss(ax, rows, architecture):
    rows = [row for row in rows if row["architecture"] == architecture]
    for branch in dict.fromkeys(row["branch_id"] for row in rows):
        label, color = model(branch)
        draw(ax, [row for row in rows if row["branch_id"] == branch], "max_steps", "mean_best_loss",
             label, color, interval=("ci95_low", "ci95_high"))
    ax.set(xlabel="Annealing budget", ylabel="Mean best loss", title=architecture)
    ax.legend(frameon=False)


def finish(fig, output, number):
    fig.savefig(output / f"Figure {number} data.pdf", bbox_inches="tight")
    fig.savefig(output / f"Figure {number} data.png", bbox_inches="tight")
    plt.close(fig)


def plot(output):
    output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.3), layout="constrained")
    for ax, arch in zip(axes, ["[3,2,1]", "[4,3,1]"]):
        loss(ax, read("Figure 4.csv"), arch)
    finish(fig, output, 4)

    for number, panel_a, panel_b, width, ykey in [
            (5, "a_budget_dependence", "b_width_dependence_t400", "hidden_width", "mean_empirical_expressivity"),
            (6, "budget_dependence", "width_dependence_t1000", "M1", "mean_expressivity")]:
        rows = read(f"Figure {number}.csv")
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), layout="constrained")
        for branch in dict.fromkeys(row["branch_id"] for row in rows):
            label, color = model(branch)
            selected = [row for row in rows if row["branch_id"] == branch and row["panel"] == panel_a]
            for w, marker in zip(sorted({int(row[width]) for row in selected}), ["o", "s", "^", "D"]):
                draw(axes[0], [row for row in selected if int(row[width]) == w], "max_steps", ykey,
                     f"{label}, width {w}", color, marker=marker)
            draw(axes[1], [row for row in rows if row["branch_id"] == branch and row["panel"] == panel_b],
                 width, ykey, label, color)
        axes[0].set(xlabel="Annealing budget", ylabel="Expressivity (fraction)", ylim=(-.02, 1.03))
        axes[1].set(xlabel="Hidden width", ylabel="Expressivity (fraction)", ylim=(-.02, 1.03),
                    title="Budget = 400" if number == 5 else "Budget = 1000")
        axes[0].legend(frameon=False, fontsize=7, ncol=2)
        axes[1].legend(frameon=False)
        finish(fig, output, number)

    fig, axes = plt.subplots(2, 2, figsize=(9, 6.8), layout="constrained")
    loss(axes[0, 0], read("Figure 7 loss.csv"), "[4,3,1]")
    rows = read("Figure 7 expressivity.csv")
    for ax, arch in [(axes[0, 1], "321"), (axes[1, 0], "431")]:
        selected = [row for row in rows if row["source_panel"] == "c033_curves" and row["architecture_key"] == arch]
        for branch in dict.fromkeys(row["branch_id"] for row in selected):
            label, color = model(branch)
            draw(ax, [row for row in selected if row["branch_id"] == branch], "max_steps", "exact_fit_rate", label, color, scale=100)
        ax.set(xlabel="Annealing budget", ylabel="Expressivity (%)", title=f"[{','.join(arch)}]", ylim=(0, 105))
        ax.legend(frameon=False)
    trials = [row for row in rows if row["source_panel"] == "map1_confirm_seed_gaps"]
    gaps = [float(row["paired_gap_pp"]) for row in trials]
    axes[1, 1].plot(range(1, 11), gaps, linestyle="none", marker="D", color=RED, markersize=4)
    axes[1, 1].axhline(statistics.mean(gaps), color=RED, linewidth=1, label="Mean")
    axes[1, 1].set(xlabel="Independent initialization", ylabel="QNN minus periodic CNN (%)", title="Budget = 2000")
    axes[1, 1].legend(frameon=False)
    finish(fig, output, 7)

    rows = read("Figure 8.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), layout="constrained")
    for q, color in [(0, RED), (.01, BLUE), (.1, "#4D7551")]:
        draw(axes[0], [row for row in rows if int(row["shots"]) == 512 and float(row["q_readout_flip"]) == q],
             "p_depolarizing", "absolute_recovery", f"q = {q:g}", color, scale=100,
             interval=("absolute_ci_low", "absolute_ci_high"))
    for pq, color in [(0, RED), (.02, BLUE)]:
        draw(axes[1], [row for row in rows if float(row["p_depolarizing"]) == pq and float(row["q_readout_flip"]) == pq],
             "shots", "absolute_recovery", f"p = q = {pq:g}", color, scale=100,
             interval=("absolute_ci_low", "absolute_ci_high"))
    axes[0].set(xlabel="Pauli-depolarizing probability p", ylabel="Success probability (%)", title="512 shots per input")
    axes[1].set(xlabel="Shots per input", ylabel="Success probability (%)")
    for ax in axes:
        ax.legend(frameon=False)
    finish(fig, output, 8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "Plots")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("verify_figure_data", Path(__file__).with_name("Verify figure data.py"))
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.verify()
    plot(args.output)
    print(f"Saved computed-data plots for Figures 4--8 to {args.output.resolve()}")
