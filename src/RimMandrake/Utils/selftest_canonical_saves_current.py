#!/usr/bin/env python3
"""selftest_canonical_saves_current.py - at every ./publish: the companion's list of canonical saves is what
CANONICAL_SAVE.md names, both saves canon.yml names are guarded, and this check sees a planted fault of each kind.
Page: design/specs/2026-11-23-canonical-save-guard/boundary.md. No game, no build."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon_save
import canonical_saves as CS


def guarded(stem, names, starts):
    s = stem.lower()
    return s in [n.lower() for n in names] or any(s.startswith(p.lower()) for p in starts)


def problems(doc, gen, yml):
    """-> every way the list, the document and canon.yml disagree."""
    try:
        bad = CS.problems(doc, gen)
        names, starts = CS.rule(doc)
    except CS.Unreadable as e:
        return ["UNREADABLE: %s" % e]
    for key in ("start_savegame", "frozen_record_savegame"):
        m = re.search(r"^  %s:\s*([^\s#]+)" % key, yml, re.M)
        if not m:
            bad.append("canon.yml has no planet.%s" % key)
        elif not guarded(re.sub(r"(?i)\.rws$", "", m.group(1)), names, starts):
            bad.append("canon.yml planet.%s is %s, and CANONICAL_SAVE.md does not guard it" % (key, m.group(1)))
    return bad


def main():
    with open(os.path.join(CS.REPO, *CS.DOC.split("/")), encoding="utf-8") as f:
        doc = f.read()
    with open(canon_save.CANON_YML, encoding="utf-8") as f:
        yml = f.read()
    gen = CS.committed()
    fails = problems(doc, gen, yml)
    start = canon_save.start_savegame_name()
    stem = start[:-4]
    plants = {
        "the document names a new canonical save in the block": (doc.replace("```guard\n", "```guard\nASHKARR_NEW_WORLD\n"), gen, yml),
        "the document names a new save in its prose": (doc + "\nCurrent: `ASHKARR_NEW_WORLD_R1.rws`.\n", gen, yml),
        "the document guards a new name start": (doc.replace("```guard\n", "```guard\nWORLD_*\n"), gen, yml),
        "the list lacks the current start": (doc, (gen or "").replace('            "%s",\n' % stem, ""), yml),
        "the list is absent": (doc, None, yml),
        "a hand edit adds a name": (doc, (gen or "").replace('"%s",' % stem, '"%s",\n            "MINE",' % stem), yml),
        "the block is gone": (doc.replace("```guard", "```text"), gen, yml),
        "canon.yml names a start the document does not": (doc, gen, yml.replace("start_savegame: " + start, "start_savegame: OTHER_R9.rws")),
    }
    for name, args in plants.items():
        if not problems(*args):
            fails.append("a planted fault was not seen: " + name)
    for b in fails:
        print("FAIL " + b)
    print("selftest_canonical_saves_current: %s (%d planted faults)" % ("FAIL" if fails else "PASS", len(plants)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
