#!/usr/bin/env python3
"""selftest_blind_reader.py -- offline proof of northstar/blind_reader.py (LOOK_BLIND_READER), 0 ticks, no reader call.

Fake readers stand in for `claude -p`: a truthful one must PASS every bar; a habit reader (first option, 1..n order)
and a position reader (recovers the order on the foil too) must FAIL; a missing capture or an unparsable reply is
UNMEASURED, never PASS; the prompt carries no truth. Then each mutant of the scorer must turn a check red.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_blind_reader.py
"""
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blind_reader as br  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
TABLE = os.path.join(ROOT, "design/concepts/FlowWorks/version/test_table.json")


def manifest(tmp):
    """One picture file per question, its bytes naming the question: a reader can answer only by opening it."""
    m = {}
    for q in br.QUESTIONS:
        img = os.path.join(tmp, "cap_%d.png" % br.QUESTIONS.index(q))
        open(img, "wb").write(b"\x89PNG\r\n\x1a\n" + q["id"].encode())
        e = {"images": [img]}
        if q["kind"] == "order":
            e.update({"n": 5, "truth": [3, 1, 5, 2, 4]})
        elif q["kind"] == "label_each":
            e.update({"n": 4, "truth": ["water", "oil", "mud", "tar"]})
        m[q["id"]] = e
    return m


def answer_for(q, truth, how):
    if how == "truth":
        if q["kind"] == "order":
            return br.CANT if q["foil"] else truth
        return truth if q["kind"] == "label_each" else q["truth"]
    if how == "habit":      # the same answer whatever the picture
        return list(range(1, 6)) if q["kind"] == "order" else (
            ["water"] * 4 if q["kind"] == "label_each" else q["options"][0])
    if how == "position":   # reads the order straight off the layout, foil or not
        return truth if q["kind"] == "order" else answer_for(q, truth, "truth")
    if how == "near_miss":  # the foil read one swap away from the truth
        return [3, 1, 5, 4, 2] if q["kind"] == "order" and q["foil"] else answer_for(q, truth, "truth")
    raise ValueError(how)


def fake(m, how, override=None, raw=None):
    """A reader that opens each picture to learn which question it is, then answers `how`."""
    seen = {}

    def reader(prompt, pics_dir):
        seen.update(prompt=prompt, pics_dir=pics_dir)
        if raw is not None:
            return raw
        out, nid = {}, None
        for line in prompt.splitlines():
            h = re.match(r"^(Q\d+): ", line)
            if h:
                nid = h.group(1)
            pm = re.match(r"^  picture: (.+)$", line)
            if pm and nid:
                qid = open(pm.group(1), "rb").read()[8:].decode()
                q = br.BY_ID[qid]
                a = answer_for(q, m[qid].get("truth"), how)
                out[nid] = (override or {}).get(qid, a)
        return "some reasoning first {\"not\": 1}\n" + json.dumps(out)
    return reader, seen


def cp(m):
    return json.loads(json.dumps(m))


def checks():
    fails = []

    def ok(cond, what):
        if not cond:
            fails.append(what)

    try:
        _checks(ok)
    except BaseException as e:   # a crash or a refusal is a red check, never a silent pass
        fails.append("checks crashed: %r" % (e,))
    return fails


def _checks(ok):
    with tempfile.TemporaryDirectory() as tmp:
        m = manifest(tmp)
        r, seen = fake(m, "truth")
        res = br.run(cp(m), r, seed=7)
        rows = {x["id"]: x for x in res["rows"]}
        ok(res["parsed"], "truthful reply parsed")
        ok(all(v == "PASS" for v in res["bars"].values()), "truthful reader passes every bar: %s" % res["bars"])
        ok(all(x["verdict"] == "PASS" for x in rows.values()), "truthful reader passes every row, foils included")
        pr = seen["prompt"]
        ok(not [q["id"] for q in br.QUESTIONS if q["id"] in pr], "no question id in the prompt")
        ok("foil" not in pr and "control" not in pr, "no foil mark in the prompt")
        ok(not re.search(r"3\s*,\s*1\s*,\s*5\s*,\s*2\s*,\s*4", pr), "no order truth in the prompt")
        ok(tmp not in pr and "/home/" not in pr, "the prompt names picture copies, never the captures' paths")
        ok(seen["pics_dir"].startswith("/tmp/") and not os.path.exists(seen["pics_dir"]),
           "pictures copied to a /tmp dir that is gone after the run")
        ok(br.CANT in pr, "the reader is offered 'cannot tell'")
        r2, seen2 = fake(m, "truth")
        br.run(cp(m), r2, seed=8)
        ok(seen2["prompt"] != pr, "the seed shuffles questions and options")

        res = br.run(cp(m), fake(m, "habit")[0], seed=7)
        ok(all(v == "FAIL" for v in res["bars"].values()), "habit reader fails every bar: %s" % res["bars"])
        same = {q: "the same" for q in ("fill_differ", "fill_same_foil")}
        res = br.run(cp(m), fake(m, "truth", override=same)[0], seed=7)
        ok(res["bars"]["fill_level_legible"] == "FAIL", "one answer to both fill twins fails the bar")

        res = br.run(cp(m), fake(m, "position")[0], seed=7)
        rows = {x["id"]: x for x in res["rows"]}
        ok(rows["dig_depth_order_foil"]["verdict"] == "FAIL", "position reader fails the dig foil row")
        ok(res["bars"]["canal_reads_as_dug"] == "FAIL", "position reader fails on the dig foil")
        ok(res["bars"]["pit_reads_as_hole"] == "PASS", "position reader still passes a bar with no order foil")
        res = br.run(cp(m), fake(m, "near_miss")[0], seed=7)
        ok(res["bars"]["canal_reads_as_dug"] == "FAIL", "a foil read one swap from the truth is still a reading: FAIL")

        m2 = cp(m)
        m2["hose_kind"]["images"] = [os.path.join(tmp, "absent.png")]
        res = br.run(m2, fake(m, "truth")[0], seed=7)
        ok(res["bars"]["hose_reads_as_hose"] == "UNMEASURED", "missing capture -> UNMEASURED: %s" % res["bars"])
        ok(res["bars"]["inv_looks"] == "UNMEASURED", "missing capture keeps the look inventory UNMEASURED")
        m3 = cp(m)
        del m3["bridge_under"]
        res = br.run(m3, fake(m, "truth")[0], seed=7)
        ok(res["bars"]["hung_bridge_spans"] == "UNMEASURED", "question absent from manifest -> UNMEASURED")
        m4 = cp(m)
        m4["dig_banks"] = "oops"
        m4["pit_kind"]["images"] = m4["pit_kind"]["images"][0]
        res = br.run(m4, fake(m, "truth")[0], seed=7)
        ok(res["bars"]["canal_reads_as_dug"] == "UNMEASURED" and res["bars"]["pit_reads_as_hole"] == "UNMEASURED",
           "a non-object entry or a string images value -> UNMEASURED, no crash")
        m5 = cp(m)
        m5["dig_depth_order_foil"]["truth"] = ["3", "1", "5", "2", "4"]
        res = br.run(m5, fake(m5, "position")[0], seed=7)
        ok(res["bars"]["canal_reads_as_dug"] != "PASS", "a string-typed order truth never lets the foil pass")
        res = br.run(cp(m), fake(m, "truth", override={"fill_order": [1, "2", 3, 4, None]})[0], seed=7)
        ok(res["bars"]["fill_level_legible"] == "UNMEASURED", "a mixed-type order answer -> UNMEASURED, no crash")
        res = br.run(cp(m), fake(m, "truth", raw="I could not open the pictures.")[0], seed=7)
        ok(set(res["bars"].values()) == {"UNMEASURED"}, "unparsable reply -> all UNMEASURED")
        res = br.run(cp(m), fake(m, "truth", override={"pit_kind": "a big hole"})[0], seed=7)
        ok(res["bars"]["pit_reads_as_hole"] == "UNMEASURED", "an answer off the option list is UNMEASURED")

        m6 = cp(m)
        m6["pit_kind"]["label"] = "superdeep pit"
        orig = br.prompt_for
        br.prompt_for = lambda asked, rng=None: (orig(asked, rng)[0] + "\n(label: superdeep pit)", {})
        try:
            br.run(m6, fake(m, "truth")[0], seed=7)
            ok(False, "a prompt carrying a label is refused")
        except SystemExit as e:
            ok("REFUSED" in str(e), "leak refusal names itself")
        finally:
            br.prompt_for = orig
        ok(br.leaks("Q1: hose_flat_foil", {}), "a question id in the prompt is a leak")
        ok(not br.leaks(br.prompt_for([("Q1", br.BY_ID["fill_liquids"], 4, ["/tmp/x/picture_01.png"])],
                                      __import__("random").Random(1))[0], cp(m)),
           "a label truth made of option words is not a false leak")

        calls = {}
        orig_run = br.subprocess.run
        br.subprocess.run = lambda cmd, **kw: (calls.update(cmd=cmd, **kw),
                                               type("R", (), {"returncode": 0, "stdout": "{}", "stderr": ""})())[1]
        try:
            br.claude_reader("p", "/tmp/blind_reader_x")
        finally:
            br.subprocess.run = orig_run
        c = calls.get("cmd") or []
        ok(c[c.index("--tools") + 1] == "Read" and c[c.index("--permission-mode") + 1] == "dontAsk"
           and "Read(/home/**)" in c and "Read(/mnt/**)" in c and "--strict-mcp-config" in c
           and calls.get("cwd") == "/tmp/blind_reader_x", "the reader is sandboxed: Read only, dontAsk, /home and /mnt denied")

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


def mutants():
    """Each mutant must make checks() red."""
    red = []
    o_score, o_leaks, o_prompt = br.score, br.leaks, br.prompt_for

    def no_foil(q, spec, a):
        return o_score(dict(q, foil=False), spec, a)

    def lax_choice(q, spec, a):
        v, w = o_score(q, spec, a)
        return ("PASS", w) if q["kind"] == "choice" and v == "FAIL" else (v, w)

    def unmeasured_passes(q, spec, a):
        v, w = o_score(q, spec, a)
        return ("PASS" if v == "UNMEASURED" else v), w

    def foil_any_mismatch(q, spec, a):
        if q["kind"] == "order" and q["foil"] and isinstance(a, list):
            return ("FAIL" if a == spec.get("truth") else "PASS"), "mutant"
        return o_score(q, spec, a)

    def real_ids(asked, rng=None):
        return o_prompt([(q["id"], q, n, p) for _, q, n, p in asked], rng)

    for name, attr, m in (("foil scored as a plain question", "score", no_foil),
                          ("any option passes a choice", "score", lax_choice),
                          ("UNMEASURED counted as PASS", "score", unmeasured_passes),
                          ("any non-exact order passes a foil", "score", foil_any_mismatch),
                          ("the leak guard sees nothing", "leaks", lambda p, man: []),
                          ("the prompt shows real question ids", "prompt_for", real_ids)):
        setattr(br, attr, m)
        try:
            red.append((name, bool(checks())))
        finally:
            br.score, br.leaks, br.prompt_for = o_score, o_leaks, o_prompt
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
