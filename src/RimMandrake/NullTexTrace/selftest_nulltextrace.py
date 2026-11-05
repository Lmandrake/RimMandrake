#!/usr/bin/env python3
"""selftest_nulltextrace.py -- offline proof for the NullTexTrace mod (WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR).

    python3 src/RimMandrake/NullTexTrace/selftest_nulltextrace.py

No game and no bridge. It checks:
  1. the mod installs from a Mod constructor (load time, before the menu) and patches Unity's internal 12-argument
     GUI.DrawTexture funnel with a prefix that never skips the original;
  2. it writes through UnityEngine.Debug.Log (Verse.Log has a message cap) and never calls Verse's Log;
  3. the line formats in the C# are the ones nulltex_log_check.py parses (rendered from the C# literals);
  4. the committed DLL is the build of the committed source (.srchash "# dll:" and source lines);
  5. About.xml: packageId mandrake.rm.nulltextrace, a Harmony dependency;
  6. nulltex_log_check.judge() gives PASS / FAIL / UNMEASURED on synthetic logs, and 0 null calls is never a FAIL;
  7. the live_proofs file runs the log check under python3, with no bridge site line, on a list naming MenuShell
     and NullTexTrace.
Exit 0 when every check passes.
"""
import hashlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ITEM = "WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR"
CS = os.path.join(HERE, "Source", "NullTexTrace.cs")
DLL = os.path.join(HERE, "Assemblies", "NullTexTrace.dll")
STAMP = DLL + ".srchash"
ABOUT = os.path.join(HERE, "About", "About.xml")
PROOFS = os.path.join(REPO, "infrastructure", "state", "live_proofs", ITEM + ".txt")
sys.path.insert(0, HERE)
import nulltex_log_check as lc  # noqa: E402

fails = []


def check(ok, label, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (("  -- " + detail) if detail and not ok else ""))
    if not ok:
        fails.append(label)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


src = open(CS, encoding="utf-8").read()
code = re.sub(r"//[^\n]*", "", src)  # comments out: they may name things the code must not do

# 1. load-time install, the 12-arg funnel, a prefix that never returns false
check(re.search(r"class NullTexTraceMod\s*:\s*Mod\b", code) is not None, "a Verse Mod subclass")
check(re.search(r"public NullTexTraceMod\(ModContentPack content\)\s*:\s*base\(content\)\s*\{\s*NullTexTrace\.Install\(\);",
                code) is not None, "its constructor calls Install (runs during LoadAllActiveMods, before the menu)")
args = re.search(r"TargetArgs\s*=\s*\{([^}]*)\}", code)
want = ["Rect", "Texture", "ScaleMode", "bool", "float", "Color", "Color", "Color", "Color", "Vector4", "Vector4", "bool"]
got = re.findall(r"typeof\((\w+)\)", args.group(1)) if args else []
check(got == want, "TargetArgs is the internal 12-arg GUI.DrawTexture signature", "got %s" % got)
check('AccessTools.Method(typeof(GUI), "DrawTexture", TargetArgs)' in code, "patches GUI.DrawTexture by that signature")
check(re.search(r"Patch\(m, prefix:", code) is not None and "postfix" not in code and "transpiler" not in code,
      "a prefix only")
check(re.search(r"private static void Prefix\(Texture __1\)", code) is not None,
      "the prefix is void (cannot skip the original) and binds the texture by position")
check("ev.type != EventType.Repaint" in code, "records under the engine's own Repaint condition")

# 2. Debug.Log, never Verse's capped Log
check("UnityEngine.Debug.Log(" in code, "writes through UnityEngine.Debug.Log")
check(re.search(r"(?<![\w.])Log\.(Message|Warning|Error)\(", code) is None, "never calls Verse.Log (message cap)")

# 3. formats: render each C# Debug.Log template with sample values and parse it back
tag = re.search(r'Tag = "([^"]*)"', code).group(1)
check(tag == lc.TAG, "the C# tag is the parser's tag", repr(tag))
check('"installed target=" + Target +' in code and '" rimthemes=" + Active("aRandomKiwi.RimThemes")' in code
      and '" menushell=" + Active("mandrake.rut.menushell")' in code, "installed line carries both list flags")
check('"caller #" + ByCaller.Count + " at n=" + n + " state=" + state' in code
      and '" longEvent=" + longEvent + ": " + string.Join(" <- ", kept)' in code, "caller line template")
check('"summary n=" + n + " callers=" + ByCaller.Count + " dropped=" + _dropped' in code
      and '" top: " + string.Join(" || ", top)' in code and '.Select(kv => kv.Key + " x" + kv.Value)' in code,
      "summary line template")
check('"NOT installed: "' in code, "a failed install says so")
sample = "\n".join([
    tag + "installed target=UnityEngine.GUI.DrawTexture(...) rimthemes=True menushell=True",
    tag + "caller #1 at n=1 state=Entry longEvent=False: aRandomKiwi.RimThemes.UI_BackgroundMain_Patch.Prefix "
          "[RimThemes] <- RimWorld.UI_BackgroundMain.BackgroundOnGUI [Assembly-CSharp]",
    tag + "summary n=1 callers=1 dropped=0 top: aRandomKiwi.RimThemes.UI_BackgroundMain_Patch.Prefix [RimThemes] x1",
])
p = lc.parse(sample)
check(p["installed"] == (True, True) and len(p["callers"]) == 1 and p["summary"] is not None
      and p["summary"][2][0][1] == 1, "the parser reads every rendered template", repr(p))

# 4. the committed DLL is the build of the committed source
stamp = open(STAMP, encoding="utf-8").read().splitlines()
dll_line = [x for x in stamp if x.startswith("# dll: ")]
check(dll_line and dll_line[0].split()[-1] == sha(DLL), ".srchash # dll: matches the DLL bytes")
src_lines = [x.split() for x in stamp if x and not x.startswith("#")]
check(src_lines == [[sha(CS), "NullTexTrace.cs"]], ".srchash source line matches NullTexTrace.cs", repr(src_lines))

# 5. About.xml
about = ET.parse(ABOUT).getroot()
check(about.findtext("packageId") == "mandrake.rm.nulltextrace", "packageId mandrake.rm.nulltextrace")
deps = [li.findtext("packageId") for li in about.find("modDependencies")]
check("brrainz.harmony" in deps, "depends on Harmony")

# 6. judge on synthetic logs
I = tag + "installed target=X rimthemes=True menushell=True\n"
RT = "aRandomKiwi.RimThemes.UI_BackgroundMain_Patch.Prefix [RimThemes]"
OTHER = "VBE.Something.Draw [VanillaBackgroundsExpanded]"
C1 = tag + "caller #1 at n=1 state=Entry longEvent=False: " + RT + " <- RimWorld.UIRoot_Entry.DoMainMenu\n"
C2 = tag + "caller #2 at n=4 state=Entry longEvent=True: " + OTHER + "\n"


def S(n, *top, dropped=0):
    return tag + "summary n=%d callers=%d dropped=%d top: " % (n, len(top), dropped) + " || ".join("%s x%d" % t for t in top) + "\n"


cases = [
    ("no mod", "Bridge token: x\n", "A1", lc.UNMEASURED),
    ("not installed", tag + "NOT installed: overload not found\n", "A1", lc.UNMEASURED),
    ("wrong list", tag + "installed target=X rimthemes=False menushell=True\n" + C1, "A1", lc.UNMEASURED),
    ("0 calls A1", I, "A1", lc.UNMEASURED),
    ("0 calls A2", I, "A2", lc.UNMEASURED),
    ("A1 named", I + C1 + S(1, (RT, 1)), "A1", lc.PASS),
    ("A1 unmanaged only", I + tag + "caller #1 at n=1 state=Entry longEvent=False: "
                                    "<no managed caller above GUI.DrawTexture>\n", "A1", lc.FAIL),
    ("A2 RimThemes top", I + C1 + C2 + S(1, (RT, 1)) + S(10, (RT, 8), (OTHER, 2)), "A2", lc.PASS),
    ("A2 last summary wins", I + C1 + C2 + S(1, (RT, 1)) + S(10, (OTHER, 7), (RT, 3)), "A2", lc.FAIL),
    ("A2 no summary", I + C1, "A2", lc.UNMEASURED),
    ("A2 only the n=1 summary", I + C1 + S(1, (RT, 1)), "A2", lc.UNMEASURED),
    ("A2 tie", I + C1 + C2 + S(10, (RT, 5), (OTHER, 5)), "A2", lc.UNMEASURED),
    ("A2 dropped could outrank", I + C1 + S(100, (RT, 40), dropped=50), "A2", lc.UNMEASURED),
]
for name, text, clause, want_code in cases:
    got_code, lines = lc.judge(text, clause)
    check(got_code == want_code, "judge: %s -> %s" % (name, want_code), "got %s %s" % (got_code, lines))
_, lines = lc.judge(I + C1 + C2 + S(10, (OTHER, 7), (RT, 3)), "A2")
check(any(OTHER in x and "real one" in x for x in lines), "a refuting A2 names the real top caller")

# 7. live_proofs
pl = open(PROOFS, encoding="utf-8").read().splitlines()
proofs = {m.group(1): m.group(2) for m in (re.match(r"live-proof (A\d): (.*)", x) for x in pl) if m}
for cl in ("A1", "A2"):
    check(proofs.get(cl, "").startswith("python3 src/RimMandrake/NullTexTrace/nulltex_log_check.py %s" % cl),
          "live-proof %s is the python3 log check" % cl, proofs.get(cl, "<none>"))
check(not any(x.startswith("live-site") for x in pl), "no bridge site-prep line")
mods = [m.strip() for x in pl if x.startswith("live-mods:") for m in x.split(":", 1)[1].split(",")]
check("MenuShell" in mods and "NullTexTrace" in mods, "live-mods names MenuShell and NullTexTrace", repr(mods))

print("%d FAILED" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
