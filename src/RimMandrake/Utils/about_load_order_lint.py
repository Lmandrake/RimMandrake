#!/usr/bin/env python3
"""about_load_order_lint.py — no loadAfter/loadBefore CYCLE among our own mods.

Reads every src/**/About/About.xml and builds the ordering graph RimWorld will see,
keyed on RUNTIME packageIds: a composed member (src/RimMandrake/Biomes.compose.json,
entries with wave <= compose_wave) has no packageId at runtime, so its edges are
folded onto the composite's id (mandrake.rm.biomes), exactly as biomes_compose.py's
union_about() does. Edges to ids that are not ours are ignored (only our cycles are
ours to fix). `loadAfter`/`forceLoadAfter` X  =>  X before me; `loadBefore`/
`forceLoadBefore` X  =>  me before X. Ids are compared lower-cased, as the engine does.

Why: a cycle is silently broken by whatever sorts the list (modset_builder.py warns and
picks the lowest rank; RimSort/the engine pick their own), so the edge one mod actually
needs can lose. Found 2026-10-11: mandrake.rm.explosivegrowth loadAfter mandrake.rm.biomes
while FloodedCanyon (folded into biomes) loadAfter explosivegrowth.

Also WARNs (does not fail) when a mod outside a composite names a folded member id in
loadAfter/loadBefore: that id never loads, so the edge silently does nothing.

Usage: python3 about_load_order_lint.py [--src <src root>]   exit 1 on any cycle.
"""
import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biomes_compose  # noqa: E402

DEFAULT_SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
AFTER = ("loadAfter", "forceLoadAfter")
BEFORE = ("loadBefore", "forceLoadBefore")


def _ids(root, fields):
    out = []
    for f in fields:
        for node in root.findall(f):
            for li in node.findall("li"):
                t = (li.text or "").strip().lower()
                if t:
                    out.append(t)
    return out


def scan(src_root):
    """-> (mods, edges, warnings, problems).
    mods: {runtime id: [about paths]}; edges: {(a, b): [why]} meaning a loads before b."""
    m = biomes_compose.load_manifest(src_root)
    folded = {}  # member source folder -> composite id
    if m:
        target_id = m["about"]["packageId"].strip().lower()
        for e in biomes_compose.composed_entries(m):
            folded[os.path.normpath(os.path.join(src_root, biomes_compose.TIER_DIR, e["source"]))] = target_id
    member_ids = {}  # folded member packageId -> composite id
    abouts, problems = [], []
    for p in sorted(glob.glob(os.path.join(src_root, "**", "About", "About.xml"), recursive=True)):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as ex:
            problems.append("%s: unparseable (%s)" % (p, ex))
            continue
        own = (root.findtext("packageId") or "").strip().lower()
        if not own:
            continue
        mod_dir = os.path.normpath(os.path.dirname(os.path.dirname(p)))
        rt = folded.get(mod_dir, own)
        if rt != own:
            member_ids[own] = rt
        abouts.append((p, own, rt, root))
    mods = {}
    for p, own, rt, _ in abouts:
        mods.setdefault(rt, []).append(p)
    if m:
        mods.setdefault(m["about"]["packageId"].strip().lower(), [])
    edges, warnings = {}, []

    def resolve(x, p, rt):
        if x in member_ids:
            if rt != member_ids[x]:
                warnings.append("%s names folded member id %s (no runtime packageId; edge never applies)"
                                % (os.path.relpath(p, src_root), x))
            return member_ids[x]
        return x

    for p, own, rt, root in abouts:
        rel = os.path.relpath(p, src_root)
        for x in _ids(root, AFTER):
            x = resolve(x, p, rt)
            if x in mods and x != rt:
                edges.setdefault((x, rt), []).append("%s loadAfter %s" % (rel, x))
        for x in _ids(root, BEFORE):
            x = resolve(x, p, rt)
            if x in mods and x != rt:
                edges.setdefault((rt, x), []).append("%s loadBefore %s" % (rel, x))
    return mods, edges, warnings, problems


def find_cycles(edges):
    """Strongly connected components of size > 1 (Tarjan, iterative)."""
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set())
    index, low, on, stack, sccs, n = {}, {}, set(), [], [], [0]
    for start in sorted(adj):
        if start in index:
            continue
        work = [(start, iter(sorted(adj[start])))]
        index[start] = low[start] = n[0]; n[0] += 1
        stack.append(start); on.add(start)
        while work:
            v, it = work[-1]
            nxt = next(it, None)
            if nxt is not None:
                if nxt not in index:
                    index[nxt] = low[nxt] = n[0]; n[0] += 1
                    stack.append(nxt); on.add(nxt)
                    work.append((nxt, iter(sorted(adj[nxt]))))
                elif nxt in on:
                    low[v] = min(low[v], index[nxt])
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop(); on.discard(w); comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    sccs.append(sorted(comp))
    return sccs


def run(src_root, out=print):
    mods, edges, warnings, problems = scan(src_root)
    cycles = find_cycles(edges)
    for w in warnings:
        out("WARN " + w)
    for pr in problems:
        out("FAIL " + pr)
    for c in cycles:
        members = set(c)
        out("FAIL load-order cycle among: " + ", ".join(c))
        for (a, b), why in sorted(edges.items()):
            if a in members and b in members:
                for y in why:
                    out("       %s  (%s before %s)" % (y, a, b))
    out("about load order: %d mods, %d edges among them, %d cycle(s), %d folded-id warning(s) -> %s"
        % (len(mods), len(edges), len(cycles), len(warnings), "FAILED" if cycles or problems else "OK"))
    return cycles, warnings, problems, len(mods), len(edges)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", default=DEFAULT_SRC)
    a = ap.parse_args()
    cycles, _, problems, nmods, nedges = run(os.path.abspath(a.src))
    if nmods < 20 and os.path.abspath(a.src) == DEFAULT_SRC:
        print("FAIL sanity probe: only %d mods seen under src; the scan is blind" % nmods)
        return 1
    return 1 if cycles or problems else 0


if __name__ == "__main__":
    sys.exit(main())
