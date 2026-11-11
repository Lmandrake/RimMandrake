"""First bridge read: actual tool census and ordered running load list."""
from pathlib import Path
import sys
import json
import time
sys.path.insert(0, r'D:\Luke\dev\RimMandrake\src\RimMandrake\Utils')
from validation_core import Bridge
here = Path(__file__).resolve().parent
b = Bridge()
tools = b.S.list_tools()
names = [tool.get('name', tool.get('Name')) for tool in tools]
assert names and all(names)
(here / 'live_tool_descriptors.json').write_text(json.dumps(tools, indent=2) + '\n')
running = b.call('jawa/running_mods', assembly='', details=False)
expected = json.loads((here / 'live_inputs_before.json').read_text())['mods']
assert running.get('success') is True and [s.lower() for s in running['packageIds']] == expected
assert sum(name.startswith('jawa/') for name in names) > 0
(here / 'live_census.json').write_text(json.dumps(dict(time=time.time(), tool_count=len(names),
    jawa_count=sum(name.startswith('jawa/') for name in names), names=names, running=running,
    ordered_list_matches=True), indent=2) + '\n')
print('PASS actual census and ordered list', len(names), len(expected))
