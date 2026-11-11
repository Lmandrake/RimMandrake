"""Inspect raw proof, derive counts, and verify exact source/kernel identities."""
import hashlib,json,re,subprocess,time
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[2]
wrapper=(here/'selftest_stdout.txt').read_text()
csharp=(here/'csharp_stdout.txt').read_text()
receipt=json.loads((here/'selftest_receipt.json').read_text())
counts=re.search(r'^(\d+)/(\d+) passed$',csharp,re.M)
hose=re.search(r'hose: (\d+)/(\d+) assertions passed',csharp)
exact=(here/'exact_stdout.txt').read_text(); mutant=(here/'mutant_stdout.txt').read_text()
source=root/'src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert counts and counts[1]==counts[2]
assert hose and hose[1]==hose[2]
assert receipt['returncode']==0 and receipt['source_test_hashes_unchanged']
assert 'PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in wrapper
assert not re.search(r'^FAIL',csharp,re.M)
assert 'UNMEASURED, not a pass or a fail' not in csharp
for label in ['exact','mutant']:
 r=json.loads((here/(label+'_receipt.json')).read_text())
 assert r['returncode']==0 and r['fixture_source_sha256']==sha
 bad=[p for p,v in r['production_inputs'].items() if v['source_sha256']!=v['stage_sha256']]
 assert bad==(['src/RimMandrake/_Shared/SlackGeometry/CordPlanner.cs'] if label=='mutant' else [])
assert 'PASS Original scenic: the cost never blocks' in mutant
assert 'FAIL Final scenic: the cost never blocks (both poses cross both remote reel columns with no way round: no route)' in mutant
assert len(re.findall('^FAIL ',mutant,re.M))==1
assert 'mouth=(20.026,8.773) floor=(20,8) walkable=True outlet_clear=True' in mutant
assert 'PASS Final scenic can-fail: blocking the remote reel seals the corridor (no route)' in exact
assert re.search(r'^  HoseGptFix: 27/27$',csharp,re.M)
# Program.Check is silent on individual passes; exact_stdout prints each check separately.
assert 'PASS Final scenic: the cost never blocks (both poses cross both remote reel columns with no way round: laid)' in exact
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=root,text=True).splitlines()
assert changed==['src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs']
record=dict(time=time.time(),source_sha256=sha,counts=list(map(int,counts.groups())),hose_counts=list(map(int,hose.groups())),wrapper_returncode=receipt['returncode'],source_test_hashes_unchanged=receipt['source_test_hashes_unchanged'],tracked_changed_paths=changed,checks='All assertions in verify_proof.py passed',csharp_sha256=hashlib.sha256(csharp.encode()).hexdigest(),wrapper_sha256=hashlib.sha256(wrapper.encode()).hexdigest(),limits=['Offline planned Lay seed 7; no live or rendered proof','No relay endpoint, separate CheckInstall search, or all carried-route guarantee','Plump can use Flat fallback in production; distinct shape not asserted'])
assert not (here/'verification.json').exists()
(here/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
