"""Every C# SelfTest case a validation.py chain asks for still exists (SELFTEST_FIX_DRAWBRIDGE_PROOF_PHBJ class guard).

A chain lists case names in a module-level *_CASES list; the C# SelfTest (Source/SelfTest/*.cs) defines them with
Case("<name>", ...). When a commit renames or deletes a case in C# and leaves the list alone, the chain silently asks
for a case that no longer exists, and only the nightly run notices (b7e8e8f1cc renamed
Drawbridge_StyledHeavyAnchors_upright_per_facing to Suspension_SteelHeavyAnchors_no_rope_table). This test fails on
any listed name with no matching Case("...") anywhere in Source/SelfTest, for every chain at once.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
for p_ in (os.path.join(os.path.dirname(FW), "Utils"), FW):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import validation as VAL  # noqa: E402


def main():
    files = glob.glob(os.path.join(FW, "Source", "SelfTest", "*.cs"))
    cs = set()
    for f in files:
        cs |= set(re.findall(r'Case\("([^"]+)"', open(f, encoding="utf-8").read()))
    lists = {k: v for k, v in vars(VAL).items()
             if k.endswith("_CASES") and isinstance(v, (list, tuple)) and all(isinstance(x, str) for x in v)}
    # sanity: the instrument can see (a blind glob or regex would make every name look dead, or none)
    if len(files) < 5 or len(cs) < 100 or len(lists) < 5:
        print("FAIL instrument blind: %d .cs files, %d cases, %d *_CASES lists" % (len(files), len(cs), len(lists)))
        return 1
    dead = sorted((k, n) for k, v in lists.items() for n in v if n not in cs)
    for k, n in dead:
        print("FAIL validation.%s names %r, which no Case(\"...\") in Source/SelfTest defines" % (k, n))
    print("validation case names: %d lists, %d names, %d C# cases, %s"
          % (len(lists), sum(len(v) for v in lists.values()), len(cs), "FAIL" if dead else "ok"))
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
