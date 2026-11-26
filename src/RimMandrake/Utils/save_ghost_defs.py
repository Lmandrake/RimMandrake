#!/usr/bin/env python3
"""save_ghost_defs.py -- find and strip, offline, every place a savegame names a def that we deleted.

Why (SLAUGHTER_ROWS_PRUNE_GHOSTS_IN_PEN, 2026-11-26): BIOMES_PORT_PRUNE_FORTY_TWO_HITCHHIKERS (5814416460) deleted 42
Biomes! port creatures and their closure (eggs, leathers, drugs, the Pustule Hornets faction). The canonical start save
R3 still named them: 230 food-restriction filter rows, 31 auto-slaughter rows, 4 drug-policy rows, 2 worn apparel
`<stuff>`, 2 inventory things, and a whole Faction (loadID 17) with 24 relation rows pointing at it. Each missing def
is one `Could not load reference to ... named X` Log.Error on every load (ScribeExtractor.DefFromNode), then
FactionManager logs `Some factions were null after loading.` The game drops the rows, but every load of the
canonical start carries the error storm, which hides the first real exception.

    python3 save_ghost_defs.py check <save.rws> [--def NAME ...]          exit 0 none, 1 found, 2 UNMEASURED
    python3 save_ghost_defs.py strip <in.rws> <out.rws> [--def NAME ...] [--stuff-to Leather_Plain] [--apply]

Names: the prune's ROOTS + CLOSURE (src/RimStarWars/SWBestiary/selftest_biomes_port_prune_42.py) unless --def is
given; a name that src/ still defines is left out and printed (it is not a ghost). Each ghost name also brings its
implied Corpse_<name> and Meat_<name> defs (with_implied): the game generates them from the race, so no XML names them.

What strip does, by the element whose text is a ghost name (any other element shape is refused by name):
  <li>NAME</li>                    the line is removed (ThingFilter allowedDefs, world info factions, VEF ignoredFactions)
  <animal>/<drug>/<thingDef>NAME   the enclosing <li> block is removed (auto-slaughter config, drug-policy entry)
  <def>NAME in a block with <id>   the thing's <li> block is removed; refused if its id is named anywhere else
  <def>NAME in a block with
       <loadID>                    the Faction's <li> block is removed, with every relation <li> whose <other> is it;
                                   refused if Faction_<loadID> is named anywhere else after that
  <stuff>NAME                      repointed to --stuff-to (a vanilla def), so the apparel survives
Plan only without --apply. --apply refuses if OUT exists, writes OUT, re-parses it and re-runs check on it.
Byte edits only: every other byte is kept (CRLF and tabs included).
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRUNE_TEST = ROOT / "src" / "RimStarWars" / "SWBestiary" / "selftest_biomes_port_prune_42.py"
NONE, FOUND, UNMEASURED = 0, 1, 2
BLOCK_TAGS = ("animal", "drug", "thingDef")


def prune_names():
    sys.path.insert(0, str(PRUNE_TEST.parent))
    import selftest_biomes_port_prune_42 as p  # noqa: E402
    return set(p.ROOTS) | set(p.CLOSURE)


def still_defined(names):
    """Names that a <defName> or Name= under src/ still defines (not ghosts)."""
    alive = set()
    rx = re.compile(r'<defName>([^<]+)</defName>|\bName="([^"]+)"')
    for path in (ROOT / "src").rglob("*.xml"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in rx.finditer(text):
            n = m.group(1) or m.group(2)
            if n in names:
                alive.add(n)
    return alive


IMPLIED_PREFIXES = ("Corpse_", "Meat_")   # defs the game generates from a race def; no XML of ours defines them


def with_implied(names):
    """names plus the implied defs the game makes from each one (Corpse_<race>, Meat_<race>). A non-race name gets
    names that no save holds, which costs nothing. Why: after the first strip of R3, its food filters still named 282
    Corpse_<race> and 42 Meat_<race> defs of the deleted races, and the check read NONE (2026-11-26 load of R3 on
    ArchBig)."""
    return set(names) | {p + n for n in names for p in IMPLIED_PREFIXES}


def resolve_names(defs):
    if defs:
        return set(defs), set()
    names = prune_names()
    alive = still_defined(names)
    return with_implied(names - alive), alive


def census(path, names):
    """(hits: Counter of element path -> count, factions: int). Streaming parse; paths keep the last 6 tags."""
    stack, hits, factions = [], collections.Counter(), 0
    for ev, el in ET.iterparse(path, events=("start", "end")):
        if ev == "start":
            stack.append(el.tag)
            continue
        if el.tag == "li" and len(stack) >= 2 and stack[-2] == "allFactions":
            factions += 1
        t = (el.text or "").strip()
        if t in names:
            hits["/".join(stack[-6:]) + " " + t] += 1
        stack.pop()
        el.clear()
    return hits, factions


def cmd_check(path, names):
    try:
        hits, factions = census(path, names)
    except (ET.ParseError, OSError) as e:
        print(f"UNMEASURED: cannot parse {path}: {e}")
        return UNMEASURED
    if factions == 0:
        print(f"UNMEASURED: {path}: no allFactions rows parsed, the reader is blind or this is not a savegame")
        return UNMEASURED
    total = sum(hits.values())
    by_kind = collections.Counter()
    for k, c in hits.items():
        by_kind[k.split(" ")[0]] += c
    print(f"{os.path.basename(path)}: {factions} factions parsed, {len(names)} ghost names looked for")
    for k, c in by_kind.most_common():
        print(f"  {c:5d}  {k}")
    print(f"{'FOUND' if total else 'NONE'}: {total} references to deleted defs")
    return FOUND if total else NONE


LI_OPEN = re.compile(rb"<li(?:\s[^>]*)?>")
LI_SELF = re.compile(rb"<li(?:\s[^>]*)?/>")
LI_CLOSE = b"</li>"


def li_close(d, start):
    """Index just past the </li> that closes the <li> opening at start, or -1."""
    depth, i = 0, start
    while True:
        o = LI_OPEN.search(d, i)
        c = d.find(LI_CLOSE, i)
        if c < 0:
            return -1
        if o and o.start() < c:
            if not LI_SELF.match(d, o.start()):
                depth += 1
            i = o.end()
            continue
        depth -= 1
        i = c + len(LI_CLOSE)
        if depth == 0:
            return i


def enclosing_li(d, i):
    """(start, end) of the innermost <li> block that holds byte i."""
    j = i
    while True:
        s = d.rfind(b"<li", 0, j)
        if s < 0:
            raise ValueError(f"no enclosing <li> at byte {i}")
        if LI_OPEN.match(d, s) and not LI_SELF.match(d, s):
            e = li_close(d, s)
            if e > i:
                return s, e
        j = s


def line_span(d, s, e):
    """Widen [s, e) to whole lines: from the line start to past the line end (CRLF or LF)."""
    ls = d.rfind(b"\n", 0, s) + 1
    if d[ls:s].strip():
        ls = s
    le = e
    if d[e:e + 2] == b"\r\n":
        le = e + 2
    elif d[e:e + 1] == b"\n":
        le = e + 1
    return ls, le


class Refused(Exception):
    pass


def plan(d, names, stuff_to):
    """(removals: list of (start, end, why), repoints: list of (start, end, new bytes, why))."""
    alt = b"|".join(re.escape(n.encode()) for n in sorted(names, key=len, reverse=True))
    rx = re.compile(rb"<([A-Za-z_][A-Za-z0-9_.]*)>(" + alt + rb")</\1>")
    removals, repoints, faction_ids = [], [], []
    for m in rx.finditer(d):
        tag, name = m.group(1).decode(), m.group(2).decode()
        if tag == "li":
            removals.append((m.start(), m.end(), f"filter/list row: <li>{name}</li>"))
        elif tag in BLOCK_TAGS:
            s, e = enclosing_li(d, m.start())
            removals.append((s, e, f"{tag} block: <{tag}>{name}"))
        elif tag == "def":
            s, e = enclosing_li(d, m.start())
            body = d[s:e]
            lid = re.search(rb"<loadID>(\d+)</loadID>", body)
            tid = re.search(rb"<id>([^<]+)</id>", body)
            if lid and b"<relations>" in body:
                faction_ids.append(lid.group(1).decode())
                removals.append((s, e, f"faction: Faction_{lid.group(1).decode()} ({name})"))
            elif tid:
                ref = tid.group(1)
                others = len(re.findall(rb">(?:Thing_)?" + re.escape(ref) + rb"<", d))
                if others > 1:
                    raise Refused(f"thing {ref.decode()} ({name}) is named {others - 1} more time(s) in the save")
                removals.append((s, e, f"thing: {ref.decode()} ({name})"))
            else:
                raise Refused(f"<def>{name}</def> at byte {m.start()} is in a block with neither <id> nor a Faction")
        elif tag == "stuff":
            if not stuff_to:
                raise Refused(f"<stuff>{name}</stuff> at byte {m.start()} and no --stuff-to")
            repoints.append((m.start(), m.end(), f"<stuff>{stuff_to}</stuff>".encode(), f"stuff {name} -> {stuff_to}"))
        else:
            raise Refused(f"<{tag}>{name}</{tag}> at byte {m.start()}: no rule for this shape")
    for fid in faction_ids:
        for m in re.finditer(rb"<other>Faction_" + fid.encode() + rb"</other>", d):
            s, e = enclosing_li(d, m.start())
            removals.append((s, e, f"relation: to Faction_{fid}"))
    spans = []
    for s, e, why in removals:
        ls, le = line_span(d, s, e)
        spans.append((ls, le, why))
    spans.sort()
    merged = []
    for s, e, why in spans:
        if merged and s < merged[-1][1]:
            if e > merged[-1][1]:
                raise Refused(f"overlapping edits at bytes {s}-{e} ({why}) and {merged[-1][0]}-{merged[-1][1]}")
            continue  # inside a block already removed
        merged.append((s, e, why))
    for s, e, _n, why in repoints:
        if any(ms <= s < me for ms, me, _w in merged):
            raise Refused(f"{why} sits inside a removed block")
    return merged, repoints, faction_ids


def apply_edits(d, removals, repoints):
    edits = [(s, e, b"") for s, e, _w in removals] + [(s, e, new) for s, e, new, _w in repoints]
    edits.sort()
    out, pos = [], 0
    for s, e, new in edits:
        out.append(d[pos:s])
        out.append(new)
        pos = e
    out.append(d[pos:])
    return b"".join(out)


def cmd_strip(inp, out, names, stuff_to, do_apply):
    d = Path(inp).read_bytes()
    try:
        removals, repoints, fids = plan(d, names, stuff_to)
    except (Refused, ValueError) as e:
        print(f"REFUSED: {e}")
        return FOUND
    kinds = collections.Counter(w.split(":")[0] for _s, _e, w in removals)
    removed = sum(e - s for s, e, _w in removals)
    delta = sum(len(n) - (e - s) for s, e, n, _w in repoints)
    print(f"plan: {len(removals)} spans removed ({removed} bytes), {len(repoints)} repointed, factions {fids or 'none'}")
    for k, c in kinds.most_common():
        print(f"  {c:5d}  {k}")
    for _s, _e, _n, why in repoints:
        print(f"  repoint  {why}")
    if not do_apply:
        print("plan only (add --apply to write OUT)")
        return NONE
    if os.path.exists(out):
        print(f"REFUSED: {out} exists")
        return FOUND
    new = apply_edits(d, removals, repoints)
    if len(new) != len(d) - removed + delta:
        print(f"REFUSED: size {len(new)} is not {len(d)} - {removed} + {delta}")
        return FOUND
    Path(out).write_bytes(new)
    for fid in fids:
        if re.search(rb">Faction_" + fid.encode() + rb"<", new):
            print(f"FAIL: Faction_{fid} is still named in {out}")
            return FOUND
    rc = cmd_check(out, names)
    print(f"wrote {out}: {len(d)} -> {len(new)} bytes")
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("save")
    c.add_argument("--def", dest="defs", action="append")
    s = sub.add_parser("strip")
    s.add_argument("inp")
    s.add_argument("out")
    s.add_argument("--def", dest="defs", action="append")
    s.add_argument("--stuff-to", default="Leather_Plain")
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    names, alive = resolve_names(a.defs)
    if alive:
        print(f"left out (src/ still defines them): {', '.join(sorted(alive))}")
    if not names:
        print("UNMEASURED: no ghost names to look for")
        return UNMEASURED
    if a.cmd == "check":
        return cmd_check(a.save, names)
    return cmd_strip(a.inp, a.out, names, a.stuff_to, a.apply)


if __name__ == "__main__":
    sys.exit(main())
