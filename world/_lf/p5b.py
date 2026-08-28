import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
for x in b.list_tools():
    if x.get('name')=='jawa/set_pawn_identity':
        print("schema ::", json.dumps(x.get('inputSchema') or {})[:700]); print()
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
tame=[x for x in ps if x.get('isPlayer') and x.get('intelligence')!='Humanlike']
a=tame[1]; pid=a['id']
def nameof(pid):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    return pw.get('name')
print("start:", nameof(pid))
for args in ({'pawn':pid,'nameFirst':'OWNERSET'},{'pawn':pid,'nickName':'OWNERSET'},
             {'pawn':pid,'name':'OWNERSET'},{'pawn':pid,'nameShort':'OWNERSET'}):
    r=c('jawa/set_pawn_identity',args)
    print("  %-14s -> success=%s name=%-14s %s"%(list(args)[1],r.get('success'),nameof(pid),(r.get('message') or '')[:60]))
n=nameof(pid)
c('jawa/set_pawn_faction',{'pawn':pid,'faction':'none'})
c('jawa/set_pawn_faction',{'pawn':pid,'faction':'player'})
print("after none->player round trip:", nameof(pid), "| unchanged =", nameof(pid)==n)
