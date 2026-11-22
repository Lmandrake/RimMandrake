# RIMMANDRAKE_BUILD_HUGETHINGS_CROWD_AT_REMAINS_BAR_HELD

Filed 2026-11-22 by the HugeThings ticket sweep (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`).
Sweep record: `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\HugeThings.md`.

**Version: next.** He held the crowd bar `titan_crowd_comes_for_remains` by card on 2026-11-14 ("Titan bars → Validate
5-6, hold the crowd"), so the competition for the remains is not in the first version's bars. Everything here is the
crowd that comes for the remains. It never moves the current bars. This is the obvious reading, not his word on the
split: the Conductor may move it to the current version by lifting the crowd bar's hold.

## spec

A dead titan is a time limit (his design intent, 2026-11-03). The player races to harvest before others arrive to compete
for the remains: animal scavengers and intelligent factions, violently if the player keeps them out. Code:
`src/RimMandrake/HugeThings/Source/Titanic/CorpseSite/` (`Building_TitanicCorpseSite`, `CorpseSiteVisitors`, the
harvest WorkGiver and JobDriver) and `northstar/showcase_titan_live.py` (its CROWD phase).

1. **Visitors arrive without an order.** Session 2026-11-03: the camp (`LordJob_VisitColony`, 2 pawns) sat at the east edge
   about 6000 ticks; 3 `RSW_PustuleHornet` scavengers barely moved though `canReach=true`; they reached the site only
   after a manual `order_pawn`. Evidence:
   `D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\04_TITAN_CAMPS\stage_log.txt`.
2. **Fenced-out visitors respond by faction** (his answer 5, 2026-11-11): attack, negotiate, threaten, complain, or hover
   nearby, wait and sneak in. Faction dominates. Visible warnings or acts come before consequences where the faction
   would give them. An independent design judge decides the faction mapping (delegated design), not another question to
   him. Add a visitor row to the CROWD phase of the titan showcase (today it measures scavengers and camps only).
3. **A prior claim on an older carcass is visible** (his answer 7): the faction decides the claim (the whole site, a sold
   share, or a fight), and the claim shows before the colony's first harvest order. Use a hand-staged older-carcass
   fixture. No procedural worldgen, no new world.
4. **A serious harvest is a parallel expedition** (his answer 8): several colonists cut and haul at once, the trip is
   rewarded, and plenty is left for the next day and for rivals. Replace one-worker reservations where needed; every pool
   unit is conserved through placement failures, concurrency and load. Prove a small and a large colony, an ordinary and
   a frozen control. Rot follows ordinary meat rules (that half is current, in
   `RIMMANDRAKE_FIX_HUGETHINGS_REMAINS_ROT_FIFTEEN_PERCENT_A_DAY`).
5. His two scenarios (2026-11-03): S1, a titan crosses doing its destructive damage, is force-killed, and the site and
   the competition follow; S2, a new map with an older carcass that is already being scavenged, where the locals resent
   the newcomer.

## Acceptance test

None, its design is not decided: the faction mapping of points 2 and 3 is delegated design not yet made. When the design
judge decides it, write the live rows (visitors arrive unordered within the crowd bar's window; each declared faction
response; the claim shown before the first order; parallel harvest conserves pools) and watch each one fail on today's
build first.

## Merged into this ticket (2026-11-22)

| item | class | one line |
|---|---|---|
| `RIMMANDRAKE_GIVE_HUGETHINGS_VISITORS_FACTION_RESPONSES` | KEEP, next | point 2, his answer 5 |
| `RIMMANDRAKE_SHOW_HUGETHINGS_PRIOR_CARCASS_CLAIMS` | KEEP, next | point 3, his answer 7 |
| `RIMMANDRAKE_PARALLELIZE_HUGETHINGS_CARCASS_EXPEDITIONS` | KEEP, next | point 4, his answer 8 |
| `CORPSE_VISITORS_FIX_NEVER_ARRIVE` | KEEP, next | point 1, a failure seen 2026-11-03 |
| `TITAN_CAMPS_SCAVENGERS_EVENTS_1` | STALE | he did not accept it on 2026-11-03; his answers of 2026-11-11 and the crowd hold of 2026-11-14 replaced it; the built scavenger draw and passage events stay in the code |

## His words on the merged items (word for word)

- 2026-09-09, cards #4 and #5 (quoted in `TITAN_CAMPS_SCAVENGERS_EVENTS_1`): *"The largest tier's corpse becomes a map
  landmark harvested over days — camps, spoilage, scavenger draw — never an instant meat mountain."* · *"Titans roam only
  where the rosters home them; anywhere else they arrive as scripted events/quests with warning (footfall tremors
  first). Wake damage applies to any structure including the player's — that is the point."*
- 2026-10-21 (`TITAN_CAMPS_SCAVENGERS_EVENTS_1`): "art regen everywhere we know we need".
- 2026-11-03 (`TITAN_CAMPS_SCAVENGERS_EVENTS_1`): "I'm confused how the carcass summoning scavengers and visitors relates
  to the coming of a new titan threat. And the titan looks ridiculous!"
- 2026-11-03 (same item): "So the true test might be to have the titan stomp across the map doing its dangerous
  destructive behavior just by being so large, THEN force-kill it and show it triggers the second action as a follow-on
  consequence. Alternatively, a new map might have an older carcass present ... that's actively being scavenged and the
  locals aren't too happy about the newcomer's arrival. Those are both valid scenarios to include and test."
- 2026-11-11, by card (`ANSWERS_OWNER.md` answers 5, 7, 8): "Fence -> (written in) Any of these depending on the faction.
  Faction dominates. Attack negotiate threaten complain or just hover nearby and wait and sneak."; "Prior claim ->
  Faction decides, visibly; Harvest day -> Expedition, plenty left".
- 2026-11-14, by card: "Titan bars → Validate 5-6, hold the crowd".
