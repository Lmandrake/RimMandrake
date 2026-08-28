# -*- coding: utf-8 -*-
"""J7: a droid raid arrives with no NRE naming Pawn_RelationsTracker. Game stays PAUSED."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
for x in b.list_tools():
    if x.get('name')=='jawa/fire_raid':
        print("fire_raid keys:", sorted((x.get('inputSchema',{}).get('properties') or {}).keys()))
print("paused before:", c('rimworld/get_cell_info',{'x':125,'z':125}).get('state',{}).get('paused'))
before={x['id'] for x in (c('jawa/list_pawns',{'limit':999}).get('pawns') or [])}
r=c('jawa/fire_raid',{'faction':'Jawa_FreeDroidEnclaves','points':400,'spawnCenter':'5,5','dryRun':False})
print("fire_raid ->", r.get('success'), (r.get('message') or json.dumps(r))[:220])
after=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
new=[x for x in after if x['id'] not in before]
print("raiders that arrived:", len(new))
import collections
print(dict(collections.Counter((x.get('kindDef'),x.get('factionName')) for x in new)))
print("paused after:", c('rimworld/get_cell_info',{'x':125,'z':125}).get('state',{}).get('paused'))
