"""selftest_spoil_gate -- spoiled-run regression suite (PROOF_SPOILED_RUNS_BUILD_NO_BLANKET_GREEN).

One fixture per spoil class of GPT bridge review s7 row 14 (unknown blocking window, visitor-sensitive gap, empty
rows, DRAFT status, capped list, log blindness) must grade non-GREEN overall; need/mood/job rows go INDETERMINATE on an
unobserved visitor gap while other rows stay PASS-with-note (owner card 2026-10-24); a clean, fully observed run and a
low-TPS-only run reach GREEN (controls). Also drives runner.run_suite on the offline FakeWorld: a spoiled
situational chain vetoes all_green; a clean one stays green. Offline.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spoil_gate as SG  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def comp(name, verdict="PASS", **kw):
    d = {"name": name, "verdict": verdict, "execution": "completed", "detail": ""}
    d.update(kw)
    return d


def clean_chain(name="c1"):
    return {"name": name,
            "components": [comp("pit_digs"), comp("colonist_need_food_met"), comp("hauler_job_completes")],
            "modal_check": {"found_open": False, "dialogs": {"Dialog_NamePlayerFaction": 0}, "errors": []},
            "situational": {"bland": True, "companion": True, "surprises": [], "hits_seen": [],
                            "ticks_spent": 6000, "tps": 4.2,       # slow is not hung: low TPS is not a spoil
                            "runValidity": {"verdict": "CLEAN", "note": "CLEAN: no visitor observed", "visitors": [],
                                            "letters": [], "disruptions": [], "observationFailures": []}}}


def run(*chains, **kw):
    s = {"chains": list(chains)}
    s.update(kw)
    return s


def grade(s, situational=True):
    return SG.grade(s, situational=situational)


def row(g, name):
    return next(r for r in g["rows"] if r["row"].endswith("/" + name))


# ---------------------------------------------------------------- controls
g = grade(run(clean_chain(), clean_chain("c2"), checklist_state="VALIDATED"))
ok(g["overall"] == "GREEN" and not g["spoils"], "control: clean fully observed run (low TPS) grades GREEN", g)

ch = clean_chain()
ch["situational"]["runValidity"]["visitors"] = [{"id": "Thing_Megascarab1", "kind": "Megascarab",
                                                  "removed": True, "interferenceObserved": True}]
ch["situational"]["runValidity"]["note"] = "CLEAN with 1 visitor(s) recorded and removed"
g = grade(run(ch))
ok(g["overall"] == "GREEN", "control: a visitor whose interference WAS observed leaves the run GREEN", g)

# ---------------------------------------------------------------- spoil classes
def spoiled(label, s, cls, situational=True):
    g = grade(s, situational)
    ok(g["overall"] != "GREEN", "%s: overall is not GREEN (got %s)" % (label, g["overall"]), g)
    ok(cls in g["classes"], "%s: spoil class %s recorded" % (label, cls), g["classes"])
    return g


# 1 unknown blocking window: modal sweep errored / not recorded
ch = clean_chain()
ch["modal_check"] = {"found_open": False, "dialogs": {"Dialog_NamePlayerFaction": None},
                     "errors": ["Dialog_NamePlayerFaction: timeout"]}
g = spoiled("unknown blocking window (sweep errored)", run(ch, clean_chain("c2")), "unknown_blocking_window")
ok(row(g, "pit_digs")["grade"] == "INDETERMINATE", "unknown blocking window: its PASS rows are INDETERMINATE")
ok(all(r["grade"] == "PASS" for r in g["rows"] if r["row"].startswith("c2/")),
   "unknown blocking window: an unaffected chain keeps PASS rows")
ch = clean_chain()
ch["modal_check"] = None
spoiled("unknown blocking window (no modal check)", run(ch), "unknown_blocking_window")
ch = clean_chain()
ch["modal_check"] = {"found_open": True, "dialogs": {"Dialog_NamePlayerFaction": 1}, "errors": []}
spoiled("known open blocking window", run(ch), "blocking_window_open")

# 2 visitor-sensitive gap: a visitor removed, its need/mood/job interference unseen
ch = clean_chain()
ch["situational"]["runValidity"].update(
    visitors=[{"id": "Thing_Boomalope7", "kind": "Boomalope", "removed": True}],
    note="CLEAN with 1 visitor(s) recorded and removed, no evidence of disruption (origin unknown)")
g = spoiled("visitor-sensitive gap", run(ch), "visitor_gap")
ok(g["overall"] == "INDETERMINATE", "visitor gap: overall INDETERMINATE", g["overall"])
ok(row(g, "colonist_need_food_met")["grade"] == "INDETERMINATE", "visitor gap: need row INDETERMINATE")
ok(row(g, "hauler_job_completes")["grade"] == "INDETERMINATE", "visitor gap: job row INDETERMINATE")
r = row(g, "pit_digs")
ok(r["grade"] == "PASS" and any(n.startswith("clean-with-note") for n in r["notes"]),
   "visitor gap: an other-class row stays PASS with a note (owner card 2026-10-24)", r)
ch = clean_chain()
ch["components"] = [comp("colonist_wellbeing", criterion_class="mood")]
ch["situational"]["runValidity"].update(verdict="INDETERMINATE",
                                        observationFailures=[{"source": "list_pawns", "why": "truncated"}])
g = spoiled("visitor gap (observation failure, declared mood class)", run(ch), "visitor_gap")
ok(row(g, "colonist_wellbeing")["grade"] == "INDETERMINATE", "declared criterion_class=mood is honoured")
ch = clean_chain()
ch["components"] = [comp("pit_digs")]
ch["situational"]["runValidity"]["letters"] = [{"detector": "raid_arrived", "summary": "raid letter", "tick": 5}]
g = grade(run(ch))
ok(g["overall"] == "GREEN" and "visitor_gap" not in g["classes"],
   "visitor gap with no need/mood/job row: clean-with-note, still GREEN", g)
ch = clean_chain()
ch["situational"]["runValidity"].update(verdict="DISRUPTED", note="DISRUPTED: Thing_Wolf attacked Pawn_A",
                                        disruptions=[{"kind": "attacked", "visitor": "Thing_Wolf", "subject": "A"}])
ch["components"][0]["verdict"] = "FAIL"
g = spoiled("disrupted run", run(ch), "disrupted")
ok(g["overall"] == "UNMEASURED" and all(r["grade"] == "UNMEASURED" for r in g["rows"]),
   "disrupted run: every row UNMEASURED (its FAIL included), overall UNMEASURED", g)

# 3 empty rows
ch = clean_chain()
ch["components"] = []
g = spoiled("empty chain", run(ch, clean_chain("c2")), "empty_rows")
ok(g["overall"] == "UNMEASURED", "empty chain: overall UNMEASURED", g["overall"])
ch = clean_chain()
ch["components"][0]["verdict"] = ""
spoiled("empty verdict row", run(ch), "empty_rows")
spoiled("run with no chains", run(), "empty_rows")
ch = clean_chain()
for c in ch["components"]:
    c["execution"] = "not_run"
spoiled("chain whose rows are all not_run", run(ch, clean_chain("c2")), "empty_rows")

# 4 DRAFT status
ch = clean_chain()
ch["components"][0]["verdict"] = "PASS(DRAFT)"
g = spoiled("DRAFT verdict row", run(ch), "draft_status")
ok(row(g, "pit_digs")["grade"] == "INDETERMINATE", "DRAFT verdict: row INDETERMINATE although it starts PASS")
spoiled("DRAFT checklist", run(clean_chain(), checklist_state="DRAFT"), "draft_status")

# 5 capped list
ch = clean_chain()
ch["situational"]["hits_seen"] = [{"tick": 9, "detector": "listing_truncated", "severity": "WARN",
                                   "summary": "list_things listing is truncated (beyond the limit of 100)"}]
spoiled("capped listing", run(ch), "capped_list")
ch = clean_chain()
ch["situational"]["hits_seen"] = [{"tick": i, "detector": "wildlife_near_colonist", "severity": "INFO",
                                   "summary": "x"} for i in range(SG.HITS_CAP)]
spoiled("hits_seen at its own cap", run(ch), "capped_list")

# 6 log blindness
ch = clean_chain()
ch["situational"]["companion"] = False
g = spoiled("companion detectors off", run(ch), "log_blind")
ok(all(r["grade"] == "INDETERMINATE" for r in g["rows"]), "log blind: every PASS row INDETERMINATE")
spoiled("Verse.Log cap (log_alive false)", run(clean_chain(), log_alive=False), "log_blind")

# envelope off: no situational envelope => blocking window and visitors unobserved
ch = clean_chain()
ch["modal_check"], ch["situational"] = None, None
spoiled("non-situational run", run(ch), "envelope_off", situational=False)

# GPT review 2026-11-02 (D:\\ClaudeWork\\rimmandrake\\relentless\\spoil_gate_gpt_review.md): each finding is a case
ch = clean_chain()
ch["components"].append(comp("later_row", "NOT_RUN", execution="not_run"))
spoiled("GPT1 mixed executed/not-run rows", run(ch), "partial_run")
for label, sit in (("situational None", None), ("runValidity None", "rv")):
    ch = clean_chain()
    if sit is None:
        ch["situational"] = None
    else:
        ch["situational"]["runValidity"] = None
    g = spoiled("GPT2 %s on a situational chain" % label, run(ch), "visitor_gap")
    ok(row(g, "colonist_need_food_met")["grade"] == "INDETERMINATE", "GPT2 %s: need row INDETERMINATE" % label)
for label, mc in (("empty dict", {}), ("dialogs None", {"found_open": False, "dialogs": None, "errors": []}),
                  ("dialogs list", {"found_open": False, "dialogs": ["x"], "errors": []})):
    ch = clean_chain()
    ch["modal_check"] = mc
    spoiled("GPT3 modal check %s" % label, run(ch), "unknown_blocking_window")
crashy = [run(None), run(clean_chain(), components=None)]
ch = clean_chain(); ch["components"].append(None); crashy.append(run(ch))
ch = clean_chain(); ch["situational"]["hits_seen"] = [None]; crashy.append(run(ch))
ch = clean_chain(); ch["situational"]["runValidity"]["visitors"] = [None]; crashy.append(run(ch))
ch = clean_chain(); ch["modal_check"]["errors"] = [None, 3]; crashy.append(run(ch))
for i, s in enumerate(crashy):
    try:
        gi = grade(s)
        okc = True
    except Exception as e:      # noqa: BLE001
        gi, okc = repr(e), False
    ok(okc, "GPT5 malformed shape %d grades without raising" % i, gi)
ok(grade(crashy[0])["overall"] != "GREEN", "GPT5 a None chain record is not GREEN")
spoiled("GPT6 checklist_state present but None", run(clean_chain(), checklist_state=None), "draft_status")
spoiled("GPT7 situational=False on a fully recorded chain", run(clean_chain()), "envelope_off", situational=False)

# FAIL beats everything; a spoil never turns a FAIL into a PASS
ch = clean_chain()
ch["components"][0]["verdict"] = "FAIL"
ch["situational"]["companion"] = False
ok(grade(run(ch))["overall"] == "RED", "a FAIL row in a spoiled (non-disrupted) run stays RED")

# fixtures are not mutated by grading
base = clean_chain()
snap = copy.deepcopy(base)
grade(run(base))
ok(base == snap, "grade() does not mutate its input")

# ---------------------------------------------------------------- runner wiring
src = open(os.path.join(HERE, "runner.py"), encoding="utf-8").read()
ok("spoil_gate" in src and '"acceptance": acceptance' in src, "runner.py records the spoil grade as summary['acceptance']")


# ---------------------------------------------------------------- runner veto, end to end (blind check 4d4b1155: GAP)
# run_suite on the offline FakeWorld: every component PASSes, so all_green is True before the veto; a spoiled
# situational chain (the modal sweep errored = unknown blocking window) must still read all_green False with a
# non-GREEN summary['acceptance']; the same suite on a clean sweep stays all_green True and GREEN (control).
import shutil  # noqa: E402
import tempfile  # noqa: E402
import runner  # noqa: E402
import run_identity  # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row  # noqa: E402
from suite import Suite  # noqa: E402

_tmp = tempfile.mkdtemp(prefix="spoil_gate_runner_")
_orig = (runner.SHEET_DIR, runner.FIXTURE_LEDGER, run_identity.modal_sweep)
runner.SHEET_DIR = _tmp
runner.FIXTURE_LEDGER = os.path.join(_tmp, "fixtures.json")   # never rewrite the tracked fixture ledger


def _world():
    w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103), pawn_row("Col3", x=106)])
    w.shot_dir = _tmp
    return w


def _suite():
    st = Suite("SpoilVeto")

    @st.chain("c1")
    def _c1(t):
        with t.component("quiet wait"):
            t.wait_ticks(1200)
    return st


try:
    clean = runner.run_suite(_suite(), _world(), anchor=(100, 100), situational=True)
    ok(clean["all_green"] is True, "runner control: clean situational run_suite stays all_green",
       (clean["all_green"], clean.get("acceptance", {}).get("overall")))
    ok(clean.get("acceptance", {}).get("overall") == SG.GREEN, "runner control: clean run's summary acceptance is GREEN",
       clean.get("acceptance"))

    def _blind_sweep(call, *a, **k):
        return {"found_open": False, "dialogs": {"Dialog_MessageBox": None}, "errors": ["Dialog_MessageBox: bridge timeout"]}
    run_identity.modal_sweep = _blind_sweep
    bad = runner.run_suite(_suite(), _world(), anchor=(100, 100), situational=True)
    verdicts = [c["verdict"] for ch in bad["chains"] for c in ch["components"]]
    ok(verdicts and all(v == "PASS" for v in verdicts), "runner spoiled: every component PASSed (veto is the only red)",
       verdicts)
    ok(bad.get("acceptance", {}).get("overall") not in (None, SG.GREEN),
       "runner spoiled: summary acceptance is non-GREEN", bad.get("acceptance", {}).get("overall"))
    ok(bad["all_green"] is False, "runner spoiled: all_green vetoed to False by the spoil gate", bad["all_green"])
    ok(bad.get("fresh_green") is not True, "runner spoiled: fresh_green is not True", bad.get("fresh_green"))
finally:
    runner.SHEET_DIR, runner.FIXTURE_LEDGER, run_identity.modal_sweep = _orig
    shutil.rmtree(_tmp, ignore_errors=True)

print("RESULT %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
