"""Proof that the second mountain pass left biomes and surface settlement tiles alone
and the river and road links (MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED, clause "biomes, the 326 river
links, the 1,242 road links and the 97 settlements must be unchanged").

    python3 src/RimMandrake/Utils/selftest_mountain2_base_pins.py [<save.rws>]

The pre-pass base (ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws) lives outside the repo, in
D:\\ClaudeWork\\backups\\saves_pre_cleanup_20261020T2220\\, so its tileBiome array and its sorted
surface settlement tiles are PINNED here as sha256 digests (measured from that base 2026-11-03).
Links are pinned too: the road Origins/Adjacency/Def arrays byte for byte (sha256 of the three
raw arrays), and the river links as a sorted SET of (origin, target, def shortHash) edges, target
resolved through worldgeom - the separate river re-lay rewrote array order and adjacency slots but kept
the same edges and defs, so the set, not the byte order, is what must not change.
The save must reproduce every digest exactly. When the base is readable, the pins are first
re-derived from it (a pin that no longer matches its own base is a FAIL, not a skip).
Sanity probes: a copy of the save's arrays with ONE biome tile changed, and with one settlement
tile moved, one road origin moved one tile, and one river edge re-aimed at another neighbour, must each
miss its pin - so a pass means the instrument can see one tile or one link.
Default save: world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws. Exit 0 = unchanged.
"""
import hashlib, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mountain2_save_check as m2  # noqa: E402
import worldgeom, worldmap, worldview  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SAVE = os.path.join(REPO, "world", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws")
BASE = "/mnt/d/ClaudeWork/backups/saves_pre_cleanup_20261020T2220/ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws"
TILES = 21872
PIN_BIOME = "af24d020b96286f77fdf3267df9034fdcfd36d92dcf65cc58331ffd8a36135f6"
PIN_SETTL = "1cb873360838e5343cc354a5286370f170be094782c366e590b81775f71a6691"
PIN_ROAD = "2c0def8d876aaf738e3c9c45b71752d13ae5d33fa764110a614aace14ce4c7ff"
PIN_RIVER = "38a6ebed8a87806523c06366f16efa482e81afa1193dd7e2f88eefb0c72b70f1"


def digest(seq):
    return hashlib.sha256(repr(tuple(seq)).encode()).hexdigest()


def read_links(path, geom):
    """(road raw arrays (origins, slots, hashes), sorted river edge set [(origin, target, hash)])."""
    g = worldmap.WorldGrid.__new__(worldmap.WorldGrid)
    g.save_path = path
    with open(path, encoding="utf-8", errors="surrogateescape") as fh:
        g.text = fh.read()
    g._locate_surface()
    out = {}
    for kind in ("road", "river"):
        o, a, d, _ = worldview.LINKS[kind]
        ob, ab, db = (g._read_array(n) for n in (o, a, d))
        if ob is None or ab is None or db is None:
            raise SystemExit("FAIL %s link arrays missing in %s" % (kind, path))
        n = len(ob) // 4
        origins = list(struct.unpack("<%dI" % n, ob))
        slots = list(ab)
        hashes = list(struct.unpack("<%dH" % (len(db) // 2), db))
        if not (len(slots) == len(hashes) == n):
            raise SystemExit("FAIL %s link arrays disagree in length in %s" % (kind, path))
        out[kind] = (origins, slots, hashes)
    o, s, h = out["river"]
    river = sorted((t, geom.neighbours(t)[k], x) for t, k, x in zip(o, s, h))
    return out["road"], river


def road_digest(road):
    o, s, h = road
    raw = struct.pack("<%dI" % len(o), *o) + bytes(s) + struct.pack("<%dH" % len(h), *h)
    return hashlib.sha256(raw).hexdigest()


def main(argv):
    save = argv[0] if argv else SAVE
    fails = []
    arr, _, settl = m2.read_save(save)
    biome = arr["tileBiome"]
    if len(biome) != TILES:
        fails.append("tileBiome has %d tiles, not %d" % (len(biome), TILES))
    geom = worldgeom.Geometry(TILES)
    road, river = read_links(save, geom)
    if os.path.exists(BASE):
        barr, _, bsettl = m2.read_save(BASE)
        if digest(barr["tileBiome"]) != PIN_BIOME or digest(bsettl) != PIN_SETTL:
            fails.append("pins no longer match the base %s" % BASE)
        broad, briver = read_links(BASE, geom)
        if road_digest(broad) != PIN_ROAD or digest(briver) != PIN_RIVER:
            fails.append("link pins no longer match the base %s" % BASE)
        nb = sum(x != y for x, y in zip(barr["tileBiome"], biome))
        print("base readable: %d biome tiles differ from it; road links %s; river edges %d not in base"
              % (nb, "byte-identical" if broad == road else "DIFFER", len(set(river) - set(briver))))
    else:
        print("base not readable at %s; using the pins alone" % BASE)
    # sanity probes: one changed tile must miss each pin
    other = next(v for v in set(biome) if v != biome[0])
    if digest((other,) + tuple(biome[1:])) == PIN_BIOME:
        fails.append("probe: a one-tile biome change still matches the pin")
    moved = list(settl)
    if moved:
        moved[0] = (moved[0] + 1) % TILES
    if digest(sorted(moved)) == PIN_SETTL:
        fails.append("probe: a moved settlement still matches the pin")
    o, sl, h = road
    if road_digest(([(o[0] + 1) % TILES] + o[1:], sl, h)) == PIN_ROAD:
        fails.append("probe: a road link moved one tile still matches the pin")
    t0, tgt, h0 = river[0]
    alt = next(u for u in geom.neighbours(t0) if u != tgt)
    if digest(sorted([(t0, alt, h0)] + river[1:])) == PIN_RIVER:
        fails.append("probe: a river edge re-aimed at another neighbour still matches the pin")
    if digest(sorted(river[1:] + [(t0, tgt, h0 ^ 1)])) == PIN_RIVER:
        fails.append("probe: a river edge with another def still matches the pin")
    dr, dv = road_digest(road), digest(river)
    if dr != PIN_ROAD:
        fails.append("road links differ from the pre-pass base (sha %s)" % dr[:12])
    if dv != PIN_RIVER:
        fails.append("river edges differ from the pre-pass base (sha %s)" % dv[:12])
    print("road links %d sha %s; river edges %d sha %s" % (len(o), dr[:12], len(river), dv[:12]))
    db, ds = digest(biome), digest(settl)
    if db != PIN_BIOME:
        fails.append("tileBiome differs from the pre-pass base (sha %s)" % db[:12])
    if ds != PIN_SETTL:
        fails.append("surface settlement tiles differ from the pre-pass base (sha %s)" % ds[:12])
    print("biome sha %s, %d distinct biomes; %d surface settlements sha %s"
          % (db[:12], len(set(biome)), len(settl), ds[:12]))
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else "FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
