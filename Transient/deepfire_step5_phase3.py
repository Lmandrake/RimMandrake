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

wall_id = targets["wall"]

log("designate wall:", call("deepfire/designate", thing=wall_id))

log("unpause superfast")
call("rimworld/set_time_speed", speed="Superfast")

coats = 0
for i in range(90):
    c = call("deepfire/comp_coats", thing=wall_id)
    coats = c.get("coats", 0)
    if coats >= 1:
        log("coat reached at poll", i, c)
        break
    time.sleep(2)

log("final wall comp_coats:", call("deepfire/comp_coats", thing=wall_id))
call("rimworld/set_time_speed", speed="Paused")
log("paused. ticksGame:", call("rimworld/get_game_info").get("ticksGame"))

log("wall glow after real job coat1:", call("deepfire/glow_at", x=cells["wall"][0], z=cells["wall"][1]))
