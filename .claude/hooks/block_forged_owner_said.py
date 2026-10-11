#!/usr/bin/env python3
"""PreToolUse hook — a `--owner-said "..."` or bare `--said "..."` quote must be
provable against the transcript, not merely shaped like an instruction.

COVERS TWO FLAG NAMES, ONE TRUST BOUNDARY
==========================================
`--owner-said` is `rimflow`'s own flag. But `./game --said "<words>" <state>`
(which exports `RIMFLOW_OWNER_SAID` and shells out to `rimflow ... --owner-said`
from INSIDE `broadcast.py` — never as a new Bash tool call this hook would see
again) and `apply_blanket_ruling.py --said "<words>"` stamp the identical
`ownerSaid` ledger field from a different flag spelling, and were invisible to
this hook until `OWNER_SAID_FLAG_BYPASS_1` (2026-09-20): a FOUNDRY subagent ran
`./game --said "FOUNDRY closing the beastmechanics verification load" down` —
its own words, not the owner's — and the ledger recorded it as `"seat":"OWNER"`
with that quote as `ownerSaid`, unrefused, because the FLAG regex only ever
matched the literal string `--owner-said`. Both flags are checked identically
below; `--owner-said` never double-matches the bare-`--said` alternative
(the substring `--said` does not appear inside `--owner-said` — the dash before
`said` there is single, not double).

WHY
===
On 2026-09-19T06:27:43Z a FOUNDRY subagent ran
`rimflow claim --seat OWNER --owner-said "autonomous FOUNDRY work"`. Those are
not the owner's words -- they are the agent describing its own situation --
and the flip put LIQUID_SINK_DRAINAGE_1 under OWNER. Undone at `d4a10ee0a`.

`rimflow`'s own `_check_owner_said` validates SHAPE only (rejects a question,
rejects bare assent) -- it cannot tell whether the owner ever said the words,
so any sentence shaped like an instruction passes. The flag is both the
authorization AND the record, so a fabricated one corrupts the one field the
system treats as evidence a boundary was crossed on purpose. This hook adds
the missing check: the quoted text must appear in a turn the OWNER actually
typed, this session.

THE REJECTED APPROACH -- do not re-derive it
==============================================
The first ask was "refuse `--owner-said` from a subagent". MEASURED
2026-09-19: a subagent's environment is byte-identical to its seated parent's
(same `CLAUDE_CODE_SESSION_ID`, same seat env vars, same role file) -- there
is no signal that distinguishes a subagent from its window, so any guard
built on that discriminator refuses the seat itself or nothing at all.
Provenance, not identity, is the only thing that works, and it is strictly
better: it also catches a fabricated quote from the SEATED WINDOW, which the
subagent rule never would.

PreToolUse hooks and this transcript are confirmed live for a subagent's own
Bash calls -- MEASURED 2026-09-19: a subagent's `git add -A` was refused by
`block_blanket_git_stage.py` (a sibling hook on this same matcher) with that
hook's normal message, and a subagent's own `CLAUDE_CODE_SESSION_ID` matched
its parent's exactly. So a subagent and its seat window share one transcript
file, and reading `transcript_path` from the hook payload -- whichever of the
two actually ran the Bash call -- reads that ONE shared file.

WHAT COUNTS AS "THE OWNER TYPED IT"
====================================
A transcript line is `type: "user"` for many reasons: a genuine keystroke, a
tool_result being relayed back in the "user" role, a `<local-command-caveat>`
wrapper, a scheduled/queued wakeup. MEASURED across this project's saved
transcripts: `promptSource` is `"typed"` ONLY for a line the owner actually
typed at the prompt (paired with `origin: {"kind": "human"}` on every sample
checked); every tool-result / caveat / scheduled line reads `promptSource:
None`, and no other harness-observed value ("system", "queued", "sdk") ever
carried a human sentence. So `promptSource == "typed"` is the discriminator
for a CHAT turn.

TYPED WHILE THE AGENT WAS BUSY (OWNER_SAID_GUARD_MIDTURN_BLIND_1, 2026-10-11)
==========================================================================
A sentence he types mid-turn never becomes a `typed` user line. MEASURED over
528 saved transcripts: it lands as an `attachment` of type `queued_command`
(`commandMode: "prompt"`, 703 lines), or later as a `user` line with
`promptSource: "queued"` (661). Every one of those that is his carries
`origin: {"kind": "human"}`. The same queue also carries a peer session's relay
(`kind: "peer"`, `isMeta`, 136) and task notifications. Those words are not his,
so only `kind == "human"` is read. Ignoring these shapes refused his real
quotes as forged, three times on record (lessons 2026-09-24, 09-26, 10-04).

HOW A QUOTE MATCHES (adversarial review, 2026-10-11)
===================================================
At 65de8e2bf a quote passed if it was a SUBSTRING of every owner text joined
together, so 19 of 37 attacks passed: one letter, "...", a mid-word slice, a
sentence spliced across two turns or across a card question we wrote, harness
and hook prose inside card results, text he pasted, a dropped "not", `"$A"`,
`--owner` (an argparse abbreviation), a python argv list, RIMFLOW_OWNER_SAID.
Now a quote must be WHOLE WORDS inside ONE owner text (a one-word quote must
BE the whole text), not straight after a negator, literal or resolvable from
a literal assignment in the same command. Report and harness:
`Transient/owner_said_guard_review_20261011.md`.

SECOND SOURCE: TEXT HE TYPED INTO A QUESTION CARD (owner, 2026-09-22)
=====================================================================
Owner ruling, verbatim: *"Please include user text through a question card as a
valid owner-said line in the process definitions. That is the intention."*

An `AskUserQuestion` answer comes back as a `tool_result` in the "user" role
with `promptSource: None`, so the chat-turn rule above excluded it and a real
ruling he typed into a card was refused. MEASURED shape, this project's
transcript 2026-09-22:

    {"type":"tool_result","tool_use_id":"toolu_...",
     "content":"User has answered your questions: \"<Q>\"=\"<A>\"
                user notes: <NOTES>"}

🔴 THE HAZARD, AND WHY THIS IS SUBTRACTIVE RATHER THAN ADDITIVE. That single
string is only PARTLY his. The question text, every option label and every
option description inside it were authored by the ASSISTANT that called the
tool, and `<A>` is usually a verbatim copy of one of those labels. Accepting
the string whole would mean an agent could write any sentence into an option
label, have the owner click it, and then quote it back through
`--owner-said` as his words -- reintroducing the exact laundering this file
exists to prevent, and the one CLAUDE.md already records ("a question-card
LABEL is not his words").

So: for each card result we look up the paired `tool_use` block by
`tool_use_id`, collect every string the assistant authored in it (questions,
headers, labels, descriptions, previews), and SUBTRACT those - plus the
harness boilerplate - from the result string. What survives is text only he
could have put there: the `user notes:` body, and a free-text "Other" answer
(which by construction matches no label we wrote). Fragmenting the haystack by
subtraction can only make this check STRICTER, never looser, which is the safe
direction for a guard.

A card whose labels an agent crafted therefore still authorizes nothing, while
a sentence he actually typed into the notes box now does.

This closes the laundering vector the spec named: "a subagent's transcript
contains its own PROMPT as a user turn" -- an Agent-tool call's brief is
authored by the calling ASSISTANT and arrives back as a tool_result, which is
`type: "user"` but `promptSource: None`. It can never pass this check no
matter what an agent puts in it.

NEAR-MISS, DECIDED (do not leave this accidental): the owner said it in an
EARLIER session, not this one -- REFUSED. Only the current transcript file is
read. Scanning every prior session for a matching sentence is unbounded and
would let a stale, out-of-context quote from weeks ago authorize a fresh
action; the refusal message tells the operator to have him repeat it this
session.

Fails OPEN: any parse problem (unreadable transcript, unexpected JSON shape)
allows the call through, because a broken hook must never wedge the session.
Fails CLOSED only on the one case the whole file exists to catch: a
transcript that opens cleanly and genuinely does not contain the quote.
"""
import json
import os
import re
import sys

# Which spellings reach the `ownerSaid` field (OWNER_SAID_GUARD_REVIEW, 2026-10-11):
#   --owner-said, --said (./game, apply_blanket_ruling.py), and
#   RIMFLOW_OWNER_SAID=... , which broadcast.py turns into --owner-said itself;
#   argparse ABBREVIATIONS -- rimflow and apply_blanket_ruling.py keep
#   allow_abbrev, so `--owner "x"` / `--sa "x"` set the same field. Those are
#   only read when the command names that tool: `gh search repos --owner X`
#   is not an authorization;
#   a python argv list, `"--owner-said", "x"`.
_VALUE = (r'(?:["\']\s*,\s*|=|\s+)'   # space, =, or the `", "` of a python list
          r'(?:"((?:[^"\\]|\\.)*)"'   # double-quoted
          r"|'((?:[^'\\]|\\.)*)'"     # single-quoted
          r'|(\S+))')                 # bare token (rare, still checked)
FLAG = re.compile(r'(?:--(?:owner-)?said|\bRIMFLOW_OWNER_SAID)' + _VALUE)
_ABBREVS = (
    (re.compile(r'rimflow|cli\.py'),
     re.compile(r'--o(?:w(?:n(?:e(?:r(?:-(?:s(?:ai?)?)?)?)?)?)?)?' + _VALUE)),
    (re.compile(r'apply_blanket_ruling'), re.compile(r'--sai?' + _VALUE)),
)

# A double-quoted or bare word with an unescaped `$` or backtick is expanded by
# the shell AFTER this hook reads it: `--owner-said "$A"` checks the letter `a`
# while rimflow records whatever $A holds. A `$NAME` is resolved from a literal
# assignment or `for NAME in "..." ...` list in the same command (the common
# `Q="his words"; rimflow ... --owner-said "$Q"`); anything else is refused.
_EXPANDS = re.compile(r'(?<!\\)[$`]')
_REF = re.compile(r'(?<!\\)\$(?:\{(\w+)\}|(\w+))')
_LIT = r'"(?:[^"\\]|\\.)*"|\'[^\']*\''
_ASSIGN = re.compile(r'(?:^|[\s;&|(])(?:export\s+|local\s+)?([A-Za-z_]\w*)=(%s)' % _LIT)
_FOR = re.compile(r'\bfor\s+([A-Za-z_]\w*)\s+in\s+((?:(?:%s)\s*)+)(?:;|\n|\s)\s*do\b' % _LIT)


def _unquote(lit):
    if lit.startswith("'"):
        return lit[1:-1], False
    body = lit[1:-1]
    return body.replace('\\"', '"').replace("\\'", "'"), bool(_EXPANDS.search(body))


def _shell_values(command):
    """-> {NAME: [values]} from literal assignments and for-lists; a value that
    itself expands is recorded as None (unresolvable)."""
    vals = {}
    for m in _ASSIGN.finditer(command):
        v, exp = _unquote(m.group(2))
        vals.setdefault(m.group(1), []).append(None if exp else v)
    for m in _FOR.finditer(command):
        for lit in re.findall(_LIT, m.group(2)):
            v, exp = _unquote(lit)
            vals.setdefault(m.group(1), []).append(None if exp else v)
    return vals


def _expand(raw, vals):
    """-> [(text, unprovable)] for a double-quoted/bare value."""
    if _EXPANDS.search(_REF.sub("", raw)):        # `...`, $(...), $@, a bare $
        return [(raw, True)]
    outs = [raw]
    for m in _REF.finditer(raw):
        cands = vals.get(m.group(1) or m.group(2)) or [None]
        if None in cands or len(outs) * len(cands) > 64:
            return [(raw, True)]
        outs = [o.replace(m.group(0), c, 1) for o in outs for c in cands]
    return [(o.replace('\\"', '"').replace("\\'", "'"), False) for o in outs]

# The matching rules (NEGATORS, SEP, _norm, _proven, card subtraction,
# owner_texts) live in owner_said_provenance.py, shared with the consumers
# (rimflow, broadcast.py, apply_blanket_ruling.py) so the quote is proven again
# where it is USED -- a command-text hook cannot see a script file (A36).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from owner_said_provenance import (  # noqa: E402
    NEGATORS, SEP, _norm, _proven, owner_texts,  # noqa: F401
)


def extract_quotes(command):
    """-> [(quote, unprovable)] where unprovable means the shell will expand it
    into something this hook cannot see."""
    flags = [FLAG] + [rx for tool, rx in _ABBREVS if tool.search(command)]
    vals = _shell_values(command)
    out = []
    seen = set()
    for rx in flags:
        for m in rx.finditer(command):
            if m.start() in seen:
                continue
            seen.add(m.start())
            if m.group(2) is not None:                # single quotes: literal
                out.append((m.group(2), False))
                continue
            raw = m.group(1) if m.group(1) is not None else (m.group(3) or "")
            out.extend(_expand(raw, vals))
    return out




def offence(payload):
    """-> (quote, command) of the first unprovable quote, or None."""
    if payload.get("tool_name") != "Bash":
        return None
    command = (payload.get("tool_input") or {}).get("command") or ""
    quotes = [(q, x) for q, x in extract_quotes(command) if q.strip()]
    if not quotes:
        return None
    transcript_path = payload.get("transcript_path") or ""
    if not transcript_path:
        return None                      # nothing to check against -- fail open
    texts = owner_texts(transcript_path)
    if texts is None:
        return None                      # unreadable transcript -- fail open
    # One segment per owner text, split again at every SEP: a quote must sit
    # inside one of them as whole words (no mid-word, no cross-turn splice).
    segments = [_norm(part) for t in texts for part in t.split(SEP)]
    for q, unprovable in quotes:
        nq = _norm(q)
        if unprovable or not nq or not _proven(nq, segments):
            return q, command
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                         # fail open

    hit = offence(payload)
    if not hit:
        return 0
    quote, command = hit

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked: the quoted %r does not appear in anything the "
                "owner actually typed this session -- neither a chat turn nor "
                "text he typed into a question card.\n\n"
                "The quote must be WHOLE WORDS from ONE thing he typed (not "
                "spliced across turns, not text he pasted), must not drop a "
                "'not'/'never'/'don't' just before it (quote that word too), "
                "and must be literal: a `$` or backtick inside double quotes "
                "is expanded after this check, so use single quotes or a "
                "literal VAR=\"...\" in the same command. One word counts only "
                "if it was his whole message. Merely MENTIONING the flag in "
                "prose? Wrap it in backticks: `--owner-said`.\n\n"
                "NOTE on cards: what he TYPED into one (the notes box, or a "
                "free-text 'Other') counts and is accepted. An option LABEL "
                "he merely clicked does NOT -- we wrote it, so it is our "
                "sentence, not his. Record a click as \"decision taken by "
                "question card\".\n\n"
                "This applies to `--owner-said` (rimflow), `--said` "
                "(./game, apply_blanket_ruling.py) -- same field, same "
                "rule, whichever flag spelled it. The flag is both the "
                "authorization AND the record -- a sentence merely SHAPED "
                "like an instruction is not the owner's words, and the "
                "ledger would record it as his.\n\n"
                "If he really said this:\n"
                "  - have him repeat it in THIS session (a quote from an "
                "earlier session is refused on purpose -- see "
                "block_forged_owner_said.py's NEAR-MISS note), then re-run "
                "the command\n\n"
                "If he did not say it:\n"
                "  - drop the flag and act under your own seat, naming "
                "whose call it is (./game <state> with no --said still "
                "stamps the event as OWNER's, just unattributed)\n\n"
                "See OWNER_SAID_PROVENANCE_GUARD_1 (an agent's own "
                "description of its situation got stamped as the owner's "
                "authorization via --owner-said) and OWNER_SAID_FLAG_BYPASS_1 "
                "(the same thing via --said, which this check now also covers)."
                % quote
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
