#!/usr/bin/env python3
"""Live proof of the four wreck reads (item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL):
jawa/thing_set_sample, jawa/install_blueprint, jawa/study_record, jawa/processor_fill, and the three of the stage-5 scenes:
jawa/reach_edge, jawa/caravan_mass, jawa/caravan_form_load. Their rules are proven offline by
selftest_wreck_reads.py; this reads each against the game, with a row that must refuse beside each row that must answer.
Run under Windows python.exe on a test game on the Wrecked Machines small list (VFE Factory loaded), after
build.py --gm --apply and a restart:

    python.exe prove_wreck_reads.py

It makes its own quicktest map. Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED (no bridge, or a row that could not look)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

ROWS = []
S = [None]
SMELTER = "VFEFactory_AutomatedSmelter"      # VFE Factory 1.6 (read 2026-11-27); a PipeSystem processor
CHIP = "SignalChip"                          # Biotech: CompAnalyzableUnlockResearch, analysisID 92349061 (RimSage)


def row(name, ok, detail):
    v = "PASS" if ok is True else ("FAIL" if ok is False else "UNMEASURED")
    ROWS.append((name, v))
    print("%-40s %-10s %s" % (name, v, str(detail)[:500]), flush=True)
    return ok is True


def connect():
    host, port, token = rb.resolve_endpoint()
    if not token:
        raise SystemExit("UNMEASURED: no bridge token")
    S[0] = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    S[0].connect()


def call(tool, **p):
    try:
        r = S[0].call(tool, p, check=False) or {}
    except Exception as e:  # noqa: BLE001 - a refusal may arrive as a transport error; it is the reading
        return {"success": False, "_error": "%s: %s" % (type(e).__name__, e)}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except (ValueError, KeyError, IndexError, TypeError):
            pass
    return r if isinstance(r, dict) else {"_raw": r}


def playing(limit=240):
    from await_lifecycle import await_lifecycle
    return bool(await_lifecycle(call, "map_ready", deadline_s=limit))


def quicktest():
    if (call("jawa/companion_handshake").get("game") or {}).get("programState") != "Entry":
        call("rimworld/go_to_main_menu")
    r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    return r.get("success") is not False and playing()


def centre():
    info = call("jawa/map_info")
    sx, sz = int(info.get("sizeX") or 250), int(info.get("sizeZ") or 250)
    return sx // 2, sz // 2


def thing_at(defname, x, z, r=3):
    rows = call("jawa/list_things", defName=defname, rect="%d,%d,%d,%d" % (x - r, z - r, 2 * r + 1, 2 * r + 1)).get("things") or []
    return rows[0]["id"] if rows else None


def clear(x, z, w, h):
    call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (x, z, w, h), categories="Building,Item,Plant")
    call("jawa/set_terrain_batch", terrainDef="Concrete", ops=";".join("%d,%d" % (x + i, z + j) for i in range(w) for j in range(h)))


def prove_sample():
    l = call("jawa/thing_set_sample", kind="list")
    mods = set(str(g.get("mod")).lower() for g in (l.get("thingSetMakers") or []) + (l.get("traders") or []))
    row("sample.list", bool(l.get("success") and "ludeon.rimworld" in mods and len(l.get("traders") or []) > 3),
        "%d sets, %d traders, mods %s" % (len(l.get("thingSetMakers") or []), len(l.get("traders") or []), sorted(mods)[:8]))
    r = call("jawa/thing_set_sample", kind="thingSetMaker", runs=30, **{"def": "MapGen_AncientComplexRoomLoot_Default"})
    rows = r.get("rows") or []
    row("sample.thing_set_maker", bool(r.get("success") and r.get("runs") == 30 and rows and rows[0]["runsWith"] <= 30),
        "runs %s empty %s failed %s, top %s" % (r.get("runs"), r.get("emptyRuns"), r.get("failedRuns"), rows[:3]))
    t = call("jawa/thing_set_sample", kind="trader", runs=5, **{"def": "Orbital_BulkGoods"})
    row("sample.trader_stock", bool(t.get("success") and (t.get("rows") or [])),
        "runs %s, %d defs, top %s" % (t.get("runs"), len(t.get("rows") or []), (t.get("rows") or [])[:3]))
    c = call("jawa/thing_set_sample", kind="thingSetMaker", runs=2001, **{"def": "MapGen_AncientComplexRoomLoot_Default"})
    row("sample.refuses_over_cap", c.get("success") is False and "2000" in str(c), str(c)[:200])
    n = call("jawa/thing_set_sample", kind="thingSetMaker", runs=3, **{"def": "NoSuchMaker"})
    row("sample.refuses_unknown_def", n.get("success") is False, str(n)[:160])


def prove_install(x, z):
    clear(x - 2, z - 2, 24, 10)
    call("jawa/build_batch", ops="StandingLamp:%d,%d" % (x, z), faction="Player")
    call("jawa/build_batch", ops="Wall:%d,%d" % (x + 4, z), faction="Player")
    lamp, wall = thing_at("StandingLamp", x, z), thing_at("Wall", x + 4, z, 0)
    m = call("jawa/thing_minify", thing=lamp) if lamp else {}
    mini = ((m.get("minified") or {}).get("id"))
    r = call("jawa/install_blueprint", thing=mini, x=x + 10, z=z, rot="east") if mini else {}
    bp = r.get("blueprint") or {}
    row("install.blueprint_of_carried", bool(r.get("success") and r.get("mode") == "Install"
                                             and (bp.get("position") or {}).get("x") == x + 10 and bp.get("rotation") == 1),
        "lamp %s minified %s -> %s" % (lamp, mini, str(r)[:240]))
    w = call("jawa/install_blueprint", thing=wall, x=x + 14, z=z) if wall else {"success": None}
    row("install.refuses_a_wall", w.get("success") is False and "minifiable" in str(w), str(w)[:200])
    call("jawa/build_batch", ops="StandingLamp:%d,%d" % (x + 2, z + 4), faction="Player")
    lamp2 = thing_at("StandingLamp", x + 2, z + 4, 0)
    re_ = call("jawa/install_blueprint", thing=lamp2, x=x + 16, z=z + 4) if lamp2 else {}
    row("install.reinstall_of_standing", bool(re_.get("success") and re_.get("mode") == "Reinstall"), str(re_)[:200])
    call("jawa/build_batch", ops="Wall:%d,%d" % (x + 18, z), faction="Player")
    blocked = call("jawa/install_blueprint", thing=mini, x=x + 18, z=z) if mini else {"success": None}
    row("install.refuses_a_blocked_cell", blocked.get("success") is False and "refused by the engine" in str(blocked), str(blocked)[:200])


def prove_study():
    r = call("jawa/study_record", **{"def": CHIP})
    projects = r.get("projects") or []
    agree = all(p.get("gameSays") == p.get("completed") for p in projects)
    row("study.record_of_chip", bool(r.get("success") and r.get("analysisID") == 92349061
                                      and r.get("status") in ("no_record", "partial", "complete") and projects and agree),
        "status %s done %s/%s, projects %s" % (r.get("status"), r.get("timesDone"), r.get("required"),
                                               [(p["defName"], p["completed"], p["gameSays"]) for p in projects][:4]))
    s = call("jawa/study_record", **{"def": "Steel"})
    row("study.no_comp_kept_apart", bool(s.get("success") and s.get("status") == "no_study_comp" and not s.get("projects")), str(s)[:200])
    u = call("jawa/study_record", **{"def": "NoSuchThing"})
    row("study.refuses_unknown_def", u.get("success") is False, str(u)[:160])


def prove_fill(x, z):
    clear(x - 3, z - 3, 12, 12)
    call("jawa/set_terrain_batch", terrainDef="VFEF_FactoryFloor", ops=";".join("%d,%d" % (x - 2 + i, z - 2 + j) for i in range(8) for j in range(8)))
    b = call("jawa/build_batch", ops="%s:%d,%d" % (SMELTER, x, z), faction="Player")
    sm = thing_at(SMELTER, x, z)
    if not sm:
        return row("fill.smelter_placed", None, "no %s stood after build_batch: %s" % (SMELTER, str(b)[:200]))
    d = call("jawa/processor_fill", thing=sm, dryRun=True)
    avail = d.get("available") or (d.get("details") or {}).get("available") or []
    row("fill.reads_the_tab_list", bool(avail), "available %s, list %s" % (avail[:6], d.get("processes") or (d.get("details") or {}).get("processes")))
    pick = avail[0] if avail else None
    f = call("jawa/processor_fill", thing=sm, process=pick, add=True) if pick else {"success": None}
    rows = f.get("rows") or []
    row("fill.inputs_placed", bool(f.get("success") and rows and f.get("allFull")
                                   and all(r.get("haveAfter") >= r.get("required") for r in rows if not r.get("net"))),
        "process %s rows %s" % (f.get("process"), rows[:4]))
    again = call("jawa/processor_fill", thing=sm, process=pick) if pick else {}
    row("fill.second_fill_adds_nothing", bool(again.get("success") and all(r.get("used") == 0 for r in again.get("rows") or [])),
        str(again.get("rows"))[:240])
    lamp = None
    call("jawa/build_batch", ops="StandingLamp:%d,%d" % (x + 6, z + 6), faction="Player")
    lamp = thing_at("StandingLamp", x + 6, z + 6, 0)
    n = call("jawa/processor_fill", thing=lamp) if lamp else {"success": None}
    row("fill.refuses_a_non_processor", n.get("success") is False and "CompAdvancedResourceProcessor" in str(n), str(n)[:160])


def prove_reach_and_caravan(x, z):
    clear(x - 6, z - 6, 14, 14)
    ring = ";".join("Wall:%d,%d" % (x + i, z + j) for i in range(-2, 3) for j in range(-2, 3) if abs(i) == 2 or abs(j) == 2)
    call("jawa/build_batch", ops=ring, faction="Player")
    r = call("jawa/reach_edge", cells="%d,%d;%d,%d" % (x, z, x + 5, z + 5))
    rows = r.get("cells") or [{}, {}]
    row("reach.walled_in_and_open", bool(r.get("success") and rows[0].get("canReachEdge") is False and rows[1].get("canReachEdge") is True),
        str(rows)[:240])
    dig = call("jawa/reach_edge", cells="%d,%d" % (x, z), mode="PassAllDestroyableThings")
    # the engine walks regions and a wall has none: a digging mode would read "cannot get out" from any walled cell, so it is refused
    row("reach.refuses_digging_mode", dig.get("success") is False, str(dig)[:200])
    bad = call("jawa/reach_edge", cells="%d,%d" % (x, z), mode="Fly")
    row("reach.refuses_unknown_mode", bad.get("success") is False, str(bad)[:160])
    pawns = [((call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=x + 4 + k, z=z - 4).get("pawns") or [{}])[0]).get("id") for k in range(2)]
    call("jawa/spawn_batch", ops="Steel:%d,%d,75" % (x + 6, z - 5))
    steel = (call("jawa/list_things", defName="Steel", rect="%d,%d,3,3" % (x + 5, z - 6)).get("things") or [{}])[0].get("id")
    light = call("jawa/caravan_mass", pawns=pawns[0], things=steel)
    row("caravan.mass_reads_capacity", bool(light.get("success") and light.get("capacity", 0) > 0 and light.get("usage", -1) >= 0
                                             and light.get("over") is (light.get("usage", 0) > light.get("capacity", 0))), str(light)[:200])
    call("jawa/spawn_batch", ops="Steel:%d,%d,75;Steel:%d,%d,75;Steel:%d,%d,75" % (x + 6, z - 3, x + 7, z - 3, x + 8, z - 3))
    heavy = [r_["id"] for r_ in call("jawa/list_things", defName="Steel", rect="%d,%d,6,6" % (x + 4, z - 6)).get("things") or []]
    over = call("jawa/caravan_mass", pawns=pawns[0], things=",".join(heavy))
    row("caravan.mass_over_when_heavy", over.get("over") is True, str(over)[:200])
    nobody = call("jawa/caravan_form_load", pawns="", things=steel, destTile=0)
    row("caravan.form_refuses_no_pawn", nobody.get("success") is False, str(nobody)[:160])


def main():
    connect()
    if not quicktest():
        row("map", None, "no quicktest map reached Playing")
    else:
        x, z = centre()
        for fn in (prove_sample, lambda: prove_install(x - 30, z - 20), prove_study, lambda: prove_fill(x + 10, z + 10),
                   lambda: prove_reach_and_caravan(x - 30, z + 20)):
            try:
                fn()
            except Exception as e:  # noqa: BLE001 - a crash in one block is that block's UNMEASURED, the others still run
                row("block", None, "%s: %s" % (type(e).__name__, e))
    v = [r[1] for r in ROWS]
    print("prove_wreck_reads: %d PASS, %d FAIL, %d UNMEASURED" % (v.count("PASS"), v.count("FAIL"), v.count("UNMEASURED")))
    return 1 if "FAIL" in v else (2 if "UNMEASURED" in v or not v else 0)


if __name__ == "__main__":
    sys.exit(main())
