#!/usr/bin/env python3
"""selftest_wrapup_handoff_env.py — WRAPUP_DEBRIS_FIX_BLAMES_THE_WHOLE_HOUSE: the role-unit wrap-up is handed its
environment by `systemd-run -E NAME` (role_launch.stoppost_handoff), which sets an UNSET name to '' (systemd 259,
measured 2026-11-06). RM_WRAPUP_SEAT_CLONES='' read as "no seat clones" and the shared seat clone was filed as every
role unit's debris (20 open files, 2026-11-06); RIMFLOW_SHARED_BRIDGE='' read as "no lock".

  H1  wrapup.HANDOFF_ENV is role_launch.HANDOFF_ENV (the scrub covers every name the handoff passes)
  H2  scrub_handoff_env drops exactly the '' ones; seat_clones('') is the default, never []
  H3  end to end: `wrapup.py unit --clone <default seat clone>` with every HANDOFF_ENV name set to '' (but the state dir)
      carries the seat clone and files nothing; main() under RIMFLOW_SHARED_BRIDGE='' still reads the default lock
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wrapup  # noqa: E402
import role_launch  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        FAILS.append(name)


def main():
    check("H1 handoff names agree", tuple(wrapup.HANDOFF_ENV) == tuple(role_launch.HANDOFF_ENV),
          "%s vs %s" % (wrapup.HANDOFF_ENV, role_launch.HANDOFF_ENV))

    env = {"RM_WRAPUP_SEAT_CLONES": "", "RIMFLOW_SHARED_BRIDGE": "", "RM_DATA_ROOT": "/x", "OTHER": ""}
    gone = wrapup.scrub_handoff_env(env)
    check("H2 scrub drops the empty handoff names only", sorted(gone) == ["RIMFLOW_SHARED_BRIDGE", "RM_WRAPUP_SEAT_CLONES"]
          and env == {"RM_DATA_ROOT": "/x", "OTHER": ""}, repr(env))
    default = [os.path.realpath(wrapup.SEAT_CLONES_DEFAULT)]
    check("H2 seat_clones('') is the default", wrapup.seat_clones({"RM_WRAPUP_SEAT_CLONES": ""}) == default)

    with tempfile.TemporaryDirectory() as d:
        sd = os.path.join(d, "wrapup")
        e = {k: "" for k in wrapup.HANDOFF_ENV if k != "PATH"}
        e.update(PATH=os.environ.get("PATH", "/usr/bin:/bin"), RM_WRAPUP_DIR=sd, RM_WRAPUP_PREV_LOG="")
        r = subprocess.run([sys.executable, os.path.join(HERE, "wrapup.py"), "unit", "--unit", "rm-role-test-1",
                            "--seat", "BENCH", "--clone", wrapup.SEAT_CLONES_DEFAULT], env=e, capture_output=True,
                           text=True, timeout=120)
        rows = []
        try:
            with open(os.path.join(sd, "runs.jsonl")) as f:
                rows = [json.loads(ln) for ln in f if ln.strip()]
        except OSError:
            pass
        rec = rows[-1] if rows else {}
        clone = [x for x in rec.get("rows", []) if x.get("kind") == "clone"]
        check("H3 unit exits 0", r.returncode == 0, (r.stderr or "")[-200:])
        check("H3 seat clone carried, nothing filed", rec.get("filed") == 0 and len(clone) == 1
              and clone[0]["act"] == "carried", json.dumps(rec)[:300])
        # the bridge, through main(): RIMFLOW_SHARED_BRIDGE='' must fall back to the default lock path (here a temp
        # lock held by another agent), never read as "free" by blindness
        lock = os.path.join(d, "BRIDGE_SHARED.json")
        with open(lock, "w") as f:
            json.dump({"holder": "OTHERSEAT", "clone": "/elsewhere", "purpose": "selftest"}, f)
        keys = ("RIMFLOW_SHARED_BRIDGE", "RM_WRAPUP_DIR", "RM_WRAPUP_SEAT_CLONES", "RM_WRAPUP_PREV_LOG")
        saved = {k: os.environ.get(k) for k in keys}
        saved_default = wrapup.SHARED_BRIDGE_DEFAULT
        sd2 = os.path.join(d, "wrapup2")
        try:
            os.environ.update(RIMFLOW_SHARED_BRIDGE="", RM_WRAPUP_DIR=sd2, RM_WRAPUP_SEAT_CLONES="", RM_WRAPUP_PREV_LOG="")
            wrapup.SHARED_BRIDGE_DEFAULT = lock
            rc = wrapup.main(["unit", "--unit", "rm-role-test-2", "--seat", "BENCH", "--clone",
                              wrapup.SEAT_CLONES_DEFAULT])
        finally:
            wrapup.SHARED_BRIDGE_DEFAULT = saved_default
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        with open(os.path.join(sd2, "runs.jsonl")) as f:
            rec2 = [json.loads(ln) for ln in f if ln.strip()][-1]
        br = [x for x in rec2.get("rows", []) if x.get("kind") == "bridge"]
        check("H3 main() sees the default bridge lock under RIMFLOW_SHARED_BRIDGE=''", rc == 0 and len(br) == 1
              and "OTHERSEAT" in br[0].get("why", ""), json.dumps(br)[:200])

    print("selftest_wrapup_handoff_env: %s" % ("FAIL " + ", ".join(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
