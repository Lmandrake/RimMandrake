# FOUNDRY_HANDOFF_202610210531 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610200157`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

**Read `design/Jawa/worldbuilding/planet_state_2026-10-20.md` first.** It is the cold-start table of every planet look/physics mechanism (file, Mod Settings toggle, owner ruling, deploy state, verify item). The dev start is `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3` (owner choice by card; the other eight intermediate dev saves were deleted after a byte-identical backup in `D:\ClaudeWork\backups\saves_pre_cleanup_20261020T2220\`). Nothing was written to `CANONICAL_ASHKARR_START_*`; promotion waits until the owner has seen the sun-lit peaks, swirl layers and Rust Cathedral redraw (card: "Not yet").

**Owner order for the next session (card 10:16 PM):** world-look art FIRST (peaks, Abyss/Rot swirl layer, Rust Cathedral), then the flier rebuild after his eye-line/shoulder-line test, then FlowWorks/GimmeSomeSlack. The game was left relaunching (cold load) after the last deploy: load R3 when it reaches the menu.

## What the owner should see

- He has not yet SEEN in game: the road/river colour redesign (earth-tone roads, blue-grey rivers tinted only in Contagion/Miasma/Wasteland/Rust Cathedral, the highway as old broken asphalt), the sun-flare fix, the 70% labels and recentred Dune Sea, the Ortolan ear repaint, the soft hills/landmarks. Many were verified by state reads, not by his eye.
- Flagged for him: the river redesign REVERSES his 2026-09-06 "red rivers in the mountains" ruling (red now only in Contagion); size genes are real again, so Nelvaanian is 1.20 and seven small species are 0.80 (raid difficulty shifts; his 2026-08-22 instruction); my own numbers: head allowances (Lasat 1.65x wide, Ortolan 0.80 below chin), metabolism +6 on the unused `_smallest` gene; Rings now ship (card) at ~0.5 GB private memory.
- His flier test: eye line and shoulder line level across frames. 12 flier sets are HELD until he sees the line overlays; Uvak wings to be recoloured to canon and checked for donor art.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `SUN_FLARE_VERIFY_NO_GLOW_THROUGH_ROCK` — Planet Atmosphere's flare (ZTest Always) hidden by a CreatureBehaviors patch, deployed, never seen; NEXT: with the game up on R3, shoot the planet centred on tiles 18991, 18987, 8427 and compare with `D:\ClaudeWork\rimmandrake\scratch\live7\before_night_boost.png`.
- `WORLD_PATHS_VERIFY_WATER_FINALLY_WET` — new road/river palette deployed, unseen; NEXT: screenshot the Scald shore (tile 8506), Anvil (19331), a Contagion river (9160) and the highway near tile 2363 (must be old broken asphalt, not gold).
- `FEATURES_IMPORT_FIX_REGIONS_SEEING_DOUBLE` — companion DLL with the by-name fix deployed; NEXT: on a load you will not save run step 12 of `D:\ClaudeWork\rimmandrake\scratch\live6\wtsmoke.py` and confirm 71 regions stay 71, then reload R3.
- `WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS` — owner chose sun-lit peak clusters (card 10:12 PM); NEXT: read `design/Jawa/worldbuilding/worldmap_mods_study_2026-10-20.md`, generate the peak atlases offline with a per-tile angle toward the substellar point, preview Dew Horn before/after, then deploy.
- `WORLD_FACES_REDRAW_ABYSS_ROT_RUST` — owner chose a biome-wide swirl layer (Abyss, Rot) and a harsher NEW Rust Cathedral face; NEXT: build the swirl overlay in RM_WorldLook style with a toggle, regenerate the three faces via biome_worldfaces.py, preview, deploy.
- `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES` — 6 sets rebuilt and installed (Sketto, PekoPeko female, FireHawk, Uvak, Hawkbat, Hawkbat juvenile), 12 HELD on the owner's eye-line/shoulder-line test; NEXT: add the two-line check to `flier_body_stabilize.py`, show him the overlays on the six sets, rebuild the rest only after his word.
- `UVAK_WINGS_RESKIN_TO_CANON` — owner chose recolour to canon and noted donor art; NEXT: read the Uvak canon entry, check every frame for donor art, recolour wings in the plate rebuild.
- `FLIER_FRAMES_FILL_FIVE_GHOST_FLOCKS` — donor frames for Brezak, Drexl, Thranta, Tibidee installed (owner card), not flight-tested; NEXT: queue them for the body-lock rebuild after his line test.
- `PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT` — owner chose to ship the Rings; NEXT: add `rwnodetree.rwplanetatmosphere` after `mandrake.rut.empirepursuit` to the SHIP list, ship the MIDDLE-B atmosphere settings, re-run the list consistency checks.
- `HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS` — skull sizes measured live (Lasat 1.18, Nelvaanian 1.03, Mimbanese 0.98, Ortolan 1.00), hat shot taken; NEXT: ask the owner to look at `D:\ClaudeWork\rimmandrake\scratch\live6\PHONE_lineup_hat.png` and close the item.
- `SELFTEST_SWEEP_FIX_FOUR_REDS_REMAIN` — nightly stays red: drowning-message bug `DROWN_MESSAGE_FIX_MUTE_AFTER_OLDER_SAVE`, review-map coverage for BENCH's ladder defs, 4 UNMEASURED tests need a fresh def dump; NEXT: with the game down run `python3 src/RimMandrake/Utils/refresh.py`, then fix the drowning message when BENCH's FlowWorks DLL is committed.
- `SALVAGER_CONTENT_PROVE_ROGUES_GROUNDED` and `CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT` — salvager quest/site cut and faction ban deployed with UtinniPatches, not proven; NEXT: take a def-dump capture after the load and run `banned_factions.py check-dump` until PASS.
- SHIP, LANDED and FOUNDERS dev saves — still lack the faction cleanup (Combs, Space Exchange, Celestial Rogues, pop-up ignore list); NEXT: regenerate them from the final R3-derived world once the look work is done (owner card: rebuild after the look work).
- `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL` — filed by another seat/agent during the session; NEXT: read it before the next deploy so one trip carries everything.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Worldbuilder replaces the seasonal-amplitude calculation, so a patch to the tidal-lock planet's curve does nothing on the full list. (filed: LESSONS; see: `design/Jawa/worldbuilding/planet_state_2026-10-20.md`)
- Our border-blend overlays at height 0.01 hid every river (vanilla rivers draw at 0.01); overlays now 0.003. (filed: LESSONS)
- The vanilla ocean shader ignores depth; the "grey sea" was the land material, and the honeycomb was the sea-floor layer drawing through. (filed: LESSONS)
- The tidal-lock mod's glow cache keeps returning the old value after a clock rewind, so a "constant glow" check proves nothing. (filed: LESSONS)
- Landmark icons, not hills, were the Rust Cathedral speckle. (filed: LESSONS)
- A generator (`gen_races_mod.py`) silently reverted the five size genes to cosmetic. (filed: LESSONS)
- The audit tool's label frame was mirrored (cost a wrong "fix" of 60 labels); the label centre check now compares by angle. (filed: LESSONS)
- `rimflow close --sha HEAD` stores the word HEAD; use `$(git rev-parse --short HEAD)`. (filed: LESSONS)
- A tool run from WSL with a Windows path literal creates a directory named `D:\ClaudeWork\rimmandrake` in the repo root. (filed: LESSONS)
- The bounding box is the wrong registration for heads (ears became the chin) and fliers (wings move the body): register on the rigid body. (filed: LESSONS; memory `head-art-centre-on-skull-mass-not-appendages`)

## Commits

```
6684950b5 ledger: labels70, Dune Sea centre, Comb camps closed; sun flare verify item; deploy notes
662386035 conversations: catch-up 2 record(s)
86e16be47 conversations: catch-up 2 record(s)
3378ff783 ledger: owner card 10:16 PM, Rings ship
a6a3a2995 lessons: BENCH 2026-10-20 (review loop, enact vs Core slots, OWNER shard, card hook)
e07d4bb93 ledger: drawbridge phases 4-6a notes
58f0307b9 FlowWorks DLL rebuilt from merged source (drawbridge phase 6a + origin's FlowWorks changes)
9630b2f03 Line widths: measured pipe (on spec, 14.5 px) and hose (24-30 px, set in code)
69290c91c Drawbridge phase 6a (content): timber/steel drawbridge build buttons, gate leaf, art-contract paths with stand-ins
439401d21 ledger: file OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL (owner card)
7613d36ca Owner cards 10:12 PM: sun-lit peaks, biome-wide swirl layer, harsher Rust Cathedral
b262d9b9f Scrub farmer camps removed (owner card: Remove the camps); Dune Sea label centred on its interior
a7ce577bb Owner cards 10:09 PM: Uvak canon recolour, Dune Sea label centre items
040ec719d World paths: ancient highway is old broken asphalt, not gold
cfa4ba8f7 Worldmap mods study: WMBP fixed-rotation peaks, sun-facing hill rotation verdict, swirl techniques
45a2a528d Owner feedback items: flier eye/shoulder test, farmer camps, mountains and faces redraw
68ebfa681 item: WORLD_PATHS_VERIFY_WATER_FINALLY_WET cites the published shas
59e61a395 FlowWorks River Colours: blue-grey water, tinted only in Contagion/Miasma/Wasteland/Rust Cathedral
c94bb0c92 World paths: grey-brown stone road (no teal); rivers as water, tinted only in story biomes
b30afc395 Sun flare hidden while the sun is behind the planet (Planet Atmosphere flare is ZTest Always)
... 325 more: git log --oneline 9027de7bf..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.decisions.json   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
 M Transient/modcheck/fixtures.json   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
 M conversations/2026-10-20-0158-9897b713.md   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? "D:\\ClaudeWork\\rimmandrake/"   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T084726.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T084802.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T092155.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_20261017T110253.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p00.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p03.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p10.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S1_p14.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_20261017T084824.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_20261017T092355.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_20261017T110404.txt   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_p00.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_p10.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
?? Transient/fw_scenes/live/S2_p30.png   generated or another seat's (FlowWorks/BENCH scenes, modcheck, modlist-swap backups): not mine, left untouched
... 147 more uncommitted paths (by top-level dir: Transient 143, deployed 3, src 1): git status --short
```

