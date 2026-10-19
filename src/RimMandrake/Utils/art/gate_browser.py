#!/usr/bin/env python3
"""gate_browser.py — render a biome art sheet in headless Edge, the way the owner sees it (req 13 of scaled_review_gate).

A sheet opened from file:// shows NO rows at all (it wants its sidecar), so only a SERVED page measures anything. This starts a
throwaway sidecar on a COPY of the decisions file (his are never touched), dumps the rendered DOM and the console, and stops it.
Returns (rendered <img> count or None, uncaught console errors, problem text or "").
"""
from __future__ import annotations

import os
import re
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


EDGE_TIMEOUT_S = int(os.environ.get("GATE_EDGE_TIMEOUT_S") or 90)   # hard cap on the Edge stage (was 600 s with a retry: 20 min)
URL_WAIT_S = 20


def edge_cmd(url: str, profile: str) -> list[str]:
    """The headless-Edge DOM dump. A module-level function so the selftest can swap in a stdlib fetcher."""
    return [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000", "--disable-extensions",
            "--enable-logging=stderr", "--log-level=0", "--user-data-dir=" + profile, "--no-first-run", "--dump-dom", url]


def browser_render(html_path, decisions_path=None, timeout: int | None = None):
    timeout = int(timeout or EDGE_TIMEOUT_S)
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
    # THE SIDECAR'S OUTPUT GOES TO A FILE, NEVER A PIPE (2026-10-19). It logs one line per HTTP request, and every image
    # on the scratch copy 404s; with stdout=PIPE read only until the URL, ~64 KB of log lines filled the pipe, the
    # sidecar blocked mid-request and Edge waited on it until the 600 s timeout (a 178-row sheet never gated). A file
    # cannot fill; it is deleted with the scratch dir. selftest_gate_browser.py serves thousands of 404s to prove it.
    log = work / "sidecar.log"
    try:
        if decisions_path and Path(decisions_path).is_file():
            shutil.copy(decisions_path, scratch)
        with open(log, "wb") as fh:
            proc = subprocess.Popen([sys.executable, "-u", str(SIDECAR), "--no-open", "--sheet", str(work / f"{sid}.html"),
                                     "--decisions", str(scratch)],
                                    cwd=str(work), stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        url, t0, buf = None, time.time(), ""
        while time.time() - t0 < URL_WAIT_S and not url:
            time.sleep(0.2)
            try:
                buf = log.read_text(errors="replace")
            except OSError:
                buf = ""
            m = URL_RE.search(buf)
            url = m.group(0) if m else None
            if proc.poll() is not None and not url:
                break
        if not url:
            return None, [], "UNMEASURED: throwaway sidecar printed no URL: " + buf[-160:].replace("\n", " ")
        _wait_answers(url, 5.0)                              # the URL is printed before the socket reliably answers
        # ...from WSL. Windows reaches it through the WSL localhost relay, which can lag: Edge then exits in under a
        # second with "Page load failed: net::ERR_CONNECTION_REFUSED" and an empty DOM, read as "renders blank"
        # (MEASURED 2026-10-19: 3 builds of a 190-row sheet refused that way; the same page rendered 1936 <img> in
        # 12.6 s one attempt later). Such a refusal is retried here, never counted as a render.
        for attempt in range(4):
            r = subprocess.run(edge_cmd(url, profile), capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
            if "<img" in r.stdout or "ERR_CONNECTION_REFUSED" not in (r.stderr or ""):
                break
            time.sleep(1.5 * (attempt + 1))
    except (OSError, subprocess.SubprocessError) as e:
        tail = ""
        if isinstance(e, subprocess.TimeoutExpired):
            tail = f" after {timeout} s"
            if e.stderr:
                raw = e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else e.stderr
                tail += " | Edge stderr tail: " + " / ".join(l.strip()[:160] for l in raw.splitlines()[-6:])
        return None, [], f"UNMEASURED: headless Edge failed to run ({type(e).__name__}){tail}"
    finally:
        if Path(EDGE).is_file() and edge_cmd.__module__ == __name__:
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


def _wait_answers(url: str, limit: float) -> None:
    import urllib.request
    t0 = time.time()
    while time.time() - t0 < limit:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return
        except Exception:                               # noqa: BLE001
            time.sleep(0.2)
