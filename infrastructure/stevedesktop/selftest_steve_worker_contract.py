#!/usr/bin/env python3
"""selftest_steve_worker_contract.py - worker.py publishes only what contracts.models.TestqResult accepts
(TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT).

  K1  a DONE result carrying chain_versions (set on every real DONE) is published unchanged
  K2  a result the contract refuses (a row detail past 4000 chars) is published as INVALID/HARNESS naming the error,
      the original kept as result.refused.json, the outbox copy the stand-in; never an exception
  K3  `start` with a contract that cannot load (pydantic broken in TESTQ_PYDEPS) refuses before any attempt exists,
      exit 1, the error naming the install line; testq.py keeps such a job pending
  K4  spawn's outer copy is the models.py bytes loaded before the pin, not whatever the pinned clone holds
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, "worker.py")
FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_steveworker_contract_")
    try:
        home = os.path.join(tmp, "home")
        os.environ["TESTQ_HOME"] = home
        os.environ.pop("TESTQ_REPO", None)
        sys.path.insert(0, HERE)
        import worker as W
        S = W.S
        W.ensure_dirs()
        job_id = "J20261103T120000Z-abc123"

        def attempt(n):
            aid = "%s.a%d" % (job_id, n)
            d = os.path.join(home, "attempts", aid)
            os.makedirs(d)
            return aid, d

        # K1
        aid, d = attempt(1)
        res = W.base_result(job_id, aid, "0123456789abcdef0123456789abcdef01234567")
        res.update(outcome="DONE", rows=[{"chain": "c1", "row": "r1", "verdict": "PASS", "detail": "ok"}],
                   chain_versions={"c1": "v3"})
        W.publish_result(d, res)
        got = json.load(open(os.path.join(d, "result.json")))
        check(got["outcome"] == "DONE" and got["chain_versions"] == {"c1": "v3"} and got["counts"] == {"PASS": 1}
              and not os.path.exists(os.path.join(d, "result.refused.json")),
              "K1 a DONE result with chain_versions publishes unchanged: %s" % str(got)[:200])

        # K2
        aid, d = attempt(2)
        res = W.base_result(job_id, aid, None)
        res.update(outcome="DONE", rows=[{"chain": "c1", "row": "r1", "verdict": "PASS", "detail": "x" * 4001}])
        check(W.contract_errors(res) != [], "K2 precondition: TestqResult refuses a 4001-char row detail")
        try:
            W.publish_result(d, res)
            raised = None
        except Exception as e:  # noqa: BLE001
            raised = e
        got = json.load(open(os.path.join(d, "result.json"))) if os.path.exists(os.path.join(d, "result.json")) else {}
        box = os.path.join(home, "outbox", aid + ".json")
        kept = os.path.join(d, "result.refused.json")
        check(raised is None and got.get("outcome") == "INVALID" and got.get("cause") == "HARNESS"
              and "TestqResult" in got.get("note", "") and got.get("rows") == [],
              "K2 a refused result is published as INVALID/HARNESS naming the contract: %s %s" % (raised, str(got)[:300]))
        check(os.path.exists(kept) and json.load(open(kept))["rows"][0]["detail"] == "x" * 4001
              and os.path.exists(box) and json.load(open(box))["outcome"] == "INVALID",
              "K2 the original is kept as result.refused.json and the outbox carries the stand-in")

        # K4 (in-process: the module already loaded models.py; a later change on disk must not reach the copy)
        loaded = W._MODELS[1]
        fake_src = os.path.join(tmp, "models_pinned.py")
        open(fake_src, "w").write("raise ImportError('the pinned clone')\n")
        W.MODELS_SRC = fake_src
        outer = os.path.join(home, "outer")
        os.makedirs(outer, exist_ok=True)
        W.contract_models()
        with open(os.path.join(outer, W.OUTER_MODELS), "wb") as f:     # the two lines spawn runs
            f.write(W._MODELS[1])
        check(open(os.path.join(outer, W.OUTER_MODELS), "rb").read() == loaded and b"class TestqResult" in loaded,
              "K4 the outer contracts_models.py is the bytes loaded before the pin")
        spawn_src = open(WORKER).read().split("def spawn(", 1)[1].split("\ndef ", 1)[0]
        check("f.write(_MODELS[1])" in spawn_src and "contract_models()" in spawn_src,
              "K4 spawn writes the captured bytes (not a copy from the clone)")

        # K3
        pydeps = os.path.join(tmp, "pydeps")
        os.makedirs(os.path.join(pydeps, "pydantic"))
        open(os.path.join(pydeps, "pydantic", "__init__.py"), "w").write("raise ImportError('broken on purpose')\n")
        env = dict(os.environ, TESTQ_PYDEPS=pydeps, TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1")
        job = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", "0" * 40)
        r = subprocess.run([sys.executable, WORKER, "start"], input=json.dumps(job), env=env,
                           capture_output=True, text=True, timeout=60)
        try:
            o = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            o = {"raw": r.stdout + r.stderr}
        check(r.returncode == 1 and o.get("state") == "contract_missing" and "pip install --target" in o.get("error", "")
              and "attempt" not in o and not os.path.exists(os.path.join(home, "jobs", job["id"])),
              "K3 start refuses when the contract cannot load, before any attempt: rc %s %s" % (r.returncode, str(o)[:300]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
