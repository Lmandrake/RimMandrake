import json,os,statistics as st,math,re,collections,random
S=os.path.dirname(os.path.abspath(__file__)); R=json.load(open(S+'/tickets_result.json'))
print("model",set(r['model'] for r in R),"n",len(R),"labels",collections.Counter(r['label'] for r in R))
ms=sorted(r['ms'] for r in R); tok=[r['tok'] for r in R]
print("latency ms p50 %d p90 %d max %d (6 threads); tokens in median %d sum %d out sum %d"%(ms[len(ms)//2],ms[int(len(ms)*.9)],ms[-1],st.median(tok),sum(tok),sum(r['out_tok'] for r in R)))
def auc(s,y):
    pos=[a for a,b in zip(s,y) if b==1]; neg=[a for a,b in zip(s,y) if b==0]
    return sum((p>n)+.5*(p==n) for p in pos for n in neg)/(len(pos)*len(neg))
y=[r['label'] for r in R]
pfix=[r['ans']['verdict']['p'].get('fix_it',0) for r in R]
pred=[1 if r['ans']['verdict']['choice']=='fix_it' else 0 for r in R]
acc=sum(a==b for a,b in zip(pred,y))/len(y)
tp=sum(a==1 and b==1 for a,b in zip(pred,y)); tn=sum(a==0 and b==0 for a,b in zip(pred,y))
print("verdict acc %.3f  fixed called fix_it %d/%d  nwt called nwt %d/%d  AUC p(fix_it) %.3f"%(acc,tp,sum(y),tn,len(y)-sum(y),auc(pfix,y)))
for q in ('failure_observed','predicted_only','ordinary_reach','wording_only'):
    s=[r['ans'][q]['noul'] for r in R]
    a=auc(s,y); print("%-17s AUC vs fixed %.3f  median fixed %.2f nwt %.2f"%(q,a,st.median([v for v,l in zip(s,y) if l]),st.median([v for v,l in zip(s,y) if not l])))
# calibration of the stated probability of the picked option
bins=collections.defaultdict(list)
for r,p,l in zip(R,pred,y):
    pm=max(r['ans']['verdict']['p'].values()); bins[min(int(pm*10),9)].append(p==l)
print("calibration: stated p of pick -> share right")
ece=0
for b in sorted(bins):
    v=bins[b]; mid=b/10+.05; ece+=len(v)/len(R)*abs(sum(v)/len(v)-mid); print("  %.1f-%.1f n=%3d right %.2f"%(b/10,b/10+.1,len(v),sum(v)/len(v)))
print("ECE ~ %.3f"%ece)
cb=collections.defaultdict(list)
for r,p,l in zip(R,pred,y): cb[min(int((r['ans']['verdict']['conf'] or 0)*5),4)].append(p==l)
print("confidence quintile -> right:",{ "%.1f"%(k/5):(len(v),round(sum(v)/len(v),2)) for k,v in sorted(cb.items())})
# selective prediction: act only when p(pick)>=t
for t in (.6,.7,.8,.9,.95):
    v=[(p==l) for r,p,l in zip(R,pred,y) if max(r['ans']['verdict']['p'].values())>=t]
    d=[(p,l) for r,p,l in zip(R,pred,y) if max(r['ans']['verdict']['p'].values())>=t and p==0]
    print("  act when p>=%.2f: covers %d/%d, right %.3f; drops proposed %d, of them really fixed (false drop) %d"%(t,len(v),len(R),sum(v)/max(len(v),1),len(d),sum(l for p,l in d)))
# false-drop operating points on p(nwt)
pn=[1-p for p in pfix]
for t in (.5,.7,.8,.9,.95,.98):
    sel=[l for p,l in zip(pn,y) if p>=t]; print("  p(nwt)>=%.2f: flags %d, real nwt caught %d/%d, fixed tickets wrongly flagged %d/%d"%(t,len(sel),sel.count(0),y.count(0),sel.count(1),y.count(1)))
# floors: length, and leave-one-out naive Bayes on words
print("floor: title length AUC %.3f"%auc([len(r['title']) for r in R],y))
def toks(r): return set(re.findall(r"[a-z_]{3,}",(r['title']+' '+r['filed_why']).lower()))
T=[toks(r) for r in R]; s=[]
for i in range(len(R)):
    c=[collections.Counter(),collections.Counter()]; n=[0,0]
    for j in range(len(R)):
        if j==i: continue
        n[y[j]]+=1
        for w in T[j]: c[y[j]][w]+=1
    s.append(sum(math.log((c[1][w]+1)/(n[1]+2))-math.log((c[0][w]+1)/(n[0]+2)) for w in T[i]))
print("floor: leave-one-out naive Bayes on words AUC %.3f acc %.3f"%(auc(s,y),sum((a>0)==b for a,b in zip(s,y))/len(y)))
# worst errors
E_=sorted([(max(r['ans']['verdict']['p'].values()),r) for r,p,l in zip(R,pred,y) if p!=l],key=lambda x:-x[0])
print("confident errors (top 8 of %d):"%len(E_))
for p,r in E_[:8]: print("  p=%.2f label=%s | %s || end: %s"%(p,'fixed' if r['label'] else 'nwt',r['title'][:130],r['end_reason'][:110]))
