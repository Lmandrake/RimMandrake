"""Fresh content readback after restoration/release; never touch or relabel old evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
root = here.parents[2]
attempt = sys.argv[1]
run_number = attempt.removeprefix('live_attempt')
assert run_number.isdigit()
target = here / 'final_readback.json'
assert not target.exists(), 'Preserve completed readbacks'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
live = json.loads((here/(attempt+'.json')).read_text())
cleanup = json.loads((here/(attempt+'_cleanup.json')).read_text())
assert live['status'] == live['restore']['status'] == 'PASS'
assert not live['changed_existing_saves'] and live['protected_before'] == live['protected_after']
assert not live['log_budget']['new_errors'] and live['log_budget']['lost'] == 0 and live['log_budget']['sentinel']['alive']
assert all(x['returncode'] == 0 for x in cleanup['cleanup'])
assert 'driver lock: FREE' in cleanup['cleanup'][-1]['stdout'] and 'bridge FREE' in cleanup['cleanup'][-1]['stdout']
assert 'NOT RUNNING' in cleanup['cleanup'][-2]['stdout']
before = json.loads((here/'green2/integrity_before.json').read_text())
actual = {p:sha(root/p) for p in before['sha256']}
assert actual == before['sha256']
# Supplement the pre-run FlowWorks manifest with external direct Compile inputs.
# Their BEFORE provenance is the recorded clean Git state/immutable initial HEAD,
# not a pretended earlier filesystem hash. Read stage/current bytes independently.
project = root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage = Path('/mnt/d/ClaudeWork/rimmandrake/build/selftest_RimMandrakeFlowWorks.SelfTest_79bb8021')
external = {}
for element in ET.parse(project).iter('Compile'):
    include = element.get('Include','').replace('\\','/')
    p = (project.parent/include).resolve()
    if not p.is_file() or not p.is_relative_to(root) or p.is_relative_to(root/'src/RimMandrake/FlowWorks/Source'):
        continue
    rel = str(p.relative_to(root))
    blob = hashlib.sha256(subprocess.check_output(['git','show',before['HEAD']+':'+rel],cwd=root)).hexdigest()
    external[rel] = dict(initial_committed_blob=blob,current=sha(p),windows_stage=sha(stage/rel))
    assert len(set(external[rel].values())) == 1
raw = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/tank-theft-raw')
traces = {}
for name in ('red1','green1','green2'):
    receipt = json.loads((here/name/'output_extraction.json').read_text())
    path = raw/(name+'_selftest_writes.strace')
    traces[str(path)] = sha(path)
    assert traces[str(path)] == receipt['original_observer_sha256']
commits = ['bd3ebe304e93e19b3cd23b560cd9ba397f7df027']
for name in ('publish_proof1','publish_proof2','publish_proof3','publish_proof4'):
    text = (here/(name+'_stdout.txt')).read_text()
    commits += [line.split()[1] for line in text.splitlines() if line.startswith('PUBLISHED ')]
ancestry = {s:subprocess.run(['git','merge-base','--is-ancestor',s,'origin/main'],cwd=root).returncode for s in commits}
assert set(ancestry.values()) == {0}
proof = 'src/RimMandrake/FlowWorks/northstar/tank_theft_live.py'
assert sha(root/proof) == hashlib.sha256(subprocess.check_output(['git','show',commits[-1]+':'+proof],cwd=root)).hexdigest()
paths = [root/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll',
         Path('/mnt/d/Luke/dev/RimMandrake/src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'),
         Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll')]
dlls = {str(p):sha(p) for p in paths}
assert len(set(dlls.values())) == 1 and next(iter(dlls.values())) == live['identity']['assemblyFileSha256']
evidence = ['green2/csharp_stdout.txt','green2/selftest_receipt.json','green2/windows_stage_readback.json',
            'build1_command.json','build1_stdout.txt','deploy_apply1_stdout.txt',attempt+'.json',attempt+'_cleanup.json',
            'preflight_offline'+run_number+'.json','preflight_live'+run_number+'.json','live_census'+run_number+'.json','owner_stamp_fault.json','stamp_loading1_stderr.txt']
record = dict(time=time.time(),operation='Fresh content/source/deployed bytes/raw execution/restoration readback after release',
              latest_publication=commits[-1],publications=commits,ancestry=ancestry,source_inputs_match_tested=actual,
              external_compile_inputs=external,proof_sha256=sha(root/proof),dll_sha256=dlls,
              evidence_sha256={p:sha(here/p) for p in evidence},external_original_traces=traces,
              live_status=live['status'],arms=live['arms'],restoration=live['restore'],
              protected_hashes=live['protected_after'],cleanup=cleanup['cleanup'],log_budget=live['log_budget'])
target.write_text(json.dumps(record,indent=2)+'\n')
print('PASS final readback:',len(actual),'original inputs;',len(external),'external compile inputs; exact DLL; raw traces; restored DOWN/FREE')
