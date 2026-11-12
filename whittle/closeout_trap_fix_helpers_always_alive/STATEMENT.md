# CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE — done statement

The fix closed 2026-11-01 at 569bc559081c (close reason: "Request always records; kill waits; drain and spawn freeze
live. 15 of 15 mutants killed.") with the promise `--live "hook=block_agent_over_slots.py"`. The deadman reopened it
2026-11-08 20:34Z: "hook block_agent_over_slots.py is not wired in ~/.claude/settings.json,
/home/mandrake/rm/dispatch/.claude/settings.json". It recovered 2026-11-09 04:19Z ("sweep: running again"). The
ledger says it OWES A GUARD: it closes only with a class guard test shown failing on the instance.

Done when:
- **The hook is wired now.** `live_line._hook("block_agent_over_slots.py", None)` returns None in this clone and the
  dispatch tree. Evidence: the `--live "hook=block_agent_over_slots.py"` check passing at close.
- **A class guard exists and is shown failing on the instance.** A selftest checks that every `hook=` promise on
  the ledger (and `live_baseline.txt`) is wired in the repo's `.claude/settings.json`, so a landing that clobbers the
  settings file (the instance: 8fb9f7f2b6, the Pyrelands squash, restored by 943a7a66da) goes red. Evidence:
  `rimflow guard CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE --test <selftest> --instance "--settings <8fb9f7f2b6 copy>"`
  recorded red, and the same test green on the real settings file.
- **The guard can see.** A sanity row: the test reads at least one hook promise from the ledger (not zero), and a
  fixture settings file missing one hook reports that hook by name.
- **Closed with evidence.** A level-tagged pass on the published sha, then `rimflow close --sha <sha> --live
  "hook=block_agent_over_slots.py"`.
