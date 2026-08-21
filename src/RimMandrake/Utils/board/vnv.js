/* vnv.js — the V&V matrix: items × configurations, each cell the LATEST run.
 *
 * 🔴 WHAT THIS VIEW EXISTS TO STOP.
 * The old queues reopened an item when its check failed, which erased that it had ever
 * failed and made "how many times did we try this" unanswerable. `rimflow`'s Run is
 * immutable instead — a fail stands forever — so this view must never undo that by
 * drawing over it. ⇒ **A cell whose LATEST run passed still shows every earlier fail**:
 * one tick per historical run in order, a tally that names the fail count in words, and
 * an amber attention bar on any cell with a fail in its past. A green cell that hides
 * three prior failures is the exact lie the ledger was rebuilt to stop telling.
 *
 * ⚠️ AND: an empty cell is NOT a pass. UNMEASURED is drawn as a dashed, hatched panel
 * reading `NEVER RUN`; PASSED is a solid panel reading `PASS`. They share no border
 * style, no fill, no glyph and no word, and the legend states the difference outright.
 *
 * ⚠️ Run numbers restart per config, and that is correct, not a collision:
 * `C40/run-1@minimal-13` and `C40/run-1@full-578` are both run-1 and both real. A pass
 * on 13 mods and a pass on 578 mods are different questions, not a retry of one — so
 * every column keeps its own history and no column ever inherits another's verdict.
 *
 * ⛔ COLUMNS ARE DERIVED FROM THE RUNS PRESENT, never from a hard-coded list. If
 * `minimal-13 · full-578 · bridge · offline` were written in here, the first seat to
 * verify against a fifth config would get no column and its results would silently
 * vanish off the board.
 *
 * ⛔ Colour is never the only encoding (see palette.js — two of our own categories are
 * ΔE 7.1 apart to a reader with ordinary sight). Every mark here carries a glyph AND a
 * word. Status uses only the two hues the plan allots — restrained cyan for the quiet
 * good state, amber for attention — and borrows no categorical hue, so `fail` can never
 * compete with `art` for the same pixel.
 *
 * DATA: `/board` (rimflow-board/1). Uses `catalog[]` — per item `runs[]` of
 * `{name, n, config, result, evidence, sha, ts}` — plus `findings{}` keyed by name.
 * `items` is a count, not a list; this view does not read it.
 */
import { kindOf } from "./palette.js";

const CSS_ID = "vnv-css";

/* Results, as they are validated in rimflow: pass | fail | partial. Anything else is
 * shown as UNKNOWN by name — never quietly folded into a pass. */
const RESULT = {
  pass:    { glyph: "✔", label: "PASS",    cls: "vnv-pass" },
  fail:    { glyph: "✘", label: "FAIL",    cls: "vnv-fail" },
  partial: { glyph: "◐", label: "PARTIAL", cls: "vnv-partial" },
};
const UNMEASURED = { glyph: "·", label: "NEVER RUN", cls: "vnv-unmeasured" };

function resultOf(r) {
  const k = String(r == null ? "" : r).toLowerCase();
  return RESULT[k] || { glyph: "?", label: "UNKNOWN: " + (k || "(blank)"),
                        cls: "vnv-unknown" };
}

/* ---------------------------------------------------------------- projection */

/* project(board) -> the whole view as data, with no DOM anywhere near it, so the
 * matrix can be asserted without a browser and the drawing code has no logic in it. */
export function project(board) {
  const b = board || {};
  if (b.unavailable) {
    return { ok: false, reason: "unavailable",
             why: b.why || "board.json could not be built" };
  }
  if (!Array.isArray(b.catalog)) {
    /* An older board.json carried only counts. Say so; do NOT draw an empty grid,
     * which would read as 144 items that all passed. */
    return { ok: false, reason: "no-catalog",
             why: "this /board payload has no `catalog[]` (schema " +
                  (b.schema || "unknown") + "), so per-item runs are not available" };
  }

  const findings = b.findings && typeof b.findings === "object" ? b.findings : {};
  const configSeen = new Set();
  const items = b.catalog.map(function (raw) {
    const runs = (Array.isArray(raw.runs) ? raw.runs : []).map(function (r, i) {
      const res = resultOf(r.result);
      return {
        name: r.name || (raw.id + "/run-" + (r.n == null ? i + 1 : r.n) +
                         "@" + (r.config || "?")),
        n: r.n == null ? i + 1 : r.n,
        config: r.config == null ? "" : String(r.config),
        result: res, raw: r.result,
        evidence: r.evidence || null, sha: r.sha || null, ts: r.ts || null,
      };
    });
    runs.forEach(function (r) { if (r.config) configSeen.add(r.config); });

    const cells = {};
    runs.forEach(function (r) {
      const c = cells[r.config] || (cells[r.config] =
        { config: r.config, runs: [], pass: 0, fail: 0, partial: 0, other: 0 });
      c.runs.push(r);
    });
    Object.keys(cells).forEach(function (k) {
      const c = cells[k];
      /* Run numbers are per config and monotonic, so `n` is the honest order even if
       * two runs share a timestamp. */
      c.runs.sort(function (x, y) { return x.n - y.n; });
      c.runs.forEach(function (r) {
        const key = String(r.raw).toLowerCase();
        if (key === "pass" || key === "fail" || key === "partial") c[key] += 1;
        else c.other += 1;
      });
      c.latest = c.runs[c.runs.length - 1];
      c.total = c.runs.length;
      /* The whole point: a later pass does not erase an earlier fail. */
      c.priorFail = c.fail - (c.latest.raw === "fail" ? 1 : 0);
      c.hiddenFail = c.latest.raw !== "fail" && c.fail > 0;
    });

    return {
      id: raw.id, title: raw.title || "", kind: raw.kind || "",
      owner: raw.owner || "", state: raw.state || "", needs: raw.needs || "",
      target: raw.target || "", blocked: !!raw.blocked,
      blockedReason: raw.blocked_reason || "",
      findings: (Array.isArray(raw.findings) ? raw.findings : []),
      runs: runs, cells: cells,
      total: runs.length,
      fails: runs.filter(function (r) { return r.raw === "fail"; }).length,
      everFailed: runs.some(function (r) { return r.raw === "fail"; }),
    };
  });

  /* ⛔ Derived, never declared. Alphabetical so a column does not move under the
   * reader's cursor between polls; a new config simply slots in where it belongs. */
  const configs = Array.from(configSeen).sort();

  const verified = items.filter(function (i) { return i.total > 0; });
  return {
    ok: true,
    asOf: b.as_of || null,
    schema: b.schema || null,
    items: items,
    configs: configs,
    findings: findings,
    ledgerErrors: Array.isArray(b.errors) ? b.errors.length : 0,
    stats: {
      items: items.length,
      verified: verified.length,
      unverified: items.length - verified.length,
      runs: items.reduce(function (a, i) { return a + i.total; }, 0),
      fails: items.reduce(function (a, i) { return a + i.fails; }, 0),
      everFailed: items.filter(function (i) { return i.everFailed; }).length,
      configs: configs.length,
    },
  };
}

/* --------------------------------------------------------------------- DOM */

function el(tag, attrs, kids) {
  const n = document.createElement(tag);
  if (attrs) Object.keys(attrs).forEach(function (k) {
    if (k === "class") n.className = attrs[k];
    else if (k === "text") n.textContent = attrs[k];
    else if (attrs[k] != null) n.setAttribute(k, attrs[k]);
  });
  (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
  return n;
}
const txt = function (t) { return document.createTextNode(t); };

function stylesheet() {
  if (document.getElementById(CSS_ID)) return;
  const href = new URL("./vnv.css", import.meta.url).href;
  document.head.appendChild(el("link", { id: CSS_ID, rel: "stylesheet", href: href }));
}

function shortTs(ts) { return ts ? String(ts).replace("T", " ").replace("Z", "") : "—"; }

/* One mark. Glyph + word, always both, per palette.js's measured rule. */
function markEl(res, extraClass) {
  return el("span", { class: "vnv-mark " + res.cls + (extraClass ? " " + extraClass : "") }, [
    el("span", { class: "vnv-glyph", text: res.glyph, "aria-hidden": "true" }),
    el("span", { class: "vnv-word", text: res.label }),
  ]);
}

/* The streak: one tick per historical run, oldest → newest. This is the thing that
 * makes an erased failure impossible — the ticks are the record, not the verdict. */
function streakEl(cell) {
  const wrap = el("span", { class: "vnv-streak" });
  const runs = cell.runs;
  const MAX = 8;
  const shown = runs.length > MAX ? runs.slice(runs.length - MAX) : runs;
  if (runs.length > MAX) {
    wrap.appendChild(el("span", { class: "vnv-tick vnv-more",
      text: "+" + (runs.length - MAX),
      title: (runs.length - MAX) + " earlier runs — open the cell for all of them" }));
  }
  shown.forEach(function (r) {
    wrap.appendChild(el("span", {
      class: "vnv-tick " + r.result.cls, text: r.result.glyph,
      title: "run-" + r.n + " @" + r.config + " · " + r.result.label + " · " + shortTs(r.ts),
    }));
  });
  return wrap;
}

function cellEl(item, config, cell, onOpen) {
  const res = cell ? cell.latest.result : UNMEASURED;
  const classes = ["vnv-cell", res.cls];
  if (cell && cell.hiddenFail) classes.push("vnv-hasfail");
  if (!cell) classes.push("vnv-empty");
  const td = el("td", {
    class: classes.join(" "), tabindex: "0", role: "button",
    "data-item": item.id, "data-config": config || "",
    title: cell
      ? item.id + " @" + config + "\nlatest: run-" + cell.latest.n + " " +
        cell.latest.result.label + " (" + shortTs(cell.latest.ts) + ")\n" +
        cell.total + " run(s), " + cell.fail + " failed" +
        (cell.hiddenFail ? "\n⚠ this cell's latest run did NOT fail, but "
                           + cell.fail + " earlier run(s) did" : "")
      : item.id + " @" + (config || "any config") +
        "\nNEVER RUN — unmeasured. This is not a pass.",
  });
  td.appendChild(markEl(res));
  if (cell) {
    td.appendChild(streakEl(cell));
    const tally = el("span", { class: "vnv-tally" });
    tally.appendChild(txt(cell.total + (cell.total === 1 ? " run" : " runs")));
    if (cell.fail > 0) {
      tally.appendChild(el("b", {
        class: "vnv-failcount",
        text: " ⚠ " + cell.fail + " FAILED" + (cell.hiddenFail ? " EARLIER" : ""),
      }));
    }
    td.appendChild(tally);
  } else {
    td.appendChild(el("span", { class: "vnv-tally", text: "0 runs · unmeasured" }));
  }
  const open = function () { onOpen(item, config, cell); };
  td.addEventListener("click", open);
  td.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
  });
  return td;
}

function legendEl() {
  const wrap = el("div", { class: "vnv-legend" });
  const add = function (res, note) {
    wrap.appendChild(el("span", { class: "vnv-legend-item" }, [
      markEl(res), el("span", { class: "vnv-legend-note", text: note }),
    ]));
  };
  add(RESULT.pass, "latest run passed");
  add(RESULT.fail, "latest run failed — it stands forever");
  add(RESULT.partial, "latest run partially met its criteria");
  add(UNMEASURED, "nobody has run it. NOT a pass.");
  wrap.appendChild(el("span", { class: "vnv-legend-item vnv-legend-rule" }, [
    el("span", { class: "vnv-tick vnv-fail", text: "✘" }),
    el("span", { class: "vnv-tick vnv-fail", text: "✘" }),
    el("span", { class: "vnv-tick vnv-pass", text: "✔" }),
    el("span", { class: "vnv-legend-note",
      text: "one tick per run, oldest first — a pass never erases an earlier fail" }),
  ]));
  wrap.appendChild(el("span", { class: "vnv-legend-item vnv-legend-rule" }, [
    el("span", { class: "vnv-legend-note",
      text: "run numbers restart per config: run-1@minimal-13 and run-1@full-578 are " +
            "different questions, not a retry" }),
  ]));
  return wrap;
}

/* ------------------------------------------------------------------ drill-down */

function detailEl(view, sel) {
  const dock = el("div", { class: "vnv-dock" });
  if (!sel) {
    dock.appendChild(el("div", { class: "vnv-dock-hint",
      text: "Select a cell to see every run it has ever had — not just the latest." }));
    return dock;
  }
  const item = sel.item;
  const runs = sel.config
    ? (item.cells[sel.config] ? item.cells[sel.config].runs : [])
    : item.runs;
  const k = kindOf(item);
  dock.appendChild(el("div", { class: "vnv-dock-head" }, [
    el("span", { class: "vnv-kind", text: k.glyph, title: k.label,
                 style: "color:" + k.hex }),
    el("b", { class: "vnv-dock-id", text: item.id }),
    el("span", { class: "vnv-dock-scope",
      text: sel.config ? "@" + sel.config : "all configs" }),
    el("span", { class: "vnv-dock-title", text: item.title }),
  ]));
  dock.appendChild(el("div", { class: "vnv-dock-meta", text:
    [k.label, item.owner, item.state, "needs " + item.needs,
     item.target].filter(Boolean).join(" · ") +
    (item.blocked ? " · ⚠ BLOCKED: " + item.blockedReason : "") }));

  if (!runs.length) {
    dock.appendChild(el("div", { class: "vnv-dock-hint vnv-unmeasured-note", text:
      "NEVER RUN" + (sel.config ? " against " + sel.config : "") +
      ". Unmeasured, which is not the same as passed and must never be read as one." }));
    dock.appendChild(el("code", { class: "vnv-cmd",
      text: "rimflow verify " + item.id + " --result pass|fail|partial --config " +
            (sel.config || "<config>") + " --evidence <path>" }));
    return dock;
  }

  const tbl = el("table", { class: "vnv-runs" });
  tbl.appendChild(el("thead", {}, [el("tr", {}, ["run", "config", "result", "when",
      "sha", "evidence", "findings"].map(function (h) {
    return el("th", { text: h });
  }))]));
  const tb = el("tbody");
  /* Newest first here — the dock answers "what happened, most recently first",
   * while the streak in the cell answers "in what order did it happen". */
  runs.slice().reverse().forEach(function (r) {
    const fs = item.findings.filter(function (name) {
      const f = view.findings[name];
      return f && f.from === r.name;
    });
    tb.appendChild(el("tr", { class: r.result.cls }, [
      el("td", { class: "vnv-runname", text: "run-" + r.n }),
      el("td", { text: r.config || "—" }),
      el("td", {}, [markEl(r.result, "vnv-mark-inline")]),
      el("td", { text: shortTs(r.ts) }),
      el("td", { class: "vnv-sha", text: r.sha ? String(r.sha).slice(0, 10) : "—" }),
      el("td", { class: "vnv-evidence", text: r.evidence || "—",
                 title: r.evidence || "" }),
      el("td", { text: fs.length ? fs.join(", ") : "—" }),
    ]));
  });
  tbl.appendChild(tb);
  dock.appendChild(tbl);
  const fails = runs.filter(function (r) { return r.raw === "fail"; }).length;
  dock.appendChild(el("div", { class: "vnv-dock-foot" + (fails ? " vnv-hasfail" : ""),
    text: runs.length + " run(s) recorded · " + fails + " failed · every one is " +
          "immutable; the follow-up to a fail is a NEW item, never a reopen" }));
  return dock;
}

/* ---------------------------------------------------------------- empty states */

function panel(kind, head, lines, cmd) {
  const p = el("div", { class: "vnv-panel " + kind });
  p.appendChild(el("h2", { text: head }));
  lines.forEach(function (l) { p.appendChild(el("p", { text: l })); });
  if (cmd) p.appendChild(el("code", { class: "vnv-cmd", text: cmd }));
  return p;
}

/* --------------------------------------------------------------------- render */

export function render(root, board) {
  stylesheet();
  root.className = (root.className || "").replace(/\bvnv\b/g, "").trim() + " vnv";
  root.textContent = "";

  const view = project(board);
  if (!view.ok) {
    root.appendChild(view.reason === "unavailable"
      ? panel("vnv-bad", "V&V MATRIX — UNAVAILABLE", [
          "The board could not be built, so there is nothing to show. An empty " +
          "matrix would read as 'everything passed'; this says nothing is known.",
          view.why])
      : panel("vnv-bad", "V&V MATRIX — NO RUN DATA IN THIS PAYLOAD", [
          "Per-item runs are missing from /board, so this view cannot draw the " +
          "matrix. It is deliberately not drawing an empty one.",
          view.why]));
    return view;
  }

  const st = view.stats;
  const state = { q: "", failsOnly: false,
                  showUnverified: st.verified === 0, sel: null };

  /* --- header ------------------------------------------------------------- */
  const head = el("header", { class: "vnv-head" }, [
    el("h1", { text: "V&V MATRIX" }),
    el("span", { class: "vnv-sub", text: "items × configurations · each cell the " +
                                         "latest run, with all of its history" }),
  ]);
  const stats = el("span", { class: "vnv-stats" });
  const stat = function (n, l, cls) {
    stats.appendChild(el("span", { class: "vnv-stat " + (cls || "") }, [
      el("b", { text: String(n) }), el("i", { text: l })]));
  };
  stat(st.items, "items");
  stat(st.configs, "configs");
  stat(st.runs, "runs");
  stat(st.verified, "verified");
  stat(st.unverified, "UNMEASURED", "vnv-stat-unmeasured");
  stat(st.fails, "FAILS on record", st.fails ? "vnv-stat-fail" : "");
  head.appendChild(stats);
  if (view.asOf) head.appendChild(el("span", { class: "vnv-asof",
    text: "as of " + shortTs(view.asOf) + (view.schema ? " · " + view.schema : "") }));
  if (view.ledgerErrors) head.appendChild(el("span", { class: "vnv-warn",
    text: "⚠ the ledger refused " + view.ledgerErrors + " event(s) — the run record " +
          "may be incomplete" }));
  root.appendChild(head);
  root.appendChild(legendEl());

  /* --- the "nothing verified yet" case, which is today's real state -------- */
  if (st.runs === 0) {
    root.appendChild(panel("vnv-void", "NOTHING HAS BEEN VERIFIED YET", [
      "0 runs across " + st.items + " items, and 0 configurations have been seen. " +
      "That is a true statement about the record, not a failure of this view: the " +
      "ledger was imported from hand-written queues that never recorded a run.",
      "⚠ Every row below is UNMEASURED. Unmeasured is not passed. No item on this " +
      "board has been shown to work, and none has been shown to be broken.",
      "Columns appear on their own as configurations show up in the runs — nothing " +
      "here is hard-coded, so a new config gets a column the moment it is used.",
    ], "rimflow verify <ID> --result pass|fail|partial --config <config> " +
       "--evidence <path>"));
  }

  /* --- controls ------------------------------------------------------------ */
  const bar = el("div", { class: "vnv-controls" });
  const q = el("input", { class: "vnv-q", type: "search",
                          placeholder: "filter by id, title, owner or kind" });
  bar.appendChild(q);
  const toggle = function (label, key, hint) {
    const id = "vnv-t-" + key;
    const cb = el("input", { type: "checkbox", id: id });
    cb.checked = !!state[key];
    cb.addEventListener("change", function () { state[key] = cb.checked; draw(); });
    bar.appendChild(el("label", { class: "vnv-toggle", title: hint || "" },
      [cb, el("span", { text: label })]));
  };
  toggle("show UNMEASURED items", "showUnverified",
         "items with no run at all — off by default only when there is real data " +
         "to look at; they are never counted as passing either way");
  toggle("only rows that ever FAILED", "failsOnly",
         "every fail is permanent, so this finds them even where the latest run passed");
  const count = el("span", { class: "vnv-count" });
  bar.appendChild(count);
  root.appendChild(bar);

  const host = el("div", { class: "vnv-scroll" });
  root.appendChild(host);
  const dockHost = el("div", { class: "vnv-dockhost" });
  root.appendChild(dockHost);

  /* --- the matrix ---------------------------------------------------------- */
  /* With no runs anywhere there are no real columns. Rather than draw nothing —
   * which is indistinguishable from a clean sheet — draw one honest column of
   * NEVER RUN so the roster still says, per item, that it is unmeasured. */
  const columns = view.configs.length ? view.configs : [null];

  function rows() {
    const needle = state.q.trim().toLowerCase();
    return view.items.filter(function (i) {
      if (state.failsOnly && !i.everFailed) return false;
      if (!state.showUnverified && i.total === 0) return false;
      if (!needle) return true;
      return (i.id + " " + i.title + " " + i.owner + " " + i.kind)
        .toLowerCase().indexOf(needle) >= 0;
    }).sort(function (a, b) {
      /* Anything with a fail in its history first — that is what a reader is here
       * for — then the rest of the verified, then the unmeasured. */
      const rank = function (i) { return i.everFailed ? 0 : i.total ? 1 : 2; };
      return rank(a) - rank(b) || a.id.localeCompare(b.id);
    });
  }

  function openCell(item, config, cell) {
    state.sel = { item: item, config: config, cell: cell };
    drawDock();
    host.querySelectorAll(".vnv-cell.vnv-sel").forEach(function (n) {
      n.classList.remove("vnv-sel");
    });
    const q2 = '.vnv-cell[data-item="' + (window.CSS && CSS.escape
      ? CSS.escape(item.id) : item.id) + '"][data-config="' + (config || "") + '"]';
    const n = host.querySelector(q2);
    if (n) n.classList.add("vnv-sel");
  }

  function drawDock() {
    dockHost.textContent = "";
    dockHost.appendChild(detailEl(view, state.sel));
  }

  function draw() {
    host.textContent = "";
    const list = rows();
    count.textContent = list.length + " of " + view.items.length + " items shown";

    const tbl = el("table", { class: "vnv-matrix" });
    const hr = el("tr", {}, [
      el("th", { class: "vnv-h-item", text: "item" }),
      el("th", { class: "vnv-h-all", text: "all runs",
                 title: "across every configuration — so a fail cannot hide off-screen" }),
    ]);
    columns.forEach(function (c) {
      hr.appendChild(el("th", { class: "vnv-h-config" }, [
        el("b", { text: c || "no configuration recorded yet" }),
        el("i", { text: c ? (view.items.reduce(function (a, i) {
          return a + (i.cells[c] ? i.cells[c].total : 0); }, 0)) + " runs" : "—" }),
      ]));
    });
    tbl.appendChild(el("thead", {}, [hr]));

    const tb = el("tbody");
    list.forEach(function (item) {
      const k = kindOf(item);
      const tr = el("tr", { class: item.everFailed ? "vnv-row-fail" : "" });
      const idc = el("td", { class: "vnv-item" }, [
        el("span", { class: "vnv-kind", text: k.glyph, title: k.label,
                     style: "color:" + k.hex }),
        el("b", { class: "vnv-id", text: item.id, title: item.title }),
        el("span", { class: "vnv-itemmeta",
                     text: [item.owner, item.state].filter(Boolean).join(" · ") +
                           (item.blocked ? " ⚠" : "") }),
      ]);
      idc.addEventListener("click", function () { openCell(item, null, null); });
      tr.appendChild(idc);
      tr.appendChild(el("td", { class: "vnv-all" +
          (item.everFailed ? " vnv-hasfail" : item.total ? "" : " vnv-unmeasured"),
        text: item.total === 0 ? "· never run"
              : item.total + " run" + (item.total === 1 ? "" : "s") +
                (item.fails ? " · ⚠ " + item.fails + " FAILED" : " · 0 failed"),
      }));
      columns.forEach(function (c) {
        tr.appendChild(cellEl(item, c, c ? item.cells[c] : null, openCell));
      });
      tb.appendChild(tr);
    });
    tbl.appendChild(tb);
    host.appendChild(tbl);
    if (!list.length) {
      host.appendChild(el("div", { class: "vnv-dock-hint",
        text: "No item matches the filter. Nothing here is a pass — it is a filter." }));
    }
  }

  q.addEventListener("input", function () { state.q = q.value; draw(); });
  draw();
  drawDock();
  return view;
}

export default render;
