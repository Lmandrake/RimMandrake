#!/usr/bin/env python3
"""selftest_rerun_relation.py: the promises of design/specs/2026-11-21-rerun-only-related/boundary.md, one test of each
promise's name (boundary_check.py), on a throwaway git repository with one planted mod. Item
RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203.

No test reaches a launcher, a live game, the ledger or the repo's own files: every repository is a temp folder, and
main() checks that infrastructure/state/ledger/events/ is byte-for-byte unchanged after the run.

  --mutate relation_ignored   plants the fault "the build match ignores the relation" (the rule before 2026-11-21:
                              any change to the mod reruns every row); the run must go red
  --mutate all_untouched      plants "the relation says untouched for every check"; the run must go red
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

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
                 "entry": "scene_b", "reads": ["src/RimMandrake/Planted/Defs/B.xml",
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
        self.write(rel, self.read(rel).replace(old, new))

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
        BM.judge_row = lambda test, spec, r, walk, tiers, relation=None: real(test, spec, r, walk, tiers, None)
    elif kind == "all_untouched":
        RR.Relation.touches = lambda self, tid, old: ("untouched", "planted", [])
    else:
        raise SystemExit("unknown mutation %s" % kind)


def main():
    if "--mutate" in sys.argv:
        _mutate(sys.argv[sys.argv.index("--mutate") + 1])
    before = _ledger_digest()
    t_declared_paths_are_exercises_reads_and_file()
    t_untouched_row_counts()
    t_touched_check_reruns()
    t_undeclared_change_reruns_nothing_and_is_listed()
    t_unreadable_relation_reruns_alone()
    t_whole_mod_check_reruns_on_any_change()
    t_whole_mod_check_skips_hashignored()
    t_csharp_relates_by_source_file()
    t_python_relates_by_symbol()
    t_json_relates_by_entry()
    t_spec_change_reruns()
    t_rows_from_several_builds()
    t_walk_not_the_source_is_one_deploy()
    t_tier_list_of_any_install_here_counts()
    t_full_list_is_the_mods_the_game_can_load()
    t_a_path_outside_the_repo_is_not_in_the_change()
    t_python_imports_read_once_per_commit()
    ok("the run left infrastructure/state/ledger/events/ unchanged", _ledger_digest() == before)
    print("%d of %d checks failed" % (len(FAILS), len(SEEN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
