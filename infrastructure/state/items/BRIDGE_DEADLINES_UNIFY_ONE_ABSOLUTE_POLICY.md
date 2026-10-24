# BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY

Source: Transient/foundry_bridge_system_review_gpt_20261010.md (N04 line 127; cold-load thresholds lines 436-440; row 9 line 786; decision 12 line 809; line 842). GPT opinion. Note the owner bridge cards of 2026-10-11 already ruled on authority questions; this item touches timing only.

## spec
GPT quotes:
- N04 "Timeout extended forever by traffic: Each event/read resets a socket timeout -> Call exceeds its intended deadline indefinitely. Fix: An absolute monotonic operation deadline independent of individual reads."
- "25 minutes: warning/investigation threshold. 45 minutes: supervisory deadline for the cold-load attempt. Neither is a kill trigger by itself."
- Decision 12: "Use one conservative deadline policy; no 25-minute automatic kill."
- Row 9: "Transport parser and absolute-deadline fault suite: Split every byte boundary, Unicode, partial timeout/EOF, event flood, malformed lengths: bounded failure; no false result or duplicate dispatch."
- N01: on partial-frame timeout "Preserve parser state, or close the connection and mark the operation indeterminate. Never restart parsing mid-frame."

Build: one versioned deadline policy module read by launcher, watchdog, runner and briefing; per-call absolute monotonic deadline; remove any automatic 25-minute kill (find with grep for 25*60 / 1500 in launcher/watchdog); "deadline exceeded" output states whether the process is alive. Add the parser fault suite.

## verify
- Selftest: an event flood that keeps arriving cannot extend a call past its deadline.
- Selftest: parser fed every split point of a valid frame yields the same result; partial timeout closes the connection or marks indeterminate.
- No code path kills the game from elapsed time alone; grep proves it.
- Deadline-exceeded message includes alive/dead.
