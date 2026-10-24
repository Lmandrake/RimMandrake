# PIPELINE_TUNING_HARVEST_CAULDRON_VERDICTS

Data for the art-eval pipeline-tuning helper (the tuning itself is a separate helper's job; nothing here changed a prompt, policy or version).

Source sheet: Transient/biome_ffar/owner_escalations_cauldron_sheet_2026-10-24.html (his decisions savedAt 2026-10-24T07:08:32, writeCount 46).
Owner order: "Done with Art-eval shadow check — owner_escalations_cauldron_20261024. Remember to update the pipeline tuning, and fully enact."

Table (every judged picture, Opus band + finding codes with model severity/confidence, GPT answers, visible-height spread, canvas, his action, class):
D:\ClaudeWork\rimmandrake\pipeline_tuning\cauldron.md  (/mnt/d/ClaudeWork/rimmandrake/pipeline_tuning/cauldron.md)

Headline: 26 pictures; REJECT_OF_GOOD 10, AGREE 11, NOT_SHOWN 5, PASS_OF_BAD 0.
Codes behind rejects of good art: DEPARTURE_MISSING 8, F_SIZE_JUMP 7, F_INCONSISTENT 6, ALPHA_HALO 3, STYLE_OFF 3, STYLE_CARTOON 2.
Criteria-ledger entries: CL-035..CL-041 (one per subject).
Sibling sheets with the same shape: leaningscrub_1 (CL-019..025), leaningscrub_2 (CL-012..018), contagion (CL-026..034).

Observations (not applied):
1. Policy promotes polish-rated low-confidence Opus findings to blocking; GPT then confirms one (usually F_SIZE_JUMP) -> regen of art he picks.
2. F_SIZE_JUMP from the visible-height spread gate on long east profiles (see ART_EVAL_SIZEJUMP_TUNE_OVERBLOCK).
3. Live art REGENed on all 7; he kept live on BedBug, Mullgoth, Vexxiss.
4. No canvas check (ARTEVAL_REGEN_CANVAS_FIX_HARDCODED_SIZE): Vexxiss 512 for rule 1024 ("too low res"), Suush V_C 512 for rule 256.
5. Mullgoth round double count (ARTEVAL_ROUNDS_FIX_REJUDGE_DOUBLE_COUNT).
6. Replaced kept art not shown on the sheet (SHADOW_SHEET_WIDEN_REPLACED_KEPT_ART).
