"""FLOWWORKS water-fix live check, owner's headline scene (2026-10-16): a pond fed by a river and a 1-deep trench dug beside it.

  python.exe src/RimMandrake/FlowWorks/northstar/live_probes/fw_water_headline.py OUT_DIR
  (bridge held; the `river` test site loaded: modcheck/test_site_saves.py load river)

Scene on the river site (tile 3247): the river's moving water is at x<=111 around z=120; a 4x3 WaterShallow pond at
(112..115,119..121) touches it, so FormBody merges pond + river into ONE limitless body (MEASURED: limitless, truncated).
A 8-cell trench at (116..123,120), D=1, is dug east of the pond (excavation_drive, no fill). Time advances only through
jawa/safe_advance in 250-tick chunks (one engine pulse each); every chunk reads the trench fills.
Save is taken after 3 chunks (mid-fill). Run A continues to the end; the save is then reloaded from the main menu and run B
repeats the same chunks. Bar: trench full (all 8 = 1) and fill sequence A == B chunk for chunk.
Screenshots: jawa/take_screenshot (the game's own frame; an OS capture shows whatever window sits on top of the game).
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import proof_hose as PH  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
B = PH.PB()
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
SAVE = "RM_FW_headline_20261016"
POND = (112, 119, 4, 3)
TRENCH = [(116 + k, 120) for k in range(8)]
SCENE = (108, 116, 20, 10)
res = {"script": "fw_water_headline.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S")}


def call(t, **k):
    return B.call(t, **k)


def fills():
    r = call("jawa/flowworks_excavation_rect", x=TRENCH[0][0], z=120, w=8, h=1, onlyNonZero=False)
    rows = r.get("rows") or []
    return [q.get("f") for q in rows], [q.get("d") for q in rows]


def adv(n):
    r = call("jawa/safe_advance", ticks=n)
    return r.get("success") and r.get("executed") == n and not r.get("triggers"), r


def tick():
    return (call("rimworld/get_game_info").get("ticksGame"))


def shot(name):
    call("jawa/clear_ui", all=True)
    call("rimworld/jump_camera_to_cell", x=SCENE[0] + 10, z=SCENE[1] + 5)
    call("rimworld/set_camera_zoom", rootSize=9.0)
    call("rimworld/jump_camera_to_cell", x=SCENE[0] + 10, z=SCENE[1] + 5)
    time.sleep(2.0)
    r = call("jawa/take_screenshot", fileName=name)
    src = r.get("filePath")
    for _ in range(20):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    dst = os.path.join(OUT, name + ".png")
    shutil.copyfile(src, dst)
    res.setdefault("shots", []).append(dst)
    return dst


def body():
    return call("jawa/flowworks_body_report", x=113, z=120, classify=False).get("body")


def run_chunks(n, label, seq):
    for i in range(n):
        ok, r = adv(250)
        f, d = fills()
        seq.append({"tick": tick(), "fills": f, "ok": bool(ok)})
        print(label, i, seq[-1]["tick"], f, flush=True)
        if f and all(v == 1 for v in f) and i > 0:
            break


# ---- stage
call("jawa/clear_area", rect="%d,%d,%d,%d" % SCENE, dryRun=False)
call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SCENE)
call("jawa/set_terrain_batch", ops="Soil:116,117,10,8")
call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,%d,%d" % POND)
cls = call("jawa/flowworks_body_report", x=113, z=120, classify=True)
res["classify"] = cls
res["body0"] = cls.get("body")
call("jawa/weather_set", weather="Clear", lockWeather=True)
call("jawa/incident_queue_clear")
res["before_shot"] = shot("headline_before")
res["terrain_before"] = call("jawa/get_terrain_batch", rects="%d,%d,%d,%d" % SCENE).get("ops")
# ---- dig the trench
for c in TRENCH:
    call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=1, setFill=-1)
f0, d0 = fills()
res["trench_dug"] = {"fills": f0, "depth": d0, "tick": tick()}
print("dug", f0, d0)
res["dug_shot"] = shot("headline_dug_dry")
# ---- run until mid-fill, save
seqA = []
run_chunks(3, "A", seqA)
before = set(os.listdir(PH.V.__dict__.get("SAVES", "."))) if False else None
call("rimworld/save_game", saveName=SAVE)
time.sleep(6)
res["save_tick"] = tick()
res["save_fills"] = fills()[0]
res["save_body"] = body()
run_chunks(12, "A", seqA)
res["seqA"] = seqA
res["body_end"] = body()
res["after_shot"] = shot("headline_after")
# ---- reload the save, repeat
call("rimworld/go_to_main_menu")
for _ in range(60):
    st = (call("rimworld/get_ui_state") or {}).get("programState")
    if st == "Entry":
        break
    time.sleep(2)
try:
    call("rimworld/load_game", saveName=SAVE, ignoreModCompatibility=True)
except Exception as ex:  # noqa: BLE001
    res["loadRaised"] = type(ex).__name__
for _ in range(120):
    try:
        if (call("rimworld/get_ui_state") or {}).get("programState") == "Playing" and call("jawa/map_info").get("tile") is not None:
            break
    except Exception:  # noqa: BLE001
        pass
    time.sleep(3)
mi = call("jawa/map_info")
res["reload_map"] = {"tile": mi.get("tile"), "mapId": mi.get("mapId")}
if mi.get("tile") != 3247:
    call("jawa/set_current_map", mapId=5)
call("jawa/weather_set", weather="Clear", lockWeather=True)
call("jawa/incident_queue_clear")
res["reload_tick"] = tick()
res["reload_fills"] = fills()[0]
res["reload_body"] = body()
seqB = []
run_chunks(12, "B", seqB)
res["seqB"] = seqB
res["reload_shot"] = shot("headline_reloaded_end")
fa = [s["fills"] for s in seqA[3:]]
fb = [s["fills"] for s in seqB]
n = min(len(fa), len(fb))
res["compare"] = {"A_after_save": fa, "B": fb, "identical_prefix": fa[:n] == fb[:n], "n": n}
res["full_A"] = bool(seqA) and all(v == 1 for v in seqA[-1]["fills"])
res["full_B"] = bool(seqB) and all(v == 1 for v in seqB[-1]["fills"])
res["verdict"] = "PASS" if (res["full_A"] and res["full_B"] and fa[:n] == fb[:n]) else "FAIL"
res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
with open(os.path.join(OUT, "headline_result.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print("VERDICT", res["verdict"])
