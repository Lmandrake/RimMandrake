# FOUNDRY_HANDOFF_202610260536 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610252223`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-26): "full belt", ended when he wrote "finish up and handoff". The offline queue is nearly drained: what is left is owner picks, the live game (BENCH holds the bridge), or art needing the artpipe daemon. `rimflow next` keeps offering stale or owner-only items; block them with a reason and move on. (filed: ledger)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- `ASHKARR_LABELS_RENAME_TO_RULED_NAMES`, `MINERAL_ROW_METEORITIC_DECIDE_FLAG` and the mineral_numbers_review sheet approvals need his word.
- Four placed art files are foreign copies of cache images (RM_Muttavaq_south, RSW_Sandstrider_north, rmvenomvine_v1, Runyip swimming east); real renders harvested at `D:\ClaudeWork\rimmandrake\foreign_copy_audit\harvest\harvest_sheet.png`.
- ~480 dead Alpha Animals ops deleted (`ea19b46b37a5`) without a `validate_patch --defs` verdict (it times out over 320 mods).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS` — real renders harvested, nothing installed; NEXT: on a seat with the artpipe daemon requeue or finalize the 4 jobs, run art-eval, then `art install` with --why "delegated: art-eval foreign-copy harvest".
- `TILEFEATURES_SOURCE_VET_STILL_WARM` — a reviewer was running at wrap; NEXT: run `code_review_status.py check` over src/RimMandrake/TileFeatures and mark-clean what a full read passes.
- `VEE_FLORA_VENTS_BUILD_XML_FIRST` — built offline at ee2e8c910532; NEXT: when the bridge is free, run the L1 cold load and L2 quicktests in TileFeatures/validation.py.
- `MINERAL_SURFACE_PROVE_LIVE_MAP` — R3 built offline (b5b48cf8e6); NEXT: live-prove the surface check when the bridge is free.
- `ALPHA_ANIMALS_DEAD_OPS_DELETE_REMAINING_REFS` — done but unmeasured; NEXT: run validate_patch.py --defs as a background job longer than 540 s and read the verdict.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `validate_patch.py --defs` over all mods exceeds a 540 s foreground limit and exits 124 with no output; run it as a long background job (filed: this handoff).
- A helper that stops "waiting on background work" re-notifies several times with the same report; treat repeats as noise (filed: this handoff).

## Commits

```
ee2e8c9105 TileFeatures: new mod mandrake.rm.tilefeatures, 21 VEE flora/weather/vent tile features ported to RM_ defs + first validation.py
a41f653988 ledger: foreign-copy harvest note on ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS
2bf6edc806 ledger: owner card files RIMPULSE_PLAN_BUILD_ON_TRACK_WHILE_AWAY
c8fe04a1bd Owner cards: spare capacity order with a conditional pass; weekly account budget; hands-on jobs folded; paper 'new' = since he last opened it
7e82c4af2f ledger: BENCH closes STEVEDESKTOP_DOORS_VERIFY_BEFORE_LEAVING; notes on submit-time chain validation and item-less filler jobs
ea19b46b37 Delete dead Alpha Animals (sarg.alphaanimals) ops from rename, ArtFold, eviction and dupes patches
c643ce478f testq fill: Steve never idles with no LLM in the loop - every tick, if nothing runnable is pending/running, queue the 4 stalest FlowWorks chains (BENCH.filler, prio 20); brakes: QHOME/fill.stop, 8 per local day, paused lane, two non-DONE fillers in a row
8fec91141e review: RM_PollinationGateExtension.cs + BiomeDescriptions_Ashkarr.xml clean; filed ANIMALDUPES_ORPHAN_OPS_AUDIT_SOLE_SPAWN_CUT, ASHKARR_LABELS_RENAME_TO_RULED_NAMES
3cbf0876dd BiomeDescriptions_Ashkarr.xml review: stale BiomeGRimond and Scarlands-tile comments corrected, AridShrubland port made verbatim to RUT_AridShrubland
cc7f47aca8 ledger: file RIMPULSE_PAGE_FIX_CHORES_POSE_AS_RULINGS
074a9264fa design: RimPulse make-it-great pass for two machines, three accounts (GPT critique folded, six owner cards)
d326a66d59 ledger: phone brief built + L1 verified (owner phone check owed), account page item closed, widget-packet and plan-usage items filed; lesson on headless screenshots of SSE pages
844c00e0b9 Delete 43 dead Alpha Animals ops from AnimalBiomeDuplicates_Generated.xml (ALPHA_ANIMALS_DEAD_OPS_DELETE_FROM_DUPES)
59639732a0 code review: pulse brief/pulse/pulse_core/selftest_brief clean at 1eed616cb9
00e59c9615 RimPulse brief judge: derive a look's packet path from the monitor row itself, not the composer's claim
ab6695980c RimPulse brief: every look ships as a review packet - recommendation, alternatives, evidence, doubts - or reads "packet incomplete" (owner card 2026-10-25)
b8d9ab4235 ledger: ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR built (step 5 refs), 3 findings filed, 4 clean marks; lesson donor-prefix-not-exclusive
3bb15d8b42 ledger: owner card on RimPulse review packets (evidence and doubts)
69d7b1967e RimPulse brief: a live card with no item id reads as its own text, not ": BENCH asks ..." (seen on the first live render)
92792d8b14 Rebuild RimMandrake.EnvironmentalHazards.dll from committed source at landing
... 206 more: git log --oneline 9a3579c059..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M infrastructure/state/ledger/events/FOUNDRY.jsonl   (helpers' ledger events; carried by the next publish)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_p00.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_p03.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_p10.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S1_p14.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_p00.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_p10.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_p30.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S2_p60.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S3A_p20.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S3B_p06.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S3B_p16.png   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
?? Transient/fw_scenes/live/S3_20261017T084854.txt   (BENCH/FOUNDRY FlowWorks scene captures, untracked Transient, not mine)
... 119 more uncommitted paths (by top-level dir: Transient 114, conversations 3, design 1, infrastructure 1): git status --short
```

