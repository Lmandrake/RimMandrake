/* deck.js — DECK, the default view: the one screen that answers "what is
 * happening". Vanilla ES module, no build step, no framework, no CDN.
 *
 *     import { render } from "./deck.js";
 *     render(document.getElementById("view"), await (await fetch("/board")).json());
 *
 * It shows, in this order, because that is the order the questions get asked:
 *   1. GAME STATE, from all THREE sources at once — and the disagreement, which
 *      is the interesting case and must never be resolved by picking one.
 *   2. BRIDGE HOLDER — who owns the live game right now.
 *   3. OWNER-QUESTION DEPTH — the only number on the board the owner alone can move.
 *   4. FOUR SEAT LANES (+ OWNER): doing / ready / blocked-and-on-what, or idle
 *      WITH ITS REASON. `no-ready-work` and `context-exhausted` are different
 *      states and are never drawn the same.
 *   5. BLOCKED items, with what each is blocked on.
 *   6. REPLAY ERRORS — refusals already sitting in an append-only file that
 *      nobody can remove. Surfaced, never swallowed.
 *
 * ⛔ COLOUR IS NEVER THE ONLY ENCODING. Every item mark carries its glyph AND
 * its label, from palette.js. Read the comment at the top of that file: two of
 * our own categories are ΔE 7.1 apart to a reader with ordinary sight.
 *
 * ⚠️ STATUS IS A SEPARATE CHANNEL from category, and borrows no categorical
 * hue: blocked is a ring plus ⚠, doing is full opacity, done dims to 45%,
 * idle is a dashed outline. All of that lives in the `.st-*` classes.
 */
import { mark, kindOf, statusStyle, SURFACE } from "./palette.js";

/* ---------------------------------------------------------------------------
 * The projection carries NO per-item `kind` — `rimflow render` drops it, and
 * the ledger's kind is a property of the queue FILE an item was filed in
 * (importer.py SOURCES). So we recover it from the owning seat rather than
 * guessing per item, and an unknown seat falls through kindOf() to the neutral
 * "unclassified" rather than borrowing a real category's colour.
 * ------------------------------------------------------------------------- */
const SEAT_KIND = {
  DECIDE: "decision", // DECIDE.md      -> decision -> doc  ▤
  BUILD: "task",      // BUILD.md       -> task     -> code ⌘
  CHECK: "check",     // CHECK.md       -> check    -> test ◈
  OWNER: "question",  // HUMAN.md       -> question -> doc  ▤
  REP: "infra",       // no queue file of its own
};
const SEATS = ["DECIDE", "BUILD", "CHECK", "REP", "OWNER"];
const SEAT_NOTE = {
  DECIDE: "design + rulings",
  BUILD: "mods, defs, C#",
  CHECK: "verification",
  REP: "tooling + reporting",
  OWNER: "the human",
};

/* Idle is not one state. These are the reasons POLICY.md defines, and each gets
 * its own weight — a seat that ran out of context needs a fresh window, a seat
 * with no ready work needs items filed. Confusing them costs a session. */
const IDLE_REASON = {
  "context-exhausted": { pill: "warn", say: "context exhausted — needs a fresh window" },
  "no-ready-work": { pill: "quiet", say: "no ready work — nothing is filed it can start" },
  "awaiting-game-state": { pill: "warn", say: "waiting on a game state" },
};

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* --------------------------------------------------------------------------
 * The mark. Glyph + id + category LABEL, with status applied as its own
 * channel on top. Never call this without a status — an unmarked chip claims
 * a state it has not got.
 * ------------------------------------------------------------------------ */
function itemMark(id, seat, status) {
  const m = mark({ kind: SEAT_KIND[seat], ...status });
  const st = statusStyle({ ...status });
  const cls = ["mk"];
  if (status.blocked) cls.push("st-blocked");
  else if (status.state === "doing") cls.push("st-doing");
  else if (status.state === "done") cls.push("st-done");
  else if (status.state === "idle") cls.push("st-idle");
  if (st.strike) cls.push("st-gone");
  const title = `${id} — ${m.label}` +
    (status.blocked ? " — BLOCKED" : status.state ? ` — ${status.state}` : "");
  return `<span class="${cls.join(" ")}" style="--c:${m.hex};opacity:${st.opacity}"` +
    ` title="${esc(title)}">` +
    `<span class="g">${m.glyph}</span>` +
    `<span class="id">${esc(id)}</span>` +
    `<span class="kl">${esc(m.label)}</span>` +
    (st.warn ? `<span class="w">${st.warn}</span>` : "") +
    `</span>`;
}

const cell = (head, body) =>
  `<div class="cell"><div class="h">${head}</div><div class="v">${body}</div></div>`;
const none = (why) => `<span class="none">${esc(why)}</span>`;

/* --------------------------------------------------------------------------
 * GAME STATE — three sources, and the disagreement is the point.
 *
 *   game.state      what a SEAT wrote into status/game.json
 *   game.ledger     what the OWNER last announced through the ledger
 *   game.load_done  whether a load actually FINISHED, read off Player.log
 *
 * `/board` (the raw projection) carries `game` as a bare string — the ledger
 * announcement only. `/data` carries it as an object holding all three. Accept
 * either, and where a source is simply absent say ABSENT, never assume DOWN.
 * ------------------------------------------------------------------------ */
function readGame(board) {
  const raw = board.game;
  const g = (raw && typeof raw === "object") ? raw : { ledger: raw || null };
  return {
    seat: g.state == null ? null : String(g.state).toUpperCase(),
    ledger: g.ledger == null ? null : String(g.ledger).toUpperCase(),
    load: g.load_done === true ? true : g.load_done === false ? false : null,
    at: g.at || null,
    bridge: g.bridge != null ? g.bridge : (board.bridge_holder != null ? board.bridge_holder : null),
  };
}

/* UP-ness, coarsely, so two differently-worded claims can be compared at all.
 * PLAYABLE and UP are the same answer to "is the game up"; LOADING is not. */
const upness = (s) => s == null ? null
  : /^(UP|PLAYABLE|RUNNING)$/.test(s) ? "up"
    : /^LOADING$/.test(s) ? "loading"
      : /^DOWN$/.test(s) ? "down" : "other";

function gameConflicts(g) {
  const out = [];
  const a = upness(g.seat), b = upness(g.ledger);
  if (a && b && a !== b) {
    out.push(`the seat wrote <b>${esc(g.seat)}</b> but the owner last announced ` +
      `<b>${esc(g.ledger)}</b> — one of the two is stale, and the board will not guess which`);
  }
  if (g.load === true && (a === "loading" || b === "loading")) {
    out.push("a source still says <b>LOADING</b>, but the log says this launch " +
      "finished loading — the LOADING stamp is out of date");
  }
  if (g.load === false && (a === "up" || b === "up")) {
    out.push("a source says the game is <b>UP</b>, but no finished load appears in " +
      "the log for this launch — a load that aborted still leaves the bridge answering");
  }
  return out;
}

function gamePanel(board) {
  const g = readGame(board);
  const row = (dt, val, from) =>
    `<dt>${dt}</dt><dd>${val == null ? '<span class="none">absent</span>' : esc(val)}` +
    `<span class="from">${from}</span></dd>`;
  const conflicts = gameConflicts(g);
  return `<div class="panel"><p class="ttl">GAME STATE — THREE SOURCES</p>
    <dl class="src">
      ${row("SEAT WROTE", g.seat, "status/game.json")}
      ${row("OWNER ANNOUNCED", g.ledger, "ledger — the game verb")}
      ${row("LOAD FINISHED", g.load == null ? null : (g.load ? "YES" : "NO"), "Player.log, this launch")}
    </dl>
    ${conflicts.length
      ? `<div class="conflict"><b>⚠ SOURCES DISAGREE</b><ul>` +
        conflicts.map((c) => `<li>${c}</li>`).join("") + `</ul></div>`
      : `<p class="agree">${g.seat == null && g.ledger == null && g.load == null
        ? "no source has reported — this is not the same fact as DOWN"
        : "the sources that reported agree"}</p>`}
  </div>`;
}

function bridgePanel(board) {
  const g = readGame(board);
  const held = g.bridge != null && g.bridge !== "";
  return `<div class="panel"><p class="ttl">BRIDGE HOLDER</p>
    <div class="big ${held ? "" : "zero"}">${held ? esc(g.bridge) : "FREE"}</div>
    <p class="sub">${held
      ? "holds the live game. Nobody else drives RimWorld until it is released."
      : "no seat has taken the bridge."}</p></div>`;
}

/* --------------------------------------------------------------------------
 * OWNER-QUESTION DEPTH — the only number here the owner alone can move.
 *
 * Two components, kept apart rather than added into one flattering total:
 *   items filed TO the owner (HUMAN.md, kind: question), and
 *   items owned by a SEAT that are blocked on an owner decision.
 * Adding them would double-count anything filed to OWNER *and* blocked.
 * ------------------------------------------------------------------------ */
function ownerPanel(board) {
  const seats = board.seats || {};
  const owner = seats.OWNER || {};
  const filed = owner.open != null ? owner.open : (owner.counts
    ? (owner.counts.ready || 0) + (owner.counts.doing || 0) + (owner.counts.proposed || 0)
    : 0);
  const blocked = (board.blocked || []).filter(
    (b) => b.owner !== "OWNER" &&
      (b.needs === "owner" || /\b(owner|human)\b/i.test(b.reason || "")));
  const onHuman = (board.blockers || {}).on_human;
  return `<div class="panel"><p class="ttl">WAITING ON THE OWNER</p>
    <div class="big ${filed ? "attn" : "zero"}">${filed}</div>
    <p class="sub">question${filed === 1 ? "" : "s"} filed to OWNER and still open.
      ${blocked.length
      ? `<br><b>${blocked.length}</b> further item${blocked.length === 1 ? " is" : "s are"}
         blocked on an owner decision: ` +
      blocked.map((b) => itemMark(b.id, b.owner, { blocked: true, state: b.state })).join(" ")
      : "No seat item is blocked on an owner decision."}
      ${onHuman != null && onHuman !== blocked.length
      ? `<br><span class="none">the ledger counts ${onHuman} blocked on a human,
           this view classes ${blocked.length}</span>` : ""}</p></div>`;
}

/* --------------------------------------------------------------------------
 * The seat lanes.
 * ------------------------------------------------------------------------ */
const MIX = [
  ["doing", "var(--cyan)"],
  ["ready", "#3e4a52"],
  ["done", "#2f4f3c"],
  ["dropped", "#2b2a27"],
  ["superseded", "#2b2a27"],
];

function mixStrip(counts) {
  const c = counts || {};
  const tot = MIX.reduce((a, [k]) => a + (c[k] || 0), 0);
  const bar = tot
    ? MIX.filter(([k]) => c[k]).map(([k, col]) =>
      `<i style="width:${(100 * c[k] / tot).toFixed(2)}%;background:${col}" title="${c[k]} ${k}"></i>`).join("")
    : "";
  // The numbers are printed regardless of the bar: a fixed-order strip may use
  // colour alone, but a strip nobody can read a value off is decoration.
  const nums = MIX.filter(([k]) => c[k])
    .map(([k]) => `<b>${c[k]}</b> ${k}`).join(' <span class="sep">·</span> ');
  return `<div class="cell mix"><div class="h">MIX</div>
    <div class="bar">${bar}</div>
    <div class="n">${nums || "<span class=\"none\">no items</span>"}</div></div>`;
}

/* What the seat is: what the LEDGER says it has started, reconciled against
 * what the seat last ANNOUNCED about itself. When those disagree that IS the
 * finding — a seat announcing busy with nothing started is exactly the failure
 * the old board could not see. */
function seatPill(s, blockedHere) {
  const says = s.says || {};
  const said = says.state ? String(says.state).toLowerCase() : null;
  const doing = (s.doing || []).length;
  const total = Object.values(s.counts || {}).reduce((a, n) => a + (n || 0), 0);

  if (!total && !said) {
    return { pill: `<span class="pill gone">NO ITEMS</span>`,
      why: `<span class="why">nothing is filed for this seat</span>` };
  }
  if (said === "idle") {
    const r = String(says.reason || "").toLowerCase();
    const known = IDLE_REASON[r];
    return {
      pill: `<span class="pill ${known ? known.pill : "quiet"}">${known && known.pill === "warn" ? "⚠ " : ""}IDLE</span>`,
      why: `<span class="why">${known ? known.say : (says.reason
        ? `idle — <b>${esc(says.reason)}</b>`
        : "idle — <b>no reason given</b>, which is itself a defect")}` +
        (says.item ? ` <span class="none">(last: ${esc(says.item)})</span>` : "") + `</span>` +
        (doing ? `<span class="disagree">⚠ but ${doing} item${doing === 1 ? " is" : "s are"}
           still marked doing in the ledger</span>` : ""),
    };
  }
  if (blockedHere) {
    return { pill: `<span class="pill warn">⚠ BLOCKED</span>`,
      why: `<span class="why">${blockedHere} open item${blockedHere === 1 ? "" : "s"} blocked</span>` };
  }
  if (doing) {
    return { pill: `<span class="pill active">DOING</span>`,
      why: says.state && said !== "working" && said !== "doing"
        ? `<span class="disagree">⚠ seat announced <b>${esc(says.state)}</b></span>` : "" };
  }
  if (said) {
    return { pill: `<span class="pill">${esc(String(says.state).toUpperCase())}</span>`,
      why: says.reason ? `<span class="why">${esc(says.reason)}</span>` : "" };
  }
  // Nothing started, nothing announced. That is idle whether or not a seat
  // admitted it, and the reason is unknown rather than "no ready work".
  const ready = (s.counts || {}).ready || 0;
  return {
    pill: `<span class="pill quiet">IDLE</span>`,
    why: `<span class="why">${ready
      ? `<b>never announced a state</b> — ${ready} item${ready === 1 ? " is" : "s are"} ready and unstarted`
      : "<b>never announced a state</b>, and nothing is ready"}</span>`,
  };
}

function lane(seat, board) {
  const s = (board.seats || {})[seat] || {};
  const blocks = (board.blocked || []).filter((b) => b.owner === seat);
  const p = seatPill(s, blocks.length);
  const doing = (s.doing || []).map((id) => itemMark(id, seat, { state: "doing" }));
  const nextId = s.next;
  const ready = (s.counts || {}).ready || 0;

  const nextCell = nextId
    ? itemMark(nextId, seat, { state: "ready" }) +
      (s.offered > 1 ? ` <span class="none">+${s.offered - 1} more offered</span>` : "")
    : none(ready ? `${ready} ready, none offered — every one is gated` : "nothing ready");

  const blockedCell = blocks.length
    ? blocks.map((b) => itemMark(b.id, seat, { blocked: true, state: b.state })).join(" ")
    : none("none");

  return `<div class="lane">
    <div class="nm">${seat}<small>${SEAT_NOTE[seat] || ""}</small></div>
    <div class="cell">${p.pill}${p.why}</div>
    ${cell("DOING NOW", doing.length ? doing.join(" ") : none("nothing started"))}
    ${cell("NEXT UP", nextCell)}
    ${mixStrip(s.counts)}
    ${blocks.length ? `<div class="cell" style="grid-column:3/-1">
        <div class="h">BLOCKED ON</div>
        <div class="v">${blockedCell}</div></div>` : ""}
  </div>`;
}

/* --------------------------------------------------------------------------
 * Blocked detail and replay errors.
 * ------------------------------------------------------------------------ */
function blockedPanel(board) {
  const bs = board.blocked || [];
  if (!bs.length) return `<div class="panel"><p class="ttl">BLOCKED</p>
    <p class="sub">Nothing open is blocked.</p></div>`;
  return `<div class="panel"><p class="ttl">BLOCKED — ${bs.length}</p>` +
    bs.map((b) => `<div class="blk">
      ${itemMark(b.id, b.owner, { blocked: true, state: b.state })}
      <div class="r"><b>${esc(b.owner || "?")}</b> · ${esc(b.reason || "unexplained")}
        ${b.on ? ` · on <b>${esc(b.on)}</b>` : ""}
        ${b.needs ? ` · needs <b>${esc(b.needs)}</b>` : ""}
        ${b.row ? ` · row ${esc(b.row)}` : ""}</div></div>`).join("") + `</div>`;
}

function errorsPanel(board) {
  const es = board.errors || [];
  if (!es.length) return "";
  return `<div class="panel" style="border-color:var(--amber)">
    <p class="ttl" style="color:var(--amber)">⚠ REPLAY REFUSED ${es.length} EVENT${es.length === 1 ? "" : "S"}</p>
    <p class="sub">These are already in <b>ledger/events.jsonl</b>, which is append-only.
      They cannot be deleted — only corrected by a later event.</p>` +
    es.map((e) => `<div class="err">
      <span class="ix">#${esc(e.index)}</span> ${esc(e.message)}
      <code>${esc(typeof e.event === "string" ? e.event : JSON.stringify(e.event))}</code>
    </div>`).join("") + `</div>`;
}

/* ------------------------------------------------------------------------ */
function unavailable(why) {
  return `<div class="unavail"><b>BOARD UNAVAILABLE</b>
    <p>${esc(why || "board.json could not be built, and no reason was given.")}</p>
    <p class="hint">Zeros are not being shown, because zeros look like an answer.
      Nothing below this line is known — not the seat states, not the game state,
      not the owner depth. Regenerate with
      <code>python3 src/RimMandrake/rimflow/render.py</code> and reload.</p></div>`;
}

function age(board) {
  const t = Date.parse(board.as_of || "");
  if (!t) return "";
  const m = (Date.now() - t) / 60000;
  const s = m < 1 ? "just now" : m < 60 ? Math.floor(m) + "m ago" : (m / 60).toFixed(1) + "h ago";
  return `<span class="age${m > 5 ? " stale" : ""}">ledger as of ${esc(board.as_of)} — ${s}` +
    `${m > 5 ? " · STALE" : ""}</span>`;
}

/* CSS is fetched once, from the same directory this module was served from, so
 * the host page needs to know nothing about the view it mounted. */
function ensureCss() {
  const href = new URL("./deck.css", import.meta.url).href;
  if (document.querySelector(`link[href="${href}"]`)) return;
  const l = document.createElement("link");
  l.rel = "stylesheet";
  l.href = href;
  document.head.appendChild(l);
}

/**
 * Draw the deck into `root`.
 * @param {HTMLElement} root
 * @param {object} board  the `/board` projection, or the `/data` snapshot.
 */
export function render(root, board) {
  if (!root) return;
  ensureCss();
  root.classList.add("deck");
  root.style.background = SURFACE;

  // ⚠️ An absent or unbuildable board must not render as zeros. Both spellings
  // are accepted: `/board` reports `unavailable`, `/data` reports
  // `board_unavailable` — and a null board is the same fact as either.
  if (!board || board.unavailable || board.board_unavailable) {
    root.innerHTML = `<div class="dk-head"><h2>DECK</h2></div>` +
      unavailable(board && (board.why || board.board_why));
    return;
  }

  const errs = errorsPanel(board);
  root.innerHTML = `
    <div class="dk-head">
      <h2>DECK</h2>
      ${age(board)}
      <span class="age">${board.items != null ? board.items + " items · " : ""}${board.events != null ? board.events + " events · " : ""}target ${esc(board.target || "?")}</span>
    </div>
    <div class="row top">
      ${gamePanel(board)}
      ${bridgePanel(board)}
      ${ownerPanel(board)}
    </div>
    <div class="row"><div class="panel">
      <p class="ttl">SEATS — DOING · NEXT · BLOCKED · IDLE-WITH-REASON</p>
      ${SEATS.map((s) => lane(s, board)).join("")}
    </div></div>
    <div class="row">${blockedPanel(board)}</div>
    ${errs ? `<div class="row">${errs}</div>` : ""}
    <p class="foot">Category is hue + glyph + label; status is ring / opacity /
      dashed outline. Colour is never the only encoding — see palette.js.</p>`;
}

/* Convenience for a host page that would rather not own the fetch. Polling is
 * the caller's business: this page is left open all day and nothing here moves
 * on its own. */
export async function load(root, url) {
  let board = null;
  try {
    const r = await fetch(url || "/board", { cache: "no-store" });
    board = await r.json();
  } catch (e) {
    board = { unavailable: true, why: "could not fetch " + (url || "/board") + " — " + e };
  }
  render(root, board);
  return board;
}

export default { render, load, kindOf };
