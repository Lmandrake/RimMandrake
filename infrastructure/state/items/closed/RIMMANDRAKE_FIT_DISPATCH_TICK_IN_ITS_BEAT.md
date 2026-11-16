## Finding (2026-11-14, CONDUCTOR helper, incident dispatcher-20261113182805)

The Dispatcher tick runs as the metronome's `dispatch` phase with `limit_s` 20
(`src/RimMandrake/Utils/systemd/metronome_phases.json`). Past 20 s the metronome SIGTERMs the group, the tick
raises `SystemExit: 143` and journals `tick:raised`, which keeps the emergency incident
`dispatcher-20261113182805` ringing.

Measured from `/mnt/d/ClaudeWork/rimmandrake/metronome/shadow/beats.jsonl` (last 6000 lines, 639 dispatch beats):
613 exit 0, 25 `overrun` (`killed_term`, 20.1-23.1 s), 1 deferred. The overruns came in bursts:
18 between 2026-11-13 18:19Z and 20:34Z (before the network outage), one at 2026-11-14 02:05Z, and 5 between 08:49Z
and 09:15Z (during the DNS outage, when git and publish hung). Completed dispatch beats: p50 5.4 s, p90 15.9 s,
p99 18.4 s, so the normal tick runs close to its limit.

Why the kill still happens: `tick()` (src/RimMandrake/rimflow/dispatcher.py) bounds only `execute()` (acts stop
`BEAT_ACT_RESERVE_S` = 6 s before `METRONOME_DEADLINE`; notes and publish stop 2 s before). `default_obs()` +
`decide()` before it and `HB.tick_step()` after it have no deadline [measured by reading the code]. Which step is
slow in the bursts is not measured yet [guess ~60%: observation reads (git, systemctl, ledger) under load ~9].

A killed tick loses no work (launches are given back, the next beat decides again), but every kill is an emergency
alarm.

## Do
1. Measure the time per step inside a tick (obs, decide, execute, helper budget) for >= 100 beats.
2. Bound the slow step against `beat_end`, or skip/defer it, so a tick ends on its own before the kill.
   Changing a value in the phase table (for example `limit_s`) is allowed under the Relentless freeze; a new key is not.

## Acceptance test
Over 24 h of beats that contain no network outage, `beats.jsonl` shows 0 dispatch beats with
`exit == "overrun"`, and the Dispatcher journal shows 0 `tick:raised` lines:

```python
import json,time
cut=time.time()-86400; n=bad=0
for l in open('/mnt/d/ClaudeWork/rimmandrake/metronome/shadow/beats.jsonl'):
    try: d=json.loads(l)
    except ValueError: continue
    if d.get('phase')=='dispatch' and d.get('start',0)>=cut:
        n+=1; bad+=d.get('exit')=='overrun'
print(('PASS' if n>=300 and bad==0 else 'FAIL'), 'dispatch beats', n, 'overrun', bad)
```
