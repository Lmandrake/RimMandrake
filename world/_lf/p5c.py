import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
def nameof(pid):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    return pw.get('name')
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
tame=[x for x in ps if x.get('isPlayer') and x.get('intelligence')!='Humanlike']
pid=tame[1]['id']
print("taming-assigned :", nameof(pid))
r=c('jawa/set_pawn_identity',{'pawn':pid,'single':'OWNERSET_KEEPME'})
print("player rename   :", nameof(pid), "(success=%s)"%r.get('success'))
c('jawa/set_pawn_faction',{'pawn':pid,'faction':'none'})
c('jawa/set_pawn_faction',{'pawn':pid,'faction':'player'})
n=nameof(pid)
print("re-tamed        :", n, "  => P5", "PASS - a player-set name is not overwritten" if n=='OWNERSET_KEEPME' else "FAIL")
