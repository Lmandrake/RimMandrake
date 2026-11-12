#!/usr/bin/env python3
"""Selftest for agent_improve.py gather: routing, recurrence, the day bound, the caps, and that a lonely piece is
not signalled. Every source is a temp fixture; the real store, alarms and ledger are never read."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agent_improve as A  # noqa: E402

fails = []


def check(name, cond, detail=""):
    if not cond:
        fails.append(name)
        print("FAIL: %s %s" % (name, detail))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# home normalisation: every form the corpus uses
for home, want in [("rimworld-modding", "rimworld-modding"), ("skills/rimbridge/references/traps.md", "rimbridge"),
                   ("skill: using-rimflow", "using-rimflow"), ("skill:git-efficiency", "git-efficiency"),
                   ("`rimworld-deploy`", "rimworld-deploy"), ("NONE", None), ("", None), (None, None),
                   ("infrastructure/state/facts/instrument_traps.md", "instrument_traps.md")]:
    check("norm_target %r" % home, A.norm_target(home) == want, "got %r" % A.norm_target(home))

with tempfile.TemporaryDirectory() as root:
    les = os.path.join(root, "lessons")
    store = os.path.join(root, "store")
    alarms = os.path.join(root, "alarms.json")
    owner = os.path.join(root, "OWNER.jsonl")
    # lessons: skill-a twice on the day (recurs); skill-b once on the day plus once 3 days before (recurs in window);
    # skill-c once only (not signalled); skill-d only on another day (not today's); one with no home (unrouted? no:
    # a homeless lesson has no target and is not owner words, so it is dropped from targets but counted today)
    write(os.path.join(les, "20261101T010000Z-BENCH-a1.md"), "Skill A trap one\nhome: skill-a\n")
    write(os.path.join(les, "20261101T020000Z-FOUNDRY-a2.md"), "Skill A trap two\nhome: skills/skill-a/SKILL.md\n")
    write(os.path.join(les, "20261101T030000Z-BENCH-b1.md"), "Skill B today\nhome: skill: skill-b\n")
    write(os.path.join(les, "20261029T030000Z-BENCH-b0.md"), "Skill B earlier\nhome: skill-b\n")
    write(os.path.join(les, "20261101T040000Z-BENCH-c1.md"), "Skill C lonely\nhome: skill-c\n")
    write(os.path.join(les, "20261102T000000Z-BENCH-d1.md"), "Skill D next day\nhome: skill-d\n")
    write(os.path.join(les, "20261020T000000Z-BENCH-d0.md"), "Skill D long ago\nhome: skill-d\n")
    write(os.path.join(les, "README.md"), "not a lesson\n")
    # relentless: two rejects and a finish on the day, a start row with no end, a learned line, an alarm
    rows = [{"at": "2026-11-01T05:00:00Z", "end": "blind_fail", "detail": "proof did not run the clause"},
            {"at": "2026-11-01T06:00:00Z", "end": "finish"},
            {"at": "2026-11-01T06:30:00Z", "gen": 3},
            {"at": "2026-10-31T23:59:59Z", "end": "proof_weak", "detail": "yesterday"},
            {"at": "2026-11-01T07:00:00Z", "end": "proof_weak", "detail": "no red seen"}]
    write(os.path.join(store, "items", "ITEM_ONE", "attempts.jsonl"), "".join(json.dumps(r) + "\n" for r in rows)
          + "not json\n")
    write(os.path.join(store, "items", "ITEM_ONE", "learned.md"),
          "# learned\n- 2026-11-01T08:00:00Z gen 2: the deploy plan needs --apply\n"
          "- 2026-10-30T08:00:00Z gen 1: older line\n")
    write(os.path.join(store, "journal.jsonl"),
          json.dumps({"at": "2026-11-01T09:00:00Z", "do": "alarm", "kind": "remove_failed", "why": "gone",
                      "clone": "/r/clones/WIDGET_REPAIR_SHAPE.q2"}) + "\n"
          + json.dumps({"at": "2026-10-20T09:00:00Z", "do": "alarm", "kind": "understaffed", "why": "breaker open"}) + "\n"
          + json.dumps({"at": "2026-11-01T09:00:00Z", "do": "tick"}) + "\n")
    write(alarms, json.dumps({"X": {"name": "OPS_X", "title": "disk full", "since": "2026-11-01T10:00:00Z"},
                              "Y": {"name": "OPS_Y", "title": "old", "since": "2026-10-01T10:00:00Z"}}))
    write(owner, json.dumps({"seat": "OWNER", "event": "note", "id": "SOME_ITEM", "ownerSaid": "do it this way",
                             "ts": "2026-11-01T11:00:00Z"}) + "\n"
          + json.dumps({"seat": "OWNER", "event": "note", "id": "SOME_ITEM", "text": "no words",
                        "ts": "2026-11-01T11:00:00Z"}) + "\n")
    src = {"lessons": les, "store": store, "ops_alarms": alarms, "owner": owner}

    pk = A.gather("2026-11-01", src)
    names = [t["target"] for t in pk["targets"]]
    by = {t["target"]: t for t in pk["targets"]}
    check("relentless signalled first", names and names[0] == "relentless", names)
    check("relentless counts rejects, learned, alarm; not finish or no-end",
          by.get("relentless", {}).get("kinds") == {"reject:blind_fail": 1, "reject:proof_weak": 1, "learned": 1,
                                                   "alarm:remove_failed": 1}, by.get("relentless", {}).get("kinds"))
    al = [p for p in by.get("relentless", {}).get("pieces", []) if p["kind"] == "alarm:remove_failed"]
    check("an alarm names its own item (clones/<item>[.qN]), so it carries that item's kind (4.3)",
          al and al[0]["text"] == "WIDGET_REPAIR_SHAPE: gone" and A.task_kind(al[0]) == "REPAIR", al)
    bare = A.relentless_pieces(store, A.day_bounds("2026-10-20")[0], A.day_bounds("2026-10-20")[1])
    check("an alarm with no item keeps its bare why and no kind",
          [(p["text"], A.task_kind(p)) for p in bare] == [("breaker open", None)], bare)
    # a lesson's item: footer is its kind and is never second-guessed from the text (design 4.3)
    lk = os.path.join(root, "lessons_kinds")
    for name, body in [("own", "Names WIDGET_REPAIR_SHAPE first.\nitem: GADGET_BUILD_FRAME\nhome: x\n"),
                       ("none", "Names WIDGET_REPAIR_SHAPE.\nitem: NONE\nhome: x\n"),
                       ("legacy", "Names WIDGET_REPAIR_SHAPE.\nitem: SEA_DIVE_HATCH_REMOVE_1\nhome: x\n"),
                       ("quoted", "Names WIDGET_REPAIR_SHAPE.\nitem: NONE\nquoted from a log, not the footer\nhome: x\n"),
                       ("bare", "Names WIDGET_REPAIR_SHAPE.\nhome: x\n")]:
        write(os.path.join(lk, "20261101T010000Z-BENCH-%s.md" % name), body)
    got = {os.path.basename(p["path"])[23:-3]: A.task_kind(p) for p in A.lesson_pieces(lk, 0, 2 ** 31)}
    check("lesson kinds: footer item, NONE, kindless own item, a quoted item: line, none recorded",
          got == {"own": "BUILD", "none": None, "legacy": None, "quoted": "REPAIR", "bare": "REPAIR"}, got)
    check("skill-a recurs on the day", "skill-a" in names, names)
    check("skill-b recurs over the window", "skill-b" in names and by["skill-b"]["window_count"] == 2, names)
    check("skill-c lonely, not signalled", "skill-c" not in names and "skill-c" in pk["unsignalled"], pk["unsignalled"])
    check("skill-d not today", "skill-d" not in names and "skill-d" not in pk["unsignalled"])
    check("operations: one alarm today is not a recurrence", "operations" in pk["unsignalled"], pk["unsignalled"])
    check("owner words unrouted", [p["kind"] for p in pk["unrouted"]] == ["owner_said"], pk["unrouted"])
    check("day bound excludes 23:59:59 the day before",
          all("yesterday" not in p["text"] for t in pk["targets"] for p in t["pieces"]))
    md = A.render(pk)
    check("render names each target", all("## %s " % n in md for n in names), md)

    # the target cap keeps agents first and reports the rest; the piece cap keeps one of each kind
    A.MAX_TARGETS, A.MAX_PIECES = 2, 3
    pk2 = A.gather("2026-11-01", src)
    check("target cap", len(pk2["targets"]) == 2 and pk2["dropped_over_cap"], pk2)
    check("cap keeps the agent", pk2["targets"][0]["target"] == "relentless")
    rk = pk2["targets"][0]
    check("piece cap", len(rk["pieces"]) == 3 and rk["today"] == 4, rk)
    check("piece cap keeps distinct kinds", len({p["kind"] for p in rk["pieces"]}) == 3, rk["pieces"])
    check("render says showing", "(showing 3 of 4)" in A.render(pk2))

    # an empty day writes an empty packet, never an error
    pk3 = A.gather("2026-06-01", src)
    check("empty day", pk3["pieces_today"] == 0 and pk3["targets"] == [], pk3)

print("selftest_agent_improve: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
