import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));from validation_core import Bridge
import game_paths
b=Bridge();schemas=b.S.list_tools()
(E/'hover_schemas.json').write_text(json.dumps([s for s in schemas if 'hover' in s['name'] or 'tooltip' in s['name']],indent=2)+'\n')
r=b.call('jawa/window_list_close',action='close',typeName='RimWorld.Dialog_ModSettings')
(E/'baseline_owned_close.json').write_text(json.dumps(r,indent=2)+'\n')
r=b.call('jawa/window_list_close',action='list');(E/'baseline_windows_after.json').write_text(json.dumps(r,indent=2)+'\n')
b.S.close()
config=Path(game_paths.MODS_CONFIG).parent
files=[p for p in config.glob('*') if 'hugethings' in p.name.lower()]
for p in files:(E/('native_saved_'+p.name)).write_bytes(p.read_bytes())
print([str(p) for p in files])
