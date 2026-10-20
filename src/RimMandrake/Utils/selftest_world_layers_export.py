#!/usr/bin/env python3
"""selftest_world_layers_export.py - world_layers_export.py on a tiny synthetic save. Offline, seconds.

Checks: every layer decodes from a fixture .rws; a ShortHashGiver collision (two names, one raw hash,
the record naming the older one) is SETTLED to the record's name rather than the capture's; a hash no
capture names is decoded through the historical-rename list and ported to its new name; the faction
with no <loadID> is Faction_0; the round trip (written files re-read) is identical; the identity diff
sees adds/losses/moves; and --out pointing at the committed stamp folder is refused.
"""
import base64
import os
import shutil
import struct
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_layers_export as wle                                   # noqa: E402
from save_donor_rewrite import short_hash_raw                       # noqa: E402

FAILS = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def b64(raw):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(raw) + c.flush()).decode()


class FakeGeom(object):
    # 4 tiles on a ring: 0-1-2-3-0
    NB = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [2, 0]}

    def neighbours(self, t):
        return self.NB[t]


H_DESERT = 100
H_COLLIDE = short_hash_raw("RUT_TheForge")          # in the capture this hash is RM_FloodedCanyon
H_LOST = short_hash_raw("RUT_ForsakenCrags")         # no capture names it
H_MUT_A, H_MUT_B = 200, 201
H_ROAD, H_RIVER = 300, 400


def fixture_save():
    biome = struct.pack("<4H", H_DESERT, H_COLLIDE, H_LOST, H_DESERT)
    elev = struct.pack("<4H", 8192 + 10, 8192 + 20, 8192 - 5, 8192)
    temp = struct.pack("<4H", 3000 + 141, 3000, 3000 - 50, 3000 + 5)
    rain = struct.pack("<4H", 0, 100, 200, 300)
    feat = struct.pack("<4H", 21, 21, 22, 0xFFFF)
    pol = struct.pack("<4H", 0, 0, 0, 0)
    hill = bytes([1, 2, 3, 4])
    swamp = bytes([92, 0, 255, 0])
    mdefs = struct.pack("<3H", H_MUT_A, H_MUT_B, H_MUT_A)
    mtiles = struct.pack("<3I", 0, 0, 2)
    r_or, r_adj, r_def = struct.pack("<1I", 0), bytes([0]), struct.pack("<1H", H_RIVER)         # 0-1
    d_or, d_adj, d_def = struct.pack("<2I", 1, 2), bytes([1, 1]), struct.pack("<2H", H_ROAD, H_ROAD)  # 1-2, 2-3

    def arr(name, raw):
        return "<%sDeflate>%s</%sDeflate>" % (name, b64(raw), name)
    surf = "".join([arr("tileBiome", biome), arr("tileElevation", elev), arr("tileTemperature", temp),
                    arr("tileRainfall", rain), arr("tileFeature", feat), arr("tilePollution", pol),
                    arr("tileHilliness", hill), arr("tileSwampiness", swamp),
                    arr("tileMutatorDefs", mdefs), arr("tileMutatorTiles", mtiles),
                    arr("tileRiverOrigins", r_or), arr("tileRiverAdjacency", r_adj), arr("tileRiverDef", r_def),
                    arr("tileRoadOrigins", d_or), arr("tileRoadAdjacency", d_adj), arr("tileRoadDef", d_def)])
    return """<?xml version="1.0" encoding="utf-8"?>
<savegame><meta><modIds><li>ludeon.rimworld</li><li>mandrake.rut.patches</li></modIds></meta>
<game><world>
<info><name>Fixture</name><seedString>x</seedString></info>
<grid><layers><li Class="SurfaceLayer">%s</li><li Class="OrbitLayer"><tileBiomeDeflate>%s</tileBiomeDeflate></li></layers></grid>
<factionManager><allFactions>
<li><def>RUT_Jawa_Junkers</def><name>the Junkers</name><relations><li><other>Faction_1</other><kind>Hostile</kind><goodwill>-100</goodwill></li></relations><ideos><primaryIdeo>Ideo_7</primaryIdeo></ideos></li>
<li><def>PlayerColony</def><loadID>1</loadID><name>Us</name></li>
</allFactions></factionManager>
<ideoManager><ideos><li><id>7</id><name>the Weight</name><culture>RUT_Jawa_Culture_Junkers</culture></li></ideos></ideoManager>
<worldObjects><worldObjects>
<li Class="Settlement"><def>Settlement</def><tile>3,0</tile><ID>135</ID><faction>Faction_0</faction><nameInt>Sunspire</nameInt></li>
<li Class="Settlement"><def>Settlement</def><tile>1,0</tile><ID>200</ID><faction>Faction_1</faction><nameInt>Home</nameInt></li>
</worldObjects></worldObjects>
<features><features>
<li><def>WB_MapLabelFeature</def><uniqueID>21</uniqueID><name>Pan</name><drawCenter>(1, 2, 3)</drawCenter><maxDrawSizeInTiles>12</maxDrawSizeInTiles></li>
<li><def>WB_MapLabelFeature</def><uniqueID>22</uniqueID><name>Kiln</name><drawCenter>(4, 5, 6)</drawCenter><maxDrawSizeInTiles>3</maxDrawSizeInTiles></li>
</features></features>
<landmarks><landmarks><keys><li>2,0</li></keys><values><li><def>AB_TarLakes</def><name>Black Pool</name></li></values></landmarks></landmarks>
<components><li Class="RimMandrake.FlowWorks.LiquidTypes.RM_WorldComponent_LiquidTags" /></components>
</world></game></savegame>
""" % (surf, b64(struct.pack("<2H", 1, 1)))


RECORD = {
    "tiles": "tile,lat,lon,arc,bearing,elev_m,temp_c,rain_mm,biome,water,river_flow,region,hilliness,swampiness\n"
             "0,1.0,2.0,3.0,4.0,10,14.1,0,RUT_Desert,0,0,Pan,1,0.36\n"
             "1,1.0,2.0,3.0,4.0,20,0.0,100,RUT_TheForge,0,0,Pan,2,0.00\n"
             "2,1.0,2.0,3.0,4.0,-5,-5.0,200,RUT_ForsakenCrags,0,0,Kiln,3,1.00\n"
             "3,1.0,2.0,3.0,4.0,0,0.5,300,RUT_Desert,0,0,,4,0.00\n",
    "links": "kind,a,b,def\nriver,1,0,Creek\nroad,0,3,DirtRoad\n",
    "mutators": "tile,mutators\n0,Mountain\n",
    "landmarks": "tile,landmark,why\n2,AB_TarLakes,the black pool\n",
    "settlements": "id,faction_def,faction,name,tile,lat,lon,arc,biome,why\n0,RUT_Jawa_Junkers,the Junkers,Sunspire,2,,,,,seat\n",
}


def main():
    tmp = tempfile.mkdtemp(prefix="wle_selftest_")
    try:
        save = os.path.join(tmp, "fixture.rws")
        open(save, "w", encoding="utf-8").write(fixture_save())
        recdir = os.path.join(tmp, "world")
        os.makedirs(recdir)
        for l, txt in RECORD.items():
            open(os.path.join(recdir, "ASHKARR_WORLDMAP_%s.csv" % l), "w").write(txt)
        prof = os.path.join(tmp, "ModsConfig.xml")
        open(prof, "w").write("<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>mandrake.rut.patches</li>"
                              "</activeMods></ModsConfigData>")
        table = wle.TableFromDicts(
            {"BiomeDef": {H_DESERT: "RUT_Desert", H_COLLIDE: "RM_FloodedCanyon"},
             "TileMutatorDef": {H_MUT_A: "Mountain", H_MUT_B: "AB_TarLakes"},
             "RoadDef": {H_ROAD: "DirtRoad"}, "RiverDef": {H_RIVER: "Creek"},
             "FactionDef": {}},
            {"BiomeDef": {"RUT_Desert": "mandrake.rut.patches", "RUT_TheForge": "mandrake.rut.patches",
                          "RUT_Abyss": "mandrake.rut.patches"},
             "TileMutatorDef": {"Mountain": "ludeon.rimworld", "RM_TarLakes": "mandrake.rm.thesump"},
             "LandmarkDef": {"RM_TarLakes": "mandrake.rm.thesump"},
             "RoadDef": {"DirtRoad": "ludeon.rimworld"}, "RiverDef": {"Creek": "ludeon.rimworld"},
             "FactionDef": {"RUT_Jawa_Junkers": "mandrake.rut.patches"}, "FeatureDef": {}})
        out = os.path.join(tmp, "out")
        res, layers, ported = wle.run(save, out, prof, False, record_prefix=os.path.join(recdir, "ASHKARR_WORLDMAP_"),
                                      table=table, geom=FakeGeom(), src_idx={}, quiet=True)
        c = res["counts"]
        check(c["tiles"] == 4, "4 surface tiles (orbit stub ignored)")
        check(c["mutator_entries"] == 3 and c["mutator_tiles"] == 2, "3 mutator entries on 2 tiles")
        check(c["river_entries"] == 1 and c["road_entries"] == 2, "1 river, 2 roads")
        check(c["landmarks"] == 1 and c["settlements_npc"] == 1 and c["settlements_player"] == 1,
              "1 landmark, 1 NPC + 1 player settlement")
        b = [t["biome"] for t in layers["tiles"]]
        check(b[1] == "RUT_TheForge", "collision hash settled to the record's RUT_TheForge, not the capture's "
                                      "RM_FloodedCanyon (got %s)" % b[1])
        check(b[2] == "RUT_ForsakenCrags", "lost hash decoded via the historical rename list (got %s)" % b[2])
        check([t["biome"] for t in ported["tiles"]][2] == "RUT_Abyss", "ported tiles carry RUT_Abyss")
        check(layers["tiles"][0]["temp_c"] == "14.1" and layers["tiles"][2]["elev_m"] == "-5"
              and layers["tiles"][0]["swampiness"] == "0.36", "scalar encodings (temp/elev/swamp)")
        check(layers["tiles"][2]["region"] == "Kiln" and layers["tiles"][3]["region"] == "",
              "region joined on feature uniqueID")
        check(layers["factions"][0]["ref"] == "Faction_0" and layers["factions"][0]["ideo_name"] == "the Weight",
              "faction without loadID is Faction_0, ideo joined")
        check(layers["settlements"][0]["faction_def"] == "RUT_Jawa_Junkers", "settlement faction resolved")
        lk = layers["links"]
        check(lk[0] == {"kind": "river", "a": 1, "b": 0, "def": "Creek"}, "shared river edge keeps the record's orientation")
        check(ported["mutators"][0]["mutators"] == "Mountain;RM_TarLakes", "port map applied to mutators")
        check(ported["landmarks"][0]["landmark"] == "RM_TarLakes", "port map applied to landmarks")
        check(all(res["roundtrip_raw"].values()) and all(res["roundtrip_ported"].values()), "round trip identical")
        d = res["diffs"]
        check(d["settlements"]["moved_same_name_faction"] == 1, "settlement move seen (Sunspire 2 -> 3)")
        check(d["links"]["road"]["added_edges"] == 2 and d["links"]["road"]["lost_edges"] == 1, "road topology diff")
        check(d["mutators"]["adds"] == 2 and d["mutators"]["losses"] == 0, "mutator identity diff")
        check(os.path.exists(os.path.join(out, "REPORT.md")) and os.path.exists(os.path.join(out, "raw", "world_info.json")),
              "REPORT.md and world_info.json written")
        info = open(os.path.join(out, "raw", "world_info.json")).read()
        check("EMPTY" in info, "liquid worldTags store reported empty")
        try:
            wle.run(save, recdir, prof, True, record_prefix=os.path.join(recdir, "ASHKARR_WORLDMAP_"),
                    table=table, geom=FakeGeom(), src_idx={}, quiet=True)
            check(False, "refuses --out == committed stamp folder")
        except SystemExit:
            check(True, "refuses --out == committed stamp folder")
        dry = os.path.join(tmp, "dry")
        wle.run(save, dry, prof, True, record_prefix=os.path.join(recdir, "ASHKARR_WORLDMAP_"),
                table=table, geom=FakeGeom(), src_idx={}, quiet=True)
        check(not os.path.exists(dry), "--dry-run writes nothing")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d FAIL" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
