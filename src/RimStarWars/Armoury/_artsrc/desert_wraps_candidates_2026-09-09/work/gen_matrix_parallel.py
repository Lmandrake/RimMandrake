#!/usr/bin/env python3
"""Parallel driver for gen_matrix.py's job set (DESERT_WRAPS_ART_COMMISSION_1).

Serially the 60-job matrix is ~2 hours at the measured 123 s/job. codex_image.py
supports concurrent workers explicitly via --codex-home (each worker gets its own
seeded CODEX_HOME so they cannot collide over the thread-writer lock or harvest
each other's images), so this runs N workers over the same job dict.

Quota wall: the Codex imagegen quota is what stopped the first wave
(rc=1 "resets in about 3 hours 34 minutes", 2026-09-18 ~14:18Z-local). This driver
STOPS THE WHOLE RUN on the first quota-wall signature rather than loop-retrying and
burning the reset window -- per the item's standing instruction.

Prompts, job names and skip-if-exists semantics all come from gen_matrix.py; this
file adds only scheduling. No third-party image is an input to any call.
"""
import os
import queue
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_matrix as G  # noqa: E402

WORKERS = int(os.environ.get("DW_WORKERS", "4"))
HOMES = Path("/mnt/c/Users/Mandrake/.codex_workers")
QUOTA_RE = re.compile(r"resets in about|quota|usage limit|rate limit", re.I)

quota_hit = threading.Event()
lock = threading.Lock()
results = {}


def one(name, prompt, home, attempts=2, timeout=200):
    dest = G.OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 20000:
        return "SKIP", ""
    for i in range(attempts):
        if quota_hit.is_set():
            return "ABORT", "quota wall"
        t0 = time.time()
        p = subprocess.run(
            [sys.executable, str(G.CODEX), "generate", "--out", str(dest),
             "--prompt", prompt, "--timeout", str(timeout),
             "--codex-home", str(home), "--force"],
            capture_output=True, text=True)
        el = time.time() - t0
        if dest.exists() and dest.stat().st_size > 20000:
            return "OK", f"{el:.0f}s {dest.stat().st_size // 1024}KB"
        blob = (p.stderr or "") + (p.stdout or "")
        if QUOTA_RE.search(blob):
            quota_hit.set()
            return "QUOTA", blob[-300:].strip()
        if i == attempts - 1:
            return "FAIL", f"rc={p.returncode} {blob[-200:].strip()}"
    return "FAIL", "exhausted"


def worker(wid, q):
    home = HOMES / f"dw{wid}"
    while not quota_hit.is_set():
        try:
            name = q.get_nowait()
        except queue.Empty:
            return
        status, detail = one(name, G.ALL_JOBS[name], home)
        with lock:
            results[name] = status
            print(f"[w{wid}] {status:5s} {name}  {detail}", flush=True)


def main():
    want = sys.argv[1:] or list(G.ALL_JOBS)
    todo = [n for n in want
            if not ((G.OUT / f"{n}.png").exists()
                    and (G.OUT / f"{n}.png").stat().st_size > 20000)]
    print(f"JOBS total={len(want)} todo={len(todo)} workers={WORKERS}", flush=True)
    q = queue.Queue()
    for n in todo:
        q.put(n)
    ts = [threading.Thread(target=worker, args=(i + 1, q), daemon=True)
          for i in range(WORKERS)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    ok = sum(1 for v in results.values() if v == "OK")
    print(f"\nDONE ok={ok} of todo={len(todo)}  quota_wall={quota_hit.is_set()}")
    left = [n for n in todo if results.get(n) != "OK"]
    print("REMAINING:", " ".join(left) if left else "none")


if __name__ == "__main__":
    main()
