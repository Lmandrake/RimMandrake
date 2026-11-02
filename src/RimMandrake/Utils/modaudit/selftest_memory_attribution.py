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
"""
import os
import struct
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import memory_attribution as M  # noqa: E402

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
        planted = want + 64 * 64 * 4 / 3.0 / M.MB
        ok(abs(planted - want) * M.MB > 1000, "7 sanity: double-counted override is visible")
    if FAILS:
        for f in FAILS:
            print("FAIL", f)
        return 1
    print("selftest_memory_attribution: PASS (7 groups)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
