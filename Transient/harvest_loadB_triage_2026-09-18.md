# Load B harvest triage — 2026-09-18

Source: `Transient/harvest_loadB_2026-09-18.txt` (log written 2026-09-18 15:00/15:01, 632 mods).
Raw `--show` dumps: `Transient/harvest_loadB_crossref_2026-09-18_tmp.txt`,
`harvest_loadB_scribe_2026-09-18_tmp.txt`, `harvest_loadB_configerror_2026-09-18_tmp.txt`,
`harvest_loadB_patchfail_2026-09-18_tmp.txt`, `harvest_loadB_outerrim_2026-09-18_tmp.txt`,
`harvest_loadB_checkcfg_2026-09-18_tmp.txt`.
Earlier-today comparison logs (10:35, 635 mods): `harvest_crossref_2026-09-18_1035.txt`,
`harvest_scribe_2026-09-18_1035.txt`, `harvest_patchfail_2026-09-18_1035.txt`.

## cross-reference

181 lines / 19 distinct messages now, vs 444 lines / 192 distinct at 10:35 — **net improvement**,
not a regression. The huge cluster of `Water*`/`Marsh`/`ShallowFloodwater`/`RM_Fill_*`/
`RM_WaterBrackish*` etc. TerrainDef cross-refs (~170 distinct messages at 10:35, tied to
FlowWorks LiquidTypes/LiquidTerrainSuite) is GONE in this load — whatever changed between
10:35 and 15:00 (LanternDeeps/LiquidTypes deploy, or the CAVERNS_PARITY_BUILD_1 sweep at
`2ea6edfc1`) fixed it. Do not re-open that as a defect.

**Pre-existing, NOT new** (present at 10:35 too):
- `RUT_VentForge` (wanter=recipeUsers) x111, `RUT_VentKiln` (wanter=recipeUsers) x39 — 150 of
  181 raw lines. OURS (RimUtinni FlowWorks). A missing/renamed ThingDef referenced by many
  RecipeDefs' `recipeUsers`.
- `Pawn_Squirrel_Call` SoundDef x4, `RUT_TibannaGas` x1, `RM_GreentideChurnmud` x1 — all present
  at 10:35, unchanged.

**NEW since 10:35** (9 distinct messages, all OURS — RimStarWars SWBestiary / RimUtinni):
- `RSW_Scavrat`, `RSW_Scurrier`, `RSW_Runyip` PawnKindDef not found (wanter=BiomeAnimalRecord)
- `RSW_Qormot` BodyDef not found
- `RSW_Leather_Ronto`, `RSW_Ronto_Meat` ThingDef not found (wanter=RaceProperties)
- `RSW_SW_GoldForage` AbilityDef + TrainableDef not found
- `EmptyAICore` ThingDef not found (wanter=thingDefs) x2

**CONFIRMED cause (deploy lag, not a code bug) for the SWBestiary/Ronto/GoldForage cluster:**
`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (committed, deployed, MayRequire
`mandrake.rsw.swbestiary`) was extended today (commits `f2f0ac8f9` "Pass 20: wire
Pufferpig/Qormot/Ronto" and the still-**uncommitted** Pass 21 Scavrat/Scurrier/Runyip work) to
reference new SWBestiary species/items. But the deployed copy at
`/mnt/c/.../RimWorld/Mods/SWBestiary/` is stale:
- `RSW_Scavrat.xml`, `RSW_Runyip.xml`, `RSW_Scurrier.xml` are **untracked in git** (`git status`
  shows `??`) and are **absent entirely** from the deployed `Defs/ThingDefs_Races/` folder.
- `RSW_MlieWaveC_Bodies.xml` has an **uncommitted 455-line diff** on disk (adds Scavrat/
  Scurrier/Runyip BodyDefs on top of an already-committed Qormot BodyDef); the deployed copy
  has **0 matches** for `RSW_Qormot`/`RSW_Scavrat`/`RSW_Runyip`/`RSW_Scurrier` — even the
  committed Qormot BodyDef never made it to Mods/.
- `RSW_MlieWaveC_Resources.xml` (committed, has `RSW_Leather_Ronto`/`RSW_Ronto_Meat`) and
  `RSW_MlieWaveC_Abilities.xml` (committed, has `RSW_SW_GoldForage`) both show **0 matches** in
  the deployed copy.
Net: the patch that adds these species/items to Ash'karr was deployed; the mod that defines
them was not (mid-flight commit, `deploy_custom_mods.py --apply` never re-run for SWBestiary).

**CONFIRMED (real bug, not deploy lag) for `EmptyAICore`:** `src/RimUtinni/ResearchRetag/
Defs/ThingDefs_Buildings/RUT_Ported_GravForge.xml` (committed+deployed today, `59944939f`
"RESEARCH_TRIO_RETIRE_1") references `EmptyAICore` in `recipeUsers`/`thingDefs`. Searched the
full deployed `Data/` and `Mods/` trees for `<defName>EmptyAICore</defName>` — **zero hits
anywhere**. This defName does not exist in any active mod or core. OURS, needs a fix (find the
real intended ThingDef or drop the reference), not a deploy-lag issue.

## scribe

10 lines, **identical** to the 10:35 snapshot (same `Meat_TYR_*`/`Corpse_TYR_*` set, same order).
Not new — a pre-existing, already-red stale-save reference (TYR_ prefix — third-party, not
ours). No action needed for Load B specifically.

## configerror

`check_config_errors.py` classifies against `config_error_baseline_2026-09-06.json` (12 days
stale), so most of the 97 "new" distinct lines are new only relative to that stale baseline,
not new to today. No same-day-morning configerror snapshot exists to diff against directly, so
clusters below are dated by git history instead.

**Known-by-design, not a defect** (~26 distinct TerrainDefs x2 = most of the volume): every
`RM_LiquidProperties does nothing beyond documenting viscosity...` line (WaterDeep, Marsh,
RM_Fill_*, RM_Water*, RM_Ichor*, RM_Ooze*, RM_Tar*, VEE_*, etc.) — this is FlowWorks' own
liquids-framework authoring check, ruled canon 2026-09-13 (`liquids_framework_design.md`): "an
empty extension is still a complete, working liquid." OURS, explicitly not a hard error.

**Pre-existing (dated by git, not new today):**
- `RSW_*Juv` (`MeeJuv`, `FaaJuv`, `LaaJuv`, `YobshrimpJuv`, `SiltLampreyJuv`, `RustNipperJuv`,
  `OpeeSeaKillerJuv`) "lifeStages minAges are not in ascending order" — from
  `SeaBeasts_NurseryJuveniles.xml`, last touched `05974eeb4` (2026-09-11), clean/deployed. A
  week-old standing bug, just newly visible against the stale baseline. OURS.
- Third-party, unrelated to today: `ModernFixtures`/`RR_Furniture` research-tab collision,
  `AdvancedShowers`/`VCE_StewCooking` collision, `RR_LateralThinking`/`RR_Organization`
  researchView not set, `AM_AncientLogisticsSystem` and `guy762_*` Hyperweave tradeability,
  `TargetedInsultingSpree` label chars, `Techprint_RR_lighting` trailing whitespace.

**NEW / worth a look (OURS, from today's RimUtinni work):**
- `Utinni Shellmandrake.rut.menushell` — "defName ... should only contain letters, numbers,
  underscores, or dashes." PLAUSIBLE: looks like a packageId string (`rut.menushell`) got
  pasted into a `defName` field by mistake. Needs a source-file read to fix; not yet located.
- `RUT_GiveQuest_VaultThaw_V1..V6` — "quest is run from both incident and random quest" x6,
  one per Vault-Thaw quest variant (RustCathedral/Scorch/FallLine/Deadstone/Slough/Umbra).
  Systematic across all 6 siblings — PLAUSIBLE a shared authoring pattern (dual incident+random
  hookup) rather than 6 independent mistakes.
- `RUT_BrineDeposit_Tekk/Drazz/BrinePlate` — "claimable item is compressible; faction will be
  unset after load" (FlowWorks brine deposits).
- `RUT_BrinePlate` — "graphicClass is null." PLAUSIBLE missing art/graphicData, likely a
  placeholder item not yet finished.
- `RUT_TwinkleSpikeTestPlant` — "has nutrition but ingestible properties are null." Name says
  "Test" — likely a leftover dev-test def that should be deleted, not fixed.
- `RUT_Slough_GelatinousBreach`, `RUT_ComplexStructures` — LandmarkDef "no mutators with a
  chance of 1 or higher."
- 3x `Exception in ConfigErrors() of <biome>` (`AridShrubland`, `Desert`, `ExtremeDesert`) —
  `System.NullReferenceException`. These are the Ash'karr-relevant campaign biomes. Not yet
  root-caused (no stack trace in the harvested lines) — PLAUSIBLE tied to the same FlowWorks
  liquid/terrain wiring touched by today's CAVERNS_PARITY_BUILD_1 sweep, given the crossref
  section's TerrainDef churn, but this needs the full exception text from Player.log to confirm.
- `RSW_Orray` — tool with `linkedBodyPartsGroup Teeth` but body has no Teeth part group.
- `RSW_KilnClay` — ingestible preferability/socialPropernessMatters mismatch (warden food-serve
  bug risk).

## patchfail

16 lines, **identical set and order** to the 10:35 snapshot — not new to Load B. Same 16 as
this morning: `Torment Master`→HAR (Humanoid Alien Races) FindMod, `Vanilla Mining Outpost
Patch`→Gemstones/Jewelry FindMod, `Biomes! Caverns`→PlaceWorker Replace, `Intimacy - Gender
Works` x3 Remove ops, `RimStarWars Patches`→ABF FindMod x5 + `Conditional(.../weaponTags)` x4
on `OuterRim_DroidWeapon_{BlasterCannon,TwinWristBlaster,WristBlaster,WristBlasterIon}`, `Jawa
Pawn Flavor`→KotOR Resources FindMod. All third-party donor mods except the RimStarWars
Patches xpath no-matches, which are OURS but a documented no-op (context note: these Conditional
ops no-match on `OuterRim_DroidWeapon_*` because the earlier `PatchOperationAdd` for the same
defNames already fails to find its target node — see `harvest_loadB_outerrim_2026-09-18_tmp.txt`
line 11-14 `Failed to find a node with the given xpath` for the same 4 defNames). Baseline is 5;
these extra 11 have been standing since at least 10:35 today — not a Load B regression.

## outerrim

8 lines = 4 `PatchOperationAdd(xpath=".../ThingDef[defName=\"OuterRim_DroidWeapon_*\"]")` →
"Failed to find a node with the given xpath" + the same 4 `PatchOperationConditional(.../
weaponTags)` failures already counted under patchfail. Single root cause, CONFIRMED by reading
`StarWarsPatches/Patches/WeaponTags_Renormalise.xml`'s own xpath (per the task's own context
note): the `Add` targets `ThingDef[defName="OuterRim_DroidWeapon_BlasterCannon"]` etc. and those
4 ThingDefs do not exist under the current OuterRim mod version/load order, so the xpath
matches nothing and both the `Add` and the dependent `Conditional` no-op. Not new to Load B —
present in the same form in the 10:35 patchfail snapshot. Third-party donor mod (OuterRim) is
the reference target; our `StarWarsPatches` patch is the one that needs a defName check or
`PatchOperationFindMod` gate.

## Verdict

- **Most important finding**: SWBestiary (RimStarWars) mod deploy is stale. `RSW_Scavrat.xml`/
  `RSW_Runyip.xml`/`RSW_Scurrier.xml` are untracked-in-git and entirely missing from the
  deployed Mods/SWBestiary folder; `RSW_MlieWaveC_Bodies.xml` has an uncommitted 455-line diff
  never deployed (not even the already-committed Qormot BodyDef made it out); Resources/
  Abilities files with Ronto leather/meat and GoldForage are committed but also not deployed.
  Fix: commit the Pass 21 work, then `deploy_custom_mods.py --mod SWBestiary --apply`.
- **Second finding, real bug**: `RUT_Ported_GravForge.xml` (RimUtinni ResearchRetag,
  `59944939f` today) references `EmptyAICore`, a ThingDef that exists **nowhere** in the active
  632-mod set or core data. Needs the real intended defName or the reference dropped.
- crossref is net BETTER than 10:35 (192→19 distinct) — the FlowWorks/LiquidTypes TerrainDef
  storm from this morning is resolved, do not re-file it.
- scribe, patchfail, outerrim: all unchanged from the 10:35 same-day log — none are new to
  Load B, no action needed today.
- configerror: bulk is the known-canon liquids "authoring check" (not a defect) plus a
  week-old RSW_*Juv lifeStages bug; worth a look but not urgent: `Utinni Shellmandrake.rut.
  menushell` malformed defName, `RUT_BrinePlate` null graphicClass, `RUT_TwinkleSpikeTestPlant`
  (looks like leftover test content), and the 3 NullReferenceExceptions in ConfigErrors() of
  AridShrubland/Desert/ExtremeDesert — the last is Ash'karr-relevant and PLAUSIBLE-only, needs
  the full stack trace to root-cause.
