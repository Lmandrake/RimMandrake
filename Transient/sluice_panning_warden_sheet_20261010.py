#!/usr/bin/env python3
"""Review sheet: SluiceBox, PanningSpot, Sluice door (menu icon + mover), Thrummel Warden renders.
Usage: python3 sluice_panning_warden_sheet_20261010.py <repo_root>   (run from the repo; reads src/ there)
Writes Transient/sluice_panning_warden_sheet_20261010.html + _img/. Installs nothing, writes NO decisions."""
import json, os, sys, shutil, html, glob
R = sys.argv[1]; AP = "/mnt/d/Luke/dev/_artpipe"; N = "sluice_panning_warden_sheet_20261010"
T = os.path.join(R, "Transient"); IMG = os.path.join(T, N + "_img"); os.makedirs(IMG, exist_ok=True)
e = html.escape
def cp(src, name):
    shutil.copyfile(src, os.path.join(IMG, name)); return N + "_img/" + name
def job(i):
    j = json.load(open(f"{AP}/done/{i}.json")); m = json.load(open(f"{AP}/done/{i}.manifest.json"))
    return j, m, cp(f"{AP}/_artsrc/{i}/{i}.png", i + ".png")
def facts(m):
    return f"facts {m.get('facts')} {m.get('facts_findings') or ''}; validator {m.get('validator')}; canon_check {(m.get('canon_check') or {}).get('status')}; {m.get('width')}x{m.get('height')}"
FW = "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks"
TS = "src/RimMandrake/TheSump/Textures/Things/Pawn/Animal/RM_ThrummelWarden/RM_ThrummelWarden"
rows = []
def add(title, defn, item, olds, news, canon, note=""):
    rows.append(dict(title=title, defn=defn, item=item, olds=olds, news=news, canon=canon, note=note))
def newl(i, label):
    j, m, img = job(i); return dict(label=label, img=img, facts=facts(m), prompt=j.get("prompt", ""), style=j.get("style_notes", ""), install=j.get("install_to") or j.get("target_texpath", ""))
NOC = "No canon entry exists for this subject (design/RimStarWars/canon_references has none; artpipe canon_check skipped: no canon entry and no owner note), so there is no Must show list."
add("Sluice box (river bank, 1x2)", "RM_SluiceBox", "FLOWWORKS_QUARRY_DIGGING_1",
    [dict(label="current: borrowed weir texture RM_BankWeir (drawSize 2.2)", img=cp(f"{R}/{FW}/Rivers/RM_BankWeir.png", "old_bankweir.png"))],
    [newl("RM_SluiceBox_v1", "NEW RM_SluiceBox_v1 (256x400)")], NOC)
add("Panning spot (1x1 marker)", "RM_PanningSpot", "FLOWWORKS_QUARRY_DIGGING_1",
    [dict(label="current: borrowed vanilla Things/Building/Misc/MeditationSpot (Core texture, packed in the game's assets, not in the repo, so not shown)", img=None)],
    [newl("RM_PanningSpot_v1", "NEW RM_PanningSpot_v1")], NOC)
add("Sluice gate door: menu icon", "RM_Sluice", "FLOWWORKS_DOOR_FAMILY_1",
    [dict(label="current uiIconPath Canals/RM_Sluice", img=cp(f"{R}/{FW}/Canals/RM_Sluice.png", "old_sluice.png"))],
    [newl("RM_Sluice_MenuIcon_v1", "NEW RM_Sluice_MenuIcon_v1 (128)")], NOC)
add("Sluice gate door: mover panel", "RM_Sluice", "FLOWWORKS_DOOR_FAMILY_1",
    [dict(label="current graphic Canals/RM_Sluice", img=cp(f"{R}/{FW}/Canals/RM_Sluice.png", "old_sluice2.png"))],
    [newl("RM_Sluice_Mover_v1", "NEW RM_Sluice_Mover_v1 (slides and mirrors; symmetric)")], NOC)
for f in ("south", "east", "north"):
    add(f"Thrummel Warden, {f}", "RM_ThrummelWarden", "SUMP_FAUNA_ROSTER_1 / BIOME_FLORAFAUNA_ART_REVIEW_1",
        [dict(label=f"current in src: RM_ThrummelWarden_{f}", img=cp(f"{R}/{TS}_{f}.png", f"old_warden_{f}.png"))],
        [newl(f"RM_ThrummelWarden_{f}", f"NEW A: RM_ThrummelWarden_{f} (2026-09-26 roster render)"),
         newl(f"thesump_ThrummelWarden_v2_{f}", f"NEW B: thesump_ThrummelWarden_v2_{f} (2026-10-06, owner note: match the thrummels)")],
        NOC, "Two candidates per facing: A and B are different jobs for the same def; the sheet makes no choice between them.")
def fig(o, big=False):
    if not o.get("img"): return f'<figure><div class="none">{e(o["label"])}</div></figure>'
    return f'<figure><img class="{"big" if big else ""}" src="{o["img"]}"><figcaption>{e(o["label"])}</figcaption></figure>'
cards = []
for r in rows:
    nw = "".join(fig(n, True) + f'<p class="f">{e(n["facts"])}</p><details><summary>prompt and notes</summary><p>{e(n["style"])}</p><p>{e(n["prompt"])}</p><p>install target (not installed): {e(n["install"])}</p></details>' for n in r["news"])
    cards.append(f'<section class="row"><h3>{e(r["title"])} <small>{e(r["defn"])} / {e(r["item"])}</small></h3><div class="pair"><div class="col"><h4>CURRENT in game</h4>{"".join(fig(o) for o in r["olds"])}</div><div class="col"><h4>NEW render(s)</h4>{nw}</div></div><p class="canon">{e(r["canon"])} {e(r["note"])}</p></section>')
page = f'''<!doctype html><meta charset="utf-8"><title>Sluice, panning spot, Thrummel Warden: art review sheet</title>
<style>body{{background:#1e150f;color:#e8d8c0;font:15px/1.4 system-ui,sans-serif;margin:0;padding:16px}}h1{{color:#f0c987}}h3{{margin:0 0 6px;color:#f0c987}}h3 small{{color:#a8957a;font-weight:normal;font-size:12px}}h4{{margin:4px 0;color:#c9b08a;font-size:13px}}
.row{{background:#2a1d14;border:1px solid #4a3524;border-radius:8px;padding:12px;margin:12px 0}}.pair{{display:flex;gap:28px;flex-wrap:wrap}}.col{{min-width:200px}}figure{{display:inline-block;margin:4px 10px 4px 0;text-align:center;vertical-align:top}}
img{{width:192px;height:192px;object-fit:contain;background:repeating-conic-gradient(#3a2a1c 0 25%,#2e2116 0 50%) 0 0/16px 16px;border:1px solid #4a3524}}img.big{{width:256px;height:256px}}
figcaption{{font-size:11px;color:#a8957a;max-width:260px}}.canon,.f{{color:#c9b08a;font-size:13px;margin:4px 0}}.none{{color:#c08060;width:192px;font-size:12px;border:1px dashed #6a4a30;padding:8px}}details{{font-size:12px;color:#a8957a}}</style>
<h1>Sluice box, panning spot, sluice door, Thrummel Warden ({len(rows)} rows)</h1>
<p class="canon">Review only. Nothing installed, no decisions written. Current = what ships in src/ now; new = artpipe renders in the state dir.</p>{"".join(cards)}'''
open(os.path.join(T, N + ".html"), "w").write(page); print(len(rows), "rows")
