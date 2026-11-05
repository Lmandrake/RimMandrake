#!/usr/bin/env python3
"""selftest_deploy_exclude_dirs_shared — the deploy def guard judges exactly the
XML a deploy ships (DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH).

deploy_def_guard.xml_files() once skipped only Source/__pycache__/.git/obj/bin
while deploy_custom_mods.shippable() also skipped art_candidates/art_source/
_artsrc/.vs, so a def file under art_source/ counted as deployed and could raise
a false --apply refusal. For every excluded dir, an XML under it must be absent
from xml_files() and refused by shippable(); a sibling under Defs/ must be seen
by both (the sanity probe that the instrument can see)."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D  # noqa: E402
import deploy_def_guard as G    # noqa: E402

fails = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  [%s]" % detail) if detail else ""))
    if not ok:
        fails.append(name)


def main():
    check("one set: deploy EXCLUDE_DIRS is the guard's set", D.EXCLUDE_DIRS is G.DEPLOY_EXCLUDE_DIRS)
    for d in ("art_candidates", "art_source", "_artsrc", ".vs", "Source", "obj", "bin"):
        check("set holds %s" % d, d in D.EXCLUDE_DIRS)
    with tempfile.TemporaryDirectory() as tmp:
        rels = ["Defs/Real.xml"] + ["%s/Defs/Stray.xml" % d for d in sorted(D.EXCLUDE_DIRS)]
        for rel in rels:
            p = os.path.join(tmp, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write("<Defs/>")
        seen = G.xml_files(tmp)
        check("probe: guard sees Defs/Real.xml", "Defs/Real.xml" in seen, str(sorted(seen)))
        check("probe: deploy ships Defs/Real.xml", D.shippable(os.path.join("Defs", "Real.xml")))
        for rel in rels[1:]:
            shipped = D.shippable(os.path.join(*rel.split("/")))
            check("%s: guard agrees with deploy (shipped=%s)" % (rel, shipped), (rel in seen) == shipped)
    print("FAILURES: %d" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
