#!/usr/bin/env python3
"""Selftest for the mod-audit evidence pipeline (src/RimMandrake/Utils/modaudit/). Offline, no game, no network.

    python3 src/RimMandrake/Utils/modaudit/selftest_modaudit.py
"""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def t_universe():
    import universe as u
    check("classify core", u.classify("Ludeon.RimWorld.Odyssey"), "CORE_DLC")
    check("classify ours", u.classify("mandrake.rut.patches"), "OURS")
    check("classify not-ours lookalike", u.classify("mandrakeish.mod"), "THIRD_PARTY")
    check("classify src id", u.classify("weird.id", {"weird.id"}), "OURS")
    inst = {"a.b": [{"folder": "/w/1", "root_kind": "workshop"}, {"folder": "/m/AB", "root_kind": "mods"}]}
    rows = u.resolve([("A.B", "FULL"), ("a.b", "FULL"), ("mandrake.rm.x", "OURS_ABSENT"), ("gone.mod", "FULL")],
                     inst, {"mandrake.rm.x": "src/RimMandrake/X"})
    check("resolve dedup case", len(rows), 3)
    check("resolve prefers local copy", rows[0]["folder"], "/m/AB")
    check("resolve duplicate flag", rows[0]["duplicate"], True)
    check("resolve repo-src fallback", rows[1]["resolution"], "repo-src")
    check("resolve unresolved kept", rows[2]["resolution"], "UNRESOLVED")


def t_defscan():
    import defscan as d
    check("xpath types+names", d.xpath_targets('Defs/ThingDef[defName="A" or defName=\'B\']/comps'),
          (["ThingDef"], ["A", "B"]))
    check("xpath text() form", d.xpath_targets('/Defs/PawnKindDef[defName[text()="Wolf"]]'),
          (["PawnKindDef"], ["Wolf"]))
    check("xpath Name selector is no defName", d.xpath_targets('Defs/ThingDef[@Name="BaseGun"]'), (["ThingDef"], []))
    xml = """<Patch>
      <Operation Class="PatchOperationFindMod"><mods><li>Alpha Animals</li></mods>
        <match Class="PatchOperationSequence"><operations>
          <li Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="X"]/comps</xpath><value/></li>
          <li Class="PatchOperationRemove" MayRequire="Some.Mod"><xpath>Defs/BiomeDef[defName="Y"]/x</xpath></li>
        </operations></match></Operation>
      <Operation Class="PatchOperationReplace"><xpath>Defs/ThingDef[defName="X"]/label</xpath><value/></Operation>
    </Patch>"""
    c = d.patch_file_census(ET.fromstring(xml))
    check("ops_root", c["ops_root"], 2)
    check("ops_all (nested counted)", c["ops_all"], 5)
    check("findmod names", dict(c["findmod_names"]), {"Alpha Animals": 1})
    check("def_names counted per xpath", dict(c["def_names"]), {"X": 2, "Y": 1})
    check("mayrequire lowercased", dict(c["mayrequire"]), {"some.mod": 1})
    check("None root is empty", d.patch_file_census(None)["ops_all"], 0)


def t_diskfacts():
    import diskfacts as df
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "About"))
        p = os.path.join(td, "About", "About.xml")
        open(p, "w").write("""<ModMetaData><packageId>Me.Mod</packageId><name>My Mod</name>
          <supportedVersions><li>1.5</li><li>1.6</li></supportedVersions>
          <modDependencies><li><packageId>brrainz.harmony</packageId><displayName>Harmony</displayName></li></modDependencies>
          <loadAfter><li>ludeon.rimworld</li></loadAfter><url>https://github.com/me/mod</url></ModMetaData>""")
        a = df.parse_about(p)
        check("about packageId is direct child", a["packageId"], "Me.Mod")
        check("about 1.6", a["supports_1_6"], True)
        check("about deps", [x["packageId"] for x in a["modDependencies"]], ["brrainz.harmony"])
        check("about loadAfter", a["loadAfter"], ["ludeon.rimworld"])
        png = os.path.join(td, "t.png")
        open(png, "wb").write(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (256).to_bytes(4, "big") +
                              (128).to_bytes(4, "big") + b"\x08\x06\x00\x00\x00")
        check("png dims", tuple(df.image_dims(png)), (256, 128))
        dll = os.path.join(td, "Assemblies")
        os.makedirs(dll)
        open(os.path.join(dll, "M.dll"), "wb").write(b"MZ..HarmonyLib..DoSettingsWindowContents..")
        disk, tex, dlls, src, lay = df.walk_mod(td)
        check("dll flags", dlls[0]["flags"], ["harmony", "settings_screen"])
        check("texture count", tex["images"], 1)


def t_runtime():
    import runtime as r
    op = lambda ln: ln.startswith("Exception") or ln.startswith("Config error")
    cont = lambda ln: ln.startswith(" ") or ln.startswith("at ")
    bl = r.blocks(["Exception in X", "  at Foo.Bar.Baz ()", "noise", "Config error in Y", "", "  at Q"], op, cont)
    check("blocks count", len(bl), 2)
    check("blocks continuation", bl[0][1], ["  at Foo.Bar.Baz ()"])
    check("blank ends block", bl[1][1], [])
    ns = {"VFECore": "VFECore", "VFECore.Abilities": "VFECore"}
    check("ns longest prefix", r.ns_root_match("VFECore.Abilities.Thing.Method", ns), "VFECore")
    check("ns base never attributes", r.ns_root_match("Verse.Thing.Tick", {"Verse": "x"}), None)
    maps = {"folder": {"2009463077": {"a.mod"}}, "asm": {"vfecore": {"ve.core"}}, "tag": {"my mod": {"m.mod"}},
            "ns": ns, "asm_by_first_ns": {}, "owners": {"Wolf": ["ludeon.rimworld", "z.mod"]}}
    h = r.attribute("Config error in Wolf: bad", ["  at VFECore.Abilities.X.Y ()",
                                                  "  path C:\\Steam\\294100\\2009463077\\Defs"], maps)
    check("attribute kinds", {k: sorted(v) for k, v in h.items()},
          {"z.mod": ["def"], "ve.core": ["frame"], "a.mod": ["path"]})
    check("tag attribution", dict(r.attribute("[My Mod] boom", [], maps)), {"m.mod": {"tag"}})


def t_sources():
    import sources as s
    got = s.extract("see https://github.com/Owner/Repo.git and github.com/owner/repo/issues, "
                    "gitlab.com/g/p and https://github.com/sponsors/x and github.com/Solo")
    check("extract", got, [("github.com", "Owner", "Repo"), ("gitlab.com", "g", "p"), ("github.com", "Solo", None)])


def t_batches():
    import batches as b
    f = lambda **k: dict({"packageId": "x.y", "class": "THIRD_PARTY", "name": "", "description": "",
                          "defs_by_type": {}, "def_total": 0, "dll_count": 0, "texture_count": 0}, **k)
    check("ours", b.categorize(f(packageId="mandrake.rsw.armoury", **{"class": "OURS"})), "ours_rsw_rut")
    check("ours rm", b.categorize(f(packageId="mandrake.rm.flowworks", **{"class": "OURS"})), "ours_rm")
    check("core", b.categorize(f(**{"class": "CORE_DLC"})), "frameworks_libraries")
    check("library no defs", b.categorize(f(dll_count=2)), "frameworks_libraries")
    check("star wars by text", b.categorize(f(name="Star Wars: Clones", def_total=50,
                                                defs_by_type={"ThingDef": 50})), "star_wars_donors")
    check("creatures", b.categorize(f(def_total=40, defs_by_type={"PawnKindDef": 10, "ThingDef": 30})),
          "creatures_animals")
    check("biomes", b.categorize(f(def_total=30, defs_by_type={"BiomeDef": 2, "TerrainDef": 10, "ThingDef": 18})),
          "biomes_world")
    parts = b.split_balanced({"a": list(range(100)), "b": list(range(10))}, target=45)
    check("split sizes", sorted(len(v) for v in parts.values()), [10, 50, 50])
    check("split names", sorted(parts), ["a_1", "a_2", "b"])


def main():
    for t in (t_universe, t_defscan, t_diskfacts, t_runtime, t_sources, t_batches):
        try:
            t()
        except Exception as e:                       # a crash is a failure, named
            FAILS.append("%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    if FAILS:
        print("FAIL %d" % len(FAILS))
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("OK selftest_modaudit (6 groups)")


if __name__ == "__main__":
    main()
