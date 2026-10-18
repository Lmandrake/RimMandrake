import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack")
import validation as V
B = V.Bridge()
AT = "RimMandrake.GimmeSomeSlack.Aerial.AerialSettings"
GT = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings"
G = ["enabled","tangles","needlessLoops","diveThrough","breakReadout","hideHookupWires","whip","downedWire","highlight","sway","lod","floorRipple"]
A = ["enabled","explosionsCut","kineticSway","tapsEnabled","tapEvents","autoLink"]
def get(t,f): return B.call("jawa/mod_settings_field", typeName=t, action="get", field=f)
def setv(t,f,v):
    if t==GT: return B.probe("set:%s=%s"%(f,v))
    return B.call("jawa/mod_settings_field", typeName=t, action="set", field=f, value=v)
orig = {}
for t,fs in ((GT,G),(AT,A)):
    for f in fs:
        r = get(t,f); orig[(t,f)] = r.get("value"); 
print("orig", {k[1]+"@"+k[0][-8:]:v for k,v in orig.items()})
res = {"orig": {t.split(".")[-1]+"."+f: v for (t,f),v in orig.items()}}
def snap(tag):
    c = B.probe("census")
    keep = {k: c.get(k) for k in ("success","enabled","invisibleApplied","texPaths","hookupWiresSuppressed","layerVisible","layerVerts","builds","pieces","ticksGame")}
    res[tag] = keep; print(tag, json.dumps(keep))
snap("before")
for (t,f) in orig:
    if orig[(t,f)] is None: continue
    setv(t,f,"False")
B.ticks(2); time.sleep(1); snap("all_off")
rb = {t.split(".")[-1]+"."+f: get(t,f).get("value") for (t,f) in orig}
res["readback_off"] = rb
for (t,f) in orig:
    if orig[(t,f)] is None: continue
    setv(t,f,"True")
B.ticks(2); time.sleep(1); snap("all_on")
res["readback_on"] = {t.split(".")[-1]+"."+f: get(t,f).get("value") for (t,f) in orig}
for (t,f),v in orig.items():
    if v is not None: setv(t,f,str(v))
res["restored"] = {t.split(".")[-1]+"."+f: get(t,f).get("value") for (t,f) in orig}
json.dump(res, open("Transient/bench_live_20261018/gss_settings_round_apply.json","w"), indent=1)
print("restored", res["restored"])
