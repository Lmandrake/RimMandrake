/* mineral numbers sheet: row body, editable cells, snapshot-on-save */
(function(){
const MATS = CFG.materials || [];
const PL = new Set(["gold","silver","rough gem (Minerals Sparkle)","jade","diamond","ruby","sapphire","magnetite","uraninite","uranium"]);
const fmt = n => (Math.round(n*100)/100).toString();
const units = c => Math.round((c.cur !== undefined ? c.cur : c.v) * c.size).toLocaleString();
function curV(it,c){ const r=DEC[it.id]; const v=r&&r.values&&r.values[c.m]; return v===undefined?c.v:v; }
function curR(it,c){ const r=DEC[it.id]; const v=r&&r.rivers&&r.rivers[c.m]; return v===undefined?c.rv:v; }
const PROV = {intent:['doc intent','#5ac37f','a biome doc / built def / ruling says this biome HAS it; the number is still a guess'],
  guess:['guess','#e8b64c','agent guess, presence and number'],
  'owner-intent-zero':['0 by intent','#98a2b3','owner: some biomes have no iron - listed 0 on purpose'],
  zero:['0','#5f6b7a','registry says none here']};
function cellRow(it,c){
  if (c.unb) return `<tr class="mn"><td>${esc(c.m)}</td><td colspan="3" class="sub">unbounded - sieve output is labour-limited, no deposit count</td></tr>`;
  const v=curV(it,c), ch = Math.abs(v-c.v)>1e-9, p=PROV[c.prov]||PROV.guess;
  const tip=`${esc(c.basis)}. Registry value ${c.raw.toLocaleString()} ${c.yr?'units/yr':'units'} per map = ${fmt(c.v)} ${c.yr?'sources':'deposits'} of ${c.size} units.`;
  return `<tr class="mn"><td>${esc(c.m)}${c.yr?' <span class="sub">(sources/yr)</span>':''}</td>
   <td><input class="num${ch?' chg':''}" type="number" step="any" min="0" data-k="v" data-m="${esc(c.m)}" value="${v}" title="${tip}"></td>
   <td class="sub u" title="units per deposit: ${c.size}">${units({cur:v,size:c.size})} ${c.yr?'/yr':'units'}</td>
   <td><span class="pv" style="color:${p[1]};border-color:${p[1]}" title="${esc(p[2])}">${p[0]}</span></td></tr>`;
}
window.itemBody = it => {
  const nz = it.cells.filter(c=>c.unb||curV(it,c)>0), z = it.cells.filter(c=>!c.unb&&!(curV(it,c)>0));
  const pl = it.cells.filter(c=>!c.unb&&PL.has(c.m));
  const marks = [];
  if (it.bare) marks.push('<span class="mark absent">bare biome - local rock only</span>');
  const nint = it.cells.filter(c=>c.prov==='intent').length;
  if (nint) marks.push(`<span class="mark absent">${nint} cells doc-intent</span>`);
  const seaNote = it.id.includes('SeabedFloor') ? '<div class="sub">Sea floor: no rivers, rivers-carry fixed at 0 (assumption; edit if wrong).</div>' : '';
  return `<div class="effect">${esc(it.effect)}</div><div class="marks">${marks.join('')}</div>
  <div class="mntab"><table class="mt"><thead><tr><th>material</th><th>deposits per map</th><th>about</th><th>provenance</th></tr></thead>
  <tbody>${nz.map(c=>cellRow(it,c)).join('')||'<tr><td colspan=4 class="sub">nothing present</td></tr>'}</tbody></table>
  <details><summary>${z.length} zero materials (editable - set above 0 to add one)</summary>
  <table class="mt"><tbody>${z.map(c=>cellRow(it,c)).join('')}</tbody></table></details>
  <div class="rvh">What the rivers carry <span class="sub">(placer bars per map, for panning and sluice - all guesses: half the local deposit count)</span></div>
  ${seaNote}<table class="mt"><tbody>${pl.map(c=>{const r=curR(it,c),ch=Math.abs(r-c.rv)>1e-9;
   return `<tr class="mn"><td>${esc(c.m)}</td><td><input class="num${ch?' chg':''}" type="number" step="any" min="0" data-k="rv" data-m="${esc(c.m)}" value="${r}" title="placer bars per map; guess = half local deposits (min 0.1), proposed ${c.rv}"></td><td><span class="pv" style="color:#e8b64c;border-color:#e8b64c">guess</span></td></tr>`;}).join('')}</tbody></table></div>`;
};
// snapshot full numbers into the record on every queued save, so the file alone is buildable
const _q = queue;
queue = function(id){
  const it=byId.get(id), r=DEC[id];
  if (it && r) {
    r.values = Object.assign(Object.fromEntries(it.cells.filter(c=>!c.unb).map(c=>[c.m,c.v])), r.values||{});
    r.rivers = Object.assign(Object.fromEntries(it.cells.filter(c=>!c.unb&&PL.has(c.m)).map(c=>[c.m,c.rv])), r.rivers||{});
    r.changed = it.cells.filter(c=>!c.unb && (Math.abs(r.values[c.m]-c.v)>1e-9 || (PL.has(c.m)&&Math.abs(r.rivers[c.m]-c.rv)>1e-9))).map(c=>c.m);
    r.unitNote = 'values are DEPOSITS PER MAP (regrowing sources: sources per map); rivers are placer bars per map';
  }
  return _q(id);
};
el('list').addEventListener('input', e => {
  const t=e.target; if(!t.classList||!t.classList.contains('num')) return;
  const id=t.closest('.row').dataset.id, it=byId.get(id); if(!it||frozen) return;
  const n=parseFloat(t.value); if(!(n>=0)) { t.style.outline='2px solid #e06c6c'; return; } t.style.outline='';
  const rec = DEC[id] || (DEC[id]={decision:'',note:'',prefill:null});
  const k=t.dataset.k, m=t.dataset.m, c=it.cells.find(x=>x.m===m);
  if(k==='v'){ rec.values=rec.values||{}; rec.values[m]=n; t.classList.toggle('chg',Math.abs(n-c.v)>1e-9);
     const u=t.closest('tr').querySelector('.u'); if(u) u.textContent=units({cur:n,size:c.size})+(c.yr?' /yr':' units'); }
  else { rec.rivers=rec.rivers||{}; rec.rivers[m]=n; t.classList.toggle('chg',Math.abs(n-c.rv)>1e-9); }
  queue(id); paintCounts();
});
const st=document.createElement('style');
st.textContent=`.mntab{margin-top:6px;max-width:720px}.mt{border-collapse:collapse;width:100%;font-size:12px}
.mt th{text-align:left;color:var(--dim);font-weight:500;font-size:11px;padding:2px 6px}.mt td{padding:2px 6px;border-top:1px solid #171b21}
input.num{width:96px;background:#0c1420;border:1px solid #2b3a4d;border-radius:4px;padding:2px 6px;color:#dff0ff}
input.num.chg{background:#2a1d06;border-color:var(--accent)}
.pv{font-size:10.5px;border:1px solid;border-radius:3px;padding:0 5px}
.rvh{margin-top:8px;font-weight:600;color:var(--accent);font-size:12px}details{margin-top:4px;font-size:12px}summary{cursor:pointer;color:var(--dim)}
.sizetab td,.sizetab th{padding:1px 8px;text-align:left;font-size:11.5px}`;
document.head.appendChild(st);
const sz=document.getElementById('sizetab');
if(sz) sz.outerHTML='<table class="sizetab">'+MATS.map(m=>`<tr><td>${esc(m.m)}</td><td>${m.size} units</td><td>${esc(m.basis)}</td></tr>`).join('')+'</table>';
})();
