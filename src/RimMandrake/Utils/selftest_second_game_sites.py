#!/usr/bin/env python3
"""selftest_second_game_sites.py - each tool that used to pick "the" game acts only on its own, beside a second one.

Two fake games and shims on PATH (fake_two_games.py). A tool that drives a window or owns a hard-wired powershell path is
tested on the script it builds and never run: a focus script must not reach a real desktop from a selftest.
GI_ONLY=picks,any runs some (selftest_second_game_mutants.py uses it).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import fake_two_games as F  # noqa: E402

FAILS = []
BY_NAME = "Get-Process RimWorldWin64"


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def picks(w):
    builders = {"belt_watchdog": "import belt_watchdog as M; print(M.probe_script())",
                "focus_heal": "import focus_heal as M; print(M.get_rw_script())",
                "game_focus": "import game_focus as M; print(M.focus_script())",
                "planet_atmosphere_cost": "import planet_atmosphere_cost as M; print(M.sample_script())"}
    for name, code in builders.items():
        for inst, mine, other in ((None, "a", "b"), ("b", "b", "a")):
            pids = {"a": w.start_a(), "b": w.start_b()}
            r = w.py(code, instance=inst)
            check("Get-Process -Id %d " % pids[mine] in r.stdout and "Get-Process -Id %d " % pids[other] not in r.stdout
                  and BY_NAME not in r.stdout, "%s under %s picks %s by pid: %s" % (name, inst, mine, r.stderr[-160:]))
            w.clear()
            w.start_b() if mine == "a" else w.start_a()
            r = w.py(code, instance=inst)
            check("$p = @()" in r.stdout and "Get-Process -Id" not in r.stdout, "%s under %s with only the other game up sees no game" % (name, inst))
            w.clear()
        w.start_a()
        r = w.py(code, FAKE_PS_MODE="fail")
        check(r.returncode != 0 and "Blind" in r.stderr, "%s when blind raises, never 'no game'" % name)
        w.clear()

    code = "import belt_watchdog as M; print(json.dumps(M.probe_windows()))".replace("print(", "import json; print(", 1)
    a, b = w.start_a(), w.start_b()
    r = w.py(code, instance="b", FAKE_PS_PROCESS_REPLY='{"game": {"pid": 1}, "games": []}')
    scripts = " ".join(w.log_lines("PS "))
    check('"game"' in r.stdout and "$o.games = @(Get-Process -Id %d " % b in scripts and BY_NAME not in scripts,
          "belt_watchdog lists only its own game as 'games': %s" % r.stderr[-160:])
    w.clear()

    a, b = w.start_a(), w.start_b()
    r = w.py("import coldstart_crashes as M; print(M.process_start())", instance="b", FAKE_PS_PROCESS_REPLY="2026-11-07T00:00:00.0000000Z")
    scripts = " ".join(w.log_lines("PS "))
    check("Get-Process -Id %d " % b in scripts and BY_NAME not in scripts and r.stdout.split()[-1:] != ["None"],
          "coldstart_crashes reads its own game's start: %s %s" % (r.stdout[-60:], r.stderr[-120:]))
    r = w.py("import coldstart_crashes as M; print(M.process_start())", FAKE_PS_MODE="fail")
    check("UNMEASURED" in r.stdout and r.returncode == 0, "coldstart_crashes when blind says UNMEASURED")
    w.clear()

    code = "import sys; sys.path.insert(0, 'src/RimMandrake/Utils/testq'); import archmagi_phases as M; print(repr(M.game_pid()))"
    a, b = w.start_a(), w.start_b()
    check(w.py(code, cwd=w.repo).stdout.strip() == repr(str(a)), "archmagi_phases.game_pid, nothing set, is game a's")
    check(w.py(code, cwd=w.repo, instance="b").stdout.strip() == repr(str(b)), "archmagi_phases.game_pid under b is b's")
    check(w.py(code, cwd=w.repo, FAKE_PS_MODE="fail").stdout.strip() == "None", "archmagi_phases.game_pid blind is None, never ''")
    w.clear()


def any_game(w):
    rows = [("modset_builder.game_running", "import modset_builder as M; print(M.game_running())"),
            ("load_policy.game_alive", "import load_policy as M; print(M.game_alive())"),
            ("preflight_bridge.win_processes", "import preflight_bridge as M; print(bool(M.win_processes()))")]
    for name, code in rows:
        for inst, mine, other in ((None, "a", "b"), ("b", "b", "a")):
            w.start_b() if other == "b" else w.start_a()
            r = w.py(code, instance=inst)
            check(r.stdout.strip().endswith("False"), "%s under %s: only the other game up reads as down: %s %s" % (name, inst, r.stdout[-40:], r.stderr[-160:]))
            w.start_a() if mine == "a" else w.start_b()
            r = w.py(code, instance=inst)
            check(r.stdout.strip().endswith("True"), "%s under %s: its own game up reads as up" % (name, inst))
            w.clear()
    w.start_a()
    r = w.py("import modset_builder as M; print(M.game_running())", FAKE_PS_MODE="fail")
    check(r.stdout.strip().endswith("True") and "assuming it is live" in r.stderr, "modset_builder when blind assumes live: %s" % r.stderr[-120:])
    check(w.py("import load_policy as M; print(M.game_alive())", FAKE_PS_MODE="fail").stdout.strip() == "None", "load_policy when blind is UNKNOWN")
    check(w.py("import preflight_bridge as M; print(M.win_processes())", FAKE_PS_MODE="fail").stdout.strip() == "None", "preflight when blind is None")
    w.clear()
    # a deploy writes the one Mods folder both games load, so these two stay on ANY game: the shim's tasklist sees either
    for rel, fn in (("src/RimMandrake/Utils/art/enact.py", "enact"), ("src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py", "prep_wsl")):
        text = open(os.path.join(w.repo, rel), encoding="utf-8").read()
        check("IMAGENAME eq RimWorldWin64.exe" in text and "ANY game on this machine" in text, "%s keeps its any-game check, on purpose" % fn)


def launches(w):
    code = ("import sys; sys.path.insert(0, 'src/RimMandrake/bridgetools'); import launch_ready as L; "
            "pol = dict(kill_existing_grace_s=20, launch_to_process_s=20, late_arrival_watch_s=2, process_to_bridge_warn_s=30, "
            "process_to_bridge_deadline_s=30, bridge_to_dispatcher_s=10, name='t'); "
            "r = L.run(L.RealEnv(), pol); print('VERDICT', r['verdict'], r.get('why'), r.get('port'), r.get('pid'))")
    # game a up, launch b beside it: step 1's kill must not see a
    a = w.start_a()
    r = w.py(code, instance="b", cwd=w.repo, timeout=120)
    line = [ln for ln in r.stdout.splitlines() if ln.startswith("VERDICT")]
    b = w.gi("pid", "b").stdout.strip()
    check(line and line[0].startswith("VERDICT READY") and " 5175 " in line[0], "launch_ready under b comes up READY on the port line: %s %s" % (line, r.stderr[-200:]))
    check(F.alive(a) and w.kills() == [], "launch_ready under b left game a alone: %s" % w.kills())
    check(any("Start-Process" in ln for ln in w.log_lines("START")) and not w.log_lines("cmd "), "launch_ready under b never touched steam://")
    # b up, a's launch_ready replaces only a
    r = w.py(code, cwd=w.repo, timeout=120)
    check(F.wait_dead(a) and F.alive(int(b)), "launch_ready, nothing set, stops only game a: %s" % r.stdout[-120:])
    check(any("steam://rungameid/294100" in ln for ln in w.log_lines("cmd ")), "launch_ready, nothing set, launches through Steam as before")
    w.clear()

    code = ("import load_policy, sys; sys.path.insert(0, %r); import live_session as L; L.time.sleep = lambda s: None; "
            "L.logwait = None; L.launch_and_wait(budget=60); print('UP')" % os.path.join(w.repo, "src/RimMandrake/Utils/northstar_driver"))
    a = w.start_a()
    r = w.py(code, instance="b", timeout=120)
    check("UP" in r.stdout and F.alive(a) and not w.log_lines("cmd ") and w.gi("pid", "b").stdout.strip().isdigit(),
          "live_session launch under b starts b directly and sees its port line: %s %s" % (r.stdout[-80:], r.stderr[-200:]))
    check(not [ln for ln in w.log_lines("PS ") if "steam://" in ln], "live_session under b never touched steam://")
    w.clear()
    code = ("import relentless_stage as S; print(S.Ops({'item': 'X', 'gen': 1}).launch()[0])")
    a = w.start_a()
    r = w.py(code, instance="b", timeout=60)
    scripts = " ".join(w.log_lines("PS "))
    check(r.stdout.strip() == "0" and w.gi("pid", "b").stdout.strip().isdigit() and "steam://" not in scripts, "relentless Ops.launch under b starts b directly: %s" % r.stderr[-160:])
    w.clear()
    r = w.py(code, timeout=60)
    check("steam://rungameid/294100" in " ".join(w.log_lines("PS ")) and not w.gi("pid", "b").stdout.strip(), "relentless Ops.launch, nothing set, goes through Steam as before")
    w.clear()
    text = open(os.path.join(w.repo, "src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py"), encoding="utf-8").read()
    check("game_instance.py launch" in text and text.index("game_instance.py launch") < text.index("next: launch through Steam"), "prep_wsl tells a named game its own launch")


def ready_lines(w):
    PORT = "[RimBridge] GABP server connected to GABS on port 5175\n"
    TOKEN = "[RimBridge] GABP server running standalone on port 5174\n[RimBridge] Bridge token: AAA\n"
    d = tempfile.mkdtemp(dir=w.tmp)
    p = os.path.join(d, "Player.log")
    code = ("import logwait as W; c = W.LogCursor(%r); open(%r, 'a').write(%r); print(bool(c.poll(%r)))")
    open(p, "w").write("old session\n")
    check(w.py(code % (p, p, PORT, "Bridge token:")).stdout.strip() == "True", "logwait: a wait for 'Bridge token:' takes the port line")
    check(w.py(code % (p, p, TOKEN, "Bridge token:")).stdout.strip() == "True", "logwait: and still the token line")
    check(w.py(code % (p, p, PORT, "Some other text")).stdout.strip() == "False", "logwait: no other literal is widened")
    open(p, "w").write(PORT)
    check(w.py("import logwait as W; c = W.LogCursor(%r); print(bool(c.poll('Bridge token:')))" % p).stdout.strip() == "False", "logwait: the old session's port line does not count")

    code = "import sys; sys.path.insert(0, 'src/RimMandrake/Utils/modcheck'); import launch_gate as G; r = G.scan(%r); print(r['ok'], r['probe'])"
    check(w.py(code % PORT, cwd=w.repo).stdout.strip() == "True True", "launch_gate: the port line is proof the log is current")
    check(w.py(code % "nothing here\n", cwd=w.repo).stdout.strip() == "False False", "launch_gate: no bridge line is still UNMEASURED")

    code = "import sys; sys.path.insert(0, 'src/RimMandrake/bridgetools'); import launch_ready as L; print(L._token(%r), L._port(%r))"
    check(w.py(code % (PORT, PORT), cwd=w.repo, GABP_TOKEN="ENVTOK").stdout.strip() == "ENVTOK 5175", "launch_ready: the port line reads with the given token")
    check(w.py(code % (TOKEN, TOKEN), cwd=w.repo, GABP_TOKEN="ENVTOK").stdout.strip() == "AAA 5174", "launch_ready: a token line still wins")
    check(w.py(code % (PORT, PORT), cwd=w.repo).stdout.strip() == "None 5175", "launch_ready, game a: a port line with no token given is not ready")

    os.makedirs(w.b_dir, exist_ok=True)
    w.gi("env", "b")
    with open(os.path.join(w.b_dir, "Player.log"), "w") as f:
        f.write(PORT)
    b = w.start_b()
    code = "import preflight_bridge as M; ctx = {'procs': [(%d, None)]}; print(vars(M.c_live_identity(ctx)))" % b
    r = w.py(code, instance="b")
    check("listening on 5175" in r.stdout, "preflight c_live_identity passes on the port line: %s %s" % (r.stdout[-120:], r.stderr[-120:]))
    w.clear()


def endpoint(w):
    with open(os.path.join(w.a_dir, "Player.log"), "w") as f:
        f.write("[RimBridge] GABP server running standalone on port 5174\n[RimBridge] Bridge token: AAA\n")
    code = "import rimbridge_client as R; print(R.resolve_endpoint()[1:])"
    code_cli = "import rimbridge_client as R; print(R.resolve_endpoint(port=9, token='CLI')[1:])"
    check(w.py(code).stdout.strip() == "(5174, 'AAA')", "nothing set: game a's log, as before")
    if os.path.exists(os.path.join(w.b_dir, "bridge_token.txt")):
        os.remove(os.path.join(w.b_dir, "bridge_token.txt"))
    r = w.py(code, instance="b")
    check(r.stdout.strip() == "(5175, '')", "b with no token yet: port 5175 and no token, never a's: %s %s" % (r.stdout, r.stderr[-160:]))
    w.gi("env", "b")
    token = open(os.path.join(w.b_dir, "bridge_token.txt")).read()
    check(w.py(code, instance="b").stdout.strip() == "(5175, %r)" % token, "b: its own port and token, with game a's log right there")
    check(w.py(code, instance="b", GABP_SERVER_PORT="6000", GABP_TOKEN="E").stdout.strip() == "(6000, 'E')", "the environment pair still beats the name")
    check(w.py(code_cli, instance="b").stdout.strip() == "(9, 'CLI')", "an explicit argument still beats everything")
    check(w.py("import rimbridge_client as R; print(R.DEFAULT_PLAYER_LOG)", instance="b").stdout.strip() == os.path.join(w.b_dir, "Player.log"),
          "b's log is the only log looked at")


SECTIONS = {"picks": picks, "any": any_game, "launches": launches, "ready": ready_lines, "endpoint": endpoint}


def main():
    only = [s for s in os.environ.get("GI_ONLY", "").split(",") if s]
    w = F.World(F.REPO)
    try:
        for name, fn in SECTIONS.items():
            if not only or name in only:
                print("-- " + name)
                fn(w)
                w.clear()
    finally:
        w.close()
    print("%s selftest_second_game_sites: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
