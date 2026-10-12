"""BENCH ad hoc live checks, GimmeSomeSlack tier, 2026-10-11 (run from the HEAD export root with python.exe).

  python.exe Transient/bench_live_20261011/gss_live_checks.py <out.json>

Blocks (each writes rows; any could-not-ask is UNMEASURED, never PASS):
  TC  TAPCLAMP_REDRAW_BITES_DOWN_AT_LAST: a clamp on an E-W enemy run (ours from the south) and on a N-S enemy run
      (ours from the east); screenshots for the look (jaws on THEIR cord; E-W handles up, N-S handles away from ours = west).
  PT  POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK A2/A3: the E-W victim grid is a NEUTRAL faction with a witness 4-6 cells away;
      the "Power theft discovered" letter + caughtCount; one in-game day later goodwill fell by theftGoodwillPerDay (2);
      then the clamp is removed and another day costs nothing.
  FI  FALLEN_WIRE_SHOCK_1 A5 (chemfuel half): a live fallen cord's tip on Filth_Fuel starts a fire within a few sweeps.
  CS  TAP_CONSERVATION_SELFTEST_1 A1: after a bridge save+load, cstyles twice = same pending + members; cprocess drains.
"""
import json
import os
import sys
import time

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "GimmeSomeSlack"))
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402

OUT = sys.argv[1]
B = VA.A()
rows = []
res = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "shots": []}
THEFT = "RimMandrake.GimmeSomeSlack.Aerial.PowerTheftConsequences"
SHOCK = "RimMandrake.GimmeSomeSlack.Aerial.RM_FallenWireShock"
VA.SHOTS = os.path.join(ROOT, "Transient", "bench_live_20261011", "shots")


def row(rid, st, cls, det):
    rows.append({"id": rid, "status": st, "class": cls, "detail": det})
    print("%-40s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)


def stat(t, f):
    return B.call("jawa/mod_settings_field", typeName=t, action="get", field=f).get("value")


def save():
    json.dump(res, open(OUT, "w"), indent=1, default=str)


def prep(rect):
    r = "%d,%d,%d,%d" % rect
    B.call("jawa/destroy_batch", rects=r, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:" + r)
    B.call("jawa/set_fog", action="unfog", rect=r)
    B.call("jawa/set_roof_batch", ops="None:" + r)


def first_id(defn, rect):
    lt = B.call("jawa/list_things", defName=defn, rect="%d,%d,%d,%d" % rect, limit=10)
    return [t.get("id") or t.get("thingId") for t in lt.get("things") or []]


rm = B.call("jawa/running_mods", assembly="RimMandrakeGimmeSomeSlack", details=False)
res["running"] = len(rm.get("packageIds") or [])
B.ap("defaults")
B.ticks(1)
facs = B.call("jawa/list_factions").get("factions") or []
res["factions"] = [{k: f.get(k) for k in ("defName", "name", "hostile", "goodwill", "permanentEnemy", "hidden")} for f in facs]
neutral = next((f for f in facs if not f.get("isPlayer") and not f.get("hostile") and not f.get("permanentEnemy")
                and not f.get("hidden") and str(f.get("defName", "")).startswith("Outlander")), None) or \
    next((f for f in facs if not f.get("isPlayer") and not f.get("hostile") and not f.get("permanentEnemy") and not f.get("hidden")), None)
res["neutral"] = neutral
save()

# ------------------------------------------------------------------ scenes
S1 = (14, 14, 30, 26)          # E-W victim (neutral) run
S2 = (50, 14, 22, 26)          # N-S victim (hostile) run
prep(S1)
prep(S2)
nf = neutral["defName"] if neutral else "hostile"
# S1: three neutral batteries (1x2, rot N) under an E-W conduit run at z=24; clamp south of the run's middle; ours from the south
b1 = [B.call("jawa/build_batch", ops="Battery:%d,22,0;Battery:%d,22,0;Battery:%d,22,0" % (18, 20, 22), faction=nf),
      B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(x, 24) for x in range(18, 36)]), faction=nf, wipeExisting=False),
      B.call("jawa/build_batch", ops="RM_PowerTapClamp:28,23", faction="player", wipeExisting=False),
      B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(28, 20), (28, 19), (28, 18)]), faction="player", wipeExisting=False),
      B.call("jawa/build_batch", ops="StandingLamp:29,17", faction="player", wipeExisting=False)]
# S2: hostile batteries + a N-S run at x=56; clamp east of the run's middle; ours from the east
b2 = [B.call("jawa/build_batch", ops="Battery:53,16,0;Battery:53,19,0", faction="hostile", wipeExisting=False),
      B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(56, z) for z in range(16, 36)] + [(54, 17), (55, 17), (54, 20), (55, 20)]),
             faction="hostile", wipeExisting=False),
      B.call("jawa/build_batch", ops="RM_PowerTapClamp:57,27", faction="player", wipeExisting=False),
      B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(60, 27), (61, 27), (62, 27)]), faction="player", wipeExisting=False),
      B.call("jawa/build_batch", ops="StandingLamp:63,28", faction="player", wipeExisting=False)]
B.call("jawa/map_commit")
bats = first_id("Battery", S1) + first_id("Battery", S2)
for bid in bats:
    B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
# witnesses for S1 (neutral): 3 pawns 4-6 cells north of the clamp, open ground between
wit = B.call("jawa/spawn_pawn", kindDef="Villager", x=28, z=29, faction=nf, count=3) if neutral else {}
res["build"] = {"s1": [b.get("survived") for b in b1], "s2": [b.get("survived") for b in b2], "batteries": bats,
                "witness": {k: wit.get(k) for k in ("success", "pawns", "failed")}}
gw0 = next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or [] if neutral and f.get("defName") == nf), None)
cc0 = stat(THEFT, "caughtCount")
B.ticks(300)
ct = B.ap("census")
res["taps0"] = ct.get("taps")
letters = B.call("jawa/letter_list").get("letters") or []
pt_letter = [l for l in letters if "Power theft" in json.dumps(l)]
cc1 = stat(THEFT, "caughtCount")
save()
res["shots"].append(B.shot("tapclamp_EW_enemy_run_ours_from_south", (24, 19, 9, 7)))
time.sleep(1.5)
res["shots"].append(B.shot("tapclamp_NS_enemy_run_ours_from_east", (54, 23, 9, 8)))
time.sleep(1.5)
res["shots"].append(B.shot("tapclamp_both_context", (14, 14, 58, 24)))
taps = ct.get("taps") or []
row("TC_taps_connected", "PASS" if len(taps) == 2 and all(t.get("connected") and t.get("ourNet") != t.get("victimNet") for t in taps)
    else ("UNMEASURED" if not taps else "FAIL"), "MOD", {"taps": taps})
row("TC_look_shots", "UNMEASURED", "LOOK", {"shots": res["shots"], "bar": "jaws on THEIR cord; E-W handles up; N-S handles away from ours (west)"})
if not neutral:
    row("PT_A2_letter", "UNMEASURED", "SITE", "no non-hostile faction in this world")
else:
    row("PT_A2_letter", "PASS" if pt_letter and (cc1 or 0) > (cc0 or 0) else "FAIL", "MOD",
        {"letter": pt_letter[:1], "caughtCount": [cc0, cc1], "witness": wit.get("pawns")})
save()

# one in-game day of draining, the clamp still on
gc0 = stat(THEFT, "goodwillCharged")
B.ticks(60000 + 500)
gw1 = next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or [] if f.get("defName") == nf), None)
gc1 = stat(THEFT, "goodwillCharged")
ct2 = B.ap("census")
ev = B.call("jawa/faction_goodwill_situations", faction=nf) if neutral else {}
s1lamp = VA.net_at(B, (29, 17))
row("PT_A3_goodwill_day", ("UNMEASURED" if not neutral else
                           ("PASS" if gw0 is not None and gw1 is not None and gw0 - gw1 == 2 and (gc1 or 0) - (gc0 or 0) == -2 else "FAIL")),
    "MOD", {"goodwill": [gw0, gw1], "goodwillCharged": [gc0, gc1], "taps": ct2.get("taps"), "ourLamp": s1lamp.get("things"),
            "situations": ev})
save()
# remove the S1 clamp -> another day costs nothing
B.call("jawa/destroy_batch", rects="28,23,1,1", categories="All")
B.ticks(60000 + 500)
gw2 = next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or [] if f.get("defName") == nf), None)
gc2 = stat(THEFT, "goodwillCharged")
row("PT_A3_removed_stops", "UNMEASURED" if not neutral else ("PASS" if gw2 == gw1 and gc2 == gc1 else "FAIL"), "MOD",
    {"goodwill": [gw1, gw2], "goodwillCharged": [gc1, gc2], "stop": "clamp removed (not flicked)"})
save()

# ------------------------------------------------------------------ FI: live fallen cord tip on chemfuel
S3 = (14, 44, 30, 12)
prep(S3)
B.call("jawa/build_batch", ops="Battery:15,48,0", faction="player", wipeExisting=False)
B.call("jawa/build_batch", ops=V.ops("RM_AerialMast", [(16, 48), (28, 48)]), faction="player", wipeExisting=False)
B.call("jawa/map_commit")
for bid in first_id("Battery", S3):
    B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
B.ticks(3)
c = B.ap("census")
ap = VA.anchors_by_pos(c)
m1, m2 = ap.get((16, 48)), ap.get((28, 48))
fi = {"linked": bool(m1 and m2 and any(l.get("state") == "Up" for l in m1.get("links") or []))}
if m1 and m2:
    B.ap("kill:%d" % m2["id"])
    B.ticks(2)
    B.ap("poll")
    c2 = B.ap("census")
    a1 = VA.anchors_by_pos(c2).get((16, 48)) or {}
    fl = (a1.get("fallen") or [{}])[0]
    tip = fl.get("tip")
    fi.update({"fallenLive": a1.get("fallenLive"), "tip": tip, "laidLen": fl.get("laidLen")})
    if tip and a1.get("fallenLive"):
        tx, tz = int(tip[0]), int(tip[1])
        fuel = B.call("jawa/spawn_batch", ops=";".join("Filth_Fuel:%d,%d" % (tx + dx, tz + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)))
        fi["fuelSpawn"] = fuel.get("success")
        ig0 = stat(SHOCK, "ignitions")
        fires = []
        for i in range(12):                      # 12 sweeps of 250 ticks at 35 % each
            B.ticks(250)
            fires = first_id("Fire", (tx - 3, tz - 3, 7, 7))
            if fires:
                break
        fi.update({"sweeps": i + 1, "fires": len(fires), "ignitions": [ig0, stat(SHOCK, "ignitions")]})
        res["shots"].append(B.shot("fallen_live_tip_on_chemfuel_fire", (tx - 6, tz - 4, 13, 9)))
        row("FI_A5_chemfuel_ignites", "PASS" if fires else "FAIL", "MOD", fi)
    else:
        row("FI_A5_chemfuel_ignites", "UNMEASURED", "SITE", fi)
else:
    row("FI_A5_chemfuel_ignites", "UNMEASURED", "SITE", fi)
B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % S3, categories="All")
save()

# ------------------------------------------------------------------ CS: cstyles readout across a bridge save+load
name = "RM_bench_cstyles_%s" % time.strftime("%Y%m%d%H%M%S")
before = V._saves_stat()
B.call("rimworld/save_game", saveName=name)
V._wait_saved(name)
after = V._saves_stat()
new = sorted(set(after) - set(before))
ld = B.call("rimworld/load_game", saveName=name)
ok, waited = V._wait_playing(B)
B.ticks(1)
rect = "14,14,58,26"


def snap(r):
    cn = r.get("counters") or {}
    return {"success": r.get("success"), "pending": cn.get("pending"), "processed": cn.get("processed"),
            "members": sorted(json.dumps(m, sort_keys=True) for m in (r.get("members") or []))}


s1, s2 = snap(B.ap("cstyles:" + rect)), snap(B.ap("cstyles:" + rect))
pl = B.ap("cplace:PowerConduit:Industrial:%d,%d:god" % (30, 36))
s3, s4 = snap(B.ap("cstyles:" + rect)), snap(B.ap("cstyles:" + rect))
pr = B.ap("cprocess")
s5 = snap(B.ap("cstyles:" + rect))
same = s1["success"] and s1 == s2 and s3 == s4
row("CS_A1_cstyles_read_is_idempotent", "PASS" if same and ok and new == [name + ".rws"] else ("UNMEASURED" if not ok else "FAIL"), "MOD",
    {"save": name, "newFiles": new, "loaded": ok, "waited": waited,
     "reads": [{k: s[k] for k in ("pending", "processed")} | {"n": len(s["members"])} for s in (s1, s2, s3, s4, s5)],
     "place": pl.get("success"), "cprocess": pr})
row("CS_A1_cprocess_drains", "PASS" if pr.get("success") and (s5.get("pending") in (0, None)) else "UNMEASURED", "MOD",
    {"pendingAfterPlace": s3.get("pending"), "cprocessed": pr.get("processed"), "pendingAfter": s5.get("pending"),
     "note": "MapComponentUpdate drains every frame, so a non-empty queue is only seen if a read lands between frames"})
res["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
save()
print("DONE", OUT)
