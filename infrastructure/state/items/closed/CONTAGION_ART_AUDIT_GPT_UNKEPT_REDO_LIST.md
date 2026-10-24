# CONTAGION_ART_AUDIT_GPT_UNKEPT_REDO_LIST

Sources: Transient/gpt_biome_art_review_2026-10-24.md (digest) and D:\ClaudeWork\rimmandrake\gpt_biome_review\Contagion.md (full review; raw answers in raw/). Everything below is GPT (gpt-6.1-sol) opinion; nothing was acted on.

Rows where GPT says redo/cut and the owner has NO keep on record. Filed as a FINDING, not queued: the art rule (memory 'Queue art only for NONE/PLACEHOLDER/DONOR') needs the destination state confirmed from the art ledger first, and that was not done here. Next step: confirm each row's state in the art ledger; NONE/PLACEHOLDER/DONOR may be queued, a live art-eval-pipeline redraw is shown to the owner after with a revert. Tile kinds: live = installed art, artpipe = candidate render.

## RM_Bloodlurk - art redo
- Reason: All three sets communicate a jointed ambusher but lack a clearly readable siphon, a defining feature of the subject.
- T005 (live) redo: Strong jointed forelimbs, but no legible siphon; add a distinct tubular feeding structure consistent across facings.
- T006 (artpipe) redo: Hooked forelimbs read, but the siphon is unreadable and the dark torso loses separation at normal zoom; clarify the siphon and lift body values.
- T007 (artpipe) redo: Towering scythe-like forelimbs dominate while the defining siphon remains unreadable; integrate a substantial siphon into the central body.

## RM_BloodyMess - art redo
- Reason: Both sets remain dominated by exposed entrails and fail to clearly provide the cohesive translucent red jelly body requested by the owner.
- T008 (live) redo: Reads as exposed viscera rather than a cohesive jelly organism; suspend half-organs in continuous translucent red jelly as the owner requested.
- T009 (artpipe) redo: Low creeping silhouette fits, but exposed coils still resemble discarded entrails; add substantial transparent jelly connecting and engulfing them.

## RM_Meltgut - art redo
- Reason: No version clearly delivers three organic meals at successive digestion stages: T039 and T040 contain houses, while T038 and T041 have indistinct organic contents. Correct the facing problems and enlarge the configured scale to support house-sized.
- T038 (live) redo: Retain the diseased slug anatomy, but show three distinct organic meals at successive digestion stages and make north unmistakably rear-facing.
- T039 (artpipe) redo: Recognizable houses occupy the translucent belly; replace them with three organic victims at progressively dissolved stages.
- T040 (artpipe) redo: Replace the houses inside the belly with organic victims and rebuild the overhead north image as a true rear view.
- T041 (artpipe) redo: The ridged rear is improved, but the mottled organic contents do not clearly distinguish three meals at three digestion stages.

## RM_Sloshbelly - art redo
- Reason: The live muzzle and paw-like limbs suggest a swollen quadruped; T056 supplies the required translucent tick anatomy.
- T055 (live) redo: The pointed muzzle and separated, paw-like limbs read as a swollen quadruped; replace them with tick mouthparts and clustered arthropod legs.


## Per-row outcome (FOUNDRY, 2026-10-24, delegated: GPT art triage)
Gate = regen_eligibility.Gate over every texPath of the def; pipeline = infrastructure/state/art_eval/runs/*/decisions.jsonl; PROTECTED = art.py status live slots. Queued directly: NONE (no redo slot is NONE/PLACEHOLDER/DONOR; dessicated slots that are DONOR are not what GPT flagged).

| def | gate | protected slots | art-eval runs so far | outcome |
|---|---|---|---|---|
| RM_Bloodlurk | DONOR,REFUSED_REGEN | 0 | {'REGEN@r1': 1, 'REGEN@r2': 1, 'REGEN@r3': 1} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_contagion_r2_00, latest REGEN r3); no second intake. Regens follow the pipeline loop. |
| RM_BloodyMess | DONOR,REFUSED_REGEN | 0 | {'REGEN@r1': 1, 'ACCEPT@r1': 1} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_contagion_r1_00, latest ACCEPT r1); no second intake. Regens follow the pipeline loop. |
| RM_Meltgut | REFUSED_REGEN | 2 | {'REGEN@r1': 1, 'REGEN@r2': 1} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_contagion_r1_02, latest REGEN r2); no second intake. Regens follow the pipeline loop. |
| RM_Sloshbelly | DONOR,REFUSED_REGEN | 0 | {'REGEN@r1': 1, 'ACCEPT@r1': 1} | ALREADY A CANDIDATE: judged by the art-eval pipeline (fauna_contagion_r1_03, latest ACCEPT r1); no second intake. Regens follow the pipeline loop. |
