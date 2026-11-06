#!/usr/bin/env python3
"""selftest_nightly_red_deleted_clears.py -- class guard for NIGHTLY_COP_FIX_RED_ZHIYUZ_VVZU_QJMI: a nightly red whose
test file was deleted since that night reads 0 end to end (known_reds -> ops_watch.nightly_news -> red_groups), even when
its build-cop alarm is ALREADY HELD. A held group skips the rerun gate (red_groups reruns only new groups), so before
9b4d9ef960 (known_reds.deleted_tests) nothing could cure it: Utils/arena was deleted 2026-11-05 and the alarm on
selftest_arena_judge.py was refiled under a fresh item each time the last one retired.

The fixture replays the instance: the 2026-11-05 night's CRASH of src/RimMandrake/Utils/arena/selftest_arena_judge.py
(first error line `[Errno 2] No such file or directory`, so key testing.red_zhiyuz), its alarm held, the data clone
no longer holding the file. Every rerun is off, so only the instrument's own reading can clear it.

    python3 src/RimMandrake/Utils/selftest_nightly_red_deleted_clears.py              the current instrument: green
    python3 src/RimMandrake/Utils/selftest_nightly_red_deleted_clears.py --rev <sha>  known_reds.py as of <sha> (git
                                                                                      show): before the fix, red
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--rev", help="load known_reds.py from this git revision instead of the working tree")
ARGS = ap.parse_args()

TMP = Path(tempfile.mkdtemp(prefix="st_red_deleted_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_STREAMS_BENCH"] = str(TMP / "clone")
os.environ["RM_KNOWN_REDS"] = str(TMP / "known.json")
(TMP / "ops").mkdir()
sys.path.insert(0, str(HERE))
if ARGS.rev:
    src = subprocess.run(["git", "-C", str(REPO), "show", "%s:src/RimMandrake/Utils/known_reds.py" % ARGS.rev],
                         capture_output=True, text=True, timeout=60, check=True).stdout
    (TMP / "rev").mkdir()
    (TMP / "rev" / "known_reds.py").write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("known_reds", str(TMP / "rev" / "known_reds.py"))
    K = importlib.util.module_from_spec(spec)
    sys.modules["known_reds"] = K
    K.__dict__["__file__"] = str(HERE / "known_reds.py")      # its HERE must still find rimflow/testing_policy
    spec.loader.exec_module(K)
else:
    import known_reds as K  # noqa: E402
import ops_watch as OW  # noqa: E402
K.new_items_per_pass = lambda: 8      # the live policy may be paused at 0; this test's cap is its own

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(name)


GONE = "src/RimMandrake/Utils/arena/selftest_arena_judge.py"          # deleted at 1f0e666566 (arena trial ended)
KEPT = "src/RimMandrake/Utils/selftest_kept_red.py"                   # a red whose test still exists: must stay red
AT = "2026-11-05T11:00:00Z"
NOW = K.epoch(AT) + 3 * 3600
DETAIL = ["uncaught JudgeError (rc 1) - the test died before reaching a verdict",
          "ok    split -> third fresh run, majority reject",
          "FAIL  forced: with the sandbox masks removed, the judge process CAN open the map",
          "Traceback (most recent call last):",
          "arena_judge.JudgeError: opus judge exit 2: /usr/bin/python3: can't open file "
          "'/tmp/selftest_run_x/arena_judge_st_y/fake_model.py': [Errno 2] No such file or directory"]

clone = TMP / "clone"
(clone / "Transient").mkdir(parents=True)
(clone / "src/RimMandrake/Utils").mkdir(parents=True)
(clone / "src/RimMandrake/Utils/known_reds.py").write_text("", encoding="utf-8")   # deleted_tests' proof it sees a clone
(clone / KEPT).write_text("", encoding="utf-8")                                     # GONE is not written: deleted
(clone / "Transient/selftests_nightly.log").write_text(
    "\n=== %s nightly\nCRASH (1/9) — reached no verdict: %s [uncaught JudgeError (rc 1), died]\nFAIL (1/9): %s\n"
    "RESULT: RED (green = FAIL 0 and CRASH 0)\nexit 1\n" % (AT, GONE, KEPT), encoding="utf-8")
last = "PASS          0.1s  src/x/selftest_ok.py\n"
last += "CRASH         1.4s  %s\n" % GONE + "".join("             %s\n" % ln for ln in DETAIL)
last += "FAIL          1.0s  %s\n             rc 1\n             FAIL the kept widget count is 3, want 4\n" % KEPT
last += "RESULT: RED (green = FAIL 0 and CRASH 0)\n"
lp = clone / "Transient/selftests_nightly.last"
lp.write_text(last, encoding="utf-8")
os.utime(lp, (K.epoch(AT) + 60, K.epoch(AT) + 60))
K.save([])

KEY = "testing.red_zhiyuz"
check("instance fidelity: the deleted test's first error line keys to %s" % KEY,
      "testing.red_" + K.letters("sig:" + K.normalise(K.first_error("CRASH", DETAIL), GONE)).lower() == KEY,
      K.normalise(K.first_error("CRASH", DETAIL), GONE))
(TMP / "ops" / "alarms.json").write_text(json.dumps({"NIGHTLY_RED:" + KEY: {"state": "OPEN", "item": "X"}}), encoding="utf-8")
OW.RERUN_REDS = None                    # no rerun gate: a held group never reaches it anyway, and none may cure this

pts = OW.nightly_news(NOW, {"open_ids": set(), "no_reruns": True})
check("the night is read (the fixture is seen, not blind)", pts.get("testing.nightly_unparked_reds", {}).get("m") == "MEASURED",
      pts.get("testing.nightly_unparked_reds"))
check("a HELD alarm on a red whose test file is deleted since reads 0, so it clears", (pts.get(KEY) or {}).get("v") == 0,
      pts.get(KEY))
check("the deleted test is in no red group", not any(GONE in json.dumps((p.get("x") or {}).get("news", [])) for k, p in pts.items()
                                                     if k.startswith("testing.red_")), sorted(pts))
check("... and is not counted unparked or overdue", pts["testing.nightly_unparked_reds"].get("v") == 1
      and GONE not in json.dumps(pts["testing.nightly_reds_overdue"]), (pts["testing.nightly_unparked_reds"],
                                                                      pts["testing.nightly_reds_overdue"]))
check("the instrument is not blind: a red whose test still exists keeps its group",
      any(k.startswith("testing.red_") and (p.get("v") or 0) >= 1 and KEPT in json.dumps((p.get("x") or {}).get("news", []))
          for k, p in pts.items()), sorted(pts))

print("RESULT: %s (%d failed)" % ("RED" if FAILS else "GREEN", len(FAILS)))
sys.exit(1 if FAILS else 0)
