# The Rot proposed comprehensive definition

Design Version 0.1.0. Author of scope, defaults and interpretations is the Designer in this cleansing pass. Owner rulings remain constraints. Proposal application awaits the owner's reading and the fresh review described in the brief.

## The mod in player language

A pale forest of enormous fungi rises out of glowing ground and milky ponds on Ash'karr's night shoulder. Its living floor helps heat your shelter, while the surrounding decomposer ecology consumes supplies left exposed. Food harvested from that ecology keeps giving off heat in storage, so settling here means arranging shelter, harvest and refrigeration around the same metabolism.

Land comprises pale cap architecture, readable ground contacts, biological light, milk shallows, dark sky, wet fungal emission and ordinary wreckage. Life comprises fungal forage and timber, existing hybrid residents, their ordinary diets, predation, poison defenses, products and reproduction, and dangerous resident Prime/Skulltop patches. The signature is the metabolic bargain in which the living floor warms shelter, exposed organic stores feed decomposition, and living harvest brings heat into storage.

The runner-up is the kin network that redistributes wounds and accelerates recovery. It lost because it introduces a separate combat/healing state machine, can run independently of the colony's food and shelter, and largely affects hunting or husbandry. Guarded medicine expeditions and the giant's ship story are further independent chains. Connecting their prose through the word “living” does not merge their causes.

## Why a player reaches for it

This is a cold settlement whose local abundance is genuinely useful and whose storage problems reward layout. Biological light and towering caps make its identity visible before selection. Ordinary fungi supply food, building stock, fibre and basic medicine. Native mat reduces the heating burden in enclosed rooms. A prepared colony keeps food usable by managing enclosure and refrigerator load. The prediction is that this connected routine makes comfort feel earned. Enjoyment remains a prediction.

The owner-selected experience is recorded in design/RimMandrake/biome_experiences_2026-10-20.md, TheRot row, picked by card. The frozen sheet design/Jawa/worldbuilding/biomes/the_rot.md supplies the planetary gut, metabolic warmth, cold shoulder, all-fungus flora, hybrid fauna and living harvest. Selecting this subset is a delegated version decision under this brief. Prior kit headings calling other systems v1 are historical scope. Their owner-set semantics remain binding when those systems are enabled in a later version.

## Using it

### First hour

Inspect the pale standing fungi, select a usable forage plant and find dry ground for a shelter. Ground-level contact and usable routes remain readable beneath large caps. Put walls and a roof over living mat, then haul perishables into the resulting enclosed store. A lean-to leaves the digestive exposure condition active. Temperature, floor identification and ordinary item rot information explain the change. No research, ritual, core or brew is a prerequisite to native warmth.

### Routine

Harvest ordinary fungal food and timber through normal jobs. Cut, haul, cook, feed animals, construct bridges and keep goo lamps fueled through ordinary vanilla workflows. Storing metabolizing glimmerslime and dulcis adds a visible thermal load. Divide storage, provide cooling capacity, reduce held stock or cook and consume the harvest. Frozen outdoor meat still meets the ruled digestive deadline. Indoor refrigeration has its ordinary preservation effect once its heat budget works.

The mat uses ordinary room heat. It helps at the cold end and stops adding heat at its ceiling. Ambient cold, clothing, insulation and backup heating still matter. Covering qualifying living floor with inert flooring changes the warmth qualification. Opening a doorway changes heat leakage. Breaching the roof or enclosing a formerly open stockpile changes digestive exposure. A reload re-derives room and thing membership from actual map state.

### A colony of forty

A working base uses designated indoor storage and sensible walking routes, with harvesting paced to food use. Its routine remains actionable through normal hauling, cooking and temperature management. The colony has no special feeding task for native ground. Population, ordinary animal products, decomposing corpses, wet-native plant cycling, gas defenses and room heat all run together. Excessive time spent correcting unexplained losses or repeatedly unblocking jobs is a whole-bar failure. Workload and food-chain tolerances must be calibrated by the whole-map model, then judged in the complete colony.

## What changes in the colony's story

The same ground that supports a bedroom digests the meat left beyond its walls. A harvest expands food security and raises the freezer load. Outdoor corpse disposal competes with hauling, rescue and butchery. Native poison and fungal predators require care when approaching food patches. An ordinary giant may still wander past. Its special swallowed-person, metal-recovery and ship-reward behavior belongs to the next version.

## Costs

Cold exposure, hauling before digestion, power or fuel for remaining heating/cooling, ordinary dangerous wildlife, and the opportunity cost of living flooring. Crop and animal yields remain tunable. Scarce expedition prizes, gene acquisition and exotic trade are outside this economy. Ordinary husbandry retains eggs, milk, silk, metamorphosis and Agari reproduction because these supply the resident species' normal player-facing use.

## When it goes wrong and the readable sign

An exposed stack shows digestion/rot state and loses freshness before it disappears. Frozen exposure needs an explicit digestive status because a vanilla frozen label otherwise promises safety. A roofed but unenclosed store has a visible exposure explanation. A qualifying mat room names its living-floor warmth in an inspectable readout. A rising freezer temperature corresponds to a visible quantity of metabolizing produce. These signs use existing inspect/temperature surfaces where possible. T68 specifies missing presentation.

Plant gas shows a local cloud and a health consequence during an ordinary approach. Current plant emitters use CompTick while Plant ticking normally follows TickLong. A forced Burst proves the helper alone. T69 requires normal-tick evidence and the existing engine's contract to be fulfilled. Pawn deaths use ordinary health/corpse and message paths. Population limiting admits or delays new wildlife through the shared spawner. It must retain a readable sign for any departure and preserve existing animals. Current hwelgrue OverCap destroys a wild extra with Vanish before its feature gate, so T23 contains the decoupling required by the life bar.

## Edges

The first-version promise covers authored Rot maps across their full warm-to-cold shoulder. The live site temperature and geometric sun position are inputs. Excluded experiences are Sheen infection, extra allergy incidents, guarded tea/symbiont prizes, kin sharing, chittik host implantation, psylink trees, weapon/fuel manufacture, grown heater/gene rewards, portable mat upkeep/budding, vats, purge medicine, special giant guts, rescue, core/log quests, ritual discovery, atmospheric food machines and mood mutators. Detailed fates and containment are in census.json and tickets.md.

Standing exclusions include automated planetary placement in any version, ordinary water rain on Rot, general gene banks, active engineered bioweapon ecology and arbitrary fauna disappearance. The setting is one received save on a fixed planet. Milk pools are local substrate and secretion. They add no planetary rivers, rainfall hydrology or traversable sea layer. Star Wars IP and authored campaign places belong to the deeper tier. Multi-homed species remain on their existing rosters.

## Neighbours and engine contracts

EnvironmentalHazards supplies the existing room-heat, organic-decay, living-produce and local gas mechanisms. This proposal specifies required outcomes and missing content bindings. Shared implementation choices stay with that engine. CreatureBehaviors retains ordinary services and the code for dormant kin/alarm behaviors. Vanilla Expanded Framework supplies the existing weird diet, product, reproduction and metamorphosis services used by residents. HugeThings supplies collision at measured ground contact, selection of the whole visible body and safe placement during growth.

ExplosiveGrowth already enrolls Rot as wet-native, with Churn rows and immortal exceptions in src/RimMandrake/ExplosiveGrowth/Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml. Existing wet-native cycling stays active. Wreckage supplies ordinary digested hull/frame placement, weathering and salvage under its shared commission. Bones supplies ordinary butchery products with its current race exclusions. The Acoustic Scanner patch records the owner's payload-on-every-biome requirement, so its ordinary residents/wreck/hollow integration stays. Its hwelgrue “metal ring” text must become an ordinary animal reading while the core is dormant.

Vanilla supplies food jobs, rooms, roofs, doors, refrigeration, cooking, taming, health and death. The substrate drinking contract follows the standing native-water ruling. Milk is a fungal medium. Native hydration succeeds beside it. Human potable-water production has no new mechanic here. The Rot is stabilized natural ecology adjacent to old war material, with the general genetic archive reserved to Slime. Dustveil remains fungus-grown and actually flies. Its no-laboratory ruling and directional flight requirement stand.

Durrok and mullgoth are historically reported as shared with Leaning Scrub, and mullgoth with Cauldron, in design/RimMandrake/rot_open_questions_2026-10-22.md. Their external source and the campaign canon patch are absent in this checkout. Current merged roster presence is unknown. T65 checks composition and historical membership without making evictions or inventing local substitutes.

## Settings

Keep the existing searchable, collapsible settings front, reset and persistence. Shipped defaults enable native mat warmth, digestive decay/compost, living produce, ordinary biological lighting, native predation/defense, ordinary animal lifecycle, shared wet-native growth and common wreckage. Each major retained behavior has a named toggle with effective scope. A disabled signature component leaves its terrain/content readable and the rest functional. Master-off makes special Rot behavior dormant while retaining safe defs, animals and held-state conservation.

Moved extras receive separate next-version controls with factory defaults off, including when an older settings file omits a new field. Restart-sensitive content gates declare restart/new-map scope. Existing shared engine controls remain effective and the front shows when a shared control suppresses a feature. Existing cross-biome controls remain off and labelled unsupported. Portable mat keeps its expressly ruled supported-anywhere contract inside its dormant next-version option. Turning it off must stop spread/upkeep/heat safely, preserve existing floors and save state, and allow recovery of any held contents in related systems.

## Four stories

### The first hour

The landing party sees a dark woodland lit from below, selects a food cap and carries timber through the gap between giant stems. Their first enclosed room retains the living mat. Its thermometer rises relative to the matching bare-floor shelter. Meat left under a roof outside the room continues toward digestion. The player finishes the store enclosure before bringing the next load in.

### An ordinary week

The cook keeps up with harvest. A brogg is milked and the dustveil's silk gives a husbandry reason to protect it. Stored glimmerslime raises the freezer load. Moving that stock and adding cooling restores preservation. The base's warmth and food costs remain legible while local Prime clouds make harvesting its particular patch a careful approach. Rain-like sleet is named Sheen and comes from the fungi.

### The worst day

A fight leaves a downed worker and several corpses outdoors. Rescue uses the ordinary rescue job. The first version's hwelgrue continues its ordinary animal life. A damaged roof exposes stores and cold air reaches bedrooms. The player can trace losses to roof, enclosure and stock, repair the roof, haul salvageable food and choose which corpses to butcher before the gut takes them. Every casualty has a readable health/death trail.

### The season's turn

After a mid-season reload, growth, reproduction and decomposition resume from saved state. The colony expands storage before harvesting, then repeats the sequence with harvesting first to expose the consequences. Across the full map the pale forest remains alive, dangerous patches remain local, usable routes remain, and ordinary colony management continues. A forest-wide gas flood, collapsed food web, permanently jammed hauling or repeated error stream fails the whole bar.
