#!/usr/bin/env python3
"""Live proof that bridge tools no longer report a success the game did not show (RIMMANDRAKE_TELL_TRUE_BRIDGE_TOOL_OUTCOME)
and that the main-thread hops of RIMMANDRAKE_BOUND_BRIDGE_MAIN_THREAD_WORK answer, and that designate_batch
HarvestPlant takes a grown tree (RIMMANDRAKE_LET_BRIDGE_CHOP_TREES_NOT_ONLY_CROPS).

Run under Windows python.exe, after build.py --gm --apply and a restart, on a TEST-profile quicktest map (never a
campaign save; never a flyer). Only the tree row writes to the map, and it removes what it added:
  build_batch_failed_op_is_failure   build_batch with one out-of-bounds op: success=false, partial=false, failedCount 1
                                     (the old companion answered success=true with placed 0)
  map_comp_timing_paused_unmeasured  on a paused game, map_comp_timing ticks=60 maxSeconds=3: success=false and the
                                     error says UNMEASURED (no tick ran); the game is left paused, as it was set
  debug_action_yielders_answers      debug_action_yielders query=zzz_no_match: success, yieldersInvoked > 0 (each
                                     yielder now runs on the main thread, one hop each)
  designate_harvest_grown_tree       designate_batch add HarvestPlant on one vanilla Plant_Tree* cell at a time, up to
                                     40 trees: PASS when one reads added=1 (the old companion gave skippedWrongType=1 on
                                     every tree), then that designation is removed. UNMEASURED when no vanilla tree
                                     stands on the map.
Not covered live, each because no safe failing input exists on a quicktest map; the code is the argument:
  trade_execute (needs a trader and a refused deal), lord_job SetJob throw, render save over a stale file,
  forecast_incidents snapshot failure, kit split merge-back (needs a ground stack staged at its own cell).
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED (no bridge, no map, or a row that could not look).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

rows = []


def row(name, verdict, detail):
    rows.append((name, verdict))
    print("%-38s %-10s %s" % (name, verdict, str(detail)[:220]))


def main():
    host, port, token = rb.resolve_endpoint()
    if not token:
        print("UNMEASURED: no bridge token in Player.log")
        return 2
    S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
    S.connect()

    def call(tool, check=True, **p):
        try:
            r = S.call(tool, p, check=check) or {}
        except Exception as e:  # noqa: BLE001 - a refusal may arrive as a transport error; it is the reading
            return {"_error": "%s: %s" % (type(e).__name__, e)}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except (ValueError, KeyError, IndexError, TypeError):
                pass
        return r if isinstance(r, dict) else {"_raw": r}

    mi = call("jawa/map_info")
    if mi.get("success") is not True:
        print("UNMEASURED: no map (%s)" % mi)
        return 2

    r = call("jawa/build_batch", ops="Wall:99999,99999", readBack=0)
    row("build_batch_failed_op_is_failure",
        "PASS" if r.get("success") is False and r.get("partial") is False and r.get("failedCount") == 1
        and r.get("placed") == 0 else "FAIL", r)

    call("rimworld/pause_game", pause=True)
    r = call("jawa/map_comp_timing", ticks=60, maxSeconds=3, top=3)
    row("map_comp_timing_paused_unmeasured",
        "PASS" if r.get("success") is False and "UNMEASURED" in str(r.get("error")) and r.get("ticksElapsed") == 0
        else "FAIL", {k: r.get(k) for k in ("success", "error", "ticksElapsed", "patchedMethods", "_error")})

    r = call("jawa/debug_action_yielders", query="zzz_no_match", limit=10, maxMillis=3000)
    row("debug_action_yielders_answers",
        "PASS" if r.get("success") is True and (r.get("yieldersInvoked") or 0) > 0 else "FAIL",
        {k: r.get(k) for k in ("success", "yieldersInvoked", "yieldersFailed", "stopReason", "_error")})

    lt = call("jawa/list_things", group="Plant", limit=5000)
    trees = [t for t in (lt.get("things") or []) if str(t.get("def", "")).startswith("Plant_Tree")]
    if lt.get("success") is not True:
        row("designate_harvest_grown_tree", "UNMEASURED", {"list_things": lt})
    elif not trees:
        row("designate_harvest_grown_tree", "UNMEASURED",
            "no vanilla Plant_Tree* on the map (scanned %s plants)" % lt.get("scanned"))
    else:
        tried, hit = [], None
        for t in trees[:40]:
            cell = "%d,%d,1,1" % (t["x"], t["z"])
            r = call("jawa/designate_batch", action="add", designation="HarvestPlant", rect=cell)
            tried.append((t["def"], r.get("added"), r.get("skippedWrongType"), r.get("alreadyPresent")))
            if r.get("success") is True and r.get("added") == 1:
                hit = (t, cell)
                call("jawa/designate_batch", action="remove", designation="HarvestPlant", rect=cell)
                break
        row("designate_harvest_grown_tree", "PASS" if hit else "FAIL",
            {"hit": hit and hit[0].get("def"), "tried": tried[:6], "triedCount": len(tried)})

    fails = [n for n, v in rows if v == "FAIL"]
    unmeasured = [n for n, v in rows if v == "UNMEASURED"]
    print("\n%d row(s), %d FAIL, %d UNMEASURED" % (len(rows), len(fails), len(unmeasured)))
    return 1 if fails else (2 if unmeasured else 0)


if __name__ == "__main__":
    sys.exit(main())
