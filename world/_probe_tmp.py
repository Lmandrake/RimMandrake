import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint()
b = rc.RimBridge(host=h, port=p, token=t); b.connect()
tools = b._request('tools/list',{})
if isinstance(tools, dict): tools = tools.get('tools', tools)
with io.open(r"D:\Luke\dev\Rimworld\world\_audit\tools.json","w",encoding="utf-8") as f:
    json.dump(tools, f, ensure_ascii=False, indent=1)
print("wrote", len(tools))
