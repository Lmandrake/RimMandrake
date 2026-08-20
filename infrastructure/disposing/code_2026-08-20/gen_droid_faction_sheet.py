#!/usr/bin/env python3
"""Build the droid -> faction assignment sheet, same instrument as the race matrix.

77 droid PawnKindDefs across four mods. Unlike xenotypes these are PAWN KINDS, so a
faction fields them through pawnGroupMakers, and a faction that fields droids sets
`humanlikeFaction false` - which is how the KotOR rogue collective does it, and why
xenotypeChances is irrelevant for a droid faction.

    python3 src/RimMandrake/Utils/gen_droid_faction_sheet.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump/defs")
OUT = os.path.join(REPO, "design/Jawa/worldbuilding/review/droid_faction_assignment.html")
PREFILL = OUT.replace(".html", ".prefill.json")
TPL_SRC = os.path.join(HERE, "gen_race_faction_sheet.py")

# only factions that could plausibly field droids
FACTIONS = [
    ("Jawa_FreeDroidEnclaves",    "Free Droid Enclaves", "the freed droids - allies. NEEDS humanlikeFaction false + these kinds"),
    ("Jawa_GeonosianFoundryHive", "Geonosian Foundry Hive", "mass-produces droids in ancient factories; these are Foundry product"),
    ("JDSCIS_CIS_Faction",        "The Confederacy", "battle droids; ships 15 of its own already"),
    ("Empire",                    "The Galactic Empire", "Imperial security and probe droids"),
    ("Jawa_HuttCartel",           "Hutt Cartel", "the Droid Gotra historically served as Hutt muscle"),
    ("Jawa_Junkers",              "the Junkers", "scrap crews - salvaged and half-repaired units"),
    ("Jawa_IndigenousTribes",     "Jawa Trade Moot", "Jawa restore and resell droids; that is the trade"),
    ("UNASSIGNED",                "(no faction)", "def stays, spawnable in dev and quests, occurs organically nowhere"),
]

INVENTED = [
 "guy762_KotORFaction_RogueDroids is NOT a column: it is hidden + permanentEnemy, the "
 "Mechanoid pattern, and it already fields its own 14 hostile kinds. Its roster is left alone.",
 "40 droid kinds default to PlayerColony - the Droid Depot and KotOR 'good' droids. I read "
 "that as the friendly pool and pre-filled the Enclaves from it. Nothing says so explicitly.",
 "Geonosians given a share of everything the Enclaves get, on the ruling that Enclave "
 "chassis are escaped Foundry product - the same models, different owners.",
 "Jawa Trade Moot given a rare share of the cheap civilian droids, because restoring and "
 "reselling droids is what a salvage moot would do. Invented.",
 "The 15 JDSCIS battle droids are left with the Confederacy at A and given to nobody else; "
 "battle droids in Hutt or Jawa hands is a bigger fiction change than it looks.",
]


def main():
    if os.path.exists(PREFILL):
        try:
            if json.load(open(PREFILL)).get("frozen") and "--i-know-this-overwrites-the-owners-decisions" not in sys.argv:
                sys.exit("REFUSING: %s is frozen." % PREFILL)
        except Exception:
            pass

    d = json.load(open(os.path.join(DUMP, "PawnKindDef.json")))["defs"]

    def t(x, k):
        return x.get(k) or ""

    droids = [x for x in d if re.search(r"droid", t(x, "defName") + " " + t(x, "label"), re.I)]

    rows, grid = [], {}
    for x in sorted(droids, key=lambda y: (t(y, "modName"), t(y, "label").lower())):
        dn = t(x, "defName")
        f = x.get("fields") or {}
        power = f.get("combatPower")
        fac = f.get("defaultFactionDef") or ""
        mod = t(x, "modName")
        role = ("combat, power %s" % power) if power else "non-combat / utility"
        rows.append({
            "id": dn, "label": t(x, "label") or dn,
            "genes": power or 0,          # reuse the template's numeric slot as combat power
            "namer": False,
            "desc": "%s · race %s · ships defaulted to %s · %s"
                    % (mod, f.get("race") or "?", fac or "no faction", role),
            "why": "", "contested": False, "wasOrphan": not fac,
        })
        cells = {}
        # pre-fill: the friendly pool goes to the Enclaves; battle droids stay with the CIS
        if fac == "JDSCIS_CIS_Faction":
            cells["JDSCIS_CIS_Faction"] = "A"
            rows[-1]["why"] = "CIS battle droid - left with the Confederacy only"
        elif fac == "guy762_KotORFaction_RogueDroids":
            rows[-1]["why"] = "hostile rogue-collective kind - left to that faction, no column here"
        elif fac == "PlayerColony":
            grade = "A" if (power or 0) <= 45 else "S"
            cells["Jawa_FreeDroidEnclaves"] = grade
            cells["Jawa_GeonosianFoundryHive"] = "S" if grade == "A" else "R"
            if (power or 0) <= 30:
                cells["Jawa_IndigenousTribes"] = "R"
                cells["Jawa_Junkers"] = "R"
            rows[-1]["why"] = "friendly pool (ships as PlayerColony) - Enclave roster"
        elif fac == "OuterRim_GalacticEmpire":
            cells["Empire"] = "S"
            rows[-1]["why"] = "Imperial-issue droid"
        elif fac == "Ancients":
            rows[-1]["why"] = "ancient-danger droid - leave to map generation"
        elif fac == "OuterRim_RogueDroidColony":
            cells["Jawa_FreeDroidEnclaves"] = "S"
            rows[-1]["why"] = "rogue-colony kind; R14 calls that def an empty shell, so reuse the KIND here"
        grid[dn] = cells
        if power and power >= 90:
            rows[-1]["contested"] = True
            rows[-1]["why"] += " · ⚠ heavy unit, power %s" % power

    pre = {"posture": "matrix", "generated": "2026-08-17",
           "meaning": "Per droid kind x faction: A abundant, S some, R rare, N absent. "
                      "Written into each faction's pawnGroupMakers options, weighted "
                      "A=100 S=40 R=10. A faction fielding droids MUST also set "
                      "humanlikeFaction false.",
           "grid": grid, "notes": {}}
    if not os.path.exists(PREFILL):
        json.dump(pre, open(PREFILL, "w"), indent=1)

    src = open(TPL_SRC, encoding="utf-8").read()
    tpl = src[src.find('HTML = r"""') + len('HTML = r"""'):src.rfind('"""')]
    tpl = (tpl.replace("Ash'karr - race x faction matrix", "Ash'karr - droid x faction matrix")
              .replace("race &times; faction matrix", "droid &times; faction matrix")
              .replace("search race…", "search droid, mod or role…")
              .replace("all races", "all droids").replace("contested only", "heavy units only")
              .replace("not fielded today", "ships with no faction")
              .replace("no faction at all", "placed nowhere").replace("placed somewhere", "placed")
              .replace("ashkarr_matrix", "ashkarr_droids")
              .replace("race_faction_assignment.prefill.json", "droid_faction_assignment.prefill.json")
              .replace("'matrix'", "'droidmatrix'")
              .replace("Race descriptions, for review", "Droid roster, for review")
              .replace("+'g'", "+' pow'")
              .replace("<th class=\"first\">race", "<th class=\"first\">droid")
              .replace("races</b>", "droids</b>").replace("placed <b>", "placed <b>"))
    doc = (tpl.replace("__ROWS__", json.dumps(rows))
              .replace("__FACTIONS__", json.dumps(FACTIONS))
              .replace("__PREFILL__", json.dumps(pre))
              .replace("__INVENTED__", json.dumps(INVENTED)))
    open(OUT, "w", encoding="utf-8").write(doc)
    print("droid kinds: %d   factions: %d   cells pre-filled: %d   heavy units flagged: %d"
          % (len(rows), len(FACTIONS) - 1, sum(len(v) for v in grid.values()),
             sum(r["contested"] for r in rows)))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
