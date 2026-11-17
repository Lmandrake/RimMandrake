# Page one — what I propose

A traveller crosses dirty-white upland ice beneath a cold sky, passing frozen wrecks and ridges that do not look alive. Stopping brings useful salvage and shelter, but escaping warmth draws warned breaches and blind shivven inside the ice. A prepared supplied refuge can endure by protecting its warmth and perimeter; a party can take its haul and move on.

Land: hard impure white ice, open crossing ground, hoarfrost, cold overhead sky and preserved expedition debris.

Life: scarce admitted visitors, supplied milk/cargo animals, the behaviourless mineable hessarund and concealed shivven; no pasture or native plants.

Signature: exposed warmth raises pressure; warned attackable cracks release approaching shivven; cold, floors, hull and fighting provide real responses.

These are my delegated Design Version choices under the cleanse brief. The runner-up was the sohl's single lifetime movement: a separate encounter with its own aftermath, so it waits. Your admissions and rulings stand. No roster eviction or population-ratio waiver is reopened.

Next version, switched off:

- Zhissa electric shock.
- Thaw/calving; lost-soul rescue events.
- Reconnection storms; margin ablation/rime-fall; drifting Dark.
- Active crevasse collapse.
- Sohl; frissim; wyrmlets; nest and dhorrumak.
- Saallen scraping; oolm hardening; neshkoll leak fans.
- Frozen-person extraction; larder and pocket rescue.
- Insect-fall; heat-drawn assailants.
- Cold Ledger rite.

I recommend retiring the newer tellurox hexplate: its clean-floor function duplicates vanilla sterile tile and adds a ship furnishing outside this promise. Until you decide, keep its defs/art behind a next-version switch defaulting off. Ordinary tellurox, shell stuff and cargo remain. The built zhissa shock also gets a tested switch-off; its milk, breeding and physical defence remain. Your previously passed ship/sound/research proposals stay closed.

Counts: capabilities 59 before disposal, kept 39 for this version, next_version 19, recommend_retire 1. These include shared engines and proof instruments, not just player mechanics. Bars 8 after, old_bars 0 before; live-only bars 2 after, none locked before. Checks 11 and rules 12 are separate from passing. Models 4, tickets 31, unknown_pairs 3, questions 0. Counts are from result.json and its underlying files; the earlier concept has no locked leaves.

No change is applied yet. This proposal needs the fresh review and your decision; it claims no new gameplay proof.

# Page two — what to check

The consequential readings I took:

- “Nobody stays”: lasting refuge allowed, as your recorded answer already settles; no eviction mechanic.
- “Highway”: open crossing country, not a required paved line.
- “Dig/go under” requires ordinary mining/salvage and a working Deeps descent/return at shipped defaults in both free and campaign loads. Entrance placement follows its ordinary chance rules. The rescue pocket waits with the larder.
- “Young ice”: hard dirty-white geology, not snow, blue ice or accelerated growth.
- “Nearly empty”: admitted visitors and stationary life, not missing ecology or an arctic replacement zoo.
- “Insulate”: a comfortable cold-exterior refuge must reduce exposed thermal pressure. The current indoor sum cannot prove that; my explicit proxy needs calibration against actual room cooling and heater duty.
- “Hottest”: choose sensed reachable warmth before ranking strength. Your answer rules out protected decoys monopolizing attention.
- “Warmth”: fires and warm rooms need coherent approach targets too. Existing shivven can approach downed living warmth; a cold corpse emits none. No healthy-walker hunt or invented abduction.
- “Floor protection”: validate every emergence cell and actual path step. Flooring a pending opening visibly seals it; its old timer never moves elsewhere or revives later.
- “First warning”: enough time for ordinary worker recall and response. “Later vague”: no exact countdown or notification arrow; manual searching/scanning can still find the crack.
- “Off”: cancel pending owned hazards visibly, stop owned jobs and keep animals accounted for; no delayed release after re-enabling.
- “No water/farming”: no prefab puddle tolerance or native soil; no invented ban on imported supplies or vanilla hydroponics.
- “Whole” keeps normal weather, jobs, heat, needs and breach clocks running through reload and reversed preparations. Direct override/lock and sky-scheduler reads must detect a planted Clear lock even when ordinary weather would also stay Clear.
- “Capacity” can stay permanently full of surviving waiting shivven. Only accounted death frees an occupied slot. I added this regime to the season model and bar ranges.

I kept the ordinary hoarfrost and mineable ridge because removing them loses the ruled land and stationary life. I moved their independent neighbours' mechanics instead of retaining extras under a “life” label. Scanner payload and shared salvage remain dependency contracts. Deeps hosting now requires runtime eligibility and a real pawn round trip in both load contexts. That evidence is still missing.

Build the specified instruments in this order:

- Situation/lifecycle generator: cover states, cancellation, metadata and actual reloads that today's forced helpers miss.
- Ice-boundary geometry sweep: compare planned routes with actual steps, source eligibility and legal emergence after construction.
- Exterior-heat model: compare equal-comfort insulated/exposed real rooms before trusting my pressure proxy.
- Whole-plateau season model includes permanently saturated survivors, direct lock detection and Deeps trips alongside heat, salvage, repairs and warnings.

What remains unknown is measurable: whether actual paths honour defence without stalling; whether the exposure proxy preserves useful insulation feedback; whether the combined supplied colony has working time between interventions. I specified models and acceptance tests, rather than asking you to predict those observations. Existing isolated October successes remain historical evidence; no current full-season proof is available. No unresolved scope choice requires a question.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a sourced core promise omitted or weakened (bars.json B4 (accept[0], meant.intent, range); definition.md 'Implementation choices' exposure proxy; models.md M3). Owner-ratified sheet design/Jawa/worldbuilding/biomes/sleeping_ice.md:180-183: "Gameplay: your heating is your threat generator. Insulate, run cold, and nothing comes. Heat the base to a comfortable temperature and you have lit a flare on a dark plain. That is a real strategic tension". B4 accept[0] instead accepts "A warm refuge retains its indoor comfort after its exterior is better insulated; the readout falls", and its meant.intent says "insulation preserves useful warmth indoors". definition.md weights a closed door at 0.25, a wall face at 0.1/t and a roof cell at 0.05 against 1 for an open boundary. On those coefficients a walled, roofed, closed-door room is weighted at well under a tenth of an exposed one [guess ~85%, arithmetic on a 5x5 room]. B4, B8 and M3 compare only exposed against insulated rooms at equal comfort. None of them requires that a comfortably heated insulated base still draws more breach pressure than the same insulated base run cold. So the comfort-against-safety tension the owner ratified can be insulated away and no bar would refuse it. Would pass: A B4 pair that keeps both owner clauses: insulation lowers pressure, but a comfortable insulated refuge still draws more breach pressure than the same refuge run cold. M3 must check that ordering, not only the open-against-closed one. Smallest fix: Add a B4 reject picture: "A walled, roofed base heated to comfort draws breaches no more often than the same base left cold." Add a 'comfortable insulated vs cold insulated, same walls' paired cohort to B4.range and to M3's sweep and calibration. Reword meant.intent to cite sleeping_ice.md §4 'comfortable = flare' alongside 'insulate'.
- an extra left in the first version without its needed_by deletion argument (census.json row tellurox_livestock (fate life); bars.json B2 accept[0] and reject[0]). The row says "Housed in this module, not on its inline wild roster" and gives as its why only "Imported working livestock carries cargo and yields permanent shell when butchered; it is not a new wild admission." Its needed_by is empty. Its home was a tier migration by card (OWNER.jsonl tsn 1792859729611947407, byCard "Tellurox home → RM tier, lore removed"), not a ruling that it is this biome's life. A player meets it only through trade. It carries its own permanent-shell butcher bonus. Even so, B2 makes it part of passing ("an imported tellurox carries cargo"; reject "the shell pack beast cannot carry a caravan load"). Would pass: Either a stated deletion argument showing why land, life or the signature fails without tellurox, or tellurox classed as a def the module hosts (a dependency or outside the biome's first-version life), with B2's pack picture met by any imported pack animal. Smallest fix: Change tellurox_livestock's fate to dependency (a hosted def, kept as is), and rewrite B2's pictures to say "an imported pack animal carries cargo" instead of naming tellurox and its shell.
- evidence that cannot tell success from a plausible false pass (bars.json B2 (says, range, sees.control)). B2 says "A colony on the ice must bring food" and rejects "renewing wild pasture". The proposal keeps every visitor admission at positive density (census ice_doctrine "Density 0.2"; surface_roster: zhissa inline, plus RSW_CaveLemming, RSW_Wampa and RSW_Tauntaun patched in), and the vanilla wild spawner keeps topping that population up. B2.range lists "fed/unfed imported livestock, birth, milking, caravan loading, casualty and ordinary departure". B2.control only "distinguish[es] milk from hidden grazing". No branch hunts the visitors. A camp living indefinitely on hunted, respawning visitors would pass every observation B2 makes while breaking its 'must bring food' sentence. Would pass: B2's range and control include a hunting branch over the respawning visitors, and B2 says plainly whether hunting scarce visitors is allowed as a supplement or must fail to sustain a camp. Smallest fix: Add 'hunting admitted visitors across days 1–15 at shipped density' to B2.range, add a food-provenance control that tags meat by hunted pawn, and add one accept or reject picture that settles whether hunting visitors can feed the camp.
- an instrument or scene that would read with a mechanic off or the sky locked (bars.json B1 sees.on and range.left_out; definition.md 'Using it' (Deeps host required)). definition.md: "The first version requires SleepingIce to host a working Lantern Deeps descent and return at shipped defaults in both franchise-free and campaign loads." sleeping_ice.md §6 allows exactly one surface glow: "Lantern Deeps emergences ... leak the caverns' glow at the surface; they are not residents." B1 says "without ... a native surface glow", yet its sees.on lists CreatureBehaviors, Wreckage, EnvironmentalHazards, ExplosiveGrowth, Bones and WeatherSuite, and leaves Lantern Deeps out (only B8.on loads it). B1 can therefore pass its land and glow judgement on maps where the required neighbour's entrance scatter and glow cannot appear. Would pass: B1's scene loads Lantern Deeps at shipped defaults, includes entrance-present and entrance-absent cohorts, and has a picture that tells the allowed emergence leak apart from a native glow. Smallest fix: Append "Lantern Deeps at shipped defaults (entrance-present and no-entrance cohorts)" to B1.sees.on and B1.range.varies, and add a reject picture: "glow spreads across the ice away from any Deeps emergence".
- a figurative word unmarked (bars.json B4 says and meant.figurative (empty)). B4 says "A camp that exposes more warmth to the ice draws greater breach pressure". 'Breach pressure' is the dial and breach-chance sensor, not physical ice pressure: definition.md says "Heat pressure is a sensor of exposure, not a second temperature". 'Exposes ... to the ice' means the exterior-transmission proxy, not heat reaching ice cells. figurative is [] and no accept picture departs from the literal reading. Would pass: meant.figurative names 'breach pressure' (the continuous thermal dial and the breach chance it drives) and 'exposes warmth to the ice' (the outdoor exposure the proxy counts), each with an accept picture that departs from the literal reading. Smallest fix: Add the two figurative entries and one accept picture: "No ice cell warms and nothing deforms, yet the thermal readout rises and breaches follow when a warm room's door is left open."
