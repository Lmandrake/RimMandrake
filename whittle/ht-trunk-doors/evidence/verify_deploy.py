import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import game_paths as G
rows=[]
pairs=[('HugeThings/Assemblies/RM_HugeThings.dll','HugeThings/Assemblies/RM_HugeThings.dll'),
('HugeThings/Assemblies/RM_HugeThings.dll.srchash','HugeThings/Assemblies/RM_HugeThings.dll.srchash'),
('HugeThings/Defs/JobDefs/RM_JobDefs.xml','HugeThings/Defs/JobDefs/RM_JobDefs.xml'),
('HugeThings/Defs/WorkGiverDefs/RM_WorkGivers.xml','HugeThings/Defs/WorkGiverDefs/RM_WorkGivers.xml'),
('HugeThingsTestRaces/Defs/ThingDefs_Plants/RM_TestContactPlant.xml','HugeThingsTestRaces/Defs/ThingDefs_Plants/RM_TestContactPlant.xml'),
('FlowWorks/Assemblies/RimMandrakeFlowWorks.dll','FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'),
('FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash','FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash'),
('GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll','GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll'),
('LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll','LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll'),
('LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll.srchash','LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll.srchash'),
('TheRot/Patches/RotGiants_HugeFootprint.xml','RimMandrake.Biomes/Biomes/TheRot/Patches/RotGiants_HugeFootprint.xml'),
('TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml','RimMandrake.Biomes/Biomes/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml'),
('Cauldron/Assemblies/RimMandrake.Cauldron.dll','RimMandrake.Biomes/Biomes/Cauldron/Assemblies/RimMandrake.Cauldron.dll'),
('Cauldron/Assemblies/RimMandrake.Cauldron.dll.srchash','RimMandrake.Biomes/Biomes/Cauldron/Assemblies/RimMandrake.Cauldron.dll.srchash')]
for source,target in pairs:
 a=root/'src/RimMandrake'/source;b=Path(G.LOCAL_MODS)/target
 rows.append(dict(source=str(a),deployed=str(b),source_sha256=hashlib.sha256(a.read_bytes()).hexdigest(),deployed_sha256=hashlib.sha256(b.read_bytes()).hexdigest()))
Path(sys.argv[1]).write_text(json.dumps(rows,indent=2)+'\n')
assert all(r['source_sha256']==r['deployed_sha256'] for r in rows),'deployment bytes differ'
print('PASS direct deployment bytes',len(rows))
