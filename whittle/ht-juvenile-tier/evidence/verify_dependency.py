"""Exact authorized dependency pair readback; never modifies FlowWorks source/artifacts."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
work=Path(__file__).resolve().parents[1]
a=json.loads((work/'DEPENDENCY_AUTHORIZATION.json').read_text());assert a['authorized'] is True
mod=ROOT/'src/RimMandrake/FlowWorks'
game=Path('/mnt/d/SteamLibrary/steamapps/common/RimWorld/Mods/FlowWorks')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'RimMandrakeFlowWorks.dll':a['expected_dll_sha256'],'RimMandrakeFlowWorks.dll.srchash':a['expected_stamp_sha256']}
report={'phase':sys.argv[1],'pairs':{},'compiled_inputs':{}}
for name,digest in expected.items():
    repo=mod/'Assemblies'/name;installed=game/'Assemblies'/name
    assert sha(repo)==digest
    report['pairs'][name]={'repo_sha256':sha(repo),'installed_sha256':sha(installed)}
    if sys.argv[1]=='after':assert sha(installed)==digest
text=(mod/'Assemblies/RimMandrakeFlowWorks.dll.srchash').read_text()
assert '# dll: '+expected['RimMandrakeFlowWorks.dll'] in text
for digest,name in re.findall(r'^([0-9a-f]{64}) (.+)$',text,re.M):
    source=(mod/'Source'/name.strip()).resolve();actual=sha(source);assert actual==digest,name
    report['compiled_inputs'][str(source.relative_to(ROOT))]={'expected':digest,'actual':actual}
Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'phase':report['phase'],'pairs':report['pairs'],'compiled_input_count':len(report['compiled_inputs'])}))
