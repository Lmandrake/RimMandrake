#!/usr/bin/env python3
"""selftest for launch_permissions.py: each promise of design/specs/2026-11-23-launch-permissions/boundary.md, and the
tree itself (the last check: every launch specification in this repo skips permissions)."""
import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import launch_permissions as LP  # noqa: E402

BAD = []


def check(name, ok, got=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        BAD.append(name)


ROWS = []


def scanned():
    """The real tree, read once."""
    if not ROWS:
        ROWS.extend(LP.scan())
    return ROWS


def py(src):
    return [v for _l, v, _w in LP.Py(src, "x.py").sites()]


def sh(src):
    return [v for _l, v, _w in LP.shell_sites(src)]


S, W, N, L = LP.SKIPS, LP.WALLED, LP.NOSESSION, LP.LACKS
F = LP.FLAG

OLD_FLEET = """$tiles = @(
    @{ Title = 'S'; Dir = '~/seat-server'; Cmd = '~/.local/bin/claude remote-control --name SteveDesktop-Server' },
    @{ Title = 'R'; Dir = '~/rm/runner'; Cmd = '~/.local/bin/claude --remote-control SteveDesktop-Runner' }
)
"""
NEW = OLD_FLEET.replace("remote-control --name SteveDesktop-Server", "remote-control --name SteveDesktop-Server --permission-mode "
                        "bypassPermissions").replace("claude --remote-control", "claude %s --remote-control" % F)


def t_a_launch_without_the_flag_is_red():
    check("the 2026-10-31 fleet lines that blocked him are red", sh(OLD_FLEET) == [L, L], sh(OLD_FLEET))
    check("the fixed fleet lines are green", sh(NEW) == [S, S], sh(NEW))
    WAKE = 'import shlex, shutil\ndef launch_wake(b):\n exe = shutil.which("claude") or "x"\n return w("%%s -p \\"$(cat %%s)\\"%s" %% (shlex.quote(exe), b))\n'
    check("the test lane's wake line as it stood is red", py(WAKE % "") == [L], py(WAKE % ""))
    check("the test lane's wake line with the flag is green", py(WAKE % (" " + F)) == [S])
    check("an argv list without the flag is red", py('CLAUDE="/h/.local/bin/claude"\nrun([CLAUDE, "-p", q, "--model", "opus"])') == [L])
    check("an argv list with the flag is green", py('CLAUDE="/h/.local/bin/claude"\nrun([CLAUDE, "-p", q, "%s"])' % F) == [S])
    check("--allowed-tools is no wall: red", py('run(["claude", "-p", q, "--allowed-tools", "Read"])') == [L])
    check("another permission mode is red", py('run(["claude", "-p", q, "--permission-mode", "acceptEdits"])') == [L])
    check("the flag on one branch only is red",
          py('def f(a):\n run(["claude", "-p", q] + (["%s"] if a else []))' % F) == [L])
    check("the flag added under an if is red",
          py('def f(a):\n cmd = ["claude", "-p", q]\n if a:\n  cmd += ["%s"]\n run(cmd)' % F) == [L])
    check("the flag added on every path is green",
          py('def f(a):\n cmd = ["claude", "-p", q]\n cmd += ["%s"]\n run(cmd)' % F) == [S])
    check("a helper function whose every return carries it is green",
          py('def t(a):\n if a:\n  return ["%s"]\n return ["--tools", a]\ndef f():\n cmd = ["claude", "-p"]\n cmd += t(1)\n' % F) == [W])
    check("a helper function with one bare return is red",
          py('def t(a):\n if a:\n  return ["%s"]\n return []\ndef f():\n cmd = ["claude", "-p"]\n cmd += t(1)\n' % F) == [L])
    check("the flag on a later, different argv does not count",
          py('def f():\n a = ["claude", "-p", q]\n run(a)\n b = ["x", "%s"]' % F) == [L])
    check("a command a brief tells an agent to run is red",
          py('def h():\n return ("Start each: `src/RimMandrake/Utils/claude_bounded.sh -p --model opus \\"<its brief>\\"`")') == [L])
    check("a WT profile line is red without the flag", py('LAUNCH = ("{script} --name \'{label}\' --model {model}")') == [L])
    check("a remote-control line kept apart from its program is red", py('SERVER = "remote-control --name \'x\'"') == [L]
          and py('SERVER = "remote-control --name \'x\' --permission-mode bypassPermissions"') == [S])
    check("a shell variable that holds the program is followed", sh('W="$H/claude_bounded.sh"\n"$W" --name x "$P"\n') == [L]
          and sh('W="$H/claude_bounded.sh"\n"$W" %s --name x "$P"\n' % F) == [S])
    check("a shell line continued over lines is one line", sh("claude -p \"$x\" \\\n  --model opus %s\n" % F) == [S])
    check("a unit file's ExecStart is read, its comment is not",
          [v for _l, v, _w in LP.shell_sites("# a `claude -p --x` run\nExecStart=/u/claude -p \"go\"\n", unit=True)] == [L])
    check("a JSON argv is read", [v for _l, v, _w in LP.json_sites(json.dumps({"a": [["/x/claude_bounded.sh", "--bg", "--resume", "i"]]}))] == [L]
          and [v for _l, v, _w in LP.json_sites(json.dumps({"a": [["/x/claude_bounded.sh", "--bg", F]]}))] == [S])

    check("a message and a docstring are not launches",
          py('"""claude -p --model opus "x" """\nraise E("claude -p timed out after 3s")\nh = "pinned judge model (claude --model)"') == [])


def t_a_closed_tool_list_is_its_own_answer():
    check("a closed --tools list reads WALLED", py('run(["claude", "-p", q, "--tools", ""])') == [W])
    check("auth status and /usage are no session", py('run(["claude", "auth", "status"])\nrun(["claude", "-p", "/usage"])') == [N, N])


def t_a_route_it_cannot_read_is_named():
    with tempfile.TemporaryDirectory() as d:
        def put(p, t):
            os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
            with open(os.path.join(d, p), "w", encoding="utf-8") as f:
                f.write(t)
        put("src/a.py", 'import shutil\nX = shutil.which("claude")\ngo(X)\n')
        put("src/b.py", 'def broken(:\n  X = which("claude")\n')
        put("src/c.py", 'run(["claude", "-p", q])\n')
        put("src/selftest_c.py", 'run(["claude", "-p", q])\n')
        put("design/x.py", 'run(["claude", "-p", q])\n')
        subprocess.run(["git", "init", "-q", d], check=True, timeout=60)
        subprocess.run(["git", "-C", d, "add", "."], check=True, timeout=60)
        rows = LP.scan(d)
        got = {p: v for p, _l, v, _w in rows}
        check("a file that names the program with no readable launch is COULD NOT LOOK, never clean",
              got.get("src/a.py") == LP.BLIND, rows)
        check("a file that does not parse is COULD NOT LOOK", got.get("src/b.py") == LP.BLIND, rows)
        check("a planted launch in a tree is found; selftests and design records are not launches",
              got.get("src/c.py") == L and "src/selftest_c.py" not in got and "design/x.py" not in got, rows)
        with contextlib.redirect_stdout(io.StringIO()) as o:
            rc = LP.main(["repo", "--root", d])
        check("an exception that excuses nothing is red", set(LP.EXCEPTIONS) <= {r[0] for r in rows if r[2] == L}, rows)
    check("the command exits 1 and names the file", rc == 1 and "src/c.py" in o.getvalue(), (rc, o.getvalue()))
    check("exit: lacks 1, could not look 3, all good 0", (LP.code([S, L, LP.BLIND]), LP.code([S, LP.BLIND]), LP.code([S, W])) == (1, 3, 0))


def t_an_exception_carries_its_reason():
    check("each exception and each file set aside says why", all(len(w) > 10 for w in list(LP.EXCEPTIONS.values()) + list(LP.NO_LAUNCH.values())))
    rows = scanned()
    check("the exceptions of today excuse a real launch", set(LP.EXCEPTIONS) <= {r[0] for r in rows if r[2] == LP.EXCEPTION}, rows)
    # an exception that excuses nothing is red: checked on the planted tree of t_a_route_it_cannot_read_is_named, which holds none


def t_installed_and_running():
    GOOD = json.dumps({"permissions": {"defaultMode": "bypassPermissions"}, "skipDangerousModePermissionPrompt": True})


    def host(**k):
        return [r[2] for r in LP.judge_host("H", dict({"settings": GOOD, "procs": [], "fleet": None, "wt": []}, **k))]


    check("settings with no default mode is red", host(settings="{}") == [L])
    check("settings whose first start asks is red", host(settings='{"permissions":{"defaultMode":"bypassPermissions"}}') == [L])
    check("a running session with no flag is covered by the settings, and red without them",
          host(procs=[["/x/claude", "--name", "a"]]) == [S, S] and host(settings="{}", procs=[["/x/claude", "--name", "a"]]) == [L, L])
    check("the deployed fleet file is read", host(fleet=OLD_FLEET) == [S, L, L] and host(fleet=NEW) == [S, S, S])
    check("a fleet file with no readable launch is COULD NOT LOOK", host(fleet="nothing") == [S, LP.BLIND])
    WT = json.dumps({"profiles": {"list": [{"name": "A", "commandline": "wsl.exe -- bash -lc \"/h/claude_bounded.sh --name 'A'\""},
                                           {"name": "B", "commandline": "wsl.exe"}]}})
    check("a Terminal profile without the flag is red", host(wt=[["f", WT]]) == [S, L] and host(wt=[["f", WT.replace("--name", F + " --name")]]) == [S, S])
    check("an unreadable Terminal file is COULD NOT LOOK", host(wt=[["f", None]]) == [S, LP.BLIND])


    def dead(h, s):
        if s:
            raise OSError("exit 255: no route")
        return {"settings": GOOD, "procs": [], "fleet": None, "wt": []}


    rows = LP.live(probe=dead)
    check("a machine that does not answer is COULD NOT LOOK by name, and the Macs read NOT CHECKED",
          ("SteveDesktop", LP.BLIND) in [(r[0], r[2]) for r in rows] and LP.code([r[2] for r in rows]) == 3
          and sum(r[2] == "NOT CHECKED" and r[0].startswith("Mac") for r in rows) == 2, rows)
    with tempfile.TemporaryDirectory() as d:
        real, LP.live = LP.live, lambda: rows
        try:
            p = os.path.join(d, "r.json")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = LP.main(["live", "--reading", p])
            check("the promised reading does not move on a look that failed", rc == 3 and not os.path.exists(p)
                  and os.path.exists(p[:-5] + "_failed.json"), os.listdir(d))
        finally:
            LP.live = real


def t_the_one_launcher_adds_a_forgotten_flag():
    with tempfile.TemporaryDirectory() as d:
        for n, body in (("claude", '#!/bin/sh\nprintf "%s\\n" "$@"\n'), ("systemd-run", "#!/bin/sh\nexit 1\n"),
                        ("systemctl", "#!/bin/sh\nexit 0\n"), ("sleep", "#!/bin/sh\nexit 0\n")):
            with open(os.path.join(d, n), "w") as f:
                f.write(body)
            os.chmod(os.path.join(d, n), stat.S_IRWXU)

        def bounded(*a):
            r = subprocess.run(["bash", os.path.join(HERE, "claude_bounded.sh"), *a], capture_output=True, text=True, timeout=60,
                               stdin=subprocess.DEVNULL, env=dict(os.environ, PATH=d + ":" + os.environ["PATH"], HOME=d,
                                                                  SEAT_TMP_ROOT=d + "/t", XDG_CONFIG_HOME=d + "/c"))
            return r.stdout.split("\n")[:-1]
        EFF = ["--effort", "high"]      # claude_bounded also adds the effort table's level (selftest_effort_ladder.py)
        check("claude_bounded adds a forgotten flag", bounded("-p", "go now") == EFF + [F, "-p", "go now"], bounded("-p", "go now"))
        check("claude_bounded leaves the caller's flag alone", bounded("-p", "x", F) == EFF + ["-p", "x", F])
        check("claude_bounded leaves a closed tool list walled", bounded("-p", "--tools", "", "x") == EFF + ["-p", "--tools", "", "x"])
        check("claude_bounded gives remote-control its own form", bounded("remote-control", "--name", "S") ==
              ["remote-control", "--permission-mode", "bypassPermissions", "--name", "S"], bounded("remote-control", "--name", "S"))
        check("claude_bounded adds nothing to auth", bounded("auth", "status") == ["auth", "status"])
        check("claude_bounded with no argument skips too", bounded() == EFF + [F], bounded())


def t_every_launch_specification_in_this_tree():
    rows = scanned()
    bad = ["%s:%s %s %s" % r for r in rows if r[2] in (L, LP.BLIND)]
    check("every launch specification in this repo skips permissions (fix: add %s to the line named)" % F, not bad, bad)
    seen = {p for p, _l, v, _w in rows if v in (S, W)}
    KNOWN = {"infrastructure/stevedesktop/claude_session.sh"} | {"src/RimMandrake/" + x for x in (
        "Utils/install_wt_seat_profiles.py", "Utils/findings_judge.sh", "Utils/testq/steward.py", "rimflow/detached_helper.py",
        "rimflow/role_launch.py", "rimflow/seat_restart.py", "rimflow/dispatcher.py", "rimflow/coverage_judge.py",
        "rimflow/designer_cleanse.py", "rimflow/item_exam.py")}
    check("the reader sees each route known on 2026-11-23 (a reader gone blind is red)", KNOWN <= seen, KNOWN - seen)
    path = "src/RimMandrake/Utils/install_wt_seat_profiles.py"
    with open(os.path.join(LP.ROOT, path), encoding="utf-8") as f:
        src = f.read()
    at = src[:src.index("SERVER_CMD = (")].count("\n") + 1
    check("the Windows Terminal Server template is read (its fragment starts with a space)",
          (at, S) in {(l, v) for l, v, _w in LP.Py(src, path).sites()})
    mut = src.replace("--permission-mode bypassPermissions\"", "--permission-mode default\"", 1)
    check("that template alone changed to default reads LACKS", (at, L) in {(l, v) for l, v, _w in LP.Py(mut, path).sites()})

    root = LP.ROOT
    for p in sorted({r[0] for r in rows if r[2] == S}):
        with open(os.path.join(root, p), encoding="utf-8") as f:
            mut = f.read().replace(F, "--verbose").replace("--permission-mode bypass", "--x bypass")
        vs = [v for _l, v, _w in (LP.Py(mut, p).sites() if p.endswith(".py") else LP.shell_sites(mut))]
        check("with its flag taken out, %s is red" % p, S not in vs and L in vs, vs)


def main():
    for t in (t_a_launch_without_the_flag_is_red, t_a_closed_tool_list_is_its_own_answer, t_a_route_it_cannot_read_is_named,
              t_an_exception_carries_its_reason, t_installed_and_running, t_the_one_launcher_adds_a_forgotten_flag,
              t_every_launch_specification_in_this_tree):
        t()
    print("%s: %d failed" % ("RED" if BAD else "GREEN", len(BAD)))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
