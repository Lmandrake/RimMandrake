from pathlib import Path
import subprocess,json,hashlib,time
p=Path(__file__).resolve().parent;root=p.parents[2];sha='88b81f3dd8f550b1efd6b2b827b4ffb84e74141b'
subprocess.run(['git','merge-base','--is-ancestor',sha,'origin/main'],cwd=root,check=True)
b=json.loads((p/'build_integrity.json').read_text())
for s,h in b['artifacts'].items():assert hashlib.sha256((root/s).read_bytes()).hexdigest()==h,s
before=json.loads((p/'integrity_before.json').read_text())['sha256'];changes=[s for s,h in before.items() if hashlib.sha256((root/s).read_bytes()).hexdigest()!=h];assert sorted(changes)==sorted(list(b['artifacts'])+['src/RimMandrake/Utils/selftest_settings_screens.py'])
r=dict(unrelated_publication_input_change='Utils/selftest_settings_screens.py arrived from origin during publication; not retested, no FlowWorks/GSS/shared change',time=time.time(),PUBLISHED=sha,ancestry_verified=True,HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),changes_since_suite=changes,artifacts=b['artifacts'],live_driver_sha256=hashlib.sha256((root/'src/RimMandrake/FlowWorks/northstar/reel_body_inlet_live.py').read_bytes()).hexdigest())
(p/'publication.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
