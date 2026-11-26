"""sc_grass_regreens, resumable: the embergrass_regrow chain's own steps (same pad, cohort, burn, thresholds, real clock),
split across foreground calls of <= BUDGET_S each, state in Transient/pv1/regrow_state.json. Heat guard every 6000 ticks
(the chain's own guard: clear Heatstroke on player colonists, food topped up). Isolation set OFF during, restored at the end."""
import sys, json, os, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
ST=r"Transient\pv1\regrow_state.json"; BUDGET_S=430
S="RimMandrake.Pyrelands.RM_PyrelandsSettings"
OFF=["burnLineEnabled","fireHawkSpreadEnabled","fireClockEnabled","burrowOnFireEnabled","furnaceThermalEnabled"]
X,Z=190,190; R=(X-10,Z-10,20,20); INNER="%d,%d,16,16"%(R[0]+2,R[1]+2); RS="%d,%d,%d,%d"%R
st=json.load(open(ST)) if os.path.exists(ST) else {"phase":"setup"}
h,p,tk=resolve_endpoint(); t0=time.time()
with RimBridge(h,p,tk) as rb:
    def ids(rect):
        r=rb.call("jawa/list_things",{"defName":"RM_FE_Plant_EmberGrass,RM_FE_Plant_Quickgrass","rect":rect,"limit":2000})
        return [q.get("id") for q in r.get("things") or []]
    def guard():
        r=rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True,"limit":100})
        for q in r.get("pawns") or []:
            if q.get("dead") or q.get("intelligence") not in (None,"Humanlike"): continue
            if any(h0.get("def")=="Heatstroke" for h0 in (q.get("health") or {}).get("hediffs") or []):
                rb.call("jawa/pawn_health",{"pawn":q["id"],"action":"remove","hediff":"Heatstroke"})
            rb.call("jawa/pawn_need",{"pawn":q["id"],"action":"need","need":"Food","level":1.0})
    def adv(n):
        left=n
        while left>0:
            s=min(6000,left); r=rb.call("jawa/safe_advance",{"ticks":s,"timeException":False,"timeoutMs":600000})
            ex=int(r.get("executed") or 0); left-=ex; st["advanced"]=st.get("advanced",0)+ex; guard()
            if r.get("state")!="done": st["stops"]=st.get("stops",[])+[str(r.get("stopBy") or r.get("state"))[:200]]
            if ex==0: raise SystemExit("advance stalled: %r"%r)
            if time.time()-t0>BUDGET_S: return left
        return 0
    def now(): return int(rb.call("jawa/weather_get",{}).get("ticksGame"))
    if st["phase"]=="setup":
        st["prior"]={f: rb.call("jawa/mod_settings_field",{"typeName":S,"action":"get","field":f}).get("value") for f in OFF}
        for f in OFF: rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":f,"value":"False"})
        x,z,w,hh=R; ring=[(x-4,z-4,w+8,4),(x-4,z+hh,w+8,4),(x-4,z,4,hh),(x+w,z,4,hh)]
        rb.call("jawa/clear_area",{"rect":"%d,%d,24,24"%(X-12,Z-12),"dryRun":False})
        rb.call("jawa/set_terrain_batch",{"ops":";".join("Concrete:%d,%d,%d,%d"%r for r in ring),"layer":"top"})
        rb.call("jawa/set_plants",{"ops":";".join("CLEAR:%d,%d,%d,%d"%r for r in ring)})
        rb.call("jawa/set_terrain",{"x":x,"z":z,"terrainDef":"RM_FE_Ash_Deep","width":20,"height":20,"layer":"top"})
        st["planted"]=rb.call("jawa/set_plants",{"ops":"RM_FE_Plant_EmberGrass:"+RS,"growth":1.0}).get("planted")
        st["pre"]=ids(INNER)
        st["fire"]=rb.call("jawa/map_fire",{"action":"start","rect":RS,"fireSize":1.2}).get("firesStarted")
        adv(5000); rb.call("jawa/map_fire",{"action":"extinguish","rect":"0,0,250,250"})
        standing=len([i for i in ids(INNER) if i in set(st["pre"])])
        st["standingAfterBurn"]=standing; st["t_burn_end"]=now(); st["phase"]="regrow"; st["fracs"]=[]
        print("setup", {k:st[k] for k in ("planted","fire","standingAfterBurn","t_burn_end")}, "pre", len(st["pre"]))
    if st["phase"]=="regrow":
        pre=set(st["pre"])
        for days in (3,7):
            if any(d==days for d,_ in st["fracs"]): continue
            target=st["t_burn_end"]+days*60000; left=target-now()
            if left>0 and adv(left)>0: break
            if now()>=target:
                new=len([i for i in ids(INNER) if i not in pre]); st["fracs"].append((days, new/float(len(pre))))
                print("day", days, "new", new, "of", len(pre))
                if days==3:
                    rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":X,"z":Z})
                    rb.call("rimworld/frame_cell_rect",{"x":R[0],"z":R[1],"width":20,"height":20,"paddingCells":3})
                    st["shot3"]=rb.call("rimworld/take_screenshot",{"fileName":"regrow_day3"}).get("path")
        if len(st["fracs"])==2:
            rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":X,"z":Z})
            rb.call("rimworld/frame_cell_rect",{"x":R[0],"z":R[1],"width":20,"height":20,"paddingCells":3})
            st["shot7"]=rb.call("rimworld/take_screenshot",{"fileName":"regrow_day7"}).get("path")
            for f,v in st["prior"].items(): rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":f,"value":str(v)})
            f3,f7=st["fracs"][0][1],st["fracs"][1][1]
            st["verdict"]="PASS" if (f3>=0.25 and f3<=0.55 and f7>=0.6 and st["standingAfterBurn"]<=0.5*len(pre)) else "FAIL"
            st["phase"]="done"; print("VERDICT", st["verdict"], st["fracs"])
    print("phase", st["phase"], "advanced", st.get("advanced"), "stops", st.get("stops"), "wall", int(time.time()-t0))
json.dump(st, open(ST,"w"))
