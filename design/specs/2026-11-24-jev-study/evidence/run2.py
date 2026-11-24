import json,sys,os,concurrent.futures as cf
S=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.expanduser('~/dev/Dispatch/providers/jev')); sys.path.insert(0,S)
from consultjev import ask
import questions as Q
pool=json.load(open(S+'/pool.json')); done={r['id']:r for r in json.load(open(S+'/tickets_result.json'))}
rows=[r for r in pool['fixed'] if r['kind'] in('bug','fix') and r['id'] not in done]
def one(r):
    try:
        a=ask({"title":r['title'],"filed_why":r['filed_why'] or "(none given)"},Q.TICKET,model=Q.MODEL)
        return dict(r,ok=True,model=a.model,tok=a.input_tokens,out_tok=a.output_tokens,ms=a.elapsed_ms,ans={k:{"noul":v.noul,"choice":v.choice,"conf":v.confidence,"p":v.probabilities} for k,v in a.answers.items()})
    except Exception as e: return dict(r,ok=False,err=str(e)[:300])
with cf.ThreadPoolExecutor(6) as ex: out=list(ex.map(one,rows))
print("new",len(out),"errors",sum(not x['ok'] for x in out))
allr=list(done.values())+[x for x in out if x['ok']]
json.dump(allr,open(S+'/tickets_result_all.json','w'),indent=1)
