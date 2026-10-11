"""Keep the Windows side of telemetry running: VictoriaMetrics, Grafana, telemetryd.

Run every minute by the Windows scheduled task "RimMandrake\\Telemetry" (no elevation:
`schtasks /SC MINUTE` works as the owner's user, like "RimMandrake\\TPS Observer"). Each run is a
few milliseconds when all is well: it reads the pid files, checks each pid still runs the
expected exe, and starts whatever is missing, detached, with no console window. telemetryd is
also restarted when its code (in the mirror D:\\Luke\\dev\\RimMandrake) changes, so a push is a deploy.

Lives on Windows on purpose (design §5): it survives `wsl --shutdown`, which is exactly when disk
and memory telemetry matter. From WSL: `telemetry up` / `telemetry down` / `telemetry health`.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import host  # noqa: E402
from tcommon import CODE_DIR, cfg, read_json, write_json_atomic  # noqa: E402

NEW_GROUP = 0x00000200
NO_WINDOW = 0x08000000
BREAKAWAY = 0x01000000


def specs() -> dict:
    c = cfg()
    b = c["bin"]
    py = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(py):
        py = sys.executable
    graf_home = os.path.join(b, "grafana")
    return {
        "victoriametrics": {
            "exe": os.path.join(b, "victoria-metrics-windows-amd64-prod.exe"),
            "args": [f"-storageDataPath={os.path.join(c['root'], 'vm')}", f"-retentionPeriod={c['vm_retention']}",
                     "-httpListenAddr=127.0.0.1:8428", "-loggerOutput=stderr",
                     "-search.latencyOffset=1s", "-memory.allowedPercent=10"],
            "cwd": c["root"], "log": "victoriametrics.log",
        },
        "grafana": {
            "exe": os.path.join(graf_home, "bin", "grafana.exe"),
            "args": ["server", "--homepath", graf_home, "--config", os.path.join(c["root"], "grafana", "custom.ini")],
            "cwd": graf_home, "log": "grafana.log",
        },
        "telemetryd": {
            "exe": py, "args": [os.path.join(CODE_DIR, "telemetryd.py")], "cwd": c["root"], "log": "telemetryd.out",
            "code": True,
        },
    }


def _alive(pid: int | None, exe: str) -> bool:
    if not pid:
        return False
    names = host.process_pids({os.path.basename(exe).lower()})
    return pid in names.get(os.path.basename(exe).lower(), [])


def _kill(pid: int) -> None:
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, creationflags=NO_WINDOW,
                   stdin=subprocess.DEVNULL)


def ensure(name: str, sp: dict, pids: dict, code: str | None) -> str:
    rec = pids.get(name) or {}
    if not os.path.exists(sp["exe"]):
        return "NOT INSTALLED"
    if sp.get("code"):
        # The Store python launcher's pid is not the interpreter's, so telemetryd is judged by its own
        # heartbeat (pid + code it writes itself), never by the pid Popen returned.
        hb = read_json(os.path.join(cfg()["state"], "heartbeat.json")) or {}
        fresh = time.time() - hb.get("at", 0) < 90
        alive = fresh and host.pid_alive(hb.get("pid"))
        if not alive and time.time() - rec.get("started", 0) < 90:
            return "starting"
        rec = {**rec, "pid": hb.get("pid") if alive else None, "code": hb.get("code")}
    else:
        alive = _alive(rec.get("pid"), sp["exe"])
    if alive and sp.get("code") and code and rec.get("code") != code:
        _kill(rec["pid"])
        alive = False
        status = "restarted (code changed)"
    else:
        status = "up" if alive else "started"
    if alive:
        return status
    logf = open(os.path.join(cfg()["logs"], sp["log"]), "ab")
    # NO DETACHED_PROCESS: a detached parent has no console, so every console child it spawns
    # (Grafana's gpx_* plugin backends) gets its OWN VISIBLE window — that popped windows on the
    # owner's desktop (2026-10-11, "STOP THE GRAFANA WINDOWS"). CREATE_NO_WINDOW gives the child a
    # hidden console that its children inherit; SW_HIDE covers GUI-subsystem children.
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0  # SW_HIDE
    flags = NEW_GROUP | NO_WINDOW
    try:
        p = subprocess.Popen([sp["exe"], *sp["args"]], cwd=sp["cwd"], stdout=logf, stderr=logf, startupinfo=si,
                             stdin=subprocess.DEVNULL, creationflags=flags | BREAKAWAY, close_fds=True)
    except OSError:  # breakaway refused by the job object: start without it
        p = subprocess.Popen([sp["exe"], *sp["args"]], cwd=sp["cwd"], stdout=logf, stderr=logf, startupinfo=si,
                             stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
    pids[name] = {"pid": p.pid, "started": time.time(), "code": code if sp.get("code") else None}
    return status


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    c = cfg()
    for d in ("state", "logs"):
        os.makedirs(c[d], exist_ok=True)
    pf = os.path.join(c["state"], "pids.json")
    pids = read_json(pf, {}) or {}
    if os.path.exists(os.path.join(c["state"], "DISABLED")) and "--force" not in argv:
        return 0
    if argv[:1] == ["stop"]:
        for name, rec in pids.items():
            if rec.get("pid"):
                _kill(rec["pid"])
        write_json_atomic(pf, {})
        print("stopped")
        return 0
    from telemetryd import code_hash
    code = code_hash()
    out = {}
    for name, sp in specs().items():
        out[name] = ensure(name, sp, pids, code)
        if name == "victoriametrics" and out[name] == "started":
            time.sleep(2)   # let VM bind before telemetryd's first flush (it spools otherwise)
    write_json_atomic(pf, pids)
    write_json_atomic(os.path.join(c["state"], "supervise.json"), {"at": time.time(), "status": out, "code": code})
    if "--print" in argv:
        print(" · ".join(f"{k}: {v}" for k, v in out.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
