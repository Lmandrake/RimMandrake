import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=120.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
r = call("jawa/get_defs", defs="BiomeDef/RM_SeabedFloor_GreySea;WeatherDef/RM_GreySaltSnow", fields="baseWeatherCommonalities,temperatureRange,favorability,isBad,repeatable,snowRate,commonalityRainfallFactor")
for d in r.get("defs",[]): print(d.get("defName"), d.get("found"), json.dumps(d.get("fields"))[:600])
print(r.get("success"), r.get("notFound"), r.get("message"))
