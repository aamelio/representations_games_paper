# CLAUDE.md — representations_games_paper

## Paper Summary
"Beyond Social Preferences: Mental Representations in Games" (Amelio, Gennaioli, Nunnari).
Model + large pre-registered Prolific experiments (DG/UG/TG, ~12,750 participants): players
retrieve mental representations of games (attention weights over own earnings / surplus / sharing
norm + beliefs about the counterpart); context manipulations (market frame, Aid/Bonus stories)
shift representations, actions, beliefs, and forecast errors coherently.

## Canonical Files
- `main.tex` — the paper, **version 1.1** (SN, 2026-07-20). **Compile this.**
- `main_v1.tex` — **version 1.0**: the copy SENT TO NG, the one his 2026-07-19 comments are on
  (the tracker calls it v0.1). This IS the frozen pre-NG-revision backup. Pre-equal-payoff-anchor
  (still equal-split at l.142), so it is also the witness to the old model spec. Never edit.
- NOTE: the `% paper_v2.tex --- Version 2.0 skeleton ... paper_v1.tex remains the v1.1 record`
  header on line 1–2 is STALE and identical in both files — do not read version numbers off it.
  `paper.tex`, `paper_v1.tex`, and `main_v2.0_pre_ng_revision.tex` do not exist in this project.
  There is NO frozen pre-NG-revision backup on disk; that state lives only in Dropbox history.
- `model.tex` — companion model note (NG's Model 2.0), kept in sync with Section 2.
- `ng_comments_tracker.md` — authoritative comment-by-comment record of the NG revision round.

## Build
`latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` then
`grep -E "(undefined|Undefined)" main.log` must be empty. A PostToolUse chktex hook lints every
edited .tex (incl. `\input`-ed generated tables); suppress false positives with `% chktex NN`
(max two numbers per comment) or `% chktex-file NN`.

## Directory Layout
- `replication_package/` — data (`data/player{1,2}_all_categorized.xlsx`; condition coding
  0=Control 1=Market 2=Bonus 4=Aid), pipeline `code/01–12_*.py`, outputs in `output/{figures,tables}`
- `llm_similarity/` — May round-1 materials + `round2/` (vignette-based contexts×categories module,
  ready to run) + `similarity_survey_design.md` (human survey, Module B)
- `instruments/` — verbatim game instructions and stories
- `preregistrations/` — AsPredicted #261370 (DG), #286187 (UG/TG)
- `literature/` — key PDFs

## Status
- **Stage:** NG round COMPLETE + post-round polish COMPLETE (2026-07-19, fourth session): new
  abstract (keywords capitalized), §5 restructured (5.1 accounting / 5.2 Surplus and Inequality /
  5.3 circling back), four instability figures → one 2×2 panel (fig:instability_all), archive
  comments stripped (tracker = sole archive), round-1 raters named, instruction typos fixed,
  DISPARITY MODEL CUT from the paper (single-model architecture; blocks commented, grep
  "CUT 2026-07-19") and folded verbatim into model.tex Part II. main.tex 109 pp. + model.tex
  47 pp. (Part I Model 2.0 + Part II disparity note), both compile clean, 0 undefined refs.
  **2026-07-20 (second session):** NG email rewritten section by section with SN (numbering
  corrected to NG's own five general comments; every claim re-verified against outputs) and
  §3.2 gained the category-level calibration clause; main.tex recompiled clean, 109 pp.,
  0 undefined. **2026-07-20 (third session):** coauthor email FINALIZED as
  `Dropbox/Downloads/email_ng_response_final.txt` — SN's condensed version verified
  claim-by-claim (all numbers correct), paper pointers inserted from main.aux, SN hand-edited
  after delivery; supersedes `email_ng_response.md`.
- **Current task:** SN sends `Dropbox/Downloads/email_ng_response_final.txt` (both 07-20 loose
  ends resolved: Oaxaca sits in Comment 4; quotes table linked via the section-4 opener "The
  memory-consistency check you asked for"; table/figure numbers are from the current compile —
  re-check them only if main.tex recompiles before sending); revokes the round-2 Anthropic API
  key (last used 2026-07-20 for the unclassified runs); deletes the redundant
  `Downloads/Gennaioli-2`, `Downloads/representations_paper_archive`, and the ported
  project-root `player1_examples_method_email_package/` folder. AA reply on the unclassified
  exercise SENT 2026-07-20.
- **Next steps:** coauthor reactions (anchor framing, equalization placement, DG-LT,
  disparity-cut veto, unclassified footnote); 3-model similarity grid (needs GPT/Gemini keys);
  human survey Module B via /preregistration (TG similarity nulls = sharpest target); M1-LOO
  stays held out (restorable, grep "HELD OUT").
- **Blockers:** none. Only SN actions pending: send the NG email, revoke the API key, delete
  the two Downloads folders.

## Decision Log
- 2026-07-19: Terminology unified per SN — "conditions" (four cells), "treatments" (the two
  manipulations), "within-subject designs"; never "arms".
- 2026-07-19: Calibration headline = FOC-inversion route; two-point route fails validity
  (a<0, a+b=1.7–2.6) and is kept as a diagnostic of chosen-action optimism (+16–20pp).
- 2026-07-19: DG-LT stays in the similarity-gradient table (defended in text); DG-LT rows of the
  heterogeneity tables moved to Appendix app:heterogeneity. Alternative (all DG-LT to §5.2) to be
  mentioned to NG.
- 2026-07-19: P2 accounting keeps the fitted-P1-action spec; §5.1 footnote rewritten to the
  verified 0.88-vs-0.62 claim (with vs without the P1-action channel) — the old
  "representation-predicted" description had no generating code.
- 2026-07-19: P2 protest-model fit (p2_schedules.tex) HELD out of the paper pending coauthor
  discussion: TG returned shares rise with the send (contra rem:return); proposal = payoff-
  equalization target for the actual receiver, rem:return kept for sender beliefs.
- 2026-07-19: Similarity round 2 = vignette-based design, classification-scheme categories,
  overall-situational similarity instruction (not May's structural-only), 10 contexts incl. LT;
  single-model Opus 4.8 run acceptable for the working exhibit, 3-model grid before paper claims.
- 2026-07-19: Intro rewritten world-first per NG; 12 verified references added to references.bib.
- 2026-07-19: Round-2 protocol (SN): generator = Fable 5, raters = Opus 4.8 + adaptive thinking +
  effort high, 3 permuted sets; no model fallbacks (refusal/truncation aborts loudly); Opus is the
  headline rater, other models enter robustness only (filter in 04_analysis.py).
- 2026-07-19: Vignette freeze v2 = generator output verbatim except C8 "craft fairs"→"craft
  markets"; M1 kept; the v1 (craft-fairs) run archived in `v1_craftfairs/` as test-retest (r=.994).
- 2026-07-19: M1 leave-one-out HELD OUT of the paper text per SN (full set = main analysis);
  preserved in `05_loo_m1.py` + commented main.tex passages (grep "HELD OUT"); both raters show
  the same pattern (only Bonus–Moral moves ~5pts; H5 fit survives).
- 2026-07-19: TG similarity nulls (market shifts ≈0; receiver split flat) reported openly in §3.3
  as the F_c/availability channel, flagged as the sharpest item for the human survey.
- 2026-07-19: Held item 1 resolved as SN's symmetric horse race (both objectives tested on both
  objects, no ex-ante split): actual Moral-good/MBC receivers ≈ payoff equalization (slopes +0.28
  reject the declining norm-target family), beliefs ≈ flat/norm-target (medians 0.00) — wedge =
  TG forecast error; model propositions untouched; text insertion awaits the coauthor call.
- 2026-07-19: Fable robustness accepted at 2/3 conversations after 4 consecutive msg0 safety-filter
  refusals (incl. a seeded substitute permutation, set 4 in 03_api_runner.py); documented verbatim
  in app:similarity_vignettes; retry option open.
- 2026-07-19 (third session): receiver-side equalization INSERTED in app:receiver (held 3b closed):
  s^e(t) return anchor (inverse of t^e), tab:p2_schedules, moral floor below t=1/4 disclosed;
  placement = appendix per the primitives convention, promote-to-§5.1 alternative in the NG email.
- 2026-07-19 (third session): source comments carry current state only — the tracker is the
  archive (SN); old calibration TODO replaced with clean text, AA 07-11 attribution question moot.
- 2026-07-19 (third session): NG communication = one consolidated response email
  (`email_ng_response.md`, drafted), no separate notes; amendments presented as implemented
  changes with receipts (16/17 scripts), three decision points posed to coauthors.
- 2026-07-19 (third session): EQUAL-PAYOFF ANCHOR IMPLEMENTED (SN decision, no NG pre-approval;
  no new frozen backup — pre-NG version + Dropbox history + tracker §2 record suffice; goes into
  the consolidated NG email). TG norm anchor = t^e(s); zero new parameters; §2/§3.2/§4.2 + all
  proofs + model.tex + 08 (re-run, 1000/1000) + 05 note synced; TG attenuation now uniform
  .15–.22, anomaly sentence deleted; full-send spike explained (censored anchor, 30.5%→52.0%);
  both docs compile clean. Dry run `17_tg_anchor_dryrun.py`; record in tracker §2. rem:return
  kept as belief foundation; receiver-side equalization insertion still held for the call (3b).
- 2026-07-19 (third session): TG Moral belief-slope anomaly analyzed (`16_moral_slope_check.py`,
  HELD for the call): misclassified-cooperators reading untenable (pi needed 1.2+/0.6 vs ~9%
  measured via the memory detector, which itself validates: pure vs mixed Morals p=.002); the
  MBC cell's own excess (obs .264 vs pred .000) plus the receiver horse race point instead to
  payoff-equalization-at-expected-return targets in the TG — one amendment resolving held items
  1, 3b, and the anomaly. SN decides framing on the coauthor call; paper text untouched.
- 2026-07-19 (third session): P6 EXECUTED with AA's hpmin microdata. Memory texts classified into
  the new scheme with Claude Opus 4.8 (batch API, `14_hp_classification.py`), prompt verbatim except
  a two-sentence preamble adaptation (texts are situations, not justifications); classifier swap
  validated on 800 stratified reasons answers (agreement .833, κ .777 — above the human benchmark,
  same MBC-boundary confusions) — doubles as the deferred cross-model robustness check of the
  classification rules. Person-level results (`15_hp_person_level.py`): modal memory category =
  stated-reason category in every row (63.4%, κ .39; Control .805); high-SP memories 38.7% (Moral
  reasons) vs 11.1% (SI); market moves pre-decision memories coherently (Moral 68→19.2). Inserted:
  app:hp closing paragraph + tab:hp_person_level + §3.2 sentence; hpmin selection caveat disclosed.
- 2026-07-19 (third session): generators 01/05/06 synced to the "conditions" terminology; 06 and 05
  re-run and ALL emitted .tex tables verified byte-identical to the hand-patched versions (four 05
  tables briefly clobbered during verification were restored from backup before the final sync).
- 2026-07-19 (third session): Fable third conversation COMPLETED as set 6 (seed 20260725, found
  by a pre-committed successor-seed probe hunt; 11 total msg0 refusals across 8 orderings). Probes
  proved the filter's false positives stochastic per request (identical text refused then
  accepted), falsifying both the sticky-state and the deterministic-ordering diagnoses and making
  fixed-permutation retries selection-free. 3-conversation check r=.982, mean |diff| 4.9; TG null
  intact (+1.6). Appendix check two rewritten with the full refusal tally; 04_analysis.py note
  now conditional; tracker updated.
- 2026-07-19 (fourth session): Full-paper polish per SN — new abstract (SN's five notes: general
  attention phrasing, no "quantitatively", "Overall, our findings suggest…"; Keywords
  capitalized); §4.1/§4.2 redundancies trimmed; §3.1 validation footnote slimmed; §3.2 heads
  sentence-cased; calibration paragraph split.
- 2026-07-19 (fourth session): §5 restructured — 5.1 "Accounting for Treatment Effects and
  Heterogeneity", surplus split out as 5.2 "Surplus and Inequality" (label sec:surplus kept;
  two §2 refs repointed), Circling Back = 5.3.
- 2026-07-19 (fourth session): Four predicted-vs-actual figures → one 2×2 panel
  (fig:instability_all); single-panel figures + their generating calls kept commented in
  main.tex and script 02 (re-run verified: tables byte-identical, PNGs pixel-identical).
- 2026-07-19 (fourth session): Archive comments stripped from main.tex (tracker = sole archive);
  kept: TODOs, HELD OUT blocks, constraint one-liners, build/layout comments, the §2
  sympy-corrections header. Note: `% chktex-file` takes ONE warning number per comment.
- 2026-07-19 (fourth session): Round-1 similarity raters named in §3.3 (GPT-5.5 Thinking, Claude
  Opus 4.7, Gemini 3 Pro); app:instructions typos fixed per SN ("decision affects", "broker you
  will") — verbatim preservation overridden; recheck against screens if ever disputed.
- 2026-07-19 (fourth session): DISPARITY MODEL CUT from the paper (SN: single-model architecture;
  the alternative did no empirical work and, with its development external, broke
  self-containment): App J + §2 Remark + pointer removed, preserved commented (grep
  "CUT 2026-07-19"); NG's cooperative-proposers tension VERIFIED and recorded there (control UG
  MBC offer 56.8% [47.4, 66.2] — highest of the three categories — vs disparity+projection's
  low-offer prediction); veto line in the NG email.
- 2026-07-19 (fourth session): Disparity model's full development FOLDED into model.tex as
  Part II (verbatim; II.-prefixed numbering; app:proofs_disparity; preface maps ω_o/ω_e/ω_d to
  σ/ρ−σ/μ); model.pdf 47 pp., 0 undefined, chktex clean. Downloads/Gennaioli-2 (July-16 project
  snapshot) and Downloads/representations_paper_archive are now redundant — SN deletes.
- 2026-07-19 (fourth session): Conclusions learning-paragraph TODO retired — the ask was NG's
  July-9 outline, all three elements are already in the text, and no July-19 comment touches the
  Conclusions; flagged in the email for the call.
- 2026-07-19 (fourth session): AA confirmed the within-subject inventory ("è come dice Claude"):
  three designs × 600 fielded via two Qualtrics surveys (the market survey contains both KW and
  LT); no paper change needed; app:within restructure guard lifted.
- 2026-07-19 (fourth session): Internal-files policy (SN): tracker + NG email live in
  Dropbox/Downloads deliberately (outside the Overleaf sync); the GPT-4.1/Opus-4.8 classifier
  split judged fine as disclosed and validated in app:hp — optional GPT-4.1 re-classification
  of the hp texts only if a referee insists.
- 2026-07-20: AA's example-based forced classification of the 309 unclassified P1 Control/Market
  answers EXECUTED and inserted as a robustness footnote in §4.2 (sec:market_control) + forward
  pointer in the §3.2 residual footnote; main.tex compiles clean (109 pp., 0 undefined).
  Headline classifier Opus 4.8 per protocol (AA's Sonnet 4.6 = cross-check; LOO on the 95
  reference examples 84%/83%, κ≈.71 — but 92–97% where all three forced raters agreed vs 73–79%
  where the LLM matched one RA). Fold-in moves every Market−Control category effect ≤5.0pp
  (max DG-KW Self-interest 4.97), no sign changes; robust to model swap and to the earlier
  forced pass. Account: unclassified Market answers are shorter (15 vs 22 words), 92% mention
  no counterpart (vs 46% classified), two-thirds Self-interest when forced, transfers slightly
  below classified same-condition participants — the far end of the counterpart-abstraction
  shift, coherent with the hp residual rising 11.8→43.4 under Market. Rescued labels are
  AGGREGATE-GRADE ONLY (agreement on the 214 hard cases: .81 Opus–Sonnet, .70/.62 vs earlier
  pass) — never for person-level analyses. Scripts 18/19 + AA's three input workbooks now in
  the replication package (outputs in output/unclassified/, every footnote number in
  foldin_summary.txt); AA's original folder droppable (email attachment = provenance copy).
  NOTE: an early session-folder version of the descriptives had an index-alignment bug
  ("equal length" was wrong — residual answers are ~7 words shorter); scripts 18/19 are the
  corrected, authoritative versions. Reply SENT 2026-07-20; SN discards the draft file after
  sending (its earlier mid-session "disappearance" was SN's own deletion, not a sync fault).
- 2026-07-20: NG email amended with a §4 paragraph on the unclassified robustness exercise
  (credited as AA's initiative: fold-in ≤5pp / no sign changes, LOO 84% κ=.72, 92% no-counterpart
  account) + scripts 18/19 and foldin_summary.txt added to the attachments footer.
- 2026-07-20: `main (Salvatore Nunnari's conflicted copy).out` (Dropbox sync artifact of the
  regenerated hyperref file) deleted; sole conflicted copy in the project.
- 2026-07-20 (second session): NG email section 2 RENUMBERED to NG's own general comments
  (tracker order: 1 similarity, 2 calibration, 3 P2 foundation, 4 weights×beliefs, 5 motivation
  + references). The draft had labelled model-section discipline "C1" — that is page-by-page P2
  (p.11), not a general comment — while Comment 1, the similarity round, sat buried in a
  half-sentence under "Also inserted". Similarity promoted to Comment 1 as the round's main
  addition; model-section discipline demoted to the page-by-page highlights; the preregistered
  Oaxaca (P17) folded into Comment 4, whose own result is a null. All 17 page-by-page items
  verified ☑ in the tracker, so "I tackled all your other comments" is supportable.
- 2026-07-20 (second session): main.tex §3.2 calibration paragraph now states the identification
  assumption explicitly — moments come from different participants (each plays a single game),
  so the calibration imposes that a category carry the same attention profile wherever retrieved.
  Rationale: the chain is recursive (DG transfer → σ/μ, since ρ is idle there; + TG send+belief
  → ρ/μ; + UG FOC + reference belief → (a,b)), so category-level pooling is FORCED by
  identification, not chosen for cross-game prediction. Compiles clean, 109 pp., 0 undefined.
- 2026-07-20 (second session): CANONICAL FILES CORRECTED (SN): `main.tex` = v1.1, `main_v1.tex`
  = v1.0. The `% paper_v2.tex --- Version 2.0 skeleton ... paper_v1.tex remains the v1.1 record`
  header on line 1–2 is STALE and IDENTICAL in both files — never read version numbers off it.
  `paper.tex`, `paper_v1.tex`, `main_v2.0_pre_ng_revision.tex` do not exist here. The frozen
  pre-NG-revision backup DOES exist — it is `main_v1.tex`, the copy sent to NG and the one his
  comments are on (SN, 2026-07-20); no new freeze needed. Stale headers inside the two .tex
  files left untouched pending SN.
- 2026-07-20 (second session): verified for the email — Market share of TG senders with believed
  return ≥ 1/2 is 52.0% (Control 30.5%); script 17 emits only the Control figure, so the Market
  number was recomputed from `player1_all_categorized.xlsx` (all TG senders with a belief;
  classified-only gives 52.4%). Calibration cross-checks: Moral predicted/observed belief slope
  0.113/0.306, MBC 0.000/0.264; similarity Market−Control Moral −34.2/−29.5/−25.0 (KW/LT/UG),
  TG +0.6; H5 slope .0122 (se .0025), R²=.59, N=18.
- 2026-07-20 (second session): five claim corrections applied to the email drafts, do not let
  them regress — (a) the old anchor's full-send corner was reachable by ANY low-μ sender
  (material or cooperative), not only "optimistic selfish" ones; what it could never deliver is
  a norm-dominated sender at the maximum; (b) the two elicited belief points violate a LINEAR
  probability schedule (p(1)>1), not every schedule — a curved one could fit both; (c) the
  similarity exercise correlates with reasons-based CATEGORY SHARES, not behaviour/transfers;
  (d) in the overidentifying test the held-out object is the chosen-offer BELIEF — the chosen
  offer itself is used, via the optimality condition; (e) the anchor censors at s ≥ 1/2 ("at
  least half"), not "more than half" — at exactly 1/2 the anchor equals the full send, and the
  30.5%/52.0% shares were computed with >=. Also: the coauthor is **Andrea** Amelio (a draft
  had "Alessandro", fabricated from the initials "AA").
- 2026-07-20 (second session): "excessively optimistic" must always carry its benchmark — the
  11–23pp gap is optimism relative to the proposer's OWN coherent schedule at her chosen action,
  not relative to reality; against actual behaviour beliefs UNDERSHOOT acceptance (§4.3), so the
  unqualified phrasing reads as contradicting the forecast-error section.
- 2026-07-20 (third session): coauthor email FINALIZED as
  `Dropbox/Downloads/email_ng_response_final.txt` (supersedes `email_ng_response.md`): SN's
  condensed 4-section version (Italian opener + English) verified claim-by-claim against
  tracker/main.tex/outputs — every number correct, incl. newly pinned ones (old-anchor SI ratio
  0.38 from `tg_anchor_dryrun_stats.txt`; UG decomposition 60% composition vs TG 14%; residual
  shares 2.4%→13.0% from `foldin_summary.txt`) — then paper pointers inserted from main.aux
  (Tables 1/2/4/6/13/14/16/22/38; Figures 5–9, 11, 12, 17; Appendices B/C/D/F/H; NG's "Fig 10"
  = v1.1 Figure 11 fig:player2_hypothetical); word-diff confirmed pointer-only changes; SN
  hand-edited after delivery. Pointers are current-compile — re-verify if main.tex recompiles.
- 2026-07-20 (third session): SN's email calls — the .md draft's decision-points block,
  disparity veto line, and attachments footer NOT carried over (changes presented as done;
  decision points move to the coauthor call); LLM raters disclosed in Comment 1 with the
  receiver-type vignettes added (8×3 sender + 2 per type = 32); P6 halves linked (section-4
  opener "The memory-consistency check you asked for"; objects described as pre-decision memory
  texts); interaction ratios stated as "1-2 points" (UG .43→.44, TG .62→.64).
- 2026-07-20 (third session): full-send bullet clarified — belief ≥ 1/2 makes the full send the
  unique payoff-equalizing action, so the norm itself points to the corner and the belief
  threshold ties the 30.5%→52.0% belief shift to the 16%→27% corner mass; replacement text
  supplied, SN applied it by hand.
