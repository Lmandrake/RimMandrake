#!/usr/bin/env python3
"""vv_matrix_clock.py - the clock's one run of the shipped-settings fuzz matrix (RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS).

    python3 src/RimMandrake/Utils/vv_matrix_clock.py [--prove] [--dry-run]

Runs vv_shipped_matrix.py at full n (offline: a staged C# build and Windows dotnet.exe, no game), and with --prove (the
timer passes it on Sundays) vv_laws.py prove as well, so a green matrix is known to be able to go red. Writes ONE
reading, <agent storage>/rimmandrake/vv_matrix/last.json, AFTER the runs end and never before (a reading written first
could pass for an answer): {when, matrix_rc, matrix_verdict, prove_rc, prove_line, results}. matrix_verdict is the
matrix's own VERDICT line; a run that printed none reads UNMEASURED with its exit code. Exit: the matrix's exit code,
or the prove's when the matrix passed; 3 when a run exited 0 but printed no answer. Unit: src/RimMandrake/Utils/systemd/rm-vv-matrix.{service,timer}.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)


def reading_path():
    import rmpaths
    return str(rmpaths.rm_path("vv_matrix", "last.json"))


def ppid_table():
    """{pid: parent pid} from /proc (Linux); {} when /proc cannot be read."""
    t = {}
    for d in os.listdir("/proc") if os.path.isdir("/proc") else []:
        if d.isdigit():
            try:
                with open("/proc/%s/stat" % d) as f:
                    t[int(d)] = int(f.read().rsplit(")", 1)[1].split()[1])
            except (OSError, ValueError, IndexError):
                continue
    return t


def descendants(pid, table=None):
    """Every process below pid, whatever its session or group (a child that called setsid still counts)."""
    table = ppid_table() if table is None else table
    kids, out = {}, []
    for c, par in table.items():
        kids.setdefault(par, []).append(c)
    todo = list(kids.get(pid, []))
    while todo:
        c = todo.pop()
        out.append(c)
        todo += kids.get(c, [])
    return out


def run(cmd, timeout):
    """-> (rc, output). The child gets its own process group; on a timeout its whole descendant tree (collected from /proc
    first, so a descendant that left the group or session is included) and its group are killed and reaped before this
    returns, so no build or probe it started outlives the reading (rc 124). A Windows dotnet.exe started through WSL
    interop dies with its interop parent [guess ~80%]."""
    p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=timeout)
        return p.returncode, out or ""
    except subprocess.TimeoutExpired:
        for d in descendants(p.pid):
            try:
                os.kill(d, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, _ = p.communicate()
        return 124, (out or "") + "\ntimed out after %ds (process group killed)" % timeout


def last(pattern, text):
    m = re.findall(pattern, text, re.M)
    return m[-1] if m else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prove", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the commands, run nothing, write nothing")
    a = ap.parse_args(argv)
    mcmd = [sys.executable, os.path.join(HERE, "vv_shipped_matrix.py")]
    pcmd = [sys.executable, os.path.join(HERE, "vv_laws.py"), "prove"]
    if a.dry_run:
        print("would run:", " ".join(mcmd))
        if a.prove:
            print("would run:", " ".join(pcmd))
        print("would write:", reading_path())
        return 0
    t0 = time.time()
    mrc, mout = run(mcmd, 6 * 3600)
    verdict = last(r"^VERDICT: (\w+)", mout)
    rec = {"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "wall_s": None, "matrix_rc": mrc,
           "matrix_verdict": verdict or "UNMEASURED (no VERDICT line; exit %d)" % mrc,
           "matrix_why": [l.strip() for l in mout.splitlines()[-12:] if l.startswith("  ") and "red at" in l],
           "results": last(r"^results: (.+)$", mout), "prove_rc": None, "prove_line": "not run (no --prove)"}
    # an answer that is missing is not a pass: a zero exit with no VERDICT (or no proof line) is an exit of its own (3)
    rc = mrc if verdict else (mrc or 3)
    if a.prove:
        prc, pout = run(pcmd, 3 * 3600)
        line = last(r"^laws proven: .+$", pout)
        rec["prove_rc"], rec["prove_line"] = prc, line or "UNMEASURED (no line; exit %d)" % prc
        if rc == 0:
            rc = prc if line else (prc or 3)
    rec["wall_s"] = round(time.time() - t0, 1)
    p = reading_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(p + ".tmp", p)
    print("vv matrix: %s; laws: %s -> %s" % (rec["matrix_verdict"], rec["prove_line"], p))
    return rc


if __name__ == "__main__":
    sys.exit(main())
