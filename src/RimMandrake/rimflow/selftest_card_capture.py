#!/usr/bin/env python3
"""selftest_card_capture.py — a card answer's whole option text travels with the decision.

Item RIMMANDRAKE_RECORD_CARD_OPTION_TEXT_LABEL_LOST_THE_ART (2026-11-15: the ledger kept "Keep 'twice', raise body to
9+", the description's "needs bigger art" was lost, and no art was made). Offline, fixtures only: a temp ledger, temp
items dir, temp card store, an empty transcript dir; the real ledger and store are never touched.

  hook        a PostToolUse payload through the registered hook script lands the whole card in the store
  ledger      `file --by-card "question → label"` stamps `card` with the picked option's description
  grep        owner_rulings.py --grep finds "bigger art", a phrase only the description held
  prose       items/<ID>.md gets "## What the card said" with the description and the owed "needs bigger art"
  launch      a brief missing the description is refused, naming the text and the fix; one holding it is not
  close       a close whose words do not name "bigger art" is refused with the path to pass; one that does is not
  empty       a card whose option has no description still stamps, writes prose and launches
  plain       a non-card item: no `card`, no section, no launch or close refusal
  transcript  a card found only in a session transcript (hook never ran) is still found and stamped
  bare        a bare --by-card takes the card answered last
  overflow    a four-question card of the tool's maximum size records whole: every line under 4096 bytes, `show` prints
              all four with the picked descriptions verbatim; a one-question card stays one event; his typed note
              travels; an empty card store refuses by name
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
HOOK = os.path.join(REPO, ".claude", "hooks", "capture_card_answer.py")
RULINGS = os.path.join(HERE, "owner_rulings.py")
sys.path.insert(0, HERE)
FAILS = []

FURNACE_Q = "Pyrelands failed its final look on one bar. How should the giant be made the giant?"
FURNACE_DESC = ("Why: holds the original promise literally, a giant twice anything on the map. Costs: overturns your "
                "ruled body size of 6, needs bigger art, and breaks again if a larger animal is ever patched in.")
FURNACE = {"question": FURNACE_Q, "header": "Furnace size", "multiSelect": False, "options": [
    {"label": "Reword bar, draw it bigger (Recommended)", "description": "Why: keeps your body size of 6."},
    {"label": "Keep 'twice', raise body to 9+", "description": FURNACE_DESC},
    {"label": "Pass it as is, list as polish", "description": "Why: gets Pyrelands moving today."}]}
EMPTY_Q = "Delete the four old placeholder files?"
EMPTY = {"question": EMPTY_Q, "header": "Placeholders", "multiSelect": False, "options": [
    {"label": "Delete them", "description": ""}, {"label": "Keep them", "description": ""}]}
TX_Q = "Which scene should be Graffiti's face?"
TX_DESC = "Why: the walk shows what reads; needs a zoomed capture of the wall."
TX = {"question": TX_Q, "header": "Face", "multiSelect": False, "options": [
    {"label": "Decide after the walk", "description": TX_DESC}, {"label": "The market wall", "description": "x"}]}


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def env(tmp, **over):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT")}
    e["RIMFLOW_LEDGER"] = os.path.join(tmp, "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(tmp, "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = "BUILD"
    e["RM_CARDS_STORE"] = os.path.join(tmp, "cards", "cards.jsonl")
    e["RM_CARDS_TRANSCRIPTS"] = os.path.join(tmp, "transcripts")
    e["RM_FULLTEXT_DIR"] = os.path.join(tmp, "fulltext")
    e.update(over)
    return e


def run(tmp, *args, **over):
    p = subprocess.run([sys.executable, CLI] + list(args), capture_output=True, text=True,
                       env=env(tmp, **over), cwd=REPO, timeout=120)
    return p.returncode, p.stdout, p.stderr


def events(tmp):
    out = []
    for dp, _, fs in os.walk(tmp):
        if os.sep + "cards" in dp:
            continue
        for f in sorted(fs):
            if f.endswith(".jsonl") and "transcripts" not in dp:
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    out += [json.loads(l) for l in fh if l.strip()]
    return out


def last_for(tmp, iid):
    evs = [e for e in events(tmp) if e.get("id") == iid]
    return evs[-1] if evs else None


def closed(tmp, iid):
    return any(e.get("event") == "close" for e in events(tmp) if e.get("id") == iid)


def prose(tmp, iid):
    try:
        with open(os.path.join(tmp, "items", iid + ".md"), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def hook(tmp, question, answer):
    payload = {"session_id": "sess-fixture", "tool_name": "AskUserQuestion", "tool_use_id": "toolu_%d" % time.time_ns(),
               "tool_input": {"questions": [question]},
               "tool_response": {"questions": [question], "answers": {question["question"]: answer}, "annotations": {}}}
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True,
                       env=env(tmp), cwd=REPO, timeout=60)
    return p.returncode, p.stdout, p.stderr


def big_card(n=4, tag="q"):
    qs = [{"question": ("%s%d " % (tag, i)) + "Q" * 500, "header": "H%d" % i, "multiSelect": False,
           "options": [{"label": "L%d%s" % (i, c), "description": ("D%d%s " % (i, c)) + "d" * 335} for c in "abc"]}
          for i in range(n)]
    return qs


def hook_card(tmp, qs, answers, annotations=None):
    payload = {"session_id": "sess-big", "tool_name": "AskUserQuestion", "tool_use_id": "toolu_%d" % time.time_ns(),
               "tool_input": {"questions": qs},
               "tool_response": {"questions": qs, "answers": answers, "annotations": annotations or {}}}
    return subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True,
                          env=env(tmp), cwd=REPO, timeout=60)


def overflow_cases(tmp):
    qs = big_card(4)
    hook_card(tmp, qs, {q["question"]: q["options"][1]["label"] for q in qs},
              {qs[0]["question"]: {"notes": "his typed note"}})
    G = "RIMMANDRAKE_PROBE_FOUR_QUESTION_CARD_FIXTURE"
    run(tmp, "file", G, "--for", "BUILD", "--title", "t")
    rc, out, err = run(tmp, "note", G, "--text", "x", "--by-card")
    lines = []
    for dp, _, fs in os.walk(tmp):
        if os.sep + "cards" in dp or "transcripts" in dp:
            continue
        for f in fs:
            if f.endswith(".jsonl"):
                lines += open(os.path.join(dp, f), "rb").read().splitlines(True)
    check(rc == 0 and lines and max(len(l) for l in lines) < 4096,
          "overflow: a four-question card records with a bare --by-card, every line < 4096 (%d %s)" % (rc, (out + err).strip()[-160:]))
    p = subprocess.run([sys.executable, os.path.join(HERE, "card_capture.py"), "show", G, "--events", os.path.join(tmp, "events")],
                       capture_output=True, text=True, env=env(tmp), cwd=REPO, timeout=60)
    shown = p.stdout
    check(p.returncode == 0 and all(q["question"] in shown and q["options"][1]["description"] in shown for q in qs)
          and "his typed note" in shown,
          "overflow: show prints all four questions, the picked descriptions verbatim and his typed note (%s)" % p.stderr.strip()[-120:])
    md = prose(tmp, G)
    check(all(q["options"][1]["description"] in md for q in qs), "overflow: the item prose holds all four descriptions")

    J = "RIMMANDRAKE_PROBE_FOUR_QUESTION_FILE_FIXTURE"
    rc, out, err = run(tmp, "file", J, "--for", "BUILD", "--title", "t", "--by-card")
    mine = [e for e in events(tmp) if e.get("id") == J]
    check(rc == 0 and len(mine) == 4 and sum(len(e["card"]["questions"]) for e in mine if e.get("card")) == 4,
          "overflow: the file path splits into one event per question (%d, %d events)" % (rc, len(mine)))

    q1 = big_card(1, "solo")
    hook_card(tmp, q1, {q1[0]["question"]: q1[0]["options"][0]["label"]})
    H = "RIMMANDRAKE_PROBE_ONE_QUESTION_BIG_CARD_FIXTURE"
    run(tmp, "file", H, "--for", "BUILD", "--title", "t")
    before = len([e for e in events(tmp) if e.get("id") == H])
    rc, out, err = run(tmp, "note", H, "--text", "x", "--by-card")
    after = len([e for e in events(tmp) if e.get("id") == H])
    check(rc == 0 and after - before == 1, "overflow: a one-question card is one event (%d)" % (after - before))

    empty = os.path.join(tmp, "empty")
    os.makedirs(os.path.join(empty, "transcripts"))
    rc, out, err = run(empty, "note", H, "--text", "x", "--by-card", "no such question → nope")
    check("no answered card" in err, "overflow: an empty card store is named in the warning")


# ---- a card too big for one ledger line even split (RIMMANDRAKE_FIX_CARD_STAMP_OVER_LEDGER_LINE_LIMIT), one test per
# promise on design/specs/2026-11-19-card-stamp-fit/boundary.md. The fixture is tonight's card's shape: three questions,
# his long typed answer on the first (no option picked), a picked option with a description on each other. SOLO is one
# question (never split) too long for a line, with a picked option: the fit, not the split, must carry it.

TYPED = "He typed this answer himself. " * 120     # 3.6 KB: the bare --by-card summary alone is over a line
BIG = [{"question": "q-typed " + "Q" * 800, "header": "Old tickets", "multiSelect": False,
        "options": [{"label": "Judge them all", "description": "D-a " + "a" * 300}, {"label": "Leave them", "description": "D-b"}]},
       {"question": "q-two " + "R" * 370, "header": "Next moves", "multiSelect": True,
        "options": [{"label": "Stop rule", "description": "D-stop Costs: needs a calibration run. " + "s" * 300},
                    {"label": "One fault", "description": "D-one " + "o" * 300}]},
       {"question": "q-three " + "S" * 370, "header": "Pages", "multiSelect": False,
        "options": [{"label": "Locked bars", "description": "D-locked " + "l" * 320}, {"label": "Other", "description": "x"}]}]
STAMP = []
SOLO = [{"question": "q-solo " + "V" * 4200, "header": "Solo", "multiSelect": False,
         "options": [{"label": "Take it", "description": "D-take Costs: needs a calibration run. " + "t" * 300},
                     {"label": "Leave it", "description": "D-leave"}]}]
SOLO_ID = "RIMMANDRAKE_PROBE_ONE_HUGE_QUESTION_CARD_FIXTURE"


def solo(tmp):
    """File one item with a bare --by-card on SOLO, once. -> (rc, err, its events, its prose)."""
    if len(STAMP) < 2:
        stamped(tmp)
        hook_card(tmp, SOLO, {SOLO[0]["question"]: "Take it"})
        rc, out, err = run(tmp, "file", SOLO_ID, "--for", "BUILD", "--title", "t", "--by-card")
        STAMP.append((rc, err))
    rc, err = STAMP[1]
    return rc, err, [e for e in events(tmp) if e.get("id") == SOLO_ID], prose(tmp, SOLO_ID)


def stamped(tmp):
    """File one item with a bare --by-card on the big card, once. -> (rc, err, the item's events, its prose, id)."""
    iid = "RIMMANDRAKE_PROBE_TYPED_ANSWER_CARD_FIXTURE"
    if not STAMP:
        hook_card(tmp, BIG, {BIG[0]["question"]: TYPED, BIG[1]["question"]: "Stop rule",
                             BIG[2]["question"]: "Locked bars"})
        rc, out, err = run(tmp, "file", iid, "--for", "BUILD", "--title", "T" * 150, "--by-card",
                           "--why", "W" * 400)
        STAMP.append((rc, err))
    rc, err = STAMP[0]
    return rc, err, [e for e in events(tmp) if e.get("id") == iid], prose(tmp, iid), iid


def ledger_lines(tmp):
    lines = []
    for dp, _, fs in os.walk(tmp):
        if os.sep + "cards" in dp or "transcripts" in dp:
            continue
        lines += [l for f in fs if f.endswith(".jsonl") for l in open(os.path.join(dp, f), "rb").read().splitlines(True)]
    return lines


def t_a_card_over_one_line_records(tmp):
    rc, err, mine, _md, _iid = stamped(tmp)
    lines = ledger_lines(tmp)
    check(rc == 0 and mine and max(len(l) for l in lines) < 4096,
          "card fit: a card whose one question is over a ledger line records with a bare --by-card, every line < 4096 "
          "(rc %d, %s)" % (rc, err.strip()[-200:]))
    rc, err, mine, _md = solo(tmp)
    check(rc == 0 and len(mine) == 1 and max(len(l) for l in ledger_lines(tmp)) < 4096,
          "card fit: one question too long for a line records as one event (rc %d, %s)" % (rc, err.strip()[-200:]))


def t_the_whole_card_reaches_the_item_prose(tmp):
    rc, err, _mine, md, _iid = stamped(tmp)
    flat = " ".join(md.split())
    check(rc == 0 and " ".join(TYPED.split()) in flat and BIG[0]["question"] in md
          and all(o["description"] in md for q, lab in zip(BIG[1:], ("Stop rule", "Locked bars"))
                  for o in q["options"] if o["label"] == lab),
          "card fit: the item prose holds his whole typed answer, the whole question and every picked description")
    rc, err, _mine, md = solo(tmp)
    check(rc == 0 and SOLO[0]["question"] in md and SOLO[0]["options"][0]["description"] in md,
          "card fit: a card fitted but not split still reaches the prose whole")


def t_picked_descriptions_stay_whole_on_the_events(tmp):
    _rc, _err, mine, _md, _iid = stamped(tmp)
    got = [o.get("description") for e in mine for q in (e.get("card") or {}).get("questions") or []
           for o in q.get("picked") or []]
    want = [o["description"] for q, lab in zip(BIG[1:], ("Stop rule", "Locked bars")) for o in q["options"]
            if o["label"] == lab]
    check(sorted(got) == sorted(want), "card fit: each picked description is whole on an event card (the gates read "
          "them there): %d of %d" % (len([d for d in got if d in want]), len(want)))
    _rc, _err, mine, _md = solo(tmp)
    got = [o.get("description") for e in mine for q in (e.get("card") or {}).get("questions") or []
           for o in q.get("picked") or []]
    check(got == [SOLO[0]["options"][0]["description"]], "card fit: the fitted question's picked description is whole")


def t_a_card_that_fits_is_stamped_whole(tmp):
    q = [dict(BIG[1], question="q-small")]
    hook_card(tmp, q, {"q-small": "One fault"})
    iid = "RIMMANDRAKE_PROBE_SMALL_CARD_STAYS_WHOLE_FIXTURE"
    rc, out, err = run(tmp, "file", iid, "--for", "BUILD", "--title", "t", "--by-card")
    ev = last_for(tmp, iid) or {}
    cq = ((ev.get("card") or {}).get("questions") or [{}])[0]
    check(rc == 0 and cq.get("question") == "q-small" and cq.get("answer") == "One fault"
          and "whole text" not in json.dumps(ev), "card fit: a card that fits one line is stamped whole, nothing cut")


def main():
    tmp = tempfile.mkdtemp(prefix="rm_card_capture_")
    os.makedirs(os.path.join(tmp, "transcripts"))
    try:
        rc, out, err = hook(tmp, FURNACE, "Keep 'twice', raise body to 9+")
        store = os.path.join(tmp, "cards", "cards.jsonl")
        held = open(store, encoding="utf-8").read() if os.path.exists(store) else ""
        check(rc == 0 and out.strip() == "" and "needs bigger art" in held and "Pass it as is" in held,
              "hook: the answered card lands in the store whole, silently (rc %d, %s)" % (rc, err.strip()[-160:]))

        A = "RIMMANDRAKE_PROBE_CARD_DESCRIPTION_TRAVELS_FIXTURE"
        rc, out, err = run(tmp, "file", A, "--for", "BUILD", "--title", "t",
                           "--by-card", "How should the giant be made the giant? → Keep 'twice', raise body to 9+")
        ev = last_for(tmp, A) or {}
        card = ev.get("card") or {}
        q = (card.get("questions") or [{}])[0]
        check(rc == 0 and ev.get("byCard", "").endswith("raise body to 9+"),
              "ledger: file --by-card writes (%d %s)" % (rc, err.strip()[-200:]))
        check(q.get("question") == FURNACE_Q and [o.get("description") for o in q.get("picked", [])] == [FURNACE_DESC],
              "ledger: the event holds the question and the picked option's whole description")
        check(set(q.get("others") or []) == {"Reword bar, draw it bigger (Recommended)", "Pass it as is, list as polish"},
              "ledger: the event names the other options' labels")

        p = subprocess.run([sys.executable, RULINGS, "--events", os.path.join(tmp, "events"), "--grep", "bigger art", "--last", "0"],
                           capture_output=True, text=True, timeout=60)
        check(p.returncode == 0 and A in p.stdout, "grep: owner_rulings finds 'bigger art', said only in the description "
              "(%s)" % (p.stdout + p.stderr).strip()[-160:])
        p = subprocess.run([sys.executable, RULINGS, "--events", os.path.join(tmp, "events"), "--grep", "zzz-not-on-any-card", "--last", "0"],
                           capture_output=True, text=True, timeout=60)
        check(A not in p.stdout, "grep: a phrase on no card finds nothing (the instrument can say no)")

        md = prose(tmp, A)
        check("## What the card said" in md and FURNACE_DESC in md and "needs bigger art" in md.split("Owed by this card")[-1],
              "prose: items/%s.md has the section, the description, and the owed consequence" % A)

        import detached_helper as DH
        bad = "Raise the furnace-beast's body size to 9. Check the sprite; if it is blurry, file an art item."
        good = bad + "\n\nWhat the card said: " + FURNACE_DESC
        shards = os.path.join(tmp, "events")
        why = DH.card_refusal(A, bad, events_dir=shards)
        check(bool(why) and "needs bigger art" in why and "paste" in why.lower() and "card_capture.py show" in why,
              "card_refusal: a brief missing the description is named, with the text and the fix (%r)" % (why or "")[:120])
        check(DH.card_refusal(A, good, events_dir=shards) is None, "launch: a brief holding the description verbatim passes")
        check(DH.card_refusal(A, good.replace(". Costs", ".   Costs").replace("'", "’"), events_dir=shards) is None,
              "launch: whitespace and curly quotes do not refuse a verbatim paste")
        try:
            rc, text = DH.launch("BENCH", A, bad, "opus", None, 1, known={A},
                                 runner=lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "fake runner"),
                                 events_dir=shards)
        except Exception as e:  # noqa: BLE001  the fake runner stops it later; only the card refusal matters here
            rc, text = 1, "%s: %s" % (type(e).__name__, e)
        check(not (rc == 2 and "decided by card" in text), "launch: launch() never refuses a short brief for its card "
              "text (owner 2026-11-20); card_repair adds it (%d %s)" % (rc, text[-120:]))
        fixed, added = DH.card_repair(A, bad, events_dir=shards)
        check(added and DH.card_refusal(A, fixed, events_dir=shards) is None, "launch: card_repair adds the card's words")
        check("needs bigger art" in DH.card_footer(A, events_dir=shards),
              "launch: the footer tells the builder each consequence is work owed at close")

        rc, out, err = run(tmp, "close", A, "--no-code", "raised the body size", "--why", "done")
        check(rc != 0 and "needs bigger art" in (out + err) and "--why" in (out + err),
              "close: a close not naming 'bigger art' is refused with the path to pass (%d)" % rc)
        rc, out, err = run(tmp, "close", A, "--no-code", "raised the body size",
                           "--why", "bigger art: filed RIMMANDRAKE_REDRAW_FURNACE_BEAST_FIXTURE")
        check("needs bigger art" not in (out + err) and closed(tmp, A),
              "close: naming where the bigger art was filed passes (%d %s)" % (rc, (out + err).strip()[-160:]))

        hook(tmp, EMPTY, "Delete them")
        B = "RIMMANDRAKE_PROBE_EMPTY_DESCRIPTION_CARD_FIXTURE"
        rc, out, err = run(tmp, "file", B, "--for", "BUILD", "--title", "t",
                           "--by-card", "Delete the four old placeholder files? → Delete them")
        evb = last_for(tmp, B) or {}
        check(rc == 0 and ((evb.get("card") or {}).get("questions") or [{}])[0].get("picked", [{}])[0].get("label") == "Delete them",
              "empty: a card with no description still stamps (%d %s)" % (rc, err.strip()[-160:]))
        check("## What the card said" in prose(tmp, B) and "Its description" not in prose(tmp, B),
              "empty: its prose section has no empty description line")
        check(DH.card_refusal(B, "delete the files", events_dir=shards) is None, "empty: nothing to paste, launch passes")

        C = "RIMMANDRAKE_PROBE_PLAIN_ITEM_NO_CARD_FIXTURE"
        rc, out, err = run(tmp, "file", C, "--for", "BUILD", "--title", "t")
        evc = last_for(tmp, C) or {}
        check(rc == 0 and "card" not in evc and "byCard" not in evc, "plain: a non-card item carries no card")
        check("What the card said" not in prose(tmp, C), "plain: no card section in its prose")
        check(DH.card_refusal(C, "anything", events_dir=shards) is None, "plain: launch is not refused")
        rc, out, err = run(tmp, "close", C, "--no-code", "nothing", "--why", "done")
        check(closed(tmp, C), "plain: close unaffected (%d %s)" % (rc, err.strip()[-160:]))

        tx = {"type": "user", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()), "sessionId": "s2",
              "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_tx"}]},
              "toolUseResult": {"questions": [TX], "answers": {TX_Q: "Decide after the walk"}, "annotations": {}}}
        with open(os.path.join(tmp, "transcripts", "s2.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "user", "message": {"content": "hi"}}) + "\n" + json.dumps(tx) + "\n")
        D = "RIMMANDRAKE_PROBE_TRANSCRIPT_ONLY_CARD_FIXTURE"
        rc, out, err = run(tmp, "file", D, "--for", "BUILD", "--title", "t",
                           "--by-card", "Which scene should be Graffiti's face? → Decide after the walk")
        evd = last_for(tmp, D) or {}
        check(rc == 0 and TX_DESC in json.dumps(evd.get("card")), "transcript: a card the hook never saw is found and stamped")

        E = "RIMMANDRAKE_PROBE_BARE_BY_CARD_FIXTURE"
        rc, out, err = run(tmp, "file", E, "--for", "BUILD", "--title", "t", "--by-card")
        eve = last_for(tmp, E) or {}
        check(rc == 0 and (eve.get("card") or {}).get("questions") and "→" in eve.get("byCard", ""),
              "bare: --by-card alone takes the card answered last and writes question → label (%r)" % eve.get("byCard"))

        F = "RIMMANDRAKE_PROBE_UNMATCHED_CARD_TEXT_FIXTURE"
        rc, out, err = run(tmp, "file", F, "--for", "BUILD", "--title", "t", "--by-card", "Some other question → Nope")
        evf = last_for(tmp, F) or {}
        check(rc == 0 and "card" not in evf and "no answered card" in err,
              "unmatched: a text matching no card still records, and says so on stderr")

        rc, out, err = run(tmp, "note", C, "--text", "late relay", "--by-card",
                           "Delete the four old placeholder files? → Delete them")
        check(rc == 0 and not os.path.exists(os.path.join(tmp, "items", C + ".md")) and (last_for(tmp, C) or {}).get("card"),
              "closed: a card note on a closed item lands on the ledger but makes no live prose (%d %s)" % (rc, err.strip()[-120:]))

        import card_capture as CC
        neg = {"questions": [{"picked": [{"label": "x", "description": "Offline stages need no game; it needs nothing new "
                                          "registered. Costs: needs a person there once."}]}]}
        check(CC.consequences(neg) == ["needs a person there once"],
              "owed: a negation owes nothing, a real cost does (%r)" % CC.consequences(neg))

        overflow_cases(tmp)
        for t in (t_a_card_over_one_line_records, t_the_whole_card_reaches_the_item_prose,
                  t_picked_descriptions_stay_whole_on_the_events, t_a_card_that_fits_is_stamped_whole):
            t(tmp)

        import model  # noqa: E402
        check("card" in model.UNIVERSAL_FIELDS, "model: card is a universal field")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
