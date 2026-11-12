"""gen_junk_roster_cut.py -- FASCINATING_WORLD_JUNK_1: write Patches/AncientJunk_RosterCut.xml from the junk roster.

The roster (design/Jawa/worldbuilding/junk/junk_roster.json) is the data; this patch is derived from it. Every
`cut` row names a def and the vanilla junk GenSteps it is taken out of; every `cut_prefabs` row names a prefab
taken out of a GenStep_ScatterGroupPrefabs. The whole patch sits inside the RimStarWars Patches setting
`junkRosterCut` (default on; off = vanilla scatter).

It also writes Patches/AncientJunk_RosterText.xml from the roster's `text` rows: the scavenger label and description of
every kept def that keeps its vanilla picture, inside the `junkReskin` setting (the same switch as the art reskin:
"Star Wars junk ... carry matching names and descriptions").

    python3 gen_junk_roster_cut.py           write both patches
    python3 gen_junk_roster_cut.py --check   exit 1 if a committed patch differs from what the roster makes
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROSTER = os.path.join(REPO, "design", "Jawa", "worldbuilding", "junk", "junk_roster.json")
OUT = os.path.join(HERE, "Patches", "AncientJunk_RosterCut.xml")
OUT_TEXT = os.path.join(HERE, "Patches", "AncientJunk_RosterText.xml")
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


TEXT_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!--
  AncientJunk_RosterText.xml        FASCINATING_WORLD_JUNK_1        GENERATED, do not edit by hand.
  Source: the `text` rows of design/Jawa/worldbuilding/junk/junk_roster.json via gen_junk_roster_cut.py.

  Re-texts the kept junk that keeps its vanilla picture in the scavenger register (what it was, what it yields, what
  it risks), each yield and risk read from the def's own mechanics. Text only: no graphic, size or stat changes.
  Each field is replaced where the def writes it and added where it inherits it. Inside the Mod Settings gate
  "Star Wars junk" (junkReskin, default on), the same switch as the art reskin.
-->
<Patch>
  <Operation Class="%s">
    <setting>junkReskin</setting>
    <match Class="PatchOperationSequence">
      <operations>
""" % GATE


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def field_op(d, tag, value):
    base = '/Defs/ThingDef[defName="%s"]' % d
    return ("        <li Class=\"PatchOperationConditional\">\n"
            "          <xpath>%s/%s</xpath>\n"
            "          <match Class=\"PatchOperationReplace\">\n"
            "            <xpath>%s/%s</xpath>\n"
            "            <value><%s>%s</%s></value>\n"
            "          </match>\n"
            "          <nomatch Class=\"PatchOperationAdd\">\n"
            "            <xpath>%s</xpath>\n"
            "            <value><%s>%s</%s></value>\n"
            "          </nomatch>\n"
            "        </li>\n") % (base, tag, base, tag, tag, esc(value), tag, base, tag, esc(value), tag)


def build_text(roster):
    body = []
    for d in sorted(roster.get("text", {})):
        t = roster["text"][d]
        body.append("        <!-- %s -->\n" % d)
        body.append(field_op(d, "label", t["label"]))
        body.append(field_op(d, "description", t["description"]))
    return TEXT_HEAD + "".join(body) + TAIL


def main():
    roster = json.load(open(ROSTER, encoding="utf-8"))
    text = build(roster)
    pairs = [(OUT, text), (OUT_TEXT, build_text(roster))]
    if "--check" in sys.argv:
        bad = 0
        for path, want in pairs:
            cur = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if cur != want:
                print("STALE %s: run gen_junk_roster_cut.py" % path)
                bad = 1
            else:
                print("ok  %s matches the roster" % os.path.relpath(path, REPO))
        return bad
    for path, want in pairs:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(want)
    print("WROTE %s (%d cut defs, %d cut prefabs) and %s (%d re-texted defs)" % (
        os.path.relpath(OUT, REPO), len(roster["cut"]), len(roster.get("cut_prefabs", [])),
        os.path.relpath(OUT_TEXT, REPO), len(roster.get("text", {}))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
