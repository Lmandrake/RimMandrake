#!/usr/bin/env python3
"""gss_playtest_runner.py - launcher for the Gimme Some Slack in-game scenario runner (JawaBenchGssPlaytest.cs).

    python.exe D:\\Luke\\dev\\RimMandrake\\src\\RimMandrake\\GimmeSomeSlack\\northstar\\gss_playtest_runner.py [--recipe quick]
        [--seed 1] [--tick-mode batch|speed] [--budget-ms 50] [--poll 2] [--timeout 1500] [--force] [--no-resume]

Same shape as FlowWorks' playtest_runner.py, whose journal/verdict/timing logic this reuses unchanged: three bridge
tools (jawa/gss_playtest_start / _status / _collect), the run advances inside the game across frames, the journal
is re-read and its verdict re-derived here, and copied to Transient/gss_playtest/.

Recipes: quick (cords,hose_bend,ui), full (cords,hose_bend,hose_carry,soak,ui,save_reload), or a comma list of
cords, hose_bend, hose_carry, soak, ui, save_reload, save_reload_b. save_reload is two-phase exactly like
FlowWorks': the first half saves and writes PENDING, this launcher loads that save (rimworld/load_game_ready) and runs
save_reload_b with resume=<first runId>.

Needs python.exe (the bridge binds Windows loopback), a running game with a map, GSS on the mod list, and a companion
DLL that carries the tools (built by src/RimMandrake/bridgetools/build.py, deployed only with --apply while the game is
DOWN). The run MODIFIES THE MAP - scratch maps only.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar"))
import playtest_runner as P  # noqa: E402

TOOLS = {"start": "jawa/gss_playtest_start", "status": "jawa/gss_playtest_status", "collect": "jawa/gss_playtest_collect"}
SCENES = ("cords", "hose_bend", "hose_carry", "soak", "ui", "save_reload", "save_reload_b")
RECIPES = {"quick": ("cords", "hose_bend", "ui"), "full": ("cords", "hose_bend", "hose_carry", "soak", "ui", "save_reload")}


def expand(recipe):
    """Recipe -> scene list (pure; mirrors GssParseRecipe in the C#). Unknown names raise ValueError."""
    out = []
    for raw in (recipe or "quick").split(","):
        s = raw.strip().lower()
        if not s:
            continue
        if s in RECIPES:
            out.extend(RECIPES[s])
        elif s in SCENES:
            out.append(s)
        else:
            raise ValueError("unknown scene %r (known: %s; recipes %s)" % (s, ", ".join(SCENES), ", ".join(RECIPES)))
    return out


def run_once(s, calls, a, recipe, resume=None):
    t0 = time.time()
    p = dict(recipe=recipe, seed=a.seed, tickMode=a.tick_mode, frameBudgetMs=a.budget_ms, force=a.force)
    if resume:
        p["resume"] = resume
    st = P._call(s, calls, TOOLS["start"], **p)
    if not st.get("success"):
        print("START REFUSED: %s" % st.get("message", st))
        return None
    run_id = st["runId"]
    print("run %s  scenarios=%s  mode=%s%s" % (run_id, ",".join(st["scenarios"]), st["tickMode"], "  resume=" + resume if resume else ""))
    seen = 0
    while True:
        time.sleep(a.poll)
        stat = P._call(s, calls, TOOLS["status"], runId=run_id)
        recs = stat.get("records") or []
        for r in recs[seen:]:
            print("  %-12s %-8s %6.2fs %6d ticks  %s" % (r["name"], P.mark(r), r["wallSec"], r["ticks"], (r.get("reason") or "")[:300]))
        seen = len(recs)
        if stat.get("state") != "running":
            break
        if time.time() - t0 > a.timeout:
            print("LAUNCHER TIMEOUT after %.0f s; the run is still going in game" % (time.time() - t0))
            break
    col = P._call(s, calls, TOOLS["collect"], runId=run_id)
    path = col.get("reportPath")
    if not path or not os.path.exists(path):
        print("COLLECT: no readable journal (%s); C# verdict %s" % (path, col.get("verdict")))
        return None
    with open(path, encoding="utf-8") as f:
        recs, torn = P.parse_journal(f.read())
    os.makedirs(a.out_dir, exist_ok=True)
    copy = os.path.join(a.out_dir, os.path.basename(path))
    with open(copy, "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(r) for r in recs) + "\n")
    v = P.verdict(recs)
    print()
    print(P.timing_table(recs, {"wall": time.time() - t0, "calls": calls[0]}))
    if v != col.get("verdict"):
        print("VERDICT DISAGREEMENT: file says %s, C# collect says %s" % (v, col.get("verdict")))
    print("RUN VERDICT %s  (%d records%s)  copy %s" % (v, len(recs), ", %d torn" % torn if torn else "", copy))
    return recs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recipe", default="quick")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tick-mode", default="batch", choices=("batch", "speed"))
    ap.add_argument("--budget-ms", type=int, default=50)
    ap.add_argument("--poll", type=float, default=2.0)
    ap.add_argument("--timeout", type=float, default=1500.0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--resume", default=None)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--out-dir", default=os.path.join(REPO, "Transient", "gss_playtest"))
    a = ap.parse_args(argv)
    expand(a.recipe)   # refuse a typo before touching the game
    calls = [0]
    s = P._connect()
    recs = run_once(s, calls, a, a.recipe, a.resume)
    if recs is None:
        return 2
    final = P.verdict(recs)
    pend = P.pending_resume(recs)
    if pend and not a.no_resume:
        ev = pend.get("evidence") or {}
        print("\nRESUME: loading %s (tick %s)" % (ev.get("saveName"), ev.get("ticksAtSave")))
        t = time.time()
        calls[0] += 1
        lr = s.call("rimworld/load_game_ready", {"saveName": ev.get("saveName")}) or {}
        if isinstance(lr, dict) and lr.get("content"):
            try:
                lr = json.loads(lr["content"][0]["text"])
            except (ValueError, KeyError, IndexError, TypeError):
                pass
        while lr.get("success") and time.time() - t < 180:
            gi = P._call(s, calls, "rimworld/get_game_info")
            tk = gi.get("ticksGame")
            if (gi.get("mapCount") or 0) >= 1 and isinstance(tk, int) and 0 < tk <= (ev.get("ticksAtSave") or 0) + 5:
                break
            time.sleep(1.0)
        second = run_once(s, calls, a, ev.get("resumeRecipe"), pend.get("runId")) if lr.get("success") else None
        final = P.combine(recs, second)
    elif pend:
        print("save_reload armed and NOT resumed (--no-resume): verdict stays INCOMPLETE")
    print("\nVERDICT %s" % final)
    return 0 if final in ("PASS", "XFAIL") else 1


if __name__ == "__main__":
    sys.exit(main())
