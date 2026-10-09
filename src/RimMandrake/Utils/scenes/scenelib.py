"""Scene harness: cheap live scenes over the RimBridge. Run under python.exe from the repo root.

    from scenes import scenelib as S
    with S.Scene("dark_room", x=100, z=100, w=9, h=9) as sc:
        sc.room(roof=True); sc.put("StandingLamp", 2, 2); sc.power(); print(sc.glow(4, 4))

Facts baked in (all MEASURED live 2026-10-09): rects and cells are STRINGS "x,z,w,h" / "x,z"
(a dict raises InvalidCastException); pawns are killed with jawa/damage, never destroy_batch;
sky_glow_set is overwritten next frame (use time_set_ticks for a lasting hour).
"""
import sys as _s
_s.stdout.reconfigure(encoding="utf-8", errors="replace")
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import rimbridge_client as rb

_c = None
def rbc():
    global _c
    if _c is None:
        h, p, t = rb.resolve_endpoint()
        _c = rb.RimBridge(host=h, port=p, token=t, timeout=60.0); _c.connect()
    return _c

def call(tool, **params):
    """Bridge call; returns the parsed JSON dict (or raw text). Never raises on success:false."""
    r = rbc().call(tool, params, check=False) or {}
    if isinstance(r, dict) and r.get("content"):
        try: return json.loads(r["content"][0]["text"])
        except Exception: return r["content"][0]["text"]
    return r

def ok(r):
    return isinstance(r, dict) and r.get("success") is True

def need(r, what):
    if not ok(r): raise RuntimeError("%s failed: %s" % (what, json.dumps(r, default=str)[:300]))
    return r

def step(n):
    return call("rimworld/step_game_ticks", ticks=n, timeoutMs=300000)

def rect(x, z, w, h): return "%d,%d,%d,%d" % (x, z, w, h)
def cell(x, z): return "%d,%d" % (x, z)

class Scene:
    """A rect of map owned by the scene. Coordinates in methods are relative to (x, z)."""
    def __init__(self, name, x=100, z=100, w=9, h=9):
        self.name, self.x, self.z, self.w, self.h = name, x, z, w, h
        self.pawns = []
    def __enter__(self): self.clear(); return self
    def __exit__(self, *a): self.teardown()
    def abs(self, dx, dz): return self.x + dx, self.z + dz
    @property
    def rect(self): return rect(self.x, self.z, self.w, self.h)

    # ---- build
    def room(self, roof=True, stuff="BlocksGranite", floor="TileGranite"):
        kw = dict(rect=self.rect, stuffDef=stuff, floorDef=floor)
        if roof: kw["roofDef"] = "RoofConstructed"
        return need(call("jawa/make_empty_room", **kw), "make_empty_room")
    def floor(self, terrain, rel=None):
        r = rel or (0, 0, self.w, self.h)
        return call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, rect(self.x + r[0], self.z + r[1], r[2], r[3])), layer="top")
    def put(self, defName, dx, dz, stuff=None, rot=None):
        """Spawn one thing at a relative cell."""
        x, z = self.abs(dx, dz)
        kw = dict(ops="%s:%d,%d" % (defName, x, z))
        r = call("jawa/spawn_batch", **kw)
        return need(r, "spawn %s" % defName)
    def power(self, defName="Battery", dx=0, dz=0):
        return self.put(defName, dx, dz)
    def pawn(self, kind, dx, dz, faction="none", count=1):
        x, z = self.abs(dx, dz)
        r = need(call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=count), "spawn_pawn " + kind)
        self.pawns.append(r)
        return r
    def colonist(self, dx, dz):
        return self.pawn("Colonist", dx, dz, faction="PlayerColony")

    # ---- act
    def hediff(self, pawn, hediff, severity=0.5):
        return call("jawa/pawn_health", pawn=pawn, action="add", hediff=hediff, severity=severity)
    def time_of_day(self, hour):
        """Set the local hour (0-24) by moving the tick counter; lasting, unlike sky_glow_set."""
        clk = call("jawa/time_clock"); cur = call("jawa/glow_at", cells="%d,%d" % (self.x, self.z)).get("hour", 0.0)
        delta = ((hour - cur) % 24.0) * 2500
        return call("jawa/time_set_ticks", ticks=int(clk["ticksGame"] + delta))
    def kill(self, tid):
        return call("jawa/damage", damageDef="Bullet", amount=5000, thingId=tid, allowColonists=True)
    def kill_hostiles(self): return call("jawa/kill_hostiles")

    # ---- read
    def glow(self, dx, dz):
        x, z = self.abs(dx, dz)
        return call("jawa/glow_at", cells=cell(x, z))["cells"][0]["groundGlow"]
    def temp(self, dx, dz):
        x, z = self.abs(dx, dz); return call("jawa/cell_temperature", cell=cell(x, z)).get("temperature")
    def things(self, defName=None, rel=True):
        kw = dict(rect=self.rect, includePawns=True)
        if defName: kw["defName"] = defName
        return call("jawa/list_things", **kw)
    def pawn_state(self, pid): return call("jawa/pawn_get", pawn=pid)
    def hediffs(self, pid):
        pg = (self.pawn_state(pid) or {}).get("pawns") or []
        return [h["def"] for h in pg[0]["hediffs"]] if pg else None

    # ---- teardown
    def clear(self):
        """Strip roof and destroy every thing in the rect (GenDebug.ClearArea). Pawns are killed
        by damage first because destroy-style calls leave them standing."""
        r = self.things()
        for t in (r.get("things") or []) if isinstance(r, dict) else []:
            if t.get("isPawn") or t.get("kind") == "Pawn": self.kill(t.get("id"))
        return call("jawa/clear_area", rect=self.rect, dryRun=False)
    def teardown(self):
        self.clear()
