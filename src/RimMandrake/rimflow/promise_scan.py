#!/usr/bin/env python3
"""promise_scan.py: the Conductor's untracked promises in a reply (RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL,
design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E2, advisory first: nothing here blocks a turn).

WHY. 6 of the 9 debts a restarting Conductor lost or paid late were promises written as prose in an ordinary reply
("When one of those slots frees I will launch …"), with no item saying the Conductor owed the act (spec §2).

    python3 src/RimMandrake/rimflow/promise_scan.py --text-file F [--owed-ids ID,ID]
        prints `PROMISE: <sentence>` per untracked promise; exit 1 if any, 0 if none, 2 the file could not be read

A promise is a sentence in which the Conductor commits itself to a future act or leaves one of its own acts unfinished
("I will / I'll …", "The next window will / should …", "This one is mine", "… not launched / never written / still
owed / I have not ruled"), or a question that ends the reply. It is tracked, and not reported, only when the sentence
names an open owed id, names the item an open owed item acts on (its caused_by), or holds most of an open owed
item's title words (`covered`). A target item's id alone, with no owed item on it, does not track it (the T16 loss
named its item and was still lost).
Quoted text is not the Conductor's: a `>` block and the wake's `<<< … >>>` reprint of the old reply are dropped first.

Reader: .claude/hooks/conductor_goodbye.py prints the last reply's hits on the next prompt. A window killed for its size
has no next prompt: the next window's wake prints its last reply whole (seat_restart.py wake).
"""
import argparse
import re
import sys

PROMISE = re.compile(
    r"\bI\s+will\b|\bI['’]ll\b|\bthe\s+next\s+window\s+(?:will|should)\b|\bthis\s+one\s+is\s+mine\b"
    r"|\bnot\s+(?:yet\s+)?launched\b|\bnever\s+written\b|\bstill\s+owed\b|\bI\s+have\s+not\s+ruled\b",
    re.I)
REPRINT = re.compile(r"<<<.*?>>>", re.S)          # the wake's reprint of the old window's reply
SPLIT = re.compile(r"(?<=[.!?])[\"'”)\]*_]*\s+")
# a period that ends one of these is not a sentence's end: "I will ask Dr. Smith …" is one sentence
# a period that ends one of these is not a sentence's end: "I will ask Dr. Smith …" is one sentence. Case-sensitive, and
# no word that also ends sentences ("yes or no.", "etc.", "4 p.m."): a missed split only joins two sentences, a wrong
# join lets one sentence's owed id hide the other's promise (Codex's second look, 2026-11-18)
ABBREV = re.compile(r"(?:^|[\s(])(?:Dr|Mr|Mrs|Ms|St|Jr|Sr|Fig|vs|e\.g|i\.e)\.[\"'\u201d)\]*_]*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
BULLET = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
ID = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]{2,}(?![A-Za-z0-9_])")


def sentences(text):
    """-> [sentence] of the reply's own words, in order: quotes and reprints dropped, one line or bullet never joined to
    the next paragraph."""
    text = REPRINT.sub(" ", text or "")
    out = []
    para = []

    def flush():
        if para:
            joined = []
            for x in (x for x in SPLIT.split(" ".join(para)) if x.strip()):
                if joined and ABBREV.search(joined[-1]):      # rejoin a split made at an abbreviation's period
                    joined[-1] += " " + x
                else:
                    joined.append(x)
            out.extend(x.strip() for x in joined)
            para.clear()

    fence = None                    # the open fence (``` or ~~~, its length): only the same kind, as long or longer, closes
    for line in text.splitlines():
        m = FENCE.match(line)
        if m and fence is None:
            fence = m.group(1)
            flush()
            continue
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not line.strip()[len(m.group(1)):]:
            fence = None
            continue
        if fence is not None or line.lstrip().startswith(">"):
            flush()
            continue
        if not line.strip():
            flush()
            continue
        if BULLET.match(line):
            flush()
            line = BULLET.sub("", line)
        para.append(line.strip())
    flush()
    return out


WORD = re.compile(r"[a-z0-9]+")
STOP = frozenset("a an and are as at be by for from has have i in is it its me my of on or our that the this to was we "
                 "will with you your".split())
COVER_SHARE = 0.6       # a sentence holding this share of an owed title's content words is that act
COVER_MIN = 3           # ... and at least this many of them (a two-word title would match any sentence)


def _content(text):
    return {w for w in WORD.findall(str(text or "").lower()) if w not in STOP and len(w) > 2}


def covered(sentence, owed_items):
    """-> the open owed id that covers `sentence`, or None. owed_items: {owed id: (title, caused_by)}. A sentence is
    covered when it names an owed item's caused_by item, or holds most of an owed title's content words: an open owed
    item already tracks that act, and saying so again is noise (owner 2026-11-20: "The system should not be in our
    way."; RIMMANDRAKE_STOP_GATES_DEMANDING_OWNER_WORDS_HE_ALREADY_SPOKE). Pure."""
    ids = set(ID.findall(sentence))
    words = _content(sentence)
    for oid, (title, caused_by) in sorted((owed_items or {}).items()):
        if caused_by and caused_by in ids:
            return oid
        t = _content(title)
        shared = len(t & words)
        if t and shared >= COVER_MIN and shared >= COVER_SHARE * len(t):
            return oid
    return None


def scan(text, owed_ids=(), owed_items=None):
    """-> [sentence]: the promises in `text` that name no id in `owed_ids` and that no open owed item covers
    (`covered`, owed_items {id: (title, caused_by)}), in order. Pure."""
    owed = set(owed_ids or ()) | set(owed_items or ())
    ss = sentences(text)
    hits = []
    for i, s in enumerate(ss):
        closing_question = i == len(ss) - 1 and s.rstrip("*_`)\"'” ").endswith("?")
        if not (PROMISE.search(s) or closing_question):
            continue
        if owed & set(ID.findall(s)) or covered(s, owed_items):
            continue
        hits.append(s)
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="the untracked promises in a reply")
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--owed-ids", default="", help="comma-separated open owed ids (a sentence naming one is tracked)")
    a = ap.parse_args(argv)
    try:
        with open(a.text_file, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print("promise_scan could not look: %s unreadable (%s)" % (a.text_file, e))
        return 2
    hits = scan(text, [i.strip() for i in a.owed_ids.split(",") if i.strip()])
    for h in hits:
        print("PROMISE: %s" % h)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
