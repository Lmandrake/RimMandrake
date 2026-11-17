# Stillsand — page one: what I propose

Stillsand is an exposed ochre plain of deep sand, sparse living things and travelling giants under a fixed sun. Distant rock islands offer caves to explore and secure, rather than automatic safety or guaranteed treasure. Useful discoveries become supplies or equipment through ordinary collection, work or trade to provision the next expedition or outpost.

Land: open corrugated sand, actual geometric shade, dry weather, sparse rock, bones and wreckage.

Life: the existing roster, including buried predators, shade tenants, real flyers and usable ordinary plants and animal products. No animal is evicted.

Signature: cross exposed sand, explore and physically secure a cave, then use its discoveries to provision the next undertaking. The dune gale loses because its carry, return and renewal economy is another complete cycle.

Following review, I move the special workshop as well. Cache food/components/steel, edible clutches, ordinary catches and real trade already support expeditions; deleting solar manufacture does not defeat that experience. Shared raw-sand yield, biosilica, pearls and edible eggs/sacs remain. These are my scope decisions under the cleanse mandate, replacing earlier delegated blanket water/workshop retention. Standing rulings remain binding.

Next version, switched off:

- Furnace, lens bench, glass/lens recipes and fine-sand workshop access.
- Plain solar oven, plain still and brine dipping.
- Gale, carry/return and aftermath.
- Muurrok visits/beam; sand-buster eruption/brood.
- Thumper, geophone, fishing attraction, acoustic payload.
- Horn, den quest, special campaign cave/seep routes.
- Debt, Return, corpse wringing, pour/wet line, hourbloom.
- Sieve, pearl/canon lens upgrades, crest oven, salt boiling.
- Glare/goggles, dung growth, dune song, bone harp.
- Ordinary giant corpse conversion and special desiccation.

I recommend retiring the sun turret (extra weapon economy), delayed horizon arrivals (duplicate information and another queue), mirage punishment (duplicates heatstroke), extra fossil scatter (duplicates sparse bones), cooling draught (unneeded thermal potion), and obsolete biome heat policy (contradicts shared Direct Sun). Code/defs stay; retirement is yours. Prohibited heat semantics cannot be re-enabled.

Before: 71 inventory capabilities [measured: concept record.json], 14 bars, all 14 assigned live methods [measured: tree.json tier_proposed]. After splitting mixed capabilities and naming dependencies: 91 census rows; 43 retained, 38 next version, 10 retirement/exclusion rows. Those 10 include 4 already-cut historical rows, not fresh retirement requests. Passing scope: 8 bars, 5 live-only bars; 12 regression checks and 15 build rules. The whole bar runs the complete season with midway reload and reordered actions.

This remains a proposal for Design Version 0.1.0 [standing Design Versions ruling]. Nothing changes until you read these pages and say so; independent review and the existing build hold remain in force.

# Page two: what to check

The ambiguity decisions that changed the build:

- “Empty ocean”: exposed travel between destinations, with functioning sparse life.
- “Harbour”: explored, currently secure physical shelter; no quest flag or automatic immunity.
- “Fortune”: usable provisions/equipment or actual ordinary trade, never guaranteed wealth or renewable loot.
- “Cool cave”: blocks Direct Sun; ordinary hot air remains. Remove obsolete drip/cooling claims.
- Low sun: roofs and parasols still cover; replace legacy heat branches and false advice.
- Moving shade: follows the actual giant; its former position cannot remain protected.
- “Preserved cave”: recorded roofed cells and owned state only; carried/outside contents resume ordinary decay.
- “Current water”: keep actual edible egg/sac use and optional provider integration; production, pouring and religion move. Wetness expiry is not film water.
- “Useful lenses”: optional workshop, not required resupply. No fine-sand trader is established; the actual sieve route also stays deferred.
- “Seep”: environmental brine, food web and possible refuge; no promised drinking-water fortune.
- “Off”: stops producers, jobs, offers, queues and tier activation; hiding UI is insufficient.
- Saved extras: finish/recover old entities visibly; never delete a pawn to meet absence.
- “Whole”: full map, all kept mechanics on, ordinary weather unlocked; a showcase pad cannot certify it.

The delegated root names the workshop; I defer it by default under this cleanse mandate. Say yes to keeping that workshop and it returns as kept scope, with its supplier and output-use specification required before acceptance.

Without DBH, deferred still-water is non-ingestible carried/trade stock, never an ordinary drink or cooling treatment. Existing edible eggs/sacs retain actual ingestion. The cooling hediff has no located ordinary drink hookup; its positive test remains explicitly unavailable.

Models specified, first to build first:

- Situation generator: cave, creature, item, ordinary work and save transitions; find ownership or activation failures.
- Whole-map season: coupled sand, growth, animals and ordinary supply; find floods, starvation or stalls.
- Geometry sweep: cover, moving shadows and chamber approaches across legal placements and bearings.
- Provisioning model: actual useful-find routes, buyer acceptance, contention and lost items with every workshop gate off.

There are 4 models, 8 unknown interaction groups, 55 tickets and 0 owner questions. Models require agreement with real game reads. Geometry, ownership, ordinary supply and whole-map feedback remain empirical uncertainties; I have not guessed their results. All reviewer refusals are addressed in this revision, pending the reviewer's second look. No game, bridge, deployment or source edits occurred; no current runtime proof is claimed.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- two bars, or a bar and a rule, that cannot hold together (design/concepts/Stillsand/cleanse/bars.json B_PRESERVE (says, range) vs rule R_REFUGE vs census.json row cave_preservation vs tickets.md T_CAVE). B_PRESERVE says: "After a cave is physically secured, the player can keep eligible contents preserved". Its range then sets the gate as "the existing unowned-giant/current-cell eligibility ... a smaller threatening resident still prevents a secured refuge, but does not acquire a new rot-suppression rule". The code matches the range, not the says: RM_PreciousCaves.cs:424-437 DenHeld() is true only for `p.Faction == null && p.RaceProps.Animal && p.BodySize >= 3f && caveCells.Contains(p.Position)`, and RM_CavePlace.cs:29 runs preservation whenever `preservationEnabled && !comp.DenHeld()`. That includes before first exploration and in caves that are not secured. census.json cave_preservation argues the feature is needed because "Deleting it can rot the intended practical discovery before first exploration", so preservation must run before the cave is secured, against the bar's own words. R_REFUGE says "A returning dangerous unowned occupant suspends cave preservation". That is a danger test, but the predicate is a size test: a harmless wild grazer of giant size (e.g. Aurrok) standing on a cave cell suspends it, and a dangerous small resident (Drazzik/guzzka class) does not. T_CAVE calls the same size test "dangerous held-den occupancy". A builder who gates preservation on 'secured' fails the census argument. A builder who keeps the code passes the range and breaks the says and R_REFUGE. Would pass: One gate for preservation, stated the same way in B_PRESERVE says/accept, R_REFUGE, R_PRESERVE, T_CAVE and the census row. Either (a) preservation is on in any roofed recorded cave not held by a qualifying occupant, including before exploration, with 'qualifying' named as a giant-size unowned wild animal on cave cells, harmless grazers included, and kept apart from 'secured refuge'. Or (b) preservation is gated on the same physical 'secured' state B_REFUGE uses, and the census deletion argument is rewritten so it no longer relies on preservation before exploration. Smallest fix: Take reading (a), which matches the code. Change B_PRESERVE says to: "While no giant-size wild animal holds a roofed cave, its eligible contents stay preserved in the recorded roofed cells, before and after exploration, and return to ordinary decay when that protection is lost." Reword R_REFUGE's preservation clause and T_CAVE's "dangerous held-den occupancy" to the size test. State in B_REFUGE or R_REFUGE that a small threat makes a cave unsecured without suspending preservation.
