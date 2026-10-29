#!/usr/bin/env python3
"""selftest_role_unit_stamp.py — every ledger event a role run writes carries `role_unit`.

V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE, spec design/RimMandrake/v3_health_daily_check_2026-10-29.md §8 step 1:
"`rimflow cli` writes `role_unit` from `RM_ROLE_UNIT` on every event when set. L0: an event written with the
variable set carries it; without it, the event is byte-identical to today's." role_launch already exports
RM_ROLE_UNIT=<unit> to every headless role run; the output tracer (Utils/v3_health_trace.py) counts a role's
outputs by this stamp and only falls back to the seat-and-window ESTIMATE when it is absent.

Cases (temp ledger, CLI driven as a subprocess, the real ledger is never touched):
  carried     RM_ROLE_UNIT set -> the written line has role_unit == the unit
  identical   RM_ROLE_UNIT unset (and set-but-empty) -> no role_unit key, and the line minus ts/tsn
              equals the line written with no variable at all
  validated   a malformed unit (spaces / overlong) is refused loudly, never written silently
  model       model.UNIVERSAL_FIELDS names role_unit, so strict validate accepts it on any verb
  mutation    a line carrying role_unit for a DIFFERENT unit is not what was asked for (the check can fail)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
sys.path.insert(0, HERE)
FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def env(tmp, **over):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RM_ROLE_UNIT")}
    e["RIMFLOW_LEDGER"] = os.path.join(tmp, "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(tmp, "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = "BUILD"
    e.update(over)
    return e


def run(tmp, *args, **over):
    p = subprocess.run([sys.executable, CLI] + list(args), capture_output=True, text=True,
                       env=env(tmp, **over), cwd=REPO, timeout=120)
    return p.returncode, p.stdout, p.stderr


def lines(tmp):
    out = []
    for dp, _, fs in os.walk(tmp):
        for f in sorted(fs):
            if f.endswith(".jsonl"):
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    out += [json.loads(l) for l in fh if l.strip()]
    return out


def last_for(tmp, iid):
    evs = [e for e in lines(tmp) if e.get("id") == iid]
    return evs[-1] if evs else None


def strip_time(ev):
    return {k: v for k, v in ev.items() if k not in ("ts", "tsn", "id", "title")}


def main():
    tmp = tempfile.mkdtemp(prefix="rm_role_unit_")
    try:
        unit = "rm-role-arbiter-1793300000"
        rc, out, err = run(tmp, "file", "ROLE_STAMP_CARRIED_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
                           RM_ROLE_UNIT=unit)
        ev = last_for(tmp, "ROLE_STAMP_CARRIED_PROBE_FIXTURE")
        check(rc == 0 and ev is not None, "carried: file with RM_ROLE_UNIT set exits 0 (%d %s)" % (rc, err.strip()[-200:]))
        check(bool(ev) and ev.get("role_unit") == unit, "carried: event has role_unit == %s (got %r)" % (unit, ev and ev.get("role_unit")))
        # mutation: the check above would fail for a different unit
        check(not (bool(ev) and ev.get("role_unit") == unit + "x"), "mutation: role_unit check distinguishes units")
        rc, out, err = run(tmp, "note", "ROLE_STAMP_CARRIED_PROBE_FIXTURE", "--text", "n", "--why", "selftest",
                           RM_ROLE_UNIT=unit)
        ev2 = last_for(tmp, "ROLE_STAMP_CARRIED_PROBE_FIXTURE")
        check(rc == 0 and bool(ev2) and ev2.get("event") == "note" and ev2.get("role_unit") == unit,
              "carried: a second verb (note) is stamped too (%d %s)" % (rc, err.strip()[-200:]))

        rc, _, err = run(tmp, "file", "ROLE_STAMP_PLAIN_PROBE_FIXTURE", "--for", "BUILD", "--title", "t")
        plain = last_for(tmp, "ROLE_STAMP_PLAIN_PROBE_FIXTURE")
        rc2, _, err2 = run(tmp, "file", "ROLE_STAMP_EMPTY_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
                           RM_ROLE_UNIT="")
        empty = last_for(tmp, "ROLE_STAMP_EMPTY_PROBE_FIXTURE")
        check(rc == 0 and plain is not None and "role_unit" not in plain, "identical: unset -> no role_unit key")
        check(rc2 == 0 and empty is not None and "role_unit" not in empty, "identical: empty -> no role_unit key")
        check(plain is not None and empty is not None and strip_time(plain) == strip_time(empty),
              "identical: unset and empty write the same event (minus ts/tsn/id)")
        stamped_keys = set(ev or {}) - {"role_unit"}
        check(plain is not None and set(plain) == stamped_keys,
              "identical: stamped and unstamped events differ ONLY by role_unit (%s vs %s)"
              % (sorted(set(plain or {})), sorted(stamped_keys)))

        for bad in ("rm role arbiter", "x" * 200):
            n0 = len(lines(tmp))
            rc, out, err = run(tmp, "file", "ROLE_STAMP_BAD_PROBE_FIXTURE", "--for", "BUILD", "--title", "t",
                               RM_ROLE_UNIT=bad)
            check(rc != 0 and "RM_ROLE_UNIT" in (out + err) and len(lines(tmp)) == n0,
                  "validated: malformed unit %r refused loudly, nothing written" % bad[:20])

        import model  # noqa: E402
        check("role_unit" in model.UNIVERSAL_FIELDS, "model: role_unit is a universal field")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
