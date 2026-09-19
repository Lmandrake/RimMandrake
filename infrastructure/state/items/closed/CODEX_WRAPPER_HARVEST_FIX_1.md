# CODEX_WRAPPER_HARVEST_FIX_1 — the image wrapper discards finished images on timeout

Found 2026-09-06 during the transparency test (`design/RimMandrake/codex_receiving_agent_design.md`,
addendum). MEASURED: a generation succeeded at 62 s; the wrapper's 180 s ceiling expired
during Codex's wrap-up turn; `codex_image.py`'s `run_codex()` raises on `TimeoutExpired`
so `harvest_new()` never runs — a finished PNG in `$CODEX_HOME/generated_images/` is
reported as "no image produced".

## spec
1. `run_codex()`: on timeout, ALWAYS attempt `harvest_new()` before raising; a harvested
   image is a success, not a timeout.
2. Raise or remove the 180 s ceiling for the wrap-up turn; consider
   `model_reasoning_effort` lower than `xhigh` for the image turn (config.toml currently
   sets xhigh — the trivial copy-and-report turn reasons at xhigh, the probable long tail).
3. **Recover the orphans**: `TREE_GRAPHICS_OWNERSHIP_1` logged ~14 "timeouts" — check
   `generated_images/` for PNGs at those timestamps; they are very likely finished work.
4. **Native transparency is real** (MEASURED: 1448x1086 RGBA, alpha-0 55.7%, corners
   (0,0,0,0), mid-alpha 0.28%, no fringe/halo — better than chroma-key): retire
   `chroma_key.py`, the `TRANSPARENT_CLAUSE` in `build_prompt()`, and `rembg_cut.py`
   inside `make_sprite.py`. KEEP `conform_sprite.py` (the tool ignores requested size)
   and the fringe check. Update `generating-images` / `generating-rimworld-sprites`
   skills' contract accordingly (skills are edited only in a fresh-context curation
   pass — file the lesson in LESSONS_INBOX and leave the skill text to that pass).
5. Reference image for the claim: `Transient/transparency_test/crate_check.png`.

## verify
A deliberately slow generation harvests correctly past the old ceiling; the orphan sweep
reports N recovered; a sprite passes `validate_sprite.py` with no chroma-key stage run.

## done 2026-09-06 — code landed, one live check still owed

1. ✅ `run_codex()` returns `(rc, output, timed_out)` and never raises on timeout;
   `do_image()` harvests on EVERY path, plus a 20 s grace poll for the file that lands
   after our own kill (the sea-beast "LATE" case). A harvested image exits 0.
2. ✅ Ceiling: the wrapper's own default was already 900 s — the 180 s came from callers.
   `gen_sea_facings.py` 210→600 s. New `--reasoning-effort`, **default `low`**, sends
   `-c model_reasoning_effort="low"` so the trivial copy-and-report turn stops reasoning
   at `xhigh` after the PNG already exists. `low` is legal for `gpt-5.6-sol` — read from
   `$CODEX_HOME/models_cache.json`, not guessed.
3. ✅ **14 orphans recovered** (not ~14 — exactly 14, across 10 sessions whose rollout
   JSONL carries the verbatim sweetline prompt) to
   `src/RimUtinni/AshkarrFlora/_artsrc/sweetline_orphans_2026-09-06/`, with a manifest and
   a contact sheet. All 14 re-read after copying: valid IHDR, intact IEND, byte-identical.
   ⚠️ `RUT_SweetlineTreeA.png` is still EMPTY on purpose — picking 1 of 14 and its 768x768
   registration is an art call, and `conform_sprite.py` has no reference sprite for that def.
   7 of the 14 carry native alpha, which corroborates §4 across seven generations.
4. ⚠️ Partly. The chroma-key WORKFLOW is retired — `--chroma-key` and `TRANSPARENT_CLAUSE`
   deleted, the cutout stage gone from `make_sprite.py`, the three batch drivers now ask for
   alpha in their own prompts. **`chroma_key.py` was NOT deleted**: it has two live callers
   that read green raws already on disk (`build_sea_facings.py`,
   `recrop_east_v2.py`), plus the 7 green orphans. It carries a RETIRED banner naming them.
   `rembg_cut.py` likewise kept — `gemini_image.py` has no native alpha. `conform_sprite.py`
   and the fringe check untouched. Lesson filed in `LESSONS_INBOX.md`; SKILL.md text left
   for the curation pass, as this item instructs.
5. ➕ Per-worker isolation: `--codex-home DIR` (auto-seeded from the shared home);
   `gen_sea_facings.py`'s 3 workers each take one. ⚠️ MEASURED: a WSL process does not pass
   a bare env var to a Windows child — `CODEX_HOME` must also be named in `WSLENV` or it
   arrives empty, which would have made the wrapper harvest a different directory than the
   one codex wrote to.

`skills/generating-images/scripts/selftest_codex_image.py` — 30 checks, all against stubs,
zero quota. 🔴 **Still owed: one authorized live generation.** Nothing here was proved
against a real `codex exec` image turn, so the `low` effort default and the
ask-for-alpha-in-the-prompt drivers are untested in anger. `TREE_GRAPHICS_OWNERSHIP_1`
Owed §1 still quotes `--chroma-key '#00ff00' --timeout 105`; that command is stale.
