## spec
The owner's scope was **every large scanned artifact**, and the refusal layer (E)
honours it — `Player.log`, the world CSVs, `.rws` and `.dll` are all classified in
`measure/artifacts.py` and a blind scan of any of them is refused with the right
instrument named.

⚠️ **But the FORMAT layer (C) only ever covered the def dump.** For the `.rws` and
third-party DLLs that is permanent and correct — we do not own those formats, and
the ruling says D+E only there. **For `Player.log` and the world CSVs it is simply
not built**, and the gap was not called out clearly when the item closed.

What is missing:
  `Player.log`   — `harvest_log.py` exists and is allowlisted, but it is not a
                   Measurement: it does not answer "how many DISTINCT errors" as
                   MEASURED/UNMEASURED. The registry's own rule — *a `grep -c`
                   counts LINES, and one error spanning 30 lines is not 30
                   errors* — has no instrument enforcing it.
  world CSVs     — `measure/cli.py csv --where col=value` exists and excludes the
                   header, but there is no coverage/provenance notion: nothing
                   says which world revision a count is a count OF, which is the
                   same class of gap the dump had before `provenance`.

⛔ Do NOT put either behind SQLite reflexively. The dump earned it at 646 MB;
a 1.7 MB CSV does not. The deliverable is a Measurement, not a database.

## verify
`measure count-errors <Player.log>` returns distinct error COUNT as MEASURED
with a stack-trace-aware grouping, validated against a log whose error count was
established by hand. `measure csv` answers carry the world fingerprint. Both
demonstrated against a known answer, per the rule the whole item rests on.

## criteria
no question about Player.log or a world CSV can be answered with a plausible
wrong number, and every answer says which artifact revision it is about.

## notes
Filed by BUILD 2026-08-21 from three audits run after the owner asked
whether the new instrument was actually adopted. It was not.
