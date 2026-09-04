"""Read and rewrite a RimWorld map's terrain grids directly in the save file.

Map grids are base64 + **raw DEFLATE** arrays of **2-byte def shortHashes**, one
per cell:

    <terrainGrid>
      <topGridDeflate>        ...base64...   what you walk on
      <underGridDeflate>      ...base64...   what is beneath a floor
      <foundationGridDeflate> ...base64...
      <tempGridDeflate>       ...base64...
    <roofGrid><roofsDeflate>  ...base64...   RoofDef shortHash (own hash namespace)
    <pollutionGrid><grid><mapSizeX>250</mapSizeX><arrDeflate>

NOT handled: `<snowGrid><depthGridDeflate>` looks the same shape but is a ushort
encoding of a FLOAT depth, not a defName shortHash -- see the GRID_DEF_TYPE
comment below. `<fogGrid>` is a bitfield, not ushorts at all -- see `write()`.

Verified on a 250x250 map: `zlib.decompress(data, -15)` yields exactly
125,000 bytes = 62,500 cells x 2.

⚠️ shortHash depends on the loaded mod set, so the hash table MUST come from a
dump taken with the same mod list as the save; `SaveMap` refuses to run without
one rather than guessing. Never edit a save in place -- `write()` refuses to
overwrite its source.

DOCTRINE -- read before using this module: skills/rimworld-savegame/SKILL.md.
It carries the mod-set rule, the fogGrid bitfield hazard, the backup procedure,
and the division of labour between RimBridge (things and structures, live) and
save editing (the substrate: terrain, rock, water, roofs).
"""
import base64
import io
import os
import re
import struct
import zlib

GRIDS = {
    "terrain": ("terrainGrid", "topGridDeflate"),
    "under":   ("terrainGrid", "underGridDeflate"),
    "foundation": ("terrainGrid", "foundationGridDeflate"),
    "roof":    ("roofGrid", "roofsDeflate"),
}

# Def type each grid's ushorts index into. "roof" is a SEPARATE hash namespace
# from terrain -- RimWorld's ShortHashGiver collision-resolves per Def TYPE
# (Verse/RoofGrid.cs ExposeData: DefDatabase<RoofDef>.GetByShortHash), so
# decoding roofsDeflate through the TerrainDef table looks up the wrong
# namespace and can silently return a real (wrong) TerrainDef name on a hash
# collision between the two spaces. Verified against Verse/RoofGrid.cs.
GRID_DEF_TYPE = {"roof": "RoofDef"}

# ⚠️ snowGrid's depthGridDeflate is DELIBERATELY NOT in GRIDS. It is not a
# defName shortHash array at all: Verse/SnowGrid.cs ExposeData round-trips
# through SnowFloatToShort/SnowShortToFloat, a ushort encoding of a FLOAT
# depth (0-1). Same width as every other grid (2 bytes/cell), so it decodes
# without error through this module's defName machinery and would return
# meaningless "hash:N" labels on read -- or, on a paint(), write a TerrainDef
# shortHash into the depth field, corrupting snow silently. This is the
# fogGrid trap's sibling: wrong CONTENT type at the right width, not wrong
# width. Leave it alone; drive snow depth through the live bridge
# (SnowGrid.SetDepth / JawaBenchSystemTools.cs) instead.


def load_hash_table(dump_dir, def_type="TerrainDef"):
    """shortHash -> defName, and the inverse, from a RimDefDump capture.

    MUST come from a dump taken with the same mod list as the save.
    """
    import sys
    utils = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if utils not in sys.path:
        sys.path.insert(0, utils)
    from def_diff import iter_live_defs
    path = os.path.join(dump_dir, "defs", "%s.json" % def_type)
    if not os.path.isfile(path):
        raise IOError("no %s in %s" % (def_type, dump_dir))
    by_hash, by_name = {}, {}
    for d in iter_live_defs(path):
        h, n = d.get("shortHash"), d.get("defName")
        if h is not None and n:
            by_hash[h] = n
            by_name[n] = h
    return by_hash, by_name


class SaveMap(object):
    """A save's map grids, decoded to editable arrays of defNames.

        m = SaveMap(save_path, dump_dir)
        m.paint(cells, "Gravel")
        m.write(out_path)     # never overwrites the original
    """

    def __init__(self, save_path, dump_dir):
        self.path = save_path
        self.dump_dir = dump_dir
        self.text = io.open(save_path, encoding="utf-8", errors="replace").read()
        self.by_hash, self.by_name = load_hash_table(dump_dir)   # TerrainDef
        self._hash_tables = {"TerrainDef": (self.by_hash, self.by_name)}
        m = re.search(r"<mapSizeX>(\d+)</mapSizeX>.*?<mapSizeZ>(\d+)</mapSizeZ>",
                      self.text, re.S)
        self.w = int(m.group(1)) if m else 250
        self.h = int(m.group(2)) if m else 250
        self._grids = {}

    def _hash_table(self, which):
        """(by_hash, by_name) for the def type that grid `which` indexes into.

        "roof" is RoofDef, everything else is TerrainDef -- see GRID_DEF_TYPE.
        Using the wrong table decodes through the wrong ShortHashGiver
        namespace; see the GRIDS/GRID_DEF_TYPE comment above.
        """
        def_type = GRID_DEF_TYPE.get(which, "TerrainDef")
        if def_type not in self._hash_tables:
            self._hash_tables[def_type] = load_hash_table(self.dump_dir, def_type)
        return self._hash_tables[def_type]

    # ------------------------------------------------------------- codec
    @staticmethod
    def _decode(b64):
        return zlib.decompress(base64.b64decode("".join(b64.split())), -15)

    @staticmethod
    def _encode(raw):
        c = zlib.compressobj(9, zlib.DEFLATED, -15)
        return base64.b64encode(c.compress(raw) + c.flush()).decode("ascii")

    def grid(self, which="terrain"):
        """Decode a grid to a list of ushorts, one per cell, row-major by z."""
        if which in self._grids:
            return self._grids[which]
        parent, tag = GRIDS[which]
        m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), self.text, re.S)
        if not m:
            raise KeyError("grid %s (<%s>) not present in this save" % (which, tag))
        raw = self._decode(m.group(1))
        arr = list(struct.unpack("<%dH" % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
        self._grids[which] = arr
        return arr

    def idx(self, x, z):
        return z * self.w + x

    # -------------------------------------------------------------- read
    def terrain_at(self, x, z, which="terrain"):
        g = self.grid(which)
        i = self.idx(x, z)
        by_hash, _ = self._hash_table(which)
        return by_hash.get(g[i], "hash:%d" % g[i]) if 0 <= i < len(g) else None

    def census(self, which="terrain"):
        """defName -> cell count. The fastest way to understand a map."""
        import collections
        by_hash, _ = self._hash_table(which)
        c = collections.Counter(self.grid(which))
        return {by_hash.get(h, "hash:%d" % h): n for h, n in c.most_common()}

    # ------------------------------------------------------------- write
    def paint(self, cells, terrain, which="terrain", clear_under=True):
        """Set terrain over an iterable of (x, z[, weight]). Returns cells set.

        clear_under -- when painting the TOP grid, also zero underGrid at those
        cells. Default True, and that default is the safe one.

        RimWorld keeps a constructed floor in topGrid and the natural terrain it
        was laid over in underGrid, so painting natural terrain into topGrid
        alone ORPHANS the buried terrain -- a state the game never produces.
        Measured: 61,671 / 62,500 underGrid cells are 0, so 0 genuinely means
        "nothing buried" and clearing means writing 0.

        PASS clear_under=False WHEN PAINTING A FLOOR -- there the natural
        terrain underneath is meant to be preserved. This function cannot tell a
        floor from natural ground (the hash table carries defName only, not the
        `natural` flag), so the caller says. Rationale in full:
        skills/rimworld-savegame/SKILL.md section 4.

        ⚠️ NOT HANDLED: foundationGrid. On the save measured it holds a single
        distinct value across all 62,500 cells, so there was nothing to test a
        rule against, and inventing one from a uniform sample is how the wrong
        rule gets baked in. If you author over gravship substructure, check it.
        """
        _, by_name = self._hash_table(which)
        h = by_name.get(terrain)
        if h is None:
            raise KeyError("unknown terrain %r for this mod set. Known: %d defs"
                           % (terrain, len(by_name)))
        g = self.grid(which)
        under = None
        if clear_under and which == "terrain":
            try:
                under = self.grid("under")
            except Exception:
                under = None          # save has no underGrid; nothing to orphan
        n = 0
        self.last_cleared_under = 0
        for c in cells:
            x, z = c[0], c[1]
            if 0 <= x < self.w and 0 <= z < self.h:
                i = self.idx(x, z)
                g[i] = h
                if under is not None and i < len(under) and under[i] != 0:
                    under[i] = 0
                    self.last_cleared_under += 1
                n += 1
        return n

    def write(self, out_path):
        """Re-encode every modified grid and write a NEW save. Never in place.

        ⚠️ DO NOT "FIX" THE STALE FOG BY ADDING fogGrid TO THE GRIDS TABLE.
        fogGridDeflate is a BITFIELD -- 7,813 bytes for 62,500 cells, one bit
        per cell -- while every GRIDS row is unpacked as '<%dH', two-byte
        shorts. Decoding at 16x the wrong width still "succeeds" and re-encoding
        silently corrupts the fog of a healthy save. Leaving it alone is
        SAFE-BY-CONSTRUCTION: never decoded, never re-encoded, passed through
        untouched. Full entry: skills/rimworld-savegame/SKILL.md section 6.
        """
        if os.path.abspath(out_path) == os.path.abspath(self.path):
            raise IOError("refusing to overwrite the source save; give a new path")
        text = self.text
        for which, arr in self._grids.items():
            parent, tag = GRIDS[which]
            raw = struct.pack("<%dH" % len(arr), *arr)
            text = re.sub(r"<%s>.*?</%s>" % (tag, tag),
                          "<%s>%s</%s>" % (tag, self._encode(raw), tag),
                          text, count=1, flags=re.S)
        io.open(out_path, "w", encoding="utf-8", newline="\n").write(text)
        return out_path


def roundtrip_check(save_path, dump_dir):
    """Prove decode→encode→decode is lossless before trusting any edit.

    Run this first on any new save or mod set. If it fails, do not write.
    """
    m = SaveMap(save_path, dump_dir)
    arr = list(m.grid("terrain"))
    raw = struct.pack("<%dH" % len(arr), *arr)
    again = SaveMap._decode(SaveMap._encode(raw))
    ok = again == raw
    return {"cells": len(arr), "expected": m.w * m.h, "lossless": ok,
            "distinct": len(set(arr))}
