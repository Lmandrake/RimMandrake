import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
names=sorted(x.get('name') for x in b.list_tools())
jawa=[n for n in names if n.startswith('jawa/')]
print("LIVE: %d tools total, %d jawa"%(len(names), len(jawa)))
for n in ('jawa/pawn_stats','jawa/room_get','jawa/thing_stats'):
    print("   %-20s %s"%(n, "REGISTERED" if n in names else "ABSENT"))
io.open(r"D:\Luke\dev\Rimworld\world\_lf\live_jawa_after.txt","w",encoding='utf-8').write("\n".join(jawa))
