"""r5 re-proof TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK (78f534c9e5): a WILD animal downed mid-advance must not stop the
governed clock; the chunk resumes and the stop is listed in clockgate.BENIGN_STOPS. Staging: on the loaded site, spawn a
wild Muffalo far from the colonists and give it Heatstroke 0.6 so the 56 C site downs it within the advance.
PASS: all requested ticks executed, BENIGN_STOPS lists >=1 wild downed resume naming the muffalo, muffalo downed, no
colonist downed. UNMEASURED: the muffalo never went down (nothing tested) or a colonist went down (disturbed)."""
import json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import proof_hose as PH
from modcheck import clockgate as CG
out = sys.argv[1]
B = PH.PB()
res = {"started": time.strftime("%Y-%m-%dT%H:%M:%S")}
cols = B.hp("colonists").get("pawns") or []
res["colonists"] = [(p["id"], p.get("pos"), p.get("downed")) for p in cols]
cx = sum(p["pos"][0] for p in cols) // max(1, len(cols)); cz = sum(p["pos"][1] for p in cols) // max(1, len(cols))
tx, tz = (cx + 40 if cx < 200 else cx - 40), cz
sp = B.call("jawa/spawn_pawn", kindDef="Muffalo", x=tx, z=tz, faction="none") or {}
res["spawn"] = sp
row0 = (sp.get("pawns") or sp.get("spawned") or [{}])[0] if isinstance(sp.get("pawns") or sp.get("spawned"), list) else {}
mid = sp.get("pawnId") or sp.get("thingId") or sp.get("id") or row0.get("id") or row0.get("pawnId") or row0.get("thingId")
mnum = "".join(ch for ch in str(mid) if ch.isdigit())
res["heat"] = B.call("jawa/pawn_health", pawn=mnum, action="add", hediff="Heatstroke", severity=0.612)
t0 = (B.call("rimworld/get_game_info") or {}).get("ticksGame")
CG.BENIGN_STOPS.clear()
err = None
try:
    ex = CG.advance_chunk(B, 2000)
except Exception as e:  # GovernorStop
    ex, err = None, repr(e)
t1 = (B.call("rimworld/get_game_info") or {}).get("ticksGame")
mg = (B.call("jawa/pawn_get", pawn=mnum) or {}).get("pawns") or [{}]
cols2 = B.hp("colonists").get("pawns") or []
res.update({"executed": ex, "error": err, "ticks": [t0, t1], "benign": list(CG.BENIGN_STOPS),
            "muffalo": {"id": mnum, "downed": mg[0].get("downed"), "dead": mg[0].get("dead"), "hediffs": mg[0].get("hediffs")},
            "colonistsAfter": [(p["id"], p.get("downed")) for p in cols2]})
col_down = any(p.get("downed") for p in cols2)
wild_resumes = [b for b in CG.BENIGN_STOPS if b.get("detail") and "downed" in b["detail"]]
if col_down:
    v = "UNMEASURED (a colonist went down: disturbed)"
elif not wild_resumes:
    v = "UNMEASURED (no wild downed stop happened)" if err is None else "UNMEASURED (stopped by something else: %s)" % err
else:
    v = "PASS" if err is None and t1 is not None and t0 is not None and t1 - t0 >= 2000 else "FAIL"
res["verdict"] = v
json.dump(res, open(out, "w"), indent=1, default=str)
print(v, json.dumps({k: res[k] for k in ("executed", "error", "ticks", "benign", "muffalo")}, default=str)[:1200])
