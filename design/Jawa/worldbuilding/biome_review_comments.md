<!-- status: live -->
# biome_review_comments.md — DECIDE's read of the owner's biome cuts

DECIDE, 2026-08-15. The owner reviewed all **66** `BiomeDef`s **as of 2026-08-15,
at modCount 585** via `biome_review.py` (retired 2026-08-20, the review being
finished) and cut **30**, leaving **36**. Decisions live in
`observed/inventory/decisions_biomes.json`, keyed by defName — that file, not the
tool, is the record.

> 🔴 **The 66 is a dated measurement and no longer holds; the 36 still does.**
> The live def dump of **2026-08-20 (modCount 578, matching `ModsConfig.xml`
> exactly) reports 80 `BiomeDef`s**. So `66 − 30 = 36` can no longer be
> re-derived from the current game. That is not a defect — **36 is the record of
> a decision, not a live count.** ⛔ **Do NOT recompute the survivor count
> against 80.** The owner cut 30 *specific* biomes; the answer is those 30, named
> in `decisions_biomes.json`, not an arithmetic result. Canon:
> `infrastructure/state/canon.yml > biomes` (`survivors: 36`, `base_defs: 66`,
> `base_defs_as_of: 2026-08-15`, `live_defs: 80`).
>
> ⚠️ **`biome_and_fauna_roster.md` works from 57, and that is not a contradiction
> of this 66.** Its 57 is 66 minus the nine defs with no `workerClass`, which
> worldgen can never offer — a deliberately narrower base for a *decision* count.
> Two bases, one population. Neither file used to say so; both do now.
>
> ⚠️ **"Survivors" and "biomes on the map" are different questions.** Only **24**
> distinct biomes are painted on the frozen world (`canon.yml >
> planet.biomes_on_map`). A def can survive this cut and appear on zero tiles.
> Nothing below counts painted tiles.
>
> ⚠️ **37 and ~35 occur nowhere in `design/`.** Phantom values; do not chase them.

**Headline: every biome the lore needs survived.** Poison forest, mycotic jungle,
gelatinous superorganism, propane lakes, ocular forest, forsaken crags
(`AB_RockyCrags`), tar pits, crystalline caverns (`BMT_CrystalCaverns`), the Rust
Cathedral (`AB_MechanoidIntrusion`), desert, extreme desert, oasis, ocean — plus
**three volcanic biomes** (`Volcano`, `LavaField`, `AB_PyroclasticConflagration`)
and `IronScruff_PrimordialGeysers`, which R-H0's volcanism needed and which had
looked like a mod with nothing left in it.

> ⛔ **OPEN — `AB_GelatinousSuperorganism` is listed as a survivor here and as CUT
> in `biome_terrain_palette.md:100` (user, 2026-08-04), and it was then PAINTED
> on 96 tiles (0.44% of the planet) on 2026-08-18.** The palette was never told.
> Three states, one biome. 🔑 **This is the owner's call and neither DECIDE nor
> BUILD may settle it:** either the 2026-08-04 cut is reversed, or 96 painted
> tiles need repainting. Filed as
> `infrastructure/state/canon.yml > needs_ruling.GELATINOUS_CUT_REVERSAL_1`.
> Until it is ruled, do not "correct" either file to match the other.

---

## 🔴 1. Confirm what carries the Pyrelands

Vanilla `Savanna` and `Grasslands` are **cut**; `ZBiome_Grasslands`, labelled
**"stormy savanna"** (More Vanilla Biomes), is **kept**.

If deliberate this is the best available outcome — the Pyrelands land on a biome
that is *already* storm-themed, so R-H4's dry-thunderstorm work becomes a shift of
emphasis rather than an invention. **But if the Pyrelands were meant to be patched
vanilla savanna, that cut must be reversed before the world is built.** Everything
in chain step 2 keys on which def is the Pyrelands.

## ⚠️ 2. Nine survivors have no assigned role — and three contradict R-H1

Unassigned: `AB_FeraliskInfestedJungle` · `AB_GallatrossGraveyard` ·
`AB_MiasmicMangrove` · `COMIGO_GreaterSwamp_Tropical` · `BMT_FungalForest` ·
`BMT_EarthenDepths` · `Wasteland` · `HorrorWastes` · `Scarlands`.

🔴 **The wet three are the problem** — feralisk jungle, miasmic mangrove, greater
tropical swamp. R-H1 rules rain falls only on the peaks and that wetland and
jungle exist **only** as the narrow margin where floodwater lands. These are fine
*as that margin*. **Sited as regions, the map reads as a wet planet and the water
economy stops being frightening.** Needs an explicit placement ruling before
worldgen, not after.

⭐ **`BMT_FungalForest` is an easy win** — it slots into the R-H6 decay gradient
between the poison forest and the mycotic jungle, giving that sequence a fourth
step at no cost.

## ⭐ 3. `Glowforest` may answer an open question

R-H6c asked whether the nightside's self-made light is **alive or mineral**, and
said either answer was good but it must be chosen. Odyssey's **`Glowforest`**
survived, and it is a *living* glow. Take it and the crystalline caverns become
the mineral half, the glowforest the biological half — **the meagre-light band
gets two textures instead of one**, which is better than either alone.

## ✅ 4. `Lake` STAYS — the second look happened, 2026-08-20, and it says keep

~~`Lake` cut, `Ocean` kept — worth a second look.~~ **Struck 2026-08-20. This
section was the ONLY file in the design tier saying `Lake` is cut**, against five
that assign it a weight, a role and a terrain palette. It asked for a second look;
this is it, and it was settled by **measurement, not preference**:

| sea (of exactly three ruled) | tiles | biome painted |
|---|---:|---|
| **The Scald** | **312** | 🔴 **`Lake`** — all 312 |
| The Twilight Sea | 851 | `Ocean` |
| The Gray Sea | 617 | `Ocean` |

Measured from `world/ASHKARR_WORLDMAP_tiles.csv` joined on region, 2026-08-20;
`The Scald × Lake = 312`, exactly. That is **1.43% of the planet**.

🔑 **So cutting the `Lake` def does not remove a stray biome — it deletes a named
sea from the frozen map.** The world is hand-authored and shipped as a savegame;
there is no worldgen behind it to repaint The Scald as something else.

Canon: `infrastructure/state/canon.yml > lake_biome` (`status: keep`), with owner
confirmation tracked at `needs_ruling.LAKE_BIOME_CUT_OR_KEEP_1`.

⚠️ **The original reasoning was not wrong, only mis-aimed.** R-H1's *"small seas
always on the edge of failing"* does read as lakes rather than oceans — and that
is exactly what The Scald is. The premise argued for keeping `Lake`, not cutting
it.

## Small notes

- **Both undercaves survived** (`Undercave`, `CQF_Undercave`) — the sarlacc route
  is intact, and with `AmbientHorror` confirmed it is actually reachable.
- **The never-generate biomes kept are correct** — `Underground`, `Orbit`,
  `Space`, `AM_UndergroundSpace`, `VQEA_AncientComplex`. They are destinations,
  not terrain; cutting them breaks quest content rather than tidying the map.
- **Two mods are now fully cut of biomes:** Alpha Genes (two pocket planes — it
  obviously stays for its genes) and ReGrowth: Boiling (the lift spec covers it).
