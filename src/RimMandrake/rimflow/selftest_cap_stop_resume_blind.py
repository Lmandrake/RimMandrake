#!/usr/bin/env python3
"""selftest_cap_stop_resume_blind: a run resumed or continued after a spend watchdog stop is never told why it stopped
(RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED; owner 2026-11-16: "I don't like how you're telling the
agent how much it's spent. This has been shown to reduce their creativity and obsess on cost savings...").

2026-11-18 ~7:50 PM PST: the Sump biome reader resumed a session the watchdog had stopped, read its item with
`rimflow show`, found the run-end note "Result: Stopped by spend_watchdog at its cap ($15) ... 3,856,777 weighted
tokens", and wrote that it stopped reading early to stay under the cap.

Hermetic, no model call: a real spend_watchdog.py run stops a fake claude child over its cap; detached_helper.finish
ends that run (fake runner, item reader and waker; temp records and Conductor log); left_open_continue launches its
continuation (fake launch). Then:
  A  the run-end note on the item (what `rimflow show` gives the successor) names no cap, spend, budget, remainder,
     dollar or token figure, and no path to the result file that holds them; it says the run was interrupted
  B  the continuation's brief (header + the original brief) names none of them, and says it was interrupted
  C  the people-facing record keeps the true cause: the Conductor log line says the watchdog stopped it at its cap, in
     weighted tokens (no dollars), with the output path; the run record keeps the result file and its dollars
  D  a run that ends success still notes its own result words; its note carries no token figure either
  E  mutants: a note that quotes the watchdog result, and a header that says "cap", are caught by the A/B check
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_cap_stop_resume_blind_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import left_open_continue as LOC  # noqa: E402
import spend_watchdog as SW  # noqa: E402

FAILS = []
LOG = os.environ["RM_CONDUCTOR_LOG"]
ITEM = "RIMMANDRAKE_READ_FIVE_BIOME_PAGES_SECOND_READER"
# wording that tells an agent about its spend or the stop's cause
LEAK = re.compile(r"(?i)\bcap\b|\bcapped\b|spend|\bspent\b|budget|remain|\$\s?\d|dollar|\busd\b|weighted|\btokens?\b"
                  r"|watchdog|\blimit\b")


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def leaks(text):
    return sorted({m.group(0) for m in LEAK.finditer(text or "")})


# ------------------------------------------------------------------ a real watchdog stop
proj = os.path.join(TMP, "projects", "-tmp-clone")
os.makedirs(proj)
os.makedirs(DH.runs_dir(), exist_ok=True)
line = json.dumps({"type": "assistant", "timestamp": "2026-11-18T10:00:00Z", "message": {
    "id": "k", "model": "claude-opus-5-5", "usage": {"input_tokens": 0, "cache_creation_input_tokens": 0,
                                                     "cache_read_input_tokens": 0, "output_tokens": 9000000}}}) + "\n"
child = os.path.join(TMP, "fakeclaude.py")
with open(child, "w") as f:
    f.write("import sys, time, os\nsid = sys.argv[sys.argv.index('--session-id') + 1]\n"
            "open(os.path.join(%r, sid + '.jsonl'), 'w').write(%r)\nprint('partial', flush=True)\ntime.sleep(60)\n"
            % (proj, line))
T0 = time.time()
UNIT = "rm-detached-bench-read-five-biome-pages-%d" % int(T0)
OUT = os.path.join(DH.runs_dir(), UNIT + ".out.json")
ERR = os.path.join(DH.runs_dir(), UNIT + ".err")
with open(OUT, "w") as fo, open(ERR, "w") as fe:
    rc = subprocess.run([sys.executable, SW.__file__, "--cap-usd", "15", "--poll-s", "0.3", "--grace-s", "3",
                         "--projects", os.path.join(TMP, "projects"), "--", sys.executable, child, "--model", "opus"],
                        stdout=fo, stderr=fe, timeout=90).returncode
res = json.load(open(OUT))
check("setup: the watchdog stopped the child and wrote its cap result", rc != 0 and res.get("stopped_by") == "spend_watchdog",
      open(OUT).read()[:200])

clone = os.path.join(TMP, "clones", ITEM + ".det")
os.makedirs(clone)
src = os.path.join(DH.runs_dir(), UNIT + ".brief.src.md")
BRIEF = "# Second reader: check the rewritten designs for five biomes\n\nRead every source to its end.\n"
with open(src, "w", encoding="utf-8") as f:
    f.write(BRIEF)
DH.write_record({"unit": UNIT, "seat": "BENCH", "item": ITEM, "clone": clone, "clone_how": "reused", "model": "opus",
                 "max_s": None, "budget_usd": 15.0, "at": T0, "state": os.environ["RM_DISPATCHER_STATE"],
                 "status": "running", "brief_src": src, "out": OUT, "err": ERR, "continue_on_cap": 1})

NOTES = []


class R(object):
    def __init__(self, out=""):
        self.returncode, self.stdout, self.stderr = 0, out, ""


def runner(argv, **kw):
    if "note" in argv and "--text" in argv:
        NOTES.append(argv[argv.index("--text") + 1])
    return R("PUBLISHED abcdef1234567")


open(LOG, "w").close()
KICKED = []
DH.finish(UNIT, now=T0 + 400, env={"SERVICE_RESULT": "exit-code", "EXIT_CODE": "exited", "EXIT_STATUS": "1"},
          runner=runner, item_reader=lambda c, i: {"state": "claimed", "notes": []}, waker=lambda *a: None,
          continuer=lambda r, p: KICKED.append(p) or "continue kicked", log_path=LOG)

# ------------------------------------------------------------------ A: the note the successor reads
note = NOTES[-1] if NOTES else ""
check("A: finish wrote one run-end note on the item", len(NOTES) == 1, str(NOTES))
check("A: the run-end note names no cap, spend, budget, remainder, dollar or token figure (%s)" % leaks(note),
      note and not leaks(note), note)
check("A: the run-end note gives no path to the result file", OUT not in note and ERR not in note, note)
check("A: the run-end note says the run was interrupted", "interrupted" in note.lower(), note)

# ------------------------------------------------------------------ B: the continuation's brief
LAUNCHES = []


def fake_launch(seat, item, brief, model, max_s, budget, **kw):
    LAUNCHES.append(brief)
    return 0, "DETACHED rm-detached-bench-read-five-biome-pages-cont\n  item %s" % item


plan = (DH.read_record(UNIT) or {}).get("continue_plan") or {}
check("B: finish planned one continuation", plan.get("act") == "continue" and len(KICKED) == 1, str(plan))
gates = {"paused": lambda mod: None, "held": lambda mod: None, "voided": lambda unit: False, "blocked": lambda s: None}
LOC.run(UNIT, now=T0 + 430, launch_fn=fake_launch, gates=gates, log_path=LOG,
        reader=lambda target: {"state": "doing", "wait_until": None},     # the step's recheck: still open
        plan_dir=os.path.join(TMP, "no_account_notice"))                  # never the live account's drain
brief = LAUNCHES[0] if LAUNCHES else ""
head = brief.split("---- the previous run's brief ----")[0]
check("B: the continuation was launched", bool(brief), str(LAUNCHES))
check("B: its brief names no cap, spend, budget, remainder, dollar or token figure (%s)" % leaks(brief),
      brief and not leaks(brief), brief[:600])
check("B: its header says the run was interrupted and to carry on", "interrupted" in head.lower()
      and "carry on" in head.lower(), head)

# ------------------------------------------------------------------ C: the people-facing record keeps the cause
log = open(LOG).read()
ended = [ln for ln in log.splitlines() if UNIT in ln and "DETACHED RUN ENDED" in ln]
cl = ended[-1] if ended else ""
check("C: the Conductor log line says the watchdog stopped it at its cap", "cap" in cl and "watchdog" in cl, cl)
check("C: the Conductor log line states the cap in weighted tokens, no dollars", "weighted tokens" in cl
      and not re.search(r"\$\s?\d", cl), cl)
check("C: the Conductor log line carries the output path", OUT in cl, cl)
rec = DH.read_record(UNIT) or {}
check("C: the run record keeps the result file and its dollars", rec.get("out") == OUT
      and isinstance(rec.get("cost_usd"), float), str({k: rec.get(k) for k in ("out", "cost_usd")}))

# ------------------------------------------------------------------ D: an ordinary success run
U2 = UNIT + "-ok"
OUT2 = os.path.join(DH.runs_dir(), U2 + ".out.json")
with open(OUT2, "w") as f:
    json.dump({"type": "result", "subtype": "success", "is_error": False, "result": "Two of five pages are published.",
               "usage": {"input_tokens": 10, "output_tokens": 2000}}, f)
DH.write_record({"unit": U2, "seat": "BENCH", "item": ITEM, "clone": clone, "clone_how": "reused", "model": "opus",
                 "max_s": None, "budget_usd": 15.0, "at": T0, "state": os.environ["RM_DISPATCHER_STATE"],
                 "status": "running", "brief_src": src, "out": OUT2, "err": OUT2 + ".err"})
del NOTES[:]
DH.finish(U2, now=T0 + 400, env={"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"},
          runner=runner, item_reader=lambda c, i: {"state": "done", "notes": []}, waker=lambda *a: None,
          continuer=lambda r, p: "none", log_path=LOG)
n2 = NOTES[-1] if NOTES else ""
check("D: a success run's note keeps its own result words", "Two of five pages are published." in n2, n2)
check("D: a success run's note carries no token figure (%s)" % leaks(n2), n2 and not leaks(n2), n2)

# ------------------------------------------------------------------ E: mutants
check("E: a note quoting the watchdog result is caught", bool(leaks(note + " Result: " + res.get("result", ""))))
check("E: a header naming the cap is caught", bool(leaks(head.replace("interrupted", "stopped at its cap"))))
check("E: the old run-end note wording is caught", bool(leaks(
    "DETACHED run u ended exit-code/claude-error (exited 1) after 1000 s, 3,856,777 weighted tokens (model fable).")))

print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
