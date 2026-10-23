#!/usr/bin/env python3
"""retire_cut_mechanics.py — retire the textures of mechanics cut by the 2026-10-23 fluff review, through the art ledger.

The owner ruled by question card (2026-10-23, BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL): "How do you want to rule on the
rest? -> I cut, you veto (Recommended)". Each cut mechanic's art is RETIRED, never purged: artledger.retire archives the
bytes in the art store, deletes the file and appends a `live` event with sha None, so `art.py install <mod> <rel> <sha>`
puts it back if he vetoes. An owner-KEPT picture is refused by the ledger (retiring it needs his words) and is reported,
never forced. Digest of every cut: design/RimMandrake/fluff_cuts_2026-10-23.md.

    python3 src/RimMandrake/Utils/art/retire_cut_mechanics.py <Textures png path>...          # dry run
    python3 src/RimMandrake/Utils/art/retire_cut_mechanics.py --apply <Textures png path>...  # retire
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A  # noqa: E402

REASON = "script:src/RimMandrake/Utils/art/retire_cut_mechanics.py fluff cut 2026-10-23"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    bad = 0
    for p in a.paths:
        path = Path(p).resolve()
        if not path.is_file():
            print("ABSENT  %s" % p)
            continue
        if not a.apply:
            sha = A.sha256_file(path)
            kept = A.cached_index().protected(sha)
            print("%s %s  %s" % ("KEPT   " if kept else "WOULD  ", sha[:12], p))
            continue
        try:
            r = A.retire(path, reason=REASON)
            print("%-7s %s  %s" % (r["status"].upper(), (r.get("old") or "")[:12], p))
        except A.Refused as e:
            bad += 1
            print("REFUSED %s  %s" % (p, e))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
