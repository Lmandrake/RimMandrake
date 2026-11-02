# RW - Planet Atmosphere: what it costs (PLANET_ATMOSPHERE_CLOUD_COST_1)

Owner card C18: *"Measure real memory cost first"*. Instrument: `src/RimMandrake/Utils/planet_atmosphere_cost.py`
(selftest `selftest_planet_atmosphere_cost.py`).

## Offline (INFERRED from the loader rule, 2026-11-02)

RimWorld 1.6 loads every PNG under a mod's `Textures/`, decodes it to RGBA32 with mipmaps, and, with
`textureCompression` on (it is, in Prefs.xml) and both sides divisible by 4, compresses it to DXT5 at
1 byte per pixel. The rule comes from the decompile of `Verse.ModContentLoader.LoadTextureViaImageConversion`.
The mod loads 5 textures:

| texture | size | resident | transient decode |
|---|---|---|---|
| `EarthCloudTex/8k_earth_clouds.png` | 8192×4096 DXT5 | 42.7 MB | 170.7 MB |
| `Effect/sunFlare.png` | 5000×5000 DXT5, 2 mips | 29.8 MB | 127.2 MB |
| rings and water (3) | small | 1.6 MB | — |
| **total** | | **≈74 MB VRAM** | |

The mod audit (`records/batch_14.md`) says "1131.6 MB est decoded". It counted 19 PNGs at 4 bytes per pixel,
including the art under `src/`, which the game never loads. Its own label for the figure was "not a measurement".
Not counted above: the mod's render targets. Its LUTs are 256² ×3 plus a 128·32·8·32 scatter table, and
the world view needs full-screen ARGBFloat temporaries (16 bytes per pixel, about 59 MB each at 2560×1440).
These cost memory only while the planet is drawn. `renderingSizeFactor` is 1, so there is no extra camera
target.

## Live A/B (owed)

`record --require with|without` samples a running launch. `verdict` prints the deltas. The clauses are in
`infrastructure/state/live_proofs/PLANET_ATMOSPHERE_CLOUD_COST_1.{txt,criteria}`.
