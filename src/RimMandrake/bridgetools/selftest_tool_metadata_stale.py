#!/usr/bin/env python3
"""selftest_tool_metadata_stale.py - selftest_tool_metadata.py compares only a build of these sources.

NIGHTLY_COP_FIX_RED_INLFTF_XEWJ: a stale gitignored DLL read as a lost-tools FAIL. The cure must not blind the test,
so the break case matters most: a DLL that IS a build of these sources and lacks a tool still fails.

    python3 src/RimMandrake/bridgetools/selftest_tool_metadata_stale.py
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import companion_identity      # noqa: E402
import selftest_tool_metadata as stm  # noqa: E402
import tool_metadata           # noqa: E402

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

    if fails:
        print("FAIL - %d case(s): %s" % (len(fails), "; ".join(fails)))
        return 1
    print("\n6/6 passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
