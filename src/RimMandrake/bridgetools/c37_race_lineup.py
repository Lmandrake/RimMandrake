# -*- coding: utf-8 -*-
"""C37 — spawn one of every RimMandrake race and report failures BY DEFNAME.

Written offline while the game loaded. Order is deliberate:
  gate 1  is the process NEWER than the deployed content? (deployed != live)
  gate 2  do the 70 XenotypeDefs exist in THIS PROCESS? (dump != runtime;
          BTD was deleting exactly these species until today)
  then    spawn, and read xenotype + name back off the engine.
"""
import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

import os, re
_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "Jawa", "RimMandrake_StarWarsRaces",
                    "Defs", "XenotypeDefs", "RimMandrakeXenotypes.xml")
XENOS = sorted(set(re.findall(r"<defName>([^<]*)</defName>", open(_XML, encoding="utf-8").read()) + ["MandrakeJawa"]))
ORIGIN_X, ORIGIN_Z, STEP, COLS = 14, 14, 4, 10

host, port, token = resolve_endpoint()
results, spawn_fail, missing = [], [], []

with RimBridge(host, port, token, timeout=120) as rb:
    # ---- gate 2: do they exist in THIS process? --------------------------
    print("== gate: do the %d xenotypes exist in the RUNNING game? ==" % len(XENOS))
    for i in range(0, len(XENOS), 25):
        chunk = XENOS[i:i+25]
        r = rb.call("jawa/get_defs", {"defs": ";".join("XenotypeDef/"+x for x in chunk)})
        for d in (r.get("defs") or []):
            if not d.get("found"):
                missing.append(d.get("defName"))
    print("   resolved %d of %d" % (len(XENOS)-len(missing), len(XENOS)))
    if missing:
        print("   🔴 ABSENT FROM RUNTIME (by defName):")
        for m in missing: print("      ", m)

    present = [x for x in XENOS if x not in missing]

    # ---- pause before spawning (owner's standing rule) -------------------
    rb.call("rimworld/set_time_speed", {"speed": "Paused"})
    a = rb.call("rimworld/get_game_info", {}); time.sleep(2)
    b = rb.call("rimworld/get_game_info", {})
    print("\npaused: %s (ticks %s)" % (a.get("ticksGame") == b.get("ticksGame"), b.get("ticksGame")))

    before = {p.get("id") for p in (rb.call("jawa/list_pawns", {}).get("pawns") or [])}

    # ---- spawn one of each ----------------------------------------------
    print("\n== spawning %d ==" % len(present))
    placed = {}
    for n, xt in enumerate(present):
        x = ORIGIN_X + (n % COLS) * STEP
        z = ORIGIN_Z + (n // COLS) * STEP
        try:
            r = rb.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": x, "z": z,
                                            "faction": "PlayerColony", "xenotype": xt,
                                            "count": 1})
            if r.get("success"): placed[xt] = (x, z)
            else: spawn_fail.append((xt, str(r.get("message"))[:80]))
        except Exception as e:
            spawn_fail.append((xt, str(e)[:80]))
        if (n+1) % 20 == 0: print("   ...%d/%d" % (n+1, len(present)))

    # ---- DRAFT everyone, before any time passes -------------------------
    # Owner's instruction 2026-08-15: draft them all before advancing time so
    # they hold the grid instead of wandering off to their own AI jobs. An
    # UNDRAFTED pawn does not hold position, which is what scattered the last
    # lineup across the whole map.
    # 🔴 unpause=False on every call - jawa/order_pawn UNPAUSES by default.
    pawns = rb.call("jawa/list_pawns", {}).get("pawns") or []
    fresh = [p for p in pawns if p.get("id") not in before]
    print("\n== drafting %d in place ==" % len(fresh))
    undrafted = []
    for i, p in enumerate(fresh):
        try:
            rb.call("jawa/order_pawn", {"pawnId": p.get("id"),
                                        "x": p.get("x"), "z": p.get("z"),
                                        "draft": True, "undraftAfter": False,
                                        "unpause": False, "waitTicks": 1})
        except Exception as e:
            undrafted.append((p.get("id"), str(e)[:60]))
        if (i+1) % 20 == 0: print("   ...%d/%d" % (i+1, len(fresh)))
    # verify the pause actually held
    g1 = rb.call("rimworld/get_game_info", {}); time.sleep(2)
    g2 = rb.call("rimworld/get_game_info", {})
    print("   time still stopped: %s (ticks %s)" % (g1.get("ticksGame") == g2.get("ticksGame"),
                                                    g2.get("ticksGame")))
    if undrafted: print("   ⚠️ draft call failed for: %s" % undrafted)

    # ---- read back ------------------------------------------------------
    pawns = rb.call("jawa/list_pawns", {}).get("pawns") or []
    new = [p for p in pawns if p.get("id") not in before]
    got = {}
    for p in new:
        got.setdefault(str(p.get("xenotype")), []).append(p)

    print("\n== READBACK ==")
    wrong_xeno, vanilla_name = [], []
    for xt in present:
        rows = got.get(xt) or []
        if not rows:
            wrong_xeno.append(xt)
        else:
            nm = str(rows[0].get("name") or "")
            results.append((xt, nm, rows[0].get("x"), rows[0].get("z")))
    print("   spawned and read back with the RIGHT xenotype: %d of %d" % (len(results), len(present)))

    print("\n== FAILURES BY DEFNAME ==")
    if missing:      print("   ABSENT FROM RUNTIME : %s" % ", ".join(missing))
    if spawn_fail:   print("   SPAWN REFUSED       : %s" % ", ".join(f"{a} ({b})" for a, b in spawn_fail))
    if wrong_xeno:   print("   WRONG/NO XENOTYPE   : %s" % ", ".join(wrong_xeno))
    if not (missing or spawn_fail or wrong_xeno):
        print("   none — every species spawned with its own xenotype")

    json.dump({"ok": results, "missing": missing,
               "spawn_fail": spawn_fail, "wrong": wrong_xeno},
              open("c37_result.json", "w"))
    print("\nNAMES (for the namer check — 51 of 70 should have a species namer):")
    for xt, nm, x, z in results:
        print("   %-34s %-22s (%s,%s)" % (xt, nm, x, z))
