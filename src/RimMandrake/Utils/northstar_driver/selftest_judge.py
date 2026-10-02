#!/usr/bin/env python3
"""Offline selftest for judge_cli.py -- a MOCK judge, no network, no `claude`.

Covers: unanimity on cannot-show (3 agreeing -> verdict; a split -> UNMEASURED), must-show
YES/NO -> PASS/FAIL with "judge:" evidence, throttle -> serial fallback that still lands the
verdict, unreadable / missing image -> UNMEASURED without the judge ever being asked, a state FAIL
staying FAIL, the __cell_rect crop preference, and cli.py recording screenshot paths on a mock run.
"""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

from northstar_driver import PASS, FAIL, UNMEASURED      # noqa: E402
from northstar_driver import judge_cli as J              # noqa: E402
from northstar_driver import cli                         # noqa: E402

FAILS = []
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
       b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
       b"\x00\x00\x00\x00IEND\xaeB`\x82")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail if not cond else ""))
    if not cond:
        FAILS.append(name)


def env(verdict, why="mock"):
    return json.dumps({"type": "result", "is_error": False, "modelUsage": {"mock-judge-1": {}},
                       "result": json.dumps({"verdict": verdict, "why": why})})


class Mock(object):
    """script: {(bar, image basename): [reply, reply, ...]} consumed in order; a reply is a verdict
    string, "THROTTLE", or "ERROR"."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.asked = []

    def __call__(self, prompt_for, image):
        prompt = prompt_for(image)
        bar = prompt.split("id:", 1)[1].split()[0]
        key = (bar, os.path.basename(image))
        self.asked.append(key)
        reply = self.script[key].pop(0) if self.script.get(key) else "YES"
        if reply == "THROTTLE":
            return False, "API Error: 429 rate_limit_error: too many requests"
        if reply == "ERROR":
            return False, "claude -p exited 1"
        return True, env(reply)


def doc_with(tmp):
    good = os.path.join(tmp, "good.png")
    open(good, "wb").write(PNG)
    full = os.path.join(tmp, "framed.png")
    open(full, "wb").write(PNG)
    open(os.path.join(tmp, "framed__cell_rect.png"), "wb").write(PNG)
    bad = os.path.join(tmp, "bad.png")
    open(bad, "wb").write(b"this is not an image")
    shot = lambda p: {"path": p, "win": cli.to_win(p), "wsl": p}        # noqa: E731
    comps = [
        {"chain": "c", "name": "must_ok", "shows": ["m_ok"], "screenshots": [shot(good)]},
        {"chain": "c", "name": "must_no", "shows": ["m_no"], "screenshots": [shot(full)]},
        {"chain": "c", "name": "cannot_unan", "shows": ["c_unan"], "screenshots": [shot(good)]},
        {"chain": "c", "name": "cannot_split", "shows": ["c_split"], "screenshots": [shot(good)]},
        {"chain": "c", "name": "unreadable", "shows": ["m_bad"], "screenshots": [shot(bad)]},
        {"chain": "c", "name": "missing", "shows": ["m_missing"],
         "screenshots": [shot(os.path.join(tmp, "nope.png"))]},
        {"chain": "c", "name": "noshot", "shows": ["m_noshot"], "screenshots": []},
        {"chain": "c", "name": "state_failed", "shows": ["m_statefail"], "screenshots": [shot(good)]},
        {"chain": "c", "name": "throttled", "shows": ["m_thr"], "screenshots": [shot(good)]},
    ]
    ids = ["m_ok", "m_no", "c_unan", "c_split", "m_bad", "m_missing", "m_noshot", "m_statefail", "m_thr"]
    texts = {i: {"polarity": "cannot" if i.startswith("c_") else "must", "text": "statement %s" % i}
             for i in ids}
    bars = [{"id": i, "status": UNMEASURED, "evidence": "x=PASS", "visual": True,
             "state_status": FAIL if i == "m_statefail" else PASS, "state_evidence": "x"} for i in ids]
    return {"mod": "T", "expected": ids, "bars": bars, "components": comps, "bar_text": texts}


def main():
    tmp = tempfile.mkdtemp(prefix="nsjudge_st_")
    doc = doc_with(tmp)
    m = Mock({("m_ok", "good.png"): ["YES"],
              ("m_no", "framed__cell_rect.png"): ["NO"],
              ("c_unan", "good.png"): ["NO", "NO", "NO"],
              ("c_split", "good.png"): ["NO", "YES", "NO"],
              ("m_statefail", "good.png"): ["YES"],
              ("m_thr", "good.png"): ["THROTTLE", "YES"]})
    log = []
    J.judge_doc(doc, m, jobs=4, backoff_s=0, log=log.append)
    st = {b["id"]: b["status"] for b in doc["bars"]}
    ev = {b["id"]: b["evidence"] for b in doc["bars"]}
    check("must YES -> PASS", st["m_ok"] == PASS, st["m_ok"])
    check("PASS evidence begins judge:", ev["m_ok"].startswith("judge:"), ev["m_ok"])
    check("must NO -> FAIL with judge: evidence", st["m_no"] == FAIL and ev["m_no"].startswith("judge:"), ev["m_no"])
    check("crop preferred over full frame", ("m_no", "framed__cell_rect.png") in m.asked, m.asked)
    check("cannot-show asked 3x", m.asked.count(("c_unan", "good.png")) == 3)
    check("cannot-show unanimous NO -> PASS", st["c_unan"] == PASS, ev["c_unan"])
    check("cannot-show split vote -> UNMEASURED", st["c_split"] == UNMEASURED and "split" in ev["c_split"], ev["c_split"])
    check("unreadable image -> UNMEASURED", st["m_bad"] == UNMEASURED, ev["m_bad"])
    check("unreadable image never sent to the judge", not any(k[0] == "m_bad" for k in m.asked))
    check("missing image -> UNMEASURED", st["m_missing"] == UNMEASURED and "does not exist" in ev["m_missing"], ev["m_missing"])
    check("no screenshot -> UNMEASURED", st["m_noshot"] == UNMEASURED, ev["m_noshot"])
    check("state FAIL stays FAIL despite judge YES", st["m_statefail"] == FAIL and ev["m_statefail"].startswith("state FAIL"))
    check("throttle -> serial fallback lands the verdict", st["m_thr"] == PASS, ev["m_thr"])
    check("fallback recorded", doc["judge"]["stats"]["fallback"] and doc["judge"]["stats"]["serial"] >= 1, doc["judge"]["stats"])
    check("judge provenance recorded", doc["judge"]["prompt_sha256"] == J.PROMPT_SHA256
          and doc["judge"]["models_reported"] == ["mock-judge-1"], doc["judge"].get("models_reported"))
    check("per-call raw replies retained",
          all(c["raw"] for cl in doc["judge"]["claims"] for c in cl["calls"]))
    check("not all_green with FAIL/UNMEASURED bars", doc["all_green"] is False)
    check("progress printed per call", sum(1 for line in log if line.startswith("judge ")) >= 10, len(log))

    # a throttle that persists -> UNMEASURED, never a verdict
    doc2 = doc_with(tempfile.mkdtemp(prefix="nsjudge_st2_"))
    doc2["components"] = [c for c in doc2["components"] if c["name"] == "throttled"]
    J.judge_doc(doc2, Mock({("m_thr", "good.png"): ["THROTTLE", "THROTTLE"]}), backoff_s=0, log=lambda s: None)
    r = [b for b in doc2["bars"] if b["id"] == "m_thr"][0]
    check("persistent throttle -> UNMEASURED", r["status"] == UNMEASURED and "throttled" in r["evidence"], r["evidence"])

    # all PASS -> GREEN, and re-judging a judged file is idempotent on state
    doc3 = doc_with(tempfile.mkdtemp(prefix="nsjudge_st3_"))
    keep = {"must_ok", "cannot_unan"}
    doc3["components"] = [c for c in doc3["components"] if c["name"] in keep]
    doc3["bars"] = [b for b in doc3["bars"] if b["id"] in ("m_ok", "c_unan")]
    doc3["expected"] = ["m_ok", "c_unan"]
    mk = lambda: Mock({("c_unan", "good.png"): ["NO", "NO", "NO"]})     # noqa: E731
    J.judge_doc(doc3, mk(), log=lambda s: None)
    check("every bar judged PASS -> all_green", doc3["all_green"] is True, doc3["summary"])
    J.judge_doc(doc3, mk(), log=lambda s: None)
    check("re-judge keeps state_status", all(b["state_status"] == PASS for b in doc3["bars"]) and doc3["all_green"])

    # error reply -> UNJUDGEABLE -> UNMEASURED
    doc4 = doc_with(tempfile.mkdtemp(prefix="nsjudge_st4_"))
    doc4["components"] = [c for c in doc4["components"] if c["name"] == "must_ok"]
    J.judge_doc(doc4, Mock({("m_ok", "good.png"): ["ERROR"]}), log=lambda s: None)
    r = [b for b in doc4["bars"] if b["id"] == "m_ok"][0]
    check("judge error -> UNMEASURED", r["status"] == UNMEASURED, r["evidence"])

    # path translation
    check("to_wsl", cli.to_wsl(r"C:\Users\M\Shots\a.png") == "/mnt/c/Users/M/Shots/a.png")
    check("to_win", cli.to_win("/mnt/d/Luke/x.png") == r"D:\Luke\x.png")

    # cli.py mock run records components + screenshots + bar_text, and holds visual bars UNMEASURED
    plan = os.path.join(cli.ROOT, "src", "RimMandrake", "Graffiti", "northstar_plan.py")
    if os.path.isfile(plan):
        from northstar_driver import bars as B
        B.REGISTRY.clear()
        out = os.path.join(tempfile.mkdtemp(), "g.json")
        cli.main(["run", "--mock", "--mod", "Graffiti", "--out", out, "--plan", plan])
        d = json.load(open(out))
        shots = [s for c in d.get("components", []) for s in c["screenshots"]]
        check("mock run: components recorded", len(d.get("components", [])) > 10, len(d.get("components", [])))
        check("mock run: screenshots carry path/win/wsl",
              bool(shots) and all({"path", "win", "wsl"} <= set(s) for s in shots), shots[:1])
        check("mock run: bar_text covers every expected bar",
              set(d["expected"]) <= set(d.get("bar_text", {})), d.get("bar_text_source"))
        check("mock run: no visual bar PASSes on state alone",
              all(b["status"] != PASS for b in d["bars"] if b.get("visual")),
              [(b["id"], b["status"]) for b in d["bars"]])
        check("mock run: not GREEN before judging", d["all_green"] is False)
    print("selftest_judge: %s (%d failure(s))" % ("FAILED" if FAILS else "all passed", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
