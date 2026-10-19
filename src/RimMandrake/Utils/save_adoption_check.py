#!/usr/bin/env python3
"""save_adoption_check.py -- OFFLINE: what in a savegame will NOT resolve on a given mod list, and the live worklist.

    python3 src/RimMandrake/Utils/save_adoption_check.py [--save <.rws>] [--modlist <ModsConfig.xml>]
            [--universe-capture DIR] [--live-capture DIR] [--md out.md] [--json out.json]

Defaults: the donor-free candidate save `CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18.rws`
(Saves/), the 544-mod `ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml`. Read-only on the save: it is
parsed, never written, and nothing is written under Saves/. Item: DONOR_FOUR_RETIRE_JUST_GET_IT_DONE (A4/A5);
runbook Transient/phase0_L1_runbook.md step 6. Doctrine: skills/rimworld-savegame.

WHAT "RESOLVES" MEANS HERE (defindex.ModSetDefs): two def dumps and src/ --
  universe capture  the newest dump that still loaded the retired donors (2026-10-16, 549 mods): knows the donors'
                    names and owners, so a save name can be ATTRIBUTED to the mod that defined it;
  live capture      the newest dump (written by the donor-free load itself when there is one): a name it holds is
                    provided, full stop, and ITS shortHash table is the one the game uses when it loads the save;
  src/              our defs added after either capture (only mods whose packageId is on the list).
A name is UNRESOLVED when some source defines it and none of the list's mods does. A name no source knows is
not reported as a def (most single-token texts in a save are not def names), except under the always-a-def
tags (def, kindDef, xenotype, ...): those are listed as UNKNOWN = UNMEASURED.

GRIDS (base64 raw-DEFLATE ushort shortHashes; savemap.py has the codec rules): map terrain/under/foundation
(TerrainDef), roofs (RoofDef), deep resources (ThingDef), world tileBiome per layer (BiomeDef) and tileMutatorDefs
(TileMutatorDef, surface layer). Each hash is decoded through the LIVE table (what the game will do) and through
the universe table; a hash the live table lacks is lost on load; a hash the two tables name differently is DRIFT
(INFERRED -- the save was written by a 614-mod list that no dump captured). River/road/feature grids: not decoded.
Control: `<def>Human</def>` must read > 0 (it was 75 at P6) or the instrument is blind and the run says so.
"""
import argparse
import base64
import collections
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import defindex  # noqa: E402

SAVE_NAME = "CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18.rws"
MODLIST = os.path.join(REPO, "infrastructure", "state", "modlists",
                       "ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml")
RETIRED_FOUR = ("mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts",
                "sarg.alphabiomes")
TOKEN = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-]{1,80}$")
DEF_TAGS = {"def": None, "kindDef": "PawnKindDef", "xenotype": "XenotypeDef", "body": "BodyDef",
            "iconDef": "IdeoIconDef", "biome": "BiomeDef", "landmark": "LandmarkDef", "stuff": "ThingDef"}
# (<faction> holds a load ID such as Faction_21, never a defName: it is deliberately not a def tag.)
KINDS = (("Thing", ("ThingDef", "TerrainDef", "BodyDef", "BodyPartDef")),
         ("PawnKind/Xenotype", ("PawnKindDef", "XenotypeDef", "LifeStageDef", "GeneDef")),
         ("Hediff", ("HediffDef",)),
         ("Faction", ("FactionDef",)),
         ("Ideo meme/precept", ("MemeDef", "PreceptDef", "RitualPatternDef", "RitualBehaviorDef", "IdeoIconDef",
                                "StyleCategoryDef", "IssueDef", "RitualOutcomeEffectDef", "IdeoColorDef",
                                "AbilityDef", "NeedDef", "ThoughtDef", "HistoryEventDef")),
         ("WorldObject/landmark", ("WorldObjectDef", "LandmarkDef", "TileMutatorDef", "FeatureDef",
                                   "SitePartDef", "MapGeneratorDef")),
         ("Biome", ("BiomeDef",)))
GRIDS = (("map terrain", "topGridDeflate", "TerrainDef"), ("map under-terrain", "underGridDeflate", "TerrainDef"),
         ("map foundation", "foundationGridDeflate", "TerrainDef"), ("map roofs", "roofsDeflate", "RoofDef"),
         ("map deep resources", "defGridDeflate", "ThingDef"), ("world tileBiome", "tileBiomeDeflate", "BiomeDef"),
         ("world tileMutatorDefs", "tileMutatorDefsDeflate", "TileMutatorDef"))


def default_save():
    from game_paths import SAVES
    return os.path.join(SAVES, SAVE_NAME)


def kind_of(types, ctx_type=None):
    if ctx_type:
        types = {ctx_type} | set(types)
    for label, tys in KINDS:
        if (ctx_type and ctx_type in tys) or (not ctx_type and set(types) & set(tys)):
            return label
    for label, tys in KINDS:
        if set(types) & set(tys):
            return label
    return "Other"


class Resolver(object):
    def __init__(self, universe, live, packages, src):
        self.u = defindex.ModSetDefs(universe, packages, src)
        self.live = live
        self.live_names = set(live.by_name) if live else set()
        self.cache = {}

    def state(self, name, ctx_type=None):
        """'ok' | 'unresolved' | 'unknown' (no offline source knows the name)."""
        k = (name, ctx_type)
        if k not in self.cache:
            if name in self.live_names:
                r = "ok"
            else:
                p = self.u.provided(name, ctx_type)
                if p is None and ctx_type:
                    p = self.u.provided(name)
                r = "ok" if p else "unknown" if p is None else "unresolved"
            self.cache[k] = r
        return self.cache[k]

    def types(self, name):
        t = set(self.u.types(name))
        if self.live:
            t |= {defindex.norm_type(r[0]) for r in self.live.by_name.get(name, ())}
        return t

    def owners(self, name):
        return self.u.owner(name)

    def live_owners(self, name, def_type=None):
        if not self.live:
            return []
        return sorted({p for t, h, p in self.live.by_name.get(name, ())
                       if p and (not def_type or defindex.norm_type(t) == def_type)})

    def rehomed(self, name, def_type=None):
        """Resolves on the list, but a retired donor defined it in the save's day: ANOTHER mod's def of the same
        name will be loaded in its place (e.g. Alpha Memes ships its own AA_Eyeling, body AM_EyeBody)."""
        was = set(self.u.owner(name))
        return bool(was & set(RETIRED_FOUR)) and self.state(name, def_type) == "ok"


def ctx_type(tag, path):
    if tag in DEF_TAGS and DEF_TAGS[tag]:
        return DEF_TAGS[tag]
    if tag == "def":
        p = "/".join(path[-4:])
        if "hediffs" in p:
            return "HediffDef"
        if "directRelations" in p:
            return "PawnRelationDef"
        if "landmarks" in p:
            return "LandmarkDef"
        if "worldObjects" in p:
            return "WorldObjectDef"
        if "factions" in p and len(path) <= 6:
            return "FactionDef"
        if "precepts" in p:
            return "PreceptDef"
        if path[-2:-1] in (["thing"], ["li"]) and ("things" in path or "pawnsAlive" in path or "pawnsDead" in path):
            return "ThingDef"
    if tag == "li" and path and path[-1] == "memes":
        return "MemeDef"
    return None


def _name_of(el):
    n = el.find("name")
    if n is None:
        return None
    parts = [(n.findtext(k) or "").strip() for k in ("first", "nick", "last", "name")]
    return " ".join(p for p in parts if p) or None


def scan(save, R):
    tree = ET.parse(save)
    root = tree.getroot()
    refs = collections.defaultdict(lambda: {"n": 0, "paths": collections.Counter(), "ctx": None})
    unknown = collections.Counter()
    control = [0]
    things, rels, landmarks, kinds = [], [], [], collections.Counter()

    def walk(el, path):
        path.append(el.tag)
        t = (el.text or "").strip()
        if t and len(el) == 0 and TOKEN.match(t):
            if el.tag == "def" and t == "Human":
                control[0] += 1
            ct = ctx_type(el.tag, path[:-1])
            st = R.state(t, ct)
            if st == "unresolved":
                r = refs[t]
                r["n"] += 1
                r["paths"]["/".join(path[-4:])] += 1
                r["ctx"] = r["ctx"] or ct
            elif st == "unknown" and el.tag in DEF_TAGS:
                unknown["%s @ %s" % (t, "/".join(path[-3:]))] += 1
            if el.tag == "kindDef":
                kinds[(t, st)] += 1
        parent = path[-2] if len(path) > 1 else ""
        if (el.tag == "thing" and parent == "things") or (el.tag == "li" and parent in ("pawnsAlive", "pawnsDead")
                                                         and el.find("def") is not None):
            d = (el.findtext("def") or "").strip()
            kd = (el.findtext("kindDef") or "").strip()
            bad = [x for x in (d, kd) if x and R.state(x, "PawnKindDef" if x == kd else "ThingDef") == "unresolved"]
            moved = [x for x in (d, kd) if x and R.rehomed(x, "PawnKindDef" if x == kd else "ThingDef")]
            if bad or moved:
                things.append({"id": (el.findtext("id") or "").strip(), "def": d, "kindDef": kd or None,
                               "pos": (el.findtext("pos") or "").strip() or None, "map": el.findtext("map"),
                               "faction": (el.findtext("faction") or "").strip() or None, "name": _name_of(el),
                               "where": "world pawn (%s)" % parent if parent != "things" else "map thing",
                               "class": el.get("Class"), "rehomed": bool(moved and not bad),
                               "nowFrom": R.live_owners(d, "ThingDef") if moved and not bad else None})
        for c in el:
            walk(c, path)
        path.pop()

    walk(root, [])
    # relations and landmarks need sibling context: a second, cheap pass over the tree
    for pawn in root.iter():
        dr = pawn.find("social/directRelations") if pawn.tag in ("thing", "li") else None
        if dr is not None:
            for li in dr.findall("li"):
                o = (li.findtext("otherPawn") or "").strip()      # a reference is "Thing_" + the pawn's <id>
                rels.append({"pawn": (pawn.findtext("id") or "").strip(), "pawnName": _name_of(pawn),
                             "relation": (li.findtext("def") or "").strip(),
                             "other": o[len("Thing_"):] if o.startswith("Thing_") else o})
    for lm in root.iter("landmarks"):
        keys, vals = lm.find("keys"), lm.find("values")
        if keys is None or vals is None:
            continue
        for k, v in zip(keys.findall("li"), vals.findall("li")):
            d = (v.findtext("def") or "").strip()
            if d and R.state(d, "LandmarkDef") != "ok":
                landmarks.append({"tile": (k.text or "").strip(), "def": d, "name": (v.findtext("name") or "").strip(),
                                  "state": R.state(d, "LandmarkDef")})
    return root, refs, unknown, control[0], things, rels, landmarks, kinds


def _inflate(b64):
    return zlib.decompress(base64.b64decode("".join(b64.split())), -15)


def grids(text, live, universe, R):
    out = []
    tables = {}
    for label, tag, dtype in GRIDS:
        if dtype not in tables:
            tables[dtype] = (live.hash_table(dtype) if live else {}, universe.hash_table(dtype))
        lt, ut = tables[dtype]
        for i, m in enumerate(re.finditer(r"<%s>(.*?)</%s>" % (tag, tag), text, re.S)):
            try:
                raw = _inflate(m.group(1))
            except (zlib.error, ValueError) as exc:
                out.append({"grid": label, "n": i, "error": str(exc)})
                continue
            hs = collections.Counter(struct.unpack("<%dH" % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
            hs.pop(0, None)
            lost, drift, unres = collections.Counter(), collections.Counter(), collections.Counter()
            for h, c in hs.items():
                ln, un = lt.get(h), ut.get(h)
                if live and ln is None:
                    nm = un or "hash:%d" % h
                    if un and R.state(un, dtype) == "ok":
                        drift["%s (hash %d not in the live table; def provided)" % (un, h)] += c
                    else:
                        lost[nm] += c
                elif live and un and ln != un:
                    drift["%s -> %s" % (un, ln)] += c
                elif not live and un and R.state(un, dtype) != "ok":
                    unres[un] += c
            out.append({"grid": label, "n": i, "cells": sum(hs.values()), "distinct": len(hs),
                        "lostOnLoad": dict(lost.most_common(20)), "drift": dict(drift.most_common(20)),
                        "unresolved": dict(unres.most_common(20))})
    return out


def worklist(things, rels, landmarks, kinds, refs):
    W = []
    pawns = [t for t in things if t["class"] == "Pawn" or t["kindDef"]]
    for p in [t for t in pawns if t.get("rehomed")]:
        rb = [r for r in rels if r["other"] == p["id"]]
        if p["where"] != "map thing":
            W.append("WORLD PAWN %s (%s) %s: RE-HOMED to %s, loads as that mod's def; runbook step 6.4 does not "
                     "re-create it -- leave it, or remove it live (owner's call)%s." % (
                         p["id"], p["def"], p["where"], ",".join(p.get("nowFrom") or []) or "?",
                         "; related: " + ", ".join(r["pawn"] for r in rb) if rb else ""))
            continue
        W.append("PAWN %s (%s%s) %s at %s, faction %s: RE-HOMED -- its def now loads from %s, not the retired donor; "
                 "it will NOT be dropped. Ikee swap: destroy it, spawn %s at its cell%s." % (
                     p["id"], p["def"], ", name %s" % p["name"] if p["name"] else "", p["where"], p["pos"] or "-",
                     p["faction"] or "none", ",".join(p.get("nowFrom") or []) or "?",
                     "RSW_Ikee" if "Eyeling" in p["def"] else "its port",
                     "; re-create " + ", ".join("%s with %s (%s)" % (r["relation"], r["pawnName"] or r["pawn"],
                                                                     r["pawn"]) for r in rb) if rb else
                     "; no other pawn relates to it"))
    pawns = [t for t in pawns if not t.get("rehomed")]
    things = [t for t in things if not t.get("rehomed")]
    for p in pawns:
        rb = [r for r in rels if r["other"] == p["id"]]
        repl = "RSW_Ikee" if "Eyeling" in (p["def"] or "") else "a port of %s (none known)" % p["def"]
        W.append("PAWN %s (%s%s) %s at %s, faction %s: Scribe drops it on load. Replace with %s%s." % (
            p["id"], p["def"], ", name %s" % p["name"] if p["name"] else "", p["where"], p["pos"] or "-",
            p["faction"] or "none", repl,
            "; re-create " + ", ".join("%s with %s (%s)" % (r["relation"], r["pawnName"] or r["pawn"], r["pawn"])
                                       for r in rb) if rb else "; no other pawn relates to it"))
    bld = collections.defaultdict(list)
    for t in things:
        if t not in pawns:
            bld[t["def"]].append(t)
    if bld:
        n = sum(len(v) for v in bld.values())
        W.append("BUILDINGS/THINGS %d on maps whose def no list mod provides (Scribe drops each on load, one error "
                 "line each): %s. Live: decide replace-or-let-drop; to remove first, jawa/destroy_batch on their ids "
                 "(listed in --json)." % (n, ", ".join("%s x%d" % (k, len(v)) for k, v in
                                                      sorted(bld.items(), key=lambda kv: -len(kv[1])))))
    for lm in landmarks:
        W.append("LANDMARK tile %s %s '%s' (%s): jawa/world_landmarks_set to a provided LandmarkDef or remove it."
                 % (lm["tile"], lm["def"], lm["name"], lm["state"]))
    bad_k = {k: c for (k, st), c in kinds.items() if st != "ok"}
    W.append("kindDef rows: %d total, %d distinct; unresolved %s" % (sum(kinds.values()), len({k for k, _ in kinds}),
                                                                      bad_k or "none"))
    left = [n for n in refs if not any(n in (t["def"], t["kindDef"]) for t in things)
            and not any(n == lm["def"] for lm in landmarks)]
    if left:
        W.append("OTHER unresolved names (rows the engine drops or rebuilds, or a live decision): %s"
                 % ", ".join(sorted(left)[:40]) + (" ..." if len(left) > 40 else ""))
    return W


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--save")
    ap.add_argument("--modlist", default=MODLIST)
    ap.add_argument("--universe-capture", help="dump that still loaded the donors (default: newest such)")
    ap.add_argument("--live-capture", help="dump of the list itself (default: newest capture, used only if its mod "
                                           "set is within 3 mods of the list)")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    save = a.save or default_save()
    if not os.path.isfile(save):
        print("save not found: %s" % save)
        return 3
    packages = defindex.modlist_packages(a.modlist)
    ucap = a.universe_capture or defindex.capture_with(RETIRED_FOUR)
    universe = defindex.Index(defindex.load_raw(ucap))
    live, live_note = None, "UNMEASURED: no live capture"
    from game_paths import CAPTURES
    lcap = a.live_capture
    if not lcap:
        caps = sorted(os.listdir(CAPTURES)) if os.path.isdir(CAPTURES) else []
        lcap = os.path.join(CAPTURES, caps[-1]) if caps else None
    if lcap and os.path.abspath(lcap) != os.path.abspath(ucap or ""):
        lraw = defindex.load_raw(lcap)
        diff = set(lraw["mods"]) ^ set(packages)
        if len(diff) <= 3:
            live = defindex.Index(lraw)
            live_note = "%s (%d mods; differs from the list by %s)" % (live.capture, len(live.mods),
                                                                      sorted(diff) or "nothing")
        else:
            live_note = "UNMEASURED: newest capture %s differs from the list by %d mods" % (lraw["capture"], len(diff))
    R = Resolver(universe, live, packages, defindex.src_defs())
    root, refs, unknown, control, things, rels, landmarks, kinds = scan(save, R)
    text = open(save, encoding="utf-8", errors="replace").read()
    G = grids(text, live, universe, R)
    by_kind = collections.defaultdict(list)
    for n, r in refs.items():
        by_kind[kind_of(R.types(n), r["ctx"])].append(n)
    W = worklist(things, rels, landmarks, kinds, refs)
    L = []
    L.append("SAVE ADOPTION CHECK  %s" % os.path.basename(save))
    L.append("  list %s (%d mods) | universe %s | live %s" % (os.path.basename(a.modlist), len(packages),
                                                            universe.capture, live_note))
    L.append("  control <def>Human</def> = %d%s" % (control, "" if control else "  -- BLIND: the scan sees nothing"))
    am = {n for n, _ in R.cache if "sarg.alphamemes" in R.owners(n)}
    am_ok = sum(1 for n in am if R.state(n) == "ok")
    L.append("  control Alpha Memes names seen %d, resolving %d (it stays on the list)" % (len(am), am_ok))
    L.append("  UNRESOLVED names %d, element hits %d" % (len(refs), sum(r["n"] for r in refs.values())))
    for label, _ in KINDS + (("Other", ()),):
        ns = sorted(by_kind.get(label, []))
        if ns:
            L.append("    %-22s %3d  %s" % (label, len(ns), ", ".join("%s x%d [%s]" % (n, refs[n]["n"],
                                                                                    ",".join(R.owners(n)) or "?")
                                                                     for n in ns[:12]) + (" ..." if len(ns) > 12 else "")))
    L.append("  UNKNOWN to every offline source under a def tag (UNMEASURED): %d%s" % (
        len(unknown), "\n      " + "\n      ".join("%s x%d" % kv for kv in unknown.most_common(20)) if unknown else ""))
    L.append("  GRIDS (decoded through the live table = what the load will do)" if live else
             "  GRIDS (no live table: decoded through the universe table only, INFERRED)")
    for g in G:
        if "error" in g:
            L.append("    %-22s #%d  DECODE ERROR %s" % (g["grid"], g["n"], g["error"]))
            continue
        bits = []
        for k in ("lostOnLoad", "unresolved", "drift"):
            if g[k]:
                bits.append("%s %s" % (k, ", ".join("%s x%d" % kv for kv in list(g[k].items())[:5])))
        L.append("    %-22s #%d  %d cells, %d defs%s" % (g["grid"], g["n"], g["cells"], g["distinct"],
                                                         ("  " + " | ".join(bits)) if bits else "  clean"))
    L.append("  WORKLIST for the live pass:")
    for w in W:
        L.append("    - " + w)
    L.append("  NOT MEASURED offline: defs made at runtime that no dump captured; mods on the list never dumped "
             "(%s); hash drift vs the 614-mod list that wrote the save (no dump of it); river/road grids." %
             (sorted(set(packages) - set((live or universe).mods)) or "none"))
    rep = "\n".join(L)
    print(rep)
    if a.md:
        open(a.md, "w", encoding="utf-8").write("```\n" + rep + "\n```\n")
    if a.json:
        json.dump({"save": save, "list": a.modlist, "universe": universe.capture, "live": live_note,
                   "control": control, "unresolved": {n: {"n": r["n"], "ctx": r["ctx"], "owners": R.owners(n),
                                                          "kind": kind_of(R.types(n), r["ctx"]),
                                                          "paths": dict(r["paths"])} for n, r in refs.items()},
                   "unknown": dict(unknown), "things": things, "landmarks": landmarks,
                   "relationsToDropped": [r for r in rels if r["other"] in {t["id"] for t in things}],
                   "kindDefs": {"%s|%s" % k: c for k, c in kinds.items()}, "grids": G, "worklist": W},
                  open(a.json, "w", encoding="utf-8"), indent=1)
    if not control:
        return 3
    return 1 if refs or any(g.get("lostOnLoad") for g in G) else 0


if __name__ == "__main__":
    sys.exit(main())
