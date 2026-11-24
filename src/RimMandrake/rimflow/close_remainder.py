#!/usr/bin/env python3
"""close_remainder.py: what a closer's own words say is not built, and whether a ticket already holds it. Pure: no ledger
write, no model. `cli.py close` and `detached_helper.finish` act on it.

Item RIMMANDRAKE_STOP_CLOSE_WHEN_RUN_SAYS_SPEC_PARTS_ARE_NOT_BUILT. Page
design/specs/2026-11-24-close-files-its-remainder/boundary.md.
"""
import re

_UNBUILT = (r"(?:(?:not|never)(?: been)?(?: yet)? (?:built|wired|implemented)"
            r"|un(?:built|wired|implemented)|partial scope|scope:? partial)")
NAMED = re.compile(r"\b%s\b" % _UNBUILT, re.I)
# words that say the opposite: "no part is unbuilt", "nothing was left unbuilt", "0 parts not built", "Not built: none"
DENIED = re.compile(r"\b(?:no|nothing|none|0|zero)\b(?: \w+){0,5}? (?:%s)\b|\b(?:%s)\b[\s*_]{0,4}[:=][\s*_]{0,4}(?:none|nothing|no parts?|0)\b(?! but| except)"
                    % (_UNBUILT, _UNBUILT), re.I)
# a report DECLARES (no agent is there to say it meant something else): a heading "Not built: ..." or "parts ... are not built"
DECLARED = re.compile(r"^[\s>*_#\-\d.)]*(?:(?:left|still|spec|parts?|yet)\s+){0,3}%s\b[^:.]{0,40}:"
                      r"|\b(?:parts?|pieces?) of the (?:spec|ticket|item)\b[^.;:]{0,40}\b%s\b" % (_UNBUILT, _UNBUILT), re.I)
UNTESTED = re.compile(r"\b(?:untested|not tested)\W{0,4}:\W{0,4}(.+?)(?=\.\s|\n|$)", re.I | re.S)
IS_REMAINDER = re.compile(r"remainder|finish|%s" % _UNBUILT, re.I)
_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}\b")
_COMMON = {"with", "from", "that", "this", "have", "into", "only", "when", "never", "each", "item", "test", "tests", "live", "file"}
RUN_ENDED = "DETACHED run "     # finish's own note: the report, read at the run's end and not as the closer's last note
TITLE_WORDS = 400               # danger: one ledger line every replay reads; the whole text is in the note beside it


def named(text):
    """-> the sentences of `text` that name something unbuilt."""
    return [s.strip() for ln in str(text or "").splitlines() for s in re.split(r"(?<=[.;!?])\s+(?=[A-Z`*(\d])", ln)
            if NAMED.search(DENIED.sub(" ", s))]


def declared(report):
    """-> the lines of a run's report that declare unbuilt parts; a heading with nothing after it takes its sub-bullets."""
    lines, out = str(report or "").splitlines(), []
    for k, ln in enumerate(lines):
        if not DECLARED.search(DENIED.sub(" ", ln)):
            continue
        if re.search(r":[\s*_]*$", ln):
            for sub in lines[k + 1:]:
                if sub.strip() and not re.match(r"\s+\S|[-*] ", sub):
                    break
                ln += " " + sub.strip()
        out.append(" ".join(ln.split()))
    return out


def _words(text):
    out = set()
    for w in re.findall(r"[a-z]{4,}", str(text or "").lower()):
        if w not in _COMMON:
            out.add(re.sub(r"(?:ing|s)$", "", w))
    return out


def untested(text, spec):
    """-> the parts after `Untested:` that share two words with one line of the item's spec."""
    lines = [_words(b) for b in re.split(r"\n\s*(?=[-*] )|\n\s*\n", str(spec or ""))]
    out = []
    for m in UNTESTED.finditer(str(text or "")):
        for part in re.split(r"[,;]| and ", m.group(1)):
            have = _words(part)
            if part.strip() and any(len(have & ln) >= 2 for ln in lines):
                out.append(part.strip())
    return out


def last_start(evs, iid):
    """-> the index of the item's last start (or reopen, or file): what came before it is another run's."""
    at = 0
    for k, e in enumerate(evs):
        if e.get("id") == iid and e.get("event") in ("file", "start", "reopen"):
            at = k
    return at


def last_note(evs, iid):
    """-> the text of the item's last note since its last start, or ""."""
    text = ""
    for e in evs[last_start(evs, iid):]:
        if e.get("id") == iid and e.get("event") == "note" and not str(e.get("text") or "").startswith(RUN_ENDED):
            text = str(e.get("text") or "")
    return text


def holds(items, iid, cand):
    """-> whether `cand` can hold a remainder of `iid`: an item that was filed, is not `iid` and is not dropped."""
    it = items.get(cand)
    return it is not None and cand != iid and it.state != "dropped"


def ids(text):
    """-> the item ids that `text` names."""
    return _ID.findall(str(text or ""))


def owed(iid, parts, items):
    """-> the parts whose own words name no ticket that can hold them."""
    return [p for p in parts if not any(holds(items, iid, c) for c in ids(p))]


def linked(iid, evs, items):
    """-> the id of a ticket caused by the item since its last start that says it holds a remainder, or ""."""
    for e in evs[last_start(evs, iid):]:
        if (e.get("event") == "file" and e.get("caused_by") == iid and holds(items, iid, e.get("id"))
                and IS_REMAINDER.search(("%s %s" % (e.get("id"), e.get("title") or "")).replace("_", " "))):
            return e["id"]
    return ""


def name(iid, taken):
    """-> a free item name for the remainder: whole words, 64 characters at most, as `rimflow namecheck` reads it."""
    words = [w for w in iid.split("_") if w][1:]
    for tail in (["UNBUILT", "PARTS"], ["UNBUILT", "PARTS", "AGAIN"]):
        room = 9 - 2 - len(tail)
        for at in range(max(1, len(words))):
            keep = words[at:at + room]
            while keep and len("_".join(["RIMMANDRAKE", "FINISH"] + keep + tail)) > 64:
                keep.pop()
            n = "_".join(["RIMMANDRAKE", "FINISH"] + keep + tail)
            if n not in taken:
                return n
    raise ValueError("no free name for a remainder of %s" % iid)


def to_file(iid, seat, parts, taken):
    """-> the `file` event of the remainder that a program files."""
    return {"seat": seat, "event": "file", "id": name(iid, taken), "title": title(iid, parts), "kind": "task",
            "needs": "offline", "target": "v1", "for": "BENCH", "caused_by": iid}


def title(iid, parts):
    t = " | ".join(" ".join(p.split()) for p in parts)
    if len(t) > TITLE_WORDS:
        t = t[:TITLE_WORDS].rsplit(" ", 1)[0] + " ... (whole text in its note)"
    return "Remainder of %s, which closed with parts that its closer named as not built: %s" % (iid, t)


def repair(iid, seat, parts, free):
    """-> the answer to a launched run: what its words named, the filled file command, and the close again."""
    return ("close: %s: your own words name spec parts that are not built (or untested), and no ticket holds them:\n%s\n\n"
            "A check that passes on less than the spec does not finish the spec. Build the parts now, in this run; or file "
            "them as ONE ticket and close again with the same command:\n\n"
            "    python3 src/RimMandrake/rimflow/cli.py file %s --for BENCH --title \"Remainder of %s: <each unbuilt part, "
            "and its acceptance test>\" --caused-by %s --seat %s --why \"unbuilt remainder\" --publish\n\n"
            "Filed already: add `--remainder <its id>`. Nothing is unbuilt (the parts are built, or the spec does not ask "
            "for them): add `--no-remainder \"<why>\"`. Nothing changed: the item is as it was."
            % (iid, "\n".join("  - %s" % p for p in parts), free, iid, iid, seat))
