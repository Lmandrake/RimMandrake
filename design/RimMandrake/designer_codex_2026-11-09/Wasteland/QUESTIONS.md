DRY RUN — Wasteland / The Wastes, stages 0 and 1. This is an agent-authored proposal and question bank. Guesses are not answers; nothing is approved, sent through rimflow, or written to the ledger.

PROPOSED ROOT

The Wastes makes a colony live at the receiving end of a ruined world: rivers end in brine, ash settles, and old poison stays. The ground, air and water set the terms of work; the strange animals are the life that has endured those terms. Staying here means choosing where to shelter, where to work and how much exposure a prize is worth. Storms leave fresh fall and shift what the ash hides, so yesterday's prospecting route cannot simply be trusted tomorrow. Useful survivors offer uneasy bargains: herds concentrate waste into goods, and a living furnace warms the same room it doses. Accepting paid waste deliveries gives the colony physical casks to contain, process or illegally bury, with visible leaks and consequences for unsafe handling. A twenty-cell Middenshell brings the landscape's danger into motion: its warned crossing can flatten a settlement, waste can draw it aside, its trail remains, and its dead shell becomes a quarry paid for in dose. Brine beds and irradiated wrecks offer other reasons to venture out. These promises belong to one dry, contaminated place; shared engines supply drifting ash, salvage and ordinary toxic buildup, while the campaign supplies its own people and history.

Basis: the Wasteland row in `design/RimMandrake/biome_experiences_2026-10-20.md`, the definition sheet `design/Jawa/worldbuilding/biomes/wastes.md`, and the built inventory in record.json. The experience file records his chosen sentence: “Where rivers come to die and nothing ever leaves: salt, ash and fallout pile up forever. The land is the monster, and the creatures are its victims.” That existing quotation is the source, not approval of this new paragraph.

My claim: every attractive use of this place should make the colony handle the contamination it has inherited.
The strongest objection: a collection of profitable animals, a dumping quest and one spectacular giant could overshadow the land itself. The paragraph also promises more than today's proof establishes: danger-reading flora, a storm that redistributes hazardous ground, useful waste processing and a completed quarry expedition need stronger evidence.

Eight drafts follow. Start with 01–02; serve at most three in a real dialogue turn. All pictures are written thought experiments, not captures, visual mocks or staged acceptance scenes. A different picture or “this doesn't matter to me” is a useful answer. Silence approves nothing.

01. ASK FIRST — A place to live in, between the events

Picture: The colony has survived a week. No storm is running and the Middenshell has gone. A worker walks from a roofed workshop toward a promising wreck across a flat that looked harmless yesterday.

Question: What should that ordinary working day make you weigh, and which sentence in the proposed root gets that wrong?

Why it matters: F1. The old sheet makes the land dangerous even when nothing attacks. Most explicit dose code is attached to weather, creatures, salvage and waste. An exciting incident list could leave the quiet hours feeling like an ordinary dry map.

My guessed answer — a guess, not your answer: The attraction is choosing a profitable outing against the exposure it costs, with a place to recover and prepare. I would lead with that daily bargain.

What changes in the tree: If outings carry the experience, make one complete prepare/work/return scene the root's ordinary-use case. If maintaining a home is the central struggle, require a sustained occupied-base scene as well. If another moment matters more, rewrite the root around it while retaining coverage of every built feature. An answer can correct the root; it is not recorded as approval unless he actually approves its text.

Evidence: `wastes.md` §§4–7; `Source/RM_MapComponent_WastesStorms.cs`; `Wreckage/Defs/RM_WreckWeatheringDefs/RM_WreckWeatherings.xml` (full paths in record.json).

02. ASK FIRST — The first demonstration

Picture: A, a scout returns after an ash storm, finds something newly exposed and brings salvage home at a dose cost. B, a paid waste delivery becomes a containment and animal-processing problem, followed by a leak. C, a warned Middenshell crossing is diverted, leaves its mark, and later a dead shell is worked as a quarry. These are proposed scenes, not completed demonstrations.

Question: Which would you put first when deciding whether this is your Wasteland, and what failure in it would make you stop the demonstration?

Why it matters: F1/F2. The biggest spectacle may be the wrong first test of “the land is the monster.” No flagship choice was found.

My guessed answer — a guess: A first, because ordinary work under the land's terms should carry the biome before its giant arrives. B and C deserve separate demonstrations.

What changes in the tree: His chosen scene becomes showcase 1 only after a recorded pick. The other features retain their own acceptance scenes; later showcases must add substantially different play. His reject case becomes a candidate core requirement. Root approval alone does not pick a flagship.

Evidence: `designer_scene_contract.md`; the experience row; `ITEM:WASTELAND_GPT_ENRICHMENT_1`; `Patches/RM_Wastes_MovingDunesBinding.xml`.

03. Reading a changed route

Picture: A storm has passed. Cinderfelt now marks fresh fall beside yesterday's route to a wreck; radmoss is thick farther along. The optional ship scanner can report a wreck or brine beds, but its present payload does not measure a safe walking route. The current flora definitions do not establish the dosimeter behaviour described in the old sheet.

Question: What should a scout be able to observe that makes “cross here, go around there” a reasoned choice?

Why it matters: F1/F3. The requirement that plants reveal dangerous ground is already in the sheet. The unresolved part is what useful information the player can actually read, especially after the ground changes.

My guessed answer — a guess: An honest rough distinction between safer crust and hotter growth, enough to choose a route without an exact radiation overlay. I recommend proving that distinction with two otherwise similar routes.

What changes in the tree: Visible bands require a demonstrated correlation between what grows and what harms, with a misleading-looking control. A close inspection requirement needs an actionable local reading. If the answer needs a dedicated instrument, establish its owner's boundary before adding a new one. No answer turns a decorative plant's name into proof that it measures dose.

Evidence: `wastes.md` §4; `Defs/ThingDefs_Plants/RM_WastesFlora.xml`; `Patches/RM_AcousticPayload_Wastes.xml`.

04. A refinery that can serve a settlement

Picture: Forty colonists have accepted a waste contract. Several bays hold casks; a small herd stands nearby. The current bay converts a cask when a nearby processor qualifies, without giving the animal a processing job. The excretor is a different, slower shearable producer; it is not a bay processor.

Question: What would a successful day's work look like here, and what would tell you that the herd has taken on more waste than it can handle?

Why it matters: F2/F3. “A kept herd is a slow refinery” can pass a one-cask test while one animal serves many bays for free, or while incoming waste outpaces it with no useful sign.

My guessed answer — a guess: A modest, visible flow of goods with a backlog the colony can understand and plan around. I would judge useful capacity and the cost of tending the herd together.

What changes in the tree: A limit per animal requires a shared-capacity case across several bays. A limit per bay instead requires that rule to be legible and a sustained throughput check. If supporting feed and hauling are the labour, demonstrate those jobs rather than inventing a new processing job. His scene sets tuning targets and the required backlog information; it does not reopen the built refinery's existence.

Evidence: `Source/RM_WasteCaskBay.cs:534`; `Source/RM_CompProcessorGatherable.cs:98`; `Defs/ThingDefs_Races/RM_Excretor.xml`.

05. The winter furnace's price

Picture: A hessekh warms a shelter. The present RM creature doses everyone sharing its enclosed room, including someone far from the animal; a separate room is outside that room-wide dose. Heat and dose have separate switches.

Question: Over a cold week, what routine should make keeping this animal a tempting bargain, and what result would make it feel like a trap with no useful choice?

Why it matters: F2. Heat plus a rising health number is a mechanism. The promised experience is choosing to keep a useful animal while managing the consequence.

My guessed answer — a guess: It makes otherwise difficult cold work possible, but time sharing its shelter has a cost people must manage. I would compare a useful shelter with and without the animal, and read the week's exposure as well as temperature.

What changes in the tree: A short-stay warming shelter needs a full use-and-leave scene. A continuously occupied shelter needs a sustainable protection or exposure-management case using the actual protection system. The answer tunes the bargain and its explanation; ambient dose stays an existing promise under either answer.

Evidence: `Defs/ThingDefs_Races/RM_Smolderback.xml`; `Source/RM_CompAmbientDose.cs:108`; `validation.py:1139`.

06. When the last paid delivery is over

Picture: The third waste load arrives and the contract ends. Casks remain on the ground. Later, the colony buries one, or loads contained casks aboard its ship. Today the reburial discovery check only reaches active tipping contracts; WasteRun's disposal destinations belong to a separate campaign mod.

Question: What responsibility should still follow the colony after the last payment, especially if it leaves the site?

Why it matters: F2/F3. The root's enduring waste and the built finite contract meet here. Physical pollution persists, but the length of the social obligation is not specified by the chosen enrichment.

My guessed answer — a guess: The waste remains the colony's problem, and completion should not silently erase the people who care about its handling. I would make any continuing obligation explicit before acceptance.

What changes in the tree: If obligations end with the contract, state that boundary and prove physical consequences continue independently. Continuing inspections require durable responsibility and a post-completion discovery case. A departure condition requires a concrete site-handoff rule and a ship-return case. No answer folds WasteRun or the Stenchlands into this biome.

Evidence: `Source/RM_RiteOfTipping.cs:113`, `:371`, `:452`; `Source/RM_WasteCaskBay.cs:225`; `design/RimMandrake/fluff_cuts_2026-10-23.md:172`.

07. Trusting a diversion

Picture: Tremors warn of a Middenshell from the east. You put waste away from the houses to draw it aside. A rock outcrop or ship deck blocks that approach; its current route is a sequence of local choices, not a guaranteed clear path. At arrival it can even choose a different edge if the warned entrance is obstructed.

Question: What should the colony be able to count on after committing that bait, and what sign should tell it that the plan is failing?

Why it matters: F1/F3. Luring is built and promised. Its reliability and the warning needed when the situation changes decide whether it is a costly tactic or a misleading line on the ground.

My guessed answer — a guess: It follows reachable waste under its existing body rules, and a changed approach is communicated while there is still time to react. I would keep uncertainty about a perfect route, but make a failed lure readable.

What changes in the tree: A dependable diversion requires a reachable-bait route and consumption/continuation case. A probabilistic or easily blocked diversion needs honest cues and a failed-plan scene. A different arrival edge needs its own preparation window; persistence at the same edge needs a blocked-entry case. The twenty-cell width and ship protections remain fixed.

Evidence: `Source/RM_Middenshell.cs:254`, `:310`, `:522`; `Source/RM_MiddenshellProcession.cs:193`; `ITEM:WASTELAND_MECHANICS_BUILD_1`.

08. Coming home from the dead giant

Picture: A dead Middenshell has become a field of bezoar seams. Miners work its edge, haulers collect the product, and exposure limits the visit. The current carcass code doses pawns beside remaining seams and forgets the carcass when the last seam is gone.

Question: What would the first expedition bring home, and what should make the colony decide “enough for today” while there is still treasure there?

Why it matters: F2. The quarry already exists. Its reward, labour and dose must produce the expedition the root promises, rather than instant riches or an unusable death zone.

My guessed answer — a guess: A worthwhile partial haul, an understandable exposure cost and a reason to return better prepared. I recommend observing the miner and hauler separately.

What changes in the tree: If exposure sets the trip length, require useful yield before an understood retreat threshold, with protected and unprotected controls. If slow excavation sets the length, require a meaningful day's progress and persistent remaining seams. If hauling is the commitment, demonstrate the whole return path. Each case retains the permanent mineable landmark until worked out; none asks whether to keep it.

Evidence: `Source/RM_Middenshell.cs:932`, `:973`; `Defs/ThingDefs_Buildings/RM_Middenshell.xml`.

These questions clarify experience and proof; none offers a built capability for removal. Full source paths, proof limits and the script audit are in record.json. Independent review status is recorded there and in NOTES.md.
