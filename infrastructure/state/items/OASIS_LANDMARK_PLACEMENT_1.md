# OASIS_LANDMARK_PLACEMENT_1 — place and name the pools

Spec: `design/Jawa/worldbuilding/biomes/weeping_stones.md` (architecture ruling at
top, §12 for loadout↔faction pairings). Vanilla `LandmarkDef Oasis` hand-placed via
the bridge on chosen `ZBiome_DesertOasis` tiles (236 MEASURED), each with a chosen
companion-mutator loadout — AncientUplink / AnimalHabitat / Stockpile / none (dead
ring) — and a hand-picked name. Never rolled.

- ⚠️ `TileMutatorDef Oasis` whitelists only Desert/ExtremeDesert — verify hand-placement
  bypasses the gate or wait on `OASIS_MUTATOR_PATCH_1`; a world_commit is required
  before anything is visible (rimworld-world-editing skill).
- Seep-oasis siting (Scald Spine/Anvil hot tiles, §2b) waits on
  `VAPOR_EMITTER_PLACEMENT_1`'s vent rules.
- Hutt palace anchors (8, `HUTT_LORDS_AND_POSTS_1`) must land on placed oases.
