You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, THE GREENTIDE. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

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
- The Greentide IS extreme heat (temperature median ~45 C, max ~64 C) in saturated air, with heat kind AMBIENT (steam: shade does nothing). Its 'wet-bulb overwhelm' is a campaign map condition that worsens vanilla heat, never a new heat kind.
- Hard bans of this biome (frozen sheet): NO truce, ever (open free-for-all); NO Earth-named fauna or flora (terrestrial-analog SHAPES allowed, names not); NO high-flammability native flora (saturated growth does not burn; fire is NOT the tool here); NO windowed native architecture; NO dry ground pockets beyond the habitable band; NO safe standing water (deep water always carries ambush risk). Dianoga do NOT belong here.

# What the owner has liked and rejected (aim at what he likes)

- He PICKS: biome-unique LEARNED technology made from local materials that, once learned, is usable everywhere (his favourite: lightning breakers, learnable only in the Pyrelands from its lightning and sand); rites whose effect is a dramatic, RISKY world event rather than a reward (the Struck Glass: a powerful random lightning blast that might even hit the ship); living, hydrocarbon or alien fauna; GIANTS.
- He REJECTS: ship-centric gimmicks; automation conveniences; abstract weather mechanics; repeatable or reversible "choices"; anything needing endless animation work.

# The biome: THE GREENTIDE ("a green ribbon of total war, steaming, growing while you watch")

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- Image: a gallery jungle hugging every mile of the dayside rivers that fall off a storm range, a green ribbon a few tiles wide through desert country with full desert sun (+45 degrees). The rivers STEAM all the time; an inversion lid keeps the steam from rising so it ROILS at ground level. Thesis: "water is the only argument". Maximum sun x permanent water = growth faster than anything except the things that eat it.
- OPEN FREE-FOR-ALL, NO TRUCE: everything is eating or being eaten, mating or laying eggs, growing visibly or dying trying. The loudest biome on the planet (scream, chew, drip, creak, crash); its scariest signal is SILENCE (ambience ducks out before an apex predator arrives).
- Growth is visible inch by inch; darkness brings roots, light brings leaves; ONLY DRY HEAT repels growth (and animals). Plants grow into and block your doors.
- "You don't sweat, the air sweats you": wet-bulb overwhelm. Homes are made by going DOWN: windowless round mud domes in the habitable band (too close to the river cooks you, too far desiccates). THE DRY-AIR BLOWER: a hot dry air curtain over each doorway that repels growth, repels animals and dries the room.
- The dying river: clean and sterile upstream, broad and living midstream, milky and saline downstream, ending in a RIVER GRAVE (a salt pan where the last water gives up). Droid enclaves take salt water at the graves.
- Trees grow until they crack and fall. Three fellers: GNAWED from below (insects), CRACKED from within, SHATTERED from the side (megafauna). Distant crashes are the biome's percussion.
- THE GREATBOLES: terrain-scale living towers too big to fall; you MINE chambers into the heartwood; the tree REGROWS into unclaimed tunnels and squeezes you out unless you paint the walls with toxin sealant. Wild greatboles are dungeons.
- The floor: CHURNMUD (slow, swallows dropped items, mires the unlucky, invisible under the Roil) and ROOT CAUSEWAYS (the giants' roots are raised natural roads; all pathing follows them; they move between visits).
- Fauna sorts in the sheet: Gnawers (huge tree-base insects), SHATTERERS (megafauna that knock trees over as a way of life; a herd passing is a weather event; a provoked one is a siege engine), Brakes (big fast grazers mowing the growth line; grazing suppresses encroachment), Lungers (huge submerged ambush predators), Swingers (canopy dwellers who fall into the river), Fliers (everywhere, screaming).

Already BUILT or RULED (do not re-pitch; you may build ON these):
- Churnmud mire and swallow; dig-out jobs for buried items; toxin sealant floor; sap/resin; seek-shade AI; the silence cue (predator ducks the ambience).
- The frenzy disease (a jungle fever) and SURVIVORS BECOME SPECIALISTS (a lasting fever mark on those who live: qualifications only marked people have). Danger stays FLAT as the player masters the jungle (ruled).
- Greatbole landmark: mineable heartwood, regrowth, sealant, a threshold ladder of events, the fruit (a purple fruit with three butchered products, a rind coat), the greatbole grub (a purple spined grub that looks like a fruit pile, comes down with the harvest, breeds fast). Pending: the greatbole's hum as a progress bar, thermal sanctuary in chambers, pilgrims who read the tree's wounds.
- The humming grove: a tree (thalquith) whose hum layers change as the camera walks through the grove.
- Weather (campaign): the Roil (waist-deep hot ground fog that hides the floor), steam devils (scald vortices), Breaklight (the steam lifts and the naked sun is the disaster), roil lock and wet-bulb lock conditions.
- Creatures: skerrel (gall wasps: disturb the gall and the colony comes), krannock (moss-furred canopy beetle that drops onto a marked trunk and grinds it down: the Gnawer), the canopy swinger, the stench-smoke grenade, 14 invented trees and 7 understory plants (brakkel staple fruit, the yearning fruit that wants to be eaten), 8 invented river fish incl. the lunger fry. RULED, unbuilt: the ILLISK (a shoal of toothy fish, crazy fast, nearly unkillable except with explosives: the body of the water becomes impassable) and the VURRAK (a silted ambusher indistinguishable from the bank until weight lands on it: the edge of the water cannot be trusted). The Lunger ambush comp exists. The Shatterer tree-felling aura exists in code but NO Shatterer creature exists.
- Root causeway map generation and living-bole generation exist (campaign wiring).

The GAPS the owner most wants filled (aim at least four of your five here, one idea per gap where you can):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here, from local materials, that is then usable everywhere. Today only the sealant and a grenade recipe exist; nothing is learned and kept. (Not the dry-air blower itself, which is ruled; not the traction lance or lightning breakers, which are other biomes'.)
- Mark 5, the GIANT BEAST: the colossus today is a TREE (the greatbole). The sheet's SHATTERERS are the natural giant sort; give a different, surprising ANGLE on a living megafauna giant here (never tamed or allied as a mount, never a clone of the furnace-beast, the tar beast, the titanoslime, the stone-crab, the hessarund, the Summ or the Webwork's dead urraveth).
- Mark 6, a GRAVSHIP TOUCH: the biome modifies, marks or threatens the player's ship in its own voice (the owner REJECTS ship-centric gimmicks: it must be the biome acting on the ship). NOT roots threading doorframes (pitched for the Webwork).
- Mark 9, RELATIONSHIP TO THE GODS: a rite the Salvation can FIND here (an inscription/site with a reason to be there; learned once; performable anywhere afterwards). Favour only via events and odds; cohesion only; the effect may be a dramatic risky world event. Gods: Ishko (hiding, ambush; AT CAP), Ohm (the living machine; AT CAP), Oomo (water; AT CAP), Mob'Unloo (debt; AT CAP), Sh'kaar (the searing sun; AT CAP), Zizzik (malfunction; avoid), Rekko (salvage, repair, the discarded rewoken; has room), Ta'Baa (flight, the refusal to root; has room), Ozzik (ambition, pride, grief; has room). Avoid "bury or seal an offering", "light a fire you set", darkness, "offer water back", "walk someone's prints", "cut a held person free", "fell a tree at noon".
- Also welcome: a FREE-TIER sky (the Roil and Breaklight live only in the campaign layer today; the free tier has vanilla weather), or a soundscape idea beyond the humming grove and the silence cue.

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
- Rust Cathedral: the hum (a biome mood that answers your behaviour), living bolts that behave differently when watched, the deep-drill response.
- Nightside Ice: the heat dial (your heating draws blind thermal tunnelers), the breach loop and rumble-tell, the hull rule, the larder, the thaw pulse and calving of the well-provisioned dead out of the ice, the sohl (moves once), the hessarund (a ridge that is one living organism, quiet landform), the reconnection storm on the surface, the Cold Ledger rite (seal a counter-gift in ice to pay a frozen dead man's debt, Mob'Unloo).
- Twilight Deep / Twilight Sea: the light economy (skylight wells, the sun-sphere, mobile lamp constellations), mud-channel rivers, lit dwellings.
- The seas (Scald, Grey, Twilight, Propane): the gravship dive to the sea floor, brine elders, an aurora-surge power plant, a fire ban in the chill sea, and "you are the only source of ignition on the hemisphere" (propane lakes).

- Lantern Deeps (underground pocket map): light that is alive; sustained light draws predators; the Lantern (the one safe light); the Working Dead and Shard-minds; Orun-Ghal, a crystal-worn dead mining suit you study and befriend; twelve hydrocarbon animals (incl. a ceiling-pinned methane giant); the ship cargo hoist; the Answering rite (Ohm, settlement with a mindstone); Zizzik's Nine Faults.

- Pyrelands (the burning savanna, dayside): the standing burn on its own clock, the four-rung ash ladder, fulgurite (lightning glass), scorch-fruit, BlackRain; the ullai herd that grazes the fresh black; the furnace-beast giant whose warmth you stand near; LIGHTNING BREAKERS (a power-grid breaker made of metal and sand, learnable only there, usable everywhere); the Struck Glass rite (break a lightning-glass ring in a storm, a huge random lightning blast, for Zizzik).


- The Sump (tar basin, permanent dusk): the tar that preserves and the dig lottery; tar moats lit into a wall; the tar belch and tarred pawns; GASLIGHT chemistry (tar + acid green gas lamps, flame statuary); the tar vault; glasswalk; mouse-lines that read the thin crust; a tar-beast giant you evacuate ahead of; rites: the Sinking (Ishko, a valuable sunk to erase ownership claims) and Mob'Unloo's Price (a good thing plus a hated effigy that holds a faction off).

- The Webwork (the sibling jungle that DRANK ITS OWN RIVER; silent, owned by a blind bone-white giant spider that dies in sunlight): the creeping web front, web-sense (touch a web and it is felt), the light-moat (sunlit clearings are the fortress), the nest on every map and the egg economy, thrixweave silk as the only hyperweave source, quarrok anchor-chewing beetles, vennick egg-mites. Rulings 2026-10-02: its GIANT is a DEAD colossus the spiders ate (the urraveth: a wrapped skeleton read bone by bone); its learned tech is the TRACTION LANCE (a tether emplacement that reels a target in, a sibling of the Sump's Blackline Capstan lasso-pull); its rite is THE FELLED NOON for Sh'kaar (fell the tallest tree at high noon and stand bare-headed in the sun-hole). Not chosen there, but pitched and so also off-limits: falling web sheets after storms, roots threading a landed ship's doorframes, a remembrance rite under open sky.

Nearest neighbours to stay clear of: the Webwork (sibling jungle: silent, owned, web, light-moat); Fever Wood (jungle with mirror pools, lures and a tentacle elder); the Miasma (fever-forging, crèches, haze); the Slime (field conversion); Long Shade (shade as currency).

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
