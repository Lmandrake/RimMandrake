# Judge: LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT

Judge: fresh-eyes subagent on claude-offline3, 2026-11-11. Read STATEMENT.md, NOTES.md, the item file's spec/criteria and
evidence/. Did not read DONE.md or BROADEN.md. I re-ran `replay --enforce`, `selftest_relentless_needs.py` (118 ok, 0
fails) and both `baseline` windows at HEAD 35f19251ee. My output matched the evidence files exactly.

## Line 1: Replay, at least 17 of 20 R1/R2 items get the right mod added before repair, zero wrong additions. TRUE

- My re-run prints `ENFORCE R1/R2 items right 17/20 (bar 17)  wrong additions 0 ... -> OK`, exit 0. This matches
  `evidence/replay_enforce.txt`.
- The answer key is independent of this build. The fixture's `cases` (the expected "added" mods) are identical to their
  state at 26d038280b (2026-11-05, the earlier item). This item's commit e306ca56e9 changed only the `passes` side.
- Caveat for honesty, though not one that fails the line: it passes at exactly the bar. Three misses are named:
  ART_OVERRIDE_FAMILY_SCRIPT_1 (sarg.alphamemes, vanillaexpanded.vgeneticse), TITANIC_BODYSIZE_TEST_RACE_1
  (neku.largepawns) and WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR (MenuShell). There is no margin.

## Line 2: Negative control, zero additions on the last 50 PASS proofs after the migration's live-without lines. FALSE

- The tool's own line says `gate additions 50`. The criterion says zero additions, and the gate makes 50 on those 50
  PASS proofs.
- The evidence reinterprets "addition" as "an addition the run passed without" (`negative_control_unrecorded.md`).
  Even on that reading, the line is not shown:
  - 24 were held per a recorded live list.
  - 14 were argued held from the scripts.
  - 12 remain "cannot tell" by the builder's own count: 11 transitive About.xml closures plus 1 HORRORS_RAIDING_FACTION_1
    run (11-03 23:32) that could pass without AshkarrWeatherSuite.
- The reinterpretation is reasonable engineering (adding a mod the run already loaded is a no-op). But it is a changed
  criterion, and it needs the owner's or Conductor's acceptance, not the builder's.
- "After the migration's live-without lines": the migration (`migrate.txt`: 215 proofs, 110 additions, 0 conflicts)
  added no live-without lines. Only one proof in `infrastructure/state/live_proofs/` carries `live-without:`
  (STILLSAND_RETURN_REMAINDER_1). So that half of the line has nothing to judge, which is acceptable.
- What would settle it: either the owner accepts "zero additions the run did without" as the bar, or there are PASS runs
  whose `env.running` load was recorded (the new row field), replayed with 0 unheld additions.

## Line 3: One week after landing, mod-list-cause failures in runs.jsonl against a baseline recounted first. CANNOT TELL (counts as not shown)

- The baseline was recounted first, and my re-run matches it: 7 days before d7f3a0699d hold 141 mod-list rows, 126 held,
  15 ran, 26 games, 33 items. The data starts at 2026-11-02, so it is really about 4 days.
- The "week after" holds 22 hours: the first row is 2026-11-06T04:28, the last 2026-11-07T02:26. The Relentless units on
  Archmagi are disabled (`criterion3_relentless_state.txt`: 0 active units, and runs.jsonl's mtime is 11-06 18:26).
  The week has not been observed.
- The landing it is counted against (d7f3a0699d) is not the code being judged. Later commits, e306ca56e9 and
  35f19251ee (today), changed the gate's live-without and closure behaviour, so no run has used HEAD's gate.
- What the 22 h show is mixed:
  - Good: modlist_ran fell from 15 to 0, so no game started on a short list.
  - Not yet better: 78 mod-list rows were still held and modlist_games was 12 in about a day. The before-window had 26
    in about 4 days, so the per-day rate of games touched is not visibly lower.
- What would settle it: re-enable Relentless with HEAD's gate, then run `baseline` over 7 full days from that restart,
  set against the recounted window above.

## Staging and flattering notes

- Line 1 sits exactly on its bar.
- Line 2's headline "-> OK" and "did WITHOUT 0" read cleaner than the 12 untold additions behind them.
- Line 3's post window is short and comes from a pipeline that was then switched off. It measures an earlier gate.
- The selftests are the builder's own (118 ok). They show the mechanisms work as specified, not the outcome criteria.

would show: no
