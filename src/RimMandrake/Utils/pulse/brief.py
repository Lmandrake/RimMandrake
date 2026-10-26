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
import glob
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
import usage  # noqa: E402

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
SECTION_SOURCES = {"away": ("ledger",), "word": ("ledger",), "raised": ("ledger",), "open": ("hands", "sheets"), "home": ("ledger",), "overnight": ("ledger",),
                   "decided": ("ledger",), "spend": ("tokens",), "testing": ("testing",), "next": ("sessions",)}
TITLES = {"away": "By your return", "word": "Needs your word", "raised": "Escalated, nobody on it", "open": "Open these", "home": "When you're home", "overnight": "Overnight, in words",
          "decided": "Decided for you", "spend": "Spend", "testing": "Testing rigs", "next": "Next", "coverage": "Coverage"}
ORDER = ("away", "word", "raised", "open", "home", "overnight", "decided", "spend", "testing", "next", "coverage")

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


_PACKAGES: dict[str, str] | None = None
TOOL_AREAS = {"pulse": "RimPulse", "rimpulse": "RimPulse", "rimflow": "rimflow", "artpipe": "artpipe",
              "rimbench": "rimbench", "stevedesktop": "SteveDesktop", "modcheck": "modcheck", "testq": "testq"}
_NOT_AREAS = {"state", "items", "ledger", "closed", "utils", "src", "design", "transient"}


def packages() -> dict[str, str]:
    """{lowercase name: mod folder} of every mod with an About.xml in a clone (src/<tier>/<Mod>/About)."""
    global _PACKAGES
    if _PACKAGES is None:
        _PACKAGES = {}
        for root in [HERE.parents[3]] + list(pc.CLONES):
            for a in glob.glob(str(Path(root) / "src" / "*" / "*" / "About" / "About.xml")):
                name = Path(a).parents[1].name
                _PACKAGES.setdefault(name.lower(), name)
            if _PACKAGES:
                break
    return _PACKAGES


def goal_of(iid: str, item=None, words: str = "", pkgs: dict | None = None) -> str:
    """The package or V1 row an item serves (owner 2026-10-25: the brief "invented goals from the first word of
    titles"). Order: its V1 row; a mod folder its spec / close note / evidence names (src/<tier>/<Mod>/); a
    mod whose name is a word of its id or title; a tool area its paths name; else 'No package recorded' -
    never a word of the title promoted to a goal."""
    pkgs = packages() if pkgs is None else pkgs
    if item is not None and getattr(item, "row", None) not in (None, ""):
        return f"V1 row {item.row}"
    mods = Counter(x.lower() for x in re.findall(r"\bsrc[/\\]Rim\w+[/\\](\w+)[/\\]", words) if x.lower() in pkgs)
    if mods:
        return pkgs[mods.most_common(1)[0][0]]
    for w in str(iid or "").split("_"):
        if w.lower() in pkgs:
            return pkgs[w.lower()]
    for w in re.findall(r"\b[A-Z][A-Za-z]+\b", str(getattr(item, "title", "") or "")):
        if w.lower() in pkgs and w[1:].lower() != w[1:]:      # CamelCase names only: 'Abyss' the word stays a word
            return pkgs[w.lower()]
    for w in str(iid or "").split("_"):
        if w.lower() in TOOL_AREAS:
            return TOOL_AREAS[w.lower()]
    areas = Counter(x.lower() for x in re.findall(r"\b(?:Utils|infrastructure)[/\\](\w+)[/\\]", words)
                    if x.lower() not in _NOT_AREAS and not x.endswith("py"))
    if areas:
        a = areas.most_common(1)[0][0]
        return TOOL_AREAS.get(a, a)
    return "No package recorded"


def commit_paths(shas: list[str], root: Path | None = None) -> dict[str, str]:
    """{sha given: the paths its commit changed, space-joined}, in ONE git call; a sha this clone lacks is
    skipped (--ignore-missing), and git failing at all yields {} (grouping then falls back, never raises)."""
    shas = sorted({str(x) for x in shas if re.fullmatch(r"[0-9a-f]{7,40}", str(x or ""))})
    if not shas:
        return {}
    git = ["git", "-C", str(root or HERE.parents[3])]
    try:   # an abbreviated sha this clone lacks is a fatal 'bad revision' to log (--ignore-missing misses it)
        known = subprocess.run(git + ["cat-file", "--batch-check=%(objectname) %(objecttype)"],
                               input="\n".join(shas) + "\n", capture_output=True, text=True, timeout=60).stdout.splitlines()
        shas = [x for x, k in zip(shas, known) if k.endswith(" commit")]
        if not shas:
            return {}
        out = subprocess.run(git + ["log", "--no-walk=unsorted", "--stdin", "--name-only", "--format=@@%H"],
                             input="\n".join(shas) + "\n", capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    full: dict[str, list[str]] = {}
    cur = None
    for ln in out.splitlines():
        if ln.startswith("@@"):
            cur = ln[2:].strip()
            full[cur] = []
        elif cur and ln.strip():
            full[cur].append(ln.strip())
    return {s_: " ".join(full[h]) for s_ in shas for h in full if h.startswith(s_)}


def item_words(iid: str) -> str:
    """An item's prose file (open or closed), for the paths it names; '' when no clone has one."""
    for c in pc.CLONES:
        for sub in ("", "closed/"):
            f = Path(c) / "infrastructure" / "state" / "items" / f"{sub}{iid}.md"
            try:
                return f.read_text(encoding="utf-8", errors="replace")[:20000]
            except OSError:
                continue
    return ""


def outcome_of(iid: str, events: list[dict], since: float, now: float) -> str:
    """What an item ended with, in its own record: the close / implemented note in the window, else the last
    passing verify's 'verified <criterion> (<evidence>)'. '' when the ledger says nothing (the title stands in)."""
    note, ver = "", ""
    for e in events:
        if e.get("id") != iid or not (since <= _tsec(e) <= now):
            continue
        if e.get("event") in ("close", "implemented") and (e.get("reason") or e.get("text")):
            note = str(e.get("reason") or e.get("text"))
        elif e.get("event") == "verify" and e.get("result") == "pass":
            ev = str(e.get("evidence") or "")
            ver = f"verified {e.get('criterion') or ''}".strip() + (f" ({Path(ev).name})" if ev and " " not in ev else "")
    return note or ver


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


def packet_view(row: dict) -> dict:
    """The widget's view of a look's packet, from the same reader the phone brief uses: {parts, missing}."""
    parts, missing = read_packet(packet_path(row))
    return {"parts": {k: _short(v, 220) for k, v in parts.items()}, "missing": missing}


def _source_down(snap: dict, sec: str) -> list[str]:
    src = snap.get("sources") or {}
    return [s for s in SECTION_SOURCES.get(sec, ()) if not (src.get(s) or {}).get("ok")]


def compose(snap: dict, events: list[dict], since: float, now: float, plan: dict | None = None) -> dict:
    world, moves = transitions(events, since, now)
    secs: dict[str, list[dict]] = {k: [] for k in ORDER}
    notes: dict[str, str] = {}
    if plan:   # BY YOUR RETURN: the trip plan and whether the ledger bears it out (RIMPULSE_PLAN_BUILD_ON_TRACK_WHILE_AWAY)
        secs["away"] = plan_lines(plan, world, now)
    else:
        notes["away"] = "no trip plan"
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
        # the question in plain words, noun first (pulse_core.ask_label); the ticket name rides in `id`
        text = r.get("label") or (pc.ask_label(iid, title) if iid else title)
        asks.append({"sec": "word", "text": _short(text, 150), "id": iid,
                     "meta": {"since": r.get("since"), "blocks": blocks.get(iid, 0), "kind": r["kind"],
                              "who": r.get("who")},
                     "link": f"/item/{iid}" if iid else (r.get("link") or {}).get("value"),
                     "claim": {"type": "ask", "id": iid} if iid else {"type": "card", "key": r["key"]}})
    asks.sort(key=lambda a: (-a["meta"]["blocks"], a["meta"]["since"] or now))
    secs["word"] = asks

    # WHEN YOU'RE HOME: hands-on machine jobs (owner card 2026-10-25, "Folded 'when you're home' list"),
    # apart from the rulings, by machine, with the total time the runbooks give
    home = sorted((r for r in rows if r["kind"] == "chore"),
                  key=lambda r: (str(r.get("machine") or ""), r.get("minutes") or 999))
    for r in home:
        iid = r["key"][6:] if str(r.get("key", "")).startswith("needs:") else None
        mins = r.get("minutes")
        secs["home"].append({"sec": "home", "text": _short(f"{r.get('machine') or 'at home'}: {r.get('label') or r.get('text') or ''}", 150),
                             "id": iid, "meta": {"since": r.get("since"), "minutes": mins},
                             "link": f"/item/{iid}" if iid else None,
                             "claim": {"type": "ask", "id": iid} if iid else {"type": "card", "key": r["key"]}})
    if not home:
        notes["home"] = "no machine jobs waiting"

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
    own: dict[str, list[dict]] = defaultdict(list)     # each moved item's own events, one pass
    for e in events:
        if e.get("id") in last:
            own[e["id"]].append(e)
    pkgs = packages()
    changed = commit_paths([e.get("sha") for es in own.values() for e in es
                            if e.get("event") in ("close", "implemented", "verify")])
    for iid, m in last.items():
        if m["to"] in STATE_WORD:
            words = " ".join(str(e.get("spec") or "") + " " + str(e.get("reason") or "") + " " + str(e.get("evidence") or "")
                             for e in own[iid] if e.get("event") in ("file", "close", "implemented", "verify"))
            # what its commits changed outranks what its prose mentions: those paths come first and count double
            cp = " ".join(changed.get(str(e.get("sha")), "") for e in own[iid] if e.get("sha"))
            words = f"{cp} {cp} {words} {item_words(iid)}"
            by_goal[goal_of(iid, world.items.get(iid), words, pkgs)].append(
                {"id": iid, "to": m["to"], "tsn": m["tsn"], "t": m["t"]})
    goals = sorted(by_goal.items(), key=lambda kv: (kv[0] == "No package recorded", -len(kv[1]), kv[0]))
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
            out = outcome_of(x["id"], own[x["id"]], since, now)
            if out.startswith("verified ") or not out:          # no close note: what it was, then its evidence
                out = (it.title or x["id"]) + (f" — {out}" if out else "")
            secs["overnight"].append({"sec": "overnight", "goal": g, "text": _short(out, 100),
                                      "title": it.title or x["id"],
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
    # plan usage per account against the budget rule (usage.py); "unknown" where nothing measured it
    for ln in usage.lines((snap.get("charts") or {}).get("usage"), now):
        secs["spend"].append({"sec": "spend", **ln})

    # TESTING: the rigs' day so far (TESTING_RIG_MONITOR_EFFICIENCY_IN_PULSE), one line, re-derived by the judge
    ln = testing_line(snap)
    if ln:
        secs.setdefault("testing", []).append(ln)
    else:
        notes["testing"] = "no testing history yet"
    # RAISED: an escalation a seat has not taken up (the SteveDesktop steward's T+30, design
    # work_allocation_framework_2026-10-26.md section 6.4), one line each, re-derived by the judge
    for it in sorted((i for i in world.items.values() if i.open and getattr(i, "raised", None)),
                     key=lambda i: (i.raised, i.id)):
        secs["raised"].append({
            "sec": "raised", "id": it.id, "link": f"/item/{it.id}",
            "text": _short(f"Raised for {(it.owner or '?').capitalize()}, {it.state}: {it.title or it.id}", 150),
            "claim": {"type": "raised", "id": it.id, "state": it.state}})

    # NEXT: what each seat is on, from the live session chips, item named by the ledger
    for c in snap.get("chips") or []:
        if c.get("seat") in SEATS:
            m = re.search(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+){1,7})\b", c.get("title") or "")
            iid = m.group(1) if m else None
            it = world.items.get(iid) if iid else None
            n = int(c.get("agents") or 0)   # helpers working under an idle seat window are work (owner 2026-10-25)
            what = (_short(it.title, 90) if it else "working" if c.get("state") == "run"
                    else f"{n} helper{'s' if n != 1 else ''} working" if n else "idle")
            if n and (it or c.get("state") == "run"):
                what += f" (+{n} helper{'s' if n != 1 else ''})"
            secs["next"].append({"sec": "next", "text": f"{c['seat'].capitalize()}: {what}",
                                 "link": f"/item/{iid}" if it else None,
                                 "claim": {"type": "seat", "seat": c["seat"], "id": iid if it else None,
                                           "state": c.get("state"), "agents": n}})

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


TESTING_LINE = (("busy_pct", "busy", "%"), ("rows_per_hour", "rows/h", ""), ("findings", "findings", ""),
                ("waste_pct", "waste", "%"))


def testing_line(snap: dict) -> dict | None:
    """'Testing <day>: SteveDesktop busy 40% · 12 rows/h · 2 findings · waste 10% | Archmagi ...' from the
    monitor's Testing panel; an UNMEASURED value is the word, never 0. The claim carries every number shown."""
    panel = (snap.get("charts") or {}).get("testing") or {}
    if not panel.get("machines"):
        return None
    parts, values = [], {}
    for m in panel["machines"]:
        bits = []
        for k, word, unit in TESTING_LINE:
            x = m["metrics"].get(k) or {}
            if x.get("m") == "MEASURED" and x.get("v") is not None:
                values[f"{m['key']}.{k}"] = x["v"]
                n = x["v"]
                bits.append(f"{word} {n:g}{unit}" if word in ("busy", "waste") else f"{n:g} {word}")
            else:
                values[f"{m['key']}.{k}"] = None
                bits.append(f"{word} unmeasured")
        parts.append(f"{m['label']} " + " · ".join(bits))
    return {"sec": "testing", "text": f"Testing {panel.get('day')}: " + " | ".join(parts),
            "claim": {"type": "testing", "day": panel.get("day"), "values": values}}


def check_testing(c: dict) -> str:
    """Re-derive the line from the collector's own history file (not the monitor's copy)."""
    import testing_metrics as T
    rec = T.best_per_day(T.read_history()).get(c.get("day") or "")
    if not rec:
        return f"fail: no testing record for {c.get('day')}"
    for key, shown in (c.get("values") or {}).items():
        mach, k = key.split(".", 1)
        x = ((rec.get("machines") or {}).get(mach) or {}).get(k) or {}
        got = x.get("v") if x.get("m") == "MEASURED" else None
        if got != shown:
            return f"fail: {key} reads {got} in the history, the line says {shown}"
    return "pass"


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
            if "state" in c:   # the line's seat state and helper count must match the monitor's own chip
                ch = next((x for x in snap.get("chips") or [] if x.get("seat") == c.get("seat")), None)
                if not ch or ch.get("state") != c["state"] or int(ch.get("agents") or 0) != int(c.get("agents") or 0):
                    return "fail: the monitor's seat chip says otherwise"
            if c.get("id") is None:
                return "pass"
            it = world.items.get(c["id"])
            return "pass" if it and it.open else "fail: item not open"
        if t == "testing":
            return check_testing(c)
        if t == "raised":
            it = world.items.get(c.get("id"))
            if not it:
                return "fail: no such item in the ledger"
            if not it.open or not getattr(it, "raised", None):
                return f"fail: item is {it.state}{'' if getattr(it, 'raised', None) else ', not raised'}"
            return "pass" if it.state == c.get("state") else f"fail: item is {it.state}, the line says {c.get('state')}"
        if t == "plan":   # its own replay's states, and its own verdict when the line gives one
            got = {i: ("missing" if i not in world.items else "blocked" if world.items[i].open and world.items[i].blocked
                       else world.items[i].state) for i in c.get("states") or {}}
            if got != c.get("states"):
                return "fail: the ledger says " + ", ".join(f"{i} {v}" for i, v in got.items() if v != c["states"].get(i))
            if "on_track" in c and plan_verdict({"at": c.get("at"), "until": c.get("until")}, got,
                                                brief.get("at") or time.time())[0] != c["on_track"]:
                return "fail: the ledger does not bear out the on-track verdict"
            return "pass"
        if t == "usage":
            return usage.check_claim(c, (snap.get("charts") or {}).get("usage"))
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
.m{color:var(--dim);font-size:12.5px}.st{color:var(--mustard);font-size:12.5px;white-space:nowrap}.new{color:var(--bg,#111);background:var(--mustard);border-radius:3px;padding:0 4px;font-size:11px;margin-left:4px}
.none{color:var(--faint);font-size:13.5px}a{color:var(--lk)}
.foot{margin-top:26px;color:var(--faint);font-size:12px}
.pk{font-size:13px;color:var(--dim);margin-top:3px}.pk b{color:var(--ink);font-weight:600;text-transform:capitalize}
.inc{font-size:13px;color:var(--red);margin-top:3px}
"""


def line_time(ln: dict) -> float | None:
    """When the thing a line reports happened: an ask's wait start, a move's ledger event."""
    c = ln.get("claim") or {}
    if c.get("tsn"):
        return c["tsn"] / 1e9
    tsns = [x.get("tsn") for x in c.get("items") or [] if x.get("tsn")]
    return max(tsns) / 1e9 if tsns else (ln.get("meta") or {}).get("since")


def render(brief: dict | None, hb: dict, now: float, base: str = "", visit: dict | None = None) -> str:
    e = html.escape
    out = [f"<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           # reload only while it is on screen: a hidden tab reloading is not him reading it (brief_opens)
           "<script>setInterval(function(){if(document.visibilityState==='visible')location.reload()},120000)</script>"
           f"<title>RimPulse brief</title><style>{CSS}</style></head><body><main>",
           f"<div class='hb{' red' if hb['red'] else ''}'>{e(hb['text'])}</div>"]
    if not brief:
        out.append("<div class=age>No brief yet<small>run pulse.py brief</small></div></main></body></html>")
        return "".join(out)
    bs = brief.get("since_basis") or {}
    why = (f" - the paper you last opened ({bs.get('device')}, {time.strftime('%a %H:%M', time.localtime(bs['seen']))})"
           if bs.get("kind") == "opened" and bs.get("seen") else "")
    out.append(f"<div class=age>{e(_ago(brief['at'], now))} old<small>brief of {time.strftime('%a %H:%M', time.localtime(brief['at']))}, "
               f"new since {time.strftime('%a %H:%M', time.localtime(brief['since']))}{e(why)}</small></div>")
    bar = (visit or {}).get("before")   # what THIS device had seen by the end of its last visit
    if visit:
        out.append(f"<div class=m>{e(visit['device'])}: " + (f"marked new = since the paper of "
                   f"{time.strftime('%a %H:%M', time.localtime(bar))} you saw here last" if bar else "first open on this device")
                   + "</div>")
    for sec in ORDER:
        lines = [ln for ln in brief["sections"].get(sec, []) if ln.get("check") == "pass"]
        note = brief.get("notes", {}).get(sec)
        if sec in ("coverage", "raised") and not lines or sec == "away" and not lines and note:
            continue                          # no trip, no "By your return" heading
        if sec == "away" and not lines:
            note = "a trip plan exists but the ledger did not bear out its lines"
        count = f" ({len(lines)})" if sec in ("word", "open", "home") else ""
        if sec == "home" and lines:
            count = f" ({len(lines)} · {pc.chores_time([ln.get('meta') or {} for ln in lines])})"
        out.append(f"<h2>{e(TITLES[sec])}{count}</h2>")
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
            if sec == "home":
                mm = ln.get("meta") or {}
                meta = f"<div class=m>{mm['minutes']} min</div>" if mm.get("minutes") else "<div class=m>time not given</div>"
            if sec == "word":
                mm = ln.get("meta") or {}
                meta = f"<div class=m>waiting {_ago(mm.get('since'), now)}" + (f" · blocks {mm['blocks']}" if mm.get("blocks") else "") + "</div>"
            st = f" <span class=st>{e(ln['state'])}</span>" if ln.get("state") else ""
            lt = line_time(ln)
            nw = " <span class=new>new</span>" if bar and lt and lt > bar else ""
            out.append(f"<li>{txt}{st}{nw}{meta}</li>")
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


# ---------------------------------------------------------------- by your return (trip plan)
# RIMPULSE_PLAN_BUILD_ON_TRACK_WHILE_AWAY: before a trip the seat writes a short plan - what will be done by
# his return, the first thing that will need him, the fallback - with `brief.py plan set`; he may change it
# (`plan edit --owner-said`); every paper then says on track or not against it, from the ledger.
PLAN = pc.STATE_DIR / "away_plan.json"
DONE_STATES = ("done", "validated")
SLACK = 1 / 3        # on track while the share done is no more than a third behind the share of time gone


def read_plan(path: Path | None = None) -> dict | None:
    try:
        d = json.loads((path or PLAN).read_text())
        return d if isinstance(d, dict) and d.get("items") else None
    except (OSError, ValueError):
        return None


def write_plan(plan: dict, path: Path | None = None) -> None:
    path = path or PLAN
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(plan, indent=1))
    tmp.replace(path)


def plan_states(plan: dict, world) -> dict[str, str]:
    out = {}
    for iid in plan.get("items") or []:
        it = world.items.get(iid)
        out[iid] = "missing" if not it else ("blocked" if it.open and it.blocked else it.state)
    return out


def plan_verdict(plan: dict, states: dict[str, str], now: float) -> tuple[bool, str]:
    """(on track?, the words). Pure: the composer and the judge both call it on their own replay."""
    n = len(states)
    done = [i for i, st in states.items() if st in DONE_STATES]
    gone = [i for i, st in states.items() if st in ("dropped", "superseded", "missing")]
    stuck = [i for i, st in states.items() if st == "blocked"]
    at, until = plan.get("at") or now, plan.get("until") or now
    frac = 1.0 if until <= at else min(1.0, max(0.0, (now - at) / (until - at)))
    head = f"{len(done)} of {n} done"
    if len(done) == n:
        return True, f"done: all {n} items closed or checked"
    if now >= until:
        return False, f"missed: {head} by your return; open: {', '.join(i for i in states if i not in done)}"
    if gone:
        return False, f"not on track: {', '.join(gone)} {'was' if len(gone) == 1 else 'were'} dropped or replaced; {head}"
    if stuck:
        return False, f"not on track: {', '.join(stuck)} {'is' if len(stuck) == 1 else 'are'} blocked; {head}"
    if len(done) / n + SLACK < frac:
        return False, f"behind: {head} with {frac:.0%} of the time gone"
    return True, f"on track: {head}, {frac:.0%} of the time gone"


def plan_lines(plan: dict, world, now: float) -> list[dict]:
    states = plan_states(plan, world)
    ok, words = plan_verdict(plan, states, now)
    by = time.strftime("%a %H:%M", time.localtime(plan["until"])) if plan.get("until") else "?"
    out = [{"sec": "away", "head": True, "goal": f"Plan by {plan.get('by') or '?'} for your return {by}",
            "text": words, "on_track": ok,
            "claim": {"type": "plan", "states": states, "on_track": ok, "at": plan.get("at"), "until": plan.get("until")}}]
    for iid, st in states.items():
        it = world.items.get(iid)
        out.append({"sec": "away", "text": _short(f"{(it.title if it else '') or iid}", 140), "id": iid,
                    "state": STATE_WORD.get(st, st), "link": f"/item/{iid}" if it else None,
                    "claim": {"type": "plan", "states": {iid: st}, "at": plan.get("at"), "until": plan.get("until")}})
    fn = plan.get("first_need") or {}
    if fn.get("text"):
        out.append({"sec": "away", "text": "First thing that will need you: " + _short(fn["text"], 160), "id": fn.get("id"),
                    "link": f"/item/{fn['id']}" if fn.get("id") else None, "claim": {"type": "unknown"}})
    if plan.get("fallback"):
        out.append({"sec": "away", "text": "If it goes wrong: " + _short(plan["fallback"], 160), "claim": {"type": "unknown"}})
    for ed in (plan.get("edits") or [])[-3:]:
        who = "you" if ed.get("owner_said") else ed.get("by") or "?"
        out.append({"sec": "away", "text": f"Changed by {who} {time.strftime('%a %H:%M', time.localtime(ed['at']))}: "
                                           + _short(ed.get("owner_said") or ed.get("why") or ed.get("change") or "", 160),
                    "claim": {"type": "unknown"}})
    return out


def plan_cli(argv: list[str], path: Path | None = None, events: list[dict] | None = None) -> int:
    """brief.py plan set|edit|show|clear - how an agent writes the trip plan (and records his changes)."""
    import argparse
    ap = argparse.ArgumentParser(prog="brief.py plan")
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("set", help="write the plan before a trip (replaces any old one)")
    st.add_argument("--by", required=True, help="the seat writing it")
    st.add_argument("--until", required=True, help="his return, local time 'YYYY-MM-DD HH:MM'")
    st.add_argument("--item", action="append", required=True, help="a rimflow id that will be done (repeat)")
    st.add_argument("--first-need", required=True, help="the first thing that will need him, in words")
    st.add_argument("--first-need-id", help="its rimflow id, if it has one")
    st.add_argument("--fallback", required=True, help="what happens if the plan goes wrong")
    ed = sub.add_parser("edit", help="change it; his words in --owner-said, an agent's own reason in --why")
    ed.add_argument("--by", required=True)
    g = ed.add_mutually_exclusive_group(required=True)
    g.add_argument("--owner-said")
    g.add_argument("--why")
    ed.add_argument("--add", action="append", default=[])
    ed.add_argument("--drop", action="append", default=[])
    ed.add_argument("--until")
    ed.add_argument("--first-need")
    ed.add_argument("--first-need-id")
    ed.add_argument("--fallback")
    sub.add_parser("show")
    sub.add_parser("clear", help="the trip is over")
    a = ap.parse_args(argv)
    path = path or PLAN
    now = time.time()

    def when(v: str) -> float:
        return time.mktime(time.strptime(v, "%Y-%m-%d %H:%M"))

    def known(ids: list[str]) -> None:
        world = _model().replay(events if events is not None else pc.read_ledger())
        bad = [i for i in ids if i not in world.items]
        if bad:
            raise SystemExit(f"plan: no such rimflow item: {', '.join(bad)}")
    if a.cmd == "show":
        plan = read_plan(path)
        if not plan:
            print("no trip plan")
            return 0
        world = _model().replay(events if events is not None else pc.read_ledger())
        for ln in plan_lines(plan, world, now):
            print(("== " + ln["goal"] + ": " if ln.get("head") else "  ") + ln["text"] + (f"  [{ln['state']}]" if ln.get("state") else ""))
        return 0
    if a.cmd == "clear":
        if path.exists():
            path.unlink()
        print("trip plan cleared")
        return 0
    if a.cmd == "set":
        known(a.item + ([a.first_need_id] if a.first_need_id else []))
        u = when(a.until)
        if u <= now:
            raise SystemExit("plan: --until is not in the future")
        write_plan({"v": 1, "by": a.by, "at": now, "until": u, "items": list(dict.fromkeys(a.item)),
                    "first_need": {"text": a.first_need, "id": a.first_need_id}, "fallback": a.fallback, "edits": []}, path)
        print(f"trip plan written: {len(a.item)} items by {a.until}")
        return 0
    plan = read_plan(path)
    if not plan:
        raise SystemExit("plan: no trip plan to edit (plan set first)")
    known(a.add + ([a.first_need_id] if a.first_need_id else []))
    change = []
    for i in a.add:
        if i not in plan["items"]:
            plan["items"].append(i)
            change.append(f"+{i}")
    for i in a.drop:
        if i in plan["items"]:
            plan["items"].remove(i)
            change.append(f"-{i}")
    if a.until:
        plan["until"] = when(a.until)
        change.append(f"until {a.until}")
    if a.first_need or a.first_need_id:
        fn = plan.get("first_need") or {}
        plan["first_need"] = {"text": a.first_need or fn.get("text"), "id": a.first_need_id or (None if a.first_need else fn.get("id"))}
        change.append("first need")
    if a.fallback:
        plan["fallback"] = a.fallback
        change.append("fallback")
    if not plan["items"]:
        raise SystemExit("plan: an edit may not empty the plan (plan clear ends the trip)")
    plan.setdefault("edits", []).append({"at": now, "by": a.by, "owner_said": a.owner_said, "why": a.why,
                                         "change": ", ".join(change)})
    write_plan(plan, path)
    print(f"trip plan edited: {', '.join(change) or 'words only'}")
    return 0


# "New" = everything since he last opened the paper (owner, 2026-10-25), per device. One visit is a run of
# requests with gaps under VISIT_GAP (the page reloads itself while it is on screen).
OPENS = pc.STATE_DIR / "brief_opens.json"
VISIT_GAP = 30 * 60
_OPENS_LOCK = threading.Lock()


def read_opens() -> dict:
    try:
        d = json.loads(OPENS.read_text())
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def record_open(device: str, brief_at: float | None, now: float) -> dict:
    """Note that `device` has the paper of `brief_at` on screen; return this device's record, whose
    `before` is the newest paper it had seen by the end of its previous visit (what is new to it now)."""
    with _OPENS_LOCK:
        d = read_opens()
        r = dict(d.get(device) or {})
        if not r or now - (r.get("seen") or 0) > VISIT_GAP:   # a new visit: what it saw last time is the bar
            r.update(visit=now, before=r.get("brief_at"), before_seen=r.get("seen"), visits=int(r.get("visits") or 0) + 1)
        r["seen"] = now
        if brief_at:
            r["brief_at"] = max(brief_at, r.get("brief_at") or 0)
        d[device] = r
        OPENS.parent.mkdir(parents=True, exist_ok=True)
        tmp = OPENS.with_name(f"{OPENS.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(d, indent=1))
        tmp.replace(OPENS)
        return {**r, "device": device}


def since_basis(prev: dict | None, opens: dict, now: float) -> tuple[float, dict]:
    """(since, basis): the newest paper he opened on any device, else the previous paper, else a day."""
    seen = [(r["brief_at"], dev, r.get("seen")) for dev, r in opens.items() if (r or {}).get("brief_at")]
    if seen:
        at, dev, when = max(seen)
        return max(at, now - WINDOW_CAP), {"kind": "opened", "device": dev, "seen": when, "brief_at": at}
    if prev:
        return max(prev.get("at") or 0, now - WINDOW_CAP), {"kind": "previous"}
    return now - 24 * 3600, {"kind": "day"}


def write_brief(folder: Path, snap: dict, now: float | None = None, run_judge: bool = True) -> Path:
    now = now or time.time()
    _, prev = latest_brief(folder)
    since, basis = since_basis(prev, read_opens(), now)
    events = pc.read_ledger()
    b = compose(snap, events, since, now, plan=read_plan())
    b["since_basis"] = basis
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


def whois(ip: str) -> tuple[str | None, str | None]:
    """(login, device name) of a tailnet peer; (None, None) when tailscaled cannot say."""
    hit = _WHO.get(ip)
    if hit and time.time() - hit[2] < 300:
        return hit[0], hit[1]
    try:
        r = subprocess.run(["tailscale", "whois", "--json", ip], capture_output=True, text=True, timeout=5)
        d = json.loads(r.stdout) if r.returncode == 0 else {}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        d = {}
    login = (d.get("UserProfile") or {}).get("LoginName")
    node = d.get("Node") or {}
    device = node.get("ComputedName") or str(node.get("Name") or "").split(".")[0] or None
    if login:   # only a hit is cached: one tailscaled hiccup must not lock the phone out for 5 min
        _WHO[ip] = (login.lower(), device, time.time())
    return (login.lower() if login else None), device


def tailnet_ip() -> str | None:
    try:
        r = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    ip = (r.stdout or "").strip().splitlines()
    return ip[0] if r.returncode == 0 and ip else None


def page(path: str, snap_fn, folder: Path, device: str | None = None) -> tuple[int, str, bytes]:
    """The read-only brief routes, shared by the loopback daemon and the tailnet listener. `device` is set
    only for his own tailnet devices: that request is an open of the paper (record_open)."""
    now = time.time()
    path = path.split("?")[0]
    if path in ("/brief", "/brief/"):
        _, b = latest_brief(folder)
        visit = record_open(device, (b or {}).get("at"), now) if device else None
        return 200, "text/html; charset=utf-8", render(b, heartbeat(snap_fn(), b, now), now, visit=visit).encode()
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
            ip = self.client_address[0]
            who, device = whois(ip)
            if not allow or who not in allow:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"forbidden\n")
                return
            p = "/brief" if self.path in ("/", "") else self.path
            # his opens move "new": a request from this machine itself is an agent checking, never him
            code, ctype, body = page(p, snap_fn, folder, device=None if ip == tailnet_ip() else (device or ip))
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
    if argv and argv[0] == "plan":
        return plan_cli(argv[1:])
    print("usage: brief.py judge PATH | brief.py plan set|edit|show|clear   (compose with: pulse.py brief)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
