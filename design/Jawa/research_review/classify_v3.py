#!/usr/bin/env python3
"""RESEARCH_TREE_NORMALIZATION_1 — v3: faction-locked trees.

Reads  design/Jawa/research_review/restructured_model_v2.json  (522 rows)
Writes design/Jawa/research_review/restructured_model_v3.json  (522 rows, v3 fields)

v3 adds four columns per row:
  tab3     the tree it lives in  (None for cut/merge rows)
  tier3    T0..T4, band(cost)    (None for cut/merge rows)
  fate3    untouched | keep | reflavor | cut | merge   (carried from fate2)
  access3  common | faction:<FactionDefName> | jawa-special | ship-only | n/a

Nothing here executes against the game. This is a PROPOSAL artifact.
Coverage-or-refuse: the assertions at the bottom fail loudly rather than
writing a partial model. Run it and read the printed block.

A CUT REMOVES A ResearchProjectDef AND NOTHING ELSE (owner, 2026-09-03).
Every ThingDef / creature / building / map feature a cut row unlocked stays
in the game for the campaign's own repurposing.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "restructured_model_v2.json")
DST = os.path.join(HERE, "restructured_model_v3.json")

# ---------------------------------------------------------------- ruled bands
BANDS = [(600, "T0"), (1600, "T1"), (3000, "T2"), (5000, "T3")]


def band(cost):
    c = float(cost)
    for ceiling, name in BANDS:
        if c <= ceiling:
            return name
    return "T4"


# ------------------------------------------------------- the locked trees (3)
# tree name -> (FactionDef defName, FactionDef categoryTag, tag is NEW?, rows)
LOCKED_TREES = OrderedDict([
    ("The Junker Yards", dict(
        faction="Jawa_Junkers", tag="Pirate", tag_new=False,
        route="raid loot + quest reward (no trader: PirateBandBase has no traderKinds)",
        rows=[
            "VFEP_Warcaskets",
            "VFEP_WarcasketWeaponry",
            "VFEP_AdvancedWarcaskets",
            "VFEP_SpecialisedWarcaskets",
            "VFEP_SpacerWarcaskets",
            "VFEP_SpacerWarcasketWeaponry",
        ])),
    ("The Foundry Hive", dict(
        faction="Jawa_GeonosianFoundryHive", tag="GeonosianHive", tag_new=True,
        route="settlement/caravan/visitor trade (OutlanderFactionBase traders already "
              "carry StockGenerator_Techprints) + quest reward",
        rows=[
            "VFEI2_BasicHivetech",
            "VFEI2_StandardHivetech",
            "VFEI2_ExoticHivetech",
            "guy762_ResearchKotOR_sonic",
            "OuterRim_BattleDroids",
        ])),
    ("The Ascendant Ladder", dict(
        faction="Jawa_AscendantHelix", tag="AscendantHelix", tag_new=True,
        route="trade + the Helix's own specialist medicine/genetics quest line",
        rows=[
            "Biosculpting",
            "Bioregeneration",
            "NeuralSupercharger",
            "Xenogermination",
            "GeneProcessor",
            "Archogenetics",
            "FertilityProcedures",
            "GrowthVats",
        ])),
])

# ------------------------------- locked ROWS that stay in their existing tree
# defName -> (FactionDef defName, categoryTag)
LOCKED_ROWS = {
    # --- the Empire (vanilla `Empire`, categoryTag Empire — already correct today)
    "KOTOR_Research_cloaking":          ("Empire", "Empire"),
    "KOTOR_Research_Lobot":             ("Empire", "Empire"),
    "guy762_ResearchKotOR_lightsabers": ("Empire", "Empire"),
    "guy762_ResearchKotOR_advsabers":   ("Empire", "Empire"),   # NEW gate: chain consistency
    "guy762_ResearchKotOR_saberparts":  ("Empire", "Empire"),
    "guy762_ResearchKotOR_jedi":        ("Empire", "Empire"),
    "guy762_ResearchKotOR_republic":    ("Empire", "Empire"),
    "guy762_ResearchKotOR_echanishields": ("Empire", "Empire"),
    "guy762_ResearchKotOR_sith":        ("Empire", "Empire"),   # WAS Outlander (7 holders)
    # --- the Hutt Cartel
    "guy762_ResearchKotOR_hutts":       ("Jawa_HuttCartel", "HuttCartel"),   # WAS Pirate
    "guy762_ResearchKotOR_exchange":    ("Jawa_HuttCartel", "HuttCartel"),   # WAS Pirate
    # --- the Wildsteam Clan (Wookiee-kin)
    "guy762_ResearchKotOR_wookiee":     ("Jawa_WildsteamClan", "WildsteamClan"),  # WAS Outlander
    # --- the Deep Desert Tribes (+ the Jawa Trade Moot; Tribal stays shared, deliberately)
    "guy762_ResearchKotOR_tusken":      ("TribeCivil", "Tribal"),   # WAS Raider — NO HOLDER, dead row
    # --- the Blackstar Company (vanilla `Pirate` def; needs a categoryTag, has none today)
    "guy762_ResearchKotOR_mando":       ("Pirate", "BlackstarCompany"),   # WAS Pirate -> Junkers, no route
    "guy762_ResearchKotOR_disruptor":   ("Pirate", "BlackstarCompany"),   # WAS Pirate -> Junkers, no route
    # --- the Ascendant Helix, rows that stay in their tree
    "KOTOR_Research_Kolto":             ("Jawa_AscendantHelix", "AscendantHelix"),  # WAS Empire
    "guy762_ResearchKotOR_czerka":      ("Jawa_AscendantHelix", "AscendantHelix"),  # WAS Outlander
}

JAWA_SPECIAL = {
    "guy762_ResearchKotOR_jawa",     # the clan's own gear; techprintCount drops to 0
    "RSW_JawaIon_Weaponry",          # canon: ion is the clan's own doctrine
}

SHIP_ONLY = {
    "MM_Research_AncientShipDesigns",
    "MM_Research_CWShipDesigns",
    "MM_Research_EmpireShipDesigns",
}

# Prereq re-points PROPOSED by this pass (no defName renames; prereq edits only).
PREREQ_REPOINT = {
    # Freeing a pawn welded into a casket must not require allying the welders.
    # Removal stays common in The Shell, so its prereq cannot be a locked row.
    "VFEP_WarcasketRemoval": (["VFEP_SpecialisedWarcaskets"], ["Machining"]),
}


def main():
    rows = json.load(open(SRC, encoding="utf-8"))
    by = {r["defName"]: r for r in rows}

    tree_of = {}
    for tree, spec in LOCKED_TREES.items():
        for dn in spec["rows"]:
            if dn in tree_of:
                sys.exit(f"REFUSE: {dn} assigned to two locked trees")
            tree_of[dn] = tree

    unknown = [dn for dn in list(tree_of) + list(LOCKED_ROWS) + list(JAWA_SPECIAL)
               + list(SHIP_ONLY) + list(PREREQ_REPOINT) if dn not in by]
    if unknown:
        sys.exit(f"REFUSE: defNames not present in v2: {unknown}")

    for r in rows:
        dn = r["defName"]
        r["fate3"] = r["fate2"]

        if r["tab2"] is None:                      # cut / merge — no tree, no access
            r["tab3"], r["tier3"], r["access3"] = None, None, "n/a"
            r["access3_tag"] = None
            continue

        r["tab3"] = tree_of.get(dn, r["tab2"])
        r["tier3"] = band(r["cost2"] if r.get("cost2") else r["cost"])

        if dn in tree_of:
            spec = LOCKED_TREES[tree_of[dn]]
            r["access3"] = "faction:" + spec["faction"]
            r["access3_tag"] = spec["tag"]
        elif dn in LOCKED_ROWS:
            fac, tag = LOCKED_ROWS[dn]
            r["access3"] = "faction:" + fac
            r["access3_tag"] = tag
        elif dn in JAWA_SPECIAL:
            r["access3"], r["access3_tag"] = "jawa-special", None
        elif dn in SHIP_ONLY:
            r["access3"], r["access3_tag"] = "ship-only", None
        else:
            r["access3"], r["access3_tag"] = "common", None

        if dn in PREREQ_REPOINT:
            old, new = PREREQ_REPOINT[dn]
            if r["prereqs"] != old:
                sys.exit(f"REFUSE: {dn} prereqs are {r['prereqs']}, expected {old}")
            r["prereqs3"] = new
        else:
            r["prereqs3"] = r["prereqs"]

    # ------------------------------------------------------------- assertions
    out = []
    P = out.append
    P("=" * 72)
    P("RESEARCH_TREE_NORMALIZATION_1 — v3 coverage assertion")
    P("=" * 72)

    assert len(rows) == 522, f"row count {len(rows)} != 522"
    P(f"rows in  : {len(rows)}")

    assert len({r['defName'] for r in rows}) == 522, "duplicate defName"
    P("defNames : 522 unique, no duplicates")

    assert all(set(("tab3", "tier3", "fate3", "access3")) <= set(r) for r in rows)
    P("v3 fields: tab3/tier3/fate3/access3 present on all 522")

    fates = Counter(r["fate3"] for r in rows)
    P(f"fate3    : {dict(fates)}  (sum {sum(fates.values())})")
    assert sum(fates.values()) == 522

    placed = [r for r in rows if r["tab3"]]
    unplaced = [r for r in rows if not r["tab3"]]
    assert len(placed) + len(unplaced) == 522
    assert all(r["fate3"] in ("cut", "merge") for r in unplaced), \
        "an unplaced row is not cut/merge"
    assert all(r["fate3"] not in ("cut", "merge") for r in placed), \
        "a cut/merge row was placed in a tree"
    P(f"placed   : {len(placed)}   unplaced (cut/merge): {len(unplaced)}")

    trees = Counter(r["tab3"] for r in placed)
    assert sum(trees.values()) == len(placed)
    P(f"trees    : {len(trees)}   per-tree sum {sum(trees.values())} == placed {len(placed)}")
    for t, c in sorted(trees.items(), key=lambda kv: -kv[1]):
        lock = ""
        if t in LOCKED_TREES:
            lock = "   [LOCKED -> " + LOCKED_TREES[t]["faction"] + "]"
        P(f"           {c:3d}  {t}{lock}")

    # band conformance: tier3 must be band(cost3)
    bad = [r["defName"] for r in placed
           if r["tier3"] != band(r["cost2"] if r.get("cost2") else r["cost"])]
    assert not bad, f"tier3 off band: {bad}"
    P(f"bands    : all {len(placed)} placed rows conform to T0<=600 T1<=1600 "
      "T2<=3000 T3<=5000 T4>5000")

    acc = Counter(r["access3"] for r in rows)
    P(f"access3  : {dict(acc)}  (sum {sum(acc.values())})")
    assert sum(acc.values()) == 522

    # every faction-held row names a faction we confirmed present on the planet
    PRESENT = {"Empire", "Jawa_HuttCartel", "OutlanderCivil", "TribeCivil",
               "Jawa_FreeDroidEnclaves", "Jawa_WildsteamClan", "Jawa_DeepwaterCompact",
               "Jawa_GeonosianFoundryHive", "Jawa_AscendantHelix", "Pirate",
               "Jawa_IndigenousTribes", "Jawa_Junkers"}
    held = [r for r in rows if r["access3"].startswith("faction:")]
    ghosts = sorted({r["access3"].split(":", 1)[1] for r in held} - PRESENT)
    assert not ghosts, f"gated on faction(s) NOT on the planet: {ghosts}"
    P(f"holders  : {len(held)} faction-held rows, "
      f"{len({r['access3'] for r in held})} distinct holders, all present on the planet")

    # GATE-LEAK CHECK: no common/jawa-special/ship-only row may require a locked row
    lockednames = {r["defName"] for r in held}
    leaks = []
    for r in rows:
        if r["fate3"] in ("cut", "merge") or r["access3"].startswith("faction:"):
            continue
        for p in (r.get("prereqs3") or []):
            if p in lockednames:
                leaks.append((r["defName"], p))
    assert not leaks, f"GATE LEAK — ungated rows requiring a locked row: {leaks}"
    P(f"gateleak : 0  (no common/jawa-special/ship-only row requires a locked row)")

    # cross-lock check: a locked row's prereqs must be common or in the SAME lock
    cross = []
    for r in held:
        for p in (r.get("prereqs3") or []):
            if p in lockednames and by[p]["access3"] != r["access3"]:
                cross.append((r["defName"], r["access3"], p, by[p]["access3"]))
    assert not cross, f"CROSS-LOCK — locked row requires a DIFFERENTLY locked row: {cross}"
    P("crosslock: 0  (no locked row depends on a differently-locked row)")

    # every prereq referenced by a surviving row still exists and survives
    survivors = {r["defName"] for r in rows if r["fate3"] not in ("cut", "merge")}
    orphan = sorted({p for r in rows if r["defName"] in survivors
                     for p in (r.get("prereqs3") or []) if p not in survivors})
    P(f"orphans  : {len(orphan)} prereq references to non-surviving rows"
      + (f" -> {orphan}" if orphan else ""))

    P("=" * 72)
    P("COVERAGE: 522 in, 522 accounted. ASSERTIONS PASSED.")
    P("=" * 72)

    block = "\n".join(out)
    print(block)

    payload = rows
    with open(DST, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {DST}  ({len(rows)} rows)")

    with open(os.path.join(HERE, "v3_coverage_assertion.txt"), "w", encoding="utf-8") as fh:
        fh.write(block + "\n")


if __name__ == "__main__":
    main()
