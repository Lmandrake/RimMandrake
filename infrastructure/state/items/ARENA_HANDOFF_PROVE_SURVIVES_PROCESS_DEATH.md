# ARENA_HANDOFF_PROVE_SURVIVES_PROCESS_DEATH

Follow-up from the blind review (GPT, round 1) of ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE.
The model `src/RimMandrake/arena/models/LiveHandoff.tla` (runner `check_models.py`) proves the
fixed goodbye/pilot/arena handoff only for game crashes; the reviewer's High finding is that the
CONTEXTS and the DISPATCHER never die on their own.

Not yet modelled (add as environment actions, rerun `check_models.py`):

- the old window dies by itself between Goodbye and KillOk (the real `restart_kill` then finds no
  process, and the relaunch path refuses when `proc_start` returns None: is anything after the
  cursor ever read?);
- the dispatcher dies after WriteRecord, before or after the final fence (record recovery: an
  aborted-record marker, restart generation, which record a restarted dispatcher picks);
- the fresh window dies after consuming its one-time wake token but before delivering the read
  messages (Relaunch is atomic in the model today).

Also from the same review, documented as assumptions A4-A6 in the spec header rather than modelled:
the candidate queue is durable by construction, a handoff starts only at a test boundary, and the
fence models only the input gate (the owner-idle and window-status gates only refuse a kill).

Done when: each of the three deaths is an action, and either the fixed protocol still passes S5
(with a new liveness property that every sent message is eventually handled or read) or TLC shows
the real gap, which is then filed against seat_restart.py.

Review text: D:\ClaudeWork\rimmandrake\build\tla\review1.md
