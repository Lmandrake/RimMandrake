# -*- coding: utf-8 -*-
import sys, json, os, csv, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
P=json.load(open(os.path.join(A,'wither_plan.json'),encoding='utf-8'))
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(os.path.join(A,'neighbors.csv'),encoding='utf-8'))}
struct=P['struct']; assign={int(k):v for k,v in P['assign'].items()}
def chunks(x,n):
    for i in range(0,len(x),n): yield x[i:i+n]
# 1. strip landmarks off the spine
for t_ in P['lm_on_struct']:
    b.call('jawa/world_landmarks_set',{'action':'remove','tiles':str(t_)})
print("landmarks removed from the spine:", len(P['lm_on_struct']))
# 2. clear EVERY mutator off the spine
for c in chunks(struct,300):
    b.call('jawa/world_mutators_set',{'action':'clear','tiles':','.join(map(str,c)),'readBack':0})
print("mutators cleared on", len(struct), "tiles")
# 3. and pull the scars off the rest of Wither too
if P['scars_elsewhere']:
    b.call('jawa/world_mutators_set',{'action':'remove','mutators':'TerraformingScar',
           'tiles':','.join(map(str,P['scars_elsewhere'])),'readBack':0})
    print("scars removed elsewhere in Wither:", len(P['scars_elsewhere']))
# 4. raise the whole spine to Mountainous so canyon defs are legal at all
b.call('jawa/world_tile_set',{'tiles':','.join(map(str,struct)),'hilliness':'Mountainous','readBack':0})
print("spine raised to Mountainous")
# 5. one Mountain-category canyon def per tile
byd=collections.defaultdict(list)
for t_,d in assign.items(): byd[d].append(t_)
for d,ts in byd.items():
    for c in chunks(sorted(ts),300):
        b.call('jawa/world_mutators_set',{'action':'add','mutators':d,'tiles':','.join(map(str,c)),'readBack':0})
    print("  %-24s %d tiles"%(d,len(ts)))
# 6. non-conflicting texture
for d,ts in P['extra'].items():
    for c in chunks(sorted(ts),300):
        b.call('jawa/world_mutators_set',{'action':'add','mutators':d,'tiles':','.join(map(str,c)),'readBack':0})
    print("  %-24s %d tiles (texture)"%(d,len(ts)))
# 7. landmarks along the spine, spaced
blocked=set()
for x in b.call('jawa/world_landmarks_get',{'limit':30000})['landmarks']:
    blocked.add(x['tile']); blocked|=set(NB[x['tile']])
placed=[]
for d,want in (('VEE_SerpentineCanyons',4),('Chasm',3),('Cavern',2),('Hollow',1)):
    got=0
    for t_ in P['order']:
        if got>=want: break
        if t_ in blocked or assign.get(t_)!=d: continue
        r=b.call('jawa/world_landmarks_set',{'action':'add','def':d,'tiles':str(t_),'checkValid':True})
        rows=r.get('tiles') or []
        if r.get('added',0)>=1 and rows and rows[0].get('landmark')==d:
            got+=1; placed.append([d,t_,rows[0].get('landmarkName')])
            blocked.add(t_); blocked|=set(NB[t_])
    print("  LMK %-24s %d/%d"%(d,got,want))
print("commit:", b.call('jawa/world_commit',{}).get('success'))
json.dump(placed,open(os.path.join(A,'wither_placed.json'),'w'))
