# Mutator Placement Audit — WORLDMAP_FINAL_REVIEW_1 (offline lane)

**Instrument**: `Transient/worldreview/mutators.json` (fresh live-bridge dump, 2026-09-12,
21,872 tiles examined, 14,394 carrying mutators — 27,887 total mutator instances — no
truncation, `limitHit: false`) joined against `world/ASHKARR_WORLDMAP_tiles.csv`
(21,872 data rows, parsed with `csv.DictReader`) on `tile`, plus
`Transient/worldreview/landmarks.json` (3,414 landmark placements) for the
ancient-ruin join in Rule 2. Rules per
`design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md` §"Owner rulings".
Every count below is MEASURED from this join unless marked UNMEASURED with a reason.

---

## Rule 1 — Steam geysers: radial decay from mountains/vulcanism, zero at/past terminator (arc≥90)

- `SteamGeysers_Increased`: **33 tiles MEASURED** (down from the 54 tiles the
  frozen-map audit recorded). **0 violations MEASURED** — max arc across all 33
  tiles is **73.98** (tile 10527, `AB_MycoticJungle`); none reach arc 90.
- `VEE_SteamGeysers_Decreased` (the "kill it" mutator): **0 tiles**, unchanged
  from the prior audit — still unused anywhere on Ash'karr.
- **Comparison with the known 21-tile finding**: the frozen-map audit found
  54 `SteamGeysers_Increased` tiles with 21/54 (39%) at/past arc 90. This fresh
  dump shows 33 tiles, 0 violations. **54 − 33 = 21** — the exact size of the
  prior violation set — strong circumstantial evidence the 21 offending tiles
  were removed (consistent with `VAPOR_TERMINATOR_GEYSER_FIX_1` having already
  run against the live world). Not independently confirmed against that item's
  ledger state — flagged as inference, not proof.

**Violation count: 0** (steam geyser terminator rule)

---

## Rule 2 — Ancient*Vent family: allowed only on tiles carrying an ancient-ruin landmark

Family checked: `AncientSmokeVent`, `AncientToxVent`, `AncientHeatVent`,
`AB_AncientFreezingVent`, `AB_AncientGreyPallVent`, `AB_AncientBloodRainVent`,
`AB_AncientDeathPallVent`. Ancient-ruin landmark set (from `landmarks.json`,
every landmark defName present on the map starting `Ancient`/`Abandoned`, plus
`Ruins`/`FrozenRuins`/`RUT_ComplexStructures`/`RUT_GapingDoom`):
`AncientChemfuelRefinery, AncientGarrison, AncientHeatVent, AncientInfestedSettlement,
AncientLaunchSite, AncientQuarry, AncientSmokeVent, AncientToxVent, AncientWarehouse,
AbandonedColonyOutlander, AbandonedColonyTribal, Ruins, FrozenRuins,
RUT_ComplexStructures, RUT_GapingDoom`.

Per-type instance counts (MEASURED): `AncientHeatVent` 180, `AB_AncientFreezingVent`
61, `AB_AncientBloodRainVent` 43, `AB_AncientGreyPallVent` 42, `AncientSmokeVent`
34, `AB_AncientDeathPallVent` 33, `AncientToxVent` 24 — **417 total instances**.

**Violation count: 283 / 417 (68%)** — tile carries the vent mutator but no
ancient-ruin landmark (269 of the 283 have *no* landmark at all on the tile;
14 have a non-ruin landmark instead, e.g. `VEE_ContaminatedReservoir`). By type:
`AncientHeatVent` 64, `AB_AncientFreezingVent` 61, `AB_AncientBloodRainVent` 41,
`AB_AncientGreyPallVent` 35, `AncientSmokeVent` 33, `AB_AncientDeathPallVent` 30,
`AncientToxVent` 19.

Example violating tiles (15):
```
AncientSmokeVent   tile 136   ExtremeDesert       (no landmark)
AncientSmokeVent   tile 1801  PoisonForest        (no landmark)
AncientSmokeVent   tile 1965  PoisonForest        (no landmark)
AncientToxVent     tile 76    ExtremeDesert       (no landmark)
AncientToxVent     tile 918   PoisonForest        (no landmark)
AncientToxVent     tile 1023  PoisonForest        (no landmark)
AncientHeatVent    tile 69    AB_MechanoidIntrusion (landmark: VEE_ContaminatedReservoir)
AncientHeatVent    tile 676   AB_MechanoidIntrusion (no landmark)
AncientHeatVent    tile 679   AB_MechanoidIntrusion (no landmark)
AB_AncientFreezingVent  tile 196  PoisonForest    (no landmark)
AB_AncientFreezingVent  tile 377  PoisonForest    (no landmark)
AB_AncientFreezingVent  tile 455  PoisonForest    (no landmark)
AB_AncientGreyPallVent  tile 376  PoisonForest    (no landmark)
AB_AncientGreyPallVent  tile 1094 PoisonForest    (no landmark)
AB_AncientGreyPallVent  tile 1981 PoisonForest    (no landmark)
```

---

## Rule 3 — Magma vents (`AB_MagmaVents`) locked to volcanic-crater biomes

Engine whitelist: `AB_PyroclasticConflagration`, `BiomeGRimphire`.

**Total instances: 13 MEASURED** (doc's prior audit found 10 — 3 more have
appeared since). **Violations (out-of-lock): 5 MEASURED** — matches the
expected ~5 known finding exactly.

```
tile 3067   ZBiome_Badlands
tile 4143   AB_RockyCrags
tile 9002   ZBiome_Badlands
tile 20583  AB_RockyCrags
tile 20586  AB_RockyCrags
```

---

## Rule 4 — Swamp/ruin gases (rotstink→swamp, toxic/deadlife→dead-machine ruins; PoisonForest carries toxic+green gas by rule)

**Rotstink** (`VEE_RotstinkVent(s)`): 16 instances, biome/region breakdown —
`COMIGO_GreaterSwamp_Tropical` 10, `AB_MiasmicMangrove` 3, `BiomeCypreJungle` 3,
**all 16 in region "Fever Wood"** (the map's swamp region). **Violations: 0
MEASURED** — every instance sits on a swamp-flavored biome.

**Toxic** (`VEE_ToxicVent(s)`): 91 instances. 84/91 on `AB_MechanoidIntrusion`
(region "Rust Cathedral", the dead-machine ruin biome — in rule). **Violations:
7 MEASURED** — sit on biomes/regions with no dead-machine-ruin association:
```
tile 1317   AB_OcularForest        region Scald Spine
tile 3653   AB_PyroclasticConflagration  region Dune Sea
tile 7100   Volcano                region Dune Sea
tile 15176  AB_OcularForest        region Scald Spine
tile 15184  AB_OcularForest        region Scald Spine
tile 15207  AB_OcularForest        region Scald Spine
tile 19494  LavaField              region Dune Sea
```

**Deadlife** (`VEE_DeadlifeVent(s)`): 10 instances. 6/10 on `AB_MechanoidIntrusion`
(Rust Cathedral — in rule). **Violations: 4 MEASURED** — not dead-machine-ruin
biomes:
```
tile 48    Wasteland      region Ashen Wastes  arc 109.65
tile 220   Wasteland      region Ashen Wastes  arc 103.79
tile 138   RUT_BlueDesert region Cinderdark    arc 132.97
tile 216   RUT_BlueDesert region Cinderdark    arc 125.96
```
Note: the frozen-map review characterized the `RUT_BlueDesert` nightside pair
as "not a violation," but that comment was scoped to the *steam* terminator
rule (this family "isn't steam-ruled"), not to the swamp/ruin biome-family
rule being audited here — under this rule they are biome-mismatched. Whether
`RUT_BlueDesert`/`Wasteland` count as "dead-machine ruin" by design intent is
**UNMEASURED** (would need a biome-def/design read, not available from this
CSV+JSON join).

**PoisonForest toxic+green gas coverage**: PoisonForest has 546 tiles total
(CSV), 352 carry any mutator, only **18 (3.3% of 546) carry a toxic-flavored
mutator** (`AncientToxVent`). **No mutator def in the entire dump matches
"green gas"** (searched every distinct def/label for "green" — zero hits) —
**UNMEASURED for the green-gas half of the rule: the def appears not to exist
in the currently-loaded mod set**, this is a coverage gap, not a placement
violation.

**Rule 4 combined violation count: 11** (7 toxic + 4 deadlife; 0 rotstink)

---

## Rule 5 — Helixien gas vents: junker-related, Poison Forest and the Rot ONLY

Searched every distinct mutator def/label in the dump for "helix" or "vhge":
**zero matches**. `VHGE_GasGeyser` (the Helixien ThingDef) has no corresponding
`TileMutatorDef` anywhere on Ash'karr — consistent with Part 1's finding that
its placement mechanism is unconfirmed in the engine. **0 instances exist on
the map to check against the rule** — nothing to violate.

Also searched biome and region names for "rot": **zero matches** — "the Rot"
(the owner's second allowed context) does not correspond to any biome or
region string in `ASHKARR_WORLDMAP_tiles.csv`. **UNMEASURED**: cannot identify
which map feature "the Rot" refers to from this CSV+JSON instrument alone.

**Violation count: 0 (no placements exist to violate the rule); rule itself UNENFORCEABLE-TO-CHECK pending "the Rot" identification and the engine-mechanism follow-up already flagged in Part 1**

---

## Rule 6 — General

**Top 10 mutator types by count (MEASURED, 27,887 total instances):**

| rank | def | count |
|---|---|---|
| 1 | VEE_MoreSolarPower | 4,362 |
| 2 | VEE_LessSolarPower | 3,900 |
| 3 | Caves | 1,568 |
| 4 | Dunes | 1,536 |
| 5 | VEE_DeepOreDevoid | 1,534 |
| 6 | VEE_MineralDevoid | 1,533 |
| 7 | WildTattooinePlants | 1,403 |
| 8 | Mountain | 1,039 |
| 9 | MineralRich | 613 |
| 10 | Fish_Increased | 605 |

**Mutators on water-covered tiles** (`waterCovered: true`, MEASURED 1,171
total instances across all water tiles): breakdown —
Fish_Increased 382, AnimalHabitat 173, WindyMutator 151, Fish_Decreased 90,
CoastalIsland 48, AnimalLife_Increased 43, VEE_LessSolarPower 39,
VEE_SulfuricLake 31, SteamGeysers_Increased 30, Caves 26, VEE_GravelBeach 21,
Iceberg 20, VEE_SaltPlains 17, IceDunes 16, VEE_MarineSanctuary 15,
ToxicLake 14, VEE_DeepSnow 12, River 9, VEE_Cenotes 7, MixedBiome 6.

Most of these are plausible on water (fish, marine sanctuary, iceberg, toxic
lake, sulfuric lake, coastal/beach, wind). Flagged as **plainly land-only
features on a water-covered tile** (candidate anomalies, not adjudicated as
violations since no rule was given for this case): `Caves` (26), `VEE_SaltPlains`
(17), `VEE_Cenotes` (7), `VEE_DeepSnow` (12), `River` (9), `IceDunes` (16) —
**87 instances total**, UNMEASURED whether this is a real defect (no ruled
rule exists to check it against; reported as an observation per the "general"
ask, not a rule violation).

**Per-biome zero-mutator fraction, enrichment targets** (MEASURED against the
full CSV population, not just the 14,394 tiles carrying mutators):

| biome | total tiles | tiles w/ mutators | zero-mutator tiles | zero-mutator fraction |
|---|---|---|---|---|
| Desert | 2,390 | 932 | 1,458 | **61.0%** |
| Wasteland | 1,853 | 666 | 1,187 | **64.1%** |

The enrichment item's claimed figures were 53%/63% thin; current measured
values are 61.0% (Desert, +8pp vs. claim) and 64.1% (Wasteland, close to the
63% claim, +1pp). Both remain well above one-in-two tiles empty.

---

## Summary table

| rule | instances checked | violations | notes |
|---|---|---|---|
| 1. Steam geysers (terminator) | 33 (`SteamGeysers_Increased`) | **0** | was 21/54; 21 tiles appear removed since |
| 2. Ancient*Vent (ruin-only) | 417 | **283** | 68% lack an ancient-ruin landmark |
| 3. Magma vents (biome lock) | 13 | **5** | matches expected ~5 |
| 4. Swamp/ruin gases (biome family) | 117 (16+91+10) | **11** | 7 toxic + 4 deadlife; rotstink clean |
| 5. Helixien gas vents | 0 | **0** | no placements exist; "the Rot" unidentified — UNMEASURED |

**UNMEASURED items**: whether `RUT_BlueDesert`/`Wasteland` count as
"dead-machine ruin" for the Deadlife rule; identity of "the Rot" biome/region;
whether the 21-tile steam fix was applied via `VAPOR_TERMINATOR_GEYSER_FIX_1`
specifically (inferred from the count delta, not confirmed against the ledger);
whether the 87 land-only-on-water instances are a defect (no rule was given
to check them against).
