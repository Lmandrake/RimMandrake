#!/usr/bin/env python3
"""vanilla_beast_carriers.py — VANILLA_BEAST_EXCISION_1 wave 3: the caravan pack-carrier route, biome by biome.

    python3 src/RimMandrake/Utils/vanilla_beast_carriers.py [--db PATH] [--save PATH] [--simulate PATCH.xml] [--json OUT]

The engine rule (decompiled 1.6, PawnGroupKindWorker_Trader, read via RimSage 2026-10-11):
  * CanGenerateFrom(parms, groupMaker) on a valid tile is
        groupMaker.carriers.Any(x => Find.WorldGrid[parms.tile].PrimaryBiome.IsPackAnimalAllowed(x.kind.race))
    and IsPackAnimalAllowed is allowedPackAnimals.Contains(race). So a faction's trader group can visit a home map
    ONLY if one of its carriers' races is in that biome's allowedPackAnimals — otherwise that group never generates.
  * The carrier itself is drawn from the same intersection, by selectionWeight.
So "which vanilla beast walks in as a pack animal, where" is exactly: carriers ∩ allowedPackAnimals, per biome.

Sources: the def dump (post-patch, pre-Cherry-Picker) for FactionDef trader groups, PawnKindDef→race, BiomeDef
allowedPackAnimals and each race's packageId (official = ludeon.rimworld*); the WORLD's factions from the canonical
start save's factionManager (a frozen world; the def set is not the faction set).

--simulate PATCH applies a VanillaBeastExcision patch file to the dump in memory and refuses (exit 3) if any
(faction, biome) pair that could trade before cannot after, or an official carrier is still reachable in a biome
the patch touched. It understands exactly two op shapes and refuses any other:
  PatchOperationAdd    xpath /Defs/FactionDef/pawnGroupMakers/li[kindDef="Trader"]/carriers[not(RSW_Bantha)]
                       (every trader group that has a carriers node and does not already list RSW_Bantha; the dump
                       cannot tell an empty <carriers/> from an absent one, so an empty group is modelled as ABSENT —
                       the pessimistic reading, which is also the true one for RUT_Jawa_FreeDroidEnclaves)
  PatchOperationRemove xpath /Defs/BiomeDef[defName="B"]/allowedPackAnimals/li[text()="R"]
  PatchOperationConditional xpath /Defs/BiomeDef[defName="B"]/allowedPackAnimals, match = PatchOperationAdd of <li>R</li>
                       to that node, nomatch = PatchOperationAdd of the whole <allowedPackAnimals> node to the BiomeDef;
                       both branches must name the same races (PACK_ANIMALS_RESTORE_EMPTY_SADDLES)
--simulate may be given more than once; the files are applied together.
Sanity probes (exit 2 if either fails — the instrument is reading nothing): OutlanderCivil's trader carriers
include Muffalo, and RM_LanternDeeps' allowedPackAnimals include Muffalo (both true of the unpatched dump).
"""
import argparse
import json
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET

DB = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite"
SAVE = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves/CANONICAL_ASHKARR_START_2026-09-12.rws"
ADD_XPATH = '/Defs/FactionDef/pawnGroupMakers/li[kindDef="Trader"]/carriers[not(RSW_Bantha)]'
REMOVE_RE = re.compile(r'^/Defs/BiomeDef\[defName="([^"]+)"\]/allowedPackAnimals/li\[text\(\)="([^"]+)"\]$')
ALLOW_RE = re.compile(r'^/Defs/BiomeDef\[defName="([^"]+)"\]/allowedPackAnimals$')


# ---------------------------------------------------------------- pure core (selftested)

def matrix(groups, allowed, kind_race, official):
    """groups: {faction: [[carrier kind, ...] per trader group]}; allowed: {biome: [race, ...]}.
    Returns {biome: {faction: {"can_trade": bool, "official": [race], "owned": [race]}}} for factions with a trader group."""
    out = {}
    for b, al in allowed.items():
        al = set(al)
        row = {}
        for f, gs in groups.items():
            if not gs:
                continue
            reach = set()
            ok = False
            for g in gs:
                hit = {kind_race.get(k, k) for k in g} & al
                ok = ok or bool(hit)
                reach |= hit
            row[f] = {"can_trade": ok, "official": sorted(r for r in reach if r in official),
                      "owned": sorted(r for r in reach if r not in official)}
        out[b] = row
    return out


def parse_patch(xml_text):
    """-> (added carrier kinds {kind: weight}, removals [(biome, race)], pack adds [(biome, race)]).
    Refuses any op shape it does not model."""
    root = ET.fromstring(xml_text)
    added, removals, pack_adds = {}, [], []
    for op in root.findall("Operation"):
        cls = op.get("Class")
        xp = (op.findtext("xpath") or "").strip()
        if cls == "PatchOperationAdd" and xp == ADD_XPATH:
            for el in op.find("value"):
                added[el.tag] = float(el.text)
        elif cls == "PatchOperationRemove" and REMOVE_RE.match(xp):
            removals.append(REMOVE_RE.match(xp).groups())
        elif cls == "PatchOperationConditional" and ALLOW_RE.match(xp):
            b = ALLOW_RE.match(xp).group(1)
            m, n = op.find("match"), op.find("nomatch")
            ok = (m is not None and n is not None and m.get("Class") == n.get("Class") == "PatchOperationAdd"
                  and (m.findtext("xpath") or "").strip() == xp
                  and (n.findtext("xpath") or "").strip() == '/Defs/BiomeDef[defName="%s"]' % b)
            node = n.find("value/allowedPackAnimals") if ok else None
            if node is None:
                raise ValueError("unmodelled allowedPackAnimals conditional for %s" % b)
            mr = [li.text.strip() for li in m.find("value").findall("li")]
            nr = [li.text.strip() for li in node.findall("li")]
            if not mr or mr != nr:
                raise ValueError("allowedPackAnimals branches disagree for %s: %s vs %s" % (b, mr, nr))
            pack_adds += [(b, r) for r in mr]
        else:
            raise ValueError("unmodelled op %s %s" % (cls, xp))
    return added, removals, pack_adds


def apply_patch(groups, allowed, added, removals, pack_adds=()):
    g2 = {f: [list(g) + [k for k in added if k not in g] if g and "RSW_Bantha" not in g else list(g) for g in gs]
          for f, gs in groups.items()}
    a2 = {b: list(v) for b, v in allowed.items()}
    for b, r in removals:
        if b not in a2 or r not in a2[b]:
            raise ValueError("remove matches nothing: %s/%s" % (b, r))  # PatchOperationRemove errors on no match too
        a2[b] = [x for x in a2[b] if x != r]
    for b, r in pack_adds:
        if b not in a2:
            raise ValueError("pack add targets no BiomeDef of ours: %s" % b)  # the xpath would match nothing
        if r not in a2[b]:
            a2[b].append(r)
    return g2, a2


def regressions(before, after, touched):
    """Pairs that could trade before and cannot after; official carriers left in touched biomes."""
    lost = [(b, f) for b, row in before.items() for f, c in row.items() if c["can_trade"] and not after[b][f]["can_trade"]]
    left = [(b, f, c["official"]) for b in touched for f, c in after[b].items() if c["official"]]
    return lost, left


# ---------------------------------------------------------------- IO

def world_factions(save):
    data = open(save, "rb").read()
    i = data.find(b"<factionManager>")
    j = data.find(b"</factionManager>", i)
    root = ET.fromstring(data[i:j] + b"</factionManager>")
    return [li.findtext("def") for li in root.find("allFactions")]


def load(db, save):
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    cap = dict(c.execute("select key, value from provenance").fetchall()).get("captured_utc")
    races = {}
    for n, p, js in c.execute("select def_name, package_id, json from defs where def_type='ThingDef'"):
        r = (json.loads(js).get("fields") or {}).get("race")
        if isinstance(r, dict) and r.get("intelligence") == "Animal":
            races[n] = p or ""
    official = {n for n, p in races.items() if p.startswith("ludeon.rimworld")}
    kind_race = {}
    for n, js in c.execute("select def_name, json from defs where def_type='PawnKindDef'"):
        r = (json.loads(js).get("fields") or {}).get("race")
        kind_race[n] = r.get("defName") if isinstance(r, dict) else r
    wf = world_factions(save)
    groups, missing = {}, []
    for f in wf:
        row = c.execute("select json from defs where def_type='FactionDef' and def_name=?", (f,)).fetchone()
        if not row:
            missing.append(f)
            continue
        gm = (json.loads(row[0]).get("fields") or {}).get("pawnGroupMakers") or []
        groups[f] = [[o["kind"] for o in (g.get("carriers") or [])] for g in gm if g.get("kindDef") == "Trader"]
    allowed = {}
    for n, p, js in c.execute("select def_name, package_id, json from defs where def_type='BiomeDef'"):
        if (p or "").startswith("mandrake."):
            allowed[n] = (json.loads(js).get("fields") or {}).get("allowedPackAnimals") or []
    return dict(captured=cap, official=official, kind_race=kind_race, groups=groups, allowed=allowed,
                world=wf, missing=missing, races=races)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--save", default=SAVE)
    ap.add_argument("--simulate", action="append")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    d = load(a.db, a.save)
    groups, allowed, kr, off = d["groups"], d["allowed"], d["kind_race"], d["official"]
    probe_f = any("Muffalo" in {kr.get(k, k) for k in g} for g in groups.get("OutlanderCivil", []))
    probe_b = "Muffalo" in allowed.get("RM_LanternDeeps", [])
    print("dump %s; world factions %d (missing from dump: %s); our BiomeDefs %d"
          % (d["captured"], len(d["world"]), d["missing"] or "none", len(allowed)))
    print("sanity probes: OutlanderCivil carries Muffalo %s; RM_LanternDeeps allows Muffalo %s"
          % ("OK" if probe_f else "FAILED", "OK" if probe_b else "FAILED"))
    if not (probe_f and probe_b):
        return 2
    m = matrix(groups, allowed, kr, off)
    traders = sorted(f for f, gs in groups.items() if gs)
    dead_groups = sorted(f for f, gs in groups.items() if any(not g for g in gs))
    no_pack = sorted(b for b, al in allowed.items() if not al)
    closed = sorted(b for b, row in m.items() if allowed[b] and not any(c["can_trade"] for c in row.values()))
    off_reach = {b: sorted({r for c in row.values() for r in c["official"]}) for b, row in m.items()}
    off_reach = {b: v for b, v in off_reach.items() if v}
    print("world trader factions: %d %s" % (len(traders), traders))
    print("trader groups with ZERO carriers (never generate on a valid tile): %s" % (dead_groups or "none"))
    print("our biomes with EMPTY allowedPackAnimals (no trader caravan from anyone): %d of %d" % (len(no_pack), len(allowed)))
    print("our biomes allowing pack animals but matching NO world faction's carrier: %s" % (closed or "none"))
    print("our biomes where an OFFICIAL carrier is reachable: %s" % (off_reach or "none"))
    out = dict(captured_utc=d["captured"], world_traders=traders, dead_trader_groups=dead_groups,
               biomes_without_pack_animals=no_pack, biomes_allowing_but_unmatched=closed,
               official_carrier_reachable=off_reach, matrix=m)
    rc = 0
    if a.simulate:
        added, removals, pack_adds = {}, [], []
        for path in a.simulate:
            ad, rm, pk = parse_patch(open(path, encoding="utf-8").read())
            added.update(ad)
            removals += rm
            pack_adds += pk
        unknown_r = sorted({r for _, r in pack_adds if r not in d["races"]})
        official_r = sorted({r for _, r in pack_adds if r in off})
        if unknown_r or official_r:
            print("SIMULATE REFUSED: unknown pack races %s, official pack races %s" % (unknown_r, official_r))
            return 3
        unknown = [k for k in added if k not in kr]
        notpack = [k for k in added if kr.get(k) in off]
        if unknown or notpack:
            print("SIMULATE REFUSED: unknown kinds %s, official kinds %s" % (unknown, notpack))
            return 3
        g2, a2 = apply_patch(groups, allowed, added, removals, pack_adds)
        m2 = matrix(g2, a2, kr, off)
        touched = sorted({b for b, _ in removals})
        lost, left = regressions(m, m2, touched)
        opened = sorted((b, f) for b, row in m2.items() for f, c in row.items() if c["can_trade"] and not m[b][f]["can_trade"])
        off2 = sorted(b for b, row in m2.items() if any(c["official"] for c in row.values()))
        print("simulate %s: +%d carrier kinds on every trader group, %d allowedPackAnimals removals in %s, "
              "%d additions in %s" % (a.simulate, len(added), len(removals), touched, len(pack_adds),
                                       sorted({b for b, _ in pack_adds})))
        still = sorted(b for b, al in a2.items() if not al)
        print("  our biomes with EMPTY allowedPackAnimals after: %d of %d" % (len(still), len(a2)))
        print("  (faction, biome) pairs opened: %d; lost: %d %s" % (len(opened), len(lost), lost or ""))
        print("  official carrier still reachable in a touched biome: %s" % (left or "none"))
        print("  biomes where an official carrier is still reachable after: %s" % (off2 or "none"))
        out["simulate"] = dict(added=added, removals=removals, pack_adds=pack_adds, opened=opened, lost=lost,
                               left=left, official_after=off2, empty_after=still)
        rc = 3 if (lost or left) else 0
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
