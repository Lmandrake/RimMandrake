"""RimPulse morning brief + heartbeat (RIMPULSE_BRIEF_BUILD_MORNING_PAPER_PHONE; design
design/RimMandrake/rimpulse_redesign_2026-10-23.md §4A "The Morning Paper").

The owner's card choices (2026-10-24): a phone-sized morning brief plus a one-line heartbeat; overnight
outcomes in words, by goal; each line checked by a second reader against the ledger; blocking first, then
oldest promised; a Claude plan usage line only from a MEASURED source; coverage reads "unknown" when a
collector is down; links to cards and sheets, no answer buttons; overnight push only for emergency question
cards (push stays off here: PHONE_PUSH_ENABLED in pulse.py).

Three parts, each a pure function over what it is handed:
  compose(snap, events, since, now)  -> a brief: sections of lines, every line carrying the CLAIM it makes
                                        (an item moved to a state at an event, an ask is open, a look exists)
  judge(brief, events, snap)         -> the same brief with every line checked. It re-derives each claim from
                                        its own rimflow replay (model.replay with observe), never from the
                                        composer's numbers. A line that fails is withheld from the page and
                                        counted, so nothing reaches him that the ledger does not say.
  heartbeat(snap, brief, now)        -> one live line. Red only for: monitor down, a missed brief, a card
                                        blocking a seat, no seat working for 30 min (§4A).
`pulse.py brief` composes, then runs the judge in a separate process (`brief.py judge PATH`) and stores
both under the digests folder as brief_<date>_<HHMM>.json. The daemon serves /brief, /heartbeat and
/item/<ID> on 127.0.0.1:8765, and the same read-only pages on this machine's tailnet address (port
RM_BRIEF_PORT, default 8791) for his phone, gated by `tailscale whois` against an allowlist.
"""
from __future__ import annotations

import calendar
import html
import json
import os
import re
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pulse_core as pc  # noqa: E402

BRIEF_PORT = int(os.environ.get("RM_BRIEF_PORT", "8791"))
BRIEF_MAX_AGE = 14 * 3600      # rm-pulse-brief.timer: 05:45 and 17:15; older than this one was missed
SNAP_STALE = 300               # the monitor writes pulse_now.json every 5 s; 5 min silent = down
RUN_STOPPED = 1800             # §4A: no seat working for 30 min
WINDOW_CAP = 36 * 3600         # a brief never reaches back further than this
PER_GOAL = 2                   # outcome lines named per goal; the goal's count line covers the rest
MAX_GOALS = 5                  # a phone screen: the biggest goals by name, the rest in one line
STATE_WORD = {"done": "closed", "validated": "checked", "built": "built, checks owed"}
STATE_RANK = ("done", "validated", "built")
SEATS = ("BENCH", "FOUNDRY")
JUDGE = "brief.py judge (separate process; its own rimflow replay)"

# which collector each section stands on: when it is down the section says "unknown", never "nothing"
SECTION_SOURCES = {"word": ("ledger",), "open": ("hands", "sheets"), "overnight": ("ledger",),
                   "decided": ("ledger",), "spend": ("tokens",), "next": ("sessions",)}
TITLES = {"word": "Needs your word", "open": "Open these", "overnight": "Overnight, in words",
          "decided": "Decided for you", "spend": "Spend", "next": "Next", "coverage": "Coverage"}
ORDER = ("word", "open", "overnight", "decided", "spend", "next", "coverage")

# A look's review packet (owner card 2026-10-25, "Plus evidence and doubts"): the artifact ships with a
# recommendation, the alternatives with their reasons, the evidence (what was measured) and the doubts (what
# was not, where the agent is unsure). Read from `## ` sections of a markdown: the hand's --packet file, or
# an item look's items/<ID>.md. A look short of any part is listed as "packet incomplete", never a bare link.
PACKET_PARTS = ("recommendation", "alternatives", "evidence", "doubts")
PACKET_HEADS = (("recommend", "recommendation"), ("alternative", "alternatives"), ("option", "alternatives"),
                ("evidence", "evidence"), ("measured", "evidence"), ("doubt", "doubts"), ("unsure", "doubts"),
                ("not measured", "doubts"), ("unknown", "doubts"))


def _model():
    return pc._model()


def _tsec(ev: dict) -> float:
    if ev.get("tsn"):
        return int(ev["tsn"]) / 1e9
    try:
        return float(calendar.timegm(time.strptime(str(ev.get("ts", "")), "%Y-%m-%dT%H:%M:%SZ")))
    except ValueError:
        return 0.0


def _short(s: str, n: int = 110) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def goal_of(iid: str) -> str:
    """The goal an item serves, in words: its id's SUBJECT (ids are SUBJECT_INTENT_TWIST)."""
    head = iid.split("_")[0]
    return {"FLOWWORKS": "FlowWorks", "RIMPULSE": "RimPulse", "STEVEDESKTOP": "SteveDesktop",
            "TESTQ": "Test queue", "GSS": "GSS"}.get(head, head.capitalize())


def transitions(events: list[dict], since: float, now: float) -> tuple[dict, list[dict]]:
    """(world, moves): every state change an event made inside [since, now], from rimflow's own fold."""
    model, prev, moves = _model(), {}, []

    def obs(ev, world, ok):
        iid = ev.get("id")
        it = world.items.get(iid) if iid else None
        if it is None:
            return
        before, prev[iid] = prev.get(iid), it.state
        t = _tsec(ev)
        if ok and before is not None and before != it.state and since <= t <= now:
            moves.append({"id": iid, "from": before, "to": it.state, "event": ev.get("event"),
                          "tsn": ev.get("tsn"), "t": t, "seat": ev.get("seat")})
    world = model.replay(events, observe=obs)
    return world, moves


def packet_path(row: dict) -> str | None:
    """Where a look row's packet lives: the hand's --packet file, else an item look's own items/<ID>.md."""
    if row.get("packet"):
        return str(row["packet"])
    key = str(row.get("key") or "")
    if key.startswith("needs:"):
        for c in pc.CLONES:
            f = c / "infrastructure" / "state" / "items" / f"{key[6:]}.md"
            if f.is_file():
                return str(f)
    return None


def read_packet(path: str | None) -> tuple[dict, list[str]]:
    """({part: text}, missing parts). A part counts only with words under its heading."""
    if not path:
        return {}, list(PACKET_PARTS)
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}, list(PACKET_PARTS)
    parts: dict[str, str] = {}
    cur = None
    for ln in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m:
            h = m.group(1).lower()
            cur = next((part for pre, part in PACKET_HEADS if h.startswith(pre)), None)
            continue
        if cur and ln.strip():
            parts[cur] = (parts.get(cur, "") + " " + ln.strip()).strip()
    return parts, [k for k in PACKET_PARTS if not parts.get(k)]


def _source_down(snap: dict, sec: str) -> list[str]:
    src = snap.get("sources") or {}
    return [s for s in SECTION_SOURCES.get(sec, ()) if not (src.get(s) or {}).get("ok")]


def compose(snap: dict, events: list[dict], since: float, now: float) -> dict:
    world, moves = transitions(events, since, now)
    secs: dict[str, list[dict]] = {k: [] for k in ORDER}
    notes: dict[str, str] = {}
    rows = [r for r in (snap.get("rows") or []) if not r.get("agent")]

    # NEEDS YOUR WORD: his asks and live cards, blocking first, then oldest promised
    blocks = Counter(i.blocked_on for i in world.items.values() if i.open and i.blocked and i.blocked_on)
    asks = []
    for r in rows:
        if r["kind"] not in ("review", "provide", "amber"):
            continue
        iid = r["key"][6:] if str(r.get("key", "")).startswith("needs:") else None
        it = world.items.get(iid) if iid else None
        title = (it.title if it else None) or r.get("text") or ""
        if iid and title.startswith(iid):
            title = title[len(iid):].lstrip(" —-")
        head = (r.get("title") or iid or "").capitalize()
        asks.append({"sec": "word", "text": _short(f"{head}: {title}" if head else title, 150),
                     "meta": {"since": r.get("since"), "blocks": blocks.get(iid, 0), "kind": r["kind"],
                              "who": r.get("who")},
                     "link": f"/item/{iid}" if iid else (r.get("link") or {}).get("value"),
                     "claim": {"type": "ask", "id": iid} if iid else {"type": "card", "key": r["key"]}})
    asks.sort(key=lambda a: (-a["meta"]["blocks"], a["meta"]["since"] or now))
    secs["word"] = asks

    # OPEN THESE: pre-read looks
    for r in rows:
        if r["kind"] == "look":
            lk = r.get("link") or {}
            pp = packet_path(r)
            parts, missing = read_packet(pp)
            secs["open"].append({"sec": "open", "text": _short(r.get("title") or r.get("text"), 150),
                                 "meta": {"since": r.get("since")},
                                 "link": None if missing else lk.get("value"),   # no bare link without a packet
                                 "packet": {k: _short(v, 220) for k, v in parts.items()}, "missing": missing,
                                 "claim": {"type": "look", "key": r["key"], "packet": pp, "missing": missing}})

    # OVERNIGHT, IN WORDS: per goal one line of counts in the ledger's state words, then its first
    # outcomes (tasks before bugs, closed before checked before built); small goals fold into one line
    last = {}
    for m in moves:                      # where each item ended up inside the window
        last[m["id"]] = m
    by_goal: dict[str, list[dict]] = defaultdict(list)
    for iid, m in last.items():
        if m["to"] in STATE_WORD:
            by_goal[goal_of(iid)].append({"id": iid, "to": m["to"], "tsn": m["tsn"], "t": m["t"]})
    goals = sorted(by_goal.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for g, ms in goals[:MAX_GOALS]:
        ms.sort(key=lambda x: (world.items[x["id"]].kind != "task", STATE_RANK.index(x["to"]), -x["t"]))
        c = Counter(x["to"] for x in ms)
        secs["overnight"].append({"sec": "overnight", "goal": g, "head": True,
                                  "text": ", ".join(f"{c[s]} {STATE_WORD[s]}" for s in STATE_RANK if c.get(s)),
                                  "claim": {"type": "moved_many", "items": [{**x, "type": "moved"} for x in ms]}})
        for x in ms[:PER_GOAL]:
            it = world.items[x["id"]]
            word = STATE_WORD[x["to"]]
            if x["to"] == "validated" and it.outstanding:
                word = "checked, " + "/".join(it.owed_levels()) + " owed"
            secs["overnight"].append({"sec": "overnight", "goal": g, "text": _short(it.title or x["id"], 100),
                                      "state": word, "link": f"/item/{x['id']}",
                                      "claim": {"type": "moved", "id": x["id"], "to": x["to"], "tsn": x["tsn"]}})
    if len(goals) > MAX_GOALS:
        rest = [x for _, ms in goals[MAX_GOALS:] for x in ms]
        names = ", ".join(f"{g} {len(ms)}" for g, ms in goals[MAX_GOALS:MAX_GOALS + 8])
        secs["overnight"].append({"sec": "overnight", "goal": "Everything else", "head": True,
                                  "text": f"{len(rest)} across {len(goals) - MAX_GOALS} goals: {names}"
                                          + (", …" if len(goals) > MAX_GOALS + 8 else ""),
                                  "claim": {"type": "moved_many", "items": [{**x, "type": "moved"} for x in rest]}})

    # DECIDED FOR YOU: delegated calls (delegation_policy.md: `why` starts "delegated:")
    dele = [e for e in events if str(e.get("why") or "").lower().startswith("delegated:")
            and since <= _tsec(e) <= now]
    if dele:
        cls = Counter(_short(str(e["why"]).split(":", 1)[1].split(";")[0].split("(")[0], 40) for e in dele)
        secs["decided"].append({"sec": "decided",
                                "text": f"{len(dele)} delegated call{'s' if len(dele) != 1 else ''}: "
                                        + ", ".join(f"{k} {v}" for k, v in cls.most_common(4)),
                                "claim": {"type": "delegated", "tsns": [e.get("tsn") for e in dele]}})
    else:
        notes["decided"] = "no delegated calls in the ledger since the last brief"

    # SPEND: measured token burn; plan usage only from a measured source (none exists yet)
    burn = ((snap.get("charts") or {}).get("burn") or {})
    day = sum(v for _, v in burn.get("day") or [])
    if burn.get("day"):
        peak = max(v for _, v in burn["day"])
        part = "" if burn.get("complete") else " - partial, the reader is still catching up"
        secs["spend"].append({"sec": "spend", "text": f"Claude tokens, last 24 h: {_human(day)} (peak {_human(peak)}/h){part}",
                              "claim": {"type": "measure", "src": "tokens", "value": day}})
    secs["spend"].append({"sec": "spend", "text": "Claude plan window used / resets: unknown (no measured source yet)",
                          "claim": {"type": "unknown"}})

    # NEXT: what each seat is on, from the live session chips, item named by the ledger
    for c in snap.get("chips") or []:
        if c.get("seat") in SEATS:
            m = re.search(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+){1,7})\b", c.get("title") or "")
            iid = m.group(1) if m else None
            it = world.items.get(iid) if iid else None
            what = _short(it.title, 90) if it else ("idle" if c.get("state") != "run" else "working")
            secs["next"].append({"sec": "next", "text": f"{c['seat'].capitalize()}: {what}",
                                 "link": f"/item/{iid}" if it else None,
                                 "claim": {"type": "seat", "seat": c["seat"], "id": iid if it else None}})

    down = sorted(s for s, v in (snap.get("sources") or {}).items() if not (v or {}).get("ok"))
    if down:
        secs["coverage"].append({"sec": "coverage", "text": "collectors down, so these read unknown: " + ", ".join(down),
                                 "claim": {"type": "coverage", "down": down}})
    for sec in SECTION_SOURCES:
        d = _source_down(snap, sec)
        if d:
            secs[sec] = []
            notes[sec] = "unknown: the " + "/".join(d) + " collector is down"
    return {"v": 1, "at": now, "since": since, "snap_at": snap.get("collected_at"), "sections": secs,
            "notes": notes, "judged": False}


def _human(n: float) -> str:
    for d, u in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if n >= d:
            return f"{n / d:.1f}{u}".replace(".0", "")
    return str(int(n))


# ---------------------------------------------------------------- judge


def judge(brief: dict, events: list[dict], snap: dict) -> dict:
    """Check every line's claim against an independent replay of the ledger (and, for live rows, the
    monitor's snapshot). Marks each line `check` = "pass" or "fail: <why>"; never edits the words."""
    model = _model()
    tsn_state: dict = {}
    by_tsn = {e.get("tsn"): e for e in events if e.get("tsn")}

    def obs(ev, world, ok):
        iid = ev.get("id")
        if ok and iid and iid in world.items and ev.get("tsn"):
            tsn_state[ev["tsn"]] = (iid, world.items[iid].state)
    world = model.replay(events, observe=obs)
    owner_rows = {r.get("key"): r for r in snap.get("rows") or [] if not r.get("agent")}
    keys = set(owner_rows)

    def check(c: dict) -> str:
        t = c.get("type")
        if t == "ask":
            it = world.items.get(c.get("id"))
            if not it:
                return "fail: no such item in the ledger"
            if not it.open:
                return f"fail: item is {it.state}, not open"
            if it.needs != "owner":
                return f"fail: item needs {it.needs}, not owner"
            return "pass"
        if t in ("card", "look"):
            if c.get("key") not in keys:
                return "fail: no longer on the monitor"
            if t == "look":
                _, missing = read_packet(packet_path(owner_rows[c["key"]]))   # its own path + read, not the composer's
                if sorted(missing) != sorted(c.get("missing") or []):
                    return f"fail: packet is missing {missing or 'nothing'}, the line says {c.get('missing') or 'nothing'}"
            return "pass"
        if t == "moved":
            got = tsn_state.get(c.get("tsn"))
            if not got or got[0] != c.get("id"):
                return "fail: no ledger event for this item at that time"
            if got[1] != c.get("to"):
                return f"fail: that event left it {got[1]}, not {c.get('to')}"
            now_state = world.items[c["id"]].state
            if c.get("to") == "done" and now_state != "done":
                return f"fail: reopened since (now {now_state})"
            return "pass"
        if t == "moved_many":
            bad = [x["id"] for x in c.get("items") or [] if check({**x, "type": "moved"}) != "pass"]
            return "pass" if not bad else f"fail: {len(bad)} not borne out ({', '.join(bad[:3])})"
        if t == "delegated":
            ok = [by_tsn.get(n) for n in c.get("tsns") or []]
            return "pass" if ok and all(e and str(e.get("why", "")).lower().startswith("delegated:") for e in ok) \
                else "fail: a delegated event is missing"
        if t == "measure":
            src = (snap.get("sources") or {}).get(c.get("src")) or {}
            return "pass" if src.get("ok") else "fail: its collector is down"
        if t == "seat":
            if c.get("id") is None:
                return "pass"
            it = world.items.get(c["id"])
            return "pass" if it and it.open else "fail: item not open"
        if t in ("unknown", "coverage"):
            return "pass"
        return f"fail: unknown claim type {t!r}"

    for lines in brief["sections"].values():
        for ln in lines:
            ln["check"] = check(ln.get("claim") or {})
    brief["judged"] = True
    brief["judged_at"] = time.time()
    brief["judged_by"] = JUDGE
    brief["withheld"] = sum(1 for ls in brief["sections"].values() for ln in ls if ln["check"] != "pass")
    return brief


# ---------------------------------------------------------------- heartbeat


def latest_brief(folder: Path) -> tuple[Path | None, dict | None]:
    for p in sorted(folder.glob("brief_*.json"), reverse=True):
        try:
            b = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        if b.get("judged"):
            return p, b
    return None, None


def heartbeat(snap: dict | None, brief: dict | None, now: float) -> dict:
    """{text, red, why}: one line. Red only for §4A's reasons, each with the verb that clears it."""
    if not snap or now - (snap.get("collected_at") or 0) > SNAP_STALE:
        at = (snap or {}).get("collected_at")
        return {"red": True, "why": "monitor", "text": "monitor down" + (f" since {_hm(at)}" if at else "")
                + ": restart rm-pulse (systemctl --user restart rm-pulse) or WSL"}
    rows = [r for r in snap.get("rows") or [] if not r.get("agent")]
    for r in rows:
        if r["kind"] == "amber":
            return {"red": True, "why": "card", "text": f"a card blocks {r.get('who') or 'a seat'}: {_short(r.get('text'), 80)}"}
    chips = [c for c in snap.get("chips") or [] if c.get("seat") in SEATS]
    working = [c for c in chips if c.get("state") == "run"]
    if chips and not working:
        quiet = now - max((c.get("since") or now) for c in chips)
        if quiet >= RUN_STOPPED:
            return {"red": True, "why": "stopped", "text": f"run stopped: no seat working for {int(quiet // 60)} min"}
    if not brief or now - (brief.get("at") or 0) > BRIEF_MAX_AGE:
        return {"red": True, "why": "brief", "text": "brief missed" + (f" (last {_hm(brief['at'])})" if brief else "")
                + ": run pulse.py brief"}
    ask = sum(1 for r in rows if r["kind"] in ("review", "provide"))
    look = sum(1 for r in rows if r["kind"] == "look")
    seats = " · ".join(f"{c['seat'].lower()} {'working' if c.get('state') == 'run' else c.get('state')}"
                       + (f" ({c['agents']} agents)" if c.get("agents") else "") for c in chips)
    need = []
    if ask:
        need.append(f"{ask} need{'s' if ask == 1 else ''} your word")
    if look:
        need.append(f"{look} to open")
    return {"red": False, "why": None,
            "text": "● running · " + (seats or "no seats seen") + " · " + (", ".join(need) or "nothing needs you")}


def _hm(t: float | None) -> str:
    return time.strftime("%H:%M", time.localtime(t)) if t else "?"


def _ago(t: float | None, now: float) -> str:
    if not t:
        return "?"
    s = max(0, now - t)
    return f"{int(s // 60)} min" if s < 5400 else (f"{s / 3600:.0f} h" if s < 172800 else f"{s / 86400:.0f} d")


# ---------------------------------------------------------------- render

CSS = """
:root{--bg:#191512;--ink:#efe4cf;--dim:#a99c86;--faint:#6d6253;--mustard:#e0aa3e;--red:#e0604a;--lk:#e6d5b0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 -apple-system,system-ui,sans-serif}
main{max-width:min(560px,100vw);overflow-wrap:anywhere;margin:0 auto;padding:14px 14px 40px}
.hb{padding:10px 12px;border-radius:8px;background:#241e19;font-size:14px}.hb.red{background:#4a1d16;color:#ffd9d0}
.age{font-size:30px;font-weight:700;margin:16px 0 0;letter-spacing:-.5px}.age small{display:block;font-size:13px;font-weight:400;color:var(--dim);letter-spacing:0}
h2{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--mustard);margin:22px 0 6px}
h3{font-size:13px;color:var(--dim);margin:10px 0 2px;font-weight:600}
ul{list-style:none;margin:0;padding:0}li{padding:6px 0;border-bottom:1px solid #2c251f}
.m{color:var(--dim);font-size:12.5px}.st{color:var(--mustard);font-size:12.5px;white-space:nowrap}
.none{color:var(--faint);font-size:13.5px}a{color:var(--lk)}
.foot{margin-top:26px;color:var(--faint);font-size:12px}
.pk{font-size:13px;color:var(--dim);margin-top:3px}.pk b{color:var(--ink);font-weight:600;text-transform:capitalize}
.inc{font-size:13px;color:var(--red);margin-top:3px}
"""


def render(brief: dict | None, hb: dict, now: float, base: str = "") -> str:
    e = html.escape
    out = [f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<meta http-equiv=refresh content=120><title>RimPulse brief</title><style>{CSS}</style></head><body><main>",
           f"<div class='hb{' red' if hb['red'] else ''}'>{e(hb['text'])}</div>"]
    if not brief:
        out.append("<div class=age>No brief yet<small>run pulse.py brief</small></div></main></body></html>")
        return "".join(out)
    out.append(f"<div class=age>{e(_ago(brief['at'], now))} old<small>brief of {time.strftime('%a %H:%M', time.localtime(brief['at']))}, "
               f"covering since {time.strftime('%a %H:%M', time.localtime(brief['since']))}</small></div>")
    for sec in ORDER:
        lines = [ln for ln in brief["sections"].get(sec, []) if ln.get("check") == "pass"]
        note = brief.get("notes", {}).get(sec)
        if sec == "coverage" and not lines:
            continue
        out.append(f"<h2>{e(TITLES[sec])}{f' ({len(lines)})' if sec in ('word', 'open') else ''}</h2>")
        if not lines:
            out.append(f"<div class=none>{e(note or ('nothing waiting' if sec in ('word', 'open') else 'nothing'))}</div>")
            continue
        out.append("<ul>")
        goal = None
        for ln in lines:
            if ln.get("head"):
                goal = ln.get("goal")
                out.append(f"</ul><h3>{e(goal)} <span class=m>· {e(ln['text'])}</span></h3><ul>")
                continue
            txt = e(ln["text"])
            if ln.get("link") and str(ln["link"]).startswith(("/", "http")):
                href = base + ln["link"] if ln["link"].startswith("/") else ln["link"]
                txt = f"<a href='{e(href)}'>{txt}</a>"
            meta = ""
            if sec == "open":
                if ln.get("missing"):
                    meta = ("<div class=inc>packet incomplete: no " + e(", no ".join(ln["missing"]))
                            + " - the agent that handed it owes these before you look</div>")
                else:
                    pk = ln.get("packet") or {}
                    meta = "".join(f"<div class=pk><b>{e(k)}</b> {e(pk.get(k, ''))}</div>" for k in PACKET_PARTS)
            if sec == "word":
                mm = ln.get("meta") or {}
                meta = f"<div class=m>waiting {_ago(mm.get('since'), now)}" + (f" · blocks {mm['blocks']}" if mm.get("blocks") else "") + "</div>"
            st = f" <span class=st>{e(ln['state'])}</span>" if ln.get("state") else ""
            out.append(f"<li>{txt}{st}{meta}</li>")
        out.append("</ul>")
    w = brief.get("withheld") or 0
    out.append(f"<div class=foot>Every line checked by {e(brief.get('judged_by') or '?')} at {_hm(brief.get('judged_at'))}"
               + (f"; {w} line{'s' if w != 1 else ''} withheld because the ledger did not bear {'them' if w != 1 else 'it'} out" if w else "")
               + ". Answer cards in the Claude app; this page has no buttons.</div></main></body></html>")
    return "".join(out)


def render_item(iid: str, events: list[dict]) -> str | None:
    world = _model().replay(events)
    it = world.items.get(iid)
    if not it:
        return None
    e = html.escape
    hist = [ev for ev in events if ev.get("id") == iid][-12:]
    rows = "".join(f"<li><span class=m>{e(str(ev.get('ts', ''))[:16])} {e(ev.get('seat') or '')} {e(ev.get('event') or '')}</span><br>"
                   f"{e(_short(ev.get('text') or ev.get('reason') or ev.get('title') or ev.get('ownerSaid') or ev.get('why') or '', 400))}</li>"
                   for ev in reversed(hist))
    return (f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{e(iid)}</title><style>{CSS}</style></head><body><main><a href='/brief'>← brief</a>"
            f"<h2>{e(iid)}</h2><div>{e(it.title or '')}</div><div class=m>{e(it.state)} · needs {e(it.needs)} · owner {e(it.owner or '?')}"
            f"{' · blocked on ' + e(it.blocked_on) if it.blocked and it.blocked_on else ''}</div>"
            f"<h2>Latest events</h2><ul>{rows}</ul></main></body></html>")


# ---------------------------------------------------------------- write + serve


def write_brief(folder: Path, snap: dict, now: float | None = None, run_judge: bool = True) -> Path:
    now = now or time.time()
    _, prev = latest_brief(folder)
    since = max((prev or {}).get("at") or 0, now - WINDOW_CAP) if prev else now - 24 * 3600
    events = pc.read_ledger()
    b = compose(snap, events, since, now)
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / time.strftime("brief_%Y-%m-%d_%H%M.json", time.localtime(now))
    tmp = p.with_name(f"{p.name}.{os.getpid()}.tmp")   # one tmp per writer process
    tmp.write_text(json.dumps(b, indent=1))
    tmp.replace(p)
    if run_judge:   # a separate process: the judge shares no state with the composer
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "judge", str(p)],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"brief judge failed: rc {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
    return p


def allowlist() -> list[str]:
    env = os.environ.get("RM_BRIEF_ALLOW", "")
    if env.strip():
        return [a.strip().lower() for a in env.split(",") if a.strip()]
    try:   # the identity this machine's account page already admits (claude-remote-control machine.json)
        conf = json.loads((Path.home() / ".claude-accounts" / "machine.json").read_text())
        return [str(a).lower() for a in conf.get("page_allow") or []]
    except (OSError, ValueError):
        return []


_WHO: dict = {}


def whois(ip: str) -> str | None:
    hit = _WHO.get(ip)
    if hit and time.time() - hit[1] < 300:
        return hit[0]
    try:
        r = subprocess.run(["tailscale", "whois", "--json", ip], capture_output=True, text=True, timeout=5)
        login = (json.loads(r.stdout).get("UserProfile") or {}).get("LoginName") if r.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        login = None
    if login:   # only a hit is cached: one tailscaled hiccup must not lock the phone out for 5 min
        _WHO[ip] = (login.lower(), time.time())
    return login.lower() if login else None


def tailnet_ip() -> str | None:
    try:
        r = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    ip = (r.stdout or "").strip().splitlines()
    return ip[0] if r.returncode == 0 and ip else None


def page(path: str, snap_fn, folder: Path) -> tuple[int, str, bytes]:
    """The read-only brief routes, shared by the loopback daemon and the tailnet listener."""
    now = time.time()
    path = path.split("?")[0]
    if path in ("/brief", "/brief/"):
        _, b = latest_brief(folder)
        return 200, "text/html; charset=utf-8", render(b, heartbeat(snap_fn(), b, now), now).encode()
    if path == "/heartbeat":
        _, b = latest_brief(folder)
        return 200, "text/plain; charset=utf-8", (heartbeat(snap_fn(), b, now)["text"] + "\n").encode()
    if path == "/brief.json":
        _, b = latest_brief(folder)
        return 200, "application/json", json.dumps({"brief": b, "heartbeat": heartbeat(snap_fn(), b, now)}).encode()
    m = re.fullmatch(r"/item/([A-Z0-9_]{3,64})", path)
    if m:
        body = render_item(m.group(1), pc.read_ledger())
        return (200, "text/html; charset=utf-8", body.encode()) if body else (404, "text/plain", b"no such item\n")
    return 404, "text/plain", b"not found\n"


def serve_tailnet(snap_fn, folder: Path, port: int = BRIEF_PORT) -> None:
    """Bind this machine's tailnet address (retrying until tailscaled has one) and serve the brief
    pages to allowlisted tailnet identities only. Never binds 0.0.0.0."""
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            allow = allowlist()
            who = whois(self.client_address[0])
            if not allow or who not in allow:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"forbidden\n")
                return
            p = "/brief" if self.path in ("/", "") else self.path
            code, ctype, body = page(p, snap_fn, folder)
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    while True:
        ip = tailnet_ip()
        if ip:
            try:
                srv = ThreadingHTTPServer((ip, port), H)
                srv.daemon_threads = True
                print(f"pulse: brief for the tailnet on http://{ip}:{port}/", flush=True)
                srv.serve_forever()
            except OSError as e:
                print(f"pulse: brief tailnet listener: {e}", flush=True)
        time.sleep(60)


def start_tailnet(snap_fn, folder: Path) -> None:
    if BRIEF_PORT:
        threading.Thread(target=serve_tailnet, args=(snap_fn, folder), daemon=True).start()


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "judge":
        p = Path(argv[1])
        b = json.loads(p.read_text())
        snap = json.loads((pc.STATE_DIR / "pulse_now.json").read_text())
        b = judge(b, pc.read_ledger(), snap)
        tmp = p.with_name(f"{p.name}.{os.getpid()}.tmp")   # one tmp per writer process
        tmp.write_text(json.dumps(b, indent=1))
        tmp.replace(p)
        print(f"judged {p.name}: {b['withheld']} withheld")
        return 0
    print("usage: brief.py judge PATH   (compose with: pulse.py brief)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
