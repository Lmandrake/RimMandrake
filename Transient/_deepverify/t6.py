import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=120); b.connect()
r=b.call("jawa/get_defs",{"defs":"PawnKindDef/RSW_BloodropMoth;PawnKindDef/RSW_ShatterjawBeetle","fields":"defName,label"},check=False); print(json.dumps({k:v for k,v in r.items() if k!="operation"})[:400])
