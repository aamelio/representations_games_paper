# Replication package — "Beyond Social Preferences: Mental Representations in Games"

Amelio, Gennaioli, Nunnari. Not AEA-level; a working package. `../main.tex` draws
every exhibit from this folder (`\graphicspath` → `output/figures/`, `\input` →
`output/tables/`).

## Layout

```
replication_package/
├── README.md
├── data/
│   ├── player{1,2}_all_categorized.xlsx   master categorized workbooks (one row
│   │                                      per response, LLM category)
│   ├── within_switching_results.xlsx      AA's within-subject summary (input to 04)
│   ├── within_regression_results.{xlsx,txt}  AA's raw within regression output
│   │                                      (provenance for the within tables)
│   └── missingdata/                       AA's delivery 2026-07-10: 6 human-coder
│                                          validation workbooks + within microdata
│                                          (within_all_{long,pairs}_categorized.xlsx)
├── code/
│   ├── 01…07_*.py                         pipeline (run order below)
│   └── verification/                      5 pure-sympy scripts checking every
│                                          proposition/remark symbolically
└── output/
    ├── figures/                           all paper figures (PNG);
    │   └── fitted_fullpooled/             02's model-fit figures
    └── tables/                            all paper tables (.tex) + run logs (*.txt);
                                           control_treatment_figure_stats.txt and
                                           forecast_error_figure_stats.txt (2026-07-16)
                                           log every statistic rendered on 01/03's
                                           figures, incl. the all-responses treatment
                                           effects quoted in the paper's text (the
                                           figures use the classified sample; the two
                                           conventions differ by <1pp cell by cell)
```

## Run order

From `code/` (Python 3 with pandas, numpy, matplotlib, statsmodels, scipy, openpyxl):

```
python3 01_control_treatment_and_appendix_figures.py   # control/treatment + appendix figures
python3 02_general_equilibrium_tables_figures.py       # fitted model tables + figures
python3 03_forecast_error_figures.py                   # forecast-error figures + derived CSVs (to data/)
python3 04_paper_v1_extra_outputs.py                   # intro figure, surplus/within tables, Fig. 16
python3 05_paper_v2_new_outputs.py                     # E1-E5 (NOT yet in the paper; pending AA re-run)
python3 06_validation_and_within_checks.py             # LLM-human agreement table + within checks
python3 07_player2_exhibit_split.py                    # P2 figure split (imports 01)
python3 08_calibration.py                              # NG round: per-category (sigma/mu, rho/mu),
                                                       #   (a,b), s; overid tests; Cov(sigma/mu,s)
python3 09_p2_foundation.py                            # NG round: P2 categories vs action faced;
                                                       #   schedules by category; believed-vs-actual
                                                       #   slopes; FE by offer bin
python3 10_interaction_accounting.py                   # NG round: category x belief interactions
python3 11_oaxaca.py                                   # NG round: preregistered Oaxaca, cat x belief cells
python3 12_ng_page_items.py                            # NG round: SP x action panel, quote candidates
python3 verification/proof_audit_checks.py             # + the other four verification scripts
```

All scripts anchor paths at the package root via `__file__` (`03` additionally
assumes the working directory is `code/` or the package root).

## Regeneration caveats

- Re-running `02`/`04` rewrites .tex tables with LF line endings where the
  originals were CRLF; content is unchanged but the byte diff is spurious.
- `01` also writes four v1-era figures the paper no longer uses
  (`paper_figure{3,4}_mixed.png`, `paper_outcome_treatment_effects_with_model.png`,
  `paper_representation_treatment_effects.png`); they are deleted from
  `output/figures/` (decision 2026-07-16) and will reappear on a fresh run.
- `05`'s two PNGs re-render with environment-dependent bytes; statistics
  (`paper_v2_new_stats.txt` and all .tex) reproduce exactly (verified 2026-07-16).

## Known gaps

- `output/figures/hp_sp_moral_corr_{ctrl,mkt}.png` (Appendix C heatmaps) have NO
  generator here — they rest on the v1 fine-grained hp classification, which exists
  in no file we hold (verified 2026-07-15). Appendix C's tables are hard-coded in
  `main.tex`.
- `output/tables/within_*regression_table*.tex` (4 files) are AA's, not
  script-generated; edited 2026-07-10 to drop the non-identified LTFirst/ControlFirst
  rows (originals in `../backups/within_tables_2026-07-10/`). `06` reproduces every
  FE-identified coefficient from `data/missingdata/within_all_long_categorized.xlsx`.
- `output/figures/choice_switch_control_kw_first.png` is AA's original of Fig. 16;
  the paper uses `04`'s regenerated `within_choice_switch_kw_first.png`.
- `05`'s similarity constants (94.6/51.2/29.9/14.4) are audited means from
  `../LLM_Similarity/memory_games_llm_recording.xlsx`, hard-coded, not read at runtime.
