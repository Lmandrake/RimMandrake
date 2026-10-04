"""selftest_mandrakepatches.py -- every_fix_is_guarded_static is green on the shipped Patches/ and reddens on
each break it exists to catch (planted in a temp copy, never the shipped files)."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    spec = importlib.util.spec_from_file_location("mp_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    shipped = v.unguarded_ops()
    check("shipped Patches/: every top-level op guarded", shipped == [], shipped)
    tmp = tempfile.mkdtemp()
    try:
        pd = os.path.join(tmp, "Patches")
        shutil.copytree(os.path.join(HERE, "Patches"), pd)
        f = os.path.join(pd, "ThirdPartySignConfigErrors_Fix.xml")
        s = open(f, encoding="utf-8").read()
        brk = s.replace('<Operation Class="PatchOperationFindMod">', '<Operation Class="PatchOperationFindMod" MayRequire="Dark.Signs">', 1)
        open(f, "w", encoding="utf-8").write(brk)
        got = v.unguarded_ops(pd)
        check("break: top-level MayRequire is reported as inert", len(got) == 1 and "inert" in got[0][2], got)
        open(f, "w", encoding="utf-8").write(s)
        open(os.path.join(pd, "Bare.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationReplace"><xpath>Defs/X</xpath><value><a/></value></Operation></Patch>')
        got = v.unguarded_ops(pd)
        check("break: a bare Replace is reported unguarded", got == [("Bare.xml", 0, "unguarded PatchOperationReplace")], got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if FAILS:
        print("\n%d MandrakePatches selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall MandrakePatches selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
