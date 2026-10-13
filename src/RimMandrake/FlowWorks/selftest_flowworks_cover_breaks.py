#!/usr/bin/env python3
"""FLOWWORKS_REVIEW_LOOKS_ROUND_1 item 11 (owner, 2026-10-06): "And when something falls into a covered pit, of
course it is no longer covered".

Measured in source, not assumed: the ONLY way anything drops through an intact pit cover is
Building_PitCover.Spring (the deck's mass trigger), and Spring destroys every cover of the deck BEFORE it sends a
single faller down (RM_SuperdeepTrap.OnForcedDescent). Everywhere else an intact cover is ground (IsHeldAt and the
descent detector skip a covered cell), so nothing can be "in the pit" under a cover that still stands.

This check pins both facts so a refactor that reorders Spring, a detector that stops skipping covered cells, or a new
path that drops a pawn/item through a cover without springing it (or without requiring an open pit at the falling cell),
fails here; in-memory mutants prove the detector and open-pit guards can go red. Items/corpses (Explosive Knockback, not built) must call Spring too.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_cover_breaks.py
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source"


def method_body(text, signature):
    i = text.index(signature)
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j:k + 1]
    raise ValueError(signature)


HEADER = re.compile(r"^\s*(?:\[[^\]]*\]\s*)*(?:public|private|internal|protected)\b[^;=]*\)\s*$", re.M)


def enclosing_method(text, pos):
    """The body of the method whose header is the last one before `pos` (headers are one line in this codebase)."""
    heads = [m for m in HEADER.finditer(text, 0, pos)]
    assert heads, "no method header before offset %d" % pos
    return method_body(text, heads[-1].group(0).strip())


def detector_guard_probs(trap):
    """The descent detector (RM_SuperdeepTrapState.Tick) must skip a covered cell: its descent condition carries
    !IsCovered(map, pos)."""
    tick = method_body(trap, "public void Tick(Map map, RM_MapComponent_Excavation eng)")
    i, j = tick.find("if (lastCell.TryGetValue"), tick.find("descents.Add(")
    if i < 0 or j < 0:
        return ["the descent detector's condition is gone from Tick (anchor moved: re-scope this check)"]
    if not re.search(r"!\s*(?:Pits\.)?RM_PitCoverUtility\.IsCovered\(\s*map\s*,\s*pos\s*\)", tick[i:j]):
        return ["the descent detector no longer skips a covered cell (!IsCovered(map, pos) gone from its condition)"]
    return []


def open_pit_guard_probs(text, rel):
    """Every OnForcedDescent(p, CELL, ...) call outside Spring and the detector sits in a method that returns early
    unless CELL itself is an open pit: !IsOpenPit(..., CELL). IsOpenPit on another cell, or un-negated, does not count."""
    probs = []
    # every call must be READ: a call the parsing regex cannot fit (an indexed or member first argument, two
    # arguments) used to be counted as a caller and then never checked -- a vacuous pass
    calls = [m for m in re.finditer(r"OnForcedDescent\(", text)
             if not any(k in text[text.rfind("\n", 0, m.start()):m.end()] for k in ("static void OnForcedDescent", "///"))]
    parsed = []
    for m in re.finditer(r"OnForcedDescent\(\s*\w+\s*,\s*([^,]+?)\s*,", text):
        line = text.count("\n", 0, m.start()) + 1
        if "static void OnForcedDescent" in text[text.rfind("\n", 0, m.start()):m.end()]:
            continue
        parsed.append(m.start())
        body = enclosing_method(text, m.start())
        before = body[:body.find(m.group(0))]
        cell = re.escape(m.group(1))
        # IsOpenHole (PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP) is the relative rule's open-pit test: any dug cell not under an
        # intact cover; pinned below to keep its cover read
        if not re.search(r"!\s*(?:RM_PitPathing\.)?IsOpen(?:Pit|Hole)\([^;]*?,\s*%s\s*\)" % cell, before):
            probs.append("%s:%d drops through without requiring an open pit at %s" % (rel, line, m.group(1)))
    for m in calls:
        if m.start() not in parsed:
            probs.append("%s:%d OnForcedDescent call this check cannot parse (unchecked): %s" % (
                rel, text.count("\n", 0, m.start()) + 1, text[m.start():text.find("\n", m.start())].strip()[:80]))
    return probs


def main():
    cover = (SRC / "Pits" / "Building_PitCover.cs").read_text(encoding="utf-8")
    spring = method_body(cover, "public void Spring(List<Pawn> fallers)")
    destroy = spring.find("c.Destroy(")
    descend = spring.find("OnForcedDescent(")
    assert destroy >= 0, "Spring no longer destroys the covers"
    assert descend >= 0, "Spring no longer sends the fallers down"
    assert destroy < descend, "Spring sends fallers down before the cover is gone"
    assert re.search(r"foreach \(Building_PitCover c in deck\)", spring), "Spring no longer breaks the WHOLE deck"
    # every forced descent outside the trap itself goes through Spring
    callers = []
    for f in SRC.rglob("*.cs"):
        if "SelfTest" in f.parts:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "OnForcedDescent(" in line and "static void OnForcedDescent" not in line and "///" not in line:
                callers.append((f.relative_to(SRC).as_posix(), n))
    probe = [c for c in callers if c[0] == "Pits/Building_PitCover.cs"]
    assert probe, "sanity probe: the Spring call site itself must be found (%s)" % callers
    trap = (SRC / "Superdeep" / "RM_SuperdeepTrap.cs").read_text(encoding="utf-8")
    det = [c for c in callers if c[0] == "Superdeep/RM_SuperdeepTrap.cs"]
    assert len(det) == 1, "the trap file should call OnForcedDescent once (the detector), found %s" % det
    probs = detector_guard_probs(trap)
    for f in sorted({f for f, _ in callers} - {"Pits/Building_PitCover.cs", "Superdeep/RM_SuperdeepTrap.cs"}):
        probs += open_pit_guard_probs((SRC / f).read_text(encoding="utf-8"), f)
    assert not probs, "a forced descent can pass through an intact cover: %s" % probs
    held = method_body(trap, "public static bool IsHeldAt(Pawn p, IntVec3 c)")
    assert "IsCovered" in held, "an intact cover no longer reads as ground for the hold"

    # CAN IT FAIL (in-memory mutants; the real files are never written)
    assert detector_guard_probs(trap.replace("&& !Pits.RM_PitCoverUtility.IsCovered(map, pos)", "", 1)), \
        "CANNOT FAIL: deleting the detector's cover gate stayed green"
    pp = (SRC / "Superdeep" / "RM_PitPathing.cs").read_text(encoding="utf-8")
    assert not open_pit_guard_probs(pp, "pp"), "sanity: the real PitPathing guard must pass"
    hole = method_body(pp, "public static bool IsOpenHole(Map map, RM_MapComponent_Excavation eng, IntVec3 c)")
    assert "!Pits.RM_PitCoverUtility.IsCovered(map, c)" in hole and "return IsOpenPit(map, eng, c);" in hole, \
        "IsOpenHole (the relative rule's open-pit guard) no longer reads the cover / falls back to IsOpenPit"
    mut = re.sub(r"!\s*RM_PitPathing\.IsOpenHole\(p\.Map, eng, p\.Position\)", "false", pp, count=1)
    assert mut != pp and open_pit_guard_probs(mut, "pp"), \
        "CANNOT FAIL: removing the p.Position open-pit guard stayed green (IsOpenPit(.., from) alone satisfied it)"
    odd = pp.replace("RM_PitPathing.IsOpenHole(p.Map, eng, p.Position)",
                     "RM_PitPathing.IsOpenHole(p.Map, eng, p.Position)) {} if (false) RM_SuperdeepTrap.OnForcedDescent(fallers[0], c);"
                     " if (!(true)", 1)
    assert odd != pp and any("cannot parse" in x for x in open_pit_guard_probs(odd, "pp")), \
        "CANNOT FAIL: a two-argument / indexed OnForcedDescent caller stayed green (counted, never checked)"
    print("ok  cover breaks on every fall: Spring destroys the whole deck before %d descent call(s); the detector skips "
          "covered cells; other drops require an open pit at the falling cell; intact cover = ground; 3 mutants red"
          % len(probe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
