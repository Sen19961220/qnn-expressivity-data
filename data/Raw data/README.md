# Numerical run records

Each compressed CSV contains one row per optimization run, except `Finite shot probabilities.csv.gz`, which contains one row per trained network and noise/shot setting. Gzip is a compression format: use Python's `gzip.open(path, "rt")` with `csv.DictReader`, or decompress with a standard archive utility.

| File | Records | Manuscript figure |
|---|---:|---|
| QNN transported runs.csv.gz | 71160 | QNN loss in 4 and 7(a); part of the four-input expressivity results in 6 |
| QNN completion runs.csv.gz | 161280 | QNN width and budget comparisons in 5 and 6 |
| Periodic CNN loss runs.csv.gz | 4860 | Periodic-CNN loss in 7(a) |
| Sign CNN loss and three input budget runs.csv.gz | 40440 | Classical loss in 4 and three-input budget comparison in 5(a) |
| Sign CNN three input width runs.csv.gz | 7680 | Classical width comparison in 5(b), including widths 12, 24 and 48 |
| Sign CNN four input width three runs.csv.gz | 61440 | Classical width-3 budget comparison in 6 |
| Sign CNN four input width two and four early budgets.csv.gz | 73728 | Classical widths 2 and 4 at budgets 400, 1000 and 2000 in 6 |
| Sign CNN four input width two and four late budgets.csv.gz | 49152 | Classical widths 2 and 4 at budgets 4000 and 8000 in 6 |
| QNN and periodic CNN budget runs.csv.gz | 130560 | Periodic comparisons in 7(b,c) and the width-2 QNN series in 5(a) |
| Finite shot probabilities.csv.gz | 32256 | 256 targets, 3 trained initializations and 42 settings in 8 |

The repeated independent comparison in Figure 7(d) has its own directory. The two sign-CNN observations at widths 5 and 6 in Figure 6(b) are preserved separately under `Aggregate records`; per-run records for those two observations were not available in the source archive assembled for this release. All plotted observations, including these two, are provided under `Figure data`.

## Identifiers and numerical values

`architecture` is the list [input nodes, hidden nodes, output nodes]. `architecture_key` is its compact historical identifier. In completion records, `n` and `h` are the input count and hidden width. `branch_id` or `branch` identifies QNN, sign-CNN or periodic-CNN; see the figure-data dictionary.

`target_index` is the integer represented by the Boolean truth table, with leading zeros retained when converted to bits. Inputs are enumerated lexicographically. `target_id` is a textual identifier for the same table. `Target sets.json` records the target indices in each named set. Historical labels such as `fig5b_fig8b_431_dense4096` are target-set identifiers; their embedded figure numbers refer to an earlier working manuscript. Use the table above for current figure numbers.

`max_steps` or `budget` is the maximum annealing budget. Each budget is a separate optimization experiment. `seed_bundle`, `repeat` and `optimizer_seed_id` identify initialization repeats; `master_seed` is the actual numerical random seed. `pairing_key` records the matching of a target and initialization across models. Some data collections overlap, so the total row count across files is not a count of unique experiments.

`initial_loss`, `best_loss` and `final_loss` refer to the initial, best encountered and final states of optimization. `exact_fit` indicates an exact target fit. `exact_final` separately describes the final state when present. `accepted_moves`/`accepted_steps`, `rejected_moves`/`rejected_steps`, `proposal_budget`/`attempted_steps`, and `objective_evaluations` preserve optimizer counts. `first_exact_fit_step` or `first_exact_proposal` is empty when no exact fit was reached.

`T0`, `Tmin`, `cooling`, `tau`, `freeze_step` and `hold_at_tmin` preserve the annealing schedule. `epsilon`, `normalized_epsilon`, `epsilon_multiplier` and `epsilon_float_hex` preserve proposal widths in their recorded numerical coordinates. These values have not been halved to match the analytical notation in the manuscript.

`reuse_transform` and `initialization_provenance` document the output-bias transport of historical QNN records. In particular, the loss records in Figures 4 and 7(a) retain their expectation-readout provenance. They are not newly rerun digital-readout loss records. Historical `target_kind` labels in classical-network files do not denote an additional quantum model.

`campaign_id`, `protocol_id`, `stage`, `panel_id`, `group`, `cell_id`, `run_id`, and retained hashes are identifiers from the numerical analysis. They are included to preserve grouping and pairing; they are not new experimental variables. Machine paths, execution-time telemetry, empty error logs and unrelated bookkeeping fields were excluded from these public copies. Retained field values were compared exactly with the source records after filtering.

## Finite-shot records

`p_depolarizing`, `q_readout_flip` and `shots` specify the noise/readout setting. `function_recovery_probability` is the analytically calculated probability of a completely correct truth table for one trained network. The word `recovery` is historical; the manuscript calls it success probability. `clean_exact_fit` describes the noiseless infinite-shot baseline; `infinite_shot_exact` describes the specified noisy setting. Average over all 768 trained networks to obtain the unconditional plotted probability. The three-repeat variation within each target gives the pointwise uncertainty in SI S3. See `Analysis/Verify noise data.py` for the calculation.

## Integrity

`Run data manifest.json` at the release root records the retained columns, record counts and hashes. The public compression and names differ from the source archives, but retained numerical strings and identifiers are unchanged. Empty CSV fields remain empty rather than being replaced with zeros.
