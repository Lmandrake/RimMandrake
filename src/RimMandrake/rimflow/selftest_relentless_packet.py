#!/usr/bin/env python3
"""relentless_packet: planted contaminated packets are refused, a clean one and code words are not."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless_packet as P  # noqa: E402

BAD = 0


def ok(v, what):
    global BAD
    print(("ok   " if v else "FAIL ") + what)
    BAD += 0 if v else 1


def clean():
    return {"goal": "g", "proof": "p", "range": "a..b", "oracle_diff": "", "exists": ["relentless.py has mods_held()"],
            "how_to_check": [{"command": "python3 x.py", "expected": "PASS"}], "unverified": ["no run on the real pool"]}


def hand_scored():
    """The committed real sample: lint is re-run on every row, and its false rejects and misses against the hand labels
    must be the counts the file records. A word-list change that moves either count fails here until it is re-scored."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata", "relentless_packet_handscored.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    rows = doc["rows"]
    ok(len(rows) >= 48 and len({r["evidence"] for r in rows}) == len(rows), "hand-scored set: %d distinct real rows" % len(rows))
    ok(all(r["hand"] in ("clean", "contaminated") for r in rows), "every row carries a hand label")
    drift = [r["n"] for r in rows if P.report(r) != r["lint_hits"]]
    ok(not drift, "lint reads each row as it did when scored (drift: %s)" % drift[:5])
    fr = sum(1 for r in rows if P.report(r) and r["hand"] == "clean")
    mi = sum(1 for r in rows if not P.report(r) and r["hand"] == "contaminated")
    want = doc["counts"]
    ok(fr == want["false_rejects"], "false rejects %d of %d hits, recorded %d" % (fr, sum(1 for r in rows if P.report(r)), want["false_rejects"]))
    ok(mi == want["misses"], "misses %d, recorded %d" % (mi, want["misses"]))


def main():
    st = {"contract": {"proof": "p"}}
    ok(P.lint(clean(), st) == [], "a clean packet passes")
    planted = [
        ("free field", lambda p: p.update(note="trust me"), "free field note"),
        ("evidence prose", lambda p: p.update(evidence="all green"), "free field evidence"),
        ("missing field", lambda p: p.pop("exists"), "no exists"),
        ("proof swapped", lambda p: p.update(proof="easier"), "proof differs"),
        ("nested clause", lambda p: p.update(unverified=[{"x": 1}]), "flat list"),
        ("no check", lambda p: p.update(how_to_check=[]), "non-empty"),
        ("prose check", lambda p: p.update(how_to_check=["run it"]), "how_to_check 0"),
        ("extra check key", lambda p: p["how_to_check"][0].update(why="x"), "how_to_check 0"),
        ("empty expected", lambda p: p["how_to_check"][0].update(expected=" "), "how_to_check 0"),
        ("because", lambda p: p["unverified"].append("skipped this because it is slow"), "word: because"),
        ("history", lambda p: p["exists"].append("the last attempt was rejected"), "word: last attempt"),
        ("marker named", lambda p: p["exists"].append("satisfies the Marker"), "word: the marker"),
        ("advocacy in expected", lambda p: p["how_to_check"][0].update(expected="PASS, clearly fine"), "word: clearly"),
        ("long clause", lambda p: p["unverified"].append("x" * 201), "over 200"),
    ]
    for name, plant, want in planted:
        p = clean()
        plant(p)
        got = P.lint(p, st)
        ok(any(want in r for r in got), "planted %s refused: %s" % (name, got[:2]))
    ok(P.lint("x") == ["schema: a packet is an object"], "not an object")
    p = clean()
    p["unverified"].append("the `because` token in parser.py is unchecked")
    ok(P.lint(p, st) == [], "a backticked word is the tree's, not Build's")
    p = clean()
    p["exists"].append("becauseOf() and prioritised lists")
    ok(P.lint(p, st) == [], "whole words only")
    ok(P.lint(P.build(st, {}, "g", "r", "d", {"exists": [], "how_to_check": clean()["how_to_check"], "evil": 1}), st) == [],
       "build drops what Build may not author")
    d = tempfile.mkdtemp()
    r = os.path.join(d, "store", "items", "I", "receipts")
    os.makedirs(r)
    for i, e in enumerate(("selftest PASS", "green because I was careful")):
        with open(os.path.join(r, "g%d.json" % i), "w") as f:
            json.dump({"item": "I", "gen": i, "evidence": e}, f)
    ok([bool(P.report(x)) for _, x in P.receipts(d)] == [False, True], "scan reads real receipts, and can see a hit")
    hand_scored()
    print("selftest_relentless_packet: %s" % ("PASS" if not BAD else "FAIL %d" % BAD))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
