# -*- coding: utf-8 -*-
import sys, json, os, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(os.path.join(A,'neighbors.csv'),encoding='utf-8'))}
blocked=set()
for x in json.load(open(os.path.join(A,'final_landmarks.json'),encoding='utf-8')):
    blocked.add(x['tile']); blocked|=set(NB[x['tile']])
for j in json.load(open(os.path.join(A,'fill2.json'),encoding='utf-8')):
    got=0
    for tile in j['cands']:
        if got>=j['want']: break
        if tile in blocked: continue
        r=b.call('jawa/world_landmarks_set',{'action':'add','def':j['d'],'tiles':str(tile),'checkValid':True})
        rows=r.get('tiles') or []
        if r.get('added',0)>=1 and rows and rows[0].get('landmark')==j['d']:
            got+=1; blocked.add(tile); blocked|=set(NB[tile])
        elif r.get('success') is False: print("  refused:",str(r.get('message'))[:90])
    print("%-22s %d/%d"%(j['d'],got,j['want']))
print("commit:", b.call('jawa/world_commit',{}).get('success'))
