"""Watchers kit live state reads, run 2 (colonists cannot walk DeepSand, so watchers sit on the sand edge x=100)."""
exec(open("Transient/belt_watchers_live_20261008.py").read().split("# settings sanity")[0])
call("jawa/destroy_batch", rects="80,80,60,60", categories="All")
call("jawa/set_terrain_batch", ops="RM_DeepSand:100,100,20,20", refresh=True)
call("jawa/set_terrain_batch", ops="Soil:80,80,20,60;Soil:100,120,40,20", refresh=True)
C1 = "Human49128"; C2 = "Human54585"
for c in (C1, C2): call("jawa/set_draft", pawnId=c, drafted=True)
def ensure(msg, ok): 
    if not ok: print("  !! move failed:", msg)
def reset(): 
    call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
def hidden(pid): return "RM_WatcherHidden" in [str(x) for x in hed(pid)]
setting("geophone", True)
ensure("C1 out", goto(C1, 84, 112)); ensure("C2 out", goto(C2, 84, 104))
# T1
reset(); P = piin(100, 110); ensure("C1 12", goto(C1, 88, 110)); tick(250)
log("T1_job_colonist_at_12", (census(P) or {}).get("job")); log("T1_hidden", hidden(P))
# T2
ensure("C1 5", goto(C1, 95, 110)); h = None
for i in range(10):
    tick(30)
    if hidden(P): h = i * 30; break
log("T2_hidden_after_ticks_near5", h); sg = signs(); log("T2_signs", [(t["x"], t["z"]) for t in sg])
log("T2_pawn_spawned_while_hidden", (census(P) or {}).get("spawned"))
ensure("C1 away", goto(C1, 82, 110)); e = None
for i in range(60):
    tick(100)
    if not hidden(P): e = (i + 1) * 100; break
log("T2_emerged_after_ticks_leaving", e); log("T2_signs_after", len(signs())); log("T2_job_after", (census(P) or {}).get("job"))
# T3
reset(); P3 = piin(94, 110); ensure("C1", goto(C1, 88, 112)); jobs = []
for i in range(8):
    tick(40); jobs.append(((census(P3) or {}).get("job") or {}).get("def"))
log("T3_jobs_on_soil", sorted(set(map(str, jobs)))); log("T3_hidden_on_soil", hidden(P3)); log("T3_signs_on_soil", len(signs()))
tick(600); q = census(P3) or {}; log("T3_after", [q.get("x"), q.get("z"), (q.get("job") or {}).get("def")])
# T6 hunt order
reset(); P6 = piin(100, 108); ensure("C1", goto(C1, 88, 108)); tick(200); log("T6_pre_job", (census(P6) or {}).get("job"))
r = call("jawa/designate_batch", action="add", designation="Hunt", rect="100,108,1,1", onThings=True); log("T6_added", r.get("added"))
tick(120); log("T6_hidden_after", hidden(P6)); log("T6_hunt_left", call("jawa/designate_batch", action="query", designation="Hunt", rect="95,100,10,20").get("total"))
# T5 flush
reset(); tick(300); P5 = piin(100, 110); ensure("C1 near", goto(C1, 95, 110)); tick(120); log("T5_hidden", hidden(P5))
sg = [t for t in signs()]; log("T5_sign", [(t["id"], t["x"], t["z"]) for t in sg])
if sg:
    sid = sg[0]["id"]; ensure("C2", goto(C2, 92, 110))
    r = call("jawa/designate_batch", action="add", designation="RM_WatcherFlushMark", rect="%d,%d,1,1" % (sg[0]["x"], sg[0]["z"]), onThings=True); log("T5_marked", r.get("added"))
    call("jawa/ordered_job", pawnId=C2, jobDef="RM_WatcherFlush", targetAId=sid, waitTicks=0)
    for i in range(10):
        tick(40); q = census(P5) or {}
        log("T5_s%d" % i, [(q.get("job") or {}).get("def"), hidden(P5), len(signs()), ((census(C2) or {}).get("job") or {}).get("def"), pos(C2)])
        if not hidden(P5): break
    log("T5_hunt_designations", call("jawa/designate_batch", action="query", designation="Hunt", rect="85,95,30,30").get("total"))
# T4 geophone (+ control with toggle off)
for toggle in (True, False):
    reset(); setting("geophone", toggle); ensure("C1", goto(C1, 84, 112)); ensure("C2", goto(C2, 84, 104)); tick(100)
    P4 = piin(100, 110); ensure("C1 12", goto(C1, 88, 110)); tick(200); pre = ((census(P4) or {}).get("job") or {}).get("def")
    ensure("C1 away", goto(C1, 82, 118))   # >14 cells from the swimmer, watcher keeps watching? (no visitor) record anyway
    m = call("jawa/spawn_pawn", kindDef="RM_Muurrok", x=108, z=110, faction="none")["pawns"][0]["id"]
    tick(30); mh = [str(x) for x in hed(m)]
    res = None
    for i in range(10):
        tick(30)
        if hidden(P4): res = i * 30 + 30; break
    log("T4_geophone_%s" % toggle, {"pre_job": pre, "swimmer_hediffs": mh, "hidden_after_ticks": res, "signs": len(signs())})
setting("geophone", True)
print("DONE")
