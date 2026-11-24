#!/usr/bin/env python3
"""Selftest of scene_size.py; each check has the name of a promise of design/specs/2026-11-24-scene-size/boundary.md.
Run: python3 <this file>"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import scene_size as Z  # noqa: E402

PYRE = os.path.join(ROOT, "design", "concepts", "Pyrelands", "version", "test_table.json")
# sc_walk's entry as it stood on 2026-11-23 (fe1c67df02) and the waits of its chain, WALK_DAYS 7 twice and the later parts
OLD_WALK = {"id": "sc_walk", "kind": "live_full", "stage": "6", "file": "walk.py", "entry": "walk_season",
            "why_full_list": "the walk is ordinary play on his list (leaf walk_season_on_the_pyre, tier live_full)",
            "observes": "the digest after reload equals the one before; the second pass yields fruit again; no colonist takes a "
                        "burn standing in fire and none starves at fire duty; the grass under the new roof withers within days; "
                        "herds reach the water one at a time and none dehydrates; with the roster toggle off, and again with the "
                        "Mod enabled master (pyrelandsEnabled) off, no new front, no ash laid and no bed fire over the day, and "
                        "all three resume once it is back on; switches leave nothing behind; log clean"}
OLD_SRC = ("WALK_DAYS = 7\nTEN_DAY = 60000\ndef walk_season(t):\n    _wait(t, WALK_DAYS * 60000)\n    _wait(t, WALK_DAYS * 60000)\n"
           "    _ten(t)\ndef _ten(t):\n    _wait(t, 3 * TEN_DAY)\n    for _ in range(4):\n        _wait(t, TEN_DAY // 4)\n")


def spec(**k):
    return dict({"kind": "live_minimal", "stage": "6", "file": "x.py", "entry": "go", "observes": "a thing is seen"}, **k)


def tmp_root(src, name="x.py"):
    d = tempfile.mkdtemp(prefix="scene_size_")
    with open(os.path.join(d, name), "w") as f:
        f.write(src)
    return d


def words(sp, root):
    return Z.owed({"tests": {"t": sp}}, root).get("t", (None, []))[1]


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = Z.main(argv)
    return rc, out.getvalue()


def t_old_walk_is_red():
    w = words(OLD_WALK, tmp_root(OLD_SRC, "walk.py"))
    assert any("18.0 game days" in x for x in w) and any("full list" in x for x in w) and any("7 claims" in x for x in w), w
    f = os.path.join(tmp_root(""), "t.json")
    json.dump({"tests": {"sc_walk": OLD_WALK}}, open(f, "w"))
    rc, out = run(["check", "--table", f, "--mod", "Pyrelands"])
    assert rc == 1 and "sc_walk" in out, (rc, out)


def t_new_scenes_are_green():
    tt = json.load(open(PYRE))
    owes = Z.owed(tt)
    for t in ("sc_reload_keeps_the_burn", "sc_fire_sense"):
        assert t in tt["tests"] and t not in owes, (t, owes.get(t))
    m = Z.measure(tt["tests"]["sc_reload_keeps_the_burn"])
    assert m["days"] is not None and 0 < m["days"] < 0.2 and m["claims"] == 1 and not Z.over(m), m
    assert not [t for t, e in tt["tests"].items() if e.get("kind") == "live_full"]


def t_evidence_clears():
    r = tmp_root("def go(t):\n    _wait(t, 600000)\n")
    assert words(spec(), r) and not words(spec(cheaper_why="a year is the claim"), r)
    assert words(spec(cheaper_why="  "), r)


def t_span_is_counted():
    src = ("D = 60000\ndef go(t):\n    for i in range(3):\n        helper(t)\n    if x:\n        _wait(t, 5)\n    else:\n"
           "        t.wait_ticks(D)\n    while True:\n        _wait(t, 10)\n    for k in things:\n        _wait(t, n)\n"
           "def helper(t):\n    _wait(t, D // 2)\n")
    assert Z.span_ticks(src, "go") == (3 * 30000 + 60000 + 10, 2), Z.span_ticks(src, "go")
    assert Z.span_ticks(src, "gone") is None
    assert Z.span_ticks("def go(t):\n    go(t)\n    _wait(t, 7)\n", "go") == (7, 0)
    m = Z.measure(spec(file="missing.py"), tmp_root(""))
    assert m["days"] is None and Z.over(m) == []
    assert Z.measure(spec(), tmp_root("def go(:\n"))["days"] is None
    assert Z.measure(spec(file="a.cs"), tmp_root(""))["days"] is None


def t_declared_size_wins():
    r = tmp_root("def go(t):\n    _wait(t, 600000)\n")
    assert not words(spec(game_days=0.5), r) and words(spec(game_days=2), r)
    assert words(spec(game_days=0, claims=["a", "b"]), r) == ["holds 2 claims"]
    assert not words(spec(game_days=0, claims=["a"], observes="a; b; c; d; e; f"), r)
    assert words(spec(game_days=True), r)


def t_one_day_and_one_claim_pass():
    assert not words(spec(), tmp_root("def go(t):\n    _wait(t, 60000)\n"))
    assert words(spec(), tmp_root("def go(t):\n    _wait(t, 60001)\n    _wait(t, 3000)\n"))
    r = tmp_root("def go(t):\n    pass\n")
    assert not words(spec(observes="a; b; c; d; log clean"), r) and words(spec(observes="a; b; c; d; e"), r)
    assert Z.owed({"tests": {"t": spec(kind="offline", observes="a;b;c;d;e"), "u": spec(kind="look", stage="8", claims=["a", "b"])}}, r) == {}


def t_known_is_not_new():
    r = tmp_root("def go(t):\n    _wait(t, 120000)\n")
    tt = {"M": {"tests": {"t": spec()}}}
    assert len(Z.check(tt, r, {})[0]) == 1
    k = {"M": {"t": {"days": 2.0, "full": False, "claims": 1}}}
    assert Z.check(tt, r, k) == ([], [("M", "t", ["plays 2.0 game days (limit 1)"])])
    for grew in (dict(k["M"]["t"], days=1.5), dict(k["M"]["t"], claims=0)):
        assert len(Z.check(tt, r, {"M": {"t": grew}})[0]) == 1, grew
    full = {"M": {"tests": {"t": spec(kind="live_full")}}}
    assert len(Z.check(full, r, k)[0]) == 1


def t_full_list_is_refused():
    r = tmp_root("def go(t):\n    _wait(t, 10)\n")
    for sp in (spec(kind="live_full", cheaper_why="because"), spec(why_full_list="a donor patch", cheaper_why="because")):
        tt = {"M": {"tests": {"t": sp}}}
        new, _ = Z.check(tt, r, {"M": {"t": {"days": 9.0, "full": True, "claims": 9}}})
        assert len(new) == 1 and "full list" in new[0][2][0], new
        assert Z.check(tt, r, {}, left={("M", "t"): "why"}) == ([], [])
    assert not Z.check({"M": {"tests": {"t": spec(kind="live_minimal", why_full_list="")}}}, r, {})[0]
    for (m, t), why in Z.FULL_LEFT.items():         # an exemption names a test that still stands, with its reason
        tt = json.load(open(os.path.join(ROOT, "design", "concepts", m, "version", "test_table.json")))
        assert Z.measure(tt["tests"][t])["full"] and why, (m, t)


def t_tree_is_clean():
    rc, out = run(["check"])
    assert rc == 0, out


def t_unreadable_is_could_not_look():
    f = os.path.join(tmp_root(""), "t.json")
    open(f, "w").write("{")
    assert run(["check", "--table", f])[0] == 2
    assert run(["check", "--mod", "NoSuchMod"])[0] == 2
    keep, Z.KNOWN = Z.KNOWN, f
    try:
        keep_fn, Z.load_known = Z.load_known, lambda path=f: json.load(open(f))
        try:
            assert run(["check", "--mod", "Pyrelands"])[0] == 2
        finally:
            Z.load_known = keep_fn
    finally:
        Z.KNOWN = keep


def t_brief_names_them():
    r = tmp_root(OLD_SRC, "walk.py")
    got = Z.brief_lines(r, "Pyrelands", {"tests": {"sc_walk": OLD_WALK}})
    assert len(got) == 1 and "sc_walk" in got[0] and "cheaper_why" in got[0], got
    assert Z.brief_lines(r, "M", {"tests": {}}) == []
    src = open(os.path.join(HERE, "maturation.py"), encoding="utf-8").read()
    body = src.split("def ingame_brief_text(", 1)[1].split("\ndef ", 1)[0]
    assert "SZ.brief_lines(root, mod, tt)" in body
    import maturation as M
    lines = M._check_lines({"tests": {"t": spec(cheaper_why="because so")}, "bars": []}, ["t"], ROOT)
    assert any("because so" in x for x in lines), lines


def main():
    bad = 0
    tests = [t_old_walk_is_red, t_new_scenes_are_green, t_evidence_clears, t_span_is_counted,
             t_declared_size_wins, t_one_day_and_one_claim_pass, t_known_is_not_new, t_full_list_is_refused,
             t_tree_is_clean, t_unreadable_is_could_not_look, t_brief_names_them]
    for f in tests:
        try:
            f()
            print("PASS  %s" % f.__name__)
        except Exception as e:  # noqa: BLE001 - each check reports itself
            bad += 1
            print("FAIL  %s: %s: %s" % (f.__name__, type(e).__name__, str(e)[:400]))
    print("selftest_scene_size: %s" % ("FAIL %d" % bad if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
