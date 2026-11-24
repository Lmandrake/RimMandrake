#!/usr/bin/env python3
"""item_packet.py: one item's history as one text, for the brief of a detached run. No model, no tokens.

Item RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT. Page design/specs/2026-11-23-item-packet/boundary.md;
selftest selftest_item_packet.py. `detached_helper.brief_message` puts the text in every detached brief, but for a role
that starts fresh (`role_of`).

    python3 src/RimMandrake/rimflow/item_packet.py ITEM [--clone DIR]    print the packet a run of ITEM would carry
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

BUDGET_CHARS = 12000    # the text is read again on every turn of a run (the page's LIMITS)
COMMITS = 12
GIT_S = 120             # hang guard
COULD_NOT = "could not look"
SHOW = "python3 src/RimMandrake/rimflow/cli.py show %s"
GITLOG = "git log --extended-regexp --grep='\\b%s\\b'"

# ---- the roles that start fresh -------------------------------------------------------------------------------------
# A blind judge, a fresh reader, an examiner, a challenger and a coverage judge get no history (CLAUDE.md: they always start
# fresh). A wrong yes costs a run one `show`; a wrong no spoils a blind verdict, so the patterns lean to yes.
ROLE_ENV = "RM_FRESH_ROLE"                          # a hand launch can say it: --env RM_FRESH_ROLE="fresh reader"
FRESH_STAGES = {"blind_challenge": "blind judge", "pre_human": "fresh reader"}
_YOU = r"\byou are[ \t\n]+(?:[\w'’-]+,?[ \t\n]+){0,6}?"
ROLES = (
    ("blind judge", re.compile(_YOU + r"blind[ \t\n]+judge\b|\byou judge \S+ blind\b|^#+ *blind challenge \(stages",
                               re.I | re.M)),
    ("coverage judge", re.compile(_YOU + r"coverage[ \t\n-]+judge\b", re.I)),
    ("examiner", re.compile(_YOU + r"examiner\b", re.I)),
    ("challenger", re.compile(_YOU + r"challenger\b", re.I)),
    ("fresh reader", re.compile(_YOU + r"reader\b|^title: *(?:(?:one|a|the) )?fresh[ -]reader\b", re.I | re.M)),
)


def role_of(brief, env=None):
    """-> the fresh-start role this run has (it gets no history), else None."""
    env = env or {}
    if str(env.get(ROLE_ENV) or "").strip():
        return str(env[ROLE_ENV]).strip()
    text = re.sub(r"[*`_]", "", brief or "")
    for name, rx in ROLES:
        if rx.search(text):
            return name
    return FRESH_STAGES.get(env.get("RM_CONTROL_STAGE"))


# ---- what a launched agent is not given -----------------------------------------------------------------------------
_PRICED = re.compile(r"\d[\d.,]*\s*[kM]?\s+weighted\b|\bweighted[_ ]v\d", re.I)
_SENTENCE = re.compile(r"(?<=[.!?;])\s+")


def clean(text):
    """-> (text without its cost sentences, how many lines lost one). Every other line stays as it was written."""
    import spend_talk
    out, lost = [], 0
    for line in str(text or "").split("\n"):
        if not (spend_talk.is_spend(line) or _PRICED.search(line)):
            out.append(line)
            continue
        kept = " ".join(s for s in _SENTENCE.split(spend_talk.strip(line)) if not _PRICED.search(s))
        lost += 1
        if kept.strip():
            out.append(line[:len(line) - len(line.lstrip())] + kept)
    return "\n".join(out), lost


# ---- the packet -----------------------------------------------------------------------------------------------------
_HEADED = re.compile(r"^\W*(?:LEFT OPEN:|PROGRESS:)", re.M | re.I)
_CAPS = re.compile(r"\b(?:RULING|REFUSED)\b|\b(?i:ruling):")
CLOSED = ("done", "dropped", "superseded")


def decisive(note):
    """A note that is never dropped: the owner's words or seat, or LEFT OPEN:, PROGRESS:, RULING, REFUSED."""
    t = str(note.get("text") or "")
    return bool(note.get("owner_said") or note.get("by_card") or note.get("seat") == "OWNER" or _HEADED.search(t) or _CAPS.search(t))


def _note(n, i, of):
    text, lost = clean(n.get("text"))
    head = "[note %d of %d] %s %s%s" % (i, of, n.get("ts") or "no time", n.get("seat") or "no seat",
                                        " (%s)" % n["event"] if n.get("event") not in (None, "note") else "")
    said, lost2 = clean(n.get("owner_said"))
    if said.strip() and said.strip() not in text:
        text += "\nthe owner's words: \"%s\"" % said
    card, lost3 = clean(n.get("by_card"))
    if card.strip() and card.strip() not in text:
        text += "\nthe owner's card: %s" % card
    return "%s\n%s\n" % (head, text), lost + lost2 + lost3


def _run(r):
    config, config_lost = clean(r.get("config"))
    evidence, evidence_lost = clean(r.get("evidence"))
    if not evidence:
        evidence = "(left out, below)" if evidence_lost else "no evidence named"
    text = "%s %s%s: %s" % (r.get("ts") or "no time", r.get("result") or "no result",
                           " (%s)" % config if config else "", evidence)
    return text, config_lost + evidence_lost


def _linked_row(x):
    title, lost = clean(x.get("title"))
    text = "%s [%s]%s%s" % (x.get("id"), x.get("state") or COULD_NOT, " " + title if title else "",
                            " (%s)" % x["how"] if x.get("how") else "")
    return text, lost


def _ranges(nums):
    """[1, 2, 3, 7] -> "1-3, 7"."""
    out = []
    for n in nums:
        if out and out[-1][1] == n - 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join("%d" % a if a == b else "%d-%d" % (a, b) for a, b in out)


class _Part(object):
    """One droppable or kept piece of the text."""

    def __init__(self, kind, i, text, name, lost=0, keep=False, rank=0):
        self.kind, self.i, self.text, self.name, self.lost, self.keep, self.rank = kind, i, text, name, lost, keep, rank


def _parts(facts, budget):
    """-> {kind: [_Part] in the order read, or None when the part could not be read}."""
    out = {}
    notes = facts.get("notes")
    if notes is not None:
        last = max((k for k, n in enumerate(notes) if n.get("event") in (None, "note")), default=-1)
        out["notes"] = []
        for k, n in enumerate(notes):
            text, lost = _note(n, k + 1, len(notes))
            out["notes"].append(_Part("notes", k + 1, text, "note %d of %d (%s %s)" % (
                k + 1, len(notes), n.get("ts") or "no time", n.get("seat") or "no seat"), lost,
                keep=k in (last, len(notes) - 1) or decisive(n), rank=0))
    else:
        out["notes"] = None
    rows = (("commits", lambda c: clean("%s %s" % (c.get("sha"), c.get("subject"))), lambda c: "commit %s" % c.get("sha"),
             lambda c: (False, 1)),
            ("linked", _linked_row, lambda x: "linked item %s" % x.get("id"),
             lambda x: (False, 2 if x.get("state") in CLOSED else 4)),
            ("runs", _run, lambda r: "run of %s (%s)" % (r.get("ts"), r.get("result")), lambda r: (r.get("result") != "pass", 3)),
            ("criteria", lambda c: clean(str(c)), lambda c: "criterion", lambda c: (True, 9)))
    for kind, say, name, how in rows:
        got = facts.get(kind)
        if got is None:
            out[kind] = None
            continue
        out[kind] = []
        # commits come newest first: the oldest goes first, so the newest has the highest number
        for k, g in enumerate(got):
            text, lost = say(g)
            keep, rank = how(g)
            out[kind].append(_Part(kind, len(got) - k if kind == "commits" else k + 1, "- %s\n" % text, name(g), lost, keep,
                                   rank))
    prose = facts.get("prose")
    if prose is None:
        out["prose"] = None
    else:
        text, lost = clean(prose)
        out["prose"] = [_Part("prose", 1, text.strip() + "\n", "the prose (%s)" % (
            facts.get("prose_path") or "its item file"), lost, keep=len(text) <= budget, rank=5)] if prose.strip() else []
    return out


SECTIONS = (("prose", "The item's prose", "the item has no prose"), ("criteria", "Open criteria", "no open criteria"),
            ("notes", "Notes, oldest first", "no notes"), ("runs", "Runs of its test", "no runs recorded"),
            ("linked", "Linked items", "no linked items"),
            ("commits", "The newest commits that name it", "no commits name it"))


def packet(item, facts, budget_chars=BUDGET_CHARS):
    """-> {"text", "left_out": [each dropped part], "could_not_look": [each part that could not be read]}. The contract
    is in the head of the acceptance script and on the page."""
    if not isinstance(item, str) or not item.strip():
        raise ValueError("item_packet.packet: no item")
    item, show, why = item.strip(), SHOW % item.strip(), facts.get("why") or {}
    parts = _parts(facts, budget_chars)
    if "criteria" not in facts:     # the contract's facts hold none: not a part that was asked for
        parts["criteria"] = []
    could_not = []
    for kind, _, _ in SECTIONS:
        if parts[kind] is None:
            could_not.append("%s: %s" % (kind, why.get(kind) or "the reading is not there"))
    for k in ("state", "title"):
        if facts.get(k) is None:
            could_not.append("%s: %s" % (k, why.get(k) or "the reading is not there"))
    if facts.get("ledger", "") is None:
        could_not.append("whether the ledger is level with origin/main: %s" % (why.get("ledger") or "no cause"))

    def text_of(dropped):
        stripped = [p for k in parts if parts[k] for p in parts[k] if p.lost and p not in dropped]
        (title, tlost), (state, slost) = clean(facts.get("title")), clean(facts.get("state"))
        left = [p.name for p in dropped] + ["%d line(s) of %s lost a sentence about what a run costs" % x for x in
                                            [(p.lost, p.name) for p in stripped] + [(slost, "the state"), (tlost, "the title")]
                                            if x[0]]
        more = facts.get("commits_more") or 0
        if more:
            left.append("%d older commit(s)" % more)
        L = ["ITEM PACKET of %s. The launcher read the item at %s; a later write is not here." % (
            item, facts.get("as_of") or "a time that was not recorded")]
        if facts.get("ledger"):
            L.append("The ledger of this clone: %s." % facts["ledger"])
        if facts.get("known") is False:
            L.append("The ledger of this clone does not know this item: looked, found none.")
        L += ["State: %s" % (
                  COULD_NOT if facts.get("state") is None else state.strip() or ("(left out, below)" if slost else "")),
              "Title: %s" % (
                  COULD_NOT if facts.get("title") is None else title.strip() or ("(left out, below)" if tlost else ""))]
        if could_not:
            L += ["%s: %s" % (COULD_NOT.capitalize(), c) for c in could_not] + ["The command that looks again: `%s`" % show]
        if left:
            groups = []
            for kind, one in (("notes", "notes"),):
                nums = sorted(p.i for p in dropped if p.kind == kind)
                if nums:
                    groups.append("%s %s of %d" % (one, _ranges(nums), len(parts[kind])))
            groups += [p.name for p in dropped if p.kind != "notes"]
            groups += left[len(dropped):]
            L.append("LEFT OUT of this packet: %d part(s): %s. The item, whole: `%s`%s" % (
                len(left), "; ".join(groups), show, ("; its commits: `%s`" % (GITLOG % item)) if more or any(
                    p.kind == "commits" for p in dropped) else ""))
        else:
            L.append("Nothing was left out. The same from the ledger: `%s`" % show)
        if facts.get("bookkeeping"):
            L.append("%d bookkeeping events (claims, leases, starts and the like) are not shown." % facts["bookkeeping"])
        for kind, head, none in SECTIONS:
            if kind == "criteria" and "criteria" not in facts:
                continue
            L += ["", "## %s" % head]
            if parts[kind] is None:
                L.append("%s: %s" % (COULD_NOT, why.get(kind) or "the reading is not there"))
            elif not parts[kind]:
                L.append("Looked: %s." % none)
            else:
                body = [p.text.rstrip("\n") for p in parts[kind] if p not in dropped]
                L += body or ["(all of it is left out, above)"]
        return "\n".join(L) + "\n", left

    queue = sorted((p for k in parts if parts[k] for p in parts[k] if not p.keep), key=lambda p: (p.rank, p.i))
    dropped = []
    text, left = text_of(dropped)
    while len(text) > budget_chars and queue:
        over, gone = len(text) - budget_chars, 0
        while queue and gone < over:        # at least what is over; the list of names then asks for more
            p = queue.pop(0)
            gone += len(p.text)
            dropped.append(p)
        text, left = text_of(dropped)
    return {"text": text, "left_out": left, "could_not_look": could_not}


# ---- reading the item -----------------------------------------------------------------------------------------------
BOOKKEEPING = ("file", "spawn", "claim", "start", "lease", "reclaim", "home", "shape", "effect", "verify",
               "capability", "preflight", "retarget", "guard")
# An event that is not a note gives each of its fields whole, but for the machine's own stamps. `card` is not text: the
# launch puts the card's words in the brief itself (detached_helper.card_repair).
STAMPS = ("ts", "tsn", "seat", "event", "id", "role_unit", "session", "preflight", "preflight_run", "preflight_ms",
          "ownerSaid", "byCard", "card")
NAME = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}\b")


def _git(clone, *args):
    r = subprocess.run(["git", "-C", clone] + list(args), capture_output=True, text=True, timeout=GIT_S,
                       stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (args[0], (r.stderr or "").strip()))
    return r.stdout


def _event_note(e):
    """One ledger event as a note: a note's text as written; another event's own fields, each whole."""
    if e.get("event") == "note":
        text = e.get("text") or ""
    else:
        text = "; ".join("%s: %s" % (f, v) for f, v in e.items() if f not in STAMPS and v not in (None, "")
                         and not (e.get("event") in ("file", "spawn") and f in ("title", "spec")))      # both stand above
    return {"ts": e.get("ts"), "seat": e.get("seat"), "event": e.get("event"), "text": text,
            "owner_said": e.get("ownerSaid"), "by_card": e.get("byCard")}


def _now_text(t=None):
    try:
        from zoneinfo import ZoneInfo
        d = datetime.datetime.fromtimestamp(t, ZoneInfo("America/Los_Angeles")) if t is not None else \
            datetime.datetime.now(ZoneInfo("America/Los_Angeles"))
    except Exception:  # noqa: BLE001 - no zone data: the machine's own clock, named
        d = datetime.datetime.fromtimestamp(t).astimezone() if t is not None else datetime.datetime.now().astimezone()
    return d.strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def _read_prose(item, clone):
    """-> (text, path). No file: "" and the live path; a file that is there and cannot be read raises."""
    rels = [os.path.join("infrastructure", "state", "items", item + ".md"),
            os.path.join("infrastructure", "state", "items", "closed", item + ".md")]
    if not os.path.isdir(os.path.join(clone, "infrastructure", "state", "items")):
        raise RuntimeError("the clone holds no infrastructure/state/items")
    for rel in rels:
        if os.path.isfile(os.path.join(clone, rel)):
            with open(os.path.join(clone, rel), encoding="utf-8") as fh:
                return fh.read(), rel
    return "", rels[0]


def _state(it):
    bits = [str(it.state)]
    if it.wait_until:
        bits.append("waits until %s: %s" % (it.wait_until, it.wait_reason))
    if it.blocked:
        bits.append("blocked: %s%s" % (it.blocked_reason, " (on %s)" % it.blocked_on if it.blocked_on else ""))
    if it.closed_sha:
        bits.append("closed at %s" % it.closed_sha)
    if it.live_broken:
        bits.append("its live promise is broken: %s" % it.live_broken)
    if it.effect:
        bits.append("outcome check: %s" % it.effect)
    return "; ".join(bits)


def _linked(world, it, text):
    """-> the linked items: [{id, state, title, how}], each once."""
    out, seen = [], {it.id}

    def add(iid, how):
        x = world.items.get(str(iid)) if iid else None
        if x is None:       # a run links to its item
            import model
            m = model.RUN_RE.match(str(iid or ""))
            x = world.items.get(m.group("item")) if m else None
        if x is not None and x.id not in seen:
            seen.add(x.id)
            out.append({"id": x.id, "state": x.state, "title": x.title, "how": how})

    cause = world.findings.get(str(it.caused_by), {}).get("from", it.caused_by)
    for iid, how in ((cause, "caused this item"), (it.spawned_by, "spawned this item"),
                     (it.blocked_on, "blocks this item"), (it.superseded_by, "supersedes this item")):
        add(iid, how)
    for iid in it.blocked_also or ():
        add(iid, "blocks this item")
    for x in sorted((x for x in world.items.values() if x.caused_by == it.id), key=lambda x: x.created_index or 0):
        add(x.id, "caused by this item")
    for name in NAME.findall(text or ""):
        add(name, "named in the prose")
    return out


def gather(item, clone):
    """-> the facts of `packet`, as the clone holds them now. A part that cannot be read is None, its cause in `why`."""
    f = {k: None for k in ("state", "title", "prose", "notes", "runs", "linked", "commits", "criteria", "ledger")}
    why = f["why"] = {}
    f["as_of"] = _now_text()
    item, clone = str(item).strip(), os.path.abspath(str(clone))

    def part(names, fn):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 - said in the packet, never guessed at
            for n in names:
                f[n] = None
                why[n] = "%s: %s" % (type(e).__name__, e)

    def prose():
        f["prose"], f["prose_path"] = _read_prose(item, clone)

    def ledger():
        import model
        head = os.path.join(clone, "infrastructure", "state", "ledger", "events.jsonl")
        if not os.path.isdir(os.path.join(os.path.dirname(head), model.SHARD_DIR)):
            raise RuntimeError("the clone holds no ledger")
        evs = model.read_clone(head)
        if not evs:
            raise RuntimeError("the ledger read 0 events")
        world = model.replay(evs)
        it = world.items.get(item)
        f["known"] = it is not None
        if it is None:
            f.update(state="not in the ledger", title="", notes=[], runs=[], linked=[], criteria=[])
            return
        mine = [evs[k] for k in it.history]
        specs = [str(e["spec"]) for e in mine if e.get("event") in ("file", "spawn") and e.get("spec")]
        if f["prose"] is not None:      # a program's filer writes its spec on the event (spawn --spec)
            f["prose"] = "\n".join([f["prose"]] + [s for s in specs if s.strip() not in f["prose"]]).strip("\n")
        notes, quiet = [], 0
        for e in mine:
            if e.get("event") in BOOKKEEPING and not (e.get("ownerSaid") or e.get("byCard")):
                quiet += 1
                continue
            notes.append(_event_note(e))
        f.update(state=_state(it), title=it.title or "", notes=notes, bookkeeping=quiet,
                 runs=[{"ts": r.ts, "result": r.result, "evidence": r.evidence, "config": r.config} for r in it.runs],
                 linked=_linked(world, it, f["prose"]), criteria=[str(c) for c in it.outstanding or ()])

    def commits():
        got = _git(clone, "log", "--extended-regexp", "--grep=\\b%s\\b" % item, "--format=%h%x09%s")
        rows = [ln.partition("\t")[::2] for ln in got.splitlines() if ln.strip()]
        rows = [{"sha": a, "subject": b} for a, b in rows if not b.startswith("ledger:")]
        f.update(commits=rows[:COMMITS], commits_more=len(rows[COMMITS:]))

    def level():
        n = int(_git(clone, "rev-list", "--count", "HEAD..origin/main", "--", "infrastructure/state/ledger").strip())
        at = os.path.join(clone, _git(clone, "rev-parse", "--git-path", "FETCH_HEAD").strip())
        when = ("as it was fetched at %s" % _now_text(os.path.getmtime(at))) if os.path.exists(at) else \
            "as this clone was made (it never fetched)"
        f["ledger"] = ("BEHIND origin/main by %d commit(s) that write the ledger, %s" % (n, when)) if n else \
            "level with origin/main %s" % when

    part(["prose"], prose)
    part(["state", "title", "notes", "runs", "linked", "criteria"], ledger)
    part(["commits"], commits)
    part(["ledger"], level)
    return f


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("item")
    ap.add_argument("--clone", default=REPO)
    ap.add_argument("--budget-chars", type=int, default=BUDGET_CHARS)
    a = ap.parse_args(argv)
    r = packet(a.item, gather(a.item, a.clone), a.budget_chars)
    print(r["text"], end="")
    return 2 if r["could_not_look"] else 0


if __name__ == "__main__":
    sys.exit(main())
