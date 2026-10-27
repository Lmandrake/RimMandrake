#!/usr/bin/env python3
"""blind_view.py — the queue and item notes as a token-blind role may read them (review W, L1 + L3).

The token-blind roles (Conductor, Producer, Arbiter, Auditor, Innovator: every role whose schedule entry is not
`token_aware: true`) must never read a token, account, runway, quota, week, burn, cap or budget value (owner,
2026-10-27). Code routes are guarded, but titles and notes are written by hand, and ledger events are append-only:
a leaking note can never be edited away. So a blind role reads the queue and an item's notes through this view,
never through raw `rimflow queue` / `rimflow show`.

Allow-list, never a word denylist (lesson of 2026-10-27): the view prints only fields it knows are safe — id, state,
kind, needs, row, owner, a BLOCKED flag, event verbs and their times. Free text (titles, notes, block reasons, the
one-line spec summary) passes only through redact(): any upper-case id naming accounts, any number that sits within NEAR_TOKENS words of an account,
token, quota, cap, budget, runway, burn, spend, usage, limit or week word, any number with a k / M / % / tokens /
$ unit, and any number of 10,000 or more is replaced with "[…]". Dates, clock times and hex shas pass.
An item about accounts by its id or kind (withheld()) is withheld whole: the queue counts it and names nothing, `show`
prints only that it is withheld, and its id is redacted out of any other item's free text.

Free-text redaction can never be perfect, and this one does not try to be: a phrasing nobody has thought of will get
through. The backstop is ops_watch's token-talk drift check (ops_watch_rules.json token_talk), which measures how often
each blind seat's and role's reports hold token talk at all. Add a phrasing to selftest_blind_view.py when one is found;
do not chase a perfect regex (review X).

Usage:
  python3 src/RimMandrake/rimflow/blind_view.py queue BENCH
  python3 src/RimMandrake/rimflow/blind_view.py show <ID> [--last N] [--prefix "REPLAN REQUEST"]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))

MASK = "[…]"
NEAR_TOKENS = 8                      # words either side of a sensitive word in which a number is redacted
BIG_NUMBER = 10000                   # a bare number this large is a token count until proved otherwise
# a word part (split at _ . - and case) that makes a number near it sensitive; matched as a prefix of the part
SENSITIVE_PREFIXES = ("account", "token", "quota", "budget", "runway", "burn", "spend", "spent", "usage", "limit",
                      "week", "pct", "percent", "economy")
SENSITIVE_WORDS = {"cap", "caps", "capped", "capping", "capx", "wk", "wkly", "headroom",
                   "allowance", "pace"}
TABLE_WORDS = {"share", "used", "left", "remaining", "pct", "percent"}   # also make a whole table sensitive
# "soft" sensitive parts: ordinary project words too, so a count of work items next to them is kept (review X, X7)
SOFT_PARTS = ("week", "limit")
WORK_NOUNS = {"item", "items", "ticket", "tickets", "row", "rows", "file", "files", "def", "defs", "test", "tests",
              "commit", "commits", "claim", "claims", "patch", "patches", "mod", "mods", "bug", "bugs", "finding",
              "findings", "job", "jobs", "task", "tasks", "sprite", "sprites", "step", "steps", "milestone",
              "milestones", "check", "checks", "review", "reviews", "helper", "helpers", "role", "roles", "seat",
              "seats", "line", "lines", "page", "pages", "round", "rounds"}
TIME_NOUNS = {"week", "weeks", "day", "days"}
ACCOUNT_NAMES = {"lukas", "steven", "system", "codex", "sonnet", "opus", "haiku"}    # + lent_accounts of slot_rules
SOFT_NAMES = {"system"}               # an ordinary word as well as an account: its counts of work items stay
NAME_AFTER, NAME_BEFORE = 6, 4        # a number this many words after / before an account name is its value
# an id with one of these parts (or an NNK part) has the digits in it masked: PRODUCER_RUN_30K_EVENT
ID_DIGIT_PARTS = {"K", "TOKEN", "TOKENS", "CAP", "CAPS", "BUDGET", "RUNWAY", "WEEK", "PCT", "PERCENT", "BURN", "QUOTA",
                  "SPEND", "USAGE"}
# an item whose id starts with one of these, or whose id or kind has one of these parts, is about accounts: withheld
# whole. Kept narrow on purpose: CAP, BURN, RUNWAY and BUDGET are ordinary game words here (a wildlife cap, Burn
# weather, RM_RunwayBloom, a frame budget), and withholding hides real work from the Conductor; their numbers are
# redacted near the word anyway.
WITHHELD_ID_PREFIXES = ("OPS_", "OPERATIONS_")
WITHHELD_ID_PARTS = {"ACCOUNT", "ACCOUNTS", "TOKEN", "TOKENS", "QUOTA", "QUOTAS", "SPEND"}
WITHHELD_KIND_PARTS = WITHHELD_ID_PARTS | {"OPS", "OPERATIONS", "BUDGET", "BUDGETS", "RUNWAY", "BURN"}

_MAGN = (r"(?i:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|(?:thir|four|fif|six|seven|eigh|nine)"
         r"teen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|and|a|\d+(?:[.,]\d+)*)[\s-]+)*")
_TOKEN_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?Z?)?)"
    r"|(?P<time>\b\d{1,2}:\d{2}(?::\d{2})?Z?\b)"
    r"|(?P<unit>\$\s?\d+(?:[.,]\d+)*(?:\s?[kKM])?|[€£₤]\s?\d+(?:[.,]\d+)*"
    r"|\d+(?:[.,]\d+)*(?:\s?(?:[kKM]|%|pct|percent|tokens?|tok|kt))(?![A-Za-z0-9])"
    r"|\b" + _MAGN + r"(?i:thousand|million|billion)\b)"
    r"|(?P<scaled>\d+(?:[.,]\d+)*\s?(?:[xX×]|d|days?|h|hrs?|hours?|w|wks?|weeks?)(?![A-Za-z0-9_]))"
    r"|(?P<word>[A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<num>\d+(?:[.,]\d+)*)")


def _parts(word):
    """`daily_token_cap` -> [daily, token, cap]; `sessionWeekPct` -> [session, week, pct]."""
    out = []
    for p in re.split(r"[_\d]+", word):
        out += [q.lower() for q in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", p)]
    return out


def sensitive_word(word):
    return any(p in SENSITIVE_WORDS or p.startswith(SENSITIVE_PREFIXES) for p in _parts(word))


_ID_FRAGMENT_RE = re.compile(r"_[A-Z0-9]{3,6}")


def _account_id(word):
    """An item id (or an alarm-id fragment like `_C01D`) that names accounts, even one not in this world (closed,
    or in another clone): an upper-case id that withheld() would withhold by id, or a bare `_XXXX` id suffix."""
    if _ID_FRAGMENT_RE.fullmatch(word):
        return True
    return "_" in word and word.upper() == word and _account_item_id(word)


def _account_item_id(iid):
    return iid.upper().startswith(WITHHELD_ID_PREFIXES) or bool(set(re.split(r"[^A-Z]+", iid.upper()))
                                                                 & WITHHELD_ID_PARTS)


def _number(s):
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


_names_cache = []


def account_names():
    """Account and model names, lower case: ACCOUNT_NAMES plus every key of slot_rules.json lent_accounts and every
    account name ops_watch's rules or the slot rules mention under `accounts` (read at run time, never hard-coded)."""
    if not _names_cache:
        names = set(ACCOUNT_NAMES)
        try:
            import json
            utils = os.path.join(os.path.dirname(HERE), "Utils")
            for fn, keys in (("slot_rules.json", ("lent_accounts", "accounts")),
                             ("ops_watch_rules.json", ("accounts", "lent_accounts"))):
                try:
                    d = json.load(open(os.path.join(utils, fn), encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                for k in keys:
                    if isinstance(d.get(k), dict):
                        names |= {str(n).lower() for n in d[k] if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{2,}", str(n))
                                  and not str(n).startswith("_")}
        except Exception:  # noqa: BLE001 — names are best effort on top of the built-in set
            pass
        _names_cache.append(names)
    return _names_cache[0]


def _is_name(word):
    n = account_names()
    return word.lower() in n or any(p in n for p in _parts(word))


def digit_id(word):
    """An upper-case id with a number in it and a K / TOKEN / CAP / BUDGET / RUNWAY ... part (or an NNK part), or an
    account name: PRODUCER_RUN_30K_EVENT, LUKAS_93_WEEK_DRAIN."""
    if "_" not in word or word.upper() != word or not re.search(r"\d", word):
        return False
    parts = word.split("_")
    return any(p in ID_DIGIT_PARTS or re.fullmatch(r"\d+K", p) or p.lower() in account_names() for p in parts)


def mask_id(word):
    """-> the id with the digits of a digit_id masked, else unchanged."""
    return re.sub(r"\d+", MASK, word) if digit_id(word) else word


def _blank_tables(text):
    """A markdown table with an account or token column (a sensitive word or account name anywhere in it) is blanked
    whole: a number far from the word is still in its column (review X, X4)."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            block = lines[i:j]
            words = re.findall(r"[A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*", "\n".join(block))
            if any(sensitive_word(w) or _is_name(w) or w.lower() in TABLE_WORDS for w in words):
                out.append("[table redacted: it has an account or token column]")
            else:
                out += block
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def redact(text, hide_ids=(), keep_ids=()):
    """Pure. Free text -> the same text with every account/cap number replaced by MASK, and every id in hide_ids
    (items withheld from blind roles) replaced by MASK. An id in keep_ids (a real ledger id) is never
    altered: ids are keys. None -> ""."""
    if not text:
        return ""
    text = _blank_tables(str(text))
    toks = [m for m in _TOKEN_RE.finditer(text)]
    # hot[i] = "strong" | "soft" | ("name", soft): a word that makes a number near it sensitive
    hot = {}
    for i, m in enumerate(toks):
        if m.lastgroup == "scaled" and re.search(r"(?:w|wks?|weeks?)$", m.group()):
            hot[i] = "soft"
        if m.lastgroup != "word":
            continue
        w = m.group()
        if _is_name(w):
            hot[i] = ("name", w.lower() in SOFT_NAMES)
        elif sensitive_word(w):
            hot[i] = "soft" if all(p in SOFT_PARTS or not (p in SENSITIVE_WORDS or p.startswith(SENSITIVE_PREFIXES))
                                   for p in _parts(w)) else "strong"

    def word_at(k):
        return toks[k].group().lower() if 0 <= k < len(toks) and toks[k].lastgroup == "word" else ""

    def near(i):
        """-> 'strong' | 'soft' | None: how a number at token i is tied to an account word."""
        best = None
        for h, kind in hot.items():
            d = i - h
            if isinstance(kind, tuple):
                if not (1 <= d <= NAME_AFTER or -NAME_BEFORE <= d <= -1):
                    continue
                c = "soft" if kind[1] else "strong"
            elif abs(d) <= NEAR_TOKENS and d != 0:
                c = kind
            else:
                continue
            if c == "strong":
                return "strong"
            best = "soft"
        return best

    cut = []
    for i, m in enumerate(toks):
        g = m.lastgroup
        if g == "unit":
            cut.append((m.start(), m.end(), MASK))
        elif g in ("num", "scaled"):
            v = _number(re.match(r"\d+(?:[.,]\d+)*", m.group()).group())
            n = near(i)
            if g == "num" and v is not None and v >= BIG_NUMBER:
                cut.append((m.start(), m.end(), MASK))
            elif n == "strong":
                cut.append((m.start(), m.end(), MASK))
            elif n == "soft":
                # a count of work items or of weeks/days stays (review X, X7): "3 tickets this week", "rows 4 and 5"
                nxt, prv = word_at(i + 1), word_at(i - 1)
                keep = nxt in WORK_NOUNS or prv in WORK_NOUNS or (g == "num" and nxt in TIME_NOUNS) or (
                    g == "scaled" and re.search(r"(?:w|wks?|weeks?)$", m.group()))
                if not keep:
                    cut.append((m.start(), m.end(), MASK))
        elif g == "word":
            w = m.group()
            if w in hide_ids or _account_id(w):
                cut.append((m.start(), m.end(), MASK))
            elif w in keep_ids:
                continue
            elif digit_id(w):
                cut.append((m.start(), m.end(), mask_id(w)))
    out, pos = [], 0
    for a, b, r in cut:
        out.append(text[pos:a])
        out.append(r)
        pos = b
    out.append(text[pos:])
    return "".join(out)


def withheld(it):
    """Is this item about accounts? By its id or kind only: a title word is no guide ("accounted for", "quotas" of a
    review), and a withheld item is work the Conductor cannot see. Its title's numbers are redacted either way."""
    if _account_item_id(it.id or ""):
        return True
    if any(re.fullmatch(r"\d+K", p) for p in (it.id or "").split("_")):
        return True     # the id itself carries a token-cost number: withheld, never mangled
    return bool(set(re.split(r"[^A-Z]+", (it.kind or "").upper())) & WITHHELD_KIND_PARTS)


def _load():
    from rimflow import model
    evs = model.read()
    return evs, model.replay(evs)


def known_ids(world):
    return {i.id for i in world.items.values() if not withheld(i)}


def hidden_ids(world):
    return {i.id for i in world.items.values() if withheld(i)}


def queue_text(world, seat, target="v1", ctx=None, summaries=True):
    """-> the blind queue of one seat: the same sections, in the same order, as `rimflow queue <SEAT>`, with
    allow-listed fields only and redacted free text."""
    from rimflow import render
    hide = hidden_ids(world)
    keep = known_ids(world)
    ranked, sections = render.view_sections(world, seat, target, ctx)
    n_hidden = len({i.id for i in world.items.values() if i.owner == seat and i.open and i.id in hide})
    out = ["# %s queue, blind view" % seat,
           "Ids, states, kinds and needs. Titles, notes and reasons are redacted: a number about accounts or caps "
           "reads %s. %d open item(s) about accounts are withheld (Operations' alone)." % (MASK, n_hidden), ""]

    def item(it):
        lines = ["## %s %s" % (it.id, redact(it.title, hide, keep)),
                 "state: %s%s   kind: %s   needs: %s   row: %s" % (
                     it.state, " (BLOCKED)" if it.blocked else "", it.kind or "task", it.needs,
                     it.row if it.row not in (None, "") else "unassigned")]
        if it.blocked:
            lines.append("blocked: %s" % redact(it.blocked_reason or "unexplained", hide, keep))
        if summaries:
            lines.append("summary: %s" % redact(render.summary(it.id), hide, keep))
        return lines + [""]
    groups = [("NEXT", ranked)] + [(t, items) for t, items, _n, _x in sections]
    for title, items in groups:
        items = [i for i in items if i.id not in hide]
        if not items:
            continue
        out.append("# %s (%d)" % (title, len(items)))
        out.append("")
        for it in items:
            out += item(it)
    return "\n".join(out) + "\n"


def show_text(evs, world, iid, last=10, prefix=None):
    """-> one item's allow-listed fields and its last `last` notes (only those starting `prefix`, if given),
    free text redacted. A withheld item prints that it is withheld and nothing else."""
    it = world.items.get(iid)
    if it is None:
        return "%s: no such item\n" % iid
    hide = hidden_ids(world)
    keep = known_ids(world)
    if iid in hide:
        return "%s: withheld from the blind view (an item about accounts: Operations' alone)\n" % iid
    out = ["%s   state %s%s   kind %s   owner %s   needs %s" % (
        it.id, it.state, " (BLOCKED)" if it.blocked else "", it.kind or "task", it.owner, it.needs),
        "title: %s" % redact(it.title, hide, keep)]
    if it.blocked:
        out.append("blocked: %s" % redact(it.blocked_reason or "unexplained", hide, keep))
    if it.closed_sha:
        out.append("closed at %s" % it.closed_sha)
    if it.superseded_by:
        out.append("superseded by %s" % (MASK if it.superseded_by in hide else it.superseded_by))
    notes = [evs[i] for i in it.history if evs[i].get("event") == "note"]
    if prefix:
        notes = [e for e in notes if (e.get("text") or "").lstrip().startswith(prefix)]
    shown = notes[-last:] if last else notes
    out.append("--- notes: last %d of %d%s (redacted) ---" % (len(shown), len(notes),
                                                              " starting %r" % prefix if prefix else ""))
    for e in shown:
        out.append("%s %s: %s" % (e.get("ts"), e.get("seat"), redact(e.get("text"), hide, keep)))
    others = [evs[i] for i in it.history if evs[i].get("event") != "note"]
    out.append("--- other events: %d (verb, time, seat only) ---" % len(others))
    for e in others[-last:] if last else others:
        out.append("%s %s %s" % (e.get("ts"), e.get("event"), e.get("seat")))
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue", help="a seat's queue, blind")
    q.add_argument("seat")
    s = sub.add_parser("show", help="one item's fields and notes, blind")
    s.add_argument("id")
    s.add_argument("--last", type=int, default=10, help="notes to print (0 = all; default 10)")
    s.add_argument("--prefix", help="only notes whose text starts with this (e.g. 'REPLAN REQUEST')")
    a = ap.parse_args(argv)
    evs, world = _load()
    if a.cmd == "queue":
        sys.stdout.write(queue_text(world, a.seat.upper()))
    else:
        sys.stdout.write(show_text(evs, world, a.id, a.last, a.prefix))
    return 0


if __name__ == "__main__":
    sys.exit(main())
