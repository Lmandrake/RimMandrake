import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=120); b.connect()
r=b.call("jawa/mod_settings_field",{"typeName":"RimMandrake.Utinni.LanternDeeps.LanternDeepsSettings","action":"list"},check=False); print(json.dumps({k:v for k,v in r.items() if k!="operation"})[:700])
r=b.call("jawa/type_probe",{"typeName":"RimMandrake.Utinni.LanternDeeps.MapComponent_LanternDeepDarkness"},check=False); print(json.dumps({k:v for k,v in r.items() if k!="operation"})[:600])
b.call("jawa/set_current_map",{"mapId":4},check=False)
r=b.call("jawa/inspect_string",{"defName":"Campfire","limit":2},check=False); print(json.dumps({k:v for k,v in r.items() if k!="operation"})[:500])
