"""Final read-only content checks after external caller proof, publication and release."""
import hashlib,json,subprocess,time,sys
from pathlib import Path
import xml.etree.ElementTree as ET
here=Path(__file__).resolve().parent;root=here.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name): return json.loads((here/name).read_text())
target=here/(sys.argv[1] if len(sys.argv)>1 else 'final_readback_external.json');assert not target.exists()
manifest=read('external_green2/integrity_before.json')['sha256']
receipt=read('external_green2/selftest_receipt.json')
assert receipt['returncode']==0 and receipt['source_test_hashes_unchanged']
assert manifest==receipt['sha256_after']=={p:sha(root/p) for p in manifest}
assert not read('external_green2/windows_stage_readback.json')['mismatches']
pub=read('external_publication.json');commit=pub['sha']
assert subprocess.run(['git','merge-base','--is-ancestor',commit,'origin/main'],cwd=root).returncode==0
for name,digest in pub['inputs'].items():
    assert sha(root/name)==digest
    assert hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=root)).hexdigest()==digest
# Include every direct external Compile input, even unchanged preexisting source links.
project=root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage=Path('/mnt/d/ClaudeWork/rimmandrake/build/selftest_RimMandrakeFlowWorks.SelfTest_79bb8021')
external={}
for node in ET.parse(project).iter('Compile'):
    p=(project.parent/node.get('Include','').replace('\\','/')).resolve()
    if p.is_file() and p.is_relative_to(root) and not p.is_relative_to(root/'src/RimMandrake/FlowWorks/Source'):
        rel=str(p.relative_to(root));external[rel]=dict(current=sha(p),stage=sha(stage/rel),published=hashlib.sha256(subprocess.check_output(['git','show',commit+':'+rel],cwd=root)).hexdigest())
        assert len(set(external[rel].values()))==1
live=read('live_attempt4.json');cleanup=read('live_attempt4_cleanup.json')
assert live['status']==live['restore']['status']=='PASS'
assert not live['changed_existing_saves'] and live['protected_before']==live['protected_after']
assert not live['log_budget']['new_errors'] and live['log_budget']['lost']==0 and live['log_budget']['sentinel']['alive']
for cmd in cleanup['cleanup']: assert cmd['returncode']==0
core=root/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'
corehash=sha(core);assert corehash==live['identity']['assemblyFileSha256']
proof='src/RimMandrake/FlowWorks/northstar/tank_theft_live.py'
proofhash=sha(root/proof)
prior_live_readback=read('final_readback.json')
assert prior_live_readback['time']>cleanup['finished']
assert proofhash==prior_live_readback['proof_sha256']
assert proofhash==hashlib.sha256(subprocess.check_output(['git','show',commit+':'+proof],cwd=root)).hexdigest()
# Shipping source stamp excludes SelfTest; compare every compiled core source to the actual live bytes' stamp.
core_source={}
for line in Path(str(core)+'.srchash').read_text().splitlines():
    if not line or line.startswith('#'): continue
    digest,rel=line.split(' ',1);p=(core.parent.parent/'Source'/rel).resolve();assert sha(p)==digest;core_source[str(p.relative_to(root))]=digest
assert '# dll: '+corehash in Path(str(core)+'.srchash').read_text()
deployment=read('external_deployment_readback.json')
assert deployment['status']=='PASS'
assert deployment['applied_files']==4 and deployment['unrelated_drift_preserved']
for row in deployment['files']:
    assert sha(Path(row['source']))==sha(Path(row['target']))==row['published_sha256']
for path,digest in deployment['unrelated_drift_before_sha256'].items():
    p=Path(path);assert (sha(p) if p.is_file() else None)==digest,path
for path,row in read('external_deployment_backup.json')['files'].items():
    assert sha(Path(row['backup']))==row['backup_sha256']
build=read('external_build_after.json')
for path,digest in build['source_inputs'].items():
    assert sha(root/path)==digest,path
for mod,pair in build['pairs'].items():
    for path,digest in pair['source_sha256'].items():
        assert sha(root/path)==digest,path
        assert sha(Path('/mnt/d/ClaudeWork/rimmandrake/build')/mod/path)==digest,path
assert sha(Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'))==corehash
assert '1278/1278 passed' in (here/'external_green2/csharp_stdout.txt').read_text()
assert 'NOT RUNNING' in (here/'final_game_stdout.txt').read_text()
locks=(here/'final_bridge_stdout.txt').read_text();assert 'driver lock: FREE' in locks and 'bridge FREE' in locks
traces={}
for name in ('red1','green1','green2','external_red1','external_red2','external_red3','external_green2'):
    p=Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/tank-theft-raw')/(name+'_selftest_writes.strace')
    digest=sha(p);assert digest==read(name+'/output_extraction.json')['original_observer_sha256'];traces[str(p)]=digest
inputs=['external_green2/csharp_stdout.txt','external_green2/selftest_receipt.json','external_green2/windows_stage_readback.json','external_build_before.json','external_build_after.json','external_publication.json','external_deployment_readback.json','external_deployment_backup.json','external_catalog.json','deploy_external_plan_stdout.txt','deploy_external_pairs_plan.json','live_attempt4.json','live_attempt4_cleanup.json','final_game_stdout.txt','final_bridge_stdout.txt','build1_stdout.txt','build_Cauldron_stdout.txt','build_LuminousPigment_stdout.txt','reference_provenance.json','claim_withdrawal.json','owner_stamp_fault.json','external_green1_interruption.json']
record=dict(time=time.time(),status='PASS',operation='Final readback of tested/published/staged/source-stamped/deployed bytes, original raw traces and restored DOWN/FREE state',publication=commit,source_inputs_match_tested=manifest,external_compile_inputs=external,core_dll_sha256=corehash,core_compiled_source_sha256=core_source,external_build=read('external_build_after.json'),external_deployment=deployment,original_traces=traces,raw_evidence_sha256={p:sha(here/p) for p in inputs},live_status=live['status'],restoration=live['restore'],protected_hashes=live['protected_after'],log_budget=live['log_budget'],live_script_sha256=proofhash,original_post_live_script_readback=dict(file='final_readback.json',time=prior_live_readback['time'],sha256=sha(here/'final_readback.json')),limits=['Optional integration transfer bodies executed offline; the 13-mod live proof exercises unchanged FlowWorks bytes, not GlowTank/gas-tap in game.','Original OWNER-stamp wrapper fault and unsupported LOADING stamp are retained; final game measurement and locks are explicit.'])
target.write_text(json.dumps(record,indent=2)+'\n')
print('PASS final external readback:',len(manifest),'test inputs;',len(external),'external Compile inputs;',len(core_source),'live core source-stamp inputs; deployed pairs; DOWN/FREE')
