#!/usr/bin/env python3
"""selftest_designer_repin.py - a locked version changed by his card re-pins instead of reopening stage 1
(RIMMANDRAKE_REPIN_LOCKED_CHANGE_STAGES_CARD_REOPENS_STAGE_ONE; refusal record
design/concepts/Pyrelands/version/evidence/exam_and_judge_refusal_2026-11-14.json, clause stale_root_reopens_stage_1).

The fixture is a scratch git repo (ext4, ~/rm/scratch, never /tmp) replaying the real Pyrelands history: the concept
files as stage 3 accepted them (a0d5452ac6), the six maturation test-text corrections (08d917c12a, under his card "All
four now, offline only" on the ADVANCE item) and his paving card "Drop the sentence" (f71693d77a), with the real
stage.json, OWNER lines and a ledger event tying each commit to its card. Checks:
1. before the verb, stale_stage is (1, ['root']), as on the real concept 2026-11-14;
2. `repin` citing each change by its OWNER event and commit (and his two process words on the item) leaves nothing
   stale, stage 4 the open stage, and a locked_change history row; the CLI does the same;
3. it refuses, stage.json byte-identical, a CONDUCTOR source, no source, an unlocked version, a card that is not the
   change's (the exam card for the paving commit), a change left uncited (the corrections), a commit paired with the
   wrong card, an uncommitted edit, and an OWNER event that is not his word (a --per-ruling close);
4. his word after the loop crossed its ceiling lifts the spend park even when no park was written yet (the park would
   have been written after his card and waited for another word); no word, no lift."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

REPO = DS.REPO
SRC = "design/concepts/Pyrelands"
STATE_AT = "249d86c35e"   # stage.json and VERSION.json as the 2026-11-14 refusal found them (the live ones move on)
FILES = ("record.json", "tree.json", "sheet.md", "scenes.json", "floor.json", "exam.json")
ITEM = "BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS"
ADVANCE = "RIMMANDRAKE_ADVANCE_PYRELANDS_OFFLINE_BESIDE_THE_PILOT"
PAVING = "1794695014598425560"        # his card "Drop the sentence", 2026-11-14 ~2:20 PM PST
PAVING_CLOSE = "1794696026595731326"  # the close that carries f71693d77a: --per-ruling, not his word
ADVANCE_CARD = "1794684238949922350"  # "All four now, offline only"
EXAM_CARD = "1794721014843506307"     # "They still owe it", on the ADVANCE item
HOLD_WORD = "1794611171307640419"     # "Yes, we're going to do what you recommend." on the item
EXAM_CARD_ITEM = "1794721773574845016"  # the exam card recorded on the item
FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def git(root, *a):
    r = subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout.strip()


def real(commit, path):
    return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (commit, path)], capture_output=True,
                          timeout=60, check=True).stdout


FROZEN_TSN = 1794748469904049550


def owner_lines():
    keep = {PAVING, PAVING_CLOSE, ADVANCE_CARD, EXAM_CARD}
    out = []
    with open(os.path.join(REPO, CT.OWNER_SHARD), encoding="utf-8") as f:
        for ln in f:
            try:
                ev = json.loads(ln)
            except ValueError:
                continue
            # the shard as it stood when the fixture was cut: a later owner event on ITEM (OWNER:1794748469904049550,
            # 2026-11-15) is not part of the replayed history and turned this selftest red on base
            if (ev.get("id") == ITEM and int(ev.get("tsn") or 0) < FROZEN_TSN) or str(ev.get("tsn")) in keep:
                out.append(ln if ln.endswith("\n") else ln + "\n")
    return out


def fixture():
    base = os.path.expanduser("~/rm/scratch")
    os.makedirs(base, exist_ok=True)
    root = tempfile.mkdtemp(prefix="selftest-repin-", dir=base)
    d = os.path.join(root, SRC)
    os.makedirs(os.path.join(d, "version"))
    ev = os.path.join(root, os.path.dirname(CT.OWNER_SHARD))
    os.makedirs(ev)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "selftest@example.invalid")
    git(root, "config", "user.name", "selftest")
    with open(os.path.join(d, "stage.json"), "wb") as f:
        f.write(real(STATE_AT, SRC + "/stage.json"))
    with open(os.path.join(d, "version", "VERSION.json"), "wb") as f:
        f.write(real(STATE_AT, SRC + "/version/VERSION.json"))
    with open(os.path.join(root, CT.OWNER_SHARD), "w", encoding="utf-8") as f:
        f.writelines(owner_lines())
    shas = {}
    for name, commit in (("accepted", "a0d5452ac6"), ("corrections", "08d917c12a"), ("paving", "f71693d77a")):
        for fn in FILES:
            with open(os.path.join(d, fn), "wb") as f:
                f.write(real(commit, "%s/%s" % (SRC, fn)))
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture: Pyrelands at %s (%s)" % (commit, name))
        shas[name] = git(root, "rev-parse", "HEAD")
    with open(os.path.join(root, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"), "w") as f:
        f.write(json.dumps({"seat": "CONDUCTOR", "event": "note", "id": ADVANCE, "tsn": 1,
                            "text": "Stage 1 table + 6 corrections %s" % shas["corrections"][:10]}) + "\n")
    with open(os.path.join(root, CT.OWNER_SHARD), "a", encoding="utf-8") as f:
        f.write(json.dumps({"seat": "OWNER", "event": "close", "id": "RIMMANDRAKE_ASK_PYRE_ROOT_STILL_PROMISES_PAVING_HOLDS",
                            "sha": shas["paving"], "perRuling": "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM",
                            "tsn": 2}) + "\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture: ledger")
    return root, d, shas


def good(shas):
    return ["OWNER:%s@%s" % (PAVING, shas["paving"]), "OWNER:%s@%s" % (ADVANCE_CARD, shas["corrections"]),
            "OWNER:" + HOLD_WORD, "OWNER:" + EXAM_CARD_ITEM]


def stage_bytes(d):
    with open(DS.state_path(d), "rb") as f:
        return f.read()


def refuses(name, d, root, sources, want):
    before = stage_bytes(d)
    try:
        DS.repin(d, sources, "selftest", repo=root)
        got = None
    except DS.Refused as e:
        got = str(e)
    check("refuses %s (%s)" % (name, want), got is not None and want in got, got)
    check("refused %s leaves stage.json byte-identical" % name, stage_bytes(d) == before)


def main():
    root, d, shas = fixture()
    try:
        st = DS.load_state(d)
        s = DS.stale_stage(d, st, root)
        check("1 before the verb: stale_stage is (1, ['root'])", s == (1, ["root"]), s)

        refuses("a CONDUCTOR source", d, root, ["CONDUCTOR:1794721030959200569@" + shas["paving"]] + good(shas)[1:],
                "OWNER")
        refuses("no source", d, root, [], "no source")
        refuses("the exam card for the paving commit", d, root,
                ["OWNER:%s@%s" % (EXAM_CARD, shas["paving"])] + good(shas)[1:], "not tied")
        refuses("the corrections left uncited", d, root, [good(shas)[0]] + good(shas)[2:], shas["corrections"][:10])
        refuses("commits paired with the wrong cards", d, root,
                ["OWNER:%s@%s" % (PAVING, shas["corrections"]), "OWNER:%s@%s" % (ADVANCE_CARD, shas["paving"])]
                + good(shas)[2:], "not tied")
        refuses("a --per-ruling close as the source", d, root,
                ["OWNER:%s@%s" % (PAVING_CLOSE, shas["paving"])] + good(shas)[1:], "his word")
        refuses("his process word left uncited", d, root, good(shas)[:3], EXAM_CARD_ITEM)
        sheet = os.path.join(d, "sheet.md")
        keep = open(sheet, "rb").read()
        with open(sheet, "ab") as f:
            f.write(b"\n- an uncommitted line\n")
        refuses("an uncommitted edit", d, root, good(shas), "uncommitted")
        with open(sheet, "wb") as f:
            f.write(keep)
        vp = os.path.join(d, "version", "VERSION.json")
        vkeep = open(vp, "rb").read()
        v = json.loads(vkeep)
        v["state"] = "draft"
        with open(vp, "w") as f:
            json.dump(v, f)
        refuses("an unlocked version", d, root, good(shas), "not locked")
        with open(vp, "wb") as f:
            f.write(vkeep)

        out = DS.repin(d, good(shas), "selftest: his paving card and the advance corrections", repo=root)
        st = DS.load_state(d)
        s = DS.stale_stage(d, st, root)
        check("2 after repin: nothing stale", s == (None, []), s)
        check("2 after repin: stage 4 is the open stage", st.get("stage") == 4, st.get("stage"))
        row = (st.get("history") or [{}])[-1]
        check("2 a locked_change history row cites every source", row.get("what") == "locked_change"
              and all(("OWNER:" + t) in row.get("why", "") for t in (PAVING, ADVANCE_CARD, HOLD_WORD)), row)
        check("2 repin reports the re-pinned stages", sorted(out) == [1, 2, 3], out)
        refuses("a second repin with nothing stale", d, root, good(shas), "nothing to re-pin")

        # the CLI, on a fresh fixture
        shutil.rmtree(root)
        root, d, shas = fixture()
        argv = ["repin", d, "--why", "selftest cli"]
        for sv in good(shas):
            argv += ["--source", sv]
        old = DS.REPO
        DS.REPO = root
        try:
            rc = DS.main(argv)
            rc_bad = DS.main(["repin", d, "--why", "selftest cli"])
        finally:
            DS.REPO = old
        st = DS.load_state(d)
        check("2 cli repin exits 0 and leaves nothing stale", rc == 0 and DS.stale_stage(d, st, root) == (None, []),
              (rc, DS.stale_stage(d, st, root)))
        check("3 cli repin with no source exits 1", rc_bad == 1, rc_bad)

        # 5: RIMMANDRAKE_REPIN_STAGE_FOUR_LEAVES_EXAM_VOID: an accepted exam over a changed tree is not re-pinned
        root5, d5, shas5 = fixture()
        try:
            st5 = DS.load_state(d5)
            res = {r["stage"]: r for r in st5.get("results") or [] if r.get("outcome") == "done"}
            with open(os.path.join(d5, "exam.json"), "w") as f:      # the exam, frozen against stage 3's tree and sheet
                json.dump({"inputs": {k: res[3]["inputs"].get(k) for k in ("tree", "sheet")}}, f)
            git(root5, "add", "-A")
            git(root5, "commit", "-q", "-m", "fixture: an exam taken before the change")
            cur5 = DS.inputs(d5, st5, root5)
            r4 = {"stage": 4, "outcome": "done", "inputs": dict(
                {k: res[3]["inputs"].get(k) for k in ("sheet", "tree", "scenes", "floor")},
                exam=cur5.get("exam"), owner=res[2]["inputs"].get("owner")),
                "owner_uncited": res[2].get("owner_uncited")}
            st5["results"].append(r4)
            st5["stage"] = 5
            DS.write_json(DS.state_path(d5), st5)
            changed4 = sorted(k for k in ("tree", "sheet") if r4["inputs"].get(k) != cur5.get(k))
            out5 = DS.repin(d5, good(shas5), "selftest: a tree change under an accepted exam", repo=root5)
            st5 = DS.load_state(d5)
            s5 = DS.stale_stage(d5, st5, root5)
            ee = DS.exam_errors(DS.read_json(os.path.join(d5, "exam.json")), d5, st5, root5)
            check("5 the fixture's change moves the exam's tree or sheet", bool(changed4), changed4)
            check("5 repin leaves stage 4 out when its exam's tree or sheet changed", 4 not in out5, out5)
            check("5 stale_stage reports stage 4, agreeing with exam_errors", s5[0] == 4
                  and any("another" in e for e in ee), (s5, ee[:2]))
            row5 = (st5.get("history") or [{}])[-1]
            check("5 the history says stage 4 was left stale", "stage 4 left stale" in row5.get("why", ""), row5)
        finally:
            shutil.rmtree(root5, ignore_errors=True)

        # 4: the spend ceiling and his word that predates the park
        st = DS.load_state(d)
        check("4 the replayed loop is past its ceiling", bool(DS.loop_ceiling(st)), DS.loop_ceiling(st))
        check("4 no park written yet", not isinstance(st.get("park"), dict), st.get("park"))
        lifted = DS.lift_park(st, d, root)
        check("4 his word after the crossing lifts the ceiling with no park written", lifted is True
              and DS.loop_ceiling(st) is None and (st.get("parks") or [{}])[-1].get("kind") == "ceiling",
              (lifted, DS.loop_ceiling(st), st.get("parks")))
        st = DS.load_state(d)
        st["item"] = "NO_SUCH_ITEM_HAS_HIS_WORD"
        check("4 no word on the item, no lift", DS.lift_park(st, d, root) is False and bool(DS.loop_ceiling(st)))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%d check(s) failed" % len(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
