#!/usr/bin/env python3
"""The account actuator: the act of the account plan's pass on this machine. account_plan.tick decides (one pure
decision, the plan file's rules) and drives check() here with that decision; this module holds no rule of its own.

What it does with each decision: the switch (`claude-account use`) and the fleet stop and start, each armed and
disarmed around the call; the transition markers that tell the plan's switch from a hand switch; the notice
(notice.json) that each launch gate and the checkpoint hook read; the state file; the drain while live runs finish;
the end of an account (account_end.py: the warning, the save order at the line, the pause before an emergency
switch); the repeats each REPEAT_S while an account ends; the meter poll near a line. Live runs finish
(owner 2026-11-20: "And yes for live runs finish past, absolutely. Actually 0.1% is even ok kept. We just don't want
to crash to zero and get stuck."): a switch or a stop that falls due waits while a detached run is live.

Pages: design/specs/2026-11-20-account-drain/boundary.md (the drain) and design/specs/2026-11-24-account-end/boundary.md
(the end of an account); the decision: design/specs/2026-11-24-account-plan-one-file/boundary.md.

Brake: a file HOLD in the output dir makes every pass passive (the owner's or an agent's brake).

    account_actuator.py check [--dry-run]   one pass: the same as `./acct tick` (the timer runs `account_plan.py pass`)

Env seams (selftests): RM_SWITCH_PLAN_DIR (output dir), RM_CLAUDE_ACCOUNT (switcher), RM_ACCOUNTS_DIR (the switcher's
folder, whose log.jsonl names the last switch).
"""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE_OUT = Path("/mnt/d/ClaudeWork/rimmandrake/switching_plan")   # the folder keeps its name: the live state is there
OUT = Path(os.environ.get("RM_SWITCH_PLAN_DIR", LIVE_OUT))
CA = os.environ.get("RM_CLAUDE_ACCOUNT") or str(Path.home() / ".local/bin/claude-account")
SWITCH_LOG = Path(os.environ.get("RM_ACCOUNTS_DIR", Path.home() / ".claude-accounts")) / "log.jsonl"
WEEK = 7 * 86400
STALE_PENDING_S = 2400  # arm + use + disarm at 600 s each plus the reads: a pending marker older is a pass that died
NOTICE_FRESH_S = 20 * 60  # readers (slot_allocator) ignore an older notice: the timer stopped
DRY = False
clock = time.time  # a seam: check() re-reads it after the slow poll
sleep = time.sleep  # a seam: the pause before an emergency switch, and the repeats while an account ends
sys.path.insert(0, str(HERE))
import account_end as AE  # noqa: E402


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).astimezone().isoformat(timespec="seconds")


def epoch(s):
    try:
        return datetime.fromisoformat(str(s)).timestamp() if s else None
    except ValueError:
        return None


def write_atomic(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True))
    os.replace(tmp, path)


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def load_state() -> dict:
    return read_json(OUT / "state.json", {}) or {}


def save_state(st: dict) -> None:
    write_atomic(OUT / "state.json", st)


def read_markers() -> dict:
    d = OUT / "markers"
    out = {}
    if d.is_dir():
        for p in d.glob("*.json"):
            v = read_json(p)
            if isinstance(v, dict):
                out[p.stem] = v
    return out


def write_marker(key: str, obj: dict) -> None:
    write_atomic(OUT / "markers" / f"{key}.json", obj)


def log(rec: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec["at"] = iso(time.time())
    if DRY:
        rec["dry"] = True
    with open(OUT / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(json.dumps(rec, sort_keys=True))


def next_reset(r: dict, now: float):
    """Epoch of the account's next weekly reset: the recorded one, rolled a week on while it has passed."""
    rs = epoch((r or {}).get("week_resets_at"))
    if rs is None:
        return None
    while rs <= now:
        rs += WEEK
    return rs


def reset_passed(r: dict, now: float) -> bool:
    """The reading is from before a reset that has since landed: its figures say nothing about now."""
    rs = epoch((r or {}).get("week_resets_at"))
    return rs is not None and rs <= now


def usable(r) -> bool:
    return bool(r) and r.get("source") == "MEASURED" and not r.get("stale") and r.get("week_pct_left") is not None


def switch_key(frm: str, to: str, target_rec: dict) -> str:
    rs = epoch((target_rec or {}).get("week_resets_at"))
    wk = datetime.fromtimestamp(rs, timezone.utc).astimezone().strftime("%Y%m%d") if rs else "unknown"
    return f"use_{frm}_to_{to}_{wk}"


def stop_key(name: str, rec: dict, now: float) -> str:
    rs = next_reset(rec, now)
    return f"{name}_" + (datetime.fromtimestamp(rs, timezone.utc).astimezone().strftime("%Y%m%d") if rs else "unknown")


def switches(path=None) -> list | None:
    """Every switch that changed the live account, oldest first, from the switcher's own append-only log; [] when it
    has none, None when it cannot be read. A malformed line is skipped (a line being appended right now)."""
    try:
        text = Path(path or SWITCH_LOG).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    except OSError:
        return None
    out = []
    for ln in text.splitlines():
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("op") == "use" and r.get("changed"):
            out.append(r)
    return out


def last_switch(path=None):
    """The newest switch that changed the live account: {from, to, ts}, or None when the log has none."""
    return (switches(path) or [None])[-1]


def manual_switch(sw, markers: dict, live, history=None):
    """The last switch when it put `live` there and the plan did not make it, else None. The plan writes its marker
    before it calls `use` and the call ends inside STALE_PENDING_S; one call makes at most ONE switch, the first of its
    transition in the switcher's log (`history`, default the log; by POSITION, a shared second proves no order) after
    the marker, landing no later than the call `ended` (both stamps are this machine's wall clock, to the second).
    Any other switch of that transition in the span is his (RIMMANDRAKE_ATTRIBUTE_MANUAL_SWITCH_BY_LOG_NOT_OLD_MARKER:
    his own lukas->system->lukas->system inside 40 min was read as the plan's and a later pull could undo it). A
    lapsed marker never called `use`. A switch with no readable time is the plan's to judge: nothing can say it is
    recent; an unreadable log falls back to the marker's window alone."""
    ts = epoch((sw or {}).get("ts"))
    if ts is None or sw.get("to") != live:
        return None
    if history is None:
        history = switches()
    for m in markers.values():
        at = epoch(m.get("at"))
        if not (m.get("from") == sw.get("from") and m.get("to") == sw.get("to") and m.get("phase") != "lapsed"
                and at is not None and 0 <= ts - at <= STALE_PENDING_S):
            continue
        ended = epoch(m.get("ended"))
        if ended is not None and ts > ended:
            continue  # landed after the plan's call returned: not the plan's
        if history:
            same = [r for r in history if r.get("from") == sw.get("from") and r.get("to") == sw.get("to")
                    and at <= (epoch(r.get("ts")) or -1) <= ts]
            if not same or same[-1] != sw:  # sw is the newest switch: the log's last of its transition, or after it
                same.append(sw)
            if len(same) > 1:
                continue  # the plan's switch is an earlier one in the log: this one is his
        return None
    return sw


def runs_why(live_runs) -> str:
    if live_runs is None:
        return "the live runs are UNMEASURED (systemd could not be read), so they count as live"
    return "%d live run(s): %s" % (len(live_runs), ", ".join(live_runs[:4]) + (" ..." if len(live_runs) > 4 else ""))


def drained(d: dict, plan: dict, live_runs) -> dict:
    """A switch or stop due on an account at its line waits while a detached run is live: -> the decision as a drain
    (`soft`, drain and account_end true: the save order at the line), or d, `emergency` true when it goes with a run
    live on an account at 1%. live_runs None (unreadable) counts as live. An account kept well above zero waits for its
    runs (no emergency), down to 1%."""
    if d.get("do") not in ("switch", "stop") or (d["do"] == "switch" and not d.get("under")):
        return d
    if live_runs is not None and not live_runs:
        return d
    p, ln, cfg = d.get("pct_left"), d.get("line"), plan["account_end"]
    if p is None or ln is None:
        return d
    if p <= cfg["emergency_pct"]:
        return {**d, "emergency": True} if AE.has_emergency(ln, cfg) else d
    w = d.get("warn_line")
    if w is None or p > w:      # past its window with budget left: the runs finish as they are, nobody is told to end
        return {**d, "do": "soft", "drain": True, "drain_of": d["do"],
                "why": f"{d['account']} at {p}% must be left: the {d['do']} waits while live runs finish "
                       f"({runs_why(live_runs)}); no new start; it goes when they end. Was: " + str(d.get("why"))}
    return {**d, "do": "soft", "drain": True, "account_end": True, "drain_of": d["do"],
            "why": f"{d['account']} at {p}% is at its {ln}% line: the {d['do']} waits while live runs "
                   f"save and end ({runs_why(live_runs)}); no new start; it goes when they end"
                   + (f" or at {cfg['emergency_pct']}%" if AE.has_emergency(ln, cfg) else "") + ". Was: "
                   + str(d.get("why"))}


def lowered(ep: dict, line) -> bool:
    """The account's line fell after its warning (a dated exception opened more of it): the warning no longer stands."""
    return line is not None and ep.get("line") is not None and line < ep["line"]


def run(argv, full=False, timeout=600):
    """-> (rc, out). full=True returns stdout whole: a parser must never see a truncated tail (the ~2030-char status
    once lost its opening brace to a 2000-char tail)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, f"{argv[1:2]} timed out after {timeout} s"
    except OSError as e:
        return 127, f"{argv[:1]} could not run: {e}"
    return r.returncode, r.stdout if full else (r.stdout + r.stderr)


def switcher_status() -> dict:
    """The switcher's whole status when it names the live account, else {} (account_live, the one reader)."""
    sys.path.insert(0, str(HERE))
    import account_live as AL
    return AL.status_of(AL.read(exe_path=CA))


def meter_now() -> dict:
    sys.path.insert(0, str(HERE))
    import account_usage
    return account_usage.read_now().get("accounts") or {}


def levelled(meter: dict, model=None) -> dict:
    """Pure. The meter as a run of `model` sees it: each account's week figures are the LOWER of its all-models
    weekly limit and that model's own (account_usage.week_left_for), `week_limit` naming which; `model_weeks_left`
    carries every per-model limit as LEFT. model None (the plan's `level_model` unset) changes no figure: the machine
    runs every model, so only the all-models limit is the whole account's level
    (RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED)."""
    sys.path.insert(0, str(HERE))
    import account_usage
    out = {}
    for n, r in (meter or {}).items():
        r = dict(r or {})
        r["model_weeks_left"] = {k: (w or {}).get("pct_left") for k, w in (r.get("model_weeks") or {}).items()}
        lv, lim, h = account_usage.week_left_for(r, model)
        r["week_limit"] = lim
        if lim != "all models":
            r.update(week_pct_left=lv, week_pct_used=round(100 - lv, 1), hours_to_week_reset=h,
                     week_resets_at=r["model_weeks"][lim].get("resets_at"))
        out[n] = r
    return out


def next_refill(meter: dict, plan: dict, now: float) -> dict:
    """The first metered reset (by its time, then the plan's order) of an account that a refill puts above its line:
    the reset that can give the fleet headroom. plan: the numbers in the shape of account_plan.legacy_view (each
    account's line is its leave_pct_left, else the wait floor; that shape has no window and no dated exception)."""
    for rs, name in sorted(((rs, n) for n in plan["order"] if (rs := next_reset(meter.get(n), now)) is not None),
                           key=lambda pair: (pair[0], plan["order"].index(pair[1]))):
        leave = (plan["accounts"].get(name) or {}).get("leave_pct_left")
        if 100 > (leave if leave is not None else plan["floors"]["wait_pct_left"]):
            return {"reset_at": iso(rs), "reset_account": name}
    return {}


def meter_poll() -> None:
    rc, out = run([sys.executable, str(HERE / "account_usage.py"), "poll"], timeout=420)
    log({"do": "meter_poll", "rc": rc, "out": out})


def notify_stop(state: dict) -> None:
    """Existing phone route, once per successful stop; failed deliveries retry on the next pass."""
    stopped = state.get("stopped") or {}
    if not stopped or stopped.get("phone_notified"):
        return
    from ops_core import phone_push
    until = stopped.get("reset_at")
    resume = (f"The next account refills at {until}; the fleet will restart after the switcher confirms headroom "
              "(checked every five minutes)." if until else
              "The next account's reset time is unmeasured; the fleet will restart once headroom is confirmed.")
    try:
        phone_push.send({"key": "account-plan-hard-stop:" + stopped["at"], "kind": "red",
                         "title": "Claude stopped: all accounts are out",
                         "detail": "Claude usage is out on every account. The Claude windows were stopped. " + resume})
    except Exception as e:
        log({"do": "phone_notice_failed", "error": str(e)})
        return
    stopped["phone_notified"] = True
    save_state(state)


def record_stop(state: dict, d: dict, now: float) -> None:
    state["stopped"] = {"account": d.get("account"), "key": d.get("key"), "at": iso(now),
                        **{k: d[k] for k in ("reset_at", "reset_account") if k in d}}
    save_state(state)  # crash recovery never repeats fleet-stop just to deliver the notice
    write_notice({**d, "do": "stop", "stopped_at": iso(now)}, now)
    notify_stop(state)


def write_notice(d: dict, now: float) -> None:
    write_atomic(OUT / "notice.json", notice_of(d, now, read_json(OUT / "notice.json", {}) or {}))


def notice_of(d: dict, now: float, prev: dict) -> dict:
    """The notice of the decision d (pure). prev: the notice before it, whose `since` goes on while the state does."""
    state = {"soft": "soft", "stop": "stop", "stopped": "stop"}.get(d["do"], "none")
    since = (d.get("stopped_at") if state == "stop" else None) or (
        prev.get("since") if prev.get("state") == state and prev.get("since")
        and bool(prev.get("drain")) == bool(d.get("drain")) else iso(now))     # a drain's own start bounds a pull
    warned = bool(d.get("warning")) and state in ("soft", "none") and not d.get("drain")
    # a soft decision only because the live level is not read (account_plan.decide `unread`): no switch is pending
    unread = state == "soft" and bool(d.get("unread")) and not d.get("account_end")
    msg = {"soft": ("the account is at its line: save your work now and publish; no new start" if d.get("account_end")
                    else "the level of %s is not read yet: no new run starts until it is read; live runs go on" % (
                        d.get("account") or "the live account") if unread
                    else "draining: no new start; live runs finish on this account, then it switches" if d.get("drain")
                    else "the account nears its line: save a note, publish what is done, keep working; new work "
                         "still starts" if warned else "switch pending: publish and finish; no new helpers"),
           "stop": "hard stop: the fleet is stopped until a reset",
           "none": "the account nears its line: save a note, publish what is done, keep working; new work still starts"
                   if warned else ""}[state]
    return {"state": state, "since": since, "at": iso(now), "account": d.get("account"),
            "line": d.get("line"), "pct_left": d.get("pct_left"), "message": msg,
            "why": d.get("why"), "drain": bool(d.get("drain")) and state == "soft",
            "account_end": bool(d.get("account_end")) and state == "soft",
            # what the checkpoint hook reads (switch_checkpoint_signal.py): a soft notice of an unread level is none
            "switch_pending": state == "soft" and not unread,
            # the warning's text, which a run that starts now gets in its start package
            "warning": d.get("warning_text") if warned else None,
            **({k: d.get(k) or prev.get(k) for k in ("reset_at", "reset_account")} if state == "stop" else {})}


def armed_call(st: dict, argv: list, still=None) -> dict:
    """arm if the machine is disarmed, run the switcher verb, disarm again if it was disarmed before. `still()` is
    asked after a slow arm whether the decision still holds; when it does not, the verb is skipped as 'lapsed'. A
    `still()` that returns a verb list instead names a brake now due in its place: it runs while the machine is armed."""
    machine = st.get("machine") or ""
    was_armed = bool(st.get("armed"))
    out = {}
    if not was_armed:
        out["arm"] = run([CA, "arm", "--confirm", machine])
    ok = still() if (was_armed or out["arm"][0] == 0) and still is not None else True
    if isinstance(ok, list):
        out[argv[0]] = (None, f"lapsed: the decision no longer holds after arming; {ok[0]} is due instead")
        out[ok[0]] = run([CA, *ok])
    elif not ok:
        out[argv[0]] = (None, "lapsed: the decision no longer holds after arming")
    elif was_armed or out["arm"][0] == 0:
        out[argv[0]] = run([CA, *argv, *(["--confirm", machine] if argv[0] == "use" else [])])
    else:
        out[argv[0]] = (None, "not armed")
    if not was_armed:
        out["disarm"] = run([CA, "disarm"])
    return out


def live_detached_runs(runner=subprocess.run):
    """-> the live detached run units (rm-detached-* services, active or activating, less their -return and -continue
    steps), or None when systemd cannot be read."""
    try:
        r = runner(["systemctl", "--user", "list-units", "--type=service", "--state=active,activating", "--plain",
                    "--no-legend", "rm-detached-*"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    units = [ln.split()[0] for ln in (r.stdout or "").splitlines() if ln.split()]
    return [u[:-len(".service")] for u in units if u.endswith(".service")
            and not u[:-len(".service")].endswith(("-return", "-continue"))]


def default_runs():
    """The live plan dir reads the live runs; a test's plan dir never does (it reads none unless it hands runs_fn)."""
    return live_detached_runs() if OUT == LIVE_OUT else []


def default_burn(live, now, cfg):
    """The live plan dir reads the live series; a test's plan dir reads none (unknown: the safe values)."""
    return (AE.read_burn(live, now, cfg, since=live_since(live)) if OUT == LIVE_OUT
            else AE.stale_burn("a test's plan reads no series"))


def live_since(live):
    """When `live` last went live, by the switcher's log; None when the log's last switch is to another account."""
    sw = last_switch()
    return epoch(sw.get("ts")) if sw and sw.get("to") == live else None


def burn_now(live, meter, now, cfg, burn_fn):
    """The burn this pass acts on. A level that cannot be read, or is older than stale_min, makes it stale too: the
    warning line, the pause and each text then use the safe values, whatever the series says."""
    r = meter.get(live) or {}
    if not usable(r) or (r.get("age_min") is not None and r["age_min"] > cfg["stale_min"]):
        return AE.stale_burn("the level reads %s, %s min old" % (
            str(r.get("source")) + (" stale" if r.get("stale") else ""), num_age(r)))
    try:
        return burn_fn(live, now, cfg)
    except Exception as e:  # noqa: BLE001  could not read is the safe value, never a slow burn
        return AE.stale_burn("%s: %s" % (type(e).__name__, e))


def num_age(r):
    return "?" if r.get("age_min") is None else "%g" % round(r["age_min"])


def check(decide, load_plan, dry: bool = False, now=None, meter_fn=meter_now, poll_fn=meter_poll, runs_fn=None, burn_fn=None, orders=None,
          passes: int = 1) -> int:
    """One pass under an exclusive non-blocking lock: a pass that finds another running stands down (the markers are
    not a lock, and two passes could both switch). `passes` > 1: while an account ends the pass repeats each REPEAT_S.
    decide(meter, live, now, plan, state, markers, polled=, manual=, live_runs=, burn=) -> the decision, and
    load_plan() -> the numbers in the shape of account_plan.legacy_view: the caller's (account_plan.tick)."""
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "check.lock", "a") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            log({"do": "skip", "why": "another pass holds check.lock", "acted": False})
            return 0
        rc = _check(decide, load_plan, dry, now, meter_fn, poll_fn, runs_fn or default_runs, burn_fn or default_burn, orders)
        for _ in range(passes - 1):
            if dry or not load_state().get("account_end") or load_state().get("stopped") or (OUT / "HOLD").exists():
                break
            sleep(REPEAT_S)
            rc = _check(decide, load_plan, dry, None, meter_fn, poll_fn, runs_fn or default_runs, burn_fn or default_burn, orders)
        if not dry and OUT == LIVE_OUT:
            flush_events()
    if not dry and OUT == LIVE_OUT and not (OUT / "HOLD").exists():
        resume_stopped_runs()
    return rc


def resume_stopped_runs():
    """After a live pass: start the sweep that resumes the detached runs a fleet stop killed (rimflow/stop_resume.py,
    RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL). Only for the live plan dir, so a test's pass never reads the live runs;
    never under HOLD (it acts on nothing); never fails the pass. Writes no plan line: headroom reads the plan log."""
    try:
        sys.path.insert(0, str(HERE.parent / "rimflow"))
        import stop_resume
        print(stop_resume.kick(plan_dir=str(OUT), acct_log=str(SWITCH_LOG)))
    except Exception as e:  # noqa: BLE001
        print(f"stop_resume did not run: {type(e).__name__}: {e}", file=sys.stderr)
    try:    # the runs that saved and ended because the account ended
        import left_open_continue
        print(left_open_continue.kick_waiting(plan_dir=str(OUT)))
    except Exception as e:  # noqa: BLE001
        print(f"left_open_continue did not run: {type(e).__name__}: {e}", file=sys.stderr)


ACTS = ("soft", "stop", "stopped", "switch")
REPEAT_S = 60   # page LIMITS, poll_min: 4 repeats fit inside one 5-min beat


def default_orders():
    """The live plan dir orders the live runs; a test's plan dir never does (it hands its own)."""
    return AE.Orders() if OUT == LIVE_OUT else None


def record_step(state: dict, step: str, text: str, now: float) -> None:
    """One Conductor log line now, and one ledger event owed (flush_events writes it after the pass's acts, so a slow
    publish never delays an order or a switch). Never raises: a record never stops a step."""
    state.setdefault("account_end_events", []).append(f"ACCOUNT END {step} at {iso(now)}: {text}")
    save_state(state)
    log({"do": "account_end", "step": step, "text": text, "acted": False})
    if OUT == LIVE_OUT:
        try:
            AE.conductor_line(f"{step}: {text}", now)
        except Exception as e:  # noqa: BLE001
            print(f"account_end: conductor log not written: {e}", file=sys.stderr)


def flush_events() -> None:
    state = load_state()
    texts = state.get("account_end_events") or []
    if not texts:
        return
    try:
        left_over = AE.ledger_events(texts)
    except Exception as e:  # noqa: BLE001  tried again at the next pass
        print(f"account_end: ledger events not written: {type(e).__name__}: {e}", file=sys.stderr)
        return
    state = load_state()
    state["account_end_events"] = left_over
    if not left_over:
        state.pop("account_end_events")
    save_state(state)


def end_episode(state: dict, d: dict, orders, why: str) -> None:
    """The account did not end after all (a reset, another account live): its undelivered orders are withdrawn."""
    ep = state.pop("account_end", None) or {}
    save_state(state)
    if ep.get("acts") and orders is not None:
        n, err = orders.withdraw(ep["acts"], why)
        log({"do": "account_end", "step": "over", "text": f"{why}; {err or '%s order(s) withdrawn' % n}", "acted": False})


def send_orders(state: dict, d: dict, step: str, mode: str, text: str, runs, orders, now, deadline=None):
    """The order of one step to every live run that has not had it. -> (units ordered now, why not or None)."""
    ep = state["account_end"]
    seen = ep.setdefault("ordered", {})
    store, blind = [], []
    if orders is not None:
        try:
            store = orders.store_runs()
        except Exception as e:  # noqa: BLE001  said in the step's record; the runs systemd lists are ordered all the same
            blind = ["the control store could not be read (%s)" % e]
    units = sorted(set(runs or []) | set(store))
    todo = [u for u in units if step not in (seen.get(u) or {})]
    blind += [] if runs is not None else ["systemd could not be read"]
    if not todo or orders is None:
        return [], "; ".join(blind) or None
    act, err = orders.send(todo, mode, text, deadline)
    if err:
        return [], "; ".join(blind + ["the orders could NOT be written: " + err])
    ep.setdefault("acts", []).append(act)
    for u in todo:
        seen.setdefault(u, {})[step] = now
    save_state(state)
    return todo, "; ".join(blind) or None


def facts(d: dict, plan: dict, burn, runs) -> str:
    b = burn or {}
    rate = "burn STALE (%s)" % (b.get("why") or "unread") if b.get("stale", True) or b.get("rate") is None else \
        "burn %.3f%% a minute" % b["rate"]
    m = AE.minutes_left(d["pct_left"], burn, plan["account_end"]) if d.get("pct_left") is not None else None
    em = AE.has_emergency(d.get("line"), plan["account_end"])
    return (f"{d['account']} at {d.get('pct_left')}% (line {d.get('line')}%, warning line {d.get('warn_line')}%), {rate}, "
            + (("about %s min to the emergency step" % ("?" if m is None else int(m))) if em else "no emergency step on "
               "this account") + f"; {runs_why(runs)}")


def open_episode(state: dict, d: dict, now: float) -> bool:
    """The end of the live account is recorded (its warning line latched). -> True when it opens now."""
    if (state.get("account_end") or {}).get("account") == d["account"]:
        return False
    state["account_end"] = {"account": d["account"], "warn_line": d.get("warn_line"), "line": d.get("line"),
                            "warned_at": iso(now)}
    save_state(state)
    return True


def warn_step(state: dict, d: dict, plan: dict, burn, runs, orders, now: float) -> None:
    """Step 1, at the warning line: every live run is warned (save a note, publish what is done, keep working); it ends
    no run and refuses no start. Recorded once; a run that appears later gets the warning too."""
    first = open_episode(state, d, now)
    sent, err = send_orders(state, d, "warn", "warn", d["warning_text"], runs, orders, now)
    if first:
        record_step(state, "warning", facts(d, plan, burn, runs) + f"; warned: {', '.join(sent) or 'none'}"
                    + (f"; {err}" if err else ""), now)
    elif err:
        log({"do": "account_end", "step": "warn", "text": err, "acted": False})


def save_step(state: dict, d: dict, plan: dict, burn, runs, orders, now: float) -> None:
    """Step 2, at the line of an account whose switch waits for its runs: every live run is told to save and end.
    Recorded once; a run that appears later gets its order too."""
    open_episode(state, d, now)
    ep = state["account_end"]
    first = not ep.get("save_at")
    if first:
        ep["save_at"] = iso(now)
        save_state(state)
    last = d.get("drain_of") != "switch"
    text = AE.save_text(d["account"], d.get("pct_left"), burn, d.get("line"), plan["account_end"], last)
    sent, err = send_orders(state, d, "save", "at_easy_spot", text, runs, orders, now)
    if first:
        record_step(state, "save order at the line", facts(d, plan, burn, runs) + f"; ordered: {', '.join(sent) or 'none'}"
                    + (f"; {err}" if err else ""), now)
    elif err:
        log({"do": "account_end", "step": "save", "text": err, "acted": False})


def emergency_step(state: dict, d: dict, plan: dict, burn, runs, runs_fn, orders, now: float) -> bool:
    """Step 3: the emergency order, then the pause. -> True to go on with the switch, False on a HOLD. A pass that died
    in the pause finds its start in the state and waits only what is left."""
    open_episode(state, d, now)
    ep = state["account_end"]
    em, first = ep.get("emergency"), False
    if not em:
        first = True
        secs = AE.pause_s(burn, plan["account_end"])
        em = ep["emergency"] = {"at": now, "pause_s": secs}
        save_state(state)
    last = d["do"] == "stop"
    text = AE.emergency_text(d["account"], d.get("pct_left"), burn, em["pause_s"], last)
    t0 = clock()
    sent, err = send_orders(state, d, "emergency", "write_now", text, runs, orders, now, em["at"] + em["pause_s"])
    if first:
        record_step(state, "emergency", facts(d, plan, burn, runs) + f"; pause {em['pause_s']} s; ordered: "
                    f"{', '.join(sent) or 'none'}" + (f"; {err}" if err else ""), now)
    while True:
        left_s = em["at"] + em["pause_s"] - (now + clock() - t0)
        if left_s <= 0:
            break
        try:
            still_live = runs_fn()
        except Exception:  # noqa: BLE001  unreadable counts as live
            still_live = None
        if still_live is not None and not still_live:
            break       # the last run ended: nothing is left to wait for
        sleep(min(5, left_s))
        if (OUT / "HOLD").exists():
            break
    return not (OUT / "HOLD").exists()


def saved_lines(state: dict, orders) -> str:
    """What each ordered run had saved, read before the switch stops it."""
    ep = state.get("account_end") or {}
    got = ep.get("ordered") or {}
    if not got or orders is None:
        return "no run was ordered"
    return "; ".join("%s: %s" % (u, orders.saved(u, min(v.values()))) for u, v in sorted(got.items()))


def _check(decide, load_plan, dry, now, meter_fn, poll_fn, runs_fn=default_runs, burn_fn=default_burn, orders=None) -> int:
    global DRY
    DRY = dry
    t0 = clock()
    now = now or t0
    plan, state = load_plan(), load_state()
    if (OUT / "HOLD").exists():
        log({"do": "passive", "why": f"{OUT / 'HOLD'} present"})
        return 0
    st = switcher_status()
    live = st.get("live")
    raw_meter_fn = meter_fn
    meter_fn = lambda: levelled(raw_meter_fn(), plan.get("level_model"))  # noqa: E731  unset: all-models only
    meter = meter_fn()
    t1 = clock()
    now += t1 - t0  # a slow status or meter read moves time on too: windows are judged when the pass acts
    t_now = t1  # the clock sample `now` stands for: a stamp taken later is now + clock() - t_now

    def manual_now():  # read at each decision: a human can switch during a slow poll
        return manual_switch(last_switch(), read_markers(), live)
    try:
        runs = runs_fn()
    except Exception:  # noqa: BLE001  unreadable runs count as live
        runs = None
    orders = orders or default_orders()
    burn = burn_now(live, meter, now, plan["account_end"], burn_fn)
    d = decide(meter, live, now, plan, state, read_markers(), manual=manual_now(), live_runs=runs, burn=burn)
    pre = None
    if d.get("poll"):
        last = epoch(state.get("last_poll")) or 0
        gap = plan["account_end"]["poll_min"] if d.get("warn_line") is not None and d.get("pct_left") is not None and (
            d["pct_left"] <= d["warn_line"] + 1) else plan["fresh"]["max_age_min"]
        if not dry and now - last >= gap * 60 - 5:  # 5 s: a repeat each 60 s must not miss its poll by the pass's own time
            # the poll can take minutes: if this pass would brake on what it already sees, the brake goes out first
            pre = decide(meter, live, now, plan, state, read_markers(), polled=True, manual=manual_now(),
                         live_runs=runs, burn=burn)
            if ((pre["do"] == "stop" and (state.get("stopped") or {}).get("account") != live)
                    or (pre["do"] == "switch" and pre.get("under"))):
                d = pre  # a brake on a spent account is never deferred behind a slow poll (agents keep burning)
            else:
                if pre["do"] in ACTS:       # a stopped fleet stays a stop; the rest brake soft during the poll
                    write_notice(pre if pre["do"] == "stopped" else {**pre, "do": "soft"}, now)
                state["last_poll"] = iso(now)
                save_state(state)
                poll_fn()
                st = switcher_status()
                live = st.get("live")
                meter = meter_fn()
                t_now = clock()
                now += t_now - t1  # time moved during the poll: windows and resets are judged at the new time
                burn = burn_now(live, meter, now, plan["account_end"], burn_fn)
                if (OUT / "HOLD").exists():
                    log({"do": "passive", "why": f"{OUT / 'HOLD'} appeared during the poll"})
                    return 0
        if d is not pre:
            d = decide(meter, live, now, plan, state, read_markers(), polled=True, manual=manual_now(), live_runs=runs,
                       burn=burn)
    d.update(next_refill(meter, plan, now))
    if state.get("stopped"):
        d["stopped_at"] = state["stopped"].get("at")
    rec = {"do": d["do"], "live": live, "to": d.get("to"), "why": d.get("why"), "pct_left": d.get("pct_left"),
           "line": d.get("line")}
    if dry or d["do"] in ("passive", "skip", "hold"):
        pl, ln = d.get("pct_left"), d.get("line")
        if not dry and d["do"] == "hold" and pl is not None and ln is not None and pl <= ln + plan["soft_margin_pct"]:
            write_notice({**d, "do": "soft"}, now)  # held near a line: the soft brake still goes out
        log({**rec, "acted": False})
        return 0
    rc = 0
    ep = state.get("account_end") or {}
    if ep and ep.get("account") != live:
        end_episode(state, d, orders, f"{live} is live now")
    elif ep and d.get("pct_left") is not None and d["pct_left"] > (ep.get("warn_line") or 0) + plan["account_end"]["clear_pct"]:
        end_episode(state, d, orders, f"{live} reads {d['pct_left']}%: it has reset")
    elif ep and lowered(ep, d.get("line")):
        end_episode(state, d, orders, f"{live}'s line was lowered from {ep['line']}% to {d['line']}%")
    if d.get("account_end") and d["do"] == "soft":
        write_notice(d, now)    # first: nothing new starts while the orders go out
        save_step(state, d, plan, burn, runs, orders, now)
    elif d.get("warning"):      # the warning zone: the runs are warned and keep working; nothing is refused
        d["warning_text"] = AE.warn_text(d["account"], d.get("pct_left"), burn, d.get("line"), plan["account_end"],
                                         bool(d.get("last_account")))
        warn_step(state, d, plan, burn, runs, orders, now)
    if d.get("emergency") and (state.get("stopped") or {}).get("account") != live:
        write_notice({**d, "do": "soft", "drain": True, "account_end": True}, now)
        t_e = clock()
        if not emergency_step(state, d, plan, burn, runs, runs_fn, orders, now):
            log({"do": "passive", "why": f"{OUT / 'HOLD'} appeared in the pause"})
            return 0
        now += clock() - t_e
        t_now = clock()
    saved = saved_lines(state, orders) if d["do"] in ("switch", "stop") and state.get("account_end") else None
    t2 = clock()
    brake = {}

    def still():
        """A slow arm can close a window, pass a reset or spend a target: re-read the meter and re-decide at the new
        time (without this pass's own pending marker); the act goes ahead only if the same act is still due."""
        if (OUT / "HOLD").exists():  # the owner's brake, set while we armed
            return False
        mk = {k: v for k, v in read_markers().items() if k != d.get("key")}
        live2 = switcher_status().get("live") or live  # a human may have switched while we armed
        if live2 != live:
            return False
        m2, n2 = meter_fn(), now + clock() - t2
        d2 = decide(m2, live, n2, plan, state, mk, polled=True, manual=manual_switch(last_switch(), mk, live),
                    live_runs=runs, burn=burn)
        d2.update(next_refill(m2, plan, n2))
        same = d2["do"] == d["do"] and d2.get("to") == d.get("to")
        if same and d2.get("under"):  # exhaustion seen on the recheck latches into the marker
            d["under"] = True
        # a brake that became due while we armed is never dropped with the lapsed act: a stop now due, or a spent live
        # account whose switch target changed, stops the fleet now (the next pass switches from the stopped fleet)
        due = d2["do"] == "stop" or (d2["do"] == "switch" and d2.get("under"))
        if d["do"] == "stop" and due:
            d.update(next_refill(m2, plan, n2))
            return True  # live is still spent: the stop holds even if a switch target appeared meanwhile
        if not same and due and d["do"] != "stop" and (state.get("stopped") or {}).get("account") != live:
            brake.update({**d2, "do": "stop", "key": d2["key"] if d2["do"] == "stop" else stop_key(live, m2.get(live) or {}, n2)})
            return ["fleet-stop"]
        return same
    if d["do"] == "switch" and not d.get("under") and (runs is None or runs):
        # a switch made above the line (a priority or reset pull, nothing spent) waits while a detached run is live, so
        # it finishes on its own account and keeps its cache (owner 2026-11-20, "live runs finish past"); at most
        # pull_drain_max_s after the first drain notice. A switch at or under the line waits in decide (drained).
        bound = plan.get("pull_drain_max_s") or 0
        nt = read_json(OUT / "notice.json", {}) or {}
        since = epoch(nt.get("since")) if nt.get("state") == "soft" and nt.get("drain") else None
        if isinstance(bound, (int, float)) and bound > 0 and (since is None or now - since < bound):
            write_notice({**d, "do": "soft", "drain": True,
                          "why": f"the switch to {d['to']} waits while live runs finish: {d.get('why')}"}, now)
            left_s = int(bound - (now - since)) if since is not None else int(bound)
            log({**rec, "do": "drain", "acted": False,
                 "why": f"switch to {d['to']} waits while live runs finish ({runs_why(runs)}), at most {left_s} s more "
                        f"(pull_drain_max_s {bound}); was: {d.get('why')}"})
            return 0
    if d["do"] == "switch":
        write_marker(d["key"], {"phase": "pending", "at": iso(now), "from": live, "to": d["to"], "under": d.get("under"),
                                "line": d.get("line")})
        write_notice({**d, "do": "soft", "drain": True, "account_end": True}, now)  # nothing starts inside the switch
        res = armed_call(st, ["use", d["to"]], still)
        ok = (res.get("use") or (1,))[0] == 0
        lapsed = (res.get("use") or (1,))[0] is None and "lapsed" in str(res.get("use"))
        # `ended`: a switch of this transition in the log after the call returned is his, not this marker's
        write_marker(d["key"], {"phase": "done" if ok else "lapsed" if lapsed else "failed", "at": iso(now), "from": live, "to": d["to"],
                                "under": d.get("under"), "line": d.get("line"), "result": res,
                                "ended": iso(now + clock() - t_now)})
        if ok:
            state.pop("stopped", None)
            save_state(state)
            write_notice({**d, "do": "normal"}, now)
            if saved is not None:
                record_step(state, "switch", f"{live} -> {d['to']}; {facts(d, plan, burn, runs)}; before the switch: "
                            f"{saved}", now + clock() - t2)
                state.pop("account_end", None)
                save_state(state)
        rec["result"], rc = res, 0 if ok else 1
        if not ok and not lapsed and d.get("under") and not d.get("above_line") \
                and (state.get("stopped") or {}).get("account") != live:
            # a failed switch off a spent account never leaves it burning: stop now, retry the switch from the stop
            res2 = armed_call(switcher_status() or st, ["fleet-stop"])
            rec["brake"] = res2
            if (res2.get("fleet-stop") or (1,))[0] == 0:
                brake.update({**d, "do": "stop", "key": stop_key(live, meter.get(live) or {}, now),
                              "why": f"switch {d['key']} failed and {live} is spent: hard stop"})
                res = {**res, "fleet-stop": res2["fleet-stop"]}
        if brake:
            braked = (res.get("fleet-stop") or (1,))[0] == 0
            write_notice(brake, now)
            if braked:
                record_stop(state, brake, now + clock() - t2)
                if saved is not None:
                    record_step(state, "stop in place of the switch", f"{facts(d, plan, burn, runs)}; before the stop: "
                                f"{saved}", now + clock() - t2)
            rc = 0 if braked else 1
    elif d["do"] == "stop":
        write_notice(d, now)
        res = armed_call(st, ["fleet-stop"], still)
        rec["result"], rc = res, 0 if (res.get("fleet-stop") or (1,))[0] == 0 else 1
        if not rc:  # recorded only once the fleet is stopped: a pass that died mid-call retries the stop
            record_stop(state, d, now + clock() - t2)
            if saved is not None:
                record_step(state, "stop, no account has headroom", f"{facts(d, plan, burn, runs)}; before the stop: {saved}",
                            now + clock() - t2)
                state.pop("account_end", None)
                save_state(state)
    elif d["do"] == "start":
        res = armed_call(st, ["fleet-start"], still)
        if (res.get("fleet-start") or (1,))[0] == 0:
            state.pop("stopped", None)
            save_state(state)
            write_notice({**d, "do": "normal"}, now)
        else:
            rc = 1
        rec["result"] = res
    else:
        if d["do"] == "stopped":
            stopped = state.get("stopped") or {}
            stopped.update({k: d[k] for k in ("reset_at", "reset_account") if k in d})
            save_state(state)
            notify_stop(state)
        write_notice(d, now)
    log({**rec, "acted": d["do"] in ("switch", "stop", "start")})
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("check",))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    import account_plan     # the decision and the numbers have one home: the account plan's pass
    return account_plan.tick(dry=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
