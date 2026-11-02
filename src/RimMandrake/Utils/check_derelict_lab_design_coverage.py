#!/usr/bin/env python3
"""Check that the derelict gene lab design covers what its item asked for, not just its citations.

Item DERELICT_LABS_DESIGN_ONE_MORE_MUTATOR asked for "a derelict gene lab as a normal
world mutator (replaces AB_DerelictBioLab) ... on vanilla's procedural ruin generator".
check_design_citations.py reads only the '## Cited machinery' table, so a doc that
stopped saying what it replaces, or stopped being a TileMutatorDef, stayed green
(blind check, gen 2). This tool reads the coverage itself:

  REPLACES  the preamble (before '## 1.') says it "replaces `AB_DerelictBioLab`", and
            AB_DerelictBioLab is a real retired TileMutatorDef key in
            design/RimMandrake/retired_mutators_port_map.json; the build section
            ('## <n>. Build order ...') maps that row to `new: RM_DerelictGeneLab`.
  MUTATOR   a row of the '## <n>. The decisions ...' table defines
            `TileMutatorDef` `RM_DerelictGeneLab` with `ParentName="AncientStructureMutBase"`,
            `TileMutatorWorker_AncientStructure` and
            `structureGenParms.structureLayoutDef` `RM_DerelictGeneLab`.
  LAYOUT    a decisions row defines `StructureLayoutDef` `RM_DerelictGeneLab` on
            `LayoutWorker_AncientRuins`.
  ROOMS     a decisions row names `LayoutRoomDef`; the '## <n>. The room table'
            table has >= 1 **new** RM_ room and >= 1 vanilla room, and every
            vanilla room is a vanilla row of '## Cited machinery'.
  NOROLL    a decisions row sets `chanceOnNonLandmarkTile` to `0` (no worldgen).
  RESOLVE   every key machinery name above, and every vanilla room, is found in
            the game's Data/ folder (check_design_citations' own search, with its
            sanity probe: TileMutatorDef found, canary absent).

Exit 0: covered. Exit 1: a clause fails (each failure is printed). Exit 2: usage or a
root unreadable. --selftest <doc> applies each mutant the blind checker named (and one
per clause) in memory and requires every one to fail ITS OWN clause and the unmutated doc green.

Usage: python3 src/RimMandrake/Utils/check_derelict_lab_design_coverage.py [--selftest] <doc.md>
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import check_design_citations as CDC  # noqa: E402

PORT_MAP = os.path.join(REPO, "design", "RimMandrake", "retired_mutators_port_map.json")
OLD, NEW = "AB_DerelictBioLab", "RM_DerelictGeneLab"
KEY_VANILLA = ("TileMutatorDef", "StructureLayoutDef", "LayoutWorker_AncientRuins",
               "TileMutatorWorker_AncientStructure", "AncientStructureMutBase",
               "LayoutRoomDef", "chanceOnNonLandmarkTile", "structureGenParms",
               "structureLayoutDef")
TICK = re.compile(r"`([A-Za-z0-9_.]+)`")


def split_doc(text):
    """Return (preamble, {lowercased heading: body}) for '## ' sections."""
    pre, secs, head, buf = [], {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if head is not None:
                secs[head] = "\n".join(buf)
            head, buf = line[3:].strip().lower(), []
        elif head is None:
            pre.append(line)
        else:
            buf.append(line)
    if head is not None:
        secs[head] = "\n".join(buf)
    return "\n".join(pre), secs


def section(secs, pattern):
    for head, body in secs.items():
        if re.match(pattern, head):
            return body
    return None


def rows(body):
    """Return data rows (cell lists) of every markdown table in body."""
    out = []
    for ln in (body or "").splitlines():
        s = ln.strip()
        if s.startswith("|") and not set(s) <= set("|-: "):
            out.append([c.strip() for c in s.strip("|").split("|")])
    return out


def cited(secs):
    return {(m.group(1), m.group(2)) for ln in (secs.get("cited machinery") or "").splitlines()
            for m in [CDC.ROW.match(ln.strip())] if m}


def check(text, vanilla_blobs, port_map):
    fails = []
    pre, secs = split_doc(text)
    # REPLACES
    if not re.search(r"replaces\W{0,4}`" + OLD + "`", pre):
        fails.append(f"REPLACES: preamble never says it replaces `{OLD}`")
    if OLD not in port_map.get("TileMutatorDef", {}):
        fails.append(f"REPLACES: {OLD} is not a retired TileMutatorDef in {PORT_MAP}")
    build = section(secs, r"\d+\.\s+build order")
    if build is None or not re.search("`" + OLD + "`[^\n]*(?:\n[^\n]+)?`new: " + NEW + "`", build):
        fails.append(f"REPLACES: build section never maps `{OLD}` to `new: {NEW}`")
    # MUTATOR / LAYOUT / NOROLL / ROOMS (decisions table)
    dec = rows(section(secs, r"\d+\.\s+the decisions"))
    if not dec:
        return fails + ["DECISIONS: no '## <n>. The decisions ...' table"]
    joined = [" | ".join(r) for r in dec]
    if not any(f"`TileMutatorDef` `{NEW}`" in r and 'ParentName="AncientStructureMutBase"' in r
               and "`TileMutatorWorker_AncientStructure`" in r
               and f"`structureGenParms.structureLayoutDef` `{NEW}`" in r for r in joined):
        fails.append(f"MUTATOR: no decisions row defines `TileMutatorDef` `{NEW}` on the AncientStructure "
                     "parent/worker with structureGenParms naming its layout")
    if not any(f"`StructureLayoutDef` `{NEW}`" in r and "`LayoutWorker_AncientRuins`" in r for r in joined):
        fails.append(f"LAYOUT: no decisions row defines `StructureLayoutDef` `{NEW}` on `LayoutWorker_AncientRuins`")
    if not any(re.search(r"`chanceOnNonLandmarkTile`[^|]*?`0`", r) for r in joined):
        fails.append("NOROLL: no decisions row sets `chanceOnNonLandmarkTile` to `0`")
    if not any("`LayoutRoomDef`" in r for r in joined):
        fails.append("ROOMS: no decisions row names `LayoutRoomDef`")
    room_rows = [r for r in rows(section(secs, r"\d+\.\s+the room table")) if len(r) >= 2 and TICK.fullmatch(r[0])]
    new_rooms = [r[0] for r in room_rows if "new" in r[1].lower() and r[0].startswith("`RM_")]
    van_rooms = [TICK.fullmatch(r[0]).group(1) for r in room_rows if r[1].lower().startswith("vanilla")]
    if not new_rooms:
        fails.append("ROOMS: room table has no **new** RM_ room")
    if not van_rooms:
        fails.append("ROOMS: room table has no vanilla room")
    cit = cited(secs)
    for name in van_rooms:
        if (name, "vanilla") not in cit:
            fails.append(f"ROOMS: vanilla room `{name}` is not a vanilla row of '## Cited machinery'")
    # RESOLVE
    for name in KEY_VANILLA + tuple(van_rooms):
        if not CDC.found(vanilla_blobs, name):
            fails.append(f"RESOLVE: `{name}` not found in vanilla Data/")
    return fails


def mutants(text):
    """(clause, label, mutated text); each must fail its own clause."""
    pre_end = text.index("\n## ")
    pre, rest = text[:pre_end], text[pre_end:]
    drop_line = lambda t, s: "\n".join(ln for ln in t.splitlines() if s not in ln)
    return [
        ("REPLACES", "blind: rename AB_DerelictBioLab, replaces->sits beside",
         text.replace(OLD, "SOMETHING").replace("replaces", "sits beside")),
        ("REPLACES", "preamble drops 'replaces'", pre.replace("replaces", "sits beside") + rest),
        ("REPLACES", "replaced name not a retired mutator", text.replace(OLD, "AB_NoSuchMutator")),
        ("REPLACES", "build section drops new: mapping", text.replace(f"`new: {NEW}`", "`new: null`")),
        ("MUTATOR", "drop TileMutatorDef decisions row", drop_line(text, "| What places the lab?")),
        ("MUTATOR", "mutator is not a TileMutatorDef", text.replace(f"`TileMutatorDef` `{NEW}`", f"`ThingDef` `{NEW}`")),
        ("LAYOUT", "drop StructureLayoutDef decisions row", drop_line(text, "| What builds the plan?")),
        ("LAYOUT", "layout on another worker", text.replace("`LayoutWorker_AncientRuins`, `structureSizeRange`",
                                                  "`LayoutWorker_Custom`, `structureSizeRange`")),
        ("NOROLL", "drop chanceOnNonLandmarkTile 0", drop_line(text, "| How does it reach the map?")),
        ("ROOMS", "drop LayoutRoomDef decisions row", drop_line(text, "| Which rooms?")),
        ("ROOMS", "room table without new rooms", re.sub(r"\| \*\*new\*\* \|", "| vanilla (Odyssey) |", text)),
        ("ROOMS", "vanilla room not cited", drop_line(text, "| `AncientLab` | vanilla | room |")),
        ("RESOLVE", "vanilla room that does not exist", text.replace("`AncientLab`", "`AncientNoSuchLab_qzx`")),
    ]


def main(argv):
    selftest = "--selftest" in argv
    args = [a for a in argv[1:] if a != "--selftest"]
    if len(args) != 1 or not os.path.isfile(args[0]):
        print(__doc__.strip().splitlines()[-1]); return 2
    blobs = CDC.load_root("vanilla")
    probe, canary = CDC.PROBES["vanilla"]
    if not blobs or not CDC.found(blobs, probe) or CDC.found(blobs, canary):
        print("UNREADABLE: vanilla Data/ failed its sanity probe"); return 2
    try:
        with open(PORT_MAP, encoding="utf-8") as fh:
            port_map = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"UNREADABLE: {PORT_MAP}: {e}"); return 2
    with open(args[0], encoding="utf-8") as fh:
        text = fh.read()
    base = check(text, blobs, port_map)
    if not selftest:
        for f in base:
            print("FAIL", f)
        print(f"{'COVERED' if not base else 'NOT COVERED'}: {len(base)} failure(s)")
        return 0 if not base else 1
    bad = 0
    if base:
        bad += 1
        print("SELFTEST FAIL: unmutated doc is red:", base)
    for clause, label, mut in mutants(text):
        if mut == text:
            bad += 1; print(f"SELFTEST FAIL: mutant '{label}' did not change the doc"); continue
        hit = [f for f in check(mut, blobs, port_map) if f.startswith(clause + ":")]
        print(f"{'red  ' if hit else 'GREEN'} [{clause}] {label}" + (f"  ({hit[0]})" if hit else ""))
        bad += 0 if hit else 1
    pm = {k: v for k, v in port_map.items() if k != "TileMutatorDef"}
    hit = [f for f in check(text, blobs, pm) if "not a retired TileMutatorDef" in f]
    print(f"{'red  ' if hit else 'GREEN'} [REPLACES] port map without {OLD}")
    bad += 0 if hit else 1
    print(f"SELFTEST {'PASS' if not bad else 'FAIL'}: {bad} problem(s)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
