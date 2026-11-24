import json,sys,random,time,concurrent.futures as cf,os
S=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.expanduser('~/dev/Dispatch/providers/jev')); sys.path.insert(0,S)
from consultjev import ask
import questions as Q
pool=json.load(open(S+'/pool.json')); random.seed(20261124)
fx=pool['fixed'][:len(pool['nwt'])]; rows=pool['nwt']+fx
def one(r):
    st={"title":r['title'],"filed_why":r['filed_why'] or "(none given)"}
    try:
        a=ask(st,Q.TICKET,model=Q.MODEL)
        return dict(r,ok=True,model=a.model,tok=a.input_tokens,out_tok=a.output_tokens,ms=a.elapsed_ms,
          ans={k:{"noul":v.noul,"choice":v.choice,"conf":v.confidence,"p":v.probabilities} for k,v in a.answers.items()})
    except Exception as e: return dict(r,ok=False,err=str(e)[:300])
out=[]
with cf.ThreadPoolExecutor(6) as ex:
    for x in ex.map(one,rows): out.append(x)
json.dump(out,open(S+'/tickets_result.json','w'),indent=1)
ok=[x for x in out if x['ok']]; print("rows",len(out),"ok",len(ok),"errors",len(out)-len(ok)); 
if len(ok)<len(out): print([x['err'] for x in out if not x['ok']][:2])
