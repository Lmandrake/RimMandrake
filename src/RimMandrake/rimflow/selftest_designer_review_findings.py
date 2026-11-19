#!/usr/bin/env python3
"""selftest_designer_review_findings.py - one case per confirmed finding of the Codex reviews of designer_stage.py
(parent RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS; reviews /mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_ds_*.txt
and r_ds_elsewhere2.txt), each named after the child ticket that fixes it. Every case failed on the base it was written
against. Runs in temp dirs; touches no real concept, ledger or state."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_JUDGE_SYNC", "0")
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402
from selftest_designer_stage import ITEM, Repo, put  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def crashes(fn, *a, **k):
    """-> (value, None) or (None, "ExcType: msg") for any exception but Refused (a refusal is an answer)."""
    try:
        return fn(*a, **k), None
    except DS.Refused as e:
        return ("REFUSED", str(e)), None
    except Exception as e:   # noqa: BLE001 - the case is "it crashed"
        return None, "%s: %s" % (type(e).__name__, e)


def concept(tmp, name, runner=None, stage=None, **st_kw):
    d = os.path.join(tmp, "design/concepts", name)
    DS.init(d, name, ITEM, cap=100000, reserve=10000, runner=runner)
    if stage is not None or st_kw:
        st = DS.load_state(d)
        if stage is not None:
            st["stage"] = stage
        st.update(st_kw)
        DS.write_json(DS.state_path(d), st)
    return d


def speaker_owner_needs_his_words():
    """RIMMANDRAKE_REQUIRE_HIS_WORDS_BEHIND_SPEAKER_OWNER_RULING_PASSED (finding 2, review-2 finding 8)."""
    ev = {"5": {"tsn": "5", "id": "X", "seat": "OWNER", "perRuling": "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM",
                "why": "Conductor's own words"},
          "6": {"tsn": "6", "id": "X", "seat": "OWNER", "ownerSaid": "keep the ladder"}}
    quote = {"id": "d1", "kind": "decision", "speaker": "owner", "quote": True, "source": "OWNER:5", "text": "x"}
    errs = DS.authority_errors(quote, "decisions[d1]", ev)
    check("speaker owner: a quotation citing a Conductor-only OWNER event is refused", errs, errs)
    waiver = {"id": "w1", "kind": "floor_disable", "speaker": "owner", "source": "OWNER:5", "text": "x"}
    errs = DS.authority_errors(waiver, "decisions[w1]", ev)
    check("speaker owner: an owner-only kind without words citing a Conductor-only event is refused", errs, errs)
    good = dict(quote, source="OWNER:6")
    check("speaker owner: his ownerSaid event still passes", DS.authority_errors(good, "decisions[d1]", ev) == [],
          DS.authority_errors(good, "decisions[d1]", ev))
    both = dict(quote, source=["OWNER:5", "OWNER:6"])
    check("speaker owner: a Conductor event beside one of his passes", DS.authority_errors(both, "d", ev) == [],
          DS.authority_errors(both, "d", ev))
    check("speaker owner: not judged when OWNER.jsonl was not asked (owner_ev None)",
          DS.authority_errors(quote, "d", None) == [], DS.authority_errors(quote, "d", None))
    conductor = dict(quote, speaker="conductor", quote=False)
    check("speaker conductor citing a Conductor event is fine", DS.authority_errors(conductor, "d", ev) == [],
          DS.authority_errors(conductor, "d", ev))


def examiner_is_author_by_id(tmp):
    """RIMMANDRAKE_MATCH_EXAMINER_TO_AUTHOR_BY_ID_NOT_LABEL (finding 4)."""
    d = concept(tmp, "Exam", stage=4)
    st = DS.load_state(d)
    aid = "a0123456789abcdef"
    ex = {"author": "agent:%s (designer)" % aid, "examiner": "agent:%s (examiner)" % aid}
    msg = "exam: the examiner is not the tree's author"
    check("examiner: the author's agent id under another label is refused", msg in DS.exam_errors(ex, d, st, tmp),
          [e for e in DS.exam_errors(ex, d, st, tmp) if "examiner" in e])
    ex2 = dict(ex, examiner="agent:a fedcba9876543210 (examiner)".replace("a fed", "afed"))
    check("examiner: a different agent id passes this line", msg not in DS.exam_errors(ex2, d, st, tmp))
    ex3 = dict(ex, examiner=ex["author"])
    check("examiner: the identical string is still refused", msg in DS.exam_errors(ex3, d, st, tmp))


def flawed_criterion_not_designers():
    """RIMMANDRAKE_ROUTE_FLAWED_CRITERION_GAPS_OFF_DESIGNER_REWORK (finding 7, lane B's probe of program_result)."""
    gap = {"gid": "g1", "what": "the soak scene", "return_to": 3}
    flawed = {"verdict": "not_covered", "gaps": [dict(gap, criterion_verdict="flawed")]}
    check("can_fix: a gap whose criterion the judge calls flawed is not the Designer's alone",
          DS.designer_can_fix(flawed) is False, DS.designer_can_fix(flawed))
    unatt = {"verdict": "not_covered", "gaps": [dict(gap, criterion_verdict="unattainable")]}
    check("can_fix: an unattainable criterion is not the Designer's alone", DS.designer_can_fix(unatt) is False)
    sound = {"verdict": "not_covered", "gaps": [dict(gap, criterion_verdict="sound")]}
    check("can_fix: a sound criterion returning to stage 3 is still the Designer's", DS.designer_can_fix(sound) is True)
    st = {"stage": 5, "status": "ready"}
    check("program: a flawed-criterion gap is not turned into a program return to stage 3",
          DS.program_result(st, flawed, "r1") is None, DS.program_result(st, flawed, "r1"))
    nested = {"verdict": "not_covered", "gaps": [gap], "contract": {"advisory": "brief uncalibrated"}}
    check("program: an advisory verdict (contract.advisory) is not turned into a program return",
          DS.program_result(st, nested, "r1") is None, DS.program_result(st, nested, "r1"))
    check("program: a plain not_covered verdict still returns to stage 3",
          (DS.program_result(st, {"verdict": "not_covered", "gaps": [gap]}, "r1") or {}).get("to") == 3)


def cli_repin_reads_concept_clone(tmp):
    """RIMMANDRAKE_RESOLVE_CONCEPT_CLONE_IN_CLI_REPIN_REPO_WON (finding 9)."""
    other = os.path.join(tmp, "otherclone")
    os.makedirs(os.path.join(other, os.path.dirname(CT.OWNER_SHARD)))
    d = os.path.join(other, "design/concepts/Rp")
    os.makedirs(d)
    seen = {}
    real = DS.repin

    def fake(dd, sources, why, repo=None, dry=False):
        seen["repo"] = repo or DS.clone_of(dd) or DS.REPO
        return [3]
    DS.repin = fake
    try:
        DS.main(["repin", d, "--source", "OWNER:1", "--why", "test"])
    except SystemExit:
        pass
    finally:
        DS.repin = real
    check("cli repin: a concept in another clone is re-pinned against that clone, not this one",
          seen.get("repo") == other, seen)


def malformed_results_reject(tmp):
    """RIMMANDRAKE_REJECT_MALFORMED_DESIGNER_RESULTS_NOT_CRASH (review-2 finding 9, lane B's probes)."""
    cases = [("record [1] at stage 1", 1, [1], None, "done"),
             ("record {asks: 3} at stage 2", 2, {"asks": 3}, None, "done"),
             ("record {asks: 3} waiting_owner at stage 1", 1, {"asks": 3}, None, "waiting_owner"),
             ("record [1] at stage 0", 0, [1], None, "done"),
             ("interaction scene with no id at stage 3", 3, {}, {"scenes": [{"kind": "interaction", "features": ["f1"]}]}, "done")]
    for i, (name, stage, rec, scenes, outcome) in enumerate(cases):
        d = concept(tmp, "Bad%d" % i, stage=stage)
        DS.open_run(d, "rm-role-designer-%d" % (10 + i), repo=tmp)
        put(d, "record.json", rec)      # the run writes them: the packet was built from a clean folder
        if scenes is not None:
            put(d, "scenes.json", scenes)
        put(d, "result.json", {"run": "rm-role-designer-%d" % (10 + i), "stage": stage, "outcome": outcome})
        got, err = crashes(DS.close_run, d, "rm-role-designer-%d" % (10 + i), 500, repo=tmp)
        st = DS.load_state(d) if os.path.exists(DS.state_path(d)) else {}
        check("malformed: %s is a rejected result, never a crash" % name,
              err is None and got and got[0] is False and st.get("running") is None
              and (st.get("results") or [{}])[-1].get("outcome") == "rejected", (got, err))
    d = concept(tmp, "BadJson")
    DS.open_run(d, "rm-role-designer-30", repo=tmp)
    put(d, "result.json", "{not json")
    got, err = crashes(DS.close_run, d, "rm-role-designer-30", 700, repo=tmp)
    st = DS.load_state(d)
    check("malformed: an unparseable result.json is rejected and its run charged, never left open",
          err is None and got and got[0] is False and st.get("running") is None and st["budget"]["spent"] == 700
          and os.path.exists(os.path.join(d, "result.rm-role-designer-30.rejected.json")), (got, err, st["budget"]))


def unreadable_owner_feed_is_not_an_answer(tmp):
    """RIMMANDRAKE_REFUSE_UNREADABLE_OWNER_FEED_BLIND_IS_NO_REPLY (review-2 finding 10, lane B's probe)."""
    d = concept(tmp, "Wait", stage=1, status="waiting_owner", waiting_owner_feed="feed-before")
    shard = os.path.join(tmp, CT.OWNER_SHARD)
    keep = shard + ".kept"
    os.replace(shard, keep)
    try:
        got, err = crashes(DS.open_run, d, "rm-role-designer-40", repo=tmp)
        check("waiting: an unreadable OWNER feed is refused as UNMEASURED, not opened as his answer",
              err is None and isinstance(got, tuple) and got[0] == "REFUSED" and "UNMEASURED" in got[1]
              and DS.load_state(d).get("status") == "waiting_owner", (got, err, DS.load_state(d).get("status")))
    finally:
        os.replace(keep, shard)
    got, err = crashes(DS.open_run, d, "rm-role-designer-41", repo=tmp)
    check("waiting: a readable feed that moved still opens the run",
          err is None and isinstance(got, tuple) and got[0] != "REFUSED", (got, err))


def packet_failure_leaves_no_run(tmp):
    """RIMMANDRAKE_BUILD_PACKET_BEFORE_SAVING_OPEN_RUN_PHANTOM_CHARGE (review-2 finding 11)."""
    d = concept(tmp, "Pkt")
    real = DS.packet

    def broken(*a, **k):
        raise DS.Refused("record.json does not parse: test")
    DS.packet = broken
    try:
        got, err = crashes(DS.open_run, d, "rm-role-designer-50", repo=tmp)
    finally:
        DS.packet = real
    st = DS.load_state(d)
    check("packet: a packet that cannot be built leaves no open run behind",
          st.get("running") is None, (got, err, st.get("running")))
    DS.open_run(d, "rm-role-designer-51", repo=tmp)
    check("packet: the next open charges nothing for the run that never launched",
          DS.load_state(d)["budget"]["spent"] == 0, DS.load_state(d)["budget"])


# each child's section joins once its fix lands (every one was watched failing on base 25d20f71e0 first)
SECTIONS = [
    lambda tmp: speaker_owner_needs_his_words(),
    examiner_is_author_by_id,
    lambda tmp: flawed_criterion_not_designers(),
    cli_repin_reads_concept_clone,
    malformed_results_reject,
]


def main():
    tmp = tempfile.mkdtemp(prefix="designer_review_findings_")
    try:
        Repo(tmp).said("first words")
        for run in SECTIONS:
            run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
