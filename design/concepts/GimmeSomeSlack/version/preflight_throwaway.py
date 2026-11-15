#!/usr/bin/env python3
"""THROWAWAY (Maturation hand run beside the pilot, row 3, 2026-11-14): Stage 2 preflight of GimmeSomeSlack 0.1.0.

Checks version/test_table.json against the repo, the def dump and the test tiers, the way the spec's Stage 2 table says
(design/specs/2026-11-13-maturation-pipeline.md §4 Stage 2). No model. Every refusal carries its line, evidence, the smallest
fix and where it goes back to (owner 2026-11-12: a refusal carries its path to pass). Writes version/preflight.json and
prints the run time. A bar's meaning is never judged here: only whether what the table names is real.

    python3 design/concepts/GimmeSomeSlack/version/preflight_throwaway.py
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

T0 = time.time()
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(REPO)
C = "design/concepts/GimmeSomeSlack/"
G = "src/RimMandrake/GimmeSomeSlack/"
sys.path.insert(0, "src/RimMandrake/Utils")
sys.path.insert(0, "src/RimMandrake/rimflow")

table = json.load(open(C + "version/test_table.json"))
tree = json.load(open(C + "tree.json"))
rec = json.load(open(C + "record.json"))
scn = json.load(open(C + "scenes.json"))
TESTS, BARS = table["tests"], table["bars"]
checks, refusals = [], []
PLANT = os.environ.get("GSS_PREFLIGHT_PLANT") == "1"  # watch the guard go red: plant one fault per check, write nothing
EXTRA_TEXT = ""
if PLANT:
    BARS[0]["decides"].append("T_DOES_NOT_EXIST")
    TESTS["T_CORE"]["reads"] = TESTS["T_CORE"]["reads"] + [G + "Source/NoSuchFile.cs"]
    TESTS["sc_settings"]["why_game"] = ""
    table["held_statements"] = table["held_statements"][1:]
    rec["inventory"][0]["impl_evidence"] = rec["inventory"][0]["impl_evidence"] + ["ITEM:GSS_NO_SUCH_ITEM_PLANTED"]
    EXTRA_TEXT = " RM_PlantedDefThatIsNotReal RM_PlantedStaleDef "


def check(name, ok, n, **refusal):
    checks.append(dict(check=name, result="pass" if ok else "refuse", n=n))
    if not ok:
        refusals.append(dict(check=name, **refusal))


# 1. the table holds exactly the owed bars (coverage_judge.required_ids)
import coverage_judge  # noqa: E402
owed = coverage_judge.required_ids(C, tree)
have = [b["id"] for b in BARS]
check("bars_match_required_ids", owed == have or set(owed) == set(have), len(owed),
      line="test_table.json bars", evidence="missing %s, extra %s" % (sorted(set(owed) - set(have)), sorted(set(have) - set(owed))),
      smallest_fix="regenerate the table", return_to="1")

# 2. every bar has a deciding test; 3. every test names a stage the spec knows
nodec = [b["id"] for b in BARS if not b["decides"]]
check("every_bar_has_a_test", not nodec, len(BARS), line=", ".join(nodec), evidence="decides is empty",
      smallest_fix="name a deciding test", return_to="1")
badstage = [t for t, v in TESTS.items() if v.get("stage") not in table["stages"]]
check("every_test_names_its_stage", not badstage, len(TESTS), line=", ".join(badstage), evidence="stage not in 2, 4-5, 6, 8",
      smallest_fix="give each its stage", return_to="1")
unknown = sorted({t for b in BARS for t in b["decides"] + b["supports"] if t not in TESTS})
check("every_cited_test_is_listed", not unknown, sum(len(b["decides"]) + len(b["supports"]) for b in BARS),
      line=", ".join(unknown), evidence="a bar cites a test id the tests list lacks", smallest_fix="list it", return_to="1")

# 4. every game-stage test says why the game is needed; every full-list test says why the full list
game = {t: v for t, v in TESTS.items() if v["stage"] in ("6", "8")}
nowhy = sorted(t for t, v in game.items() if not (v.get("why_game") or "").strip())
check("game_tests_say_why", not nowhy, len(game), line=", ".join(nowhy), evidence="why_game empty",
      smallest_fix="write why an offline test cannot decide it", return_to="1")
full = {t: v for t, v in TESTS.items() if v.get("kind") == "live_full"}
nofull = sorted(t for t, v in full.items() if not (v.get("why_full_list") or "").strip())
check("full_list_tests_say_why", not nofull, len(full), line=", ".join(nofull), evidence="why_full_list empty",
      smallest_fix="write why the minimal list cannot decide it", return_to="1")

# 5. every named file is real (test files, reads, entry points); a NEW test's file may be absent, its folder may not
missing_files, missing_dirs = [], []
for t, v in TESTS.items():
    paths = ([v["file"]] if v.get("file") else []) + list(v.get("reads") or [])
    for p in paths:
        if os.path.exists(p):
            continue
        if v.get("new") and p == v.get("file"):
            if not os.path.isdir(os.path.dirname(p)):
                missing_dirs.append("%s: %s" % (t, p))
            continue
        missing_files.append("%s: %s" % (t, p))
check("named_files_exist", not missing_files and not missing_dirs, sum(1 + len(v.get("reads") or []) for v in TESTS.values()),
      line="; ".join((missing_files + missing_dirs)[:12]) + (" (+%d)" % (len(missing_files) - 12) if len(missing_files) > 12 else ""),
      evidence="%d paths named by tests do not exist" % (len(missing_files) + len(missing_dirs)),
      smallest_fix="correct the path in the table, or the test it names", return_to="1")
LEDGER_IDS = set()
for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"):
    LEDGER_IDS.update(re.findall(r'"id":"([^"]+)"', open(f, encoding="utf-8").read()))
ev_missing = []
for i in rec["inventory"]:
    for e in i.get("impl_evidence") or []:
        if e.startswith("ITEM:"):
            iid = e[5:]
            if iid not in LEDGER_IDS:  # many old items live only in the ledger, with no prose file
                ev_missing.append("%s: %s" % (i["id"], e))
        elif not os.path.exists(re.sub(r":\d+$", "", e)):  # a path may carry :line
            ev_missing.append("%s: %s" % (i["id"], e))
check("inventory_evidence_exists", not ev_missing, sum(len(i.get("impl_evidence") or []) for i in rec["inventory"]),
      line="; ".join(ev_missing), evidence="record.json impl_evidence names a path or item that does not exist",
      smallest_fix="correct the reference in record.json (a fact, not a bar)", return_to="1")

# 6. built mod: every in-game test that DECIDES a bar has its entry in code ("Built: runs", his card 2026-11-13)
deciders = {t for b in BARS for t in b["decides"] if t in TESTS}  # an unlisted id is refused above
absent = sorted(t for t in deciders if TESTS[t]["kind"] != "offline" and TESTS[t]["kind"] != "look" and not TESTS[t].get("entry_exists"))
check("built_mod_decider_entries_exist", not absent, len([t for t in deciders if TESTS[t]["kind"] not in ("offline", "look")]),
      line=", ".join(absent), evidence="scenes.json names entry points that are not defined: 'def <entry>(' occurs 0 times in the named file",
      smallest_fix="Stage 3 builds the entry points (item GSS_SCENES_BUILD_EVERY_CORD_A_FOIL, live), each red first",
      return_to="3")
spec_off = sorted(t for t in deciders if TESTS[t]["kind"] == "offline" and not TESTS[t]["runs_today"].get("ran"))
check("built_mod_offline_deciders_run", not spec_off, len([t for t in deciders if TESTS[t]["kind"] == "offline"]),
      line=", ".join(spec_off), evidence="specified at this lock, not built", smallest_fix="Stage 3 builds them, red first",
      return_to="3")
red = sorted(t for t, v in TESTS.items() if v["kind"] == "offline" and v["runs_today"].get("ran") and v["runs_today"].get("result") != "PASS")
check("built_offline_tests_green", not red, sum(1 for v in TESTS.values() if v["kind"] == "offline" and v["runs_today"].get("ran")),
      line=", ".join(red), evidence="ran red today" + "".join("; %s is filed as %s" % (t, TESTS[t]["known_red"]) for t in red if TESTS[t].get("known_red")),
      smallest_fix="fix the mod, or (a flawed criterion) the neutral fixer repairs the bar with the owner; never loosen the test",
      return_to="3")

# 7. every named def is real: def-like names in the bars' own text, against the def dump, our Defs XML and our C# symbols
# the tree's `coverage` block is the judge program's stamp (signed_by CoverageJudge), not bar text
txt = open(C + "scenes.json").read() + json.dumps({k: v for k, v in tree.items() if k != "coverage"}) + open(C + "record.json").read() + EXTRA_TEXT
toks = sorted(set(re.findall(r"\b(?:RM|RSW|RUT)_[A-Za-z0-9_]+\b|\b[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+\b", txt)))
import refresh  # noqa: E402
dump_dir = os.path.join(refresh.D_DUMP, "defs")
t_dump = time.time()
dump_names, dump_ours = set(), set()
for f in glob.glob(os.path.join(dump_dir, "*.json")):
    with open(f, encoding="utf-8") as fh:
        for n, pk in re.findall(r'"defName":"([^"]+)"[^{}]*?"packageId":"([^"]+)"', fh.read()):
            dump_names.add(n)
            if pk.lower().startswith("mandrake."):
                dump_ours.add(n)
t_dump = time.time() - t_dump
xml_names = set()
for f in glob.glob(G + "Defs/**/*.xml", recursive=True) + glob.glob(G + "Patches/**/*.xml", recursive=True):
    xml_names.update(re.findall(r"<defName>([^<]+)</defName>", open(f, encoding="utf-8").read()))
# Stale-dump hole (lesson 20261114T194216Z, Pyrelands run): the dump is a capture of 2026-11-12, so a def of OURS the repo has
# since deleted still reads as real there. A name the dump attributes to a mandrake.* mod, or any RM_/RSW_/RUT_ name, counts as a
# def only if the repo's CURRENT XML (every mod under src/RimMandrake) defines it.
repo_names = set()
for f in glob.glob("src/RimMandrake/**/*.xml", recursive=True):
    try:
        repo_names.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", open(f, encoding="utf-8", errors="replace").read()))
    except OSError:
        pass
if PLANT:
    dump_names.add("RM_PlantedStaleDef")
    dump_ours.add("RM_PlantedStaleDef")
src = " ".join(open(f, encoding="utf-8").read() for f in glob.glob(G + "Source/**/*.cs", recursive=True))
src += " ".join(open(f, encoding="utf-8").read() for f in glob.glob("src/RimMandrake/FlowWorks/Source/**/*.cs", recursive=True))
files = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(G + "**/*", recursive=True)}
WORDS = {"GimmeSomeSlack", "FlowWorks", "RimMandrake", "MessyConduit", "SelfTest", "StarWarsJawa"}
cls = {}
for tok in toks:
    ours = tok in dump_ours or re.match(r"(?:RM|RSW|RUT)_", tok)
    if tok in xml_names or tok in repo_names:
        cls[tok] = "def"
    elif tok in dump_names and not ours:
        cls[tok] = "def"
    elif tok in dump_names and ours:
        cls[tok] = "STALE_DUMP_DEF"  # ours in the 2026-11-12 dump, gone from the repo: refused below
    elif tok in WORDS:
        cls[tok] = "name"
    elif tok in files:
        cls[tok] = "file"
    elif re.search(r"\b%s\b" % re.escape(tok), src):
        cls[tok] = "csharp"
    elif tok.startswith("RM_") and re.match(r"RM_[a-z]", tok[:4]):
        cls[tok] = "save_or_id"
    else:
        cls[tok] = "UNKNOWN"
unk = sorted(t for t, c in cls.items() if c in ("UNKNOWN", "STALE_DUMP_DEF"))
check("named_defs_and_symbols_real", not unk, len(toks), line=", ".join(("%s (%s)" % (t, cls[t])) for t in unk),
      evidence="named in tree/scenes/record; not a defName in the dump (%d names, capture %s) or our Defs, not a C# symbol of GSS "
               "or FlowWorks, not a GSS file; STALE_DUMP_DEF = a def of ours the dump holds but no repo XML defines now" % (len(dump_names), os.path.basename(refresh.D_DUMP)),
      smallest_fix="correct the name in the text (a fact) or say what it is", return_to="1")
ours_not_in_dump = sorted(n for n in xml_names if n not in dump_names)
checks.append(dict(check="our_defs_in_dump", result="note", n=len(xml_names),
                   note="%d of our %d defNames are absent from the dump (dump predates them, or they failed to load): %s"
                        % (len(ours_not_in_dump), len(xml_names), ", ".join(ours_not_in_dump[:10]))))

# 8. every named mod is real and on the tier its in-game tests run on
import modset_builder as MB  # noqa: E402
tier = MB.TIERS["gimmesomeslack"]
pkg = {}
for f in glob.glob("src/RimMandrake/*/About/About.xml"):
    m = re.search(r"<packageId>([^<]+)</packageId>", open(f, encoding="utf-8").read())
    if m:
        pkg[f.split("/")[2]] = m.group(1).lower()
need_fw = sorted(s["id"] for s in scn["scenes"] if "FlowWorks" in json.dumps(s.get("start", "")))
# a scene's tier: test_table.json's "tier" on its test, else the mod's own tier
def tier_of(sid):
    return MB.TIERS.get((TESTS.get(sid) or {}).get("tier") or "gimmesomeslack")
if PLANT:
    need_fw = need_fw + ["sc_planted_fw_scene"]
lack_fw = [s for s in need_fw if not tier_of(s) or pkg.get("FlowWorks") not in [w.lower() for w in tier_of(s)["want"]]]
fw_in = not lack_fw
check("named_mods_on_the_tier", fw_in or not need_fw, len(need_fw), line=", ".join(lack_fw),
      evidence="these scenes stage FlowWorks content (start text names FlowWorks); the tier each runs on (test_table.json "
               "'tier', default 'gimmesomeslack') does not load %s" % pkg.get("FlowWorks"),
      smallest_fix="name the tier each of these scenes runs on (a GSS+FlowWorks tier exists? if not, add one), or drop the "
                   "FlowWorks part to a FlowWorks-side test", return_to="1")
check("tier_loads_all_dlc", bool(tier.get("dlc")), 1, line="gimmesomeslack tier", evidence="dlc flag off",
      smallest_fix="set dlc True", return_to="1")
check("mod_packageid_on_tier", pkg.get("GimmeSomeSlack") in [w.lower() for w in tier["want"]], 1,
      line="gimmesomeslack tier", evidence="GSS packageId %s not wanted" % pkg.get("GimmeSomeSlack"),
      smallest_fix="add it", return_to="1")

# 9. every held look statement for this mod has been placed
held_hits = []
for f in sorted(glob.glob("design/RimMandrake/validation_holding/owner_look_defects_*.md")):
    for line in open(f, encoding="utf-8"):
        cols = [c.strip() for c in line.split("|")]
        # his words are column 2; the build column often says "+ GSS" for a FlowWorks row, which is not about this mod
        if line.startswith("|") and len(cols) > 3 and re.match(r"^[0-9]+[a-z]?$", cols[1]) and \
                re.search(r"\bGSS\b|Gimme ?Some ?Slack", cols[2]):
            held_hits.append((f, cols[1]))
placed = {(h["file"], str(h["row"])) for h in table["held_statements"]}
unplaced = [("%s#%s" % (os.path.basename(f), r)) for f, r in held_hits if (f, r) not in placed]
check("held_statements_placed", not unplaced, len(held_hits), line=", ".join(unplaced),
      evidence="a held row names GSS but the table places it nowhere", smallest_fix="place it on a bar and a test", return_to="1")
checks.append(dict(check="held_statements_without_a_bar", result="note", n=len(table["held_statements"]),
                   note="all three sit on cords_draw_under_things, the bar his card 2026-11-14 added"))

# 10. the locked bytes: current blobs against bars.md's pins
pins = re.findall(r"\| `(design/concepts/GimmeSomeSlack/[^`]+)` \| `([0-9a-f]{40})` \|", open(C + "version/bars.md").read())
drift = []
for p, blob in pins:
    cur = subprocess.run(["git", "hash-object", p], capture_output=True, text=True).stdout.strip()
    if cur != blob:
        drift.append(os.path.basename(p))
check("lock_pins_current", not drift, len(pins), line=", ".join(drift),
      evidence="these locked files differ from the blobs bars.md pins (his lock word, bf33322d77)",
      smallest_fix="a test-text correction is re-pinned with a journal line; a changed bar is a new version",
      return_to="1")

out = dict(mod="GimmeSomeSlack", version="0.1.0", ran_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           seconds=round(time.time() - T0, 2), dump_read_seconds=round(t_dump, 2), dump=refresh.D_DUMP,
           by="design/concepts/GimmeSomeSlack/version/preflight_throwaway.py (throwaway, no model)",
           verdict="refuse" if refusals else "pass", checks=checks, refusals=refusals,
           name_classes={c: sorted(t for t, k in cls.items() if k == c) for c in sorted(set(cls.values()))})
if not PLANT:
    json.dump(out, open(C + "version/preflight.json", "w"), indent=1)
for c in checks:
    print("%-34s %-7s n=%s" % (c["check"], c["result"], c["n"]))
print("verdict %s, %d refusals, %.1f s (dump read %.1f s)" % (out["verdict"], len(refusals), out["seconds"], t_dump))
