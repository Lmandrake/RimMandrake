#!/usr/bin/env python3
"""STYLE_READBACK_PROBE_ANY_BUILT_THING -- offline gate for the any-building style reader (Hose/StyleReadback.cs).

No bridge call read Thing.StyleDef or the drawn texture of a faucet, sprinkler head or pipe pole (list_things and
inspect_string omit style; HoseStyleProbe's place: verb refuses non-reel defs), so MODERN_FITTINGS StyleDef/texPath rows
stayed UNMEASURED. This gate checks, without the game:

  R1  StyleReadback.StyleRow(string "x,z") exists as a public static string method (the jawa/static_call door)
  R2  HoseProbe dispatches "stylerow:x,z" to the same reader (the HoseProbe door)
  R3  the reader is NOT gated on a styled def (no IsStyled call; any Building/Blueprint/Frame on the cell is reported)
  R4  each row carries def, rawStyle, style, look, graphicPath and drawnTex
  R5  the drawn texture is read off the material the thing draws at its rotation (Graphic.MatAt(Rotation).mainTexture)
  R6  HoseStyleProbe's row is the same reader's row (one definition of a style row)
  R7  StyleReadback.cs is in the csproj Compile list (EnableDefaultCompileItems is false)
  R8  the committed RimMandrakeFlowWorks.dll is built from these sources: its .srchash lists StyleReadback.cs, every listed
      source hash matches the file on disk, the "# dll:" line matches the DLL's own bytes, and the DLL names StyleRow
  R9  the live proof (northstar/style_readback_proof.py) reads the faucet, sprinkler head and pipe pole Modern styles
  C1  can-fail: a reader body that calls IsStyled, and a srchash with one source hash altered, are both caught

  python3 selftest_style_readback.py      # exit 0 PASS, 1 FAIL
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
READER = os.path.join(SRC, "Hose", "StyleReadback.cs")
PROBE = os.path.join(SRC, "Hose", "HoseProbe.cs")
STYLE_PROBE = os.path.join(SRC, "Hose", "HoseStyleProbe.cs")
CSPROJ = os.path.join(SRC, "RimMandrake_FlowWorks.csproj")
DLL = os.path.join(HERE, "Assemblies", "RimMandrakeFlowWorks.dll")
STAMP = DLL + ".srchash"
LIVE = os.path.join(HERE, "northstar", "style_readback_proof.py")
FIELDS = ["def", "rawStyle", "style", "look", "graphicPath", "drawnTex"]

fails = []


def check(name, ok, detail=""):
    print("%-4s %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
    if not ok:
        fails.append(name)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def method_body(src, name):
    """The brace-balanced body of the first method called `name` (None when absent)."""
    m = re.search(r"\b%s\s*\([^)]*\)\s*\{" % re.escape(name), src)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(src) and depth:
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    return src[m.end():i - 1]


def reader_gated(src):
    """True when StyleRow / StyleRowOn would refuse a def that is not a styled def."""
    body = (method_body(src, "StyleRow") or "") + (method_body(src, "StyleRowOn") or "")
    return "IsStyled" in body or "not a styled def" in body


def stamp_problems(stamp_text, base, dll_bytes):
    """[] when every source line's sha256 matches the file under `base` and the '# dll:' line matches dll_bytes."""
    probs = []
    seen_dll = False
    for ln in stamp_text.splitlines():
        if ln.startswith("# dll:"):
            seen_dll = True
            if ln.split(":", 1)[1].strip() != hashlib.sha256(dll_bytes).hexdigest():
                probs.append("dll bytes differ from # dll:")
            continue
        if not ln.strip() or ln.startswith("#"):
            continue
        sha, rel = ln.split(None, 1)
        p = os.path.normpath(os.path.join(base, rel.replace("\\", "/")))
        if not os.path.exists(p):
            probs.append("missing " + rel)
            continue
        with open(p, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != sha:
                probs.append("source changed since build: " + rel)
    if not seen_dll:
        probs.append("no # dll: line")
    return probs


def main():
    reader = read(READER)
    probe = read(PROBE)
    sprobe = read(STYLE_PROBE)

    check("R1 static StyleRow(string) door", re.search(r"public static string StyleRow\(string \w+\)", reader) is not None)
    check("R2 HoseProbe stylerow: verb", re.search(r'cmd\.StartsWith\("stylerow:"\)\)\s*return StyleReadback\.StyleRowOn\(map, cmd\.Substring\(9\)\)', probe) is not None)
    check("R3 no styled-def gate", not reader_gated(reader))
    row = method_body(reader, "Row") or ""
    missing = [f for f in FIELDS if '\\"%s\\":' % f not in row]
    check("R4 row fields", not missing, "missing %s" % missing if missing else "")
    tex = method_body(reader, "TexOf") or ""
    check("R5 drawn tex from MatAt(Rotation)", "MatAt(t.Rotation)" in tex and "mainTexture" in tex)
    check("R6 HoseStyleProbe uses the same row", re.search(r"StyleRow\(Thing t\)\s*=>\s*StyleReadback\.Row\(t\)", sprobe) is not None)
    check("R7 csproj compiles StyleReadback.cs", '<Compile Include="Hose\\StyleReadback.cs" />' in read(CSPROJ))

    with open(DLL, "rb") as f:
        dll = f.read()
    stamp = read(STAMP)
    probs = stamp_problems(stamp, SRC, dll)
    listed = any(ln.rstrip().endswith("Hose/StyleReadback.cs") or ln.rstrip().endswith("Hose\\StyleReadback.cs") for ln in stamp.splitlines())
    names = b"StyleReadback" in dll and b"StyleRow" in dll and b"SpawnStyled" in dll
    check("R8 DLL built from these sources", listed and not probs and names,
          "listed=%s names=%s %s" % (listed, names, probs[:4]))

    live = read(LIVE) if os.path.exists(LIVE) else ""
    want = ["RM_PipeFaucet_Modern", "RM_SprinklerHead_Modern", "RM_PipePole_Modern", "StyleReadback", "StyleRow"]
    check("R9 live proof reads the three Modern fittings", all(w in live for w in want),
          "missing %s" % [w for w in want if w not in live])

    # C1 can-fail: the instruments must see a planted defect
    planted = reader.replace("IntVec3? c = ParseCell(arg);", "IntVec3? c = ParseCell(arg); if (!HoseLook.IsStyled(null)) return null;", 1)
    bad_stamp = re.sub(r"^[0-9a-f]{64}(?= )", "0" * 64, stamp, count=1, flags=re.M)
    check("C1 can-fail (gate + stamp)", planted != reader and reader_gated(planted) and bool(stamp_problems(bad_stamp, SRC, dll)))

    print("VERDICT:", "FAIL " + ", ".join(fails) if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
