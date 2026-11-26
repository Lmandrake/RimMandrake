#!/usr/bin/env python3
"""selftest_save_ghost_defs.py -- save_ghost_defs.py finds and strips every shape of a deleted-def reference, keeps
every other byte, and refuses the shapes it has no safe rule for.

A mini-save (CRLF, tabs) holds each shape that R3 held (SLAUGHTER_ROWS_PRUNE_GHOSTS_IN_PEN, 2026-11-26), beside a
living twin of each that must survive. Planted faults: a ghost thing whose id is referenced elsewhere, a ghost in an
element shape with no rule, and a save with no factions (UNMEASURED, never NONE).
    python3 src/RimMandrake/Utils/selftest_save_ghost_defs.py        exit 0 pass, 1 fail
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_ghost_defs as g  # noqa: E402

GHOSTS = {"RSW_Ghost", "RSW_GhostEgg", "RSW_GhostLeather", "RSW_GhostDrug", "RSW_GhostFaction"}

MINI = """<?xml version="1.0" encoding="utf-8"?>
<savegame>
\t<game>
\t\t<foodRestrictionDatabase><foodRestrictions><li><filter><allowedDefs>
\t\t\t<li>Kibble</li>
\t\t\t<li>RSW_GhostEgg</li>
\t\t\t<li>EggChickenFertilized</li>
\t\t</allowedDefs></filter></li></foodRestrictions></foodRestrictionDatabase>
\t\t<drugPolicyDatabase><policies><li><drugs>
\t\t\t<li>
\t\t\t\t<drug>RSW_GhostDrug</drug>
\t\t\t\t<allowedForAddiction>True</allowedForAddiction>
\t\t\t</li>
\t\t\t<li>
\t\t\t\t<drug>Beer</drug>
\t\t\t\t<allowedForAddiction>True</allowedForAddiction>
\t\t\t</li>
\t\t</drugs></li></policies></drugPolicyDatabase>
\t\t<maps><li><autoSlaughterManager><configs>
\t\t\t<li>
\t\t\t\t<animal>RSW_Ghost</animal>
\t\t\t\t<maxTotal>-1</maxTotal>
\t\t\t</li>
\t\t\t<li>
\t\t\t\t<animal>Muffalo</animal>
\t\t\t\t<maxTotal>-1</maxTotal>
\t\t\t</li>
\t\t</configs></autoSlaughterManager></li></maps>
\t\t<world>
\t\t\t<info><factions>
\t\t\t\t<li>OutlanderCivil</li>
\t\t\t\t<li>RSW_GhostFaction</li>
\t\t\t</factions></info>
\t\t\t<factionManager><allFactions>
\t\t\t\t<li>
\t\t\t\t\t<def>OutlanderCivil</def>
\t\t\t\t\t<loadID>0</loadID>
\t\t\t\t\t<relations>
\t\t\t\t\t\t<li>
\t\t\t\t\t\t\t<other>Faction_7</other>
\t\t\t\t\t\t\t<kind>Hostile</kind>
\t\t\t\t\t\t</li>
\t\t\t\t\t\t<li>
\t\t\t\t\t\t\t<other>Faction_1</other>
\t\t\t\t\t\t\t<kind>Neutral</kind>
\t\t\t\t\t\t</li>
\t\t\t\t\t</relations>
\t\t\t\t</li>
\t\t\t\t<li>
\t\t\t\t\t<leader>null</leader>
\t\t\t\t\t<def>RSW_GhostFaction</def>
\t\t\t\t\t<loadID>7</loadID>
\t\t\t\t\t<relations>
\t\t\t\t\t\t<li>
\t\t\t\t\t\t\t<other>Faction_0</other>
\t\t\t\t\t\t\t<kind>Hostile</kind>
\t\t\t\t\t\t</li>
\t\t\t\t\t</relations>
\t\t\t\t</li>
\t\t\t</allFactions></factionManager>
\t\t\t<components><li Class="VEF.Factions.NewFactionSpawningState"><ignoredFactions>
\t\t\t\t<li>RSW_GhostFaction</li>
\t\t\t</ignoredFactions></li></components>
\t\t\t<worldPawns><pawnsAlive><li>
\t\t\t\t<apparel><wornApparel><innerList>
\t\t\t\t\t<li>
\t\t\t\t\t\t<def>Apparel_Cape</def>
\t\t\t\t\t\t<id>Apparel_Cape1</id>
\t\t\t\t\t\t<stuff>RSW_GhostLeather</stuff>
\t\t\t\t\t\t<customizationData IsNull="True" />
\t\t\t\t\t</li>
\t\t\t\t</innerList></wornApparel></apparel>
\t\t\t\t<inventory><innerContainer><innerList>
\t\t\t\t\t<li Class="ThingWithComps">
\t\t\t\t\t\t<def>RSW_GhostDrug</def>
\t\t\t\t\t\t<id>RSW_GhostDrug9</id>
\t\t\t\t\t\t<questTags IsNull="True" />
\t\t\t\t\t</li>
\t\t\t\t\t<li Class="ThingWithComps">
\t\t\t\t\t\t<def>Beer</def>
\t\t\t\t\t\t<id>Beer10</id>
\t\t\t\t\t</li>
\t\t\t\t</innerList></innerContainer></inventory>
\t\t\t</li></pawnsAlive></worldPawns>
\t\t</world>
\t</game>
</savegame>
""".replace("\n", "\r\n")

MUST_STAY = ("<li>Kibble</li>", "<li>EggChickenFertilized</li>", "<drug>Beer</drug>", "<animal>Muffalo</animal>",
             "<li>OutlanderCivil</li>", "<other>Faction_1</other>", "<def>Apparel_Cape</def>", "<id>Beer10</id>",
             "<stuff>Leather_Plain</stuff>", '<customizationData IsNull="True" />')
MUST_GO = ("RSW_Ghost", "Faction_7")

fails = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def run(tmp, text, name):
    p = os.path.join(tmp, name)
    with open(p, "wb") as f:
        f.write(text.encode())
    return p


with tempfile.TemporaryDirectory() as tmp:
    src = run(tmp, MINI, "mini.rws")
    check(g.cmd_check(src, GHOSTS) == g.FOUND, "check reads FOUND on the mini-save")
    out = os.path.join(tmp, "out.rws")
    check(g.cmd_strip(src, out, GHOSTS, "Leather_Plain", False) == g.NONE and not os.path.exists(out),
          "strip without --apply writes nothing")
    rc = g.cmd_strip(src, out, GHOSTS, "Leather_Plain", True)
    check(rc == g.NONE, "strip --apply ends NONE (its own check on OUT)")
    new = open(out, "rb").read().decode()
    for s in MUST_STAY:
        check(s in new, f"kept: {s}")
    for s in MUST_GO:
        check(s not in new, f"gone: {s}")
    check("\n" not in new.replace("\r\n", ""), "line ends stay CRLF, no bare LF left")
    check("\t\t\t\t\t\t<li>\r\n\t\t\t\t\t\t\t<other>Faction_1" in new, "kept rows keep their indentation")
    check(g.cmd_strip(src, out, GHOSTS, "Leather_Plain", True) == g.FOUND, "--apply refuses an existing OUT")
    check(g.cmd_check(out, GHOSTS) == g.NONE, "check reads NONE on the stripped save")

    # planted fault: the ghost thing's id is named elsewhere
    bad = run(tmp, MINI.replace("<other>Faction_1</other>", "<other>Faction_1</other><t>Thing_RSW_GhostDrug9</t>"),
              "ref.rws")
    check(g.cmd_strip(bad, os.path.join(tmp, "o2.rws"), GHOSTS, "Leather_Plain", True) == g.FOUND
          and not os.path.exists(os.path.join(tmp, "o2.rws")), "refuses a ghost thing whose id is referenced")
    # planted fault: a ghost in a shape with no rule
    bad = run(tmp, MINI.replace("<maxTotal>-1</maxTotal>", "<maxTotal>-1</maxTotal><hediff>RSW_Ghost</hediff>", 1),
              "shape.rws")
    check(g.cmd_strip(bad, os.path.join(tmp, "o3.rws"), GHOSTS, "Leather_Plain", True) == g.FOUND,
          "refuses a ghost in an element shape with no rule")
    # planted fault: a ghost stuff with no --stuff-to
    check(g.cmd_strip(src, os.path.join(tmp, "o4.rws"), GHOSTS, "", True) == g.FOUND,
          "refuses a ghost <stuff> with no --stuff-to")
    # blind reader: no factions parsed is UNMEASURED, never NONE
    blind = run(tmp, '<?xml version="1.0"?>\r\n<savegame><game/></savegame>\r\n', "blind.rws")
    check(g.cmd_check(blind, GHOSTS) == g.UNMEASURED, "no factions parsed reads UNMEASURED")
    broken = run(tmp, "<savegame><game>", "broken.rws")
    check(g.cmd_check(broken, GHOSTS) == g.UNMEASURED, "an unparseable file reads UNMEASURED")
    # the real name set: the prune list resolves and is not empty
    names, _alive = g.resolve_names(None)
    check(len(names) > 40 and "RSW_RoyalRhino" in names, f"the prune name set resolves ({len(names)} names)")
    # implied defs: the game makes Corpse_<race> from each race, and R3's food filters named 282 of them after the
    # first strip (the 2026-11-26 load of R3 logged one Could not load reference per row; the check read NONE)
    check("Corpse_RSW_PustuleHornet" in names, "the name set holds the implied Corpse_ def of a deleted race")
    corpse = run(tmp, MINI.replace("<li>Kibble</li>", "<li>Kibble</li>\r\n\t\t\t<li>Corpse_RSW_Ghost</li>"),
                 "corpse.rws")
    check(g.cmd_check(corpse, g.with_implied(GHOSTS)) == g.FOUND and "Corpse_RSW_Ghost" in g.with_implied(GHOSTS)
          and "Corpse_Muffalo" not in g.with_implied(GHOSTS), "with_implied adds Corpse_ of each ghost name only")
    # implied Meat_<race>: the same R3 load logged 42 Meat_ rows of deleted races (Meat_RSW_AcidSlug x6 among them)
    check("Meat_RSW_AcidSlug" in names, "the name set holds the implied Meat_ def of a deleted race")
    check("Meat_RSW_Ghost" in g.with_implied(GHOSTS) and "Meat_Muffalo" not in g.with_implied(GHOSTS),
          "with_implied adds Meat_ of each ghost name only")
    # a map <thing> of a deleted def: R3 held one RM_CaveDripSource on map 0, and strip climbed past the <thing> to the
    # whole map <li> and refused (2026-11-26). The rule removes the <thing> block whole and keeps its neighbours.
    things = ("\t\t<maps><li><things>\r\n"
              "\t\t\t<thing Class=\"ThingWithComps\">\r\n\t\t\t\t<def>Kibble</def>\r\n\t\t\t\t<id>Kibble5</id>\r\n"
              "\t\t\t</thing>\r\n"
              "\t\t\t<thing Class=\"ThingWithComps\">\r\n\t\t\t\t<def>RSW_Ghost</def>\r\n\t\t\t\t<id>RSW_Ghost21193</id>\r\n"
              "\t\t\t\t<comps><li><x>1</x></li></comps>\r\n\t\t\t</thing>\r\n"
              "\t\t\t<thing>\r\n\t\t\t\t<def>Steel</def>\r\n\t\t\t\t<id>Steel7</id>\r\n\t\t\t</thing>\r\n"
              "\t\t</things></li></maps>\r\n")
    assert "\t\t<maps><li>" in MINI
    tmini = MINI.replace("\t\t<maps><li>", things + "\t\t<maps><li>", 1)
    tsrc = run(tmp, tmini, "thing.rws")
    tout = os.path.join(tmp, "thing_out.rws")
    check(g.cmd_strip(tsrc, tout, GHOSTS, "Leather_Plain", True) == g.NONE and os.path.exists(tout),
          "strip removes a ghost map <thing> (no refusal)")
    tnew = open(tout, "rb").read().decode() if os.path.exists(tout) else ""
    check("RSW_Ghost21193" not in tnew and "<x>1</x>" not in tnew, "gone: the ghost <thing> block, comps included")
    check("<id>Kibble5</id>" in tnew and "<id>Steel7</id>" in tnew
          and "\t\t\t</thing>\r\n\t\t\t<thing>\r\n\t\t\t\t<def>Steel</def>" in tnew,
          "kept: the live <thing> blocks on both sides, whole lines")
    bad = run(tmp, tmini.replace("<other>Faction_1</other>",
                                 "<other>Faction_1</other><t>Thing_RSW_Ghost21193</t>"), "thingref.rws")
    check(g.cmd_strip(bad, os.path.join(tmp, "o5.rws"), GHOSTS, "Leather_Plain", True) == g.FOUND
          and not os.path.exists(os.path.join(tmp, "o5.rws")), "refuses a ghost map <thing> whose id is referenced")

    # planted fault: a ghost <def> with an <id> that is not its <li>'s first child (the <li> would hold more than it)
    wide = run(tmp, tmini.replace("<maps><li><things>", "<maps><li><index>0</index><def>RSW_Ghost</def><id>9</id><things>",
                                  1), "wide.rws")
    check(g.cmd_strip(wide, os.path.join(tmp, "o6.rws"), GHOSTS, "Leather_Plain", True) == g.FOUND
          and not os.path.exists(os.path.join(tmp, "o6.rws")), "refuses a ghost <def> that is not its <li>'s first child")

print("PASS" if not fails else f"FAIL: {len(fails)}")
sys.exit(1 if fails else 0)
