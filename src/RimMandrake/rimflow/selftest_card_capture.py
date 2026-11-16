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
              "launch: a brief missing the description is refused, naming the text and the fix (%r)" % (why or "")[:120])
        check(DH.card_refusal(A, good, events_dir=shards) is None, "launch: a brief holding the description verbatim passes")
        check(DH.card_refusal(A, good.replace(". Costs", ".   Costs").replace("'", "’"), events_dir=shards) is None,
              "launch: whitespace and curly quotes do not refuse a verbatim paste")
        rc, text = DH.launch("BENCH", A, bad, "opus", None, 1, known={A}, runner=lambda *a, **k: None,
                             events_dir=shards)
        check(rc == 2 and "needs bigger art" in text, "launch: launch() itself refuses the short brief before any clone")
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

        import model  # noqa: E402
        check("card" in model.UNIVERSAL_FIELDS, "model: card is a universal field")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
