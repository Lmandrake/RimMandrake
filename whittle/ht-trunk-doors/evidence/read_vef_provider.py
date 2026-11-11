from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
from lint_harmony_targets import _fix_dnfile_coded_index_width
import dnfile
_fix_dnfile_coded_index_width(dnfile)
p=Path('/mnt/d/SteamLibrary/steamapps/workshop/content/294100/2023507013/1.6/Assemblies/VEF.dll')
a=dnfile.dnPE(str(p));wanted={'VEF.Plants.DualCropExtension','VEF.AnimalBehaviours.CompProperties_AnimalProduct'}
found=[str(t.TypeNamespace)+'.'+str(t.TypeName) for t in a.net.mdtables.TypeDef if str(t.TypeNamespace)+'.'+str(t.TypeName) in wanted]
r=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),type_names=found)
Path(__file__).with_name('raw').joinpath('vef-provider.json').write_text(json.dumps(r,indent=2)+'\n')
assert set(found)==wanted,found
print('VEF provider metadata PASS')
