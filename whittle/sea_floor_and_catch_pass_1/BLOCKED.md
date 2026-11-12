# BLOCKED: SEA_FLOOR_AND_CATCH_PASS_1 (CLAUDE_STEVEDESKTOP_OFFLINE4), 2026-11-11 22:40 -0800

What's left needs a live game, which this offline lane can't run. It doesn't need the owner. All three judges gave the same verdict: the defs are authored and consistent, and the item's own criteria (fly down, meet the animals, fish the shore) were never observed.

This round (published d181c2ca93):
- I closed the two offline gaps the judge named. per_sea.py now re-runs with no argument and reproduces the verdict.
- The three sea fuzz selftests now PASS on this seat. They used to crash on the absent /mnt/d/Luke/dev cwd. That was fixed centrally in winbuild, which unblocks 77 fuzz tests.

What unblocks it, for a live lane (needs=bridge is already set on the ledger):
1. PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE (built 8fe73e4f, awaiting its L2 game run). It unblocks SEABED_DESCENT_ASCENT_1's proof.
2. Then, per sea:
   - Fly down and read Find.CurrentMap.Tile.Layer and the floor biome.
   - Census the floor map's pawns against evidence/per_sea_verdict.txt.
   - Fish one catch on an RM_SeaCoast land tile beside the sea.
   - Load a pre-wiring save and look for the "Seabed floor re-derived" log line.
