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
import re
import sys

FLAG = re.compile(
    r'--(?:owner-)?said(?:=|\s+)'  # --owner-said (rimflow) or bare --said
    r'(?:"((?:[^"\\]|\\.)*)"'      # (./game, apply_blanket_ruling.py)
    r"|'((?:[^'\\]|\\.)*)'"        # single-quoted
    r'|(\S+))'                     # bare token (rare, still checked)
)


def _norm(s):
    """Lowercase, strip punctuation, collapse space -- mirrors rimflow's own
    `_norm_said` so 'Yes!' and 'yes' (and a quote reflowed across two lines
    in the transcript JSON) compare equal."""
    return " ".join("".join(c for c in s.lower() if c.isalnum() or c.isspace()).split())


def extract_quotes(command):
    out = []
    for m in FLAG.finditer(command):
        raw = m.group(1) or m.group(2) or m.group(3) or ""
        out.append(raw.replace('\\"', '"').replace("\\'", "'"))
    return out


ASK_TOOL = "AskUserQuestion"

# Harness scaffolding inside a card-result string. Subtracted alongside the
# assistant's own strings so that only the owner's typing survives.
CARD_BOILERPLATE = (
    "User has answered your questions:",
    "User has answered your question:",
    "You can now continue with the user's answers in mind.",
    "user notes:",
)


def _authored_strings(tool_input):
    """-> every string in an AskUserQuestion call the ASSISTANT wrote.

    These can never authorize anything: an agent picks its own labels, so a
    label the owner merely CLICKED is not a sentence he said."""
    out = []
    for q in (tool_input or {}).get("questions") or []:
        if not isinstance(q, dict):
            continue
        out.append(q.get("question") or "")
        out.append(q.get("header") or "")
        for opt in q.get("options") or []:
            if isinstance(opt, dict):
                out.append(opt.get("label") or "")
                out.append(opt.get("description") or "")
                out.append(opt.get("preview") or "")
    return [s for s in out if isinstance(s, str) and s.strip()]


def _result_body(block):
    """Card results carry `content` as a str, or as text blocks in some harness
    versions. Anything else yields '' (that source simply contributes nothing,
    which fails CLOSED for it -- the safe direction)."""
    body = block.get("content")
    if isinstance(body, str):
        return body
    if isinstance(body, list):
        return "\n".join(
            b.get("text") or ""
            for b in body
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _strip_authored(body, authored):
    """Remove assistant-authored text and harness boilerplate from a card
    result, leaving only what the owner typed.

    Longest-first so a label that contains a shorter label is removed whole.
    Replacement is a NEWLINE, never '': splicing two surviving fragments
    together could otherwise manufacture a sentence nobody ever typed."""
    out = body
    for s in sorted(authored, key=len, reverse=True):
        out = out.replace(s, "\n")
    for s in CARD_BOILERPLATE:
        out = out.replace(s, "\n")
    return out


def owner_texts(transcript_path):
    """-> list of every string the OWNER actually typed this session -- chat
    turns plus what he typed into question cards -- or None if the transcript
    could not be read/parsed at all (caller fails open).

    One forward pass: a tool_use always precedes its tool_result in the file,
    so AskUserQuestion calls are known by the time their answers arrive."""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except Exception:
        return None
    texts = []
    authored_by_id = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        typ = ev.get("type")
        content = (ev.get("message") or {}).get("content")

        if typ == "assistant":
            if isinstance(content, list):
                for block in content:
                    if (
                        isinstance(block, dict)
                        and block.get("type") == "tool_use"
                        and block.get("name") == ASK_TOOL
                    ):
                        authored_by_id[block.get("id")] = _authored_strings(
                            block.get("input")
                        )
            continue

        if typ != "user":
            continue

        if ev.get("promptSource") == "typed":
            # A real chat turn: every word of it is his.
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text") or "")
            continue

        # Not a typed chat turn. The only other admissible source is the answer
        # to a card WE called -- and only the part of it he typed.
        if isinstance(content, list):
            for block in content:
                if not (isinstance(block, dict) and block.get("type") == "tool_result"):
                    continue
                authored = authored_by_id.get(block.get("tool_use_id"))
                if authored is None:
                    continue          # not a card result -- ordinary tool output
                texts.append(_strip_authored(_result_body(block), authored))
    return texts


def offence(payload):
    """-> (quote, command) of the first unprovable quote, or None."""
    if payload.get("tool_name") != "Bash":
        return None
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not FLAG.search(command):
        return None
    quotes = [q for q in extract_quotes(command) if q.strip()]
    if not quotes:
        return None
    transcript_path = payload.get("transcript_path") or ""
    if not transcript_path:
        return None                      # nothing to check against -- fail open
    texts = owner_texts(transcript_path)
    if texts is None:
        return None                      # unreadable transcript -- fail open
    haystack = _norm("\n".join(texts))
    for q in quotes:
        if _norm(q) not in haystack:
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
