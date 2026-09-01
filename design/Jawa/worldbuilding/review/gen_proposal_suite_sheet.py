#!/usr/bin/env python3
"""Generate proposal_suite_review.html from proposal_suite_rows.json.

Safe to re-run: the sheet READS the owner's decisions file at runtime and
merges per-row — regenerating the sheet never touches decisions.
The page (and only the page) stamps savedAt/decidedBy into the decisions
file; nothing here ever writes those keys (review-sheets skill §11).
"""
import json, pathlib

HERE = pathlib.Path(__file__).parent
rows = json.loads((HERE / "proposal_suite_rows.json").read_text())
DEC_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\proposal_suite_review.decisions.json"
SHEET_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\proposal_suite_review.html"
GREENLIT = "Rows already green-lit 2026-09-01 (fire/weather/livestock v1 slices) are pre-locked v1 — items exist; overruling one here reopens a filed item, say so out loud."

html = r"""<!doctype html><html><head><meta charset="utf-8">
<title>Proposal Suite Review — PROPOSAL_SUITE_REVIEW_1</title>
<style>
body{background:#0c0e11;color:#e8e6e3;font:13px/1.5 system-ui,sans-serif;margin:0}
header{position:sticky;top:0;z-index:20;background:#14161a;border-bottom:1px solid #2a2f37}
.hrow{display:flex;align-items:center;gap:12px;padding:10px 22px}
h1{font-size:16px;margin:0}.sub{color:#9aa3ad;font-size:12px}
#fold{margin-left:auto;cursor:pointer;background:#0f1216;border:1px solid #2a2f37;color:#e8e6e3;border-radius:5px;padding:5px 12px;font:inherit}
body.folded #brief{display:none}
#brief{padding:4px 22px 10px;font-size:12.5px;color:#c7cdd4;max-width:1100px}
#brief b{color:#ffd479}
.pathbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:#0f1216;border:1px solid #2a2f37;border-radius:5px;padding:9px 12px;margin:8px 0;font-size:12px}
.pathbar code{color:#cfe3ff;font-family:ui-monospace,monospace}
.pathbar button,#linkbtn,#exportbtn{cursor:pointer;background:#1d2733;border:1px solid #2f4358;color:#cfe3ff;border-radius:4px;padding:4px 10px;font:inherit}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:8px 22px;background:#111419}
.bar select,.bar input{background:#0f1216;border:1px solid #2a2f37;color:#e8e6e3;border-radius:4px;padding:4px 8px;font:inherit}
#savestate{font-size:11.5px;color:#9aa3ad;margin-left:auto}
#savestate.err{color:#ff7a7a}
.gh{position:sticky;z-index:10;background:#10141a;border-top:1px solid #2a2f37;border-bottom:1px solid #2a2f37;padding:6px 22px;font-size:12px;font-weight:700;color:#ffb454;cursor:pointer}
.gh .oneline{font-weight:400;color:#9aa3ad;margin-left:8px}
.gh.nostick{position:static}
.row{display:grid;grid-template-columns:210px 1fr 320px;gap:14px;padding:9px 22px;border-bottom:1px solid #181c22;align-items:start}
.row.contested{border-left:3px solid #d7a54a}
.row.greenlit{border-left:3px solid #4ac26b}
.label{font-weight:600}.sect{color:#7c8590;font-size:11px}
.does{color:#c7cdd4}
.inv{color:#ff9d9d;font-size:11.5px;margin-top:3px}
.inv:before{content:"⚠ invented premise: ";font-weight:700}
.cost{display:inline-block;font-size:10.5px;color:#8fa8c4;border:1px solid #2a3542;border-radius:3px;padding:0 5px;margin-left:6px}
.ctl{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.ctl select{background:#0f1216;border:1px solid #2a2f37;color:#e8e6e3;border-radius:4px;padding:3px 6px;font:inherit}
.ctl select.touched{border-color:#4ac26b;background:#14231a}
.note{width:100%;background:#171b13;border:1px dashed #4a5a3a;color:#ffe9a8;border-radius:4px;padding:4px 8px;font:italic 12px/1.4 system-ui;margin-top:5px;min-height:20px}
.note::placeholder{color:#6f7a5f}
.badge{font-size:10px;font-weight:700;border-radius:3px;padding:1px 5px;margin-left:6px}
.badge.gl{background:#153c22;color:#6fe08f}.badge.ct{background:#3c3115;color:#ffd479}
</style></head><body>
<header>
 <div class="hrow"><h1>Proposal Suite Review</h1><span class="sub" id="counts"></span><button id="fold">▾ brief</button></div>
 <div id="brief">
  <p><b>What this is:</b> 125 mechanics from the 14 draft proposal docs of the 2026-08-31 brainstorm sitting. <b>Pre-filled from each doc's own build ladder — that ranks COST and DEPENDENCY, not worth.</b> Your overrules and especially your <i>notes</i> are the point; agreeing is the cheap outcome.</p>
  <p><b>Posture: nothing is destroyed by silence.</b> A row you never touch simply ships at its pre-filled ladder position (v1-slice items already filed; v2/dream stay backlog). <b>cut</b> is the only destructive verdict, and only through a later pass acting on this file. __GREENLIT__</p>
  <p><b>⚠ 25 rows carry an <span style="color:#ff9d9d">invented premise</span></b> — something a writer asserted about the world that no prior canon states. Each is named in red on its row; filter <i>invented</i> to rule on all of them. <b>21 rows are contested</b> (amber edge) — defensible both ways, they carry most of the real judgement.</p>
  <div class="pathbar"><b>Save decisions to</b> <code id="p1">__DEC__</code> <button data-copy="p1">copy path</button>
  <span>picker takes a FILENAME only — paste this whole path into its name box</span>
  <button id="linkbtn">link file</button><button id="exportbtn">copy JSON</button></div>
  <div class="pathbar"><b>This sheet</b> <code id="p2">__SHEET__</code> <button data-copy="p2">copy path</button></div>
 </div>
 <div class="bar">
  <input id="q" placeholder="search label + effect…" size="26">
  <select id="fdoc"><option value="">all docs</option></select>
  <select id="fdec"><option value="">any decision</option><option>v1</option><option>v2</option><option>dream</option><option>cut</option></select>
  <select id="fflag"><option value="">all rows</option><option value="contested">contested</option><option value="invented">invented</option><option value="greenlit">green-lit</option><option value="touched">my overrules</option></select>
  <span id="savestate">not linked — decisions cached in this browser only</span>
 </div>
</header>
<div id="list"></div>
<script>
const DATA = __DATA__;
const GREEN = new Set(["Fire Ecology / The Pyrelands","Terminator Weather Suite","Ludicrous Livestock — Deep Design"]);
const el = i => document.getElementById(i);
const LSKEY = 'proposal_suite_review_v1';

// ---------- state ----------
let dec = {};            // id -> {d, n, t:1 touched}
let extraKeys = {};      // unknown top-level keys carried through verbatim
let fileHandle = null, dirty = false, saveTimer = null;

function loadCache(){ try{ const c = JSON.parse(localStorage.getItem(LSKEY)||'{}'); if(c.rows) dec = c.rows; }catch(e){} }
function cacheNow(){ try{ localStorage.setItem(LSKEY, JSON.stringify({rows:dec})); }catch(e){} }

function decidedCount(){ return Object.values(dec).filter(x=>x.t).length; }

function fileBody(){
  const out = Object.assign({}, extraKeys, {
    sheet: "proposal_suite_review",
    posture: "prefill-ships; untouched rows keep their pre-filled ladder position; cut is the only destructive verdict",
    savedAt: new Date().toISOString(),
    decidedBy: "owner-sheet",
    touchedCount: decidedCount(),
    rows: {}
  });
  for (const d of DATA.docs) for (const r of d.rows){
    const s = dec[r.id] || {};
    out.rows[r.id] = { d: s.d || r.ladder, n: s.n || "", touched: !!s.t, prefill: r.ladder, doc: d.file };
  }
  return JSON.stringify(out, null, 1);
}

async function writeFile(){
  if(!fileHandle) return;
  // truncation guard: refuse a write that would drop the owner's touched rows
  const before = decidedCount();
  if (window.__lastWrittenTouched && before < window.__lastWrittenTouched - 5){
    el('savestate').textContent = '⛔ refused write: touched-row count fell from '+window.__lastWrittenTouched+' to '+before+' — reload before trusting this page';
    el('savestate').className='err'; return;
  }
  try{
    const w = await fileHandle.createWritable();
    await w.write(fileBody()); await w.close();
    window.__lastWrittenTouched = before;
    el('savestate').textContent = 'linked ✓ saved '+new Date().toLocaleTimeString()+' · '+before+' overrules';
    el('savestate').className='';
  }catch(e){
    el('savestate').textContent = '⚠ write failed ('+e.name+') — click "link file" to re-grant';
    el('savestate').className='err';
  }
}
function queueSave(){ cacheNow(); clearTimeout(saveTimer); saveTimer = setTimeout(writeFile, 1000); refreshCounts(); }

// IndexedDB handle persistence
function idb(){ return new Promise((res,rej)=>{ const r = indexedDB.open('sheet_handles',1);
  r.onupgradeneeded = ()=>r.result.createObjectStore('h'); r.onsuccess=()=>res(r.result); r.onerror=()=>rej(r.error); }); }
async function saveHandle(h){ const db = await idb(); db.transaction('h','readwrite').objectStore('h').put(h,'dec'); }
async function loadHandle(){ try{ const db = await idb();
  return await new Promise(res=>{ const g = db.transaction('h').objectStore('h').get('dec'); g.onsuccess=()=>res(g.result); g.onerror=()=>res(null); }); }catch(e){ return null; } }

async function absorbExisting(h){
  try{
    const f = await h.getFile(); const txt = await f.text(); if(!txt.trim()) return;
    const j = JSON.parse(txt);
    for (const k of Object.keys(j)) if(!['sheet','posture','savedAt','decidedBy','touchedCount','rows'].includes(k)) extraKeys[k]=j[k];
    let kept=0, filled=0;
    if (j.rows) for (const [id,v] of Object.entries(j.rows)){
      if (v.touched){ dec[id] = {d:v.d, n:v.n||'', t:1}; kept++; } else filled++;
    }
    el('savestate').textContent = 'linked ✓ kept your '+kept+' decisions, pre-fill covers the rest';
  }catch(e){ el('savestate').textContent='⚠ existing file unreadable ('+e.name+') — NOT overwriting; fix or pick a new file'; el('savestate').className='err'; throw e; }
}

el('linkbtn').onclick = async ()=>{
  try{
    const h = await showSaveFilePicker({suggestedName:'proposal_suite_review.decisions.json',
      types:[{description:'JSON',accept:{'application/json':['.json']}}]});
    await absorbExisting(h); fileHandle=h; await saveHandle(h); render(); await writeFile();
  }catch(e){ if(e.name!=='AbortError'){ el('savestate').textContent='⚠ '+e.name; el('savestate').className='err'; } }
};
el('exportbtn').onclick = async ()=>{ try{ await navigator.clipboard.writeText(fileBody()); el('exportbtn').textContent='copied ✓';
  setTimeout(()=>el('exportbtn').textContent='copy JSON',1200);}catch(e){ alert(fileBody()); } };

if (!window.showSaveFilePicker) el('savestate').textContent = 'this browser has no file link (Firefox?) — use copy JSON when done';

// ---------- render ----------
function refreshCounts(){
  const t = decidedCount();
  const per = {v1:0,v2:0,dream:0,cut:0};
  for (const d of DATA.docs) for (const r of d.rows){ per[(dec[r.id]&&dec[r.id].d)||r.ladder]++; }
  el('counts').textContent = `125 rows · v1 ${per.v1} · v2 ${per.v2} · dream ${per.dream} · cut ${per.cut} · your overrules ${t}`;
}
function card(r, d){
  const s = dec[r.id]||{}; const cur = s.d || r.ladder; const touched = !!s.t;
  const gl = GREEN.has(d.title) && r.ladder==='v1';
  return `<div class="row ${r.contested?'contested':''} ${gl?'greenlit':''}" data-id="${r.id}">
   <div><div class="label">${r.label}${gl?'<span class="badge gl">GREEN-LIT</span>':''}${r.contested?'<span class="badge ct">contested</span>':''}</div>
   <div class="sect">${r.section}<span class="cost">${r.cost}</span></div></div>
   <div><div class="does">${r.does}</div>${r.invented?`<div class="inv">${r.invented}</div>`:''}</div>
   <div class="ctl"><select class="dsel ${touched?'touched':''}">
     ${['v1','v2','dream','cut'].map(o=>`<option ${o===cur?'selected':''}>${o}</option>`).join('')}</select>
     <span class="sect">${touched?'your call':'pre-fill: '+r.ladder}</span>
     <textarea class="note" placeholder="why — your criterion is the valuable part">${s.n||''}</textarea></div></div>`;
}
function render(){
  const q=(el('q').value||'').toLowerCase(), fd=el('fdoc').value, fe=el('fdec').value, ff=el('fflag').value;
  let html='';
  for (const d of DATA.docs){
    if (fd && d.title!==fd) continue;
    const rows = d.rows.filter(r=>{
      const s=dec[r.id]||{}; const cur=s.d||r.ladder;
      if (q && !(r.label+' '+r.does+' '+r.section).toLowerCase().includes(q)) return false;
      if (fe && cur!==fe) return false;
      if (ff==='contested'&&!r.contested) return false;
      if (ff==='invented'&&!r.invented) return false;
      if (ff==='greenlit'&&!(GREEN.has(d.title)&&r.ladder==='v1')) return false;
      if (ff==='touched'&&!s.t) return false;
      return true;
    });
    if (!rows.length) continue;
    html += `<div class="gh${rows.length<=3?' nostick':''}">${d.title} · ${rows.length}<span class="oneline">${d.oneLine}</span></div>`;
    html += rows.map(r=>card(r,d)).join('');
  }
  el('list').innerHTML = html || '<div style="padding:30px;color:#7c8590">nothing matches the filters</div>';
  for (const row of el('list').querySelectorAll('.row')){
    const id = row.dataset.id;
    row.querySelector('.dsel').onchange = e=>{ dec[id]=Object.assign(dec[id]||{n:''},{d:e.target.value,t:1}); e.target.classList.add('touched'); queueSave(); };
    row.querySelector('.note').oninput = e=>{ dec[id]=Object.assign(dec[id]||{},{n:e.target.value,t:1,d:(dec[id]&&dec[id].d)||null}); if(!dec[id].d){const r2=find(id);dec[id].d=r2.ladder;} queueSave(); };
  }
  measure(); refreshCounts();
}
function find(id){ for(const d of DATA.docs) for(const r of d.rows) if(r.id===id) return r; }

for (const d of DATA.docs){ const o=document.createElement('option'); o.textContent=d.title; el('fdoc').appendChild(o); }
for (const id of ['q','fdoc','fdec','fflag']) el(id).oninput = render;

// chrome: fold + measure + copy
const FOLDKEY='psr_folded';
function setFold(f){ document.body.classList.toggle('folded',f); el('fold').textContent=f?'▸ brief':'▾ brief';
  try{localStorage.setItem(FOLDKEY,f?'1':'')}catch(e){} measure(); }
el('fold').onclick=()=>setFold(!document.body.classList.contains('folded'));
function measure(){ const h=document.querySelector('header').offsetHeight;
  for (const g of document.querySelectorAll('.gh')) g.style.top=h+'px'; }
addEventListener('resize',measure);
for (const b of document.querySelectorAll('[data-copy]')) b.onclick=async()=>{ const n=el(b.dataset.copy);
  try{ await navigator.clipboard.writeText(n.textContent); const t=b.textContent; b.textContent='copied ✓'; setTimeout(()=>b.textContent=t,1200);}
  catch(e){ const r=document.createRange(); r.selectNode(n); getSelection().removeAllRanges(); getSelection().addRange(r); b.textContent='press Ctrl+C'; } };

// boot: cache → maybe stored handle
loadCache();
(async()=>{ const h = await loadHandle();
  if (h){ try{ if ((await h.queryPermission({mode:'readwrite'}))==='granted'){ await absorbExisting(h); fileHandle=h; }
    else { el('savestate').textContent='file known — click "link file" to reconnect (browser needs one click after restart)'; } }catch(e){} }
  try{ setFold(localStorage.getItem(FOLDKEY)==='1'); }catch(e){ setFold(false); }
  render(); })();
</script></body></html>"""

html = html.replace("__DATA__", json.dumps(rows)).replace("__DEC__", DEC_NATIVE).replace("__SHEET__", SHEET_NATIVE).replace("__GREENLIT__", GREENLIT)
(HERE / "proposal_suite_review.html").write_text(html)
print("wrote", HERE / "proposal_suite_review.html", len(html), "bytes")
