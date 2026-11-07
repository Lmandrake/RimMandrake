#!/usr/bin/env python3
"""selftest_fleet_mods.py — RELENTLESS_NOW's mods/receipts derivations, offline (no git, no ledger, no store).

Covers: title_short (prefixes, tags, ids, word cut), real_count (ledger-only commits excluded), mod grouping
(mod_of_path, attribute dropping infra when a mod was touched, mod_by_name longest match), outcome (main commit, marks
skipped), receipts (today only, PASS/FAIL), detached_done (finished detached helpers only), and the retirement of
Fleet Watch (FLEETWATCH_CODE_RETIRE_NOBODY_WAS_WATCHING): its files are gone and nothing live names them.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fleet_mods as M  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# title_short
check("title: alarm prefix dropped", M.title_short("Ops alarm: FOO_BAR_1 died") == "Foo bar died")
check("title: MOD prefix needs a separator", M.title_short("MODCHECK ultrafast clock") == "MODCHECK ultrafast clock")
check("title: [TAG] dropped", M.title_short("[MINOR] Hot springs") == "Hot springs")
check("title: snake name made words", M.title_short("suspension_settings_live") == "Suspension settings live")
check("title: head before colon", M.title_short("Cold storage: 16 new defs and more") == "Cold storage")
t = M.title_short("Can we replicate Geological Landforms worldgen behaviour in our own mod")
check("title: <=28 chars, word cut", len(t) <= 28 and t.endswith("…") and not t[:-1].endswith(" "))
check("title: path -> basename", "fleet_mods.py" in M.title_short("Fix src/RimMandrake/Utils/fleet_mods.py now"))

# real_count
log = "@@a1\ninfrastructure/state/ledger/events/BENCH.jsonl\n@@b2\nsrc/RimMandrake/Utils/x.py\n@@c3\nconversations/x.md\n"
check("real_count excludes ledger-only commits", M.real_count(log) == 1)

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


# marks: a tick means a passed check; a finish with no check says so
check("finish_mark: PASS tick, FAIL cross, unchecked dot", (M.finish_mark("PASS"), M.finish_mark("FAIL"), M.finish_mark(None),
      M.finish_mark("WEAK"), M.finish_mark("PASS", ok=False)) == (("✓", "pass"), ("✗", "fail"), ("●", "done"), ("●", "done"),
                                                                ("✗", "fail")))
check("day_label: today is blank, earlier days dated", M.day_label(now - 1, now) == "" and
      M.day_label(M.local_midnight(now) - 3600, now) != "" and M.day_label(0, now) == "")
check("split_cross: 3+ mods (infra not counted) is cross", M.split_cross(
      {"A": {"X", "Y", "Z"}, "B": {"X", "Y", M.INFRA}, "C": {"X"}}) == {"A"})
check("display_title: a two-word head keeps the rest", M.display_title("Full list: dev save loads Default")
      == "Full list: dev save loads Default" and M.display_title("Biome tier cleanup: x") == "Biome tier cleanup")
# detached_done: finished detached helpers only, readers injected (no systemctl, no git, no ledger)
import json  # noqa: E402
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    def put(name, rec):
        with open(os.path.join(td, name), "w") as f:
            json.dump(rec, f)

    outp = os.path.join(td, "a.out.json")
    put("a.out.json", {"usage": {"input_tokens": 10, "output_tokens": 5}})
    put("a.json", {"unit": "u-a", "item": "D_DONE", "at": now - 600, "out": outp})
    put("b.json", {"unit": "u-b", "item": "D_LIVE", "at": now - 600})
    put("c.json", {"unit": "u-c", "item": "D_OLD", "at": now - 50 * 3600})
    put("d.json", {"unit": "u-d", "item": "D_QUIET", "at": now - 300})
    dd = {r["item"]: r for r in M.detached_done(24, now=now, root=td,
                                                unit_state=lambda u: "active" if u == "u-b" else "inactive",
                                                item_state=lambda i: "closed" if i == "D_DONE" else "doing",
                                                commits=lambda i, since: 2 if i == "D_DONE" else 0)}
check("detached_done: running and too-old helpers left out", set(dd) == {"D_DONE", "D_QUIET"})
check("detached_done: closed item is Done with commits and tokens", dd.get("D_DONE", {}).get("status") == "Done"
      and dd["D_DONE"]["commit_count"] == 2 and dd["D_DONE"]["tokens"] == 15)
check("detached_done: no commits, not closed -> Stopped, tokens UNMEASURED", dd.get("D_QUIET", {}).get("status") == "Stopped"
      and dd["D_QUIET"]["tokens"] is None)

# Fleet Watch is retired (owner 2026-11-04: "Retire FleetWatch, we're not using it, and it saves tokens."):
# its files stay gone and no live code, unit, rule or allowlist names them. History (ledger, lessons, handoffs,
# conversations) and this test are exempt.
import re  # noqa: E402

UTILS = os.path.dirname(os.path.abspath(__file__))
REPO = M.REPO
GONE = ["src/RimMandrake/Utils/fleet_watch.py", "src/RimMandrake/Utils/fleet_refresh.py",
        "src/RimMandrake/Utils/fleetwatch_page.html", "src/RimMandrake/Utils/selftest_fleet_refresh.py",
        "src/RimMandrake/Utils/systemd/rm-fleetwatch.service", "src/RimMandrake/Utils/systemd/rm-fleetwatch.timer"]
check("retired: Fleet Watch files are gone", [g for g in GONE if os.path.exists(os.path.join(REPO, g))] == [])
check("retired: fleet_mods.py and owner_queue.py, which RELENTLESS_NOW reads, remain",
      all(os.path.exists(os.path.join(UTILS, f)) for f in ("fleet_mods.py", "owner_queue.py")))
NAMES = re.compile(r"\bfleet_watch\b|\bfleet_refresh\b|fleetwatch_page|rm-fleetwatch")
named = []
for root, dirs, files in os.walk(os.path.join(REPO, "src")):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "bin", "obj")]
    for fn in files:
        if not fn.endswith((".py", ".json", ".service", ".timer", ".sh", ".html", ".md")):
            continue
        fp = os.path.join(root, fn)
        if os.path.abspath(fp) == os.path.abspath(__file__):
            continue
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                if NAMES.search(f.read()):
                    named.append(os.path.relpath(fp, REPO))
        except OSError:
            pass
check("retired: nothing under src/ names fleet_watch, fleet_refresh, fleetwatch_page or rm-fleetwatch %s" % named,
      named == [])
check("retired: the instrument can see (it finds fleet_mods in running_now.py)",
      "fleet_mods" in open(os.path.join(UTILS, "running_now.py"), encoding="utf-8").read())

print("\n%d FAIL" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
