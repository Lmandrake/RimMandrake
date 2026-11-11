from pathlib import Path
import sys,json,time
sys.path.insert(0,r'D:\Luke\dev\RimMandrake\src\RimMandrake\Utils')
from validation_core import Bridge
h=Path(__file__).resolve().parent
b=Bridge();tools=b.S.list_tools();names=[x.get('name',x.get('Name')) for x in tools];assert all(names)
(h/'live_tool_descriptors.json').write_text(json.dumps(tools,indent=2)+'\n')
r=b.call('jawa/running_mods',assembly='',details=False)
expected=json.loads((h/'live_inputs_before.json').read_text())['mods']
assert r.get('success') is True and [s.lower() for s in r['packageIds']]==expected,r
assert sum(n.startswith('jawa/') for n in names)>0
(h/'live_census.json').write_text(json.dumps(dict(time=time.time(),tool_count=len(names),jawa_count=sum(n.startswith('jawa/') for n in names),names=names,running=r,ordered_list_matches=True),indent=2)+'\n')
print('PASS live census',len(names),'tools;',sum(n.startswith('jawa/') for n in names),'jawa;',len(expected),'ordered mods')
