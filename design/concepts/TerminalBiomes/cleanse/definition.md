# Terminal Biomes — proposed Design Version 0.1.0

Designer decisions, delegated by this cleanse brief, 2026-11-17. Nothing here changes a ruling or the running mod. The launcher’s fresh review and the owner’s reading precede application. This is a proposal, not certification of current code or art.

## Read basis and limits

The CASE was read first. Ruling basis: CLAUDE.md, biome_rulings.md, standing_rulings.md, biome_mod_architecture.md, NAMING_SCHEME_PLAN.md, ASHKARR_WORLD_DEFINITION.md, the_one_map.md and Alien_Bestiary.md. The later painted-world, floor-only, native-water and Direct Sun rulings take precedence over historical migration prose. The world is fixed; no planet generation, biome repaint or tile-count finding belongs to this proposal. In particular, the Scald is a terminal volcanic crater, not the perched river source still described in its BiomeDef and About.xml. The cast is alien rather than imported Earth organisms or franchise references in the RM tier.

No concept record.json, sheet.md, tree.json, log.md or existing next-version file was present in this checkout; the concept directory initially contained an empty cleanse directory. No waiver is known and none is reopened. The CASE explicitly gives no tree leaves, so old_bars is exactly {}. Existing validation/walk prose is an engineering inventory, not an invented former locked bar set.

Read the four named ledger items, the source/defs/patches/kernels and proof scripts, the validation walk, TerminalBiomes review and the relevant sea sheets/floor agendas. The two closed items establish historical scaffolding and the EH hard-dependency fix; they do not establish current gameplay. The review-fixes item is explicitly a list of unverified review evidence. Present source already fixes some listed problems: source-map carry ownership, terminal sink registration, due-time rearming, persistent graze debt and off-map Sunk recovery. They are not new findings here. No runtime, bridge, build or proof script was run. No current source fingerprint has been compared to a deployed DLL.

The dependency implementations are in this checkout. DivingInteraction’s RM_SeabedSiteParent and RM_SeabedLayer.xml define floor identity, the map generator and ordinary site retention. SeaShores’ RM_SeaShoreUtility and RM_SeaShoresMod supply shore classification and integration. FlowWorks’ RM_LiquidHeat and RM_Weir supply heating and existing bank works. Shared LightLedger.cs supplies the glow API used by WellLedger. Source inspection establishes those seams. Resolved launch, shore weather, native-water classification and live behavior still need composed proof. The local gardener callback exists. No corresponding living keeper was found in source.

## Say the mod

Visit alien sea floors by gravship: the Scald boils, the Grey grows salt, the Chill holds dark fuel, and the Twilight shelters gardens beneath living glass. Their native plants, prey and predators belong to those liquids, and the fish caught at the beach have living counterparts below. In the Twilight, harvestable banks tempt you beside a current that can carry a careless worker into a sink, so routes, warnings and rescue shape the visit.

Land: distinct material, floor, visibility, ordinary weather and building ground, with calm underwater presentation separated from beach weather.

Life: preserve the present rosters, normal native growth/harvest, movement, hunting, ordinary taming and environmental viability; no species eviction.

**Signature.** Replaced by the owner's cards of 2026-11-20 and 2026-11-22: each sea has its own signature, and the Twilight's is the light-wells, with glowing colourful shafts of light under the panes that fade before the floor (the floor between the wells stays dark). The bank, current, surge and sink are shared by all four seas: in the Twilight's 0.1.0, in the other three seas' 0.2.0. Detail: `design/concepts/TerminalBiomes/TwilightSea_design.md` §Scope.

Runner-up: the cultivated-light/tenancy economy. It loses because it adds portable growers, culture, ownership, predators of light and ship maintenance alongside the bank/current chain. Minimal natural well drift and keeper support remain necessary land under the frozen lid laws; they are not a licence to retain that economy. Ordinary hot water, cold fuel and mineral pools use shared environmental rules rather than becoming additional bespoke progression systems.

## Why a player reaches for it

These are destinations for a supplied expedition that wants different resources, living encounters and a place worth navigating. The prediction is that planning a bank route and rescuing a worker makes Twilight visits memorable; enjoyment is not a bar. Vanilla water chiefly obstructs movement and supplies fishing; this kit must show floor life and a working, changing bank boundary. The sources’ GravTide comparison establishes a useful local-floor generation precedent, not proof of our own floor. We borrow no new engine from a donor and promise no alternative planet.

## Using it: first hour, routine, and a large colony

First arrival: the existing ship/layer dependency carries the crew and inventory down. A legal landing reserves its hull and unloading/return corridor outside current and surge reach. The crew can reach working ground without a hatch. Landing is refused or relocated safely if the geometry cannot fit. A broken ship from unrelated combat still needs vanilla repair.

Between visits, standard departure keeps the seabed site and its ticking map by default. DivingInteraction’s RM_SeabedSite is a MapParent eligible as a player home with vanilla Abandon support. Returning to a kept site reuses the same map, including harvest state, the living gardener and the well ledger. WellLedger saves the records via ExposeData and ages them on MapComponentTick without a player-presence gate. An actual reload preserves elapsed age. No time passes while the simulation is paused. Explicit discard or abandonment ends that map; landing again where legal creates a new one. This is the R14 contract, inferred from the shared source and the sea dive spec’s persistence rule. T40 still verifies the composed launch and return path.

First Twilight work: the bed reads as a silt trough with a distinguishable centre and margins; aligned bed detail and inspect text give downstream direction. Stakes mark the outside of surge reach, not the edge of calm safety. B5 requires a cold reader to distinguish the dry-looking bed and stakes from bank silt in unlabelled ordinary play views; a fired warning and correctly placed terrain alone cannot prove that visual boundary. The bank is visibly outside the trough and offers a better harvest than other reachable gathering ground, including lit gardens away from the current. The current map paints ordinary RM_BankSilt on authoritative bank cells. R15 gives eligible gloamurn and hoolimbre placements there extra weight during natural seeding and replenishment, with ordinary crop fertility and off-bank plants preserved. Static weircomb marks the habitat but does not count as harvest. Soil fertility is a tuning input, and the silt-trap conversion to worked silt is deferred. A new worker receives a readable entry warning before carry can become lethal. The centre is not a usable swimming crossing: ordinary pathing through it must be interrupted by carry. Marginal contact permits retreat, not immunity. Loose items drift through the same field; no cargo float is needed to demonstrate it.

Routine: forage and haul along safe ground; keep the sink approach reachable; use existing arrest works and a harness when deliberately working close. The harness slows the cost, never erases it. An undersurge announces and visibly widens the reach; the stakes and direction remain truthful. The player can withdraw beyond it without abandoning the ship. Banks may be depleted by harvest, but native growth is real and not scripted infinite food.

At 40 colonists: repeated work orders, moving animals, stockpiles and rescue jobs coexist on full maps. Existing field membership, light caches, native growth and pathfinding must remain coherent across crowds, multiple loaded floors, map transfers and save/load. No fixed wall-time target is an owner bar; a task or clock that stops progressing is a visible failure. The whole-system model measures work budgets to guide rules and tuning.

## What changes in the colony’s story

A sea visit has an arrival, a safe working edge, temptation beyond it, a bad choice and a possible recovery. Twilight’s living lid, its overhead gardener and temporary columns show a living garden. Campaign bottom dwellings, residents, plots, moorings and lamplight move to the next version: their removal leaves the land, native life and current signature intact. This is my scope decision under the later cleansing card, not a cancellation of the frozen sheet’s initial inhabited-reveal promise or its peaceful-holdings doctrine. RM passes independently of that campaign content. No tenancy, claim-buoy commerce, rent, special quest or new faction hostility is retained.

## Costs and ordinary materials

The ship carries ordinary food, water, power and environmental protection. This version does not add a machine to solve every environmental cost. Scald body water and its cooler margin never become potable; steam being clean means free of the lake’s fouling, not a separate poison or health currency. A condenser can produce a distinct distilled resource when its next-version feature is enabled, but default play does not depend on it.

On the Scald beach, Odyssey’s ordinary HotSpring thought accompanies contact burns from the boiling water. The cooler RM_ScaldMargin provides comfort and normal bathing without contact burns. Neither water supplies a drink. Dry shore also ends contact. Below, walkable RM_ScaldFloorSubstrate replaces the boiling terrain bands while keeping native mat habitat. Vents and bubbles remain visible. The floor is hot through the ordinary ambient temperature path, and the working route from the hull needs no burning pools. Native biology remains the environmental exception. The Chill is cold and oxygen-poor, with hull atmosphere and ordinary protective gear from the existing floor dependency. Native fuel organisms are unsuitable as ordinary colonist food. Stonewater keeps its ordinary harvest and cooking use. Its custom extractor and refinery chains move. Ordinary material harvesting, including natural salt, remains.

## When it goes wrong and the readable sign

A current victim retains identity and a location in the basin, with a visible Sunk condition and an actionable warning. The basin is a terminal destination, not another carrying cell that repeatedly re-registers arrivals. A blocked landing location never defaults to an unchecked occupied cell; report a placement failure and keep the victim findable at the last valid position until safe placement is available. It must not become a perpetual sink-teleport loop.

Rescue requires leaving dangerous liquid into reachable safe shelter or a safe carrier. Safe carriage means held by a living rescuer/ship outside the active hazard, or already transferred to a valid safe destination; merely being unspawned is not sufficient. A roof erected over live sinking water is not rescue. A dead/interrupted rescuer leaves the victim or corpse in a readable place. Neglect can kill; no pawn or animal disappears without remains, a location or another explicit readable transition. Existing off-map recovery code is evidence of an earlier fix, not proof this tighter predicate already holds.

The protected giant gardener lives far overhead under the waveglass on every active Twilight floor and is visible swimming in ordinary play. Its living state and stable identity belong to the retained floor. The far-overhead presentation leaves the floor’s paths and occupancy free. Rim overgrowth, grazing and patch jobs, and selectable ceiling routing are next-version work.

My delegated limit for this version keeps the animal alive and present whenever the waveglass stands. Ordinary play offers no way to harm, hunt, capture, tame, trade or transfer it, and environmental and health conditions cannot remove it. Any applicable attempt receives a readable protection reason. Save/load and ordinary departure preserve the same living individual. The lore’s last-gardener death would kill the roof. If the player opts out of the entire living-lid feature, keep the saved animal and roof together.

Light columns stay finite on the Twilight sheet’s years scale. Ordinary inspection shows a decreasing countdown and the light visibly wanes. At expiry the old light ends. Normal updates open replacement wells on eligible garden ground using authoritative current membership, hull exclusion and ordinary habitat. R7 preserves well identities and stage when migrating old week-clock saves. B7 reads both same-well aging on retained visits and actual expiry and replacement from a staged start through the normal update path. K11 is a separate regression sweep. B8 observes reachable gardens and ordinary aging alongside current, forage and predation with well ages and lifetimes unedited.

## Edges and deletion arguments

Ordinary roster bodies, static glow, ordinary harvests and viable native feeding/drinking remain. This is not a blanket exemption for unusual species mechanics. Contact venom, weather-retraction art, fuselight explosion, tarnn wake, hesuun extrusion, plant charge/wilt and well-triggered special spreading all move; the bodies remain. Replace event-only placement with ordinary habitat placement so deleting an extra does not empty the life roster. The death-drop organ and special loot move without removing the creature. Natural creature light must move with its body, which is why its registration adapter stays.

Scald steam presentation belongs to the beach; the floor has submerged bubbles and no weather-steam exposure clock. Grey salt fall is crystals in water, not cold snow or water rain. Mineral crowding is allowed while Grey wild animals arrive singly and remain dispersed. Under the Twilight lid niim form lit shoals and noolim form dim-water shoals. Initial seeding and later replenishment both have to produce this pattern. Shore animals remain solitary. Brief convergence at a shared resource does not constitute a shoal. Chill ice is floor bedrock/crust or a neighbouring beach, never a new location on the lake’s top. There is no native-land-predator invasion or new free immunity to boil traversal.

The explicit exceptions retained as needed support are current warnings/inspection, the float harness and existing arrest interfaces, findable sink recovery, natural light registration and the living protected gardener. Their deletion respectively destroys informed use, preparation, consequences, moving life or the roof’s creature-and-light law. Removing inhabitants does none of those things, so the inhabited reveal is deferred rather than treated as an exception. Settings, aliases and defensive guards are inherited/load support, not extra experiences. No bars demand a particular yield, density, duration, variant count, art path or numerical equilibrium.

## Neighbours and contracts

The mod remains a source member of the composed Baroque Biomes package. RM has generic names/defs/classes; Star Wars additions belong in the scenario patch tier; Ash’karr placement and Compact story belong in Utinni. RM_Eldspar’s RUT_AuroraGlass harvest is a concrete tier-binding risk, ticketed, not silently renamed. The available base rosters show no repeated animal across these named sea defs. This is not a complete patched/global multi-home measurement: RM_Bulloo references TheForge, some sea creatures and juveniles have broader historical placements, and unavailable campaign patches may add homes. Preserve all current assignments; no eviction or invented migration explanation.

CreatureBehaviors supplies ordinary creature behaviours, native adaptation interfaces, real flight for fictional flyers and the sole Direct Sun geometry. ExplosiveGrowth supplies normal growth and wet-source integration without adding bloom incidents. EnvironmentalHazards supplies weather pulses, presentation helpers and mechanic gates without a private steam-health system. FlowWorks supplies material contact/heat, water classification and public bank-work arrest seams; no river redesign. Wreckage supplies ordinary scatter/salvage/decay. Bones supplies ordinary butchery remains. DivingInteraction/SeaShores supply ship/layer access, floor environment and beach material delivery. Shared LightLedger composes existing contributions. Campaign inhabited holdings are deferred opt-in content; no kept feature or passing bar depends on them. Unresolved kept-engine contracts are first instrument work, not proof of absence everywhere.

## Settings

Ship master on, each sea on. Expose on/off per major kept mechanic: ordinary land presentation, normal life adaptations, natural well lifecycle, current, surge and warnings. Show effective parent state, shipped tuning/reset, and whether a change applies now or on the next local floor. All-off stops scripted behaviour without removing defs, destroying held things, leaving a launch restriction or blocking return travel. Do not switch off the world’s literal terrain or undo the fixed planet. An explicitly opted-out sandbox is not the default fiction.

Next-version options default false in both initialization and missing-value Scribe load. Each option is labelled next version, and gates construction, recipes, research, trade, incidents, map ticks, running jobs and reload reassertion wherever relevant. Natural counterparts remain available. Existing saved opt-ins need a readable migration, not a silent state purge. The 2026-10-15 owner card keeps existing cross-biome controls, default off and labelled “Unsupported: may work outside our biomes, not tested”. Cross-biome validation is released. No new worldgen control.

## First hour

The crew arrives beneath the Twilight lid. Gold columns pick out a garden; the bank path runs between the ship and forage. A worker starts toward a tempting patch across the bed, reads the warning and retreats. The scene already supplies the mod’s promise without rent, a pane strike or a custom farming station.

## An ordinary week

Foragers work the banks and loose dropped stock shows the downstream direction. A warned surge widens the reach; the crew brings workers beyond the stakes and resumes after calm returns. Native prey feed and predators hunt while harvest changes the accessible patches. The giant animal swims far overhead while well clocks continue normally. Campaign dwellings and residents remain absent at default settings.

## The worst day

A worker ignores the boundary and is carried into the sink. The warning selects a findable victim. A rescuer dies on the approach, leaving a body and an interrupted job rather than deleting either pawn. A second rescuer uses reachable safe ground, carries the worker into the hull and the condition improves. Reloading during that carriage preserves the outcome; roofing the sink would not have saved them.

## The season’s turn

The visit continues across natural current changes and ordinary native growth. A mid-way save survives reload, and hauling before foraging produces another viable route. While the crew works and later returns to the retained Twilight floor, the same living keeper is overhead and the same active well has less time left. Well sites migrate on their own years-scale clock. The Grey keeps its mineral murk, the Scald still boils at the beach and the Chill still demands heat. The whole-mod recorder tests this prediction.
