"""POWER_THEFT A3 rerun: the first run's 60,500-tick step hit step_game_ticks' 120 s timeout after ~7,200 ticks
(1 tick/frame), so no day ever elapsed (HARNESS). This plays at speed 3/4 and polls ticksGame until a full day has passed.

  python.exe Transient/bench_live_20261011/gss_theft_day.py <out.json>     (HEAD export root, gimmesomeslack tier map)
"""
import json
import os
import sys
import time

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "GimmeSomeSlack"))
import validation as V  # noqa: E402,F401
import validation_aerial as VA  # noqa: E402

OUT = sys.argv[1]
B = VA.A()
THEFT = "RimMandrake.GimmeSomeSlack.Aerial.PowerTheftConsequences"
rows = []
res = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}


def row(rid, st, cls, det):
    rows.append({"id": rid, "status": st, "class": cls, "detail": det})
    print("%-32s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
    json.dump(res, open(OUT, "w"), indent=1, default=str)


def tick():
    return B.call("rimworld/get_game_info").get("tick") or B.call("rimworld/get_game_info").get("ticksGame")


def play(n):
    t0 = tick()
    B.call("rimworld/set_time_speed", speed=4)
    w0 = time.time()
    while time.time() - w0 < 1800:
        time.sleep(3)
        t = tick()
        if t is not None and t0 is not None and t - t0 >= n:
            break
    B.call("rimworld/set_time_speed", speed=0)
    time.sleep(1)
    a, b = tick(), (time.sleep(1.0), tick())[1]
    return {"from": t0, "to": b, "elapsed": (b or 0) - (t0 or 0), "pausedVerified": a == b}


def goodwill(dn):
    return next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or [] if f.get("defName") == dn), None)


gi = B.call("rimworld/get_game_info")
res["gameInfoKeys"] = sorted(gi.keys())[:40]
nf = "OutlanderCivil"
B.call("jawa/destroy_batch", rects="28,23,1,1", categories="All")
b = B.call("jawa/build_batch", ops="RM_PowerTapClamp:28,23", faction="player", wipeExisting=False)
B.call("jawa/map_commit")
lt = B.call("jawa/list_things", defName="Battery", rect="14,14,30,26", limit=10)
for t in lt.get("things") or []:
    B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
w = B.call("jawa/spawn_pawn", kindDef="Villager", x=28, z=29, faction=nf, count=2)
cc0 = B.call("jawa/mod_settings_field", typeName=THEFT, action="get", field="caughtCount").get("value")
B.ticks(300)
cc1 = B.call("jawa/mod_settings_field", typeName=THEFT, action="get", field="caughtCount").get("value")
caught = int(cc1 or 0) > int(cc0 or 0)
gw0, gc0 = goodwill(nf), B.call("jawa/mod_settings_field", typeName=THEFT, action="get", field="goodwillCharged").get("value")
res["setup"] = {"clamp": b.get("survived"), "witness": [p.get("id") for p in w.get("pawns") or []], "caughtCount": [cc0, cc1]}
if not caught:
    row("PT_A3_goodwill_day", "UNMEASURED", "SITE", res["setup"])
    sys.exit(0)
p1 = play(60000 + 300)
gw1, gc1 = goodwill(nf), B.call("jawa/mod_settings_field", typeName=THEFT, action="get", field="goodwillCharged").get("value")
ct = B.ap("census")
tap = next((t for t in ct.get("taps") or [] if t.get("victimFaction") == next((f.get("name") for f in B.call("jawa/list_factions").get("factions") or [] if f.get("defName") == nf), None)), None)
letters = [l for l in B.call("jawa/letter_list").get("letters") or [] if "oodwill" in json.dumps(l) or "theft" in json.dumps(l).lower()]
ok_day = p1["elapsed"] >= 60000
row("PT_A3_goodwill_day", ("UNMEASURED" if not ok_day else ("PASS" if gw0 is not None and gw1 is not None and gw0 - gw1 == 2 else "FAIL")), "MOD",
    {"play": p1, "goodwill": [gw0, gw1], "goodwillCharged": [gc0, gc1], "tap": tap, "letters": letters[-3:]})
B.call("jawa/destroy_batch", rects="28,23,1,1", categories="All")
p2 = play(60000 + 300)
gw2, gc2 = goodwill(nf), B.call("jawa/mod_settings_field", typeName=THEFT, action="get", field="goodwillCharged").get("value")
row("PT_A3_removed_stops", "UNMEASURED" if p2["elapsed"] < 60000 else ("PASS" if gw2 == gw1 and gc2 == gc1 else "FAIL"), "MOD",
    {"play": p2, "goodwill": [gw1, gw2], "goodwillCharged": [gc1, gc2], "stop": "clamp removed (not flicked)"})
print("DONE")
