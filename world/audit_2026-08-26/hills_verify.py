# -*- coding: utf-8 -*-
import sys, json, os, collections, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
print(json.dumps(b.call('jawa/world_tile_export',{'path':os.path.join(A,'hills_tiles.csv'),
      'format':'csv','extended':True}))[:120])
SETT=[o for o in b.call('jawa/world_objects_get',{'def':'Settlement','limit':500})['objects']]
ids=','.join(str(o['tile']) for o in SETT)
s=b.call('jawa/tile_settleable',{'tiles':ids,'examplesPerReason':4})
print("settleable:", json.dumps({k:v for k,v in s.items() if k not in ('operation','tiles')})[:420])
lint=b.call('jawa/world_lint',{'limit':4})
print("lint findings:", lint.get('totalFindings'))
for k,v in lint['checks'].items():
    n=v.get('count') if isinstance(v,dict) else None
    if n: print("   %-26s %s"%(k,n))
