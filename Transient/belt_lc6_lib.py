"""Live-check helper for belt_live_checks6 (2026-10-08). Run under python.exe from the repo root."""
import sys as _s
_s.stdout.reconfigure(encoding="utf-8", errors="replace")
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "RimMandrake", "Utils"))
import rimbridge_client as rb
_c = None
def rbc():
    global _c
    if _c is None:
        h, p, t = rb.resolve_endpoint()
        _c = rb.RimBridge(host=h, port=p, token=t, timeout=60.0); _c.connect()
    return _c
def call(tool, **params):
    r = rbc().call(tool, params) or {}
    if isinstance(r, dict) and r.get("content"):
        try: return json.loads(r["content"][0]["text"])
        except Exception: return r["content"][0]["text"]
    return r
def show(x, n=1500):
    s = x if isinstance(x, str) else json.dumps(x, default=str)
    print(s[:n])
def step(n):
    return call("rimworld/step_game_ticks", ticks=n, timeoutMs=120000)
def spawn_pawn(kind, x, z, faction="none", count=1):
    r = call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=count)
    return r
def things(defName, **kw):
    return call("jawa/list_things", defName=defName, includePawns=True, **kw)
def pawn(id):
    return call("jawa/pawn_get", pawn=id)
def census(**kw):
    return call("jawa/pawn_census", **kw)
def job_of(pid):
    r = census()
    for p in r.get("pawns", []):
        if pid in (p.get("id"), p.get("thingId"), p.get("name")): return p
    return None
def wstate(pid, sign="RM_WatcherSign_SandDimple"):
    p = job_of(pid)
    pg = call("jawa/pawn_get", pawn=pid)["pawns"]
    hid = None; pos=None
    if pg:
        hid = any(h["def"] == "RM_WatcherHidden" for h in pg[0]["hediffs"]); pos = pg[0]["position"]
    s = call("jawa/list_things", defName=sign)
    signs = [(t.get("x"), t.get("z")) if "x" in t else t for t in (s.get("things") or [])]
    return {"job": (p or {}).get("job"), "dead": (p or {}).get("dead"), "hidden": hid, "pos": pos, "signs": signs}
def kill(tid, dmg="Bullet", amt=2000):
    return call("jawa/damage", damageDef=dmg, amount=amt, thingId=tid, allowColonists=True)
APROBE = "RimMandrake.GimmeSomeSlack.Aerial.AerialProbe"
def ap(cmd, wait_s=20.0):
    import time
    before = call("jawa/mod_settings_field", typeName=APROBE, action="get", field="serial").get("value")
    s = call("jawa/mod_settings_field", typeName=APROBE, action="set", field="request", value=cmd)
    if not s.get("success"): return {"success": False, "error": "set failed", "raw": s}
    t0 = time.time()
    while time.time() - t0 < wait_s:
        now = call("jawa/mod_settings_field", typeName=APROBE, action="get", field="serial").get("value")
        if now != before:
            res = call("jawa/mod_settings_field", typeName=APROBE, action="get", field="result").get("value")
            try: return json.loads(res)
            except Exception: return {"success": False, "raw": res}
        time.sleep(0.3)
    return {"success": False, "error": "probe timed out"}
