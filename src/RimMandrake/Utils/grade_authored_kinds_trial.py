#!/usr/bin/env python3
"""Grade an AUTHORED_KINDS_MUST_FIELD_1 attempt offline, against the item's own stop signs.

Written to judge a nemotron BUILD trial (KIMI_GATEWAY_FOR_BUILD_1) without a game load.
Every check below is one of the item's explicit criteria or one of its three stop signs.

Usage: grade_authored_kinds_trial.py <worktree-root>
"""
import re, sys, os
import xml.etree.ElementTree as ET

P = "src/RimUtinni/UtinniPatches/Patches/{}.xml"
FILES = ["DeepDesertTribes", "BlackstarCompany", "GalacticEmpire"]
# vanilla kinds that must never appear in one of OUR combat groups
VANILLA_TRIBAL = re.compile(r"<Tribal_\w+>")
VANILLA_PIRATE = re.compile(r"<(Pirate|Grenadier|Mercenary|Scavenger|Drifter|Thrasher)\w*>")


def combat_blocks(text):
    """The <value> payloads of replaces aimed at a Combat group's options."""
    out = []
    for m in re.finditer(
            r'<xpath>([^<]*pawnGroupMakers[^<]*)</xpath>\s*<value>(.*?)</value>',
            text, re.S):
        out.append((m.group(1), m.group(2)))
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    res, fatal = [], 0

    def check(name, ok, detail=""):
        nonlocal fatal
        res.append((("PASS" if ok else "FAIL"), name, detail))
        if not ok:
            fatal += 1

    texts = {}
    for f in FILES:
        p = os.path.join(root, P.format(f))
        if not os.path.isfile(p):
            check(f"{f} exists", False, "missing")
            continue
        texts[f] = open(p, encoding="utf-8").read()
        try:
            ET.parse(p)
            check(f"{f} parses as XML", True)
        except Exception as e:
            check(f"{f} parses as XML", False, str(e)[:120])

    # STOP SIGN 1 - Inherit="False" on pawnGroupMakers drops Trader/Peaceful/
    # Settlement. 🔑 CALIBRATED against the shipped answer, 2026-08-26: HEAD USES IT
    # on DeepDesertTribes, deliberately, because TribeCivil inherits all twelve groups
    # from TribeBase and a Replace on the child matches ZERO nodes. The item's objection
    # was the DROP, and the file answers it by re-declaring the eight non-combat groups
    # byte-for-byte from Core. So the real check is not "did you use it" but
    # "if you used it, did you put the non-combat groups back".
    for f, t in texts.items():
        used = re.search(r'<pawnGroupMakers[^>]*Inherit\s*=\s*"False"', t)
        if not used:
            check(f'{f}: pawnGroupMakers inheritance intact', True)
            continue
        kinds = set(re.findall(r"<kindDef>(\w+)</kindDef>", t))
        restored = {"Trader", "Peaceful", "Settlement"} <= kinds
        check(f'{f}: Inherit="False" but non-combat groups re-declared', restored,
              "have: " + ",".join(sorted(kinds)) if not restored else
              f"{len(kinds)} group kinds declared")

    # STOP SIGN 2 - no vanilla kinds inside a combat group we rewrote
    for f, pat in (("DeepDesertTribes", VANILLA_TRIBAL),
                   ("BlackstarCompany", VANILLA_PIRATE)):
        if f not in texts:
            continue
        hits = []
        for xp, val in combat_blocks(texts[f]):
            if "Combat" in xp:
                hits += pat.findall(val)
        check(f"{f}: no vanilla kinds in a Combat group", not hits,
              ", ".join(sorted(set(hits))[:6]))

    # CRITERION - our kinds are actually fielded
    for f, needle in (("DeepDesertTribes", "Jawa_DeepDesert_"),
                      ("BlackstarCompany", "Jawa_Blackstar_")):
        if f not in texts:
            continue
        n = texts[f].count(needle)
        check(f"{f}: {needle}* appears at all", n > 0, f"{n} occurrences")
        # a kind is FIELDED either via a Replace on a Combat group's options, or
        # inside a wholesale <pawnGroupMakers> declaration's Combat li - both ship.
        groups = [xp for xp, v in combat_blocks(texts[f])
                  if "Combat" in xp and needle in v]
        declared = re.findall(
            r"<kindDef>Combat</kindDef>.*?</options>", texts[f], re.S)
        inline = [d for d in declared if needle in d]
        check(f"{f}: {needle}* is inside a Combat group", bool(groups or inline),
              f"{len(groups)} replaced + {len(inline)} declared")

    # STOP SIGN 3 - non-combat groups stay vanilla in the two NEW files
    for f in ("DeepDesertTribes", "BlackstarCompany"):
        if f not in texts:
            continue
        # only a REPLACE aimed at a non-combat group counts as touching it; a
        # re-declaration that restores vanilla's own kinds is the sanctioned route.
        touched = [xp for xp, v in combat_blocks(texts[f])
                   if any(k in xp for k in ("Trader", "Peaceful", "Settlement"))]
        check(f"{f}: Trader/Peaceful/Settlement untouched", not touched,
              "; ".join(touched)[:160])

    w = max(len(n) for _, n, _ in res)
    for st, n, d in res:
        print(f"  {st}  {n.ljust(w)}  {d}")
    print(f"\n  {len(res)-fatal}/{len(res)} checks pass"
          f"{'' if not fatal else f'  -  {fatal} FAILED'}")
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
