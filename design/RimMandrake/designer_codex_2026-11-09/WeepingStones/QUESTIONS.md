DRY RUN — WeepingStones, stages 0 and 1. The proposed root, pictures, questions and guesses are agent text. Nothing here is an answer, approval or ledger entry.

PROPOSED ROOT

WeepingStones makes bright, dry stone and secret wet shade into places where life gathers, and where tending a pool changes what lives in it. Its alien plants, grazers, fliers and caravan beasts give the oasis a life of its own. At the water, predators leave drinkers alone and a guilty attack brings the nearby wildlife against the attacker's faction; the dangerous work is in the fish pens. Moisture farmers catch breeders, stock and feed their pools, read their health, and choose what to harvest. Neglect and crowding can turn their stock into a vhorrin; rescuing the farm produces a feast, while other delicious catches carry a real cost in a colonist's peace of mind. Dewgourds, spice, dewsilk and huldu fur make the place worth working and trading with. The unique old gorrask carries a working condenser and a seasonal oasis: the colony can guide it, sell its next settling place, or kill it to take the machine onto a ship. Its two optional quests put money and captivity against protecting its freedom. These promises belong together, but the farm, the truce and the walking oasis each need their own demonstration.

The root is my expansion of the experience you chose by card on 2026-10-20, recorded in `design/RimMandrake/biome_experiences_2026-10-20.md`, WeepingStones row: “Bright dry stone and secret weeping shade, where every pool is a gathering. Keep the oasis healthy, or it breeds something wrong.” That existing sentence is yours; this proposed paragraph is mine. The walk still calls its north star DRAFT; choosing the experience sentence did not approve this new root or a set of acceptance bars.

My claim: a gathering around water, and the farmer's responsibility for what it breeds, join the place and its mechanics.
The strongest objection: the root may make an ordinary oasis sound like a simulated water budget. That larger born-and-dying-water proposal was rejected. Here, farm health concerns its living stock; the crab's seasonal pool is a separate, already built promise. Nor does the paragraph claim that all these experiences have passed in game.

Eight drafts form a bank. Ask **01 and 02 first**, then at most three useful questions in a turn. A phrase, a different scene, or “this doesn't matter to me” is enough. No reply is assumed. I recommend the working farm first: it directly tests the chosen experience, including the failure and the recovery, without making the rare crab carry the whole biome.

01. ASK FIRST — What makes this place itself?

Picture (written thought experiment, not a capture): A traveller leaves bright stone, reaches a shaded pool crowded with living things, and rests under the truce. Beside it a farmer finds the stock thinning, changes the day's work, and later serves a meal from the rescued pen. Farther off, the old crab is beginning its next move.

Question: Which part makes this the Weeping Stones to you, and where does the proposed root give the wrong impression?

Why it matters: F1/F2/F3. The chosen experience already gives the direction. This checks my expansion: the place could become a list of production jobs, or the giant could overshadow ordinary life there.

My guess — not your answer: The contrast between harsh stone, shared water and troubling husbandry is the foundation; the crab is its exceptional story. I recommend leading with the ordinary oasis.

What changes in the tree: If the gathering leads, put the shared-water encounter before the farm in the root and main walk. If the farm leads, centre the root and main walk on tending, trouble and recovery. If the crab leads, reorder the explanation around its choices while retaining the farm and truce's separate coverage. Any correction rewrites the dependent claims; nothing becomes an approved root without your explicit approval.

Basis: chosen experience file; frozen sheet §§1, 4–6; stocked-pool spec header; `OWNER:1790972004219944071` for the giant's chosen story.

02. ASK FIRST — The first demonstration

Picture (three written scene drafts, not staged play): A, a working farm shown healthy, then neglected, then rescued, ending at the stove and dinner table. B, a crowded wild pool where predator and prey coexist, followed by a clearly attributable guilty attack and its response. C, the old crab makes a pool, moves, and presents its three choices; the capture and protection quests are separate branches.

Question: Which would you watch first to decide whether the mod understands you, and what single failure there would end the demonstration?

Why it matters: F1/F2/F3. An approved experience sentence or giant story is not a recorded pick of showcase 1. A useful demonstration needs a rejection case, not merely objects on a map.

My guess — not your answer: A, especially seeing the health change before it becomes a monster. I recommend B next and C as its own longer demonstration.

What changes in the tree: The chosen scene becomes the flagship only after a recorded pick. Its failure becomes an acceptance condition attached to the relevant promise. Other capabilities retain their own scenes; the dinner is not proof that the farm reproduces, and wildlife attacking a faction is not proof that normal hunts are suppressed. Later showcases must add different functionality; the current script does not yet stage all these stories.

Basis: scene contract; `validation.py::job_feed`, `job_harvest`, `job_cull`, `truce_hunt_suppression`, `walking_condenser`.

03. A farm that can run while you look elsewhere

Picture (written thought experiment): Your forty-colonist settlement has a gentle breeding pool, a pen of biters for volume, and a pen of expensive beasts. Handlers are assigned animal work. You spend the day building elsewhere. The current work givers choose the nearest pen for new stock and offer any eligible resident for harvest; they have no per-pen stock target or harvest limit.

Question: Before leaving those handlers to work, what decisions would you expect to give them once, and which decisions should bring you back to the pool?

Why it matters: F1. A farm can have five working jobs and still demand constant interruption, or quietly turn its last breeder into meat. The existing husbandry promise settles that the farm exists, but not how the player directs a colony-scale routine.

My guess — not your answer: Set the species mix and a safe breeding reserve once; return for a worsening pool, an escape or a deliberate big harvest. I recommend decisions per pen rather than a series of orders to individual fish.

What changes in the tree: Targets and reserves require pen policies and an unattended-cycle scene. Individual harvest orders require a clear selection and command path plus a routine-work demonstration at this scale. If a named keeper makes the decisions, require that keeper's assignment and authority to be visible. Every answer preserves netting, stocking, feeding, harvesting, culling and their risks; none licenses ordinary work to erase the farm unintentionally.

Basis: `RM_WorkGiver_StockPoolPen.cs:61`, `RM_WorkGiver_HarvestPoolPen.cs:64`, stocked-pool spec §3.

04. The last useful warning

Picture (written sequence, not proposed artwork): Yesterday the pen was busy. Today its rings are thin. Tomorrow one broad, slow ring replaces them. At present those states are inspect text, updated by a pulse; there is no ring overlay. The existing spec already calls for health readable on the water, without opening an inspector.

Question: At which moment should a careful farmer still be able to put things right through ordinary tending, and what would make the later cull feel like the result of a missed warning?

Why it matters: F1. “Keep it healthy, or it breeds something wrong” needs a chance to understand and respond. A correct state label shown only after an unpredictable conversion would miss the experience.

My guess — not your answer: Thin rings give a meaningful working interval to feed or relieve crowding; the broad ring says ordinary tending was too late and now a cull is needed. I recommend testing the warning against handlers already busy with normal work.

What changes in the tree: A warning interval requires a controlled healthy → stressed → danger sequence with an intervention arm. An abrupt turn, if that is the intended story, instead needs the earlier risk conditions to be legible and the remaining rescue action clear. Feeding and crowding need distinct causes in the proof. Your answer sets the response opportunity; an actual visual mock is still owed before binding how the rings look. The established on-water gauge is not being reopened as optional.

Basis: chosen experience; stocked-pool spec §§2d, 3; `RM_PoolKernel.cs:54`; `RM_PoolBody.cs:82`.

05. The creature that seems to run the pool

Picture (written thought experiment): Two otherwise matching pens are tended alike. One holds an ivvol, the flat creature with the watching eyes. Its current description says those pens have fewer escapes and never grow a vhorrin, but the pool code gives an ivvol no special effect. The original spec explicitly left a real benefit versus farmer superstition unresolved.

Question: When a farmer stakes the safety of a valuable pen on an ivvol, what should the next bad season teach them about that belief?

Why it matters: F1/F2. This changes the species-mix decision and the meaning of eating the animal that supposedly looked after the farm. Current prose and mechanics disagree; neither is your answer to the original open question.

My guess — not your answer: A modest real benefit, with no immunity to gross neglect. I recommend making it helpful enough to notice while keeping responsibility with the farmer; the old absolute “no vhorrin” sentence would need to match whichever rule you choose.

What changes in the tree: A real benefit needs species-aware pool behaviour and matched pens that isolate its effect. A fallible belief needs explicitly attributed folklore and no hidden bonus requirement. Absolute protection, if chosen, needs an exact boundary against crowding, hunger, reload and removing the ivvol. No answer changes the creature's existing presence, catch, meat or thoughts.

Basis: stocked-pool spec §6 question 6; `RM_StockedPoolFauna.xml` ivvol description; `RM_MapComponent_PoolStock.cs::Pulse`.

06. Where “guide it onto your land” lands it

Picture (written layout, not a UI mock): Your home area contains a dry workshop yard, a planted garden and an open strip of stony ground. The old crab is ready to move. Today Guide chooses a random home-area cell and then nearby reachable ground; it does not ask you to point to the strip. Pool growth protects built floors, foundations and buildings, but can still change ordinary soil.

Question: What would you expect to tell the crab so its next pool arrives where you meant it to?

Why it matters: F3. “Onto your land” does not settle whether the bargain is precise placement, broad guidance or accepting an animal's choice. A welcome oasis can be a bad surprise beside a garden.

My guess — not your answer: Point to a rough settling place, see whether it can reach it, and let the crab choose within that patch. I recommend clear refusal if the intended patch cannot support its pool.

What changes in the tree: Pointing to a site needs a target action and reachability/pool-space feedback. Choosing a broad area needs an area-bound destination rule. Letting the crab choose needs a preview or other clear expectation before committing. Each needs a blocked-site control and a scene with nearby working colony ground. Show a labelled UI mock before binding the interaction's appearance; these words are not that mock.

Basis: `RM_WalkingCondenser.cs:260`, `:283`, `:140`; `ITEM:WEEPINGSTONES_WALKING_CONDENSER_1`.

07. When the settling-place sale is earned

Picture (written thought experiment): A faction buys the crab's next season at its inhabited settlement, which respects the existing claim law. Before arrival, the crab dies or cannot get there. Today's Sell action pays immediately and records the buyer, but I found no delivery step that makes the buyer's season pool happen.

Question: What has the colony promised that buyer, and what should happen to the payment when that promise cannot be fulfilled?

Why it matters: F3. The pool at the buyer's settlement is already promised; making it real is owed work, not a new feature to vote on. The unresolved part is who bears the risk between the sale and fulfilment.

My guess — not your answer: Payment buys an actual season of water; failed delivery returns the money or creates a clear debt. I recommend a visible unfulfilled obligation rather than an unconditional payout.

What changes in the tree: Payment on arrival needs a pending sale and arrival-triggered settlement. Advance payment with liability needs refund/debt and failure handling. A paid guarantee needs a defined replacement obligation. If the sale is instead explicitly a risky reservation, the offer must say so and define its cancellation terms. Every answer still owes the built sale's promised destination and season; none authorises a payment-only substitute or an absentee toll.

Basis: `RM_WalkingCondenser.cs:298`; `RM_WalkingCondenser.xml` sale text; frozen sheet claim law; walking-condenser item §3.

08. Alive, but no longer free

Picture (written counterexample): You accept the farmers' protection quest, wall the old crab inside the colony and defeat both hunter waves. The timer finishes with the crab alive behind those walls. The current quest's success route is its timer; it does not demonstrate the crab walking on or the farmers actually sharing its pool.

Question: What would the farmers need to see before they could honestly call that season “kept free”?

Why it matters: F3. Your choice already opposes captivity to keeping it free. “Not dead when the timer ends” may be a cheaper, wrong version of that promise. A wall can also be temporary protection, so the exact boundary matters.

My guess — not your answer: Temporary shelter is fair, but success means it can leave under its own power and the farmers get the promised season at its water. I recommend proving an open route and an actual departure, rather than requiring it to survive every attack without help.

What changes in the tree: A departure requirement needs an unobstructed route and observed movement after protection. Freedom to choose without a forced departure needs a defined confinement check. Temporary confinement needs a release deadline and a failure or delay state if the colony refuses. If survival alone expresses your intent, name that narrower success honestly while retaining the existing story's promised aftermath as coverage debt. No option offers to remove either quest.

Basis: `OWNER:1790972004219944071`; `RM_CondenserQuests.xml` keep-free branch; `RM_CondenserQuests.cs:292`.

Evidence and the implementation/proof/scope distinctions are in `record.json`. These drafts received a local evidence and wording check only; the role's fresh-agent review remains pending. No appearance was judged, no scene was staged, and nothing is protocol-approved as sent.

Excluded: questions reopening thrown-net capture, the cheap v1 truce, real doubt-meat thoughts, the crop or tree's existence, the two chosen giant quests, the dead wind-hour or the rejected born-and-dying-water system. The Refused Toll is deferred to v2 by `OWNER:1792755168241448197`. The fish walk, pilgrim passage, dewsilk casket and lying fish are recorded close misses and are not re-pitched here.
