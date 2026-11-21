# QNN expressivity data

Numerical data for **Expressivity of Classical and Quantum Neural Networks** by Sen Li, Lasse Knipping, and Tim Byrnes.

The [data](data) directory contains the numerical observations used in Figures 4--8, the available underlying simulation records, and scripts for checking the reported statistics. Figures 1--3 are diagrams.

| Folder | Contents |
|---|---|
| [Figure data](data/Figure%20data) | Six CSV tables corresponding to the manuscript figures, with column definitions |
| [Raw data](data/Raw%20data) | Per-run records for the loss, width and budget comparisons, and per-network noise/readout probabilities |
| [Independent comparison](data/Independent%20comparison) | Calibration and confirmation records for the repeated QNN versus periodic-CNN comparison |
| [Aggregate records](data/Aggregate%20records) | The two archived classical-network width-5/6 observations for which only aggregate records were available |
| [Display curves](data/Display%20curves) | Fitted display coordinates and residuals, separate from the computed observations |
| [Analysis](data/Analysis) | Data checks and portable plotting scripts |

Rates and probabilities are stored as fractions unless a column explicitly indicates a percent-scale value. Original numerical values and historical column identifiers are retained. File names and the directory structure have been simplified; [Data dictionary](data/Figure%20data/Data%20dictionary.md) explains the model labels, coordinates, units and figure mapping.

The main repeated comparison contains 26,353 QNN exact fits and 19,481 periodic-CNN exact fits out of 40,960 target-initialization pairs. The records include the separate calibration set and the paired confirmation outcomes. Per-run records for two older sign-CNN points in Figure 6(b), hidden widths 5 and 6 at budget 1000, were not available in the source archive used for this release; their preserved aggregate values are included and identified separately.

## Download and use

Choose **Code > Download ZIP**, or clone this repository. Open the CSV tables directly, or read compressed CSV/JSONL records using standard gzip tools. Detailed file descriptions are included in each data folder.

For numerical checks, open a terminal in the downloaded `data` directory and run:

```console
python "Analysis/Verify figure data.py"
python -m pip install -r "Analysis/requirements.txt"
python "Analysis/Verify noise data.py"
python "Independent comparison/Verify results.py" --raw --bootstrap
```

The verification scripts check the deposited data and recompute summary statistics; they do not rerun network training. Optional plots of the observations can be generated with:

```console
python "Analysis/Plot figure data.py" --output "Plots"
```

These portable plots show the data rather than reproducing the exact typesetting of the manuscript. The manuscript's fitted display coordinates are supplied separately.

## Citation

When using these data, cite **Sen Li, Lasse Knipping, and Tim Byrnes, Expressivity of Classical and Quantum Neural Networks**, and include this repository's URL and the commit identifier of the version used. This repository accompanies the manuscript; it does not assign a publication DOI or imply acceptance by a journal.

Prepared on 22 November 2026. Original research files and the manuscript were not altered when assembling this deposit.
