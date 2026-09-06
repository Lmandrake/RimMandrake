"""
Selftest: retired donor mods stay retired.

Two things are proven here, and the second is the one that matters.

1. `retired_mods.is_retired` matches a whole display name or a whole
   packageId, and nothing else. A substring match would quietly retire
   "Megafauna Bestiary Continued" along with "Megafauna".

2. NO patch file anywhere in `src/` carries a `PatchOperationFindMod` block
   naming a retired mod. This is the regression guard the repo did not have:
   commit bbf66830 stripped three such blocks from Armour_Leather.xml by hand,
   the generator that owns that file would have re-emitted all three on its
   next run, and nothing would have said a word
   (ARMOURY_LEATHER_GEN_DESYNC_1). A resurrect is now a failing selftest
   rather than a discovery weeks later.

A block naming a retired mod is not merely dead weight: `PatchOperationFindMod`
returns TRUE when the mod is absent, so the operations inside it are skipped in
silence -- no error, no log line, nothing to notice.
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from retired_mods import is_retired, entries, filter_rows  # noqa: E402

SRC = os.path.join(ROOT, "src")
FINDMOD = re.compile(
    r"PatchOperationFindMod.*?<mods>(.*?)</mods>", re.S)
LI = re.compile(r"<li>(.*?)</li>", re.S)

fails = []


def check(ok, what):
    if ok:
        print("  ok   %s" % what)
    else:
        print("  FAIL %s" % what)
        fails.append(what)


print("retired_mods: the list itself")
ents = entries()
check(len(ents) >= 4, "fact file carries the four 2026-09-05 retirements")
for e in ents:
    check(is_retired(e["packageId"]), "packageId %s reads retired" % e["packageId"])
    for n in e["modNames"]:
        check(is_retired(n), "name %r reads retired" % n)

print("retired_mods: matching is whole-value, not substring")
check(not is_retired("Megafauna Bestiary Continued"),
      "a longer name containing a retired name is NOT retired")
check(not is_retired("Alpha Animals"), "a live mod is not retired")
check(not is_retired(""), "empty string is not retired")
check(not is_retired(None), "None is not retired")

print("retired_mods: filter_rows drops by either column")
rows = [{"modName": "Megafauna", "packageId": ""},
        {"modName": "", "packageId": "Mlie.BeastsoftheRim"},
        {"modName": "Alpha Animals", "packageId": "sarg.alphaanimals"}]
kept = filter_rows(rows)
check(len(kept) == 1 and kept[0]["modName"] == "Alpha Animals",
      "filter_rows keeps only the live row (kept %d)" % len(kept))

print("no patch file in src/ names a retired mod in a FindMod block")
offenders = []
scanned = 0
for dirpath, dirnames, filenames in os.walk(SRC):
    dirnames[:] = [d for d in dirnames
                   if d not in (".git", "obj", "bin", "Assemblies")]
    for fn in filenames:
        if not fn.endswith(".xml"):
            continue
        p = os.path.join(dirpath, fn)
        try:
            s = io.open(p, encoding="utf-8-sig").read()
        except (IOError, UnicodeDecodeError):
            continue
        scanned += 1
        if "PatchOperationFindMod" not in s:
            continue
        for block in FINDMOD.findall(s):
            for name in LI.findall(block):
                name = name.strip()
                if is_retired(name):
                    offenders.append((os.path.relpath(p, ROOT), name))

check(not offenders,
      "%d xml files scanned, %d FindMod blocks name a retired mod"
      % (scanned, len(offenders)))
for p, name in offenders[:20]:
    print("       %s -> %s" % (p, name))

print("\n%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
sys.exit(1 if fails else 0)
