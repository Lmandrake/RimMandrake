#!/usr/bin/env python3
"""deadman_check: the one sweep of everything that must stay alive (LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING).

A separate no-AI program on its own systemd timer (rm-deadman.timer, every 15 min, from the Dispatcher's clone). Each
pass rechecks (1) every `live` line on the ledger, (2) rimflow/live_baseline.txt, the running system's own promises,
(3) each arm's LAST-RUN STAMP (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT: an arm cannot report its own death).

On failure it reopens the SAME item (`rimflow live --result broken`), filing LIVE_RESTORE_<NAME> first if the promise
has no item. On recovery it puts the item back. The ledger is the only state, so one promise has one id and
`live_repeats` counts its outages; at 2 the report says it needs a fold. The pass writes ops_watch/live_sweep.json,
whose `line` reads "61 promises, 58 kept, 3 broken". A pass that cannot see systemd says so and touches nothing.
With --file-alarms a dead arm (Dispatcher, ops_watch) or a broken timer promise (`unit=`) also rings the owner's phone
through pulse/phone_push.py, a fixed template with no AI in the path, once per outage (the key closes on recovery),
whatever the ledger write did (DEADMAN_WIRE_PHONE_WITHOUT_AI). RM_DEADMAN_PUSH=0 turns the phone off.

    ops_watch   $RM_OPS_WATCH_DIR/status.json  key "t" (epoch of the last pass; timer every 15 min)  limit 50 min
    dispatcher  $RM_DISPATCHER_STATE/state.json key "last_ok_tick" (ISO; timer every 2 min)            limit 15 min
                the state of the mode the rm-dispatcher.service timer RUNS (`--apply` in its ExecStart: live, else
                dry/; $RM_DISPATCHER_MODE live|dry overrides), never the fresher of the two: a dry run must not mask a
                dead live Dispatcher. Mode unknown -> no stamp (a fault). last_ok_tick is stamped only by a tick that
                completed and was not blind; last_tick (any attempt) is read only from a state file that has no
                last_ok_tick key at all (a dispatcher clone older than review round Q).
    A stamp that is not a finite number (NaN, inf, bool) is no stamp.
    An arm's clock starts no earlier than its own timer did, and a timer paused with its restart armed excuses its arm:
    after a mass stop this pass restarts beside the arm and would otherwise read the outage as a death (17EC, 129E).

    python3 src/RimMandrake/Utils/deadman_check.py run [--file-alarms]
    python3 src/RimMandrake/Utils/deadman_check.py install [--apply]    systemd user timer (plan unless --apply)
    python3 src/RimMandrake/Utils/deadman_check.py baseline [--write]   generate the baseline from what runs today
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))

LIMITS = {"ops_watch": 50 * 60, "dispatcher": 15 * 60}
BASELINE = HERE.parent / "rimflow" / "live_baseline.txt"
SETTLED = ("done", "built", "validated")
RETIRED = ("dropped", "superseded")
MAX_PER_PASS = 10
FOLD_AT = 2                 # a second outage means the first fix did not fold
ARM_UNITS = {"ops_watch": "rm-ops-watch.timer", "dispatcher": "rm-dispatcher.timer"}
TRIAL_ONLY = ("rm-replay-watch.timer", "rm-arena-anchor.timer")     # they end with the arena trial


def ops_dir():
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def dispatcher_dir():
    import doorbell
    return Path(doorbell.state_dir())


def sweep_file():
    return ops_dir() / "live_sweep.json"


def _json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _iso_epoch(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def dispatcher_mode(runner=subprocess.run):
    """'live' | 'dry' | None: the mode the rm-dispatcher.service timer runs, read from its ExecStart."""
    env = os.environ.get("RM_DISPATCHER_MODE")
    if env in ("live", "dry"):
        return env
    try:
        r = runner(["systemctl", "--user", "show", "-p", "ExecStart", "--value", "rm-dispatcher.service"],
                   capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return None
    m = re.search(r"argv\[\]=([^;]*)", r.stdout or "") if not r.returncode else None
    if not m or "dispatcher.py" not in m.group(1):
        return None
    return "live" if "--apply" in m.group(1).split() else "dry"


def dispatcher_stamp(d):
    """Pure. A parsed state.json -> epoch | None."""
    if not isinstance(d, dict):
        return None
    key = "last_ok_tick" if "last_ok_tick" in d else "last_tick"
    e = _iso_epoch(d.get(key)) if isinstance(d.get(key), str) else None
    return e if e is not None and finite(e) else None


def stamps(mode=None):
    """-> {arm: epoch | None}. None = missing or unreadable (reported as such, never as fresh)."""
    out = {}
    st = _json(ops_dir() / "status.json")
    t = st.get("t") if isinstance(st, dict) else None
    out["ops_watch"] = float(t) if finite(t) else None
    mode = mode or dispatcher_mode()
    if mode is None:
        out["dispatcher"] = None
    else:
        p = dispatcher_dir() / "state.json" if mode == "live" else dispatcher_dir() / "dry" / "state.json"
        out["dispatcher"] = dispatcher_stamp(_json(p))
    return out


def judge(st, now, limits=None):
    """-> {arm: None (alive) | reason string}. Pure (tested). A stamp in the future by over 5 min is also a fault."""
    limits = limits or LIMITS
    res = {}
    for arm, lim in limits.items():
        t = st.get(arm)
        if not finite(t):
            res[arm] = "%s has no readable last-run stamp" % arm
        elif now - t > lim:
            res[arm] = "%s last ran %d min ago (limit %d min)" % (arm, (now - t) // 60, lim // 60)
        elif t - now > 300:
            res[arm] = "%s stamp is %d min in the future (clock or file wrong)" % (arm, (t - now) // 60)
        else:
            res[arm] = None
    return res


def arm_clocks(st, now, runner=subprocess.run):
    """-> st with each readable stamp advanced to the moment its timer last started. A missing stamp stays missing."""
    import live_line
    out = dict(st)
    for arm, unit in ARM_UNITS.items():
        try:
            began = float(live_line._systemctl_show(unit, "ActiveEnterTimestamp", runner))
        except ValueError:
            continue
        if finite(out.get(arm)) and finite(began) and out[arm] < began <= now:
            out[arm] = began
    return out


def arm_faults(st, now, runner=subprocess.run):
    """-> {arm: None | reason}, leaving out a fault whose timer is paused with its restart armed (the same rule as a
    promise: see excused). A left-out arm files nothing and, if already broken, stays broken until it really runs."""
    res = judge(arm_clocks(st, now, runner), now)
    return {a: why for a, why in res.items()
            if not (why and excused("unit=%s max_age=1h" % ARM_UNITS[a], runner))}


def item_id(line):
    """The fixed id of a promise that has no item of its own: same unit, same item, for good."""
    import live_line
    p = live_line.parse(line)
    name = {"unit": lambda: p["unit"].rsplit(".", 1)[0], "hook": lambda: p["hook"].rsplit(".", 1)[0],
            "role": lambda: p["role"]}[p["kind"]]()
    return "LIVE_RESTORE_" + re.sub(r"\W+", "_", name).upper()


def load_baseline(path=None):
    """The running system's promises, one live line each ('#' comments). A line that does not parse raises: the
    sweep must not silently watch less than the file says."""
    import live_line
    lines = []
    for raw in Path(path or BASELINE).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            live_line.parse(line)
            lines.append(line)
    return lines


EXCUSED = "(excused)"   # paused on purpose: not broken, and no proof it recovered either


def promises(items, baseline):
    """-> [{"item", "line"}]: the baseline's, then every promise on the ledger. Pure. `once:` is the visible escape and
    is ignored; an item being worked holds its own promise until it closes again; a retired item holds none."""
    out = []
    for line in baseline:
        iid = item_id(line)
        it = items.get(iid)
        if not (it is not None and it.state in RETIRED):
            out.append({"item": iid, "line": line})
    seen = {r["item"] for r in out}        # a fixed id answers for its baseline line, whatever it closed with
    for iid, it in sorted(items.items()):
        line = getattr(it, "live", None)
        if not line or line.startswith("once:") or it.state in RETIRED or iid in seen:
            continue
        if it.state in SETTLED or it.live_broken:
            out.append({"item": iid, "line": line})
    return out


def excused(line, runner=subprocess.run):
    """A timer paused with its own restart armed (timers_guard), or a role the schedule has switched off."""
    import live_line
    p = live_line.parse(line)
    if p["kind"] == "unit":
        import timers_guard
        return any(p["unit"] in (units or []) and live_line._systemctl("is-active", resume, runner) == "active"
                   for resume, units in timers_guard.load_pauses().items())   # an old record excuses nothing
    if p["kind"] == "role":
        sched = json.loads((HERE.parent / "rimflow" / "dispatcher_schedule.json").read_text(encoding="utf-8"))
        return not any(r.get("name") == p["role"] and r.get("enabled") for r in sched.get("roles", []))
    return False


def real_check(line):
    import live_line
    return EXCUSED if excused(line) else live_line.check(line)


def read_items():
    import ops_watch  # noqa: F401   puts pulse/ on the path
    import pulse_core as pc
    own = HERE.parents[2]                  # this pass's own shard, or it would not see what it filed until others pull
    return pc._model().replay(pc.read_ledger([*pc.CLONES, *([own] if own not in pc.CLONES else [])])).items


def known_ids():
    """Every item id ever filed, closed ones too (timers_guard mints an alarm name against these)."""
    return set(read_items())


def sweep(now, filer, items, baseline, arms, checker=real_check, sees=True, pusher=None):
    """One pass: recheck every promise, reopen what died, put back what recovered. The ledger is the state, so a pass
    that could not file simply tries again. filer(todo, conf) -> {item: None|error}; None files nothing. pusher (see
    phone): a dead arm or a broken timer also rings the owner's phone, whatever the filer did. -> the report."""
    if not sees:
        report = {"t": now, "line": "promises unread: this pass could not see systemd", "blind": True, "broken": [],
                  "unpublished": (_json(sweep_file()) or {}).get("unpublished")}
        OW_atomic(sweep_file(), report)
        return report
    rows = [dict(p, why=checker(p["line"])) for p in promises(items, baseline)]
    excused_n = sum(r["why"] == EXCUSED for r in rows)
    rows = [r for r in rows if r["why"] != EXCUSED]
    rows += [{"item": "LIVE_RESTORE_" + arm.upper(), "line": None, "why": why} for arm, why in sorted(arms.items())]
    todo = []
    for r in rows:
        it = items.get(r["item"])
        if r["why"] and it is None:
            todo.append({"item": r["item"], "result": "broken", "detail": r["why"], "spawn": True,
                         "title": ("Live promise broken: %s" % r["why"])[:160]})
        elif r["why"] and not it.live_broken:
            todo.append({"item": r["item"], "result": "broken", "detail": r["why"]})
        elif not r["why"] and it is not None and it.live_broken:
            todo.append({"item": r["item"], "result": "kept", "detail": "sweep: running again"})
    held = todo[MAX_PER_PASS:]        # a mass outage files over several passes, never a wall of commits in one
    todo = todo[:MAX_PER_PASS]
    errors = {}
    prior = _json(sweep_file()) or {}
    if todo or prior.get("unpublished"):     # a reading that stayed local is pushed by the next pass, not forgotten
        if filer:
            import ops_watch as OW
            try:
                errors = filer(todo, OW.alarm_conf(OW.load_rules()))
            except Exception as e:  # noqa: BLE001
                errors = {t["item"]: "filer raised %s: %s" % (type(e).__name__, str(e)[:200]) for t in todo}
                errors["_publish"] = "filer raised after an unknown number of readings"
        else:
            errors = {t["item"]: "filing off (run without --file-alarms)" for t in todo}
    broken = [r for r in rows if r["why"]]
    repeats = {r["item"]: getattr(items.get(r["item"]), "live_repeats", 0) for r in rows}
    just = {t["item"] for t in todo if t["result"] == "broken" and not errors.get(t["item"])}
    fold = sorted(i for i, n in repeats.items() if n + (i in just) >= FOLD_AT)
    report = {"t": now, "promises": len(rows) + excused_n, "kept": len(rows) - len(broken), "excused": excused_n,
              "broken": [{"item": r["item"], "why": r["why"]} for r in broken], "fold": fold,
              "held": len(held), "errors": {k: v for k, v in errors.items() if v and not k.startswith("_")},
              "unpublished": unpushed(errors, prior), "raise_failed": errors.get("_raise") or {},
              "line": "%d promises, %d kept, %d broken%s%s" % (
                  len(rows) + excused_n, len(rows) - len(broken), len(broken),
                  ", %d paused" % excused_n if excused_n else "", ", %d need a fold" % len(fold) if fold else "")}
    if pusher:
        report["phone"] = phone(rows, pusher)
    OW_atomic(sweep_file(), report)
    return report


def phone_worthy(row):
    """A dead arm (Dispatcher, ops_watch) or a broken timer promise (`unit=`): what must reach the owner's phone with
    no AI in the path (DEADMAN_WIRE_PHONE_WITHOUT_AI). Pure."""
    return row["line"] is None or "unit=" in (row["line"] or "")


def phone_row(row):
    """-> the phone_push row for a sweep ROW. Pure: a fixed template, no agent writes it."""
    return {"key": "deadman:" + row["item"], "kind": "red", "label": "dead-man %s" % row["item"],
            "detail": "deadman_check (no AI): %s. The ledger holds %s; restore it, then the sweep puts it back."
                      % (row["why"], row["item"])}


def phone(rows, pusher):
    """Push every phone-worthy broken row, close the key of every one that is kept again. pusher: an object with
    send(row) -> bool and close(key) (pulse/phone_push; a selftest double). The push dedups by key, so a broken row
    pushes once per outage and a failed send retries next pass. -> [what happened], for the report."""
    out = []
    for r in rows:
        if not phone_worthy(r):
            continue
        pr = phone_row(r) if r["why"] else None
        try:
            if pr:
                if pusher.send(pr):
                    out.append("pushed %s" % pr["key"])
            else:
                pusher.close("deadman:" + r["item"])
        except Exception as e:  # noqa: BLE001  the phone failing must not stop the sweep or its report
            out.append("push failed %s: %s: %s" % (r["item"], type(e).__name__, str(e)[:160]))
    return out


def real_pusher():
    """pulse/phone_push (Todoist due-now task), unless RM_DEADMAN_PUSH=0."""
    if os.environ.get("RM_DEADMAN_PUSH", "1") == "0":
        return None
    sys.path.insert(0, str(HERE / "pulse"))
    import phone_push
    return phone_push


def unpushed(errors, prior):
    """Pure. -> why the last reading is still local | None. No publish this pass leaves the old answer standing."""
    got = errors.get("_publish")
    if got is None:
        return prior.get("unpublished")
    if got == "nothing to publish":     # nothing was tried, so nothing is settled
        return prior.get("unpublished")
    return None if got == "pushed" or got.endswith("; pushed") else got


def OW_atomic(path, obj):
    import ops_watch as OW
    OW.atomic_json(path, obj)


def live_filer(todo, conf):
    """Spawn-if-new then record the reading, as RUNNER from the dispatch clone under QHOME/ingest.lock, published: the
    same road as ops_watch.real_filer. -> {item: None | error}."""
    import fcntl
    import importlib.util
    import ops_watch as OW
    path = Path(conf["clone"]) / "src/RimMandrake/Utils/testq/ingest.py"
    spec = importlib.util.spec_from_file_location("deadman_ingest", str(path))
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    res = {}
    with open(OW.qhome() / "ingest.lock", "w") as lk:
        t0 = time.time()
        while True:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() - t0 > conf["lock_wait_s"]:
                    return {t["item"]: "ingest.lock busy for %d s" % conf["lock_wait_s"] for t in todo}
                time.sleep(2)
        n = 0
        nobody = OW.alarm_receiver_problem(conf)     # T2: no item is filed for a receiver nobody wakes
        for t in todo:
            rc, out = 0, ""
            if t.get("spawn") and nobody:
                rc, out = 1, "no receiver: " + nobody
            elif t.get("spawn"):
                rc, out = ing.rimflow("spawn", "--from", conf["parent"], "--for", conf["for"], "--needs", conf["needs"],
                                      "--name", t["item"], "--title", t["title"],
                                      "--why", "live sweep (deterministic, no AI): " + t["item"])
            if rc == 0:
                rc, out = ing.rimflow("live", t["item"], "--result", t["result"], "--detail", t["detail"])
            if rc == 0 and t["result"] == "broken":    # a broken promise is first in relentless pool_order
                rrc, rout = ing.rimflow("raise", t["item"], "--reason", OW.RAISE_REASON)
                if rrc != 0:
                    res.setdefault("_raise", {})[t["item"]] = rout[-300:]
            res[t["item"]] = None if rc == 0 else out[-300:]
            n += rc == 0
        res["_publish"] = ing.publish(n, message="ledger: live sweep %s" % ", ".join(
            "%s %s" % (t["item"], t["result"]) for t in todo if res.get(t["item"]) is None)) \
            if n or not todo else "nothing to publish"
    return res


def duration_s(timers):
    """The period in systemd's `OnUnitInactiveUSec=1h 30min ;` text, seconds | None. Pure."""
    m = re.search(r"OnUnit(?:In)?[aA]ctiveUSec=([^;]+);", timers or "")
    unit = {"s": 1, "min": 60, "h": 3600, "d": 86400}
    return sum(int(n) * unit[u] for n, u in re.findall(r"(\d+)(min|h|s|d)\b", m.group(1))) if m else None


def generate_baseline(runner=subprocess.run):
    """The first lines, from what runs today: each enabled timer (allowed three of its own intervals, at least 2 h),
    each wired hook, each enabled Dispatcher role. Regenerate only to add; a removed line is a retired promise."""
    import live_line
    lines = []
    r = runner(["systemctl", "--user", "list-unit-files", "rm-*.timer", "timer-guard.timer", "--state=enabled",
                "--no-legend"], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    for row in sorted(r.stdout.splitlines()):
        unit = row.split()[0]
        if unit in TRIAL_ONLY:
            continue
        last = live_line._systemctl_show(unit, "LastTriggerUSec", runner)
        nxt = live_line._systemctl_show(unit, "NextElapseUSecRealtime", runner)
        gap = int(nxt) - int(last) if last.isdigit() and nxt.isdigit() else \
            duration_s(live_line._systemctl_show(unit, "TimersMonotonic", runner)) or 8 * 86400    # unknown: never tighter than a weekly timer allows
        lines.append("unit=%s max_age=%dh" % (unit, max(2, math.ceil(3 * gap / 3600))))
    root = HERE.parent.parent.parent
    wired = json.dumps(json.loads((root / ".claude/settings.json").read_text(encoding="utf-8")).get("hooks") or {})
    lines += ["hook=%s" % h for h in sorted(set(re.findall(r"([\w.-]+\.(?:py|sh))", wired)))]
    sched = json.loads((HERE.parent / "rimflow" / "dispatcher_schedule.json").read_text(encoding="utf-8"))
    lines += ["role=%s max_age=%s" % (r["name"], "6d" if r["name"] == "Innovator" else "3d")   # it runs twice a week
              for r in sched["roles"] if r.get("enabled")]
    return lines


UNIT = """# rm-deadman: the no-AI sweep of every live promise, with the outside dead-man for the Dispatcher and ops_watch (LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING).
[Unit]
Description=Recheck every live promise, and the Dispatcher and ops_watch stamps

[Service]
Type=oneshot
WorkingDirectory={deploy}
ExecStart=/usr/bin/python3 {deploy}/src/RimMandrake/Utils/deadman_check.py run --file-alarms
TimeoutStartSec=300s
Nice=10
"""
TIMER = """[Unit]
Description=Live promise sweep every 15 min

[Timer]
OnCalendar=*:03/15
Persistent=true

[Install]
WantedBy=timers.target
"""


def install(apply, deploy):
    d = Path.home() / ".config/systemd/user"
    files = {d / "rm-deadman.service": UNIT.format(deploy=deploy), d / "rm-deadman.timer": TIMER}
    for p, body in files.items():
        old = p.read_text() if p.exists() else None
        print(("unchanged " if old == body else "write ") + str(p))
        if apply and old != body:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
    if apply:
        for cmd in (["daemon-reload"], ["enable", "--now", "rm-deadman.timer"]):
            r = subprocess.run(["systemctl", "--user"] + cmd, capture_output=True, text=True, timeout=60)
            print("systemctl --user %s: exit %d %s" % (" ".join(cmd), r.returncode, r.stderr.strip()))
            if r.returncode:
                return 1
    else:
        print("plan only: pass --apply to write and enable")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--file-alarms", action="store_true")
    i = sub.add_parser("install")
    i.add_argument("--apply", action="store_true")
    i.add_argument("--deploy", default="/home/mandrake/rm/dispatch")
    b = sub.add_parser("baseline")
    b.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "install":
        return install(a.apply, a.deploy)
    if a.cmd == "baseline":
        lines = generate_baseline()
        fresh = {item_id(x) for x in lines}
        lines += [x for x in load_baseline() if item_id(x) not in fresh]   # only a hand removes a promise
        if a.write:
            BASELINE.write_text("# The running system's live promises (LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING): "
                                "deadman_check.py sweeps them.\n# A failed line files or reopens LIVE_RESTORE_<NAME>. "
                                "Delete a line to retire its promise.\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print("%d lines%s" % (len(lines), " written to %s" % BASELINE if a.write else ""))
        return 0
    import live_line
    report = sweep(time.time(), live_filer if a.file_alarms else None, read_items(), load_baseline(),
                   arm_faults(stamps(), time.time()), sees=live_line.can_see(),
                   pusher=real_pusher() if a.file_alarms else None)
    print("sweep: %s" % report["line"])
    for b_ in report["broken"]:
        print("  %s: %s" % (b_["item"], b_["why"]))
    return 1 if report.get("blind") or report.get("errors") else 0


if __name__ == "__main__":
    sys.exit(main())
