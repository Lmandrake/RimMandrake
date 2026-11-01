#!/usr/bin/env python3
"""PreToolUse/AskUserQuestion hook - refuse a card whose ONLY questions are in a class the owner delegated.

Item CARDS_ENFORCE_DELEGATED_CLASSES_STOP. design/RimMandrake/delegation_policy.md:
  s1 `scope`   - work order, which item next, helper count, whether to continue / start now or later
  s2.4 `twin`  - applying an existing ruling to a case it does not name (campaign copy, sister biome, sibling def)
Measured: 29 ordering cards (81% agreement), ~235 typed go-aheads, 9 twin cards (8 yes) in 3 weeks.

A model reads each question, because regexes never generalised: five sealed reads of tuned patterns gave recall
0.19, 0.62, 0.90, 0.50, 0.58 (DELEGATED_CARDS_FIX_HELD_OUT_RECALL). JUDGE names the class, VETO re-reads a positive.
False positives are the only way this hook does harm, so it refuses only when
  * EVERY question in the call is judged delegated and survives the veto, AND
  * no question carries the override marker [owner-asked] (he asked to be asked).
A failed, late or unreadable model call allows the card. Exit 2 blocks; anything unparseable exits 0.
The prompts are measured text: change either one and run the selftest with --remeasure.

    python3 .claude/hooks/selftest_block_delegated_cards.py [--remeasure]
"""
import concurrent.futures
import json
import re
import subprocess
import sys
import tempfile

OVERRIDE = re.compile(r"\[owner-asked\]", re.I)
MODEL = "sonnet"     # a CLI alias: the account behind it is the environment's business
CALL_TIMEOUT_S = 13  # two stages must fit inside the hook's 30 s in .claude/settings.json
CLI = ["claude", "-p", "--model", MODEL, "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
       "--tools", "", "--no-session-persistence", "--system-prompt"]  # then the prompt, then PREFIX + the card
PREFIX = "CARD QUESTION:\n"

JUDGE = """You classify one question an AI agent wants to put to its human owner on a decision card, in a RimWorld modding project. Agents were told which classes they must decide alone. Decide whether this card is a leak.

scope: the ask is only about WORK MANAGEMENT of work already understood: what to do or build next or first, the order of items, which items from a list to build or queue now, when to do something, whether to start, continue, go ahead or wait, how many helpers or agents to run.
twin: the ask is only whether an EXISTING ruling or decision should also cover a further similar case it did not name: "should X go too?", "same treatment for the sibling def / sister biome / campaign copy?", "shrink these too, as you approved for that one?".
none: everything else. In particular: how a thing should work, look, be named or be numbered; which design, option or approach is right; what should happen to a thing when the options differ in content rather than timing; review verdicts on art or a design; what a ruling meant, or two rulings that conflict; how a process, policy, trial or tool should be set up; a question of fact; asking for his preference or permission on a new kind of act. Also none, whatever the wording, when the answer touches: north-star bars; irreversible acts on work not ours (force-push, deleting others' work, re-freezing the frozen dump); replacing art he kept; changing or reinterpreting one of his rulings; outward or paid acts (publishing, buying, spending, Steam, Workshop); live tests of flying creatures.

Examples.
scope: "Aiwha's wingspan failed all four renders, so what should we try next?" · "Two art tests stay red until it's settled. What now?" · "Should I queue redraws for all 1,716 sets?" · "Start the runner pilot now?" · "When a decision is open, should I proceed on the plan's default?" · "The redraw is pushed but not deployed. What should happen next?" · "This was held to next week by your card. Today?" · "Which shape should the next sprint take?" · "When should these 14 mods come out?" · a bare topic with a time word: "Grown limbs this sprint", "defname rename now", "Kit art ahead of the sprint"
twin: "Should the rest of the fish drop fishskin too?" · "This one is 512 px against the 256 canvas rule: shrink it?" · "Massassi's skin is sourced. Remove the rest?" · "Should those biomes get it too?"
none: "Approve this pass list of 80 rows?" · "How do you want to take the remaining 60 picks?" · "When sand-lock hits, should the sarlacc also be stopped?" (a mechanic) · "Does your ruling cover this heat source?" is twin only if it asks to extend the ruling, none if it asks what the ruling means.

Judge the ask, not the background: a preamble may mention rulings, sprints or the bridge in passing. If several questions are asked, judge the main one. When truly unsure between a class and none, answer none.

Reply with exactly one word: scope, twin or none."""

VETO = """An AI agent wants to put a question to its human owner on a decision card, in a RimWorld modding project. A first reader marked the question as one agents settle alone: plain work order or timing ("which next", "when", "start now?", "what now?", "shall I deploy?"), helper count, or one more sibling case of an existing ruling ("X too?", "the rest too?").

Most such marks are right. Questions about when to do something, what to do first, or whether to go ahead stay LEAK even if the work is big, needs a game restart, or involves him: scheduling is delegated.

Answer OWNER only if the question is really one of these in disguise:
- it conflicts with the plain text of a ruling of his, and the card says so;
- it would replace art he accepted or kept;
- it sets a blanket rule across every biome, species or mod (an extension to a few named siblings is still LEAK);
- it chooses between two claims on a shared resource, such as two seats wanting the game;
- it asks what a choice should BE (a look, a mechanic, a design), with timing only as a wrapper;
- it adds a new creature, item or mechanic nobody has ruled on, even when worded "also add the others?";
- it spends or paces an account's quota or allowance ("how fast", "reset now or next week");
- it ships something into the game before he has reviewed it;
- it cuts or keeps content on taste ("should the other off-tone mods be cut too?");
- it hands over failed work with no plan ("how should it go?", "what do I do with it?");
- it asks how far a plan should go or how a process should be set up;
- a bare pronoun with no named subject ("Should those biomes get one?", "Which v2 weeks should it fit?").

These stay LEAK: "Should we start redrawing now?" · "Which batches should I queue now?" · "When should it go?" · "How much should we land today?" · "Grown limbs this sprint" · "Rename now?" · "Art tests red: what now?" · "Which belong in this sprint?" · "This was held to next week. Today?" · "Build now or re-sort first?" · "Which shape should the next sprint take?" · "Which of these controls should I build?" · "This needs a sitting with you. When?" · "How should the helpers be split across the streams?" · "Art you picked is 1024 px but the rule gives 256: shrink?" · "The same on every sunlit map, RUT_ twins included?"

Otherwise answer LEAK. Reply with exactly one word: LEAK or OWNER."""


def ask_model(system, text):
    """The model's first word, lower-cased. Run from a temp dir with no settings: no hooks, project files or tools."""
    r = subprocess.run(CLI + [system, PREFIX + text], capture_output=True, text=True, timeout=CALL_TIMEOUT_S, cwd=tempfile.gettempdir(),
                       stdin=subprocess.DEVNULL)
    words = r.stdout.split()
    return words[0].strip(":.,").lower() if r.returncode == 0 and words else ""


def question_texts(payload):
    ti = (payload or {}).get("tool_input") or {}
    qs = ti.get("questions")
    if not isinstance(qs, list):
        return []
    return qs if all(isinstance(q, dict) for q in qs) else []  # a card we cannot fully read goes through


def card_text(question):
    """What the model reads: header, question, then the options (one can change what the card is about)."""
    labels = [" - ".join(str(o[k]) for k in ("label", "description") if o.get(k))
              for o in question.get("options") or [] if isinstance(o, dict) and o.get("label")]
    parts = (str(question.get("header") or ""), str(question.get("question") or ""),
             "Options: " + " | ".join(labels) if labels else "")
    return "\n".join(p for p in parts if p)


def classify(text):
    """The delegated class of one question, or None. Any failure reads as None: an unjudged card goes through."""
    try:
        cls = ask_model(JUDGE, text)
        if cls not in ("scope", "twin"):
            return None
        return cls if ask_model(VETO, text) == "leak" else None
    except (OSError, subprocess.SubprocessError):
        return None


def verdict(payload):
    """(classes, reason) -> reason is None when the call is allowed."""
    qs = question_texts(payload)
    if not qs or OVERRIDE.search(json.dumps(payload.get("tool_input"), ensure_ascii=False)):
        return [], None
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(qs)) as pool:
        classes = list(pool.map(classify, map(card_text, qs)))
    if None in classes:
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
                 "a flyer live test), say so in the question text: a model read it and can be wrong. If he asked to be "
                 "asked, put [owner-asked] in the question text. Check: CARDS_ENFORCE_DELEGATED_CLASSES_STOP.")
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or (payload.get("tool_name") or "AskUserQuestion") != "AskUserQuestion":
        return 0
    try:
        classes, hit = verdict(payload)
    except Exception:
        classes, hit = [], None  # an unjudged card goes through, but still owes the path check below
    if hit:
        sys.stderr.write(message(classes) + "\n")
        return 2
    import block_owner_doc_wsl_paths as OWNER_DOC
    OWNER_DOC.refuse(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
