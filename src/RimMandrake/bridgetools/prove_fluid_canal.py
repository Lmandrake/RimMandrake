"""Prove the fluid-canal bridge surface end to end: canal_dig,
canal_cell_report, type_probe — then FLUID_CANAL_FLOOD_LIVE_CHECK_1's three
readings (recoverable / rate / boxed-in expiry). All three PASSED 2026-09-04
on the 21-mod MINIMAL list; this is the harness that proved it.

Run under WINDOWS python.exe after launch_and_wait.sh:
  python.exe D:\\Luke\\dev\\Rimworld\\src\\RimMandrake\\bridgetools\\prove_fluid_canal.py

Traps this harness handles because they each cost a blind stretch once:
- Dialog_NamePlayerFactionAndSettlement (forcePause=true) freezes the sim
  while every bridge call keeps succeeding. Plain window-close RE-QUEUES it;
  only clicking its OK retires it. dismiss_force_pause() does that.
- jawa/set_game_speed takes 'Paused'/'Normal'/'Fast'/'Superfast' strings.
- jawa/time_set_ticks jumps the clock WITHOUT simulating; queued temp-terrain
  removals fire on the next real ticks, so sleep a few seconds after a jump.
"""
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


def cell(x, z):
    r = call("jawa/canal_cell_report", x=x, z=z)
    fl = None
    for t in r.get("things", []):
        if t.get("flood"):
            fl = t["flood"]
    return {"xz": (x, z), "terrain": r.get("terrain"), "temp": r.get("tempTerrain"),
            "under": r.get("underneath"), "flood": fl, "tick": r.get("ticksGame")}


def dismiss_force_pause():
    """Click OK on any forcePause naming dialog; closing it only re-queues it."""
    wl = call("jawa/window_list_close")
    for w in wl.get("windows", []):
        if not w.get("forcePause"):
            continue
        lay = call("rimworld/get_ui_layout")
        for el in json.loads(json.dumps(lay, default=str)).get("elements", []) or []:
            if el.get("label") == "OK" and el.get("actionable"):
                print("dismissing", w["type"], "via", el["targetId"])
                call("rimworld/click_ui_target", targetId=el["targetId"])
                return True
    return False


def wait_flood_gone(x, z, cap_polls=80):
    call("jawa/set_game_speed", speed="Superfast")
    gone_at, last, stuck = None, None, 0
    for i in range(cap_polls):
        time.sleep(4)
        c = cell(x, z)
        if c["flood"] is None:
            gone_at = c["tick"]
            break
        if last and c["tick"] == last["tick"]:
            stuck += 1
            if stuck >= 2 and dismiss_force_pause():
                stuck = 0
        last = c
        print("poll", i, "tick", c["tick"], "flood", c["flood"])
    call("jawa/set_game_speed", speed="Normal")
    return gone_at, (last or {}).get("flood")


# -- 0. map + registration ---------------------------------------------------
call("rimworld/start_debug_game_ready", timeoutMs=280000,
     readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    if call("rimworld/get_ui_state").get("programState") == "Playing":
        break
    time.sleep(1)
names = [t.get("name", "") for t in (S.list_tools() or [])]
mine = [n for n in ("jawa/canal_dig", "jawa/canal_cell_report", "jawa/type_probe") if n in names]
print("REGISTERED:", mine, "of 3")

# -- 1. the DEBUG_SURFACE contrast: AllTypes walker vs the host's tree -------
pr = call("jawa/type_probe", typeName="RimMandrake.FluidCanals.FluidCanalsDebugActions")
print("PROBE inAllTypes:", pr.get("inAllTypesByIdentity"),
      "actions:", [(a.get("name"), a.get("isAllowedNow")) for a in pr.get("debugActions", [])])
tr = call("rimworld/search_debug_actions", query="canal", limit=10)
print("HOST TREE canal matches:", tr.get("totalMatchCount"))

# -- 2. open ground: spring + concrete + dig, rate + recoverability ----------
cx, cz = 125, 125
call("jawa/clear_area", rect="%d,%d,9,9" % (cx - 4, cz - 4), dryRun=False)
call("rimworld/spawn_thing", defName="RM_FluidSpring_Test", x=cx, z=cz)
call("jawa/set_terrain", x=cx - 1, z=cz, terrainDef="Concrete")
d = call("jawa/canal_dig", x=cx + 1, z=cz)
print("DIG:", d.get("terrainNow"), "floodsOnMap:", d.get("floodsOnMap"))
t0 = cell(cx + 1, cz)["tick"]

call("jawa/set_game_speed", speed="Superfast")
time.sleep(10)
call("jawa/set_game_speed", speed="Normal")
c = cell(cx + 1, cz)
if c["flood"]:
    dt = max(1, (c["tick"] or 1) - (t0 or 1))
    print("RATE: %s tiles in %s ticks (~1/%d; PASS if ~60)" %
          (c["flood"]["floodedTileCount"], dt, dt / max(1, c["flood"]["floodedTileCount"])))
gone_at, _ = wait_flood_gone(cx + 1, cz)
print("open flood gone at", gone_at)
print("flooded concrete (1A):", json.dumps(cell(cx - 1, cz), default=str))

jump_to = (gone_at or 10000) + 310000
call("jawa/time_set_ticks", ticks=jump_to)
time.sleep(4)
print("after drain (1B):", json.dumps(cell(cx - 1, cz), default=str))

# -- 3. boxed-in expiry ------------------------------------------------------
call("jawa/make_empty_room", rect="132,132,7,7", floorDef="Sand")
call("rimworld/spawn_thing", defName="RM_FluidSpring_Test", x=135, z=135)
call("jawa/canal_dig", x=136, z=135)
c0 = cell(136, 135)
exp = (c0["flood"] or {}).get("expiresAtTick")
gone_at, last_flood = wait_flood_gone(136, 135)
print("BOXED: gone_at", gone_at, "own expiry", exp, "last state", last_flood,
      "-> PASS" if (gone_at and exp and gone_at <= exp + 600) else "-> FAIL")
call("jawa/time_set_ticks", ticks=(gone_at or 20000) + 320000)
time.sleep(4)
wet = [(x, z) for x in range(133, 138) for z in range(133, 138)
       if cell(x, z)["temp"] == "ShallowFloodwater"]
print("still flooded after drain:", len(wet), wet, "-> PASS" if not wet else "-> FAIL")
print("DONE")
