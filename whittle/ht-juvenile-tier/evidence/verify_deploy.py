"""Verify exact current HugeThings DLL/stamp/compiled source identity and the bounded published Biomes XML delta."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'))
import game_paths
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MOD=ROOT/'src/RimMandrake/HugeThings'
installed=Path(game_paths.LOCAL_MODS)/'HugeThings'
stamp=(MOD/'Assemblies/RM_HugeThings.dll.srchash').read_text()
rows=re.findall(r'^([0-9a-f]{64}) (.+)$',stamp,re.M)
report={'compiled_inputs':{},'deployment':{}}
for digest,name in rows:
    path=MOD/'Source'/name.strip();got=sha(path)
    report['compiled_inputs'][str(path.relative_to(ROOT))]={'stamp':digest,'actual':got}
    assert got==digest,name
assert '# dll: '+sha(MOD/'Assemblies/RM_HugeThings.dll') in stamp
for rel in ['Assemblies/RM_HugeThings.dll','Assemblies/RM_HugeThings.dll.srchash','Defs/TitanicTierDefs/RM_TitanicTierDef.xml']:
    pair=[sha(p/rel) for p in [MOD,installed]];report['deployment'][rel]=pair;assert pair[0]==pair[1],rel
source=ROOT/'src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml'
target=Path(game_paths.LOCAL_MODS)/'RimMandrake.Biomes/Biomes/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml'
pair=[sha(p) for p in [source,target]];report['deployment'][str(target)]=pair;assert pair[0]==pair[1]
Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'compiled_input_count':len(rows),'deployment':report['deployment']}))
