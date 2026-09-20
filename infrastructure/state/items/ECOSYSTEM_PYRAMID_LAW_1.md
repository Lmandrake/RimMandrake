# ECOSYSTEM_PYRAMID_LAW_1 — the food-pyramid law

## The law, his words

> *"So there's a standing rule that all ecosystems must have many more smaller
> critters than large ones. Food pyramid and all that."* — owner, 2026-09-14

Applied once already, to his yes: Gizka lifted 0.3 → 1.0 in the Pyrelands roster and
its wiring, making it the most-seen animal there, above Zeer at 0.6. **The law itself
still owes a `canon.yml` entry, and the other rosters still owe the sweep.**

## The sweep — MEASURED 2026-09-20

Against `defs.sqlite` `mods=617/6a41e05c828eed67`, captured 2026-09-20T07:47:24Z, which
matches the live mod list exactly. `race.baseBodySize` is known for **2,421** animal
ThingDefs. Weighting is by **commonality**, because that is what a roster actually
controls; SMALL is `baseBodySize < 1.0` (below a human), LARGE is `>= 1.0`.
Full output: `Transient/ecosystem_pyramid_sweep_20260920.txt`.

**9 of 24 biome rosters fail the law.**

| biome | small % of commonality | defs | note |
|---|---|---|---|
| `RUT_RustCathedral` | **0.0%** | 1 | roster is one large animal |
| `RUT_TheScald` | **0.0%** | 2 | both large |
| `RUT_NightsideIce` | **16.7%** | 6 | |
| `RUT_ForsakenCrags` | **33.3%** | 14 | 🔴 the worst real roster |
| `RUT_TheRot` | 35.9% | 8 | |
| `RUT_Webwork` | 36.4% | 4 | |
| `RUT_TheForge` | 43.4% | 6 | |
| `RUT_WeepingStones` | 44.4% | 10 | |
| `RUT_Desert` | 45.0% | 56 | 🔴 the biggest roster in the set |

Passing, for contrast: `RUT_Slime` 91.1%, `RUT_FeverWood` 80.7%, `RUT_PoisonForest`
80.4%, `RUT_ExtremeDesert` 77.0%, `RUT_AridShrubland` 76.3%, `RUT_Miasma` 76.1%,
`RUT_CrackedLands` 74.4%, `RUT_Wasteland` 73.3%, `RUT_Contagion` 71.7%,
`RUT_Greentide` 63.3%, `RUT_Umbra` 58.7%, `RUT_Scarlands` 53.0%, `RUT_Sump` 52.4%,
`RUT_GreySea` and `RUT_TwilightSea` 90.9% each.

⚠️ **Three of the four worst are near-empty rosters, not inverted pyramids.**
RustCathedral has ONE animal, TheScald has two, NightsideIce six with commonalities
summing under 0.02. A roster that small cannot express a pyramid; calling it a
violation would be reading a ratio off almost no data. The genuine offenders are
**ForsakenCrags, TheRot, Webwork, TheForge, WeepingStones and Desert**.

## What needs him

Two calls, both one line:

1. **The threshold.** "Many more smaller than large" needs a number to be checkable.
   Proposed: **small ≥ 60% of a roster's total commonality**, which passes 12 of the
   24 today and fails the 9 above plus the three flat ones. A softer 50% passes 15.
2. **The near-empty rosters.** RustCathedral, TheScald, NightsideIce and the two seas
   have 1–6 entries. Either they are exempt (a shrine, a lava field and an ice cap are
   not ecosystems), or they are owed small fauna. ⇒ **Recommend exempting them and
   filing the fauna gap separately** — inventing critters to satisfy a ratio is the
   tail wagging the dog.

## Owed after he rules

- The `canon.yml` entry for the law, with the ruled threshold in it.
- A lift pass on the six genuine offenders, same shape as the Gizka fix: raise the
  grain rather than cut the megafauna, so the pyramid comes from more small animals
  rather than fewer large ones.
- A checker so the law is enforced rather than swept — the sweep script above is the
  measurement half and should become `measure`-backed and selftested.

## Side finding, not part of this law

`OuterRim_DUMDroid`, `DestroyerDroid`, `FX7Droid`, `GNKDroid`, `MSEDroid`,
`MuckrakerDroid` and one more appear in the `wildAnimals` block of `RUT_Desert`,
`RUT_AridShrubland` and `RUT_ExtremeDesert`, and **none resolves to a ThingDef
carrying `race.baseBodySize`** in the current dump. Either they are cut, or they are
mechanoids with no `race` block. Droids as wild animals may well be deliberate
(scavenged desert junk that wanders), but they are silently outside this measurement
either way. Not chased here.
