#!/usr/bin/env python3
"""Class guard (OPS_TIMER_REPAIR_EC51): a unit, hook or role retired on purpose takes its live promises with it.

RimPulse was retired 2026-11-03 (5734f22602): its units were deleted, but their baseline lines and the promise
OPS_TIMER_REPAIR_EC51 closed on (`unit=rm-pulse-health.timer`) stayed, so the deadman sweep reopened a finished
fix and spawned LIVE_RESTORE_RM_PULSE_* for a unit nobody wants back. Retiring is a line in
src/RimMandrake/rimflow/live_retired.txt; deadman_check.promises() then sweeps no promise naming it.
Fixtures plus the two real files; no ledger or systemd touched.

    python3 src/RimMandrake/Utils/selftest_live_retired.py
    python3 src/RimMandrake/Utils/selftest_live_retired.py --retired /dev/null   # replays the instance: no list, red
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_live_retired_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
import deadman_check as DM  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class It:
    def __init__(self, state="done", live=None, live_broken=None):
        self.state, self.live, self.live_broken, self.live_repeats = state, live, live_broken, 0


INSTANCE = "unit=rm-pulse-health.timer max_age=10m"
DIGEST = "unit=rm-pulse-digest.timer max_age=35h"
UPDATE_ITEM = ("unit=rm-pulse-update.timer reading=/mnt/d/ClaudeWork/rimmandrake/pulse-deploy/.git/pulse_update_last_good "
               "max_age=2h")


def sweep_entry(retired_path=None):
    """The real entry point: `deadman_check.py run` (what rm-deadman.timer runs) must hand the sweep the real retired
    file, not just promises() when a test passes it. Drive main(["run"]) with the ledger, systemd and arms faked; record
    what promises() returned inside the sweep and hand the sweep nothing to check (no systemctl is called)."""
    import live_line
    seen = []
    real_promises = DM.promises

    def recording(*a, **k):
        seen.extend(real_promises(*a, **k))
        return []
    items = {"OPS_TIMER_REPAIR_EC51": It(live=INSTANCE, live_broken="is-enabled says 'not-found'"),
             "LIVING_FIXTURE": It(live="unit=rm-living-fixture.timer max_age=1h")}
    saved = (DM.promises, DM.read_items, DM.load_baseline, DM.stamps, DM.arm_faults, live_line.can_see, DM.RETIRED_FILE)
    base = DM.load_baseline()
    try:
        DM.promises, DM.read_items = recording, (lambda: items)
        DM.load_baseline = lambda path=None: base + [INSTANCE, "unit=rm-pulse-brief.timer max_age=14h"]
        DM.stamps, DM.arm_faults = (lambda mode=None: {}), (lambda st, now, runner=None: {})
        live_line.can_see = lambda *a, **k: True
        if retired_path:
            DM.RETIRED_FILE = Path(retired_path)
        rc = DM.main(["run"])
    finally:
        (DM.promises, DM.read_items, DM.load_baseline, DM.stamps, DM.arm_faults, live_line.can_see,
         DM.RETIRED_FILE) = saved
    lines = [r["line"] for r in seen]
    check(rc == 0 and "unit=rm-living-fixture.timer max_age=1h" in lines,
          "`deadman_check.py run` reaches the sweep and still sweeps a living promise (rc=%s, %d rows)" % (rc, len(lines)))
    check(not [l for l in lines if "rm-pulse-" in l],
          "`deadman_check.py run` (the rm-deadman.timer entry point) sweeps no retired RimPulse promise, item or baseline")


def main(retired_path=None):
    if not hasattr(DM, "load_retired"):
        check(False, "deadman_check has no retired-promises list: a deleted unit's promise is swept for ever")
        return
    retired = DM.load_retired(retired_path)
    baseline = DM.load_baseline()
    # the instance: the item closed on rm-pulse-health, the unit retired with RimPulse, the sweep reopened it
    items = {"OPS_TIMER_REPAIR_EC51": It(live=INSTANCE, live_broken="is-enabled says 'not-found'")}
    rows = DM.promises(items, baseline, retired)
    check(not [r for r in rows if "rm-pulse-health" in r["line"]], "a retired unit's promise is not swept (the instance)")
    check(not [r for r in rows if "rm-pulse-" in r["line"] or "im_back_hook" in r["line"]],
          "no RimPulse promise survives in the baseline")
    # LIVE_RESTORE_RM_PULSE_HEALTH: spawned "from the baseline", so the baseline route must hold too, not only the item's
    health = DM.promises({}, baseline + [INSTANCE], retired)
    check(not [r for r in health if "rm-pulse-health" in r["line"]],
          "a baseline promise for the retired rm-pulse-health.timer is not swept (LIVE_RESTORE_RM_PULSE_HEALTH)")
    # LIVE_RESTORE_RM_PULSE_BRIEF: the baseline line for rm-pulse-brief.timer (spawned by the sweep) is not swept
    brief = DM.promises({}, baseline + ["unit=rm-pulse-brief.timer max_age=14h"], retired)
    check(not [r for r in brief if "rm-pulse-brief" in r["line"]],
          "a baseline promise for the retired rm-pulse-brief.timer is not swept (LIVE_RESTORE_RM_PULSE_BRIEF)")
    # LIVE_RESTORE_RM_PULSE_DIGEST: the baseline line 2a1e978b75 wrote for the digest timer, deleted with RimPulse
    rows = DM.promises({}, [DIGEST], retired)
    check(not rows, "the retired digest timer's old baseline line is not swept (LIVE_RESTORE_RM_PULSE_DIGEST)")
    # LIVE_RESTORE_RM_PULSE_STREAMS: the streams timer was RENAMED, not dropped: the old name is retired, the new one promised
    streams = DM.promises({}, baseline + ["unit=rm-pulse-streams.timer max_age=2h"], retired)
    check(not [r for r in streams if "rm-pulse-streams" in r["line"]],
          "a baseline promise for the retired rm-pulse-streams.timer is not swept (LIVE_RESTORE_RM_PULSE_STREAMS)")
    check("unit=rm-streams-collect.timer" in {DM.subject(l) for l in baseline},
          "its successor rm-streams-collect.timer is promised in the baseline (LIVE_RESTORE_RM_PULSE_STREAMS)")
    # LIVE_RESTORE_RM_PULSE_UPDATE: the updater was RENAMED too (rm-pulse-update -> rm-deploy-update); same rule
    update = DM.promises({}, baseline + ["unit=rm-pulse-update.timer max_age=2h"], retired)
    check(not [r for r in update if "rm-pulse-update" in r["line"]],
          "a baseline promise for the retired rm-pulse-update.timer is not swept (LIVE_RESTORE_RM_PULSE_UPDATE)")
    check("unit=rm-deploy-update.timer" in {DM.subject(l) for l in baseline},
          "its successor rm-deploy-update.timer is promised in the baseline (LIVE_RESTORE_RM_PULSE_UPDATE)")
    # PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT: closed on the old updater's name; the sweep reopened it 2026-11-03 ('not-found')
    fix = DM.promises({"PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT": It(live=UPDATE_ITEM, live_broken="is-enabled says 'not-found'")},
                      [], retired)
    check(not fix, "a settled item's promise on the retired rm-pulse-update.timer is not swept "
                   "(PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT)")
    # LIVE_RESTORE_IM_BACK_HOOK: the "I'm back" hook was deleted with RimPulse; its hook promise must not be swept
    back = DM.promises({}, baseline + ["hook=im_back_hook.py"], retired)
    check(not [r for r in back if "im_back_hook" in r["line"]],
          "a baseline promise for the retired hook im_back_hook.py is not swept (LIVE_RESTORE_IM_BACK_HOOK)")
    # the class, on fixtures: every kind of subject, from the baseline and from a settled item
    fx = DM.parse_retired(["unit=rm-gone.timer  # retired", "hook=gone_hook.py", "role=Gone"])
    lines = ["unit=rm-gone.timer max_age=2h", "unit=rm-here.timer max_age=2h", "hook=gone_hook.py", "role=Gone max_age=3d"]
    got = DM.promises({"X": It(live="reading=/x unit=rm-gone.timer max_age=6h"), "Y": It(live="unit=rm-here.timer max_age=1h")},
                      lines, fx)
    check(sorted(r["line"] for r in got) == ["unit=rm-here.timer max_age=1h", "unit=rm-here.timer max_age=2h"],
          "unit, hook and role retirements all hold, from the baseline and from an item; the living stay swept")
    check(DM.subject("max_age=2h unit=rm-gone.timer") == "unit=rm-gone.timer" and DM.subject("once: why") == "",
          "the subject is found in any field order; `once:` has none")
    check(DM.promises({"Y": It(live="unit=rm-here.timer max_age=1h")}, [], ()) != [], "no retired list sweeps as before")
    # the two files never disagree: a line is either promised or retired
    both = {DM.subject(l) for l in baseline} & retired
    check(not both, "no subject is both promised in the baseline and retired (%s)" % sorted(both))
    sweep_entry(retired_path)
    try:
        DM.parse_retired(["unit=rm-x.timer max_age=2h garbage"])
        check(False, "a retired line that does not parse is refused")
    except Exception:  # noqa: BLE001
        check(True, "a retired line that does not parse is refused")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--retired") + 1] if "--retired" in a else None)
    print("FAIL %d" % len(FAILS) if FAILS else "ALL OK")
    sys.exit(1 if FAILS else 0)
