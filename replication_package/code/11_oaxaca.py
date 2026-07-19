#!/usr/bin/env python3
"""Preregistered Blinder-Oaxaca decomposition with representation = category x belief cells
(NG Section-5 comment, 2026-07-19; AsPredicted #261370 and #286187, "symmetrized
(Shapley/Oaxaca-Blinder) decomposition").

Representation cells: stated category x tercile of the hypothetical belief (UG, TG; terciles
computed within game on the two conditions being compared). DG-KW has no belief elicitation:
category-only cells (stated in the notes). For each comparison (Market vs Control, Aid vs
Bonus) and game, the mean-action difference decomposes into:

  representation component  =  sum_c dq_c * ybar_c    (distribution of representations moves)
  behavior component        =  sum_c q_c * dybar_c    (behavior conditional on representation moves)

three reference schemes: symmetrized (Shapley: averages both paths - the preregistered
variant), control-reference (ybar_c from the baseline condition, q from the treated - NG's
"alloc media in control"), and pooled-reference (ybar_c from all four conditions pooled -
NG's "tutto il pooled sample"). Cells empty in one condition contribute their observed-side
mean to the representation component and zero to the behavior component.

Inputs:  data/player1_all_categorized.xlsx
Outputs: output/tables/oaxaca_catbelief.tex, oaxaca_catbelief_stats.txt
"""

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
TABLES = HERE.parent / "output" / "tables"

CATS = ["Moral", "Self-interest", "Mutual Benefit / Cooperation"]
COMPARISONS = [("Market vs Control", 1, 0), ("Aid vs Bonus", 4, 2)]
GAMES = [("dgkw", "DG-KW"), ("ug", "UG"), ("tg", "TG")]

L = []


def log(*s):
    line = " ".join(str(x) for x in s)
    L.append(line)
    print(line)


def cellize(d, game):
    """Assign representation cells: category x belief tercile (UG/TG) or category (DG)."""
    d = d.copy()
    if game == "dgkw":
        d["cell"] = d["category"]
        return d, "category only (no belief elicitation in the DG)"
    d = d.dropna(subset=["beliefs_hp"])
    try:
        d["ter"] = pd.qcut(d["beliefs_hp"], 3, labels=["low", "mid", "high"], duplicates="drop")
    except ValueError:
        d["ter"] = "all"
    d["cell"] = d["category"].astype(str) + " x " + d["ter"].astype(str)
    return d, "category x belief tercile"


def decompose(d, treated, baseline, ref_means):
    """Two-way decomposition given a dict of reference cell means."""
    qT = d[d.story == treated]["cell"].value_counts(normalize=True)
    qB = d[d.story == baseline]["cell"].value_counts(normalize=True)
    yT = d[d.story == treated].groupby("cell")["share_sent"].mean()
    yB = d[d.story == baseline].groupby("cell")["share_sent"].mean()
    cells = sorted(set(qT.index) | set(qB.index))
    rep = beh = 0.0
    for c in cells:
        qt, qb = qT.get(c, 0.0), qB.get(c, 0.0)
        yt, yb = yT.get(c, np.nan), yB.get(c, np.nan)
        ybar_ref = ref_means.get(c, np.nanmean([yt, yb]))
        y_avg = np.nanmean([yt, yb])
        rep += (qt - qb) * (ybar_ref if np.isfinite(ybar_ref) else y_avg)
        if np.isfinite(yt) and np.isfinite(yb):
            beh += ref_means["__q__"].get(c, (qt + qb) / 2) * (yt - yb)
    return rep, beh


def main():
    p1 = pd.read_excel(DATA / "player1_all_categorized.xlsx")
    p1["story"] = pd.to_numeric(p1["story"], errors="coerce")
    p1 = p1[p1.category.isin(CATS)].copy()

    rows = []
    for comp, treated, baseline in COMPARISONS:
        for game, glabel in GAMES:
            dall = p1[p1.game == game]
            d, scheme = cellize(dall[dall.story.isin([treated, baseline])], game)
            dpool, _ = cellize(dall, game)  # all four conditions, for pooled reference
            diff = (d[d.story == treated]["share_sent"].mean()
                    - d[d.story == baseline]["share_sent"].mean())

            qT = d[d.story == treated]["cell"].value_counts(normalize=True)
            qB = d[d.story == baseline]["cell"].value_counts(normalize=True)
            refs = {
                "symmetrized": {"__q__": ((qT + qB) / 2).fillna(qT).fillna(qB).to_dict()},
                "control-ref": {**d[d.story == baseline].groupby("cell")["share_sent"]
                                .mean().to_dict(), "__q__": qT.to_dict()},
                "pooled-ref": {**dpool.groupby("cell")["share_sent"].mean().to_dict(),
                               "__q__": ((qT + qB) / 2).to_dict()},
            }
            out = {}
            for name, ref in refs.items():
                ref.setdefault("__q__", {})
                rep, beh = decompose(d, treated, baseline, ref)
                out[name] = (rep, beh)
            rows.append(dict(comparison=comp, game=glabel, scheme=scheme, dmean=diff,
                             n=len(d), **{f"{k}_{p}": v[i] for k, v in out.items()
                                          for i, p in enumerate(["rep", "beh"])}))
            log(f"{comp:>18} {glabel:>6} ({scheme}): observed diff {diff:+.3f}, N {len(d)}")
            for name, (rep, beh) in out.items():
                log(f"      {name:>12}: representation {rep:+.3f} ({rep / diff * 100:.0f}%), "
                    f"behavior {beh:+.3f} ({beh / diff * 100:.0f}%), "
                    f"residual {diff - rep - beh:+.3f}")

    res = pd.DataFrame(rows)

    def f3(v):
        return f"{v:+.3f}"

    body = []
    for _, r in res.iterrows():
        pct = r.symmetrized_rep / r.dmean * 100 if r.dmean != 0 else np.nan
        body.append(
            f"{r.comparison} & {r.game} & {f3(r.dmean)} & {f3(r.symmetrized_rep)} & "
            f"{f3(r.symmetrized_beh)} & {pct:.0f}\\% & {f3(r['control-ref_rep'])} & "
            f"{f3(r['pooled-ref_rep'])} & {r.n} \\\\")
    tex = r"""\begin{table}[!htbp]
\centering
\footnotesize
\renewcommand{\arraystretch}{1.15}
\caption{\textbf{Decomposition of Treatment Effects into Representation and Behavior Components}}
\label{tab:oaxaca_catbelief}
\begin{tabular}{ll c cc c cc c}
\toprule
& & & \multicolumn{3}{c}{Symmetrized (preregistered)} & \multicolumn{2}{c}{Representation comp.} & \\
\cmidrule(lr){4-6}\cmidrule(lr){7-8}
Comparison & Game & $\Delta$ mean & Repr. & Behav. & Repr. \% & Control ref. & Pooled ref. & $N$ \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\begin{flushleft}
\footnotesize Notes: Pre-registered symmetrized (Shapley/Oaxaca--Blinder) decomposition of the difference in mean Player 1 actions between conditions into a component due to the distribution of representations and a component due to behavior conditional on the representation. Representation cells are the stated category interacted with terciles of the hypothetical belief (ultimatum and trust games, with terciles computed within game on the two conditions compared); the dictator game has no belief elicitation, so its cells are categories only. The last two columns recompute the representation component holding conditional means fixed at the baseline condition (Control ref.)\ and at the four-condition pooled sample (Pooled ref.). Cells empty in one condition contribute their observed mean to the representation component. Classified sample with non-missing beliefs where applicable.
\end{flushleft}
\end{table}
"""
    (TABLES / "oaxaca_catbelief.tex").write_text(tex)
    (TABLES / "oaxaca_catbelief_stats.txt").write_text("\n".join(L))
    print(f"\nwrote {TABLES / 'oaxaca_catbelief.tex'} and oaxaca_catbelief_stats.txt")


if __name__ == "__main__":
    main()
