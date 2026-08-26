# -*- coding: utf-8 -*-
import sys, json, os, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
P=json.load(open(os.path.join(A,'ops2.json'),encoding='utf-8'))
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(os.path.join(A,'neighbors.csv'),encoding='utf-8'))}
blocked=set()
for x in json.load(open(os.path.join(A,'final_landmarks.json'),encoding='utf-8')):
    blocked.add(x['tile']); blocked|=set(NB[x['tile']])
def place(d,cands,want):
    global blocked
    got=[]
    for tile in cands:
        if len(got)>=want: break
        if tile in blocked: continue
        r=b.call('jawa/world_landmarks_set',{'action':'add','def':d,'tiles':str(tile),'checkValid':True})
        rows=r.get('tiles') or []
        if r.get('added',0)>=1 and rows and rows[0].get('landmark')==d:
            got.append((tile,rows[0].get('landmarkName'))); blocked.add(tile); blocked|=set(NB[tile])
        elif r.get('success') is False: print("     refused:",str(r.get('message'))[:80])
    return got
print("== nine empty regions + cactus fields ==")
for j in P['jobs']:
    g=place(j['d'],j['cands'],j['want'])
    print("  %-14s %-22s %d/%d  %s"%(j['region'],j['d'],len(g),j['want'],
          ', '.join(n for _,n in g)[:60]))
print("== vegetation ==")
for v in P['veg']:
    if not v['tiles']: continue
    for i in range(0,len(v['tiles']),350):
        b.call('jawa/world_mutators_set',{'action':'add','mutators':v['d'],
               'tiles':','.join(map(str,v['tiles'][i:i+350])),'readBack':0})
    print("  %-14s %-24s %d tiles"%(v['region'],v['d'],len(v['tiles'])))
print("== relocations off settlement tiles ==")
for r_ in P['reloc']:
    cands=r_['cands']
    if not cands:   # widen to ring 3
        seen={r_['tile']}; front=[r_['tile']]
        for _ in range(3):
            nxt=[]
            for u in front:
                for v2 in NB[u]:
                    if v2 not in seen: seen.add(v2); nxt.append(v2)
            front=nxt
        cands=[x for x in front if x not in blocked]
    rem=b.call('jawa/world_landmarks_set',{'action':'remove','tiles':str(r_['tile'])})
    got=place(r_['d'],cands,1)
    print("  tile %-6d %-22s removed=%s  moved to %s"%(r_['tile'],r_['d'],rem.get('removed'),
          got[0] if got else 'NO VALID TILE FOUND (left removed)'))
print("commit:", b.call('jawa/world_commit',{}).get('success'))
