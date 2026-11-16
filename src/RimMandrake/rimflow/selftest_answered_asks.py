#!/usr/bin/env python3
"""selftest_answered_asks.py — an incident plan that asks him something he has since answered is not raised again.

Item RIMMANDRAKE_STOP_ANSWERED_ASKS_RERAISED_THIRD_TIME_TO_HIM. 2026-11-15: the plan of incident refusals-20261115061558
(acked 22:42Z) said "brings Pyrelands to him on one card ... reword the bar to 'largest of the roster'". He answered that
card at 23:52:53Z ("Keep 'twice', raise body to 9+") and the work was built, but nothing touched the plan. A fresh
Conductor window read it from `rimflow incidents` at 6:11 PM PST and raised the answered question to him again at 6:11
and 6:42 PM ("This is the third time this has come to me."). The fixture below is that plan and that card, verbatim.

  exact       the 22:42Z plan + the 23:52:53Z card -> answered, by card, naming the question and his pick
  reacked     a plan written after the card (the 03:29Z correction) -> not answered
  before      a card answered before the plan -> not answered
  unrelated   a card on another subject answered after the plan -> not answered
  no ask      a plan that asks nothing of him -> not answered
  owner-said  his --owner-said on the subject after the plan -> answered, by owner-said; our title on his event is not
              his words
  incidents   `rimflow incidents` prints the ANSWERED line under the incident; none after the re-ack
  line        `rimflow incident-line` refuses a line on an answered ask, with the path to pass; --not-the-same-ask passes
  blind       a torn card store: `incidents` says the check did not run and still lists; `incident-line` lets it through
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_answered_asks_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CARDS_STORE"] = os.path.join(TMP, "cards.jsonl")
os.environ["RM_OWNER_EVENTS"] = os.path.join(TMP, "owner.jsonl")
os.makedirs(os.environ["RM_OPS_WATCH_DIR"])
import incident as IN  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append(name)
        if detail:
            print("      %s" % str(detail)[:1500])


PLAN_2242 = (
    "Measured 14:45 PST: the new trip is concept:Pyrelands round 7 (the one final look, 2b9f9817e7), not_covered on ONE "
    "gap g1 (furnacebeast_warms/inv_furnacebeast): the judge itself rates that criterion UNATTAINABLE (scenes.json:688 "
    "asks body size >= 2x every roster kind, but his ruled size is 6 and RSW_Zeer is 4.5), so no build can pass it; it "
    "is a criterion repair for the neutral fixer, not builder work. The other 7 alarm rows are standing (owner holds, "
    "ExplosiveKnockback owner-passed, family/item counters). Next: the Conductor's next owner-facing turn brings "
    "Pyrelands to him on one card with that evidence (obvious answer: let the neutral fixer reword the bar to 'largest "
    "of the roster' and release one look); per his card a final-look not_covered is his. Closes when the Pyrelands row "
    "is released.")
PLAN_0329 = "CORRECTED 7:30 PM PST: the Pyrelands giant question is NOT open and must not go to him again. He answered it by card 2026-11-15 3:53 PM PST (keep 'twice', raise body to 9+, new bigger art); built and closed: RIMMANDRAKE_ENLARGE_FURNACE_BEAST_TWICE_THE_ZEER_MEANS_NINE, RIMMANDRAKE_REDRAW_FURNACE_BEAST_BIGGER_ART_CARD_PROMISED_IT. This plan's old text raised it to him a third time (owner, 7:28 PM PST: 'This is the third time this has come to me.'). Root-cause run: RIMMANDRAKE_STOP_ANSWERED_ASKS_RERAISED_THIRD_TIME_TO_HIM."   # the real 03:29:11Z correction, verbatim
GIANT_CARD = {
    "answered": "2026-11-15T23:52:53Z", "session": "30f9cab8-cdb8-4eef-9c39-30604268f2a8", "key": "toolu_giant",
    "questions": [{
        "question": "Pyrelands failed its final look on one bar: the furnace-beast (the biome's giant) must be twice the "
                    "body size of every other animal there. That cannot pass: a patched-in animal, the Zeer, is body "
                    "size 4.5, the furnace-beast is 6 (your ruled size), and twice 4.5 is 9. Also, the furnace-beast is "
                    "drawn at 5.5 while the Zeer is drawn at 6, so the giant looks smaller. 'Drawn size' is how big the "
                    "sprite appears; 'body size' is the game stat for health, meat and carrying. How should the giant "
                    "be made the giant?",
        "header": "Furnace size", "answer": "Keep 'twice', raise body to 9+",
        "picked": [{"label": "Keep 'twice', raise body to 9+",
                    "description": "Why: holds the original promise literally, a giant twice anything on the map. Buys "
                                   "an unmistakable giant with no bar change. Costs: overturns your ruled body size of "
                                   "6, changes its health, meat and combat balance, needs bigger art, and breaks again "
                                   "if a larger animal is ever patched in."}],
        "his_words": "", "others": ["Reword bar, draw it bigger (Recommended)", "Move the Zeer out of the Pyrelands",
                                    "Pass it as is, list as polish"]}]}
QUOTA_CARD = {
    "answered": "2026-11-16T00:30:00Z", "session": "s", "key": "toolu_quota",
    "questions": [{"question": "Operations proposes pulling work forward. The system account has 50% of its week left "
                               "with 97 h to reset; the lukas account has 100% left. Spend the spare quota now?",
                   "header": "Spare quota", "answer": "More helpers now (Recommended)", "picked": [], "his_words": "",
                   "others": []}]}
T_2242 = 1794782546.7705762          # 2026-11-15T22:42:26Z, the real ack
T_0329 = 1794799751.0                # 2026-11-16T03:29:11Z


def inc(plan, t):
    return {"id": "refusals-20261115061558", "state": "open", "plan": plan, "acked_t": t, "told_t": t - 60}


# ------------------------------------------------------------------ pure
hit = IN.answered_since(inc(PLAN_2242, T_2242), [GIANT_CARD], [])
check("exact: the 22:42Z plan is answered by the 23:52:53Z giant card",
      bool(hit) and hit["by"] == "card" and "made the giant" in hit["what"] and "Keep 'twice'" in hit["what"], hit)
check("exact: the hit names when (his answer's time) and the shared subject words",
      bool(hit) and hit["at"] == "2026-11-15T23:52:53Z" and {"pyrelands", "zeer"} <= set(hit["shared"]), hit)
check("reacked: a plan written after the card is not answered",
      IN.answered_since(inc(PLAN_0329, T_0329), [GIANT_CARD], []) is None)
early = dict(GIANT_CARD, answered="2026-11-15T22:00:00Z")
check("before: a card answered before the plan does not answer it",
      IN.answered_since(inc(PLAN_2242, T_2242), [early], []) is None)
check("unrelated: a card on another subject answered after the plan does not answer it",
      IN.answered_since(inc(PLAN_2242, T_2242), [QUOTA_CARD], []) is None)
noask = PLAN_2242.replace("brings Pyrelands to him on one card", "lets the neutral fixer act").replace(
    "per his card a final-look not_covered is his", "").replace("owner holds", "holds").replace(
    "his ruled size", "the ruled size").replace("owner-facing", "next")
check("no ask: a plan that asks nothing of him is not flagged", IN.answered_since(inc(noask, T_2242), [GIANT_CARD], []) is None,
      noask)
said = {"seat": "OWNER", "event": "note", "id": "RIMMANDRAKE_ENLARGE_FURNACE_BEAST_TWICE_THE_ZEER_MEANS_NINE",
        "ownerSaid": "Pyrelands final look: keep the bar, the furnace-beast body size goes to 9, twice the Zeer's 4.5; "
                     "the ruled size of 6 is overturned. Draw it bigger.",
        "ts": "2026-11-16T00:05:00Z"}
h2 = IN.answered_since(inc(PLAN_2242, T_2242), [], [said])
check("owner-said: his words on the subject after the plan answer it", bool(h2) and h2["by"] == "owner-said", h2)
filed = {"seat": "OWNER", "event": "file", "id": "RIMMANDRAKE_STOP_ANSWERED_ASKS_RERAISED_THIRD_TIME_TO_HIM",
         "title": "An ask he already answered reached him again: the Pyrelands giant criterion, answered by card "
                  "2026-11-15 3:53 PM PST and built, was raised a third time at 6:10 and 6:41 PM PST from the stale plan "
                  "text of incident refusals-20261115061558.", "ownerSaid": "This is the third time this has come to me.",
         "ts": "2026-11-16T03:29:13Z"}
check("owner-said: our title on his event is not his words (the live false hit on the 03:29Z correction)",
      IN.answered_since(inc(PLAN_0329, T_0329), [], [filed]) is None)
check("owner-said: his words before the plan do not",
      IN.answered_since(inc(PLAN_2242, T_2242), [], [dict(said, ts="2026-11-15T20:00:00Z")]) is None)

# ------------------------------------------------------------------ the CLI, on a fixture told.jsonl
told = os.path.join(os.environ["RM_OPS_WATCH_DIR"], "told.jsonl")
with open(told, "w") as f:
    for r in ({"ev": "opened", "id": "refusals-20261115061558", "at": "2026-11-15T06:15:58Z", "t": 1794730558.0,
               "state": "open", "class": "distressed", "cause": "refusals", "rung": 0, "reader": "Conductor",
               "told_at": "2026-11-15T06:15:58Z", "told_t": 1794730558.0, "metrics": {"REFUSAL_NOTHING_COULD_EVER_PASS": 1}},
              {"ev": "acked", "id": "refusals-20261115061558", "at": "2026-11-15T22:42:26Z", "t": T_2242, "acked_t": T_2242,
               "ack_by": "OWNER", "plan": PLAN_2242, "auto_ack": False}):
        f.write(json.dumps(r) + "\n")
with open(os.environ["RM_CARDS_STORE"], "w") as f:
    f.write(json.dumps(GIANT_CARD) + "\n" + json.dumps(QUOTA_CARD) + "\n")
open(os.environ["RM_OWNER_EVENTS"], "w").close()

ENV = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID",
                                                        "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT")}
ENV.update(RIMFLOW_LEDGER=os.path.join(TMP, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(TMP, "items"),
           RIMFLOW_PROBE="no-reading", RIMFLOW_SEAT="BENCH")
open(ENV["RIMFLOW_LEDGER"], "w").close()


def cli(*args):
    p = subprocess.run([sys.executable, CLI] + list(args), capture_output=True, text=True, env=ENV, timeout=120)
    return p.returncode, p.stdout + p.stderr


rc, out = cli("incidents")
check("incidents: the stale plan is listed with an ANSWERED line naming his card and pick",
      rc == 0 and "ANSWERED after this plan" in out and "made the giant" in out and "Keep 'twice'" in out, out)
check("incidents: the ANSWERED line tells the reader not to raise it and how to clear it",
      "do not raise" in out.lower() and "rimflow ack refusals-20261115061558" in out, out)
rc, out = cli("incident-line", "refusals-20261115061558", "Pyrelands is blocked on the giant bar; reword it?")
check("line: a line on an answered ask is refused, naming the card and the path to pass",
      rc != 0 and "made the giant" in out and "--not-the-same-ask" in out and "rimflow ack" in out, out)
check("line: the refusal wrote nothing", "ev\": \"line" not in open(told).read())
rc, out = cli("incident-line", "refusals-20261115061558", "Another Pyrelands matter.", "--not-the-same-ask",
              "this line is about the spend ceiling, not the giant")
check("line: --not-the-same-ask writes the line", rc == 0 and '"ev": "line"' in open(told).read(), out)
rc, out = cli("ack", "refusals-20261115061558", "--plan", PLAN_0329)
rc, out = cli("incidents")
check("incidents: after a re-ack written after the card, no ANSWERED line", rc == 0 and "ANSWERED after this plan" not in out, out)

with open(os.environ["RM_CARDS_STORE"], "a") as f:
    f.write("{torn\n")
with open(told, "a") as f:
    f.write(json.dumps({"ev": "acked", "id": "refusals-20261115061558", "at": "2026-11-15T23:00:00Z", "t": T_2242 + 1000,
                        "acked_t": T_2242 + 1000, "ack_by": "OWNER", "plan": PLAN_2242, "auto_ack": False}) + "\n")
rc, out = cli("incidents")
check("blind: a torn card store says the check did not run and still lists the incident",
      rc == 0 and "did not run" in out and "refusals-20261115061558" in out, out)
rc, out = cli("incident-line", "refusals-20261115061558", "a line while the check is blind")
check("blind: incident-line lets the line through and says the check did not run", rc == 0 and "did not run" in out, out)

shutil.rmtree(TMP, ignore_errors=True)
print("%d fail(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
