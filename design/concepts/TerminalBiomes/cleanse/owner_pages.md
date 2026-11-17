# Page one — what the mod now is

Visit alien sea floors by gravship: the Scald boils, the Grey grows salt, the Chill holds dark fuel, and the Twilight shelters gardens beneath living glass. Their native plants, prey and predators belong to those liquids, and the fish caught at the beach have living counterparts below. In the Twilight, harvestable banks tempt you beside a current that can carry a careless worker into a sink, so routes, warnings and rescue shape the visit.

**Land:** distinct floors, materials, visibility and ordinary weather; beach steam above, submerged Scald bubbles below.

**Life:** existing native rosters, forage, prey, predators, moving light and environmental survival; no evictions.

**Signature:** productive Twilight banks tempt workers beside carrying water whose warned surges can take them to a findable, rescuable sink.

My delegated choice: keep the ruled sea bundle with that current chain as its signature. The cultivated-light economy loses as runner-up because it adds another progression system. Natural temporary wells and their actual animal gardener stay under the frozen roof laws. Campaign inhabitants move: removing the reveal defeats neither land, native life nor the signature.

Next version, switched off:

- Steam-catch production, steam-exposure clock and suit research.
- Steam devils, vent flashes, staged sail/walker appearances.
- Wreck-colonising sponge interaction.
- Falling panes, deck accumulation and launch obstruction.
- Suulk feeding, vaulisk ambush and lure-organ reward.
- Cargo floats and harsher sink outcomes.
- Portable light cages, clipped lamps and cultured sunlight.
- Grey hull crust, lamp-response encounters and elder treasures.
- Reactive crowns, contact venom and sentinel squirts.
- Chill growers, extraction and fuel/drug processing.
- Hesuun extrusion, fuselight explosion and tarnn wake.
- Twilight plant charge, wilt and event spreading.
- Lab-ending receiver, claims, charts and theatrical lid-dark events.
- Chill warmth defence and harvestable aurora surges.
- Inhabited campaign holdings and automatic Compact weir dressing.

Species remain rostered when attached extras stop. Existing code/defs stay behind labelled settings; tickets test default absence, opt-in presence and safe switch-off.

**Recommend retiring:** inert cross-biome controls; they change nothing and the cross-biome guarantee was already released. I recommend; you decide.

**Counts:** capabilities 71 before, 36 kept; next version 34; recommend retirement 1. Bars 0 before, 8 proposed; live-only bars 0 before, 2 proposed. Before bars are [measured] from the CASE’s empty old-bar set; capability counts come from this proposal’s source census. Checks 10; rules 10; unknown shared meetings 8; models 5; tickets 43; questions 0. These are proposal counts, not gameplay measurements.

# Page two — what to check

My consequential defaults:

- “Sea surface”: floor or neighbouring beach only; ship-only travel, no hatch.
- Scald “perched/outflow”: stale prose; retain the terminal basin, change no world.
- “Boiling contact”: beach boiling water and localized authored floor pools burn. Other floor substrate is ordinary hot ground; retreat there stops contact burns. The cool margin is beach-only and undrinkable.
- “Clean steam”: purity/private-heat constraints are rules and checks; visitor burns and drinking denial are the experience.
- “Sparse Grey”: solitary fauna, not empty mineral ground; Twilight shoals remain below the lid.
- “Current”: a cold reader must distinguish the dry-looking bed and stakes from bank silt in ordinary views. Warning delivery alone cannot pass. Ordinary visitors cannot harmlessly cross between registration ticks.
- “Safe arrival/rescue”: protect hull access from surge; rescue means outside dangerous water in safe shelter/carriage, never merely roofing the sink.
- “Gardener”: a living giant swims at the ceiling, clears skylight rims and patches spent openings, changing rim/light state. My version limit protects it from injury, death and removal; no flag, replacement after death or roof-collapse system qualifies.
- “Temporary light”: an ordinary visit shows finite remaining life. Later waning/replacement requires a fresh floor aged by real simulation ticks, recorded through the game’s own saves. Edited ages or skipped clocks disqualify it; this workload is separate from the season.
- “Inhabited ark”: the sheet historically promises an initial reveal. Under this later cleansing card I defer it, preserving the promise and peaceful-holdings doctrine; RM bars no longer require campaign content.
- “Off”: stop availability, dispatch, ongoing effects and reload reassertion while preserving saved bodies and contents.

No owner question is needed. These are my stated decisions, not new words attributed to you.

Models, first to build first:

- **Situation and transition generator:** actions, gardener protection/tending, transfers, rescue, settings and reload.
- **Channel and landing geometry:** boundaries, crossing phases, banks, sinks and ship reservations.
- **Whole sea season model:** all kept systems together; separately budget the natural-tick light-cycle record.
- **Liquid and native physiology replay:** pool-versus-ground contact, drinking, shared heat and survival.
- **Light habitat and food-chain model:** real creature tending, replacement wells and viable gardens without the light economy.

Unknowns remain integration and measurement: missing channel-terrain bindings, obsolete hatch reservation, absent local gardener implementation, unavailable floor/liquid dependency adapters and a campaign-tier harvest product. Tickets specify the contracts; no model or gameplay PASS is claimed.

The first reviewer’s refusals have been addressed here; the second look is pending. This proposal changes nothing until you read it and the fresh review is resolved.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- a kept mechanic with no definition (bars.json B4 (range, accept 2, reject 3); rules R6; definition.md 'Costs and ordinary materials'; tickets.md T45). B4 lists RM_ScaldWaterOceanDeep and RM_ScaldWaterOceanShallow among the paid boiling-contact terrains. It also says the rest of the floor is 'ordinary hot mineral substrate', where standing costs nothing, and that boiling pools are 'localized vent-fed pools explicitly authored'. The built floor is almost entirely those two terrains: src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml terrainsByFertility maps every non-rock cell to OceanDeep (fertility below 0.6) or OceanShallow (0.6 and above), and the comment there records a measured 49,940 deep cells on a 250x250 map. Patches/RM_ScaldWater_LiquidHeat.xml applies liquid heat to exactly those terrains. No terrain def exists for the 'ordinary hot substrate', and no genstep or rule places 'localized pools'. T45 only says to export that mask and keep a route clear. Built as it is now, the floor meets B4's own reject picture 3 ('the entire submerged floor burns a worker continuously'). The census row C02 calls this 'present'. Would pass: The floor's nonboiling hot substrate and the placement of its localized boiling pools are defined: which terrain def, how pools are placed relative to vents, and that the hull-to-bank route is clear. A build ticket with an acceptance test implements them, and B4's floor list of paid terrains names only the pool terrain. Smallest fix: Add a ticket (with its acceptance test, watched to fail on the current floor) to replace the floor's terrainsByFertility bands with a nonboiling floor substrate plus vent-adjacent pool cells. Split B4's terrain list into beach-paid and floor-paid parts. Set C02 to absent for the floor substrate and the pools.
- two bars, or a bar and a rule, that cannot hold together (bars.json B8 (reject 1, range) against R7 and B7; brief's whole-bar definition). R7: 'Lifetime remains finite on the frozen sheet's years scale; current short-lived values are tunable implementation debt' (the kernel is 5 to 9 days: Kernel/RM_WellKernel.cs Lifespan). B8's range is '15 game days' and says 'the season itself need not show years-scale expiry'. Yet B8 reject 1 refuses a build where 'light replacement leaves only dangerous ground'. A season under R7 will almost never contain a replacement, so that clause cannot be read. The brief requires the whole bar to run 'through a stretch long enough to see its cycle'. With the well cycle measured in years, the kept lifecycle never runs together with current, forage and predation in the whole bar. Would pass: Either the well cycle fits inside the whole bar's stretch, or the whole bar does not claim to see replacement and the lifecycle is not a kept bar experience. Smallest fix: Keep the built week-scale clock as the rule for 0.1.0 and mark 'years scale' in the sheet's ban as the drift's upper bound (no permanence). Put this on page two as a question with its evidence: years makes turnover impossible to observe in any season. Or drop the replacement clause from B8 reject 1.
- evidence that cannot tell success from a plausible false pass (bars.json B7 (says 'later visits showing waning and replacement'; sees.start); models.md M3 tick-aged branch; T46 acceptance). The instrument says 'Keep that floor loaded… A later visitor uses this same floor.' The bar's experience is a crew that leaves and returns. Whether a sea-floor map persists, and ages, while no crew is on it belongs to DivingInteraction, which the proposal itself says is absent from this checkout (definition.md 'Read basis'; census D07 'unknown'). No meeting or model covers persistence across departure. A build that discards or freezes the floor when the ship leaves, and regenerates fresh wells on return, would pass this continuously loaded branch while the player never sees waning on a later visit. The provenance contract also forbids any catch-up aging, which such a build would need. Would pass: The evidence follows the player's real path: depart, time passes, return to the same floor. It reads that floor's identity and the wells' age progression under whatever persistence rule the layer dependency really has. Or the later-visit clause is dropped from the bar. Smallest fix: Drop 'with later visits showing waning and replacement' from B7's says. Keep 'temporary columns whose finite remaining life can be inspected' (this satisfies the sheet's no-permanence ban). Move turnover to a check driven by M1's staged boundaries. Add floor persistence across departure as an unknown in the floor_access meeting.
- a kept mechanic with no definition (definition.md 'When it goes wrong' (gardener paragraph); bars.json B7 accept 1; R7; T43; T46). 'A completed graze clears the rim's visible occlusion and restores that opening's existing light footprint… without a new roof-health, roof-growth hazard'. Nothing in the proposal says what occludes a rim, when occlusion accrues, or how much light it removes. Without a cause of occlusion, a graze has nothing to clear. 'Restores' also implies an occluded well gives less light, which is an unspecified light rule touching M5 and the twilight_light meeting. T43 only says to implement 'grazing rim occlusion clear'. Would pass: A rule names the occlusion state: its cause, the reduced footprint as a check number, and what the gardener does to it. Or the bar has the gardener tend visibly without any occlusion state. Smallest fix: Add a rule R12 that defines rim occlusion (ceiling-garden growth on open rims at a check-only rate, reducing that well's light) and cite it from T43 and M5. Or delete 'occluded…clear' and 'restores light footprint' from B7 accept 1 and the definition, and keep patching of spent openings as the visible state change.
- a figurative word unmarked (bars.json B2 accept 1). 'pale mineral forms disappear into Grey murk' is an accept picture for a bar whose says requires the visitor to distinguish 'the Grey's murk and mineral forms'. B2's own accept 2 asks for 'distinct pools and silhouettes rather than a white screen'. 'Disappear' is unmarked and reads literally as a failure. This reviewer's blind sort put picture 6 as reject. Would pass: The Grey clause of the picture shows mineral forms that are still readable through the murk. Smallest fix: Reword to 'pale mineral forms loom dimly through Grey murk yet stay readable as shapes', or add 'disappear' to B2's figurative list with what it stands for.
- evidence that cannot tell success from a plausible false pass (bars.json B3 accept 3). 'Chill industrial catches are identifiable as fuel chemistry and cannot be fed to ordinary colonists as food.' B3's says is about meeting living catch counterparts, prey and predators, and native survival. This picture shows none of those, so a build with only an inedible fuel item would satisfy it. K5 already checks 'industrial nonfood flags'. A cold reader (this blind sort, picture 2) rejects it as not meeting the bar. Would pass: Every accept picture shows the bar's experience: living counterparts, encounters, native survival. Smallest fix: Delete B3 accept 3; leave non-edibility to K5.
- a figurative word unmarked (bars.json B1 says and range ('can work from the hull to the bank', 'All 4 named seas')). B1 covers all four seas, but 'bank' is defined only for the Twilight channel (B5, the C22 signature). For the Scald, Grey and Chill floors nothing says what 'the bank' is. B4's range reuses 'hull-to-bank route' for the Scald without defining it. B1's figurative list marks only 'carrying water'. Would pass: 'Bank' is defined for each sea, or B1 says 'working ground' outside the Twilight. Smallest fix: Add 'bank' to B1's figurative list: for the Twilight, the channel bank; for the other seas, the reachable working ground beyond the hull. Give one accept picture for a non-Twilight sea.
- a cold reader sorted a bar's pictures differently from the proposal (the Stranger test: repair) (bars.json B2). a cold reader sorted 'At normal colony zoom a worker beside cyan water and rainbow mats reads as Scald; gold-lit gardens under glass read as Twilight; pale mineral forms disappear into Grey murk; dark fuel pools interrupt Chill ice.' as reject; the proposal labels it accept Would pass: pictures a cold reader sorts as the proposal does Smallest fix: rewrite those pictures, or the bar's says, so the line between accept and reject is plain from the words alone
- a cold reader sorted a bar's pictures differently from the proposal (the Stranger test: repair) (bars.json B3). a cold reader sorted 'Chill industrial catches are identifiable as fuel chemistry and cannot be fed to ordinary colonists as food.' as reject; the proposal labels it accept Would pass: pictures a cold reader sorts as the proposal does Smallest fix: rewrite those pictures, or the bar's says, so the line between accept and reject is plain from the words alone
