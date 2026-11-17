## spec
An account switch or a hard stop of the fleet never loses a detached run's work or leaves it dead.

Forensics: /mnt/d/ClaudeWork/rimmandrake/conductor/mass_kill_20261117_0335.md (D:\ClaudeWork\rimmandrake\conductor\mass_kill_20261117_0335.md).
At 03:35 PST 2026-11-17 the switching plan's hard stop SIGTERMed every Claude process; the Fable run
rm-detached-bench-rimmandrake-lay-slack-close-fittings-twe-1794902099 died with exit 143 after 3 h 40 min and stayed
dead until a hand relaunch at 05:57. Switches at 05:46, 05:54 and 05:58 killed more.

Priority (Conductor brief, 2026-11-17 08:03):
1. After any fleet stop caused by a switch (the plan's or a manual `claude-account use`), every detached run that was
   alive and died with the stop is resumed on the new account by itself: the same session where its transcript is
   there, else its saved brief plus a "where it stopped" note. No hand act; the conductor log says so. No spend, cap
   or remainder goes into any brief or resume note.
2. Before a planned switch (the plan's `soft`), detached runs get a checkpoint signal and a grace period, if a
   mechanism exists or is cheap.
3. A hard stop parks the killed runs as resumable and resumes them when an account has headroom again.

Design (built here):
- `src/RimMandrake/rimflow/stop_resume.py`: `scan` (read-only) and `sweep`. Stop events are the plan's acted
  stop/switch lines (`D:\ClaudeWork\rimmandrake\switching_plan\log.jsonl`, result rc 0) and `claude-account`'s
  op=use changed lines (`~/.claude-accounts/log.jsonl`). A run is resumed when `detached_helper.killed()` says it was
  killed (no result JSON), its end falls on a stop (or it has no end and a stop came after its launch), it was not
  already resumed and no later run of the same item exists, its item is still open, and the maturation tick does not
  own it (a unit named in a `design/concepts/*/version/stage_record.json` is retried by that tick).
- No headroom (the plan's newest pass is soft, stop or stopped): the run is parked (`parked` on its record, one
  conductor line) and resumed by the first pass with headroom.
- `detached_helper.launch` saves every brief as `<unit>.brief.src.md` (`brief_src` on the record), so a run with no
  transcript can still be relaunched.
- `switching_plan.check` runs the scan after every non-dry pass without HOLD and starts the sweep as its own
  transient unit (`rm-stop-resume`) when there is something to resume or park.

Limits: a bare `claude-account fleet-stop` that neither the plan nor `use` logged is not seen; with HOLD set or the
timer stopped nothing sweeps (`stop_resume.py sweep` by hand does). Stops before this landed are not swept.
A hand relaunch landing in the seconds between the sweep's per-run rescan and its launch can still double that run
(closing it needs hand launches to coordinate with the sweep). In a given clone, a `claude -p` session started by
hand within 300 s of the launch and before the run's own transcript can be taken for the run's session (interactive
windows are skipped: their entrypoint is `cli`). A run that crashed within 15 min before a stop is resumed; a kill
logged more than 15 min after it is missed. A run not launched by `detached_helper` (e.g. a seat's own unit) is
not seen, and runs launched before `brief_src` landed relaunch only by session. Not built: the checkpoint signal
with a grace period before a soft switch (goal 2).

## criteria
- a detached run killed by a switch's fleet stop is relaunched on the new account by the next plan pass, the same
  session where its transcript exists, else its brief plus a note; the conductor log has a line for it
- a run that finished normally, a run already relaunched, a maturation-owned run and a run on a closed item are not
  relaunched; no run is launched twice
- with no headroom a killed run is parked, and relaunched by the first pass with headroom
- no resume note carries spend, cap or remainder

## verify
Acceptance test: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_stop_resume` (fails on the base:
no module resumes a run). Also selftest_detached_helper, selftest_switching_plan, selftest_switching_plan_notice,
selftest_holder_resume.
Live: the next real switch (account-plan.timer, about 15:00 PST 2026-11-17, to steven) must resume
rm-detached-bench-rimmandrake-judge-pyrelands-blind-cycle-1794925887 (session c8a3854d) if it is still running
(the slack run's item is closed, so it is rightly not resumed); read
`python3 src/RimMandrake/rimflow/stop_resume.py scan` and the conductor log after it.

## refs
- /mnt/d/ClaudeWork/rimmandrake/conductor/mass_kill_20261117_0335.md
- /mnt/d/ClaudeWork/rimmandrake/conductor/hard_stop_checkpoint_20261117.md (helper progress)
- src/RimMandrake/Utils/switching_plan.py, src/RimMandrake/rimflow/detached_helper.py, ~/.local/bin/claude-account
- RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT (maturation's own retry of killed pipeline runs)
