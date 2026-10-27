#!/usr/bin/env python3
"""dispatcher.py — RimFlow v3.0, the Dispatcher: a PROGRAM, not an AI (design/RimMandrake/rimflow_v3_2026-10-26.md
§2, §3, §6 item 1; item RIMFLOW_V3_BUILD_DISPATCHER_FIRST). It decides nothing: it follows its schedule file.

Every tick (the rm-dispatcher.timer, every 2 min) it, for each seat in the schedule:
  1. OBSERVES the seat's window: `claude agents --json` (status idle/busy, session id). If that command fails the
     whole tick is UNMEASURED and nothing is done (never act on a blind instrument).
  2. WAKES a stalled window — idle for `stall_after_s`, and its queue has work (`rimflow next --peek` in the seat's
     clone) — by RINGING its doorbell (doorbell.py, an asyncRewake Stop hook): it writes inbox/<SEAT>.json with the
     hand-off message. The message tells the window to run `rimflow next`, which takes the item under a LEASE (the
     2026-10 lease redesign, lease.py: "doing" is a 45 min lease the window renews, never a sticky claim).
  3. VERIFIES: the doorbell moves the inbox file to consumed/ (delivered), then the seat's own ledger shard gains a
     lease take / claim / start after the ring (the hand-off happened). Not consumed in `verify_s` -> withdrawn and
     retried, up to `max_retries`, then an ALARM and a cooldown. Consumed but no hand-off in `handoff_s` -> recorded
     as WOKE_NO_HANDOFF (partial).
  4. RECOVERS a dead window — its session (found by its `--name`, never by cwd) gone from `claude agents` for
     `dead_after_s` — by resuming that session in the background in the seat's clone with the seat launcher's own
     line (`recover_argv`, default `claude_bounded.sh --bg --resume <session> --dangerously-skip-permissions --name …
     --model … --remote-control …`), then checks that SAME session reappears.
  5. RECORDS: every action to state/journal.jsonl; verified hand-offs, give-ups and recoveries as `rimflow note`s by
     seat DISPATCHER (note-only, model.DISPATCHER_VERBS), committed and pushed with the testq RUNNER's publisher
     (ingest.publish, given the DISPATCHER shard).

Never takes the game while the owner plays: it never calls the bridge, `./game` or a deploy itself, and before a ring
it reads idle_probe (the `rimflow bridge idle` rule): a ticket that needs bridge/game-up/deploy is HELD unless the owner
is MEASURED idle >= 20 min (UNMEASURED holds too), and every ring sent while he is not idle carries the line
"owner present: do not take the bridge, restart the game or deploy".

Caps/budgets (schedule "caps"): wakes per seat per hour and per day, wakes per day overall, recoveries per seat per
day, a cooldown after a give-up, and a PAUSE file (state/PAUSE) that stops everything. §3's roles are listed in the
schedule; role_launch.py starts an enabled role that has its launch keys on its clock slots (its own transient
systemd unit, so the run outlives this oneshot tick), gated by its off switch, the ops_watch reading, its throttle
band and its token caps; an enabled role without launch keys is an alarm.

Ledger notes and their publish run under testq's ingest.lock (the RUNNER ingest commits/pulls/pushes in the same
dispatch clone). A side effect that raises never skips the state save (the caps live there); an unreadable state
file stops the tick instead of resetting the caps.

Dry-run is the DEFAULT. Without --apply it rings nobody, recovers nothing, writes no ledger, and keeps its own
bookkeeping under state/dry/ only, so a dry week shows what it would have done.

Reused, not copied: testq's tick.lock flock pattern (testq.cmd_tick), schema.dump/utcnow, ingest.publish (commit +
pull --rebase + ledger lint + push of one shard), idle_probe.measure/decide, lease.py's leases via `rimflow next`.

    dispatcher.py tick [--apply] [--schedule PATH] [--json]
    dispatcher.py status [--schedule PATH]
Names no host or account.
"""
import argparse
import fcntl
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TESTQ = os.path.join(REPO, "src", "RimMandrake", "Utils", "testq")
for _d in (HERE, TESTQ):
    if _d not in sys.path:
        sys.path.insert(0, _d)
import doorbell  # noqa: E402
import role_launch as RL  # noqa: E402
import schema as S  # noqa: E402  (testq: dump, utcnow, parse_ts)

DEFAULT_SCHEDULE = os.path.join(HERE, "dispatcher_schedule.json")
SHARD_REL = os.path.join("infrastructure", "state", "ledger", "events", "DISPATCHER.jsonl")
GAME_NEEDS = ("bridge", "game-up", "deploy")
OPEN_STATES = ("proposed", "ready", "doing", "built", "validated")   # model.OPEN_STATES (selftest pins them equal)
HANDOFF = ("claim", "start")            # plus a lease event with action take

DEFAULTS = {"tick_s": 120, "stall_after_s": 240, "verify_s": 300, "handoff_s": 600, "max_retries": 2,
            "cooldown_s": 3600, "dead_after_s": 600, "recover_verify_s": 300, "owner_idle_s": 20 * 60,
            "ledger_notes": True, "publish": True}
CAP_DEFAULTS = {"wakes_per_seat_hour": 3, "wakes_per_seat_day": 30, "wakes_per_day": 80, "recovers_per_seat_day": 3}
# The seat windows' own launch line (src/RimMandrake/Utils/install_wt_seat_profiles.py LAUNCH: `claude_bounded.sh
# --dangerously-skip-permissions --name '<label>' --model <m> --remote-control '<label>'`, AGENT_SEAT exported, cwd =
# the clone), plus `--bg --resume <id>`. Through claude_bounded.sh, never bare claude: the wrapper puts the session in
# its own memory-capped systemd scope (the 2026-08-14 whole-VM OOM) and so OUT of this oneshot unit's cgroup, which
# systemd kills when the tick exits.
DEFAULT_RECOVER = ["{clone}/src/RimMandrake/Utils/claude_bounded.sh", "--bg", "--resume", "{session_id}",
                   "--dangerously-skip-permissions", "--name", "{name}", "--model", "{model}",
                   "--remote-control", "{name}", "{message}"]


# ---------------------------------------------------------------- schedule and state

def load_schedule(path=None):
    with open(path or DEFAULT_SCHEDULE, encoding="utf-8") as f:
        sch = json.load(f)
    for k, v in DEFAULTS.items():
        sch.setdefault(k, v)
    caps = dict(CAP_DEFAULTS)
    caps.update(sch.get("caps") or {})
    sch["caps"] = caps
    return sch


def state_root(apply):
    root = doorbell.state_dir()
    return root if apply else os.path.join(root, "dry")


class StateUnreadable(Exception):
    pass


def load_state(root):
    p = os.path.join(root, "state.json")
    st = doorbell._read_json(p)
    if st is None:
        if os.path.exists(p):
            # Fail closed: a torn/unreadable state would silently reset every cap and pending ring.
            raise StateUnreadable("%s exists but is unreadable" % p)
        st = {}
    st.setdefault("seats", {})
    st.setdefault("wakes", [])          # [{seat, at}] for the caps
    st.setdefault("recovers", [])
    st.setdefault("alarms", {})         # kind -> last epoch (rate limit)
    return st


def journal(root, rec):
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "journal.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


# ---------------------------------------------------------------- observation (tests replace these)

def claude_exe():
    return os.environ.get("RM_DISPATCHER_CLAUDE") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")


def observe_agents(timeout=60):
    """-> {"state": MEASURED, "sessions": [...]} or {"state": UNMEASURED, "why": ...}."""
    try:
        r = subprocess.run([claude_exe(), "agents", "--json"], capture_output=True, text=True, timeout=timeout,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            return {"state": "UNMEASURED", "why": "claude agents exit %d: %s" % (r.returncode, r.stderr.strip()[-160:])}
        data = json.loads(r.stdout)
        if not isinstance(data, list):
            return {"state": "UNMEASURED", "why": "claude agents --json is not a list"}
        return {"state": "MEASURED", "sessions": data}
    except Exception as e:  # noqa: BLE001 - every failure is UNMEASURED
        return {"state": "UNMEASURED", "why": "%s: %s" % (type(e).__name__, str(e)[:160])}


def peek_ticket(clone, seat, timeout=120):
    """-> {"id", "needs"} of the seat's next item per `rimflow next --peek` in its clone, {} when its queue is empty,
    None when unreadable."""
    cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
    try:
        r = subprocess.run([sys.executable, cli, "next", "--seat", seat, "--peek"], cwd=clone, capture_output=True,
                           text=True, timeout=timeout, env=dict(os.environ, RIMFLOW_SEAT=seat),
                           stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return None
    if r.returncode:
        return None
    return parse_peek(r.stdout)


def parse_peek(out):
    """The first item line of `rimflow next --peek`: `<ID>   <state>  row …  needs <x>  target …`. Pure (tested)."""
    for line in (out or "").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isupper() and "_" in parts[0] and not parts[0].endswith(":") \
                and parts[1] in OPEN_STATES:
            needs = None
            if "needs" in parts:
                i = parts.index("needs")
                needs = parts[i + 1] if i + 1 < len(parts) else None
            return {"id": parts[0], "needs": needs if needs not in ("-", None) else None}
    return {}


def seat_events_since(clone, seat, since_iso):
    """Events the seat wrote to its own shard (on disk in its clone, before any push) at or after since_iso."""
    p = os.path.join(clone, "infrastructure", "state", "ledger", "events", "%s.jsonl" % seat)
    out = []
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("seat") == seat and (ev.get("ts") or "") > since_iso:   # strictly after the ring's second
                    out.append(ev)
    except OSError:
        pass
    return out


def consumed_ring(root, seat, ring_id):
    for p in glob.glob(os.path.join(root, "consumed", "%s-*.json" % seat)):
        rec = doorbell._read_json(p) or {}
        if rec.get("ring_id") == ring_id:
            return rec
    return None


def owner_reading():
    import idle_probe
    return idle_probe.measure()


def pid_alive(pid):
    return bool(pid) and doorbell._alive(int(pid))


# ---------------------------------------------------------------- the core

def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def find_session(sessions, cfg):
    """The seat's window BY NAME only. Every seat is launched with `--name 'AGENT <SEAT>'`
    (install_wt_seat_profiles.py: the name is what makes a seat addressable). No cwd fallback: an owner window, a
    remote-control session or HESTIA/EMERGENCY can sit in a seat's clone, and adopting one would remember ITS session
    id for a `--dangerously-skip-permissions` resume."""
    name = cfg.get("session_name")
    for s in sessions:
        if name and s.get("name") == name:
            return s
    return None


def handoff_seen(events):
    for ev in events:
        if ev.get("event") in HANDOFF or (ev.get("event") == "lease" and ev.get("action") == "take"):
            return ev
    return None


def caps_ok(st, sch, seat, now):
    c = sch["caps"]
    mine = [w for w in st["wakes"] if w["seat"] == seat]
    if sum(1 for w in mine if now - w["at"] < 3600) >= c["wakes_per_seat_hour"]:
        return False, "cap: %d wakes/hour for %s" % (c["wakes_per_seat_hour"], seat)
    if sum(1 for w in mine if now - w["at"] < 86400) >= c["wakes_per_seat_day"]:
        return False, "cap: %d wakes/day for %s" % (c["wakes_per_seat_day"], seat)
    if sum(1 for w in st["wakes"] if now - w["at"] < 86400) >= c["wakes_per_day"]:
        return False, "cap: %d wakes/day overall" % c["wakes_per_day"]
    return True, ""


def message(seat, cfg, ticket, owner_line, ring_id):
    lines = ["[RimFlow Dispatcher — a program, not a person; ring %s]" % ring_id,
             "Seat %s: you are idle and your queue has work. Run `python3 src/RimMandrake/rimflow/cli.py next "
             "--seat %s --ringed`, which gives you the item under a lease, and work it; renew the lease every 10 min "
             "(`rimflow renew`). The peeked next item is %s." % (seat, seat, ticket.get("id")),
             "If you are mid-task, finish it first; if the queue is wrong, say so on the item with `rimflow note`."]
    if owner_line:
        lines.append(owner_line)
    if cfg.get("extra"):
        lines.append(cfg["extra"])
    return "\n".join(lines)


def decide(sch, st, obs, now, apply):
    """-> actions. Mutates st (the seat bookkeeping). Pure except for the lazy calls in obs (owner(), peek(seat),
    events(seat, since), consumed(seat, ring_id), armed(seat), alive(pid)) so a selftest can drive every path."""
    actions = []

    def act(**kw):
        kw.setdefault("at", iso(now))
        actions.append(kw)

    # Runs already launched are supervised FIRST, whatever ends this tick early (PAUSE, a blind `claude agents`, a
    # disabled role): a launched role stays tracked and time-limited no matter what (review round Q 1).
    role_busy = RL.supervise_roles(sch, st, obs["roles"], now, act) if obs.get("roles") else None
    if obs.get("paused"):
        act(do="skip", why="PAUSE file present: %s" % obs["paused"])
        for seat, ss in sorted(st["seats"].items()):     # a ring already in an inbox would still wake its window
            if ss.get("ring") and not ss["ring"].get("consumed_at"):
                act(do="withdraw", seat=seat, ring_id=ss["ring"]["ring_id"], pending=ss.pop("ring"))
        return actions
    agents = obs["agents"]
    if agents.get("state") != "MEASURED":
        act(do="skip", why="claude agents UNMEASURED (%s): no action on a blind instrument" % agents.get("why"))
        return actions
    if obs.get("roles"):          # role_launch.py: enabled roles with launch keys run on their clock; others alarm
        RL.decide_roles(sch, st, obs["roles"], now, act, busy=role_busy)
    else:
        for role in sch.get("roles") or []:
            if role.get("enabled"):
                act(do="alarm", kind="role:" + role.get("name", "?"),
                    why="role %s is enabled but this tick has no role observer" % role.get("name"))
    owner_cache = {}

    def owner():
        if "r" not in owner_cache:
            owner_cache["r"] = obs["owner"]()
        return owner_cache["r"]

    for seat, cfg in sorted((sch.get("seats") or {}).items()):
        if not cfg.get("enabled", True):
            continue
        ss = st["seats"].setdefault(seat, {})
        sess = find_session(agents["sessions"], cfg)
        status = (sess or {}).get("status") or (sess or {}).get("state")
        pend = ss.get("ring")
        # ---- a ring in flight: verify it
        if pend:
            if status != "idle":
                ss.pop("idle_since", None)       # busy time is not stall time
            rec = obs["consumed"](seat, pend["ring_id"])
            if rec and not pend.get("consumed_at"):
                pend["consumed_at"] = rec.get("consumed_at") or now
            if pend.get("consumed_at"):
                ev = handoff_seen(obs["events"](seat, pend["rung_iso"]))
                if ev:
                    act(do="verified", seat=seat, ring_id=pend["ring_id"], ticket=ev.get("id") or pend.get("ticket"),
                        evidence="%s %s at %s" % (ev.get("event"), ev.get("action") or "", ev.get("ts")),
                        note=True)
                    ss.pop("ring")
                    ss["attempt"] = 0
                    ss["last_verified"] = now
                elif now - pend["rung_at"] >= sch["handoff_s"]:
                    act(do="woke_no_handoff", seat=seat, ring_id=pend["ring_id"], ticket=pend.get("ticket"),
                        why="doorbell consumed but no lease/claim/start by %s in %d s" % (seat, sch["handoff_s"]),
                        note=True)
                    ss.pop("ring")
                    ss["attempt"] = 0
                    ss["cooldown_until"] = now + sch["cooldown_s"]
                continue
            if now - pend["rung_at"] >= sch["verify_s"]:
                act(do="withdraw", seat=seat, ring_id=pend["ring_id"], pending=dict(pend))
                ss.pop("ring")
                if pend["attempt"] >= sch["max_retries"] + 1:
                    act(do="alarm", kind="undelivered:" + seat, seat=seat, ticket=pend.get("ticket"), note=True,
                        why="%d rings to %s never consumed: its doorbell is not running" % (pend["attempt"], seat))
                    ss["cooldown_until"] = now + sch["cooldown_s"]
                    ss["attempt"] = 0
                else:
                    ss["attempt"] = pend["attempt"]
            continue
        # ---- recovery in flight: verify it
        rv = ss.get("recover")
        if rv:
            if sess and (not rv.get("session_id") or sess.get("sessionId") == rv["session_id"]):
                act(do="recovered", seat=seat, session=sess.get("sessionId"), note=True,
                    why="session back after recover at %s" % iso(rv["at"]))
                ss.pop("recover")
                ss.pop("dead_since", None)
            elif now - rv["at"] >= sch["recover_verify_s"]:
                act(do="alarm", kind="recover:" + seat, seat=seat, note=True,
                    why="recover of %s did not bring a session back in %d s: %s" % (seat, sch["recover_verify_s"],
                                                                                    rv.get("out", "")[:160]))
                ss.pop("recover")
                ss["cooldown_until"] = now + sch["cooldown_s"]
            continue
        if ss.get("cooldown_until", 0) > now:
            continue
        # ---- dead window
        if not sess:
            ss.pop("idle_since", None)
            ss.setdefault("dead_since", now)
            if now - ss["dead_since"] < sch["dead_after_s"]:
                continue
            if not cfg.get("recover_dead"):
                act(do="alarm", kind="dead:" + seat, seat=seat, why="%s has had no session for %d s (recovery off)"
                    % (seat, now - ss["dead_since"]))
                continue
            if not ss.get("session_id"):
                act(do="alarm", kind="dead:" + seat, seat=seat, why="%s is dead and no session id was ever seen" % seat)
                continue
            day = [r for r in st["recovers"] if r["seat"] == seat and now - r["at"] < 86400]
            if len(day) >= sch["caps"]["recovers_per_seat_day"]:
                act(do="alarm", kind="cap:recover:" + seat, seat=seat,
                    why="cap: %d recovers/day for %s" % (sch["caps"]["recovers_per_seat_day"], seat))
                continue
            import idle_probe
            owner_ok, owner_why = idle_probe.decide(owner(), "", need=sch["owner_idle_s"])
            msg = ("[RimFlow Dispatcher] Your window was found dead and resumed in the background. Run "
                   "`python3 src/RimMandrake/rimflow/cli.py next --seat %s` and continue." % seat)
            if not owner_ok:     # the resumed session may have died mid bridge/deploy work: tell it not to resume that
                msg += "\nowner present: do not take the bridge, restart the game or deploy (%s)." % owner_why
            act(do="recover", seat=seat, session_id=ss["session_id"], message=msg)
            st["recovers"].append({"seat": seat, "at": now})
            if apply:
                ss["recover"] = {"at": now, "session_id": ss["session_id"]}
            else:
                ss["cooldown_until"] = now + sch["cooldown_s"]   # dry: say it once per cooldown, not every tick
            continue
        ss.pop("dead_since", None)
        ss["session_id"] = sess.get("sessionId") or ss.get("session_id")
        if status != "idle":
            ss.pop("idle_since", None)
            continue
        ss.setdefault("idle_since", now)
        if now - ss["idle_since"] < sch["stall_after_s"] or not cfg.get("wake", True):
            continue
        # ---- stalled: can it be woken, is there work, may it be woken now
        armed = obs["armed"](seat)
        if not armed or not obs["alive"](armed.get("pid")):
            act(do="alarm", kind="unwakeable:" + seat, seat=seat,
                why="%s is idle but no doorbell is armed (install doorbell.py as its Stop hook)" % seat)
            continue
        if armed.get("session_id") and sess.get("sessionId") and armed["session_id"] != sess["sessionId"]:
            act(do="alarm", kind="unwakeable:" + seat, seat=seat,
                why="%s's armed doorbell is session %s, not the window's %s (a `claude -p` child or second window "
                    "with AGENT_SEAT re-armed it): not ringing a stranger" % (seat, armed["session_id"],
                                                                               sess["sessionId"]))
            continue
        ticket = obs["peek"](seat)
        if ticket is None:
            act(do="alarm", kind="peek:" + seat, seat=seat, why="rimflow next --peek failed in %s" % cfg.get("clone"))
            continue
        if not ticket:
            continue                     # empty queue: an idle window is correct
        ok, why = caps_ok(st, sch, seat, now)
        if not ok:
            act(do="alarm", kind="cap:" + seat, seat=seat, why=why)
            continue
        import idle_probe
        owner_ok, owner_why = idle_probe.decide(owner(), ticket.get("id") or "", need=sch["owner_idle_s"])
        if ticket.get("needs") in GAME_NEEDS and not owner_ok:
            act(do="hold", seat=seat, ticket=ticket["id"], why="ticket needs %s; %s" % (ticket["needs"], owner_why))
            continue
        owner_line = None if owner_ok else (
            "owner present: do not take the bridge, restart the game or deploy (%s)." % owner_why)
        attempt = ss.get("attempt", 0) + 1
        ring_id = "%s-%d-%d" % (seat, int(now), attempt)
        act(do="ring", seat=seat, ring_id=ring_id, ticket=ticket["id"], attempt=attempt,
            session_id=sess.get("sessionId"), message=message(seat, cfg, ticket, owner_line, ring_id))
        st["wakes"].append({"seat": seat, "at": now})
        if apply:
            ss["ring"] = {"ring_id": ring_id, "rung_at": now, "rung_iso": iso(now), "ticket": ticket["id"],
                          "attempt": attempt}
        ss["idle_since"] = now           # the next wake waits a full stall window again
    # prune the cap windows
    st["wakes"] = [w for w in st["wakes"] if now - w["at"] < 86400]
    st["recovers"] = [r for r in st["recovers"] if now - r["at"] < 86400]
    return actions


# ---------------------------------------------------------------- side effects

def ring(root, seat, ring_id, msg, session_id=None):
    doorbell._write_json_atomic(doorbell.inbox_path(seat, root),
                                {"seat": seat, "ring_id": ring_id, "message": msg, "rung_at": time.time(),
                                 "session_id": session_id})


def withdraw(root, seat, ring_id):
    src = doorbell.inbox_path(seat, root)
    rec = doorbell._read_json(src) or {}
    if rec.get("ring_id") != ring_id:
        return "not ours / gone"
    dst = os.path.join(root, "withdrawn")
    os.makedirs(dst, exist_ok=True)
    try:
        os.rename(src, os.path.join(dst, "%s.json" % ring_id))
        return "withdrawn"
    except OSError:
        return "gone (the doorbell took it)"


def recover(cfg, session_id, msg, runner=subprocess.run):
    argv = [a.format(claude=claude_exe(), clone=cfg["clone"], session_id=session_id, name=cfg.get("session_name") or "",
                     model=cfg.get("model") or "sonnet", message=msg) for a in (cfg.get("recover_argv") or DEFAULT_RECOVER)]
    env = claude_env(cfg["seat"])
    try:
        r = runner(argv, cwd=cfg["clone"], env=env, capture_output=True, text=True, timeout=120,
                   stdin=subprocess.DEVNULL)
        return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()[-200:]
    except Exception as e:  # noqa: BLE001
        return False, "%s: %s" % (type(e).__name__, str(e)[:160])


def claude_env(seat):
    """The seat env for claude_bounded.sh, with claude's own directory on PATH: the systemd user manager's PATH (the
    timer's) has no ~/.local/bin, and claude_bounded exits 127 without it (proved 2026-10-27, role_launch proof)."""
    env = dict(os.environ, AGENT_SEAT=seat, RIMFLOW_SEAT=seat)
    d = os.path.dirname(claude_exe())
    if d and d not in env.get("PATH", "").split(":"):
        env["PATH"] = d + ":" + env.get("PATH", "/usr/bin:/bin")
    return env


def ledger_note(item, text, run=subprocess.run):
    cli = os.path.join(HERE, "cli.py")
    env = dict(os.environ, RIMFLOW_SEAT="DISPATCHER", CLAUDE_PROJECT_DIR=REPO)
    r = run([sys.executable, cli, "note", item, "--text", text, "--seat", "DISPATCHER"], cwd=REPO, env=env,
            capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()[-200:]


def publish(n):
    import ingest
    if not n and not ingest.unpublished(SHARD_REL):
        return None
    return ingest.publish(n, shard_rel=SHARD_REL, message="ledger: DISPATCHER notes (%d)" % n)


def git_lock(wait_s=90):
    """testq's ingest.lock: the RUNNER ingest commits, pull --rebases and pushes in this same dispatch clone. Our note
    appends (an unstaged DISPATCHER.jsonl) and our publish must not interleave with its pull --rebase, or each makes
    the other's rebase refuse. -> an open locked file, or None when it stayed busy for wait_s."""
    import testq
    testq.ensure_dirs()
    lk = open(testq.q("ingest.lock"), "w")
    end = time.time() + wait_s
    while True:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lk
        except BlockingIOError:
            if time.time() >= end:
                lk.close()
                return None
            time.sleep(2)


def execute(actions, sch, st, root, apply, now, fx=None):
    """Carry the actions out (apply) or only journal them (dry). fx overrides the side effects (selftests)."""
    fx = fx or {}
    do_ring, do_withdraw = fx.get("ring", ring), fx.get("withdraw", withdraw)
    do_recover, do_note, do_publish = fx.get("recover", recover), fx.get("note", ledger_note), fx.get("publish", publish)
    do_lock = fx.get("lock", git_lock)
    do_launch, do_stop = fx.get("role_launch", RL.launch), fx.get("role_stop", RL.stop)
    do_off, do_paused = fx.get("off", RL.off_switch), fx.get("paused", paused_now)
    wants_ledger = apply and sch.get("ledger_notes") and any(a.get("note") for a in actions)
    lk = do_lock() if (wants_ledger or (apply and sch.get("publish"))) else None
    ledger_ok = lk is not None
    notes = 0
    try:
        for a in actions:
            res = None
            if a["do"] == "alarm":
                last = st["alarms"].get(a["kind"])
                if last is not None and now - last < sch.get("alarm_every_s", 6 * 3600):
                    a["note"] = False
                    res = "repeat alarm (rate-limited)"
                else:
                    st["alarms"][a["kind"]] = now
            if apply:
                try:     # one failing side effect must not skip the rest, nor the state save that holds the caps
                    if a["do"] == "ring":
                        do_ring(root, a["seat"], a["ring_id"], a["message"], a.get("session_id"))
                        res = "rung"
                    elif a["do"] == "withdraw":
                        res = do_withdraw(root, a["seat"], a["ring_id"])
                        if res.startswith("gone") and a.get("pending"):
                            # the doorbell consumed it between decide and here: it WAS delivered — keep verifying it
                            # instead of ringing a second time
                            ss = st["seats"].setdefault(a["seat"], {})
                            ss["ring"] = dict(a["pending"], consumed_at=now)
                    elif a["do"] == "recover":
                        cfg = dict(sch["seats"][a["seat"]], seat=a["seat"])
                        ok, out = do_recover(cfg, a["session_id"], a["message"])
                        res = ("started: " if ok else "failed: ") + out
                        st["seats"][a["seat"]].setdefault("recover", {"at": now})["out"] = out
                    elif a["do"] == "role_launch":
                        role = next(r for r in sch["roles"] if r.get("name") == a["role"])
                        # the off switch and PAUSE again, now: decide() read them before the ingest.lock wait
                        off = do_off(RL.wsl_path(role.get("off_file") or ""))
                        paused = do_paused()
                        if off is not None or paused or not role.get("enabled"):
                            res = "held at launch: %s" % (
                                ("PAUSE (%s)" % paused) if paused else ("off switch %s (%s)" % (
                                    role.get("off_file"), off or "no reason given")) if off is not None
                                else "role no longer enabled")
                            a["why"] = "%s — NOT LAUNCHED, %s" % (a["why"], res)
                        else:
                            # the run is recorded BEFORE systemd-run: a raise after the unit started (a timeout, a
                            # failed MainPID query) must not leave a launched role untracked (review round Q 4)
                            out_p, err_p = RL.run_paths(root, a["unit"])
                            runs = st.setdefault("roles", {}).setdefault(a["role"], {}).setdefault("runs", [])
                            run = dict(out=out_p, err=err_p, scope=None, unit=a["unit"], at=now, day=RL.day_of(now),
                                       mode=a["mode"], budget=a["budget"], slot=a["slot"], band=a["band"],
                                       item=a["ticket"], seat=a.get("seat") or role.get("seat"),
                                       run_max_s=a.get("run_max_s"), state="running", tokens=None)
                            runs.append(run)
                            ok, out, rec = do_launch(role, a["unit"], a["message"], root, claude_exe())
                            res = ("launched: " if ok else "failed: ") + out
                            if ok:
                                run.update(rec or {})
                            else:
                                runs.remove(run)            # systemd-run said no: nothing started
                                a["why"] = "%s — LAUNCH FAILED: %s" % (a["why"], out)
                    elif a["do"] == "role_stop":
                        res = do_stop(a["unit"], a.get("scope"), seat=a.get("seat"))
                except Exception as e:  # noqa: BLE001
                    res = "error: %s: %s" % (type(e).__name__, str(e)[:160])
                if a.get("note") and sch.get("ledger_notes"):
                    item = a.get("ticket") or sch.get("alarm_item")
                    if item and not ledger_ok:
                        a["ledger"] = "not noted: testq ingest.lock busy (the journal holds it)"
                    elif item:
                        try:
                            ok, out = do_note(item, "dispatcher %s %s: %s" % (
                                a["do"], a.get("seat") or a.get("role") or "",
                                a.get("evidence") or a.get("why") or a.get("ring_id") or ""))
                        except Exception as e:  # noqa: BLE001 - a rimflow timeout
                            ok, out = False, "%s: %s" % (type(e).__name__, str(e)[:160])
                        notes += ok
                        a["ledger"] = "noted" if ok else "note failed: " + out
            a["result"] = res if apply else ("DRY: " + (res or "would %s" % a["do"]))
            journal(root, dict(a, message=None, pending=None) if a.get("message") or a.get("pending") else a)
        if apply and ledger_ok and sch.get("publish"):
            try:
                out = do_publish(notes)       # also retries an earlier publish that stopped (ingest.unpublished)
            except Exception as e:  # noqa: BLE001
                out = "error: %s: %s" % (type(e).__name__, str(e)[:160])
            if out is not None:
                journal(root, {"at": iso(now), "do": "publish", "result": out})
    finally:
        if lk is not None:
            lk.close()
    return actions


def paused_now():
    """The PAUSE file's reason ('paused' when empty), or None."""
    p = os.path.join(doorbell.state_dir(), "PAUSE")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read().strip() or "paused"
    except OSError:
        return "paused (PAUSE unreadable)"


def default_obs(sch, root):
    seats = sch.get("seats") or {}
    return {
        "paused": paused_now(),
        "agents": observe_agents(),
        "owner": owner_reading,
        "peek": lambda seat: peek_ticket(seats[seat]["clone"], seat),
        "events": lambda seat, since: seat_events_since(seats[seat]["clone"], seat, since),
        "consumed": lambda seat, rid: consumed_ring(doorbell.state_dir(), seat, rid),
        "armed": lambda seat: doorbell._read_json(doorbell.armed_path(seat)),
        "alive": pid_alive,
        "roles": {
            "ops": lambda: RL.read_ops(RL.ops_status_path(sch)),
            "account": RL.resolve_account,
            "unit_state": RL.unit_state,
            "result": RL.read_result,
            "off": RL.off_switch,
        },
    }


def tick(sch, apply, obs=None, now=None, fx=None):
    root = state_root(apply)
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "tick.lock"), "w") as lk:        # testq.cmd_tick's pattern
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return [{"do": "skip", "why": "a tick is already running"}]
        now = time.time() if now is None else now
        try:
            st = load_state(root)
        except StateUnreadable as e:
            rec = {"at": iso(now), "do": "skip", "why": "state UNREADABLE, no action (fix or remove it): %s" % e}
            journal(root, rec)
            return [rec]
        acts = []
        st.setdefault("last_ok_tick", None)   # present (null) from the first tick: the dead-man reads it, never last_tick
        try:
            o = obs or default_obs(sch, root)
            acts = decide(sch, st, o, now, apply)
            execute(acts, sch, st, root, apply, now, fx)
            # a tick that WORKED: no raise, and not blind (PAUSE is the owner's choice, a working tick) — review Q 11
            if o.get("paused") or (o.get("agents") or {}).get("state") == "MEASURED":
                st["last_ok_tick"] = iso(now)
        finally:     # the caps and pending rings are in st: save them even when a step raised
            st["last_tick"] = iso(now)        # last ATTEMPT
            st["apply"] = apply
            S.dump(st, os.path.join(root, "state.json"))
    return acts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--apply", action="store_true", help="really ring/recover/record (default: dry-run)")
    t.add_argument("--schedule")
    t.add_argument("--json", action="store_true")
    s = sub.add_parser("status")
    s.add_argument("--schedule")
    s.add_argument("--apply", action="store_true", help="show the live state instead of the dry one")
    a = ap.parse_args(argv)
    sch = load_schedule(a.schedule)
    if a.cmd == "status":
        print(json.dumps(load_state(state_root(a.apply)), indent=1, sort_keys=True))
        return 0
    acts = tick(sch, a.apply)
    for x in acts:
        if a.json:
            print(json.dumps(dict(x, message=None) if x.get("message") else x, sort_keys=True))
        else:
            print("%s %-16s %-10s %s" % (x.get("at", ""), x["do"], x.get("seat", ""),
                                         x.get("result") or x.get("why") or x.get("ticket") or ""))
    if not acts:
        print("%s nothing to do (%s)" % (iso(time.time()), "apply" if a.apply else "dry-run"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
