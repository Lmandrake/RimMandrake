#!/usr/bin/env python3
"""selftest for retired_loops_check.py and its deadman arm (item RIMMANDRAKE_RETIRE_RELENTLESS_ARTISAN_WHITTLE_NOTHING_TO_RESUME).
Fake systemctl/ps text only; nothing real is read.

    python3 src/RimMandrake/Utils/selftest_retired_loops_check.py
    python3 src/RimMandrake/Utils/selftest_retired_loops_check.py --broken   # feeds bad input to the good cases: must go red
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_retired_loops_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
import deadman_check as DM  # noqa: E402
import retired_loops_check as RL  # noqa: E402

FAILS = []
BROKEN = "--broken" in sys.argv


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def files(overrides=None, extra=()):
    st = {u: "masked" for u in RL.RETIRED_UNITS}
    st.update(overrides or {})
    st.update({"rm-deadman.timer": "enabled", "rm-detached-bench-x.service": "transient"})
    rows = ["%-60s %-10s %s" % (u, s, "enabled") for u, s in st.items()]
    return "\n".join(rows + list(extra)) + "\n"


UNITS = "rm-deadman.timer loaded active waiting Live promise sweep\n"
PS = "    PID COMMAND\n      1 /sbin/init\n   2001 python3 /x/Utils/deadman_check.py run\n"
BRIEF = ("   3001 /x/claude_bounded.sh -p # Brief: relentless.py is retired, see ralph_gss and whittle_stop.py rules\n")


def fake(f=None, u=None, p=None, rc=0):
    outs = {"list-unit-files": f if f is not None else files(), "list-units": u if u is not None else UNITS,
            "ps": p if p is not None else PS}
    def run(argv):
        for k, v in outs.items():
            if k in argv or k == argv[0]:
                return rc, v
        return 1, ""
    return run


def main():
    r = RL.measure(fake())
    if BROKEN:                                  # one bad input per run: the green case must turn red
        r = RL.measure(fake(f=files({"rm-relentless.timer": "enabled"})))
    check(r["status"] == "ok", "1 all retired units masked, nothing loaded -> pass (%s)" % r["line"])

    r = RL.measure(fake(f=files({"rm-artisan-now.timer": "enabled"})))
    check(r["status"] == "alarm" and "rm-artisan-now.timer" in r["line"], "2 a retired unit enabled -> alarm naming it")
    r = RL.measure(fake(f=files({"whittle-claude@.service": "disabled"})))
    check(r["status"] == "alarm" and "whittle-claude@.service" in r["line"], "2b a retired unit merely unmasked -> alarm")

    live = "rm-relentless-foo.timer loaded active waiting new\n"
    r = RL.measure(fake(u=UNITS + live))
    check(r["status"] == "alarm" and "rm-relentless-foo.timer" in r["line"], "3 loaded rm-relentless-foo.timer -> alarm")
    r = RL.measure(fake(f=files(extra=["rm-whittle-bar.timer enabled enabled"])))
    check(r["status"] == "alarm" and "rm-whittle-bar.timer" in r["line"], "3b enabled rm-whittle-bar.timer file -> alarm")

    det = "rm-detached-bench-x.service loaded active running detached helper\n"
    r = RL.measure(fake(u=UNITS + det, p=PS + BRIEF))
    check(r["status"] == "ok", "4 rm-detached-bench-x.service active (and a brief that only mentions relentless.py) -> no alarm")

    r = RL.measure(fake(p=PS + "   4001 python3 /x/rimflow/relentless.py tick\n"))
    check(r["status"] == "alarm" and "relentless.py" in r["line"], "5a a relentless.py worker alive -> alarm")

    r = RL.measure(fake(rc=1))
    check(r["status"] == "unmeasured" and RL.UNMEASURED in r["line"] and RL.arm_reason(r), "5 systemctl fails -> UNMEASURED alarm")
    r = RL.measure(fake(f="garbage\n"))
    check(r["status"] == "unmeasured", "5b unparseable unit-file list -> UNMEASURED")
    r = RL.measure(fake(f="", u=""))
    check(r["status"] == "unmeasured", "5c empty output -> UNMEASURED, never a pass")

    def boom(argv):
        raise FileNotFoundError("systemctl")
    check(RL.measure(boom)["status"] == "unmeasured", "5d a missing binary -> UNMEASURED")

    doc = (HERE.parent.parent.parent / "design/RimMandrake/retired_loops_2026-11-13.md").read_text(encoding="utf-8")
    names = {u.rsplit(".", 1)[0].split("@")[0] for u in RL.RETIRED_UNITS}
    check(all(n in doc for n in names), "6 every checked unit family is named in the retirement doc")

    # deadman arm: fixed item id, files nothing when off, reading written
    DM_arm = DM.retired_loops_arm(lambda: RL.measure(fake()), 1_800_000_000.0)
    check(DM_arm == {"retired_loops": None}, "7 deadman arm quiet when off")
    rd = json.loads((TMP / "ops/retired_loops.json").read_text())
    check(rd["status"] == "ok" and rd["t"] == 1_800_000_000.0 and rd["steve_covered"] is False, "7b reading file written")
    bad = DM.retired_loops_arm(lambda: RL.measure(fake(rc=1)))
    check(bad["retired_loops"] and "UNMEASURED" in bad["retired_loops"], "7c deadman arm carries UNMEASURED reason")
    check(DM.phone_worthy({"line": None}), "7d an arm row rings the phone")

    print("FAILED %d" % len(FAILS) if FAILS else "all green")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
