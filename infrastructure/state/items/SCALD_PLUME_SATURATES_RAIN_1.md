## spec
`ashkarr_paint.py:481` builds the rainfall source field as

    rain_src = clip((0.35 + 3.6*lift) * moist * dayside  +  2.6 * scald_plume, 0.02, None)
               \\________ gated by dayside ________/     \\___ UNGATED ___/

`scald_plume = exp(-((d - 15)/11)**2)` peaks at **1.0**, so the plume term alone reaches
**2.6** — and `:902` computes `rain = 18 + 1650 * clip(rain_src/2.6, 0, 1)**2.2`, whose
ceiling is exactly **1668**. The plume is the one term not multiplied by `dayside`, so every
tile within ~15° of the Scald pins the rainfall scale whatever it is made of.

**596 tiles sat at that ceiling, 2.7% of the planet.** 271 were `AB_FeraliskInfestedJungle`
— the corridor the plume EXISTS to create, correct and wanted. The other 325 were not:
78 `ZBiome_Badlands`, 52 `ExtremeDesert`, 52 `ZBiome_DesertOasis`, 36 `ZBiome_Grasslands`,
31 `AB_PyroclasticConflagration`, 28 `Desert`, 23 `Volcano`, 15 `LavaField`,
6 `AB_MiasmicMangrove`, 4 `AridShrubland`. **The entire 69-tile volcanic province read as
the wettest ground on the planet.**

✅ **MITIGATED 2026-08-21, not fixed.** `ashkarr_clamp_rain.py` capped 231 arid ceiling tiles
to each biome's own 90th percentile among its unpinned tiles (`a33dbbd`), and pushed it live.
The volcanic biomes had no unpinned tile to sample and fall back to the arid pooled figure,
40 mm.

⛔ **The gate itself is still ungated**, because fixing it properly means re-running the
painter, and `rain_src` is not a leaf column there — it feeds `flow()` → `acc` → where the
rivers ARE → riparian → biome. Gating the plume re-rolls the hydrology and moves biomes, so
the ortho globes the owner accepted stop describing the file.
⚠️ And the faithful reconstruction is not available: `ashkarr_regate_rain.py` refused itself
at 67.8% exact because `lift` is computed from PRE-erosion elevation and the bundle stores
the post-erosion value.

## verify
The clamp is verified: `ashkarr_clamp_rain.py` asserts all thirteen other columns are
byte-identical across all 21,872 rows before writing, and the live read-back on tiles
11965 / 19495 / 2540 returned **40 mm** on all three.

What remains unverified is whether the CLAMPED map still reads right as a planet — rainfall
now describes the ground rather than the hydrology that carved it, and the rivers still
follow the ungated field.

## criteria
- no arid or volcanic tile reads the 1668 ceiling ✅ (231 moved, ceiling 596 → 365)
- the jungle corridor keeps its 271 ✅
- 🔴 **and the owner looks at the planet and does not name the rainfall as a defect** — the
  clamp is a number, and whether the world reads right is not a number

## notes
Filed by CHECK 2026-08-21, mitigated the same night on the owner's call ("targeted clamp").
The owner's other option — re-run the painter with the plume gated — is the correct fix and
is deferred behind a fresh look at the globes, because it costs the map's acceptance.
