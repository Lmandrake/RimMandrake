#!/usr/bin/env python3
"""Measure the group size every custom creature spawns in, per live biome (BIOME_GROUP_SIZE_WALK_1).

A biome's roster is its BiomeDef's inline <wildAnimals> plus every patch Add/Replace that targets
`BiomeDef[defName="X"]/wildAnimals` (an `RM_` twin's real cast is patch-added). A creature is custom
when its PawnKindDef defName starts RM_/RSW_/RUT_. Its group size is the PawnKindDef's `wildGroupSize`
and its herd flag the race ThingDef's `race/herdAnimal`, both resolved through ParentName inheritance.

    biome_group_sizes.py measure [--json OUT]   one row per (biome, creature), today's values
    biome_group_sizes.py check                  the walk's table vs the defs; exit 0 = they agree

The live biomes are the 26 `RM_` defs of the painted world plus `RUT_Umbra` (biome_rulings.md); every
other `RUT_` BiomeDef is a frozen twin and is not walked.
"""
import argparse
import csv
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
TABLE = ROOT / "design/RimMandrake/biome_group_sizes/biome_group_sizes.csv"
RULINGS = ROOT / "design/RimStarWars/canon_herd_lore/canon_herd_lore_decisions.csv"
CUSTOM = ("RM_", "RSW_", "RUT_")
EXTRA_LIVE = {"RUT_Umbra"}


def is_live(biome):
    return biome.startswith("RM_") or biome in EXTRA_LIVE
SKIP_PARTS = ("selftest_fixtures", "Backup", "backup", "_archive", "retired")
ROSTER_FIELDS = ("wildAnimals", "wildPlants")   # surprise_book.py reads the plant roster by the same rules
ROSTER_XPATHS = {f: re.compile(r"""BiomeDef\[defName=(["'])([^"']+)\1\]/%s$""" % f) for f in ROSTER_FIELDS}
ROSTER_XPATH = ROSTER_XPATHS["wildAnimals"]
DEF_XPATH = re.compile(r"""Defs/(\w+)\[defName=(["'])([^"']+)\2\]""")


def xml_files(root=SRC):
    for p in sorted(root.rglob("*.xml")):
        if not any(part in str(p) for part in SKIP_PARTS):
            yield p


def parse(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None


def collect(root=SRC, roster="wildAnimals"):
    """Return (defs by type, patch roster ops on the `roster` list) from every XML file under root."""
    defs = {"ThingDef": {}, "PawnKindDef": {}, "BiomeDef": {}, "_all": set()}
    named = {"ThingDef": {}, "PawnKindDef": {}, "BiomeDef": {}}
    ops = []
    for path in xml_files(root):
        top = parse(path)
        if top is None:
            continue
        if top.tag == "Defs":
            for el in top:
                if el.findtext("defName"):
                    defs["_all"].add((el.tag, el.findtext("defName").strip()))
                if el.tag not in defs or el.tag == "_all":
                    continue
                dn = el.findtext("defName")
                name = el.get("Name")
                if dn:
                    defs[el.tag].setdefault(dn, []).append((path, el))
                if name and el.tag in named:
                    named[el.tag][name] = el
        elif top.tag == "Patch":
            parents = {c: p for p in top.iter() for c in p}
            for op in top.iter():
                xp = (op.findtext("xpath") or "").strip()
                m = ROSTER_XPATHS[roster].search(xp)
                cls = op.get("Class", "")
                if m and cls not in ("PatchOperationAdd", "PatchOperationReplace", "PatchOperationConditional"):
                    raise ValueError(f"{path}: roster op {cls} on {m.group(2)} is not understood")
                if m and cls in ("PatchOperationAdd", "PatchOperationReplace"):
                    value = op.find("value")
                    if value is None:
                        continue
                    rows = value.find(roster) if cls == "PatchOperationReplace" else value
                    if rows is None:
                        raise ValueError(f"{path}: Replace on {m.group(2)}'s {roster} carries no <{roster}>")
                    inherit = rows.get("Inherit", "").lower() != "false"
                    ops.append((m.group(2), cls, [c.tag for c in rows if isinstance(c.tag, str)], inherit,
                                branch(op, parents, m.group(2)), roster))
    return defs, named, ops


def branch(op, parents, biome):
    """Every enclosing Conditional's (branch, xpath) for op, innermost first; resolve() decides whether it runs."""
    conds = []
    node = op
    while node in parents:
        up = parents[node]
        if up.get("Class") == "PatchOperationConditional" and node.tag in ("match", "nomatch"):
            test = (up.findtext("xpath") or "").strip()
            conds.append((node.tag, test))
        node = up
    return conds


def resolve(conds, biome, all_defs, exists, roster="wildAnimals"):
    """True when every enclosing Conditional lets the op run; refuses a test this reader cannot evaluate."""
    for tag, test in conds:
        m = ROSTER_XPATHS[roster].search(test)
        d = DEF_XPATH.fullmatch(test.lstrip("/"))
        if m and m.group(2) == biome:
            ok = exists
        elif d:
            ok = (d.group(1), d.group(3)) in all_defs
        else:
            raise ValueError(f"roster op on {biome} under a Conditional this reader cannot resolve: {test}")
        if ok != (tag == "match"):
            return False
    return True


def field(el, path, named, depth=0):
    """Read a dotted child path from a def, falling back through ParentName."""
    hit = el.find(path)
    if hit is not None:
        return (hit.text or "").strip()
    parent = el.get("ParentName")
    if parent and parent in named and depth < 20:
        return field(named[parent], path, named, depth + 1)
    return None


def live_biomes(defs):
    return sorted(b for b in defs["BiomeDef"] if is_live(b))


def inherited_roster(el, named_biomes, roster="wildAnimals"):
    """The def's `roster` tags merged down its ParentName chain (child first; Inherit="False" stops it)."""
    chain, depth = [el], 0
    while chain[-1].get("ParentName") in named_biomes and depth < 20:
        chain.append(named_biomes[chain[-1].get("ParentName")])
        depth += 1
    cast = None
    for node in chain:
        wa = node.find(roster)
        if wa is None:
            continue
        cast = (cast or []) + [c.tag for c in wa if isinstance(c.tag, str) and c.tag not in (cast or [])]
        if wa.get("Inherit", "").lower() == "false":
            break
    return cast


def rosters(defs, ops, named, roster="wildAnimals"):
    """Each live biome's cast: patches run on the def's own XML first, then ParentName inheritance merges in,
    the order RimWorld uses. An Add to a list that does not exist matches nothing, as in game."""
    own, inherit = {}, {}
    for b in live_biomes(defs):
        if len(defs["BiomeDef"][b]) != 1:
            raise ValueError(f"{b}: {len(defs['BiomeDef'][b])} BiomeDefs")
        wa = defs["BiomeDef"][b][0][1].find(roster)
        own[b] = [c.tag for c in wa if isinstance(c.tag, str)] if wa is not None else None
        inherit[b] = wa is None or wa.get("Inherit", "").lower() != "false"
    for b, cls, rows, keeps, conds, _roster in ops:
        if b not in own or own[b] is None:
            continue
        if not resolve(conds, b, defs["_all"], True, roster):
            continue
        if cls == "PatchOperationReplace":
            own[b], inherit[b] = list(rows), keeps
        else:
            own[b] += [r for r in rows if r not in own[b]]
    out = {}
    for b, cast in own.items():
        cast = list(cast or [])
        parent = defs["BiomeDef"][b][0][1].get("ParentName")
        if inherit[b] and parent in named["BiomeDef"]:
            cast += [r for r in inherited_roster(named["BiomeDef"][parent], named["BiomeDef"], roster) or [] if r not in cast]
        out[b] = cast
    return out


def measure(root=SRC):
    defs, named, ops = collect(root)
    rows = []
    for biome, cast in rosters(defs, ops, named).items():
        for kind in cast:
            if not kind.startswith(CUSTOM):
                continue
            hits = defs["PawnKindDef"].get(kind, [])
            if not hits:
                rows.append({"biome": biome, "kind": kind, "race": "", "wildGroupSize": "NO_KINDDEF",
                             "herdAnimal": "", "kind_file": ""})
                continue
            path, el = hits[0]
            race = field(el, "race", named["PawnKindDef"]) or ""
            rhits = defs["ThingDef"].get(race, [])
            herd = field(rhits[0][1], "race/herdAnimal", named["ThingDef"]) if rhits else None
            rows.append({"biome": biome, "kind": kind, "race": race,
                         "wildGroupSize": field(el, "wildGroupSize", named["PawnKindDef"]) or "unset",
                         "herdAnimal": herd or "unset",
                         "kind_file": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                         "kind_defs": len(hits)})
    return rows


def size_range(text):
    """'2~5' -> (2, 5); '3' -> (3, 3); unset/None -> None."""
    if not text or text in ("unset", "NO_KINDDEF"):
        return None
    if not re.fullmatch(r"\d+(~\d+)?", text):
        raise ValueError(f"wildGroupSize {text!r} is not an integer range")
    lo, _, hi = text.partition("~")
    lo, hi = int(lo), int(hi or lo)
    if not 1 <= lo <= hi:
        raise ValueError(f"wildGroupSize {text!r} is not a range 1 <= a <= b")
    return lo, hi


def check(rows, table, rulings):
    """Failures between the walk's table, today's defs and the canon herd rulings."""
    bad = []
    try:
        table_sizes(table)
    except ValueError as e:
        bad.append(str(e))
    want = {(t["biome"], t["kind"]): t for t in table}
    for r in rows:
        key = (r["biome"], r["kind"])
        if r["wildGroupSize"] == "NO_KINDDEF":
            bad.append(f"{key}: no PawnKindDef carries this defName")
            continue
        if r.get("kind_defs", 1) != 1:
            bad.append(f"{key}: {r['kind_defs']} PawnKindDefs carry this defName")
        t = want.get(key)
        if t is None:
            bad.append(f"{key}: on the roster but no row in the walk's table")
            continue
        try:
            differs = size_range(r["wildGroupSize"]) != size_range(t["set_wildGroupSize"])
        except ValueError as e:
            bad.append(f"{key}: {e}")
            continue
        if differs or size_range(t["set_wildGroupSize"]) is None:
            bad.append(f"{key}: def wildGroupSize {r['wildGroupSize']} != walk {t['set_wildGroupSize']}")
        if t["src"] != "delegated:design (BIOME_GROUP_SIZE_WALK_1)":
            bad.append(f"{key}: src {t['src']!r}")
        if not t.get("judge_verdict"):
            bad.append(f"{key}: no judge verdict")
    live = {(r["biome"], r["kind"]) for r in rows}
    for key in want:
        if key not in live:
            bad.append(f"{key}: in the walk's table but not on the roster")
    by_def = {}
    for d in rulings:
        for dn in d["defs"].replace(";", " ").split():
            by_def[dn] = d["decision"]
    for r in rows:
        dec = by_def.get(r["kind"]) or by_def.get(r["race"])
        try:
            rng = size_range(r["wildGroupSize"])
        except ValueError:
            continue
        if dec == "herd" and (rng is None or rng[1] <= 1):
            bad.append(f"{r['kind']}: canon herd but wildGroupSize {r['wildGroupSize']}")
        if dec == "solitary" and rng != (1, 1):
            bad.append(f"{r['kind']}: canon solitary but wildGroupSize {r['wildGroupSize']}")
    return bad


BLOCK = re.compile(r"<PawnKindDef\b[^>]*>.*?</PawnKindDef>", re.S)
SIZE_TAG = re.compile(r"<wildGroupSize\b[^>]*>[^<]*</wildGroupSize\s*>")
COMMENT = re.compile(r"<!--.*?-->", re.S)


def write_size(text, kind, size):
    """Set `kind`'s own wildGroupSize in one file's text; returns the new text (or raises)."""
    tag = f"<defName>{kind}</defName>"
    name = re.compile(rf"<defName\s*>\s*{re.escape(kind)}\s*</defName\s*>")
    blocks = [m for m in BLOCK.finditer(text) if name.search(COMMENT.sub("", m.group(0)))]
    if len(blocks) != 1:
        raise ValueError(f"{kind}: {len(blocks)} PawnKindDef blocks in its file")
    m = blocks[0]
    block = m.group(0)
    said = "".join(COMMENT.findall(block))
    if "wildGroupSize" in said or "<defName" in said or "PawnKindDef" in said:
        raise ValueError(f"{kind}: a comment in its PawnKindDef names a field this writer edits; edit it by hand")
    if tag not in block:
        raise ValueError(f"{kind}: its defName tag is not written plainly")
    if block.count("<wildGroupSize") != len(SIZE_TAG.findall(block)):
        raise ValueError(f"{kind}: a wildGroupSize tag this writer cannot parse")
    found = SIZE_TAG.findall(block)
    new = f"<wildGroupSize>{size}</wildGroupSize>"
    if len(found) > 1:
        raise ValueError(f"{kind}: {len(found)} wildGroupSize tags in one PawnKindDef")
    if found:
        block = SIZE_TAG.sub(new, block)
    else:
        line = re.search(r"\n([ \t]*)<defName>", block)
        indent = line.group(1) if line else "    "
        block = block.replace(tag, f"{tag}\n{indent}{new}", 1)
    return text[:m.start()] + block + text[m.end():]


def table_sizes(table):
    """kind -> size from the walk's table; refuses a duplicate row or one kind given two sizes."""
    seen, want = set(), {}
    for t in table:
        key = (t["biome"], t["kind"])
        if key in seen:
            raise ValueError(f"duplicate walk row {key}")
        seen.add(key)
        if size_range(t["set_wildGroupSize"]) is None:
            raise ValueError(f"{key}: the walk sets no size")
        if want.setdefault(t["kind"], t["set_wildGroupSize"]) != t["set_wildGroupSize"]:
            raise ValueError(f"{t['kind']}: the walk gives two sizes for one PawnKindDef")
    return want


def apply(rows, table):
    """Write the walk's sizes into every PawnKindDef whose own value differs; returns files touched."""
    want = table_sizes(table)
    files = {}
    for r in rows:
        size = want.get(r["kind"])
        if size is None or size_range(r["wildGroupSize"]) == size_range(size):
            continue
        files.setdefault(r["kind_file"], {})[r["kind"]] = size
    for rel, kinds in sorted(files.items()):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        for kind, size in sorted(kinds.items()):
            text = write_size(text, kind, size)
        path.write_text(text, encoding="utf-8")
    return files


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--json")
    sub.add_parser("check")
    sub.add_parser("apply")
    a = ap.parse_args()
    rows = measure()
    if not rows:
        raise SystemExit("measured zero custom roster rows: the instrument cannot see")
    if a.cmd == "apply":
        files = apply(rows, read_csv(TABLE))
        print(f"{sum(len(k) for k in files.values())} kinds written across {len(files)} files")
        return 0
    if a.cmd == "measure":
        if a.json:
            pathlib.Path(a.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        biomes = {r["biome"] for r in rows}
        print(f"{len(rows)} custom roster rows across {len(biomes)} biomes")
        return 0
    bad = check(rows, read_csv(TABLE), read_csv(RULINGS))
    for b in bad:
        print(b)
    print(f"{len(rows)} rows checked, {len(bad)} failures")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
