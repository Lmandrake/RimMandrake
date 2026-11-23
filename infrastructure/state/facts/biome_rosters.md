# facts/biome_rosters.md — what our BiomeDef wild tables actually contain

One fact per entry, newest at the bottom. Correct or delete a false entry (`infrastructure/state/facts/README.md`).

---

## 2026-09-20 — third-party donor load across every owned BiomeDef

A donor is a third-party mod whose animals and plants our rosters borrow.

- The counts in the tables and in the unguarded list are of 2026-09-20.
- Later renames changed 5 row names: `RUT_Cauldron` (measured as `RUT_PoisonForest`), `RUT_Abyss`
  (`RUT_ForsakenCrags`), `RUT_Wastes` (`RUT_Wasteland`), `RUT_SleepingIce` (`RUT_NightsideIce`), `RM_TheRot`
  (`RUT_TheRot`).
- Commit `ee7c219b70` (2026-11-06) deleted 25 frozen `RUT_` BiomeDefs from `src/`. Of the BiomeDefs that this census
  measured, only `RUT_Umbra` is still in `src/`.

**How measured:** the census read all 26 `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml` with
`xml.etree.ElementTree`. It walked the `<wildPlants>` and `<wildAnimals>` children of each `BiomeDef`. It skipped XML
comments (`isinstance(tag, str)`).

It read ownership from the **`MayRequire` packageId attribute** of each entry, not from the defName prefix:

- `mandrake.*` = ours;
- `Ludeon.*` = core/DLC;
- anything else = third-party donor;
- no attribute = unguarded.

🔴 **These tables are ELEMENT-KEYED, not `<li>`-keyed.** An entry is
`<Bantha MayRequire="mlie.starwarsanimalcollection">0.8</Bantha>`. A parser that looks for `<li>` returns **zero rows
for every biome**. That zero is a failure, not a finding. The session of 2026-09-20 hit this exact failure.

🔴 **Do not infer a donor from the defName prefix.**

- The Star Wars Animal Collection ships BARE defNames: `Bantha`, `Kreetle`, `Scavrat`, `Shyrack`, `Gorg`, `Gutkurr`,
  `Jamel`, `Rat`. So a prefix rule buckets them as vanilla Core.
- A census of the same session did exactly that. It reported the desert as "98.4% donor, 40 of them vanilla". The real
  reading: those 40 are almost all the single largest donor on the planet.
- The `MayRequire` attribute is ground truth, and it is already in the file.

### Planet-wide third-party load, by donor mod (entries across all owned biomes)

| entries | packageId |
|---:|---|
| 160 | `mlie.starwarsanimalcollection` |
| 102 | `sarg.alphaanimals` |
| 21 | `neronix17.outerrim.droiddepot` |
| 8 | `vanillaexpanded.vgeneticse` |
| 7 | `oskarpotocki.vfe.insectoid2` |
| 6 | `sarg.alphabiomes` |
| 4 | `who.vfee.isopodageneline` |
| 3 | `sarg.alphamemes` |
| 2 | `mlie.horrors` |
| 2 | `biomesteam.biomescaverns` |
| 1 | `lingluo.cockroach` |
| 1 | `regrowth.botr.core` |

**Two mods carry 262 of ~330 borrowed roster entries.** Those mods are `mlie.starwarsanimalcollection` and
`sarg.alphaanimals`. A donor-retirement plan that is not mostly about those two mods is aimed at the long tail.

### Per biome — ours / core / third-party / unguarded

| biome | ours | core | 3rd-party | unguarded | top donors |
|---|---:|---:|---:|---:|---|
| `RUT_Desert` | 1 | 0 | 54 | 7 | swanimals:39, alphaanimals:7, droiddepot:7 |
| `RUT_AridShrubland` | 2 | 0 | 51 | 11 | swanimals:38, droiddepot:7, alphaanimals:4 |
| `RUT_Greentide` | 2 | 0 | 36 | 0 | swanimals:30, alphabiomes:2, alphaanimals:2 |
| `RUT_ExtremeDesert` | 0 | 0 | 22 | 3 | swanimals:10, droiddepot:7, alphaanimals:4 |
| `RUT_Miasma` | 10 | 0 | 20 | 7 | alphaanimals:10, swanimals:9 |
| `RUT_Cauldron` | 1 | 0 | 16 | 9 | alphaanimals:8, swanimals:3, alphamemes:3 |
| `RUT_FeverWood` | 3 | 0 | 15 | 0 | swanimals:10, alphabiomes:3 |
| `RUT_Abyss` | 0 | 0 | 14 | 6 | alphaanimals:14 |
| `RUT_Wastes` | 7 | 1 | 12 | 1 | alphaanimals:5, vgeneticse:4 |
| `RUT_Contagion` | 1 | 0 | 10 | 10 | alphaanimals:10 |
| `RUT_Slime` | 0 | 0 | 9 | 6 | alphaanimals:7, vgeneticse:2 |
| `RUT_WeepingStones` | 0 | 1 | 9 | 4 | swanimals:8 |
| `RM_TheRot` | 21 | 0 | 8 | 13 | alphaanimals:7 |
| `RUT_CrackedLands` | 3 | 0 | 7 | 6 | swanimals:5, alphaanimals:2 |
| `RUT_SleepingIce` | 0 | 0 | 7 | 0 | alphaanimals:7 |
| `RUT_Scarlands` | 1 | 0 | 7 | 1 | isopodageneline:3, alphaanimals:2 |
| `RUT_TheForge` | 1 | 0 | 6 | 13 | alphaanimals:3, swanimals:2 |
| `RUT_Umbra` | 0 | 0 | 4 | 4 | alphaanimals:4 |
| `RUT_Sump` | 0 | 0 | 3 | 1 | alphaanimals:3 |
| `RUT_Webwork` | 1 | 0 | 3 | 7 | swanimals:3 |
| `RUT_RustCathedral` | 1 | 0 | 2 | 0 | cockroach:1, vgeneticse:1 |
| `RUT_GreySea` | 1 | 0 | 1 | 0 | alphaanimals:1 |
| `RUT_TwilightSea` | 1 | 0 | 1 | 0 | alphaanimals:1 |
| `RUT_TheScald` | 4 | 0 | 0 | 0 | — |

**`RM_TheRot` is the only biome where we own more than we borrow** (21 ours vs 8 third-party). That is what a finished
verdict pass looks like. `RM_TheRot` is the before/after benchmark for every biome below it.

### `RM_BlueDesert` carries its commissioned hydrocarbon life (moved 2026-09-25)

FOUNDRY is a retired seat name.

- `BLUE_DESERT_LIFE_AUTHORING_1` (FOUNDRY, done 2026-09-21) authored the Swallowers/Burners/Pickers cast and the
  transparent fractal flora.
- `BLUEDESERT_RM_MOD_BUILD_1` (FOUNDRY, done 2026-09-25) moved all of it into its own mod, `mandrake.rm.bluedesert`
  (`src/RimMandrake/BlueDesert`). The BiomeDef then held:
  - `animalDensity` 0.5 and `plantDensity` 0.33;
  - 4 `wildAnimals` rows (`RM_Vekkit`/`RM_Dorrak`/`RM_Krissek` plus the inline `AA_Thunderbeast` import);
  - 6 `wildPlants` rows.
- On 2026-09-25 `RUT_BlueDesert` was FROZEN in `UtinniPatches`, to carry the world unchanged until the terminal paint
  (the one paint of the planet at the end). Commit `ee7c219b70` (2026-11-06) deleted `RUT_BlueDesert` with the other
  frozen twins.
- The roster JSON's `Vapaad` (genuinely canon Star Wars) rides `WildAnimals_BlueDesert.xml` onto `RM_BlueDesert` instead.
- The roster's own "two Star Wars rows" framing was wrong. `AA_Thunderbeast` is a plain Alpha Animals import with no Star
  Wars content. It ships inline on the RM_ def.

### Unguarded entries — no `MayRequire`, not one of our defs

Unguarded entries are present in 16 of 24 populated biomes. Vanilla Core entries need no guard and are fine. The ones
that matter are **donor defs with no guard at all**. Those defs are exactly what breaks when a donor is retired. In the
desert family:

- `RUT_Desert` — `AB_HardyGrass`, `AB_Aaklac`, `AB_DessertTree` (Alpha Biomes,
  unguarded), plus `Plant_Chakroot_Wild`, `Plant_HubbaGourd_Wild`,
  `JOE_Landopus`, `Rat`
- `RUT_ExtremeDesert` — `AB_GiantStikehr` (Alpha Biomes, unguarded), plus
  `Plant_Bloddle`, `Rat`
- `RUT_AridShrubland` — `RG_Plant_AridGrass`, `RG_Plant_CreepStern`,
  `RG_Plant_CrimsonCushion`, `RG_Plant_Dervish` (ReGrowth, unguarded), plus
  seven vanilla `Plant_*` and `Rat`

⚠️ Nobody has ruled this a defect yet. This entry records it, so that the retirement pass does not discover it the hard
way.
