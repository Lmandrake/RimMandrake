"""gen_junk_roster_cut.py -- FASCINATING_WORLD_JUNK_1: write Patches/AncientJunk_RosterCut.xml from the junk roster.

The roster (design/Jawa/worldbuilding/junk/junk_roster.json) is the data; this patch is derived from it. Every
`cut` row names a def and the vanilla junk GenSteps it is taken out of; every `cut_prefabs` row names a prefab
taken out of a GenStep_ScatterGroupPrefabs. The whole patch sits inside the RimStarWars Patches setting
`junkRosterCut` (default on; off = vanilla scatter).

    python3 gen_junk_roster_cut.py           write the patch
    python3 gen_junk_roster_cut.py --check   exit 1 if the committed patch differs from what the roster makes
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROSTER = os.path.join(REPO, "design", "Jawa", "worldbuilding", "junk", "junk_roster.json")
OUT = os.path.join(HERE, "Patches", "AncientJunk_RosterCut.xml")
GATE = "RimMandrake.StarWars.Patches.RSW_PatchOperationStarWarsPatchesSetting"

HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!--
  AncientJunk_RosterCut.xml        FASCINATING_WORLD_JUNK_1        GENERATED, do not edit by hand.
  Source: design/Jawa/worldbuilding/junk/junk_roster.json via gen_junk_roster_cut.py
  (selftest_junk_roster.py checks this file equals the generator's output).

  Takes the junk the roster CUTS out of vanilla's junk scatter GenSteps. Nothing is deleted: the defs still
  exist for quests, layouts and dungeon rooms that name them; only the scatter stops laying them on maps.
  A group the cut leaves empty is removed with it, so the scatterer never draws from an empty table.
  Inside the Mod Settings gate "Leave earth junk out of the scatter" (junkRosterCut, default on).
-->
<Patch>
  <Operation Class="%s">
    <setting>junkRosterCut</setting>
    <match Class="PatchOperationSequence">
      <operations>
""" % GATE

TAIL = """      </operations>
    </match>
  </Operation>
</Patch>
"""


def op(xpath, comment):
    return ("        <!-- %s -->\n"
            "        <li Class=\"PatchOperationRemove\">\n"
            "          <xpath>%s</xpath>\n"
            "        </li>\n") % (comment, xpath)


def build(roster):
    body = []
    steps = []
    for row in roster["cut"]:
        for step in row["from"]:
            if step not in steps:
                steps.append(step)
            body.append(op('/Defs/GenStepDef[defName="%s"]/genStep/groups/li/things/%s' % (step, row["def"]),
                           "%s: %s" % (row["def"], row["why"])))
    for row in roster.get("cut_prefabs", []):
        for step in row["from"]:
            body.append(op('/Defs/GenStepDef[defName="%s"]/genStep/groups/%s' % (step, row["prefab"]),
                           "%s: %s" % (row["prefab"], row["why"])))
    # A group with no things left would hand the scatterer an empty weighted table. Only groups that held a cut
    # def can empty, but the remove is safe on every step the cut touched (it matches nothing when none empties).
    # PatchOperationRemove fails when its xpath matches nothing, so the empty-group sweep is wrapped in a
    # Conditional: no empty group is the normal case, not an error.
    for step in steps:
        xp = '/Defs/GenStepDef[defName="%s"]/genStep/groups/li[not(things/*)]' % step
        body.append("        <!-- %s: drop any group the cut emptied -->\n"
                    "        <li Class=\"PatchOperationConditional\">\n"
                    "          <xpath>%s</xpath>\n"
                    "          <match Class=\"PatchOperationRemove\">\n"
                    "            <xpath>%s</xpath>\n"
                    "          </match>\n"
                    "        </li>\n" % (step, xp, xp))
    return HEAD + "".join(body) + TAIL


def main():
    roster = json.load(open(ROSTER, encoding="utf-8"))
    text = build(roster)
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text:
            print("STALE %s: run gen_junk_roster_cut.py" % OUT)
            return 1
        print("ok  %s matches the roster" % os.path.relpath(OUT, REPO))
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("WROTE %s (%d cut defs, %d cut prefabs)" % (os.path.relpath(OUT, REPO), len(roster["cut"]),
                                                       len(roster.get("cut_prefabs", []))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
