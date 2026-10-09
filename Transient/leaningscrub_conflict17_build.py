#!/usr/bin/env python3
"""Builds the 17-picture Delete/Keep pick page (Transient/leaningscrub_conflict17_2026-10-08.*). Deletes nothing."""
import glob, json, shutil, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench"); T = R / "Transient"
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L
STEM = "leaningscrub_conflict17_2026-10-08"
IMG = T / (STEM + "_img"); IMG.mkdir(exist_ok=True)
dec = json.load(open(T / "biome_ffar/leaningscrub_sheet_2026-10-05.decisions.json"))["decisions"]
snap = json.load(open(R / "infrastructure/state/art/sheets/leaningscrub_sheet_2026-10-05.snapshot.json"))["rows"]
idx = L.Index()
CANON = R / "design/RimStarWars/canon_references"
def must(name):
    out, f = [], False
    for ln in (CANON / name / "description.md").read_text().splitlines():
        if ln.startswith("## Must show"): f = True; continue
        if ln.startswith("## "): f = False
        if f and ln.strip().startswith("- "): out.append(ln.strip()[2:].replace("[ ] ", ""))
    return out
def cimgs(name):
    res = []
    for p in sorted((CANON / name).iterdir()):
        if p.suffix.lower() in (".png", ".jpg", ".webp") and "donor_current" not in p.name:
            d = IMG / f"canon_{name}_{p.name}"; shutil.copy(p, d); res.append(d.name)
    return res[:4]
def put(sha):
    p = IMG / f"{sha[:16]}.png"
    if not p.exists(): p.write_bytes(L.store_get(sha))
    return p.name
items = []
for row in ["RSW_Eopie", "RSW_Lothcat", "RSW_Scurrier", "RSW_Strill"]:
    cr = row[4:].lower(); cols = snap[row]["columns"]
    inv = {sha: (let, f) for let, c in cols.items() for f, sha in c.items()}
    for sha in dec[row].get("purge", []):
        if idx.is_purged(sha): continue
        live = idx.live_anywhere(sha); kept = idx.protected(sha)
        if not (live or kept): continue
        let, face = inv[sha]; g = snap[row]["graphic_of"].get(let)
        ref = None
        if not live:
            for l2, c in cols.items():
                s2 = c.get(face)
                if s2 and idx.live_anywhere(s2) and (ref is None or snap[row]["graphic_of"].get(l2) == g):
                    ref = (l2, s2)
        else:
            ref = (let, sha)
        marks = ["owner ✕ delete (leaningscrub sheet 2026-10-05)"]
        if kept: marks.append("owner KEEP on file (" + Path(kept[0].get("via") or kept[0]["id"]).name + ")")
        if live: marks.append("live in game")
        items.append({"id": f"{row}/{sha[:12]}", "sha": sha, "group": row, "label": f"{row} · {face} · column {let}",
            "creature": row, "facing": face, "graphic": g, "colLabel": snap[row]["labels"].get(let, ""),
            "live": bool(live), "livePath": live[0] if live else None, "marks": marks,
            "img": put(sha), "refImg": put(ref[1]) if ref else None,
            "refLabel": (snap[row]["labels"].get(ref[0], "") + " — " + (idx.live_anywhere(ref[1]) or ["?"])[0]) if ref else "no live picture for this facing",
            "canon": cimgs(cr), "must": must(cr), "effect": ""})
assert len(items) == 17, len(items)
tpl = Path(glob.glob(str(Path.home() / ".claude/skills/review-sheets/assets/*template.html"))[0]).read_text()
cfg = {"sheetId": STEM, "title": "LeaningScrub: 17 pictures marked both ✕ and keep/live", "subtitle": "Delete or Keep, one row per picture",
 "briefHtml": "<p>You marked each of these 17 pictures ✕ (delete) on the LeaningScrub sheet, but each is also live in game or carries a keep from an earlier ruling, so nothing was purged. <b>Delete</b> permanently removes the picture and releases its keep. <b>Keep</b> leaves it as is. Nothing is deleted by this page; your choices are only recorded.</p><p>Pre-filled with nothing: every row is yours to pick. A LIVE picture that you delete leaves its slot with no art until a replacement is installed.</p>",
 "criterion": "Grouped by creature, not ranked. Each row shows the picture, what marks it carries, and the live art for the same facing beside it.",
 "invented": [], "posture": {"mode": "blacklist", "explain": "Default is KEEP: a row you leave empty is not deleted. Only rows you mark Delete are purged."},
 "options": [{"key": "delete", "label": "Delete", "hotkey": "1", "color": "#e06c6c", "counts": "out"},
             {"key": "keep", "label": "Keep", "hotkey": "2", "color": "#5ac37f", "counts": "in"}],
 "groupLabel": "creature", "media": False, "decisionsFile": STEM + ".decisions.json", "decisionsPath": "", "sheetPath": ""}
for it in items:
    it["prefill"] = "keep"; it["thumb"] = None; it["effect"] = ("LIVE in game and " if it["live"] else "") + "marked ✕ by you; " + ("keep on file" if any("KEEP" in m for m in it["marks"]) else "no keep")
tpl = tpl.replace('"sheetId": "demo_sheet"', "XX", 1)  # sanity: template carries the demo config
import re
tpl = re.sub(r'(<script id="CONFIG" type="application/json">).*?(</script>)', lambda m: m.group(1) + json.dumps(cfg, ensure_ascii=False) + m.group(2), tpl, count=1, flags=re.S) if False else tpl
a = tpl.index('<script id="CONFIG"'); b = tpl.index("</script>", a)
tpl = tpl[:a] + '<script id="CONFIG" type="application/json">\n' + json.dumps(cfg, ensure_ascii=False) + "\n" + tpl[b:]
a = tpl.index('<script id="ITEMS"'); b = tpl.index("</script>", a)
tpl = tpl[:a] + '<script id="ITEMS" type="application/json">\n' + json.dumps(items, ensure_ascii=False).replace("</", "<\\/") + "\n" + tpl[b:]
old = "  rec.decidedAt = new Date().toISOString();      // a human act: prefilled vs yours is countable"
assert old in tpl
tpl = tpl.replace(old, "  rec.purge = (key === 'delete') ? [it.sha] : []; rec.purgeTouched = true;   // art.py enact reads purge[]")
render = r"""<script id="RENDER">
window.itemBody = it => {
  const im = (src, cap, w) => `<div class="thumb" style="width:${w}px;height:${w}px;flex:none" data-zoom="${esc(src)}" data-cap="${esc(cap)}"><img src="${esc(src)}" alt="" style="width:100%;height:100%;object-fit:contain;image-rendering:pixelated;background:#222"></div>`;
  const imgs = it.canon.map(c => im(window.IMGDIR + c, 'canon reference', 110)).join('');
  return `<div style="display:flex;gap:14px;flex-wrap:wrap;margin:6px 0">
    <div><div class="effect">THIS picture (${esc(it.graphic||'')})</div>${im(window.IMGDIR + it.img, it.label, 256)}</div>
    <div><div class="effect">${it.live ? 'It IS the live art' : 'Live art, same facing'}</div>${it.refImg ? im(window.IMGDIR + it.refImg, it.refLabel, 256) : '<div class="effect">none live</div>'}<div class="effect" style="max-width:256px">${esc(it.refLabel)}</div></div>
  </div>
  <div class="marks"><span class="mark ${it.live ? 'contested' : 'absent'}">LIVE: ${it.live ? 'YES — ' + esc(it.livePath) : 'no'}</span>${it.marks.map(m => `<span class="mark absent">${esc(m)}</span>`).join('')}<span class="mark absent">${esc(it.colLabel)}</span></div>
  <div class="effect" style="margin-top:6px"><b>Canon references</b> (${esc(it.creature)})</div><div style="display:flex;gap:6px;flex-wrap:wrap">${imgs}</div>
  <div class="effect"><b>Must show:</b><ul style="margin:2px 0 0 18px;padding:0">${it.must.map(m => `<li>${esc(m)}</li>`).join('')}</ul></div>`;
};
window.IMGDIR = '""" + STEM + """_img/';
</script>
"""
a = tpl.index("<script>\n\"use strict\";")
tpl = tpl[:a] + render + tpl[a:]
(T / (STEM + ".html")).write_text(tpl)
dp = T / (STEM + ".decisions.json")
if not dp.exists() or not json.loads(dp.read_text()).get("savedBy"):
    dp.write_text(json.dumps({"posture": "blacklist", "criterion": cfg["criterion"], "sheetId": STEM,
        "reviewStatus": {"state": "prefill", "by": None, "at": None, "evidence": "generated; no human has picked"},
        "decisions": {i["id"]: {"decision": "keep", "prefill": "keep", "note": ""} for i in items}}, indent=2) + "\n")
print(len(items), "items;", sum(i["live"] for i in items), "live")
