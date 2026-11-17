# Next version, switched off

Designer decisions for Design Version 0.1.0. These defer scope; they do not revoke owner rulings. Species stay rostered. Code/defs stay in the tree pending separate owner retirement decisions. Worldgen is permanently out, not deferred.

### legacy weather ports — RECOMMEND RETIRING

What: Owned compatibility weather defs copied from donor: RM_ForsakenNight, RM_ForsakenRainyNight and RM_ForsakenThunderstorm. The active RM_Abyss weather table uses the newer three weathers.

Why: Designer delegated: Unused donor compatibility weather set duplicates owned active weather and serves no present player experience. Keep inert pending owner retirement. Ticket: T1.

### placement worker — RECOMMEND RETIRING

What: Existing biome score worker and rarity slider. It can score new planets in code; player-facing worldgen is permanently outside the campaign, not a future feature.

Why: Designer delegated: Worldgen is permanently forbidden by standing ruling, not next-version work. Recommend deleting placement/rareness UI; until approved suppress all placement. Ticket: T2.

### storm call

What: Witchfire weather has wind/lightning and poor accuracy; delayed rumble/flash may bring a manhunting Summ, with threat letter. Natural storm schedule separate from stolen-egg call.

Why: Designer delegated: An extra scheduled manhunter encounter; removing it leaves Witchfire land weather and the light economy complete. Ticket: T3.

### heat observation

What: A colonist in clear air near a visible active heat source under otherwise dark ambient air completes the observation project and unlocks heat-folding. Option off grants observation on load.

Why: Designer delegated: A bespoke discovery/research unlock; ordinary heaters already demonstrate warmth and remain usable. Ticket: T4.

### fold lamp

What: Fuelled, rotatable heater-lamp with a forward lane of Dark clearance; walls stop each column, clearance fades with distance. Plain heat/light remains without Dark.

Why: Designer delegated: A custom directional tool is unnecessary when ordinary heat clears rooms and living plants light farms. Ticket: T5.

### gill ash — RECOMMEND RETIRING

What: Gharrek shearable gill-ash product, brittle chitin hide; gill-ash refines to chemfuel at BiofuelRefinery. Shearing is ordinary time-based vanilla, not gust-gated.

Why: Designer delegated: Secondary chemfuel husbandry duplicates tholin recovery and vanilla refinery feedstocks; no essential food-chain or light function. Ticket: T6.

### sorter rings

What: Wild sorter (RM_Durrgak) places capped shard rings away from home; a colonist seeing a cairn gains a memory.

Why: Designer delegated: Authored ring placement and memory are a parallel sign/lore system; ordinary sorter diet/hauling remain. Ticket: T7.

### sorter sites

What: Map step scatters stocked den, loose row of rings and optional salvage cache using forbidden steel/components; proof hook calls actual placement but not new-map wiring.

Why: Designer delegated: Stocked den/cache set pieces are authored one-off interactions, unnecessary for ordinary life or Dark. Ticket: T8.

### summ hide

What: Summ creature is tough, regenerates healable injuries and develops a readable sunburn under bright open sky; shade/Dark cool it. Regeneration and UV sensitivity have switches.

Why: Designer delegated: Regeneration and UV injury are a separate megafauna husbandry mechanic; ordinary large native animal and Dark vision remain. Ticket: T9.

### continuous growth

What: Constant problematic lifelong summ growth with escalating size/hunger/space is ruled in item prose, but no continuous growth implementation was located; finite stage plateaus do not fulfil it.

Why: Designer delegated: Lifelong size/hunger/space escalation belongs to the deferred bane-and-boon beast, not ordinary native life stages. Preserve owner's no-plateau requirement there. Ticket: T10.

### ship cover state

What: Saved temporary ship-cover meter: home Abyss map with GravEngine and few lit building lamps builds cover, noise erodes it, expiry/probe report causes cooldown. Engine absence resets it; no direct engine-start hook here. Older design rules call ship touch campaign-only even though implementation lives in RM; this dry run does not extend free-tier scope.

Why: Designer delegated: Active gravship concealment is an independent stealth/cooldown system; existing sensor shadow and local obscuration supply first-version protection. Ticket: T11.

### probe search

What: Scheduled probe visits under cover: faction/kind extension, vanilla militor fallback, moving-colonist/lamplight accumulation, report/collapse, departure and kill message. Detection is distance-based without LOS or a heat read.

Why: Designer delegated: Scheduled scout/report encounters belong with active cover, not to the ordinary Dark cycle. Ticket: T12.

### cover external effects

What: End-to-end orbital trade suppression and raid/pursuit response to dynamic cover are not verified. No CoverLevel/IsCovered consumer beyond Abyss was found in the source search; the component exposes a state API.

Why: Designer delegated: Orbital trade isolation and dynamic pursuit response are deferred with active cover; do not mistake an exposed API for working consumers. Ticket: T13.

### cryptid sites

What: 0–2 extra runs of sorter placement; identical material signs, no certain Nhaleth structure/pawn/faction. Toggle does not remove already placed ordinary sites.

Why: Designer delegated: Additional deniable sites are lore set pieces, not ordinary habitat. Ticket: T14.

### cryptid exchange

What: Occasional unwatched unforbidden item exchange inside a shard circle, returned goods and letter; awake colonists' LOS prevents it. Reward capped to one stack of each return material; forced proof hook bypasses random timing.

Why: Designer delegated: Unwatched item exchange is a separate offering/reward interaction. Ticket: T15.

### cryptid phantom

What: Rare temporary clear pocket on apparently empty ground away from buildings/colonists; no creature appears. Active pocket list is not saved; expiry pruning is hourly.

Why: Designer delegated: No-source clearing events are a parallel lore cause; warmth/weather already supply the Dark's physical transitions. Ticket: T16.

### cryptid lore

What: Single RulePack cryptid name/whisper, rare social interaction, tale usable in art; Utinni adds Sith whisper only. No certainty/reveal is owed.

Why: Designer delegated: Whispers/tales are extra lore events; keep the never-appear ban in all versions. Ticket: T17.

### cryptid dream

What: Sleeping colonists can receive long-stay dream memory after map AgeInDays threshold; actual individual tenure is not tracked.

Why: Designer delegated: A long-stay dream is a separate timed lore event; erosion already supplies the cost of staying. Ticket: T18.

### brood site

What: Marker-gated local-map brood site places sleeping mother, clutch, great bones, stuff heaps and optional wreck. Global MapCommonBase step checks tile mutator/landmark extension. Local map generation is distinct from alternative planet generation.

Why: Designer delegated: Lightfall brood is a special expedition, not ordinary terrain or the light economy. Landmark geology remains external. Ticket: T19.

### brood pressure

What: One saved hidden pressure/peak/threshold joins light, salvage and theft; stir/rumble warnings, partial refund/decay and re-arming. Concurrent additions can wake after warning without a guaranteed elapsed grace period.

Why: Designer delegated: Saved greed/wake pressure is the deferred expedition's risk system. Ticket: T20.

### brood wake

What: Sleeping 7x7 impassable mother drawn 15 across becomes a permanently manhunting Summ pawn with 3% incoming damage and no pain; warning/letter/shake say flee. Full physical scale/navigation remains unproved.

Why: Designer delegated: Landscape mother transformation/manhunt is that expedition's consequence. Ticket: T21.

### bone resources

What: Field supplies light woody SummBone stuff and minifiable great bone restricted by place worker to ship substructure; the latter gates imprint.

Why: Designer delegated: Special great-bone retrieval and SummBone stuff serve imprinting/expedition, not ordinary butcher bone. Ticket: T22.

### egg theft return

What: Egg stores lair identity/theft, adds wake pressure when taken, partially refunds if placed near mother on original map. Current return is near coils, while item also mentions return at lip.

Why: Designer delegated: Egg theft/return is a bespoke expedition interaction. Ticket: T23.

### egg storm

What: Stolen egg on another home map periodically starts Witchfire and later spawns a searching manhunter Summ; timers saved per egg. Moving/removing egg affects whether pending calls run.

Why: Designer delegated: A carried egg's home-map weather/manhunter clock is a secondary encounter system. Ticket: T24.

### egg hatch imprint

What: Timed hatch produces summing; player-held/claimed egg bonds only if a player great bone stands on substructure on that map, otherwise wild with inspect reason. Same-map foundation is used as ship membership proxy.

Why: Designer delegated: Bone-gated bonding is the expedition reward system. Ticket: T25.

### summ bane

What: Player Summ gets hunger hediff and semi-random autonomous killing of reachable wild/tame animals, with warning for tame victims. Drafting/mental/current attack states suppress new hunt; applies to any player-owned Summ, not recorded imprint only.

Why: Designer delegated: Autonomous extra killing and hunger escalation belong to the bonded-beast package, not ordinary rostered Summs. Ticket: T26.

### wreck salvage

What: Finite rescue-wreck inventory with seven bill products; each completion spends stock and adds greed, last-stock bills deleted; saleable/smeltable foreign fittings remain loot. No second usable gravship.

Why: Designer delegated: Finite rescue-wreck bill economy is an authored expedition reward, separate from ordinary Wreckage. Ticket: T27.

### ship restore

What: Four accepted fitting classes repair damaged colony buildings on substructure with budget; three refused types explain refusal and are not consumed. No redesign; no engine/connectivity check of what constitutes the player's ship.

Why: Designer delegated: Fittings that repair a particular ship are that expedition's payoff, not ordinary salvage resources. Ticket: T28.

### lirrith decay disease

What: Lirrith custom corpse decay/disease bite

Why: Designer delegated: Ordinary feeding/attacks suffice; corpse processing and infection are additional systems. Ticket: T32.

### moravatha low rest

What: Moravatha bespoke low-rest behavior

Why: Designer delegated: Pack grazing does not need a special rest engine. Ticket: T33.

### ysvaltha blades

What: Ysvaltha bespoke blade/tail attack animation or ability

Why: Designer delegated: Existing melee tools already implement its predator role; shoulder blades are not a flight promise. Ticket: T34.

### sesserith spine spray

What: Sesserith ranged spine spray

Why: Designer delegated: Ranged spray is a second attack system beyond ordinary melee predation. Ticket: T35.

### ossumatha dig rage

What: Ossumatha custom hungry digging and propagated group rage

Why: Designer delegated: Ordinary herd grazing/retaliation remains whole without custom terrain damage or propagation. Ticket: T36.

### globe poison

What: Glow-globe special poison when eaten

Why: Designer delegated: Light economy needs a living lamp, not an additional ingestion hazard. Ticket: T37.

### fungus spores

What: Sickly mushroom bespoke spore-air exposure

Why: Designer delegated: Inherited pollution-ground plant behavior is sufficient ordinary life; a new exposure system is extra. Ticket: T38.

### vine turning

What: Paddle-vine tracking/turning toward light

Why: Designer delegated: A moving plant gimmick is unnecessary to fiber harvest or lighting. Ticket: T39.

### seep works

What: Chemistry seep tapping and explosions

Why: Designer delegated: Separate fuel/explosion industry duplicates the kept collapsed-grain fuel cycle. Ticket: T40.

### glowberry item

What: Harvested berry item emitting mobile light

Why: Designer delegated: The plant already gives RawBerries; inventory light is a new portable-light capability. Ticket: T41.

### rites

What: Campaign darkness rites

Why: Designer delegated: Rituals do not operate the land, life or Dark cycle. Ticket: T42.


### outdoor drifting pockets

What: The built Perlin effective-temperature offset opens and closes outdoor clear patches without changing the ordinary outdoor thermometer; retain its code behind a labelled next-version switch, off.

Why: Designer delegated: Ordinary warm rooms and map-wide temperature/weather clearance suffice for land and the Dark/light/feeder/grain signature; an outdoor microclimate system is additional scope. A later supported cause must be specified consistently with ordinary temperature, not guessed on this pass. Ticket: T43.

### nevarithia carried Dark

What: The owned grazer's promised local carried knot, including where ambient Dark cannot form; unbuilt, deferred off. Its ordinary roster presence and appearance stay.

Why: Designer delegated: Removing the knot leaves ordinary life and the complete ambient Dark/light/feeder/grain chain intact; a ruled description constrains future behavior rather than establishing first-version necessity. Ticket: T44.

### nevarithia death release

What: The promised release/dispersal of the carried knot on death; unbuilt, deferred off with its halo parent.

Why: Designer delegated: Without a carried knot there is nothing to release; ordinary death/corpse evidence already makes life readable. This is a second part of the deferred creature system, not ambient land or signature. Ticket: T45.
