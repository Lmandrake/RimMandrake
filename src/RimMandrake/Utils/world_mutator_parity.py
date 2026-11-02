"""Does a world save hold exactly the stamped tile mutators? (parity U2, offline)

    python3 src/RimMandrake/Utils/world_mutator_parity.py <save.rws> [--stamp CSV]

Reads every (tile, TileMutatorDef) on the save's world grid and diffs it against the stamp
input (default world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_mutators.csv, retired donor
names ported) with parity_fix_plans.mutator_diff, the same rule w9_run.py stage 4a enforces:
nothing the engine rolled survives except KEEP_DERIVED (RM_SeaCoast).

Exit 0 = PASS: entries > 0, 0 unresolved hashes, 0 rolled entries outside the stamp,
0 stamp entries missing. Exit 1 = FAIL (counts and the top offending defs printed).
A save with no mutator entries at all FAILS: an empty read is a blind instrument, not parity.
Sanity probe (2026-11-02): world/WORLDMAP_gen.rws, an engine-generated world, reads
remove 29,945 / restore 23,007, so the instrument sees rolled entries when they exist.
"""
import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def verdict(n_entries, unresolved, remove, restore):
    """-> (ok, reasons). remove/restore: lists of (tile, def)."""
    why = []
    if n_entries == 0:
        why.append("0 mutator entries read (blind instrument or wrong file)")
    if unresolved:
        why.append("%d entr(ies) with no def in the dump (dump does not match the save's mod set)"
                   % unresolved)
    if remove:
        why.append("%d rolled entr(ies) not in the stamp: %s"
                   % (len(remove), Counter(m for _, m in remove).most_common(8)))
    if restore:
        why.append("%d stamp entr(ies) missing: %s"
                   % (len(restore), Counter(m for _, m in restore).most_common(8)))
    return not why, why


def main(argv=None):
    import parity_fix_plans as p
    import worldmap
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("save")
    ap.add_argument("--stamp", default=os.path.join(p.PAINT, "ASHKARR_WORLDMAP_mutators.csv"))
    a = ap.parse_args(argv)
    byh, _ = worldmap.load_hash_table("TileMutatorDef")
    ents = worldmap.WorldGrid(a.save).mutator_entries()
    unres = sum(1 for _, h in ents if h not in byh)
    named = [(int(t), byh[h]) for t, h in ents if h in byh]
    pm = json.load(open(p.PORT_MAP, encoding="utf-8"))["TileMutatorDef"]
    stamp = p.read_stamp_mutators(a.stamp, pm)
    remove, restore, kept, sup = p.mutator_diff(named, stamp)
    ok, why = verdict(len(ents), unres, remove, restore)
    print("%s: entries %d, stamp %d, unresolved %d, rolled %d, missing %d, kept-derived %d, "
          "superseded-by-kept %d" % (os.path.basename(a.save), len(ents), len(set(stamp)), unres,
                                     len(remove), len(restore), len(kept), len(sup)))
    for r in why:
        print("  FAIL: " + r)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
