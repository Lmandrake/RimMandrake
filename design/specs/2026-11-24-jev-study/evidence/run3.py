import json,sys,os,re,time,statistics as st,concurrent.futures as cf,collections,math
S=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.expanduser('~/dev/Dispatch/providers/jev')); sys.path.insert(0,S)
from consultjev import ask
import questions as Q
P=[r for r in json.load(open(S+'/findings_pool.json')) if not re.search(r'significan|polish|\bnit\b',r['text'],re.I)]
def one(r):
    try:
        a=ask({"finding":r['text']},Q.FINDING,model=Q.MODEL)
        return dict(r,ok=True,tok=a.input_tokens,ms=a.elapsed_ms,ans={k:{"noul":v.noul,"choice":v.choice,"conf":v.confidence,"p":v.probabilities} for k,v in a.answers.items()})
    except Exception as e: return dict(r,ok=False,err=str(e)[:300])
with cf.ThreadPoolExecutor(6) as ex: F=list(ex.map(one,P))
json.dump(F,open(S+'/findings_result.json','w'),indent=1)
F=[x for x in F if x['ok']]
def auc(s,y):
    pos=[a for a,b in zip(s,y) if b==1]; neg=[a for a,b in zip(s,y) if b==0]
    return sum((p>n)+.5*(p==n) for p in pos for n in neg)/(len(pos)*len(neg))
y=[r['label'] for r in F]; pred=[int(r['ans']['verdict']['choice']=='significant') for r in F]
print("FINDINGS n",len(F),"sig",sum(y),"polish",len(y)-sum(y),"errors",len(P)-len(F))
print(" acc %.3f sig kept %d/%d polish caught %d/%d AUC %.3f concrete AUC %.3f measured AUC %.3f"%(sum(a==b for a,b in zip(pred,y))/len(y),sum(a and b for a,b in zip(pred,y)),sum(y),sum((not a)and(not b) for a,b in zip(pred,y)),len(y)-sum(y),auc([r['ans']['verdict']['p'].get('significant',0) for r in F],y),auc([r['ans']['concrete_case']['noul'] for r in F],y),auc([r['ans']['measured']['noul'] for r in F],y)))
for lo in (.5,.7,.9):
    v=[(p==l) for r,p,l in zip(F,pred,y) if lo<=max(r['ans']['verdict']['p'].values())<(lo+.2 if lo<.9 else 1.01)]; print("  stated p %.1f+: n=%d right %.2f"%(lo,len(v),sum(v)/max(1,len(v))))
T=[set(re.findall(r"[a-z_]{3,}",r['text'].lower())) for r in F]; s=[]
for i in range(len(F)):
    c=[collections.Counter(),collections.Counter()]; n=[0,0]
    for j in range(len(F)):
        if j==i: continue
        n[y[j]]+=1
        for w in T[j]: c[y[j]][w]+=1
    s.append(sum(math.log((c[1][w]+1)/(n[1]+2))-math.log((c[0][w]+1)/(n[0]+2)) for w in T[i]))
print("  floor NB leave-one-out AUC %.3f acc %.3f"%(auc(s,y),sum((a>0)==b for a,b in zip(s,y))/len(y)))
# latency: serial, 1 question vs 5 vs 15
st0={"title":"FlowWorks sc_hole_prison: once in two runs a warden gets no DeliverFood job for a hungry prisoner","filed_why":"visit 5: FAIL then PASS"}
def lat(qs,n=12):
    ms=[];tok=0
    for _ in range(n):
        a=ask(st0,qs,model=Q.MODEL); ms.append(a.elapsed_ms); tok=a.input_tokens
    ms.sort(); return ms[len(ms)//2],ms[-2],tok
one_q={"verdict":Q.TICKET["verdict"]}
fifteen={("%s_%d"%(k,i)):v for i in range(3) for k,v in Q.TICKET.items()}
print("LATENCY serial (p50, 2nd-worst, input tokens): 1q",lat(one_q),"5q",lat(Q.TICKET),"15q",lat(fifteen))
# play-time sample: determinism and sensitivity
base={"resident":{"name":"Orra Venn","role":"refinery foreman","traits":["gruff","loyal to the crew","distrusts offworlders"]},"place":"a small oil refinery in the desert, crew of nine, two guards","event":"A gravship lands 200 metres away and four armed strangers step out."}
runs=[ask(base,{"react":Q.REACT,"mood":Q.MOOD},model=Q.MODEL) for _ in range(10)]
print("PLAY same state x10: picks",collections.Counter(r['react'].choice for r in runs),"p(pick) min/max %.4f/%.4f"%(min(max(r['react'].probabilities.values()) for r in runs),max(max(r['react'].probabilities.values()) for r in runs)),"mood min/max %.3f/%.3f"%(min(r['mood'].score for r in runs),max(r['mood'].score for r in runs)),"ms p50",st.median(r.elapsed_ms for r in runs),"tokens",runs[0].input_tokens)
print(" base probs",{k:round(v,3) for k,v in runs[0]['react'].probabilities.items()})
var=[("trader, greedy, curious","A gravship lands 200 metres away and four armed strangers step out."),("drudge, timid, owes a debt","A gravship lands 200 metres away and four armed strangers step out."),("guard, brave, bored","A gravship lands 200 metres away and four armed strangers step out."),("refinery foreman, gruff","The newcomers shot a guard an hour ago and are walking toward the barracks."),("refinery foreman, gruff","Two unarmed travellers walk up on foot at noon, carrying trade goods.")]
for tr,evn in var:
    s2=dict(base,resident={"name":"X","role":tr.split(',')[0],"traits":[t.strip() for t in tr.split(',')[1:]]},event=evn)
    a=ask(s2,{"react":Q.REACT,"mood":Q.MOOD},model=Q.MODEL)
    print("  %-28s | %-60s -> %s p=%.2f conf=%.2f mood=%.2f"%(tr,evn[:60],a['react'].choice,max(a['react'].probabilities.values()),a['react'].confidence,a['mood'].score))
