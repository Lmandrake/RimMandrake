#!/usr/bin/env python3
"""card_capture.py — a question card's WHOLE text travels with the decision (RIMMANDRAKE_RECORD_CARD_OPTION_TEXT_LABEL_LOST_THE_ART).

2026-11-15: he picked a card option whose description said the choice "needs bigger art". The ledger kept only the
label (`--by-card "question → label"`), the Conductor wrote the builder's brief from memory, the promise became "check if
the sprite is blurry", no art was made, and an hour later nobody could find the request: it lived only in the card's
description, which no record kept. Owner: "Look harder... and find out why this is hard for you. Something needs to be
fixed." So:

  capture   the PostToolUse hook (.claude/hooks/capture_card_answer.py) appends every answered card, every question
            with every option's label AND description and what he picked or typed, to the host's card store
            (<agent storage>/cards/cards.jsonl; RM_CARDS_STORE overrides). Nobody retypes it.
  stamp     `rimflow … --by-card "question → label"` finds that card (store first, then this repo's recent session
            transcripts) and stamps the matched questions whole on the event as `card`; a bare `--by-card` takes the
            card answered last. owner_rulings.py --grep then finds words that were only in a description.
  prose     a `file`/`note` carrying `card` appends "## What the card said" to items/<ID>.md.
  launch    detached_helper.py refuses a brief for a by-card item that lacks a picked option's description verbatim.
  close     each consequence the card states ("needs X") is work owed: `rimflow close` refuses until the close's words
            name each one (where it was done or filed).

    python3 src/RimMandrake/rimflow/card_capture.py show <ITEM>          the card text a brief for ITEM must carry
                    (its spend, token and account sentences out: no launched agent is told its spend; --whole for
                    the person's whole card)
    python3 src/RimMandrake/rimflow/card_capture.py ingest <transcript.jsonl>...   cards from a transcript into the store
    python3 src/RimMandrake/rimflow/card_capture.py recent [--last N]    the store's newest cards
    python3 src/RimMandrake/rimflow/card_capture.py backfill --since YYYY-MM-DD [--apply]
                    each older --by-card event with no `card`: matched at its own time, then (--apply) a `note` on its
                    item through rimflow carrying the whole card (and the prose section)
"""
import argparse
import calendar
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EVENTS = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
AGENT_STORAGE = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
WINDOW_S = 7 * 86400        # a --by-card relays a card answered at most this long ago (one was relayed 5 days late)
BARE_WINDOW_S = 2 * 3600    # a bare --by-card takes the newest card answered this recently
HEADING = "## What the card said"
ARROW = re.compile(r"\s*(?:→|->)\s*")
_ROOT = []


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().casefold()


def store_path():
    env = os.environ.get("RM_CARDS_STORE", "").strip()
    if env:
        return env
    if not _ROOT:
        r = subprocess.run([sys.executable or "python3", AGENT_STORAGE, "rimmandrake"], capture_output=True, text=True,
                           # budget: danger=a hung agent_storage.py holds the card record; never reached in the 14 days to
                           # budget: 2026-11-24; no record of its run
                           timeout=30)
        out = r.stdout.strip()
        if r.returncode or not out:
            raise RuntimeError("agent_storage.py rimmandrake failed: %s" % (r.stderr.strip() or "no output"))
        _ROOT.append(out)
    return os.path.join(_ROOT[0], "cards", "cards.jsonl")


# ------------------------------------------------------------------ one card, from a tool result

def _picked(answer, options):
    """-> (picked options [{label, description}], his own words or ""). An answer is a label, labels joined by ", "
    (multiSelect), or free text; free text that opens "(3)" / "3." / "option 3" picks that option and keeps his words."""
    a = (answer or "").strip()
    by_label = {norm(o.get("label")): o for o in options if o.get("label")}
    if norm(a) in by_label:
        return [by_label[norm(a)]], ""
    parts = [p for p in (x.strip() for x in a.split(",")) if p]
    if parts and all(norm(p) in by_label for p in parts):
        return [by_label[norm(p)] for p in parts], ""
    m = re.match(r"\s*(?:\((\d+)\)|option\s+(\d+)\b|(\d+)[.):])", a, re.I)
    if m:
        n = int(next(g for g in m.groups() if g))
        if 1 <= n <= len(options):
            return [options[n - 1]], a
    hits = [o for o in options if o.get("label") and norm(o["label"]) in norm(a)]
    return hits[:1], a


def from_result(questions, answers, annotations=None, answered="", session="", key=""):
    """-> the card record, or None when nothing was answered. Every option is kept whole."""
    if not isinstance(answers, dict) or not answers or not isinstance(questions, list):
        return None
    qs = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        text = q.get("question") or ""
        if text not in answers:
            continue
        opts = [{"label": o.get("label") or "", "description": o.get("description") or ""}
                for o in (q.get("options") or []) if isinstance(o, dict)]
        picked, words = _picked(answers[text], opts)
        note = (annotations or {}).get(text) if isinstance(annotations, dict) else None
        if isinstance(note, dict):
            note = note.get("notes") or note.get("note") or ""
        qs.append({"question": text, "header": q.get("header") or "", "answer": answers[text],
                   "picked": picked, "his_words": "\n".join(x for x in (words, note or "") if x),
                   "others": [o["label"] for o in opts if o not in picked]})
    if not qs:
        return None
    key = key or hashlib.sha1(json.dumps([answered, qs], sort_keys=True).encode()).hexdigest()[:16]
    return {"answered": answered, "session": session, "key": key, "questions": qs}


def from_hook(payload):
    res = payload.get("tool_response") or {}
    if isinstance(res, str):
        try:
            res = json.loads(res)
        except ValueError:
            res = {}
    inp = payload.get("tool_input") or {}
    return from_result(res.get("questions") or inp.get("questions"), res.get("answers") or inp.get("answers"),
                       res.get("annotations"), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       payload.get("session_id") or "", payload.get("tool_use_id") or "")


def from_transcript(path):
    """-> every answered card in one Claude Code transcript, oldest first."""
    out = []
    with open(path, "rb") as f:
        for raw in f:
            if b'"toolUseResult"' not in raw or b'"answers"' not in raw:
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                continue
            res = rec.get("toolUseResult")
            if not isinstance(res, dict):
                continue
            tid = ""
            for c in ((rec.get("message") or {}).get("content") or []):
                if isinstance(c, dict) and c.get("tool_use_id"):
                    tid = c["tool_use_id"]
            card = from_result(res.get("questions"), res.get("answers"), res.get("annotations"),
                               (rec.get("timestamp") or "")[:19] + "Z", rec.get("sessionId") or "", tid)
            if card:
                out.append(card)
    return out


# ------------------------------------------------------------------ the store

def load(path=None):
    path = path or store_path()
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return out


def save(cards, path=None):
    """Append the cards the store does not hold yet (by key). -> how many were new."""
    path = path or store_path()
    have = {c.get("key") for c in load(path)}
    new = [c for c in cards if c.get("key") not in have]
    if new:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            for c in new:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return len(new)


def transcript_paths(max_age_s=WINDOW_S, now=None):
    """This repo's recent main session transcripts (RM_CARDS_TRANSCRIPTS: a dir of fixtures instead)."""
    d = os.environ.get("RM_CARDS_TRANSCRIPTS", "").strip()
    if d:
        dirs = [d]
    else:
        base = os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), "projects")
        stem = re.sub(r"[^A-Za-z0-9]", "-", REPO)
        dirs = [os.path.join(base, stem)]
    now = now or time.time()
    out = []
    for d in dirs:
        for p in glob.glob(os.path.join(d, "*.jsonl")):
            try:
                if now - os.path.getmtime(p) <= max_age_s:
                    out.append(p)
            except OSError:
                continue
    return out


# ------------------------------------------------------------------ matching a --by-card text to its card

def _epoch(ts):
    try:
        return calendar.timegm(time.strptime((ts or "")[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return None


def _words(s):
    return {w for w in re.findall(r"[a-z0-9']{4,}", norm(s))}


def _pairs(text):
    """'Q1 → A1; Q2 → A2' -> [(q, a)]; a part with no arrow is an answer alone."""
    out = []
    for part in re.split(r";\s+(?=[^;]*(?:→|->))", text or ""):
        bits = ARROW.split(part, maxsplit=1)
        out.append((bits[0], bits[1]) if len(bits) == 2 else ("", bits[0]))
    return out


def _answer_hits(q, answer):
    a = norm(answer)
    if not a:
        return False
    for o in q.get("picked") or []:
        lab = re.sub(r"\s*\(recommended\)\s*$", "", norm(o.get("label")))     # we drop the marker when relaying
        if lab and (a.startswith(lab) or lab.startswith(a[:max(12, len(a))]) or lab in a):
            return True
    words = norm(q.get("his_words"))
    return bool(words) and (words[:40] in a or a[:40] in words)


def match(text, cards, now=None, window_s=WINDOW_S, session=""):
    """-> a card holding only the questions `text` relays (the newest answer per relayed pair), or None.
    A bare text ("", "yes") takes the newest card answered within BARE_WINDOW_S, this session's first."""
    now = now or time.time()
    live = []
    for c in cards:
        t = _epoch(c.get("answered"))
        if t is not None and now - window_s <= t <= now + 120:
            live.append((t, c))
    live.sort(key=lambda x: x[0])
    if norm(text) in ("", "yes"):
        recent = [c for t, c in live if now - t <= BARE_WINDOW_S]
        mine = [c for c in recent if session and c.get("session") == session]
        pick = (mine or recent or [None])[-1]
        return dict(pick) if pick else None
    chosen = []
    for qtext, answer in _pairs(text):
        best = None
        for t, c in live:
            for q in c.get("questions") or []:
                if not _answer_hits(q, answer):
                    continue
                overlap = len(_words(qtext) & _words(q.get("question", "") + " " + q.get("header", "")))
                if qtext.strip() and not overlap and norm(q.get("header")) != norm(qtext):
                    continue
                score = (overlap, t)
                if best is None or score >= best[0]:
                    best = (score, c, q)
        if best and best[2] not in [x[1] for x in chosen]:
            chosen.append((best[1], best[2]))
    if not chosen:
        return None
    base = chosen[-1][0]
    return {"answered": max(c.get("answered") or "" for c, _ in chosen), "session": base.get("session", ""),
            "key": ",".join(sorted({c.get("key", "") for c, _ in chosen})), "questions": [q for _, q in chosen]}


def find(text, now=None, session=""):
    """The store first, then this repo's recent transcripts (whatever they add is saved). -> card or None.
    A throwaway ledger (RIMFLOW_LEDGER, a selftest) reads only the store and transcripts it names, never the host's."""
    throwaway = bool(os.environ.get("RIMFLOW_LEDGER"))
    if os.environ.get("RM_CARDS_NOW"):          # the backfill matches an old relay at its own time
        now = float(os.environ["RM_CARDS_NOW"])
    if throwaway and not os.environ.get("RM_CARDS_STORE"):
        return None
    try:
        path = store_path()
    except RuntimeError:
        path = None
    cards = load(path) if path else []
    hit = match(text, cards, now, session=session)
    if hit:
        return hit
    found = []
    if throwaway and not os.environ.get("RM_CARDS_TRANSCRIPTS"):
        return None
    for p in transcript_paths(now=now):
        try:
            found += from_transcript(p)
        except OSError:
            continue
    if path and found:
        try:
            save(found, path)
        except OSError:
            pass
    return match(text, cards + found, now, session=session)


# ------------------------------------------------------------------ what a card owes

def descriptions(card):
    """-> every non-empty description of a picked option, whole."""
    return [o["description"] for q in (card or {}).get("questions") or [] for o in q.get("picked") or []
            if (o.get("description") or "").strip()]


CONSEQUENCE = re.compile(r"\bneeds?\s+((?:to\s+)?[a-z0-9][\w'+-]*(?:\s+[\w'+-]+){0,5}?)(?=\s*(?:[,.;:)]|\band\b|\bor\b|$))", re.I)


def consequences(card):
    """-> each "needs X" a picked option's description states: work owed by whoever builds the decision."""
    out = []
    for d in descriptions(card):
        for m in CONSEQUENCE.finditer(d):
            phrase = "needs " + m.group(1).strip()
            if re.match(r"needs (no|nothing|none|not)\b", phrase, re.I):     # "needs no game" owes nothing
                continue
            if phrase.lower() not in [x.lower() for x in out]:
                out.append(phrase)
    return out


def for_brief(text):
    """-> text as a launched agent may read it: every spend, token or account sentence out, each "needs X" kept
    (spend_talk; RIMMANDRAKE_STRIP_SPEND_TALK_FROM_CARD_BRIEFS_HAND_CUT)."""
    import spend_talk
    return spend_talk.strip(text or "")


def flatten(card, brief=False):
    """-> the card as plain text: question, picked label, its description, his words, the other options. brief: as a
    launched agent may read it (for_brief on every part; an option left empty by that is not listed)."""
    f = for_brief if brief else (lambda t: t)
    lines = []
    for q in (card or {}).get("questions") or []:
        lines.append("Question: %s" % f(q.get("question", "")))
        for o in q.get("picked") or []:
            lines.append("Picked: %s" % f(o.get("label", "")))
            if o.get("description") and f(o["description"]).strip():
                lines.append("Its description: %s" % f(o["description"]))
        if q.get("his_words") and f(q["his_words"]).strip():
            lines.append("His words: %s" % f(q["his_words"]))
        others = [x for x in (f(o) for o in q.get("others") or []) if x.strip()]
        if others:
            lines.append("Other options: %s" % " · ".join(others))
    return "\n".join(lines)


def prose_section(card, verb, seat):
    owed = consequences(card)
    body = ["", HEADING, "", "<!-- answered %s; recorded by `%s` (%s); written by rimflow, never by hand -->"
            % (card.get("answered") or "?", verb, seat), ""]
    for q in card.get("questions") or []:
        body.append("**Question:** %s" % q.get("question", ""))
        for o in q.get("picked") or []:
            body.append("**Picked:** %s" % o.get("label", ""))
            if o.get("description"):
                body.append("**Its description:** %s" % o["description"])
        if q.get("his_words"):
            body.append("**His words:** %s" % q["his_words"])
        if q.get("others"):
            body.append("**Other options:** %s" % " · ".join(q["others"]))
        body.append("")
    if owed:
        body.append("**Owed by this card** (the close names where each was done or filed): %s" % "; ".join(owed))
        body.append("")
    return "\n".join(body)


def append_prose(items_dir, iid, card, verb, seat):
    """Append the section to items/<iid>.md (made if absent; a closed item is left alone). -> path or None."""
    path = os.path.join(items_dir, iid + ".md")
    if os.path.exists(os.path.join(items_dir, "closed", iid + ".md")):
        return None
    sec = prose_section(card, verb, seat)
    old = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    probe = sec.split("-->", 1)[1]           # the same card already written: once is enough
    if probe.strip() and probe.strip() in old:
        return None
    os.makedirs(items_dir, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(("# %s\n" % iid if not old else ("" if old.endswith("\n") else "\n")) + sec)
    return path


def item_cards(item, evs=None, events_dir=EVENTS):
    """-> the `card` of every ledger event on `item`, oldest first."""
    if evs is None:
        evs = []
        for p in sorted(glob.glob(os.path.join(events_dir, "*.jsonl"))):
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"card"' not in line or item not in line:
                        continue
                    try:
                        evs.append(json.loads(line))
                    except ValueError:
                        continue
    return [e["card"] for e in sorted(evs, key=lambda e: e.get("tsn") or 0)
            if e.get("id") == item and isinstance(e.get("card"), dict)]


def brief_missing(brief, cards):
    """-> each picked description a brief must hold verbatim (whitespace and quote style aside) and does not, as a
    brief may carry it: its spend, token and account sentences out (for_brief), so no gate asks for them."""
    b = norm(brief)
    out = []
    for c in cards:
        for d in descriptions(c):
            d = for_brief(d).strip()
            if d and norm(d) not in b and d not in out:
                out.append(d)
    return out


def close_missing(text, cards):
    """-> each consequence the item's cards owe that the close's words do not name."""
    t = norm(text)
    out = []
    for c in cards:
        for phrase in consequences(c):
            core = norm(re.sub(r"^needs\s+(to\s+)?", "", phrase, flags=re.I))
            if core not in t and phrase not in out:
                out.append(phrase)
    return out


# ------------------------------------------------------------------ CLI

def hook_main(stdin=sys.stdin):
    """PostToolUse/AskUserQuestion: store the answered card. Never blocks, never prints to the window."""
    try:
        payload = json.load(stdin)
        if (payload.get("tool_name") or "AskUserQuestion") != "AskUserQuestion":
            return 0
        card = from_hook(payload)
        if card:
            save([card])
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("card_capture: %s\n" % e)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("show")
    s.add_argument("item")
    s.add_argument("--whole", action="store_true", help="the whole card, spend sentences included (for a person)")
    s.add_argument("--events", default=EVENTS)
    s = sub.add_parser("ingest")
    s.add_argument("paths", nargs="+")
    s = sub.add_parser("recent")
    s.add_argument("--last", type=int, default=5)
    sub.add_parser("hook")
    s = sub.add_parser("backfill")
    s.add_argument("--since", required=True)
    s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "hook":
        return hook_main()
    if a.cmd == "show":
        cards = item_cards(a.item, events_dir=a.events)
        if not cards:
            print("card_capture: no ledger event on %s carries a card (measured over %s)" % (a.item, EVENTS))
            return 1
        for c in cards:
            print(flatten(c, brief=not a.whole))
            owed = consequences(c)
            if owed:
                print("Owed: " + "; ".join(owed))
            print()
        return 0
    if a.cmd == "ingest":
        found = []
        for p in a.paths:
            found += from_transcript(p)
        print("ingest: %d cards read, %d new in %s" % (len(found), save(found), store_path()))
        return 0
    if a.cmd == "recent":
        for c in load()[-a.last:]:
            print(c.get("answered"), c.get("session", "")[:8])
            print("  " + flatten(c).replace("\n", "\n  "))
        return 0
    if a.cmd == "backfill":
        return backfill(a.since, a.apply)
    ap.print_help()
    return 1


def backfill(since, apply=False):
    cards = load()
    evs = []
    for p in sorted(glob.glob(os.path.join(EVENTS, "*.jsonl"))):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"byCard"' in line:
                    try:
                        evs.append(json.loads(line))
                    except ValueError:
                        continue
    done = {(e.get("id"), norm(e.get("byCard"))) for e in evs if isinstance(e.get("card"), dict)}
    todo, seen = [], set()
    for e in sorted(evs, key=lambda e: e.get("ts") or ""):
        k = (e.get("id"), norm(e.get("byCard")))
        if (e.get("ts") or "") < since or not e.get("id") or k in done or k in seen:
            continue
        seen.add(k)
        t = _epoch(e.get("ts"))
        m = match(e["byCard"], cards, now=(t or 0) + 60)
        todo.append((e, m, t))
    ok = bad = 0
    for e, m, t in todo:
        print("%s %s %s | %s" % ("OK" if m else "--", e["ts"][:16], e["id"], e["byCard"][:70]))
        if not (apply and m):
            continue
        env = dict(os.environ, RM_CARDS_NOW=str((t or 0) + 60))
        r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "note", e["id"], "--text",
                            "card backfill: the whole card behind the --by-card of %s (RIMMANDRAKE_RECORD_CARD_OPTION_TEXT_"
                            "LABEL_LOST_THE_ART)" % e["ts"], "--by-card", e["byCard"], "--seat", "BENCH",
                            "--why", "card backfill from the session transcripts"],
                           capture_output=True, text=True, env=env, cwd=REPO, timeout=300)  # budget: class=rimflow
        if r.returncode:
            bad += 1
            print("   note refused: %s" % (r.stdout + r.stderr).strip())
        else:
            ok += 1
    print("backfill: %d relays since %s, %d matched a card, %d noted, %d refused"
          % (len(todo), since, sum(1 for _, m, _ in todo if m), ok, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
