#!/usr/bin/env python3
"""Selftest: MayRequire naming a FOLDED packageId (MAYREQUIRE_REPAIR_GUARDS_NAME_A_GHOST).

A composed mod drops every folded packageId from the mod list, so a MayRequire
naming one can never be satisfied and RimWorld silently drops the guarded node.
Deploy rewrites them to the composed id in the DEPLOYED copy (compose and
ordinary mods alike); this test proves the rewrite, the staging, the scanner's
sanity probe against the real src/, and prints the measured census.

    python3 src/RimMandrake/Utils/selftest_mayrequire_folded.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biomes_compose as B                                      # noqa: E402

SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(SRC, "src") if os.path.basename(SRC) != "src" else SRC
fails = []


def check(ok, what):
    print("  %s %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        fails.append(what)


M = {"a.folded": "x.composed", "b.folded": "x.composed"}
t, h = B.rewrite_mayrequire('<li MayRequire="a.folded"/> <li MayRequireAnyOf="a.folded,b.folded,c.keep"/>'
                            ' <li MayRequire="c.keep"/>', M)
check(t == '<li MayRequire="x.composed"/> <li MayRequireAnyOf="x.composed,c.keep"/> <li MayRequire="c.keep"/>',
      "rewrites single + comma list, dedupes, leaves others (%r)" % t)
check(len(h) == 3, "3 hits")
t2, h2 = B.rewrite_mayrequire('<li MayRequire="C.KEEP"/>', M)
check(not h2 and t2 == '<li MayRequire="C.KEEP"/>', "untouched when nothing folded")

tmp = tempfile.mkdtemp(prefix="st_mr_")
try:
    d = os.path.join(tmp, "Mod")
    os.makedirs(os.path.join(d, "Defs"))
    for n, txt in (("Defs/bad.xml", '<Defs><X MayRequire="a.folded"/></Defs>'),
                   ("Defs/ok.xml", "<Defs><X/></Defs>")):
        with open(os.path.join(d, n), "w", encoding="utf-8") as fh:
            fh.write(txt)
    st = B.stage_rewritten(d, M, log=lambda *_: None)
    check(st is not None, "stage produced for an offending mod")
    if st:
        got = open(os.path.join(st, "Defs", "bad.xml"), encoding="utf-8").read()
        check('MayRequire="x.composed"' in got, "staged copy rewritten")
        check(os.path.islink(os.path.join(st, "Defs", "ok.xml")), "clean file is a link, untouched")
        check('a.folded' in open(os.path.join(d, "Defs", "bad.xml")).read(), "source never modified")
        shutil.rmtree(os.path.dirname(st), ignore_errors=True)
    os.remove(os.path.join(d, "Defs", "bad.xml"))
    check(B.stage_rewritten(d, M, log=lambda *_: None) is None, "no stage when clean")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

fm = B.folded_ids(SRC)
check(len(fm) > 0, "real src: %d folded ids" % len(fm))
found = B.scan_ghost_guards(SRC)
# sanity probe: the scanner must see the known FlowWorks case
probe = [f for f in found if f[0].endswith("RM_LiquidWorksScatter.xml")]
check(len(probe) >= 1, "scanner sees the known FlowWorks guard (%d)" % len(probe))
print("\nMEASURED: %d MayRequire site(s) in src/ name a folded id; %d are true ghosts (no satisfiable member):"
      % (len(found), sum(1 for f in found if f[4])))
for f in found:
    print("  %s %s:%d %s=%s" % ("GHOST" if f[4] else "warn ", f[0], f[1], f[2], f[3]))
print("(deploy rewrites all of them in the deployed copy; src/ is untouched)")
print("PASS" if not fails else "FAIL: %d" % len(fails))
sys.exit(1 if fails else 0)
