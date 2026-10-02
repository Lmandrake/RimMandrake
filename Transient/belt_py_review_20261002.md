# belt py review 20261002

## Marked CLEAN (full-file review, no findings)
- src/RimMandrake/Utils/system_screenshot.py
- src/RimMandrake/Utils/reload_check.py (hand-run tool; docs reference only)
- src/RimMandrake/Utils/artpipe/mock_codex_worker.py (selftest_artpipe passes)
- src/RimMandrake/Utils/probe_png_wellformed.py

## Edited (NOT marked clean; needs commit then mark-clean)
- src/RimMandrake/Utils/whats_new.py: f-string with a backslash inside the expression (SyntaxError on Python <3.12) hoisted into a variable. Compiles; --no-mark run OK.

## Dead candidates (only closed-item/dashboard/handoff references; not reviewed, not deleted)
- worldmap_prefill.py: FROZEN 2026-08-16, refuses to run without an overwrite flag; would clobber owner decisions.
- rimbench/gl_schema_census.py: one-shot generator of a committed reference doc (latent min([]) crash on empty FloatRange, mixed None/str sort).
- extract_mlie_sounds.py, gen_pawn_flavor_register.py, gen_pawn_flavor_phase2_register.py, planet_portrait.py, ashkarr_place_complex_structures.py: referenced only by closed items/handoffs/health dashboard.
