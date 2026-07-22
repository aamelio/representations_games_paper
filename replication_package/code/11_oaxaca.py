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
variant), baseline-reference (ybar_c from the baseline condition of the comparison, Control
or Bonus - NG's "alloc media in control"), and pooled-reference (ybar_c from all four
conditions pooled - NG's "tutto il pooled sample"). Cells empty in one condition contribute
their observed-side mean to the representation component and zero to the behavior component.

Revision 2026-07-22 (AA's four T14 notes, construction agreed with SN):
  * pooled reference made internally consistent and exact: the belief-tercile edges are the
    ones computed on the two compared conditions (as in the rest of the table) and are
    applied to the four-condition pooled sample with open outer bins; the behavior component
    is the exact complement  beh = sum_c [qT_c (yT_c - ybar_c) - qB_c (yB_c - ybar_c)],
    so rep + beh = diff to machine precision. (The pre-revision construction cut pooled
    terciles on all four conditions - 14.5-31.9% of participants changed tercile label -
    and left log-only residuals up to +0.046; the displayed column moves <= 0.006.)
  * participant-level nonparametric bootstrap (B = 1000, seed 20260721; resampling within
    game x condition strata; terciles and the full decomposition recomputed in every draw).
    SEs are displayed under the mean difference and every level component; representation
    shares stay point estimates; the Aid-vs-Bonus TG share is suppressed (dash) because the
    total effect there is indistinguishable from zero.
  * "Control ref." header renamed "Baseline ref." (the baseline is Bonus, story == 2, in the
    Aid vs Bonus comparison). Both reference columns retained per NG's 2026-07-19 request.

Inputs:  data/player1_all_categorized.xlsx
Outputs: output/tables/oaxaca_catbelief.tex, oaxaca_catbelief_stats.txt
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
TABLES = HERE.parent / "output" / "tables"

CATS = ["Moral", "Self-interest", "Mutual Benefit / Cooperation"]
COMPARISONS = [("Market vs Control", 1, 0), ("Aid vs Bonus", 4, 2)]
GAMES = [("dgkw", "DG-KW"), ("ug", "UG"), ("tg", "TG")]

B = 1000
SEED = 20260721

L = []


def log(*s):
    line = " ".join(str(x) for x in s)
    L.append(line)
    print(line)


def two_cond_cells(dg, treated, baseline, game):
    """Two-condition sample with category x belief-tercile cells; returns (df, edges).

    Tercile edges (UG/TG) come from the two compared conditions; outer edges are opened to
    +-inf so the same cuts can be applied to the pooled sample.
    """
    two = dg[dg.story.isin([treated, baseline])].copy()
    if game == "dgkw":
        two["cell"] = two["category"].astype(str)
        return two, None
    two = two.dropna(subset=["beliefs_hp"])
    try:
        ter, bins = pd.qcut(two["beliefs_hp"], 3, labels=["low", "mid", "high"],
                            duplicates="drop", retbins=True)
        two["ter"] = ter
        edges = bins.astype(float).copy()
        edges[0], edges[-1] = -np.inf, np.inf
    except ValueError:
        two["ter"] = "all"
        edges = None
    two["cell"] = two["category"].astype(str) + " x " + two["ter"].astype(str)
    return two, edges


def pooled_cells(dg, edges, game):
    """Four-condition pooled sample assigned with the two-condition tercile edges."""
    if game == "dgkw":
        pool = dg.copy()
        pool["cell"] = pool["category"].astype(str)
        return pool
    pool = dg.dropna(subset=["beliefs_hp"]).copy()
    if edges is None:
        pool["ter"] = "all"
    else:
        pool["ter"] = pd.cut(pool["beliefs_hp"], edges, labels=["low", "mid", "high"])
    pool["cell"] = pool["category"].astype(str) + " x " + pool["ter"].astype(str)
    return pool


def moments(two, treated, baseline):
    """Cell shares and conditional means by condition, plus the mean difference."""
    qT = two[two.story == treated]["cell"].value_counts(normalize=True)
    qB = two[two.story == baseline]["cell"].value_counts(normalize=True)
    yT = two[two.story == treated].groupby("cell")["share_sent"].mean()
    yB = two[two.story == baseline].groupby("cell")["share_sent"].mean()
    diff = (two[two.story == treated]["share_sent"].mean()
            - two[two.story == baseline]["share_sent"].mean())
    return qT, qB, yT, yB, diff


def all_schemes(dg, treated, baseline, game):
    """diff and the three decompositions on one (game, comparison) sample.

    Returns dict with diff, n, sym_rep, sym_beh, base_rep, base_beh, pool_rep, pool_beh.
    Symmetrized and baseline-reference reproduce the published construction exactly;
    the pooled reference is the corrected (exact) 2026-07-22 construction.
    """
    two, edges = two_cond_cells(dg, treated, baseline, game)
    qT, qB, yT, yB, diff = moments(two, treated, baseline)
    pool = pooled_cells(dg, edges, game)
    ypool = pool.groupby("cell")["share_sent"].mean()
    cells = sorted(set(qT.index) | set(qB.index))

    sym_rep = sym_beh = base_rep = base_beh = pool_rep = pool_beh = 0.0
    for c in cells:
        qt, qb = qT.get(c, 0.0), qB.get(c, 0.0)
        yt, yb = yT.get(c, np.nan), yB.get(c, np.nan)
        y_avg = np.nanmean([yt, yb])
        # symmetrized (Shapley): reference mean = average of the two conditional means
        sym_rep += (qt - qb) * y_avg
        if np.isfinite(yt) and np.isfinite(yb):
            sym_beh += ((qt + qb) / 2) * (yt - yb)
        # baseline reference: conditional means held at the baseline condition
        base_rep += (qt - qb) * (yb if np.isfinite(yb) else y_avg)
        if np.isfinite(yt) and np.isfinite(yb):
            base_beh += qt * (yt - yb)
        # pooled reference (corrected): pooled means on two-condition cuts, exact complement
        yp = ypool.get(c, np.nan)
        pool_rep += (qt - qb) * yp
        if qt > 0:
            pool_beh += qt * (yt - yp)
        if qb > 0:
            pool_beh -= qb * (yb - yp)

    assert abs(pool_rep + pool_beh - diff) < 1e-9, "pooled decomposition must be exact"
    return dict(diff=diff, n=len(two), sym_rep=sym_rep, sym_beh=sym_beh,
                base_rep=base_rep, base_beh=base_beh,
                pool_rep=pool_rep, pool_beh=pool_beh)


def main():
    p1 = pd.read_excel(DATA / "player1_all_categorized.xlsx")
    p1["story"] = pd.to_numeric(p1["story"], errors="coerce")
    p1 = p1[p1.category.isin(CATS)].copy()

    order = [(c, t, b, g, gl) for (c, t, b) in COMPARISONS for (g, gl) in GAMES]

    # ------------------------------ point estimates ------------------------------ #
    rows = {}
    for comp, treated, baseline, game, glabel in order:
        dg = p1[p1.game == game]
        r = all_schemes(dg, treated, baseline, game)
        rows[(comp, glabel)] = r
        scheme = ("category only (no belief elicitation in the DG)" if game == "dgkw"
                  else "category x belief tercile")
        log(f"{comp:>18} {glabel:>6} ({scheme}): observed diff {r['diff']:+.3f}, N {r['n']}")
        for name, rep, beh in [("symmetrized", r["sym_rep"], r["sym_beh"]),
                               ("baseline-ref", r["base_rep"], r["base_beh"]),
                               ("pooled-ref", r["pool_rep"], r["pool_beh"])]:
            log(f"      {name:>12}: representation {rep:+.3f} ({rep / r['diff'] * 100:.0f}%), "
                f"behavior {beh:+.3f} ({beh / r['diff'] * 100:.0f}%), "
                f"residual {r['diff'] - rep - beh:+.3f}")

    # -------------------------------- bootstrap ---------------------------------- #
    log("")
    log(f"Participant-level bootstrap: B={B}, seed {SEED}, resampling within "
        f"game x condition strata; terciles and decomposition recomputed per draw.")
    rng = np.random.default_rng(SEED)
    game_idx = {}
    for g, gl in GAMES:
        dg = p1[p1.game == g]
        story_groups = {s: dg.index[dg.story == s].to_numpy()
                        for s in sorted(dg.story.dropna().unique())}
        game_idx[g] = (dg, story_groups)

    metrics = ("diff", "sym_rep", "sym_beh", "base_rep", "pool_rep", "sym_share")
    stats = {(comp, gl): {m: [] for m in metrics} for comp, t, b, g, gl in order}

    t0 = time.perf_counter()
    for _ in range(B):
        for g, gl in GAMES:
            dg_full, story_groups = game_idx[g]
            picks = np.concatenate([rng.choice(idx, size=len(idx), replace=True)
                                    for idx in story_groups.values()])
            dgb = dg_full.loc[picks]
            for comp, treated, baseline in COMPARISONS:
                r = all_schemes(dgb, treated, baseline, g)
                st = stats[(comp, gl)]
                for m in ("diff", "sym_rep", "sym_beh", "base_rep", "pool_rep"):
                    st[m].append(r[m])
                st["sym_share"].append(r["sym_rep"] / r["diff"]
                                       if abs(r["diff"]) > 1e-9 else np.nan)
    runtime = time.perf_counter() - t0

    def se_ci(a):
        a = np.asarray(a, dtype=float)
        return (np.nanstd(a, ddof=1),
                np.nanpercentile(a, 2.5), np.nanpercentile(a, 97.5))

    boot = {}
    log("")
    log(f"{'Comparison':>18} {'Game':>6} | metric        {'SE':>9} {'CI2.5':>9} {'CI97.5':>9}")
    for comp, t, b, g, gl in order:
        st = stats[(comp, gl)]
        boot[(comp, gl)] = {}
        for m in ("diff", "sym_rep", "sym_beh", "base_rep", "pool_rep"):
            se, lo, hi = se_ci(st[m])
            boot[(comp, gl)][m] = se
            log(f"{comp:>18} {gl:>6} | {m:<12} {se:9.4f} {lo:+9.4f} {hi:+9.4f}")

    log("")
    log("Symmetrized representation-share diagnostics (rep/diff across draws):")
    log(f"{'Comparison':>18} {'Game':>6} | {'median%':>9} {'p2.5%':>10} {'p97.5%':>10} "
        f"{'%degenerate':>12}")
    degenerate = {}
    for comp, t, b, g, gl in order:
        sh = np.asarray(stats[(comp, gl)]["sym_share"], dtype=float)
        bad = np.isnan(sh) | (sh < 0.0) | (sh > 1.5)
        degenerate[(comp, gl)] = bad.mean() * 100
        log(f"{comp:>18} {gl:>6} | {np.nanmedian(sh) * 100:9.1f} "
            f"{np.nanpercentile(sh, 2.5) * 100:10.1f} "
            f"{np.nanpercentile(sh, 97.5) * 100:10.1f} {bad.mean() * 100:12.1f}")
    log("")
    log(f"Bootstrap wall-clock: {runtime:.2f} s")

    # ---------------------------------- table ------------------------------------ #
    def f3(v):
        return f"{v:+.3f}"

    def fse(v):
        return f"({v:.3f})"

    dash_key = ("Aid vs Bonus", "TG")  # total effect ~0: share suppressed
    body = []
    for comp, t, b, g, gl in order:
        r = rows[(comp, gl)]
        se = boot[(comp, gl)]
        pct = ("---" if (comp, gl) == dash_key
               else f"{r['sym_rep'] / r['diff'] * 100:.0f}\\%")
        body.append(
            f"{comp} & {gl} & {f3(r['diff'])} & {f3(r['sym_rep'])} & "
            f"{f3(r['sym_beh'])} & {pct} & {f3(r['base_rep'])} & "
            f"{f3(r['pool_rep'])} & {r['n']} \\\\")
        body.append(
            f" & & {fse(se['diff'])} & {fse(se['sym_rep'])} & {fse(se['sym_beh'])} & "
            f"& {fse(se['base_rep'])} & {fse(se['pool_rep'])} & \\\\")
        body.append(r"\addlinespace[2pt]")
    body = body[:-1]  # no trailing addlinespace before \bottomrule

    tg_aid = rows[dash_key]
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
Comparison & Game & $\Delta$ mean & Repr. & Behav. & Repr. \% & Baseline ref. & Pooled ref. & $N$ \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\begin{flushleft}
\footnotesize Notes: Pre-registered symmetrized (Shapley/Oaxaca--Blinder) decomposition of the difference in mean Player 1 actions between conditions into a component due to the distribution of representations and a component due to behavior conditional on the representation. Representation cells are the stated category interacted with terciles of the hypothetical belief (ultimatum and trust games, with terciles computed within game on the two conditions compared); the dictator game has no belief elicitation, so its cells are categories only. The last two columns recompute the representation component holding conditional means fixed at the baseline condition of each comparison (Baseline ref.: Control or Bonus) and at the four-condition pooled sample (Pooled ref.), with the two-condition tercile edges applied to the pooled sample; each reference scheme decomposes the mean difference exactly. Cells empty in one condition contribute their observed mean to the representation component. Bootstrap standard errors in parentheses ($B=1{,}000$ participant-level draws within game $\times$ condition strata; terciles and the full decomposition recomputed in each draw). Representation shares are point estimates of the symmetrized split; the share is not reported for the trust-game story comparison, where the total effect is """ + f3(tg_aid["diff"]) + r""" (bootstrap SE """ + f"{boot[dash_key]['diff']:.3f}" + r""") and the share is undefined or degenerate in """ + f"{degenerate[dash_key]:.0f}" + r"""\% of bootstrap draws. Classified sample with non-missing beliefs where applicable.
\end{flushleft}
\end{table}
"""
    (TABLES / "oaxaca_catbelief.tex").write_text(tex)
    (TABLES / "oaxaca_catbelief_stats.txt").write_text("\n".join(L))
    print(f"\nwrote {TABLES / 'oaxaca_catbelief.tex'} and oaxaca_catbelief_stats.txt")


if __name__ == "__main__":
    main()
