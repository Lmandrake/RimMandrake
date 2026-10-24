# PYRELANDS_ART_AUDIT_GPT_UNKEPT_REDO_LIST

Sources: Transient/gpt_biome_art_review_2026-10-24.md (digest) and D:\ClaudeWork\rimmandrake\gpt_biome_review\Pyrelands.md (full review; raw answers in raw/). Everything below is GPT (gpt-6.1-sol) opinion; nothing was acted on.

Rows where GPT says redo/cut and the owner has NO keep on record. Filed as a FINDING, not queued: the art rule (memory 'Queue art only for NONE/PLACEHOLDER/DONOR') needs the destination state confirmed from the art ledger first, and that was not done here. Next step: confirm each row's state in the art ledger; NONE/PLACEHOLDER/DONOR may be queued, a live art-eval-pipeline redraw is shown to the owner after with a revert. Tile kinds: live = installed art, artpipe = candidate render.

## RM_FireWasp - art redo
- Reason: The installed art is overly glossy and weak on scale plating; candidates still need clearer directional views and a distinct flight presentation.
- T011 (live) redo: Glossy smooth segments look stylized and do not convincingly show the described scale plating; use naturalistic overlapping armour.
- T012 (artpipe) redo: Scale plating works, but south and north read as dorsal spread-wing display views; establish clearer front and rear elevations with leg support.
- T013 (artpipe) redo: Useful frontal orientation, but bulbous eyes and polished segmented armour read as a toy insect.
- T014 (live) redo: The shown flying-state image retains the glossy grounded wasp treatment; render a distinct airborne sequence, with body registration still unverified.

## RM_Flamefang - art redo
- Reason: The installed serpent needs a naturalistic replacement; T020 is viable, while T021 has the wrong body plan.
- T019 (live) redo: Regular bright bands and a simplified cobra face look cartoonish; redraw the serpent with naturalistic scales and shading.
- T021 (artpipe) cut: A four-legged lizard contradicts the explicitly described serpent body plan.

## RM_FurnaceBeast - art redo
- Reason: The installed mineral-giant design works but its reported native resolution is inadequate; T024 and T025 are usable replacement sets.
- T022 (live) redo: The design works, but the reported approximately 47 native pixels per cell is insufficient for the 5.5-cell creature's intended zoom resolution.
- T023 (artpipe) redo: Retains the undersampled side design; regenerate genuinely higher-resolution art for the giant draw size.


## Per-row outcome (FOUNDRY, 2026-10-24, delegated: GPT art triage)
Gate = regen_eligibility.Gate over every texPath of the def; pipeline = infrastructure/state/art_eval/runs/*/decisions.jsonl; PROTECTED = art.py status live slots. Queued directly: NONE (no redo slot is NONE/PLACEHOLDER/DONOR; dessicated slots that are DONOR are not what GPT flagged).

| def | gate | protected slots | art-eval runs so far | outcome |
|---|---|---|---|---|
| RM_FireWasp | NONE,REFUSED_REGEN | 6 | {'REGEN@r1': 1} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_pyrelands_c, latest REGEN r1); no second intake. Regens follow the pipeline loop. |
| RM_Flamefang | REFUSED_REGEN | 5 | {'REGEN@r1': 2} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_pyrelands_r1_02, latest REGEN r1); no second intake. Regens follow the pipeline loop. |
| RM_FurnaceBeast | REFUSED_REGEN | 2 | {'REGEN@r1': 1, 'REGEN@r2': 1} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_pyrelands_r1_00, latest REGEN r2); no second intake. Regens follow the pipeline loop. |
