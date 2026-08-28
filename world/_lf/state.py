import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for m in ("rimworld/get_game_state","jawa/game_info","rimworld/get_map_target_info"):
    try: print(m,"->",json.dumps(b.call(m,{}))[:600])
    except Exception as e: print(m,"ERR",e)
names=sorted(x.get("name") for x in b.list_tools())
print([n for n in names if "state" in n or "info" in n or "mod" in n][:30])
