#!/usr/bin/env python3
"""selftest for codex_advice.py and its callers (CODEX_CALLERS_ENFORCE_DRY_BY_THURSDAY).

Offline: a fake ops-watch status.json in a temp dir (RM_OPS_WATCH_DIR), codex never started (find_codex_cli and
subprocess are stubbed). Proves: the advice is read the allocator's way; HOLD refuses an unmarked gpt_consult call
before Codex starts and lets a --required one through; EXHAUSTED refuses every call (required too), names the owner's
alarm and appends the refusal; no fallback runs; the art-eval second look marks itself required and race.py's
experiments do not.
"""
import contextlib
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
os.environ.pop("RM_CODEX_REQUIRED", None)
import codex_advice as CA  # noqa: E402
import gpt_consult as GC  # noqa: E402
import slot_allocator as SA  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


def status(runway=None, mark="MEASURED", age_min=1.0):
    pts = {} if runway is None else {"codex.runway": {"m": mark, "v": runway}}
    (TMP / "status.json").write_text(json.dumps({"t": time.time() - age_min * 60, "points": pts}))


LINE = SA.load_rules()["ops"]["codex_conserve_runway"]

# 1. advice states, read through slot_allocator.ops_inputs
for rw, mark, age, want in [(LINE + 1.0, "MEASURED", 1, "OK"), (LINE / 2, "MEASURED", 1, "HOLD"),
                            (LINE / 2, "ESTIMATE", 1, "HOLD"), (0.0, "MEASURED", 1, "EXHAUSTED"),
                            (None, "MEASURED", 1, "UNMEASURED"), (LINE / 2, "UNMEASURED", 1, "UNMEASURED"),
                            (0.0, "MEASURED", 600, "UNMEASURED")]:
    status(rw, mark, age)
    got = CA.advice()["state"]
    check(f"advice runway={rw} {mark} age={age}min -> {want}", got == want, got)
(TMP / "status.json").unlink()
check("advice with no status file -> UNMEASURED", CA.advice()["state"] == "UNMEASURED")

# 2. the allocator's own advice agrees on HOLD/CONSERVE (one reading, two readers)
status(LINE / 2)
_, adv = SA._ops({"ops": SA.ops_inputs(time.time(), SA.load_rules())}, SA.load_rules(), 4, [])
check("slot_allocator says CONSERVE where codex_advice says HOLD", adv["codex"] == "CONSERVE", adv)


# 3. gpt_consult enforces it before Codex starts
class Started(Exception):
    pass


def boom():
    raise Started()


GC.codex_image.find_codex_cli = boom
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
status(LINE / 2)
rc, err = consult()
check("HOLD: unmarked consult refused with exit 4, Codex not started", rc == CA.EXIT_HOLD, (rc, err))
check("HOLD: refusal says so and offers no fallback", "REFUSED (Codex HOLD)" in err and "no Claude fallback" in err, err)
rc, _ = consult("--required", "code review round (standing_rulings §Code review)")
check("HOLD: --required consult reaches Codex", rc == "STARTED", rc)
os.environ["RM_CODEX_REQUIRED"] = "env-declared rule"
rc, _ = consult()
check("HOLD: RM_CODEX_REQUIRED consult reaches Codex", rc == "STARTED", rc)
os.environ.pop("RM_CODEX_REQUIRED")

n0 = len(ref.read_text().splitlines()) if ref.is_file() else 0
status(0.0)
rc, err = consult("--required", "any rule")
check("EXHAUSTED: even a required consult is refused with exit 5", rc == CA.EXIT_EXHAUSTED, (rc, err))
check("EXHAUSTED: refusal is loud and names the owner's alarm", "REFUSED (Codex EXHAUSTED)" in err and CA.ALARM in err, err)
lines = ref.read_text().splitlines() if ref.is_file() else []
check("EXHAUSTED: refusal appended to codex_refusals.jsonl", len(lines) == n0 + 1
      and json.loads(lines[-1])["state"] == "EXHAUSTED", lines[-1:])
check("no subprocess (no fallback reviewer) ran on any refusal", runs == [], runs)

status(LINE + 1.0)
rc, _ = consult()
check("OK: unmarked consult reaches Codex", rc == "STARTED", rc)
(TMP / "status.json").unlink()
rc, _ = consult()
check("UNMEASURED: unmarked consult reaches Codex (no reading is no brake)", rc == "STARTED", rc)
status(0.0)
os.environ["RM_UNDER_SELFTEST"], saved = "1", os.environ.pop("RM_OPS_WATCH_DIR")
check("a selftest child with no RM_OPS_WATCH_DIR reads no live advice", CA.advice()["state"] == "UNMEASURED")
os.environ["RM_OPS_WATCH_DIR"] = saved
check("a selftest child pointing RM_OPS_WATCH_DIR at a fixture still reads it", CA.advice()["state"] == "EXHAUSTED")
(TMP / "status.json").unlink()

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
check("art-eval: exit 4 is read as a Codex HOLD refusal", meta.get("codex_refused") == "HOLD" and meta.get("error"), meta)
R.subprocess.run = fake_run(5)
_, meta = R.call_gpt("p", [], work)
check("art-eval: exit 5 is read as Codex EXHAUSTED", meta.get("codex_refused") == "EXHAUSTED", meta)
check("art-eval: a bare call_gpt (race.py's experiments) is not marked required", "--required" not in seen[-1], seen[-1])
import re  # noqa: E402
race = (HERE / "art_eval" / "race.py").read_text()
calls = [race[m.start():m.start() + 200] for m in re.finditer(r"R\.call_gpt\(", race)]   # each call, + its args
check("race.py's GPT calls are found and none is marked required",
      len(calls) == 2 and not any("required" in c for c in calls) and "SECOND_LOOK_RULE" not in race, calls)

print(f"{'FAIL' if FAILS else 'PASS'}: selftest_codex_advice ({len(FAILS)} failing)")
sys.exit(1 if FAILS else 0)
