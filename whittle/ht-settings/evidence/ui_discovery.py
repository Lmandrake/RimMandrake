import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'))
from validation_core import Bridge
b=Bridge()
r=b.call('rimworld/get_ui_layout',surfaceId='window:1:RimWorld.Dialog_ModSettings',timeoutMs=15000)
(E/'baseline_owned_layout.json').write_text(json.dumps(r,indent=2)+'\n')
r=b.call('rimworld/take_screenshot',fileName='baseline_native_settings',clipTargetId='window:1:RimWorld.Dialog_ModSettings',outputDirectory=str(E),suppressMessage=True)
(E/'baseline_owned_screenshot.json').write_text(json.dumps(r,indent=2)+'\n')
b.S.close()
