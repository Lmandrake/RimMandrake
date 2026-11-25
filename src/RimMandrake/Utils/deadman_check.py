#!/usr/bin/env python3
"""deadman_check: the one sweep of everything that must stay alive (LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING).

A separate no-AI program on its own systemd timer (rm-deadman.timer, every 15 min, from the Dispatcher's clone). Each
pass rechecks (1) every `live` line on the ledger, (2) rimflow/live_baseline.txt, the running system's own promises,
(3) each arm's LAST-RUN STAMP (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT: an arm cannot report its own death),
(4) that the retired Relentless/Artisan/Whittle loops stay off (retired_loops_check.py; arm `retired_loops`, item
LIVE_RESTORE_RETIRED_LOOPS; Archmagi only), (5) that every unit text of ours has its one home and is what systemd has
installed (ops_clocks.units_problems; arm `units`, item LIVE_RESTORE_UNITS; reading ops_watch/units.json).

On failure it reopens the SAME item (`rimflow live --result broken`), filing LIVE_RESTORE_<NAME> first if the promise
has no item. One outage files one ticket (hosts_of; page design/specs/2026-11-19-one-fault-one-ticket/boundary.md): one
subject under many fixes files its host, and one cause across subjects files LIVE_RESTORE_CAUSE_<hash>; the members file
nothing. On recovery it puts the item back. The ledger is the only state, so one promise has one id and
`live_repeats` counts its outages; at 2 the report says it needs a fold. The pass writes ops_watch/live_sweep.json,
whose `line` reads "61 promises, 58 kept, 3 broken". A pass that cannot see systemd says so and touches nothing.
With --file-alarms a dead arm (Dispatcher, ops_watch) or a broken timer promise (`unit=`) also rings the owner's phone
through ops_core/phone_push.py, a fixed template with no AI in the path, once per outage (the key closes on recovery),
whatever the ledger write did (DEADMAN_WIRE_PHONE_WITHOUT_AI). RM_DEADMAN_PUSH=0 turns the phone off. Its only route,
a Todoist task, is retired (owner, 2026-11-19) and off unless RM_TODOIST_ALARM_POSTS=1: the report says "phone off".

    ops_watch   $RM_OPS_WATCH_DIR/status.json  key "t" (epoch of the last pass; a metronome beat, ~1 min)  limit 50 min
    dispatcher  $RM_DISPATCHER_STATE/state.json key "last_ok_tick" (ISO; a dispatch beat, ~2 min)          limit 15 min
                the state of the mode its clock RUNS (`--apply` in the owning metronome phase's argv, or before
                cutover in rm-dispatcher.service's ExecStart: live, else
                dry/; $RM_DISPATCHER_MODE live|dry overrides), never the fresher of the two: a dry run must not mask a
                dead live Dispatcher. Mode unknown -> no stamp (a fault). last_ok_tick is stamped only by a tick that
                completed and was not blind; last_tick (any attempt) is read only from a state file that has no
                last_ok_tick key at all (a dispatcher clone older than review round Q).
    A stamp that is not a finite number (NaN, inf, bool) is no stamp.
    An arm's clock starts no earlier than its own timer did, and a timer paused with its restart armed excuses its arm:
    after a mass stop this pass restarts beside the arm and would otherwise read the outage as a death (17EC, 129E).

    python3 src/RimMandrake/Utils/deadman_check.py run [--file-alarms]
    its units: src/RimMandrake/Utils/systemd/rm-deadman.{service,timer}; install: ops_clocks.py install rm-deadman --apply --enable
    python3 src/RimMandrake/Utils/deadman_check.py baseline [--write]   generate the baseline from what runs today
"""
import argparse
import hashlib
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
RETIRED_FILE = HERE.parent / "rimflow" / "live_retired.txt"   # units, hooks, roles retired on purpose (OPS_TIMER_REPAIR_EC51)
SETTLED = ("done", "built", "validated")
RETIRED = ("dropped", "superseded")
MAX_PER_PASS = 10
FOLD_AT = 2                 # a second outage means the first fix did not fold
# ops_watch runs as the metronome's sense phase since 2026-11-05 (OPS_METRONOME_MIGRATE_CLOCKS_FENCED): its clock is
# rm-metronome.timer, whose pause excuses a stale stamp exactly as the old timer's did.
# The Dispatcher ticks as the dispatch phase since 2026-11-06 (same item): its clock is rm-metronome.timer too.
ARM_UNITS = {"ops_watch": "rm-metronome.timer", "dispatcher": "rm-metronome.timer"}


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


def dispatcher_mode(runner=subprocess.run, table_path=None):
    """'live' | 'dry' | None: the mode the Dispatcher's clock runs. Once a metronome phase owns rm-dispatcher.timer
    (2026-11-06), that phase's argv decides; before, rm-dispatcher.service's ExecStart."""
    env = os.environ.get("RM_DISPATCHER_MODE")
    if env in ("live", "dry"):
        return env
    import metronome
    phase = metronome.owner_of("rm-dispatcher.timer", table_path)
    if phase:
        try:
            argv = metronome.read_json(table_path or metronome.TABLE)["phases"][phase].get("argv") or []
        except (KeyError, TypeError, AttributeError):
            return None
        return "live" if "--apply" in argv else "dry"
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


def retired_loops_arm(measurer=None, now=None):
    """The retired Relentless/Artisan/Whittle loops stay off (retired_loops_check): -> {"retired_loops": None | reason}.
    A broken arm files the one fixed item LIVE_RESTORE_RETIRED_LOOPS and rings the phone, like a dead Dispatcher. The reading
    (ops_watch/retired_loops.json) is rewritten every pass, which is what the item's `live` promise watches."""
    import retired_loops_check as RL
    res = (measurer or RL.measure)()
    try:
        RL.write_reading(ops_dir() / "retired_loops.json", res, now)
    except OSError:
        pass          # the reading is a witness; the alarm does not depend on it
    return {"retired_loops": RL.arm_reason(res)}


def units_arm(measurer=None, now=None):
    """Every unit text of ours has its one home (ops_clocks.units_problems; page
    design/specs/2026-11-22-units-one-folder/boundary.md): -> {"units": None | reason}. A broken arm files the one fixed
    item LIVE_RESTORE_UNITS. The reading (ops_watch/units.json) is rewritten every pass; the item's `live` promise
    watches it. A measurer that raises is a broken arm with its cause, never a clean one."""
    import ops_clocks as OC
    try:
        probs = (measurer or OC.units_problems)()
    except Exception as e:  # noqa: BLE001 - any failure to look is reported, not swallowed
        probs = ["units: could not look (%s: %s)" % (type(e).__name__, e)]
    line = ("%d unit text(s) out of their one home: %s" % (len(probs), "; ".join(probs[:3])
                                                          + (" ..." if len(probs) > 3 else ""))) if probs else None
    try:
        path = ops_dir() / "units.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(str(path) + ".tmp")
        tmp.write_text(json.dumps({"t": now or time.time(), "status": "alarm" if probs else "ok",
                                   "problems": probs}, indent=1), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass          # the reading is a witness; the alarm does not depend on it
    return {"units": line}


def item_id(line):
    """The fixed id of a promise that has no item of its own: same unit, same item, for good."""
    import live_line
    p = live_line.parse(line)
    name = {"unit": lambda: p["unit"].rsplit(".", 1)[0], "hook": lambda: p["hook"].rsplit(".", 1)[0],
            "role": lambda: p["role"]}[p["kind"]]()
    return "LIVE_RESTORE_" + re.sub(r"\W+", "_", name).upper()


def shared_hosts(rows):
    """-> {item: host}: the broken rows of one pass ({"item", "line", "why"}) that are ONE outage. Two or more items
    broken on the same subject (unit=/hook=/role=) with the same reason, digits aside, map to that subject's fixed host
    `item_id(line)`; the host never maps to itself. A kept row (no why), a row with no promise line, and a subject that
    names nothing share nothing (RIMMANDRAKE_CHARGE_SHARED_OUTAGE_ONCE_FORTY_FIVE_DEATHS: one stop of one shared timer
    was read as 45 deaths). Pure."""
    groups = {}
    for r in rows:
        line, why = r.get("line"), r.get("why")
        if not line or not why or not isinstance(why, str) or not subject(line):
            continue
        groups.setdefault((subject(line), re.sub(r"\d+", "#", why)), []).append(r)
    out = {}
    for rs in groups.values():
        if len({r["item"] for r in rs}) < 2:
            continue
        try:
            host = item_id(rs[0]["line"])
        except Exception:  # noqa: BLE001   a line live_line cannot parse names no host: nothing is excused
            continue
        out.update({r["item"]: host for r in rs if r["item"] != host})
    return out


SHARED_MARK = "shared outage of "     # the head of a host's reading: what puts a cause ticket back when its cause clears


def cause_key(line, why):
    """-> what one cause looks like across promises: the subject's kind and the reason with the subject's own name and
    every digit masked ('hook a.py is not wired in X' and 'hook b.py is not wired in X' are one key), or None for a
    row that names no subject or no reason. Pure. Two faults that read alike are one key: the cost of that merge is
    bounded, since the ticket names each member and a member left broken alone files its own (sweep)."""
    subj = subject(line)
    if not subj or not why or not isinstance(why, str):
        return None
    kind, name = subj.split("=", 1)
    return "%s|%s" % (kind, re.sub(r"\d+", "#", why.replace(name, "<%s>" % kind)))


def cause_id(key, items=None):
    """-> the one ticket of a cause key: LIVE_RESTORE_CAUSE_<8 hex of the key>, the same every pass, so a repeat reopens
    it. A dropped or superseded one cannot be reopened, so its successor (the key's next generation) takes over."""
    items = items or {}
    for gen in range(1, 100):
        cid = "LIVE_RESTORE_CAUSE_%s" % hashlib.sha1(
            (key if gen == 1 else "%s#%d" % (key, gen)).encode("utf-8")).hexdigest()[:8].upper()
        it = items.get(cid)
        if it is None or it.state not in RETIRED:
            return cid
    raise RuntimeError("cause %r: 99 generations retired" % key)


def hosts_of(rows, items=None):
    """-> {item: host}: every broken row of one pass that is part of ONE outage, mapped to that outage's one ticket.
    First the same subject (shared_hosts: one timer under many fixes), then one cause across subjects (cause_key: 24
    hooks unwired by one settings path, 2026-11-08). A subject group joins a cause group as one member, through its
    host. A cause needs two or more members. A host never maps to itself. Pure but for cause_id's read of `items`."""
    shared = shared_hosts(rows)
    groups = {}
    for r in rows:
        k = cause_key(r.get("line"), r.get("why"))
        if k:
            groups.setdefault(k, set()).add(shared.get(r["item"], r["item"]))
    cause = {}
    for k, reps in groups.items():
        if len(reps) >= 2:
            cid = cause_id(k, items)
            cause.update({rep: cid for rep in reps})
    out = {}
    for r in rows:
        if not r.get("why"):
            continue
        rep = shared.get(r["item"], r["item"])
        host = cause.get(rep, shared.get(r["item"]))
        if host and host != r["item"]:
            out[r["item"]] = host
    return out


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


def subject(line):
    """'max_age=2h unit=rm-foo.timer' -> 'unit=rm-foo.timer': what a promise is about, whatever it asks of it and in
    whatever field order live_line accepts. '' when it names none (`once:`). Pure."""
    return next((t for t in (line or "").split() if t.startswith(("unit=", "hook=", "role="))), "")


def parse_retired(raw_lines):
    """-> {subject}: one bare `unit=`/`hook=`/`role=`/`reading=` per line ('#' comments). Anything else raises: a typo must not
    leave a retired thing swept, nor retire a living one."""
    out = set()
    for raw in raw_lines:
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if not re.fullmatch(r"(unit|hook|role|reading)=\S+", line):
            raise ValueError("not a retired subject (want unit=|hook=|role=<name> or reading=<path> alone): %r" % line)
        out.add(line)
    return out


def load_retired(path=None):
    p = Path(path or RETIRED_FILE)
    return parse_retired(p.read_text(encoding="utf-8").splitlines()) if p.exists() else set()


# A closed item cannot be re-closed to change its `live` line, so a file that moved on purpose is listed here: the
# ledger's old reading= path is swept as the new one.
MOVED_READINGS = {}


def moved(line):
    """A ledger promise line with any moved reading= path replaced by its new home. Pure."""
    for old, new in MOVED_READINGS.items():
        line = (line or "").replace("reading=" + old, "reading=" + new)
    return line


EXCUSED = "(excused)"   # paused on purpose: not broken, and no proof it recovered either


def retired_line(line, retired):
    """True when the promise's subject, or the reading it watches (its program was removed on purpose), is retired. Pure."""
    m = re.search(r"(?:^|\s)(reading=\S+)", line)
    return subject(line) in retired or bool(m and m.group(1) in retired)


def promises(items, baseline, retired=()):
    """-> [{"item", "line"}]: the baseline's, then every promise on the ledger. Pure. `once:` is the visible escape and
    is ignored; an item being worked holds its own promise until it closes again; a retired item holds none, and
    nor does any promise whose subject or reading is in `retired` (a unit/hook/role/program removed on purpose)."""
    out = []
    for line in baseline:
        if retired_line(line, retired):
            continue
        iid = item_id(line)
        it = items.get(iid)
        if not (it is not None and it.state in RETIRED):
            out.append({"item": iid, "line": line})
    seen = {r["item"] for r in out}        # a fixed id answers for its baseline line, whatever it closed with
    for iid, it in sorted(items.items()):
        line = getattr(it, "live", None)
        if not line or line.startswith("once:") or it.state in RETIRED or iid in seen or retired_line(line, retired):
            continue
        if it.state in SETTLED or it.live_broken:
            out.append({"item": iid, "line": moved(line)})
    return out


def excused(line, runner=subprocess.run):
    """A timer paused with its own restart armed, or held on a condition that still waits (timers_guard), or a role the
    schedule has switched off."""
    import live_line
    p = live_line.parse(line)
    if p["kind"] == "unit":
        import timers_guard
        if live_line._systemctl("is-active", p["unit"], runner) != "inactive":
            return False                       # running needs no second look; failed or unread is no pause (timers_guard.judge)
        if p["unit"] in timers_guard.held_covered():
            return True                        # a recorded hold whose condition still waits (timers_guard.hold)
        try:
            t = runner(["systemctl", "--user", "list-timers", "--no-legend", "--no-pager"], capture_output=True, text=True,
                       timeout=60, stdin=subprocess.DEVNULL)
            if t.returncode:
                return False
            fired = {w for ln in (t.stdout or "").splitlines() if not timers_guard.still_pending(ln.split()) for w in ln.split()}
            if any(p["unit"] in (units or []) and resume not in fired and live_line._systemctl("is-active", resume, runner) == "active"
                   for resume, units in timers_guard.load_pauses().items()):   # an old record excuses nothing
                return True
            return p["unit"] in timers_guard.hand_armed(t.stdout, runner)
        except Exception:  # noqa: BLE001   could not ask: an outage stays an outage, and the sweep lives
            return False
    if p["kind"] == "role":
        sched = json.loads((HERE.parent / "rimflow" / "dispatcher_schedule.json").read_text(encoding="utf-8"))
        return not any(r.get("name") == p["role"] and r.get("enabled") for r in sched.get("roles", []))
    return False


def just_restarted(line, runner=subprocess.run):
    """A reading that predates its timer's last start, the start within one max_age: a wait for the first run after a
    stop, in live_line's own words (not_yet), not a death. One max_age, not silence (TIMERSTOP_MEASURE_SWITCH_READS_AS_OUTAGE)."""
    import live_line
    try:
        p = live_line.parse(line)
        if p["kind"] != "unit" or not p["unit"].endswith(".timer") or p["max_age_s"] is None:
            return False
        began = float(live_line._systemctl_show(p["unit"], "ActiveEnterTimestamp", runner))
        return finite(began) and live_line.not_yet(live_line.check(line, not_before=began, runner=runner))
    except Exception:  # noqa: BLE001   could not ask: an outage stays an outage
        return False


def real_check(line, runner=subprocess.run):
    import live_line
    try:
        pardon = excused(line, runner)
    except Exception:  # noqa: BLE001   a line that does not parse, an unread schedule: no excuse; check() says what is wrong
        pardon = False
    if pardon:
        return EXCUSED
    why = live_line.check(line, runner=runner)
    return EXCUSED if why and just_restarted(line, runner) else why


def read_items():
    import ops_watch  # noqa: F401   puts ops_core/ on the path
    import ops_ledger as pc
    own = HERE.parents[2]                  # this pass's own shard, or it would not see what it filed until others pull
    return pc._model().replay(pc.read_ledger([*pc.CLONES, *([own] if own not in pc.CLONES else [])])).items


def known_ids():
    """Every item id ever filed, closed ones too (timers_guard mints an alarm name against these)."""
    return set(read_items())


def sweep(now, filer, items, baseline, arms, checker=real_check, sees=True, pusher=None, retired=()):
    """One pass: recheck every promise, reopen what died, put back what recovered. The ledger is the state, so a pass
    that could not file simply tries again. filer(todo, conf) -> {item: None|error}; None files nothing. pusher (see
    phone): a dead arm or a broken timer also rings the owner's phone, whatever the filer did. -> the report."""
    if not sees:
        report = {"t": now, "line": "promises unread: this pass could not see systemd", "blind": True, "broken": [],
                  "unpublished": (_json(sweep_file()) or {}).get("unpublished")}
        OW_atomic(sweep_file(), report)
        return report
    rows = [dict(p, why=checker(p["line"])) for p in promises(items, baseline, retired)]
    excused_n = sum(r["why"] == EXCUSED for r in rows)
    rows = [r for r in rows if r["why"] != EXCUSED]
    rows += [{"item": "LIVE_RESTORE_" + arm.upper(), "line": None, "why": why} for arm, why in sorted(arms.items())]
    todo = []
    shared = hosts_of(rows, items)
    # One outage files ONE ticket, its host's (RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET): a host no row already
    # reads broken is filed broken, its reading naming every member; a member files, reopens and raises nothing of its
    # own. Hosts go FIRST, since the MAX_PER_PASS cut below keeps the head of the list. A host that holds no member
    # this pass is put back (its cause cleared, or one member is left, which then files its own). The report still
    # counts the real promises only.
    hosts = sorted(set(shared.values()) - {r["item"] for r in rows if r["why"]})
    host_rows = []
    for h in hosts:
        members = [r for r in rows if shared.get(r["item"]) == h]
        host_rows.append(dict(members[0], item=h, why="%s%d promises: %s (%s)" % (
            SHARED_MARK, len(members), members[0]["why"], ", ".join(r["item"] for r in members))))
    seen = {r["item"] for r in rows} | set(hosts)
    host_rows += [{"item": iid, "line": None, "why": None} for iid, it in sorted(items.items())
                  if iid not in seen and str(getattr(it, "live_broken", None) or "").startswith(SHARED_MARK)]
    for r in host_rows + rows:
        if r["item"] in shared:
            continue
        it = items.get(r["item"])
        if r["why"] and it is None:
            todo.append({"item": r["item"], "result": "broken", "detail": r["why"], "spawn": True,
                         "title": ("Live promise broken: %s" % r["why"])[:160]})  # cut-ok: an item title (one line); the whole why is the item's detail
        elif r["why"] and not it.live_broken:
            todo.append({"item": r["item"], "result": "broken", "detail": r["why"]})
        elif not r["why"] and it is not None and it.live_broken:
            todo.append({"item": r["item"], "result": "kept", "detail": "sweep: running again"})
    todo.sort(key=lambda t: t["item"] not in shared.values())      # stable: hosts first, the rest in sweep order
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
                errors = {t["item"]: "filer raised %s: %s" % (type(e).__name__, str(e)) for t in todo}
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
    send(row) -> bool and close(key) (ops_core/phone_push; a selftest double). The push dedups by key, so a broken row
    pushes once per outage and a failed send retries next pass. -> [what happened], for the report."""
    out = []
    off = getattr(pusher, "route_off", lambda: None)()
    for r in rows:
        if not phone_worthy(r):
            continue
        pr = phone_row(r) if r["why"] else None
        try:
            if pr and off:
                out.append("phone off %s: %s" % (pr["key"], off))
            elif pr:
                if pusher.send(pr):
                    out.append("pushed %s" % pr["key"])
            else:
                pusher.close("deadman:" + r["item"])
        except Exception as e:  # noqa: BLE001  the phone failing must not stop the sweep or its report
            out.append("push failed %s: %s: %s" % (r["item"], type(e).__name__, str(e)))
    return out


def real_pusher():
    """ops_core/phone_push, unless RM_DEADMAN_PUSH=0. Its Todoist route is retired (owner, 2026-11-19) and off unless
    RM_TODOIST_ALARM_POSTS=1, so today the report reads "phone off" and nothing reaches the phone."""
    if os.environ.get("RM_DEADMAN_PUSH", "1") == "0":
        return None
    sys.path.insert(0, str(HERE / "ops_core"))
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
                rc, out = ing.rimflow("live", t["item"], "--result", t["result"], "--detail", t["detail"],
                                      *(("--shared-with", t["sharedWith"]) if t.get("sharedWith") else ()))
            if rc == 0 and t["result"] == "broken":    # a broken promise is raised, first in the BENCH queue
                rrc, rout = ing.rimflow("raise", t["item"], "--reason", OW.RAISE_REASON)
                if rrc != 0:
                    res.setdefault("_raise", {})[t["item"]] = rout
            res[t["item"]] = None if rc == 0 else out
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
        last = live_line._systemctl_show(unit, "LastTriggerUSec", runner)
        nxt = live_line._systemctl_show(unit, "NextElapseUSecRealtime", runner)
        gap = int(nxt) - int(last) if last.isdigit() and nxt.isdigit() else \
            duration_s(live_line._systemctl_show(unit, "TimersMonotonic", runner)) or 8 * 86400    # unknown: never tighter than a weekly timer allows
        lines.append("unit=%s max_age=%dh" % (unit, max(2, math.ceil(3 * gap / 3600))))
    root = HERE.parent.parent.parent
    wired = json.dumps(json.loads((root / ".claude/settings.json").read_text(encoding="utf-8")).get("hooks") or {})
    lines += ["hook=%s" % h for h in sorted(set(re.findall(r"([\w.-]+\.(?:py|sh))", wired)))]
    sched = json.loads((HERE.parent / "rimflow" / "dispatcher_schedule.json").read_text(encoding="utf-8"))
    lines += ["role=%s max_age=3d" % r["name"] for r in sched["roles"] if r.get("enabled")]
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--file-alarms", action="store_true")
    b = sub.add_parser("baseline")
    b.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "baseline":
        gone = load_retired()
        lines = [x for x in generate_baseline() if subject(x) not in gone]
        fresh = {item_id(x) for x in lines}
        lines += [x for x in load_baseline() if item_id(x) not in fresh and subject(x) not in gone]   # only a hand removes a promise
        if a.write:
            BASELINE.write_text("# The running system's live promises (LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING): "
                                "deadman_check.py sweeps them.\n# A failed line files or reopens LIVE_RESTORE_<NAME>. "
                                "To retire one, move it to live_retired.txt.\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print("%d lines%s" % (len(lines), " written to %s" % BASELINE if a.write else ""))
        return 0
    import live_line
    arms = arm_faults(stamps(), time.time())
    arms.update(retired_loops_arm())
    arms.update(units_arm())
    report = sweep(time.time(), live_filer if a.file_alarms else None, read_items(), load_baseline(),
                   arms, sees=live_line.can_see(),
                   pusher=real_pusher() if a.file_alarms else None, retired=load_retired())
    print("sweep: %s" % report["line"])
    for b_ in report["broken"]:
        print("  %s: %s" % (b_["item"], b_["why"]))
    return 1 if report.get("blind") or report.get("errors") else 0


if __name__ == "__main__":
    sys.exit(main())
