#!/usr/bin/env python3
"""gate_browser.py — render a biome art sheet in headless Edge, the way the owner sees it (req 13 of scaled_review_gate).

A sheet opened from file:// shows NO rows at all (it wants its sidecar), so only a SERVED page measures anything. This starts a
throwaway sidecar on a COPY of the decisions file (his are never touched), dumps the rendered DOM and the console, and stops it.
Returns (rendered <img> count or None, uncaught console errors, problem text or "").
"""
from __future__ import annotations

import os
import re
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path

EDGE = "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
SIDECAR = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "serve_sheet.py"
URL_RE = re.compile(r"http://localhost:\d+/\?t=[A-Za-z0-9_-]+")
# Edge runs on WINDOWS through interop: a timeout kills only the WSL-side handle and the Windows msedge tree lives on.
# MEASURED 2026-10-06 00:50: 915 msedge.exe (110 headless roots) had piled up and every new render timed out. Each run
# therefore gets its own --user-data-dir, and everything carrying that marker is stopped afterwards, timeout or not.
SCRATCH_WIN, SCRATCH_WSL = r"D:\Luke\dev\_rmscratch\edge_gate", "/mnt/d/Luke/dev/_rmscratch/edge_gate"
KILL_PS1 = r"""param([string]$Marker)
$p = Get-CimInstance -ClassName Win32_Process | Where-Object { $_.Name -eq 'msedge.exe' -and $_.CommandLine -like "*$Marker*" }
$p | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
"stopped=$($p.Count)"
"""


def stop_marked(marker: str) -> str:
    """Stop every Windows msedge.exe whose command line carries `marker` (this run's profile dir). Never another Edge."""
    try:
        os.makedirs(SCRATCH_WSL, exist_ok=True)
        ps1 = os.path.join(SCRATCH_WSL, "stop_marked_edge.ps1")
        if not os.path.isfile(ps1) or open(ps1).read() != KILL_PS1:
            open(ps1, "w").write(KILL_PS1)
        r = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                            SCRATCH_WIN + "\\stop_marked_edge.ps1", "-Marker", marker],
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return r.stdout.strip()
    except (OSError, subprocess.SubprocessError) as e:
        return f"stop failed: {type(e).__name__}"


def browser_render(html_path, decisions_path=None, timeout: int = 600):
    if not Path(EDGE).is_file():
        return None, [], f"UNMEASURED: Edge not found at {EDGE}"
    html_path = Path(html_path).resolve()
    # the page insists on its own sheetId, so it is served under its REAL name from a scratch dir beside the sheet
    # (images 404 there, which is fine: the check counts rendered <img> elements), with a COPY of the decisions: nothing of the real sheet or his decisions is touched
    sid = html_path.name.replace(".gate.tmp.html", "").removesuffix(".html")
    work = html_path.parent / f".gatecheck_{sid}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    shutil.copy(html_path, work / f"{sid}.html")
    scratch = work / f"{sid}.decisions.json"
    proc = None
    marker = "gate_%d_%d" % (os.getpid(), int(time.time() * 1000))
    profile = SCRATCH_WIN + "\\" + marker
    try:
        if decisions_path and Path(decisions_path).is_file():
            shutil.copy(decisions_path, scratch)
        proc = subprocess.Popen([sys.executable, "-u", str(SIDECAR), "--no-open", "--sheet", str(work / f"{sid}.html"), "--decisions", str(scratch)],
                                cwd=str(work), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0,
                                stdin=subprocess.DEVNULL)
        url, t0, buf = None, time.time(), ""
        while time.time() - t0 < 20 and not url:
            if select.select([proc.stdout], [], [], 0.5)[0]:
                buf += os.read(proc.stdout.fileno(), 4096).decode("utf-8", "replace")
                m = URL_RE.search(buf)
                url = m.group(0) if m else None
            if proc.poll() is not None and not url:
                break
        if not url:
            return None, [], "UNMEASURED: throwaway sidecar printed no URL: " + buf[-160:].replace("\n", " ")
        time.sleep(3)                                         # the URL is printed before the socket reliably answers
        r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000", "--disable-extensions", "--enable-logging=stderr",
                            "--log-level=0", "--user-data-dir=" + profile, "--no-first-run", "--dump-dom", url],
                           capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        tail = ""
        if isinstance(e, subprocess.TimeoutExpired) and e.stderr:
            raw = e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else e.stderr
            tail = " | Edge stderr tail: " + " / ".join(l.strip()[:160] for l in raw.splitlines()[-6:])
        return None, [], f"UNMEASURED: headless Edge failed to run ({type(e).__name__}){tail}"
    finally:
        stop_marked(marker)
        shutil.rmtree(os.path.join(SCRATCH_WSL, marker), ignore_errors=True)
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.SubprocessError:
                proc.kill()
        shutil.rmtree(work, ignore_errors=True)
    errs = [l.strip()[:220] for l in r.stderr.splitlines() if "Uncaught" in l]
    return r.stdout.count("<img"), errs, ""
