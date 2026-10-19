import json,os,sys
HERE=os.path.dirname(os.path.abspath(__file__))
UT=os.path.join(HERE,"..","..","src","RimMandrake","Utils")
sys.path.insert(0,UT)
from rimbridge_client import RimBridge, resolve_endpoint
ports=json.load(open(os.path.join(HERE,"ports_list.json")))
h,p,t=resolve_endpoint()
res={}
items=sorted(ports.items())
with RimBridge(h,p,t,timeout=120.0) as rb:
    for i in range(0,len(items),40):
        chunk=items[i:i+40]
        r=rb.call("jawa/get_defs",{"defs":";".join("%s/%s"%(v,k) for k,v in chunk),"fields":"defName,label"})
        if i==0: print(json.dumps(r)[:900])
        res[i]=r
json.dump(res,open(os.path.join(HERE,"a2_raw.json"),"w"),indent=1,default=str)
