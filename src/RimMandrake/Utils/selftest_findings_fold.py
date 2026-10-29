#!/usr/bin/env python3
"""selftest_findings_fold.py - the no-AI findings sorter (findings_fold.py, FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X).

Pure fold() over hand-made ledger events and testq done records, plus run() as a subprocess on temp inputs. Proves:
identical signatures merge (numbers, timestamps, file names and job ids stripped) with count, first and last seen,
and every raw text kept; different failures never merge (other text, other row, other chain, other mod); a row
retires only after 3 passes in a row after its last FAIL (an UNMEASURED breaks the streak) and reopens when it fails
again; an item `validated` with 26 fails and 0 passes is a CONTRADICTION at the top of curation.md; red canaries and
machine-health rows route to the lane item; a repeat of a decided signature merges into that decision with one
idempotent note; a raw text whose done record vanished survives from the previous table; unreadable input (a torn
done record, a torn previous table, a torn ledger line, a torn decisions line) exits 2 and writes nothing.
Mutation-style checks: the same fixtures fail if the digit rule, the row in the signature, or the 3-pass rule is
removed (each is exercised by a case whose answer flips without it).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import findings_fold as FF  # noqa: E402

FAILS = []
RULES = FF.load_rules()
LANE = RULES["lane_item"]


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


_TSN = [0]


def ts(day, hh, mm=0):
    return "2026-10-%02dT%02d:%02d:00Z" % (day, hh, mm)


def fev(name, item, row, text, at, chain="c1", run=None):
    _TSN[0] += 1
    return {"seat": "RUNNER", "event": "finding", "id": item, "type": "UNTRIAGED", "severity": "medium",
            "name": name, "from": run or "%s/run-%d@steve-targeted" % (item, _TSN[0]),
            "why": "%s/%s FAIL on SteveDesktop: %s" % (chain, row, text[:160]), "ts": at}


def rec(job, mod, at, rows, findings=(), item="X"):
    """rows: (chain, row, verdict, detail)."""
    return {"job": {"id": job, "mod": mod, "item": item},
            "result": {"outcome": "DONE", "finished": at, "attempt": job + ".a1",
                       "rows": [{"chain": c, "row": r, "verdict": v, "detail": d} for c, r, v, d in rows]},
            "ingested": {"run": "%s/run-1@steve-targeted" % item, "findings": list(findings), "at": at}}


def fold(events, states, recs, decisions=(), prev=None, now=ts(29, 20)):
    return FF.fold(events, states, recs, list(decisions), prev, RULES, now)


def sig_of(table, name):
    return table["raw"][name]["sig"]


# ------------------------------------------------------------------ 1. identical signatures merge
T1 = "ExpectationFailed: the dig job never finished after %d ticks (dig_result_2026102%dT1%d0000.json, job J20261028T101010Z-a1b2c3)"
evs = [fev("Q_A", "QUARRY_ITEM", "cut_turns_up", T1 % (2500, 7, 1), ts(27, 1)),
       fev("Q_B", "QUARRY_ITEM", "cut_turns_up", T1 % (3100, 8, 2), ts(28, 2)),
       fev("Q_C", "QUARRY_ITEM", "cut_turns_up", T1 % (2501, 9, 3), ts(29, 3))]
t = fold(evs, {"QUARRY_ITEM": "doing"}, [])
s = {sig_of(t, n) for n in ("Q_A", "Q_B", "Q_C")}
check(len(s) == 1, "three runs of one failure, numbers/timestamps/files/job ids apart, share one signature")
row = t["signatures"][s.pop()] if len(s) == 1 else {}
check(row.get("count") == 3, "the merged signature counts 3 (got %s)" % row.get("count"))
check(row.get("first_seen") == ts(27, 1) and row.get("last_seen") == ts(29, 3), "first and last seen kept")
check(sorted(row.get("findings") or []) == ["Q_A", "Q_B", "Q_C"], "every finding name stays listed")
check(all(T1 % a in t["raw"][n]["text"] for n, a in (("Q_A", (2500, 7, 1)), ("Q_B", (3100, 8, 2)))),
      "each raw text is kept verbatim, not the normalised one")
check(t["counts"]["findings"] == 3 and t["counts"]["distinct"] == 1, "counts: 3 findings, 1 distinct")
check(row.get("status") == "NEW", "an undecided signature is NEW for FOUNDRY (got %s)" % row.get("status"))

# ------------------------------------------------------------------ 2. different failures never merge
evs2 = [fev("D_A", "IT", "row_a", "ExpectationFailed: tank filled first", ts(28, 1)),
        fev("D_B", "IT", "row_a", "ExpectationFailed: tank never filled", ts(28, 2)),        # other text
        fev("D_C", "IT", "row_b", "ExpectationFailed: tank filled first", ts(28, 3)),        # other row
        fev("D_D", "IT", "row_a", "ExpectationFailed: tank filled first", ts(28, 4), chain="c2")]  # other chain
recs2 = [rec("J1", "ModA", ts(28, 1), [("c1", "row_a", "FAIL", "ExpectationFailed: tank filled first")], ["D_A"]),
         rec("J5", "ModB", ts(28, 5), [("c1", "row_a", "FAIL", "ExpectationFailed: tank filled first")], ["D_E"])]
evs2.append(fev("D_E", "IT", "row_a", "ExpectationFailed: tank filled first", ts(28, 5)))   # other mod (from the record)
t2 = fold(evs2, {"IT": "doing"}, recs2)
sigs2 = [sig_of(t2, n) for n in ("D_A", "D_B", "D_C", "D_D", "D_E")]
check(len(set(sigs2)) == 5, "other text / row / chain / mod: five signatures, nothing merged (%d)" % len(set(sigs2)))
check(FF.normalise("tank filled at 3", RULES) == FF.normalise("tank filled at 41", RULES),
      "mutation: the digit rule is what merges run numbers")
check(FF.signature("M", "c", "r1", "x", RULES) != FF.signature("M", "c", "r2", "x", RULES),
      "mutation: the row is part of the signature")
check(FF.normalise("tank filled first", RULES) != FF.normalise("tank never filled", RULES),
      "normalising never erases words")
# the full detail of the done record wins over the ledger's 160-char cut, so a difference past char 160 still splits
long_a, long_b = "E: " + "x" * 170 + " alpha", "E: " + "x" * 170 + " beta"
evs2b = [fev("L_A", "IT", "r", long_a, ts(28, 1)), fev("L_B", "IT", "r", long_b, ts(28, 2))]
recs2b = [rec("JLA", "M", ts(28, 1), [("c1", "r", "FAIL", long_a)], ["L_A"]),
          rec("JLB", "M", ts(28, 2), [("c1", "r", "FAIL", long_b)], ["L_B"])]
t2b = fold(evs2b, {"IT": "doing"}, recs2b)
check(sig_of(t2b, "L_A") != sig_of(t2b, "L_B"), "texts equal for 160 chars but different after stay apart")
check(t2b["raw"]["L_A"]["text"] == long_a, "the raw text is the full done-record detail, not the 160-char cut")

# ------------------------------------------------------------------ 3. retire after 3 passes, reopen on a fail
def timeline(verdicts, start_day=26):
    out, names, evs_ = [], [], []
    for k, v in enumerate(verdicts):
        at = ts(start_day + k // 10, k % 10 + 1)
        fnames = []
        if v == "FAIL":
            n = "R_%d" % k
            fnames = [n]
            evs_.append(fev(n, "RET_ITEM", "flaky_row", "ExpectationFailed: boom", at))
        out.append(rec("JR%d" % k, "M", at, [("c1", "flaky_row", v, "ExpectationFailed: boom" if v == "FAIL" else "")],
                       fnames))
    return evs_, out


e3, r3 = timeline(["FAIL", "PASS", "PASS"])
row3 = list(fold(e3, {"RET_ITEM": "doing"}, r3)["signatures"].values())[0]
check(row3["status"] != "RETIRED" and row3["pass_streak"] == 2, "2 passes after the fail: not retired")
e3, r3 = timeline(["FAIL", "PASS", "UNMEASURED", "PASS", "PASS"])
row3 = list(fold(e3, {"RET_ITEM": "doing"}, r3)["signatures"].values())[0]
check(row3["status"] != "RETIRED", "an UNMEASURED run breaks the streak: P U P P is not 3 in a row")
e3, r3 = timeline(["FAIL", "FAIL", "PASS", "PASS", "PASS"])
t3 = fold(e3, {"RET_ITEM": "doing"}, r3)
row3 = list(t3["signatures"].values())[0]
check(row3["status"] == "RETIRED" and row3["retired_at"], "3 passes in a row after the last fail: RETIRED")
check(len(row3.get("retire_proof") or []) == 3, "the retirement carries its 3 passing runs as proof")
check(any(a["kind"] == "retire" and a["item"] == "RET_ITEM" for a in t3["actions"]), "a retire note is written")
e3, r3 = timeline(["FAIL", "PASS", "PASS", "PASS", "FAIL"])
t3 = fold(e3, {"RET_ITEM": "doing"}, r3)
row3 = list(t3["signatures"].values())[0]
check(row3["status"] == "REOPENED" and row3["reopened"] == 1, "a retired row that fails again REOPENS (got %s)"
      % row3["status"])
check(any(a["kind"] == "reopen" for a in t3["actions"]), "a reopen note is written")
check(row3["count"] == 2, "the reopened signature keeps counting from its history")
saved = RULES["retire_after_passes"]
RULES["retire_after_passes"] = 99
e3, r3 = timeline(["FAIL", "PASS", "PASS", "PASS"])
check(list(fold(e3, {"RET_ITEM": "doing"}, r3)["signatures"].values())[0]["status"] != "RETIRED",
      "mutation: the pass count comes from rules (99 needed: not retired)")
RULES["retire_after_passes"] = saved

# ------------------------------------------------------------------ 4. the contradiction (quarry fixture)
e4, r4 = [], []
for k in range(26):
    at = ts(26 + k // 10, k % 10 + 1)
    e4.append(fev("QQ_%d" % k, "QUARRY_DIGGING", "cut_turns_up", "ExpectationFailed: the dig job never finished", at))
    r4.append(rec("JQ%d" % k, "FlowWorks", at, [("dig", "cut_turns_up", "FAIL",
                                                  "ExpectationFailed: the dig job never finished")], ["QQ_%d" % k]))
e4.append(fev("OTHER_1", "OPEN_ITEM", "x", "boom", ts(29, 1)))
t4 = fold(e4, {"QUARRY_DIGGING": "validated", "OPEN_ITEM": "doing"}, r4)
q = [r for r in t4["signatures"].values() if "QUARRY_DIGGING" in r["items"]]
check(len(q) == 1 and q[0]["count"] == 26, "the 26 quarry fails fold into one signature")
check(q and q[0]["status"] == "CONTRADICTION", "an item validated with 26 fails and 0 passes is a CONTRADICTION")
check(t4["counts"]["contradictions"] == 1, "contradictions counted: 1")
md = FF.render_md(t4)
first = [ln for ln in md.splitlines() if ln.startswith("## ")][:1]
check(first and first[0].startswith("## CONTRADICTION"), "CONTRADICTIONS is the first section of curation.md")
check("QUARRY_DIGGING" in md.split("## ", 2)[1], "the quarry item is named in that top section")
check(any(a["kind"] == "contradiction" and a["item"] == "QUARRY_DIGGING" for a in t4["actions"]),
      "a contradiction note goes on the validated item")
t4d = fold(e4, {"QUARRY_DIGGING": "done", "OPEN_ITEM": "doing"}, r4)
check(t4d["counts"]["contradictions"] == 1, "a done item still failing is a contradiction too")
t4o = fold(e4, {"QUARRY_DIGGING": "doing", "OPEN_ITEM": "doing"}, r4)
check(t4o["counts"]["contradictions"] == 0, "the same fails under an open item are no contradiction")

# ------------------------------------------------------------------ 5. routing to Operations' lane item
e5 = [{"seat": "RUNNER", "event": "finding", "id": LANE, "type": "UNTRIAGED", "severity": "high",
       "name": "STEVE_LANE_CANARY_RED_%s" % h, "from": "%s/run-%d@steve-lane" % (LANE, k),
       "why": "SteveDesktop lane paused: the vanilla canary was red after a load (testq J20261029T1%d0000Z-%s.a1: "
              "the vanilla canary was red: no mod row ran); it admits nothing" % (k, h.lower()), "ts": ts(29, k)}
      for k, h in ((1, "AAAAAA"), (2, "BBBBBB"))]
e5.append(fev("PIL_1", "SOME_ITEM", "diptych", "HARNESS: diptych could not be composed (No module named 'PIL')",
              ts(29, 3)))
t5 = fold(e5, {LANE: "doing", "SOME_ITEM": "done"}, [])
lane = [r for r in t5["signatures"].values() if LANE in r["items"]]
check(len(lane) == 1 and lane[0]["count"] == 2 and lane[0]["status"] == "ROUTED",
      "two red canaries fold to one ROUTED signature")
pil = t5["signatures"][sig_of(t5, "PIL_1")]
check(pil["status"] == "ROUTED", "a machine-health row (no PIL on the runner) routes, even under a done item")
check(t5["counts"]["routed"] == 2, "routed counted: 2")
check(all(a["item"] == LANE for a in t5["actions"] if a["kind"] == "route") and
      sum(1 for a in t5["actions"] if a["kind"] == "route") == 2, "each routed signature notes the lane item")

# ------------------------------------------------------------------ 6. a repeat of a decided signature merges
e6 = [fev("M_1", "HOST", "r", "boom", ts(27, 1)), fev("M_2", "HOST", "r", "boom", ts(28, 1)),
      {"seat": "FOUNDRY", "event": "spawn", "name": "FIX_BOOM_ITEM", "from": "M_1", "for": "FOUNDRY", "ts": ts(27, 5)}]
t6 = fold(e6, {"HOST": "doing", "FIX_BOOM_ITEM": "ready"}, [])
r6 = t6["signatures"][sig_of(t6, "M_2")]
check(r6["status"] == "MERGED" and r6["decision"]["into"] == "FIX_BOOM_ITEM",
      "a finding spawned into an item is that signature's decision; its repeat MERGES into it")
m6 = [a for a in t6["actions"] if a["kind"] == "merge"]
check(len(m6) == 1 and m6[0]["item"] == "FIX_BOOM_ITEM" and "count 2" in m6[0]["text"],
      "one merge note on the decided item, with the count")
check("M_2" in m6[0]["needle"], "the merge note's needle names the newest finding, so a rerun writes nothing new")
dec = [{"sig": sig_of(t, "Q_A"), "as": "memory", "into": "skills/x/SKILL.md:12", "by": "FOUNDRY", "ts": ts(28, 1),
        "why": "general"}]
t6b = fold(evs, {"QUARRY_ITEM": "doing"}, [], decisions=dec)
check(t6b["signatures"][sig_of(t6b, "Q_A")]["status"] == "MERGED", "a decisions-file line decides a signature")
dec.append({"sig": sig_of(t, "Q_A"), "as": "undo", "by": "FOUNDRY", "ts": ts(28, 2), "why": "wrong"})
t6c = fold(evs, {"QUARRY_ITEM": "doing"}, [], decisions=dec)
check(t6c["signatures"][sig_of(t6c, "Q_A")]["status"] == "NEW", "a later undo returns it to NEW")
t6d = fold(e6, {"HOST": "doing", "FIX_BOOM_ITEM": "done"}, [])
check(t6d["signatures"][sig_of(t6d, "M_2")]["status"] == "CONTRADICTION",
      "a decision item that is done while its signature still fails is a contradiction")

# ------------------------------------------------------------------ 7. raw texts survive from the previous table
prev = {"schema": FF.SCHEMA, "raw": {"GONE_1": {"sig": "deadbeef00", "text": "the only copy", "ts": ts(20, 1),
                                                "why": "w", "item": "OLD"}}, "signatures": {}}
t7 = fold(evs, {"QUARRY_ITEM": "doing"}, [], prev=prev)
check(t7["raw"].get("GONE_1", {}).get("text") == "the only copy", "a raw text from the previous table is never lost")

# ------------------------------------------------------------------ 8. run(): fail closed on unreadable input
tmp = tempfile.mkdtemp(prefix="ffold_")
try:
    qd, out, led = (os.path.join(tmp, n) for n in ("q", "out", "ledger"))
    os.makedirs(os.path.join(qd, "done"))
    os.makedirs(os.path.join(led, "events"))
    events_file = os.path.join(led, "events.jsonl")
    with open(events_file, "w") as f:
        f.write("")
    with open(os.path.join(led, "events", "RUNNER.jsonl"), "w") as f:
        for e in evs:
            f.write(json.dumps(e) + "\n")
    decf = os.path.join(tmp, "decisions.jsonl")
    env = dict(os.environ, TESTQ_QUEUE=qd, FINDINGS_FOLD_OUT=out, RIMFLOW_LEDGER=events_file,
               FINDINGS_FOLD_DECISIONS=decf)

    def run(*extra):
        return subprocess.run([sys.executable, os.path.join(HERE, "findings_fold.py"), "run", "--no-notes"] +
                              list(extra), env=env, capture_output=True, text=True, timeout=120)
    r = run()
    check(r.returncode == 0 and os.path.isfile(os.path.join(out, "standing.json")),
          "a clean run exits 0 and writes standing.json (%d: %s)" % (r.returncode, (r.stderr or r.stdout)[-200:]))
    good = open(os.path.join(out, "standing.json")).read()
    check(os.path.isfile(os.path.join(out, "curation.md")), "and curation.md")

    def closed(label, setup, undo, expect=None):
        setup()
        r = run()
        now = open(os.path.join(out, "standing.json")).read()
        check(r.returncode == 2 and now == (good if expect is None else expect) and "UNMEASURED" in (r.stdout + r.stderr),
              "%s: exit 2, UNMEASURED said, the table untouched (got %d)" % (label, r.returncode))
        undo()
    bad = os.path.join(qd, "done", "J_BAD.json")
    closed("a torn done record", lambda: open(bad, "w").write("{not json"), lambda: os.remove(bad))
    st = os.path.join(out, "standing.json")
    closed("a torn previous table",
           lambda: open(st, "w").write(good[:40]), lambda: open(st, "w").write(good), expect=good[:40])
    sh = os.path.join(led, "events", "RUNNER.jsonl")
    keep = open(sh).read()
    closed("a torn ledger line", lambda: open(sh, "a").write('{"event": "finding", "na\n'),
           lambda: open(sh, "w").write(keep))
    closed("a torn decisions line", lambda: open(decf, "w").write("{oops\n"), lambda: os.remove(decf))
    qd2 = env["TESTQ_QUEUE"]
    env["TESTQ_QUEUE"] = os.path.join(tmp, "no_such_queue")
    closed("a missing done directory", lambda: None, lambda: None)
    env["TESTQ_QUEUE"] = qd2
    r = run()
    check(r.returncode == 0, "after the inputs are mended the run is clean again")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ------------------------------------------------------------------ 9. the conservation invariant
check(t4["counts"]["findings"] == sum(r["count"] for r in t4["signatures"].values()) == 27,
      "every in-scope finding is in exactly one signature (27 = sum of counts)")
check(sum(t4["counts"]["by_status"].values()) == t4["counts"]["distinct"], "statuses sum to the distinct count")

print("ALL PASS" if not FAILS else "%d FAILED" % len(FAILS))
sys.exit(1 if FAILS else 0)
