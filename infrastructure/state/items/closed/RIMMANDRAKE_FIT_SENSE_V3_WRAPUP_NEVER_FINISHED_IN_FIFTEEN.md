## Finding
rm-metronome.timer switched on 2026-11-13 00:23 PST. Sense beats 3603-3647: 23 of 45 overran 15 s (killed_term), against 161 of 1269 before cutover (phase table reason). Retry-alone pass rescues most families, but v3 (4 tries) and wrapup (4 tries) were killed even when read alone and never finished; evidence, companion, timers, flow, queues, codex, testing each lost a solo retry once. Load avg ~9 on 14 cores with 5 detached Opus helpers and a FlowWorks selftest suite running. Evidence: /mnt/d/ClaudeWork/rimmandrake/metronome/shadow/beats.jsonl (beat >= 3603).

## verify
Save as a script and run with python3; exit 0 + one PASS line expected (1 of 1). Watched FAIL at c1751a43ff (01:30 PST): 'FAIL never finished in 2h: [v3, wrapup]'.

```python
import json,sys,time,collections
ok=collections.Counter(); seen=collections.Counter(); cut=time.time()-7200
for l in open('/mnt/d/ClaudeWork/rimmandrake/metronome/shadow/beats.jsonl'):
    try: d=json.loads(l)
    except ValueError: continue
    if d.get('phase')!='sense' or d.get('start',0)<cut: continue
    for f in d.get('families') or []:
        seen[f]+=1; ok[f]+=d.get('exit')==0
bad=[f for f in ('v3','wrapup') if not ok[f]]
print('FAIL never finished in 2h: %s' % bad if bad else 'PASS v3 %d/%d wrapup %d/%d' % (ok['v3'],seen['v3'],ok['wrapup'],seen['wrapup']))
sys.exit(1 if bad or not seen['v3'] else 0)
```
