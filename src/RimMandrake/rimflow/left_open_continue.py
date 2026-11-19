#!/usr/bin/env python3
"""left_open_continue: a detached run that ends success with work left is continued by itself
(RIMMANDRAKE_CONTINUE_LEFT_OPEN_RUNS_WITHOUT_A_HAND_RELAUNCH).

2026-11-18: a four-ticket lane closed one ticket and exited, a five-step code split did step one and exited with a
LEFT OPEN note, and the Conductor relaunched each by hand; a third run, stopped by its spend cap mid-job, was resumed
by hand. Owner: "Why are you having to relaunch it?" His 2026-11-15 rule: a wait is automated or paused with an alarm,
never hand-walked.

  plan    finish calls it with the run's clone still standing: what the run left, from its own ledger
  run     `left_open_continue.py run --unit U`, its own unit (<U>-continue, --no-block) started by finish: it waits
          for the run's clone to be given back (detached_helper.launch does), checks the gates again and launches ONE
          continuation of the same work, same model, seat, budget and env, with a header quoting what was left

A run is continued when it ended success (exit 0) and either its item is still open with a `LEFT OPEN:` note written
since the run began, or its brief is a lane (it says "lane" and bullets ticket ids) with tickets still open: the
continuation then works the first open ticket. A run the spend watchdog stopped is continued only when its launch
carried `--continue-on-cap N` (default 0), at most N times along its chain: a cap stays meaningful. Never continued:
a killed, voided or failed run, a closed item (a lane with every ticket closed), an owner-held mod, a paused pipeline,
a `pipe off` switch on its scope; a gate that cannot be read is a named no. At most MAX_PER_DAY continuations per item
(its chain's first item) in 24 h; the next one is the alarm ALARM_ID in the Conductor log and no launch. The header
carries no spend, cap or remainder (owner 2026-11-16: no launched agent is told its spend).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

MAX_PER_DAY = 3
DAY_S = 86400
ALARM_ID = "DETACHED_CONTINUE_LIMIT_REACHED"
HEAD = "LEFT OPEN CONTINUE"
LANE_RX = re.compile(r"\blane\b", re.I)
BULLET_ID_RX = re.compile(r"^\s*[-*]\s+`([A-Z][A-Z0-9_]{7,})`", re.M)
TERMINAL = ("done", "dropped", "superseded")     # model.TERMINAL, without importing the ledger here
READ_STATES = r"""
import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "rimflow"))
import model
items = model.replay(model.read()).items
print(json.dumps({i: getattr(items.get(i), "state", None) for i in sys.argv[1:]}))
"""


def local(t):
    return time.strftime("%Y-%m-%d %I:%M %p %Z", time.localtime(t))


def brief_of(rec):
    """-> the brief the chain began with (a continuation's own brief is header + this), or ""."""
    for p in (rec.get("continue_brief_src"), rec.get("brief_src")):
        try:
            with open(p or "/nonexistent", encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            continue
    return ""


def lane_tickets_of(rec):
    """-> the ticket ids a lane brief bullets, in order; [] for a brief that is not a lane."""
    b = brief_of(rec)
    if not LANE_RX.search(b):
        return []
    return list(dict.fromkeys(BULLET_ID_RX.findall(b)))


def read_states(clone, ids):
    """-> {id: state or None} as the run's clone folds its ledger; raises when it cannot be read."""
    if not ids:
        return {}
    r = subprocess.run([sys.executable, "-c", READ_STATES] + list(ids), cwd=clone, capture_output=True, text=True,
                       timeout=120, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("ledger read in %s exited %d: %s" % (clone, r.returncode, (r.stderr or "")[-200:]))
    return json.loads(r.stdout)


def capped(rec):
    """True when the spend watchdog (or claude's own budget stop) ended the run."""
    import role_launch as RL
    res = RL.read_result({"out": rec.get("out") or "", "err": rec.get("err") or ""})
    return isinstance(res, dict) and (res.get("stopped_by") == "spend_watchdog"
                                      or res.get("subtype") == "error_max_budget_usd")


def last_left_open(notes, item, since):
    """-> the newest note on `item` since `since` that starts LEFT OPEN:, or None."""
    best = None
    for e in notes or []:
        t = DH._epoch(e.get("ts")) if isinstance(e, dict) else None
        if (t is not None and t >= since and e.get("id") == item and e.get("event") == "note"
                and str(e.get("text") or "").strip().upper().startswith(DH.LEFT_OPEN)):
            if best is None or t >= best[0]:
                best = (t, e)
    return best[1] if best else None


# ---------------------------------------------------------------- gates (each injectable; a read failure is a no)
def _paused(mod):
    import pipeline_pause
    return pipeline_pause.blocks(mod)


def _held(mod):
    import mod_owner_hold
    h = mod_owner_hold.held(mod) if mod else None
    return mod_owner_hold.status(h) if h else None


def _voided(unit):
    import control as C
    import run_void
    return bool(C.voided([unit])) or unit in run_void.active()


def _blocked(spec):
    import control as C
    return C.blocked(spec)


GATES = {"paused": _paused, "held": _held, "voided": _voided, "blocked": _blocked}


def gate_no(rec, item, gates):
    """-> why no continuation may start now, or None."""
    g = dict(GATES, **(gates or {}))
    mod = (rec.get("env") or {}).get("RM_CONTROL_MOD")
    spec = {"family": "detached", "item": item, "mod": mod, "stage": (rec.get("env") or {}).get("RM_CONTROL_STAGE")}
    for name, arg in (("voided", rec.get("unit")), ("held", mod), ("paused", mod), ("blocked", spec)):
        try:
            v = g[name](arg)
        except Exception as e:  # noqa: BLE001  a gate that cannot be read never lets a launch through
            return "the %s gate could not be read (%s: %s)" % (name, type(e).__name__, e)
        if v:
            return "the run is voided" if name == "voided" else str(v)
    return None


def today(rec, now, root=None):
    """-> the continuations of this chain's item (or this item) launched in the last DAY_S, oldest first."""
    import stop_resume as SR
    key = rec.get("continue_root_item") or rec.get("item")
    return sorted((r for r in SR.recent_records(root, now)
                   if r.get("continued_from") and (r.get("at") or 0) >= now - DAY_S
                   and key in (r.get("continue_root_item"), r.get("item"))), key=lambda r: r.get("at") or 0)


def relaunched(rec, targets, now, root=None):
    """-> the unit of a run of one of `targets` (the item, its lane's open tickets) launched after this run began (a
    hand relaunch, another continuation), or None."""
    import stop_resume as SR
    later = sorted((r for r in SR.recent_records(root, now) if r.get("unit") != rec.get("unit")
                    and r.get("item") in set(targets) and (r.get("at") or 0) > (rec.get("at") or 0)
                    and r.get("status") not in ("launch_failed", "refused")), key=lambda r: r.get("at") or 0)
    return later[0]["unit"] if later else None


def waiting(got, now):
    """-> why the item's own dated `rimflow wait` forbids a continuation now, or None (no wait, or its date passed).
    A wait is the item saying nothing can move before its date; an unreadable date is a no, named."""
    until = (got or {}).get("wait_until")
    if not until:
        return None
    t = DH._epoch(until)
    if t is None:
        return "its wait date %r could not be read, so it is treated as still running" % (until,)
    return "it waits until %s (rimflow wait), so a continuation now has nothing to do" % local(t) if t > now else None


def plan(rec, got, lane_states, now=None, gates=None, root=None):
    """-> {act: continue|alarm|none, why, ...}. rec: the finished run (its result set); got: read_item's {state, notes}
    for its item from the run's clone; lane_states: {ticket: state} for its lane's tickets."""
    now = now or time.time()
    item = rec.get("item")
    res = str(rec.get("result") or "")
    base = {"unit": rec.get("unit"), "item": item}
    if rec.get("continued_by"):
        return dict(base, act="none", why="already continued as %s" % rec["continued_by"])
    if res.startswith("killed"):
        return dict(base, act="none", why="killed runs are never continued (%s)" % res)
    cap = capped(rec)
    opt = int(rec.get("continue_on_cap") or 0)
    used = int(rec.get("cap_continues_used") or 0)
    if cap and used >= opt:
        return dict(base, act="none", why="stopped by the spend watchdog; its launch's --continue-on-cap %d is %s"
                    % (opt, "used" if opt else "not set"))
    if not cap and not res.startswith("success ("):
        return dict(base, act="none", why="the run did not end success (%s)" % (res or "no result"))
    if not isinstance(got, dict):
        return dict(base, act="none", why="its item's state could not be read from the run's clone")
    state = got.get("state")
    lane = lane_tickets_of(rec)
    open_lane = [t for t in lane if (lane_states or {}).get(t) not in TERMINAL and (lane_states or {}).get(t)]
    noted = last_left_open(got.get("notes"), item, rec.get("at") or 0)
    item_open = bool(state) and state not in TERMINAL
    if item_open and (noted or open_lane or cap):
        target = item
    elif open_lane:
        target = open_lane[0]
    elif not item_open:
        return dict(base, act="none", why="%s is %s" % (item, state or "absent from the ledger"))
    else:
        return dict(base, act="none", why="%s is still %s with no LEFT OPEN: note since the run began and no open "
                                         "lane ticket (finish flags it OWED)" % (item, state))
    waits = waiting(got, now) if target == item else None
    if waits:
        return dict(base, act="none", why=waits)
    no = gate_no(rec, target, gates)
    if no:
        return dict(base, act="none", why=no)
    done = today(rec, now, root)
    if len(done) >= MAX_PER_DAY:
        return dict(base, act="alarm", why="%d continuations of %s in 24 h already (%s)" % (
            len(done), rec.get("continue_root_item") or item, ", ".join(r["unit"] for r in done[-MAX_PER_DAY:])))
    return dict(base, act="continue", target=target, open_lane=open_lane, capped=cap,
                note={"ts": noted.get("ts"), "text": noted.get("text")} if noted else None,
                n=int(rec.get("continue_n") or 0) + 1,
                why=("stopped from outside; --continue-on-cap %d" % opt) if cap else
                    ("LEFT OPEN note" if noted and target == item else "%d lane ticket(s) open" % len(open_lane)))


def header(rec, p, now):
    """The continuation's brief header. Never a word on spend, its cap or what is left of one."""
    lines = ["CONTINUED BY ITSELF (left_open_continue.py, %s): continuation %d of at most %d a day for %s." % (
        local(now), p["n"], MAX_PER_DAY, rec.get("continue_root_item") or rec["item"])]
    if p.get("capped"):
        lines.append("Your previous run %s on %s was stopped from outside before it finished; its launch asked for it "
                     "to be carried on." % (rec["unit"], rec["item"]))
    else:
        lines.append("Your previous run %s on %s ended success with work left, so it is carried on without a hand "
                     "relaunch." % (rec["unit"], rec["item"]))
    if p.get("note"):
        lines.append("Its LEFT OPEN note (%s), verbatim:" % (p["note"].get("ts") or "?"))
        lines += ["> " + ln for ln in str(p["note"].get("text") or "").splitlines() or [""]]
    if p.get("open_lane"):
        lines.append("Still open: %s (lane tickets in the brief below; you work %s first)."
                     % (", ".join("`%s`" % t for t in p["open_lane"]), p["target"]))
    lines.append("This is a fresh session with no memory of the previous one. Your clone stands on origin/main. First "
                 "read `git log --oneline -15` and `python3 src/RimMandrake/rimflow/cli.py show %s`; do not redo work "
                 "that is already published. Then carry on from where it stopped." % p["target"])
    return "\n".join(lines) + "\n"


def alarm(rec, p, now, log_path=None):
    rec = DH.read_record(rec["unit"]) or rec
    if rec.get("continue_alarm"):
        return dict(p, act="none", why="alarm already raised")
    try:
        DH.conductor_line("ALARM %s: %s on %s ended with work left and is NOT continued: %s. Look at the item "
                          "(rimflow show %s) and relaunch by hand or close it." % (
                              ALARM_ID, rec["unit"], rec["item"], p["why"], rec["item"]), now, log_path, head=HEAD)
    except Exception as e:  # noqa: BLE001
        p = dict(p, log_failed=str(e))
    rec["continue_alarm"] = {"at": now, "why": p["why"]}
    DH.write_record(rec)
    journal({"at": DH.iso(now), **{k: v for k, v in p.items() if k != "note"}, "act": "alarm"})
    return dict(p, act="alarmed")


def journal(row, root=None):
    try:
        with open(os.path.join(DH.runs_dir(root), "left_open_continue.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    except OSError:
        pass


def recheck(rec, now, gates=None, root=None):
    """The continuation step's own look, minutes after finish planned it: the plan still stands? -> why not, or None."""
    p = rec.get("continue_plan") or {}
    if p.get("act") != "continue":
        return "no continuation planned"
    if rec.get("continued_by"):
        return "already continued as %s" % rec["continued_by"]
    claim = rec.get("continue_claim")
    if claim and now - claim < 900:
        return "another continuation step claimed it at %s" % local(claim)
    later = relaunched(rec, [p["target"]] + list(p.get("open_lane") or []), now, root)
    if later:
        return "already relaunched as %s" % later
    no = gate_no(rec, p["target"], gates)
    if no:
        return no
    if len(today(rec, now, root)) >= MAX_PER_DAY:
        return "limit"
    return None


def run(unit, now=None, launch_fn=None, gates=None, root=None, log_path=None):
    """The continuation unit's step: launch the planned continuation once. -> {act, why, ...}."""
    now = now or time.time()
    rec = DH.read_record(unit, root)
    if not rec:
        return {"unit": unit, "act": "none", "why": "no record"}
    p = dict(rec.get("continue_plan") or {})
    why = recheck(rec, now, gates, root)
    if why == "limit":
        return alarm(rec, dict(p, why="%d continuations in 24 h already" % MAX_PER_DAY), now, log_path)
    if why:
        if p.get("act") == "continue":
            rec["continue_skipped"] = {"at": now, "why": why}
            DH.write_record(rec, root)
            journal({"at": DH.iso(now), "unit": unit, "item": rec.get("item"), "act": "skipped", "why": why}, root)
        return {"unit": unit, "act": "none", "why": why}
    rec["continue_claim"] = now
    DH.write_record(rec, root)
    root_brief = rec.get("continue_brief_src") or rec.get("brief_src")
    text = header(rec, p, now)
    orig = brief_of(rec)
    if orig.strip():
        text += "\n---- the previous run's brief ----\n" + orig.rstrip() + "\n"
    import stop_resume as SR
    text = SR.with_card_text(p["target"], text, DH.REPO)
    extra = {"continued_from": unit, "continue_root": rec.get("continue_root") or unit,
             "continue_root_item": rec.get("continue_root_item") or rec["item"], "continue_n": p["n"],
             "continue_brief_src": root_brief, "continue_on_cap": int(rec.get("continue_on_cap") or 0),
             "cap_continues_used": int(rec.get("cap_continues_used") or 0) + (1 if p.get("capped") else 0)}
    launch_fn = launch_fn or DH.launch
    try:
        code, out = launch_fn(rec.get("seat"), p["target"], text, rec.get("model"), rec.get("max_s") or "none",
                              rec.get("budget_usd") or 0.0, now=now, env=rec.get("env") or None,
                              clone=SR.given_clone(rec), extra=extra,
                              skip_launch_checks="continuation of %s: the same work, whose launch checks already ran"
                                                 % unit)
    except Exception as e:  # noqa: BLE001
        code, out = 1, "%s: %s" % (type(e).__name__, e)
    rec = DH.read_record(unit, root) or rec
    rec.pop("continue_claim", None)
    m = re.match(r"DETACHED (\S+)", out or "")
    if code == 0 and m:
        rec.update(continued_by=m.group(1), continued_at=now)
        DH.write_record(rec, root)
        line = "%s on %s ended with work left (%s); continued as %s on %s, same model %s (%d of at most %d today)" % (
            unit, rec["item"], p.get("why"), m.group(1), p["target"], rec.get("model"), p["n"], MAX_PER_DAY)
        try:
            DH.conductor_line(line, now, log_path, head=HEAD)
        except Exception as e:  # noqa: BLE001
            print("conductor log not written: %s" % e, file=sys.stderr)
        journal({"at": DH.iso(now), "unit": unit, "item": rec["item"], "act": "continued", "new": m.group(1),
                 "target": p["target"]}, root)
        return {"unit": unit, "act": "continued", "new": m.group(1), "why": p.get("why")}
    rec["continue_refused"] = {"at": now, "why": str(out)[:500]}
    DH.write_record(rec, root)
    try:
        DH.conductor_line("%s on %s ended with work left but its continuation was REFUSED: %s" % (
            unit, rec["item"], " ".join(str(out).split())[:300]), now, log_path, head=HEAD)
    except Exception:  # noqa: BLE001
        pass
    journal({"at": DH.iso(now), "unit": unit, "item": rec["item"], "act": "refused", "why": str(out)[:300]}, root)
    return {"unit": unit, "act": "refused", "why": str(out)[:300]}


def kick_argv(rec):
    """The continuation step as its own unit (--no-block): finish runs inside the run's TimeoutStopSec and the return
    step after it gives the clone back, so the launch (which waits for that return) cannot run inside finish."""
    me = os.path.basename(os.path.abspath(__file__))
    env = ["--setenv", "RM_DISPATCHER_STATE=" + rec["state"], "--setenv", "RIMFLOW_SEAT=" + rec["seat"],
           "--setenv", "AGENT_SEAT=" + rec["seat"]]
    for k in ("RM_DETACHED_POOL", "RM_CONDUCTOR_LOG", "RELENTLESS_ROOT", "PATH", "WSL_INTEROP"):
        if os.environ.get(k):
            env += ["--setenv", "%s=%s" % (k, os.environ[k])]
    return ["/usr/bin/systemd-run", "--user", "--quiet", "--collect", "--no-block", "--unit", rec["unit"] + "-continue",
            "-p", "RuntimeMaxSec=1800", "-p", "WorkingDirectory=/", *env,
            *DH.stop_resolver(candidates(rec, me), ["run", "--unit", rec["unit"]])]


def candidates(rec, me):
    """Where the step's script may run from: the seat clones first, the run's own clone last (its return deletes it
    while the step waits, and the step imports more modules after that wait)."""
    own = rec.get("clone") and os.path.join(os.path.abspath(rec["clone"]), "")
    c = DH.stop_candidates(rec, me, run_clone_last=True)
    return [x for x in c if not (own and os.path.abspath(x).startswith(own))] + \
        [x for x in c if own and os.path.abspath(x).startswith(own)]


def kick(rec, p, runner=subprocess.run):
    """finish's step: start the continuation unit. -> one line."""
    import control as C     # the one admission point: `pipe off family:left_open_continue` stops every kick
    try:
        r = C.launch_unit(kick_argv(rec), {"family": "left_open_continue", "unit": rec["unit"] + "-continue",
                                           "item": p.get("target")},
                          runner=runner, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001
        return "continue NOT kicked: %s: %s" % (type(e).__name__, e)
    if getattr(r, "refused", False):
        return "continue refused by control: %s" % r.why
    return "continue kicked %s-continue (%s)" % (rec["unit"], p.get("why")) if r.returncode == 0 else \
        "continue NOT kicked: %s" % ((r.stderr or r.stdout or "").strip()[:200])


def at_finish(rec, got, clone, now, runner=subprocess.run, continuer=None, states_reader=None):
    """finish's whole step: plan, then alarm or kick. -> (plan, step line)."""
    try:
        lane = lane_tickets_of(rec)
        states = (states_reader or read_states)(clone, lane) if lane else {}
    except Exception as e:  # noqa: BLE001
        return {"act": "none", "why": "lane tickets unreadable: %s" % e}, "continue: lane tickets UNMEASURED (%s)" % e
    try:
        p = plan(rec, got, states, now=now)
    except Exception as e:  # noqa: BLE001
        return {"act": "none", "why": "plan failed: %s" % e}, "continue: plan FAILED (%s: %s)" % (type(e).__name__, e)
    fresh = DH.read_record(rec["unit"]) or rec
    fresh["continue_plan"] = p          # written before the kick: the continuation step reads it
    DH.write_record(fresh)
    if p["act"] == "alarm":
        alarm(fresh, p, now)
        return p, "continue: ALARM %s (%s)" % (ALARM_ID, p["why"])
    if p["act"] != "continue":
        return p, "continue: none (%s)" % p["why"]
    return p, (continuer or (lambda r, q: kick(r, q, runner)))(fresh, p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="the continuation unit's step (finish starts it)")
    r.add_argument("--unit", required=True)
    s = sub.add_parser("plan", help="read-only: what finish would plan for a finished run, from its record alone")
    s.add_argument("--unit", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        x = run(a.unit)
    else:
        rec = DH.read_record(a.unit) or {}
        x = rec.get("continue_plan") or {"act": "none", "why": "no plan on the record (finish wrote none)"}
    print("%s %s: %s" % (x.get("act"), a.unit, x.get("why")))
    return 0 if x.get("act") in ("continued", "none", "continue", "alarmed", "alarm") else 1


if __name__ == "__main__":
    sys.exit(main())
