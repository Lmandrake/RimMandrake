"""Read back staged inputs and generated complete production bodies after final proof."""
import hashlib,json,subprocess,sys,time
import xml.etree.ElementTree as ET
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[2]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import selftest_winstage,winbuild
project=root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage=Path(winbuild.BUILD_ROOT)/selftest_winstage.stage_name_for(str(project),str(root))
before=json.loads((h/'integrity_before.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for rel,digest in before['sha256'].items():
 if rel.startswith('whittle/'): continue
 p=stage/rel
 checks[rel]=dict(expected=digest,actual=sha(p) if p.is_file() else None)
# Expand every direct project Compile input. Inputs outside the hose-focused before manifest
# were tracked/unchanged at its recorded HEAD/status: recover those exact immutable Git blobs.
compile_inputs={}
for node in ET.parse(project).getroot().iter('Compile'):
 rel=node.get('Include','')
 if not rel or '$(' in rel: continue
 path=(project.parent/rel.replace('\\','/')).resolve()
 repo_rel=str(path.relative_to(root))
 expected=before['sha256'].get(repo_rel)
 provenance='pre-proof hash manifest'
 if expected is None:
  expected=hashlib.sha256(subprocess.check_output(['git','show',before['HEAD']+':'+repo_rel],cwd=root)).hexdigest()
  provenance='immutable pre-proof HEAD; recorded status has no modification to this input'
 compile_inputs[repo_rel]=dict(expected=expected,current=sha(path),stage=sha(stage/repo_rel),provenance=provenance)
for rel in ['src/RimMandrake/LuminousPigment/Source/FlowWorksWaterBridge.cs','src/RimMandrake/Cauldron/Source/RM_GasTap.cs']:
 expected=hashlib.sha256(subprocess.check_output(['git','show',before['HEAD']+':'+rel],cwd=root)).hexdigest()
 compile_inputs[rel]=dict(expected=expected,current=sha(root/rel),stage=sha(stage/rel),provenance='immutable pre-proof HEAD; recorded status unchanged; source read by extraction target')
assert all(v['expected']==v['current']==v['stage'] for v in compile_inputs.values())
# Normal rsync excludes binary artwork. Shipping DLLs are checked separately in identity_after.
excluded=[p for p in checks if Path(p).suffix.lower() in ('.png','.psd','.ogg','.wav')]
assert all(v['expected']==v['actual'] for p,v in checks.items() if p not in excluded)
source=(root/'src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs').read_text()
generated=stage/project.relative_to(root).parent/'obj/Release/net8.0/HoseShadow.g.cs'
gen=generated.read_text()
sigs=['private void DrawAll()','private void DropMeshes(','private static void DestroyMeshes(','private static void DestroyOver(','private void DrawCrossShadow(','private void RebuildCrossShadow(','private void BuildCrossMesh(']
methods={}
for sig in sigs:
 a=source.index(sig); b=source.index('{',a); depth=0
 for k in range(b,len(source)):
  if source[k]=='{': depth+=1
  if source[k]=='}':
   depth-=1
   if depth==0: break
 body=source[a:k+1]
 assert gen.count(body)==1,sig
 methods[sig]=dict(sha256=hashlib.sha256(body.encode()).hexdigest(),chars=len(body),exact_occurrences=gen.count(body))
(h/'HoseShadow.generated.txt').write_bytes(generated.read_bytes())
artifacts={str(p.relative_to(stage)):sha(p) for p in (stage/project.relative_to(root).parent/'bin/Release/net8.0').glob('RimMandrakeFlowWorks.SelfTest.*')}
receipt=dict(time=time.time(),stage=str(stage),inputs=checks,compile_inputs=compile_inputs,excluded=excluded,all_inputs_match=True,exact_production_methods=methods,generated_sha256=sha(generated),artifacts=artifacts,BUILD_SOURCE=json.loads((stage/'BUILD_SOURCE.json').read_text()))
assert not (h/'stage_identity.json').exists()
(h/'stage_identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(input_count=len(checks),excluded=len(excluded),methods=len(methods),artifacts=artifacts)))
