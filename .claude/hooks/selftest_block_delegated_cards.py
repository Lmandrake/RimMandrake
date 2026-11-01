#!/usr/bin/env python3
"""Selftest for block_delegated_cards.py: unit cases + a labelled corpus mined from OWNER.jsonl --by-card texts.

The corpus questions are the text before the arrow of real `byCard` strings in
infrastructure/state/ledger/events/OWNER.jsonl (the ledger keeps the card topic, not the full body, so these
are SHORTER than a live card: recall here is a floor). Labels are hand-made from the delegation policy:
IN = only question is s1 scope / s2.4 twin; OUT = anything else (taste, design, s2 triggers).
Even-indexed rows were used to tune the patterns; odd-indexed rows were held out, until two of their misses were
fixed by name (2026-10-31), which spent that split. FRESH_IN/FRESH_OUT are later card topics, also spent.
block_delegated_cards_corpus.json holds real full card texts, see its _note. The hook is a model, so this test replays
block_delegated_cards_verdicts.json, written only by --remeasure, and refuses a record of other prompts.
`blind_gold` gates (blind + blind2 pooled): fresh rows where three independent labellers agree; one pre-registered read,
bar in the corpus `bar` record (recall >= 0.80, false positives <= 2%, below rater agreement; the owner loosened it from 0.90
on 2026-11-01). `blind` and `blind2` alone are reported only. `sealed` is reported, not gated: one labeller's
rows, on which a careful reader cannot reach the bar. On a sample of them a fresh Opus scored recall 0.75 with 6 false
positives and GPT 0.79 with 18, and contested rows are where a refusal is arguable anyway.

    python3 .claude/hooks/selftest_block_delegated_cards.py [-v] [--remeasure]
"""
import concurrent.futures
import hashlib
import json
import os
import subprocess
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

FRESH_IN = [
    'New Pyrelands creature art provisional, art tests red — what now?',
    'When tune landmark density?',
    'Aiwha next',
    'Grown limbs this sprint',
    'Retire Alpha Biomes in phase 0 too?',
    'Redraw five audit pictures now (... Ashwallow dome ...)',
    'Should Alpha Biomes retire as a donor too',
    'River works and hose art fixes: which to commission?',
    'Fix the Bileworm and Zrrik guards now?',
    'defname rename now',
    'TunnelSnake B and Vurra B are 1024 px wide but the size rule gives 512/256: shrink too?',
    'Suush V_C is 512 px against the 256 canvas rule (drawSize ≤2) — shrink it?',
    'Bloodlurk C, Scaldhide B and Ribbonwhip B (art you picked tonight) are 1024 px but the size rule gives 256: shrink?',
    'Fish hides: should the rest of the fish drop fishskin?',
    'After the Dispatcher, which roles first?',
    'What should FlowWorks aim for this week?',
]
FRESH_OUT = [
    'Ash: what should Pyrelands ground do?',
    'How far does the sekkulaath rising reach?',
    'Where should the remaining goal lines come from?',
    'How do we finish the primitive droid tier?',
    "The pilot's finish line says Pyrelands must reach 0 UNMEASURED rows, which it can't. How should that line read now?",
    'The cargo tank is already the tall size at 160. What should tall mean for it?',
    'When a colonist digs in a dried-out pond bed, what should happen?',
    'How should we change the way the three mods are tested live?',
    'Furnace-beast warmth has no readable sign; which way?',
    'Re-stringing a cut power line is instant and free... What ships?',
    'Which features that are finished but OFF by default should ship ON?',
    'Drinking water also counts as food...Should it?',
    'How should vent gas burn',
    'The Struck Glass rite used fulgurite as its ingredient; what now?',
    'Some creatures look bigger facing you than side-on. How many should be rescaled?',
    'Which tar look should come back?',
    "About 259 creatures can't be fixed by shrinking. What should happen to them?",
    'How should players lacquer clothes and weapons with deepfire?',
    'How should the 7 canon Star Wars plants get their non-canon Baroque bases?',
    'Where should the material colour go on the new styled containers?',
    'How should the engine count liquid so buckets and bottles can hold realistic amounts?',
    'Should natural water get partial depth like dug cells?',
    'Do animals get thirsty?',
    'How should pump capacity relate to network size?',
    'When a pond feeds a canal, how should the water settle?',
    'Should still ponds lose water to the sun?',
    'Venomvine 48 renders: how to judge?',
    'How level must water be?',
    'One kind of water, or two?',
    'How deep must a pit be before it makes a room?',
    'How should we set tree sizes?',
    'Which cell-count rule decides when a lake is limitless?',
    'How should fall damage scale with depth?',
    'How should 0.5 m water look',
    'Pit depth widening (P5): what do we do with the look?',
    'Sixteen roster rows cast donor defs we have no def of: what happens?',
    '13 plants and lunger fry point at missing Succulents art: what do they wear?',
    'Weather sensing: what happens to the instrument mast?',
    'How far do we go to make art review fast and reliable?',
    'Should CAI stay now Real FoW is going?',
    'How should this frozen biome be settled?',
    'Lopsided tidal-lock daylight: what should light do?',
    'Every tile swings ~15 C with the seasons: what should seasons do?',
    'How far below the horizon should dusk light reach?',
    'How should head sizes be set?',
    'What should a live cord under wreckage do?',
    "What should 'tap' mean?",
    'How should an empty Scrapper hose stand out?',
    'Can pawns walk freely across the COVERED part of a partly-covered pit, as if it were floor?',
    'Should placement of a liquid drill or ground well be refused on a square the survey says holds no liquid?',
    'Drawbridges: look pictures vs your Timber/Steel picks — which should win?',
    'How should we resolve the side walls?',
    'RimPulse surface: what should it become?',
    'Leaning Scrub wind: what do you want for the final look?',
    'Contagion RustPuff: what do you want?',
    'Bleed well: what should change?',
    'Scrapper pipes: what should happen with it?',
    'Rail ladder: which way should def and art agree?',
    'Short hoses: how should spans with no smooth curve behave?',
    'Vexxiss: which becomes the main, and what happens to the other?',
    'Excretor: what should happen?',
    'For digging, how should salt crusts, packed snow and asphalt behave?',
    'Should our pit spikes pierce armour?',
    'Should drawbridges stay at most 3 wide?',
    'How should the drawbridge gate be added?',
    'Where should hands-on jobs at the machines go?',
    "What should 'new since last time' mean?",
    'Thornhold: how hard should it forbid its den?',
    'Rollbug: which carrion may it take?',
    'How should we set the system up going forward?',
    "What do we do with the 'on a stick' food?",
    'Should roast on a stick become the meal anyone can make?',
    "What should count as 'RimFlow v3 is superior to v2'?",
    "When should the Innovator count as having 'proved itself'?",
    'How far should the plan drain system and lukas before moving on?',
    'What should you tune the table in?',
    'What unit should the cells use?',
    'How much steel should rocky biomes have?',
    'How sparse should minerals be?',
    'Should those biomes get one?',
    'How should the mountain bands be enforced?',
    "How should we set each week's goals?",
    'How should venomvine be settled?',
    'How should findings be sorted on a regular schedule?',
    'Who should own the daily check?',
    'What should the kill test compare against?',
    'Who should plant faults for Operations to catch?',
    'When v3 is compared with v2, what should count?',
    'Which v2 weeks should it fit?',
    'When one of your habits shifts a lot, how should you hear about it?',
    'When may the Arbiter see the secret register?',
    'How should the check-ins run?',
    'What should count as done for being on schedule?',
    'What should happen to the seven builders?',
    'Which mod list should live testing run on?',
    'What should count most?',
    'Who decides a reload is justified?',
    'What should your role be during the trial?',
    'How much token budget should the 3 measuring days get?',
    'What should a win in the trial authorise?',
    'What should the trial do?',
]

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = json.load(open(os.path.join(HERE, "block_delegated_cards_corpus.json"), encoding="utf-8"))
RECORD = os.path.join(HERE, "block_delegated_cards_verdicts.json")
TUNE = lambda rows: rows[0::2]
HELD = lambda rows: rows[1::2]
# s2 reservations in plain words: the model must leave these with him.
S2_OUT = ["Which north star bar should I build first?", "Should I do the flyer live test next?",
          "Redraw the kept picture next?"]
SETS = (("tune", TUNE(IN), TUNE(OUT), True, True),
        ("spent", HELD(IN), HELD(OUT), True, True),
        ("spent2", FRESH_IN, FRESH_OUT, True, True),
        ("s2", [], S2_OUT, True, True),
        ("sealed", CORPUS["sealed_in"], CORPUS["sealed_out"], False, False),
        ("blind", CORPUS["blind_in"], CORPUS["blind_out"], False, False),
        ("blind2", CORPUS["blind2_in"], CORPUS["blind2_out"], False, False),
        ("blind_gold", CORPUS["blind_in"] + CORPUS["blind2_in"], CORPUS["blind_out"] + CORPUS["blind2_out"], True, False))
BAR = CORPUS["bar"]   # numbers live in the corpus data with their _why


def prompts_id():
    return hashlib.sha1((" ".join(H.CLI) + H.PREFIX + H.JUDGE + H.VETO).encode("utf-8")).hexdigest()


def key(system, text):
    return ("judge" if system == H.JUDGE else "veto") + ":" + hashlib.sha1(text.encode("utf-8")).hexdigest()


def remeasure():
    """Ask the real model about every scored row and write the record. A row it cannot answer aborts the write."""
    rows = sorted({t for _, i, o, _, _ in SETS for t in i + o})
    real, limit = H.ask_model, H.CALL_TIMEOUT_S
    H.CALL_TIMEOUT_S = 60
    seen = {}

    def ask(system, text):
        for _ in range(3):
            try:
                word = real(system, text)
            except (OSError, subprocess.SubprocessError):
                continue
            if word:
                seen[key(system, text)] = word
                return word
        raise RuntimeError("no answer: " + text[:60])  # classify() lets this through; the old record stays
    H.ask_model = ask
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(H.classify, rows))
    with open(RECORD, "w") as f:
        json.dump({"prompts": prompts_id(), "verdicts": seen}, f, indent=0, sort_keys=True)
    H.ask_model, H.CALL_TIMEOUT_S = real, limit
    print("remeasured %d rows, %d calls" % (len(rows), len(seen)))


def replay():
    rec = json.load(open(RECORD)) if os.path.exists(RECORD) else {}
    if rec.get("prompts") != prompts_id():
        return None
    H.ask_model = lambda system, text: rec["verdicts"][key(system, text)]
    return rec


def flagged(text):
    return bool(H.verdict({"tool_name": "AskUserQuestion", "tool_input": {"questions": [{"question": text}]}})[1])


def score(ins, outs):
    fn = [t for t in ins if not flagged(t)]
    fpl = [t for t in outs if flagged(t)]
    tp = len(ins) - len(fn)
    return (tp / (tp + len(fpl)) if tp + len(fpl) else 1.0), (tp / len(ins) if ins else 1.0), fn, fpl


def logic_checks(check):
    """The hook's own rules, on a stub model."""
    mk = lambda *qs: {"tool_name": "AskUserQuestion", "tool_input": {"questions": [
        {"header": "h", "question": q, "options": []} for q in qs]}}

    def stub(system, text):
        if system == H.VETO:
            return "owner" if "vetoed" in text else "leak"
        return "scope" if "first" in text or "vetoed" in text else "twin" if "too" in text else "none"
    H.ask_model = stub
    check("plain order refused", H.verdict(mk("Which item first?")) == (["scope"], True))
    check("override allows", not H.verdict(mk("[owner-asked] Which item first?"))[1])
    check("mixed call allowed", not H.verdict(mk("Which item first?", "Should the Rot gene be removed?"))[1])
    check("two classes refused", H.verdict(mk("Which item first?", "That one too?")) == (["scope", "twin"], True))
    check("veto allows", not H.verdict(mk("A vetoed thing"))[1])
    check("non-object stdin exits 0", subprocess.run([sys.executable, H.__file__], input="null", text=True).returncode == 0)
    check("malformed question allows", not H.verdict({"tool_input": {"questions": [{"question": "Which item first?"}, None]}})[1])
    check("garbage payload", H.verdict({})[1] is None and H.verdict({"tool_input": {"questions": "x"}})[1] is None)
    check("options are read", "Options: A | B" in H.card_text({"question": "q", "options": [{"label": "A"}, {"label": "B"}]}))
    check("option descriptions are read", "Options: A - why" in H.card_text(
        {"question": "q", "options": [{"label": "A", "description": "why"}]}))
    H.ask_model = lambda system, text: "maybe"
    check("unreadable answer allows", not H.verdict(mk("Which item first?"))[1])
    for err in (OSError("no claude"), subprocess.TimeoutExpired("claude", 1)):
        def boom(system, text, err=err):
            raise err
        H.ask_model = boom
        check("failed model allows: " + type(err).__name__, not H.verdict(mk("Which item first?"))[1])
    check("message names delegation", "delegated: scope" in H.message(["scope"]) and "digest" in H.message(["scope"]))
    check("twin message", "twin" in H.message(["twin"]))
    check("two calls fit the hook's timeout", H.CALL_TIMEOUT_S * 2 < 30)


def main():
    verbose = "-v" in sys.argv
    if "--remeasure" in sys.argv:
        remeasure()
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    logic_checks(check)
    if replay() is None:
        fails.append("verdict record is missing or from other prompts: run --remeasure")
    else:
        for label, rows_in, rows_out, gated, show in SETS:
            p, r, fn, fp = score(rows_in, rows_out)
            print("%-9s in=%d out=%d precision=%.2f recall=%.2f false+=%d" % (label, len(rows_in), len(rows_out), p, r, len(fp)))
            if verbose and show:
                for t in fn:
                    print("   MISSED :", t[:100])
                for t in fp:
                    print("   FALSE+ :", t[:100])
            if gated:
                check(label + " has rows", rows_out and (rows_in or label == "s2"))
                check(label + " false positives <= %.0f%%" % (BAR["fp_max_share"] * 100), len(fp) <= BAR["fp_max_share"] * len(rows_out))
                check(label + " recall >= %.2f" % BAR["recall_min"], r >= BAR["recall_min"])   # bar in corpus data (owner loosened it 2026-11-01)
    for f in fails:
        print("FAIL:", f)
    print("selftest_block_delegated_cards: %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
