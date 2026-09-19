#!/usr/bin/env python3
"""PreToolUse hook — a `--owner-said "..."` quote must be provable against the
transcript, not merely shaped like an instruction.

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
carried a human sentence. So `promptSource == "typed"` is the discriminator.

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
    r'--owner-said(?:=|\s+)'
    r'(?:"((?:[^"\\]|\\.)*)"'      # double-quoted
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


def typed_user_texts(transcript_path):
    """-> list of every string the OWNER actually typed this session, or None
    if the transcript could not be read/parsed at all (caller fails open)."""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except Exception:
        return None
    texts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") != "user" or ev.get("promptSource") != "typed":
            continue
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text") or "")
    return texts


def offence(payload):
    """-> (quote, command) of the first unprovable quote, or None."""
    if payload.get("tool_name") != "Bash":
        return None
    command = (payload.get("tool_input") or {}).get("command") or ""
    if "--owner-said" not in command:
        return None
    quotes = [q for q in extract_quotes(command) if q.strip()]
    if not quotes:
        return None
    transcript_path = payload.get("transcript_path") or ""
    if not transcript_path:
        return None                      # nothing to check against -- fail open
    texts = typed_user_texts(transcript_path)
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
                "Blocked: `--owner-said %r` does not appear in anything the "
                "owner actually typed this session.\n\n"
                "The flag is both the authorization AND the record -- a "
                "sentence merely SHAPED like an instruction is not the "
                "owner's words, and the ledger would record it as his.\n\n"
                "If he really said this:\n"
                "  - have him repeat it in THIS session (a quote from an "
                "earlier session is refused on purpose -- see "
                "block_forged_owner_said.py's NEAR-MISS note), then re-run "
                "the command\n\n"
                "If he did not say it:\n"
                "  - drop --owner-said and act under your own seat, naming "
                "whose call it is\n\n"
                "See OWNER_SAID_PROVENANCE_GUARD_1: on 2026-09-19 an agent's "
                "own description of its situation (\"autonomous FOUNDRY "
                "work\") got stamped as the owner's authorization this way."
                % quote
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
