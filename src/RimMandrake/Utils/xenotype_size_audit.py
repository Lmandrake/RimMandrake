#!/usr/bin/env python3
"""Which xenotypes are already big, and which could feasibly be made big.

Written for ``BIG_WEAPON_XENOTYPE_AUDIT_1``.  The owner asked which of the 139
installed xenotypes could feasibly carry a "big & tall" gene so they could wield
giant / warcasket weapons.  Before any shortlist means anything, two things have
to be MEASURED rather than assumed:

  1. which genes actually change a pawn's MECHANICAL body size, as opposed to
     merely scaling its sprite;
  2. which xenotypes already carry one, and how big they already are.

The cosmetic / mechanical split is not a judgement call -- Big and Small and
Vanilla Expanded Framework each ship BOTH, under names one letter apart:

    MECHANICAL   SM_BodySizeOffset      SM_BodySizeMultiplier
                 VEF_BodySize_Offset    VEF_BodySize_Multiplier
    COSMETIC     SM_Cosmetic_BodySizeOffset   SM_Cosmetic_BodySizeMultiplier
                 VEF_CosmeticBodySize_Offset  VEF_CosmeticBodySize_Multiplier
                 SM_HeadSize_Cosmetic         VEF_HeadSize_Cosmetic

A gene carrying only the Cosmetic stats makes the pawn LOOK bigger and changes
nothing else -- not its health scale, not its carrying capacity, not anything a
weapon check could read.  Matching on the substring "BodySize" anywhere in a
gene returns ~542 defs and is almost entirely that render scaling; this script
matches on the exact stat defName instead.

Two further mechanical routes exist and are counted:

    modExtensions GeneDefExtension_Pawn.bodySizeFactor   (a plain multiplier)
    modExtensions GeneExtension.sizeByAge                (an offset from an age)

``sizeByAgeMult`` is deliberately NOT counted.  It is Big and Small's early- and
late-maturity curve: it changes how fast a pawn reaches its adult size, not what
that adult size is.  ``BS_EarlyMaturity`` on ``MandrakeJawa`` is that gene, and
counting it would report the player xenotype as carrying a size gene when it
does not.

Data source is the live def dump's sqlite, opened READ-ONLY.  It is what the
running game actually built -- post-patch, post-inheritance, post-dedup.

Usage
-----
    xenotype_size_audit.py genes        the mechanical size genes, with values
    xenotype_size_audit.py xenotypes    all 139, each with its measured size
    xenotype_size_audit.py report       the markdown report the owner reads
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import DEF_DUMP  # noqa: E402
import dump_projection  # noqa: E402

# 🔴 The db is at the DefDump ROOT, not inside the capture — it is derived, so
# pruning a capture must never cost it. `DEF_DUMP` is the CAPTURE under the dated
# layout, so resolving this by hand breaks the day the dump is migrated. It did,
# on 2026-08-22. `sqlite_path` knows both layouts.
SQLITE = Path(dump_projection.sqlite_path(str(DEF_DUMP)) or (Path(DEF_DUMP) / "defs.sqlite"))

# Exact stat defNames.  Anything not on one of these two lists is not a size
# stat at all, whatever its name suggests.
MECHANICAL_STATS = {
    "SM_BodySizeOffset": "offset",
    "SM_BodySizeMultiplier": "factor",
    "VEF_BodySize_Offset": "offset",
    "VEF_BodySize_Multiplier": "factor",
}
COSMETIC_STATS = {
    "SM_Cosmetic_BodySizeOffset",
    "SM_Cosmetic_BodySizeMultiplier",
    "VEF_CosmeticBodySize_Offset",
    "VEF_CosmeticBodySize_Multiplier",
    "SM_HeadSize_Cosmetic",
    "VEF_HeadSize_Cosmetic",
}

# A human pawn is bodySize 1.0.  These are the thresholds the report groups on;
# they are ours, not the engine's -- nothing in RimWorld reads them.
BIG_ENOUGH = 0.4  # +0.4 is BS_LargeFrame, the smallest gene anyone would call "big"


def _connect() -> sqlite3.Connection:
    if not SQLITE.is_file():
        sys.exit(f"no def dump sqlite at {SQLITE} -- run refresh.py, or the DefDumper")
    return sqlite3.connect(f"file:{SQLITE}?mode=ro", uri=True)


def _stat_mods(value) -> list[tuple[str, float]]:
    """Pull (stat, value) out of a serialised statOffsets / statFactors block.

    The dump writes these as a LIST of StatModifier objects
    ``[{"$type": "StatModifier", "stat": "X", "value": 0.4}]`` -- not as the
    map the XML looks like.  Older captures used a list of single-key objects,
    so both shapes are read.
    """
    out: list[tuple[str, float]] = []
    if isinstance(value, dict):
        for key, val in value.items():
            if key != "$type":
                out.append((key, val))
    elif isinstance(value, list):
        for entry in value:
            if not isinstance(entry, dict):
                continue
            if "stat" in entry:
                out.append((entry["stat"], entry.get("value")))
            else:
                for key, val in entry.items():
                    if key != "$type":
                        out.append((key, val))
    return out


def _mod_extensions(fields: dict) -> list[dict]:
    ext = fields.get("modExtensions") or []
    if isinstance(ext, dict):
        ext = [ext]
    return [e for e in ext if isinstance(e, dict)]


def size_genes(conn: sqlite3.Connection) -> dict[str, dict]:
    """Every gene that changes mechanical body size, keyed by defName."""
    found: dict[str, dict] = {}
    for def_name, mod_name, label, blob in conn.execute(
        "select def_name, mod_name, label, json from defs where def_type='GeneDef'"
    ):
        fields = json.loads(blob).get("fields", {})
        effects = []
        for block in ("statOffsets", "statFactors"):
            for stat, val in _stat_mods(fields.get(block)):
                if stat in MECHANICAL_STATS:
                    effects.append((MECHANICAL_STATS[stat], stat, val))
        for ext in _mod_extensions(fields):
            factor = ext.get("bodySizeFactor")
            if factor not in (None, 1):
                effects.append(("factor", "modExt bodySizeFactor", factor))
            by_age = ext.get("sizeByAge")
            if isinstance(by_age, dict) and by_age.get("$type") == "SizeByAge":
                # minOffset/maxOffset are the offset at the low/high end of the
                # age range; an adult pawn gets maxOffset.
                effects.append(("offset", "modExt sizeByAge", by_age.get("maxOffset")))
            elif isinstance(by_age, list) and by_age:
                # A curve of CurvePoints. The dump serialises the points as bare
                # {"$type": "CurvePoint"} with the x/y stripped, so the final size
                # is UNMEASURABLE from the dump -- record the gene, not a number.
                effects.append(("curve", "modExt sizeByAge curve", None))
        if effects:
            found[def_name] = {
                "mod": mod_name,
                "label": label,
                "effects": effects,
                "net": _net(effects),
            }
    return found


def cosmetic_only_genes(conn: sqlite3.Connection, mechanical: set[str]) -> dict[str, dict]:
    """Genes that scale the sprite and nothing else. Named so they are not mistaken."""
    found: dict[str, dict] = {}
    for def_name, mod_name, label, blob in conn.execute(
        "select def_name, mod_name, label, json from defs where def_type='GeneDef'"
    ):
        if def_name in mechanical:
            continue
        fields = json.loads(blob).get("fields", {})
        hits = []
        for block in ("statOffsets", "statFactors"):
            for stat, val in _stat_mods(fields.get(block)):
                if stat in COSMETIC_STATS:
                    hits.append((stat, val))
        if hits:
            found[def_name] = {"mod": mod_name, "label": label, "effects": hits}
    return found


def _net(effects) -> float:
    """Approximate adult bodySize starting from a human's 1.0.

    Offsets add, factors multiply.  This is the game's own order for these two
    stats and it is only ever indicative -- a real pawn's size also depends on
    its race's base and its life stage.
    """
    size = 1.0
    for kind, _stat, val in effects:
        if val is None:
            continue
        if kind == "offset":
            size += float(val)
        else:
            size *= float(val)
    return round(size, 3)


def xenotypes(conn: sqlite3.Connection, genes: dict[str, dict],
              cosmetic: dict[str, dict]) -> list[dict]:
    rows = []
    for def_name, label, mod_name, blob in conn.execute(
        "select def_name, label, mod_name, json from defs "
        "where def_type='XenotypeDef' order by mod_name, def_name"
    ):
        fields = json.loads(blob).get("fields", {})
        gene_list = fields.get("genes") or []
        mech = [g for g in gene_list if g in genes]
        cosm = [g for g in cosmetic if g in gene_list]
        effects = [e for g in mech for e in genes[g]["effects"]]
        rows.append({
            "defName": def_name,
            "label": label or def_name,
            "mod": mod_name,
            "genes": len(gene_list),
            "sizeGenes": mech,
            "cosmeticGenes": cosm,
            "size": _net(effects) if effects else 1.0,
            "description": (fields.get("descriptionShort")
                            or fields.get("description") or "").strip(),
        })
    return rows


def cmd_genes(args) -> None:
    conn = _connect()
    genes = size_genes(conn)
    total = conn.execute(
        "select count(*) from defs where def_type='GeneDef'").fetchone()[0]
    print(f"MEASURED {len(genes)} GeneDefs change mechanical body size (of {total})")
    for name, info in sorted(genes.items(), key=lambda kv: -kv[1]["net"]):
        eff = ", ".join(f"{s}={v}" for _k, s, v in info["effects"])
        print(f"  {info['net']:>6}  {name:<34} {info['mod'][:34]:<34} {eff}")
    if args.cosmetic:
        cosm = cosmetic_only_genes(conn, set(genes))
        print(f"\nCOSMETIC ONLY -- {len(cosm)} genes scale the sprite and nothing else:")
        for name, info in sorted(cosm.items()):
            print(f"  {name:<34} {info['mod'][:34]:<34} "
                  + ", ".join(f"{s}={v}" for s, v in info["effects"]))


def cmd_xenotypes(args) -> None:
    conn = _connect()
    genes = size_genes(conn)
    cosm = cosmetic_only_genes(conn, set(genes))
    rows = xenotypes(conn, genes, cosm)
    print(f"MEASURED {len(rows)} XenotypeDefs")
    for row in rows:
        flag = "BIG " if row["size"] >= 1 + BIG_ENOUGH else "    "
        note = ",".join(row["sizeGenes"]) or ("cosmetic:" + ",".join(row["cosmeticGenes"])
                                              if row["cosmeticGenes"] else "-")
        print(f"  {flag}{row['size']:>5}  {row['defName']:<32} {row['mod'][:30]:<30} {note}")


# --------------------------------------------------------------------------
# The feasibility verdicts.
#
# 🔑 These are judgements about the FICTION, not about the numbers.  The owner
# asked which species could feasibly be big and tall; a Jawa is canonically
# small and is not a candidate whatever a stat says.  Every verdict here is a
# RECOMMENDATION for the owner to rule on -- nothing in this file applies
# anything.
#
# Only species we actually field are judged.  A third-party xenotype we do not
# put on the map is NOT OURS: out of scope unless the owner says otherwise.
# --------------------------------------------------------------------------

STRONG = "STRONG"        # canonically large AND built to fight
PLAUSIBLE = "PLAUSIBLE"  # arguably large; the owner could go either way
TALL = "TALL NOT BIG"    # tall but slight -- a giant frame would read wrong
HUMAN = "HUMAN SCALE"    # no reason in the fiction to be bigger
NEVER = "NEVER"          # canonically small; must not be a candidate
SPECIAL = "SPECIAL"      # big, but a giant weapon still reads wrong
ALREADY = "ALREADY BIG"  # carries a mechanical size gene already
SMALLER = "ALREADY SMALL"
FOREIGN = "NOT OURS"

VERDICTS = {
    # ---- strong candidates -------------------------------------------------
    "RimMandrakeWookiee": (STRONG, "2.1 m and the galaxy's byword for strength; the single most obvious candidate"),
    "RimMandrakeGamorrean": (STRONG, "the def's own text says 'tall, strong bipeds'; porcine brutes hired as muscle"),
    "Jawa_Xeno_Gamorrean": (STRONG, "our own Gamorrean variant -- same call as RimMandrakeGamorrean, and it already carries the cosmetic big gene"),
    "RimMandrakeHerglic": (STRONG, "the def calls them 'hulking' and says they 'hit like a wrecking ball'"),
    "RimMandrakeTrandoshan": (STRONG, "2 m reptilian trophy hunters; large and built for violence"),
    "RimMandrakeTogorian": (STRONG, "the def's own text: 'large, feline beings'"),
    "RimMandrakeLasat": (STRONG, "over 2 m and famously powerful in melee"),
    "RimMandrakeFeeorin": (STRONG, "tall, heavily muscled and long-lived; grows stronger with age"),
    "RimMandrakeSithMassassi": (STRONG, "the Sith war caste -- bred tall and heavily muscled for exactly this"),
    # ---- plausible ---------------------------------------------------------
    "RimMandrakeKlatoonian": (PLAUSIBLE, "the def's own text: 'possessed a strong build, which made them useful laborers'"),
    "RimMandrakeAqualish": (PLAUSIBLE, "burly and thickset; frequently cast as heavies"),
    "RimMandrakeCathar": (PLAUSIBLE, "large athletic felinoids, though closer to human height than to a giant"),
    "RimMandrakeKaleesh": (PLAUSIBLE, "formidable warriors, but canonically near human height -- the fighting is the argument, not the size"),
    "RimMandrakeChagrian": (PLAUSIBLE, "tall and solidly built, though not warriors by disposition"),
    "RimMandrakeNelvaanian": (PLAUSIBLE, "lupine and powerfully built; a defensible large frame"),
    "RimMandrakeGungan": (PLAUSIBLE, "tall amphibians, but rangy rather than heavy"),
    # ---- tall, not big -----------------------------------------------------
    "RimMandrakeKaminoan": (TALL, "2.3 m and famously frail -- tall is not big, and a giant weapon on one would read as a joke"),
    "RimMandrakeMuun": (TALL, "the def says it: 'tall thin humanoids'. Bankers."),
    "RimMandrakeCerean": (TALL, "the height is in the cranium; the body is ordinary"),
    "RimMandrakePyke": (TALL, "tall and spindly criminal caste"),
    "RimMandrakeNagai": (TALL, "the def says 'tall and agile' -- agility is the point, mass is not"),
    "RimMandrakeIthorian": (TALL, "tall, but gentle herbivore pacifists; arming one with an ogre club is against the species"),
    "RimMandrakeKelDor": (TALL, "slight build under the mask"),
    # ---- special -----------------------------------------------------------
    "RimMandrakeHutt": (SPECIAL, "canonically the largest species we field by a wide margin, so a size gene is RIGHT -- but a Hutt is a sessile slug with vestigial arms and could not swing a giant hammer. Size yes, giant weapons no."),
    # ---- never -------------------------------------------------------------
    "MandrakeJawa": (NEVER, "the player xenotype, and canonically ~1 m. Never a candidate."),
    "RimMandrakeJawa": (NEVER, "canonically ~1 m"),
    "RimMandrakeEwok": (NEVER, "the def's own text: 'small primitive species', 'diminutive size'"),
    "RimMandrakeChadraFan": (NEVER, "the def's own text: 'meter-tall, rodent-like humanoids'"),
    "RimMandrakeUgnaught": (NEVER, "canonically short and stocky labourers"),
    "RimMandrakeYoderForceGremlin": (NEVER, "the Yoda species; tiny by definition"),
    "RimMandrakeSullustan": (NEVER, "short"),
    "RimMandrakeBothan": (NEVER, "short and slight"),
    "RimMandrakeDefel": (NEVER, "small shadow-dwellers"),
    "RimMandrakeGand": (NEVER, "small insectoids"),
    "RimMandrakeGeonosianVariants": (NEVER, "slight winged insectoids"),
    "RimMandrakeSnivvian": (NEVER, "short"),
    "RimMandrakeSelkath": (NEVER, "modest build"),
    "RimMandrakeOrtolan": (NEVER, "the def's own text: 'squat, blue-skinned bipeds'"),
}

# Everything else of ours is human scale.  Named so the table is complete and so
# a future reader can see the default was a decision, not an omission.
OURS_PREFIXES = ("RimMandrake", "MandrakeJawa", "Jawa_", "guy762_")


def verdict_for(row: dict) -> tuple[str, str]:
    name = row["defName"]
    if name in VERDICTS:
        return VERDICTS[name]
    if row["size"] >= 1 + BIG_ENOUGH:
        return ALREADY, f"already bodySize {row['size']} via {', '.join(row['sizeGenes'])}"
    if row["size"] < 1:
        return SMALLER, f"already bodySize {row['size']} via {', '.join(row['sizeGenes'])}"
    if name.startswith(OURS_PREFIXES):
        if name == "guy762_debugxenotype_droid":
            return FOREIGN, "a debug def from a resource mod; not a species we field"
        return HUMAN, "near-human build in the fiction; no reason to be larger"
    return FOREIGN, "a third-party xenotype we do not field; out of scope unless the owner says otherwise"


def cmd_shortlist(args) -> None:
    conn = _connect()
    genes = size_genes(conn)
    cosm = cosmetic_only_genes(conn, set(genes))
    rows = xenotypes(conn, genes, cosm)
    order = {v: i for i, v in enumerate(
        [STRONG, PLAUSIBLE, SPECIAL, TALL, ALREADY, HUMAN, NEVER, SMALLER, FOREIGN])}
    for row in rows:
        row["verdict"], row["why"] = verdict_for(row)
    rows.sort(key=lambda r: (order[r["verdict"]], -r["size"], r["defName"]))
    if args.markdown:
        print("| xenotype | mod | size now | verdict | why |")
        print("|---|---|---:|---|---|")
        for row in rows:
            print(f"| `{row['defName']}` | {row['mod']} | {row['size']} | "
                  f"**{row['verdict']}** | {row['why']} |")
    else:
        for row in rows:
            print(f"{row['verdict']:<14} {row['size']:>5}  {row['defName']:<32} {row['why']}")
    counts = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    total = sum(counts.values())
    print(f"\n{total} xenotypes, each judged once: "
          + ", ".join(f"{v} {k}" for k, v in sorted(counts.items(), key=lambda kv: order[kv[0]])))


def cmd_report(args) -> None:
    conn = _connect()
    genes = size_genes(conn)
    cosm = cosmetic_only_genes(conn, set(genes))
    rows = xenotypes(conn, genes, cosm)
    cap = dict(conn.execute("select key, value from provenance"))
    already = [r for r in rows if r["size"] >= 1 + BIG_ENOUGH]
    print(f"# Xenotype size audit\n")
    print(f"Source: `{SQLITE}` — mods={cap.get('mod_count', '?')}"
          f"/{cap.get('modlist_fingerprint', '?')} "
          f"game={cap.get('game_version', '?')} "
          f"captured={cap.get('captured_utc', '?')}\n")
    print(f"- {len(genes)} genes change mechanical body size.")
    print(f"- {len(cosm)} more change only the sprite and must not be confused with them.")
    print(f"- {len(already)} of {len(rows)} xenotypes are already at or above "
          f"bodySize {1 + BIG_ENOUGH}.\n")
    print("| xenotype | mod | size | size genes |")
    print("|---|---|---:|---|")
    for row in sorted(rows, key=lambda r: -r["size"]):
        print(f"| `{row['defName']}` | {row['mod']} | {row['size']} | "
              f"{', '.join(f'`{g}`' for g in row['sizeGenes']) or '—'} |")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("genes", help="the mechanical size genes, with values")
    p.add_argument("--cosmetic", action="store_true",
                   help="also list the sprite-only genes, so they can be ruled out by name")
    p.set_defaults(func=cmd_genes)
    p = sub.add_parser("xenotypes", help="all installed xenotypes with measured size")
    p.set_defaults(func=cmd_xenotypes)
    p = sub.add_parser("shortlist",
                       help="every xenotype with a feasibility verdict, judged on the fiction")
    p.add_argument("--markdown", action="store_true", help="emit the report table")
    p.set_defaults(func=cmd_shortlist)
    p = sub.add_parser("report", help="the markdown report")
    p.set_defaults(func=cmd_report)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
