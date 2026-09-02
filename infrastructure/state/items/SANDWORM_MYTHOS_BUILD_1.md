# SANDWORM_MYTHOS_BUILD_1 — the Long Hunger, a VAST-tier dune leviathan

Owner, verbatim (2026-09-02): *"Keep the giant Krayt dragon just as it is, but
create a NEW massive dune-style sandworm with its own mythos. Plenty of room
for both. But Krayt dragons deserve their own treatment. Feel free to borrow
from the giant worm mod to build another version for the Krayt."*

Research already done: `research/Jawa/sandworm_krayt_survey_2026-09-02.md`
(giant-worm mod survey, Krayt provenance, borrow-vs-original analysis). Krayt
Dragon (`mlie.starwarsanimalcollection`) is **untouched** by this item — it
stays exactly as it is, per the ruling.

## spec

**Identity**: the Long Hunger — Deep Desert tribal lore for a colossal entity
that lives beneath the `Dunes`-mutated `ExtremeDesert` tiles (1,083 tiles,
5.0% of the planet — `ASHKARR_WORLD_DEFINITION.md` §13.1). Those tiles are
already known to be stripped bare (no ruins, no junk, no plants, no geysers —
the `Dunes` TileMutator's own effect). This item's in-fiction explanation:
nothing survives on that ground long enough to leave anything behind, because
the Long Hunger has already taken it. That also grounds the reward loop in
the campaign's central scavenging economy — its loot IS the wreckage of
centuries of swallowed salvage, not generic treasure.

**Architecture, ruled precedent**: `design/Jawa/worldbuilding/setting_physics.md`
Part 5 already names `chezhou.creature.sandworm` (LEVIATHANS:SANDWORM,
already installed) as the working reference for every VAST-tier entity this
campaign authors — **a world object with weather and music attached,
encountered through a quest, not a wildlife-table spawn.** `RUT_LongHunger`
has no `<race>` element, matching that template.

**Design borrowed, not code**: per the survey's verdict, the reference mod's
own C# (`ChezhouLib`) is Workshop-only/closed and was NOT read or copied.
What's genuinely portable and was actually used: the architecture shape
(quest-gated encounter, a summoning device, weather/atmosphere, a big single
eruption + a defined lifetime before submerging). All C# in this item
(`src/RimUtinni/LongHunger/Source/`) is original, written from RimSage-cited
decompiled vanilla APIs (`GenExplosion.DoExplosion`, `RCellFinder`,
`ThingSetMakerDefOf.Reward_ItemsStandard`), following the
`rimworld-quests` skill's own "start in XML, always" guidance — the quest
itself (`RUT_LongHungerContract`) mirrors `src/RimMandrake/StrandedQuest`'s
proven vanilla-node shape almost exactly, with one addition
(`QuestNode_CreateIncidents`, cited against real decompiled source, not
guessed) to fire the encounter.

## v1 deliberate simplifications — named, not hidden

1. **Home-map encounter, not a distant travel/site quest.** The reference mod
   marks a "deep-sand echo zone" on the WORLD map and the player caravans to
   it. This item's v1 fires the encounter on the player's OWN map instead —
   a real, deliberate reduction in scope to avoid the site-generation risk
   surface on a pass with no bridge available to live-test against. A
   travel/site version is a named v2, not abandoned.
2. **Single-cell entity, not a separate multi-tile hit-proxy body.** The
   reference's `SandWorm_HitProxy` (a 5×5 damageable surface separate from
   the 1×1 visual `SandWorm_Thing`) needs `ChezhouLib`'s closed C# and real
   live tuning to get right. `RUT_LongHunger` is one `(1,1)` Building with a
   large `drawSize` and a genuine area-damage eruption + tremor pulses
   (`LongHungerThing.cs`) — visually and mechanically "vast," but not true
   multi-tile geometry. Named v2 improvement.
3. **No accumulated-vibration tracking.** The reference's Sandhammer must run
   undisturbed for a real in-game 10 hours before the worm answers. This
   item's `RUT_Groundcaller` is flavor — a normal buildable prop, not
   mechanically wired to the quest's timer via a custom activation signal.
   The encounter fires on a fixed delay from quest ACCEPT (8–14 in-game
   hours), regardless of whether the player ever builds one. A real
   build-then-activate interactive loop (a `ThingComp` gizmo sending a quest
   signal via `QuestUtility.SendQuestTargetSignals`) is a named v2, not
   built here — avoided this pass specifically because getting the
   `questTags`/signal-linkage wiring wrong is a silent, hard-to-catch quest
   bug class this skill's own reference material warns about repeatedly.
4. **Placeholder art on both new ThingDefs.** `RUT_Groundcaller` reuses
   vanilla's mini-turret gun texture (`Things/Building/Security/TurretMini_Top`,
   confirmed real by reading `Buildings_Security_Turrets.xml` directly — a
   first guess at `Turret_Mortar`'s own path turned out to be wrong, since
   that def inherits its texture rather than declaring one literally, and
   was caught by `validate_patch.py` before shipping). `RUT_LongHunger`
   reuses Anomaly's PitGate texture (`Things/Building/PitGate/PitGate`,
   confirmed real the same way). Both are stated placeholders, not final art
   — a real sprite pass (`generating-rimworld-sprites` skill) is owed.
5. **`RUT_DuneHaze` (the atmosphere WeatherDef) is authored but NOT wired**
   to the encounter — a v2 hookup via a `GameConditionDef`, matching
   `WeatherSuite`'s own precedent, not rushed into this pass.

## verify

- `dotnet build` clean — **done**: 0 warnings, 0 errors
  (`"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build ...LongHunger.csproj -c Release`).
- `python3 skills/rimworld-quests/scripts/validate_quest.py` on
  `Quest_LongHunger.xml` — **done**: 0 errors, 0 warnings.
- `validate_patch.py` against the live 592-mod set — **done**: 0 errors, 3
  advisory texPath warnings (the known asset-bundle blind spot, both paths
  independently confirmed real by reading the source XML directly, not
  assumed).
- Deployed (`deploy_custom_mods.py --mod LongHunger --apply`) — **done**,
  file-copy only, NOT enabled in `ModsConfig.xml`, no restart triggered.
- **Not done, owed to the next bridge session**: enable
  `mandrake.rut.longhunger` (requires Anomaly active — confirm), cold-load
  clean, then live-verify: the quest actually offers/fires (dev mode ->
  Quests -> Generate quest, per the skill's own "never gate a verification
  on the storyteller" rule), `RUT_LongHungerSurfaces` incident fires and
  spawns `RUT_LongHunger`, the eruption + pulse damage register on a nearby
  pawn, it submerges and drops loot on schedule (~2500 ticks), the quest's
  own timer completes and pays the contract fee.

## criteria

A correct v1: the Long Hunger is a genuine VAST-tier world entity (no
`<race>`), quest-gated per the ruled template, with a real (if simplified)
eruption/tremor/submerge mechanism and a scavenging-economy-appropriate loot
payoff — offline-authored and validated clean. Krayt Dragon confirmed
untouched. Live-fired and observed in a real game is the next pass's job, not
this one's.
