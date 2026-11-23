# swim.py <evidence.json> : the bridge-down control watch, poll by poll: tick, leaf, each raider x,z and its ProofSwim words
import json,sys
d=json.load(open(sys.argv[1])); calls=d['calls']
# the control starts at the LAST lord_assault_spawn
i0=max(i for i,c in enumerate(calls) if c['tool']=='jawa/lord_assault_spawn')
pos={}; n=0
for c in calls[i0:]:
    t=c['tool']; a=c['args']; r=c['result']
    if t=='jawa/list_pawns' and isinstance(a,dict) and a.get('faction')=='hostile':
        n+=1; pos={p['id'][5:]:(p.get('x'),p.get('z')) for p in r.get('pawns',[]) if p.get('x') is not None}
        print('POLL',n,'tick',(r.get('state') or {}).get('tick'),' '.join('%s@%s,%s'%(k,v[0],v[1]) for k,v in sorted(pos.items())))
    elif t=='jawa/static_call' and a[1]=='ProofSwim':
        res=str(r.get('result'))
        if 'deepCell=True' in res or 'swimming=True' in res: print('   SWIM',a[2],res[:230])
    elif t=='jawa/static_call' and a[1]=='ProofLeaf': print('   LEAF',str(r.get('result'))[:160])
