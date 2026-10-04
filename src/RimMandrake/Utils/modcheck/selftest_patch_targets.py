#!/usr/bin/env python3
"""selftest_patch_targets.py — the xpath replay on a synthetic game + mods, temp dirs only.

Each fixture op is built to land in exactly one status; a replay that cannot tell them apart fails here.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modcheck import patch_targets as PT  # noqa: E402

FAILS = []


def check(name, cond, extra=""):
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{extra}]" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def w(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


ABOUT = '<ModMetaData><name>{name}</name><packageId>{pid}</packageId>{extra}</ModMetaData>'


def build(tmp: Path):
    data = tmp / "Data"
    w(data / "Core" / "About" / "About.xml", "<ModMetaData><packageId>Ludeon.RimWorld</packageId></ModMetaData>")
    w(data / "Core" / "Defs" / "Things.xml", """<Defs>
      <ThingDef><defName>Steel</defName><statBases><Mass>0.5</Mass></statBases></ThingDef>
      <ThingDef Name="BaseGun" Abstract="True"><weaponTags><li>Gun</li></weaponTags></ThingDef>
    </Defs>""")
    roots = tmp / "ws"
    w(roots / "1" / "About" / "About.xml", ABOUT.format(name="Declared Donor", pid="a.donor", extra=""))
    w(roots / "1" / "1.6" / "Defs" / "D.xml", "<Defs><ThingDef><defName>DonorGun</defName><label>d</label></ThingDef></Defs>")
    w(roots / "1" / "LoadFolders.xml", "<loadFolders><v1.6><li>1.6</li></v1.6></loadFolders>")
    w(roots / "2" / "About" / "About.xml", ABOUT.format(name="Undeclared", pid="b.hidden", extra=""))
    w(roots / "2" / "Defs" / "H.xml", "<Defs><ThingDef><defName>HiddenGun</defName><label>h</label></ThingDef></Defs>")
    mod = tmp / "src" / "MyMod"
    w(mod / "About" / "About.xml", ABOUT.format(name="Mine", pid="me.mine",
                                                 extra="<loadAfter><li>a.donor</li></loadAfter>"))
    w(mod / "Defs" / "Own.xml", "<Defs><ThingDef><defName>MyThing</defName></ThingDef></Defs>")
    ops = {
        "add_ok": '<Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="Steel"]/statBases</xpath><value><Beauty>1</Beauty></value></Operation>',
        "relative_ok": '<Operation Class="PatchOperationReplace"><xpath>Defs/ThingDef[defName="MyThing"]</xpath><value><ThingDef><defName>MyThing</defName><label>x</label></ThingDef></value></Operation>',
        "donor_ok": '<Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="DonorGun"]</xpath><value><x/></value></Operation>',
        "located_ok": '<Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="HiddenGun"]</xpath><value><x/></value></Operation>',
        "abstract_ok": '<Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[@Name="BaseGun"]/weaponTags</xpath><value><li>X</li></value></Operation>',
        "missing_child": '<Operation Class="PatchOperationRemove"><xpath>/Defs/ThingDef[defName="Steel"]/noSuchChild</xpath></Operation>',
        "missing_def": '<Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="NowhereGun"]</xpath><value><x/></value></Operation>',
        "guard_idle": '<Operation Class="PatchOperationConditional"><xpath>/Defs/ThingDef[defName="Steel"]/notThere</xpath><match Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="Steel"]</xpath><value><y/></value></match></Operation>',
        "guard_dead": '<Operation Class="PatchOperationConditional"><xpath>/Defs/ThingDef[defName="GhostDef"]/label</xpath><match Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="GhostDef"]</xpath><value><y/></value></match></Operation>',
        "findmod_absent": '<Operation Class="PatchOperationFindMod"><mods><li>Not Installed Mod</li></mods><match Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="AbsentModGun"]</xpath><value><y/></value></match></Operation>',
        "sequence_replay": '<Operation Class="PatchOperationSequence"><operations>'
                           '<li Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="Steel"]</xpath><value><addedNode><z>1</z></addedNode></value></li>'
                           '<li Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="Steel"]/addedNode/z</xpath><value><z>2</z></value></li>'
                           '</operations></Operation>',
        "mayrequire_inert": '<Operation Class="PatchOperationAdd" MayRequire="not.installed"><xpath>/Defs/ThingDef[defName="Steel"]</xpath><value><q/></value></Operation>',
        "unmodelled": '<Operation Class="PatchOperationAddModExtension"><xpath>/Defs/ThingDef[defName="Steel"]</xpath><value><li/></value></Operation>',
    }
    for i, (k, op) in enumerate(ops.items()):
        w(mod / "Patches" / f"{i:02d}_{k}.xml", f"<Patch>{op}</Patch>")
    return data, roots, mod


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        data, roots, mod = build(tmp)
        mods = PT.mod_index(roots=(roots,), src=None, game_data=data)
        res, meta = PT.check_mod(mod, mods=mods, game_data=data, cache=tmp / "cache.json")
        by = {}
        for r in res:
            by.setdefault(r["where"].split("#")[0].split("_", 1)[1].removesuffix(".xml"), []).append(r)

        def st(k):
            return [r["status"] for r in by.get(k, [])]
        check("sanity probe: Core Steel/statBases seen, missing child and bogus def not", PT.sanity(meta["index"]) == [])
        check("sanity probe goes RED on an index without the game Data",
              PT.sanity(PT.DefIndex([mod / "Defs"])) != [])
        check("plain Add on a Core def PASSes", st("add_ok") == ["PASS"], st("add_ok"))
        check("a relative 'Defs/...' xpath resolves on the checked mod's own def", st("relative_ok") == ["PASS"], st("relative_ok"))
        check("a declared (loadAfter) donor's LoadFolders 1.6 def is indexed", st("donor_ok") == ["PASS"], st("donor_ok"))
        check("an undeclared installed mod is found via the location index", st("located_ok") == ["PASS"]
              and len(meta["located"]) == 1, (st("located_ok"), meta["located"]))
        check("an abstract parent by @Name resolves", st("abstract_ok") == ["PASS"], st("abstract_ok"))
        check("a missing child under a real def FAILs and says the def exists",
              st("missing_child") == ["FAIL"] and "def exists" in by["missing_child"][0]["why"])
        check("a def no installed mod has FAILs naming it",
              st("missing_def") == ["FAIL"] and "NowhereGun" in by["missing_def"][0]["why"])
        check("an idle guard over a real def PASSes", st("guard_idle") == ["PASS"], st("guard_idle"))
        check("a guard over an absent def FAILs (can never fire)", st("guard_dead") == ["FAIL"], st("guard_dead"))
        check("a FindMod branch for an uninstalled mod is SKIP, never PASS", "PASS" not in st("findmod_absent")
              and "SKIP" in st("findmod_absent"), st("findmod_absent"))
        check("a Sequence's later op sees the node an earlier op added (replay applies)",
              st("sequence_replay") == ["PASS", "PASS"], st("sequence_replay"))
        check("MayRequire on <Operation> is replayed unconditionally and noted as inert",
              st("mayrequire_inert") == ["PASS"] and "INERT" in by["mayrequire_inert"][0]["why"])
        check("an unmodelled op class is UNMEASURED, not PASS", st("unmodelled") == ["UNMEASURED"], st("unmodelled"))
        check("the location cache was written", (tmp / "cache.json").is_file())
        res2, meta2 = PT.check_mod(mod, mods=mods, game_data=data, cache=tmp / "cache.json")
        check("a cached re-run gives identical verdicts", [r["status"] for r in res2] == [r["status"] for r in res])
    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
