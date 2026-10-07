#!/usr/bin/env python3
"""Selftest for lint_def_type_refs.py: a lint that finds nothing must first prove it can find something.

Builds a throwaway src/ tree with one planted defect of every kind plus clean controls, runs the lint over it, and
requires exactly the planted findings (and none for the controls). Then runs it over the real repo as a smoke check that
it still judges thousands of references (a clean bill from a lint that judged nothing is not a pass).
Run: python3 src/RimMandrake/Utils/selftest_lint_def_type_refs.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_def_type_refs as L  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def w(root, rel, text, binary=False):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as fh:
        fh.write(text)


def build(root):
    # mod A: explicit-compile csproj, one file left out, a stale DLL
    w(root, "Alpha/About/About.xml", "<ModMetaData><packageId>t.alpha</packageId></ModMetaData>")
    w(root, "Alpha/Source/Alpha.csproj", '<Project><PropertyGroup><AssemblyName>Alpha</AssemblyName><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>'
      '<ItemGroup><Compile Include="Good.cs" /><Compile Include="Fresh.cs" /><Compile Include="RM_Bare.cs" /></ItemGroup></Project>')
    w(root, "Alpha/Source/Good.cs", '''using System;
namespace Test.Alpha
{
    // class GhostInComment : ThingComp
    public class GoodComp { string s = "class GhostInString {"; public class Inner {} }
    public abstract class AbstractBase { }
    public static class StaticHelper { }
    public enum Mode { A }
    public class Outer { public class Nested { } }
}
''')
    w(root, "Alpha/Source/Orphan.cs", "namespace Test.Alpha { public class OrphanComp { } }\n")
    w(root, "Alpha/Source/Fresh.cs", "namespace Test.Alpha { public class FreshComp { } }\n")
    w(root, "Alpha/Source/RM_Bare.cs", "public class RM_BareGood { }\n")
    w(root, "Alpha/Assemblies/Alpha.dll", b"Alpha\0Test.Alpha\0GoodComp\0Inner\0AbstractBase\0StaticHelper\0Mode\0Outer\0Nested\0RM_BareGood\0", binary=True)
    # mod B: no dependency on Alpha
    w(root, "Beta/About/About.xml", "<ModMetaData><packageId>t.beta</packageId></ModMetaData>")
    w(root, "Beta/Defs/D.xml", '''<Defs>
  <ThingDef><defName>RM_WreckDensity_X</defName><comps>
    <li Class="Test.Alpha.GoodComp">a</li>
    <li Class="Test.Alpha.MissingComp">b</li>
    <li Class="Test.Alpha.OrphanComp">c</li>
    <li Class="Test.Alpha.FreshComp">d</li>
    <li Class="Test.Alpha.AbstractBase">e</li>
    <li Class="Test.Alpha.StaticHelper">f</li>
    <li Class="Test.Alpha.Outer+Nested">g</li>
    <li Class="Test.Alpha.Outer.Nested">h</li>
    <li Class="RimWorld.CompProperties_Foo">vanilla</li>
    <li Class="Verse.Something">vanilla</li>
  </comps>
  <compClass>RM_BareGood</compClass>
  <thingClass>RM_BareMissing</thingClass>
  <densityClass>RM_WreckDensity_X</densityClass>
  <tracker>Test.Alpha.TextMissing</tracker>
  </ThingDef>
</Defs>''')
    w(root, "Beta/Patches/P.xml", '''<Patch><Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef/comps/li[@Class="Test.Alpha.XpathMissing"]</xpath>
<value><li Class="Test.Alpha.GoodComp"/></value></Operation></Patch>''')


def main():
    with tempfile.TemporaryDirectory() as td:
        build(td)
        L.SRC = L.REPO = td
        idx = L.Index(td)
        names = set(idx.decl)
        check("declares nested + namespaced types", {"Test.Alpha.GoodComp", "Test.Alpha.GoodComp+Inner", "Test.Alpha.Outer+Nested", "RM_BareGood"} <= names, str(sorted(names)))
        check("comment/string text is not a declaration", not any("Ghost" in n for n in names), str(sorted(names)))
        findings, stats = L.lint(idx, None, True, td)
        got = {(k, n) for _s, k, _r, n, _c, _d in findings}
        want = {
            ("UNRESOLVED", "Test.Alpha.MissingComp"),
            ("NOT_COMPILED", "Test.Alpha.OrphanComp"),
            ("NOT_IN_DLL", "Test.Alpha.FreshComp"),
            ("NOT_INSTANTIABLE", "Test.Alpha.AbstractBase"),
            ("NOT_INSTANTIABLE", "Test.Alpha.StaticHelper"),
            ("UNRESOLVED", "RM_BareMissing"),
            ("UNRESOLVED", "Test.Alpha.TextMissing"),
            ("UNRESOLVED", "Test.Alpha.XpathMissing"),
            ("NO_DEPENDENCY", "Test.Alpha.GoodComp"),
        }
        for k, n in sorted(want):
            check("planted %s %s found" % (k, n), (k, n) in got, "got %s" % sorted(got))
        extra = {(k, n) for k, n in got if (k, n) not in want and k != "NO_DEPENDENCY"}
        check("no finding beyond the planted ones (controls clean)", not extra, str(sorted(extra)))
        check("vanilla / def-name controls were skipped", ("UNRESOLVED", "RM_WreckDensity_X") not in got and not any(n.startswith(("RimWorld.", "Verse.")) for _k, n in got))
        check("nested type resolves both spellings", ("UNRESOLVED", "Test.Alpha.Outer+Nested") not in got and ("UNRESOLVED", "Test.Alpha.Outer.Nested") not in got)
        check("clean control GoodComp is not flagged beyond the dependency warning", not [f for f in findings if f[3] == "Test.Alpha.GoodComp" and f[1] != "NO_DEPENDENCY"])
        # a DLL that does not carry its own name is UNMEASURED, not a verdict
        w(td, "Alpha/Assemblies/Alpha.dll", b"garbage", binary=True)
        L._dll_cache.clear()
        f2, _ = L.lint(idx, None, True, td)
        check("a DLL failing its sanity probe reads UNMEASURED, not NOT_IN_DLL", any(f[1] == "UNMEASURED_DLL" for f in f2) and not any(f[1] == "NOT_IN_DLL" for f in f2))
    # smoke over the real repo
    L.SRC = os.path.join(L.REPO if False else os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "src")
    L.REPO = os.path.dirname(L.SRC)
    L._dll_cache.clear(); L._dll_found.clear()
    real = L.Index(L.SRC)
    rf, rs = L.lint(real, None, True, L.SRC)
    check("real repo: judges thousands of references", rs["judged"] > 1000 and rs["resolved"] > 1000, str(rs))
    check("real repo: indexes thousands of types", len(real.decl) > 2000, str(len(real.decl)))
    check("real repo: EnvironmentalHazards types are in the index", "RimMandrake.EnvironmentalHazards.RM_AxisKernel" in real.decl)
    bad = [f for f in rf if f[0] == "FAIL"]
    check("real repo: no FAIL-severity findings", not bad, "; ".join("%s %s %s" % (f[1], f[3], f[2]) for f in bad[:5]))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
