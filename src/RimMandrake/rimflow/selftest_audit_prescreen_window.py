"""selftest_audit_prescreen_window.py - python3 src/RimMandrake/rimflow/selftest_audit_prescreen_window.py

AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN, offline (temp dirs only; the real Auditor state is never read or
written): the pre-screen window starts at the last Auditor run that FINISHED done (the stamp), so a skipped daily run's
closes are screened by the next run; no stamp -> now-1d, said; a failed run never moves the stamp; --days overrides.
"""
import contextlib, io, json, os, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import audit_prescreen as ap                                       # noqa: E402  the module role_launch imports
import role_launch as RL                                           # noqa: E402
from selftest_dispatcher import D, fresh, sched                    # noqa: E402

FAILED = []
TMP = tempfile.mkdtemp(prefix="selftest_audit_prescreen_window_")
PAST = os.path.join(TMP, "audits.jsonl")
open(PAST, "w").close()


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


def ev(e, i, ts, seat="BENCH", **k):
    d = {"event": e, "id": i, "ts": ts, "seat": seat}
    d.update(k)
    return d


def close(i, ts):
    return [ev("claim", i, ts.replace("T10:", "T09:")), ev("close", i, ts, sha="", reason="selftest ran")]


# three days of closes; the Auditor runs daily at 13:00. Day 1's run finished; day 2's was refused (no run);
# the day-3 run must screen day 2 AND day 3.
EVENTS = (close("DAY1_BEFORE_STAMP_ITEM", "2026-10-26T10:00:00Z")      # screened by the day-1 run
          + close("DAY2_SKIPPED_ITEM", "2026-10-27T10:00:00Z")         # its run was refused
          + close("DAY3_TODAY_ITEM", "2026-10-28T10:00:00Z"))
NOW = "2026-10-28T13:00:00Z"


def run(stamp, *extra):
    out = os.path.join(TMP, "prescreen_%d.json" % len(os.listdir(TMP)))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ap.main(["--now", NOW, "--out", out, "--past-audits", PAST, "--stamp", stamp] + list(extra),
                     events=[dict(e) for e in EVENTS])
    with open(out) as f:
        doc = json.load(f)
    return rc, doc, buf.getvalue()


def items(doc):
    return sorted(r["item"] for r in doc["ranked"])


def at(iso):
    return ap._epoch(iso)


# ---- 1. one daily run skipped: stamp two days old -> both days' closes
st1 = os.path.join(TMP, "skip", "last_finished_run.json")
print("write:", ap.write_stamp(st1, at("2026-10-26T13:00:00Z"), "rm-role-auditor-1"))
rc, doc, txt = run(st1)
print("  | " + txt.splitlines()[0])
ok("skipped run: next run screens both days' closes", (rc, items(doc)), (0, ["DAY2_SKIPPED_ITEM", "DAY3_TODAY_ITEM"]))
ok("skipped run: window source is the stamp", (doc["window"]["source"], doc["since"]),
   ("stamp", "2026-10-26T13:00:00Z"))
ok("skipped run: the old fixed --days 1 would have dropped day 2", items(run(st1, "--days", "1")[1]),
   ["DAY3_TODAY_ITEM"])
ok("explicit --days overrides the stamp, said", run(st1, "--days", "1")[1]["window"]["source"], "days")

# ---- 2. stamp absent -> now-1d fallback, labelled
st2 = os.path.join(TMP, "none", "last_finished_run.json")
rc, doc, txt = run(st2)
print("  | " + txt.splitlines()[0])
ok("no stamp: now-1d fallback", (rc, items(doc), doc["since"]), (0, ["DAY3_TODAY_ITEM"], "2026-10-27T13:00:00Z"))
ok("no stamp: labelled FALLBACK in output and doc",
   (doc["window"]["source"], "FALLBACK" in txt.splitlines()[0], "no stamp" in doc["window"]["why"]),
   ("fallback", True, True))
st2b = os.path.join(TMP, "torn.json")
open(st2b, "w").write('{"at": ')
ok("torn stamp: fallback, said unreadable", (run(st2b)[1]["window"]["source"], "unreadable" in run(st2b)[2]),
   ("fallback", True))
st2c = os.path.join(TMP, "future", "s.json")
ap.write_stamp(st2c, at("2026-10-29T00:00:00Z"))
ok("stamp after --now: fallback, said", run(st2c)[1]["window"]["source"], "fallback")
st2d = os.path.join(TMP, "old", "s.json")
ap.write_stamp(st2d, at("2026-10-01T13:00:00Z"))
rc, doc, txt = run(st2d)
ok("stamp 27 days back: clamped to 7, said", (doc["window"]["source"], doc["since"], "CLAMPED" in txt),
   ("stamp_clamped", "2026-10-21T13:00:00Z", True))

# ---- 3. a failed run does not advance the stamp; a done run does (role_launch -> dispatcher.execute)
def finish(result, launched):
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: result, "procs": lambda *a, **k: []}
    rs = {"runs": [{"state": "running", "unit": "rm-role-auditor-%d" % launched, "at": launched, "scope": "S.scope",
                    "marker": "M", "item": "I", "budget": 10 ** 9, "mode": "run"}]}
    RL._supervise_one("Auditor", rs, {"run_max_s": 10 ** 6, "seat": "S"}, obs, launched + 600,
                      lambda **kw: acts.append(kw), set())
    return acts, rs["runs"][0]["state"]


class _Lk:
    def close(self):
        pass


FX = {"note": lambda i, t: (True, ""), "publish": lambda n: None, "lock": lambda: _Lk(), "paused": lambda: None,
      "off": lambda p: None}


def execute(acts, path):
    # the stamp action's path is redirected to the temp stamp: the real Auditor state dir is never written
    acts = [dict(a, path=path) if a["do"] == "role_stamp" else a for a in acts]
    D.execute(acts, sched(), fresh(), os.path.join(TMP, "root"), True, time.time(), FX, deadline=time.time() + 100)
    return acts


os.makedirs(os.path.join(TMP, "root", "inbox"), exist_ok=True)
good = {"type": "result", "subtype": "success", "is_error": False, "result": "ok",
        "usage": {k: 1 for k in RL.USAGE_KEYS}, "modelUsage": {"m": {}}}
bad = dict(good, is_error=True, subtype="error_during_execution")
st3 = os.path.join(TMP, "fail", "last_finished_run.json")
ap.write_stamp(st3, at("2026-10-26T13:00:00Z"))
day2 = int(at("2026-10-27T13:00:00Z"))
acts, state = finish(bad, day2)
execute(acts, st3)
ok("failed run: no role_stamp action", (state, [a for a in acts if a["do"] == "role_stamp"]), ("failed", []))
rc, doc, txt = run(st3)
print("  | " + txt.splitlines()[0])
ok("failed run: stamp unchanged, next run still screens the failed day",
   (doc["since"], items(doc)), ("2026-10-26T13:00:00Z", ["DAY2_SKIPPED_ITEM", "DAY3_TODAY_ITEM"]))
acts, state = finish(good, day2)
done = execute(acts, st3)
stamps = [a for a in done if a["do"] == "role_stamp"]
ok("done run: one role_stamp at its launch, written", (state, len(stamps), stamps[0].get("result")),
   ("done", 1, "stamped 2026-10-27T13:00:00Z"))
ok("done run: next window starts at it", run(st3)[1]["since"], "2026-10-27T13:00:00Z")
ok("an older run finishing late never moves the stamp back",
   ap.write_stamp(st3, at("2026-10-26T13:00:00Z")), "kept 2026-10-27T13:00:00Z")
ok("stamp write is atomic: no tmp left", [f for f in os.listdir(os.path.dirname(st3)) if ".tmp" in f], [])
dry = os.path.join(TMP, "dry.json")
D.execute([dict(stamps[0], path=dry)], sched(), fresh(), os.path.join(TMP, "root"), False, time.time(), FX,
          deadline=time.time() + 100)
ok("dry run (apply False) writes no stamp", os.path.exists(dry), False)
ok("FINISH_STAMP is beside the pre-screen's output (no new hard-wired path)",
   os.path.dirname(RL.FINISH_STAMP["Auditor"]), os.path.dirname(ap.OUT))
sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
pre = [r for r in sch["roles"] if r["name"] == "Auditor"][0]["pre_launch"]
ok("the Auditor's pre_launch no longer pins --days", [s for s in pre if "audit_prescreen.py" in " ".join(s)][0],
   ["python3", "src/RimMandrake/rimflow/audit_prescreen.py"])

print("FAILED: %s" % FAILED if FAILED else "all ok")
sys.exit(1 if FAILED else 0)
