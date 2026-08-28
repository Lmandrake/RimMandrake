import sys, json, io, re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
want=('rimworld/open_window_by_type','rimworld/open_inspect_tab','rimworld/select_pawn',
      'rimworld/take_screenshot','rimworld/get_ui_layout','rimworld/get_screen_targets',
      'rimworld/scroll_ui_target','rimworld/read_ui_text','rimworld/get_ui_text')
names=[x.get('name') for x in b.list_tools()]
print("ui-ish tools:", [n for n in names if 'ui_' in n or 'window' in n or 'inspect' in n or 'text' in n])
for x in b.list_tools():
    if x.get('name') in want:
        print("###",x['name'],"::",json.dumps(x.get('inputSchema') or {})[:420])
