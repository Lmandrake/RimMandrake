# Propane lands: name candidates and land description — 2026-10-03

Item `PROPANE_LANDS_RENAME_1`. Owner ruled by card (2026-10-03): the nightside LAND biome `AB_PropaneLakes`
(label "the Propane Lakes", 2,531 tiles; `src/RimUtinni/UtinniPatches/Patches/BiomeNames_Ashkarr.xml:55-60`)
gets a new name and its own description. The actual lake of propane is now "the Chill" (`RM_TheChill` /
`RUT_PropaneLake`), and the Chill's lake text was copied into this biome at
`BiomeDescriptions_Ashkarr.xml:97-102`. Method follows `biome_name_candidates_2026-09-26.md`: every
candidate traced to a phrase in the definition sheet (`biomes/the_propane_lakes.md`), checked against labels.

## Collision check

Swept every `<label>` under `src/` (xml) and the repo's `.md`/`.xml` for each candidate. No candidate equals
or contains an existing biome label. Vanilla's 25 labels (list in the 09-26 doc) are not brushed.
Already taken, so avoided: the Chill, the Fuel Snows, the Sleeping Ice, the Haze, the Stall, the Gale, the Wastes,
the Blue Desert, the Abyss. Region names inside this biome (Deadstone, Umbra, Ammonia Flats, Fuelmere,
Sootreach, Frostvein, Quiet Ground, Cinderdark) are avoided as bare names. Modded labels in the 600-mod list
were NOT swept.

## Candidates

Register: "the" + one or two plain words naming what a person meets (the Chill, the Pyrelands, the Greentide).

1. **the Rimefall** — *"It snows fuel... The plants are crystal and grow overnight from what falls"* (sheet §1); rime nodules (§0). The ground-level event of the place. Risk: "-fall" echoes "the Fuel Snows" family; reads as weather more than land.
2. **the Curtains** — *"Aurora curtains over a black mirror sea"* (§9 theme). Short, strange, beautiful. Risk: names the sky, not the ground; the mirror sea half of the image now belongs to the Chill.
3. **the Dew Point** — *"every tile's annual mean below propane's -42 C dew point"* (§0). Names the physics that defines the biome. Risk: technical and cold-sounding; "point" reads like a place on a map, not a region.
4. **the Frostglass** — crystal flora, *"translucent crystal flora... starlight on crystal"* (§9), frost-white palette. Evocative and ground-facing. Risk: sounds like a material or item (frost glass), and leans toward crystal when kyber is banned here (ban 2).
5. **the Running Flame** — *"blue flame running on the ice"* and the Burners whose halo is locomotion (§4, §9). Memorable, and names the life. Risk: promises fire in the coldest place; a player may read it as a heat biome.
6. **the Tap** — the electrojet tap, *"long grounded wire loops across the ice"* (§7). Names the unique thing you can build. Risk: ordinary word; collides in meaning with the tap mechanic and 38 files use "the tap".
7. **the Exhaust** — *"the exhaust port of a machine"* (sheet thematic handle). Strong and eerie. Risk: spoils terramanufacture, a past-why the player is not cleared to read; use only if the owner accepts the hint.
8. **the Antipode** — antistellar regime, *"the far end of the world"* (§1, §2). Plain geographic fact. Risk: academic register unlike the other names; Umbra already carries the "far end" idea.
9. **the Starfrost** — *"starlit and curtain-lit"*, *"Not dark"* (§1). Gentle and pretty. Risk: generic fantasy sound; close in feel to "Sleeping Ice".
10. **the Blue Flame Ice** — Burners crossing ice (§4). Risk: three words, clumsy, and over-specific; listed only for completeness.

Recommended: **the Rimefall** (owner picks; best fit for ground, no spoiler, no collision).

## Draft land description (name-agnostic; no name appears in the text)

> Frozen ground under the brightest sky on the planet, where the cold is far below the point at which fuel turns liquid and a fine snow of hydrocarbon crystals falls without end. Translucent crystal growth rises overnight from what settles, and the aurora lights the ice from above at all hours. The few things that move across it do so in a halo of blue flame.

Drawn only from sheet §0 (cold, dew point), §1 (brightest sky, fuel snow, crystal plants grown overnight),
§4 (Burners' blue-fire locomotion), §4b (aurora-clear). Deliberately omits: the lake and its fuel sea (now the Chill),
the war lab, the machine and its origin (SSGM-gated, ban 8), the crater ending, and ammonia chemistry.
Register matches the neighbours (the Rot and the Blue Desert descriptions: sensory, 2-4 sentences, no plot).
Risk: the last sentence promises burning creatures; the sheet rules this ("always in flame when moving").
