#!/usr/bin/env python3
"""selftest_timer_prune: the timer audit of 2026-11-03, as enacted (TIMERS_PRUNE_AUDIT_FINALLY_READ).

Retired (uninstalled 2026-11-04; unit text kept in D:\\ClaudeWork\\rimmandrake\\backups\\timers_retired_2026-11-04):
rm-arena-anchor, rm-replay-watch, rm-v3-vs-v2, account-plan, claude-account-warm. Slowed: rm-mirror 15 min,
rm-telemetry-export 5 min, rm-arteval-autojudge 2 h. Kept as they are, against the audit's text, on a re-read:
testq-tick stays at 60 s (its slow-down was "while the steward is BRAKED", and it was RUNNING), testq-steward-watch
stays its own timer (the audit's keep-list names it, and steward.py's STALE_S of 300 s assumes a 60 s tick).

Repo half: always. Live half: only where `systemctl --user` answers; elsewhere one UNMEASURED line, not a failure.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []
RETIRED = ("rm-arena-anchor", "rm-replay-watch", "rm-v3-vs-v2", "account-plan", "claude-account-warm")
SLOWED = {  # unit -> (repo file, timer key, value systemd reports)
    "rm-mirror": (HERE / "systemd/rm-mirror.timer", "OnUnitInactiveSec=15min", "OnUnitInactiveUSec=15min"),
    "rm-telemetry-export": (HERE / "telemetry/systemd/rm-telemetry-export.timer", "OnUnitActiveSec=5min",
                            "OnUnitActiveUSec=5min"),
    "rm-arteval-autojudge": (HERE / "systemd/rm-arteval-autojudge.timer", "OnUnitActiveSec=2h", "OnUnitActiveUSec=2h"),
}
KEPT_ACTIVE = ("testq-tick", "testq-steward-watch")


def check(cond, what, detail=""):
    print("%s  %s%s" % ("PASS" if cond else "FAIL", what, "" if cond else "  -- %s" % detail))
    if not cond:
        FAILS.append(what)


def names_in(text):
    return [n for n in RETIRED if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(n), text)]


# --- repo: the retired names are gone from what reads them
for rel in ("deadman_check.py", "running_now_families.json", "../rimflow/dispatcher_schedule.json"):
    p = HERE / rel
    check(not names_in(p.read_text(encoding="utf-8")), "%s names no retired timer" % p.name,
          names_in(p.read_text(encoding="utf-8")))
# ops_clocks.json: its _doc and ops_clocks.UNIT_GLOBS keep "account-plan" on purpose, so a reinstall fails the check
oc = json.loads((HERE / "systemd/ops_clocks.json").read_text(encoding="utf-8"))
oc_names = names_in(json.dumps([oc["clocks"], oc["outside"]]))
check(not oc_names, "ops_clocks.json clocks/outside name no retired timer", oc_names)
sched = json.loads((HERE.parent / "rimflow/dispatcher_schedule.json").read_text(encoding="utf-8"))
check(all("v3_vs_v2" != r.get("name") for k in sched if isinstance(sched[k], list) for r in sched[k]
          if isinstance(r, dict)), "dispatcher_schedule has no v3_vs_v2 entry")
check("account-plan" not in oc["clocks"], "account-plan is no Operations clock")
for n in RETIRED:
    for ext in ("service", "timer"):
        check(not (HERE / "systemd" / ("%s.%s" % (n, ext))).exists(), "no shipped %s.%s" % (n, ext))

# --- repo: the slowed timers carry their new interval
for unit, (path, key, _live) in SLOWED.items():
    lines = path.read_text(encoding="utf-8").splitlines()
    check(key in lines, "%s ships %s" % (unit, key), [l for l in lines if l.startswith("OnUnit")])

# --- repo: what the re-read kept is unchanged
tq_text = (HERE / "testq/testq.py").read_text(encoding="utf-8")
tick = re.search(r'"testq-tick\.timer": """(.*?)"""', tq_text, re.S)
watch = re.search(r'"testq-steward-watch\.timer": """(.*?)"""', tq_text, re.S)
check(bool(tick) and "OnUnitInactiveSec=60s" in tick.group(1), "testq-tick template still ticks every 60 s")
check(bool(watch) and "OnUnitInactiveSec=60s" in watch.group(1), "testq-steward-watch keeps its own 60 s timer")
check(re.search(r"^STALE_S = 300\b", (HERE / "testq/steward.py").read_text(encoding="utf-8"), re.M) is not None,
      "steward.py STALE_S is 300 s, which a 60 s tick satisfies")


# --- live: only where the user manager answers
def show(unit, prop):
    try:
        r = subprocess.run(["systemctl", "--user", "show", "-p", prop, "--value", unit], capture_output=True, text=True,
                           timeout=30, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


if show("rm-mirror.timer", "LoadState") != "loaded":
    print("UNMEASURED  live half: systemctl --user does not answer here (or rm-mirror.timer is not loaded)")
else:
    for n in RETIRED:
        st = show(n + ".timer", "LoadState")
        check(st == "not-found", "live: %s.timer is uninstalled" % n, st)
    for unit, (_p, _k, live) in SLOWED.items():
        tm = show(unit + ".timer", "TimersMonotonic") or ""
        check(live in tm, "live: %s.timer loaded with %s" % (unit, live), tm[:120])
    # A slowed timer is reinstalled, so it must come back ENABLED and ACTIVE: rm-arteval-autojudge came back with its
    # new file but disabled, twice (LIVE_RESTORE_RM_ARTEVAL_AUTOJUDGE).
    for unit in tuple(SLOWED) + KEPT_ACTIVE:
        st = show(unit + ".timer", "ActiveState")
        check(st == "active", "live: %s.timer active" % unit, st)
        en = show(unit + ".timer", "UnitFileState")
        check(en == "enabled", "live: %s.timer enabled" % unit, en)

print("selftest_timer_prune: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
