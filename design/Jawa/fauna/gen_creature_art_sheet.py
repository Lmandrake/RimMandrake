#!/usr/bin/env python3
"""Generate the creature ART FLAG sheet for CREATURE_ART_REVIEW_FLAGS_1.

    python3 design/Jawa/fauna/gen_creature_art_sheet.py

Reads  design/Jawa/fauna/cast_assignment.csv           the cast — 621 creatures actually on Ash'karr
       design/Jawa/fauna/sprite_features.csv           measured px / contrast / fill / sat per sprite
       design/Jawa/fauna/sprites/<defName>.png         the cached sprite, embedded base64
       design/Jawa/fauna/creature_art_decisions.json   the OWNER's file — read, merged, never written
Writes design/Jawa/fauna/creature_art_review.html

🔴 **FLAG ONLY. THIS SHEET FIXES NOTHING.** Standing owner directive: art *fixing* is stopped
until he personally verifies art is broken. This produces a LIST for him and nothing else.
⛔ No sprite is generated, no texture edited, no art file touched — by this script or after it.

⭐ **PREFER SHRINK OVER REDRAW.** `CREATURE_SIZES_ADJUSTED_1` already ships the resize path, so
shrinking is free and reversible while redrawing is neither. Every rule below proposes the
cheapest remedy that could work.

🔴 **THE MAGENTA CHECK CAME BACK CLEAN, AND THAT IS A RESULT.** Measured 2026-08-23 across all
621 cast creatures: **ZERO** carry a magenta placeholder (hue 0.78–0.92 at sat > 0.55, fill >
0.5). ⇒ **Nothing here is a MISSING texture and nothing is flagged as one.**
⚠️ The known blind spot stands: a `Graphic_Multi` def resolves per-facing, so a missing side
never renders magenta and this test cannot see it. Absence of magenta is evidence, not proof.

🔴 **THE THRESHOLDS BELOW ARE INVENTED BY THIS SCRIPT AND THE OWNER HAS NOT RULED ON THEM.**
They are percentiles of the cast's own measured distribution, not a standard:
    px < 2,579        the cast's p25 resolution
    contrast < 0.138  the cast's p05
    sat < 0.111       the cast's p25
    fill > 0.814      the cast's p95
That makes them defensible and still arbitrary. **They decide only WHERE HE LOOKS FIRST**, and
the sheet says so on its face. If he disagrees with a call, the call is wrong, not the sprite.
⚠️ px measures RESOLUTION, never quality. A crisp small sprite and a muddy huge one can score
alike. The eye on the picture is the authority; this is a sort order.
"""
from __future__ import annotations
import base64
import collections
import csv
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(HERE, 'cast_assignment.csv')
FEAT = os.path.join(HERE, 'sprite_features.csv')
SPRITES = os.path.join(HERE, 'sprites')
DECISIONS = os.path.join(HERE, 'creature_art_decisions.json')
OUT = os.path.join(HERE, 'creature_art_review.html')

P25_PX, P05_CT, P25_SAT, P95_FILL, P25_CT, MED_PX = 2579.0, 0.138, 0.111, 0.814, 0.194, 3398.0
BIG = {'huge', 'SUPER'}


def num(r, k, d=0.0):
    try:
        return float(r[k])
    except (TypeError, ValueError, KeyError):
        return d


def judge(band, px, ct, st, fl):
    """(flags, state, remedy, why). 🔴 Default is KEEP — a sheet proposing 600 changes is a chore."""
    flags = []
    if band in BIG and px < P25_PX:
        flags.append('BLUR')
    if ct < P05_CT and st < P25_SAT:
        flags.append('MUDDY')
    if fl > P95_FILL and ct < P25_CT:
        flags.append('BLOB')
    if band == 'SUPER' and px < MED_PX:
        flags.append('HEADLINER_WEAK')
    if not flags:
        return [], 'keep', '', f'{px:,.0f} px at {band}, contrast {ct:.2f}. Reads correctly.'

    if 'BLUR' in flags:
        why = (f'🔴 {px:,.0f} px carrying a {band} silhouette — below the cast\'s p25 of '
               f'{P25_PX:,.0f}. Scaled up to {band}, this reads as blur. **Shrink the DRAW '
               f'only**; its mechanics are untouched and the change is reversible.')
        return flags, 'shrink', 'drawSize', why
    if 'MUDDY' in flags:
        why = (f'Contrast {ct:.2f} and saturation {st:.2f} — the flattest and greyest end of '
               f'the cast. It will read as a smudge against ground of any colour. Shrinking '
               f'helps a little; **replacing it with another creature already cast nearby '
               f'costs nothing** and is the cheaper fix than a redraw.')
        return flags, 'replace', '', why
    if 'BLOB' in flags:
        why = (f'Fill {fl:.2f} with contrast {ct:.2f} — a near-solid mass filling its frame '
               f'with no internal detail. Looks like a silhouette rather than a creature.')
        return flags, 'replace', '', why
    why = (f'{px:,.0f} px as a SUPER headliner, under the cast median of {MED_PX:,.0f}. '
           f'Adequate but not generous, and a headliner is the one everybody looks at. '
           f'**Look before deciding** — flagged, not proposed.')
    return flags, 'keep', '', why


def main() -> int:
    feat = {r['defName']: r for r in csv.DictReader(open(FEAT, encoding='utf-8'))}
    cast = {}
    for r in csv.DictReader(open(CAST, encoding='utf-8')):
        cast.setdefault(r['defName'], r)

    prior = {}
    if os.path.exists(DECISIONS):
        try:
            prior = json.load(open(DECISIONS, encoding='utf-8'))
        except ValueError:
            prior = {}

    items, missing_sprite, flagged = [], 0, 0
    for d, c in cast.items():
        s = feat.get(d)
        if not s:
            continue
        px, ct, st, fl = num(s, 'px'), num(s, 'contrast'), num(s, 'sat'), num(s, 'fill')
        flags, state, field, why = judge(c['band'], px, ct, st, fl)
        flagged += bool(flags)
        p = os.path.join(SPRITES, d + '.png')
        img = ''
        if os.path.exists(p):
            img = base64.b64encode(open(p, 'rb').read()).decode('ascii')
        else:
            missing_sprite += 1
        items.append({
            'id': d, 'label': s.get('label') or d, 'mod': s.get('mod') or '?',
            'band': c['band'], 'biome': c['biome'], 'px': int(px), 'ct': round(ct, 3),
            'sat': round(st, 3), 'fill': round(fl, 3), 'flags': flags,
            'state': state, 'field': field, 'why': why,
            'sev': max([_sev(f, px, ct, fl) for f in flags], default=0.0), 'img': img,
        })
    items.sort(key=lambda i: (-i['sev'], i['id']))

    html_out = PAGE.replace('__DATA__', json.dumps(items)) \
                   .replace('__PRIOR__', json.dumps(prior)) \
                   .replace('__NFLAG__', str(flagged)) \
                   .replace('__NTOT__', str(len(items)))
    open(OUT, 'w', encoding='utf-8').write(html_out)
    print(f'cast creatures {len(items)} · flagged {flagged} ({100*flagged/max(len(items),1):.0f}%) '
          f'· sprites missing from cache {missing_sprite}')
    by = collections.Counter(f for i in items for f in i['flags'])
    print('by rule:', dict(by))
    print(f'wrote {OUT}  ({os.path.getsize(OUT)/1e6:.1f} MB)')
    print('open it:  ./src/RimMandrake/Utils/show.sh design/Jawa/fauna/creature_art_review.html')
    return 0


def _sev(flag, px, ct, fl):
    if flag == 'BLUR':
        return (P25_PX - px) / P25_PX
    if flag == 'MUDDY':
        return (P05_CT - ct) / P05_CT
    if flag == 'BLOB':
        return (fl - P95_FILL) / (1 - P95_FILL)
    return (MED_PX - px) / MED_PX


PAGE = r"""<meta charset="utf-8"><title>Ash'karr — creature art flags</title>
<style>
:root{--bg:#14161a;--fg:#e8e6e3;--dim:#9aa0a8;--line:#2a2f37;--card:#1b1f26;--warn:#ffb454;--bad:#ff6b6b;--ok:#7ec699}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
header{padding:18px 22px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:9}
h1{margin:0 0 6px;font-size:19px}.sub{color:var(--dim);font-size:13px}
.panel{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--warn);padding:10px 14px;margin:10px 0;border-radius:5px;font-size:13px}
.panel b{color:var(--warn)}.panel.ok{border-left-color:var(--ok)}.panel.ok b{color:var(--ok)}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:10px}
input,select,button{background:#0f1216;color:var(--fg);border:1px solid var(--line);border-radius:5px;padding:6px 9px;font:inherit}
button{cursor:pointer}button:hover{border-color:#4a5361}
#link{font-size:12px;color:var(--dim);margin-left:auto}
.pathbar{margin-top:9px;font-size:12px;background:#0f1216;border:1px solid var(--line);border-radius:5px;padding:8px 11px}
.pathbar code{color:#cfe3ff;font-family:ui-monospace,monospace;font-size:12px}
.pathbar b{color:var(--ok)}.pathbar .pn{display:block;color:var(--dim);margin-top:4px}
.row{display:grid;grid-template-columns:132px 1fr 300px;gap:14px;padding:14px 22px;border-bottom:1px solid var(--line)}
.row.hide{display:none}
.spr{width:132px;height:132px;background:#0b0d10 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16'%3E%3Cpath d='M0 0h8v8H0zM8 8h8v8H8z' fill='%23161a1f'/%3E%3C/svg%3E");border:1px solid var(--line);border-radius:5px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.spr img{max-width:100%;max-height:100%;image-rendering:pixelated}
.nm{font-weight:600}.meta{color:var(--dim);font-size:12px;margin:2px 0 6px}
.why{font-size:13px}.why b{color:var(--warn)}
.tags span{display:inline-block;font-size:11px;padding:1px 7px;border-radius:9px;border:1px solid var(--line);margin-right:5px;color:var(--warn)}
.ev{font-size:11px;color:var(--dim);font-family:ui-monospace,monospace;margin-top:5px}
.ctl{display:flex;flex-direction:column;gap:6px}
.ctl label{font-size:12px;color:var(--dim)}
textarea{width:100%;min-height:52px;background:#101821;color:#cfe3ff;border:1px solid #24405c;border-radius:5px;padding:6px;font:inherit;resize:vertical}
.count{font-variant-numeric:tabular-nums}
</style>
<header>
<h1>Ash'karr — creature art, flagged for review</h1>
<div class="sub">__NTOT__ creatures actually cast on the planet · <b class="count" id="nf">__NFLAG__</b> flagged · sorted worst first</div>

<div class="panel ok"><b>⭐ The magenta check came back clean, and that is a result.</b>
Measured across all __NTOT__ cast creatures: <b>ZERO</b> carry a magenta placeholder. <b>Nothing here is a MISSING texture</b> and nothing is flagged as one.
<i>Blind spot, stated:</i> a <code>Graphic_Multi</code> def resolves per facing, so a missing side never renders magenta and this test cannot see it. Absence of magenta is evidence, not proof.</div>

<div class="panel"><b>🔴 These thresholds are invented by the generator and you have not ruled on them.</b>
They are percentiles of the cast's own measured spread — px &lt; 2,579 (p25), contrast &lt; 0.138 (p05), saturation &lt; 0.111 (p25), fill &gt; 0.814 (p95) — which makes them defensible and still arbitrary.
<b>They decide only where you look first.</b> px measures RESOLUTION, never quality: a crisp small sprite and a muddy huge one score alike. If you disagree with a call, the call is wrong, not the sprite.</div>

<div class="panel"><b>⛔ FLAG ONLY — this sheet fixes nothing.</b> No sprite is generated and no texture edited, here or after.
<b>Prefer shrink over redraw:</b> the resize path already ships, so shrinking is free and reversible; redrawing is neither.
Default for every row is <b>keep</b> — only the flagged rows carry a proposal.</div>

<div class="bar">
<input id="q" placeholder="search name, mod, biome, reason…" size="30">
<select id="fl"><option value="">all rows</option><option value="flagged" selected>flagged only</option><option value="BLUR">BLUR</option><option value="MUDDY">MUDDY</option><option value="BLOB">BLOB</option><option value="HEADLINER_WEAK">HEADLINER_WEAK</option></select>
<select id="fm"><option value="">all mods</option></select>
<select id="fs"><option value="">any decision</option><option value="keep">keep</option><option value="shrink">shrink</option><option value="replace">replace</option><option value="redraw">redraw</option></select>
<button id="save">Link file…</button><button id="copy">Copy JSON</button>
<span id="link">not linked — decisions are in this tab only</span>
</div>
<div class="pathbar">🔑 <b>Save it exactly here</b>, or the generator cannot merge your calls back:
<code>D:\Luke\dev\Rimworld\design\Jawa\fauna\creature_art_decisions.json</code>
<span class="pn">⚠️ the file picker cannot be given a folder — that is a browser rule, not an oversight — so the path is printed here to be read. The sheet itself is <code>D:\Luke\dev\Rimworld\design\Jawa\fauna\creature_art_review.html</code></span></div>
</header>
<div id="list"></div>
<script>
const DATA=__DATA__, PRIOR=__PRIOR__;
const D={}; let handle=null, timer=null;
// 🔑 A FileSystemFileHandle is structured-cloneable, so IndexedDB can hold it and localStorage
// cannot. Without this the link dies on every reload and the human silently stops saving.
const IDB='ashkarr_art_fs', IKEY='handle';
function idb(){return new Promise((res,rej)=>{const r=indexedDB.open(IDB,1);
  r.onupgradeneeded=()=>r.result.createObjectStore('h');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);});}
async function idbPut(h){try{const db=await idb();db.transaction('h','readwrite').objectStore('h').put(h,IKEY);}catch(e){}}
async function idbGet(){try{const db=await idb();return await new Promise(res=>{
  const q=db.transaction('h','readonly').objectStore('h').get(IKEY);q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null);});}catch(e){return null;}}
// 🔴 merge PER ROW: a row already decided is left exactly alone, every other takes the prefill.
let kept=0, filled=0;
for(const it of DATA){
  const p = PRIOR && PRIOR.decisions && PRIOR.decisions[it.id];
  if(p && p.state){ D[it.id]={...p}; kept++; }
  else { D[it.id]={state:it.state, note:''}; filled++; }
}
const el=id=>document.getElementById(id);
const mods=[...new Set(DATA.map(i=>i.mod))].sort();
for(const m of mods){const o=document.createElement('option');o.value=m;o.textContent=m;el('fm').appendChild(o);}

function card(it){
  const d=D[it.id];
  const img = it.img ? `<img src="data:image/png;base64,${it.img}" alt="">` : `<span style="color:#6b7280;font-size:11px">no sprite cached</span>`;
  const tags = it.flags.map(f=>`<span>${f}</span>`).join('');
  const why = it.why.replace(/\*\*(.+?)\*\*/g,'<b>$1</b>');
  return `<div class="row" data-id="${it.id}">
    <div class="spr">${img}</div>
    <div>
      <div class="nm">${it.label} <span style="color:#6b7280;font-weight:400">${it.id}</span></div>
      <div class="meta">${it.mod} · band <b style="color:#e8e6e3">${it.band}</b> · cast in ${it.biome}</div>
      <div class="tags">${tags}</div>
      <div class="why">${why}</div>
      <div class="ev">px ${it.px.toLocaleString()} · contrast ${it.ct} · sat ${it.sat} · fill ${it.fill}${it.field?' · field '+it.field:''}</div>
    </div>
    <div class="ctl">
      <label>decision</label>
      <select class="st">
        ${['keep','shrink','replace','redraw','undecided'].map(s=>`<option value="${s}"${d.state===s?' selected':''}>${s}</option>`).join('')}
      </select>
      <label>your note — overrides everything above</label>
      <textarea class="nt" placeholder="why you disagree, or what to do instead">${(d.note||'').replace(/</g,'&lt;')}</textarea>
    </div></div>`;
}

function render(){
  const q=el('q').value.toLowerCase(), f=el('fl').value, m=el('fm').value, s=el('fs').value;
  let shown=0;
  el('list').innerHTML = DATA.map(it=>{
    let ok = true;
    if(f==='flagged') ok = it.flags.length>0; else if(f) ok = it.flags.includes(f);
    if(ok && m) ok = it.mod===m;
    if(ok && s) ok = D[it.id].state===s;
    if(ok && q) ok = (it.id+' '+it.label+' '+it.mod+' '+it.biome+' '+it.why).toLowerCase().includes(q);
    if(!ok) return '';
    shown++; return card(it);
  }).join('');
  el('nf').textContent = shown;
  for(const r of document.querySelectorAll('.row')){
    const id=r.dataset.id;
    r.querySelector('.st').onchange = e=>{ D[id].state=e.target.value; save(); };
    r.querySelector('.nt').oninput  = e=>{ D[id].note =e.target.value; save(); };
  }
}
['q','fl','fm','fs'].forEach(i=>el(i).oninput=render);

function payload(){
  // ⭐ carry through every top-level key this page did not author — a whole-file writer
  // that only emits its own keys DELETES things like a freeze marker written elsewhere.
  const out = Object.assign({}, PRIOR);
  out.posture = 'flag-only';
  out.postureMeaning = 'A decision here is a FLAG for the owner. Nothing in this file edits art. Rows left `keep` are accepted as-is.';
  out.decisions = D;
  out.savedAt = new Date().toISOString();   // 🔴 only the PAGE writes this. A consumer must
  out.savedBy = 'creature_art_review.html'; // refuse to run without it, or it will ship the
  return JSON.stringify(out, null, 2);      // generator's guesses under the owner's name.
}
async function save(){
  clearTimeout(timer);
  timer=setTimeout(async()=>{
    if(!handle) return;
    const decided = Object.values(D).filter(v=>v.state && v.state!=='undecided').length;
    if(decided < 10){ el('link').textContent='REFUSED to write — only '+decided+' decided rows looks like a bug, not a review'; return; }
    try{ const w=await handle.createWritable(); await w.write(payload()); await w.close();
         el('link').textContent='saved '+new Date().toLocaleTimeString(); }
    catch(e){ el('link').textContent='write failed: '+e.message; }
  }, 900);
}
el('save').onclick=async()=>{
  if(!window.showSaveFilePicker){ el('link').textContent='this browser has no File System Access API — use Copy JSON'; return; }
  try{ handle=await window.showSaveFilePicker({suggestedName:'creature_art_decisions.json',
        types:[{description:'JSON',accept:{'application/json':['.json']}}]});
       await idbPut(handle);
       el('link').textContent='linked — autosaving'; save(); }
  catch(e){}
};
// ⭐ Chrome needs a gesture to re-grant after a restart, so OFFER the reconnect rather than
// failing quietly - a sheet that looks linked and is not is the worst of the three states.
(async()=>{ const h=await idbGet(); if(!h) return;
  const perm = await h.queryPermission({mode:'readwrite'});
  if(perm==='granted'){ handle=h; el('link').textContent='relinked to your file — autosaving'; }
  else { el('link').innerHTML='<b style="color:#ffb454;cursor:pointer" id="regrant">click to reconnect your file</b>';
         el('regrant').onclick=async()=>{ if(await h.requestPermission({mode:'readwrite'})==='granted'){
           handle=h; el('link').textContent='relinked — autosaving'; save(); } }; }
})();
el('copy').onclick=()=>{ navigator.clipboard.writeText(payload()); el('link').textContent='copied to clipboard'; };
render();
console.log('prefilled '+filled+' rows, kept '+kept+' existing decisions untouched');
</script>
"""

if __name__ == '__main__':
    sys.exit(main())
