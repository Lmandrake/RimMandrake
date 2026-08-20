# biome_review_comments.md — DECIDE's read of the owner's biome cuts

DECIDE, 2026-08-15. The owner reviewed all 66 `BiomeDef`s via `biome_review.py`
(retired 2026-08-20, the review being finished) and cut **30**, leaving **36**.
Decisions live in `observed/inventory/decisions_biomes.json`, keyed by defName —
that file, not the tool, is the record.

**Headline: every biome the lore needs survived.** Poison forest, mycotic jungle,
gelatinous superorganism, propane lakes, ocular forest, forsaken crags
(`AB_RockyCrags`), tar pits, crystalline caverns (`BMT_CrystalCaverns`), the Rust
Cathedral (`AB_MechanoidIntrusion`), desert, extreme desert, oasis, ocean — plus
**three volcanic biomes** (`Volcano`, `LavaField`, `AB_PyroclasticConflagration`)
and `IronScruff_PrimordialGeysers`, which R-H0's volcanism needed and which had
looked like a mod with nothing left in it.

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

## ⚠️ 4. `Lake` cut, `Ocean` kept — worth a second look

R-H1 describes **"small seas always on the edge of failing"**, which read as lakes
far more than as oceans. Ocean's share is dialable via `elevationRange`, so this
may be right — but the hypersaline sea of R-H2 is a *small* body by design and
only the large-body def survives.

## Small notes

- **Both undercaves survived** (`Undercave`, `CQF_Undercave`) — the sarlacc route
  is intact, and with `AmbientHorror` confirmed it is actually reachable.
- **The never-generate biomes kept are correct** — `Underground`, `Orbit`,
  `Space`, `AM_UndergroundSpace`, `VQEA_AncientComplex`. They are destinations,
  not terrain; cutting them breaks quest content rather than tidying the map.
- **Two mods are now fully cut of biomes:** Alpha Genes (two pocket planes — it
  obviously stays for its genes) and ReGrowth: Boiling (the lift spec covers it).
