You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, THE RUST CATHEDRAL. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

# The hard requirements on your answer

1. EXACTLY FIVE ideas. Not four, not six.
2. Each idea must be clearly DIFFERENT from the other four: a different player verb, a different system it touches, and a different emotional beat. Before writing them, list the five verbs and five systems in one line each and check none repeat.
3. Each idea must be different from EVERY OTHER BIOME's signature listed below. If an idea shares a mechanism with one, name the biome and say in one sentence why this is not the same package.
4. DO DEEP RESEARCH first. Look at games like RimWorld (Dwarf Fortress, Oxygen Not Included, Kenshi, Frostpunk 1 and 2, Don't Starve / Don't Starve Together, Songs of Syx, Subnautica and Below Zero, Green Hell, The Forest / Sons of the Forest, Grounded, The Long Dark, Caves of Qud, Cataclysm: Dark Days Ahead, Stonehearth, Going Medieval, Timberborn, Against the Storm, Valheim, Project Zomboid, Death Stranding, Pathologic, Sunless Sea, Darkwood, Rain World, Terra Nil) and at RimWorld mod content (Vanilla Expanded series incl. VFE Ancients/Insectoids/Tribals, Vanilla Plants/Trees Expanded, Alpha Animals, Alpha Biomes, ReGrowth (all parts), Dubs Bad Hygiene, Biomes! Islands/Caverns, VGE/Vanilla Gravship, Odyssey's gravship, Anomaly's fleshmass and dormant horrors, Biotech, Ideology rituals). For EVERY idea, cite specifically what it draws from (game + feature, or mod + feature) and what it does that the source does not.
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
- The Rust Cathedral IS extreme heat (temperature median ~62 C, the highest steady sun on the planet, +79 degrees, overhead). Its heat kind is OVERHEAD SUN (shade works). Any heat effect worsens vanilla heat; never a new heat kind.
- Hard bans of this biome (frozen sheet): (1) NO plot truth in player-facing text (the mind's nature, the smart metal's origin, the bolts' origin, the eels' meaning stay hidden); (2) NO explanation of why droids are spared here, anywhere; (3) NO HUNTING mechanoids: the garrison defends perimeters and patrols, never pursues or raids from here; (4) no organic settlement or faction presence (only droids dwell here); (5) no true acid terrain; (6) NO explanation of what deep drilling wakes, ever; (7) NO ORDINARY WILDLIFE: nothing organic spawns except the short list (mynock flocks in the campaign, the coolant eels, scaria-mad strays dying on the edges); green flora count ZERO, no green anywhere.

# What the owner has liked and rejected (aim at what he likes)

- He PICKS: biome-unique LEARNED technology made from local materials that, once learned, is usable everywhere (his favourite: lightning breakers, learnable only in the Pyrelands from its lightning and sand); rites whose effect is a dramatic, RISKY world event rather than a reward (the Struck Glass: a powerful random lightning blast that might even hit the ship); living, hydrocarbon or alien fauna; GIANTS.
- He REJECTS: ship-centric gimmicks; automation conveniences; abstract weather mechanics; repeatable or reversible "choices"; anything needing endless animation work.

# The biome: THE RUST CATHEDRAL ("a circuit board the size of a country, humming to itself in its sleep")

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- Image: a flat metal plateau at the foot of the eternal noon (the sun nearly overhead, forever). The flatness is BUILT: the plateau IS an ancient factory; halls the size of canyons lie under the deck plate; gantry forests and cooling stacks are the only relief. A circuit-board maze of intentional walls, rust dust banked in drifts, heat shimmer, hard geometric shadows that never move, the whitest emptiest sky on the planet, no rain, no humidity, no erosion. Time stopped here.
- Under everything, always, a HUM: the voice of a vast dormant machine mind (the players are never told it is a mind). The hum shifts tone with its mood and REACTS to how you behave. You survive here by MANNERS, not walls: mine the bulk freely, touch nothing sacred, when the hum drops stop moving, when a great guardian machine crosses your line of sight be small and boring.
- Rarely a production line somewhere under the plate CYCLES ONCE: a mile of machinery turning over in its sleep; every living thing on the plateau stops until it passes (ruled, unbuilt).
- Coolant canals (the 'rivers' are not water): coolant still circulates to cool something that was never finished. Blind pale coolant eels circle the closed loop eating microfouling; fishing them is possible and deeply inadvisable (the hum changes when a line goes in).
- The densest mechanoid garrison on the planet; the really powerful ones are seen slowly on patrol, visible from far off, terrifying to any biological they spot, but they guard and patrol and do not hunt. Droids arriving with reverence are inexplicably spared: their holy city (droid enclaves) stands here.
- Dig deep enough and very bad things happen (massive mechanoid movement), never explained.
- The campaign plot (campaign tier only): the mind hides from the player because the player's ancient gravship flying around agitating the Empire is exactly what it fears; the player earns regard by manners and missions; the mind can grant gravtech boons at its own risk; if exposed, it fights and slowly falls and "the ship mourns".

Already BUILT or RULED (do not re-pitch; you may build ON these):
- BUILT: the hum-mood system (a biome attitude value moving through mood bands, three layered hum SoundDefs: drone, tense, alarm; droid commentary lines; sustained sacrilege drains faction goodwill); LIVING BOLTS (tiny mechanical 'wildlife', a bolt with legs or a gear with opinions, that dance strange resonant patterns reflecting the hum's mood, freeze when the hum drops, shed bright machined curiosities, and behave differently when watched); the CATHEDRAL ROACH (a small tireless mechanoid cleaner); coolant eel fishing with a hum consequence and a slow 'coolant load' residue hediff; the WALL LADDER (free deck plate, dead smartsteel veins: an alloy that 'was smart once, self-assembling, self-repairing, now just very good metal'; one sacred wall variant that is watched; deep LIVE pattern metal); the deep-drill response incident (undescribed); Mod Settings for all of it.
- RULED (campaign, unbuilt): the concealment arc (Regard, missions, gravtech boons priced against Imperial Heat, a walkable descent site, the exposure ending); hum literacy as learnable knowledge (reading the tones and the bolts' dances).
- Weather today: vanilla Clear 90, DryThunderstorm 4. No sky of its own.

The GAPS (aim at least four of your five here, one idea per gap where you can):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here, from local materials or observation, that is then usable everywhere. 'Self-repairing alloy' is the obvious seed (the smartsteel is dead); give a skilful, non-obvious angle. Not lightning breakers (Pyrelands), not the traction lance (Webwork), not the blood-stopping lace (Greentide), not the fold-lamp (Abyss).
- Mark 5, the GIANT: nothing colossal exists; the largest resident is tiny. The sheet's great patrolling guardian machines are the natural seed, but NOTHING organic may be giant here except possibly the eels (the only organic residents). Never a hunter (ban 3), never tamed or allied. Not a clone of the furnace-beast, tar beast, titanoslime, stone-crab, hessarund, Summ, the Webwork's dead urraveth, or the Greentide's tree-felling herd.
- Mark 6, a GRAVSHIP TOUCH: the biome acting on the player's ship in its own voice (the owner REJECTS ship-centric gimmicks). Not dunes taking the ship (Stillsand), not a hidden ship vanishing from pursuit (Abyss), not a hull-rasping organism (pitched for Greentide), not roots in doorframes (Webwork).
- Mark 8, INTERESTING WEATHER: a sky effect that belongs nowhere else, in a place with no water and no wind-driven weather (the owner rejects abstract weather mechanics; it must be seen and felt).
- Mark 9, RELATIONSHIP TO THE GODS: a rite the Salvation can FIND here (inscription at a site with a reason to be there; learned once; performable anywhere afterwards). Favour only via events and odds; cohesion only; the effect may be a dramatic, risky world event. Gods: Ishko (stillness, hiding; AT CAP), Ohm (the living machine; AT CAP), Oomo (water; AT CAP), Mob'Unloo (debt; AT CAP), Sh'kaar (the searing sun; AT CAP), Ozzik (pride, grief; AT CAP), Zizzik (malfunction; avoid). ONLY these two have room: REKKO of the Second Hand (salvage, repair, the discarded rewoken; pleased when we mend, sharply offended when we scrap the mendable) and TA'BAA the Unrooted (flight, the refusal to root; his favour erodes the longer the clan stays put). Avoid already-taken shapes: a shrine of scrap, seating a relic in the hull, laying an unfinished thing down, inheriting a dead crew's wreck, claiming flood salvage, crossing a shadow, walking someone's prints, sealing a returned body aboard, the launch-rite itself, leaving a broken thing behind as an offering, uprooting the oldest planting and dragging it out, ceding a room to be overgrown, stillness vigils, darkness rites, offering water.
- Also welcome: a FREE-TIER mechanic around the line-cycle, the hum, or hum literacy that is not already built.

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
- Gelatinous Slime: slimification, field conversion, slime rain, gene archive, the titanoslime.
- Weeping Stones: stocked pools with pens and culling, the water truce with animal retribution, the giant stone-crab.
- Miasma: the gradient axis and the sea surge, warden-mother succession, crèche nurseries, fever-forging, permanent haze.
- Nightside Ice: the heat dial (your heating draws blind thermal tunnelers), the breach loop and rumble-tell, the hull rule, the larder, the thaw pulse and calving of the well-provisioned dead out of the ice, the sohl (moves once), the hessarund (a ridge that is one living organism, quiet landform), the reconnection storm on the surface, the Cold Ledger rite (seal a counter-gift in ice to pay a frozen dead man's debt, Mob'Unloo).
- Twilight Deep / Twilight Sea: the light economy (skylight wells, the sun-sphere, mobile lamp constellations), mud-channel rivers, lit dwellings.
- The seas (Scald, Grey, Twilight, Propane): the gravship dive to the sea floor, brine elders, an aurora-surge power plant, a fire ban in the chill sea, and "you are the only source of ignition on the hemisphere" (propane lakes).

- Lantern Deeps (underground pocket map): light that is alive; sustained light draws predators; the Lantern (the one safe light); the Working Dead and Shard-minds; Orun-Ghal, a crystal-worn dead mining suit you study and befriend; twelve hydrocarbon animals (incl. a ceiling-pinned methane giant); the ship cargo hoist; the Answering rite (Ohm, settlement with a mindstone); Zizzik's Nine Faults.

- Pyrelands (the burning savanna, dayside): the standing burn on its own clock, the four-rung ash ladder, fulgurite (lightning glass), scorch-fruit, BlackRain; the ullai herd that grazes the fresh black; the furnace-beast giant whose warmth you stand near; LIGHTNING BREAKERS (a power-grid breaker made of metal and sand, learnable only there, usable everywhere); the Struck Glass rite (break a lightning-glass ring in a storm, a huge random lightning blast, for Zizzik).


- The Sump (tar basin, permanent dusk): the tar that preserves and the dig lottery; tar moats lit into a wall; the tar belch and tarred pawns; GASLIGHT chemistry (tar + acid green gas lamps, flame statuary); the tar vault; glasswalk; mouse-lines that read the thin crust; a tar-beast giant you evacuate ahead of; rites: the Sinking (Ishko, a valuable sunk to erase ownership claims) and Mob'Unloo's Price (a good thing plus a hated effigy that holds a faction off).

- The Webwork (the sibling jungle that DRANK ITS OWN RIVER; silent, owned by a blind bone-white giant spider that dies in sunlight): the creeping web front, web-sense (touch a web and it is felt), the light-moat (sunlit clearings are the fortress), the nest on every map and the egg economy, thrixweave silk as the only hyperweave source, quarrok anchor-chewing beetles, vennick egg-mites. Rulings 2026-10-02: its GIANT is a DEAD colossus the spiders ate (the urraveth: a wrapped skeleton read bone by bone); its learned tech is the TRACTION LANCE (a tether emplacement that reels a target in, a sibling of the Sump's Blackline Capstan lasso-pull); its rite is THE FELLED NOON for Sh'kaar (fell the tallest tree at high noon and stand bare-headed in the sun-hole). Not chosen there, but pitched and so also off-limits: falling web sheets after storms, roots threading a landed ship's doorframes, a remembrance rite under open sky.

- Greentide (the steaming river jungle, the loud lawless sibling): churnmud that swallows dropped things, toxin sealant, the frenzy fever and its survivor-specialist mark, the greatbole you mine rooms into while it regrows, the Roil hot ground fog, Breaklight, the dry-air door blower, root causeways, the humming grove, the silence cue. Rulings 2026-10-02: its GIANT is a TREE-FELLING HERD of huge browsers (the thurrock) whose passing is crash after crash; its learned tech is a BLOOD-STOPPING LACE (a cartridge that stops all bleeding, learned from a branch that closes its own vessels); its rite is THE CEDED ROOM for Ozzik (give your finest room to the jungle to be overgrown). The Open Boast (Ozzik: declare an ambition, a challenge answers) went to the Warscar. Pitched there and so also off-limits: a hull-rasping colonial organism on a landed ship, noise masking work.

Nearest neighbours to stay clear of: the Warscar / Scarlands next door (the Cathedral's builders' graves and last stand: the Settling fallout that keeps tracks, the Geiger choir, the hospice for deserting machines, the old tongue, pilgrim camps of kneeling chassis that face the Cathedral); the Lantern Deeps (the Working Dead, Shard-minds, a befriended dead mining suit, the Answering rite with a mindstone); the Abyss (darkness rites); Stillsand (eternal noon desert, the Listening geophone); the Sump (the ancient-preserving tar).

# Output format (Markdown)

Start with the two check lines (five verbs; five systems). Then for each of the five ideas:

## <n>. <evocative title>
- **Marks it serves:** (from 2, 5, 6, 8, 9, or others)
- **The player's experience:** 3-5 sentences, concrete, in play.
- **How it works in RimWorld 1.6:** def types, C# hook, what it reads and writes, Mod Settings it needs.
- **Readable signs:** what the player sees/hears so nothing happens invisibly.
- **Drawn from:** cited games/mods and their exact features; what this does that they don't.
- **Why it is unique here:** one sentence against the nearest other biome above.
- **Tier:** free (RM_) or campaign (RUT_), and why.
- **Size:** S / M / L build.

End with a 3-line ranking of which two you would build first and why. Keep the whole answer under 2,200 words.
