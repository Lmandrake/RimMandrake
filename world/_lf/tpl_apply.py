# -*- coding: utf-8 -*-
"""TEMPLATE_ENGINE_ACCEPTANCE_1 - issue the dwelling and read every cell back OUT OF THE ENGINE."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
R=r"D:\Luke\dev\Rimworld\world\_lf"
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}

calls=json.load(open(R+r"\tpl_calls.json"))
plan =json.load(open(R+r"\tpl_plan.json"))

# --- translate rect -> ops for the two tools whose live schema has no `rect`
def translate(call):
    tool, prm = call['tool'], dict(call['params'])
    if tool in ('jawa/set_terrain_batch','jawa/set_roof_batch') and 'rect' in prm:
        d = prm.pop('terrainDef', None) or prm.pop('roofDef', None)
        prm = {'ops': '%s:%s' % (d, prm.pop('rect'))}
    return tool, prm

log=[]
print("=== issuing %d calls ==="%len(calls))
for call in calls:
    tool, prm = translate(call)
    r=c(tool, prm)
    log.append({'tool':tool,'params':prm,'reply':r})
    print("  %-26s success=%-5s %s"%(tool, r.get('success'), (r.get('message') or '')[:88]))
json.dump(log, open(R+r"\tpl_apply_log.json","w"), indent=1)

# --- READ BACK, criterion 4: every planned cell, out of the engine
print("\n=== criterion 4: plan vs map, read back cell by cell ===")
want_t={}
for e in plan['terrain']:
    want_t[(e['x'],e['z'])]=e.get('def') or e.get('terrain') or e.get('defName')
want_th=collections.defaultdict(list)
for e in plan['things']:
    want_th[(e['x'],e['z'])].append(e.get('def') or e.get('defName'))
got_t={}; got_th=collections.defaultdict(list); got_roof={}
X0,Z0,W,H=170,170,18,10
for z in range(Z0,Z0+H):
    r=c('rimworld/get_cells_info',{'x':X0,'z':z,'width':W,'height':1})
    for cell in (r.get('cells') or []):
        k=(cell['x'],cell['z'])
        got_t[k]=cell.get('terrainDefName')
        got_roof[k]=cell.get('roofDefName')
        got_th[k]=[d for d in (cell.get('solidThingDefs') or [])]
tmiss=[(k,v,got_t.get(k)) for k,v in want_t.items() if got_t.get(k)!=v]
thmiss=[(k,v,got_th.get(k)) for k,v in want_th.items() if not set(v)<=set(got_th.get(k) or [])]
roofed=sum(1 for k in got_roof if got_roof[k])
print("  terrain planned %d | mismatched %d"%(len(want_t),len(tmiss)))
for k,w_,g in tmiss[:6]: print("     %s want=%-22s got=%s"%(k,w_,g))
print("  thing cells planned %d | missing/wrong %d"%(len(want_th),len(thmiss)))
for k,w_,g in thmiss[:8]: print("     %s want=%-22s got=%s"%(k,w_,g))
print("  roof planned %d | cells roofed now %d"%(len(plan['roof']),roofed))
print("\n=== criterion 3: refusals ===")
print("  plan refusals:", plan.get('refusals'), "| plan notes:", plan.get('notes'))
for e in log:
    rp=e['reply']
    for key in ('placed','requested','refused','changed','failed','skipped'):
        if key in rp: print("   %-26s %s=%s"%(e['tool'],key,json.dumps(rp[key])[:120]))
json.dump({'tmiss':[[list(k),w,g] for k,w,g in tmiss],
           'thmiss':[[list(k),w,g] for k,w,g in thmiss]},
          open(R+r"\tpl_readback.json","w"), indent=1)
