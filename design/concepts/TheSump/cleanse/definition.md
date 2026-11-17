# The Sump — proposed Design Version 0.1.0

Designer-authored, delegated scope decisions, 2026-11-17. This proposal changes no source, game, concept record or ruling. Application remains the separate review/owner process. There are no locked concept leaves to preserve or remap. No waiver was found in the earlier inventory record, and none is requested again.

The Sump is a cold, flat black basin under permanent dry dusk, with solid glassy ground between pools of tar. Its waxy plants feed without sunlight, and its seated animals forage, hunt and can be tamed among the margins. Crossing raw tar slows and dirties workers; choosing routes and supplying solvent lets an established colony keep working without becoming clean everywhere.

Land: black pools, deep mere, shallow edges, cooled sheets, low margin vegetation, cold ambient air, usable building ground and dry dusk. Life: the existing roster's ordinary bodies, feeding, forage, cultivation, hunting, products, taming and locomotion. Signature: crossing raw tar brings a persistent movement/work burden into the colony, answered by route planning and supplied worker cleanup.

Runner-up: excavation of the preserved archive. It lost because the owner's chosen experience sentence concerns ordinary resistance, whereas strata, traps, truthful clues, rare finds, artifact research and awakened beasts demand a second chain. This is a version boundary, not a change to the archive's lore or its prior rulings. The strongest argument against my choice is the frozen sheet's phrase “excavation as core gameplay” (the_sump.md §7). I take the later explicit land/life/one-signature instruction as authority to sequence that promise, while retaining its bans and the later trap/evacuation answers for its return.

## Why a player reaches for it

The player wants a settlement where ordinary errands have a terrain cost and an established colony still looks inhabited by this particular place. This is an alternative to vanilla mud plus a normal temperate food web: the plants do not await sunrise, the ground tracks tar, and a permanent clean route buys convenience with pitch, labour and continuing slower travel. Predicting that the route/recovery tradeoff will be enjoyable is a design hypothesis, not a passing bar.

## Using it

First hour: look at the terrain and inspect a shallow margin before committing a worker. Pick solid building ground, haul initial food, gather reachable skelver/lanneth and sow dorvel where planting is allowed. There is no promised opening harvest, medicine-free instant cure, research gift or new arrival letter. Crossing shallow tar is possible but slower than the same worker on solid clean ground. Deep tar is visibly a barrier to ordinary ground walking, not a hidden pawn deletion. A normal floor is a useful initial route and can collect tracked tar.

Routine: grow food, harvest korveth pitch, use the existing rendering/bench chain to make bitumen, and lay glasswalk along chosen traffic routes. It rejects deposits but does not cure a dirty carrier merely by standing on it. Ordinary accepting floor and a clean work spot allow the carrier to shed tar and gradually recover; solvent is the faster chosen recovery. Workers use the player's standing cleaning/work priorities and solvent-reserve policy, physically reach the material, reserve it and do the work without repeated per-pawn medical bills. The current surgery is evidence of a partial mechanism, not this completed routine.

At a forty-colonist scale: the player changes route layout, work sites, staffing and reserve policy. Workers handle ordinary cleaning and accessible-material retrieval. Dirty outside workers and dirty accepting floors persist; the colony does not require the player to issue forty scrub bills after every expedition. Glasswalk leaves no tar deposit, while existing carried tar still needs a real removal path. Cleanup may be delayed by sleep, danger, downing, work priorities or shortage; it may not reserve the same solvent indefinitely or starve all food/hauling work in a retry loop. No guarantee is made that native forage alone feeds this colony.

## What changes in the colony's story

A useful path and a stocked cleanup station matter. The worker who cuts across a pool brings home the cost of that shortcut; the colony gradually pays to route regular traffic around it. The native crop and local pitch/wax resources give settlers reasons to use the margins. Ordinary predators still threaten prey and tame stock. No new quest, religion, beast catastrophe, gaslight industry or hidden clue system is needed to tell this story.

## Costs

Crossing tar costs time and later work efficiency, with the existing readable tarred stages and mood cost. Its existing flammability consequence uses ordinary fire and heat, not a new burn system. Raw ground and ordinary floors can foul; glasswalk costs bitumen and work and remains slower than clean paving for the same walking pawn. Clean-ground recovery is slow; weak solvent consumes locally obtainable wax and work for faster relief. The broodmother's ordinary butcher product currently supplies raw seepwax; custom mounds are not a prerequisite. Large or repeated expeditions can exhaust stock. No special renewable mound economy or foreign strong-solvent supply is promised. Strong solvent remains an inert, compatible trade hook, explicitly not a commissioned trade route.

The existing production bench is TableMachining; no first-hour solvent guarantee is inferred. Current recipe prerequisites must remain reachable by ordinary research, without draw-joint, gaslight, vat or vault unlocks. If the colony deliberately hunts out every local source, shortages are a consequence, not permission for hidden resource generation. The solvent model will determine whether ordinary supplied routine is credible at default throughput, not dictate a permanent yield bar.

## When it goes wrong and the readable sign

The pawn shows tarred state and its movement/work consequences; terrain inspection identifies shallow/deep tar and solid glasswalk; the cleanup action shows missing/unreachable solvent or work access. A successful application clears carried tar as well as the associated condition. Cosmetic health removal followed by immediate reacquisition is failure. The chemical reaction can dissipate harmlessly; bottled gas is off with gaslight. No medical injury, forced anaesthesia or death is acceptable for routine solvent application.

On job interruption, save/reload, downing or death, reserved material has one owner and is released or consumed exactly once. A corpse, dropped goods, visible departure or disabled saved creature remains readable; no Sump mechanic erases an animal or pawn. Natural deep tar is impassable to ordinary ground walkers. An animal's ordinary adaptation or real flight must be read as actual movement, never a teleport/despawn shortcut. Saved deferred creatures are visibly paused or migrated compatibly; default-off must not delete them.

## Edges

No alternative planets, biome-scoring feature, active world mutator or world repaint. A zero-tile BiomeDef is expected. Local terrain initialization for a fixed world's already selected site is land creation, not authority to generate a second world: its geometry can be modeled, but no world seed sweep or placement slider is retained. Existing canonical saves are not touched.

No instantaneous tar killing or passive swallowing, no pallick collapse, truthful gas/treasure cues, mouse-route instrument, catastrophe, excavation lottery, scripted belch, custom smoke wall, capstan, winch, vault, aged food, gaslight fuel loop, ritual or inhabited settlement injection runs by default. Existing fixed-world stations and independent neighbouring mods are not removed. Pallick and the indicator plants stay seated as harmless flora in this version; their descriptions and the arrival advice must not promise disabled functions. This is not an ecological claim that their future functions were cancelled.

## Neighbours and inherited constraints

Ash'karr is a fixed tidally locked desert world. The Pyrelands make the tar over geological time; drainage and the cold night-edge basin collect it. This is history, not a simulation of petroleum arriving from another live map. Cold and dry do not imply every native can always grow: vanilla ambient temperature still constrains growth. Plants are chemotrophs, low and non-glowing; warm points of light come from ordinary built lamps. Brindeth no longer yields wood, per the later size ruling. Bones can supply ordinary building stock through its own system, not WoodLog for a recipe.

EnvironmentalHazards supplies the weather lock, exposure link, coating APIs and compatibility infrastructure. CreatureBehaviors supplies its ordinary shared animal support and Direct Sun; the sun remains one geometric rule into vanilla heat. Fog/dusk/glow are not a sun-heat exemption. FlowWorks supplies tar terrains, ordinary coating, channels, source/sink, gates, burn and cooling. Those physical behaviours remain enabled at shipped defaults even though Sump's special moat/post/belch are off. A player may use generic channels; no new Sump plumbing product or duplicate fire engine is defined. Existing cooling to glasswalk stays land integration.

ExplosiveGrowth remains enabled: inspect resolved profiles rather than infer them from growMinGlow. Its base roster search found no explicit Sump plant entries; the native default classifier can therefore matter. Verify chemotroph progression and effective top/soak behaviour through its existing data API before believing a whole-map forecast. Wreckage remains the ordinary shared wreck engine, with no new Sump wreck field commissioned; any existing composed default fields belong in the whole run. Bones supplies ordinary applicable butcher stock. None of these engines is redesigned here.

The campaign-only Hssiss addition stays conditional and is multi-homed according to the earlier record's Greentide reference; evictions are stopped. The invented native names remain RM tier, genuine canon remains patched in the campaign layer. The Holy Flame act already belongs to the Shkaar idol and was expressly excluded from the owner-deferred Nine rites: do not disable or revisit that neighbour. ColdStorage, AcousticScanner, FlameStatues and HugeThings keep their own systems; deferred Sump integrations must not switch their global engines off. Natives must meet thirst at their own environmental tar through FlowWorks home-liquid support, without human consequences (biome_rulings.md, 2026-11-01). The shared support exists but tar binding was not found in the inspected patches; it is required integration, not a new thirst engine. Humanlikes need ordinary supplied drinking water; no potable tar or fresh-water terrain is invented. Random anima trees remain blocked by the standing ruling. All DLC is assumed. No DLC-absent configuration is a test region.

## Settings

Shipped defaults: ordinary land/life, dry-dusk presentation, tar pickup/exposure, glasswalk, local pitch/solvent routes and routine cleanup on; every next-version Sump producer and effect off. Give each major retained feature an honest control, meaningful tuning and scope label, with search/reset using the existing settings kit. Show next-version options together, labelled experimental/next version, default off. Coupled extras may have an explicit group prerequisite, never a silent enable of companions.

Switching effects off on a saved map leaves land and seated bodies intact, releases reservations and restores ordinary work without frozen tar penalties. It does not change a neighbour's global setting. A glasswalk build-off setting hides new construction without destroying saved floor. Turning off presentation does not change Direct Sun geometry or thaw/remove tar. All-off degrades to ordinary playable ground/life, with no custom operations or penalty left running. Reset restores the advertised defaults. Local habitat/land creation controls are clearly labelled new local maps only, not worldgen. Existing unsupported cross-biome controls remain off and labelled; none is added. Density changes retain honest restart timing.

## First hour — a story

The builder finds solid black ground beside a pool and puts the stores there. A shortcut through the margin delays a hauler, and the returning worker's inspect state explains the black on the floor. The player sets a regular paved approach and starts the local crop. There is no letter advising reliance on a mouse trail that does not exist.

## Ordinary week — a story

The colony harvests pitch and wax, renders material and keeps solvent reserved for outside workers. A clean glasswalk approach needs no floor scrubbing, but a worker still carrying tar walks through the cleanup routine before returning to demanding work. Dirt remains on ordinary floors. The player changes a growing zone and a route, not a list of individual medical bills.

## Worst day — a story

Solvent stores run out while outside work has several people caked. The shortage is named; workers use reachable clean ground and ordinary cleaning while the player postpones another raw-tar expedition. A fire brought to natural tar burns according to FlowWorks, with visible danger and no special Sump rain to rescue it. It must not automatically summon a beast or a scripted belch. Work is delayed, not trapped in invisible retry jobs.

## Season's turn — a story

After a season and a reload, the same colony is still growing on eligible margins, keeping prey and predators in a readable population, maintaining chosen paths and spending wax on selected cleanup. A colder interval can stop crops for a visible temperature reason. It has neither become a grass meadow nor been paved automatically into a sterile glass map. Reversing the order of route building and solvent production changes the dirt they endure, not whether the settlement can function. This outcome is unmeasured: the full-map and queue models are specified to test it, not asserted as already true.

## Final lazy-build attack

A beautiful dark map with no tracking fails the exposure bar. A working hediff with a cure that leaves dirty boots fails recovery. A floor that reports filth-proof while a global handler still stuns its users fails the default-scope boundary. A plain mouse that cannot move through its ordinary habitat fails life. Fast default growth that fills every open cell with charged native offspring fails the whole run even if crop and exposure fixtures pass separately. A clean test lane made by disabling dusk is no substitute for these comparisons in the complete default biome.
