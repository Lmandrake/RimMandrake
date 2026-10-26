"""Live probe of the player_missions fixtures (MISSION_FIXTURE_FIX_RESEARCH_WINDOW_BLINDS re-run, wired as a modcheck
driver by MISSION_PROBE_WIRE_PLAYER_MISSIONS_CHAIN). NOT a player: it runs `player_missions start <mission>` then
`report --json` for each fixed mission and asks only whether the fixture left the game READABLE:

  PM_<m>_fixture        the mission's fixture ops all succeeded (start exit 0)
  PM_chain_tank_baseline_read   the chain mission's start-of-mission tank baseline is not None (a modal window such as
                        Window_ResearchComplete made it None before jawa/clear_ui all)
  PM_<m>_report_reads   report's goal check gave a verdict (PASS/FAIL/TIMEOUT), not UNMEASURED

It does not judge whether a mission is winnable. Writes mission_fixture_result_<stamp>.json (rows + driver_stamp) that
validation.py's `player_missions` chain reads at the current mod hash.

  python.exe src/RimMandrake/FlowWorks/northstar/mission_fixture_probe.py [out.json] [--fresh-map] [--missions canal,pit,chain]
"""
import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

MISSIONS = ("canal", "pit", "chain")
BLIND = ("UNMEASURED", None)


def judge_start(mission, rc, run):
    """(status, class, detail) rows for one started mission; `run` is run.json (None when start left none)."""
    out = []
    if run is None:
        return [("PM_%s_fixture" % mission, "UNMEASURED", "HARNESS", {"why": "start wrote no run.json (rc %s)" % rc})]
    bad = [r.get("tool") for r in run.get("fixture", []) if not r.get("ok")]
    out.append(("PM_%s_fixture" % mission, "PASS" if rc == 0 and not bad else "FAIL", "MOD",
                {"rc": rc, "failed_ops": bad, "ops": len(run.get("fixture", []))}))
    if mission == "chain":
        base = run.get("tank_baseline")
        out.append(("PM_chain_tank_baseline_read", "PASS" if base is not None else "FAIL", "MOD",
                    {"tank_baseline": base, "why": None if base is not None else
                     "baseline None: the tank click read selected nothing (a modal window absorbing input?)"}))
    return out


def judge_report(mission, rep):
    v = (rep or {}).get("verdict")
    return ("PM_%s_report_reads" % mission, "FAIL" if v in BLIND else "PASS", "MOD",
            {"verdict": v, "evidence": (rep or {}).get("evidence")})


def run_mission(PMS, mission, runs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = PMS.main(["--runs", runs, "start", mission])
    start_out = buf.getvalue()[-600:]
    run = rep = None
    try:
        cur = open(os.path.join(runs, "CURRENT"), encoding="utf-8").read().strip()
        with open(os.path.join(runs, cur, "run.json"), encoding="utf-8") as f:
            run = json.load(f)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            PMS.main(["--runs", runs, "report", "--json"])
        rep = json.loads(buf.getvalue())
    except (OSError, ValueError):
        pass
    return rc, run, rep, start_out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--missions", default=",".join(MISSIONS))
    a = ap.parse_args(argv)
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    import player_missions as PMS     # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "mission_fixture_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "mission_fixture_probe.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows,
           "args": vars(a)}
    import driver_stamp
    driver_stamp.stamp(res, B.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-34s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    save()
    runs = tempfile.mkdtemp(prefix="pm_probe_")
    for m in [x for x in a.missions.split(",") if x]:
        if not ok:
            row("PM_%s_fixture" % m, "UNMEASURED", "SITE", {"why": "not playing"})
            continue
        try:
            rc, run, rep, tail = run_mission(PMS, m, runs)
        except BaseException as ex:     # noqa: BLE001 - SystemExit from an unknown mission too
            row("PM_%s_fixture" % m, "UNMEASURED", "HARNESS", {"why": repr(ex)})
            continue
        for r in judge_start(m, rc, run):
            row(*r)
        if run is not None:
            row(*judge_report(m, rep))
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
