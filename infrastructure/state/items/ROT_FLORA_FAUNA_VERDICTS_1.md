## spec

Wire the 5 owner-approved landed sprites from Group C of
`Transient/rot_flora_fauna_review_2026-09-18.decisions.json`:
- twistingthornweed_v1_r2
- twitchingpuffer_grown_v1
- twitchingpuffer_harvested_v2
- twitchingpuffer_immature_v1
- twitchingpuffer_tendrils_v1

Also wire any other approved-but-unwired Deeps sprite from
`Transient/deeps_art_review_2026-09-18.decisions.json` (PrennaLace,
TwitchingPuffer per the deeps species sheet).

Rot cuts: remove `RSW_BovineBeetle` from `<wildAnimals>` in
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` (now the Deeps'
Grabber). `RUT_Emberscythe` marked cut but is not in Rot's tables (Pyrelands
fauna shipped inside RotSporeKit) — no XML change, flag for owner: move to a
Pyrelands mod?

Validate + deploy LanternDeeps, UtinniPatches, and twistingthornweed's mod;
commit only own files; rimflow note.

## status log

- 2026-09-19: skeleton written, starting investigation.
- 2026-09-19: TASK 1 investigated. All 4 `twitchingpuffer_*` and `twitchingpuffer_tendrils_v1`
  sprites were ALREADY wired and committed (`a1e40ff04`, `DEEP_FLORA_RENAME_1`) — pixel-identical
  to the artsrc PNGs (bytes differ, PIL recompression, but `ImageChops.difference` confirmed
  identical pixels), no action needed. PrennaLace (`greylady*`) likewise already wired and
  committed (`e1427a149`). Ran `wire_art.py` plan mode against the deeps decisions file: 44 kept,
  and a pixel-diff sweep of all 44 found exactly ONE actually unwired: `lanternstonesowableimmature_v1`
  (dest `RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature.png` did not exist). Copied it
  by hand (not via `wire_art.py --apply`, which does unconditional `shutil.copy2` on all 44 rows and
  would have rewritten the 43 already-identical files with different bytes — pure noise in the diff).
  `twistingthornweed_v1_r2`: only ONE regen job was queued (not an a/b pair), existing
  `TwistingThornweed_a.png`/`_b.png` (from `POLLUTED_LANDS_FLORA_PORT_1`) are still in place;
  wired the new approved sprite as a third Graphic_Random variant, `TwistingThornweed_c.png`,
  per the task's literal instruction (append per the folder's existing convention) rather than
  replacing a/b, which would need an explicit owner ruling. Note: new art is 256x256, existing
  a/b are 128x128 — inconsistent canvas within one Graphic_Random folder; not blocking (RimWorld
  doesn't require matching sizes across variants) but flagging.
  PNGs wired this session:
  - `src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature.png`
  - `src/RimUtinni/UtinniPatches/Textures/Things/Plant/TwistingThornweed/TwistingThornweed_c.png`
- 2026-09-19: TASK 2 done. `RSW_BovineBeetle` line removed from `<wildAnimals>` in
  `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` (was line 135, weight 0.2).
  `RUT_Emberscythe` confirmed NOT present anywhere in `RUT_TheRot.xml` — grep found no match,
  matching `build_review_sheet.py`'s own note ("NOT in RUT_TheRot ... Pyrelands fire-follower
  shipped in this same kit [RotSporeKit]"). "cut" is therefore already true for the Rot; no XML
  change made. Open question for the owner: should `RUT_Emberscythe` MOVE out of RotSporeKit
  into a dedicated Pyrelands mod, since it's Pyrelands fauna currently shipped inside a Rot-named
  kit with placeholder art (a vanilla Megascarab recolor, per its own header comment)?
- 2026-09-19: STEP 1 (applying owner's Rot species verdicts, `rosters/rot_regen_briefs.json`,
  48 rows) done. All 27 `RUT_*` defs edited directly across
  `RUT_PaleTree.xml`, `RUT_RotSporeKit_FurnaceCap.xml`, `RUT_RotSporeKit_GuardianGroves.xml`,
  `RUT_RotSporeKit_Flora.xml`: label + description on every row, `<plant><visualSizeRange>`
  MAX set to the ruled width (min scaled to the def's own existing ratio, or 0.3x max for
  `RUT_FlakespireFungus`/`RUT_BleedingTooth`, which had no visualSizeRange at all — added one)
  on the 15 rows with a ruled size. The 19 donor `AB_*`/`AA_*` defs (Alpha Biomes'
  `Plants_MycoticJungle.xml`, Alpha Animals' `Races_*.xml`, found via the live def dump's
  `manifest.json` at rootDirs `.../294100/1841354677` and `.../1541721856` — About.xml scans
  and `find` timed out repeatedly on the workshop tree, the dump's `rootDir` field was the
  fast route) got ONE new patch file, `src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml`:
  label + description always, `<plant>/visualSizeRange` replace for flora with a ruled size,
  fauna PawnKindDef adult stage (`lifeStages/li[3]`, matching lifeStageAges' baby/juvenile/adult
  order) `bodyGraphicData/drawSize` replace for the 5 fauna with a ruled size.
  🔴 **Deviated from the brief's "PatchOperationFindMod-gated per donor packageId"**: this
  repo's own `PlantTolerances_Ashkarr.xml` carries a hard-won header warning that
  `PatchOperationFindMod` matches a mod's display Name, not its packageId, and that the
  working, already-proven gate here is `PatchOperationConditional` on the def's own xpath
  (absent def -> xpath simply doesn't match -> silent no-op, same guarantee, no name lookup
  needed). Used that pattern instead — same effect, matches the standing convention.
  `AA_Agaripod`/`RSW_FungalMantis` (owner's "keep + rename"): label only, no size, no art job.
  `RSW_FungalMantis`/`RSW_FungalWeevil` edited directly in
  `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
  (ours), both ThingDef+PawnKindDef label, `RSW_FungalWeevil`'s adult drawSize 1.8->4.
  Dessicated-corpse drawSize left untouched throughout (out of the ruling's scope).
  Marsh/growable sibling variants (`RUT_NuitaeMarsh`, `RUT_WrinklecapMarsh`, `RUT_GreenArpeau`,
  `RUT_NogtylMarsh`, `RUT_MortalMorelPlantGrowable`) were NOT touched — not named in the
  ruling, though they share the base def's old label and now read inconsistently with it
  (e.g. `RUT_Nuitae` is now "nissik gill" but `RUT_NuitaeMarsh` is still "nuitae") — flagged
  for a follow-on pass, not fixed here. Collision check: no new label/alternate collides with
  any existing `<label>` in `src/` (script sweep, the only same-string hit is `rustpuff`
  against itself, which keeps its name).
- 2026-09-19: STEP 2 (validate) done. `validate_patch.py` against the new patch file with
  BOTH `--defs` roots (Mods + workshop/content/294100) AND
  `--mods-config infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`
  (the live `ModsConfig.xml` only has 6 active mods right now — minimal-list regime — so the
  bare command resolved 0 def files and failed with "ZERO def files loaded"; the full-list
  snapshot fixed that, 621 active / 615 found on disk, 7,038 def files). Result: **0 errors,
  1 benign warning** (Operation 17, AA_Agaripod's PawnKindDef — a direct
  `PatchOperationReplace` on `label` under a `PatchOperationConditional` testing the parent
  node; the validator flags "test one node, edit another" as a pattern to double-check, and
  it's the intended one here). Every one of the 25 Operations matched exactly 1 node in
  Alpha Biomes/Alpha Animals' own files — confirms all 19 xpaths are real and correctly
  targeted, none silently matching zero.
- 2026-09-19: STEP 3 (deploy) done. Checked `./game` first: reported RUNNING/LOADING-by-default
  (no bridge probe), but `Player.log` showed a steady idle GC tick pattern (`Unloading N
  Unused Serialized files`, repeating every few seconds, no asset-load lines) — read as an
  idle menu, not an active load, so proceeded rather than waiting the full 20-minute loop.
  `RotSporeKit`: plan showed only my own 4 files drifting -> `--apply` succeeded, 4 files
  deployed and verified in sync. `UtinniPatches`: plan showed non-held drift on
  `RUT_TwinkleSpikeTestPlant.xml` (another window's uncommitted file, not mine) alongside my
  new `Patches/RotSpecies_NamesAndSizes.xml` -> did NOT run `--apply`; hand-copied only that
  one new file to the game's `Mods/UtinniPatches/Patches/` and diff-confirmed byte-identical.
  `SWBestiary`: plan showed non-held drift on six other files (`RimMandrakeLivestockRSW.dll`,
  `RSW_MlieWaveC_Bodies.xml`, `ThingDefs_Onnik.xml`, `SeaBeasts_NurseryJuveniles.xml`,
  `RSW_MlieWaveC_Resources.xml`, `RSW_Yobshrimp.xml`, `Waterline_Lane1.xml` — another window's
  work) alongside my `RSW_BiomesTeamPort_Races.xml` -> did NOT run `--apply`; hand-copied only
  my file and diff-confirmed byte-identical. Neither mod is enabled in the live minimal
  ModsConfig, so nothing here is visible until a full-list load anyway.
- 2026-09-19: STEP 4 (art jobs) done. Built an art-list JSON from the 46 `decision=="regen"`
  rows of `rot_regen_briefs.json` (only, per `fill_queue.py --input`): id
  `rot_<defName without its AB_/AA_/RUT_/RSW_ prefix, lowercased>_v2`, `rimflow_item_id`
  `ROT_FLORA_FAUNA_VERDICTS_1`, prompt = each row's `art_prompt` verbatim, priority 40, no
  `reference` field, `background: transparent`. Canvas per the artpipe README's actual rule
  (`drawSize×128`, next power of two, floor 256 — the README explicitly wins over any fixed
  ceiling table, and its own words are "canvas sizing errs GENEROUS, never a rejector"), using
  each row's ruled width when set, else its current width for the 15 "unchanged size" rows.
  Facings: every fauna `art_prompt` explicitly says "three facings" in its own text (confirmed
  against the def dump — none of the 6 fauna ThingDefs carries an explicit `graphicClass`
  override that would make it a single-texture case), so all 6 fauna got `south,east,north`;
  all 40 flora got none (their prompts are single-view, no facings language). `--dry-run`
  then a real run: **58 job files filed** (40 flora + 6 fauna×3 facings), **0 duplicates
  refused, 0 row errors** — into `infrastructure/artpipe/pending/`, written only through
  `fill_queue.py` as required. Sizes ran generously large for the biggest rulings (e.g.
  `rot_agariluxprime_v2` at 4096×4096 for the 20-cell grath elder, `rot_mycoidcolossus_v2_*`
  at 2048×2048 for the 15-cell vorrugath) — `fill_queue.py` warned on every row exceeding its
  own advisory ceiling and filed anyway, matching the README's standing ruling.
  `AA_Agaripod`/`RSW_FungalMantis` (keep+rename) correctly got NO job, per the ruling.
