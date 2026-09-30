# GRAVSHIP_ACOUSTIC_SCANNER_1 — the ship listens to the ground, in every biome

This started as GPT's "Belly Sounder" in the Cracked Lands enrichment consult (2026-09-30). The owner
picked it by question card and typed:

> "I like the belly sounder immensely and it should do something in every biome actually. Acoustic
> scanner."

Tier: RimMandrake (a gravship system every biome can use). **Model: opus**: a new cross-biome system
with a per-biome payload design and no test to catch a wrong design.

## spec

- A ship-mounted **acoustic scanner**. When the grounded gravship fires a sounding pulse, dust jumps
  from nearby walls and a bass vibration travels through the hull. It shows **broad probability bands**
  on a temporary overlay, never exact cells.
- **What it finds depends on the biome.** Each biome supplies its own payload through a def extension
  on the BiomeDef, so adding a biome is XML. The first payloads to author:
  - **Cracked Lands**: hidden water, fossil strata and suspiciously regular pans (sleeping giants).
    GPT's original, and it ties to the ruled survey-and-cistern loop.
  - **Stillsand**: things moving or buried under the sand, such as swimmers, caches and caves.
    Coordinate with the Stillsand sitting's Listening and sand-swim kit.
  - **Others**: each biome's sitting or enrichment names its own. A biome with no payload yet gives a
    plain "nothing unusual" reading.
- It is unlocked by a first field survey or a research step (discoverable technology), not given free.
- It is **not** a ship-mounted chime and **not** a wax tank; both were rejected at the Cracked Lands
  sitting.
- It ships with Mod Settings.

## criteria

- It works from a landed gravship on a Cracked Lands map and a Stillsand map.
- The per-biome payload is pure XML.
- The reading is always banded, never exact.
