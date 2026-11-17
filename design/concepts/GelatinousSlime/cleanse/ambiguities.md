# Decisions that change scope, construction or passing

Every selection below is mine as Designer under the current brief. Source establishes the fact or prior intent, not an owner endorsement of my new wording. Deferred systems keep their already answered constraints; the record contains no waiver to reopen. Missing runtime observations remain unknown.

### The defining experience

Two readings: the mod is the selected-gene expedition, with ordinary biome content as its stage; or the first version is ordinary life on a useful, absorbing body. Consequence: the former needs archive curation, navigation, extraction, coma, inheritance and social state before any biome can pass. I select the ordinary material/contact chain and defer the expedition. The concrete counterargument is the original owner instruction in `RM_gelatinous_slime_mod.md` and the later delegated flagship pick, not a lack of imagination. The new cleansing card explicitly delegates scope and requires land, life and one signature. Deferring this request preserves it without requiring both signatures now. The fresh reviewer correctly identified concrete evidence against this default, so owner_pages.md page two now carries Q1: the choice, verbatim-flow/centerpiece/showcase evidence, the material/contact default and the required redefinition if he chooses the expedition. The default remains in force for this proposal; no owner answer or acceptance is invented.

### Colonists acquiring resistance (R1)

Two readings: moving the archive journey leaves an unspecified first-version colonist immunity route; or it also defers new resistance acquisition. Consequence: the latter gives up the owner's explicit acquirable-resistance economy, law 1 (2026-09-10, RM_gelatinous_slime_mod.md §3). I take the latter as a scope proposal and disclose the conflict under Q1 before application, without changing the ruling or claiming a replacement route. Floors, processing, drying and antidote still permit ordinary settlement. If the owner keeps acquirable resistance, retain a priced RM_Gene_SlimeResistance route independently of the expedition if needed, with a use_body or escape picture and delivery ticket. SlimeGenes.xml and DefaultArchive.xml establish the promised gene and acquisition; RM_SlimeResistant is a race-extension identity, not a colonist acquisition action. Existing active genes and native resistance checks stay functional. The reviewer is right that this loss needed its own census row and explicit disclosure.

### “A living, spreading superorganism”

Two readings: a strategic organism conquers neighbouring world tiles; or the existing terrain, native organisms and shared plant tops express local assimilation. Consequence: the first introduces world mutation and a new spread engine. I select local terrain/life/contact, including existing Slime growth tops, never world-tile conquest. Source: CASE root line, `RM_TopResolver.Slime`, fixed-world/no-worldgen rulings, frozen sheet's little-to-no-sentience and connected-body lore. No planet-scale expansion model is requested.

### “Reading,” “library,” “body,” and “the fee”

Two readings: conscious targeting with a literal per-cell genome store; or figurative assimilation and its progressive health cost. Consequence: a builder could create thinking AI or revive the deferred archive to make the metaphor true. I select assimilation; ordinary land requires no database interface or intent. Source: frozen `the_slime.md` §§1,3,6. Bars either use literal contact/film/outcome language or list the surviving figurative term and a nonliteral accepting picture. In use_body, harvesting means bellows/forage raw slime, never terrain excavation or creature butchery (`SlimeFlora.xml` RM_Plant_Bellows harvestedThingDef). In escape, body means contact-active terrain; an early patient can leave it for a floor without leaving the biome. “Drying country” means a loaded DryingBiomeExtension on the current map or supported caravan tile (`Patches/DryingBiomes.xml`), including tagged salt geography, never hardened crust or merely arid-looking untagged land. Each is now marked in its own bar rather than relying on another bar’s glossary.

### “Everything belonging here” versus optional extras

Two readings: every historically requested capability remains default-on because code exists; or each independent player-facing chain must earn this version. Consequence: the old broad root never shrinks. I select the latter, using an explicit deletion test per census row. Source callers prove coupling, not experiential necessity. Genomics, resurrection, bombs/seals, gourmet cuisine, ruins, paving and wound spawning move; ordinary weather, growth, feeding and resource processing earn their places separately.

### Worldgen for other players

Two readings: the older universal-mod spec licenses generated planets despite Ash'karr's fixed world; or the explicit current no-worldgen instruction applies in every version. Consequence: a rarity slider could silently remain an authorized alternative-planet feature. I select no worldgen and recommend permanent retirement of the scoring feature; retain inert code/defs until the owner retires it. Sources: current brief; CLAUDE.md worldgen ban; stale contrary prose in `SlimeBiome.cs` and the old mod brief is disclosed, not adopted. This does not delete the BiomeDef, animals or ordinary local-map content.

### Planet generation versus existing local content hooks

Two readings: a BiomeDef or local initial animal hook is itself an offer to generate alternative worlds; or fixed-world biome content and existing local map population can exist without any player worldgen capability. Consequence: conflating them either restores forbidden worldgen or deletes ordinary flora/animals. I retain the authored biome and existing scoped local population data, propose no generator and perform no map creation. Existing farm-ruin generation is deferred as an extra. Geometry inputs are local cell arrangements, not world seeds. No rarity setting can re-enable planet scoring.

### “Dry” hardened slime

Two readings: a hardened shelf is safe or converts workers more slowly; or it is still tagged living contact ground. Consequence: a player builds a roofed crust hospital and patients continue accumulating film unexpectedly. I select active contact at the ordinary rate; only constructed non-slime flooring blocks that contact, and a declared drying biome reverses established film. Evidence: all primary terrains inherit `RM_SlimeTerrain`; exposure has no hardened-specific rate. Correct the contradictory “more slowly” description rather than invent a hidden rate branch.

### Roof, floor, bed and carried patient

Two readings: any shelter or furniture blocks slime; or current top terrain at the held position controls contact, with drying geography separately resolved. Consequence: a bed on exposed ground could falsely pass as a safe treatment room. I select actual top-terrain/holder-position semantics (`SlimeUtility.IsBeingRead/BiomeOf`), independent shared roof sun/rain rules and real completed treatment in beds. Death/release paths must use a valid map or caravan holder and never discard gear because no map cell exists.

### “Footprints always”

Two readings: the frozen passage-mark request is essential land; or it is a separable custom detail under the cleansing brief. Consequence: the former requires a new warm-ground renderer before the terrain can pass. I move it unbuilt to the next version under T18 (R2). Removing marks leaves firm shelves, soft mats, liquid channels and their building/travel affordances readable, so the reviewer is right that the old rationale only repeated the request. `SlimeTerrain.xml` documents snow-only footprints and no warm-ground provider was found; nothing needs switching off. Ground no longer requires marks.

### Outsiders “visibly” absorbed (R3)

Two readings: a body overlay marks every filmed outsider; or health, inspect and actual impairment expose absorption while the sprite is unchanged. Consequence: the first restores the explicitly deferred film renderer. I take the second and make residents.says literal: “readably being absorbed (health and inspect).” Its accepting picture explicitly leaves the sprite unchanged. The reviewer is right that “visibly” could demand the moved extra.

### “The ground strikes back” / slime in the eyes

Two readings: a new random terrain-attack projectile system is owed; or established film causes sight/manipulation/movement impairment. Consequence: inventing a separate hazard adds another attack loop. I select the existing progressive film sight impairment as the first-version consequence, from `Slimification.xml` and the current contact source. The frozen sheet's warning is retained as impairment, not a separate new attack mechanic. No additional hit-frequency or projectile promise is introduced.

### “Never hostile” / “nothing here is hostile”

Two readings: every native, outsider and encounter is harmless, with all predator jobs forcibly suppressed; or conversion itself never grants hostility while ordinary native predation, retaliation and acid deaths retain their causes. Consequence: the former deletes the fubbum and giant's ecological roles. I select the latter, grounded in the current concept's recorded non-hostility clarification and `SlimeVisitors.cs`/`Slimification.cs`. Existing late-film mental-state suppression does not prove every normal hunting job is cancelled. Rewrite misleading blanket peace text. No sentience, faction recruitment or new aggression may come from absorption.

### “About a week,” terminal stage and a warning clock

Two readings: the late warning stage is death, or all pawns receive an identical wall-clock countdown; or severity/location/clock settings determine remaining life and terminal dissolution is separate. Consequence: treatment could be refused while still possible, or drying patients get false “hours left” messages. I select separate warning and terminal states with truthful rate context. Production source thresholds are 0, .2, .5, .9 and terminal 1; ordinary growth is calibrated around the sourced week, settings permit 2..30 days. These are checks/ranges, not numerical bars. Source: `RM_SlimeLadder` and `HediffComp_Slimification`.

### Early wipe-off versus advanced hold

Two readings: stepping off slime always cures; or early ordinary film decays, advanced ordinary film holds in neutral country and needs drying geography or treatment. Consequence: the universal step-off cure erases the real exit-planning problem. I select the latter from `RM_SlimeLadder.RatePerDay` and the recorded concept decision. Rainwater does not restart an injected clock; the gene dose that sets that flag is deferred.

### Map travel and caravan travel

Two readings: a map-only rate model suffices; or location transitions and off-map ticking must produce the same declared cure semantics and readable loss. Consequence: a caravan can falsely “dry” by failing to tick, or terminal goods disappear without a recoverable holder. I select the real caravan/holder transition obligation. Evidence: `SlimeUtility.BiomeOf` and hediff tick source expressly claim caravan support, but current proof notes say transit/terminal inventory is unproven. M1/T28 require game transition calibration, not extrapolation from a map helper.

### “Cures any poison” and “potable”

Two readings: arbitrary bad health is removed and any green liquid counts as clean water; or the raw dose clears the declared toxin/venom/radiation family with exclusions, while collected rainwater is a different potable product. Consequence: a missing limb or addiction might be “cured,” or a thirst test accepts raw absorption-laden liquid as clean rainwater. I select the latter from `SlimeIngestion.cs`, `RM_SlimeLadder.IsPoisonLike`, FlowWorks liquid definitions and the frozen rain carve-out. Name matching is an attackable implementation rule, with ambiguous mod hediffs checked before claims. It never means every bad hediff.

### Raw cost, processing and resistance

Two readings: even a resistant native must acquire film for fairness, and cooked food carries the same dose; or resistance exempts susceptible-film application and processing yields ordinary safe food. Consequence: the former violates native admission or makes the material routine impossible. I select the source order: cure first, then film only for susceptible flesh. Normal meals lack the raw doer; contact still applies during gathering. The poison bargain is no free cure for susceptible workers, but resistance is a legitimate advantage. At the existing dose ceiling another dose need not increase film: it cannot reduce current film or instantly force dissolution. The ordinary remaining clock still governs. This prevents a maximum-dose boundary from being mistaken for waived absorption.

### Antidote “works”

Two readings: a direct `DoEffectOn` call removes a hediff; or a capable helper can target, reach and finish an ordinary UseItem action while the patient lives, consuming the item and paying toxicity. Consequence: a comatose/downed patient is advertised as savable but cannot receive the item job. I select completed normal treatment, paired with delayed/untreated arms. Source: existing targetable antidote and owner existing-UI answer. No pre-injection safety veto or guaranteed rescue is invented; injected gene rescue itself moves.

R4 exposes a second ambiguity: one real treatment receipt could calibrate every holder, or each engine availability class needs its own witness. I require T28 running-game rows for walking on map, bed, downed on bare map ground, held/released and caravan before any M1 escape output counts. Read actual action availability, targeting, reach/travel, completion, cleared film on the same living patient, consumption and toxic cost, with cancelled/delayed controls. If held treatment needs release, witness that release and subsequent ordinary helper job; caravan needs its actual supported action. An unavailable or uncalibrated class stays UNKNOWN and blocks full-range acceptance. M1 only extends timing/severity coverage between calibrated classes. The reviewer is right that the clinical kernel cannot establish engine job availability.

### Hazard OFF with established film

Two readings: OFF merely prevents new map exposure, allowing raw/liquid dosing or established advanced film to continue/hold; or it stops the feature's application and progression and clears existing film safely. Consequence: a player turns the feature off and remains permanently impaired despite the advertised wipe-off. I select the advertised safe opt-out. Evidence: `SlimeSettings` off text versus `RM_SlimeLadder.RatePerDay` advanced neutral-country hold and ungated ingestion doer. T23 fixes consumers, including loaded legacy fast-clock patients, without changing unrelated genes/coma or killing a terminal patient on the toggle boundary.

### “Farms fail,” “within a few harvests,” and “converted”

Two readings: change a terrain identifier once; or the native-ground field actually loses dependable cultivation. Consequence: replacing fertility 1.0 grass with current .85 rich slime can preserve permanent food farming. I select an observable post-reversion crop attempt: reverted substrate refuses sowing or stops the ordinary crop before harvest while the same crop reaches harvest on compatible imported substrate or hydroponics and unzoned native forage regrows. The observation must include that successful harvest, not an arbitrary timeout or a claim about indefinitely many harvests. A crop already growing at conversion may finish. Source: frozen no-permanent-farmland law versus `MapComponent_SlimeFieldConversion` and primary terrain values. This is my tightened operational reading after the reviewer showed that “dependable” concealed a productive-but-slightly-worse false pass. M2/T25 enumerate loaded ordinary crop compatibility and require a substrate-causal refusal/growth-stop receipt, preserving native forage and constructed workshops. Exact delays/yields stay tuning, not passing numbers.

### A “sown” farm versus a growing zone

Two readings: only a planted crop triggers decay; or merely designating a growing zone does. Consequence: an unsown planned plot changes under the player. I select the actual source growing-zone gate and require the description/setting to say so. De-zoning stops new zone-driven conversion but does not restore past terrain. Source: `Zone_Growing` test, with no plant-presence test, in `SlimeExposure.cs`. A future alternative is a rule change to attack before loosening the experience. The ground bar now witnesses heavy construction on a shelf versus refusal on soft ground and real compressor blocks. Its former roof/floor contact picture belongs under absorption and has moved there; it never certified the ground experience by itself.

### Shared growth is not an optional backdrop

Two readings: test the biome with slow base plants and wet growth/top effects OFF; or run shipped ExplosiveGrowth and its Slime top. Consequence: wet plants can scatter produce and convert terrain that every isolated bar missed. I select all shared mechanisms ON, as dependencies. `RM_ExplosiveGrowthRoster.xml` explicitly lists the native flora; `RM_TopResolver.Slime` drops produce, kills the plant and replaces eligible surrounding ground while protecting water/floors/edifices. Rain/growth/forage/crop/contact feedback is M2/M3, not a guessed sentence about abundance.

### “Rain,” “brief,” “flooding,” and “fast draining”

Two readings: green overlays plus `rainRate` establish collection, inundation and drainage; or real event-created liquid reaches exposed collectors/ground, is drinkable, and the ambient inundation recedes. Consequence: a weather-only mod passes while the water promise is absent. I select the latter, keeping the frozen land law. The bounded source trace finds FlowWorks `ApplyRain` but not a complete Slime-specific undug-ground/collector path; it is unknown, not called absent. T22/M3 trace actual ownership. No numerical intensity/frequency/depth is an approval condition.

The reviewer correctly found a further build-changing split: a visual wet tint, a deep-water terrain swap, water only in dug low cells, or standing potable water over exposed natural land. I choose the last as my specification of the frozen potable-flood picture. Every unroofed, unbuilt natural slime land cell, including crust and planted ground, receives a shallow FlowWorks-accounted surface layer; existing channels, imported substrate, floors, edifices and roofs are excluded. Normal in-place drinking and collection must work. The layer preserves underlying movement/build support and contact, adds only existing wet/slip behaviour, and neither kills crops nor changes fertility. Recession removes event water rather than restoring an obsolete terrain snapshot: prior terrain remains, with independent conversion/growth writes retained. Roof/floor additions stop new input and drain existing event water safely. T22 and M3 must prove the route before any model prediction is credited; no existing engine capability is asserted by this design choice.

### Natural rain availability versus forced weather

Two readings: a forced slime-rain event proves it belongs on this fixed desert world; or natural selection must allow it without changing the world's rainfall. Consequence: forced scenes pass while zero-rainfall tiles never see their water cycle. I select natural availability plus controlled replay as a diagnostic. Evidence: `ASHKARR_WORLD_DEFINITION.md` rainfall suppression mechanism, current WeatherDef, weather pool and campaign strip. Whether this custom def inherits a suppressing curve must be read in the actual loaded state; I do not claim source omission proves either outcome. No planetary rainfall repair.

### Potable floodwater and toxic-water distillation feedstock

Two readings: “toxic water for distillation” means rainwater must poison the drinker; or process-category reuse and the drinker's actual potable product are distinct. Consequence: collection can meet a filter name but violate safe drinking. I retain the frozen sheet's explicit potable rainwater outcome and the existing raw-channel last-resort rule; FlowWorks resolves classification/processing at its owned boundary. No new unsafe-drink exception is inferred from an old category label. M3 tests actual fluid composition and completed drinking.

### No rock, no trees and bootstrap materials

Two readings: all construction must start from naked local forage with no imported supplies, and thumbstalk provides wood; or no local quarry coexists with ordinary transported building inputs and later wood rulings. Consequence: benches requiring steel/wood become impossible and a builder restores cut wood yields to make a scene pass. I select accounted imports and no invented thumbstalk harvest. Evidence: `SlimeWorks.xml` costs and `SlimeFlora.xml` later wood-cut comment/empty harvest; legacy saved slimy trees remain, not a planetary “no trees” claim. Bones/Wreckage keep normal filters rather than a new compulsory resource route.

### Family names versus hidden animal mechanics

Two readings: retaining an animal name implicitly retains every comp; or species and each unusual player behaviour get independent deletion arguments. Consequence: paving and stock multiplication hide in “life.” I keep gappo feeding but defer channel engineering; keep oomb refuse feeding but defer promotion/fission despite their shared VEF comp; keep wuum ordinary capped reproduction because the genderless species needs biological renewal. This is an attackable Designer role choice, supported by the actual race/comp defs. No roster form is removed or merged.

### Conditional VEF behaviour

Two readings: guarded comps are already proven active, or absent VEF is an alternative shipped ecological design; versus the actual shipped behaviour needs its declared framework context and absence remains load safety. Consequence: the reviewer accepts an oomb that never scavenges by inspecting its XML. I select declared VEF-loaded behaviour evidence for feeding/cloning, with absent-framework guard checks only. All DLC remain present; VEF is a mod dependency question, not a DLC exception. No shared engine redesign.

### “Fubbum hunts gelatids”

Two readings: gelatid-exclusive prey and never harms any colonist; or vanilla prey selection permits suitable targets under size/combat/difficulty gates. Consequence: a small child or another eligible animal could make a false safety promise lethal. I select vanilla permitted prey without adding exclusions, from `FubbumHunting.cs` and the race. The tooltip's “never hunts colonists first” is unsupported by a dedicated species filter. No nocturnal pooling behaviour was found; it is not promised.

### “Dwommo flies”

Two readings: MaxFlightTime/animation files establish actual flight or immunity; or the flight tracker must enter flight and resistance is independent. Consequence: a grounded stat-only creature passes. I select deterministic real state, not unattended visual trials. Evidence: `DwommoFlight.cs` explicitly warns about cached stats and the standing flyer rule requires genuine flight. T23 includes existing-pawn cache/landing transitions. The owner-only live visual restriction remains and is not made a new question.

### Visitors, cap and “nearby”

Two readings: a visitor-only cap leaves unlimited natives, and “nearby” means arbitrary plausible animals; or the source counts all factionless wild animals and reads immediately adjacent world-tile biome rosters. Consequence: reproducing natives can prevent any arrivals, or builders invent a second home for a species. I select actual adjacent-tile input and current all-wild-animal budget until M2 exposes whether that rule defeats the outsider experience. Empty inputs stay empty. Initial local seeding is never rerun on reload. No species home is edited; a moving visitor is not a roster assignment.

### The giant as necessary life, shedding as extra

Two readings: giant mechanics are another biome signature and every combat embellishment stays; or natural feeding/engulf/growth define the already authored resident while combat production is separable. Consequence: keeping chunks, wound spawns and seals forces a weapon/adventure pipeline into basic ecology. I keep natural mouth/rescue/permanent growth, whose deletion would make this expressly swallowing/growing animal false, and defer wound shedding and all chunk systems. Existing gelatid roster stays; no default caller needs ShedOne or a chunk.

### Permanent growth versus disappearing prey

Two readings: a larger sprite or debug-set stage suffices; or actual feeding changes saved physical stage, occupied cells and applicable prey/capacity, without default loss from wounds/dryness/starvation. Consequence: the giant can show growth while colliding or swallowing against a stale footprint. I select physical permanent growth from the owner ruling and kernel/size integration. M4 sweeps stage changes while held prey, corpse conversion and release compete for cells. The reversible option remains OFF by default; exact thresholds are checks.

### “Visible rescue time” and no vanishing

Two readings: a countdown string permits deleting held prey on down/death/OFF; or the same held identity returns on supported release and a real terminal result accounts for gear. Consequence: rescuers win the fight but lose the colonist anyway. I select the latter; source ThingOwner/release-before-corpse-site design and the readable-loss ruling require it. Timing/geometry are model questions. No guarantee that a fully blocked map can conjure a free cell; unsupported placement must be rejected before a pawn is swallowed, or the holder must retain them safely with a readable reason.

### Feature OFF versus destructive cleanup

Two readings: hide UI while built extras continue in jobs/recipes/incident callbacks; or block both acquisition and active consumers, retaining old objects and paid state safely. Consequence: a default map still gets resurrection, chunks or promotions, or disabling deletes people/items. I select full consumer isolation and paused valid legacy state. Source: exposed tick/effect/bill/recipe/target paths in census/tickets. The already recorded paid-vat safe-pause answer is preserved, not reopened. Default-reset snapshots must reflect proposed OFF values in static initializers, Scribe fallbacks, settings UI and actual consumers.

### Native water and ordinary hazards

Two readings: a resistant native is immune to all harm and automatically satisfied thirst; or it resists film while its own environmental-water drinking must genuinely satisfy thirst, retaining predator/acid/heat rules. Consequence: immunity to film masks dehydration or claims immunity to Direct Sun. I select the latter under biome_rulings native-water rule, FlowWorks drinking service and shared geometric sun. Native death bursts do not imply free throwable weapons or permit sentient arsenal generation.

### Legacy ground and current rosters

Two readings: support only newly named primary ground, or treat every foreign slime-labelled surface as supported; versus explicitly map packaged owned legacy surfaces/vegetation without changing unrelated mods. Consequence: old authored maps become safe/inert by accident or support grows without limit. I select the owned legacy inventory and actual tags/semantics in T24. Frozen donor-era cast and bestiary names do not establish current effective rows. The bestiary is an aspirational naming register; no new animal is inferred from it. Effective multi-homes are preserved and noted, never evicted.

### Whole season, “viable,” “flood,” “desert,” and “stall”

Two readings: a successful short showcase with mechanics disabled proves viability; or prepared ordinary work and ecological/water cycles coexist on the complete map for the declared season with reload and changed action order. Consequence: quiet clear-sky scenes hide runaway terrain, animals or food. I select the latter. “Flood” includes persistent expanding water/slime/animal occupation that prevents the defined routine, “desert” is lost renewable forage/native encounters, “stall” is normal jobs/cycles unable to advance, and “error storm” is repeating faults that interrupt those actions. No fixed sustainable colony size or tick budget is invented; M2/M5 expose pressures and the whole bar reads the actual managed routine. Ordinary failure of a deliberately unprepared colony is not a refusal.

### Check versus bar versus art verdict

Two readings: every failed def/stat/variant/check row refuses the mod; or only missing owner-visible experiences do, with instrument reliability and declared values kept as regression checks. Consequence: retuning forces perpetual re-passage and a numbered animation resolver bug masquerades as failed flight. I select the current standing bar rule. The current kit checker is repaired, not treated as proof that frames are absent. Existing owner giant art review remains owed under the floor; no new asset-count bar or invented approval appears here.

### Other-version promises and already answered choices

Two readings: deferral cancels original gene/last-touch/chunk/family requirements; or it removes default execution while preserving the exact request for its next version. Consequence: a later builder returns a death-time clone, rewinds a remarriage or makes an ally-safe reusable bomb. I select retained constraints and OFF default. `record.json`, the source November `ANSWERS_OWNER.md` and cited events already answer UI, return-to-family and weapon consequence; no question or waiver is raised again. Joining Water remains already deferred under OWNER:1792755170245820662. A readable compatibility pause is not owner acceptance of an untested feature.
