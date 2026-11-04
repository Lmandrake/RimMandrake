#!/usr/bin/env python3
"""selftest_tool_metadata_stale.py - selftest_tool_metadata.py compares only a build of these sources.

NIGHTLY_COP_FIX_RED_INLFTF_XEWJ: a stale gitignored DLL read as a lost-tools FAIL. The cure must not blind the test,
so the break case matters most: a DLL that IS a build of these sources and lacks a tool still fails.

check() hands main() a made-up hash; check_real() leaves want_hash at its default, because that default is the only
thing the nightly run ever exercises. Without those cases, deleting the line that computes the real hash stayed green
while every DLL read UNMEASURED for good (blind check at d0aaa74f).

    python3 src/RimMandrake/bridgetools/selftest_tool_metadata_stale.py
"""
import contextlib
import glob
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import companion_identity      # noqa: E402
import selftest_tool_metadata as stm  # noqa: E402
import tool_metadata           # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import run_selftests           # noqa: E402

build = stm.build

WANT = "a" * 64
OTHER = "b" * 64
SOURCE = tool_metadata.tool_names_from_source(stm.SOURCE_DIR)
GATED = stm.gm_gated_names_from_source(stm.SOURCE_DIR)
fails = []


def check(name, stamp, surface, want_rc, want_text):
    """Run the real main() on a fixture DLL carrying `stamp`, whose tool surface reads as `surface`."""
    with tempfile.TemporaryDirectory() as tmp:
        dll = companion_identity.write_fixture(os.path.join(tmp, companion_identity.DLL_NAME), stamp)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = stm.main(dll_path=dll, want_hash=WANT, read_dll=lambda _path: set(surface))
    text = out.getvalue()
    good = rc == want_rc and want_text in text
    print("%s  %s (rc %s)" % ("ok   " if good else "WRONG", name, rc))
    if not good:
        fails.append(name)
        print(text)


def check_real(name, stamp, surface, want_rc, want_text, want_state):
    """As check(), with want_hash at its DEFAULT, and the harness's verdict on the output as well."""
    with tempfile.TemporaryDirectory() as tmp:
        dll = companion_identity.write_fixture(os.path.join(tmp, companion_identity.DLL_NAME), stamp)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = stm.main(dll_path=dll, read_dll=lambda _path: set(surface))
    text = out.getvalue()
    state = run_selftests.classify(rc, text)[0]
    good = rc == want_rc and want_text in text and state == want_state
    print("%s  %s (rc %s, harness %s)" % ("ok   " if good else "WRONG", name, rc, state))
    if not good:
        fails.append(name)
        print(text)


def verify_refuses(dll):
    """True when build.verify_src_hash() refuses this DLL."""
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            build.verify_src_hash(dll)
        except SystemExit:
            return True
    return False


def check_build_side(real):
    """The hash main() compares is the one build.py embeds and verifies, and the csproj takes it under that key."""
    prop = build.src_hash_prop()
    with tempfile.TemporaryDirectory() as tmp:
        same = companion_identity.write_fixture(os.path.join(tmp, "same.dll"), real)
        other = companion_identity.write_fixture(os.path.join(tmp, "other.dll"), OTHER)
        accepted, refused = not verify_refuses(same), verify_refuses(other)
    csproj = glob.glob(os.path.join(stm.SOURCE_DIR, "*.csproj"))
    text = open(csproj[0], encoding="utf-8").read() if csproj else ""
    embeds = '<AssemblyMetadata Include="%s" Value="$(JawaSrcHash)"' % companion_identity.META_KEY in text
    with open(os.path.join(HERE, "build.py"), encoding="utf-8") as f:
        passed = f.read().count("src_hash_prop()]")
    for name, good in (("build.py passes the hash main() compares", prop == "-p:JawaSrcHash=%s" % real),
                       ("build.py verifies a DLL of that hash and refuses another", accepted and refused),
                       ("the csproj embeds it under the key the reader looks for", embeds),
                       ("both of build.py's compile commands pass it", passed == 2)):
        print("%s  %s" % ("ok   " if good else "WRONG", name))
        if not good:
            fails.append(name)


def check_tree_moved(real, victim, stale_text):
    """The incident: the tree gains a source file after the build. Hashes the ON-DISK tree, not a git revision."""
    src = os.path.join(build.REPO_ROOT, *companion_identity.SRC_REL.split("/"))
    saved = build.REPO_ROOT
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, *companion_identity.SRC_REL.split("/"))
        shutil.copytree(src, copy, ignore=shutil.ignore_patterns("bin", "obj"))
        with open(os.path.join(copy, "AddedAfterTheBuild.cs"), "w", encoding="utf-8") as f:
            f.write("// a source edit made after the DLL was built\n")
        moved = companion_identity.srchash_worktree(tmp)
        build.REPO_ROOT = tmp
        try:
            if not moved or moved == real:
                print("WRONG  the moved tree did not change the source hash")
                fails.append("moved tree hash")
            check_real("the tree moved after the build: the older DLL is UNMEASURED", real, SOURCE - {victim}, 2,
                       stale_text, "UNMEASURED")
            check_real("the tree moved: a DLL built from the tree on disk still FAILS on a lost tool", moved,
                       SOURCE - {victim}, 1, victim, "FAIL")
            check_real("the tree moved: a DLL built from the tree on disk passes", moved, SOURCE, 0, "1/1 passed",
                       "PASS")
        finally:
            build.REPO_ROOT = saved


def check_unhashable(real, stale_text):
    """Sources that cannot be hashed measure nothing, whatever the DLL carries."""
    saved = companion_identity.srchash_worktree
    companion_identity.srchash_worktree = lambda _root: None
    try:
        check_real("unhashable sources, stamped DLL: UNMEASURED", real, SOURCE, 2, stale_text, "UNMEASURED")
        check_real("unhashable sources, unstamped DLL: UNMEASURED", None, SOURCE, 2, stale_text, "UNMEASURED")
    finally:
        companion_identity.srchash_worktree = saved


def main():
    if len(SOURCE) < 100 or not GATED or not GATED < SOURCE:
        print("WRONG  the source scan cannot see the roster: %d tools, %d gated" % (len(SOURCE), len(GATED)))
        return 1
    print("source fixture: %d tools, %d gated" % (len(SOURCE), len(GATED)))
    victim = sorted(SOURCE - GATED)[0]
    stale_text = "UNMEASURED, not a pass or a fail"

    check("a build of other sources lacking a tool is UNMEASURED", OTHER, SOURCE - {victim}, 2, stale_text)
    check("a DLL with no embedded hash is UNMEASURED", None, SOURCE - {victim}, 2, stale_text)
    check("break: a build of these sources lacking a tool still FAILS", WANT, SOURCE - {victim}, 1, victim)
    check("break: a build of these sources with an extra tool still FAILS", WANT, SOURCE | {"jawa/phantom"}, 1,
          "jawa/phantom")
    check("a build of these sources with the full surface passes", WANT, SOURCE, 0, "1/1 passed")
    check("a non-GM build of these sources passes", WANT, SOURCE - GATED, 0, "1/1 passed")

    # The nightly run calls main() bare, so every default is part of what it measures.
    defaults = stm.main.__defaults__
    good = defaults == (stm.DLL_PATH, None, tool_metadata.tool_names_from_dll) and \
        stm.DLL_PATH == os.path.join(build.ARTIFACT_DIR, build.DLL_NAME)
    print("%s  main() defaults to the built DLL, the real hash and the real reader" % ("ok   " if good else "WRONG"))
    if not good:
        fails.append("main() defaults")

    real = companion_identity.srchash_worktree(build.REPO_ROOT)
    if not real or len(real) != 64 or real in (WANT, OTHER):
        print("WRONG  the real source hash is not a hash: %r" % (real,))
        return 1
    print("real source hash: %s" % real[:12])
    check_real("default hash: a true-hash DLL lacking a tool FAILS", real, SOURCE - {victim}, 1, victim, "FAIL")
    check_real("default hash: a true-hash DLL with an extra tool FAILS", real, SOURCE | {"jawa/phantom"}, 1,
               "jawa/phantom", "FAIL")
    check_real("default hash: a true-hash DLL with the full surface passes", real, SOURCE, 0, "1/1 passed", "PASS")
    check_real("default hash: a non-GM true-hash DLL passes", real, SOURCE - GATED, 0, "1/1 passed", "PASS")
    check_real("default hash: another hash is UNMEASURED", OTHER, SOURCE - {victim}, 2, stale_text, "UNMEASURED")
    check_real("default hash: no hash is UNMEASURED", None, SOURCE - {victim}, 2, stale_text, "UNMEASURED")
    check_tree_moved(real, victim, stale_text)
    check_unhashable(real, stale_text)
    check_build_side(real)

    if fails:
        print("FAIL - %d case(s): %s" % (len(fails), "; ".join(fails)))
        return 1
    print("\nall cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
