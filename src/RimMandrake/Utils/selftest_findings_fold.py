#!/usr/bin/env python3
"""selftest_findings_fold.py - the no-AI findings sorter (findings_fold.py, FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X).

Pure fold() over hand-made ledger events and testq done records, plus run() as a subprocess on temp inputs and the
live note path on a throwaway ledger. Proves: identical failures merge when only volatile identifiers differ
(timestamps, job ids, whole UUIDs, shas, thing ids, run numbers) with count, first and last seen and every raw text
kept; different failures never merge (error code, file name, count, measured value, row, chain, mod; review F1, F11,
F14); retirement and reopening are per signature, need 3 passes in a row, and any blind run (an UNMEASURED row or an
INVALID/INTERRUPTED record whose selector covers the row) breaks the streak (F4, F5, F9); a retire decision without
proof is AWAITING_PROOF; a failing row under a done/validated item is a CONTRADICTION even when routed (F6); carried
and record-less findings keep their signature, count and decision (F2, F3); unreadable input, including a
structurally wrong record, exits 2 and writes nothing (F12); runs on one folder are serialised with unique temp files
(F7); live, the ledger read and the notes share one hold of the clone lock (F8); an unchanged rerun writes no byte
(F10); the timer's ExecStart does not mask exit 2 (F13); the real note path writes each note once (F14).
Every review check above fails against the pre-review module (3f4d6647dd).
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
# only explicitly volatile identifiers differ between the three runs: a timestamped file name, a job id, a UUID, a git
# sha, a thing id and the run number. The tick count (an assertion value) is the same in all three.
T1 = ("ExpectationFailed: the dig job never finished after 2500 ticks (dig_result_2026102%dT1%d0000.json, job "
      "J2026102%dT101010Z-a1b2c%d.a2, request %s, built at %s, pawn Human%d, QUARRY_ITEM/run-%d@steve-targeted)")
V1 = {"Q_A": (7, 1, 7, 1, "3f2a9c1e-abcd-4e5f-8a9b-0123456789ab", "4c0b13067d9e", 118501, 3),
      "Q_B": (8, 2, 8, 2, "9d8e7f6a-beef-4a1b-9c2d-ba9876543210", "3f4d6647dd", 476708, 14),
      "Q_C": (9, 3, 9, 3, "0a1b2c3d-cafe-4d5e-8f90-a1b2c3d4e5f6", "c02cf591b0aa", 99999, 15)}
evs = [fev(n, "QUARRY_ITEM", "cut_turns_up", T1 % V1[n], ts(27 + k, k + 1)) for k, n in enumerate(sorted(V1))]
recs1 = [rec("JQ1%d" % k, "FlowWorks", ts(27 + k, k + 1), [("c1", "cut_turns_up", "FAIL", T1 % V1[n])], [n])
         for k, n in enumerate(sorted(V1))]
t = fold(evs, {"QUARRY_ITEM": "doing"}, recs1)
s = {sig_of(t, n) for n in ("Q_A", "Q_B", "Q_C")}
check(len(s) == 1, "three runs of one failure, timestamps/job ids/UUIDs/shas/thing ids/run numbers apart, share one "
                   "signature")
row = t["signatures"][s.pop()] if len(s) == 1 else {}
check(row.get("count") == 3, "the merged signature counts 3 (got %s)" % row.get("count"))
check(row.get("first_seen") == ts(27, 1) and row.get("last_seen") == ts(29, 3), "first and last seen kept")
check(sorted(row.get("findings") or []) == ["Q_A", "Q_B", "Q_C"], "every finding name stays listed")
check(all(T1 % V1[n] == t["raw"][n]["text"] for n in ("Q_A", "Q_B")),
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
check(FF.normalise("dig_result_20261027T101010.json at 2026-10-27T10:10:10Z", RULES) ==
      FF.normalise("dig_result_20261028T121212.json at 2026-10-28 12:12", RULES),
      "mutation: the timestamp rules are what merge run times (file stem kept)")
# review finding 1: error codes, measured values and file identity are the failure, never volatile
for a_, b_ in (("HTTP 401 from parser.py", "HTTP 500 from renderer.py"), ("HTTP 401 from parser.py",
               "HTTP 500 from parser.py"), ("HTTP 401 from parser.py", "HTTP 401 from renderer.py"),
               ("the dig job never finished after 2500 ticks", "the dig job never finished after 3100 ticks"),
               ("{'RM_Dehydration': 0.117750995}", "{'RM_Dehydration': 0.118501234}"),
               ("expected 3 got 4", "expected 3 got 5")):
    check(FF.normalise(a_, RULES) != FF.normalise(b_, RULES) and
          FF.signature("M", "c", "r", a_, RULES) != FF.signature("M", "c", "r", b_, RULES),
          "F1: %r and %r are two signatures" % (a_, b_))
# review finding 11: a whole UUID is one volatile id; its letter-only groups never split a repeat
check(FF.normalise("request 3f2a9c1e-abcd-4e5f-8a9b-0123456789ab failed", RULES) ==
      FF.normalise("request 9d8e7f6a-beef-4a1b-9c2d-ba9876543210 failed", RULES) ==
      "request <uuid> failed", "F11: two UUIDs that differ in letter-only groups normalise alike, to <uuid>")
# review finding 14: the chain alone splits (same mod from records, same row and text, other chain)
recs2c = [rec("JC1", "ModA", ts(28, 1), [("c1", "row_a", "FAIL", "ExpectationFailed: tank filled first")], ["C_1"]),
          rec("JC2", "ModA", ts(28, 2), [("c2", "row_a", "FAIL", "ExpectationFailed: tank filled first")], ["C_2"])]
t2c = fold([fev("C_1", "IT", "row_a", "ExpectationFailed: tank filled first", ts(28, 1)),
            fev("C_2", "IT", "row_a", "ExpectationFailed: tank filled first", ts(28, 2), chain="c2")],
           {"IT": "doing"}, recs2c)
check(t2c["raw"]["C_1"]["mod"] == t2c["raw"]["C_2"]["mod"] == "ModA" and sig_of(t2c, "C_1") != sig_of(t2c, "C_2"),
      "F14: same mod, row and text on two chains: two signatures (the chain dimension alone)")
check(FF.signature("M", "c1", "r", "x", RULES) != FF.signature("M", "c2", "r", "x", RULES),
      "mutation: the chain is part of the signature")
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

# review finding 4: FAIL A -> PASS x3 -> FAIL B on one row: A stays retired, B is new (not a reopening of A)
r4a = [rec("JA0", "M", ts(26, 1), [("c1", "flaky_row", "FAIL", "ExpectationFailed: A")], ["A_0"])] + \
      [rec("JA%d" % k, "M", ts(26, 1 + k), [("c1", "flaky_row", "PASS", "")]) for k in (1, 2, 3)] + \
      [rec("JB4", "M", ts(26, 5), [("c1", "flaky_row", "FAIL", "ExpectationFailed: B")], ["B_4"])]
t4a = fold([fev("A_0", "RET_ITEM", "flaky_row", "ExpectationFailed: A", ts(26, 1)),
            fev("B_4", "RET_ITEM", "flaky_row", "ExpectationFailed: B", ts(26, 5))], {"RET_ITEM": "doing"}, r4a)
sa, sb = t4a["signatures"][sig_of(t4a, "A_0")], t4a["signatures"][sig_of(t4a, "B_4")]
check(sa["status"] == "RETIRED" and sb["status"] == "NEW" and sb["reopened"] == 0,
      "F4: another signature's FAIL neither un-retires A nor makes new B a reopening (A %s, B %s)"
      % (sa["status"], sb["status"]))
check(not any(a["kind"] == "reopen" for a in t4a["actions"]), "F4: no reopen note")
r4b = r4a[:4] + [rec("JA5", "M", ts(26, 6), [("c1", "flaky_row", "FAIL", "ExpectationFailed: A")], ["A_5"])]
t4b = fold([fev("A_0", "RET_ITEM", "flaky_row", "ExpectationFailed: A", ts(26, 1)),
            fev("A_5", "RET_ITEM", "flaky_row", "ExpectationFailed: A", ts(26, 6))], {"RET_ITEM": "doing"}, r4b)
check(t4b["signatures"][sig_of(t4b, "A_5")]["status"] == "REOPENED", "F4: A failing again after retiring REOPENS A")
r4c = [r4a[0], r4a[1], rec("JX2", "M", ts(26, 3), [("c1", "flaky_row", "FAIL", "ExpectationFailed: B")], ["B_2"]),
       r4a[2], r4a[3]]
t4c = fold([fev("A_0", "RET_ITEM", "flaky_row", "ExpectationFailed: A", ts(26, 1))], {"RET_ITEM": "doing"}, r4c)
check(t4c["signatures"][sig_of(t4c, "A_0")]["status"] != "RETIRED",
      "F4: the row failing (another way) mid-streak breaks the streak: P F(B) P P does not retire A")

# review finding 5: a retire decision alone never retires
e5f, r5f = timeline(["FAIL", "FAIL"])
dec5 = [{"sig": sig_of(fold(e5f, {"RET_ITEM": "doing"}, r5f), "R_0"), "as": "retire", "into": None, "by": "FOUNDRY",
         "ts": ts(29, 23), "why": "fixed, I think"}]
t5f = fold(e5f, {"RET_ITEM": "doing"}, r5f, decisions=dec5)
r5r = t5f["signatures"][dec5[0]["sig"]]
check(r5r["status"] == "AWAITING_PROOF" and not any(a["kind"] == "retire" for a in t5f["actions"]),
      "F5: a retire decision with 0 passes and a latest FAIL is not RETIRED (got %s), no retire note" % r5r["status"])
t5g = fold(e5f, {"RET_ITEM": "done"}, r5f, decisions=dec5)
check(t5g["signatures"][dec5[0]["sig"]]["contradicts"] == ["RET_ITEM"],
      "F5/F6: a retire decision never hides a still-failing done item")
e5h, r5h = timeline(["FAIL", "PASS", "PASS", "PASS"])
dec5h = [dict(dec5[0], sig=sig_of(fold(e5h, {"RET_ITEM": "doing"}, r5h), "R_0"))]
check(fold(e5h, {"RET_ITEM": "doing"}, r5h, decisions=dec5h)["signatures"][dec5h[0]["sig"]]["status"] == "RETIRED",
      "F5: with its 3 passes it retires")

# review finding 9: a run that measured nothing (not DONE) breaks the streak, by its rows or by its selector
def blind(job, at, rows=None, selector=None, outcome="INVALID", mod="M"):
    r = rec(job, mod, at, rows or [])
    r["result"]["outcome"] = outcome
    r["job"]["selector"] = selector or {"chains": ["c1"]}
    if rows is None:
        del r["result"]["rows"]
    return r


for label, b9 in (("an INVALID record holding the row as PASS", blind("JB", ts(26, 3), [("c1", "flaky_row", "PASS", "")])),
                  ("an INVALID record with no rows, selector chains [c1]", blind("JB", ts(26, 3))),
                  ("an INTERRUPTED record, selector full", blind("JB", ts(26, 3), selector={"full": True},
                                                                outcome="INTERRUPTED")),
                  ("an INVALID record, selector rows [flaky]", blind("JB", ts(26, 3),
                                                                     selector={"chains": ["c1"], "rows": ["flaky"]}))):
    e9, r9 = timeline(["FAIL", "PASS", "PASS", "PASS"])
    r9 = r9[:2] + [b9] + r9[2:]
    t9 = fold(e9, {"RET_ITEM": "doing"}, r9)
    check(t9["signatures"][sig_of(t9, "R_0")]["status"] != "RETIRED",
          "F9: F P [%s] P P does not retire" % label)
e9, r9 = timeline(["FAIL", "PASS", "PASS", "PASS"])
for label, b9 in (("another chain", blind("JB", ts(26, 3), selector={"chains": ["c9"]})),
                  ("another mod", blind("JB", ts(26, 3), mod="Other")),
                  ("another row prefix", blind("JB", ts(26, 3), selector={"chains": ["c1"], "rows": ["T12"]}))):
    t9 = fold(e9, {"RET_ITEM": "doing"}, r9[:2] + [b9] + r9[2:])
    check(t9["signatures"][sig_of(t9, "R_0")]["status"] == "RETIRED", "F9: a blind run of %s does not touch it" % label)

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
# review finding 6: routing never hides a contradiction; the done item is flagged and noted too
check(pil["contradicts"] == ["SOME_ITEM"] and t5["counts"]["contradictions"] == 1,
      "F6: the routed PIL row under a done item still CONTRADICTS it (got %s)" % pil["contradicts"])
check(any(a["kind"] == "contradiction" and a["item"] == "SOME_ITEM" for a in t5["actions"]),
      "F6: and a contradiction note goes on the done item, beside the route note")
check("SOME_ITEM" in FF.render_md(t5).split("## ", 2)[1], "F6: and it heads curation.md")
check(all(a["item"] == LANE for a in t5["actions"] if a["kind"] == "route") and
      sum(1 for a in t5["actions"] if a["kind"] == "route") == 2, "each routed signature notes the lane item")

# ------------------------------------------------------------------ 6. a repeat of a decided signature merges
e6 = [fev("M_1", "HOST", "r", "boom", ts(27, 1)), fev("M_2", "HOST", "r", "boom", ts(28, 1)),
      {"seat": "FOUNDRY", "event": "spawn", "name": "FIX_BOOM_ITEM", "from": "M_1", "for": "FOUNDRY", "ts": ts(27, 5)}]
r6s = [rec("JM1", "M", ts(27, 1), [("c1", "r", "FAIL", "boom")], ["M_1"]),
       rec("JM2", "M", ts(28, 1), [("c1", "r", "FAIL", "boom")], ["M_2"])]
t6 = fold(e6, {"HOST": "doing", "FIX_BOOM_ITEM": "ready"}, r6s)
r6 = t6["signatures"][sig_of(t6, "M_2")]
check(r6["status"] == "MERGED" and r6["decision"]["into"] == "FIX_BOOM_ITEM",
      "a finding spawned into an item is that signature's decision; its repeat MERGES into it")
m6 = [a for a in t6["actions"] if a["kind"] == "merge"]
check(len(m6) == 1 and m6[0]["item"] == "FIX_BOOM_ITEM" and "count 2" in m6[0]["text"],
      "one merge note on the decided item, with the count")
check("M_2" in m6[0]["needle"], "the merge note's needle names the newest finding, so a rerun writes nothing new")
dec = [{"sig": sig_of(t, "Q_A"), "as": "memory", "into": "skills/x/SKILL.md:12", "by": "FOUNDRY", "ts": ts(28, 1),
        "why": "general"}]
t6b = fold(evs, {"QUARRY_ITEM": "doing"}, recs1, decisions=dec)
check(t6b["signatures"][sig_of(t6b, "Q_A")]["status"] == "MERGED", "a decisions-file line decides a signature")
dec.append({"sig": sig_of(t, "Q_A"), "as": "undo", "by": "FOUNDRY", "ts": ts(28, 2), "why": "wrong"})
t6c = fold(evs, {"QUARRY_ITEM": "doing"}, recs1, decisions=dec)
check(t6c["signatures"][sig_of(t6c, "Q_A")]["status"] == "NEW", "a later undo returns it to NEW")
t6d = fold(e6, {"HOST": "doing", "FIX_BOOM_ITEM": "done"}, r6s)
check(t6d["signatures"][sig_of(t6d, "M_2")]["status"] == "CONTRADICTION",
      "a decision item that is done while its signature still fails is a contradiction")

# ------------------------------------------------------------------ 7. raw texts survive from the previous table
prev = {"schema": FF.SCHEMA, "raw": {"GONE_1": {"sig": "deadbeef00", "text": "the only copy", "ts": ts(20, 1),
                                                "why": "w", "item": "OLD"}}, "signatures": {}}
t7 = fold(evs, {"QUARRY_ITEM": "doing"}, [], prev=prev)
check(t7["raw"].get("GONE_1", {}).get("text") == "the only copy", "a raw text from the previous table is never lost")
# review finding 3: a carried finding still STANDS: in its signature, counted, contradicting, keeping its decision
prev3 = {"schema": FF.SCHEMA, "raw": {"GONE_2": {"mod": "M", "chain": "c1", "row": "r", "text": "boom",
                                                "ts": ts(27, 1), "why": "c1/r FAIL on SteveDesktop: boom",
                                                "item": "GONE_HOST", "provenance": "record"}}, "signatures": {}}
t7b = fold([fev("M_2", "HOST", "r", "boom", ts(28, 1))], {"HOST": "doing", "GONE_HOST": "done"},
           [r6s[1]], prev=prev3)
g = [r for r in t7b["signatures"].values() if "GONE_2" in r["findings"]]
check(len(g) == 1 and g[0]["count"] == 2 and "M_2" in g[0]["findings"] and g[0]["carried"] == 1,
      "F3: a carried finding stands in its signature beside its live repeat (count 2)")
check(g and g[0]["contradicts"] == ["GONE_HOST"], "F3: its done host is still contradicted")
check(t7b["counts"]["findings"] == 2 and t7b["counts"]["raw_carried"] == 1 and
      sum(r["count"] for r in t7b["signatures"].values()) == 2, "F3: conservation counts the carried finding")
# review finding 2: an event whose done record is gone keeps the previous table's detail, mod and signature
prev2 = {"schema": FF.SCHEMA, "raw": {"M_2": dict(t6["raw"]["M_2"])}, "signatures": {}}
t7c = fold(e6, {"HOST": "doing", "FIX_BOOM_ITEM": "ready"}, [r6s[0]], prev=prev2)
check(t7c["raw"]["M_2"]["mod"] == "M" and t7c["raw"]["M_2"]["provenance"] == "prev" and
      sig_of(t7c, "M_2") == sig_of(t6, "M_2"), "F2: a lost record keeps its mod, detail and signature from prev")
check(t7c["signatures"][sig_of(t7c, "M_2")]["status"] == "MERGED", "F2: and so keeps its decision (MERGED)")
t7d = fold([fev("U_1", "IT1", "r", "boom", ts(28, 1)), fev("U_2", "IT2", "r", "boom", ts(28, 2))],
           {"IT1": "doing", "IT2": "doing"}, [])
check(sig_of(t7d, "U_1") != sig_of(t7d, "U_2") and t7d["counts"]["unresolved"] == 2,
      "F2: two unresolved findings (mod unknown) never merge, however alike")

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
    # review finding 12: a structurally wrong record is unreadable, not silently skipped
    base = rec("JV", "M", ts(28, 1), [("c1", "r", "PASS", "")])
    for label, body in (("an empty-object done record", {}),
                        ("a record with no job mod", dict(base, job={"id": "JV"})),
                        ("a record whose row verdict is not a verdict",
                         dict(base, result=dict(base["result"], rows=[{"row": "r", "verdict": "MAYBE"}]))),
                        ("a record with no finish time", dict(base, result=dict(base["result"], finished="soon"))),
                        ("a DONE record with no rows", dict(base, result={"outcome": "DONE", "finished": ts(28, 1)}))):
        closed("F12: " + label, lambda: open(bad, "w").write(json.dumps(body)), lambda: os.remove(bad))

    # review finding 10: an unchanged rerun writes nothing (both files byte-identical, same mtime)
    st_m, cu = os.stat(st).st_mtime_ns, open(os.path.join(out, "curation.md")).read()
    r = run()
    check(r.returncode == 0 and "unchanged" in r.stdout and open(st).read() == good and
          os.stat(st).st_mtime_ns == st_m and open(os.path.join(out, "curation.md")).read() == cu,
          "F10: a rerun over the same inputs writes nothing (%d: %s)" % (r.returncode, r.stdout[-160:]))

    # review finding 7: one run at a time per output folder, unique temp files
    def add_finding(n):
        with open(sh, "a") as f:
            f.write(json.dumps(fev(n, "QUARRY_ITEM", "other_row", "ExpectationFailed: %s" % n, ts(29, 5))) + "\n")
    add_finding("LOCK_1")
    import fcntl
    with open(os.path.join(out, ".findings_fold.lock"), "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        env["FINDINGS_FOLD_LOCK_WAIT_S"] = "1"
        r = run()
        env.pop("FINDINGS_FOLD_LOCK_WAIT_S")
        fcntl.flock(lk, fcntl.LOCK_UN)
    check(r.returncode == 2 and "UNMEASURED" in r.stdout and open(st).read() == good,
          "F7: while another run holds the folder, a run waits, then exits 2 and writes nothing (%d)" % r.returncode)
    os.mkdir(st + ".tmp")                          # the old fixed temp name, taken
    r = run()
    check(r.returncode == 0 and "LOCK_1" in open(st).read(),
          "F7: temp files are unique per run (a taken standing.json.tmp does not stop it: %d %s)"
          % (r.returncode, (r.stderr or r.stdout)[-160:]))
    os.rmdir(st + ".tmp")
    for k in range(6):
        add_finding("PAR_%d" % k)
    procs = [subprocess.Popen([sys.executable, os.path.join(HERE, "findings_fold.py"), "run", "--no-notes"], env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) for _ in range(6)]
    outs = [(p_.wait(timeout=120), p_.stdout.read()) for p_ in procs]
    final = json.load(open(st))
    check(all(rc == 0 for rc, _ in outs) and all("PAR_%d" % k in final["raw"] for k in range(6)) and
          not [n for n in os.listdir(out) if n.endswith(".tmp")],
          "F7: 6 concurrent runs all succeed, the table holds every finding, no temp file left (%s)"
          % [rc for rc, _ in outs])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ------------------------------------------------------------------ 8b. the live path (review findings 8, 13, 14)
sys.path.insert(0, os.path.join(HERE, "testq"))
import contextlib  # noqa: E402
import ingest as I  # noqa: E402
CLI = os.path.join(FF.RIMFLOW, "cli.py")
REAL_SHARD = os.path.join(FF.REPO, "infrastructure", "state", "ledger", "events", "RUNNER.jsonl")
real_before = os.path.getsize(REAL_SHARD) if os.path.exists(REAL_SHARD) else -1
tmp = tempfile.mkdtemp(prefix="ffold_live_")
try:
    qd, out, led, items = (os.path.join(tmp, n) for n in ("q", "out", "ledger", "items"))
    os.makedirs(os.path.join(qd, "done"))
    os.makedirs(os.path.join(led, "events"))
    os.makedirs(items)
    events_file = os.path.join(led, "events.jsonl")
    open(events_file, "w").close()
    for r_ in recs1:
        with open(os.path.join(qd, "done", r_["job"]["id"] + ".json"), "w") as f:
            json.dump(r_, f)
    lenv = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "CLAUDE_PROJECT_DIR")}
    lenv.update(TESTQ_QUEUE=qd, FINDINGS_FOLD_OUT=out, RIMFLOW_LEDGER=events_file, RIMFLOW_ITEMS=items,
                FINDINGS_FOLD_DECISIONS=os.path.join(tmp, "decisions.jsonl"), FINDINGS_FOLD_PUSH="0",
                FINDINGS_FOLD_RULES=os.path.join(tmp, "rules.json"))
    live_rules = json.load(open(FF.RULES_PATH))
    live_rules["live_notes"] = True
    json.dump(live_rules, open(lenv["FINDINGS_FOLD_RULES"], "w"))
    filed = [subprocess.run([sys.executable, CLI, "file", it, "--for", "BENCH", "--title", "t", "--seat", "BENCH"],
                            env=lenv, capture_output=True, text=True, timeout=120).returncode
             for it in ("QUARRY_CUT_FIX_IT", "SOME_ITEM_FIX_IT", LANE)]
    check(filed == [0, 0, 0], "live fixture: items filed in a throwaway ledger (%s)" % filed)
    shard = os.path.join(led, "events", "RUNNER.jsonl")
    with open(shard, "a") as f:
        for e in evs + [fev("PIL_9", "QUARRY_ITEM", "diptych", "HARNESS: No module named 'PIL'", ts(29, 4))]:
            f.write(json.dumps(dict(e, id="QUARRY_CUT_FIX_IT")) + "\n")   # an item name the cli accepts
    with open(lenv["FINDINGS_FOLD_DECISIONS"], "w") as f:
        f.write(json.dumps({"sig": sig_of(t, "Q_A"), "as": "work", "into": "SOME_ITEM_FIX_IT", "by": "FOUNDRY",
                            "ts": ts(27, 5), "why": "fix it"}) + "\n")

    def lrun():
        return subprocess.run([sys.executable, os.path.join(HERE, "findings_fold.py"), "run"], env=lenv,
                              capture_output=True, text=True, timeout=300)

    def notes():
        return [json.loads(x) for x in open(shard) if '"note"' in x and "findings_fold" in x]
    r1 = lrun()
    n1, sh1 = notes(), open(shard).read()
    kinds = sorted(n_["text"].split()[2] for n_ in n1)
    check(r1.returncode == 0 and kinds == ["merge", "route"] and
          {n_["id"] for n_ in n1} == {"SOME_ITEM_FIX_IT", LANE} and all(n_.get("seat") == "RUNNER" for n_ in n1),
          "F14: the real note path writes one merge note on the decided item and one route note on the lane item "
          "(%d %s %s)" % (r1.returncode, kinds, (r1.stdout + r1.stderr)[-300:]))
    std1 = open(os.path.join(out, "standing.json")).read()
    r2 = lrun()
    check(r2.returncode == 0 and open(shard).read() == sh1 and open(os.path.join(out, "standing.json")).read() == std1
          and "unchanged" in r2.stdout,
          "F14/F10: a second live run writes no ledger line and no table byte (%d %s)" % (r2.returncode, r2.stdout[-200:]))
    check((os.path.getsize(REAL_SHARD) if os.path.exists(REAL_SHARD) else -1) == real_before,
          "the real RUNNER shard was never touched")

    # review finding 8: live, the ledger is read and the notes written under ONE hold of the clone lock
    orig_lock, orig_read, orig_apply = I.repo_lock, FF.read_ledger, FF.apply_notes
    hold, seen = [0, None], {}

    @contextlib.contextmanager
    def counting(wait_s=0):
        outer = not I._HELD
        with orig_lock(wait_s) as got:
            if outer and got:
                hold[0] += 1
                hold[1] = hold[0]
            try:
                yield got
            finally:
                if outer:
                    hold[1] = None

    def spy_read():
        seen["read"] = hold[1]
        return orig_read()

    def spy_apply(actions, push):
        seen["apply"] = hold[1]
        return 0, [], None
    saved_env = {k: os.environ.get(k) for k in lenv}
    os.environ.update(lenv)
    with open(shard, "a") as f:
        f.write(json.dumps(fev("PIL_10", "QUARRY_CUT_FIX_IT", "diptych", "HARNESS: No module named 'PIL' again",
                               ts(29, 6))) + "\n")
    I.repo_lock, FF.read_ledger, FF.apply_notes = counting, spy_read, spy_apply
    try:
        FF.main(["run"])
    finally:
        I.repo_lock, FF.read_ledger, FF.apply_notes = orig_lock, orig_read, orig_apply
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check(seen.get("read") is not None and seen.get("read") == seen.get("apply"),
          "F8: live, the ledger snapshot and its notes share one hold of the clone lock (%s)" % seen)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# review finding 13: the timer does not mask the fold's exit
sys.path.insert(0, os.path.join(HERE, "testq"))
import testq as TQ  # noqa: E402
tick = TQ.UNITS["testq-tick.service"]
fl = [ln for ln in tick.splitlines() if "findings_fold.py run" in ln]
check(len(fl) == 1 and fl[0].startswith("ExecStart=/"), "F13: the fold's ExecStart has no '-': its exit 2 fails the "
                                                         "unit (%s)" % fl)

# ------------------------------------------------------------------ 9. the conservation invariant
check(t4["counts"]["findings"] == sum(r["count"] for r in t4["signatures"].values()) == 27,
      "every in-scope finding is in exactly one signature (27 = sum of counts)")
check(sum(t4["counts"]["by_status"].values()) == t4["counts"]["distinct"], "statuses sum to the distinct count")

print("ALL PASS" if not FAILS else "%d FAILED" % len(FAILS))
sys.exit(1 if FAILS else 0)
