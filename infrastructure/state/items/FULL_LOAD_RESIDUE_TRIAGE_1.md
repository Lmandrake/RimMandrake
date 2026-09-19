## (1) patchfail lines — FIXED, live re-confirmation owed

10 NEW patchfail lines in the 2026-09-18 10:35 harvest, all root-caused by
reading `Transient/Player.log.pre_restart_enable_injections_2026-09-18` around
the stack traces (lines 869-920), not just the one-line summaries:

- **4x `OuterRim_DroidWeapon_*` `PatchOperationConditional`** (WeaponTags_Renormalise.xml)
  — already FIXED before this pass, by `OUTERRIM_DROIDDEPOT_PATCH_GUARD_1`
  (commit `72995c875`, merged `80b5742de` at 2026-09-19 00:29:09), which lands
  AFTER the 10:35 harvest that reported them. No action needed here; live
  re-confirmation will show 0.

- **5x `PatchOperationFindMod(ABF: Artificial Beings Framework)`**
  (`src/RimStarWars/StarWarsPatches/Patches/DroidDonor_ABFGate.xml`, sites 2-6)
  — REAL, but not the breakage the file's own header assumed. ABF genuinely
  is NOT active (`Killathon.ArtificialBeings` absent from every 2026-09-18/19
  ModsConfig snapshot checked), so `nomatch` correctly fires — but the targets
  it tries to Remove (`guy762_DroidPawnKindBase`, `KotORDroidBase_good`,
  `SWCPDroidBase_bad`, `guy762_DroidBattery[_adv]`) only exist when
  `guy762.KotORDroids` or `SWCP.GCWVehicles` is ALSO active (kotorcore's
  `_DroidsBase`/`_BnSDroidsBase` `AdditionalMods` folders, `LoadFolders.xml`
  gated `IfModActive`) — both confirmed absent too, even though kotorcore
  itself (`guy762.mm.kotorcore`, "Star Wars KotOR Resources and Materials")
  IS active. So `PatchOperationRemove` finds nothing and logs a false
  failure. FIXED: wrapped each site's `Remove` in an inner
  `PatchOperationConditional` (xpath-exists test, `match`-only, no `nomatch`)
  — same silent-no-op shape already used elsewhere in this repo
  (`Armoury/Patches/Warcasket_BuildPathCut.xml`) and the same root cause class
  as `OUTERRIM_DROIDDEPOT_PATCH_GUARD_1`.

- **1x `PatchOperationFindMod(Star Wars KotOR Resources and Materials)`**
  (`src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml`, final
  Operation) — same root cause: `guy762_debugxenotype_droid` (a debug
  XenotypeDef) only exists via the same `_DroidsBase`/`_BnSDroidsBase`
  folders, absent for the same reason. FIXED: added an outer
  `PatchOperationConditional` gating the whole label/description-edit
  sequence on that XenotypeDef existing at all.

`validate_patch.py --defs <Data> <Mods> <Workshop 294100>` on both edited
files: **0 errors** (170 advisory warnings, pre-existing/expected shape,
unrelated to these edits). The new guard on the Xenotype file reports
"test xpath matches 0 nodes ... Expected if the target mod is not installed"
— exactly the intended dormant state.

**Owed**: live-load re-confirmation that patchfail count actually drops to 0
(this was an offline-only pass, no bridge/restart used).

## (2) Config errors 93 vs baseline 17 — FIXED (bulk), one investigated-clean, one pre-existing-unrelated

Read exact text with `harvest_log.py --show configerror --stale-ok` (declared
stale, offline dump), not guessed from the summary count.

- **42 of 93 — the aquatic Juv wave**
  (`src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_NurseryJuveniles.xml`):
  exact text is `Config error in RSW_<X>Juv: lifeStages minAges are not in
  ascending order`, 6x each for `RSW_{Mee,Faa,Laa,Yobshrimp,SiltLamprey,
  RustNipper,OpeeSeaKiller}Juv`. Root cause: every one of the 7 `ThingDef`s'
  `<lifeStageAges>` override was missing `Inherit="False"`. RimWorld's
  default List<T> merge on `ParentName` inheritance APPENDS rather than
  replaces, so each Juv's own 2-stage list (Baby, Juvenile, ascending) landed
  AFTER the already-inherited 3-stage vanilla `AnimalThingBase` list
  (Baby, Juvenile, Adult, also ascending) — 5 stages total, going up then
  back down to 0. FIXED: added `Inherit="False"` to all 7, the same pattern
  already used in this repo (`ThingDefs_ForsakenCrags.xml`,
  `RUT_LivingBolt.xml`, `RUT_CathedralRoach.xml`). `validate_patch.py`: 0
  errors, 0 warnings.

- **`RSW_KilnClay`** — exact text: `ingestible preferability >
  DesperateOnlyForHumanlikes but socialPropernessMatters=false`. Real bug:
  its `ParentName="ResourceBase"` doesn't set `socialPropernessMatters`
  (defaults false), unlike vanilla's own `RawBad`-preferability base
  (`PlantFoodRawBase` in Core's `Items_Resource_RawPlant.xml`), which sets
  `<socialPropernessMatters>true</socialPropernessMatters>` at the ThingDef
  level specifically to avoid this warden/prisoner-feeding bug. FIXED: added
  the same field. (`validate_patch.py` also flagged 2 PRE-EXISTING, UNRELATED
  texPath errors on this file — `RSW_KilnClay`'s and `RSW_CrackedCeramicShards`'
  own art — not touched, not part of this item, not introduced by this edit;
  matches the already-known `KOTORCORE_ABSORPTION_MISSING_TEXTURES_1` class
  noted elsewhere in the ledger.)

- **`RUT_TwinkleSpikeTestPlant`** — flagged as a TEST def in the shipping
  list. Investigated against its own item, `TWINKLE_FLORA_SPIKE_1`: that
  item is CLOSED/done, but its own report explicitly says a live density
  measurement is STILL OWED and names this exact def as "the one test plant
  this spike was scoped to... spawn it by hand to observe it" — so it must
  stay spawnable, not be deleted. Two real bugs, both fixed without removing
  the def: (a) `has nutrition but ingestible properties are null` — had a
  stray `<Nutrition>0.1</Nutrition>` statBase with no `<ingestible>` block;
  removed the statBase (a tick-cost test article has no reason to be food).
  (b) `Could not load Texture2D at 'Things/Plant/Bush'` — vanilla's own
  `Plant_Bush` inherits `Graphic_Random` from `PlantBaseNonEdible`, so no
  bare single-file "Bush" texture exists for this def's (mechanism-required)
  `Graphic_Single` to load. Repointed at `Things/Building/Production/DeepDrill`
  instead — a real vanilla Graphic_Single asset, the same placeholder-reuse
  pattern this mod already uses live in `RUT_DigShaft.xml` (confirmed:
  `validate_patch.py` flags that file's identical texPath with the identical
  ERROR text — a documented checker blind spot, `validate_patch.py:1906`,
  for vanilla-only assets baked into `resources.assets`, invisible to the
  loose-file scanner — not a real defect).

- **`RM_FE_Ground_SoilRich`** — investigated, NOT a defect. Exact text
  `burnedDef is flammable` is the owner-ruled EXPECTED/ACCEPTED warning
  documented right in the file's own header (`ScorchableGround.xml`, ruling
  2026-09-03): the fire-ecology mechanism deliberately chains
  ground→ash→ash→...→terminal, so `burnedDef` pointing at something
  flammable is the whole point, not a bug. No action; matches the other 3
  siblings (`Sand`/`Gravel`/`Soil`) already carrying the same warning at
  baseline.

**Owed**: live-load re-confirmation of the new configerror count.

## (3) 10 Scribe refs to `Meat_TYR_*`/`Corpse_TYR_*` — ROOT CAUSE WAS WRONG, no save affected

The item's own filing assumed "a SAVE holds a dead def name." That
assumption does not survive a check of the actual log: this log
(`Player.log.pre_restart_enable_injections_2026-09-18`) contains **zero**
save-loading strings anywhere (no "LoadGame", no `.rws` path, nothing) — per
`rimworld-savegame`'s own §1, it never loaded a save at all; these Scribe
lines fire from the OTHER startup-deserialized surface: `Config/Mod_*.xml`.

Traced by grepping the live LocalLow `Config/` folder directly (never the
repo) for the exact defNames:

- **`Config/Mod_3532608331_DeepStorageMod.xml`** (LWM Deep Storage's own
  persisted per-defName settings list) carries all 10:
  `Meat_TYR_{HotfootRat,KangarooRat,Lemming,Mouse,MousePoison}` and
  `Corpse_TYR_{same 5}`, each inside a plain `<li>` list.
- **`Config/Mod_3521312241_Mod_CherryPicker.xml`** (our own Cherry Picker
  tool's live cut-list) separately carries 2 of them:
  `ThingDef/TYR_KangarooRat`, `ThingDef/TYR_Mouse`,
  `ThingDef/Meat_TYR_KangarooRat`, `ThingDef/Meat_TYR_Mouse` — matches
  `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`'s tracked cut
  list line-for-line (git-tracked, confirmed).

`TYR_` = `tyrannidae.fancyratsplus` ("Fancy Rats Plus"), confirmed live in
ModsConfig.xml today. Our own repo patches reference `TYR_KangarooRat`
against a "(Little Critters)"-labelled pairing in
`AnimalBiomeDuplicates_Fix.xml`/`AnimalTolerances_Ashkarr.xml` — those are
unrelated xpath patches on the still-live mod's OTHER species, not the
source of the dead names.

**Disposition: no campaign save touched, none at risk, nothing edited.**
Both files are LIVE, per-install LocalLow `Config/` state OUTSIDE this repo
(not `Mods/`, not a save) — DeepStorage's is entirely third-party and not
ours to edit; Cherry Picker's live copy could in principle be cleaned of 2
stale entries, but that is a live-game action on a running install
(`live-load re-confirmation... separate later step` per this item's own
ground rules), not an offline-repo fix. These 10 lines are advisory boot
noise only — they cost nothing at runtime beyond the log lines themselves,
never touch colony state, and are NOT the "SAVE holds a dead def name" risk
class this item was filed under.

**Owed**: if wanted, a live-game pass could re-save Cherry Picker's live cut
list without the 2 stale `TYR_` entries and/or ask LWM DeepStorage to purge
its own stale cache — neither is a repo change, both are optional cleanup
with zero urgency.

## (4) 2026-09-19 FOUNDRY (overnight full-621-mod batch) — live re-confirmation + one NEW regression found and fixed

Full 621-mod cold load, confirmed via `Bridge token:`. `harvest_log.py` full sweep:

- **A genuinely NEW config error, caused by this item's own (1) fix**: 7 lines,
  `Config error in RSW_{Mee,Faa,Laa,Yobshrimp,SiltLamprey,RustNipper,OpeeSeaKiller}Juv:
  PawnKindDef defines 5 lifeStages while race def defines 2`. Root cause: the (1) fix
  above added `Inherit="False"` to each Juv **ThingDef's** `<lifeStageAges>` (correctly
  trimming the ThingDef to 2 stages), but the sibling **PawnKindDef's** own
  `<lifeStages>` block (already hand-written with exactly 2 `<li>` entries, per this
  same file's own header comment: *"PawnKindDef.lifeStages is trimmed to match (2
  entries instead of 3)"*) had no `Inherit="False"` of its own — so it inherited its
  parent kind's 3-stage list and APPENDED its 2, landing at 5, the same
  List<T>-append shape as the original bug, just one field over. **FIXED**: added
  `Inherit="False"` to all 7 `<lifeStages>` blocks in
  `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_NurseryJuveniles.xml`.
  Deployed this session (`deploy_custom_mods.py --mod SWBestiary --apply`).
  **Not yet live-re-verified** — defs are startup-parsed only, and this repo's own
  batch-restart doctrine says don't spend a second full restart to prove one
  def-only XML fix; it rides the next natural load.
- **patchfail**: live count read **96** (baseline 5), not 0 as the (1) entry above
  expected. Broken down: 75 of 96 are `[RimUtinni Patches (Jawa campaign)]
  PatchOperationConditional(.../BMT_*/statBases) failed` (from
  `AnimalTolerances_Ashkarr.xml`) and 10 more are the sibling
  `[RimStarWars Patches] .../BMT_*/weaponTags failed` (from
  `WeaponTags_Renormalise.xml`) — a large, previously-uncounted-at-this-scale wave
  hitting dozens of `BMT_*` creature defs each. **NOT investigated further this
  pass** (time-boxed) — flagging as the single highest-value unresolved thread from
  this item: 85 of the 96 current patchfail lines are this one wave, from two
  patch files each iterating the full `BMT_*` roster. The 10x `ABF`-gated fix and
  4x `OuterRim_DroidWeapon` fix from the (1) entry above are confirmed absent from
  this list (i.e., those two specific fixes are holding) — this is a DIFFERENT,
  larger, not-yet-triaged wave.
- **configerror**: live count read **160** (baseline 17). A large fraction is
  repeating `RM_LiquidProperties does nothing beyond documenting viscosity...`
  advisory lines (WaterDeep/WaterShallow/Marsh/slime fills etc.) which read as
  intentional/advisory per their own text, not investigated as defects. The 7 Juv
  PawnKindDef lines above are the one new confirmed regression; the rest of the
  160 were not individually triaged this pass.
- **1 DEAD MOD**: `JumppackForMeleeAI` — `Error in static constructor of
  JumppackForMeleeAI.JumppackForMeleeAI: ... HarmonyException` (third-party mod,
  not ours). Not investigated further — flagging only.
- **5 DEFS DISCARDED**: all from `Absorbed_*` files (this repo's own Cherry
  Picker/absorption output) — `Absorbed_KotorWeapons_WeaponRanged_KotOR{Bowcaster,
  HeavyRepeater,LightRepeater}.xml` each fail on `Could not find type named
  IgnoreConfigErrors.Ignore_ForcedMissRadius`, and
  `Absorbed_Kotorcore_BTDKotORGravships_Gravship_{DynamicFreighter,KT400Freighter}.xml`
  each fail on `Could not find type named SWCP.Core.ThingComps.
  CompProperties_HideShipRoof`. Both missing types belong to donor mods/classes not
  currently active in this mod set — these are absorbed-content files referencing a
  class from whatever mod they were absorbed from, not currently satisfied. Worth a
  proper investigation (is the type genuinely gone, or is this a load-order/
  MayRequire gap in the absorbed file) but not attempted this pass.

**Not pulled this pass** (time-boxed, ~250 lines of the original ~350 remain
untouched): crossref (185), stale Scribe (105 — largely the DeepStorage/CherryPicker
advisory noise already root-caused in (3) above, likely unchanged).
