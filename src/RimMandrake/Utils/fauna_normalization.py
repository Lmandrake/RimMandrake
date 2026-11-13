#!/usr/bin/env python3
"""fauna_normalization.py — Laws 3, 5 and 6 of the beast normalization, over the whole roster.

Item FAUNA_TOLERANCE_NORMALIZATION_1. The laws are written in
design/Jawa/worldbuilding/beast_normalization_spec.md §2d (Law 5) and §2e (Law 3 extension, Law 6),
ruled by the owner at the 2026-09-11 phone-card sitting:

  Law 3  best melee hit in 12-15 x bodySize for every rostered animal ("one band, whole roster").
         Out-of-band animals go to K = 15 (the coefficient the SW pass quicktested and shipped);
         in-band animals are left as authored; the 28 rows of fauna_lore_divergence_manifest.csv
         take K_ruled x bodySize instead. The other tools scale by the same ratio; a tool's
         cooldown only ever lengthens, to keep its DPS at or under 10 x sqrt(bodySize).
  Law 5  ComfyTemperatureMin <= envLo - 15 and ComfyTemperatureMax >= envHi + 15, where
         [envLo, envHi] = [min p05, max p95] of tile temp_c over the animal's roster biomes.
         Widening only.
  Law 6  products follow bodySize alone: LeatherAmount base 40 (Core's animal base; the engine's
         StatPart_BodySize makes the yield linear), MeatAmount base 140 (StatDef default) for
         bodySize <= 1 and 140 x bodySize above it (the owner's 2026-08-11 megafauna rule,
         gen_megafauna_yield.py: meat ~ bodySize^2). Explicit overrides that deviate are reset;
         a 0 (meatless / hideless creature) is kept and listed as an exemption.

Three verbs:

  snapshot  (needs the game's mod folders) — resolve the 316-mod FULL list with def_inventory,
            take every animal on an RM_/RUT_ biome roster (BiomeDef wildAnimals plus src patch
            adds), and write the committed input snapshot + its fingerprint.
  generate  (pure: committed files only) — write the manifest and the three patches.
  check     (pure) — regenerate in memory, require byte-identity with the committed outputs,
            then lint every law on SIMULATED post-patch values (snapshot + the earlier patches
            that touch the same fields + ours). Exit 0 clean, 1 on findings.

  plot      draw the four sitting graphs into Transient/fauna_normalization/ (needs matplotlib).

    python3 src/RimMandrake/Utils/fauna_normalization.py snapshot [--config <ModsConfig.xml>]
    python3 src/RimMandrake/Utils/fauna_normalization.py generate
    python3 src/RimMandrake/Utils/fauna_normalization.py check
    python3 src/RimMandrake/Utils/fauna_normalization.py plot

Envelope join. The tile record (world/ASHKARR_WORLDMAP_tiles.csv) still names the painted RUT_
defs of its export date; most roster biomes are the RM_ mod twins that the paint-once repaint will
put on those same tiles (0 tiles today, expected — owner 2026-09-20). Each RM_ biome is joined to
its painted twin by design/RimMandrake/biome_mod_architecture.md §2a/§2b, and a painted name the
record no longer spells (RUT_Wastes = record RUT_Wasteland) is matched by its tile count, which
must be unique in the record. A biome with no tiles and no twin (the Lantern Deeps injection layer)
is UNMEASURED: listed by name, never passed. A pocket biome whose BiomeDef sets
constantOutdoorTemperature (the Lantern Deeps, 17 C) has that one temperature as its envelope.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "data")
SNAPSHOT = os.path.join(DATA, "fauna_norm_input.csv")
SNAPSHOT_META = os.path.join(DATA, "fauna_norm_input.meta.json")
MANIFEST = os.path.join(DATA, "fauna_norm_manifest.csv")
DIVERGENCE = os.path.join(DATA, "fauna_lore_divergence_manifest.csv")
TILES = os.path.join(ROOT, "world", "ASHKARR_WORLDMAP_tiles.csv")
ARCH = os.path.join(ROOT, "design", "RimMandrake", "biome_mod_architecture.md")
UP = os.path.join(ROOT, "src", "RimUtinni", "UtinniPatches", "Patches")
PATCH_LAW3 = os.path.join(UP, "FaunaNorm_Law3_Damage.xml")
PATCH_LAW5 = os.path.join(UP, "FaunaNorm_Law5_Tolerance.xml")
PATCH_LAW6 = os.path.join(UP, "FaunaNorm_Law6_Products.xml")
# Earlier patches that write the same fields. RimWorld applies one mod's Patches/ files in
# filesystem (= name) order, so AnimalTolerances_* run before FaunaNorm_*; the simulation does too.
PRIOR_TOLERANCE = [os.path.join(UP, n) for n in (
    "AnimalTolerances_Ashkarr.xml", "AnimalTolerances_OwnedPorts.xml",
    "AnimalTolerances_OwnedPorts_Warscar.xml")]
PRIOR_LAW3 = os.path.join(ROOT, "src", "RimStarWars", "SWBestiary", "Patches", "BeastNorm",
                          "BeastNorm_Law3.xml")
PRIOR_MEAT = [os.path.join(ROOT, "src", "RimUtinni", "Doctrine", "Patches", n) for n in (
    "MegafaunaYield.xml", "MegafaunaYield_OwnedPorts.xml", "MegafaunaYield_OwnedPorts_Warscar.xml")]
DEFAULT_CONFIG = os.path.join(ROOT, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
PLOT_DIR = os.path.join(ROOT, "Transient", "fauna_normalization")

K_LO, K_HI, K_SET = 12.0, 15.0, 15.0
DPS_K = 10.0                     # sublinear DPS ceiling for a rescaled tool: 10 x sqrt(bodySize)
MARGIN = 15.0                    # Law 5, ruled
EPSILON = 0.1                    # the spawn gate is STRICT (MapTemperature.SeasonAcceptableFor): a band
                                 # that only touches envLo - 15 would reject that exact temperature
STAT_DEFAULT = {"ComfyTemperatureMin": 0.0, "ComfyTemperatureMax": 40.0}   # Core StatDef defaults
MEAT_BASE, LEATHER_BASE = 140.0, 40.0
ROSTER_PREFIXES = ("RM_", "RUT_")
# The 25 RUT_ twin BiomeDefs deleted 2026-11-06: their names stay out of every src/ XML file, comments too
# (selftest_biome_twins_retired.py holds the same list). The tile record still spells them; the comments do not.
RETIRED_TWINS = frozenset("RUT_" + n for n in (
    "Greentide BlueDesert TheScald TheRot FeverWood Cauldron PropaneLake Scarlands ExtremeDesert GreySea SleepingIce "
    "CrackedLands Miasma Sump TwilightSea WeepingStones Slime Abyss Webwork TheForge Wastes Contagion Desert "
    "RustCathedral AridShrubland").split())
SNAP_FIELDS = ["defName", "rostered", "mod", "sourceFile", "bodySize", "biomes",
               "comfyMin", "comfyMax", "comfyMin_own", "comfyMax_own",
               "meat", "meat_own", "leather", "leather_own", "leatherDef",
               "tools_own_count", "tools_json", "tools_xml"]
MANIFEST_FIELDS = ["defName", "law", "field", "old", "new", "rule", "note"]


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def fmt(x):
    """Shortest stable decimal, 3 places: 45.0 -> '45', -6.25 -> '-6.25', 3.004 -> '3.004'."""
    s = ("%.3f" % x).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _pct(xs, p):
    """Same nearest-rank percentile as design/Jawa/fauna/animal_tolerances.py."""
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round((len(xs) - 1) * p))))] if xs else 0.0


# ---------------------------------------------------------------- snapshot (reads game files)

def _patch_roster_adds():
    """(biome, pawnkind) pairs our src patches add to RM_/RUT_ BiomeDef wildAnimals."""
    pairs = set()
    rx = re.compile(r'BiomeDef\[defName="([A-Za-z0-9_]+)"\]/wildAnimals$')
    for base, _, files in os.walk(os.path.join(ROOT, "src")):
        if os.sep + "Patches" not in base + os.sep:
            continue
        for fn in files:
            if not fn.endswith(".xml"):
                continue
            try:
                tree = ET.parse(os.path.join(base, fn))
            except ET.ParseError:
                continue
            for op in tree.iter():
                if (op.get("Class") or "") != "PatchOperationAdd":
                    continue
                m = rx.search((op.findtext("xpath") or "").strip())
                val = op.find("value")
                if not m or val is None or not m.group(1).startswith(ROSTER_PREFIXES):
                    continue
                for kid in val:
                    if isinstance(kid.tag, str):
                        pairs.add((m.group(1), kid.tag))
    return pairs


def snapshot(config):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import def_inventory as di
    ds = di.build(config=config, types=("ThingDef", "PawnKindDef", "BiomeDef"), quiet=True)
    if not ds.mods:
        sys.exit("UNMEASURED: empty load set from %s" % config)
    race_of = {}
    for rec in ds.of_type("PawnKindDef"):
        race = di.txt(rec.element, "race")
        if rec.defName and race:
            race_of[rec.defName] = race
    roster = collections.defaultdict(set)          # race defName -> biome defNames
    biome_rows = 0
    constant = {}                                  # pocket biomes: one fixed temperature
    for rec in ds.of_type("BiomeDef"):
        if not rec.defName.startswith(ROSTER_PREFIXES):
            continue
        t = fnum(di.txt(rec.element, "constantOutdoorTemperature"))
        if t is not None:
            constant[rec.defName] = t
        for w in rec.element.findall("wildAnimals/*"):
            biome_rows += 1
            roster[race_of.get(w.tag, w.tag)].add(rec.defName)
    adds = _patch_roster_adds()
    for biome, kind in adds:
        roster[race_of.get(kind, kind)].add(biome)
    wanted = set(roster) | set(divergences())     # divergence beasts take Law 3 even off-roster
    animals = {}
    for rec in ds.of_type("ThingDef"):
        # Selection by name first (cheap), then a RESOLVED <race>: a rostered def may inherit its
        # whole race block. Restricting to roster names is what keeps vehicles and mechs out.
        if rec.defName not in wanted or rec.isAbstract or rec.element.find("race") is None:
            continue
        animals[rec.defName] = rec                  # last in load order wins, as in game
    rows, missing = [], sorted(set(roster) - set(animals))
    for dn in sorted(animals):
        rec = animals[dn]
        el, own = rec.element, rec.own
        tools = []
        tel = el.find("tools")
        for i, t in enumerate(el.findall("tools/li"), 1):
            tools.append({"i": i, "label": di.txt(t, "label"),
                          "power": fnum(di.txt(t, "power")),
                          "cooldown": fnum(di.txt(t, "cooldownTime"))})
        rows.append({
            "defName": dn, "rostered": "1" if dn in roster else "0", "mod": rec.modName, "sourceFile": rec.sourceFile,
            "bodySize": di.txt(el, "race/baseBodySize") or "1",
            "biomes": ";".join(sorted(roster.get(dn, ()))),
            "comfyMin": di.txt(el, "statBases/ComfyTemperatureMin"),
            "comfyMax": di.txt(el, "statBases/ComfyTemperatureMax"),
            "comfyMin_own": di.txt(own, "statBases/ComfyTemperatureMin"),
            "comfyMax_own": di.txt(own, "statBases/ComfyTemperatureMax"),
            "meat": di.txt(el, "statBases/MeatAmount"),
            "meat_own": di.txt(own, "statBases/MeatAmount"),
            "leather": di.txt(el, "statBases/LeatherAmount"),
            "leather_own": di.txt(own, "statBases/LeatherAmount"),
            "leatherDef": di.txt(el, "race/leatherDef"),
            "tools_own_count": str(len(own.findall("tools/li"))),
            "tools_json": json.dumps(tools, separators=(",", ":")),
            "tools_xml": (ET.tostring(tel, encoding="unicode").strip() if tel is not None else ""),
        })
        rec.release()
    with open(SNAPSHOT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SNAP_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    ids = [m["packageId"] for m in ds.mods]
    meta = {
        "item": "FAUNA_TOLERANCE_NORMALIZATION_1",
        "config": os.path.relpath(config, ROOT) if config.startswith(ROOT) else config,
        "active_mods": len(ids),
        "load_set_fingerprint": hashlib.sha1("\n".join(ids).encode()).hexdigest()[:16],
        "biome_roster_rows": biome_rows, "biome_constant_temperature": constant, "patch_roster_adds": len(adds),
        "rostered_names": len(roster), "rows": len(rows),
        "rostered_with_def": sum(1 for r in rows if r["rostered"] == "1"),
        "rostered_without_def": missing,
        "note": "mod XML, inheritance-resolved, PRE-patch; defs from the deployed game Mods folder, "
                "roster patch adds from repo src",
    }
    with open(SNAPSHOT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
        f.write("\n")
    print("snapshot: %d rows, %d rostered with a def (%d names, %d without a def), %d mods, fp %s"
          % (len(rows), meta["rostered_with_def"], len(roster), len(missing), len(ids), meta["load_set_fingerprint"]))


# ---------------------------------------------------------------- inputs for generate / check

def load_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def tile_temps():
    t = collections.defaultdict(list)
    for r in load_csv(TILES):
        t[r["biome"]].append(float(r["temp_c"]))
    return t


def arch_twins():
    """RM_ BiomeDef -> (painted def named by the architecture table, tile count in the record)."""
    out = {}
    for line in open(ARCH, encoding="utf-8"):
        if not re.match(r"^\| *[0-9]", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        painted = re.findall(r"`((?:RUT_|ZBiome_)[A-Za-z]+)`", cells[1])
        counts = [int(x) for x in re.findall(r"\d+", cells[2])]
        rms = re.findall(r"`(RM_[A-Za-z]+)`", " ".join(cells[3:]))
        if not painted or not rms:
            continue
        # §2b's "RUT_TwilightSea + RUT_GreySea | 607 + 472 | ... | RM_TwilightSea, RM_GreySea":
        # pair them positionally; a §2a row is one painted def and one target.
        rms = [r for r in dict.fromkeys(rms) if not r.startswith("RM_FE_")]
        for k, p in enumerate(painted):
            if k < len(rms) and k < len(counts):
                out.setdefault(rms[k], (p, counts[k]))
    return out


def envelopes():
    """biome defName -> (lo, hi, source) or None; built once per run."""
    temps = tile_temps()
    by_count = collections.defaultdict(list)
    for b, xs in temps.items():
        by_count[len(xs)].append(b)
    twins = arch_twins()
    constant = {}
    if os.path.exists(SNAPSHOT_META):
        constant = json.load(open(SNAPSHOT_META)).get("biome_constant_temperature", {})

    def resolve(painted, count):
        if painted in temps:
            return painted
        hits = by_count.get(count, [])
        return hits[0] if len(hits) == 1 else None

    painted_of = {}
    for rm, (p, n) in twins.items():
        painted_of[rm] = resolve(p, n)
        painted_of.setdefault(p, painted_of[rm])  # the table's own painted name (RUT_Wastes)

    def env(b):
        if b in constant:                 # a pocket map's BiomeDef fixes its temperature
            return (constant[b], constant[b], "constantOutdoorTemperature")
        src = b if b in temps else painted_of.get(b)
        if not src or src not in temps:
            return None
        xs = temps[src]
        return (_pct(xs, 0.05), _pct(xs, 0.95), src)
    return env


def parse_prior_values(paths, tags):
    """[(defName, tag, value)] in file order, for <value> leaves named in `tags`."""
    out = []
    rx = re.compile(r'defName="([A-Za-z0-9_]+)"')
    for p in paths:
        if not os.path.exists(p):
            continue
        for op in ET.parse(p).iter():
            xp, val = op.find("xpath"), op.find("value")
            if xp is None or val is None:
                continue
            m = rx.search(xp.text or "")
            if not m:
                continue
            for leaf in val.iter():
                if leaf.tag in tags and fnum(leaf.text) is not None:
                    out.append((m.group(1), leaf.tag, fnum(leaf.text), (xp.text or "").strip()))
    return out


def prior_law3():
    """{(defName, tool index, field): value} written by BeastNorm_Law3.xml."""
    out = {}
    rx = re.compile(r'tools/li\[(\d+)\]/(power|cooldownTime)$')
    for dn, tag, v, xp in parse_prior_values([PRIOR_LAW3], ("power", "cooldownTime")):
        m = rx.search(xp)
        if m:
            out[(dn, int(m.group(1)), tag)] = v
    return out


def divergences():
    return {r["defName"]: r for r in load_csv(DIVERGENCE)} if os.path.exists(DIVERGENCE) else {}


# ---------------------------------------------------------------- the laws

def law3_target(bs, best, div):
    """(target best power, rule) or (None, rule) when no change is owed."""
    if div is not None:
        k = fnum(div["K_ruled"])
        rb = fnum(div["ruled_best"])
        if abs(fnum(div["bodySize"]) - bs) < 1e-6 and rb is not None:
            return rb, "divergence %s K=%s (fauna_lore_divergence_manifest.csv)" % (div["direction"], div["K_ruled"])
        return max(1.0, round(k * bs, 1)), "divergence %s K=%s, bodySize moved: K kept" % (div["direction"], div["K_ruled"])
    lo, hi = max(1.0, K_LO * bs), max(1.0, K_HI * bs)
    if lo - 1e-6 <= best <= hi + 1e-6:
        return None, "in band"
    return max(1.0, round(K_SET * bs, 1)), ("above band -> K=15" if best > hi else "below band -> K=15")


def build_all():
    """Everything generate/check need: per-animal decisions, simulated post values, findings."""
    snap = load_csv(SNAPSHOT)
    env = envelopes()
    divs = divergences()
    bn = prior_law3()
    bn_defs = {k[0] for k in bn}
    tol_prior = parse_prior_values(PRIOR_TOLERANCE, tuple(STAT_DEFAULT))
    meat_prior = parse_prior_values(PRIOR_MEAT, ("MeatAmount",))
    tol_by = collections.defaultdict(list)
    for dn, tag, v, _ in tol_prior:
        tol_by[dn].append((tag, v))
    meat_by = {}
    for dn, tag, v, _ in meat_prior:
        meat_by[dn] = v
    animals = []
    for r in snap:
        dn, bs = r["defName"], fnum(r["bodySize"]) or 1.0
        a = {"defName": dn, "bs": bs, "row": r, "manifest": [], "unmeasured": [],
             "rostered": r["rostered"] == "1"}
        # ---- Law 5 (rostered animals only; an off-roster divergence beast has no home)
        lo = hi = None
        srcs = []
        for b in (r["biomes"].split(";") if a["rostered"] else []):
            e = env(b) if b else None
            if e is None:
                a["unmeasured"].append(b)
                continue
            lo = e[0] if lo is None else min(lo, e[0])
            hi = e[1] if hi is None else max(hi, e[1])
            if b in RETIRED_TWINS:
                continue                       # its envelope counts; its name stays out of src XML
            srcs.append("%s<-%s" % (b, e[2]) if e[2] != b and e[2] not in RETIRED_TWINS else b)
        cur = {"ComfyTemperatureMin": fnum(r["comfyMin"]), "ComfyTemperatureMax": fnum(r["comfyMax"])}
        for k in cur:
            if cur[k] is None:
                cur[k] = STAT_DEFAULT[k]
        for tag, v in tol_by.get(dn, []):
            cur[tag] = v                       # absolute writes, file order
        a["comfy_pre"] = dict(cur)
        a["env"] = (lo, hi, ",".join(srcs))
        a["law5"] = {}
        if lo is not None:
            need_lo = math.floor((lo - MARGIN - EPSILON) * 10) / 10.0
            need_hi = math.ceil((hi + MARGIN + EPSILON) * 10) / 10.0
            a["need"] = (need_lo, need_hi)
            if cur["ComfyTemperatureMin"] > need_lo:
                a["law5"]["ComfyTemperatureMin"] = need_lo
            if cur["ComfyTemperatureMax"] < need_hi:
                a["law5"]["ComfyTemperatureMax"] = need_hi
            env_note = "env %s..%s (%s) +/-%s" % (fmt(lo), fmt(hi), a["env"][2], fmt(MARGIN))
            for k, v in sorted(a["law5"].items()):
                a["manifest"].append([dn, "5", k, fmt(cur[k]), fmt(v), "widen to envelope +/-15C", env_note])
        a["comfy_post"] = dict(cur, **a["law5"])
        # ---- Law 3
        tools = json.loads(r["tools_json"] or "[]")
        if dn in bn_defs:
            for t in tools:
                for fld, key in (("power", "power"), ("cooldownTime", "cooldown")):
                    v = bn.get((dn, t["i"], fld))
                    if v is not None:
                        t[key] = v
            a["law3_owner"] = "BeastNorm_Law3.xml"
        a["tools_pre"] = tools
        a["tools_post"] = [dict(t) for t in tools]
        a["law3"] = None
        best = max([t["power"] or 0 for t in tools], default=0)
        a["best_pre"] = best
        if best > 0 and dn not in bn_defs:
            target, rule = law3_target(bs, best, divs.get(dn))
            a["law3_rule"] = rule
            if target is not None and abs(target - best) > 1e-6:
                ratio = target / best
                cap = DPS_K * math.sqrt(bs)
                for t, p in zip(tools, a["tools_post"]):
                    if not t["power"]:
                        continue
                    p["power"] = target if t["power"] == best else max(0.1, round(t["power"] * ratio, 1))
                    cd = t["cooldown"] or 2.0
                    p["cooldown"] = max(cd, math.ceil(p["power"] / cap * 100) / 100.0)   # ceil: never over the cap
                a["law3"] = (best, target, rule)
                for t, p in zip(tools, a["tools_post"]):
                    if p["power"] != t["power"]:
                        a["manifest"].append([dn, "3", "tools/li[%d]/power" % t["i"], fmt(t["power"]), fmt(p["power"]),
                                              rule, "bodySize %s band %s..%s" % (fmt(bs), fmt(max(1, K_LO * bs)), fmt(max(1, K_HI * bs)))])
                    if p["cooldown"] != (t["cooldown"] or 2.0) or (t["cooldown"] is None and p["power"] != t["power"]):
                        a["manifest"].append([dn, "3", "tools/li[%d]/cooldownTime" % t["i"], fmt(t["cooldown"] or 2.0),
                                              fmt(p["cooldown"]), "cooldown lengthened: DPS <= 10 x sqrt(bodySize)", ""])
        elif best <= 0:
            a["law3_rule"] = "no melee tools"
        else:
            a["law3_rule"] = "owned by BeastNorm_Law3.xml"
        a["best_post"] = max([t["power"] or 0 for t in a["tools_post"]], default=0)
        # ---- Law 6
        a["law6"] = {}
        if not a["rostered"]:
            a["meat_post"] = a["leather_post"] = a["meat_target"] = None
            animals.append(a)
            continue
        meat = fnum(r["meat"])
        if not r["meat_own"] and dn in meat_by:
            meat = meat_by[dn]
        meat_t = MEAT_BASE * bs if bs > 1 else MEAT_BASE
        meat_t = round(meat_t, 1)
        eff_meat = MEAT_BASE if meat is None else meat
        if meat is not None and meat == 0:
            a["manifest"].append([dn, "6x", "MeatAmount", "0", "0", "exempt: meatless creature (0 kept)", ""])
        elif abs(eff_meat - meat_t) > 0.05:
            a["law6"]["MeatAmount"] = meat_t
            a["manifest"].append([dn, "6", "MeatAmount", fmt(eff_meat), fmt(meat_t),
                                  "meat base 140%s" % (" x bodySize (megafauna rule, bs>1)" if bs > 1 else ""), ""])
        leather = fnum(r["leather"])
        if leather is None or leather == 0:
            if r["leatherDef"] or leather == 0:
                a["manifest"].append([dn, "6x", "LeatherAmount", fmt(leather or 0), fmt(leather or 0),
                                      "exempt: hideless creature (0 kept)", ""])
        elif abs(leather - LEATHER_BASE) > 0.05:
            a["law6"]["LeatherAmount"] = LEATHER_BASE
            a["manifest"].append([dn, "6", "LeatherAmount", fmt(leather), fmt(LEATHER_BASE), "leather base 40", ""])
        a["meat_post"] = a["law6"].get("MeatAmount", eff_meat)
        a["leather_post"] = a["law6"].get("LeatherAmount", leather or 0)
        a["meat_target"] = meat_t
        for b in a["unmeasured"]:
            a["manifest"].append([dn, "5u", "envelope", "", "", "UNMEASURED biome %s (no tiles, no twin)" % b, ""])
        animals.append(a)
    return animals


# ---------------------------------------------------------------- emitters

HEADER = """<?xml version="1.0" encoding="utf-8"?>
<!-- GENERATED by src/RimMandrake/Utils/fauna_normalization.py generate - do not hand-edit.
     FAUNA_TOLERANCE_NORMALIZATION_1. %s
     Decision record: design/Jawa/worldbuilding/data/fauna_norm_manifest.csv.
     Law text: design/Jawa/worldbuilding/beast_normalization_spec.md %s. -->
<Patch>
"""


def _def(dn):
    return '/Defs/ThingDef[defName="%s"]' % dn


def _stat_set(dn, tag, v, guard=None):
    """Set statBases/<tag> to v on the def's own XML, adding statBases if needed.
    guard: an xpath predicate; an existing node is replaced only when it matches (widen-only)."""
    d = _def(dn)
    node = "%s/statBases/%s" % (d, tag)
    val = "<%s>%s</%s>" % (tag, fmt(v), tag)
    if guard:
        g = "%s[%s]" % (node, guard)
        match = ("    <match Class=\"PatchOperationConditional\">\n      <xpath>%s</xpath>\n"
                 "      <match Class=\"PatchOperationReplace\">\n        <xpath>%s</xpath>\n"
                 "        <value>%s</value>\n      </match>\n    </match>\n" % (g, g, val))
    else:
        match = ("    <match Class=\"PatchOperationReplace\">\n      <xpath>%s</xpath>\n"
                 "      <value>%s</value>\n    </match>\n" % (node, val))
    return ("  <Operation Class=\"PatchOperationConditional\">\n    <xpath>%s</xpath>\n%s"
            "    <nomatch Class=\"PatchOperationConditional\">\n      <xpath>%s/statBases</xpath>\n"
            "      <match Class=\"PatchOperationAdd\">\n        <xpath>%s/statBases</xpath>\n"
            "        <value>%s</value>\n      </match>\n"
            "      <nomatch Class=\"PatchOperationConditional\">\n        <xpath>%s</xpath>\n"
            "        <match Class=\"PatchOperationAdd\">\n          <xpath>%s</xpath>\n"
            "          <value><statBases>%s</statBases></value>\n        </match>\n"
            "      </nomatch>\n    </nomatch>\n  </Operation>\n"
            % (node, match, d, d, val, d, d, val))


def emit_law5(animals):
    o = [HEADER % ("Law 5: every rostered animal's comfy band covers its roster biomes' tile envelope "
                   "[p05, p95] +/-15 C.\n     WIDEN ONLY and order-proof: an existing value is replaced "
                   "only when an xpath predicate shows it is narrower.", "§2d")]
    n = 0
    for a in animals:
        if not a["law5"]:
            continue
        o.append("\n  <!-- %s: env %s..%s C (%s), band %s..%s -> %s..%s -->\n" % (
            a["defName"], fmt(a["env"][0]), fmt(a["env"][1]), a["env"][2],
            fmt(a["comfy_pre"]["ComfyTemperatureMin"]), fmt(a["comfy_pre"]["ComfyTemperatureMax"]),
            fmt(a["comfy_post"]["ComfyTemperatureMin"]), fmt(a["comfy_post"]["ComfyTemperatureMax"])))
        for tag, v in sorted(a["law5"].items()):
            guard = ("number(.) &gt; %s" if tag.endswith("Min") else "number(.) &lt; %s") % fmt(v)
            o.append(_stat_set(a["defName"], tag, v, guard))
            n += 1
    o.append("</Patch>\n")
    return "".join(o), n


def emit_law6(animals):
    o = [HEADER % ("Law 6: products follow bodySize alone (leather base 40; meat base 140, x bodySize "
                   "above 1 per the 2026-08-11 megafauna rule).", "§2e")]
    n = 0
    for a in animals:
        if not a["law6"]:
            continue
        o.append("\n  <!-- %s: bodySize %s -->\n" % (a["defName"], fmt(a["bs"])))
        for tag, v in sorted(a["law6"].items()):
            o.append(_stat_set(a["defName"], tag, v))
            n += 1
    o.append("</Patch>\n")
    return "".join(o), n


def _tools_xml_rescaled(a):
    """The resolved tools list with the new power/cooldown, as <tools Inherit="False">."""
    el = ET.fromstring(a["row"]["tools_xml"])
    el.attrib.clear()
    el.set("Inherit", "False")
    for li, p in zip(el.findall("li"), a["tools_post"]):
        for fld, key in (("power", "power"), ("cooldownTime", "cooldown")):
            if p[key] is None:            # a tool with no such leaf keeps none (never an empty element)
                continue
            node = li.find(fld)
            if node is None:
                node = ET.SubElement(li, fld)
            node.text = fmt(p[key])
    return ET.tostring(el, encoding="unicode")


def emit_law3(animals):
    o = [HEADER % ("Law 3: best melee hit in 12-15 x bodySize for the whole roster (out of band -> K=15;\n"
                   "     the 28 lore divergences at their ruled K). Defs BeastNorm_Law3.xml already owns are skipped.", "§2, §2e")]
    n = 0
    for a in animals:
        if not a["law3"]:
            continue
        dn, r = a["defName"], a["row"]
        best, target, rule = a["law3"]
        o.append("\n  <!-- %s: bodySize %s, best %s -> %s (%s) -->\n" % (dn, fmt(a["bs"]), fmt(best), fmt(target), rule))
        own = int(r["tools_own_count"] or 0)
        if own == len(a["tools_pre"]):
            for t, p in zip(a["tools_pre"], a["tools_post"]):
                for fld, key, old in (("power", "power", t["power"]), ("cooldownTime", "cooldown", t["cooldown"])):
                    if p[key] == old:
                        continue
                    x = "%s/tools/li[%d]/%s" % (_def(dn), t["i"], fld)
                    li = "%s/tools/li[%d]" % (_def(dn), t["i"])
                    o.append("  <Operation Class=\"PatchOperationConditional\">\n    <xpath>%s</xpath>\n"
                             "    <match Class=\"PatchOperationReplace\">\n      <xpath>%s</xpath>\n"
                             "      <value><%s>%s</%s></value>\n    </match>\n"
                             "    <nomatch Class=\"PatchOperationConditional\">\n      <xpath>%s</xpath>\n"
                             "      <match Class=\"PatchOperationAdd\">\n        <xpath>%s</xpath>\n"
                             "        <value><%s>%s</%s></value>\n      </match>\n    </nomatch>\n  </Operation>\n"
                             % (x, x, fld, fmt(p[key]), fld, li, li, fld, fmt(p[key]), fld))
                    n += 1
        else:
            # Tools inherited (whole or in part): give the def its own full list, Inherit="False",
            # so the parent's list is not appended to it.
            body = _tools_xml_rescaled(a)
            o.append("  <Operation Class=\"PatchOperationConditional\">\n    <xpath>%s/tools</xpath>\n"
                     "    <match Class=\"PatchOperationReplace\">\n      <xpath>%s/tools</xpath>\n"
                     "      <value>%s</value>\n    </match>\n"
                     "    <nomatch Class=\"PatchOperationConditional\">\n      <xpath>%s</xpath>\n"
                     "      <match Class=\"PatchOperationAdd\">\n        <xpath>%s</xpath>\n"
                     "        <value>%s</value>\n      </match>\n    </nomatch>\n  </Operation>\n"
                     % (_def(dn), _def(dn), body, _def(dn), _def(dn), body))
            n += 1
    o.append("</Patch>\n")
    return "".join(o), n


def emit_manifest(animals):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(MANIFEST_FIELDS)
    for a in animals:
        for row in a["manifest"]:
            w.writerow(row)
    return buf.getvalue()


def outputs(animals):
    return {MANIFEST: emit_manifest(animals), PATCH_LAW3: emit_law3(animals)[0],
            PATCH_LAW5: emit_law5(animals)[0], PATCH_LAW6: emit_law6(animals)[0]}


# ---------------------------------------------------------------- lint

def lint(animals):
    bad, notes = [], []
    rost = [a for a in animals if a["rostered"]]
    if len(rost) < 400:
        bad.append("snapshot holds only %d rostered animals (expected 400+): a short read" % len(rost))
    divs = divergences()
    measured = unmeasured_only = 0
    for a in animals:
        dn, bs = a["defName"], a["bs"]
        if "need" in a:
            measured += 1
            lo, hi = a["need"]
            mn, mx = a["comfy_post"]["ComfyTemperatureMin"], a["comfy_post"]["ComfyTemperatureMax"]
            if mn > lo + 1e-6 or mx < hi - 1e-6:
                bad.append("Law5 %s: band %s..%s does not cover need %s..%s" % (dn, fmt(mn), fmt(mx), fmt(lo), fmt(hi)))
        else:
            unmeasured_only += 1
        b = a["best_post"]
        if b > 0:
            if dn in divs:
                k = fnum(divs[dn]["K_ruled"])
                want = fnum(divs[dn]["ruled_best"]) if abs(fnum(divs[dn]["bodySize"]) - bs) < 1e-6 else max(1.0, round(k * bs, 1))
                if abs(b - want) > 0.05:
                    bad.append("Law3 %s: best %s, divergence wants %s" % (dn, fmt(b), fmt(want)))
            elif a["rostered"] and not (max(1.0, K_LO * bs) - 0.05 <= b <= max(1.0, K_HI * bs) + 0.05):
                bad.append("Law3 %s: best %s outside %s..%s (%s)" % (dn, fmt(b), fmt(max(1, K_LO * bs)),
                                                                     fmt(max(1, K_HI * bs)), a.get("law3_rule")))
        if not a["rostered"]:
            continue
        if a["meat_post"] not in (0, None) and abs(a["meat_post"] - a["meat_target"]) > 0.05:
            bad.append("Law6 %s: meat base %s != %s" % (dn, fmt(a["meat_post"]), fmt(a["meat_target"])))
        if a["leather_post"] and abs(a["leather_post"] - LEATHER_BASE) > 0.05:
            bad.append("Law6 %s: leather base %s != 40" % (dn, fmt(a["leather_post"])))
    if measured < 300:
        bad.append("only %d animals have a measured envelope (expected 300+): the biome join is broken" % measured)
    unm = sorted({b for a in animals for b in a["unmeasured"]})
    notes.append("rows %d, rostered %d; Law 5 measured %d, envelope-unmeasured %d (biomes with no tiles and no twin: %s)"
                 % (len(animals), len(rost), measured, unmeasured_only - (len(animals) - len(rost)), ", ".join(unm) or "none"))
    return bad, notes


def cmd_generate():
    animals = build_all()
    for path, text in outputs(animals).items():
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    _, n3 = emit_law3(animals)
    _, n5 = emit_law5(animals)
    _, n6 = emit_law6(animals)
    print("generate: %d animals; ops Law3 %d, Law5 %d, Law6 %d; manifest %d rows"
          % (len(animals), n3, n5, n6, sum(len(a["manifest"]) for a in animals)))


def cmd_check():
    animals = build_all()
    bad, notes = lint(animals)
    for path, text in outputs(animals).items():
        cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if cur != text:
            bad.append("STALE: %s differs from a regeneration (run generate)" % os.path.relpath(path, ROOT))
    for n in notes:
        print("note:", n)
    for b in bad:
        print("FINDING:", b)
    print("check: %s (%d findings)" % ("CLEAN" if not bad else "FAIL", len(bad)))
    return 0 if not bad else 1


def cmd_plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    animals = build_all()
    os.makedirs(PLOT_DIR, exist_ok=True)
    fp = json.load(open(SNAPSHOT_META))["load_set_fingerprint"]
    src = "source: fauna_norm_input.csv, load set %s (%s mods), post = simulated post-patch" % (
        fp, json.load(open(SNAPSHOT_META))["active_mods"])

    def outliers(ax, pts, n=12):
        for x, y, lab in sorted(pts, key=lambda p: -p[1])[:n]:
            ax.annotate(lab, (x, y), fontsize=6, xytext=(3, 2), textcoords="offset points")

    xs = [a["bs"] for a in animals if a["best_post"]]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, key, title in ((axes[0], "best_pre", "before"), (axes[1], "best_post", "after")):
        bsr = sorted(set(xs))
        ax.fill_between(bsr, [max(1, K_LO * b) for b in bsr], [max(1, K_HI * b) for b in bsr], color="#cde", label="12-15 x bodySize")
        pts = [(a["bs"], a[key], a["defName"]) for a in animals if a["best_post"]]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=8, color="#555")
        outliers(ax, [(x, y / max(1, K_HI * x), l) for x, y, l in pts] and
                 [(x, y, l) for x, y, l in pts if y > max(1, K_HI * x) + 0.05 or y < max(1, K_LO * x) - 0.05])
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("bodySize"); ax.set_title("best hit, %s" % title)
    axes[0].set_ylabel("best tool power"); axes[0].legend(fontsize=8)
    fig.suptitle("Law 3 — damage vs bodySize (%s)" % src, fontsize=8)
    fig.savefig(os.path.join(PLOT_DIR, "law3_damage_vs_bodysize.png"), dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    pts = []
    for a in animals:
        dps = max([(t["power"] or 0) / (t["cooldown"] or 2.0) for t in a["tools_post"]], default=0)
        if dps:
            pts.append((a["bs"], dps, a["defName"]))
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=8, color="#555")
    bsr = sorted({p[0] for p in pts})
    ax.plot(bsr, [DPS_K * math.sqrt(b) for b in bsr], color="#c33", label="10 x sqrt(bodySize)")
    outliers(ax, [p for p in pts if p[1] > DPS_K * math.sqrt(p[0]) * 1.5])
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("bodySize"); ax.set_ylabel("best DPS (post)")
    ax.legend(fontsize=8); ax.set_title("DPS vs bodySize (%s)" % src, fontsize=8)
    fig.savefig(os.path.join(PLOT_DIR, "law3_dps_vs_bodysize.png"), dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 7))
    ms = [a for a in animals if "need" in a]
    ms.sort(key=lambda a: (a["env"][0] + a["env"][1]) / 2)
    for i, a in enumerate(ms):
        ax.plot([i, i], [a["comfy_pre"]["ComfyTemperatureMin"], a["comfy_pre"]["ComfyTemperatureMax"]], color="#bbb", lw=2)
        ax.plot([i, i], [a["comfy_post"]["ComfyTemperatureMin"], a["comfy_post"]["ComfyTemperatureMax"]], color="#36c", lw=0.8)
        ax.plot([i, i], [a["env"][0], a["env"][1]], color="#c33", lw=1.5)
    ax.set_xlabel("rostered animals, sorted by envelope midpoint (%d)" % len(ms)); ax.set_ylabel("deg C")
    ax.set_title("Law 5 — grey: comfy band before, blue: after, red: home envelope p05..p95 (%s)" % src, fontsize=8)
    fig.savefig(os.path.join(PLOT_DIR, "law5_tolerance_vs_envelope.png"), dpi=110); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, key, title in ((axes[0], "meat", "meat yield"), (axes[1], "leather", "leather yield")):
        pre, post = [], []
        for a in animals:
            r = a["row"]
            if not a["rostered"]:
                continue
            if key == "meat":
                v0 = fnum(r["meat"]) if r["meat"] else MEAT_BASE
                v1 = a["meat_post"]
                f = (lambda v, b: v * b)          # engine: base x bodySize
            else:
                v0 = fnum(r["leather"]) or 0
                v1 = a["leather_post"]
                f = (lambda v, b: v * b)
            pre.append((a["bs"], f(v0, a["bs"]), a["defName"]))
            post.append((a["bs"], f(v1, a["bs"]), a["defName"]))
        ax.scatter([p[0] for p in pre], [p[1] for p in pre], s=10, color="#bbb", label="before")
        ax.scatter([p[0] for p in post], [p[1] for p in post], s=6, color="#36c", label="after")
        ax.set_xscale("log"); ax.set_yscale("symlog"); ax.set_xlabel("bodySize"); ax.set_title(title + " (base x bodySize, before the engine's postProcessCurve)", fontsize=8)
        ax.legend(fontsize=8)
    fig.suptitle("Law 6 — products vs bodySize (%s)" % src, fontsize=8)
    fig.savefig(os.path.join(PLOT_DIR, "law6_products_vs_bodysize.png"), dpi=110); plt.close(fig)
    print("plot: 4 PNGs in %s" % PLOT_DIR)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("verb", choices=("snapshot", "generate", "check", "plot"))
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    a = ap.parse_args(argv)
    if a.verb == "snapshot":
        snapshot(a.config)
    elif a.verb == "generate":
        cmd_generate()
    elif a.verb == "check":
        return cmd_check()
    else:
        cmd_plot()
    return 0


if __name__ == "__main__":
    sys.exit(main())
