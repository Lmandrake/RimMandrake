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
    # fix 3: reference census for labelled dependants
    dx = ET.fromstring("""<Defs><ThingDef><defName>RSW_Door</defName><thingClass>Building_Door</thingClass>
      <placeWorkers><li>JecsTools.PlaceWorker_Outline</li><li>PlaceWorker_Bare</li></placeWorkers>
      <comps><li Class="FacialAnimationGeneticHeads.CompProps_X"/></comps>
      <genes><li MayRequire="LovelyDovey.Sex.WithRosaline">SEX_AlwaysAphrodor</li></genes>
      <wildAnimals><RSW_Faa>0.5</RSW_Faa></wildAnimals><label>a door</label></ThingDef></Defs>""")
    r = d.xml_refs(dx)
    check("class full refs", sorted(r["class_refs_full"]), ["FacialAnimationGeneticHeads.CompProps_X",
                                                             "JecsTools.PlaceWorker_Outline"])
    check("class bare refs only in type contexts", sorted(r["class_refs_bare"]), ["Building_Door", "PlaceWorker_Bare"])
    check("mayrequire on any element", dict(r["mayrequire_any"]), {"lovelydovey.sex.withrosaline": 1})
    check("def tokens incl. tags, not own defName", ("SEX_AlwaysAphrodor" in r["tokens"], "RSW_Faa" in r["tokens"],
                                                     "RSW_Door" in r["tokens"]), (True, True, False))
    owners = {"SEX_AlwaysAphrodor": {"lovelydovey.sex.withrosaline"}, "RSW_Faa": {"me", "other"},
              "Building_Door": {"ludeon.rimworld"}}
    check("def_refs unique non-core owner only", dict(d.def_refs(r["tokens"], owners, "me", {"ludeon.rimworld"})),
          {"lovelydovey.sex.withrosaline": 1})


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
        check("dll types on a non-.NET blob is []", dlls[0]["types"], [])
        # fix 1: per-version deps + by-version load order
        open(p, "w").write("""<ModMetaData><packageId>a.b</packageId>
          <modDependenciesByVersion><v1.6><li><packageId>Aoba.Framework</packageId></li></v1.6></modDependenciesByVersion>
          <loadAfterByVersion><v1.6><li>Zetrith.Prepatcher</li></v1.6></loadAfterByVersion></ModMetaData>""")
        a = df.parse_about(p)
        check("about deps by version", a["modDependenciesByVersion"], {"v1.6": ["aoba.framework"]})
        check("about loadAfterByVersion", a["loadAfterByVersion"], {"v1.6": ["zetrith.prepatcher"]})
        # fix 2: only Textures/ images outside source-like dirs count
        for sub in ("Source/packages/x/Textures", "Source/packages/y", "1.6/Textures/Things"):
            os.makedirs(os.path.join(td, sub))
            open(os.path.join(td, sub, "i.png"), "wb").write(open(png, "rb").read())
        os.remove(png)
        os.makedirs(os.path.join(td, "1.6", "Mods", "VGE", "Defs", "Things"))
        open(os.path.join(td, "1.6", "Mods", "VGE", "Defs", "Things", "d.xml"), "w").write("<Defs/>")
        disk, tex, dlls, src, lay = df.walk_mod(td)
        check("all images counted", tex["images"], 3)
        check("only Textures/ outside Source counts", tex["images_loaded"], 1)
        check("decoded est is loaded-only", tex["decoded_mb_est"] < tex["decoded_mb_est_all_images"], True)
        check("defs dirs keyed to the Defs folder", lay["defs_dirs"], {"1.6/Mods/VGE/Defs": 1})
    check("texture_is_loaded About", df.texture_is_loaded("About"), False)
    check("texture_is_loaded bin/Textures", df.texture_is_loaded("obj/Textures"), False)
    check("texture_is_loaded common/Textures/A", df.texture_is_loaded("Common/Textures/A"), True)
    import dotnetmeta
    real = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3524247750/1.3/Assemblies/0JecsTools.dll"
    if os.path.isfile(real):
        check("metadata TypeDef read", "JecsTools.PlaceWorker_Outline" in dotnetmeta.type_names(open(real, "rb").read()), True)


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
    # fix 5: false-match sources are REJECTED, found-nothing is INFERRED
    V = lambda url, push: {"status": "VERIFIED", "html_url": url, "pushed_at": push, "license": "MIT", "archived": False}
    mono = {"packageId": "t.le", "steam_url": "https://steam/x", "source_kind": "github", "confidence": "MEASURED",
            "source_url": "https://github.com/MonoMod/MonoMod", "last_push": "2026-10-05",
            "candidates": [{"where": "readme", "host": "github.com", "owner": "MonoMod", "repo": "MonoMod",
                            "verify": V("https://github.com/MonoMod/MonoMod", "2026-10-05")}]}
    r = s.reselect(mono, "t.le", "Tech Level Enforcement", "THIRD_PARTY", False)
    check("monomod rejected -> steam-only", (r["source_kind"], r["confidence"], r["last_push"]), ("steam-only", "INFERRED", None))
    check("rejected candidate marked", r["candidates"][0]["verify"]["status"], "REJECTED")
    check("source_note says searched", r["source_note"].startswith("no source found (searched:"), True)
    two = dict(mono, candidates=[{"host": "github.com", "owner": "pardeike", "repo": "Harmony",
                                  "verify": V("https://github.com/pardeike/Harmony", "x")},
                                 {"host": "github.com", "owner": "me", "repo": "Mod", "verify": V("https://github.com/me/Mod", "y")}])
    check("falls through to next candidate", s.reselect(two, "me.mod", "Mod", "THIRD_PARTY", False)["source_url"],
          "https://github.com/me/Mod")
    check("harmony itself keeps Harmony", s.reselect(two, "brrainz.harmony", "Harmony", "THIRD_PARTY", False)["source_url"],
          "https://github.com/pardeike/Harmony")
    nf = dict(mono, candidates=[{"host": "github.com", "owner": "b", "repo": "StandaloneHotspring", "verify": {"status": "NOT_FOUND"}}])
    r = s.reselect(nf, "b.hs", "Standalone Hot Spring", "THIRD_PARTY", False)
    check("NOT_FOUND is never the source", (r["source_url"], r["source_kind"]), (None, "steam-only"))
    check("wiki repo rejected", s.reject_reason("a", "A", "x", "RimWorldWiki") is not None, True)
    check("rwmt/Publicise rejected", s.reject_reason("a", "A", "rwmt", "Publicise") is not None, True)
    hits = [{"fullName": "kanid99/Rimworld-AutoSeller-VehicleFramework-Patch", "url": "u1"},
            {"fullName": "SmashPhil/Vehicle-Framework", "url": "u2"}]
    r = s.reselect({"packageId": "v", "candidates": [], "steam_url": "x"}, "v", "Vehicle Framework", "THIRD_PARTY", False, hits)
    check("search: non-resembling hit skipped, next taken", (r["source_url"], r["confidence"]), ("u2", "INFERRED"))
    check("resembles", (s.resembles("HugsLib", "RimworldHugsLibChecker"), s.resembles("XML Extensions", "XmlExtensions"),
                        s.resembles("Sand Castles", "SandCastleMod")), (False, True, True))


def t_depgraph():
    import depgraph as g
    about = {"aoba.fortress.industrial": {"modDependenciesByVersion": {"v1.5": ["brrainz.harmony"], "v1.6": ["aoba.framework"]}},
             "krkr.rule56": {"modDependenciesByVersion": {"v1.6": ["zetrith.prepatcher"]}},
             "ours.x": {"loadAfter": ["LeutianKane.MineablesOR"], "loadAfterByVersion": {"v1.6": ["z.z"]}},
             "aoba.framework": {"name": "Fortified Features Framework"}, "zetrith.prepatcher": {}, "z.z": {},
             "leutiankane.mineablesor": {}, "brrainz.harmony": {}, "sd.fa.geneticheadsframework": {}, "f.user": {},
             "jecrell.jecstools": {}, "sex.r": {}}
    patches = {"f.user": {"findmod_names": {"Fortified Features Framework": 2}, "targets_owner_mods": {"z.z": 3}}}
    refs = {"sd.fa.geneticheadsbiotech": {"class_refs_full": {"FacialAnimationGeneticHeads.CompX": 11}},
            "ours.x": {"class_refs_full": {"JecsTools.PlaceWorker_Outline": 2}, "class_refs_bare": {"Verse_Bare": 1},
                       "mayrequire_any": {"sex.r": 1}, "def_refs_owner_mods": {"sex.r": 1}}}
    types = {"sd.fa.geneticheadsframework": ["FacialAnimationGeneticHeads.CompX"],
             "jecrell.jecstools": ["JecsTools.PlaceWorker_Outline", "RimWorld.Verse_Bare", "Other.NotBare"],
             "a": ["Shared.T"], "b": ["Shared.T"], "c": ["Shared.T"], "d": ["Shared.T"]}
    known = set(about) | {"sd.fa.geneticheadsbiotech"}
    e = g.build(about, patches, refs, types, known)
    check("hard_dep_v1.6 edge", dict(e["aoba.framework"]["aoba.fortress.industrial"]), {"hard_dep_v1.6": 1})
    check("findmod by About name", dict(e["aoba.framework"]["f.user"]), {"findmod": 2})
    check("v1.5-only dep makes no edge", "aoba.fortress.industrial" in e["brrainz.harmony"], False)
    check("prepatcher via rule56", list(e["zetrith.prepatcher"]), ["krkr.rule56"])
    check("load_after lowercased + by-version", (dict(e["leutiankane.mineablesor"]["ours.x"]), dict(e["z.z"]["ours.x"])),
          ({"load_after": 1}, {"load_after": 1}))
    check("class_ref full", dict(e["sd.fa.geneticheadsframework"]["sd.fa.geneticheadsbiotech"]), {"class_ref": 11})
    check("class_ref full + implicit-ns bare", dict(e["jecrell.jecstools"]["ours.x"]), {"class_ref": 3})
    check("mayrequire + def_ref", dict(e["sex.r"]["ours.x"]), {"mayrequire": 1, "def_ref": 1})
    e2 = g.build(about, patches, refs, types, known, skip_sources={"ours.x"})
    check("skipped source (Core/DLC never depends on a mod)", "ours.x" in e2["sex.r"], False)
    full, bare = g.type_index(types)
    check("vendored type (4 owners) dropped", "Shared.T" in full, False)
    check("bare only in implicit ns", ("Verse_Bare" in bare, "NotBare" in bare), (True, False))
    check("detail shape", g.detail(e["z.z"]), [{"packageId": "f.user", "kinds": ["patch_xpath"], "refs": 3},
                                              {"packageId": "ours.x", "kinds": ["load_after"], "refs": 1}])


def t_assemble():
    import assemble as a
    T = lambda xs: ["ThingDef/%s" % x for x in xs]
    check("shell at 90%", a.cherry_shell(T("abcdefghij"), set(T("abcdefghi"))), (9, True))
    check("not a shell at 26 of 30", a.cherry_shell(T(range(30)), set(T(range(26)))), (26, False))
    check("no defs is no shell", a.cherry_shell([], set()), (0, False))
    infra = ["SoundDef/s%d" % i for i in range(30)]
    check("shell judged on content defs, infra leftovers ignored", a.cherry_shell(T(range(20)) + infra, set(T(range(19)))),
          (19, True))
    check("defs outside loaded dirs (old version folders apart)",
          a.defs_outside({"1.6/Defs": 5, "1.6/Mods/VGE/Defs": 7, "Defs": 2, "1.5/Defs": 3, "v1.4/Defs": 1},
                         ["1.6/Defs", "Defs"]), (18, 7, ["1.6/Mods/VGE/Defs"], 4))
    check("defs_outside ignores Source", a.defs_outside({"Source/x/Defs": 1}, []), (1, 0, [], 0))


def t_batches():
    import batches as b
    f = lambda **k: dict({"packageId": "x.y", "class": "THIRD_PARTY", "name": "", "description": "",
                          "defs_by_type": {}, "def_total": 0, "dll_count": 0, "texture_count": 0}, **k)
    check("ours", b.categorize(f(packageId="mandrake.rsw.armoury", **{"class": "OURS"})), "ours_rsw_rut")
    check("ours rm", b.categorize(f(packageId="mandrake.rm.flowworks", **{"class": "OURS"})), "ours_rm")
    check("core", b.categorize(f(**{"class": "CORE_DLC"})), "frameworks_libraries")
    check("library: code + dependants", b.categorize(f(dll_count=2, dependants=["a.b"])), "frameworks_libraries")
    check("library: code + framework word", b.categorize(f(dll_count=1, name="Some Framework")), "frameworks_libraries")
    check("code-only, nobody depends -> behaviour/QoL", b.categorize(f(dll_count=2)), "code_tweaks_qol_ui")
    check("star wars by text", b.categorize(f(name="Star Wars: Clones", def_total=50,
                                                defs_by_type={"ThingDef": 50})), "star_wars_donors")
    check("creatures", b.categorize(f(def_total=40, defs_by_type={"PawnKindDef": 10, "ThingDef": 30})),
          "creatures_animals")
    check("biomes", b.categorize(f(def_total=30, defs_by_type={"BiomeDef": 2, "TerrainDef": 10, "ThingDef": 18})),
          "biomes_world")
    parts = b.split_balanced({"a": list(range(100)), "b": list(range(10))}, target=45)
    check("split sizes", sorted(len(v) for v in parts.values()), [10, 50, 50])
    check("split names", sorted(parts), ["a_1", "a_2", "b"])
    one = b.split_balanced({"c": list(range(60))}, target=45)
    check("one chunk keeps plain name", sorted(one), ["c"])
    m = b.merge_small({"x_1": list(range(40)), "x_2": list(range(30)), "tiny": [1, 2], "ours_rm": [3]}, floor=8)
    check("tiny spills into smallest non-ours batch", (len(m["x_2"]), "tiny" in m, len(m["ours_rm"])), (32, False, 1))


def main():
    for t in (t_universe, t_defscan, t_diskfacts, t_runtime, t_sources, t_depgraph, t_assemble, t_batches):
        try:
            t()
        except Exception as e:                       # a crash is a failure, named
            FAILS.append("%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    if FAILS:
        print("FAIL %d" % len(FAILS))
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("OK selftest_modaudit (8 groups)")


if __name__ == "__main__":
    main()
