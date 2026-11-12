# BLOCKED: SEA_FLOOR_AND_CATCH_PASS_1 (CLAUDE_STEVEDESKTOP_OFFLINE4), 2026-11-11 21:54 -0800

The live step blocks this, not an owner question. Everything that can be shown offline is built, published (f74549e3d7, then 94759b90a5) and shown in `whittle/sea_floor_and_catch_pass_1/evidence/`. The statement's remaining half is the item's own criteria: "Flying the gravship down to a sea's floor shows you the animals…, and fishing its shore pulls out the same creatures". Only a running game can show that, and this offline lane drives none.

What unblocks it:
- **PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE.** The descent proof lays a VGE pipe on a game without VGE, and that blocks SEABED_DESCENT_ASCENT_1's live proof.
- Then a live lane, per sea:
  1. Fly down and read `Find.CurrentMap.Tile.Layer` and the floor biome.
  2. Count the floor map's animals by kind against `evidence/per_sea_verdict.txt`.
  3. Fish one catch on a coast beside the sea.
  4. Look for the "Seabed floor re-derived" log line when loading a save whose floor was mirrored before the per-sea wiring.

On the ledger: needs=bridge is set, and a rimflow note carries the NEXT step.
