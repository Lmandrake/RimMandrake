
## spec
`HorrorWastes` (Horrors (Continued)) now holds **468 tiles, −74.9 … −33.9 °C, median −49.3**,
scattered nightside pockets in `Deadstone`, `Umbra` and `Ammonia Flats`. Its def was authored
for a warm dry region and every field reads wrong on that ground:

| field | shipped | why it is wrong at −49 °C |
|---|---|---|
| `terrainsByFertility` | `Sand` 0.01→0.45 · `Soil` 0.45→0.90 · `SoilRich` 0.90→0.99 | warm sand on the deep nightside |
| `wildPlants` | exactly one: `Plant_Agave` | a desert succulent |
| `plantDensity` | 0.5 | high, for a roster of one |
| its own `description` | *"A **dry region**…"* | authored for the band it no longer holds |

⚠️ **Do not "fix" this by moving tiles.** The placement is ruled and closed — see
`HORROR_WASTES_ON_NIGHTSIDE_1`. This item changes the DEF only.

**Ground colours, MEASURED** from the real textures (`design/Jawa/fauna/biome_palette.json`):
`AB_RockyCrags` — the near-black rock all around it — is **[30, 29, 34]**; `Ice`, its other
neighbour, is **[155, 164, 172]**.

🔑 **The read is *dark biological muck breaking through frost*, not a snowfield** — brighter
than the crags, broken and dirty rather than the flat pale sheet of sea ice. In fertility order:

1. bare frozen ground — `AB_Ice` [151,167,191] or `AB_PackedIce`
2. frost over stone — `AB_SnowOverRocks` [234,232,230]
3. dark organic breaking through — `AB_DarkMud` [33,26,20]

⛔ **`AB_Obsidian` [46,46,46] was considered and rejected** — too close to [30,29,34] to read
as a different place.

## verify
`python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs …` **and** `--live`.
Then LOOK: a quicktest map on a `HorrorWastes` tile, and the ground is not warm sand.

## criteria
- [ ] `terrainsByFertility` replaced; no `Sand`/`Soil`/`SoilRich`.
- [ ] `Plant_Agave` gone from `wildPlants`.
- [ ] `plantDensity` set to match whatever roster survives — **0 with a stated reason is an
      acceptable answer** and is DECIDE's call, not BUILD's; ask before inventing a roster.

## Watch out
⚠️ **`AB_PackedIce`, `AB_PackedSnow` and `AB_DarkGravel` are UNMEASURED.** The 68-entry palette
only covers terrains already used by a *placed* biome. Sample the texture before substituting
one for a colour named above.
⚠️ **A `PatchOperationReplace` that matches nothing is a RED ERROR, not a no-op**, and
`MayRequire` only checks the MOD, never that the def still exists. Wrap in a `Conditional` on
the def — that was the saber bug and both fauna patches.
🔴 **`animalDensity` is 3.6 and the cast is NOT this item's job** (`BIOME_CREATURE_CAST_1`).
A near-empty cast at high density is the `AB_RockyCrags` failure repeated, so do not lower the
density to paper over a missing cast — say so instead.
⛔ **Do not read `BiomeDef.wildAnimals` from the def dump.** All 80 BiomeDefs report the same
1024 alphabetical entries; it is a truncation artifact and cannot be re-derived there.
