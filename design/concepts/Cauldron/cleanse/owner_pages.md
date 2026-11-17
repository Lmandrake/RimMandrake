# Page one — what I propose the Cauldron becomes

The Cauldron is a wet mineral forest in permanent dusk, with rainless lightning and chemical pools that cannot simply be drunk. Its vents quiet before a metal-heavy bloom, giving workers time to shelter or seal themselves before exposure leaves lasting harm. Capping that same chemistry turns combustible danger into collected condensate and useful supplies, so preparation earns dependable work while outdoor expeditions remain risky.

Land: distinguishable dark soils, mineral trunks, chemical fog and condensation, rainless storms, acidic air and actually hazardous pools.

Life: the current admitted cast feeds, breeds, hunts and supplies food, timber, metal and protective material; flying natives fly, rhossak bind, and native animals can drink their environmental water. No roster evictions.

Signature: heed the vent warning, protect workers, then cap and refine the same dangerous chemistry into useful supplies.

Runner-up: rhossak forest renewal. It is another complete cycle, so seeding and grove-rooting move; binding and edible galls stay.

My next-version list, all switched off:

- Dew beads and weather-swapped plant colours.
- Shore nettle spread and vent flower gardens.
- Fexxil venom and kissaveth toxic leaks.
- Suush and garsulix explosive behaviours.
- Zisska fire-spit and bedbug paralysis.
- Vexxiss water poisoning, fire policing, vent drinking, prying and tracking.
- Dressed ruins, rig-study discovery and Oomo shrine.
- Bespoke plate-only door, upgraded machines and ship corrosion/lining.
- Rhossak seeding/rooting, ossrith uranium refining and the additional trunk-age coat.

Ordinary research, basic tap/Filter-Works, suits, liquid vessels, material protection, truthful timber assay and existing mineral flecks stay. Their code must be separated from the moved features. Your previous keeps remain future promises; these are my version decisions, not your rejection of them.

I recommend retiring the alternative-world scorer/rarity option because worldgen is forbidden in every version; the Cauldron scanner payload because inspection already supplies its information; and periodic manufactured crystalmit bricks because they duplicate stonecutting. Nothing is retired here. The scorer becomes inert; the other recommendations stay off pending your decision. Mineral feeding stays.

Counts: 82 audited capabilities before scoping, 54 retained, 25 next-version and 3 recommended retirements. The census expands the earlier inventory’s 68 rows by splitting bundled behaviours and naming dependencies [measured: record.json inventory; cleanse/census.json]. Before: 18 bars, all 18 assigned a runtime tier [measured: tree.json]; that old tree does not distinguish bridge-readable from look-only. After: 10 bars, 3 live-only bars. The rest use causal state reads or calibrated models. There are 12 checks and 15 attackable build rules. No new yield, stat or art-variant count is a passing bar.

# Page two — what to check

These are my defaults, derived from your recorded answers and the source:

- “Dusk” means diffuse dim weather tint, not fixed brightness; “wet” needs fog/dewfall and existing art, not moved decorations. Shared Direct Sun governs heat; vents are chemical.
- “About an hour” measures warning-to-bloom, separately from sky interpolation and first dose. Capped sources or absent wildlife use the timed message. Walking natives supply the visual hush; suush hover is read by job/flight state, with visuals owner-present only and no flight images.
- “Sealed” uses the same final vacuum/environmental-resistance stats for acid and bloom; full non-gear sources count too. Item immunity stays a build rule. Direct liquid and smoke remain separate.
- “Persistent” means no natural metal clearance. A normal advanced-medicine purge must work even on a hidden saved trace.
- Permanent acid harm means actual lasting facial/sensory consequences after ordinary healing, not a scar label. Exceptional restoration remains possible.
- Toxic and acid water keep their actual chemistry through ordinary transfer. A coloured pool or injected tank proves nothing about delivered water.
- Connected gas crosses water; maintained empty gaps and sealed corners stop combustion. Reload must preserve the active flame front, not merely gas bytes.
- Deferring the ruined rig requires ordinary research to remain reachable. Deferring machine upgrades must leave suits and containers available.
- Ordinary animal life remains; extra jobs/hazards move without removing their animals. Renewal cannot secretly rescue the seasonal food chain.

No questions: the contrary evidence concerns construction and unrun measurement, rather than a reason to choose a different experience.

Models specified, first-to-build first:

- Situation generator: enumerate reachable states, transitions, controls and recovery.
- Gas geometry and save walk: expose corner leaks and lost active fronts.
- Coupled season and work model: find gas, ecology, illness and labour feedback failures.
- Liquid ledger and interruption walk: find chemistry changes and missing/duplicated stock.
- Exposure and treatment state walk: separate prevention, persistent load, real purge and lasting acid injury.

There are 6 unknown grouped interactions, covered by those 5 models; the 38 tickets cover switch-offs, missing mechanics and instruments. Models are predictions until checked against actual game traces. The complete system must still run through a season, reload midway and repeat the main work in another order with weather, needs and damage active.

Unsettled delivery: natural metal decay, sealing, warning timing, pool binding, active combustion saves, and coupled seasonal balance need implementation or measurement. No live proof was performed. The first reviewer’s flight, figurative wording, blast evidence, bar/rule and seal-definition objections are repaired here; the second look is pending. The whole bar now explicitly refuses goods relocation without a visible gas explosion and visible throwing. Nothing changes the mod until the review and your application decision; the build hold stays.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- two bars, or a bar and a rule, that cannot hold together (bars.json rules R_health and R_local, bar whole (range and reject), meeting 'health'; ambiguities.md section 'Persistent versus merely slow metal clearance'). R_health says: 'Designer default medical route is MedicineUltratech in a normal bill'. R_local keeps 'a residual ambient floor', so exposure never reaches zero. R_health also allows 'No natural or ordinary-care removal of positive metal load'. The whole bar's range runs to a 'day-100 state' with 'Starting water, food, medicine, components and cartridges ... finite and declared', and it rejects 'a colony that spends all its time recovering from unavoidable routine exposure'. In vanilla, glitterworld medicine has no crafting recipe and comes only from trade or loot [guess ~85%]. So every unroofed, unsealed errand adds load that never fades, and the only cure is an item the colony cannot make. The health meeting is marked 'argued' but never says where the purge medicine comes from. The owner's words (OWNER:1794373071501926623, 'requires advanced medicine to purge') name no medicine tier. ambiguities.md treats the tier as 'missing construction detail, not a new owner preference', yet that choice decides whether the cure can be reached at all on the fixed desert world. Page two never mentions the tier. Would pass: A purge whose supply route is named and reachable at shipped defaults: either a craftable tier, or an argued trade route (for example, vent reagent sold for medicine) listed as a member of the health and colony_work meetings and an input to the coupled season model. The tier chosen is shown to the owner as a settled ambiguity. Smallest fix: Add an ambiguity 'advanced medicine: industrial versus glitterworld' with its supply consequence. Take a reading that has a supply route, and write that route into R_health. Add medicine supply to the coupled season model's inputs and to the health meeting's argument. Put one line on owner page two.
- an extra left in the first version without its needed_by deletion argument (census.json rows vent_cycle_falter and eskith; bars.json bar warning (says, accept picture 3), rule R_warning, meeting hush_flight). The case for keeping native stillness is census eskith: 'deleting movement makes the warning indistinguishable from idle scenery'. The warning bar's own accept picture contradicts this: 'Already capped sources or absent eligible wildlife do not fake a puff change; the retained timed warning message still gives the worker a chance to shelter.' Vent puffs and the message already make the warning readable without hush. The owner's sourced falter words (record.json s_falter, OWNER:1792108481222070856) are about an hour of warning, not animal stillness; the hush text at record.json:760 is agent text. Keeping hush brings in the whole suush hover-in-flight rule, the hush_flight meeting, part of T30 and a flight-state calibration arm in the situation generator. Would pass: Either a deletion argument showing the default-map warning is not readable from puffs and the message without native hush, or hush moved to the next version and switched off. Smallest fix: Move native hush (with the suush hover rule) to next_version.md with a switch-off ticket. Delete 'eligible wild natives falling still when present' from warning.says and its pictures, and drop the hush_flight meeting and R_warning's hush paragraph.
- a sourced core promise omitted or weakened (bars.json bar living_cast says; ambiguities.md (no entry); source design/RimMandrake/biome_experiences_2026-10-20.md:9). The owner typed the Cauldron experience: 'Water is acid, animals are minerals, and life twists under the load… including you.' living_cast weakens this to 'mineral-adapted wildlife'. No bar picture shows a player seeing a native animal as a mineral body; the mineral reading in the bars is about the forest (place) and diets and products. ambiguities.md settles 'Angry, roils, eternal, breathes' and 'Wet, green, lush and mineral' (about plants), but has no entry for 'animals are minerals' or 'life twists'. Would pass: living_cast (or place) states what 'animals are minerals' means to the player: mineral bodies readable at ordinary zoom, or mineral diet, products and remains. It marks the phrase figurative if it is, keeps the owner-kept imports as a stated exception, and has an accept picture and a reject picture (for example, ordinary-looking fauna that only eats rocks). Smallest fix: Add one ambiguity entry and one figurative entry with an accept picture to living_cast; change 'mineral-adapted' to the reading taken.
- a figurative word unmarked (bars.json bar whole says ('dangerous expeditions', 'runaway gas'); its figurative list holds only 'error storm'). The owner's answer was 'Dependable industry, risky expeditions ... exposed discoveries' (ANSWERS_OWNER.md:5). The agent's earlier question read 'expedition' as a trip off the map: 'If the successful life is expeditionary, demonstrate what a trip brings home' (design/RimMandrake/designer_codex_2026-11-09/Cauldron/record.json:1291). The whole bar's accept picture quietly reads it as on-map 'hazardous outdoor tasks'. Those two readings differ in scope (whether caravans or off-map sites are in the season run). 'Runaway gas' is defined only in models.md ('flood: connected gas continually invading normal work routes'), not in the bar. Would pass: 'expeditions' marked figurative with what it stands for (on-map outdoor errands beyond shelter), or scoped literally with caravans in range. 'runaway' marked figurative and tied to the flood definition, each with an accept picture. Smallest fix: Add two figurative entries to whole.meant.figurative and one line in ambiguities.md on the expedition reading.
