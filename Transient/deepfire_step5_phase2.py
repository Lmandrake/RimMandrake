import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

def log(*a):
    print(*a)
    sys.stdout.flush()

with open(r"D:\Luke\dev\Rimworld\Transient\deepfire_step5_ids.json") as f:
    ids = json.load(f)
targets = ids["targets"]
cells = ids["cells"]

# reference cell far from every target, no Deepfire ever applied - a
# baseline for "is it night yet"
REF = (10, 10)

def glow(x, z):
    return call("deepfire/glow_at", x=x, z=z)

log("before time-skip, ref glow:", glow(*REF))

# advance to night: TicksPerHour = 2500. Jump 16h.
r = call("rimworld/step_game_ticks", ticks=40000)
log("step_game_ticks:", json.dumps(r)[:300])

log("after time-skip, ref glow:", glow(*REF))
for name, (x, z) in cells.items():
    log("after time-skip,", name, "glow:", glow(x, z))
