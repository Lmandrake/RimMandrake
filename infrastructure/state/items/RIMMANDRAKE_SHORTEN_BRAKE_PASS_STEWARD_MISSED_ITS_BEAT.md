## spec

The second defect named inside `RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED`, split out
2026-11-17 so that ticket's builder could keep a minimal diff — it is a different file and a different failure.

Its words, from that ticket: *"brake_release.py takes over 120 s a pass (per-mod fill_plan), so
brake_release.json ran 38 min stale and steward.json missed its heartbeat twice."*

**Where it is.** `src/RimMandrake/Utils/testq/brake_release.py:102`, in `decide()`:

```python
plans = {m: T.fill_plan(m, 1, int(os.environ.get("TESTQ_FILL_CAP") or T.FILL_CAP_DEFAULT), T.FILL_DAY_S, now)
         for m in mods}
```

One `fill_plan` per mod, every pass, before anything is known about whether a brake needs lifting at all — and the
very next line throws most of it away (`braked = [m for m, p in plans.items() if p["verdict"] == "brake"]`, then
only `braked[0]` is used). The pass is the cost of planning every mod to find the first braked one.

**Why it matters beyond slowness.** `steward.py:117` sets `STALE_S = 300` and `steward.py:37` names
`STALE_HEARTBEAT` — *"the watcher's: steward.json not written for 5 min"* — which restarts the tick timer once and
then escalates. So a pass over 120 s does not merely run late: it eats a measurable share of the heartbeat budget,
and twice it ate all of it. A watchdog that fires because its own watcher is busy is an alarm about nothing, and it
trains the next reader to ignore it. There is precedent in this same file's history:
`selftest_brake_release_beat.py:7` records *"Steve beats took 8-15 s, so the release returned silently on every
beat and brake_release.json went 2 h stale"* — the same shape, already fixed once at a smaller scale.

**The fix.** Make the pass cost bounded, not proportional to the mod list: find the braked mod without planning
every mod (the cheap `brake_tail(filler_jobs())` check already gates entry — ask which mods are even candidates
before planning), or plan lazily and stop at the first brake, or cache a plan within a pass. Whichever way, the
work must not grow with the roster.

🔴 **Keep the four answers apart while you do it, because a cheaper check is exactly where they get lost.** A mod
whose plan was NOT COMPUTED this pass (because we stopped early) is not a mod that is "not braked" — the record
must not imply the skipped ones were read and found clean. And a `fill_plan` that could not run at all stays
UNMEASURED and must not be collapsed into "no brake to lift". The `{"state": "none", "reason": ...}` return already
carries per-mod text; whatever replaces it must distinguish *looked and not braked* from *not looked at*.

Related but NOT this ticket: the game-restart half is
`RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED` (in `infrastructure/stevedesktop/worker.py`),
being built separately.

## refs

file: src/RimMandrake/Utils/testq/brake_release.py
file: src/RimMandrake/Utils/testq/steward.py
file: src/RimMandrake/Utils/testq/selftest_brake_release_beat.py

## verify

python3 src/RimMandrake/Utils/testq/selftest_brake_release_beat.py

## criteria

- A1: a `decide()` pass over a roster of many mods costs a bounded number of `fill_plan` calls, not one per mod,
  and the measured wall time no longer approaches `steward.STALE_S`.
- A2: the pass's record distinguishes a mod planned and found not braked from a mod not planned this pass, and from
  a mod whose plan could not be computed.
- A3: the braked mod chosen is the same one the current code would choose (no behaviour change in what gets lifted).
- A4: `steward.json`'s heartbeat is not missed in a pass over a full roster.

## acceptance

Acceptance test: a case in `selftest_brake_release_beat.py` (or beside it) with a stubbed `fill_plan` that COUNTS
its calls over a roster of N mods, asserting the count does not scale with N and that the chosen braked mod is
unchanged; plus a case where one mod's `fill_plan` raises, asserting the record says UNMEASURED for that mod rather
than "no brake". Watched FAILING on the base commit, where the call count equals N. The 120 s / 38 min / two missed
beats figures come from the parent ticket's incident and are the motivation, not the bar — the bar is the call
count and the four-answers distinction, both measurable offline.
