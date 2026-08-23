#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""block_paste_handoff.py — a `Stop` hook. The seat does not hand the owner a
command to paste; it RUNS it.

🔴 OWNER, 2026-08-22, verbatim:
    "From now on, for ALL agents, instead of asking me to type ! python for me,
     JUST RUN IT YOURSELF, ok? No more of this cut-paste weirdness. Make this true."

⭐ "MAKE THIS TRUE" IS WHY THIS FILE EXISTS. The rule was already written — the
2026-08-22 upgrade to `~/.claude/CLAUDE.md` and `POLICY.md`'s *"Stop handing him
`! RIMFLOW_SEAT=OWNER python3 …` lines to paste"* both said it — and a seat handed
him one anyway, twice, in the session where he issued this. Doctrine that only
discipline enforces decays; this is the enforcement.

HOW IT WORKS. On `Stop` the harness gives us the transcript. We read the seat's
FINAL message and look for a line that is a `!`-prefixed shell handoff — the Claude
Code idiom for "paste this into your own prompt". Finding one, we `block`, which
does not discard the turn: the seat is handed the reason and continues, and the
right continuation is to run the command and report the outcome.

⛔ WHAT IT DELIBERATELY DOES NOT DO. It does not read intent, and it does not fire
on prose like "you could run X" — only on the `!` idiom, which is unambiguous. A
seat determined to hand over a task can still do it in words; this catches the form
he actually complained about, and catching that form is the whole ask.

✅ THE CARVE-OUT, and there is exactly one class. Some acts ARE his:
`./game up|down|loading` is his announcement (he types it, `game` is his verb), and
an interactive login cannot be run by us at all. Lines that are plainly his are let
through — see OWNERS_OWN below.

⚠️ NEVER LOOPS. `stop_hook_active` is set when we are already inside a block-driven
continuation; we exit clean on it, so a seat that blocks twice is impossible.
"""
import json
import os
import re
import sys

# ✅ Commands that are genuinely the owner's to type. Matched against the command
# text after the `!`. Keep this list SHORT — every entry is a hole in the rule.
OWNERS_OWN = (
    re.compile(r"^\.?/?game\b"),                     # ./game up|down|loading — his verb
    re.compile(r"\bbroadcast\.py\b"),                # OWNER ONLY by ruling
    re.compile(r"\b(gcloud|aws|az|gh)\s+auth\b"),    # interactive login, not runnable by us
    re.compile(r"\bssh-add\b|\bpasswd\b|\bsudo\b"),  # needs a human at a prompt
)

# The Claude Code paste idiom: a line that is nothing but `!` + a command.
BANG = re.compile(r"^\s*!\s*(\S.*)$")


def last_assistant_text(path):
    """-> the text of the final assistant message, or '' if unreadable.

    ⚠️ Never raises. A hook that dies on an unexpected transcript shape would
    block every turn in the session, which is far worse than missing one paste.
    """
    text = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except Exception:
        return ""
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") != "assistant":
            continue
        content = (ev.get("message") or {}).get("content") or []
        if isinstance(content, str):
            return content
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text.append(block.get("text") or "")
        return "\n".join(text)
    return ""


def offending(text):
    """-> the first `!` handoff line that is NOT the owner's own act, else None."""
    for raw in text.splitlines():
        m = BANG.match(raw)
        if not m:
            continue
        cmd = m.group(1).strip().lstrip("`").strip()
        # `!` also starts ordinary prose ("!important", "!= 3"); require something
        # that looks like a command — a path, an executable, or an env assignment.
        if not re.match(r"^([A-Za-z_][A-Za-z0-9_]*=|\.?/|[A-Za-z][\w.-]*\s)", cmd):
            continue
        if any(p.search(cmd) for p in OWNERS_OWN):
            continue
        return cmd
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    # ⚠️ Already inside a continuation we caused. Never block twice.
    if payload.get("stop_hook_active"):
        return 0
    transcript = payload.get("transcript_path") or ""
    if not transcript or not os.path.exists(transcript):
        return 0
    cmd = offending(last_assistant_text(transcript))
    if not cmd:
        return 0
    reason = (
        "⛔ You handed the owner a command to paste:\n\n    %s\n\n"
        "🔴 He ruled that out, 2026-08-22, verbatim: \"instead of asking me to type "
        "! python for me, JUST RUN IT YOURSELF, ok? No more of this cut-paste "
        "weirdness. Make this true.\"\n\n"
        "✅ RUN IT NOW and report the outcome in one line.\n"
        "✅ If a guard refuses YOU, that is not a task for HIM — find the flag or "
        "seat override. In rimflow that is `--owner-said \"<his verbatim words>\"`, "
        "which records his authorization on the event.\n"
        "✅ Only if the act is genuinely his — his hands, his eyes, his account, or "
        "an authorization he has not given — ask him a QUESTION in words, not a "
        "command line.\n\n"
        "Full rule: ~/.claude/CLAUDE.md, \"RUN IT YOURSELF\"." % cmd[:200]
    )
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
