"""One bounded live attempt; always stop the game and release SteveDesktop."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
ATTEMPT = EVIDENCE / (sys.argv[1] if len(sys.argv) > 1 else "live_run_1")
ATTEMPT.mkdir(exist_ok=False)
ENV = dict(os.environ)
TIER = "mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_hugethingstestraces__mandrake_rm_patches"
GAME = ["bash", "/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh"]
BRIDGE = ["python3", "src/RimMandrake/rimflow/cli.py", "bridge"]
ENV_FILE = "/home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh"
summary = {"started_utc": datetime.now(timezone.utc).isoformat(), "commands": [], "ok": False}


def run(name, args, require=True, timeout=900):
    command = "source " + ENV_FILE + "\nexport RIMFLOW_SEAT=BENCH RM_CODEX_SIDE=wsl\n" + shlex.join(args)
    started = time.time()
    p = subprocess.run(["bash", "-c", command], cwd=ROOT, env=ENV, capture_output=True, timeout=timeout)
    # Never persist credentials, including an unexpected token-bearing helper tail.
    def safe(data):
        return b"\n".join(b"[credential line redacted]" if re.search(
            rb"bridge token:|authorization:|bearer ", line, re.I) else line for line in data.split(b"\n"))
    (ATTEMPT / (name + ".stdout")).write_bytes(safe(p.stdout))
    (ATTEMPT / (name + ".stderr")).write_bytes(safe(p.stderr))
    (ATTEMPT / (name + ".rc")).write_text(str(p.returncode) + "\n")
    summary["commands"].append({"name": name, "args": args, "rc": p.returncode, "elapsed_s": time.time() - started})
    (ATTEMPT / "receipt.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(name, "rc", p.returncode, flush=True)
    if require and p.returncode:
        raise RuntimeError(name + " failed; inspect raw receipts")
    return p


def preflight(name, live=False):
    path = ATTEMPT / (name + ".json")
    args = ["/home/mandrake/.cache/ht-warning-venv/bin/python3", "src/RimMandrake/Utils/preflight_bridge.py", "--tier", "quicktest", "--modset", TIER,
            "--deep", "--all", "--seat", "BENCH", "--json", str(path)]
    if live:
        args += ["--live"]
    run(name, args, require=False)
    report = json.loads(path.read_text())
    bad = [r for r in report["rows"] if r["required"] and r["id"] != "O02" and r["status"] != "PASS"]
    lease = [r for r in report["rows"] if r["id"] == "O02"]
    assessment = {"O02_actual": lease, "O02_applicability": "not applicable: reads other host Archmagi BRIDGE; owner exception",
                  "other_required_nonpasses": bad, "ok": not bad}
    (ATTEMPT / (name + "_assessment.json")).write_text(json.dumps(assessment, indent=2) + "\n")
    if bad:
        raise RuntimeError(name + " has required nonpasses: " + str([(r["id"], r["status"]) for r in bad]))


def inspect_log(name):
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    import game_paths
    p = Path(game_paths.PLAYER_LOG)
    lines = p.read_text(errors="replace").splitlines()
    exceptions = [(i + 1, s) for i, s in enumerate(lines) if re.search(r"Exception|Traceback", s)]
    configs = [(i + 1, s) for i, s in enumerate(lines) if "Config error" in s]
    selected = ([exceptions[0]] if exceptions else []) + configs
    selected = [(i, s) for i, s in selected if not re.search(r"token|authorization|bearer", s, re.I)]
    r = {"log_path": str(p), "first_exception": selected[0] if exceptions and selected else None,
         "exception_line_count": len(exceptions), "config_error_count": len(configs), "selected_lines": selected}
    (ATTEMPT / (name + ".json")).write_text(json.dumps(r, indent=2) + "\n")
    return r


held = False
try:
    run("readiness_python", ["/home/mandrake/.cache/ht-warning-venv/bin/python3", "-c",
                             "import sys,lxml; print(sys.executable); print(lxml.__version__)"])
    # The task inherits the parent driver's generation. Verify it before using its PID override.
    p = run("guard_before", ["python3", "src/RimMandrake/rimflow/host_guard.py", "status", "--json"])
    guard = json.loads(p.stdout)
    if str(guard["generation"]) != ENV.get("RM_HOST_GUARD_GEN") or guard["seat"] != "BENCH":
        raise RuntimeError("inherited host generation is not the actual BENCH holder")
    ENV["RM_DRIVER_PID"] = str(guard["identity"]["pid"])
    summary["inherited_driver"] = guard
    run("take", BRIDGE + ["take", "--host", "stevedesktop", "--idle-ok", "--for",
                          "HT: TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS"])
    held = True
    run("lease_before", BRIDGE + ["who", "--host", "stevedesktop"])
    run("game_before", GAME + ["status"], require=False)
    # Python-only diagnostic change: reviewed full plan is in sync; no apply.
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    import game_paths
    compared = {}
    for rel in ("Assemblies/RM_HugeThings.dll", "Assemblies/RM_HugeThings.dll.srchash"):
        pair = [hashlib.sha256(p.read_bytes()).hexdigest() for p in
                (ROOT / "src/RimMandrake/HugeThings" / rel, Path(game_paths.LOCAL_MODS) / "HugeThings" / rel)]
        compared[rel] = pair
        if pair[0] != pair[1]:
            raise RuntimeError("deployed bytes differ; parent coordination needed: " + rel)
    (ATTEMPT / "deploy_bytes.json").write_text(json.dumps(compared, indent=2) + "\n")
    preflight("preflight_offline")
    # Scoped adapter: rw_game.sh remains the sole game-control entry point; its launch goes through Steam.
    real = run("powershell_path", ["which", "powershell.exe"]).stdout.decode().strip()
    ENV["HT_POWERSHELL_REAL"] = real
    ENV["PATH"] = str(ROOT / "whittle/ht-two-hour-warning/evidence/steam_adapter") + os.pathsep + ENV["PATH"]
    launch = run("up", GAME + ["up", "--wait"], require=False)
    # Steam can return before process creation. Observe status, never issue a second launch.
    if launch.returncode:
        for attempt in range(12):
            time.sleep(5)
            p = run("delayed_status_" + str(attempt), GAME + ["status"], require=False)
            if p.returncode == 0 and b"bridge port in Player.log: 5174" in p.stdout:
                break
        else:
            raise RuntimeError("Steam launch did not establish a process/bridge")
    time.sleep(45)  # main-thread bridge readiness after the listener announces
    preflight("preflight_live", live=True)
    log = inspect_log("player_log_inspection")
    if log["exception_line_count"] or log["config_error_count"]:
        raise RuntimeError("Player.log has an exception/config error; inspect first cause")
    run("running_identity", ["/home/mandrake/.cache/ht-warning-venv/bin/python3", "src/RimMandrake/Utils/preflight_bridge.py", "--emit-running-mods"])
    run("lease_live", BRIDGE + ["who", "--host", "stevedesktop"])
    script = ROOT / "src/RimMandrake/HugeThings/northstar/roofwall_modes_live.py"
    script_win = run("script_winpath", ["wslpath", "-w", str(script)]).stdout.decode().strip()
    out_win = run("out_winpath", ["wslpath", "-w", str(ATTEMPT / "live.json")]).stdout.decode().strip()
    run("probe", ["python.exe", script_win, "--out", out_win], timeout=600)
    live = json.loads((ATTEMPT / "live.json").read_text())
    if not live.get("ok") or not live["restoration"]["ok"]:
        raise RuntimeError("live contract or exact readback restoration failed")
    log = inspect_log("player_log_after_probe")
    if log["exception_line_count"] or log["config_error_count"]:
        raise RuntimeError("fresh probe log has exception/config errors")
    summary["ok"] = True
except Exception as exc:
    summary["error"] = str(exc)
    print("FAILED:", exc, flush=True)
finally:
    if held:
        try:
            run("down_finally", GAME + ["down"])
        except Exception as exc:
            summary["down_error"] = str(exc)
            summary["ok"] = False
        try:
            run("game_after", GAME + ["status"], require=False)
            run("release", BRIDGE + ["release", "--host", "stevedesktop"])
            run("lease_after", BRIDGE + ["who", "--host", "stevedesktop"])
            run("guard_after", ["python3", "src/RimMandrake/rimflow/host_guard.py", "status", "--json"])
        except Exception as exc:
            summary["release_error"] = str(exc)
            summary["ok"] = False
    summary["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (ATTEMPT / "receipt.json").write_text(json.dumps(summary, indent=2) + "\n")
sys.exit(0 if summary["ok"] else 1)
