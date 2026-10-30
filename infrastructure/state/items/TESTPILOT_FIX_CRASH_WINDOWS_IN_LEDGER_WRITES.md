# TESTPILOT_FIX_CRASH_WINDOWS_IN_LEDGER_WRITES

Blind GPT review F4, F6, F7 of src/RimMandrake/Utils/arena/testpilot.py; probes p_wake_interrupt_crash,
p_reload_crash. Evidence /mnt/d/ClaudeWork/rimmandrake/arena_testpilot/gpt_blind/ (gpt_round2.md, probes.py, probes_out.txt).

## spec
Three multi-write sequences each had a crash window that loses or misstates state:
- F4 enqueue: supersede records, the queue record and the `queued` state were three appends. Fix: ONE record.
  The queue record carries `supersedes: [cand...]` (the prior attempts that were queued at sealing); states()
  folds a baseline from the queue (every candidate `queued`, each named one `superseded`) and then the state
  records, terminal-sticky (the rule set_state already enforced on write). An unterminated queue line is not a
  record (_read), so enqueue either happened whole or not at all. Old files (with explicit state records) fold
  the same.
- F6 wake: in_flight was cleared and saved before _interrupted() ran. Fix: the interrupted marker moves to a durable
  `recovering` list in the same session write; _interrupted is idempotent per marker (keyed by the in_flight id,
  stored on its evidence and state records); the marker is removed only after it has been processed, so a
  replacement pilot that dies in wake leaves it for the next one.
- F7 reload: the session game was published only after Lane.reload returned. Fix: a `pending_reload` marker
  (decision id, target) is saved before Lane.reload and cleared in the same write that publishes the game. A wake
  that finds it cannot know what the game runs (the canary's sha check reads the session, not the game), so it
  does not adopt the session game: game=None, epoch bumped, a `reconcile` decision logged; the next decision is a
  ruled R0 reload.

## criteria
- A1 L0: selftest t_enqueue_single_record: enqueue writes exactly one line; a queue record with supersedes and no state records folds to new=queued, old=superseded; a late state record never leaves superseded (red before the fix)
- A2 L0: selftest t_wake_interrupt_crash: a replacement pilot dying inside wake's recovery leaves the marker; the next wake records exactly one invalid crash record and one requeue for the interrupted scenario (red before: 0)
- A3 L0: selftest t_reload_crash: a pilot dying after Lane.reload leaves pending_reload; the next wake logs a reconcile decision, drops the stale game, and its next act is an R0 reload of the queued target (red before: the stale game was adopted)
