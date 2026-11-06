#!/usr/bin/env python3
"""Selftest for agent_improve_general.py (design 4.3): the sample (held-out kinds exclude the source kinds, spread over
kinds, only closes inside the window), the blind judge (A/B order varies, the outcome is mapped back to the new text),
the four verdicts harm/overfit, gain/general, narrow and no_gain plus unmeasured, the evidence file and the
append-only change record, `show`, and the L2 gate in agent_improve.apply_change. Agents are stubs; the real repo,
ledger and models are never touched."""
import json
import os
import random
import subprocess
import sys
import tempfile

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
        for i in range(3):
            iid = "THING%s_%s_CASE_NUMBER_%s" % (i, k, "ABC"[i])
            lines.append({"event": "file", "id": iid, "kind": "task", "title": "Do the %s thing %d well" % (k, i)})
            lines.append({"event": "close", "id": iid, "ts": "2026-11-0%dT10:00:00Z" % (i + 1), "sha": "abc%d" % i,
                          "reason": "landed the %s fix" % k})
            write(os.path.join(items, "closed", iid + ".md"), "# %s\n\nA spec long enough to read for %s.\n" % (iid, k))
    lines.append({"event": "file", "id": "OLDCASE_REPAIR_LONG_AGO_GONE", "kind": "task", "title": "x" * 50})
    lines.append({"event": "close", "id": "OLDCASE_REPAIR_LONG_AGO_GONE", "ts": "2026-09-01T00:00:00Z"})
    lines.append({"event": "drop", "id": "DROPPED_AUDIT_NEVER_CLOSED_AT_ALL", "ts": "2026-11-02T00:00:00Z"})
    write(os.path.join(ev, "BENCH.jsonl"), "\n".join(json.dumps(x) for x in lines) + "\nnot json\n")
    return ev, items


def runner(prompt):
    return "PLAN: follow %s" % ("NEWWAY" if "NEW-RULES" in prompt else "OLDWAY")


def judge_by(table, seen):
    """table: kind -> 'new' | 'old' | 'tie' (who the judge prefers for that kind's items)."""
    def judge(prompt):
        seen.append(prompt)
        kind = next(k for k in KINDS if "Do the %s thing" % k in prompt)
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
    check("window: 24 closes in, the September close and the drop out", len(pool) == 24
          and "OLDCASE_REPAIR_LONG_AGO_GONE" not in pool, sorted(pool))
    check("kind is the intent word", pool["THING0_AUDIT_CASE_NUMBER_A"]["kind"] == "AUDIT"
          and pool["THING0_AUDIT_CASE_NUMBER_A"]["ledger_kind"] == "task")
    held, src = G.sample(pool, ["REPAIR"], random.Random(1))
    check("6 held out, none of the source kind", len(held) == 6 and all(i["kind"] != "REPAIR" for i in held),
          [i["id"] for i in held])
    check("held out spread over 6 kinds", len({i["kind"] for i in held}) == 6, [i["kind"] for i in held])
    check("2 source items, all REPAIR", len(src) == 2 and all(i["kind"] == "REPAIR" for i in src))
    h2, _ = G.sample(pool, ["REPAIR"], random.Random(2))
    check("fresh each time: another seed, another sample", {i["id"] for i in h2} != {i["id"] for i in held})

    def run(table, kinds=("REPAIR",), seed=7, rnr=runner):
        seen = []
        r = G.check(T, OLD, NEW, list(kinds), now=NOW, seed=seed, runner=rnr, judge=judge_by(table, seen),
                    events_dir=ev, items_dir=items)
        return r, seen

    every = {k: "old" for k in KINDS if k != "REPAIR"}
    r, seen = run(dict(every, REPAIR="new"))
    check("harm: held-out losses beat wins -> overfit, revert", r["verdict"] == "overfit" and r["keep"] is False
          and r["held_out"]["loss"] == 6 and r["source"]["win"] == 2, r["held_out"])
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
    check("no gain anywhere -> no_gain, revert", r["verdict"] == "no_gain" and r["keep"] is False)
    mixed = dict({k: "tie" for k in KINDS}, REPAIR="old")
    r, _ = run(mixed)
    check("source losses alone are not harm: no_gain", r["verdict"] == "no_gain", r)

    def broken(prompt):
        raise OSError("claude: not found")   # not a RuntimeError: a worker thread must still not crash the check
    r, _ = run({}, rnr=broken)
    check("no pair judged -> unmeasured, keep None", r["verdict"] == "unmeasured" and r["keep"] is None
          and all(p["outcome"] == "error" for p in r["pairs"]))
    r, _ = run({"REPAIR": "new"}, kinds=KINDS)   # every kind is a source kind: nothing held out
    check("source gain with no held-out pair -> unmeasured, never kept", r["verdict"] == "unmeasured"
          and r["keep"] is None and r["source"]["win"] >= 1 and r["source"]["loss"] == 0, (r["held_out"], r["source"]))
    check("verdict rule direct", G.verdict({"win": 1, "loss": 1, "tie": 0}, {"win": 2, "loss": 0, "tie": 0})
          == "narrow" and G.verdict({"win": 2, "loss": 3, "tie": 0}, {"win": 9, "loss": 0, "tie": 0}) == "overfit")

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
    check("appended, first entry unchanged", [g["verdict"] for g in gens] == ["general", "no_gain"]
          and gens[0]["evidence"] == os.path.relpath(e1, tmp), gens)
    check("evidence holds both answers of every pair", all("a" in p and "b" in p for p in json.load(open(e1))["pairs"]))
    rc, lines = G.show(T, "v3", changes_dir=changes, repo=tmp)
    check("show: judged entry -> 0", rc == 0 and len(lines) == 2, lines)

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

print("selftest_agent_improve_general: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
