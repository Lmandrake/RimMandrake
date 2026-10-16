#!/usr/bin/env python3
"""save_donor_rewrite.py - Phase 0 step P6: rewrite a COPY of a savegame so it names no retired donor def.

    python3 save_donor_rewrite.py <in.rws> <out.rws> --table out_table.md [--dry-run]

Byte-level, never text mode: CRLF and every untouched byte survive (the output is the input with a list of
(start, end, replacement) splices applied). Never writes in place. Map/world GRIDS are NOT touched: a donor
shortHash inside a deflate grid is reported by save_donor_census-style probing and left for the owner.

Per hit (an element whose whole text is a donor defName, donors = RETIRE below; alphabiomes is report-only):
  rename  when a verified port of the right def type exists (ours = every Defs/ XML under src/), and the port is
          not already a sibling in the same list/dict (that would duplicate a set member or a dict key)
  drop    list/dict rows the engine re-creates on load (storage filters, price history, auto-slaughter configs,
          drug-policy rows, work priorities, NPC contracts, ignored factions, stale Big&Small caches)
  HOLD    everything that would change a living thing or a picture without a port: reported, untouched
Also drops `<li Class="AlphaBehavioursAndEvents.*">` map components and the donors' rows in <meta> modIds /
modSteamIds / modNames (parallel lists, removed by index).
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # repo root
sys.path.insert(0, HERE)
import save_donor_census as census  # noqa: E402

RETIRE = ("mlie.starwarsanimalcollection", "sarg.alphaanimals")
DONOR_ASSEMBLY_NS = (b"AlphaBehavioursAndEvents.",)

# Owner-ruled / ported-today mappings that are not simply RSW_<name> or RM_<name minus AA_>.
EXPLICIT = {
    # Sarlacc landmark port (Transient/phase0_sarlacc_save_renames.md)
    "sw_Sarlacc": "RSW_Sarlacc", "sw_DeadSarlacc": "RSW_DeadSarlacc",
    "SarlaccPit": "RSW_SarlaccPit", "DeadSarlacc": "RSW_DeadSarlaccHusk",
    "Blueprint_Install_SarlaccPit": "Blueprint_Install_RSW_SarlaccPit",
    "Blueprint_Install_DeadSarlacc": "Blueprint_Install_RSW_DeadSarlaccHusk",
    "SarlacciSpore": "RSW_SarlacciSpore", "SarlaccCavity": "RSW_SarlaccCavity",
    "FeedCorpse": "RSW_FeedCorpseToSarlacc", "DoBillsFeedSarlacc": "RSW_DoBillsFeedSarlacc",
    # SWAC tracker twin whose name differs
    "Wyyyschokk": "RM_Ollathrix",
    # Alpha Animals P2 (Transient/phase0_p2_classification.md)
    "AA_Aerofleet": "RM_Bulloo", "AA_AngelMoth": "RM_Dustveil", "AA_AnimaColossus": "RM_Pluurva",
    "AA_Cactipine": "RM_Chikka", "AA_Helixien": "RM_Bileworm", "AA_Lockjaw": "RM_Siezer",
    "AA_Murkling": "RM_Lirrith", "AA_ShockGoat": "RM_Zhissa",
    "AA_Swarmling": "RM_Chittik", "AA_Wildpawn": "RM_Durrok", "AA_Wildpod": "RM_Mullgoth",
    "AA_Eyeling": "RSW_Ikee",
    # shrimps (4da613788), ondrukka (aabcd7a5a), twin-only slime family (3021d7031, 3fbec5530)
    "AA_BloodShrimp": "RM_Zrrik", "AA_RaptorShrimp": "RM_Sharpshrimp",
    "VFEI2_BlackSwarmling": "RM_Ondrukka",
    "AA_GreenGoo": "RM_Wuum", "AA_AcanthamoebaGiganteaSmall": "RM_LesserOomb",
    "AA_AcanthamoebaGiganteaLarge": "RM_Oomb", "AA_AcanthamoebaGiganteaHuge": "RM_GreaterOomb",
}
# Dropped/cut by the owner 2026-10-15: never mapped, rows dropped, things HELD for him.
NO_PORT = {"Aiwha", "AA_Needlepost"}
ENGINE_PREFIX = ("Blueprint_Install_", "Blueprint_", "Frame_", "Corpse_")

TAG_RE = re.compile(rb"<(/?)([A-Za-z_][\w.:-]*)((?:\s[^<>]*?)?)(/?)>|<!--.*?-->|<\?.*?\?>", re.S)


def our_defs():
    ours = collections.defaultdict(set)
    bodies = {}
    for p in glob.glob(os.path.join(SRC, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            n = (d.findtext("defName") or "").strip()
            if n:
                ours[n].add(d.tag)
                if d.tag == "BodyDef":
                    bodies[n] = d
    return ours, bodies


def donor_bodies():
    out = {}
    for pkg in RETIRE:
        wid = census.DONORS[pkg][0]
        for p in glob.glob(os.path.join(census.WS, wid, "1.6", "**", "*.xml"), recursive=True):
            if "/Defs/" not in p:
                continue
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError:
                continue
            for d in root:
                if d.tag == "BodyDef" and d.findtext("defName"):
                    out[d.findtext("defName").strip()] = d
    return out


def body_sig(b):
    """Flattened part list in AllParts order (depth-first): (def, customLabel) - hediff part indices index this."""
    out = []

    def walk(p):
        pd = re.sub(r"^(RSW_|RM_)", "", (p.findtext("def") or "").strip())  # a ported BodyPartDef keeps its slot
        out.append((pd, (p.findtext("customLabel") or "").strip()))
        for c in p.findall("parts/li"):
            walk(c)
    cp = b.find("corePart")
    if cp is not None:
        walk(cp)
    return out


def want_type(path):
    last = path[-1]
    if last == "body":
        return "BodyDef"
    if last == "kindDef":
        return "PawnKindDef"
    if last == "Workgiver":
        return "WorkGiverDef"
    if last == "iconDef":
        return "IdeoIconDef"
    if path[-4:-1] == ["landmarks", "values", "li"]:
        return "LandmarkDef"
    if path[-3:-1] == ["abilities", "li"]:
        return "AbilityDef"
    return "ThingDef"


def port_for(name, pkg, wtype, ours):
    if name in NO_PORT:
        return None
    pre, base = "", name
    for p in ENGINE_PREFIX:
        if name.startswith(p) and name not in EXPLICIT:
            pre, base = p, name[len(p):]
            break
    if base in NO_PORT:
        return None
    cands = []
    if name in EXPLICIT:
        cands.append(EXPLICIT[name])
        pre = ""
    elif base in EXPLICIT:
        cands.append(EXPLICIT[base])
    elif pkg == "mlie.starwarsanimalcollection":
        cands += ["RSW_" + base, "RSW_" + re.sub(r"^(sw_|SW_)", "", base)]
    else:
        cands += ["RM_" + re.sub(r"^AA_", "", base)] if base.startswith("AA_") else []
    for c in cands:
        if pre:  # engine-made name: the base def must exist as a ThingDef
            if "ThingDef" in ours.get(c, ()):
                return pre + c
        elif c.startswith("Blueprint_Install_"):
            if "ThingDef" in ours.get(c[len("Blueprint_Install_"):], ()):
                return c
        elif wtype in ours.get(c, ()):
            return c
    return None


class Node(object):
    __slots__ = ("tag", "start", "cstart", "cend", "end", "idx", "parent", "text")


def scan(raw, donor_names, port_names, want_dicts):
    """One pass over the bytes. Returns hits, sibling texts, dict value rows, class nodes, meta lists."""
    stack = []
    hits = []
    sib = collections.defaultdict(set)      # parent.start -> leaf texts (donor or port names only)
    values_rows = {}                         # dict start -> [li Node, ...] of its <values>
    keep_end = {}                            # start -> Node whose end we need
    class_nodes = []
    meta_lists = {}
    nchild = [0]
    pos = 0
    for m in TAG_RE.finditer(raw):
        if m.group(2) is None:
            continue
        close, tag, attrs, selfc = m.group(1), m.group(2), m.group(3), m.group(4)
        if not close:
            n = Node()
            n.tag = tag.decode()
            n.start = m.start()
            n.cstart = m.end()
            n.idx = nchild[-1]
            nchild[-1] += 1
            n.parent = stack[-1] if stack else None
            n.text = None
            if attrs and b"Class=" in attrs and any(ns in attrs for ns in DONOR_ASSEMBLY_NS):
                class_nodes.append(n)
            if selfc:
                n.cend = n.end = m.end()
                n.text = b""
                if n.parent is not None and n.parent.tag == "values" and n.parent.parent is not None \
                        and n.parent.parent.start in want_dicts:
                    values_rows.setdefault(n.parent.parent.start, []).append(n)
                continue
            stack.append(n)
            nchild.append(0)
        else:
            n = stack.pop()
            had_children = nchild.pop()
            n.cend = m.start()
            n.end = m.end()
            if not had_children:
                t = raw[n.cstart:n.cend].strip()
                n.text = t
                if t in donor_names:
                    path = [x.tag for x in stack] + [n.tag]
                    hits.append((n, path))
                    for a in stack[-4:]:
                        keep_end[a.start] = a
                if (t in donor_names or t in port_names) and n.parent is not None:
                    sib[n.parent.start].add(t)
            p = n.parent
            if p is not None and p.tag == "values" and p.parent is not None and p.parent.start in want_dicts:
                values_rows.setdefault(p.parent.start, []).append(n)
            if n.tag in ("modIds", "modSteamIds", "modNames") and len(stack) >= 1 and stack[-1].tag == "meta":
                meta_lists[n.tag] = n
    return hits, sib, values_rows, class_nodes, meta_lists


def line_span(raw, start, end):
    """Whole lines [start,end): from after the previous newline to after the element's own line ending."""
    s = raw.rfind(b"\n", 0, start) + 1
    if raw[s:start].strip():
        s = start
    e = end
    if raw[e:e + 2] == b"\r\n":
        e += 2
    elif raw[e:e + 1] == b"\n":
        e += 1
    return s, e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--table", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if os.path.abspath(a.inp) == os.path.abspath(a.out):
        sys.exit("refusing to write in place")
    raw = open(a.inp, "rb").read()

    names = {}
    for pkg, (wid, act) in census.DONORS.items():
        for dn, ty in census.donor_defs(wid).items():
            names.setdefault(dn, (pkg, ty))
    ours, our_bodies = our_defs()
    dbodies = donor_bodies()
    donor_b = {n.encode() for n, v in names.items() if v[0] in RETIRE}
    # every possible port name, for sibling-duplicate checks
    port_b = set()
    for n, (pkg, _) in names.items():
        if pkg in RETIRE:
            for wt in ("ThingDef", "PawnKindDef", "BodyDef", "WorkGiverDef", "LandmarkDef", "AbilityDef"):
                p = port_for(n, pkg, wt, ours)
                if p:
                    port_b.add(p.encode())

    # pass 1 finds dicts holding donor keys; pass 2 collects their <values> rows
    hits, sib, _, _, _ = scan(raw, donor_b, port_b, set())
    want_dicts = {n.parent.parent.start for n, path in hits
                  if path[-2:] == ["keys", "li"] and n.parent.parent is not None}
    hits, sib, values_rows, class_nodes, meta_lists = scan(raw, donor_b, port_b, want_dicts)

    edits = []      # (start, end, bytes)
    table = collections.OrderedDict()   # (old, new|DROP|HOLD, context) -> count
    holds = []

    def rec(old, new, ctx):
        table[(old, new, ctx)] = table.get((old, new, ctx), 0) + 1

    def drop(node):
        s, e = line_span(raw, node.start, node.end)
        edits.append((s, e, b""))

    def rename(node, new):
        edits.append((node.cstart, node.cend, raw[node.cstart:node.cend].replace(node.text, new.encode())))

    body_ok = {}
    dropped_dict_rows = collections.defaultdict(set)
    for n, path in hits:
        old = n.text.decode()
        pkg = names[old][0]
        ctx = "/".join(path[-3:])
        wt = want_type(path)
        new = port_for(old, pkg, wt, ours)
        if wt == "BodyDef" and new:
            ok = body_ok.get(old)
            if ok is None:
                ok = old in dbodies and new in our_bodies and body_sig(dbodies[old]) == body_sig(our_bodies[new])
                body_ok[old] = ok
            if not ok:
                new = None
        dup = new is not None and new.encode() in sib.get(n.parent.start, ()) and path[-1] == "li"
        li = n.parent  # the row element for <li><x>NAME</x>...</li> shapes

        def in_list(container, tagname):
            return new is not None and ("<%s>%s</%s>" % (tagname, new, tagname)).encode() in raw[container.cstart:container.cend]
        if path[-4:-1] == ["priceHistoryRecorders", "values", "li"]:
            continue  # handled with its key row
        if path[-2:] == ["allowedDefs", "li"]:
            if new and not dup:
                rename(n, new); rec(old, new, ctx)
            else:
                drop(n); rec(old, "DROP", ctx)
        elif path[-2:] == ["keys", "li"]:
            d = n.parent.parent
            keyset = sib.get(n.parent.start, set())
            if new and new.encode() not in keyset:
                rename(n, new); rec(old, new, ctx)
                if path[-3] == "priceHistoryRecorders":
                    vr = values_rows.get(d.start, [])
                    if n.idx < len(vr):
                        v = vr[n.idx]
                        td = raw[v.cstart:v.cend]
                        tag = b"<thingDef>" + n.text + b"</thingDef>"
                        if tag in td:
                            off = v.cstart + td.index(tag) + len(b"<thingDef>")
                            edits.append((off, off + len(n.text), new.encode()))
            else:
                vr = values_rows.get(d.start, [])
                if n.idx >= len(vr):
                    holds.append((old, ctx, "dict values row not found")); rec(old, "HOLD", ctx); continue
                drop(n); drop(vr[n.idx]); rec(old, "DROP", ctx)
        elif ctx.endswith("configs/li/animal"):
            if new and not in_list(li.parent, "animal"):
                rename(n, new); rec(old, new, ctx)
            else:
                drop(li); rec(old, "DROP", ctx)
        elif path[-1] in ("Workgiver", "drug", "item") and path[-3] in ("Priorities", "drugs", "npcSubmittedContracts"):
            if new and (path[-3] == "npcSubmittedContracts" or not in_list(li.parent, path[-1])):
                rename(n, new); rec(old, new, ctx)
            else:
                drop(li); rec(old, "DROP", ctx)
        elif path[-2:] == ["ignoredFactions", "li"]:
            drop(n); rec(old, "DROP", ctx)
        elif path[-1] == "BS_OriginalThing":
            pid = raw.find(b"<BS_CachePawnID>", li.cstart, li.cend)
            pawn_id = raw[pid + 16:raw.find(b"<", pid + 16)] if pid >= 0 else b""
            alive = pawn_id and (b"<id>" + pawn_id + b"</id>") in raw
            if old == "AA_Eyeling":
                holds.append((old, ctx, "the ikee pawn is held")); rec(old, "HOLD", ctx)
            elif new:
                rename(n, new); rec(old, new, ctx)
            elif not alive:
                drop(li); rec(old, "DROP (pawn gone)", ctx)
            else:
                holds.append((old, ctx, "living pawn, no port")); rec(old, "HOLD", ctx)
        elif new and path[-1] in ("def", "kindDef", "body", "stuff", "thingDef", "iconDef"):
            if old == "AA_Eyeling" or (path[-1] == "body" and old == "AA_EyeBody"):
                holds.append((old, ctx, "the ikee pawn: race and body differ (AA_EyeBody vs Monkey)"))
                rec(old, "HOLD", ctx); continue
            rename(n, new); rec(old, new, ctx)
        else:
            why = "body parts differ from the port" if wt == "BodyDef" and old in body_ok else "no port"
            holds.append((old, ctx, why)); rec(old, "HOLD", ctx)

    # AA hold-out: pawns of AA_Eyeling keep their def; so their body/def/kind stay (reported).
    for cn in class_nodes:
        edits.append(line_span(raw, cn.start, cn.end) + (b"",))
        rec(raw[cn.start:cn.cstart].decode(), "DROP", "map component")

    # meta: parallel lists, remove by index
    retire_b = {p.encode() for p in RETIRE}
    ml = meta_lists.get("modIds")
    if ml is not None:
        ids = re.findall(rb"<li>([^<]*)</li>", raw[ml.cstart:ml.cend])
        kill = [i for i, x in enumerate(ids) if x.lower() in retire_b]
        for tagname in ("modIds", "modSteamIds", "modNames"):
            node = meta_lists.get(tagname)
            if node is None:
                continue
            lis = list(re.finditer(rb"<li>[^<]*</li>", raw[node.cstart:node.cend]))
            if len(lis) != len(ids):
                holds.append(("meta", tagname, "list length differs from modIds")); continue
            for i in kill:
                mm = lis[i]
                edits.append(line_span(raw, node.cstart + mm.start(), node.cstart + mm.end()) + (b"",))
                rec(mm.group(0).decode(), "DROP", "meta/" + tagname)

    # apply
    edits.sort()
    for (s1, e1, _), (s2, e2, _) in zip(edits, edits[1:]):
        if s2 < e1:
            sys.exit("overlapping edits at %d/%d - refusing" % (s1, s2))
    out = bytearray()
    last = 0
    for s, e, b in edits:
        out += raw[last:s] + b
        last = e
    out += raw[last:]
    predicted = len(raw) + sum(len(b) - (e - s) for s, e, b in edits)
    assert len(out) == predicted, (len(out), predicted)

    rows = ["| old | new | context | count |", "|---|---|---|---:|"]
    for (o, n, c), k in table.items():
        rows.append("| `%s` | %s | `%s` | %d |" % (o, n if n.startswith(("DROP", "HOLD")) else "`%s`" % n, c, k))
    hl = ["| name | context | why held |", "|---|---|---|"] + ["| `%s` | `%s` | %s |" % h for h in sorted(set(holds))]
    open(a.table, "w").write("## Rename/drop table (%d edits)\n\n%s\n\n## Held, untouched\n\n%s\n"
                             % (len(edits), "\n".join(rows), "\n".join(hl)))
    print("edits %d, renamed %d, dropped %d, held %d; bytes %d -> %d" % (
        len(edits), sum(k for (o, n, c), k in table.items() if not n.startswith(("DROP", "HOLD"))),
        sum(k for (o, n, c), k in table.items() if n.startswith("DROP")),
        sum(k for (o, n, c), k in table.items() if n == "HOLD"), len(raw), len(out)))
    if not a.dry_run:
        if os.path.exists(a.out):
            sys.exit("refusing to overwrite " + a.out)
        open(a.out, "wb").write(bytes(out))


if __name__ == "__main__":
    main()
