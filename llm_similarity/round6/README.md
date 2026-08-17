# Round 6: joint-action vignette similarity

This folder contains the blinded inputs and the reproducible pipeline for rating the new joint-action vignettes.

## Design

- Games: DG-KW, UG, and TG.
- Frames: Control, Market, Aid, and Bonus, giving 12 game-by-frame contexts.
- Aid and Bonus reproduce the experimental order: the story comes first, followed by the corresponding cleaned abstract-game instructions.
- Survey logistics such as implementation probabilities, screen-transition markers, and later elicitation-task language are omitted. Substantive payoff and decision information is retained.
- Every context is rated against all 30 vignettes. The model sees only neutral context and vignette identifiers.
- The prompt requests independent absolute similarity ratings from 0 to 100. It does not ask the ratings to sum to a fixed total.

## Files and workflow

1. `01_build_anonymized_inputs.py` parses `joint_action_vignettes_classified.txt` and the cleaned source contexts from round 2. It writes:
   - `anonymized_vignettes.csv` (30 neutral vignette IDs and texts);
   - `anonymized_contexts.csv` (12 neutral context IDs and texts);
   - `anonymization_map.json` (private mapping used only after scoring).

2. `02_rate_similarity.py` sends each neutral context and all 30 neutral vignettes to an API model. Each context-replicate is a fresh call, and vignette order is independently permuted. Example commands:

   ```text
   python 02_rate_similarity.py --dry-run
   python 02_rate_similarity.py --provider anthropic --model MODEL_ID --replicates 3
   ```

   The corresponding API key must be set in the environment. No API keys are read from or saved to repository files. Parsed scores are written atomically to `similarity_ratings.csv`; full prompts, responses, and label mappings are retained in `transcripts/`. A hash of the exact blinded inputs and prompt version prevents a resumed run from mixing materials from different versions. If a transcript was saved immediately before an interruption, the next run recovers its scores without making another paid call.

3. `03_analyze_similarity.py` normalizes each repetition first, then averages repetitions within each model and gives each model equal weight. It retains two normalizations:
   - `weight_all30`: a vignette's mean absolute score divided by the sum across all 30 vignettes;
   - `weight_within_game`: a vignette's mean absolute score divided by the sum across the matching game's vignette pool.

   The requested primary figures use `weight_all30`, following the instruction to normalize by total similarity across all vignettes. Thus, the displayed bars for a game sum to the all-30 mass assigned to that game's vignette family. Conditional `weight_within_game` versions are also produced to isolate composition within the structural family. Run:

   ```text
   python 03_analyze_similarity.py
   ```

## Figure structure

- `control_similarity_distribution.png`: DG has M, S, and C blocks; UG and TG have M-C, M-D, S-C, S-D, C-C, and C-D blocks. Within each block, the individual personal (`P`) and anonymous-market (`K`) vignettes are separate bars. These primary plots use the all-30 denominator.
- `market_minus_control_similarity_differences.png`: the Market weight minus the Control weight for every corresponding bar.
- `aid_minus_bonus_similarity_differences.png`: the Aid weight minus the Bonus weight for every corresponding bar.

Each figure also has a `_within_game` counterpart using the conditional within-family denominator.

## In-task Codex exploratory ratings

`04_merge_codex_blind_ratings.py` validates and combines three blinded rating passes generated within a Codex task. The raters use only the two anonymized CSVs and the neutral prompt; the private mapping is reattached only after all scores are fixed. These passes are repeated judgments from the same Codex model family, not independent external models or human raters. They therefore provide an exploratory similarity estimate but not cross-model validation.

   The underlying plotted values and the full normalized rating table are saved in `output/`. `structural_family_shares.csv` reports how much of the all-30 similarity mass each context assigns to the DG, UG, and TG vignette families; this is the structural-matching diagnostic. The comparison data also retain differences in the unnormalized mean ratings, because a normalized-weight change can be caused by movements elsewhere in the vignette pool.
