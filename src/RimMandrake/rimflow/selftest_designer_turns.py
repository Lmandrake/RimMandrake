#!/usr/bin/env python3
"""selftest_designer_turns.py - DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP.

A Designer turn that closes waiting_owner must reach the owner wherever he looks, and stay there until an OWNER event
answers it: designer_stage.pending_turns -> owner_queue.needs_you (NEEDS YOU), running_now's Needs-you box (RUNNING
NOW), seat_restart's wake, and role_launch's escalation line in the Conductor's log. And the stale-clone trap: the
Dispatcher's clone was behind origin and refused "WAITING_OWNER: no new owner event" with his answer already published;
role_launch.judge_sync fetches and designer_stage reads origin/main's OWNER.jsonl too.

    python3 src/RimMandrake/rimflow/selftest_designer_turns.py
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (HERE, UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

FAILS = []
ITEM = "FOO_SCRIPT_MEASURE_PREP"


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (str(got)[:600],)))
    if not ok:
        FAILS.append(name)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def owner_ev(shard, item, t, event="note", **kw):
    with open(shard, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict({"seat": "OWNER", "event": event, "id": item, "ts": iso(t), "tsn": int(t * 1e9)},
                                **kw)) + "\n")


def waiting_concept(d, repo, closed_at, asks=("ask_prisoner", "ask_match")):
    """A concept whose stage-2 turn closed waiting_owner at `closed_at`, the way close_run leaves it."""
    DS.init(d, "Foo", ITEM, cap=100000, reserve=10000)
    st = DS.load_state(d)
    st.update(stage=2, status="waiting_owner")
    st["results"].append({"stage": 2, "outcome": "waiting_owner", "run": "rm-role-designer-7", "at": iso(closed_at),
                          "summary": "Turn 2 sent (design/concepts/Foo/turn_02.md): two edges"})
    st["waiting_owner_feed"] = DS.owner_feed(repo, ITEM, d)
    DS.write_json(DS.state_path(d), st)
    with open(os.path.join(d, "record.json"), "w") as f:
        json.dump({"asks": [{"id": a, "status": "sent", "text": "Which way for %s?" % a} for a in asks] +
                           [{"id": "ask_old", "status": "answered", "text": "an answered one"}]}, f)
    with open(os.path.join(d, "turn_01.md"), "w") as f:
        f.write("turn 1\n")
    with open(os.path.join(d, "turn_02.md"), "w") as f:
        f.write("turn 2\n")


class Item:
    def __init__(self, iid, title, needs=None):
        self.id, self.title, self.needs, self.open, self.history = iid, title, needs, True, []


def surfaces(root, now):
    """-> what each surface says: (pending turns, owner_queue line, needs_you, RUNNING NOW box, wake text)."""
    import owner_queue as OQ
    import running_now as RN
    import seat_restart as SR
    turns, bad = DS.pending_turns(root)
    oq = OQ.designer_turns(root)
    n = OQ.needs_you({ITEM: Item(ITEM, "the concept's own item")}, {}, questions={}, evs=[], turns=oq)
    box = RN.needs_html({"fleet": {"mods": [], "good_t": now, "needs": n}, "now": now, "showings": {}})
    real = DS.concepts_root
    DS.concepts_root = lambda *a: root
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            SR._wake_designer_turns()
    finally:
        DS.concepts_root = real
    return turns, bad, oq, n, box, buf.getvalue()


def doorstep(tmp):
    now = time.time()
    repo = os.path.join(tmp, "clone")
    shard = os.path.join(repo, CT.OWNER_SHARD)
    os.makedirs(os.path.dirname(shard))
    owner_ev(shard, ITEM, now - 7200, text="his root, before the turn")
    root = os.path.join(repo, "design", "concepts")
    d = os.path.join(root, "Foo")
    waiting_concept(d, repo, now - 3600)
    os.makedirs(os.path.join(root, "_dry_walk"))
    DS.write_json(os.path.join(root, "_dry_walk", "stage.json"), {"status": "waiting_owner"})

    turns, bad, oq, n, box, wake = surfaces(root, now)
    check("pending_turns: the waiting turn is found, with its two sent asks and its turn file; the dry walk is not",
          len(turns) == 1 and [a["id"] for a in turns[0]["asks"]] == ["ask_prisoner", "ask_match"]
          and turns[0]["turn"].endswith("turn_02.md") and not bad, (turns, bad))
    line = oq.get(ITEM, "")
    check("owner queue: designer_turns gives the item a line naming both asks and the mirror path of turn_02.md",
          "ask_prisoner" in line and "ask_match" in line and "Foo\\turn_02.md" in line
          and line.startswith("Foo Designer turn (stage 2) waits on you"), oq)
    check("NEEDS YOU: needs_you counts the turn as his although the ledger never routed the item to him",
          n["count"] == 1 and n["lines"][0]["item"] == ITEM and "ask_prisoner" in n["lines"][0]["q"], n)
    import owner_queue as OQ
    check("is_his: an item whose Designer turn waits is his", OQ.is_his(Item(ITEM, "t"), None, [], turns=oq), "")
    n2 = OQ.needs_you({}, {}, questions={}, evs=[], turns=oq)
    check("NEEDS YOU: a turn whose item the ledger does not hold is still a line", n2["count"] == 1, n2)
    check("RUNNING NOW: the board's Needs-you box shows the turn and its asks",
          "NEEDS YOU, 1" in box and "Foo Designer turn" in box and "ask_prisoner" in box, box)
    check("wake: the seat-restart report lists the waiting turn with its asks",
          "DESIGNER TURNS WAITING ON HIM (1)" in wake and "ask_match" in wake, wake)

    # not an answer: a seat's lifecycle move recorded on OWNER.jsonl after the close, and anything naming another item
    owner_ev(shard, ITEM, now - 1800, event="lease", action="take")
    owner_ev(shard, "OTHER_ITEM", now - 1700, text="unrelated")
    owner_ev(shard, ITEM, now - 1600, text="Conductor: rerouted the concept", perRuling="SOME_RULING")
    owner_ev(shard, ITEM, now - 7000, text="an old answer of his, before the turn", ownerSaid="earlier words")
    turns, bad, oq, n, box, wake = surfaces(root, now)
    check("not an answer: an OWNER lease, a --per-ruling note, his words from before the close, a note on another "
          "item: the turn stays on every surface",
          len(turns) == 1 and n["count"] == 1 and "NEEDS YOU, 1" in box and "WAITING ON HIM (1)" in wake, (turns, n))

    # his answer: an OWNER note naming the item after the turn closed takes it off every surface
    owner_ev(shard, ITEM, now - 60, text="Answer to Designer ask_prisoner: (b)", byCard="How? -> (b)")   # his card
    turns, bad, oq, n, box, wake = surfaces(root, now)
    check("answered: pending_turns drops the turn", turns == [] and not bad, (turns, bad))
    check("answered: the owner queue and NEEDS YOU clear", oq == {} and n["count"] == 0, (oq, n))
    check("answered: the RUNNING NOW box says nothing waits", "Nothing waits on you." in box, box)
    check("answered: the wake says none wait", "Designer turns waiting on him: none" in wake, wake)

    # an unreadable state is said, never silently dropped
    bad_d = os.path.join(root, "Broken")
    os.makedirs(bad_d)
    with open(os.path.join(bad_d, "stage.json"), "w") as f:
        f.write("{not json")
    turns, bad = DS.pending_turns(root)
    oq = OQ.designer_turns(root)
    check("unreadable: a broken stage.json is UNMEASURED on the owner queue, not nothing",
          bad and "DESIGNER_TURNS_UNMEASURED" in oq, (bad, oq))
    shutil.rmtree(bad_d)
    return repo, d


def escalation(tmp, d):
    """role_launch: the run that closed waiting_owner fires a Dispatcher escalation line into the Conductor's log."""
    import role_launch as RL
    import dispatcher as D
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")
    now = time.time()
    # re-open the turn: a fresh close at `now` (the answer in doorstep() predates it)
    st = DS.load_state(d)
    st["results"][-1]["at"] = iso(now)
    DS.write_json(DS.state_path(d), st)
    rs = {"runs": [{"state": "running", "unit": "rm-role-designer-7", "at": now - 60, "day": RL.day_of(now),
                    "budget": 90000, "mode": "run", "item": "X", "concept": d, "scope": "S.scope", "marker": "M"}]}
    res = {"subtype": "success", "usage": {k: 0 for k in RL.USAGE_KEYS}}
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: [],
           "stage_close": lambda c, u, t: (True, [])}
    RL._supervise_one(row["name"], rs, dict(RL.ROLE_DEFAULTS, **row), obs, now, lambda **kw: acts.append(kw), set())
    esc = [a for a in acts if a.get("kind") == "role:%s:waiting_owner" % row["name"]]
    check("escalation: a run closing waiting_owner raises one alarm to the Conductor's log for the concept's item",
          len(esc) == 1 and esc[0].get("conductor_log") is True and esc[0].get("ticket") == ITEM
          and "question card" in esc[0].get("raise_first", ""), [(a.get("do"), a.get("kind")) for a in acts])
    log = os.path.join(tmp, "conductor_log.md")
    if esc:
        D.conductor_log({"no_handoff": {"conductor_log": log}}, esc[0], now)
    text = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
    check("escalation: the Conductor's log gets a DISPATCHER ESCALATION line with the asks and RAISE FIRST",
          "DISPATCHER ESCALATION (role:Designer:waiting_owner)" in text and "ask_match" in text
          and "RAISE FIRST" in text and "question card" in text, text)
    acts = []
    obs["stage_close"] = lambda c, u, t: (False, ["no result.json"])
    rs["runs"][0]["state"] = "running"
    RL._supervise_one(row["name"], rs, dict(RL.ROLE_DEFAULTS, **row), obs, now, lambda **kw: acts.append(kw), set())
    check("escalation: a rejected result escalates no turn", not [a for a in acts if "waiting_owner" in str(a.get("kind"))],
          [(a.get("do"), a.get("kind")) for a in acts])


def git(*a, cwd=None):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main"] + list(a),
                       cwd=cwd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout


def stale_clone(tmp):
    """The trap: the judging clone is behind origin; his answer is on origin only."""
    import role_launch as RL
    now = time.time()
    origin, seed = os.path.join(tmp, "origin.git"), os.path.join(tmp, "seed")
    git("init", "-q", "--bare", origin)
    git("clone", "-q", origin, seed)
    os.makedirs(os.path.join(seed, os.path.dirname(CT.OWNER_SHARD)))
    owner_ev(os.path.join(seed, CT.OWNER_SHARD), ITEM, now - 7200, text="his root")
    git("add", CT.OWNER_SHARD, cwd=seed)
    git("commit", "-q", "-m", "seed", cwd=seed)
    git("push", "-q", "origin", "HEAD:main", cwd=seed)
    disp, bench = os.path.join(tmp, "dispatch"), os.path.join(tmp, "bench")
    git("clone", "-q", origin, disp)
    git("clone", "-q", origin, bench)
    d = os.path.join(tmp, "concepts_outside_any_clone", "Foo")     # judged only from the dispatch clone's ledger
    waiting_concept(d, disp, now - 3600)
    check("stale: the fixture concept waits, judged from the dispatch clone",
          DS.pending_turn(d, disp, CT.owner_lines(disp)) is not None, "")
    # he answers; the answer is published from the bench clone
    owner_ev(os.path.join(bench, CT.OWNER_SHARD), ITEM, now - 60, text="Answer to Designer ask_match: toss a flame",
             ownerSaid="toss a flame")
    git("commit", "-q", "-am", "his answer", cwd=bench)
    git("push", "-q", "origin", "HEAD:main", cwd=bench)
    real_repo, env = DS.REPO, os.environ.get("RM_JUDGE_SYNC")
    DS.REPO = disp
    try:
        os.environ["RM_JUDGE_SYNC"] = "0"
        e = None
        try:
            RL.stage_open(d, "rm-role-designer-8", 50000)
        except DS.Refused as x:
            e = str(x)
        check("stale: without a fetch the behind clone refuses WAITING_OWNER (the trap as it happened)",
              e and "WAITING_OWNER" in e, e)
        os.environ.pop("RM_JUDGE_SYNC", None)
        notes = RL.judge_sync(d)
        check("stale: judge_sync fetches the dispatch clone without moving its working tree",
              notes == [] and ITEM not in open(os.path.join(disp, CT.OWNER_SHARD)).read().split("his root")[1], notes)
        check("stale: owner_lines reads origin/main's shard beside the working tree's",
              any("toss a flame" in ln for ln in CT.owner_lines(disp) or []), "")
        try:
            packet, budget = RL.stage_open(d, "rm-role-designer-8", 50000)
            e = None
        except DS.Refused as x:
            e = str(x)
        check("stale: after the sync the same judge opens the run (his published answer counts)",
              e is None and DS.load_state(d)["status"] == "waiting_owner", e)
        check("stale: and the surfaces read the answer from origin too: the turn is off his doorstep",
              DS.pending_turn(d, disp) is None, DS.pending_turn(d, disp))
        broken = os.path.join(tmp, "nofetch")
        os.makedirs(broken)
        git("init", "-q", broken)
        notes = RL.judge_sync(d, timeout=20, repos=[broken])
        check("stale: a fetch that fails is said, not swallowed", notes and "exited" in notes[0], notes)
    finally:
        DS.REPO = real_repo
        if env is None:
            os.environ.pop("RM_JUDGE_SYNC", None)
        else:
            os.environ["RM_JUDGE_SYNC"] = env
    sub = os.path.join(bench, "sub")
    os.makedirs(sub)
    check("origin_shard: a folder inside a clone is not that clone (no borrowed origin)", CT.origin_shard(sub) is None, "")


def main():
    tmp = tempfile.mkdtemp(prefix="designer_turns_")
    os.environ.setdefault("RM_DISPATCHER_STATE", os.path.join(tmp, "dstate"))
    try:
        _, d = doorstep(tmp)
        escalation(tmp, d)
        stale_clone(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
