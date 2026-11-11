"""Read actual engine state and the bridge's safe tick observation, without dereferencing a missing TickManager."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'))
from validation_core import Bridge
b=Bridge()
report={'at':datetime.now(timezone.utc).isoformat(),'calls':[]}
try:
    tools=b.S.list_tools();schema=next(t for t in tools if t['name']=='jawa/static_call')
    assert {'type','method','args'}<=b.S._declared_params(schema)
    for ty,method,expected in [('Verse.Current','get_ProgramState','Entry'),('Verse.Current','get_Game','null'),('Verse.Find','get_CurrentMap','null')]:
        args=dict(type=ty,method=method,args='')
        r=b.call('jawa/static_call',**args)
        report['calls'].append({'tool':'jawa/static_call','params':args,'result':r})
        assert r.get('success') is True and r.get('result')==expected,r
    report['ticksGame']=[c['result']['ticksGame'] for c in report['calls']]
    assert len(set(report['ticksGame']))==1,report
finally:
    b.S.close()
    Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
