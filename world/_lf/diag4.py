# -*- coding: utf-8 -*-
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
names=sorted(x.get("name") for x in b.list_tools())
print("list_colonists present:", 'rimworld/list_colonists' in names,
      "| candidates:", [n for n in names if 'list_' in n][:12])
lc=c('rimworld/list_colonists')
rows=lc.get('colonists') or lc.get('pawns') or []
print("list_colonists -> %d rows; keys=%s"%(len(rows), sorted(rows[0].keys()) if rows else '-'))
for q in rows[:3]: print("   ", {k:q.get(k) for k in list(q)[:6]})

ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
cnt=collections.Counter(x.get('name') for x in ps)
uniq_animals=[x for x in ps if not x.get('factionName') and cnt[x.get('name')]==1]
print("\nuniquely-named animals on map:", len(uniq_animals))
for a in uniq_animals[:4]:
    r=c('rimworld/jump_camera_to_pawn',{'pawnName':a['name']})
    print("  ANIMAL pawnName=%-24s -> success=%s  %s"%(a['name'],r.get('success'),(r.get('message') or '')[:60]))
# and a colonist id from list_colonists, if any
if rows:
    idk=[k for k in rows[0] if 'id' in k.lower()]
    for k in idk:
        r=c('rimworld/jump_camera_to_pawn',{'pawnId':str(rows[0][k])})
        print("  COLONIST pawnId(%s)=%-14s -> success=%s %s"%(k,str(rows[0][k])[:14],r.get('success'),(r.get('message') or '')[:60]))
