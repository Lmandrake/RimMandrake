# -*- coding: utf-8 -*-
import sys, json, os, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
print(json.dumps(b.call('jawa/world_tile_export',
      {'path':os.path.join(A,'final_tiles.csv'),'format':'csv','extended':True}))[:180])
N=21872; mut=[]
for s in range(0,N,1000):
    r=b.call('jawa/world_mutators_get',{'range':'%d-%d'%(s,min(s+1000,N)-1),'onlyWithMutators':True,'limit':5000})
    mut+= (r.get('tiles') or [])
json.dump(mut, open(os.path.join(A,'final_mutators.json'),'w'))
lm=b.call('jawa/world_landmarks_get',{'limit':30000})
json.dump(lm['landmarks'], open(os.path.join(A,'final_landmarks.json'),'w'))
print("mutated tiles",len(mut),"landmarks",lm['count'])
