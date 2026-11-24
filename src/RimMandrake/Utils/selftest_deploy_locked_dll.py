#!/usr/bin/env python3
"""Selftest (RIMMANDRAKE_KEEP_STAMP_OFF_A_DLL_THE_DEPLOY_COULD_NOT_WRITE): a DLL the OS refuses to write (the running game
locks it) keeps its old .srchash too, so the stamp never names a build that is not there; the other files still deploy, and a
writable DLL's stamp deploys with it.

    python3 src/RimMandrake/Utils/selftest_deploy_locked_dll.py
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402
from selftest_deploy_prune import write                         # noqa: E402

RELS = ["Assemblies/A.dll.srchash", "Assemblies/A.dll", "Assemblies/B.dll", "Assemblies/B.dll.srchash", "Defs/X.xml"]


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main():
    bad = []
    with tempfile.TemporaryDirectory(prefix="deploylocked-") as tmp:
        src, dst = os.path.join(tmp, "src"), os.path.join(tmp, "dst")
        for r in RELS:
            write(os.path.join(src, r), "<Defs />" if r.endswith(".xml") else "new")
            write(os.path.join(dst, r), "old")
        real = D.shutil.copy2

        def locked(s, d, *a, **k):
            if d.endswith("A.dll"):
                raise OSError(22, "Invalid argument", d)
            return real(s, d, *a, **k)
        D.shutil.copy2 = locked
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                copied, refused, failed = D.copy(src, dst, RELS)
        finally:
            D.shutil.copy2 = real
        got = dict((r, read(os.path.join(dst, r))) for r in RELS)
        names = sorted(f[0] for f in failed)
        for ok, what in (
                (got["Assemblies/A.dll"] == "old" and got["Assemblies/A.dll.srchash"] == "old",
                 "a locked DLL keeps its old stamp (stamp listed before the DLL)"),
                (names == ["Assemblies/A.dll", "Assemblies/A.dll.srchash"], "both are named as not written: %s" % names),
                (got["Assemblies/B.dll"] == got["Assemblies/B.dll.srchash"] == "new", "a writable DLL deploys with its stamp"),
                (got["Defs/X.xml"] == "<Defs />" and copied == 3 and not refused, "the other files still deploy (%d)" % copied)):
            print(("ok   " if ok else "FAIL ") + what)
            if not ok:
                bad.append(what)
    print("deploy locked dll: %s" % ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
