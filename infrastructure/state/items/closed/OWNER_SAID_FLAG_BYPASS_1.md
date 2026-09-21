# OWNER_SAID_FLAG_BYPASS_1 — `--said` bypasses the transcript-provenance guard entirely

## what is wrong

`OWNER_SAID_PROVENANCE_GUARD_1` (closed `fce1c0f2a`, 2026-09-19) built
`.claude/hooks/block_forged_owner_said.py`, a `PreToolUse` hook that refuses a
`--owner-said "..."` quote unless it appears in a `promptSource=="typed"` user turn
of the transcript. It is well built and does exactly that job.

**It only matches the literal string `--owner-said`.** At least two other live
entry points stamp the same `ownerSaid` ledger field from a *different* flag name,
and neither is covered:

1. **`./game --said "<words>" <state>`** — exports `RIMFLOW_OWNER_SAID="<words>"`,
   then execs `src/RimMandrake/Utils/broadcast.py`, which reads that env var
   (`broadcast.py:343`) and passes it to `rimflow/cli.py game <state> --owner-said
   <words>` as an **internal `subprocess.run` call**, not a new Bash tool
   invocation. The hook never sees `--owner-said` at all — the only Bash command
   text it ever inspects is `./game --said "<words>" <state>`, which contains
   `--said`, not `--owner-said`.
2. **`src/RimMandrake/Utils/apply_blanket_ruling.py --said "<words>"`** — its own
   `argparse` flag, same "his words, VERBATIM" contract, same trust boundary,
   same non-coverage.

`rimflow`'s own `_check_owner_said` (shape-only: rejects blank/question/bare
assent) still runs in both paths, but the actual provenance check — does the
transcript show the owner typing it — never fires for either.

## why it matters

This is not hypothetical. **Caught live, 2026-09-20**, during
`PORTED_BEAST_MECHANICS_REBUILD_1`'s FOUNDRY build/verification pass: the
subagent ran `./game --said "FOUNDRY closing the beastmechanics verification
load" down` to record shutting down its own quicktest — a legitimate, in-scope
action, but the words are the AGENT's own description of its situation, not
anything the owner said. The ledger now carries:

```
{"seat":"OWNER","event":"game","state":"DOWN","ranBy":"FOUNDRY",
 "ownerSaid":"FOUNDRY closing the beastmechanics verification load",
 "ts":"2026-09-21T00:28:10Z"}
```

— an event stamped `"seat":"OWNER"` with a quote the owner never said, exactly
the failure class `OWNER_SAID_PROVENANCE_GUARD_1` exists to prevent, produced by
an agent that (per its own self-correction in the same report) knew the rule and
still used the wrong flag form because the guard let it through silently. The
agent flagged its own mistake and it is already recorded in
`infrastructure/state/LESSONS_INBOX.md`, but the ledger event itself still
carries the false attribution, and — more importantly — **the hole that let it
happen is still open** for the next agent that reaches for `./game --said`
without knowing better.

## the work

1. Broaden `block_forged_owner_said.py`'s `FLAG` regex from matching only
   `--owner-said` to matching **both** `--owner-said` and a bare `--said`
   (`r'--(?:owner-)?said(?:=|\s+)...'`). Confirm `--owner-said` never
   double-matches as a bare `--said` (it doesn't — `"--owner-said"` has no
   `--said` substring; the `-` before `said` there is single, not double).
2. Update `offence()`'s cheap pre-check (currently `if "--owner-said" not in
   command: return None`) to use `FLAG.search(command)` directly instead of a
   substring test, so it isn't hostage to which literal string is checked.
3. Update the docstring and the refusal message to name both flags and both
   real call sites (`./game --said`, `apply_blanket_ruling.py --said`), so the
   next reader doesn't have to re-derive that this covers more than
   `rimflow ... --owner-said`.
4. Add selftest cases to `selftest_block_forged_owner_said.py` exercising a
   `./game --said "<fabricated>" down` -shaped command and an
   `apply_blanket_ruling.py ... --said "<fabricated>"` -shaped command, both
   DENY when unprovable and ALLOW when the quote was genuinely typed this
   session — mirroring the existing `--owner-said` cases.
5. Confirm the selftest is (or gets added to) `run_selftests.py`'s hook-selftest
   sweep, per `OWNER_SAID_PROVENANCE_GUARD_1`'s own verify bullet.

## watch out

- `apply_blanket_ruling.py --said` takes its own required argparse value; it
  does not export an env var or shell out the way `./game` does. The regex-level
  fix on the Bash-command text covers it identically either way, since the hook
  only ever inspects the literal Bash tool-call text.
- Do not weaken the existing `--owner-said` behavior or its selftest cases —
  this is additive coverage, not a rewrite.
- The false ledger event above (`ts: 2026-09-21T00:28:10Z`,
  `PORTED_BEAST_MECHANICS_REBUILD_1`) is **not** edited or removed by this item
  — `events.jsonl` is append-only provenance. If a correction is wanted, it is a
  new `note` event pointing at the bad one, not a rewrite of history.

## verify

- `./game --said "something an agent invented" down` (run manually in a shell
  with the hook active, or via the selftest's subprocess harness) is DENIED
  with a message naming the route.
- A genuinely owner-typed sentence, passed the same way, is ALLOWED.
- `python3 .claude/hooks/selftest_block_forged_owner_said.py` passes clean,
  including the new `--said` cases.
- `python3 src/RimMandrake/Utils/run_selftests.py` passes clean.

## criteria

A fabricated quote cannot reach the `ownerSaid` ledger field through `--said`
(via `./game` or `apply_blanket_ruling.py`) any more than it can through
`--owner-said` — same guarantee, same guard, both flags.
