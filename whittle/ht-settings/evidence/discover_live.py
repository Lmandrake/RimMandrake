import sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'))
from validation_core import Bridge
b=Bridge();tools=b.S.list_tools()
wanted=['rimworld/get_mod_settings','rimworld/open_mod_settings','rimworld/get_ui_layout','rimworld/scroll_ui_target','rimworld/take_screenshot','rimworld/get_ui_state','jawa/window_list_close','jawa/mod_settings_field','jawa/static_call']
(E/'live_schemas.json').write_text(json.dumps([t for t in tools if t.get('name') in wanted],indent=2)+'\n')
(E/'tool_census.json').write_text(json.dumps({'total':len(tools),'jawa':sum(t.get('name','').startswith('jawa/') for t in tools)},indent=2)+'\n')
for name,tool,p in [('baseline_windows','jawa/window_list_close',{'action':'list'}),('baseline_ui','rimworld/get_ui_state',{}),('baseline_semantic','rimworld/get_mod_settings',{'modId':'RimMandrake.HugeThings.RM_HugeThingsMod'}),('baseline_fields','jawa/mod_settings_field',{'typeName':'RimMandrake.HugeThings.RM_HugeThingsSettings','action':'list'})]:
 r=b.call(tool,**p);(E/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(name,r.get('success'),flush=True)
b.S.close()
