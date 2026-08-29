# EMPIRE_PURSUIT_SURVEY_SHADOW_1 — poorly-surveyed biomes slow the Empire's pursuit

Owner, 2026-08-28 (verbatim, on the pursuit cadence): "Matching the initial fast
timeline... it takes them that long to 'relocate' the ship on the dayside. But any
area that's poorly surveyed (e.g. forsaken crags, or possibly some others, and even
in distant v2 maybe on the ocean floor for a sealed ship) it's more like 20-30 days"

## spec
Ruthless Faction Pursuit has one global `raidDelayHours`. Fork the bundled source
(MIT-style, credit required — workshop 3621784437 ships Source/) to add a
biome-keyed delay multiplier on `ScenPart_RuthlessPursuingMechanoids`: settled-map
biome in a "survey shadow" list ⇒ raidDelay × ~4 (156h → ~600±150h ≈ 20-30 days).
The list is owner data (starts with the Forsaken Crags biome def; he says "possibly
some others"), kept as a def/field he can read, per owner-rules-must-be-data.
v2 note: ocean-floor sealed-ship idea rides the same mechanism.

## verify
Scratch game, part active with tiny delays: normal biome raids on the fast clock;
a survey-shadow biome map gets the multiplied clock (read the part's scribed
mapRaidTimers in a save).

## criteria
- [x] Global cadence 156±36h ships in the campaign scenario part.
- [x] Survey-shadow biomes get ~4x delay, from an owner-editable list.
- [x] Mod author credited per license.

## progress 2026-08-29
Built, offline half only (bridge live-check owed separately, see below).

Forked `ScenPart_RuthlessPursuingMechanoids` (namespace/class/ScenPartDef defName kept
identical to upstream, on purpose, for save/scenario compatibility) into
`D:\Luke\dev\Rimworld\src\Jawa\EmpirePursuit\`. Dropped Omni Pursuit entirely — not our
fiction, matches the design note. Ported Utilities.cs/Settings.cs/HarmonyPatches.cs
unchanged (renamed the Harmony instance id to this fork's own packageId).

- **Survey shadow**: new `ScenPartDef_RuthlessPursuit : ScenPartDef` carries
  `surveyShadowBiomes` (List<BiomeDef>) and `surveyShadowMultiplier` (default 4) as
  plain XML data on the def — `Defs/Scenarios/ScenParts_EmpirePursuit.xml`, seeded with
  `AB_RockyCrags` (Alpha Biomes' "Forsaken Crags", confirmed by defName lookup in the
  mod's own XML). `StartTimers()` now multiplies both the raid and warning delay by
  this factor when the settled map's `Biome` is on the list — applies to both the
  first-period and per-map branches. Owner can add more biomes without touching code.
- **Cadence defaults**: changed the *Def consts from upstream's 636h/204h (18-35 day,
  vanilla-derived) to the owner's ruled 156h/36h (5-8 days) and warning 48h/12h, so a
  freshly-added part already ships the ruled cadence without per-field construction.
- **Credit**: About.xml credits Matathias/GPLv3 per the original's own request, LICENSE.txt
  (GPLv3) copied in, source-header provenance comments on every ported/modified file.
  `incompatibleWith: matathias.ruthlessmechanoids` set — same ScenPartDef defName and
  class, so the two must never both be enabled.

Builds clean: `dotnet.exe build EmpirePursuit.csproj -c Release` → 0 errors, 0 warnings,
`Assemblies/RuthlessPursuingMechanoids.dll`.

**Not done here, on purpose**: this item's own `verify` (scratch game, tiny delays,
confirm the multiplied clock in a save) needs the bridge — the game is mid cold-load
this session. Not deployed to the live Mods folder either; that and the runtime
scenario-part insert both belong to EMPIRE_PURSUIT_SCENPART_INSTALL_1, which is already
blocked on game-up + bridge for exactly this reason. Leaving this item OPEN rather than
closing it, so the live check has somewhere to land.
