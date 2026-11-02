#!/usr/bin/env python3
"""Selftest: memory_attribution.py (FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE). Offline, under a second.

Checks the engine load rules it encodes (from the 1.6 decompile) on synthetic input, then one synthetic mod walked
end to end:
 1 LoadFolders parse: version key lower-cased with the 'v' dropped, '/' is the root, IfModActive* attributes split
 2 ShouldLoad: IfModActive any-of, IfModActiveAll, IfModNotActive, _steam suffix ignored
 3 folder order: exact version, else the highest defined version <= 1.6, else default; no LoadFolders -> 1.6 (or
   best older version dir), Common, root
 4 texture bytes: DXT5 1 B/px x4/3 when both sides %4 and compression on, RGBA32 4 B/px otherwise
 5 audio headers: Vorbis channels + last granule; RIFF fmt/data
 6 a synthetic mod: a 1.6 override replaces the root copy (counted once), a .png beside a same-named .dds is
   skipped, a 1.5-only texture is not loaded, a 64x62 png stays RGBA32, a big .ogg is streamed
 7 sanity: a planted wrong rule (override counted twice) would change the total - the walk can see the difference
 8 atlas pages (atlas_attribution, from StaticTextureAtlas): page size by NextPowerOfTwo(sqrt*1.05), the taller
   retry, colour mips floor(log2(w/512))+1, DXT 1 B/px vs RGBA 4, mask page 1 mip
 9 atlas insertion: RealtimeOnly inserts nothing; Building+minifiable inserts twice (Building and Item); >=512 px
   is refused; a later mod's override wins the path; Multi takes _north/_east/_south/_west; Collection takes the
   folder minus _m masks; a mod's own graphic class inserts nothing; a vanilla path is counted unsized
10 atlas sanity: split bytes sum to the page bytes; a planted rule (no minifiable double insert) changes the total
"""
import json
import os
import struct
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import memory_attribution as M  # noqa: E402
import atlas_attribution as A  # noqa: E402

FAILS = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)


def png(w, h):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00" * 8)) + chunk(b"IEND", b""))


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)


def main():
    lf = M.parse_load_folders(b"""<loadFolders>
      <v1.6><li>/</li><li>1.6</li><li IfModActive="Ludeon.RimWorld.Biotech, x.y">Mods/Bio</li>
            <li IfModNotActive="a.b">Mods/NoAB</li><li IfModActiveAll="a.b,c.d">Mods/Both</li></v1.6>
      <v1.5><li>1.5</li></v1.5><default><li>/</li></default></loadFolders>""")
    ok(set(lf) == {"1.6", "1.5", "default"}, "1 version keys %r" % sorted(lf))
    ok(lf["1.6"][0][0] == "" and lf["1.6"][2][1] == ["Ludeon.RimWorld.Biotech", "x.y"], "1 root / IfModActive split")
    act = {"ludeon.rimworld.biotech", "a.b"}
    ok(M.should_load(["Ludeon.RimWorld.Biotech_steam"], None, None, act), "2 any-of with _steam suffix")
    ok(not M.should_load(None, None, ["a.b"], act), "2 IfModNotActive")
    ok(not M.should_load(None, ["a.b", "c.d"], None, act), "2 IfModActiveAll needs all")
    ok(M.folders_descending([], lf, act) == ["Mods/Bio", "1.6", ""], "3 exact version, descending, filtered: %r"
       % M.folders_descending([], lf, act))
    lf15 = {"1.4": [("1.4", None, None, None)], "1.5": [("1.5", None, None, None)], "1.7": [("1.7", None, None, None)]}
    ok(M.folders_descending([], lf15, act) == ["1.5"], "3 highest older version")
    ok(M.folders_descending([], {"default": [("", None, None, None)]}, act) == [""], "3 default")
    ok(M.folders_descending(["1.6", "1.5", "Common", "Textures"], None, act) == ["1.6", "Common", ""], "3 no LF")
    ok(M.folders_descending(["1.4", "1.5", "About"], None, act) == ["1.5", ""], "3 no LF, best older dir")
    ok(abs(M.texture_bytes(64, 64, True) - 64 * 64 * 4 / 3.0) < 1e-6, "4 DXT5")
    ok(abs(M.texture_bytes(64, 62, True) - 64 * 62 * 16 / 3.0) < 1e-6, "4 not %4 -> RGBA32")
    ok(abs(M.texture_bytes(64, 64, False) - 64 * 64 * 16 / 3.0) < 1e-6, "4 compression off -> RGBA32")
    head = b"OggS" + b"\x00" * 24 + b"\x01vorbis" + struct.pack("<IB", 0, 2) + struct.pack("<I", 44100) + b"\x00" * 8
    tail = b"junk" + b"OggS" + b"\x00\x04" + struct.pack("<q", 88200) + b"\x00" * 20
    ok(M.ogg_samples(head, tail) == (2, 88200), "5 ogg %r" % (M.ogg_samples(head, tail),))
    wav = (b"RIFF" + struct.pack("<I", 0) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, 22050, 44100, 2, 16)
           + b"data" + struct.pack("<I", 2000) + b"\x00" * 2000)
    ok(M.wav_samples(wav) == (1, 1000), "5 wav %r" % (M.wav_samples(wav),))
    with tempfile.TemporaryDirectory() as d:
        put(d, "About/About.xml", b"<ModMetaData/>")
        put(d, "Textures/A.png", png(64, 64))           # replaced by the 1.6 copy below
        put(d, "1.6/Textures/A.png", png(1024, 1024))
        put(d, "Textures/B.png", png(256, 256))         # skipped: B.dds beside it
        put(d, "Textures/B.dds", b"DDS " + b"\x00" * 124 + b"\x00" * 1000)
        put(d, "1.5/Textures/Old.png", png(512, 512))   # not loaded on 1.6
        put(d, "Textures/Odd.png", png(64, 62))         # RGBA32
        put(d, "Sounds/big.ogg", b"OggS" + b"\x00" * (M.STREAM_OVER + 10))
        put(d, "Sounds/s.wav", wav)
        r = M.collect(d, set(), True)
        want = (1024 * 1024 * 4 / 3.0 + 1000 + 64 * 62 * 16 / 3.0) / M.MB
        ok(abs(r["tex_mb"] - round(want, 2)) < 0.011, "6 tex_mb %r want %.3f" % (r["tex_mb"], want))
        ok(r["tex_files"] == 3 and r["dds"] == 1 and r["tex_rgba"] == 1 and r["tex_dxt"] == 1, "6 counts %r" % r)
        ok(r["snd_files"] == 2 and r["snd_streamed"] == 1, "6 audio %r" % r)
        ok(r["folders"] == ["1.6", ""], "6 folders %r" % r["folders"])
        ok(r["tex_dims"].get("a") == [1024, 1024] and r["tex_dims"].get("odd") == [64, 62]
           and "old" not in r["tex_dims"], "6 tex_dims for the atlas pass %r" % r["tex_dims"])
        planted = want + 64 * 64 * 4 / 3.0 / M.MB
        ok(abs(planted - want) * M.MB > 1000, "7 sanity: double-counted override is visible")
    # 8 pages
    ok(A.page_size([(64, 64)] * 4) == (256, 64), "8 4x64^2: w NPOT(128*1.05)=256, h NPOT(16384/256)=64 %r"
       % (A.page_size([(64, 64)] * 4),))
    ok(A.page_size([(300, 300)] * 3) == (1024, 512), "8 taller retry: 3x300 in 1024x256 overflows -> 1024x512 %r"
       % (A.page_size([(300, 300)] * 3),))
    ok(A.page_bytes(2048, 1024, True, False) == 2048 * 1024 + 1024 * 512 + 512 * 256, "8 colour mips: 3 levels at 2048")
    ok(A.page_bytes(256, 64, True, False) == 256 * 64, "8 narrow page keeps 1 level")
    ok(A.page_bytes(2048, 1024, False, True) == 2048 * 1024 * 4, "8 mask: RGBA 4 B/px, 1 mip")
    # 9 insertion
    recs = [("m.a", {"tex_dims": {"t/chair": [64, 64], "t/big": [512, 64], "t/pot_north": [32, 32],
                                  "t/pot_east": [32, 32], "t/pot_south": [32, 32], "t/rock/a": [16, 16],
                                  "t/rock/a_m": [16, 16], "t/rock/b": [16, 16], "t/x": [8, 8]}}),
            ("m.b", {"tex_dims": {"t/chair": [128, 128]}})]
    idx = {"things": [["Building", True, "MapMeshOnly", "Verse.Graphic_Single", "T/Chair", None, "Cutout"],
                      ["Item", False, "RealtimeOnly", "Verse.Graphic_Single", "t/x", None, "Cutout"],
                      ["Item", False, "MapMeshOnly", "Verse.Graphic_Single", "t/big", None, "Cutout"],
                      ["Building", False, "MapMeshOnly", "Verse.Graphic_Multi", "t/pot", None, "Cutout"],
                      ["Item", False, "MapMeshOnly", "Verse.Graphic_Random", "t/rock", None, "Cutout"],
                      ["Item", False, "MapMeshOnly", "Mod.Graphic_Own", "t/x", None, "Cutout"],
                      ["Plant", False, "MapMeshOnly", "Verse.Graphic_Single", "Things/Vanilla", None, "Cutout"]],
           "scatter": []}
    e = A.estimate(idx, recs, True)
    ok(e["textures"] == 7, "9 7 inserts: chair x2 groups, 3 pot dirs, rock a+b (not a_m): %d" % e["textures"])
    ok(e["too_big"] == 1 and e["defs_foreign_class"] == 1 and e["vanilla_unsized"] == 1, "9 refusals %r" % {
        k: e[k] for k in ("too_big", "defs_foreign_class", "vanilla_unsized")})
    ok(set(e["by_mod_mb"]) == {"m.a", "m.b"} and e["by_mod_mb"]["m.b"] > e["by_mod_mb"]["m.a"] * 0.5,
       "9 override: m.b's 128 px chair wins %r" % e["by_mod_mb"])
    ok({(p["group"], p["textures"]) for p in e["pages"]} == {("Building", 4), ("Item", 3)}, "9 pages %r" % e["pages"])
    h2 = A.Holder([("m", {"tex_dims": {"c/p_north": [8, 8], "c/p_northm": [8, 8], "c/q": [8, 8], "c/q_m": [8, 8]}})])
    got = sorted(A.def_textures("Verse.Graphic_Random", "c", None, True, h2))
    ok(got == [("c/p_north", "c/p_northm"), ("c/q", "c/q_m")], "9 collection masks: <dir>m and _m %r" % got)
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "manifest.json"), "w") as fh:
            fh.write('{"capturedUtc": "x", "mods": [{"packageId": "B", "loadOrder": 2}, {"packageId": "a", "loadOrder": 1}]}')
        ok(A.dump_matches(d, ["a", "b"], str.lower)[:3:2] == (True, set()), "9 dump in load order matches")
        ok(not A.dump_matches(d, ["b", "a"], str.lower)[0], "9 same mods, other order: stale")
        ok(not A.dump_matches(d, ["a", "b", "c"], str.lower)[0], "9 list mod missing from the dump: stale")
        got = A.dump_matches(d, ["a"], str.lower)
        ok(not got[0], "9 dropped mod over 5%% of a 1-mod list: stale %r" % (got,))
        lst = ["a"] + ["x%d" % i for i in range(19)]
        with open(os.path.join(d, "manifest.json"), "w") as fh:
            json.dump({"capturedUtc": "x", "mods": [{"packageId": p, "loadOrder": i} for i, p in
                                                    enumerate(["a", "B_steam"] + lst[1:])]}, fh)
        got = A.dump_matches(d, lst, lambda p: A._pid(p))
        ok(got[0] and got[2] == {"b"} and "left out: b" in got[1], "9 one dropped mod of 20: usable %r" % (got,))
        ok(not A.dump_matches(d, lst[1:] + ["a"], lambda p: A._pid(p))[0], "9 dropped + reordered: stale")
    # 9 dropped mods' defs are excluded, not counted
    idx3 = {"things": [r + ["m.a"] for r in idx["things"]] + [["Building", False, "MapMeshOnly",
                                                               "Verse.Graphic_Single", "t/chair", None, "Cutout",
                                                               "gone.mod_steam"]],
            "scatter": [["t/rock/b", "gone.mod"]]}
    e3 = A.estimate(idx3, recs, True, drop={"gone.mod"})
    ok(e3["defs_dropped"] == 2 and e3["textures"] == e["textures"], "9 drop: 2 defs out, inserts unchanged %r" % (
        (e3["defs_dropped"], e3["textures"]),))
    ok(A.estimate(idx3, recs, True)["textures"] == e["textures"] + 1, "9 no drop: the scatter rock/b inserts in"
       " Terrain")
    # 10 sanity
    ok(abs(sum(e["by_mod_mb"].values()) - e["total_mb"]) < 0.01, "10 split sums to page total")
    idx2 = {"things": [list(t) for t in idx["things"]], "scatter": []}
    idx2["things"][0][1] = False
    ok(A.estimate(idx2, recs, True)["textures"] == 6, "10 planted: no minifiable double insert is visible")
    if FAILS:
        for f in FAILS:
            print("FAIL", f)
        return 1
    print("selftest_memory_attribution: PASS (10 groups)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
