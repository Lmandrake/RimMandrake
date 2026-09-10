# CODEX_UAC_STORM_1 — ~30 UAC prompts from calibration's fresh codex homes

## Root cause (CONFIRMED 2026-09-09, log evidence)

Codex's Windows build auto-updated 0.153.1 → 0.153.4 on 2026-09-08 (between
19:18 and 20:51 local, visible in `.sandbox/sandbox.2026-09-09.log`: new bin
hash `8e5b6932251c2c1c`, then `sandbox setup required: sandbox users missing
or incompatible with marker version` → `ensuring sandbox users` — the
operation that creates two Windows local accounts + firewall rules and needs
Administrator consent). The `.codex_sandbox_seed` template was captured
2026-09-07 against 0.153.1, and `seed_sandbox_from_template()` validated a
template purely by `setup_marker.json` EXISTING — no version check — so every
fresh calibration worker home carried incompatible sandbox artifacts and
independently triggered elevated re-setup on first use. 13+ homes ≈ the ~30
prompts. The "seeding path skipped" hypothesis is ruled out: seeding ran
correctly every time; it copied a doomed template.

## Fix (landed)

1. **Seed recaptured** same night from the shared home's current (post-update,
   already-elevated) `.sandbox*` dirs — pure file copy, no UAC. Stale template
   kept beside it as `.codex_sandbox_seed.stale-0.153.1-*`.
2. **Version-aware seeding** (`skills/generating-images/scripts/codex_image.py`,
   commit `31a92df6`): fingerprint = newest `codex-command-runner-*.exe` by
   parsed version (never mtime — recaptures give identical mtimes); template
   vs installed mismatch refuses LOUDLY with the recapture command; unknown
   (no `.sandbox-bin`) is treated as mismatch; the old false-confidence
   "no UAC prompt expected" line prints only after the check passes.
3. **Daemon preflight** (`artpipe/common.py::codex_sandbox_preflight`,
   `artpiped.py` startup + admission gating): on mismatch the codex channel is
   disabled for the run — workers never each discover the incompatibility
   live — while the gemini channel proceeds.
4. Selftests: `selftest_codex_image.py` 81/81 (+4 new),
   `selftest_artpipe.py` 340/340 (+3 preflight tests, sandbox fixtures
   isolated from the real /mnt/c homes), full `run_selftests.py` 47/47.

## Deferred, deliberately

**Live zero-UAC confirmation** (one fresh worker home, first `codex exec`,
zero prompts) needs an attended session — a queued elevation dialog with
nobody to click it is this item's own failure mode. It gates
`ART_PIPELINE_DAEMON_1`'s first attended codex-channel run; the fingerprints
match today, so the preflight passes and the storm cannot recur silently
either way.
