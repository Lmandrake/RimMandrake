#!/usr/bin/env python3
"""selftest_game_hold_split_install.py - his walk holds game a only; game b has its own install and takes the runs.

Item RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST; page design/specs/2026-11-20-per-game-hold-own-install/
boundary.md (each t_ function is one promise of it). The owner walked game a twice on 2026-11-20 and both times every
in-game run waited for hours, although game b existed: "You should not have been waiting for the game. there are two
games" (3:40 PM PST). The causes, measured that morning: the only way to keep runs off his game was to switch the whole
in-game stage off; both games loaded one Mods and one BridgeTools folder, so a deploy for b wrote into a's; and inside
the Conductor's process tree its own walk hold on a read as free (pick_game took a; leftovers said to stop his game).

Offline: fake folders, a throwaway control store, stand-in bridge readings; no game, no Windows. Written before the
code; seen failing on the base commit d309e9d2f6 (32 FAIL, the 5 must-stay-green cases passing), and each of 10
planted faults turned it red by its own case.
"""
import contextlib
import io
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
BT = os.path.join(REPO, "src", "RimMandrake", "bridgetools")
for _p in (HERE, UTILS, BT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"

FAILS = []


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:200])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def _safe(fn, default):
    """fn(), or default when it raises: the check after it then reads the default and FAILS by name (on the base)."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        print("     (raised %s: %s)" % (type(e).__name__, str(e)[:160]))
        return default


def _raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False


def under(p, top):
    a = os.path.realpath(p).replace("\\", "/").rstrip("/").lower() + "/"
    return a.startswith(os.path.realpath(top).replace("\\", "/").rstrip("/").lower() + "/")


def fake_install(top):
    """A fake game a install under top/steamapps/common/RimWorld and a b data folder under top/instances/b."""
    a = os.path.join(top, "steamapps", "common", "RimWorld")
    for d in ("Mods/SomeLib/About", "BridgeTools/JawaBench", "Data/Core", "MonoBleedingEdge", "RimWorldWin64_Data",
              "ModsRetired"):
        os.makedirs(os.path.join(a, d), exist_ok=True)
    for f in ("RimWorldWin64.exe", "UnityPlayer.dll", "Version.txt", "steam_appid.txt", "Mods/SomeLib/About/About.xml"):
        with open(os.path.join(a, f), "w") as fh:
            fh.write("x")
    os.makedirs(os.path.join(top, "steamapps", "workshop", "content", "294100"), exist_ok=True)
    b = os.path.join(top, "instances", "b")
    for d in ("Config", "game/Mods", "game/Data", "game/BridgeTools/JawaBench"):
        os.makedirs(os.path.join(b, d), exist_ok=True)
    with open(os.path.join(b, "game", "RimWorldWin64.exe"), "w") as fh:
        fh.write("x")
    with open(os.path.join(b, "Config", "ModsConfig.xml"), "w") as fh:
        fh.write("<ModsConfigData><version>1.6</version><activeMods><li>ludeon.rimworld</li></activeMods>"
                 "</ModsConfigData>")
    os.makedirs(os.path.join(top, "low", "Config"), exist_ok=True)
    shutil.copyfile(os.path.join(b, "Config", "ModsConfig.xml"), os.path.join(top, "low", "Config", "ModsConfig.xml"))
    return a, b


def sub_env(top, game=None, **extra):
    env = dict(os.environ)
    for k in ("RM_GAME_INSTANCE", "RM_GAME_USERDATA", "RM_GAME_LOGDIR", "RIMFLOW_DRIVER_LOCK"):
        env.pop(k, None)
    env.update(RM_STEAMAPPS=os.path.join(top, "steamapps"), RM_INSTANCES_ROOT=os.path.join(top, "instances"),
               RM_GAME_USERDATA=os.path.join(top, "low"), RM_GAME_LOGDIR=os.path.join(top, "low"),
               PYTHONDONTWRITEBYTECODE="1")
    if game:
        env["RM_GAME_INSTANCE"] = game
    env.update(extra)
    return env


def _hold(X, game, on, why):
    import control as C
    C.switch("game:" + game, on, why, p=X.db)


# ---------------------------------------------------------------------------------------------- promises

def t_a_game_hold_is_a_scope_that_refuses_runs_on_that_game_only(X):
    import control as C
    chk(lambda: C.scope_of("game:a") == "game:a", "hold: `game:a` is a scope")
    chk(lambda: _raises(lambda: C.scope_of("game:ab"), C.Refused), "hold: `game:ab` is refused (one letter)")
    _hold(X, "a", True, "his walk")
    chk(lambda: "his walk" in (C.game_held("a", X.db) or ""), "hold: game_held(a) names the walk")
    chk(lambda: C.game_held("b", X.db) is None, "hold: game b is not held")
    spec = {"family": "detached", "unit": "rm-x", "stage": "in_game", "mod": None}
    chk(lambda: C.blocked(dict(spec, game="a"), X.db) is not None, "hold: a run spec on game a is refused")
    chk(lambda: C.blocked(dict(spec, game="b"), X.db) is None, "hold: a run spec on game b is not refused")
    chk(lambda: "game:a" in C.run_scopes({"family": "detached", "game": "a"}), "hold: run_scopes carries the game")
    _hold(X, "a", False, "walk over")


def t_a_run_names_a_game_only_when_it_drives_one(X):
    import control as C
    import detached_helper as DH
    stage = {"RM_CONTROL_MOD": "Pyrelands", "RM_CONTROL_STAGE": "in_game"}
    steward, visit = "RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_THREE_FAILURES_BACK", "RIMMANDRAKE_RUN_PYRELANDS_IN_GAME_VISIT_FOUR"
    game = lambda item, env: _safe(lambda: DH.run_game(item, env), "base")  # noqa: E731
    chk(lambda: game(steward, stage) is None, "names: a steward run at stage in_game names no game")
    chk(lambda: game(visit, stage) == "a", "names: an in-game visit naming no game drives game a")
    chk(lambda: game(visit, dict(stage, RM_GAME_INSTANCE="b")) == "b", "names: RM_GAME_INSTANCE=b names game b")
    chk(lambda: game(steward, dict(stage, RM_GAME_INSTANCE="b")) == "b", "names: a steward run told game b names it")
    _hold(X, "a", True, "his walk")
    spec = {"family": "detached", "unit": "rm-x", "stage": "in_game", "mod": "Pyrelands"}
    chk(lambda: C.blocked(dict(spec, item=steward, game=game(steward, stage)), X.db) is None,
        "names: his hold on game a does not refuse the steward run")
    chk(lambda: C.blocked(dict(spec, item=visit, game=game(visit, stage)), X.db) is not None,
        "names: his hold on game a refuses the in-game visit")
    _hold(X, "a", False, "walk over")


def t_a_held_game_is_never_picked_and_game_b_takes_the_run(X):
    import maturation_dispatch as MD
    cfg = {"game_instances": ["a", "b"], "seat": "BENCH"}
    go = lambda p, game="a": (True, "TAKEABLE  free")  # noqa: E731
    _hold(X, "a", True, "his walk")
    chk(lambda: MD.pick_game(cfg, go, "visit")[0] == "b", "pick: game a held by `pipe off game:a` -> game b")
    _hold(X, "a", False, "walk over")
    got = _safe(lambda: MD.pick_game(cfg, go, "visit", hold=lambda g: None), (None, []))
    chk(lambda: got[0] == "a", "pick: no hold -> game a first, as before")


def t_a_full_list_only_visit_waits_for_game_a_and_says_so_by_name(X):
    import maturation_dispatch as MD
    cfg = {"game_instances": ["a", "b"], "seat": "BENCH"}
    go = lambda p, game="a": (True, "TAKEABLE  free")  # noqa: E731
    chk(lambda: MD.full_list_only({"checks": ["sc_walk"], "full_list": ["sc_walk"]}) == ["sc_walk"],
        "pick: a visit whose every check is full-list needs game a")
    chk(lambda: MD.full_list_only({"checks": ["sc_x", "sc_walk"], "full_list": ["sc_walk"]}) == [],
        "pick: a visit with a tier check may use game b")
    # the checks a visit OWES decide, not every check of the table (Pyrelands visit 6, 2026-11-23: 32 of 38 owed, one of
    # them full-list; a later visit owing sc_walk alone must wait for game a, or it runs on b and leaves it UNMEASURED)
    chk(lambda: MD.full_list_only({"checks": ["sc_x", "sc_walk"], "to_run": ["sc_walk"], "full_list": ["sc_walk"]})
        == ["sc_walk"], "pick: a visit that owes only full-list checks needs game a, whatever else the table holds")
    chk(lambda: MD.full_list_only({"checks": ["sc_x", "sc_walk"], "to_run": ["sc_x", "sc_walk"],
                                   "full_list": ["sc_walk"]}) == [],
        "pick: a visit that owes a tier check may use game b (must stay green)")
    chk(lambda: MD.full_list_only({"checks": ["sc_x", "sc_walk"], "to_run": [], "full_list": ["sc_walk"]}) == [],
        "pick: a visit that owes nothing is not full-list-only (must stay green)")
    _hold(X, "a", True, "his walk")
    g, whys = _safe(lambda: MD.pick_game(cfg, go, "visit", only={"b": "every check needs his full list (sc_walk)"}),
                    ("x", []))
    chk(lambda: g is None and any("sc_walk" in w for w in whys) and any("his walk" in w for w in whys),
        "pick: a full-list-only visit with game a held waits, and says why by name")
    _hold(X, "a", False, "walk over")


def t_the_askers_own_hold_is_a_hold_for_a_new_run(X):
    import driver_lock
    import host_guard
    chk(lambda: host_guard.crossing(X.lock) is None, "newrun: my own window's hold lets me drive (unchanged)")
    chk(lambda: host_guard.crossing(X.lock, new_run=True) is not None,
        "newrun: my own window's hold is a hold for a NEW run")


def t_leftovers_never_offers_a_held_game(X):
    import game_instance as GI
    games_was = GI.games
    GI.games = lambda exe=GI.GAME_EXE: [{"pid": 37580, "start": 1.0, "cmd": "RimWorldWin64.exe", "instance": "a"}]
    try:
        os.environ["RIMFLOW_DRIVER_LOCK"] = X.lock
        chk(lambda: GI.leftovers(refusal=lambda n, p: None) == [],
            "leftovers: inside the holder's own tree game a is not offered")
        os.environ["RIMFLOW_DRIVER_LOCK"] = os.path.join(X.top, "no_lock.json")
        chk(lambda: GI.leftovers(refusal=lambda n, p: None) == [{"instance": "a", "pid": 37580}],
            "leftovers: an idle game nobody holds is still a leftover (must stay green)")
        _hold(X, "a", True, "his walk")
        chk(lambda: GI.leftovers(refusal=lambda n, p: None) == [], "leftovers: a held game is never a leftover")
        _hold(X, "a", False, "walk over")
    finally:
        GI.games = games_was


def t_stop_of_a_held_game_refuses_unless_despite_hold(X):
    import game_instance as GI
    pids_was, br_was, run_was = GI.pids, GI.bridge_refusal, GI._run
    GI.pids = lambda name=None: [37580]
    GI.bridge_refusal = lambda *a, **k: None
    killed = []
    GI._run = lambda argv, timeout=60: killed.append(argv) or subprocess.CompletedProcess(argv, 0, "ok", "")
    _hold(X, "a", True, "his walk")
    try:
        chk(lambda: _raises(lambda: GI.stop(name="a"), GI.Refused) and not killed,
            "stop: a held game refuses the stop and signals nothing")
        chk(lambda: GI.stop(name="a", despite="the Conductor, on purpose")[0] == 0 and killed,
            "stop: --despite-hold passes")
    finally:
        GI.pids, GI.bridge_refusal, GI._run = pids_was, br_was, run_was
        _hold(X, "a", False, "walk over")


def t_a_named_games_paths_are_its_own_install(X):
    code = ("import json, game_paths as g; print(json.dumps([g.GAME_DIR, g.LOCAL_MODS, g.GAME_DATA, g.WORKSHOP, "
            "g.A_GAME_DIR]))")
    rb = json.loads(subprocess.run([sys.executable, "-c", code], cwd=UTILS, env=sub_env(X.top, "b"),
                                   capture_output=True, text=True, timeout=60).stdout or "null")
    chk(lambda: all(under(p, X.b_dir) for p in rb[:3]), "paths: game b's GAME_DIR, Mods and Data are its own install")
    chk(lambda: under(rb[3], os.path.join(X.top, "steamapps", "workshop")), "paths: game b shares Steam's Workshop")
    chk(lambda: under(rb[4], X.a_dir), "paths: A_GAME_DIR stays Steam's in a b shell")
    ra = json.loads(subprocess.run([sys.executable, "-c", code], cwd=UTILS, env=sub_env(X.top),
                                   capture_output=True, text=True, timeout=60).stdout or "null")
    chk(lambda: all(under(p, X.a_dir) for p in ra[:3]), "paths: game a unchanged (Steam's install)")


def _plan_line(X, *args):
    dep = os.path.join(UTILS, "deploy_custom_mods.py")
    r = subprocess.run([sys.executable, dep] + list(args), cwd=REPO, env=sub_env(X.top, RM_CONTROL_DB=X.db),
                       capture_output=True, text=True, timeout=600)
    return r, next((x for x in (r.stdout or "").splitlines() if x.startswith("game :")), "")


def _write(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def t_a_deploy_for_game_b_writes_only_under_game_b(X):
    r, line = _plan_line(X, "--gate", "--mod", "FlowWorks", "--instance", "b")
    chk(lambda: line and under(line[6:].strip(), os.path.join(X.b_dir, "game", "Mods")),
        "deploy: --instance b plans into b's own Mods (%s)" % (line or (r.stderr or "")[-160:]))
    r, line = _plan_line(X, "--gate", "--mod", "FlowWorks")
    chk(lambda: line and under(line[6:].strip(), X.a_dir), "deploy: no instance plans into game a's Mods (unchanged)")

    repo = os.path.join(X.top, "repair_repo")
    src = os.path.join(repo, "src")
    tier = os.path.join(src, "RimMandrake")
    tools = os.path.join(tier, "Utils")
    os.makedirs(tools)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, timeout=30)
    dep = os.path.join(tools, "deploy_custom_mods.py")
    shutil.copyfile(os.path.join(UTILS, "deploy_custom_mods.py"), dep)
    manifest = {
        "target": "RimMandrake.Biomes", "compose_wave": 1,
        "entries": [{"key": "Stillsand", "source": "Stillsand", "wave": 1, "label": "Stillsand"}],
        "shell": {"source": "BiomesShell", "assemblies": []},
        "about": {"name": "Baroque Biomes", "packageId": "mandrake.rm.biomes", "author": "test",
                  "supportedVersions": ["1.6"], "description": "Deploy repair fixture"},
    }
    _write(os.path.join(tier, "Biomes.compose.json"), json.dumps(manifest))
    about = "<ModMetaData><packageId>%s</packageId></ModMetaData>"
    _write(os.path.join(tier, "Stillsand", "About", "About.xml"), about % "mandrake.rm.stillsand")
    _write(os.path.join(tier, "Stillsand", "Defs", "Vekka.xml"),
          "<Defs><ThingDef><defName>RM_Vekka</defName></ThingDef>"
          "<RimMandrake.EnvironmentalHazards.RM_DefAliasDef><defName>SandLionAlias</defName><aliases>"
          "<li><from>RSW_SandLion</from><to>RM_Vekka</to><defType>ThingDef</defType></li>"
          "</aliases></RimMandrake.EnvironmentalHazards.RM_DefAliasDef></Defs>")
    b_mods = os.path.join(X.b_dir, "game", "Mods")
    for d in (os.path.join(src, "RimStarWars"), b_mods):
        _write(os.path.join(d, "SWBestiary", "About", "About.xml"), about % "mandrake.sw.bestiary")
    _write(os.path.join(b_mods, "SWBestiary", "Defs", "SandLion.xml"),
          "<Defs><ThingDef><defName>RSW_SandLion</defName></ThingDef></Defs>")
    env = sub_env(X.top, RM_CONTROL_DB=X.db, RM_HOST="archmagi", RM_COMPOSE_TMP=X.top,
                  PYTHONPATH=os.pathsep.join((UTILS, HERE)))

    def plan(*args):
        return subprocess.run([sys.executable, dep, *args], cwd=repo, env=env,
                              capture_output=True, text=True, timeout=60)

    r = plan("--compose", "biomes", "--instance", "ArchSmall")
    fix = next((line.partition("fix: ")[2] for line in r.stdout.splitlines()
                if line.strip().startswith("fix: python3 ")), "")
    words = shlex.split(fix)
    repair = ("ALIAS-STALE ThingDef RSW_SandLion -> RM_Vekka" in r.stdout
              and {"--compose", "--with", "SWBestiary", "--apply", "--prune"} <= set(words))
    chk(lambda: repair, "deploy: ArchSmall's stale SandLion triggers a composed repair with SWBestiary and --prune"
        + ("" if repair else " (%s)" % (r.stderr.strip() or r.stdout.strip())[-500:]))
    if repair:
        retry = plan(*(arg for arg in words[2:] if arg != "--apply"))
        line = next((line[6:].strip() for line in retry.stdout.splitlines() if line.startswith("game :")), "")
        chk(lambda: line and under(line, b_mods),
            "deploy: replaying ArchSmall's repair selects ArchSmall (got %s)" %
            ("ArchBig" if line and under(line, X.a_dir) else line or retry.stderr.strip()))

    r = plan("--mod", "Stillsand", "--instance", "ArchSmall")
    chk(lambda: r.returncode != 0 and "deploy it with:" in r.stderr and "--instance ArchSmall" in r.stderr,
        "deploy: ArchSmall's folded-mod retry command names ArchSmall")


def t_a_deploy_into_a_held_game_refuses_and_writes_nothing(X):
    _hold(X, "b", True, "a planted hold on b")
    try:
        r, _ = _plan_line(X, "--apply", "--mod", "FlowWorks", "--instance", "b")
        chk(lambda: r.returncode != 0 and "is held" in (r.stdout + r.stderr)
            and not os.path.exists(os.path.join(X.b_dir, "game", "Mods", "FlowWorks")),
            "deploy: --apply into a held game refuses and writes nothing (rc %s: %s)" % (
                r.returncode, (r.stdout + r.stderr).strip()[-160:]))
    finally:
        _hold(X, "b", False, "planted hold lifted")

    import control as C
    with mock.patch.dict(os.environ, sub_env(X.top)):
        import deploy_custom_mods as D
    src = os.path.join(X.top, "native_src")
    _write(os.path.join(src, "RimMandrake", "NativeProbe", "About", "About.xml"),
          "<ModMetaData><packageId>mandrake.nativeprobe</packageId></ModMetaData>")
    mods = os.path.join(X.a_dir, "Mods")
    config = os.path.join(X.top, "low", "Config", "ModsConfig.xml")
    native_os = types.SimpleNamespace(**vars(os))
    native_os.name = "nt"
    _hold(X, "a", True, "his walk")
    try:
        with mock.patch.dict(os.environ, RM_HOST="archmagi"), mock.patch.object(
                C, "DEFAULT_DB", os.path.join(X.top, "windows_profile", "control.db")), mock.patch.object(
                C, "test_process", return_value=False), mock.patch.multiple(
                D, os=native_os, SRC_ROOT=src, LOCAL_MODS=mods, _MODS=[mods], _CONFIG=[config]), mock.patch.object(
                D, "copy", return_value=(0, 0, 0)) as copy:
            os.environ.pop("RM_CONTROL_DB")
            os.environ.pop("RM_GAME_INSTANCE", None)
            argv = ["deploy_custom_mods.py", "--mod", "NativeProbe"]
            with mock.patch.object(sys, "argv", argv + ["--apply"]), contextlib.redirect_stdout(io.StringIO()):
                try:
                    rc = D.main()
                except SystemExit as e:
                    rc = e.code
            chk(lambda: isinstance(rc, str) and "REFUSING" in rc and "ArchBig" in rc and "WSL" in rc
                and "python3 src/RimMandrake/Utils/deploy_custom_mods.py --instance ArchBig --mod NativeProbe --apply"
                in rc and not copy.called,
                "deploy: native --apply refuses before writes for ArchBig (copy called: %s)" % copy.called)
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
                D.main()
            chk(lambda: "plan only" in out.getvalue() and "+  About/About.xml" in out.getvalue(),
                "deploy: native dry run still reports the pending file")
    finally:
        _hold(X, "a", False, "planted hold lifted")


def t_a_companion_build_for_game_b_writes_only_under_game_b(X):
    code = "import json, build as B; B.aim(%r); print(json.dumps([B.GAME, B.DEPLOY_DIR, B.GAME_ROOT]))"
    rb = json.loads(subprocess.run([sys.executable, "-c", code % "b"], cwd=BT, env=sub_env(X.top),
                                   capture_output=True, text=True, timeout=120).stdout or "null")
    chk(lambda: rb[0] == "b" and under(rb[1], os.path.join(X.b_dir, "game", "BridgeTools")),
        "build: aim(b) deploys into b's own BridgeTools")
    ra = json.loads(subprocess.run([sys.executable, "-c", code % "a"], cwd=BT, env=sub_env(X.top),
                                   capture_output=True, text=True, timeout=120).stdout or "null")
    chk(lambda: ra[0] == "a" and "steamapps" in ra[2].replace("\\", "/").lower()
        and not under(ra[1], os.path.join(X.top, "instances")), "build: game a keeps Steam's BridgeTools")


def t_the_in_game_gate_reads_the_runs_own_game(X):
    import maturation as M
    import companion_identity as CI
    seen = []
    v_was, d_was = CI.verdict, CI.describe
    CI.verdict = lambda dll, *a, **k: seen.append(dll) or {"state": "FRESH"}
    CI.describe = lambda v: "stand-in"
    env_was = os.environ.pop(M.COMPANION_ENV, None)
    try:
        M.companion_current(game="b")
        chk(lambda: seen and under(seen[-1], os.path.join(X.b_dir, "game", "BridgeTools")),
            "verify: companion_current(game=b) reads b's own companion (%s)" % (seen[-1:] or ["none"])[0])
    finally:
        CI.verdict, CI.describe = v_was, d_was
        if env_was is not None:
            os.environ[M.COMPANION_ENV] = env_was
    argv_seen = []
    runner = lambda argv, **k: argv_seen.append(argv) or subprocess.CompletedProcess(argv, 0, "Everything in sync.", "")  # noqa: E731
    plan_was = os.environ.pop(M.DEPLOY_PLAN_ENV, None)
    try:
        _safe(lambda: M.mod_deployed(REPO, "FlowWorks", runner=runner, game="b"), None)
    finally:
        if plan_was is not None:
            os.environ[M.DEPLOY_PLAN_ENV] = plan_was
    chk(lambda: argv_seen and argv_seen[-1][-2:] == ["--instance", "b"],
        "verify: mod_deployed(game=b) plans with --instance b")


def t_install_writes_only_under_the_named_game(X):
    import game_instance as GI
    os.environ["RM_INSTANCES_ROOT"] = os.path.join(X.top, "inst2")
    copies = []

    def copier(src, dst, files):
        copies.append((src, dst))
        os.makedirs(dst, exist_ok=True)
        if files:
            for f in files:
                shutil.copyfile(os.path.join(src, f), os.path.join(dst, f))
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
    try:
        where, done = _safe(lambda: GI.install("b", copier=copier, source=X.a_dir), (X.top, []))
        chk(lambda: copies and all(under(d, os.path.join(X.top, "inst2", "b", "game")) for _, d in copies)
            and not any(under(d, X.a_dir) for _, d in copies), "install: every write lands under b's own folder")
        chk(lambda: "Mods/" in done and "BridgeTools/" in done and "ModsRetired/" not in done
            and os.path.exists(os.path.join(where, "RimWorldWin64.exe")), "install: the game's files and Mods, no junk")
        chk(lambda: GI.install("b", copier=copier, source=X.a_dir)[1] == [], "install: an install that exists is kept")
        os.remove(os.path.join(where, "steam_appid.txt"))
        chk(lambda: GI.install("b", copier=copier, source=X.a_dir)[1] == ["steam_appid.txt"]
            and os.path.exists(os.path.join(where, "steam_appid.txt")),
            "install: a top-level file game a has and b lacks is copied into the kept install")
        os.environ["RM_INSTANCES_ROOT"] = os.path.join(X.a_dir, "instances")
        chk(lambda: _raises(lambda: GI.install("b", copier=copier, source=X.a_dir), GI.Refused),
            "install: a b folder inside game a's install is refused")
    finally:
        os.environ["RM_INSTANCES_ROOT"] = os.path.join(X.top, "instances")
    chk(lambda: GI.owner(r'"D:\ClaudeWork\rimmandrake\instances\b\game\RimWorldWin64.exe" -logfile x') == "b",
        "install: a game started from b's own exe is game b")


def t_a_named_games_list_swap_is_its_own(X):
    code = "import modset_builder as MB; print(MB.owned_backups('BENCH'))"
    env = sub_env(X.top, "b", RM_DATA_ROOT=os.path.join(X.top, "data"))
    rb = subprocess.run([sys.executable, "-c", code], cwd=UTILS, env=env, capture_output=True, text=True, timeout=120)
    env.pop("RM_GAME_INSTANCE")
    ra = subprocess.run([sys.executable, "-c", code], cwd=UTILS, env=env, capture_output=True, text=True, timeout=120)
    pb, pa = (rb.stdout or "").strip(), (ra.stdout or "").strip()
    chk(lambda: pb and os.path.basename(pb) == "BENCH.b", "swap: game b's swap marker is its own (%s)" % (
        pb or (rb.stderr or "")[-160:]))
    chk(lambda: pa and os.path.basename(pa) == "BENCH", "swap: game a's stays where it was (%s)" % (
        pa or (ra.stderr or "")[-160:]))


def t_game_bs_brief_names_its_own_install_and_its_unmeasured_full_list_checks(X):
    import game_instance as GI
    text = _safe(lambda: GI.brief("b", ["sc_walk"]), "")
    chk(lambda: "own install" in text and "Both games read one Mods folder" not in text,
        "brief: game b has its own Mods folder")
    chk(lambda: "sc_walk" in text and "UNMEASURED" in text, "brief: b's full-list checks are recorded UNMEASURED")


def t_a_named_game_gets_the_registered_site_saves_it_lacks(X):
    import game_instance as GI
    reg = os.path.join(X.top, "sites.json")
    with open(reg, "w") as f:
        json.dump({"pyrelands": {"save": "NS_site_x", "load": "..."}, "calm": {"save": "RM_calm_v1"},
                   "river": {"save": "RM_river_v2"}, "note": "no save here"}, f)
    src = os.path.join(X.top, "a_saves")
    os.makedirs(src, exist_ok=True)
    for n in ("NS_site_x", "RM_calm_v1", "NS_unregistered"):
        with open(os.path.join(src, n + ".rws"), "w") as f:
            f.write("a:" + n)
    bsaves = os.path.join(GI.data_dir("b"), "Saves")
    os.makedirs(bsaves, exist_ok=True)
    with open(os.path.join(bsaves, "RM_calm_v1.rws"), "w") as f:
        f.write("b's own")
    done = _safe(lambda: GI.seed_site_saves("b", source=src, registry=reg), None)
    chk(lambda: done == ["NS_site_x"], "site saves: b gets the registered save it lacks, only that one (%r)" % (done,))
    chk(lambda: open(os.path.join(bsaves, "NS_site_x.rws")).read() == "a:NS_site_x", "site saves: the copy is a's file")
    chk(lambda: open(os.path.join(bsaves, "RM_calm_v1.rws")).read() == "b's own", "site saves: b's own save is never overwritten")
    chk(lambda: not os.path.exists(os.path.join(bsaves, "NS_unregistered.rws")), "site saves: an unregistered save is not copied")
    chk(lambda: not os.path.exists(os.path.join(bsaves, "RM_river_v2.rws")), "site saves: a save a lacks is skipped, not invented")
    chk(lambda: _safe(lambda: GI.seed_site_saves("a", source=src, registry=reg), None) == [],
        "site saves: ArchBig is the source and is never written")


def main():
    top = tempfile.mkdtemp(prefix="game_hold_split_")
    a_dir, b_dir = fake_install(top)
    X = types.SimpleNamespace(top=top, a_dir=a_dir, b_dir=b_dir, db=os.path.join(top, "control.db"),
                              lock=os.path.join(top, "lock_a.json"))
    saved = {k: os.environ.get(k) for k in ("RM_CONTROL_DB", "RM_INSTANCES_ROOT", "RIMFLOW_DRIVER_LOCK",
                                             "RM_GAME_INSTANCE", "RM_STEAMAPPS")}
    os.environ["RM_CONTROL_DB"] = X.db
    os.environ["RM_INSTANCES_ROOT"] = os.path.join(top, "instances")
    os.environ.pop("RM_GAME_INSTANCE", None)
    try:
        import control as C
        import driver_lock
        C.init(X.db)
        driver_lock.acquire(X.lock, "CONDUCTOR", "his walk", driver_lock.my_identity())
        for t in (t_a_game_hold_is_a_scope_that_refuses_runs_on_that_game_only,
                  t_a_run_names_a_game_only_when_it_drives_one,
                  t_a_held_game_is_never_picked_and_game_b_takes_the_run,
                  t_a_full_list_only_visit_waits_for_game_a_and_says_so_by_name,
                  t_the_askers_own_hold_is_a_hold_for_a_new_run,
                  t_leftovers_never_offers_a_held_game,
                  t_stop_of_a_held_game_refuses_unless_despite_hold,
                  t_a_named_games_paths_are_its_own_install,
                  t_a_deploy_for_game_b_writes_only_under_game_b,
                  t_a_deploy_into_a_held_game_refuses_and_writes_nothing,
                  t_a_companion_build_for_game_b_writes_only_under_game_b,
                  t_the_in_game_gate_reads_the_runs_own_game,
                  t_install_writes_only_under_the_named_game,
                  t_a_named_games_list_swap_is_its_own,
                  t_game_bs_brief_names_its_own_install_and_its_unmeasured_full_list_checks,
                  t_a_named_game_gets_the_registered_site_saves_it_lacks):
            try:
                t(X)
            except Exception as e:  # noqa: BLE001
                chk(lambda: False, "%s (raised %s: %s)" % (t.__name__, type(e).__name__, str(e)[:200]))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(top, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
