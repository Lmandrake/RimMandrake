import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=120.0); S.connect()
r = S.call("rimworld/get_cells_info", {"x":121,"z":189,"width":2,"height":2})
print(json.dumps(r)[:1500])
