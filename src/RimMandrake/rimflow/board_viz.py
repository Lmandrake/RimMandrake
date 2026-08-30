#!/usr/bin/env python3
"""board_viz.py — render the mirrored GitHub tickets as a self-contained HTML board.

QUEUE_GITHUB_MIRROR_1's sibling: github_mirror.py pushes rimflow items to GitHub
Issues one-way; this script reads the SAME ledger plus the SAME mirror map
(infrastructure/state/ledger/github_mirror_map.json) and renders a relationship
graph + kanban board of exactly the items that are mirrored — nothing invented,
nothing the ledger doesn't already say.

Effort and importance have no ledger field. They are INFERRED from each item's
prose file (infrastructure/state/items/<ID>.md) by a small heuristic — checklist
size, word count, distinct file-paths touched, owner-flag (\U0001F534) density, fan-out
(how many other mirrored items this one caused), and blocking pressure. The
heuristic and its reasoning per item ship INSIDE the page (click any card/node),
labelled as inferred, never presented as ledger fact.

Relationships drawn are exactly the ledger's own edges: caused_by, superseded_by,
blocked_on — read via rimflow.model.replay(), never guessed from prose.

Regenerate any time: `python3 src/RimMandrake/rimflow/board_viz.py`
(reads the live ledger + the current mirror map; writes the one output file).
Rerun `github_mirror.py --apply` FIRST if the mirror map might be stale.
"""
import json
import os
import re
import sys
import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "RimMandrake"))
from rimflow import model

ITEMS_DIR = os.path.join(REPO_ROOT, "infrastructure", "state", "items")
MAP_PATH = os.path.join(REPO_ROOT, "infrastructure", "state", "ledger", "github_mirror_map.json")
OUT_PATH = os.path.join(REPO_ROOT, "infrastructure", "state", "board", "tickets_board.html")
GH_REPO = "Lmandrake/RimMaster"


def read_prose(iid):
    p = os.path.join(ITEMS_DIR, iid + ".md")
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def infer_effort(prose):
    if not prose:
        return "M", "no prose file on disk — defaulted, not inferred"
    checks = re.findall(r"^- \[[ xX]\]", prose, re.M)
    words = len(prose.split())
    paths = set(re.findall(r"[A-Za-z0-9_./\\-]+\.(?:cs|xml|py|json|md|png)", prose))
    score = len(checks) * 2 + words / 120.0 + len(paths) * 1.5
    reason = "%d checklist line(s), %d words, %d file path(s) named" % (len(checks), words, len(paths))
    if score < 6:
        return "S", reason
    if score < 16:
        return "M", reason
    if score < 32:
        return "L", reason
    return "XL", reason


def infer_importance(prose, item, fanout_count, blockers_count):
    score = 0
    bits = []
    if prose:
        flags = len(re.findall(u"\U0001F534", prose))
        if flags:
            score += flags * 2
            bits.append(u"%d owner-flag(\U0001F534) marker(s)" % flags)
        if re.search(r"[Oo]wner[,:].{0,40}verbatim", prose) or re.search(r"[Oo]wner \(verbatim\)", prose):
            score += 2
            bits.append("carries a verbatim owner quote")
        if re.search(r"\bcanon\b", prose, re.I):
            score += 1
            bits.append("touches canon")
    if fanout_count:
        score += fanout_count
        bits.append("caused %d other mirrored item(s)" % fanout_count)
    if blockers_count:
        score += blockers_count * 2
        bits.append("blocks %d mirrored item(s)" % blockers_count)
    if item.needs == "owner":
        score += 1
        bits.append("needs:owner")
    if item.blocked:
        score += 1
        bits.append("currently blocked")
    if score >= 6:
        tier = "critical"
    elif score >= 3:
        tier = "high"
    elif score >= 1:
        tier = "medium"
    else:
        tier = "low"
    return tier, ("; ".join(bits) if bits else "no strong signal found in prose or the ledger")


def build_tickets():
    world = model.replay()
    with open(MAP_PATH) as f:
        mmap = json.load(f)

    caused_by_counts, blocked_on_counts = {}, {}
    for iid, it in world.items.items():
        if it.caused_by and it.caused_by in mmap:
            caused_by_counts[it.caused_by] = caused_by_counts.get(it.caused_by, 0) + 1
        if it.blocked_on and it.blocked_on in mmap:
            blocked_on_counts[it.blocked_on] = blocked_on_counts.get(it.blocked_on, 0) + 1

    out = []
    for iid, info in mmap.items():
        it = world.items.get(iid)
        if it is None:
            continue
        prose = read_prose(iid)
        effort, effort_why = infer_effort(prose)
        importance, importance_why = infer_importance(
            prose, it, caused_by_counts.get(iid, 0), blocked_on_counts.get(iid, 0))
        out.append({
            "id": iid,
            "issue": info.get("number"),
            "gh_open": info.get("open"),
            "title": it.title,
            "kind": it.kind,
            "owner": it.owner,
            "needs": it.needs,
            "state": it.state,
            "open": it.open,
            "blocked": it.blocked,
            "blocked_reason": it.blocked_reason,
            "blocked_on": it.blocked_on if it.blocked_on in mmap else None,
            "caused_by": it.caused_by if it.caused_by in mmap else None,
            "superseded_by": it.superseded_by if it.superseded_by in mmap else None,
            "effort": effort,
            "effort_why": effort_why,
            "importance": importance,
            "importance_why": importance_why,
            "has_prose": bool(prose),
        })
    out.sort(key=lambda r: r["id"])
    return out


TEMPLATE = r"""<!doctype html>
<title>__TITLE__</title>
<style>
:root{
  --bg:#eeece4; --surface:#ffffff; --surface-2:#f7f5ee; --border:#dcd6c6;
  --ink:#2a241d; --ink-2:#655c4d; --ink-3:#948a76;
  --accent:#1f8f83; --accent-ink:#ffffff;
  --st-proposed:#6341c8; --st-ready:#419bc8; --st-doing:#a3720f; --st-blocked:#c84c41;
  --st-done:#279b57; --st-dropped:#948a76; --st-superseded:#c841c8;
  --shadow: 0 1px 2px rgba(30,25,15,.08), 0 4px 16px rgba(30,25,15,.06);
  color-scheme: light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#171310; --surface:#211c17; --surface-2:#271f19; --border:#3a3025;
    --ink:#f1e9db; --ink-2:#c2b6a0; --ink-3:#8d8271;
    --accent:#39c8b8; --accent-ink:#0d1a17;
    --st-proposed:#845ed7; --st-ready:#3aa0d6; --st-doing:#c99a2e; --st-blocked:#e2645a;
    --st-done:#37b06a; --st-dropped:#8d8271; --st-superseded:#d268c9;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
    color-scheme: dark;
  }
}
:root[data-theme="dark"]{
  --bg:#171310; --surface:#211c17; --surface-2:#271f19; --border:#3a3025;
  --ink:#f1e9db; --ink-2:#c2b6a0; --ink-3:#8d8271;
  --accent:#39c8b8; --accent-ink:#0d1a17;
  --st-proposed:#845ed7; --st-ready:#3aa0d6; --st-doing:#c99a2e; --st-blocked:#e2645a;
  --st-done:#37b06a; --st-dropped:#8d8271; --st-superseded:#d268c9;
  --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
  color-scheme: dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,sans-serif;font-size:14px;line-height:1.5}
code,.mono,.id,.stat-n,.chip{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace}
h1,h2,h3{text-wrap:balance;margin:0}
a{color:var(--accent)}

header.top{position:sticky;top:0;z-index:20;background:var(--surface);
  border-bottom:1px solid var(--border);padding:14px 20px;display:flex;
  align-items:center;gap:20px;flex-wrap:wrap;box-shadow:var(--shadow)}
header.top .brand{display:flex;flex-direction:column;gap:2px;margin-right:auto}
header.top .brand .name{font-weight:700;font-size:17px;letter-spacing:.2px}
header.top .brand .sub{color:var(--ink-3);font-size:12px}
.stat-row{display:flex;gap:14px;flex-wrap:wrap}
.stat{display:flex;flex-direction:column;align-items:center;min-width:44px}
.stat .stat-n{font-size:17px;font-weight:600}
.stat .stat-l{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3)}
.tabs{display:flex;gap:4px;background:var(--surface-2);border:1px solid var(--border);
  border-radius:8px;padding:3px}
.tab{padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;color:var(--ink-2);
  user-select:none}
.tab.active{background:var(--accent);color:var(--accent-ink);font-weight:600}
.ghlink{font-size:12px;color:var(--ink-2);text-decoration:none;border:1px solid var(--border);
  padding:6px 10px;border-radius:6px;white-space:nowrap}
.ghlink:hover{border-color:var(--accent);color:var(--accent)}

.filters{position:sticky;top:64px;z-index:19;background:var(--bg);
  border-bottom:1px solid var(--border);padding:10px 20px;display:flex;gap:10px;
  flex-wrap:wrap;align-items:center}
.filters input[type=search]{background:var(--surface);border:1px solid var(--border);
  border-radius:6px;color:var(--ink);padding:6px 10px;font-size:13px;width:220px}
.fgroup{display:flex;gap:4px;flex-wrap:wrap}
.fchip{border:1px solid var(--border);background:var(--surface);color:var(--ink-2);
  border-radius:999px;padding:4px 10px;font-size:11.5px;cursor:pointer;user-select:none}
.fchip.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.fclear{font-size:11.5px;color:var(--ink-3);cursor:pointer;text-decoration:underline;
  text-underline-offset:2px}

main{padding:18px 20px 60px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--ink-2);
  margin:0 0 14px;align-items:center}
.legend .lg-group{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.note{font-size:11.5px;color:var(--ink-3);max-width:640px}

/* ---- graph view ---- */
#graphwrap{background:var(--surface);border:1px solid var(--border);border-radius:10px;
  overflow:hidden;position:relative}
#graph{width:100%;display:block;cursor:grab}
#graph:active{cursor:grabbing}
.gnode circle{stroke-width:2px}
.gnode text{font-family:"IBM Plex Mono",monospace;font-size:9px;fill:var(--ink-2);
  pointer-events:none}
.glink{stroke:var(--ink-3);stroke-opacity:.55;fill:none}
.glink.superseded{stroke-dasharray:3,3}
.glink.blocks{stroke:var(--st-blocked);stroke-opacity:.8}
.gnode.dim{opacity:.18}
.glink.dim{opacity:.06}

/* ---- board view ---- */
#board{display:grid;grid-template-columns:repeat(6,minmax(200px,1fr));gap:12px;
  overflow-x:auto}
.col{background:var(--surface-2);border:1px solid var(--border);border-radius:10px;
  padding:10px;min-width:200px;display:flex;flex-direction:column;gap:8px}
.col h3{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;
  display:flex;justify-content:space-between;color:var(--ink-2)}
.card{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--ink-3);
  border-radius:8px;padding:9px 10px;cursor:pointer;box-shadow:var(--shadow)}
.card:hover{border-color:var(--accent)}
.card .id{font-size:11px;font-weight:600;word-break:break-word}
.card .title{font-size:12px;color:var(--ink-2);margin-top:3px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card .chips{margin-top:6px;display:flex;gap:5px;flex-wrap:wrap}
.chip{font-size:9.5px;padding:2px 6px;border-radius:5px;background:var(--surface-2);
  border:1px solid var(--border);color:var(--ink-2)}
.chip.imp-critical{background:var(--st-blocked);color:#fff;border-color:transparent}
.chip.imp-high{background:color-mix(in srgb, var(--st-blocked) 35%, var(--surface-2));
  color:var(--ink);border-color:transparent}

/* ---- detail drawer ---- */
#scrim{position:fixed;inset:0;background:rgba(10,8,5,.35);display:none;z-index:29}
#drawer{position:fixed;top:0;right:0;height:100%;width:min(420px,92vw);background:var(--surface);
  border-left:1px solid var(--border);box-shadow:var(--shadow);transform:translateX(100%);
  transition:transform .18s ease;z-index:30;overflow-y:auto;padding:20px}
#drawer.open{transform:translateX(0)}
#scrim.show{display:block}
#drawer h2{font-size:15px;margin-bottom:2px}
#drawer .dtitle{color:var(--ink-2);font-size:13px;margin-bottom:14px}
#drawer .drow{display:flex;justify-content:space-between;gap:10px;padding:6px 0;
  border-bottom:1px solid var(--border);font-size:12.5px}
#drawer .drow .k{color:var(--ink-3)}
#drawer .rel{font-size:12.5px;margin:4px 0;padding:6px 8px;background:var(--surface-2);
  border-radius:6px}
#drawer .why{font-size:12px;color:var(--ink-2);background:var(--surface-2);
  border-radius:6px;padding:8px;margin-top:6px}
#drawer .why b{color:var(--ink)}
#drawer .close{position:absolute;top:14px;right:16px;cursor:pointer;color:var(--ink-3);
  font-size:18px;line-height:1;background:none;border:none}
#drawer a.ghbtn{display:inline-block;margin-top:14px;background:var(--accent);
  color:var(--accent-ink);padding:7px 12px;border-radius:6px;font-size:12.5px;
  text-decoration:none;font-weight:600}
[hidden]{display:none!important}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">

<header class="top">
  <div class="brand">
    <div class="name">Mirrored Tickets — RimMaster</div>
    <div class="sub">rimflow ledger → GitHub Issues mirror, visualized — generated __GENERATED_AT__</div>
  </div>
  <div class="stat-row" id="statrow"></div>
  <div class="tabs">
    <div class="tab active" data-view="graph">Graph</div>
    <div class="tab" data-view="board">Board</div>
  </div>
  <a class="ghlink" href="https://github.com/__GH_REPO__/issues" target="_blank" rel="noopener">Issues on GitHub ↗</a>
</header>

<div class="filters">
  <input type="search" id="search" placeholder="Filter by ID or title…">
  <div class="fgroup" id="f-state"></div>
  <div class="fgroup" id="f-needs"></div>
  <span class="fclear" id="fclear" hidden>clear filters</span>
</div>

<main>
  <div class="legend">
    <div class="lg-group"><b>State:</b>
      <span><span class="dot" style="background:var(--st-proposed)"></span> proposed</span>
      <span><span class="dot" style="background:var(--st-ready)"></span> ready</span>
      <span><span class="dot" style="background:var(--st-doing)"></span> doing</span>
      <span><span class="dot" style="background:var(--st-blocked)"></span> blocked</span>
      <span><span class="dot" style="background:var(--st-done)"></span> done</span>
      <span><span class="dot" style="background:var(--st-superseded)"></span> superseded/dropped</span>
    </div>
    <div class="lg-group"><b>Node size</b> = inferred effort (S→XL) &nbsp; <b>ring width</b> = inferred importance &nbsp; <b>◆ diamond</b> = blocked (shape, not just color)</div>
    <div class="lg-group"><b>Edges:</b> solid → caused-by &nbsp; dashed → superseded-by &nbsp; <span style="color:var(--st-blocked)">red</span> → blocked-on</div>
  </div>
  <p class="note">Relationships are read straight from the rimflow ledger (caused_by / superseded_by / blocked_on) —
  nothing here is invented. <b>Effort and importance have no ledger field</b>; both are inferred per item from its prose
  file by a small heuristic (checklist size, word count, file-paths named, owner-flag density, how many other mirrored
  items it caused, how many it blocks). Click any node or card to see the reasoning and mark it as what it is: an
  inference, not a ledger fact.</p>

  <div id="graphwrap"><svg id="graph"></svg></div>
  <div id="board" hidden></div>
</main>

<div id="scrim"></div>
<div id="drawer">
  <button class="close" id="drawerclose">✕</button>
  <div id="drawerbody"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script id="ticket-data" type="application/json">__TICKETS_JSON__</script>
<script>
const DATA = JSON.parse(document.getElementById('ticket-data').textContent);
const GH_REPO = "__GH_REPO__";
const STATE_COLOR = {proposed:'var(--st-proposed)', ready:'var(--st-ready)', doing:'var(--st-doing)',
  blocked:'var(--st-blocked)', done:'var(--st-done)', dropped:'var(--st-dropped)', superseded:'var(--st-superseded)'};
const EFFORT_R = {S:9, M:13, L:17, XL:22};
const IMP_W = {low:1.5, medium:2.5, high:4, critical:6};
const byId = Object.fromEntries(DATA.map(d => [d.id, d]));

function displayState(d){ return d.blocked ? 'blocked' : d.state; }

// ---------- stat row ----------
(function(){
  const counts = {};
  DATA.forEach(d => { const s = displayState(d); counts[s] = (counts[s]||0)+1; });
  const order = ['proposed','ready','doing','blocked','done'];
  const row = document.getElementById('statrow');
  order.forEach(s => {
    if(!counts[s]) return;
    const el = document.createElement('div');
    el.className = 'stat';
    el.innerHTML = `<span class="stat-n" style="color:${STATE_COLOR[s]}">${counts[s]}</span><span class="stat-l">${s}</span>`;
    row.appendChild(el);
  });
})();

// ---------- filter chips ----------
let activeState = null, activeNeeds = null, searchQ = '';
function chipRow(container, values, activeGetter, setter){
  values.forEach(v => {
    const c = document.createElement('span');
    c.className = 'fchip'; c.textContent = v;
    c.onclick = () => { setter(activeGetter() === v ? null : v); render(); };
    container.appendChild(c);
  });
}
chipRow(document.getElementById('f-state'),
  ['proposed','ready','doing','blocked','done','dropped','superseded'],
  () => activeState, v => activeState = v);
chipRow(document.getElementById('f-needs'),
  [...new Set(DATA.map(d=>d.needs))].sort(),
  () => activeNeeds, v => activeNeeds = v);
document.getElementById('search').addEventListener('input', e => { searchQ = e.target.value.toLowerCase(); render(); });
document.getElementById('fclear').onclick = () => {
  activeState = null; activeNeeds = null; searchQ = '';
  document.getElementById('search').value = '';
  render();
};

function matches(d){
  if(activeState && displayState(d) !== activeState) return false;
  if(activeNeeds && d.needs !== activeNeeds) return false;
  if(searchQ && !(d.id.toLowerCase().includes(searchQ) || (d.title||'').toLowerCase().includes(searchQ))) return false;
  return true;
}

function syncChipUI(){
  document.querySelectorAll('#f-state .fchip').forEach(c => c.classList.toggle('on', c.textContent === activeState));
  document.querySelectorAll('#f-needs .fchip').forEach(c => c.classList.toggle('on', c.textContent === activeNeeds));
  document.getElementById('fclear').hidden = !(activeState || activeNeeds || searchQ);
}

// ---------- drawer ----------
const drawer = document.getElementById('drawer'), scrim = document.getElementById('scrim');
function openDrawer(d){
  const rel = [];
  if(d.caused_by) rel.push(`caused by <b>${d.caused_by}</b>`);
  if(d.blocked_on) rel.push(`blocked on <b>${d.blocked_on}</b>`);
  if(d.superseded_by) rel.push(`superseded by <b>${d.superseded_by}</b>`);
  const causes = DATA.filter(x => x.caused_by === d.id).map(x=>x.id);
  if(causes.length) rel.push(`caused: ${causes.map(c=>`<b>${c}</b>`).join(', ')}`);
  const blocks = DATA.filter(x => x.blocked_on === d.id).map(x=>x.id);
  if(blocks.length) rel.push(`blocks: ${blocks.map(c=>`<b>${c}</b>`).join(', ')}`);
  document.getElementById('drawerbody').innerHTML = `
    <h2>${d.id}</h2>
    <div class="dtitle">${(d.title||'').replace(/</g,'&lt;')}</div>
    <div class="drow"><span class="k">state</span><span>${displayState(d)}${d.blocked?' — '+(d.blocked_reason||''):''}</span></div>
    <div class="drow"><span class="k">owner (seat)</span><span>${d.owner||'—'}</span></div>
    <div class="drow"><span class="k">needs</span><span>${d.needs}</span></div>
    <div class="drow"><span class="k">effort (inferred)</span><span>${d.effort}</span></div>
    <div class="drow"><span class="k">importance (inferred)</span><span>${d.importance}</span></div>
    ${rel.length ? '<div style="margin-top:10px">'+rel.map(r=>`<div class="rel">${r}</div>`).join('')+'</div>' : ''}
    <div class="why"><b>Why this effort:</b> ${d.effort_why}</div>
    <div class="why"><b>Why this importance:</b> ${d.importance_why}</div>
    ${d.issue ? `<a class="ghbtn" target="_blank" rel="noopener" href="https://github.com/${GH_REPO}/issues/${d.issue}">Open issue #${d.issue} on GitHub ↗</a>` : '<div class="note" style="margin-top:10px">Not yet mirrored to an issue.</div>'}
  `;
  drawer.classList.add('open'); scrim.classList.add('show');
}
document.getElementById('drawerclose').onclick = () => { drawer.classList.remove('open'); scrim.classList.remove('show'); };
scrim.onclick = document.getElementById('drawerclose').onclick;

// ---------- tabs ----------
document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  const v = t.dataset.view;
  document.getElementById('graphwrap').hidden = v !== 'graph';
  document.getElementById('board').hidden = v !== 'board';
});

// ---------- board view ----------
const COLS = [
  {key:'proposed', label:'Proposed'}, {key:'ready', label:'Ready'},
  {key:'doing', label:'Doing'}, {key:'blocked', label:'Blocked'},
  {key:'done', label:'Done'}, {key:'closed', label:'Superseded / Dropped'},
];
function renderBoard(){
  const board = document.getElementById('board');
  board.innerHTML = '';
  COLS.forEach(col => {
    const colEl = document.createElement('div'); colEl.className = 'col';
    let items = DATA.filter(matches).filter(d => {
      if(col.key === 'closed') return d.state === 'dropped' || d.state === 'superseded';
      return displayState(d) === col.key;
    });
    const h = document.createElement('h3');
    h.innerHTML = `<span>${col.label}</span><span>${items.length}</span>`;
    colEl.appendChild(h);
    items.forEach(d => {
      const c = document.createElement('div');
      c.className = 'card';
      c.style.borderLeftColor = STATE_COLOR[displayState(d)] || 'var(--ink-3)';
      c.innerHTML = `<div class="id">${d.id}</div><div class="title">${(d.title||'').replace(/</g,'&lt;')}</div>
        <div class="chips">
          <span class="chip">${d.effort}</span>
          <span class="chip imp-${d.importance}">${d.importance}</span>
          <span class="chip">${d.needs}</span>
          ${d.issue ? `<span class="chip">#${d.issue}</span>` : ''}
        </div>`;
      c.onclick = () => openDrawer(d);
      colEl.appendChild(c);
    });
    board.appendChild(colEl);
  });
}

// ---------- graph view ----------
let sim, svg, gLink, gNode;
function buildGraph(){
  const w = document.getElementById('graphwrap').clientWidth || 900, h = 560;
  svg = d3.select('#graph').attr('viewBox', [0,0,w,h]);
  svg.selectAll('*').remove();
  const zoomG = svg.append('g');
  svg.call(d3.zoom().scaleExtent([0.3,3]).on('zoom', ev => zoomG.attr('transform', ev.transform)));

  const nodes = DATA.map(d => Object.assign({}, d));
  const links = [];
  nodes.forEach(d => {
    if(d.caused_by && byId[d.caused_by]) links.push({source:d.caused_by, target:d.id, type:'caused'});
    if(d.superseded_by && byId[d.superseded_by]) links.push({source:d.id, target:d.superseded_by, type:'superseded'});
    if(d.blocked_on && byId[d.blocked_on]) links.push({source:d.blocked_on, target:d.id, type:'blocks'});
  });

  sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(70).strength(0.35))
    .force('charge', d3.forceManyBody().strength(-90))
    .force('center', d3.forceCenter(w/2, h/2))
    .force('collide', d3.forceCollide(d => EFFORT_R[d.effort] + 6));

  gLink = zoomG.append('g').selectAll('path').data(links).join('path')
    .attr('class', d => 'glink ' + (d.type === 'superseded' ? 'superseded' : d.type === 'blocks' ? 'blocks' : ''))
    .attr('stroke-width', 1.3);

  gNode = zoomG.append('g').selectAll('g').data(nodes).join('g')
    .attr('class', 'gnode')
    .style('cursor','pointer')
    .call(d3.drag()
      .on('start', (ev,d) => { if(!ev.active) sim.alphaTarget(0.2).restart(); d.fx=d.x; d.fy=d.y; })
      .on('drag', (ev,d) => { d.fx=ev.x; d.fy=ev.y; })
      .on('end', (ev,d) => { if(!ev.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));

  // Blocked items get a DIAMOND, not a circle — a colorblind-safe cue for the
  // one state most worth spotting at a glance, independent of the hue check.
  gNode.each(function(d){
    const r = EFFORT_R[d.effort] || 12;
    const sel = d3.select(this);
    const shape = d.blocked
      ? sel.append('rect').attr('x', -r*0.78).attr('y', -r*0.78)
          .attr('width', r*1.56).attr('height', r*1.56)
          .attr('transform', 'rotate(45)')
      : sel.append('circle').attr('r', r);
    shape.attr('fill', STATE_COLOR[displayState(d)])
      .attr('fill-opacity', (d.state==='dropped'||d.state==='superseded') ? 0.35 : 0.85)
      .attr('stroke', STATE_COLOR[displayState(d)])
      .attr('stroke-width', IMP_W[d.importance] || 1.5);
  });

  gNode.append('text')
    .attr('dy', d => (EFFORT_R[d.effort]||12) + 11)
    .attr('text-anchor','middle')
    .text(d => d.id.length > 22 ? d.id.slice(0,20)+'…' : d.id);

  gNode.on('click', (ev,d) => openDrawer(d));
  gNode.on('mouseenter', (ev,d) => highlight(d.id));
  gNode.on('mouseleave', () => highlight(null));

  sim.on('tick', () => {
    gLink.attr('d', d => `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`);
    gNode.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  function highlight(id){
    if(!id){ gNode.classed('dim', false); gLink.classed('dim', false); return; }
    const neigh = new Set([id]);
    links.forEach(l => { if(l.source.id===id) neigh.add(l.target.id); if(l.target.id===id) neigh.add(l.source.id); });
    gNode.classed('dim', d => !neigh.has(d.id));
    gLink.classed('dim', l => l.source.id!==id && l.target.id!==id);
  }
  applyGraphFilter();
}
function applyGraphFilter(){
  if(!gNode) return;
  gNode.style('display', d => matches(d) ? null : 'none');
}

function render(){
  syncChipUI();
  renderBoard();
  applyGraphFilter();
}

buildGraph();
render();
window.addEventListener('resize', () => { buildGraph(); });
</script>
"""


def main():
    tickets = build_tickets()
    html = TEMPLATE
    html = html.replace("__TITLE__", "Mirrored Tickets")
    html = html.replace("__GENERATED_AT__", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    html = html.replace("__GH_REPO__", GH_REPO)
    payload = json.dumps(tickets).replace("</script", "<\\/script")
    html = html.replace("__TICKETS_JSON__", payload)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d tickets)" % (OUT_PATH, len(tickets)))


if __name__ == "__main__":
    main()
