#!/usr/bin/env python3
"""check_pseudo_sw_name.py — refuse a non-canon creature name that is not a
pseudo-Star-Wars coinage, or that steals a real canon name.

WHY THIS EXISTS
    Owner, 2026-09-20, twice, the second time sharply:
      "Any non canon beasts need renaming as well into pseudo Star Wars
       equivalents."
      "No! ... When I say pseudo Star Wars I mean it."
      "Do not assign canon to non canon."

    BENCH drafted 23 names and every single one was an English descriptive
    compound — Sandstrider, Spineroller, EmberCarpet, Ferroclaw. MEASURED:
    23 of 23 built from English stems. That is the defect this refuses.

THE TWO RULES, and they are separate
    1. COINED, NOT COMPOUNDED. The name must read as an alien word, not as
       English parts glued together. Star Wars does ship a few English
       compounds (dewback, hawkbat, mudhorn, fanback, clodhopper) — but they
       are 7 of 44 canon creature names, and they are homely two-syllable
       nouns, not fantasy kennings. When in doubt, coin.
    2. DO NOT ASSIGN CANON TO NON-CANON. A coined name must not BE a real
       Star Wars name. Naming an invented beast "acklay" or "kinrath" is
       worse than a bad name: it tells the player a canon creature is present
       when it is not.

THE PHONETIC TARGET — MEASURED from the 37 coined (non-compound) creature
names in design/RimStarWars/canon_references/, 2026-09-20:
    syllables   2 (26/37), 3 (6), 1 (3), 4 (2)     -> two is the default
    length      4-7 letters (31/37)
    final char  a (9), o (4), r (4), k (3), g (2)  -> vowel endings dominate
    doubled     12/37 carry a doubled letter (acklay, cannok, zakkeg, orray)
    k/q/x/z     14/37 carry one                    (gizka, horax, vulptex)

⚠️ This checks SHAPE and COLLISION. It cannot tell you a name is GOOD — that
   is the owner's ear, and his overrule is the signal worth having.

    python3 check_pseudo_sw_name.py Grakkath Ozzeel Sandstrider
    python3 check_pseudo_sw_name.py --file names.txt
"""
import argparse
import pathlib
import re
import sys

CANON_DIR = pathlib.Path(__file__).resolve().parents[3] / "design/RimStarWars/canon_references"

# English stems that keep turning up in bad drafts. Not exhaustive by design:
# it catches the compound habit, it is not a dictionary.
ENGLISH_STEMS = """
sand spine stare barb spore paw horn dune stalk stone back maw mass tusk coil volt
cinder mite grass scrub star vine ember carpet whirl bloom sweet bark tree ash worm
rat strider roller ling ferro iron steel fire flame frost ice rock crag dust wind
storm shadow night day sun moon blood bone tooth fang claw wing tail hide scale
shell quill needle thorn burr web silk gut belly skull eye ear nose snout beak
creep crawl leap run swim dig burrow hunt prowl lurk
""".split()


def canon_names():
    if not CANON_DIR.is_dir():
        sys.exit(f"FAIL: canon library not found at {CANON_DIR}")
    return {d.name.lower().replace("_", "") for d in CANON_DIR.iterdir() if d.is_dir()}


def syllables(word):
    return max(1, len(re.findall(r"[aeiouy]+", word.lower())))


def check(name, canon):
    """-> (ok, [problems], [notes])"""
    bare = re.sub(r"^(RSW_|RUT_|RM_)", "", name)
    low = bare.lower()
    problems, notes = [], []

    if low in canon:
        problems.append(f"COLLIDES with canon entry '{low}' — do not assign canon to non-canon")

    hits = [s for s in ENGLISH_STEMS if s in low]
    if hits:
        problems.append(f"built from English stem(s): {', '.join(sorted(set(hits)))}")

    s = syllables(bare)
    if s > 3:
        problems.append(f"{s} syllables — canon coinages are 2 (26/37) or 3 (6/37)")
    if not 4 <= len(bare) <= 9:
        problems.append(f"{len(bare)} letters — must be 4-9 (canon coinages mostly run 4-7, 31/37)")

    if s != 2:
        notes.append(f"{s} syllables; 2 is the canon default")
    if not re.search(r"(.)\1", low):
        notes.append("no doubled letter (12/37 canon coinages have one)")
    if not re.search(r"[kqxz]", low):
        notes.append("no k/q/x/z (14/37 canon coinages have one)")
    if low[-1] not in "aoeiy":
        notes.append(f"ends '{low[-1]}'; canon coinages favour a vowel (17/37)")

    return (not problems), problems, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*")
    ap.add_argument("--file", help="one name per line")
    a = ap.parse_args()

    names = list(a.names)
    if a.file:
        names += [l.strip() for l in open(a.file, encoding="utf-8") if l.strip()]
    if not names:
        ap.error("give names, or --file")

    canon = canon_names()
    bad = 0
    for n in names:
        ok, problems, notes = check(n, canon)
        mark = "PASS" if ok else "REFUSED"
        if not ok:
            bad += 1
        print(f"{mark:8} {n}")
        for p in problems:
            print(f"         X {p}")
        for t in notes:
            print(f"         . {t}")
    print(f"\n{len(names) - bad}/{len(names)} pass shape+collision "
          f"(checked against {len(canon)} canon entries)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
