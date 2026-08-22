## spec
CHECK.md gave CHECK the duty of stamping `game.json` while `rimflow game`
refused every seat but OWNER, so the seat told to record the state had no way
to record it — and `rimflow game` took no `--note`, so the prose the old
`game.json` carried (what the load is for, where the blocker is) had nowhere
to go.

## verify
```
python3 src/RimMandrake/rimflow/cli.py game --help     # --owner-said and --note both listed
./game                                                 # measures the process from any seat
```

## criteria
1. A seat other than OWNER can record a state change the owner announced,
   without a permission fight, and the authorization is on the event.
2. A state change can carry one line of prose.
3. `infrastructure/agents/CHECK.md` no longer reads as contradicting the tool.

## notes
Closed 2026-08-22 by BUILD. All three met.
1. Resolved in the tool's favour by the OWNER, not by code: `rimflow game`
   still refuses a seat that INFERS the state — that is the rule's whole point
   — but admits a seat QUOTING him via `--owner-said`, and `./game` with no
   argument MEASURES the running process and corrects the record from any seat.
   Measuring is not inferring (owner, 2026-08-22).
2. `--note` is built and shipped; optional on purpose.
3. CHECK.md now says he keeps the state true rather than originates it, and
   names both routes at the point of the duty.
CHECK does NOT lose the duty. What he cannot do is originate the state.
