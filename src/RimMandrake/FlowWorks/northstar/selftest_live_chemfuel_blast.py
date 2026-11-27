#!/usr/bin/env python3
"""Offline check of live_chemfuel_blast.py's pure verdicts (RIMMANDRAKE_PROVE_LIT_CHEMFUEL_BLAST_THROWS_WITH_KNOCKBACK): the
radius rule, the two parsers and the blast/pawn verdicts, each with a case that must FAIL and one that must be UNMEASURED,
so a blind instrument cannot read as PASS."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_chemfuel_blast as P  # noqa: E402

LIT = (122, 150)


def main():
    bad, n = [], [0]

    def check(cond, what):
        n[0] += 1
        if not cond:
            bad.append(what)

    check(abs(P.expected_radius(360000) - 3.448) < 1e-3, "full body caps at a 150 stack: %r" % P.expected_radius(360000))
    check(abs(P.expected_radius(1500) - 1.1) < 1e-9, "a smear blasts as one item")
    check(abs(P.expected_radius(2000 * 10) - (1.1 + (9 * 0.037) ** 0.5)) < 1e-9, "ten items")
    b = P.parse_blasts("IGNITIONBLASTS 122,150 r=3.45 t=900 fired")
    check(b == [{"x": 122, "z": 150, "r": 3.45, "t": 900, "fired": True}], "parse blasts: %r" % (b,))
    check(P.parse_blasts("REFUSED: no current map") is None and P.parse_blasts(None) is None, "parse refuses junk")
    check(P.parse_blasts("IGNITIONBLASTS") == [], "no blast parses empty")
    j = P.parse_journal('{"type":"request","exp":7,"thing":"Human1","centre":[122,150]}\njunk\n{bad')
    check(len(j) == 1 and P.blast_exps(j, LIT) == {7}, "journal parse and exp pick")
    r = 3.448
    check(P.v_blast(b, LIT, r)[0] == "PASS", "one fired blast passes")
    check(P.v_blast([], LIT, r)[0] == "FAIL", "no blast fails")
    check(P.v_blast(b + b, LIT, r)[0] == "FAIL", "two blasts fail")
    check(P.v_blast([dict(b[0], fired=False)], LIT, r)[0] == "FAIL", "queued-only fails")
    check(P.v_blast([dict(b[0], r=2.0)], LIT, r)[0] == "FAIL", "wrong radius fails")
    check(P.v_blast(None, LIT, r)[0] == "UNMEASURED", "failed read is blind")
    req = {"type": "request", "exp": 7, "thing": "H1", "centre": [122, 150]}
    lau = {"type": "launch", "exp": 7, "thing": "H1"}
    land = {"type": "land", "exp": 0, "thing": "H1", "at": [126, 150]}
    rows = [req, lau, land]
    st, det = P.v_pawn("inside", "H1", (123, 150), (123, 150), rows, {7}, LIT)
    check(st == "PASS" and det["gain"] == 3.0, "inside thrown 3 (land row wins): %r" % (det,))
    check(P.v_pawn("inside", "H1", (123, 150), (123, 150), [req], {7}, LIT)[0] == "FAIL", "inside not launched fails")
    check(P.v_pawn("inside", "H1", (123, 150), (123, 150), [req, lau], {7}, LIT)[0] == "FAIL", "launch but no gain fails")
    check(P.v_pawn("inside", "H1", None, (1, 1), rows, {7}, LIT)[0] == "UNMEASURED", "inside read failure is blind")
    e = [{"type": "request", "exp": 7, "thing": "H2"}]
    check(P.v_pawn("edge", "H2", (122, 153), (122, 153), e, {7}, LIT, 3.0)[0] == "PASS", "edge reached, not thrown")
    check(P.v_pawn("edge", "H2", (122, 153), (122, 153), [], {7}, LIT, 3.0)[0] == "FAIL", "edge unreached fails")
    far = e + [{"type": "launch", "exp": 7, "thing": "H2", "from": [122, 153], "to": [122, 158]}]
    check(P.v_pawn("edge", "H2", (122, 153), (122, 158), far, {7}, LIT, 3.0)[0] == "FAIL", "edge thrown farther fails")
    near = e + [{"type": "launch", "exp": 7, "thing": "H2", "from": [122, 153], "to": [122, 154]}]
    st, det = P.v_pawn("edge", "H2", (122, 153), (122, 154), near, {7}, LIT, 3.0)
    check(st == "PASS" and det["throw"] == 1.0, "edge thrown less than inside holds: %r" % (det,))
    sk = e + [{"type": "skip", "exp": 7, "thing": "H2", "reason": "weak"}]
    st, det = P.v_pawn("edge", "H2", (122, 153), (127, 157), sk, {7}, LIT, 3.0)
    check(st == "PASS" and det["throw"] == 0.0 and det["walk"] > 3.0 and det["skips"] == ["weak"],
          "edge skipped by EK, walked away burning: walk recorded, not judged: %r" % (det,))
    check(P.thrown([{"type": "launch", "from": [123, 150], "to": [126, 150]}], LIT) == 3.0, "throw from launch row")
    check(P.thrown([{"type": "request"}], LIT) == 0.0, "no launch, no throw")
    check(P.v_pawn("edge", "H2", (122, 153), (122, 153), e, {7}, LIT, None)[0] == "UNMEASURED", "edge without inside blind")
    check(P.v_pawn("outside", "H3", (122, 145), (122, 145), [], {7}, LIT)[0] == "PASS", "outside untouched")
    check(P.v_pawn("outside", "H3", (122, 145), (122, 145), [{"exp": 7, "thing": "H3"}], {7}, LIT)[0] == "FAIL",
          "outside reached fails")
    check(P.v_pawn("outside", "H3", (122, 145), (122, 144), [], {7}, LIT)[0] == "FAIL", "outside moved fails")
    check(P.v_pawn("outside", "H3", (122, 145), (122, 145), [{"exp": 9, "thing": "H3"}], {7}, LIT)[0] == "PASS",
          "another explosion's row is not this blast's")
    site = (118, 143, 13, 14)
    pw = [{"id": "Old1", "x": 124, "z": 150}, {"id": "Old2", "x": 122, "z": 145, "isPlayer": True},
          {"id": "Dead", "x": 124, "z": 150, "dead": True}, {"id": "Gone", "x": 124, "z": 150, "spawned": False},
          {"id": "Far", "x": 200, "z": 150}, {"id": "Rim", "x": 115, "z": 140}, {"id": "Out", "x": 114, "z": 150},
          {"id": "NoPos", "x": None, "z": None}]
    check(P.squatters(pw, site) == ["Old1", "Old2", "Rim"], "squatters: live spawned pawns of any faction on site+margin: %r"
          % P.squatters(pw, site))
    check(P.squatters([], site) == [], "no pawns, no squatters")
    col = {"isPlayer": True, "intelligence": "Humanlike"}
    mine = [dict(col, id="H1"), dict(col, id="H2"), dict(col, id="H3")]
    check(P.own_to_remove(mine + [dict(col, id="Map1")], ["H1", "H2", "H3"]) == ["H1", "H2", "H3"],
          "own pawns go while a map colonist stays")
    check(P.own_to_remove(mine, ["H1", "H2", "H3"]) == [], "own pawns stay when they are the last colonists")
    check(P.own_to_remove(mine + [dict(col, id="Dead", dead=True), {"id": "Dog", "isPlayer": True,
                                                                     "intelligence": "Animal"}], ["H1", "H2", "H3"]) == [],
          "a dead colonist or a colony animal does not keep the colony")
    print("selftest_live_chemfuel_blast: %d/%d cases hold%s" % (n[0] - len(bad), n[0], "" if not bad else ": " + "; ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
