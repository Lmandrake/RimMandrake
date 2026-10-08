import sys, os, json
U=os.path.join(os.getcwd(),"src","RimMandrake","Utils")
sys.path.insert(0,U)
import rimbridge_client as rb
h,p,t=rb.resolve_endpoint(); c=rb.RimBridge(host=h,port=p,token=t,timeout=60.0); c.connect()
tool=sys.argv[1]; args=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
r=c.call(tool,args)
if isinstance(r,dict) and r.get("content"):
    r=json.loads(r["content"][0]["text"])
print(json.dumps(r))
