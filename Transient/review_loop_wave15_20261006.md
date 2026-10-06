# Review loop wave 15 (2026-10-06), FOUNDRY, offline
Selftests: selftest_frozen_dumps.py 34/34 (refresh); palette.py loads/--check run; others py_compile only (no selftest exists).
- Utils/refresh.py: CLEAN, marked. Reachable: CLAUDE.md, gen_armour_patch/gen_megafauna_yield import D_DUMP. Nit: freeze() docstring says "sorted" mods, code hashes in manifest order.
- Utils/cherrypicker.py: CLEAN, marked. Reachable: imported by palette.py + sheet builders. Nit: load() returns an empty Cuts if the settings file exists but has zero keys.
- Utils/palette.py: FIXED, left DIRTY. check() let cherrypicker.load()'s IOError escape as a traceback instead of the UNMEASURED line used for the missing dump. Nit: importing it replaces sys.stdout globally.
- Utils/stage_review.py: FIXED, left DIRTY. daylight()/settle_weather() swallowed step_game_ticks errors (scene never advanced, still "ok"); now warn on stderr. main() always exit 0; now 1 when keeper save is not verified.
- Utils/print_gravship.py: FIXED, left DIRTY. Crashed TypeError on a layout with no gravEngine (engine print line unguarded) and ValueError on an empty layout; --apply exited 0 despite failedVerify>0 / commit failure; now exits 1. Unfixed: --strip-whole-map hardcodes 250x250.
- Utils/shared_sync.py: DEAD candidate. 14-line RETIRED stub, exits 1; only docs cite it. Not marked, not deleted.
