#!/usr/bin/env python3
"""selftest_rerun_relation.py: the promises of design/specs/2026-11-21-rerun-only-related/boundary.md, one test of each
promise's name (boundary_check.py), on a throwaway git repository with one planted mod. Item
RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203.

No test reaches a launcher, a live game, the ledger or the repo's own files: every repository is a temp folder, and
main() checks that infrastructure/state/ledger/events/ is byte-for-byte unchanged after the run.

  --mutate relation_ignored   plants the fault "the build match ignores the relation" (the rule before 2026-11-21:
                              any change to the mod reruns every row); the run must go red
  --mutate parts_untouched    plants "a declared part is never touched"; the run must go red
  --mutate all_untouched      plants "the relation says untouched for every check"; the run must go red
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_match as BM        # noqa: E402
import rerun_relation as RR     # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOD = "Planted"
FAILS = []
SEEN = []

VALIDATION_0 = '''
ROWS = {"sc_a": ["A_row_one"], "sc_b": ["B_row_one"]}
SHIPPED = {"alpha": "1", "beta": "2"}


def helper_a(x):
    return x + 1


def helper_b(x):
    return x * 2


def scene_a(rows):
    rows.append(("A_row_one", helper_a(1)))


def scene_b(rows):
    rows.append(("B_row_one", helper_b(1)))


def floor_reset():
    return [k for k in SHIPPED]
'''

SCENES_0 = {"scenes": [{"id": "sc_a", "what": "a"}, {"id": "sc_b", "what": "b"}]}


def table(extra=None):
    t = {
        "sc_a": {"id": "sc_a", "kind": "live_minimal", "stage": "6", "tier": "t", "file": "src/RimMandrake/Planted/validation.py",
                 "entry": "scene_a", "reads": ["src/RimMandrake/Planted/Source/A.cs",
                                               "design/concepts/Planted/scenes.json"]},
        "sc_b": {"id": "sc_b", "kind": "live_minimal", "stage": "6", "tier": "t", "file": "src/RimMandrake/Planted/validation.py",
                 "entry": "scene_b", "reads": ["src/RimMandrake/Planted/Defs/B.xml", "src/RimMandrake/Planted/Source/B.cs",
                                               "design/concepts/Planted/scenes.json"]},
        "sc_c": {"id": "sc_c", "kind": "live_minimal", "stage": "6", "tier": "t",
                 "reads": ["src/RimMandrake/Planted/Source/C.cs"]},
        "sc_blank": {"id": "sc_blank", "kind": "live_minimal", "stage": "6", "tier": "t"},
        "sc_whole": {"id": "sc_whole", "kind": "live_minimal", "stage": "6", "tier": "t", "exercises": ["*"]},
        "sc_full": {"id": "sc_full", "kind": "live_full", "stage": "6", "why_full_list": "breadth",
                    "file": "src/RimMandrake/Planted/walk.py"},
    }
    t.update(extra or {})
    return t


class Tree:
    """A throwaway git repository with one mod; commit() returns the commit id."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="rerun_relation_selftest_")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "selftest@example.invalid")
        self.git("config", "user.name", "selftest")
        self.write("src/RimMandrake/Planted/validation.py", VALIDATION_0)
        self.write("src/RimMandrake/Planted/walk.py", "def scene_walk():\n    return 1\n")
        for c in "ABC":
            self.write("src/RimMandrake/Planted/Source/%s.cs" % c, "class %s { int v = 0; }\n" % c)
        self.write("src/RimMandrake/Planted/Defs/B.xml", "<Defs><ThingDef><defName>B</defName></ThingDef></Defs>\n")
        self.write("src/RimMandrake/Planted/Defs/Loose.xml", "<Defs/>\n")
        self.write("src/RimMandrake/Planted/Assemblies/P.dll", "dll0")
        self.write("src/RimMandrake/Planted/Assemblies/P.dll.srchash", "# dll: 0\n00 A.cs\n00 B.cs\n00 C.cs\n")
        self.write("design/concepts/Planted/scenes.json", json.dumps(SCENES_0, indent=1))
        self.set_table(table())
        self.base = self.commit("base")

    def git(self, *a):
        return subprocess.run(["git", "-C", self.root] + list(a), capture_output=True, text=True, timeout=60,
                              check=True).stdout.strip()

    def write(self, rel, text):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.root, rel)) as f:
            return f.read()

    def set_table(self, tests):
        self.write("design/concepts/Planted/version/test_table.json", json.dumps({"tests": tests}, indent=1))

    def commit(self, msg):
        self.git("add", "-A", ".")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def edit(self, rel, old, new):
        text = self.read(rel)
        if old not in text:   # a scenario whose edit misses tests an empty change and passes or fails for nothing
            raise AssertionError("edit of %s: %r is not in the file" % (rel, old))
        self.write(rel, text.replace(old, new))

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def relate(tr, rows, tests=None):
    tests = tests or json.loads(tr.read("design/concepts/Planted/version/test_table.json"))["tests"]
    return RR.relate(tr.root, MOD, tests, rows)


def all_rows(sha, tests=None):
    return {t: {"mod_sha": sha} for t in (tests or table())}


def ok(name, cond, why=""):
    SEEN.append(name)
    print("%s  %s%s" % ("ok   " if cond else "FAIL ", name, "" if cond else ": %s" % (why,)))
    if not cond:
        FAILS.append(name)
    return cond


# ---- the promises ---------------------------------------------------------------------------------------------------

def t_declared_paths_are_exercises_reads_and_file():
    paths, whole = RR.declared({"exercises": ["src/X/e.cs"], "reads": ["src/X/r.py", "src/RimMandrake (prose)"],
                                "file": "src/X/f.py"}, "M")
    ok("declared-paths-are-exercises-reads-and-file: all three, a bracketed note cut, a parent of the mod is whole",
       paths == ["src/X/e.cs", "src/X/f.py", "src/X/r.py"] and whole, (paths, whole))
    paths, whole = RR.declared({"reads": ["src/RimMandrake/M/Defs/"]}, "M")
    ok("declared-paths-are-exercises-reads-and-file: a folder covers the files under it, and is not the whole mod",
       RR.covers(paths[0], "src/RimMandrake/M/Defs/a.xml") and not whole, (paths, whole))


def t_untouched_row_counts():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/Source/A.cs", "v = 0", "v = 1")
        new = tr.commit("A.cs")
        res = relate(tr, all_rows(tr.base))
        ok("untouched-row-counts: a change to A.cs leaves sc_b and sc_c untouched",
           res["rows"]["sc_b"]["state"] == "untouched" and res["rows"]["sc_c"]["state"] == "untouched", res["rows"])
        # the build match counts the untouched rows though the mod hash moved (the 203 case: red before 2026-11-21)
        walk = {"mod_hash": "sha256:new", "game_build": "1.6", "active_mods": ["x"]}
        last = {t: {"mod_sha": tr.base, "mod_hash": "sha256:old", "game_build": "1.6", "active_mods": ["x"],
                    "tier": "t"} for t in ("sc_a", "sc_b")}
        tests = [(t, table()[t]) for t in ("sc_a", "sc_b")]
        bm = BM.compare(tests, last, walk, lambda t: (["x"], None), relation=res)
        ok("untouched-row-counts: the build match counts sc_b on the new build and reruns only sc_a",
           bm["rerun"] == ["sc_a"] and bm["rows"]["sc_b"]["counts"], (bm["rerun"], bm["rows"]))
        del new
    finally:
        tr.close()


def t_touched_check_reruns():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/Source/A.cs", "v = 0", "v = 1")
        tr.edit("src/RimMandrake/Planted/Defs/B.xml", "<defName>B</defName>", "<defName>B2</defName>")
        tr.commit("A.cs and B.xml")
        res = relate(tr, all_rows(tr.base))
        touched = sorted(res["touched"])
        ok("touched-check-reruns: a change to one C# file and one def reruns only the checks that declare them "
           "(and the whole-mod ones)", touched == ["sc_a", "sc_b", "sc_full", "sc_whole"], touched)
    finally:
        tr.close()


def t_undeclared_change_reruns_nothing_and_is_listed():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/Defs/Loose.xml", "<Defs/>", "<Defs><X/></Defs>")
        tr.commit("loose")
        res = relate(tr, all_rows(tr.base))
        part = sorted(set(res["touched"]) - {"sc_whole", "sc_full"})
        ok("undeclared-change-reruns-nothing-and-is-listed: no declared check reruns, the file is listed",
           part == [] and res["undeclared"] == ["src/RimMandrake/Planted/Defs/Loose.xml"], (part, res["undeclared"]))
    finally:
        tr.close()


def t_shipped_csharp_reruns_the_live_checks_that_name_none():
    name = "shipped-csharp-reruns-the-live-checks-that-name-none"
    stamp = "# project: RimMandrake/Planted/Source/P.csproj\n# dll: %s\n%s A.cs\n00 B.cs\n00 C.cs\n"
    src = "src/RimMandrake/Planted/"
    extra = {
        # the Pyrelands shape: a scene script and scenes.json, no C# anywhere
        "sc_py": {"id": "sc_py", "kind": "live_minimal", "stage": "6", "tier": "t", "file": src + "validation.py",
                  "entry": "scene_a", "reads": [src + "validation.py", "design/concepts/Planted/scenes.json"]},
        "sc_def": {"id": "sc_def", "kind": "live_minimal", "stage": "6", "tier": "t", "reads": [src + "Defs/B.xml"]},
        "sc_folder": {"id": "sc_folder", "kind": "live_minimal", "stage": "6", "tier": "t", "reads": [src + "Source/Kernel/"]},
        "sc_selftest": {"id": "sc_selftest", "kind": "live_minimal", "stage": "6", "tier": "t",
                        "reads": [src + "Source/SelfTest/T.cs"]},
        "off_py": {"id": "off_py", "kind": "offline", "stage": "3", "file": src + "validation.py", "entry": "scene_a"},
    }

    def tree():
        tr = Tree()
        tr.write(src + "Source/P.csproj", "<Project/>\n")
        tr.write(src + "Source/Kernel/K.cs", "class K { int v = 0; }\n")
        tr.write(src + "Source/SelfTest/T.csproj", "<Project/>\n")
        tr.write(src + "Source/SelfTest/T.cs", "class T { int v = 0; }\n")
        tr.write(src + "Assemblies/P.dll.srchash", stamp % ("0", "00") + "00 Kernel/K.cs\n")
        tr.set_table(table(extra))
        return tr, tr.commit("the planted mod, its project and its offline program")

    def read(*edits):
        tr, base = tree()
        try:
            for rel, a, b in edits:
                tr.edit(rel, a, b)
            tr.commit("the change")
            return relate(tr, all_rows(base, table(extra)))
        finally:
            tr.close()

    res = read((src + "Source/A.cs", "v = 0", "v = 1"))
    un = sorted(set(res["unreadable"]) - {"sc_blank"})
    ok(name + ": a C# change reruns every live check that names no shipped C# (a def check and a check that names only "
       "an offline program among them), and no offline check", un == ["sc_def", "sc_py", "sc_selftest"] and
       res["rows"]["off_py"]["state"] == "untouched", (un, res["rows"]["off_py"]))
    ok(name + ": a check that names other C#, by file or by folder, keeps its own answer",
       all(res["rows"][t]["state"] == "untouched" for t in ("sc_b", "sc_c", "sc_folder"))
       and res["rows"]["sc_a"]["state"] == "touched", res["rows"])
    ok(name + ": the reading names the changed C#", res["rows"]["sc_py"]["files"] == [src + "Source/A.cs"] and
       "Source/A.cs" in res["rows"]["sc_py"]["why"], res["rows"]["sc_py"])
    res = read((src + "Source/SelfTest/T.cs", "v = 0", "v = 1"), (src + "Defs/Loose.xml", "<Defs/>", "<Defs><X/></Defs>"))
    un = sorted(set(res["unreadable"]) - {"sc_blank"})
    ok(name + ": an offline program and a def nobody declares rerun no live check", un == [] and all(
       res["rows"][t]["state"] == "untouched" for t in ("sc_py", "sc_b", "sc_def")), (un, res["rows"]))
    res = read((src + "validation.py", "def scene_b(rows):", "def scene_b(rows, x=1):"))
    ok(name + ": a scene-script change reruns only the check that reaches it", res["rows"]["sc_py"]["state"] ==
       "untouched" and res["rows"]["sc_b"]["state"] == "touched", (res["rows"]["sc_py"], res["rows"]["sc_b"]))
    # a declaration in exercises.json makes the relation readable again
    tr, base = tree()
    try:
        tr.write("design/concepts/Planted/version/exercises.json", json.dumps({"checks": {"sc_py": [src + "Source/B.cs"]}}))
        base = tr.commit("declared")
        tr.edit(src + "Source/A.cs", "v = 0", "v = 1")
        tr.commit("A.cs")
        res = relate(tr, all_rows(base, table(extra)))
        ok(name + ": a declared check is related by its declaration", res["rows"]["sc_py"]["state"] == "untouched" and
           res["rows"]["sc_def"]["state"] == "unreadable", (res["rows"]["sc_py"], res["rows"]["sc_def"]))
    finally:
        tr.close()


def t_rebuilt_dll_relates_by_its_srchash():
    name = "rebuilt-dll-relates-by-its-srchash"
    src = "src/RimMandrake/Planted/"
    live_def = {"sc_def": {"id": "sc_def", "kind": "live_minimal", "stage": "6", "tier": "t", "reads": [src + "Defs/B.xml"]}}
    tr = Tree()
    try:
        tr.set_table(table(live_def))
        tr.base = tr.commit("a check that names no C#")
        tr.write(src + "Assemblies/P.dll", "dll1")
        tr.write(src + "Assemblies/P.dll.srchash", "# dll: 1\n11 A.cs\n00 B.cs\n00 C.cs\n")
        tr.commit("the DLL rebuilt from source that landed before")
        res = relate(tr, all_rows(tr.base, table(live_def)))
        ok(name + ": the check that declares the recompiled file reruns, and so does the live check that names no C#; "
           "the check on another file does not", res["rows"]["sc_a"]["state"] == "touched" and
           res["rows"]["sc_def"]["state"] == "unreadable" and res["rows"]["sc_c"]["state"] == "untouched", res["rows"])
    finally:
        tr.close()
    tr = Tree()
    try:
        tr.set_table(table(live_def))
        tr.base = tr.commit("a check that names no C#")
        tr.write(src + "Assemblies/P.dll", "dll1")
        tr.write(src + "Assemblies/P.dll.srchash", "# dll: 1\n00 A.cs\n00 B.cs\n00 C.cs\n")
        tr.commit("the DLL rebuilt, no source moved")
        res = relate(tr, all_rows(tr.base, table(live_def)))
        ok(name + ": a rebuild of the same source touches no part check", all(
            res["rows"][t]["state"] == "untouched" for t in ("sc_a", "sc_b", "sc_c", "sc_def")), res["rows"])
    finally:
        tr.close()


def t_unreadable_relation_reruns_alone():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/Defs/Loose.xml", "<Defs/>", "<Defs><X/></Defs>")
        tr.commit("loose")
        rows = all_rows(tr.base)
        rows["sc_c"] = {"mod_sha": "0123456789abcdef"}              # a commit git cannot resolve
        res = relate(tr, rows)
        ok("unreadable-relation-reruns-alone: a check that declares nothing, and a row on an unknown commit, are "
           "unreadable; the others keep their answers",
           sorted(res["unreadable"]) == ["sc_blank", "sc_c"] and res["rows"]["sc_a"]["state"] == "untouched"
           and res["rows"]["sc_b"]["state"] == "untouched", (res["unreadable"], res["rows"]))
    finally:
        tr.close()


def t_whole_mod_check_reruns_on_any_change():
    tr = Tree()
    try:
        tr.write("src/RimMandrake/Planted/Assemblies/P.dll", "dll1")
        tr.commit("dll only")
        res = relate(tr, all_rows(tr.base))
        ok("whole-mod-check-reruns-on-any-change: a DLL-only change reruns the whole-mod and full-list checks only",
           sorted(res["touched"]) == ["sc_full", "sc_whole"], res["touched"])
    finally:
        tr.close()


def t_whole_mod_check_skips_hashignored():
    """A change only to files the mod's .hashignore lists (they never ship; the deployed mod_hash does not move) reruns no
    whole-mod or full-list check; the same change beside a shipped file still does (GSS in-game visit 3, 2026-11-21:
    three review/ docs sent his full-list walk back on an unchanged mod_hash)."""
    tr = Tree()
    try:
        tr.write("src/RimMandrake/Planted/.hashignore", "# never ships\nreview\nart_*\n")
        tr.write("src/RimMandrake/Planted/review/KEYSHEET.md", "v0\n")
        base = tr.commit("hashignore + review doc")
        tr.write("src/RimMandrake/Planted/review/KEYSHEET.md", "v1\n")
        tr.write("src/RimMandrake/Planted/art_source_a.psd", "x\n")
        tr.commit("review doc and art source only")
        res = relate(tr, all_rows(base))
        ok("whole-mod-check-skips-hashignored: a change only under .hashignore paths reruns no whole-mod or full-list "
           "check", not set(res["touched"]) & {"sc_full", "sc_whole"}, res["touched"])
        tr.write("src/RimMandrake/Planted/Defs/Loose.xml", "<Defs><!-- shipped --></Defs>\n")
        tr.commit("a shipped def beside it")
        res = relate(tr, all_rows(base))
        ok("whole-mod-check-skips-hashignored: a shipped file beside the ignored ones still reruns both",
           {"sc_full", "sc_whole"} <= set(res["touched"]), res["touched"])
    finally:
        tr.close()
    # a check's own script is never skipped: Explosive Knockback visit 5 (2026-11-23), its walk's validation.py never ships
    # and voided the barrage row that never reads it; ignored, it must still rerun the walk that does
    tr = Tree()
    try:
        tr.write("src/RimMandrake/Planted/.hashignore", "walk.py\nselftest_*\n")
        tr.write("src/RimMandrake/Planted/walk.py", "v = 0\n")
        base = tr.commit("walk.py ignored")
        tr.write("src/RimMandrake/Planted/walk.py", "v = 1\n")
        tr.commit("the full-list check's own script")
        res = relate(tr, all_rows(base))
        ok("whole-mod-check-skips-hashignored: an ignored script reruns the check that declares it, and only that one",
           set(res["touched"]) & {"sc_full", "sc_whole"} == {"sc_full"}, res["touched"])
    finally:
        tr.close()


def t_csharp_relates_by_source_file():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/Source/C.cs", "v = 0", "v = 2")
        tr.write("src/RimMandrake/Planted/Assemblies/P.dll", "dll2")
        tr.write("src/RimMandrake/Planted/Assemblies/P.dll.srchash", "# dll: 2\n00 A.cs\n00 B.cs\n11 C.cs\n")
        tr.commit("C.cs, rebuilt")
        res = relate(tr, all_rows(tr.base))
        part = sorted(set(res["touched"]) - {"sc_whole", "sc_full"})
        ok("csharp-relates-by-source-file: C.cs reruns sc_c alone; the DLL and .srchash touch nothing by themselves",
           part == ["sc_c"] and not res["undeclared"], (part, res["undeclared"]))
    finally:
        tr.close()


PROOF_CS = '''using System;
using System.Collections.Generic;
namespace Planted
{
    public static partial class Proof
    {
        private sealed class Scene
        {
            public string name;
            public int a;
        }

        private static readonly Dictionary<string, Scene> scenes = new Dictionary<string, Scene>();
        internal static readonly HashSet<int> NoHarm = new HashSet<int>();

        public static string Stage(string arg)
        {
            var s = new Scene { name = arg };
            scenes[arg] = s;
            return Build(s);
        }

        private static int Helper(int x) => x + 1;

        private static string Build(Scene s)
        {
            switch (s.name)
            {
                case "alpha":
                    s.a = Helper(1);
                    return "A";
                case "beta":
                    // a comment with { a brace
                    if (NoHarm.Contains(7)) { return "B{" + '}'; }
                    return @"B "" {";
                case "gamma":
                    goto case "beta";
                case "reset":
                    scenes.Clear();
                    return "R";
            }
            return null;
        }
    }
}
'''

PROOF_OTHER_CS = "namespace Planted { public static class Other { public static int Use() => 1; } }\n"


def _proof_tests():
    f = "src/RimMandrake/Planted/Source/Proof.cs"
    return {k: {"id": k, "kind": "live_minimal", "stage": "6", "tier": "t", "file": f, "entry": e,
                "reads": [f, "src/RimMandrake/Planted/Source/Other.cs"]}
            for k, e in (("sc_alpha", "alpha"), ("sc_beta", "beta"), ("sc_gamma", "gamma"), ("sc_delta", "delta"))}


def _proof_case(edits, other=None):
    """-> the touched checks after the edits [(old, new)] to Proof.cs alone, or the error. other: Other.cs's text at both
    commits (it never changes, so it touches nothing by itself)."""
    tr = Tree()
    try:
        tr.write("src/RimMandrake/Planted/Source/Proof.cs", PROOF_CS)
        tr.write("src/RimMandrake/Planted/Source/Other.cs", other if other is not None else PROOF_OTHER_CS)
        tests = _proof_tests()
        tr.set_table(tests)
        base = tr.commit("proof base")
        for a, b in edits:
            if a not in tr.read("src/RimMandrake/Planted/Source/Proof.cs"):
                return "edit target missing: %r" % a
            tr.edit("src/RimMandrake/Planted/Source/Proof.cs", a, b)
        tr.commit("proof edit")
        res = relate(tr, all_rows(base, tests), tests)
        return sorted(res["touched"])
    finally:
        tr.close()


def t_csharp_relates_by_scene_section():
    """One proof file holds every scene (ExplosiveKnockback RM_KnockbackProof.cs, 2026-11-23: a change to sc_spared's
    case alone sent all 54 scene checks of visit 5 back). Each scenario reads its touched set against the one it owes."""
    allc = ["sc_alpha", "sc_beta", "sc_delta", "sc_gamma"]
    cases = [
        ("an edit inside case beta reruns beta and gamma (goto case beta), and delta (no case of its own)",
         [('return "A";\n                case "beta":\n                    // a comment with { a brace\n'
           '                    if (NoHarm.Contains(7))', 'return "A";\n                case "beta":\n'
           '                    // a comment with { a brace\n                    if (NoHarm.Contains(8))')],
         None, ["sc_beta", "sc_delta", "sc_gamma"]),
        ("a new Scene field that only case alpha uses reruns alpha (and delta)",
         [("public int a;", "public int a;\n            public int b;"),
          ("s.a = Helper(1);", "s.a = Helper(1);\n                    s.b = 2;")], None, ["sc_alpha", "sc_delta"]),
        ("a helper only case alpha calls reruns alpha (and delta)",
         [("x + 1;", "x + 2;")], None, ["sc_alpha", "sc_delta"]),
        ("a comment-only edit inside case beta reruns nothing but delta",
         [("a comment with { a brace", "a comment with no brace")], None, ["sc_delta"]),
        ("the bridge method Stage, called from outside the file, reruns every check",
         [("scenes[arg] = s;", "scenes[arg] = s; s.a = 0;")], None, allc),
        ("a Scene field initializer runs for every scene: every check",
         [("public int a;", "public int a = 3;")], None, allc),
        ("case reset, which no check's entry names, reruns every check",
         [('return "R";', 'return "R2";')], None, allc),
        ("case alpha starts writing a shared static case beta reads: alpha, beta, gamma (and delta)",
         [("s.a = Helper(1);", "s.a = Helper(1);\n                    NoHarm.Add(7);")], None, allc),
        ("a helper another C# file of the mod names reruns every check",
         [("x + 1;", "x + 2;")], "namespace Planted { public static class Other { public static int Use() => "
                                 "Proof.Helper(1); } }\n", allc),
        ("a new public method no check reaches (a bridge entry, called from outside) reruns every check",
         [("x + 1;", "x + 1;\n        public static int Spare() => 2;")], None, allc),
        ("a file that no longer parses (one brace short) relates whole",
         [('return null;\n        }', 'return null;\n')], None, allc),
        ("a using line relates whole", [("using System;\n", "using System;\nusing System.Linq;\n")], None, allc),
    ]
    for why, edits, other, want in cases:
        got = _proof_case(edits, other)
        ok("csharp-relates-by-scene-section: %s" % why, got == want, "got %s, want %s" % (got, want))
    # every .cs file of the repo read on 2026-11-23 (2,646); the six unread ones opened a verbatim string on "" (@""")
    u = RR.cs_units('class K { string v = @""" q"" x"; int w; }\n')
    ok("csharp-relates-by-scene-section: a verbatim string that opens on \"\" (@\"\"\" ...) reads",
       u is not None and "K/w" in u, sorted(u or {}))


AFTER_CS = '''namespace Planted
{
    public static partial class After
    {
        private sealed class Scene { public string name; }

        private static int Ret(int x) => x + 1;
        private static int Brk(int x) => x + 2;
        private static int LaneHelper(int x) => x + 3;
        private static string Lane(Scene s) => "L" + LaneHelper(1);
        private static int Build(string def, int x, string stuff = null) => x;

        private static string Build(Scene s)
        {
            int pre = Ret(0);
            switch (s.name)
            {
                case "ret":
                    return "R" + Ret(pre);
                case "brk":
                    Brk(1);
                    break;
                case "cond":
                    if (pre > 0) return "C";
                    break;
                case "jump":
                    goto case "brk";
                case "loop":
                    yield_like();
                    return "Y";
                case "rec":
                    return Build(new Scene { name = "lane_x" });
                case "place":
                    Build("Wall", 1);
                    Build("Door", 2, "Wood");
                    return "P";
                case "group":
                    System.Func<Scene, string> f = Build;
                    return f(s);
                case "blk":
                {
                    System.Func<int> g = () => { return Ret(2); };
                    return "B" + g();
                }
                case "ifblk":
                    if (pre > 9) { return "I"; }
                    else { Brk(3); }
                    return "J";
                case "blkif":
                {
                    if (pre > 9) { return "K"; }
                }
            }
            if (s.name.StartsWith("lane_"))
            {
                return Lane(s);
            }
            return "unknown " + s.name;
        }

        private static void yield_like() { }
    }
}
'''

LOCALFN_CS = '''namespace Planted
{
    public static partial class After
    {
        private static int LaneHelper(int x) => x + 3;

        private static string Build(string n)
        {
            switch (n)
            {
                case "ret":
                    return Local();
            }
            string Local() { return "L" + LaneHelper(1); }
            return null;
        }
    }
}
'''


def _after_case(text, edits, entries):
    """-> the touched checks after the edits [(old, new)] to After.cs, or the error."""
    f = "src/RimMandrake/Planted/Source/After.cs"
    tr = Tree()
    try:
        tr.write(f, text)
        tests = {"sc_" + e: {"id": "sc_" + e, "kind": "live_minimal", "stage": "6", "tier": "t", "file": f, "entry": e,
                             "reads": [f]} for e in entries}
        tr.set_table(tests)
        base = tr.commit("after base")
        for a, b in edits:
            if a not in tr.read(f):
                return "edit target missing: %r" % a
            tr.edit(f, a, b)
        tr.commit("after edit")
        return sorted(relate(tr, all_rows(base, tests), tests)["touched"])
    finally:
        tr.close()


def t_csharp_code_after_a_switch_runs_when_a_section_falls_out():
    """Code after a method's switch runs for a scene only when its section can end without return or throw
    (ExplosiveKnockback visit 2, 2026-11-26: Build's `if (s.name.StartsWith("settings_sweep_")) return SettingsSweep(s);`
    after the switch sent all 64 scene checks back for a change in SweepLane that only sc_settings_sweep reaches)."""
    ents = ["ret", "brk", "cond", "jump", "loop", "rec", "place", "group", "blk", "ifblk", "blkif"]
    falls = ["sc_blkif", "sc_brk", "sc_cond", "sc_group", "sc_jump", "sc_rec"]
    cases = [
        ("a helper only the code after the switch calls reruns the sections that can fall out or call the method again "
         "(an overload of its name with another count of arguments is no such call; a method group may be)",
         AFTER_CS, [("x + 3;", "x + 4;")], ents, falls),
        ("an edit to the code after the switch reruns the same sections",
         AFTER_CS, [('return "unknown " + s.name;', 'return "unknown: " + s.name;')], ents, falls),
        ("an edit before the switch reruns every section", AFTER_CS, [("int pre = Ret(0);", "int pre = Ret(1);")], ents,
         ["sc_" + e for e in sorted(ents)]),
        ("a helper of the returning section reruns it and the sections that reach it (rec through Build, pre)",
         AFTER_CS, [("x + 1;", "x + 5;")], ents, ["sc_" + e for e in sorted(ents)]),
        ("a local function after the switch, called by a returning section, keeps the code after it in the method",
         LOCALFN_CS, [("x + 3;", "x + 4;")], ["ret"], ["sc_ret"]),
    ]
    for why, text, edits, entries, want in cases:
        got = _after_case(text, edits, entries)
        ok("csharp-code-after-a-switch-runs-when-a-section-falls-out: %s" % why, got == want,
           "got %s, want %s" % (got, want))


VERD_CS = ("namespace Planted\n{\n    public static class Verd\n    {\n        public static int Off(int x) => Deep.In(x);\n"
           "        public static int Other() => 2;\n    }\n}\n")
DEEP_CS = ("namespace Planted\n{\n    public static class Deep\n    {\n        public static int In(int y) => y;\n"
           "        public static int Out() => 4;\n    }\n}\n")
# a type only case beta names; its members carry words case alpha reaches (Off, a, Helper) without the type
PROBE_CS = ("namespace Planted\n{\n    public sealed class Probe : MonoBehaviour\n    {\n        public static int Off;\n"
            "        public static string[] Paths = { \"a\" };\n        public static bool Begin(int n) => n > 0;\n"
            "        public static string Tag() => \"Begin\";\n        public void OnDestroy() { Off = 0; }\n"
            "        public static int Pick(string k)\n        {\n            switch (k)\n            {\n"
            "                case \"Begin\":\n                    return 1;\n            }\n            return 0;\n        }\n"
            "    }\n}\n")
# an offline program of its own project, the shipped DLL not built from it, whose type name case alpha's code holds
SELFTEST_CS = ("namespace PlantedTest\n{\n    internal static class Helper\n    {\n        public static int fail;\n"
               "        public static void Main() { fail = 1; }\n    }\n}\n")


def t_csharp_reads_the_types_it_names():
    """A declared C# file reads the mod's C# files that define the types it names, at either commit (ExplosiveKnockback,
    2026-11-23: RM_KnockbackVerdicts.cs and the partial class's RM_KnockbackProof_StageThree.cs, where sc_frame_probe_check's
    RM_FrameProbe lives, are declared by no check; the whole-file relation had rerun them by the proof file alone)."""
    cases = [
        ("a changed member case alpha calls reruns alpha (and delta, which anchors nowhere)",
         ("int x) => Deep.In(x);", "int x) => Deep.In(x) + 1;"), ["sc_alpha", "sc_delta"], "Verd.cs"),
        ("a changed member of a file the named file names, which case alpha reaches through it, reruns alpha",
         ("int y) => y;", "int y) => y + 1;"), ["sc_alpha", "sc_delta"], "Deep.cs"),
        ("a member of that file nothing reaches reruns delta alone", ("() => 4;", "() => 5;"), ["sc_delta"], "Deep.cs"),
        ("a changed member no check's section calls reruns delta alone", ("() => 2;", "() => 3;"), ["sc_delta"], "Verd.cs"),
        ("a using line in the named file relates whole", ("namespace Planted\n", "using System;\nnamespace Planted\n"),
         ["sc_alpha", "sc_beta", "sc_delta", "sc_gamma"], "Verd.cs"),
        ("a member whose name case alpha holds, of a type case alpha never names, does not rerun alpha",
         ("public static int Off;", "public static int Off = 1;"), ["sc_delta"], "Probe.cs"),
        ("a list element whose value is a word case alpha holds does not rerun alpha", ('{ "a" }', '{ "a2" }'),
         ["sc_delta"], "Probe.cs"),
        ("a method whose string is a word case beta holds is not reached by it", ('=> "Begin";', '=> "Begin" + "!";'),
         ["sc_delta"], "Probe.cs"),
        ("a case section whose label is a word case beta holds is not reached by it", ("return 1;", "return 3;"),
         ["sc_delta"], "Probe.cs"),
        ("an engine-called member reruns the checks that name its type (beta, gamma by goto), not alpha",
         ("{ Off = 0; }", "{ Off = 2; }"), ["sc_beta", "sc_delta", "sc_gamma"], "Probe.cs"),
        ("a file of another C# project than the one the DLL is built from is no file a check names",
         ("{ fail = 1; }", "{ fail = 2; }"), [], "SelfTest/Program.cs"),
    ]
    for why, (a, b), want, name in cases:
        tr = Tree()
        try:
            tr.write("src/RimMandrake/Planted/Source/Proof.cs", PROOF_CS.replace(
                "s.a = Helper(1);", "s.a = Helper(1) + Verd.Off(1);").replace(
                "if (NoHarm.Contains(7))", "if (NoHarm.Contains(7) && Probe.Begin(1))"))
            tr.write("src/RimMandrake/Planted/Source/Probe.cs", PROBE_CS)
            tr.write("src/RimMandrake/Planted/Source/Planted.csproj", "<Project />\n")
            tr.write("src/RimMandrake/Planted/Source/SelfTest/SelfTest.csproj", "<Project />\n")
            tr.write("src/RimMandrake/Planted/Source/SelfTest/Program.cs", SELFTEST_CS)
            tr.write("src/RimMandrake/Planted/Assemblies/Planted.dll.srchash",
                     "# project: RimMandrake/Planted/Source/Planted.csproj\n# dll: 00\n11 Proof.cs\n22 Other.cs\n")
            tr.write("src/RimMandrake/Planted/Source/Other.cs", PROOF_OTHER_CS)
            tr.write("src/RimMandrake/Planted/Source/Verd.cs", VERD_CS)
            tr.write("src/RimMandrake/Planted/Source/Deep.cs", DEEP_CS)
            tests = _proof_tests()
            tr.set_table(tests)
            base = tr.commit("proof base")
            tr.edit("src/RimMandrake/Planted/Source/" + name, a, b)
            tr.commit("verd edit")
            res = relate(tr, all_rows(base, tests), tests)
            got = sorted(res["touched"])
            ok("csharp-reads-the-types-it-names: %s" % why, got == want, "got %s, want %s" % (got, want))
        finally:
            tr.close()


def t_declared_exercises_bound_the_types_named():
    """A check that anchors in no C# (a scene driven from Python) and lists the C# it exercises is related by that list,
    not whole through every file the list's types name (Gimme Some Slack, 2026-11-23: the CordBuilder.cs fix sent 75 more
    rows back, the aerial ones among them, past a declaration written so that it would not: 206 of 206 reran)."""
    src = "src/RimMandrake/Planted/Source/"
    cases = [
        ("a changed type of an undeclared file reruns the check with no list alone", "Verd.cs", ("() => 2;", "() => 3;"),
         ["sc_bare"]),
        ("a using line there reruns the check with no list alone", "Verd.cs",
         ("namespace Planted\n", "using System;\nnamespace Planted\n"), ["sc_bare"]),
        ("a change in the listed file itself reruns both", "Proof.cs", ("Helper(1)", "Helper(2)"), ["sc_bare", "sc_listed"]),
    ]
    for why, name, (a, b), want in cases:
        tr = Tree()
        try:
            tr.write(src + "Proof.cs", PROOF_CS.replace("s.a = Helper(1);", "s.a = Helper(1) + Verd.Off(1);"))
            tr.write(src + "Planted.csproj", "<Project />\n")
            tr.write("src/RimMandrake/Planted/Assemblies/Planted.dll.srchash",
                     "# project: RimMandrake/Planted/Source/Planted.csproj\n# dll: 00\n11 Proof.cs\n")
            tr.write(src + "Verd.cs", VERD_CS)
            tr.write(src + "Deep.cs", DEEP_CS)
            spec = {"kind": "live_minimal", "stage": "6", "tier": "t", "file": "src/RimMandrake/Planted/validation.py",
                    "entry": "no_such_entry"}
            tests = {"sc_listed": dict(spec, id="sc_listed", exercises=[src + "Proof.cs"]),
                     "sc_bare": dict(spec, id="sc_bare", reads=[src + "Proof.cs"])}
            tr.set_table(tests)
            base = tr.commit("listed base")
            tr.edit(src + name, a, b)
            tr.commit("listed edit")
            got = sorted(relate(tr, all_rows(base, tests), tests)["touched"])
            ok("declared-exercises-bound-the-types-named: %s" % why, got == want, "got %s, want %s" % (got, want))
        finally:
            tr.close()


def t_python_relates_by_symbol():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/validation.py", "return x + 1", "return x + 3")
        tr.edit("src/RimMandrake/Planted/validation.py", '"beta": "2"}', '"beta": "2", "gamma": "3"}')
        tr.edit("src/RimMandrake/Planted/validation.py", '"sc_b": ["B_row_one"]}',
                '"sc_b": ["B_row_one"], "sc_new": ["N_row_one"]}')
        tr.commit("helper_a, a new setting, a new scene's rows")
        res = relate(tr, all_rows(tr.base))
        ok("python-relates-by-symbol: a change in helper_a reruns sc_a (scene_a calls it), not sc_b; entries added to "
           "two tables rerun no other check", res["rows"]["sc_a"]["state"] == "touched"
           and res["rows"]["sc_b"]["state"] == "untouched", res["rows"])
    finally:
        tr.close()
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/validation.py", '"beta": "2"}', '"beta": "9"}')
        tr.commit("a shipped value changed")
        tt = table({"sc_floor": {"id": "sc_floor", "kind": "live_minimal", "stage": "6", "tier": "t",
                                 "file": "src/RimMandrake/Planted/validation.py", "entry": "floor_reset"}})
        res = relate(tr, all_rows(tr.base, tt), tests=tt)
        ok("python-relates-by-symbol: a changed entry of a table reruns a check that loops over the whole table",
           res["rows"]["sc_floor"]["state"] == "touched" and res["rows"]["sc_a"]["state"] == "untouched", res["rows"])
    finally:
        tr.close()


def t_python_def_name_is_no_row_id():
    """Pyrelands in-game visit 8: "RM_FurnaceBeast" in a check's own strings read as a row id, so every def of the 7,000-line
    validation.py holding that string was the check's own, and an edit to the walk reran seven other checks."""
    src = ('def scene_a(t):\n    t.spawn("RM_FurnaceBeast")\n    rows("A7_row_one")\n\n\n'
           'def scene_b(t):\n    t.spawn("RM_FurnaceBeast")\n\n\n'
           'def maker(t):\n    rows("A7_row_one")\n')
    got = RR.py_reach({"v.py": RR.py_symbols(src)}, {"scene_a"})["v.py"]
    ok("python_relates_by_symbol: a def naming the same creature is not reached", "scene_b" not in got, sorted(got))
    ok("python_relates_by_symbol: a def writing a row the anchor names still is", "maker" in got, sorted(got))


REGISTER_IDIOM = '''
def scene_a(t):
    return 1


def _register_other():
    spec = importlib.util.spec_from_file_location("other", "other.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.register(suite, types.SimpleNamespace(**globals()))


_register_other()
'''


def t_python_chain_registration_is_the_other_files():
    """Pyrelands in-game visit 8: 077f18f8b0 registered two new chains from a new file by this idiom; the added top-level call
    reads as a changed '<module>', so 32 checks of validation.py reran."""
    with_call, without = RR.py_symbols(REGISTER_IDIOM), RR.py_symbols(REGISTER_IDIOM.replace("\n_register_other()\n", "\n"))
    ok("python_relates_by_symbol: registering another file's chains changes no module-level state",
       "<module>" not in RR.py_changed(without, with_call), sorted(RR.py_changed(without, with_call)))
    ok("python_relates_by_symbol: the registration call is still a symbol of its own",
       "<call _register_other>" in RR.py_changed(without, with_call), sorted(RR.py_changed(without, with_call)))
    loop = REGISTER_IDIOM.replace('    spec = importlib.util.spec_from_file_location("other", "other.py")',
                                  '    for n in ("other", "third"):\n        spec = importlib.util.spec_from_file_location(n, n + ".py")')
    loop = loop.replace("\n    mod = ", "\n        mod = ").replace("\n    spec.l", "\n        spec.l").replace("\n    mod.r", "\n        mod.r")
    ok("python_relates_by_symbol: a loop over two files registered (5411bd360c) changes no module-level state",
       "<module>" not in RR.py_changed(with_call, RR.py_symbols(loop)), sorted(RR.py_changed(with_call, RR.py_symbols(loop))))
    other = REGISTER_IDIOM.replace("    mod.register(suite, types.SimpleNamespace(**globals()))", "    globals()['LIMIT'] = 3")
    a, b = RR.py_symbols(other.replace("\n_register_other()\n", "\n")), RR.py_symbols(other)
    ok("python_relates_by_symbol: a module-level call that does anything else still relates whole",
       "<module>" in RR.py_changed(a, b), sorted(RR.py_changed(a, b)))
    kept = REGISTER_IDIOM.replace("    mod.register(", "    suite.limit = 3\n    mod.register(")
    a, b = RR.py_symbols(kept.replace("\n_register_other()\n", "\n")), RR.py_symbols(kept)
    ok("python_relates_by_symbol: a registration that also sets something still relates whole",
       "<module>" in RR.py_changed(a, b), sorted(RR.py_changed(a, b)))


def t_json_relates_by_entry():
    tr = Tree()
    try:
        s = json.loads(tr.read("design/concepts/Planted/scenes.json"))
        s["scenes"][1]["what"] = "b, restaged"
        tr.write("design/concepts/Planted/scenes.json", json.dumps(s, indent=1))
        tr.commit("sc_b restaged")
        res = relate(tr, all_rows(tr.base))
        ok("json-relates-by-entry: restaging sc_b in scenes.json reruns sc_b, not sc_a",
           res["rows"]["sc_b"]["state"] == "touched" and res["rows"]["sc_a"]["state"] == "untouched", res["rows"])
    finally:
        tr.close()


def t_spec_change_reruns():
    tr = Tree()
    try:
        t = table()
        t["sc_c"]["command"] = "run sc_c --harder"
        t["sc_a"]["command"] = None
        tr.set_table(t)
        tr.commit("sc_c's command")
        res = relate(tr, all_rows(tr.base))
        ok("spec-change-reruns: a changed command reruns its own check only",
           res["rows"]["sc_c"]["state"] == "touched" and res["rows"]["sc_b"]["state"] == "untouched", res["rows"])
        ok("spec-change-reruns: a trailing note in brackets is the table maker's prose, not a change",
           RR.run_key({"command": "x --scene a   (minimal list; entry ABSENT)"}, "command")
           == RR.run_key({"command": "x --scene a   (minimal list; entry exists)"}, "command"))
    finally:
        tr.close()


def t_rows_from_several_builds():
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/Source/A.cs", "v = 0", "v = 1")
        mid = tr.commit("A.cs")
        tr.edit("src/RimMandrake/Planted/Source/C.cs", "v = 0", "v = 1")
        tr.commit("C.cs")
        rows = all_rows(tr.base)
        rows["sc_a"] = {"mod_sha": mid}                 # sc_a was rerun on the middle build
        res = relate(tr, rows)
        ok("rows-from-several-builds: sc_a's row on the middle build is untouched by C.cs; sc_c's on the base is "
           "touched", res["rows"]["sc_a"]["state"] == "untouched" and res["rows"]["sc_c"]["state"] == "touched",
           res["rows"])
    finally:
        tr.close()


def t_walk_not_the_source_is_one_deploy():
    d = tempfile.mkdtemp(prefix="rerun_relation_walk_")
    try:
        for side, text in (("src/RimMandrake/W", "00 A.cs\n"), ("game/W", "99 A.cs\n")):
            os.makedirs(os.path.join(d, side, "Assemblies"))
            with open(os.path.join(d, side, "Assemblies", "W.dll.srchash"), "w") as f:
                f.write(text)
        deploy, _ = BM.walk_source(d, "W", {"deployed_folder": os.path.join(d, "game", "W")})
        with open(os.path.join(d, "game/W/Assemblies/W.dll.srchash"), "w") as f:
            f.write("00 A.cs\n")
        deploy2, _ = BM.walk_source(d, "W", {"deployed_folder": os.path.join(d, "game", "W")})
        walk = {"mod_hash": "sha256:new", "game_build": "1.6", "active_mods": ["x"]}
        bm = BM.compare([("sc_a", table()["sc_a"])], {"sc_a": {"mod_sha": "abc1234", "mod_hash": "sha256:new",
                                                               "game_build": "1.6", "active_mods": ["x"], "tier": "t"}},
                        walk, lambda t: (["x"], None), relation={"rows": {}}, deploy=deploy)
        ok("walk-not-the-source-is-one-deploy: a stale walk folder names one deploy and reruns no check; a current one "
           "names none", bool(deploy) and "deploy" in deploy and deploy2 is None and bm["rerun"] == []
           and bm["deploy"] == deploy, (deploy, deploy2, bm["rerun"]))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_stale_walk_folder_still_reads_the_source_change():
    """GimmeSomeSlack in-game visit 1, 2026-11-23: the folder still held the rows' build while CordBuilder.cs had changed
    at HEAD; the match read "206 count, 0 to run ... no check reruns for this", and the relation read 206 touched."""
    rows = {t: {"mod_sha": "abc1234", "mod_hash": "sha256:old", "game_build": "1.6", "active_mods": ["x"], "tier": "t"}
            for t in ("sc_a", "sc_b", "sc_c", "sc_d")}
    walk = {"mod_hash": "sha256:old", "game_build": "1.6", "active_mods": ["x"]}
    rel = {"rows": {"sc_a": {"state": "touched", "why": "A.cs", "old": "abc1234"},
                    "sc_b": {"state": "untouched", "why": "", "old": "abc1234"},
                    "sc_c": {"state": "unreadable", "why": "no declared path", "old": "abc1234"}}}
    tests = [(t, dict(table()["sc_a"])) for t in sorted(rows)]
    stale = BM.compare(tests, rows, walk, lambda t: (["x"], None), relation=rel, deploy="deploy it")
    cur = BM.compare(tests, rows, walk, lambda t: (["x"], None), relation=rel, deploy=None)
    ok("stale-walk-folder-still-reads-the-source-change: while a deploy is owed, a row made on the folder's own build "
       "reruns when the change to the source touches it or cannot be read, the others count; a current folder's equal "
       "hash counts every row", stale["rerun"] == ["sc_a", "sc_c"] and cur["rerun"] == [], (stale["rerun"], cur["rerun"]))


def t_tier_list_of_any_install_here_counts():
    """RIMMANDRAKE_READ_TIER_LIST_FROM_EVERY_GAME_INSTALL_HERE (Pyrelands visit 7, 2026-11-23): 37 ArchSmall rows read "to
    run" because the reference came from ArchBig's older About.xml."""
    walk = {"mod_hash": "h", "game_build": "g", "active_mods": ["x"], "why": []}
    r = {"mod_hash": "h", "game_build": "g", "active_mods": ["x", "dep"], "tier": "t", "mod_sha": "s"}

    def tiers(t):
        return ["x"], None
    tiers.others = lambda t: [("ArchSmall", ["x", "dep"], None)]
    yes = BM.judge_row("c", {}, r, walk, tiers)
    no = BM.judge_row("c", {}, dict(r, active_mods=["x", "stray"]), walk, tiers)
    ok("tier-list-of-any-install-here-counts: the list on the other install counts, a list on neither does not",
       yes[0] and "ArchSmall" in yes[1] and not no[0], (yes, no))


def t_mod_list_only_reruns_related_rows():
    import maturation as M

    name = "mod-list-only-reruns-related-rows"
    tr = Tree()
    try:
        d = "design/concepts/Planted/"
        src = "src/RimMandrake/Planted/"
        tr.write(src + "About/About.xml", "<ModMetaData><packageId>test.planted</packageId><modDependencies>"
                 "<li><packageId>test.required</packageId></li></modDependencies></ModMetaData>")
        tr.write(src + "Patches/Target.xml", '<Patch><Operation MayRequire="test.target"/></Patch>')
        tests = {k: dict(table()["sc_full"], id=k) for k in ("a", "b")}
        tests["b"] = dict(tests["b"], kind="live_minimal", why_full_list=None, tier="small", mods=[])
        scenes = [{"id": "a", "mods": ["test.a"]}, {"id": "b"}]
        tr.set_table(tests)
        tr.write(d + "scenes.json", json.dumps({"scenes": scenes}))
        old = tr.commit("the rows' build before the walk switched lists")
        tr.write(d + "version/small_list.json", '{"tier":"small"}')
        tr.commit("the new walk list")
        tt = {"tests": tests}
        base = ["test.planted", "test.required", "test.target"]

        def match(before, after, specs=tt, b_before=None):
            walk = {"mod_hash": "h", "game_build": "g", "active_mods": after, "standin": "planted"}
            rows = {k: dict(test=k, mod_sha=old, mod_hash="h", game_build="g", active_mods=before,
                            tier="small", verdict="PASS", site_checked=True) for k in tests}
            if b_before is not None:
                rows["b"]["active_mods"] = b_before
            tr.write(d + "version/in_game/visit_1/rows.jsonl", "".join(json.dumps(r) + "\n" for r in rows.values()))
            tier = lambda _: (after, "planted new list unreadable" if after is None else None)
            with patch.object(BM, "walk_build", return_value=walk), patch.object(BM, "tier_lister", return_value=tier):
                return BM.check_visit(tr.root, MOD, 1, specs, "planted.rws", cache_dir=None)

        for before, after, owed, label in (
                (base + ["test.unused"], base, [], "dropping only unread mods owes zero rows"),
                (base + ["TEST.A_steam"], base, ["a"], "dropping a read mod owes only its row"),
                (base, base + ["test.a"], ["a"], "joining a read mod owes only its row"),
                (base, base + ["test.unused"], [], "joining only unread mods owes zero rows, including an empty read set"),
                (base, base[1:], ["a", "b"], "each row reads the tested mod"),
                (base, base[:1] + base[2:], ["a", "b"], "each row reads its required mods"),
                (base, base[:-1], ["a", "b"], "each row reads its patch targets")):
            res = match(before, after)
            ok(name + ": " + label, res["rerun"] == owed, "owed %s, expected %s" % (res["rerun"], owed))
        res = match(None, base, b_before=base)
        ok(name + ": unreadable old list owes only its row and says why",
           res["rerun"] == ["a"] and "old mod list" in res["rows"]["a"]["why"], res["rows"])
        res = match([], base, b_before=base)
        ok(name + ": an empty old list is said as empty",
           res["rerun"] == ["a"] and "is empty" in res["rows"]["a"]["why"], res["rows"])
        res = match(base, None)
        ok(name + ": unreadable new list owes rows and says why",
           res["rerun"] == ["a", "b"] and all("list" in x["why"] for x in res["rows"].values()), res["rows"])
        no_mods = dict(tt, tests=dict(tests, b={k: v for k, v in tests["b"].items() if k != "mods"}))
        res = match(base + ["test.unused"], base, no_mods)
        ok(name + ": a check and scene that name no extra mods keep the row of an unread mod", not res["rerun"], res["rows"])
        res = match(base, base[:-1], no_mods)
        ok(name + ": and owe it for a mod that the mod itself reads", res["rerun"] == ["a", "b"], res["rows"])
        match(base + ["test.a"], base)
        with patch.object(BM, "tier_lister", return_value=lambda _: (base, None)):
            wo = M.walk_owed(tr.root, MOD, {"stage": "his_walk"})
            plan = M.ingame_to_run(tr.root, MOD, 2, tt)
        ok(name + ": the tick and next visit owe only the row the list change touches",
           list(wo["owed"]) == ["a"] and "test.a" in wo["owed"]["a"] and plan == (["a"], ["b"]), (wo, plan))
        switched = dict(tests, b=dict(tests["b"], tier="next-small"))
        tr.set_table(switched)
        tr.commit("check b switches to a tier that only drops an unread mod")
        res = match(base + ["test.unused"], base, {"tests": switched})
        with patch.object(BM, "tier_lister", return_value=lambda _: (base, None)):
            plan = M.ingame_to_run(tr.root, MOD, 2, {"tests": switched})
        ok(name + ": switching the named tier keeps a row when its reads are unchanged",
           not res["rerun"] and plan == ([], ["a", "b"]), (res["rerun"], plan))
    finally:
        tr.close()


def t_full_list_is_the_mods_the_game_can_load():
    """RIMMANDRAKE_DROP_UNINSTALLED_MOD_FROM_FULL_LIST_IDENTITY_KOTH (ExplosiveKnockback visit 4, 2026-11-23): ModsConfig named
    koth.isid, which is not installed; the rows listed 315 mods, the save the game wrote 314, and no full row counted."""
    d = tempfile.mkdtemp(prefix="full_list_")
    try:
        cfg, vt = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "Version.txt")
        with open(cfg, "w") as f:
            f.write("<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>Koth.ISID</li><li>A.Mod_steam</li>"
                    "</activeMods></ModsConfigData>")
        with open(vt, "w") as f:
            f.write("1.6.4871 rev590\n")

        def idn(scan, **k):
            return BM.identity(d, "Planted", mods_dir=d, config=cfg, version_txt=vt, mod_sha="s", scan=scan, **k)
        here = {"ludeon.rimworld": {}, "a.mod": {}}
        full = idn(lambda m: here, full=True)
        ok("full-list-is-the-mods-the-game-can-load: a package with no mod on this machine is left out and named",
           full["active_mods"] == ["ludeon.rimworld", "A.Mod_steam"] and full.get("not_installed") == ["Koth.ISID"], full)
        both = idn(lambda m: dict(here, **{"koth.isid": {}}), full=True)
        ok("full-list-is-the-mods-the-game-can-load: an installed package stays in",
           len(both["active_mods"]) == 3 and not both.get("not_installed"), both)

        def boom(m):
            raise OSError("no drive")
        for name, scan in (("raises", boom), ("finds no game", lambda m: {})):
            bad = idn(scan, full=True)
            ok("full-list-is-the-mods-the-game-can-load: a scan that %s is 'could not look', never a filtered list" % name,
               len(bad["active_mods"]) == 3 and "not_installed" not in bad
               and any("installed mods" in w for w in bad["why"]), bad)
        tier = idn(boom, tier="t")
        ok("full-list-is-the-mods-the-game-can-load: a tier row is not scanned",
           len(tier["active_mods"]) == 3 and not any("installed mods" in w for w in tier.get("why") or []), tier)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_path_outside_the_repo_is_not_in_the_change():
    """RIMMANDRAKE_KEEP_RERUN_RELATION_READABLE_PAST_THE_STEAM_FOLDER: Pyrelands' table declared `/mnt/c/Program Files`
    paths; git diff refused the whole pathspec (exit 128), and all 64 checks read 'git cannot list the change'."""
    tr = Tree()
    try:
        extra = {"sc_out_mixed": {"id": "sc_out_mixed", "kind": "live_minimal", "stage": "6", "tier": "t",
                                  "reads": ["/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
                                            "src/RimMandrake/Planted/Source/C.cs"]},
                 "sc_out_only": {"id": "sc_out_only", "kind": "live_minimal", "stage": "6", "tier": "t",
                                 "reads": ["/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
                                           "C:\\Users\\Someone\\AppData\\ModsConfig.xml"]}}
        tr.set_table(table(extra))
        base = tr.commit("table with paths outside the repository")
        tr.edit("src/RimMandrake/Planted/Source/A.cs", "v = 0", "v = 1")
        tr.commit("A.cs")
        res = relate(tr, all_rows(base, table(extra)))
        ok("a-path-outside-the-repo-is-not-in-the-change: a declared path outside the repository leaves the change "
           "readable; a check declaring only such paths is unreadable alone",
           sorted(res["unreadable"]) == ["sc_blank", "sc_out_only"] and res["rows"]["sc_a"]["state"] == "touched"
           and res["rows"]["sc_out_mixed"]["state"] == "untouched" and res["rows"]["sc_b"]["state"] == "untouched",
           (res["unreadable"], {k: v["state"] for k, v in res["rows"].items()}))
    finally:
        tr.close()


TESTS = [t_declared_paths_are_exercises_reads_and_file, t_untouched_row_counts, t_touched_check_reruns,
         t_undeclared_change_reruns_nothing_and_is_listed, t_unreadable_relation_reruns_alone,
         t_whole_mod_check_reruns_on_any_change, t_whole_mod_check_skips_hashignored,
         t_csharp_relates_by_source_file, t_python_relates_by_symbol,
         t_json_relates_by_entry, t_spec_change_reruns, t_rows_from_several_builds, t_walk_not_the_source_is_one_deploy,
         t_stale_walk_folder_still_reads_the_source_change,
         t_tier_list_of_any_install_here_counts, t_full_list_is_the_mods_the_game_can_load,
         t_a_path_outside_the_repo_is_not_in_the_change]


def t_python_imports_read_once_per_commit():
    """Three checks declare validation.py and it changed: its imports are parsed once at each of the two commits (the
    symbol tables parse it once more per commit), never once per check."""
    import ast
    tr = Tree()
    try:
        tr.edit("src/RimMandrake/Planted/validation.py", "return x + 1", "return x + 3")
        tr.commit("helper_a")
        tt = table({"sc_a2": dict(table()["sc_a"], id="sc_a2"), "sc_a3": dict(table()["sc_a"], id="sc_a3")})
        texts = {tr.git("show", "%s:src/RimMandrake/Planted/validation.py" % s) for s in (tr.base, "HEAD")}
        counts = {}
        real = ast.parse

        def counting(src, *a, **k):
            if src.strip() in texts:
                counts[src.strip()] = counts.get(src.strip(), 0) + 1
            return real(src, *a, **k)
        ast.parse = counting
        try:
            res = relate(tr, all_rows(tr.base, tt), tests=tt)
        finally:
            ast.parse = real
        ok("python-imports-read-once-per-commit: three checks on one changed file parse it at most twice per commit "
           "(imports once, symbols once)", counts and max(counts.values()) <= 2
           and res["rows"]["sc_a3"]["state"] == "touched", {"parses": sorted(counts.values()), "rows": res["rows"]})
    finally:
        tr.close()


def t_commit_reads_shared_across_relations():
    """A second relation in the same process, with the same runner, reads a file at a full commit id and the C# units
    of that file from the first relation's reads: no second git call. A read at a name that can move (HEAD) still asks
    git each time it resolves the name."""
    tr = Tree()
    try:
        calls = []

        def counting(argv, *a, **k):
            calls.append(list(argv))
            return subprocess.run(argv, *a, **k)
        full = tr.git("rev-parse", tr.base)
        path = "src/RimMandrake/Planted/Source/A.cs"
        r1 = RR.Relation(tr.root, MOD, table(), runner=counting)
        a1 = r1.git.show(full, path)
        u1 = r1._cs(full, path)
        before = len(calls)
        r2 = RR.Relation(tr.root, MOD, table(), runner=counting)
        after_new = len(calls)
        a2 = r2.git.show(full, path)
        u2 = r2._cs(full, path)
        shows = [c for c in calls[after_new:] if "show" in c]
        ok("commit-reads-shared-across-relations: a second relation reads a file and its C# units at a full commit id "
           "with no second git show", a1 == a2 and a1 is not None and u1 is not None and set(u1) == set(u2)
           and not shows, {"shows": shows, "calls_before": before})
        tr.edit(path, "int v = 0;", "int v = 9;")
        moved = tr.commit("move HEAD")
        r3 = RR.Relation(tr.root, MOD, table(), runner=counting)
        ok("commit-reads-shared-across-relations: HEAD is resolved again by each relation, so a moved HEAD is seen",
           r3.new == moved and r1.new == full, {"r3.new": r3.new, "moved": moved})
    finally:
        tr.close()


HUB_CS = """namespace P {
class Fire {
    static int Roll() { return Spot() + Settings.alpha; }
    static int Spot() { return 1; }
    int made = 1;
    public override void ExposeData() { int e = 0; }
}
class Rain {
    static int Douse() { return Settings.beta; }
    static int Wet() { return Help.Both(); }
}
class Help { static int Both() { return 7; } }
}
"""
SETTINGS_CS = """namespace P {
class Settings {
    static int alpha = 1;
    static int beta = 2;
    static int gamma = 3;
    static int Reset() { return 4; }
    public override void ExposeData() { int e = 0; }
}
}
"""


def _part_tree(checks):
    """A planted mod with two hub C# files; `checks` {id: exercises} declared beside the table."""
    src = "src/RimMandrake/Planted/"
    tests = table({t: {"id": t, "kind": "live_minimal", "stage": "6", "tier": "t", "file": src + "validation.py",
                       "entry": "scene_a"} for t in checks})
    tr = Tree()
    tr.write(src + "Source/H.cs", HUB_CS)
    tr.write(src + "Source/S.cs", SETTINGS_CS)
    tr.write(src + "Assemblies/P.dll.srchash", "# dll: 0\n00 A.cs\n00 B.cs\n00 C.cs\n00 H.cs\n00 S.cs\n")
    tr.set_table(tests)
    tr.write("design/concepts/Planted/version/exercises.json", json.dumps({"checks": checks}))
    return tr, tr.commit("hubs"), tests


def _part_case(checks, *edits):
    """relate() after `edits` (file under Source/, old text, new text)."""
    tr, base, tests = _part_tree(checks)
    try:
        for f, a, b in edits:
            tr.edit("src/RimMandrake/Planted/Source/" + f, a, b)
        tr.commit("the change")
        return relate(tr, all_rows(base, tests), tests)
    finally:
        tr.close()


H, S = "src/RimMandrake/Planted/Source/H.cs", "src/RimMandrake/Planted/Source/S.cs"


def _states(res, checks):
    return {t: res["rows"][t]["state"] for t in checks}


def t_csharp_part_relates_by_its_members():
    name = "csharp-part-relates-by-its-members"
    ck = {"fire": [H + "::Fire"], "rain": [H + "::Rain"], "both": [H + "::Fire,Rain"], "spot": [H + "::Spot"],
          "wet": [H + "::Wet"], "file": [H], "split": [H + "::Rain", H + "::Fire"]}
    got = _states(_part_case(ck, ("H.cs", "return 1;", "return 2;")), ck)
    ok(name + ": a changed member touches the checks that declare its type, itself or the file, and no other",
       got == {"fire": "touched", "rain": "untouched", "both": "touched", "spot": "touched", "wet": "untouched",
               "file": "touched", "split": "touched"}, got)
    got = _states(_part_case(ck, ("H.cs", "return 7;", "return 8;")), ck)
    ok(name + ": a helper that a declared part calls in the same file touches the check",
       got["rain"] == "touched" and got["wet"] == "touched" and got["fire"] == "untouched", got)
    got = _states(_part_case(ck, ("H.cs", "int e = 0", "int e = 1")), ck)
    ok(name + ": a member the engine calls touches the checks that declare its type, not one that declares another member",
       got["fire"] == "touched" and got["rain"] == "untouched" and got["spot"] == "untouched", got)
    got = _states(_part_case(ck, ("H.cs", "made = 1", "made = 2")), ck)
    ok(name + ": an instance field's initializer runs with its type, so it touches a check that declares any member of it",
       got["spot"] == "touched" and got["fire"] == "touched" and got["rain"] == "untouched", got)
    got = RR.run_key({"exercises": [H + "::Fire"]}, "exercises") != RR.run_key({"exercises": [H + "::Rain"]}, "exercises")
    ok(name + ": a table entry whose declared part changed is a changed entry", got)
    got = _states(_part_case(ck, ("H.cs", "namespace P {\nclass Fire", "using System;\nnamespace P {\nclass Fire")), ck)
    ok(name + ": a using line touches every check that declares a part of the file", set(got.values()) == {"touched"}, got)
    got = _states(_part_case({"a": [H + "::Rain", H]}, ("H.cs", "return 1;", "return 2;")), ["a"])
    ok(name + ": the whole file declared beside a part is the whole file", got["a"] == "touched", got)
    got = _states(_part_case({"a": [H + "::Rain", "src/RimMandrake/Planted/Source/"]}, ("H.cs", "return 1;", "return 2;")), ["a"])
    ok(name + ": a folder declared beside a part is the whole file", got["a"] == "touched", got)
    res = _part_case(ck, ("H.cs", "class Help {", "class Help { /* unclosed"))
    ok(name + ": a file that does not read relates whole", set(_states(res, ck).values()) == {"touched"}, _states(res, ck))
    tr, base, tests = _part_tree({"rain": [H + "::Rain"]})
    try:
        tr.write("src/RimMandrake/Planted/Assemblies/P.dll.srchash", "# dll: 1\n00 A.cs\n00 B.cs\n00 C.cs\n11 H.cs\n00 S.cs\n")
        tr.commit("recompiled, its text landed before")
        res = relate(tr, all_rows(base, tests), tests)
        ok(name + ": a recompiled file whose text did not change relates whole", res["rows"]["rain"]["state"] == "touched",
           res["rows"]["rain"])
    finally:
        tr.close()


def t_unknown_part_relates_whole():
    name = "unknown-part-relates-whole"
    ck = {"typo": [H + "::Rian"], "gone": [H + "::Help"], "half": [H + "::Rain,Rian"]}
    res = _part_case(ck, ("H.cs", "return 1;", "return 2;"))
    got = _states(res, ck)
    ok(name + ": a declared part that the file holds at neither commit relates the whole file, and the reading says so",
       got["typo"] == "touched" and got["half"] == "touched" and "Rian" in res["rows"]["typo"]["why"], res["rows"]["typo"])
    got = _states(_part_case(ck, ("H.cs", "class Help {", "class Aid {")), ck)
    ok(name + ": a declared part that the change renames touches the check", got["gone"] == "touched", got)


def t_reached_part_follows_the_declared_csharp():
    name = "reached-part-follows-the-declared-csharp"
    ck = {"fire": [H + "::Fire", S + "::~"], "rain": [H + "::Rain", S + "::~"], "file": [H, S + "::~"]}
    got = _states(_part_case(ck, ("S.cs", "alpha = 1", "alpha = 5")), ck)
    ok(name + ": a member of a ~ file touches only the checks whose declared C# names it",
       got == {"fire": "touched", "rain": "untouched", "file": "touched"}, got)
    got = _states(_part_case(ck, ("S.cs", "gamma = 3", "gamma = 5"), ("S.cs", "return 4;", "return 5;")), ck)
    ok(name + ": a member no declared C# names touches none", set(got.values()) == {"untouched"}, got)
    got = _states(_part_case(ck, ("S.cs", "int e = 0", "int e = 1")), ck)
    ok(name + ": a member the engine calls, on a type the declared C# names, touches the check",
       set(got.values()) == {"touched"}, got)
    got = _states(_part_case({"only": [S + "::~"]}, ("S.cs", "gamma = 3", "gamma = 5")), ["only"])
    ok(name + ": a ~ file with no other declared C# has nothing to follow and relates whole", got["only"] == "touched", got)
    tr, base, tests = _part_tree({"a": [H + "::Fire", "src/RimMandrake/Planted/Source/A.cs", S + "::~"]})
    try:
        tr.write("src/RimMandrake/Planted/Source/A.cs", "class A { /* unclosed\n")
        base = tr.commit("a declared file that does not read, at both commits")
        tr.edit("src/RimMandrake/Planted/Source/S.cs", "gamma = 3", "gamma = 5")
        tr.commit("the change")
        res = relate(tr, all_rows(base, tests), tests)
        ok(name + ": declared C# that does not read leaves nothing to follow, and ~ relates whole",
           res["rows"]["a"]["state"] == "touched", res["rows"]["a"])
    finally:
        tr.close()
    got = _states(_part_case(ck, ("H.cs", "Settings.beta", "Settings.gamma"), ("S.cs", "gamma = 3", "gamma = 5")), ck)
    ok(name + ": a name that the change starts to use is followed", got["rain"] == "touched" and got["fire"] == "untouched", got)
    ck = {"sc": [H + "::Rain", S + "::~,gamma"]}
    got = [_states(_part_case(ck, ("S.cs", a, b)), ck)["sc"] for a, b in
           (("gamma = 3", "gamma = 5"), ("beta = 2", "beta = 5"), ("alpha = 1", "alpha = 5"))]
    ok(name + ": ~ and a named member of one file are both read", got == ["touched", "touched", "untouched"], got)


def t_changed_member_no_check_declares_is_listed():
    name = "changed-member-no-check-declares-is-listed"
    ck = {"fire": [H + "::Fire", S + "::~"], "rain": [H + "::Rain"]}
    res = _part_case(ck, ("S.cs", "return 4;", "return 5;"))
    ok(name + ": the member is listed with its file", res["undeclared"] == [S + "::P/Settings/Reset()"] or
       res["undeclared"] == [S + "::Settings/Reset()"], res["undeclared"])
    res = _part_case(ck, ("S.cs", "alpha = 1", "alpha = 5"))
    ok(name + ": a member that a check reaches is not listed", res["undeclared"] == [], res["undeclared"])
    res = _part_case(dict(ck, file=[S]), ("S.cs", "return 4;", "return 5;"))
    ok(name + ": a file that another check declares whole lists nothing", res["undeclared"] == [], res["undeclared"])


def t_declared_none_is_read_as_no_csharp():
    name = "declared-none-is-read-as-no-csharp"
    ck = {"none": ["none"], "blank": []}
    got = _states(_part_case(ck, ("H.cs", "return 1;", "return 2;")), ck)
    ok(name + ": a live check declared to exercise no C# keeps its row on a C# change; one that declares nothing reruns",
       got == {"none": "untouched", "blank": "unreadable"}, got)
    ok(name + ": none is no path: a check that declares it and nothing else declares nothing it reads",
       RR.declared({"exercises": ["none"]}, MOD) == ([], False), RR.declared({"exercises": ["none"]}, MOD))
    got = _states(_part_case({"none": ["none", H + "::Fire"]}, ("H.cs", "return 1;", "return 2;")), ["none"])
    ok(name + ": none beside a C# part does not hide the part", got["none"] == "touched", got)
    got = _states(_part_case({"none": ["none"]}, ("../validation.py", "helper_a(1)", "helper_a(2)")), ["none"])
    ok(name + ": its scene script still relates", got["none"] == "touched", got)


def _ledger_digest():
    h = hashlib.sha256()
    d = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
    for nm in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, nm)
        if os.path.isfile(p):
            with open(p, "rb") as f:
                h.update(nm.encode() + b"\0" + f.read())
    return h.hexdigest()


def _mutate(kind):
    """Plant one fault in the code under test, in this process only."""
    if kind == "relation_ignored":
        real = BM.judge_row
        BM.judge_row = lambda test, spec, r, walk, tiers, relation=None, deploy=None: real(test, spec, r, walk, tiers, None, deploy)
    elif kind == "all_untouched":
        RR.Relation.touches = lambda self, tid, old: ("untouched", "planted", [])
    elif kind == "parts_untouched":
        RR.Relation.part_hits = lambda self, tid, f, o: (False, "planted", set(), set())
    else:
        raise SystemExit("unknown mutation %s" % kind)


def t_tick_uses_deploy_build_without_walking():
    """The page's promise of that name: its checks live in selftest_build_match.tick_walk_checks (a compose apply
    stamps the deployed folder; two Dispatch ticks read the stamp and walk no tree). Run here so the page's test of
    the same name runs them."""
    import selftest_build_match as SBM
    tmp = tempfile.mkdtemp(prefix="rerun_relation_tickwalk_")
    try:
        before = len(SBM.FAILS)
        SBM.tick_walk_checks(tmp)
        bad = SBM.FAILS[before:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok("tick-uses-deploy-build-without-walking", not bad, "; ".join(bad))


def main():
    if "--mutate" in sys.argv:
        _mutate(sys.argv[sys.argv.index("--mutate") + 1])
    before = _ledger_digest()
    t_declared_paths_are_exercises_reads_and_file()
    t_untouched_row_counts()
    t_touched_check_reruns()
    t_undeclared_change_reruns_nothing_and_is_listed()
    t_shipped_csharp_reruns_the_live_checks_that_name_none()
    t_rebuilt_dll_relates_by_its_srchash()
    t_unreadable_relation_reruns_alone()
    t_whole_mod_check_reruns_on_any_change()
    t_whole_mod_check_skips_hashignored()
    t_csharp_relates_by_source_file()
    t_csharp_relates_by_scene_section()
    t_csharp_code_after_a_switch_runs_when_a_section_falls_out()
    t_csharp_reads_the_types_it_names()
    t_declared_exercises_bound_the_types_named()
    t_python_relates_by_symbol()
    t_python_def_name_is_no_row_id()
    t_python_chain_registration_is_the_other_files()
    t_json_relates_by_entry()
    t_spec_change_reruns()
    t_rows_from_several_builds()
    t_walk_not_the_source_is_one_deploy()
    t_stale_walk_folder_still_reads_the_source_change()
    t_tier_list_of_any_install_here_counts()
    t_mod_list_only_reruns_related_rows()
    t_full_list_is_the_mods_the_game_can_load()
    t_a_path_outside_the_repo_is_not_in_the_change()
    t_python_imports_read_once_per_commit()
    t_commit_reads_shared_across_relations()
    t_csharp_part_relates_by_its_members()
    t_unknown_part_relates_whole()
    t_reached_part_follows_the_declared_csharp()
    t_changed_member_no_check_declares_is_listed()
    t_declared_none_is_read_as_no_csharp()
    t_tick_uses_deploy_build_without_walking()
    ok("the run left infrastructure/state/ledger/events/ unchanged", _ledger_digest() == before)
    print("%d of %d checks failed" % (len(FAILS), len(SEEN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
