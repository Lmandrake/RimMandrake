#!/usr/bin/env python3
"""Selftest for GEOSTONE_BUILD_SIX_LABELS_AWAIT_STAMP: the six geological landmarks are built and ready to stamp.

The need (design/RimMandrake/world_remake_2026-10-19/16_geo_landmarks.md "How it will work"): a map generated on a tile
of a geological landmark has walls of that landmark's stones, whatever biome it lies in; each landmark has a name the
player can travel to, and a Mod Settings switch; nothing places one but the hand-made stamp of the one paint.

What this reads (the shipped defs and C#, against the data of record geo_landmarks.csv):
  D1 one TileMutatorDef per row, defName = id, a category of its own (= its defName), chanceOnNonLandmarkTile 0, and
     an RM_GeoStonesExtension whose stones are the row's stones_now and whose setting is geo<Name>Enabled.
  D2 one LandmarkDef per row, label = the row's name, commonality 0, no nameMaker (AddLandmark then names it by its
     label), an icon, and mutatorChances of exactly one entry: its own mutator, Required.
  C1 RM_GeoStones patches World.NaturalRockTypesIn(PlanetTile) with Postfix_NaturalRockTypesIn, which replaces the
     result only with StonesOf(...) and leaves a biome that forces its rock (forceRockTypes) alone.
  C2 every setting the defs name is a public static bool of RM_EnvironmentalHazardsSettings, default true, scribed
     with default true, and drawn in a NewMapsOnly group.
  C3 the committed RimMandrake.EnvironmentalHazards.dll is built from these sources (.srchash).
Not read here: a generated map's walls (that needs the stamp, which is part of the one paint, BIOME_PAINT_ONCE_AT_THE_END_1).
Named mutants must each turn it red, or the check is blind.

  python3 src/RimMandrake/Utils/remake/selftest_geostones.py            the shipped files
  python3 src/RimMandrake/Utils/remake/selftest_geostones.py --rev REV  the files at a git revision (red run)
"""
import csv, hashlib, io, os, re, subprocess, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
CSV = "design/RimMandrake/world_remake_2026-10-19/geo_landmarks.csv"
DEFS = "src/RimMandrake/EnvironmentalHazards/Defs/GeoLandmarks/RM_GeoLandmarks.xml"
CS = "src/RimMandrake/EnvironmentalHazards/Source/RM_GeoStones.cs"
MOD = "src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs"
SRCHASH = "src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll.srchash"


def read(rev, path):
    if rev:
        r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, path)], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    p = os.path.join(REPO, path)
    return open(p, "rb").read() if os.path.isfile(p) else None


def check(rows, defs, cs, mod, srchash, cs_b, mod_b):
    errs = []
    if defs is None:
        return ["%s is absent: no geological landmark is built" % DEFS]
    try:
        root = ET.fromstring(defs)
    except ET.ParseError as e:
        return ["%s does not parse: %s" % (DEFS, e)]
    muts = {m.findtext("defName"): m for m in root.findall("TileMutatorDef")}
    lms = {m.findtext("defName"): m for m in root.findall("LandmarkDef")}
    settings = set()
    for r in rows:
        d, want_stones = r["id"], r["stones_now"].split(";")
        m = muts.get(d)
        if m is None:
            errs.append("D1 %s: no TileMutatorDef" % d)
        else:
            cats = [li.text for li in m.findall("categories/li")]
            if cats != [d]:
                errs.append("D1 %s: categories %s, not its own (a shared category lets a later mutator drop it)" % (d, cats))
            if (m.findtext("chanceOnNonLandmarkTile") or "").strip() not in ("0", "0.0"):
                errs.append("D1 %s: chanceOnNonLandmarkTile is not 0 (world generation could place it)" % d)
            ext = [li for li in m.findall("modExtensions/li") if li.get("Class", "").endswith("RM_GeoStonesExtension")]
            if len(ext) != 1:
                errs.append("D1 %s: no RM_GeoStonesExtension" % d)
            else:
                got = [li.text for li in ext[0].findall("stones/li")]
                if got != want_stones:
                    errs.append("D1 %s: stones %s, the plan's stones_now %s" % (d, got, want_stones))
                want_setting = "geo" + d[len("RM_Geo_"):] + "Enabled"
                if ext[0].findtext("setting") != want_setting:
                    errs.append("D1 %s: setting %r, not %s" % (d, ext[0].findtext("setting"), want_setting))
                settings.add(ext[0].findtext("setting"))
        lm = lms.get(d)
        if lm is None:
            errs.append("D2 %s: no LandmarkDef" % d)
            continue
        if lm.findtext("label") != r["name"]:
            errs.append("D2 %s: label %r, not the plan's name %r" % (d, lm.findtext("label"), r["name"]))
        if (lm.findtext("commonality") or "").strip() not in ("0", "0.0"):
            errs.append("D2 %s: commonality is not 0 (world generation could place it)" % d)
        if lm.find("nameMaker") is not None:
            errs.append("D2 %s: a nameMaker would replace its fixed name" % d)
        if not (lm.findtext("iconTexturePath") or "").strip():
            errs.append("D2 %s: no icon" % d)
        mc = list(lm.find("mutatorChances") if lm.find("mutatorChances") is not None else [])
        if len(mc) != 1 or mc[0].tag != d or (mc[0].get("Required") or "").lower() != "true":
            errs.append("D2 %s: mutatorChances must be exactly its own %s, Required (AddLandmark rolls every entry)" % (d, d))
    if len(muts) != len(rows) or len(lms) != len(rows):
        errs.append("D1/D2: %d mutators and %d landmarks for %d planned rows" % (len(muts), len(lms), len(rows)))

    if cs is None:
        errs.append("C1 %s is absent" % CS)
    else:
        if not re.search(r"AccessTools\.Method\(typeof\(World\),\s*nameof\(World\.NaturalRockTypesIn\),\s*new\[\]\s*\{\s*typeof\(PlanetTile\)\s*\}\)", cs):
            errs.append("C1 the patch does not target World.NaturalRockTypesIn(PlanetTile)")
        if "nameof(Postfix_NaturalRockTypesIn)" not in cs:
            errs.append("C1 the patch does not install Postfix_NaturalRockTypesIn")
        post = cs.split("public static void Postfix_NaturalRockTypesIn", 1)[-1] if "Postfix_NaturalRockTypesIn(PlanetTile" in cs else ""
        if "forceRockTypes != null" not in post or "if (stones != null) __result = stones;" not in post:
            errs.append("C1 the postfix does not replace the rocks only with StonesOf(...) while leaving forced rock alone")
        so = cs.split("public static List<ThingDef> StonesOf", 1)[-1]
        if "if (biomeForcesRock || mutators == null) return null;" not in so or "if (on(ext)) return ext.stones;" not in so:
            errs.append("C1 StonesOf does not return a switched-on landmark's stones and nothing else")
    for s in sorted(settings):
        if not re.search(r"public static bool %s = true;" % re.escape(s), mod):
            errs.append("C2 %s: not a public static bool of the settings, default true" % s)
        if 'Scribe_Values.Look(ref %s, "%s", true);' % (s, s) not in mod:
            errs.append("C2 %s: not scribed with default true" % s)
        if not re.search(r'Group\(list, "[^"]*", RimMandrake\.Shared\.SettingScope\.NewMapsOnly, new\[\] \{[^}]*"%s"' % re.escape(s), mod) \
                or "ref %s," % s not in mod:
            errs.append("C2 %s: not drawn in a new-maps-only settings group" % s)
    for name, b in (("RM_GeoStones.cs", cs_b), ("RM_EnvironmentalHazardsMod.cs", mod_b)):
        line = [l for l in srchash.splitlines() if l.endswith(" " + name)]
        if b is None:
            continue
        if not line:
            errs.append("C3 srchash has no %s line: the DLL is not built from it (run winbuild.py EnvironmentalHazards)" % name)
        elif line[0].split()[0] != hashlib.sha256(b).hexdigest():
            errs.append("C3 the DLL is not built from this %s (srchash stale): run winbuild.py EnvironmentalHazards" % name)
    return errs


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else None
    rows = list(csv.DictReader(io.StringIO(open(os.path.join(REPO, CSV), encoding="utf-8").read())))
    defs_b, cs_b, mod_b, sh_b = (read(rev, p) for p in (DEFS, CS, MOD, SRCHASH))
    dec = lambda b: b.decode("utf-8-sig") if b is not None else None
    defs, cs, mod, sh = dec(defs_b), dec(cs_b), dec(mod_b) or "", dec(sh_b) or ""
    errs = check(rows, defs, cs, mod, sh, cs_b, mod_b)
    if not rev:
        d0 = rows[0]["id"]
        mutants = {
            "a landmark with a random extra": (defs.replace('<%s Required="True" />' % d0,
                                                            '<%s Required="True" />\n      <Caves>0.4</Caves>' % d0), cs, mod),
            "worldgen may place a landmark": (defs.replace("<commonality>0</commonality>", "<commonality>0.3</commonality>", 1), cs, mod),
            "a shared category": (defs.replace("<li>%s</li>" % d0, "<li>Geology</li>", 1), cs, mod),
            "a stone dropped": (defs.replace("          <li>Granite</li>\n", "", 1), cs, mod),
            "forced rock overridden": (defs, cs.replace("t.PrimaryBiome?.forceRockTypes != null", "false"), mod),
            "a switch not scribed": (defs, cs, mod.replace('Scribe_Values.Look(ref geoHullbedEnabled, "geoHullbedEnabled", true);', "")),
        }
        for name, (df, c, md) in mutants.items():
            if (df, c, md) == (defs, cs, mod):
                errs.append("mutant '%s' did not apply (the source moved; update the mutant)" % name)
            elif not check(rows, df, c, md, sh, cs_b, mod_b):
                errs.append("mutant '%s' stayed green: the check is blind" % name)
        if not check(rows, defs, cs, mod, sh, cs_b + b"\n// edit", mod_b):
            errs.append("mutant 'stale srchash' stayed green: the check is blind")
    for e in errs:
        print("FAIL:", e)
    if errs:
        return 1
    print("OK %d geological landmarks: own-category mutators carrying their stones_now, fixed-name landmarks of one "
          "required mutator, no world generation, NaturalRockTypesIn postfix, %d switches; DLL srchash matches; 7 mutants red"
          % (len(rows), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
