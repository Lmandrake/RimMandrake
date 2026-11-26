#!/usr/bin/env python3
"""Pyrelands blind cycle 5, lane 1, the defs/text/settings half: written from the bars (biome_text_says_engineered,
inv_firebreak_firefoam, inv_lightning_breaker, inv_settings_gate, inv_art_and_text) and the shipped files only.
    python3 lane1_defs.py [--src <Pyrelands mod dir>]
One JSON row per line on stdout. Exit 0 no FAIL, 1 a FAIL, 2 could not read the mod."""
import argparse, glob, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
FAILS = 0


def row(rid, bars, kind, verdict, cases, detail):
    global FAILS
    FAILS += verdict == "FAIL"
    print(json.dumps({"id": rid, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail}))


def xml_files(root):
    return sorted(glob.glob(os.path.join(root, "**", "*.xml"), recursive=True))


def parse(p):
    try:
        return ET.parse(p).getroot()
    except ET.ParseError as e:
        return e


def code_lines(text):
    """C# text with // and /* */ comments and string literals removed (identifiers only)."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(REPO, "src/RimMandrake/Pyrelands"))
    src = ap.parse_args().src
    defs_dir, patches_dir, lang_dir = (os.path.join(src, d) for d in ("Defs", "Patches", "Languages"))
    if not os.path.isdir(defs_dir):
        print("no Defs folder under", src)
        sys.exit(2)
    roots = {p: parse(p) for p in xml_files(defs_dir)}
    bad_xml = [os.path.relpath(p, src) for p, r in roots.items() if isinstance(r, Exception)]
    row("defs_parse", ["inv_art_and_text"], "fixed", "FAIL" if bad_xml else "PASS", len(roots),
        "every Defs XML parses" + (": broken " + ", ".join(bad_xml) if bad_xml else ""))
    defs = []
    for p, r in roots.items():
        if isinstance(r, Exception):
            continue
        for d in r:
            if isinstance(d.tag, str):
                defs.append((p, d))

    # ------------------------------------------------ biome_text_says_engineered (offline bar)
    bars = ["biome_text_says_engineered"]
    biome = [d for p, d in defs if d.tag == "BiomeDef" and (d.findtext("defName") or "").strip() == "RM_Pyrelands"]
    desc = (biome[0].findtext("description") or "") if biome else ""
    says = bool(re.search(r"genetically[\s-]+engineered", desc, re.I))
    millennia = bool(re.search(r"millenni", desc, re.I))
    savanna = bool(re.search(r"savann", desc, re.I))
    row("biome_desc_engineered", bars, "fixed", "PASS" if biome and says and millennia and savanna else "FAIL", 1,
        ("one RM_Pyrelands BiomeDef" if len(biome) == 1 else "%d RM_Pyrelands BiomeDefs" % len(biome))
        + "; description says genetically engineered: %s, a savanna: %s, burned for millennia: %s; text: %r" % (says, savanna, millennia, desc[:260]))
    # "As loaded": nothing in this mod, nor any mod in the repo, replaces that description (patch, DefInjected, a second def).
    overriders = []
    for p in xml_files(os.path.join(REPO, "src/RimMandrake")):
        if "/Pyrelands/Defs/" in p:
            continue
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if re.search(r"RM_Pyrelands[\"'\]]\s*\]?/description|<RM_Pyrelands\.description>", t):
            overriders.append(os.path.relpath(p, REPO))
        elif "/Defs/" in p and re.search(r"<defName>\s*RM_Pyrelands\s*</defName>", t) and "<BiomeDef" in t:
            overriders.append(os.path.relpath(p, REPO) + " (a second RM_Pyrelands BiomeDef)")
    abstract_parent = biome[0].get("ParentName") if biome else None
    row("biome_desc_not_overridden", bars, "fixed", "PASS" if not overriders else "UNSETTLED", len(overriders),
        "no patch, DefInjected or second def in src/RimMandrake replaces the RM_Pyrelands description (ParentName %r)" % abstract_parent
        if not overriders else "these files touch RM_Pyrelands' description: %s; which wins as loaded needs a def dump or the live game" % overriders)

    # ------------------------------------------------ inv_firebreak_firefoam and inv_lightning_breaker (offline bars): excised
    def excised(rid, bar, pattern, what):
        hits = []
        for p, d in defs:
            dn = (d.findtext("defName") or "") + " " + (d.get("Name") or "") + " " + (d.findtext("label") or "")
            if re.search(pattern, dn, re.I):
                hits.append("def %s %s in %s" % (d.tag, dn.strip(), os.path.relpath(p, src)))
        for p in xml_files(patches_dir):
            t = open(p, encoding="utf-8", errors="replace").read()
            t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
            if re.search(pattern, t, re.I):
                hits.append("patch " + os.path.relpath(p, src))
        for p in xml_files(lang_dir):
            t = re.sub(r"<!--.*?-->", " ", open(p, encoding="utf-8", errors="replace").read(), flags=re.S)
            for m in re.finditer(r"<([A-Za-z0-9_.]+)>([^<]*)</\1>", t):
                if re.search(pattern, m.group(1) + " " + m.group(2), re.I):
                    hits.append("text %s in %s" % (m.group(1), os.path.relpath(p, src)))
        for p in glob.glob(os.path.join(src, "Source", "**", "*.cs"), recursive=True):
            if "/SelfTest/" in p:
                continue
            c = code_lines(open(p, encoding="utf-8", errors="replace").read())
            c = re.sub(r"\"(?:\\.|[^\"\\])*\"", lambda m: m.group(0) if re.search(pattern, m.group(0), re.I) else '""', c)
            for m in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*|\"[^\"]*\"", c):
                if re.search(pattern, m.group(0), re.I):
                    hits.append("code %s in %s" % (m.group(0)[:60], os.path.relpath(p, src)))
                    break
        about = os.path.join(src, "About", "About.xml")
        if os.path.exists(about):
            t = re.sub(r"<!--.*?-->", " ", open(about, encoding="utf-8", errors="replace").read(), flags=re.S)
            if re.search(pattern, t, re.I):
                hits.append("About.xml promises it")
        row(rid, [bar], "fixed", "FAIL" if hits else "PASS", 1,
            ("%s is gone from defs, patches, text, code and About.xml (comments excluded)" % what) if not hits else "%s still present: %s" % (what, hits[:8]))

    excised("firebreak_excised", "inv_firebreak_firefoam", r"fire\s*break", "the firebreak floor")
    excised("lightning_breaker_excised", "inv_lightning_breaker", r"breaker|fulgurite", "the lightning breaker and fulgurite")
    # the sprayer the bar's id names stays (his root ending): it must still be a def
    spr = [d for p, d in defs if re.search(r"firefoam", (d.findtext("defName") or ""), re.I)]
    row("firefoam_sprayer_stays", ["inv_firebreak_firefoam", "inv_firefoam_sprayer"], "fixed", "PASS" if spr else "FAIL", 1,
        "firefoam defs that stay: %s" % [(d.tag, d.findtext("defName")) for d in spr])

    # ------------------------------------------------ inv_settings_gate (offline bar): the settings as shipped
    bars = ["inv_settings_gate"]
    mod = open(os.path.join(src, "Source", "RM_PyrelandsMod.cs"), encoding="utf-8").read()
    consts = dict(re.findall(r"(?:public|private|internal)\s+const\s+float\s+(\w+)\s*=\s*([-\d.]+)f", mod))
    for k in ("BlackRainDousingDefault",):
        m = re.search(r"const float " + k + r"\s*=\s*([-\d.]+)f", open(os.path.join(src, "Source/Kernel/RM_FireEcoKernel.cs")).read())
        if m:
            consts[k] = m.group(1)
    fields = re.findall(r"public static (bool|float|int|string) (\w+) = ([^;]+);", mod)

    def val(typ, txt):
        txt = txt.strip()
        if txt in consts:
            txt = consts[txt]
        if typ == "bool":
            return txt == "true"
        if typ == "string":
            return txt.strip('"')
        try:
            return float(txt.rstrip("f"))
        except ValueError:
            return txt
    shipped = {n: (t, val(t, v)) for t, n, v in fields}
    scribed = {m.group(1): m.group(3) for m in re.finditer(r"Scribe_Values\.Look\(ref (\w+), \"(\w+)\", ([^)]+)\);", mod)}
    mism, unsaved = [], []
    for n, (t, v) in shipped.items():
        if n not in scribed:
            unsaved.append(n)
            continue
        if val(t, scribed[n]) != v:
            mism.append("%s: field %r, scribe default %r" % (n, v, scribed[n]))
    row("settings_saved_default_is_shipped", bars, "fixed", "FAIL" if mism else "PASS", len(shipped),
        "%d settings; each saved with its shipped value as the default%s; not saved (session only): %s"
        % (len(shipped), (": MISMATCH " + "; ".join(mism)) if mism else "", unsaved or "none"))
    # every bool has a checkbox; every tuning number has a slider whose range holds its shipped value
    boxes = set(re.findall(r"CheckboxLabeled\([^,]+, ref (\w+)", mod))
    sliders = re.findall(r"(\w+) = (?:Mathf\.RoundToInt\(|\(int\))?list\.Slider\((\w+), ([^,]+), ([^)]+?)\)\)?;", mod)
    nobox = [n for n, (t, v) in shipped.items() if t == "bool" and n not in boxes]
    out_of_range = []
    slid = set()
    for lhs, arg, lo, hi in sliders:
        slid.add(arg)
        def num(x):
            x = x.strip()
            for k, v in consts.items():
                x = x.replace(k, v)
            x = re.sub(r"(\d)f\b", r"\1", x)
            x = x.replace("RM_PyrelandsDensityEnforcer.WildPlantRegrowDays", "1e9")
            return eval(x, {"__builtins__": {}})
        try:
            l, h = num(lo), num(hi)
        except Exception as e:  # noqa: BLE001
            out_of_range.append("%s: range %s..%s unreadable (%s)" % (arg, lo, hi, e))
            continue
        v = shipped.get(arg, (None, None))[1]
        if not isinstance(v, float) or not (l <= v <= h):
            out_of_range.append("%s=%r outside %s..%s" % (arg, v, l, h))
    noslider = [n for n, (t, v) in shipped.items() if t in ("float", "int") and n not in slid]
    row("settings_every_switch_drawn", bars, "fixed", "FAIL" if nobox else "PASS", len(boxes),
        "every bool setting has a checkbox in the window%s" % ((": missing " + ", ".join(nobox)) if nobox else ""))
    row("settings_slider_ranges_hold_default", bars, "sweep", "FAIL" if out_of_range else "PASS", len(sliders),
        "%d sliders; each range holds its shipped default%s; numbers without a slider: %s"
        % (len(sliders), (": " + "; ".join(out_of_range)) if out_of_range else "", noslider or "none"))
    # worldgen: the only worldgen toggle ships off and its label says unsupported (his card 2026-11-13); restart toggles say so
    wg = shipped.get("biomeGenerationEnabled", (None, None))[1]
    lab = re.search(r"CheckboxLabeled\(\"([^\"]*)\", ref biomeGenerationEnabled", mod)
    restart = {n: re.search(r"CheckboxLabeled\(\"([^\"]*)\", ref " + n, mod) for n in ("furnaceBeastGiant", "ullaiEnabled", "ambientAshHeavy")}
    ok = wg is False and lab and "unsupported" in lab.group(1).lower() and all(m and "restart" in m.group(1).lower() for m in restart.values())
    row("settings_worldgen_off_and_labelled", bars, "fixed", "PASS" if ok else "FAIL", 4,
        "biomeGenerationEnabled ships %r, label %r; restart-only toggles labelled: %s"
        % (wg, lab.group(1) if lab else None, {k: (m.group(1) if m else None) for k, m in restart.items()}))
    # Reset: the reset-all button resets every field to its shipped value (shippedDefaults read from the initialisers)
    reset_ok = "ResetAllFields" in mod and "shippedDefaults" in mod
    row("settings_reset_all_present", bars, "info", "INFO", 1,
        "a Reset-all button exists (%s); whether it restores every field is a reflection read at runtime (game-side)" % reset_ok)

    # ------------------------------------------------ inv_art_and_text (offline bar): every shipped picture and text resolves
    bars = ["inv_art_and_text"]
    tex_root = os.path.join(src, "Textures")
    all_tex = set()
    for p in glob.glob(os.path.join(REPO, "src/RimMandrake", "*", "Textures", "**", "*.png"), recursive=True):
        rel = p.split("/Textures/", 1)[1][:-4]
        all_tex.add(rel)
    own_tex = {p.split("/Textures/", 1)[1][:-4] for p in glob.glob(os.path.join(tex_root, "**", "*.png"), recursive=True)}
    missing, foreign, checked = [], [], 0
    for p, d in defs:
        for g in d.iter():
            if g.tag not in ("texPath", "texturePath", "iconPath", "uiIconPath") or not (g.text or "").strip():
                continue
            tp = g.text.strip()
            checked += 1
            variants = [tp, tp + "_north", tp + "_south", tp + "_east", tp + "_east"]
            hit = any(v in all_tex for v in variants) or any(t.startswith(tp + "/") for t in all_tex)
            if hit:
                continue
            top = tp.split("/")[0]
            if any(t.startswith(top + "/") and "RM_" in tp for t in own_tex) or tp.split("/")[-1].startswith(("RM_", "RUT_", "RSW_")):
                missing.append("%s %s: %s" % (d.tag, d.findtext("defName") or d.get("Name"), tp))
            else:
                foreign.append(tp)
    row("art_texture_paths_resolve", bars, "fixed", "FAIL" if missing else "PASS", checked,
        "%d texture paths in the defs; of our own (RM_/RUT_/RSW_ named), unresolved in any repo mod's Textures: %s"
        % (checked, missing[:10] or "none"))
    # Vanilla paths read from RimSage this sitting (2026-11-21): Core Terrain_Natural.xml (Gravel, Sand, Soil, SoilRich
    # texturePath), Core Items_Exotic.xml (ThrumboHorn texPath), Designator_Mine.cs (ContentFinder "UI/Designators/Mine").
    vanilla_seen = {"Terrain/Surfaces/Gravel", "Terrain/Surfaces/Sand", "Terrain/Surfaces/Soil", "Terrain/Surfaces/SoilRich",
                    "Things/Item/Special/ThrumboHorn", "UI/Designators/Mine"}
    unknown = sorted(set(foreign) - vanilla_seen)
    row("art_vanilla_texture_paths", bars, "not_kernel" if unknown else "fixed", "UNSETTLED" if unknown else "PASS", len(foreign),
        ("%d texture paths name no RM_ art, are in no repo mod and were not seen in vanilla: %s. Settles by RimSage or a def dump."
         % (len(unknown), unknown[:12])) if unknown else
        "%d paths outside the repo's art, each a vanilla Core texture seen in RimSage: %s" % (len(set(foreign)), sorted(set(foreign))))
    # text: every concrete def a player reads has a label and a description
    need_desc = ("ThingDef", "TerrainDef", "BiomeDef", "WeatherDef", "HediffDef", "PawnKindDef", "ResearchProjectDef", "GameConditionDef")
    nolabel, nodesc, n = [], [], 0
    for p, d in defs:
        if d.tag not in need_desc or d.get("Abstract", "").lower() == "true":
            continue
        dn = d.findtext("defName") or ""
        if not dn:
            continue
        n += 1
        has = lambda k: bool((d.findtext(k) or "").strip())
        if not has("label") and not d.get("ParentName"):
            nolabel.append(dn)
        if d.tag in ("ThingDef", "TerrainDef", "BiomeDef", "HediffDef", "ResearchProjectDef") and not has("description") and not d.get("ParentName"):
            cat = (d.findtext("category") or "")
            if cat not in ("Mote", "Ethereal", "Projectile", "Filth") and not dn.endswith(("_Leather", "_Meat")):
                nodesc.append("%s %s" % (d.tag, dn))
    row("text_labels_and_descriptions", bars, "fixed", "FAIL" if (nolabel or nodesc) else "PASS", n,
        "%d concrete defs a player reads (no parent): no label %s; no description %s" % (n, nolabel[:10] or "none", nodesc[:10] or "none"))
    # keyed: every "Key".Translate() in the shipped code has an English keyed string (an unkeyed key prints raw in game)
    keyed = set()
    for p in xml_files(os.path.join(lang_dir, "English", "Keyed")):
        r = parse(p)
        if not isinstance(r, Exception):
            keyed |= {c.tag for c in r if isinstance(c.tag, str)}
    used = {}
    for p in glob.glob(os.path.join(src, "Source", "**", "*.cs"), recursive=True):
        if "/SelfTest/" in p:
            continue
        for k in re.findall(r"\"(RM_[A-Za-z0-9_]+)\"\s*\.\s*Translate", code_lines(open(p, encoding="utf-8").read())):
            used.setdefault(k, os.path.relpath(p, src))
    unkeyed = sorted(k for k in used if k not in keyed)
    row("text_keyed_strings_exist", bars, "fixed", "FAIL" if unkeyed else "PASS", len(used),
        "%d RM_ keys translated in code, %d English keyed strings; unkeyed: %s" % (len(used), len(keyed), [(k, used[k]) for k in unkeyed[:10]] or "none"))
    # a keyed string's named slots: {A_B} is read by the engine as A with sub-symbol B (blank slot); every slot is fed
    underscored = []
    for p in xml_files(os.path.join(lang_dir, "English", "Keyed")):
        for m in re.finditer(r"<([A-Za-z0-9_]+)>([^<]*)</\1>", open(p, encoding="utf-8").read()):
            for slot in re.findall(r"\{([A-Za-z][A-Za-z0-9_]*)\}", m.group(2)):
                if "_" in slot:
                    underscored.append("%s {%s}" % (m.group(1), slot))
    row("text_named_slots_no_underscore", bars + ["inv_firehawk_hunt_rewards"], "fixed", "FAIL" if underscored else "PASS", 1,
        "no keyed string has a named slot with '_' in it (the engine would read it as a sub-symbol and print it blank): %s" % (underscored or "none"))
    # the approval itself is a record (the owner's sheet approval, 2026-10-16): lane 1 cannot read the ledger
    row("art_owner_sheet_approval", bars, "info", "INFO", 0,
        "not game logic: the bar's approval half is his ledger record of the art sheet (OWNER:1792122659817386516), which "
        "lane 1 does not read; it is decided by the record check RECORD_ART_SHEET rerun in lane 2.")
    sys.exit(1 if FAILS else 0)


main()
