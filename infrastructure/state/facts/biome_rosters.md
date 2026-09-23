# facts/biome_rosters.md — what our BiomeDef wild tables actually contain

One fact per entry, newest at the bottom. Append only.

---

## 2026-09-20 — third-party donor load across every owned BiomeDef

**How measured:** `xml.etree.ElementTree` over all 26 `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_*.xml`,
walking each `BiomeDef`'s `<wildPlants>` and `<wildAnimals>` children. Ownership
read from each entry's **`MayRequire` packageId attribute**, not from its defName
prefix: `mandrake.*` = ours, `Ludeon.*` = core/DLC, anything else = third-party
donor, no attribute = unguarded. XML comments skipped (`isinstance(tag, str)`).

🔴 **These tables are ELEMENT-KEYED, not `<li>`-keyed** — an entry is
`<Bantha MayRequire="mlie.starwarsanimalcollection">0.8</Bantha>`. A parser that
looks for `<li>` returns **zero rows for every biome**, which is a failure, not a
finding. (Hit this exact way, this session.)

🔴 **Do not infer a donor from the defName prefix.** The Star Wars Animal
Collection ships BARE defNames — `Bantha`, `Kreetle`, `Scavrat`, `Shyrack`,
`Gorg`, `Gutkurr`, `Jamel`, `Rat` — so a prefix rule buckets them as vanilla
Core. A census this session did exactly that and reported the desert as "98.4%
donor, 40 of them vanilla"; the real reading is that those 40 are almost all the
single largest donor on the planet. The `MayRequire` attribute is ground truth
and it is already in the file.

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

🔑 **Two mods carry 262 of ~330 borrowed roster entries.** Any donor-retirement
plan that is not mostly about `mlie.starwarsanimalcollection` and
`sarg.alphaanimals` is aimed at the long tail.

### Per biome — ours / core / third-party / unguarded

| biome | ours | core | 3rd-party | unguarded | top donors |
|---|---:|---:|---:|---:|---|
| `RUT_Desert` | 1 | 0 | 54 | 7 | swanimals:39, alphaanimals:7, droiddepot:7 |
| `RUT_AridShrubland` | 2 | 0 | 51 | 11 | swanimals:38, droiddepot:7, alphaanimals:4 |
| `RUT_Greentide` | 2 | 0 | 36 | 0 | swanimals:30, alphabiomes:2, alphaanimals:2 |
| `RUT_ExtremeDesert` | 0 | 0 | 22 | 3 | swanimals:10, droiddepot:7, alphaanimals:4 |
| `RUT_Miasma` | 10 | 0 | 20 | 7 | alphaanimals:10, swanimals:9 |
| `RUT_PoisonForest` | 1 | 0 | 16 | 9 | alphaanimals:8, swanimals:3, alphamemes:3 |
| `RUT_FeverWood` | 3 | 0 | 15 | 0 | swanimals:10, alphabiomes:3 |
| `RUT_ForsakenCrags` | 0 | 0 | 14 | 6 | alphaanimals:14 |
| `RUT_Wasteland` | 7 | 1 | 12 | 1 | alphaanimals:5, vgeneticse:4 |
| `RUT_Contagion` | 1 | 0 | 10 | 10 | alphaanimals:10 |
| `RUT_Slime` | 0 | 0 | 9 | 6 | alphaanimals:7, vgeneticse:2 |
| `RUT_WeepingStones` | 0 | 1 | 9 | 4 | swanimals:8 |
| `RUT_TheRot` | 21 | 0 | 8 | 13 | alphaanimals:7 |
| `RUT_CrackedLands` | 3 | 0 | 7 | 6 | swanimals:5, alphaanimals:2 |
| `RUT_NightsideIce` | 0 | 0 | 7 | 0 | alphaanimals:7 |
| `RUT_Scarlands` | 1 | 0 | 7 | 1 | isopodageneline:3, alphaanimals:2 |
| `RUT_TheForge` | 1 | 0 | 6 | 13 | alphaanimals:3, swanimals:2 |
| `RUT_Umbra` | 0 | 0 | 4 | 4 | alphaanimals:4 |
| `RUT_Sump` | 0 | 0 | 3 | 1 | alphaanimals:3 |
| `RUT_Webwork` | 1 | 0 | 3 | 7 | swanimals:3 |
| `RUT_RustCathedral` | 1 | 0 | 2 | 0 | cockroach:1, vgeneticse:1 |
| `RUT_GreySea` | 1 | 0 | 1 | 0 | alphaanimals:1 |
| `RUT_TwilightSea` | 1 | 0 | 1 | 0 | alphaanimals:1 |
| `RUT_TheScald` | 4 | 0 | 0 | 0 | — |

🔑 **`RUT_TheRot` is the only biome where we own more than we borrow** (21 ours vs
8 third-party) — that is what a finished verdict pass looks like, and it is the
before/after benchmark for every biome below it.

### `RUT_BlueDesert` carries its commissioned hydrocarbon life (re-read 2026-09-23)

`BLUE_DESERT_LIFE_AUTHORING_1` (FOUNDRY, done 2026-09-21) authored the Swallowers/Burners/Pickers
cast and the transparent fractal flora into `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_BlueDesert.xml`
(163 lines): `animalDensity` 0.5, `plantDensity` 0.33, 3 `wildAnimals` rows, 6 `wildPlants` rows — MEASURED
with `xml.etree`. The sheet is `design/Jawa/worldbuilding/biomes/the_blue_desert.md`; the roster JSON
`rosters/the_blue_desert.json` still lists only 2 fauna (`Vapaad`, `AA_Thunderbeast`), both unwired — owed
as `WildAnimals_BlueDesert.xml` at `BLUEDESERT_RM_MOD_BUILD_1` step 2, per that ticket's STATE section.

### Unguarded entries — no `MayRequire`, not one of our defs

Present in 16 of 24 populated biomes. Vanilla Core entries need no guard and are
fine; the ones that matter are **donor defs with no guard at all**, which is
exactly what breaks when a donor is retired. In the desert family:

- `RUT_Desert` — `AB_HardyGrass`, `AB_Aaklac`, `AB_DessertTree` (Alpha Biomes,
  unguarded), plus `Plant_Chakroot_Wild`, `Plant_HubbaGourd_Wild`,
  `JOE_Landopus`, `Rat`
- `RUT_ExtremeDesert` — `AB_GiantStikehr` (Alpha Biomes, unguarded), plus
  `Plant_Bloddle`, `Rat`
- `RUT_AridShrubland` — `RG_Plant_AridGrass`, `RG_Plant_CreepStern`,
  `RG_Plant_CrimsonCushion`, `RG_Plant_Dervish` (ReGrowth, unguarded), plus
  seven vanilla `Plant_*` and `Rat`

⚠️ Not yet ruled a defect — recorded so the retirement pass does not discover it
the hard way.
