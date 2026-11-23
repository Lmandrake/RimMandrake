#!/usr/bin/env python3
"""selftest_flowworks_pawn_own_picture_cut.py — RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON.

WHY: at his FlowWorks walk (2026-11-22) the owner rejected the "water sheet" on a colonist in a liquid: two blue blobs,
smaller than her and off her body. The cause (design/specs/2026-11-22-pawn-in-liquid-look/design.md section 1):
RM_SubmergeDraw.CoverPawn painted r.SilhouetteGraphic, which for a humanlike is the LIFE STAGE's generic 64 px icon, not
her picture. By card he picked concept A: her own picture, cut at the liquid's surface, the line at body landmarks.

This test holds the fix offline:
  1. the production draw never paints SilhouetteGraphic; it opens a cut on her own render tree (PawnRenderTree.Draw),
     cuts every node at one world line (GenDraw.DrawMeshNowOrLater), turns vanilla's far-zoom atlas cache off for a
     wet pawn, keeps the realtime gate that hides a pawn wholly under an opaque liquid, and every patch obeys the
     setting pitSubmergeCutEnabled;
  2. the pure rule (Source/Superdeep/RM_PawnCutMath.cs; its tables read from the C# file) gives, in a python twin:
     1 m of water on a 1.75 m colonist at her waist, not her chin; deeper never shows more; body size sets the line;
     a lying pawn is never cut (GPT: a line across a lying body cuts her face); a carried pawn is whole; wholly under a
     clear liquid = tinted whole, under an opaque one = hidden.
The behaviour is also checked in C# by SelfTest PawnCutChecks (--dotnet runs it on Windows).

CAN IT FAIL: on the parent commit it is RED for the reason (CoverPawn paints SilhouetteGraphic; no RM_PawnCutMath).
--mutate plants each fault (straight-metres table, a cut lying body, the icon back, the cache left on, the setting
ignored) and every one must go RED.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_pawn_own_picture_cut.py [--rev <sha>] [--mutate] [--dotnet]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DRAW = "src/RimMandrake/FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs"
MATH = "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PawnCutMath.cs"
CSPROJ = "src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj"
UL = "src/RimMandrake/FlowWorks/Source/Superdeep/RM_UnderLiquid.cs"


def read(rel: str, rev: str | None) -> str:
    if rev is None:
        p = REPO / rel
        return p.read_text(encoding="utf-8") if p.exists() else ""
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{rel}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


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
        else:
            out.append(ch); i += 1
    return "".join(out)


def table(src: str, name: str) -> list[float] | None:
    m = re.search(r"float\[\]\s+" + name + r"\s*=\s*\{([^}]*)\}", src)
    if not m:
        return None
    return [float(x.strip().rstrip("f")) for x in m.group(1).split(",") if x.strip()]


def const(src: str, name: str) -> float | None:
    m = re.search(r"const\s+float\s+" + name + r"\s*=\s*([0-9.]+)f", src)
    return float(m.group(1)) if m else None


# ── the python twin of RM_PawnCutMath ─────────────────────────────────────────

def lerp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return ys[i - 1] + (ys[i] - ys[i - 1]) * t
    return ys[-1]


def picture_share(tables, humanlike, level, height):
    if not level > 0:
        return 0.0
    if not height > 0:
        return 1.0
    d = level / height
    if d >= 1:
        return 1.0
    return lerp(tables["HumanHeight"], tables["HumanPicture"], d) if humanlike else d


def decide(tables, lying, carried, humanlike, level, height, lie_h, clarity):
    """-> (mode, line_share, tint_strength); mode in Whole, Cut, Tinted, Hidden."""
    if carried or not level > 0:
        return "Whole", 0.0, 0.0
    clear = clarity > 0
    if lying and tables.get("lying_cut"):   # a planted fault: the lying body cut like a standing one
        return "Cut", picture_share(tables, humanlike, level, height), 1.0
    if lying:
        s = min(1.0, level / lie_h) if lie_h > 0 else 1.0
        if s >= 1:
            return ("Tinted" if clear else "Hidden"), 0.0, 1.0
        k = s if clear else s * tables["LyingOpaqueTint"]
        return ("Tinted" if k > 0 else "Whole"), 0.0, k
    p = picture_share(tables, humanlike, level, height)
    if p <= 0:
        return "Whole", 0.0, 0.0
    if p >= 1:
        return ("Tinted" if clear else "Hidden"), 0.0, 1.0
    return "Cut", p, 1.0


# ── checks ───────────────────────────────────────────────────────────────────

def check_source(draw: str, csproj: str, ul: str) -> list[str]:
    bad = []
    d = mask_comments(draw)
    if not d:
        return ["RM_SubmergeDraw.cs is missing"]
    if "SilhouetteGraphic" in d:
        bad.append("CoverPawn paints the life stage's generic icon (SilhouetteGraphic), not her own picture")
    if not re.search(r"\[HarmonyPatch\(typeof\(PawnRenderTree\), nameof\(PawnRenderTree\.Draw\)\)\]", d):
        bad.append("no cut opens on her own render tree (PawnRenderTree.Draw)")
    if not re.search(r"\[HarmonyPatch\(typeof\(GenDraw\), nameof\(GenDraw\.DrawMeshNowOrLater\), new\[\] \{ typeof\(Mesh\), typeof\(Matrix4x4\)", d):
        bad.append("her nodes are not cut where they are drawn (GenDraw.DrawMeshNowOrLater)")
    if not re.search(r'\[HarmonyPatch\(typeof\(PawnRenderer\), "ParallelGetPreRenderResults"\)\][\s\S]{0,600}?ref bool disableCache[\s\S]{0,300}?disableCache = true', d):
        bad.append("vanilla's far-zoom atlas cache stays on for a wet pawn (one quad, nothing to cut)")
    # live matrix 2026-11-22: at far zoom vanilla draws a humanlike from the atlas and never calls PawnRenderTree.Draw, so
    # a wet mark set only there was never set and the atlas stayed on (the pawn drawn whole): RenderPawnAt must mark it
    if not re.search(r"\[HarmonyPatch\(typeof\(PawnRenderer\), nameof\(PawnRenderer\.RenderPawnAt\)\)\][\s\S]{0,400}?internal static class Patch_RM_SubmergePawnWet[\s\S]{0,600}?RM_SubmergeDraw\.NoteWet\(", d):
        bad.append("a wet pawn first seen at far zoom keeps vanilla's atlas (the wet mark is set only inside PawnRenderTree.Draw, which the atlas path never reaches)")
    # live matrix 2026-11-22: wound overlays (PawnOverlayDrawer.DoDrawCall) draw by Graphics.DrawMesh, outside GenDraw, so
    # they stayed bright red and uncut on a pawn in a liquid: that one call must pass the same cut
    if not (re.search(r'typeof\(PawnOverlayDrawer\), "DoDrawCall"[\s\S]{0,1500}?nameof\(RM_SubmergeDraw\.DrawOverlayMesh\)', d)
            and re.search(r"public static void DrawOverlayMesh\([\s\S]{0,300}?if \(!DrawCutNode\(", d)):
        bad.append("a pawn's wound overlays are drawn outside the cut (PawnOverlayDrawer.DoDrawCall's Graphics.DrawMesh): red wounds show under tar")
    for cls in ("Patch_RM_SubmergePawnCut", "Patch_RM_SubmergePawnNode", "Patch_RM_SubmergePawnNoCache", "Patch_RM_SubmergePawnWet", "Patch_RM_SubmergePawnOverlay"):
        m = re.search(r'PatchFeature\("[^"]*", typeof\([^)]*\), "pitSubmergeCutEnabled"\)\]\s*internal static class ' + cls + r"\b", d)
        if not m:
            bad.append(f"{cls} does not obey the setting pitSubmergeCutEnabled")
    if not re.search(r"static bool BeginRealtime[\s\S]*?RealtimeVerdict\.Hidden[\s\S]*?return false;", d):
        bad.append("the realtime gate no longer hides a pawn wholly under an opaque liquid")
    body = re.search(r"internal static void BeginPawnCut\([\s\S]*?\n\t\t\}", d)
    b = body.group(0) if body else ""
    if not b:
        bad.append("BeginPawnCut is missing")
    else:
        if not re.search(r"parms\.DrawNow \|\| parms\.Portrait \|\| parms\.Cache \|\| parms\.Statue", b):
            bad.append("a portrait, atlas or statue render would be cut")
        if "RM_PawnCutMath.Decide(" not in b:
            bad.append("the cut does not ask the pure rule (RM_PawnCutMath.Decide)")
        # live matrix 2026-11-22: a hare in 0.5 m of tar (exactly her height) passed the realtime gate's strict boundary and
        # a Hidden decision fell back to drawing her whole: the cut itself must draw nothing when the rule says Hidden
        if re.search(r"mode == RM_PawnCutMath\.Mode\.Whole \|\| mode == RM_PawnCutMath\.Mode\.Hidden\)\s*\{\s*return;", b):
            bad.append("a pawn the rule hides (wholly under an opaque liquid) is drawn whole when the realtime gate lets her through")
        if "ParentHolder as Corpse" not in b:
            bad.append("a carried pawn would take her carrier's liquid (only a corpse's holder counts)")
    node = re.search(r"internal static bool DrawCutNode\([\s\S]*?\n\t\t\}", d)
    n = node.group(0) if node else ""
    if not re.search(r"ClipMesh\(mesh, s, matrix, cut\.lineZ, true\)", n) or not re.search(r"if \(cut\.clear\)[\s\S]*?ClipMesh\(mesh, s, matrix, cut\.lineZ, false\)", n):
        bad.append("the node is not drawn as its part above the line plus (clear liquids only) its part below")
    if 'Compile Include="Superdeep\\RM_PawnCutMath.cs"' not in csproj:
        bad.append("RM_PawnCutMath.cs is not compiled into the mod")
    if "CoverFromOwnPicture" in mask_comments(ul):
        bad.append("the retired own-picture-cover rule (CoverFromOwnPicture) is still in RM_UnderLiquid")
    return bad


def check_rule(tables) -> list[str]:
    bad = []
    if tables.get("HumanHeight") is None or tables.get("HumanPicture") is None or tables.get("LyingOpaqueTint") is None:
        return ["RM_PawnCutMath has no landmark tables (HumanHeight, HumanPicture, LyingOpaqueTint)"]
    hh, hp = tables["HumanHeight"], tables["HumanPicture"]
    if len(hh) != len(hp) or hh[0] != 0 or hh[-1] != 1 or hp[0] != 0 or hp[-1] != 1:
        bad.append("the landmark tables do not run 0..1 knot for knot")
    if any(b <= a for a, b in zip(hh, hh[1:])) or any(b <= a for a, b in zip(hp, hp[1:])):
        bad.append("a landmark table is not rising")
    lie = tables["CorpseMetres"]
    p = picture_share(tables, True, 1.0, 1.75)
    if not (0.19 < p < 0.476):
        bad.append(f"1 m of water on a 1.75 m colonist is not at her waist (picture share {p:.3f}; chin 0.52)")
    if not picture_share(tables, True, 0.9 * 1.75, 1.75) > 0.52:
        bad.append("at the drowning line (0.9 H) her mouth is not under")
    for human in (True, False):
        prev = 0.0
        for i in range(1, 35):
            s = picture_share(tables, human, i * 0.05, 1.75)
            if not (prev < s <= 1):
                bad.append(f"deeper shows more ({human}, {i * 0.05:.2f} m)")
                break
            prev = s
    if not (picture_share(tables, False, 0.5, 0.5) == 1 and picture_share(tables, False, 0.5, 1.75) > picture_share(tables, False, 0.5, 4.0) > 0):
        bad.append("body size does not set the line (small whole, huge least)")
    for i in range(41):
        for c in (0.45, 0.0):
            m, line, _ = decide(tables, True, False, True, i * 0.05, 1.75, lie, c)
            if m == "Cut":
                bad.append(f"a lying body is cut by a horizontal line at {i * 0.05:.2f} m (it would cut her face)")
                break
        else:
            continue
        break
    if decide(tables, False, True, True, 1.5, 1.75, lie, 0.0)[0] != "Whole" or decide(tables, True, True, True, 1.5, 1.75, lie, 0.45)[0] != "Whole":
        bad.append("a carried pawn takes her carrier's liquid")
    if decide(tables, False, False, True, 2.0, 1.75, lie, 0.45)[0] != "Tinted":
        bad.append("wholly under clear water is not her whole picture, dimmed")
    if decide(tables, False, False, True, 2.0, 1.75, lie, 0.0)[0] != "Hidden" or decide(tables, True, False, True, 1.0, 1.75, lie, 0.0)[0] != "Hidden":
        bad.append("wholly under tar is not hidden")
    if decide(tables, False, False, True, 1.0, 1.75, lie, 0.0)[0] != "Cut":
        bad.append("waist deep in tar is not cut at the line")
    return bad


def load_tables(math: str, ul: str) -> dict:
    return {"HumanHeight": table(math, "HumanHeight"), "HumanPicture": table(math, "HumanPicture"),
            "LyingOpaqueTint": const(math, "LyingOpaqueTint"), "CorpseMetres": const(ul, "CorpseMetres") or 0.3}


def run(rev: str | None) -> list[str]:
    draw, math, csproj, ul = read(DRAW, rev), read(MATH, rev), read(CSPROJ, rev), read(UL, rev)
    return check_source(draw, csproj, ul) + check_rule(load_tables(math, ul))


def mutate() -> int:
    draw, math, csproj, ul = read(DRAW, None), read(MATH, None), read(CSPROJ, None), read(UL, None)
    t = load_tables(math, ul)
    faults = {
        "straight metres (no landmarks)": lambda: check_rule({**t, "HumanPicture": list(t["HumanHeight"])}),
        "a lying body cut": lambda: check_rule({**t, "lying_cut": True}),
        "the icon back": lambda: check_source(draw.replace("internal static bool DrawCutNode(", "Graphic g = r.SilhouetteGraphic;\n\t\tinternal static bool DrawCutNode(", 1), csproj, ul),
        "cache left on": lambda: check_source(draw.replace("disableCache = true;", "disableCache = false;"), csproj, ul),
        "setting ignored": lambda: check_source(draw.replace('"Pit contents under liquid (pawn nodes)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitSubmergeCutEnabled"', '"Pit contents under liquid (pawn nodes)", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "none"'), csproj, ul),
        "opaque lower part drawn": lambda: check_source(draw.replace("if (cut.clear)\n", "if (true)\n", 1), csproj, ul),
        "not compiled": lambda: check_source(draw, csproj.replace("RM_PawnCutMath.cs", "RM_PawnCutMathX.cs"), ul),
        "hidden drawn whole": lambda: check_source(draw.replace("if (mode == RM_PawnCutMath.Mode.Whole)\n", "if (mode == RM_PawnCutMath.Mode.Whole || mode == RM_PawnCutMath.Mode.Hidden)\n", 1), csproj, ul),
        "overlays outside the cut": lambda: check_source(draw.replace("RM_SubmergeDraw.DrawOverlayMesh", "RM_SubmergeDraw.DrawOverlayMeshX"), csproj, ul),
        "wet mark only in the tree": lambda: check_source(draw.replace("RM_SubmergeDraw.NoteWet(", "RM_SubmergeDraw.NoteWetX("), csproj, ul),
    }
    missed = 0
    for name, f in faults.items():
        red = f()
        print(("RED   " if red else "MISSED") + f"  planted: {name}" + (f"  -> {red[0]}" if red else ""))
        missed += 0 if red else 1
    clean = run(None)
    print(("GREEN " if not clean else "RED   ") + " unplanted (the real build)")
    return 1 if missed or clean else 0


def dotnet() -> int:
    b = subprocess.run([sys.executable, str(REPO / "src/RimMandrake/Utils/winbuild.py"),
                        "src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj"], capture_output=True, text=True)
    if b.returncode != 0:
        print("UNMEASURED: the SelfTest did not build:\n" + b.stdout[-800:] + b.stderr[-400:])
        return 2
    exe = next((p for p in (Path.home() / ".dotnet/dotnet", Path("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe"),
                            Path("/mnt/c/Program Files/dotnet/dotnet.exe")) if p.exists()), None)
    d = Path("/mnt/d/ClaudeWork/rimmandrake/build/FlowWorks/src/RimMandrake/FlowWorks/Source/SelfTest")
    if exe is None or not (d / "bin/Release/net8.0/RimMandrakeFlowWorks.SelfTest.dll").exists():
        print("UNMEASURED: no dotnet or no built SelfTest dll")
        return 2
    r = subprocess.run([str(exe), "bin/Release/net8.0/RimMandrakeFlowWorks.SelfTest.dll", "--only", "PawnCut_*,PitLook1114_drowned_body_cover_is_the_pawns_own_picture"],
                       cwd=str(d), capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if l.startswith(("ok", "FAIL", "fail")) or "passed" in l))
    return 0 if r.returncode == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rev", help="check the files as they are at this commit (the parent must be RED)")
    ap.add_argument("--mutate", action="store_true", help="plant each fault and require RED")
    ap.add_argument("--dotnet", action="store_true", help="also run SelfTest PawnCutChecks on Windows dotnet")
    a = ap.parse_args()
    if a.mutate:
        return mutate()
    bad = run(a.rev)
    for b in bad:
        print("FAIL  " + b)
    rc = 1 if bad else 0
    if not bad:
        print("PASS  pawn in a liquid: her own picture cut at the surface (source shape + pure rule)")
    if a.dotnet and rc == 0:
        rc = dotnet()
    return rc


if __name__ == "__main__":
    sys.exit(main())
