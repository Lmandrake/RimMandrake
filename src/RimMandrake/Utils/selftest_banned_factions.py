#!/usr/bin/env python3
"""selftest for banned_factions.py: the guard that no faction the owner banned (2026-10-20: "We don't want those...
same with the Space Exchange.") can raid, trade, visit or show in a list.

1. check-repo on THIS repo passes: every banned def carries the banish values, the orbital traders are unfactioned,
   and nothing under src/ names a banned def outside the reasoned allowlist.
2. The checker can SEE: each check is run on a fixture built to fail it, and must fail (a guard that cannot fail is
   not a guard). Fixtures: a repo whose patch drops one field, a repo with a GenStep naming a banned faction, a save
   with a LIVE banned faction, a save with it BANISHED, a save with no factions (UNMEASURED), a dump before and after,
   and the salvager content cut (patch op dropped, a dump still generating a cut faction or pawn kind).
Offline, no game files. Reasoning: design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md."""
import copy
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import banned_factions as bf  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def quiet(_):
    pass


def make_repo(tmp, reg, patch_text, extra_files=None):
    for f in reg["factions"]:
        if f.get("own_def_file"):
            dst = os.path.join(tmp, f["own_def_file"])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(bf.ROOT, f["own_def_file"]), dst)
    p = os.path.join(tmp, reg["patch_file"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(patch_text)
    for rel, text in (extra_files or {}).items():
        q = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        open(q, "w", encoding="utf-8").write(text)


SAVE = """<?xml version="1.0" encoding="utf-8"?>
<savegame><game><world>
<factionManager><allFactions>
<li><def>PlayerColony</def><loadID>1</loadID></li>
{fac}
</allFactions></factionManager>
<worldObjects><worldObjects>{objs}</worldObjects></worldObjects>
</world></game></savegame>"""


def write(tmp, name, text):
    p = os.path.join(tmp, name)
    open(p, "w", encoding="utf-8").write(text)
    return p


def make_dump(tmp, name, reg, banished, content=True):
    cap = os.path.join(tmp, name)
    os.makedirs(os.path.join(cap, "defs"))
    fields = dict(reg["_banish_fields"]) if banished else {"hidden": False, "raidsForbidden": False}
    fields = {k: (v == "true" if v in ("true", "false") else int(v) if v.lstrip("-").isdigit() else v)
              for k, v in fields.items()} if banished else fields
    facs = [{"defName": f["defName"], "fields": fields} for f in reg["factions"]]
    facs.append({"defName": "OutlanderCivil", "fields": {"hidden": False}})
    trd = [{"defName": t, "fields": {"faction": None if banished else "TradersGuild"}}
           for t in reg["orbital_traders_unfactioned"]]
    json.dump({"defs": facs}, open(os.path.join(cap, "defs", "FactionDef.json"), "w"))
    json.dump({"defs": trd}, open(os.path.join(cap, "defs", "TraderKindDef.json"), "w"))
    if content:
        cc = reg["content_cut"]
        quests = [{"defName": q, "fields": {"rootSelectionWeight": 0 if banished else 1}} for q in cc["quests_zero_weight"]]
        quests.append({"defName": "OpportunitySite_Other", "fields": {"rootSelectionWeight": 1}})
        steps = [{"defName": g, "fields": {"linkWithSite": None if banished else "Site_X",
                                           "genStep": {"factionDef": cc["factions"][0]}}} for g in cc["gensteps_unlinked"]]
        steps += [{"defName": g, "fields": {"linkWithSite": "Site_Q", "genStep": {"factionDef": cc["factions"][0]}}}
                  for g in cc["gensteps_unreachable"]]
        steps.append({"defName": "Wreck", "fields": {"linkWithSite": "Site_X", "genStep": {"factionDef": "AncientsHostile"}}})
        tsm = [{"defName": t["def"], "fields": {"root": {"options": [
            {"thingSetMaker": {"pawnKind": "TradersGuild_Citizen"}}]
            + ([] if banished else [{"thingSetMaker": {"pawnKind": t["pawnKind"]}}])}}}
            for t in cc["thingsetmaker_pawn_options_removed"]]
        for name, defs in (("QuestScriptDef", quests), ("GenStepDef", steps), ("ThingSetMakerDef", tsm)):
            json.dump({"defs": defs}, open(os.path.join(cap, "defs", name + ".json"), "w"))
    return cap


def add_defs(cap, def_type, extra):
    p = os.path.join(cap, "defs", def_type + ".json")
    data = json.load(open(p))
    data["defs"].extend(extra)
    json.dump(data, open(p, "w"))


def main():
    reg = bf.load_registry()
    patch_path = os.path.join(bf.ROOT, reg["patch_file"])
    patch_text = open(patch_path, encoding="utf-8").read()

    # 1. the real repo
    lines = []
    check("check-repo passes on this repo", bf.check_repo(reg, out=lines.append) == bf.PASS, "; ".join(lines))
    check("registry is not empty", len(reg["factions"]) >= 3, str(len(reg["factions"])))

    tmp = tempfile.mkdtemp(prefix="selftest_banned_factions_")
    try:
        # 2a. the patch loses raidsForbidden for TradersGuild -> must fail
        broken = patch_text.replace(
            '<value><raidsForbidden>true</raidsForbidden></value>\n          </match>',
            '<value><raidsForbidden>false</raidsForbidden></value>\n          </match>', 1)
        check("fixture edit applied", broken != patch_text)
        r1 = os.path.join(tmp, "r1")
        make_repo(r1, reg, broken)
        check("check-repo FAILS when a banish field is wrong",
              bf.check_repo(reg, root_dir=r1, out=quiet) == bf.FAIL)

        # 2b. an orbital trader keeps its faction -> must fail
        t0 = reg["orbital_traders_unfactioned"][0]
        cut = patch_text.replace('/Defs/TraderKindDef[defName="%s"]/faction' % t0, '/Defs/TraderKindDef[defName="X"]/faction')
        r2 = os.path.join(tmp, "r2")
        make_repo(r2, reg, cut)
        check("check-repo FAILS when an orbital trader keeps its faction",
              bf.check_repo(reg, root_dir=r2, out=quiet) == bf.FAIL)

        # 2c. a GenStep names a banned faction -> must fail; the same name in a comment must not
        r3 = os.path.join(tmp, "r3")
        make_repo(r3, reg, patch_text, {
            "src/RimMandrake/Fake/Defs/GenStep.xml":
                "<Defs><GenStepDef><defName>X</defName><genStep><farmerFaction>RM_Faction_CombHolds"
                "</farmerFaction></genStep></GenStepDef></Defs>"})
        out3 = []
        check("check-repo FAILS on an XML reference to a banned faction",
              bf.check_repo(reg, root_dir=r3, out=out3.append) == bf.FAIL and any("GenStep.xml" in x for x in out3))
        r4 = os.path.join(tmp, "r4")
        make_repo(r4, reg, patch_text, {
            "src/RimMandrake/Fake/Defs/Note.xml": "<Defs><!-- was RM_Faction_CombHolds --></Defs>",
            "src/RimMandrake/Fake/Source/A.cs": "// TradersGuild in a comment\nclass A { string s = \"OutlanderCivil\"; }",
            "src/RimMandrake/Fake/Source/B.cs": "class B { string s = \"TradersGuild\"; }"})
        out4 = []
        rc4 = bf.check_repo(reg, root_dir=r4, out=out4.append)
        check("comments are not references; a C# string literal is",
              rc4 == bf.FAIL and any("B.cs" in x for x in out4) and not any(("A.cs" in x) or ("Note.xml" in x) for x in out4),
              "; ".join(out4))

        # 2d. an empty registry is UNMEASURED, never a pass
        empty = copy.deepcopy(reg)
        empty["factions"], empty["orbital_traders_unfactioned"] = [], []
        check("empty registry -> UNMEASURED", bf.check_repo(empty, root_dir=r3, out=quiet) == bf.UNMEASURED)

        # 3. saves
        live = write(tmp, "live.rws", SAVE.format(
            fac="<li><def>TradersGuild</def><loadID>23</loadID><name>Space Exchange</name></li>",
            objs="<li><def>SpaceSettlement</def><faction>Faction_23</faction></li>"))
        check("check-save FAILS on a LIVE banned faction", bf.check_save(reg, live, out=quiet) == bf.FAIL)
        half = write(tmp, "half.rws", SAVE.format(
            fac="<li><def>TradersGuild</def><loadID>23</loadID><hidden>True</hidden></li>", objs=""))
        check("check-save FAILS when hidden but not defeated", bf.check_save(reg, half, out=quiet) == bf.FAIL)
        ban = write(tmp, "ban.rws", SAVE.format(
            fac="<li><def>TradersGuild</def><loadID>23</loadID><hidden>True</hidden><defeated>True</defeated></li>",
            objs="<li><def>Settlement</def><faction>Faction_1</faction></li>"))
        check("check-save PASSES on a BANISHED faction", bf.check_save(reg, ban, out=quiet) == bf.PASS)
        zero = write(tmp, "zero.rws", SAVE.format(fac="", objs="").replace(
            "<li><def>PlayerColony</def><loadID>1</loadID></li>", ""))
        check("check-save on a save with no factions -> UNMEASURED", bf.check_save(reg, zero, out=quiet) == bf.UNMEASURED)
        # def-hidden resolved through a dump: stored hidden absent, def hidden true, defeated true -> pass
        cap_ok = make_dump(tmp, "dump_ok", reg, banished=True)
        viadump = write(tmp, "viadump.rws", SAVE.format(
            fac="<li><def>RM_Faction_CombHolds</def><loadID>9</loadID><defeated>True</defeated></li>", objs=""))
        check("check-save resolves def.hidden through --dump", bf.check_save(reg, viadump, cap_ok, out=quiet) == bf.PASS)
        check("check-save without --dump does not assume hidden", bf.check_save(reg, viadump, out=quiet) == bf.FAIL)

        # 4. dumps
        cap_bad = make_dump(tmp, "dump_bad", reg, banished=False)
        check("check-dump PASSES after the banish", bf.check_dump(reg, cap_ok, out=quiet) == bf.PASS)
        check("check-dump FAILS before it", bf.check_dump(reg, cap_bad, out=quiet) == bf.FAIL)
        # 5. salvager content cut (owner by card 2026-10-20: "Cut them")
        cap_tsm = make_dump(tmp, "dump_tsm", reg, banished=True)
        add_defs(cap_tsm, "ThingSetMakerDef", [{"defName": "Y", "fields": {"root": {"options": [
            {"thingSetMaker": {"pawnKind": reg["content_cut"]["pawn_kinds"][-1]}}]}}}])
        check("check-dump FAILS on any ThingSetMakerDef that makes a cut pawn kind",
              bf.check_dump(reg, cap_tsm, out=quiet) == bf.FAIL)
        cap_gs = make_dump(tmp, "dump_gs", reg, banished=True)
        add_defs(cap_gs, "GenStepDef", [{"defName": "Z", "fields": {"linkWithSite": "Site_Y",
                                                                     "genStep": {"factionDef": "Salvagers"}}}])
        check("check-dump FAILS on an unlisted site GenStep that makes a cut faction",
              bf.check_dump(reg, cap_gs, out=quiet) == bf.FAIL)
        cap_nc = make_dump(tmp, "dump_nc", reg, banished=True, content=False)
        check("check-dump without quest/genstep/thingsetmaker defs -> UNMEASURED",
              bf.check_dump(reg, cap_nc, out=quiet) == bf.UNMEASURED)
        for label, frm, to in (
                ("quest weight", '<value><rootSelectionWeight>0</rootSelectionWeight></value>\n      </match>',
                 '<value><rootSelectionWeight>1</rootSelectionWeight></value>\n      </match>'),
                ("genstep unlink", '<xpath>/Defs/GenStepDef[defName="Opportunity_OrbitalWreck_Salvagers"]/linkWithSite</xpath>\n    </match>',
                 '<xpath>/Defs/GenStepDef[defName="X"]/linkWithSite</xpath>\n    </match>'),
                ("pod option", 'li[thingSetMaker/pawnKind="Salvager_Pirate"]</xpath>\n    </match>',
                 'li[thingSetMaker/pawnKind="X"]</xpath>\n    </match>')):
            b = patch_text.replace(frm, to, 1)
            check("fixture edit applied: " + label, b != patch_text)
            rr = os.path.join(tmp, "rc_" + label.replace(" ", "_"))
            make_repo(rr, reg, b)
            check("check-repo FAILS when the content cut loses its " + label,
                  bf.check_repo(reg, root_dir=rr, out=quiet) == bf.FAIL)
        check("check-dump on a missing capture -> UNMEASURED",
              bf.check_dump(reg, os.path.join(tmp, "nope"), out=quiet) == bf.UNMEASURED)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, c, detail in RESULTS:
        if not c:
            print("FAIL %s %s" % (name, detail))
    print("%d/%d passed" % (ok, len(RESULTS)))
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
