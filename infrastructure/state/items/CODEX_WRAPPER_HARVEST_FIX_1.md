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
