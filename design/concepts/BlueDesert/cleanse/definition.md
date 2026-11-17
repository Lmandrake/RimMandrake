# Blue Desert — proposed Design Version 0.1.0

This is the Designer's proposal, not an applied change or an owner quotation. Nothing here changes the mod, its ledger, its rulings or its old concept records. No live evidence was collected. The requested concept root contains only this proposal destination: there is no supplied sheet, record, log, next-version file or tree to overwrite. The earlier rehearsal under `design/RimMandrake/designer_codex_2026-11-09/BlueDesert/` supplies inventory and later owner answers; its old guesses are not answers. There are no old tree leaves to map.

Blue Desert is an open, ancient ice plateau whose blue distance resolves into pale ice and transparent, branching life. Its useful native growth and creatures are cold-stable fuel: damage or warming can turn a connected patch, and the cargo taken from it, into an explosive chain. Crews prepare a work site, keep an exit clear, mine ordinary water ice and recover old salvage, then keep native cargo cold at home.

Land: old water ice, ice-grain weather, poor visibility in fog, physical abandoned extraction sites, and useful ordinary ice/salvage.

Life: the existing low flora and resident food web, wild harvesting, cold-dependent native bodies/products, tameable dovvik and actual vrisk flight.

Signature: **Cold preserves useful native fuel; disturbing or warming it can propagate a blast from the living field into the colony's cargo, so preparation and cold handling matter.**

Runner-up: archaeological study and thaw-awakened siege forms. It lost because an unlock ladder plus a separate campaign threat would create another defining system. Static abandoned work remains land; reading tiers, timed discovery and crysalis delivery move together to the next version. The owner’s November ordinary-mining answer also removes the premise for a special cold-cutting technique.

## Why a player reaches for it

It offers an alien, beautiful place where profitable work changes how the colony plans heat, routes and storage. Premium water ice and old material salvage are useful even before native fuel is collected. The fuel is tempting because it is usable, rather than a decorative dangerous item: an ordinary bill at the vanilla biofuel refinery (`BiofuelRefinery`) converts cold-handled wax into ordinary vanilla `Chemfuel`, as specified in the ratified life brief section 7. This consumer is absent in current source. The bench already serves refinery bills in `src/RimMandrake/Abyss/Defs/RecipeDefs/RM_Recipes_Chemfuel.xml` and `src/RimMandrake/TerminalBiomes/Defs/RecipeDefs/RM_TheChillFuelChain.xml`. The existing recipe ownership supports that bench choice. Wax remains reactive throughout the bill work, and a warm workroom ruins or wicks the input before completion.

Prediction, not a bar: deliberate preparation followed by a small avoidable disaster should be more interesting than repeated arbitrary instant losses. The player is choosing exposure and containment, not guessing an invisible mining roll.

## Using it

First hour: land with cold protection and ordinary supplies. The local map has walkable ice, naturally present low plants and living native animals. The colony need not eat native biology: it supplies no human-food self-sufficiency promise. A physical abandoned extraction face and equipment lead to accessible mineable ice. Plain scene context explains an earlier attempt, without requiring a campaign faction, special lore letter or untranslated-script interaction. The crew cuts/harvests live growth along its working route, moves reactive harvest away from the exit, and uses the normal Mine job. Pick speed generates neither a special heat budget nor a loot roll.

Routine: harvest wild flora rather than sowing it. Most plants yield wax; qeshra supplies cold-handled native feed, vashpuk uses ordinary repeated harvesting, lisqueth has static light, and the Garden shapes remain ordinary plants with the same charge mechanism. Hazebell timed opening, vapor and post-Haze clock are off. The existing naming exceptions stand. No species is evicted. A tame dovvik is a native grazer, not a temporary-safety tool. A visible murrek remains a predator, without reseeding or invisibility jobs. Ossivel are herd animals; the previously cut choir and virr song stay cut.

Native grazing removes a plant safely through ingestion; normal cut/harvest is also safe. Damage-killing a plant releases its charge. Sustained warming advances a warning state and then releases the charge; a brief harmless temperature excursion must not masquerade as a resolved full warming test. Before irreversible ignition, removing heat/cooling arrests the warming hazard. Once an actual wick or blast has begun, cooling is not promised to undo it. Sound reinforces a locatable inspect/notification state rather than being the only warning.

At 40-colonist scale, use several cold storage areas and deliberate hauling routes. Loose water ice absorbs finite heat without a rack. Door traffic, large rooms and heaters can exhaust it. In a prepared closed hold under its declared ordinary heat load, loose ice alone keeps the room cold far longer than an ordinary cooling repair. A matched unrepaired hold must still be cold with substantial reserve after real workers finish the repair. Reducing traffic and restoring powered cooling remain ordinary work. Open-door bursts, exhausted reserves and deliberately excessive heat are separate stress cases. The thermal model must establish the supported room/load regimes. No new hauling or excavation job is required. A poor stockpile order can carry wax through an apparently safe gap and reconnect the fuel graph. Preparation must consider corpses, animals and carried cargo, not only plants.

## What changes in the colony's story

A work site is a decision to separate useful fuel from the operation and keep its exit usable. Old equipment and an abandoned face are evidence that earlier crews made the same choice. The retained scene need not tell every civilization's history. A prepared crew can recover water and salvage with ordinary labor; a crew shooting a Burner in connected growth may explain its own disaster afterward.

The Swallower's sealed gut and its rupture are an innate body adaptation, kept as life. The Burner's oxidation halo is a visible biological distinction, not a second combat system. Its death releases fuel once through the chosen charge path: the duplicate local BigExplosion action is recommended for retirement, while its class remains available to the propane-lake ascendant consumer. Most native death charges are not made heat-gated; that exception belongs specifically to the vhaulk. A kinetic or cold kill does not detonate that cistern, but its cold corpse is still an organic hazard. A heat-family death and any EMP hit on a living vhaulk retain their ruled consequences. An off-map death cannot explode on an unrelated map.

The existing vhaulk still walks away with a readable sign. Taming, downing, a blocked edge, an interrupted job or map teardown never permits silent disposal. The later giant-ground-exposure answer belongs to a future separate passage system, not restoration of the already cut rime road or enlargement of the existing vhaulk.

## Costs

Cold protection, work-site preparation, ordinary salvage/mining time, separate reactive stockpiles and repairable cooling are the costs. Water ice and heat capacity are finite; every conversion route must account for the same material and residual reserve. Metal and water are inert. Hydrocarbon organs, feed, wax and corpses retain their cold-dependent hazard through storage, carrying, splitting and reload. Wax remains reactive during refinery work until a completed cold-room bill yields ordinary Chemfuel. Pure carbon is an inorganic exception in the older char-lace definition, but its production is off in this version.

Wild native food is not cultivated. Qeshra roe is native feed; foreign ingestion must be visibly incompatible, rather than merely discouraged by food preference. ColdStorage's preserved-roe recipes are an extra and must be gated separately. Shared Bones output cannot quietly contradict the organic rule: declared mineralized inorganic bone may be inert; organic components must preserve the hazard. This is a local product contract, not a new Bones design.

Wax refining uses the existing refinery and ordinary bill work. A properly cold workspace keeps input stacks and the bench interaction cell at or below the loaded wax safe limit. The current value is -1 °C [measured from `src/RimMandrake/BlueDesert/Defs/ThingDefs_Items/RM_ColdWax.xml`, `maxSafeTemperature`]. The wax bill adds no temperature interlock. The input retains its warning/ruin/wick state throughout work and interruptions, including cancellation and reload. A warm workroom ruins or wicks the wax before the bill finishes. Recipe quantities remain tuning checks from the life brief.

Completed cold-room work yields ordinary vanilla `Chemfuel`, with vanilla stack merging, refueling and consumption. The ratified life brief section 7 explicitly says to refine wax in a cold room and “it is ordinary fuel.” T13 supplies the ordinary bill and verifies both the ingredient hazard during work and the completed output's ordinary fuel behavior.

## When it goes wrong and its sign

A warm field has an identified charge warning and crack; it can then propagate discrete explosions along reachable fuel/heat paths. The warning lets an attentive crew stop a heat source and withdraw before irreversible ignition under the declared reachable-site cases. A sudden lethal shot or EMP hit is a described immediate hazard, not a fake delayed warning case. The warning must remain meaningful after a save made mid-countdown.

Native feed makes foreign eaters visibly ill rather than becoming ordinary hay. Warm stored organics show progress and an identified recovery action before their wick; native corpses get the same continuity. The dead do not become safe by bypassing generated-def injection. Departure is an actual exit or transport with a sign; death is a corpse/blast event. No creature vanishes to keep the model stable.

Deep ice-sand buildup reaches the approach cells beside walls, doors and hulls, applying the thickest SandGrid category's movement cost until crews work a sand-clear area or deposits erode. “Against” describes adjacent deposits. The owner card at `BLUEDESERT_DESIGN_SITTING_1`, recorded in the biome sheet section 4b amendment, rules SandGrid path-cost burial. The supplied R1 engine evidence gives Thick buildup +12 movement ticks per cell at depth 0.75 or above, with zero depth under full-fillage buildings. Read permitted approach cells beside those footprints. Attribute deposited path cost through depth, trip and clearing reads with drift weather ended or matched between routes. The drift weather itself slows movement, so timing an in-storm trip alone cannot prove buildup. Fog reduces targeting reach/accuracy and movement while present, with normal recovery when it lifts. Its independent shuttle-launch prohibition is off. Haze remains a settling atmospheric veil; its skin/lung exposure meter is off. Weather must rotate naturally during acceptance; a locked clear sky invalidates the whole bar.

## Edges

No world generation, seed sweep, alternative planet, planetary painting, tile reassignment or tile-count gate. Existing local map content placement is not permission to create another world. Proposed models consume captured local geometries and state ranges; they do not generate planets. Map construction for tests happens later on disposable fixtures, never on the canonical save.

No new roster, eviction, mining-tech research, variable pick-heat model, global block-count loot, bespoke study/rite/quest, ablation-timer gifts, scanner prose, safe-trail minigame, valve job, special gravship digging or giant passage in this version. No resurrection of the owner's cut soundscape, rime road or rack drip. No attempt to treat a light chemical metaphor as laboratory chemistry: the world lore supplies the fuel rule; the biome's ground is ordinary water ice, not explosive hydrocarbon ice.

Objects held in containers must retain identity and hazard progress. Off-map simulation must at least carry debt/progress and apply it honestly on return, without a surprise unlocated map blast or free refrigeration. T12/T17 require the lifecycle contract before these states can pass. No claim of perfect molecular heat transfer, atmospheric scattering or deterministic survival after a deliberate full-map ignition.

## Neighbors

The one fixed Ash'karr uses angular distance from the substellar point, not latitude bands; this nightside does not get invented sun heat. `the_one_map.md`, the current world definition and later biome rulings outrank outdated per-sector/no-bullseye wording on the old biome sheet. We change none of them. The RM biome remains a composed member under `mandrake.rm.biomes`, with RM identity, not a new standalone release. All DLC remain assumed.

CreatureBehaviors supplies the geometric Direct Sun and existing ordinary departure notices. ExplosiveGrowth is a shared growth compatibility surface, not this mod's explosion engine: it must not make water-dependent/sown plants sprout here. EnvironmentalHazards supplies gate/type/exposure/optional storm services; disabled local film and storm producers still retain resolvable defs. Wreckage supplies physical wreck placement, salvage and weathering. Bones supplies global butchery output, with the local product compatibility requirement above. None is redesigned.

FlowWorks already consumes ice and meltwater; reuse its liquid/potable-water contracts and reconcile mass. ColdStorage already consumes roe, so its adapter must be gated at the consumer, not hidden by removing qeshra. Watchers can still resolve the dormant buried-murrek hediff but should see no naturally buried murrek by default. AcousticScanner's general engine stays available; only bespoke local payload is off. NightHorrors already owns crysalises; no duplicate common-biome engine or default mining link is added.

Roster note: `RSW_Vapaad` is patch-added by Utinni and has other `wildBiomes` in SWBestiary; keep it and note multi-homing, without enforcement. Its ordinary meat/leather and cold/metabolic adaptation are not demonstrated by this reading. `RM_Thunderbeast` likewise lacks the native marker and uses pig leather. The default is to keep both roster identities and require local-compatible physiology/product adapters; no silent exception to the hydrocarbon rule, no global bestiary rewrite. If such adaptation cannot preserve species identity, this is a real owner conflict, stated on his pages. The proposal does not certify that combination today.

Vanilla comparisons that shaped this cut: normal Mine and ordinary bills already explain mineral extraction; WildPlantSpawner and predator hunting already explain ordinary life; vanilla temperature and explosive wicks explain room costs; boomalopes demonstrate an individual death blast but not containment across native field/cargo. The retained chain, lifecycle and preparation are the added experience, not another loot incident or appliance.

## Settings

Retained default-on groups: master mechanics, native fuel releases and ruled vhaulk triggers, flora damage/warm chains, foreign-ingestion response, native-product reactivity, readable warning cues, loose-ice thermal reserve, ordinary weather and biological visual tells/departure behavior. Existing flora roster controls remain default-on; independent char-lace/bloom switches must not disable the retained plants. Shipped defaults are this definition after application, not today's all-true source snapshot.

Every moved built extra has an independent setting labelled **Next version**, default off, and preserves its defs/code in the tree. Recommended retirements remain off pending the owner's choice, not deleted. Features with no implementation have no executable default path. Independent controls must not make a switch labelled off broaden danger: notably the current vhaulk heat-gate off behavior changes deaths to universal detonation and must be replaced with a truthful disable policy. Master/all-off neutralizes scripted local hazards/cooling/events, leaves world/roster identities intact and does not delete saved objects. Ordinary Core weather travel modifiers remain ordinary terrain/weather and must be labelled when not controlled by master. Cues may mute audio but may not remove all readable warning. T11 states migration and transition requirements.

Already active optional events on older saves finish a labelled bounded cleanup without producing untested output; buried animals surface visibly, haze film decays, rack fuel stays inertly stored. Exact policies are tickets. Reset/search/persistence are floor checks, not extra passing bars. Existing cross-biome options, if any are discovered, stay unsupported/off; build no new one.

## First hour

The crew sees blue distance and clear low shapes near its boots. It marks an old extraction face, cuts plants beside the approach, moves their wax to a cold stockpile and mines ordinary water ice. Their preparation changes where a later blast can reach, not how hard a pick swings.

## Ordinary week

Dovvik and prey feed in the cold while predators move between patches. Fog interrupts a long shot; drift slows a hauling route until it clears. The colony harvests wild feed and wax, turns gathered resources into water and ordinary Chemfuel by refining wax in a cold room, and checks whether regrowth or a dropped stack has reconnected yesterday's work site.

## Worst day

Power fails in a busy cold hold while a fueled heater in the neighboring room continues leaking heat into it. In the matched no-ice hold, that heat raises the room past the wax safe limit. Loose ice keeps the prepared closed hold below that limit with reserve for well beyond the ordinary repair while a worker cuts unnecessary traffic and another restores cooling. A neglected organic stack warns; a crew that ignores it sees a wick and an attributed chain. The same warning and remaining reserve persist across a reload; the game has not secretly reset their chance to respond.

## Season's turn

The colony returns to the old face after weather and feeding have changed the surrounding connections. A local careless shot may have scarred one patch, but the map is still alive and offers work. A mid-season reload and reversed haul/clear/mine order must preserve that story. We do not yet know whether the current blast, density, growth and predation rules can sustain it: the whole-season and containment models are explicit first build work, not a declaration of balance.
