#!/usr/bin/env python3
"""selftest_dispatch_two_games.py - the Dispatch tick and the pilot launches pick a FREE game of the two, by themselves.

RIMMANDRAKE_LAUNCH_BOTH_GAMES_STEAM_REFUSES_A_BESIDE_B. The owner, 2026-11-16 9:23 PM PST: "don't forget we have two
Rimworld games, so I don't want to hear any 'waiting for game'". The tick used to hold every in-game visit while ANY
in-game run was live, and read only game a's bridge, so a free game b never took a run. Now each game in
maturation_dispatch.json's game_instances is free when no live driver's run record names it (RM_GAME_INSTANCE in the
unit's env, else a) and its own `rimflow bridge idle` says takeable; the first free one is the run's, and reaches the
unit as --env RM_GAME_INSTANCE=<game> and in its brief. A held game is never handed out, and nothing here stops a game.
Written before the code and watched failing on the base; the bridge is the world's stand-in, never the real one.
The JawaBench companion is a stand-in too (RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH): the companion gate
(63388ebcfb) landed after this file, so every launch here read the game folder's real DLL, passing only on a machine whose
deployed companion was FRESH and failing five cases on a Mac or in a container. MATURATION_COMPANION_DLL now names a file
that does not exist, so a launch that still reads the real companion refuses and its case FAILS, never passes by luck.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import selftest_maturation_dispatch as SD  # noqa: E402
import selftest_maturation as SM  # noqa: E402
import maturation as M  # noqa: E402
import maturation_dispatch as MD  # noqa: E402
import game_names as _GN  # noqa: E402  (a game reads by its name on this machine: ArchBig, ArchSmall)

FAILS = []


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:160])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    root = tempfile.mkdtemp(prefix="dispatch_two_games_")
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
            "RM_MATURATION_DISPATCH_DIR", "FAKE_DH_FAIL", "MATURATION_BRIDGE_IDLE", "FAKE_IDLE", "FAKE_IDLE_LOG", M.COMPANION_ENV)
    env_was = {k: os.environ.get(k) for k in keys}
    rec_was = MD.DH.read_record
    try:
        SM.copy_ingame(root)
        SM.copy_ingame(root, as_mod="PyrelandsTwin")
        fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        idle, ilog = os.path.join(root, "fake_idle.py"), os.path.join(root, "fake_idle.log")
        with open(fake, "w") as f:
            f.write(SD.FAKE_DH)
        with open(idle, "w") as f:
            f.write(SM.FAKE_IDLE)
        open(log, "w").close()
        open(ilog, "w").close()
        sd = os.path.join(root, "state")
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(SM.INGAME_CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"), RM_MATURATION_DISPATCH_DIR=sd,
                          MATURATION_BRIDGE_IDLE=idle, FAKE_IDLE="NOT", FAKE_IDLE_LOG=ilog,
                          **{M.COMPANION_ENV: os.path.join(root, "no_companion_here.dll")})
        os.environ.pop("FAKE_DH_FAIL", None)
        T0 = SM.INGAME_CLOCK
        world = {"live": {}, "runs": {}, "held": {}, "records": {}}
        asked = []

        def bridge(p, game="a"):        # a reading that can name the game: one verdict per game
            asked.append(game)
            why = world["held"].get(game)
            return (False, "NOT TAKEABLE  %s" % why) if why else (True, "TAKEABLE  free")

        def lbridge(p, s, game="a"):    # launch_mod's reading (purpose, seat)
            return bridge(p, game=game)

        def fresh(game="a"):            # the companion stand-in: current on both games (one install serves both)
            return True, "test stand-in: companion FRESH on game %s" % game

        MD.DH.read_record = lambda unit, root=None: world["records"].get(unit)

        def launches():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        def env_of(argv):
            return [argv[i + 1] for i, x in enumerate(argv) if x == "--env"]

        def brief_of(argv):
            with open(argv[argv.index("--brief-file") + 1], encoding="utf-8") as f:
                return f.read()

        def facts_for(c):
            out = {}
            for mod in c["advancing"]:
                f = M.build_facts(root, mod)
                f["live_units"] = list(world["live"].get(mod, []))
                f["last_end"], f["stage_runs"], f["run_tokens"] = None, {}, {}
                runs = world["runs"].get(mod, [])
                out[mod] = MD.add_ingame(root, mod, MD.add_blind(root, mod, f, runs), runs)
            return out

        fx = {"autonomy": False, "convergence": SD.no_convergence, "account": lambda: (True, "test account KEEP"),
              "known": lambda: set(), "bridge": bridge,
              "file": lambda item, title, why, **kw: (True, "filed %s" % item),
              "launch": lambda mod, cap, item, **kw: M.launch_mod(root, mod, cap, item, model="opus", seat="BENCH",
                                                                  bridge=lbridge,
                                                                  **dict({"companion": fresh,
                                                                          "deployed": lambda r_, m_: (True, "in sync")},
                                                                         **kw))}

        def tick(c, at=0):
            return MD.tick(root, c, True, fx=dict(fx, facts=lambda: facts_for(c)), now=T0 + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del asked[:]
            world.update(live={}, runs={}, held={}, records={})

        def dec(rd, mod="Pyrelands"):
            return rd["mods"][mod]["decision"]

        base = SD.load_cfg()
        two = dict(base, advancing=["Pyrelands", "PyrelandsTwin"], ingame_enabled=True, max_live=5,
                   game_instances=["a", "b"])
        other_live = [{"unit": "rm-detached-x", "item": "RIMMANDRAKE_DRIVE_PYRELANDSTWIN_IN_GAME_ACCEPTANCE_VISIT_ONE",
                       "live": True, "at": T0}]

        chk(lambda: MD.load_cfg().get("game_instances") == ["a", "b"],
            "the shipped settings name both games: %s" % MD.load_cfg().get("game_instances"))

        rd = [None]

        def t_two_mods_two_games():
            reset()
            rd[0] = tick(two)
            ls = launches()
            return (dec(rd[0]) == "launched" and dec(rd[0], "PyrelandsTwin") == "launched" and len(ls) == 2
                    and env_of(ls[0]).count("RM_GAME_INSTANCE=a") == 1 and env_of(ls[1]).count("RM_GAME_INSTANCE=b") == 1)
        chk(t_two_mods_two_games, "two mods owed a visit, both games free: one launches on game a, the other on game b, "
                                  "each with RM_GAME_INSTANCE")

        def t_brief_names_game():
            ls = launches()
            return ls and "RM_GAME_INSTANCE=b" in brief_of(ls[1]) and "game_instance.py launch %s" % _GN.show("b") in brief_of(ls[1])
        chk(t_brief_names_game, "the run's brief names its game and how to start it")

        def t_driver_on_a():
            reset()
            world["runs"]["PyrelandsTwin"] = other_live
            world["live"]["PyrelandsTwin"] = ["rm-detached-x"]
            world["records"]["rm-detached-x"] = {"env": {"RM_GAME_INSTANCE": "a"}}
            rd[0] = tick(dict(two, advancing=["Pyrelands", "PyrelandsTwin"]))
            ls = launches()
            return (dec(rd[0]) == "launched" and len(ls) == 1 and "RM_GAME_INSTANCE=b" in env_of(ls[0])
                    and "a" not in asked)
        chk(t_driver_on_a, "an in-game run live on game a: the visit launches on game b, a's bridge not even asked")

        def t_hand_driver_unknown_game():
            reset()
            world["runs"]["PyrelandsTwin"] = other_live
            world["live"]["PyrelandsTwin"] = ["rm-detached-x"]          # no run record: a hand launch drives game a
            rd[0] = tick(two)
            ls = launches()
            return dec(rd[0]) == "launched" and len(ls) == 1 and "RM_GAME_INSTANCE=b" in env_of(ls[0])
        chk(t_hand_driver_unknown_game, "a live driver with no game in its record counts as game a's: b is used")

        def t_a_held_b_free():
            reset()
            world["held"]["a"] = "driver lock held by CONDUCTOR (another seat)"
            rd[0] = tick(dict(two, advancing=["Pyrelands"]))
            ls = launches()
            return dec(rd[0]) == "launched" and len(ls) == 1 and "RM_GAME_INSTANCE=b" in env_of(ls[0])
        chk(t_a_held_b_free, "game a's bridge held by another seat, b free: launched on b, never 'waiting for game'")

        def t_both_unavailable():
            reset()
            world["runs"]["PyrelandsTwin"] = other_live
            world["live"]["PyrelandsTwin"] = ["rm-detached-x"]
            world["records"]["rm-detached-x"] = {"env": {"RM_GAME_INSTANCE": "a"}}
            world["held"]["b"] = "bridge held by BENCH for: pyre week run 2"
            rd[0] = tick(two)
            why = rd[0]["mods"]["Pyrelands"]["why"]
            return (dec(rd[0]) in ("bridge_held", "driver_busy") and not launches() and _GN.show("a") in why
                    and _GN.show("b") in why)
        chk(t_both_unavailable, "a driven by a live run and b held: nothing launches, and the line says why for each game")

        def t_single_game_setting():
            reset()
            world["runs"]["PyrelandsTwin"] = other_live
            world["live"]["PyrelandsTwin"] = ["rm-detached-x"]
            rd[0] = tick(dict(two, game_instances=["a"]))
            return dec(rd[0]) == "driver_busy" and not launches()
        chk(t_single_game_setting, "game_instances [a]: one game, the old one-driver rule holds")

        def t_launch_mod_reads_its_game():
            reset()
            world["held"]["b"] = "held by OTHER"
            r = M.launch_mod(root, "Pyrelands", 20, "RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_ONE",
                             bridge=lbridge, env={"RM_GAME_INSTANCE": "b"})
            return r[0] == 2 and _GN.show("b") in r[1] and not launches()
        chk(t_launch_mod_reads_its_game, "launch_mod checks the bridge of the run's own game (b held: refused, says b)")

        def t_real_companion_never_read():
            reset()
            r = M.launch_mod(root, "Pyrelands", 20, "RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_ONE",
                             bridge=lbridge, env={"RM_GAME_INSTANCE": "b"})
            return r[0] == 2 and "MISSING %s" % os.environ[M.COMPANION_ENV] in r[1] and not launches()
        chk(t_real_companion_never_read, "tripwire: with no stand-in the companion read is this test's missing file, so "
                                         "the visit is refused by name (no case can pass on the machine's real DLL)")

        def t_bridge_idle_names_game():
            envlog = os.path.join(root, "idle_env.log")
            spy = os.path.join(root, "idle_env.py")
            with open(spy, "w") as f:
                f.write("import os\nopen(%r, 'a').write('RM_GAME_INSTANCE=%%s\\n' %% os.environ.get('RM_GAME_INSTANCE'))\n"
                        "print('TAKEABLE  free')\n" % envlog)
            os.environ["MATURATION_BRIDGE_IDLE"] = spy
            try:
                got_b = M.bridge_idle("probe", "BENCH", game="b")
                os.environ["RM_GAME_INSTANCE"] = "b"           # a b-shell asking about game a
                got_a = M.bridge_idle("probe", "BENCH", game="a")
            finally:
                os.environ.pop("RM_GAME_INSTANCE", None)
                os.environ["MATURATION_BRIDGE_IDLE"] = idle
            with open(envlog) as f:
                seen = f.read().split()
            return got_b[0] and got_a[0] and seen == ["RM_GAME_INSTANCE=b", "RM_GAME_INSTANCE=None"]
        chk(t_bridge_idle_names_game, "maturation.bridge_idle asks rimflow about the named game (RM_GAME_INSTANCE=b)")
        def t_live_holder_not_takeable():
            """seat BENCH reads another BENCH run's hold as ours: a live holder process on the game's driver lock is
            not takeable, whatever rimflow's TAKEABLE line says (the real host_guard, on a fake machine's lock)."""
            import subprocess
            sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
            import fake_two_games as F
            w = F.World(F.REPO)
            saved = dict(os.environ)
            holder = None
            try:
                os.environ.pop("MATURATION_BRIDGE_IDLE", None)
                os.environ.update({k: v for k, v in w.env.items() if k.startswith(("RIMFLOW_", "RM_INSTANCES_ROOT"))})
                said = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "TAKEABLE  delegated: bridge idle (ours)\n", "")
                free_before = M.bridge_idle("probe", "BENCH", runner=said, game="a")[0]
                holder = subprocess.Popen([sys.executable, os.path.join(HERE, "host_guard.py"), "run", "--seat", "BENCH",
                                           "--for", "another BENCH run drives a", "--", "sleep", "60"],
                                          env=dict(w.env, RM_HOST="archmagi"), stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
                for _ in range(100):
                    if os.path.exists(w.env["RIMFLOW_DRIVER_LOCK"]):
                        break
                    F.time.sleep(0.05)
                F.time.sleep(0.3)
                go, why = M.bridge_idle("probe", "BENCH", runner=said, game="a")
                return free_before and not go and "another BENCH run drives a" in why
            finally:
                if holder:
                    holder.kill()
                    holder.wait()
                os.environ.clear()
                os.environ.update(saved)
                w.close()
        what = "a live BENCH holder on the game's lock: bridge_idle says NOT TAKEABLE, though rimflow reads the hold as ours"
        if os.path.isdir("/proc"):
            chk(t_live_holder_not_takeable, what)
        else:   # fake_two_games' machine finds and clears its processes through /proc (Linux only), as seat_restart's R4
            print("UNMEASURED, not a pass or a fail — %s: fake_two_games lists its processes through /proc, which %s "
                  "has none of" % (what, sys.platform))
    finally:
        MD.DH.read_record = rec_was
        for k, v in env_was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)
    print("%s selftest_dispatch_two_games: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
