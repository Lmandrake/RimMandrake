# -*- coding: utf-8 -*-
import sys, json, io, re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
j=[x for x in ps if x.get('kindDef')=='Jawa_Tribal_Scavenger'][0]
print("select:", c('rimworld/select_pawn',{'pawnId':'Thing_'+j['id']}).get('success'), j['name'])
print("inspect_string:", json.dumps(c('jawa/inspect_string',{'pawn':j['id']}))[:300])
for wt in ('Dialog_InfoCard','RimWorld.Dialog_InfoCard'):
    r=c('rimworld/open_window_by_type',{'windowType':wt})
    print("open %s -> %s %s"%(wt, r.get('success'), (r.get('message') or '')[:100]))
    if r.get('success'): break
st=c('rimworld/get_screen_targets')
tg=[x for x in (st.get('targets') or st.get('windows') or []) if 'InfoCard' in json.dumps(x)]
print("info-card target:", json.dumps(tg)[:250])
lay=c('rimworld/get_ui_layout', {'surfaceId':(tg[0].get('id') if tg else None)} if tg else {})
s=json.dumps(lay)
m=re.findall(r'[^"]*[Cc]omfortable[^"]*', s)[:6]
print("layout bytes:", len(s), "| comfortable hits:", m[:4])
open(r"D:\Luke\dev\Rimworld\world\_lf\infocard_layout.json","w",encoding='utf-8').write(s)
