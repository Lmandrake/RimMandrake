#!/usr/bin/env python3
"""Generate the plant cherrypick review sheet.

Reads  design/Jawa/mods/plant_cherrypick_candidates.csv   (190 reachable plants)
       world/ASHKARR_WORLDMAP_tiles.csv                   (biome tile counts)
       design/Jawa/mods/plant_sprites/manifest.json       (optional sprites)
       design/Jawa/mods/plant_decisions.json              (optional, the owner's file)
Writes design/Jawa/mods/plant_review.html

The owner's decisions file is NEVER written by this script. It is read so the
sheet can merge his calls per-row over the prefill.
"""
import base64, csv, json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODS = os.path.join(ROOT, 'design', 'Jawa', 'mods')
CSV  = os.path.join(MODS, 'plant_cherrypick_candidates.csv')
TILES= os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
SPR  = os.path.join(MODS, 'plant_sprites')
OUT  = os.path.join(MODS, 'plant_review.html')

CORE_DESERT = {'Desert', 'ExtremeDesert', 'AridShrubland'}
GROUPS = [
    ('A', 'Core desert — this is what you were looking at',
     'Desert · ExtremeDesert · AridShrubland. 7,863 tiles, 36% of the planet. Anything here is in the raids, the caravans and every screenshot.'),
    ('B', 'Rocky Crags — the single biggest biome',
     "AB_RockyCrags, 4,703 tiles. ⚠️ Its only wood comes from Alpha Biomes toxic flora. Cut those and the biggest biome on Ash'karr has no wood at all."),
    ('C', 'Oasis and Badlands — the green exceptions',
     'ZBiome_DesertOasis 227 · ZBiome_Badlands 546 · ZBiome_Grasslands 233. Small, deliberate, and the only place lush growth is meant to read as correct.'),
    ('D', 'Wasteland and Scarlands',
     'Wasteland 1,721 · Scarlands 90. Dead ground; the flora here is meant to look like it lost.'),
    ('E', 'Exotic biomes — decide the BIOME first, not the plant',
     "Mycotic Jungle 1,939 · Poison Forest 604 · Propane Lakes 554 · Feralisk Jungle 534 · Fungal Forest 425 · Crystal Caverns 127 and smaller. \U0001f511 These are left UNDECIDED on purpose — the real question is whether the biome belongs on Ash'karr."),
    ('F', 'Marginal — under 100 tiles',
     'Volcano 23 · LavaField 15 · Ocular Forest 3 · Mechanoid Intrusion 236 · Tar Pits 57 · Miasmic Mangrove 65 · Gelatinous Superorganism 96. Almost never seen.'),
]
GROUP_BIOMES = {
    'B': {'AB_RockyCrags'},
    'C': {'ZBiome_DesertOasis', 'ZBiome_Badlands', 'ZBiome_Grasslands'},
    'D': {'Wasteland', 'Scarlands'},
    'F': {'Volcano', 'LavaField', 'AB_OcularForest', 'AB_MechanoidIntrusion',
          'AB_TarPits', 'AB_MiasmicMangrove', 'AB_GelatinousSuperorganism',
          'AB_PyroclasticConflagration'},
}

def tile_counts():
    c = collections.Counter()
    with open(TILES, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            c[r['biome']] += 1
    return c

def group_of(biomes):
    if biomes & CORE_DESERT: return 'A'
    for g in ('B', 'C', 'D', 'F'):
        if biomes & GROUP_BIOMES[g]: return g
    return 'E'

DESERT_READS = ('cactus', 'saguaro', 'agave', 'palm', 'succulent', 'yucca',
                'aloe', 'scrub', 'brush', 'sage', 'grass', 'moss', 'lichen',
                'shrub', 'thistle', 'weed', 'dead', 'snag', 'bramble')

def decide(r, biomes, wood_lifeline):
    """Returns (state, rule, note). state: keep | cut | undecided

    wood_lifeline is computed AFTER a provisional pass, so it only protects a
    plant whose loss would actually leave a biome short — not every plant in a
    biome that happens to have few wood sources.
    """
    name = r['label'].lower()
    tree = r['isTree'] == 'True'
    g = group_of(biomes)
    if r['defName'] in wood_lifeline:
        return 'keep', 'R3', 'LAST WOOD — cutting this leaves its biome with too few wood sources.'
    if g == 'E':
        return 'undecided', 'R4', 'Only appears in an exotic biome. Decide the biome, not the plant.'
    if not tree:
        return 'keep', 'R5', 'Groundcover. Cutting it makes the desert emptier, not drier.'
    if g == 'A':
        if any(k in name for k in DESERT_READS):
            return 'keep', 'R2', 'Reads as desert flora — this is the register we want.'
        return 'cut', 'R1', 'A TREE in the core desert that does not read as desert flora.'
    return 'keep', 'R2', 'Confined to a biome where growth is meant to read as correct.'

def main():
    rows = list(csv.DictReader(open(CSV, encoding='utf-8')))
    tiles = tile_counts()

    # Wood safety, done in two passes so R3 protects only what actually matters.
    # Pass 1: decide with NO lifelines, to see which plants R1 would really cut.
    # Pass 2: for every biome, if those cuts would leave it under MIN_WOOD sources,
    #         reinstate the cut wood-providers there and mark them lifelines.
    MIN_WOOD = 2
    bwood = collections.defaultdict(list)
    for r in rows:
        if r['harvestedThingDef'] == 'WoodLog':
            for b in r['biomes'].split('|'):
                if b in tiles: bwood[b].append(r['defName'])

    provisional = {}
    for r in rows:
        biomes = {b for b in r['biomes'].split('|') if b in tiles}
        provisional[r['defName']] = decide(r, biomes, set())[0]

    lifeline = set()
    for b, ws in bwood.items():
        if tiles[b] < 100:
            continue
        surviving = [w for w in ws if provisional[w] != 'cut']
        if len(surviving) < MIN_WOOD:
            # reinstate the ones we were going to cut, largest-reach last
            cut_here = [w for w in ws if provisional[w] == 'cut']
            need = MIN_WOOD - len(surviving)
            lifeline.update(cut_here[:max(0, need)])
        # a biome that ALREADY has under MIN_WOOD before any cut: protect all of them
        if len(ws) < MIN_WOOD:
            lifeline.update(ws)

    sprites = {}
    man = os.path.join(SPR, 'manifest.json')
    if os.path.exists(man):
        try:
            m = json.load(open(man, encoding='utf-8'))
            for d, info in m.items():
                if info.get('missing'): continue
                p = os.path.join(SPR, info.get('file', d + '.png'))
                if os.path.exists(p) and os.path.getsize(p) < 200000:
                    sprites[d] = base64.b64encode(open(p, 'rb').read()).decode('ascii')
        except Exception as e:
            print(f'  sprites: manifest unreadable ({e}); shipping without', file=sys.stderr)

    items = []
    for r in rows:
        biomes = {b for b in r['biomes'].split('|') if b in tiles}
        state, rule, note = decide(r, biomes, lifeline)
        reach = int(r['tilesReachable'])
        bits = []
        if r['isTree'] == 'True': bits.append('TREE')
        if r['harvestedThingDef'] == 'WoodLog': bits.append('wood')
        elif r['harvestedThingDef']: bits.append(r['harvestedThingDef'])
        try: bits.append(f"{float(r['growDays']):g}d")
        except (ValueError, TypeError): pass
        items.append({
            'd': r['defName'], 'l': r['label'], 'm': r['mod'],
            'g': group_of(biomes), 't': r['isTree'] == 'True',
            'w': r['harvestedThingDef'] == 'WoodLog',
            'r': reach, 'pct': round(100.0 * reach / 21872, 1),
            'b': sorted(biomes), 'eff': ' · '.join(bits),
            's': state, 'rule': rule, 'note': note,
            'life': r['defName'] in lifeline,
            'img': sprites.get(r['defName'], ''),
        })
    items.sort(key=lambda x: (x['g'], -x['r']))

    payload = json.dumps({'items': items, 'groups': GROUPS,
                          'generated': 'plant_review.html'}, ensure_ascii=False)
    html = TEMPLATE.replace('/*__DATA__*/', payload)
    open(OUT, 'w', encoding='utf-8').write(html)
    n = collections.Counter(i['s'] for i in items)
    print(f"wrote {OUT}")
    print(f"  {len(items)} plants · prefill: keep {n['keep']} · cut {n['cut']} · undecided {n['undecided']}")
    print(f"  sprites embedded: {len(sprites)}/{len(items)}")
    print(f"  wood lifelines protected: {len(lifeline)}")

TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ash'karr plant cherrypick</title><style>
*{box-sizing:border-box}
body{margin:0;background:#14161a;color:#d8dbe0;font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}
header{padding:10px 20px 0;background:#1b1e24;border-bottom:1px solid #2c313a}
h1{display:inline-block}
details.brief{margin:8px 0 0}
details.brief>summary{cursor:pointer;color:#7fa8d0;font-size:12.5px;padding:4px 0;list-style:none;user-select:none}
details.brief>summary::-webkit-details-marker{display:none}
details.brief>summary:before{content:'\25b8 ';color:#5a616b}
details.brief[open]>summary:before{content:'\25be '}
details.brief>summary:hover{color:#a8c8e8}
#stick{position:sticky;top:0;z-index:50;background:#1b1e24;border-bottom:1px solid #2c313a;padding:8px 20px}
h1{margin:0 0 2px;font-size:17px;color:#fff}
.sub{color:#8b929e;font-size:12.5px}
.panel{margin:8px 0 0;padding:10px 12px;border-radius:7px;background:#20242b;border-left:3px solid #d08a3e;font-size:12.5px;color:#c3c8d0}
.panel.crit{border-left-color:#d4574e}
.panel b{color:#fff}
.panel ul{margin:6px 0 0;padding-left:18px}
.panel li{margin:3px 0}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
input[type=search],select{background:#14161a;border:1px solid #333a45;color:#d8dbe0;padding:6px 9px;border-radius:5px;font-size:13px}
input[type=search]{min-width:220px}
.count{font-size:12.5px;color:#8b929e;margin-left:auto;text-align:right}
.count b{color:#fff}
.k{color:#5fb87a}.c{color:#e0685e}.u{color:#c99a3e}
main{padding:0 20px 60px}
.grp{margin-top:26px}
.gh{padding:9px 12px;background:#1b1e24;border:1px solid #2c313a;border-radius:7px 7px 0 0}
.gh.stick{position:sticky;top:53px;z-index:20}
.gh h2{margin:0;font-size:14.5px;color:#fff}
.gh p{margin:3px 0 0;font-size:12px;color:#8b929e}
.gh .acts{margin-top:7px;display:flex;gap:6px}
button{background:#262b33;border:1px solid #39404b;color:#c3c8d0;padding:4px 9px;border-radius:4px;cursor:pointer;font-size:12px}
button:hover{background:#2f3540;color:#fff}
table{width:100%;border-collapse:collapse;background:#181b21;border:1px solid #2c313a;border-top:0}
td{padding:7px 9px;border-top:1px solid #23272f;vertical-align:top}
tr.cut{background:#241a1a}tr.undec{background:#241f16}
.spr{width:44px}.spr img{width:40px;height:40px;object-fit:contain;image-rendering:pixelated;background:#0e1013;border-radius:4px}
.nospr{width:40px;height:40px;background:#1e222a;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#4a515c;font-size:9px}
.nm{font-weight:600;color:#fff}
.dn{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#6d7583}
.eff{font-size:12px;color:#9aa2ad;margin-top:2px}
.why{font-size:11.5px;color:#7d8590;margin-top:3px;font-style:italic}
.tags{margin-top:3px}
.tag{display:inline-block;font-size:10px;padding:1px 5px;border-radius:3px;background:#262b33;color:#8b929e;margin-right:4px}
.tag.tree{background:#3a2f1c;color:#d0a95e}
.tag.life{background:#1e3524;color:#6fc98c}
.tag.rule{background:#2a2436;color:#a48fd0}
.reach{width:88px;text-align:right;font-size:12px;color:#9aa2ad;white-space:nowrap}
.reach b{color:#d8dbe0;display:block;font-size:13px}
.dec{width:158px;white-space:nowrap}
.dec button{margin-right:3px;min-width:44px}
.dec button.on[data-s=keep]{background:#2c5138;border-color:#3f7a50;color:#fff}
.dec button.on[data-s=cut]{background:#5c2b2b;border-color:#8a3f3f;color:#fff}
.dec button.on[data-s=undecided]{background:#4d3d1c;border-color:#7a642f;color:#fff}
.note{width:100%;margin-top:5px;background:#0f1115;border:1px dashed #3a414c;color:#c9b98a;padding:4px 6px;border-radius:4px;font-size:12px;font-family:inherit}
.bio{font-size:11px;color:#666d78;margin-top:3px}
footer{position:fixed;bottom:0;left:0;right:0;background:#1b1e24;border-top:1px solid #2c313a;padding:8px 20px;display:flex;gap:10px;align-items:center;font-size:12.5px;z-index:60}
#link{color:#8b929e}#link b{color:#5fb87a}#link.bad b{color:#e0685e}
.hidden{display:none}
</style></head><body>
<header>
<h1>Ash'karr — plant cherrypick</h1>
<div class="sub">190 plants that can appear on this planet, of 669 installed. <b>Default is KEEP</b> — only what you mark <span class="c">CUT</span> is stripped, so anything you never look at stays in.</div>
<details class="brief"><summary>the five rules I pre-filled with, and the one finding that shrinks this job</summary>
<div class="panel crit"><b>🔴 Rules I invented to pre-fill this. Overrule any of them in one line.</b>
<ul>
<li><b>R1 — a TREE in the core desert that does not read as desert flora is CUT.</b> This is your complaint, and it turns out to be only three plants.</li>
<li><b>R2 — cacti, saguaro, agave, palms and scrub STAY.</b> They are the Tatooine register; a desert with no succulents reads as a parking lot.</li>
<li><b>R3 — nothing is cut if it is the last wood in a biome.</b> Hard constraint, overrules R1. Cutting a rung out of a progression is how a tech tree ends up with a gap nobody notices.</li>
<li><b>R4 — flora confined to an exotic biome is left UNDECIDED on purpose.</b> The real question there is whether Mycotic Jungle or Poison Forest belong on Ash'karr at all, and that is a biome call, not a plant call.</li>
<li><b>R5 — non-tree groundcover STAYS.</b> Cutting it makes the desert emptier, not drier.</li>
</ul></div>

<div class="panel"><b>⭐ The finding that shrinks this job.</b> Of 51 trees, only <b>five</b> reach Desert / ExtremeDesert / AridShrubland — and two of those are the pebble cactus and the saguaro, which you want. So the whole of your complaint is <b>three plants</b>: <span class="c">Plant_TreeDrago</span>, <span class="c">BMT_Plant_TreeTwistingThornwood</span> and <span class="c">BMT_Plant_TreeMartyr</span>. Cutting all three costs <b>no wood at all</b> — pebble cactus and saguaro both drop WoodLog and both survive. The other 46 trees only exist in biomes that are themselves exotic.
<br><br>⚠️ <b>The one place this could break something:</b> AB_RockyCrags is the largest biome on the planet at 4,703 tiles, and every wood source in it is Alpha Biomes toxic flora. Those are marked <span class="k">LAST WOOD</span> and pre-set to keep.</div>

</details>
</header>
<div id="stick"><div class="bar">
<input type="search" id="q" placeholder="search name, defName, mod, effect…">
<select id="fs"><option value="">all decisions</option><option value="keep">keep</option><option value="cut">cut</option><option value="undecided">undecided</option></select>
<select id="ft"><option value="">trees + groundcover</option><option value="tree">trees only</option><option value="ground">groundcover only</option></select>
<select id="fm"><option value="">all mods</option></select>
<div class="count" id="count"></div>
</div></div>
<main id="main"></main>
<footer>
<button id="btnlink">Link to file…</button>
<button id="btncopy">Copy JSON</button>
<span id="link">not linked — <b>your work is in this browser only</b></span>
</footer>
<script>
const DATA = /*__DATA__*/;
const ITEMS = DATA.items, GROUPS = DATA.groups;
const LSKEY = 'ashkarr_plants_v1';
let state = {};   // defName -> {s, note}
let fileHandle = null, dirty = false;

/* ---------- persistence ---------- */
function loadLocal(){ try{ return JSON.parse(localStorage.getItem(LSKEY)||'{}'); }catch(e){ return {}; } }
function saveLocal(){ try{ localStorage.setItem(LSKEY, JSON.stringify(state)); }catch(e){} }

// Merge PER ROW: a row the human touched is left alone; untouched rows take the prefill.
function seed(){
  const prior = loadLocal();
  let kept = 0, filled = 0;
  for(const it of ITEMS){
    if(prior[it.d] && prior[it.d].touched){ state[it.d] = prior[it.d]; kept++; }
    else { state[it.d] = {s: it.s, note: (prior[it.d]&&prior[it.d].note)||'', touched:false}; filled++; }
  }
  if(kept) console.log(`Filled ${filled} rows from the prefill, kept your ${kept} existing decisions untouched.`);
}

function payload(extra){
  const dec = {};
  for(const it of ITEMS){ const s = state[it.d];
    dec[it.d] = {decision: s.s, note: s.note||'', label: it.l, mod: it.m, touched: !!s.touched}; }
  const o = Object.assign({
    posture: 'blacklist',
    postureMeaning: "Default is KEEP. Only entries with decision=='cut' go on the Cherry Picker kill list. An undecided entry STAYS in the game.",
    savedBy: 'plant_review.html',          // only this page ever writes these two
    savedAt: new Date().toISOString(),
    decidedCount: Object.values(state).filter(s=>s.touched).length,
    total: ITEMS.length,
    decisions: dec
  }, extra||{});
  return o;
}

// A whole-file writer must carry through top-level keys it does not own.
let carried = {};
async function writeFile(){
  if(!fileHandle) return;
  const touched = Object.values(state).filter(s=>s.touched).length;
  const total = ITEMS.length;
  // refuse a truncating write
  if(total < 50){ setLink('refused — implausible row count', true); return; }
  try{
    const w = await fileHandle.createWritable();
    await w.write(JSON.stringify(Object.assign({}, carried, payload()), null, 2));
    await w.close();
    setLink('saved ' + new Date().toLocaleTimeString() + ' · ' + touched + ' of ' + total + ' touched');
  }catch(e){ setLink('write failed: ' + e.message, true); }
}
let t=null;
function queueWrite(){ saveLocal(); if(!fileHandle) return; clearTimeout(t); t=setTimeout(writeFile,900); }
function setLink(msg, bad){ const el=document.getElementById('link'); el.className = bad?'bad':''; el.innerHTML = fileHandle ? ('linked · <b>'+msg+'</b>') : ('not linked — <b>your work is in this browser only</b>'); }

document.getElementById('btnlink').onclick = async ()=>{
  if(!window.showSaveFilePicker){ alert("This browser has no File System Access API (Firefox does not). Use Copy JSON and paste it into design/Jawa/mods/plant_decisions.json"); return; }
  try{
    fileHandle = await window.showSaveFilePicker({suggestedName:'plant_decisions.json',
      types:[{description:'JSON',accept:{'application/json':['.json']}}]});
    // read what is already there and carry unknown top-level keys through
    try{ const f = await fileHandle.getFile(); const txt = await f.text();
      if(txt.trim()){ const j = JSON.parse(txt);
        for(const k of Object.keys(j)) if(!['posture','postureMeaning','savedBy','savedAt','decidedCount','total','decisions'].includes(k)) carried[k]=j[k];
        if(j.decisions) for(const d in j.decisions){ if(state[d] && j.decisions[d].touched){ state[d]={s:j.decisions[d].decision,note:j.decisions[d].note||'',touched:true}; } }
      }
    }catch(e){}
    render(); await writeFile();
  }catch(e){}
};
document.getElementById('btncopy').onclick = ()=>{
  navigator.clipboard.writeText(JSON.stringify(payload(),null,2))
    .then(()=>setLink('copied to clipboard'),()=>alert('clipboard blocked'));
};

/* ---------- render ---------- */
function set(d, s){ state[d].s = s; state[d].touched = true; queueWrite(); render(); }
function setNote(d, v){ state[d].note = v; state[d].touched = true; queueWrite(); }
function bulk(g, s){ for(const it of ITEMS) if(it.g===g && visible(it)) { state[it.d].s=s; state[it.d].touched=true; } queueWrite(); render(); }

let q='', fs='', ft='', fm='';
function visible(it){
  if(fs && state[it.d].s!==fs) return false;
  if(ft==='tree' && !it.t) return false;
  if(ft==='ground' && it.t) return false;
  if(fm && it.m!==fm) return false;
  if(q){ const h=(it.l+' '+it.d+' '+it.m+' '+it.eff+' '+it.note).toLowerCase(); if(!h.includes(q)) return false; }
  return true;
}
function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

function render(){
  const main=document.getElementById('main'); main.innerHTML='';
  let nk=0,nc=0,nu=0;
  for(const it of ITEMS){ const s=state[it.d].s; if(s==='keep')nk++; else if(s==='cut')nc++; else nu++; }
  document.getElementById('count').innerHTML =
    `<b class="k">${nk}</b> keep · <b class="c">${nc}</b> will be stripped · <b class="u">${nu}</b> undecided <span style="color:#5a616b">(undecided stays)</span>`;

  for(const [gid,gtitle,gdesc] of GROUPS){
    const rows = ITEMS.filter(it=>it.g===gid && visible(it));
    if(!rows.length) continue;
    const div=document.createElement('div'); div.className='grp';
    // sticky headers cover short groups — disable for <=3 rows
    const stick = rows.length>3 ? ' stick' : '';
    div.innerHTML = `<div class="gh${stick}"><h2>${esc(gtitle)}</h2><p>${gdesc}</p>
      <div class="acts"><span style="font-size:11.5px;color:#6d7583;align-self:center">${rows.length} shown —</span>
      <button onclick="bulk('${gid}','keep')">keep all</button>
      <button onclick="bulk('${gid}','cut')">cut all</button>
      <button onclick="bulk('${gid}','undecided')">clear</button></div></div>
      <table><tbody>${rows.map(row).join('')}</tbody></table>`;
    main.appendChild(div);
  }
}
function row(it){
  const s=state[it.d];
  const cls = s.s==='cut'?' class="cut"' : (s.s==='undecided'?' class="undec"':'');
  const img = it.img ? `<img src="data:image/png;base64,${it.img}" alt="">` : `<div class="nospr">no art</div>`;
  const bio = it.b.length>4 ? it.b.slice(0,4).join(', ')+' +'+(it.b.length-4) : it.b.join(', ');
  return `<tr${cls}>
  <td class="spr">${img}</td>
  <td><div class="nm">${esc(it.l)}</div><div class="dn">${esc(it.d)} · ${esc(it.m)}</div>
    <div class="eff">${esc(it.eff)}</div>
    <div class="tags">${it.t?'<span class="tag tree">TREE</span>':''}${it.life?'<span class="tag life">LAST WOOD</span>':''}<span class="tag rule">${it.rule}</span></div>
    <div class="why">${esc(it.note)}</div>
    <div class="bio">${esc(bio)}</div>
    <input class="note" placeholder="your note…" value="${esc(s.note||'')}" oninput="setNote('${it.d}',this.value)">
  </td>
  <td class="reach"><b>${it.r.toLocaleString()}</b>tiles · ${it.pct}%</td>
  <td class="dec">
    <button data-s="keep" class="${s.s==='keep'?'on':''}" onclick="set('${it.d}','keep')">keep</button>
    <button data-s="cut" class="${s.s==='cut'?'on':''}" onclick="set('${it.d}','cut')">cut</button>
    <button data-s="undecided" class="${s.s==='undecided'?'on':''}" onclick="set('${it.d}','undecided')">?</button>
  </td></tr>`;
}
/* ---------- boot ---------- */
seed();
const mods=[...new Set(ITEMS.map(i=>i.m))].sort();
document.getElementById('fm').innerHTML='<option value="">all mods</option>'+mods.map(m=>`<option>${esc(m)}</option>`).join('');
document.getElementById('q').oninput=e=>{q=e.target.value.toLowerCase();render();};
document.getElementById('fs').onchange=e=>{fs=e.target.value;render();};
document.getElementById('ft').onchange=e=>{ft=e.target.value;render();};
document.getElementById('fm').onchange=e=>{fm=e.target.value;render();};
render(); setLink('');
</script></body></html>'''

if __name__ == '__main__':
    main()
