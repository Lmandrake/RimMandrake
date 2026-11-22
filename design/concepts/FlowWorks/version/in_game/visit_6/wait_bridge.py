"""wait_bridge.py: wait (up to 480 s) until this instance's bridge answers; exit 0 answered, 2 not (visit 5 helper, reused in visit 6)."""
import sys, time, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
import validation_core as V
t0 = time.time()
while time.time() - t0 < 480:
    try:
        r = V.Bridge().call("rimworld/get_game_info") or {}
        if r:
            print("answer after %.0fs: %s" % (time.time() - t0, str(r)[:160])); sys.exit(0)
    except Exception as e:
        pass
    time.sleep(10)
print("no answer in 480 s"); sys.exit(2)
