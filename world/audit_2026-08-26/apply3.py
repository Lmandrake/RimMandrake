# -*- coding: utf-8 -*-
import sys, json, os, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
ops=json.load(open(os.path.join(A,'ops3.json'),encoding='utf-8'))
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(os.path.join(A,'neighbors.csv'),encoding='utf-8'))}
blocked=set()
for x in json.load(open(os.path.join(A,'now_landmarks.json'),encoding='utf-8')):
    blocked.add(x['tile']); blocked|=set(NB[x['tile']])
fails=[]
def call(tool,par):
    try:
        r=b.call(tool,par)
        if isinstance(r,dict) and r.get('success') is False: fails.append((tool,str(par)[:60],str(r.get('message'))[:110]))
        return r
    except Exception as e:
        fails.append((tool,str(par)[:60],str(e)[:110])); return {}
def chunks(x,n):
    for i in range(0,len(x),n): yield x[i:i+n]
# phase 1: landmark removals, then mutator removals, then mutator adds
for o in ops:
    if o['kind']=='lmk_remove':
        for t_ in o['tiles']:
            call('jawa/world_landmarks_set',{'action':'remove','tiles':str(t_)})
            blocked.discard(t_)
        print("%-14s LMK REMOVE %d"%(o['p'],len(o['tiles'])))
for o in ops:
    if o['kind']=='mut' and o['action']=='remove':
        for c in chunks(o['tiles'],300):
            call('jawa/world_mutators_set',{'action':'remove','mutators':o['d'],'tiles':','.join(map(str,c)),'readBack':0})
        print("%-14s REMOVE %-28s %d"%(o['p'],o['d'],len(o['tiles'])))
for o in ops:
    if o['kind']=='mut' and o['action']=='add':
        for c in chunks(o['tiles'],300):
            call('jawa/world_mutators_set',{'action':'add','mutators':o['d'],'tiles':','.join(map(str,c)),'readBack':0})
        print("%-14s add    %-28s %d"%(o['p'],o['d'],len(o['tiles'])))
# phase 2: landmarks, one at a time
placed=[]
for o in ops:
    if o['kind']!='lmk': continue
    got=0
    for tile in o['candidates']:
        if got>=o['want']: break
        if tile in blocked: continue
        r=call('jawa/world_landmarks_set',{'action':'add','def':o['d'],'tiles':str(tile),'checkValid':True})
        rows=r.get('tiles') or []
        if r.get('added',0)>=1 and rows and rows[0].get('landmark')==o['d']:
            got+=1; placed.append([o['d'],tile,rows[0].get('landmarkName')])
            blocked.add(tile); blocked|=set(NB[tile])
    print("%-14s LMK    %-28s %d/%d"%(o['p'],o['d'],got,o['want']))
print("commit:", call('jawa/world_commit',{}).get('success'))
json.dump(placed,open(os.path.join(A,'placed3.json'),'w'))
print("failures:",len(fails))
for x in fails[:12]: print("   ",x)
