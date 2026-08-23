#!/usr/bin/env python3
"""Generate the creature RESIZE review sheet for CREATURE_SIZES_ADJUSTED_1.

Reads  design/Jawa/fauna/cast_assignment.csv    the 746 cast rows, 621 creatures, 26 biomes
       design/Jawa/fauna/sprite_features.csv    px / w / h per sprite — the ART EVIDENCE
       <DefDump>/captures/<latest>/animals.json the live stats, incl. race.baseBodySize
       design/Jawa/fauna/sprites/<defName>.png  1,163 cached sprites
       design/Jawa/fauna/creature_size_decisions.json   optional, the owner's file
Writes design/Jawa/fauna/creature_size_review.html

🔴 **The owner's file is NEVER written by this script.** It is read so the sheet can merge
his calls per row over the prefill — a row he has touched is left exactly alone.

WHAT THE SHEET IS FOR, in the owner's words (2026-08-22):
  *"We may need to re-size some of them to adjust for low-quality graphics (make them
  smaller) or to fill in gaps (need more giant things)."*

🔑 **TWO FIELDS, TWO CONSEQUENCES, AND THE ITEM DEMANDS THEY BE NAMED SEPARATELY.**
  `drawSize`  purely visual. Costs nothing, changes nothing but the picture.
  `bodySize`  moves meat, leather, hunting yield, carrying capacity, food need and melee
              damage. A giant that is only `drawSize` is a cardboard cutout; a giant that
              is `bodySize` changes the economy.
⇒ Every non-keep row on this sheet carries which field it means.

🔴 **THE ART EVIDENCE IS `px`, AND IT IS THE POINT.** `sprite_features.csv` measures the
actual texture. A creature cast as SUPER whose sprite is 1,614 px is being scaled up from
almost nothing — that is the "low-quality graphics" case, measured rather than felt.
⚠️ px is a proxy for RESOLUTION, not for whether the art is *good*. A crisp small sprite
and a muddy large one can score the same. The owner looking at it is the authority; this
only decides where he looks first.

    python3 design/Jawa/fauna/gen_creature_size_sheet.py
"""
from __future__ import annotations
import base64, collections, csv, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CAST = os.path.join(HERE, 'cast_assignment.csv')
FEAT = os.path.join(HERE, 'sprite_features.csv')
SPR = os.path.join(HERE, 'sprites')
OUT = os.path.join(HERE, 'creature_size_review.html')
DEC = os.path.join(HERE, 'creature_size_decisions.json')
DEC_WIN = r'D:\Luke\dev\Rimworld\design\Jawa\fauna\creature_size_decisions.json'

DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump")

BANDS = ['SUPER', 'huge', 'large', 'med', 'small', 'tiny']

GROUPS = [
    ('SUPER', '🦖 SUPER-HUGE — one per biome, and they carry the silhouette',
     "24 of them, one for each biome that has one. ⚠️ <b>Two biomes have NONE</b> — "
     "<code>AB_MiasmicMangrove</code> and <code>IceSheet</code>. These are the creatures a "
     "player tells stories about, so weak art hurts most here and is worth fixing first."),
    ('huge', '🐘 HUGE — the big fauna under the headliner', ''),
    ('large', '🐂 LARGE', ''),
    ('med', '🐕 MEDIUM', ''),
    ('small', '🐇 SMALL', ''),
    ('tiny', '🐁 TINY — <b>shrinking these achieves nothing</b>; they are already small', ''),
]

# 🔑 The thresholds. px is the sprite's pixel area from sprite_features.csv. These are the
# 25th percentile of each band as measured 2026-08-23 — i.e. "in the weakest quarter of its
# own size class", not an absolute the art has to clear.
WEAK_PX = {'SUPER': 3311, 'huge': 2884, 'large': 2734, 'med': 2659, 'small': 2532, 'tiny': 1533}
STRONG_PX = 6000       # a sprite with room to be enlarged without going soft
NO_SUPER = ['AB_MiasmicMangrove', 'IceSheet']

# 🔼 THE SECOND HALF OF THE OWNER'S BRIEF — *"need more giant things"*. Two biomes have no
# super-huge, so the sheet PROPOSES one for each rather than leaving him to find it. Both
# picked the same way: the largest band already cast there, tie-broken on sprite strength,
# because promoting a creature the biome already has beats inventing one.
#   AB_MiasmicMangrove  Zakkeg          huge · 4,015 px · bodySize 5 - already its biggest
#   IceSheet            BMT_Thrumbungus huge · 5,172 px · bodySize 4 · commonality 0.35
# ⚠️ Proposals, not decisions. Both are `bodySize+drawSize`, because a headliner that is only
# drawn big is a cardboard cutout.
PROMOTE = {
    'Zakkeg': 'AB_MiasmicMangrove',
    'BMT_Thrumbungus': 'IceSheet',
}


def latest_animals():
    caps = sorted(glob.glob(os.path.join(DUMP, 'captures', '*', 'animals.json')))
    flat = os.path.join(DUMP, 'animals.json')
    p = caps[-1] if caps else (flat if os.path.exists(flat) else None)
    if not p:
        return {}, None
    d = json.load(open(p, encoding='utf-8'))
    return {a['defName']: a for a in d.get('animals', [])}, d.get('capturedUtc')


def decide(band, px, body, biomes, n_biomes, defName=''):
    """(state, field, rule, note). 🔴 Default is KEEP — most creatures are fine and a sheet
    that proposes 600 changes is a chore, not a decision aid."""
    weak = WEAK_PX.get(band)
    if defName in PROMOTE:
        b = PROMOTE[defName]
        return ('enlarge', 'bodySize+drawSize', 'R0',
                f'🔼 PROPOSED HEADLINER FOR `{b}`, which has no super-huge at all. It is '
                f'already the biggest thing cast there ({band}, {px:,} px, bodySize '
                f'{body:g}) — promoting what the biome has beats inventing a creature. '
                f'Both fields, because a giant that is only drawn big is a cutout.')
    if band in ('SUPER', 'huge') and px and weak and px < weak:
        return ('shrink', 'drawSize', 'R1',
                f'WEAKEST QUARTER OF ITS BAND — {px:,} px carrying a {band} silhouette. '
                f'Scaled up, this reads as blur. Shrink the DRAW only; its mechanics are fine.')
    if band == 'SUPER' and px and px < STRONG_PX:
        return ('keep', '', 'R2',
                f'{px:,} px. Adequate for a headliner but not generous — look at it before '
                f'deciding, this is the band where art shows.')
    if px and px >= STRONG_PX and band in ('med', 'large'):
        return ('keep', '', 'R3',
                f'⭐ STRONG ART ({px:,} px) sitting at {band}. A candidate to PROMOTE if a '
                f'biome needs a giant — enlarging this one would not go soft.')
    if band == 'tiny':
        return ('keep', '', 'R4', 'Already the smallest band. Shrinking achieves nothing.')
    if px and weak and px < weak:
        return ('keep', '', 'R5',
                f'{px:,} px, the weak quarter of {band} — but small creatures are seen small, '
                f'so the art costs little. Flagged, not proposed.')
    return ('keep', '', 'R6', f'{px:,} px at {band}. Reads correctly for its size.' if px
            else f'{band}. No sprite measured — look before deciding.')


def main() -> int:
    cast = list(csv.DictReader(open(CAST, encoding='utf-8')))
    feat = {r['defName']: r for r in csv.DictReader(open(FEAT, encoding='utf-8'))}
    animals, captured = latest_animals()

    # one row per CREATURE, carrying every biome it is cast into
    per = collections.OrderedDict()
    for r in cast:
        d = r['defName']
        e = per.setdefault(d, {'defName': d, 'label': r['label'], 'mod': r['mod'],
                               'band': r['band'], 'biomes': [], 'status': r['status'],
                               'bodySize': r['bodySize'], 'promoted': r.get('promoted', '')})
        e['biomes'].append((r['biome'], r['commonality']))
        # a creature cast at different bands in different biomes takes the biggest
        if BANDS.index(r['band']) < BANDS.index(e['band']):
            e['band'] = r['band']

    prior = {}
    if os.path.exists(DEC):
        try:
            prior = json.load(open(DEC, encoding='utf-8')).get('decisions', {}) or {}
        except Exception as ex:
            print(f'  decisions unreadable ({ex}); shipping prefill only', file=sys.stderr)

    items, n_spr = [], 0
    for d, e in per.items():
        f = feat.get(d)
        px = int(f['px']) if f and f['px'].isdigit() else 0
        a = animals.get(d) or {}
        body = (a.get('race') or {}).get('baseBodySize')
        if body is None:
            try:
                body = float(e['bodySize'])
            except (TypeError, ValueError):
                body = None
        state, field, rule, note = decide(e['band'], px, body, e['biomes'], len(e['biomes']), d)
        img = ''
        p = os.path.join(SPR, d + '.png')
        if os.path.exists(p) and os.path.getsize(p) < 300000:
            img = base64.b64encode(open(p, 'rb').read()).decode('ascii')
            n_spr += 1
        bits = [e['band']]
        if body is not None:
            bits.append(f'bodySize {body:g}')
        bits.append(f'{px:,} px' if px else 'NO SPRITE MEASURED')
        bits.append(f'{len(e["biomes"])} biome' + ('s' if len(e['biomes']) != 1 else ''))
        items.append({
            'd': d, 'l': e['label'], 'm': e['mod'], 'g': e['band'],
            'px': px, 'body': body if body is not None else '',
            'b': [b for b, _ in e['biomes']],
            'eff': ' · '.join(bits), 's': state, 'f': field, 'rule': rule, 'note': note,
            'img': img,
            'gap': [b for b in NO_SUPER if b in [x for x, _ in e['biomes']]],
        })
    order = {g: i for i, (g, _t, _d) in enumerate(GROUPS)}
    items.sort(key=lambda x: (order.get(x['g'], 9), -x['px']))

    payload = json.dumps({'items': items, 'groups': GROUPS, 'captured': captured,
                          'target': DEC_WIN}, ensure_ascii=False)
    open(OUT, 'w', encoding='utf-8').write(TEMPLATE.replace('/*__DATA__*/', payload))
    n = collections.Counter(i['s'] for i in items)
    print(f'wrote {OUT}')
    print(f"  {len(items)} creatures · prefill: keep {n['keep']} · shrink {n['shrink']} "
          f"· enlarge {n['enlarge']} · undecided {n['undecided']}")
    print(f"  sprites embedded: {n_spr}/{len(items)} · animals.json captured {captured}")
    if prior:
        print(f"  the owner's file holds {sum(1 for v in prior.values() if v.get('touched'))} "
              f"touched rows; the sheet merges them per row on load")
    return 0


TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ash'karr creature sizes</title><style>
*{box-sizing:border-box}
body{margin:0;background:#14161a;color:#d8dbe0;font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;padding-bottom:52px}
header{padding:12px 20px 0;background:#1b1e24;border-bottom:1px solid #2c313a}
h1{margin:0 0 2px;font-size:17px;color:#fff}
.sub{color:#8b929e;font-size:12.5px}
.panel{margin:8px 0 0;padding:10px 12px;border-radius:7px;background:#20242b;border-left:3px solid #d08a3e;font-size:12.5px;color:#c3c8d0}
.panel b{color:#fff} .panel code{background:#14161a;padding:1px 4px;border-radius:3px;color:#c9b98a}
#stick{position:sticky;top:0;z-index:50;background:#1b1e24;border-bottom:1px solid #2c313a;padding:8px 20px}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
input[type=search],select{background:#14161a;border:1px solid #333a45;color:#d8dbe0;padding:6px 9px;border-radius:5px;font-size:13px}
input[type=search]{min-width:220px}
.count{font-size:12.5px;color:#8b929e;margin-left:auto;text-align:right}
.count b{color:#fff}
main{padding:0 20px}
section.grp{margin:16px 0 0}
section.grp>h2{position:sticky;top:52px;z-index:40;background:#171b21;margin:0;padding:8px 12px;
border:1px solid #2c313a;border-radius:7px 7px 0 0;font-size:14px;color:#fff}
section.grp.short>h2{position:static}
section.grp>h2 span{display:block;font-weight:400;font-size:12px;color:#9aa2ad;margin-top:3px}
section.grp>h2 button{font-size:11px;margin-left:6px}
table{width:100%;border-collapse:collapse;background:#171b21;border:1px solid #2c313a;border-top:0}
td{border-top:1px solid #23282f;padding:8px 10px;vertical-align:top}
tr.shrink{background:#1d1614} tr.enlarge{background:#141d18} tr.undec{background:#1a1a22}
td.spr{width:74px} td.spr img{width:64px;height:64px;object-fit:contain;image-rendering:pixelated;background:#0f1115;border-radius:5px}
.nospr{width:64px;height:64px;display:flex;align-items:center;justify-content:center;background:#2a1a1a;color:#e08a80;font-size:10px;border-radius:5px;text-align:center}
.nm{font-weight:600;color:#fff} .dn{font-size:11.5px;color:#7d8794}
.eff{font-size:12px;color:#9aa2ad;margin-top:2px}
.tags{margin-top:4px}
.tag{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:9px;margin-right:5px}
.tag.rule{background:#2a2436;color:#a48fd0}
.tag.gap{background:#3a2020;color:#e88f86}
.tag.fld{background:#1e2a35;color:#7fb6e0}
.why{font-size:12px;color:#c3c8d0;margin-top:4px}
.bio{font-size:11.5px;color:#6f7883;margin-top:3px}
.note{width:100%;margin-top:5px;background:#0f1115;border:1px dashed #3a414c;color:#c9b98a;padding:4px 6px;border-radius:4px;font-size:12px;font-family:inherit}
td.px{width:110px;font-size:12px;color:#8b929e;text-align:right;white-space:nowrap}
td.px b{color:#fff;display:block;font-size:14px}
td.dec{width:290px;white-space:nowrap}
button{background:#232830;border:1px solid #39404b;color:#c3c8d0;padding:4px 9px;border-radius:5px;font-size:12px;cursor:pointer}
button:hover{background:#2c323b}
button.on[data-s=keep]{background:#1e3524;border-color:#2f6b43;color:#9fe0b6}
button.on[data-s=shrink]{background:#3a2018;border-color:#7d4028;color:#f0b49c}
button.on[data-s=enlarge]{background:#173726;border-color:#2f7d52;color:#9ff0c4}
.fldsel{margin-top:5px}
footer{position:fixed;bottom:0;left:0;right:0;background:#1b1e24;border-top:1px solid #2c313a;padding:8px 20px;display:flex;gap:10px;align-items:center;font-size:12.5px;z-index:60}
#link b{color:#fff} #link.bad b{color:#e08a80}
.tgt{margin-left:auto;color:#8b929e}
.tgt code{background:#0f1115;padding:2px 5px;border-radius:3px;color:#c9b98a;user-select:all}
button.mini{font-size:11px;padding:2px 6px;margin-left:6px}
</style></head><body>
<header>
<h1>Ash'karr — creature sizes</h1>
<div class="sub">Owner, 2026-08-22: <i>"We may need to re-size some of them to adjust for
low-quality graphics (make them smaller) or to fill in gaps (need more giant things)."</i></div>
<div class="panel"><b>Default is KEEP.</b> Only rows you mark <b>shrink</b> or <b>enlarge</b>
become work; everything else stays exactly as it ships. Every change carries <b>which field</b>:
<code>drawSize</code> is purely visual and costs nothing, <code>bodySize</code> moves meat,
leather, hunting yield, carrying capacity, food need and melee damage.
<br><b>The art evidence is <code>px</code></b> — the real texture area, from
<code>sprite_features.csv</code>. A creature cast SUPER at 1,614&nbsp;px is being scaled up
from almost nothing. ⚠️ px measures RESOLUTION, not whether the art is <i>good</i> — it only
decides where you look first. <b>You are the authority; this is a pre-fill to disagree with.</b>
<br>🔴 <b>Two biomes have no super-huge at all:</b> <code>AB_MiasmicMangrove</code> and
<code>IceSheet</code>. Rows cast into them carry a <span class="tag gap">NEEDS A GIANT</span> tag.</div>
</header>
<div id="stick"><div class="bar">
<input type="search" id="q" placeholder="search name, defName, mod, reason…">
<select id="fs"><option value="">all decisions</option><option value="keep">keep</option><option value="shrink">shrink</option><option value="enlarge">enlarge</option><option value="undecided">undecided</option></select>
<select id="fb"><option value="">all bands</option><option>SUPER</option><option>huge</option><option>large</option><option>med</option><option>small</option><option>tiny</option></select>
<select id="fm"><option value="">all mods</option></select>
<select id="fx"><option value="">any art</option><option value="weak">🔴 weakest quarter of its band</option><option value="strong">⭐ strong art (6,000+ px)</option><option value="none">no sprite</option><option value="gap">🔴 in a biome with no giant</option></select>
<div class="count" id="count"></div>
</div></div>
<main id="main"></main>
<footer>
<button id="btncopy">Copy JSON</button>
<button id="btnlink">Link to file…</button>
<button id="btnre" style="display:none">Reconnect file</button>
<span id="link">not linked — <b>your work is in this browser only</b></span>
<span class="tgt">save as <code id="tgtpath"></code><button id="btnpath" class="mini">copy path</button></span>
</footer>
<script>
const DATA = /*__DATA__*/;
const ITEMS = DATA.items, GROUPS = DATA.groups;
const LSKEY = 'ashkarr_creature_sizes_v1';
document.getElementById('tgtpath').textContent = DATA.target;

let state = {}, fileHandle = null;
function loadLocal(){ try{ return JSON.parse(localStorage.getItem(LSKEY)||'{}'); }catch(e){ return {}; } }
function saveLocal(){ try{ localStorage.setItem(LSKEY, JSON.stringify(state)); }catch(e){} }

// Merge PER ROW: a row the human touched is left alone; untouched rows take the prefill.
(function seed(){
  const prior = loadLocal(); let filled=0, kept=0;
  for(const it of ITEMS){
    if(prior[it.d] && prior[it.d].touched){ state[it.d] = prior[it.d]; kept++; }
    else { state[it.d] = {s: it.s, f: it.f||'', note:(prior[it.d]&&prior[it.d].note)||'', touched:false}; filled++; }
  }
  if(kept) console.log(`Filled ${filled} rows from the prefill, kept your ${kept} existing decisions untouched.`);
})();

function payload(){
  const dec = {};
  for(const it of ITEMS){ const s = state[it.d];
    dec[it.d] = {decision: s.s, field: s.f||'', note: s.note||'', label: it.l, mod: it.m,
                 band: it.g, px: it.px, bodySize: it.body, touched: !!s.touched}; }
  return {
    posture: "blacklist",
    postureMeaning: "Default is KEEP. Only entries with decision 'shrink' or 'enlarge' are work. An undecided entry is left exactly as it ships.",
    fieldMeaning: "drawSize is visual only. bodySize moves meat, leather, hunting yield, carrying capacity, food need and melee damage.",
    savedBy: "creature_size_review.html",
    savedAt: new Date().toISOString(),
    decidedCount: Object.values(state).filter(s=>s.touched).length,
    total: ITEMS.length,
    decisions: dec
  };
}

// 🔑 REMEMBER THE FILE ACROSS RELOADS. A FileSystemFileHandle is structured-cloneable, so
// IndexedDB can hold it and localStorage cannot. ⚠️ showSaveFilePicker will NOT accept a
// path in suggestedName - a filename only, by design - so the handle is the only way to
// reopen in the right folder, and the full path is printed in the footer for the first time.
const IDB='ashkarr_creature_fs', IKEY='handle';
function idb(){ return new Promise((res,rej)=>{ const r=indexedDB.open(IDB,1);
  r.onupgradeneeded=()=>r.result.createObjectStore('h'); r.onsuccess=()=>res(r.result); r.onerror=()=>rej(r.error); }); }
async function idbPut(h){ try{ const db=await idb(); db.transaction('h','readwrite').objectStore('h').put(h,IKEY); }catch(e){} }
async function idbGet(){ try{ const db=await idb(); return await new Promise(res=>{
  const q=db.transaction('h','readonly').objectStore('h').get(IKEY); q.onsuccess=()=>res(q.result||null); q.onerror=()=>res(null); }); }catch(e){ return null; } }

let carried = {};
async function writeFile(){
  if(!fileHandle) return;
  const touched = Object.values(state).filter(s=>s.touched).length;
  if(ITEMS.length < 50){ setLink('refused — implausible row count', true); return; }
  try{
    const w = await fileHandle.createWritable();
    await w.write(JSON.stringify(Object.assign({}, carried, payload()), null, 2));
    await w.close();
    setLink('saved ' + new Date().toLocaleTimeString() + ' · ' + touched + ' of ' + ITEMS.length + ' touched');
  }catch(e){ setLink('write failed: ' + e.message, true); }
}
async function adopt(h, opts){
  const write = !opts || opts.write !== false;
  fileHandle = h;
  try{ const f = await h.getFile(); const txt = await f.text();
    if(txt.trim()){ const j = JSON.parse(txt);
      for(const k of Object.keys(j)) if(!['posture','postureMeaning','fieldMeaning','savedBy','savedAt','decidedCount','total','decisions'].includes(k)) carried[k]=j[k];
      // 🔴 THE FILE FILLS GAPS; IT NEVER OVERWRITES THIS SESSION'S WORK.
      if(j.decisions) for(const d in j.decisions){
        if(state[d] && j.decisions[d].touched && !state[d].touched){
          state[d]={s:j.decisions[d].decision,f:j.decisions[d].field||'',note:j.decisions[d].note||'',touched:true}; } }
    }
  }catch(e){}
  await idbPut(h); render(); if(write) await writeFile();
}
let t=null;
function queueWrite(){ saveLocal(); if(!fileHandle) return; clearTimeout(t); t=setTimeout(writeFile,900); }
function setLink(msg, bad){ const el=document.getElementById('link'); el.className = bad?'bad':'';
  el.innerHTML = fileHandle ? ('linked · <b>'+msg+'</b>') : ('not linked — <b>your work is in this browser only</b>'); }

document.getElementById('btnlink').onclick = async ()=>{
  if(!window.showSaveFilePicker){ alert("This browser has no File System Access API (Firefox does not). Use Copy JSON and paste it into\n" + DATA.target); return; }
  try{
    const prior = await idbGet();
    const opts = {suggestedName:'creature_size_decisions.json', types:[{description:'JSON',accept:{'application/json':['.json']}}]};
    if(prior) opts.startIn = prior;
    await adopt(await window.showSaveFilePicker(opts));
  }catch(e){}
};
document.getElementById('btnre').onclick = async ()=>{
  const h = await idbGet(); if(!h) return;
  try{ const p = await h.requestPermission({mode:'readwrite'});
    if(p==='granted'){ document.getElementById('btnre').style.display='none'; await adopt(h); }
    else setLink('permission refused', true);
  }catch(e){ setLink('reconnect failed: '+e.message, true); }
};
document.getElementById('btnpath').onclick = ()=>{
  navigator.clipboard.writeText(DATA.target).then(()=>setLink('path copied'),()=>{}); };
document.getElementById('btncopy').onclick = ()=>{
  navigator.clipboard.writeText(JSON.stringify(payload(),null,2))
    .then(()=>setLink('copied to clipboard'),()=>alert('clipboard blocked')); };
(async ()=>{ const h = await idbGet(); if(!h) return;
  try{ const p = await h.queryPermission({mode:'readwrite'});
    if(p==='granted') await adopt(h, {write:false});
    else { document.getElementById('btnre').style.display=''; setLink('a file is remembered — click Reconnect file', true); }
  }catch(e){}
})();

function set(d, s){ state[d].s = s;
  if(s!=='keep' && !state[d].f) state[d].f = (s==='shrink' ? 'drawSize' : 'bodySize+drawSize');
  if(s==='keep') state[d].f='';
  state[d].touched = true; queueWrite(); render(); }
function setField(d, v){ state[d].f = v; state[d].touched = true; queueWrite(); }
function setNote(d, v){ state[d].note = v; state[d].touched = true; queueWrite(); }
function bulk(g, s){ for(const it of ITEMS) if(it.g===g && visible(it)) set2(it.d, s); queueWrite(); render(); }
function set2(d,s){ state[d].s=s; if(s==='keep') state[d].f=''; else if(!state[d].f) state[d].f=(s==='shrink'?'drawSize':'bodySize+drawSize'); state[d].touched=true; }

let q='', fs='', fb='', fm='', fx='';
const WEAK = {SUPER:3311, huge:2884, large:2734, med:2659, small:2532, tiny:1533};
function visible(it){
  if(fs && state[it.d].s!==fs) return false;
  if(fb && it.g!==fb) return false;
  if(fm && it.m!==fm) return false;
  if(fx==='weak' && !(it.px && it.px < WEAK[it.g])) return false;
  if(fx==='strong' && !(it.px >= 6000)) return false;
  if(fx==='none' && it.px) return false;
  if(fx==='gap' && !(it.gap && it.gap.length)) return false;
  if(q){ const h=(it.l+' '+it.d+' '+it.m+' '+it.eff+' '+it.note).toLowerCase(); if(!h.includes(q)) return false; }
  return true;
}
function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

function row(it){
  const s=state[it.d];
  const cls = s.s==='shrink'?' class="shrink"':(s.s==='enlarge'?' class="enlarge"':(s.s==='undecided'?' class="undec"':''));
  const img = it.img ? `<img src="data:image/png;base64,${it.img}" alt="">` : `<div class="nospr">no sprite</div>`;
  const bio = it.b.length>4 ? it.b.slice(0,4).join(', ')+' +'+(it.b.length-4) : it.b.join(', ');
  const fld = s.s==='keep' ? '' : `<div class="fldsel"><select onchange="setField('${it.d}',this.value)">
      <option value="drawSize"${s.f==='drawSize'?' selected':''}>drawSize — visual only</option>
      <option value="bodySize"${s.f==='bodySize'?' selected':''}>bodySize — meat, yield, melee</option>
      <option value="bodySize+drawSize"${s.f==='bodySize+drawSize'?' selected':''}>both — a real giant</option>
    </select></div>`;
  return `<tr${cls}>
  <td class="spr">${img}</td>
  <td><div class="nm">${esc(it.l)}</div><div class="dn">${esc(it.d)} · ${esc(it.m)}</div>
    <div class="eff">${esc(it.eff)}</div>
    <div class="tags">${it.gap&&it.gap.length?'<span class="tag gap">NEEDS A GIANT: '+esc(it.gap.join(', '))+'</span>':''}${s.f?'<span class="tag fld">'+esc(s.f)+'</span>':''}<span class="tag rule">${it.rule}</span></div>
    <div class="why">${esc(it.note)}</div>
    <div class="bio">${esc(bio)}</div>
    <input class="note" placeholder="your note…" value="${esc(s.note||'')}" oninput="setNote('${it.d}',this.value)">
  </td>
  <td class="px"><b>${it.px?it.px.toLocaleString():'—'}</b>px${it.body!==''?'<br>body '+it.body:''}</td>
  <td class="dec">
    <button data-s="keep" class="${s.s==='keep'?'on':''}" onclick="set('${it.d}','keep')">keep</button>
    <button data-s="shrink" class="${s.s==='shrink'?'on':''}" onclick="set('${it.d}','shrink')">🔽 shrink</button>
    <button data-s="enlarge" class="${s.s==='enlarge'?'on':''}" onclick="set('${it.d}','enlarge')">🔼 enlarge</button>
    ${fld}
  </td></tr>`;
}

function render(){
  const main=document.getElementById('main'); let html='';
  let nk=0,ns=0,ne=0,nu=0;
  for(const it of ITEMS){ const s=state[it.d].s;
    if(s==='keep')nk++; else if(s==='shrink')ns++; else if(s==='enlarge')ne++; else nu++; }
  for(const [gid,title,desc] of GROUPS){
    const rows=ITEMS.filter(it=>it.g===gid && visible(it));
    if(!rows.length) continue;
    html += `<section class="grp${rows.length<=3?' short':''}"><h2>${title}
      <button onclick="bulk('${gid}','keep')">keep all</button>
      <button onclick="bulk('${gid}','shrink')">shrink all</button>
      ${desc?'<span>'+desc+'</span>':''}</h2><table>${rows.map(row).join('')}</table></section>`;
  }
  main.innerHTML = html || '<p style="padding:20px;color:#8b929e">nothing matches those filters.</p>';
  document.getElementById('count').innerHTML =
    `<b>${nk}</b> keep · <b>${ns}</b> shrink · <b>${ne}</b> enlarge${nu?' · <b>'+nu+'</b> undecided':''} of <b>${ITEMS.length}</b>`;
}
(function mods(){ const sel=document.getElementById('fm');
  for(const m of [...new Set(ITEMS.map(i=>i.m))].sort()) sel.add(new Option(m,m)); })();
document.getElementById('q').oninput=e=>{q=e.target.value.toLowerCase();render();};
document.getElementById('fs').onchange=e=>{fs=e.target.value;render();};
document.getElementById('fb').onchange=e=>{fb=e.target.value;render();};
document.getElementById('fm').onchange=e=>{fm=e.target.value;render();};
document.getElementById('fx').onchange=e=>{fx=e.target.value;render();};
render(); setLink('');
</script></body></html>'''


if __name__ == '__main__':
    sys.exit(main())
