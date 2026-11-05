#!/usr/bin/env python3
"""Selftest: the Test Pilot's SURPRISE BOOK (surprise_book.py, SURPRISE_BOOK_BUILD_RETIRE_THE_BORING).

Each case writes a throwaway book in a temp dir (RM_SURPRISE_BOOK) and checks, on both sides of the threshold:
retire after N non-bug outcomes over enough sittings; union-merge duplicates not inflating a run; context-scoping (retired under the rot is still surprising in
the desert, and a wider context inherits a narrower one's retirement, never the reverse); revive at once on a real bug
and the stricter run after it; a compatible real bug beating a retirement; the per-sitting sample (its pick and
quota); settle by filing id with administrative drops abandoned; roster kinds only, an off-roster def contradicting a
retirement and an uncertain def never explaining; settle from item states; explain-away against the real roster
(an RM_TheRot creature read from BiomeDef + patches); the audit lines agreeing with the fold; the shipped book clean.

    python3 src/RimMandrake/rimflow/selftest_surprise_book.py
"""
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from rimflow import surprise_book as B          # noqa: E402

PASS, FAIL = [], []
RULES = B.load_rules()
N, M, K = RULES["retire_after"], RULES["retire_min_sittings"], RULES["retire_again_after_revive"]
ROT, DESERT = "biome=RM_TheRot", "biome=RM_BlueDesert"
KIND = "mushrooms_everywhere"


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    if not cond:
        print("FAIL %s %s" % (name, detail))


def fresh():
    d = tempfile.mkdtemp(prefix="surprise_book_")
    path = os.path.join(d, "book.jsonl")
    os.environ["RM_SURPRISE_BOOK"] = path
    return path


def tick():
    tick.n += 1
    return "2026-11-04T00:%02d:%02dZ" % divmod(tick.n, 60)


tick.n = 0


def rec(outcome, ctx=ROT, sitting="A@1", kind=KIND, **kw):
    kw.setdefault("evidence", "jawa/vitals letter: test fact %d" % tick.n)
    return B.record(kind, ctx, sitting, outcome, ts=tick(), **kw)


def verdict(ctx=ROT, kind=KIND):
    return B.lookup(kind, ctx)["verdict"]


# 1 retire: N-1 explained stays surprising; the Nth over M sittings retires and writes one retire line with evidence
assert N >= 2 and M >= 2 and K > N, "rules changed shape: re-think these cases"
fresh()
for i in range(N - 1):
    rec("explained", sitting="S%d@1" % (i % M))
ok("below_threshold_stays_surprising", verdict() == "SURPRISING", verdict())
lines = rec("explained", sitting="S%d@1" % ((N - 1) % M))
ok("nth_outcome_retires", verdict() == "EXPECTED", verdict())
ok("retire_line_written", [w["event"] for w in lines] == ["outcome", "retire"], lines)
ok("retire_line_has_evidence", len(lines[-1]["evidence"]) == N and all(e["evidence"] for e in lines[-1]["evidence"]))

# 2 one sitting alone never retires, however many explanations it writes
fresh()
for _ in range(N + 2):
    rec("explained", sitting="ONLY@1")
ok("one_sitting_never_retires", verdict() == "SURPRISING", verdict())

# 3 a filed (neutral) line neither counts nor breaks the run
fresh()
rec("explained", sitting="A@1")
rec("filed", sitting="A@1", item="SOME_ITEM_FIX_IT", evidence="")
for i in range(N - 1):
    rec("not_a_bug", sitting="B%d@1" % i)
ok("filed_is_neutral", verdict() == "EXPECTED", verdict())

# 4 context-scoping: retired in the rot, still surprising in the desert; a wider context inherits, a narrower not
ok("other_biome_still_new", verdict(DESERT) == "NEW", verdict(DESERT))
ok("wider_context_inherits", verdict(ROT + ";test=fire") == "EXPECTED", verdict(ROT + ";test=fire"))
fresh()
for i in range(N):
    rec("explained", ctx=ROT + ";test=fire", sitting="T%d@1" % i)
ok("narrow_retire_not_broad", verdict(ROT) == "NEW" and verdict(ROT + ";test=fire") == "EXPECTED")
ok("other_kind_untouched", verdict(kind="dead_animals_no_cause") == "NEW")
try:
    B.record(KIND, [], "A@1", "explained", evidence="no context at all")
    ok("empty_context_refused", False)
except B.BookError:
    ok("empty_context_refused", True)

# 5 revive: a real bug on a retired key revives it at once, with a revive line; then it needs K, not N
fresh()
for i in range(N):
    rec("explained", sitting="R%d@1" % i)
lines = rec("real_bug", sitting="R9@1", item="ROT_MUSHROOMS_FIX_SPREAD", evidence="item ROT_MUSHROOMS_FIX_SPREAD ended done",
            cause="fix_commit: 1a2b3c4d5e stops RM_Plant_Mushroom spreading onto every tile")
ok("real_bug_revives", verdict() == "SURPRISING", verdict())
ok("revive_line_written", [w["event"] for w in lines] == ["outcome", "revive"], lines)
for i in range(K - 1):
    rec("explained", sitting="P%d@1" % i)
ok("after_revive_needs_K", verdict() == "SURPRISING", verdict())
rec("explained", sitting="P%d@1" % K)
ok("after_revive_K_retires", verdict() == "EXPECTED", verdict())

# 6 a real bug in any COMPATIBLE context (no condition disagrees) beats a retirement; a conflicting one does not
fresh()
for i in range(N):
    rec("explained", sitting="W%d@1" % i)
rec("real_bug", ctx=ROT + ";test=fire", sitting="W9@1", evidence="pawn_census: 40 dead from the spores, a real bug", cause="pilot_cause: the spore cloud from RM_Plant_Mushroom kills pawns (TESTPILOT_SAT cause)")
ok("real_bug_beats_retired_narrow", verdict(ROT + ";test=fire") == "SURPRISING")
ok("real_bug_beats_retired_wide", verdict(ROT) == "SURPRISING", verdict(ROT))
ok("real_bug_beats_retired_sideways", verdict(ROT + ";season=summer") == "SURPRISING")
ok("conflicting_bug_does_not", verdict(ROT + ";test=ice") == "EXPECTED", verdict(ROT + ";test=ice"))

# 7 sample: a sitting must re-check one retired entry in its context; after it records it, none remain
fresh()
for i in range(N):
    rec("explained", sitting="Q%d@1" % i)
    rec("explained", kind="weather_snow_in_summer", sitting="Q%d@1" % i)
B.begin(ROT, "NOW@2")
pick = B.pick_sample(ROT, "NOW@2")
ok("sample_one_per_sitting", len(pick) == RULES["sample_per_sitting"] == 1, pick)
ok("sample_outside_context_none", B.pick_sample(DESERT, "NOW@2") == [])
e = B.explain(pick[0]["kind"], ROT, "NOW@2")
ok("sample_not_explained_by_book", e["outcome"] == "STANDS", e)
try:
    rec("sample_ok", kind="never_retired_kind", sitting="NOW@2", sample=True)
    ok("sample_needs_retired", False)
except B.BookError:
    ok("sample_needs_retired", True)
rec("sample_ok", kind=pick[0]["kind"], sitting="NOW@2", sample=True)
ok("sample_done_after_one", B.pick_sample(ROT, "NOW@2") == [])
B.begin(ROT, "LATER@3")
nxt = B.pick_sample(ROT, "LATER@3")
ok("sample_rotates", nxt and nxt[0]["kind"] != pick[0]["kind"], nxt)
other = [k for k in (KIND, "weather_snow_in_summer") if k != pick[0]["kind"]][0]
ok("non_sample_explained_by_book", B.explain(other, ROT, "NOW@2")["outcome"] == "EXPLAINED")

# 7b owner 2026-11-04: co-occurrence never revives; only a real bug causally linked to the observation does
fresh()
for i in range(N):
    rec("explained", sitting="CO%d@1" % i)
lines = rec("real_bug", sitting="CO9@1", item="ROT_OTHER_FIX_IT", evidence="a real bug on this map; mushrooms were nearby")
ok("co_occurrence_does_not_revive", verdict() == "EXPECTED" and [w["event"] for w in lines] == ["outcome"]
   and lines[0]["outcome"] == "co_occurred" and "co-occurred, not linked" in lines[0]["evidence"], lines)
ent = B.fold(B.read(), RULES)[(KIND, ROT)]
ok("co_occurrence_recorded_against_entry", ent["outcomes"].get("co_occurred") == 1 and not ent["last_bug"], ent["outcomes"])
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:                # a hand-written causeless real_bug folds the same
    f.write(json.dumps({"id": "handwritten0001", "ts": tick(), "event": "outcome", "kind": KIND, "context": ROT,
                        "sitting": "CO9@1", "outcome": "real_bug", "evidence": "no cause on this line"}) + "\n")
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:                # ...and the revive line written for it then is inert
    f.write(json.dumps({"id": "handwritten0002", "ts": tick(), "event": "revive", "for": "handwritten0001", "kind": KIND,
                        "context": ROT, "sitting": "CO9@1", "evidence": []}) + "\n")
ok("causeless_real_bug_line_does_not_revive", verdict() == "EXPECTED" and B.check() == [] and B.heal() == [], B.check())
for bad in ("because mushrooms", "pilot_cause: short", "fix_commit: no sha cited for the mushroom fix",
            "nearby: the mushroom was right next to the bug"):
    try:
        rec("real_bug", sitting="CO9@1", evidence="a real bug was found here", cause=bad)
        ok("bad_cause_refused " + bad, False)
    except B.BookError:
        ok("bad_cause_refused " + bad, True)
lines = rec("real_bug", sitting="CO9@1", evidence="pawns die in the spore cloud",
            cause="gone_after_fix: with RM_Plant_Mushroom spores disabled the deaths stop")
ok("linked_bug_revives_with_cause_in_audit", verdict() == "SURPRISING" and lines[-1]["event"] == "revive"
   and lines[-1]["evidence"][0]["cause"].startswith("gone_after_fix"), lines)

# 8 settle: dropped -> not_a_bug, done -> co_occurred (no causal link yet: no revive), open -> untouched; idempotent
fresh()
for i in range(N):
    rec("explained", sitting="Z%d@1" % i)
rec("filed", sitting="Z9@1", item="ROT_A_DROP_IT", evidence="")
rec("filed", sitting="Z9@1", item="ROT_B_FIX_IT", evidence="")
rec("filed", sitting="Z9@1", item="ROT_C_OPEN_IT", evidence="")
world = types.SimpleNamespace(items={"ROT_A_DROP_IT": types.SimpleNamespace(state="dropped"),
                                     "ROT_B_FIX_IT": types.SimpleNamespace(state="done"),
                                     "ROT_C_OPEN_IT": types.SimpleNamespace(state="doing")})
out = B.settle(world, ts="2026-11-05T00:00:00Z")
outs = [(w.get("item"), w.get("outcome"), w["event"]) for w in out]
ok("settle_maps_states", ("ROT_A_DROP_IT", "not_a_bug", "outcome") in outs
   and ("ROT_B_FIX_IT", "co_occurred", "outcome") in outs and not any(i == "ROT_C_OPEN_IT" for i, _, _ in outs), outs)
ok("settle_done_does_not_revive", verdict() == "EXPECTED" and not any(e == "revive" for _, _, e in outs), outs)
ok("settle_idempotent", B.settle(world) == [])
ok("settle_links_by_id", all(w["settles"] for w in out if w["event"] == "outcome"), out)
fresh()
rec("filed", sitting="Y@1", item="ROT_D_DROP_IT", evidence="")
rec("filed", sitting="Y@1", item="ROT_E_DROP_IT", evidence="")
rec("filed", sitting="Y2@1", item="ROT_D_DROP_IT", evidence="")     # the same item filed twice: both settle
world = types.SimpleNamespace(items={"ROT_D_DROP_IT": types.SimpleNamespace(state="dropped"),
                                     "ROT_E_DROP_IT": types.SimpleNamespace(state="dropped")})
out = B.settle(world, reasons={"ROT_D_DROP_IT": "duplicate of ROT_X_FIX_IT", "ROT_E_DROP_IT": "the spores are by design"})
outs = sorted((w["item"], w["outcome"]) for w in out)
ok("settle_admin_drop_abandoned", outs == [("ROT_D_DROP_IT", "abandoned"), ("ROT_D_DROP_IT", "abandoned"),
                                           ("ROT_E_DROP_IT", "not_a_bug")], outs)
ok("settle_drop_reason_in_evidence", any("by design" in w["evidence"] for w in out), out)
ok("drop_reasons_reads_ledger", B.drop_reasons([{"event": "drop", "id": "X_A_B", "reason": "later"}]) == {"X_A_B": "later"})

# 9 explain-away against the real roster: RM_Agaripod is patch-or-inline cast of RM_TheRot, not of RM_BlueDesert
fresh()
cast = B.roster("RM_TheRot")
ok("roster_reads_animals_and_plants", cast["wildAnimals"] and cast["wildPlants"], cast)
ok("roster_unknown_biome_is_none", B.roster("TemperateForest") == {"wildAnimals": None, "wildPlants": None})
web = B.roster("RM_Webwork")["wildPlants"] or []
ok("roster_sees_patch_added_plant", "RSW_Plant_TookeTrap_Wild" in web, web[-3:])   # WildPlants_Webwork.xml
e = B.explain("creature_unexpected", ROT, "A@1", defs=["RM_Agaripod"])
ok("explain_on_roster", e["outcome"] == "EXPLAINED" and "RM_Agaripod" in e["facts"][0], e)
e = B.explain("creature_unexpected", DESERT, "A@1", defs=["RM_Agaripod"])
ok("explain_off_roster_stands", e["outcome"] == "STANDS" and any("NOT on" in f for f in e["facts"]), e)
e = B.explain("creature_unexpected", "biome=TemperateForest", "A@1", defs=["RM_Agaripod"])
ok("explain_unknown_roster_stands", e["outcome"] == "STANDS", e)

# 9b explain-away guards: roster kinds only; an off-roster def contradicts a retirement; an uncertain def never explains
fresh()
e = B.explain("dead_animals_no_cause", ROT, "A@1", defs=["RM_Agaripod"])
ok("roster_explains_roster_kinds_only", e["outcome"] == "STANDS" and any("not a roster kind" in f for f in e["facts"]), e)
for i in range(N):
    rec("explained", kind="creature_unexpected", sitting="V%d@1" % i)
fake = lambda b: {"wildAnimals": ["RM_Agaripod"], "wildPlants": []}
none = lambda r: set()
e = B.explain("creature_unexpected", ROT, "V9@1", defs=["RM_Banth"], roster_of=fake, uncertain_of=none,
              events=[x for x in B.read() if True])
B.begin(ROT, "V9@1")
picked = B.pick_sample(ROT, "V9@1")
if picked:      # the retired key is this sitting's sample: then it stands for that reason; ask from a spent sitting
    rec("sample_ok", kind="creature_unexpected", sitting="V9@1", sample=True)
    e = B.explain("creature_unexpected", ROT, "V9@1", defs=["RM_Banth"], roster_of=fake, uncertain_of=none)
ok("off_roster_contradicts_retirement", e["outcome"] == "STANDS" and any("contradicts" in f for f in e["facts"]), e)
ok("on_roster_keeps_retirement", B.explain("creature_unexpected", ROT, "V9@1", defs=["RM_Agaripod"], roster_of=fake,
                                           uncertain_of=none)["outcome"] == "EXPLAINED")
ok("uncertain_beats_retirement_too", B.explain("creature_unexpected", ROT, "V9@1", defs=["RM_Agaripod"],
   roster_of=fake, uncertain_of=lambda r: {("RM_TheRot", "RM_Agaripod")})["outcome"] == "STANDS")
fresh()
e = B.explain("creature_unexpected", ROT, "A@1", defs=["RM_Agaripod"], roster_of=fake,
              uncertain_of=lambda r: {("RM_TheRot", "RM_Agaripod")})
ok("uncertain_def_never_explains", e["outcome"] == "STANDS" and any("UNCERTAIN" in f for f in e["facts"]), e)
ok("uncertain_is_scoped_to_its_biome", B.explain("creature_unexpected", DESERT, "A@1", defs=["RM_Agaripod"],
   roster_of=fake, uncertain_of=lambda r: {("RM_TheRot", "RM_Agaripod")})["outcome"] == "EXPLAINED")
ok("our_findmod_is_not_uncertain", ("RM_Webwork", "RSW_Plant_TookeTrap_Wild") not in B.uncertain("wildPlants"))
ok("entry_xpath_is_uncertain", ("ExtremeDesert", "AA_Eyeling") in B.uncertain("wildAnimals"))   # ZZZ_..Duplicates

# 9c union-merge duplicates do not inflate a run; a missing audit line is caught; sample quota and pick are enforced
fresh()
for i in range(N - 1):
    rec("explained", sitting="D%d@1" % i)
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    body = f.read()
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write(body + body)                                   # what a union merge of two clones can leave behind
ok("duplicates_do_not_retire", verdict() == "SURPRISING" and len(B.read()) == N - 1, (verdict(), len(B.read())))
lines = rec("explained", sitting="D9@1")
ok("then_the_real_nth_retires", verdict() == "EXPECTED" and lines[-1]["for"] == lines[0]["id"], lines)
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    kept = [x for x in f if '"retire"' not in x]
with open(os.environ["RM_SURPRISE_BOOK"], "w") as f:
    f.write("".join(kept))
ok("check_catches_missing_audit", any("no audit line" in p for p in B.check()), B.check())
healed = B.heal()
ok("heal_writes_the_owed_audit", [w["event"] for w in healed] == ["retire"] and B.check() == [], (healed, B.check()))
ok("heal_is_idempotent", B.heal() == [])
fresh()
for i in range(N):
    rec("explained", sitting="Q%d@1" % i)
    rec("explained", kind="weather_snow_in_summer", sitting="Q%d@1" % i)
B.begin(ROT, "X@1")
pick = B.pick_sample(ROT, "X@1")[0]["kind"]
wrong = [k for k in (KIND, "weather_snow_in_summer") if k != pick][0]
try:
    rec("sample_ok", kind=wrong, sitting="X@1", sample=True)
    ok("sample_must_be_the_pick", False)
except B.BookError:
    ok("sample_must_be_the_pick", True)
rec("sample_ok", kind=pick, sitting="X@1", sample=True)
try:
    rec("sample_ok", kind=wrong, sitting="X@1", sample=True)
    ok("sample_quota_enforced", False)
except B.BookError:
    ok("sample_quota_enforced", True)

# 9c' a sample is picked from the context the sitting declared at start, never a narrower one; no start, no sample
fresh()
for i in range(N):
    rec("explained", ctx=ROT + ";test=fire", sitting="F%d@1" % i)          # older: the pick under ROT;test=fire
for i in range(N):
    rec("explained", kind="weather_snow_in_summer", sitting="F%d@1" % i)
try:
    rec("sample_ok", kind="weather_snow_in_summer", sitting="NOSTART@1", sample=True)
    ok("sample_needs_start", False)
except B.BookError:
    ok("sample_needs_start", True)
B.begin(ROT + ";test=fire", "G@1")
ok("begin_first_context_wins", B.begin(ROT, "G@1") == "biome=RM_TheRot;test=fire")
try:
    rec("sample_ok", kind="weather_snow_in_summer", sitting="G@1", sample=True)   # the pick is the fire entry
    ok("sample_no_narrowing_bypass", False)
except B.BookError:
    ok("sample_no_narrowing_bypass", True)
ok("sitting_line_checks_clean", B.check() == [], B.check())

# 9c'' the book is never written backwards: a line older than the key's latest is refused, so no audit goes missing
try:
    B.record(KIND, ROT + ";test=fire", "OLD@1", "explained", evidence="a clock behind", ts="2026-01-01T00:00:00Z")
    ok("backdated_line_refused", False)
except B.BookError:
    ok("backdated_line_refused", True)

# 9c''' a union merge of two clones that each retired the key leaves a redundant audit, which check accepts
fresh()
for i in range(N - 1):
    rec("explained", sitting="U%d@1" % i)
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    base = f.read()
a_lines = rec("explained", sitting="UA@1")                          # clone A
with open(os.environ["RM_SURPRISE_BOOK"], "w") as f:
    f.write(base)
b_lines = rec("explained", sitting="UB@1")                          # clone B, later
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write("".join(json.dumps(w, sort_keys=True) + "\n" for w in a_lines))   # the union
ok("union_both_retire_audits", [w["event"] for w in a_lines + b_lines] == ["outcome", "retire"] * 2)
ok("union_merge_checks_clean", B.check() == [], B.check())
fresh()
for i in range(N):
    rec("explained", kind="weather_snow_in_summer", ctx=ROT + ";test=fire", sitting="H%d@1" % i)   # older, narrow
for i in range(N):
    rec("explained", sitting="H%d@1" % i)                                                       # KIND under ROT
B.begin(ROT, "HS@1")
e = B.explain(KIND, ROT + ";test=fire", "HS@1")
fresh()                                                             # two clones each below N; their union crosses it
rec("explained", sitting="J0@1")
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    base = f.read()
a_lines = rec("explained", sitting="JA@1")
with open(os.environ["RM_SURPRISE_BOOK"], "w") as f:
    f.write(base)
rec("explained", sitting="JB@1")
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write("".join(json.dumps(w, sort_keys=True) + "\n" for w in a_lines))
owed = B.check()
B.begin(ROT, "JS@1")
ok("union_crossing_healed_by_start", len(owed) == 1 and B.check() == [] and verdict() == "EXPECTED", (owed, B.check()))
fresh()                                                             # two clones settled one filing: one outcome
f_line = rec("filed", sitting="K0@1", item="ROT_K_DROP_IT", evidence="")[0]
w1 = types.SimpleNamespace(items={"ROT_K_DROP_IT": types.SimpleNamespace(state="dropped")})
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    base = f.read()
s1 = B.settle(w1)
with open(os.environ["RM_SURPRISE_BOOK"], "w") as f:
    f.write(base)
B.settle(w1)
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write("".join(json.dumps(w, sort_keys=True) + "\n" for w in s1))
ent = B.fold(B.read(), RULES)[(KIND, ROT)]
fresh()                                                             # two clones each retire by settling one filing
rec("explained", sitting="L1@1"); rec("explained", sitting="L2@1")
rec("filed", sitting="L3@1", item="ROT_L_DROP_IT", evidence="")
w2 = types.SimpleNamespace(items={"ROT_L_DROP_IT": types.SimpleNamespace(state="dropped")})
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    base = f.read()
s1 = B.settle(w2)
with open(os.environ["RM_SURPRISE_BOOK"], "w") as f:
    f.write(base)
s2 = B.settle(w2)
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write("".join(json.dumps(w, sort_keys=True) + "\n" for w in s1))
ok("double_settle_audits_check_clean", [w["event"] for w in s1].count("retire") == 1
   and [w["event"] for w in s2].count("retire") == 1 and B.check() == [] and B.heal() == [] and verdict() == "EXPECTED",
   (s1, s2, B.check()))
fresh()                                                             # the clones settled it differently: A abandoned, B not_a_bug
rec("explained", sitting="M1@1"); rec("explained", sitting="M2@1")
rec("filed", sitting="M3@1", item="ROT_M_DROP_IT", evidence="")
w3 = types.SimpleNamespace(items={"ROT_M_DROP_IT": types.SimpleNamespace(state="dropped")})
with open(os.environ["RM_SURPRISE_BOOK"]) as f:
    base = f.read()
sa = B.settle(w3, ts="2026-11-05T00:00:00Z", reasons={"ROT_M_DROP_IT": "duplicate of ROT_X_FIX_IT"})
with open(os.environ["RM_SURPRISE_BOOK"], "w") as f:
    f.write(base)
sb = B.settle(w3, ts="2026-11-05T00:00:01Z")
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write("".join(json.dumps(w, sort_keys=True) + "\n" for w in sa))
ok("differing_double_settle_check_clean", [w["event"] for w in sb] == ["outcome", "retire"] and B.check() == []
   and B.heal() == [] and verdict() == "SURPRISING", (sa, sb, B.check()))
ok("double_settle_counts_once", ent["outcomes"].get("not_a_bug") == 1 and len(ent["run"]) == 1, ent["outcomes"])
ok("explain_samples_from_sitting_context", e["outcome"] == "STANDS" and "SAMPLE" in e["facts"][0], e)

# 9d CLI: the sitting id format is enforced; a bare file name as the book path works
ok("cli_refuses_bad_sitting", B.main(["summary", "--sitting", "ITEM@2026-11-04"]) == 2)
ok("cli_accepts_sitting", B.main(["summary", "--sitting", "SOME_ITEM_FIX_IT@2026-11-04T0930"]) == 0)
cwd = os.getcwd()
os.chdir(tempfile.mkdtemp(prefix="surprise_book_rel_"))
os.environ["RM_SURPRISE_BOOK"] = "book.jsonl"
ok("relative_book_path", B.main(["record", "--kind", KIND, "--context", ROT, "--sitting", "A_B_C@2026-11-04T0930",
                                 "--outcome", "explained", "--evidence", "test purpose: rot map"]) == 0)
ok("cli_start_declares_sitting", B.main(["start", "--context", ROT, "--sitting", "A_B_C@2026-11-04T0931"]) == 0
   and B.sitting_context(B.read(), "A_B_C@2026-11-04T0931") == ROT)
os.chdir(cwd)

# 10 summary line, record guards, audit check, the shipped book
fresh()
for i in range(N):
    rec("explained", sitting="S@%d" % (i % M) if i < N - 1 else "LAST@1")
s = B.summary("LAST@1")
ok("summary_counts", s.startswith("explained 1, retired %s@%s" % (KIND, ROT)), s)
for bad in (dict(outcome="explained", evidence=""), dict(outcome="filed"), dict(outcome="sample_ok"),
            dict(outcome="bogus")):
    try:
        B.record("x_kind_ok", ROT, "A@1", bad["outcome"], evidence=bad.get("evidence", "long enough text"))
        ok("record_refuses_%s" % bad["outcome"], False)
    except B.BookError:
        ok("record_refuses_%s" % bad["outcome"], True)
ok("check_clean", B.check() == [], B.check())
with open(os.environ["RM_SURPRISE_BOOK"], "a") as f:
    f.write('{"ts": "z", "event": "retire", "kind": "made_up", "context": "biome=RM_TheRot"}\n')
ok("check_catches_forged_retire", len(B.check()) == 1, B.check())
del os.environ["RM_SURPRISE_BOOK"]
ok("shipped_book_clean", B.check() == [], B.check())

print("selftest_surprise_book: %d passed, %d failed" % (len(PASS), len(FAIL)))
sys.exit(1 if FAIL else 0)
