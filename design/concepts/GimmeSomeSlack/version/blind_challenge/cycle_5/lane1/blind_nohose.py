#!/usr/bin/env python3
"""Blind lane 1, cycle 5: the two offline bars no_hose / no_hose_in_gss, from their words alone.

Bar words (tree.json no_hose_in_gss; record.json no_hose; sheet.md): "The reader of the mod's defs and source finds no hose,
reel or pipe drawing in Gimme Some Slack: it draws power cords only, hoses live in FlowWorks. It must not read as a hose def
or texture left behind." Oracle: "offline scan: no ThingDef, texture or class for hoses or reels under
src/RimMandrake/GimmeSomeSlack"; false pass: "the scan matching only def names, missing a texture folder".

    python3 blind_nohose.py [--mod <GSS folder>]     prints one JSON row per line; exit 1 if any FAIL
Independent of the builder's selftest_gss_no_hose.py (not read before this was written)."""
import argparse, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
BARS = ["no_hose", "no_hose_in_gss"]
HR = re.compile(r"(?<![a-z])(?i:hose|reel)|Hose|Reel")   # hose or reel as a word or name part (HoseReel, fire_hose, RM_Reel), never inside "those"
PIPE = re.compile(r"(?<![a-z])(?i:pipe)|Pipe")
WORD_HR = re.compile(r"(?i)\b(hoses?|reels?)\b")
rows = []


def row(id, bars, kind, verdict, cases, detail):
    rows.append({"id": id, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail})


def strip_comments(cs):
    cs = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), cs, flags=re.S)
    return re.sub(r"//[^\n]*", "", cs)


def literals(cs):
    # regular and verbatim C# string literals, comments removed first
    for m in re.finditer(r'@"((?:[^"]|"")*)"|"((?:[^"\\\n]|\\.)*)"', strip_comments(cs)):
        yield m.group(1) if m.group(1) is not None else m.group(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod", default=os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack"))
    a = ap.parse_args()
    mod = a.mod
    files = []
    for root, dirs, fs in os.walk(mod):
        rel = os.path.relpath(root, mod)
        if rel.split(os.sep)[0] in ("art_source", "review", "northstar", "northstar_matrix", "live_probes"):
            continue      # dev tooling, not the mod as shipped (proof scripts, review sheets, art sources)
        if "SelfTest" in rel.split(os.sep):
            continue
        for f in fs:
            files.append(os.path.join(root, f))

    # 1. every def under Defs/: the def's own name, label, class, graphic and texture fields (not just defName)
    def_hits, pipe_def_hits, desc_hits, ndefs = [], [], [], 0
    for p in files:
        rel = os.path.relpath(p, mod)
        if not rel.startswith("Defs") or not p.endswith(".xml"):
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            def_hits.append(f"{rel}: unparseable ({e})")
            continue
        for d in list(root):
            if not isinstance(d.tag, str):
                continue
            ndefs += 1
            dn = d.findtext("defName") or "?"
            fields = [("tag", d.tag)] + [("@" + k, v) for k, v in d.attrib.items()]
            for el in d.iter():
                if el is d or not isinstance(el.tag, str):
                    continue
                for k, v in el.attrib.items():
                    fields.append((el.tag + "@" + k, v))
                if el.text and el.text.strip() and len(list(el)) == 0:
                    fields.append((el.tag, el.text.strip()))
            for k, v in fields:
                prose = k in ("description", "label", "reportString", "jobString", "text") or k.endswith("Text") or k.endswith("Desc")
                if prose:
                    if WORD_HR.search(v):
                        desc_hits.append(f"{rel} {d.tag} {dn} <{k}>: {v[:80]}")
                    continue
                if HR.search(v) or HR.search(k):
                    def_hits.append(f"{rel} {d.tag} {dn} <{k}>={v[:80]}")
                elif PIPE.search(v):
                    pipe_def_hits.append(f"{rel} {d.tag} {dn} <{k}>={v[:80]}")
    row("NH_DEFS_NO_HOSE_OR_REEL_FIELD", BARS, "fixed", "FAIL" if def_hits else "PASS", ndefs,
        (f"{len(def_hits)} def fields name a hose or reel: " + "; ".join(def_hits[:6])) if def_hits else
        f"{ndefs} defs under Defs/: no defName, class, graphic, texture path, comp or attribute names a hose or reel")
    row("NH_DEFS_NO_PIPE_FIELD", BARS, "fixed", "FAIL" if pipe_def_hits else "PASS", ndefs,
        (f"{len(pipe_def_hits)} non-prose def fields name a pipe: " + "; ".join(pipe_def_hits[:6])) if pipe_def_hits else
        f"{ndefs} defs: no non-prose field names a pipe")
    row("NH_DEFS_PROSE_MENTIONS", BARS, "info", "INFO", len(desc_hits),
        ("prose fields naming a hose/reel: " + "; ".join(desc_hits[:6])) if desc_hits else "no def label or description names a hose or reel")

    # 2. patches: an xpath or value that reaches a hose/reel/pipe def or texture
    patch_hits, npatch = [], 0
    for p in files:
        rel = os.path.relpath(p, mod)
        if not rel.startswith("Patches") or not p.endswith(".xml"):
            continue
        npatch += 1
        txt = re.sub(r"<!--.*?-->", "", open(p, encoding="utf-8").read(), flags=re.S)
        for ln in txt.splitlines():
            if HR.search(ln) or PIPE.search(ln):
                patch_hits.append(f"{rel}: {ln.strip()[:100]}")
    row("NH_PATCHES_TOUCH_NO_HOSE", BARS, "fixed", "FAIL" if patch_hits else "PASS", npatch,
        ("patch lines naming a hose/reel/pipe: " + "; ".join(patch_hits[:6])) if patch_hits else f"{npatch} patch files: none names a hose, reel or pipe outside comments")

    # 3. textures: every folder and file name under Textures/ (the false pass the bar names: a texture folder)
    tex = [os.path.relpath(p, mod) for p in files if os.path.relpath(p, mod).startswith("Textures")]
    tex_hits = [t for t in tex if HR.search(t) or PIPE.search(t)]
    row("NH_TEXTURES_NO_HOSE_FOLDER_OR_FILE", BARS, "fixed", "FAIL" if tex_hits else "PASS", len(tex),
        ("texture paths naming a hose/reel/pipe: " + "; ".join(tex_hits[:6])) if tex_hits else f"{len(tex)} texture files: no folder or file name holds hose, reel or pipe")

    # 4. C#: type declarations, texture-path and defName literals
    cs_files = [p for p in files if p.endswith(".cs")]
    type_hits, texlit_hits, deflit_hits, pipe_types, ui_hits = [], [], [], [], []
    for p in cs_files:
        rel = os.path.relpath(p, mod)
        src = open(p, encoding="utf-8-sig").read()
        code = strip_comments(src)
        for m in re.finditer(r"\b(class|struct|enum|interface|record)\s+(\w+)", code):
            if HR.search(m.group(2)):
                type_hits.append(f"{rel}: {m.group(1)} {m.group(2)}")
            elif PIPE.search(m.group(2)):
                pipe_types.append(f"{rel}: {m.group(1)} {m.group(2)}")
        for m in re.finditer(r"\b(?:public|internal|private)?\s*static\s+ThingDef\s+(\w+)", code):
            if HR.search(m.group(1)) or PIPE.search(m.group(1)):
                deflit_hits.append(f"{rel}: DefOf field {m.group(1)}")
        for lit in literals(src):
            if "/" in lit and " " not in lit and (HR.search(lit) or PIPE.search(lit)):
                texlit_hits.append(f"{rel}: \"{lit[:90]}\"")
            elif re.fullmatch(r"(RM|RSW|RUT)_\w+", lit) and (HR.search(lit) or PIPE.search(lit)):
                deflit_hits.append(f"{rel}: \"{lit}\"")
            elif " " in lit and re.search(r"(?i)\b(flexible|drawn|draws?)\b.*\b(pipes?|hoses?)\b|\b(pipes?|hoses?)\b.*\b(drawn|draws?)\b", lit):
                ui_hits.append(f"{rel}: \"{lit[:110]}\"")
    row("NH_SOURCE_NO_HOSE_OR_REEL_TYPE", BARS, "fixed", "FAIL" if type_hits else "PASS", len(cs_files),
        ("types named for a hose/reel: " + "; ".join(type_hits[:6])) if type_hits else f"{len(cs_files)} C# files (SelfTest excluded): no class, struct, enum or interface named for a hose or reel")
    row("NH_SOURCE_NO_HOSE_TEXTURE_OR_DEF_LITERAL", BARS, "fixed", "FAIL" if (texlit_hits or deflit_hits) else "PASS", len(cs_files),
        ("path or defName literals naming a hose/reel/pipe: " + "; ".join((texlit_hits + deflit_hits)[:6])) if (texlit_hits or deflit_hits) else
        "no string literal that is a texture path or an RM_/RSW_/RUT_ defName names a hose, reel or pipe, and no ThingDef DefOf field does")
    row("NH_SOURCE_NO_TEXT_SAYING_GSS_DRAWS_PIPES", BARS, "fixed", "FAIL" if ui_hits else "PASS", len(cs_files),
        ("player-facing text says this mod draws pipes or hoses: " + "; ".join(ui_hits[:4])) if ui_hits else "no player-facing string says the mod draws pipes or hoses")

    # 5. what ships: the compiled DLL's identifier and literal heaps
    dll = os.path.join(mod, "Assemblies", "RimMandrakeGimmeSomeSlack.dll")
    if os.path.exists(dll):
        b = open(dll, "rb").read()
        ids = set(m.group(0).decode() for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_`]{2,}", b))
        us = set(m.group(0).decode("utf-16-le") for m in re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", b))
        idh = sorted(i for i in ids if HR.search(i) and i not in ("FireHosesMod",))
        ush = sorted(u for u in us if WORD_HR.search(u) and "FlowWorks" not in u and "port" not in u)
        row("NH_SHIPPED_DLL_NO_HOSE_SYMBOL", BARS, "fixed", "FAIL" if (idh or ush) else "PASS", len(ids) + len(us),
            ("shipped DLL holds hose/reel symbols or strings: " + "; ".join((idh + ush)[:8])) if (idh or ush) else
            f"shipped Assemblies DLL: {len(ids)} identifiers and {len(us)} UTF-16 literals, none names a hose or reel (allowed: the legacy-name map's 'FireHosesMod', strings naming FlowWorks or a port)")
    else:
        row("NH_SHIPPED_DLL_NO_HOSE_SYMBOL", BARS, "fixed", "UNSETTLED", 0, "no shipped DLL at " + dll)

    # 6. pipe drawing that the bar's words ("no ... pipe is drawn by this mod") reach: overhead pipe-pole spans
    pipe_draw = []
    for p in cs_files:
        rel = os.path.relpath(p, mod)
        code = strip_comments(open(p, encoding="utf-8-sig").read())
        for k in ("AerialLineKind.Pipe", "PipeMats(", "Link pipe span"):
            if k in code:
                pipe_draw.append(f"{rel}: {k}")
    row("NH_PIPE_POLE_SPANS_DRAWN_BY_GSS_CODE", BARS + ["pipe_pole_switch"], "info", "INFO", len(pipe_draw),
        ("GSS code draws and links overhead pipe-pole spans (the FlowWorks pipe poles ride GSS's line engine): " + "; ".join(sorted(set(pipe_draw))[:8]) +
         "; the sheet says 'No hose, reel or pipe is drawn by this mod', the oracle names only hoses and reels, and the record has a pipe_pole_switch bar, so the words and the inventory disagree")
        if pipe_draw else "no pipe-span drawing in GSS code")

    for r in rows:
        print(json.dumps(r))
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)


if __name__ == "__main__":
    main()
