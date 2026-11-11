"""Mutate ONLY the external Windows test stage under the sanctioned dotnet lock.
Restore every original byte in finally. Final proof restages current clone afresh.
Each variant must compile, execute the behavioural HS cases, and fail substantively.
"""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[2]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import selftest_flowworks_stock as wrapper
import selftest_winstage,winbuild
project=root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage=Path(winbuild.BUILD_ROOT)/selftest_winstage.stage_name_for(str(project),str(root))
raw=Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-shadow-raw/controls')
raw.mkdir(exist_ok=True)
assert not (h/'negative_controls.json').exists()
comp=Path('src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs')
idx=comp.with_name('HoseCrossShadows.cs')
original={p:(stage/p).read_bytes() for p in (comp,idx)}
assert all(data==(root/p).read_bytes() for p,data in original.items()),'Stage must start byte-identical'
carry='if (!LegacyFrame && meshes.ContainsKey(r)) DropMeshes(r);'
retract='if (!LegacyFrame && r.carry == HoseCarryState.Retracting && meshes.ContainsKey(r)) DropMeshes(r);'
# Localized original behaviours: exact absent-drop branches in published pre-fix source receipts.
variants=[
 ('original_carry_no_drop',comp,lambda s:s.replace(carry,'// original carry branch: no drop',1)),
 ('original_null_lay_no_drop',comp,lambda s:s.replace(carry,'// original null-lay branch: no drop',2).replace('// original null-lay branch: no drop',carry,1)),
 ('original_retract_no_drop',comp,lambda s:s.replace(retract,'// original retract branch: no drop',1)),
 ('mutant_drop_keeps_index',comp,lambda s:s.replace('crossIndex.Drop(r.parent.thingIDNumber);','/* mutant: index is not dropped */',1)),
 ('mutant_index_drop_no_remove',idx,lambda s:s.replace('strands.Remove(id);','/* mutant: stale strand retained */',1)),
 ('mutant_index_drop_no_dirty',idx,lambda s:s.replace('strands.Remove(id);\n            MarkNear(old, id);','strands.Remove(id);\n            /* mutant: dependent uppers not invalidated */',1)),
 ('mutant_rank_reversed',idx,lambda s:s.replace('if (rankOf(o.Id) >= rank) continue;','if (rankOf(o.Id) < rank) continue;',1)),
 ('mutant_dependent_mesh_not_cleared',comp,lambda s:s.replace('c.crossShadow = null;\n                if (c.crossSpans.Count > 0)','/* mutant: old shadow retained */\n                if (c.crossSpans.Count > 0)',1)),
]
env=dict(os.environ)
env['RIMWORLD_DECOMPILED']=subprocess.check_output(['wslpath','-w',str(root/'whittle/fw-drain-selftest-resume/evidence/reference')],text=True).strip()
env['WSLENV'] += ':RIMWORLD_DECOMPILED'
records=[]
with wrapper.dotnet_lock():
 try:
  for name,path,mutate in variants:
   for p,data in original.items(): (stage/p).write_bytes(data)
   source=original[path].decode(); changed=mutate(source)
   assert changed!=source,name
   (raw/(name+'.cs')).write_text(changed)
   (stage/path).write_text(changed)
   cmd=[wrapper._find_dotnet(),'run','--project',subprocess.check_output(['wslpath','-w',str(stage/project.relative_to(root))],text=True).strip(),'-c','Release','--','--only','HS_*']
   started=time.time()
   p=subprocess.run(cmd,env=env,cwd=root,capture_output=True,timeout=180)
   (raw/(name+'_stdout.txt')).write_bytes(p.stdout); (raw/(name+'_stderr.txt')).write_bytes(p.stderr)
   output=p.stdout.decode(errors='replace')
   failures=[line for line in output.splitlines() if line.startswith('FAIL')]
   record=dict(name=name,path=str(path),command=cmd,returncode=p.returncode,elapsed=time.time()-started,original_sha256=hashlib.sha256(original[path]).hexdigest(),mutant_sha256=hashlib.sha256(changed.encode()).hexdigest(),failures=failures,compiled='error CS' not in output and 'Build FAILED' not in output)
   records.append(record)
   (h/'negative_controls_partial.json').write_text(json.dumps(records,indent=2)+'\n')
   print(json.dumps(record),flush=True)
   assert p.returncode!=0 and failures and record['compiled'],name+' did not fail behaviourally'
 finally:
  for p,data in original.items(): (stage/p).write_bytes(data)
restored=all((stage/p).read_bytes()==data for p,data in original.items())
receipt=dict(time=time.time(),stage=str(stage),records=records,restored_byte_exact=restored,scope='external selftest stage only; original current-clone shipping source untouched; final runner must restage and rebuild')
(h/'negative_controls.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert restored
