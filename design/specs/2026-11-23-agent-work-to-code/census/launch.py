import pickle,os,re,glob
from collections import Counter,defaultdict
R=pickle.load(open('rows.pkl','rb'))
D='/mnt/d/ClaudeWork/rimmandrake/dispatcher/'
lb={re.sub(r'-\d+\.md$','',os.path.basename(f)) for f in glob.glob(D+'list_dispatch/briefs/*')}
C=Counter();N=Counter();ex=defaultdict(list)
for r in R:
    try:b=open(r['brief']).read()
    except Exception: b=''
    if re.search(r'Shape list item|Shape stage\)',b): k='list: Shape run'
    elif 'list lane' in b[:3000] or r['item'] in lb: k='list: Work run (program launched)'
    elif re.search(r'red_dispatch|nightly red|NIGHTLY_COP',b[:2500]): k='red dispatch'
    elif re.search(r'continuation|carried on|LEFT OPEN',b[:600]): k='continuation'
    elif r['env'].get('RM_CONTROL_STAGE'): k='tick: '+r['env']['RM_CONTROL_STAGE']
    elif 'follow-through audit' in b or 'Audit' in b[:300]: k='audit'
    else: k='by hand (Conductor brief)'
    C[k]+=r['t'] or 0;N[k]+=1;ex[k].append(r['item'][:70])
for k,v in C.most_common(): print('%7.1fM n=%d avg %.2fM %s %s'%(v/1e6,N[k],v/N[k]/1e6,k,ex[k][:3]))
# token by same item relaunch
it=Counter(r['item'] for r in R);print('items',len(it),'multi',sum(v>1 for v in it.values()), 'runs in multi',sum(v for v in it.values() if v>1))
st=Counter((r['result'] or '')[:40] for r in R);print(st.most_common(8))
