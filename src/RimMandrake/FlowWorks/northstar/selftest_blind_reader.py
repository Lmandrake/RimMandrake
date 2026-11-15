#!/usr/bin/env python3
"""selftest_blind_reader.py -- offline proof of northstar/blind_reader.py (LOOK_BLIND_READER), 0 ticks, no reader call.

Fake readers stand in for `claude -p`: a truthful one must PASS every bar; a habit reader (first option, 1..n order)
and a position reader (recovers the order on the foil too) must FAIL; a missing capture or an unparsable reply is
UNMEASURED, never PASS; the prompt carries no truth. Then each mutant of the scorer must turn a check red.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_blind_reader.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blind_reader as br  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
TABLE = os.path.join(ROOT, "design/concepts/FlowWorks/version/test_table.json")


def manifest(tmp):
    img = os.path.join(tmp, "cap.png")
    open(img, "wb").write(b"\x89PNG\r\n\x1a\n")
    m = {}
    for q in br.QUESTIONS:
        e = {"images": [img]}
        if q["kind"] == "order":
            e.update({"n": 5, "truth": [3, 1, 5, 2, 4]})
        elif q["kind"] == "label_each":
            e.update({"n": 4, "truth": ["water", "oil", "mud", "tar"]})
        m[q["id"]] = e
    return m


def answers(m, how):
    out = {}
    for q in br.QUESTIONS:
        t = m[q["id"]].get("truth")
        if how == "truth":
            if q["kind"] == "order":
                out[q["id"]] = br.CANT if q["foil"] else t
            elif q["kind"] == "label_each":
                out[q["id"]] = t
            else:
                out[q["id"]] = q["truth"]
        elif how == "habit":
            out[q["id"]] = list(range(1, 6)) if q["kind"] == "order" else (
                [q["options"][0]] * 4 if q["kind"] == "label_each" else q["options"][0])
        elif how == "position":   # reads the order straight off the layout, foil or not
            a = answers(m, "truth")[q["id"]]
            out[q["id"]] = t if q["kind"] == "order" else a
    return out


def fake(reply):
    seen = {}

    def reader(prompt, dirs):
        seen["prompt"] = prompt
        return "some reasoning first {\"not\": 1}\n" + reply
    return reader, seen


def checks():
    fails = []

    def ok(cond, what):
        if not cond:
            fails.append(what)

    with tempfile.TemporaryDirectory() as tmp:
        m = manifest(tmp)
        r, seen = fake(json.dumps(answers(m, "truth")))
        res = br.run(json.loads(json.dumps(m)), r)
        ok(res["parsed"], "truthful reply parsed")
        ok(all(v == "PASS" for v in res["bars"].values()), "truthful reader passes every bar: %s" % res["bars"])
        ok("[3, 1, 5, 2, 4]" not in seen["prompt"] and "3, 1, 5, 2, 4" not in seen["prompt"], "no order truth in prompt")
        ok("tar" not in seen["prompt"].split("answer a list")[0], "no label truth before the option lists")
        ok(br.CANT in seen["prompt"], "the reader is offered 'cannot tell'")

        r, _ = fake(json.dumps(answers(m, "habit")))
        res = br.run(json.loads(json.dumps(m)), r)
        ok(all(v == "FAIL" for v in res["bars"].values()), "habit reader fails every bar: %s" % res["bars"])

        r, _ = fake(json.dumps(answers(m, "position")))
        res = br.run(json.loads(json.dumps(m)), r)
        ok(res["bars"]["canal_reads_as_dug"] == "FAIL", "position reader fails on the dig foil")
        ok(res["bars"]["pit_reads_as_hole"] == "PASS", "position reader still passes a bar with no order foil")

        m2 = json.loads(json.dumps(m))
        m2["hose_kind"]["images"] = [os.path.join(tmp, "absent.png")]
        r, _ = fake(json.dumps(answers(m, "truth")))
        res = br.run(m2, r)
        ok(res["bars"]["hose_reads_as_hose"] == "UNMEASURED", "missing capture -> UNMEASURED: %s" % res["bars"])
        ok(res["bars"]["inv_looks"] == "UNMEASURED", "missing capture keeps the look inventory UNMEASURED")

        m3 = json.loads(json.dumps(m))
        del m3["bridge_under"]
        res = br.run(m3, fake(json.dumps(answers(m, "truth")))[0])
        ok(res["bars"]["hung_bridge_spans"] == "UNMEASURED", "question absent from manifest -> UNMEASURED")

        res = br.run(json.loads(json.dumps(m)), fake("I could not open the pictures.")[0])
        ok(set(res["bars"].values()) == {"UNMEASURED"}, "unparsable reply -> all UNMEASURED")

        a = answers(m, "truth")
        a["pit_kind"] = "a big hole"
        res = br.run(json.loads(json.dumps(m)), fake(json.dumps(a))[0])
        ok(res["bars"]["pit_reads_as_hole"] == "UNMEASURED", "an answer off the option list is UNMEASURED")

        m4 = json.loads(json.dumps(m))
        m4["pit_kind"]["label"] = "superdeep pit"
        orig = br.prompt_for
        br.prompt_for = lambda qs, man: orig(qs, man) + "\n(label: superdeep pit)"
        try:
            br.run(m4, fake("{}")[0])
            ok(False, "a prompt carrying a label is refused")
        except SystemExit as e:
            ok("REFUSED" in str(e), "leak refusal names itself")
        finally:
            br.prompt_for = orig

    ok(br.parse_reply('x {"a": 1} y {"b": [1, 2]}') == {"b": [1, 2]}, "parse_reply takes the last JSON object")
    if os.name != "nt":
        ok(br._native("C:\\Users\\M\\shot.png") == "/mnt/c/Users/M/shot.png", "Windows capture path read from WSL")

    if os.path.exists(TABLE):
        tt = json.load(open(TABLE))
        want = {b["id"] for b in tt["bars"] if "LOOK_BLIND_READER" in (b.get("decides") or [])}
        have = set(br.BARS) | {br.LOOK_BAR}
        ok(want <= have, "every bar LOOK_BLIND_READER decides has its questions: missing %s" % sorted(want - have))
        scenes = {q["scene"] for q in br.QUESTIONS}
        ok(scenes <= set(tt["tests"]), "every question's scene is a test in the table: %s" % sorted(scenes - set(tt["tests"])))
    for b in br.BARS:
        qs = [q for q in br.QUESTIONS if q["bar"] == b]
        ok(any(q["foil"] for q in qs), "bar %s has a foil question (scenes.json control)" % b)
    return fails


def mutants():
    """Each mutant of the scorer must make checks() red."""
    red = []
    orig_score, orig_run = br.score, br.run

    def no_foil(q, spec, a):
        return orig_score(dict(q, foil=False), spec, a)

    def lax_choice(q, spec, a):
        v, w = orig_score(q, spec, a)
        return ("PASS", w) if q["kind"] == "choice" and v == "FAIL" else (v, w)

    def unmeasured_passes(q, spec, a):
        v, w = orig_score(q, spec, a)
        return ("PASS" if v == "UNMEASURED" else v), w

    for name, m in (("foil scored as a plain question", no_foil), ("any option passes a choice", lax_choice),
                    ("UNMEASURED counted as PASS", unmeasured_passes)):
        br.score = m
        try:
            red.append((name, bool(checks())))
        finally:
            br.score = orig_score
    br.run = orig_run
    return red


def main():
    fails = checks()
    for f in fails:
        print("FAIL", f)
    mut = mutants()
    for name, was_red in mut:
        print("mutant %-34s %s" % (name, "red" if was_red else "SURVIVED"))
    bad = len(fails) + sum(1 for _, r in mut if not r)
    print("selftest_blind_reader: %s (%d questions, %d mutants red)" % (
        "PASS" if not bad else "FAIL", len(br.QUESTIONS), sum(1 for _, r in mut if r)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
