#!/usr/bin/env python3
"""selftest_flowworks_underliquid_parity.py — RIMMANDRAKE_FIX_BIG_PIT_SCENE_BUILDINGS_STAY_DRY and
RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE.

WHY: everything in a dug pit under liquid follows ONE law, solved offline in model/underliquid.py and ported to
Source/Superdeep/RM_UnderLiquid.cs. This keeps the two in parity:
  1. every constant of the law (surface metres, drawn heights, building height rule, deep opacity, darkening, the floor
     shadow, the label cut-off, the pawn cover's water colour) is the same number on both sides;
  2. the golden table in SelfTest/UnderLiquidParityChecks.cs (which the dotnet SelfTest checks RM_UnderLiquid.Seen
     against) is exactly what the model computes (`--write` regenerates it after a model change);
  3. the owner's retune holds in the model (opacity at 4 m about half the 2026-11-12 law's, the shallow end no more
     opaque than before, deeper is never clearer, opaque liquids hide);
  4. the production C# carries each fix (buildings, pawns and corpses covered, one floor shadow, labels fade, the wet
     floor drawn in the dry pit's own dark ground, the darkening wash, the settings).
Shape checks read the production .cs with comments masked; the drawing itself is a live look (LIVE_LOOK_CHECKLIST.md).

CAN IT FAIL: a model with the old law, a spliced golden row and a C# file with each fix taken out must each go RED.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_underliquid_parity.py [--write]
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
UL = SRC / "Superdeep" / "RM_UnderLiquid.cs"
DRAW = SRC / "Superdeep" / "RM_SubmergeDraw.cs"
WALLS = SRC / "Superdeep" / "RM_ExcavationWalls.cs"
MOD = SRC / "RimMandrakeFlowWorksMod.cs"
GOLD = SRC / "SelfTest" / "UnderLiquidParityChecks.cs"
PROGRAM = SRC / "SelfTest" / "Program.cs"
CSPROJ = SRC / "SelfTest" / "RimMandrakeFlowWorks.SelfTest.csproj"
BEGIN, END = "// BEGIN GOLDEN (selftest_flowworks_underliquid_parity.py --write)", "// END GOLDEN"


def load_model(path: Path = HERE / "model" / "underliquid.py"):
    spec = importlib.util.spec_from_file_location("underliquid_model", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mask_comments(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1]); i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2); j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j])); i = j
        else:
            out.append(ch); i += 1
    return "".join(out)


def method_body(text: str, sig: str) -> str:
    m = re.search(sig, text)
    if not m:
        return ""
    i = text.find("{", m.end())
    depth, j = 0, i
    while 0 <= j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1
    return ""


def cs_float(text: str, name: str):
    m = re.search(r"\b(?:const|static)\s+float\s+" + name + r"\s*=\s*([0-9.]+)f\s*;", text)
    return float(m.group(1)) if m else None


def golden_block(model) -> str:
    rows = ",\n".join("\t\t\t{ %sf, %sf, %sf }" % (c, m, v) for c, m, v in model.golden_rows())
    return BEGIN + "\n\t\tinternal static readonly float[,] Golden =\n\t\t{\n" + rows + "\n\t\t};\n\t\t" + END


def gold_rows_in(text: str):
    if BEGIN not in text or END not in text:
        return None
    block = text[text.index(BEGIN):text.index(END)]
    return [tuple(float(x) for x in r) for r in re.findall(r"\{\s*([0-9.]+)f,\s*([0-9.]+)f,\s*([0-9.]+)f\s*\}", block)]


def model_checks(model) -> list[tuple[str, bool]]:
    W = 0.45
    old4, new4 = 1 - model.seen_old(W, 4.0), 1 - model.seen(W, 4.0)
    ops = [1 - model.seen(W, m / 10) for m in range(0, 41)]
    return [
        ("retune: opacity of 4 m of water is about half the 2026-11-12 law's (%.3f vs %.3f)" % (new4, old4),
         abs(new4 - old4 / 2) <= 0.05),
        ("retune: the shallow end (0.5 m) is no more opaque than before",
         1 - model.seen(W, 0.5) <= 1 - model.seen_old(W, 0.5) + 1e-9),
        ("retune: deeper is never clearer, 0..4 m", all(b >= a - 1e-12 for a, b in zip(ops, ops[1:]))),
        ("retune: water still covers: 4 m shows less than 0.5 m", model.seen(W, 4.0) < model.seen(W, 0.5) - 0.1),
        ("opaque liquids hide at any depth", all(model.seen(0.0, m) == 0.0 for m in (0.01, 1.0, 4.0))),
        ("darkened: the liquid under a fully hidden thing is darker than the liquid",
         sum(model.mix(model.WATER_BODY, (1, 1, 1), 0.0)) < sum(model.WATER_BODY)),
        ("a building is covered by its cover height (a 0.4-fill bed is 0.8 m: all under at 2 m)",
         model.look(4.0, 2.0, W, model.building_metres(0.4)).cut == 1.0),
        ("a thing's floor shadow is seen through the liquid by the same law",
         abs(model.look(4.0, 2.0, W, 0.8).shadow - model.THING_SHADOW_ALPHA * model.seen(W, 2.0)) < 1e-9
         and model.look(4.0, 2.0, 0.0, 0.8).shadow == 0.0),
        ("a label fades with its thing's top and is hidden under tar",
         model.look(4.0, 0.1, W, 0.3).label == 1.0 and 0 < model.look(4.0, 2.0, W, 0.3).label < 1
         and model.look(4.0, 2.0, 0.0, 0.3).label == 0.0),
    ]


CONSTS = [("SurfaceMetres", "SURFACE_METRES"), ("ItemMetres", "ITEM_METRES"), ("MinifiedMetres", "MINIFIED_METRES"),
          ("SwaleMetres", "SWALE_METRES"), ("LyingLadderMetres", "LYING_LADDER_METRES"), ("StakeMetres", "STAKE_METRES"),
          ("CorpseMetres", "CORPSE_METRES"), ("FullCoverMetres", "FULL_COVER_METRES"),
          ("MinThingMetres", "MIN_THING_METRES"), ("LabelHidden", "LABEL_HIDDEN"),
          ("DefaultDeepOpacity", "DEEP_OPACITY"), ("DefaultDarken", "DARKEN"),
          ("DefaultThingShadowAlpha", "THING_SHADOW_ALPHA")]


def cs_checks(model, ul: str, draw: str, walls: str, mod: str, gold: str, program: str, csproj: str):
    ulm, drm, wam, mom = mask_comments(ul), mask_comments(draw), mask_comments(walls), mask_comments(mod)
    out = []
    for cs, py in CONSTS:
        v = cs_float(ulm, cs)
        out.append(("constant %s = model %s (%s vs %s)" % (cs, py, v, getattr(model, py)),
                    v is not None and abs(v - getattr(model, py)) < 1e-6))
    wb = re.search(r"WaterBody\s*=\s*new\s+Float3\(\s*([0-9.]+)f\s*,\s*([0-9.]+)f\s*,\s*([0-9.]+)f\s*\)", ulm)
    out.append(("pawn cover water colour = model WATER_BODY",
                bool(wb) and all(abs(float(a) - b) < 1e-6 for a, b in zip(wb.groups(), model.WATER_BODY))))
    seen = method_body(ulm, r"public\s+static\s+float\s+Seen\s*\(\s*float\s+clarity\s*,\s*float\s+metresOver\s*\)")
    out.append(("C# Seen caps a clear liquid by DeepOpacity", "DeepOpacity" in seen))
    rows = gold_rows_in(gold)
    want = [tuple(float(x) for x in r) for r in model.golden_rows()]
    out.append(("golden table in UnderLiquidParityChecks.cs = model (%s rows)" % (len(rows) if rows else 0),
                rows is not None and len(rows) == len(want)
                and all(abs(a - b) < 1e-5 for r, w in zip(rows, want) for a, b in zip(r, w))))
    out.append(("dotnet SelfTest compiles and runs the parity checks",
                "UnderLiquidParityChecks.cs" in csproj and "UnderLiquidParityChecks.Run(Case)" in program))
    begin = method_body(drm, r"public\s+static\s+void\s+Begin\s*\(\s*Thing\s+t\s*\)")
    standing = method_body(drm, r"private\s+static\s+float\s+StandingMetres\s*\(\s*Thing\s+t\s*\)")
    out.append(("installed buildings are covered by their real height (Begin -> StandingMetres -> BuildingMetres)",
                "StandingMetres(t)" in begin and "BuildingMetres(t)" in standing and "BuildingMetres(" in ulm))
    out.append(("pawns and corpses standing in liquid get the cover (PawnRenderer.RenderPawnAt)",
                re.search(r"HarmonyPatch\(\s*typeof\(\s*PawnRenderer\s*\)\s*,\s*nameof\(\s*PawnRenderer\.RenderPawnAt\s*\)", drm) is not None))
    out.append(("no vanilla sun shadow from a thing in a pit (SectionLayer_SunShadows transpiled)",
                re.search(r'TypeByName\(\s*"Verse\.SectionLayer_SunShadows"\s*\)\s*,\s*"Regenerate"', drm) is not None
                and "ShadowCaster" in drm))
    out.append(("no vanilla contact shadow in a pit; one floor shadow instead (Printer_Shadow + FloorShadow)",
                re.search(r"HarmonyPatch\(\s*typeof\(\s*Printer_Shadow\s*\)", drm) is not None and "FloorShadow(" in drm))
    out.append(("labels and stack counts fade with their thing (GenMapUI.DrawThingLabel)",
                re.search(r"HarmonyPatch\(\s*typeof\(\s*GenMapUI\s*\)\s*,\s*nameof\(\s*GenMapUI\.DrawThingLabel\s*\)", drm) is not None
                and "LabelAlpha(" in drm))
    st = method_body(wam, r"private\s+void\s+SeeThrough\s*\(")
    out.append(("the wet floor is the DRY pit's own dark ground (DryTerrainFor), not the light ground dug from",
                "DryTerrainFor(" in st and "OriginalTerrainAt" not in st))
    out.append(("the liquid is darkened under what it covers (Darken wash in SeeThrough)", "Darken" in st))
    for s in ("underLiquidDeepOpacity", "underLiquidDarken", "pitThingShadowAlpha"):
        out.append(("setting %s is saved and shown" % s, ('Scribe_Values.Look(ref ' + s) in mom and mom.count(s) >= 4))
    return out


def run(label: str, rows) -> int:
    bad = 0
    for name, ok in rows:
        print(("PASS " if ok else "FAIL ") + label + name)
        bad += not ok
    return bad


def main() -> int:
    model = load_model()
    texts = [p.read_text(encoding="utf-8") for p in (UL, DRAW, WALLS, MOD, GOLD if GOLD.exists() else UL, PROGRAM, CSPROJ)]
    if "--write" in sys.argv:
        g = GOLD.read_text(encoding="utf-8")
        if BEGIN not in g or END not in g:
            print("FAIL --write: golden markers not found in " + str(GOLD)); return 1
        GOLD.write_text(g[:g.index(BEGIN)] + golden_block(model) + g[g.index(END) + len(END):], encoding="utf-8")
        print("WROTE golden table: " + str(GOLD)); texts[4] = GOLD.read_text(encoding="utf-8")
    bad = run("", model_checks(model)) + run("", cs_checks(model, *texts))
    # can-fail: the old law, a spliced golden row, and each C# fix taken out must go red
    old = load_model()
    old.seen = lambda c, m, d=1.0: old.seen_old(c, m)
    red_old = [n for n, ok in model_checks(old) if not ok]
    ok = any(n.startswith("retune: opacity of 4 m") for n in red_old)
    print(("PASS " if ok else "FAIL ") + "can-fail: the 2026-11-12 law goes red: " + "; ".join(red_old)[:160]); bad += not ok
    spliced = texts[4].replace(str(model.golden_rows()[4][2]) + "f", "0.11111f", 1)
    ok = not [g for n, g in cs_checks(model, texts[0], texts[1], texts[2], texts[3], spliced, texts[5], texts[6])
              if n.startswith("golden table")][0]
    print(("PASS " if ok else "FAIL ") + "can-fail: a spliced golden row goes red"); bad += not ok
    for name, idx, old_s, new_s in [
        ("BuildingMetres taken out of Begin", 1, "BuildingMetres(t", "ItemOnly(t"),
        ("the wet floor back to the original ground", 2, "DryTerrainFor(", "OriginalGround("),
        ("the sun-shadow patch taken out", 1, '"Verse.SectionLayer_SunShadows"', '"Verse.SectionLayer_Things"'),
    ]:
        t = list(texts)
        if old_s not in t[idx]:
            print("FAIL can-fail %s: '%s' not found" % (name, old_s)); bad += 1; continue
        t[idx] = t[idx].replace(old_s, new_s)
        reds = [n for n, ok2 in cs_checks(model, *t) if not ok2]
        ok = len(reds) > 0
        print(("PASS " if ok else "FAIL ") + "can-fail: %s goes red (%s)" % (name, "; ".join(reds)[:120])); bad += not ok
    print("RESULT " + ("GREEN" if not bad else "RED %d" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
