#!/usr/bin/env python3
"""Check a proposed or existing xenotype gene list against the LIVE gene set.

Answers the five questions you cannot answer by eye once several hundred mods
are loaded and 4800+ GeneDefs exist:

  1. does every defName resolve?
  2. do any two genes share an ``exclusionTags`` entry?  (the mechanical core --
     two such genes cannot coexist on one pawn)
  3. is every ``prerequisite`` present, transitively?
  4. what are the biostatCpx / biostatMet / biostatArc totals, and how do they
     sit against the gene-assembler caps?
  5. which installed xenotypes already carry a similar set?

Data source, in preference order:
  --source dump   the LIVE def dump (post-patch truth, every field, 4833 genes)
  --source scan   observed/genome/genes.json + xenotypes.json, as written by
                  genome_scan.py  (offline, no game run needed, fewer fields)

The dump is authoritative: it is what the running game actually built, after
every PatchOperation and after GeneTemplateDef expansion. genome_scan.py reads
XML and expands templates itself, so it agrees on defNames but carries a
narrower field set (no prerequisite, no endogeneCategory, no geneClass).

Usage
-----
  # check a proposed list
  xenotype_check.py check --genes Furskin,Robust,MinorAggression
  xenotype_check.py check --genes-file design/Jawa/proposed_genes.txt

  # check something already shipped (ours or a mod's)
  xenotype_check.py check --xenotype BTD_Jawa

  # go from a paragraph brief to candidate genes
  xenotype_check.py suggest "small heat-adapted scavengers, dark vision, poor fighters"

  # what carries this tag / what does this gene cost
  xenotype_check.py tag SkinColorOverride
  xenotype_check.py gene Furskin

  # the whole installed set, sorted by any biostat
  xenotype_check.py xenotypes --sort met | head -20

Exit code is 1 if any HARD failure is found (unknown defName, exclusion
collision, unmet prerequisite), 0 otherwise. Soft warnings never fail the run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parents[3]
SCAN_DIR = REPO / "observed" / "genome"

# The live def dump. game_paths.py knows the game install; the dump lives beside
# the config under LocalLow and is written by the def-dump mod at load.
DUMP_DIR = Path(
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
    "RimWorld by Ludeon Studios/DefDump/defs"
)

# --- the caps ---------------------------------------------------------------
# Vanilla Biotech gene assembler: base complexity 6, +2 per connected
# GeneProcessor (StatDef GeneticComplexityIncrease, value 2 on ThingDef
# GeneProcessor -- verified in the live dump, StatDef.json / ThingDef.json),
# max 3 processors -> 12. These bound what a PLAYER can assemble in the UI.
# An authored XenotypeDef is NOT validated against them; see
# skills/rimworld-xenotype/references/complexity-and-metabolism.md.
CPX_BASE = 6
CPX_PER_PROCESSOR = 2
CPX_MAX_PROCESSORS = 3
CPX_CAP_MAX = CPX_BASE + CPX_PER_PROCESSOR * CPX_MAX_PROCESSORS  # 12

# Metabolism -> hunger rate. Vanilla shows a discrete descriptor per band.
MET_BANDS = [
    (5, "hyper-efficient"),
    (3, "very efficient"),
    (1, "efficient"),
    (0, "normal"),
    (-2, "slightly hungry"),
    (-4, "hungry"),
    (-6, "very hungry"),
    (-99, "starving"),
]


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- loading


def _flat_dump(path: Path) -> dict[str, dict]:
    """Read one DefDump JSON into defName -> flattened record."""
    blob = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for d in blob.get("defs", []):
        rec = dict(d.get("fields") or {})
        rec["defName"] = d.get("defName")
        rec["modName"] = d.get("modName")
        rec["packageId"] = d.get("packageId")
        if rec["defName"]:
            out[rec["defName"]] = rec
    return out


def _as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _num(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default


def normalise_gene(rec: dict) -> dict:
    """One shape for a gene regardless of which source it came from."""
    return {
        "defName": rec.get("defName"),
        "label": rec.get("label") or rec.get("defName"),
        "description": rec.get("description") or "",
        "mod": rec.get("modName") or rec.get("mod") or "",
        "packageId": (rec.get("packageId") or "").lower(),
        "cpx": _num(rec.get("biostatCpx")),
        "met": _num(rec.get("biostatMet")),
        "arc": _num(rec.get("biostatArc")),
        "exclusionTags": [str(t) for t in _as_list(rec.get("exclusionTags"))],
        "prerequisite": rec.get("prerequisite") or None,
        "endogeneCategory": (rec.get("endogeneCategory") or "None"),
        "displayCategory": rec.get("displayCategory") or "",
        "geneClass": rec.get("geneClass") or "",
        "iconPath": rec.get("iconPath") or "",
        "generated": bool(rec.get("generated")),
        # the "would a player notice this" signals
        "statOffsets": _as_list(rec.get("statOffsets")),
        "statFactors": _as_list(rec.get("statFactors")),
        "capMods": _as_list(rec.get("capMods")),
        "abilities": _as_list(rec.get("abilities")),
        "forcedTraits": _as_list(rec.get("forcedTraits")),
        "suppressedTraits": _as_list(rec.get("suppressedTraits")),
        "disabledWorkTags": rec.get("disabledWorkTags") or "None",
        "skinColorOverride": rec.get("skinColorOverride"),
        "skinColorBase": rec.get("skinColorBase"),
        "hairColorOverride": rec.get("hairColorOverride"),
        "bodyType": rec.get("bodyType"),
        "renderNodeProperties": _as_list(rec.get("renderNodeProperties")),
        "forcedHeadTypes": _as_list(rec.get("forcedHeadTypes")),
        "fur": rec.get("fur"),
        "aptitudes": _as_list(rec.get("aptitudes")),
        "minAgeActive": _num(rec.get("minAgeActive")),
        "randomChosen": bool(rec.get("randomChosen")),
        "resourceGizmoType": rec.get("resourceGizmoType") or "",
        "customEffectDescriptions": _as_list(rec.get("customEffectDescriptions")),
    }


def normalise_xenotype(rec: dict) -> dict:
    genes = rec.get("genes")
    if isinstance(genes, dict):
        genes = list(genes)
    return {
        "defName": rec.get("defName"),
        "label": rec.get("label") or rec.get("defName"),
        "mod": rec.get("modName") or rec.get("mod") or "",
        "genes": [g if isinstance(g, str) else (g or {}).get("defName")
                  for g in _as_list(genes)],
        "inheritable": rec.get("inheritable"),
        "factionlessGenerationWeight": _num(
            rec.get("factionlessGenerationWeight"), 0),
        "combatPowerFactor": rec.get("combatPowerFactor"),
        "canGenerateAsCombatant": rec.get("canGenerateAsCombatant"),
        "displayPriority": rec.get("displayPriority"),
        "iconPath": rec.get("iconPath") or "",
        "nameMaker": rec.get("nameMaker"),
        "chanceToUseNameMaker": rec.get("chanceToUseNameMaker"),
        "description": rec.get("description") or "",
    }


def load(source: str) -> tuple[dict, dict, str]:
    """-> (genes, xenotypes, provenance string)."""
    if source == "auto":
        source = "dump" if (DUMP_DIR / "GeneDef.json").is_file() else "scan"

    if source == "dump":
        gp, xp = DUMP_DIR / "GeneDef.json", DUMP_DIR / "XenotypeDef.json"
        if not gp.is_file():
            sys.exit(f"no def dump at {DUMP_DIR} -- try --source scan")
        genes = {k: normalise_gene(v) for k, v in _flat_dump(gp).items()}
        xenos = {k: normalise_xenotype(v) for k, v in _flat_dump(xp).items()}
        prov = f"live def dump, {gp}"
    elif source == "scan":
        gp, xp = SCAN_DIR / "genes.json", SCAN_DIR / "xenotypes.json"
        if not gp.is_file():
            sys.exit(f"no scan output at {SCAN_DIR} -- run "
                     "`python3 src/RimMandrake/Utils/genome_scan.py` first")
        genes = {k: normalise_gene(v)
                 for k, v in json.loads(gp.read_text(encoding="utf-8")).items()}
        xenos = {k: normalise_xenotype(v)
                 for k, v in json.loads(xp.read_text(encoding="utf-8")).items()}
        prov = f"genome_scan.py output, {gp}"
    else:
        sys.exit(f"unknown source {source!r}")

    # Key by defName, not by the file's key (genome_scan keys abstract defs by
    # their Name attribute).
    genes = {g["defName"]: g for g in genes.values() if g.get("defName")}
    xenos = {x["defName"]: x for x in xenos.values() if x.get("defName")}
    return genes, xenos, prov


# ---------------------------------------------------------------- the checks


def met_band(total: int) -> str:
    for threshold, name in MET_BANDS:
        if total >= threshold:
            return name
    return MET_BANDS[-1][1]


def noticeable(g: dict) -> tuple[bool, str]:
    """Would a player SEE this gene in a campaign, or is it a hidden number?

    'Visible' = changes what the pawn looks like, gives a gizmo/ability, forces
    or removes a trait, or disables work. Everything else is a stat nudge the
    player reads once on the gene tab and never again.
    """
    if g["abilities"]:
        return True, "ability"
    if g["resourceGizmoType"] and g["resourceGizmoType"] != "RimWorld.GeneGizmo_Resource":
        return True, "resource gizmo"
    if g["forcedTraits"] or g["suppressedTraits"]:
        return True, "trait"
    if g["disabledWorkTags"] not in ("None", None, ""):
        return True, "disables work"
    if (g["skinColorOverride"] or g["skinColorBase"] or g["hairColorOverride"]
            or g["bodyType"] or g["renderNodeProperties"] or g["forcedHeadTypes"]
            or g["fur"]):
        return True, "visual"
    if g["capMods"]:
        return True, "capacity"
    if g["aptitudes"]:
        return True, "skill"
    return False, "stat offset only"


def check(gene_names: list[str], genes: dict, xenos: dict,
          cpx_cap: int = CPX_CAP_MAX) -> dict:
    r: dict = {"input": gene_names, "hard": [], "soft": [], "info": {}}

    # -- 0. duplicates
    dupes = [n for n, c in Counter(gene_names).items() if c > 1]
    if dupes:
        r["soft"].append(("duplicate", f"listed more than once: {', '.join(dupes)}"))
    uniq = list(dict.fromkeys(gene_names))

    # -- 1. unknown defNames
    unknown = [n for n in uniq if n not in genes]
    for n in unknown:
        near = [k for k in genes if k.lower() == n.lower()]
        if not near:
            near = [k for k in genes if n.lower() in k.lower()][:4]
        hint = f"  did you mean: {', '.join(near)}" if near else ""
        r["hard"].append(("unknown", f"{n} is not a loaded GeneDef.{hint}"))
    known = [genes[n] for n in uniq if n in genes]

    # -- 2. exclusionTags collisions  (THE mechanical core)
    by_tag: dict[str, list[str]] = defaultdict(list)
    for g in known:
        for t in g["exclusionTags"]:
            by_tag[t].append(g["defName"])
    for tag, members in sorted(by_tag.items()):
        if len(members) > 1:
            labels = ", ".join(f"{m} ({genes[m]['label']})" for m in members)
            r["hard"].append(
                ("exclusion", f"tag '{tag}' is carried by {len(members)} genes "
                              f"-- they cannot coexist: {labels}"))

    # -- 3. prerequisites, transitively
    have = {g["defName"] for g in known}
    for g in known:
        seen, cur = set(), g["prerequisite"]
        while cur and cur not in seen:
            seen.add(cur)
            if cur not in have:
                where = "not a loaded GeneDef" if cur not in genes else "not in this list"
                r["hard"].append(
                    ("prerequisite",
                     f"{g['defName']} requires {cur}, which is {where}"))
                break
            cur = genes[cur]["prerequisite"]

    # -- 4. endogeneCategory doubling (soft: the game picks one at birth)
    by_endo: dict[str, list[str]] = defaultdict(list)
    for g in known:
        if g["endogeneCategory"] not in ("None", None, ""):
            by_endo[g["endogeneCategory"]].append(g["defName"])
    for cat, members in sorted(by_endo.items()):
        if len(members) > 1:
            r["soft"].append(
                ("endogene", f"{len(members)} genes share endogeneCategory "
                             f"'{cat}': {', '.join(members)} -- inheritance "
                             "assigns one slot per category"))

    # -- 5. biostats
    cpx = sum(g["cpx"] for g in known)
    met = sum(g["met"] for g in known)
    arc = sum(g["arc"] for g in known)
    r["info"]["biostats"] = {"cpx": cpx, "met": met, "arc": arc,
                             "metBand": met_band(met), "cpxCap": cpx_cap}
    if cpx > cpx_cap:
        r["soft"].append(
            ("complexity",
             f"complexity {cpx} exceeds the gene assembler ceiling of {cpx_cap} "
             f"(base {CPX_BASE} + {CPX_PER_PROCESSOR} x {CPX_MAX_PROCESSORS} "
             "processors). An authored XenotypeDef is NOT blocked by this -- "
             "but the player can never REBUILD this xenotype in the assembler."))
    if arc:
        r["soft"].append(
            ("archite", f"{arc} archite capsule(s) required to assemble; "
                        "archite genes are late-game and quest-gated"))
    if met < 0:
        r["soft"].append(
            ("metabolism",
             f"metabolic efficiency {met} -> '{met_band(met)}'. Pawns eat more; "
             "below about -4 they spend a visible fraction of the day eating."))

    # -- 6. modded genes: MayRequire discipline
    mods: dict[str, list[str]] = defaultdict(list)
    for g in known:
        pid = g["packageId"] or g["mod"]
        if pid and not str(pid).startswith("ludeon.rimworld"):
            mods[str(pid)].append(g["defName"])
    if mods:
        r["info"]["mayRequire"] = {k: sorted(v) for k, v in sorted(mods.items())}
        r["soft"].append(
            ("mayrequire",
             f"{sum(len(v) for v in mods.values())} genes come from "
             f"{len(mods)} non-Ludeon mod(s); each <li> needs MayRequire or the "
             "whole XenotypeDef fails to load when that mod is absent"))

    # -- 7. what will the player actually notice
    vis = [(g["defName"], why) for g in known for ok, why in [noticeable(g)] if ok]
    hidden = [g["defName"] for g in known for ok, _ in [noticeable(g)] if not ok]
    r["info"]["noticeable"] = vis
    r["info"]["hidden"] = hidden

    # -- 8. neighbours in the installed set
    myset = set(have)
    sims = []
    for x in xenos.values():
        other = set(x["genes"])
        if not other:
            continue
        j = len(myset & other) / len(myset | other)
        if j > 0:
            sims.append((round(j, 3), x["defName"], x["mod"], len(other),
                         sorted(myset & other)))
    sims.sort(reverse=True)
    r["info"]["similar"] = sims[:8]

    return r


def print_report(r: dict, genes: dict, prov: str) -> None:
    b = r["info"]["biostats"]
    n = len(set(r["input"]))
    print(f"source: {prov}")
    print(f"genes in list: {n}")
    print(f"biostats: cpx {b['cpx']} (assembler ceiling {b['cpxCap']})  "
          f"met {b['met']} ({b['metBand']})  arc {b['arc']}")
    print()

    if r["hard"]:
        print(f"FAIL -- {len(r['hard'])} hard problem(s):")
        for kind, msg in r["hard"]:
            print(f"  [{kind}] {msg}")
    else:
        print("PASS -- no unknown defName, no exclusionTags collision, "
              "every prerequisite met.")
    print()

    if r["soft"]:
        print(f"{len(r['soft'])} warning(s):")
        for kind, msg in r["soft"]:
            print(f"  [{kind}] {msg}")
        print()

    vis, hid = r["info"]["noticeable"], r["info"]["hidden"]
    tot = len(vis) + len(hid)
    if tot:
        print(f"visible in play: {len(vis)}/{tot} "
              f"({100 * len(vis) // tot}%)")
        for dn, why in vis:
            print(f"  + {dn:<32} {why}")
        if hid:
            print(f"  - hidden stat offsets only: {', '.join(hid)}")
        print()

    if r["info"]["similar"]:
        print("closest installed xenotypes (Jaccard on gene sets):")
        for j, dn, mod, cnt, shared in r["info"]["similar"]:
            print(f"  {j:>5}  {dn:<28} {cnt:>3} genes  [{mod}]")
            print(f"         shares: {', '.join(shared[:10])}"
                  + (" ..." if len(shared) > 10 else ""))


# ---------------------------------------------------------------- suggest


STOP = set("""a an and are as at be but by can cannot for from have has in into is it
its no not of on or that the their they this to who with without you your are
very who's small large big who see who can't dont don't""".split())


def suggest(brief: str, genes: dict, limit: int) -> None:
    """Prose -> candidate genes, ranked by term hits in label/description.

    Deliberately dumb: this is a CANDIDATE GENERATOR, not a designer. It exists
    so you argue with a shortlist instead of scrolling 4833 defs. Read every hit
    before you keep it.
    """
    terms = [w for w in re.findall(r"[a-z]+", brief.lower())
             if len(w) > 2 and w not in STOP]
    if not terms:
        sys.exit("nothing searchable in that brief")
    scored = []
    for g in genes.values():
        hay = f"{g['label']} {g['description']} {g['displayCategory']}".lower()
        hits = [t for t in terms if t in hay]
        if not hits:
            continue
        # label hits are worth more than description hits
        score = sum(3 if t in g["label"].lower() else 1 for t in hits)
        scored.append((score, len(set(hits)), g, sorted(set(hits))))
    scored.sort(key=lambda s: (-s[0], -s[1], s[2]["defName"]))
    print(f"terms: {', '.join(terms)}")
    print(f"{len(scored)} genes matched; top {limit}:")
    print()
    for score, _, g, hits in scored[:limit]:
        tags = ",".join(g["exclusionTags"]) or "-"
        print(f"{g['defName']:<34} cpx{g['cpx']:>3} met{g['met']:>3} "
              f"arc{g['arc']:>2}  excl:{tags:<26} [{g['mod']}]")
        print(f"    {g['label']} -- matched {', '.join(hits)}")


# ---------------------------------------------------------------- main


def resolve_gene_names(args, xenos: dict) -> list[str]:
    if args.xenotype:
        if args.xenotype not in xenos:
            sys.exit(f"{args.xenotype} is not a loaded XenotypeDef")
        return list(xenos[args.xenotype]["genes"])
    if args.genes_file:
        raw = Path(args.genes_file).read_text(encoding="utf-8")
        return [ln.split("#")[0].strip().lstrip("-").strip()
                for ln in raw.splitlines()
                if ln.split("#")[0].strip()]
    if args.genes:
        return [g.strip() for g in args.genes.replace("\n", ",").split(",")
                if g.strip()]
    sys.exit("give one of --genes, --genes-file, --xenotype")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="auto", choices=("auto", "dump", "scan"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="validate a gene list")
    c.add_argument("--genes")
    c.add_argument("--genes-file")
    c.add_argument("--xenotype")
    c.add_argument("--cpx-cap", type=int, default=CPX_CAP_MAX)
    c.add_argument("--json", action="store_true")

    s = sub.add_parser("suggest", help="prose brief -> candidate genes")
    s.add_argument("brief", nargs="+")
    s.add_argument("--limit", type=int, default=30)

    t = sub.add_parser("tag", help="who carries this exclusionTag")
    t.add_argument("tag")

    g = sub.add_parser("gene", help="dump one gene's authoring-relevant fields")
    g.add_argument("defName")

    x = sub.add_parser("xenotypes", help="every installed xenotype, totalled")
    x.add_argument("--sort", default="cpx",
                   choices=("cpx", "met", "arc", "genes", "name"))
    x.add_argument("--mod", help="substring filter on mod name")

    args = ap.parse_args()
    genes, xenos, prov = load(args.source)

    if args.cmd == "check":
        names = resolve_gene_names(args, xenos)
        r = check(names, genes, xenos, args.cpx_cap)
        if args.json:
            print(json.dumps(r, indent=1))
        else:
            print_report(r, genes, prov)
        return 1 if r["hard"] else 0

    if args.cmd == "suggest":
        suggest(" ".join(args.brief), genes, args.limit)
        return 0

    if args.cmd == "tag":
        members = [g for g in genes.values() if args.tag in g["exclusionTags"]]
        if not members:
            near = sorted({t for g in genes.values() for t in g["exclusionTags"]
                           if args.tag.lower() in t.lower()})
            print(f"no gene carries '{args.tag}'."
                  + (f" similar tags: {', '.join(near[:20])}" if near else ""))
            return 0
        print(f"{len(members)} genes carry exclusionTag '{args.tag}' "
              "-- at most ONE may be on a pawn:")
        for g in sorted(members, key=lambda g: g["defName"]):
            print(f"  {g['defName']:<34} cpx{g['cpx']:>3} met{g['met']:>3} "
                  f"{g['label']:<26} [{g['mod']}]")
        return 0

    if args.cmd == "gene":
        g = genes.get(args.defName)
        if not g:
            near = [k for k in genes if args.defName.lower() in k.lower()][:15]
            print(f"{args.defName} not loaded."
                  + (f" close: {', '.join(near)}" if near else ""))
            return 1
        vis, why = noticeable(g)
        drop = ("description", "renderNodeProperties")
        for k, v in g.items():
            if k in drop or v in (None, "", [], 0, False, "None"):
                continue
            print(f"{k:<24} {json.dumps(v) if not isinstance(v, str) else v}")
        print(f"{'visibleInPlay':<24} {vis} ({why})")
        print(f"{'description':<24} {g['description'][:400]}")
        return 0

    if args.cmd == "xenotypes":
        rows = []
        for x in xenos.values():
            if args.mod and args.mod.lower() not in x["mod"].lower():
                continue
            known = [genes[n] for n in x["genes"] if n in genes]
            miss = [n for n in x["genes"] if n not in genes]
            rows.append((x["defName"], x["mod"], len(x["genes"]),
                         sum(g["cpx"] for g in known),
                         sum(g["met"] for g in known),
                         sum(g["arc"] for g in known), len(miss)))
        key = {"cpx": 3, "met": 4, "arc": 5, "genes": 2, "name": 0}[args.sort]
        rows.sort(key=lambda r: r[key], reverse=args.sort != "name")
        print(f"{'defName':<34}{'genes':>6}{'cpx':>5}{'met':>5}{'arc':>4}"
              f"{'miss':>6}  mod")
        for dn, mod, n, cpx, met, arc, miss in rows:
            print(f"{dn:<34}{n:>6}{cpx:>5}{met:>5}{arc:>4}{miss:>6}  {mod}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
