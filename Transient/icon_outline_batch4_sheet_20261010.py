#!/usr/bin/env python3
"""Contact/review sheet: ICON_OUTLINE_REPAINT_1 batch 4 + Warden Mother aged east/north.
Usage: python3 icon_outline_batch4_sheet_20261010.py <repo_root_for_output> [src_root]
Reads job manifests from the artpipe state dir, old art from src_root (default /home/mandrake/rm/foundry).
Writes Transient/icon_outline_batch4_sheet_20261010.html + _img/. Writes NO decisions, installs nothing."""
import json, glob, os, sys, shutil, html
OUT = sys.argv[1]; SRC = sys.argv[2] if len(sys.argv) > 2 else "/home/mandrake/rm/foundry"
AP = "/mnt/d/Luke/dev/_artpipe"
T = os.path.join(OUT, "Transient"); IMG = os.path.join(T, "icon_outline_batch4_sheet_20261010_img"); os.makedirs(IMG, exist_ok=True)
CANON = os.path.join(SRC, "design/RimStarWars/canon_references")
canon_names = [os.path.basename(p)[:-3].lower() for p in glob.glob(CANON + "/*.md")] if os.path.isdir(CANON) else []

def cp(src, name):
    d = os.path.join(IMG, name); shutil.copyfile(src, d); return "icon_outline_batch4_sheet_20261010_img/" + name

def old_art(tp, defname):
    c = sorted(glob.glob(f"{SRC}/src/**/Textures/{tp}*.png", recursive=True))
    c = [p for p in c if not p.endswith(("_southm.png","_eastm.png","_northm.png","_m.png"))]
    if not c and defname == "RM_Deepfire":
        c = sorted(glob.glob(f"{SRC}/src/**/Textures/**/RM_Deepfire/**/RM_Deepfire_a.png", recursive=True))
    return c

def canon_for(defname):
    key = defname.split("_")[-1].lower()
    hits = [n for n in canon_names if key and key in n]
    return hits

rows = []
for p in sorted(glob.glob(AP + "/done/*_v3_nooutline.json")):
    j = json.load(open(p))
    if j.get("rimflow_item_id") != "ICON_OUTLINE_REPAINT_1" or "batch 4" not in j.get("style_notes", ""): continue
    i = j["id"]; src = f"{AP}/_artsrc/{i}/{i}.png"
    if not os.path.exists(src): continue
    m = json.load(open(f"{AP}/done/{i}.manifest.json"))
    olds = old_art(j["target_texpath"], j["target_def"])
    rows.append(dict(id=i, defn=j["target_def"], tex=j["target_texpath"], new=cp(src, i + ".png"),
        old=[cp(o, f"old_{i}_{n}.png") for n, o in enumerate(olds)], oldp=[os.path.relpath(o, SRC) for o in olds],
        prompt=j["prompt"], facts=m.get("facts"), canon=canon_for(j["target_def"]), size=f"{m.get('width')}x{m.get('height')}"))
rows.sort(key=lambda r: r["id"].lower())

wm = []
ref = f"{SRC}/src/RimMandrake/Miasma/Textures/Things/Pawn/Animal/Miasma/WardenMother"
for f in ("east", "north"):
    i = f"RM_WardenMother_Aged2_{f}"; src = f"{AP}/_artsrc/{i}/{i}.png"
    if not os.path.exists(src): continue
    j = json.load(open(f"{AP}/done/{i}.json")); m = json.load(open(f"{AP}/done/{i}.manifest.json"))
    wm.append(dict(id=i, facing=f, new=cp(src, i + ".png"), old=cp(f"{ref}/WardenMother_{f}.png", f"old_{i}.png"),
        oldp=f"src/RimMandrake/Miasma/Textures/Things/Pawn/Animal/Miasma/WardenMother/WardenMother_{f}.png", prompt=j["prompt"], facts=m.get("facts"), item=j["rimflow_item_id"], style=j.get("style_notes", "")))

e = html.escape
def imgs(r):
    if not r["old"]: return '<div class="none">no current texture found in src/ (new item or path differs)</div>'
    return "".join(f'<figure><img src="{o}"><figcaption>{e(p)}</figcaption></figure>' for o, p in zip(r["old"], r["oldp"]))
cards = []
for r in rows:
    cn = ("canon entry candidate(s): " + ", ".join(r["canon"]) + " (check its ## Must show)") if r["canon"] else "No canon entry for this subject."
    cards.append(f'''<section class="row" id="{e(r["id"])}"><h3>{e(r["defn"])} <small>{e(r["id"])} / {r["size"]} / facts {e(str(r["facts"]))}</small></h3>
<div class="pair"><div class="col"><h4>OLD / current in src (has outline)</h4>{imgs(r)}</div>
<div class="col"><h4>NEW (no outline)</h4><figure><img class="new" src="{r["new"]}"><figcaption>{e(r["tex"])}</figcaption></figure></div></div>
<p class="canon">{e(cn)}</p><details><summary>prompt</summary><p>{e(r["prompt"])}</p></details></section>''')
wcards = "".join(f'''<section class="row"><h3>RM_WardenMother aged, {w["facing"]} <small>{e(w["id"])} / item {e(w["item"])} / facts {e(str(w["facts"]))}</small></h3>
<div class="pair"><div class="col"><h4>OLD / current {w["facing"]} (healthy adult)</h4><figure><img class="big" src="{w["old"]}"><figcaption>{e(w["oldp"])}</figcaption></figure></div>
<div class="col"><h4>NEW aged variant</h4><figure><img class="big" src="{w["new"]}"></figure></div></div>
<p class="canon">No canon entry for this subject. Brief: {e(w["style"])}</p><details><summary>prompt</summary><p>{e(w["prompt"])}</p></details></section>''' for w in wm)
page = f'''<!doctype html><meta charset="utf-8"><title>Icon outline repaint batch 4 + Warden Mother aged: review sheet</title>
<style>body{{background:#1e150f;color:#e8d8c0;font:15px/1.4 system-ui,sans-serif;margin:0;padding:16px}}
h1{{color:#f0c987}}h3{{margin:0 0 6px;color:#f0c987}}h3 small{{color:#a8957a;font-weight:normal;font-size:12px}}h4{{margin:4px 0;color:#c9b08a;font-size:13px}}
.row{{background:#2a1d14;border:1px solid #4a3524;border-radius:8px;padding:12px;margin:12px 0}}
.pair{{display:flex;gap:24px;flex-wrap:wrap}}.col{{min-width:200px}}figure{{display:inline-block;margin:4px 10px 4px 0;text-align:center}}
img{{width:128px;height:128px;image-rendering:auto;background:repeating-conic-gradient(#3a2a1c 0 25%,#2e2116 0 50%) 0 0/16px 16px;border:1px solid #4a3524}}
img.new{{width:192px;height:192px}}img.big{{width:384px;height:384px}}figcaption{{font-size:10px;color:#a8957a;max-width:200px;word-break:break-all}}
.canon{{color:#c9b08a;font-size:13px;margin:6px 0}}.none{{color:#c08060}}details{{font-size:12px;color:#a8957a}}p.note{{color:#c9b08a}}</style>
<h1>Icon outline repaint, batch 4 ({len(rows)} items) + Warden Mother aged ({len(wm)} facings)</h1>
<p class="note">Review only. Nothing installed, no decisions written. Old = what is in src/ now; new = artpipe output (_artsrc). Gap Dakkra rest north/south was requeued and is not on this sheet.</p>
{"".join(cards)}<h2>RM_WardenMother aged variants (MIASMA_WARDEN_MOTHER_ART_1)</h2>{wcards}'''
open(os.path.join(T, "icon_outline_batch4_sheet_20261010.html"), "w").write(page)
print(len(rows), "icon rows;", len(wm), "warden rows;", sum(1 for r in rows if not r["old"]), "without old art")
