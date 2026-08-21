/* timeline.js — the ledger, filtered.  "What changed since I was last here."
 * =============================================================================
 *
 * 🔑 THE QUESTION IS THE DESIGN.  A raw event log is not a timeline: 352 events
 * scrolling past answers nothing.  This view answers exactly one question — *what
 * changed since I was last here* — and everything below is in service of that.
 *
 *   1. It picks a WINDOW and says out loud which rule picked it.  A view that
 *      silently chooses a window is a view that lies by omission.
 *   2. Inside the window it promotes what MOVED — close · block/unblock · finding ·
 *      spawn · drop · supersede · verify · retarget · reassign — and gives
 *      `game` · `bridge` · `admin` full-width bands, because a reader scanning back
 *      wants to know which deployment a run belonged to.
 *   3. Bookkeeping — `file` · `claim` · `start` · `note` · `seat` — is COLLAPSED,
 *      never dropped.  ⚠️ A filter that silently discards events makes the view lie
 *      about an append-only file, which is the one thing the ledger exists to
 *      prevent.  The footer carries `window = signal + bands + collapsed + torn`
 *      and shouts if that identity ever fails to hold.
 *
 * ⛔ ORDER IS THE FILE, NEVER THE CLOCK.  `ts` is second-resolution UTC and two
 * events routinely share one.  Position in `events.jsonl` is the causal order, so
 * nothing here ever sorts by `ts` — `ts` is display and bucketing only.  Re-sorting
 * a causal ledger reorders cause and effect, which is worse than showing nothing.
 *
 * ⛔ COLOUR IS NEVER THE ONLY ENCODING.  Categorical hue comes from ./palette.js,
 * and every mark carries its glyph AND its label — two of our own categories are
 * ΔE 7.1 apart to a reader with ordinary sight.  STATUS is a separate channel and
 * never borrows a categorical hue: it is form only — ring, dashed outline, opacity,
 * strike, and a leading verb glyph.  The only two colours this file adds are chrome,
 * not marks: restrained cyan for neutral-active, amber for attention.
 *
 * ⛔ NO MOTION.  No auto-scroll, no ticking clock, no transitions.  This page is
 * left open all day on a second monitor.
 *
 * Vanilla ES module.  No build step, no CDN, no framework.
 *
 * ── ENTRY POINT ──────────────────────────────────────────────────────────────
 *   render(root, board, opts) -> controller { refresh(), destroy(), state() }
 *
 *   board   the /board projection (rimflow-board/1).  Used for `as_of`, `game`,
 *           `bridge_holder`, and — importantly — its `events` COUNT, which this
 *           view cross-checks against the lines it actually read.  A projection
 *           that has seen events this view has not means a stale source, and that
 *           is worth saying rather than hiding.
 *
 *   opts.events    array of raw event objects, if the host already has them
 *   opts.text      raw JSONL text
 *   opts.url       one URL to fetch JSONL from
 *   opts.probe     candidate URLs to try in order (default PROBE below)
 *   opts.sessionGapMin   minutes of silence that ends a session (default 45)
 *   opts.maxRows         row budget before older rows are elided (default 400)
 *   opts.storageKey      localStorage key for the read-watermark
 *
 * ⚠️ MISSING ENDPOINT, 2026-08-20.  `/board` carries `events` as an integer COUNT,
 * not the stream, so there is today no served route to the raw ledger.  This module
 * probes for one and, finding none, renders an explicit UNAVAILABLE panel naming the
 * file and every URL it tried.  It does NOT render an empty timeline — an empty
 * timeline is an answer, and "I could not read the source" is not that answer.
 */
import { kindOf } from "./palette.js";

/* Candidate routes for the raw ledger, tried in order.  None of these exist yet;
 * see the MISSING ENDPOINT note above.  Adding one to status_server.py is the fix. */
export const PROBE = [
  "/ledger/events.jsonl",
  "/ledger",
  "/events",
  "/board/events",
];

export const LEDGER_PATH = "infrastructure/state/ledger/events.jsonl";

/* ── The 18-verb vocabulary, mirroring rimflow/model.py's VERBS table ─────────
 * `tier` decides prominence, never visibility.
 *   signal   one row each, always shown
 *   band     full-width rule across the timeline — a context boundary
 *   chatter  bucketed into one expandable row per (minute, seat, verb)
 * ⚠️ A verb this table does not know is NOT chatter and is NOT dropped: it is
 * promoted to signal, glyphed `?` and counted in the banner.  model.py is allowed
 * to grow a verb before this file hears about it, and the failure mode of that must
 * be "loud", not "invisible". */
export const VERB = {
  file:      { g: "+", label: "filed",      tier: "chatter" },
  claim:     { g: "»", label: "claimed",    tier: "chatter" },
  start:     { g: "▶", label: "started",    tier: "chatter" },
  note:      { g: "·", label: "note",       tier: "chatter" },
  seat:      { g: "▪", label: "seat state", tier: "chatter" },

  close:     { g: "✓", label: "CLOSED",     tier: "signal", loud: true },
  block:     { g: "⚠", label: "BLOCKED",    tier: "signal", loud: true, warn: true },
  unblock:   { g: "↑", label: "unblocked",  tier: "signal", loud: true },
  finding:   { g: "!", label: "FINDING",    tier: "signal", loud: true, warn: true },
  spawn:     { g: "✧", label: "spawned",    tier: "signal", loud: true },
  verify:    { g: "⊨", label: "verified",   tier: "signal" },
  drop:      { g: "✕", label: "dropped",    tier: "signal", dim: true },
  supersede: { g: "↷", label: "superseded", tier: "signal", dim: true },
  retarget:  { g: "→", label: "retargeted", tier: "signal" },
  reassign:  { g: "⇄", label: "reassigned", tier: "signal" },

  game:      { g: "◐", label: "GAME",   tier: "band" },
  bridge:    { g: "⇌", label: "BRIDGE", tier: "band" },
  admin:     { g: "§", label: "ADMIN",  tier: "band", warn: true },
};

const UNKNOWN_VERB = { g: "?", label: "UNKNOWN VERB", tier: "signal", warn: true };

export function verbOf(name) {
  return VERB[name] || UNKNOWN_VERB;
}

/* ── Parsing ─────────────────────────────────────────────────────────────────
 * 🔴 NOTHING IS EVER SKIPPED.  This repo lives on a 9p mount where unlocked
 * concurrent appends lose writes, so a torn line is a real, expected event and the
 * whole point of noticing it is that it is visible.  A parser that `continue`s past
 * a bad line hides exactly the failure the ledger exists to expose.
 *
 * Every input line becomes one record, in file order:
 *   ok         a parsed event object
 *   torn       JSON.parse failed
 *   interleaved   parse failed AND the raw text carries a second `{"seat"` — the
 *                 signature of two appends landing inside one line
 *   malformed  parsed, but not an object, or missing `event`/`ts`
 *   blank      an empty line in the middle of the file (a trailing one is normal)
 */
export function parseLedger(text) {
  const out = { events: [], bad: [], lines: 0, trailingNewline: true };
  if (text == null) return out;
  const raw = String(text).replace(/\r/g, "");
  const lines = raw.split("\n");
  if (lines.length && lines[lines.length - 1] === "") lines.pop();
  else out.trailingNewline = false;
  out.lines = lines.length;

  lines.forEach((line, i) => {
    const lineNo = i + 1;
    const rec = { idx: out.events.length, line: lineNo, raw: line };
    if (line.trim() === "") {
      rec.bad = "blank";
      rec.why = "empty line inside an append-only file";
    } else {
      let v = null;
      try {
        v = JSON.parse(line);
      } catch (e) {
        rec.bad = /\{\s*"seat"/.test(line.slice(1)) || line.includes("}{")
          ? "interleaved" : "torn";
        rec.why = String(e && e.message || e);
      }
      if (!rec.bad) {
        if (!v || typeof v !== "object" || Array.isArray(v)) {
          rec.bad = "malformed";
          rec.why = "line is valid JSON but not an event object";
        } else if (!v.event || !v.ts) {
          rec.bad = "malformed";
          rec.why = "event object with no " + (!v.event ? "`event` verb" : "`ts`");
        } else {
          Object.assign(rec, v);
        }
        if (rec.bad && v && typeof v === "object") Object.assign(rec, v, { bad: rec.bad, why: rec.why });
      }
    }
    rec.idx = out.events.length;
    out.events.push(rec);
    if (rec.bad) out.bad.push(rec);
  });
  return out;
}

/* Kind travels with the ITEM, not with the event: only `file` and `spawn` declare a
 * `kind`, so a later `close B53` has to inherit it.  Built over the WHOLE file, never
 * just the window, because the `file` event is usually outside it. */
export function kindIndex(events) {
  const byId = new Map();
  for (const e of events) {
    if (e.bad) continue;
    const id = e.event === "spawn" ? e.name : e.id;
    if (!id) continue;
    if (e.kind && !byId.has(id)) byId.set(id, { kind: e.kind, inherited: false });
    if (e.title && byId.has(id) && !byId.get(id).title) byId.get(id).title = e.title;
    else if (e.title && !byId.has(id)) byId.set(id, { kind: null, title: e.title });
  }
  return byId;
}

/* ── Sessions ────────────────────────────────────────────────────────────────
 * A session is a contiguous run of events separated from the next by `gapMin`
 * minutes of silence.  Computed off `ts` but WITHOUT sorting: the file order is
 * walked once and a gap opens a new session.  A `ts` that goes backwards is a clock
 * anomaly, recorded on the session rather than repaired by re-ordering. */
export function sessionize(events, gapMin) {
  const gap = (gapMin == null ? 45 : gapMin) * 60 * 1000;
  const out = [];
  let cur = null, prevT = null;
  for (const e of events) {
    const t = tms(e.ts);
    if (!cur || (t != null && prevT != null && t - prevT > gap)) {
      cur = { from: e.idx, to: e.idx, start: e.ts, end: e.ts, n: 0, backwards: 0 };
      out.push(cur);
    }
    if (t != null && prevT != null && t < prevT) cur.backwards++;
    cur.to = e.idx; cur.end = e.ts; cur.n++;
    if (t != null) prevT = t;
  }
  return out;
}

function tms(ts) {
  if (!ts) return null;
  const v = Date.parse(ts);
  return Number.isNaN(v) ? null : v;
}

/* ── "Since I was last here" ─────────────────────────────────────────────────
 * Decided in this order, and the RULE THAT FIRED IS PRINTED AT THE TOP.  A reader
 * must never have to guess which window they are looking at.
 *
 *   1. visit    a read-watermark this reader previously set — the honest answer.
 *               Kept as (count, fingerprint-of-last-line).  If the file no longer
 *               matches — an append-only file that shrank or was rewritten — the
 *               watermark is REFUSED, loudly, and rule 2 takes over.
 *   2. session  the last session (gap-separated burst of work).
 *   3. cap      if that session is itself enormous — a bulk import, which is
 *               exactly what this ledger's 352-events-in-2-seconds is — the window
 *               stays the session but the header says so, and collapsing does the
 *               rest.  ⚠️ The cap NEVER shortens the window silently.
 *   4. explicit 24h / 7d / all, chosen by the reader.
 */
export function chooseWindow(events, mode, watermark, opts) {
  const o = opts || {};
  const n = events.length;
  const sessions = sessionize(events, o.sessionGapMin);
  const last = sessions[sessions.length - 1];
  const nowMs = o.now != null ? o.now : Date.now();
  const newest = n ? tms(events[n - 1].ts) : null;
  /* An import-era ledger can be "old" against a real wall clock; anchor relative
   * windows on the newest event when it is ahead of, or far behind, now. */
  const anchor = (newest != null && newest > nowMs) ? newest : nowMs;

  const bySession = () => ({
    mode: "session", from: last ? last.from : 0,
    rule: "last session — the newest burst of work, separated by ≥ " +
          (o.sessionGapMin == null ? 45 : o.sessionGapMin) + " min of silence",
  });

  if (mode === "all") return { mode: "all", from: 0, rule: "everything in the file" };
  if (mode === "24h" || mode === "7d") {
    const span = mode === "24h" ? 864e5 : 6048e5;
    let from = n;
    for (let i = n - 1; i >= 0; i--) {
      const t = tms(events[i].ts);
      if (t == null || anchor - t <= span) from = i; else break;
    }
    return { mode, from, rule: "last " + (mode === "24h" ? "24 hours" : "7 days") +
             (anchor !== nowMs ? " (relative to the newest event, not the wall clock)" : "") };
  }
  if (mode === "session" || !watermark) {
    const w = bySession();
    if (!watermark && mode !== "session") {
      w.rule = "no read-watermark yet, so: " + w.rule +
               ". Mark as read and the next visit shows only what is new.";
    }
    return w;
  }

  /* mode === "visit" */
  if (watermark.n > n) {
    const w = bySession();
    w.refused = "your watermark is at event " + watermark.n + " but the file holds only " +
      n + ". An append-only file must never shrink — the source is truncated, replaced, " +
      "or you are reading a different ledger. Falling back to the last session.";
    return w;
  }
  const at = events[watermark.n - 1];
  if (watermark.n > 0 && (!at || fingerprint(at.raw) !== watermark.fp)) {
    const w = bySession();
    w.refused = "your watermark pointed at line " + watermark.n +
      ", and that line's contents have CHANGED. An append-only file is not supposed to " +
      "rewrite history. Falling back to the last session.";
    return w;
  }
  return {
    mode: "visit", from: watermark.n,
    rule: "since you marked the ledger read at " + (watermark.at || "?") +
          " — event " + watermark.n + " of " + n,
    empty: watermark.n >= n,
  };
}

export function fingerprint(s) {
  let h = 2166136261;
  const str = String(s == null ? "" : s);
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = (h * 16777619) >>> 0;
  }
  return h.toString(16);
}

/* ── Rows ────────────────────────────────────────────────────────────────────
 * Turn a window of events into row descriptors.  Signal and band events get one row
 * each, in file order.  Chatter is bucketed by (minute, seat, verb) and anchored at
 * the index of its FIRST member, so it sits where it happened; expanding shows its
 * members in file order.  Torn lines are never bucketed and never elided.
 *
 * 🔑 The invariant this function must satisfy, and which render() prints:
 *        window = signal + bands + collapsed + torn
 * If it ever fails, something was dropped, and the footer says so in amber. */
export function buildRows(events, from, expanded) {
  const win = events.slice(from);
  const rows = [];
  const buckets = new Map();
  let signal = 0, bands = 0, collapsed = 0, torn = 0, unknown = 0;

  for (const e of win) {
    if (e.bad) {
      rows.push({ type: "bad", e });
      torn++;
      continue;
    }
    const v = verbOf(e.event);
    if (v === UNKNOWN_VERB) unknown++;
    if (v.tier === "band") { rows.push({ type: "band", e, v }); bands++; continue; }
    if (v.tier === "chatter") {
      const key = String(e.ts || "").slice(0, 16) + "|" + (e.seat || "?") + "|" + e.event;
      let b = buckets.get(key);
      if (!b) {
        b = { type: "bucket", key, verb: e.event, v, seat: e.seat, ts: e.ts, members: [] };
        buckets.set(key, b);
        rows.push(b);
      }
      b.members.push(e);
      collapsed++;
      continue;
    }
    rows.push({ type: "signal", e, v });
    signal++;
  }

  /* A bucket of one or two is not worth collapsing — expanding it costs a click to
   * learn nothing.  Promote those to plain rows in place. */
  const outRows = [];
  for (const r of rows) {
    if (r.type === "bucket" && r.members.length <= 2) {
      for (const m of r.members) outRows.push({ type: "quiet", e: m, v: r.v });
      continue;
    }
    outRows.push(r);
    if (r.type === "bucket" && expanded && expanded.has(r.key)) {
      for (const m of r.members) outRows.push({ type: "quiet", e: m, v: r.v, inBucket: true });
    }
  }

  const counts = { window: win.length, signal, bands, collapsed, torn, unknown };
  counts.balances = (signal + bands + collapsed + torn) === win.length;
  return { rows: outRows, counts };
}

/* ── DOM helpers ─────────────────────────────────────────────────────────────
 * textContent only, never innerHTML: ledger `reason` and `title` text is written by
 * seats and by the owner and is not markup. */
function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = String(text);
  return n;
}

function ensureCss() {
  if (typeof document === "undefined") return;
  if (document.getElementById("rimflow-timeline-css")) return;
  const l = document.createElement("link");
  l.id = "rimflow-timeline-css";
  l.rel = "stylesheet";
  l.href = new URL("./timeline.css", import.meta.url).href;
  document.head.appendChild(l);
}

function shortTs(ts) {
  const s = String(ts || "");
  return s.length >= 19 ? s.slice(5, 10) + " " + s.slice(11, 19) : (s || "—");
}

function clip(s, n) {
  const t = String(s == null ? "" : s).replace(/\s+/g, " ").trim();
  return t.length > n ? { text: t.slice(0, n - 1) + "…", full: t } : { text: t, full: null };
}

/* ── Storage ─────────────────────────────────────────────────────────────────
 * Wrapped, because a private window, cleared site data or a browser set to block
 * storage makes every accessor throw.  No watermark is a normal state, not an error. */
function readMark(key) {
  try {
    const v = JSON.parse(localStorage.getItem(key) || "null");
    return v && typeof v.n === "number" ? v : null;
  } catch (e) { return null; }
}
function writeMark(key, v) {
  try { localStorage.setItem(key, JSON.stringify(v)); return true; }
  catch (e) { return false; }
}

/* ── Source resolution ───────────────────────────────────────────────────────
 * Returns { text, via } or { error, tried }.  Never returns silence. */
async function resolveSource(opts) {
  const o = opts || {};
  if (Array.isArray(o.events)) return { events: o.events, via: "opts.events (host-supplied)" };
  if (typeof o.text === "string") return { text: o.text, via: "opts.text (host-supplied)" };
  const tried = [];
  const urls = o.url ? [o.url] : (o.probe || PROBE);
  for (const u of urls) {
    try {
      const r = await fetch(u, { cache: "no-store" });
      if (!r.ok) { tried.push(u + " → HTTP " + r.status); continue; }
      const t = await r.text();
      if (!/^\s*\{/.test(t)) {
        tried.push(u + " → HTTP 200 but the body is not JSONL (first bytes: " +
                   JSON.stringify(t.slice(0, 24)) + ")");
        continue;
      }
      return { text: t, via: u };
    } catch (e) {
      tried.push(u + " → " + (e && e.message || e));
    }
  }
  return { error: "no served route to the raw ledger", tried };
}

/* ── render ──────────────────────────────────────────────────────────────────*/
export function render(root, board, opts) {
  const o = Object.assign({
    sessionGapMin: 45,
    maxRows: 400,
    storageKey: "rimflow.timeline.watermark",
  }, opts || {});
  ensureCss();

  const st = {
    mode: o.mode || "visit",
    expanded: new Set(),
    expandedText: new Set(),
    showAllRows: false,
    parsed: null,
    source: null,
    mark: readMark(o.storageKey),
    destroyed: false,
  };

  root.textContent = "";
  const shell = el("div", "tl");
  root.appendChild(shell);

  const head = el("div", "tl-head"); shell.appendChild(head);
  const body = el("div", "tl-body"); shell.appendChild(body);
  const foot = el("div", "tl-foot"); shell.appendChild(foot);

  head.appendChild(el("div", "tl-title", "TIMELINE — what changed since you were last here"));
  const status = el("div", "tl-status", "resolving the ledger…");
  head.appendChild(status);

  async function load() {
    const src = await resolveSource(o);
    if (st.destroyed) return;
    st.source = src;
    if (src.error) { st.parsed = null; paint(); return; }
    st.parsed = src.events
      ? { events: src.events.map((e, i) => Object.assign({ idx: i, line: i + 1, raw: JSON.stringify(e) }, e)),
          bad: [], lines: src.events.length, trailingNewline: true }
      : parseLedger(src.text);
    paint();
  }

  function paint() {
    head.textContent = "";
    body.textContent = "";
    foot.textContent = "";
    head.appendChild(el("div", "tl-title", "TIMELINE — what changed since you were last here"));

    /* ── the source could not be read.  Say so; do NOT render an empty timeline. */
    if (!st.parsed) {
      const s = st.source || {};
      const p = el("div", "tl-panel tl-warn");
      p.appendChild(el("div", "tl-panel-h", "⚠  LEDGER UNREADABLE — this is not an empty timeline"));
      p.appendChild(el("p", null,
        "The board projection reports " + (board && board.events != null ? board.events : "?") +
        " events, so the ledger exists. This view could not read them."));
      p.appendChild(el("p", "tl-path", LEDGER_PATH));
      if (s.tried && s.tried.length) {
        p.appendChild(el("div", "tl-panel-sub", "routes tried:"));
        const ul = el("ul", "tl-tried");
        s.tried.forEach((t) => ul.appendChild(el("li", null, t)));
        p.appendChild(ul);
      }
      p.appendChild(el("p", "tl-note",
        "MISSING ENDPOINT: /board serves `events` as an integer count, not the stream. " +
        "A route that returns events.jsonl verbatim — or `opts.events` / `opts.text` from " +
        "the host page — is all this view needs."));
      head.appendChild(p);
      foot.appendChild(el("div", "tl-foot-l", "0 rows rendered · source unavailable"));
      return;
    }

    const events = st.parsed.events;
    const kinds = kindIndex(events);
    const win = chooseWindow(events, st.mode, st.mark, o);
    const built = buildRows(events, win.from, st.expanded);

    /* ── controls: every window names its own size, so a choice is never blind. */
    const bar = el("div", "tl-bar");
    const counts = windowSizes(events, st.mark, o);
    [["visit", "since last visit"], ["session", "last session"],
     ["24h", "last 24h"], ["7d", "last 7d"], ["all", "everything"]].forEach(([m, label]) => {
      const b = el("button", "tl-btn" + (win.mode === m ? " on" : ""),
                   label + "  " + counts[m]);
      b.type = "button";
      b.setAttribute("aria-pressed", String(win.mode === m));
      b.onclick = () => { st.mode = m; st.showAllRows = false; paint(); };
      bar.appendChild(b);
    });
    const marker = el("button", "tl-btn tl-mark", st.mark ? "mark read ✓" : "mark read");
    marker.type = "button";
    marker.title = "Records where you got to, so the next visit shows only what is new.";
    marker.onclick = () => {
      const n = events.length;
      const v = { n, fp: n ? fingerprint(events[n - 1].raw) : "", at: nowIso(o) };
      st.mark = writeMark(o.storageKey, v) ? v : st.mark;
      if (!st.mark) alert("localStorage is unavailable in this browser context; the watermark could not be saved.");
      st.mode = "visit"; paint();
    };
    bar.appendChild(marker);
    head.appendChild(bar);

    /* ── the rule that picked this window, in words. */
    const rule = el("div", "tl-rule");
    rule.appendChild(el("span", "tl-rule-k", "window"));
    rule.appendChild(el("span", null, win.rule));
    head.appendChild(rule);
    if (win.refused) head.appendChild(banner("⚠", "WATERMARK REFUSED", win.refused));

    /* ── source integrity, up front. */
    const bad = st.parsed.bad;
    if (bad.length) {
      const kinds_ = bad.reduce((a, b) => (a[b.bad] = (a[b.bad] || 0) + 1, a), {});
      head.appendChild(banner("⤬", "SOURCE DAMAGE — " +
        Object.entries(kinds_).map(([k, n]) => n + " " + k).join(", "),
        "Lines that could not be read as events are shown IN POSITION below, with their raw bytes. " +
        "Nothing has been skipped. This repo is on a 9p mount where unlocked concurrent appends lose " +
        "writes, so a torn or interleaved line is a real failure worth seeing, not a parser quirk."));
    }
    if (!st.parsed.trailingNewline) {
      head.appendChild(banner("⚠", "NO TRAILING NEWLINE",
        "The last line of the ledger does not end in a newline. The next append will land on the same " +
        "line and tear it."));
    }
    if (built.counts.unknown) {
      head.appendChild(banner("?", built.counts.unknown + " EVENT(S) WITH A VERB THIS VIEW DOES NOT KNOW",
        "rimflow/model.py defines 18 verbs. Anything outside that table is promoted, never hidden — " +
        "update VERB in timeline.js."));
    }
    const declared = board && typeof board.events === "number" ? board.events : null;
    if (declared != null && declared !== events.length) {
      head.appendChild(banner("≠", "SOURCE AND PROJECTION DISAGREE",
        "/board was rendered from " + declared + " events; this view read " + events.length + " lines" +
        (declared > events.length ? " — the file this view is reading is stale or truncated."
                                  : " — the projection is stale; " + (events.length - declared) +
                                    " event(s) have landed since it was rendered.")));
    }
    if (win.empty) {
      head.appendChild(banner("·", "NOTHING NEW",
        "No events have been appended since you marked the ledger read. The last session is shown " +
        "below for context."));
    }

    /* ── rows. */
    let rows = built.rows;
    let elided = 0;
    if (!st.showAllRows && rows.length > o.maxRows) {
      elided = rows.length - o.maxRows;
      rows = rows.slice(elided);
      const more = el("button", "tl-more", "▲  " + elided +
        " older rows in this window are not rendered — show them");
      more.type = "button";
      more.onclick = () => { st.showAllRows = true; paint(); };
      body.appendChild(more);
    }

    let lastMinute = null;
    for (const r of rows) {
      const ts = r.e ? r.e.ts : r.ts;
      const minute = String(ts || "").slice(0, 16);
      if (minute && minute !== lastMinute) {
        lastMinute = minute;
        body.appendChild(el("div", "tl-when", minute.replace("T", "  ") + " UTC"));
      }
      body.appendChild(rowNode(r, kinds, st, paint));
    }
    if (!rows.length) {
      body.appendChild(el("div", "tl-empty",
        "The chosen window contains no events. The file holds " + events.length +
        " — widen the window above."));
    }

    /* ── the footer that makes "collapsed, not omitted" checkable. */
    const c = built.counts;
    const l = el("div", "tl-foot-l");
    l.appendChild(el("span", null,
      c.window + " events in window   =   " + c.signal + " signal + " + c.bands +
      " band + " + c.collapsed + " collapsed + " + c.torn + " damaged"));
    l.appendChild(el("span", c.balances ? "tl-ok" : "tl-bad",
      c.balances ? "  ✓ balances — nothing dropped"
                 : "  ✗ DOES NOT BALANCE — events have been lost by this view, not by the ledger"));
    foot.appendChild(l);
    foot.appendChild(el("div", "tl-foot-r",
      events.length + " events in file · " + st.parsed.lines + " lines read · via " +
      (st.source && (st.source.via || "?")) + (elided ? " · " + elided + " rows elided" : "")));
  }

  function windowSizes(events, mark, o2) {
    const out = {};
    for (const m of ["visit", "session", "24h", "7d", "all"]) {
      try {
        const w = chooseWindow(events, m, mark, o2);
        out[m] = "(" + (events.length - w.from) + ")";
      } catch (e) { out[m] = "(?)"; }
    }
    return out;
  }

  load();

  return {
    refresh() { st.showAllRows = false; return load(); },
    destroy() { st.destroyed = true; root.textContent = ""; },
    state() { return { mode: st.mode, mark: st.mark, parsed: st.parsed, source: st.source }; },
  };
}

function nowIso(o) {
  const t = o && o.now != null ? new Date(o.now) : new Date();
  return t.toISOString().slice(0, 19) + "Z";
}

function banner(glyph, title, text) {
  const b = el("div", "tl-banner");
  b.appendChild(el("span", "tl-banner-g", glyph));
  const d = el("div");
  d.appendChild(el("div", "tl-banner-t", title));
  if (text) d.appendChild(el("div", "tl-banner-x", text));
  b.appendChild(d);
  return b;
}

/* One row.  Every mark carries: verb glyph + verb label (status channel, form only)
 * and category glyph + category label + category hue (categorical channel).  Colour
 * is never alone on either channel. */
function rowNode(r, kinds, st, repaint) {
  if (r.type === "bad") return badNode(r.e);
  if (r.type === "bucket") return bucketNode(r, st, repaint);

  const e = r.e, v = r.v;
  const id = e.event === "spawn" ? e.name : e.id;
  let meta = (id && kinds.get(id)) || {};
  const k = kindOf({ kind: meta.kind });

  const cls = "tl-row tl-" + r.type +
    (v.loud ? " loud" : "") + (v.warn ? " warn" : "") + (v.dim ? " dim" : "") +
    (r.inBucket ? " in-bucket" : "");
  const n = el("div", cls);
  n.appendChild(el("span", "tl-t", shortTs(e.ts)));
  n.appendChild(el("span", "tl-seat", e.seat || "?"));

  const vg = el("span", "tl-verb");
  vg.appendChild(el("span", "tl-vg", v.g));
  vg.appendChild(el("span", "tl-vl", v.label));
  n.appendChild(vg);

  const kd = el("span", "tl-kind");
  kd.style.color = k.hex;
  kd.appendChild(el("span", "tl-kg", k.glyph));
  kd.appendChild(el("span", "tl-kl", k.label));
  kd.title = meta.kind ? ("kind `" + meta.kind + "`, carried from this item's `file` event")
                       : "no kind on the ledger for this item";
  n.appendChild(kd);

  if (id) {
    const idn = el("span", "tl-id", id);
    if (meta.title) idn.title = meta.title;
    n.appendChild(idn);
  }
  /* Many migrated items were filed with their slug AS their title. Printing it twice
   * on one row is noise, so the detail column drops a title identical to the id. */
  if (meta.title && id && meta.title === id) meta = Object.assign({}, meta, { title: null });

  n.appendChild(detail(e, meta, st, repaint));
  n.appendChild(el("span", "tl-line", "L" + e.line));
  return n;
}

/* What each verb actually needs to show.  `close` without its sha, or `block`
 * without its reason, is a row that answers nothing. */
function detail(e, meta, st, repaint) {
  const d = el("span", "tl-detail");
  const push = (cls, txt, key) => {
    if (txt == null || txt === "") return;
    const c = clip(txt, 150);
    const s = el("span", cls, st.expandedText.has(key) && c.full ? c.full : c.text);
    if (c.full) {
      s.className += " tl-clip";
      s.title = "click to expand";
      s.onclick = () => { st.expandedText.has(key) ? st.expandedText.delete(key)
                                                   : st.expandedText.add(key); repaint(); };
    }
    d.appendChild(s);
  };
  switch (e.event) {
    case "close":
      d.appendChild(el("span", "tl-sha", e.sha || "(no sha)"));
      push("tl-txt", meta.title, e.line + "t");
      break;
    case "block":
    case "unblock":
    case "drop":
      push("tl-reason", e.reason, e.line + "r");
      if (e.on) d.appendChild(el("span", "tl-on", "on " + e.on));
      break;
    case "supersede":
      d.appendChild(el("span", "tl-by", "by " + (e.by || "?")));
      push("tl-reason", e.reason, e.line + "r");
      break;
    case "finding":
      d.appendChild(el("span", "tl-sev", String(e.severity || "?").toUpperCase()));
      d.appendChild(el("span", "tl-fname", e.name || "?"));
      push("tl-txt", (e.type ? e.type + " · " : "") + "from " + (e.from || "?"), e.line + "f");
      break;
    case "spawn":
      d.appendChild(el("span", "tl-from", (e.from || "?") + "  →"));
      push("tl-txt", e.title || e.name, e.line + "s");
      if (e.this_deployment) d.appendChild(el("span", "tl-flag", "this deployment"));
      break;
    case "verify":
      d.appendChild(el("span", "tl-res " + (String(e.result).toLowerCase() === "pass" ? "pass" : "fail"),
                       String(e.result || "?").toUpperCase()));
      d.appendChild(el("span", "tl-cfg", e.config || "?"));
      push("tl-txt", e.evidence, e.line + "e");
      break;
    case "retarget":
      d.appendChild(el("span", "tl-by", (e.from || "?") + " → " + (e.to || "?")));
      push("tl-reason", e.reason, e.line + "r");
      break;
    case "reassign":
      d.appendChild(el("span", "tl-by", "→ " + (e.to || "?")));
      push("tl-reason", e.reason, e.line + "r");
      break;
    case "game":
    case "bridge":
    case "seat":
      d.appendChild(el("span", "tl-state", String(e.state || "?").toUpperCase()));
      push("tl-reason", e.reason, e.line + "r");
      break;
    case "admin":
      push("tl-reason", e.reason, e.line + "r");
      if (e.patch) push("tl-txt", "patch: " + JSON.stringify(e.patch), e.line + "p");
      break;
    case "note":
      push("tl-txt", e.text, e.line + "n");
      break;
    case "file":
      push("tl-txt", e.title, e.line + "t");
      if (e.for) d.appendChild(el("span", "tl-for", "for " + e.for));
      break;
    default:
      push("tl-txt", e.title || e.text || e.reason, e.line + "d");
  }
  return d;
}

/* A collapsed bucket.  ⚠️ Collapsed, NOT omitted: the count is on the face of the
 * row, the members are one click away in file order, and the footer's identity
 * accounts for every one of them. */
function bucketNode(r, st, repaint) {
  const open = st.expanded.has(r.key);
  const n = el("button", "tl-row tl-bucket" + (open ? " open" : ""));
  n.type = "button";
  n.setAttribute("aria-expanded", String(open));
  n.onclick = () => { open ? st.expanded.delete(r.key) : st.expanded.add(r.key); repaint(); };
  n.appendChild(el("span", "tl-t", shortTs(r.ts)));
  n.appendChild(el("span", "tl-seat", r.seat || "?"));
  const vg = el("span", "tl-verb");
  vg.appendChild(el("span", "tl-vg", open ? "▾" : "▸"));
  vg.appendChild(el("span", "tl-vl", r.v.label));
  n.appendChild(vg);
  n.appendChild(el("span", "tl-bcount", "× " + r.members.length));
  n.appendChild(el("span", "tl-bhint",
    "collapsed bookkeeping — " + r.members.length + " `" + r.verb + "` events in this minute" +
    (open ? "" : " · click to expand, nothing is hidden from the totals")));
  return n;
}

/* A line that is not an event.  Rendered where it sits, with its raw bytes, because
 * the whole reason to notice a torn line is that somebody sees it. */
function badNode(e) {
  const n = el("div", "tl-row tl-bad");
  n.appendChild(el("span", "tl-t", shortTs(e.ts)));
  n.appendChild(el("span", "tl-seat", e.seat || "—"));
  const vg = el("span", "tl-verb");
  vg.appendChild(el("span", "tl-vg", "⤬"));
  vg.appendChild(el("span", "tl-vl", String(e.bad).toUpperCase() + " LINE"));
  n.appendChild(vg);
  n.appendChild(el("span", "tl-why", e.why || ""));
  const raw = el("code", "tl-raw", e.raw === "" ? "(empty line)" : clip(e.raw, 240).text);
  n.appendChild(raw);
  n.appendChild(el("span", "tl-line", "L" + e.line));
  return n;
}

export default { render, parseLedger, sessionize, chooseWindow, buildRows, kindIndex, VERB, PROBE };
