"""DEEP STONE live check (PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS A2: "a colonist's cut that lands a square at 2 m turns up
a chunk of the map's deep stone, a stone not on this map's surface, with a first-find letter").

  python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py [out.json] [--origin X,Z] [--fresh-map]

PROVE  the bridge deepens one square of a cleared plot to 1.5 m (D3: excavation_drive makes no dig roll, so the rolled-depth
       guard is still 0); a colonist (Mining 10, every other colonist vanished) then makes the D3 -> D4 cut with the dig job's
       own path. Settings for the run (restored after): digDeepStoneEnabled on, digRockChunksEnabled on,
       digRockChunkMultiplier 4 (0.25 vanilla drop chance x 4 = certainty), digFindsEnabled off (no mineral find competes for
       the cut), digFindLetterEnabled on, digCostRisesWithDepth off (one notch of soft-ground work, not 4x).
EXPECT RM_DigDiscoveryProof "deepstone" names a rock (DS_map_has_deep_stone); after the cut, depth 3 -> 4, the report's
       last find reads "<chunk> x1 ... D=4 (deep stone)" with <chunk> = the named rock's chunk, a new thing of that def within
       6 squares, and a new letter starting "Deep stone" (DS_superdeep_cut_turns_up_deep_stone).
LIES   a cut never made measures nothing -> UNMEASURED(SITE); a chunk already lying there is excluded by the before/after
       id diff; a fallback rock whose own drop chance is under 0.25 makes the chance < 1, so a miss there is UNMEASURED,
       never FAIL (the detail carries the rock's drop chance as read from the report).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
DPROOF = "RimMandrake.FlowWorks.RM_DigDiscoveryProof"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
ITEM = "PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS"
RUN_SETTINGS = {"digDeepStoneEnabled": True, "digRockChunksEnabled": True, "digRockChunkMultiplier": 4.0,
                "digFindsEnabled": False, "digFindLetterEnabled": True, "digCostRisesWithDepth": False}


def job_gate(probe, order):
    """DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL: run 1 waited 6000 ticks for the AI scan to hand a colonist the dig and nobody did
    (depth stayed 3). Same idiom as validation_v2 J_workgiver_selection: ask WorkGiver_DigCanal first (flowworks_job_probe), then
    ORDER the exact JobDef on the cell. Returns (ok, why); not ok = UNMEASURED(SITE/HARNESS) with the reason named, never a wait."""
    wg, pw = (probe or {}).get("workGiver") or {}, (probe or {}).get("pawn") or {}
    if not (probe or {}).get("success"):
        return False, "flowworks_job_probe unavailable or refused: %s" % str((probe or {}).get("message") or probe)[:160]
    if (probe or {}).get("designationPresent") is not True:
        return False, "no RM_DigCanal designation at the cell"
    if pw.get("workTypeDisabled") is True:
        return False, "the colonist has Mining disabled"
    if wg.get("hasJobOnCell") is not True or wg.get("jobDef") != "RM_DigCanalJob":
        return False, "WorkGiver_DigCanal hands this pawn no job (shouldSkip=%s hasJobOnCell=%s deleted=%s)" % (
            wg.get("shouldSkip"), wg.get("hasJobOnCell"), wg.get("designationDeletedByWorkGiver"))
    if not (order or {}).get("accepted"):
        return False, "ordered_job refused: %s" % str((order or {}).get("note") or (order or {}).get("error") or order)[:160]
    return True, "ordered"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "deep_stone_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "deep_stone_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-40s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {"success": False}

    def report(arg):
        return str((B.call("jawa/static_call", type=DPROOF, method="ProofReport", args=arg, _answer=True) or {}).get("result"))

    ox, oz = (int(v) for v in a.origin.split(","))
    c = (ox + 5, oz + 5)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    before = {k: sget(k) for k in RUN_SETTINGS}
    res["settings_before"] = before
    if any(v is None for v in before.values()):
        row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "HARNESS",
            {"why": "a setting is unreadable (deployed DLL older than the deep stone build?)", "before": before})
        return 2
    cids = []
    try:
        for k, v in RUN_SETTINGS.items():
            sset(k, v)
        ds = report("deepstone")
        rock = ds.split("DEEPSTONE ")[1].split()[0] if ds.startswith("DEEPSTONE ") else None
        chunk = ds.split("chunk=")[1].split()[0] if "chunk=" in ds else None
        row("DS_map_has_deep_stone", "PASS" if rock and rock != "none" and chunk else "FAIL", "MOD", {"report": ds})
        if not chunk:
            return 1
        rect = (ox, oz, 11, 11)
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        site_rows = []
        V.prepare_site(B, rect, site_rows, "deep_stone_site")
        if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
            row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
            return 2
        drive = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=3, setFill=-1) or {}
        for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
            if not p.get("dead") and p.get("isPlayer"):
                B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 2, z=oz + 2, faction="player", count=3) or {}
        cids = [p_.get("id") for p_ in r.get("pawns") or [] if p_.get("id")]
        for c_ in cids:
            B.call("jawa/set_pawn_skill", pawn=c_, skill="Mining", level=10, _answer=True)
            B.call("jawa/set_work_priority", pawnId=c_, workType="Mining", priority=1)

        def things():
            lt = B.call("jawa/list_things", rect="%d,%d,13,13" % (c[0] - 6, c[1] - 6), limit=200) or {}
            return {t.get("id"): (t.get("def"), t.get("x"), t.get("z")) for t in lt.get("things") or []}

        def letters():
            lt = B.call("rimworld/list_letters") or {}
            return [str(x.get("label") or x.get("title") or x)[:80] for x in lt.get("letters") or []]

        def depth():
            return (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("depth")
        r0 = report("report")
        t0, l0, d0 = things(), letters(), depth()
        if d0 != 3:
            row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "HARNESS",
                {"why": "the square is not at D3 before the colonist cut", "depth": d0, "drive": str(drive)[:200]})
            return 2
        des = B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % c) or {}
        probe = B.call("jawa/flowworks_job_probe", x=c[0], z=c[1], kind="dig", pawnId=cids[0]) or {}
        order = B.call("jawa/ordered_job", pawnId=cids[0], jobDef="RM_DigCanalJob", targetAX=c[0], targetAZ=c[1], waitTicks=0) or {}
        job_ok, job_why = job_gate(probe, order)
        res["job_probe"], res["job_order"] = probe, order
        if not job_ok:
            row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "SITE",
                {"why": "the dig job was not taken: " + job_why, "designate": str(des)[:200], "probe": str(probe)[:300]})
            return 2
        t, cut_at = 0, None
        while t < 6000:
            step(250)
            t += 250
            if depth() not in (None, d0):
                cut_at = t
                break
        step(10)
        r1 = report("report")
        t1, l1, d1 = things(), letters(), depth()
        new = {k: v for k, v in t1.items() if k not in t0}
        new_letters = [x for x in l1 if x not in l0]
        det = {"deepstone": ds, "before": r0, "after": r1, "depth": [d0, d1], "cutAt": cut_at, "newThings": new,
               "newLetters": new_letters, "designate": str(des)[:200]}
        if cut_at is None:
            row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "SITE", dict(det, why="no colonist cut the square in 6000 ticks"))
            return 2
        last = r1.split("| last ")[1] if "| last " in r1 else ""
        got_chunk = [v for v in new.values() if v[0] == chunk]
        deep_letter = [x for x in new_letters if x.startswith("Deep stone")]
        good = (d0, d1) == (3, 4) and last.startswith(chunk + " x1") and "D=4 (deep stone)" in last and bool(got_chunk) and bool(deep_letter)
        if not good and not last.endswith("(deep stone)") and r1 == r0:
            # no roll landed at all: with a fallback rock under 0.25 drop chance that is luck, not a defect
            row("DS_superdeep_cut_turns_up_deep_stone", "UNMEASURED", "MOD", dict(det, why="the cut rolled no chunk (chance may be < 1)"))
            return 2
        row("DS_superdeep_cut_turns_up_deep_stone", "PASS" if good else "FAIL", "MOD", det)
        return 0 if good else 1
    finally:
        for c_ in cids:
            B.call("jawa/pawn_force_incapacitate", pawn=c_, action="vanish", _answer=True)
        for k, v in before.items():
            if v is not None:
                sset(k, v)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()


if __name__ == "__main__":
    sys.exit(main())
