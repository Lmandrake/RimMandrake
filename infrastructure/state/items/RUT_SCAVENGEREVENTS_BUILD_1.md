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

## NOT yet done
No RUT_ IncidentWorker C# has been written, built or bridge-tested yet — this
is the mechanism-reference phase only. Still owed: RUT_ letter-text keys (all
8 above are `MO_*`, none are ours to ship verbatim per the license-check
instruction), IncidentDef XML wiring with our own per-event baseChance,
salvage-economy loot substitution for ShipBreak/Thanksgiving/SurvivalPod's
fixed item lists, the `MO_RTWorker` def investigation, `stroke::IncidentStroke`
and `RescueTraitor`'s closure predicate (both un-expanded above), a
proven-fires bridge test per worker, the Mlie continuation-license check, the
interim MO_ baseChance zeroing, and the final `mlie.moevents` retirement +
`animal_census.csv` MO_AbominationRace row deletion.

## verify
Not started — see "NOT yet done".
