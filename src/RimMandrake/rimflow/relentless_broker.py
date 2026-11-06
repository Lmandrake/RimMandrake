#!/usr/bin/env python3
"""The game broker: built items queue their live proof lines and hold no lane; one job runs the queue when the game is idle.

LIVELANE_BUILD_GAME_BROKER_PROOF_LINES (redesign 2026-11-06, WP-11). Before it, every built item in the game lane walked
to its own prove round (relentless_game.step, phase prove -> GameFx.prove_launch), one item per round, each waiting its
turn while holding its place in the lane. Now an item whose proof lines are ready OFFERS them here and is put down:
it holds nothing. drain() (each tick after the item loop, and at the end of game_pass) launches one job for a batch
of queued items when the game is idle: no other live user (relentless_game.busy), no expedited item outside the queue,
no live round running, the game UP on the game the lines were queued for, and the bridge idle (an OWNER hold is never
overridden: `rimflow bridge idle` refuses it, and each round's relentless_live.run takes the bridge with --idle-ok).

The job runs `relentless_live_round.py round --item X` for each batch item in turn, exactly the round the item would
have launched itself, and marks the entry ran. The batch items sit in phase "proving" (relentless_game.ACTIVE) while it
runs, so every existing one-live-user check still holds. On the item's next step its turn is over and it reads its rows
as before.

Store (all under store/broker/):
  queue.json  {"items": {item: {sha, clauses, game, queued_at, state, batch, ran_at, why}}}
              state: queued | running | ran | skipped | lost | stale | dropped
  log.jsonl   one row per clause a round ran: the SLIs (clauses completed per day) read it
  fault.json  the last fault and the code fingerprint it happened on
The job reuses relentless_jobs (kind "broker", NOT in relentless_jobs.KINDS: it is launched by GameFx.broker_launch,
never by the systemd unit or the prelude's reconcile). Liveness is the job lock's flock: a table that says running
while nobody holds the lock is an abandoned job, its running entries are marked lost and their items walk on.

Faults fall back to the lane as it was: any exception in offer/drain/settle writes fault.json and journals an alarm;
while the fault's code_fp is this file's, active() is False and every item launches its own prove round again. A fix
that lands changes the fingerprint and the broker comes back on its own. relentless_broker.json "enabled": false is the
off switch.
"""
import argparse
import collections
import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "relentless_broker.json")
KIND = "broker"
LAUNCH_GRACE_S = 120    # a launched job that has not taken its lock by then never started
OVER = ("ran", "skipped", "lost", "stale", "dropped")
VERDICTS = ("PASS", "FAIL")


def cfg():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            got = json.load(f)
    except (OSError, ValueError):
        got = {}
    got = got if isinstance(got, dict) else {}
    return {"enabled": bool(got.get("enabled")), "batch_max": int(got.get("batch_max") or 6),
            "round_timeout_s": int(got.get("round_timeout_s") or 5400)}


def code_fp():
    try:
        with open(os.path.abspath(__file__), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        return None


def _dir(store):
    d = store.p("broker")
    os.makedirs(d, exist_ok=True)
    return d


def _read(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, type(default)) else default
    except (OSError, ValueError):
        return default


def _write(path, obj):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


@contextlib.contextmanager
def _qlock(store):
    fd = os.open(os.path.join(_dir(store), "queue.lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def load(store):
    q = _read(os.path.join(_dir(store), "queue.json"), {})
    q.setdefault("items", {})
    return q


def _save_q(store, q):
    _write(os.path.join(_dir(store), "queue.json"), q)


def entry(store, item):
    return load(store)["items"].get(item)


def _update(store, fn):
    with _qlock(store):
        q = load(store)
        out = fn(q)
        _save_q(store, q)
        return out


# ---------------------------------------------------------------- faults: fall back to the lane as it was

def fault(store, where, exc):
    """Record a broker fault. Never raises: a fault in the fault path still leaves the caller on the old lane."""
    rec = {"at": time.time(), "where": where, "why": ("%s: %s" % (type(exc).__name__, exc))[:400], "code_fp": code_fp()}
    try:
        _write(os.path.join(_dir(store), "fault.json"), rec)
        store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "do": "alarm", "kind": "broker_fault",
                       "where": where, "why": rec["why"]})
    except Exception:  # noqa: BLE001  the fallback is the caller's; the record is best effort
        pass
    return rec


def faulted(store):
    """The fault that holds the broker off, or None. Only a fault on this very code: a fix that lands clears it."""
    f = _read(os.path.join(_dir(store), "fault.json"), {})
    return f if f and f.get("code_fp") == code_fp() else None


def active(store, fx):
    """The broker runs only with a launcher (GameFx.broker_launch: the live supervisor), enabled, and not faulted."""
    if not callable(getattr(fx, "broker_launch", None)) or not cfg()["enabled"]:
        return False
    try:
        return faulted(store) is None
    except Exception:  # noqa: BLE001  unreadable store: the old lane
        return False


# ---------------------------------------------------------------- the job's liveness (relentless_jobs table + flock)

def _jobs():
    import relentless_jobs
    return relentless_jobs


def job_alive(store, now=None):
    j = _jobs()
    if j.running(store, KIND):
        return True
    t = j.table(store, KIND)
    now = time.time() if now is None else now
    return t.get("state") == "queued" and now - float(t.get("launched") or 0) < LAUNCH_GRACE_S


def busy(store):
    """-> "game broker round" while its job runs, else None (relentless_game.busy and the auto live round ask)."""
    try:
        return "game broker round" if os.path.isdir(store.p("jobs")) and _jobs().running(store, KIND) else None
    except Exception:  # noqa: BLE001  a probe that cannot look says nothing
        return None


def reconcile(store, now, acts):
    """An abandoned job (killed, crashed, never started): its table says running/queued and nobody holds the lock. The
    table is marked lost and every running entry with it, so its items walk on. Idempotent."""
    if job_alive(store, now):
        return []
    j = _jobs()

    def mark(q):
        lost = []
        for item, e in sorted(q["items"].items()):
            if e.get("state") == "running":
                e.update(state="lost", why="the broker job ended without running it (killed or crashed)", ended=now)
                lost.append(item)
        return lost
    with j._table(store, KIND):     # the liveness is re-read under the table lock and held while the entries are marked
        if j.running(store, KIND):
            return []       # a job started between the first look and this one: its batch is its own
        if os.path.isfile(j._path(store, KIND, ".json")):
            t = j.table(store, KIND)
            if t.get("state") in ("running", "queued"):
                t["state"] = "lost"
                t["lost"] = int(t.get("lost") or 0) + 1
                j._write(j._path(store, KIND, ".json"), t)
        lost = _update(store, mark)
    if lost:
        acts.append({"do": "broker_lost", "items": lost})
    return lost


# ---------------------------------------------------------------- what relentless_game.step calls

def offer(store, item, sha, clauses, game, now):
    """Queue an item's live proof lines. -> the entry's queued_at (the item keeps it in game.broker)."""
    def put(q):
        q["items"][item] = {"sha": sha, "clauses": list(clauses or []), "game": game, "queued_at": now,
                            "state": "queued"}
        return now
    return _update(store, put)


def waiting(store, item, g):
    """True while the item's offer still waits in the queue (it holds nothing meanwhile)."""
    b = g.get("broker") or {}
    e = entry(store, item)
    return bool(e) and e.get("state") == "queued" and e.get("queued_at") == b.get("queued_at") and not b.get("batch")


def over(store, item, g, now):
    """True when the item's broker turn has ended (ran, skipped, lost, stale, dropped, or its job is gone)."""
    b = g.get("broker") or {}
    e = entry(store, item)
    if not e or not b.get("batch") or e.get("batch") != b.get("batch") or e.get("state") in OVER:
        return True
    return e.get("state") == "running" and not job_alive(store, now)


def forget(store, item):
    _update(store, lambda q: q["items"].pop(item, None))


# ---------------------------------------------------------------- drain: run the queue when the game is idle

def round_running(store):
    path = os.path.join(store.root, "live", "round.lock")
    if not os.path.exists(path):
        return False
    fd = os.open(path, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    finally:
        os.close(fd)
    return False


def idle_why(store, fx, rd, queued):
    """-> None when the game is idle for the broker, else what holds it."""
    import relentless_game as G
    other = G.busy(store, None)
    if other:
        return "busy: %s" % other
    exp = G.expedited_ahead(store.states(), None)
    if exp and exp not in queued:
        return "expedited %s goes first" % exp
    if round_running(store):
        return "a live round is running"
    if rd.get("state") != "UP" or not rd.get("started"):
        return "game %s" % (rd.get("state") or "unread")
    return fx.bridge_idle("relentless game broker")


def _rank(s):
    import relentless_expedite
    e = (s or {}).get("expedite")
    return (0, relentless_expedite.rank(e)) if e else (1,)


def drain(store, fx, r, now, acts):
    """-> what it did ("off" | "running" | "empty" | "held: why" | "launched <batch>")."""
    if not active(store, fx):
        return "off"
    import relentless_game as G
    reconcile(store, now, acts)
    if job_alive(store, now):
        return "running"
    q = load(store)
    queued = {i: e for i, e in q["items"].items() if e.get("state") == "queued"}
    if not queued:
        return "empty"
    states = {s["item"]: s for s in store.states()}
    rd = fx.game_reading()
    gone = {}
    for item, e in queued.items():
        s = states.get(item) or {}
        g = s.get("game") or {}
        if s.get("status") != G.GAME or g.get("phase") != "prove" or (g.get("broker") or {}).get("queued_at") != e["queued_at"]:
            gone[item] = "dropped"
        elif rd.get("state") == "UP" and rd.get("started") and e.get("game") != rd["started"]:
            gone[item] = "stale"
    if gone:
        def drop(q):
            for item, how in gone.items():
                if (q["items"].get(item) or {}).get("state") == "queued":
                    q["items"][item].update(state=how, ended=now)
        _update(store, drop)
        acts.append({"do": "broker_dropped", "items": sorted(gone)})
    live = sorted((i for i in queued if i not in gone), key=lambda i: (_rank(states.get(i)), queued[i]["queued_at"], i))
    if not live:
        return "empty"
    why = idle_why(store, fx, rd, live)
    _update(store, lambda q: q.update(held=(why or None), held_at=now))
    if why:
        return "held: %s" % why
    batch = live[:cfg()["batch_max"]]
    bid = "b%d" % int(now * 1000)
    for item in batch:
        G._save(store, item, lambda s, item=item: (s.pop("put_down", None), s["game"].update(
            phase="proving", prove_pid=None, proved_at=now, waits_reload=None,
            broker=dict(s["game"].get("broker") or {}, batch=bid))))
        G.session_note(store, rd.get("started"), item, served=True, mods=rd.get("mods"), now=now)

    def run_them(q):
        for item in batch:
            q["items"][item].update(state="running", batch=bid, launched_at=now)
    _update(store, run_them)
    launch_why = _jobs().request(store, KIND, {"batch": bid, "items": batch, "root": store.root},
                                 lambda kind: fx.broker_launch())
    if launch_why:      # never started: the entries are lost at once and their items walk on
        def lose(q):
            for item in batch:
                q["items"][item].update(state="lost", why=("launch: %s" % launch_why)[:200], ended=now)
        _update(store, lose)
        acts.append({"do": "broker_launch_failed", "batch": bid, "why": str(launch_why)[:200]})
        return "launch failed: %s" % launch_why
    acts.append({"do": "broker_round", "batch": bid, "items": batch})
    return "launched %s" % bid


# ---------------------------------------------------------------- the job

def _bridge_why(root):
    """`rimflow bridge idle` as the supervisor asks it (relentless.Fx.rimflow): None, or who holds it (OWNER included)."""
    import relentless
    with open(os.environ.get("RELENTLESS_RULES") or relentless.RULES, encoding="utf-8") as f:
        seat = json.load(f).get("seat") or "BENCH"
    books = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    env = dict(os.environ, RIMFLOW_SEAT=seat, AGENT_SEAT=seat, RIMFLOW_BRIDGE_SEAT=relentless.BRIDGE_HOLDER,
               RELENTLESS_SUPERVISOR="1", CLAUDE_PROJECT_DIR=books)
    r = subprocess.run(["python3", os.path.join(HERE, "cli.py"), "bridge", "idle", "--for", "relentless game broker"],
                       cwd=books, env=env, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    return None if r.returncode == 0 else ((r.stdout or "") + (r.stderr or "")).strip()[-300:] or "bridge not idle"


def _round(root, item, timeout):
    """One prove round for one item, as GameFx.prove_launch ran it. -> (exit code, stdout)."""
    try:
        r = subprocess.run(["python3", os.path.join(HERE, "relentless_live_round.py"), "round", "--item", item],
                           cwd=os.path.abspath(os.path.join(HERE, "..", "..", "..")), capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL,
                           env=dict(os.environ, RELENTLESS_ROOT=root, RELENTLESS_PROOF_SOURCE="broker"))
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired as e:
        return 124, "timeout after %ss: %s" % (timeout, (e.stdout or "")[-400:] if isinstance(e.stdout, str) else "")


def _wake(root):
    import relentless_live_round
    relentless_live_round.wake_supervisor(root)


BRIDGE_WHY, ROUND, WAKE = _bridge_why, _round, _wake     # the selftest swaps these


def summary_of(out):
    """The round's printed summary JSON (indent=1, then possibly a wake line) -> dict, or {}."""
    a, b = out.find("{"), out.rfind("}")
    if a < 0 or b <= a:
        return {}
    try:
        got = json.loads(out[a:b + 1])
    except ValueError:
        return {}
    return got if isinstance(got, dict) else {}


def _log(store, rows):
    if not rows:
        return
    with open(os.path.join(_dir(store), "log.jsonl"), "a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def job(store):
    """The job process (`relentless_broker.py job`). -> relentless_jobs.run's word."""
    c = cfg()

    def fn(want):
        bid, root = want.get("batch"), want.get("root") or store.root
        ran = 0
        for item in want.get("items") or []:
            e = entry(store, item)
            if not e or e.get("state") != "running" or e.get("batch") != bid:
                continue
            why = BRIDGE_WHY(root)
            if why:     # an owner hold or another holder arrived between rounds: the rest walk on, nothing overridden
                _update(store, lambda q, item=item: q["items"][item].update(state="skipped", why=why[:200],
                                                                          ended=time.time()))
                continue
            code, out = ROUND(root, item, c["round_timeout_s"])
            summ = summary_of(out)
            runs = [x for x in summ.get("runs") or [] if isinstance(x, dict)]
            t = time.time()
            _log(store, [{"at": t, "batch": bid, "item": item, "criterion": x.get("criterion"),
                          "outcome": x.get("outcome")} for x in runs])
            outcomes = dict(collections.Counter(str(x.get("outcome")) for x in runs))
            _update(store, lambda q, item=item: q["items"][item].update(
                state="ran", ran_at=t, ended=t, code=code, outcomes=outcomes,
                why=(summ.get("why") or ("" if summ else out[-200:]))[:200]))
            ran += 1
            WAKE(root)      # the item settles on the next game pass
        return {"batch": bid, "ran": ran}
    def guarded(want):
        try:
            return fn(want)
        except Exception as e:  # noqa: BLE001  recorded, so the broker is held off on this code; the job still ends loudly
            fault(store, "job", e)
            raise
    return _jobs().run(store, KIND, guarded)


# ---------------------------------------------------------------- SLIs (relentless.py reading)

def slis(store, now=None):
    """Clauses completed per day (rows with a verdict in the last 24 h), oldest queued age, queue length, lost total."""
    now = time.time() if now is None else now
    day = now - 86400
    done = ran = 0
    try:
        with open(os.path.join(_dir(store), "log.jsonl"), encoding="utf-8") as f:
            for line in f:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and float(row.get("at") or 0) >= day:
                    ran += 1
                    done += row.get("outcome") in VERDICTS
    except OSError:
        pass
    q = load(store)
    waiting_at = [float(e.get("queued_at") or now) for e in q["items"].values() if e.get("state") == "queued"]
    f = faulted(store)
    return {"clauses_completed_day": done, "clauses_run_day": ran,
            "oldest_queued_s": int(now - min(waiting_at)) if waiting_at else None,
            "queued": len(waiting_at), "running": sum(e.get("state") == "running" for e in q["items"].values()),
            "lost_total": int(_jobs().table(store, KIND).get("lost") or 0), "held": q.get("held"),
            "enabled": cfg()["enabled"], "fault": (f or {}).get("why")}


def sli_line(s):
    age = s.get("oldest_queued_s")
    return ("broker: %d clause(s) completed/24h (%d run), oldest queued %s, %d queued, %d running, %d lost%s%s"
            % (s["clauses_completed_day"], s["clauses_run_day"], ("%ds" % age) if age is not None else "-",
               s["queued"], s["running"], s["lost_total"], (" | held: %s" % s["held"][:120]) if s.get("held") else "",
               (" | FAULT (old lane in use): %s" % s["fault"][:160]) if s.get("fault") else
               ("" if s.get("enabled") else " | disabled")))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("job", help="run the queued batch (launched by the supervisor, never by hand)")
    sub.add_parser("show", help="the queue, the job table and the SLIs")
    a = ap.parse_args(argv)
    sys.path.insert(0, HERE)
    import relentless
    store = relentless.Store()
    if a.cmd == "job":
        print(job(store))
        return 0
    print(json.dumps({"queue": load(store), "job": _jobs().table(store, KIND), "slis": slis(store)}, indent=1,
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
