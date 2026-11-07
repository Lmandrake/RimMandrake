#!/usr/bin/env python3
"""save_uncompress.py -- make a fixture save loadable on any superset of the list it was built on.

    python3 save_uncompress.py expand SRC.rws DST.rws      a new file; never overwrites
    python3 save_uncompress.py check PATH.rws [--expect ChunkMarble=589,MineableUranium=34]
    python.exe save_uncompress.py live NAME --expect ...   after a load of NAME: its log lines and the map's things

CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES. A map's <compressedThingMapDeflate> holds one ThingDef shortHash per cell, and
that grid is the one part of a save that ties it to the list that wrote it. RM_TestSite_calm_v2, built on the 11-mod
flowworks tier, broke three ways when loaded on the full list (Player_ee0fbaa8.log, 1738 warnings per load):

1. Elshender.stackablechunks removes saveCompressible from ChunkBase (a compressed cell has no stack count, so the mod
   is right). MapFileCompressor.ThingsToSpawnAfterLoad warns "Tried loading non-compressible thing as compressed
   thing" and DROPS the thing: 1704 chunks gone per load, and the warnings fill Verse.Log's cap.
2. shortHash is stable only within a list. ShortHashGiver takes StableStringHash % 65535, probing upward in defName
   order, so a new def can take the slot: MineableUranium is 7015 on the tier, but on the full list
   KotORBlasterBolt_ioncharger sorts first and takes 7015. All 34 uranium cells read as a projectile and vanished.
   If the new occupant is itself compressible, the wrong thing spawns with no log line at all.
3. Thing.ExposeData scribes stackCount only when stackLimit > 1 and its default is 0. A full ChunkMechanoidSlag saved at
   stackLimit 1 has no tag, so on the full list (limit 15) it reads 0: "Spawned thing with 0 stackCount".

So the fix is in the fixture, not the def: every compressed cell becomes a full <thing>, named by defName, and every
chunk carries stackCount 1. Map.FinalizeLoading merges loadedFullThings and the decompressed things into one list before
spawning, so both forms take the same path. A stackCount tag is ignored where the limit is 1.

hash -> defName comes from the raw hash plus a short upward probe over COMPRESSIBLE, and a value nothing explains is
refused by number. Add the def to COMPRESSIBLE (or pass extra=) when a fixture holds a modded compressible def.
"""
import argparse
import base64
import os
import re
import struct
import sys
import zlib

# Every non-abstract ThingDef with saveCompressible in Data/{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}/Defs, its
# thingClass and MaxHitPoints, read by inheritance on 2026-11-06. A chunk's class is Thing, which a save writes bare.
COMPRESSIBLE = {
    "CollapsedRocks": ("Mineable", 500), "RaisedRocks": ("Mineable", 500),
    "MineableSteel": ("Mineable", 1500), "MineableSilver": ("Mineable", 1500), "MineableGold": ("Mineable", 1500),
    "MineableUranium": ("Mineable", 4000), "MineablePlasteel": ("Mineable", 8000), "MineableJade": ("Mineable", 1500),
    "MineableComponentsIndustrial": ("Mineable", 2000), "MineableObsidian": ("Mineable", 1200),
    "Sandstone": ("Mineable", 400), "Granite": ("Mineable", 900), "Limestone": ("Mineable", 700),
    "Slate": ("Mineable", 500), "Marble": ("Mineable", 450), "SolidIce": ("Mineable", 240), "Vacstone": ("Mineable", 600),
    "ChunkSlagSteel": ("Thing", 300), "ChunkSandstone": ("Thing", 300), "ChunkGranite": ("Thing", 300),
    "ChunkLimestone": ("Thing", 300), "ChunkSlate": ("Thing", 300), "ChunkMarble": ("Thing", 300),
    "ChunkVacstone": ("Thing", 300),
}
PROBE_MAX = 8       # how far upward a collision may have pushed a hash (measured 0-1 on the fixtures and the full-list dump)
GRID_RE = re.compile(r"<compressedThingMapDeflate>(.*?)</compressedThingMapDeflate>", re.S)
THING_RE = re.compile(r'<thing(?: Class="[^"]*")?>\s*<def>([^<]+)</def>.*?</thing>', re.S)
ID_RE = re.compile(r"<id>[^<]*?(\d+)</id>")
LOAD_LINE = "Loading game from file %s with mods:"
BAD_LOG = ("Tried loading non-compressible thing as compressed thing", "Spawned thing with 0 stackCount")


def raw_hash(name):
    """The first slot ShortHashGiver tries: (ushort)(GenText.StableStringHash(name) % 65535), C# truncating remainder."""
    n = 23
    for ch in name:
        n = (n * 31 + ord(ch)) & 0xFFFFFFFF
    if n >= 2 ** 31:
        n -= 2 ** 32
    r = abs(n) % 65535
    return (-r if n < 0 else r) & 0xFFFF


def resolve(values, table):
    """{cell value: defName} for the grid's non-zero values: the known def whose raw hash is nearest at or below the value
    (an exact hit wins, RaisedRocks at 8309 must not contest MineableJade at 8319). Raises naming every value with no
    such def, and any two values landing on one def: a guess here would put wrong rock on the map silently."""
    out, bad = {}, []
    for v in sorted(values):
        cands = sorted((v - raw_hash(n), n) for n in table if 0 <= v - raw_hash(n) <= PROBE_MAX)
        if cands:
            out[v] = cands[0][1]
        else:
            bad.append("%d -> no known compressible def" % v)
    if len(set(out.values())) != len(out):
        bad.append("two values resolve to one def: %s" % out)
    if bad:
        raise ValueError("cannot name the compressed hashes: %s" % "; ".join(bad))
    return out


def read_grid(b64):
    raw = zlib.decompress(base64.b64decode(b64), -15)
    return struct.unpack("<%dH" % (len(raw) // 2), raw)


def write_grid(vals):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(struct.pack("<%dH" % len(vals), *vals)) + c.flush()).decode("ascii")


def map_sections(text):
    """-> [(grid match, index just after <things>, index of </things>)], one per map. Raises unless each grid has one."""
    out = []
    for m in GRID_RE.finditer(text):
        a = text.find("<things>", m.end())
        b = text.find("</things>", m.end())
        following = text.find("<compressedThingMapDeflate>", m.end())
        if a < 0 or b < a or (following != -1 and a > following):
            raise ValueError("a compressed grid at %d has no <things> list of its own" % m.start())
        out.append((m, a + len("<things>"), b))
    return out


def full_thing(defname, cls, hp, idnum, map_id, x, z):
    head = "<thing>" if cls == "Thing" else '<thing Class="%s">' % cls
    stack = "<stackCount>1</stackCount>" if defname.startswith("Chunk") else ""
    return ("\n%s<def>%s</def><id>%s%d</id><map>%s</map><pos>(%d, 0, %d)</pos><health>%d</health>%s"
            '<questTags IsNull="True" /><spawnedTick>0</spawnedTick><despawnedTick>-1</despawnedTick>'
            "<beenRevealed>True</beenRevealed></thing>") % (head, defname, defname, idnum, map_id, x, z, hp, stack)


def add_stack_counts(section):
    """Give every full chunk with no stackCount tag an explicit 1 (point 3 of the docstring). -> (new text, how many)."""
    n = [0]

    def fix(m):
        if not m.group(1).startswith("Chunk") or "<stackCount>" in m.group(0):
            return m.group(0)
        n[0] += 1
        return m.group(0).replace("</def>", "</def><stackCount>1</stackCount>", 1)
    return THING_RE.sub(fix, section), n[0]


def expand_text(text, extra=None):
    """-> (new text, {defName: cells expanded}, chunks given a stackCount)."""
    table = dict(COMPRESSIBLE, **(extra or {}))
    idm = re.search(r"<nextThingID>(\d+)</nextThingID>", text)
    if not idm:
        raise ValueError("no <nextThingID>")
    sections = map_sections(text)
    if not sections:
        raise ValueError("no compressed thing grid")
    next_id = int(idm.group(1))
    census, stacks = {}, 0
    out, pos = [], 0
    for m, things_at, things_end in sections:
        vals = read_grid(m.group(1))
        sizes = re.findall(r"<size>\((\d+), \d+, \d+\)</size>", text[max(0, m.start() - 200000):m.start()])
        sx = int(sizes[-1]) if sizes else int(round(len(vals) ** 0.5))
        if sx * (len(vals) // sx) != len(vals):
            raise ValueError("grid of %d cells does not fit map width %d" % (len(vals), sx))
        names = resolve({v for v in vals if v}, table)
        map_id = re.search(r"<map>(-?\d+)</map>", text[things_at:things_end])
        if not map_id:
            raise ValueError("cannot read the map id: this map has no full thing to copy it from")
        added = []
        for i, v in enumerate(vals):
            if v:
                name = names[v]
                cls, hp = table[name]
                added.append(full_thing(name, cls, hp, next_id, map_id.group(1), i % sx, i // sx))
                census[name] = census.get(name, 0) + 1
                next_id += 1
        section, n = add_stack_counts(text[things_at:things_end])
        stacks += n
        out += [text[pos:m.start(1)], write_grid([0] * len(vals)), text[m.end(1):things_at], "".join(added), section]
        pos = things_end
    out.append(text[pos:])
    new = "".join(out)
    return re.sub(r"<nextThingID>\d+</nextThingID>", "<nextThingID>%d</nextThingID>" % next_id, new, count=1), census, stacks


def expand(src, dst, extra=None):
    if os.path.abspath(src) == os.path.abspath(dst):
        raise ValueError("expand writes a new file: SRC and DST are the same")
    if os.path.exists(dst):
        raise ValueError("%s exists -- a site save is never overwritten; take the next version" % dst)
    with open(src, encoding="utf-8", newline="") as f:
        text = f.read()
    new, census, stacks = expand_text(text, extra)
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    os.replace(tmp, dst)
    return {"cells": census, "stackCountsAdded": stacks, "bytes": os.path.getsize(dst)}


def expand_fresh(path, extra=None):
    """Expand a save build() has just written, in place. That one write is not an overwrite of a site: nothing has read it
    yet. A refusal deletes it, so the next build can take the same name once the def is known."""
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        new, census, stacks = expand_text(text, extra)
    except ValueError as e:
        os.remove(path)
        raise RuntimeError("%s deleted, not a portable fixture: %s" % (path, e))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    os.replace(tmp, path)
    return {"cells": census, "stackCountsAdded": stacks, "bytes": os.path.getsize(path)}


def problems(text, expect=None):
    """-> (problem strings, census {defName: full things}). Empty problems = the save holds no list-bound things."""
    bad, census, sections = [], {}, map_sections(text)
    if not sections:
        bad.append("no compressed thing grid: the instrument saw no map")
    ids = []
    for m, a, b in sections:
        left = sum(1 for v in read_grid(m.group(1)) if v)
        if left:
            bad.append("%d cells still compressed" % left)
        for t in THING_RE.finditer(text[a:b]):
            census[t.group(1)] = census.get(t.group(1), 0) + 1
            n = re.search(r"<stackCount>(\d+)</stackCount>", t.group(0))
            if t.group(1).startswith("Chunk") and not (n and int(n.group(1)) >= 1):
                bad.append("%s has no stackCount >= 1" % t.group(1))
            i = ID_RE.search(t.group(0))
            if i:
                ids.append(int(i.group(1)))
    if len(ids) != len(set(ids)):
        bad.append("%d duplicate thing ids" % (len(ids) - len(set(ids))))
    nxt = re.search(r"<nextThingID>(\d+)</nextThingID>", text)
    if not nxt:
        bad.append("no <nextThingID>")
    elif ids and max(ids) >= int(nxt.group(1)):
        bad.append("nextThingID %s is not above the highest thing id %d" % (nxt.group(1), max(ids)))
    for name, want in (expect or {}).items():
        if census.get(name, 0) != want:
            bad.append("%s: %d full things, expected %d" % (name, census.get(name, 0), want))
    return bad, census


def parse_expect(s):
    return {k: int(v) for k, v in (p.split("=", 1) for p in s.split(",") if p)} if s else {}


def cmd_check(a):
    if not os.path.isfile(a.path):
        print("UNMEASURED: the save is not on this machine: %s" % a.path)
        return 2
    with open(a.path, encoding="utf-8", newline="") as f:
        bad, census = problems(f.read(), parse_expect(a.expect))
    for name, want in sorted(parse_expect(a.expect).items()):
        print("%-30s %6d (expected %d)" % (name, census.get(name, 0), want))
    print("full things %d" % sum(census.values()))
    for b in bad[:20]:
        print("PROBLEM " + b)
    print("FAIL" if bad else "PASS")
    return 1 if bad else 0


def log_verdict(log_text, save):
    """-> (problem or None, lines counted): the log after the LAST load of `save`, which must be the last load at all."""
    at = log_text.rfind(LOAD_LINE % save)
    if at < 0:
        return "UNMEASURED: no load line for the save in Player.log", 0
    after = log_text[at:]
    other = re.search(r"Loading game from file (\S+) with mods:", after[len(LOAD_LINE % save):])
    if other:
        return "UNMEASURED: a later load replaced the save in Player.log", 0
    hits = sum(after.count(s) for s in BAD_LOG)
    return ("%d bad load lines after the load line" % hits if hits else None), hits


def things_verdict(rows, expect):
    """list_things rows -> problems. At least the expected count: a fresh load holds them all, and mining makes chunks.
    The map is what counts: Verse.Log's cap can blind the log rows while things are dropped."""
    seen = {}
    bad = []
    for r in rows:
        seen[r.get("defName") or r.get("def")] = seen.get(r.get("defName") or r.get("def"), 0) + 1
    for name, want in expect.items():
        if seen.get(name, 0) < want:
            bad.append("%s: %d on the map, at least %d expected" % (name, seen.get(name, 0), want))
    return bad


def cmd_live(a):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from game_paths import PLAYER_LOG
        import rimbridge_client as rc
        with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
            log = f.read()
        problem, _ = log_verdict(log, a.save)
        if problem and problem.startswith("UNMEASURED"):
            print(problem)
            return 2
        expect = parse_expect(a.expect)
        host, port, token = rc.resolve_endpoint(None, None, None, None)
        with rc.RimBridge(host, port, token, timeout=120) as rb:
            r = rb.call("jawa/list_things", {"defName": ",".join(sorted(expect)), "limit": 5000})
    except Exception as e:  # noqa: BLE001  no bridge or no log is no measurement, never a FAIL
        print("UNMEASURED: bridge or log not readable: %s" % str(e)[:160])
        return 2
    rows = r.get("things") if isinstance(r, dict) else None
    if not isinstance(rows, list) or r.get("isCompleteList") is False:
        print("UNMEASURED: list_things gave no complete list")
        return 2
    bad = things_verdict(rows, expect) + ([problem] if problem else [])
    print("%s rows %d" % (a.save, len(rows)))
    for b in bad:
        print("PROBLEM " + b)
    print("FAIL" if bad else "PASS")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("expand")
    e.add_argument("src")
    e.add_argument("dst")
    c = sub.add_parser("check")
    c.add_argument("path")
    c.add_argument("--expect")
    v = sub.add_parser("live")
    v.add_argument("save")
    v.add_argument("--expect", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return cmd_check(a)
    if a.cmd == "live":
        return cmd_live(a)
    print(expand(a.src, a.dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
