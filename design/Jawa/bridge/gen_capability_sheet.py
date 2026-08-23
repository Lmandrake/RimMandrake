#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the DLL capability roster sheet the owner culls.

    python3 design/Jawa/bridge/gen_capability_sheet.py

Reads capability_roster_data.py, writes dll_capability_roster.html beside it.

🔴 IT WILL NOT OVERWRITE THE OWNER'S DECISIONS. The decisions live in a SEPARATE
file (dll_capability_roster.decisions.json) that this script never writes. The page
carries the roster; the JSON carries his calls; they meet in the browser. That is
deliberate - the review-sheets lesson is that a generator which owns both will
eventually regenerate over a human's work.

⭐ POSTURE IS DEFAULT INCLUDE, on the owner's choice 2026-08-23: a row he never
touches is a BUILD TARGET. That is the opposite of the worldmap sheet and it is
written into the page and into the exported JSON, because a sparse decisions file
is otherwise ambiguous and a consumer will eventually guess wrong.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import capability_roster_data as D  # noqa: E402

OUT = os.path.join(HERE, "dll_capability_roster.html")
DECISIONS = "dll_capability_roster.decisions.json"

ROWS = []
for domain, entries in D.ROSTER.items():
    for name, effect, api, diff, built, warn in entries:
        ROWS.append({"id": "%s::%s" % (domain, name), "domain": domain, "name": name,
                     "effect": effect, "api": api, "diff": diff,
                     "built": bool(built), "warn": warn})

TOTAL = len(ROWS)
BUILT = sum(1 for r in ROWS if r["built"])

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#0d1013;color:#d6dae0;font:14px/1.5 "Segoe UI",system-ui,sans-serif}
a{color:#7fb2ff}
header{position:sticky;top:0;z-index:30;background:#11161b;border-bottom:1px solid #232c35;padding:14px 18px}
h1{margin:0 0 6px;font-size:17px;letter-spacing:.2px}
.sub{color:#8b95a1;font-size:12.5px}
.panel{background:#151b21;border:1px solid #232c35;border-radius:6px;padding:12px 14px;margin:12px 18px}
.panel h2{margin:0 0 6px;font-size:13px;text-transform:uppercase;letter-spacing:.8px;color:#9fb0c2}
.posture{border-left:3px solid #d98b2b}
.invented{border-left:3px solid #b46cd1}
.gaps{border-left:3px solid #3f8fd0}
.counts{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:13px}
.count{background:#0d1216;border:1px solid #26303a;border-radius:4px;padding:4px 10px}
.count b{font-size:15px}
.c-build b{color:#5ec27a}.c-struck b{color:#e2686d}.c-flag b{color:#e0b750}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:10px 18px;background:#0f141a;border-bottom:1px solid #1d252d;position:sticky;top:0;z-index:20}
input[type=text],select{background:#0b0f13;color:#d6dae0;border:1px solid #2a343e;border-radius:4px;padding:5px 8px;font:inherit}
input[type=text]{min-width:230px}
button{background:#1c242c;color:#cdd5de;border:1px solid #2e3945;border-radius:4px;padding:5px 10px;font:inherit;cursor:pointer}
button:hover{background:#26313b}
button.on{background:#2b4a34;border-color:#3d6b4a;color:#bff0cd}
main{padding:0 18px 60px}
.group{margin-top:22px}
.ghead{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:7px 10px;background:#161d24;border:1px solid #232c35;border-radius:5px}
.ghead .gn{font-weight:600;font-size:14px}
.ghead .gc{color:#7f8b98;font-size:12px}
.ghead .sp{flex:1}
table{width:100%;border-collapse:collapse;margin-top:6px}
td{border-bottom:1px solid #1a2129;padding:8px 8px;vertical-align:top}
tr.struck td{opacity:.42}
tr.struck .nm{text-decoration:line-through}
tr.flagged{background:#231d0f}
.nm{font-weight:600;color:#e6ebf1;font-family:ui-monospace,Consolas,monospace;font-size:13px}
.ef{color:#c3ccd6}
.api{color:#6f7b88;font-family:ui-monospace,Consolas,monospace;font-size:11.5px;word-break:break-word}
.warn{color:#e0a24a;font-size:12px;margin-top:3px}
.warn.stop{color:#e2686d}
.chip{display:inline-block;border-radius:3px;padding:1px 6px;font-size:11px;border:1px solid;margin-right:5px}
.EASY{color:#5ec27a;border-color:#2f5f3f}.MEDIUM{color:#d9b23f;border-color:#5f5227}.HARD{color:#e2686d;border-color:#5f2f32}
.built{color:#7fb2ff;border-color:#2c4a70}
.acts{white-space:nowrap}
.note{width:100%;background:#0b0f13;color:#e7d9a8;border:1px solid #2a343e;border-radius:4px;padding:4px 6px;font:12px ui-monospace,Consolas,monospace;margin-top:4px}
#fsbar{margin:12px 18px;padding:10px 14px;border-radius:6px;border:1px solid;font-size:13px}
#fsbar.linked{background:#101e14;border-color:#2f5f3f}
#fsbar.unlinked{background:#1e1010;border-color:#5f2f32}
#fsbar.stale{background:#1e1a10;border-color:#5f5227}
#fslead{font-weight:600;margin-bottom:3px}
#fsdet{color:#9aa6b2}
.path{font-family:ui-monospace,Consolas,monospace;color:#9fc3ff}
.hide{display:none}
"""

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

def build():
    gaps = "".join(
        "<li><b>%s</b> — %s <span class='api'>(%s returned zero hits)</span></li>"
        % (esc(d), esc(why), esc(api)) for d, api, why in D.GAPS)

    doc = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JawaBench capability roster — the owner's cull</title><style>%s</style></head><body>
<header>
  <h1>JawaBench capability roster — what a companion <code>[Tool]</code> could do</h1>
  <div class="sub">%d capabilities across %d domains · %d already BUILT · every row names the RimWorld type behind it</div>
</header>

<div class="panel posture">
  <h2>The brief, and what an untouched row means</h2>
  <div>Owner, 2026-08-18: <i>“Produce the FULL roster of RimWorld functionality we could
  implement as companion [Tool] methods — not what is built, what is POSSIBLE — then have
  the owner select down from it for the next version of the DLL. The roster is the
  deliverable; the cull is the owner's, not ours.”</i></div>
  <div style="margin-top:8px"><b style="color:#e0a24a">POSTURE: DEFAULT INCLUDE.</b>
  Every row is a build target <b>unless you strike it</b>. A row you never look at
  <b>will be built</b>. That is the opposite of the world-map sheet, and it is your
  choice from 2026-08-23 — it is written into the exported JSON so nothing downstream
  can misread it.</div>
  <div class="counts">
    <span class="count c-build">BUILD <b id="nBuild">0</b></span>
    <span class="count c-struck">STRUCK <b id="nStruck">0</b></span>
    <span class="count c-flag">FLAGGED <b id="nFlag">0</b></span>
    <span class="count">already BUILT <b>%d</b></span>
    <span class="count">total <b>%d</b></span>
  </div>
</div>

<div class="panel invented">
  <h2>Rules I invented — overrule any of them in one line</h2>
  <ul style="margin:4px 0 0 16px;padding:0">
    <li><b>The EASY / MEDIUM / HARD calls are mine.</b> They are judgement about C# effort,
    not anything RimWorld states. HARD generally means “the engine fights you”, not “long”.</li>
    <li><b>The 24 domains are mine too.</b> RimWorld has no such grouping; I split by what
    a tool would touch, so a capability could defensibly sit in a different box.</li>
    <li><b>One row can cover several tools.</b> 63 rows are marked BUILT against 121 shipping
    <code>jawa/</code> tools — the roster is capabilities, not a 1:1 tool list.</li>
    <li><b>A BUILT row is still cullable</b>, and FLAG is there for “this exists and is not
    good enough”.</li>
  </ul>
</div>

<div class="panel gaps">
  <h2>Ten domains with no tool at all — measured, not guessed</h2>
  <div class="sub" style="margin-bottom:4px">A name scan of all 246 tools plus a targeted
  API grep in the companion source, each returning zero hits.</div>
  <ul style="margin:4px 0 0 16px;padding:0">%s</ul>
</div>

<div id="fsbar" class="unlinked">
  <div id="fslead">NOT LINKED</div>
  <div id="fsdet"></div>
  <div style="margin-top:8px">
    <button id="fslink">link to file…</button>
    <button id="fsreconnect">reconnect</button>
    <button id="fssave">save now</button>
    <button id="fsunlink">unlink</button>
    <button id="fsexport">copy JSON</button>
  </div>
</div>

<div class="bar">
  <input type="text" id="q" placeholder="search name, effect or API…">
  <select id="fdom"><option value="">every domain</option></select>
  <select id="fdiff"><option value="">any difficulty</option><option>EASY</option><option>MEDIUM</option><option>HARD</option></select>
  <select id="fbuilt"><option value="">built or not</option><option value="1">already BUILT</option><option value="0">NOT built</option></select>
  <select id="fstate"><option value="">any state</option><option value="build">build</option><option value="struck">struck</option><option value="flag">flagged</option></select>
  <button id="fwarn">only rows with a trap</button>
  <span class="sub" id="shown"></span>
</div>

<main id="main"></main>
<script>
const DATA = %s;
const TOTAL = %d, BUILT_N = %d;
const SHEET = "dll_capability_roster";
const LSKEY = "jawa.dllroster.v1";
""" % (CSS, TOTAL, len(D.ROSTER), BUILT, BUILT, TOTAL, gaps,
       json.dumps(ROWS, ensure_ascii=False), TOTAL, BUILT)

    doc += r"""
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* ---------- link to the real file ----------
   Lifted from worldmap_elements.html, which paid for every line of it:
     · showSaveFilePicker() gives a real writable handle. Chromium only.
     · IndexedDB is the ONLY store that survives a reload with a handle in it -
       localStorage stringifies it to "[object Object]" and loses it.
     · Chrome drops write permission when the tab closes and will only re-grant it
       from a CLICK, so there is a visible reconnect button and not a silent retry
       that is guaranteed to fail while looking fine. */
const FS_SUPPORTED = typeof window.showSaveFilePicker === "function";
const FS_TARGET = "dll_capability_roster.decisions.json";
const FS_DEBOUNCE = 1000;
/* 🔴 THE TRUNCATION GUARD. Under DEFAULT INCLUDE an empty decisions object is
   indistinguishable from "build everything", so the danger is the opposite of the
   whitelist sheet's: a half-loaded page would write a file that silently un-strikes
   everything he cut. Refuse the write unless the roster itself is fully in memory. */
const FS_MIN_ROWS = 150;
let fsHandle=null, fsBooted=false, fsTimer=0, fsWriting=false, fsPending=false,
    fsNeedsGesture=false, fsErr="", fsLastWrite=null;

const IDB_NAME="jawa.dllroster", IDB_STORE="handles", IDB_KEY="decisions";
function idbOpen(){return new Promise((res,rej)=>{const r=indexedDB.open(IDB_NAME,1);
  r.onupgradeneeded=()=>{const db=r.result; if(!db.objectStoreNames.contains(IDB_STORE)) db.createObjectStore(IDB_STORE);};
  r.onsuccess=()=>res(r.result); r.onerror=()=>rej(r.error);});}
function idbTx(mode,fn){return idbOpen().then(db=>new Promise((res,rej)=>{
  const tx=db.transaction(IDB_STORE,mode), rq=fn(tx.objectStore(IDB_STORE));
  tx.oncomplete=()=>res(rq?rq.result:undefined); tx.onerror=()=>rej(tx.error); tx.onabort=()=>rej(tx.error);}));}
const idbGet=()=>idbTx("readonly",st=>st.get(IDB_KEY)).catch(()=>null);
const idbPut=h=>idbTx("readwrite",st=>st.put(h,IDB_KEY)).catch(()=>null);
const idbDel=()=>idbTx("readwrite",st=>st.delete(IDB_KEY)).catch(()=>null);

async function fsPerm(h,request){ if(!h||!h.queryPermission) return "granted";
  const o={mode:"readwrite"}; let p=await h.queryPermission(o);
  if(p!=="granted"&&request) p=await h.requestPermission(o); return p; }
const clock = d => d.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"});

function fsStatus(){
  const bar=document.getElementById("fsbar"), lead=document.getElementById("fslead"),
        det=document.getElementById("fsdet");
  const show=(id,on)=>{const e=document.getElementById(id); if(e) e.style.display=on?"":"none";};
  bar.classList.remove("linked","unlinked","stale");
  if(!FS_SUPPORTED){ bar.classList.add("unlinked");
    lead.textContent="NOT LINKED — this browser cannot write to disk at all";
    det.innerHTML="The <b>File System Access API</b> does not exist in Firefox or Safari, so "
      +"auto-save to <span class='path'>"+FS_TARGET+"</span> is genuinely impossible here. Use "
      +"<b>copy JSON</b>, or reopen this page in <b>Chrome or Edge</b>. Your calls are still "
      +"kept inside this browser meanwhile.";
    ["fslink","fsreconnect","fssave","fsunlink"].forEach(i=>show(i,false)); return; }
  if(!fsHandle){ bar.classList.add("unlinked");
    lead.textContent="NOT LINKED — nothing is reaching the repo";
    det.innerHTML="Your calls live only in this browser. Click <b>link to file…</b> once and pick "
      +"<span class='path'>"+FS_TARGET+"</span>; after that every click writes itself to disk.";
    show("fslink",true);show("fsreconnect",false);show("fssave",false);show("fsunlink",false); return; }
  const name=fsHandle.name||FS_TARGET;
  show("fslink",false); show("fsunlink",true);
  if(fsNeedsGesture){ bar.classList.add("stale");
    lead.textContent="LINKED but NOT WRITING — Chrome needs one click";
    det.innerHTML="The link to <span class='path'>"+esc(name)+"</span> survived the reload, but Chrome "
      +"drops write permission when the tab closes and re-grants it only from a click. Hit "
      +"<b>reconnect</b> — nothing is being saved to disk until you do.";
    show("fsreconnect",true); show("fssave",false); return; }
  show("fsreconnect",false); show("fssave",true);
  if(fsErr){ bar.classList.add("unlinked");
    lead.textContent="LINKED but the last write FAILED";
    det.innerHTML="<b>"+esc(fsErr)+"</b> · target <span class='path'>"+esc(name)+"</span>"
      +(fsLastWrite?" · last good write "+clock(fsLastWrite):" · nothing written yet this session");
    return; }
  bar.classList.add("linked");
  lead.textContent = fsWriting?"LINKED — writing…":fsPending?"LINKED — saving…":"LINKED";
  const t=tally();
  det.innerHTML="Auto-saving to <span class='path'>"+esc(name)+"</span>"
    +(fsLastWrite?" · last written <b>"+clock(fsLastWrite)+"</b> ("+t.struck+" struck, "+t.flag+" flagged)"
                 :" · not written yet this session");
}

async function fsWrite(){
  if(!fsHandle||fsWriting) return false;
  if(DATA.length < FS_MIN_ROWS){
    fsErr="REFUSED to write — only "+DATA.length+" roster rows in memory (needs "+FS_MIN_ROWS
        +"). Under DEFAULT INCLUDE that would have silently un-struck your cuts, so nothing was written.";
    fsStatus(); return false; }
  if(await fsPerm(fsHandle,false)!=="granted"){ fsNeedsGesture=true; fsErr=""; fsStatus(); return false; }
  fsWriting=true; fsStatus();
  try{ const w=await fsHandle.createWritable();
       await w.write(JSON.stringify(payload(),null,2)); await w.close();
       fsLastWrite=new Date(); fsErr=""; fsNeedsGesture=false;
  }catch(e){ fsErr="write failed — "+((e&&e.message)||e); }
  fsWriting=false; fsStatus(); return !fsErr;
}
function fsTouch(){ if(!fsBooted||!fsHandle||fsNeedsGesture) return;
  clearTimeout(fsTimer); fsPending=true; fsStatus();
  fsTimer=setTimeout(()=>{fsPending=false; fsWrite();}, FS_DEBOUNCE); }

/* ---------- state ---------- */
let S={}; try{ S=JSON.parse(localStorage.getItem(LSKEY)||"{}")||{}; }catch(e){ S={}; }
const save=()=>{ try{ localStorage.setItem(LSKEY,JSON.stringify(S)); }catch(e){} fsTouch(); };
const get=id=>S[id]||{state:"build",note:""};
function set(id,patch){ const n=Object.assign({},get(id),patch);
  if(n.state==="build"&&!n.note) delete S[id]; else S[id]=n; save(); }

function tally(){ let struck=0,flag=0;
  DATA.forEach(r=>{const st=get(r.id).state; if(st==="struck")struck++; else if(st==="flag")flag++;});
  return {struck, flag, build: DATA.length-struck}; }

/* 🔑 THE STAMP. `savedAt` is written ONLY here, by the page. A pre-fill generator must
   never emit it, so a consumer can tell the owner's real decisions from our suggestions -
   the failure that once nearly shipped an agent's guesses under his name. */
function payload(){
  const t=tally(), struck=[], flagged=[], notes={};
  DATA.forEach(r=>{ const d=get(r.id);
    if(d.state==="struck") struck.push(r.id);
    else if(d.state==="flag") flagged.push(r.id);
    if(d.note) notes[r.id]=d.note; });
  return { sheet: SHEET, posture: "default-include",
    meaning: "DEFAULT INCLUDE. Every capability in the roster is a build target EXCEPT the ids in `struck`. A row absent from this file was never touched and IS a build target. `flagged` means the owner wants it discussed, not skipped.",
    savedAt: new Date().toISOString(),
    rosterRows: DATA.length, alreadyBuilt: BUILT_N,
    buildCount: t.build, struckCount: t.struck, flaggedCount: t.flag,
    struck, flagged, notes };
}

/* ---------- render ---------- */
const domains=[...new Set(DATA.map(r=>r.domain))];
const fdom=document.getElementById("fdom");
domains.forEach(d=>{const o=document.createElement("option");o.value=d;o.textContent=d;fdom.appendChild(o);});

const main=document.getElementById("main");
main.innerHTML = domains.map(d=>{
  const rows=DATA.filter(r=>r.domain===d);
  return "<section class='group' data-dom='"+esc(d)+"'>"
    + "<div class='ghead'><span class='gn'>"+esc(d)+"</span>"
    + "<span class='gc'>"+rows.length+" · "+rows.filter(r=>r.built).length+" built</span>"
    + "<span class='sp'></span>"
    + "<button data-bulk='build' data-d='"+esc(d)+"'>all build</button>"
    + "<button data-bulk='struck' data-d='"+esc(d)+"'>strike all</button></div>"
    + "<table>" + rows.map(r=>{
      const warn = r.warn ? "<div class='warn"+(r.warn.indexOf("⛔")>=0?" stop":"")+"'>"+esc(r.warn)+"</div>" : "";
      return "<tr id='r_"+esc(r.id)+"' data-id='"+esc(r.id)+"'>"
       + "<td style='width:52%'><div class='nm'>"+esc(r.name)+"</div>"
       + "<div class='ef'>"+esc(r.effect)+"</div>"
       + "<div class='api'>"+esc(r.api)+"</div>" + warn
       + "<textarea class='note' rows='1' placeholder='note…'></textarea></td>"
       + "<td style='width:16%'><span class='chip "+r.diff+"'>"+r.diff+"</span>"
       + (r.built?"<span class='chip built'>BUILT</span>":"") + "</td>"
       + "<td class='acts'><button data-s='build'>build</button> "
       + "<button data-s='struck'>strike</button> "
       + "<button data-s='flag'>flag</button></td></tr>"; }).join("")
    + "</table></section>"; }).join("");

function paint(r){
  const tr=document.getElementById("r_"+r.id); if(!tr) return;
  const d=get(r.id);
  tr.classList.toggle("struck", d.state==="struck");
  tr.classList.toggle("flagged", d.state==="flag");
  tr.querySelectorAll("button[data-s]").forEach(b=>b.classList.toggle("on", b.dataset.s===d.state));
  const n=tr.querySelector(".note"); if(n && n.value!==(d.note||"")) n.value=d.note||"";
}
function retally(){ const t=tally();
  document.getElementById("nBuild").textContent=t.build;
  document.getElementById("nStruck").textContent=t.struck;
  document.getElementById("nFlag").textContent=t.flag; fsStatus(); }

main.addEventListener("click", e=>{
  const bulk=e.target.closest("button[data-bulk]");
  if(bulk){ const d=bulk.dataset.d, st=bulk.dataset.bulk;
    DATA.filter(r=>r.domain===d).forEach(r=>{ set(r.id,{state:st}); paint(r); });
    retally(); return; }
  const b=e.target.closest("button[data-s]"); if(!b) return;
  const id=b.closest("tr").dataset.id, row=DATA.find(r=>r.id===id);
  set(id,{state:b.dataset.s}); paint(row); retally();
});
main.addEventListener("input", e=>{
  if(!e.target.classList.contains("note")) return;
  const id=e.target.closest("tr").dataset.id;
  set(id,{note:e.target.value}); retally();
});

let warnOnly=false;
function filter(){
  const q=document.getElementById("q").value.toLowerCase().trim();
  const dm=fdom.value, df=document.getElementById("fdiff").value,
        bt=document.getElementById("fbuilt").value, st=document.getElementById("fstate").value;
  let shown=0;
  DATA.forEach(r=>{
    const tr=document.getElementById("r_"+r.id); if(!tr) return;
    let ok = (!dm||r.domain===dm) && (!df||r.diff===df)
          && (!bt || (bt==="1")===r.built) && (!st||get(r.id).state===st)
          && (!warnOnly || !!r.warn);
    if(ok && q) ok = (r.name+" "+r.effect+" "+r.api+" "+r.domain).toLowerCase().indexOf(q)>=0;
    tr.classList.toggle("hide", !ok); if(ok) shown++;
  });
  document.querySelectorAll("section.group").forEach(sec=>{
    const any=[...sec.querySelectorAll("tr")].some(t=>!t.classList.contains("hide"));
    sec.classList.toggle("hide", !any); });
  document.getElementById("shown").textContent = shown+" of "+DATA.length+" shown";
}
["q","fdom","fdiff","fbuilt","fstate"].forEach(i=>{
  const e=document.getElementById(i);
  e.addEventListener(i==="q"?"input":"change", filter); });
document.getElementById("fwarn").addEventListener("click", e=>{
  warnOnly=!warnOnly; e.target.classList.toggle("on",warnOnly); filter(); });

document.getElementById("fslink").addEventListener("click", async ()=>{
  try{ const h=await window.showSaveFilePicker({suggestedName:FS_TARGET,
        types:[{description:"JSON",accept:{"application/json":[".json"]}}]});
    fsHandle=h; await idbPut(h); fsNeedsGesture=false; fsErr=""; await fsWrite();
  }catch(e){ if(e && e.name!=="AbortError"){ fsErr=(e.message||e); fsStatus(); } } });
document.getElementById("fsreconnect").addEventListener("click", async ()=>{
  if(!fsHandle) return;
  if(await fsPerm(fsHandle,true)==="granted"){ fsNeedsGesture=false; await fsWrite(); } else fsStatus(); });
document.getElementById("fssave").addEventListener("click", ()=>fsWrite());
document.getElementById("fsunlink").addEventListener("click", async ()=>{
  fsHandle=null; await idbDel(); fsStatus(); });
document.getElementById("fsexport").addEventListener("click", async ()=>{
  const t=JSON.stringify(payload(),null,2);
  try{ await navigator.clipboard.writeText(t); alert("Copied "+t.length+" bytes."); }
  catch(e){ prompt("Copy this:", t); } });

(async function boot(){
  DATA.forEach(paint); retally(); filter();
  if(FS_SUPPORTED){ const h=await idbGet();
    if(h){ fsHandle=h; fsNeedsGesture = (await fsPerm(h,false))!=="granted"; } }
  fsBooted=true; fsStatus();
})();
</script></body></html>
"""
    io.open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote %s — %d rows, %d domains, %d marked BUILT"
          % (OUT, TOTAL, len(D.ROSTER), BUILT))

if __name__ == "__main__":
    build()
