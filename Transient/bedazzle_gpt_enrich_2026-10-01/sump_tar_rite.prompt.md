You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner has invented a RITE for one biome, THE SUMP (a planet's tar basin), and asked: "What else could be put in the tar? What else could it do?" Your job is to answer that question with EXACTLY FIVE ideas.

# The owner's rite, verbatim (this is fixed; build on it, do not replace it)

"There should be a rite where the tribe tosses an object of value as sacrifice into the tar, as well as an effigy of something hated. If it's the Empire, it might reduce the current heat level. If it's one of the factions, perhaps some of their members when next seen appear covered in tar. You should keep going on these ideas and flesh them out more. What else could be put in the tar? What else could it do?"

Context for the two effects he named:
- "The current heat level" is IMPERIAL HEAT: the campaign's measure of how much attention the Galactic Empire is paying the player. It is an external number kept by a game-master layer outside the save (a state machine reading the game over a bridge), not an in-game stat; Empire raids, inspections and orbital detection key off it. A design rule elsewhere says Heat is never scrubbed by mission success (no laundering), so a rite lowering it is a deliberate exception the owner chose.
- "Covered in tar" is a readable sign: members of the cursed faction, next time they appear, arrive visibly tarred (the biome already has a tarred condition: slowed, stinking, filthy).
- The campaign's factions: the Galactic Empire; the Hutt Cartel; the Homestead Defense League (moisture farmers); the Deep Desert Tribes (fire-farmers); the Free Droid Enclaves; the Wildsteam Clan; the Deepwater Compact; the Geonosian Foundry Hive; the Ascendant Helix; the Blackstar Company (mercenaries); the Jawa Trade Moot; the Junkers (the Sump's own tar-station gangs).
- The player is a Jawa clan whose faith is "the Salvation": nine small jealous gods. Ishko (hiding, ambush, prepared dark), Ohm (the living machine), Oomo (water; overfed, avoid), Mob'Unloo (debt, trade, exchange, grudges collected), Rekko (salvage, repair, the discarded rewoken), Ta'Baa (flight, refusal to root), Zizzik (malfunction, the wrong spark), Sh'kaar (the searing sun; one of "the hungry gods"), Ozzik (ambition, pride, grief). NO GOD IS EVIL, and no god may be made an enemy: an effigy of a god is not allowed.

# What to give

FIVE ideas, each a different answer to "what else could be put in the tar, and what else could it do?" Each is a new OFFERING (what goes in) paired with a new CONSEQUENCE (what the tar or the world does). They extend this one rite, as variants or further offerings within it; they are not new rites of their own.

1. EXACTLY FIVE. Each must differ from the other four in what is offered AND in what kind of consequence follows (a faction's behaviour, the map, the creatures, the dead, the ship's Narrator, trade, the tar beast, etc.). Start with two check lines: the five offerings; the five consequence kinds.
2. Each must differ from the owner's two named effects (Empire effigy lowers Heat; faction effigy makes their members arrive tarred) and from every other biome's rites and signatures listed below.
3. DO DEEP RESEARCH: sacrifice and curse mechanics in games like RimWorld (Ideology rituals, Anomaly's dark rituals and psychic rituals), Crusader Kings 3 (schemes, hostile acts, sacrifice faiths), Dwarf Fortress (engravings, temples), Don't Starve (Pig King trading, the Ancient Pseudoscience Station), Darkest Dungeon (curios and their consequences), Cult of the Lamb (rituals and their trade-offs), Pathologic, Frostpunk (laws and faith), Black & White, Sunless Sea, Kenshi; and RimWorld mods (Vanilla Ideology Expanded memes and rituals, VFE Ancients, Alpha Memes, Rimsenal Feral, Anomaly addons). Real-world bog-body sacrifices and votive hoards (the Tollund Man, the Gundestrup cauldron, Bronze Age weapons thrown into rivers and bogs, curse tablets thrown into Roman springs at Bath) are an ideal grounding: cite what each idea draws from and what it does that the source does not.
4. Buildable in RimWorld 1.6: name the def types (RitualPatternDef, RitualOutcomeEffectDef, IncidentDef, HediffDef for the tarred sign, QuestScriptDef, etc.) and the main C# hook.

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


# Laws specific to this rite (violating one disqualifies the idea)

- The rite creates COHESION, never a material reward and never a power. Nothing comes back out of the tar as loot for the player.
- God favour shows only through events, world state and subtle odds, told by the ship's Narrator; never a buff, hediff or stat on the colony.
- A risky or dramatic WORLD EVENT as the effect is welcome; he loves rites whose effect is a dramatic gamble.
- What is thrown in must be really LOST (value destroyed), and the tar keeps it perfectly (the Sump's law: "the trap that remembers").
- No animal or pawn ever vanishes without a readable sign. If something living is offered, ban it or make it readable; human sacrifice is out.
- Never gate on darkness (the Abyss owns that).

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

- Nightside Ice's Cold Ledger: seal a counter-gift in ice to pay a frozen dead man's debt (Mob'Unloo). Stay clear.
- The Abyss' Blind Offering: an offering left in the dark overnight (Mob'Unloo). Stay clear.
- The Unburdening (Ozzik): destroying wealth to vent pride. Stay clear of plain "destroy wealth for nothing".

# Output format (Markdown)

The two check lines, then for each idea:

## <n>. <evocative title>
- **What is put in the tar:**
- **What it does:** 3-5 sentences in play, concrete.
- **Which god it speaks to, and why** (never as an enemy):
- **How it works in RimWorld 1.6:**
- **Readable signs:**
- **Drawn from:** cited sources, and what this does that they don't.
- **Why it is unique here:** one sentence against the nearest rite or biome above.
- **Size:** S / M / L.

End with a 3-line ranking: which two to build first and why. Keep the whole answer under 2,000 words.
