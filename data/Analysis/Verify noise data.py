"""Reaggregate Figure 8 from target-initialization finite-shot probabilities.

Run: python "Analysis/Verify noise data.py"
Requires SciPy for Student-t quantiles. This recomputes means and uncertainty
intervals from stored analytic probabilities; it does not rerun training or
generate new quantum measurement samples.
"""
from pathlib import Path
from collections import defaultdict
import csv
import gzip
import json
import math
import statistics

try:
    from scipy.stats import t
except ImportError as error:
    raise SystemExit("This check requires scipy. Run: python -m pip install scipy") from error

ROOT = Path(__file__).resolve().parents[1]


def setting(row):
    return (float(row["p_depolarizing"]), float(row["q_readout_flip"]), int(row["shots"]))


def truth(value):
    if value.lower() not in {"true", "false"}:
        raise AssertionError(f"Unrecognized Boolean value: {value}")
    return value.lower() == "true"


def summarize(rows):
    by_target = defaultdict(list)
    pairs = set()
    for row in rows:
        key = (row["target_id"], row["seed_bundle"])
        assert key not in pairs, f"Duplicate target-initialization record: {key}"
        pairs.add(key)
        probability = float(row["function_recovery_probability"])
        assert math.isfinite(probability) and 0 <= probability <= 1
        by_target[row["target_id"]].append(probability)
    assert len(rows) == 768 and len(by_target) == 256
    assert all(len(values) == 3 for values in by_target.values())

    mean = statistics.mean(value for values in by_target.values() for value in values)
    variances = [statistics.variance(values) for values in by_target.values()]
    variance_sum = sum(variances)
    mean_variance = variance_sum / (256 ** 2 * 3)
    denominator = sum(variance ** 2 / 2 for variance in variances)
    degrees = variance_sum ** 2 / denominator if denominator else math.inf
    half_width = float(t.ppf(0.975, degrees)) * math.sqrt(mean_variance)
    result = {"absolute_recovery": mean,
              "absolute_ci_low": max(0, mean - half_width),
              "absolute_ci_high": min(1, mean + half_width),
              "infinite_shot_exact_rate": statistics.mean(truth(row["infinite_shot_exact"]) for row in rows),
              "clean_exact_runs": sum(truth(row["clean_exact_fit"]) for row in rows),
              "degrees_of_freedom": degrees}
    return result, pairs


def verify():
    raw_path = ROOT / "Raw data" / "Finite shot probabilities.csv.gz"
    with gzip.open(raw_path, "rt", encoding="utf-8", newline="") as handle:
        grouped = defaultdict(list)
        for row in csv.DictReader(handle):
            grouped[setting(row)].append(row)
    with (ROOT / "Figure data" / "Figure 8.csv").open(encoding="utf-8-sig", newline="") as handle:
        table = list(csv.DictReader(handle))
    assert len(table) == 42 and len(grouped) == 42
    assert sum(map(len, grouped.values())) == 32256
    assert {setting(row) for row in table} == set(grouped)

    errors = defaultdict(float)
    common_pairs = None
    results = []
    for published in table:
        key = setting(published)
        values, pairs = summarize(grouped[key])
        if common_pairs is None:
            common_pairs = pairs
        assert pairs == common_pairs, "Different trained ensemble across evaluation settings"
        assert values["clean_exact_runs"] == int(published["clean_exact_runs"]) == 726
        for column in ["absolute_recovery", "absolute_ci_low", "absolute_ci_high", "infinite_shot_exact_rate"]:
            error = abs(values[column] - float(published[column]))
            errors[column] = max(errors[column], error)
            assert error < 1e-12, f"Figure 8 mismatch: {key}, {column}, error={error}"
        results.append({"p": key[0], "q": key[1], "shots": key[2], **values})
    return {"status": "PASS", "raw_records": 32256, "settings": 42,
            "targets_per_setting": 256, "initializations_per_target": 3,
            "maximum_absolute_errors": dict(errors),
            "method": "Within-target initialization variances; Welch-Satterthwaite Student-t 95% intervals; clipped to [0,1].",
            "scope": "Reaggregated unconditional finite-shot means and stored 95% intervals, and infinite-shot exact rates. Conditional statistics are not substituted for plotted absolute success.",
            "settings_at_512_shots": [result for result in results if result["shots"] == 512 and (result["p"], result["q"]) in {(0, 0), (.02, .02)}]}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
