# FOUNDRY_HANDOFF_202610151923 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610120035`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->


## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
The Star Wars donor is OFFLINE-complete: port check 0 donor-only refs, 0 donor-served textures (Acid is Biotech's), 40 regenerated species + Nysillin installed and deployed, and a 22-mod donor-off load came up clean (Transient/Player_donor_off_w4.log). Only species-spawn and map-gen checks remain before retiring it.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- Aiwha adult is installed at drawSize (10,5) but its FACE is still weak. Rancor/ChrysalideRancor/Rycrit/Squall were flipped from CutoutComplex to plain Cutout white (never seen in game). Akk S, Nexu N, Veermok S facings still failing canon: those 3 species (and FrogDog, Grazer male, Torton female) keep donor art until they pass. Nysillin immature is my 55% scale-down of the accepted adult, not a separate pick.; NEXT: - `DONOR_OFF_LOAD_PROVE_AFTER_BENCH` — loads clean, spawn/mapgen/flight not run (companion build mismatch blocked preflight L05); NEXT: when bridge is free and companion matches, spawn the ported species and generate AridShrubland, TheRot, Webwork on tier donor_off_w4, then retire mlie.starwarsanimalcollection
- `donorart_akk_v3_south, donorart_nexuw_v3_north, donorart_veermok_v2_south` — refiled in artpipe pending; NEXT: when they pass canon, art.py install the three slots (with --owner-said citing his Accept) and deploy SWBestiary
- `AIWHA_HEAD_CLOSEUP_REDRAW_STILL_UGLY` — filed; NEXT: close-up head pass composited onto the wing-first body via aiwha_composite.py
- `ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE` — filed; NEXT: add def footprint in cells plus a cell ruler to art_sheet.py output and to fill_queue briefs
- `FrogDog / Grazer male / Torton female / juveniles, females, swimming of the 40` — rendered, canon passed except noted, owner has not seen them; NEXT: send them to him as chat images, then install on his word
- `SWBestiary donor-only manhunterOn* patches` — log "failed" harmlessly; NEXT: delete or guard those PatchOperationConditionals once the donor is retired
- `WAVE1_RELIC_HEALTH_MOSS_OPEN` — relic repair untested live, health metrics written not deployed, moss verify needs a game look; NEXT: at the next bridge window run the wave-1 W5 relic acceptance, then deploy the companion and prove the eight health metrics
- ModsConfig — restored to pre-swap copy md5 ee01dae9 (not BENCH's earlier d065795f); NEXT: BENCH confirms its list before launching

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- art.py install keys ledger events by the mod string you pass: use src/RimStarWars/SWBestiary, not SWBestiary, or the push guard rejects (filed: LESSONS).
- Graphic_Random texPath and immatureGraphicPath are FOLDERS; a single file logs "No textures found" (filed: LESSONS).
- fill_queue rows need canvas_w/canvas_h (filed: LESSONS).
- Square drawSize on a 2:1 canvas squashes the sprite; use Vector2 (filed: LESSONS).

## Commits

```
7edc179de Ledger: Nysillin_Immature folder move recorded
3ae14f5d6 W4 donor-off live load: loads clean; Nysillin immature as a folder; donor_off_w4 tier
b0ec1721f FlowWorks fuel moat step 1: chemfuel and astrofuel name their canal fluids, so a tank pumps or hoses them into a dug channel (C9-F1)
4f470f7c5 GSS: GssSessionReset no longer written into saves (dropped from Game.components while saving); O7 now fails any unsaved-guardless Game/Map/WorldComponent
413adc9f4 L1 fixes progress skeleton
78f55b91b Install 40 accepted donor-art regens (120 facings); tint-mask species flipped to plain Cutout, white colour; no donor-served sw* texPaths remain
6915c296d Review records: JawaBenchTerrainTools.cs CLEAN; review_final_2.md table complete (harness, bridge, skipped, still DIRTY)
b7aef06ca Review records: GSS/FlowWorks python harness and bridge companion files CLEAN (BENCH reviewer pass 2)
131573075 jawa/pawn_severity_adjust: a negative offset that takes a hediff to 0 removes it, and the tool reported that working push as a failure; now success with removed=true (compiled, not deployed)
e1e2c21de JawaBench comments: map_info's inline note said Map.Biome can diverge from the tile after world_tile_set (its own Description, verified, says it cannot); AwarenessCore named a JawaBenchAwarenessHooks.cs that does not exist
f47381e9e FlowWorks v2: W2R/W2 comments and one row message still described the pre-unify ponds (2-cell W2R cap 10, W2 cap 5); now 4-cell cap 8 and W2's capacity (text only, offline tier + mock 61/61 green)
7674f8ab3 FlowWorks review map: pit ramp art (04657a349b) had no coverage rule, so review_map.py --plan failed 4 uncovered; rule added, key sheet regenerated (it predated today's station text)
bcda687a2 Review records: Pyrelands + settings-screens selftest CLEAN (BENCH reviewer pass 2)
0f6ecb6f6 selftest_settings_screens: MODS held 28 duplicate keys (merge artifacts; only the last of each counted, ScarlandsLadder's two disagreed); deduplicated, effective table unchanged, 822/822
201544a4f Review records: FlowWorks C#, liquid terrain defs, generator CLEAN (BENCH reviewer pass 2); table so far
94c8f530e FlowWorks review: superdeep pit text names the ramp as a way out; SelfTest csproj no longer points at the read-only mirror; generator brine note (generated output byte-identical)
c0b0cba10 FlowWorks review: RM_PitRamp no longer claims placeholder art (real art 04657a349b); Excavation header names the relative-rule trap tick; csproj build line points at winbuild, not the read-only mirror; DLL rebuilt
020311ef3 ledger: L1 verifies + closes (test-site saves, BUMBLEDRONE, FERRY_ROPE, fire queue, dig reset, static_call warmth, heat dome, burrow x2)
e3f885330 Review records: 25 GSS/_Shared files CLEAN after full-file review (BENCH reviewer pass 2)
98c33bb9c L1 sitting: test-site saves built and loaded by every suite; sections 5-8, teardown (owner list ee01dae9 restored), 5 items filed
... 643 more: git log --oneline 2cba93633..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/scale_ground_measured.json   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/01fbc3e8db36f63ab5e8.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/0246ec2415ecfd9034c5.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/0365aef56ed78f6d87d8.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/037c682927ae2ff0ddef.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/03e20205e836860cb067.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/03e388a41435a8895e9b.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/046b4216ce4eef45833d.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/05c5e9c0a46d55d12961.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/06aa0e0bb52a2036646c.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/07b66a2274fb4d0778ae.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/07be76681b529c2f20aa.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/09badcca167e3e12ba77.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
?? Transient/biome_ffar/img/09d522f97b5c2058acd4.webp   FOUNDRY (review-sheet thumbnail cache / measured json, regenerable; deliberately uncommitted)
... 563 more uncommitted paths (by top-level dir: Transient 562, deployed 1): git status --short
```

