import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
names = sorted(x.get("name") for x in b.list_tools())
import re
print("\n".join(n for n in names if re.search(r'map|gen|tile|camera|screenshot|debug_game|select', n)))
