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

def ticks():
    return call("jawa/time_clock").get("ticksGame", 0)

def run(n, speed=4):
    """Advance ~n game ticks. MEASURED 2026-10-09: step_game_ticks ran ~5-14 ticks/s on the 19-mod tier,
    play_for at speed 4 (Ultrafast) ~400/s, so use this. Pauses again at the end."""
    t0 = ticks(); call("jawa/set_game_speed", speed=speed)
    try:
        while ticks() - t0 < n:
            call("rimworld/play_for", durationMs=max(200, min(8000, int((n - (ticks() - t0)) / 0.4))), speed=speed)
    finally:
        call("jawa/set_game_speed", speed=0)
    return ticks() - t0

step = run   # old name

import contextlib
@contextlib.contextmanager
def setting(typeName, **kv):
    """Set mod-settings fields for the body (raw, no ApplySettings) and always restore them."""
    old = {f: call("jawa/mod_settings_field", typeName=typeName, action="get", field=f).get("value") for f in kv}
    try:
        for f, v in kv.items(): need(call("jawa/mod_settings_field", typeName=typeName, action="set", field=f, value=str(v)), "set " + f)
        yield
    finally:
        for f, v in old.items(): call("jawa/mod_settings_field", typeName=typeName, action="set", field=f, value=str(v))

def rect(x, z, w, h): return "%d,%d,%d,%d" % (x, z, w, h)
def cell(x, z): return "%d,%d" % (x, z)

def _tile_objs(tile):
    r = call("jawa/world_objects_get", tiles=str(tile), limit=50)
    return [o for o in (r.get("objects") or []) if o.get("tile") == tile]

def biome_map(tile, biome, size=100, layer=None, keeper=(50, 50)):
    """Generate a map of `biome` on `tile` (any free tile), make it current, and return mapId.
    Pass layer='RM_SeabedLayer' for a sea-floor map. Free it with drop_map(id, tile).
    MEASURED 2026-10-09, two traps: (1) the generated Settlement has NO faction, so after the map is culled its
    CheckDefeated NREs every tick, spawning ~1 DestroyedSettlement and a raid letter per 5 ticks (11,587 objects, play_for
    auto-paused forever); so the settlement is handed to the player faction here and removed by drop_map.
    (2) an unowned map is culled within ~1000 ticks; a player settlement plus a player colonist keeps it."""
    quiet()
    kw = dict(tile=tile, biome=biome, sizeX=size, sizeZ=size)
    if layer: kw["layer"] = layer
    r = need(call("jawa/world_tile_map_generate", **kw), "world_tile_map_generate")
    mid = r["mapId"]
    ids = [str(o["id"]) for o in _tile_objs(tile) if o.get("isSettlement")]
    if ids: call("jawa/world_objects_set", ids=",".join(ids), faction="PlayerColony")
    need(call("jawa/set_current_map", mapId=mid), "set_current_map")
    call("jawa/kill_hostiles", mapId=mid)        # the generated map arrives with armed non-player pawns that shoot the colonists
    call("jawa/spawn_pawn", kindDef="Colonist", x=keeper[0], z=keeper[1], faction="player", count=1)
    return mid

def drop_map(mid, tile=None, back=0):
    call("jawa/set_current_map", mapId=back)
    r = call("jawa/map_drop", mapIndex=mid, notifyPlayer=False)
    if tile is not None:
        ids = [str(o["id"]) for o in _tile_objs(tile)]
        if ids: call("jawa/world_objects_remove", ids=",".join(ids))
    return r

def quiet():
    """Storyteller off + incident queue cleared + hostiles killed. MEASURED 2026-10-09: with the storyteller on, a raid letter
    auto-pauses the game mid-run (play_for returns 'paused externally', run() hangs). Storyteller-off is a static, not saved."""
    a = call("jawa/site_state", storyteller="off", clearIncidentQueue=True)
    call("jawa/kill_hostiles")
    return a

class Scene:
    """A rect of map owned by the scene. Coordinates in methods are relative to (x, z)."""
    def __init__(self, name, x=100, z=100, w=9, h=9):
        self.name, self.x, self.z, self.w, self.h = name, x, z, w, h
        self.pawns = []
    def __enter__(self): quiet(); self.clear(); return self
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
    def put(self, defName, dx, dz, n=None, stuff=None):
        """Spawn a thing (or n of them / a stack of n) at a relative cell."""
        x, z = self.abs(dx, dz)
        kw = dict(ops="%s:%d,%d" % (defName, x, z) + (",%d" % n if n else ""))
        if stuff: kw["stuff"] = stuff
        r = call("jawa/spawn_batch", **kw)
        return need(r, "spawn %s" % defName)
    def power(self, defName="Battery", dx=0, dz=0):
        return self.put(defName, dx, dz)
    def pawn(self, kind, dx, dz, faction="none", count=1):
        x, z = self.abs(dx, dz)
        r = need(call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=count), "spawn_pawn " + kind)
        self.pawns.append(r)
        return (r.get("pawns") or [{}])[0].get("id")
    def colonist(self, dx, dz):
        """A fed, rested, undrafted player colonist; returns its id."""
        pid = self.pawn("Colonist", dx, dz, faction="player")
        call("jawa/set_draft", pawnId=pid, drafted=False)
        for n in ("Food", "Rest"): call("jawa/pawn_need", pawn=pid, action="need", need=n, level=1.0)
        return pid

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

    def grid(self, col=4, gen="WoodFiredGenerator", gx=2, gz=3):
        """Real power: a generator at (gx,gz) and a conduit column at x=col (z 1..h-2). MEASURED: a conduit touching the
        generator's east side joins its net; one on its south side did NOT. Put consumers touching the column (x=col+1)."""
        self.put(gen, gx, gz)
        for dz in range(1, self.h - 1): self.put("PowerConduit", col, dz)
        call("jawa/map_commit", power=True, regions=True)
    def netsize(self, defName):
        t = self.find(defName)
        return (call("jawa/power_net", thing=t["id"]).get("net") or {}) if t else None
    def fuel(self, pid, gen="WoodFiredGenerator", fuel="WoodLog", n=40, ticks=1200):
        """Spawn fuel beside the pawn and order Refuel on the generator; run until it is accepted."""
        g = self.find(gen); x, z = g["x"] - self.x, g["z"] - self.z
        self.put(fuel, 1, self.h - 2, n=n)
        f = self.find(fuel)
        r = self.order(pid, "Refuel", a=g["id"], b=f["id"], count=n)
        run(ticks); return r
    def heat(self, dx, dz, temp):
        x, z = self.abs(dx, dz)
        return call("jawa/room_heat", mode="set", value=temp, x=x, z=z)
    def comp(self, defName, comp, members):
        t = self.find(defName)
        return (call("jawa/comp_read", thing=t["id"], comp=comp, members=members).get("values") if t else None)
    def weather(self, w): return call("jawa/weather_set", weather=w, lockWeather=True)
    def power_on(self, tid, on=True):
        return call("jawa/power_net", thing=tid, forcePowerOn=bool(on))
    def order(self, pid, jobDef, a=None, b=None, count=None, wait=60):
        kw = dict(pawnId=pid, jobDef=jobDef, waitTicks=wait)
        if a: kw["targetAId"] = a
        if b: kw["targetBId"] = b
        if count: kw["count"] = count
        return call("jawa/ordered_job", **kw)
    def find(self, defName):
        """First thing of defName in the rect, or {}."""
        r = call("jawa/list_things", defName=defName, rect=self.rect, includePawns=True)
        return ((r.get("things") if isinstance(r, dict) else None) or [{}])[0]
    def inspect(self, tid):
        r = call("jawa/inspect_string", thingIds=tid)
        return json.dumps(r.get("things") or r, default=str)

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
