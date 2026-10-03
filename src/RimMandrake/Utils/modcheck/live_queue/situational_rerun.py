"""situational_rerun: `--situational --policy abort` re-run of every registered suite, in ONE session, on the fixed runner.

Calls runner.run_suite directly (the swap/deploy/compose half of runner.run() is WSL-side and was done once by
prep_wsl.py before launch). Per mod it writes <outdir>/<Mod>_summary.json; the record carries a per-mod digest.

Checks (each can FAIL):
  * no suite raised out of run_suite (a script bug, not a game result);
  * FlowWorks is NOT refused (its validated floor was 38/38 at f9d1b4c70);
  * no component is UNMEASURED by BudgetExceeded (Antiquities' 95000-tick chain now declares tick_cap);
  * every chain established a bland map (watch.bland) -- otherwise its verdicts are not verdicts;
  * every recorded surprise has its evidence on disk (sidecar json; png when a screenshot was taken).
Surprises themselves are LISTED for attribution, not failed: deciding whether a hit is the chain's own act
(Ninefold's induced break) is a reading of the chain, and the fix is a declared expectation in that suite.
`--mods A,B` narrows the set (e.g. a re-run of two suites after a fix).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, main   # noqa: E402


def digest(mod, summary):
    comps = [c for ch in summary.get("chains", []) for c in ch.get("components", [])]
    by = {}
    for c in comps:
        v = c.get("verdict")
        by[v] = by.get(v, 0) + 1
    surprises, budget, unbland = [], [], []
    for ch in summary.get("chains", []):
        sit = ch.get("situational") or {}
        if sit and not sit.get("bland", True):
            unbland.append(ch["name"])
        for s in sit.get("surprises", []) or []:
            surprises.append({"chain": ch["name"], "sidecar": s.get("sidecar"), "png": s.get("png")})
        for c in ch.get("components", []):
            if "BudgetExceeded" in str(c.get("detail")) or "BudgetExceeded" in json.dumps(c.get("surprises"), default=str):
                budget.append("%s/%s" % (ch["name"], c.get("name")))
    hits = sorted({"%s:%s" % (h.get("detector"), h.get("severity"))
                   for ch in summary.get("chains", []) for h in ((ch.get("situational") or {}).get("hits_seen") or [])
                   if h.get("severity") in ("SURPRISE", "FATAL")})
    return {"mod": mod, "refused": summary.get("refused") or "", "verdicts": by,
            "all_green": summary.get("all_green"), "surprises": surprises, "serious_detectors": hits,
            "budget_unmeasured": budget, "unbland_chains": unbland}


def evidence_present(path):
    if not path:
        return False
    p = path
    if not os.path.isabs(p):
        p = os.path.join(ROOT, p)
    try:
        from surprise import to_local_path
        p = to_local_path(p)
    except Exception:                                           # noqa: BLE001
        pass
    return os.path.isfile(p)


def record_summary(mod, summ, path, dry_run, _record=None, _resolve=None):
    """Record one mod's run_suite summary in modcheck_status.json exactly as runner.run() would (same record_run
    arguments: verdict = summary all_green, refused text carried, genuine hash). Returns a note string.
    Never records on a dry run, never invents a PASS: a summary with no all_green key is not recorded."""
    if dry_run:
        return "dry run: not recorded"
    if "all_green" not in summ:
        return "not recorded: summary carries no all_green verdict"
    import time
    refused = summ.get("refused") or ""
    green = bool(summ.get("all_green")) and not refused
    if _resolve is None:
        import runner
        mod_dir = runner.find_mod_dir(mod)
        walk = runner.northstar_for(mod)[0]
    else:
        mod_dir, walk = _resolve(mod)
    rec = _record
    if rec is None:
        import status
        rec = status.record_run
    entry = rec(mod, mod_dir, "%s@%d" % (mod, int(time.time())), green, walk=walk, refused=refused,
                extra={"source": {"verb": "situational_rerun", "summary": path}})
    return "recorded %s" % entry.get("status")


def judge(job, digests, crashed):
    job.check("no suite raised out of run_suite", not crashed, crashed)
    fw = [d for d in digests if d["mod"] == "FlowWorks"]
    if fw:
        job.check("FlowWorks ran (not refused)", not fw[0]["refused"], fw[0]["refused"][:300])
    budget = [b for d in digests for b in d["budget_unmeasured"]]
    job.check("no component UNMEASURED by BudgetExceeded (Antiquities chunked)", not budget, budget)
    unbland = ["%s/%s" % (d["mod"], c) for d in digests for c in d["unbland_chains"]]
    job.check("every chain established a bland map", not unbland, unbland)
    missing = []
    for d in digests:
        for s in d["surprises"]:
            if not evidence_present(s["sidecar"]):
                missing.append("%s/%s sidecar" % (d["mod"], s["chain"]))
            if s.get("png") and not evidence_present(s["png"]):
                missing.append("%s/%s png" % (d["mod"], s["chain"]))
    job.check("every recorded surprise has its evidence on disk", not missing, missing)


def body(s, job):
    import runner
    from jobs import suite_mods
    argv = sys.argv[1:]
    mods = suite_mods()
    if "--mods" in argv:
        mods = [m for m in argv[argv.index("--mods") + 1].split(",") if m]
    digests, crashed, recorded = [], [], {}
    if not job.dry_run:        # a freshly launched game sits at the main menu: every suite would die with ClockLost (2026-10-03)
        job.note("map", runner.ensure_playing_map())
    if job.dry_run:
        from suite import Suite
        dry = Suite("DryRun")

        @dry.chain("quiet_wait")
        def _q(t):
            with t.component("waits"):
                t.wait_ticks(600)
        plan = [("DryRun", dry)]
    else:
        plan = []
        for m in mods:
            try:
                plan.append((m, runner.load_validation(runner.find_mod_dir(m))))
            except Exception as e:                              # noqa: BLE001
                crashed.append("%s: load: %s" % (m, e))
    use_world = "--bland-world" in argv
    if use_world:
        # the bland_tile recipe once, then bland_world.reset() between suites (no relaunch)
        import bland_world
        info = bland_world.setup(s, log=lambda *a: print("     bland_world:", *a))
        job.note("bland_world_setup", info)
        job.check("bland world established (tile %s, map %s)" % (info["tile"], info["mapIndex"]),
                  not info["problems"], info["problems"])
    import belt_heartbeat
    for m, suite in plan:
        print("  -- %s" % m)
        belt_heartbeat.step("suite %s" % m, budget_s=belt_heartbeat.DEFAULT_STEP_BUDGET_S)   # hang -> exit 4
        try:
            summ = runner.run_suite(suite, s, mod=None if job.dry_run else m, situational=True, policy="abort",
                                    bland_world=use_world)
        except Exception as e:                                  # noqa: BLE001
            crashed.append("%s: %s: %s" % (m, type(e).__name__, e))
            continue
        with open(os.path.join(job.outdir, "%s_summary.json" % m), "w", encoding="utf-8") as f:
            json.dump(summ, f, indent=1, default=str)
        spath = os.path.join(job.outdir, "%s_summary.json" % m)
        try:
            recorded[m] = record_summary(m, summ, spath, job.dry_run)
        except Exception as e:                                  # noqa: BLE001
            recorded[m] = "RECORDING FAILED (status NOT updated): %s: %s" % (type(e).__name__, e)
            print("     !! %s: %s" % (m, recorded[m]))
        d = digest(m, summ)
        digests.append(d)
        print("     refused=%r verdicts=%s surprises=%d serious=%s" % (d["refused"][:80], d["verdicts"],
                                                                     len(d["surprises"]), d["serious_detectors"]))
    job.note("digests", digests)
    job.note("status_recording", recorded)
    judge(job, digests, crashed)


if __name__ == "__main__":
    sys.exit(main("situational_rerun", body))
