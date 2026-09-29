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

wall_id = "Thing_Wall37288"
pawn_id = "Thing_Human543"

for i in range(40):
    c = call("deepfire/comp_coats", thing=wall_id)
    coats = c.get("coats", 0)
    cur = call("rimworld/list_colonists")
    cj = next((x.get("job") for x in cur.get("colonists", []) if x.get("pawnId") == pawn_id), None)
    log("poll", i, "coats", coats, "job", cj, "tick", call("rimworld/get_game_info").get("ticksGame"))
    if coats >= 1:
        break
    call("rimworld/step_game_ticks", ticks=200)

g = call("deepfire/glow_at", x=123, z=135)
log("done. final glow near wall:", g.get("groundGlow"), g.get("visual"))
