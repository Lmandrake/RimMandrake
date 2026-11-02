#!/usr/bin/env python3
"""selftest_fleet_mods.py — the Fleet Watch page's derivations, offline (no git, no ledger, no store).

Covers: title_short (prefixes, tags, ids, word cut), activity (no shell text ever reaches the page), stuck (silent /
circling only on live rows), real_count (ledger-only commits excluded), mod grouping (mod_of_path, attribute dropping
infra when a mod was touched, mod_by_name longest match), outcome (main commit, marks skipped), receipts (today only,
PASS/FAIL), and fleet_refresh.plan writing only changed rows, `mods` only when due, board/factory never alone.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fleet_mods as M  # noqa: E402
import fleet_refresh as F  # noqa: E402
import fleet_watch as W  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# title_short
check("title: alarm prefix dropped", W.title_short("Ops alarm: FOO_BAR_1 died") == "Foo bar died")
check("title: MOD prefix needs a separator", W.title_short("MODCHECK ultrafast clock") == "MODCHECK ultrafast clock")
check("title: [TAG] dropped", W.title_short("[MINOR] Hot springs") == "Hot springs")
check("title: snake name made words", W.title_short("suspension_settings_live") == "Suspension settings live")
check("title: head before colon", W.title_short("Cold storage: 16 new defs and more") == "Cold storage")
t = W.title_short("Can we replicate Geological Landforms worldgen behaviour in our own mod")
check("title: <=28 chars, word cut", len(t) <= 28 and t.endswith("…") and not t[:-1].endswith(" "))
check("title: path -> basename", "fleet_watch.py" in W.title_short("Fix src/RimMandrake/Utils/fleet_watch.py now"))

# activity: never shell text
check("activity: Bash description", W.activity("Bash", {"command": "ls -la", "description": "List files"}) == "listing files")
a = W.activity("Bash", {"command": "python3 src/RimMandrake/Utils/run_selftests.py --only x", "description": "cd /x && grep -n foo | head"})
check("activity: shellish description falls back to a phrase", a == "running selftests")
check("activity: unknown command dropped", W.activity("Bash", {"command": "awk '{print $2}' f | sort -u"}) == "")
check("activity: Read basename", W.activity("Read", {"file_path": "/a/b/c.py"}) == "reading c.py")
check("activity: unknown tool dropped", W.activity("Frobnicate", {}) == "")
for name, inp in (("Bash", {"command": "git log --oneline | head", "description": "git log --oneline | head"}),
                  ("Bash", {"command": "sed -i s/a/b/ x"}), ("Grep", {"pattern": "x|y"})):
    out = W.activity(name, inp)
    check("activity: no shell chars in %r" % out, not any(ch in out for ch in "|&;$`>"))

# stuck
now = 10000
check("stuck: silent live row", W.stuck({"status": "Building", "last_activity": now - 11 * 60}, now) == "silent 11m")
check("stuck: quiet done row is not stuck", W.stuck({"status": "Done", "last_activity": now - 99 * 60}, now) == "")
check("stuck: fresh live row", W.stuck({"status": "Building", "last_activity": now - 60}, now) == "")
check("stuck: circling wins", W.stuck({"status": "Checking", "last_activity": now}, now, "same diff twice").startswith("circling"))

# real_count
log = "@@a1\ninfrastructure/state/ledger/events/BENCH.jsonl\n@@b2\nsrc/RimMandrake/Utils/x.py\n@@c3\nconversations/x.md\n"
check("real_count excludes ledger-only commits", W.real_count(log) == 1)

# grouping
mods = {"Stillsand", "FlowWorks"}
check("mod_of_path src", M.mod_of_path("src/RimMandrake/Stillsand/Defs/a.xml", mods) == "Stillsand")
check("mod_of_path design", M.mod_of_path("design/RimMandrake/FlowWorks/x.md", mods) == "FlowWorks")
check("mod_of_path tooling -> None", M.mod_of_path("src/RimMandrake/Utils/x.py", mods) is None)
glog = M.parse_log("@@s1\t100\tA_ONE: still defs\nsrc/RimMandrake/Stillsand/a.xml\nsrc/RimMandrake/Utils/t.py\n"
                   "@@s2\t200\tB_TWO: tool\nsrc/RimMandrake/Utils/t.py\n"
                   "@@s3\t300\tA_ONE: ledger\ninfrastructure/state/ledger/events/BENCH.jsonl\n")
by_item, item_mods, mod_last, item_last = M.attribute(glog, {"A_ONE", "B_TWO"}, mods)
check("attribute: mod item not also infra", item_mods["A_ONE"] == {"Stillsand"})
check("attribute: tooling item is infra", item_mods["B_TWO"] == {M.INFRA})
check("attribute: ledger-only commit ignored", item_last["A_ONE"] == 100 and len(by_item["A_ONE"]) == 1)
check("mod_by_name longest match", M.mod_by_name("FLOW_WORKS_PUMP_1", {"FLOW": "Flow", "FLOWWORKS": "FlowWorks"}) == "FlowWorks")

# outcome
cs = [{"subject": "X_Y: review marks", "files": ["a", "b", "c"]},
      {"subject": "X_Y: exact-step speed proof", "files": ["src/a.py", "src/b.py"]},
      {"subject": "X_Y: ledger", "files": ["infrastructure/state/ledger/events/B.jsonl"]}]
check("outcome: main commit, marks skipped", M.outcome(cs) == "Exact-step speed proof.")
check("outcome: none -> empty", M.outcome([]) == "")


# receipts
class World:
    items = {}


now = int(time.time())
rel = {"R_OK": {"status": "done", "done_at": now - 60, "gen": 2, "attempts": 1, "spent": 5000,
                "check": {"verdict": "PASS"}},
       "R_BAD": {"status": "done", "done_at": now - 120, "check": {"verdict": "FAIL"}},
       "R_OLD": {"status": "done", "done_at": M.local_midnight(now) - 60, "check": {"verdict": "PASS"}}}
rc = {r["item"]: r for r in M.receipts(now, {"R_OK": cs}, rel, World(), [])}
check("receipts: today only", set(rc) == {"R_OK", "R_BAD"})
check("receipts: PASS row", rc["R_OK"]["receipt"] == {"ok": True, "check": "PASS", "outcome": "Exact-step speed proof.",
                                                      "commits": 2, "tokens": 5000} and "ga" not in rc["R_OK"])
check("receipts: PASS row marked check-passed", rc["R_OK"]["glyph"] == "✓")
check("receipts: FAIL row", rc["R_BAD"]["glyph"] == "✗" and rc["R_BAD"]["receipt"]["check"] == "FAIL")


# plan: changed rows only, mods when due, factory never alone
def row(item, status, el=1):
    return {"item": item, "title": item, "status": status, "elapsed_min": el}


docs = [("mods", "Stillsand", {"id": "Stillsand", "x": 1}), ("board", "factory", {"ok": True, "tokens_today": 5})]
w, _, _, st = F.plan([row("A", "Building")], {}, 100, "/r", docs, mods_due=True)
check("plan: first run writes row, mod, factory", [(x["collection"], x["doc_id"]) for x in w] ==
      [("parts", "A"), ("board", "factory"), ("mods", "Stillsand")])
check("plan: mod doc by file_path", w[2]["file_path"] == "/r/mods/Stillsand.json")
many = [("mods", "M%d" % i, {"id": i}) for i in range(80)]
wc, _, _, stc = F.plan([row("R%d" % i, "Done") for i in range(45)], {"status": {"R0": "Building"}}, 100, "/r", many, True)
check("plan: one batch stays under the 50-write limit", len(wc) <= F.MAX_WRITES)
check("plan: unwritten rows stay unhashed for the next run", len(stc["row_hashes"]) == F.MAX_WRITES - F.FEED_MAX - 1)
check("plan: mods not all written -> still due next run", stc["mods_at"] == 0)
prev = dict(st, versions={"parts/A": 1, "mods/Stillsand": 1, "board/factory": 1, "board/summary": 2})
docs2 = [docs[0], ("board", "factory", {"ok": True, "tokens_today": 9})]
w2, _, _, _ = F.plan([row("A", "Building", el=7)], prev, 200, "/r", docs2, mods_due=True)
check("plan: unchanged row, mod and token-only factory -> no writes", w2 == [])
w3, _, _, _ = F.plan([row("A", "Done")], prev, 300, "/r", [("mods", "Stillsand", {"id": "Stillsand", "x": 2})] + docs2[1:])
check("plan: changed row writes it plus factory; mods wait until due",
      [(x["collection"], x["doc_id"]) for x in w3 if x["collection"] != "feed"] == [("parts", "A"), ("board", "factory")])
check("plan: known docs carry if_version", all("if_version" in x for x in w3 if x["collection"] != "feed"))
w4, _, _, _ = F.plan([row("A", "Building")], prev, 400, "/r", [("board", "factory", {"ok": False, "tokens_today": 9})])
check("plan: factory going not-ok writes alone", [(x["collection"], x["doc_id"]) for x in w4] == [("board", "factory")])

# headline: Python's words, the model relays them
hl = F.headline([dict(row("A", "Building"), title="Hot springs: new defs"), row("B", "Checking"),
                 dict(row("C", "Done"), receipt={"check": "PASS"}), dict(row("D", "Done"), receipt={"check": "FAIL"})])
check("headline from rows alone", hl == "Building Hot springs; checking 1; 2 finished today (1 PASS, 1 FAIL, 0 unchecked).")

# marks: a tick means a passed check; a finish with no check says so
check("finish_mark: PASS tick, FAIL cross, unchecked dot", (M.finish_mark("PASS"), M.finish_mark("FAIL"), M.finish_mark(None),
      M.finish_mark("WEAK"), M.finish_mark("PASS", ok=False)) == (("✓", "pass"), ("✗", "fail"), ("●", "done"), ("●", "done"),
                                                                ("✗", "fail")))
check("feed words: unchecked finish is not a PASS", F.finished_words({"status": "Done", "receipt": {"ok": True}}) ==
      "finished, unchecked" and F.finished_words({"status": "Done", "receipt": {"ok": True, "check": "PASS"}}) ==
      "finished, check PASS" and F.finished_words({"status": "Ended"}) == "stopped reporting")
check("attempt in words, none on the first try", (W.attempt_words(1), W.attempt_words(3), W.attempt_words(None)) ==
      ("", "attempt 3", ""))
check("day_label: today is blank, earlier days dated", M.day_label(now - 1, now) == "" and
      M.day_label(M.local_midnight(now) - 3600, now) != "" and M.day_label(0, now) == "")
check("split_cross: 3+ mods (infra not counted) is cross", M.split_cross(
      {"A": {"X", "Y", "Z"}, "B": {"X", "Y", M.INFRA}, "C": {"X"}}) == {"A"})
check("display_title: a two-word head keeps the rest", M.display_title("Full list: dev save loads Default")
      == "Full list: dev save loads Default" and M.display_title("Biome tier cleanup: x") == "Biome tier cleanup")
dup = [{"item": "LS_A", "title": "LeaningScrub stall: animals made", "short": "LeaningScrub stall"},
       {"item": "LS_B", "title": "LeaningScrub stall: animals made", "short": "LeaningScrub stall"},
       {"item": "C", "title": "Other thing", "short": "Other thing"}]
F.disambiguate(dup)
check("disambiguate: one title for two items gets told apart", len({r["short"] for r in dup}) == 3
      and dup[2]["short"] == "Other thing")
check("headline empty fleet", F.headline([]) == "Nothing building.")
check("headline: a row that stopped reporting is not a finish", F.headline([dict(row("E", "Ended"))]) ==
      "Nothing building; 1 stopped reporting.")
bw = F.board_write("H", 5, 3)
check("board write ready-made", bw == {"op": "update", "collection": "board", "doc_id": "summary",
                                       "data": {"headline": "H", "updated": 5}, "if_version": 3})
check("prompt carries the board write, no model words asked", '"headline": "H"' in F.prompt([], "H", 5, 3)
      and "HEADLINE" not in F.prompt([], "H", 5, 3))

print("\n%d FAIL" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
