#!/usr/bin/env python3
"""Run one ./publish in ~/rm/bench and measure its check-tree checkout: /proc/pressure/io each second, the samples
during which a git process works in an rm-treecheck tree, and publish's own 'tree checks:' line (seconds, MB written).
usage: kept_measure.py <out.txt> <commit message> <path>..."""
import json, os, subprocess, sys, threading, time
out, msg, paths = sys.argv[1], sys.argv[2], sys.argv[3:]
os.chdir(os.path.expanduser("~/rm/bench"))
samples, stop = [], threading.Event()

def pressure():
    d = {}
    for ln in open("/proc/pressure/io"):
        k, *kv = ln.split()
        d[k] = {a: float(b) for a, b in (x.split("=") for x in kv)}
    return d

def git_in_tree():
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            c = open("/proc/%s/cmdline" % p, "rb").read().split(b"\0")
        except OSError:
            continue
        if c and c[0].endswith(b"git") and any(b"rm-treecheck" in x for x in c):
            return True
    return False

def sample():
    while not stop.is_set():
        samples.append((time.time(), git_in_tree(), pressure()))
        stop.wait(1.0)

t = threading.Thread(target=sample, daemon=True); t.start()
t0 = time.time()
import re
pp = subprocess.Popen(["./publish", "-m", msg, *paths], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
lines, win = [], []
for ln in pp.stdout:
    lines.append(ln.rstrip("\n"))
    m = re.search(r"tree checks: .*running them on a full checkout.*\((\d+\.\d) s, wrote", ln)
    if m:
        now = time.time(); win.append((now - float(m.group(1)), now))
rc = pp.wait()
stop.set(); t.join()
class R: pass
r = R(); r.returncode = rc
act = [s for s in samples if win and win[0][0] - 0.5 <= s[0] <= win[0][1] + 0.5]
rep = ["publish rc=%d wall=%.1f s" % (r.returncode, time.time() - t0)]
rep += [ln for ln in lines if "tree checks:" in ln or "PUBLISHED" in ln or "REFUSED" in ln]
if act:
    a, b = act[0], act[-1]
    span = max(b[0] - a[0], 1e-9)
    rep.append("checkout window (from publish's own seconds, first checkout): %d samples over %.1f s" % (len(act), span))
    for k in ("some", "full"):
        rep.append("  %s: avg10 max %.2f; stalled %.0f%% of the window (total delta)" % (
            k, max(s[2][k]["avg10"] for s in act), 100 * (b[2][k]["total"] - a[2][k]["total"]) / 1e6 / span if span > 0.5 else float("nan")))
else:
    rep.append("checkout window: no sample saw a git process in a check tree (shorter than the 1 s sampling)")
rep.append("pressure at start: %s" % json.dumps(samples[0][2]) if samples else "no samples")
open(out, "w").write("\n".join(rep + ["", "--- publish output ---"] + lines) + "\n")
print("\n".join(rep))
