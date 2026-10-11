#!/usr/bin/env python3
"""Install / repair the telemetry stack. Idempotent; run from WSL: `python3 install.py [--no-download]`.

Windows side (no elevation needed):
  E:\\telemetry\\bin\\victoria-metrics-windows-amd64-prod.exe   (sha256 checked against the release)
  E:\\telemetry\\bin\\grafana\\                                 (Grafana OSS zip, extracted)
  E:\\telemetry\\grafana\\plugins\\frser-sqlite-datasource\\     (SQLite datasource plugin)
  E:\\telemetry\\grafana\\custom.ini                            (rendered from grafana/custom.ini.template)
  scheduled task "RimMandrake\\Telemetry"  every minute: pythonw supervise.py (from the MIRROR)
WSL side:
  ~/.config/systemd/user/rm-telemetry-{export,health}.{service,timer}  (copied from ./systemd)
  ~/.local/bin/telemetry -> this directory's `telemetry` wrapper

Pinned versions are below; bump them here, re-run, commit.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_W = "E:\\telemetry"
ROOT = "/mnt/e/telemetry"
MIRROR_W = "D:\\Luke\\dev\\RimMandrake"
MIRROR_CODE_W = MIRROR_W + "\\src\\RimMandrake\\Utils\\telemetry"
VM_VER = "v1.153.0"
VM_ZIP = f"victoria-metrics-windows-amd64-{VM_VER}.zip"
VM_URL = f"https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/{VM_VER}/"
GRAFANA_VER = "13.2.3"
GRAFANA_ZIP = f"grafana-{GRAFANA_VER}.windows-amd64.zip"
GRAFANA_URL = f"https://dl.grafana.com/oss/release/{GRAFANA_ZIP}"
SQLITE_PLUGIN_URL = ("https://grafana.com/api/plugins/frser-sqlite-datasource/versions/latest/download"
                     "?os=windows&arch=amd64")
TASK = "RimMandrake\\Telemetry"
UNITS = ["rm-telemetry-export.service", "rm-telemetry-export.timer",
         "rm-telemetry-health.service", "rm-telemetry-health.timer"]


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def pywin(code: str) -> str:
    r = sh(["python.exe", "-c", code])
    if r.returncode:
        raise SystemExit(f"python.exe failed: {r.stderr[-800:]}")
    return r.stdout


def fetch(url: str, dst: str) -> None:
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return
    print(f"  download {url}")
    with urllib.request.urlopen(url, timeout=600) as r, open(dst + ".part", "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(dst + ".part", dst)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not os.path.isdir("/mnt/e"):
        print("E: is not mounted: refusing (the store lives on E:, owner's pick)")
        return 2
    for d in ("bin", "dl", "vm", "grafana/data", "grafana/logs", "grafana/plugins", "raw", "state", "inbox/changes",
              "inbox/wsl", "logs"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    dl = os.path.join(ROOT, "dl")
    if "--no-download" not in argv:
        fetch(VM_URL + VM_ZIP, os.path.join(dl, VM_ZIP))
        fetch(VM_URL + VM_ZIP.replace(".zip", "_checksums.txt"), os.path.join(dl, VM_ZIP.replace(".zip", "_checksums.txt")))
        fetch(GRAFANA_URL, os.path.join(dl, GRAFANA_ZIP))
        fetch(SQLITE_PLUGIN_URL, os.path.join(dl, "sqlite-plugin.zip"))
    # VictoriaMetrics: verify the zip against the release checksum file
    want = open(os.path.join(dl, VM_ZIP.replace(".zip", "_checksums.txt"))).read()
    got = hashlib.sha256(open(os.path.join(dl, VM_ZIP), "rb").read()).hexdigest()
    if got not in want:
        print(f"REFUSING: {VM_ZIP} sha256 {got} not in the release checksums")
        return 1
    vm_exe = os.path.join(ROOT, "bin", "victoria-metrics-windows-amd64-prod.exe")
    marker = os.path.join(ROOT, "bin", "VERSIONS.txt")
    have = open(marker).read() if os.path.exists(marker) else ""
    if VM_VER not in have or not os.path.exists(vm_exe):
        print("  extract VictoriaMetrics")
        pywin(f"import zipfile;zipfile.ZipFile(r'{ROOT_W}\\dl\\{VM_ZIP}').extractall(r'{ROOT_W}\\bin')")
    if f"grafana {GRAFANA_VER}" not in have or not os.path.exists(os.path.join(ROOT, "bin", "grafana", "bin", "grafana.exe")):
        print("  extract Grafana (Windows-side, ~1 min)")
        pywin("import zipfile,shutil,os\n"
              f"d=r'{ROOT_W}\\bin'\n"
              "t=os.path.join(d,'grafana')\n"
              "shutil.rmtree(t,ignore_errors=True)\n"
              f"zipfile.ZipFile(r'{ROOT_W}\\dl\\{GRAFANA_ZIP}').extractall(d)\n"
              f"os.replace(os.path.join(d,'grafana-{GRAFANA_VER}'),t)\n")
    plug = os.path.join(ROOT, "grafana", "plugins", "frser-sqlite-datasource")
    if not os.path.isdir(plug):
        print("  extract SQLite datasource plugin")
        pywin(f"import zipfile;zipfile.ZipFile(r'{ROOT_W}\\dl\\sqlite-plugin.zip').extractall(r'{ROOT_W}\\grafana\\plugins')")
    with open(marker, "w") as f:
        f.write(f"victoriametrics {VM_VER}\ngrafana {GRAFANA_VER}\n")
    # Grafana config (admin password generated once, kept in state, never in git)
    pwf = os.path.join(ROOT, "state", "grafana_admin.txt")
    if not os.path.exists(pwf):
        with open(pwf, "w") as f:
            f.write(secrets.token_urlsafe(18))
    tpl = open(os.path.join(HERE, "grafana", "custom.ini.template")).read()
    ini = tpl.format(root=ROOT_W.replace("\\", "/"), mirror=MIRROR_W.replace("\\", "/"),
                     admin_password=open(pwf).read().strip())
    with open(os.path.join(ROOT, "grafana", "custom.ini"), "w", newline="\r\n") as f:
        f.write(ini)
    # Windows scheduled task: supervise.py every minute, from the mirror (a push is the deploy)
    pyw = pywin("import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))").strip()
    r = sh(["schtasks.exe", "/Create", "/F", "/TN", TASK, "/SC", "MINUTE", "/MO", "1",
            "/TR", f'"{pyw}" "{MIRROR_CODE_W}\\supervise.py"'])
    print(f"  scheduled task {TASK}: {'ok' if r.returncode == 0 else 'FAILED ' + r.stderr.strip()}")
    # WSL units + CLI
    ud = os.path.expanduser("~/.config/systemd/user")
    for u in UNITS:
        shutil.copy(os.path.join(HERE, "systemd", u), os.path.join(ud, u))
    sh(["systemctl", "--user", "daemon-reload"])
    r = sh(["systemctl", "--user", "enable", "--now", "rm-telemetry-export.timer", "rm-telemetry-health.timer"])
    print(f"  systemd timers: {'ok' if r.returncode == 0 else 'FAILED ' + r.stderr.strip()}")
    binp = os.path.expanduser("~/.local/bin/telemetry")
    if os.path.islink(binp) or os.path.exists(binp):
        os.remove(binp)
    os.symlink(os.path.join(HERE, "telemetry"), binp)
    print("  ~/.local/bin/telemetry linked")
    r = sh(["schtasks.exe", "/Run", "/TN", TASK])
    print(f"  kicked supervisor: {'ok' if r.returncode == 0 else r.stderr.strip()}")
    print("done. Grafana: http://localhost:3000   check: telemetry health")
    return 0


if __name__ == "__main__":
    sys.exit(main())
