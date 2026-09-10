## spec
Build RUT_ScavengerEvents (mandrake.rut.scavengerevents): port 8 Mo'Events
mechanics as our own IncidentWorkers (SurvivalPod, ShipBreak, PodCrash->spacer
rescue, RescueTraitor, Insects->desert fauna, Migration,
Thanksgiving->clan-tribute/moisture-tithe, Stroke; drop Nausea+Amnesia),
register-true letter text, loot from our salvage economy; per-event
baseChance settings kept. Interim: zero all MO_ baseChances via Mo'Events own
settings. Each worker needs a proven-fires bridge test. Then retire
mlie.moevents BEFORE save freeze; delete stale animal_census.csv
MO_AbominationRace row. Port behavior not bugs (author's 3 disabled events
were buggy); check Mlie continuation license before lifting C# verbatim.

## mechanism reference — decompiled 2026-09-10, not read from any wiki/memory
`MoreIncidents.dll` (mlie.moevents, `.../workshop/content/294100/2035143365/
1.6/Assemblies/MoreIncidents.dll`) ships no C# source, only the compiled
assembly — read via a scratch copy of `ilprobe` (repointed `DLL` in
`meta_core.py`/`meta.py`, tool itself untouched). Real IL, not guessed:

- **MOIncidentWorker_SurvivalPod** — unconditional. One drop pod
  (`DropPodUtility.DropThingsNear`, radius 110) holding: Hyperweave pants +
  shirt + jacket + tuque, 4x `MealSurvivalPack`, 1x `Gun_Autopistol`.
  `PositiveEvent` letter (`MO_SurvivalPods`).

- **MOIncidentWorker_ShipBreak** — unconditional. Builds a random loot list
  (excludes leather/meat ThingDefs, one item added per loop, stack size
  20-40 capped to `stackLimit`, running total capped to a `Rand.Range(150,900)`
  market-value budget, max 25 items) — `DropThingsNear` (radius 110). PLUS two
  `SpaceRefugee`-kind pawns from `RandomNonHostileFaction`: one `DamageUntilDowned`
  (alive) and one `DamageUntilDead` → its corpse — each in its OWN drop pod
  (`MakeDropPodAt`, `openDelay=180`, `leaveSlag=true`). `PositiveEvent` letter
  (`MO_CargoRain`, not "ShipBreak" — the internal keys don't match the class
  name).

- **MOIncidentWorker_PodCrashTribal** (item's "spacer rescue") — unconditional.
  One `Villager`-kind pawn from `RandomNonHostileFaction`, `DamageUntilDowned`,
  one drop pod (`MakeDropPodAt`, same params as above). Letter uses the
  instance's own `NewQuest` `LetterDef` field (quest-hook letter, not a plain
  Positive/Negative), keys `MO_TribalAid`/`MO_TribalAidDesc`.

- **MOIncidentWorker_RescueTraitor** — spawns one `MO_RTWorker` ThingDef at a
  random cell (`CellFinderLoose.RandomCellWith`, search radius 1000, predicate
  closure not further disassembled — likely a walkable/unroofed check) via
  plain `GenSpawn.Spawn`, **no letter at all** in the decompiled path. Thinnest
  of the 8 — confirm `MO_RTWorker`'s own def (creature vs. structure) before
  porting; the name implies a caged/rescuable pawn, not the thing spawned here.

- **MOIncidentWorker_Insect** (item's "desert fauna") — resolves the live
  `Insect` FactionDef, spawns `count = round(colonistCount/3, min 2)` pawns
  split across `Spelopede`/`Megaspider`, each forced into
  `MentalStateDefOf.ManhunterPermanent`, food need set to ~0 (immediate
  aggression), `exitMapAfterTick` in 90k-130k ticks, at a random map-edge entry
  cell. `ThreatBig` letter (`MO_Insects`). Genuinely hostile, not decorative.

- **MOIncidentWorker_Migration** — spawns `round((animalPoolSize*Rand(4,8))/
  Rand(2,6), capped so count ≤ animalPoolSize+8)` wild animals drawn from the
  CURRENT MAP's own `BiomeDef.AllWildAnimals`, walking from a random edge cell
  toward the map (`JobDefOf.Goto`, `exitMapOnArrival=true`), each
  `exitMapAfterTick` in 10k-12k ticks if not already gone. Only fires if a
  spawn point is found `>50` map-units from another checked point
  (`checkDistance`). `NeutralEvent` letter (`MO_Migration`). Ambient wildlife
  passage, not a threat — biome-correct animals only, which is why the item
  calls this the safest of the 8 to re-skin.

- **MOIncidentWorker_Thanksgiving** (item's "clan-tribute/moisture-tithe") —
  **conditional**: only fires if the found `RandomNonHostileFaction` is not
  hostile to the player AND the colony's `ResourceCounter.TotalHumanEdibleNutrition`
  is below `4 * FreeColonistsSpawnedCount` (i.e., the colony is genuinely low on
  food). Drop pod (radius 110) with 2x `MealSimple` + 2x `MealFine`, each
  stacked 20-40. `PositiveEvent` letter (`MO_Thanksgiving`). This is food-relief-
  when-hungry, not a calendar holiday — the re-flavor to "tribute/tithe" fits
  the actual trigger better than the original name did.

- **MOIncidentWorker_Stroke** — picks one eligible free colonist via a static
  predicate delegate (`stroke::IncidentStroke`, not further disassembled —
  likely an age/health-condition filter worth reading before porting),
  `DamageUntilDowned`, rest need maxed, current job ended, gains memory thought
  `MO_HadStroke`, scatters 10x `Filth_Blood` in a radius-3 walk near the pawn,
  forces normal game speed briefly so the player doesn't miss it while fast-
  forwarding. `NegativeEvent` letter (`MO_Stroke`) naming the pawn.

**Dropped per spec** (Nausea, Amnesia) — not decompiled, out of scope.

## progress: mechanism 1 of 8 built, deployed, awaiting a proven-fires load
`mandrake.rut.scavengerevents` scaffolded at `src/RimUtinni/ScavengerEvents/`
(About/Defs/Languages/Source, mirrors `RestrainingBolts`' csproj shape) with
`RUT_Migration` (`IncidentWorker_Migration.cs`) — the ambient-wildlife-passage
mechanic. Own defName, own `RUT_Migration`/`RUT_MigrationDesc` Keyed strings,
own `IncidentDef` (`targetTags Map_PlayerHome`, `category Misc`, `baseChance 5`,
`minRefireDays 7`, `earliestDay 1` — matches the donor's own IncidentDef
shape, read from its XML rather than guessed). The donor's animal-count
formula was an opaque integer-division artifact (poolCount canceled out of
its own ratio, then a no-op `Math.Round` on an already-integer value) — not
intentional tuning, so replaced with a plain `Rand.RangeInclusive(2, 8)` per
"port behavior not bugs."

- **Built clean**: `dotnet.exe build ... -c Release` → 0 warnings, 0 errors —
  every guessed API signature (`RCellFinder.TryFindRandomPawnEntryCell`,
  `CellFinder.RandomClosewalkCellNear`, the `Job`/`StartJob` overloads,
  `Pawn_MindState.exitMapAfterTick`, `Map.Biome`/`Center`,
  `BiomeDef.AllWildAnimals`, `LetterStack.ReceiveLetter`) compiled against the
  real `Assembly-CSharp.dll`, not just against the decompile.
- **Deployed clean**: `deploy_custom_mods.py --mod ScavengerEvents --apply` —
  4 files, nothing else touched, VERIFIED in sync.
- **Enabled for the NEXT load only**: added `mandrake.rut.scavengerevents`
  to `ModsConfig.xml` right after `mlie.moevents` (no patches/Harmony, so no
  load-order sensitivity) — backup at
  `Transient/ModsConfig_before_scavengerevents_add_2026-09-10.xml`. **Not
  restarted** — the owner was mid-session on the live campaign map when this
  was built; forcing a restart to prove-fires would have pulled the game out
  from under him. Whoever restarts next (owner or FOUNDRY) will load it.
- **NOT yet proven-fires** — needs a bridge test (quicktest map, biome with
  a non-empty `AllWildAnimals`, `IncidentDefOf`-style manual fire or
  `DebugTools` "do incident" call, verify the letter + the pawns actually
  spawn and walk off) once a load happens. This is the next concrete step for
  this item — do it before starting mechanism 2.

## still owed (mechanisms 2-8, and the close-out)
The remaining 7 workers (ShipBreak, PodCrashTribal, RescueTraitor, Insect,
Thanksgiving, Stroke — RescueTraitor and Insect both touch `SpaceRefugee`/
combat-relevant mechanics and deserve more care than Migration did). Also:
salvage-economy loot substitution for ShipBreak/Thanksgiving/SurvivalPod's
fixed item lists, the `MO_RTWorker` def investigation, `stroke::IncidentStroke`
and `RescueTraitor`'s closure predicate (both un-expanded in the mechanism
reference above), a proven-fires bridge test per worker, the Mlie
continuation-license check, the interim MO_ baseChance zeroing, and the final
`mlie.moevents` retirement + `animal_census.csv` MO_AbominationRace row
deletion.

## verify
Migration: build clean (done), deploy clean (done), proven-fires bridge test
(owed, blocked on a restart). The other 7: not started.
