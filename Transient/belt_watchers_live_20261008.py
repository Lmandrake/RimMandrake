"""Live state-read checks for the Watchers kit (WATCHER_CREATURES_MOD_1), 2026-10-08. Run: python.exe <this>.
Reads state only (job, hediff, sign Thing, designation); no screenshots, no flyers."""
exec(open("Transient/belt_watchers_probe.py").read().split("st=call")[0])
R = {}
def tick(n): call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=300000)
def census(pid):
    for q in call("jawa/pawn_census").get("pawns", []):
        if q.get("id") == pid: return q
def hed(pid):
    r = call("jawa/pawn_get", pawn=pid)
    try: return [h.get("def") or h.get("defName") or h for h in r["pawns"][0]["hediffs"]]
    except Exception: return ["?", r.get("message")]
def signs():
    return call("jawa/list_things", defName="RM_WatcherSign_SandDimple").get("things", [])
def clear():
    call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
    ids = [t.get("id") or t.get("thingId") for t in signs()]
    pass
def colonist(x, z):
    r = call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player")
    cid = r["pawns"][0]["id"]; call("jawa/set_draft", pawnId=cid, drafted=True); return cid
def pos(cid):
    q = census(cid) or {}; return (q.get("x") or -999, q.get("z") or -999)
def goto(cid, x, z):
    r = call("jawa/ordered_job", pawnId=cid, jobDef="Goto", targetAX=x, targetAZ=z, waitTicks=0)
    for i in range(30):
        tick(20)
        p = pos(cid)
        if p and abs(p[0]-x) <= 1 and abs(p[1]-z) <= 1: return True
    print("  goto did not arrive", cid, pos(cid), "wanted", (x, z), json.dumps(r)[:200]); return False
def setting(f, v): return call("jawa/mod_settings_field", typeName="RimMandrake.Watchers.RM_WatchersSettings", action="set", field=f, value=str(v)).get("success")
def piin(x, z):
    return call("jawa/spawn_pawn", kindDef="RM_Piinnok", x=x, z=z, faction="none")["pawns"][0]["id"]
def log(k, v): R[k] = v; print("##", k, "=>", v, flush=True)

# settings sanity (all toggles shipped defaults)
st = call("jawa/mod_settings_field", typeName="RimMandrake.Watchers.RM_WatchersSettings", action="list")
log("settings_list", json.dumps(st)[:600])

call("jawa/destroy_batch", rects="80,80,60,60", categories="All")
call("jawa/set_terrain_batch", ops="RM_DeepSand:100,100,20,20", refresh=True)
call("jawa/set_terrain_batch", ops="Soil:80,80,20,60;Soil:100,120,40,20;Soil:120,80,20,40", refresh=True)
# ---- T1 watches (and faces)
clear(); P = piin(110, 110); C1 = "Human49128"; C2 = "Human54585"; call("jawa/set_draft", pawnId=C1, drafted=True); call("jawa/set_draft", pawnId=C2, drafted=True); print("C1", census(C1), "C2", census(C2)); goto(C1, 110, 122); goto(C2, 130, 130); tick(250)
q = census(P); log("T1_job_with_colonist_at_12", (q or {}).get("job"))
log("T1_thing_graphic_keys", json.dumps(call("jawa/thing_graphic", thing=P))[:400])
# ---- T2 flinch -> hide + sign, then re-emerge
goto(C1, 110, 106); seen = None
for i in range(12):
    tick(60); h = hed(P); s = signs()
    if "RM_WatcherHidden" in [str(x) for x in h]: seen = (i, h, [(t.get("x"), t.get("z")) for t in s]); break
log("T2_hidden_after_approach", seen)
log("T2_signs_while_hidden", [ (t.get("def"), t.get("x"), t.get("z")) for t in signs()])
log("T2_census_hidden", json.dumps(census(P))[:400])
goto(C1, 125, 125); gone = None
for i in range(40):
    tick(100); h = hed(P)
    if "RM_WatcherHidden" not in [str(x) for x in h] : gone = (i * 100, h, len(signs())); break
log("T2_emerged_after_ticks", gone)
# ---- T3 never hides / watches off medium: plain sand, colonist near
clear(); goto(C1, 92, 122); tick(400)
P3 = piin(92, 110); jobs = set(); 
for i in range(10):
    tick(60); jobs.add(str((census(P3) or {}).get("job")))
log("T3_off_medium_jobs", sorted(jobs)); q = census(P3); log("T3_final_pos", (q or {}).get("x"), ) 
log("T3_final_xz", [(q or {}).get("x"), (q or {}).get("z")])
tick(600); q = census(P3); log("T3_after_600_more", [(q or {}).get("x"), (q or {}).get("z"), (q or {}).get("job"), signs() and "signs" or "nosign"])
log("T3_terrain_at_final", json.dumps(call("jawa/get_terrain_batch", rects="%d,%d,1,1" % ((q or {}).get("x", 0), (q or {}).get("z", 0))))[:260])
# ---- T6 hunt order sinks a peeker
clear(); goto(C1, 110, 125); tick(300); P6 = piin(110, 110); tick(250)
log("T6_pre_job", (census(P6) or {}).get("job"))
r = call("jawa/designate_batch", action="add", designation="Hunt", rect="110,110,1,1", onThings=True); log("T6_hunt_designate", json.dumps(r)[:300])
tick(120); log("T6_hediffs_after", hed(P6)); log("T6_hunt_designations_left", json.dumps(call("jawa/designate_batch", action="query", designation="Hunt", rect="105,105,10,10"))[:300])
# ---- T5 flush
clear(); goto(C2, 110, 100); goto(C1, 110, 125); tick(300); P5 = piin(110, 110); tick(200)
goto(C2, 110, 106); tick(150); log("T5_hidden_pre", hed(P5))
sg = signs(); log("T5_sign", [(t.get("id") or t.get("thingId"), t.get("x"), t.get("z")) for t in sg])
if sg:
    sid = sg[0].get("id") or sg[0].get("thingId")
    r = call("jawa/designate_batch", action="add", designation="RM_WatcherFlushMark", rect="%d,%d,1,1" % (sg[0]["x"], sg[0]["z"]), onThings=True); log("T5_mark", json.dumps(r)[:300])
    goto(C2, 110, 99)
    r = call("jawa/ordered_job", pawnId=C2, jobDef="RM_WatcherFlush", targetAId=sid, waitTicks=0); log("T5_flush_order", json.dumps(r)[:300])
    for i in range(8):
        tick(60); q = census(P5); log("T5_step%d" % i, [(q or {}).get("job"), hed(P5), len(signs()), (census(C2) or {}).get("job")])
    log("T5_hunt_marked", json.dumps(call("jawa/designate_batch", action="query", designation="Hunt", rect="100,100,20,20"))[:300])
# ---- T4 geophone
clear(); goto(C1, 125, 125); goto(C2, 125, 125); tick(300); P4 = piin(104, 104); tick(200)
log("T4_pre_job", (census(P4) or {}).get("job"))
r = call("jawa/spawn_pawn", kindDef="RM_Muurrok", x=112, z=112, faction="none"); log("T4_swimmer_spawn", json.dumps(r)[:300])
for i in range(8):
    tick(60); q = census(P4); log("T4_step%d" % i, [(q or {}).get("job"), hed(P4)])
print("DONE")
