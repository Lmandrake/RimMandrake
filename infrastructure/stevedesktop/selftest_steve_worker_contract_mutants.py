#!/usr/bin/env python3
"""selftest_steve_worker_contract_mutants.py - selftest_steve_worker_contract.py goes RED when worker.py stops
validating with contracts.models.TestqResult (TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT, blind check GAP:DIFF).

Each case copies worker.py and the contract selftest into a scratch tree (src/ symlinked to this repo), applies one
mutant to the copy, runs the copied selftest and reads its exit and FAIL lines. This repo's files are never written.

  M0  control: the unmutated copy PASSES (the harness can see a pass at all)
  M1  publish_result's TestqResult block put back to the pre-item `S.validate_result(res)` -> RED
  M2  contract_errors answering with the minimal schema.validate_result instead of TestqResult -> RED
  M3  publish_result skipping the contract altogether -> RED
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORKER = os.path.join(HERE, "worker.py")
TEST = os.path.join(HERE, "selftest_steve_worker_contract.py")
FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


SRC = open(WORKER).read()
BLOCK_START = "    errs = contract_errors(res)\n    if errs:    # never publish"
BLOCK_END = "    S.dump(res, os.path.join(d, \"result.json\"))\n"
CE_BODY = "    m = contract_models()\n    return m.errors(m.TestqResult, res)\n"


def between(src, start, end):
    i = src.index(start)
    return src[i:src.index(end, i)]


MUTANTS = {
    "M1": lambda s: s.replace(between(s, BLOCK_START, BLOCK_END), "    S.validate_result(res)\n", 1),
    "M2": lambda s: s.replace(CE_BODY, "    try:\n        S.validate_result(res)\n        return []\n"
                                       "    except S.SchemaError as e:\n        return [str(e)]\n", 1),
    "M3": lambda s: s.replace(between(s, BLOCK_START, BLOCK_END), "", 1),
}


def run(tag, src):
    tmp = tempfile.mkdtemp(prefix="rf_contract_mutant_%s_" % tag)
    try:
        d = os.path.join(tmp, "infrastructure", "stevedesktop")
        os.makedirs(d)
        os.symlink(os.path.join(REPO, "src"), os.path.join(tmp, "src"))
        open(os.path.join(d, "worker.py"), "w").write(src)
        shutil.copy(TEST, d)
        env = {k: v for k, v in os.environ.items() if not k.startswith("TESTQ_")}
        r = subprocess.run([sys.executable, os.path.join(d, "selftest_steve_worker_contract.py")], env=env,
                           capture_output=True, text=True, timeout=180)
        out = r.stdout + r.stderr
        return r.returncode, [ln for ln in out.splitlines() if ln.startswith("FAIL ")], out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    for anchor in (BLOCK_START, BLOCK_END, CE_BODY):
        check(anchor in SRC, "anchor still in worker.py (a missed anchor would make a mutant a no-op): %r" % anchor[:50])
    if FAILS:
        print("\n%d failed" % len(FAILS))
        return 1
    rc, fails, out = run("M0", SRC)
    check(rc == 0 and not fails and "PASS K1" in out and "PASS K2" in out,
          "M0 control: the unmutated copy passes: rc %s %s" % (rc, (fails or out[-300:])))
    for tag, mut in MUTANTS.items():
        src = mut(SRC)
        check(src != SRC, "%s applies (the copy differs from worker.py)" % tag)
        rc, fails, out = run(tag, src)
        check(rc != 0 and any(f.startswith(("FAIL K1", "FAIL K2")) for f in fails),
              "%s goes RED in the contract selftest: rc %s %s" % (tag, rc, fails[:3] or out[-300:]))
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
