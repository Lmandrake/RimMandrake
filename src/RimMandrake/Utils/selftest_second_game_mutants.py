#!/usr/bin/env python3
# selftest-timeout: 1500
"""selftest_second_game_mutants.py - a planted fault in each second-game tool must turn its selftest red.

The faults were written down before the first run (mutate-your-checker). Each is one realistic regression: a kill by name
coming back, a site reading "any game" again, a blind list read as "no game". It runs in a temp copy, one at a time, with no
bytecode. An unmutated control must be green first, a plant that does not apply fails by name, and a kill only counts on
the selftest's own FAIL line: a crash is a separate verdict, because a broken copy reads as killing everything.

GM_ONLY=name,name runs some. Never plant in game_instance._exe: the shims' resolving first is what keeps a Linux pid away
from the real taskkill.
"""
import fnmatch
import glob
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GI, GP, RW = "src/RimMandrake/Utils/game_instance.py", "src/RimMandrake/Utils/game_paths.py", "infrastructure/stevedesktop/rw_game.sh"
LS = "src/RimMandrake/Utils/northstar_driver/live_session.py"
RS = "src/RimMandrake/rimflow/relentless_stage.py"
T_GI = "src/RimMandrake/Utils/selftest_game_instance.py"
T_ST = "src/RimMandrake/Utils/selftest_second_game_sites.py"
T_IK = "src/RimMandrake/rimflow/selftest_bridge_instance_key.py"
U = "src/RimMandrake/Utils/"
MB, LR = U + "modset_builder.py", "src/RimMandrake/bridgetools/launch_ready.py"
MO, CL, HG_, DL = ("src/RimMandrake/rimflow/%s.py" % n for n in ("model", "cli", "host_guard", "driver_lock"))

T_DL = "src/RimMandrake/Utils/selftest_bridge_deadlines.py"
COPY = ["src/RimMandrake/FlowWorks/northstar/*.py", "src/RimMandrake/Utils/*.py", "src/RimMandrake/Utils/*.json", "src/RimMandrake/Utils/northstar_driver/*.py",
        "src/RimMandrake/Utils/loadsweep/*.sh", "src/RimMandrake/Utils/rimbench/*.sh", "src/RimMandrake/rimflow/*.py",
        "src/RimMandrake/rimflow/*.json", "src/RimMandrake/bridgetools/*.py", "src/RimMandrake/Utils/modcheck/*.py",
        "src/RimMandrake/Utils/modcheck/live_queue/*.py", "src/RimMandrake/Utils/testq/*.py", "src/RimMandrake/Utils/art/enact.py",
        "infrastructure/stevedesktop/*", "infrastructure/state/modlists/ModsConfig.MINIMAL.xml"]
BY_NAME = 'taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1'

# (name, file, text, replacement, selftest, GI_ONLY sections)
MUTANTS = [
    ("owner_matches_substring", GI, 'parts[-2] == "instances" and re.fullmatch("[a-z]", parts[-1])', '"instances" in "/".join(parts)', T_GI, "owners"),
    ("owner_sees_only_game_a", GI, '        return parts[-1]\n', '        return DEFAULT\n', T_GI, "stop"),
    ("owner_misses_quoted_path", GI, '''"-savedatafolder=([^"]*)"|-savedatafolder="([^"]*)"|''', '', T_GI, "owners"),
    ("stop_kills_by_name", GI, '["/PID", str(p)]', '["/IM", GAME_EXE]', T_GI, "stop"),
    ("stop_takes_any_pid", GI, 'if pid_ is not None and pid_ not in mine:', 'if False:', T_GI, "stop"),
    ("stop_is_always_forced", GI, '(["/F"] if force else [])', '["/F"]', T_GI, "stop"),
    ("stop_with_no_pid_takes_all", GI, 'targets = [pid_] if pid_ is not None else mine', 'targets = [pid_] if pid_ is not None else [g["pid"] for g in games()]', T_GI, "stop"),
    ("blind_list_reads_as_no_game", GI, 'if r.returncode != 0 or LIST_OK not in lines:', 'if False:', T_GI, "blind"),
    ("unreadable_game_is_game_a", GI, '"instance": owner(cmd) if cmd else None', '"instance": owner(cmd)', T_GI, "blind"),
    ("running_ignores_unattributable", GI, 'g["instance"] in (name, None)', 'g["instance"] == name', T_GI, "blind"),
    ("port_ignores_the_index", GI, 'BASE_PORT + ord(check_name(name or current())) - ord("a")', 'BASE_PORT', T_GI, "names"),
    ("game_a_gets_an_environment", GI, '    if name == DEFAULT:\n        return {}\n', '    if name == DEFAULT:\n        return {"RM_GAME_INSTANCE": "a"}\n', T_GI, "names"),
    ("typo_falls_back_to_game_a", GI, 'return check_name(os.environ.get(INSTANCE_ENV, "").strip() or DEFAULT)', 'return (os.environ.get(INSTANCE_ENV, "").strip() + "a")[:1]', T_GI, "names"),
    ("token_rotates_every_read", GI, '    have = read_token(name)\n    if have:\n        return have\n', '', T_GI, "names"),
    ("wslenv_drops_the_token", GI, '"GABP_SERVER_PORT", "GABP_TOKEN",\n', '"GABP_SERVER_PORT",\n', T_GI, "names"),
    ("launch_starts_game_a", GI, 'if name == DEFAULT:\n        raise Refused("game a keeps', 'if False:\n        raise Refused("game a keeps', T_GI, "launch"),
    ("launch_without_steam_appid", GI, 'if not os.path.exists(os.path.join(game_paths.GAME_DIR, "steam_appid.txt")):', 'if False:', T_GI, "launch"),
    ("launch_without_steam", GI, 'if not _steam_running():', 'if False:', T_GI, "launch"),
    ("launch_token_is_not_the_file", GI, 'port(name), ensure_token(name), game_dir', 'port(name), "wrong", game_dir', T_GI, "launch"),
    ("launch_no_window_size", GI, '    text = _set_pref(_set_pref(text, "screenWidth", WINDOW[0], keep=True), "screenHeight", WINDOW[1], keep=True)\n', '', T_GI, "launch"),
    ("launch_overwrites_a_kept_size", GI, 'WINDOW[0], keep=True', 'WINDOW[0]', T_GI, "launch"),
    ("launch_keeps_the_old_log", GI, '        os.replace(log, log + ".prev")\n', '        pass\n', T_GI, "launch"),
    ("wait_never_sees_the_line", GI, '"%s %d" % (PORT_LINE, port(name)) in text', '"nothing like this" in text', T_GI, "launch"),
    ("wait_accepts_any_port", GI, '"%s %d" % (PORT_LINE, port(name)) in text', 'PORT_LINE in text', T_GI, "launch"),
    ("prepare_while_running", GI, '    if running(name):\n        raise Refused("game %s is running; it rewrites', '    if False:\n        raise Refused("game %s is running; it rewrites', T_GI, "launch"),
    ("paths_ignore_the_name", GP, 'not in ("", "a"):', 'in ("never",):', T_GI, "paths"),
    ("paths_import_on_nothing_set", GP, 'if os.environ.get("RM_GAME_INSTANCE", "").strip().lower() not in ("", "a"):\n    import sys', 'import game_instance as _touch\nif os.environ.get("RM_GAME_INSTANCE", "").strip().lower() not in ("", "a"):\n    import sys', T_GI, "paths"),
    ("rw_pid_is_always_game_a", RW, 'pid_of() { python3 "$GI" pid; }', 'pid_of() { python3 "$GI" pid a; }', T_GI, "rw_game"),
    ("rw_kills_by_name", RW, 'python3 "$GI" stop "$pid" >/dev/null\n', 'taskkill.exe /IM RimWorldWin64.exe >/dev/null\n', T_GI, "rw_game"),
    ("rw_keeps_game_a_folders", RW, 'eval "$_env"; NAMED=', 'NAMED=', T_GI, "rw_game"),
    ("rw_up_uses_game_a_route", RW, '    if [ -n "$NAMED" ]; then python3 "$GI" launch ${1:+"$1"}; return $?; fi\n', '', T_GI, "rw_game"),
    ("rw_init_uses_game_a_route", RW, '    if [ -n "$NAMED" ]; then python3 "$GI" prepare; return $?; fi\n', '', T_GI, "rw_game"),
    ("rw_blind_reads_as_stopped", RW, '''local pid; pid=$(pid_of) || { echo "REFUSED: the game list could not be read; nothing stopped"; return 2; }''', 'local pid; pid=$(pid_of)', T_GI, "rw_game"),
    ("session_kills_by_name", LS, '        game_instance.stop()\n', '        sh(["taskkill.exe", "/IM", "RimWorldWin64.exe"], timeout=60)\n', T_GI, "sites"),
    ("clock_kills_the_game", LS, '        game_instance.stop()\n', '        if time.time() - 0 > 1500:\n            game_instance.stop()\n', T_DL, ""),
    ("session_any_game_is_running", LS, '        return game_instance.running()\n', '        return "RimWorldWin64" in sh(["tasklist.exe"], timeout=60)[1]\n', T_GI, "sites"),
    ("stage_kills_by_name", RS, 'return self.instance().stop(force=force)', 'return self.sh(["taskkill.exe"] + (["/F"] if force else []) + ["/IM", "RimWorldWin64.exe"], timeout=60)', T_GI, "sites"),
    ("stage_any_game_is_running", RS, 'return self.instance().running()', 'return "RimWorldWin64" in self.sh(["tasklist.exe"], timeout=60)[1]', T_GI, "sites"),
    ("biome_proof_kills_by_name", "src/RimMandrake/Utils/loadsweep/biome_load_proof.sh", 'python3 "$REPO/src/RimMandrake/Utils/game_instance.py" stop --force >/dev/null', BY_NAME, T_GI, "sites"),
    ("sweep_kills_by_name", "src/RimMandrake/Utils/loadsweep/sweep_load.sh", 'python3 "$DIR/../game_instance.py" stop --force >/dev/null', BY_NAME, T_GI, "sites"),
    ("gl_sheet_kills_by_name", "src/RimMandrake/Utils/rimbench/gl_sheet_run.sh", 'python3 "$REPO/src/RimMandrake/Utils/game_instance.py" stop --force >/dev/null', BY_NAME, T_GI, "sites"),
    ("biome_proof_loses_its_refusal", "src/RimMandrake/Utils/loadsweep/biome_load_proof.sh", '[ "${RM_GAME_INSTANCE:-a}" = a ] || { echo "REFUSED: this launches through Steam, which can only start game a"; exit 2; }\n', '', T_GI, "sites"),
    ("modset_any_game_is_up", MB, 'return game_instance.running()      # this list', 'return "RimWorldWin64" in subprocess.run(["tasklist.exe"], capture_output=True, text=True).stdout  # this list', T_ST, "any"),
    ("modset_blind_reads_as_down", MB, "    except game_instance.Blind as e:\n        why = str(e)\n    print(", "    except game_instance.Blind as e:\n        return False\n    print(", T_ST, "any"),
    ("alive_any_game", U + "load_policy.py", "    if image == GAME_IMAGE:\n        import game_instance", "    if False:\n        import game_instance", T_ST, "any"),
    ("preflight_lists_every_game", U + "preflight_bridge.py", "for p in game_instance.procs()]", "for p in [dict(pid=g['pid'], start=g['start']) for g in game_instance.games()]]", T_ST, "any"),
    ("watchdog_first_process", U + "belt_watchdog.py", '$p = @GAME@\n', '$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1\n', T_ST, "picks"),
    ("watchdog_lists_every_game", U + "belt_watchdog.py", '@(@GAMES@ |', '@(Get-Process RimWorldWin64 -ErrorAction SilentlyContinue |', T_ST, "picks"),
    ("heal_first_process", U + "focus_heal.py", '$p = @GAME@\n', '$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1\n', T_ST, "picks"),
    ("focus_every_game", U + "game_focus.py", '$p = @GAME@\n', '$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue\n', T_ST, "picks"),
    ("atmosphere_first_process", U + "planet_atmosphere_cost.py", '$p = @GAME@\n', '$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1\n', T_ST, "picks"),
    ("coldstart_first_process", U + "coldstart_crashes.py", "\"$p = %s; if ($p) { $p.StartTime.ToUniversalTime().ToString('o') }\" % game_instance.ps_process()", "\"$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1; if ($p) { $p.StartTime.ToUniversalTime().ToString('o') }\"", T_ST, "picks"),
    ("testq_pid_blind_is_no_game", U + "testq/archmagi_phases.py", "        except game_instance.Blind:\n            return None\n", "        except game_instance.Blind:\n            return ''\n", T_ST, "picks"),
    ("ps_no_game_is_null", GI, 'else "@()"\n\n\ndef ps_processes', 'else "$null"\n\n\ndef ps_processes', T_ST, "picks"),
    ("launch_ready_kills_every_game", LR, 'return game_instance.procs()    # Blind', 'return [dict(pid=g["pid"], start=g["start"]) for g in game_instance.games()]    # Blind', T_ST, "launches"),
    ("launch_ready_b_uses_steam", LR, 'if game_instance.current() != game_instance.DEFAULT:    # Steam', 'if False:    # Steam', T_ST, "launches"),
    ("session_b_uses_steam", LS, 'if game_instance.current() != game_instance.DEFAULT:        # Steam', 'if False:        # Steam', T_ST, "launches"),
    ("stage_b_uses_steam", RS, 'if gi.current() != gi.DEFAULT:', 'if False:', T_ST, "launches"),
    ("prep_b_told_steam", U + "modcheck/live_queue/prep_wsl.py", 'print("next: launch directly -- python3 src/RimMandrake/Utils/game_instance.py launch --wait")', 'print("next: launch")', T_ST, "launches"),
    ("waiter_needs_the_token_line", U + "logwait.py", "(BRIDGE_LINES if token == BRIDGE_LINES[0] else (token,))", "(token,)", T_ST, "ready"),
    ("waiter_widens_every_wait", U + "logwait.py", "(BRIDGE_LINES if token == BRIDGE_LINES[0] else (token,))", "BRIDGE_LINES", T_ST, "ready"),
    ("gate_needs_the_token_line", U + "modcheck/launch_gate.py", "probe = PROBE in text or PORT_PROBE in text", "probe = PROBE in text", T_ST, "ready"),
    ("gate_any_log_is_current", U + "modcheck/launch_gate.py", "probe = PROBE in text or PORT_PROBE in text", "probe = True", T_ST, "ready"),
    ("ready_needs_the_token_line", LR, "    if game_instance.PORT_LINE in (text or \"\"):", "    if False:", T_ST, "ready"),
    ("preflight_needs_the_token_line", U + "preflight_bridge.py", " or game_instance.PORT_LINE in log ", " ", T_ST, "ready"),
    ("client_falls_through_to_game_a", U + "rimbridge_client.py", 'NAMED_GAME = os.environ.get("RM_GAME_INSTANCE", "").strip().lower() not in ("", "a")', "NAMED_GAME = False", T_ST, "endpoint"),
    ("client_name_beats_environment", U + "rimbridge_client.py", 'port = int(env_port) if env_port else (log_port or DEFAULT_PORT)', 'port = log_port or (int(env_port) if env_port else DEFAULT_PORT)', T_ST, "endpoint"),
    ("key_opens_imaginary_locks", MO, 'if machine not in BRIDGE_HOSTS or (dot and not re.fullmatch("[a-z]", inst)):', 'if machine not in BRIDGE_HOSTS:', T_IK, ""),
    ("key_a_is_a_second_lock", MO, 'return machine if inst == "a" else k ', 'return k ', T_IK, ""),
    ("key_b_is_game_a", MO, 'return machine if inst == "a" else k ', 'return machine ', T_IK, ""),
    ("ambient_ignores_the_name", MO, '    if inst in ("", "a"):\n        return None\n    return "%s.%s"', '    if True:\n        return None\n    return "%s.%s"', T_IK, ""),
    ("mirror_loses_the_line", CL, 'others=others)', 'others=None)', T_IK, ""),
    ("mirror_skips_other_host_takes", CL, '    _emit(ev, w, quiet=True)\n    _mirror_from_ledger(None)\n    print("%s bridge taken', '    _emit(ev, w, quiet=True)\n    print("%s bridge taken', T_IK, ""),
    ("guard_call_ignores_the_game", CL, 'with _cl.redirect_stdout(buf), host_guard.instance_env(inst):', 'with _cl.redirect_stdout(buf):', T_IK, ""),
    ("host_no_instance_suffix", HG_, 'return "%s.%s" % (machine, inst) if machine and inst not in ("", "a") else machine', 'return machine', T_IK, ""),
    ("remote_loses_the_game", HG_, '"RM_GAME_INSTANCE=%s " % inst if inst else ""', '""', T_IK, ""),
    ("remote_trusts_an_old_clone", HG_, "if inst else \"\"\n    cmd =", "if False else \"\"\n    cmd =", T_IK, ""),
    ("instance_env_not_restored", HG_, '        for k, v in saved.items():\n            if v is None:\n                os.environ.pop(k, None)\n            else:\n                os.environ[k] = v\n', '        pass\n', T_IK, ""),
    ("lock_ignores_the_name", DL, 'if (os.environ.get("RM_GAME_INSTANCE") or "").strip().lower() not in ("", "a"):\n        import game_instance ', 'if False:\n        import game_instance ', T_IK, ""),
]


def copy_tree(dst):
    n = 0
    for src in glob.glob(os.path.join(REPO, "src", "*", "*", "modcheck_env.py")):      # modset_builder reads these at import
        target = os.path.join(dst, os.path.relpath(src, REPO))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(src, target)
    for pattern in COPY:
        src_dir = os.path.join(REPO, os.path.dirname(pattern))
        for f in sorted(os.listdir(src_dir)) if os.path.isdir(src_dir) else []:
            src = os.path.join(src_dir, f)
            if fnmatch.fnmatch(f, os.path.basename(pattern)) and os.path.isfile(src):
                target = os.path.join(dst, os.path.dirname(pattern), f)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy2(src, target)
                n += 1
    return n


def run_selftest(tree, test, only):
    env = {k: v for k, v in os.environ.items() if k not in ("GI_ONLY", "GM_ONLY")}
    env.update(GI_ONLY=only, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, os.path.join(tree, test)], env=env, capture_output=True, text=True, timeout=420,
                       stdin=subprocess.DEVNULL, cwd=tree)
    return p.returncode, p.stdout, p.stderr


def main():
    table = MUTANTS
    only = [s for s in os.environ.get("GM_ONLY", "").split(",") if s]
    tree = tempfile.mkdtemp(prefix="second_game_mutants_")
    bad = []
    try:
        print("copied %d files" % copy_tree(tree))
        for test, sections in sorted({(m[4], m[5]) for m in table if not only or m[0] in only}):
            rc, out, err = run_selftest(tree, test, sections)
            if rc != 0:
                print("CONTROL RED: %s [%s]\n%s\n%s" % (test, sections, out[-1500:], err[-800:]))
                return 1
            print("control green: %s [%s]" % (os.path.basename(test), sections))
        for name, rel, old, new, test, sections in table:
            if only and name not in only:
                continue
            path = os.path.join(tree, rel)
            with open(path, encoding="utf-8", newline="") as f:
                clean = f.read()
            if clean.count(old) < 1 or clean.replace(old, new) == clean:
                print("NOT APPLIED  %s: its anchor is gone from %s" % (name, rel))
                bad.append(name)
                continue
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(clean.replace(old, new))
            try:
                rc, out, err = run_selftest(tree, test, sections)
            except subprocess.TimeoutExpired:
                rc, out, err = -1, "", "timed out"
            finally:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(clean)
            own = [ln for ln in out.splitlines() if ln.startswith("FAIL ") and "selftest_" not in ln[:24]]
            if rc != 0 and own:
                print("caught       %-34s %s" % (name, own[0][5:115]))
            elif rc != 0:
                print("CRASHED      %-34s %s" % (name, (err or out)[-200:].replace("\n", " | ")))
                bad.append(name)
            else:
                print("SURVIVED     %s" % name)
                bad.append(name)
    finally:
        shutil.rmtree(tree, ignore_errors=True)
    print("%s selftest_second_game_mutants: %d of %d not caught: %s" % ("FAIL" if bad else "PASS", len(bad), len(table), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
