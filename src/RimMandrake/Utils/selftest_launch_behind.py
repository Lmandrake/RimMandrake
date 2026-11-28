#!/usr/bin/env python3
"""selftest_launch_behind.py - every start of a game goes through launch_behind.guarded, the one shared function.

RIMMANDRAKE_LAUNCH_GAME_BEHIND_HIS_WINDOWS_IT_STEALS_FOCUS. Offline, no Windows. Checks:
  every_start_goes_through_guarded:
  guarded_paths        in game_instance.py, every launch act (a call that carries STEAM_URL, or the _ps/_run call of a
                       function that builds a start of GAME_EXE: launch_behind.start_script or a Start-Process) sits inside a launch_behind.guarded(...)
                       argument, or in a private function that is itself reached only through one. No public function
                       (launch, fire_a, main, ...) reaches a launch act outside guarded.
  no_other_starter     no other file under src/RimMandrake starts the game itself (rungameid, a Start-Process of
                       RimWorldWin64, start_script or [RmWin]::Start): every tool goes through game_instance.
  planted_paths_red    three planted faults turn the two checks above red: the named game's start unguarded, a new
                       public function that starts the exe directly, and a second file that fires rungameid.
  the_guard_is_up_before_the_launch_fires, a_front_reason_starts_no_guard_and_says_why,
  a_guard_that_cannot_start_never_stops_the_launch:
                       guarded() starts the guard before the launch; with a front reason (argument or RM_LAUNCH_FRONT)
                       it starts none and says why; a guard that cannot start never stops the launch.
Each check above is part of a promise test of the same name on design/specs/2026-11-27-launch-behind/boundary.md.
Exit 0 all pass, 1 a check failed.
"""
import ast
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import launch_behind  # noqa: E402

GI = os.path.join(HERE, "game_instance.py")
FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail else ""))
    if not ok:
        FAILS.append(name)


def _is_guarded_call(node):
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    return ((isinstance(f, ast.Attribute) and f.attr == "guarded") or
                                           (isinstance(f, ast.Name) and f.id == "guarded"))


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _strs(node):
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def unguarded_starts(source):
    """-> [(function, line, why)] for each public function that reaches a launch act outside launch_behind.guarded."""
    tree = ast.parse(source)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    parent = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            parent[c] = n

    def inside_guarded(node):
        n = node
        while n in parent:
            p = parent[n]
            if _is_guarded_call(p) and n is not p.func:
                return True
            n = p
        return False

    acts = {}           # function -> [(line, why)] of launch acts outside guarded
    for name, fn in funcs.items():
        builds_start = (any("Start-Process" in s for s in _strs(fn)) and "GAME_EXE" in _names(fn)) or any(
            isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "start_script"
            for c in ast.walk(fn))
        for c in ast.walk(fn):
            if not isinstance(c, ast.Call) or inside_guarded(c):
                continue
            callee = c.func.id if isinstance(c.func, ast.Name) else (c.func.attr if isinstance(c.func, ast.Attribute)
                                                                       else "")
            if "STEAM_URL" in _names(c) or any("rungameid" in s for s in _strs(c)):
                acts.setdefault(name, []).append((c.lineno, "fires the Steam URL"))
            elif builds_start and callee in ("_ps", "_run", "run", "Popen"):
                acts.setdefault(name, []).append((c.lineno, "runs a start of GAME_EXE"))
    reach = dict(acts)
    changed = True
    while changed:              # a function that calls a reaching function outside guarded reaches too
        changed = False
        for name, fn in funcs.items():
            if name in reach:
                continue
            for c in ast.walk(fn):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in reach and \
                        not inside_guarded(c):
                    reach[name] = [(c.lineno, "calls %s outside guarded" % c.func.id)]
                    changed = True
                    break
    return [(n, w[0][0], w[0][1]) for n, w in sorted(reach.items()) if not n.startswith("_")]


START_RE = re.compile(r"rungameid|Start-Process[^\n]{0,200}(RimWorldWin64|GAME_EXE)|start_script\(|Win32_Process -MethodName Create",
                      re.I)
SCAN_SKIP = ("game_instance.py", "launch_behind.py", "fake_two_games.py", "selftest_launch_behind.py")


def other_starters(root):
    """-> [path:line] of files under root (py, sh, ps1) other than game_instance.py that start the game themselves."""
    hits = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "Source", "__pycache__", "bin", "obj")]
        for fn in files:
            if not fn.endswith((".py", ".sh", ".ps1")) or fn in SCAN_SKIP or fn.startswith("selftest_"):
                continue
            p = os.path.join(d, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    lines = f.read().splitlines()
            except OSError:
                continue
            for i, ln in enumerate(lines, 1):
                if START_RE.search(ln.split("#", 1)[0]):        # a comment that names the route starts nothing
                    hits.append("%s:%d" % (os.path.relpath(p, root), i))
    return hits


def _src():
    with open(GI, encoding="utf-8") as f:
        return f.read()


def t_every_start_goes_through_guarded():
    _guarded_paths()
    _no_other_starter()
    _planted_paths_red()


def _guarded_paths():
    bad = unguarded_starts(_src())
    check("guarded_paths", not bad, "; ".join("%s line %d %s" % b for b in bad) or "every start is guarded")


def _no_other_starter():
    hits = other_starters(os.path.join(REPO, "src", "RimMandrake"))
    check("no_other_starter", not hits, ", ".join(hits) or "only game_instance.py starts a game")


def _planted_paths_red():
    src = _src()
    a = src.replace("launch_behind.guarded(lambda: _ps(script), log, front)", "(_ps(script), 'unguarded')")
    check("planted_named_start_unguarded", a != src and bool(unguarded_starts(a)),
          "%s" % (unguarded_starts(a) if a != src else "the plant did not apply"))
    b = src + "\n\ndef quick_start(flags=()):\n    _start_direct_a(list(flags))\n"
    check("planted_public_direct_start", bool(unguarded_starts(b)), "%s" % unguarded_starts(b))
    c = src.replace("launch_behind.guarded(lambda: _fire_a(sleep, clock, front), a_player_log(), front)",
                    "(_fire_a(sleep, clock, front), 'unguarded')")
    check("planted_steam_route_unguarded", c != src and bool(unguarded_starts(c)),
          "%s" % (unguarded_starts(c) if c != src else "the plant did not apply"))
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "quick_launch.py"), "w") as f:
            f.write('import subprocess\nsubprocess.run(["cmd.exe", "/c", "start", "", "steam://rungameid/294100"])\n')
        with open(os.path.join(d, "own_start.py"), "w") as f:
            f.write('import launch_behind\nscript = launch_behind.start_script("C:\\\\G\\\\RimWorldWin64.exe", "C:\\\\G", [])\n')
        with open(os.path.join(d, "clean.py"), "w") as f:
            f.write('import game_instance\ngame_instance.launch("b")\n')
        hits = other_starters(d)
        check("planted_second_starter", sorted(hits) == ["own_start.py:2", "quick_launch.py:2"], "%s" % hits)


class _Fake:
    """start_guard replaced for one test: records the order of guard and launch."""

    def __init__(self, ok=True):
        self.calls, self.ok, self.real = [], ok, launch_behind.start_guard

    def __enter__(self):
        os.environ.pop(launch_behind.FRONT_ENV, None)
        launch_behind.start_guard = lambda log, **k: (self.calls.append(("guard", log)), (
            (True, "guard pid 1") if self.ok else (False, "guard: COULD NOT START (planted)")))[1]
        return self

    def fire(self):
        self.calls.append(("fire",))
        return "fired"

    def __exit__(self, *a):
        launch_behind.start_guard = self.real
        os.environ.pop(launch_behind.FRONT_ENV, None)


def t_the_guard_is_up_before_the_launch_fires():
    with _Fake() as f:
        r, note = launch_behind.guarded(f.fire, "L")
        check("guard_before_fire", f.calls == [("guard", "L"), ("fire",)] and r == "fired" and "behind" in note,
              "%s %r" % (f.calls, note))


def t_a_front_reason_starts_no_guard_and_says_why():
    with _Fake() as f:
        r, note = launch_behind.guarded(f.fire, "L", front="owner sitting")
        check("front_arg_no_guard", f.calls == [("fire",)] and "owner sitting" in note, "%s %r" % (f.calls, note))
    with _Fake() as f:
        os.environ[launch_behind.FRONT_ENV] = "his look at ArchBig"
        r, note = launch_behind.guarded(f.fire, "L")
        check("front_env_no_guard", f.calls == [("fire",)] and "his look" in note, "%s %r" % (f.calls, note))


def t_a_direct_start_shows_the_window_without_activating_it():
    os.environ.pop(launch_behind.FRONT_ENV, None)
    plain = launch_behind.start_script(r"C:\Program Files\G\RimWorldWin64.exe", "C:\\G", ["-a", "it's x"],
                                       env_set=[("GABP_TOKEN", "t")], env_remove=("GABP_SERVER_PORT",))
    front = launch_behind.start_script("C:\\G\\RimWorldWin64.exe", "C:\\G", [], front="owner sitting")
    check("start_through_wmi_noactivate", "-MethodName Create" in plain and "ShowWindow=[uint16]4;" in plain
          and "@('GABP_TOKEN','GABP_SERVER_PORT') -notcontains" in plain and "+ @('GABP_TOKEN=t')" in plain
          and "$q + 'it''s x' + $q" in plain and '"' not in plain and "Start-Process" not in plain, plain)
    check("start_front_shows_normal", "ShowWindow=[uint16]1;" in front, front)


def t_a_guard_that_cannot_start_never_stops_the_launch():
    with _Fake(ok=False) as f:
        r, note = launch_behind.guarded(f.fire, "L")
        check("guard_failure_still_launches", f.calls == [("guard", "L"), ("fire",)] and r == "fired"
              and "COULD NOT START" in note, "%s %r" % (f.calls, note))


def main():
    t_every_start_goes_through_guarded()
    t_the_guard_is_up_before_the_launch_fires()
    t_a_front_reason_starts_no_guard_and_says_why()
    t_a_guard_that_cannot_start_never_stops_the_launch()
    t_a_direct_start_shows_the_window_without_activating_it()
    print("selftest_launch_behind: %s" % ("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
