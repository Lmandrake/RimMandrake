# FLOOD_CANYON_BIOME_1 — flooded-canyons biome as a standalone RimMandrake mod

Owner, 2026-09-12 (verbatim on the filing event): the flood-witness work
restructures into its own standalone biome mod — canyons that get periodically
flooded, flooding as one of its events, the chime warning mechanic included.
RimMandrake tier: not Star Wars specific, playable on any planet.

## spec
- Biome mod per the tier grammar (`design/NAMING_SCHEME_PLAN.md`): packageId
  `mandrake.rm.<name>`, RM_ prefixes, namespace `RimMandrake.<Mod>`. No
  RSW_/RUT_ token, no Star Wars string inside.
- Core content: a canyon biome whose floor floods on a cycle — warning chimes
  (the Cracked Lands chime mechanic, generalized), then the wall of water,
  then soak-driven explosive plant growth where applicable.
- Design inputs already written (campaign register — generalize, don't copy
  lore): `design/Jawa/worldbuilding/biomes/the_cracked_lands.md` §10b (flood
  weeks canon), `design/Jawa/worldbuilding/flood_witness_event_design.md` (the ruled campaign design: chime tells,
  injury-ceiling lethality, invitation route),
  `design/Jawa/worldbuilding/explosive_plant_growth_design.md` (growth mechanic; core
  rulings landed 2026-09-10 in its §7 — injury-ceiling lethality etc.).
- MOD_OPTIONS_RETROFIT_1 doctrine applies from day one: per-feature Mod
  Settings (flood cycle on/off + period, chime lead time, growth coupling,
  canyon biome insertion vs feature-only in other biomes).
- The CAMPAIGN plot beat (guaranteed first witnessing per the ruled
  invitation design in `flood_witness_event_design.md`) stays in the Utinni layer and consumes this
  mod as a dependency — it is NOT part of this mod.
- Coordinate with GREENTIDE_STANDALONE_MOD_1 / SHIP_VERMIN_MOD_1 on where
  shared RM_ mechanics assemblies live.

## verify
Mod folder with About.xml + packageId `mandrake.rm.*`; deploys via
deploy_custom_mods.py; no Star Wars token; flood cycle + chimes provable on a
quicktest map in the canyon biome; features toggleable per settings.

## criteria
A player with only this mod gets flooded canyons with chime warnings on any
world; the Utinni campaign rides it for the witness beat.

## status 2026-09-12 (FOUNDRY)

Built: `src/RimMandrake/FloodedCanyon/` — standalone mod, packageId
`mandrake.rm.floodedcanyon`, no Star Wars/campaign token anywhere (grepped).

- **Biome**: `RM_FloodedCanyon` BiomeDef + `RM_BiomeWorker_FloodedCanyon`
  (rarity-gated worldgen insertion, same pattern as the sibling Gelatinous
  Slime mod's own worker). Vanilla-core roster only.
- **Flood cycle**: `RM_MapComponent_CanyonFlood` — a per-map clock (chime
  warning -> wait `chimeLeadTimeHours` -> a bounded flood-fill wall of
  `WaterMovingShallow` for `floodDurationHours` -> recede to `SoilRich`,
  "death, then soil"). Deliberately does NOT use vanilla's Odyssey-gated
  `Flood`/temp-terrain system (every `temporary="true"` flood terrain in
  Core is `[MayRequireOdyssey]` — MEASURED against the 1.6 assembly), so it
  runs identically with or without that DLC. One light, capped, non-fatal
  hit on a pawn caught in the wall's first cell (toggle). `RM_CanyonFlood`
  GameConditionDef is the player-visible signal only (plain vanilla
  `GameCondition` class, no override — the mechanism lives in the map
  component).
- **Soak-driven growth coupling**: `RM_Patch_Plant_GrowthRate` (Harmony
  postfix on `Plant.GrowthRate`, same pattern as the sibling RimUtinni
  PlantGrowth mod) — freshly-flooded ground carries a decaying growth-rate
  multiplier. Deliberately the light version, not
  `EXPLOSIVE_PLANT_GROWTH_1`'s full mesh-rebuild/burst engine (a separate,
  larger, unbuilt item this mod does not attempt — noted in About.xml).
- **Mod Settings** (`RM_FloodedCanyonMod`/`RM_FloodedCanyonSettings`): biome
  rarity slider (0 = never generates), "run the flood cycle in other biomes
  too" (the item's own "feature-only" ask), flood-cycle master toggle,
  period/lead-time/duration sliders, flood-damage toggle, growth-coupling
  toggle + multiplier + decay slider. Defaults = the behavior described
  above.
- **Debug test surface**: `src/RimMandrake/FloodedCanyon/Source/Debug/RM_FloodedCanyonDebugActions.cs`
  — "Arm chime + flood soon", "Start flood NOW", "Report flood state", so a
  live pass never has to wait out `floodPeriodDays` (20 days by default).

**Verified offline**: builds clean with zero errors/warnings
(`dotnet build ... RM_FloodedCanyon.csproj -c Release`, confirmed
`RimMandrake.FloodedCanyon.dll` produced); `validate_patch.py` on the mod
folder — 0 errors, 0 warnings; `deploy_custom_mods.py --mod FloodedCanyon
--apply` — deployed and VERIFIED in sync to the live Mods folder. Every
defName referenced (BiomeDef fauna/flora/diseases, `TerrainDefOf.*`,
`DamageDefOf.Blunt`, `SoundDefOf.TinyBell`) was checked against RimSage
def/C# lookups before use, not guessed.

**NOT verified — honestly incomplete against this item's own `## verify`
line**: "flood cycle + chimes provable on a quicktest map" was not done.
This session had no bridge/rimbridge MCP tool available at all (checked;
not merely deferred) and the game is recorded DOWN, so no live quicktest,
no screenshot, and no in-game confirmation that the biome worldgens, the
chime fires, the wall visibly appears, or the settings screen renders
without error. The mod is deployed and ready for that pass; the debug
actions above make it a ~1-minute check once a bridge-capable session picks
it up (rimworld-debug-testing skill: "Arm chime + flood soon" then wait
`chimeLeadTimeHours` of game time, or "Start flood NOW" for an instant
check) — do not skip it, and do not accept this note as a substitute for
actually looking.

**Not blocked on**: the campaign witness quest (`FLOOD_WITNESS_EVENT_1`)
and the full explosive-growth engine (`EXPLOSIVE_PLANT_GROWTH_1`) are
explicitly out of scope per this item's own spec — both consume this mod
as a dependency rather than living inside it.
