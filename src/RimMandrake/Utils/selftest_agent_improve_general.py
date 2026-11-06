#!/usr/bin/env python3
"""Selftest for agent_improve_general.py (design 4.3): the sample (held-out kinds exclude the source kinds, spread over
kinds, only closes inside the window), the blind judge (A/B order varies, the outcome is mapped back to the new text),
the null control and the noise floor (harm or gain only past the null margin and the sign test, else no_signal), the
verdicts overfit, general, narrow, no_signal and unmeasured, the evidence file and the append-only change record, `show`,
and the L2 gate in agent_improve.apply_change. Agents are stubs; no model runs. The real ledger is only read, to prove
the rule change is recorded."""
import json
import os
import random
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agent_improve as A  # noqa: E402
import agent_improve_general as G  # noqa: E402

fails = []


def check(name, cond, detail=""):
    if not cond:
        fails.append(name)
        print("FAIL: %s %s" % (name, str(detail)[:400]))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


NOW = A.epoch("2026-11-06T00:00:00Z")
T = "rimworld-modding"   # a real skill, so resolve_target works; its texts below are fakes
OLD, NEW = "# skill\nOLD-RULES\n", "# skill\nNEW-RULES\n"
KINDS = ["AUDIT", "REPAIR", "WIRE", "PROBE", "HUNT", "TUNE", "DEBUG", "BUILD"]


def fixture(tmp):
    ev, items = os.path.join(tmp, "events"), os.path.join(tmp, "items")
    lines = []
    for k in KINDS:
        for i in range(6):
            iid = "THING%s_%s_CASE_NUMBER_%s" % (i, k, "ABCDEF"[i])
            lines.append({"event": "file", "id": iid, "kind": "task", "title": "Do the %s thing %d well" % (k, i)})
            lines.append({"event": "close", "id": iid, "ts": "2026-10-%dT10:00:00Z" % (24 + i), "sha": "abc%d" % i,
                          "reason": "landed the %s fix" % k})
            write(os.path.join(items, "closed", iid + ".md"), "# %s\n\nA spec long enough to read for %s.\n" % (iid, k))
    lines.append({"event": "file", "id": "OLDCASE_REPAIR_LONG_AGO_GONE", "kind": "task", "title": "x" * 50})
    lines.append({"event": "close", "id": "OLDCASE_REPAIR_LONG_AGO_GONE", "ts": "2026-09-01T00:00:00Z"})
    lines.append({"event": "drop", "id": "DROPPED_AUDIT_NEVER_CLOSED_AT_ALL", "ts": "2026-11-02T00:00:00Z"})
    write(os.path.join(ev, "BENCH.jsonl"), "\n".join(json.dumps(x) for x in lines) + "\nnot json\n")
    return ev, items


def runner(prompt):
    return "PLAN: follow %s" % ("NEWWAY" if "NEW-RULES" in prompt else "OLDWAY")


def labelled_runner(fail_rerun=False):
    """Marks the second run of the same old prompt RERUN, so a stub judge can tell the two old answers apart."""
    lock, seen = threading.Lock(), {}

    def rnr(prompt):
        if "NEW-RULES" in prompt:
            return "PLAN: follow NEWWAY"
        with lock:
            seen[prompt] = seen.get(prompt, 0) + 1
            again = seen[prompt] > 1
        if again and fail_rerun:
            raise OSError("claude: out of credit")
        return "PLAN: follow OLDWAY" + (" RERUN" if again else "")
    return rnr


def judge_by(table, seen, null="tie"):
    """table: kind -> 'new' | 'old' | 'tie' (who the judge prefers for that kind's items).
    null: 'tie' or 'rerun', what it does when both answers are the old text (needs labelled_runner to pick the rerun)."""
    def judge(prompt):
        seen.append(prompt)
        kind = next(k for k in KINDS if "Do the %s thing" % k in prompt)
        if "NEWWAY" not in prompt:   # a null pair
            if null == "tie":
                return '{"better": "tie", "why": "even"}'
            a = prompt.split("===== ANSWER A =====")[1].split("===== ANSWER B =====")[0]
            return '{"better": "%s", "why": "noise"}' % ("A" if "RERUN" in a else "B")
        want = table.get(kind, "tie")
        if want == "tie":
            return '{"better": "tie", "why": "even"}'
        a = prompt.split("===== ANSWER A =====")[1].split("===== ANSWER B =====")[0]
        a_is_new = "NEWWAY" in a
        pick = "A" if (want == "new") == a_is_new else "B"
        return 'Sure. {"better": "%s", "why": "better plan"}' % pick
    return judge


with tempfile.TemporaryDirectory() as tmp:
    ev, items = fixture(tmp)
    pool = G.closed_items(NOW, 14, ev)
    check("window: 48 closes in, the September close and the drop out", len(pool) == 48
          and "OLDCASE_REPAIR_LONG_AGO_GONE" not in pool, sorted(pool))
    check("kind is the intent word", pool["THING0_AUDIT_CASE_NUMBER_A"]["kind"] == "AUDIT"
          and pool["THING0_AUDIT_CASE_NUMBER_A"]["ledger_kind"] == "task")
    held, src = G.sample(pool, ["REPAIR"], random.Random(1))
    check("6 held out, none of the source kind", len(held) == 6 and all(i["kind"] != "REPAIR" for i in held),
          [i["id"] for i in held])
    check("held out spread over 6 kinds", len({i["kind"] for i in held}) == 6, [i["kind"] for i in held])
    check("6 source items, all REPAIR", len(src) == 6 and all(i["kind"] == "REPAIR" for i in src))
    h2, _ = G.sample(pool, ["REPAIR"], random.Random(2))
    check("fresh each time: another seed, another sample", {i["id"] for i in h2} != {i["id"] for i in held})

    def run(table, kinds=("REPAIR",), seed=7, rnr=runner, null="tie"):
        seen = []
        r = G.check(T, OLD, NEW, list(kinds), now=NOW, seed=seed, runner=rnr, judge=judge_by(table, seen, null),
                    events_dir=ev, items_dir=items)
        return r, seen

    every = {k: "old" for k in KINDS if k != "REPAIR"}
    r, seen = run(dict(every, REPAIR="new"))
    check("harm: held-out losses beat wins -> overfit, revert", r["verdict"] == "overfit" and r["keep"] is False
          and r["held_out"]["loss"] == 6 and r["source"]["win"] == 6, r["held_out"])
    check("blind: the judge prompt never names old or new text", all("OLD-RULES" not in p and "NEW-RULES" not in p
                                                                        for p in seen))
    order = {p["new_is_a"] for p in r["pairs"]}
    check("A/B order varies across pairs", order == {True, False}, order)
    r, _ = run({k: "new" for k in KINDS})
    check("gain on held out -> general, keep", r["verdict"] == "general" and r["keep"] is True, r["held_out"])
    r, _ = run({"REPAIR": "new"})
    check("gain on the source kind only, held out ties -> narrow, keep", r["verdict"] == "narrow"
          and r["keep"] is True and r["held_out"]["tie"] == 6, (r["held_out"], r["source"]))
    r, _ = run({})
    check("all ties -> no_signal, which neither reverts nor keeps", r["verdict"] == "no_signal" and r["keep"] is None)
    check("no_no_gain: the old revert-on-nothing verdict is gone", "no_gain" not in G.VERDICTS and "no_gain" not in G.KEEP)
    mixed = dict({k: "tie" for k in KINDS}, REPAIR="old")
    r, _ = run(mixed)
    check("source losses alone are not harm: no_signal", r["verdict"] == "no_signal", r)

    # the null control: measured on the same sample, recorded beside each check
    calls, lock = [], threading.Lock()

    def counting(prompt):
        with lock:
            calls.append(prompt)
        return runner(prompt)
    r, seen = run({k: "new" for k in KINDS}, rnr=counting)
    judged = [p for p in r["pairs"] if p["outcome"] in ("win", "loss", "tie")]
    check("every judged pair carries its null, on the same item", judged and all(p["null"]["outcome"] == "tie"
                                                                                 for p in judged), r["pairs"][:1])
    check("each item: old text twice, new text once, with the same task", len(calls) == 3 * len(r["pairs"]) and all(
        sum(1 for c in calls if c == c0) == (1 if "NEW-RULES" in c0 else 2) for c0 in calls), len(calls))
    check("two blind judgments per item, the null's old against old", len(seen) == 2 * len(r["pairs"])
          and sum(1 for p in seen if "NEWWAY" not in p) == len(r["pairs"]), len(seen))
    check("null tallies stand beside the real ones", r["null_held_out"] == {"win": 0, "loss": 0, "tie": 6, "error": 0}
          and r["null_source"]["tie"] == 6 and r["held_out"]["win"] == 6, r["null_held_out"])
    check("the stated rule and each sample's reading are recorded", G.RULE == r["rule"] and "0.05" in r["rule"]
          and r["signal"]["held_out"]["call"] == "gain" and r["signal"]["held_out"]["sign_p"] == 0.0156,
          r["signal"]["held_out"])
    s = G.summary(r, "e", {})
    check("the summary carries the null too", s["null_held_out"] == r["null_held_out"] and s["signal"] == r["signal"]
          and s["rule"] == r["rule"], s)

    # the null outcome maps to the rerun, whichever slot it had
    it = {"id": "THING0_AUDIT_CASE_NUMBER_A", "kind": "AUDIT", "close_text": "closed"}
    def picks_new_else_rerun(p):
        a = p.split("===== ANSWER A =====")[1].split("===== ANSWER B =====")[0]
        return '{"better": "%s", "why": "w"}' % ("A" if "THE-NEW" in a or "OLD-TWO" in a else "B")
    for rerun_is_a in (True, False):
        answers = iter(["OLD-ONE", "THE-NEW", "OLD-TWO"])
        rec = G.run_pair(it, "Do the AUDIT thing", "o", "n", "skill", True, lambda _p: next(answers),
                         picks_new_else_rerun, rerun_is_a=rerun_is_a)
        check("rerun picked is a null win, rerun_is_a=%s" % rerun_is_a, rec["outcome"] == "win"
              and rec["null"]["outcome"] == "win" and ("OLD-TWO" in rec["null"]["a"]) == rerun_is_a, rec.get("null"))

    # the first real run: 2 wins, 3 losses, 1 tie must read no_signal, whatever the null did
    z = {"win": 0, "loss": 0, "tie": 0, "error": 0}
    first = {"win": 2, "loss": 3, "tie": 1, "error": 0}
    check("2-3-1 direct, null all ties -> no_signal", G.verdict(first, z, dict(z, tie=6), z) == "no_signal")
    check("2-3-1 direct, null 3-3 -> no_signal", G.verdict(first, z, dict(z, win=3, loss=3), z) == "no_signal")
    r0, _ = run({})
    order = [p["kind"] for p in r0["pairs"] if p["side"] == "held_out"]
    table = dict(zip(order, ["new", "new", "old", "old", "old", "tie"]))
    r, _ = run(table)
    check("2-3-1 through the whole check -> no_signal, keep None, no revert", r["verdict"] == "no_signal"
          and r["keep"] is None and (r["held_out"]["win"], r["held_out"]["loss"], r["held_out"]["tie"]) == (2, 3, 1),
          r["held_out"])

    # each bar on its own
    h = lambda w, l, t=0: dict(z, win=w, loss=l, tie=t)   # noqa: E731
    quiet = h(0, 0, 6)
    check("sign test values", G.sign_p(5, 0) == 1 / 32 and G.sign_p(4, 0) == 1 / 16 and G.sign_p(1, 5) == 7 / 64
          and G.sign_p(0, 0) == 1.0, G.sign_p(1, 5))
    check("6-0 and 5-0 clear both bars", G.verdict(h(6, 0), z, quiet, z) == "general"
          and G.verdict(h(0, 6), z, quiet, z) == "overfit" and G.verdict(h(5, 0, 1), z, quiet, z) == "general"
          and G.verdict(h(0, 5, 1), z, quiet, z) == "overfit")
    check("sign bar alone stops 4-0 and 5-1 though the null is silent", G.verdict(h(4, 0, 2), z, quiet, z) == "no_signal"
          and G.verdict(h(5, 1), z, quiet, z) == "no_signal" and G.verdict(h(0, 4, 2), z, quiet, z) == "no_signal")
    check("margin bar alone stops 5-0 when the null reached 5", G.verdict(h(5, 0, 1), z, h(5, 0, 1), z) == "no_signal"
          and G.verdict(h(0, 5, 1), z, h(0, 5, 1), z) == "no_signal")
    check("a null of the other sign counts the same", G.verdict(h(5, 0, 1), z, h(0, 5, 1), z) == "no_signal")
    check("clears a smaller null margin", G.verdict(h(6, 0), z, h(3, 0, 3), z) == "general"
          and G.verdict(h(5, 0, 1), z, h(3, 1, 2), z) == "general")
    check("a failed null pair widens the margin", G.noise_margin(h(1, 0, 3) | {"error": 2}) == 3
          and G.verdict(h(6, 0), z, dict(z, error=6), z) == "no_signal")
    check("source needs both bars too", G.verdict(quiet, h(2, 0), quiet, h(0, 0, 2)) == "no_signal"
          and G.verdict(quiet, h(5, 0, 1), quiet, h(5, 0, 1)) == "no_signal"
          and G.verdict(quiet, h(5, 0, 1), quiet, quiet) == "narrow")
    check("a held-out call beats a source gain", G.verdict(h(0, 6), h(6, 0), quiet, quiet) == "overfit")

    # noise reaching the real result through the whole check
    every_new = {k: "new" for k in KINDS}
    r, _ = run(every_new, rnr=labelled_runner(), null="rerun")
    check("a judge as decisive on nothing as on the change: 6-0 reads no_signal", r["verdict"] == "no_signal"
          and r["keep"] is None and r["held_out"]["win"] == 6 and r["null_held_out"]["win"] == 6,
          (r["held_out"], r["null_held_out"]))
    r, _ = run(every_new, rnr=labelled_runner(fail_rerun=True))
    check("null runs all fail: the real pairs stand but no call is made", r["verdict"] == "no_signal"
          and r["held_out"]["win"] == 6 and r["null_held_out"]["error"] == 6, (r["held_out"], r["null_held_out"]))
    check("a pair that failed before judging owes no null", all("null" not in p for p in run({}, rnr=lambda _p: 1 / 0)[0]
                                                                ["pairs"]))

    def broken(prompt):
        raise OSError("claude: not found")   # not a RuntimeError: a worker thread must still not crash the check
    r, _ = run({}, rnr=broken)
    check("no pair judged -> unmeasured, keep None", r["verdict"] == "unmeasured" and r["keep"] is None
          and all(p["outcome"] == "error" for p in r["pairs"]))
    r, _ = run({k: "new" for k in KINDS}, kinds=KINDS)   # every kind is a source kind: nothing held out
    check("source gain with no held-out pair -> unmeasured, never kept", r["verdict"] == "unmeasured"
          and r["keep"] is None and r["source"]["win"] >= 1 and r["source"]["loss"] == 0, (r["held_out"], r["source"]))

    # the record: evidence file, appended summary, never rewritten; show
    changes, gdir = os.path.join(tmp, "changes"), os.path.join(tmp, "general")
    write(os.path.join(changes, "%s_v3.json" % T), json.dumps({"target": T, "version": 3, "generalization": []}))
    rc, _ = G.show(T, "v3", changes_dir=changes, repo=tmp)
    check("show: no entry -> 1", rc == 1)
    r1, _ = run({k: "new" for k in KINDS})
    e1, c1 = G.record(r1, T, 3, changes, gdir, tmp, {"old": "a", "new": "b"})
    r2, _ = run({})
    r2["at"] = "2026-11-06T00:00:01Z"
    G.record(r2, T, 3, changes, gdir, tmp, {"old": "a", "new": "b"})
    gens = json.load(open(c1))["generalization"]
    check("appended, first entry unchanged", [g["verdict"] for g in gens] == ["general", "no_signal"]
          and gens[0]["evidence"] == os.path.relpath(e1, tmp), gens)
    check("evidence holds both answers of every pair", all("a" in p and "b" in p for p in json.load(open(e1))["pairs"]))
    rc, lines = G.show(T, "v3", changes_dir=changes, repo=tmp)
    check("show: judged entry -> 0", rc == 0 and len(lines) == 2, lines)
    check("show prints the null beside the real tally", "null_held_out={'win': 0" in lines[0], lines[0])

    # the L2 gate in apply_change
    repo = os.path.join(tmp, "repo")
    write(os.path.join(repo, "skills", T, "SKILL.md"), OLD)
    for c in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "f"]):
        subprocess.run(["git"] + c, cwd=repo, check=True, capture_output=True)
    gchanges = os.path.join(repo, "infrastructure", "state", "agent_improve", "changes")
    row = {"target": T, "new_text": NEW, "cites": [0], "diff": "x", "day": "2026-11-06"}
    ent = {"pieces": [{"text": "lesson about THING0_REPAIR_CASE_NUMBER_A"}]}
    got = {}

    def stub_general(verdict):
        def g(t, old, new, kinds):
            got.update(t=t, old=old, new=new, kinds=kinds)
            return {"at": "x", "verdict": verdict, "keep": G.KEEP[verdict], "held_out": {}, "source": {}, "seed": 1}
        return g
    out = os.path.join(tmp, "out")
    os.makedirs(out)
    ok, why = A.apply_change(dict(row), ent, out, repo=repo, pk_level=2, general=stub_general("overfit"),
                             changes_dir=gchanges)
    check("L2 gate refuses an overfit change", not ok and "overfit" in why, why)
    check("gate passes current text, proposed text and source kinds", got == {"t": T, "old": OLD, "new": NEW,
                                                                              "kinds": ["REPAIR"]}, got)
    ok, why = A.apply_change(dict(row), ent, out, repo=repo, pk_level=2)
    check("L2 gate refuses with no checker", not ok and "generalization" in why, why)
    ok, why = A.apply_change(dict(row), ent, out, repo=repo, pk_level=2, general=stub_general("no_signal"),
                             changes_dir=gchanges)
    check("L2 gate does not apply a no_signal change: unproven, not kept", not ok and "no_signal" in why, why)
    r = dict(row)
    ok, why = A.general_gate(r, ent, A.resolve_target(T), out, repo, stub_general("narrow"), gchanges)
    check("L2 gate keeps a narrow change and carries the flag", ok and why == "narrow"
          and r["general"]["verdict"] == "narrow")
    check("gate evidence goes to outdir, never into the repo before publish", os.path.dirname(r["general_path"]) == out
          and os.path.isfile(r["general_path"]) and not os.path.isdir(os.path.join(os.path.dirname(gchanges),
                                                                                    "general")), r["general"])
    os.makedirs(gchanges, exist_ok=True)
    r.update(path="skills/%s/SKILL.md" % T, verdict="KEEP", judge={"reasons": "", "violated": ""}, recheck="x")
    ent["pieces"][0]["path"] = "lessons/x.md"
    prep = A._prepare_record(r, ent, A.resolve_target(T), T, repo, gchanges, os.path.join(tmp, "delegated"))
    crec = json.load(open(prep[4], encoding="utf-8"))
    g0 = crec["generalization"][0]
    check("on publish the gate evidence is copied into general/ and named in the record and the commit paths",
          g0["verdict"] == "narrow" and g0["evidence"].startswith("infrastructure/state/agent_improve/general/")
          and os.path.isfile(os.path.join(repo, g0["evidence"])) and g0["evidence"] in prep[6], (g0, prep[6]))
    write(os.path.join(repo, "skills", T, "SKILL.md"), OLD + "dirty\n")
    got.clear()
    ok, why = A.apply_change(dict(row), ent, out, repo=repo, pk_level=2, general=stub_general("general"),
                             changes_dir=gchanges)
    check("a dirty target is refused before the gate judges working-tree text", not ok and "uncommitted" in why
          and not got, why)

# the change to the Conductor's verdict rule is on the ledger, with its reason
ITEM = "AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT"
notes = []
# Read from git at HEAD, never the folder: the walled checker's tree leaves the ledger out but has the history, and a
# record that counts is a committed one.
git = lambda *c: subprocess.run(["git"] + list(c), cwd=A.REPO, capture_output=True, text=True, errors="replace",  # noqa: E731
                                check=True).stdout
for path in git("ls-tree", "--name-only", "HEAD", os.path.relpath(G.EVENTS, A.REPO) + "/").splitlines():
    for ln in git("show", "HEAD:" + path).splitlines():
        if ITEM in ln and "noise_floor_v1" in ln:
            e = json.loads(ln)
            if e.get("id") == ITEM and e.get("event") == "note":
                notes.append(e)
check("the ledger records the rule change and why", notes and "2026-11-02" in json.dumps(notes[-1])
      and "2-3-1" in json.dumps(notes[-1]), notes)

print("selftest_agent_improve_general: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
