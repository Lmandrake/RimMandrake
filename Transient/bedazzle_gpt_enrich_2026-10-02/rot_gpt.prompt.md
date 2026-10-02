You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, THE ROT. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

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
- The Rot is NOT an extreme-heat biome: it is nightside-cold air (median about -19 C, floor -42 C) over a living fungal mat that is metabolically WARM to lie on. That warmth is vanilla temperature on warm terrain. Never a new heat kind, never a new cold kind.
- Hard bans of this biome (frozen sheet): (1) NO conventional (green, non-fungal) plants; (2) NO pure-animal residents: every resident creature must be a fungus/animal HYBRID; (3) NO water rain ever: everything that falls is the jungle's own emission; (4) NO stockpilable teas or symbionts: the live preparations die if refrigerated or delayed, you come here and brew on site; (5) NO general gene bank (the gene-memory reactor belongs to another biome, the Slime); (6) NO psycast economy; (7) NO active bioweapon-class organism: the Rot composted the war's bioweapon material and is DISARMED; (8) NO undefended prizes: anything worth taking defends itself; (9) recognisable creatures stay recognisable.

# What the owner has liked and rejected (aim at what he likes)

- He PICKS: biome-unique LEARNED technology made from local materials that, once learned, is usable everywhere (his favourite: lightning breakers, learnable only in the Pyrelands from its lightning and sand); rites whose effect is a dramatic, RISKY world event rather than a reward (the Struck Glass: a powerful random lightning blast that might even hit the ship); living, hydrocarbon or alien fauna; GIANTS, which he often rewrites into something specific with a plot hook; ideas that tie a biome to the ship, the gods, and the Jawa clan's identity as SCAVENGER TRADERS (they buy, salvage, haggle and resell across the planet).
- He REJECTS: ship-centric gimmicks with no biome voice; automation conveniences; abstract weather mechanics; repeatable or reversible "choices"; anything needing endless animation work.

# The biome: THE ROT ("a pale forest with a heartbeat of rot"; the planet's GUT)

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- Image: a pale fungal continent on the night shoulder of the stormwall. Bone-white and lilac towers of fungus under a black sky; a glow-moss floor warm to lie on while the air above would kill you; milky ponds and streams of NOT-WATER (the jungle's own exhalation running back down); breath-fog where the mat vents heat into freezing air. Nothing here is a plant; nothing is quite an animal. All useful light is biological.
- Planetary role: the dayside photosynthesises, the stormwall shreds and exports, and the wet-toxin fraction falls here: the Rot is a continent-scale DECOMPOSER eating the sky's export forever. Long ago the war's biological weapon material fell here by lateral gene transfer; an age of ecological stability broke it down and kept only what earned its place. "Nature won here." Digestion sites: ruins the jungle grew through, quietly warm, richer in genes.
- THE SHEEN: a reproductive sleet the jungle flings outward to colonise, a fog that cloys and sticks; its coating is also called the Sheen. Breathing it without a compatible immune system virtually guarantees disease: the biome's border is enforced by its own breath. Everything sheened is being considered for colonisation; the longer you stay, the more you shine.
- THE ROT CLOCK: everything decays much faster; raw meat left out is gone within a day. Instant composting as a service.
- WHAT YOU HARVEST IS STILL ALIVE: produce keeps metabolising after harvest and pushes heat, wrecking any freezer not overbuilt.
- EVERYTHING IS CONNECTED: when a creature is badly hurt, others rush to it and SHARE its wounds (true wound-splitting on some species, a softer tend-aura on others), and this works on tamed creatures too: your herd bleeds as one. (Ruled; the creatures' descriptions promise it.)
- GUARDIANSHIP IS A LAW OF POTENCY: the tea-source mushrooms are the armed nobility, defended by suffocating spore clouds, network alarms, rings of false fruit; the AGARILUX PRIME is a permanent predatory mushroom that suffocates animals with spores and feeds on the corpses with prehensile hyphae.
- The pale tree: a mushroom anima-analog sacred to a wandering creed of the wild, granting only a few light vanilla psycasts and the feeling you should find someone to train you.

Already BUILT or RULED (do not re-pitch; you may build ON these):
- BUILT: the Sheen weathers (Sheen-fall, Sheen-storm, Sheen-mist carry 30 of 39 weather weight) and an exposure ladder (coating hediff, a protection stat on gear); warm living ground; accelerated rot; heat-pushing living produce; spore cloud incidents and spore damage types; THE TEAS (age-reversal, bioregeneration, the pleasure brew: biosculpter effects in a cup, brewed live in a brewing vessel at the grove) and FOUR SYMBIONTS (accelerated healing / massive metabolism; sleep abolished / a little psychotic; Sheen immunity / sun intolerance; a mycoid symbiote) plus a toxic injection; guardian groves for the three tea mushrooms; a treasure conscience (a bad memory for selling Rot treasure); a grown furnace (a cultivated heat-giving mushroom) and a heat gene; mushroom leather, mushroom bridges over the milk ponds, glow-goo torches, fungiponics; blastpod chemfuel (wild only); one generic research project (advanced fungi).
- Free-tier creatures (hybrids): rennok, gromma, durrok, mullgoth (shambling animal-fungus mounds that feel each other's wounds), chittik (a swarm vermin that shares every wound), vorrugath (a six-legged walking grove, the current colossus, donor-bodied), a moth, a large slow anima colossus. Ratified to become ours: the thozzik (toxic-gas hornets and queens), the illoth (a lure-light moth), the brullith (a gentle huge fungal amalgam), the brogg (a hunchbacked grazer), the grellik (a weevil in partnership with its fungus), the skerrith (a person-sized mantis that passes as a cap).
- Campaign (unbuilt): the wild creed's sacred groves and pilgrim paths; a fungal-soil trade (dig the mat, distress the hybrids, sell the soil to moisture farmers).
- NOTHING touches the ship. The biome has NO sound of its own (the sheet wants an insect hum day and night, wet settling, the hiss of Sheen-fall, warmth you can hear as slow subterranean movement).

The GAPS (aim at least four of your five here, one idea per gap where you can):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here, from local materials or observation, that is then usable everywhere. The teas and symbionts CANNOT leave (ban 4), so the tech must be something that DOES travel. Not lightning breakers (Pyrelands), not the traction lance (Webwork), not the blood-stopping lace (Greentide), not the fold-lamp (Abyss), not gaslight chemistry (Sump), not remnant rebuilding (pitched for the Rust Cathedral).
- Mark 5, the GIANT, OUR OWN: the current colossus is a donor body. Must be a fungus/animal hybrid. Never a bioweapon. Not a clone of the furnace-beast, tar beast, titanoslime, stone-crab, hessarund, Summ, the Webwork's dead urraveth, the Greentide's tree-felling herd, the Rust Cathedral's peaceful mining droid, or the Lantern Deeps' ceiling-pinned methane giant. The 'everything is connected / shared wounds' law is the natural seed.
- Mark 6, a GRAVSHIP TOUCH: the biome acting on the player's ship in its own voice. The Sheen colonising a landed hull is the obvious seed: give it a skilful, non-gimmick angle with a real decision. Not dunes taking the ship (Stillsand), not a hidden ship vanishing (Abyss), not a hull-rasping organism (pitched for Greentide), not roots in doorframes (Webwork), not stowaway hull pets that spy (Rust Cathedral).
- Mark 7, SOUNDSCAPE: a sound that does work in play (a tell, a warning, a reading of the mat), not decoration.
- Mark 9, RELATIONSHIP TO THE GODS: a rite the Salvation can FIND here (inscription at a site with a reason to be there; learned once; performable anywhere afterwards). Favour only via events and odds; cohesion only; the effect may be a dramatic, risky world event. Gods with ONE slot left each: Ishko (hiding, ambush, the prepared dark), Ohm (the living machine), OOMO the Unspilled (water, thirst, rationing AND ALL THE BODY'S WATERS: blood, sweat, lovemaking; famine angers him), MOB'UNLOO the Ever-Owed (debt, trade, the sacred exchange, ghosts laid to rest), Sh'kaar (the searing sun; hungry, dangerous), REKKO of the Second Hand (salvage, repair, the discarded rewoken). TA'BAA the Unrooted (flight, the refusal to root; his favour erodes the longer the clan stays put) has TWO slots. Ozzik (pride, grief) and Zizzik (malfunction) are FULL: do not use them. Avoid already-taken shapes: darkness and stillness vigils, offering water, first water from a filter, sealing a gift in ice to pay a frozen dead man's debt, sinking a valuable in tar, throwing a hated effigy in tar, a shrine of scrap, seating a relic in the hull, inheriting a wreck, claiming flood salvage, mending a structure into a room, repairing a droid, crossing a shadow, walking prints, sealing a returned body aboard, the launch-rite itself, felling the tallest tree at noon, ceding a room to be overgrown, burial in darkness, a boast and challenge, the Sunning (red water in the open).

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

- The Rust Cathedral (metal plateau, an ancient factory roof under eternal noon, a hum that answers your manners): the hum-mood system, living bolts that dance and freeze, the wall ladder of dead smartsteel, coolant eels, the line-cycle (every animal stops while machinery turns over). Rulings 2026-10-02: its GIANT is a massive, dim, peaceful mining droid (a digging tank with drill and scoop) escaped from the abandoned mines; its ship mark is STOWAWAY BOLTS that stay on the hull as weather-proof hull pets and are secretly the Cathedral's listening posts (a god reveals it; remove them and anger the Cathedral, or be spied on); its rites are the MENDING WELD for Rekko (restore a stretch of old structure into a properly formed room) and a DROID-REPAIR rite (repair a free droid as a sacred act, then capture or release it). Pitched there and so off-limits: remnant rebuilding from fracture casts, focused sun bars, paired interlock doors.

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
