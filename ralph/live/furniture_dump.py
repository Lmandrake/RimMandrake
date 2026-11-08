#!/usr/bin/env python3
"""Every artificial building in each played colony (gss_ba_<Look>), for the offline lab: a bed or a table a cord's slack wanders under reads as
the cord plugging into it. Runs on Steve: python.exe ralph/live/furniture_dump.py; writes Transient/lab/ba/buildings_<Look>.json."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
import run_live as RL  # noqa: E402

B = RL.LiveBridge()
st = json.load(open("ralph/live/ba_state.json"))
os.makedirs("Transient/lab/ba", exist_ok=True)
for look, s in st.items():
    r = B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000)
    ox, oz = s["ox"], s["oz"]
    for _ in range(60):
        res = B.call("jawa/list_things", group="BuildingArtificial", rect="%d,%d,%d,%d" % (ox - 15, oz - 20, 110, 50), limit=3000)
        if res.get("success") is not False:
            break
        time.sleep(1)
    things = res.get("things") or []
    print(look, r.get("success"), len(things), json.dumps(things[0])[:300] if things else res)
    json.dump({"look": look, "ox": ox, "oz": oz, "things": things}, open("Transient/lab/ba/buildings_%s.json" % look, "w"))
