# Visual portfolio — FLORA distribution after the assignment pass (figs F1–F3)

**Built 2026-09-09** by
`design/Jawa/worldbuilding/review/gen_flora_distribution_portfolio.py`
(`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\gen_flora_distribution_portfolio.py`).
Companion to `PORTFOLIO_creature_distribution.md` (figs 4–8, fauna economy/lethality/
law) and to figs 9–11 in `gen_biome_assignment_portfolio.py` (fauna mass, size ladder,
biome matrix). **The fauna portfolios never look at plants; this one only looks at
plants.**

## Where every number comes from

| quantity | source | status |
|---|---|---|
| which plant lives in which biome, at what commonality | `design/Jawa/worldbuilding/biomes/rosters/*.json` via `rosters_residency.py` | commonality is a **DESIGN CHOICE**, never a measured stat |
| `minGrowthTemp` / `maxGrowthTemp` | `design/Jawa/mods/plant_pool.csv` (669 plant defs) | **MEASURED** |
| biome temperature envelope | `review/biome_climate.json` — transcribed **verbatim** from each sheet's "## 0. The measurements everything rests on" block, the sheet's own wording carried beside every number | **MEASURED** where the sheet states a figure; **UNMEASURED** (and excluded, named on-figure) where it does not |
| `Flammability` | `review/plant_flammability.json`, read from the inheritance-resolved def dump `defs.sqlite` (capture 2026-09-08T22:04:59Z, 600 mods, game 1.6.4871) | **MEASURED** — 647 of 669 pool defs carry the stat; the 22 without it are `ChoppedStump*`/`SmashedStump*` filler defs, not plants |

⛔ **Nothing here reads the creature register's `biomes` / `group` / `topCommonality`.**
Those are the mods' default residency on a vanilla planet and are stale for placement.

**Why the climate numbers are transcribed and not parsed.** The 34 biome sheets state
temperature in **seven incompatible textual forms** — the canonical
`Temp p10/median/p90 A/B/C °C` on only 10 sheets, and elsewhere parenthetical ranges,
range-only, per-region tables, an unlabeled triple, and six sheets with no biome-wide
figure at all. A regex tuned to the canonical form silently drops 13 sheets that DO
carry a usable number. `biome_climate.json` therefore holds one transcribed entry per
BiomeDef with `form` and `verbatim` beside it, so every figure number is checkable
against the sheet without running anything. `_freeze_matrix.csv` was **not** used: it
condenses the same §0 blocks and loses the p10/p90 spread.

---

## figF1 — `figF1_flora_landed_purged.png` — the flora work is mostly SUBTRACTION

**199 landed roster rows (143 distinct plant defs) against 198 named purges and 5
wholesale purge rulings, across 30 BiomeDefs. 35 authored-later plant defs are owed as
NEW art/defs and can be measured against nothing yet.**

- Biggest purges: **AridShrubland 56 named** against 10 landed; **Desert 25** against 5;
  **ZBiome_DesertOasis 19** against 4; **ZBiome_Grasslands 18** and **Wasteland 18**.
- Biggest landings: **AB_MycoticJungle 32** (the Rot's fungal suite, zero purges — the
  donor biome was kept and extended), **Wasteland 25**, the Forge's three defs 13 each.
- Five purge rows are **rulings, not plants** — `ALL`, `ALL-nonglow-donor-rows`,
  `(donor vanilla wildPlants, wholesale)` and two siblings. They are drawn in a separate
  pale band because each is one ruling over an unknown number of defs; folding them into
  the named count would be a made-up number. Three named purge targets
  (`PlantTreeOak`, `PlantBush`, `grimpepper`) sit outside `plant_pool.csv` and are
  counted as named purges, which is what they are.
- Purges are recorded **per sheet**, so a sheet binding several BiomeDefs shows the same
  purge count on each bar (the Forge's three, the two propane defs, the blue desert's
  two). That is the ruling's real scope, not double counting — stated on-figure.

## figF2 — `figF2_flora_temperature_fit.png` — 46 of 126 landed flora cannot grow at their biome's median

The headline the sheets already suspected, now measured: **46 of the 126 landed flora
rows in temperature-stated biomes sit where the biome's MEDIAN temperature is outside
the plant's own `[minGrowthTemp, maxGrowthTemp]` window.** The Rot alone contributes 31.

Worst misfits (biome median vs the plant's own limits):

| plant | biome | biome median | grows | short by |
|---|---|---|---|---|
| `BMT_Blastpod` | `AB_MycoticJungle` | −18.8 °C | 50 … 352 °C | 68.8 °C |
| `AB_CrystalHorn` | `RUT_PropaneLake` | −79 °C | −60 … 10 °C | 19 °C |
| `AB_CrystalFlower` | `RUT_PropaneLake` | −79 °C | −60 … 10 °C | 19 °C |
| `AB_FrostLeaf` | `RUT_PropaneLake` | −79 °C | −60 … 10 °C | 19 °C |
| `AB_RimeNodules` | `RUT_PropaneLake` | −79 °C | −60 … 10 °C | 19 °C |
| `AB_Bryolux`, `AB_Glowstool` (and the rest of the fungal suite) | `AB_MycoticJungle` | −18.8 °C | 0 … 58 °C | 18.8 °C |

- **The Rot is the known case and it is real.** Median −18.8 °C against a fungal suite
  whose `minGrowthTemp` is 0 — the whole donor twelve-species suite plus its imports.
  This is a design decision, not a bug report: either the plants get a cold-tolerance
  patch (they are the biome's own thermogenic fungi — the sheet's §3 already argues the
  warmth is metabolic), or the roster loses them. **The figure cannot decide it; it can
  only stop it being invisible.**
- **The propane lakes are the same shape one octave colder** — all four landed flora
  bottom out at −60 °C against a −79 °C water def whose own floor is −82 °C.
- ⚠️ **A red row is a design question, not proof of a dead plant.** The median is one
  number over a whole tile set; a plant failing the median may still hold its warm tail.
  And the *optimal* window (`minOptTemp`/`maxOptTemp`) is narrower still and is not
  drawn — a grey row may still grow badly.
- **5 biomes with landed flora are excluded, not guessed**, and named on the figure:
  `PoisonForest` (9 flora — the sheet states no biome-wide temperature at all),
  `AB_PyroclasticConflagration` / `LavaField` / `Volcano` (13 each — the Forge gives a
  42–56 °C range with no median), `Wasteland` (25 — per-family ranges, no aggregate).
  **That is 73 landed rows this figure cannot judge**, and the fix is a §0 median in
  those four sheets, not an interpolation here.

## figF3 — `figF3_flora_flammability.png` — the ban-9 gap, MEASURED (not the UNMEASURED list it was going to be)

`plant_pool.csv` has no flammability column, so this figure was scoped as an honest
UNMEASURED plant list. It is not: the live def dump carries an **inheritance-resolved**
`Flammability` statBase for 647 of the 669 pool defs, and **all 199 landed flora rows
resolve** — so there is no UNMEASURED rail on the figure at all, and the ban can be
linted for real.

- **185 of 199 landed flora rows will burn.** Only the Forge's three defs and the Rot
  carry fireproof (0.0) plants at all.
- 🔴 **`arid_shrubland.md` ban 9 — "No flammable living flora" — is VIOLATED by 10 of
  its 10 landed flora.** Every one: `Plant_ShrubLow` 1.0, `RG_Plant_AridGrass` **1.3**,
  `Plant_Bush` 1.0, `Plant_Brambles` 1.0, `Plant_Ripthorn` 1.0, `Plant_HealrootWild` 1.0,
  `RG_Plant_Dervish` 1.0, `RG_Plant_CreepStern` 0.6, `RG_Plant_CrimsonCushion` 0.6,
  `Plant_Nysyllin_Wild` 1.0. The ban says the native plants "resist fire greatly and burn
  only…"; the landed roster is entirely ordinary vanilla-flammability donor scrub. This
  is the single clearest actionable defect in the flora assignment: either the shrubland
  roster gets a Flammability patch alongside its landing, or ban 9 is amended.
- Values above 1.0 exist and are real (`RG_Plant_ToxiGrass`/`TallToxiGrass` 1.5, the
  yellow-grass family 1.3). One outlier is clipped and named on-figure:
  **`BMT_GreyLady` Flammability 40** in the Rot — three orders of magnitude past vanilla,
  almost certainly a donor authoring slip, and worth one look before it ships.
- **A raw mod-XML grep would have returned confident wrong numbers here** — most plants
  declare no Flammability and inherit it from an abstract `PlantBase` parent. The dump's
  `statBases` is post-inheritance, which is why it is the instrument.

---

## What this portfolio does NOT claim

- Commonality mass is not spawn count. RimWorld resolves plant density from the biome's
  own fields; nothing here carries that.
- 35 authored-later plant defs (the `new_defs` rows across every sheet) have no def to
  measure. They are drawn as a distinct segment in figF1 and are **absent** from figF2
  and figF3 — stated on both.
- The four range-only / no-median sheets are gaps in the SHEETS, not in this generator.

## Regenerate

```
python3 design/Jawa/worldbuilding/review/gen_flora_distribution_portfolio.py
python3 design/Jawa/worldbuilding/review/gen_flora_distribution_portfolio.py --refresh-flammability
```
The second re-reads `Flammability` from the live def dump into
`review/plant_flammability.json` (a committed cache, so the figure is reproducible on a
machine with no dump). Re-run it after any mod-list change; the file records the dump's
`captured_utc`, `mod_count` and `modlist_fingerprint`.

## CORRECTION 2026-09-09 (fix wave, BENCH)
figF2's headline "46 dead-temp rows" was a STALE-SOURCE reading — it took plant
stats from `plant_pool.csv` (snapshot 2026-08-23, pre-dating the tolerance patch).
Against the live dump only **6 rows / 5 defs** were genuinely dead; the fix wave
(`9574513a`) re-picked one (BMT_Blastpod → Boomshroom) and extended the rest on
sheet authority (the Rot's thermogenesis). Post-fix: **0 of 122 landed rows fail
their biome's median.** Regenerate figF2 from the live dump before citing it.
