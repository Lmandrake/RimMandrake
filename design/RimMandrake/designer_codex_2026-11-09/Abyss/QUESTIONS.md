DRY RUN — Abyss, stages 0 and 1. The proposed root, pictures and guesses are agent-authored. Nothing is approved or sent.

PROPOSED ROOT

The Abyss makes shelter and dread come from the same Dark. It shields a fugitive ship while hiding terrors close enough to matter; warmth opens clear air, living lamps sustain the colony, and a rare Unveiling turns the country into a moment of wonder before the Dark closes again. Beauty and danger both recur, and a familiar safe routine can become frightening very quickly. Living here means tending light, reading the gusts and the creatures that answer them, gathering food and the fallen grain that becomes fuel, and staying quiet when a searching probe passes. Going deeper offers a greater temptation: salvage a rescue wreck and retrieve an egg and a great bone beside a sleeping, landscape-sized summ whose waking means flight. The haul restores the player's own ship, and raising the summ brings power together with hunger, aggression and growing demands. Rings, exchanges and dreams make a long stay feel increasingly personal, while the Nhaleth remain a fear that nobody can prove. Each of these built promises needs its own demonstration; feature switches and tuning belong to the experience.

Grounding: Mandrake's chosen experience is recorded at `design/RimMandrake/biome_experiences_2026-10-20.md:7` (typed, 2026-10-20). Its protection, nearby terrors, recurring beauty and fear of staying are the foundation here. This paragraph is my proposed expression of that intent, not his words and not a report that all of it passes.

My claim: the Dark is valuable enough to stay in and frightening enough to make that choice costly.
The strongest objection: the implementation can deliver isolated penalties, brighter weather and loot without delivering that emotional turn. The inventory records those gaps separately from built content.

These nine questions are a draft bank. Ask **01 and 02 first**, then at most three at a time as the answers make the rest useful. A short phrase, another scene, or “this doesn't matter to me” is enough. No answer is assumed. All pictures below are written thought experiments, not captures, visual mockups or accepted scenes. A later choice about appearance or motion needs an actual labelled picture before it can bind the tree.

01. What the root must get right — ASK FIRST

Picture: A fugitive crew first welcomes the darkness around its ship. Later the air clears and reveals a beautiful country; when it closes again, something dangerous is much nearer than the crew thought. A month later, familiar rings and dreams no longer feel harmless.

Question: Which turn in that little story carries the Abyss for you, and where does the proposed root give the wrong impression?

Why it matters: F1/F2. Your experience sentence joins protection, beauty, terror and the fear of staying. A catalogue of hazards would miss that relationship.

My guess, not your answer: Protection draws the crew in; repeated beauty makes staying tempting; familiar things turning threatening make departure difficult. I would make that cycle the root's test.

What changes in the tree: If the protection-to-dread turn leads, organise the root and its main interaction check around refuge becoming exposure. If beauty-to-nightmare leads, make the Unveiling and its aftermath the central interaction. If long familiarity leads, make the existing signs and dreams carry that through-line. All built capabilities remain covered. A different account rewrites the root; silence approves nothing.

Evidence: `design/RimMandrake/biome_experiences_2026-10-20.md:7`.

02. The first demonstration — ASK FIRST

Picture: Three proposed demonstrations: A, a quiet ship and an operating settlement through Dark, Unveiling and a probe search; B, a farm lit by living plants, with gust-feeding animals and a light-thief disrupting work; C, an expedition deciding how much wreck salvage and brood loot to carry out before the mother wakes.

Question: Which would you watch first to decide whether we understood the Abyss, and what failure there would make the demonstration stop?

Why it matters: F1/F2/F3. There is no owner flagship pick in the evidence read. The most dramatic set piece could hide a weak everyday biome.

My guess, not your answer: A first: prove that the Dark is both refuge and danger. B and C then show different reasons to stay and to venture deeper.

What changes in the tree: The chosen scene becomes showcase 1 only after a recorded owner pick. The other scenes retain their own acceptance and interaction checks. A rejection case becomes a core bar if it is decisive; an aesthetic rejection needs a labelled visual exploration before its appearance is bound. Root approval alone is not a flagship choice.

Evidence: `src/RimMandrake/Abyss/validation.py:802`.

03. What the Unveiling changes

Picture: The Dark lifts while a worker is outside and a predator is nearby. Rings stand revealed; lamps regain their reach, ordinary sight and shooting improve, and falling grain increases. The map does not magically reveal unexplored secrets. Soon the Dark returns.

Question: What would make you send people out during that opening, and what change would make you call them back?

Why it matters: F1/F2. The built weather can be a brighter interval without creating the tempting, frightening reversal in your sentence. The decision to use it is still undefined.

My guess, not your answer: Use the opening to read the nearby country or retrieve something previously too risky; retreat when the returning Dark threatens to strand the party. I would let existing dangers change the calculation rather than invent a compulsory attack at every opening.

What changes in the tree: A useful reconnaissance window needs an outing with an ordinary-sight control and a readable return transition. A resource window needs a worthwhile retrieval and a measured way home. If the opening should itself expose the colony to danger, add that specific existing-threat interaction. No answer authorises global secret revelation or a new attack schedule.

Evidence: `src/RimMandrake/Abyss/Source/RM_MapComponentDark.cs:112`.

04. A quiet refuge that still has a working colony

Picture: Forty colonists have settled around a landed gravship. The current cover code treats at most four lit building lamps across the whole map as quiet; living glow plants are not counted. Probes still search, and cover eventually wears thin. The orbital and raid consequences are not yet verified end to end.

Question: While lying low, what ordinary work should the colony still manage, and what activity should force a deliberate risk of being found?

Why it matters: F1/F3. The existing cover needs a believable cost. A map-wide lamp count can make a small outlying workshop decide the fate of the whole ship.

My guess, not your answer: Food, repairs and careful hauling remain possible around living light; conspicuous activity near the ship or a passing scout forces a choice. I would judge a complete day's work rather than approve four lamps as a magic number.

What changes in the tree: If concealment is about the ship's immediate surroundings, the leaf needs a bounded ship area and a distant-work control. If it is the whole settlement's signature, keep a map-wide case and require the player to understand why distant activity matters. If particular work is the tell, specify that work and its warning. Existing probes, temporary cover, trade isolation and launch exposure remain obligations.

Evidence: `src/RimMandrake/Abyss/Source/RM_MapComponentShipCover.cs:67`.

05. A light-thief reaches the farm

Picture: A planted lamp lights a farm and a path. Wild krizzaks settle near it, its reach contracts, and an ishvarith can approach closer as darkness returns. Heat can interrupt feeding and the light recovers after the thieves leave. Power and the lamp itself remain intact.

Question: What should a well-run colony do when that happens, and how much of its working day should that response consume?

Why it matters: F2/F3. The built interactions might create an interesting husbandry problem or repeated busywork. The current feed and recovery numbers alone cannot distinguish them.

My guess, not your answer: Notice one local failure, drive the thieves off or use heat, then resume work; a neglected swarm can threaten the perimeter, but every lamp should not demand constant manual attention.

What changes in the tree: A quick local intervention needs a readable cause and a recovery scene before the next work cycle. A recurring husbandry task needs sustainable labour at forty-colonist scale. An expedition-level threat needs a distinct exposed-field scene with a meaningful way back. This sets response time and workload acceptance without asking whether the light-thief stays.

Evidence: `src/RimMandrake/Abyss/Source/RM_CompKrizzak.cs:29`.

06. The last sensible haul from the lair

Picture: The expedition has taken some fittings and is hauling a great bone when the mother's breathing changes and the stone rumbles. Another salvage bill is almost finished; the egg is still beside her. Her exact waking threshold stays hidden, and learning it by reloading is already allowed.

Question: At that rumble, what can a careful expedition reasonably finish before escape becomes a desperate gamble?

Why it matters: F2. A warning can exist in code yet leave no useful action between hearing it and being attacked. Several workers can add pressure nearly together.

My guess, not your answer: Stop taking new things, finish securing what is already in hand, and make a dangerous retreat; insisting on the egg as well risks waking her. I would test simultaneous workers and a slow bone hauler.

What changes in the tree: An immediate-retreat answer needs a warning-to-exit opportunity with a loaded party. Finishing one current task needs that task's duration and concurrent-pressure control. A warning that can already be too late needs a clearly distinct earlier actionable sign. None reveals the numerical threshold, weakens her ruled strength, or asks again whether save/load is acceptable.

Evidence: `src/RimMandrake/Abyss/Source/RM_BroodWakeLogic.cs:109`.

07. Restoring the ship's glory

Picture: The crew returns with rescue-ship fittings. The current implementation accepts four kinds and spends a repair budget on damaged colony buildings standing on ship substructure; three foreign fittings are refused in words and remain saleable or smeltable loot. It never creates a second ship.

Question: After a successful haul, what change aboard your own ship would make you say that some of its lost glory has returned?

Why it matters: F2/F3. The repair machinery exists, but restoring generic hit points may be less than the payoff your earlier description intended.

My guess, not your answer: Recognisably worn fittings become sound again, with enough restored to justify that expedition. I would first demonstrate that using an accepted part restores the ship itself.

What changes in the tree: If condition repair is the payoff, bind visible damage/condition and actual repair on the correct ship, plus an undamaged control. If named damaged systems must return to service, add those specific restoration effects and tests while preserving the repair-only boundary. If the presentation supplies the missing feeling, explore it with a labelled mock before adding an appearance requirement. Refused loot remains useful in each case.

Evidence: `src/RimMandrake/Abyss/Source/RM_ShipWreck.cs:119`.

08. What staying too long means

Picture: The colony finds tidy rings, then an unwatched offering is exchanged, then someone dreams of no longer needing the light. In the current code the dream becomes eligible after the map is thirty days old; that is not a record of how long this colonist has lived here. Nothing ever proves who made the signs.

Question: What should become different for a colony that stays a season, compared with travellers who leave after a few nights?

Why it matters: F2/F3. Your last sentence can mean accumulated dread or a changing pattern of consequences. Neither a literal reveal nor an automatic punishment follows from it.

My guess, not your answer: The signs become harder to dismiss as they attach to familiar places and people; the fear deepens without confirming the Nhaleth or transforming a colonist into one.

What changes in the tree: If familiarity alone carries it, give the existing signs a long-stay scene and add no escalation clock. If time changes the pattern, specify that change and whether time follows the person or the settlement; use new-arrival and revisit controls. If a costly consequence is needed, define its readable sign and limit before adding it. The no-sighting/no-certain-proof boundary holds throughout.

Evidence: `design/RimMandrake/biome_experiences_2026-10-20.md:7`.

09. The summ that becomes too much

Picture: The great bone is aboard, the egg bonds, and the summing becomes a powerful defender. Later it is eating through the food reserve and killing wildlife or livestock. Constant troublesome growth is already your requirement; the current finite life stages do not yet fulfil it.

Question: What should make this beast worth taking with you, and what change in the colony's daily life would show that its growing cost is real?

Why it matters: F2/F3. Large health numbers and a hunger modifier can coexist without producing the bane-and-boon story already ruled.

My guess, not your answer: It saves the crew in a fight they could not otherwise survive, then forces real changes to feeding, animal safety and ship space. I would judge the same bonded animal at successive ages.

What changes in the tree: A combat payoff needs an encounter where its strength changes the outcome, alongside an ordinary-animal control. A transport or work payoff needs that particular useful job instead. Food pressure binds a supply budget; animal safety binds hunting and readable losses; space pressure binds physical accommodation. These choose demonstrations and consequences, never reopen the bone requirement, aggression or continuous growth.

Evidence: `infrastructure/state/items/ABYSS_LIGHTFALL_BROOD_WRECK_1.md`.

These drafts have had a local evidence and wording check. Fresh author-independent review has not run, so none is marked reviewed-pass or sent. No built capability is offered for removal. Known correctness faults in NOTES.md are reading findings, not questions for you to solve.

