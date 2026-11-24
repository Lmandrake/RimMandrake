# The 15 leaves that commit 4e53cf96e5 reworded, for the Conductor's call

For item `RIMMANDRAKE_RULE_FIFTEEN_REWORDED_BARS_SOME_LOOSENED_UNLOGGED`. Written by the run of
`RIMMANDRAKE_ENACT_SEASON_PLAY_IS_PLAYTEST_NOT_ACCEPTANCE_NOR_HIS_WALK`, 2026-11-24. This run logged nothing and reverted nothing.

- The old and new texts are read from git [measured]. "Looser" and "settled" are this run's reading of those texts [guess ~80%].
- The bar's sentence (`experience`) changed in 4 of the 15: `prepared_day`, `attack_brings_raids`, `walk_tribes_season`, `ordinary_work` [measured].
- The new text is the text of `4e53cf96e5`. After it, this run only took the long play on his walk out of it.
- The same commit made the door lint refuse the walk leaf of all six trees: the scenario lacks the words for the repeat or the
  second order. At its parent no tree had those faults [measured, `concept_tree.py lint`].

## Summary

| mod | leaf | sentence changed | looser? | does the ruling of 2026-11-24 settle it? |
|---|---|---|---|---|
| Cauldron | `prepared_day` | yes | yes: the bar's sentence lost the forty-colonist settlement, food, and the wild vent competition with its choices | partly: the colony-scale ordinary play. Not the food and not the vent competition |
| Cauldron | `cauldron_walk` | no | some: the persistent injured worker, the bound grove and the repeat of the main action left the scenario | no; only the sentence's tail (returning still offers dependable work) is long play |
| Contagion | `genome_brings_tissue` | no | no: the four-day jump became a deadline set ahead, and the scene was split | no: nothing here is long play |
| Contagion | `cast_lives_here` | no | slightly: spawning within a day at density became a spawner call and a def read | no: a day is not a season |
| Contagion | `walk_red_lid` | no | yes: the natural Burn with a dash, the repeated dash and the full list left | partly: the lived-in weeks on the full list. Not the dash |
| FeverWood | `branch_home` | no | slightly: the repeat with forty workers left | partly: colony scale only |
| FeverWood | `delayed_establishment` | no | yes: faction-gained arrival, the defeated adult and the reloads before maturity left | no |
| FeverWood | `bait_wager` | no | yes: the live second front, the blocked edge and the reload with a wave pending left (raid tests are paused) | no |
| FeverWood | `ordinary_walk` | no | some: the repeated branch trip and 'without restaging' left | no; only 'repeats ordinary branch work' comes near long play |
| GelatinousSlime | `repeat_walk` | no | yes: the forty-colonist routine with contention and alerts left, and the cost record | partly: carrying on with a prepared colony |
| PyrelandsMechanics | `attack_brings_raids` | yes | yes: the bar's sentence lost the raid in the following days | no: the raid is a raid claim (raid tests are paused) |
| PyrelandsMechanics | `no_arson_tally` | no | no: three fires and a fire-hawk replace several over days | no |
| PyrelandsMechanics | `walk_tribes_season` | yes | yes: the bar's sentence lost the warning at the scar and the full list; the oracle lost the second rite | partly: waiting in play until a rite comes by itself. Not the warning and not the second rite |
| Stillsand | `ordinary_work` | yes | yes: the bar's sentence lost the forty-colonist harbour | partly: colony scale only |
| Stillsand | `stillsand_walk` | no | yes: the expedition, the security of the island and the next departure left the scenario | partly: the whole loop played. Not the repeat of the expedition action |

## Cauldron `prepared_day`

- oracle_proposed, old: Phase-keyed jobs, queue uptake/completion, free fed workers, health and stock conservation, actual default settings and declared supplies, attributed component timing under inherited advisory floor. No 30-day soak or unsupported numerical yield target.
- oracle_proposed, new: the prepared workers complete their orders with no new ambient injury; the bare worker is harmed; stock deltas match the completed jobs
- experience, old: A player running a prepared forty-colonist Cauldron settlement completes ordinary shelter, forestry, hauling, food and water work through a bloom without unavoidable new ambient injury or silent production loss. An exposed expedition and wild vent competition still present attributable choices and danger.
- experience, new: The player whose people are sheltered, geared and supplied gets ordinary shelter, forestry, hauling and water work done through a bloom without unavoidable new ambient injury or silent production loss. An exposed expedition still carries its danger.
- scenario, old: routine_day runs a bounded ordinary duty cycle at shipped tuning after the individual features pass, using actual workers, shelter and full gear, stockpiles and supplied research/industry. Contrast an otherwise equivalent missing-shelter/gear worker and a competing wild vexxiss. Capture work completion, resource ledger and health per phase; do not replace colony needs with immortality.
- scenario, new: routine_day runs one compressed bloom over two prepared workers and one bare one with three orders. His walk: an ordinary settlement through a bloom.

## Cauldron `cauldron_walk`

- sentence, unchanged: The player can resume midway through Cauldron work, repeat the core action and perform the main actions in a second order without losing protection, grove binding, vent state, health, stored fluids or completed discovery. Returning still offers dependable work and risky expeditions.
- oracle_proposed, old: Compare durable per-actor/map inventory and research/state manifest before/after real save-load, repeat job and conversion deltas in both orders; run gas_chain mid-burn continuity independently.
- oracle_proposed, new: the state digest before the save equals the one after the reload; both orders give the same products and stock deltas
- scenario, old: resume_walk saves midway through warning and tap/works production with a persistent injured worker and bound grove; reload that save, repeat thornwood harvest and production, then use a second order: secure protection and process water before forestry, compared with forestry then industry. A separate mid-flame reload in gas_chain proves active combustion continuity. Perform normal medical purge after the persistence observation.
- scenario, new: resume_walk saves midway through warning and tap production and reloads; resume_walk_second_order takes the main jobs in both orders from one checkpoint; metal_purge and gas_chain decide the purge and the mid-flame reload. His walk: returning to the colony.

## Contagion `genome_brings_tissue`

- sentence, unchanged: The player who extracts a genome sample, injects a Bloody Mess and waits out the gestation sees the odds before committing and, when the wanted part misses, still gets matched or sellable tissue.
- scenario, old: Saved site: extract a sample from a donor, inject a host, jump four days; read the odds shown before the injection, the batch and its donor labels; install one organ on the donor; interrupt a second injection mid-bar.
- scenario, new: Saved site: extract a sample from a donor, read the odds, inject a host, set the gestation deadline ahead and read the batch; separate small scenes install parts, refuse orders and read the burst.

## Contagion `cast_lives_here`

- sentence, unchanged: The player sees the Contagion's natives spawn at density and each read as its own creature, never a magenta square.
- oracle_proposed, old: every roster row spawns at least once within the day and is captured at play zoom; a judge agent names each capture as a distinct creature and none as another row's; no species renders the missing texture
- oracle_proposed, new: every roster row comes from the biome's own spawner and is captured at play zoom; a judge agent names each capture as a distinct creature and none as another row's; no species renders the missing texture; animalDensity is above zero in the def
- scenario, old: Saved site, wild animals spawned to the biome's density over a day by clock; screenshot each species at play zoom; count spawns per roster row.
- scenario, new: Saved site, the biome's own spawner called for each roster row; each species captured at play zoom.

## Contagion `walk_red_lid`

- sentence, unchanged: The player walks a lived-in Contagion colony through a Bloom day, a natural Burn with a dash, a Repulsor Burn and a gestation, and the sky and the body tell one story.
- oracle_proposed, old: after reload the Burn clock, touched severity and gestation match the save; both orders give the same batch and letters; the repeated dash costs a dose again
- oracle_proposed, new: after the reload the Burn clock, touched severity and gestation deadline are the saved ones; both orders give the same batch and letters; that the sky and the body tell one story is judged at his walk
- tier_reason, old: the walk is the mod in play on the full list
- tier_reason, new: the script's part is one save and load and one order check, on the small list; a lived-in colony on his full list is his walk
- scenario, old: Load a lived-in Contagion save made mid-way through two in-game weeks; take a natural Burn with one dash, then a Repulsor Burn and a gestation; reload and take them in the second order, gestation first; repeat the dash on the next Burn; read doses, hediffs, the batch and letters each time.
- scenario, new: Script: touch a colonist, inject a host, jump the Burn clock to mid-tells, save, reload and compare; then, from one checkpoint, a Repulsor Burn and a birth in both orders. His walk: a lived-in Contagion colony on his full list through a Bloom day, a Burn with a dash and a gestation.
- false_pass, old: ['a fresh map stands in for the lived-in save', 'the second order is never run']
- false_pass, new: ['a reload compared with itself', 'one order run twice']
- tier_proposed, old: live_full
- tier_proposed, new: live_minimal

## FeverWood `branch_home`

- sentence, unchanged: The player at play zoom sees ordinary workers harvest and haul between inhabited crown destinations along actual bough routes; marsh refuses heavy construction and a built stilt platform supplies the alternative. Walking onto or off the crown works for colonists and raiders without ascent gates.
- scenario, old: Authored FeverWood site using the real local terrain passes: two crown work destinations, connected boles, marsh shortcut, registered pool and alternate branch lane. Repeat with a route interrupted and with 40 routine workers; compare build orders on marsh and completed stilts. Before furnishing, generated_terrain checks real ordered pass outputs, soil-to-marsh conversion, bole anchoring, allowlisted painting and per-cell pool registration/cluster membership, with generation-off paired maps.
- scenario, new: Authored FeverWood site using the real local terrain passes: two crown work destinations, connected boles, marsh shortcut, registered pool and alternate branch lane. Repeat with a route interrupted; compare build orders on marsh and completed stilts. Before furnishing, generated_terrain checks real ordered pass outputs, soil-to-marsh conversion, bole anchoring, allowlisted painting and per-cell pool registration/cluster membership, with generation-off paired maps.

## FeverWood `delayed_establishment`

- sentence, unchanged: The player at play zoom sees an armed tank escapee enter a particular registered pool and establish there for several days before the adult returns. During that interval only the right poison at that pool prevents maturity; treating another pool or holding no reagent does not. Arrival alone does not erase a prior adult victory.
- scenario, old: Armed escape, wild-born, faction-gained and deliberate-return arrivals; defeated adult before entry. No treatment, correct treatment, wrong pool, wrong reagent and absent reagent arms; reload just before maturity and treatment completion. Verify free crafting and campaign acquisition separately. Campaign-only RUT_FeverWoodRadioactiveSalvage is a proposed missing output of the existing irradiated-wreck salvage lane under the filed water/captive items. Prove normal acquisition before local treatment, with a campaign-patch-absent control.
- scenario, new: Armed escape arrival at A, with wild-born and deliberate-return controls; its deadline set ahead. Treatment choice, wrong pool, wrong reagent and none from one checkpoint. Campaign reagent acquisition is campaign_reagent_lane's.

## FeverWood `bait_wager`

- sentence, unchanged: The player at play zoom designates living bait, has it nonlethally subdued, hauled and staked through normal work, and watches either first faction converge on it. A possible second front comes later from a separated reachable approach; a lone front remains dangerous and triggered release can lock. Bait is not merely an initial goto before an unrelated assault.
- oracle_proposed, old: Trace normal designation to nonlethal work, haul, live restraint and value. Record each actual faction/entry/tick, ongoing jobs/targets and pending schedule through delayed or absent second-wave, blocked-edge and reload cases. Available bait draws continuing approaches; a first goto alone is insufficient. Corpse/invalid/disabled bait is refused and post-trigger release respects its configured lock.
- oracle_proposed, new: Trace normal designation to nonlethal work, haul, live restraint and value. The scheduler gives a later, single, separated second front and refuses a blocked edge (offline). One pawn of a first faction targets the bait. Corpse, invalid and disabled bait is refused and post-trigger release respects its configured lock.
- scenario, old: Eligible and invalid/corpse bait, normal designation/workgiver flow and voluntary release before/after trigger. Either first faction, second-wave present/absent, blocked preferred edge, bait lost and reload while a wave is pending. Observe jobs through approach and clash, with ordinary workers as competing targets.
- scenario, new: Eligible and invalid bait, normal designation and work, release before and after the trigger. The schedule of a second front is read offline; one pawn of the first faction shows the pull of the bait. Two factions at the bait are his walk.

## FeverWood `ordinary_walk`

- sentence, unchanged: The player repeats ordinary branch work after a save made mid-consequence and reload; the save retains the active rescue and pool memory rather than forgiving them. In a second order the player returns a young before taking shore work, and outstanding gifts and delayed lure or maturation work still finish once.
- oracle_proposed, old: Compare independent snapshots before save and after reload for an actual active shore deadline, agitation/grievance, product clock, pool maturity, hush reasons, owed gift and pending wave. Complete or expire each once without restaging, repeat the normal branch trip/rescue and run return-before-shore versus shore-before-return. Idle-only reload and copied saves missing an obligation cannot pass.
- oracle_proposed, new: Each saved identity and absolute due tick after the reload is the saved one; each obligation ends once; both orders end alike. Idle-only reload and a copied save that misses an obligation cannot pass.
- scenario, old: Do branch harvest/haul, actual shore seizure, save mid-rescue, reload and repeat the core action with a nearby helper. Save distinct occupied-tank, establishing-young, owed-gift, hush and pending-wave branches; reload each. Run a second order: peaceful return, branch haul, shore rescue, then collect the gift, compared with shore work before return.
- scenario, new: ordinary_reload_walk: one real seizure, saved and reloaded. reload_owed_obligations: one save with six obligations, each read before and after. return_before_or_after_shore: both orders from one checkpoint. His walk: repeated branch work.

## GelatinousSlime `repeat_walk`

- sentence, unchanged: At ordinary play zoom, the player can resume a mid-journey save, repeat the chosen-gene rescue and carry on with a prepared colony. The body stays useful and its costs stay legible through a different order of the main actions.
- oracle_proposed, old: Record ordinary actions and exact saved/resumed identities, item/health/job counts, next-order uptake and continuing routine. Capture player-readable urgency and record contention/performance against the advisory inherited floor.
- oracle_proposed, new: saved identities, clocks and item counts are read again after the reload; a spent dose is refused; both orders give the same products; that the body stays useful and its costs legible is judged at his walk
- scenario, old: Save mid-way with a primed/loaded seeker and active patient, reload and complete extraction/injection/friend rescue. Repeat the core chosen-gene action with fresh accounted items. Use a second order of main actions, production before expedition and expedition before production. Resume a representative 40-colonist routine with shared-friend contention, native activity and alerts.
- scenario, new: walk_reload_repeat: one patient saved mid-absorption and reloaded. repeat_with_fresh_dose: the core action again. production_and_expedition_order: both orders from one checkpoint. His walk: a working colony with a patient in it.

## PyrelandsMechanics `attack_brings_raids`

- oracle_proposed, old: relation goes to hostile on the attack; a later raid's faction is the Tribes
- oracle_proposed, new: relation goes to hostile on the attack
- experience, old: The player orders colonists to attack a Tribes party openly: the Tribes turn hostile, and a raid from them comes in the following days, possibly again later. This is vanilla faction hostility; nothing in this mod adds to it.
- experience, new: The player orders colonists to attack a Tribes party openly: the Tribes turn hostile, and vanilla faction hostility follows. Nothing in this mod adds to it.
- scenario, old: Order a drafted colonist to shoot a rite harvester who is not defending fruit; read goodwill and relation; let days pass and read the storyteller's raids by faction.
- scenario, new: Order a drafted colonist to shoot a rite harvester who is not defending fruit; read goodwill and relation.
- false_pass, old: ['the hostility is set by the test', 'a raid from another faction is counted']
- false_pass, new: ['the hostility is set by the test']

## PyrelandsMechanics `no_arson_tally`

- sentence, unchanged: The player whose colony sets fires on a Pyrelands map, its own and its tamed animals', never sees a raid, a goodwill loss or a warning from the Tribes because of them.
- scenario, old: After the arson count is removed: let colonists light several grass fires over days with the Tribes present; read goodwill, letters and queued incidents; read that RUT_FireRaid, the arson debt tally and their settings no longer load.
- scenario, new: After the arson count is removed: let colonists light three grass fires and a tame fire-hawk drop a twig with the Tribes present; read goodwill, letters and queued incidents; read that RUT_FireRaid, the arson debt tally and their settings no longer load.

## PyrelandsMechanics `walk_tribes_season`

- oracle_proposed, old: state digest before save equals after reload; the second rite harvests again; the switches leave no Tribes pawn or lord behind; log clean
- oracle_proposed, new: state digest before save equals after reload; the party leaves with its fruit; the switches leave no Tribes pawn or lord behind; no log line names this mod; that a rite comes by itself is judged at his walk
- tier_reason, old: whether a rite ever comes in ordinary play, and survives a reload, shows only on his full list with the real fire clock (failure mode 1)
- tier_reason, new: the script's part is one forced rite, saved and reloaded on the small list; a rite that comes by itself in a played season is his walk
- experience, old: The player plays a Pyrelands colony on the full list in ordinary play until a rite party comes on its own: watches it light the grass and pick behind the front, sends a colonist to pick in their scar and is warned off, saves while the party is harvesting, reloads, and finds the party, its lord, its scar and its carried fruit exactly as they were; the party then walks off with the fruit.
- experience, new: The player saves while a rite party is harvesting, reloads, and finds the party, its lord, its scar and its carried fruit exactly as they were; the party then walks off with the fruit. In ordinary play a rite party comes on its own, lights the grass and picks behind the front.
- scenario, old: On his full list, wait for a rite to arrive by its own roll (the hook only if none comes in the time budget, and recorded as such); save mid-harvest; reload and compare lord toil, scar cells, carried counts and goodwill; repeat the core action on the next rite; then a second order: a colonist picks first and the rite arrives while it is in the scar; switch the rite and the visit off and on mid-game and see nothing left behind.
- scenario, new: Script: force a rite, save mid-harvest, reload and compare; a rite that finds a colonist picking; a switch off under a rite; the roll offline. His walk: ordinary play on his full list until a rite comes by itself.
- false_pass, old: ['the reload is from a save made before the party arrived', 'the rite is forced every time, so the ordinary-play roll is never seen']
- false_pass, new: ['the reload is from a save made before the party arrived']
- tier_proposed, old: live_full
- tier_proposed, new: live_minimal

## Stillsand `ordinary_work`

- experience, old: The player constructs and uses the retained workshop, resource and creature systems through ordinary orders. Jobs, reservations, persistent outcomes and feature controls remain usable with repeat work, interruption and a 40-colonist harbour. Settings report their actual application time and preserve prior user values after testing.
- experience, new: The player constructs and uses the retained workshop, resource and creature systems through ordinary orders. Jobs, reservations, persistent outcomes and feature controls remain usable with repeat work, interruption. Settings report their actual application time and preserve prior user values after testing.

## Stillsand `stillsand_walk`

- sentence, unchanged: The tester can carry out the expedition and resupply loop, reload a save made midway and repeat the core action, then complete the main actions in a second order without losing work, discoveries or persistent consequences.
- oracle_proposed, old: Use ordinary player orders with an event/item census at each checkpoint, a before/reloaded/final identity comparison and a no-reload sibling. Both orders must reach their declared next undertaking with accounted costs. Unique captures establish the visible continuity.
- oracle_proposed, new: the state before the save is read again after the reload; an emptied cave stays empty; both orders end with the same provisions and paid costs; the expedition itself is judged at his walk
- scenario, old: Do the prepared-harbour departure, sparse crossing, island exploration/security, useful cave return, workshop provisioning and next departure. Save mid-way during return work with an active wet interval and pending warning, reload and finish. Repeat the core expedition/resupply action with the emptied-cave variant. In a second order prepare the workshop before exploration, then discover/secure/resupply. Compare resulting items, bills, reservations, wet expiry, warnings and harbour state.
- scenario, new: walk_accept: one save and reload mid-work with a pour and a warning. emptied_cave_stays_empty. workshop_before_or_after_cave: both orders from one checkpoint. His walk: the expedition and resupply loop.
