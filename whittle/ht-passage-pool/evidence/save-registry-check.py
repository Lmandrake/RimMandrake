"""Tie the existing test-site inventory to its registered biome, without guessing short hashes."""
import json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3];e=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import biomes_compose as B
registry=root/'src/RimMandrake/Utils/modcheck/test_site_saves.json'
r=json.loads(registry.read_text())
inv=json.loads((e/'save-inventory-focused.json').read_text())
fmap=B.folded_ids(str(root/'src'))
out={'registry_path':str(registry),'registry_sha256':hashlib.sha256(registry.read_bytes()).hexdigest(),
     'Stillsand_source_package':'mandrake.rm.stillsand',
     'Stillsand_effective_owning_package':fmap.get('mandrake.rm.stillsand','mandrake.rm.stillsand'),
     'existing_registered_sites':[], 'limit':'Registry is a saved historical measurement, not a fresh live map read; no shortHash lookup used.'}
for s in inv['saves']:
 name=Path(s['path']).stem
 entries=[{'site':k,**v} for k,v in r.items() if v.get('save')==name]
 out['existing_registered_sites'].append({'save':name,'sha256':s['sha256'],'bytes':s['bytes'],'registry_entries':entries,
     'owning_content_in_saved_header':out['Stillsand_effective_owning_package'] in s['modIds']})
(e/'save-registry-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
