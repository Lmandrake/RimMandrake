You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, the Pyrelands. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

# The hard requirements on your answer

1. EXACTLY FIVE ideas. Not four, not six.
2. Each idea must be clearly DIFFERENT from the other four: a different player verb, a different system it touches, and a different emotional beat. Before writing them, list the five verbs and five systems in one line each and check none repeat.
3. Each idea must be different from EVERY OTHER BIOME's signature listed below. If an idea shares a mechanism with one, name the biome and say in one sentence why this is not the same package.
4. DO DEEP RESEARCH first. Look at games like RimWorld (Dwarf Fortress, Oxygen Not Included, Kenshi, Frostpunk 1 and 2, Don't Starve / Don't Starve Together, Songs of Syx, Subnautica Below Zero, The Long Dark, Caves of Qud, Cataclysm: Dark Days Ahead, Stonehearth, Going Medieval, Timberborn, Factorio, Against the Storm, Banished, Valheim, Project Zomboid, Tharsis/Surviving Mars, The Thing) and at RimWorld mod content (Vanilla Expanded series incl. VFE Ancients/Insectoids/Mechanoids/Deserters, Alpha Animals, Alpha Biomes, Biomes! Caverns/Islands, ReGrowth, Dubs Bad Hygiene, Vanilla Temperature Expanded, SOS2, Odyssey's gravship, Anomaly's pit gate / fleshmass / void, Biotech, Ideology rituals). For EVERY idea, cite specifically what it draws from (game + feature, or mod + feature) and what it does that the source does not.
5. Every idea must be buildable in RimWorld 1.6 (XML defs, C# ThingComps, MapComponents, GameConditions, IncidentDefs, WeatherDefs, SoundDefs, Harmony patches, ritual defs, research projects). Name the def types and the main C# hook.

# Binding project rules (violating one disqualifies the idea)

- RimWorld 1.6 with ALL five DLCs present (Royalty, Ideology, Biotech, Anomaly, Odyssey); depend on them freely.
- One fixed, hand-made, tidally locked planet: a dayside, a terminator, a nightside. NO worldgen features of any kind, no procedural planets, no variants. Content lives on maps, incidents, pawns, buildings.
- ONE kind of heat planet-wide: vanilla temperature, heatstroke, hypothermia. Never invent a new "kind" of heat or cold or a new heat hediff.
- No animal or pawn ever vanishes without a readable sign (a mark, a letter, a trail, a tell).
- If it flies in the fiction, it flies in the game (real 1.6 flight).
- The free tier (RM_, franchise-free) uses only INVENTED exotic names; genuine Star Wars IP (canon creatures, Jedi/Sith, named canon planets) belongs only in the separate campaign layer (RUT_). The free tier must stand alone, not be a thin fallback.
- One animal, one biome, unless there is an in-game reason (migration, a life stage that moves).
- Every mod ships real Mod Settings: feature toggles, tuning sliders.
- The religion of the campaign (the Jawa "Salvation", nine small jealous gods) is in the campaign layer; a biome can TEACH a rite (found inscription → research row → ritual performable anywhere).
- NO GOD IS EVIL. Sh'kaar (the searing sun) and Zizzik (malfunction, the wrong spark) are "the hungry gods", dangerous, never villains.
- A god's favour shows ONLY through events, world state and subtle odds (and the ship's Narrator speaking of the gods vividly). NEVER a hediff, a stat blessing, a buff or a curse status.
- A rite may not grant a power. "Rituals create cohesion, not material rewards."
- Powerful tech is good; balance it by cost or gating, never by narrowing what it does.
- Avoid anything that needs new multi-frame animation work; the owner warns against "endless animation development". Static art, sound, terrain, map conditions, AI behaviour and UI are cheap; new animated rigs are not.
- The Pyrelands' heat is ordinary vanilla heat (its sun kind is "overhead", angle from the tile's latitude). Fire is vanilla fire.

# The biome: the Pyrelands ("the burning savanna")

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- A hot dayside grassland (temperature median ~54 C, sun high overhead, rain essentially zero). Thematic handle: THE STANDING BURN. Image: "a grassland that has been on fire since ages before the war, and a people walking the flame-line collecting a debt."
- The ruled loop: freakish growth -> standing dry grass constantly renewed; no rain -> never wet; dry lightning -> it lights; fire -> dry thunderstorms -> more lightning. "The fire lights the storm, and the storm lights the fire." The burn never ends; only its address changes.
- The water answer: the quickgrass is a Rakatan-engineered forage crop gone feral (roots to the water table, regrowth in days). Theme: genetic engineering is not bad, "it's what you do with it"; an engineered landscape of generosity ages after its gardeners died. (Rakatans are campaign-only IP; the free tier says only "engineered forage".)
- The only rain is BlackRain: a filthy downpour dragged out of a big fire's own smoke column; the fire makes the storm that kills it. After it, "the loudest silence on the dayside".
- Ash becomes tar downstream (that is another biome's harvest). The nightside mirror is the Propane Lakes (fuel everywhere, no ignition).
- The fire food-web: four igniters keep the burn alive (lightning; fire-hawks that carry burning twigs to spread it; furnace-beasts, migratory megafauna whose mineral hide banks heat, warm to stand near, whose bed-down grounds smoulder alight; and deliberate hands). Three families: fire-followers (hunt the flame edge), burrowers (let the fire pass over, emerge into ash), ash-grazers (the great herds eating the regrowth sprint).
- The Deep Desert Tribes are the fire-farmers: controlled burns on THEIR schedule, scorch-fruit harvested on the burn line, sacred fire carried away; an unplanned burn is an act of war answered by short furious "fire raids". Their faith, the Sun-Debt: the sun poured its theft into the grass and burning repays the land; "the flame harvest is collection". This is ANOTHER faith; the player's Jawa colony cannot learn its rites.
- Hard bans: no ordinary rain; no fire-immune flora (only the scorch-fruit pod's casing); no scorch-fruit that keeps (it spoils within a day); no permanent settlement in the burn's path but the Tribes' moving camps; no Earth flora or fauna. Fire-hawks and furnace-beasts are TAMEABLE ("Fires all the time! I love it.").

Already BUILT (do not re-pitch; you may build ON these):
- The standing burn: a map component guaranteeing a burn somewhere always, plus a fire-front clock (a line of grass goes up and walks every 2-4 days); burn-line intelligence (where is the burn).
- Ember grass (dries to tinder, regrows in under a day) and quickgrass; scorch-fruit that grows only where fire just was and spoils in a day; four-rung ash ladder terrain (trace/light/heavy/deep) that banks with each burn; scorchable ground; FIREBREAK terrain; scorched ruins at mapgen; fulgurite (lightning-glass) wherever lightning strikes; the firefoam sprayer building.
- Weather: clear, dry thunderstorm, ash fall, cinderfall, BlackRain (whose odds jump while a big fire burns).
- Creatures: fire-hawk (flier, carries embers), furnace-beast (bs 3.2, thermal circuit, warmth near it, bed-down ignition, a world-map migrating herd), flamefang (venomous serpent that beds ahead of the front), sytheclaw (gold-plated pack hunter invisible in the tall grass), barbslinger (calf-sized scorpion turning the cooling ash, tail volley), fire wasp (flier swarm living inside the heat), ashwallow (grazer that burrows when a front comes), emberscythe mantis (fast predator at the burn's edge); canon herds in the campaign layer.
- Campaign: the Tribes' flame harvest event, fire raids, the Tribes' own fire rite.

Already PROPOSED in this sitting (do NOT re-propose): moving the invented creatures to the free tier; a new free-tier herd grazer that follows the burn scar to eat the regrowth; growing the furnace-beast into a true giant; a soundscape (grass hiss, crackle before the light, hawk screams, the silence after BlackRain); a heat-kind declaration; a rite where the colony stands down and lets the wild burn take a field it planted (Sh'kaar); a rite grounding a lightning strike into a fulgurite ring (Zizzik).

The GAPS the owner most wants filled (aim at least three of your five here):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here (a research row, a method), ideally free tier. Today only buildings (firefoam sprayer, firebreak terrain) exist; nothing is learned.
- Mark 6, GRAVSHIP TOUCH (Odyssey gravship): the ship lands in a country that is always burning somewhere. What does the burn do to, with, or for a landed gravship, its launch, or its travel? (Avoid the Leaning Scrub's "the plain reads the ship as fire and herds converge on a launch", and Stillsand's "the dunes take the ship".)
- Mark 7, SOUNDSCAPE beyond the plain ambient bed we already proposed: a sound that MATTERS in play.
- Mark 9, RELATIONSHIP TO THE GODS of the Salvation (not the Tribes): favour only via events/odds; rites create cohesion only. Gods: Ishko (hiding, ambush, prepared dark), Ohm (the living machine), Oomo (water; OVERFED, avoid), Mob'Unloo (debt, trade, exchange), Rekko (salvage, repair, the discarded rewoken), Ta'Baa (flight, refusal to root), Zizzik (malfunction, the wrong spark; fed by fires and breakdowns), Sh'kaar (the searing sun, exposure; perversely fed by destruction incl. our own losses, then lenient a while), Ozzik (ambition, pride, grief). Zizzik already has four rites (avoid him); NEVER gate a rite on darkness (the Abyss owns that); avoid "set your own field alight as a last rite" (Leaning Scrub's Calling-Pyre, Zizzik).
- Mark 5, the GIANT: the furnace-beast-as-giant is already proposed; a different answer is welcome only if it is not just another big animal.

# Other biomes' signatures: AVOID these (each line is a biome's spine and signature mechanics)

- The Abyss (dark crags): the Dark as real air that blinds and swallows lamplight while HEAT OPENS CLEAR POCKETS in it; the Unveiling (rare lifting of the Dark); the Summ storm-dragons and the brood-mother Summ the All-Render; etchfall (falling grain erodes unroofed walls into tholin dust); the etchcap fungus; lamps as crops; a hidden ship that vanishes from pursuit (with probe droids hunting it); the fold-lamp (research: warmth pushes the Dark back); four darkness rites (Dark Vigil, Blind Offering left in the dark overnight, the Snuffing of lights, the Lightless Burial).
- Stillsand: the Listening / geophone, sand-swimming predators with a rumble, the dunes take the ship, the Stillstorm, the Return, biosilica optics, eternal noon.
- Long Shade: shade as currency, the golden hour, the shade awning / Shipfall Commons, the khorrak alloy, the dew condenser, middens.
- Leaning Scrub: the Stall-and-Gale wind calendar, the Lean, the tallest thing on the plain, the vaporator, the smother-craft, the calling-pyre.
- Blue Desert: silence-then-boom, the blue-ice heat sink, katabatic drift, the returned hulls the ablation line gives up.
- Cracked Lands: read-the-land survey, water-wake, flash floods, floodline salvage claim.
- Cauldron: fluid conversion, the four-stroke weather, condensate gardens, vent blooms, eyeless vibration-sensing ambusher.
- Forge: giant-on-the-clock, floatstone keelwork, the four voices, white plume fronts.
- Wasteland: named storms (Deadlight Halo, Cinderwire), storm exhumation, the Middenshell procession, the Sealed Cask Bay, the Rite of Tipping.
- Warscar: the Settling (calm → fallout film that keeps tracks), the aerosol screen, the Geiger choir, the hospice, the old tongue, the rainbow pools.
- Contagion: draftprints / bodyprints, the Dive, the Bloom and the Burn, the Unfinished.
- The Rot: the Sheen exposure lock, warm ground, accelerated rot, the treasure conscience.
- Fever Wood: mirror pools that swallow drinkers, ground refusal, two-front lure stakes, a tentacle elder met as six limbs.
- Greentide: churnmud that mires and swallows, buried caches, frenzy disease, the roil weather, the greatbole tree.
- Gelatinous Slime: slimification, field conversion, slime rain, gene archive, the titanoslime.
- Weeping Stones: stocked pools with pens and culling, the water truce with animal retribution, the giant stone-crab.
- The Sump: tar moats with fuse posts, dig-strata lottery, tar-vault seal, the pit belch, the eternal dusk lock.
- Miasma: the gradient axis and the sea surge, warden-mother succession, crèche nurseries, fever-forging, permanent haze.
- Webwork: the creeping web front, nest scatter, egg-clutch relay, loom-binding, sun scald.
- Rust Cathedral: the hum (a biome mood that answers your behaviour), living bolts that behave differently when watched, the deep-drill response.
- Nightside Ice: the heat dial (your heating draws blind thermal tunnelers), the breach loop and rumble-tell, the hull rule, the larder, the thaw pulse and calving of the well-provisioned dead out of the ice, the sohl (moves once), the hessarund (a ridge that is one living organism, quiet landform), the reconnection storm on the surface, the Cold Ledger rite (seal a counter-gift in ice to pay a frozen dead man's debt, Mob'Unloo).
- Twilight Deep / Twilight Sea: the light economy (skylight wells, the sun-sphere, mobile lamp constellations), mud-channel rivers, lit dwellings.
- The seas (Scald, Grey, Twilight, Propane): the gravship dive to the sea floor, brine elders, an aurora-surge power plant, a fire ban in the chill sea, and "you are the only source of ignition on the hemisphere" (propane lakes).

- Lantern Deeps (underground pocket map): light that is alive; sustained light draws predators; the Lantern (the one safe light); the Working Dead and Shard-minds; Orun-Ghal, a crystal-worn dead mining suit you study and befriend; twelve hydrocarbon animals (incl. a ceiling-pinned methane giant); the ship cargo hoist; the Answering rite (Ohm, settlement with a mindstone); Zizzik's Nine Faults.

Note the nearest neighbours: the Leaning Scrub owns fire-as-last-rite (the Calling-Pyre), giants stamping fire, and the ship as the tallest thing that the plain reads as fire; the Forge owns lava, white plume fronts and a giant on the clock; the Wasteland owns named storms; the Long Shade owns shade as currency and heat you can hear (a lit-vs-shade sound bed). Stay clear of all four.

# Output format (Markdown)

Start with the two check lines (five verbs; five systems). Then for each of the five ideas:

## <n>. <evocative title>
- **Marks it serves:** (from 2, 5, 6, 7, 9, or others)
- **The player's experience:** 3-5 sentences, concrete, in play.
- **How it works in RimWorld 1.6:** def types, C# hook, what it reads and writes, Mod Settings it needs.
- **Readable signs:** what the player sees/hears so nothing happens invisibly.
- **Drawn from:** cited games/mods and their exact features; what this does that they don't.
- **Why it is unique here:** one sentence against the nearest other biome above.
- **Tier:** free (RM_) or campaign (RUT_), and why.
- **Size:** S / M / L build.

End with a 3-line ranking of which two you would build first and why. Keep the whole answer under 2,200 words.
