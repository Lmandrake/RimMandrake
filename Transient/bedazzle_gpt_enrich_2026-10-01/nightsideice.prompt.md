You are a senior game designer consulting on a RimWorld 1.6 mod campaign. The owner wants SKILLFUL, UNIQUE enhancements for one biome, the Nightside Ice. He is explicit: "We're looking for unique contributions, not just pattern replication across everywhere." Your job is to give EXACTLY FIVE ideas.

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

# The biome: the Nightside Ice ("the Sleeping Ice")

Owner-ratified sheet, frozen. Do NOT contradict any of this, and do NOT re-propose what is already ruled (listed below): build on it.

- Dirty WHITE ice (impure, geologically young) on the highest ground of the deep night, under stars and aurora. Typical temperature -45 to -22 °C, never above 0. Ice as hard as rock; it flows, crevasses, calves, and gives back what it swallowed.
- The interior is DEAD STILL (no wind; the katabatic wind starts at its edges and blows away). No precipitation on the interior. No liquid water anywhere, ever. No vents, no geothermal, no volcanism. No soil, never farmable. No photosynthesis. No glowing residents. No ordinary animal silhouettes; nothing with eyes; nothing warm-blooded, fast, fleeing or flocking on the surface.
- THE LAW: sensing is thermal only. "The player is the loudest thing on the hemisphere." Your heating is your threat generator: insulate and run cold and nothing comes; heat your base and you light a flare on a dark plain.
- Life is a CATALYST on chemical seams, sessile, laminar and enormous: "a ridge is an organism; a boulder field is one organism." Motion is paid for out of savings.
- Anything left here is preserved perfectly and indefinitely, until the ice calves it back out.

Already RULED (do not re-pitch; you may build ON these):
- Creatures: the SOHL (the one-move animal: terrain for a century, moves exactly once, inert forever after); the SHIVVEN (blind thermal tunnelers moving inside the ice, colonial, surfacing to feed on the dying); the FRISSIM (icy insects in the ice's bubbles, active only in a thaw); the DHORRUMAK (apex ice wyrm, surfaces under sustained high heat) and its WYRMLETS (juveniles that eat frissim; seeing them means you are in its country); unnamed hectare-scale catalytic sheets; chemical frosts and HOARFROST ice forms as terrain features. Visitors that stray in and die: a static-charged heat-reading grazer (zhissa), and in the campaign layer tauntaun, wampa, mahllik.
- Mechanics: the heat dial (total colony heat output continuously escalates breach frequency); the breach loop (a warren surfacing point is a visible attackable crack; the first breach is timed and taught, later ones vaguely warned); the rumble-tell (a moving grumble and ice-twitch at the shivven's position, you never see the animal); the hull rule (no burst through constructed floor or a gravship hull; your waste heat softening the ice around the base IS the breach ring; flooring is defence); no light-warding (ward with cold, never lamps); the larder (shivven drag downed pawns under the ice, stored not eaten; recovery = cutting down into the warren); the nest eruption (calving reveals the dhorrumak's eggs; taking them brings the parent).
- Events: thaw pulse (a warm intrusion softens dirty ice; it slumps, calves and releases what it held), calving delivery (machine parts, cocoons, the well-provisioned dead of failed expeditions), the lost soul (a dying traveller; save or bury; the shivven are already coming), rime-fall and ablation at the margins only, the reconnection storm (aurora: radiation up, circuits surge), the insect-fall (a freeze-dried swarm deposited from the sky), heat-drawn assailant raids, a neighbouring biome's dark cloud drifting over.
- Resources: dirty ice (melt and filter for water), calving inclusions, cold as a resource (superconduction, refrigeration, heat rejection), an aurora "electrojet tap" for power, perfect preservation.
- Settlements: buried and bermed structures with exteriors at ambient (thermal camouflage); droid enclaves built cold on purpose.

The GAPS the owner most wants filled (aim at least three of your five here):
- Mark 2, DISCOVERABLE TECHNOLOGY: something the colony LEARNS here, not just uses.
- Mark 6, GRAVSHIP TOUCH (Odyssey gravship): a landed ship is the hottest thing on the hemisphere, and nothing claims it.
- Mark 7, SOUNDSCAPE: currently silent. Canon anchor: "tunnels that make the wind sing", in a place with no wind.
- Mark 9, RELATIONSHIP TO THE GODS: the nine Jawa gods; candidates that fit this biome: Ishko (hiding, stillness, ambush, death as the perfect concealment), Mob'Unloo (the ledger, debt, exchange; "an unpaid debt follows you past death"; he is UNDER-served, prefer him), Rekko (salvage, inherited history of wrecks), Ohm (the living machine, droids). Oomo (water, family) is OVER-served: avoid him.
- Mark 5, the GIANT: the ridge-organism has no def and no behaviour beyond "it is a ridge".

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
- Lantern Deeps: pocket caverns, darkness lit only by living lanternstone, deep-flora regrowth.
- Pyrelands: it burns on its own schedule, ash layers, the burn line and firebreaks, fulgurite.
- Twilight Deep / Twilight Sea: the light economy (skylight wells, the sun-sphere, mobile lamp constellations), mud-channel rivers, lit dwellings.
- The seas (Scald, Grey, Twilight, Propane): the gravship dive to the sea floor, brine elders, an aurora-surge power plant, a fire ban in the chill sea, and "you are the only source of ignition on the hemisphere" (propane lakes).

Note the two nearest neighbours: the Abyss already owns "heat versus darkness" and "the ship hides"; the Blue Desert already owns "ice as heat sink". Stay clear of both.

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
