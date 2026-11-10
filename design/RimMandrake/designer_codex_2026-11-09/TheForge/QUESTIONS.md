DRY RUN — TheForge, stages 0 and 1. This is an agent-authored proposal and question bank, with guesses, not approvals or a sent dialogue turn. Only the historical sentence immediately below is Mandrake's wording.

The experience, in the owner's words (2026-10-20):

> Where the gods came to forge a world is now the ruins that seek to unmake you. Even the beasts challenge your presence.

Source: `design/RimMandrake/biome_experiences_2026-10-20.md:24`, corroborated by the validation walk's experience section. This file source is deliberate: I did not find an OWNER event with a tsn for this sentence.

PROPOSED ROOT — my expansion, not his words

TheForge makes living in a ruined volcanic forge feel like trespassing in something still at work. Fire and water set the colony's working day: gas ignites exposed growth, boiling rain drives people to shelter and floods the ground, and lava briefly becomes a walkable, steaming crust where floatstone gardens grow. The opportunity closes with glowing cracks, drifting gardens and the return of the melt. Its animals belong to that same place: apparent outcrops wake in rain, swarms run on the wet interval, herds and hunters gather around the vapour columns, and a placid dhoggur becomes a fire-spitting danger when attacked. Survival means reading the mountain and making deliberate trips into it; floatstone and its strong, light construction are a reason to risk those trips. The old works must feel present in the experience, while the campaign's tower dungeon, gas monopoly and other lore remain separately owned integrations. Settings let the player tune the built dangers without leaving broken terrain or stranded creatures.

My claim: the mountain should feel like an old forge that still works, on terms the colony must respect.

Strongest objection: the ordinary biome has much of that living machinery, but its ruin skyline is largely a description; the tower shell is campaign-layer content. A passing cycle could therefore miss the heart of your sentence. The paragraph proposes an experience; it does not claim acceptance or settle that boundary.

These six drafts are a bank. **Ask 01 and 02 first**, then at most three at a time after review. A phrase, another scene, or “this doesn't matter to me” is enough. The pictures are written thought experiments, not captures, staged scenes or visual acceptance. Existing capabilities are retained; none is offered for removal. Recommendations and guesses below are mine.

01. **ASK FIRST — The old works before a tower visit**

Picture: On the franchise-free Forge, the crew shelters from a gas wash, watches the lava crust over and ventures out for floatstone. You have seen the mountain's cycle and its animals, but have not entered a tower or met a machine. The existing campaign design already promises real towers and machines, with a separately built tower entrance and one-floor dungeon shell. Those promises and their campaign ownership stand.

Question: What should the crew encounter in that ordinary RM day, before any campaign tower visit, for the proposed root to describe the right experience?

Why it matters: F1. The code can deliver a volcanic harvest cycle while the RM player's sense of the old works is only prose. The campaign's physical ruins are already settled; the remaining gap is what experience this paragraph promises before entering them.

My guess, not your answer: The cycle should feel like the dangerous workings of the place, with recognisable traces of manufacture on the ordinary map; entering the campaign tower deepens that encounter. I recommend stating that relationship explicitly before binding the root.

What changes in the tree: If the cycle and the existing arrival description supply the pre-tower experience, bind those to the RM root without inventing another encounter; the campaign's physical towers and machines retain their own requirements. If a physical trace or encounter on ordinary RM maps is essential, add that bounded requirement and identify which existing assets supply it and what still needs building. If the required moment is specifically the existing campaign tower, make that integration explicit and correct the root's promise to the RM reader; do not erase the tower, generalise its lore or treat its shell as a finished encounter. A correction changes dependent claims. No answer approves this root.

Evidence: experience source above; `src/RimMandrake/TheForge/About/About.xml`; `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FoundryTowerScatter.xml` and `RUT_FoundryFloor.xml` (all `src/` paths are relative to the mirror).

02. **ASK FIRST — The first demonstration**

Picture: Three candidate scene cards. A: the crew shelters through fire and rain, crosses the cooled seam, harvests a garden and returns before the melt. B: an apparent hill wakes, moves near the colony's walls and leaves its worn way behind. C: herds gather in the columns and a jossur hunts there. Each is an exploration draft, not a staged demonstration.

Question: Which would you put first when deciding whether this mod understands the Forge, and what one wrong moment would make you reject it?

Why it matters: F1/F2. The first scene should test your defining experience, not whichever debug action is easiest to run. No flagship pick was located.

My guess, not your answer: A, with a real working crew and a real return route. I recommend it because the dangerous place, tempting reward and retreat become one decision. B and C deserve separate demonstrations of their own features.

What changes in the tree: The chosen scene becomes showcase 1 only after an explicit recorded pick. Its reject example sets the central acceptance property. Later showcases must add different functionality; other built features still receive ordinary acceptance coverage and interaction checks. Choosing A does not accept animals, audio, research or doors through incidental presence.

Evidence: `ITEM:FORGE_CYCLE_MECHANICS_1`, `ITEM:FORGE_GPT_ENRICHMENT_1`; `src/RimMandrake/TheForge/validation.py::cycle_walk`, `::sky_pastures`.

03. A warning worth hearing

Picture: Forty colonists are spread between workshops and outside jobs when the vents begin to hiss. The built warning precedes the gas wash by a provisional hour and a half; later the cracks letter gives the remaining time before melt. A short random boiling-rain burst can also happen during still heat. The earlier rain ruling already says one burst is survivable, leaving the victim downed and scarred, never instantly dead.

Question: By the time each danger arrives, what should an attentive colony have been able to finish: recalling exposed workers, getting a rescue out, recovering the last load, or something else?

Why it matters: F2. A letter can arrive correctly while allowing no useful decision. Gas, ordinary rain bursts and melt have different clocks; one warning check cannot accept all three.

My guess, not your answer: The hiss permits a prompt recall, the cracks permit an orderly retreat, and rescuing someone after ignoring the danger is a risky extra effort. I recommend judging those actions before choosing exact durations.

What changes in the tree: A recall promise gets a dispersed-worker scene with a measured route to shelter. A rescue promise adds a downed pawn and a second worker with a feasible return. Recovering stores adds hauling time and capacity to that case. If a particular preparation is not promised, state the narrower warning there rather than inventing a generous timer. Preserve the settled survivable-first-burst bar; no new fireweed gear economy is inferred.

Evidence: `src/RimMandrake/TheForge/Defs/GameConditionDefs/RM_ForgePulse.xml:59`; `src/RimMandrake/TheForge/Source/RM_GameCondition_ForgeCycle.cs:263`; `design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md:438`. The later fireweed-gear exclusion is `ITEM:FORGE_RULED_CONTENT_1`.

04. The haul that justifies the trip

Picture: A crew waits for the crust, works the gardens and returns before cracks. Today's garden yields one block per harvest, with five to ten gardens seeded per cycle before losses or other effects; a special door costs 25 blocks and hull costs seven per cell. Those are source defaults, not measured expedition returns. The yield was reduced under the existing plant-economy bar.

Question: What should a successful trip let the colony do when it gets home, and how many such trips should a meaningful piece of floatstone construction represent?

Why it matters: F3. Harvesting a block proves a product exists, but can leave the dangerous expedition unrewarding. The material's strength, beauty and lightness are already settled; their useful scale in play is not shown by the harvest test.

My guess, not your answer: A trip should visibly advance a chosen project, while fitting out a ship remains a sustained achievement. I recommend judging one named project rather than treating a high sale price as the whole payoff.

What changes in the tree: A small-building payoff needs a bounded acquisition-to-construction scene and matching costs or availability. A rare luxury payoff instead demonstrates worthwhile partial progress and a believable longer supply. A trade-led payoff needs actual sale proceeds and opportunity cost. Reconcile any tuning with `plant_economy_rule_2026-11-01.md`; do not quietly reverse its yield bar or restore the removed fuel-saving brace.

Evidence: `src/RimMandrake/TheForge/Defs/ThingDefs_Plants/RM_TheForge_Flora.xml`; `src/RimMandrake/TheForge/Defs/ThingDefs_Buildings/RM_SpunstoneParts.xml`; `design/RimMandrake/plant_economy_rule_2026-11-01.md`; `OWNER:1792759866253411416`.

05. What stops a steam front?

Picture: The same white front rolls over an open work site, an open-sided roofed shelter and a closed stone workshop. Rain scald already distinguishes roofed from unroofed pawns. The separate plume implementation moves across walls and roofs: it marks heat across the moving radius and directly adds vanilla smoke to each non-filled cell, even behind a wall. Vanilla handles the smoke after that injection. This is a comparison of exposure, not a new kind of heat.

Question: What protection should the workers in those three places actually get as the front passes?

Why it matters: F2. A roof stopping rain does not establish that it stops steam or hot air. Smoke, the front's visible position and its heat can currently disagree about which room is exposed.

My guess, not your answer: An open roof stops falling rain but offers little protection from a sideways steam wash; a closed room blocks the immediate front, with normal temperature rules deciding what happens over time. I recommend that because the protection follows the place's physical shape.

What changes in the tree: If enclosure blocks the front, require a sealed-room/open-door control and consistent smoke, heat and visible-front boundaries. If hot steam penetrates enclosure, name the route and the protection a colony can actually build, and demonstrate it against a closed-room control. If only some effects penetrate, describe and prove those separately. All answers keep vanilla heatstroke and the existing plume capability; none invents biome-specific sun or treats shade as cooling ambient air.

Evidence: `src/RimMandrake/TheForge/Source/RM_ForgePlumeFronts.cs:163`; `src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_WeatherPulse.cs::DoScaldDamageOnMap`; `ITEM:FORGE_WHITE_PLUME_FRONTS_1`; `CLAUDE.md` Direct Sun ruling.

06. Working beside the sky's hunters

Picture: The safe route to a ripe garden passes the edge of a vapour pasture. A jossur is hunting among the smaller animals there. The crew can take a longer route, send armed protection, or hurry through together. The current code biases hunting toward columns and starts real flight during a hunt; it does not establish which of those plans makes a satisfying human encounter.

Question: What should a well-planned crew be able to do about that hunter, and what mistake should make its presence costly?

Why it matters: F1/F2. “Even the beasts challenge your presence” needs decisions in the crew's day, as well as working animal code. A predator on the map alone does not prove that experience.

My guess, not your answer: Reading its hunting ground and escorting exposed workers should help; treating the column as empty scenery should be the mistake. I recommend a threat the crew can understand and plan around.

What changes in the tree: Detouring makes habitat boundaries and a genuinely safer route part of the interaction scene. Escorting requires useful intervention before the victim is lost. A fast crossing requires a finite, achievable escape opportunity. If ordinary vanilla predator behaviour supplies the intended answer, test that interaction without inventing another combat system. A more specific hunting pattern becomes a bounded requirement only after it is described. Flight proof remains a state read with the owner present, never an unattended flight hunt.

Evidence: `src/RimMandrake/TheForge/Source/RM_ForgeSkyPastures.cs:487`; `src/RimMandrake/TheForge/Defs/ThingDefs_Races/RM_TheForgeNatives.xml` (jossur); owner experience source above.

The full inventory, provenance, failure modes and script audit are in `record.json`. No guesses are stored as answers, no new text is attributed to the owner, and nothing goes on the ledger.
