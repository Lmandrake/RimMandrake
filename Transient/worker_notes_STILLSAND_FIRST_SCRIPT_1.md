# Worker note STILLSAND_FIRST_SCRIPT_1

STATUS: in progress. Files being authored: `src/RimMandrake/Stillsand/validation.py`, `northstar_plan.py`,
`northstar_site.py`, `selftest_stillsand.py`, walk `design/validation_walks/RimMandrake/Stillsand.md`.

Facts that shaped it (all read, none guessed):
- Stillsand ships COMPOSED in `mandrake.rm.biomes` (Biomes.compose.json, wave 2): EXPECT_MODS = `mandrake.rm.biomes`,
  tier = existing `baroque_wave0` (no new tier needed; the closure carries MovingDunes, CreatureBehaviors, FlowWorks).
- Site recipe is the one PROVEN live 2026-10-01 (`Transient/LIVE_SESSION_2_2026-10-01.md`, `Transient/livesession2_20261001/regen.py`):
  `jawa/world_tile_set biome=RM_Stillsand` + `jawa/world_commit` + debug action `Actions\Regenerate Current Map`.
- Live shapes reused from those proven scripts: spawn_pawn, list_pawns includeHealth, list_things, letter_list,
  fire_incident, game_condition, pawn_use_verb cast, pawn_flight report, drain_log, the `T: Kill` debug action.

## Sections to fill
- bars / walk
- tier
- offline proof
- LIVE-RUN SHEET
- break-it proofs
- FOLLOW-UP ITEMS
