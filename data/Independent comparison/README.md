# Independent QNN and periodic CNN comparison

These records support the repeated 2000-step comparison for the [4,3,1]
network and its statistical analysis in *Expressivity of Classical and
Quantum Neural Networks* by Sen Li, Lasse Knipping, and Tim Byrnes.

## Files

| File | Contents |
|---|---|
| Calibration QNN runs.jsonl.gz | 35,840 QNN endpoint records: 1,024 targets, 5 seeds, 7 proposal widths |
| Calibration CNN runs.jsonl.gz | The corresponding 35,840 periodic CNN endpoint records |
| Confirmation QNN runs.jsonl.gz | 40,960 QNN endpoint records: 4,096 targets and 10 seeds |
| Confirmation CNN runs.jsonl.gz | The corresponding 40,960 periodic CNN endpoint records |
| Calibration targets.csv | The 1,024 calibration truth tables and their complement-pair identifiers |
| Confirmation targets.csv | The disjoint 4,096 confirmation truth tables |
| Calibration scores.csv | Success counts, per-seed counts, and selection keys for all 14 model/width candidates |
| Paired target results.csv.gz | Exact-fit indicators for each of the 40,960 target/seed pairs |
| Seed results.csv | Rates and paired differences for the ten confirmation seeds |
| Experiment metadata.json | Architecture, numerical conventions, optimizer settings, selected widths, and statistical procedure |
| Verify results.py | Checks of the deposited records and a reproduction of the archived confidence interval |

JSONL means one JSON object per line. Gzip files can be opened with standard
gzip tools or Python's `gzip` module. No proprietary software is needed.

## Experimental scope

Each model selected its proposal width independently using the calibration
set. The selected widths in the stored implementation coordinates are 0.1
for the QNN and 0.125 for the periodic CNN. The confirmation set did not
participate in this selection. Each run has a maximum of 2000 optimizer
steps and stops early on an exact truth-table fit. The calibration and
confirmation target sets are disjoint, although these same sets had been
used in an earlier experiment; this is not a newly sampled blind panel.

All endpoint records retain the best and final parameter arrays, their
predicted truth tables, losses, random seeds, and optimization-step counts.
The original scientific values are unchanged. Internal bookkeeping hashes
and chunk identifiers were omitted when combining the archived chunks into
the four JSONL files. Full iteration-by-iteration trajectories are not part
of these endpoint records.

## Target and parameter conventions

The 16 input strings are ordered lexicographically from `0000` to `1111`.
`target_index` is the integer represented by the 16 target output bits,
including leading zeros. Its complement has index `65535 - target_index`.
`pair_representative` is the smaller of those two indices.

The raw numerical records use their original implementation coordinates.
They were not reparameterized when the manuscript's angle and output-label
notation was revised. `map1` denotes the QNN; `signsin2` denotes the periodic
CNN. In canonical bit coordinates the QNN predicts
`1 - int(output Pauli-Z expectation > 0)`, whereas the periodic CNN uses
`int(sin(2u) > 0)`. The registry columns `map1_target` and `signsin2_target`
store the corresponding native labels (`1 - canonical bit` and
`1 + canonical bit`). These are numerical encodings of the same target,
not different tasks.

QNN parameters are stored as a 4 by 5 array. In rows 0--2, column 0 is a
hidden-node bias and columns 1--4 are its four input weights. In row 3,
column 0 is the output bias and columns 1--3 are the hidden-to-output
weights. Row 3, column 4 is an unused storage slot. There are 19 active
parameters. CNN parameters form a vector of length 19: the first 12 values
are the 3 by 4 hidden-weight matrix in row-major order, followed by three
hidden biases, three output weights, and one output bias.

`epsilon_hex` is Python's exact hexadecimal floating-point representation
of the proposal width; use `float.fromhex(value)` to read it. Calibration
candidate `k` gives the anchor width times `2**(k/2)`, with `k=-3,...,3`.
`pair_seed_id` identifies a repeat shared by the two models; `master_seed`
is the seed actually used by the optimizer for a particular target.

Losses are mismatch fractions over all 16 inputs: `best_errors / 16` for
the best stored prediction. `exact_fit` is true exactly when this count is
zero. `best_parameters` and `final_parameters` can differ for unsuccessful
runs. `initial_loss` precedes optimization. Attempted steps equal accepted
plus rejected steps; objective evaluations include the initial evaluation.

## Results and uncertainty

The confirmation data contain 26,353 QNN exact fits and 19,481 periodic-CNN
exact fits out of 40,960 target/seed combinations per model. The respective
rates are 0.6433837890625 and 0.4756103515625. The paired mean difference is
0.1677734375.

The archived analysis averages the two complementary targets within each
pair, forming a 2,048 by 10 matrix. It independently resamples complement
pairs and optimizer seeds, preserving model pairing. The stored analysis
used 100,000 draws with random seed 31031 and percentile limits at 0.025
and 0.975. Its interval is [0.1570556640625, 0.1785400390625]. Rates and
interval bounds in these files are fractions, not percentages.

## Verification

Run from this directory with Python 3.10 or newer:

```console
python "Verify results.py"
python "Verify results.py" --raw
python "Verify results.py" --raw --bootstrap
```

Only the optional bootstrap calculation requires NumPy. The verification
checks data integrity and recomputes the statistics from the stored
outcomes; it does not rerun model training.
