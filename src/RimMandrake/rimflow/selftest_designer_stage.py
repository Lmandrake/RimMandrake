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
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

FAILS = []
ITEM = "CONCEPT_FOO_ITEM"


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
    real_lint, real_gate = CT.lint, CT.gate
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
        rec = {"inventory": [inv()], "failure_modes": ["a", "b", "c"]}
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
        put(d, "scenes.json", {"scenes": [good, flood]})
        put(d, "floor.json", {"lines": lines})
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
                "scenarios": scen, "scenarios_hash": CT.sha(scen), "score": {"right": 10, "total": 10},
                "accept_where_reject_core": 0, "challenger_misses": []}
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
        rec["decisions"] = [{"id": "d_steel", "text": "steel ladders only", "source": steel, "speaker": "owner"}]
        put(d, "record.json", rec)
        ok, errs = run_cycle(d, repo, "run17b")
        ok2, _ = run_cycle(d, repo, "run18")       # stage 3 again
        check("after the correction the stages rerun in order (2, 3)", ok and ok2 and DS.load_state(d)["stage"] == 4,
              errs)
        put(d, "exam.json", dict(exam, inputs=DS.inputs(d, DS.load_state(d), repo.root)))
        ok, errs = run_cycle(d, repo, "run19")
        check("stage 4 done with a fresh exam -> stage 5", ok and DS.load_state(d)["stage"] == 5, errs)
        # an artifact edit after the exam invalidates stage 3 onward
        put(d, "scenes.json", {"scenes": [good, flood, expl]})
        text, _ = DS.open_run(d, "run20", repo=repo.root)
        check("an edited scenes.json after the exam reopens stage 3", DS.load_state(d)["stage"] == 3 and
              "scenes" in text, DS.load_state(d)["stage"])
        ok, _ = DS.close_run(d, "run20", 100, repo=repo.root)     # no result: a retry
        ok, errs = run_cycle(d, repo, "run21")
        put(d, "exam.json", dict(exam, inputs=DS.inputs(d, DS.load_state(d), repo.root)))
        ok2, errs2 = run_cycle(d, repo, "run22")
        CT.gate = lambda dd, rr=None, ff=None: (["no Arbiter coverage signature"], [])
        ok3, errs3 = run_cycle(d, repo, "run23")
        check("stage 5: done with a failing gate is refused", ok and ok2 and not ok3
              and any("gate:" in e for e in errs3), (errs, errs2, errs3))
        CT.gate = lambda dd, rr=None, ff=None: ([], [])
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
              st["budget"]["spent"] == 80000 and st["running"] is None, st["budget"])
        check("exhausted budget: refused, stage unchanged, the refusal says no gate is waived",
              r and "BUDGET_EXHAUSTED" in r and "never waives a gate" in r and st["stage"] == 0, r)
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

        # ---- the launcher wiring
        wiring(tmp, repo)
    finally:
        CT.lint, CT.gate = real_lint, real_gate
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d: %s" % (len(FAILS), FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


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
    DS.charge(d, 95000, "consult", "gpt")
    st = {"roles": {row["name"]: {"run_now": dict(req, at=now - 5)}}}
    acts = []
    RL.decide_roles(s2, st, robs, now, lambda **kw: acts.append(kw), set(), None)
    check("decide: an exhausted budget refuses the run-now with an alarm, no launch",
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
