#!/usr/bin/env python3
"""selftest_owner_words_not_refused.py - the owner's word and the Conductor's act are never refused for provenance
(RIMMANDRAKE_STOP_GATES_DEMANDING_OWNER_WORDS_HE_ALREADY_SPOKE; owner 2026-11-20: "The system should not be refusing
needed items. The system should not be in our way. Make it so.").

Each case runs the real code, in a throwaway ledger or a fixture card store:
  launch-adds-card-text   detached_helper.launch never refuses a by-card brief for its card text; card_repair adds it
  note-silent-if-covered  promise_scan stays silent on a promise an open owed item covers; the hook's line is a note
  close-conductor-act     `rimflow close` from the Conductor window with --per-ruling RULING closes with no level-tagged
                          pass, recorded `uncheckedLifted`; his --owner-said does too
  his-question-recorded   `--owner-said` records his words ending in "?" (and a bare "yes"), never refuses them
  either-conductor-ruling a his-words gate (conductor_authority.carried) takes either of the Conductor's two rulings
  kept guards (planted)   a launched run citing RULING is refused; a helper citing another ruling, or no flag, is still
                          refused `unchecked`; a promise no owed item covers still shows

    python3 src/RimMandrake/rimflow/selftest_owner_words_not_refused.py      exit 0 PASS, 1 FAIL
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CLI = os.path.join(HERE, "cli.py")
HOOK = os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
os.environ.setdefault("RM_UNDER_SELFTEST", "1")

FAILS = []
RULING = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"
CARD_ITEM = "RIMMANDRAKE_PROBE_OWNER_WORDS_CARD_FIXTURE"
DESC = "Rebuild the pits as superdeep cells, and it needs a live visit before the close."
CARD = {"answered": "2026-11-20T09:40:00Z", "questions": [{
    "question": "Rebuild FlowWorks pits now?", "picked": [{"label": "Rebuild now", "description": DESC}],
    "others": ["Wait"], "his_words": ""}]}


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + str(detail)[-300:] if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def t_launch_adds_card_text():
    import detached_helper as DH
    tmp = tempfile.mkdtemp(prefix="owner_words_card_")
    ev_dir = os.path.join(tmp, "events")
    os.makedirs(ev_dir)
    with open(os.path.join(ev_dir, "OWNER.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"event": "file", "id": CARD_ITEM, "tsn": 1, "card": CARD}) + "\n")
    short = "# Fix the pits\n\nRebuild them.\n"
    repair = getattr(DH, "card_repair", None)
    check("launch-adds-card-text: card_repair exists", callable(repair))
    if callable(repair):
        fixed, added = repair(CARD_ITEM, short, events_dir=ev_dir)
        check("launch-adds-card-text: the card's words are added", added and DESC in fixed, fixed)
        same, added2 = repair(CARD_ITEM, fixed, events_dir=ev_dir)
        check("launch-adds-card-text: a brief that carries them is left as it is", not added2 and same == fixed)
        plain, added3 = repair("RIMMANDRAKE_PROBE_NO_CARD_FIXTURE", short, events_dir=ev_dir)
        check("launch-adds-card-text: an item with no card is untouched", not added3 and plain == short)
    try:
        rc, text = DH.launch("BENCH", CARD_ITEM, short, "opus", None, 1, known={CARD_ITEM},
                             runner=lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "fake runner"),
                             events_dir=ev_dir)
    except Exception as e:  # noqa: BLE001  the fake runner may stop it later; only the card refusal matters here
        rc, text = 1, "%s: %s" % (type(e).__name__, e)
    check("launch-adds-card-text: launch() does not refuse for the card text",
          "decided by card" not in text, "%d %s" % (rc, text))


def t_note_silent_if_covered():
    import promise_scan as PS
    items = {"RIMMANDRAKE_LAUNCH_PITS_FIXER_OWED": ("launch the FlowWorks pits fixer", "RIMMANDRAKE_PITS_TARGET")}
    try:
        got = PS.scan("When the slot frees I will launch the FlowWorks pits fixer.", owed_items=items)
        check("note-silent-if-covered: a title-covered promise is silent", got == [], got)
        got = PS.scan("I will relaunch RIMMANDRAKE_PITS_TARGET tonight.", owed_items=items)
        check("note-silent-if-covered: a promise naming the owed item's target is silent", got == [], got)
        got = PS.scan("I will write the art judge's summary.", owed_items=items)
        check("kept: a promise no owed item covers still shows", len(got) == 1, got)
    except TypeError as e:
        check("note-silent-if-covered: scan takes owed_items", False, e)
    src = open(HOOK, encoding="utf-8").read()
    check("note-silent-if-covered: the hook's line is a note, never a demand",
          "say it is not a promise" not in src and "NOTE, nothing blocked" in src)


def _git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()


def _code_sha():
    import live_line
    for sha in _git("log", "origin/main", "--format=%H", "-n", "300", "--", "src/RimMandrake/Utils/").split():
        paths = _git("diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split()
        if paths and not live_line.needs_line(paths):
            return sha
    return None


def t_close_conductor_act():
    tmp = tempfile.mkdtemp(prefix="owner_words_close_")
    ledger, items = os.path.join(tmp, "events.jsonl"), os.path.join(tmp, "items")
    os.makedirs(os.path.join(items, "closed"))

    def cli(*args, seat="BENCH", unit=None):
        env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID",
                                                                 "RIMFLOW_GITINDEX", "RM_ROLE_UNIT")}
        env.update(RIMFLOW_LEDGER=ledger, RIMFLOW_ITEMS=items, RIMFLOW_SEAT=seat, AGENT_SEAT=seat)
        if unit:
            env["RM_ROLE_UNIT"] = unit
        r = subprocess.run([sys.executable, CLI, *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def state(iid):
        from rimflow import model
        model.EVENTS = ledger
        return model.replay(model.read()).items[iid]

    sha = _code_sha()
    if not sha:
        check("close-conductor-act: a code commit to close against", False, "UNMEASURED: none in the last 300")
        return
    cli("file", RULING, "--for", "BENCH", "--title", "the ruling, fixture")
    names = {}
    for k in ("CONDUCTOR", "OWNERSAID", "HELPER", "OTHER", "PLAIN"):
        iid = "RIMMANDRAKE_PROBE_CLOSE_%s_FIXTURE" % k
        names[k] = iid
        cli("file", iid, "--for", "BENCH", "--title", "fixture")
        cli("claim", iid)
    why = "closing on the owner's order, the work is landed and seen"
    rc, out = cli("close", names["CONDUCTOR"], "--sha", sha, "--per-ruling", RULING, "--why", why)
    it = state(names["CONDUCTOR"])
    check("close-conductor-act: the Conductor's act closes with no level-tagged pass",
          rc == 0 and it.state == "done", "%d %s" % (rc, out))
    evs = [json.loads(l) for l in open(ledger, encoding="utf-8")] if os.path.exists(ledger) else []
    shard_dir = os.path.join(tmp, "events")
    for fn in (os.listdir(shard_dir) if os.path.isdir(shard_dir) else []):
        evs += [json.loads(l) for l in open(os.path.join(shard_dir, fn), encoding="utf-8") if l.strip()]
    closes = [e for e in evs if e.get("event") == "close" and e.get("id") == names["CONDUCTOR"]]
    check("close-conductor-act: the event records uncheckedLifted",
          bool(closes) and closes[-1].get("uncheckedLifted") is True, closes)
    rc, out = cli("close", names["OWNERSAID"], "--sha", sha, "--owner-said", "close it, it is done")
    check("close-conductor-act: his --owner-said closes with no level-tagged pass",
          rc == 0 and state(names["OWNERSAID"]).state == "done", "%d %s" % (rc, out))
    rc, out = cli("close", names["HELPER"], "--sha", sha, "--per-ruling", RULING, "--why", why, unit="rm-helper-x")
    check("kept: a launched run citing the Conductor's ruling is refused",
          rc != 0 and state(names["HELPER"]).state != "done", "%d %s" % (rc, out))
    rc, out = cli("close", names["OTHER"], "--sha", sha, "--per-ruling", names["PLAIN"], "--why", why)
    check("kept: a close citing another ruling is still refused unchecked",
          rc != 0 and "unchecked" in out and state(names["OTHER"]).state != "done", "%d %s" % (rc, out))
    rc, out = cli("close", names["PLAIN"], "--sha", sha, "--why", "done")
    check("kept: a seat's own close is still refused unchecked",
          rc != 0 and "unchecked" in out and state(names["PLAIN"]).state != "done", "%d %s" % (rc, out))
    check("close-conductor-act: the refusal names the Conductor's act as the way through",
          RULING in out and "Only the owner's word" not in out, out)


def t_his_question_is_recorded():
    tmp = tempfile.mkdtemp(prefix="owner_words_said_")
    ledger, items = os.path.join(tmp, "events.jsonl"), os.path.join(tmp, "items")
    os.makedirs(os.path.join(items, "closed"))
    env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID",
                                                             "RIMFLOW_GITINDEX", "RM_ROLE_UNIT")}
    env.update(RIMFLOW_LEDGER=ledger, RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH", AGENT_SEAT="BENCH")
    q = "Could you make a big excel spreadsheet of all the minerals in the game?"
    for iid, said in (("RIMMANDRAKE_PROBE_SAID_QUESTION_FIXTURE", q), ("RIMMANDRAKE_PROBE_SAID_ASSENT_FIXTURE", "yes")):
        r = subprocess.run([sys.executable, CLI, "file", iid, "--for", "BENCH", "--title", "fixture", "--owner-said", said],
                           cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
        text = ""
        for root, _, files in os.walk(tmp):
            for fn in files:
                if fn.endswith(".jsonl"):
                    text += open(os.path.join(root, fn), encoding="utf-8").read()
        check("his-question-recorded: %r is recorded as his words" % said[:30],
              r.returncode == 0 and json.dumps(said)[1:-1] in text, (r.stdout + r.stderr)[-300:])


def t_either_conductor_ruling():
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    import conductor_authority as CA
    check("either-conductor-ruling: the Conductor's act ruling is carried",
          CA.carried(RULING, "the Conductor sets two slots for the night"))
    check("either-conductor-ruling: the authority ruling is carried",
          CA.carried(CA.RULING, "the Conductor sets two slots for the night"))
    check("kept: another ruling carries nothing", not CA.carried("BIOME_SPECIFIC_FAUNA_LAW_1", "a reason"))
    check("kept: a ruling with no Conductor text carries nothing", not CA.carried(RULING, " "))


def main():
    for t in (t_launch_adds_card_text, t_note_silent_if_covered, t_close_conductor_act, t_his_question_is_recorded,
              t_either_conductor_ruling):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    print("selftest_owner_words_not_refused: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
