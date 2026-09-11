"""Full-auto: wait for bridge, focus game, load canonical save, prove Playing,
run phase0_export. Prints progress lines (flushed) for the harness monitor."""
import sys, time, subprocess
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")

def say(*a):
    print(*a, flush=True)

LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"

# 1. wait for the bridge token line (fresh token each launch)
deadline = time.time() + 1500
while time.time() < deadline:
    try:
        txt = open(LOG, encoding="utf-8", errors="ignore").read()
        if "Bridge token:" in txt or "GABP" in txt:
            say("BRIDGE-READY line seen")
            break
    except OSError:
        pass
    time.sleep(20)
else:
    say("FATAL: no bridge token within 25 min"); sys.exit(1)

time.sleep(30)  # settle past bridge-up

import game_focus
say("focus:", game_focus.focus_game())

from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()

def call(tool, params=None):
    with RimBridge(h, p, t) as rb:
        return rb.call(tool, params or {})

# 2. sanity: companion registered, program at Entry
pr = call("jawa/load_stall_probe")
say("state at start:", pr.get("programState"))

# 3. load the canonical save, poll to Playing (focus again each minute — focus is fragile)
r = call("rimworld/load_game", {"saveName": "CANONICAL_ASHKARR_2026-09-09"})
say("load_game:", r.get("status"), r.get("success"))
for i in range(60):
    time.sleep(15)
    if i % 4 == 3:
        game_focus.focus_game()
    try:
        st = call("jawa/load_stall_probe").get("programState")
        say(f"[{(i+1)*15}s] {st}")
        if st == "Playing":
            say("PLAYING")
            break
    except Exception as e:
        say("poll err:", str(e)[:70])
else:
    say("FATAL: never reached Playing"); sys.exit(2)

time.sleep(45)  # the 40s reactivity window
# 4. phase 0
say("running phase0_export...")
rc = subprocess.run([sys.executable, r"D:\Luke\dev\Rimworld\Transient\final_review\phase0_export.py"]).returncode
say("PHASE0 exit:", rc)
sys.exit(rc)
