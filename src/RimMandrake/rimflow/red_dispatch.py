#!/usr/bin/env python3
"""red_dispatch.py: hands each nightly red's fix item to ONE capped detached fixer. No model, no tokens of its own.

Item RIMMANDRAKE_ROUTE_NIGHTLY_REDS_RAISED_INTO_A_RETIRED_POOL. Measured 2026-11-15: the build cop (ops_watch, every 10 min
on rm-ops-reds.timer) files one SELFTEST_FIX_* / NIGHTLY_COP_FIX_* item per red root cause and raises it, but its fix step
was "first in relentless pool_order", and Relentless was retired 2026-11-13; no builder started or closed one since.

    python3 src/RimMandrake/rimflow/red_dispatch.py tick [--apply]     one pass; launches only with --apply
    python3 src/RimMandrake/rimflow/red_dispatch.py status             the last reading, one line per red item
    python3 src/RimMandrake/rimflow/red_dispatch.py clear ITEM --why "..."   the Conductor lifts a stop (one more try)
    python3 src/RimMandrake/rimflow/red_dispatch.py started [--hours 24]
            acceptance test (B): every red item this step launched on has a `start` by a seat other than OWNER or
            CONDUCTOR within --hours of its alarm filing; exit 1 names the ones without

Runs on rm-red-dispatch.timer (every 10 min, from the dispatch clone). Settings: red_dispatch.json beside this file.
Input: the build cop's OPEN NIGHTLY_RED alarms (ops_watch alarms.json: item and tests), the ledger (state, blocked), the
detached-run records (live units) and the night's output (each test's last status and its detail lines for the brief).
Per red item, in due order, one decision:
  closed | blocked | claimed   the item is done/dropped, blocked, or someone holds it (state doing, no run of ours)
  live          a detached run is live on the item: nothing
  green         every test of the group passed on the last night: nothing (the build cop clears the alarm)
  attempted     this night's one attempt was made: nothing
  stopped       an attempt ended and the item is still open: nothing, ever, until `clear`; one Needs Conductor line in
                the Conductor log, once. There is no automatic reject-and-retry loop (the owner's condition, 2026-11-14).
  night_cap | slots_full | account_hold | disabled   caps: max_launches_per_night, max_live, the Dispatcher's account pick
  launch        write the brief, detached_helper.py launch it (sonnet when the red selftest proves the fix, opus when an
                opus_if rule matches; that model's cap). The fixer's first step is `rimflow start <item> --seat BENCH`
                (RUNNER, this step's filing seat, may not `start`: model.RUNNER_VERBS).
Reading: <RM_DISPATCHER_STATE>/red_dispatch/reading.json (RM_RED_DISPATCH_DIR overrides). Selftest: selftest_red_dispatch.py.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

ITEM = "RIMMANDRAKE_ROUTE_NIGHTLY_REDS_RAISED_INTO_A_RETIRED_POOL"
CFG_PATH = os.path.join(HERE, "red_dispatch.json")
PREFIXES = ("SELFTEST_FIX_", "NIGHTLY_COP_FIX_")
ALARM_PREFIX = "NIGHTLY_RED:testing.red_"
CLOSED = ("done", "dropped", "superseded")
PAC = dt.timezone(dt.timedelta(hours=-8), "PST")
NIGHT_START_H = 3


def load_cfg(path=CFG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sdir():
    d = os.environ.get("RM_RED_DISPATCH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "red_dispatch")
    os.makedirs(d, exist_ok=True)
    return d


def _read(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(p, obj):
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)


def pac(t):
    return dt.datetime.fromtimestamp(t, PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def night_of(t):
    """The night a moment belongs to: the Pacific date of the last 03:00 (the nightly sweep's start)."""
    return (dt.datetime.fromtimestamp(t, PAC) - dt.timedelta(hours=NIGHT_START_H)).date().isoformat()


def pick_model(cfg, tests, said):
    """-> (model, why). Sonnet unless an opus_if rule matches."""
    o = cfg.get("opus_if") or {}
    if len(tests) >= int(o.get("min_tests", 2)):
        return "opus", "%d tests share one first error line (a shared cause)" % len(tests)
    if o.get("said_regex") and re.search(o["said_regex"], said or ""):
        return "opus", "the error line matches %s" % o["said_regex"]
    hit = [t for t in tests if o.get("test_path_regex") and re.search(o["test_path_regex"], t)]
    if hit:
        return "opus", "%s lives in a mod's own tree" % hit[0]
    return "sonnet", "one test, its own selftest proves the fix"


# ---- what is true now -----------------------------------------------------------------------------------------------

def red_alarms(alarms):
    """ops_watch alarms.json -> [{item, key, tests, said, due, filed}] for the OPEN build-cop groups that name an item."""
    out = []
    for aid, a in sorted((alarms or {}).items()):
        if not aid.startswith(ALARM_PREFIX) or not isinstance(a, dict) or a.get("state") != "OPEN":
            continue
        item = a.get("item") or a.get("name")
        if not item or not item.startswith(PREFIXES):
            continue
        noted = [str(n) for n in a.get("noted") or []]
        tests = [n.split(" (due ")[0] for n in noted]
        dues = [m.group(1) for m in (re.search(r"\(due (\S+?)\)", n) for n in noted) if m]
        out.append({"item": item, "key": aid.split(":", 1)[1], "tests": tests, "said": a.get("title") or "",
                    "due": min(dues) if dues else None, "filed": a.get("filed")})
    return sorted(out, key=lambda r: (r["due"] or "9", r["item"]))


def ledger_items(ids):
    import model as LM
    w = LM.replay()
    out = {}
    for i in ids:
        it = w.items.get(i)
        out[i] = None if it is None else {"state": it.state, "blocked": bool(it.blocked), "owner": it.owner}
    return out


def detached_runs(ids):
    """-> {item: {"live": [units], "ended": [units]}} from the detached-run records (live_status, never a stale record)."""
    import detached_helper as DH
    out = {}
    for rec in DH.all_records():
        if rec.get("item") not in ids:
            continue
        st = DH.live_status(rec)
        r = out.setdefault(rec["item"], {"live": [], "ended": []})
        r["live" if st in ("launching", "running") else "ended"].append(rec["unit"])
    return out


def night_details():
    """-> {test path: (status, [detail lines])} from the night's full output, or None when it cannot be read."""
    import known_reds as KR
    try:
        return KR.details(KR.last_path().read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return None


def gather():
    import ops_watch as OW
    alarms = _read(os.path.join(str(OW.ops_dir()), "alarms.json"), None)
    reds = red_alarms(alarms) if isinstance(alarms, dict) else None
    ids = [r["item"] for r in reds or []]
    return {"reds": reds, "items": ledger_items(ids) if ids else {}, "runs": detached_runs(set(ids)) if ids else {},
            "night": night_details()}


def account_gate():
    import maturation_dispatch as MD
    return MD.account_gate()


# ---- the decision ---------------------------------------------------------------------------------------------------

def decide(cfg, st, facts, now, account=(True, "")):
    """-> (rows, launches). Pure over (cfg, st, facts); mutates st. One row per OPEN red item."""
    rows, launches = [], []
    night = night_of(now)
    items = st.setdefault("items", {})
    reds = facts.get("reds")
    if reds is None:
        return [{"item": "-", "decision": "blind", "why": "ops_watch alarms.json cannot be read; nothing launches"}], []
    runs = facts.get("runs") or {}
    live_total = sum(len(r.get("live") or []) for r in runs.values())
    tonight = sum(1 for s in items.values() for a in s.get("attempts") or [] if a.get("night") == night)
    details = facts.get("night")
    for red in reds:
        iid = red["item"]
        s = items.setdefault(iid, {})
        led = (facts.get("items") or {}).get(iid)
        run = runs.get(iid) or {}
        row = {"item": iid, "tests": red["tests"], "due": red["due"]}
        rows.append(row)

        def put(decision, why):
            row["decision"], row["why"] = decision, why

        if led is None:
            put("blind", "the ledger has no %s yet (its filing has not reached this clone)" % iid)
            continue
        if led["state"] in CLOSED:
            put("closed", "the item is %s" % led["state"])
            continue
        if led["blocked"]:
            put("blocked", "the item is blocked")
            continue
        if run.get("live"):
            put("live", "%s is live on it" % ", ".join(run["live"]))
            continue
        att = s.get("attempts") or []
        if att and not s.get("cleared_after_attempt"):
            last = att[-1]
            if last.get("night") == night and not last.get("failed") and last.get("unit") not in (run.get("ended") or []):
                put("attempted", "tonight's attempt %s is recorded and its unit is not seen ended yet" % last.get("unit"))
                continue
            why = ("the automatic launch on %s failed: %s" % (last.get("night"), last.get("failed")) if last.get("failed")
                   else "attempt %s (%s, %s) ended and the item is still %s" % (last.get("unit"), last.get("model"),
                                                                                last.get("night"), led["state"]))
            put("stopped", why)
            if not s.get("told"):
                row["need"] = ("%s: %s; red_dispatch launches no second automatic try (tests: %s). Read the run's note "
                               "on the item, then fix by hand, park it (known_reds.py add), or `red_dispatch.py clear %s "
                               "--why ...` for one more try" % (iid, why, ", ".join(red["tests"][:3]), iid))
            continue
        if led["state"] == "doing" and not att:
            put("claimed", "the item is doing under %s and no run of ours is on it" % led["owner"])
            continue
        if details is not None and red["tests"] and all((details.get(t) or ("?",))[0] == "PASS" for t in red["tests"]):
            put("green", "every test of the group passed on the last night; the build cop clears it")
            continue
        if not cfg.get("enabled"):
            put("disabled", "red_dispatch.json has enabled: false")
            continue
        if tonight >= int(cfg.get("max_launches_per_night", 6)):
            put("night_cap", "%d launches tonight, the most is %s" % (tonight, cfg.get("max_launches_per_night")))
            continue
        if not account[0]:
            put("account_hold", account[1])
            continue
        if live_total >= int(cfg.get("max_live", 2)):
            put("slots_full", "%d live red-fix runs, the most is %s" % (live_total, cfg.get("max_live", 2)))
            continue
        model, mwhy = pick_model(cfg, red["tests"], red["said"])
        cap = cfg.get("%s_cap_usd" % model)
        if not (isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0):
            put("no_cap", "red_dispatch.json has no positive %s_cap_usd; nothing launches without a cap" % model)
            continue
        live_total += 1
        tonight += 1
        row.update(model=model, cap=cap, model_why=mwhy, said=red["said"])
        put("launch", "%s at USD %g: %s" % (model, cap, mwhy))
        launches.append(iid)
    return rows, launches


# ---- the acts -------------------------------------------------------------------------------------------------------

def brief_text(row, details, cfg):
    tests = row["tests"]
    lines = []
    for t in tests:
        stt, det = (details or {}).get(t, ("UNMEASURED", []))
        lines.append("  %s  %s" % (stt, t))
        lines += ["      " + d for d in det[: int(cfg.get("detail_lines", 60))]]
    return """Fix ledger item {item}: a nightly red the build cop filed (offline only: no bridge, no game, no ModsConfig).

Alarm: {said}
Red tests and the night's detail lines (Transient/selftests_nightly.last in /home/mandrake/rm/bench):
{detail}

Steps:
0. Start the item and publish the shard, before anything else:
   python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "detached red fix (red_dispatch.py)"
   ./publish -m "ledger: {item} start" infrastructure/state/ledger/events/BENCH.jsonl
1. Run the red test(s) here first: python3 src/RimMandrake/Utils/run_selftests.py --only {only}
   (foreground, with a timeout). If it is GREEN at origin/main, the red is gone: say so with the output in a note and close
   the item (step 4) on HEAD's sha.
2. Find the root cause (a rollback first when one commit broke it: git log on the test and the code it exercises).
3. Fix the CODE the test checks. Never weaken an assertion, delete a check, or edit a north-star bar. When the test itself
   is wrong (it asserts a retired thing), fix the test and say why in the commit. Rerun step 1's command to GREEN.
4. Land with ./publish -m "{item}: <what>" <explicit paths>, then
   python3 src/RimMandrake/rimflow/cli.py close {item} --sha <published sha> --seat BENCH --why "detached red fix: <test> GREEN at <sha>"
   (a refused close: put the refusal in the note, do not fight the gate).
5. Cannot fix it within the cap: write what you found and the one next action in the note; do not park the red yourself.
   This is the only automatic attempt: nothing retries it, the Conductor reads your note.
""".format(item=row["item"], said=row.get("said") or "-", detail="\n".join(lines) or "  (no detail read)",
           only=" ".join(os.path.basename(t) for t in tests))


def launch(item, model, cap, brief, seat):
    d = os.path.join(sdir(), "briefs")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s-%d.md" % (item, int(time.time())))
    with open(path, "w", encoding="utf-8") as f:
        f.write(brief)
    argv = [sys.executable, os.path.join(HERE, "detached_helper.py"), "launch", "--seat", seat, "--item", item,
            "--brief-file", path, "--model", model, "--budget-usd", "%g" % cap]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"^DETACHED (\S+)", r.stdout or "", re.M)
    return r.returncode, out, (m.group(1) if m and not r.returncode else None)


def conductor_need(text, now, path=None):
    """One Needs Conductor line in the Conductor log (the guards detached_helper.conductor_line uses)."""
    import detached_helper as DH
    import doorbell
    import conductor_log_guard
    path = path or DH.conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(DH.REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — NEEDS CONDUCTOR (red_dispatch): %s\n" % (DH.iso(now), text))
    return path


def execute(cfg, st, rows, launches, now, details, fx=None):
    fx = fx or {}
    do_launch = fx.get("launch", launch)
    do_need = fx.get("need", conductor_need)
    night = night_of(now)
    for row in rows:
        s = (st.get("items") or {}).get(row["item"])
        if row.get("need") and s is not None:
            try:
                do_need(row["need"], now)
                s["told"] = now
            except Exception as e:  # noqa: BLE001 -- the line stays owed and is said on the row
                row["need_failed"] = "%s: %s" % (type(e).__name__, e)
        if row["item"] not in launches:
            continue
        rc, text, unit = do_launch(row["item"], row["model"], row["cap"], brief_text(row, details, cfg),
                                   cfg.get("seat", "BENCH"))
        ok_launch = rc == 0 and bool(unit)
        s.pop("cleared_after_attempt", None)
        s.pop("told", None)
        s.setdefault("attempts", []).append({"night": night, "at": now, "unit": unit, "model": row["model"],
                                             "cap": row["cap"],
                                             "failed": None if ok_launch else (text or "rc %s" % rc)[:400]})
        if ok_launch:
            row.update(decision="launched", unit=unit)
        else:
            row.update(decision="launch_failed", why=(text or "rc %s" % rc)[:400])


def reading(rows, now, night):
    return {"schema": 1, "at": now, "at_pac": pac(now), "night": night,
            "launched": [{"item": r["item"], "unit": r.get("unit"), "model": r.get("model")} for r in rows
                         if r.get("decision") == "launched"],
            "needs_conductor": [r["need"] for r in rows if r.get("need")],
            "items": {r["item"]: {k: r.get(k) for k in ("decision", "why", "tests", "due", "model", "unit")}
                      for r in rows}}


def tick(cfg, apply, fx=None, now=None):
    fx = fx or {}
    now = now or time.time()
    d = sdir()
    st = _read(os.path.join(d, "state.json"), {})
    facts = fx["facts"]() if "facts" in fx else gather()
    account = fx["account"]() if "account" in fx else account_gate()
    rows, launches = decide(cfg, st, facts, now, account)
    if not apply:
        for r in rows:
            if r["item"] in launches:
                r["decision"] = "would_launch"
            r.pop("need", None)
        launches = []
    else:
        execute(cfg, st, rows, launches, now, facts.get("night"), fx)
    rd = reading(rows, now, night_of(now))
    if apply:
        _write(os.path.join(d, "state.json"), st)
        _write(os.path.join(d, "reading.json"), rd)
        with open(os.path.join(d, "ticks.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "decisions": {r["item"]: r.get("decision") for r in rows},
                                "launched": rd["launched"]}) + "\n")
    return rd


# ---- acceptance test (B) --------------------------------------------------------------------------------------------

def started_check(hours=24, now=None, events=None, st=None):
    """-> (rc, lines). Every item this step launched on has a `start` event by a seat other than OWNER or CONDUCTOR, at
    most `hours` after its alarm was filed (the ledger's file/spawn ts). rc 0 when all do, 1 naming the rest, 2 blind."""
    import model as LM
    now = now or time.time()
    st = st if st is not None else _read(os.path.join(sdir(), "state.json"), {})
    ours = [i for i, s in (st.get("items") or {}).items() if s.get("attempts")]
    if not ours:
        return 2, ["UNMEASURED: red_dispatch has launched on no item yet (state %s)" % os.path.join(sdir(), "state.json")]
    evs = events if events is not None else LM.read()
    filed, starts = {}, {}
    for e in evs:
        i = e.get("id")
        if i not in ours:
            continue
        t = LM.epoch(e.get("ts")) if e.get("ts") else None
        if e.get("event") in ("file", "spawn") and i not in filed:
            filed[i] = t
        elif e.get("event") == "start" and str(e.get("seat")).upper() not in ("OWNER", "CONDUCTOR"):
            starts.setdefault(i, []).append((t, e.get("seat")))
    bad, lines = [], []
    for i in sorted(ours):
        f0 = filed.get(i)
        ok = [s for s in starts.get(i, []) if f0 is not None and s[0] is not None and s[0] - f0 <= hours * 3600]
        lines.append("%s  %s  %s" % ("PASS" if ok else "FAIL", i, ("start by %s %.1f h after filing" % (
            ok[0][1], (ok[0][0] - f0) / 3600.0)) if ok else "no start by a builder seat within %g h" % hours))
        if not ok:
            bad.append(i)
    lines.append("%d of %d launched red items started within %g h" % (len(ours) - len(bad), len(ours), hours))
    return (1 if bad else 0), lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true", help="launch and write state; without it, a dry pass")
    sub.add_parser("status")
    c = sub.add_parser("clear")
    c.add_argument("item")
    c.add_argument("--why", required=True)
    s = sub.add_parser("started")
    s.add_argument("--hours", type=float, default=24)
    o = ap.parse_args(argv)
    cfg = load_cfg()
    if o.cmd == "tick":
        rd = tick(cfg, o.apply)
        for iid, r in rd["items"].items():
            print("%-48s %-13s %s" % (iid, r["decision"], r["why"]))
        print("night %s; launched %d; needs conductor %d" % (rd["night"], len(rd["launched"]), len(rd["needs_conductor"])))
        return 0
    if o.cmd == "status":
        rd = _read(os.path.join(sdir(), "reading.json"), None)
        if not rd:
            print("no reading yet")
            return 1
        print("reading at %s (night %s)" % (rd["at_pac"], rd["night"]))
        for iid, r in rd["items"].items():
            print("%-48s %-13s %s" % (iid, r["decision"], r["why"]))
        return 0
    if o.cmd == "clear":
        p = os.path.join(sdir(), "state.json")
        st = _read(p, {})
        s = st.setdefault("items", {}).setdefault(o.item, {})
        s["cleared_after_attempt"] = True
        s.pop("told", None)
        s.setdefault("cleared", []).append({"at": time.time(), "why": o.why})
        _write(p, st)
        print("CLEARED %s: the next tick may launch one more attempt" % o.item)
        return 0
    if o.cmd == "started":
        rc, lines = started_check(o.hours)
        print("\n".join(lines))
        return rc
    return 2


if __name__ == "__main__":
    sys.exit(main())
