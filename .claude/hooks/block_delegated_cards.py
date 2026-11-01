#!/usr/bin/env python3
"""PreToolUse/AskUserQuestion hook - refuse a card whose ONLY questions are in a class the owner delegated.

Item CARDS_ENFORCE_DELEGATED_CLASSES_STOP. design/RimMandrake/delegation_policy.md:
  s1 `scope`   - work order, which item next, helper count, whether to continue / start now or later
  s2.4 `twin`  - applying an existing ruling to a case it does not name (campaign copy, sister biome, sibling def)
Measured: 29 ordering cards (81% agreement), ~235 typed go-aheads, 9 twin cards (8 yes) in 3 weeks.

False positives are the only way this hook does harm, so it refuses only when
  * EVERY question in the call matches a delegated class, AND
  * no ask or option carries a s2 trigger (north star, irreversible on others' work, kept art, his rulings
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
        r"^(?!\s*(when|if)\b[^,]*,)(?!.*\bhappen\b).*\b(what|which)\b[^?]{0,90}\b(first|next)\b(?! (\w+ing|version|time|case)\b)",
        r"\bwhat'?s? next\b|\bwhat next\b|\bnext build\b|\bbuild order\b|\b\w+ order\b|\bin what order\b",
        r"\b(which|what)\b(?![^?]{0,25}\b(version|layout|look|design|variant|style|form|approach|way|model)\b)[^?]{0,50}\b(should|shall|will|would)\b (i|we)\b[^?]{0,30}\b(build|drive|start|do(?! with\b| about\b)(?!\?)|take|work on|tackle|commission|run)\b",
        r"\b\w+ next\??$",
        r"\b(day|night|week|sprint|shift) shape\b",
        r"\bwhen (should|do|shall|can|will)\b[^?]*\b(build|built|take|start|run|do|go|come out|get|file|begin)\b|^\s*when (?!(may|can|should|do|does|did|is|are|will|would|a|an|the)\b)\w+\b[^,?]{0,40}\?$",
        r"\bhow to staff\b|\baim for\b[^?]{0,20}\bthis (week|sprint|cycle)\b",
        r"\b(wait|hold) for\b[^?]{0,40}\bor come first\b|\bor (come|go) first\b",
        r"\bshould (i|we)\b[^?]{0,30}\b(build|start|queue|do)\b[^?]{0,30}\b(now|first|next|this (cycle|sprint|week))\b",
        r"\bshould (we|i) build this (cycle|sprint|week)\b|^(?!\s*(how|what)\b).*\bthis (cycle|sprint)\?$",
        r"\bwho builds\b|\bwhat should be built first\b",
        r"\b(do|should|shall) (we|i) build\b[^?]*\bnow\?",
        r"\bwhich\b[^?]{0,40}\bto (build|commission|start|do|work on|tackle)\b",
        r"\b(prioriti[sz]e|sequence|sequencing|what priority|priority order)\b",
        # helper count
        r"\bhow many (helpers?|agents?|subagents?|slots?|seats?|workers?|builders?)\b",
        r"\b(helpers?|agents?|subagents?)\b[^?]{0,40}\b(at once|in parallel|working at once|concurrently)\b",
        # continue / start / now or later
        r"^(?!.*\bwhich\b)(?!\s*(how|what|why)\b).*\b(should|shall|may|can|want me to|do you want me to|would you like me to)\b[^?]{0,20}\b(i|we)?\s*(continue|keep going|proceed|go ahead|carry on|start (now|building|redrawing|on)|begin)\b",
        r"^(?!\s*(how|what|why)\b).*\bshould\b[^?]{0,30}\b(start|begin|proceed)\?",
        r"\bday'?s work\b|\b(helpers?|builders?|agents?) work on\b|\bnow,? or\b[^?]{0,30}\?$",
        r"\b(run|rewrite|walk|review|deploy|pass|sitting)\b[^?]{0,20}\bhappen\?|\bwhen should (it|this|that|they) deploy\b",
        r"\b(may|can|should) (we|i) start\b",
        r"\b(now|today|this sprint) or (later|next|tomorrow|after)\b|\bnow or later\b|\bwhen (should|do|shall)\b[^?]{0,30}\b(build|start|run|do|file|begin)\b|\b(?!from\b)\w+ when\?$",
        r"\bdoes it join the sprint\b|\bjoin the (next )?sprint\b|\bshape should the next sprint\b|\bahead of the sprint\b",
        # status-led "what now" only: after a design fact ("the rite lost its ingredient; what now?") it is not scope
        r"\b(red|broken|failing|blocked|stuck|done)\b[^?]{0,20}\bwhat now\?",
        # timing as the whole ask: trailing "now?/today?", or an imperative with "now"
        r"(^|[.!?:]\s+)(?!(what|how|why|who|where|which|when)\b)[^.!?]{0,45}(?<!for )\b(now|today|tonight|this (sprint|week))\??$",
        r"\b(build|rebuild|fix|redraw|draw|start|run|rename)\b[^?.]{0,50}(?<!from )(?<!for )\bnow\b",
    ],
    "twin": [
        r"\b(twins?|sibling|sister|campaign copy|counterpart)\b",
        r"\b(rut|rsw|rm)_ twins?\b",
        r"\b(does|do) (this|that|the|your|'?all)\b[^?]{0,50}\b(ruling|rule|cut|decision)\b[^?]{0,20}\b(apply|extend|include|cover)\b",
        r"\bdoes (the|this|that|your)[^?]{0,40}\b(rule|ruling)\b[^?]{0,30}\b(extend|apply)\b",
        r"\b(extend|apply|carry)\b[^?]{0,30}\b(to|onto)\b[^?]{0,30}\b(the same|its|their|both|the other|also)\b",
        r"\b(ban|cut|drop|remove|retire) (it|them|that) too\b",
        r"\bdoes '?all [\w ]+'? include\b",
        r"^(?!.*\b(can|could) (it|they|this|that)\b[^,]{0,40}\btoo\b).*\btoo\??$",
        r"\bthe rest of\b|\bthe same\b[^?]{0,60}\b(genes?|traits?|case|problem)\b",
        r"\bagainst the [\w ]{0,20}\brule\b",
        r"\bas (the )?[\w ]{1,30} did\?$|\bremove the rest\b",
        r"\b(rule|ruling) (gives|says|wants|requires)\b",
    ],
}
CLASSES = {k: [re.compile(p, re.I) for p in v] for k, v in CLASSES.items()}

# s2 triggers: any hit anywhere in the payload means the call is not purely delegated.
TRIGGERS = [re.compile(p, re.I) for p in [
    r"north[- ]?star",
    r"force[- ]?push|reset --hard|\bpurge\b|re-?freeze|frozen",
    r"\bkept\b|\bkeep\b[^?]{0,15}\b(art|picture|version)|owner[- ]kept|newest mark|(?<!-)\bmarks?\b",
    r"standing ruling|overturn|reinterpret|change what (it|the ruling) says|\bcontradict|canon\b",
    r"workshop|publish|\bpaid?\b|\bpay\b|spend|purchase|\bbuy\b|\bmoney\b|\bsubscription|plan usage|\blogin\b|log in|credential|\bupload",
    r"flyer|flier|(?<!in )flight|\bfly\b|human present",
    r"delete|\bdrop\b[^?]{0,20}(work|item)|irreversible|not ours|someone else",
    r"\bbroadcast\b|\bbridge\b",
    r"\bsteam\b|(?<!this )\bpush\b",
]]


def question_texts(payload):
    ti = (payload or {}).get("tool_input") or {}
    qs = ti.get("questions")
    if not isinstance(qs, list):
        return []
    return [q for q in qs if isinstance(q, dict)]


def ask_parts(question):
    """The parts that state the ask: the header, then each sentence ending in '?' (the whole text if none does).
    A card's preamble cites rulings, times and sprints freely; matching it refused cards that asked something else."""
    body = str(question.get("question") or "")
    asks = [s for s in re.split(r"(?<=[.!?])\s+", body.strip()) if s.endswith("?")]
    return [str(question.get("header") or "")] + (asks or [body])


def classify(parts):
    """Return the delegated class any part falls in, or None."""
    for cls, pats in CLASSES.items():
        if any(p.search(part) for p in pats for part in parts):
            return cls
    return None


def verdict(payload):
    """(classes, reason) -> reason is None when the call is allowed."""
    qs = question_texts(payload)
    if not qs:
        return [], None
    if OVERRIDE.search(json.dumps(payload.get("tool_input"), ensure_ascii=False)):
        return [], None
    classes = []
    scoped = []
    for q in qs:
        parts = ask_parts(q)
        c = classify(parts)
        if c is None:
            return [], None
        classes.append(c)
        scoped += parts + [json.dumps(q.get("options"), ensure_ascii=False)]
    # Triggers read the ask and its options, not the preamble: a card's background names the bridge, canon or a delete
    # in passing, and that hid plain "which first" asks (5 of 12 misses on a held-out sample).
    if any(t.search(part) for t in TRIGGERS for part in scoped):
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
