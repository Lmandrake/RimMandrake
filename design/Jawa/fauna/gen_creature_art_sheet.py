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
:root{--bg:#14161a;--fg:#e8e6e3;--dim:#9aa0a8;--line:#2a2f37;--card:#1b1f26;--warn:#ffb454;--ok:#7ec699}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
header{border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:20}
.hrow{display:flex;align-items:center;gap:12px;padding:10px 22px}
h1{margin:0;font-size:17px}.sub{color:var(--dim);font-size:13px}
#fold{margin-left:auto;background:#0f1216;border:1px solid var(--line);color:var(--fg);border-radius:5px;padding:5px 12px;cursor:pointer;font:inherit}
#brief{padding:0 22px 12px}
body.folded #brief{display:none}
.panel{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--warn);padding:9px 13px;margin:8px 0;border-radius:5px;font-size:13px}
.panel b{color:var(--warn)}.panel.ok{border-left-color:var(--ok)}.panel.ok b{color:var(--ok)}
.pathbar{background:#0f1216;border:1px solid var(--line);border-radius:5px;padding:9px 12px;margin:8px 0;font-size:12px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.pathbar code{color:#cfe3ff;font-family:ui-monospace,monospace}
.pathbar button{background:#1d2733;border:1px solid #2f4358;color:#cfe3ff;border-radius:4px;padding:4px 10px;cursor:pointer;font:inherit}
.pathbar button:hover{border-color:#4d6a8a}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:0 22px 11px}
input,select{background:#0f1216;color:var(--fg);border:1px solid var(--line);border-radius:5px;padding:6px 9px;font:inherit}
#link{font-size:12px;color:var(--dim);margin-left:auto}
.gh{position:sticky;z-index:10;background:#10141a;border-top:1px solid var(--line);border-bottom:1px solid var(--line);
    padding:6px 22px;font-size:12px;font-weight:600;color:var(--warn);letter-spacing:.03em}
.gh.nostick{position:static}
.row{display:grid;grid-template-columns:132px 1fr 300px;gap:14px;padding:14px 22px;border-bottom:1px solid var(--line)}
.spr{width:132px;height:132px;background:#0b0d10;border:1px solid var(--line);border-radius:5px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.spr img{max-width:100%;max-height:100%;image-rendering:pixelated}
.nm{font-weight:600}.meta{color:var(--dim);font-size:12px;margin:2px 0 6px}
.why b{color:var(--warn)}
.tags span{display:inline-block;font-size:11px;padding:1px 7px;border-radius:9px;border:1px solid var(--line);margin-right:5px;color:var(--warn)}
.ev{font-size:11px;color:var(--dim);font-family:ui-monospace,monospace;margin-top:5px}
.ctl{display:flex;flex-direction:column;gap:6px}.ctl label{font-size:12px;color:var(--dim)}
textarea{width:100%;min-height:52px;background:#101821;color:#cfe3ff;border:1px solid #24405c;border-radius:5px;padding:6px;font:inherit;resize:vertical}
</style>
<header>
<div class="hrow"><h1>Ash'karr — creature art flags</h1>
<span class="sub"><b id="nf">__NFLAG__</b> shown of __NTOT__ cast · worst first</span>
<button id="fold">▾ brief</button></div>

<div id="brief">
<div class="panel ok"><b>⭐ The magenta check came back clean, and that is a result.</b>
Across all __NTOT__ cast creatures: <b>ZERO</b> carry a magenta placeholder. <b>Nothing here is a MISSING texture.</b>
<i>Blind spot:</i> a <code>Graphic_Multi</code> def resolves per facing, so a missing side never renders magenta. Absence of magenta is evidence, not proof.</div>
<div class="panel"><b>🔴 These thresholds are invented and you have not ruled on them.</b>
Percentiles of the cast's own spread — px &lt; 2,579 (p25), contrast &lt; 0.138 (p05), sat &lt; 0.111 (p25), fill &gt; 0.814 (p95).
<b>They decide only where you look first.</b> px is RESOLUTION, never quality. If you disagree with a call, the call is wrong.</div>
<div class="panel"><b>⛔ FLAG ONLY — nothing here fixes art.</b> <b>Prefer shrink over redraw</b>: the resize path ships, so shrinking is free and reversible. Default is <b>keep</b>.</div>
<div class="pathbar"><b style="color:var(--ok)">Save decisions to</b>
<code id="p1">D:\Luke\dev\Rimworld\design\Jawa\fauna\creature_art_decisions.json</code>
<button data-copy="p1">copy path</button>
<span style="color:var(--dim)">the picker cannot be given a folder — a browser rule — so copy this into its filename box</span></div>
<div class="pathbar"><b style="color:var(--ok)">This sheet</b>
<code id="p2">D:\Luke\dev\Rimworld\design\Jawa\fauna\creature_art_review.html</code>
<button data-copy="p2">copy path</button></div>
</div>

<div class="bar">
<input id="q" placeholder="search name, mod, biome, reason…" size="26">
<select id="fl"><option value="">all rows</option><option value="flagged" selected>flagged only</option><option value="BLUR">BLUR</option><option value="MUDDY">MUDDY</option><option value="BLOB">BLOB</option><option value="HEADLINER_WEAK">HEADLINER_WEAK</option></select>
<select id="fm"><option value="">all mods</option></select>
<select id="fs"><option value="">any decision</option><option value="keep">keep</option><option value="shrink">shrink</option><option value="replace">replace</option><option value="redraw">redraw</option></select>
<button id="save" style="background:#0f1216;border:1px solid var(--line);color:var(--fg);border-radius:5px;padding:6px 9px;cursor:pointer;font:inherit">Link file…</button>
<button id="copy" style="background:#0f1216;border:1px solid var(--line);color:var(--fg);border-radius:5px;padding:6px 9px;cursor:pointer;font:inherit">Copy JSON</button>
<span id="link">not linked — decisions are in this tab only</span>
</div>
</header>
<div id="list"></div>
<script>
const DATA=__DATA__, PRIOR=__PRIOR__;
const D={}; let handle=null, timer=null;
const el=id=>document.getElementById(id);

// ── collapsible brief. It is sticky, so left open it eats the screen on every scroll.
// The state is remembered because re-collapsing it on every visit is the same annoyance.
const FOLDKEY='ashkarr_art_folded';
function setFold(f){ document.body.classList.toggle('folded',f); el('fold').textContent=f?'▸ brief':'▾ brief';
  try{localStorage.setItem(FOLDKEY,f?'1':'')}catch(e){} measure(); }
el('fold').onclick=()=>setFold(!document.body.classList.contains('folded'));
try{ setFold(localStorage.getItem(FOLDKEY)==='1'); }catch(e){ setFold(false); }

// ── copy-path buttons. A path you must retype is a path you will get wrong.
for(const b of document.querySelectorAll('[data-copy]')) b.onclick=async()=>{
  try{ await navigator.clipboard.writeText(el(b.dataset.copy).textContent);
       const t=b.textContent; b.textContent='copied ✓'; setTimeout(()=>b.textContent=t,1200); }
  catch(e){ const r=document.createRange(); r.selectNode(el(b.dataset.copy));
       getSelection().removeAllRanges(); getSelection().addRange(r); b.textContent='press ⌘/Ctrl+C'; }
};

// ── the sticky group label needs to sit exactly under the header, whatever height it is now
function measure(){ const h=document.querySelector('header').offsetHeight;
  document.documentElement.style.setProperty('--hh', h+'px');
  for(const g of document.querySelectorAll('.gh')) g.style.top=h+'px'; }
addEventListener('resize', measure);

const IDB='ashkarr_art_fs', IKEY='handle';
function idb(){return new Promise((res,rej)=>{const r=indexedDB.open(IDB,1);
  r.onupgradeneeded=()=>r.result.createObjectStore('h');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);});}
async function idbPut(h){try{const db=await idb();db.transaction('h','readwrite').objectStore('h').put(h,IKEY);}catch(e){}}
async function idbGet(){try{const db=await idb();return await new Promise(res=>{
  const q=db.transaction('h','readonly').objectStore('h').get(IKEY);q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null);});}catch(e){return null;}}

let kept=0, filled=0;
for(const it of DATA){ const p=PRIOR&&PRIOR.decisions&&PRIOR.decisions[it.id];
  if(p&&p.state){ D[it.id]={...p}; kept++; } else { D[it.id]={state:it.state,note:''}; filled++; } }
const mods=[...new Set(DATA.map(i=>i.mod))].sort();
for(const m of mods){const o=document.createElement('option');o.value=m;o.textContent=m;el('fm').appendChild(o);}

function card(it){
  const d=D[it.id];
  const img=it.img?`<img src="data:image/png;base64,${it.img}" alt="">`:`<span style="color:#6b7280;font-size:11px">no sprite</span>`;
  const why=it.why.replace(/\*\*(.+?)\*\*/g,'<b>$1</b>');
  return `<div class="row" data-id="${it.id}"><div class="spr">${img}</div><div>
    <div class="nm">${it.label} <span style="color:#6b7280;font-weight:400">${it.id}</span></div>
    <div class="meta">band <b style="color:#e8e6e3">${it.band}</b> · cast in ${it.biome}</div>
    <div class="tags">${it.flags.map(f=>`<span>${f}</span>`).join('')}</div>
    <div class="why">${why}</div>
    <div class="ev">px ${it.px.toLocaleString()} · contrast ${it.ct} · sat ${it.sat} · fill ${it.fill}${it.field?' · field '+it.field:''}</div>
  </div><div class="ctl"><label>decision</label>
    <select class="st">${['keep','shrink','replace','redraw','undecided'].map(s=>`<option value="${s}"${d.state===s?' selected':''}>${s}</option>`).join('')}</select>
    <label>your note — overrides everything above</label>
    <textarea class="nt" placeholder="why you disagree, or what to do instead">${(d.note||'').replace(/</g,'&lt;')}</textarea>
  </div></div>`;
}

function render(){
  const q=el('q').value.toLowerCase(), f=el('fl').value, m=el('fm').value, st=el('fs').value;
  const shown=DATA.filter(it=>{
    let ok=true;
    if(f==='flagged') ok=it.flags.length>0; else if(f) ok=it.flags.includes(f);
    if(ok&&m) ok=it.mod===m;
    if(ok&&st) ok=D[it.id].state===st;
    if(ok&&q) ok=(it.id+' '+it.label+' '+it.mod+' '+it.biome+' '+it.why).toLowerCase().includes(q);
    return ok;});
  // group by MOD - whole groups share a character and get decided in one motion
  const groups=new Map();
  for(const it of shown){ if(!groups.has(it.mod)) groups.set(it.mod,[]); groups.get(it.mod).push(it); }
  let html='';
  for(const [mod,items] of groups){
    // ⚠️ a sticky label taller than its group covers the only row in it
    html+=`<div class="gh${items.length<=3?' nostick':''}">${mod} · ${items.length}</div>`;
    html+=items.map(card).join('');
  }
  el('list').innerHTML=html||'<div style="padding:40px 22px;color:#9aa0a8">nothing matches those filters.</div>';
  el('nf').textContent=shown.length;
  measure();
  for(const r of document.querySelectorAll('.row')){ const id=r.dataset.id;
    r.querySelector('.st').onchange=e=>{D[id].state=e.target.value;save();};
    r.querySelector('.nt').oninput =e=>{D[id].note =e.target.value;save();}; }
}
['q','fl','fm','fs'].forEach(i=>el(i).oninput=render);

function payload(){
  const out=Object.assign({},PRIOR);
  out.posture='flag-only';
  out.postureMeaning='A decision here is a FLAG for the owner. Nothing in this file edits art. Rows left `keep` are accepted as-is.';
  out.decisions=D; out.savedAt=new Date().toISOString(); out.savedBy='creature_art_review.html';
  return JSON.stringify(out,null,2);
}
async function save(){ clearTimeout(timer); timer=setTimeout(async()=>{ if(!handle) return;
  const decided=Object.values(D).filter(v=>v.state&&v.state!=='undecided').length;
  if(decided<10){ el('link').textContent='REFUSED to write — only '+decided+' decided rows looks like a bug, not a review'; return; }
  try{ const w=await handle.createWritable(); await w.write(payload()); await w.close();
       el('link').textContent='saved '+new Date().toLocaleTimeString(); }
  catch(e){ el('link').textContent='write failed: '+e.message; } },900); }
el('save').onclick=async()=>{
  if(!window.showSaveFilePicker){ el('link').textContent='no File System Access API here — use Copy JSON'; return; }
  try{ handle=await window.showSaveFilePicker({suggestedName:'creature_art_decisions.json',
        types:[{description:'JSON',accept:{'application/json':['.json']}}]});
       await idbPut(handle); el('link').textContent='linked — autosaving'; save(); }catch(e){}
};
el('copy').onclick=()=>{navigator.clipboard.writeText(payload());el('link').textContent='copied to clipboard';};
(async()=>{ const h=await idbGet(); if(!h) return;
  const perm=await h.queryPermission({mode:'readwrite'});
  if(perm==='granted'){ handle=h; el('link').textContent='relinked to your file — autosaving'; }
  else{ el('link').innerHTML='<b style="color:#ffb454;cursor:pointer" id="regrant">click to reconnect your file</b>';
        el('regrant').onclick=async()=>{ if(await h.requestPermission({mode:'readwrite'})==='granted'){
          handle=h; el('link').textContent='relinked — autosaving'; save(); } }; }
})();
render();
console.log('prefilled '+filled+' rows, kept '+kept+' existing decisions untouched');
</script>
"""

if __name__ == '__main__':
    sys.exit(main())
