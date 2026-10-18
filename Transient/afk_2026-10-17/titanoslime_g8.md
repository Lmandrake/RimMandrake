# TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID — gate g8 live run 2026-10-17 (BENCH)

## Status
- [x] game closed (Stop-Process), biomes composed + deployed (2 files: GelatinousSlime DLL + .srchash)
- [x] relaunched via Steam on the 22-mod list (incl. neku.largepawns, mandrake.rm.hugethings), quicktest maps
- [x] g8: 6/6 PASS — ghosts=0 before/after vanish, Muffalo respawn 9/9 each case
- [x] gates 1-6 + g8 with vanish cleanup: 33/33 PASS (titanoslime_g8_final_run.log)
- [x] script switched back to vanish; item closed

## Harness defects found (HARNESS, fixed in titanoslime_gates.py)
- g3 absorb arm leaked three manhunter slimes -> 100+ "Resolved path returned no nodes" lines in later log budgets.
- g3 mass bar assumed an adult victim; a random Colonist is sometimes a HumanlikeTeenager (BodySize 0.8), 4/11 runs.
  A 20-colonist probe that read all 1.0 briefly made this look false.
- Vanish/kill replies were never read; G.gone() now checks destroyedAfter (2 expected misses: colonists still held).
