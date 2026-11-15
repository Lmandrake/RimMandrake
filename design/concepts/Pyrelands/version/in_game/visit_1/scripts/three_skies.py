"""Visit 1 three-skies experiment (sc_three_skies clauses the cinderfall/blackrain chains do not read). Paused-step only."""
import sys, json, os, shutil
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
S="RimMandrake.Pyrelands.RM_PyrelandsSettings"; ASH="RimMandrake.Pyrelands.PyrelandsAsh"
OFF=["burnLineEnabled","fireHawkSpreadEnabled","fireClockEnabled","burrowOnFireEnabled","furnaceThermalEnabled"]
out={}
with RimBridge(h,p,tk) as rb:
    prior={f: rb.call("jawa/mod_settings_field",{"typeName":S,"action":"get","field":f}).get("value") for f in OFF}
    for f in OFF: rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":f,"value":"False"})
    def fires():
        r=rb.call("jawa/list_things",{"defName":"Fire","limit":1}); return r.get("countMatched")
    def adv(n):
        left=n
        while left>0:
            s=min(2500,left); r=rb.call("jawa/safe_advance",{"ticks":s,"timeException":False}); left-=s
            if r.get("state")!="done": return r
    def ash(rect): return rb.call("jawa/static_call",{"type":ASH,"method":"ProbeAsh","args":rect}).get("result")
    W="0,0,250,250"
    try:
        # lightning: count fires appearing per 1000 ticks under each sky, extinguishing between reads
        for w in ("RM_FE_Weather_AshFall","RM_FE_Weather_Cinderfall"):
            rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
            rb.call("jawa/weather_set",{"weather":w,"lockWeather":True})
            seen=[]
            for i in range(10):
                adv(1000); n=fires(); seen.append(n)
                if n: rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
            out["fires_per_1000_"+w]=seen; print(w, seen)
        # black rain washes ash: lay ash on a patch under AshFall first? read a patch's depth, then 2500 ticks of black rain
        rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
        P="100,100,30,30"
        rb.call("jawa/weather_set",{"weather":"RM_FE_Weather_AshFall","lockWeather":True}); adv(2500)
        a0=ash(P); rb.call("jawa/weather_set",{"weather":"RM_FE_BlackRain","lockWeather":True}); adv(2500); a1=ash(P); adv(2500); a2=ash(P)
        out["ash_patch_ashfall_then_blackrain"]=[a0,a1,a2]; print("ash", a0, "|", a1, "|", a2)
        # fires out under black rain vs clear: same pad, sequentially
        for w in ("RM_FE_BlackRain","Clear"):
            rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
            rb.call("jawa/weather_set",{"weather":w,"lockWeather":True}); adv(300)
            r=rb.call("jawa/map_fire",{"action":"start","rect":"150,40,8,8","fireSize":1.2})
            ser=[fires()]
            for i in range(6): adv(250); ser.append(fires())
            out["fires_after_ignition_"+w]=ser; print(w, r.get("firesStarted"), ser)
        rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
        # captures: same frame under four skies (vanilla Rain the control)
        os.makedirs(r"Transient\pv1\shots", exist_ok=True)
        for w in ("RM_FE_Weather_AshFall","RM_FE_Weather_Cinderfall","RM_FE_BlackRain","Rain"):
            rb.call("jawa/weather_set",{"weather":w,"lockWeather":True}); adv(600)
            rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":110,"z":115})
            rb.call("rimworld/frame_cell_rect",{"x":95,"z":100,"width":30,"height":30,"paddingCells":2})
            s=rb.call("rimworld/take_screenshot",{"fileName":"sky_"+w}); pth=s.get("path")
            shutil.copy(pth, os.path.join(r"Transient\pv1\shots", os.path.basename(pth))); print("shot", w)
    finally:
        rb.call("jawa/map_fire",{"action":"extinguish","rect":W})
        rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True}); adv(60)
        rb.call("jawa/weather_set",{"unlock":True})
        for f,v in prior.items(): rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":f,"value":str(v)})
        print("restored", prior)
json.dump(out, open(r"Transient\pv1\three_skies.json","w"), indent=1)
