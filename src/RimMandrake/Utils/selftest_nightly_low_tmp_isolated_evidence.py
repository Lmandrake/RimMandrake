#!/usr/bin/env python3
"""NIGHTLY_COP_FIX_RED_CYGHVG_QCWJ: the isolated-evidence selftests must not depend on free space under /tmp.

Two floors bite a night with 1.8 GB free: isolated_evidence's 12 GB (`--run` exits 2, the test dies on the journal it
never wrote) and run_selftests' 2 GB in the INNER runner the fixture really spawns (it refuses, nothing is recorded).
The second lives in a child process, so a reading forced only inside the test cannot see it. So the low reading here
covers the whole process tree (a sitecustomize on PYTHONPATH), and a real 1800 MB tmpfs on /tmp is tried as well.

Sanity probes first: the forced reading must trip both real floors in a child, or this proof could not see the
condition. A sweep that STARTS under 2 GB refuses by design; the harness case passes the outer guard with
RM_SELFTEST_NESTED, the same state as a sweep that started above the floor and then fell under it.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
RIMFLOW = os.path.join(SRC, "rimflow")
RUNNER = os.path.join(HERE, "run_selftests.py")
TESTS = [os.path.join(RIMFLOW, t) for t in ("selftest_isolated_evidence.py", "selftest_isolated_evidence_mut.py")]
SHIM = ("import shutil, types\n"
        "shutil.disk_usage = lambda r: types.SimpleNamespace(free=int(1.8 * 1024 ** 3))\n")
TIMEOUT = 300
bad = []


def tail(p):
    return (p.stdout + p.stderr)[-600:]


# this file itself runs inside the nightly sweep: nothing of the outer run may hide the condition
clean = {k: v for k, v in os.environ.items() if k not in ("RM_SELFTEST_NESTED", "RM_SELFTEST_SKIP_DISK_GUARD",
                                                          "RM_SELFTEST_REPO_ROOT", "RM_SELFTEST_CACHE_DIR")}
shimdir = tempfile.mkdtemp(prefix="st_lowtmp_")
with open(os.path.join(shimdir, "sitecustomize.py"), "w") as f:
    f.write(SHIM)
low = dict(clean, PYTHONPATH=os.pathsep.join(x for x in (shimdir, clean.get("PYTHONPATH")) if x))

probe = subprocess.run([sys.executable, "-c",
                        "import shutil, sys; sys.path.insert(0, %r); from rimflow import isolated_evidence as ie; "
                        "print(shutil.disk_usage('/').free < ie.MIN_FREE)" % SRC],
                       capture_output=True, text=True, timeout=120, env=low)
if probe.stdout.strip() != "True":
    bad.append("probe: the forced reading does not trip the 12 GB floor: " + tail(probe))
probe = subprocess.run([sys.executable, RUNNER, "--only", TESTS[0]], capture_output=True, text=True, timeout=120, env=low)
print("probe: a bare child runner under the forced reading rc %d" % probe.returncode)
if probe.returncode != 2 or "REFUSED" not in probe.stderr:
    bad.append("probe: the forced reading does not reach a child's 2 GB floor: " + tail(probe))

for t in TESTS:
    p = subprocess.run([sys.executable, t], capture_output=True, text=True, timeout=TIMEOUT, env=low)
    print("%s rc %d, whole tree reads 1.8 GB free" % (os.path.basename(t), p.returncode))
    if p.returncode != 0:
        bad.append("%s rc %d: %s" % (os.path.basename(t), p.returncode, tail(p)))

p = subprocess.run([sys.executable, RUNNER, "--full", "--because", "low-tmp proof must really run these",
                    "--only", *TESTS],
                   capture_output=True, text=True, timeout=2 * TIMEOUT, env=dict(low, RM_SELFTEST_NESTED="1"))
print("harness past its own guard, whole tree reads 1.8 GB free: rc %d" % p.returncode)
if p.returncode != 0:
    bad.append("harness rc %d: %s" % (p.returncode, tail(p)))

# the real thing, where the machine allows a private mount namespace; the forced cases above do not depend on it
INNER = ("mount -t tmpfs -o size=1800m tmpfs /tmp || exit 77; export TMPDIR=/tmp; "
         "%s -c \"import shutil,sys; sys.exit(0 if shutil.disk_usage('/tmp').free < 2*1024**3 else 78)\" || exit 78; " % sys.executable
         + "; ".join('%s "%s" >/dev/null 2>&1 || { echo "FAILED %s"; exit 1; }' % (sys.executable, t, os.path.basename(t)) for t in TESTS))
try:
    p = subprocess.run(["unshare", "-rm", "sh", "-c", INNER], capture_output=True, text=True, timeout=2 * TIMEOUT, env=clean)
    rc, why = p.returncode, tail(p)
except FileNotFoundError as e:
    rc, why = 77, str(e)
if rc == 0:
    print("real 1800 MB tmpfs on /tmp: both tests rc 0")
elif rc == 1 and "FAILED" in why:
    bad.append("real 1800 MB tmpfs: " + why)
else:
    print("real tmpfs NOT MEASURED here (rc %d: %s); the forced cases above stand" % (rc, why.strip()[:200]))

shutil.rmtree(shimdir, ignore_errors=True)
for b in bad:
    print("FAIL", b)
print("RESULT:", "FAIL" if bad else "PASS")
sys.exit(1 if bad else 0)
