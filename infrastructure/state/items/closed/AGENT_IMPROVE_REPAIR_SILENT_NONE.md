# AGENT_IMPROVE_REPAIR_SILENT_NONE

On the 2026-11-01 hand run (`D:\ClaudeWork\rimmandrake\agent_improve\2026-11-01\`), three of six Curator replies were
`decision: none` with an empty `why_text`: operations, instrument_traps.md and git-efficiency. The last two took 5-6 s.
- Nothing can tell a judged "no change worth making" from a skim.
- git-efficiency's one piece (a local `git clone` hardlinks objects, so chmod on the clone changes the source repo) is a
  plausible proposal.

Fix in `src/RimMandrake/Utils/agent_improve.py`:
- the Curator prompt requires a one-line reason for every decision;
- a `none` without one is recorded as `decision: error` ("no reason given");
- the reason is copied into the pass row and packet.md.
## criteria
A selftest row: a stub Curator replying none with no reason gives error; with a reason, the row carries it.
