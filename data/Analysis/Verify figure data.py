"""Check the published figure tables without rerunning network training.

Run from any directory: python "Analysis/Verify figure data.py"
The checks use the Python standard library. See the data dictionary for units.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Figure data"
COUNTS = {"Figure 4.csv": 216, "Figure 5.csv": 57, "Figure 6.csv": 40,
          "Figure 7 loss.csv": 108, "Figure 7 expressivity.csv": 30,
          "Figure 8.csv": 42}


def read(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def near(actual, expected, label, tolerance=2e-12):
    if not math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=tolerance):
        raise AssertionError(f"{label}: {actual} != {expected}")


def unique(rows, fields):
    keys = [tuple(row[key] for key in fields) for row in rows]
    assert len(keys) == len(set(keys)), f"Duplicate observation: {fields}"


def point(rows, **criteria):
    selected = [row for row in rows if all(row[key] == value for key, value in criteria.items())]
    assert len(selected) == 1, f"Expected one point for {criteria}, found {len(selected)}"
    return selected[0]


def interval(row, mean, low, high):
    values = [float(row[key]) for key in [low, mean, high]]
    assert all(math.isfinite(value) for value in values)
    assert 0 <= values[0] <= values[1] <= values[2] <= 1, (mean, values)


def verify():
    hashes = json.loads((ROOT / "Analysis" / "Figure data hashes.json").read_text(encoding="utf-8"))
    tables = {}
    for name, count in COUNTS.items():
        digest = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
        assert digest == hashes[name], f"Source table bytes changed: {name}"
        tables[name] = read(name)
        assert len(tables[name]) == count, f"Wrong row count: {name}"

    for name in ["Figure 4.csv", "Figure 7 loss.csv"]:
        rows = tables[name]
        unique(rows, ["architecture", "branch_id", "max_steps"])
        for row in rows:
            interval(row, "mean_best_loss", "ci95_low", "ci95_high")
            assert (int(row["n_targets"]), int(row["n_repeats"]), int(row["bootstrap_resamples"])) == (30, 3, 5000)
    # Figure 7(a) deliberately reuses the QNN loss data from Figure 4(b).
    shared4 = [row for row in tables["Figure 4.csv"] if row["architecture"] == "[4,3,1]" and row["branch_id"].startswith("qnn")]
    shared7 = [row for row in tables["Figure 7 loss.csv"] if row["branch_id"].startswith("qnn")]
    assert shared4 == shared7, "Shared QNN loss data differ"

    rows5 = tables["Figure 5.csv"]
    unique(rows5, ["panel", "branch_id", "hidden_width", "max_steps"])
    for row in rows5:
        assert int(row["n_targets"]) == 256 and int(row["n_seeds_per_target"]) == 3
        count = 768 * float(row["mean_empirical_expressivity"])
        near(count, round(count), "Figure 5 integer exact-fit count")
    widths = {int(row["hidden_width"]) for row in rows5 if row["panel"] == "b_width_dependence_t400" and row["branch_id"] == "cnn_sign"}
    assert {12, 24, 48} <= widths, "Extended Figure 5(b) points are missing"
    for width, expected in [("4", 767 / 768), ("5", 766 / 768)]:
        row = point(rows5, panel="a_budget_dependence", branch_id="qnn_lasse_map1_physical_aligned", hidden_width=width, max_steps="1000")
        near(row["mean_empirical_expressivity"], expected, f"Figure 5 width {width}")

    rows6 = tables["Figure 6.csv"]
    unique(rows6, ["panel", "branch_id", "M1", "max_steps"])
    for row in rows6:
        assert int(row["targets"]) == 4096 and int(row["seeds"]) == 3
        count = 12288 * float(row["mean_expressivity"])
        near(count, round(count), "Figure 6 integer exact-fit count")
    for model, expected in [("qnn_lasse_map1_physical_aligned", 0.9775390625), ("cnn_sign", 0.0082194010416666)]:
        row = point(rows6, panel="budget_dependence", branch_id=model, M1="3", max_steps="8000")
        near(row["mean_expressivity"], expected, f"Figure 6 {model}")

    rows7 = tables["Figure 7 expressivity.csv"]
    curves = [row for row in rows7 if row["source_panel"] == "c033_curves"]
    trials = [row for row in rows7 if row["source_panel"] == "map1_confirm_seed_gaps"]
    assert len(curves) == 20 and len(trials) == 10
    unique(curves, ["architecture_key", "branch_id", "max_steps"])
    unique(trials, ["pair_seed_id"])
    for row in curves:
        near(row["exact_fit_rate"], int(row["exact_fit_count"]) / int(row["rows"]), "Figure 7 exact-fit rate")
    for row in trials:
        gap = float(row["qnn_exact_rate"]) - float(row["signsin2_exact_rate"])
        near(row["paired_gap_fraction"], gap, "Figure 7 paired gap")
        near(row["paired_gap_pp"], 100 * gap, "Figure 7 percent-scale gap")
        assert gap > 0, "QNN is not higher in this repetition"
    qnn_count = sum(4096 * float(row["qnn_exact_rate"]) for row in trials)
    cnn_count = sum(4096 * float(row["signsin2_exact_rate"]) for row in trials)
    near(qnn_count, 26353, "QNN total exact fits")
    near(cnn_count, 19481, "Periodic-CNN total exact fits")
    mean_gap = statistics.mean(float(row["paired_gap_fraction"]) for row in trials)
    near(mean_gap, (26353 - 19481) / 40960, "Main comparison gap")

    rows8 = tables["Figure 8.csv"]
    unique(rows8, ["p_depolarizing", "q_readout_flip", "shots"])
    for row in rows8:
        assert (int(row["targets"]), int(row["total_runs"]), int(row["clean_exact_runs"])) == (256, 768, 726)
        interval(row, "absolute_recovery", "absolute_ci_low", "absolute_ci_high")
        interval(row, "conditional_recovery", "conditional_ci_low", "conditional_ci_high")
        interval(row, "infinite_shot_exact_rate", "infinite_shot_ci_low", "infinite_shot_ci_high")
    clean = point(rows8, p_depolarizing="0.0", q_readout_flip="0.0", shots="512")
    noisy = point(rows8, p_depolarizing="0.02", q_readout_flip="0.02", shots="512")
    near(clean["absolute_recovery"], 0.6779196714409309, "Clean finite-shot success")
    near(noisy["absolute_recovery"], 0.6476138971815952, "Noisy finite-shot success")
    near(clean["infinite_shot_exact_rate"], 0.9453125, "Clean infinite-shot rate")
    near(noisy["infinite_shot_exact_rate"], 0.8984375, "Noisy infinite-shot rate")
    return {"status": "PASS", "table_rows": COUNTS,
            "main_comparison": {"qnn_count": round(qnn_count), "periodic_cnn_count": round(cnn_count),
                                "target_initialization_pairs": 40960, "mean_gap_fraction": mean_gap},
            "finite_shot_success": {"shots_per_input": 512, "clean": float(clean["absolute_recovery"]),
                                    "p_and_q_0.02": float(noisy["absolute_recovery"]),
                                    "retention": float(noisy["absolute_recovery"]) / float(clean["absolute_recovery"])},
            "scope": "Figure tables, checksums, shared observations, and reported summary values; no new training or bootstrap recomputation."}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
