# FlowWorks live day 2 report — 2026-10-17 (FOUNDRY live driver)

## 0. Bridge, game, mod list at start
- 20:14Z `rimflow bridge who`: driver lock FREE, BENCH hold idle 69 min (AFK review walk, 18:25Z) -> taken by FOUNDRY.
- BENCH left the game RUNNING on a 20-mod walk list (11-mod flowworks core + VFE core, alphabiomes, VFE insectoid2,
  rsw.cuisine, weathersuite, luminouspigment, rut.patches, rm.biomes, rsw.swbestiary). Saved as
  `infrastructure/state/modlists/ModsConfig_BENCH_walk20_before_fw11_2026-10-17.xml`; swapped to the 11-mod flowworks list.
- The FOUNDRY clone `/home/mandrake/rm/foundry` holds ANOTHER builder's uncommitted FlowWorks C# (24 files, DLL rebuilt
  13:12 local, pit-trap/cliff-mask/dig-canal work): NOT deployed. Everything below ran from a scratch clone at origin/main
  ab932161c (`/home/mandrake/rm/scratch/FOUNDRY/live2`).

## 1. Deploy P3+P4 DLL, relaunch, migration log
- origin/main FlowWorks DLL = 79ac42417 (P3 7b2fbe7a0 + P4/P8 data side); `dll_source_stamp.py check`: MATCH.
- Game closed 20:19Z; `deploy_custom_mods.py --mod FlowWorks --apply` from the scratch clone: 7 files (DLL, srchash, 4 defs,
  Keys), VERIFIED. Deployed DLL sha256 f4065b26... = repo `# dll:` header; srchash byte-identical. Was 160fcdde... (stale).
- Saves backed up whole: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves_backup_FOUNDRY_20261017T2025Z`.
- Relaunched via Steam: bridge answered in 44 s; Player.log clean (Harmony patched 68, missing 0).
- Pre-rewire fixture: `RM_fw_scene_S6_20261017111339.rws` (fe309aefe DLL, 18:13Z; no RM_levelModel/pondBudget/depthView
  keys) copied to `RM_fw_premigration_S6_20261017.rws` and loaded. Migration log, verbatim:
  - `level model 0 -> 1 (exact decilitres, one surface per body): canals 12 wet square(s), 12 kL before and after; pond #2 35 kL -> 35 kL; pond #4 35 kL -> 35 kL (2 limited pond(s)).`
  - `pond budget model 0 -> 1 (the slider is gone): 0 limited pond(s) re-sized from their floor, each keeping its fill fraction.`
  - `depth view model 0 -> 1: 12 wet dug square(s) re-pictured by their metres of water; no water moved.`
  No exception in the load. Litres unchanged per body (L2 evidence for the save-migration rows of P3/P4).

## 2. S1..S6 walk at shipped settings
f4065b26 DLL, 11-mod list, `water_scenes_walk.py go S<n> --fresh-map` (one fresh quicktest map per scene), pulse 250 ticks,
shipped settings except the scene file's own exceptions. Stdout `Transient/fw_scenes/live/day2/run_S<n>_stdout.txt`; rows
`Transient/fw_scenes/live/S<n>_rows.json`; annotated sheet `Transient/fw_scenes/live/annotated/index.html`; per-square
ProofReadout captures `Transient/fw_scenes/live/day2/S5_readouts.txt`, `S6_readouts.txt`. belt_watchdog HEALTHY at every read.

**Totals: 22 MATCHES, 8 DIFFERS, 1 UNMEASURED (S3.e, not staged), 3 OPEN RULINGS shown (S3.Q1, S4.Q1, S6.Q1).**

| scene | rows |
|---|---|
| S1 | a, b, c, d MATCHES |
| S2 | lvl, a (p11), b (p12), c MATCHES; **d DIFFERS = HARNESS**: the settle detector caught a 4-pulse plateau mid-fill ([3 3 3 3] p7-p10); from p12 to p60 nothing changed. The pond now rises as ONE surface ([1 1 1 1], [2 2 2 2] ...), no half-steps. |
| S3 | a, d MATCHES; **b, c DIFFERS**; e UNMEASURED |
| S4 | a, b, e, c, d MATCHES |
| S5 | b, d, h (=F), f MATCHES; **a, c, e, g, i DIFFERS** |
| S6 | a, b, c MATCHES (run 1 = run 2 at pulse 30; readouts equal square for square) |

**Most DIFFERS are the walk's whole-notch reader, blind to level water.** The walk counts a canal square's whole notches
(`fill`); under P3 a canal holds a sub-notch sheet, which reads 0. ProofReadout per square (the P8 read) shows the P3
oracle's numbers live:
- S5 A: all 10 canal squares `Water 0.24 m (474 L)`, all 9 pond squares `Water 1.74 m (3,474 L)` in a 2 m hole: both
  surfaces 0.26 m below ground; 4,740 + 31,266 = 36,006 L (readout rounding) of 36,000. Oracle: 0.237 m, -0.263 m.
- S5 B: 9 canal squares `0.05 m (91 L)` (oracle 4.5 cm) + pond B `1.55 m (3,091 L)`; the 10th is cell 1, filled in by part C.
- S5 E basin: all 36 squares `0.11 m (222 L)` = 7,992 L (oracle 0.111 m sheet; doc total 8,000).
- S5 F: pond 1.00 m (2,000 L) + 2 m canal square 1.00 m (2,000 L): MATCHES.
- S6: 10 canal squares 0.24 m, 9 pond squares 1.74 m, run 1 and run 2 identical.

**Real findings (MOD), not reader artefacts:**
1. **Pump into a canal stops after one notch.** S3 and S5 G: the pump moves 2 levels (`pump.moved` 2, never more), one
   level reaches the canal and spreads level (6 squares `0.08 m (167 L)` = 1,000 L), the hose holds the other; then the hose
   drains and 9,734 units (973 L) leave the network as a "spill". Likely mechanism (not proven): the Outflow end still
   pours WHOLE notches per square (P4 log: "world-to-world outflow still moves whole notches") and once a sheet is laid no
   canal square has a whole notch of room. S3.b/S5.i expected the canal to fill; it never gets past 1,000 L.
2. **The spill makes no filth.** Player.log: `[FlowWorks] a spill of RM_Liquid_FreshWater at (55, 0, 32) found no cell
   that takes filth; the liquid left the network anyway` (S3 outflow square = canal cell 1, which is water). `jawa/list_things
   RM_Filth_LiquidSpill` over the whole S5 map: 0 things (33,569 scanned). 1,947 L vanished over S3 + S5 G
   (`net.spilledUnits` 19,473) with no puddle and no message: a conservation break, not the ruled filth sink.
3. **Filling in a canal square that holds a sheet destroys it** (S5.e): cell 1 of canal B held 4.5 cm (91 L); filling it in
   logged `conservation exception: 0.1 fill level(s) overflowed with nowhere to go and were destroyed`; the doc says nothing
   is destroyed. Under whole notches cell 1 was dry, so this is new with level water (displacement should move part-notches).
4. **S3.Q1 "game today" is (a), not (b):** the walk printed "nothing reached the canal" (whole-notch reader) but the
   RM_FlowSource canal holds 4 x `0.13 m (250 L)` = 1,000 L after 10 pulses with no hose. The RM_LiquidTap canal stays 0.

## 3. Level-surface north-star bar + measured answers
`RM_NorthstarProofs.ProofLevelSurface("-")` (whole map) parsed by `level_surface_bar.parse_proof`/`worst_gap_m`, read after
each settled scene (S5, S2, S3 restaged fresh with `--no-shots` for the read; S6 after its walk). Raw answers:
`Transient/fw_scenes/live/day2/level_surface_S<n>.txt`. Bar: every body within 1 cm.
- S2: 1 body (dug pond 4 + trench 6 = 10 squares) gap 0.0000 m, surface at ground (0.0000). PASS.
- S3: 2 bodies: canal 6 sq gap 0.0001 m at -0.4167; S3q Source-tap canal 4 sq gap 0.0000 at -0.3750. PASS.
- S5: 7 bodies, worst 0.0001 m: canal A 10 sq -0.2632; basin E 36 sq -0.8889; canal G 6 sq -0.4167; canal B 9 sq
  -0.4546; 3 one-square bodies. PASS.
- S6: 6 bodies, worst 0.0001 m: both 10-square canals -0.2632; gate pieces 3 sq at 0.0000 and 4 sq at -0.2500. PASS.
- Instrument scope: the WaterDeep-terrain ponds (S3 4x3, S5 A, S6 3x3) do not appear as squares in the bar's body list;
  their level comes from ProofReadout below. The bar reads dug squares (S2's dug pond is in it).

**Measured answers**
- **Is the 3x3 pond now level?** YES. S5 A and both S6 runs: all 9 squares `Hole 2 m · Water 1.74 m (3,474 L)` (surface
  -0.26 m, the canal's -0.2632). Yesterday one square turned ChestDeep and eight stayed WaterDeep.
- **Does the S3 spill still produce a filth puddle?** NO, and the water still leaves: the hose drain spills 9,734 units
  (973 L) at the outflow square, which is water, so `found no cell that takes filth; the liquid left the network anyway`;
  0 `RM_Filth_LiquidSpill` on the map. 266 units return to the pond.
- **Does canal cell 1 wet?** YES, everywhere: S3 cell 1 (the Outflow end, 55,32) `0.08 m (167 L)` like the other five;
  S5 G likewise; S5 A cell 1 `0.24 m`. It wets at the same depth as the rest (one surface), but the canal only ever gets
  1,000 L from a pump (finding 1).

## 4. ProofReadout strings per square type
`jawa/static_call RM_NorthstarProofs.ProofReadout("x,z")`, verbatim (the separator is U+00B7 "·"):
- dry dug canal (S3q liquid-tap canal, 42,55): `Hole 0.5 m · Water 0.00 m (0 L)`
- wet canal, sub-notch (S3 canal, 55,32): `Hole 0.5 m · Water 0.08 m (167 L)`; full (S2 trench, 16,55): `Hole 0.5 m · Water 0.50 m (1,000 L)`
- dug pond (S2 2x2, 14,55): `Hole 2 m · Water 2.00 m (4,000 L)`
- natural (WaterDeep-terrain, limited) pond (S3 4x3, 41,31): `Hole 2 m · Water 1.92 m (3,835 L)`; S5 A: `Hole 2 m · Water 1.74 m (3,474 L)`
- edge lake, limitless (S2 west-edge WaterDeep 14x11, 2,55): `Open water, never runs dry (about 2 m deep)`
- undug ground / a cell with no hollow: `-`
- No ledge appeared in any read: every hole read opens onto ground on at least one side, which by `LedgeAt` means no ledge.
- natural river (river_site tile 2610, TemperateForest, moving water): `Open water, never runs dry (about 1 m deep)`;
  a deeper river square (92,5): `Open water, never runs dry (about 2 m deep)`. Captures: `Transient/fw_scenes/live/day2/river_readouts.txt`.
- sea / ocean coast: UNMEASURED (no ocean map staged today).

## 5. objects_sheet.py and river_scenes_walk.py live
First live runs of both (offline-authored). Scripts fixed where the game answered differently, selftest_fw_walks green after
every fix, then rerun:
- objects_sheet: the `_Futuristic/_Industrial/_Modern/_Scrapper` names are ThingStyleDefs, not ThingDefs (build_batch: "no
  ThingDef"): now builds the base def and picks the look through the game's own "Choose style" button
  (`execute_gizmo` -> `get_context_menu_options` -> `execute_context_menu_option`), reading the look back from the menu's
  "(current)" entry. Tank/pipe menus read "<Look>: this tank"/"<Look>: whole connected run"; the reel's reads just "<Look>".
  Weirs on a river bank were refused by grass/reeds (`wipeExisting=false`): the weir now places with wipe.
  **Result: 38 MATCHES, 0 DIFFERS, 0 UNMEASURED** (ladders lowered/raised/autoturn 12; tank, tall tank, reel, pipe x5 looks
  20; weirs 5 with rotation and look read back; fords 1). Default look of every styled def = Scrapper.
  Sheet: `Transient/fw_scenes/live/objects/index.html`; log `Transient/fw_scenes/live/day2/objects_all_stdout.txt`.
- river_scenes_walk (`prep` = river_site.py, then `go R1..R5`): pawn ids did not match (jawa/spawn_pawn answers
  "Human54153", the HoseProbe colonists list 54153), so every position read None and R3 saw nobody: fixed (`_num`). R3 now
  asks `jawa/pawn_get` where each returned pawn is. R1 first read DIFFERS on a SITE artefact (R2's ford stones from an
  earlier run lay on R1's cell); rerun on a fresh river site.
  **Result: 15 MATCHES, 1 DIFFERS, 1 UNMEASURED.** R1 a,b (carried 5 squares),c; R2 a,b (ford 0, control 3),c; R3 a,b;
  R4 a,b,c,d; R5 a,b,c MATCH. R3.d UNMEASURED (letters not read; they do show in the letter stack).
  **R3.c DIFFERS = MOD finding: washed-away colonists come back as STRANGERS.** Staged as `PlayerColony` (game read), swept
  off the edge (pending 0 -> 3), `ProofSwept return` -> `SWEPT pending=0`; each returned pawn stands on a map edge but its
  faction is now TradersGuild, PirateWaster, OutlanderCivil (another run: OutlanderRoughPig). 3 of 3, twice. Likely the
  pawn sits in WorldPawns while away and is handed to an NPC faction; `RM_WorldComponent_SweptAway.TryReturn` spawns it
  without restoring `Faction.OfPlayer`. Panels: `Transient/fw_scenes/live/rivers/index.html`; log
  `Transient/fw_scenes/live/day2/rivers_R3_stdout.txt`.

## 6. Left over / claimable
- MOD: pump into a canal stops after one notch (Outflow end pours whole notches; S3.b, S5.i). File as a P4 follow-up.
- MOD: a spill on a water square makes no filth and the litres leave the ledger silently (1,947 L over S3 + S5 G).
- MOD: filling in a canal square that holds a sheet destroys the sheet (S5.e, 91 L); displacement should move part-notches.
- MOD: swept-away colonists return with an NPC faction (R3.c).
- HARNESS: water_scenes_walk reads whole notches (`fill`); under level water its S3/S5/S6 canal rows need the dL / readout
  read (ProofReadout or WaterDlAt) and the scene doc's whole-notch rows (S5.a "at most 9 wet", S5.c "only cell 1") are
  obsolete under P3. S2.d settle detector stops on a mid-fill plateau.
- The level-surface bar does not list WaterDeep-terrain ponds as bodies; ProofReadout covered them.
- Not run: sea readout; the 4/7/7/4 square; S3.e round trip; mouseover in the UI (ProofReadout is the data the mouseover uses).
- Game left RUNNING on the 11-mod flowworks list (river site map). BENCH's 20-mod walk list is NOT restored; it is saved at
  `infrastructure/state/modlists/ModsConfig_BENCH_walk20_before_fw11_2026-10-17.xml`.
- belt_watchdog: HEALTHY through the water scenes; from 13:39 local it read STALLED on `belt_art_log_20261009h.md`
  (an art belt log, not this run); no live-run signal was ever unhealthy.
- companion_profile.json expiresUtc 2026-10-18T02:00:00Z still ahead; not touched.
- Bridge released 20:52Z.
