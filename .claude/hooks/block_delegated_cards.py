#!/usr/bin/env python3
"""PreToolUse/AskUserQuestion hook - refuse a card whose ONLY questions are in a class the owner delegated.

Item CARDS_ENFORCE_DELEGATED_CLASSES_STOP. design/RimMandrake/delegation_policy.md:
  s1 `scope`   - work order, which item next, helper count, whether to continue / start now or later
  s2.4 `twin`  - applying an existing ruling to a case it does not name (campaign copy, sister biome, sibling def)
Measured: 29 ordering cards (81% agreement), ~235 typed go-aheads, 9 twin cards (8 yes) in 3 weeks.

False positives are the only way this hook does harm, so it refuses only when
  * EVERY question in the call matches a delegated class, AND
  * nothing in the payload carries a s2 trigger (north star, irreversible on others' work, kept art, his rulings
    changing, outward/paid acts, flyer live tests), AND
  * no question carries the override marker [owner-asked] (he asked to be asked).
Exit 2 blocks (this machine runs bypassPermissions); anything unparseable exits 0.

    python3 .claude/hooks/selftest_block_delegated_cards.py
"""
import json
import re
import sys

OVERRIDE = re.compile(r"\[owner-asked\]", re.I)

CLASSES = {
    "scope": [
        # order / which next / which first
        r"\b(what|which)\b[^?]{0,60}\b(first|next)\b",
        r"\bwhat'?s? next\b|\bwhat next\b|\bnext build\b|\bbuild order\b|\b\w+ order\b|\bin what order\b",
        r"\b(which|what)\b[^?]{0,50}\b(should|shall|do|will|would)\b (i|we)\b[^?]{0,30}\b(build|drive|start|do|take|work on|tackle|commission|run)\b",
        r"\bwhich\b[^?]{0,40}\bto (build|commission|start|do|work on|tackle)\b",
        r"\b(priority|prioriti[sz]e|sequence|sequencing)\b",
        # helper count
        r"\bhow many (helpers?|agents?|subagents?|slots?|seats?|workers?|builders?)\b",
        r"\b(helpers?|agents?|subagents?)\b[^?]{0,40}\b(at once|in parallel|working at once|concurrently)\b",
        r"\bwho builds\b",
        # continue / start / now or later
        r"\b(should|shall|may|can|want me to|do you want me to|would you like me to)\b[^?]{0,20}\b(i|we)?\s*(continue|keep going|proceed|go ahead|carry on|start (now|building|redrawing|on)|begin)\b",
        r"\b(may|can|should) (we|i) start\b",
        r"\b(now|today|this sprint) or (later|next|tomorrow|after)\b|\bnow or later\b|\bwhen (should|do|shall)\b[^?]{0,30}\b(build|start|run|do|file|begin)\b|\b\w+ when\?$",
        r"\bdoes it join the sprint\b|\bjoin the (next )?sprint\b|\bshape should the next sprint\b|\bahead of the sprint\b|\bwhat now\?",
    ],
    "twin": [
        r"\b(twins?|sibling|sister|campaign copy|counterpart)\b",
        r"\b(rut|rsw|rm)_ twins?\b",
        r"\b(does|do) (this|that|the|your|'?all)\b[^?]{0,50}\b(ruling|rule|cut|decision)\b[^?]{0,20}\b(apply|extend|include|cover)\b",
        r"\bdoes (the|this|that|your)[^?]{0,40}\b(rule|ruling)\b[^?]{0,30}\b(extend|apply)\b",
        r"\b(extend|apply|carry)\b[^?]{0,30}\b(to|onto)\b[^?]{0,30}\b(the same|its|their|both|the other|also)\b",
        r"\b(ban|cut|drop|remove|retire) (it|them|that) too\b",
        r"\bdoes '?all [\w ]+'? include\b",
    ],
}
CLASSES = {k: [re.compile(p, re.I) for p in v] for k, v in CLASSES.items()}

# s2 triggers: any hit anywhere in the payload means the call is not purely delegated.
TRIGGERS = [re.compile(p, re.I) for p in [
    r"north[- ]?star",
    r"force[- ]?push|reset --hard|\bpurge\b|re-?freeze|frozen",
    r"\bkept\b|\bkeep\b[^?]{0,15}\b(art|picture|version)|owner[- ]kept|newest mark|\bmarks?\b",
    r"standing ruling|overturn|reinterpret|change what (it|the ruling) says|\bcontradict|canon\b",
    r"workshop|publish|\bpaid?\b|\bpay\b|spend|purchase|\bbuy\b|\bmoney\b|\bsubscription|plan usage|\blogin\b|log in|credential|\bupload",
    r"flyer|flight|\bfly\b|human present",
    r"delete|\bdrop\b[^?]{0,20}(work|item)|irreversible|not ours|someone else",
    r"\bbroadcast\b|\bbridge\b",
    r"\bsteam\b|\bpush\b",
]]


def question_texts(payload):
    ti = (payload or {}).get("tool_input") or {}
    qs = ti.get("questions")
    if not isinstance(qs, list):
        return []
    return [q for q in qs if isinstance(q, dict)]


def classify(text):
    """Return the delegated class a question text falls in, or None."""
    for cls, pats in CLASSES.items():
        if any(p.search(text) for p in pats):
            return cls
    return None


def verdict(payload):
    """(classes, reason) -> reason is None when the call is allowed."""
    qs = question_texts(payload)
    if not qs:
        return [], None
    blob = json.dumps(payload.get("tool_input"), ensure_ascii=False)
    if OVERRIDE.search(blob):
        return [], None
    classes = []
    for q in qs:
        text = " ".join(str(q.get(k) or "") for k in ("header", "question"))
        c = classify(text)
        if c is None:
            return [], None
        classes.append(c)
    if any(t.search(blob) for t in TRIGGERS):
        return [], None
    return sorted(set(classes)), True


def message(classes):
    lines = ["Blocked: every question on this card is a class the owner already DELEGATED "
             "(design/RimMandrake/delegation_policy.md)."]
    if "scope" in classes:
        lines.append("  - `scope` (s1): work order, which item next, helper count, continue/start now or later. "
                     "29 such cards in 3 weeks were answered with the recommended choice 81% of the time.")
    if "twin" in classes:
        lines.append("  - `twin` (s2.4): applying an existing ruling to a case it does not name (campaign copy, "
                     "sister biome, sibling def). 8 of 9 such cards were yes; changing what a ruling SAYS is still his.")
    lines.append("Decide it yourself, log it `rimflow note <ID> --why \"delegated: %s\" --text \"<the decision>\"`, "
                 "and list it in the daily digest (policy s3)." % "/".join(classes))
    lines.append("If this is NOT really that class (a north star, kept art, his rulings changing, an outward or paid act, "
                 "a flyer live test), say so in the question text. If he asked to be asked, put [owner-asked] in the "
                 "question text. Check: CARDS_ENFORCE_DELEGATED_CLASSES_STOP.")
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if (payload.get("tool_name") or "AskUserQuestion") != "AskUserQuestion":
        return 0
    try:
        classes, hit = verdict(payload)
    except Exception:
        return 0
    if hit:
        sys.stderr.write(message(classes) + "\n")
        return 2
    import block_owner_doc_wsl_paths as OWNER_DOC
    OWNER_DOC.refuse(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
