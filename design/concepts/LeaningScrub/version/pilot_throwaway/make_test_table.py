#!/usr/bin/env python3
"""THROWAWAY (Maturation Pipeline Stage 2, LeaningScrub 0.1.0): build the test table.

Shape copied from design/concepts/Graffiti/version/pilot_throwaway/make_test_table.py. No bar-to-test pair is
hand-written here: every pair is read from the locked files.
  decides  = the scenes the signed coverage verdict names for the bar (coverage_verdict.json checklist parts)
             + scenes whose `requirement` names the leaf + scenes whose `exercises` name it + coverage_rest `by`
  supports = showcase-bundle scenes exercising it that do not decide it, and built offline tests whose file names
             the bar id or one of its deciding scenes literally
runs_today is MEASURED: every built offline test is run now (logs under
D:\\ClaudeWork\\rimmandrake\\leaningscrub_preflight\\runs); a scene's entry function is looked up in its file.

Writes design/concepts/LeaningScrub/version/test_table.json and test_table.md.
"""
import json, os, re, subprocess, sys, time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CON = ROOT / "design/concepts/LeaningScrub"
VER = CON / "version"
LS = "src/RimMandrake/LeaningScrub"
RUNS = Path("/mnt/d/ClaudeWork/rimmandrake/leaningscrub_preflight/runs")
HELD = [("design/RimMandrake/validation_holding/owner_look_defects_2026-11-12.md", 26)]

tree = json.loads((CON / "tree.json").read_text())
LEAVES = {l["id"]: l for l in tree["leaves"]}
record = json.loads((CON / "record.json").read_text())
INV = {i["id"]: i for i in record["inventory"]}
scn = json.loads((CON / "scenes.json").read_text())
SCENES = {s["id"]: s for s in scn["scenes"]}
cov = json.loads((CON / "coverage_verdict.json").read_text())
LOCKED = json.loads((VER / "locked_bars.json").read_text())["ids"]

T = {}

# ---- built offline tests (all exist today; each is run below) ----
OFFLINE = [
    ("T_SELFTEST", LS + "/selftest_leaningscrub.py", "the mod's main offline selftest"),
    ("T_FAUNA_BEHAVIOURS", LS + "/selftest_leaningscrub_fauna_behaviours.py", "fauna behaviour comps and defs"),
    ("T_GPT_FIXES", LS + "/selftest_leaningscrub_gpt_fixes.py", "regressions of the GPT review fixes"),
    ("T_SHIRREL_GLIDE", LS + "/selftest_leaningscrub_shirrel_glide.py", "shirrel glide flight defs"),
    ("T_SITE", LS + "/selftest_leaningscrub_site.py", "the test-site spec and staging helpers"),
    ("T_SOUNDSCAPE", LS + "/selftest_scrub_soundscape.py", "wind soundscape defs"),
    ("T_WILDLIFE_ZERO_PATHS", LS + "/selftest_scrub_wildlife_zero_paths.py", "wildlife spawn paths never zero"),
    ("T_WIND", LS + "/selftest_scrub_wind.py", "wind states, lean heading and gale rules"),
    ("T_SHED_PROBE", LS + "/selftest_sweetline_shed_probe.py", "the sweetline shed probe's verdict logic"),
    ("T_FUZZ", "src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py", "kernel rules by fuzz and mutation"),
    ("T_LINT_DEFS", "src/RimMandrake/Utils/lint_leaningscrub_defs.py", "static clauses over the mod's defs"),
]
# Not a test here: LS/preflight_leaningscrub.py is the retired biomes_sprint round's readiness check. Its red rows on
# 2026-11-16 were O-DEPLOY (the deployed composite differs from src: deploy state, not the build spec) and O-MANIFEST
# (no sprint manifest: the sprint is retired). It decides and supports no bar of 0.1.0.
for tid, f, obs in OFFLINE:
    T[tid] = dict(id=tid, kind="offline", stage="4-5", file=f, entry=None, observes=obs, reads=[f],
                  command="python3 " + f, new=False, item=None, defs=[], symbols=[], mods=[])


# ---- one test per scene; its kind from the tiers of the leaves it is required for ----
def scene_kind(sc):
    tiers = {LEAVES[r]["tier_proposed"] for r in (sc.get("requirement") or []) if r in LEAVES}
    if tiers and tiers <= {"offline"}:
        return "offline"
    if any("full list" in s.lower() for s in sc.get("start", [])):
        return "live_full"
    return "live_minimal"


def entry_exists(path, entry):
    src = (ROOT / path).read_text(errors="replace") if (ROOT / path).exists() else ""
    return bool(re.search(r"^def %s\(" % re.escape(entry), src, re.M))


DEC = defaultdict(list)
SUP = defaultdict(list)


def add(d, bar, tid):
    if tid not in d[bar]:
        d[bar].append(tid)


for c in cov["checklist"]:
    for p in c.get("parts", []):
        if p.get("scene"):
            add(DEC, c["id"], p["scene"])
for sid, sc in SCENES.items():
    for r in (sc.get("requirement") or []) + (sc.get("exercises") or []):
        add(DEC, r, sid)
for cr in scn.get("coverage_rest", []):
    for by in cr["by"]:
        add(DEC, cr["capability"], by)
for sh in scn.get("showcases", []):
    for x in sh["exercises"]:
        for sid in sh["scenes"]:
            if sid not in DEC[x]:
                add(SUP, x, sid)


def why_game_for(sid, sc):
    """The tier_reason of a live leaf the scene is required for, else of a live leaf it decides, else (an exploration
    or interaction scene on inventory rows only) a reason the table maker writes from the scene's own locked kind,
    question and features, marked why_game_by so the Stage 4 challenger knows to judge it."""
    cands = list(sc.get("requirement") or []) + [b for b in LOCKED if sid in DEC.get(b, [])]
    for r in cands:
        lf = LEAVES.get(r)
        if lf and (lf.get("tier_proposed") or "") in ("live_minimal", "live_full", "quicktest") and lf.get("tier_reason"):
            return lf["tier_reason"], r
    if sc.get("kind") == "exploration" and sc.get("question"):
        return ("an exploration of the running game, never acceptance (scenes.json scene_policy); its open question, "
                "'%s', has no offline model to ask" % sc["question"][:160]), "steward"
    if sc.get("kind") == "interaction" and sc.get("features"):
        return ("an interaction: %s acting together on one live map; each rule alone has its own test, the joint "
                "behaviour exists only in the running game" % ", ".join(sc["features"])), "steward"
    return "", None


for sid, sc in SCENES.items():
    f, entry = sc["entry_point"].split("::")
    kind = scene_kind(sc)
    why, leaf = ("", None) if kind == "offline" else why_game_for(sid, sc)
    exp = sc.get("expect", "")
    T[sid] = dict(id=sid, kind=kind, stage="4-5" if kind == "offline" else "6", scene_kind=sc.get("kind"),
                  file=f, entry=entry, observes=("; ".join(exp) if isinstance(exp, list) else str(exp))[:400],
                  reads=[f], command=("python3 %s %s" % (f, entry)) if kind == "offline" else "bridge: %s %s" % (f, entry),
                  why_game=why, why_game_from_leaf=leaf, why_full_list="", entry_exists=entry_exists(f, entry),
                  item=sc.get("entry_point_item") or None, scene_status=sc.get("status"), hold=sc.get("hold"),
                  new=False, defs=[], symbols=[], mods=["mandrake.rm.leaningscrub"])

T["LOOK_STAGE8"] = dict(id="LOOK_STAGE8", kind="look", stage="8", file=None, entry=None, observes="the owner walks the mod",
                        reads=[], command="owner walk", new=False, item=None, defs=[], symbols=[], mods=[],
                        runs_today={"ran": False, "why": "Stage 8: the owner's own walk"})

# built offline tests support every bar whose id, or one of whose deciding scenes, the test file names literally
for tid, f, _ in OFFLINE:
    src = (ROOT / f).read_text(errors="replace")
    for b in LOCKED:
        if re.search(r"\b%s\b" % re.escape(b), src) or any(re.search(r"\b%s\b" % re.escape(s), src) for s in DEC[b]):
            add(SUP, b, tid)

# held look statements: the placement IS the ingest
HELD_PLACE = {26: (["biome_cast"], ["sc_native_cast", "LOOK_STAGE8"],
                   "a question, not a defect: the dinosaur he saw in big pit BP3 is RM_Segnosaurus, LeaningScrub's absorbed "
                   "fauna (RM_Absorbed_Segnosaurus.xml); the pit-site wildlife clear landed a09040a09e; the cast's presence "
                   "and natural generation are what sc_native_cast decides, and he judges whether it belongs at the walk")}


for _n, (_bars, _tests, _) in HELD_PLACE.items():
    for _b in _bars:
        for _t in _tests:
            if _t not in DEC[_b]:
                add(SUP, _b, _t)


def held_rows():
    rows = []
    for path, n in HELD:
        for line in (ROOT / path).read_text().splitlines():
            m = re.match(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|", line)
            if m and int(m.group(1)) == n:
                bars, tests, note = HELD_PLACE[n]
                rows.append(dict(source="%s row %d" % (path, n), row=n, text=m.group(2)[:300],
                                 speaker="owner (verbatim in the source row)", bars=bars, tests=tests, note=note))
    return rows


# ---- measure runs_today ----
def run_offline(t):
    RUNS.mkdir(parents=True, exist_ok=True)
    log = RUNS / (Path(t["file"]).stem + ".txt")
    t0 = time.time()
    try:
        p = subprocess.run(["python3", t["file"]], cwd=ROOT, capture_output=True, text=True, timeout=500)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or "") if isinstance(e.stdout, str) else "", "timeout"
    log.write_text(out)
    lines = [l for l in out.splitlines() if l.strip()]
    return {"ran": True, "rc": rc, "seconds": round(time.time() - t0, 1), "last": lines[-1][:200] if lines else "",
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "log": str(log),
            "result": "PASS" if rc == 0 else "FAIL"}


for t in T.values():
    if t["kind"] == "offline" and not t.get("entry"):
        t["runs_today"] = run_offline(t)
        print("ran", t["id"], t["runs_today"]["result"], t["runs_today"]["seconds"], "s", flush=True)
    elif t.get("entry"):
        t["runs_today"] = {"ran": False, "entry_exists": t["entry_exists"],
                           "why": ("entry present; a scene is run at its stage" if t["entry_exists"] else
                                   "entry not written yet: Stage 3 work (%s)" % t.get("item"))}


def runnable(tid):
    t = T[tid]
    if t.get("entry"):
        return bool(t["entry_exists"]) and not t.get("known_red")
    if t["kind"] == "offline":
        return bool(t["runs_today"].get("ran")) and t["runs_today"].get("result") == "PASS"
    return False


ORDER = {"4-5": 1, "6": 2, "8": 3}
held = held_rows()
bars = []
for bid in LOCKED:
    src = "tree" if bid in LEAVES else "record"
    dec, sup = DEC.get(bid, []), [x for x in SUP.get(bid, []) if x not in DEC.get(bid, [])]
    offd = [d for d in dec if T[d]["kind"] == "offline"]
    bars.append(dict(
        id=bid, source=src,
        kind=(LEAVES[bid].get("tier_proposed") if src == "tree" else "inventory"),
        scope=(INV[bid].get("scope") if src == "record" else None),
        proves_at=max((T[d]["stage"] for d in dec), key=lambda s: ORDER[s]) if dec else None,
        decides=dec, supports=sup, held=[r["row"] for r in held if bid in r["bars"]], offline_decides=offd,
        offline_green_today=bool(offd) and all(runnable(d) for d in offd),
        every_decider_runnable_today=bool(dec) and all(runnable(d) for d in dec),
        any_test_runnable_today=any(runnable(x) for x in dec + sup)))

out = dict(mod="LeaningScrub", version="0.1.0", made=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           made_by="design/concepts/LeaningScrub/version/pilot_throwaway/make_test_table.py (throwaway, no model)",
           stages={"4-5": "offline (blind)", "6": "in game", "8": "owner walk"},
           rule="a bar passes when every test in decides passes; supports adds evidence and decides nothing; "
                "proves_at is the highest stage among the deciders",
           pairs_from="coverage_verdict.json checklist parts; scenes.json requirement, exercises, coverage_rest, showcases",
           known_red={},
           held_statements=held,
           held_note="validation_holding names LeaningScrub in one row (owner_look_defects_2026-11-12.md row 26); "
                     "no other file or row names it",
           tests=T, bars=bars)

if __name__ == "__main__":
    (VER / "test_table.json").write_text(json.dumps(out, indent=1) + "\n")
    off_built = [t for t in T.values() if t["kind"] == "offline" and not t.get("entry")]
    ent = [t for t in T.values() if t.get("entry")]
    md = ["# LeaningScrub 0.1.0 test table (read view of test_table.json)", "",
          "Made by `pilot_throwaway/make_test_table.py`, %s. A bar passes when every deciding test passes. "
          "Every bar-to-test pair is read from the locked files (%s); none is hand-written." % (out["made"], out["pairs_from"]), "",
          "## Counts", "",
          "- bars: %d (locked: %d)" % (len(bars), len(LOCKED)),
          "- tests: %d (%d built offline, %d scene tests, %d look)" % (
              len(T), len(off_built), len(ent), sum(1 for t in T.values() if t["kind"] == "look")),
          "- scene entries present: %d, absent (Stage 3 work): %d" % (
              sum(1 for t in ent if t["entry_exists"]), sum(1 for t in ent if not t["entry_exists"])),
          "- built offline green today: %d, red: %d" % (
              sum(1 for t in off_built if t["runs_today"]["result"] == "PASS"),
              sum(1 for t in off_built if t["runs_today"]["result"] != "PASS")),
          "- bars with every decider runnable today: %d" % sum(1 for b in bars if b["every_decider_runnable_today"]),
          "- bars with no deciding test: %d" % sum(1 for b in bars if not b["decides"]), "",
          "## Bars", "", "| bar | scope | proves at | decides | supports | held | runnable today |", "|---|---|---|---|---|---|---|"]
    for b in bars:
        md.append("| %s | %s | %s | %s | %s | %s | %s |" % (b["id"], b["scope"] or b["kind"], b["proves_at"] or "-",
                  ", ".join(b["decides"]) or "**none**", ", ".join(b["supports"]) or "-",
                  ", ".join(map(str, b["held"])) or "-", "yes" if b["every_decider_runnable_today"] else "no"))
    md += ["", "## Tests", "", "| test | kind | stage | file::entry | today | item |", "|---|---|---|---|---|---|"]
    for t in T.values():
        rt = t.get("runs_today", {})
        today = rt.get("result") or ("entry present" if t.get("entry_exists") else
                                      ("entry absent" if t.get("entry") else rt.get("why", "")))
        md.append("| %s | %s | %s | %s | %s | %s |" % (t["id"], t["kind"], t["stage"],
                  (t["file"] or "-") + ("::" + t["entry"] if t.get("entry") else ""), today, t.get("item") or "-"))
    md += ["", "## Held statements placed", "", "| source row | bars | tests | note |", "|---|---|---|---|"]
    for r in held:
        md.append("| %s | %s | %s | %s |" % (r["source"], ", ".join(r["bars"]), ", ".join(r["tests"]), r["note"]))
    (VER / "test_table.md").write_text("\n".join(md) + "\n")
    print("wrote", VER / "test_table.json", "and test_table.md")
