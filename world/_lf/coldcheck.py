import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
for pid in ('Human58390','Human58394'):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    pos=pw.get('position') or {}
    ct=c('jawa/cell_temperature',{'cell':'%s,%s'%(pos.get('x'),pos.get('z'))})
    print("%s xeno=%-16s pos=%s dead=%s"%(pid, pw.get('xenotype'), pos, pw.get('dead')))
    print("   cell temp there: %.1f  (outdoor %.1f)"%(ct.get('temperature') or 0, ct.get('outdoorTemp') or 0))
    print("   apparel: %s"%json.dumps([a.get('def') for a in (pw.get('apparel') or [])]))
    print("   ALL hediffs: %s"%json.dumps(pw.get('hediffs'))[:500])
    print()
# and a control: the list_pawns health view
r=c('jawa/list_pawns',{'includeHealth':True,'limit':400,'faction':'none'})
ps=[x for x in (r.get('pawns') or []) if x.get('id') in ('Human58390','Human58394')]
for x in ps:
    print("list_pawns includeHealth ->", json.dumps({k:v for k,v in x.items() if 'ealth' in k or k=='id'})[:400])
