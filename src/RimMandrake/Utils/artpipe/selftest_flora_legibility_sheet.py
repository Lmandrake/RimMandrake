#!/usr/bin/env python3
"""selftest_flora_legibility_sheet.py — FLORA_GRADING_SHEET_REBUILD_DECAYED_UNGRADED: the flora legibility sheet's
subject pick and question, offline (no def dump, no art store). Exit 0 on pass."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_flora_legibility_sheet as B  # noqa: E402

FAILS = []


def ok(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  [{detail}]"))
    if not cond:
        FAILS.append(name)


def plants(n_tree, n_clump, n_single):
    out = []
    for s, n in (("tree", n_tree), ("clump", n_clump), ("single", n_single)):
        out += [{"defName": f"RM_{s.capitalize()}{i:03d}", "texPath": f"T/{s}{i}", "stratum": s} for i in range(n)]
    return out


def main() -> int:
    ok("stratum: a treeCategory makes a tree", B.stratum({"treeCategory": "Full", "maxMeshCount": 1}) == "tree")
    ok("stratum: Super trees are trees", B.stratum({"treeCategory": "Super"}) == "tree")
    ok("stratum: maxMeshCount > 1 is a clump", B.stratum({"treeCategory": "None", "maxMeshCount": 9}) == "clump")
    ok("stratum: one mesh, no tree is single", B.stratum({"treeCategory": "None", "maxMeshCount": 1}) == "single")
    ok("stratum: missing fields read as single", B.stratum({}) == "single")

    pool = plants(55, 77, 254)
    wave = {"tree000", "clump005", "single010", "single011"}
    a = B.select(pool, wave, 120)
    b = B.select(list(reversed(pool)), wave, 120)
    ok("select: deterministic whatever the input order", [p["defName"] for p in a] == [p["defName"] for p in b])
    ok("select: about the target", 115 <= len(a) <= 125, str(len(a)))
    names = {p["defName"] for p in a}
    ok("select: no def twice", len(names) == len(a))
    ok("select: every wave def is kept",
       {"RM_Tree000", "RM_Clump005", "RM_Single010", "RM_Single011"} <= names)
    ok("select: wave rows say so", all(p["why"] == "wave" for p in a if p["defName"] in
                                       {"RM_Tree000", "RM_Clump005", "RM_Single010", "RM_Single011"}))
    for s, share in (("tree", 55), ("clump", 77), ("single", 254)):
        got = sum(1 for p in a if p["stratum"] == s)
        want = round(120 * share / 386)
        ok(f"select: {s} gets its share ({want})", abs(got - want) <= 1, str(got))
    # sweep: every target from 1 to the pool keeps strata within one of their share and never repeats
    bad = []
    for t in range(1, 386):
        c = B.select(pool, set(), t)
        if len({p["defName"] for p in c}) != len(c):
            bad.append((t, "dup"))
        for s, share in (("tree", 55), ("clump", 77), ("single", 254)):
            if abs(sum(1 for p in c if p["stratum"] == s) - round(t * share / 386)) > 1:
                bad.append((t, s))
    ok("select: sweep 1..385, shares within one, no repeats", not bad, str(bad[:5]))
    ok("select: target >= pool returns everything", len(B.select(pool, set(), 999)) == len(pool))

    dup = [{"defName": "RM_A", "texPath": "T/x", "stratum": "single"},
           {"defName": "RM_ACultured", "texPath": "T/x", "stratum": "single"},
           {"defName": "RM_B", "texPath": "T/y", "stratum": "single"}]
    ok("select: one row per picture (shared texPath collapses)",
       [p["defName"] for p in B.select(dup, set(), 99)] == ["RM_A", "RM_B"])

    ok("wave stems: only class=flora", B.flora_stems({"stems": {"a": {"class": "flora"}, "b": {"class": "creature"}, "c": 1}}) == {"a"})

    q = B.question(a)
    ok("question: key legibility", q["key"] == "legibility")
    ok("question: works / borderline / mud", [o[0] for o in q["options"]] == ["works", "borderline", "mud"])
    ok("question: a row per chosen def", set(q["rows"]) == names)
    ok("question: no prefill anywhere (the decayed sheet was prefill-only)",
       not any(r.get("prefill") for r in q["rows"].values()))
    sys.path.insert(0, str(B.UTILS / "art"))
    try:
        import art_sheet
        import json, tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(q, fh)
        ok("question: art_sheet.load_question accepts it", art_sheet.load_question(fh.name)["key"] == "legibility")
        Path(fh.name).unlink()
    except ImportError as exc:
        ok("question: art_sheet importable", False, str(exc))

    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
