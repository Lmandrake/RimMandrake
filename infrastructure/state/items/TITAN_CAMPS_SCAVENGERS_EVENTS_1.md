# TITAN_CAMPS_SCAVENGERS_EVENTS_1 — Huge Things titans: corpse camps, scavenger draw, footfall-warned titan events

Ruled by card, owner 2026-09-09 (`infrastructure/state/items/closed/TITANIC_CREATURES_MOD_1.md`):
#4 *"The largest tier's corpse becomes a map landmark harvested over days — camps, spoilage, scavenger draw — never an
instant meat mountain."* · #5 *"Titans roam only where the rosters home them; anywhere else they arrive as scripted
events/quests with warning (footfall tremors first). Wake damage applies to any structure including the player's — that is
the point."* Spoilage and the multi-session harvest were built; camps, scavengers and the event were not (found by the GPT
full review, `Transient/hugethingsbounds2026-10-07/`).

## spec (as built, FOUNDRY 2026-10-21; engine-only, no creature or faction named)

- **Scavenger draw** (`CorpseSiteVisitors.DrawScavengers`, in `Building_TitanicCorpseSite`'s daily step): a daily chance
  (default 35%) brings 1..max (default 3) wild predators the map's own biomes home, adult tier None, season-survivable,
  from a map edge to the site. Count never exceeds what the meat left can feed for a day (`RM_TitanicKernel.ScavengerCount`).
- **Camps** (`CorpseSiteVisitors.MakeCamp`): a daily chance (default 10%) brings 2-4 people of a non-hostile humanlike
  faction; vanilla `LordJob_VisitColony` with the chill spot beside the site for `corpseSiteCampHours` (default 36), then
  they leave. Letter on arrival.
- **Eating**: each scavenger/camper within 10 cells of the site takes `corpseSiteVisitorMeatPerDay` (default 20) meat a day
  (`RM_TitanicKernel.VisitorTake`). Inspect line shows who is at the remains.
- **Titan passage** (`IncidentDef RM_TitanPassage`, `IncidentWorker_TitanPassage`, `MapComponent_TitanPassages`): picks a
  race of adult tier T2/T3 that some biome homes and none of this map's biomes do (`RM_TitanicKernel.TitanEventEligible`,
  also the one-T3-per-map spacing law); "Footfall tremors" letter naming the edge; camera shake every 300 ticks rising
  0.3 -> 1.5 and a message every 2 h through `titanEventWarningHours` (default 6); then the titan spawns and walks edge to
  edge on a vanilla `LordJob_ExitMapNear` (the herd-migration shape). Re-checked at arrival; if no longer eligible the
  tremors "fade".
- Mod Settings: scavengers / camps toggles + chance, max, meat/day, camp hours under the corpse-site group; a new "Titan
  events" group with its toggle and warning hours. All numbers **PROVISIONAL** (FOUNDRY first guess, to be tuned live).

## criteria

- A1 L0: `validation.py` STATIC PASS with the new needles; titanic fuzz family `visitors` 0 failures; HugeThings selftests green.
- A2 L2: on a map with a T3 corpse site, scavenger chance 100%, `DebugDailyStep` -> ScavengerCount > 0 (predators of the map's biome, none tiered); after they reach the site the next step lowers MeatRemaining by VisitorsEatenTotal's increase.
- A3 L2: camp chance 100%, `DebugDailyStep` -> CamperCount > 0 under a non-hostile faction's VisitColony lord; they leave after corpseSiteCampHours.
- A4 L2: firing RM_TitanPassage on a map whose biome homes no titan -> HasPending true and a tremor letter; DebugArriveNow -> LastArrived spawned, tier >= T2, race not homed in the map's biome, with an ExitMapNear lord; with a T3 already on the map a T3 is never chosen.
- A5 L2: each new toggle off removes exactly its effect (no draw / no camp / CanFireNow false).
- A6 L4: the owner sees a passage and a scavenged site in play and judges the feel and the numbers.
