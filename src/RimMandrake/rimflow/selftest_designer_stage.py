#!/usr/bin/env python3
"""selftest_designer_stage.py - the Designer's stage machine against GPT's listed failure cases
(design/RimMandrake/designer_v4/gpt_review_2026-11-03.md, last section; item DESIGNER_STAGES_REBUILD_LAUNCHER_HOLDS_LEASH):
a built but unproven feature, a missing script, a hand-staged scene labelled as proof, no owner reply, a late owner
correction during examination, a resumed Stage 4 run, interrupted teardown, an exhausted budget, and a mod with no
applicable visual floor lines; plus the result protocol, provenance, and the launcher wiring (role_launch run-now,
decide preview, dispatcher commit, supervise close). Runs in a temp dir; touches no real concept, ledger or state."""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_JUDGE_SYNC", "0")    # role_launch.judge_sync: fixture concepts, no fetch of this clone
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

FAILS = []
ITEM = "CONCEPT_FOO_ITEM"
DONE = {"FOO_LADDER_BUILD_CLIMB": "Foo: ladder lets a pawn climb out", "BAR_UNRELATED_THING": "something else",
        "TOOLING_FOOBARBAZ_STYLES": "FooBarBaz styles"}


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
    except DS.Refused as e:
        return str(e)
    return None


class Repo:
    def __init__(self, tmp):
        self.root = tmp
        self.owner = os.path.join(tmp, CT.OWNER_SHARD)
        os.makedirs(os.path.dirname(self.owner))
        open(self.owner, "w").close()
        os.makedirs(os.path.join(tmp, "src/Foo"))
        with open(os.path.join(tmp, "src/Foo/validation.py"), "w") as f:
            f.write("def scene_ladder_climb(ctx):\n    pass\n")
        self.tsn = 1000

    def said(self, words, item=ITEM):
        self.tsn += 1
        with open(self.owner, "a") as f:
            f.write(json.dumps({"tsn": str(self.tsn), "id": item, "seat": "OWNER", "ownerSaid": words}) + "\n")
        return "OWNER:%d" % self.tsn


def put(d, name, obj):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f)


def result(d, outcome, **kw):
    st = DS.load_state(d)
    put(d, "result.json", dict({"run": (st.get("running") or {}).get("run"), "stage": st["stage"],
                                "outcome": outcome}, **kw))


def inv(**kw):
    e = {"id": "ladder", "what": "the ladder", "impl": "present", "impl_evidence": "src/Foo/validation.py",
         "proof": "missing", "scope": "approved", "source": "src/Foo/validation.py"}
    e.update(kw)
    return e


def ask(**kw):
    a = {"id": "a1", "text": "When the pit floods, should the ladder still be climbable?", "decision": "flooded ladder",
         "about": ["ladder"], "offers_removal": False, "author": "run1", "status": "sent",
         "review": {"by": "fresh-reviewer", "verdict": "pass"}, "source": "log.md#L3"}
    a.update(kw)
    return a


def run_cycle(d, repo, run, outcome="done", tokens=1000, **kw):
    DS.open_run(d, run, repo=repo.root)
    result(d, outcome, **kw)
    return DS.close_run(d, run, tokens, repo=repo.root)


def main():
    tmp = tempfile.mkdtemp(prefix="designer_stage_")
    real_lint, real_gate, real_done = CT.lint, CT.gate, DS.done_items
    # the test repo has no ledger to fold: the done items are this fixture (the real fold is probed at the end)
    DS.done_items = lambda repo: dict(DONE)
    try:
        repo = Repo(tmp)
        d = os.path.join(tmp, "design/concepts/Foo")
        DS.init(d, "Foo", ITEM, cap=200000, reserve=20000)
        root_src = repo.said("the ladder lets a pawn climb out of a deep pit")

        # ---- manifest and packets
        st = DS.load_state(d)
        text, budget = DS.open_run(d, "run0", repo=repo.root)
        st = DS.load_state(d)
        check("packet: stage 0 injects core, grounding and scene contract by manifest, hashed into stage.json",
              set(st["running"]["manifest"]) == {"designer.md", "designer_grounding.md", "designer_scene_contract.md"}
              and "=== designer_grounding.md" in text and "=== designer_dialogue.md" not in text, st["running"])
        check("packet: the run budget is the remaining task budget less the reserve", budget == 180000, budget)

        # ---- result protocol: a closing message is not a result
        ok, errs = DS.close_run(d, "run0", 5000, repo=repo.root)
        st = DS.load_state(d)
        check("no result.json: rejected, stage stays 0, the run is charged", not ok and st["stage"] == 0
              and st["budget"]["spent"] == 5000 and "no result.json" in errs[0], (ok, errs, st["stage"]))

        # ---- stage 0: inventory with built/proven/scope separate
        put(d, "record.json", {"inventory": [inv(impl="absent")], "failure_modes": ["a", "b"]})
        DS.open_run(d, "run1", repo=repo.root)
        result(d, "done")
        ok, errs = DS.close_run(d, "run1", 1000, repo=repo.root)
        check("stage 0: absent without search_scope and only two failure modes are refused",
              not ok and any("search_scope" in e for e in errs) and any("three ways" in e for e in errs), errs)
        # ---- stage 0 accounts for what is built: src tree, done items under the mod's prefix, their live proofs
        lp = os.path.join(tmp, DS.LIVE_PROOFS)
        os.makedirs(lp)
        for n in ("FOO_LADDER_BUILD_CLIMB.txt", "FOO_LADDER_BUILD_CLIMB.criteria", "BAR_UNRELATED_THING.txt"):
            open(os.path.join(lp, n), "w").close()
        refs, notes = DS.built_evidence(repo.root, "Foo")
        check("built evidence: the src tree, the done item under FOO_ and its live proof, nothing unrelated",
              refs == ["src/Foo", "ITEM:FOO_LADDER_BUILD_CLIMB",
                       "infrastructure/state/live_proofs/FOO_LADDER_BUILD_CLIMB.txt"] and notes == [], (refs, notes))
        check("built evidence: an alias adds its prefix (GSS for GimmeSomeSlack)",
              DS.mod_prefixes("RimMandrake/GimmeSomeSlack", ["GSS"]) == ["GIMMESOMESLACK_", "GSS_"],
              DS.mod_prefixes("RimMandrake/GimmeSomeSlack", ["GSS"]))
        rec = {"inventory": [inv()], "failure_modes": ["a", "b", "c"]}
        put(d, "record.json", rec)
        DS.open_run(d, "run2a", repo=repo.root)
        result(d, "done")
        ok, errs = DS.close_run(d, "run2a", 1000, repo=repo.root)
        check("stage 0: a done item and its live proof the inventory never mentions are refused (ask what we built)",
              not ok and any("not accounted for" in e and "ITEM:FOO_LADDER_BUILD_CLIMB" in e
                             and "live_proofs/FOO_LADDER_BUILD_CLIMB.txt" in e and "src/Foo," not in e for e in errs),
              errs)
        text, _ = DS.open_run(d, "run2b", repo=repo.root)
        check("packet: stage 0 lists what is built, and done items naming the mod only in their title",
              "## What is already built" in text and "- ITEM:FOO_LADDER_BUILD_CLIMB" in text
              and "TOOLING_FOOBARBAZ_STYLES" not in text.split("## What is already built")[1].split("Done items")[0],
              text[-600:])
        DS.done_items = lambda repo: None
        result(d, "done")
        ok, errs = DS.close_run(d, "run2b", 1000, repo=repo.root)
        check("stage 0: an unreadable ledger is UNMEASURED and refuses done, never 'nothing built'",
              not ok and any("UNMEASURED" in e for e in errs), errs)
        DS.done_items = lambda repo: dict(DONE)
        bad = dict(rec, built_reviewed=[{"ref": "ITEM:FOO_LADDER_BUILD_CLIMB", "covered_by": "no_such_entry"}])
        check("stage 0: built_reviewed covered_by an id not in the inventory accounts for nothing",
              DS.unaccounted(bad, refs) == refs[1:], DS.unaccounted(bad, refs))
        rec = dict(rec, inventory=[inv(impl_evidence=["src/Foo/validation.py", "ITEM:FOO_LADDER_BUILD_CLIMB"])],
                   built_reviewed=[{"ref": "infrastructure/state/live_proofs/FOO_LADDER_BUILD_CLIMB.txt",
                                    "covered_by": "ladder"}])
        put(d, "record.json", rec)
        ok, errs = run_cycle(d, repo, "run2")
        check("stage 0 done -> stage 1", ok and DS.load_state(d)["stage"] == 1, errs)

        # ---- built / proven / scope: each field refused on its own, never folded into one word
        def inv_errs(**kw):
            return [e for e in DS.record_errors({"inventory": [inv(**kw)]}, repo.root) if e.startswith("inventory[")]
        check("inventory: the baseline entry is clean (so each refusal below is its own field)", inv_errs() == [],
              inv_errs())
        for field, bad_v in (("impl", "built"), ("proof", "bogus"), ("scope", "?")):
            got = inv_errs(**{field: bad_v})
            check("inventory: %s %r is refused by name" % (field, bad_v),
                  any(("%s %r is not one of" % (field, bad_v)) in e for e in got), got)
        got = inv_errs(proof="current")
        check("inventory: proof current with no proof_evidence is refused",
              any("proof current needs proof_evidence" in e for e in got), got)
        check("inventory: proof current WITH proof_evidence passes", inv_errs(proof="current", proof_evidence="x") == [],
              inv_errs(proof="current", proof_evidence="x"))
        got = inv_errs(impl_evidence=None)
        check("inventory: present with no impl_evidence is refused",
              any("present needs impl_evidence" in e for e in got), got)

        # ---- the working record carries each entry's source ids and its impl/proof/scope
        wd = os.path.join(tmp, "wr")
        os.makedirs(wd)
        put(wd, "record.json", {"inventory": [inv(id="probe", impl="unknown", proof="stale", scope="later",
                                                  source=["src/Foo/validation.py", "OWNER:1001"])],
                                "decisions": [{"id": "d9", "text": "dec", "source": ["log.md#L7"]}]})
        wr = DS.working_record(wd)
        line = [l for l in wr.splitlines() if l.startswith("- probe:")]
        check("working record: the inventory line carries impl, proof and scope",
              len(line) == 1 and "impl=unknown proof=stale scope=later" in line[0], wr)
        check("working record: the inventory line carries its source ids",
              len(line) == 1 and line[0].endswith("[src/Foo/validation.py,OWNER:1001]"), wr)
        check("working record: a decision line carries its source id",
              any(l.startswith("- d9:") and l.endswith("[log.md#L7]") for l in wr.splitlines()), wr)

        # ---- authority and provenance
        bad = dict(rec, root={"text": "climb out", "source": "CONDUCTOR:55", "speaker": "conductor"})
        put(d, "record.json", bad)
        ok, errs = run_cycle(d, repo, "run3")
        check("stage 1: a root approved by Conductor text is refused (owner-only, his words)",
              not ok and any("owner-only" in e for e in errs), errs)
        bad = dict(rec, decisions=[{"id": "d1", "text": "x", "source": "CONDUCTOR:55", "speaker": "owner",
                                    "quote": True}])
        put(d, "record.json", bad)
        ok, errs = run_cycle(d, repo, "run3b")
        check("Conductor text stored as his quotation is refused", not ok and any("Conductor text" in e for e in errs),
              errs)
        bad = dict(rec, decisions=[{"id": "d1", "text": "x", "source": "OWNER:999999", "speaker": "owner"}])
        put(d, "record.json", bad)
        ok, errs = run_cycle(d, repo, "run3c")
        check("an OWNER source that is not in OWNER.jsonl is refused", not ok and any("finds no event" in e for e in errs),
              errs)
        check("a source path that does not exist is refused",
              any("does not exist" in e for e in DS.record_errors({"scope": [{"id": "s", "source": "no/such.md"}]},
                                                                   repo.root)), "")

        # ---- built but unproven: clarify, never offer removal
        rec["root"] = {"text": "the ladder lets a pawn climb out of a deep pit", "source": root_src, "speaker": "owner",
                       "words": "the ladder lets a pawn climb out"}
        put(d, "record.json", rec)
        check("built-but-unproven: an ask offering to remove a present capability is refused",
              any("offers to remove" in e for e in DS.ask_errors(ask(offers_removal=True), rec)),
              DS.ask_errors(ask(offers_removal=True), rec))
        for q in ("Do we still need the ladder?", "Should we keep the ladder or cut it?",
                  "Is removing the ladder fine?"):
            check("built: a keep/remove question about a built thing is refused without the flag: %r" % q,
                  any("offers to remove" in e for e in DS.ask_errors(ask(text=q, offers_removal=False), rec)),
                  DS.ask_errors(ask(text=q), rec))
        check("built: keep/remove wording naming no inventory entry is refused",
              any("without naming its inventory entry" in e for e in DS.ask_errors(
                  ask(text="Should we keep save removal?", about=[], owner_cites=[root_src]), rec)), "")
        check("built-but-unproven: an ask on its correct behaviour, reviewed by another agent, passes",
              DS.ask_errors(ask(), rec) == [], DS.ask_errors(ask(), rec))
        opened = copy.deepcopy(rec)
        opened["inventory"][0].update(scope="opened_by_owner", scope_source=[repo.said("we may not need the ladder")])
        check("built-but-unproven: removal may be asked once he opened that scope",
              DS.ask_errors(ask(offers_removal=True), opened) == [], DS.ask_errors(ask(offers_removal=True), opened))
        check("an ask reviewed by its own author, or with no review, is refused",
              DS.ask_errors(ask(review={"by": "run1", "verdict": "pass"}), rec) != []
              and DS.ask_errors(ask(review=None), rec) != [], "")
        check("an ask that names no decision is refused", DS.ask_errors(ask(decision=""), rec) != [], "")
        ok, errs = run_cycle(d, repo, "run4")
        check("stage 1 done with his root -> stage 2", ok and DS.load_state(d)["stage"] == 2, errs)

        # ---- no owner reply
        rec["asks"] = [ask()]
        put(d, "record.json", rec)
        ok, errs = run_cycle(d, repo, "run5", outcome="waiting_owner")
        check("stage 2 waiting_owner with a reviewed sent ask is accepted",
              ok and DS.load_state(d)["status"] == "waiting_owner", errs)
        r = refused(DS.open_run, d, "run6", repo=repo.root)
        check("no owner reply: the next run is refused, silence never advances", r and "WAITING_OWNER" in r, r)
        st = DS.load_state(d)
        st["status"] = "ready"            # simulate a run that tries to declare stage 2 done anyway
        DS.write_json(DS.state_path(d), st)
        ok, errs = run_cycle(d, repo, "run6b")
        check("no owner reply: stage 2 done with an ask still sent is refused",
              not ok and any("silence never advances" in e for e in errs), errs)
        st = DS.load_state(d)
        st["status"], st["waiting_owner_feed"] = "waiting_owner", DS.owner_feed(repo.root, ITEM, d)
        DS.write_json(DS.state_path(d), st)
        ans = repo.said("yes, a flooded ladder still works")
        text, _ = DS.open_run(d, "run7", repo=repo.root)
        check("his reply (an owner event naming the item) lets the next run open", "stage 2" in text, text[:120])
        more = repo.said("and make it climbable from both sides")     # the run records his follow-up itself
        rec["asks"] = [ask(status="answered", answer=[ans, more])]
        put(d, "record.json", rec)
        result(d, "done")
        ok, errs = DS.close_run(d, "run7", 1000, repo=repo.root)
        check("stage 2 done once answered, his follow-up recorded and cited inside the run -> stage 3", ok and DS.load_state(d)["stage"] == 3, errs)

        # ---- a later stage needing him returns to stage 2
        DS.open_run(d, "run8", repo=repo.root)
        result(d, "waiting_owner")
        ok, errs = DS.close_run(d, "run8", 1000, repo=repo.root)
        check("stage 3 may not wait on him itself", not ok and any("only stages 1-2" in e for e in errs), errs)
        DS.open_run(d, "run9", repo=repo.root)
        result(d, "return", to=2)
        ok, errs = DS.close_run(d, "run9", 1000, repo=repo.root)
        check("a return that names no missing decision is refused", not ok and "decision" in errs[0], errs)
        DS.open_run(d, "run10", repo=repo.root)
        result(d, "return", to=2, decision="ladder material", question="Wood or steel ladder?")
        ok, errs = DS.close_run(d, "run10", 1000, repo=repo.root)
        st = DS.load_state(d)
        check("stage 3 returns to stage 2 with the named decision", ok and st["stage"] == 2
              and st["pending_decision"] == "ladder material", errs)
        text, _ = DS.open_run(d, "run11", repo=repo.root)
        check("the returned stage's packet names the missing decision", "ladder material" in text, "")
        result(d, "done")
        ok, errs = DS.close_run(d, "run11", 1000, repo=repo.root)
        check("back to stage 3", ok and DS.load_state(d)["stage"] == 3, errs)

        # ---- stage 3: scenes and floor as checked data (lint stubbed: concept_tree has its own selftest)
        tree = {"subject": "Foo", "kind": "mod", "leaves": [
            {"id": "climb_out", "leaf_kind": "experience", "tier_proposed": "quicktest"},
            {"id": "flood_ok", "leaf_kind": "experience", "tier_proposed": "quicktest"}],
            "floor": {"off": []}}
        put(d, "tree.json", tree)
        put(d, "sheet.md", "# Foo\n")
        CT.lint = lambda dd, rr=None, ff=None: ([], [])
        good = {"id": "climb", "kind": "acceptance", "requirement": ["climb_out"], "staged_by": "script",
                "entry_point": "src/Foo/validation.py::scene_ladder_climb",
                "start": ["pit depth 3, walls unclimbable (asserted)"], "action": "order the pawn into the pit",
                "expect": "the path crosses the ladder cell",
                "control": {"case": "ladder removed", "expect": "no path", "rules_out": "climbing the wall"},
                "restore": "terrain from snapshot", "hold": "immediate"}
        flood = dict(good, id="flood", requirement=["flood_ok"], entry_point="src/Foo/validation.py::scene_flood",
                     entry_point_item="FOO_SCRIPT_FLOOD_SCENE_BUILD")
        # missing script
        miss = dict(good, entry_point="src/Foo/validation.py::scene_nowhere")
        e = DS.scene_errors({"scenes": [miss, flood]}, tree, repo.root)
        check("missing script: an acceptance scene whose entry point is not in the proof script is refused",
              any("not in the proof script" in x for x in e), e)
        check("missing script: with its implementation filed (entry_point_item) it is accepted",
              DS.scene_errors({"scenes": [good, flood]}, tree, repo.root) == [],
              DS.scene_errors({"scenes": [good, flood]}, tree, repo.root))
        # hand-staged as proof
        hand = dict(good, staged_by="hand", label="HAND-STAGED: pit dug by dev tools")
        e = DS.scene_errors({"scenes": [hand, flood]}, tree, repo.root)
        check("hand-staged labelled as proof: refused, however it is labelled",
              any("never accepts a leaf" in x for x in e), e)
        expl = {"id": "look", "kind": "exploration", "staged_by": "hand", "question": "does a rope ladder read?"}
        check("a hand-staged exploration scene is fine (it accepts nothing)",
              DS.scene_errors({"scenes": [good, flood, expl]}, tree, repo.root) == [], "")
        e = DS.scene_errors({"scenes": [dict(good, control={"case": "ladder removed", "expect": "no path"}), flood]},
                            tree, repo.root)
        check("a control with no rules_out (the alternative it excludes) is refused", any("rules_out" in x for x in e), e)
        inter = dict(good, id="both", kind="interaction", features=["climb_out", "flood_ok"])
        check("an interaction scene beside each feature's own scene is fine",
              DS.scene_errors({"scenes": [good, flood, inter]}, tree, repo.root) == [], "")
        e = DS.scene_errors({"scenes": [good, inter]}, tree, repo.root)
        check("an interaction scene never stands in for a feature's own acceptance scene",
              any("never stands in" in x for x in e), e)
        # floor applicability: a mod with no applicable visual lines
        floor = CT.load_floor()[0]
        visual = ("art", "reads_as", "clickable", "order_taken", "motion")
        lines = {ln["id"]: {"status": "applicable"} for ln in floor["lines"]}
        for v in visual:
            lines[v] = {"status": "not_applicable", "evidence": "the mod draws nothing: no ThingDef has graphicData"}
        check("no applicable visual floor lines: not_applicable with evidence passes, no owner words needed",
              DS.floor_errors({"lines": lines}, tree, floor) == [], DS.floor_errors({"lines": lines}, tree, floor))
        l2 = dict(lines, motion={"status": "not_applicable"})
        check("not_applicable with no evidence is refused",
              any("needs evidence" in x for x in DS.floor_errors({"lines": l2}, tree, floor)), "")
        l2 = dict(lines, mod_settings={"status": "not_applicable", "evidence": "small mod"})
        check("a line that applies to every mod (mod_settings) cannot be not_applicable",
              any("every mod" in x for x in DS.floor_errors({"lines": l2}, tree, floor)), "")
        l2 = dict(lines, worldgen={"status": "disabled"})
        check("a standing ruling cannot be disabled",
              any("standing ruling" in x for x in DS.floor_errors({"lines": l2}, tree, floor)), "")
        l2 = dict(lines, art={"status": "disabled"})
        check("disabled with no floor.off in his words is refused (applicability is not a waiver)",
              any("floor.off" in x for x in DS.floor_errors({"lines": l2}, tree, floor)), "")
        l2 = dict(lines, memory={"status": "applicable", "evidence_mode": "compressed"})
        check("a compressed soak must say what it establishes",
              any("establishes" in x for x in DS.floor_errors({"lines": l2}, tree, floor)), "")
        l2 = dict(lines)
        l2.pop("log")
        check("every floor line needs a status", any("floor[log]" in x for x in DS.floor_errors({"lines": l2}, tree, floor)),
              "")
        refusals_scene_floor(repo, tree, good, flood, inter, expl, lines, floor)
        refusals_record_result(tmp, repo, tree)
        refusals_showcases(repo, root_src, good, flood, tree)
        show = [{"id": "ladder_show", "scenes": ["climb"], "exercises": ["ladder"], "source": [root_src],
                 "decision": "d_flag"}]
        flag = {"id": "d_flag", "text": "judged first on the ladder climb", "source": [root_src], "speaker": "owner",
                "flagship": "ladder_show"}
        rec["decisions"] = [flag]
        put(d, "record.json", rec)
        put(d, "scenes.json", {"scenes": [good, flood]})
        put(d, "floor.json", {"lines": lines})
        ok, errs = run_cycle(d, repo, "run12a")
        check("stage 3: scenes.json with no showcase set is refused (the mod's face is a list, showcase 1 his pick)",
              not ok and any("names no showcases" in e for e in errs), errs)
        put(d, "scenes.json", {"scenes": [good, flood], "showcases": show})
        ok, errs = run_cycle(d, repo, "run12")
        check("stage 3 done with lint, scenes and floor valid -> stage 4", ok and DS.load_state(d)["stage"] == 4, errs)

        # ---- resumed stage 4
        put(d, "log.md", "# log\nLOG-SENTINEL-TEXT\n")
        text, _ = DS.open_run(d, "run13", repo=repo.root)
        check("resumed stage 4 (log.md present): the exam procedure is injected, the log is not",
              "=== designer_exam.md" in text and "Cold Reader" in text and "LOG-SENTINEL-TEXT" not in text
              and "=== designer_dialogue.md" not in text, "")
        cur = DS.inputs(d, DS.load_state(d), repo.root)
        scen = [{"id": "s%d" % i, "text": "t", "expect": "reject: wall", "expect_source": "climb_out"}
                for i in range(10)]
        exam = {"author": "designer", "examiner": "examiner-1", "inputs": {"tree": "0" * 64, "sheet": cur["sheet"]},
                "scenarios": scen, "scenarios_hash": CT.sha(scen), "readers": ["reader-a", "reader-b"],
                "score": {"right": 10, "total": 10},
                "accept_where_reject_core": 0, "challenger_misses": [],
                "control": {"broken_leaf": "climb_out", "missed": True}}
        put(d, "exam.json", exam)
        result(d, "done")
        ok, errs = DS.close_run(d, "run13", 1000, repo=repo.root)
        check("resumed stage 4: an exam run against another tree hash is refused",
              not ok and any("another tree" in e for e in errs), errs)
        exam["inputs"]["tree"] = cur["tree"]
        exam["score"] = {"right": 8, "total": 10}
        put(d, "exam.json", exam)
        ok, errs = run_cycle(d, repo, "run14")
        check("exam: 8/10 is refused", not ok and any("under" in e for e in errs), errs)
        exam["score"] = {"right": 10, "total": 10}
        exam["scenarios"] = scen[:1] + [dict(scen[1], expect="accept")] + scen[2:]
        put(d, "exam.json", exam)
        ok, errs = run_cycle(d, repo, "run15")
        check("exam: scenarios edited after the freeze are refused", not ok and any("scenarios_hash" in e for e in errs),
              errs)
        exam["scenarios"] = scen
        put(d, "exam.json", exam)
        refusals_exam(tmp, d, repo, exam)

        # ---- late owner correction during examination
        DS.open_run(d, "run16", repo=repo.root)
        steel = repo.said("actually the ladder must be steel only")
        result(d, "done")
        ok, errs = DS.close_run(d, "run16", 1000, repo=repo.root)
        check("late owner correction DURING the exam run: its done result is refused",
              not ok and any("owner event arrived" in e for e in errs), errs)
        text, _ = DS.open_run(d, "run17", repo=repo.root)
        st = DS.load_state(d)
        check("late owner correction: the next run is back at stage 2, the packet says why",
              st["stage"] == 2 and "REOPENED" in text and "owner" in text.split("REOPENED")[1][:200], st["stage"])
        result(d, "done")
        ok, errs = DS.close_run(d, "run17", 1000, repo=repo.root)
        check("late owner correction: stage 2 cannot finish until the record takes his correction in",
              not ok and any("not taken in" in e for e in errs), errs)
        rec["decisions"] = [flag, {"id": "d_steel", "text": "steel ladders only", "source": steel, "speaker": "owner"}]
        put(d, "record.json", rec)
        ok, errs = run_cycle(d, repo, "run17b")
        check("stage 2 done clears the must_cite list it was reopened with", ok and "must_cite" not in DS.load_state(d),
              DS.load_state(d).get("must_cite"))
        ok2, _ = run_cycle(d, repo, "run18")       # stage 3 again
        check("after the correction the stages rerun in order (2, 3)", ok and ok2 and DS.load_state(d)["stage"] == 4,
              errs)
        put(d, "exam.json", dict(exam, inputs=DS.inputs(d, DS.load_state(d), repo.root)))
        ok, errs = run_cycle(d, repo, "run19")
        check("stage 4 done with a fresh exam -> stage 5", ok and DS.load_state(d)["stage"] == 5, errs)
        # an artifact edit after the exam invalidates stage 3 onward
        put(d, "scenes.json", {"scenes": [good, flood, expl], "showcases": show})
        text, _ = DS.open_run(d, "run20", repo=repo.root)
        check("an edited scenes.json after the exam reopens stage 3", DS.load_state(d)["stage"] == 3 and
              "scenes" in text, DS.load_state(d)["stage"])
        ok, _ = DS.close_run(d, "run20", 100, repo=repo.root)     # no result: a retry
        ok, errs = run_cycle(d, repo, "run21")
        put(d, "exam.json", dict(exam, inputs=DS.inputs(d, DS.load_state(d), repo.root)))
        ok2, errs2 = run_cycle(d, repo, "run22")
        CT.gate = lambda dd, rr=None, ff=None: (["no coverage signature"], [])
        ok3, errs3 = run_cycle(d, repo, "run23")
        check("stage 5: done with a failing gate is refused", ok and ok2 and not ok3
              and any("gate:" in e for e in errs3), (errs, errs2, errs3))
        CT.gate = lambda dd, rr=None, ff=None: ([], [])
        put(d, "record.json", dict(rec, inventory=rec["inventory"] + [inv(id="rope", what="a rope")]))
        ok, errs = run_cycle(d, repo, "run23b")
        check("stage 5: the lock is refused while an inventory capability is exercised by no showcase and no scene",
              not ok and any("exercised by no showcase and no scene: rope" in e for e in errs), errs)
        sc_ok = DS.read_json(os.path.join(d, "scenes.json"))
        # GPT review: the edit lands DURING the stage-5 run (after open_run's staleness check), so only the lock's
        # own checks can catch it
        DS.open_run(d, "run23c", repo=repo.root)
        put(d, "scenes.json", dict(sc_ok, scenes=sc_ok["scenes"] + [{"id": "rope_check"}],
                                   coverage_rest=list(sc_ok.get("coverage_rest") or []) + [
                                       {"capability": "rope", "by": ["rope_check"], "why": "ordinary check"}]))
        result(d, "done")
        ok, errs = DS.close_run(d, "run23c", 1000, repo=repo.root)
        check("stage 5: a bare scene added mid-run to cover a capability is refused (scene contract rechecked)",
              not ok and any(e.startswith("scenes:") and "rope_check" in e for e in errs), errs)
        put(d, "scenes.json", sc_ok)
        put(d, "record.json", rec)
        # GPT review: a contract-valid edit to the showcase set during the lock run is still a change the exam never saw
        DS.open_run(d, "run23d", repo=repo.root)
        moved = copy.deepcopy(sc_ok)
        moved["showcases"][0]["scenes"] = list(moved["showcases"][0]["scenes"]) + ["flood"]
        put(d, "scenes.json", moved)
        result(d, "done")
        ok, errs = DS.close_run(d, "run23d", 1000, repo=repo.root)
        check("stage 5: a valid showcase edit made during the lock run is refused (accepted inputs moved)",
              not ok and any("changed during the lock run" in e for e in errs) and DS.load_state(d)["status"] != "locked",
              errs)
        put(d, "scenes.json", sc_ok)
        put(d, "record.json", rec)
        ok, errs = run_cycle(d, repo, "run24")
        st = DS.load_state(d)
        check("stage 5 done with the gate passing -> locked", ok and st["status"] == "locked", errs)
        r = refused(DS.open_run, d, "run25", repo=repo.root)
        check("a locked concept refuses further runs", r and "LOCKED" in r, r)
        put(d, "scenes.json", {"scenes": [good]})
        r = refused(DS.open_run, d, "run26", repo=repo.root)
        check("a locked concept edited underneath still refuses (his word only), status shows the drift",
              r and "LOCKED" in r and DS.load_state(d)["stage"] == 5 and DS.status(d, repo.root)["stale_from"] == 3, r)

        # ---- interrupted teardown
        d2 = os.path.join(tmp, "design/concepts/Bar")
        DS.init(d2, "Bar", "BAR_ITEM", cap=100000, reserve=20000)
        r = refused(DS.scene_begin, d2, "climb", "")
        check("scene-begin with no recovery information is refused", r and "restore" in r, r)
        DS.scene_begin(d2, "climb", "remove pit at 10,10; restore sand from snapshot S1")
        r = refused(DS.open_run, d2, "r1", repo=repo.root)
        check("interrupted teardown: the next run is refused until recovery", r and "RECOVERY_PENDING" in r, r)
        DS.scene_end(d2, "climb", held=True, until="his review today")
        text, _ = DS.open_run(d2, "r1", repo=repo.root)
        check("a scene held for his review lets work go on, and the packet says it is held",
              "Held for his review: climb" in text, "")
        DS.scene_end(d2, "climb")
        check("scene-end restores it", DS.status(d2, repo.root)["recovery_held"] == [], "")

        # ---- exhausted budget
        r = refused(DS.open_run, d2, "r2", repo=repo.root)
        st = DS.load_state(d2)
        check("an unclosed run is charged its whole reservation at the next open (a retry, conservative)",
              st["budget"]["spent"] == 80000 and st["running"]["run"] == "r2", st["budget"])
        check("exhausted budget is advisory: the run opens, stage unchanged, history says over_budget",
              r is None and st["stage"] == 0 and any(h["what"] == "over_budget" for h in st["history"]), r)
        dU = os.path.join(tmp, "design/concepts/Unm")
        DS.init(dU, "Unm", "UNM_ITEM", cap=100000, reserve=20000)
        DS.open_run(dU, "u1", run_cap=30000, repo=repo.root)
        DS.close_run(dU, "u1", None, repo=repo.root)
        check("an UNMEASURED run is charged its whole reservation", DS.load_state(dU)["budget"]["spent"] == 30000, "")
        d3 = os.path.join(tmp, "design/concepts/Baz")
        DS.init(d3, "Baz", "BAZ_ITEM", cap=100000, reserve=20000)
        DS.charge(d3, 30000, "helper", "exam reader")
        _, b = DS.open_run(d3, "z1", run_cap=60000, repo=repo.root)
        check("helpers are charged to the same task budget; a run gets min(role cap, remaining - reserve)", b == 50000, b)
        r = refused(DS.charge, d3, 10, "lunch", "x")
        check("an unknown charge kind is refused", r is not None, r)

        # ---- the default cap holds a measured stage-0 read (DESIGNER_CAP_REMEASURE_STAGE_ZERO_ATE_IT)
        dC = os.path.join(tmp, "design/concepts/Cap")
        DS.init(dC, "Cap", "CAP_ITEM")
        DS.charge(dC, 653533, "stage", "the largest measured stage-0 read (GimmeSomeSlack)")
        DS.charge(dC, 50157, "review", "the largest measured review")
        DS.open_run(dC, "c1", run_cap=450000, repo=repo.root)
        st = DS.load_state(dC)
        check("the default cap survives a measured stage-0 read and review: stage 1 opens without over_budget",
              not any(h["what"] == "over_budget" for h in st["history"]), st["budget"]["spent"])
        check("the default cap holds six median stages (529,000 measured) and the reserve the largest review",
              DS.DEFAULT_CAP >= 6 * 529000 and DS.DEFAULT_RESERVE >= 50157, (DS.DEFAULT_CAP, DS.DEFAULT_RESERVE))
        rows = DS.spend_by_stage(st)
        check("spend_by_stage splits a stage's runs from its reviews and helpers",
              rows == {0: {"total": 703690, "runs": 653533, "other": 50157}}, rows)
        dL = os.path.join(tmp, "design/concepts/Legacy")
        DS.init(dL, "Legacy", "LEG_ITEM", cap=500000, reserve=50000)
        DS.charge(dL, 495103, "stage", "PyrelandsMechanics stage 0")
        DS.open_run(dL, "l1", run_cap=450000, repo=repo.root)
        st = DS.load_state(dL)
        check("a state on the legacy 500,000 cap is upgraded at load, says so, and the next open is not over_budget",
              st["budget"]["cap"] == DS.DEFAULT_CAP and st["budget"]["reserve"] == DS.DEFAULT_RESERVE
              and any(h["what"] == "cap_reset" for h in st["history"])
              and not any(h["what"] == "over_budget" for h in st["history"]), st["budget"])
        check("a cap set by hand is never upgraded", DS.load_state(d3)["budget"]["cap"] == 100000, "")

        refusals_launcher(tmp, repo)
        # ---- the launcher wiring
        wiring(tmp, repo)
        # ---- the real instrument can see: the live ledger folds to thousands of done items, FlowWorks among them
        real = real_done(DS.REPO)
        check("sanity probe: the real ledger's done items are readable (not None, not a round zero)",
              real is not None and len(real) > 1000 and any(i.startswith("FLOWWORKS_") for i in real),
              None if real is None else len(real))
    finally:
        CT.lint, CT.gate, DS.done_items = real_lint, real_gate, real_done
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d: %s" % (len(FAILS), FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


# ---- one refusal per branch: each mutates ONE field of a clean baseline and names the refusal it must draw
def refusals_showcases(repo, root_src, good, flood, tree):
    """The showcase set (owner, 2026-11-05): orthogonal showcases until efficient coverage, numbers in
    showcase_rules.json."""
    rules = {"max_overlap": 0.25, "min_new_after_first": 3}
    owner_ev = CT.owner_events(repo.root)
    units = "abcdefghij"
    other = repo.said("the pit should be deep", item="SOME_OTHER_ITEM_ENTIRELY")
    rec = {"inventory": [inv(id=u, what=u) for u in units] + [
        inv(id="idea", impl="absent", search_scope="src", scope="not_opened")],
        "decisions": [{"id": "d_flag", "text": "judged first", "source": [root_src], "speaker": "owner", "flagship": "flag"},
                      {"id": "d_agent", "text": "judged first", "source": [root_src], "speaker": "agent",
                       "flagship": "flag"},
                      {"id": "d_root", "text": "the root is approved", "source": [root_src], "speaker": "owner"}]}
    scenes = [dict(good, id=s) for s in ("s1", "s2", "s3", "s4")] + [flood]
    s1 = {"id": "flag", "scenes": ["s1"], "exercises": ["a", "b", "c"], "source": [root_src], "decision": "d_flag"}
    s2 = {"id": "two", "scenes": ["s2"], "exercises": ["d", "e", "f"]}
    s3 = {"id": "three", "scenes": ["s3"], "exercises": ["g", "h", "i"]}
    rest = [{"capability": "j", "by": ["flood_ok"], "why": "one leaf check covers it"}]

    def st(shows, rest_=rest, rec_=rec, sc_=scenes):
        return DS.showcase_table({"scenes": sc_, "showcases": shows, "coverage_rest": rest_}, rec_, tree, owner_ev,
                                 repo.root, rules)
    rows, errs = st([s1, s2, s3])
    check("showcases: the baseline set is accepted, with new coverage 3/3/3 and overlap 0 reported",
          errs == [] and [r["new"] for r in rows] == [3, 3, 3] and [r["overlap"] for r in rows] == [0, 0, 0],
          (rows, errs))
    check("showcases: an unbuilt, unopened inventory line is not a unit", DS.coverage_units(rec) == list(units),
          DS.coverage_units(rec))
    gone = dict(rec, inventory=rec["inventory"] + [inv(id="gone", scope="out")])
    check("showcases: a BUILT capability scoped out is still a unit (it ships until removed)",
          "gone" in DS.coverage_units(gone), DS.coverage_units(gone))
    refuses("showcases: a built scoped-out capability with no cover is refused",
            st([s1, s2, s3], rec_=gone)[1], "exercised by no showcase and no scene: gone")
    refuses("showcases: a showcase exercising a scoped-out capability is refused (coverage_rest only)",
            st([s1, s2, dict(s3, exercises=["g", "h", "i", "gone"])], rec_=gone)[1], "scoped out")
    check("showcases: a built scoped-out capability in coverage_rest is accepted",
          st([s1, s2, s3], rec_=gone, rest_=rest + [{"capability": "gone", "by": ["s4"], "why": "removal check"}])[1]
          == [], "")
    # malformed input is a refusal, never a crash or a pass (GPT whole-file review)
    for label, shows, want in (
            ("a list as decision", [dict(s1, decision=[]), s2, s3], "names no record.json decision"),
            ("a dict among a later showcase's exercises", [s1, s2, dict(s3, exercises=["g", "h", "i", {}])],
             "not an inventory id"),
            ("a dict among a candidate's exercises during the greedy comparison",
             [s1, s2, dict(s3, exercises=[{}, "g", "h", "i"])], "not an inventory id")):
        try:
            got, crashed = st(shows)[1], None
        except Exception as e:  # noqa: BLE001 - the check is that nothing escapes
            got, crashed = [], repr(e)
        check("showcases: %s refuses without crashing" % label,
              crashed is None and any(want in e for e in got), crashed or got)
    for label, r in (("a string inventory", {"inventory": "invalid"}), ("no record.json", None),
                     ("an omitted inventory", {}), ("an inventory entry that is not an object", {"inventory": [None]}),
                     ("an inventory entry with no id", {"inventory": [{"impl": "present", "scope": "approved"}]}),
                     ("an inventory entry with no impl or scope", {"inventory": [{"id": "rope"}]}),
                     ("an inventory entry with a misspelt impl and scope",
                      {"inventory": [{"id": "rope", "impl": "presnt", "scope": "aproved"}]})):
        refuses("showcases: %s is refused, not read as zero capabilities to cover" % label,
                DS.showcase_table({"scenes": scenes, "showcases": [], "coverage_rest": []}, r, tree, owner_ev,
                                  repo.root, rules)[1], "coverage cannot be counted")
    check("showcases: an explicitly empty inventory with no showcases is accepted (nothing to cover)",
          DS.showcase_table({"scenes": scenes, "showcases": []}, {"inventory": []}, tree, owner_ev, repo.root,
                            rules)[1] == [], "")
    only_out = {"inventory": [inv(id="rope", scope="out")]}
    check("showcases: a set whose only units are built-but-scoped-out passes on coverage_rest alone (no showcase)",
          DS.showcase_table({"scenes": scenes, "showcases": [],
                             "coverage_rest": [{"capability": "rope", "by": ["s4"], "why": "removal check"}]},
                            only_out, tree, owner_ev, repo.root, rules)[1] == [], "")
    rows, errs = st([s1, dict(s2, exercises=["a", "d", "e", "f"]), s3])
    check("showcases: overlap at the limit (1 of 4 = 0.25) is accepted and reported with the shared capability",
          errs == [] and rows[1]["overlap"] == 0.25 and rows[1]["overlapped"] == ["a"], (rows, errs))
    over = dict(s2, exercises=["a", "b", "d", "e", "f"])
    rows, errs = st([s1, over, s3])
    refuses("showcases: overlap 0.40 over the limit with no staging reason is refused", errs, "no staging reason")
    check("showcases: the refusal names the overlap and the bare capabilities", rows[1]["overlap"] == 0.4 and
          any("a, b have no staging reason" in e for e in errs), errs)
    rows, errs = st([s1, dict(over, overlap_why={"a": "the raid needs the moat to reach the pit", "b": "x"}), s3])
    check("showcases: over the limit with a staging reason for every shared capability is accepted", errs == [], errs)
    refuses("showcases: a reason for only some shared capabilities is refused",
            st([s1, dict(over, overlap_why={"a": "staging"}), s3])[1], "b has no staging reason")
    refuses("showcases: a later showcase with fewer than min_new_after_first new capabilities is refused",
            st([s1, dict(s2, exercises=["d", "e"]), s3], rest_=rest + [
                {"capability": "f", "by": ["s4"], "why": "cheap"}])[1], "under min_new_after_first 3")
    big = dict(s3, exercises=["g", "h", "i", "j"])
    refuses("showcases: a later showcase newly exercising more than the one before it is refused (not greedy)",
            st([s1, s2, big], rest_=[])[1], "the order is not greedy")
    # GPT review counterexample: counts 1,3,3 look non-increasing, but showcase 3 offered 4 new when 2 was picked
    zrec = dict(rec, inventory=rec["inventory"] + [inv(id="z", what="z")])
    refuses("showcases: greedy is checked against every later chosen showcase, not only the next count",
            st([dict(s1, exercises=["z"]), dict(s2, exercises=["a", "b", "c"]),
                dict(s3, exercises=["a", "d", "e", "f"])], rec_=zrec,
               rest_=[{"capability": u, "by": ["s4"], "why": "cheap"} for u in "ghij"])[1],
            "showcase 3 (three) would have added 4 here")
    check("showcases: showcase 1 is exempt from min_new and the greedy order (his pick)",
          st([dict(s1, exercises=["a"]), dict(s2, exercises=["b", "c", "d", "e", "f"]),
              dict(s3, exercises=["g", "h", "i"])])[1] == [], "")
    refuses("showcases: showcase 1 without his OWNER source is refused",
            st([dict(s1, source=["log.md#L3"]), s2, s3])[1], "flagship he picked")
    refuses("showcases: showcase 1 citing a real but unrelated OWNER event is refused (not bound to his pick)",
            st([dict(s1, source=[other]), s2, s3])[1], "names no record.json decision")
    refuses("showcases: showcase 1 bound to his root approval (same OWNER event, no flagship pick) is refused",
            st([dict(s1, decision="d_root"), s2, s3])[1], "names no record.json decision")
    refuses("showcases: showcase 1 bound to his pick of ANOTHER showcase id is refused",
            st([dict(s1, id="other_face"), s2, s3])[1], "names no record.json decision")
    refuses("showcases: showcase 1 bound to an agent's decision is refused",
            st([dict(s1, decision="d_agent"), s2, s3])[1], "names no record.json decision")
    refuses("showcases: showcase 1 citing an OWNER event that does not exist is refused",
            st([dict(s1, source=["OWNER:99999999"]), s2, s3])[1], "finds no event")
    refuses("showcases: exercising an unbuilt, unopened capability is refused",
            st([s1, dict(s2, exercises=["d", "e", "f", "idea"]), s3])[1], "not a built or in-scope")
    refuses("showcases: a showcase naming a scene that is not in scenes.json is refused",
            st([s1, dict(s2, scenes=["nowhere"]), s3])[1], "scene nowhere is not in scenes.json")
    refuses("showcases: a capability covered by no showcase and no coverage_rest is refused (stop criterion)",
            st([s1, s2, s3], rest_=[])[1], "exercised by no showcase and no scene: j")
    refuses("showcases: coverage_rest naming no real scene or leaf is refused",
            st([s1, s2, s3], rest_=[dict(rest[0], by=["ghost"])])[1], "neither a scenes.json scene nor a tree leaf")
    refuses("showcases: coverage_rest without a why is refused",
            st([s1, s2, s3], rest_=[dict(rest[0], why="")])[1], "no why")
    refuses("showcases: coverage_rest listing a capability a showcase exercises is refused",
            st([s1, s2, s3], rest_=rest + [{"capability": "a", "by": ["s1"], "why": "x"}])[1], "lists only the rest")
    refuses("showcases: no showcases at all while capabilities exist is refused", st([])[1], "names no showcases")
    check("showcases: a mod with no unit needs no showcase", st([], rest_=[], rec_={"inventory": []})[1] == [], "")
    tmp_rules = os.path.join(repo.root, "bad_rules.json")
    with open(tmp_rules, "w") as f:
        json.dump({"max_overlap": 1.5, "min_new_after_first": 3}, f)
    real_path = DS.SHOWCASE_RULES
    DS.SHOWCASE_RULES = tmp_rules
    try:
        bad = DS.showcase_check({"scenes": scenes, "showcases": [s1]}, rec, tree, owner_ev, repo.root)
        DS.SHOWCASE_RULES = os.path.join(repo.root, "no_such_rules.json")
        missing = DS.showcase_check({"scenes": scenes, "showcases": [s1]}, rec, tree, owner_ev, repo.root)
    finally:
        DS.SHOWCASE_RULES = real_path
    check("showcases: a missing rules file is a refusal reason, never a pass",
          any("missing" in e for e in missing), missing)
    check("showcases: a rules file with an impossible limit is refused, never a silent pass",
          any("max_overlap in [0, 1)" in e for e in bad), bad)
    real = DS.load_showcase_rules()
    check("showcases: the real rules file reads, and labels its numbers UNMEASURED",
          real["max_overlap"] == 0.25 and real["min_new_after_first"] == 3 and "UNMEASURED" in real["status"], real)
    # interactions stay: the showcase set never replaces a leaf's acceptance scene or an interaction check
    walk_tree = dict(tree, leaves=tree["leaves"] + [{"id": "walk_main", "leaf_kind": "walk",
                                                       "tier_proposed": "quicktest"}])
    refuses("showcases: full showcase coverage does not excuse a walk leaf from its own acceptance scene",
            DS.scene_errors({"scenes": scenes, "showcases": [s1, s2, s3], "coverage_rest": rest}, walk_tree,
                            repo.root), "leaf walk_main")


def refuses(name, errs, needle):
    check(name, any(needle in e for e in errs), errs)


def refusals_scene_floor(repo, tree, good, flood, inter, expl, lines, floor):
    base = [good, flood]
    check("refusal table: the scene baseline is clean", DS.scene_errors({"scenes": base}, tree, repo.root) == [],
          DS.scene_errors({"scenes": base}, tree, repo.root))

    def sc(*scenes):
        return DS.scene_errors({"scenes": list(scenes)}, tree, repo.root)
    refuses("scenes: no scenes list is refused", DS.scene_errors(None, tree, repo.root), "no scenes list")
    refuses("scenes: a scene with no id is refused", sc(dict(good, id=""), flood), "not an object with an id")
    refuses("scenes: an unknown kind is refused", sc(dict(good, kind="demo"), flood), "kind 'demo' is not one of")
    refuses("scenes: an unknown staged_by is refused", sc(dict(good, staged_by="robot"), flood),
            "staged_by 'robot' is not one of")
    refuses("scenes: an exploration scene with no question is refused",
            sc(good, flood, dict(expl, question="")), "names the question it explores")
    for k in ("action", "expect", "restore"):
        refuses("scenes: an acceptance scene with no %s is refused" % k, sc(dict(good, **{k: ""}), flood), "no %s" % k)
    refuses("scenes: no asserted starting conditions is refused", sc(dict(good, start=[]), flood),
            "no asserted starting conditions")
    refuses("scenes: an unknown hold is refused", sc(dict(good, hold="later"), flood), "hold 'later' is not one of")
    refuses("scenes: an acceptance scene with no requirement is refused", sc(dict(good, requirement=[]), flood),
            "no requirement")
    refuses("scenes: an interaction scene joining one feature is refused",
            sc(good, flood, dict(inter, features=["climb_out"])), "joins two or more")
    refuses("scenes: a requirement that is not a tree leaf is refused",
            sc(good, flood, dict(good, id="ghost", requirement=["no_such_leaf"])), "no_such_leaf is not a leaf")
    for ep in ("src/Foo/validation.py", None, "src/Foo/validation.py::"):
        refuses("scenes: an entry point %r that names no function is refused" % (ep,),
                sc(dict(good, entry_point=ep), flood), "not in the proof script")
    refuses("scenes: an off-offline experience leaf with no acceptance scene is refused", sc(good),
            "leaf flood_ok")

    check("refusal table: the floor baseline is clean", DS.floor_errors({"lines": lines}, tree, floor) == [],
          DS.floor_errors({"lines": lines}, tree, floor))

    def fl(lines_, tree_=tree, owner_ev=None):
        return DS.floor_errors({"lines": lines_}, tree_, floor, owner_ev=owner_ev)
    refuses("floor: no lines object is refused", DS.floor_errors(None, tree, floor), "no lines object")
    refuses("floor: a key that is not a floor line is refused", fl(dict(lines, bogus_line={"status": "applicable"})),
            "bogus_line is not a floor line")
    refuses("floor: an unknown status is refused", fl(dict(lines, art={"status": "maybe"})), "status 'maybe' is not one of")
    refuses("floor: an unknown evidence_mode on a numeric line is refused",
            fl(dict(lines, memory={"status": "applicable", "evidence_mode": "guessed"})), "evidence_mode 'guessed'")
    said = repo.said("the art line is off for this mod", item="TABLE_ITEM")
    t_off = dict(tree, floor={"off": [{"line": "art", "ref": said, "words": "the art line is off"}]})
    refuses("floor: a floor.off line the floor still calls applicable is refused", fl(dict(lines, art={"status": "applicable"}), t_off),
            "floor.off names it but floor.json says applicable")
    ev = CT.owner_events(repo.root)
    dis = dict(lines, art={"status": "disabled"})
    check("floor: disabled with floor.off carrying his words on that event passes", fl(dis, t_off, ev) == [],
          fl(dis, t_off, ev))
    t_bad = dict(tree, floor={"off": [{"line": "art", "ref": said, "words": "skip the art entirely"}]})
    refuses("floor: disabled with floor.off words he never said is refused", fl(dis, t_bad, ev),
            "not his words on that event")


def refusals_exam(tmp, d, repo, exam):
    st = DS.load_state(d)

    def ex(**kw):
        e = copy.deepcopy(exam)
        e.update(kw)
        return DS.exam_errors(e, d, st, repo.root)
    check("refusal table: the exam baseline is clean", ex() == [], ex())
    refuses("exam: no exam.json and no waiver is refused", DS.exam_errors(None, d, st, repo.root), "no exam.json")
    s9 = exam["scenarios"][:9]
    refuses("exam: fewer than ten scenarios is refused", ex(scenarios=s9, scenarios_hash=CT.sha(s9)), "fewer than 10")
    s_bad = [dict(exam["scenarios"][0], expect_source="")] + exam["scenarios"][1:]
    refuses("exam: a scenario with no expect_source is refused", ex(scenarios=s_bad, scenarios_hash=CT.sha(s_bad)),
            "needs expect and expect_source")
    refuses("exam: a total that is not the scenario count is refused", ex(score={"right": 11, "total": 11}),
            "score needs right and total")
    # EXAM_SCORE_ENFORCE_RIGHT_OVER_TOTAL_PASSES: 999/10 passed the bar, and bool is an int in Python
    refuses("exam: right above total is refused", ex(score={"right": 999, "total": 10}), "right above total")
    refuses("exam: right one above total is refused", ex(score={"right": 11, "total": 10}), "right above total")
    refuses("exam: a negative right is refused", ex(score={"right": -1, "total": 10}), "score needs right and total")
    refuses("exam: a boolean right is refused", ex(score={"right": True, "total": 10}), "score needs right and total")
    refuses("exam: a boolean total is refused", ex(score={"right": 10, "total": True}), "score needs right and total")
    refuses("exam: a float right is refused", ex(score={"right": 10.0, "total": 10}), "score needs right and total")
    check("exam: right exactly at the 9/10 bar still passes", ex(score={"right": 9, "total": 10}) == [],
          ex(score={"right": 9, "total": 10}))
    refuses("exam: right one under the bar is refused", ex(score={"right": 8, "total": 10}), "is under 90%")
    refuses("exam: an accept where the core rejects is refused", ex(accept_where_reject_core=1), "must be 0")
    refuses("exam: a boolean accept_where_reject_core is refused", ex(accept_where_reject_core=False), "must be 0")
    refuses("exam: an examiner who is the author is refused", ex(examiner="designer"), "examiner is not the tree's author")
    # EXAM_READERS_ENFORCE_TWO_NEVER_COUNTED: a one-Reader or self-read exam passed; designer_exam.md step 4 wants two
    refuses("exam: no readers field is refused", DS.exam_errors({k: v for k, v in exam.items() if k != "readers"}, d, st,
                                                                repo.root), "readers needs two")
    refuses("exam: a one-reader exam is refused", ex(readers=["reader-a"]), "readers needs two")
    refuses("exam: a readers field that is not a list is refused", ex(readers="reader-a, reader-b"), "readers needs two")
    refuses("exam: a blank reader does not count as the second reader", ex(readers=["reader-a", " "]), "readers needs two")
    refuses("exam: a non-text reader does not count as the second reader", ex(readers=["reader-a", 7]), "readers needs two")
    refuses("exam: the same reader twice is refused", ex(readers=["reader-a", "reader-a"]), "same agent")
    a1, a2, a3 = "a973694af5dc4757a", "acddc523961c33401", "ade4a89b3cdad9f61"
    refuses("exam: one reader twice under different annotations is refused",
            ex(readers=["rm-judge %s (sonnet)" % a1, "agent:%s" % a1]), "same agent")
    refuses("exam: the author as a reader is a self-read and is refused", ex(readers=["designer", "reader-b"]),
            "reader 'designer' is the author")
    refuses("exam: an annotated author as a reader is refused",
            ex(author="stage-3 run rm-role-designer-1793982561", readers=["rm-role-designer-1793982561 (again)", "reader-b"]),
            "is the author")
    refuses("exam: the examiner as a reader is refused, it wrote expect", ex(readers=["examiner-1", "reader-b"]),
            "is the examiner")
    refuses("exam: the challenger as a reader is refused", ex(challenger="rm-judge %s (fresh)" % a3,
                                                               readers=["agent:%s" % a3, "agent:%s" % a1]), "is the challenger")
    refuses("exam: a reader named inside the examiner field is refused",
            ex(examiner="rm-judge %s (fresh), challenger rm-judge %s" % (a2, a3), readers=["agent:%s" % a3, "agent:%s" % a1]),
            "is the examiner")
    refuses("exam: the open Designer run as a reader is refused",
            DS.exam_errors(dict(copy.deepcopy(exam), readers=["rm-role-designer-55", "reader-b"]), d,
                           dict(st, running={"run": "rm-role-designer-55"}), repo.root), "is the open run")
    refuses("exam: with no author a self-read cannot be ruled out, so it is refused", ex(author=""), "author is needed")
    # the four real exams' own spelling must still pass; a helper launched by the author's run is not the author
    for label, reader_pair, author, examiner in [
            ("FlowWorks", ["agent:%s" % a1, "agent:%s" % a2], "rm-role-designer-1793863469", "agent:%s (rm-judge, fresh)" % a3),
            ("GimmeSomeSlack", ["rm-judge a9c647383a06be32f (sonnet)", "rm-judge a73f8e4814d6eb407 (sonnet)"],
             "the Designer (tree last written by stage-3 run rm-role-designer-1793955500)",
             "rm-judge helper a458cbef6aa7a4875 (sonnet, fresh context), run rm-role-designer-1793955657"),
            ("Pyrelands", ["rm-judge Reader A a4776bd56de1d8d4c (fresh Opus; sheet, tree, scenario text only)",
                           "rm-judge Reader B a5794ebcb078bebf2 (fresh Opus; sheet, tree, scenario text only)"],
             "concept (tree authored_by; stage-3 Designer run rm-role-designer-1793982561)",
             "rm-judge Examiner a11d3c9660858e7ed (fresh Opus, not the author; run rm-role-designer-1793982967)"),
            ("PyrelandsMechanics", ["rm-judge af588634fcd2ca859", "rm-judge aeb28f8ab3c9a6f8c"],
             "concept (tree authored_by; stage-3 runs rm-role-designer-1793900422, rm-role-designer-1793914531)",
             "rm-judge a341313ab1c410415 (fresh, not the author), challenger rm-judge af27af147d3853d74")]:
        got = ex(readers=reader_pair, author=author, examiner=examiner)
        check("exam: the real %s reader strings still pass" % label, got == [], got)
    got = ex(readers=["rm-judge %s, run rm-role-designer-9" % a1, "rm-judge %s, run rm-role-designer-9" % a2],
             author="stage-3 run rm-role-designer-9")
    check("exam: two helpers launched by the author's run are neither the author nor each other", got == [], got)
    refuses("exam: an unaccounted challenger miss is refused", ex(challenger_misses=[{"id": "m1"}]), "accounted for")
    refuses("exam: an exam with no control is refused", ex(control=None), "control needs broken_leaf")
    refuses("exam: a control naming no broken leaf is refused", ex(control={"missed": True}), "control needs broken_leaf")
    refuses("exam: a control that did not miss is refused", ex(control={"broken_leaf": "climb_out", "missed": False}),
            "did not miss")
    refuses("exam: a control with no missed field is refused", ex(control={"broken_leaf": "climb_out"}), "did not miss")
    refuses("exam: a control breaking a leaf the tree lacks is refused",
            ex(control={"broken_leaf": "no_such_leaf", "missed": True}), "not a leaf of the tree")
    dn = os.path.join(tmp, "notree")
    os.makedirs(dn)
    refuses("exam: a control cannot be checked against a missing tree.json, so it is refused",
            DS.exam_errors(copy.deepcopy(exam), dn, st, repo.root), "not a leaf of the tree")
    put(dn, "tree.json", {"subject": "N", "leaves": [{"id": ["climb_out"]}, {"id": "x"}]})
    refuses("exam: a leaf whose id is not a string neither crashes nor counts",
            DS.exam_errors(copy.deepcopy(exam), dn, st, repo.root), "not a leaf of the tree")
    with open(os.path.join(dn, "tree.json"), "w") as f:
        f.write("{not json")
    refuses("exam: a tree.json that does not parse is refused, not a crash",
            DS.exam_errors(copy.deepcopy(exam), dn, st, repo.root), "not a leaf of the tree")
    dw = os.path.join(tmp, "waived")
    os.makedirs(dw)
    put(dw, "tree.json", {"subject": "W", "exam_waived": {"ref": "OWNER:1", "words": "skip the exam"}})
    check("exam: a tree with exam_waived needs no exam.json (the gate checks his words)",
          DS.exam_errors(None, dw, st, repo.root) == [], DS.exam_errors(None, dw, st, repo.root))


def refusals_record_result(tmp, repo, tree):
    src = repo.said("the rope ladder lets a pawn climb out", item="TABLE_ITEM")
    ev = CT.owner_events(repo.root)
    root = {"text": "climb out", "source": src, "speaker": "owner", "words": "the rope ladder lets a pawn climb out"}
    base = {"root": root, "inventory": [inv()], "decisions": [{"id": "d1", "text": "x", "source": "log.md#L1"}]}
    check("refusal table: the record baseline is clean", DS.record_errors(base, repo.root, ev) == [],
          DS.record_errors(base, repo.root, ev))

    def rc(**kw):
        r = copy.deepcopy(base)
        r.update(kw)
        return DS.record_errors(r, repo.root, ev)
    refuses("record: no record is refused", DS.record_errors(None, repo.root), "record.json is missing")
    check("record: a section that is not a list is refused, and nothing inside it is read",
          rc(decisions={"d1": "x"}) == ["record.decisions is not a list"], rc(decisions={"d1": "x"}))
    refuses("record: an entry with no id is refused", rc(decisions=[{"text": "x", "source": "log.md#L1"}]),
            "not an object with an id")
    refuses("record: a duplicate id is refused",
            rc(decisions=[{"id": "d1", "source": "log.md#L1"}, {"id": "d1", "source": "log.md#L2"}]), "duplicate id")
    refuses("record: an entry with no source is refused", rc(decisions=[{"id": "d1", "text": "x"}]), "no source")
    refuses("record: a source of no known shape is refused", rc(decisions=[{"id": "d1", "source": "said so!"}]),
            "is not OWNER:<tsn>")
    refuses("record: an unknown speaker is refused",
            rc(decisions=[{"id": "d1", "source": "log.md#L1", "speaker": "robot"}]), "speaker 'robot' is not one of")
    refuses("record: an agent's text stored as a quotation is refused",
            rc(decisions=[{"id": "d1", "source": "log.md#L1", "speaker": "agent", "quote": True}]),
            "a quotation is his words only")
    refuses("record: a root with no text is refused", rc(root={"text": "", "source": src, "speaker": "owner"}),
            "root: needs text")
    refuses("record: a root whose words are not on its owner event is refused",
            rc(root=dict(root, words="the steel ladder is optional")), "not his words on that event")
    refuses("record: scope opened_by_owner with no OWNER scope_source is refused",
            rc(inventory=[inv(scope="opened_by_owner")]), "opened_by_owner needs scope_source")

    def ak(**kw):
        return DS.ask_errors(ask(**kw), base)
    check("refusal table: the ask baseline is clean", ak() == [], ak())
    refuses("ask: no text is refused", ak(text=""), "no text")
    refuses("ask: no decision is refused by name", ak(decision=""), "names no unresolved decision")
    refuses("ask: citing neither inventory nor his words is refused", ak(about=[]), "cites neither")
    refuses("ask: about an entry not in the inventory is refused", ak(about=["ghost"]), "ghost is not in the inventory")
    refuses("ask: a struck review does not go to him", ak(review={"by": "fresh-reviewer", "verdict": "struck"}),
            "struck by review")

    # result validation, one outcome rule at a time, against a held-open run
    dr = os.path.join(tmp, "design/concepts/Res")
    os.makedirs(dr)

    put(dr, "tree.json", tree)

    def rs(at, outcome, rec=base, **kw):
        put(dr, "record.json", rec)
        st = {"stage": at, "running": {"run": "r1"}, "item": "RES_ITEM", "must_cite": []}
        return DS.result_errors(dict({"run": "r1", "stage": at, "outcome": outcome}, **kw), dr, st, repo.root)
    refuses("result: a result for another stage is refused", rs(2, "done", stage=1),
            "result is for stage 1")
    refuses("result: a result naming another run is refused", rs(1, "done", run="r0"), "not the open run")
    refuses("result: an unknown outcome is refused", rs(1, "finished"), "outcome 'finished' is not one of")
    refuses("blocked: a block naming no dependency is refused", rs(3, "blocked"), "blocked names no dependency")
    check("blocked: a block naming its dependency is accepted", rs(3, "blocked", on="FOO_ITEM") == [],
          rs(3, "blocked", on="FOO_ITEM"))
    refuses("return: to a later stage is refused", rs(3, "return", to=4, decision="x"), "an earlier stage")
    refuses("return: to no stage is refused", rs(3, "return", decision="x"), "an earlier stage")
    refuses("return: an owner question returning past stage 2 is refused",
            rs(3, "return", to=0, decision="x", question="Wood?"), "returns to stage 2, not 0")
    check("return: an earlier stage with a named decision is accepted", rs(3, "return", to=2, decision="x") == [],
          rs(3, "return", to=2, decision="x"))
    refuses("waiting_owner: with no ask sent is refused", rs(2, "waiting_owner"), "with no ask in status sent")
    refuses("done: stage 0 with no inventory is refused", rs(0, "done", rec=dict(base, inventory=[],
                                                                                failure_modes=["a", "b", "c"])),
            "stage 0: no inventory")
    refuses("done: stage 1 with no root is refused", rs(1, "done", rec={"inventory": [inv()]}), "stage 1: no root")
    check("done: stage 1 with his root is accepted", rs(1, "done") == [], rs(1, "done"))
    refuses("done: stage 2 with an unresolved core contradiction is refused",
            rs(2, "done", rec=dict(base, contradictions=[{"id": "c1", "source": "log.md#L2", "core": True}])),
            "core contradiction c1 is unresolved")
    refuses("done: stage 3 with no scenes.json is refused", rs(3, "done"), "scenes.json is missing")
    refuses("done: stage 3 with no floor.json is refused", rs(3, "done"), "floor.json is missing")


def refusals_launcher(tmp, repo):
    """The launcher's own verbs, one guard at a time: blocked, abort, retries, manifest, charges, journal, record."""
    # blocked: the state holds, open refuses, unblock releases
    dB = os.path.join(tmp, "design/concepts/Blk")
    DS.init(dB, "Blk", "BLK_ITEM", cap=100000, reserve=20000)
    ok, errs = run_cycle(repo=repo, d=dB, run="b1", outcome="blocked", on="FOO_DEPENDENCY")
    st = DS.load_state(dB)
    check("blocked: the result is accepted, the state is blocked on the named dependency, the stage holds",
          ok and st["status"] == "blocked" and st["blocked_on"] == "FOO_DEPENDENCY" and st["stage"] == 0
          and st["results"][-1].get("on") == "FOO_DEPENDENCY", (ok, errs, st["status"]))
    r = refused(DS.open_run, dB, "b2", repo=repo.root)
    check("blocked: the next run is refused while the block stands", r and "BLOCKED on FOO_DEPENDENCY" in r, r)
    check("blocked: the refused open is written to the concept's history",
          (DS.load_state(dB)["history"][-1]["what"], DS.load_state(dB)["history"][-1]["why"][:10]) == ("refused", "BLOCKED on"),
          DS.load_state(dB)["history"][-1])
    DS.unblock(dB, "FOO_DEPENDENCY landed")
    check("blocked: unblock releases it", DS.load_state(dB)["status"] == "ready"
          and refused(DS.open_run, dB, "b3", repo=repo.root) is None, DS.load_state(dB)["status"])
    r = refused(DS.unblock, dB, "again")
    check("unblock on a concept that is not blocked is refused", r and "not blocked" in r, r)
    # abort: only the open run, nothing charged
    spent = DS.load_state(dB)["budget"]["spent"]
    check("abort: another run's id drops nothing", DS.abort_run(dB, "b9") is False
          and DS.load_state(dB)["running"]["run"] == "b3", DS.load_state(dB)["running"])
    check("abort: the open run is dropped and nothing is charged", DS.abort_run(dB, "b3") is True
          and DS.load_state(dB)["running"] is None and DS.load_state(dB)["budget"]["spent"] == spent, "")
    # close: only the open run; a rejected result is moved aside; retries reach the packet
    DS.open_run(dB, "b4", repo=repo.root)
    r = refused(DS.close_run, dB, "b5", 10, repo=repo.root)
    check("close: a run that is not the open run is refused", r and "not the open run" in r, r)
    result(dB, "finished")
    ok, _ = DS.close_run(dB, "b4", 10, repo=repo.root)
    check("close: a rejected result.json is moved aside, never left to be read as the next run's",
          not ok and not os.path.exists(os.path.join(dB, "result.json"))
          and os.path.exists(os.path.join(dB, "result.b4.rejected.json")), os.listdir(dB))
    text, _ = DS.open_run(dB, "b6", repo=repo.root)
    check("packet: a stage with rejected runs says so", "rejected or unclosed run(s)" in text, text[:400])
    DS.abort_run(dB, "b6")
    # waiting_owner: his reply turns the state back to ready at open
    st = DS.load_state(dB)
    st["status"], st["waiting_owner_feed"] = "waiting_owner", "a feed from before his reply"
    DS.write_json(DS.state_path(dB), st)
    DS.open_run(dB, "b7", repo=repo.root)
    check("waiting_owner: once he moved, the opened run leaves the state ready", DS.load_state(dB)["status"] == "ready",
          DS.load_state(dB)["status"])
    DS.abort_run(dB, "b7")
    # charges and init
    r = refused(DS.charge, dB, -5, "helper", "x")
    check("a negative charge is refused", r and "whole number" in r, r)
    r = refused(DS.charge, dB, 2.5, "helper", "x")
    check("a fractional charge is refused", r and "whole number" in r, r)
    r = refused(DS.init, dB, "Blk", "BLK_ITEM")
    check("init over an existing stage.json is refused", r and "already exists" in r, r)
    for cap, res_ in ((100, 0), (100, 100), (100, 150)):
        r = refused(DS.init, os.path.join(tmp, "design/concepts/Cap%d_%d" % (cap, res_)), "C", "C_ITEM",
                    cap=cap, reserve=res_)
        check("init: reserve %d against cap %d is refused" % (res_, cap), r and "reserve" in r, r)
    # manifest: every stage named, every file present
    md = os.path.join(tmp, "manifest")
    os.makedirs(md)
    put(md, "core.md", "core")
    mp = os.path.join(md, "m.json")
    with open(mp, "w") as f:
        json.dump({"stage_%d" % s: ["core.md"] for s in range(5)}, f)
    r = refused(DS.load_manifest, mp)
    check("manifest: one with no packet list for stage 5 is refused", r and "every stage" in r, r)
    with open(mp, "w") as f:
        json.dump(dict({"stage_%d" % s: ["core.md"] for s in range(6)}, stage_2=["core.md", "gone.md"]), f)
    r = refused(DS.manifest_hashes, 2, mp)
    check("manifest: a packet file that is missing is refused, never supplied short", r and "gone.md" in r, r)
    check("manifest: a present packet hashes", DS.manifest_hashes(0, mp) == {"core.md": DS.sha_file(
        os.path.join(md, "core.md"))}, DS.manifest_hashes(0, mp))
    # scene journal
    r = refused(DS.scene_end, dB, "never_begun")
    check("scene-end on a scene with no open recovery is refused", r and "no open recovery" in r, r)
    DS.scene_begin(dB, "s1", "restore sand from snapshot S2")
    DS.scene_end(dB, "s1", held=True, until="Friday's review")
    text, _ = DS.open_run(dB, "b8", repo=repo.root)
    check("a held scene's packet line carries until when", "s1 (until Friday's review)" in text, "")
    DS.abort_run(dB, "b8")
    # owner_uncited: no item means unmeasured, not 'nothing uncited'
    check("owner_uncited with no item is None (unmeasured), not []", DS.owner_uncited(repo.root, None) is None, "")
    # working record: root, empty, asks status, failure modes
    wd = os.path.join(tmp, "wr2")
    os.makedirs(wd)
    put(wd, "record.json", {})
    check("working record: an empty record says so", "(empty" in DS.working_record(wd), DS.working_record(wd))
    put(wd, "record.json", {"root": {"text": "climb out", "source": "OWNER:1001"},
                            "asks": [{"id": "a7", "text": "q?", "status": "sent", "source": "log.md#L2"}],
                            "failure_modes": ["fm-one", "fm-two"]})
    wr = DS.working_record(wd)
    check("working record: the root line carries its source", "root: climb out [OWNER:1001]" in wr, wr)
    check("working record: an ask line carries its status", "- a7: q? status=sent [log.md#L2]" in wr, wr)
    check("working record: the failure modes are listed", "failure_modes: fm-one | fm-two" in wr, wr)


def wiring(tmp, repo):
    import role_launch as RL
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("ledger_item") ==
               "CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING")
    check("schedule: the Designer row names the stage machine", row.get("stage_machine") == "designer_stage", row)
    row = dict(row, clone=tmp)
    s2 = {"roles": [row]}
    try:
        RL.run_now_request(s2, {"role": row["name"], "by": "BENCH", "why": "w"}, 1.0)
        got = None
    except ValueError as e:
        got = str(e)
    check("run-now: the Designer needs --concept", got and "--concept" in got, got)
    try:
        RL.run_now_request(s2, {"role": row["name"], "by": "BENCH", "why": "w", "concept": "design/concepts/Nope"}, 1.0)
        got = None
    except ValueError as e:
        got = str(e)
    check("run-now: a concept with no stage.json is refused", got and "stage.json" in got, got)
    other = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("name") and not r.get("stage_machine")
                 and r.get("run_token_cap"))
    try:
        RL.run_now_request({"roles": [dict(other, clone=tmp)]}, {"role": other["name"], "by": "BENCH", "why": "w",
                                                               "concept": "design/concepts/Wire"}, 1.0)
        got = None
    except ValueError as e:
        got = str(e)
    check("run-now: --concept on a role with no stage machine is refused", got and "stage-machine role" in got, got)
    d = os.path.join(tmp, "design/concepts/Wire")
    DS.init(d, "Wire", "WIRE_ITEM", cap=100000, reserve=10000)
    req = RL.run_now_request(s2, {"role": row["name"], "by": "BENCH", "why": "w", "concept": "design/concepts/Wire"}, 1.0)
    check("run-now: the concept is resolved against the role's clone", req.get("concept") == d, req)
    before = open(DS.state_path(d)).read()
    packet, budget = RL.stage_open(d, "rm-role-designer-1", 500000)
    check("decide's preview writes nothing", open(DS.state_path(d)).read() == before and budget == 90000, budget)
    RL.stage_open(d, "rm-role-designer-1", 90000, commit=True)
    check("execute's commit records the open run", DS.load_state(d)["running"]["run"] == "rm-role-designer-1", "")
    check("a launch that never happened is aborted uncharged", RL.stage_abort(d, "rm-role-designer-1") and
          DS.load_state(d)["budget"]["spent"] == 0 and DS.load_state(d)["running"] is None, "")
    # decide: the packet rides in the launch message; a refusal consumes the run-now with an alarm
    import time as _t
    now = _t.time()
    st = {"roles": {row["name"]: {"run_now": dict(req, at=now - 5)}}}
    acts = []
    robs = {"ops": lambda: None, "account": lambda: "acct", "unit_state": lambda u: "active",
            "result": lambda r: None, "off": lambda p: None}
    RL.decide_roles(s2, st, robs, now, lambda **kw: acts.append(kw), set(), None)
    la = [a for a in acts if a.get("do") == "role_launch"]
    check("decide: the Designer's launch message carries the stage packet and the concept",
          len(la) == 1 and "designer_stage.py packet" in la[0]["message"] and la[0].get("concept") == d,
          [(a.get("do"), a.get("why")) for a in acts])
    # execute: the stage's run is committed BEFORE systemd-run, under the launched unit; a launch systemd-run
    # refuses drops that open run uncharged
    import dispatcher as D
    xroot = os.path.join(tmp, "exec")
    os.makedirs(xroot)
    seen = []

    def fake_launch(ok):
        def f(r, unit, msg, root_, claude):
            seen.append((unit, (DS.load_state(d).get("running") or {}).get("run")))
            return (True, "ok", {}) if ok else (False, "systemd-run said no", None)
        return f
    fx = {"off": lambda p: None, "paused": lambda: None, "note": lambda i, t: (True, ""), "publish": lambda n: None}
    st.setdefault("alarms", {})
    D.execute(la, s2, st, xroot, True, now, dict(fx, role_launch=fake_launch(True)))
    check("execute: the stage's run is open in stage.json under the launched unit before systemd-run runs",
          len(seen) == 1 and seen[0][0] == la[0]["unit"] and seen[0][1] == la[0]["unit"]
          and DS.load_state(d)["running"]["run"] == la[0]["unit"], (seen, [a.get("result") for a in la]))
    DS.abort_run(d, la[0]["unit"])
    spent = DS.load_state(d)["budget"]["spent"]
    st = {"roles": {row["name"]: {"run_now": dict(req, at=now - 5)}}}
    acts = []
    RL.decide_roles(s2, st, robs, now, lambda **kw: acts.append(kw), set(), None)
    la2 = [a for a in acts if a.get("do") == "role_launch"]
    seen.clear()
    st.setdefault("alarms", {})
    D.execute(la2, s2, st, xroot, True, now, dict(fx, role_launch=fake_launch(False)))
    check("execute: a launch systemd-run refuses drops the stage's open run, uncharged",
          len(seen) == 1 and seen[0][1] == la2[0]["unit"] and DS.load_state(d)["running"] is None
          and DS.load_state(d)["budget"]["spent"] == spent, (seen, DS.load_state(d)["running"]))
    # decide: the role's own run cap reaches the stage machine (min of it and what the task budget leaves)
    rowc = dict(row, run_token_cap=40000)
    dc = os.path.join(tmp, "design/concepts/Capped")
    DS.init(dc, "Capped", "CAP_ITEM", cap=100000, reserve=10000)
    reqc = RL.run_now_request({"roles": [rowc]}, {"role": row["name"], "by": "BENCH", "why": "w",
                                                  "concept": "design/concepts/Capped"}, 1.0)
    stc = {"roles": {row["name"]: {"run_now": dict(reqc, at=now - 5)}}}
    acts = []
    RL.decide_roles({"roles": [rowc]}, stc, robs, now, lambda **kw: acts.append(kw), set(), None)
    lac = [a for a in acts if a.get("do") == "role_launch"]
    check("decide: a role cap under the task budget's remainder is the run's budget, and the packet says so",
          len(lac) == 1 and lac[0]["budget"] == 40000 and "this run 40000 weighted tokens" in lac[0]["message"],
          [(a.get("do"), a.get("budget"), a.get("why")) for a in acts])
    DS.charge(d, 95000, "consult", "gpt")
    st = {"roles": {row["name"]: {"run_now": dict(req, at=now - 5)}}}
    acts = []
    RL.decide_roles(s2, st, robs, now, lambda **kw: acts.append(kw), set(), None)
    check("decide: an exhausted budget is advisory: the run-now still launches (owner 2026-11-04)",
          [a for a in acts if a.get("do") == "role_launch"], [(a.get("do"), a.get("why")) for a in acts])
    sb = DS.load_state(d)
    sb["status"], sb["blocked_on"], sb["running"] = "blocked", "X", None
    DS.write_json(DS.state_path(d), sb)
    st = {"roles": {row["name"]: {"run_now": dict(req, at=now - 5)}}}
    acts = []
    RL.decide_roles(s2, st, robs, now, lambda **kw: acts.append(kw), set(), None)
    check("decide: the refused run-now stops there: no launch, no unit, and deciding it raises nothing",
          not [a for a in acts if a.get("do") == "role_launch" or a.get("unit")]
          and not [a for a in acts if a.get("kind") == "role:%s:schedule" % row["name"]],
          [(a.get("do"), a.get("unit"), a.get("kind")) for a in acts])
    check("decide: a blocked concept refuses the run-now with an alarm, no launch",
          not [a for a in acts if a.get("do") == "role_launch"]
          and any(a.get("kind") == "role:%s:stage_refused" % row["name"] for a in acts)
          and "refused" in str(st["roles"][row["name"]].get("run_now_last", {}).get("outcome")),
          [(a.get("do"), a.get("why")) for a in acts])
    # supervise: the run's tokens are charged and result.json judged
    d4 = os.path.join(tmp, "design/concepts/Sup")
    DS.init(d4, "Sup", "SUP_ITEM", cap=100000, reserve=10000)
    DS.open_run(d4, "rm-role-designer-9", repo=repo.root)
    rs = {"runs": [{"state": "running", "unit": "rm-role-designer-9", "at": now - 60, "day": RL.day_of(now),
                    "budget": 90000, "mode": "run", "item": "X", "concept": d4,
                    "scope": "S.scope", "marker": "M"}]}
    res = {"subtype": "success", "usage": {k: 0 for k in RL.USAGE_KEYS}}
    res["usage"]["input_tokens"] = 4000
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: []}
    RL._supervise_one(row["name"], rs, dict(RL.ROLE_DEFAULTS, **row), obs, now, lambda **kw: acts.append(kw), set())
    st4 = DS.load_state(d4)
    check("supervise: the finished run is charged to the task and its missing result is an alarm",
          st4["budget"]["spent"] == 4000 and st4["running"] is None
          and any(a.get("kind") == "role:%s:stage_rejected" % row["name"] and a.get("do") == "alarm" for a in acts),
          (st4["budget"], [(a.get("do"), a.get("kind")) for a in acts]))


if __name__ == "__main__":
    sys.exit(main())
