#!/usr/bin/env python3
"""MINERALS_WHERE_THEY_BELONG_1 wave R1: the mineral registry generator.

Source of truth: design/RimMandrake/mineral_abundance_registry_2026-10-03.csv (design doc
mineral_abundance_registry_design_2026-10-03.md §5-§8). This tool reads its `bindings` column:

    bindings := group (" | " group)*        one group = one emitted material (merged reading rows split here)
    group    := token (" " token)*
    token    := role ":" name
    role     := id        stable material_id (default: the row's material, slugged; required when >1 group)
              | item      the resource ThingDef the material IS (deep drill, quarry, salvage draw this)
              | mineable  a mineable building the registry places by vein scatter (§6.3)
              | producer  any other placer the registry governs (crystal, seam, spawner, wall) - placed by its own GenStep
              | zero      a donor producer the registry disables (string; a missing donor mod is harmless)
              | retire    a donor ITEM the registry suppresses (never drilled; conversion later)

An empty bindings cell = nothing exists to bind yet (PROMISED/unbuilt row).

What it does:
  check (default)     validate the CSV (mineral_registry_check.check) and the bindings; resolve every bound defName
                      against the def dump (defs.sqlite) and the repo's own XML; coverage check: every resource
                      mineable and every deep-drillable item in the dump must be bound by some row (§8).
  --write-deep        regenerate src/RimMandrake/DeepDrill/Defs/RM_DeepHomeTable.xml (DEEP_DRILL_HOME_BIOME_1)
                      from the CSV. Dump-free and deterministic: every item/retire def except Steel; homes = the
                      biome columns whose cell is >0 or deep-only, when the row's deep_weight > 0; else none.
  --registry-out P    emit RM_MineralRegistryDef XML (one def per material group) for rows whose status is
                      RULED/BUILT and whose every item/mineable/producer resolves. The def class lives in the
                      planned mandrake.rm.minerals mod (wave R2); until it exists this output is a staged artifact.

Numbers in the CSV are PROVISIONAL agent guesses until a biome sitting rules them.
Usage: gen_mineral_registry.py [--csv P] [--dump P] [--write-deep] [--registry-out P] [--no-dump]
       gen_mineral_registry.py --selftest
Exit 1 on a hard defect."""
import csv, glob, os, re, sqlite3, sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import mineral_registry_check as mrc  # noqa: E402

CSV = mrc.CSV
DEEP_TABLE = os.path.join(ROOT, "src", "RimMandrake", "DeepDrill", "Defs", "RM_DeepHomeTable.xml")
DUMP_ENV = "RM_DEFDUMP_SQLITE"
DUMP_DEFAULT = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
ROLES = ("id", "item", "mineable", "producer", "zero", "retire")
PLACED = ("item", "mineable", "producer")      # must resolve for a group to be emitted
CORE = "ludeon.rimworld"
NEVER_FILTERED = "Steel"                       # the planet-wide deep resource (DEEP_DRILL_HOME_BIOME_1)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse_bindings(material, text):
    """-> (groups, errors). A group is {role: [names]} with 'id' a single string."""
    groups, errs = [], []
    text = (text or "").strip()
    if not text:
        return groups, errs
    parts = [p.strip() for p in text.split("|")]
    for p in parts:
        g = {r: [] for r in ROLES if r != "id"}
        g["id"] = None
        for tok in p.split():
            role, sep, name = tok.partition(":")
            if not sep or role not in ROLES or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                errs.append(f"{material}: bad binding token {tok!r}")
                continue
            if role == "id":
                if g["id"]:
                    errs.append(f"{material}: two ids in one group")
                g["id"] = name
            else:
                g[role].append(name)
        if not any(g[r] for r in ROLES if r != "id"):
            errs.append(f"{material}: empty binding group {p!r}")
        groups.append(g)
    if len(groups) > 1 and not all(g["id"] for g in groups):
        errs.append(f"{material}: a split row needs an id: on every group")
    if len(groups) == 1 and not groups[0]["id"]:
        groups[0]["id"] = slug(material)
    return groups, errs


class DefIndex:
    """ThingDef defName -> facts, from the def dump (if readable) and the repo's own Defs XML."""

    def __init__(self, dump=None, root=ROOT, use_src=True):
        self.dump, self.src, self.fingerprint = {}, {}, None
        if dump and os.path.exists(dump):
            con = sqlite3.connect("file:" + dump + "?mode=ro", uri=True)
            prov = dict(con.execute("select key, value from provenance"))
            self.fingerprint = prov.get("modlist_fingerprint")
            for name, pkg, j in con.execute("select def_name, package_id, json from defs where def_type='ThingDef'"):
                mt = re.search(r'"mineableThing":"(\w+)"', j)
                deep = re.search(r'"deepCommonality":([0-9.eE+-]+)', j)
                res = re.search(r'"isResourceRock":(true|false)', j)
                self.dump[name] = {"pkg": pkg, "mineableThing": mt.group(1) if mt else None,
                                   "deep": float(deep.group(1)) if deep else 0.0,
                                   "resourceRock": bool(res and res.group(1) == "true")}
            con.close()
        if use_src:
            self.src = src_index(root)

    def resolve(self, name):
        """-> package id (str) or None. '' = resolved with no known package."""
        if name in self.dump:
            return self.dump[name]["pkg"] or ""
        if name in self.src:
            return self.src[name] or ""
        return None


def src_index(root):
    """defName -> packageId of the mod folder that defines it, over every Defs/ XML under src/."""
    out, pkg_cache = {}, {}

    def pkg_for(path):
        d = os.path.dirname(path)
        while d.startswith(root) and d != root:
            if d in pkg_cache:
                return pkg_cache[d]
            about = os.path.join(d, "About", "About.xml")
            if os.path.exists(about):
                m = re.search(r"<packageId>([^<]+)</packageId>", open(about, encoding="utf-8", errors="ignore").read())
                pkg_cache[d] = m.group(1).strip().lower() if m else ""
                return pkg_cache[d]
            d = os.path.dirname(d)
        return ""

    for f in glob.glob(os.path.join(root, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        names = re.findall(r"<defName>(\w+)</defName>", t)
        if names:
            p = pkg_for(f)
            for n in names:
                out.setdefault(n, p)
    return out


def biome_cols(row):
    return [k for k in row if k.startswith(("RM_", "RUT_"))]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load(path=CSV):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def analyse(rows, index):
    """-> dict(hard, soft, groups=[(row, group)], emit=[(row, group)], coverage_missing=[...])"""
    hard, soft, allg, emit = [], [], [], []
    bound = {}
    if rows and "bindings" not in rows[0]:
        return {"hard": ["CSV has no bindings column"], "soft": [], "groups": [], "emit": [], "uncovered": []}
    for r in rows:
        m = r["material"]
        groups, errs = parse_bindings(m, r.get("bindings"))
        hard += errs
        ids = set()
        for g in groups:
            if g["id"] in ids:
                hard.append(f"{m}: duplicate id {g['id']}")
            ids.add(g["id"])
            for role in ("item", "mineable", "producer", "retire"):
                for n in g[role]:
                    if n in bound and bound[n] != (m, g["id"]):
                        hard.append(f"{n}: bound twice ({bound[n][0]} and {m})")
                    bound[n] = (m, g["id"])
            allg.append((r, g))
        if float(num(r.get("OTHER_vanilla_biomes")) or 0) > 0 and num(r.get("deep_weight")) and \
                any(NEVER_FILTERED != n for g in groups for n in g["item"]):
            hard.append(f"{m}: OTHER_vanilla_biomes > 0 with deep_weight > 0 cannot be written as deep homes "
                        f"(expand the vanilla biomes or zero one of them)")
        eligible = re.match(r"(RULED|BUILT)", r["status"].strip())
        if not eligible:
            continue
        if not groups:
            soft.append(f"{m}: RULED/BUILT but nothing bound - not emitted")
            continue
        for g in groups:
            missing = [n for role in PLACED for n in g[role] if index.resolve(n) is None]
            if missing:
                soft.append(f"{m}/{g['id']}: not emitted, unresolved {', '.join(missing)}")
            else:
                emit.append((r, g))
    # mineable -> item consistency, measured only where the dump knows the mineable
    for r, g in allg:
        for n in g["mineable"]:
            d = index.dump.get(n)
            if d and d["mineableThing"] and d["mineableThing"] not in g["item"]:
                soft.append(f"{r['material']}: mineable {n} yields {d['mineableThing']}, not a bound item")
    uncovered = []
    if index.dump:
        names = set(bound)
        for r, g in allg:
            names.update(g["zero"])
        for n, d in index.dump.items():
            if n == NEVER_FILTERED or n in names:
                continue
            if d["resourceRock"] and d["mineableThing"]:
                if d["mineableThing"] not in names:
                    uncovered.append(f"{n} (resource mineable -> {d['mineableThing']})")
            elif d["deep"] > 0 and not d["mineableThing"]:
                uncovered.append(f"{n} (deep item, deepCommonality {d['deep']:g})")
    return {"hard": hard, "soft": soft, "groups": allg, "emit": emit, "uncovered": sorted(uncovered)}


def deep_homes(row):
    if not (num(row.get("deep_weight")) or 0) > 0:
        return []
    out = []
    for c in biome_cols(row):
        v = row[c].strip()
        if v == "deep-only" or (num(v) or 0) > 0:
            out.append(c)
    return out


def _comment(s):
    """Text safe inside an XML comment ('--' is illegal there; RimWorld's loader rejects the file)."""
    return re.sub(r"-{2,}", "-", escape(s)).rstrip("-")


def emit_deep_table(rows):
    lines = []
    seen = set()
    for r in rows:
        groups, _ = parse_bindings(r["material"], r.get("bindings"))
        homes = deep_homes(r)
        for g in groups:
            for n in g["item"] + g["retire"]:
                if n == NEVER_FILTERED or n in seen:
                    continue
                seen.add(n)
                h = "".join(f"<li>{b}</li>" for b in homes)
                lines.append(f"<li><thing>{n}</thing><homes>{h}</homes></li><!-- {_comment(r['material'])} -->")
    head = ("<!-- DEEP_DRILL_HOME_BIOME_1. GENERATED by src/RimMandrake/Utils/gen_mineral_registry.py (write-deep mode) from "
            "design/RimMandrake/mineral_abundance_registry_2026-10-03.csv (bindings item/retire, deep_weight, biome columns). "
            "Do not hand-edit: change the CSV and regenerate. A deposit with an empty home list is never found by a drill "
            "(steel instead). Defs not listed here pass through untouched. Steel is the planet-wide deep resource and is "
            "never filtered. -->")
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n" + head + "\n<RimMandrake.DeepDrill.RM_DeepHomeDef>\n"
            "<defName>RM_DeepHomeTable</defName>\n<rows>\n" + "\n".join(lines) + "\n</rows>\n"
            "</RimMandrake.DeepDrill.RM_DeepHomeDef>\n</Defs>\n")


def camel(s):
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[^A-Za-z0-9]+", s) if p)


def _li(name, index):
    pkg = index.resolve(name)
    may = f' MayRequire="{pkg}"' if pkg and pkg != CORE else ""
    return f"<li{may}>{name}</li>"


def emit_registry(emit, index):
    out = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<Defs>",
           "<!-- MINERALS_WHERE_THEY_BELONG_1 R1. GENERATED by src/RimMandrake/Utils/gen_mineral_registry.py from "
           "design/RimMandrake/mineral_abundance_registry_2026-10-03.csv; validated against def dump "
           f"modlist_fingerprint {index.fingerprint or 'NONE (repo XML only)'}. Values PROVISIONAL. Do not hand-edit. -->"]
    for r, g in emit:
        cells = []
        for c in biome_cols(r):
            v = r[c].strip()
            if v == "0":
                continue
            if num(v) is not None:
                cells.append(f"<li><biome>{c}</biome><value>{v}</value></li>")
            else:
                cells.append(f"<li><biome>{c}</biome><token>{v}</token></li>")
        f = ["<RimMandrake.Minerals.RM_MineralRegistryDef>",
             f"<defName>RM_Mineral_{camel(g['id'])}</defName>",
             f"<label>{escape(r['material'])}</label>",
             f"<materialId>{g['id']}</materialId>",
             f"<status>{escape(r['status'].split()[0].rstrip(';'))}</status>",
             f"<form>{escape(r['form'])}</form>",
             f"<unit>{escape(r['unit'])}</unit>"]
        for tag, col in (("unitsPerCellOrFind", "units_per_cell_or_find"), ("deepWeight", "deep_weight"),
                         ("otherBiomes", "OTHER_vanilla_biomes"), ("salvagePerYear", "salvage_per_year"),
                         ("tradePerYear", "trade_per_year")):
            if num(r.get(col)) is not None:
                f.append(f"<{tag}>{r[col].strip()}</{tag}>")
        f.append(f"<quarryLocal>{'true' if r.get('quarry', '').strip() == 'local' else 'false'}</quarryLocal>")
        q = (r.get("quarry_per_100_jobs") or "").strip()
        if num(q) is not None:
            f.append(f"<quarryPer100Jobs>{q}</quarryPer100Jobs>")
        for role, tag in (("item", "items"), ("mineable", "mineables"), ("producer", "producers")):
            if g[role]:
                f.append(f"<{tag}>" + "".join(_li(n, index) for n in g[role]) + f"</{tag}>")
        for role, tag in (("zero", "zeroProducers"), ("retire", "retiredItems")):
            if g[role]:
                f.append(f"<{tag}>" + "".join(f"<li>{n}</li>" for n in g[role]) + f"</{tag}>")
        if cells:
            f.append("<biomes>" + "".join(cells) + "</biomes>")
        f.append("</RimMandrake.Minerals.RM_MineralRegistryDef>")
        out.append("\n".join(f))
    out.append("</Defs>")
    return "\n".join(out) + "\n"


def run(argv):
    csv_path = argv[argv.index("--csv") + 1] if "--csv" in argv else CSV
    dump = None if "--no-dump" in argv else (argv[argv.index("--dump") + 1] if "--dump" in argv
                                              else os.environ.get(DUMP_ENV, DUMP_DEFAULT))
    rows, hard0, soft0, _ = mrc.check(csv_path, mrc.biome_defnames())
    index = DefIndex(dump)
    a = analyse(rows, index)
    hard = hard0 + a["hard"]
    dump_state = (f"dump {index.fingerprint} ({len(index.dump)} ThingDefs)" if index.dump
                  else "dump UNREADABLE - resolution from repo XML only, coverage UNMEASURED")
    print(f"{len(rows)} rows, {len(a['groups'])} material groups, {len(a['emit'])} emit-ready; "
          f"{len(hard)} hard, {len(soft0) + len(a['soft'])} soft; {dump_state}; values PROVISIONAL")
    for s in soft0 + a["soft"]:
        print("SOFT", s)
    if index.dump:
        # report-only: a donor mineral with no row is a registry gap to triage, not a build break
        print(f"COVERAGE MEASURED: {len(a['uncovered'])} unregistered minerals in the dump")
        for u in a["uncovered"]:
            print("UNREGISTERED", u)
    else:
        print("COVERAGE UNMEASURED: no readable def dump")
    for h in hard:
        print("HARD", h)
    if hard:
        return 1
    if "--write-deep" in argv:
        txt = emit_deep_table(rows)
        old = open(DEEP_TABLE, encoding="utf-8").read() if os.path.exists(DEEP_TABLE) else ""
        if txt != old:
            open(DEEP_TABLE, "w", encoding="utf-8", newline="\n").write(txt)
            print("WROTE", DEEP_TABLE)
        else:
            print("UNCHANGED", DEEP_TABLE)
    if "--registry-out" in argv:
        p = argv[argv.index("--registry-out") + 1]
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write(emit_registry(a["emit"], index))
        print("WROTE", p, f"({len(a['emit'])} defs)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import selftest_gen_mineral_registry as t
        sys.exit(t.main())
    sys.exit(run(sys.argv[1:]))
