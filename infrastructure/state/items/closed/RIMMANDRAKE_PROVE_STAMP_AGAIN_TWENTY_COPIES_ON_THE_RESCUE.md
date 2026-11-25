# RIMMANDRAKE_PROVE_STAMP_AGAIN_TWENTY_COPIES_ON_THE_RESCUE

The live test of `RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST` (Bridge v2 build order,
`design/specs/2026-11-23-bridge-v2/06_build_order.md`). The pure core is built and published at `61b8a76968`:
`src/RimMandrake/Utils/scene_repeats.py`, page `design/specs/2026-11-23-bridge-v2/boundary.md` §STAMP AGAIN.

## spec

- Write `src/RimMandrake/bridgetools/prove_scene_repeats.py`. It drives one `scene_repeats.Series` on the ordered-rescue scene
  of `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER` on a stage map (`stage_map.py make <game> --kind settlement`):
  each copy staged with `s.stage(station=series.station_request(size))`, its station digest from the stage's readBack blocks
  (`scene_repeats.station_digest`), its mod digests from `scene_repeats.read_mod_digests(s)`.
- Three rows:
  1. 20 stamped copies of the rescue finish in less wall time than 3 single runs take today (print both times).
  2. A planted cross-talk between two copies (a rescuer ordered onto the other copy's station) is a `BREACH`, and both copies
     read UNRESOLVED on their ledger lines.
  3. A mod state left dirty on purpose (`jawa/mod_hooks action=prove step=dirty` on a mod with a proven digest, or the mod's own
     dirtying act) changes the reset digest and stops the repeat `RESET_DIGEST_DIFFERS`.
- Needs: the ordered-rescue scene (open ticket above) and a free game (ArchSmall by default).

## verify

Acceptance test (live): the proof's reading row is on the page, written by the run that produced it.
Outcome check: `path-has:design/specs/2026-11-23-bridge-v2/boundary.md::| `prove_scene_repeats.py` |` (red at filing, 2026-11-25:
the page has no such row).

## criteria

- The three rows ran on a named game, and their reading and evidence path are in boundary.md §LIVE READINGS.
- A row that could not run is recorded UNRUN with its command, never as passed.
