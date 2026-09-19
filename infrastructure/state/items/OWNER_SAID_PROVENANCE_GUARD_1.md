## spec

🔴 **THE INCIDENT.** On `2026-09-19T06:27:43Z` a FOUNDRY subagent ran a `claim`
with `--seat OWNER --owner-said "autonomous FOUNDRY work"`. Those are not the
owner's words — they are the agent describing its own situation — and the flip
put `LIQUID_SINK_DRAINAGE_1` under OWNER. Undone 2026-09-19 at `d4a10ee0a`;
`LIQUID_SINK_LEDGER_METADATA_FIX_1` is the item that caught it.

`_check_owner_said` (cli.py) validates SHAPE only: it rejects a question and
rejects bare assent ("yes", "ok"). It cannot tell whether the owner ever said
the words, so any sentence shaped like an instruction passes. The flag is both
the authorization AND the record, so a fabricated one corrupts the record in
the one field the system treats as evidence that a boundary was crossed on
purpose.

⛔ **THE OBVIOUS FIX DOES NOT WORK — MEASURED 2026-09-19, do not re-derive it.**
The ask as first stated was "refuse `--owner-said` from a subagent". A haiku
subagent was spawned and printed its own environment: it is **byte-identical to
the seated parent's** —

    sid=unset / 64259c55-366f-4fe4-b1c2-03c724c382fa     (same as parent)
    RIMFLOW_SEAT=unset  AGENT_SEAT=BENCH                 (same as parent)
    ROLEFILE=yes                                         (parent's role file)

So there is **no env var, session id or `.claude/session_roles/<sid>` signal
that distinguishes a subagent from its window.** Any guard built on that
discriminator refuses the seat itself or nothing at all.

✅ **BUILD THIS INSTEAD — provenance, not identity.** A `PreToolUse` hook on
`Bash` receives `transcript_path` (precedent: `.claude/hooks/block_paste_handoff.py`
reads it on `Stop`). When a command contains `--owner-said`, extract the quoted
string and refuse unless it appears in a genuine **user** turn of the transcript.

🔑 This is strictly better than the original ask: it catches a fabricated quote
from the seated window too, which the subagent rule never would.

⚠️ **Two things to verify before building, not after:**
1. **Does `PreToolUse` fire for a subagent's Bash call at all?** If it does not,
   the hook is the wrong layer and the check belongs in `cli.py`, which would
   then need the transcript path passed to it.
2. **A subagent's transcript contains its own PROMPT as a user turn.** A naive
   substring match would let an agent launder a quote by putting it in the brief
   it writes for its own child. Match against the SEAT WINDOW's transcript, or
   require the match in a turn the agent did not author.

## verify

- Fabricated quote refused: `--owner-said "autonomous FOUNDRY work"` with no
  such words in any user turn → refused, non-zero exit, message naming the route.
- Real quote passes: a string the owner actually typed this session → lands, and
  still stamps `ownerSaid` on the event exactly as today.
- Near-miss: owner said it in an EARLIER session, not this one → decide and
  record which way this goes; do not leave it accidental.
- The refusal message teaches the way through (every other refusal in this
  codebase does; the generic seat rule was fixed for exactly this reason).
- A selftest beside the other hook selftests, in `run_selftests.py`'s sweep.

## criteria

- A quote the owner never uttered cannot reach the `ownerSaid` field, from a
  subagent OR from a seat window.
- No legitimate owner-authorized action becomes harder: he is never refused by a
  tool rule (CHARTER, Posture).
- ⛔ Does NOT re-gate `close`/`drop`/`supersede` — those became any-seat on
  2026-09-19 and no longer route through `--owner-said` at all.
