# SHIPPED-rung gap audit, 2026-10-01

Read-only audit of the SHIPPED rung (`NORTHSTAR_PHASE_LADDER_1` rung 6: deployed == repo, Mod Settings complete, art complete, code review CLEAN) for FlowWorks, Graffiti and Pyrelands. Items: `FLOWWORKS_NORTHSTAR_SHIP_1`, `GRAFFITI_NORTHSTAR_SHIP_1`, `PYRELANDS_SHIP_READINESS_1`. Plans: `D:\Luke\dev\RimMandrake\design\RimMandrake\northstar_trials\<Mod>_trial_plan.md` §5.

Instruments and what they cover:
- Deploy: `deploy_custom_mods.py --mod <X>` dry run (never `--apply`), comparing this worktree's `src/` (HEAD) to the Steam `Mods` folder. Pyrelands is composed, so `--compose biomes` was used, plus `--mod UtinniPatches` for its RUT_ cast.
- Code review: `code_review_status.py check` over every tracked `.cs` and `.py` in the mod folder (sanity: output shows both CLEAN and DIRTY, so the instrument discriminates). FlowWorks 71 files, Graffiti 21, Pyrelands 25, BiomesShell 1, PyrelandsMechanics 8.
- Art: a python def scan (all `texPath`, `texturePath`, `uiIconPath`, flying-frame prefixes in `Defs/**.xml`) resolved against an index of all 7,311 repo texture stems (probe: Graffiti resolves 42 of 44 texPaths, so the index can see present textures). The `measure` CLI is not on PATH in this worktree; a def-XML parse stands in for it. Paths that resolve to nothing in the repo are mostly vanilla (`Terrain/Surfaces/*`, `Things/Mote/Smoke`, `Designations/Mine`), which load from the game's own assets and are NOT missing. Those are classed below as vanilla reuse, not BadTex.
- Settings: read the `ModSettings` classes and `DoWindowContents` directly.
- `dll_source_stamp.py check` (whole repo, exit 0): FlowWorks, Graffiti, Pyrelands (`FireEcologyHook.dll`), BiomesShell, PyrelandsMechanics all MATCH.

Size scale: S = under 30 min, M = 1-3 h, L = a half day or more, XL = multi-session.
Offline-doable = needs no game or bridge, only repo edits and the artpipe daemon or a rebuild.

---

## FlowWorks

### (a) Deployed vs repo: in sync
`deploy_custom_mods.py --mod FlowWorks`: "in sync (68 files)". `.srchash` MATCH. No gap.
Related deploy hygiene (not FlowWorks-specific): `PITS_STALE_DEPLOY_COLLISION_1` (retire stale `Mods/Pits/`) is still an open item.

### Gap table

| # | Area | Gap | Size | Offline-doable |
|---|---|---|---|---|
| F1 | Code review | 4 DIRTY of 71 (was 12 on 2026-09-30). `Source/LiquidTypes/RM_LiquidBodyDef.cs` (89 lines, changed since mark `9b64f4fde`), `Source/ManyWaters/RM_NoRecreationalSwimExtension.cs` (17, never marked), `Source/ManyWaters/RM_Patch_NoRecreationalSandSwim.cs` (86, never marked), `Tools/generate_liquid_suite.py` (1373 lines, changed since mark `7cac17f5e`). The `validation.py` rewrite (plan §5.3) will add a fifth. | S + S + S + L (generator is large). About 3 h for the C#, a half day for the generator. | Yes |
| F2 | Mod Settings | Three separate settings pages ship in one mod: "FlowWorks" (31 fields: 22 checkboxes, 9 sliders, sectioned, all checkboxes have tooltips, `typedLiquidShoresEnabled` is labelled "affects newly generated maps"), "FlowWorks: Pits" (`PitsSettings`, 10 fields) and "FlowWorks: Water effects" (`RiverSteamSettings`, 2 fields). Gaps: no reset-to-defaults button on any page; the Pits page has no settings for the unbuilt mechanics (spikes, superdeep cover) which is fine until they exist; no all-off component exists (`validation.py` has no all-off case, grep found none). Whether all-off still "digs dry channels" is UNMEASURED. | M (reset button x3 plus an all-off component in the rewritten `validation.py`) | Settings code yes; all-off proof needs a live northstar run |
| F3 | Art: placeholder on forbidden texPath | 4 defs still on `Things/Building/Security/TrapSpikeArmed`: `RM_Ladder` (`Defs/Canals/ThingDefs/FlowWorks_ThingDefs.xml`), `RM_PitCellBase`, `RM_PitDigSiteBase`, `RM_OpenPitBase` (`Defs/Pits/ThingDefs/`). The item says "no def on TrapSpikeArmed", the plan says 3; measured 4 (3 are bases and may be abstract, not checked). | M (4 sprites via artpipe) | Yes (daemon generation; `Transient/flowworks_art_2026-09-16/` already holds a building/terrain/designator batch with `gap_jobs_UNRULED`, so check its rulings before queuing) |
| F4 | Art: vanilla placeholder reuse | `RM_LiquidDrill` and `RM_LiquidTap` use vanilla `Things/Building/Production/DeepDrill`. Own textures in the whole mod: 7 PNGs (barrel, bottle, bucket, tank, 3 tar filth). | S-M (2 sprites) | Yes |
| F5 | Art: terrain depth ladder and fill tiers | 78 terrain defs point at vanilla water ramp textures, `Terrain/Surfaces/Gravel` (4 channel depths `RM_Channel_Empty/Mid/Deep/Superdeep` all on the same Gravel) or `WaterDeepRamp`/`WaterChestDeepRamp`. They load fine (no BadTex) but the plan §5.6 needs "5 legible depths", fill tiers x fluids, burned channel state, reduced reservoir read, pit walls. Difference between depths is tint only. The art for visual bars is not built. | L (terrain set; the generator `generate_liquid_suite.py` exists) | Yes (generation); legibility judging needs the northstar judge or the owner |
| F6 | Art: donor dependency | `RM_WaterBottle_*` (5 defs) use `DBH/Things/Resource/WaterBottles`, a Dubs Bad Hygiene Lite texture. The def comment says it is gated on Lite's packageId. Not a gap if the gate holds. UNMEASURED whether DBH Lite ships in the shipped list. | S to confirm | Yes |
| F7 | Unbuilt mechanics behind bars (plan §5.5) | Depth-engine viscosity; per-body fluid; pawn depth draw offset plus 20 percent walls; superdeep cover; per-cell spikes; sluice/grate doors (`FLOWWORKS_DOOR_FAMILY_1` still open); pit collapse onto the primitive (`PIT_SUPERDEEP_COLLAPSE_1` still open). The SHIPPED acceptance allows closing them or parking their bars by his word. | XL (7 mechanics) | C# yes; verification needs live runs |
| F8 | validation.py | Plan §5.3: still the old Pits suite, to be rewritten against the primitive; judge is single-frame (§5.4, diptych convention). `validation.py` itself currently reads CLEAN, and will go DIRTY on rewrite. | M-L | Yes |
| F9 | Walk text | Walk steps 4-6 call `jawa/canal_dig` (always fails); rewrite against `flowworks_excavation_drive/report`. Outside the hashed section. | S | Yes |

Counts: 9 gap rows. Of the SHIPPED acceptance bullets: code review (F1), settings (F2), art (F3-F5), deploy (none, in sync), doors/pits items (F7).

---

## Graffiti

### (a) Deployed vs repo: in sync
`deploy_custom_mods.py --mod Graffiti`: "in sync (74 files)". `.srchash` MATCH. No gap.

### Gap table

| # | Area | Gap | Size | Offline-doable |
|---|---|---|---|---|
| G1 | Code review | 3 DIRTY of 21: `northstar_plan.py` (16 lines, never marked), `northstar_site.py` (32 lines, never marked), `validation.py` (400 lines, changed since mark `616570761`). All 18 `.cs` files are CLEAN. | S + S + M | Yes |
| G2 | Art: one missing texture | `RM_Graffiti_Glyph_Bloodfeeding` (`Defs/ThingDefs_GraffitiMemeGlyphs.xml`) has no texture in the repo. Its artpipe job `glyph_bloodfeeding` is in `infrastructure/artpipe/failed/` (worker exited -2, codex Traceback, `image_present=False`, 2026-09-26), so the art does not already exist. Plan said 38 defs lacked art; 37 of them are now resolved (61 PNGs in the mod, 25 other glyphs resolve). | S (requeue one job) | Yes (daemon) |
| G3 | Art: bars still RED | Plan §5.1 says bars `never_real_world_english`, `mark_reads_at_play_zoom` need `graffiti_vandal_regen_v1_*` wired. The 6 regen outputs exist in `infrastructure/artpipe/done/graffiti_vandal_regen_v1_{0..5}`; the mod's `RM_Graffiti_Vandal` folder has 6 files. Whether they ARE the regen outputs is UNMEASURED (needs a byte or hash compare against `_artsrc`/done outputs). `mark_carries_no_earth_signage` needs `GRAFFITI_WARNGLYPH_INUNIVERSE_1`; no live item file by that name exists under `infrastructure/state/items/` (it may be closed), so its state is UNMEASURED. | S to measure | Yes |
| G4 | Mod Settings | 6 fields (5 checkboxes, 1 slider 60-1000). 5 of 5 checkboxes have tooltips; the slider has a live value label but no tooltip. No reset-to-defaults button. No worldgen-affecting toggle (none apply). All-off: `paintingEnabled` gates joy, spree, designated work and raid-exit tagging, so painting off also stops raid tagging (confirmed in code: `RaidExitTagger.cs:41`). Graceful degradation reads fine in code; the live all-off proof is the plan's job. | S (slider tooltip, reset button) | Yes |
| G5 | Dead setting | `viewerReactionEnabled` is read only by `ThoughtWorker_ViewedGraffitiMark.cs:30`. Graffiti's `Defs/` contains no `ThoughtDef` at all (checked: no file). The only ThoughtDef using that worker is in `SacredGraffiti/Defs/ThoughtDefs_SacredMarks.xml`. So in Graffiti alone the setting gates nothing and misleads. `breachBiasEnabled` is NOT dead: `breachLure` appears in `Defs/ThingDefs_Graffiti.xml`. Acceptance wants the checkbox labelled or removed. | S | Yes |
| G6 | Hashed prose | Plan §5.7: correct and re-validate on the owner's word (`modcheck validate Graffiti --owner-said`). | S plus the owner's word | No: needs his word in the same sitting |
| G7 | Variant counts | Vandal 6 variants vs 3 Scratches, 3 Tally, 4 WarningGlyph (`GRAFFITI_VARIANT_COUNTS_1`). Content, not a bar. | M | Yes |
| G8 | Rungs before SHIPPED | Both GREEN rungs (acceptance bullet 1) and WIRED are not closed: `shows=` in `validation.py`. Not measured here (needs a live run). | L | Live only |

Counts: 8 gap rows, of which 5 are SHIPPED-rung proper (G1, G2, G4, G5, G6); G3, G7, G8 are bar/rung dependencies.

---

## Pyrelands

### (a) Deployed vs repo
- Standalone deploy refuses: Pyrelands is folded into `mandrake.rm.biomes`. `deploy_custom_mods.py --compose biomes` dry run: all 54 Pyrelands files are in sync (no Pyrelands lines in the drift list); `BiomesShell` `RimMandrake.Biomes.dll` in sync. `.srchash` MATCH for `FireEcologyHook.dll`, `RimMandrake.Biomes.dll` and `PyrelandsMechanics.dll`.
- The composed mod as a whole is NOT at 0 diff: the plan says "drift found": 13 repo-only adds, 23 changed, 3 game-only (`Biomes/ForsakenCrags/*`, not in repo), 10 held. All drift is in other biomes (FeverWood, LeaningScrub, LongShade, RustCathedral, Stillsand, TheForge, `_Kits/CreatureBehaviors`), none in Pyrelands. The acceptance bullet "the composed `mandrake.rm.biomes` deploys at 0 diff" therefore fails on other biomes' work.
- `deploy_custom_mods.py --mod UtinniPatches` (where the RUT_ Pyrelands cast lives): 0 adds, 0 changes touching Pyrelands cast files (grep for ashwallow, emberscythe, firehawk, firewasp, flamefang, furnace, barbslinger, sytheclaw found nothing in the drift list). UtinniPatches has its own drift (held/no-art files, 3 game-only `RM_Qorrax` textures) unrelated to Pyrelands.

### Gap table

| # | Area | Gap | Size | Offline-doable |
|---|---|---|---|---|
| P1 | Code review | 7 DIRTY of 25 in `Pyrelands/Source`: `FireEcologyHook.cs` (555 lines, changed since mark `b4fc03515`), `RM_PyrelandsMod.cs` (358, changed since mark), `PyrelandsTuning.cs` (368, changed since mark `b16769f98`), `PyrelandsMechanicsDefOf.cs` (31, changed since mark), and three never marked: `RM_BurrowOnFireExtension.cs` (30), `RM_JobDriver_Burrow.cs` (92), `RM_JobGiver_BurrowOnFire.cs` (98). Plus `BiomesShell/Source/RM_BiomesMod.cs` (207, never marked). `validation.py` is CLEAN now and will dirty on wiring. The 8 PyrelandsMechanics `.cs` in `src/RimUtinni/PyrelandsMechanics/Source` are all CLEAN. The item listed 6 DIRTY in Pyrelands; measured 7 (`FireEcologyHook.cs` also dirty now). | M-L (about 1900 lines in the 8 DIRTY C# files) | Yes |
| P2 | Art: no texture | `RUT_Ashwallow`: `Things/Pawn/Animal/Pyrelands/Ashwallow/Ashwallow` resolves to nothing in the repo (UtinniPatches/Textures has no Ashwallow folder). Searched `infrastructure/artpipe/done`, `failed`, `active`, `pending`, `_artsrc`, `Transient/` and `design/` by name: the only hit is the def XML. No art exists. | M (3 facings via artpipe; brief from the def's description) | Yes (daemon) |
| P3 | Art: placeholder | `RUT_Emberscythe` uses vanilla `Things/Pawn/Animal/Megascarab/Megascarab`. `emberscythe_v1_{east,north,south}` exist in `infrastructure/artpipe/done/` (and review images in `Transient/art_review_2026-09-12/`). OWNER RULING FOUND: `Transient/rot_flora_fauna_review_2026-09-18.decisions.json` has `B_RUT_Emberscythe` decision `cut` (2026-09-19, note empty), summarised as "2 cut (BovineBeetle, Emberscythe)". That is the Rot's review sheet and a sheet's cut is scoped to its own biome, so it does not by itself remove Emberscythe from the Pyrelands roster (`WildAnimals_Pyrelands.xml` still lists it). A decision is needed: keep it in Pyrelands and wire the v1 art, or cut it from Pyrelands too. | S once decided | Yes after a ruling (needs the owner's word on the Pyrelands sitting) |
| P4 | Art: redesign open | `BARBSLINGER_SCORPION_REDESIGN_1` open (art exists at `Things/Pawn/Animal/Pyrelands/Barbslinger/Barbslinger`, and `barbslinger_scorpion_v1_{east,north,south}` is in `_artsrc`). Redesign status not measured. | M | Yes (art) |
| P5 | Art: flyer | FireHawk flip-book frames exist (`FireHawk_Flying_1..5_*`, 90 `rut_firehawk_flying_*` files in artpipe done). Live visual judging is joint-session only per the 3x owner rule. `FIREHAWK_FLIGHT_BEHAVIOR_1` can close only by a state-read `[Tool]` or an owner-present session. | S (state-read tool) + owner session | State-read tool: yes. Visual: no |
| P6 | Art: vanilla reuse | The 17 Pyrelands-owned def texPaths: 8 not in repo, all vanilla (`Terrain/Surfaces/*`, `Things/Filth/Ash`, `ShellFirefoam`, `Revolver`). Functional, not BadTex. Dessicated corpse textures (`Dessicated_Megaspider/Warg/Cobra/Megascarab`) are vanilla too. The 7 donor-mod fauna (Anooba, Dalgo, Gizka, Iriaz, Nuna, Orray, Zeer) resolve inside `RimStarWars/SWBestiary`. | none | n/a |
| P7 | Mod Settings | Pyrelands page `RM_PyrelandsSettings` is thorough: master `pyrelandsEnabled`, per-mechanic checkboxes with tooltips, sliders, and the worldgen-affecting rows are labelled ("WORLDGEN-AFFECTING - new worlds only/new maps only"). Gaps: (1) the unified-mod per-biome toggle `RM_BiomesSettings.Enabled("Pyrelands")` gates worldgen only; the only reference to `RM_BiomesSettings` in the repo is `BiomesShell/Source/RM_BiomesMod.cs`, so no mechanic code reads it (confirmed). Pyrelands mechanics gate on their own `pyrelandsEnabled` instead, so two toggles control one biome and the Baroque Biomes toggle does not stop the mechanics. (2) No reset-to-defaults button. (3) Whether the Pyrelands page remains visible as its own category after composition is UNMEASURED. | S-M (a one-line check per mechanic entry point, or have `pyrelandsEnabled` read `RM_BiomesSettings.Enabled`) | Yes |
| P8 | Deploy hygiene | Composed mod has 13 adds / 23 changes / 3 game-only / 10 held, none in Pyrelands (see above). Needs the other biomes' owners to apply, or a `--compose biomes --apply` pass by the owner of the deploy. | S per apply | Apply is a write to the game folder; this audit did not apply |
| P9 | Wiring and walk | `shows=` wiring 0/19 bars; `validation.py` docstring stale; inert `PatchOperation` guards ×2 in `WildAnimals_Pyrelands.xml` (`PATCH_MAYREQUIRE_GUARD_INERT_1`). | M | Yes |
| P10 | Not gaps | 0 world tiles on Ash'karr (expected until the one paint pass); no DLC fallbacks owed. | n/a | n/a |

Counts: 9 gap rows (P1-P5, P7-P9, plus P6 which is informational, not a gap).

---

## Cross-mod observations
- Every settings page has tooltips on its checkboxes and none has a reset-to-defaults button.
- All-off proof is missing everywhere: none of the three `validation.py` files has an all-off component.
- Art generation is mostly offline-doable through the artpipe daemon; judging legibility and flyers needs the owner or the northstar judge.
- Code-review DIRTY totals: FlowWorks 4, Graffiti 3, Pyrelands 7, BiomesShell 1 = 15 files.
