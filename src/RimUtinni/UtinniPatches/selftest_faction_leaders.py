#!/usr/bin/env python3
"""FACTION_LEADER_REPAIR_SIX_EMPTY_THRONES: every concrete FactionDef we author that lists a *_Leader kind in its
Combat group must name a standing leader through fixedLeaderKinds (none of our PawnKindDefs sets factionLeader).
Without one, Faction.TryGenerateNewLeader finds no kind, the leader stays null, and vanilla Faction.FactionTick calls
Log.ErrorOnce("Faction leader for <name> is null") on EVERY tick - measured 2026-10-14 as 360 suppressed repeats/s
from six factions. Offline, XML only."""
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Not leaderless in game: its pawnGroupMakers merge with vanilla TribeBase's (no Inherit="False"), whose Combat group
# carries the factionLeader chief kinds, and it did not raise the null-leader error live (2026-10-14). Whether a
# vanilla chief SHOULD lead it is a separate question, filed on the item, not decided here.
EXEMPT = {"RUT_Jawa_IndigenousTribes"}


def leaderless(path):
    out = []
    for fd in ET.parse(path).getroot().iter("FactionDef"):
        if fd.get("Abstract") == "True":
            continue
        combat_leaders = []
        gm = fd.find("pawnGroupMakers")
        for li in (gm if gm is not None else []):
            if (li.findtext("kindDef") or "").strip() == "Combat" and li.find("options") is not None:
                combat_leaders += [o.tag for o in li.find("options") if o.tag.endswith("_Leader")]
        fl = fd.find("fixedLeaderKinds")
        if combat_leaders and (fl is None or not len(fl)) and fd.findtext("defName") not in EXEMPT:
            out.append((fd.findtext("defName"), combat_leaders))
    return out


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*", "*", "Defs", "**", "*.xml"), recursive=True))
    bad, seen = [], 0
    for f in files:
        try:
            r = leaderless(f)
        except ET.ParseError:
            continue
        seen += sum(1 for _ in ET.parse(f).getroot().iter("FactionDef"))
        bad += [(os.path.relpath(f, ROOT), d, k) for d, k in r]
    ok = seen > 0 and not bad
    print("FactionDefs scanned: %d (a zero here is an instrument failure, not a pass)" % seen)
    for f, d, k in bad:
        print("  LEADERLESS %s in %s: Combat names %s but no fixedLeaderKinds" % (d, f, ", ".join(k)))
    print("%s" % ("1/1 passed" if ok else "0/1 passed"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
