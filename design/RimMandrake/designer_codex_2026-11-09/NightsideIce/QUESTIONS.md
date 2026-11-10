DRY RUN — NightsideIce / The Sleeping Ice, stages 0 and 1. The proposed root, pictures, questions and guesses are agent text, not Mandrake's words. Nothing here is approved or sent.

PROPOSED ROOT

The Sleeping Ice makes a crossing, a salvage stop and a journey below the surface three ways of facing the same place: dirty white ice that preserves what it swallows and responds dangerously to warmth. The surface is sparse and still. A comfortable camp announces itself to blind shivven travelling inside the ice; their moving cracks and rumble let you follow the approach. Open ice beside the camp can develop an attackable breach, with a precisely warned first encounter and less certain later ones. Cold and constructed floors are real defences. Staying longer brings the larger story already designed for this biome: softened slabs give up preserved remains, apparently lifeless ground can spend its one movement, and insects and young wyrms foreshadow the apex below. Digging for what the ice kept and recovering someone taken beneath it are deliberate expeditions with readable danger and a way home. Frozen wrecks reward stopping; Lantern Deeps supplies its own persistent caves beneath qualifying ground. The choice is what to risk and recover before moving on, and what it takes to make a longer stay possible.

The anchor is his chosen experience sentence, reproduced from `design/RimMandrake/biome_experiences_2026-10-20.md`, NightsideIce row (picked by card, 2026-10-20): **“A frozen highway that nobody stays on. You cross it, dig into it, or go under it.”** That existing sentence is his; the proposed paragraph above is mine. The same sentence appears in `design/validation_walks/RimMandrake/SleepingIce.md`.

My claim: the warmth needed to stop safely also makes stopping dangerous; the crossing, salvage and descent give that pressure a purpose.

Strongest objection: this paragraph could make the current heat-and-cracks loop sound like a finished journey. The larder, thaw/calving, most strange life and related surface events remain design/backlog in the source I read. The Deeps is a neighbour's built destination, not proof that a shivven warren can be entered. These are proposed acceptance promises, not claims that the build passes them.

Eight draft questions form a bank. **Ask 01 and 02 first**, then at most three per turn, pruning the rest against the answers. A phrase, a different story or “this doesn't matter to me” can answer. No silence is treated as agreement. Written scenes below are thought experiments, not captures, mocks or accepted scenes; any later decision about actual appearance needs a labelled visual exploration. Independent review is pending.

01. ASK FIRST — What the journey has to mean

Picture: Your clan crosses a silent ice plateau, pauses at an abandoned expedition rig, and finds a way below. A longer stay needs warmth, and that warmth starts trouble around the camp.

Question: Which part of that journey makes your sentence true, and where does my proposed root give you the wrong picture?

Why it matters: F1/F2. “Nobody stays” could mean a place people usually traverse, or a place where a successful long stay still feels like an expedition. The existing settlement mechanics remain covered under either reading.

My guess, not your answer: Crossing is the normal story; a salvage camp or buried refuge is an exceptional commitment that must earn its trouble. I recommend leading with the journey and showing what makes a stop costly.

What changes in the tree: If moving on is central, the root and walk follow arrival, a chosen stop and departure; the warm-base loop gets its own acceptance scene. If a hard-won refuge is equally central, routine occupation becomes part of the main walk too. If my linking idea is wrong, rewrite the root before deriving leaves. Existing mechanics and admitted backlog are not put up for removal; no reply means no approved root.

Evidence: `design/RimMandrake/biome_experiences_2026-10-20.md`; `design/Jawa/worldbuilding/biomes/sleeping_ice.md` §§4, 7–8.

02. ASK FIRST — The first demonstration

Picture: A, a small warm camp: the dial rises, a first crack warns, and you stop one breach while a second example releases shivven. B, a crossing with a useful salvage detour and a clear reason to leave. C, a journey down and back, with the Lantern Deeps entrance and the still-unbuilt warren rescue shown as separate destinations.

Question: Which demonstration would you put first when deciding whether this biome understands you, and what failure there would make you stop watching?

Why it matters: F1/F2. The first showcase should test his experience, rather than merely the easiest built mechanism. His experience choice is not itself a flagship pick.

My guess, not your answer: A first, because it can show the biome's central bargain with the existing build; B then puts it into a journey. I recommend A, while being explicit that C's warren portion needs building.

What changes in the tree: The chosen scene becomes showcase 1 only after a recorded owner pick. A needs an ordinary ticking warm/cold contrast and a real attack on a crack; B needs a successful crossing and salvage payoff; C needs the actual chosen descent and return. Other capabilities remain covered by distinct scenes, with interaction checks where systems meet. Choosing an unbuilt flagship does not make it ready to stage.

Evidence: `src/RimMandrake/SleepingIce/validation.py`; `src/RimMandrake/rimflow/roles/designer_scene_contract.md`; `src/RimMandrake/LanternDeeps/Source/LanternDeepsMod.cs:115`.

03. A place forty people can occupy without forgetting where they are

Picture: A forty-person colony has made a warm, floored refuge. They still need to go outside for salvage. Compare a routine where the edge needs occasional attention with one where every workday is interrupted by another urgent crack.

Question: What should a normal day's compromise between comfort and danger look like once that refuge is working?

Why it matters: F2/F3. More heat already means more and larger breaches, and insulation/cold outside are already part of the design. The missing experience bar is how much useful work and quiet remain at colony scale. A fixed “three days” in the settings cannot answer that by itself.

My guess, not your answer: A prepared refuge gets stretches of useful work; heating carelessly creates a visible trend toward trouble. I recommend making risk a reason to manage the camp, with enough quiet to notice the stillness.

What changes in the tree: Occasional interventions need a sustained routine-use scene measuring useful work and warning load. Constant watchfulness needs an explicit staffing/attention cost in the main promise. If the exact cadence does not matter, keep frequency tuning advisory and accept only readable heat escalation, recovery and functional defences. No answer reopens the hull rule or makes the source's current heat formula the acceptance oracle.

Evidence: `design/Jawa/worldbuilding/biomes/sleeping_ice.md:174`; `src/RimMandrake/SleepingIce/Source/RM_SleepingIceMod.cs:34`; `src/RimMandrake/SleepingIce/Source/RM_HeatDial.cs:63`.

04. Enough warning to make a decision

Picture: The first crack appears while a worker is far from camp. Its letter gives an exact countdown. You can recall the worker, send someone to break the crack, or prepare to meet what comes through. The shipped first timer is 24 in-game hours; that is tuning, not a newly approved bar.

Question: Which preparations should that first countdown let a small travelling party finish, and what mistake should still cost them?

Why it matters: F2. The first breach being taught and timed is already settled. A countdown can still fail to give a traveller a useful response, or erase all danger by allowing every preparation.

My guess, not your answer: Recall exposed people and make one deliberate response; ignoring the warning should leave them facing a real breach. I recommend that as the first scene's success and rejection pair.

What changes in the tree: A recall-and-response window needs dispersed workers, actual travel and an ordinary attack order before expiry. A fortification window also needs construction labour and material costs in the fixture. A deliberately narrow escape window needs an honest departure route and recovery of the party. Later warnings remain vague under every answer; this does not ask for a second teaching letter or precise later directions.

Evidence: `design/Jawa/worldbuilding/biomes/sleeping_ice.md:255`; `src/RimMandrake/SleepingIce/Source/RM_BreachCracks.cs:103`; `src/RimMandrake/SleepingIce/Source/RM_SleepingIceMod.cs:37`.

05. Flooring a crack that has already started

Picture: A crack has opened outside. Before its timer ends, the crew completes a constructed floor across that spot. The rule that a burst cannot come through floor or hull is already fixed; the code currently checks open ice when placing the crack and does not check it again when releasing shivven.

Question: What should the crew see happen to that existing crack, and where should the pressure beneath it go?

Why it matters: F2/F3. The hull rule settles where a burst may emerge. It does not settle the story of a crack sealed after it began. This is a transition of a built capability, not an offer to remove breaches.

My guess, not your answer: The floor visibly seals this opening; a warm camp can later attract another crack on eligible open ice. I recommend preserving both the successful local defence and the ongoing cost of warmth.

What changes in the tree: A sealed opening needs a completion-before-expiry control and no emergence through the new floor. Continued pressure beneath it needs an honest blocked state and a defined outcome when that floor is later lost. Movement to another opening needs a readable relocation, legal ice cells and the agreed warning treatment. No answer permits emergence through a floor, including in adjacent spawn cells.

Evidence: `design/Jawa/worldbuilding/biomes/sleeping_ice.md:277`; `src/RimMandrake/SleepingIce/Source/RM_BreachCracks.cs:146`; `src/RimMandrake/SleepingIce/Source/RM_BreachCracks.cs:208`.

06. A decoy heater and a safer camp

Picture: A strong heater is enclosed behind flooring. A weaker working heater is exposed beside open ice. A shivven can reach the weaker one; the stronger one is either behind that barrier or beyond its sensing range. Today it selects the map's strongest working heater before considering its own range and route.

Question: What should that shivven do as it reaches the strongest warmth it can actually approach, and what should make a decoy succeed or fail?

Why it matters: F2/F3. Heat sensing and floor protection are settled. Lingering at a protected beacon, pursuing an exposed local source and ignoring everything because a remote heater won a global comparison produce very different player strategies.

My guess, not your answer: It follows warmth within reach and waits at a real barrier; a decoy can draw it somewhere useful only while it supplies a believable stronger local signal. A remote out-of-range heater should not make nearby heat cease to exist.

What changes in the tree: Strongest sensed source needs selection within the sensing boundary before pursuit. A stronger protected beacon that holds attention needs a visible waiting state and a source-off transition. Switching to accessible heat needs distinct targets and demonstrated target changes. Range and barrier cases remain separate: inability to travel is not inability to sense. No answer adds light, sound or vibration as a native sense.

Evidence: `src/RimMandrake/SleepingIce/Source/RM_HeatDial.cs:123`; `src/RimMandrake/SleepingIce/Source/RM_Shivven.cs:82`; `design/Jawa/worldbuilding/biomes/sleeping_ice.md:336`.

07. What makes a salvage stop worth the warmth

Picture: The party has reached a frozen hull and expedition rig. Spending the day recovering useful cargo means feeding and protecting a warm camp; passing by means arriving sooner. The ice-kept bodies and deliberate thaw/calving will add further finds when their existing backlog is built.

Question: What should the party bring away from a successful day's stop that makes you glad they took the risk?

Why it matters: F1/F2. The wreck field is built; the recovery story remains thin if its reward is indistinguishable from incidental scrap. This asks for the payoff, without re-pitching the passed learned technology, ship crust or rites.

My guess, not your answer: A useful haul of unusually well-preserved equipment or materials, with enough visible evidence of the failed expedition to make the stop memorable. I recommend a practical cargo payoff before adding another progression system.

What changes in the tree: A material payoff needs a complete salvage-and-haul scene with useful quantities and work costs. Recoverable equipment needs actual usable items and condition preserved. If the abandoned expedition's readable story is essential, add a bounded recognition requirement against a real scene; show a labelled mock before specifying its look. If the story is incidental, it stays advisory. Cold Ledger remains admitted campaign design, and its detailed props are not inferred from this answer.

Evidence: `src/RimMandrake/SleepingIce/Defs/ThingDefs_Buildings/RM_NightsideWrecks.xml`; `infrastructure/state/items/ICEKEPT_DEAD_BUILD_CUT_OUT_COLD.md`; `design/Jawa/worldbuilding/biomes/nightsideice_bedazzle_review_2026-10-01.md:347`.

08. Going under to bring someone home

Picture: In the designed larder story a named colonist has been dragged under, leaving a trail and a warning. You assemble a rescue party at the crack. A nearby Lantern Deeps entrance already leads to that mod's persistent cave, but it is not yet a route into the shivven's stored victims.

Question: Walk me from the rescue order to bringing that colonist home: where does the party go, and what can they do while below?

Why it matters: F1/F3. Drag-under storage and cut-down recovery are already ruled; reusing an underground movement kit does not implement them. “Go under it” needs a player action and destination, with a real distinction between the larder and the Deeps.

My guess, not your answer: Cutting down opens a bounded, dangerous rescue site with a return route, where the missing pawn and their condition remain accounted for. I recommend establishing that complete rescue before promising a second colonisable underground world.

What changes in the tree: An enterable warren needs entry, party transfer, victim storage/condition, rescue and return acceptance. A local excavation with combat above needs retrieval jobs and an observable underground custody state instead. A connection to the Deeps needs an explicit integration scene and ownership boundary, alongside each mod's own proof. If the proposed picture misses his meaning, revise the descent claim; do not quietly call a scanner echo a traversable passage. No answer permits a pawn to vanish without a sign.

Evidence: `design/Jawa/worldbuilding/biomes/sleeping_ice.md:261`; `design/Jawa/worldbuilding/biomes/nightsideice_bedazzle_review_2026-10-01.md:198`; `src/RimMandrake/LanternDeeps/Source/LanternDeepsMod.cs:115`.

Excluded after reading: keeping/removing built features; re-admitting the strange life; hessarund bargaining or research; frissim flight/food; a new ship, choir or learned-tech mark; ordinary walking titan passage; flora to fill the empty surface; native light/sound sensing; whether the hull rule applies. Those subjects already have answers or delegated verdicts. The full evidence and proof limits are in record.json and NOTES.md.
