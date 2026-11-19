#!/usr/bin/env python3
"""Offline selftest: the north-star frame judge writes refusal-contract records (RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_
NORTHSTAR_FRAME_FAILS). standing_rulings.md §A refusal carries its path to pass binds every judge, and
scene_look_judge_brief.md asks a contract record for every bar it refuses or could not see. A MOCK judge, no network,
no `claude`; `submit` is a fake that keeps what it was handed. Proves:
  R1  one bar NO, one UNJUDGEABLE, one YES -> one verdict submitted, exactly two refusal records (none for the YES, which
      is passed), and refusal_contract.check finds it well formed against its `given` (bar texts, judged captures)
  R2  the record fields are asked of a fresh follow-up call only for NO / UNJUDGEABLE: a YES costs no extra call
  R3  each record: clause = bar id, criterion_hash of the bar text, evidence = the judged capture, observed = the
      judge's why; an UNJUDGEABLE record's fix is a re-shot capture (cost rerun)
  R4  a follow-up that could not run: its bar is not recorded ("could not record", with the cause), never a malformed
      record and never a pass, and the run submits nothing (a refusal without its record is no verdict)
  R5  a judge call that died (UNJUDGEABLE "judge could not run"), a split vote, a claim with no image: no record
      (could not look), named as such
  R6  all bars YES -> an all-pass verdict is submitted (no refusal records)
  R7  no record runner -> nothing is submitted, recorded as not run with why; bar statuses are the same either way
Run: python3 src/RimMandrake/Utils/northstar_driver/selftest_judge_refusal_records.py
"""
import atexit
import copy
import json
import os
import shutil
import sys
import tempfile

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_judge_refusal_records_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
os.environ["RM_REFUSAL_DIR"] = os.path.join(tempfile.tempdir, "refusals")   # never the real store

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_REPO, "src", "RimMandrake", "rimflow"))
from northstar_driver import PASS, FAIL, UNMEASURED      # noqa: E402
from northstar_driver import judge_cli as J              # noqa: E402
import refusal_contract as RC                           # noqa: E402

FAILS = []
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
       b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
       b"\x00\x00\x00\x00IEND\xaeB`\x82")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:600]))
    if not cond:
        FAILS.append(name)


def env(obj):
    return json.dumps({"type": "result", "is_error": False, "modelUsage": {"mock-judge-1": {}}, "result": json.dumps(obj)})


FIX = {"would_pass": "the north ladder rails reach the water line in front of the pit wall in a crop at zoom 1",
       "smallest_fix": {"what": "draw the ladder graphic above the pit wall layer at full water level",
                        "attainable": "yes", "cost": "edit"},
       "criterion_verdict": "sound",
       "criterion_why": "A player expects to see a ladder reach the water, and one capture can show it."}
RESHOOT = dict(FIX, smallest_fix={"what": "re-shoot the capture at zoom 1 centred on the pit's north wall",
                                  "attainable": "yes", "cost": "rerun"})


class Bar(object):
    """Pass 2: verdicts by image basename."""

    def __init__(self, verdicts):
        self.verdicts, self.prompts = verdicts, []

    def __call__(self, prompt_for, image):
        p = prompt_for(image)
        self.prompts.append(p)
        v = self.verdicts[os.path.basename(image)]
        if isinstance(v, list):      # one reply per call, in order (a repeated vote)
            v = v.pop(0)
        if v == "DEAD":
            return False, "claude -p exited 1"
        if v == "ERRENV":
            return True, json.dumps({"type": "result", "is_error": True, "result": "permission denied"})
        why = {"YES": "the rails reach the water", "UNJUDGEABLE": "a menu covers the north wall"}.get(
            v, "the north ladder rail stops at the wall rim above the water")
        return True, env({"verdict": v, "why": why})


class Record(object):
    """The follow-up: record fields by image basename ("DEAD" = could not run)."""

    def __init__(self, answers):
        self.answers, self.prompts = answers, []

    def __call__(self, prompt_for, image):
        p = prompt_for(image)
        self.prompts.append((os.path.basename(image), p))
        a = self.answers.get(os.path.basename(image), FIX)
        if a == "DEAD":
            return False, "claude -p timed out after 180s"
        return True, env(a)


def make_doc(d, names=("no.png", "unj.png", "yes.png"), polarity="must"):
    comps, texts = [], {}
    for n in names:
        p = os.path.join(d, n)
        with open(p, "wb") as f:
            f.write(PNG)
        b = "bar_" + n.split(".")[0]
        comps.append({"name": "pit_" + b, "chain": "x", "shows": [b], "screenshots": [p]})
        texts[b] = {"text": "the north ladder of %s is drawn in front of the pit wall, down to the water" % b,
                    "polarity": polarity}
    bars = [{"id": b, "visual": True, "status": PASS, "evidence": "state ok"} for b in texts]
    return {"mod": "Mock", "item": "MOCK_ITEM", "components": comps, "bar_text": texts, "bars": bars, "expected": None}


def run(doc, verdicts, rec_runner, sink, **kw):
    def submit(verdict, given=None):
        sink.append((copy.deepcopy(verdict), copy.deepcopy(given)))
        return {"ok": True, "counted": False, "advisory": True, "pointer": "refusals.jsonl:%d" % len(sink)}
    return J.judge_doc(doc, Bar(verdicts), jobs=1, log=lambda m: None, record_runner=rec_runner, submit=submit, **kw)


def main():
    d = tempfile.mkdtemp()
    V = {"no.png": "NO", "unj.png": "UNJUDGEABLE", "yes.png": "YES"}

    sink, rr = [], Record({"unj.png": RESHOOT})
    try:
        doc = run(make_doc(d), V, rr, sink)
    except TypeError as e:
        check("R1 judge_doc takes a record runner and a submit", False, e)
        return finish()
    check("R1 one verdict submitted", len(sink) == 1, len(sink))
    if not sink:
        return finish()
    v, g = sink[0]
    refs = v.get("refusals") or []
    check("R1 exactly two refusal records, for the NO and the UNJUDGEABLE bar",
          sorted(r.get("clause") for r in refs) == ["bar_no", "bar_unj"], [r.get("clause") for r in refs])
    check("R1 the YES bar is passed, with its capture as evidence",
          [p.get("clause") for p in v.get("passed") or []] == ["bar_yes"]
          and (v["passed"][0].get("evidence") or [""])[0].endswith("yes.png"), v.get("passed"))
    errs = RC.check(v, g)
    check("R1 refusal_contract.check finds the submitted verdict well formed", errs == [], errs)
    check("R1 family scene_look_judge_brief, the item and a sha", v.get("family") == "scene_look_judge_brief"
          and v.get("item") == "MOCK_ITEM" and v.get("sha"), (v.get("family"), v.get("item"), v.get("sha")))
    check("R2 the follow-up asked only for the NO and the UNJUDGEABLE bars",
          sorted(n for n, _p in rr.prompts) == ["no.png", "unj.png"], [n for n, _p in rr.prompts])
    check("R2 the follow-up prompt carries the bar and the judge's reason, not the expected answer",
          all("down to the water" in p and ("stops at the wall rim" if n == "no.png" else "a menu covers") in p
              for n, p in rr.prompts),
          [p[:200] for _n, p in rr.prompts])
    by = {r["clause"]: r for r in refs}
    no = by.get("bar_no") or {}
    check("R3 clause, criterion_hash, evidence and observed",
          no.get("criterion_hash") == RC.criterion_hash(doc["bar_text"]["bar_no"]["text"])
          and no.get("evidence") and no["evidence"][0].endswith("no.png")
          and "stops at the wall rim" in str(no.get("observed")), no)
    check("R3 an UNJUDGEABLE record's fix is a re-shot capture (cost rerun)",
          ((by.get("bar_unj") or {}).get("smallest_fix") or {}).get("cost") == "rerun", by.get("bar_unj"))
    statuses = {r["id"]: r["status"] for r in doc["bars"]}
    check("R3 bar statuses are pass 2's, unchanged", statuses == {"bar_no": FAIL, "bar_unj": UNMEASURED,
                                                                 "bar_yes": PASS}, statuses)
    rec = (doc.get("judge") or {}).get("contract") or {}
    check("R3 the submit result is kept on the judge record", rec.get("submitted") is True
          and rec.get("pointer") == "refusals.jsonl:1", rec)

    sink = []
    doc = run(make_doc(d), V, Record({"unj.png": "DEAD"}), sink)
    rec = doc["judge"]["contract"]
    check("R4 a dead follow-up: nothing is submitted (a refusal without its record is no verdict)",
          not sink and rec.get("submitted") is False and "incomplete" in rec.get("why", ""), (sink, rec))
    check("R4 ... and it is named could not record, with the cause",
          any(c.get("clause") == "bar_unj" and "timed out" in c.get("cause", "") for c in rec.get("could_not_record") or []),
          rec)
    sink = []
    doc = run(make_doc(d, ("no.png", "yes.png")), V, Record({"no.png": "DEAD"}), sink)
    check("R4 a NO whose follow-up died next to a YES is never submitted as an all-pass", not sink, sink)
    check("R4 the follow-up's raw reply is kept on the record", all(
        "raw" in f and "ok" in f for f in doc["judge"]["contract"].get("followups") or [None]),
        doc["judge"]["contract"].get("followups"))
    sink = []
    doc = run(make_doc(d), V, Record({"no.png": dict(FIX, would_pass="it does not pass")}), sink)
    rec = doc["judge"]["contract"]
    check("R4 a follow-up whose answer the contract refuses is submitted as given (the contract refuses it, not us)",
          len(sink) == 1 and any("would_pass" in e for e in RC.check(*sink[0])), sink and RC.check(*sink[0]))

    sink = []
    doc = run(make_doc(d), dict(V, **{"unj.png": "DEAD"}), Record({}), sink)
    rec = doc["judge"]["contract"]
    v = sink[0][0] if sink else {}
    check("R5 a dead judge call is no record: could not look, named",
          [r["clause"] for r in v.get("refusals") or []] == ["bar_no"]
          and any(c.get("clause") == "bar_unj" for c in rec.get("could_not_look") or []), (v.get("refusals"), rec))
    doc0 = make_doc(d)
    doc0["components"][2]["screenshots"] = []
    sink = []
    doc = run(doc0, V, Record({}), sink)
    check("R5 a claim with no image is no record: could not look",
          any(c.get("clause") == "bar_yes" for c in doc["judge"]["contract"].get("could_not_look") or [])
          and "bar_yes" not in [p.get("clause") for p in (sink[0][0].get("passed") if sink else [])],
          doc["judge"]["contract"])

    sink, rr = [], Record({})
    doc = run(make_doc(d), {"no.png": "YES", "unj.png": "YES", "yes.png": "YES"}, rr, sink)
    check("R6 all YES: an all-pass verdict submitted, no follow-up call",
          len(sink) == 1 and sink[0][0].get("refusals") == [] and len(sink[0][0].get("passed")) == 3
          and not rr.prompts and RC.check(*sink[0]) == [], sink)

    sink, rr = [], Record({})
    doc = run(make_doc(d, ("no.png", "yes.png")), {"no.png": ["YES", "NO", "YES"], "yes.png": ["YES"] * 3}, rr, sink,
              repeat_must=3)
    check("R5 a split vote (YES, NO, YES) is no record and no pass: could not look, no follow-up",
          not rr.prompts and sink and [p["clause"] for p in sink[0][0]["passed"]] == ["bar_yes"]
          and {r["id"]: r["status"] for r in doc["bars"]}.get("bar_no") == UNMEASURED
          and not sink[0][0]["refusals"]
          and any(c.get("clause") == "bar_no" for c in doc["judge"]["contract"].get("could_not_look") or []),
          (rr.prompts, sink, doc["judge"]["contract"]))
    sink, rr = [], Record({})
    doc = run(make_doc(d, ("no.png",)), {"no.png": "ERRENV"}, rr, sink)
    check("R5 an error envelope from a process that exited 0 is could not look, never a refusal",
          not rr.prompts and not (sink and sink[0][0].get("refusals"))
          and any(c.get("clause") == "bar_no" for c in doc["judge"]["contract"].get("could_not_look") or []),
          (rr.prompts, sink, doc["judge"]["contract"]))
    doc0 = make_doc(d, ("no.png", "unj.png"))
    doc0["components"][1]["shows"] = ["bar_no"]      # two captures of one bar: one NO, one whose judge died
    sink = []
    doc = run(doc0, {"no.png": "NO", "unj.png": "DEAD"}, Record({}), sink)
    check("R5 a bar refused on one capture still names the other capture that could not look",
          [r["clause"] for r in (sink[0][0]["refusals"] if sink else [])] == ["bar_no"]
          and any(c.get("component") == "pit_bar_unj" for c in doc["judge"]["contract"].get("could_not_look") or []),
          doc["judge"]["contract"].get("could_not_look"))
    sink, rr = [], Record({})
    doc = run(make_doc(d, ("unj.png",)), {"unj.png": ["YES", "UNJUDGEABLE", "YES"]}, rr, sink, repeat_must=3)
    v = sink[0][0] if sink else {}
    check("R2 an UNJUDGEABLE among YES votes: the record and its follow-up cite the UNJUDGEABLE reason, never a YES",
          rr.prompts and "a menu covers" in rr.prompts[0][1] and "rails reach the water" not in rr.prompts[0][1]
          and v.get("refusals") and "a menu covers" in v["refusals"][0]["observed"]
          and "rails reach" not in v["refusals"][0]["observed"], (rr.prompts, v))
    sink, rr = [], Record({})
    doc = run(make_doc(d, ("no.png",), polarity="cannot"), {"no.png": ["YES"] * 3}, rr, sink)
    check("R2 a cannot-show bar answered YES: the follow-up is told a passing capture shows the defect ABSENT",
          rr.prompts and "NOT true" in rr.prompts[0][1] and sink and sink[0][0]["refusals"], (rr.prompts, sink))
    saved = J._counters_for
    J._counters_for = lambda item: (1, {"bar_no": 1})
    try:
        sink = []
        run(make_doc(d), V, Record({"unj.png": RESHOOT}), sink)
    finally:
        J._counters_for = saved
    ns = {r["clause"]: r.get("new_since") for r in (sink[0][0]["refusals"] if sink else [])}
    check("R3 after a counted refusal: a clause refused before is unfixed, a new one is late (no change is claimed)",
          ns == {"bar_no": "unfixed:bar_no", "bar_unj": "late"}, ns)
    d2 = tempfile.mkdtemp()
    shas = []
    for first, second in ((PNG, PNG + b"\0"), (PNG + b"\0", PNG)):   # the two captures swap contents, paths kept
        doc2 = make_doc(d2, ("a.png", "b.png"))
        for n, body in (("a.png", first), ("b.png", second)):
            with open(os.path.join(d2, n), "wb") as f:
                f.write(body)
        shas.append(run(doc2, {"a.png": "NO", "b.png": "NO"}, Record({}), [])["judge"]["contract"].get("sha"))
    check("R3 the verdict sha follows which content is at which capture (a swap is a new sha)",
          all(shas) and shas[0] != shas[1], shas)

    sink = []
    a = run(make_doc(d), V, None, sink)
    check("R7 no record runner: nothing submitted, recorded as not run",
          not sink and str((a["judge"].get("contract") or {}).get("status", "")).startswith("not run"),
          a["judge"].get("contract"))
    check("R7 bar statuses are the same without records", {r["id"]: r["status"] for r in a["bars"]} == statuses)
    return finish()


def finish():
    print("selftest_judge_refusal_records: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
