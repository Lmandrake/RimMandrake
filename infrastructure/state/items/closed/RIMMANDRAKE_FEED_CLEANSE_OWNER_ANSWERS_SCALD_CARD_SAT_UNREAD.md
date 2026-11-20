# RIMMANDRAKE_FEED_CLEANSE_OWNER_ANSWERS_SCALD_CARD_SAT_UNREAD

Found 2026-11-18 while reading for `RIMMANDRAKE_REWRITE_SCALD_SEA_DESIGN_READ_IN_FULL`. Filed, not fixed.

## spec

Measured: `designer_cleanse.case_text(repo, 'TerminalBiomes')` lists the concept folder, the mod's ledger items and
the design documents that name the mod. It does not name
`design/RimMandrake/designer_codex_2026-11-09/TheScaldFloor/ANSWERS_OWNER.md`, which holds three card answers the
owner gave about the Scald's sea floor on 2026-11-10, nor the same file under `TheChillFloor/` and
`PropaneLakesShore/`. The cleanse of 2026-11-17 for Terminal Biomes was written without them: the read basis in
its `definition.md` does not cite them, and its Scald scope does not use them (no row covers the vent warning
he answered about, and nothing names the ship's cooling as what ends a stay).

27 `ANSWERS_OWNER.md` files exist under `designer_codex_2026-11-09/`. Some sit in a folder whose name is not the
name of the mod the cleanse runs on, so a search by mod name misses them.

Fix: `case_text` names every `ANSWERS_OWNER.md` that belongs to the mod, under a heading saying they are his
words and outrank the brief's defaults. That needs a mapping from mod to its rehearsal folders (for example
TerminalBiomes to TheScaldFloor, TheChillFloor and PropaneLakesShore). A rehearsal folder that no mod claims is
reported by name, never dropped.

## verify

Run from the repo root. Watched `FAIL 0/1` (exit 1) on base `29749224d1`.

```
python3 -c "import sys,os;sys.path.insert(0,'src/RimMandrake/rimflow');import designer_cleanse as d;t=d.case_text(os.getcwd(),'TerminalBiomes');ok='designer_codex_2026-11-09/TheScaldFloor/ANSWERS_OWNER.md' in t;print('PASS 1/1' if ok else 'FAIL 0/1');sys.exit(0 if ok else 1)"
```

Expected after the fix: `PASS 1/1`.

## criteria

- The command above prints `PASS 1/1`.
- For every folder under `design/RimMandrake/designer_codex_2026-11-09/` that holds an `ANSWERS_OWNER.md`, some
  mod's `case_text` names that file, or the folder is reported by name as unclaimed. The fixing run adds this as an
  offline selftest covering all 27 folders, the empty case (a mod with no answers) and a mod with several folders.
- A cleanse re-run for Terminal Biomes cites the Scald's answers in its read basis.
