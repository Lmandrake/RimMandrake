#!/usr/bin/env python3
"""Offline: the GSS C# selftest holds winbuild.exclusive("GimmeSomeSlackSelfTest") from build through run
(RIMMANDRAKE_LOCK_GSS_SELFTEST_STAGE_SHARED_BY_EVERY_CLONE). Every clone stages it in the same D: folder; stage_build locks
only the compile, so one clone's running test held the DLL while another rebuilt it (MSB3027 "being used by another
process", 2026-11-16) or could run the other's half-copied build. Read from the source: main's body runs inside the lock."""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "selftest_gimmesomeslack.py"), encoding="utf-8").read()
tree = ast.parse(src)


def holds_lock(fn):
    for node in ast.walk(fn):
        if isinstance(node, ast.With):
            for item in node.items:
                c = item.context_expr
                if isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "exclusive" and \
                        c.args and isinstance(c.args[0], ast.Constant) and c.args[0].value == "GimmeSomeSlackSelfTest":
                    inner = ast.unparse(node)
                    return "stage_build" in inner and "run_interop" in inner
    return False


main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
ok = holds_lock(main)
print(("PASS" if ok else "FAIL") + " GSS selftest build and run both inside winbuild.exclusive('GimmeSomeSlackSelfTest')")
sys.exit(0 if ok else 1)
