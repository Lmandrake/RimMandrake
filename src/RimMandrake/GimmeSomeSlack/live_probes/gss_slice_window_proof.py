"""GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS A1 (L2): no sliced GSS rebuild (a frame's Rebuild(false): snapshot, Build, publish
tail) takes 20 ms or more on the main thread, collections excluded, while lattices of cords pile up on the map.
The live round 6-9 recipe: at each of four sites a 37x37 PowerConduit lattice (step 6, 469 conduits), then its 84
StandingLamps, each spawn preceded by the probe's `slicereset`; after each spawn the probe's `motion` is read until the
build settles (pending 0). Per window: winMaxSliceNoGcMs (the slowest frame rebuild no gen-0 collection landed in), the
sliceWindow record of that slice, winSlices, winSliceGcHits. Round 9 left one window at 44.6 ms (C lamps, first slice:
snapshot clone 20.5 + tail 14.8 ms, no collection counted); the round 10 fix pools the snapshot world.
python.exe (Windows Python: WSL python3 cannot reach the bridge on Windows loopback) with the bridge held; GSS deployed; a quicktest map >= 160x160 (sites are cleared to soil,
unroofed and unfogged first). argv: optional out JSON path (its folder is made). Exit 0 = every window measured and under 20 ms; 1 = a window
at or over 20 ms, or a window that measured nothing (no slice, or the build never settled)."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"
def probe(cmd, wait_s=20.0):
    before = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value")
    call("jawa/mod_settings_field", typeName=PROBE, action="set", field="request", value=cmd)
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value") != before:
            res = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="result").get("value")
            try: return json.loads(res)
            except Exception: return {"success": False, "raw": res}
        time.sleep(0.05)
    return {"success": False, "error": "probe timed out"}
BAR_MS, SIZE, STEP, LAMP = 20.0, 37, 6, 3
SITES = [(20, 20), (80, 20), (20, 80), (80, 80)]
OUT = sys.argv[1] if len(sys.argv) > 1 else None
def cells(x0, z0, lamps):
    out = set()
    for z in range(z0, z0 + SIZE):
        for x in range(x0, x0 + SIZE):
            if not lamps and ((z - z0) % STEP == 0 or (x - x0) % STEP == 0): out.add((x, z))
            if lamps and (((z - z0) % STEP == 0 and (x - x0) % STEP == LAMP) or ((x - x0) % STEP == 0 and (z - z0) % STEP == LAMP)): out.add((x, z))
    return sorted(out)
_pf = call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial")
if not (isinstance(_pf, dict) and _pf.get("success", True) is not False and "value" in _pf):
    # a game without GSS measures nothing about GSS: UNMEASURED (exit 2), never a FAIL (2026-11-03: two false A1 FAILs)
    print("UNMEASURED GimmeSomeSlack is not loaded in the running game (probe type unreadable): %s" % str((_pf or {}).get("message"))[:200])
    sys.exit(2)
res, fails = {"windows": []}, []
call("rimworld/set_time_speed", speed=1)
for i, (x0, z0) in enumerate(SITES):
    rect = "%d,%d,%d,%d" % (x0 - 1, z0 - 1, SIZE + 2, SIZE + 2)
    call("jawa/clear_area", rect=rect, dryRun=False)
    call("jawa/set_terrain_batch", ops="Soil:" + rect)
    call("jawa/set_roof_batch", ops="None:" + rect)
    call("jawa/set_fog", action="unfog", rect=rect)
for i, (x0, z0) in enumerate(SITES):
    for kind, lamps in (("PowerConduit", False), ("StandingLamp", True)):
        tag = "%s %s" % ("ABCD"[i], kind)
        cs = cells(x0, z0, lamps)
        probe("slicereset")
        sp = call("jawa/spawn_batch", ops=";".join("%s:%d,%d" % (kind, a, b) for a, b in cs)) or {}
        t0, m = time.time(), {}
        while time.time() - t0 < 30:
            m = probe("motion")
            if m.get("pending") == 0 and time.time() - t0 > 3: break
            time.sleep(0.2)
        sw = m.get("sliceWindow")
        if isinstance(sw, str):
            try: sw = json.loads(sw)
            except Exception: sw = None
        w = {"tag": tag, "want": len(cs), "spawned": sp.get("spawned"), "pending": m.get("pending"),
             "winMaxSliceNoGcMs": m.get("winMaxSliceNoGcMs"), "winMaxSliceMs": m.get("winMaxSliceMs"),
             "winSlices": m.get("winSlices"), "winSliceGcHits": m.get("winSliceGcHits"), "laidOnCaller": m.get("laidOnCaller"),
             "snapPoolReused": m.get("snapPoolReused"), "snapPoolAllocated": m.get("snapPoolAllocated"),
             "maxNoGc": (sw or {}).get("maxNoGc"), "first": (sw or {}).get("first")}
        res["windows"].append(w)
        mx = w["winMaxSliceNoGcMs"]
        print("%-16s spawned %s/%s slices %s gcHits %s pending %s maxNoGc %s max %s" % (tag, w["spawned"], w["want"], w["winSlices"],
              w["winSliceGcHits"], w["pending"], mx, w["winMaxSliceMs"]), flush=True)
        if w["spawned"] != len(cs): fails.append("%s: spawned %s of %d" % (tag, w["spawned"], len(cs)))
        elif not w["winSlices"] or mx is None: fails.append("%s: UNMEASURED (no slice in the window)" % tag)
        elif w["pending"] != 0: fails.append("%s: never settled (pending %s)" % (tag, w["pending"]))
        elif mx >= BAR_MS: fails.append("%s: slice %.1f ms >= %.0f (record %s)" % (tag, mx, BAR_MS, json.dumps(w["maxNoGc"])[:400]))
res["fails"] = fails
if OUT:
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(OUT, "w") as f: json.dump(res, f, indent=1)
print("FAIL" if fails else "PASS", "; ".join(fails))
sys.exit(1 if fails else 0)
