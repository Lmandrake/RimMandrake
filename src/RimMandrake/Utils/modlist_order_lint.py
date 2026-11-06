#!/usr/bin/env python3
"""modlist_order_lint.py — does a ModsConfig list load every mod AFTER what its About.xml says it follows?

RimWorld loads mods in ModsConfig order. `loadAfter`/`loadBefore` (and `modDependencies`) are
not obeyed by the engine: a list that breaks them only earns a mod-menu warning, and every def
the later mod patches wins over the earlier one. Found 2026-11-03
(MODLIST_ORDER_FIX_LOADAFTER_WAS_A_SUGGESTION): ModsConfig.FULL.LATEST.xml loaded
mandrake.rut.patches at 294 and mandrake.rsw.swbestiary at 314 although UtinniPatches'
About.xml loadAfter names swbestiary, so every BeastNorm_Law3.xml patch overrode UtinniPatches
on the same field. about_load_order_lint.py checks the About graph has no cycle; this checks a
LIST obeys it.

Edges come from our own src/**/About/About.xml (repo truth, what deploys) — a composed member
of mandrake.rm.biomes (Biomes.compose.json, wave <= compose_wave) lends its edges to the
composite, as at runtime. With --installed, every other mod's edges are read from the installed
About.xml files too (modset_builder.scan: DLC, workshop, game Mods folder; Windows mounts).
An edge between two mods both on the list is a constraint: `A loadAfter B` / `A depends on B` /
`B loadBefore A` => B precedes A.

  modlist_order_lint.py <ModsConfig.xml>                 exit 1 if any of our edges is broken
  modlist_order_lint.py <ModsConfig.xml> --installed     also every installed mod's edges
  modlist_order_lint.py <ModsConfig.xml> --fix [--installed]
        rewrite the list in place by a STABLE topological sort: each mod keeps its place
        unless an edge forces it later, so a fix moves only what it must. Refuses on a cycle.
"""
import argparse
import collections
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biomes_compose  # noqa: E402
from modset_builder import read_about  # noqa: E402  (pure parser; handles <tagByVersion>)

DEFAULT_SRC = os.path.abspath(os.path.join(HERE, "..", ".."))


def repo_abouts(src_root):
    """-> {runtime packageId: {"after": set, "before": set, "why": {dep: about path}}} for our mods."""
    m = biomes_compose.load_manifest(src_root)
    folded = {}
    target = None
    if m:
        target = m["about"]["packageId"].strip().lower()
        for e in biomes_compose.composed_entries(m):
            folded[os.path.normpath(os.path.join(src_root, biomes_compose.TIER_DIR, e["source"]))] = target
    recs, member = {}, {}
    for p in sorted(glob.glob(os.path.join(src_root, "**", "About", "About.xml"), recursive=True)):
        r = read_about(p)
        if not r:
            continue
        mod_dir = os.path.normpath(os.path.dirname(os.path.dirname(p)))
        rt = folded.get(mod_dir, r["packageId"])
        if rt != r["packageId"]:
            member[r["packageId"]] = rt
        rec = recs.setdefault(rt, {"after": set(), "before": set(), "why": {}})
        rel = os.path.relpath(p, src_root)
        for a in r["deps"] + r["after"]:
            rec["after"].add(a)
            rec["why"].setdefault(a, rel)
        for b in r["before"]:
            rec["before"].add(b)
            rec["why"].setdefault(b, rel)
    for rec in recs.values():  # an edge naming a folded member means the composite
        rec["after"] = {member.get(x, x) for x in rec["after"]}
        rec["before"] = {member.get(x, x) for x in rec["before"]}
    for rt, rec in recs.items():
        rec["after"].discard(rt)
        rec["before"].discard(rt)
    return recs


def read_list(path):
    root = ET.parse(path).getroot()
    return [(li.text or "").strip() for li in root.find("activeMods").findall("li")]


def constraints(ids, recs):
    """-> {(earlier, later): why} for every edge between two listed mods."""
    on = {p.lower() for p in ids}
    out = {}
    for pid, rec in recs.items():
        if pid not in on:
            continue
        for a in rec["after"]:
            if a in on:
                out.setdefault((a, pid), "%s: %s loads after %s" % (rec["why"].get(a, "?"), pid, a))
        for b in rec["before"]:
            if b in on:
                out.setdefault((pid, b), "%s: %s loads before %s" % (rec["why"].get(b, "?"), pid, b))
    return out


def broken(ids, cons):
    pos = {p.lower(): i for i, p in enumerate(ids)}
    return sorted(((pos[a], pos[b], why) for (a, b), why in cons.items() if pos[a] > pos[b]),
                  key=lambda t: (t[1], t[0]))


def stable_sort(ids, cons):
    """Kahn's algorithm, ready set ordered by original index. -> (new ids, cycle members or [])."""
    low = [p.lower() for p in ids]
    pos = {p: i for i, p in enumerate(low)}
    preds = collections.defaultdict(set)
    succ = collections.defaultdict(set)
    for a, b in cons:
        preds[b].add(a)
        succ[a].add(b)
    import heapq
    ready = [pos[p] for p in low if not preds[p]]
    heapq.heapify(ready)
    out = []
    while ready:
        i = heapq.heappop(ready)
        p = low[i]
        out.append(ids[i])
        for s in succ[p]:
            preds[s].discard(p)
            if not preds[s]:
                heapq.heappush(ready, pos[s])
    if len(out) != len(ids):
        placed = {x.lower() for x in out}
        return ids, sorted(p for p in low if p not in placed)
    return out, []


def write_list(path, ids):
    tree = ET.parse(path)
    am = tree.getroot().find("activeMods")
    lis = am.findall("li")
    assert len(lis) == len(ids)
    for li, pid in zip(lis, ids):
        li.text = pid
    tree.write(path, encoding="utf-8", xml_declaration=True)


def gather(src_root, installed):
    recs = {}
    if installed:
        import modset_builder
        for pid, r in modset_builder.scan().items():
            recs[pid] = {"after": set(r["deps"] + r["after"]) - {pid}, "before": set(r["before"]) - {pid},
                         "why": {x: "installed %s" % os.path.basename(r.get("dir", pid))
                                 for x in r["deps"] + r["after"] + r["before"]}}
    recs.update(repo_abouts(src_root))  # ours: the repo is what deploys
    return recs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("modsconfig")
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--installed", action="store_true")
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args(argv)
    ids = read_list(a.modsconfig)
    recs = gather(os.path.abspath(a.src), a.installed)
    ours = sum(1 for p in ids if p.lower() in recs and p.lower().startswith("mandrake."))
    if ours == 0:
        print("FAIL sanity probe: none of the %d listed mods has a repo About.xml; the scan is blind" % len(ids))
        return 2
    cons = constraints(ids, recs)
    bad = broken(ids, cons)
    for pa, pb, why in bad:
        print("BROKEN  #%d must precede #%d  %s" % (pa, pb, why))
    if a.fix and bad:
        new, cyc = stable_sort(ids, cons)
        if cyc:
            print("FAIL cycle: cannot sort; mods left unplaced: %s" % ", ".join(cyc))
            return 1
        import difflib
        kept = sum(b.size for b in difflib.SequenceMatcher(None, ids, new, autojunk=False).get_matching_blocks())
        write_list(a.modsconfig, new)
        print("FIXED %s: %d broken edge(s) resolved, %d mod(s) moved" % (a.modsconfig, len(bad), len(ids) - kept))
        ids, bad = new, broken(new, cons)
    print("modlist order: %d mods listed, %d with repo About.xml, %d edge(s) between listed mods, %d broken -> %s"
          % (len(ids), ours, len(cons), len(bad), "FAILED" if bad else "OK"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
