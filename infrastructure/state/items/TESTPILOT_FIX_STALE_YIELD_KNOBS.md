# TESTPILOT_FIX_STALE_YIELD_KNOBS

Filed (OWNER): owner-presence remnants after the strip (no behaviour): `testpilot_reload_rule.json` still carries
`yield_bound_steps`/`yield_bound_s`; `design/RimMandrake/testpilot_merged_2026-10-29.md` M4 bullet "When he returns,
the pilot stops safely" and O4 row "safe yield" contradict the 2026-10-30 ruling (presence is not an event).

## verify
- L0: no `yield_bound_*` key in the rule file and nothing reads one; the M4 bullet and O4 row deleted (not
  superseded) with inbound references fixed; testpilot selftests still green.
- Stopping point: finish.

## criteria
- A1 L0: yield knobs and the contradicting design prose gone; selftests green
