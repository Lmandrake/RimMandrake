import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
names=sorted(x.get('name') for x in b.list_tools())
print("keys:", sorted(k for k in [])) or print("every tool containing 'ideo':", [n for n in names if 'ideo' in n.lower()])
print("keys:", sorted(k for k in [])) or print("every tool containing 'leader':", [n for n in names if 'leader' in n.lower()])
r=b.call('jawa/faction_leader_get',{}); r.pop('operation',None)
rows=r.get("rows") or r.get("leaders") or (r.get("factions") if isinstance(r.get("factions"),list) else []) or []
print("\nfaction_leader_get -> %d rows; keys=%s"%(len(rows), sorted(rows[0].keys()) if rows else '-'))
for q in rows[:4]: print("  ", json.dumps(q)[:230])
