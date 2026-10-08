exec(open("Transient/belt_watchers_live2_20261008.py").read().split("setting(\"geophone\", True)\nensure(\"C1 out\"")[0])
def until(cond, maxt=2000, step=50):
    t = 0
    while t < maxt:
        if cond(): return t
        tick(step); t += step
    return None
def wjob(pid): return ((census(pid) or {}).get("job") or {}).get("def")
print("C1", pos(C1), "C2", pos(C2))
# T6: wait until watching
reset(); call("jawa/ordered_job", pawnId=C1, jobDef="Goto", targetAX=88, targetAZ=108, waitTicks=0)
P6 = piin(100, 108); t = until(lambda: wjob(P6) == "RM_WatcherWatch", 3000); log("T6_watching_after", t); log("T6_c1", pos(C1))
if t is not None:
    r = call("jawa/designate_batch", action="add", designation="Hunt", rect="100,108,1,1", onThings=True); log("T6_added", r.get("added"))
    log("T6_hidden_after_ticks", until(lambda: hidden(P6), 300, 20)); log("T6_hunt_left", call("jawa/designate_batch", action="query", designation="Hunt", rect="95,100,10,20").get("total"))
# T5 flush: hide first (C1 within 5), C2 comes to the sign
reset(); tick(100); P5 = piin(100, 110)
call("jawa/ordered_job", pawnId=C1, jobDef="Goto", targetAX=95, targetAZ=110, waitTicks=0)
log("T5_hidden_after", until(lambda: hidden(P5), 3000)); log("T5_c1", pos(C1))
sg = signs(); log("T5_sign", [(t["id"], t["x"], t["z"]) for t in sg])
if sg:
    sid = sg[0]["id"]
    r = call("jawa/designate_batch", action="add", designation="RM_WatcherFlushMark", rect="100,110,1,1", onThings=True); log("T5_marked", r.get("added"))
    call("jawa/ordered_job", pawnId=C2, jobDef="RM_WatcherFlush", targetAId=sid, waitTicks=0)
    for i in range(30):
        tick(60); q = census(P5) or {}
        row = [(q.get("job") or {}).get("def"), hidden(P5), len(signs()), wjob(C2), pos(C2)]
        if i % 3 == 0 or not hidden(P5): log("T5_s%d" % i, row)
        if not hidden(P5): break
    log("T5_hunt_designations_on_piinnok", call("jawa/designate_batch", action="query", designation="Hunt", rect="85,95,30,30").get("total"))
print("DONE")
