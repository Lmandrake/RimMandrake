#!/usr/bin/env python3
"""spend_talk: take the sentences that state spend, tokens, a budget or an account level out of text a launched agent
will read (owner 2026-11-16: no launched agent is told its spend).

Used where text that a person wrote for a person reaches a brief: a card's picked description
(RIMMANDRAKE_STRIP_SPEND_TALK_FROM_CARD_BRIEFS_HAND_CUT: "keeps the accounts alive to Wednesday" went through on the
Explosive Knockback rescue) and a run's own result text quoted into its continuation's header.

A card's "Costs:" line is a trade-off, not money: "cost" alone is not spend talk, and "spent" alone is not either
("no trial is spent"). A dollar, token or percent-left figure is, wherever it stands.

A dropped sentence keeps each "needs X" it states (card_capture.consequences: work owed), so a consequence is never
lost with the spend words around it.
"""
import re

SPEND = re.compile(
    r"\$\s?\d"
    r"|\b\d[\d,.]*\s*(?:k|m|million)?\s*(?:weighted(?:[_ ]v\d)?\s+)?tokens?\b"
    r"|\bweighted[_ ](?:v\d\b|tokens?\b)"
    r"|\b(?:usd|dollars?)\b"
    r"|\b\d+(?:\.\d+)?\s*%\s*(?:left|remaining|used|of\s+(?:the\s+|its\s+|his\s+)?(?:weekly|5-hour|five-hour|account|quota|cap|budget))"
    r"|\b(?:spend|spending|budgets?|quota|runway)\b"     # not "cost" (a card's "Costs:" is a trade-off) nor "spent"
    r"|\b(?:spend|budget|token|cost)\s+(?:cap|ceiling|stop|limit)s?\b"
    r"|\baccounts?\b[^.;!?\n]{0,60}\b(?:alive|left|level|levels|reset|resets|quota|runway|dark)\b"
    r"|\b(?:steven|lukas|system)(?:'s)?\s+account\b",
    re.I)
NEEDS = re.compile(r"\bneeds?\s+((?:to\s+)?[a-z0-9][\w'+-]*(?:\s+[\w'+-]+){0,5}?)(?=\s*(?:[,.;:)]|\band\b|\bor\b|$))",
                   re.I)
_SPLIT = re.compile(r"(?<=[.!?;])\s+|\n")


def is_spend(sentence):
    return bool(SPEND.search(sentence or ""))


def strip(text):
    """-> text with every spend sentence removed; a removed sentence's "needs X" phrases stay, each as its own
    sentence. Line breaks between kept sentences are kept as single spaces within a line."""
    out_lines = []
    for line in (text or "").split("\n"):
        kept = []
        for s in _SPLIT.split(line):
            if not s.strip():
                continue
            if not is_spend(s):
                kept.append(s.strip())
                continue
            for m in NEEDS.finditer(s):
                phrase = "needs " + m.group(1).strip()
                if not re.match(r"needs (no|nothing|none|not)\b", phrase, re.I):
                    kept.append(phrase + ".")
        if kept or not line.strip():
            out_lines.append(" ".join(kept))
    return "\n".join(out_lines).strip("\n")
