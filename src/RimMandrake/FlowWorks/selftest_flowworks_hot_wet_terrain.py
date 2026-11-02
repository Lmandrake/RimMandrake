#!/usr/bin/env python3
"""selftest_flowworks_hot_wet_terrain.py — HOT_RELEASE_FIX_OWN_WET_TERRAIN (GPT finding FA_core_sim_1.4).

WHY: a hot freshwater release fills a dug channel with the freshwater ladder, but RM_HotLiquid.IsFillOf asked only
OwnsFillTerrain, which excludes the ladder: no scald, no steam. The fix: IsFillOf(map, cell, fluid) accepts the
fluid's fill tiers anywhere, and OwnsWetTerrain (ladder included) on a DUG cell only — an undug rung is a lake.
Verse-bound code, so this reads the production .cs (comments blanked) and asserts the fixed shape.

CAN IT FAIL: each check also runs against the pre-fix shape (UNDO) and must go red there.

BEHAVIOUR (added after a blind check found the token checks blind to `... && false`): the IsFillOf body and
FluidDef.OwnsWetTerrain are transpiled to Python and EVALUATED over their whole input truth table, and the scald and
steam call-site conditions are evaluated with IsFillOf stubbed true/false. Named MUTANTS of the real source (the
checker's `&& false`, dropping or inverting the dug gate, dropping the ladder, inverting either call site) must
each go red, so a check that cannot see its clause fails the test.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_hot_wet_terrain.py
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

CS = Path(__file__).resolve().parent / "Source" / "Machinery" / "Kits" / "RM_HotLiquid.cs"
FLUID_CS = Path(__file__).resolve().parent / "Source" / "FluidDef.cs"

UNDO = """		public static bool IsFillOf(TerrainDef t, FluidDef fluid)
		{
			return t != null && fluid != null && fluid.OwnsFillTerrain(t);
		}
	}
	class X { void A() { if (!RM_HotLiquid.IsFillOf(map.terrainGrid.TerrainAt(pawn.Position), p.fluid)) {} }
	void B() { if (c.InBounds(map) && RM_HotLiquid.IsFillOf(map.terrainGrid.TerrainAt(c), p.fluid)) {} } }
"""


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def is_fill_of_body(text: str) -> str:
    m = re.search(r"public static bool IsFillOf\(([^)]*)\)\s*\{", text)
    if not m:
        return ""
    i, depth = m.end(), 1
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return m.group(1) + "|" + text[m.end():i]


def checks(text: str) -> list[str]:
    fails = []
    body = is_fill_of_body(text)
    if not body:
        return ["IsFillOf not found"]
    sig = body.split("|", 1)[0]
    if not re.search(r"\bMap\s+map\b", sig) or not re.search(r"\bIntVec3\s+c\b", sig):
        fails.append("IsFillOf does not take (Map, IntVec3, FluidDef)")
    if "OwnsWetTerrain" not in body:
        fails.append("IsFillOf never asks OwnsWetTerrain: the freshwater ladder is not recognised")
    if "IsDugRaw" not in body:
        fails.append("IsFillOf does not gate the ladder on a dug cell: an undug lake would scald")
    if "OwnsFillTerrain" not in body:
        fails.append("IsFillOf dropped OwnsFillTerrain: temp-layer spills over open water are lost")
    calls = re.findall(r"RM_HotLiquid\.IsFillOf\(([^;]*?)\)\)?", text)
    if len(calls) < 2:
        fails.append(f"expected the scald and steam call sites, found {len(calls)}")
    if "IsFillOf(map.terrainGrid" in text:
        fails.append("a call site still passes a bare TerrainDef")
    return fails


# ---------------------------------------------------------------- behaviour: transpile and evaluate

def method_body(text: str, header_re: str) -> tuple[str, str] | None:
    m = re.search(header_re + r"\(([^)]*)\)\s*\{", text)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return m.group(1), text[m.end():i - 1]


def cs_expr(e: str) -> str:
    e = re.sub(r"\.GetComponent<(\w+)>\(\)", r'.GetComponent("\1")', e)
    e = e.replace("!=", " __NE__ ").replace("==", " __EQ__ ")
    e = e.replace("&&", " and ").replace("||", " or ")
    e = re.sub(r"!", " not ", e)
    e = e.replace("__NE__", "!=").replace("__EQ__", "==")
    e = re.sub(r"\bnull\b", "None", e)
    e = re.sub(r"\btrue\b", "True", e)
    e = re.sub(r"\bfalse\b", "False", e)
    return e


def transpile(params: str, body: str, name: str) -> str:
    """Brace-structured C# statements (if / return / local decl) -> a Python function."""
    args = [a.split()[-1] for a in params.split(",") if a.strip()]
    out = [f"def {name}({', '.join(args)}):"]
    depth = 1
    stmts = re.findall(r"[^;{}]*[;{}]", body)
    for raw in stmts:
        st = " ".join(raw.split())
        if not st:
            continue
        if st == "{":
            continue  # a bare brace after `if (...)` on its own line: the if already raised the depth
        if st == "}":
            depth -= 1
            continue
        pad = "    " * depth
        m = re.match(r"if \((.*)\) \{$", st)
        if m:
            out.append(f"{pad}if {cs_expr(m.group(1))}:")
            depth += 1
            continue
        m = re.match(r"if \((.*)\)$", st)
        if m:
            out.append(f"{pad}if {cs_expr(m.group(1))}:")
            depth += 1
            continue
        m = re.match(r"return (.*);$", st)
        if m:
            out.append(f"{pad}return {cs_expr(m.group(1))}")
            continue
        m = re.match(r"[\w<>.]+ (\w+) = (.*);$", st)
        if m:
            out.append(f"{pad}{m.group(1)} = {cs_expr(m.group(2))}")
            continue
        raise ValueError(f"untranslatable statement in {name}: {st!r}")
    return "\n".join(out) + "\n"


class Terrain:
    pass


class Cell:
    def __init__(self, inb): self.inb = inb
    def InBounds(self, _map): return self.inb


class Eng:
    def __init__(self, dug): self.dug = dug
    def IsDugRaw(self, _c): return self.dug


class TGrid:
    def __init__(self, t): self.t = t
    def TerrainAt(self, _c): return self.t


class Map_:
    def __init__(self, t, eng): self.terrainGrid, self.eng = TGrid(t), eng
    def GetComponent(self, name):
        return self.eng if name == "RM_MapComponent_Excavation" else None


class Fluid:
    def __init__(self, fill, wet): self.fill, self.wet = fill, wet
    def OwnsFillTerrain(self, _t): return self.fill
    def OwnsWetTerrain(self, _t): return self.wet


def load(src: str, name: str, glb: dict | None = None):
    ns = dict(glb or {})
    exec(src, ns)  # noqa: S102 — our own transpiled production code
    return ns[name]


def behaviour_checks(hot: str, fluid_cs: str) -> list[str]:
    fails: list[str] = []
    mb = method_body(hot, r"public static bool IsFillOf")
    if not mb:
        return ["behaviour: IsFillOf not found"]
    try:
        is_fill_of = load(transpile(mb[0], mb[1], "IsFillOf"), "IsFillOf")
    except Exception as e:  # a shape the transpiler cannot read is a red test, never a skip
        return [f"behaviour: IsFillOf not evaluable ({e})"]
    # whole truth table; OwnsWetTerrain is a superset of OwnsFillTerrain, so fill implies wet
    for inb, has_t, fill, wet, has_eng, dug in itertools.product([False, True], repeat=6):
        if fill and not wet:
            continue
        t = Terrain() if has_t else None
        m = Map_(t, Eng(dug) if has_eng else None)
        want = inb and has_t and (fill or (has_eng and dug and wet))
        try:
            got = bool(is_fill_of(m, Cell(inb), Fluid(fill, wet)))
        except Exception as e:
            fails.append(f"behaviour: IsFillOf raised {type(e).__name__} at inb={inb} t={has_t} fill={fill} "
                         f"wet={wet} eng={has_eng} dug={dug}")
            continue
        if got != want:
            fails.append(f"behaviour: IsFillOf={got}, want {want} at inb={inb} terrain={has_t} fill={fill} "
                         f"wet={wet} excavation={has_eng} dug={dug}")
    for m_, f_ in ((None, Fluid(True, True)), (Map_(Terrain(), Eng(True)), None)):
        try:
            if is_fill_of(m_, Cell(True), f_):
                fails.append("behaviour: IsFillOf true with a null map or fluid")
        except Exception as e:
            fails.append(f"behaviour: IsFillOf raised {type(e).__name__} on a null map or fluid")

    # the ladder itself: FluidDef.OwnsWetTerrain = fill tiers, or a freshwater rung when the ladder is on
    ow = method_body(fluid_cs, r"public bool OwnsWetTerrain")
    if not ow:
        fails.append("behaviour: FluidDef.OwnsWetTerrain not found")
        return fails
    try:
        for ladder, rung, fill in itertools.product([False, True], repeat=3):
            class Ladder:
                @staticmethod
                def IsFreshwaterRung(_t, r=rung): return r
            owns_wet = load(transpile(ow[0], ow[1], "OwnsWetTerrain"), "OwnsWetTerrain",
                            {"freshwaterLadder": ladder, "RM_WaterLadderDefs": Ladder,
                             "OwnsFillTerrain": (lambda _t, f=fill: f)})
            want = fill or (ladder and rung)
            if bool(owns_wet(Terrain())) != want:
                fails.append(f"behaviour: OwnsWetTerrain wrong at ladder={ladder} rung={rung} fill={fill}")
            # the item's scenario end to end: a ladder rung (not a fill tier) in a dug channel is ours; undug is a lake
            if ladder and rung and not fill:
                class F:
                    def OwnsFillTerrain(self, _t): return False
                    def OwnsWetTerrain(self, t): return owns_wet(t)
                if not is_fill_of(Map_(Terrain(), Eng(True)), Cell(True), F()):
                    fails.append("behaviour: a hot freshwater release does not own its ladder rung in a DUG channel")
                if is_fill_of(Map_(Terrain(), Eng(False)), Cell(True), F()):
                    fails.append("behaviour: an undug freshwater rung (a lake) counts as the release's own")
    except Exception as e:
        fails.append(f"behaviour: OwnsWetTerrain not evaluable ({e})")

    # call sites: scald continues (no damage) exactly when IsFillOf is false; steam puffs exactly when true
    sc = re.search(r"if \((pawn\.Dead[^{]*?)\)\s*\{\s*continue;", hot, flags=re.S)
    st = re.search(r"if \(([^{]*?RM_HotLiquid\.IsFillOf\(map, c, p\.fluid\)[^{]*?)\)\s*\{\s*FleckMaker\.ThrowAirPuffUp",
                   hot, flags=re.S)
    if not sc:
        fails.append("behaviour: scald call-site condition not found")
    if not st:
        fails.append("behaviour: steam call-site condition not found")

    class P:
        def __init__(self): self.Dead = self.Flying = False

    for verdict in (False, True):
        seen: list = []

        class Hot:
            @staticmethod
            def IsFillOf(m, c, f, v=verdict):
                seen.append((m, c, f)); return v
        pawn = P()
        pawn.Position = type("PosObj", (), {"InHorDistOf": lambda self, a, b: True})()
        pobj = type("Patch", (), {"center": 0, "reach": 1, "fluid": "FLUID"})()
        env = {"RM_HotLiquid": Hot, "pawn": pawn, "p": pobj, "map": "MAP", "c": "CELL"}
        if sc:
            try:
                cont = bool(eval(cs_expr(" ".join(sc.group(1).split())), env))  # noqa: S307
                if cont == verdict:
                    fails.append(f"behaviour: scald site {'skips' if cont else 'burns'} when IsFillOf={verdict}")
                if not any(a == ("MAP", pawn.Position, "FLUID") for a in seen):
                    fails.append("behaviour: scald site does not pass (map, pawn.Position, p.fluid)")
            except Exception as e:
                fails.append(f"behaviour: scald site not evaluable ({e})")
        seen.clear()
        if st:
            try:
                puff = bool(eval(cs_expr(" ".join(st.group(1).split())), env))  # noqa: S307
                if puff != verdict:
                    fails.append(f"behaviour: steam site puffs={puff} when IsFillOf={verdict}")
            except Exception as e:
                fails.append(f"behaviour: steam site not evaluable ({e})")
    return fails


# Each mutant puts back a broken clause in the REAL source; behaviour_checks must go red on every one.
HOT_MUTANTS = {
    "checker's mutant: ladder branch && false":
        ("eng.IsDugRaw(c) && fluid.OwnsWetTerrain(t);", "eng.IsDugRaw(c) && fluid.OwnsWetTerrain(t) && false;"),
    "undug gate inverted": ("eng.IsDugRaw(c) && fluid.OwnsWetTerrain(t);", "!eng.IsDugRaw(c) && fluid.OwnsWetTerrain(t);"),
    "dug gate dropped": ("eng != null && eng.IsDugRaw(c) && fluid.OwnsWetTerrain(t);", "fluid.OwnsWetTerrain(t);"),
    "ladder branch reverted to fill only": ("fluid.OwnsWetTerrain(t);", "fluid.OwnsFillTerrain(t);"),
    "fill tiers dropped": ("if (fluid.OwnsFillTerrain(t))", "if (false)"),
    "scald site inverted": ("|| !RM_HotLiquid.IsFillOf(map, pawn.Position, p.fluid))",
                            "|| RM_HotLiquid.IsFillOf(map, pawn.Position, p.fluid))"),
    "steam site inverted": ("if (RM_HotLiquid.IsFillOf(map, c, p.fluid))", "if (!RM_HotLiquid.IsFillOf(map, c, p.fluid))"),
}
FLUID_MUTANTS = {
    "ladder dropped from OwnsWetTerrain":
        ("|| (freshwaterLadder && RM_WaterLadderDefs.IsFreshwaterRung(terrain))", "|| false"),
}


def mutant_checks(hot: str, fluid_cs: str) -> list[str]:
    fails = []
    for name, (a, b) in HOT_MUTANTS.items():
        if a not in hot:
            fails.append(f"CAN-IT-FAIL: mutant '{name}' no longer applies (source moved: update the mutant)")
        elif not behaviour_checks(hot.replace(a, b, 1), fluid_cs):
            fails.append(f"CAN-IT-FAIL: mutant '{name}' passed every behaviour check")
    for name, (a, b) in FLUID_MUTANTS.items():
        if a not in fluid_cs:
            fails.append(f"CAN-IT-FAIL: mutant '{name}' no longer applies (source moved: update the mutant)")
        elif not behaviour_checks(hot, fluid_cs.replace(a, b, 1)):
            fails.append(f"CAN-IT-FAIL: mutant '{name}' passed every behaviour check")
    return fails


def main() -> int:
    text = strip_comments(CS.read_text(encoding="utf-8"))
    fails = checks(text)
    undo_fails = checks(strip_comments(UNDO))
    if not undo_fails:
        fails.append("CAN-IT-FAIL: the pre-fix shape passed every check")
    fluid_cs = strip_comments(FLUID_CS.read_text(encoding="utf-8"))
    fails += behaviour_checks(text, fluid_cs)
    fails += mutant_checks(text, fluid_cs)
    for f in fails:
        print("FAIL", f)
    print("PASS selftest_flowworks_hot_wet_terrain" if not fails else f"FAILED {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
