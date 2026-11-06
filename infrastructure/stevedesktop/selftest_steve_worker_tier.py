#!/usr/bin/env python3
"""selftest_steve_worker_tier.py - an exact-tier job on the SteveDesktop worker (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD).

Owner by card 2026-11-05: SteveDesktop is the exact-tier host. A testq job of profile tier:<name> with a proofs selector
loads that tier as the WHOLE list, checks the running load against it (testq/tier_load.py) and runs the item's
live-proof lines. On selftest_steve_worker.py's harness (mock phases, no game, no ssh) what must hold:
  a running game that already is the tier is kept: no down, no swap (the train stays on the tier); each clause's line
  runs, exit 0 PASS, exit 1 FAIL, another exit UNMEASURED, a clause with no line UNMEASURED; the reading and the
  running packageIds are in the result, and the contract (TestqResult) accepts it;
  a load that is not the tier: down, modset_builder --tier <name> --apply (the swap), load, check again;
  still not the tier after the swap: INVALID/LOAD, every row UNMEASURED with the reason, and no proof runs;
  a refused swap: INVALID/LOAD, nothing runs; the deploy phase deploys the job's deploy list, never the item id;
  tier_load.compare: case-blind, aliases, extra and missing both counted.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_steve_worker as B  # noqa: E402  (its import builds the git snapshot a bare export needs)

S = B.S
FAILS = []
CHECK = r'''
import json, os, sys
st = open(os.environ["TIER_STATE"]).read().strip()
r = {"tier": sys.argv[-1], "want": ["a", "b"], "running": ["a", "b"] if st == "exact" else ["a", "b", "c"],
     "extra": [] if st == "exact" else ["c"], "missing": [], "exact": st == "exact",
     "why": None if st == "exact" else "WRONG_TIER: the running load is not tier %s (extra ['c'])" % sys.argv[-1]}
print(json.dumps(r)); sys.exit(0 if st == "exact" else 1)
'''
SWAP = r'''
import os, sys
open(os.environ["TIER_LOG"], "a").write("swap %s\n" % sys.argv[-1])
if os.environ.get("SWAP_FAIL"):
    print("REFUSING TO WRITE ModsConfig.xml: game running"); sys.exit(1)
open(os.environ["TIER_STATE"], "w").write(os.environ.get("AFTER_SWAP", "exact"))
'''
PROOFS = ("live-tier: ratchet_pilot\n"
          "live-proof A1: echo ran-A1 >> \"$TIER_LOG\"; echo PASS: A1\n"
          "live-proof A2: echo ran-A2 >> \"$TIER_LOG\"; echo 'A2 FAIL MOD: 39 mods'; exit 1\n"
          "live-proof A3: echo ran-A3 >> \"$TIER_LOG\"; exit 3\n")


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def t_compare():
    sys.path.insert(0, os.path.join(B.RUNNER, "src", "RimMandrake", "Utils", "testq"))
    import tier_load as TL
    check(TL.compare(["Ludeon.RimWorld", "a.b"], ["ludeon.rimworld", "a.b"]) == ([], []), "case-blind exact")
    check(TL.compare(["a.b", "x.y"], ["a.b", "z.z"]) == (["z.z"], ["x.y"]), "extra and missing both counted")
    check(TL.compare(["old.id"], ["new.id"], alias={"old.id": "new.id"}) == ([], []), "an alias is no gap")
    r = TL.reading("t", ["a"], ["a", "b"])
    check(not r["exact"] and r["why"].startswith("WRONG_TIER"), "a reading off the tier says WRONG_TIER: %s" % r["why"])
    check(TL.reading("t", ["a"], None, "jawa/running_mods raised")["exact"] is False, "an unread load is never exact")


def main():
    t_compare()
    tmp = tempfile.mkdtemp(prefix="rf_steveworker_tier_")
    try:
        home, mods, proofs = (os.path.join(tmp, d) for d in ("home", "mods", "proofs"))
        for d in (home, mods, proofs, os.path.join(mods, "Mock", "Defs")):
            os.makedirs(d)
        open(os.path.join(mods, "Mock", "Defs", "a.xml"), "w").write("<Defs/>")
        open(os.path.join(proofs, "VITALS_X.txt"), "w").write(PROOFS)
        check_py, swap_py = os.path.join(tmp, "check.py"), os.path.join(tmp, "swap.py")
        open(check_py, "w").write(CHECK)
        open(swap_py, "w").write(SWAP)
        state, log, deploys, downs = (os.path.join(tmp, n) for n in ("state", "log", "deploys", "downs"))
        env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT")}
        env.update(TESTQ_HOME=home, TESTQ_MODS_DIR=mods, TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1",
                   TESTQ_SHEET_DIR=os.path.join(tmp, "sheets"),
                   TESTQ_CMD_DEPLOY="echo >> %s" % deploys, TESTQ_CMD_LOAD="echo started pid 4242",
                   TESTQ_CMD_DOWN="echo down >> %s" % downs, TESTQ_CMD_PROBE="true", TESTQ_PROBE_GAP_S="0",
                   TESTQ_CMD_RUN="echo modcheck-must-not-run >> %s; false" % log,
                   TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",
                   TESTQ_CMD_DUMP="echo '{\"status\": \"refused\", \"reason\": \"selftest\"}'",
                   TESTQ_CMD_BRIDGE="true",
                   TESTQ_CMD_TIERCHECK="%s %s" % (sys.executable, check_py),
                   TESTQ_CMD_TIERSWAP="%s %s" % (sys.executable, swap_py), TESTQ_PROOFS_DIR=proofs,
                   TIER_STATE=state, TIER_LOG=log, RIMFLOW_DRIVER_LOCK=os.path.join(tmp, "DRIVER_LOCK.json"),
                   RM_HOST="stevedesktop", RM_GAME_USERDATA=tmp, RIMFLOW_LEDGER=os.path.join(tmp, "ev.jsonl"))
        head = B.subprocess.run(["git", "-C", B.RUNNER, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        env["TESTQ_COMPANION_DIR"] = os.path.join(tmp, "BridgeTools", "JawaBench")
        B.CI.write_fixture(os.path.join(env["TESTQ_COMPANION_DIR"], B.CI.DLL_NAME), B.CI.srchash_at(B.RUNNER, head))

        def run(start_state, **extra):
            for p in (log, deploys, downs):
                if os.path.exists(p):
                    os.remove(p)
            open(state, "w").write(start_state)
            job = S.make_job("VITALS_X", {"proofs": ["A1", "A2", "A3", "A4"]}, "fix", "RELENTLESS", head,
                             item="VITALS_X", profile="tier:ratchet_pilot", lane="stevedesktop", deploy=["Mock"])
            r = B.subprocess.run([sys.executable, B.WORKER, "start"], input=json.dumps(job), env=dict(env, **extra),
                                 capture_output=True, text=True, timeout=60)
            try:
                o = json.loads(r.stdout.strip().splitlines()[-1])
            except (ValueError, IndexError):
                o = {"raw": (r.stdout + r.stderr)[-300:]}
            res = wait(o.get("attempt", "x"))
            text = lambda p: open(p).read() if os.path.exists(p) else ""
            return res, text(log), text(deploys), text(downs)

        def wait(aid, limit=60):
            import time
            t = time.time()
            path = os.path.join(home, "attempts", aid, "result.json")
            while time.time() - t < limit:
                if os.path.exists(path):
                    return json.load(open(path))
                time.sleep(0.3)
            return {"note": "no result for %s" % aid}

        # 1. the game already runs the tier: kept, proofs judged
        res, lg, dp, dn = run("exact")
        v = {r["row"]: r["verdict"] for r in res.get("rows", [])}
        check(res.get("outcome") == "DONE" and v == {"A1": "PASS", "A2": "FAIL", "A3": "UNMEASURED", "A4": "UNMEASURED"},
              "exit 0 PASS, 1 FAIL, 3 UNMEASURED, no line UNMEASURED: %s %s" % (v, res.get("note")))
        check("swap" not in lg and not dn and "modcheck-must-not-run" not in lg,
              "a game already on the tier is kept: no down, no swap, no modcheck: %r %r" % (lg, dn))
        check(res.get("tier", {}).get("exact") is True and res.get("running") == ["a", "b"],
              "the reading and the running packageIds are recorded: %s" % res.get("running"))
        check("Mock" in dp and "VITALS_X" not in dp, "the deploy is the job's list, never the item id: %r" % dp)
        check(B.subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import worker; "
                                "import json; print(worker.contract_errors(json.load(open(%r))))"
                                % (B.HERE, os.path.join(home, "attempts", res.get("attempt", "x"), "result.json"))],
                               capture_output=True, text=True, env=env).stdout.strip() == "[]",
              "the result contract accepts it")
        # 2. another list runs: down, swap to the tier, load, check again
        res, lg, dp, dn = run("wrong")
        v = {r["row"]: r["verdict"] for r in res.get("rows", [])}
        check("swap ratchet_pilot" in lg and dn and res.get("outcome") == "DONE" and v.get("A1") == "PASS",
              "off the tier: down, a whole-list swap to ratchet_pilot, then judged: %r %s" % (lg, res.get("note")))
        # 3. still not the tier after the swap: nothing judged, nothing run
        res, lg, dp, dn = run("wrong", AFTER_SWAP="wrong")
        v = {r["row"]: r["verdict"] for r in res.get("rows", [])}
        check(res.get("outcome") == "INVALID" and res.get("cause") == "LOAD" and set(v.values()) == {"UNMEASURED"}
              and len(v) == 4, "a load that is not the tier is UNMEASURED, never a verdict: %s %s" % (v, res.get("note")))
        check("ran-" not in lg and "WRONG_TIER" in json.dumps(res.get("rows")),
              "no proof ran, and each row says why: %r" % lg)
        # 4. the swap refused
        res, lg, dp, dn = run("wrong", SWAP_FAIL="1")
        check(res.get("outcome") == "INVALID" and res.get("cause") == "LOAD" and "ran-" not in lg,
              "a refused swap is INVALID/LOAD and runs nothing: %s" % res.get("note"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest_steve_worker_tier: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
