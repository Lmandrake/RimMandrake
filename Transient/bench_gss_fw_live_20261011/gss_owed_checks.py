"""Ad hoc BENCH live checks for TAP_CONSERVATION_SELFTEST_1 A1 and POLE_OWNER_CHANGE_DROPS_WIRES_1 A1 (timed sweep).
python.exe gss_owed_checks.py <saveName-to-load> <out.json>   (run from the export root)"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join("src", "RimMandrake", "GimmeSomeSlack"))
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402
import validation_style as VS  # noqa: E402

save, out = sys.argv[1], sys.argv[2]
B = VA.A()
res = {"save": save, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}

# ---- TAP_CONSERVATION A1: after a bridge save+load, cstyles twice returns the same pending + members; cprocess drains
ld = B.call("rimworld/load_game", saveName=save)
ok, waited = V._wait_playing(B)
res["load"] = {"tool": ld.get("success"), "playing": ok, "waited": waited}
B.ticks(1)                                            # pause (pauseFirst) -- no ticks between the reads below
rect = "%d,%d,%d,%d" % VS.SITE2


def snap(r):
    c = r.get("counters") or {}
    return {"success": r.get("success"), "pending": c.get("pending"), "processedCounter": c.get("processed"),
            "members": sorted(json.dumps(m, sort_keys=True) for m in (r.get("members") or []))}


r1, r2 = B.ap("cstyles:" + rect), B.ap("cstyles:" + rect)
s1, s2 = snap(r1), snap(r2)
# make the queue non-empty with zero ticks: god-place one conduit beside the stage-2 site, then read twice
x0, z0, w, h = VS.SITE2
pl = B.ap("cplace:PowerConduit:Industrial:%d,%d:god" % (x0 + w - 2, z0 + h - 2))
r3, r4 = B.ap("cstyles:" + rect), B.ap("cstyles:" + rect)
s3, s4 = snap(r3), snap(r4)
pr = B.ap("cprocess")
r5 = B.ap("cstyles:" + rect)
s5 = snap(r5)
res["tap"] = {"read1": {"pending": s1["pending"], "proc": s1["processedCounter"], "n": len(s1["members"])}, "read2": {"pending": s2["pending"], "proc": s2["processedCounter"], "n": len(s2["members"])},
              "place": {k: pl.get(k) for k in ("success", "error", "placed", "message") if k in pl},
              "read3": {"pending": s3["pending"], "proc": s3["processedCounter"], "n": len(s3["members"])}, "read4": {"pending": s4["pending"], "proc": s4["processedCounter"], "n": len(s4["members"])},
              "cprocess": pr, "read5": {"pending": s5["pending"], "n": len(s5["members"])}}
pend_ok = isinstance(s3["pending"], int) and s3["pending"] >= 1
same = s1 == s2 and s3 == s4
drained = pr.get("success") is not False and (pr.get("processed") or 0) >= 1 and s5["pending"] == 0
if not (r1.get("success") is not False and s1["members"]):
    res["TAP_A1"] = "UNMEASURED"
elif not pend_ok:
    res["TAP_A1"] = "UNMEASURED" if same else "FAIL"   # never got a non-empty queue to read
else:
    res["TAP_A1"] = "PASS" if same and drained else "FAIL"

# ---- POLE_OWNER_CHANGE A1 (timed): the rare-tick sweep alone cuts within ~250 ticks; no explicit ownersweep call
MS = VA.MSITE
O1, O2 = (MS[0] + 2, MS[1] + 3), (MS[0] + 12, MS[1] + 3)
B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % MS, categories="All")
B.call("jawa/build_batch", ops=V.ops("RM_AerialMast", [O1, O2]), faction="player", wipeExisting=False)
B.call("jawa/map_commit")
B.ticks(3)
oc = VA.anchors_by_pos(B.ap("census"))
o1, o2 = oc[O1]["id"], oc[O2]["id"]
lk = B.ap("link:%d,%d" % (o1, o2))
n1, n2 = VA.net_at(B, O1).get("net"), VA.net_at(B, O2).get("net")
linked0 = n1 is not None and n1 == n2
st = B.ap("set:cutWiresOnOwnerChange=True")
oc_ = B.ap("owner:%d,hostile" % o2)
cut_at = None
for t in range(0, 300, 10):
    B.ticks(10)
    c = VA.anchors_by_pos(B.ap("census"))
    links = [l for l in (c.get(O1) or {}).get("links") or []]
    if not any(l.get("state") not in ("Cut", "Fallen") for l in links):
        cut_at = t + 10
        break
res["owner"] = {"linkedBefore": linked0, "link": lk.get("success"), "ownerSet": oc_, "cutAfterTicks": cut_at,
                "linksAtO1": (VA.anchors_by_pos(B.ap("census")).get(O1) or {}).get("links")}
res["OWNER_A1"] = "UNMEASURED" if not linked0 else ("PASS" if cut_at is not None and cut_at <= 260 else "FAIL")
B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % MS, categories="All")
json.dump(res, open(out, "w"), indent=1, default=str)
print(json.dumps({k: res[k] for k in ("TAP_A1", "OWNER_A1")}), json.dumps(res["tap"], default=str)[:600], json.dumps(res["owner"], default=str)[:600])
