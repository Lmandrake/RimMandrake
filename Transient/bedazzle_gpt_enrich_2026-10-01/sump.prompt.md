You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, THE SUMP. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

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
- The Sump is NOT extreme heat (temperature ~ -4 to +15 C). Its cold is vanilla cold. Fire is vanilla fire.

# What the owner has liked and rejected (aim at what he likes)

- He PICKS: biome-unique LEARNED technology made from local materials that, once learned, is usable everywhere (his favourite: lightning breakers, learnable only in the Pyrelands from its lightning and sand); rites whose effect is a dramatic, RISKY world event rather than a reward (the Struck Glass: a powerful random lightning blast that might even hit the ship); living, hydrocarbon or alien fauna; GIANTS.
- He REJECTS: ship-centric gimmicks; automation conveniences; abstract weather mechanics; repeatable or reversible "choices"; anything needing endless animation work.

# The biome: THE SUMP ("the trap that remembers")

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- Image: "black glass under a sun that never rises, holding a million years of the unlucky, perfectly." The planet's oil sump: the lowest basin on the planet (1 m elevation), just past the terminator on the night side, sun ~10 degrees below the horizon forever (permanent deep dusk). Flat black tar pools and cooled glassy sheet-tar ("glass reaches"), ringed with low waxy chemotroph plants that feed on the tar's energy, not the sun. No rain, no surface water: the only liquid is tar.
- Origin: the Pyrelands' endless ash, churned by ancient floods and compressed over eons, drained downhill and nightward; the cold is the lid, nothing evaporates back. The hydrocarbon ladder runs on nightward: Blue Desert chemistry, then the Propane Lakes.
- The tar PRESERVES (anoxic, cold, patient): everything that ever blundered in is still in there. Digging is a lottery across deep time: bones and hides of unnamed ages, sunken machines, sealed casings, and armed booby traps in perfect working order. Every dig is treasure or a click. Owner ruling: dig wakes are ancient machines or ancient assailants ONLY; no normal life survives the tar.
- The tar DEFENDS: nothing crosses it willingly, and it can be lit into a terrible smoky wall nothing can cross. The export is "being left alone": moat-tar for hermits, droid enclaves, paranoid rich.
- The Junker stations: nodding pumping derricks in the dusk, gangs in tar-stiff coats, holding ponds, barrel yards, the reek; the biome's only industry, law and light. The play-style law (owner): the Sump REWARDS dirty, messy, idiosyncratic colonies and FRUSTRATES neat, tidy, controlled ones.
- The TAR BEASTS: slow, huge things IN the tar, oozing and accreting it, digesting the unfortunate. Dormant set-pieces woken by deep digs, explosions or greedy pumping; a woken one is a slow, unstoppable, station-eating catastrophe you EVACUATE AHEAD OF, never fight. Hard ban: never a fightable spawn or raid entry.
- Hard bans: no whole ancient assailant ever in the tar (partial remains only; booby traps more likely than either); no sun-driven flora; no rain or surface water; no warm-climate flavour; no Earth flora or fauna.

Already BUILT or RULED (do not re-pitch; you may build ON these):
- Poured tar moats with fuse posts that light them on command into a smoke-and-flame wall; network fire along connected tar with gate firebreaks (ruled).
- The dig shaft and the dig-strata lottery (traps weighted first).
- The tar belch: a pit randomly belches tar over the local terrain; tar coats any terrain and any pawn ("tarred": slow, stinking, mood); solvents (an acid) clean it, and the cleaning reaction releases a green gas.
- GASLIGHT: tar + acid makes a green gas; gas lamps with a dancing, warbling, colour-shifting light; flame statuary (art statues with flames issuing from them, quality scales the show); natural seep flames on the map whose first sighting TEACHES the gaslight chemistry (ruled, unbuilt).
- The tar vault: anything sealed in tar never rots, but taking it out needs acid per item, or it comes out ruined.
- Walkways: cheap plank duckboards that foul with tar; poured-bitumen "glasswalk" that never fouls but is slippery (speed cap, rare harmless pratfalls).
- Ship gifts (ruled): glasswalk ship flooring; gas lamps and flame statues aboard.
- Mouse-lines: sump-mice run the tar in lines; where the lines bend, the crust is thin or something is under it.
- Fauna: sump-mouse (the instrument), gulveth (sofa-sized tar grazer that wades the black), the thrummel family (warm furred burrowing hive under the tar lid, aggressive at its mounds; chitin and seepwax; a broodmother), brommet (wool grazer of the margin), dredgel (dig-site sifter), skarrid (still hunter that mimics a tar beast's bulge), skellarn (stilt-legged flier that lands and walks the tar). Flora: wick-plants (slow-burning stems, candles), dorvel (slow crop), skelver (forage), korveth (bitumen accumulator), brindeth (woody margin), soffeth (rings where gas rises), tolleth (grave-bloom marker), velloch (tar-surface film), mirrelin (glass-reach graze), pallick (a pale false-floor crust that lies).
- The permanent dusk lock (weather).
- Campaign: an arrival letter in which the ship's memory warns about thin tar; a precept making the flame statues a holy act for Sh'kaar.

Already PROPOSED in this sitting (do NOT re-propose): moving the tar/gaslight/vault/walkway content into the free tier; wiring the gulveth and thrummels; giving the tar beast a real body (a huge slow mound that walks toward buildings, swallows them, lays tar, sinks again; woken by explosions, construction, deep digs, pumping); a soundscape (derrick creak, pump thud, mouse skitter on glass, a room-sized bubble rising before a wake); a rite for those the tar took, held at the black mere (Rekko, consolation).

The GAPS the owner most wants filled (aim at least three of your five here):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here, from local materials, that is then usable everywhere (free tier). Gaslight chemistry exists; give something DIFFERENT that only the Sump can teach.
- Mark 9, RELATIONSHIP TO THE GODS of the Salvation: favour only via events/odds; rites create cohesion only; a rite's effect may be a dramatic risky world event. Gods: Ishko (hiding, ambush, prepared dark), Ohm (the living machine), Oomo (water; OVERFED, avoid), Mob'Unloo (debt, trade, exchange), Rekko (salvage, repair, the discarded rewoken), Ta'Baa (flight, refusal to root), Zizzik (malfunction, the wrong spark; fed by fires and breakdowns; already has five rites, avoid), Sh'kaar (the searing sun, exposure; one of "the hungry gods"; already has the Holy Flame here), Ozzik (ambition, pride, grief). NEVER gate a rite on darkness (the Abyss owns that); avoid "bury or seal an offering" (Nightside Ice's Cold Ledger) and "light a fire you set" (Leaning Scrub's Calling-Pyre).
- Mark 5, the GIANT: the tar beast's body is proposed; a different angle on the giant (how it is found, read, survived or used) is welcome, not another big animal.
- Mark 7, SOUNDSCAPE beyond the ambient bed: a sound that MATTERS in play.
- Fauna: one alien or hydrocarbon creature the roster lacks is welcome if it is not a duplicate of the cast above or of Lantern Deeps' hydrocarbon animals.

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
- Webwork: the creeping web front, nest scatter, egg-clutch relay, loom-binding, sun scald.
- Rust Cathedral: the hum (a biome mood that answers your behaviour), living bolts that behave differently when watched, the deep-drill response.
- Nightside Ice: the heat dial (your heating draws blind thermal tunnelers), the breach loop and rumble-tell, the hull rule, the larder, the thaw pulse and calving of the well-provisioned dead out of the ice, the sohl (moves once), the hessarund (a ridge that is one living organism, quiet landform), the reconnection storm on the surface, the Cold Ledger rite (seal a counter-gift in ice to pay a frozen dead man's debt, Mob'Unloo).
- Twilight Deep / Twilight Sea: the light economy (skylight wells, the sun-sphere, mobile lamp constellations), mud-channel rivers, lit dwellings.
- The seas (Scald, Grey, Twilight, Propane): the gravship dive to the sea floor, brine elders, an aurora-surge power plant, a fire ban in the chill sea, and "you are the only source of ignition on the hemisphere" (propane lakes).

- Lantern Deeps (underground pocket map): light that is alive; sustained light draws predators; the Lantern (the one safe light); the Working Dead and Shard-minds; Orun-Ghal, a crystal-worn dead mining suit you study and befriend; twelve hydrocarbon animals (incl. a ceiling-pinned methane giant); the ship cargo hoist; the Answering rite (Ohm, settlement with a mindstone); Zizzik's Nine Faults.

- Pyrelands (the burning savanna, dayside): the standing burn on its own clock, the four-rung ash ladder, fulgurite (lightning glass), scorch-fruit, BlackRain; the ullai herd that grazes the fresh black; the furnace-beast giant whose warmth you stand near; LIGHTNING BREAKERS (a power-grid breaker made of metal and sand, learnable only there, usable everywhere); the Struck Glass rite (break a lightning-glass ring in a storm, a huge random lightning blast, for Zizzik).

Note the nearest neighbours: Nightside Ice owns the dead preserved in ice and a sealed-offering rite; Lantern Deeps owns hydrocarbon animals, living light and a dead mining suit you befriend; the Pyrelands owns the fire that makes this tar and lightning glass; the Propane Lakes own "you are the only ignition". Stay clear of all four.

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
