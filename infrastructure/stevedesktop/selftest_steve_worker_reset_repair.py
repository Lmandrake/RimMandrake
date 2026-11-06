#!/usr/bin/env python3
"""selftest_steve_worker_reset_repair.py - the worker repairs a crash-reset ModsConfig itself
(STEVE_MODSCONFIG_REPAIR_CRASH_RESETS_LIST).

The incident, end to end on selftest_steve_worker.py's harness (no game, no ssh): a tier job's load crashes and RimWorld
leaves Core+DLC in ModsConfig. The swap and the repair are the REAL modset_builder on temp files.
  the failed attempt ends with the before-copy live and says so in its note;
  the next job's swap is not refused; a list reset between attempts is repaired before the next job starts;
  a load that failed WITHOUT a reset leaves the tier list alone; a DONE attempt runs no end repair;
  a repair that refuses costs the job nothing and is named in the note; the archmagi lane never repairs (the owner's list).
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_steve_worker as B  # noqa: E402  (its import builds the git snapshot a bare export needs)

S = B.S
FAILS = []
RESET_LIST = ("﻿<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>ludeon.rimworld.royalty</li>"
              "<li>ludeon.rimworld.odyssey</li></activeMods></ModsConfigData>")
OWNER = "<ModsConfigData><activeMods><li>brrainz.harmony</li><li>ludeon.rimworld</li><li>a.b</li></activeMods></ModsConfigData>"
TIER = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>tier.mod</li></activeMods></ModsConfigData>"

# the real modset_builder pointed at temp files. repair: --repair-reset; swap: what --tier X --apply does to the list
MB = r'''
import os, sys
sys.path.insert(0, os.path.join(os.environ["MB_RUNNER"], "src", "RimMandrake", "Utils"))
import modset_builder as mb
cfg, bk = os.environ["MB_CONFIG"], os.environ["MB_BACKUPS"]
open(os.environ["MB_LOG"], "a").write(sys.argv[1] + "\n")
if sys.argv[1] == "repair":
    mb.CONFIG, mb.BACKUPS = cfg, bk
    sys.argv = ["modset_builder.py", "--repair-reset", "--not-my-bridge", "selftest"]
    sys.exit(mb.main())
try:
    mb.take_before_copy(cfg, bk, "t")
except mb.RestoreRefused as e:
    print("REFUSING TO WRITE: %s" % e)
    sys.exit(1)
open(cfg, "w", encoding="utf-8").write(os.environ["MB_TIER"])
mb.record_tier_written(cfg, bk)
'''
CHECK = r'''
import json, os, sys
exact = os.path.exists(os.environ["MB_LOADED_OK"])
print(json.dumps({"tier": sys.argv[-1], "want": ["a"], "running": ["a"], "extra": [], "missing": [], "exact": exact,
                  "why": None if exact else "WRONG_TIER: the running load is not it"}))
sys.exit(0 if exact else 1)
'''
# the load: with MB_CRASH set the game crashes and resets the list, as RimWorld does; a failing one exits 1
LOAD = r'''
import os, sys
if os.environ.get("MB_CRASH") == "reset":
    open(os.environ["MB_CONFIG"], "w", encoding="utf-8").write(os.environ["MB_RESET"])
if os.environ.get("MB_CRASH"):
    print("game load failed"); sys.exit(1)
open(os.environ["MB_LOADED_OK"], "w").close()
print("started pid 4242")
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_steveworker_reset_")
    try:
        home, mods, proofs, bk = (os.path.join(tmp, d) for d in ("home", "mods", "proofs", "bk"))
        for d in (home, mods, proofs, bk, os.path.join(mods, "Mock", "Defs")):
            os.makedirs(d)
        open(os.path.join(mods, "Mock", "Defs", "a.xml"), "w").write("<Defs/>")
        open(os.path.join(proofs, "VITALS_X.txt"), "w").write("live-tier: t\nlive-proof A1: echo PASS: A1\n")
        paths = {}
        for name, body in (("mb", MB), ("check", CHECK), ("load", LOAD)):
            paths[name] = os.path.join(tmp, name + ".py")
            open(paths[name], "w").write(body)
        cfg, log, ok_flag = (os.path.join(tmp, n) for n in ("ModsConfig.xml", "mb.log", "loaded_ok"))
        py = sys.executable
        env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT")}
        env.update(TESTQ_HOME=home, TESTQ_MODS_DIR=mods, TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1",
                   TESTQ_SHEET_DIR=os.path.join(tmp, "sheets"),
                   TESTQ_CMD_DEPLOY="true", TESTQ_CMD_LOAD="%s %s" % (py, paths["load"]),
                   TESTQ_CMD_DOWN="true", TESTQ_CMD_PROBE="true", TESTQ_PROBE_GAP_S="0", TESTQ_CMD_RUN="false",
                   TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",
                   TESTQ_CMD_DUMP="echo '{\"status\": \"refused\", \"reason\": \"selftest\"}'", TESTQ_CMD_BRIDGE="true",
                   TESTQ_CMD_TIERCHECK="%s %s" % (py, paths["check"]),
                   TESTQ_CMD_TIERSWAP="%s %s swap" % (py, paths["mb"]),
                   TESTQ_CMD_RESETREPAIR="%s %s repair" % (py, paths["mb"]),
                   TESTQ_PROOFS_DIR=proofs, RIMFLOW_DRIVER_LOCK=os.path.join(tmp, "DRIVER_LOCK.json"),
                   RM_HOST="stevedesktop", RM_GAME_USERDATA=tmp, RIMFLOW_LEDGER=os.path.join(tmp, "ev.jsonl"),
                   RM_MODSET_LOCK=os.path.join(tmp, "lock"), MB_RUNNER=B.RUNNER, MB_CONFIG=cfg, MB_BACKUPS=bk, MB_LOG=log,
                   MB_TIER=TIER, MB_RESET=RESET_LIST, MB_LOADED_OK=ok_flag)
        env.pop("TESTQ_WORKER_HOST", None)
        head = B.subprocess.run(["git", "-C", B.RUNNER, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        env["TESTQ_COMPANION_DIR"] = os.path.join(tmp, "BridgeTools", "JawaBench")
        B.CI.write_fixture(os.path.join(env["TESTQ_COMPANION_DIR"], B.CI.DLL_NAME), B.CI.srchash_at(B.RUNNER, head))
        marker = os.path.join(bk, "ModsConfig.swap-active.json")

        def live():
            return open(cfg, encoding="utf-8").read()

        def run(**extra):
            for path in (log, ok_flag):
                if os.path.exists(path):
                    os.remove(path)
            job = S.make_job("VITALS_X", {"proofs": ["A1"]}, "fix", "RELENTLESS", head,
                             item="VITALS_X", profile="tier:ratchet_pilot", lane="stevedesktop", deploy=["Mock"])
            r = B.subprocess.run([py, B.WORKER, "start"], input=json.dumps(job), env=dict(env, **extra),
                                 capture_output=True, text=True, timeout=120)
            try:
                aid = json.loads(r.stdout.strip().splitlines()[-1]).get("attempt", "x")
            except (ValueError, IndexError):
                return {"note": "no start: " + (r.stdout + r.stderr)[-300:]}, ""
            path, t = os.path.join(home, "attempts", aid, "result.json"), time.time()
            while time.time() - t < 90 and not os.path.exists(path):
                time.sleep(0.3)
            res = json.load(open(path)) if os.path.exists(path) else {"note": "no result for " + aid}
            return res, open(log).read() if os.path.exists(log) else ""

        def fresh():
            shutil.rmtree(bk)
            os.makedirs(bk)
            open(cfg, "w", encoding="utf-8").write(OWNER)

        # 1. the incident: the swap writes the tier, the load crashes and resets the list
        fresh()
        res, lg = run(MB_CRASH="reset")
        check(res.get("outcome") == "INVALID" and res.get("cause") == "LOAD", "the crashed load is INVALID/LOAD: %s" % res.get("note"))
        check(live() == OWNER, "the failed attempt ends with the before-copy live, no hand restore")
        check(not os.path.exists(marker), "and the swap is over")
        check("REPAIRED" in (res.get("note") or ""), "and its note says so: %s" % res.get("note"))
        # 2. the next job is not refused (the refusal was the lane's outage)
        res, lg = run()
        check(res.get("outcome") == "DONE" and live() == TIER, "the next job swaps and runs: %s" % res.get("note"))
        check("REPAIRED" not in (res.get("note") or ""), "with nothing to repair: %s" % res.get("note"))
        check(lg.count("repair") == 1, "a DONE attempt runs no end repair, only the one at start: %r" % lg)
        # 3. a reset the last attempt never saw (it died): repaired before the next job's swap
        open(cfg, "w", encoding="utf-8").write(RESET_LIST)
        res, lg = run()
        check(res.get("outcome") == "DONE" and lg.split()[:2] == ["repair", "swap"], "repaired at start, then swapped: %r %s" % (lg, res.get("note")))
        check("REPAIRED" in (res.get("note") or ""), "that repair is in the note of a DONE job too: %s" % res.get("note"))
        check(live() == TIER and open(os.path.join(bk, json.load(open(marker))["before"]), encoding="utf-8").read() == OWNER,
              "and the fresh before-copy is the owner's list, not Core+DLC")
        # 4. a load that failed with no reset: the tier list stays
        res, lg = run(MB_CRASH="plain")
        check(res.get("outcome") == "INVALID" and live() == TIER and os.path.exists(marker), "no reset, no write: %s" % res.get("note"))
        check("REPAIRED" not in (res.get("note") or ""), "and no claim of one: %s" % res.get("note"))
        # 5. a repair that refuses costs nothing but says why
        before = os.path.join(bk, json.load(open(marker))["before"])
        os.remove(before)
        open(cfg, "w", encoding="utf-8").write(RESET_LIST)
        res, lg = run(MB_CRASH="plain")
        check(res.get("outcome") == "INVALID" and live() == RESET_LIST, "before-copy gone: live untouched: %s" % res.get("note"))
        check("REFUSING --repair-reset" in (res.get("note") or ""), "and the note names the refusal: %s" % res.get("note"))
        # 6. the archmagi lane's list is the owner's
        fresh()
        res, lg = run(MB_CRASH="reset", TESTQ_WORKER_HOST="archmagi")
        check("repair" not in lg and live() == RESET_LIST, "archmagi never repairs: %r" % lg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest_steve_worker_reset_repair: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
