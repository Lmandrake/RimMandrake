import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
with Session(strict=False, quiet=True, focus=False) as s:
    try: print("menu", str(s.call("rimworld/go_to_main_menu"))[:120])
    except Exception as e: print("menu raised", type(e).__name__)
time.sleep(8)
with Session(strict=False, quiet=True, focus=False) as s:
    try: print("start", str(s.call("rimworld/start_debug_game_ready"))[:120])
    except Exception as e: print("start raised (timeout expected)", type(e).__name__)
t0=time.time()
while time.time()-t0<200:
    try:
        with Session(strict=False, quiet=True, focus=False) as s:
            r=s.call("jawa/map_info")
            if r.get("success"):
                print("MAP READY %ds biome=%s tile=%s" % (time.time()-t0, r.get("mapBiome"), r.get("tile"))); break
    except Exception as e: pass
    time.sleep(6)
