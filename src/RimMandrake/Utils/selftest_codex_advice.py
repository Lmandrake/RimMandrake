#!/usr/bin/env python3
"""selftest for codex_advice.py and its callers: Codex's door asks the account plan (`./acct can-use codex`).

Offline: a plan file and a planted frame in a temp dir (RM_ACCOUNT_PLAN_DIR, RM_ACCOUNT_PLAN_FRAME), codex never started
(the door's finder and subprocess are stubbed). Proves: over its leave line a consult reaches Codex; at or under it
every consult is refused before Codex starts with the plan's line, exit 4, required or not, and the refusal is
appended; on the reset day the line is lifted; a plan or a meter that cannot be read is COULD NOT LOOK and the job is
sent; no fallback runs; the allocator's advice line is the same answer; the art-eval callers read the exit codes.
"""
import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "art_eval"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_codex_advice_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP)
os.environ["RM_ACCOUNT_PLAN_DIR"] = str(TMP / "plan")
os.environ["RM_ACCOUNT_PLAN_FRAME"] = str(TMP / "frame.json")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
os.environ.pop("RM_CODEX_REQUIRED", None)
import account_plan as AP  # noqa: E402
import codex_advice as CA  # noqa: E402
import gpt_consult as GC  # noqa: E402
import slot_allocator as SA  # noqa: E402

FAILS = []
NOW = time.time()


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


LEGACY = json.loads((HERE / "switching_plan.json").read_text())
LEGACY["exceptions"] = []
PLAN = AP.convert_legacy(LEGACY, json.loads((HERE / "account_plan.seed.json").read_text()))     # codex: leave 25
LINE = next(s["leave"] for s in PLAN["steps"] if s["use"] == "codex")


def codex(left, hours=100.0, ok=True):
    """Plant Codex's reading: `left` percent, `hours` to its reset; ok False = not MEASURED."""
    cx = {"left": left if ok else None, "ok": ok, "state": "MEASURED" if ok else "UNMEASURED",
          "reset": NOW + hours * 3600, "reset_passed": False, "age_min": 1.0, "last_left": left,
          "why": "" if ok else "no weekly reading", "burn_h": 0.5}
    (TMP / "frame.json").write_text(json.dumps({"now": NOW, "live": "lukas", "runs": [], "rows": {}, "codex": cx}))


AP.commit(lambda _old: copy.deepcopy(PLAN), {"why": "selftest", "create": True}, base=None)

# 1. the advice is the plan's answer
for left, hours, ok, want in [(LINE + 30, 100, True, "OK"), (LINE + 0.5, 100, True, "OK"), (LINE, 100, True, "LINE"),
                              (LINE - 5, 100, True, "LINE"), (0, 100, True, "LINE"), (50, 100, False, "UNMEASURED"),
                              (LINE - 5, 10, True, "OK"), (0, 10, True, "LINE")]:
    codex(left, hours, ok)
    got = CA.advice()
    check(f"advice: codex {left}% left, {hours} h to its reset, measured={ok} -> {want}", got["state"] == want, got)
codex(LINE - 5)
check("a refusal's line names what is left and the line", "%g%% left" % (LINE - 5) in CA.advice()["why"]
      and "%g%% line" % LINE in CA.advice()["why"], CA.advice())
codex(LINE - 5, 10)
check("on the reset day the line is lifted, and the answer says so", "reset day" in CA.advice()["why"], CA.advice())

# 2. the allocator's advice line is the same answer (one rule, two readers)
os.environ.pop("RM_ACCOUNT_PLAN_FRAME")
(TMP / "plan" / "frame.json").write_text(json.dumps({"at": NOW, "codex": json.loads((TMP / "frame.json").read_text())["codex"]}))
st, line = SA.codex_use(NOW)
check("slot_allocator reads the plan's answer from the last timed pass", st == "OK" and "reset day" in line, (st, line))
st, line = SA.codex_use(NOW + 21 * 60)
check("a timed reading older than 20 min is could not look for the allocator", st == "UNMEASURED" and "COULD NOT LOOK" in line, (st, line))
os.environ["RM_ACCOUNT_PLAN_FRAME"] = str(TMP / "frame.json")


# 3. gpt_consult enforces it before Codex starts
class Started(Exception):
    pass


def boom():
    raise Started()


GC.door.find_codex = lambda side: boom()     # the door's finder: reached only if the gate let it through
os.environ.setdefault("GPT_DOOR_LOG_DIR", tempfile.mkdtemp())
runs = []
GC.subprocess.run = lambda *a, **k: runs.append(a) or (_ for _ in ()).throw(AssertionError("subprocess ran"))


def consult(*argv):
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = GC.main(["a question", *argv])
        except Started:
            rc = "STARTED"
    return rc, err.getvalue()


ref = CA.refusals_path()
n0 = len(ref.read_text().splitlines()) if ref.is_file() else 0
codex(LINE - 5)
rc, err = consult()
check("LINE: a consult is refused with exit 4, Codex not started", rc == CA.EXIT_LINE == 4, (rc, err))
check("LINE: the refusal carries the plan's line, the command that changes it, and no fallback",
      "REFUSED (Codex at its leave line)" in err and "at or under its" in err and "./acct line codex" in err
      and "no Claude fallback" in err, err)
rc, err = consult("--required", "code review round (standing_rulings §Code review)")
check("LINE: a consult marked required is refused too (the line is the owner's reserve)", rc == CA.EXIT_LINE
      and "marked required" in err, (rc, err))
lines = ref.read_text().splitlines() if ref.is_file() else []
check("LINE: each refusal is appended to codex_refusals.jsonl", len(lines) == n0 + 2
      and json.loads(lines[-1])["state"] == "LINE", lines[-1:])
check("no subprocess (no fallback reviewer) ran on any refusal", runs == [], runs)
codex(LINE - 5, 10)
rc, _ = consult()
check("reset day: the same level reaches Codex", rc == "STARTED", rc)
codex(LINE + 30)
rc, err = consult()
check("OK: a consult reaches Codex, with no gate line", rc == "STARTED" and "COULD NOT LOOK" not in err, (rc, err))
codex(50, ok=False)
rc, err = consult()
check("an unread meter: COULD NOT LOOK is said, and the job is sent", rc == "STARTED" and "COULD NOT LOOK" in err
      and "sent" in err, (rc, err))
plan_file = TMP / "plan" / "plan.json"
kept = plan_file.read_text()
plan_file.unlink()
rc, err = consult()
check("no plan file: COULD NOT LOOK is said, and the job is sent", rc == "STARTED" and "COULD NOT LOOK" in err, (rc, err))
plan_file.write_text("{broken")
rc, err = consult()
check("a plan file that is refused: COULD NOT LOOK, sent", rc == "STARTED" and "COULD NOT LOOK" in err, (rc, err))
plan_file.write_text(kept)
codex(LINE - 5)
saved = os.environ.pop("RM_ACCOUNT_PLAN_DIR")
check("a selftest child that names no plan folder reads no live plan", CA.advice()["state"] == "UNMEASURED")
os.environ["RM_ACCOUNT_PLAN_DIR"] = saved
check("a selftest child that names its plan folder still reads it", CA.advice()["state"] == "LINE")
doc = (HERE / "gpt_consult.py").read_text()
check("gpt_consult's own text states no percent of Codex's line", "25%" not in doc and "25 percent" not in doc)

# 4. the art-eval callers
import runner as R  # noqa: E402

seen = []


class Res:
    def __init__(self, rc):
        self.returncode, self.stderr, self.stdout = rc, "REFUSED", ""


def fake_run(rc):
    def run(cmd, **k):
        seen.append(cmd)
        return Res(rc)
    return run


work = TMP / "work"
work.mkdir()
R.subprocess.run = fake_run(4)
_, meta = R.Reviewers().gpt("p", [], work)
cmd = seen[-1]
check("art-eval second look passes --required with the pipeline rule",
      "--required" in cmd and cmd[cmd.index("--required") + 1] == R.SECOND_LOOK_RULE, cmd)
check("art-eval: exit 4 is read as Codex refused at its leave line", meta.get("codex_refused") == "LINE" and meta.get("error"), meta)
_, meta = R.call_gpt("p", [], work)
check("art-eval: a bare call_gpt (race.py's experiments) is not marked required", "--required" not in seen[-1], seen[-1])
import re  # noqa: E402
race = (HERE / "art_eval" / "race.py").read_text()
calls = [race[m.start():m.start() + 200] for m in re.finditer(r"R\.call_gpt\(", race)]   # each call, + its args
check("race.py's GPT calls are found and none is marked required",
      len(calls) == 2 and not any("required" in c for c in calls) and "SECOND_LOOK_RULE" not in race, calls)

print(f"{'FAIL' if FAILS else 'PASS'}: selftest_codex_advice ({len(FAILS)} failing)")
sys.exit(1 if FAILS else 0)
