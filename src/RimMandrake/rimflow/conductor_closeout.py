#!/usr/bin/env python3
"""conductor_closeout.py — the program behind B2 step 1 of the goodbye (CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK).

WHY THIS EXISTS. design/RimMandrake/conductor_briefing_2026-10-28.md B2: for every message he sent the Conductor window
that answered or ruled on something, a `--owner-said` event must carry his words; a moved item does not count. The
window checking itself is the risk B4 names, so this diffs his messages in the transcript against the ledger.

  check     lists each message of his with no ledger quote made at or after it. Exit 0 ok, 1 gaps, 3 UNMEASURED.
  dismiss   the window's written word that a listed message ruled on nothing (a chat line, an image it answered).

A program cannot tell a ruling from a chat line, so the default is the safe one: every message is a gap until his words
are on the ledger, sentence by sentence, or the window dismisses it by key with a reason. Exempt without a word: a whole-message goodbye, a
slash command, and a single-sentence question (the ledger refuses a question as `--owner-said`, and his "Perhaps X?"
is an invitation, not a ruling). A bare "yes" is NOT exempt: it may be his answer to a card and the ledger refuses to
quote it, so it stays a gap saying to record the decision another way, then dismiss it.

Gaps never stop the restart (B2 step 4: a partial close-out keeps the gaps themselves). `seat_restart.py request`
stores closeout ok|partial|unmeasured and the gaps on the request; the next window's wake prints those still open.
No top-level import of seat_restart: it imports this module lazily, as a script, and a second copy would diverge.
"""
import argparse
import calendar
import collections
import difflib
import glob
import hashlib
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ECHO_S = 600                     # a queued message's echo arrives within its turn
TEXT_KEEP = 2000                 # one gap's shown text; `miss` keeps every unquoted sentence, so the cut clears nothing
MIN_FUZZY_WORDS = 4              # below this a quote must match word for word
EXCERPT_SHARE = 0.75             # a quote this share of his sentence stands for the sentence
FUZZY_RATIO = 0.85               # his typos fixed in the quote (--owner-said allows that, meaning unchanged)
NEGATORS = frozenset(("not", "no", "never", "dont", "don", "cant", "wont", "nor", "without", "t"))
SLASH = re.compile(r"^/[A-Za-z][\w:-]*(\s|$)")
SENTENCE_END = re.compile(r"(?<=[.!?;:])\s+|\n+")
sys.path.insert(0, HERE)


class Unmeasured(Exception):
    """The ledger or the dismissals cannot be read: the answer is UNMEASURED, never ok."""


def words(text):
    """Lowercased alphanumeric words, any script (the same reading as cli._norm_said)."""
    return "".join(c if c.isalnum() else " " for c in (text or "").lower()).split()


def _pad(ws):
    return " %s " % " ".join(ws)


def covered(sent, quote):
    """Do these quoted words record this sentence? Exact; the sentence inside a longer quote (he joined sentences); a
    quote of two or more words that is EXCERPT_SHARE of the sentence (half let "back up, then delete" lose the delete); or, for MIN_FUZZY_WORDS or more, the same words in
    the same order but for a typo. Only an exact match survives a differing count of negations: "deploy today" is not
    "do not deploy today", and a quote that joins a negated sentence on costs a dismissal, which is the safe side."""
    if not sent or not quote:
        return False
    if sent == quote:
        return True
    if _negations(sent) != _negations(quote):
        return False
    if len(sent) >= 2 and _pad(sent) in _pad(quote):
        return True
    if len(quote) >= 2 and len(quote) >= EXCERPT_SHARE * len(sent) and _pad(quote) in _pad(sent):
        return True
    return len(quote) >= MIN_FUZZY_WORDS \
        and difflib.SequenceMatcher(None, sent, quote, autojunk=False).ratio() >= FUZZY_RATIO


def _negations(ws):
    return collections.Counter(w for w in ws if w in NEGATORS)


def sentences(text):
    """-> the word lists that each need a quote: every statement ("Delete production." is a ruling, and the "Yes." in
    "Yes. Keep the backup." may approve something else, so one word stays a gap until dismissed); a question cannot be
    quoted. The whole message when that leaves none."""
    parts = [(p, words(p)) for p in SENTENCE_END.split(text or "") if p.strip()]
    need = [w for p, w in parts if w and not p.rstrip().endswith("?")]
    return need or [words(text)]


def _event_ts(ev):
    try:
        return calendar.timegm(time.strptime(ev["ts"], "%Y-%m-%dT%H:%M:%SZ"))
    except (KeyError, TypeError, ValueError):
        return None


def ledger_quotes(root=None):
    """-> [(event epoch, words)] of every ownerSaid on every shard. Raises Unmeasured on a bad line, no shards, or no
    quote at all: a ledger with none is a blind instrument (1982 on 2026-11-01), not a clean window."""
    paths = glob.glob(os.path.join(root or REPO, "infrastructure", "state", "ledger", "events", "*.jsonl"))
    if not paths:
        raise Unmeasured("no ledger shards under %s" % (root or REPO))
    out = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if '"ownerSaid"' not in line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError as e:
                        raise Unmeasured("bad line in %s: %s" % (p, e)) from e
                    at = _event_ts(ev)
                    if at is not None and isinstance(ev.get("ownerSaid"), str):
                        out.append((at, words(ev["ownerSaid"])))
        except (OSError, UnicodeError) as e:
            raise Unmeasured("cannot read %s: %s" % (p, e)) from e
    if not out:
        raise Unmeasured("no ownerSaid event on any shard")
    return out


def dismissed_path(seat_log=None):
    seam = os.environ.get("CONDUCTOR_CLOSEOUT_DISMISSED")
    if seam:
        return seam
    if not seat_log:
        try:
            with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
                seat_log = json.load(f)["seat_restart"]["seats"]["BENCH"]["seat_log"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise Unmeasured("no Conductor log path in dispatcher_schedule.json: %s" % e) from e
    return os.path.join(os.path.dirname(seat_log), "closeout_dismissed.jsonl")


def dismissed_keys(path):
    try:
        with open(path, encoding="utf-8") as f:
            return {json.loads(line)["key"] for line in f if line.strip()}
    except FileNotFoundError:
        return set()
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Unmeasured("cannot read %s: %s" % (path, e)) from e


def key_of(uuid_or_key):
    return hashlib.sha1(str(uuid_or_key).encode("utf-8")).hexdigest()[:10]


def exempt_why(text, is_goodbye=None):
    t = (text or "").strip()
    if is_goodbye and is_goodbye(t):
        return "goodbye"
    if "\n" not in t and SLASH.match(t) or t.startswith("<command-") or t.startswith("<local-command"):
        return "command"
    if t and all(p.rstrip().endswith("?") for p in SENTENCE_END.split(t) if p.strip()):
        return "question"
    return None


def hint_for(text, miss=()):
    import cli
    if cli._norm_said(text or "") in cli.ASSENT_ONLY:
        return ("bare assent: the ledger refuses to quote it. If it answered something, record the decision (--by-card, "
                "or the sentence that says what to do), then dismiss it")
    if not (text or "").strip():
        return "no text (an image?): open the record in the transcript"
    if miss and len(miss) < len(sentences(text)):
        return "partly on the ledger; no quote for: %s" % " / ".join(miss)[:300]
    return ""


def evaluate(msgs, is_goodbye=None, root=None, dismissed=None):
    """msgs: [{key, ts, text}] of his messages, or None when the transcript could not be read.
    -> {closeout: ok|partial|unmeasured, why, messages, recorded, dismissed, exempt, gaps: [{key, ts, text, hint}]}."""
    base = {"closeout": "unmeasured", "why": None, "messages": 0, "recorded": 0, "dismissed": 0, "exempt": 0, "gaps": []}
    if msgs is None:
        return dict(base, why="the window's transcript is unreadable, shorter than expected or has a bad record")
    try:
        quotes = ledger_quotes(root)
        gone = dismissed_keys(dismissed or dismissed_path())
    except Unmeasured as e:
        return dict(base, why=str(e))
    msgs = one_each(msgs)
    out = dict(base, messages=len(msgs))
    for m in msgs:
        miss = unquoted(sentences(m["text"]), m.get("ts"), quotes)
        if exempt_why(m["text"], is_goodbye):
            out["exempt"] += 1
        elif not miss:
            out["recorded"] += 1
        elif m["key"] in gone:
            out["dismissed"] += 1
        else:
            out["gaps"].append({"key": m["key"], "ts": m.get("ts"), "text": (m["text"] or "")[:TEXT_KEEP],
                                "hint": hint_for(m["text"], miss), "miss": miss})
    out["closeout"] = "partial" if out["gaps"] else "ok"
    return out


def one_each(msgs):
    """Oldest first, with a message typed mid-turn and then echoed as a user record (MEASURED 2026-10-29: 4 of 444)
    counted once, at the later time. Only that pair folds: two plain "yes" are two answers."""
    out = []
    for m in sorted(msgs, key=lambda r: r.get("ts") or 0):
        twin = next((o for o in reversed(out) if o.get("queued") and not m.get("queued") and o["text"] == m["text"]
                     and (m.get("ts") or 0) - (o.get("ts") or 0) <= ECHO_S), None)
        if twin:
            out[out.index(twin)] = m
        else:
            out.append(m)
    return out


def unquoted(sents, ts, quotes):
    """-> the sentences with no quote at or after his message, joined ([] = recorded). A quote written before he spoke
    cannot be this message: without the time bar his old words clear his new ones. Ledger times are whole seconds, so
    the bar rounds up: an event in the same second may be older than the message."""
    since = math.ceil(ts) if ts else math.inf     # a message with no time cannot be placed after any quote
    live = [q for at, q in quotes if at >= since]
    return [" ".join(w) for w in sents if not any(covered(w, q) for q in live)]


def blind_gap(path, why):
    """An unreadable transcript as a gap: it travels and prints like one and only a dismissal clears it, so a later
    clean window cannot report ok over messages nobody read."""
    return {"key": key_of("blind|%s" % path), "ts": None, "hint": "",
            "text": "UNMEASURED: %s could not be read (%s). Read his messages there and record them by hand." % (path, why),
            "miss": ["blind transcript %s" % key_of(path)]}


def merge_gaps(res, inherited):
    """A verdict plus what the last window left open: a window that never saw a gap must not report ok over it."""
    have = {g["key"] for g in res["gaps"]}
    extra = [g for g in inherited or [] if g.get("key") not in have]
    if extra and res["closeout"] == "ok":
        res["closeout"] = "partial"
    res["gaps"] = extra + res["gaps"]
    return res


def still_open(gaps, root=None, dismissed=None):
    """-> the stored gaps with no ledger quote or dismissal yet; every one of them when that cannot be read."""
    try:
        quotes = ledger_quotes(root)
        gone = dismissed_keys(dismissed or dismissed_path())
    except Unmeasured:
        return list(gaps or [])
    return [g for g in gaps or [] if g.get("key") not in gone
            and unquoted([m.split() for m in g.get("miss") or [g.get("text") or ""]], g.get("ts"), quotes)]


def as_msgs(records, key_fn, text_fn, ts_fn):
    return None if records is None else [
        {"key": key_of(key_fn(r)), "ts": ts_fn(r.get("timestamp")), "text": text_fn(r),
         "queued": bool(r.get("queued_command"))} for r in records]


def transcript_messages(path):
    """-> his messages in the whole transcript via seat_restart's one reading of "his input", or None (UNMEASURED)."""
    import seat_restart as SR
    return as_msgs(SR.human_since_offset(path, 0), SR._msg_key, SR._text, SR._ts)


def window_transcript(pid=None):
    import doorbell
    import seat_restart as SR
    pid = pid or doorbell.claude_ancestor()
    sf = SR.session_file(pid) if pid else None
    return SR.transcript_path(sf["cwd"], sf["sessionId"]) if sf and sf.get("cwd") and sf.get("sessionId") else None


def _goodbye_rule():
    import goodbye_phrase as GP
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        cfg = json.load(f)["seat_restart"]["seats"]["BENCH"]
    phr = GP.phrases(cfg)
    return lambda t: GP.is_goodbye(t, phr)


def report(res):
    """-> the lines of a verdict, shared by `check` and the restart request."""
    if res["closeout"] == "unmeasured":
        lines = ["CLOSEOUT UNMEASURED: %s. Check his messages by hand; this is not ok." % res["why"]]
    else:
        lines = ["CLOSEOUT %s: %d of his messages: %d on the ledger, %d dismissed, %d exempt, %d GAPS." % (
            res["closeout"].upper(), res["messages"], res["recorded"], res["dismissed"], res["exempt"], len(res["gaps"]))]
    for g in res["gaps"]:
        lines.append("- key %s at %s: %s" % (g["key"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(g["ts"] or 0)),
                                            " ".join((g["text"] or "(no text)").split())[:300]))
        if g["hint"]:
            lines.append("    %s" % g["hint"])
    return lines


def cmd_check(args):
    path = args.transcript or window_transcript(args.pid)
    res = evaluate(transcript_messages(path) if path else None, _goodbye_rule(), args.root or None)
    print(json.dumps(res, indent=1) if args.json else "\n".join(report(res)))
    return {"ok": 0, "partial": 1}.get(res["closeout"], 3)


def cmd_dismiss(args):
    if not args.why.strip():
        print("conductor_closeout: dismiss needs a real --why")
        return 2
    try:
        p = dismissed_path()
    except Unmeasured as e:
        print("conductor_closeout: REFUSED: %s" % e)
        return 3
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        for k in args.key:
            f.write(json.dumps({"key": k, "why": args.why, "ts": time.time()}) + "\n")
    print("dismissed %d (%s)" % (len(args.key), p))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="his messages in this window against the ledger")
    c.add_argument("--transcript", help="the jsonl to read (default: this window's)")
    c.add_argument("--pid", type=int, help="the claude pid whose window to read (default: this one)")
    c.add_argument("--root", help="the clone whose ledger to read (default: this one)")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_check)
    d = sub.add_parser("dismiss", help="a listed message ruled on nothing")
    d.add_argument("--key", action="append", required=True)
    d.add_argument("--why", required=True)
    d.set_defaults(fn=cmd_dismiss)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
