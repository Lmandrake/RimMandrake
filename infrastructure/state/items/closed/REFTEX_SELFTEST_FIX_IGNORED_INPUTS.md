# REFTEX_SELFTEST_FIX_IGNORED_INPUTS

`src/RimMandrake/Utils/art/selftest_reference_textures.py` is RED in the bench clone (107 failing rows) and GREEN in
a clean `git archive` of the same commit (71 rows pass). Checked 2026-10-26 in the ART_MARKS review: the parent
of e4aaf37692 fails identically once given bench's gitignored `Transient/biome_ffar/*.subjects.json` (95 present,
6 tracked; ignored by Transient/.gitignore). So it is pre-existing and environment-dependent, not caused by
ART_MARKS. Failing sheets: art_eval_shadow_br1e x3, bridge_art_redraw (58), drawbridge (32), xeno_heads (8).
Likely the local ignored subjects files are stale (FOUNDRY fixed the generators under
REFTEX_SELFTEST_DIAGNOSE_BRIDGE_SHEET_RED, closed 052d4e8d05).

Fix: the selftest must read only tracked inputs (or regenerate the subjects it reads), so one commit gives one
verdict on every clone; then refresh or delete the stale local files.
Evidence: /mnt/d/ClaudeWork/rimmandrake/review_delegation_builds/st_reftex_*.txt
