"""Measure only the two changed integration projects and their shipping pairs/stage."""
import hashlib,json,sys,time
from pathlib import Path
import xml.etree.ElementTree as ET
here=Path(__file__).resolve().parent
root=here.parents[2]
phase=sys.argv[1]
assert phase in ('before','after')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
projects={'Cauldron':'RM_Cauldron.csproj','LuminousPigment':'RM_LuminousPigment.csproj'}
inputs={};pairs={};stage={}
for mod,name in projects.items():
    project=root/'src/RimMandrake'/mod/'Source'/name
    compiled=[(project.parent/e.get('Include').replace('\\','/')).resolve() for e in ET.parse(project).iter('Compile')]
    for p in [project]+compiled:
        rel=str(p.relative_to(root));inputs[rel]=sha(p)
        if phase=='after': stage[rel]=sha(Path('/mnt/d/ClaudeWork/rimmandrake/build')/mod/rel)
    dll=root/'src/RimMandrake'/mod/'Assemblies'/('RimMandrake.Cauldron.dll' if mod=='Cauldron' else 'RimMandrakeLuminousPigment.dll')
    if phase=='after':
        stamp=Path(str(dll)+'.srchash');text=stamp.read_text()
        assert '# dll: '+sha(dll) in text
        lines=[line.split(' ',1) for line in text.splitlines() if line and not line.startswith('#')]
        verified={str((project.parent/path).resolve().relative_to(root)):digest for digest,path in lines}
        for rel,digest in verified.items(): assert sha(root/rel)==digest,rel
        assert set(str(p.relative_to(root)) for p in compiled)<=set(verified)
        pairs[mod]=dict(dll=str(dll.relative_to(root)),dll_sha256=sha(dll),stamp_sha256=sha(stamp),source_sha256=verified)
        for p in (dll,stamp):
            rel=str(p.relative_to(root));assert sha(Path('/mnt/d/ClaudeWork/rimmandrake/build')/mod/rel)==sha(p)
references={str(p):sha(p) for p in [root/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll',Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll')]}
if phase=='after':
    prior=json.loads((here/'external_build_before.json').read_text())
    assert inputs==prior['source_inputs'] and references==prior['reference_sha256']
    assert stage==inputs
out=here/('external_build_'+phase+'.json');assert not out.exists()
out.write_text(json.dumps(dict(time=time.time(),source_inputs=inputs,stage_sha256=stage,pairs=pairs,reference_sha256=references),indent=2)+'\n')
print('PASS',phase,len(inputs),'source/project inputs;',len(pairs),'verified shipping pairs')
