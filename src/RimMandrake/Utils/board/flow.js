/* flow.js — Flow: the causal graph, and the item inspector that hangs off it.
 *
 * THE CHAIN IS  item → run → finding → spawn → item.
 * A failure never reopens earlier work. Instead the failing run stands in the ledger
 * forever, a finding is filed against it, and a NEW item is spawned as its descendant.
 * `caused_by` on an item NAMES its cause — an item id, a finding name, or a run like
 * `C40/run-3@full-578`. It names rather than indexes because line indices do not
 * survive the monthly roll of events.jsonl.
 *
 * 🔴 PROGRESSIVE DISCLOSURE FROM ONE SELECTED ITEM. NEVER THE WHOLE GRAPH.
 * 144 items and 352 events drawn at once are a hairball that answers nothing. This
 * view refuses to draw anything until an item is chosen, then draws that item's
 * ancestry and its immediate descendants and lets the reader WALK. There is no
 * force-directed layout here and there must never be one: every position below is a
 * deterministic function of (column, parents), computed once, with no settling.
 *
 * 🔴 EVERY NODE CARRIES ITS GLYPH AND ITS LABEL. COLOUR IS NEVER THE ONLY ENCODING.
 * palette.js documents that the eight categorical steps pass validation for ADJACENT
 * pairs and FAIL under all-pairs — `#d55181 ↔ #199e70` is ΔE 1.6 for deuteranopia and
 * `#e66767 ↔ #d95926` is ΔE 7.1 with NORMAL vision. This graph is all-pairs, because
 * any two work types can end up next to each other. So:
 *   - `node()` below is the ONLY function that builds a node, and it THROWS if the
 *     glyph, the id or the category label is missing. There is no second path.
 *   - `audit()` re-reads the DOM after every render and counts nodes that actually
 *     carry all three. The count is printed in the footer, so a regression is visible
 *     on screen rather than only in review.
 *
 * ⚠️ STATUS IS A SEPARATE CHANNEL from category and never borrows a categorical hue:
 * blocked is a ring plus ⚠, doing is full opacity, done dims to 45%, dropped and
 * superseded are struck through, idle is a dashed outline.
 *
 * ---------------------------------------------------------------------------
 * WHAT THIS READS FROM /board — measured against the real projection 2026-08-21.
 *
 *   board.catalog[]  {id, title, kind, owner, state, row, target, needs, blocked,
 *                     blocked_reason, blocked_on, this_deployment, created_at,
 *                     closed_sha, superseded_by, caused_by, findings[],
 *                     runs[{name, n, config, result, evidence, sha, ts}]}
 *   board.findings   name -> {from, type, severity, at}
 *   board.game, board.bridge_holder, board.target, board.as_of, board.events
 *   board.blocked[], board.seats{}      — used only as a fallback when catalog is absent
 *
 * ⚠️ WHAT /board DOES NOT CARRY, and what this view therefore cannot show:
 *   1. `items/<ID>.md` PROSE. Not in the projection and not on any endpoint. The
 *      inspector names the file's full path instead of inventing its content.
 *   2. PER-ITEM HISTORY. `Item.history` is a list of ledger indices in the model and
 *      is dropped by render.board(); the board carries only `events` as a COUNT, so
 *      the inspector reconstructs the history it can prove — the runs, the findings,
 *      the close sha, the spawn that created the item — and says so.
 *      ✅ The FULL stream is served, verbatim, at `/ledger/events.jsonl` (text/plain
 *      JSON Lines). This module does not fetch it: `render()` is synchronous and a
 *      view module reaching for the network behind its host's back is not its call.
 *      Hand it in as `board.event_log` — an array of events, or the raw JSONL text —
 *      and the inspector shows every claim, start, note and retarget instead.
 *   3. `caused_by` FOR ANYTHING BUT ITEMS. Runs belong to their item and findings
 *      carry `from`, so those two edges are derivable; nothing else is.
 * ---------------------------------------------------------------------------
 */
import { kindOf, mark } from "./palette.js";

/* Sizes. Fixed, so layout is arithmetic and not a simulation. */
const W = 232, H = 48, GAPX = 78, GAPY = 14, PAD = 22;
const ANCESTORS_DEFAULT = 3;     // how far up the chain before "show more"
const CHILD_CAP = 8;             // siblings drawn before "+K more"

/* A run name. Same grammar as model.RUN_RE, so an unresolvable cause that still
 * LOOKS like a run is drawn as a run rather than as an unknown. */
const RUN_RE = /^([A-Za-z][A-Za-z0-9._-]*)\/run-(\d+)@([\w.-]+)$/;

/* Neutral channel. Runs and findings are NOT work categories and must not borrow a
 * categorical hue — cyan for neutral-active, amber for attention, per §9.3. */
const NEUTRAL = "#2f93a6", ATTN = "#d99a2b", DIM = "#6b6b68";
const RUN_GLYPH = { pass: "✓", fail: "✗", partial: "◐" };

/* Module state. `expanded` holds node keys the reader has opened; it is cleared when
 * the selection changes, because an expansion is about the walk you are on. */
const S = { selected: null, expanded: new Set(), ancestors: ANCESTORS_DEFAULT,
            filter: "", root: null, board: null };

/* ========================================================================= */
/* INDEX — turn the flat catalog into something the chain can be walked over. */
/* ========================================================================= */
function index(board) {
  const ix = { items: new Map(), runs: new Map(), findings: new Map(),
               childrenOf: new Map(), degraded: null };

  let cat = board && board.catalog;
  if (!Array.isArray(cat)) {
    /* Fallback: an older board.json with no `catalog`. `blocked[]` and `seats{}` do
     * carry real item ids, so draw those rather than nothing — but say so. */
    cat = [];
    const seen = new Set();
    const push = (o) => { if (o && o.id && !seen.has(o.id)) { seen.add(o.id); cat.push(o); } };
    (board && board.blocked || []).forEach(push);
    Object.values((board && board.seats) || {}).forEach((s) => {
      (s.doing || []).forEach((id) => push({ id, state: "doing" }));
      if (s.next) push({ id: s.next, state: "ready" });
    });
    ix.degraded = "this board.json predates `catalog`; only " + cat.length +
      " ids could be recovered from `blocked` and `seats`. Re-run " +
      "`python3 src/RimMandrake/rimflow/render.py`.";
  }

  for (const it of cat) {
    if (!it || !it.id) continue;
    ix.items.set(it.id, it);
    for (const r of (it.runs || [])) ix.runs.set(r.name, Object.assign({ item: it.id }, r));
  }
  const fmap = (board && board.findings) || {};
  for (const name of Object.keys(fmap)) ix.findings.set(name, Object.assign({ name }, fmap[name]));
  /* A finding named on an item but absent from the global map is still real — the item
   * says it happened. Record it rather than dropping the link. */
  for (const it of ix.items.values())
    for (const f of (it.findings || []))
      if (!ix.findings.has(f)) ix.findings.set(f, { name: f, from: it.id, type: null, severity: null });

  /* Reverse edge: cause name -> the items it spawned. */
  for (const it of ix.items.values()) {
    if (!it.caused_by) continue;
    if (!ix.childrenOf.has(it.caused_by)) ix.childrenOf.set(it.caused_by, []);
    ix.childrenOf.get(it.caused_by).push(it.id);
  }
  return ix;
}

/* Resolve a NAME to a node reference. Never guesses a type it cannot justify. */
function resolve(ix, name) {
  if (!name) return null;
  if (ix.items.has(name)) return { type: "item", id: name };
  if (ix.runs.has(name)) return { type: "run", id: name };
  if (ix.findings.has(name)) return { type: "finding", id: name };
  if (RUN_RE.test(name)) return { type: "run", id: name, missing: true };
  return { type: "unknown", id: name, missing: true };
}

const keyOf = (ref) => ref.type + ":" + ref.id;

/* The parent of any node, as one step up the chain. */
/* ⚠️ TWO LABELS PER EDGE, and they are not interchangeable. `kind` reads in the
 * direction the edge is DRAWN (parent on the left, child on the right), so the graph
 * spells out item → run → finding → spawned item. `back` reads in the child's voice
 * and is what the inspector's "what caused this" answer uses. Drawing `back` on the
 * arrow labels an edge with the opposite of what it points at. */
function parentOf(ix, ref) {
  if (ref.type === "item") {
    const it = ix.items.get(ref.id);
    return it && it.caused_by
      ? { ref: resolve(ix, it.caused_by), kind: "spawned", back: "caused by" } : null;
  }
  if (ref.type === "run") {
    const r = ix.runs.get(ref.id);
    const owner = (r && r.item) || (RUN_RE.exec(ref.id) || [])[1];
    return owner ? { ref: resolve(ix, owner), kind: "run", back: "run of" } : null;
  }
  if (ref.type === "finding") {
    const f = ix.findings.get(ref.id);
    return f && f.from ? { ref: resolve(ix, f.from), kind: "found", back: "found in" } : null;
  }
  return null;
}

/* Everything one step DOWN from a node: its runs, its findings, its spawned items. */
function childrenOf(ix, ref) {
  const out = [];
  if (ref.type === "item") {
    const it = ix.items.get(ref.id);
    if (it) {
      for (const r of (it.runs || [])) out.push({ ref: { type: "run", id: r.name }, kind: "run" });
      /* Findings filed straight against the item, with no run named. */
      for (const f of (it.findings || [])) {
        const fd = ix.findings.get(f);
        if (!fd || !RUN_RE.test(String(fd.from || ""))) out.push({ ref: { type: "finding", id: f }, kind: "found" });
      }
      if (it.superseded_by && ix.items.has(it.superseded_by))
        out.push({ ref: { type: "item", id: it.superseded_by }, kind: "superseded by" });
    }
  } else if (ref.type === "run") {
    for (const f of ix.findings.values())
      if (f.from === ref.id) out.push({ ref: { type: "finding", id: f.name }, kind: "found" });
  }
  for (const id of (ix.childrenOf.get(ref.id) || []))
    out.push({ ref: { type: "item", id }, kind: "spawned" });
  /* De-duplicate: an item can be reachable twice (spawned AND superseded-by). */
  const seen = new Set(), uniq = [];
  for (const c of out) { const k = keyOf(c.ref); if (!seen.has(k)) { seen.add(k); uniq.push(c); } }
  return uniq;
}

/* ========================================================================= */
/* GRAPH — the disclosed subgraph for ONE selection. Bounded by construction. */
/* ========================================================================= */
function subgraph(ix, selId) {
  const nodes = new Map(), edges = [], overflow = new Map();
  const add = (ref, col) => {
    const k = keyOf(ref);
    const n = nodes.get(k);
    if (n) { n.col = Math.max(n.col, col); return n; }
    const made = { key: k, ref, col, y: 0 };
    nodes.set(k, made);
    return made;
  };
  const focus = { type: "item", id: selId };
  add(focus, 0).focus = true;

  /* --- upward: the ancestry, one chain, depth-limited and extendable ------ */
  let cur = focus, col = 0, hops = 0, more = false;
  const guard = new Set([keyOf(focus)]);
  for (;;) {
    const p = parentOf(ix, cur);
    if (!p || !p.ref) break;
    if (guard.has(keyOf(p.ref))) break;            // a cycle in the record, not a crash
    if (hops >= S.ancestors) { more = true; break; }
    guard.add(keyOf(p.ref));
    add(p.ref, --col);
    edges.push({ from: keyOf(p.ref), to: keyOf(cur), kind: p.kind });
    cur = p.ref; hops++;
  }

  /* --- downward: direct children, plus any the reader has expanded -------- */
  const walk = (ref, atCol, depth) => {
    const kids = childrenOf(ix, ref);
    const shown = kids.slice(0, CHILD_CAP);
    if (kids.length > shown.length) overflow.set(keyOf(ref), kids.length - shown.length);
    for (const c of shown) {
      /* Every step down the chain is exactly one column right, so item → run →
       * finding → spawned item reads left to right as the chain itself. */
      const n = add(c.ref, atCol + 1);
      edges.push({ from: keyOf(ref), to: n.key, kind: c.kind });
      if (S.expanded.has(n.key) || (depth === 0 && c.ref.type !== "item"))
        walk(c.ref, n.col, depth + 1);            // runs auto-open to their findings
    }
  };
  walk(focus, 0, 0);
  return { nodes, edges, overflow, ancestorsTruncated: more };
}

/* Deterministic layered layout: column = x, and y is the mean of a node's parents,
 * pushed down only far enough to stop overlap. No iteration to convergence, no
 * animation, same input -> same pixels. */
function layout(g) {
  const cols = new Map();
  for (const n of g.nodes.values()) {
    if (!cols.has(n.col)) cols.set(n.col, []);
    cols.get(n.col).push(n);
  }
  const parents = new Map();
  for (const e of g.edges) {
    if (!parents.has(e.to)) parents.set(e.to, []);
    parents.get(e.to).push(e.from);
  }
  const order = [...cols.keys()].sort((a, b) => a - b);
  for (const c of order) {
    const list = cols.get(c);
    for (const n of list) {
      const ps = (parents.get(n.key) || []).map((k) => g.nodes.get(k)).filter(Boolean);
      n.y = ps.length ? ps.reduce((s, p) => s + p.y, 0) / ps.length : 0;
    }
    list.sort((a, b) => a.y - b.y || a.key.localeCompare(b.key));
    let floor = -Infinity;
    for (const n of list) { n.y = Math.max(n.y, floor); floor = n.y + H + GAPY; }
  }
  const minCol = order[0] || 0;
  let minY = Infinity, maxY = -Infinity;
  for (const n of g.nodes.values()) {
    n.x = PAD + (n.col - minCol) * (W + GAPX);
    minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y + H);
  }
  for (const n of g.nodes.values()) n.y += PAD - minY;
  const maxCol = order[order.length - 1] || 0;
  return { w: PAD * 2 + (maxCol - minCol + 1) * W + (maxCol - minCol) * GAPX,
           h: PAD * 2 + (maxY - minY) };
}

/* ========================================================================= */
/* NODES — the one and only place a node is built.                            */
/* ========================================================================= */
function descriptor(ix, ref) {
  if (ref.type === "item") {
    const it = ix.items.get(ref.id);
    if (!it) return { glyph: "?", label: "not in the projection", hex: DIM,
                      opacity: 0.6, dashed: true, sub: "", title: ref.id };
    const m = mark(it);
    return { glyph: m.glyph, label: m.label, hex: m.hex, opacity: m.opacity,
             ring: !!m.ring, warn: m.warn, strike: !!m.strike,
             dashed: it.state === "ready" || it.state === "proposed",
             sub: it.owner + " · " + it.state + (it.blocked ? " · blocked" : ""),
             title: it.title || it.id };
  }
  if (ref.type === "run") {
    const r = ix.runs.get(ref.id) || {};
    const bad = r.result === "fail" || r.result === "partial";
    /* ⚠️ No ring and no ⚠ here. Those two marks mean BLOCKED and nothing else, so that
     * a reader scanning for "what is stuck" never has to re-read a node to find out.
     * A failing run says `fail` in words and carries ✗ as its glyph — that is enough. */
    return { glyph: RUN_GLYPH[r.result] || "▷", label: "run · " + (r.config || "config unrecorded"),
             hex: bad ? ATTN : NEUTRAL, opacity: 1,
             sub: (r.result || "result not in the projection") + (r.ts ? " · " + r.ts.slice(0, 10) : ""),
             title: r.evidence || ref.id };
  }
  if (ref.type === "finding") {
    const f = ix.findings.get(ref.id) || {};
    return { glyph: "⚑", label: "finding" + (f.type ? " · " + f.type : ""), hex: ATTN,
             opacity: 1,
             sub: (f.severity ? "severity " + f.severity : "severity unrecorded") +
                  (f.at ? " · " + f.at.slice(0, 10) : ""),
             title: "filed from " + (f.from || "an unrecorded source") };
  }
  return { glyph: "?", label: "unresolved cause", hex: DIM, opacity: 0.6, dashed: true,
           sub: "named by caused_by, nothing in the ledger answers to it", title: ref.id };
}

/* 🔴 THE GUARANTEE. Every node goes through here, and here refuses to build one that
 * would rely on colour alone. A throw is correct: a silently unlabelled node in an
 * all-pairs view is a wrong answer rendered confidently. */
function node(ix, n, focusKey) {
  const d = descriptor(ix, n.ref);
  if (!d.glyph || !String(d.glyph).trim())
    throw new Error("flow.js: node " + n.key + " has no glyph. Colour is not a legal sole encoding here.");
  if (!d.label || !String(d.label).trim())
    throw new Error("flow.js: node " + n.key + " has no category label. See palette.js.");
  if (!n.ref.id) throw new Error("flow.js: node with no id");

  const el = document.createElement("div");
  el.className = "fnode fnode-" + n.ref.type + (n.key === focusKey ? " is-focus" : "");
  el.dataset.nodeKey = n.key;
  el.dataset.nodeType = n.ref.type;
  el.tabIndex = 0;
  el.style.left = n.x + "px"; el.style.top = n.y + "px";
  el.style.width = W + "px"; el.style.height = H + "px";
  el.style.setProperty("--hue", d.hex);
  el.style.opacity = String(d.opacity == null ? 1 : d.opacity);
  if (d.ring) el.classList.add("is-ring");
  if (d.dashed) el.classList.add("is-idle");
  if (d.strike) el.classList.add("is-struck");
  el.title = n.ref.id + " — " + (d.title || "");

  const g = document.createElement("span");
  g.className = "fnode-glyph"; g.textContent = d.glyph; el.appendChild(g);

  const body = document.createElement("span");
  body.className = "fnode-body";
  const id = document.createElement("span");
  id.className = "fnode-id"; id.textContent = n.ref.id; body.appendChild(id);
  const meta = document.createElement("span");
  meta.className = "fnode-meta";
  const kind = document.createElement("span");
  kind.className = "fnode-kind"; kind.textContent = d.label;   /* ← never colour alone */
  meta.appendChild(kind);
  if (d.sub) {
    const sub = document.createElement("span");
    sub.className = "fnode-sub"; sub.textContent = " · " + d.sub; meta.appendChild(sub);
  }
  body.appendChild(meta);
  el.appendChild(body);

  if (d.warn) {
    const w = document.createElement("span");
    w.className = "fnode-warn"; w.textContent = d.warn; el.appendChild(w);
  }
  return el;
}

/* Re-read the DOM and prove the guarantee held, every render. */
function audit(canvas) {
  const all = [...canvas.querySelectorAll("[data-node-key]")];
  const bad = all.filter((el) => {
    const t = (s) => (el.querySelector(s) || {}).textContent || "";
    return !t(".fnode-glyph").trim() || !t(".fnode-id").trim() || !t(".fnode-kind").trim();
  });
  bad.forEach((el) => el.classList.add("is-unlabelled"));
  return { total: all.length, bad: bad.length };
}

/* ========================================================================= */
/* THE FOUR WHY ANSWERS                                                       */
/*                                                                            */
/* 🔑 The wording below deliberately MIRRORS priority.py's `why_not()` sentence  */
/* for sentence. Two vocabularies for one question is how the old queues made   */
/* "why is this not in my list" unanswerable; the CLI and the board must agree. */
/* ========================================================================= */
const NEEDS_MET = {
  "offline": () => ({ ok: true }),
  "deploy": (b) => ({ ok: b.game === "DEPLOYING" }),
  "game-up": (b) => ({ ok: b.game === "UP" }),
  "bridge": (b) => ({ ok: b.game === "UP" && b.bridge_holder === "CHECK" }),
  "harvest": () => ({ ok: null, note: "depends on whether a log is still unmined, which the board does not carry" }),
  "owner": () => ({ ok: null, note: "depends on whether the owner is at the keyboard, which the board does not carry" }),
};

function whyBlocked(it) {
  if (!it.blocked) return ["Not blocked. Nothing is wrong with it."];
  return ["BLOCKED: " + (it.blocked_reason || "unexplained") +
          (it.blocked_on ? " (on " + it.blocked_on + ")" : "")];
}

function whyV2(it, board) {
  const target = board.target || "v1";
  if (!it.target) return ["No target recorded, so it is not filtered out by version."];
  if (it.target === target) return ["Targeted at " + it.target + ", which IS the active version."];
  return ["Targeted at " + it.target + ", and the active version is " + target +
          ". That is a planning decision, not a defect."];
}

function whyNotDone(it, board) {
  const out = [];
  if (it.state === "done") return ["It IS done — closed at " + (it.closed_sha || "?") +
    ". It will never be offered again; that is the point of an append-only record."];
  if (it.state === "dropped") return ["Dropped. A dropped item cannot be revived — file a new one, and say in its notes why the drop was wrong."];
  if (it.state === "superseded") return ["Superseded by " + (it.superseded_by || "?") + ". Work its successor."];
  if (it.state === "proposed")
    out.push("state is `proposed`: items/" + it.id + ".md is missing one of ## spec, ## verify or ## criteria, so it cannot enter `ready`. " +
             "(Which one is missing is read off the file, which the board does not carry.)");
  else if (it.state !== "ready") out.push("state is `" + it.state + "`.");
  if (it.blocked) out.push("BLOCKED: " + (it.blocked_reason || "unexplained") +
    (it.blocked_on ? " (on " + it.blocked_on + ")" : ""));
  const target = board.target || "v1";
  if (it.target && it.target !== target)
    out.push("targeted at " + it.target + ", and the active version is " + target +
             ". That is a planning decision, not a defect.");
  const fn = NEEDS_MET[it.needs];
  if (!fn) out.push("needs `" + it.needs + "`, which is not a `needs` the priority engine knows. An unknown `needs` is never offered.");
  else {
    const r = fn(board);
    if (r.ok === false)
      out.push("needs `" + it.needs + "`, and the game is " + board.game +
               ". ⚠️ This is NOT blocked — nothing is wrong, the window is simply closed and will reopen.");
    else if (r.ok === null)
      out.push("needs `" + it.needs + "`, and whether that is satisfiable " + r.note + ". Ask `rimflow why " + it.id + "`.");
  }
  if (!out.length) out.push("Nothing is holding it: it is ready, unblocked, on target, and its `needs` is met. It should be offered — check `rimflow next --seat " + it.owner + "`.");
  return out;
}

function whatCaused(ix, it) {
  if (!it.caused_by) return ["Filed directly. Nothing in the ledger names a cause for it."];
  const chain = [];
  let cur = { type: "item", id: it.id }, hops = 0;
  for (;;) {
    const p = parentOf(ix, cur);
    if (!p || !p.ref || hops++ > 12) break;
    const d = descriptor(ix, p.ref);
    chain.push(d.glyph + " " + p.back + " " + p.ref.id + (p.ref.missing ? "  (named, but not in the projection)" : ""));
    cur = p.ref;
  }
  return chain.length ? chain : ["`caused_by` names " + it.caused_by + ", and nothing in the projection answers to that name."];
}

/* ========================================================================= */
/* DOM helpers                                                                */
/* ========================================================================= */
function h(tag, cls, text) {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (text != null) el.textContent = text;
  return el;
}
const NATIVE_ITEMS = "D:\\Luke\\dev\\Rimworld\\infrastructure\\state\\items\\";

function select(id) {
  if (S.selected === id) return;
  S.selected = id;
  S.expanded.clear();
  S.ancestors = ANCESTORS_DEFAULT;
  if (S.root) {
    S.root.dispatchEvent(new CustomEvent("flow:select", { detail: { id }, bubbles: true }));
    draw();
  }
}

/* ========================================================================= */
/* CHOOSER — what you see before anything is selected. Not the whole graph.   */
/* ========================================================================= */
function chooser(ix, board) {
  const wrap = h("div", "fchoose");
  wrap.appendChild(h("div", "fchoose-h", "Pick one item. The graph is drawn outward from it."));

  const linked = [...ix.items.values()].filter(
    (i) => i.caused_by || (i.runs || []).length || (i.findings || []).length || i.superseded_by);
  /* ⚠️ The test is for CAUSAL edges, not for links of any sort. A `supersede` is a real
   * edge and is listed below, but it is a planning decision, not a run that failed —
   * so on a ledger imported from the old queues (one supersede, zero runs, zero
   * findings, zero spawns) the reader still needs to be told why the graph is bare. */
  const causal = ix.runs.size || ix.findings.size ||
    [...ix.items.values()].some((i) => i.caused_by);

  if (!causal) {
    const e = h("div", "fempty");
    e.appendChild(h("div", "fempty-h", "⚑  NO CAUSAL CHAINS HAVE BEEN RECORDED YET"));
    e.appendChild(h("p", null,
      "All " + ix.items.size + " items were imported from the six hand-written queues, which " +
      "recorded no runs, no findings and no spawns. Nothing is broken and nothing is missing " +
      "from this view — the ledger simply has no causal edges in it yet."));
    e.appendChild(h("p", "fempty-sub", "A chain appears the first time CHECK records one:"));
    const ol = h("ol", "fempty-steps");
    [["rimflow verify <ID> --result fail --config full-578", "the failing run, which stands forever — the item is NOT reopened"],
     ["rimflow finding --from <ID>/run-1@full-578 --type defect --severity high --name <NAME_1>", "the finding, filed against that run"],
     ["rimflow spawn --from <NAME_1> --for BUILD --name <NEW_ITEM_1>", "the descendant item, whose caused_by names the finding"]]
      .forEach(([cmd, why]) => {
        const li = h("li");
        li.appendChild(h("code", null, cmd));
        li.appendChild(h("span", "fempty-why", why));
        ol.appendChild(li);
      });
    e.appendChild(ol);
    e.appendChild(h("p", "fempty-sub",
      "Until then this view still works as the item inspector: pick any item below."));
    wrap.appendChild(e);
  }
  if (linked.length)
    wrap.appendChild(pickList(causal ? "Items that already sit on a chain"
                                     : "Linked, but not by a causal edge", linked.map((i) => i.id), ix));

  /* Useful entry points that exist right now. */
  const doing = [], blocked = [], next = [];
  for (const it of ix.items.values()) {
    if (it.state === "doing") doing.push(it.id);
    if (it.blocked) blocked.push(it.id);
  }
  Object.values(board.seats || {}).forEach((s) => { if (s.next) next.push(s.next); });
  if (doing.length) wrap.appendChild(pickList("In progress", doing.sort(), ix));
  if (blocked.length) wrap.appendChild(pickList("Blocked", blocked.sort(), ix));
  if (next.length) wrap.appendChild(pickList("Next up, per seat", next, ix));

  const box = h("div", "fsearch");
  const inp = document.createElement("input");
  inp.type = "search"; inp.placeholder = "find any of " + ix.items.size + " items by id or title";
  inp.value = S.filter;
  const hits = h("div", "fsearch-hits");
  const run = () => {
    const q = inp.value.trim().toLowerCase();
    S.filter = inp.value;
    hits.textContent = "";
    if (q.length < 2) { hits.appendChild(h("div", "fmut", "type two characters")); return; }
    const m = [...ix.items.values()].filter(
      (i) => i.id.toLowerCase().includes(q) || String(i.title || "").toLowerCase().includes(q)).slice(0, 24);
    if (!m.length) { hits.appendChild(h("div", "fmut", "no item matches")); return; }
    hits.appendChild(pickList(null, m.map((i) => i.id), ix));
  };
  inp.addEventListener("input", run);
  box.appendChild(inp); box.appendChild(hits);
  wrap.appendChild(box);
  run();
  return wrap;
}

function pickList(title, ids, ix) {
  const box = h("div", "fpick");
  if (title) box.appendChild(h("div", "fpick-h", title));
  const seen = new Set();
  for (const id of ids) {
    if (seen.has(id)) continue; seen.add(id);
    const it = ix.items.get(id) || { id, kind: null };
    const m = mark(it);
    const b = h("button", "fpick-i");
    b.style.setProperty("--hue", m.hex);
    b.appendChild(h("span", "fpick-g", m.glyph));            /* glyph */
    b.appendChild(h("span", "fpick-id", id));                /* label */
    b.appendChild(h("span", "fpick-k", m.label));            /* category, in words */
    if (it.title && it.title !== id) b.appendChild(h("span", "fpick-t", it.title));
    b.addEventListener("click", () => select(id));
    box.appendChild(b);
  }
  return box;
}

/* The optional raw stream. A torn line is SHOWN, never skipped: model.read() refuses
 * to skip one for exactly this reason — a ledger that quietly drops a line lies, and
 * nobody learns it happened. */
function eventLog(board) {
  const raw = board && board.event_log;
  if (!raw) return null;
  if (Array.isArray(raw)) return { events: raw, torn: 0 };
  if (typeof raw !== "string") return null;
  const events = [];
  let torn = 0;
  for (const line of raw.split("\n")) {
    const t = line.trim();
    if (!t) continue;
    try { events.push(JSON.parse(t)); } catch (e) { torn++; }
  }
  return { events, torn };
}

/* ========================================================================= */
/* INSPECTOR                                                                  */
/* ========================================================================= */
function inspector(ix, board, id) {
  const it = ix.items.get(id);
  const box = h("aside", "finsp");
  if (!it) {
    box.appendChild(h("div", "finsp-h", id));
    box.appendChild(h("p", "fwarn", "This id is named by the graph but is not in the projection."));
    return box;
  }
  const m = mark(it);
  const head = h("div", "finsp-head");
  head.style.setProperty("--hue", m.hex);
  head.appendChild(h("span", "finsp-glyph", m.glyph));
  const ht = h("div", "finsp-ht");
  ht.appendChild(h("div", "finsp-id", it.id));
  ht.appendChild(h("div", "finsp-kind", m.label));
  head.appendChild(ht);
  box.appendChild(head);
  box.appendChild(h("div", "finsp-title", it.title || it.id));

  /* --- scalars --------------------------------------------------------- */
  const dl = h("dl", "finsp-scalars");
  const row = (k, v) => { dl.appendChild(h("dt", null, k)); dl.appendChild(h("dd", null, v == null || v === "" ? "—" : String(v))); };
  row("owner", it.owner); row("state", it.state);
  row("blocked", it.blocked ? "yes ⚠" : "no");
  row("needs", it.needs); row("target", it.target); row("row", it.row);
  row("this deployment", it.this_deployment ? "yes" : "no");
  row("created", it.created_at); row("closed sha", it.closed_sha);
  row("superseded by", it.superseded_by); row("caused by", it.caused_by);
  box.appendChild(dl);

  /* --- the four why answers -------------------------------------------- */
  const why = h("section", "finsp-why");
  why.appendChild(h("h4", null, "why"));
  const ask = (q, lines) => {
    const d = h("div", "fwhy");
    d.appendChild(h("div", "fwhy-q", q));
    const ul = h("ul");
    lines.forEach((l) => ul.appendChild(h("li", null, l)));
    d.appendChild(ul);
    why.appendChild(d);
  };
  ask("why blocked?", whyBlocked(it));
  ask("why v2?", whyV2(it, board));
  ask("why not done?", whyNotDone(it, board));
  ask("what caused this?", whatCaused(ix, it));
  why.appendChild(h("div", "fmut", "These mirror `rimflow why " + it.id + "` — same filters, same order, same words."));
  box.appendChild(why);

  /* --- history, and an honest account of its limits --------------------- */
  const hist = h("section", "finsp-hist");
  hist.appendChild(h("h4", null, "history"));
  const log = eventLog(board);
  if (log) {
    /* `spawn` names its product in `name`, not `id` — it is about its cause and its
     * product, never about a host item — so an item's own birth is matched on `name`. */
    const mine = log.events.filter((e) => e.id === it.id || e.name === it.id);
    const ul2 = h("ul", "fhist");
    for (const e of mine) {
      const li = h("li");
      li.appendChild(h("span", "fhist-ts", String(e.ts || "—").replace("T", " ").replace("Z", "")));
      const bits = [e.seat + " " + e.event];
      for (const k of ["result", "config", "for", "to", "by", "from", "name", "sha", "reason", "text", "evidence", "severity", "type", "state", "title"])
        if (e[k] != null && e[k] !== "") bits.push(k + "=" + e[k]);
      li.appendChild(h("span", "fhist-t", bits.join("  ")));
      ul2.appendChild(li);
    }
    if (!mine.length) ul2.appendChild(h("li", null, "no event in the stream names this item"));
    hist.appendChild(ul2);
    hist.appendChild(h("div", "fmut",
      mine.length + " of " + log.events.length + " ledger events name " + it.id +
      (log.torn ? " · ⚠ " + log.torn + " line(s) in the stream would not parse — the ledger may be torn; look at the tail before writing again" : "")));
    box.appendChild(hist);
    return proseSection(box, it);
  }
  const ev = [];
  if (it.created_at) ev.push([it.created_at, it.caused_by ? "spawned, caused by " + it.caused_by : "filed for " + it.owner]);
  for (const r of (it.runs || [])) ev.push([r.ts, (RUN_GLYPH[r.result] || "▷") + " " + r.name + " — " + r.result + (r.evidence ? " · " + r.evidence : "")]);
  for (const f of (it.findings || [])) {
    const fd = ix.findings.get(f) || {};
    ev.push([fd.at, "⚑ finding " + f + (fd.severity ? " · severity " + fd.severity : "")]);
  }
  if (it.blocked) ev.push([null, "⚠ blocked — " + (it.blocked_reason || "unexplained")]);
  if (it.closed_sha) ev.push([null, "✓ closed at " + it.closed_sha]);
  if (it.superseded_by) ev.push([null, "→ superseded by " + it.superseded_by]);
  ev.sort((a, b) => String(a[0] || "").localeCompare(String(b[0] || "")));
  const ul = h("ul", "fhist");
  ev.forEach(([ts, txt]) => {
    const li = h("li");
    li.appendChild(h("span", "fhist-ts", ts ? ts.replace("T", " ").replace("Z", "") : "—"));
    li.appendChild(h("span", "fhist-t", txt));
    ul.appendChild(li);
  });
  hist.appendChild(ul);
  hist.appendChild(h("div", "fmut",
    "Reconstructed from the projection. ⚠️ /board carries `events` only as a COUNT (" +
    (board.events == null ? "?" : board.events) + "), so claims, starts, notes and " +
    "retargets are not here. The full stream is served at /ledger/events.jsonl — pass " +
    "it in as `board.event_log` and this list becomes the ledger itself. Meanwhile " +
    "`rimflow show " + it.id + "` has them."));
  box.appendChild(hist);

  return proseSection(box, it);
}

/* --- prose ------------------------------------------------------------------ */
function proseSection(box, it) {
  const prose = h("section", "finsp-prose");
  prose.appendChild(h("h4", null, "prose"));
  const body = it.prose || it.md || it.body;
  if (body) prose.appendChild(h("pre", null, body));
  else {
    prose.appendChild(h("p", "fmut",
      "The spec, verify, criteria and notes live in the item's own file. /board does not " +
      "carry them and no endpoint serves them, so they are not invented here."));
    prose.appendChild(h("code", "fpath", NATIVE_ITEMS + it.id + ".md"));
  }
  box.appendChild(prose);
  return box;
}

/* ========================================================================= */
/* RENDER                                                                     */
/* ========================================================================= */
function drawGraph(ix, board, host) {
  const g = subgraph(ix, S.selected);
  const size = layout(g);
  const canvas = h("div", "fcanvas");
  canvas.style.width = size.w + "px";
  canvas.style.height = size.h + "px";

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "fedges");
  svg.setAttribute("width", size.w); svg.setAttribute("height", size.h);
  svg.setAttribute("viewBox", "0 0 " + size.w + " " + size.h);
  for (const e of g.edges) {
    const a = g.nodes.get(e.from), b = g.nodes.get(e.to);
    if (!a || !b) continue;
    const x1 = a.x + W, y1 = a.y + H / 2, x2 = b.x, y2 = b.y + H / 2;
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", "M" + x1 + "," + y1 + " C" + (x1 + GAPX * 0.55) + "," + y1 +
                        " " + (x2 - GAPX * 0.55) + "," + y2 + " " + x2 + "," + y2);
    p.setAttribute("class", "fedge" + (e.kind === "spawned" ? " is-spawn" : ""));
    svg.appendChild(p);
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", (x1 + x2) / 2); t.setAttribute("y", (y1 + y2) / 2 - 5);
    t.setAttribute("class", "fedge-l"); t.setAttribute("text-anchor", "middle");
    t.textContent = e.kind;
    svg.appendChild(t);
  }
  canvas.appendChild(svg);

  const focusKey = keyOf({ type: "item", id: S.selected });
  for (const n of [...g.nodes.values()].sort((a, b) => a.col - b.col || a.y - b.y)) {
    let el;
    try { el = node(ix, n, focusKey); }
    catch (err) {                       /* a refusal is louder than a wrong node */
      el = h("div", "fnode is-unlabelled");
      el.dataset.nodeKey = n.key;
      el.style.left = n.x + "px"; el.style.top = n.y + "px";
      el.style.width = W + "px"; el.style.height = H + "px";
      el.textContent = String(err.message);
      canvas.appendChild(el);
      continue;
    }
    if (n.ref.type === "item" && n.key !== focusKey)
      el.addEventListener("click", () => select(n.ref.id));
    else if (n.ref.type !== "item") {
      el.addEventListener("click", () => {
        if (S.expanded.has(n.key)) S.expanded.delete(n.key); else S.expanded.add(n.key);
        draw();
      });
    }
    el.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); el.click(); } });
    const extra = g.overflow.get(n.key);
    if (extra) {
      const more = h("span", "fnode-more", "+" + extra);
      more.title = extra + " more descendants not drawn. Select this node to walk into them.";
      el.appendChild(more);
    }
    canvas.appendChild(el);
  }

  /* ⚠️ Instant, never smooth. `scrollLeft = n` jumps; `scrollIntoView({behavior})`
   * animates, and this page is left open all day. The focus is parked a third of the
   * way in so its ancestry stays visible to the left of it. */
  const f = g.nodes.get(focusKey);
  if (f) host.dataset.focusX = String(f.x), host.dataset.focusY = String(f.y);

  if (g.ancestorsTruncated) {
    const b = h("button", "fmore fmore-up", "▲ show more ancestors");
    b.addEventListener("click", () => { S.ancestors += 3; draw(); });
    host.appendChild(b);
  }
  host.appendChild(canvas);
  return audit(canvas);
}

function draw() {
  const root = S.root, board = S.board;
  if (!root) return;
  root.textContent = "";
  root.classList.add("flow");

  if (!board || board.unavailable) {
    const u = h("div", "funavail");
    u.appendChild(h("div", "funavail-h", "UNAVAILABLE"));
    u.appendChild(h("p", null, (board && board.why) ||
      "board.json could not be built, so the ledger projection is not readable. " +
      "`derived/` is gitignored and can be absent on a fresh checkout — run " +
      "`python3 src/RimMandrake/rimflow/render.py`."));
    root.appendChild(u);
    return;
  }

  const ix = index(board);

  const bar = h("header", "fbar");
  bar.appendChild(h("span", "fbar-t", "FLOW · item → run → finding → spawn → item"));
  const facts = h("span", "fbar-f");
  facts.textContent = ix.items.size + " items · " + ix.findings.size + " findings · " +
    ix.runs.size + " runs · game " + (board.game || "?") +
    (board.as_of ? " · as of " + board.as_of.replace("T", " ").replace("Z", "") : "");
  bar.appendChild(facts);
  if (S.selected) {
    const back = h("button", "fbar-b", "← all items");
    back.addEventListener("click", () => { S.selected = null; S.expanded.clear(); draw(); });
    bar.appendChild(back);
  }
  root.appendChild(bar);

  if (ix.degraded) root.appendChild(h("div", "fwarn", "⚠ " + ix.degraded));

  const main = h("div", "fmain");
  const left = h("div", "fgraph");
  let scrollTo = null;
  let a = { total: 0, bad: 0 };
  if (!S.selected || !ix.items.has(S.selected)) {
    if (S.selected) left.appendChild(h("div", "fwarn", "⚠ " + S.selected + " is not in the projection."));
    left.appendChild(chooser(ix, board));
  } else {
    a = drawGraph(ix, board, left);
  }
  main.appendChild(left);
  scrollTo = left;
  if (S.selected && ix.items.has(S.selected)) main.appendChild(inspector(ix, board, S.selected));
  root.appendChild(main);

  const foot = h("footer", "ffoot");
  foot.textContent = a.total
    ? a.total + " nodes drawn · " + (a.total - a.bad) + " carry glyph + id + category label" +
      (a.bad ? " · ⚠ " + a.bad + " DO NOT — colour alone is not legal here (palette.js)" : " · colour is never the only encoding")
    : "nothing drawn yet — select an item";
  if (a.bad) foot.classList.add("is-bad");
  root.appendChild(foot);

  if (scrollTo && scrollTo.dataset.focusX != null) {
    const fx = parseFloat(scrollTo.dataset.focusX), fy = parseFloat(scrollTo.dataset.focusY);
    scrollTo.scrollLeft = Math.max(0, fx - scrollTo.clientWidth / 3);
    scrollTo.scrollTop = Math.max(0, fy - scrollTo.clientHeight / 3);
  }
}

/* The entry point. `selectedId` wins over whatever the reader last clicked, so a host
 * can drive the selection from a URL or from another view. */
export function render(root, board, selectedId) {
  S.root = root;
  S.board = board;
  if (selectedId !== undefined && selectedId !== null && selectedId !== S.selected) {
    S.selected = selectedId;
    S.expanded.clear();
    S.ancestors = ANCESTORS_DEFAULT;
  }
  draw();
}

export default { render };
