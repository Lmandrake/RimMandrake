"""Fresh Windows bridge surface and ordered running-list readback, before mutations."""
import hashlib
import json
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
sys.path.insert(0, str(root/'src/RimMandrake/Utils'))
from validation_core import Bridge

B = Bridge()
suffix = sys.argv[1] if len(sys.argv) > 1 else ''
assert suffix.startswith('attempt') and suffix.isalnum()
descriptors = B.S.list_tools()
names = [t.get('name',t.get('Name')) for t in descriptors]
assert names and all(names)
expected = json.loads((here/'live_inputs_before.json').read_text())['mods']
running = B.call('jawa/running_mods',assembly='',details=False)
assert running.get('success') is True and [p.lower() for p in running['packageIds']] == expected, running
assert sum(n.startswith('jawa/') for n in names) > 0
required = ('jawa/static_call','jawa/type_probe','jawa/debug_settings','jawa/build_batch','jawa/set_thing_props','jawa/spawn_pawn','jawa/mod_settings_field')
assert set(required).issubset(names)
identity = B.call('jawa/type_probe',typeName='RimMandrake.GimmeSomeSlack.Aerial.CompAerialAnchor')
expected_sha = hashlib.sha256((root/'src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll').read_bytes()).hexdigest()
assert identity.get('mvidMatchesFile') is True and identity.get('assemblyFileSha256') == expected_sha, identity
descriptor_path = here/('live_tool_descriptors' + suffix + '.json')
assert not descriptor_path.exists(), 'Preserve original census'
descriptor_path.write_text(json.dumps(descriptors,indent=2)+'\n')
receipt = dict(time=time.time(),tool_count=len(names),jawa_count=sum(n.startswith('jawa/') for n in names),running=running,identity=identity,ordered_list_matches=True)
receipt_path = here/('live_census' + suffix + '.json')
assert not receipt_path.exists(), 'Preserve original census'
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(names),'tools;',receipt['jawa_count'],'jawa;',len(expected),'ordered mods; loaded SHA',expected_sha)
