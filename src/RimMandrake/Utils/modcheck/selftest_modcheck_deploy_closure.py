#!/usr/bin/env python3
"""Selftest for RELAPSE_STEVE_FIX_DIED_TWICE: a mod's run deploys every mod of OURS its composed list names.

modcheck run() composes a mod's hard <modDependencies> and its tier closure into ModsConfig, and RimWorld drops an id
whose folder is not in the game's Mods directory. Deploying only the mod (or the composed biomes) left
mandrake.rm.luminouspigment out of every TerminalBiomes load on SteveDesktop (2026-11-04, J20261104T143941Z-f42090 and
J20261104T144746Z-3c7909: INVALID/HARNESS stale_load `not loaded: mandrake.rm.luminouspigment`), the lane braked with no
non-fault cause, and incident steve-20261101162433 relapsed a third time.

  1. the instance: TerminalBiomes' deploy carries LuminousPigment, through --compose biomes --with
  2. the class guard, over every mod under src/: each id of ours that run() composes is deployed by that mod's own
     deploy (the mod, its composed target, or deploy_closure); the pre-fix route (the mod alone) fails it on the instance
  3. deploy_args_for passes deploy_custom_mods.py's own argument checks (parse only, nothing copied)
  4. the SteveDesktop worker reads the closure from the job's tree: the instance, an older tree with no
     deploy_closure answers [], a broken tree raises (an empty guess is the defect)
Offline: nothing is deployed and no game is touched."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import runner  # noqa: E402

REPO = runner.ROOT
sys.path.insert(0, os.path.dirname(HERE))
import biomes_compose  # noqa: E402
TARGET = biomes_compose.load_manifest(os.path.join(REPO, "src"))["target"]
FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def deployed_by(args, have):
    """The deployable names a deploy_custom_mods.py argument list puts in the game, read from the FLAGS themselves."""
    got = {v for f, v in zip(args[::2], args[1::2]) if f in ("--mod", "--with")}
    if "--compose" in args:
        got.add(TARGET)
    return got


def uncovered(mod, args, have):
    """Composed ids of ours, and the mod itself, that this deploy leaves out of the game."""
    got = deployed_by(args, have)
    folded = runner.composed_into(mod)
    want = [p for p in runner.composed_ids(mod) if have.get(p)]
    return [p for p in want if have[p] not in got] + ([] if folded or mod in got else [mod])


def all_mods():
    out = []
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        d = os.path.join(REPO, "src", tier)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if os.path.isfile(os.path.join(d, n, "About", "About.xml")):
                out.append(n)
    return out


def deploy_attempt(worker):
    """Drive worker.Attempt.deploy for a TerminalBiomes job without a game, a deploy or a copy: sh() is recorded and
    answers rc 0, companion() answers True. Returns nothing; each route's recorded command must name LuminousPigment."""
    import io
    import shlex

    def attempt():
        a = worker.Attempt.__new__(worker.Attempt)          # __init__ reads an attempt dir; none is needed here
        a.job = {"id": "selftest", "mod": "TerminalBiomes", "deploy": []}
        a.d = tempfile.mkdtemp(prefix="deploy_attempt_")
        a.log = io.StringIO()
        a.res = {"outcome": None, "cause": None, "note": ""}
        a.cmds = []
        a.sh = lambda cmd, log_name=None, timeout=None: (a.cmds.append(cmd) or (0, ""))
        a.companion = lambda: True
        return a

    saved_clone, saved_env = worker.CLONE, os.environ.get("TESTQ_CMD_DEPLOY")
    worker.CLONE = REPO                                     # deploy_closure reads the job tree from CLONE
    try:
        os.environ["TESTQ_CMD_DEPLOY"] = "record-deploy"
        a = attempt()
        ok(a.deploy() is True, "Attempt.deploy (override route) succeeds on a recorded sh", a.res)
        words = shlex.split(a.cmds[0]) if a.cmds else []
        ok(words[:1] == ["record-deploy"] and "TerminalBiomes" in words and "LuminousPigment" in words,
           "Attempt.deploy (override route) deploys LuminousPigment with TerminalBiomes", a.cmds)
        shutil.rmtree(a.d, ignore_errors=True)

        del os.environ["TESTQ_CMD_DEPLOY"]
        a = attempt()
        ok(a.deploy() is True, "Attempt.deploy (plan route) succeeds when the plan finds no drift", a.res)
        plan = [c for c in a.cmds if "deploy_custom_mods.py" in c]
        words = shlex.split(plan[0]) if plan else []
        flags = list(zip(words, words[1:]))
        ok(("--with", "LuminousPigment") in flags and ("--compose", "biomes") in flags,
           "Attempt.deploy (plan route) plans --compose biomes --with LuminousPigment", a.cmds)
        shutil.rmtree(a.d, ignore_errors=True)
    finally:
        worker.CLONE = saved_clone
        if saved_env is None:
            os.environ.pop("TESTQ_CMD_DEPLOY", None)
        else:
            os.environ["TESTQ_CMD_DEPLOY"] = saved_env


def main():
    have = runner.src_mods_by_id()
    ok(have.get("mandrake.rm.luminouspigment") == "LuminousPigment", "src map names LuminousPigment by its folder",
       have.get("mandrake.rm.luminouspigment"))

    # 1. the instance
    cl = runner.deploy_closure("TerminalBiomes")
    ok("LuminousPigment" in cl, "TerminalBiomes' deploy closure carries LuminousPigment", cl)
    args = runner.deploy_args_for("TerminalBiomes")
    ok(args[:2] == ["--compose", "biomes"] and "LuminousPigment" in args[2:]
       and all(a == "--with" for a in args[2::2]), "TerminalBiomes deploys as --compose biomes --with ...", args)
    pre = uncovered("TerminalBiomes", ["--compose", "biomes"], have)       # the route before the fix
    ok("mandrake.rm.luminouspigment" in pre,
       "guard fails the pre-fix route on the instance (--compose biomes alone leaves luminouspigment out)", pre)
    # a closure member's own hard dependency rides too (2026-11-06: Pyrelands deployed UtinniPatches without the
    # WeatherSuite it hard-depends on; RUT_Umbra's PerpetualAuroraExtension went missing and braked the Steve lane)
    cl = runner.deploy_closure("Pyrelands")
    ok("UtinniPatches" in cl and "WeatherSuite" in cl and cl.index("WeatherSuite") < cl.index("UtinniPatches"),
       "Pyrelands' closure carries UtinniPatches' hard dependency WeatherSuite, before it", cl)
    pre = uncovered("HostileFlora", ["--compose", "biomes"], have)
    ok("HostileFlora" in pre, "guard sees a deploy that drops the mod under test itself", pre)

    # 2. the class guard
    bad, n = {}, 0
    for mod in all_mods():
        try:
            gap = uncovered(mod, runner.deploy_args_for(mod), have)
        except Exception as e:  # noqa: BLE001 - a mod whose closure will not compute is a finding, by name
            gap = ["%s: %s" % (type(e).__name__, str(e)[:120])]
        n += 1
        if gap:
            bad[mod] = gap
    ok(n >= 50, "guard swept the src tree (%d mods)" % n, n)
    ok(not bad, "every composed id of ours is deployed by its mod's own deploy", bad)

    # 3. deploy_custom_mods.py's argument checks accept the routes
    deploy_py = os.path.join(REPO, "src", "RimMandrake", "Utils", "deploy_custom_mods.py")
    probe = ("import runpy,sys; sys.argv=[%r]+sys.argv[1:]; g=runpy.run_path(%r, run_name='dcm');"
             "g['first_existing'].__globals__['first_existing']=lambda *a: sys.exit('PARSE_OK');"
             "sys.exit(g['main']())") % (deploy_py, deploy_py)
    for mod in ("TerminalBiomes", "Stillsand", "FlowWorks"):
        argv = runner.deploy_args_for(mod)
        r = subprocess.run([sys.executable, "-c", probe] + argv, capture_output=True, text=True, timeout=120, cwd=REPO)
        ok("PARSE_OK" in r.stderr and r.returncode == 1, "deploy_custom_mods.py accepts %s" % " ".join(argv),
           (r.returncode, r.stderr[-300:]))

    # 4. the worker reads it from the job's tree
    sys.path.insert(0, os.path.join(REPO, "infrastructure", "stevedesktop"))
    import worker  # noqa: E402
    got = worker.deploy_closure("TerminalBiomes", clone=REPO)
    ok("LuminousPigment" in got, "worker: TerminalBiomes job deploys LuminousPigment too", got)
    ok(worker.deploy_closure("NoSuchModAnywhere", clone=REPO) == [], "worker: a name with no src folder answers []")
    tmp = tempfile.mkdtemp(prefix="deploy_closure_")
    try:
        old = os.path.join(tmp, "old", "src", "RimMandrake", "Utils", "modcheck")
        os.makedirs(old)
        with open(os.path.join(old, "runner.py"), "w") as f:
            f.write("def composed_into(m):\n    return None\n")
        os.makedirs(os.path.join(tmp, "old", "src", "RimMandrake", "TerminalBiomes", "About"))
        open(os.path.join(tmp, "old", "src", "RimMandrake", "TerminalBiomes", "About", "About.xml"), "w").close()
        ok(worker.deploy_closure("TerminalBiomes", clone=os.path.join(tmp, "old")) == [],
           "worker: a job tree older than deploy_closure answers []")
        os.makedirs(os.path.join(tmp, "bare"))
        ok(worker.deploy_closure("TerminalBiomes", clone=os.path.join(tmp, "bare")) == [],
           "worker: a tree with no modcheck runner composes nothing and answers []")
        broken = os.path.join(tmp, "broken", "src", "RimMandrake", "Utils", "modcheck")
        os.makedirs(broken)
        with open(os.path.join(broken, "runner.py"), "w") as f:
            f.write("raise ImportError('torn checkout')\n")
        try:
            worker.deploy_closure("TerminalBiomes", clone=os.path.join(tmp, "broken"))
            ok(False, "worker: a modcheck runner that will not import raises")
        except RuntimeError:
            ok(True, "worker: a modcheck runner that will not import raises")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 5. Attempt.deploy itself hands the closure to the deploy command (a blind check found section 4 stays green
    # with the `mods += extra` line in deploy() taken out): both routes, the TESTQ_CMD_DEPLOY override and the
    # deploy_custom_mods.py plan, are driven with sh() recorded instead of run
    deploy_attempt(worker)

    print("ALL PASS" if not FAILS else "%d FAILED" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
