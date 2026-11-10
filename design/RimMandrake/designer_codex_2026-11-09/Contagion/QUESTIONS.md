DRY RUN — Contagion, stages 0 and 1. All proposal wording and guesses below are agent text. Nothing is approved or sent.

Existing owner-chosen anchor, recorded on 2026-10-20: “A mutation engine under a red lid, where nothing is finished, including you. When the sky clears, run.” Source: `design/RimMandrake/biome_experiences_2026-10-20.md:10`. This is his existing choice, not approval of the paragraph below.

PROPOSED ROOT — agent proposal

The Contagion is a mutation engine under a red storm: the landscape keeps making unfinished life, and a visit can leave a colonist unfinished too. The player reads the Gawpsacks sinking and the Rattlegropes shaking, then makes a costly choice when the cloud tears: reach shelter, or use the lifted fog while UV-shy life retreats and armored predators remain outside. Exposure brings unwanted changes; a Sunbeam can stop the current progression, but cannot undo what grew or protect the next trip. The same biology offers reasons to venture in: a Bloody Mess can consume itself growing donor-matched organs and natural limbs, short-lived Unfinished can be scanned for Helix contracts, and a Coalescence left through a long Bloom becomes a growing threat whose Burn collapse yields unusual tissue. Deliberately installed grown limbs exchange an ability for a lasting cost, with danger again when removed. Flesh-like plants, flying skin creatures, drifting gas sacs and the traces of death make this a living place rather than a red ordinary forest. The biome offers no forage; sterile mulch is a practical reward. These connected promises need separate demonstrations of the sky, bodily consequences and expeditions.

My claim: the sky clock and the price of unfinished biology join the mod's expeditions and daily life.
The strongest objection: the words can promise a complete living cycle while today's code still has reactive flight to shelter, immediate slime remains and incomplete visual/medical proof. This is a proposed promise, not a claim that the mod passes.

These eight drafts are a bank, not one turn of eight questions. Start with 01–02, then ask at most three at a time as the answers make the others useful. Each picture is a written thought experiment, not a screenshot, staged scene or acceptance result. A phrase, a different picture, or “this doesn't matter to me” is enough; silence changes nothing.

01. What the root has to get right — **ASK FIRST**

Picture: After a trip under the red storm, a colonist comes home with a scan and useful tissue, but starts changing. Later the cloud opens and the colony rushes between shelters.

Question: What feels wrong or missing in that story and the proposed root, given your chosen sentence about being unfinished and running when the sky clears?

Why it matters: F1/F2: a list of grotesque creatures and mechanics could still miss why the place is worth entering and frightening to inhabit.

My guess, not your answer: The weather and bodily cost lead; expeditions give the player a reason to accept that danger. I recommend making those the through-line.

What changes in the tree: If the costly expedition leads, reorder the root and connect its success to lasting bodily consequences. If living under the sky clock leads, begin with ordinary colony work repeatedly interrupted by the sky. If unfinished life itself leads, begin with its visible cycles. All built branches remain covered. A correction changes dependent claims; silence approves nothing.

Grounding: `design/RimMandrake/biome_experiences_2026-10-20.md:10`.

02. The first demonstration — **ASK FIRST**

Picture: A: ordinary workers notice the tells and shelter through a Burn, followed by a touched patient being treated. B: a genome expedition ends with a matched natural part being installed. C: a dangerous scan fills a Helix contract. D: a growing Coalescence is deliberately caught by a forced Burn. These are separate candidate demonstrations.

Question: Which demonstration would you put first, and what single failure in it would make you stop the review?

Why it matters: F1/F2/F3: the owner-chosen experience is on record, but a flagship pick and concrete rejection case are not.

My guess, not your answer: A first: show that the sky is dangerous and that what happens to people matters. I recommend B and C as distinct later scenes, with D proving its own threat and payoff.

What changes in the tree: The pick binds showcase 1 only after a real owner decision. The stated failure becomes a candidate acceptance requirement. Other capabilities retain separate scenes; later showcases must add different functionality, and ordinary checks cover the remainder. Root approval alone never becomes a flagship pick.

Grounding: `src/RimMandrake/rimflow/roles/designer_scene_contract.md`.

03. What a useful Burn lets you attempt

Picture: A prepared colonist has a roofed refuge on each side of a red clearing. During the Bloom a predator and the fog make crossing dangerous. The Burn clears the shot and drives UV-shy creatures inward, while Scaldhides remain outside and the traveller takes exposure.

Question: What should a well-prepared traveller be able to get done between those shelters before the light becomes too costly?

Why it matters: F1: the older sheet calls the Burn a travel window while your chosen line says run. Both can be true, but a harmless sunny interval or an unusable trap would miss the tension.

My guess, not your answer: One purposeful dash or a brief rescue, paid for by exposure, rather than routine safe outdoor work. I recommend a crossing that is clearly worse for an unprepared traveller.

What changes in the tree: A brief dash needs measured distance, shelters, injury and mutation exposure in one crossing scene. A rescue needs a carrying case and enough time for the return. A longer sortie needs a longer exposure-budget demonstration. An emergency-only picture changes how the root describes the tactical window while retaining the lifted fog and existing weapon behavior.

Grounding: `design/Jawa/worldbuilding/biomes/the_contagion.md`.

04. Enough warning to make a decision

Picture: A forty-colonist settlement is spread between a workshop, a near field and a distant work party. Gawpsacks sink and Rattlegropes shake. A natural Burn follows; the current lead is about twenty seconds at normal speed. In a separate case, a warmed Repulsor starts a whole-map Burn without that natural tell sequence.

Question: When the sky opens, which people should reasonably have reached safety, and what should the distant work party know before the colony starts its own Burn?

Why it matters: F1/F3: a cue can exist without giving a useful choice, and forced whole-map weather can surprise people far from the machine.

My guess, not your answer: People near a planned refuge can shelter; a remote expedition may have to improvise. I recommend an honest indication that switching the Repulsor affects everyone on the map.

What changes in the tree: Near-refuge safety sets a warning-window case with ordinary walking. Recall of the distant party requires longer lead or a planned remote refuge and a demonstration. A clear device-state explanation adds an interface requirement; a pre-activation warning adds a distinct forced-Burn scene. No automatic rescue or immunity is inferred.

Grounding: `src/RimMandrake/Contagion/Source/RM_MapComponent_ContagionSky.cs`.

05. The warning before the body changes

Picture: A worker spends time outside in the Bloom and then goes indoors. The current build keeps the touched condition; later it can grow another mutation. A Sunbeam stops that progression, leaves existing changes and gives no future protection, as already ruled.

Question: Before the first new body part or harmful change appears, what should make you decide this worker needs treatment now?

Why it matters: F2/F3: hidden accumulation can turn the ruled danger into a surprise punishment. A health entry alone may not be enough in a large colony.

My guess, not your answer: A readable early health state and a noticeable transition to active change, without repeated letters for every tiny exposure. I recommend judging the first warning and the next action together.

What changes in the tree: If the health panel is sufficient, require an intelligible progression state and no extra alert. If a visible symptom matters, define it through a labelled mock before visual acceptance. If an alert matters, bind a threshold and repetition rule. Existing exposure, arrest, persistence and reinfection behavior are not being offered for removal.

Grounding: `src/RimMandrake/Contagion/Source/RM_ContagionTouched.cs`.

06. An expedition that earns its wait

Picture: A colonist needs a natural leg. The team injects that colonist's genome into a Bloody Mess and comes back four days later. The host dies producing a matched batch of ordinary organs and limbs, but this batch has no leg. This is the current random batch, not a proposed targeted-growth machine.

Question: What has to come home from that trip for it to feel like progress worth another expedition?

Why it matters: F2: the one-use host is already ruled, but useful output and the cost of reaching and returning to it need a player-facing bar.

My guess, not your answer: Other genuinely useful or sellable matched tissue can make a failed leg roll worthwhile, provided the risk and return trip are readable. I recommend judging the whole expedition rather than the instant batch spawn.

What changes in the tree: A useful mixed haul needs a representative batch and a clear use or sale after return. Progress toward this patient's specific recovery needs a defined route beyond hoping at the next host; any added route must be argued separately. A very harsh lottery needs that cost signalled before commitment. The one-use host, normal mixed batch and sellable output remain built coverage.

Grounding: `ITEM:CONTAGION_GENOME_ORGAN_GROWING_1`.

07. A bargain you notice after surgery

Picture: A brawler fitted with a Pillar Arm wins a fight that a natural arm would have lost, then returns to an ordinary day of work and meals. Its clumsy manipulation, weight and extra hunger are already built. All five unusual limbs are built; removing one releases an Unfinished.

Question: What ordinary task should make you feel the price of that better fighter, and how disruptive should that price be during the following day?

Why it matters: F2/F3: a positive stat and a negative stat can coexist while the limb still plays as a free upgrade. The lasting costs are promised; their felt size remains provisional.

My guess, not your answer: It should force a real reassignment away from skilled hand work, plus a food burden, without making the pawn useless. I recommend comparing one unchanged day before surgery with one after.

What changes in the tree: A changed work role makes work completion and reassignment the acceptance example. A resource burden makes food and walking costs part of it. Frequent disruption needs an appropriate event case for the affected limb. The gain remains; tune and prove the lasting cost. No new requirement is derived for every stat, and no limb is offered for removal.

Grounding: `design/Jawa/worldbuilding/biomes/contagion_grown_limbs_2026-09-30.md`.

08. The reason to stop a Coalescence growing

Picture: A Coalescence grows through a long Bloom. More Unfinished walk into it; it sends mad ones out. The colony could start the Repulsor now, or wait for a larger collapse and more tissue. Its emitted manhunter count is currently capped, so a higher stage can become merely a better payout behind the same defense.

Question: What should make waiting for one more stage a difficult choice for a colony that can already handle the current attackers?

Why it matters: F1/F2: staged mass and a sample formula can pass while the giant never changes a decision. The cost of waiting needs to be concrete.

My guess, not your answer: More pressure on access to the site and on the workers who must recover the tissue, rather than a consequence unrelated to the creature. I recommend showing the same colony at two stages.

What changes in the tree: If stronger attacks are the pressure, demonstrate the changed threat at the same defense. If access is the pressure, show the threatened route and recovery trip. If waiting is meant to be a reward for containing it, require meaningful containment and retain bounded emissions. The growth, absorption, Burn collapse and payout remain independent promises.

Grounding: `src/RimMandrake/Contagion/Source/Building_RM_Coalescence.cs`.

No built capability is offered for removal. The rooted experience, consumable host, exposure sources, arrest without reversal, visible tells and plain fertilizer are already grounded; these questions clarify the remaining play expectations. Local evidence/wording review only; the role's fresh-agent review has not run, so all asks remain drafts. No guess has been stored as an owner answer.

