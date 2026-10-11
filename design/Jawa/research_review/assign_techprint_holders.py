#!/usr/bin/env python3
"""Assign heldByFactionCategoryTags + techprintCount to every research manifest row.

Item: TECHPRINT_FACTION_GATING_1. The rules are the owner's 2026-09-26 ruling as
written in design/Jawa/worldbuilding/faction_tech_alignment.md (sections 2-4 the
map, section 6 the fifteen rulings). Re-runnable: it rewrites the two columns
from scratch every time and applies the ruled row moves idempotently.

    python3 design/Jawa/research_review/assign_techprint_holders.py           # write
    python3 design/Jawa/research_review/assign_techprint_holders.py --check   # verify only

Engine constraints the output must satisfy (ResearchProjectDef.ConfigErrors,
RimWorld 1.6, VERIFIED in faction_locked_trees.md section 2.2): techprintCount>0
needs a non-empty heldByFactionCategoryTags, and tags with techprintCount 0 is
also an error. So every row is either (0, blank) or (>=1, tags).

The four access classes map onto the pair like this:
  common        0, blank   - researched freely
  jawa-special  0, blank   - known at start via ScenPart_StartingResearch
  ship-only     0, blank   - released by the Memory Core (hiddenPrerequisites)
  faction-held  N, <holder tag>;HuttCartel  - Q11: the fence carries everything
Faction-held rows whose holder is not a live faction (Rakata antiquities,
the Rust Cathedral boon) stay 0/blank: their route is a stage gate / boon, and a
tag no faction carries is the dead-tree defect (faction_locked_trees.md 4.1).
"""
import argparse
import csv
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "infrastructure/output/research_manifest_draft.csv"

NEW_COLS = ("heldByFactionCategoryTags", "techprintCount")
FENCE = "HuttCartel"

# ------------------------------------------------------------ holder -> tag
# categoryTags as built at ca7015ad9 (UtinniPatches FactionDefs + compat patch).
HOLDER_TAG = {
    "Hutts": "HuttCartel",
    "Empire": "Empire",
    "Homestead": "Outlander",
    "Tusken": "Tribal",
    "Enclaves": "FreeDroidEnclaves",
    "Wildsteam": "WildsteamClan",
    "Deepwater": "DeepwaterCompact",
    "Hive": "GeonosianHive",
    "Helix": "AscendantHelix",
    "Moot": "JawaTradeMoot",
    "Junkers": "Pirate",       # vanilla Pirate sets no tag, so Pirate == Junkers here
    # Blackstar: NO tag exists (vanilla Pirate def is also abstract PirateBandBase).
}
NON_FACTION_HOLDERS = {"Rakata": "stage gate (salvation rites)",
                       "RustCathedralDroids": "Rust Cathedral boon (source_gate)"}

# techprintCount by tier - matches the convention the live dump already carries
# (T0-T2 mostly 1, T3-T4 mostly 2).
TIER_COUNT = {"T0": 1, "T1": 1, "T2": 1, "T3": 2, "T4": 2}

# ------------------------------------------------------------ ruled row moves
# defName -> (access, holder, reason). Only rows a ruling or a SOURCED map line
# names, and only where gating breaks no common/critical-path prerequisite.
MOVES = {
    "VFEP_WarcasketRemoval": ("common", "", "Q10: freeing a welded pawn is a mercy - common"),
    "KOTOR_Research_Spice": ("faction-held", "Hutts", "Q14: the Hutts hold spice"),
    "guy762_ResearchKotOR_hutts": ("faction-held", "Hutts", "2.1 Kajidic equipment (Hutt)"),
    "guy762_ResearchKotOR_exchange": ("faction-held", "Hutts", "2.1 the Cartel is this planet's syndicate"),
    "guy762_ResearchKotOR_republic": ("faction-held", "Empire", "2.2 Imperial archives (confiscated)"),
    "guy762_ResearchKotOR_sith": ("faction-held", "Empire", "2.2 Imperial archives (confiscated)"),
    "KOTOR_Research_cloaking": ("faction-held", "Empire", "2.2 Imperial archives: Stygium cloaking"),
    "KOTOR_Research_MoistureVaporator": ("faction-held", "Homestead", "Q4: one water-from-air print, Homestead holds it"),
    "guy762_ResearchKotOR_wookiee": ("faction-held", "Wildsteam", "2.6 bowcaster manufacture - side-quest"),
    "VFES_EMPCannon": ("faction-held", "Deepwater", "Q6: EMP stays common; Deepwater keeps traps and turrets"),
    "Napalm": ("faction-held", "Junkers", "Q12: Junkers hold industrial incendiaries (manufactured firebombs)"),
    "guy762_ResearchKotOR_jawa": ("jawa-special", "", "2.11 clan gear - known at start"),
    "RSW_JawaIon_Weaponry": ("jawa-special", "", "2.11 ion doctrine - known at start"),
}
# Q14: re-point the implant prerequisite off spice so spice can be held.
# Q10: removal stays common, so it cannot sit behind a Junker-held warcasket row.
PREREQ_REPOINT = {"KOTOR_Research_AdvImplants": ("KOTOR_Research_Spice", "Bionics"),
                  "VFEP_WarcasketRemoval": ("VFEP_SpecialisedWarcaskets", "Bionics")}

# Ruled holdings NOT applied, and why - printed by --check so they stay visible.
DEFERRED = {
    "OrbitalTech": "Empire vacsuit (2.2) - prereq of StandardGravtech (ship critical path)",
    "Shuttles": "Empire shuttles (5.1) - prereq of ShipComputerCore/ShipCryptosleep/VGE_GravshipWeaponry",
    "TransportPod": "Empire drop pods (5.1) - prereq of Shuttles",
    "guy762_ResearchKotOR_tusken": "Tusken gear (2.4) - prereq-join anchor of 5 common rows",
    "GoJuiceProduction / OuterRim_StimBelts": "Blackstar combat stims (Q15) - Blackstar has no categoryTag",
}

NOTE_TAG = "TECHPRINT_FACTION_GATING_1: "


def read_manifest(path=MANIFEST):
    text = path.read_text(encoding="utf-8")
    head, body = "", text
    if text.lstrip().startswith("#"):
        head, body = text.split("\n", 1)
        head += "\n"
    rdr = csv.DictReader(io.StringIO(body))
    return head, list(rdr.fieldnames), list(rdr)


def apply(rows):
    by = {r["defName"]: r for r in rows}
    missing = [d for d in list(MOVES) + list(PREREQ_REPOINT) if d not in by]
    if missing:
        sys.exit("manifest has no row for: %s" % ", ".join(missing))
    for dn, (acc, holder, why) in MOVES.items():
        r = by[dn]
        r["access"], r["holder"] = acc, holder
        if NOTE_TAG + why not in r["note"]:
            r["note"] = (r["note"] + " | " if r["note"] else "") + NOTE_TAG + why
    for dn, (old, new) in PREREQ_REPOINT.items():
        r = by[dn]
        p = [x for x in r["prereqs"].split(";") if x.strip()]
        p = [new if x == old else x for x in p]
        r["prereqs"] = ";".join(dict.fromkeys(p))
    for r in rows:
        tags, n = assign(r)
        r["heldByFactionCategoryTags"], r["techprintCount"] = tags, n


def assign(r):
    if r["fate"] == "cut":
        return "", ""
    if r["access"] == "faction-held" and r["holder"] in HOLDER_TAG:
        tags = list(dict.fromkeys([HOLDER_TAG[r["holder"]], FENCE]))
        return ";".join(tags), str(TIER_COUNT[r["tier"]])
    return "", "0"


def check(rows):
    """(failures, warnings). A failure breaks the engine or the ruling; a warning is a
    common row sitting behind a held row - gated in effect, a judgement for BENCH."""
    bad, warn = [], []
    known = set(HOLDER_TAG.values())
    for r in rows:
        tags = [t for t in r.get("heldByFactionCategoryTags", "").split(";") if t]
        n = r.get("techprintCount", "")
        if r["fate"] == "cut":
            if tags or n:
                bad.append("%s: cut row carries techprint fields" % r["defName"])
            continue
        if n == "":
            bad.append("%s: techprintCount unset" % r["defName"])
            continue
        if (int(n) > 0) != bool(tags):
            bad.append("%s: ConfigErrors pair rule broken (count=%s tags=%s)" % (r["defName"], n, tags))
        if any(t not in known for t in tags):
            bad.append("%s: tag no campaign faction carries: %s" % (r["defName"], tags))
        if r["access"] == "faction-held" and r["holder"] not in HOLDER_TAG \
                and r["holder"] not in NON_FACTION_HOLDERS:
            bad.append("%s: faction-held with unknown holder %r" % (r["defName"], r["holder"]))
    # no faction-held row may be a prerequisite of a common/jawa-special/ship-only row
    held = {r["defName"] for r in rows if r.get("techprintCount") not in ("", "0")}
    for r in rows:
        if r["fate"] in ("cut", "merge") or r["defName"] in held:
            continue
        for p in (r["prereqs"] + ";" + r["hidden_prereqs"]).split(";"):
            if p.strip() in held:
                (bad if r["defName"] in MOVES else warn).append("%s (%s) requires techprinted %s" % (r["defName"], r["access"], p.strip()))
    return bad, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the file as it is; write nothing")
    a = ap.parse_args()
    head, cols, rows = read_manifest()
    if not a.check:
        apply(rows)
        for c in NEW_COLS:
            if c not in cols:
                cols.append(c)
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=cols, lineterminator="\r\n")   # the file's own convention
        w.writeheader()
        w.writerows(rows)
        MANIFEST.write_text(head + out.getvalue(), encoding="utf-8")
    bad, warn = check(rows)
    held = [r for r in rows if r.get("techprintCount") not in ("", "0", None)]
    by_tag = {}
    for r in held:
        by_tag.setdefault(r["heldByFactionCategoryTags"].split(";")[0], []).append(r["defName"])
    print("rows %d | techprinted %d | %s" % (len(rows), len(held),
          ", ".join("%s %d" % (t, len(v)) for t, v in sorted(by_tag.items()))))
    print("deferred (ruled, not applied): " + "; ".join("%s - %s" % kv for kv in DEFERRED.items()))
    for b in warn:
        print("WARN " + b)
    for b in bad:
        print("FAIL " + b)
    print("CHECK %s (%d problems)" % ("PASS" if not bad else "FAIL", len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
