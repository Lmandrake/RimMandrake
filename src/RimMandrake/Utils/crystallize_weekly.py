#!/usr/bin/env python3
"""crystallize_weekly.py - the weekly Crystallize pass runs by itself (RIMMANDRAKE_REVIVE_WEEKLY_CRYSTALLIZE_RAN_31_DAYS_APART).

The pass ran 2026-10-19 and 2026-11-19, 31 days apart, because nothing scheduled it. The Conductor decided on 2026-11-23:
a weekly scheduled run, not a reminder (his card of that day gave the daily improvement pass's work to this pass).
Rule: design/RimMandrake/standing_rulings.md §The weekly Crystallize pass improves the agents. Page:
design/specs/2026-11-25-weekly-crystallize-run/boundary.md.

    crystallize_weekly.py tick [--apply]   rm-crystallize.timer, daily. When this ISO week has no FINAL report and no
                                           good launch, file the week's item (RIMMANDRAKE_RUN_WEEKLY_CRYSTALLIZE_<YYYY>W<WW>)
                                           if it is not on the ledger, and launch it as a detached opus helper with the
                                           brief crystallize_weekly_brief.md. Plan only without --apply. Writes READING.
    crystallize_weekly.py report WEEK      exit 0 when <conductor>/crystallize_WEEK/CYCLE_REPORT.md holds `Status: FINAL`
                                           (the week item's outcome check), else 1
    crystallize_weekly.py fresh            exit 0 when rm-crystallize.timer is enabled and active AND the newest FINAL
                                           report is of this ISO week or the week before; else 1; 2 could not look
                                           (the repair item's outcome check: the pass runs weekly by itself)

<conductor> is `agent_storage.py rimmandrake`/conductor; RM_CRYSTALLIZE_DIR overrides it (tests).
"""
import argparse
import datetime as DT
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(ROOT, "src", "RimMandrake", "rimflow")
TIMER = "rm-crystallize.timer"
ITEM_PREFIX = "RIMMANDRAKE_RUN_WEEKLY_CRYSTALLIZE_"
FINAL_RX = re.compile(r"^Status:\s*FINAL\b", re.M)
TERMINAL = ("done", "dropped", "superseded")
sys.path.insert(0, HERE)
import time_budget  # noqa: E402

LAUNCH_TIMEOUT_S = time_budget.LAUNCH_S     # hang guard on one `cli.py file` or `detached_helper.py launch`
# budget: danger=a spend-capped pass relaunched without end; one continuation after a cap stop, then the week waits for
# a hand (detached_helper --continue-on-cap)
CONTINUE_ON_CAP = 1


def storage():
    if os.environ.get("RM_CRYSTALLIZE_DIR"):
        return os.environ["RM_CRYSTALLIZE_DIR"]
    helper = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
    r = subprocess.run([sys.executable, helper, "rimmandrake"], capture_output=True, text=True, timeout=60)
    root = (r.stdout or "").strip()
    if r.returncode or not root:
        raise SystemExit("crystallize_weekly: agent_storage.py rimmandrake gave no root (rc %s): %s"
                         % (r.returncode, (r.stderr or "").strip()))
    return os.path.join(root, "conductor")


def reading_dir(conductor):
    return os.path.join(os.path.dirname(conductor.rstrip("/")), "crystallize_weekly")


def week_of(day):
    y, w, _ = day.isocalendar()
    return "%dW%02d" % (y, w)


def monday(week):
    m = re.fullmatch(r"(\d{4})W(\d{2})", week)
    if not m:
        raise ValueError("not a week: %r" % week)
    return DT.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)


def item_id(week):
    return ITEM_PREFIX + week


def reports(conductor):
    """-> [(week, path, final)] for every crystallize_<week>/CYCLE_REPORT.md, oldest week first."""
    out = []
    for p in glob.glob(os.path.join(conductor, "crystallize_*", "CYCLE_REPORT.md")):
        week = os.path.basename(os.path.dirname(p))[len("crystallize_"):]
        try:
            monday(week)
            with open(p, encoding="utf-8", errors="replace") as f:
                final = bool(FINAL_RX.search(f.read()))
        except (ValueError, OSError):
            continue
        out.append((week, p, final))
    return sorted(out, key=lambda r: monday(r[0]))


def newest_final(conductor, before=None):
    rs = [r for r in reports(conductor) if r[2] and (before is None or monday(r[0]) < monday(before))]
    return rs[-1] if rs else None


def decide(week, final_this_week, state, launched_this_week):
    """Pure. -> (act, why). act: none | file+launch | launch."""
    if final_this_week:
        return "none", "the %s report is FINAL" % week
    if state in TERMINAL:
        return "none", "%s is %s" % (item_id(week), state)
    if launched_this_week:
        return "none", "%s was launched this week; the detached run owns it (finish, continuation)" % item_id(week)
    return ("file+launch" if state is None else "launch"), "no FINAL report for %s" % week


def item_state(iid):
    sys.path.insert(0, RIMFLOW)
    import model
    w = model.replay(model.read())
    it = w.items.get(iid)
    return getattr(it, "state", None) if it else None


def history(rdir):
    try:
        with open(os.path.join(rdir, "history.jsonl"), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]
    except (OSError, ValueError):
        return []


def record(rdir, rec):
    os.makedirs(rdir, exist_ok=True)
    tmp = os.path.join(rdir, "last.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(tmp, os.path.join(rdir, "last.json"))
    with open(os.path.join(rdir, "history.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def brief(week, conductor, prev):
    with open(os.path.join(HERE, "crystallize_weekly_brief.md"), encoding="utf-8") as f:
        text = f.read()
    folder = os.path.join(conductor, "crystallize_" + week)
    return (text.replace("{WEEK}", week).replace("{ITEM}", item_id(week)).replace("{FOLDER}", folder)
            .replace("{PREV}", prev[1] if prev else "none: no earlier FINAL report in %s" % conductor)
            .replace("{PREV_WEEK}", prev[0] if prev else "none"))


def opus_cap():
    with open(os.path.join(RIMFLOW, "list_dispatch.json"), encoding="utf-8") as f:
        return json.load(f)["opus_cap_usd"]     # the one runaway-spend cap of an opus helper; its danger is doc'd there


def run(argv):
    r = subprocess.run(argv, capture_output=True, text=True, timeout=LAUNCH_TIMEOUT_S, stdin=subprocess.DEVNULL, cwd=ROOT)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def tick(apply, now=None):
    now = now or DT.datetime.now()
    conductor = storage()
    rdir = reading_dir(conductor)
    week = week_of(now.date())
    iid = item_id(week)
    final = any(w == week and fin for w, _, fin in reports(conductor))
    state = item_state(iid)
    launched = any(h.get("week") == week and h.get("act") in ("launch", "file+launch") and h.get("ok")
                   for h in history(rdir))
    act, why = decide(week, final, state, launched)
    rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "week": week, "item": iid, "state": state,
           "act": act, "why": why, "apply": apply, "ok": True, "out": ""}
    if act != "none" and apply:
        prev = newest_final(conductor, before=week)
        out = []
        if act == "file+launch":
            rc, o = run([sys.executable, os.path.join(RIMFLOW, "cli.py"), "file", iid, "--for", "BENCH",
                         "--title", "Run the weekly Crystallize pass of %s: improve the role files and skills on the "
                                    "evidence since the last pass, carry the skill and tool proposals, write the report"
                                    % week,
                         "--effect", "cmd:python3 src/RimMandrake/Utils/crystallize_weekly.py report %s" % week,
                         "--seat", "BENCH", "--why", "rm-crystallize.timer: the week has no Crystallize report",
                         "--publish"])
            out.append(o[-600:])
            if rc:
                rec.update(ok=False, out="\n".join(out), rc=rc)
                record(rdir, rec)
                print(json.dumps(rec))
                return 1
        bdir = os.path.join(rdir, "briefs")
        os.makedirs(bdir, exist_ok=True)
        bpath = os.path.join(bdir, "%s-%d.md" % (iid, int(time.time())))
        with open(bpath, "w", encoding="utf-8") as f:
            f.write(brief(week, conductor, prev))
        rc, o = run([sys.executable, os.path.join(RIMFLOW, "detached_helper.py"), "launch", "--by-program",
                     "crystallize_weekly", "--seat", "BENCH", "--item", iid, "--brief-file", bpath, "--model", "opus",
                     "--budget-usd", "%g" % opus_cap(), "--continue-on-cap", str(CONTINUE_ON_CAP)])
        out.append(o[-600:])
        m = re.search(r"^DETACHED (\S+)", o, re.M)
        rec.update(ok=rc == 0, rc=rc, out="\n".join(out), brief=bpath, unit=m.group(1) if m else None)
    if apply:
        record(rdir, rec)
    print(json.dumps(rec))
    return 0 if rec["ok"] else 1


def timer_on():
    """-> (enabled and active, text), or (None, cause) when systemctl cannot be read."""
    try:
        en = subprocess.run(["systemctl", "--user", "is-enabled", TIMER], capture_output=True, text=True, timeout=60)
        ac = subprocess.run(["systemctl", "--user", "is-active", TIMER], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "systemctl: %s" % e
    e, a = en.stdout.strip(), ac.stdout.strip()
    if not e and not a:
        return None, "systemctl gave nothing: %s" % (en.stderr or ac.stderr).strip()
    return e in ("enabled", "enabled-runtime") and a == "active", "%s is %s/%s" % (TIMER, e or "?", a or "?")


def fresh(now=None, timer=timer_on):
    today = (now or DT.datetime.now()).date()
    conductor = storage()
    on, ttext = timer()
    if on is None:
        print("COULD NOT LOOK: " + ttext)
        return 2
    nf = newest_final(conductor)
    due = monday(week_of(today)) - DT.timedelta(days=7)
    ok_report = nf is not None and monday(nf[0]) >= due
    rtext = ("newest FINAL report %s (%s)" % (nf[0], nf[1]) if nf else "no FINAL report in %s" % conductor)
    print("%s: %s; %s; needs a FINAL report of %s or later" % ("HOLDS" if on and ok_report else "FAILS", ttext, rtext,
                                                                week_of(due)))
    return 0 if on and ok_report else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true")
    r = sub.add_parser("report")
    r.add_argument("week")
    sub.add_parser("fresh")
    a = ap.parse_args(argv)
    if a.cmd == "tick":
        return tick(a.apply)
    if a.cmd == "report":
        conductor = storage()
        hit = [x for x in reports(conductor) if x[0] == a.week and x[2]]
        print(("FINAL: %s" % hit[0][1]) if hit else "no FINAL report for %s in %s" % (a.week, conductor))
        return 0 if hit else 1
    return fresh()


if __name__ == "__main__":
    sys.exit(main())
