"""Load each look's played save and dump its cord world for the offline lab (probe worlddump), copied to the shots folder's ../worlds.
python.exe ralph/live/dump_worlds.py [Look ...]"""
import json, os, shutil, sys, time
sys.path.insert(0, os.path.join(os.getcwd(), "ralph", "live"))
import lived_in as LI  # noqa: E402
from await_lifecycle import await_lifecycle  # noqa: E402
OUT = r"D:\ClaudeWork\rimmandrake\ralph_gss\worlds"
os.makedirs(OUT, exist_ok=True)
for look in sys.argv[1:] or ["Modern", "Scrapper", "Industrial", "Futuristic"]:
    R = LI.Run()
    R.B.call("rimworld/load_game_ready", saveName="gss_ba_%s" % look, timeoutMs=240000)
    await_lifecycle(R.B.call, "map_ready", 240, poll_s=0.5)
    time.sleep(6)
    r = R.B.probe("worlddump:ba_%s" % look)
    print(look, json.dumps(r)[:200])
    src = os.path.join(os.environ.get("RM_GAME_USERDATA", ""), "GssWorlds", "ba_%s.json" % look)
    for _ in range(20):
        if os.path.exists(src):
            break
        time.sleep(0.5)
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(OUT, "ba_%s.json" % look))
