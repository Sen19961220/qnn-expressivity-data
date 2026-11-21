# Figure data

These six CSV files contain the computed observations used in Figures 4--8 of **Expressivity of Classical and Quantum Neural Networks**. Their numerical values and original column names are preserved. File names have been shortened for this release. Figures 1--3 are diagrams rather than sampled numerical results.

| File | Rows | Content |
|---|---:|---|
| Figure 4.csv | 216 | Sign-CNN and QNN loss comparisons for [3,2,1] and [4,3,1] |
| Figure 5.csv | 57 | Three-input expressivity versus budget and hidden width |
| Figure 6.csv | 40 | Four-input expressivity versus budget and hidden width |
| Figure 7 loss.csv | 108 | Periodic-CNN and QNN loss comparison for [4,3,1] |
| Figure 7 expressivity.csv | 30 | Periodic-CNN budget comparisons and ten paired confirmation trials |
| Figure 8.csv | 42 | Finite-shot truth-table success under depolarizing and readout noise |

Except for `paired_gap_pp`, probability, rate, expressivity, difference and interval columns use **fractions**, not percentages. A stored value of 0.64 corresponds to 64%. Loss is dimensionless. Empty fields mean that a statistic was not recorded or does not apply to that row; they do not mean zero.

## Common identifiers

- `architecture`: `[M0,M1,1]`, the numbers of input, hidden and output nodes. `architecture_key` is a compact identifier such as `321` or `431` for the same architectures.
- `branch_id`: `cnn_sign` is the sign-activation classical network; `cnn_sign_sin2` is the periodic classical network. `qnn_lasse_map1_physical_aligned` and `qnn_lasse_map1_z` are retained historical QNN identifiers. An identifier by itself does not specify which historical loss data were used; see the `source` field in the loss tables.
- `max_steps`: the maximum simulated-annealing step budget. Different budgets are evaluated with separate anneals. Points on a budget curve are not successive checkpoints from a single training trajectory.
- `hidden_width` or `M1`: hidden-layer node count.
- `target_set_id` and `target_group`: identifiers of the fixed target-function collections. Targets and initializations are distinct replication levels.

## Figure 4.csv and Figure 7 loss.csv

| Columns | Meaning |
|---|---|
| `mean_best_loss` | Mean best loss over the target/initialization records at the stated budget |
| `ci95_low`, `ci95_high` | Pointwise 95% target-bootstrap limits for that mean |
| `n_targets`, `n_repeats` | 30 targets and 3 initializations per target |
| `bootstrap_resamples` | 5000 draws for these loss intervals |
| `target_group` | `LOSS3_MAIN30` or `LOSS4_MAIN30` |
| `source` | Provenance description preserved from the analysis table |

The three initializations are averaged within each target before bootstrapping targets. Figure 7(a) reuses the same QNN observations as Figure 4(b). The QNN provenance field explicitly identifies accepted expectation-readout loss runs with physical-label parameter transport; these are not newly rerun digital-loss training records. The plotted manuscript curves are stretched-exponential fits, whereas the CSVs contain the computed observations and their intervals.

## Figure 5.csv

- `panel`: `a_budget_dependence` or `b_width_dependence_t400`.
- `mean_empirical_expressivity`: fraction of target-initialization pairs fitted exactly.
- `n_targets`, `n_seeds_per_target`, `cells_per_point`: 256, 3 and 768 respectively.
- `seed_rate_sample_sd`: sample standard deviation of the per-initialization exact-fit rates, when recorded. This is not a confidence interval.
- `line_style_role`: a plotting-style identifier, not an additional measured quantity.

Panel (a) uses hidden widths 2--5. Panel (b) uses budget 400, matched widths 2--8 and the additional sign-CNN widths 12, 24 and 48. All three classical extension points belong to the submitted figure and are included here. The manuscript uses saturating-exponential fits in panel (a) and lines joining points in panel (b).

## Figure 6.csv

- `panel`: `budget_dependence` or `width_dependence_t1000`.
- `mean_expressivity`: fraction of target-initialization pairs fitted exactly.
- `targets`, `seeds`: 4096 and 3 respectively.
- `seed_expressivity_std`: standard deviation across per-initialization rates, when recorded; not a confidence interval.

Panel (a) compares hidden widths 2--4. Panel (b) fixes the budget at 1000. The manuscript uses saturating-exponential fits in panel (a), except that the sign-CNN width-2 observations are joined directly. Table values are unchanged by the final label-spacing adjustment to Figure 6.

## Figure 7 expressivity.csv

This file contains two types of row, selected by `source_panel`.

**`c033_curves` (20 rows, panels b and c):**

| Columns | Meaning |
|---|---|
| `rows` | Number of target-initialization pairs: 768 for three inputs; 12288 for four inputs |
| `exact_fit_count`, `exact_fit_rate` | Number and fraction fitted exactly after the anneal |
| `initial_exact_fit_count`, `initial_exact_fit_rate` | Corresponding counts and rates at initialization |
| `epsilon_multiplier_id` | Historical proposal-width multiplier identifier; `eps_mul_1` denotes the nominal setting |

**`map1_confirm_seed_gaps` (10 rows, panel d):**

| Columns | Meaning |
|---|---|
| `pair_seed_id` | Initialization identifier shared by the two model records being compared |
| `qnn_exact_rate`, `signsin2_exact_rate` | Exact-fit rates over 4096 fixed confirmation targets for that initialization |
| `paired_gap_fraction` | QNN rate minus periodic-CNN rate |
| `paired_gap_pp` | The same difference multiplied by 100, as plotted on the percent scale |

The confirmation comparison uses [4,3,1] and budget 2000 for all ten trials. Across 40960 target-initialization pairs, exact-fit counts are 26353 for QNN and 19481 for periodic CNN, with mean difference 0.1677734375. The manuscript's crossed paired-bootstrap interval resamples complement-pair rows and initialization columns independently. It cannot be recomputed from these ten trial averages alone: use the underlying paired confirmation data. The 5000-draw count in the loss tables is a separate analysis and does not describe this crossed bootstrap.

## Figure 8.csv

| Columns | Meaning |
|---|---|
| `p_depolarizing` | Pauli-depolarizing probability p: D(rho)=(1-p)rho+(p/3)(XrhoX+YrhoY+ZrhoZ) |
| `q_readout_flip` | Independent flip probability for a measured output bit |
| `shots` | Measurements per truth-table input |
| `absolute_recovery` | **Plotted success probability:** unconditional probability of decoding the complete correct truth table, averaged over all target-initialization pairs |
| `absolute_ci_low`, `absolute_ci_high` | The corresponding pointwise approximate 95% limits |
| `conditional_recovery` | A different, conditional statistic restricted to training runs with an exact noiseless infinite-shot fit; not the published plotted metric |
| `conditional_ci_low`, `conditional_ci_high` | Interval limits for that conditional statistic |
| `infinite_shot_exact_rate` | Exact truth-table rate at the specified noise setting with an infinite-shot readout |
| `infinite_shot_ci_low`, `infinite_shot_ci_high` | Interval limits for the infinite-shot statistic |
| `clean_exact_runs` | 726 runs with an exact noiseless infinite-shot fit |
| `total_runs`, `targets` | 768 runs over 256 targets, with 3 independent initializations each |
| `mean_mode_tie_rate` | Retained diagnostic of ties in the deterministic modal readout; not the probability of a finite-shot count tie |

The historical word `recovery` in column names means truth-table success, not quantum error-correction recovery. The CSV columns remain unchanged to preserve their provenance.

Each trained [3,2,1] network is evaluated with fixed parameters at all listed noise/shot settings. The binomial majority-vote probabilities are evaluated analytically. Output +1 requires a strict majority of Z=+1 outcomes; ties decode -1. Success over eight inputs is the product of the eight probabilities, using independent shot batches. No additional Monte Carlo shot sample is implied by these tables.

The finite-shot intervals quantify variation between training initializations for the fixed population of 256 targets, using within-target sample variances and Welch--Satterthwaite t degrees of freedom as specified in SI S3. They are not the target-bootstrap intervals used for loss. At 512 shots, success is 0.6779196714409309 for p=q=0 and 0.6476138971815952 for p=q=0.02; the corresponding infinite-shot rates are 0.9453125 and 0.8984375.

## Numerical and analytical coordinates

The manuscript uses x=+1,-1 as Z eigenvalues, with binary labels y=(1-x)/2. Its neuron Hamiltonian is H=-(Y/2)(sum wZ+b-pi/2), giving Z expectation sin(theta) for a fresh neuron with theta=sum wx+b. Digital readout is +1 for a positive expectation and -1 otherwise.

The archived periodic-CNN numerical implementation uses sign(sin(2u)). For first-layer numerical parameters W and K, u=sum W(1-x)/2+K, and the analytical phase 2u corresponds to w=-W and b=2K+sum W. The factor two is a coordinate convention; it must not be removed from archived numerical code without applying the full transformation.

Numerical proposal half-widths are 0.1 for QNN, 0.125 for periodic CNN and 14 for sign CNN. These are the numerical implementation coordinates and must not be halved again because of the manuscript's analytical half-angle expression. Numerical parameters are initialized uniformly on [-2pi,2pi], with T0=10 and Tmin=0.01. Full target ordering, random seeds and run-level provenance belong to the underlying data records.

## Verification and plotting

Run `python "Analysis/Verify figure data.py"` from the repository root. It checks the six original table hashes, row counts, shared QNN loss records, extended Figure 5 points, exact-fit counts, probability intervals, and the main reported summary values. This verifies data integrity and internal numerical consistency; it does not rerun network training or recompute the bootstrap intervals.

Run `python "Analysis/Verify noise data.py"` to reaggregate the 32256 records in `Raw data/Finite shot probabilities.csv.gz`. It reconstructs all 42 unconditional finite-shot means and their stored 95% intervals from the 256 targets and 3 initializations per target, and checks the infinite-shot exact rates. It requires SciPy and applies the SI S3 within-target/Welch--Satterthwaite method. It does not replace the plotted absolute success probabilities with the conditional statistics.

Install the plotting dependency with `python -m pip install -r Analysis/requirements.txt`, then run `python "Analysis/Plot figure data.py" --output "Plots"`. This creates portable plots of computed observations and stored intervals. Straight line segments join observations; the manuscript's fitted display curves and Figure 7(d)'s crossed-bootstrap band are omitted. These plots are not intended as pixel-identical replacements for the submitted figures.
