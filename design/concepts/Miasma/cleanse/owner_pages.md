# Page one — the proposed first version

You settle among salt-white banks, stilt-root trees and honestly beautiful flowers under sickly green-gold haze. Storm-driven brine reaches up the channels and retreats, leaving sea young in shrinking pools their water-bound warden mother cannot reach. Return them and earn her tolerance, or sell them and lose her trust, while unharmed young may choose your colony and continue a weaker watch when old age takes her.

Land is difficult brackish mangal, fresh mud, salt margins and dry sick air.

Life is the admitted alien canopy, benign blooms, scuttler prey, ordinary predators, composters, flying swarms and sea juveniles, with food and husbandry products.

The signature is recession creating nursery rescues whose treatment determines maternal tolerance and the chance of juvenile inheritance.

I chose this signature as Designer. Rot electricity was the runner-up. Your October experience card includes “Rot is power”. Under your later land/life/signature instruction I defer that independent industrial chain together, preserving its promised future behaviour. Rescue, sale, trust and inheritance remain consequences of the same nursery history.

**Before and after.** The reconciled census contains 86 capabilities. I keep 59, move 22 to next version and recommend retiring 5. Old bars are 0, as supplied by the CASE. Proposed bars are 9. Live-only bars are 1. The rendered landscape requires that look. The other bars use calibrated models and ordinary-action state traces. Checks are 13 and rules are 12. Unknown meetings are 7, models are 4, tickets are 36 and questions are 0. 

**Next version, switched off**

- Found meter and research
- Rot electricity
- Spent-cell conversion
- Corpse disposal
- Bed-grown Cuisine ingredients
- Attar refining
- Artwork glazing
- Initial loose-goods seeding
- Fever-forging grants
- Strange-boon effects
- Elaborate promised boon effects
- Lastvine rearing
- Lastvine acid spit
- Sharpshrimp regeneration
- Siezer lockjaw disease
- Duskfire burning spit
- Drake fermentation and intoxicants
- Host/castings germination gates
- Bespoke plant-fed displays
- Recall of the Written-Off rite
- Custom nursery buyer visits
- Swarm contact transmission

Each built extra has a switch-off ticket, with default/on state tests and decoupling where required. Ordinary traders still supply the meaningful sale choice. Shared growth, hazards, creature pressure, canals, Wreckage and stable Bones references remain dependencies. The admitted animal roster stays in scope with ordinary diets and attacks.

**Recommended retirement**

- World scoring and rarity control conflict with the permanent worldgen ban. There is no later worldgen version.
- The map-wide crèche manhunter lottery adds generic incident pressure and can punish natural maternal death.
- Injury-changing attar balm conflicts with cosmetic-only attar and the medicine ban.
- Legacy medicinal-mangrove harvesting conflicts with that medicine ban.
- Keep the already-cut pollination gate retired, respecting the existing decision.

These are my recommendations. Stable source, definitions and assets remain available while active candidate behaviours default off.

# Page two — what to check

**The consequential defaults I took**

- A surge must actually wet and withdraw from ground, creating newly cut-off water. Current code supplies salinity repaint and existing-pool detection, leaving this causal gap.
- “Every surge brings orphans” means recurring nursery rescues. Individual recessions can have empty pools. A prepainted pond cannot prove the cycle.
- Sea connection means the actual seaward boundary. A large pond or fresh river edge cannot qualify. Full executed routes must stay in water.
- Bridge water remains connected underneath, while its constructed movement surface can obstruct swimming.
- A severed canal leaves the mother visibly trapped in a wet component. Repair restores legitimate routes.
- Carrying an unresolved distressed young is the established rescue action. Affectionate water-bound young receive no carry-home upgrade.
- Each young keeps its nursery identity after distress clears. The current return path discards state needed by later consent and inheritance.
- Completed paid sale commits betrayal. Opening or cancelling trade leaves trust intact. Ordinary traders suffice, so bespoke visitors move.
- Consent is frequent while the nursery record is clean. Inheritance needs a rescue at that same nursery and a living self-tamed young with a water route; a never-rescued sibling can inherit a real weaker watch.
- Tolerance excludes the colony, but harvesting anything inside her anchor reach immediately makes that actor a target. Outside harvest stays safe; harm to young ends the clean record and sale betrays it permanently.
- Recurring wet root-line deposits stay: water-only haul otherwise has no recurring natural work. Initial seeding alone waits. Seasonal proof uses no staged goods.
- The mother’s decline must be apparent from encounter and complete within ordinary campaign play. Age art alone leaves that behaviour unproved.
- Pool expiry excludes rescued, owned, sold and departed young. The already-permitted fallback remains available with a player-visible loss sign.
- Ordinary canopy recruitment follows the salt gradient. Additional host/castings gates wait. Rainbow blooms remain benign.
- The authored planet’s basin and river rulings govern the river-mouth fiction. Local ecology authorises no world-map repair.

**Models, first to build first**

- Shore and route sweep tests changing water, floor preservation and full swimming routes.
- Nursery transition generator tests identity, rescue, trade, consent and inheritance through reload and reordered actions.
- Whole-map season tests ecology, weather, nursery duties, frequent consent and recurring deposits versus hauling and stock accumulation.
- Food and rescue budget tests whether a ready party can respond while the colony feeds and tends itself.

The unresolved meetings concern terrain, water routes, nursery records, ecology, weather, colony workload and root-line goods. Their models require agreement with real game records before their predictions can decide a bar. Instruments and implementation gaps are ticketed. The review corrections are incorporated; its second look remains pending. Applying this proposal requires your approval after review.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a sourced core promise omitted or weakened (bars.json B4 (says, range.left_out, reject #1); definition.md 'Using it'; owner_pages.md page one). The owner's ruling, quoted word for word in design/Jawa/worldbuilding/biomes/miasma_fauna_roster_2026-09-23.md §6, says: "Means that when it spawns, so do some stranded young (sometimes)." The same section explains why it matters: "the offer arrives with her, on the first day ... it is what makes this content reachable at all." census.json row warden_sites keeps it as signature ("anchored warden and sometimes a nearby stranded juvenile"). But no bar, definition paragraph or owner-page line mentions it. B4 says only "When Miasma surge water withdraws...", and its range allows "Not every random recession must create an occupied pool." B4 reject #1 also refuses "A young is spawned in a pre-existing painted pond ... while the surge itself changes no connectivity." A cold reader would refuse the ruled day-one young under that picture. So the ruled first-day offer is neither promised nor protected, and B9's stretch may never show an orphan at all. Would pass: A bar says a mother can arrive with a stranded young of her own, so the rescue-or-sell choice can open before any storm. Surge recession remains the recurring cause. The prepainted-pond reject is narrowed so it cannot catch the mother's own arrival. Smallest fix: Add a B4 accept picture: 'A mother placed with the map sometimes has her own stranded young nearby, which calls and can be rescued before any storm has come.' Reword reject #1 to: 'a proof helper spawns a young in a painted pond, and neither the mother's arrival nor a surge caused it.' Add one line to definition.md 'Using it' and to page one.
- an extra left in the first version without its needed_by deletion argument (census.json rows flotsam_yard and water_only_haul (both needed_by signature); bars.json B5 accept #2 and reject #4, B9 accept #4 and reject #4, R7's deposit clauses, meeting 'root-line goods'; tickets T6 and T15). The signature in result.json is "Storm recession creates nursery rescues whose treatment determines maternal tolerance and the chance of a juvenile inheritance." The case for keeping the deposits is circular. ambiguities.md 'Flotsam and salvage' says "deleting them defeats recurring water-only haul". 'Trainable at the waterline' says the haul stays because removing it "defeats the affectionate child's ordinary usefulness". So the deposits are kept for the haul, and the haul is kept for usefulness, which the signature sentence never names. The fauna roster §6a table already lists Guard and release/attack as water-scoped trained work that needs no item source. Deleting the haul and its recurring deposits leaves rescue, tolerance, sale and inheritance whole. What it removes is a custom economy with stock caps, its own wet-root placement, an unknown meeting ('root-line goods') and a seasonal item-flow model. That is the 'little custom details' the owner told the Designer to move. Would pass: Either a deletion argument that ties water-side haul to land, life or the signature as stated, or water-side haul and its recurring deposits moved to next version, switched off. The young's 'useful water-bound work' in B7 is then met by Guard and release/attack. Smallest fix: Move flotsam_yard's recurring deposits and water_only_haul to next_version.md with switch-off tickets (merge T6 and T15 into one). Drop B5 accept #2's haul clause, B5 reject #4, B9 accept #4 and reject #4, R7's deposit sentences and the 'root-line goods' meeting. Keep Guard and release/attack in R7.
- a kept mechanic with no definition (bars.json B7 (accept #2 'actually guards that nursery with less reach and threat'), R6, R7; definition.md 'What changes in the colony's story'; tickets.md T14). R6: "starting any harvest of plants, wood, salt or animals inside the mother's anchor reach immediately restores that actor as a defence target, tolerated or not." The source mechanism is RM_JobGiver_AnchorDefense (EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs), which the roster describes as fighting "anything hostile-or-harvesting inside the anchor radius". The roster §6a says the heir is "simply a tamed juvenile with the anchor comp pointed at the crèche. The same mechanism". Neither the proposal nor T14 says whom the colony-owned heir targets. Does it attack its own colony's salt and wood gatherers inside its reach? Does it guard only against hostiles? Does the harvest exception end when the mother dies? The 'weaker watch' is a kept signature mechanic with no target set. Would pass: R7 and B7 state the heir's target set: for example, hostiles in its reduced reach, never its own colony's harvesters. Add an accept/reject pair: 'a colonist gathering salt beside the inherited crèche works unharmed while the heir attacks a raider crossing its channel' against 'the heir attacks its own colony's salt gatherer'. Smallest fix: Add one sentence to R7 naming the heir's targets, and that accept/reject pair to B7.
- a kept mechanic with no definition (definition.md 'Using it' ('A held distressed young ... can be offered to an ordinary eligible trader'); ambiguities.md 'Carrying versus the water-bound affection' ('held for the ruled sale'); bars.json B6 accept #2, R6, R7 ('is never conventional taming'); next_version.md buyer_visits). In code, a sellable young must belong to the colony. RM_MothersPrice.cs:280 checks "p.Faction == Faction.OfPlayer && RM_MothersPrice.IsStrandedYoung(p)". Carrying a wild pawn does not change its faction. R7 forbids conventional taming, and the roster §6a says a conventional taming grind "is working against three rulings at once". With the custom buyer moved to next version, the proposal never says how a colony comes to 'hold' a wild stranded young that an ordinary trader can buy: vanilla Tame, penning, capture, or only after self-taming. Without that, the sale half of the ruled 'carry it home or sell it' choice (MIASMA_MOTHERS_PRICE_1, owner card 2026-10-02) has no defined route. Would pass: A rule naming the act that makes a stranded young colony-held and tradeable, consistent with R7. Plus a B6 picture in which an ordinary trader's dialog lists a young the colony came to hold that way. Smallest fix: Add to R6: '<named act> makes an unresolved stranded young colony-held without taming it; only a held young appears in an ordinary trader's dialog.' Add the matching accept picture to B6.
- a figurative word unmarked (bars.json B9 says ('ecological engulfment', 'permanent barren collapse') with figurative []; B1 says ('rainbow plants') with figurative []). B9's figurative list is empty, but 'engulfment' and 'barren collapse' are images, not states. models.md defines a different set of words, 'flood', 'desert', 'stall' and 'error storm', so B9 and its own model use different vocabulary. B1's accept picture says "saturated blooms", which departs from a literal 'rainbow' without marking it. Would pass: Each word is listed in figurative with what it stands for and one accept picture that departs from the literal reading. Or B9 uses models.md's defined words. Smallest fix: Add figurative entries: 'engulfment' = breeders or events displacing ordinary play (the models' 'flood'); 'barren collapse' = ordinary life failing to recover in the habitable fresh region (the 'desert'); 'rainbow' = saturated multi-coloured blooms, not every hue on one plant.
- evidence that cannot tell success from a plausible false pass (bars.json B7 (figurative 'frequently', reject #4); models.md Whole-map season 'Game agreement before belief'; checks C11). The instrument checks only that consent counts on holdout histories "fit prediction intervals fixed from shipped chance/cadence". That tests whether the model agrees with the game, not whether consent is frequent. A build that ships a chance so low the young almost never consent would match its own model and pass. models.md says "B7 frequent-versus-almost-never classifications must agree with real traces" but never states the line that classifies a trace as frequent or almost-never. The tuning is pushed to C11. Would pass: B7's sees states the comparison a player notices, as a classification and not a tuning number. For example, across the observed stretch a clean nursery with living young usually has young choosing the colony before the mother dies, and a clean nursery whose mother dies with none having chosen is the exception. The verdict comes from game traces, never from agreement with the shipped chance. Smallest fix: Add that classification rule to B7 sees.control. Delete 'fixed from shipped chance/cadence' as the pass criterion in models.md, keeping it only as the model's calibration check.
- evidence that cannot tell success from a plausible false pass (bars.json B1 sees.instrument). "Live rendered-map look with the simultaneous terrain/salinity and access overlay supplied by T19." B1 is about the player recognising salt, mud and channels at ordinary zoom. A look taken with a salinity overlay drawn reads the overlay, so a build whose plain render leaves salt banks indistinguishable (reject #1) can pass. Would pass: The look is judged on the plain rendered map with no debug overlay. The overlay is captured as a separate frame, used only to choose and label the sampled regions. Smallest fix: Reword the B1 instrument: 'judged on the plain render with no overlay drawn; the T19 overlay is a separate frame used only to locate sample regions.'
