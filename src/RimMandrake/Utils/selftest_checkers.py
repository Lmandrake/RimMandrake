#!/usr/bin/env python3
"""selftest_checkers.py — prove check_declarations.py and check_load.py can FAIL.

    python3 src/RimMandrake/Utils/selftest_checkers.py

Exit 0 = every case reached the right verdict. 1 = at least one did not, and the
expected/actual diff is printed.

WHY THIS EXISTS
===============
**A green result from a checker that has never been seen to go red is not
evidence.** It is equally consistent with "nothing is wrong" and "the checker
cannot see anything".

That is not hypothetical here. `check_declarations.py` — written *to catch silent
failures* — shipped on 2026-08-13 reading the FIRST `<packageId>` in an About.xml.
An About.xml lists its dependencies' ids inside `<modDependencies>` before its
own, so the first one is usually `brrainz.harmony`. Every Harmony-dependent mod
registered under Harmony's id, its real id was reported MISSING, and the tool
produced **8 false alarms on its first run**. A fixture would have caught it in a
second. Case 4 below is that exact bug, frozen.

⚠️ **Fixtures only.** Every case runs against a throwaway temp tree. This never
reads the game install, the real `ModsConfig.xml`, or the repo's own mods — so it
is safe to run at any time, and its verdict does not drift when someone edits a
mod.

WHAT IT ASSERTS
===============
check_declarations.py
  1  loadAfter → an id that exists and is active                  PASS
  2  loadAfter → an id that exists nowhere                        MISSING (exit 1)
  3  loadAfter → on disk but not in ModsConfig                    INACTIVE (exit 0)
  4  a mod whose <modDependencies> precede its own <packageId>    own id read right
  5  a malformed About.xml, ours and on disk                      no crash
check_load.py
  6  same mods, same order                                        PASS
  7  requested but not loaded                                     FAIL
  8  same mods, DIFFERENT ORDER                                   FAIL
  9  manifest older than ModsConfig                               STALE (and FAIL)
  10 a missing file                                               exit 2, not a pass

PROVING THE FIXTURES BITE
=========================
A case that passes against a broken implementation is worthless. To re-verify,
copy the checkers somewhere scratch, break one, and point this at the copy:

    cp src/RimMandrake/Utils/check_*.py /tmp/scratch/
    # re-introduce the historic bug in /tmp/scratch/check_declarations.py:
    #   pid = re.search(r"<packageId>(.*?)</packageId>", open(about).read()).group(1)
    SELFTEST_CHECKER_DIR=/tmp/scratch python3 src/RimMandrake/Utils/selftest_checkers.py

Case 4 must go red. Done 2026-08-13; it does.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# The directory the checkers are loaded FROM. Overridable so a deliberately
# broken scratch copy can be run through the same cases — see the docstring.
CHECKER_DIR = os.environ.get("SELFTEST_CHECKER_DIR", HERE)


def load(name):
    path = os.path.join(CHECKER_DIR, name + ".py")
    spec = importlib.util.spec_from_file_location("selftest_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


decl = load("check_declarations")
load_chk = load("check_load")


# ---------------------------------------------------------------- harness ----
FAILURES = []
PASSED = []


def expect(case, what, want, got):
    """Record one assertion. Never raises — we want ALL failures, not the first."""
    if want == got:
        PASSED.append((case, what))
    else:
        FAILURES.append((case, what, want, got))


def silently(fn, *a, **kw):
    """Run fn, swallowing its stdout/stderr; return (result, captured text)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        result = fn(*a, **kw)
    return result, out.getvalue()


# --------------------------------------------------------------- fixtures ----
ABOUT = """<?xml version="1.0" encoding="utf-8"?>
<ModMetaData>
  <name>%(name)s</name>
  <author>selftest</author>
%(body)s</ModMetaData>
"""


def about(dirpath, name, body):
    os.makedirs(os.path.join(dirpath, "About"), exist_ok=True)
    with open(os.path.join(dirpath, "About", "About.xml"), "w",
              encoding="utf-8") as fh:
        fh.write(ABOUT % {"name": name, "body": body})


def raw_about(dirpath, text):
    os.makedirs(os.path.join(dirpath, "About"), exist_ok=True)
    with open(os.path.join(dirpath, "About", "About.xml"), "w",
              encoding="utf-8") as fh:
        fh.write(text)


def li_block(field, ids):
    return ("  <%s>\n" % field
            + "".join("    <li>%s</li>\n" % i for i in ids)
            + "  </%s>\n" % field)


def mods_config(path, active_ids):
    """A real-shaped ModsConfig: <knownExpansions> is present precisely because
    a naive `<li>` count picks it up and overstates the mod total."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n<ModsConfigData>\n'
                 '  <version>1.6.4535 rev726</version>\n'
                 + li_block("activeMods", active_ids)
                 + li_block("knownExpansions", ["ludeon.rimworld.royalty"])
                 + '</ModsConfigData>\n')


def manifest(path, ids, version="1.6.4535 rev726", captured="2026-08-13T00:00:00Z"):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"gameVersion": version, "capturedUtc": captured,
                   "mods": [{"packageId": i, "name": i} for i in ids]}, fh)


def build_declaration_fixture(tmp):
    """A fake install + a fake `src/` holding one of our mods per case."""
    disk = os.path.join(tmp, "workshop")
    src = os.path.join(tmp, "src")
    os.makedirs(disk)
    os.makedirs(src)

    # --- mods "installed on disk" ---
    about(os.path.join(disk, "ExistingActive"), "Existing Active",
          "  <packageId>vendor.existing</packageId>\n")
    about(os.path.join(disk, "ExistingInactive"), "Existing Inactive",
          "  <packageId>vendor.inactive</packageId>\n")
    about(os.path.join(disk, "Harmony"), "Harmony",
          "  <packageId>brrainz.harmony</packageId>\n")

    # 🔴 CASE 4, THE REGRESSION FIXTURE. <modDependencies> comes FIRST and names
    # brrainz.harmony, so the first <packageId> in this file is NOT this mod's.
    # The mod's own id is the DIRECT CHILD of the root; a dependency's never is.
    raw_about(os.path.join(disk, "HarmonyFirst"), """<?xml version="1.0" encoding="utf-8"?>
<ModMetaData>
  <name>Harmony Dependent</name>
  <author>selftest</author>
  <modDependencies>
    <li>
      <packageId>brrainz.harmony</packageId>
      <displayName>Harmony</displayName>
      <downloadUrl>https://github.com/pardeike/HarmonyRimWorld/releases/latest</downloadUrl>
    </li>
  </modDependencies>
  <packageId>vendor.harmonyfirst</packageId>
</ModMetaData>
""")

    # A truncated About.xml on disk — must be skipped, not fatal.
    raw_about(os.path.join(disk, "BrokenOnDisk"),
              "<?xml version=\"1.0\"?>\n<ModMetaData>\n  <packageId>vendor.trunc")

    # --- our mods, one per case ---
    about(os.path.join(src, "Case1_Resolves"), "Case 1",
          "  <packageId>jawa.case1</packageId>\n"
          + li_block("loadAfter", ["vendor.existing"]))
    about(os.path.join(src, "Case2_Missing"), "Case 2",
          "  <packageId>jawa.case2</packageId>\n"
          # The real 2026-08-13 finding: Jawa_Armoury named two ids that were
          # never on this machine, and nothing anywhere said so.
          + li_block("loadAfter", ["guy762.starwarskotorweapons",
                                   "Aoba.OuterRim.Core"]))
    about(os.path.join(src, "Case3_Inactive"), "Case 3",
          "  <packageId>jawa.case3</packageId>\n"
          + li_block("loadAfter", ["vendor.inactive"]))
    about(os.path.join(src, "Case4_Regression"), "Case 4",
          "  <packageId>jawa.case4</packageId>\n"
          + li_block("loadAfter", ["vendor.harmonyfirst"]))
    raw_about(os.path.join(src, "Case5_Malformed"),
              "<ModMetaData><packageId>jawa.case5</packageId><loadAfter>")

    config = os.path.join(tmp, "ModsConfig.xml")
    mods_config(config, ["ludeon.rimworld", "brrainz.harmony", "vendor.existing",
                         "vendor.harmonyfirst", "jawa.case1", "jawa.case2",
                         "jawa.case3", "jawa.case4"])
    return disk, src, config


# ------------------------------------------------- check_declarations cases ---
def test_declarations(tmp):
    disk, src, config = build_declaration_fixture(tmp)

    # Case 5, first half: a malformed About.xml on disk must not stop the scan.
    on_disk = decl.installed(mod_roots=[disk])
    expect("5", "malformed About.xml on disk does not abort installed()",
           True, "vendor.existing" in on_disk)
    expect("5", "unparseable mod contributes no id",
           False, "vendor.trunc" in on_disk)

    # 🔴 Case 4: the mod's own id, not its dependency's.
    expect("4", "own <packageId> read past <modDependencies>",
           True, "vendor.harmonyfirst" in on_disk)
    expect("4", "the dependent mod is NOT registered under brrainz.harmony",
           "HarmonyFirst",
           os.path.basename(os.path.dirname(os.path.dirname(
               on_disk.get("vendor.harmonyfirst", "?/?/?")))))

    act = decl.active(config=config)
    expect("0", "active() reads <activeMods> only (not <knownExpansions>)",
           8, len(act or []))

    missing, inactive, checked, abouts = decl.analyse(src, on_disk, act)
    miss = {(m, p) for m, _, p in missing}
    inact = {(m, p) for m, _, p in inactive}

    expect("1", "a resolvable, active loadAfter is not MISSING",
           False, any(m == "Case1_Resolves" for m, _ in miss))
    expect("1", "a resolvable, active loadAfter is not INACTIVE",
           False, any(m == "Case1_Resolves" for m, _ in inact))

    expect("2", "both nonexistent ids reported MISSING",
           {("Case2_Missing", "guy762.starwarskotorweapons"),
            ("Case2_Missing", "aoba.outerrim.core")},
           {t for t in miss if t[0] == "Case2_Missing"})

    expect("3", "on disk but not in ModsConfig is INACTIVE",
           {("Case3_Inactive", "vendor.inactive")},
           {t for t in inact if t[0] == "Case3_Inactive"})
    expect("3", "an INACTIVE declaration is not also MISSING",
           False, any(m == "Case3_Inactive" for m, _ in miss))

    expect("4", "a loadAfter on the Harmony-dependent mod resolves",
           False, any(m == "Case4_Regression" for m, _ in miss))

    expect("5", "a malformed About.xml of ours yields no declarations",
           [], decl.declared(os.path.join(src, "Case5_Malformed",
                                          "About", "About.xml")))
    expect("5", "the malformed mod is still enumerated",
           5, len(abouts))
    expect("0", "declaration count", 5, checked)

    # The exit code, taken from main() itself rather than re-derived here.
    rc = run_declarations_cli(disk, src, config)
    expect("2", "MISSING fails the run (exit 1)", 1, rc)

    # Case 3 in isolation: INACTIVE alone must NOT fail the run.
    only3 = os.path.join(tmp, "only_inactive")
    os.makedirs(only3)
    shutil.copytree(os.path.join(src, "Case3_Inactive"),
                    os.path.join(only3, "Case3_Inactive"))
    expect("3", "INACTIVE alone still exits 0",
           0, run_declarations_cli(disk, only3, config))

    # No declarations at all is a clean pass; no mods on disk is "cannot tell".
    empty = os.path.join(tmp, "empty_src")
    os.makedirs(empty)
    expect("0", "nothing to check exits 0", 0,
           run_declarations_cli(disk, empty, config))
    expect("0", "no mods on disk exits 2, not 0", 2,
           run_declarations_cli(os.path.join(tmp, "nothing_here"), src, config))


def run_declarations_cli(disk, src, config):
    """Drive check_declarations.main() end to end against the fixture."""
    old = (decl.MOD_ROOTS, decl.CONFIG, decl.repo_root)
    decl.MOD_ROOTS = [disk]
    decl.CONFIG = config
    # main() looks under repo_root()/src; hand it a root whose "src" is ours.
    holder = os.path.join(os.path.dirname(src), "_root_" + os.path.basename(src))
    if not os.path.islink(os.path.join(holder, "src")):
        os.makedirs(holder, exist_ok=True)
        link = os.path.join(holder, "src")
        if not os.path.exists(link):
            os.symlink(src, link)
    decl.repo_root = lambda: holder
    try:
        rc, _ = silently(decl.main)
    finally:
        decl.MOD_ROOTS, decl.CONFIG, decl.repo_root = old
    return rc


# -------------------------------------------------------- check_load cases ---
def stamp(config, man, man_newer=True):
    """Force mtimes: the manifest must postdate ModsConfig or it is STALE."""
    os.utime(config, (1_700_000_000, 1_700_000_000))
    delta = 60 if man_newer else -60
    os.utime(man, (1_700_000_000 + delta, 1_700_000_000 + delta))


def run_load_cli(config, man):
    old = (load_chk.CONFIG, load_chk.MANIFEST)
    load_chk.CONFIG, load_chk.MANIFEST = config, man
    try:
        rc, _ = silently(load_chk.main)
    finally:
        load_chk.CONFIG, load_chk.MANIFEST = old
    return rc


def test_load(tmp):
    d = os.path.join(tmp, "load")
    os.makedirs(d)
    config = os.path.join(d, "ModsConfig.xml")
    man = os.path.join(d, "manifest.json")
    ids = ["ludeon.rimworld", "brrainz.harmony", "jawa.armoury", "jawa.patches"]

    # Case 6 — identical membership AND identical order.
    mods_config(config, ids)
    manifest(man, ids)
    stamp(config, man)
    r = load_chk.evaluate(config, man)
    expect("6", "identical request and load passes", True, r["ok"])
    expect("6", "requested count ignores <knownExpansions>", 4, len(r["want"]))
    expect("6", "no missing", [], r["missing"])
    expect("6", "no extra", [], r["extra"])
    expect("6", "not stale", False, r["stale"])
    expect("6", "exit 0", 0, run_load_cli(config, man))

    # Case 7 — one requested mod never loaded.
    manifest(man, [i for i in ids if i != "jawa.armoury"])
    stamp(config, man)
    r = load_chk.evaluate(config, man)
    expect("7", "a requested-but-not-loaded mod fails", False, r["ok"])
    expect("7", "and is named", ["jawa.armoury"], r["missing"])
    expect("7", "exit 1", 1, run_load_cli(config, man))

    # Case 7b — loaded but never requested is also a mismatch.
    manifest(man, ids + ["stowaway.mod"])
    stamp(config, man)
    r = load_chk.evaluate(config, man)
    expect("7b", "an unrequested mod fails", False, r["ok"])
    expect("7b", "and is named", ["stowaway.mod"], r["extra"])

    # 🔴 Case 8 — same mods, different order. RimWorld resolves def overrides by
    # load order, so this is a different game, not a cosmetic diff.
    manifest(man, [ids[0], ids[1], ids[3], ids[2]])
    stamp(config, man)
    r = load_chk.evaluate(config, man)
    expect("8", "reordered load FAILS", False, r["ok"])
    expect("8", "order flagged", False, r["ordered"])
    expect("8", "membership is identical, so set comparison alone would pass",
           ([], []), (r["missing"], r["extra"]))
    expect("8", "exit 1", 1, run_load_cli(config, man))

    # Case 9 — a manifest describing a PREVIOUS load.
    manifest(man, ids)
    stamp(config, man, man_newer=False)
    r = load_chk.evaluate(config, man)
    expect("9", "older manifest flagged STALE", True, r["stale"])
    expect("9", "STALE fails even though the sets match exactly", False, r["ok"])
    expect("9", "the sets really do match", ([], [], True),
           (r["missing"], r["extra"], r["ordered"]))
    expect("9", "exit 1", 1, run_load_cli(config, man))

    # Case 10 — a missing file is NOT a pass.
    gone = os.path.join(d, "no_such_manifest.json")
    expect("10", "absent file reported", gone,
           load_chk.evaluate(config, gone)["absent"])
    expect("10", "exit 2, not 0", 2, run_load_cli(config, gone))


# ------------------------------------------------------------------- main ----
def main():
    tmp = tempfile.mkdtemp(prefix="selftest_checkers_")
    try:
        test_declarations(os.path.join(tmp, "decl"))
        test_load(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    cases = sorted({c for c, _ in PASSED} | {c for c, _, _, _ in FAILURES},
                   key=lambda s: (int("".join(ch for ch in s if ch.isdigit())), s))
    print("checkers under test: %s" % CHECKER_DIR)
    print("%d assertions across %d cases (%s)"
          % (len(PASSED) + len(FAILURES), len(cases), ", ".join(cases)))

    if FAILURES:
        print("\n🔴 %d ASSERTION(S) FAILED" % len(FAILURES))
        for case, what, want, got in FAILURES:
            print("\n  case %s — %s" % (case, what))
            print("    expected: %r" % (want,))
            print("    actual:   %r" % (got,))
        print("\n❌ the checkers do not behave as documented")
        return 1

    print("\n✅ every case reached the documented verdict — "
          "these checkers can fail, and fail for the right reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
