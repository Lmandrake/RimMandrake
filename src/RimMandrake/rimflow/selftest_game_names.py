#!/usr/bin/env python3
"""selftest_game_names.py - the promises of design/specs/2026-11-22-game-names/boundary.md, one test each.

The owner named the four games ArchBig, ArchSmall, Steve1 and Steve2 (card, 2026-11-22). Three kinds of check, each run
twice: once on the real map (every check must pass) and once on a planted wrong map, ArchSmall pointed at Steam's
install (`archmagi`), where the mapping checks must go red. A run that cannot turn red on the plant fails.

  (a) each reader prints the new names and no bare "game a" / "game b";
  (b) each input form takes the new names (any case) and the old aliases, and both reach the same lock;
  (c) an unknown name is refused by name, never mapped to a default game.

Nothing here reads or writes a live lock, game or control store: locks and stores are throwaway files under TMP.
"""
import atexit
import contextlib
import io
import os
import re
import shutil
import sys
import tempfile

TMP = tempfile.mkdtemp(prefix="st_game_names_")
atexit.register(shutil.rmtree, TMP, True)
for _k in ("RM_GAME_INSTANCE", "RM_GAME_USERDATA", "RM_GAME_LOGDIR", "RM_HOST_GUARD_GEN", "RM_DRIVER_PID",
           "RIMFLOW_DRIVER_LOCK", "RM_GAME_INSTANCES"):
    os.environ.pop(_k, None)
os.makedirs(os.path.join(TMP, "instances", "b"))
os.makedirs(os.path.join(TMP, "ledger", "items"))
os.environ.update(RM_HOST="archmagi", RM_INSTANCES_ROOT=os.path.join(TMP, "instances"),
                  RIMFLOW_LEDGER=os.path.join(TMP, "ledger"), RM_CONTROL_DB=os.path.join(TMP, "control.db"))
HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import game_names as GN          # noqa: E402
import game_lock as GL           # noqa: E402
import game_instance as GI       # noqa: E402
import control as C              # noqa: E402

BARE = re.compile(r"\bgames? [ab]\b|\bgame:[ab]\b", re.I)
FAILS = []
QUIET = False


def check(cond, msg, detail=""):
    if not QUIET:
        print(("ok   " if cond else "FAIL ") + msg + ("" if cond else "  %s" % (detail,))[:600])
    if not cond:
        FAILS.append(msg)
    return bool(cond)


def raises(fn, *a):
    try:
        fn(*a)
    except Exception as e:      # noqa: BLE001
        return str(e)
    return None


@contextlib.contextmanager
def host(name):
    old = os.environ.get("RM_HOST")
    os.environ["RM_HOST"] = name
    try:
        yield
    finally:
        os.environ["RM_HOST"] = old


def _model():
    import model
    return model


# --- (a) readers --------------------------------------------------------------------------------------------------
def t_every_reader_prints_the_games_name_never_a_bare_letter():
    want = {"a": "ArchBig", "b": "ArchSmall"}
    for g, name in want.items():
        for st in ({"state": "FREE"}, {"state": "HELD", "seat": "BENCH", "holder": "BENCH"},
                   {"state": "UNKNOWN", "cause": "x"}, {"state": "HIS_HOLD", "pipe_hold": "walk"}):
            line = GL.line(dict(st, game=g))
            check(name in line and not BARE.search(line), "game_lock line %s %s names %s" % (g, st["state"], name), line)
        r = GL._res(False, 75, g, "HELD by X")
        check(name in r["line"] and not BARE.search(r["line"]), "game_lock refusal for %s names %s" % (g, name),
              r["line"])
    with host("stevedesktop"):
        check(GL.line({"game": "a", "state": "FREE"}).startswith("Steve1"), "on SteveDesktop game_lock says Steve1",
              GL.line({"game": "a", "state": "FREE"}))
        check(GN.show("b") == "Steve2", "on SteveDesktop letter b is Steve2", GN.show("b"))

    # game_instance status and brief, with the process list and locks stubbed
    saved = GI.games, GL.query
    try:
        GI.games = lambda *a, **k: [{"instance": "b", "pid": 42}]
        GL.query = lambda g, pipe=True, path=None: {"game": g, "state": "FREE", "line": GL.line({"game": g,
                                                                                              "state": "FREE"})}
        lines = GI.status_lines()
        text = "\n".join(lines)
        check("ArchBig" in text and "ArchSmall" in text and not BARE.search(text),
              "game_instance status names ArchBig and ArchSmall", text)
        check(lines[0].startswith("ArchBig") and lines[1].startswith("ArchSmall"),
              "game_instance status rows start with the game's name", text)
    finally:
        GI.games, GL.query = saved
    b = GI.brief("b", full_list=["full_check"])
    check("ArchSmall" in b and "ArchBig" in b and not BARE.search(b), "the run brief for ArchSmall names both games",
          [m.group(0) for m in BARE.finditer(b)])
    a = GI.brief("a")
    check("ArchBig" in a and not BARE.search(a), "the run brief for ArchBig names it", a[:300])

    # ./pipe show's per-game lines and a switch's description
    saved = GL.games, GL.lock_path, GL.query
    try:
        GL.games = lambda: ["a", "b"]
        GL.lock_path = lambda g: "/x/%s" % g
        GL.query = lambda g, pipe=True, path=None: {"game": g, "state": "HELD", "seat": "BENCH",
                                                    "line": GL.line({"game": g, "state": "HELD", "holder": "BENCH"})}
        for short in (True, False):
            text = "\n".join(C.game_lines(short=short))
            check("ArchBig" in text and "ArchSmall" in text and not BARE.search(text),
                  "pipe show game lines (short=%s) name both games" % short, text)
    finally:
        GL.games, GL.lock_path, GL.query = saved
    d = C.describe({"layer": "owner", "scope": "game:b", "date": "2026-11-22", "said": "walk", "why": ""})
    check("ArchSmall" in d and not BARE.search(d), "a game switch's description names ArchSmall", d)
    # `pipe undo` of a game's OFF names the game (polish line of 2026-11-22, taken 2026-11-26)
    C.init(os.environ["RM_CONTROL_DB"])
    off = C.switch("game:b", True, "selftest: undo names the game")
    u = C.undo(off["act"]["id"] if isinstance(off.get("act"), dict) else off.get("act"), "selftest: undo names the game")
    check(u["ok"] and "ArchSmall" in u["line"] and not BARE.search(u["line"]), "pipe undo of a game OFF names ArchSmall",
          u["line"])

    # the tick's reasons per game
    import maturation_dispatch as MD
    games, whys = MD.pick_game({"game_instances": ["a", "b"]}, lambda p, game="a": (False, "busy"), "visit",
                               hold=lambda g: "his walk" if g == "a" else None)
    text = "; ".join(whys)
    check(games is None and "ArchBig" in text and "ArchSmall" in text and not BARE.search(text),
          "the tick's reasons name ArchBig and ArchSmall", text)

    # rimflow bridge who for another game
    import cli
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        cli._who_lines({"state": "FREE", "game": "b", "line": GL.line({"game": "b", "state": "FREE"})}, "archmagi.b")
    text = out.getvalue()
    check("ArchSmall" in text and "archmagi.b bridge" not in text and not BARE.search(text),
          "bridge who for archmagi.b names ArchSmall", text)


# --- (b) inputs ---------------------------------------------------------------------------------------------------
def t_every_input_takes_a_name_in_any_case_and_the_old_keys_and_both_reach_one_lock():
    forms = {"a": ("ArchBig", "archbig", "ARCHBIG", "a", "A", "game:a", "archmagi", "archmagi.a", "game:ArchBig"),
             "b": ("ArchSmall", "archsmall", "ARCHSMALL", "b", "game:b", "archmagi.b", "game:archsmall")}
    for g, fs in forms.items():
        for f in fs:
            got = raises(GL.check_game, f) or GL.check_game(f)
            check(got == g, "game_lock takes %r as %s" % (f, GN.show(g)), got)
            got = raises(GI.check_name, f) or GI.check_name(f)
            check(got == g, "game_instance takes %r as %s" % (f, GN.show(g)), got)
            got = raises(C.scope_of, "game:" + (f[5:] if f.lower().startswith("game:") else f)) or \
                C.scope_of("game:" + (f[5:] if f.lower().startswith("game:") else f))
            check(got == "game:" + g, "pipe takes game:%s as game:%s" % (f, g), got)
        paths = {raises(GL.check_game, f) or GL.lock_path(GL.check_game(f)) for f in fs}
        check(len(paths) == 1, "every form of %s reaches one lock" % GN.show(g), paths)
    check((raises(GL.check_game, "ArchSmall") or GL.lock_path(GL.check_game("ArchSmall"))) == GI.lock_path("b"),
          "ArchSmall's lock is game_instance's lock of b (instances/b), not Steam's", GL.lock_path("b"))
    for f in ("ArchSmall", "archsmall", "b"):
        sc = C.run_scopes({"family": "detached", "game": f})
        check("game:b" in sc, "a run spec naming %r lives in the store's scope game:b" % f, sc)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = GI.main(["env", "ArchSmall"])
    check(rc == 0 and "RM_GAME_INSTANCE=b" in out.getvalue(), "game_instance env ArchSmall exports instance b",
          out.getvalue())
    hk = {"ArchBig": "archmagi", "ArchSmall": "archmagi.b", "Steve1": "stevedesktop", "Steve2": "stevedesktop.b"}
    M = _model()
    for n, k in hk.items():
        for f in (n, n.lower(), n.upper(), k):
            got = raises(M.bridge_host_key, f) or M.bridge_host_key(f)
            check(got == k, "--host %s is %s" % (f, k), got)
        check(GN.show_key(k) == n, "the bridge key %s reads %s" % (k, n), GN.show_key(k))
    with host("stevedesktop"):
        got = (raises(GL.check_game, "Steve2") or GL.check_game("Steve2"),
               raises(GI.check_name, "steve1") or GI.check_name("steve1"))
        check(got == ("b", "a"), "on SteveDesktop Steve1/Steve2 are its letters a/b", got)


# --- (c) unknown names ----------------------------------------------------------------------------------------------
def t_an_unknown_name_is_refused_by_name_never_a_default_game():
    for bad in ("ArchMedium", "game:Steve3", "archmagi2"):
        for what, fn in (("game_lock", GL.check_game), ("game_instance", GI.check_name),
                         ("pipe", lambda x: C.scope_of("game:" + x.split(":")[-1]))):
            e = raises(fn, bad)
            check(e is not None and bad.split(":")[-1] in e, "%s refuses %r by name" % (what, bad), e)
        e = raises(_model().bridge_host_key, bad.split(":")[-1])
        check(e is not None and bad.split(":")[-1] in e, "--host refuses %r by name" % bad, e)
    e = raises(GL.check_game, "Steve1")
    check(e is not None and "Steve1" in e and "SteveDesktop".lower() in e.lower(),
          "on Archmagi Steve1 is refused as SteveDesktop's game, never mapped to ArchBig", e)


def run_all(tests):
    del FAILS[:]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s raised" % t.__name__, "%s: %s" % (type(e).__name__, e))
    return list(FAILS)


def main():
    global QUIET
    tests = (t_every_reader_prints_the_games_name_never_a_bare_letter,
             t_every_input_takes_a_name_in_any_case_and_the_old_keys_and_both_reach_one_lock,
             t_an_unknown_name_is_refused_by_name_never_a_default_game)
    real = run_all(tests)
    print("real map: %d FAIL" % len(real))
    good = GN.GAMES
    GN.GAMES = tuple(("ArchSmall", "archmagi", "archmagi", "a") if n == "ArchSmall" else (n, k, m, l)
                     for n, k, m, l in good)
    QUIET = True
    try:
        planted = run_all(tests)
    finally:
        GN.GAMES, QUIET = good, False
    print("planted map (ArchSmall -> Steam's install): %d FAIL (must be > 0)" % len(planted))
    for m in planted[:6]:
        print("  planted red: %s" % m)
    ok = not real and planted
    print("selftest_game_names: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
