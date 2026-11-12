# NOTES (newest first)

## 2026-11-11 20:25 -0800 — SETUP (CLAUDE_STEVEDESKTOP_FWLIVE)
- Ledger: 0 runs recorded on this item; nonpass tail 0 -> mode whittle. Built sha e9c39356b256 (C# + SelfTest c8aa320ce5);
  A1 L0 claimed at build. Only A2 L2 (the live script) is owed. `close` needs a level-tagged pass recorded on the BUILT sha
  (e9c39356b256): `rimflow verify ... --sha e9c39356b256 --level L2` (current main contains it; check `rimflow verify --help`).
- Past live attempts were filed on sibling items (read them: `rimflow show <ID>`):
  - `DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL` (run 1, 2026-10-23): no colonist took the dig in 6000 ticks -> HARNESS; the script
    now asks `flowworks_job_probe` and ORDERS the job (`job_gate`). DS_map_has_deep_stone was already PASS (Marble, fallback).
  - `DEEP_STONE_FIX_PROBE_NEVER_NAMES_PAWN` (driver 4): probe got `pawn=` not `pawnId=` -> HARNESS, fixed b06770af55.
  - Driver 5 rerun s5 (2026-10-24, `D:\ClaudeWork\rimmandrake\scratch\bridge_run_1f\deep_stone_s5.json`): job accepted and
    running, but depth stayed 3 over 6000 ticks; fresh map had 7 Filth_Blood + 7 RM_ChokingSpores near the colonist -> SITE.
    Owed: rerun on a spore-free tile / clean site. This is the first thing to look at: why did a running RM_DigCanalJob not
    finish the cut (pawn downed/fleeing from spores? work amount? shovel staging `shovel_stage.py`, SHOVELS_BUILD commit bf978b98da
    made digging need a shovel).
  - `DEEP_STONE_PROOF_FIX_RERUN_LETTER_FAILS` (proposed): a second run on the SAME map fails the letter check (first find
    fires once per def per map). Always use `--fresh-map`.
- Classify every finding MOD, SITE or HARNESS (skill `live-debugging-proof-harness`). A HARNESS fault is fixed in the script.
- Game: SteveDesktop game A only, via `infrastructure/whittle_claude/steve.sh` (sync/deploy/up/run/fetch). Previous round's
  note: the Steve guard lock of a dead holder refused release --force; ledger bridge read FREE; re-check `rimflow bridge who
  --host stevedesktop`.
