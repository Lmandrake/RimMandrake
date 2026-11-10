DRY RUN — LongShade, stages 0–1. Proposed ROOT and eight draft questions. All prose and guesses are agent-authored; only the explicitly attributed experience quotation is Mandrake's. Nothing here is approved, answered or sent through the Designer protocol.

PROPOSED ROOT

LongShade makes shade the ground you live by: in a perpetual sunset, you judge the next shelter, cross the exposed gap, and recover before going farther. The shadows you see must be the shelter that actually protects you, under the same sun and ordinary heat rules as the rest of the planet. Small life, herds, ambushers and the gloomcast turn those shelters into places with inhabitants, food and danger; a promising shadow can be a trap. You gather at the dew line, search the leavings in a rock's lee, prepare vorrel safely, and carry shade when reaching for the dead and their salvage. A wreck's shadow can be worth more than its metal. Building shelter changes the routes around your colony, and a landed ship draws wildlife to its shade without surrendering your ability to launch. The gloomcast carries a moving refuge and fertilises the places it visits; smoke haze temporarily opens crossings. The colony's story comes from deciding which shade to trust, reach, make and share, with understandable consequences when it chooses badly.

This paragraph is my proposal, built around the owner's chosen experience, not a new quotation or an approved root:

> Shade is the currency, and every crossing is a gamble. Rest, dash, rest, and never trust a shadow you didn't cast yourself.

Source: `design/RimMandrake/biome_experiences_2026-10-20.md:18`, under “The experience, in the owner's words”; chosen by card. The same sentence appears in the walk. No OWNER tsn is invented for that file-backed attribution.

My claim: the crossing and the shelter must both change a decision; the sunset is the setting for that play.
The strongest objection: a list of shade-related content can disguise ordinary wandering and generic encounters. The root succeeds only if reaching, altering and trusting shelter actually matter. It describes the intended result, not today's test results.

Start with **01 and 02 — ASK FIRST**. This is a bank, not a single eight-question turn; serve at most three after independent review, and let the early answers make later drafts unnecessary. A short phrase, a different picture, or “this doesn't matter to me” is enough. Each picture below is a written thought experiment, not a screenshot, visual mock or staged scene. The abbreviated LongShade design filenames below live in `design/Jawa/worldbuilding/biomes/`; full evidence paths are in `record.json`.

01. The moment that makes this your biome — ASK FIRST

Picture: You watch a herd rest at a rock, commit to the next shadow, and recover there. Your salvager wants a wreck in that same chain. Taking it apart buys metal and destroys a shelter. Nearby, a dark patch without a rock may be a mirrak.

Question: What is missing or wrongly weighted in the proposed ROOT when you picture playing that day?

Why it matters: F1/F2. Your experience sentence already settles the theme. The open decision is whether my paragraph captures its consequences, including the interesting things inside shade, without pretending that every creature has identical endurance.

My guess, not your answer: The route and the inhabitants of its stops are one experience. I would keep the root centred on choices about ground, with the beauty continuously present.

What changes in the tree: If the crossing carries the experience, the root leads with a real route decision and its failure case. If the inhabitants make the crossing worthwhile, it leads with discovering or fearing the destination while retaining the crossing requirement. If my framing is wrong, replace it before deriving leaves. Agreement with the experience quotation alone is not approval of my paragraph; silence leaves `root` null.

Evidence: experience file above; `longshade_shade_ideation_2026-09-29.md` §0 and §6; inventory `shade_dash`, `crawler_road`, `false_shade`.

02. The first demonstration — ASK FIRST

Picture A: A herd and a colonist use a wreck crossing; one link is salvaged, and the colony supplies replacement shelter. Picture B: A ship lands, wildlife gathers over time, then a pilot starts departure. Picture C: A party makes a Long Carry to exposed remains, with safe and dangerous-looking stops along the way.

Question: Which would you watch first to decide whether LongShade understands you, and what one failure there would end the demonstration?

Why it matters: F1/F2/F3. The earlier harbour → smoke → dew ranking was a build order. I found no owner pick binding one of these as the Designer's first showcase.

My guess, not your answer: A. It puts a price on shade through one understandable action, and tests animal behaviour and the player's use of the same route. I recommend B as a separate ship demonstration.

What changes in the tree: A makes route continuity, breaking and repair the first showcase's acceptance situation. B makes actual arrivals and departure the first situation, including an empty/no-ship control. C makes exposure, equipment and return with salvage the first situation. The named rejection becomes a requirement or sharpens an existing one. Every other built capability still receives coverage; root approval does not choose a showcase.

Evidence: `ITEM:LONGSHADE_BEDAZZLE_MECHANICS_1`, `ITEM:LONGSHADE_GPT_ENRICHMENT_1`; inventory `crawler_road`, `sun_graves`, `shipfall_ladder`, `shipfall_departure`.

03. An ordinary job in a large colony

Picture: Forty colonists have connected workshops and shelters. A hauling order now leads beyond the safe chain because its middle shelter has gone. Sun-aware path costs and a selected colonist's return-range display already exist; those alone need not stop an ordinary hauling job.

Question: At what point in that job should the colonist hand the decision back to you, and what risk should an ordinary work order be allowed to take on its own?

Why it matters: F1/F3. Constant individual rescue would make the biome a chore; silently overriding every dangerous order would erase the gamble. The source establishes current path preference, not the acceptable burden of supervising forty people.

My guess, not your answer: Routine work uses the shelter the colony has provided. A worker who cannot complete the trip safely waits and gives one useful reason; a deliberate order can accept the risk. That is a proposed behaviour, not a claim it is built.

What changes in the tree: Waiting requires a work-order refusal/pause case and an explicit-override control. Automatic detouring requires a complete safe-route case and a bounded delay. Accepting routine exposure requires a readable warning and a recovery opportunity. The answer sets the intervention rule; it does not reopen the shared heat model or remove existing pathing and range information.

Evidence: `src/RimMandrake/CreatureBehaviors/Source/RM_ShadeHop.cs`, `RM_SunHeatPatches.cs`; inventory `shade_dash`, `sun_pathing`, `shade_gear`.

04. When wildlife becomes the cost of hospitality

Picture: Your ship's shade has attracted tebbra, herds, pirrik and a gloomcast. The gathering is doing what was commissioned. You can still launch. Meanwhile workers are unloading and using the yard; this is an ordinary visit, separate from a panicked stampede.

Question: What should you have to change in that day's work because the wildlife has arrived?

Why it matters: F2/F3. A timer can announce a crowded commons without changing play. Inventing aggression or a launch obstruction would go beyond the existing promise. The remaining question is what makes the cost real during routine use.

My guess, not your answer: Arrange access and working space around the visitors, weigh easy hunting against continuing shelter and fertilisation, and occasionally wait for a large body to pass. Departure stays available.

What changes in the tree: An access cost needs an actual shared-yard work scene, with a usable alternative route. Competition for food needs a measured consumption consequence. A mostly observational gathering needs honest actual-arrival messages and no invented damage quota. Only consequences you name become core leaves; a decorative crowd cannot pass a requirement for disrupted work.

Evidence: `ITEM:LONGSHADE_GPT_ENRICHMENT_1`, `src/RimMandrake/LongShade/Source/RM_ShipfallCommons.cs`; inventory `shipfall_ladder`, `shipfall_departure`, `gloomcast_shade`, `gloomcast_dung`.

05. A fair mistake about a false shadow

Picture: An overheated traveller heads for a mirrak. Its body looks like dark ground, but it provides no real cooling. A real shadow nearby does. Losses already owe a readable sign; this question is about the decision before contact, not whether the loss is explained afterwards.

Question: What could a careful player do before committing that would make being fooled feel deserved?

Why it matters: F1/F2. A trap can be discoverable through observation, examination, or testing with a safer approach. A perfect information overlay and an unknowable surprise produce different kinds of gamble.

My guess, not your answer: Watch the caster and the animals, then deliberately inspect or test a suspicious stop. The ordinary route view should not promise that a mirrak is safe shade.

What changes in the tree: Observation as the answer requires a demonstrated behavioural clue with a genuine-shadow control. Examination requires information available before contact. Testing requires a bounded approach that does not silently commit the pawn to the attack. If the first encounter is meant to teach by injury, the recovery and aftermath become the bar. Any decision about the actual appearance must wait for a labelled visual exploration; this prose does not approve art.

Evidence: `longshade_shade_ideation_2026-09-29.md` §6.2; `src/RimMandrake/CreatureBehaviors/Source/RM_FalseShade.cs`; inventory `false_shade`, `clean_patch_tell`.

06. Rest that lasts long enough to matter

Picture: A hot miner reaches natural deep shade and needs to recover. Remaining still there can bring tollok infestation; built roof and awning shade are clean. Treatment and decay already exist. An infestation is not a separate tollok animal or a nest marked by the clean-patch feature.

Question: What useful rest should that miner normally finish before parasites make moving camp the better choice?

Why it matters: F1/F3. The intended tension is between recovering now and paying for a better shelter. An onset so fast that ordinary recovery always loses, or so slow that nobody notices, changes that tension. The constants in the code are provisional values, not your desired pace.

My guess, not your answer: A normal crossing's recovery is practical; a prolonged work camp starts paying for repeated use of old wild shade. Building shelter should feel like an improvement you chose.

What changes in the tree: Ordinary recovery defines the short-stay control; a prolonged camp defines the positive exposure case. If even one long recovery should be costly, use an already-hot pawn and demonstrate a survivable alternative. If tending everyone is the intended cost, prove treatment and work disruption instead of inventing forced evacuation. The answer tunes onset/severity and which numbers need settings, while preserving the built infestation and clean-built-shade distinction.

Evidence: `ITEM:LONGSHADE_TOLLOK_TICKS_1`, `src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:67`; inventory `tollok`, `lure_awning`, `shade_dash`.

07. When the haze gives back the ground

Picture: Smoke has stretched real shadows and made a distant job practical. Your party is still working when it clears. The current condition announces its end; its old ash pulse and sand-lock were deliberately removed and are not part of this picture.

Question: What chance to get home should a party that used the haze well have, and what mistake should leave it stranded?

Why it matters: F1/F3. A crossing window needs an intelligible closing edge. An immediate end message may explain the event without leaving a player any action to take.

My guess, not your answer: The party still needs to plan a return or carry shelter. Some indication that relief is fading should let an attentive player start back; ignoring it can leave a rescue problem.

What changes in the tree: A fading warning requires notice early enough for the stated return trip. A predictable duration requires accessible timing and a return-before/return-after control. An intentionally uncertain end requires a practical portable-shelter recovery, not a promise of a safe return. No answer restores the removed ash mechanics or permits a separate biome heat rule.

Evidence: `src/RimMandrake/LongShade/Defs/IncidentDefs/RM_SmokeHaze.xml`, `design/RimMandrake/fluff_cuts_2026-10-23.md`; inventory `smoke_haze`, `shade_gear`.

08. The crawler's shadow is about to leave

Picture: In the campaign layer, you have emptied the dead crawler. The returning clan arrives to tow it away, and people and animals have since come to depend on its shade. Reclaiming the crawler is already built; the current mechanism starts its timer when the visitors spawn at the map edge.

Question: What should the colony have time to do between the clan arriving and the shadow leaving?

Why it matters: F2/F3. The tow should change the local shelter network in a way the player can act on. A disappearance after an unseen timer is a different experience from a readable reclamation. I found no settled preparation window in the surviving ruling.

My guess, not your answer: Clear the hull, recover nearby workers, and make replacement shelter along the broken route. I would show the impending departure clearly and start useful preparation time from a meaningful arrival, rather than assume the edge-spawn timer supplies it.

What changes in the tree: Evacuation defines a scattered-worker return case and notice requirement. Rebuilding the crossing requires time and material access for a replacement shelter. If immediate loss is intended, the scene must demonstrate the available rescue afterwards. Bargaining, if you introduce it in your answer, is a new scoped capability with its own rules; none is presumed. The generic RM mechanism and the Utinni clan content keep separate coverage.

Evidence: `ITEM:LONGSHADE_JAWA_RETURN_1`, `src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:454`, `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_JawaReturnTow.xml`; inventory `crawler_hull_tow`, `crawler_road`.

These drafts received a local source and wording check only. Fresh author-independent review is still pending; no reviewer, approval, owner answer or waiver has been fabricated. Two candidate questions were struck locally: which small prey species to add (existing tebbra and sippra must be assessed first), and whether the old ash act belongs (already removed). No question offers to discard a built capability.
