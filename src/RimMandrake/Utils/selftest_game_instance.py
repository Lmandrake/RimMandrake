#!/usr/bin/env python3
"""selftest_game_instance.py - two fake games on one machine: stop one by pid, the other lives (fake_two_games.py).

Sections run by name; GI_ONLY=stop,sites runs some (selftest_second_game_mutants.py uses it). No game, no Windows.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import fake_two_games as F  # noqa: E402
import game_instance as G  # noqa: E402

FAILS = []
SHELL_SITES = {"src/RimMandrake/Utils/loadsweep/biome_load_proof.sh": ("REPO", "."),
               "src/RimMandrake/Utils/loadsweep/sweep_load.sh": ("DIR", "src/RimMandrake/Utils/loadsweep"),
               "src/RimMandrake/Utils/rimbench/gl_sheet_run.sh": ("REPO", ".")}


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def stdout(r):
    return r.stdout.strip()


def names(w):
    check(G.check_name("B") == "b" and G.port("a") == 5174 and G.port("b") == 5175 and G.port("c") == 5176, "port is 5174 plus the index")
    for bad in ("bb", "1", "b.", "a b"):
        try:
            G.check_name(bad)
            check(False, "bad name %r refused" % bad)
        except G.InstanceError:
            check(True, "bad name %r refused" % bad)
    check(w.gi("env").stdout == "" and w.gi("env", "a").stdout == "", "game a's environment is nothing at all")
    r = w.gi("pid", instance="bb")
    check(r.returncode == G.EX_REFUSED and "bad game instance" in r.stderr, "a typo'd RM_GAME_INSTANCE refuses by name, never game a")
    e = dict(re.findall(r"export (\w+)='?([^'\n]*)'?", w.gi("env", "b").stdout))
    token = open(os.path.join(w.b_dir, "bridge_token.txt")).read()
    check(e.get("RM_GAME_INSTANCE") == "b" and e.get("RM_GAME_USERDATA") == w.b_dir and e.get("RM_GAME_LOGDIR") == w.b_dir
          and e.get("GABP_SERVER_PORT") == "5175" and e.get("GABP_TOKEN") == token and token
          and e.get("RIMFLOW_DRIVER_LOCK") == os.path.join(w.b_dir, "DRIVER_LOCK.json"), "game b's environment: %s" % sorted(e))
    for v in ("RM_GAME_INSTANCE", "GABP_TOKEN", "GABP_SERVER_PORT", "RM_GAME_USERDATA/p", "RM_GAME_LOGDIR/p", "RIMFLOW_DRIVER_LOCK/p"):
        check(v in e.get("WSLENV", "").split(":"), "%s crosses to Windows python" % v)
    check(w.gi("env", "b", WSLENV="X/p").stdout.count("X/p") == 1, "an existing WSLENV is kept")
    e2 = dict(re.findall(r"export (\w+)='?([^'\n]*)'?", w.gi("env", "b").stdout))
    check(e2.get("GABP_TOKEN") == token, "the token is kept, so a loop's environment survives a game restart")


def owners():
    table = {r'"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe" -disable-compute-shaders': "a",
             r'D:\SteamLibrary\steamapps\common\RimWorld\RimWorldWin64.exe': "a",
             r'x.exe -savedatafolder=D:\ClaudeWork\rimmandrake\instances\b -logfile D:\y\Player.log': "b",
             r'x.exe "-savedatafolder=D:\Claude Work\instances\b" -logfile y': "b",
             r'x.exe -savedatafolder="D:\Claude Work\instances\c" -logfile y': "c",
             r'x.exe -savedatafolder=D:/ClaudeWork/INSTANCES/B/': "b",
             r'x.exe -savedatafolder=D:\ClaudeWork\instances\b\ -logfile y': "b",
             r'x.exe -savedatafolder=/tmp/instances/b': "b",
             r'x.exe -savedatafolder=D:\ClaudeWork\instances\bb': "a",
             r'x.exe -savedatafolder=D:\ClaudeWork\instances_trial\b': "a",
             r'x.exe -savedatafolder=D:\DevSaveData': "a",
             r'x.exe -logfile D:\instances\b\Player.log': "a"}
    for cmd, want in table.items():
        check(G.owner(cmd) == want, "owner %s of: %s" % (want, cmd))


def stop(w):
    # the instrument first: this shim's kill by name really takes both, so "the other lives" below can fail
    a, b = w.start_a(), w.start_b()
    w.run(["taskkill.exe", "/F", "/IM", "RimWorldWin64.exe"])
    check(F.wait_dead(a) and F.wait_dead(b), "control: taskkill /IM takes both fake games")
    w.clear()

    a, b = w.start_a(), w.start_b()
    check(stdout(w.gi("pid")) == str(a), "pid: nothing set is game a")
    check(stdout(w.gi("pid", "b")) == str(b) and stdout(w.gi("pid", instance="b")) == str(b), "pid b, by argument and by environment")
    r = w.gi("stop", str(b), "--instance", "b")
    check(r.returncode == 0 and F.wait_dead(b), "stop b's pid: b is gone")
    check(F.alive(a), "stop b's pid: a lives")
    check(w.kills() == ["taskkill /PID %d" % b], "the only signal sent was /PID b: %s" % w.kills())
    check(stdout(w.gi("pid", "b")) == "" and w.gi("pid", "b").returncode == 0, "pid b is empty once it stopped")
    w.clear()

    a, b = w.start_a(), w.start_b()
    r = w.gi("stop", str(a))
    check(r.returncode == 0 and F.wait_dead(a), "stop a's pid, nothing set: a is gone")
    check(F.alive(b), "stop a's pid: b lives")
    w.clear()

    a, b = w.start_a(), w.start_b()
    r = w.gi("stop", instance="b")
    check(r.returncode == 0 and F.wait_dead(b) and F.alive(a), "stop with no pid under RM_GAME_INSTANCE=b takes b alone")
    r = w.gi("stop")
    check(r.returncode == 0 and F.wait_dead(a), "stop with no pid, nothing set, takes a")
    check(w.gi("stop").returncode == 0 and "not running" in w.gi("stop").stdout, "stopping a stopped game is fine, and says so")
    w.clear()

    a, b = w.start_a(), w.start_b()
    r = w.gi("stop", str(a), "--instance", "b")
    check(r.returncode == G.EX_REFUSED and "not game b's" in r.stderr and F.alive(a), "b cannot stop a's pid: refused, a lives")
    check(w.kills() == [], "the refused stop sent nothing")
    r = w.gi("stop", str(b))
    check(r.returncode == G.EX_REFUSED and F.alive(b), "a cannot stop b's pid: refused, b lives")
    r = w.gi("stop", "999999")
    check(r.returncode == G.EX_REFUSED and F.alive(a) and F.alive(b), "a pid that is no game: refused")
    w.clear()

    a = w.start("--ignore-term", "-disable-compute-shaders")
    b = w.start_b()
    r = w.gi("stop")
    check(not F.wait_dead(a, 0.5) and F.alive(b), "a graceful stop is graceful: a game that ignores it stays up")
    w.gi("stop", str(a), "--force")
    check(F.wait_dead(a) and F.alive(b), "--force takes that pid, and b lives")
    w.clear()


def blind(w):
    a, b = w.start_a(), w.start_b()
    for mode in ("fail", "silent"):
        for args in (("pid",), ("stop",), ("stop", str(b), "--instance", "b"), ("status",)):
            r = w.gi(*args, FAKE_PS_MODE=mode)
            check(r.returncode == G.EX_BLIND and "BLIND" in r.stderr, "%s, %s: BLIND, never 'no game' (exit %d)" % (mode, args, r.returncode))
    r = w.gi("stop", FAKE_PS_MODE="unreadable")
    check(r.returncode == G.EX_BLIND and "command line" in r.stderr, "a command line that cannot be read: stop refuses by name")
    check(F.alive(a) and F.alive(b) and w.kills() == [], "nothing was signalled while blind: %s" % w.kills())
    r = w.py("import game_instance as G; print(G.running()); print(G.running('b')); print(G.running('c'))", FAKE_PS_MODE="unreadable")
    check(r.stdout.split() == ["True", "True", "True"], "running() counts an unattributable game as up: %s" % r.stdout.split())
    w.clear()
    r = w.py("import game_instance as G; print(G.running()); print(G.games())")
    check(r.stdout.split() == ["False", "[]"], "no game at all is a measured no: %s %s" % (r.stdout.split(), r.stderr[-200:]))


def paths(w):
    code = "import game_paths as P; print(P.MODS_CONFIG); print(P.PLAYER_LOG); print(P.SAVES)"
    r = w.py(code)
    check(r.stdout.split()[0].replace("\\", "/") == os.path.join(w.a_dir, "Config/ModsConfig.xml"), "nothing set: game_paths follows its environment as before")
    r = w.py(code, instance="b")
    out = r.stdout.replace("\\", "/").split()
    check(out and out[0] == os.path.join(w.b_dir, "Config/ModsConfig.xml") and out[1] == os.path.join(w.b_dir, "Player.log"),
          "RM_GAME_INSTANCE=b beats game a's exported folders: %s %s" % (out, r.stderr[-200:]))
    r = w.py("import game_paths", instance="bb")
    check(r.returncode != 0 and "bad game instance" in r.stderr, "a typo'd instance stops game_paths by name, never game a's folders")
    r = w.py("import sys, game_paths; print('game_instance' in sys.modules)")
    check(r.stdout.split() == ["False"], "nothing set imports nothing new into game_paths")


def launch(w):
    a = w.start_a()
    r = w.gi("launch", "a")
    check(r.returncode == G.EX_REFUSED and "keeps its own launch" in r.stderr, "launch refuses game a")
    r = w.gi("launch")
    check(r.returncode == G.EX_REFUSED, "launch with nothing set refuses too")
    r = w.gi("launch", "b", FAKE_NO_STEAM="1")
    check(r.returncode == G.EX_REFUSED and "Steam is not running" in r.stderr, "no Steam: refused by name")
    appid = os.path.join(w.game_dir, "steam_appid.txt")
    os.rename(appid, appid + ".away")
    r = w.gi("launch", "b")
    check(r.returncode == G.EX_REFUSED and "steam_appid.txt" in r.stderr, "no steam_appid.txt (Archmagi's folder): refused")
    os.rename(appid + ".away", appid)

    a_cfg = os.path.join(w.a_dir, "Config", "ModsConfig.xml")
    open(a_cfg, "w").write("game a's list")
    waited = "import game_instance as G; rc, t = G.launch('b', wait=True, wait_s=%d); print(t); print('RC', rc)"
    r = w.py(waited % 20)
    b = stdout(w.gi("pid", "b"))
    check("RC 0" in r.stdout and "bridge on port 5175" in r.stdout and b.isdigit(), "launch b --wait reads the port line: %s %s" % (r.stdout, r.stderr[-200:]))
    saw = w.saw()
    token = open(os.path.join(w.b_dir, "bridge_token.txt")).read()
    check(saw["port"] == "5175" and saw["token"] == token, "the game got the port and the token that were written")
    argv = saw["argv"]
    check(argv[0] == "-savedatafolder=" + w.b_dir and argv[argv.index("-logfile") + 1].replace("\\", "/") == w.b_dir + "/Player.log"
          and argv[argv.index("-screen-fullscreen") + 1] == "0" and argv[argv.index("-screen-width") + 1] == "1280", "command line: %s" % argv)
    prefs = open(os.path.join(w.b_dir, "Config", "Prefs.xml"), encoding="utf-8").read()
    check("<screenWidth>1280</screenWidth>" in prefs and "<screenHeight>720</screenHeight>" in prefs
          and "<fullscreen>False</fullscreen>" in prefs and "<runInBackground>True</runInBackground>" in prefs, "Prefs carries the window size")
    check(os.path.exists(os.path.join(w.b_dir, "Config", "ModsConfig.xml"))
          and '"test"' in open(os.path.join(w.b_dir, "JawaBench", "companion_profile.json")).read(), "seeded with A up: list and test profile")
    check(F.alive(a) and open(a_cfg).read() == "game a's list" and w.kills() == [], "game a is untouched by b's launch")
    r = w.gi("launch", "b")
    check(r.returncode == 0 and "already running" in r.stdout and stdout(w.gi("pid", "b")) == b, "a second launch does not start a second b")
    r = w.gi("prepare", "b")
    check(r.returncode == G.EX_REFUSED and "rewrites Prefs" in r.stderr, "prepare refuses while its own game runs")
    w.gi("stop", b, "--instance", "b")
    F.wait_dead(int(b))

    path = os.path.join(w.b_dir, "Config", "Prefs.xml")
    open(path, "w", encoding="utf-8").write(prefs.replace("<screenWidth>1280", "<screenWidth>1600"))
    w.gi("prepare", "b")
    check("<screenWidth>1600</screenWidth>" in open(path, encoding="utf-8").read(), "a size already there is kept")
    open(os.path.join(w.b_dir, "Player.log"), "w").write("old run\n")
    r = w.gi("launch", "b", "--wait")
    prev = os.path.join(w.b_dir, "Player.log.prev")
    check(r.returncode == 0 and os.path.exists(prev) and "old run" in open(prev).read(), "the old log is moved aside, not overwritten: %s" % r.stdout)
    w.gi("stop", "--instance", "b")
    F.wait_dead(int(stdout(w.gi("pid", "b")) or 0) or 1, 0.2)
    w.clear()
    a = w.start_a()
    r = w.py(waited % 3, FAKE_GAME_PORT="5174")
    check("RC 1" in r.stdout and "no port line" in r.stdout, "a port line naming the wrong port is not this game's: %s" % r.stdout[-120:])
    w.clear()


def rw_game(w):
    sh = os.path.join(w.repo, "infrastructure/stevedesktop/rw_game.sh")
    a, b = w.start_a(), w.start_b()
    with open(os.path.join(w.a_dir, "Player.log"), "w") as f:
        f.write("[RimBridge] GABP server running standalone on port 5174\n")
    with open(os.path.join(w.b_dir, "Player.log"), "w") as f:
        f.write("[RimBridge] GABP server connected to GABS on port 5175\n")
    r = w.run([sh, "status"], instance="b", RW_GAME_GUARDED="1")
    check(r.returncode == 0 and "running pid=PROCESS %d" % b in r.stdout and "Player.log: 5175" in r.stdout, "status under b reads b, and b's log: %s %s" % (r.stdout[:160], r.stderr[-100:]))
    r = w.run([sh, "status"], RW_GAME_GUARDED="1")
    check(r.returncode == 0 and "running pid=PROCESS %d" % a in r.stdout and "Player.log: 5174" in r.stdout, "status, nothing set, reads a and a's log")
    r = w.run([sh, "init"], instance="b", RW_GAME_GUARDED="1")
    check(r.returncode == G.EX_REFUSED, "init under b, with b up, refuses for b's own reason: %s %s" % (r.stdout, r.stderr[-120:]))
    r = w.run([sh, "down"], instance="b", RW_GAME_GUARDED="1", timeout=120)
    check(r.returncode == 0 and "stopped (graceful)" in r.stdout and F.wait_dead(b), "down under b stops b: %s" % r.stdout)
    check(F.alive(a), "down under b: a lives")
    check(w.kills() == ["taskkill /PID %d" % b], "down sent one signal, /PID b: %s" % w.kills())
    r = w.run([sh, "init"], instance="b", RW_GAME_GUARDED="1")
    check(r.returncode == 0 and F.alive(a) and "<screenWidth>" in open(os.path.join(w.b_dir, "Config", "Prefs.xml"), encoding="utf-8").read(),
          "init under b works with a up, and seeds the window size: %s %s" % (r.stdout, r.stderr[-120:]))
    check(not os.path.exists(os.path.join(w.a_dir, "JawaBench")), "init under b wrote nothing in a's folder")
    r = w.run([sh, "up", "--wait"], instance="b", RW_GAME_GUARDED="1")
    b2 = stdout(w.gi("pid", "b"))
    check(r.returncode == 0 and b2.isdigit() and "bridge on port 5175" in r.stdout and F.alive(a), "up --wait under b starts b beside a: %s %s" % (r.stdout, r.stderr[-100:]))
    r = w.run([sh, "down"], RW_GAME_GUARDED="1", timeout=120)
    check(r.returncode == 0 and F.wait_dead(a), "down, nothing set, stops a")
    check(F.alive(int(b2)), "down, nothing set: b lives")
    r = w.run([sh, "down"], RW_GAME_GUARDED="1", FAKE_PS_MODE="fail")
    check(r.returncode == 2 and "could not be read" in r.stdout and F.alive(int(b2)), "down while blind refuses: %s" % r.stdout)
    w.clear()


def sites(w):
    # northstar_driver/live_session.py
    code = ("import sys; sys.path.insert(0, %r); import live_session as L; L.time.sleep = lambda s: None; L.stop_game(); print('DONE')"
            % os.path.join(w.repo, "src/RimMandrake/Utils/northstar_driver"))
    for inst, mine, other in ((None, "a", "b"), ("b", "b", "a")):
        pids = {"a": w.start_a(), "b": w.start_b()}
        r = w.py(code, instance=inst, timeout=150)     # a mutant's wait runs out its 90 s
        check("DONE" in r.stdout and F.wait_dead(pids[mine]), "live_session.stop_game under %s stops %s: %s %s" % (inst, mine, r.stdout[-80:], r.stderr[-200:]))
        check(F.alive(pids[other]), "live_session.stop_game under %s: %s lives" % (inst, other))
        w.clear()

    # rimflow/relentless_stage.py
    code = ("import relentless_stage as S; o = S.Ops({'item': 'X', 'gen': 1}); print(o.running()); r = o.kill(); print(r[0]); "
            "import time; time.sleep(0.3); print(o.running()); print(o.kill(force=True)[0])")
    for inst, mine, other in ((None, "a", "b"), ("b", "b", "a")):
        pids = {"a": w.start_a(), "b": w.start_b()}
        r = w.py(code, instance=inst)
        check(r.stdout.split() == ["True", "0", "False", "0"], "relentless Ops under %s: %s %s" % (inst, r.stdout.split(), r.stderr[-200:]))
        check(F.wait_dead(pids[mine]) and F.alive(pids[other]), "relentless Ops.kill under %s stops %s; %s lives" % (inst, mine, other))
        check(all("/IM" not in k for k in w.kills()), "relentless Ops.kill sends /PID only: %s" % w.kills())
        w.clear()
    r = w.py("import relentless_stage as S\ntry:\n    S.Ops({'item': 'X', 'gen': 1}).running()\nexcept RuntimeError as e:\n    print('RAISED')",
             FAKE_PS_MODE="fail")
    check("RAISED" in r.stdout, "relentless Ops.running when blind raises, never 'down'")

    # the three shell scripts: each kill line, cut out and run, because the rest of them starts the real Steam
    for rel, (var, base) in SHELL_SITES.items():
        text = open(os.path.join(w.repo, rel), encoding="utf-8").read()
        check("taskkill" not in text, "%s has no taskkill of its own" % rel)
        got = [ln.split(";")[0].strip() for ln in text.splitlines() if re.search(r"game_instance\.py.* stop", ln)]
        check(len(got) == 1, "%s has one stop line: %s" % (rel, got))
        script = "%s=%s; %s" % (var, os.path.join(w.repo, base), got[0] if got else "false")
        for inst, mine, other in ((None, "a", "b"), ("b", "b", "a")):
            pids = {"a": w.start_a(), "b": w.start_b()}
            w.run(["bash", "-c", script], instance=inst)
            check(F.wait_dead(pids[mine]) and F.alive(pids[other]), "%s under %s stops %s; %s lives" % (rel, inst, mine, other))
            w.clear()
        # the refusal, cut out and run too: a whole script whose refusal regressed would start the real Steam
        lines = text.splitlines()
        guard = [i for i, ln in enumerate(lines) if "RM_GAME_INSTANCE" in ln and "REFUSED" in ln]
        steam = [i for i, ln in enumerate(lines) if "steam.exe" in ln and not ln.startswith("#")]
        stops = [i for i, ln in enumerate(lines) if "game_instance.py" in ln]
        check(len(guard) == 1 and steam and stops and guard[0] < min(steam + stops), "%s refuses before its stop and its Steam" % rel)
        r = w.run(["bash", "-c", lines[guard[0]] if guard else "true"], instance="b")
        check(r.returncode == 2 and "REFUSED" in r.stdout, "%s refuses a named game, since it launches through Steam" % rel)
        r = w.run(["bash", "-c", lines[guard[0]] if guard else "false"])
        check(r.returncode == 0, "%s runs as before with nothing set" % rel)


OTHER = "CLAUDE_ARCHMAGI_OFFLINE1"      # another seat (RUNNER's bridge events are refused at replay, so not RUNNER)


def bridge(w):
    """RIMMANDRAKE_GUARD_GAME_STOP_BY_BRIDGE_HOLD (GPT review p2.F2): stop asks rimflow's own delegated verdict before
    any signal. Another seat's live hold, his OWNER hold inside his 45 min, or an UNMEASURED reading of him refuses;
    free, ours, stale (45 min) and his hold past his window pass. Real `rimflow bridge idle`, on the fake ledger."""
    refuse = (("another seat's live hold", [(OTHER, 120)], None),
              ("his OWNER hold, 5 min old", [("OWNER", 300)], None),
              ("his OWNER hold past 45 min, his last act UNMEASURED", [("OWNER", 3000)], "unmeasured"),
              ("game b, another seat's live hold on b's bridge", [(OTHER, 120, "archmagi.b")], None))
    allow = (("a free bridge", [], None), ("our own hold", [("BENCH", 120)], None),
             ("another seat's stale hold (46 min)", [(OTHER, 46 * 60)], None),
             ("his OWNER hold 50 min after his last act", [("OWNER", 3000)], None),
             ("game b, a live hold on game a's bridge only", [(OTHER, 120)], None))
    for verdict, cases in (("refuses", refuse), ("allowed", allow)):
        for label, holds, owner in cases:
            inst = "b" if label.startswith("game b") else None
            w.bridge(*holds)
            if owner == "unmeasured":
                os.makedirs(w.env["RIMFLOW_OWNER_ACT_STAMP"])        # an unreadable ./bridge stamp: UNMEASURED
            p = w.start_b() if inst else w.start_a()
            r = w.gi("stop", instance=inst, RM_HOST="archmagi", timeout=120)
            if verdict == "refuses":
                check(r.returncode == G.EX_REFUSED and F.alive(p) and w.kills() == [] and "rimflow bridge" in r.stderr,
                      "stop with %s: refused, nothing sent, and says what would pass: %s %s"
                      % (label, r.returncode, r.stderr.strip()[-300:]))
            else:
                check(r.returncode == 0 and F.wait_dead(p) and w.kills() == ["taskkill /PID %d" % p],
                      "stop with %s: allowed, one /PID: %s %s" % (label, r.returncode, (r.stdout + r.stderr).strip()[-300:]))
            w.clear()
    # an answer that is not rimflow's TAKEABLE is no verdict: nothing is signalled on it
    saved = dict(os.environ)
    os.environ.update(w.env)
    real = G.RIMFLOW_CLI
    try:
        w.bridge()
        G.RIMFLOW_CLI = os.path.join(w.tmp, "no_such_cli.py")
        why = G.bridge_refusal("a")
        check(why is not None and "UNMEASURED" in why, "a rimflow that does not answer refuses, UNMEASURED: %s" % why)
        G.RIMFLOW_CLI = real
        check(G.bridge_refusal("a") is None, "control: the same call with rimflow answering passes a free bridge")
    finally:
        G.RIMFLOW_CLI = real
        os.environ.clear()
        os.environ.update(saved)
    w.bridge()


FAKE_BROADCAST = """import json, os, sys
with open(os.environ["FAKE_BROADCAST_LOG"], "a") as f:
    f.write(json.dumps({"sentence": sys.argv[1:], "why": os.environ.get("RIMFLOW_WHY")}) + "\\n")
"""


def game_idle_ok(w):
    """GPT review p2.F9: `./game --idle-ok` read the report-only `bridge idle` and then announced, so another seat could
    take the bridge in the gap. It must TAKE the bridge (`bridge take --idle-ok`) before it acts, and take nothing for
    a refused gate or a typo'd state. The real ./game and real rimflow, in a tree whose broadcast/modlist/zoom are fakes."""
    import json
    t = os.path.join(w.tmp, "gametree")
    utils = os.path.join(t, "src", "RimMandrake", "Utils")
    os.makedirs(utils)
    os.symlink(os.path.join(w.repo, "src", "RimMandrake", "rimflow"), os.path.join(t, "src", "RimMandrake", "rimflow"))
    real_utils = os.path.join(w.repo, "src", "RimMandrake", "Utils")
    fakes = {"broadcast.py": FAKE_BROADCAST, "modlist_swap.py": "print('live currently matches: FULL')\n",
             "zoom_guard.py": "pass\n"}
    for f in os.listdir(real_utils):
        if f.endswith(".py") and f not in fakes:
            os.symlink(os.path.join(real_utils, f), os.path.join(utils, f))
    for f, body in fakes.items():
        with open(os.path.join(utils, f), "w") as fh:
            fh.write(body)
    with open(os.path.join(w.repo, "game")) as fh:
        game = os.path.join(t, "game")
        with open(game, "w") as out:
            out.write(fh.read())
    os.chmod(game, 0o755)
    blog = os.path.join(w.tmp, "broadcast.log")

    def run(*args):
        if os.path.exists(blog):
            os.remove(blog)
        r = w.run([game] + list(args), RM_HOST="archmagi", FAKE_BROADCAST_LOG=blog, timeout=120)
        sent = [json.loads(ln) for ln in open(blog)] if os.path.exists(blog) else []
        shards = os.path.join(w.rf, "events")       # a take lands in its seat's shard, BENCH's written as CONDUCTOR
        files = [w.env["RIMFLOW_LEDGER"]] + ([os.path.join(shards, f) for f in os.listdir(shards)] if os.path.isdir(shards) else [])
        takes = [json.loads(ln) for p in files for ln in open(p) if ln.strip()]
        takes = [e for e in takes if e.get("seat") in ("BENCH", "CONDUCTOR") and e.get("event") == "bridge" and e.get("state") == "taken"]
        return r, sent, takes

    w.bridge((OTHER, 120))
    r, sent, takes = run("--idle-ok", "--why", "restart for the look", "down")
    check(r.returncode == 1 and not sent and not takes and "rimflow bridge idle" in r.stderr,
          "./game --idle-ok with another seat's live hold: refused, nothing announced or taken: %s %s %s" % (r.returncode, sent, r.stderr.strip()[-200:]))
    w.bridge()
    r, sent, takes = run("--idle-ok", "--why", "restart for the look", "bogus")
    check(r.returncode == 2 and not sent and not takes, "./game --idle-ok with a typo'd state takes nothing: %s %s" % (r.returncode, takes))
    w.bridge()
    r, sent, takes = run("--idle-ok", "--why", "restart for the look", "down")
    check(r.returncode == 0 and len(takes) == 1 and takes[0].get("purpose") == "restart for the look",
          "./game --idle-ok on a free bridge TAKES it before acting: %s %s %s" % (r.returncode, takes, (r.stdout + r.stderr).strip()[-200:]))
    check(len(sent) == 1 and sent[0]["sentence"] == ["Game is down"] and (sent[0]["why"] or "").startswith("delegated: restart for the look ["),
          "... then announces, the take's reason on its why: %s" % sent)
    w.bridge()


def whole_repo():
    """No live tool kills by image name again. Prose may name it; a selftest may fake it."""
    import subprocess
    probe = subprocess.run(["git", "-C", F.REPO, "grep", "-c", "RimWorldWin64", "--", "src/RimMandrake/Utils/game_instance.py"],
                           capture_output=True, text=True)
    if probe.returncode != 0:       # the mutant copy has no git; a search that cannot see is not a pass
        return print("UNMEASURED: no git here to search for taskkill /IM")
    out = subprocess.run(["git", "-C", F.REPO, "grep", "-nE", r"taskkill.*/IM.*(RimWorld|GAME)|\"/IM\".*(RimWorld|GAME)", "--", "*.py", "*.sh", "*.ps1"],
                         capture_output=True, text=True).stdout
    bad = [ln for ln in out.splitlines() if not re.search(r"selftest|fake_two_games|time_ledger_replay|^Transient/", ln.split(":")[0])]
    check(not bad, "no live taskkill /IM left: %s" % [b[:120] for b in bad])


SECTIONS = {"names": names, "stop": stop, "blind": blind, "paths": paths, "launch": launch, "rw_game": rw_game, "sites": sites,
            "bridge": bridge, "game_idle_ok": game_idle_ok}


def main():
    only = [s for s in os.environ.get("GI_ONLY", "").split(",") if s]
    check(os.path.dirname(os.path.abspath(G.__file__)) == HERE and os.path.dirname(os.path.abspath(F.__file__)) == HERE, "tests the copy beside it")
    if not only or "owners" in only:
        owners()
    if not only or "repo" in only:
        whole_repo()
    w = F.World(F.REPO)
    os.environ.update({k: v for k, v in w.env.items() if k in ("RM_INSTANCES_ROOT",)})
    try:
        for name, fn in SECTIONS.items():
            if not only or name in only:
                print("-- " + name)
                fn(w)
                w.clear()
    finally:
        w.close()
    print("%s selftest_game_instance: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
