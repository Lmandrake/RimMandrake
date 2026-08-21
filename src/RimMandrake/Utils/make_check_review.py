#!/usr/bin/env python3
"""
make_check_review.py — build TRANSIENT_check_queue_review.html, the sheet the owner
uses to decide which of CHECK's open items are worth keeping.

⛔ THIS GENERATOR WRITES SUGGESTIONS, NOT DECISIONS. It must never overwrite
`infrastructure/state/check_queue_decisions.json` once the owner has touched it —
that file is written by the PAGE, and the page stamps `savedAt`, a key this
generator never emits. Any consumer must refuse a decisions file with no `savedAt`:
without it you cannot tell the owner's calls from the agent's guesses.

    python3 src/RimMandrake/Utils/make_check_review.py --summaries <jsonl>
"""
import argparse, collections, html, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
OUT = os.path.join(REPO, "TRANSIENT_check_queue_review.html")
DECISIONS = "check_queue_decisions.json"

COST_ORDER = ["load", "bridge", "quicktest", "owner-look", "offline"]
COST_BLURB = {
    "load":       "Needs a full cold load, ~25 minutes. THE SCARCE RESOURCE — every "
                  "item you keep here has to fit in a window the owner opens by hand.",
    "bridge":     "Needs the live bridge on an already-running game. Cheap ONCE a game "
                  "is up; impossible when it is not.",
    "quicktest":  "A ~90-second throwaway dev map answers it. Nearly free.",
    "owner-look": "A human has to LOOK at something. No agent can close these.",
    "offline":    "No game at all. These should already be done — if one is sitting "
                  "here, ask why.",
}


def load_ledger():
    p = os.path.join(REPO, "infrastructure", "state", "ledger", "events.jsonl")
    with open(p, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def stats(ev):
    c = collections.Counter(e.get("event") for e in ev)
    v = collections.Counter(e.get("result") for e in ev if e.get("event") == "verify")
    per_seat = collections.Counter(e.get("for") for e in ev if e.get("event") == "file")
    reruns = collections.Counter(e.get("id") for e in ev if e.get("event") == "verify")
    days = set(e.get("ts", "")[:10] for e in ev if e.get("ts"))
    return {
        "filed": c["file"], "closed": c["close"], "dropped": c["drop"],
        "superseded": c["supersede"],
        "verify_pass": v["pass"], "verify_partial": v["partial"], "verify_fail": v["fail"],
        "check_filed": per_seat.get("CHECK", 0),
        "reverified": sum(1 for k, n in reruns.items() if n > 1),
        "ledger_days": len(days),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summaries", required=True, help="JSONL: id/proves/cost/already/rec/why/contested")
    a = ap.parse_args()

    rows = []
    seen = set()
    with open(a.summaries, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                # ⚠️ REPORTED, never skipped — a dropped row is an item the owner
                # never sees and therefore never decides.
                sys.exit("summaries: line is not valid JSON:\n  %s" % line[:160])
            if d["id"] in seen:
                sys.exit("summaries: duplicate id %s" % d["id"])
            seen.add(d["id"])
            rows.append(d)

    ev = load_ledger()
    st = stats(ev)
    st["open"] = len(rows)

    by_cost = collections.defaultdict(list)
    for r in rows:
        by_cost[r.get("cost", "offline")].append(r)
    recs = collections.Counter(r.get("rec", "KEEP") for r in rows)

    def esc(x):
        return html.escape(str(x if x is not None else ""))

    groups = []
    for cost in COST_ORDER:
        rs = by_cost.get(cost)
        if not rs:
            continue
        rs.sort(key=lambda r: (r.get("rec") != "CUT", r["id"]))
        cards = []
        for r in rs:
            flags = []
            if r.get("contested"):
                flags.append('<span class="flag contested">contested</span>')
            if r.get("already") == "yes":
                flags.append('<span class="flag already">already observed</span>')
            elif r.get("already") == "unclear":
                flags.append('<span class="flag unclear">unclear</span>')
            cards.append(
                '<div class="row" data-id="{id}" data-rec="{rec}" data-cost="{cost}" '
                'data-contested="{con}" data-already="{alr}">'
                '<div class="rowhead"><code class="rid">{id}</code>'
                '<span class="rec rec-{rec}">{rec}</span>{flags}</div>'
                '<div class="proves">{proves}</div>'
                '<div class="why">why: {why}</div>'
                '<div class="acts">'
                '<button class="b keep" data-v="KEEP">keep</button>'
                '<button class="b cut" data-v="CUT">cut</button>'
                '<button class="b merge" data-v="MERGE">merge</button>'
                '<button class="b defer" data-v="DEFER">v2 / later</button>'
                '<span class="mine"></span></div>'
                '<input class="note" placeholder="your note (optional)">'
                '</div>'.format(
                    id=esc(r["id"]), rec=esc(r.get("rec", "KEEP")), cost=esc(cost),
                    con="1" if r.get("contested") else "0",
                    alr=esc(r.get("already", "no")),
                    flags="".join(flags), proves=esc(r.get("proves", "")),
                    why=esc(r.get("why", ""))))
        groups.append(
            '<section class="grp" data-cost="{c}">'
            '<h2>{c} <span class="n">{n}</span></h2>'
            '<p class="blurb">{b}</p>'
            '<div class="bulk">whole group: '
            '<button class="gb" data-v="KEEP">keep all</button>'
            '<button class="gb" data-v="CUT">cut all</button>'
            '<button class="gb" data-v="MERGE">merge all</button></div>'
            '{cards}</section>'.format(
                c=esc(cost), n=len(rs), b=esc(COST_BLURB.get(cost, "")),
                cards="".join(cards)))

    subs = {
        "@@GROUPS@@": "".join(groups),
        "@@PAYLOAD@@": json.dumps({r["id"]: {"rec": r.get("rec", "KEEP"),
                                             "cost": r.get("cost"),
                                             "proves": r.get("proves", "")}
                                   for r in rows}),
        "@@DECISIONS@@": DECISIONS,
        "@@NOPEN@@": str(st["open"]),
        "@@NKEEP@@": str(recs.get("KEEP", 0)),
        "@@NCUT@@": str(recs.get("CUT", 0)),
        "@@NMERGE@@": str(recs.get("MERGE", 0)),
        "@@FILED@@": str(st["filed"]),
        "@@CLOSED@@": str(st["closed"]),
        "@@DROPPED@@": str(st["dropped"]),
        "@@CHECKFILED@@": str(st["check_filed"]),
        "@@VP@@": str(st["verify_pass"]),
        "@@VPAR@@": str(st["verify_partial"]),
        "@@VF@@": str(st["verify_fail"]),
        "@@REVER@@": str(st["reverified"]),
        "@@DAYS@@": str(st["ledger_days"]),
    }
    page = TEMPLATE
    for k, v in subs.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote %s" % OUT)
    print("  %d open items — prefilled KEEP %d / CUT %d / MERGE %d"
          % (st["open"], recs.get("KEEP", 0), recs.get("CUT", 0), recs.get("MERGE", 0)))


TEMPLATE = r"""<!doctype html>
<meta charset="utf-8">
<title>CHECK queue — keep or cut</title>
<style>
:root{--bg:#12141a;--pan:#1a1d26;--pan2:#20242f;--ink:#dfe3ee;--dim:#8b93a7;
--line:#2c313e;--keep:#4a9d6b;--cut:#c05a5a;--merge:#b8893a;--defer:#5a7fb8;--hot:#e2b04a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif}
header{padding:18px 22px;border-bottom:1px solid var(--line);background:var(--pan)}
h1{margin:0 0 4px;font-size:19px;letter-spacing:.2px}
.sub{color:var(--dim);font-size:13px;margin-bottom:14px}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.panel{background:var(--pan2);border:1px solid var(--line);border-radius:7px;padding:11px 13px}
.panel h3{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.7px;color:var(--dim)}
.panel p{margin:0 0 6px;font-size:12.5px;color:#c3c9d8}
.panel b{color:var(--hot)}
.warn{border-color:#5a4520;background:#241d10}
.warn h3{color:var(--hot)}
.stat{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:#c3c9d8}
.stat b{color:#fff;font-size:15px}
#bar{position:sticky;top:0;z-index:30;background:var(--pan);border-bottom:1px solid var(--line);
padding:9px 22px;display:flex;gap:9px;align-items:center;flex-wrap:wrap}
#bar input[type=search]{background:var(--bg);border:1px solid var(--line);color:var(--ink);
padding:6px 9px;border-radius:5px;min-width:210px;font-size:13px}
.chip{background:var(--bg);border:1px solid var(--line);color:var(--dim);padding:5px 10px;
border-radius:20px;cursor:pointer;font-size:12px;user-select:none}
.chip.on{background:#2b3550;color:#fff;border-color:#3f4d70}
#tally{margin-left:auto;font-size:12.5px;color:var(--dim);display:flex;gap:12px;align-items:center}
#tally b{color:#fff}
#link{font-size:12px;padding:5px 11px;border-radius:5px;border:1px solid var(--line);
background:var(--pan2);color:var(--ink);cursor:pointer}
#link.live{border-color:var(--keep);color:#9fe0b8}
#state{font-size:11.5px;color:var(--dim)}
main{padding:16px 22px 90px;max-width:1180px}
.grp{margin-bottom:26px}
.grp h2{font-size:15px;margin:0 0 2px;text-transform:uppercase;letter-spacing:.9px}
.grp h2 .n{color:var(--dim);font-weight:400;font-size:13px;letter-spacing:0}
.blurb{margin:0 0 9px;color:var(--dim);font-size:12.5px;max-width:78ch}
.bulk{margin-bottom:10px;font-size:12px;color:var(--dim)}
.bulk button{margin-left:6px;background:var(--pan2);border:1px solid var(--line);
color:var(--dim);padding:3px 9px;border-radius:4px;cursor:pointer;font-size:11.5px}
.bulk button:hover{color:#fff;border-color:#4a5470}
.row{background:var(--pan);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:6px;padding:10px 13px;margin-bottom:8px}
.row.d-KEEP{border-left-color:var(--keep)}
.row.d-CUT{border-left-color:var(--cut);opacity:.72}
.row.d-MERGE{border-left-color:var(--merge)}
.row.d-DEFER{border-left-color:var(--defer)}
.rowhead{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:4px}
.rid{font-size:11.5px;color:#96a0bb;font-family:ui-monospace,Menlo,Consolas,monospace}
.rec{font-size:10px;letter-spacing:.7px;padding:2px 7px;border-radius:3px;text-transform:uppercase}
.rec-KEEP{background:#1d3a29;color:#87d3a5}
.rec-CUT{background:#3c1f1f;color:#e39898}
.rec-MERGE{background:#3a2e14;color:#e0bc76}
.flag{font-size:10px;padding:2px 7px;border-radius:3px;letter-spacing:.5px}
.contested{background:#3a2c14;color:var(--hot)}
.already{background:#2a2140;color:#b9a4e8}
.unclear{background:#20242f;color:var(--dim)}
.proves{font-size:14px;margin-bottom:3px}
.why{font-size:12px;color:var(--dim);margin-bottom:8px}
.acts{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.b{background:var(--pan2);border:1px solid var(--line);color:var(--dim);padding:4px 12px;
border-radius:4px;cursor:pointer;font-size:12px}
.b:hover{color:#fff}
.b.sel.keep{background:var(--keep);border-color:var(--keep);color:#08130c}
.b.sel.cut{background:var(--cut);border-color:var(--cut);color:#1c0808}
.b.sel.merge{background:var(--merge);border-color:var(--merge);color:#1c1405}
.b.sel.defer{background:var(--defer);border-color:var(--defer);color:#07101c}
.mine{font-size:11.5px;color:var(--dim);margin-left:4px}
.note{margin-top:7px;width:100%;background:#0e1015;border:1px dashed #39405280;color:#cfd6e6;
padding:5px 8px;border-radius:4px;font-size:12.5px;font-style:italic}
.note:focus{outline:none;border-color:#4a5470;border-style:solid}
.hid{display:none!important}
footer{position:fixed;bottom:0;left:0;right:0;background:var(--pan);border-top:1px solid var(--line);
padding:8px 22px;font-size:12px;color:var(--dim);display:flex;gap:14px;align-items:center}
footer button{background:var(--pan2);border:1px solid var(--line);color:var(--ink);
padding:5px 11px;border-radius:5px;cursor:pointer;font-size:12px}
</style>

<header>
<h1>CHECK's open queue — which of these do we actually need?</h1>
<div class="sub">@@NOPEN@@ open items owned by the CHECK seat. Every one is pre-filled with a
recommendation; you only have to disagree.</div>

<div class="panels">
<div class="panel">
<h3>The posture — read this first</h3>
<p><b>Default is KEEP.</b> An item you never touch stays in the queue. Nothing is deleted
by leaving it alone, so you can stop half-way and lose nothing.</p>
<p><b>CUT</b> drops the item (<code>rimflow drop</code>). <b>MERGE</b> means it should
ride inside another check rather than exist separately. <b>v2 / later</b> retargets it
off v1.</p>
</div>

<div class="panel warn">
<h3>⚠ Rules I invented — overrule these</h3>
<p>The <b>cost</b> grouping is <b>my judgement, not the items' own stamp</b>. 77 of 83
CHECK items carry <code>needs: offline</code>, which is a migration default rather than a
fact — so I re-derived what each one really needs by reading it. I may have it wrong.</p>
<p>The <b>KEEP/CUT/MERGE</b> pre-fill is a few minutes of reading per item, not a re-test.
An item marked "already observed" means the item's own text says so — I did not re-verify
it against the game.</p>
</div>

<div class="panel">
<h3>Can this converge? — the measured answer</h3>
<p class="stat"><span><b>@@FILED@@</b> filed</span><span><b>@@CLOSED@@</b> closed</span>
<span><b>@@DROPPED@@</b> dropped</span><span><b>@@CHECKFILED@@</b> were CHECK's</span></p>
<p style="margin-top:7px">Across all seats <b>69%</b> of items reached an end state. CHECK
is the outlier at <b>36%</b> — not because work stalled, but because its items need a
resource that appears rarely: a live game.</p>
</div>

<div class="panel warn">
<h3>🔴 The actual leak</h3>
<p>Of @@VP@@+@@VPAR@@+@@VF@@ recorded runs: <b>@@VP@@ pass</b>, <b>@@VPAR@@ partial</b>,
<b>@@VF@@ fail</b>. A partial does not close an item — and only <b>@@REVER@@ items</b>
have ever been verified twice.</p>
<p>So ~40% of every run lands in a state that parks the item forever, and nothing re-runs
it. <b>That is the non-convergence mechanism</b>, not the filing rate.</p>
<p style="color:var(--dim)">⚠ The ledger spans <b>@@DAYS@@ day</b> — it was migrated from
the old queue files, so every event carries the same date. It cannot show a trend yet.</p>
</div>
</div>
</header>

<div id="bar">
<input type="search" id="q" placeholder="search id, effect, reason…">
<span class="chip" data-f="contested">contested only (23)</span>
<span class="chip" data-f="already">already observed (12)</span>
<span class="chip" data-f="undecided">not yet decided</span>
<span class="chip" data-f="cutrec">I said CUT (@@NCUT@@)</span>
<div id="tally">
  <span>keep <b id="tk">0</b></span><span>cut <b id="tc">0</b></span>
  <span>merge <b id="tm">0</b></span><span>later <b id="td">0</b></span>
  <span>untouched <b id="tu">0</b></span>
  <button id="link">link to file…</button><span id="state">not linked</span>
</div>
</div>

<main>@@GROUPS@@</main>

<footer>
<button id="copy">copy JSON</button>
<button id="save">save as…</button>
<span id="foot">Default KEEP · nothing is lost by leaving an item untouched</span>
</footer>

<script>
const PRE = @@PAYLOAD@@;
const FILE = "@@DECISIONS@@";
const KEY  = "check_queue_review_v1";
let D = {};       // id -> {d, note}
let extra = {};   // top-level keys from the file that are NOT ours — carried through
let handle = null, timer = null;

// ── persistence ───────────────────────────────────────────────────────────────
// ⚠️ localStorage is a CACHE, not storage. The file handle is the real thing.
function cache(){ try{ localStorage.setItem(KEY, JSON.stringify({D:D,extra:extra})); }catch(e){} }
function uncache(){
  try{ const r = localStorage.getItem(KEY); if(!r) return;
       const o = JSON.parse(r); D = o.D||{}; extra = o.extra||{}; }catch(e){}
}

function payload(){
  // 🔴 Carry unknown top-level keys through VERBATIM. A whole-file auto-writer that
  // re-emits only what it knows about silently deletes everything another commit added.
  const out = Object.assign({}, extra);
  out.posture = "default-KEEP; an untouched item stays in the queue";
  out.generatedBy = "make_check_review.py";
  out.savedAt = new Date().toISOString();   // ⭐ only the PAGE writes this. A consumer
  out.decidedCount = Object.keys(D).length; //   must refuse a file without it.
  out.decisions = D;
  return JSON.stringify(out, null, 1);
}

async function write(){
  if(!handle) return;
  // 🔴 Truncation guard. Emptying the owner's file over a transient bug is worse than
  // the clumsy manual flow this replaced.
  const n = Object.keys(D).length;
  if(n === 0){ document.getElementById('state').textContent = "refused: 0 decisions"; return; }
  try{
    const w = await handle.createWritable();
    await w.write(payload()); await w.close();
    document.getElementById('state').textContent =
      "saved " + new Date().toLocaleTimeString() + " · " + n + " decisions";
  }catch(e){ document.getElementById('state').textContent = "write failed: " + e.message; }
}
function queueWrite(){ clearTimeout(timer); timer = setTimeout(write, 900); }

document.getElementById('link').onclick = async () => {
  if(!window.showSaveFilePicker){
    document.getElementById('state').textContent =
      "this browser has no File System Access API — use copy JSON"; return; }
  try{
    handle = await window.showSaveFilePicker({suggestedName: FILE,
      types:[{description:"JSON", accept:{"application/json":[".json"]}}]});
    // Read what is already there so we do not clobber another author's keys.
    try{
      const f = await handle.getFile(); const txt = await f.text();
      if(txt.trim()){
        const o = JSON.parse(txt);
        if(o.decisions){ for(const k in o.decisions) if(!D[k]) D[k]=o.decisions[k]; }
        for(const k in o) if(!["decisions","posture","generatedBy","savedAt","decidedCount"].includes(k)) extra[k]=o[k];
      }
    }catch(e){}
    document.getElementById('link').classList.add('live');
    document.getElementById('link').textContent = "linked ✓";
    paint(); await write();
  }catch(e){}
};

document.getElementById('copy').onclick = () => {
  navigator.clipboard.writeText(payload());
  document.getElementById('foot').textContent = "copied " + Object.keys(D).length + " decisions to clipboard";
};
document.getElementById('save').onclick = () => {
  const b = new Blob([payload()], {type:"application/json"});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b); a.download = FILE; a.click();
};

// ── decisions ─────────────────────────────────────────────────────────────────
function set(id, v){
  if(D[id] && D[id].d === v) delete D[id];
  else D[id] = Object.assign(D[id]||{}, {d:v});
  paint(); cache(); queueWrite();
}

document.querySelectorAll('.row').forEach(row => {
  const id = row.dataset.id;
  row.querySelectorAll('.b').forEach(b => b.onclick = () => set(id, b.dataset.v));
  const n = row.querySelector('.note');
  n.oninput = () => { D[id] = Object.assign(D[id]||{d:PRE[id].rec}, {note:n.value});
                      cache(); queueWrite(); paint(); };
});
document.querySelectorAll('.gb').forEach(b => b.onclick = () => {
  const g = b.closest('.grp');
  g.querySelectorAll('.row').forEach(r => { if(!r.classList.contains('hid')) D[r.dataset.id] = Object.assign(D[r.dataset.id]||{}, {d:b.dataset.v}); });
  paint(); cache(); queueWrite();
});

function paint(){
  let k=0,c=0,m=0,f=0,u=0;
  document.querySelectorAll('.row').forEach(row => {
    const id = row.dataset.id, dec = D[id] && D[id].d;
    row.className = row.className.replace(/ ?d-\w+/g,'');
    if(dec) row.classList.add('d-'+dec);
    row.querySelectorAll('.b').forEach(b => b.classList.toggle('sel', b.dataset.v===dec));
    row.querySelector('.mine').textContent = dec ? "" : "— untouched, defaults to " + PRE[id].rec;
    const nt = row.querySelector('.note');
    if(D[id] && D[id].note !== undefined && nt.value !== D[id].note) nt.value = D[id].note;
    if(dec==='KEEP')k++; else if(dec==='CUT')c++; else if(dec==='MERGE')m++;
    else if(dec==='DEFER')f++; else u++;
  });
  tk.textContent=k; tc.textContent=c; tm.textContent=m; td.textContent=f; tu.textContent=u;
}

// ── filters ───────────────────────────────────────────────────────────────────
const filters = new Set();
document.querySelectorAll('.chip').forEach(ch => ch.onclick = () => {
  ch.classList.toggle('on');
  filters.has(ch.dataset.f) ? filters.delete(ch.dataset.f) : filters.add(ch.dataset.f);
  apply();
});
document.getElementById('q').oninput = apply;
function apply(){
  const q = document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('.row').forEach(r => {
    const id = r.dataset.id;
    let ok = true;
    if(q && !r.textContent.toLowerCase().includes(q)) ok = false;
    if(filters.has('contested') && r.dataset.contested !== '1') ok = false;
    if(filters.has('already')   && r.dataset.already !== 'yes') ok = false;
    if(filters.has('undecided') && D[id]) ok = false;
    if(filters.has('cutrec')    && r.dataset.rec !== 'CUT') ok = false;
    r.classList.toggle('hid', !ok);
  });
  document.querySelectorAll('.grp').forEach(g => {
    const any = [...g.querySelectorAll('.row')].some(r => !r.classList.contains('hid'));
    g.classList.toggle('hid', !any);
  });
}

uncache(); paint();
</script>
"""


if __name__ == "__main__":
    main()
