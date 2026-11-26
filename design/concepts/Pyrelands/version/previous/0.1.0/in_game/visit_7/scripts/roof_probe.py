"""python.exe: visit 7 diagnosis of furnacebeast_heats_room. Both 7x7 rooms read openRoofCount 25 after the series on
site tile 193 (visit 6, tile 38: 0). Build the same two rooms at PAD_ROOMS (160, 90) the way furnace_room does, then read
the roofs and walls at 0, +1, +60 and +600 ticks: does make_empty_room never roof, or does a roof go away later?"""
import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

X, Z = 160, 90
A, B = (X - 9, Z - 3, 7, 7), (X + 2, Z - 3, 7, 7)
rs = lambda r: "%d,%d,%d,%d" % r


def u(r):
    return (r or {}).get("result", r) if isinstance((r or {}).get("result"), dict) else (r or {})


def read(rb, tag):
    out = {"tag": tag}
    for name, r in (("A", A), ("B", B)):
        c = (r[0] + 3, r[1] + 3)
        rg = u(rb.call("jawa/room_get", {"x": c[0], "z": c[1]}))
        room = (rg.get("rooms") or [{}])[0]
        ci = u(rb.call("rimworld/get_cells_info", {"x": r[0] + 1, "z": r[1] + 1, "width": 5, "height": 5}))
        cells = ci.get("cells") or []
        roofs = collections.Counter(str(cc.get("roof") or cc.get("roofDef")) for cc in cells)
        terr = collections.Counter(str(cc.get("terrain") or cc.get("terrainDef")) for cc in cells)
        ex = u(rb.call("jawa/export_things", {"rect": rs(r), "includePawns": False, "includeItems": True, "limit": 500}))
        things = collections.Counter(str(t.get("def")) for t in ex.get("things") or [])
        out[name] = {"openRoofCount": room.get("openRoofCount"), "cellCount": room.get("cellCount"),
                     "temperature": room.get("temperature"), "usesOutdoorTemperature": room.get("usesOutdoorTemperature"),
                     "roofs": dict(roofs), "terrain": dict(terr), "things": dict(things)}
    print(json.dumps(out))
    sys.stdout.flush()


h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    print(json.dumps({"keys_cell": sorted(((u(rb.call("rimworld/get_cells_info", {"x": X, "z": Z, "width": 1, "height": 1})).get("cells") or [{}])[0]).keys())}))
    read(rb, "before (site as loaded)")
    print(json.dumps({"destroy": u(rb.call("jawa/destroy_batch", {"rects": "%d,%d,40,40" % (X - 20, Z - 20), "categories": "All"})).get("success")}))
    for r in (A, B):
        m = u(rb.call("jawa/make_empty_room", {"rect": rs(r), "stuffDef": "Steel", "doorDef": "Wall"}))
        print(json.dumps({"make_empty_room": rs(r), "success": m.get("success"), "message": m.get("message"),
                          "keys": sorted(m.keys())[:30]}))
    read(rb, "+0 after make_empty_room")
    for n in (1, 60, 600):
        a = u(rb.call("jawa/safe_advance", {"ticks": n, "timeoutMs": 60000}))
        print(json.dumps({"advance": n, "executed": a.get("executed"), "stopped": a.get("stopped") or a.get("why")}))
        read(rb, "+%d" % n)
