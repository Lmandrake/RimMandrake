#!/usr/bin/env python3
"""Selftest for block_delegated_cards.py: unit cases + a labelled corpus mined from OWNER.jsonl --by-card texts.

The corpus questions are the text before the arrow of real `byCard` strings in
infrastructure/state/ledger/events/OWNER.jsonl (the ledger keeps the card topic, not the full body, so these
are SHORTER than a live card: recall here is a floor). Labels are hand-made from the delegation policy:
IN = only question is s1 scope / s2.4 twin; OUT = anything else (taste, design, s2 triggers).
Even-indexed rows were used to tune the patterns; odd-indexed rows are held out and only reported.

    python3 .claude/hooks/selftest_block_delegated_cards.py [-v]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import block_delegated_cards as H  # noqa: E402

IN = [
    "Borrowed fauna conversion order",
    "Build order",
    "Build the deep-elevation work when?",
    "Deeper ponds (lakes deeper than 4) were held to next week by your card. Today?",
    "Direct Sun on every sunlit map incl. Scarlands, Miasma, RUT_ twins?",
    "FlowWorks day shape",
    "How many helpers should Bench keep working at once while you're away?",
    "Next build",
    "Nothing from tonight is in the game yet... When should it run?",
    "Rivers/roads order",
    "Raised rail ladder looks broken, side views skeletal: what next?",
    "Should we start redrawing now?",
    "The Rot ... does it join the sprint that starts tomorrow?",
    "What next? (trickle-fed = each feature lands small, proven live, pre-checked by an agent at once)",
    "Which build do I drive first today?",
    "Which experiment first?",
    "Which shape should the next sprint take?",
    "Who builds during the biome sprint",
    "Kit art ahead of the sprint",
    "Canal overflow build: may we start it?",
    "Which water controls / landscape controls should I build?",
    "Celestial Rogues is another faction you may not want. Ban it too?",
    "Does 'all FlowWorks' include Gimme Some Slack?",
    "Does the level-surface rule extend to spilled sheets?",
    "Should I continue with the next item or stop here?",
    "How many subagents should I run at once?",
    "Which of these three items should I do first?",
    "You cut the Abyss roaches. Should the same cut apply to the Leaning Scrub twin?",
    "Does this ruling apply to the campaign copy of the biome as well?",
    "Shall I keep going with the remaining biomes?",
]
OUT = [
    "Account reset: now (burn hard until Wed 4pm) or next week?",
    "Pay for an outside agent product now?",
    "Kept art judged really bad: may the pipeline redraw it on its own?",
    "May 'newest mark wins' become a delegated rule, with X moving the picture to the art archive",
    "Does your 'Verified' also validate GimmeSomeSlack's north star, so it stops being a d",
    "North star: add the two orphan bars",
    "Should SteveDesktop be able to push?",
    "Which saved world should the project treat as the canonical start?",
    "Which creature fills the Forge slot?",
    "Which Scald map carries the steam lock and Scald weather?",
    "Which look should a pumped-dry pond bed have?",
    "Which of these five big plants should count as trees?",
    "Which belief systems offer the calling-pyre precept",
    "Which materials may fall in meteorites?",
    "Which new reel outlet should go into the game?",
    "Which way should a hose leave its reel?",
    "Which switch owns pipe poles",
    "What does release mean for these three mods today?",
    "Starting map is 250x250, old world 325x325: which size?",
    "Where should Chikka live?",
    "Who sells the Cloud Repulsor and Sunbeam",
    "Who goes down into a pit to tend or rescue",
    "What should happen to a pawn already in a pit under a cover?",
    "How should the zoomed-out forest view work?",
    "May Archmagi's game run those batch tests unattended while you're away?",
    "May a seat take the free bridge, deploy and restart the game on its own",
    "May agents delete our own leftovers when a check proves nothing reads them",
    "Should 3-deep pits work as prisons",
    "Is the Abyss the Crags you meant?",
    "Keep yearning fruit?",
    "Uvak south flap preview: does it read as lift?",
    "Which mod set for the repaint",
    "How much capacity to keep free for you?",
    "Should the master switch also stop the bands?",
    "Aiwha wingspan: which canvas size?",
]

TUNE = lambda rows: rows[0::2]
HELD = lambda rows: rows[1::2]


def flagged(text):
    p = {"tool_name": "AskUserQuestion", "tool_input": {"questions": [
        {"header": "Q", "question": text, "options": [{"label": "A"}, {"label": "B"}]}]}}
    return bool(H.verdict(p)[1])


def score(ins, outs):
    tp = sum(flagged(t) for t in ins)
    fp = sum(flagged(t) for t in outs)
    fn = [t for t in ins if not flagged(t)]
    fpl = [t for t in outs if flagged(t)]
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / len(ins) if ins else 1.0
    return prec, rec, fn, fpl


def main():
    verbose = "-v" in sys.argv
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    mk = lambda *qs: {"tool_name": "AskUserQuestion", "tool_input": {"questions": [
        {"header": "h", "question": q, "options": []} for q in qs]}}
    check("plain order refused", bool(H.verdict(mk("Which item should I build first?"))[1]))
    check("override allows", not H.verdict(mk("[owner-asked] Which item should I build first?"))[1])
    check("mixed call allowed", not H.verdict(mk("Which item first?", "Should the Rot gene be removed?"))[1])
    check("two in-class refused", bool(H.verdict(mk("Which item first?", "How many helpers?"))[1]))
    check("north star trigger allows", not H.verdict(mk("Which north star bar should I build first?"))[1])
    check("flyer trigger allows", not H.verdict(mk("Should I do the flyer live test next?"))[1])
    check("kept art trigger allows", not H.verdict(mk("Redraw the kept picture next?"))[1])
    check("garbage payload", H.verdict({})[1] is None and H.verdict({"tool_input": {"questions": "x"}})[1] is None)
    check("message names delegation", "delegated: scope" in H.message(["scope"]) and "digest" in H.message(["scope"]))
    check("twin message", "twin" in H.message(["twin"]))

    for label, rows_in, rows_out in (("tune", TUNE(IN), TUNE(OUT)), ("held-out", HELD(IN), HELD(OUT))):
        p, r, fn, fp = score(rows_in, rows_out)
        print("%-9s in=%d out=%d precision=%.2f recall=%.2f" % (label, len(rows_in), len(rows_out), p, r))
        if verbose:
            for t in fn:
                print("   MISSED :", t[:100])
            for t in fp:
                print("   FALSE+ :", t[:100])
        check(label + " no false positives", not fp)
        check(label + " recall >= 0.8", r >= 0.8)
    for f in fails:
        print("FAIL:", f)
    print("selftest_block_delegated_cards: %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
