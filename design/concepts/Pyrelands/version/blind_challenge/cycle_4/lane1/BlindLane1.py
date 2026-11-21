#!/usr/bin/env python3
"""Pyrelands 0.1.0 blind challenge cycle 4, lane 1, the def and settings half: written from the bars alone (tree.json,
sheet.md, record.json rows) and the shipped files (Defs, Patches, Languages, About, RM_PyrelandsMod.cs). One JSON row per
line on stdout. Exit 0 = no FAIL row.
    python3 BlindLane1.py [--mod <src/RimMandrake/Pyrelands>]"""
import argparse, glob, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
FAILS = 0


def row(id_, bars, kind, verdict, cases, detail):
    global FAILS
    FAILS += verdict == "FAIL"
    print(json.dumps({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}))


def xml_files(mod, *dirs):
    out = []
    for d in dirs:
        out += sorted(glob.glob(os.path.join(mod, d, "**", "*.xml"), recursive=True))
    return out


def defs(mod):
    for p in xml_files(mod, "Defs"):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            yield p, None, e
            continue
        for el in root:
            yield p, el, None


def biome_text(mod):
    bars = ["biome_text_says_engineered"]
    found, parse_err, desc = [], [], None
    for p, el, err in defs(mod):
        if err is not None:
            parse_err.append(os.path.relpath(p, mod))
            continue
        if el.tag == "BiomeDef" and (el.findtext("defName") or "") == "RM_Pyrelands":
            found.append(os.path.relpath(p, mod))
            desc = el.findtext("description") or ""
    d = desc or ""
    eng = re.search(r"genetically\s+engineered", d, re.I) is not None
    mil = re.search(r"millenni", d, re.I) is not None
    natural = re.search(r"natural (wildfire|grassland)", d, re.I) is not None
    ok = len(found) == 1 and eng and mil and not natural and not parse_err
    row("biome_description_says_engineered", bars, "fixed", "PASS" if ok else "FAIL", 1,
        "RM_Pyrelands BiomeDefs found %s; description says 'genetically engineered' %s, 'millennia' %s, reads as a natural wildfire grassland %s; "
        "def files that do not parse %s" % (found, eng, mil, natural, parse_err))
    # Nothing later overwrites the description: no DefInjected translation, no patch on it.
    over = []
    for p in xml_files(mod, "Languages", "Patches"):
        t = open(p, encoding="utf-8").read()
        if re.search(r"RM_Pyrelands\.description|defName\s*=\s*\"RM_Pyrelands\"\][^<]*/description", t):
            over.append(os.path.relpath(p, mod))
    di = glob.glob(os.path.join(mod, "Languages", "*", "DefInjected", "BiomeDef", "*.xml"))
    row("biome_description_not_overwritten", bars, "fixed", "PASS" if not over and not di else "FAIL", 1,
        "patches or translations that touch RM_Pyrelands' description: %s; DefInjected BiomeDef files: %s" % (over, [os.path.relpath(x, mod) for x in di]))
    # False pass named by the leaf: the word only in a plant's description. Report where else it stands.
    elsewhere = []
    for p, el, err in defs(mod):
        if el is None or el.tag == "BiomeDef":
            continue
        if re.search(r"engineered", el.findtext("description") or "", re.I):
            elsewhere.append(el.findtext("defName") or el.get("Name"))
    row("biome_engineered_not_only_in_a_plant", bars, "info", "INFO", len(elsewhere),
        "other defs whose description also says engineered: %s (the biome's own description carries it, row biome_description_says_engineered)" % elsewhere)


def absent(mod, bars, id_, pattern, what):
    hits = []
    for p in glob.glob(os.path.join(mod, "**", "*"), recursive=True):
        rel = os.path.relpath(p, mod)
        if os.path.isdir(p) or rel.startswith("Source" + os.sep + "SelfTest") or rel.startswith("Assemblies"):
            continue
        if re.search(pattern, os.path.basename(p), re.I):
            hits.append(rel + " (file name)")
            continue
        if not p.endswith((".xml", ".cs")):
            continue
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            if re.search(pattern, line, re.I):
                # an item name in a comment (SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK) names history, not a firebreak
                if re.search(r"[A-Z0-9]+(_[A-Z0-9]+){2,}", line) and re.search(r"(//|<!--|///)", line) and not re.search(r"defName|Def\b|class ", line):
                    if all(re.fullmatch(r"[A-Z0-9_]+", w) for w in re.findall(r"\w*" + pattern + r"\w*", line, re.I)):
                        continue
                hits.append("%s:%d: %s" % (rel, i, line.strip()[:120]))
    # The Defs a game would load: no TerrainDef, ThingDef or RecipeDef whose defName or label names it.
    defhits = []
    for p, el, err in defs(mod):
        if el is None:
            continue
        name = (el.findtext("defName") or "") + " " + (el.findtext("label") or "")
        if re.search(pattern, name, re.I):
            defhits.append("%s %s" % (el.tag, el.findtext("defName")))
    ok = not hits and not defhits
    row(id_, bars, "fixed", "PASS" if ok else "FAIL", 1,
        "%s: defs that name it %s; files or lines that name it (item-name comments excepted) %s" % (what, defhits, hits[:8]))


def const_value(src, name):
    m = re.search(r"const\s+(?:float|int)\s+" + re.escape(name) + r"\s*=\s*([-0-9.]+)f?\s*;", src)
    return float(m.group(1)) if m else None


def num(expr, src, extra):
    e = expr.strip()
    def rep(m):
        w = m.group(0)
        if w in extra:
            return repr(extra[w])
        v = const_value(src, w.split(".")[-1])
        if v is None:
            raise ValueError("cannot resolve " + w)
        return repr(v)
    e = re.sub(r"(?<![\d.])(\d+(?:\.\d+)?)f\b", r"\1", e)
    e = re.sub(r"[A-Za-z_][\w.]*", rep, e)
    return float(eval(e, {"__builtins__": {}}))


def settings(mod):
    bars = ["inv_settings_gate"]
    src = open(os.path.join(mod, "Source", "RM_PyrelandsMod.cs"), encoding="utf-8").read()
    enforcer = open(os.path.join(mod, "Source", "RM_PyrelandsDensityEnforcer.cs"), encoding="utf-8").read()
    extra = {}
    m = re.search(r"WildPlantRegrowDays\s*=\s*([-0-9.]+)f?", enforcer)
    if m:
        extra["RM_PyrelandsDensityEnforcer.WildPlantRegrowDays"] = float(m.group(1))
    fields = re.findall(r"public static (bool|float|int|string) (\w+) = ([^;]+);", src)
    vals = {}
    for t, n, v in fields:
        v = v.strip()
        if t == "bool":
            vals[n] = (t, v == "true")
        elif t == "string":
            vals[n] = (t, v.strip('"'))
        else:
            vals[n] = (t, num(v, src, extra))
    scribe = dict()
    for n, key, d in re.findall(r"Scribe_Values\.Look\(ref (\w+), \"(\w+)\", ([^)]+)\);", src):
        scribe[n] = (key, d.strip())
    bad = []
    for n, (t, v) in vals.items():
        if n not in scribe:
            bad.append(n + ": not saved")
            continue
        d = scribe[n][1]
        dv = (d == "true") if t == "bool" else d.strip('"') if t == "string" else num(d, src, extra)
        if dv != v and not (isinstance(v, float) and abs(dv - v) < 1e-6):
            bad.append("%s: initial %r, saved default %r" % (n, v, dv))
    keys = [k for k, _ in scribe.values()]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    row("settings_defaults_saved_as_shipped", bars, "fixed", "PASS" if not bad and not dup else "FAIL", len(vals),
        "%d settings fields; a saved default that differs from the shipped value, or a field never saved: %s; duplicate save keys %s" % (len(vals), bad, dup))
    sliders = re.findall(r"(\w+) = (?:\(int\))?(?:Mathf\.RoundToInt\()?list\.Slider\((\w+), ([^,]+), ([^)]+?)\)\)?;", src)
    sbad = []
    for n, n2, lo, hi in sliders:
        lo_v, hi_v = num(lo, src, extra), num(hi, src, extra)
        v = vals.get(n, (None, None))[1]
        if n != n2 or v is None or not (lo_v <= v <= hi_v):
            sbad.append("%s default %r outside [%s, %s]" % (n, v, lo_v, hi_v))
    unslid = [n for n, (t, v) in vals.items() if t in ("float", "int") and n not in {s[0] for s in sliders}]
    row("settings_slider_ranges_hold_defaults", bars, "sweep", "PASS" if not sbad and sliders else "FAIL", len(sliders),
        "%d sliders; defaults outside their range: %s; numeric settings with no slider: %s" % (len(sliders), sbad, unslid))
    boxes = set(re.findall(r"CheckboxLabeled\([^;]*?ref (\w+)", src, re.S))
    nobox = [n for n, (t, v) in vals.items() if t == "bool" and n not in boxes]
    row("settings_every_switch_has_a_checkbox", bars, "fixed", "PASS" if not nobox else "FAIL", sum(1 for t, v in vals.values() if t == "bool"),
        "bool settings with no checkbox on the settings screen: %s" % nobox)
    lab = re.search(r"CheckboxLabeled\(\"([^\"]*)\", ref biomeGenerationEnabled", src)
    gen = vals.get("biomeGenerationEnabled", (None, None))[1]
    ok = gen is False and lab is not None and "unsupported" in lab.group(1).lower()
    row("settings_worldgen_switch_ships_off_unsupported", bars, "fixed", "PASS" if ok else "FAIL", 1,
        "biomeGenerationEnabled ships %r; label %r" % (gen, lab.group(1) if lab else None))
    row("settings_count", bars, "info", "INFO", len(vals),
        "%d settings fields (%d switches, %d numbers, %d text); the record row says about 47" % (
            len(vals), sum(t == "bool" for t, v in vals.values()), sum(t in ("float", "int") for t, v in vals.values()),
            sum(t == "string" for t, v in vals.values())))


def art(mod):
    bars = ["inv_art_and_text"]
    tex = os.path.join(mod, "Textures")
    have = set()
    for p in glob.glob(os.path.join(tex, "**", "*.png"), recursive=True):
        have.add(os.path.relpath(p, tex)[:-4].replace(os.sep, "/").lower())
    dirs = {os.path.dirname(h) for h in have}
    paths = []
    for p in xml_files(mod, "Defs", "Patches"):
        for m in re.finditer(r"<(?:texPath|iconPath|texture|wornGraphicPath|bodyGraphicPath)>([^<]+)</", open(p, encoding="utf-8").read()):
            paths.append((os.path.relpath(p, mod), m.group(1).strip()))
    ours, vanilla = [], []
    for f, t in paths:
        k = t.lower()
        ok = k in have or any(k + s in have for s in ("_north", "_south", "_east", "_a", "_b")) or k in dirs
        if not ok:
            (ours if re.search(r"(rm_|rsw_|rut_|pyre|fe_|ember|ash|scorch|furnace|ullai|firehawk|flamefang)", k) else vanilla).append("%s: %s" % (f, t))
    row("art_texture_paths_resolve", bars, "fixed", "PASS" if not ours else "FAIL", len(paths),
        "%d texture references in Defs and Patches, %d pngs shipped; ours that resolve to no shipped png: %s; others left to vanilla's own content: %d %s" % (
            len(paths), len(have), ours[:10], len(vanilla), vanilla[:6]))
    nodesc = []
    for p, el, err in defs(mod):
        if el is None or el.get("Abstract") == "True":
            continue
        if el.tag in ("ThingDef", "BiomeDef", "TerrainDef", "HediffDef", "WeatherDef") and el.findtext("label") and not el.findtext("description") and not el.get("ParentName"):
            nodesc.append("%s %s" % (el.tag, el.findtext("defName")))
    row("text_labelled_defs_have_descriptions", bars, "info", "INFO", len(nodesc),
        "labelled defs with no description and no parent to inherit one: %s" % nodesc[:12])
    row("art_owner_sheet_approval", bars, "info", "INFO", 0,
        "the bar rests on his 2026-10-16 approval of the art sheet (record.json proof_evidence OWNER:1792122659817386516); lane 1 reads no ledger. "
        "Settled by the record check of that event (lane 2 rerun of RECORD_ART_SHEET).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.path.join(REPO, "src/RimMandrake/Pyrelands"))
    a = ap.parse_args()
    for f in (biome_text,
              lambda m: absent(m, ["inv_firebreak_firefoam"], "firebreak_floor_stays_cut", r"firebreak", "the firebreak floor"),
              lambda m: absent(m, ["inv_lightning_breaker"], "lightning_breaker_stays_cut", r"breaker|fulgurite", "lightning breakers and fulgurite"),
              settings, art):
        try:
            f(a.mod)
        except Exception as e:  # a crash is a failing row, never silence
            row("py_suite_crash_%s" % getattr(f, "__name__", "lambda"), ["inv_settings_gate"], "fixed", "FAIL", 0, repr(e))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
