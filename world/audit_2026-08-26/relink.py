# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in json.load(open(os.path.join(A,'relink.json'),encoding='utf-8')):
    if x['to'] is None: print("NO NEIGHBOUR", x); continue
    r=b.call('jawa/world_links_set',{'kind':'road','def':x['d'],
             'path':'%d,%d'%(x['t'],x['to']),'readBack':0})
    print("%-28s %5d-%-5d %-12s %s"%(x['name'],x['t'],x['to'],x['d'],r.get('success')))
print("commit:", b.call('jawa/world_commit',{}).get('success'))
