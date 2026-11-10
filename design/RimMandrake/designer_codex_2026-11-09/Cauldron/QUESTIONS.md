DRY RUN — Cauldron, stages 0–1. The proposed root, questions and guesses are mine. Nothing here is approved or sent; no answer is assumed.

Existing owner experience, typed 2026-10-20 (copied from `design/RimMandrake/biome_experiences_2026-10-20.md:9`):

> The sky roils with eternal anger and lightning yet no rain ever falls. Water is acid, animals are minerals, and life twists under the load… including you.

PROPOSED ROOT — agent wording

The Cauldron is a wet, mineral forest beneath a roiling, rainless storm sky. Its open water carries acid and dissolved poisons, and its fauna carries minerals in living bodies. Its beauty and its livelihood come from chemistry that has reshaped its living things and burdens unprotected newcomers. Cold vents breathe drifting, flammable gas; their falter and the stillness of native animals announce a bloom that loads exposed bodies with metal. Thornwood pays wood and metal for slow, exposed work; mineral creatures turn the same chemistry into food, danger and rare acid-proof plate. The vexxiss tends this breathing ground while fouling water and contesting the colony's taps, and rhossak renew the groves the colony harvests. Roofs, sealed clothing, vexxith and the corroded rigs' filter technology let a colony turn dangerous liquids into useful reagents and drinking water, while acid still threatens unprotected people and ships. Living here means choosing how to work with that ecology, and how much of its burden to take into the colony.

My claim: the same chemistry joins the landscape, living things, danger and livelihood.

The strongest objection: this could describe industrial survival while understating what you meant by a person changing under the load. The proposed paragraph is a promise to discuss, not a report that every part works. In particular, the natural pools' exact liquid binding and the full study-to-production route remain unverified.

These seven drafts are a question bank. **Ask 01 and 02 first**, then use the answers to prune the rest; a real turn serves at most three. A short phrase, a different scene, or “this doesn't matter to me” is enough. No built capability is being offered for removal.

01. What happens to the person who lives here? — ASK FIRST

Picture: Written thought experiment, not a capture or staged game: Two colonists spend weeks working in the Cauldron. One shelters and seals up; the other repeatedly takes the forest's chemistry into their body. They finally leave. The current local mechanics give metal-load illness that fades and acid wounds; I found no Cauldron-specific lasting adaptation.

Question: At departure, what should be different about the second colonist, and what in my proposed root misses your meaning of “including you”?

Why it matters: F1. Your sentence can mean slow poisoning, a lasting cost, or an actual change in what a person becomes. Those require different core promises; illness alone must not silently stand in for the last one.

My guess, not your answer: I suspect you mean more than an ordinary poison meter, but I would not invent a mutation lottery. My starting guess is a readable, cumulative bodily consequence whose persistence you can describe.

What changes in the tree: If the difference is recoverable illness, bind exposure, noticeable impairment and recovery to the root and add no transformation leaf. If it is lasting damage, require the specific lasting cost and a protected control. If it is adaptation or mutation, add only the change you describe and first resolve its relationship to existing mutation systems; do not build a parallel engine by assumption. A different interpretation rewrites the root. No answer leaves it unapproved.

Evidence: `design/RimMandrake/biome_experiences_2026-10-20.md:9`.

02. The first scene that must convince you — ASK FIRST

Picture: Written scene drafts, not staged or accepted: A, a working party reads the vent falter, sees the animals go still, and gets through a bloom. B, a wild vexxiss approaches the colony's tap, drinks and interferes with it while the workers react. C, a colony uses the corroded rig's technology to turn dangerous local fluids into drinking water and useful stock. Each scene includes the forest it belongs in.

Question: Which scene would you put first to decide whether this is your Cauldron, and what single wrong moment would make you stop it?

Why it matters: F1/F2. The built mod has weather, ecology and industry. I found no owner pick of its flagship demonstration; approving a root would not pick one.

My guess, not your answer: A first: the breathing ground is the common cause of both the life and the industry. Then a different scene for the production loop and another for the giant's interference, with overlap limited to what staging needs.

What changes in the tree: Your selected scene becomes showcase 1 only after your recorded pick; its rejection case supplies the acceptance emphasis. The others remain separate feature scenes or later showcases when they add different coverage. A combined scene also needs independent feature checks and an interaction check. A new scene you describe replaces my candidate list without removing built coverage.

Evidence: `src/RimMandrake/rimflow/roles/designer_scene_contract.md`.

03. A good day after the colony has learned to live here

Picture: Written thought experiment, not a staged game: A forty-colonist base has reliable roofs, sealed work clothes, filters, cartridges and ship protection. On a good day its machines work, its workers come home, and it has something useful to show for living here.

Question: What still makes that colony plan its day around the Cauldron, and what makes the successful day worth the effort?

Why it matters: F3. The individual hazards and machines are already built. Their combined result could be satisfying chemical industry, a continuing negotiation with the wildlife, or repetitive upkeep. The intended successful life is not settled by the current rates.

My guess, not your answer: Competence should buy a workable routine and worthwhile materials. The ecology and an exposed expedition can still change the plan, while correctly used protection remains dependable. I would reject constant busywork as the whole payoff.

What changes in the tree: If successful industry is the payoff, add a sustained production scene with actual supplies, useful output and bounded labour. If the living ecology must remain the central pressure, add the named interruption and a meaningful response alongside that stable baseline. If the successful life is expeditionary, demonstrate what a trip brings home and why staying longer costs more. None of these answers weakens the already-built protection or introduces an unavoidable new tax.

Evidence: `ITEM:VEXXITH_USES_1`.

04. A capped vent during a bloom

Picture: Written thought experiment, not a staged game: A worker caps a breathing vent. Its gas cloud begins to thin and a tank starts filling. A bloom then arrives. In the current code the cap stops gas emission, but the nearby worker's bloom metal-load calculation still treats that vent as a source; ordinary acidic air is a separate danger.

Question: What should the worker be able to infer from that cap, and what should tell you which danger is still present?

Why it matters: F2. A cap can truthfully stop a flammable leak while looking like it made the whole area safe. The player must understand what changed before choosing to work beside it.

My guess, not your answer: The sealed leak and the wider weather should have distinct, honest signs. My guess is that capturing the local discharge should reduce its local contribution, while the bloom's wider burden and ordinary acid air still need shelter or gear.

What changes in the tree: If a cap also reduces the local bloom source, bind dose to capping and compare capped/uncapped workers under identical weather, holding other vents and acid exposure fixed. If it controls only the flammable gas, state that boundary and require the remaining bloom danger to be legible. If a cap can cease containing it, define that specific failure and warning before adding any overload mechanic. Existing gas containment and condensate production remain.

Evidence: `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs:385`.

05. The giant comes for the colony's tap

Picture: Written thought experiment, not a staged game: A wild vexxiss is approaching a working scaffold. It will drink and may damage the scaffold until the vent leaks again. Its tracks can be followed, but the current drinking job can begin prying without an explicit warning about the scaffold.

Question: At what moment should you understand what it is about to do, and what useful choice should still be open then?

Why it matters: F2/F3. A living rival becomes arbitrary building damage if you discover its purpose after the apparatus fails. The material, drinking and prying mechanics are already there; the missing decision is their readable encounter.

My guess, not your answer: Its approach and interest in the vent should be understandable early enough to withdraw workers, accept the lost production, or protect the equipment. I would start with the creature's readable behaviour and existing tracks rather than assume every arrival needs a letter.

What changes in the tree: If its approach is the warning, require a demonstration where its intent is readable before damage. If a message is necessary, tie it to a real approach/drink state and suppress repeats. If deliberate close work beside it is the accepted risk, bind that shorter response window and make the protected lined-tap contrast explicit. A new response you name gets its own bounded scene; no new taming, wild-shearing or bait system is inferred.

Evidence: `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs:425`.

06. Burning gas over a pool

Picture: Written thought experiment, not a staged game: One continuous cloud lies over a toxic pool and both banks. A spark catches the near bank. The gas can spread over water, but the current burning chain advances through ground fires and creates none on the water, so it can stop before the far bank.

Question: What happens above that pool, and what physical boundary should actually stop the burning cloud?

Why it matters: F2. Highly flammable gas and ground fire are different things. Choosing the wrong boundary changes whether a pool is protection, whether smoke reaches the far bank, and how the player can contain the hazard.

My guess, not your answer: A continuous flammable cloud can burn over water; the water stops a lasting ground fire, while a real break in gas or a sealed barrier stops the cloud's flame. I would demonstrate that rule beside a genuinely separated cloud.

What changes in the tree: If continuous gas carries ignition across the pool, add a gas-to-gas propagation requirement with a separated-cloud/closed-barrier control and toxic-smoke observations. If the pool reliably stops it, bind that rule and give the player a readable physical explanation. If only dense or short spans carry it, specify the visible condition and test both sides. This does not change the existing requirement that vent gas burns into toxic smoke.

Evidence: `src/RimMandrake/Cauldron/Source/RM_VentGas.cs:210`.

07. A forest after a week of profitable work

Picture: Written thought experiment, not a staged game: The colony sends a serious forestry party into mature thornwood over several days. Steel and wood come home; the harvested stand changes. Bound rhossak still sprout the ground, and groups can root new thornwood. Vexxith is a different supply, sheared from a living tame giant on a long cycle.

Question: At the end of that week, what should show that the expedition paid, and what price should be visible in the forest and the colony's work?

Why it matters: F3. A small metal stack can pass a harvest test without making the biome worth working. Regrowth and grove animals can also erase the cost so quickly that the forest becomes a free resource machine. The right trade-off needs a picture of labour and aftermath.

My guess, not your answer: A worthwhile haul for a real commitment of workers and exposed time, with a visibly worked stand that takes time and living ecology to renew. I would keep the rewards from forestry and living vexxiss distinct rather than make either replace the other.

What changes in the tree: If extraction should visibly deplete old stands, require a before/after work-and-yield scene and a later recovery observation with ordinary growth separated from rhossak effects. If tending groves is the intended sustainable livelihood, require an actual manageable cycle and its labour/material accounting. If forestry is mainly a short visit's windfall, bind that payoff without promising it can sustain a permanent industrial colony. Existing harvesting, binding, sprouting, rooting and shearing stay covered.

Evidence: `ITEM:CAULDRON_RULED_CONTENT_1`.

Already settled and excluded from the bank: dry thunderstorms are welcome; the falter target is about one in-game hour; the vents are chemical and add no heat; the martyr tree was removed; the Filter-Works, ruins and Oomo shrine are in; seismometer, bespoke audio sourcing and scab-scrapers are not new questions. Vexxith remains a strong general material. Existing imports and owner-kept art are not up for culling.

These pictures are written thought experiments. If an answer turns on the actual look or motion of a cue, show a labelled mock or exploration before binding that appearance; prose is not visual acceptance. Source and proof distinctions, the three failure modes and the scene audit are in record.json. Independent author-review has not run, so this bank remains draft.

