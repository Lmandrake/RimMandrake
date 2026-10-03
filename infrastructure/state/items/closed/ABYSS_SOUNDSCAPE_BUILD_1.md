# ABYSS_SOUNDSCAPE_BUILD_1 — the gust soundscape and the Dark that swallows sound

Biome: the Abyss. Review: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §11.2 mark 7, ruled §12. Rides `ABYSS_DARK_BUILD_1` and `ABYSS_GHARREK_BUILD_1` (gust signal). Existing neighbour: `RM_MapComponent_ProximitySoundscape` (CreatureBehaviors).

## spec

Decision taken by question card (turn 3, 2026-10-01): BOTH halves.
1. **Gust soundscape**: silence by default, each gust an impact; gill-fans rustle, grain ticks, dying lamps clatter.
2. **The Dark swallows sound**: muffled inside the Dark, sharp in a warm pocket. The muffling filter is UNPROVEN, so this half is gated by a feasibility spike (can per-area muffling be done in 1.6 audio without a global filter). Do the spike first; if it fails, report and ship half 1 alone.

## criteria

- Half 1 built with Mod Settings toggle.
- Spike result recorded (works / does not) before any half-2 build.

## verify

Offline build; sound is judged with the owner present.
