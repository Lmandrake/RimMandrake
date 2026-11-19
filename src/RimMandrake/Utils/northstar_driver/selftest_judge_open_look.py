#!/usr/bin/env python3
"""Offline selftest: judge_cli.py runs the scene-look brief's two passes (RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK).

design/RimMandrake/scene_look_judge_brief.md: pass 1 is ONE fresh judge per capture with the open question and no
checklist; pass 2 is a DIFFERENT judge with one expectation sentence, here the must-show bar's text (judge.py's statement
prompt, unchanged). A MOCK judge, no network, no `claude`. Proves:
  O1  pass 1 runs once per distinct capture, before pass 2, and its prompt names no bar id and no bar text (bar-blind)
  O2  pass 2's prompt never carries pass 1's answer
  O3  a pass-1 ODD or WRONG is a doubt on every bar row judged on that capture; the row's status is pass 2's, unchanged
  O4  pass-1 COULD NOT SEE, an unreadable answer and a judge that could not run are "could not look" (counted, with the
      cause), never a doubt and never a verdict
  O5  the record carries pass 1's prompt sha256, every look whole, and the doubt and could-not-look counts
  O6  with no open runner (the old API) no pass-1 call, open_look says why, and every bar verdict is the same as with it
  O7  pass 2's NO, UNJUDGEABLE and a state FAIL keep their statuses beside a pass-1 WRONG doubt
  O8  parsing: an error envelope (even holding a look) and a truncated final answer after an earlier example are
      could-not-look; a final object with braces inside its strings is read whole
  O9  a rerun keeps the earlier doubts (merged, never erased) and the earlier open-look record
  O10 a runner that raises is could-not-look with its cause (pass 2 still runs); a truncated image is refused before any
      call; the judged file's pixel size is recorded
Run: python3 src/RimMandrake/Utils/northstar_driver/selftest_judge_open_look.py
"""
import atexit
import json
import os
import shutil
import sys
import tempfile

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_judge_open_look_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from northstar_driver import PASS, FAIL, UNMEASURED      # noqa: E402
from northstar_driver import judge_cli as J              # noqa: E402

FAILS = []
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
       b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
       b"\x00\x00\x00\x00IEND\xaeB`\x82")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def env(obj):
    return json.dumps({"type": "result", "is_error": False, "modelUsage": {"mock-judge-1": {}}, "result": json.dumps(obj)})


class Bar(object):
    """Pass 2: YES for every bar."""

    def __init__(self):
        self.prompts = []

    def __call__(self, prompt_for, image):
        p = prompt_for(image)
        self.prompts.append(p)
        return True, env({"verdict": "YES", "why": "shown"})


class Open(object):
    """Pass 1: script {image basename: reply}; a reply is a dict (the answer), "ERROR" or "GARBAGE"."""

    def __init__(self, script, order):
        self.script, self.order, self.prompts = script, order, []

    def __call__(self, prompt_for, image):
        p = prompt_for(image)
        self.prompts.append(p)
        self.order.append(("open", os.path.basename(image)))
        r = self.script.get(os.path.basename(image), {"look": "EXPECTED", "where": "", "first_noticed": "nothing odd"})
        if r == "ERROR":
            return False, "claude -p exited 1"
        if r == "GARBAGE":
            return True, json.dumps({"type": "result", "is_error": False, "result": "I think it looks fine overall."})
        return True, env(r)


def make_doc(d):
    shots = {}
    for n in ("a.png", "b.png", "c.png", "d.png", "e.png"):
        p = os.path.join(d, n)
        with open(p, "wb") as f:
            f.write(PNG)
        shots[n] = p
    comps = [
        {"name": "pitA", "chain": "x", "shows": ["bar_ladder", "bar_water"], "screenshots": [shots["a.png"]]},
        {"name": "pitB", "chain": "x", "shows": ["bar_ladder"], "screenshots": [shots["b.png"]]},
        {"name": "pitC", "chain": "x", "shows": ["bar_rim"], "screenshots": [shots["c.png"]]},
        {"name": "pitD", "chain": "x", "shows": ["bar_d"], "screenshots": [shots["d.png"]]},
        {"name": "pitE", "chain": "x", "shows": ["bar_e"], "screenshots": [shots["e.png"]]},
    ]
    texts = {b: {"text": "THE BAR TEXT OF %s: the ladder is drawn in front of the wall" % b, "polarity": "must"}
             for b in ("bar_ladder", "bar_water", "bar_rim", "bar_d", "bar_e")}
    bars = [{"id": b, "visual": True, "status": PASS, "evidence": "state ok"} for b in texts]
    return {"mod": "Mock", "components": comps, "bar_text": texts, "bars": bars, "expected": None}


def main():
    d = tempfile.mkdtemp()
    order = []
    script = {"a.png": {"look": "ODD", "where": "north ladder", "first_noticed": "the ladder stops at the rim"},
              "b.png": {"look": "EXPECTED", "where": "", "first_noticed": "nothing"},
              "c.png": {"look": "COULD NOT SEE", "where": "", "first_noticed": "too zoomed out"},
              "d.png": "GARBAGE", "e.png": "ERROR"}
    op = Open(script, order)
    bar = Bar()

    def bar_runner(prompt_for, image):
        order.append(("bar", os.path.basename(image)))
        return bar(prompt_for, image)
    doc = J.judge_doc(make_doc(d), bar_runner, open_runner=op, jobs=1, backoff_s=0, log=lambda s: None)
    rows = {r["id"]: r for r in doc["bars"]}
    ol = doc["judge"].get("open_look") or {}

    opens = [o for o in order if o[0] == "open"]
    first_bar = next((i for i, o in enumerate(order) if o[0] == "bar"), len(order))
    check("O1 once per capture", sorted(x[1] for x in opens) == ["a.png", "b.png", "c.png", "d.png", "e.png"], opens)
    check("O1 before pass 2", all(i < first_bar for i, o in enumerate(order) if o[0] == "open"), order)
    check("O1 bar-blind", op.prompts and all("bar_" not in p and "THE BAR TEXT" not in p and "ladder is drawn" not in p
                                             for p in op.prompts), op.prompts[:1])
    check("O1 the brief's open question", op.prompts and all("Does anything look odd?" in p for p in op.prompts), op.prompts[:1])
    check("O2 pass 2 never sees pass 1", bar.prompts and all("the ladder stops at the rim" not in p and "ODD" not in p for p in bar.prompts))
    la, lw, lb = rows["bar_ladder"], rows["bar_water"], rows["bar_rim"]
    check("O3 doubt on every bar of the odd capture", any("pitA" in x for x in la.get("doubts", [])) and any("pitA" in x for x in lw.get("doubts", []))
          and "pass-1 doubt" in la["evidence"], (la, lw))
    check("O3 status is pass 2's, unchanged", la["status"] == PASS and lw["status"] == PASS and rows["bar_e"]["status"] == PASS,
          [r["status"] for r in rows.values()])
    check("O3 no doubt from an EXPECTED capture", not any("pitB" in x for x in la.get("doubts", [])), la.get("doubts"))
    looks = {os.path.basename(x["image"]): x for x in ol.get("looks", [])}
    check("O4 could-not-see is could-not-look, not a doubt",
          looks.get("c.png", {}).get("outcome") == "could_not_look" and not lb.get("doubts"), looks.get("c.png"))
    check("O4 unreadable answer is could-not-look with its cause",
          looks.get("d.png", {}).get("outcome") == "could_not_look" and "unreadable" in looks.get("d.png", {}).get("cause", ""), looks.get("d.png"))
    check("O4 a judge that could not run is could-not-look",
          looks.get("e.png", {}).get("outcome") == "could_not_look" and "could not run" in looks.get("e.png", {}).get("cause", ""), looks.get("e.png"))
    check("O5 counts", ol.get("doubts") == 1 and ol.get("could_not_look") == 3 and ol.get("expected") == 1, ol)
    check("O5 prompt sha and whole looks", ol.get("prompt_sha256") == J.OPEN_PROMPT_SHA256 and len(J.OPEN_PROMPT_SHA256) == 64
          and all("raw" in x and "image_sha256" in x for x in ol.get("looks", [])), list(ol))

    order2 = []
    doc2 = J.judge_doc(make_doc(tempfile.mkdtemp()), lambda pf, im: (order2.append(im), Bar()(pf, im))[1], jobs=1, backoff_s=0, log=lambda s: None)
    check("O6 no open runner: no pass-1 call, the record says why",
          len(order2) == 6 and "not run" in str((doc2["judge"].get("open_look") or {}).get("status")) and not any(r.get("doubts") for r in doc2["bars"]),
          (len(order2), doc2["judge"].get("open_look")))
    # O6 verdict equality: same doc, same pass-2 answers, with and without pass 1
    def verdicts(dd):
        return {r["id"]: r["status"] for r in dd["bars"]}
    v_open = verdicts(J.judge_doc(make_doc(tempfile.mkdtemp()), Bar(), open_runner=Open(script, []), jobs=1, backoff_s=0, log=lambda s: None))
    check("O6 same verdicts with and without pass 1", verdicts(doc2) == v_open, (verdicts(doc2), v_open))

    # O7: pass 2 NO / UNJUDGEABLE / state FAIL beside a WRONG doubt
    def bar_mixed(prompt_for, image):
        p = prompt_for(image)
        v = "NO" if "bar_ladder" in p else "UNJUDGEABLE" if "bar_water" in p else "YES"
        return True, env({"verdict": v, "why": "mock"})
    d7 = make_doc(tempfile.mkdtemp())
    for r in d7["bars"]:
        if r["id"] == "bar_rim":
            r["status"], r["evidence"] = FAIL, "state says no"
    wrong = {n: {"look": "WRONG", "where": "everything", "first_noticed": "x"} for n in ("a.png", "b.png", "c.png", "d.png", "e.png")}
    d7 = J.judge_doc(d7, bar_mixed, open_runner=Open(wrong, []), jobs=1, backoff_s=0, log=lambda s: None)
    r7 = {r["id"]: r for r in d7["bars"]}
    check("O7 NO stays FAIL, UNJUDGEABLE stays UNMEASURED, state FAIL stays FAIL, each with its doubt",
          r7["bar_ladder"]["status"] == FAIL and r7["bar_water"]["status"] == UNMEASURED and r7["bar_rim"]["status"] == FAIL
          and r7["bar_d"]["status"] == PASS and all(r7[b].get("doubts") for b in r7), {b: (r7[b]["status"], bool(r7[b].get("doubts"))) for b in r7})

    # O8 parsing
    err_env = json.dumps({"type": "result", "is_error": True, "result": 'API Error: 429 {"look": "EXPECTED"}'})
    trunc = json.dumps({"type": "result", "is_error": False, "result": 'e.g. {"look": "EXPECTED"} ... my answer: {"look": "WRO'})
    braces = json.dumps({"type": "result", "is_error": False, "result": 'Seen. {"look": "ODD", "where": "sign {A} by the rim", "first_noticed": "it"}'})
    nested = json.dumps({"type": "result", "is_error": False, "result": '{"answer":{"look":"EXPECTED"}'})
    pn = J.parse_open(nested)
    check("O8 an inner object of a broken outer answer is never the answer", pn[0] is None and pn[3], pn)
    pe, pt, pb = J.parse_open(err_env), J.parse_open(trunc), J.parse_open(braces)
    check("O8 error envelope is could-not-look even holding a look", pe[0] is None and "could not run" in pe[3], pe)
    check("O8 truncated final answer is never salvaged from an earlier example", pt[0] is None and pt[3], pt)
    check("O8 braces inside strings are read whole", pb[0] == "ODD" and pb[1] == "sign {A} by the rim", pb)

    # O9 rerun keeps doubts
    d9 = J.judge_doc(make_doc(tempfile.mkdtemp()), Bar(), open_runner=Open(script, []), jobs=1, backoff_s=0, log=lambda s: None)
    d9 = J.judge_doc(d9, Bar(), open_runner=Open({}, []), jobs=1, backoff_s=0, log=lambda s: None)   # second look: all EXPECTED
    r9 = {r["id"]: r for r in d9["bars"]}
    check("O9 a rerun keeps the earlier doubt and its evidence", any("pitA" in x for x in r9["bar_ladder"].get("doubts", []))
          and "pass-1 doubt" in r9["bar_ladder"]["evidence"], r9["bar_ladder"])
    check("O9 the earlier open-look record is kept", len(d9["judge"]["open_look"].get("earlier") or []) == 1, list(d9["judge"]["open_look"]))
    d9 = J.judge_doc(d9, Bar(), jobs=1, backoff_s=0, log=lambda s: None)                              # a run that skips pass 1
    d9 = J.judge_doc(d9, Bar(), open_runner=Open({}, []), jobs=1, backoff_s=0, log=lambda s: None)
    e9 = d9["judge"]["open_look"].get("earlier") or []
    check("O9 history survives ran -> skipped -> ran", len(e9) == 3 and any(x.get("doubts") == 1 for x in e9), [x.get("status") for x in e9])

    # O10 raising runner, truncated image, pixel size
    def boom(prompt_for, image):
        raise PermissionError("stage dir not writable")
    d10 = J.judge_doc(make_doc(tempfile.mkdtemp()), Bar(), open_runner=boom, jobs=1, backoff_s=0, log=lambda s: None)
    ol10 = d10["judge"]["open_look"]
    d10b = J.judge_doc(make_doc(tempfile.mkdtemp()), boom, open_runner=boom, jobs=1, backoff_s=0, log=lambda s: None)
    check("O10 a raising pass-2 runner is UNMEASURED (could not run), the run still completes",
          all(r["status"] == UNMEASURED and "could not run" in r["evidence"] for r in d10b["bars"]), [r["evidence"][:80] for r in d10b["bars"]])
    check("O10 a raising runner is could-not-look, pass 2 still runs", ol10.get("could_not_look") == 5 and
          all("PermissionError" in x["cause"] for x in ol10["looks"]) and all(r["status"] == PASS for r in d10["bars"]), ol10.get("looks", [{}])[0])
    tp = os.path.join(tempfile.mkdtemp(), "trunc.png")
    from PIL import Image
    Image.new("RGB", (64, 64), (200, 10, 10)).save(tp)
    data = open(tp, "rb").read()
    open(tp, "wb").write(data[:len(data) // 2])
    check("O10 a truncated image is refused before any call", J.image_problem(tp) is not None, J.image_problem(tp))
    check("O10 pixel size recorded", all(x.get("image_px") == [1, 1] for x in ol.get("looks", [])), [x.get("image_px") for x in ol.get("looks", [])])
    print("judge open look: %d failed" % len(FAILS) if FAILS else "judge open look: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
