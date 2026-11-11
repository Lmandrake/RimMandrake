from pathlib import Path
import hashlib,json,time
from integrity import root,here,hashes
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((here/'integrity_before.json').read_text())['sha256']
now=hashes();changed=[p for p,h in before.items() if now.get(p)!=h]
artifacts=['src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll','src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash']
assert sorted(changed)==sorted(artifacts),changed
stage=Path('/mnt/d/ClaudeWork/rimmandrake/build/FlowWorks');stamp=root/artifacts[1]
project=None;dll=None;inputs={}
for line in stamp.read_text().splitlines():
 if line.startswith('# project: '):project=(root/'src'/line[11:]).resolve()
 elif line.startswith('# dll: '):dll=line[7:]
 elif not line.startswith('#') and line.strip():
  h,p=line.split(' ',1);rel=str((project.parent/p).resolve().relative_to(root));assert sha(root/rel)==sha(stage/rel)==h,rel;inputs[rel]=h
assert dll==sha(root/artifacts[0])==sha(stage/artifacts[0])
r=dict(time=time.time(),stage=str(stage),changes_since_suite=changed,staged_compile_inputs=inputs,artifacts={p:sha(root/p) for p in artifacts},live_driver_sha256=sha(root/'src/RimMandrake/FlowWorks/northstar/railing_toggle_live.py'),gss_unchanged=all(now[p]==h for p,h in before.items() if 'GimmeSomeSlack/' in p))
assert not (here/'build_integrity.json').exists();(here/'build_integrity.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(inputs),'stamped compile inputs; exact DLL/stamp pair; GSS unchanged')
