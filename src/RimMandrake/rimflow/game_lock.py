#!/usr/bin/env python3
"""game_lock.py - who drives each game (ArchBig, ArchSmall). One record per game; a fast, token-free query, claim and release.

The one record of "who drives game X" is that game's process-keyed driver lock (driver_lock.py): ArchBig's (letter a)
is `<data root>/scratch/DRIVER_LOCK.json`, a named game's is `<instances root>/<letter>/DRIVER_LOCK.json`. A game is
typed by its name in any letter case (ArchBig, ArchSmall; on SteveDesktop Steve1, Steve2) or by its old letter or bridge
key; it is shown by its name (game_names.py, the one map). Every door
(`rimflow bridge who|take|release`, `./bridge`, host_guard, game_instance, the tick, `./pipe show`) reads or writes it
through this module. The ledger's bridge events are history written after the fact; nothing decides from them.

A holder is a PROCESS (pid + start time + boot). When it is gone, the game is free at once. A take made the old way
(`rimflow bridge take`, `host_guard.py take|run`) writes the same file in the same shape, so this module sees it, and
an old-style release frees it.

    game_lock.py query   [ArchBig|ArchSmall|all] [--json]     who drives it, since when, for what; or FREE
    game_lock.py claim   ArchBig|ArchSmall --for "<what>" [--seat S] [--force WHY] [--flyer] [--despite-hold WHY]
    game_lock.py release ArchBig|ArchSmall [--force WHY]      release what this process tree holds
    game_lock.py run     ArchBig|ArchSmall --for "<what>" [--seat S] -- CMD [ARGS...]     hold for CMD's life

Exit codes keep four answers apart (every verb):
    0   free (query) / done (claim, release; run: CMD's own exit code)
    75  held by someone else (query: held by anyone, this process tree included)
    3   his hold stops it: his OWNER hold, or `./pipe off game:<g>`
    2   could not look, with the cause (an unreadable lock or control store, no lock path). Never free, never held.
`query all` exits 2 when any game could not be looked at, else 0; each game's own answer is on its line.

Page: design/specs/2026-11-21-one-game-lock/boundary.md. Tests: selftest_game_lock.py.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (HERE, UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:                                    # imported as rimflow.game_lock (cli.py): one copy of driver_lock, not two
    from . import driver_lock
except ImportError:
    import driver_lock  # noqa: E402
try:
    from . import game_names
except ImportError:
    import game_names  # noqa: E402


def _host_guard():
    try:
        from . import host_guard
    except ImportError:
        import host_guard
    return host_guard

EX_FREE, EX_HELD, EX_HIS, EX_BLIND = 0, 75, 3, 2


class Blind(Exception):
    """A lock that could not be looked at (exit 2's cause), raised by a reader that has no "could not look" return."""
GAME_A = "a"                            # today's game: Steam's install, his
GEN_ENV = "RM_HOST_GUARD_GEN"           # a holder's children drive under its take (host_guard.export_take)
REMOTE_GAMES = ("stevedesktop", "stevedesktop.b")   # bridge keys of Steve1, Steve2: through their test lane, never read here
# budget: danger=a lock read in mid write is empty for milliseconds; ends no work: the reading says: could not look
WRITING_WAIT_S = 1.0                    # danger: a lock read mid-write is empty for milliseconds (driver_lock
                                        # WRITING_GRACE_S); past this the answer is "could not look", never a guess


# --- his flight rule: one home (cli.py imports it from here) -----------------------------------------------------
# Self-declared and fail-safe: any form of fly/flies/flew/flown/flight/flyer (also inside "butterfly", which only
# costs a refusal), take off/takeoff, airborne, glide, soar, aloft, wingspan. Not "flow" (FlowWorks).
_FLIGHT_RE = re.compile(r"fl(?:y|ie|ew|own|ight)|take[-\s]*offs?|airborne|glid|soar|aloft|wingspan", re.I)
# The one flight wording a delegated take admits: a read of a flyer's state with the game paused, by the tool that
# refuses unless paused and still (his card 2026-11-13, RIMMANDRAKE_ADMIT_PAUSED_FLYER_READS_AT_BRIDGE_TAKE: "paused
# reads allowed (no ticks, no pictures; anything moving still waits for him)"). Both the words and the tool's name must
# be there, and they are cut out before the check, so any other flight word beside them still refuses.
_PAUSED_FLYER_READ = re.compile(r"(?<!un)\bpaused flyer state read\b", re.I)
_PAUSED_FLYER_TOOL = re.compile(r"\bflyer_tier_three_state_read\.py\b", re.I)


def flight_purpose(text):
    text = text or ""
    if _PAUSED_FLYER_READ.search(text) and _PAUSED_FLYER_TOOL.search(text):
        text = _PAUSED_FLYER_TOOL.sub(" ", _PAUSED_FLYER_READ.sub(" ", text))
    return bool(_FLIGHT_RE.search(text))


# --- where each game's record lives -------------------------------------------------------------------------------
def games():
    import game_instance
    return game_instance.instances()


def check_game(g):
    """A game as typed (ArchBig, archsmall, b, game:b, archmagi.b) -> its letter on this machine. An unknown name, or a
    game of another machine, raises ValueError naming it (game_names.letter); nothing typed is today's game."""
    return game_names.letter("a" if g is None or not str(g).strip() else g)


def current_game():
    return (os.environ.get("RM_GAME_INSTANCE") or "a").strip().lower() or "a"


def lock_path(g):
    """-> game g's lock file, or None (no record can be looked at here). The same file every old door writes:
    game a's is driver_lock's (RIMFLOW_DRIVER_LOCK pins the lock of the game this shell names, host_guard.instance_env),
    a named game's is game_instance.lock_path (under RM_INSTANCES_ROOT). A redirected test ledger never reaches a live
    lock: under RIMFLOW_LEDGER game a needs RIMFLOW_DRIVER_LOCK and a named game needs RM_INSTANCES_ROOT."""
    g = check_game(g)
    env = os.environ.get("RIMFLOW_DRIVER_LOCK")
    if env is not None and g == current_game():
        return env or None
    test = bool(os.environ.get("RIMFLOW_LEDGER"))
    if g == "a":
        if test:                        # a test ledger whose RIMFLOW_DRIVER_LOCK names another game: no live a
            return None
        return driver_lock.DEFAULT if os.path.isdir(os.path.dirname(driver_lock.DEFAULT)) else None
    if test and not os.environ.get("RM_INSTANCES_ROOT"):
        return None
    import game_instance
    return game_instance.lock_path(g)


# --- the process tree ---------------------------------------------------------------------------------------------
def _tree():
    """-> [(pid, start)] for this process and its ancestors (WSL/Linux), nearest first."""
    out, p = [], os.getpid()
    for _ in range(64):
        if not p or p <= 1:
            break
        out.append((p, driver_lock._proc_start(p)))
        p = driver_lock._ppid(p)
    return out


def in_my_tree(ident):
    """The holder is this process, one of its ancestors (same pid, same start, same boot), or the process this one takes
    for (driver_lock.my_identity: the nearest claude/codex ancestor, or RM_DRIVER_PID)."""
    if not ident:
        return False
    if driver_lock.same_process(ident, driver_lock.my_identity()) or os.name == "nt":
        return driver_lock.same_process(ident, driver_lock.my_identity())
    if (ident.get("host") or "").lower() not in ("", driver_lock._local_host()) or ident.get("platform") != "wsl":
        return False
    if ident.get("boot_id") and ident["boot_id"] != driver_lock.current_boot_id():
        return False
    st = ident.get("start")
    return any(pid == ident.get("pid") and s is not None and st is not None and abs(s - st) < 0.05
               for pid, s in _tree())


# --- reading ------------------------------------------------------------------------------------------------------
def _alive_fast(cur):
    """driver_lock._alive without its slow branch: a Windows holder seen from WSL would cost a PowerShell probe
    (about 1 s, up to 30 s), so a query lets its heartbeat decide, as driver_lock does for any holder it cannot
    inspect. A claim judges it fully (driver_lock.acquire)."""
    ident = cur.get("identity") or {}
    if ident.get("platform") == "nt" and os.name != "nt":
        age = driver_lock._heartbeat_age(cur)
        alive = age is not None and age < driver_lock.STALE_HEARTBEAT_S
        return alive, "Windows pid %s, not inspected from WSL; heartbeat %s" % (
            ident.get("pid"), "%d s old" % age if age is not None else "absent")
    return driver_lock._alive(cur)


def _read_lock(path):
    """-> (cur or None, problem or None), waiting out a lock caught mid-write."""
    deadline = time.time() + WRITING_WAIT_S
    while True:
        cur, problem = driver_lock._read(path)
        if problem != "WRITING" or time.time() > deadline:
            return cur, ("UNREADABLE (still being written after %.0f s)" % WRITING_WAIT_S
                         if problem == "WRITING" else problem)
        time.sleep(0.05)


def pipe_hold(g):
    """-> (why or None, cause or None): his `./pipe off game:<g>` switch (control.game_held). A store that does not
    exist holds nothing (a hold is only ever written into it); one that cannot be read is a cause, not a "no"."""
    try:
        import control
    except Exception as e:  # noqa: BLE001  (an import that fails is an instrument that cannot see)
        return None, "the control store's code could not load: %s: %s" % (type(e).__name__, e)
    try:
        if not os.path.exists(control.db_path()):
            return None, None
        return control.game_held(g), None
    except control.Unreadable as e:
        return None, "the control store could not be read, so `pipe off game:%s` cannot be ruled out: %s" % (g, e)


def _local(ts):
    """'2026-11-21T11:26:58Z' -> '03:26 PST' (local time), or the input when it does not parse."""
    try:
        import calendar
        t = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
        return time.strftime("%H:%M %Z", time.localtime(t)), int(time.time() - t)
    except (TypeError, ValueError, OverflowError):
        return ts or "?", None


def query(g, pipe=True, path=None):
    """-> the answer for game g: {game, state, code, line, ...}. state is FREE, HELD, HIS_HOLD or UNKNOWN."""
    t0 = time.perf_counter()
    try:
        g = check_game(g)
        path = path or lock_path(g)
    except Exception as e:  # noqa: BLE001  (a data root that cannot resolve: the record cannot be looked at)
        return _done({"game": str(g), "state": "UNKNOWN", "code": EX_BLIND,
                      "cause": "no lock path: %s: %s" % (type(e).__name__, e)}, t0)
    r = {"game": g, "path": path}
    if not path:
        r.update(state="UNKNOWN", code=EX_BLIND, cause="no lock path on this machine (data root missing, or a test "
                 "ledger without RIMFLOW_DRIVER_LOCK / RM_INSTANCES_ROOT)")
        return _done(r, t0)
    hold, hold_cause = pipe_hold(g) if pipe else (None, None)
    cur, problem = _read_lock(path)
    if problem:
        r.update(state="UNKNOWN", code=EX_BLIND, cause="the lock %s is %s" % (path, problem))
        return _done(r, t0)
    if cur is not None:
        alive, how = _alive_fast(cur)
        since, age = _local(cur.get("acquired"))
        r.update(seat=cur.get("seat"), purpose=cur.get("purpose"), since=cur.get("acquired"), since_local=since,
                 held_s=age, heartbeat=cur.get("heartbeat"), generation=cur.get("generation"),
                 holder=cur.get("identity"), how=how, alive=alive, mine=bool(alive) and in_my_tree(cur.get("identity")),
                 clone=cur.get("clone"), role_unit=cur.get("role_unit"))
        if cur.get("seat") == "OWNER":
            # his rule is 45 min after his last INTERACTION, which a lock cannot see: his lock, live or not, is never
            # free from here (driver_lock.owner_held is only the floor of his rule)
            r.update(state="HIS_HOLD", code=EX_HIS, owner_hold=True,
                     note="takeability not measured here; `claim` measures his rule")
        elif alive:
            r.update(state="HELD", code=EX_HELD)
        else:
            r.update(state="FREE", code=EX_FREE, note="its last holder (%s) is gone" % how)
    else:
        r.update(state="FREE", code=EX_FREE, generation=driver_lock._last_gen(path))
    if hold:
        r["pipe_hold"] = hold
        if r["code"] in (EX_FREE, EX_HELD):
            r.update(code=EX_HIS, state="HIS_HOLD" if r["state"] == "FREE" else r["state"])
    if hold_cause:
        r.update(code=EX_BLIND, cause=hold_cause)
        if r["state"] == "FREE":
            r["state"] = "UNKNOWN"
    return _done(r, t0)


def query_all(pipe=True):
    """-> [query(g)] for every game of this machine, ArchBig first: what `query all` prints, and what every reader of
    "who drives the games" reads (maturation_nonmod, handoff, preflight_bridge). SteveDesktop's games are not read from here."""
    return [query(g, pipe=pipe) for g in games()]


def _done(r, t0):
    r["ms"] = round((time.perf_counter() - t0) * 1000, 1)
    r["line"] = line(r)
    return r


def line(r):
    g, st = r.get("game"), r.get("state")
    who = ""
    if r.get("seat"):
        held = r.get("held_s")
        who = "%s since %s%s, for: %s [%s]" % (
            r["seat"], r.get("since_local"), " (%d min)" % (held // 60) if held is not None else "",
            r.get("purpose") or "?", r.get("how"))
        if r.get("mine"):
            who += " (this process tree)"
    n = game_names.show(g)
    if st == "UNKNOWN":
        out = "%s: COULD NOT LOOK: %s" % (n, r.get("cause"))
    elif st == "HIS_HOLD":
        parts = []
        if r.get("owner_hold"):
            parts.append("his OWNER hold, %s; %s" % (who, r.get("note")))
        elif r.get("seat"):
            parts.append("HELD by %s" % who)
        if r.get("pipe_hold"):
            parts.append("pipe off game:%s: %s" % (n, r["pipe_hold"]))
        out = "%s: HIS HOLD: %s" % (n, "; ".join(parts))
    elif st == "HELD":
        out = "%s: HELD by %s" % (n, who)
    else:
        out = "%s: FREE%s" % (n, " (%s)" % r["note"] if r.get("note") else "")
    if r.get("cause") and st != "UNKNOWN":
        out += "; COULD NOT LOOK at his pipe hold: %s" % r["cause"]
    return out


# --- claim and release --------------------------------------------------------------------------------------------
def _classify(r):
    """A host_guard / driver_lock refusal -> its exit code."""
    why = r.get("why") or ""
    if (r.get("holder") or {}).get("seat") == "OWNER" or why.startswith("the OWNER") or "OWNER's lock moved" in why:
        return EX_HIS
    if "contended" in why or "UNREADABLE" in why or "WRITING" in why or not r.get("path", True):
        return EX_BLIND
    return EX_HELD


def default_seat():
    return (os.environ.get("RIMFLOW_SEAT") or "BENCH").strip().upper()


def claim(g, purpose, seat=None, force=None, flyer=False, identity=None, path=None, despite=None):
    """Take game g for `identity` (default: this process tree's owner, the window or run; driver_lock.owner_pid).
    -> {ok, code, line, ...}. His rules are read, not re-invented: `pipe off game:<g>`, his OWNER hold (measured by
    host_guard's owner gate, owner_interaction), and a flyer's flight (never claimed but by him)."""
    seat = (seat or default_seat()).upper()
    try:
        g = check_game(g)
        path = path or lock_path(g)
    except Exception as e:  # noqa: BLE001
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: no lock path: %s: %s" % (type(e).__name__, e))
    if not path:
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: no lock path on this machine (data root missing, or a test "
                    "ledger without RIMFLOW_DRIVER_LOCK / RM_INSTANCES_ROOT)")
    hold, cause = pipe_hold(g)
    if cause:
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: " + cause)
    if hold:
        if not despite:
            return _res(False, EX_HIS, g, "HIS HOLD: pipe off game:%s: %s (what passes: `./pipe on game:%s --why "
                        "\"...\"`)" % (game_names.show(g), hold, game_names.show(g)))
        sys.stderr.write("game_lock: %s is held (%s); acting anyway: %s\n" % (game_names.show(g), hold, despite))
    if (flyer or flight_purpose(purpose)) and seat != "OWNER":
        return _res(False, EX_HIS, g, "HIS HOLD: a flyer's flight is his act, never claimed without him present")
    cur, problem = _read_lock(path)
    if problem and not force:
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: the lock %s is %s (look at it, then --force \"<why>\" "
                    "breaks it, recorded)" % (path, problem))
    if cur and in_my_tree(cur.get("identity")) and driver_lock._alive(cur)[0]:
        if identity is None or driver_lock.same_process(identity, cur.get("identity")):
            driver_lock.heartbeat(path, cur["identity"])
        return _res(True, EX_FREE, g, "already held by this process tree (%s pid %s, gen %s)" % (
            cur.get("seat"), (cur.get("identity") or {}).get("pid"), cur.get("generation")),
            generation=cur.get("generation"), reentrant=True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = _host_guard().acquire(seat, purpose, force=force, identity=identity or driver_lock.my_identity(), path=path)
    if r.get("ok"):
        return _res(True, EX_FREE, g, "CLAIMED by %s, gen %s, for: %s%s" % (
            seat, r.get("generation"), purpose, " (broke a dead or forced holder)" if r.get("broke") else ""),
            generation=r.get("generation"))
    code = _classify(r)
    word = {EX_HIS: "HIS HOLD", EX_BLIND: "COULD NOT LOOK"}.get(code, "HELD")
    return _res(False, code, g, "%s: %s" % (word, r.get("why")), holder=r.get("holder"))


def release(g, force=None, seat=None, path=None):
    """Release game g when this process tree holds it. Another live holder's lock needs --force (recorded; his OWNER
    hold still refuses unless his rule is measured takeable). A lock whose holder is gone is already free."""
    seat = (seat or default_seat()).upper()
    try:
        g = check_game(g)
        path = path or lock_path(g)
    except Exception as e:  # noqa: BLE001
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: no lock path: %s: %s" % (type(e).__name__, e))
    if not path:
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: no lock path on this machine")
    cur, problem = _read_lock(path)
    if problem and not force:
        return _res(False, EX_BLIND, g, "COULD NOT LOOK: the lock %s is %s; nothing released" % (path, problem))
    if cur is None and not problem:
        return _res(True, EX_FREE, g, "already FREE")
    if cur is not None and in_my_tree(cur.get("identity")):
        r = driver_lock.release(path, cur.get("seat") or seat, cur["identity"])
        return _res(bool(r["ok"]), EX_FREE if r["ok"] else _classify(r), g,
                    "RELEASED" if r["ok"] else "NOT RELEASED: %s" % r["why"])
    if cur is not None and not force:
        alive, how = _alive_fast(cur)
        if not alive and cur.get("seat") != "OWNER":
            return _res(True, EX_FREE, g, "already FREE (its last holder, %s, is gone)" % how)
        return _res(False, EX_HIS if cur.get("seat") == "OWNER" else EX_HELD, g,
                    "NOT RELEASED: held by %s (%s), not this process tree; --force \"<why>\" cuts it, recorded" % (
                        cur.get("seat"), how), holder=cur)
    r = _host_guard().release(seat, force=force, identity=driver_lock.my_identity(), path=path)
    return _res(bool(r["ok"]), EX_FREE if r["ok"] else _classify(r), g,
                "RELEASED (forced: %s)" % force if r["ok"] else "NOT RELEASED: %s" % r["why"])


def _res(ok, code, g, text, **kw):
    d = {"ok": ok, "code": code, "game": g, "line": "%s: %s" % (game_names.show(g), text)}
    d.update(kw)
    return d


def run(g, purpose, cmd, seat=None, force=None, flyer=False):
    """Hold game g for CMD's life: the holder is THIS process, so the lock frees when CMD ends however it ends (exit,
    crash, SIGTERM or SIGINT forwarded and then released; SIGKILL of this process: its process is gone, so the game
    reads FREE at once). Children inherit the take (RM_HOST_GUARD_GEN). -> CMD's exit code, or a refusal's."""
    me = _host_guard().self_identity()
    path = lock_path(g)
    child = None
    pending = []
    release_ours = False

    def forward(signum, _frame):
        if child is None:
            pending.append(signum)
        elif child.poll() is None:
            try:
                child.send_signal(signum)
            except OSError:
                pass

    # The lock can be seen before Popen returns. Catch signals before publishing it and forward them once CMD exists.
    olds = {s: signal.signal(s, forward) for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    try:
        inherited = None
        if path and os.environ.get(GEN_ENV):
            cur, _p = driver_lock._read(path)
            if cur and str(cur.get("generation")) == os.environ[GEN_ENV] and driver_lock._alive(cur)[0]:
                inherited = cur.get("generation")
        if inherited is None:
            r = claim(g, purpose, seat=seat, force=force, flyer=flyer, identity=me)
            if not r["ok"]:
                sys.stderr.write(r["line"] + "\n")
                return r["code"]
            gen = r.get("generation")
            release_ours = not r.get("reentrant")
            if not release_ours:
                inherited = gen
        else:
            gen = inherited
        env = dict(os.environ)
        env[GEN_ENV] = str(gen)
        wslenv = env.get("WSLENV", "")
        if GEN_ENV not in wslenv.split(":"):
            env["WSLENV"] = (wslenv + ":" if wslenv else "") + GEN_ENV
        sys.stderr.write("%s: held for `%s` (gen %s%s)\n" % (game_names.show(g), " ".join(cmd), gen,
                                                                  ", inherited" if inherited is not None else ""))
        try:
            child = subprocess.Popen(cmd, env=env)
        except OSError as e:
            sys.stderr.write("%s: could not start %s: %s\n" % (game_names.show(g), cmd[0], e))
            return 127
        for signum in pending:
            forward(signum, None)
        while True:
            try:
                rc = child.wait()
                break
            except InterruptedError:
                continue
        return rc if rc >= 0 else 128 - rc
    finally:
        try:
            if release_ours and path:
                driver_lock.release(path, seat or default_seat(), me)
        finally:
            for s, h in olds.items():
                signal.signal(s, h)


# --- the command --------------------------------------------------------------------------------------------------
def _emit(r, as_json):
    if as_json:
        print(json.dumps(r, default=str))
    else:
        print(r["line"])


def _query_main(args):
    """`query [ArchBig|ArchSmall|all] [--json]`, parsed by hand: argparse alone costs ~15 ms of the 100 ms bound (measured)."""
    as_json = "--json" in args
    rest = [x for x in args if x != "--json"]
    if len(rest) > 1 or any(x.startswith("-") for x in rest):
        sys.stderr.write("usage: game_lock.py query [ArchBig|ArchSmall|all] [--json]\n")
        return EX_BLIND
    game = rest[0] if rest else "all"
    if game.lower() != "all":
        try:
            check_game(game)
        except ValueError as e:     # an unknown name is refused by name, never read as a default game
            sys.stderr.write("REFUSED: %s\n" % e)
            return EX_BLIND
    if game.lower() == "all":
        rs = query_all()
        if as_json:
            print(json.dumps({"games": rs, "remote": {h: "through the SteveDesktop test lane "
                                                      "(infrastructure/stevedesktop/RUNBOOK.md)"
                                                      for h in REMOTE_GAMES}}, default=str))
        else:
            for r in rs:
                print(r["line"])
            print("SteveDesktop games (%s): through the test lane, not read from here"
                  % ", ".join(game_names.show_key(h) for h in REMOTE_GAMES))
        return EX_BLIND if any(r["code"] == EX_BLIND for r in rs) else 0
    r = query(game)
    _emit(r, as_json)
    return r["code"]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["query"] and "-h" not in argv and "--help" not in argv:
        return _query_main(argv[1:])
    import argparse
    ap = argparse.ArgumentParser(prog="game_lock.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("query")
    q.add_argument("game", nargs="?", default="all")
    q.add_argument("--json", action="store_true")
    for name in ("claim", "release", "run"):
        s = sub.add_parser(name)
        s.add_argument("game")
        s.add_argument("--json", action="store_true")
        s.add_argument("--seat", default=None, help="the seat shown on the lock (default: RIMFLOW_SEAT, else BENCH)")
        s.add_argument("--force", default=None, help="break a live or unreadable lock; the reason is recorded")
        if name != "release":
            s.add_argument("--for", dest="purpose", required=True)
            s.add_argument("--flyer", action="store_true", help="the work flies a flyer: his act only")
        if name == "claim":
            s.add_argument("--despite-hold", dest="despite", metavar="WHY", help="claim despite the pipe game hold")
    cmd = []
    if argv[:1] == ["run"] and "--" in argv:     # everything after `--` is CMD, whatever flags it carries
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    a = ap.parse_args(argv)
    if a.cmd == "query":
        return _query_main([a.game] + (["--json"] if a.json else []))
    try:
        check_game(a.game)
    except ValueError as e:     # an unknown name is refused by name, never read as a default game
        sys.stderr.write("REFUSED: %s\n" % e)
        return EX_BLIND
    if a.cmd == "claim":
        r = claim(a.game, a.purpose, seat=a.seat, force=a.force, flyer=a.flyer, despite=a.despite)
        _emit(r, a.json)
        return r["code"]
    if a.cmd == "release":
        r = release(a.game, force=a.force, seat=a.seat)
        _emit(r, a.json)
        return r["code"]
    if not cmd:
        ap.error("run needs a command after --")
    return run(a.game, a.purpose, cmd, seat=a.seat, force=a.force, flyer=a.flyer)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
