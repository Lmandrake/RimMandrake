<!-- status: superseded-by: design/Jawa/bridge/INHABITED_DESIGN.md ; 2026-08-19 ; the architecture and class-list reading is replaced there; this file remains valid as the content catalogue of template places -->
# Living NPCs on a map — template catalogue

🔴 **DECIDE OWNS THIS DESIGN.** CHECK wrote it because CHECK holds the engine facts, but
every scope call — which templates ship, how many, in what order — is DECIDE's.
Queue item: `living-npc-templates-a-mod-concept-<hash>` in `queue/DECIDE.md`.

**Origin — the owner, 2026-08-19, in session:**
> *"the pawns for this tool are sentient, named and well detailed. They have homes (they go
> to sleep at night), they eat when hungry, they may even 'tend' nearby structures (dwell
> near farms if present, dwell indoors for long periods then go on walks outside), and other
> realistic living behavior. There should be many templates of this: a peasant at home, a
> farmer at a worksite, a military fortification that has patrolling soldiers, an
> inward-dwelling commander, and prisoners that are given food to survive, pets and
> associated animals, hunters that hunt, etc. Go a bit crazy with these options. It's for
> DECIDE to further expand or contract the concept. Really neat little mod concept!"*

**Feasibility spine:** `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` §5 and the
architecture section below. Every mechanic named here maps to a verified API anchor or is
flagged as needing a custom class.

**Vocabulary shorthand**
| | |
|---|---|
| **HOLD** | a lord at a point with a wander radius. Pawns already eat, sleep, socialise and work nearby |
| **RING** | a patrol circuit of waypoints — needs our `LordJob_Patrol` |
| **BEAT** | duty reassigned periodically within a district — the `VoidAwakeningWander` pattern |
| **DWELL** | a hold-point with a tight radius anchored indoors |
| **WORK** | a hold-point anchored on a worksite structure |

---

## CIVILIAN / DOMESTIC

**1. Peasant Hearth** — one family, one hut, one lifetime. *(owner's named start)* · **TRIVIAL** · DWELL r8 + twice-daily BEAT to a well
2–5 pawns: an adult pair, 0–3 children/elders. Homespun, one knife between them. Kind/Industrious/Nervous. 1 hut with a bed per pawn, fire, crop patch, well or vaporator. One dog bonded to the eldest.
*Hook: the softest thing on the map. Raiding it is a moral event. Kill the parents and the children remain — that is the point.*

**2. Terrace Row** — a street, not a house. · **EASY** · per-household DWELL r6 + one shared courtyard BEAT
8–16 pawns cross-linked by real relations (spouses, siblings, in-laws). Hut row, communal oven, low perimeter wall.
*Hook: relations mean grief propagates. Harm one household and the street turns.*

**3. The Hermit** — one pawn, forty years of habit. · **TRIVIAL** · DWELL r4 + one long weekly RING to a distant landmark
1 elderly pawn, one skill high and three disabled. Recluse / Ascetic / Psychopath. Shack, a shrine or workbench, and a grave with a name on it.
*Hook: knows something. The grave implies the story.*

## AGRICULTURAL

**4. Farmstead Worksite** — people who go to the field and come home. *(owner's named start)* · **MEDIUM** · ⭐ day/night split: WORK the field by day, DWELL the bunkhouse at night
4–8 labourers + 1 better-dressed overseer. Crop field, barn, bunkhouse, tool rack, granary with real stockpiled food. 2–4 draft animals penned.
*Hook: burn the granary and they starve. The tool should let that play out.*
📌 **This is the flagship for proving the tool** — it is the template that needs the schedule.

**5. Moisture Farm** — Ash'karr's canonical smallholding. · **EASY** · DWELL sunken through the hot hours, BEAT the vaporator ring at dawn and dusk
3–6 sun-weathered pawns in goggles and wraps. 6–10 vaporators on a ring, a sunken roofed habitat, a water tank.
*Hook: the vaporators are the wealth. Sabotage, theft, or protection-racket bait.*

**6. Fungal Cellar** — agriculture without sun, for the nightside. · **EASY** · DWELL entirely indoors r10, rarely surfaces
3–5 pale growers, Undergrounder. Dug-out chamber, fungal racks, sealed hatch.
*Hook: a food source that survives the dark side. Strategically valuable.*

## MILITARY / FORTIFICATION

**7. Waystation Fort** — walls and men who walk them. *(owner's named start)* · **MEDIUM** · 2–4 on RING around the perimeter, the rest HOLD in the courtyard, rotating
6–12 uniformed soldiers with matched weapons + 1 sergeant. Walls, gate, guard towers, barracks, mess, armoury with real weapons in it.
*Hook: the patrol is the puzzle — time it, distract it, or fight it. Visibly a garrison, not a mob.*

**8. Checkpoint** — a road, a barrier, a bribe. · **TRIVIAL** · HOLD r5 on the barrier + one shelter BEAT node
2–4 pawns, one in charge. Barrier, shelter, brazier, a hidden strongbox of tolls.
*Hook: the smallest possible authority encounter. Excellent filler — place a dozen.*

**9. Watchtower Pair** — two soldiers and a long view. · **TRIVIAL** · HOLD r3, the upper pawn effectively static
2 pawns, one sniper-equipped. Tower, stairs, signal fire.
*Hook: lights the signal when attacked — implies a response elsewhere on the map.*

**10. Siege Camp** — an army that has stopped moving. · **MEDIUM** · squad HOLD clusters + 1 sentry RING; officers DWELL the command tent
12–25 mixed soldiers and support, morale-worn. Tent rows, mortar emplacements, supply dump, latrine, picket line. Pack animals tethered.
*Hook: they are besieging something — the map implies a neighbour. Rich loot dump.*

**11. Imperial Garrison** — the Empire, doing what it does. · **MEDIUM** · rigid RING on fixed timing, DWELL barracks, officer indoors
10–20 identical troopers + 1 officer + 2 droids. Prefab grey blocks, floodlights, landing pad, comms mast, detention block.
*Hook: nests with Captivity. The most satisfying thing on the map to dismantle.*

## COMMAND / AUTHORITY

**12. The Inward Commander** — power that does not come outside. *(owner's named start)* · **EASY** · commander DWELL r3 indoors with a rare BEAT; bodyguards HOLD the door
1 commander (high Social/Shooting, real backstory, unique name) + 2 bodyguards. The best-built room on the map: desk, map table, private bed, safe.
*Hook: the decapitation target. Should be named and knowable BEFORE the player meets him.*

**13. Hutt Parlour** — a fat authority and its ecosystem. · **MEDIUM** · boss essentially static r2; retinue BEAT the chamber
1 Hutt-analogue + 4–8 sycophants, guards and dancers. Audience hall, vault, adjacent cells, kitchen. One exotic captive beast penned.
*Hook: negotiation OR massacre, and the vault rewards either.*

**14. Council Circle** — authority without a single head. · **EASY** · HOLD tightly on the circle by day, DWELL separate huts at night
5–7 elders, no two alike, plus attendants. Seat circle, speaking stone, archive hut.
*Hook: kill one and the others still function — deliberately un-decapitatable.*

## CAPTIVITY

**15. Fed Prisoners** — people kept alive on purpose. *(owner's named start)* · **MEDIUM** · prisoners DWELL r2 in cells; guards RING the block including a feeding node
3–8 prisoners (`SetGuestStatus` Prisoner, malnutrition hediffs, no gear) + 2 guards. Cell block with beds, food store, guard post.
*Hook: rescue is a real objective — recruit them, or find they are worse than their captors.*
📌 The feeding loop is the interesting part and the part that needs proving.

**16. Labour Gang** — captivity that works. · **MEDIUM** · prisoners WORK the pit by day, DWELL a locked compound at night; overseers BEAT
6–12 prisoners + 3–4 overseers. Quarry or salvage pit, compound, tool store, whipping post.
*Hook: liberate mid-shift and you get a riot, not a rescue.*

**17. Slave Market Pen** — merchandise. · **MEDIUM** · prisoners HOLD in pens; buyers BEAT the market floor
4–10 penned + 2 auctioneers + 3–6 **neutral** browsing buyers. Pens, auction block, strongbox, awnings.
*Hook: buy, steal, or burn. Neutral buyers make violence costly, which is better design.*

## ANIMALS / PASTORAL

**18. Herder Camp** — a family and their living wealth. · **EASY** · adults DWELL at the tent; a herder-child BEATs around the herd
3–5 pawns. Tents, pen, water trough. 10–20 herd animals, 2 bonded.
*Hook: the herd is both the wealth and the vulnerability. Predators. Rustling.*

**19. Beast Kennels** — someone breeds the dangerous things. · **EASY** · WORK anchored on the pens
3–4 handlers, high Animals, visible scars and missing fingers. Reinforced pens, feed store, med bench. 4–8 dangerous animals bonded to handlers.
*Hook: release the pens as a tactic. The handlers know it too.*

## HUNTING / FORAGING

**20. Hunter Band** — they leave and they return. *(owner's named start)* · **MEDIUM** · ⭐ long RING far across the map and back; DWELL camp between circuits
4–6 hunters, ranged, high Shooting. Camp, drying racks, cache. 2 hunting dogs accompanying.
*Hook: you meet them AWAY FROM HOME, which no other template does.*
⚠️ The widest-ranging template — needs the squad-stall escape on each leg.

**21. Scav Line** — pickers working a debris field. · **EASY** · WORK across scattered wreck cells, BEAT between them
5–10 low-tier pawns in mismatched gear. Wreck scatter, sledges, sorting yard.
*Hook: they know where the good wreck is. Ash'karr's native profession.*

## INDUSTRIAL / SCAVENGING — the Jawa register

**22. Sandcrawler Crew** — a mobile home that has stopped for now. · **HARD** · crew BEAT the hull r20; interior pawns DWELL; 2 lookouts on RING
8–15 robed, hooded Jawas + 1 chief with the best salvage. The crawler prefab dominates the map: ramps, cargo bay, droid racks, workshop. 1–2 pack beasts.
*Hook: ⭐ **the flagship set-piece.** Trade partner, robbery target, or rival clan — everything the campaign is about.*

**23. Salvage Yard** — sorted wreckage and the people who sort it. · **MEDIUM** · workers WORK the sorting bays; proprietor DWELLs the office
4–8 workers + 1 proprietor. Aisles of stacked hulls, crane, office, strongroom, guard droid. One chained, aggressive junkyard beast.
*Hook: buy parts or take them. The chained beast is the deterrent.*

**24. Droid Enclave Node** — machines living unsupervised. · **MEDIUM** · rigid, perfectly periodic RING and WORK loops
6–12 droid kinds. **No sleep, no food.** Charging racks, fabrication bay, and deliberately **no domestic structures at all**.
*Hook: the ABSENCE of domesticity is the storytelling. Free Droid Enclaves anchor.*

## RELIGIOUS / RITUAL

**25. Shrine Keepers** — devotion as a daily timetable. · **EASY** · DWELL cells, BEAT converging on the shrine at intervals — **synchronised**, which is what reads as ritual
3–6 pawns sharing one ideoligion, ritual apparel. Shrine, cells, offering store, bell.
*Hook: they will not fight well, but harming them carries ideological cost.*

**26. Pilgrim Column** — faith in transit. · **MEDIUM** · slow RING across map waypoints — they are passing through
8–20 mixed ages, poor gear, 2 guards. No structures; they stamp a night camp.
*Hook: transient. Meet them twice and they have moved.*

## DERELICT / SURVIVORS

**27. Holdouts** — a dead place with three living people in it. · **EASY** · DWELL r5 in the sealed room, rare desperate BEAT for supplies
2–4 pawns, injured, starving, hoarded gear. A high-decay ruin, one intact lit room, barricades, graves.
*Hook: the best rescue/recruit hook on the list. The `decay` parameter does the work.*

**28. Crash Site Survivors** — days old, not years. · **EASY** · HOLD tight r8 around the wreck
3–8 mixed civilian and crew, fresh injuries. Wreck prefab, tarps, signal fire, cargo scatter.
*Hook: time-limited feeling. Help, rob, or ignore.*

## TRADE / CARAVANSERAI

**29. Waterhold Caravanserai** — a neutral place on a hostile world. · **MEDIUM** · keeper DWELLs, guards RING the wall, traders BEAT the courtyard
10–20 pawns across 2–4 factions, **all neutral here**, + 1 keeper + 3 guards. Walls, well, stalls, stables, guest rooms. 6–12 pack animals tethered.
*Hook: ⭐ the social hub. Violence here is a faction-wide scandal.*

## CRIMINAL / PIRATE

**30. Bandit Roost** — predators with a lair. · **EASY** · 1–2 RING lookouts, the rest HOLD/DWELL the lair
6–12 pawns, mismatched good weapons, cruel traits. Defensible outcrop, badly stored loot, cages, trophy post.
*Hook: obvious violence target with real loot. Nests with Captivity.*

## MEDICAL / REFUGEE

**31. Fever Camp** — a place trying not to die. · **MEDIUM** · the sick DWELL tight; medics BEAT the rows
10–25 refugees carrying disease hediffs + 1–2 exhausted medics. Tents, quarantine rope, med tent, and grave rows that grow.
*Hook: medicine as currency. Aid or avoid — both have consequences.*

## RESEARCH / OUTPOST

**32. Helix Field Station** — scholars where they should not be. · **MEDIUM** · researchers DWELL the lab; guards RING; a daily sampling BEAT outward
4–6 researchers (high Intellect, weak combat) + 3 hired guards. Lab, generator, sample store, comms mast.
*Hook: Ascendant Helix anchor — they study the horror wastes. Knowledge as loot.*

## GENUINELY WEIRD

**33. The Feast That Does Not End** — a banquet frozen in ritual repetition. · **EASY** · synchronised HOLD at table seats; a BEAT that always returns to the same seat
8–12 pawns in fine apparel, blank backstories, one ideoligion, unnaturally healthy. A hall, a long table — and **no beds, no kitchen, no stores, no waste**.
*Hook: nothing explains it. The player supplies the horror. Weirdness is cheap — it is the ABSENCES that sell it.*

**34. The Mourning Line** — a procession that has walked the same route for years. · **MEDIUM** · permanent slow RING with **no home node** — they never stop
6–10 pawns carrying a bier, grieving thoughts, identical dark apparel. No structures; waypoint cairns.
*Hook: they will not talk. Following them leads somewhere.*
⚠️ "No home node" is one of the two mechanics not in the verified vocabulary.

**35. The Understudy Village** — a settlement of people who are all the same person. · **EASY** · ordinary domestic DWELL/BEAT, deliberately mundane
8–14 pawns sharing appearance and genes, named Kel-1 … Kel-14. A standard hamlet.
*Hook: cloning, ideology, or something worse. The mundane behaviour makes it worse.*

**36. The Tended Ruin** — caretakers maintaining a building nobody uses. · **EASY** · WORK anchored on the empty structure; they never enter the inner room
3–5 keepers in ritual apparel, DWELL adjacent hovels. An immaculate swept hall with a sealed inner room, hovels, tool store.
*Hook: ⭐ the inner room. The whole template is a locked door with a reason.*

---

## COMPOSABILITY

**Templates should be CONTAINERS, not leaves.** An *Imperial Garrison* (11) contains an
*Inward Commander* (12), a *Fed Prisoners* block (15) and a *Beast Kennel* (19). A
*Caravanserai* (29) contains three *Terrace Rows* (2) and a *Slave Pen* (17).
Implementation: the parent stamps its structures and **reserves sub-rects**; children
resolve into those rects with `parentFaction` inherited unless overridden.

**Every template takes the same parameters:**

| param | meaning |
|---|---|
| `faction` | who they belong to; `null` = unaffiliated survivors |
| `size` | scales pawn count and footprint (tiny → huge) |
| `techTier` | neolithic → industrial → spacer; drives apparel, weapons, structures |
| `wealth` | poor / modest / rich; drives gear quality and loot |
| `hostility` | hostile / neutral / friendly / **conditional** |
| `decay` | 0–1 ruin level; damages structures, ages pawns, adds graves and hediffs |
| `population` | override the size-derived count |
| `nightBehaviour` | sleep / continue / shift-rotate — droids and prisoners differ |
| `origin` | anchor cell or rect |
| `seed` | reproducibility — the same seed must give the same scene |

### Three calls worth making early

1. ⭐ **`decay` is the highest-value single parameter.** It turns any template into its own
   ruined variant for free. Prioritise it over new templates.
2. ⭐ **`hostility: conditional`** (neutral until provoked) is what makes these read as
   *inhabited* rather than *placed*. Without it every template is a combat encounter.
3. ⭐ **Named pawns should be the EXCEPTION.** One named, detailed pawn per template — the
   commander, the proprietor, the eldest — and the rest generated. Naming everyone costs a
   lot and flattens the emphasis.

### Recommended proving order
**1 Peasant Hearth** → **4 Farmstead Worksite** (proves day/night) → **7 Waystation Fort**
(proves the ring) → **15 Fed Prisoners** (proves guest status + the feeding loop) →
**22 Sandcrawler Crew** (the set-piece).

⚠️ **Two mechanics in this catalogue are NOT in the verified vocabulary** and DECIDE should
know before cutting: the **day/night behaviour switch** (4) and the **permanent no-home
ring** (34). Both likely need a custom `LordJob` variant.

---

# ARCHITECTURE — what the engine will and will not do

Read from 1.6 source. **Three of the four requested behaviours are nearly free. One —
"tends nearby structures" as FARMING — is hard-blocked and needs Harmony.**

## Feasibility, per behaviour

| behaviour | verdict |
|---|---|
| Named, detailed, persistent pawns | ✅ **SHIPPED** |
| Confined to a home area | ✅ **SHIPPED** — `ThinkNode_ForbidOutsideFlagRadius` |
| Eats when hungry | ✅ **SHIPPED** ⚠️ *will raid player food* |
| Sleeps when tired, in an owned bed | ✅ **SHIPPED** — but the bed's faction must match the pawn's |
| Sleeps **at night** specifically | 🔵 **SMALL CUSTOM** — one JobGiver, ~30 lines |
| Wanders / goes on walks | ✅ **SHIPPED** — `JobGiver_WanderNearDutyLocation` |
| Day/night duty schedule | 🔵 **SMALL CUSTOM** — one LordToil tick, no state graph |
| Repairs & builds nearby structures | ✅ **SHIPPED** |
| Hauls / cleans / cooks | 🔵 **SMALL CUSTOM** — Harmony prefix |
| **Farms (sow/harvest)** | 🔴 **LARGE CUSTOM** — three stacked blocks |
| Survives save/load | ✅ **SHIPPED** — override `LordJob.ExposeData` |

## 🔴 Why farming is blocked — three independent walls

1. **The WorkGiver whitelist.** `JobGiver_Work.PawnCanUseWorkGiver` refuses unless
   `giver.def.nonColonistsCanDo`. Exactly **7 shipped WorkGiverDefs** carry it, and **all
   seven are construction or repair** — `ConstructFinishFrames`,
   `ConstructDeliverResourcesToFrames/Blueprints`, `Replant`, `Repair`,
   `DeliverResourcesToFrames/Blueprints`. **No growing, no hauling, no cleaning, no cooking.**
2. **A lord-specific veto.** `WorkGiver_GrowerHarvest.ShouldSkip` opens with
   `if (pawn.GetLord() != null) return true;` — **any lorded pawn skips harvest, even a
   colonist.** The farmer concept collides with the Lord system itself.
3. **Player-only data.** `WorkGiver_Grower` sources its cells from `zoneManager.AllZones`
   and `allBuildingsColonist`. An NPC "farm" that is not a player growing zone yields **no
   work cells at all**.

⇒ **Recommendation: reframe "tends the farm" as "dwells near it and repairs it", which is
FREE.** Real farming roughly doubles the surface and pulls in Harmony — scope it separately.

## 🔑 The four facts that shape the build

* **`pawn.workSettings` exists but is uninitialised on NPCs.** `PawnGenerator` calls
  `EnableAndInitialize()` only when `request.Faction.IsPlayer`. `EverWork => priorities != null`,
  so `JobGiver_Work` returns priority 0 and the sorter skips it — **which is also why a null
  `workSettings` never NREs.** The shipped precedent is `LordToil_Siege`, which calls
  `EnableAndInitialize()` then `SetPriority(Construction, 1)` and disables everything else.
* **Bed ownership works for non-colonists**, and the gate is not "is player". It is
  `RestUtility.IsValidBedFor`: `bed.Faction == pawn.Faction`. ⇒ **set the bed's faction to
  the NPC's own faction and call `ClaimBedIfNonMedical` at spawn.** A player-faction bed
  AND a null-faction bed both fail. `BedOwnerType.Colonist` means "not prisoner/slave", not
  "player".
* **"At night" does not come free.** `Pawn_TimetableTracker.CurrentAssignment` returns
  `Anything` unless `pawn.IsColonist`, and `pawn.timetable` is **null on NPCs** anyway.
  Under `Anything`, `JobGiver_GetRest` fires only when `rest.CurLevel < 0.3` — so pawns
  sleep **when tired**, drifting out of phase with the day.
* ⚠️ **Non-player pawns ignore player forbid flags entirely.** `Thing.IsForbidden(faction)`
  returns false for any non-player faction. **They will walk into a player stockpile and eat
  the colony's lavish meals.** That is a gameplay problem, not a bug. Mitigate by giving the
  NPC faction its own food inside the radius, or accept it. 🔑 The confinement radius is the
  real leash and the same mechanism — `maxDistToSquadFlag` makes distant cells forbidden,
  which prunes food, bed and work search at once.

## 🔴 DO NOT build a StateGraph with transitions

`Lord.ExposeData_StateGraph` serialises only `curLordToilIdx` plus toil and trigger
dictionaries keyed by **POSITIONAL INDEX**, then re-runs `lordJob.CreateGraph()` on load.
**Any later change to toil ordering silently corrupts existing saves.**

⇒ **Use one toil that reassigns duty on a tick** — the `LordToil_VoidAwakeningWander`
pattern. Zero transitions, zero index fragility, and the schedule becomes ordinary C#.

⚠️ **This revises the `LordJob_Patrol` ring proposed in `BRIDGE_CAPABILITY_ROSTER.md` §5.**
The ring is a transition graph and therefore carries this save-fragility. It is still the
right shape for a *pure* patrol whose waypoint count never changes after a save exists —
but for anything that might be re-tuned, prefer a single toil that walks an index through a
waypoint list it owns and scribes. **DECIDE should rule on which.**

## Minimal class list — everything except farming

| # | class | kind | role |
|---|---|---|---|
| 1 | `LordJob_Settler` | custom `LordJob` | one toil; `ExposeData` scribes home cell, worksite cell, radii |
| 2 | `LordToil_SettlerDay` | custom `LordToil` | `LordToilTick()` reads `GenLocalDate.HourOfDay(Map)` and reassigns `PawnDuty` per pawn |
| 3 | `JobGiver_RestAtHomeAtNight` | custom `JobGiver` | night → `LayDown` on `pawn.ownership.OwnedBed` |
| 4 | `NPC_Dwell` | **DutyDef XML** | rest-at-night → `ForbidOutsideFlagRadius` → `SatisfyBasicNeedsAndWork` → `WanderNearDutyLocation` |
| 5 | `NPC_Tend` | **DutyDef XML** | clone of shipped `Build`: `JobGiver_Work` in a flag radius |
| 6 | `SettlerSetupUtility` | static helper | `EnableAndInitialize()` + priorities; set bed faction; claim bed |

**Total: 1 LordJob, 1 LordToil, 1 JobGiver, 2 DutyDef XML, 1 utility.** No Harmony.

## Persistence and failure modes

* ✅ Lords survive save/load. `LordManager` holds them `LookMode.Deep`; `Lord.ExposeData`
  scribes faction, `ownedPawns` by reference, and the LordJob deep. Override
  `LordJob.ExposeData` for our fields. **Bed ownership persists independently.**
* ✅ **Mental states do NOT strip duty** — the mental-state node simply outranks the duty
  subtree, and recovery is automatic.
* ✅ **Drafting** breaks only `LordJob_VoluntarilyJoinable` lords. Ours is unaffected, and a
  non-player pawn cannot be drafted anyway.
* ⚠️ **A faction turning hostile does not dissolve the lord** — there is no
  `Notify_FactionRelationChanged`. But the pawns become valid targets and the `Defend`
  duty's `JobGiver_AIDefendPoint` makes them fight. For non-combatants, use a custom duty
  without that node.
* ⚠️ **`Lord.ShouldExist` returns false when `ownedPawns.Count <= 0`.** Base
  `LordJob.ShouldRemovePawn` returns true for *every* condition — **override it** or a
  downed or mentally-broken pawn is dropped from the lord and never comes back.
* 📌 `ThinkNode_ConditionalLordDutyActive` **does not exist** in 1.6. The real gate is
  `ThinkNode_ConditionalHasLordDuty` → `pawn.GetLord().CurLordToil.AssignsDuties`, which
  checks the **toil**, not the duty field.

**UNCERTAIN, and worth one quicktest each:** whether `StateGraph` cycles behave in game;
whether a bed spawned by the bridge keeps `Faction == NPC faction` through the spawn path;
whether `HaulToStorageJob` resolves a destination for a non-player pawn even with the
whitelist patched.
