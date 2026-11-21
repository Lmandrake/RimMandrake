# GUIDING_PRINCIPLES — what is always true of this game

This file says what is always true of the product, above any one mod, biome or feature. `LEXICON.md` says what our
words mean. This file says what the game is. Process rules (how agents work) stay in `CLAUDE.md` and
`infrastructure/agents/CHARTER.md`. A ruling that is a case of a principle points here.

**Authority** (his third card of 2026-11-21, "Binding, short, only your rulings"). This file binds every designer and judge
agent. It holds at most 7 entries. Each entry has his words, one example that honours it and one that breaks it. Only
his ruling adds an entry. Agents may only propose, under "Proposed, not ruled", which binds nothing.

Each entry has: the sentence; his words and their date; one example that honours it and one that breaks it; its scope;
how it is checked; what makes us review it.

## 1. A mechanic works by its conditions (RULED 2026-11-21)

**The sentence.** By default, a mechanic works by the physical conditions where it acts (sun angle, heat, water,
fire, ground, roof, food, and the like), not by which biome it is in. A biome holds its data: its plants, animals,
terrain, weather odds and map generation. Many mechanics will in effect appear in one biome only, because only that
biome has the conditions: tar mechanics act where there are tar pits, or where a player carries tar; the Abyss's
mechanic needs tiny particulates, which no other map has. This is a default, not a prohibition.

**The stated exception.** A mechanic that is a heavy load even where it is not active may be left unloaded outside its
parent biome. That is an exception, not the rule: write it in the mod's design with its reason.

**His words, 2026-11-21** (item `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`; the whole text is
in the ledger and in `design/RimMandrake/standing_rulings.md` §Biome mechanics work by their conditions): *"Biome
mechanics in general do NOT stay confined to the biome of origin: they are universal, but that biome depends on them,
showcases them, or has the materials or sources to make them or make them shine."* Later the same day, typed on his
third card: *"No offline testing, we test only where the mechanics matter. And many mechanics WILL effectively only be
in a single biome (e.g. tar mechanics don't matter where there are no tar pits... unless the players bring tar
somewhere of course). We don't test outside the source biome at this time. Perhaps in future versions, but not now. I
also don't want to say it is FORBIDDEN to have a specific biome mechanic, that is not how the rule should be written. I
mean to say all of the biome specifics mechanics so far stated are per condition, not by some magic in a specific
biome. The Abyss is a good example. There are no tiny particulates on other maps for the mechanic to engage with, so it
will never be seen there. If we made a creature with those tiny particulates present, it should still work as in the
Abyss... but we're not doing that right now. Make sense? If a mechanic is a heavy load even when not "active" in all
other biomes, we may make the call to simply not load it outside the parent biome... I want to preserve that
capability. But that should be the exception, not the rule, and stated."* His card answers of that day are in
`standing_rulings.md` §Biome mechanics work by their conditions.

**Honours it.** His Rot floor, as he describes it: *"The Rot features a living floor covering that heats rooms and keeps
life alive in the cold through food consumption. It works anywhere, but it's native to the Rot and must be tended and
carried elsewhere."* The Rot is its source. Food, tending and (by his ask, the ticket
`RIMMANDRAKE_CONVERT_ROT_MAT_TO_CONDITIONS_AND_SUN_DEATH`) Direct Sun limit it. A second example, in his words: *"For
example, if for some reason we put the Rot near the Scald, I would expect the Direct overhead sun to mercilessly
overheat characters, burn out the fungus mats on the ground, and the plants would likely all die due to their
intolerance of the ambient local heat. But all the mechanics would remain on, just a very different outcome."*

**Breaks it.** The ashwallow dives from fire only on a Pyrelands map: `RM_JobGiver_BurrowOnFire.cs` asks
`burnLine.IsPyrelandsMap`, a list of biome defNames (code census row 2). The fire is the condition; the map's biome is
not. Also the sun-heat effects of `RM_MapComponent_ShadeGrid.cs`, which run only on a biome that carries
`RM_SunHeatExtension` (row 29). His example was shade against Direct Sun, planet-wide; he named no biome: *"I
accidentally mixed Stillsand and Long Shade. I just meant shade vs. direct sun."* (ticket
`RIMMANDRAKE_CONVERT_SHADE_AGAINST_DIRECT_SUN_PLANET_WIDE`).

**Scope.** All new design and code from 2026-11-21. Each existing mod converts when it next advances, as a planned
change for its next Design Version; no current version's bars move; Pyrelands 0.1.0 is not reworked. The per-mod list:
`design/specs/2026-11-21-guiding-principles/conversion_list.md`. By his cards of 2026-11-21:
- each "Enable outside this biome" switch becomes a plain on/off for its mechanic, default on, with no biome in it,
  when its mod converts;
- a dangerous mechanic is on by default on every map; its conditions decide where it acts;
- the Scald's hot water is physics, not a biome exception: water that hot harms the same way on any map;
- vanilla and third-party biomes follow the same rule: conditions decide, with no tag list and no master switch.

**How it is checked.** Where the mechanic matters: in game, on its home biome. No foreign-map check and no offline test
is owed for this rule (his words above: "Perhaps in future versions, but not now").

**Review when** a mechanic cannot be written as conditions; when the load exception is asked for twice for the same
kind of mechanic; at a MAJOR Design Version.

## 2. A visible effect with no meaning is removed, not confined (RULED 2026-11-21)

**The sentence.** A visible effect with no meaning is removed. It is not kept and confined to one biome.

**His words, 2026-11-21:** *"I didn't mind the steam so much, but the meaningless pale region around steamgeysers I
definitely did."*

**Honours it.** The swirling steam over a geyser stays. He did not mind it. Decorative atmosphere is not banned.

**Breaks it.** The constant pale marked region round each steam geyser. Commit `d07e03a938` confined it to The Forge
(`RM_ForgeSkyPastures.cs`, code census row 1) instead of removing it.

**Scope.** Every visible effect of every mod: a mark, ring, tint, glow or overlay with no meaning in play.

**How it is checked.** The art and cosmetic judge (`design/RimMandrake/art_judge_brief.md`) and the reads-as floor line
(`src/RimMandrake/rimflow/concept_floor.json`, `reads_as`) read each such effect against what it means.

**Review when** an effect is kept with no meaning, or a player reads a meaning that is false.

## 3. A limit lives in the world (RULED 2026-11-21)

**The sentence** (the description of the option he picked, the text of record): *"a mechanic is held back by things
the player can fight (a roof beats sunlight, farming feeds the Rot), never by a hidden code limit. Buys limits that are
gameplay. Costs design work: each spreading mechanic needs a real in-world brake, and a thriving transplant counts as
good play."*

**His words, 2026-11-21**, typed on his third card: *"A limit lives in the world"*.

**Honours it.** The Rot's living mat off the Rot eats food; when it is empty its heat stops and the mat it grew dies
back one cell at a time (`src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs`, header, "off the Rot"). The player can
see the brake and fight it with food.

**Breaks it.** The same mat inside the Rot: there it "eats nothing and spreads free" (`RM_LivingMatRoot.cs` header,
"in the Rot"), because the code reads the biome. Nothing in the world holds it back there, so nothing explains why the
Rot has not covered the planet. His ask that the mat dies in Direct Sun is the in-world brake (ticket
`RIMMANDRAKE_CONVERT_ROT_MAT_TO_CONDITIONS_AND_SUN_DEATH`).

**Scope.** Every mechanic that spreads, grows or accumulates.

**How it is checked.** The Designer names the in-world brake of each spreading mechanic; the judge reads it.

**Review when** a mechanic has no in-world brake that can be built.

## 4. An effect that implies harm is true (RULED 2026-11-21)

**The sentence** (the description of the option he picked, the text of record): *"a visual that suggests a
consequence (danger, heat, a zone) must match a real one the player can read. Decoration stays free. Buys trust in what
the screen shows. Costs a judge check on each new overlay or tint."*

**His words, 2026-11-21**, typed on his third card: *"An effect that implies harm is true"*.

**Honours it.** The heat soundscape: lit ground and shade sound different, and the bed follows the real exposure that
the sun-heat grid reports at the camera's cell (`src/RimMandrake/CreatureBehaviors/Source/RM_HeatSoundscape.cs`,
`RM_MapComponent_ShadeGrid.ExposureAt`). The swirling geyser steam is decoration, and stays free.

**Breaks it.** The constant pale marked region round each steam geyser (`RM_ForgeSkyPastures.cs`, the same case as
entry 2): it looks like a zone and has no consequence. No second case was found in our files.

**Scope.** Every overlay, tint, ring, mark, sound or glow that suggests danger, heat or a zone.

**How it is checked.** The art and cosmetic judge (`design/RimMandrake/art_judge_brief.md`) checks each new overlay or
tint against the consequence it suggests.

**Review when** a player reads a consequence that is not there.

## 5. Mechanics justify their combined load (RULED 2026-11-21)

**The sentence** (the description of the option he picked, the text of record): *"a dozen planet-wide mechanics can
each be fine and together be unreadable, a pile of chores, or slow. Each new one states what it adds to the load on
every map. Buys a brake on pile-up. Costs a judgment call that agents may apply unevenly."*

**His words, 2026-11-21**, typed on his third card: *"Mechanics justify their combined load"*.

**Honours it.** The heat soundscape adds no second sun model: it reads the exposure the sun-heat grid already computes,
which folds in roofs, cast shade, gear and moving shade (`RM_HeatSoundscape.cs` header). His own cut of 2026-10-19 is
the same kind of call: *"This is too ornate. Keep only Parasols and Tents"* (`standing_rulings.md` §Direct Sun).

**Breaks it.** None found in our files: until 2026-11-21 most mechanics were switched on only in their own biome, so no
map yet carries many of them at once. The first case will come as mods convert.

**Scope.** Every new mechanic that can act on more than one map.

**How it is checked.** Each new mechanic's design states what it adds to the load on every map (reading, chores, tick
cost); the judge reads that statement. A heavy load is the reason for entry 1's stated exception.

**Review when** two mechanics conflict on one map, or a map becomes slow or unreadable.

## Proposed, not ruled

Nothing is proposed now. An agent may add a proposed line here; it binds nothing until his ruling.
