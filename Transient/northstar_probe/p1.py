import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
with Session(strict=False, quiet=True, focus=False) as s:
    try: r = s.call("rimworld/start_debug_game_ready"); print("start", str(r)[:200])
    except Exception as e: print("start raised (expected timeout):", type(e).__name__)
t0=time.time()
while time.time()-t0 < 150:
    try:
        with Session(strict=False, quiet=True, focus=False) as s:
            r = s.call("jawa/time_clock")
            if r.get("success"): print("MAP UP", json.dumps({k:r[k] for k in r if k in ("ticksGame","paused","curTimeSpeed")}), int(time.time()-t0),"s"); break
    except Exception as e: print("poll", type(e).__name__)
    time.sleep(8)
