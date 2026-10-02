You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, THE WEBWORK. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

# The hard requirements on your answer

1. EXACTLY FIVE ideas. Not four, not six.
2. Each idea must be clearly DIFFERENT from the other four: a different player verb, a different system it touches, and a different emotional beat. Before writing them, list the five verbs and five systems in one line each and check none repeat.
3. Each idea must be different from EVERY OTHER BIOME's signature listed below. If an idea shares a mechanism with one, name the biome and say in one sentence why this is not the same package.
4. DO DEEP RESEARCH first. Look at games like RimWorld (Dwarf Fortress, Oxygen Not Included, Kenshi, Frostpunk 1 and 2, Don't Starve / Don't Starve Together, Songs of Syx, Subnautica and Below Zero, The Long Dark, Caves of Qud, Cataclysm: Dark Days Ahead, Stonehearth, Going Medieval, Timberborn, Factorio, Against the Storm, Banished, Valheim, Project Zomboid, Surviving Mars, Death Stranding, Pathologic, Sunless Sea, Darkwood) and at RimWorld mod content (Vanilla Expanded series incl. VFE Ancients/Insectoids/Mechanoids/Pirates, Vanilla Helixien Gas Expanded, Vanilla Chemfuel Expanded, Alpha Animals, Alpha Biomes (its tar pits), ReGrowth, Dubs Bad Hygiene, Biomes! Caverns, Odyssey's gravship, Anomaly's pit gate / fleshmass / dormant horrors, Biotech, Ideology rituals). For EVERY idea, cite specifically what it draws from (game + feature, or mod + feature) and what it does that the source does not.
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
- The Webwork IS extreme heat (temperature median ~49 C, max ~64 C) under a high sun; heat is vanilla heat (heatstroke). The owner spider's sun-scald is LIGHT lethality (unroofed sunlight), never a heat kind. Fire is vanilla fire.
- Hard bans of this biome: NO tamed, traded, negotiated or allied ollathrix/Wyyyschokk, ever; no truce language; no Earth fauna/flora; silk only ever from the mouth, never an abdomen; no guaranteed-safe dense-canopy cell (safety exists only in light); the hyperweave-equivalent silk comes ONLY from this biome.

# What the owner has liked and rejected (aim at what he likes)

- He PICKS: biome-unique LEARNED technology made from local materials that, once learned, is usable everywhere (his favourite: lightning breakers, learnable only in the Pyrelands from its lightning and sand); rites whose effect is a dramatic, RISKY world event rather than a reward (the Struck Glass: a powerful random lightning blast that might even hit the ship); living, hydrocarbon or alien fauna; GIANTS.
- He REJECTS: ship-centric gimmicks; automation conveniences; abstract weather mechanics; repeatable or reversible "choices"; anything needing endless animation work.

# The biome: THE WEBWORK ("a green and white hellscape, silent, owned, and growing")

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- Image: a dayside jungle that DRANK ITS OWN RIVER. Plants grew so dense they soaked the river up into a churning thicket of nightmare plants; the map shows a jungle with no surface water because the water is INSIDE the plants. High green mountain shoulders drink storms (heavy rain on half the tiles); the other half gets zero rain and is jungle anyway because the owner species built SILK IRRIGATION GUTTERS that carry stolen water downhill. Hot (median ~49 C), high sun, UV keeps the highest peaks bare, dry desert cages it on every side.
- It is a PLANTATION, not an infested jungle: the whole biome is one organism of shadow, owned by a giant spider. It is eerily SILENT: most animals have been eaten. Its territory grows at its margins.
- THE OLLATHRIX (free tier; the campaign skins it as Star Wars' Wyyyschokk): one race, one kind, elephant-sized frame on horse-like mass, bone-white, blind, hunts by feel through the web. Mouth-loom spit at range that applies LOOM-BOUND (near-immobilization for days unless treated: helplessness, not damage); crushing mandibles; armour-cutting leg blades; nervous-system venom. Senses intruders through the web long before they see it; converges in packs; bursts from dormant ambush (looks like debris). HELPLESS IN DIRECT SUNLIGHT (sun-scald on unroofed sunlit cells). HATES DROIDS (preferential target). Untameable, enemy of all, fecund (1,000 eggs a year) and cannibal: its own main predator.
- The three wars that keep it from winning: anchor-beetles (quarrok) chew through web anchors and can be herded to cut a corridor; egg-mites (vennick) run the silk to eat eggs, a living treasure map to the nest; and the spiders' own infighting.
- The pale flowers (pellareth) follow the web: fresh blooms mean an active line, withered ones mean abandoned web and the safe path. The palette is the map.
- The LIGHT-MOAT (ruled): a sunlit clearing is the fortress; the owners cannot cross open sunlit ground; cut, burn and keep a ring clear; threats are regrowth, overcast and an untrimmed margin. Fire is the only thing that drives them back.

Already BUILT or RULED (do not re-pitch; you may build ON these):
- The creeping web front (anchor / sheet web / gutter structures advance across border maps); the web-sense map component (touch a web anywhere and it is felt nearby, pack convergence); dormant debris-pile ambush; loom-bound hediff; loom-spit; sun-scald; beetle anchor-chewing AI; harvestable silk nodes that ring the line when cut.
- The nest: a cluster structure on EVERY Webwork map (one per map), woven of young trees and rotting hides, raidable; eggs inside; a living nest re-lays every 20-30 days; egg-clutch relay; emergent spawn when a structure is destroyed.
- The silk = the game's hyperweave renamed (thrixweave in the free tier, Shokkweave in the campaign), and this biome is its ONLY source (traders stripped). Routes: cut web, butcher, raid a nest, border creep-web yields.
- The egg economy: ollathrix eggs, a smuggler's jackpot; carrying eggs MARKS you to every web you pass; a black-market egg trader and quests to assassinate someone by planting an egg in their room (campaign); the Wildsteam faction pays a bounty for mandibles and to destroy eggs; still-burners (flame weapons fuelled by tree liquor tapped here: tavrosk).
- Fauna (6, thin by doctrine, "silence is doctrine"): ollathrix (owner, bs 2.6), quarrok (anchor-cutting beetle, chitin), vennick (egg-mite current), skennet (stilt-legged prey gleaning pods the spiders sow), cravvet (scavenger parked on fresh kill sites), sivvern (silent dusk-flier that picks mites off the silk; its circling marks egg traffic).
- Flora (16): kollavane canopy tree, threllick root-mat (moves the stolen water), dulloth canopy sealer, grennick front groundcover, vessark strangler cable, varrisk irrigated reach, pellareth pale route-flowers, fellome pods (the plantation's crop), tavrosk still-tree (liquor/fuel), brennoth margin tinder, sellith gutter-weed, kessaroth snap-trap plant, norrveth needle-cast, sorrivel bait bloom, BRIMLOCK (a plant that holds the river in its flesh: you drink water out of it), ruddreth nest-bloom.
- Soundscape (built): near-silence ambient "hush" plus a web "thrum".
- Weather: vanilla jungle table (clear, fog, rain, thunderstorm). No sky of its own.

The GAPS the owner most wants filled (aim at least four of your five here, one idea per gap where you can):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here, from local materials, that is then usable everywhere (free tier). Nothing exists yet. (Not just "silk armour": the silk is already the hyperweave.)
- Mark 5, the GIANT: the ollathrix is a big spider, not a colossus. A true giant, OR a different angle on one (found, read, survived) - but remember: never tamed or allied, one race one kind (no ollathrix castes or queens), and no big-animal clone of another biome's giant.
- Mark 6, a GRAVSHIP TOUCH: the biome modifies, marks or threatens the player's ship in its own voice (the owner REJECTS ship-centric gimmicks, so it must be the biome acting on the ship, not a ship feature).
- Mark 8, INTERESTING WEATHER: sky effects that belong nowhere else (the owner rejects ABSTRACT weather mechanics: it must be visible and do something on the map).
- Mark 9, RELATIONSHIP TO THE GODS: a rite the Salvation can FIND here (an inscription/site with a reason to be there; learned once; performable anywhere afterwards). Favour only via events and odds; cohesion only; the effect may be a dramatic risky world event. Gods: Ishko (hiding, ambush, prepared dark), Ohm (the living machine; AT CAP), Oomo (water; AT CAP), Mob'Unloo (debt, trade, exchange), Rekko (salvage, repair, the discarded rewoken), Ta'Baa (flight, refusal to root), Zizzik (malfunction; avoid), Sh'kaar (the searing sun, exposure; a "hungry god"; the sun is the only thing the owners fear here), Ozzik (ambition, pride, grief). Avoid "bury or seal an offering", "light a fire you set", anything gated on darkness, "offer water back".


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
- Miasma: the gradient axis and the sea surge, warden-mother succession, crèche nurseries, fever-forging, permanent haze.
- Rust Cathedral: the hum (a biome mood that answers your behaviour), living bolts that behave differently when watched, the deep-drill response.
- Nightside Ice: the heat dial (your heating draws blind thermal tunnelers), the breach loop and rumble-tell, the hull rule, the larder, the thaw pulse and calving of the well-provisioned dead out of the ice, the sohl (moves once), the hessarund (a ridge that is one living organism, quiet landform), the reconnection storm on the surface, the Cold Ledger rite (seal a counter-gift in ice to pay a frozen dead man's debt, Mob'Unloo).
- Twilight Deep / Twilight Sea: the light economy (skylight wells, the sun-sphere, mobile lamp constellations), mud-channel rivers, lit dwellings.
- The seas (Scald, Grey, Twilight, Propane): the gravship dive to the sea floor, brine elders, an aurora-surge power plant, a fire ban in the chill sea, and "you are the only source of ignition on the hemisphere" (propane lakes).

- Lantern Deeps (underground pocket map): light that is alive; sustained light draws predators; the Lantern (the one safe light); the Working Dead and Shard-minds; Orun-Ghal, a crystal-worn dead mining suit you study and befriend; twelve hydrocarbon animals (incl. a ceiling-pinned methane giant); the ship cargo hoist; the Answering rite (Ohm, settlement with a mindstone); Zizzik's Nine Faults.

- Pyrelands (the burning savanna, dayside): the standing burn on its own clock, the four-rung ash ladder, fulgurite (lightning glass), scorch-fruit, BlackRain; the ullai herd that grazes the fresh black; the furnace-beast giant whose warmth you stand near; LIGHTNING BREAKERS (a power-grid breaker made of metal and sand, learnable only there, usable everywhere); the Struck Glass rite (break a lightning-glass ring in a storm, a huge random lightning blast, for Zizzik).


- The Sump (tar basin, permanent dusk): the tar that preserves and the dig lottery; tar moats lit into a wall; the tar belch and tarred pawns; GASLIGHT chemistry (tar + acid green gas lamps, flame statuary); the tar vault; glasswalk; mouse-lines that read the thin crust; a tar-beast giant you evacuate ahead of; rites: the Sinking (Ishko, a valuable sunk to erase ownership claims) and Mob'Unloo's Price (a good thing plus a hated effigy that holds a faction off).

Nearest neighbours to stay clear of: the Greentide (the sibling green jungle: loud lawless plenty, churnmud, frenzy, buried caches, the greatbole tree); Fever Wood (jungle with mirror pools and lures); the Abyss (owns darkness as a substance and every darkness rite); Long Shade (owns shade as currency); Lantern Deeps (living light drawing predators). Found-rite saturation by god: Oomo and Ohm are AT their cap of four found rites (do not use); Zizzik has five (avoid); Sh'kaar, Ozzik and Ta'Baa have the most room; Rekko, Ishko and Mob'Unloo have some.

# Output format (Markdown)

Start with the two check lines (five verbs; five systems). Then for each of the five ideas:

## <n>. <evocative title>
- **Marks it serves:** (from 2, 5, 7, 9, or others)
- **The player's experience:** 3-5 sentences, concrete, in play.
- **How it works in RimWorld 1.6:** def types, C# hook, what it reads and writes, Mod Settings it needs.
- **Readable signs:** what the player sees/hears so nothing happens invisibly.
- **Drawn from:** cited games/mods and their exact features; what this does that they don't.
- **Why it is unique here:** one sentence against the nearest other biome above.
- **Tier:** free (RM_) or campaign (RUT_), and why.
- **Size:** S / M / L build.

End with a 3-line ranking of which two you would build first and why. Keep the whole answer under 2,200 words.
