## Finding (2026-11-16, BENCH detached run on RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT)
The Dispatcher tick no longer overruns its 20 s metronome beat (606 dispatch beats, 0 overrun, 0 `tick:raised` in 24 h
to 2026-11-16 03:45Z) [measured]. What is left is its `observe` step (default_obs + decide) running past the act reserve
(14 s into the beat) and being cut: 27 `step_cut` rows with `step: observe` and 2 `tick:beat_starved` alarms in the
same 24 h [measured, `/mnt/d/ClaudeWork/rimmandrake/dispatcher/journal.jsonl`]. A cut decide is given back and runs
again next beat, but 5 cut or deferring beats in a row raise `tick:beat_starved` (incident dispatcher-20261115150613).

Where decide's time goes [measured]:
- base cost ~2.3 s (p50): `incident_step`'s whole-ledger replay (`RL.read_ledger`, ~1.8 s).
- the tail is the stage-machine roles (Designer, DesignerCodex). Mean decide on beats with a `role_done:Designer` act
  12.0 s, `role_hold:Designer` 7.7 s, `role_launch:Designer` 5.7 s, against 2.3 s for the median beat. On those
  paths decide runs `role_launch.judge_sync` (two `git fetch` calls, 45 s timeout each, ~1.2 s each normally),
  `designer_stage.open_run` (the packet; its `done_items` replays are memoised since 45cea5b928), and on a close
  `stage_close` + `stage_land` (a git push to origin/main) + `chain_next`.
- live after e4e5bad073/45cea5b928: 2 observe cuts in 17 beats (03:10:24Z before a DesignerCodex launch, 03:27:43Z
  before the DesignerCodex chain launch at 03:30:06Z).
- 77ba08dfecd1 adds `where` to every `step_cut` journal row (the frames of our code it was cut in): read those first;
  they name the slow function directly.

## Do
1. Read `where` on the observe cuts since 77ba08dfecd1 landed; confirm (or refute) that the stage-machine role paths
   are the cut ones.
2. Take the network and push work out of decide's beat: for example close and land a finished stage-machine run in
   its own unit (the way a role launch is a systemd-run), or let decide skip a stage-machine role when the time left
   before the act reserve is under its measured cost (st["beat_costs"], as notes and publish do since e4e5bad073).

## Acceptance test
Over 24 h with no network outage, the Dispatcher journal shows 0 `step_cut` rows with `step == "observe"` and 0
`tick:beat_starved` alarms (FAIL on 2026-11-16 03:45Z: 27 observe cuts, 2 beat_starved):

```python
import json,time,calendar
cut=time.time()-86400; obs=st=0
for l in open('/mnt/d/ClaudeWork/rimmandrake/dispatcher/journal.jsonl'):
    try: d=json.loads(l)
    except ValueError: continue
    try: t=calendar.timegm(time.strptime(str(d.get('at'))[:19],'%Y-%m-%dT%H:%M:%S'))
    except Exception: continue
    if t<cut: continue
    obs+=d.get('do')=='step_cut' and d.get('step')=='observe'
    st+=d.get('kind')=='tick:beat_starved'
print('FAIL' if obs or st else 'PASS','observe cuts',obs,'beat_starved',st)
```
