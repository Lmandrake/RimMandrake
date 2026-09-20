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

## ruling — owner, 2026-09-20

Verbatim: **"50% small"**.

The small-fauna floor is **50%**, not the 60% this item recommended. Against the
measurement taken 2026-09-20, 15 of 24 habitats already pass; only the habitats
still under 50% are offenders and need small fauna added. He did not ask for an
exemption carve-out for the near-empty habitats, so none is created — a habitat
with 1-6 animals is judged by the same 50% bar as any other.

Any automatic checker built for this law uses 50%.

## status log — 2026-09-20, the lift pass

Re-verified against the same dump the sweep used (`defs.sqlite` `mods=617/6a41e05c828eed67`,
captured 2026-09-20T07:47:24Z — unchanged since the sweep, so no re-measurement drift).
All 9 offenders fixed by raising the grain (boosting existing small fauna and/or wiring
already-built, already-owner-ruled small fauna that a biome's own frozen roster JSON
named but never wired) — no megafauna cut anywhere, same shape as the Gizka fix.

| biome | before | after | what changed |
|---|---|---|---|
| `RUT_RustCathedral` | 0.0% | **92.5%** | wired `RUT_CathedralRoach` (0.12) + `GR_Mecharat` (0.5) — both already ruled in `rosters/the_rust_cathedral.json` fauna, never wired. Mynock deliberately NOT added: that same roster rules it "homeless-reserve" |
| `RUT_TheScald` | 0.0% | **96.6%** | wired `RSW_Faa` (0.5) + `RSW_Mee` (0.5) — both already ruled in `rosters/the_scald.json` fauna, never wired |
| `RUT_NightsideIce` | 16.7% | **68.8%** | wired `AA_ShockGoat` (0.03) — already ruled "visitor" in `rosters/nightside_ice.json`, never wired; the roster's other two unwired visitors (Tauntaun, Wampa) are LARGE and left out on purpose |
| `RUT_ForsakenCrags` | 33.3% | **55.6%** | boosted `AA_DuskRat` 0.5→1.5, `AA_Murkling` 0.5→1.0 (no unwired small fauna existed in this biome's own roster to draw on instead) |
| `RUT_TheRot` | 35.9% | **57.6%** | wired `AA_AngelMoth` (0.5) + `Snoruuk` (0.5) — both already ruled in `rosters/the_rot.json` fauna, never wired |
| `RUT_Webwork` | 36.4% | **58.8%** | boosted `Kreetle` 0.2→0.8 (the roster's two unwired entries, AA_Feralisk/GR_Chickenspider, are bodySize 1.0/1.1 — LARGE, so left out) |
| `RUT_TheForge` | 43.4% | **56.1%** | wired `AA_CrescendoAnole` (0.5) — already ruled in `rosters/the_forge.json` fauna, never wired |
| `RUT_WeepingStones` | 44.4% | **54.5%** | boosted `Ollopom` 0.7→1.3 (this biome's own roster already matches every wired entry one-for-one, nothing unwired to draw on) |
| `RUT_Desert` | 45.0% | **52.8%** | wired `JOE_Landopus` (0.5, this mod's own def, no MayRequire needed) + boosted `Kreetle` 0.8→1.3, `Scavrat` 0.6→1.0, `Sketto` 0.4→0.8, `WompRat` 0.4→0.7, `Rat` 0.1→0.2 |

Files touched (all in `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/`): `RUT_RustCathedral.xml`,
`RUT_TheScald.xml`, `RUT_NightsideIce.xml`, `RUT_ForsakenCrags.xml`, `RUT_TheRot.xml`,
`RUT_Webwork.xml`, `RUT_TheForge.xml`, `RUT_WeepingStones.xml`, `RUT_Desert.xml`.
`validate_patch.py` against the live def dump: 0 errors, 0 warnings on all 9. Deployed via
`deploy_custom_mods.py --mod UtinniPatches --apply` (9 files, verified in sync).

`infrastructure/state/canon.yml` now carries the law as data under `ecosystem_laws.food_pyramid`
(threshold 50%, ruled 2026-09-20, first-applied and swept history recorded there) — not just
prose in this closed item.

⚠️ **Still owed, not done here**: the measure-backed/selftested checker this item's "Owed
after he rules" section names. Recorded as `checker_owed` in the canon.yml entry too. Also
NOT chased: the side finding on droids in `RUT_Desert`/`RUT_AridShrubland`/`RUT_ExtremeDesert`
with no `race.baseBodySize` (still outside this measurement either way), and the apparent
stale `evictions` entries in `rosters/the_scald.json` that say `RSW_ElderSando`/
`RSW_SandoAquaMonster` moved OUT of the Scald while they are still wired here — a separate
roster-reconciliation question, not this law.

No live restart or in-game verification was performed this pass (session was mid-restart on
an unrelated matter and this item's scope was XML-only). `needs=deploy` reflects that the
content change is deployed to the Mods folder but not yet verified against a running game.
