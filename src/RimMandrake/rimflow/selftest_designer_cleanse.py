#!/usr/bin/env python3
"""Selftest of the Designer Cleanse launcher (designer_cleanse.py; item
RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED; spec design/specs/2026-11-16-designer-cleanse-and-bar-definition.md
§4-§5; brief src/RimMandrake/rimflow/roles/designer_cleanse.md).

Spec §5.3: `check` refuses a proposal with a bar holding "30%", a bar with no `range`, a census row with no fate, an old
bar unmapped, a three-page owner_pages.md; accepts a minimal good one. Plus one row per further `check` rule of the
Conductor's brief (files, needed_by argument, every bar part, meetings, one whole bar, counts, unknown model, tickets),
the CASE (contents, no spend words), the owner's hold (allow-design), the quota gate (a refusal waits and retries, never
falls back to Claude), the launcher committing only the proposal folder, the review (different model, read-only, one
fix round, one second look, what remains printed on his pages, applyable false) and the fleet's order and resume.
Pure: temp dirs, fake effects; no agent, git or network."""
import copy
import json
import os
import re
import shutil
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
FAILS = []
N = [0]


def check(ok, msg):
    N[0] += 1
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


import designer_cleanse as DC      # noqa: E402  (red first: this import fails before the launcher exists)
import mod_owner_hold as MH        # noqa: E402

OLD = ["scene_observer", "pool_chemistry"]


def good():
    """A minimal proposal that passes every rule."""
    bars = {
        "bars": [
            {"id": "B1", "says": "A colonist walking into the forest sees the ground breathe a gas that harms him.",
             "meant": {"intent": "the gas is the place", "source": "delegated: from the root sentence in record.json",
                       "figurative": [{"word": "breathe", "stands_for": "vents that puff on their own",
                                       "accept": "a vent puffs a small cloud now and then, no rhythm"}]},
             "accept": ["a vent puffs a small cloud now and then, no rhythm", "gas pools in a hollow after dusk"],
             "reject": ["gas is a static overlay that never moves", "a vent that never puffs on a full map"],
             "lazy": "gas is a static overlay that never moves",
             "range": {"varies": "vent count 0 to 40, wind on/off, season", "left_out": "space maps: no gas there"},
             "sees": {"instrument": "a state read of gas cells over 3 days", "start": "fresh map, defaults",
                      "on": "every kept mechanic at default settings, weather unlocked",
                      "control": "the same read with vents removed shows no gas", "reset": "throwaway map"},
             "live_only": False, "touches": ["gas cells", "vents"]},
            {"id": "B2", "says": "The whole biome runs for a season with gas, forest and animals together and nothing floods.",
             "meant": {"intent": "one system", "source": "brief: the whole bar", "figurative": []},
             "accept": ["a season passes; gas comes and goes; the forest stands"],
             "reject": ["gas fills the map wall to wall by midsummer"],
             "lazy": "none: the words name the whole season and the flood that would fail it",
             "range": {"varies": "seeds 1-5, colony size 3 to 40", "left_out": "other biomes"},
             "sees": {"instrument": "live look", "start": "full map", "on": "everything", "control": "a reload mid-way",
                      "reset": "throwaway save", "live_only_why": "only the whole game runs every system at once"},
             "live_only": True, "touches": ["gas cells"]},
        ],
        "whole": "B2",
        "checks": [{"id": "C1", "what": "the vent def declares a puff interval"}],
        "rules": [{"id": "R1", "rule": "gas spreads by vanilla's gas grid", "touches": ["gas cells"]}],
        "meetings": [{"thing": "gas cells", "members": ["B1", "B2", "R1"], "holds_together": "unknown",
                      "why": "a season of puffs may flood", "model": "Season gas model"}],
        "old_bars": {"scene_observer": {"to": "dropped", "as": "", "why": "an instrument, not a bar"},
                     "pool_chemistry": {"to": "kept", "as": "B1", "why": "re-derived as the breathing ground"}},
    }
    census = {"rows": [
        {"id": "gas_vents", "what": "vents that puff", "built": "present", "evidence": "Source/Vent.cs",
         "proven": "stale", "called_by": "MapComponent", "serves": "the breathing ground", "fate": "signature",
         "why": "the signature", "needed_by": "", "ticket": ""},
        {"id": "warning_letter", "what": "a letter when gas rises", "built": "present", "evidence": "Defs/Letters.xml",
         "proven": "missing", "called_by": "GasTracker", "serves": "readability", "fate": "needed_by",
         "why": "without it the player cannot read the rising gas", "needed_by": "signature", "ticket": ""},
        {"id": "ritual", "what": "a vent ritual", "built": "present", "evidence": "Defs/Rituals.xml",
         "proven": "missing", "called_by": "nothing", "serves": "flavour", "fate": "next_version",
         "why": "an extra", "needed_by": "", "ticket": "T1"},
    ]}
    result = {"mod": "Demo", "run": "test", "outcome": "proposed", "signature": "the ground breathes gas",
              "counts": {"capabilities": 3, "kept": 2, "next_version": 1, "recommend_retire": 0, "old_bars": 2,
                         "bars": 2, "live_only_bars": 1, "checks": 1, "rules": 1, "unknown_pairs": 1, "models": 2,
                         "tickets": 1, "questions": 1}, "blocked_on": None}
    pages = ("# Demo\n\nCapabilities 3 before 3 after; bars 2; live-only bars 1.\n\n## Questions\n\n"
             "Q1. Should the ritual stay? Default: next version.\n")
    files = {
        "owner_pages.md": pages,
        "definition.md": "# Definition\n",
        "census.json": json.dumps(census),
        "ambiguities.md": "# Ambiguities\n",
        "bars.json": json.dumps(bars),
        "models.md": "# Models\n\n## Season gas model\nquestion...\n\n## Situation generator\n...\n",
        "next_version.md": "- ritual: a vent ritual. Not land, life or signature.\n",
        "tickets.md": "# Tickets\n\n## T1: switch off the ritual\nAcceptance test: with defaults the ritual def is absent.\n",
        "result.json": json.dumps(result),
    }
    return files


def lay(files, old=OLD, repo=None):
    repo = repo or tempfile.mkdtemp(prefix="dc_")
    concept = os.path.join(repo, "design", "concepts", "Demo")
    out = os.path.join(concept, "cleanse")
    os.makedirs(out, exist_ok=True)
    if old is not None:
        with open(os.path.join(concept, "tree.json"), "w") as f:
            json.dump({"leaves": [{"id": i} for i in old]}, f)
    for name, text in files.items():
        if text is None:
            continue
        with open(os.path.join(out, name), "w") as f:
            f.write(text)
    return out


def mutate(name, fn):
    files = good()
    if name.endswith(".json"):
        doc = json.loads(files[name])
        fn(doc)
        files[name] = json.dumps(doc)
    else:
        files[name] = fn(files[name])
    return files


def refused(files, rule, msg, old=OLD):
    refs, _stats = DC.check_dir(lay(files, old))
    hit = [r for r in refs if r["rule"] == rule]
    check(bool(hit) and all(r.get("would_pass") for r in hit), "%s -> refused as %s with would_pass (got %s)"
          % (msg, rule, sorted({r["rule"] for r in refs})))


def test_check():
    refs, stats = DC.check_dir(lay(good()))
    check(refs == [], "a minimal good proposal passes (refusals: %s)" % [r["what"] for r in refs])
    check(stats.get("bars") == 2 and stats.get("census_rows") == 3 and "page_words" in stats,
          "check prints what it read: %s" % stats)
    # spec §5.3
    refused(mutate("bars.json", lambda d: d["bars"][0].update(says="Gas covers 30% of the map by dusk.")),
            "bar_number", "a bar holding 30%")
    refused(mutate("bars.json", lambda d: d["bars"][0].pop("range")), "bar_part", "a bar with no range")
    refused(mutate("census.json", lambda d: d["rows"][0].pop("fate")), "census_fate", "a census row with no fate")
    refused(mutate("census.json", lambda d: d["rows"][0].update(fate="maybe")), "census_fate", "a fate off the list")
    refused(mutate("bars.json", lambda d: d["old_bars"].pop("pool_chemistry")), "old_bar", "an old bar unmapped")
    refused(mutate("owner_pages.md", lambda t: t + ("word " * 1900)), "owner_pages_length", "a three-page owner_pages.md")
    # one row per further rule
    files = good()
    files["models.md"] = None
    refused(files, "files", "a file of the brief's table missing")
    refused(mutate("census.json", lambda d: d["rows"][0].update(built="maybe")), "census_row",
            "a census row whose built is off the list")
    refused(mutate("census.json", lambda d: d["rows"][0].update(id="")), "census_row", "a census row with no id")
    refused(mutate("census.json", lambda d: d["rows"][0].update(why="")), "census_row", "a census row with no why")
    files = good()
    files["census.json"] = "{not json"
    refused(files, "files", "an unparsable census.json")
    # a blocked run: only its pages and its result.json, with what it is blocked on
    files = {k: None for k in good()}
    files["owner_pages.md"] = "# Demo\n\nBlocked: the source folder is empty.\n"
    files["result.json"] = json.dumps({"mod": "Demo", "run": "t", "outcome": "blocked", "signature": "",
                                       "counts": {}, "blocked_on": "the source folder is empty"})
    refs, _ = DC.check_dir(lay(files))
    check(not refs, "a blocked run with its pages and what blocked it passes (refusals: %s)" % [r["what"] for r in refs])
    files["result.json"] = json.dumps({"mod": "Demo", "run": "t", "outcome": "blocked", "signature": "",
                                       "counts": {}, "blocked_on": ""})
    refused(files, "counts", "a blocked run that does not say what blocked it")
    refused(mutate("census.json", lambda d: d["rows"][1].update(why="")), "needed_by_argument",
            "a needed_by row with no argument")
    refused(mutate("census.json", lambda d: d["rows"][1].update(needed_by="")), "needed_by_argument",
            "a needed_by row naming nothing")
    for part, fn in (("says", lambda b: b.pop("says")),
                     ("meant source", lambda b: b["meant"].update(source="")),
                     ("figurative accept", lambda b: b["meant"]["figurative"][0].update(accept="")),
                     ("accept", lambda b: b.update(accept=[])),
                     ("reject", lambda b: b.update(reject=[])),
                     ("lazy", lambda b: b.pop("lazy")),
                     ("lazy not among reject", lambda b: b.update(lazy="a build nobody listed")),
                     ("lazy none without why", lambda b: b.update(lazy="none")),
                     ("range left_out", lambda b: b["range"].update(left_out="")),
                     ("sees instrument", lambda b: b["sees"].pop("instrument")),
                     ("sees start", lambda b: b["sees"].update(start="")),
                     ("sees on", lambda b: b["sees"].pop("on")),
                     ("sees control", lambda b: b["sees"].pop("control")),
                     ("touches", lambda b: b.update(touches=[]))):
        refused(mutate("bars.json", lambda d, fn=fn: fn(d["bars"][0])), "bar_part", "a bar missing %s" % part)
    refused(mutate("bars.json", lambda d: d["bars"][1].pop("live_only_why", None) or d["bars"][1]["sees"].pop(
        "live_only_why")), "bar_part", "a live-only bar with no reason nothing cheaper sees it")
    refused(mutate("bars.json", lambda d: d.update(meetings=[])), "meeting", "a thing shared by three with no meeting")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update(members=["B1", "B2"])), "meeting",
            "a meeting leaving out a rule that touches the thing")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update(holds_together="probably")), "meeting",
            "holds_together off the list")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update(holds_together="argued", why="")), "meeting",
            "an argued meeting with no argument")
    refused(mutate("bars.json", lambda d: d.update(whole="")), "whole", "no whole bar")
    refused(mutate("bars.json", lambda d: d["bars"][0].update(whole=True)), "whole", "two whole bars")
    refused(mutate("bars.json", lambda d: d["bars"][0]["accept"].append("the vent resolves more than one graphic variant")),
            "bar_number", "a variant count in an accept picture")
    refused(mutate("bars.json", lambda d: d["bars"][0]["reject"].append("a selftest covering every field of the vent def")),
            "bar_number", "'every field' in a reject picture")
    refused(mutate("bars.json", lambda d: d["bars"][0]["reject"].append("vents puff once every 2 hours")),
            "bar_number", "a bare number in a reject picture")
    refs, _ = DC.check_dir(lay(mutate("bars.json", lambda d: d["bars"][0]["sees"].update(start="3 colonists, day 1"))))
    check(not refs, "numbers in range and sees are legal (refusals: %s)" % [r["what"] for r in refs])
    refs, _ = DC.check_dir(lay(mutate("bars.json", lambda d: d["bars"][0].update(
        says="A colonist on a Design Version 0.1.0 map sees RM_Vent2 puff."))))
    check(not [r for r in refs if r["rule"] == "bar_number"], "a version string or a defName with a digit is no number")
    refused(mutate("result.json", lambda d: d["counts"].update(bars=3)), "counts", "result.json counting a bar too many")
    refused(mutate("result.json", lambda d: d["counts"].update(models=1)), "counts", "result.json miscounting models")
    refused(mutate("result.json", lambda d: d.update(outcome="done")), "counts", "an outcome off the list")
    refused(mutate("owner_pages.md", lambda t: t.replace("bars 2", "bars two")), "counts",
            "owner pages not stating result.json's bar count")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update(model="Gas flood model")), "unknown_model",
            "an unknown meeting naming a model models.md lacks")
    refused(mutate("census.json", lambda d: d["rows"][2].update(ticket="")), "ticket",
            "a built extra moved with no ticket")
    refused(mutate("tickets.md", lambda t: t.replace("Acceptance test: with defaults the ritual def is absent.", "")),
            "ticket", "a ticket with no acceptance test")
    # no concept folder: old_bars empty is right
    refs, _ = DC.check_dir(lay(mutate("bars.json", lambda d: d.update(old_bars={})) and
                               mutate("result.json", lambda d: d["counts"].update(old_bars=0)), old=None))
    files = good()
    b = json.loads(files["bars.json"])
    b["old_bars"] = {}
    files["bars.json"] = json.dumps(b)
    r = json.loads(files["result.json"])
    r["counts"]["old_bars"] = 0
    files["result.json"] = json.dumps(r)
    refs, _ = DC.check_dir(lay(files, old=None))
    check(not refs, "a mod with no concept tree passes with old_bars empty (refusals: %s)" % [x["what"] for x in refs])
    # GPT review 2026-11-16 (consult-20261116-230848): JSON null, the brief's other columns and parts, swapped page counts
    files = good()
    files["result.json"] = "null"
    refused(files, "counts", "a result.json holding JSON null")
    files = good()
    files["census.json"] = "null"
    refused(files, "census_fate", "a census.json holding JSON null")
    for col in ("evidence", "called_by", "serves"):
        refused(mutate("census.json", lambda d, col=col: d["rows"][0].pop(col)), "census_row", "a census row with no %s" % col)
    refused(mutate("bars.json", lambda d: d["bars"][0]["meant"].pop("intent")), "bar_part", "a bar missing meant.intent")
    refused(mutate("bars.json", lambda d: d["bars"][0]["sees"].pop("reset")), "bar_part", "a bar missing sees.reset")
    refused(mutate("owner_pages.md", lambda t: t.replace("Capabilities 3 before 3 after; bars 2; live-only bars 1.",
                                                         "Capabilities 2; bars 3; live-only bars 1.")), "counts",
            "his pages with the capability and bar counts swapped")
    for line in ("Capabilities: 3 before, 2 after; bars: 2 before, 2 after; live-only bars: 1.",
                 "3 capabilities, 2 bars and 1 live-only bar.",
                 "| Capabilities | 3 | 2 |\n| Bars | 4 | 2 |\n| Bars only the live game can decide | 1 |"):
        refs, _ = DC.check_dir(lay(mutate("owner_pages.md", lambda t, line=line: t.replace(
            "Capabilities 3 before 3 after; bars 2; live-only bars 1.", line))))
        check(not refs, "page counts stated as %r pass (refusals: %s)" % (line[:40], [x["what"] for x in refs]))
    # a malformed value anywhere in the JSON files is a refusal or a pass, never a crash
    base, n, crashed = good(), 0, []

    def paths(v, at=()):
        yield at
        if isinstance(v, dict):
            for k in v:
                yield from paths(v[k], at + (k,))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                yield from paths(x, at + (i,))
    for name in ("result.json", "census.json", "bars.json"):
        doc0 = json.loads(base[name])
        for at in list(paths(doc0)):
            for junk in (None, "", "x", 1, True, [], {}, ["x"], [1], {"x": 1}):
                doc = json.loads(base[name])
                if at:
                    tgt = doc
                    for k in at[:-1]:
                        tgt = tgt[k]
                    tgt[at[-1]] = junk
                else:
                    doc = junk
                files = dict(base, **{name: json.dumps(doc)})
                n += 1
                try:
                    DC.check_dir(lay(files))
                except Exception as e:      # noqa: BLE001
                    crashed.append("%s %s=%r: %s: %s" % (name, "/".join(map(str, at)), junk, type(e).__name__, e))
    check(not crashed and n > 1000, "check_dir on %d malformed variants (every JSON path x 10 junk values): %d crashed%s"
          % (n, len(crashed), (": " + "; ".join(crashed[:3])) if crashed else ""))
    # the reviewer's block on his pages is not counted against his two pages -- only when it IS the reviewer's
    rem = [dict(REF, evidence="reviewer words " * 600)]
    files = good()
    files["owner_pages.md"] = files["owner_pages.md"].rstrip() + "\n\n" + DC._still_refused_block(rem)
    files["review.json"] = json.dumps({"remaining": rem})
    refs, _ = DC.check_dir(lay(files))
    check(not refs, "the reviewer's still-refused block (exactly review.json's remaining) is not counted in the 950 "
          "words (%s)" % sorted({x["rule"] for x in refs}))
    files = good()
    files["owner_pages.md"] += "\n" + DC.STILL_REFUSED_HEAD + "\n\n" + ("author words " * 600)
    refs, _ = DC.check_dir(lay(files))
    check({"reviewer_block", "owner_pages_length"} <= {x["rule"] for x in refs},
          "an author's words under the reviewer's heading count, and the heading is refused (%s)"
          % sorted({x["rule"] for x in refs}))
    files["review.json"] = json.dumps({"remaining": [REF]})
    refs, _ = DC.check_dir(lay(files))
    check({"reviewer_block", "owner_pages_length"} <= {x["rule"] for x in refs},
          "a block that is not review.json's remaining word for word is the author's (%s)"
          % sorted({x["rule"] for x in refs}))
    # GPT review 2026-11-17 (a_launcherA): the shape SHAPE fixes, read strictly
    refused(mutate("tickets.md", lambda t: t + "\n## T2: another ticket\nno test line here\n"), "ticket",
            "a second ticket with no acceptance test (every ticket needs one, not only a switch-off ticket)")
    refused(mutate("tickets.md", lambda t: t.replace("Acceptance test: with defaults the ritual def is absent.",
                                                     "Acceptance test: none")), "ticket",
            "an acceptance test of `none` with no reason")
    refs, _ = DC.check_dir(lay(mutate("tickets.md", lambda t: t.replace(
        "Acceptance test: with defaults the ritual def is absent.", "**Acceptance test:** none, the def is deleted"))))
    check(not refs, "`**Acceptance test:** none, <reason>` passes (%s)" % sorted({x["rule"] for x in refs}))
    refused(mutate("bars.json", lambda d: d["old_bars"]["pool_chemistry"].update({"as": "B9"})), "old_bar",
            "an old bar kept as an id bars.json does not hold")
    refused(mutate("bars.json", lambda d: d["old_bars"]["pool_chemistry"].update({"to": "check", "as": "B1"})),
            "old_bar", "an old bar turned into a check named by a bar id")
    refs, _ = DC.check_dir(lay(mutate("bars.json", lambda d: d["old_bars"]["pool_chemistry"].update(
        {"to": "rule", "as": "R1"}))))
    check(not [x for x in refs if x["rule"] == "old_bar"], "an old bar turned into rule R1 resolves")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update({"model": "gas"})), "unknown_model",
            "an unknown meeting whose model is only a word inside a heading")
    refs, _ = DC.check_dir(lay(mutate("models.md", lambda t: t.replace("## Season gas model", "## M1: Season gas model")
                                      ) | {"bars.json": json.dumps(dict(json.loads(good()["bars.json"]), meetings=[
                                          dict(json.loads(good()["bars.json"])["meetings"][0], model="M1")]))}))
    check(not [x for x in refs if x["rule"] == "unknown_model"], "a model named by its heading's id resolves")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update({"why": ""})), "meeting",
            "an unknown meeting that does not say what is not known")
    for key in ("checks", "rules", "meetings"):
        refused(mutate("bars.json", lambda d, k=key: d.__setitem__(k, "none")), "shape", "bars.json %s as a string" % key)
        refused(mutate("bars.json", lambda d, k=key: d.pop(k)), "shape", "bars.json without %s" % key)
    refused(mutate("bars.json", lambda d: d["checks"][0].pop("what")), "shape", "a check with no what")
    refused(mutate("bars.json", lambda d: d["rules"][0].update({"touches": "gas cells"})), "shape",
            "a rule whose touches is a string")
    refused(mutate("bars.json", lambda d: d["meetings"][0].update({"members": [1, 2]})), "shape",
            "a meeting whose members are not text")
    refused(mutate("bars.json", lambda d: d.update({"old_bars": []})), "shape", "old_bars as a list")
    refused(mutate("bars.json", lambda d: d["bars"][0]["accept"].append(7)), "bar_part", "a picture that is not text")
    refused(mutate("bars.json", lambda d: d["bars"][0].update({"touches": ["gas cells", {"x": 1}]})), "bar_part",
            "a touches list holding an object")
    for junk in (True, 2.0):
        refused(mutate("result.json", lambda d, j=junk: d["counts"].update({"live_only_bars": j})), "counts",
                "a count of %r (not the integer)" % junk)
    out = lay(good())
    with open(os.path.join(out, "definition.md"), "wb") as f:
        f.write(b"# Definition \xff\xfe broken\n")
    refs, _ = DC.check_dir(out)
    check([x for x in refs if x["rule"] == "files" and x["where"] == "definition.md"],
          "a file that is not UTF-8 is refused by name, not a crash")
    out = lay(good())
    with open(os.path.join(out, "bars.json"), "w") as f:
        f.write("[" * 100000)
    try:
        refs, _ = DC.check_dir(out)
        check([x for x in refs if x["where"] == "bars.json"], "a bars.json nested too deep to parse is refused")
    except RecursionError:
        check(False, "a bars.json nested too deep to parse is refused (RecursionError)")


def fake_repo():
    repo = tempfile.mkdtemp(prefix="dc_repo_")
    os.makedirs(os.path.join(repo, "src", "RimMandrake", "rimflow", "roles"))
    os.makedirs(os.path.join(repo, "src", "RimMandrake", "DemoSrc"))
    os.makedirs(os.path.join(repo, "design", "concepts", "Demo"))
    os.makedirs(os.path.join(repo, "design", "specs"))
    os.makedirs(os.path.join(repo, "design", "RimMandrake"))
    os.makedirs(os.path.join(repo, "infrastructure", "state", "items", "closed"))
    entries = [{"key": "Eng", "source": "Eng", "group": "engine"},
               {"key": "Demo", "source": "DemoSrc", "group": "biome"},
               {"key": "Plain", "source": "Plain", "group": "biome"},
               {"key": "Pyrelands", "source": "Pyrelands", "group": "biome"},
               {"key": "Kit", "source": "Kit", "group": "kit"}]
    entries += [{"key": m, "source": m, "group": "biome"} for m in reversed(DC.CONCEPT_FIRST)]
    with open(os.path.join(repo, "src", "RimMandrake", "Biomes.compose.json"), "w") as f:
        json.dump({"entries": entries}, f)
    with open(os.path.join(repo, "src", "RimMandrake", "rimflow", "roles", "designer_cleanse.md"), "w") as f:
        f.write("# header\nnot pasted\n\n---\n\nYou are the Designer.\n")
    for p, t in (("CLAUDE.md", "rules"), ("design/RimMandrake/standing_rulings.md", "rulings"),
                 ("design/specs/demo_spec.md", "The Demo biome breathes."),
                 ("infrastructure/state/items/DEMO_FIX_THE_VENT.md", "x"),
                 ("infrastructure/state/items/closed/DEMO_OLD_THING.md", "x"),
                 ("infrastructure/state/items/OTHER_ITEM.md", "x")):
        with open(os.path.join(repo, p), "w") as f:
            f.write(t)
    with open(os.path.join(repo, "design", "concepts", "Demo", "tree.json"), "w") as f:
        json.dump({"leaves": [{"id": "pool_chemistry"}]}, f)
    return repo


SPEND = re.compile(r"\b(spend|budget|usd|dollars?|cost|time limit|deadline|minutes|hours)\b|\$\d", re.I)


def test_case():
    repo = fake_repo()
    case = DC.case_text(repo, "Demo")
    for want, what in (("src/RimMandrake/DemoSrc", "the source folder from the compose file"),
                       ("design/concepts/Demo/", "the concept folder"),
                       ("DEMO_FIX_THE_VENT", "an open ledger item of the mod"),
                       ("DEMO_OLD_THING", "a closed ledger item of the mod"),
                       ("design/specs/demo_spec.md", "a design doc that names it"),
                       ("CLAUDE.md", "the lore and rulings list"),
                       ("design/RimMandrake/standing_rulings.md", "a ruling file that exists"),
                       ("Eng", "the shared engines"),
                       ("design/concepts/Demo/cleanse/", "the output folder"),
                       ("designer_cleanse.py check design/concepts/Demo/cleanse", "the self-check command"),
                       ("ONLY inside", "write only inside the output folder"),
                       ("git", "no git command that writes"),
                       ("bridge", "no bridge")):
        check(want in case, "CASE names %s (%r)" % (what, want))
    check("OTHER_ITEM" not in case, "CASE lists no other mod's item")
    check("biome_rulings.md" not in case, "CASE drops a rulings file that does not exist")
    check("Pyrelands" not in case.split("Shared engines")[1].split("\n\n")[0] if "Shared engines" in case else False,
          "the engines list holds engines only")
    check(not SPEND.search(case), "CASE states no spend, budget or time limit (%s)" % (SPEND.search(case) or ""))
    plain = DC.case_text(repo, "Plain")
    check("no concept folder" in plain and "old_bars" in plain and "empty" in plain,
          "a mod with no concept folder: CASE says so plainly and that old_bars is empty")
    prompt = DC.prompt_for(repo, "Demo")
    check(prompt.startswith("You are the Designer.") and "not pasted" not in prompt and "CASE" in prompt,
          "the run's brief is everything below the --- line, then the CASE")


def test_owner_answers():
    """RIMMANDRAKE_FEED_CLEANSE_OWNER_ANSWERS_SCALD_CARD_SAT_UNREAD: the CASE names every ANSWERS_OWNER.md of the mod,
    by key, source folder or the named map; a folder no mod claims is reported by name; could not look is said."""
    repo = fake_repo()
    check("could not look" in DC.case_text(repo, "Demo") and DC.owner_answers(repo) is None,
          "answers: no answers folder reads 'could not look', never 'none'")
    base = os.path.join(repo, DC.ANSWERS_DIR)
    for n in ("Demo", "DemoSrc", "TheScaldFloor", "Stray"):
        os.makedirs(os.path.join(base, n))
        with open(os.path.join(base, n, DC.ANSWERS_FILE), "w") as f:
            f.write("# his answers\n")
    os.makedirs(os.path.join(base, "NoAnswers"))
    got, unclaimed = DC.owner_answers(repo)
    case = DC.case_text(repo, "Demo")
    check("%s/Demo/%s" % (DC.ANSWERS_DIR, DC.ANSWERS_FILE) in case and "%s/DemoSrc/%s" % (DC.ANSWERS_DIR, DC.ANSWERS_FILE)
          in case and "his words" in case, "answers: a mod with two folders (key and source) names both, as his words")
    check("none found under" in DC.case_text(repo, "Plain"), "answers: a mod with none says none found")
    check(unclaimed == ["Stray", "TheScaldFloor"], "answers: an unclaimed folder, and a mapped one whose mod is not in "
          "the compose file, are reported by name (%s)" % unclaimed)
    real = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    got, unclaimed = DC.owner_answers(real)
    folders = sorted(n for n in os.listdir(os.path.join(real, DC.ANSWERS_DIR))
                     if os.path.isfile(os.path.join(real, DC.ANSWERS_DIR, n, DC.ANSWERS_FILE)))
    named = sorted([p.split("/")[-2] for v in got.values() for p in v] + unclaimed)
    check(len(folders) >= 27 and named == folders, "answers: every one of the repo's %d answer folders is claimed by a "
          "mod or reported unclaimed" % len(folders))
    tb = DC.case_text(real, "TerminalBiomes")
    check(all("%s/%s/%s" % (DC.ANSWERS_DIR, n, DC.ANSWERS_FILE) in tb for n in ("TheScaldFloor", "TheChillFloor",
                                                                              "PropaneLakesShore")),
          "answers: Terminal Biomes' CASE names the Scald, Chill and Propane shore answers")


class FX:
    """Fake effects: records every call; scripted gate and agents."""

    def __init__(self, repo, gate=(), codex=(), claude=(), write=None, blinds=()):
        self.repo, self.calls, self.sleeps, self.published = repo, [], [], []
        self.gates, self.codexes, self.claudes = list(gate), list(codex), list(claude)
        self.blinds = list(blinds)     # the sealed cold-sort calls; default: every picture sorted accept
        self.blind_cwds = []
        self.write = write
        self.states = []

    def clone(self, mod):
        self.calls.append(("clone", mod))
        return self.repo

    def gate(self):
        self.calls.append(("gate",))
        if self.gates and self.gates.pop(0) == "refuse":
            raise DC.Refused("Codex weekly quota exceeds 90%")
        return {"codex.week_used_pct": {"v": 50, "m": "MEASURED"}}

    def _agent(self, kind, script, cwd, prompt, base, **kw):
        self.calls.append((kind, prompt, kw))
        out = script.pop(0) if script else {"is_error": False, "result": "done"}
        if callable(out):
            out = out(cwd, prompt)
        return out

    def _blind(self, kind, cwd, prompt, kw):
        self.calls.append(("blind", prompt, dict(kw, runner=kind)))
        self.blind_cwds.append((cwd, sorted(os.listdir(cwd))))
        out = self.blinds.pop(0) if self.blinds else accept_all
        return out(cwd, prompt) if callable(out) else out

    def codex(self, cwd, prompt, base, **kw):
        if "BLIND PICTURES:" in prompt:
            return self._blind("codex", cwd, prompt, kw)
        if self.write:
            self.write(cwd)
        return self._agent("codex", self.codexes, cwd, prompt, base, **kw)

    def claude(self, cwd, prompt, base, **kw):
        if "BLIND PICTURES:" in prompt:
            return self._blind("claude", cwd, prompt, kw)
        return self._agent("claude", self.claudes, cwd, prompt, base, **kw)

    def changed(self, cwd):
        out = []
        for d, _, fs in os.walk(cwd):
            for f in fs:
                p = os.path.relpath(os.path.join(d, f), cwd)
                if p.startswith("design/concepts/Demo/cleanse/") or p == "stray.txt":
                    out.append(p)
        return out

    def publish(self, cwd, paths, msg):
        self.published.append(list(paths))
        self.snap(cwd)
        return "abc1234"

    def snap(self, cwd=None):
        """The published proposal (what `git show HEAD:` would return): the folder's bytes now."""
        cwd = cwd or self.repo
        self.head = {}
        for p in self.changed(cwd):
            with open(os.path.join(cwd, p), encoding="utf-8") as f:
                self.head[p] = f.read()

    def head_text(self, cwd, rel):
        return getattr(self, "head", {}).get(rel)

    def sleep(self, s):
        self.sleeps.append(s)

    def status(self, mod, state, why=""):
        self.states.append((mod, state, why))

    def log(self, mod, line):
        pass

    def release(self, clone):
        return "kept"


def write_good(cwd):
    lay(good(), repo=cwd)
    with open(os.path.join(cwd, "stray.txt"), "w") as f:
        f.write("an agent wrote outside its folder")


def holds_file(mods, allow=()):
    p = os.path.join(tempfile.mkdtemp(prefix="dc_hold_"), "mod_owner_hold.json")
    with open(p, "w") as f:
        json.dump({"holds": [dict({"mod": m, "date": "2026-11-16", "said": "stop"},
                                  **({"design_allowed": {"said": "go", "date": "2026-11-16"}} if m in allow else {}))
                             for m in mods]}, f)
    return p


def test_hold():
    p = holds_file(["Demo", "Other"])
    os.environ["RM_OWNER_HOLD_FILE"] = p
    try:
        fx = FX(fake_repo(), write=write_good)
        rec = DC.run_mod("Demo", fx, runner="codex")
        check(rec["state"] == "blocked" and "allow-design" in rec["why"] and ("clone", "Demo") not in fx.calls,
              "run refuses a held mod without allow-design and takes no clone (%s)" % rec)
        h = MH.allow_design("Demo", "implement the thing", path=p)
        check(h["design_allowed"]["said"] == "implement the thing", "allow-design writes his words on the hold row")
        hs = MH.load(p)
        check(MH.design_allowed(hs["Demo"]) and not MH.design_allowed(hs["Other"]) and "Demo" in hs,
              "the hold stays on builds; only the allowed row reads design-allowed")
        try:
            MH.allow_design("Nope", "x", path=p)
            check(False, "allow-design on an unheld mod refuses")
        except KeyError:
            check(True, "allow-design on an unheld mod refuses")
        try:
            MH.allow_design("Other", "  ", path=p)
            check(False, "allow-design refuses empty words")
        except ValueError:
            check(True, "allow-design refuses empty words")
        fx = FX(fake_repo(), write=write_good)
        rec = DC.run_mod("Demo", fx, runner="codex")
        check(rec["state"] == "proposed", "an allowed held mod runs (%s)" % rec)
    finally:
        os.environ.pop("RM_OWNER_HOLD_FILE", None)


def test_run():
    os.environ["RM_OWNER_HOLD_FILE"] = holds_file([])
    try:
        fx = FX(fake_repo(), gate=["refuse", "refuse"], write=write_good,
                codex=[{"is_error": True, "result": "You've hit your usage limit (usage_limit_reached)"},
                       {"is_error": False, "result": "done"}])
        rec = DC.run_mod("Demo", fx, runner="codex")
        kinds = [c[0] for c in fx.calls]
        check(rec["state"] == "proposed", "a run whose gate refused twice and whose agent hit quota once ends proposed (%s)"
              % rec.get("why"))
        check(len(fx.sleeps) == 3 and kinds.count("codex") == 2, "each quota refusal is a wait and a retry (%d waits, %d runs)"
              % (len(fx.sleeps), kinds.count("codex")))
        check("claude" not in kinds, "a quota refusal never falls back to Claude")
        raw = "an earlier quota warning\n" + "x" * 2100 + "\nfinal failure detail"
        repo = fake_repo()
        write_good(repo)
        effects = DC.Effects(DC.Status(repo))

        def broken_json(argv, *, stdout, **kw):
            stdout.write(raw)
            return DC.subprocess.CompletedProcess(argv, 1)

        with patch.object(DC.subprocess, "run", broken_json):
            answer = effects.claude(repo, "fixture", os.path.join(repo, "capture"))
        failed = FX(repo, claude=[answer])
        out = DC.run_mod("Demo", failed, runner="claude")
        check(not failed.sleeps, "an earlier quota warning outside the fallback search tail does not cause a retry")
        check(out["agent_errors"] == [raw], "the fallback agent error record keeps the whole output")
        prompt = [c for c in fx.calls if c[0] == "codex"][0][1]
        check(prompt.startswith("You are the Designer.") and "design/concepts/Demo/cleanse/" in prompt,
              "the agent gets the brief and the CASE")
        check(not [c for c in fx.calls if c[0] == "codex" and c[2].get("timeout")],
              "no wall-clock limit on a run")
        pub = fx.published[0] if fx.published else []
        check(pub and all(p.startswith("design/concepts/Demo/cleanse/") for p in pub) and "stray.txt" not in pub,
              "the launcher commits only the proposal folder (%s)" % pub)
        check("stray.txt" in json.dumps(rec.get("stray")), "a write outside the folder is recorded, not committed")
        # a shape refusal gets one fix pass with the refusals, then stands
        def write_bad(cwd):
            files = good()
            files["models.md"] = None
            lay(files, repo=cwd)
        fx = FX(fake_repo(), write=write_bad)
        rec = DC.run_mod("Demo", fx, runner="codex")
        runs = [c for c in fx.calls if c[0] == "codex"]
        check(len(runs) == 2 and "models.md" in runs[1][1] and rec["state"] == "blocked" and "self-check" in rec["why"],
              "a proposal refused by check gets ONE fix pass with the refusals, then stands refused (%s, %d runs)"
              % (rec["state"], len(runs)))
        check(not SPEND.search(runs[1][1].split("---")[-1][-3000:]), "the fix prompt states no spend")
    finally:
        os.environ.pop("RM_OWNER_HOLD_FILE", None)


def _items(prompt):
    return json.loads(prompt.split("BLIND PICTURES:")[1].split("END BLIND PICTURES")[0])


def accept_all(cwd, prompt):
    sort = [{"bar": it["bar"], "n": p["n"], "sorted": "accept"} for it in _items(prompt) for p in it["pictures"]]
    return {"is_error": False, "result": "```json\n" + json.dumps({"blind_sort": sort}) + "\n```"}


def sort_right(cwd, prompt):
    bars = {b["id"]: b for b in json.loads(good()["bars.json"])["bars"]}
    sort = [{"bar": it["bar"], "n": q["n"], "sorted": "accept" if q["text"] in bars[it["bar"]]["accept"] else "reject"}
            for it in _items(prompt) for q in it["pictures"]]
    return {"is_error": False, "result": json.dumps({"blind_sort": sort})}


def review_json(refusals):
    def make(cwd, prompt):
        return {"is_error": False, "result": "```json\n" + json.dumps({
            "refusals": refusals, "missed_capability": "looked, none", "loop_or_three_way": "looked, none"}) + "\n```"}
    return make


REF = {"head": "no_range", "where": "B1", "evidence": "B1 says gas but range names only one season",
       "would_pass": "a range naming wind and season", "smallest_fix": "add wind to B1.range.varies"}


def test_review():
    repo = fake_repo()
    lay(good(), repo=repo)
    fx = FX(repo, claude=[review_json([REF, dict(REF, head="number_in_bar", where="B2")]),
                          review_json([dict(REF, head="number_in_bar", where="B2")])])
    rec = DC.review_mod("Demo", fx, author="codex")
    kinds = [c[0] for c in fx.calls]
    check(kinds.count("claude") == 2 and kinds.count("codex") == 1,
          "a refusing review: ONE fix run by the author, ONE second look (claude %d, codex %d)"
          % (kinds.count("claude"), kinds.count("codex")))
    look = [c for c in fx.calls if c[0] == "claude"][0]
    check(look[2].get("model") == "opus" and look[2].get("tools") == "Read,Grep,Glob",
          "author Codex -> reviewer Claude Opus, read-only tools (%s)" % look[2])
    p = look[1]
    iw, isrc, iprop = p.find("HIS WORDS"), p.find("SOURCE"), p.find("THE PROPOSAL")
    check(0 <= iw < isrc < iprop, "the reviewer gets his words and the source before the proposal")
    check(not SPEND.search(p), "the reviewer is never told its spend (%s)" % (SPEND.search(p) or ""))
    out = os.path.join(repo, "design", "concepts", "Demo", "cleanse")
    rv = json.load(open(os.path.join(out, "review.json")))
    check(len(rv["rounds"]) == 2 and rv["rounds"][0]["refusals"] and rv["remaining"], "review.json holds both looks")
    check(any(s.get("bar") == "B1" and s.get("mismatch") for s in rv["rounds"][0]["stranger"]),
          "the blind sort is scored against the proposal's own labels")
    pages = open(os.path.join(out, "owner_pages.md")).read()
    check(DC.STILL_REFUSED_HEAD in pages and REF["evidence"] in pages,
          "what the second look still refuses is on his pages in the reviewer's words")
    res = json.load(open(os.path.join(out, "result.json")))
    check(res.get("applyable") is False and rec["state"] == "refused-after-second-look",
          "result.json applyable false after a refusing second look (%s)" % rec["state"])
    check(fx.published and all(x.startswith("design/concepts/Demo/cleanse/") for x in fx.published[-1]),
          "the review publishes only the proposal folder")
    # a clean first look: no fix, applyable true
    repo = fake_repo()
    lay(good(), repo=repo)
    fx = FX(repo, claude=[review_json([])], blinds=[sort_right])
    rec = DC.review_mod("Demo", fx, author="codex")
    kinds = [c[0] for c in fx.calls]
    res = json.load(open(os.path.join(repo, "design", "concepts", "Demo", "cleanse", "result.json")))
    check(kinds.count("claude") == 1 and "codex" not in kinds and res.get("applyable") is True
          and rec["state"] == "reviewed", "a clean first look: no fix round, applyable true (%s)" % rec["state"])
    # a refusal record missing its smallest fix is the reviewer's defect, not a refusal of the proposal
    bad = DC.validate_review({"refusals": [{"head": "no_range", "where": "B1", "evidence": "x", "would_pass": "y"}],
                              "blind_sort": [], "missed_capability": "looked, none", "loop_or_three_way": "x"})
    check(bad and "smallest_fix" in " ".join(bad), "a refusal record needs evidence, would_pass and smallest_fix")
    bad = DC.validate_review({"refusals": [dict(REF, head="i do not like it")], "blind_sort": [],
                              "missed_capability": "x", "loop_or_three_way": "x"})
    check(bad, "a refusal under a head off the spec's list is refused")
    check(DC.reviewer_for("claude")[0] == "codex" and DC.reviewer_for("codex") == ("claude", "opus"),
          "the reviewer is always on the other model")
    bad = DC.validate_review({"refusals": [dict(REF, head="stranger")], "blind_sort": [],
                              "missed_capability": "x", "loop_or_three_way": "x"})
    check(bad, "the reviewer may not write the launcher's own heads (stranger, self_check)")
    # a reviewer whose record is unreadable twice decides nothing: blocked, no review.json, nothing on his pages
    repo = fake_repo()
    lay(good(), repo=repo)
    fx = FX(repo, claude=[{"is_error": False, "result": "I liked it."}, {"is_error": False, "result": "Still no JSON."}])
    rec = DC.review_mod("Demo", fx, author="codex")
    out = os.path.join(repo, "design", "concepts", "Demo", "cleanse")
    kinds = [c[0] for c in fx.calls]
    check(rec["state"] == "blocked" and not os.path.exists(os.path.join(out, "review.json"))
          and os.path.exists(os.path.join(out, "review_attempt.json")) and "codex" not in kinds
          and kinds.count("claude") == 2 and DC.STILL_REFUSED_HEAD not in open(os.path.join(out, "owner_pages.md")).read(),
          "an unreadable reviewer: one retry, then blocked, no review.json, no author fix, his pages untouched (%s)"
          % rec["state"])
    check(not DC.done(repo, "Demo"), "resume looks again at a mod whose reviewer was unreadable")


def test_detector():
    """The bar-number detector over the regimes a bar's words can take: numerals, percentages, number words bar_rule
    reads, sentence ends, version strings and names with digits. Prints what it read."""
    hit = ["Gas covers 30% of the map.", "It lasts 30.", "at least 2 vents", "-5 degrees", "1,5 tiles", "ten per cent",
           "more than one graphic variant", "every field is filled", "3 %", "x 30, then"]
    miss = ["RM_Vent2 burns", "version 0.1.0 ships", "bar B1 holds", "a vent glows at dusk", "Q1 asks", "gas2go"]
    got_hit = [s for s in hit if DC.bar_number(s)]
    got_miss = [s for s in miss if DC.bar_number(s)]
    print("detector: read %d texts; %d of %d numbered caught, %d of %d names and versions passed"
          % (len(hit) + len(miss), len(got_hit), len(hit), len(miss) - len(got_miss), len(miss)))
    check(len(got_hit) == len(hit), "every numbered text is caught (missed: %s)" % sorted(set(hit) - set(got_hit)))
    check(not got_miss, "names with digits and version strings pass (caught: %s)" % got_miss)


def test_fleet():
    repo = fake_repo()
    order = DC.fleet_order(repo, but=["Pyrelands"])
    check("Pyrelands" not in order and "Eng" not in order and "Kit" not in order, "fleet: biomes only, Pyrelands out")
    check(order.index("Demo") == len(DC.CONCEPT_FIRST), "fleet: the other biomes follow the six (%s)" % order)
    order = DC.fleet_order(repo, but=["Pyrelands"], only=["Plain"])
    check(order == ["Plain"], "fleet --only narrows the list")
    order = DC.fleet_order(repo, but=["Pyrelands"])
    check(order[:6] == list(DC.CONCEPT_FIRST) and len(order) == len(set(order)),
          "the six first in the Conductor's order though the compose file lists them reversed and last, no repeats (%s)"
          % order)
    lay(good(), repo=repo)
    out = os.path.join(repo, "design", "concepts", "Demo", "cleanse")
    with open(os.path.join(out, "review.json"), "w") as f:
        json.dump({"rounds": [], "digest": "0" * 64}, f)
    check(not DC.done(repo, "Demo"), "resume: a review of other bytes (its digest differs) is stale")
    with open(os.path.join(out, "review.json"), "w") as f:
        json.dump({"rounds": []}, f)
    # Conductor 2026-11-17: the 23 first looks predate the digest; one with no digest is the first look, not stale
    check(DC.done(repo, "Demo"), "resume: a review an older launcher wrote with no digest is kept, not re-hunted")
    with open(os.path.join(out, "review.json"), "w") as f:
        json.dump({"rounds": [], "digest": DC.proposal_digest(out)}, f)
    check(DC.done(repo, "Demo"), "resume: a mod whose proposal passes check and has a review of these bytes is skipped")
    check(not DC.done(repo, "Plain"), "resume: a mod with no proposal is not")
    sd = tempfile.mkdtemp(prefix="dc_status_")
    st = DC.Status(sd)
    st.set("Demo", "running", "")
    st.set("Plain", "blocked", "held by owner")
    md = open(os.path.join(sd, "status.md")).read()
    check(re.search(r"^Demo\s.*running", md, re.M) and re.search(r"^Plain\s.*blocked.*held by owner", md, re.M),
          "status.md: one plain line per mod with its state and why")
    check(json.load(open(os.path.join(sd, "status.json")))["mods"]["Demo"]["state"] == "running", "status.json")
    argv = DC.fleet_unit_argv(["--all-biomes-but", "Pyrelands", "--parallel", "4"], unit="u1")
    check(argv[:1] == ["--user"] and "--" in argv and "--foreground" in argv and "RuntimeMaxSec" not in " ".join(argv),
          "fleet detaches into its own systemd user unit with no wall-time bound")
    os.environ["RM_OWNER_HOLD_FILE"] = "/x/hold.json"
    try:
        argv = DC.fleet_unit_argv(["--parallel", "4"], unit="u2")
    finally:
        os.environ.pop("RM_OWNER_HOLD_FILE", None)
    check("RM_OWNER_HOLD_FILE=/x/hold.json" in argv, "the detached unit carries the hold file it was launched with")


def proposal(repo=None):
    repo = repo or fake_repo()
    lay(good(), repo=repo)
    return repo, os.path.join(repo, "design", "concepts", "Demo", "cleanse")


def test_review_hardening():
    """GPT review 2026-11-17 (a_launcherB): sealed cold sort, hold in review, broken fix, stale reviews, locks, author
    on resume."""
    os.environ["RM_OWNER_HOLD_FILE"] = holds_file([])
    pool = tempfile.mkdtemp(prefix="dc_pool_")
    os.environ["RM_DETACHED_POOL"] = pool
    sdir = tempfile.mkdtemp(prefix="dc_status_")
    os.environ["RM_CLEANSE_STATUS_DIR"] = sdir
    try:
        # the cold sort is its own call: no tool, an empty folder that is not the clone, no proposal path, no label
        repo, out = proposal()
        fx = FX(repo, claude=[review_json([])], blinds=[sort_right])
        DC.review_mod("Demo", fx, author="codex")
        b = [c for c in fx.calls if c[0] == "blind"]
        r = [c for c in fx.calls if c[0] == "claude"]
        cwd, listing = fx.blind_cwds[0]
        labels = json.dumps(json.loads(good()["bars.json"])["bars"][0]["accept"])
        check(len(b) == 1 and b[0][2].get("tools") == "" and cwd != repo and listing == [] and not os.path.exists(cwd),
              "the cold sort runs alone, no tool, in an empty folder removed after (%s, %s)" % (b[0][2] if b else None,
                                                                                               listing))
        check("cleanse" not in b[0][1] and "bars.json" not in b[0][1] and '"accept": [' not in b[0][1]
              and labels not in b[0][1], "the cold sort's prompt names no proposal file and carries no label")
        check(fx.calls.index(b[0]) < fx.calls.index(r[0]) and "BLIND PICTURES" not in r[0][1],
              "the cold sort is sealed before the review call, which carries no pictures")
        # codex as reviewer: the cold sort runs read-only too
        repo, out = proposal()
        fx = FX(repo, codex=[review_json([])], blinds=[sort_right])
        DC.review_mod("Demo", fx, author="claude")
        b = [c for c in fx.calls if c[0] == "blind"]
        check(b and b[0][2].get("runner") == "codex" and b[0][2].get("sandbox") == "read-only",
              "a Codex reviewer's cold sort runs read-only (%s)" % (b[0][2] if b else None))
        # an unreadable cold sort twice: the reviewer is unreadable, nothing decided
        repo, out = proposal()
        nojson = {"is_error": False, "result": "no"}
        fx = FX(repo, claude=[review_json([REF])], blinds=[nojson, nojson])
        rec = DC.review_mod("Demo", fx, author="codex")
        check(rec["state"] == "blocked" and not os.path.exists(os.path.join(out, "review.json"))
              and [c[0] for c in fx.calls].count("blind") == 2 and "claude" not in [c[0] for c in fx.calls],
              "a cold sort unreadable twice blocks the review before the proposal is read (%s)" % rec["state"])
        # the hold: review refuses a held mod; a hold that lands during the first look stops the fix run
        repo, out = proposal()
        os.environ["RM_OWNER_HOLD_FILE"] = holds_file(["Demo"])
        fx = FX(repo, claude=[review_json([REF])])
        rec = DC.review_mod("Demo", fx, author="codex")
        check(rec["state"] == "blocked" and "allow-design" in rec["why"] and not fx.calls,
              "review refuses a held mod without allow-design and runs nothing (%s)" % rec["state"])
        hold_late = holds_file(["Demo"])
        os.environ["RM_OWNER_HOLD_FILE"] = holds_file([])
        def look_then_hold(cwd, prompt):
            os.environ["RM_OWNER_HOLD_FILE"] = hold_late
            return review_json([REF])(cwd, prompt)
        fx = FX(repo, claude=[look_then_hold])
        rec = DC.review_mod("Demo", fx, author="codex")
        check(rec["state"] == "blocked" and "codex" not in [c[0] for c in fx.calls],
              "a hold that lands during the first look: no writing author runs (%s)" % rec["state"])
        os.environ["RM_OWNER_HOLD_FILE"] = holds_file([])
        # the fix breaks result.json: the review still ends, blocked result kept, broken bytes kept beside
        repo, out = proposal()
        def break_result(cwd, prompt):
            with open(os.path.join(out, "result.json"), "w") as f:
                f.write("{ broken")
            return {"is_error": False, "result": "done"}
        fx = FX(repo, claude=[review_json([REF]), review_json([])], codex=[break_result])
        rec = DC.review_mod("Demo", fx, author="codex")
        res = DC._json_file(os.path.join(out, "result.json"))
        rv = DC._json_file(os.path.join(out, "review.json"))
        check(isinstance(res, dict) and res.get("applyable") is False and rec["state"] == "refused-after-second-look"
              and os.path.exists(os.path.join(out, "result.broken-by-fix.txt"))
              and any(x.get("head") == "self_check" for x in rv["remaining"]),
              "a fix that breaks result.json: the review ends, applyable false, the broken bytes kept (%s)" % rec["state"])
        # the fix turns the outcome to blocked: never applyable
        repo, out = proposal()
        def to_blocked(cwd, prompt):
            d = json.load(open(os.path.join(out, "result.json")))
            d["outcome"], d["blocked_on"] = "blocked", "the fix gave up"
            with open(os.path.join(out, "result.json"), "w") as f:
                json.dump(d, f)
            return {"is_error": False, "result": "done"}
        fx = FX(repo, claude=[review_json([REF]), review_json([])], codex=[to_blocked])
        rec = DC.review_mod("Demo", fx, author="codex")
        res = DC._json_file(os.path.join(out, "result.json"))
        check(res.get("applyable") is False and rec["state"] == "refused-after-second-look",
              "a fix that leaves the outcome blocked is never applyable (%s, %s)" % (rec["state"], res.get("applyable")))
        # the digest: a clean review is trusted until the proposal's bytes change; a new run unreviews
        repo, out = proposal()
        fx = FX(repo, claude=[review_json([])], blinds=[sort_right])
        rec = DC.review_mod("Demo", fx, author="codex")
        check(rec["state"] == "reviewed" and DC.done(repo, "Demo"), "a reviewed proposal is done (%s)" % rec["state"])
        bars_p = os.path.join(out, "bars.json")
        d = json.load(open(bars_p))
        d["bars"][0]["says"] += " Also at dusk."
        with open(bars_p, "w") as f:
            json.dump(d, f)
        check(not DC.done(repo, "Demo"), "a proposal changed after its review is not done: the review is stale")
        DC.unreview(out)
        pages = open(os.path.join(out, "owner_pages.md")).read()
        check(not os.path.exists(os.path.join(out, "review.json")) and "applyable" not in json.load(
              open(os.path.join(out, "result.json"))) and DC.STILL_REFUSED_HEAD not in pages,
              "a new run clears review.json, applyable and the reviewer's block")
        repo, out = proposal()
        fx = FX(repo, claude=[review_json([REF]), review_json([REF])], blinds=[sort_right, sort_right])
        DC.review_mod("Demo", fx, author="codex")
        digest = DC._json_file(os.path.join(out, "review.json")).get("digest")
        check(digest == DC.proposal_digest(out) and DC.STILL_REFUSED_HEAD in open(os.path.join(out, "owner_pages.md")).read(),
              "the digest is of the proposal as written, his pages' reviewer block and applyable left out")
        # the lock: a second taker is refused; a fleet's mod that is held elsewhere is skipped, status untouched
        with DC.mod_lock("Demo"):
            try:
                with DC.mod_lock("Demo"):
                    check(False, "a second taker of a mod's lock is refused")
            except DC.Busy:
                check(True, "a second taker of a mod's lock is refused")
            repo, out = proposal()
            fx = FX(repo)
            DC.Status(sdir).set("Demo", "running", "the other invocation's line")
            res = DC.fleet(["Demo"], lambda m: fx, parallel=1)
            line = DC.Status(sdir).read()["mods"]["Demo"]
            check(res == [("Demo", "busy")] and not fx.calls and not fx.states and line["state"] == "running",
                  "a fleet skips a mod another invocation holds and leaves its status line alone (%s, %s)" % (res, line))
            check(DC.main(["review", "Demo"]) == 1, "review of a mod another invocation holds is refused")
        with DC.mod_lock("Demo"):
            check(True, "the lock is free again when its holder leaves")
        # resume: the proposal's own author answers its review, whoever runs the fleet now
        repo, out = proposal()
        with open(os.path.join(out, "run.json"), "w") as f:
            json.dump({"runner": "claude", "model": "opus"}, f)
        fx = FX(repo, codex=[review_json([])], blinds=[sort_right])
        res = DC.fleet(["Demo"], lambda m: fx, runner="codex", parallel=1)
        kinds = [c[0] for c in fx.calls]
        check(res == [("Demo", "reviewed")] and "codex" in kinds and "claude" not in kinds,
              "a resumed proposal written by Claude is reviewed by Codex though the fleet runs Codex (%s, %s)"
              % (res, kinds))
    finally:
        os.environ.pop("RM_OWNER_HOLD_FILE", None)
        os.environ.pop("RM_DETACHED_POOL", None)
        os.environ.pop("RM_CLEANSE_STATUS_DIR", None)
    # the reviewer's record and the cold sort, forged
    bad = DC.validate_review({"refusals": [dict(REF, head={"x": 1})], "missed_capability": "x",
                              "loop_or_three_way": "x"})
    check(bad, "a refusal whose head is an object is the reviewer's defect, not a crash (%s)" % bad)
    bad = DC.validate_review({"refusals": ["no"], "missed_capability": "x", "loop_or_three_way": "x"})
    check(bad, "a refusal that is not an object is the reviewer's defect")
    rows, refs = DC.score_blind([{"bar": ["B1"], "n": 1, "sorted": "accept"}, {"bar": "B1", "n": True}],
                                {("B1", 1): ("accept", "a vent")})
    check(len(refs) == 1 and rows[0]["sorted"] is None, "a forged cold sort (list bar, bool n) sorts nothing")
    check(DC.claude_tool_args("") == ["--tools", ""] and "--dangerously-skip-permissions" in DC.claude_tool_args(None)
          and DC.claude_tool_args("Read,Grep") == ["--tools", "Read,Grep", "--allowedTools", "Read,Grep"],
          "claude tool args: none for the cold sort, read-only for review, all for the author")


CF = os.path.join("design", "concepts", "Demo", "cleanse")


def legacy_review(out, remaining, digest=None):
    """A review as the 2026-11-16 fleet wrote it (445c1012a5): no digest, remaining on his pages, applyable false."""
    rv = {"mod": "Demo", "author": "codex", "rounds": [{"refusals": remaining}, {"refusals": remaining}],
          "remaining": remaining, "applyable": False}
    if digest:
        rv["digest"] = digest
    with open(os.path.join(out, "review.json"), "w") as f:
        json.dump(rv, f)
    with open(os.path.join(out, "owner_pages.md"), "a") as f:
        f.write("\n" + DC._still_refused_block(remaining))
    res = json.load(open(os.path.join(out, "result.json")))
    res["applyable"] = False
    with open(os.path.join(out, "result.json"), "w") as f:
        json.dump(res, f)


def _ids(prompt):
    return re.findall(r'"id": "([A-Z][\w.]*)"', prompt.split("RECORDS:")[1].split("END RECORDS")[0])


def fix_b1(cwd, prompt, counts_bars=None):
    """The author's converge fix: widens B1's range only, claims one fix per record in fixes.json."""
    out = os.path.join(cwd, CF)
    bars = json.load(open(os.path.join(out, "bars.json")))
    bars["bars"][0]["range"]["varies"] += ", wind on/off" if "wind on/off," not in bars["bars"][0]["range"]["varies"] \
        else ", dusk"
    with open(os.path.join(out, "bars.json"), "w") as f:
        json.dump(bars, f)
    if counts_bars is not None:
        res = json.load(open(os.path.join(out, "result.json")))
        res["counts"]["bars"] = counts_bars
        with open(os.path.join(out, "result.json"), "w") as f:
            json.dump(res, f)
    with open(os.path.join(out, "fixes.json"), "w") as f:
        json.dump({"fixes": [{"id": i, "changed": "B1 range names wind", "where": "bars.json bars/B1"}
                             for i in _ids(prompt)]}, f)
    return {"is_error": False, "result": "done"}


def verdict(fixed=(), not_fixed=(), regressions=(), late=()):
    def make(cwd, prompt):
        v = [{"id": i, "verdict": "fixed", "evidence": "B1.range now names wind"} for i in fixed]
        v += [{"id": i, "verdict": "not_fixed", "evidence": "B2 still says nothing floods"} for i in not_fixed]
        return {"is_error": False, "result": json.dumps({"verdicts": v, "regressions": list(regressions),
                                                         "advisory_late": list(late)})}
    return make


REF2 = {"head": "cannot_hold_together", "where": "bars.json B2", "evidence": "B2 says nothing floods while R1 lets gas "
        "fill every cell (Source/Gas.cs line 40)", "would_pass": "B2 and R1 agree on flooding",
        "smallest_fix": "bound R1 by the vent count"}
STR = {"head": "stranger", "where": "bars.json B1", "evidence": "a cold reader sorted 'gas pools' as reject",
       "would_pass": "pictures a cold reader sorts as the proposal does", "smallest_fix": "rewrite those pictures"}
NEW_ON_B2 = {"entry": "bars.json bars/B2", "evidence": "B2 never names winter", "would_pass": "B2 names winter",
             "smallest_fix": "add winter"}


def _converge_env():
    os.environ["RM_OWNER_HOLD_FILE"] = holds_file([])
    os.environ["RM_DETACHED_POOL"] = tempfile.mkdtemp(prefix="dc_pool_")
    os.environ["RM_CLEANSE_STATUS_DIR"] = tempfile.mkdtemp(prefix="dc_status_")


def test_converge():
    """Conductor 2026-11-17: the second look re-hunted (12 of 23 counts went up), so nothing converged. Standing ruling
    (standing_rulings.md, a passing bar is an experience): a new gap at a later look on material that did not change is
    the earlier look's miss: advisory."""
    _converge_env()
    try:
        # one record fixed; a new finding on B2 (which the fix did not touch) and a late note block nothing
        repo, out = proposal()
        legacy_review(out, [REF])
        fx = FX(repo, codex=[fix_b1], claude=[verdict(fixed=["R1"], regressions=[NEW_ON_B2],
                                                      late=[{"what": "B2 could name dusk", "reason": "noticed"}])])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        kinds = [c[0] for c in fx.calls]
        cv = json.load(open(os.path.join(out, "converge.json")))
        late = json.dumps(cv.get("advisory_late"))
        check(rec["state"] == "converged" and cv.get("open") == [] and "B2 never names winter" in late
              and "B2 could name dusk" in late,
              "converge does not count a new finding on material the fix did not change: advisory_late, blocks "
              "nothing (%s, open %s)" % (rec["state"], cv.get("open")))
        res = json.load(open(os.path.join(out, "result.json")))
        check(res.get("applyable") is True and not DC.check_dir(out)[0]
              and DC.STILL_REFUSED_HEAD not in open(os.path.join(out, "owner_pages.md")).read(),
              "every record fixed and check passing: applyable true, the reviewer's block leaves his pages")
        check(kinds.count("codex") == 1 and kinds.count("claude") == 1 and "gate" in kinds
              and not [c for c in fx.calls if c[0] == "claude" and "HIS WORDS" in c[1]],
              "an old no-digest review is used as the first look: one author fix, one verifier, no fresh review (%s)"
              % kinds)
        ap = [c for c in fx.calls if c[0] == "codex"][0][1]
        check("CONVERGE FIX" in ap and REF["smallest_fix"] in ap and REF["would_pass"] in ap and "fixes.json" in ap
              and "You are the Designer." not in ap, "the author's fix gets only the records, with would_pass and "
              "smallest_fix, and is asked for fixes.json")
        vc = [c for c in fx.calls if c[0] == "claude"][0]
        check(vc[2].get("model") == "opus" and vc[2].get("tools") == "Read,Grep,Glob" and "VERIFY THE FIX" in vc[1]
              and "bars.json bars/B1" in vc[1] and "bars.json bars/B2" not in vc[1] and "R1" in vc[1],
              "the verifier is Claude Opus read-only, shown the records and only the entries the fix changed")
        check(cv.get("digest") == DC.proposal_digest(out) and DC.done(repo, "Demo") and DC.converge_done(repo, "Demo"),
              "the converge verdict carries the digest; resume trusts it")
        check(fx.published and all(p.startswith(CF + "/") for p in fx.published[-1])
              and CF + "/converge.json" in fx.published[-1] and CF + "/fixes.json" in fx.published[-1],
              "converge publishes only the cleanse folder, with converge.json and fixes.json")
        # a finding on an entry the fix DID change is a regression: an open record for the next round
        repo, out = proposal()
        legacy_review(out, [REF])
        reg = dict(NEW_ON_B2, entry="bars.json bars/B1", evidence="B1 range now contradicts R1")
        fx = FX(repo, codex=[fix_b1, fix_b1], claude=[verdict(fixed=["R1"], regressions=[reg]), verdict(fixed=["G1.1"])])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        cv = json.load(open(os.path.join(out, "converge.json")))
        check(len(cv["rounds"]) == 2 and "G1.1" in json.dumps(cv["rounds"][0].get("open_after"))
              and rec["state"] == "converged",
              "a finding on an entry the fix changed is a regression, open for the next round (%s)" % rec["state"])
        # one fixed, one not: applyable stays false; at most two rounds; the rest on his pages in the reviewer's words
        repo, out = proposal()
        legacy_review(out, [REF, REF2])
        fx = FX(repo, codex=[fix_b1, fix_b1, fix_b1],
                claude=[verdict(fixed=["R1"], not_fixed=["R2"]), verdict(not_fixed=["R2"]), verdict(fixed=["R2"])])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        kinds = [c[0] for c in fx.calls]
        res = json.load(open(os.path.join(out, "result.json")))
        pages = open(os.path.join(out, "owner_pages.md")).read()
        check(res.get("applyable") is False and rec["state"] == "open-after-converge" and kinds.count("codex") == 2
              and kinds.count("claude") == 2, "one record not fixed: applyable stays false after the two rounds, no "
              "third (%s, %s)" % (rec["state"], kinds))
        check(DC.STILL_REFUSED_HEAD in pages and REF2["evidence"] in pages and REF["evidence"] not in pages
              and not DC.check_dir(out)[0], "what is still not fixed stays on his pages in the reviewer's words; the "
              "fixed one leaves; check passes the block")
        # a-dead-author-spends-no-converge-round: a run that died and changed nothing is no round, nor is a reader that
        # could not be read
        repo2, out2 = proposal()
        legacy_review(out2, [REF])
        fx2 = FX(repo2, codex=[lambda c, p: {"is_error": True, "result": "killed"}], claude=[])
        fx2.snap()
        r2 = DC.converge_mod("Demo", fx2)
        check(r2["state"] == "blocked" and not os.path.exists(os.path.join(out2, "converge.json")),
              "a-dead-author-spends-no-converge-round: blocked, no round written (%s)" % r2)
        junk = lambda c, p: {"is_error": False, "result": "not json"}  # noqa: E731
        repo2, out2 = proposal()
        legacy_review(out2, [REF])
        fx2 = FX(repo2, codex=[fix_b1], claude=[junk, junk])
        fx2.snap()
        r2 = DC.converge_mod("Demo", fx2)
        check(r2["state"] == "blocked" and "could not look" in r2["why"] and
              not os.path.exists(os.path.join(out2, "converge.json")),
              "a-dead-author-spends-no-converge-round: a verifier unreadable twice is no not_fixed (%s)" % r2)
        n = len(fx.calls)
        rec = DC.converge_mod("Demo", fx)
        check(not [c for c in fx.calls[n:] if c[0] in ("codex", "claude", "gate", "blind")]
              and rec["state"] == "open-after-converge" and DC.converge_done(repo, "Demo"),
              "a mod with two rounds behind it runs no third (resume)")
        # every record fixed but the fix broke the shape: applyable false
        repo, out = proposal()
        legacy_review(out, [REF])
        fx = FX(repo, codex=[lambda c, p: fix_b1(c, p, counts_bars=9), fix_b1], claude=[verdict(fixed=["R1"])])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        res = json.load(open(os.path.join(out, "result.json")))
        check(res.get("applyable") is False and rec["state"] == "open-after-converge"
              and DC.check_dir(out)[0], "every record fixed but check refuses: applyable false (%s)" % rec["state"])
        # a proposal the self-check refuses before converge: its refusals are round one's records too, and the fix
        # that repairs them converges it (Cauldron, 2026-11-17: published under an older check, refused by today's)
        repo, out = proposal()
        legacy_review(out, [REF])
        res = json.load(open(os.path.join(out, "result.json")))
        res["counts"]["bars"] = 9
        with open(os.path.join(out, "result.json"), "w") as f:
            json.dump(res, f)
        fx = FX(repo, codex=[lambda c, p: fix_b1(c, p, counts_bars=2)], claude=[verdict(fixed=["R1"])])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        ap = [c for c in fx.calls if c[0] == "codex"][0][1]
        vc = [c for c in fx.calls if c[0] == "claude"]
        check(rec["state"] == "converged" and '"head": "self_check"' in ap and "C0.1" in ap and len(vc) == 1
              and "C0.1" not in vc[0][1].split("END RECORDS")[0],
              "check refusals standing before converge are round one's self_check records, judged by the check, not "
              "the verifier (%s)" % rec["state"])
        # a first look whose only records were the self-check's, and today's check passes: converged, no run
        repo, out = proposal()
        legacy_review(out, [{"head": "self_check", "where": "result.json", "evidence": "counts were off",
                             "would_pass": "counts equal", "smallest_fix": "recount"}])
        fx = FX(repo)
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        check(rec["state"] == "converged" and not [c for c in fx.calls if c[0] in ("codex", "claude", "blind")]
              and json.load(open(os.path.join(out, "result.json"))).get("applyable") is True
              and DC.STILL_REFUSED_HEAD not in open(os.path.join(out, "owner_pages.md")).read()
              and DC.converge_done(repo, "Demo"),
              "an old self-check record is superseded by today's check: nothing open, converged with no run (%s)"
              % rec["state"])
        # a census column given as a list of text is filled (Cauldron's evidence lists its source paths)
        repo, out = proposal()
        census = json.load(open(os.path.join(out, "census.json")))
        census["rows"][0]["evidence"] = ["Defs/Gas.xml", "Source/Gas.cs"]
        with open(os.path.join(out, "census.json"), "w") as f:
            json.dump(census, f)
        census["rows"][1]["evidence"] = []
        with open(os.path.join(out, "census.json"), "w") as f:
            json.dump(census, f)
        refs = DC.check_dir(out)[0]
        check([r["where"] for r in refs if r["rule"] == "census_row"] == ["census.json row 2 (%s)" % census["rows"][1]["id"]],
              "a census column holding a list of paths is filled; an empty list is blank (%s)" % refs)
        # a stranger record is judged by the cold sort again, on its own bar only, not by the verifier
        repo, out = proposal()
        legacy_review(out, [STR])
        fx = FX(repo, codex=[fix_b1], blinds=[sort_right])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        b = [c for c in fx.calls if c[0] == "blind"]
        check(rec["state"] == "converged" and len(b) == 1 and [i["bar"] for i in _items(b[0][1])] == ["B1"]
              and "claude" not in [c[0] for c in fx.calls],
              "a stranger record is re-sorted cold on its bar only (%s)" % rec["state"])
        # a review of other bytes is stale: converge refuses it and runs nothing
        repo, out = proposal()
        legacy_review(out, [REF], digest="0" * 64)
        fx = FX(repo, codex=[fix_b1])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        check(rec["state"] == "blocked" and "codex" not in [c[0] for c in fx.calls],
              "a review whose digest is of other bytes is stale: converge runs nothing (%s)" % rec.get("why"))
        # a verifier answer with no verdict for a record decides nothing about it (one retry, then could not look)
        repo, out = proposal()
        legacy_review(out, [REF])
        fx = FX(repo, codex=[fix_b1, fix_b1], claude=[verdict(), verdict(), verdict(), verdict()])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        check(rec["state"] == "blocked" and not os.path.exists(os.path.join(out, "converge.json")),
              "an unreadable verifier decides nothing: no round is spent (%s)" % rec["state"])
        # the hold: a held mod is not converged
        os.environ["RM_OWNER_HOLD_FILE"] = holds_file(["Demo"])
        repo, out = proposal()
        legacy_review(out, [REF])
        fx = FX(repo, codex=[fix_b1])
        rec = DC.converge_mod("Demo", fx)
        check(rec["state"] == "blocked" and not [c for c in fx.calls if c[0] in ("codex", "clone")],
              "converge refuses a held mod before any clone or run")
        os.environ["RM_OWNER_HOLD_FILE"] = holds_file([])
        # the fleet: --converge runs it per mod, and a resumed fleet skips a converged mod
        repo, out = proposal()
        legacy_review(out, [REF])
        fx = FX(repo, codex=[fix_b1], claude=[verdict(fixed=["R1"])])
        fx.snap()
        res = DC.fleet(["Demo"], lambda m: fx, converge=True, parallel=5)
        n = len(fx.calls)
        res2 = DC.fleet(["Demo"], lambda m: fx, converge=True, parallel=5)
        check(res == [("Demo", "converged")] and res2 == [("Demo", "converged")]
              and not [c for c in fx.calls[n:] if c[0] in ("codex", "claude")],
              "fleet --converge converges, and a resumed one skips the converged mod (%s %s)" % (res, res2))
        argv = DC.fleet_unit_argv(["--converge", "--parallel", "5"], unit="u3")
        check("--converge" in argv and "--foreground" in argv, "the detached unit carries --converge")
    finally:
        for k in ("RM_OWNER_HOLD_FILE", "RM_DETACHED_POOL", "RM_CLEANSE_STATUS_DIR"):
            os.environ.pop(k, None)


def test_gather():
    _converge_env()
    try:
        repo, out = proposal()
        legacy_review(out, [REF])
        plain = os.path.join(repo, "design", "concepts", "Plain", "cleanse")
        os.makedirs(plain)
        files = good()
        census = json.loads(files["census.json"])
        census["rows"].append({"id": "moth_lamp", "what": "a lamp the moths circle", "built": "present",
                               "evidence": "Defs/Lamp.xml", "proven": "missing", "called_by": "nothing", "serves": "",
                               "fate": "recommend_retire", "why": "nothing calls it", "needed_by": "", "ticket": ""})
        files["census.json"] = json.dumps(census)
        files["owner_pages.md"] = ("# Plain\n\nCapabilities 4.\n\n# Page two\n\nQ1. Is the fog a wall? Evidence against: "
                                   "the sheet says it drifts. Default: it drifts.\n\nQ2. Keep the moths?\nDefault: keep."
                                   "\n")
        for name, text in files.items():
            with open(os.path.join(plain, name), "w") as f:
                f.write(text)
        text, totals = DC.gather(repo)
        path = os.path.join(os.environ["RM_CLEANSE_STATUS_DIR"], "ALL_BIOMES.md")
        check(os.path.exists(path) and open(path).read() == text, "gather writes ALL_BIOMES.md in the status folder")
        qs = text.split("## Every question")[1].split("\n## ")[0] if "## Every question" in text else ""
        qtexts = ["Should the ritual stay?", "Is the fog a wall?", "Keep the moths?"]
        nums = re.findall(r"^(\d+)\. ", qs, re.M)
        check(all(qs.count(q) == 1 for q in qtexts) and nums == ["1", "2", "3"] and totals.get("questions") == 3,
              "gather lists every question once, numbered, with its mod (%s; %s)" % (nums, totals))
        check("the sheet says it drifts" in qs and "it drifts" in qs and "keep" in qs and "Plain" in qs and "Demo" in qs,
              "each question carries its evidence and the default taken")
        rt = text.split("## Every recommended retirement")[1].split("\n## ")[0] if "retirement" in text else ""
        check("a lamp the moths circle" in rt and "nothing calls it" in rt and "moth_lamp" not in text
              and "R1" not in text, "retirements in one list, with no id he has not been shown")
        top = text.split("\n## ")[0]
        check(re.search(r"^\| Demo \|.*\| no \| 1 \|$", top, re.M) and re.search(r"^\| Plain \|", top, re.M)
              and "| applyable |" in top, "the top table: one row per mod, applyable and open reviewer items")
        check(files["owner_pages.md"].strip() in text and "Should the ritual stay? Default: next version." in text,
              "each mod's two pages in full under its own heading")
        sd = os.environ.pop("RM_CLEANSE_STATUS_DIR")
        try:
            import rmpaths
            check(DC.status_dir() == str(rmpaths.rm_path("designer_cleanse")), "the status folder comes from the "
                  "agent-storage helper, not a hard-wired path")
        finally:
            os.environ["RM_CLEANSE_STATUS_DIR"] = sd
    finally:
        for k in ("RM_OWNER_HOLD_FILE", "RM_DETACHED_POOL", "RM_CLEANSE_STATUS_DIR"):
            os.environ.pop(k, None)


def _snap(d):
    """-> {relpath: bytes} of every file under d (what a dry run must leave as it found it)."""
    out = {}
    for base, _dirs, files in os.walk(d):
        for f in files:
            p = os.path.join(base, f)
            try:
                with open(p, "rb") as fh:
                    out[os.path.relpath(p, d)] = fh.read()
            except OSError:
                out[os.path.relpath(p, d)] = None
    return out


def applyable(repo=None):
    """-> (repo, concept, out): good() laid out under an old tree, its review converged on the current bytes."""
    repo = repo or tempfile.mkdtemp(prefix="dc_apply_")
    out = lay(good(), repo=repo)
    res = json.load(open(os.path.join(out, "result.json")))
    res["applyable"] = True
    json.dump(res, open(os.path.join(out, "result.json"), "w"))
    json.dump({"mod": "Demo", "applyable": True, "open": [], "digest": DC.proposal_digest(out)},
              open(os.path.join(out, "converge.json"), "w"))
    return repo, os.path.dirname(out), out


def materialize(concept, files):
    for rel, text in files.items():
        p = os.path.join(concept, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)


def test_apply():
    """apply_plan (RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS): four answers, the refusal order, review-3
    findings 1 (a run open; a queued job withdrawn), 5 (one next-version section), 6 (check on every plan, a retry
    reading the old-leaf record), 7 (unreadable is COULD_NOT_LOOK; {} and 0 bytes are CONVERGE_EMPTY) and 8 (temp
    fixtures only). Writes nothing."""
    import io
    from contextlib import redirect_stdout
    repo, concept, out = applyable()
    before = _snap(concept)
    r = DC.apply_plan(repo, "Demo")
    check(r["answer"] == "WOULD_WRITE" and {"tree.json", "sheet.md", "stage.json", os.path.join("version", "VERSION.json"),
                                            "later_version.md"} <= set(r["files"]),
          "apply: a converged proposal plans tree, sheet, stage, VERSION and later_version (%s %s)" % (r["answer"], r["cause"]))
    check(_snap(concept) == before, "apply: the dry run writes nothing")
    check(DC.apply_plan(repo, "Demo")["files"] == r["files"], "apply: the same inputs plan the same files")
    tree = json.loads(r["files"]["tree.json"])
    st = json.loads(r["files"]["stage.json"])
    ver = json.loads(r["files"][os.path.join("version", "VERSION.json")])
    check([x["id"] for x in tree["leaves"]] == ["B1", "B2"] and tree["cleanse"]["old_leaf_ids"] == OLD
          and tree["cleanse"]["digest"] == DC.proposal_digest(out), "apply: every bar a leaf; the old leaf ids recorded")
    check(st["status"] == "blocked" and st["running"] is None and st["blocked_on"], "apply: a new stage is born blocked")
    check(ver["version"] == "0.1.0" and ver["proposal_digest"] == tree["cleanse"]["digest"] and ver["replaces"] is None,
          "apply: VERSION 0.1.0 names the digest and replaces nothing")
    lv = r["files"]["later_version.md"]
    check(lv.count(DC.NEXT_BEGIN) == 1 and lv.count(DC.NEXT_END) == 1 and "ritual" in lv, "apply: one next-version section")
    # materialized: the readers take it, check still passes (the old-leaf record), a re-plan has nothing to apply
    materialize(concept, r["files"])
    check(not DC.check_dir(out)[0], "apply: check_dir passes the applied folder through tree.json's old-leaf record")
    check(DC.apply_plan(repo, "Demo")["answer"] == "NOTHING_TO_APPLY", "apply: a re-plan of the applied plan has nothing to apply")
    t = json.load(open(os.path.join(concept, "tree.json")))
    t["cleanse"]["old_leaf_ids"].append("unmapped_old")
    json.dump(t, open(os.path.join(concept, "tree.json"), "w"))
    check(DC.apply_plan(repo, "Demo")["cause"] == "CHECK_FAILED", "apply: a retry still checks the original old bars")
    # an old stage: a queued job is withdrawn; a run open refuses; a later version refuses
    repo, concept, out = applyable()
    json.dump({"schema": 1, "mod": "Demo", "stage": 3, "status": "ready", "running": None,
               "budget": {"cap": 10, "reserve": 1, "spent": 0, "charges": []}, "results": [], "history": []},
              open(os.path.join(concept, "stage.json"), "w"))
    open(os.path.join(concept, "later_version.md"), "w").write("# Demo later\n\nhis older notes\n")
    r = DC.apply_plan(repo, "Demo")
    st = json.loads(r["files"]["stage.json"])
    check(st["status"] == "blocked" and st["stage"] == 3 and st["cleanse"]["was"] == "ready",
          "apply: a ready stage is withdrawn to blocked")
    lv = r["files"]["later_version.md"]
    check(lv.startswith("# Demo later\n\nhis older notes\n") and lv.count(DC.NEXT_BEGIN) == 1,
          "apply: text outside the markers is kept verbatim")
    materialize(concept, r["files"])
    again = DC.apply_plan(repo, "Demo")
    check(again["answer"] == "NOTHING_TO_APPLY" and again["files"]["later_version.md"].count(DC.NEXT_BEGIN) == 1,
          "apply: a re-plan replaces the section, never adds one")
    s = json.load(open(os.path.join(concept, "stage.json")))
    s["running"] = {"run": "rm-role-designer-1", "stage": 3}
    json.dump(s, open(os.path.join(concept, "stage.json"), "w"))
    check(DC.apply_plan(repo, "Demo")["cause"] == "DESIGNER_RUN_OPEN", "apply: a Designer run open refuses")
    repo, concept, out = applyable()
    os.makedirs(os.path.join(concept, "version"))
    json.dump({"mod": "Demo", "version": "0.2.0"}, open(os.path.join(concept, "version", "VERSION.json"), "w"))
    check(DC.apply_plan(repo, "Demo")["cause"] == "VERSION_DOWNGRADE", "apply: VERSION above 0.1.0 refuses")
    # zero moved plans no later_version.md; zero kept refuses
    repo, concept, out = applyable()
    c = json.load(open(os.path.join(out, "census.json")))
    rows = c["rows"] if isinstance(c, dict) else c
    for x in rows:
        x["fate"] = "next_version"
    json.dump(c, open(os.path.join(out, "census.json"), "w"))
    check(DC.apply_plan(repo, "Demo")["cause"] == "ZERO_KEPT", "apply: zero kept refuses")
    # each converge and result kind its own cause
    for name, fn, cause in (
            ("converge missing", lambda o: os.remove(os.path.join(o, "converge.json")), "CONVERGE_MISSING"),
            ("converge {}", lambda o: open(os.path.join(o, "converge.json"), "w").write("{}"), "CONVERGE_EMPTY"),
            ("converge 0 bytes", lambda o: open(os.path.join(o, "converge.json"), "w").close(), "CONVERGE_EMPTY"),
            ("converge open", lambda o: json.dump({"applyable": False, "open": ["x"]}, open(os.path.join(o, "converge.json"), "w")),
             "NOT_CONVERGED"),
            ("converge stale", lambda o: json.dump({"applyable": True, "open": [], "digest": "0" * 64},
                                                   open(os.path.join(o, "converge.json"), "w")), "STALE_CONVERGENCE"),
            ("converge no digest", lambda o: json.dump({"applyable": True, "open": []}, open(os.path.join(o, "converge.json"), "w")),
             "STALE_CONVERGENCE")):
        repo, concept, out = applyable()
        fn(out)
        got = DC.apply_plan(repo, "Demo")
        check((got["answer"], got["cause"]) == ("REFUSED", cause), "apply: %s is %s (%s)" % (name, cause, got["cause"]))
    repo, concept, out = applyable()
    res = json.load(open(os.path.join(out, "result.json")))
    res["applyable"] = False
    json.dump(res, open(os.path.join(out, "result.json"), "w"))
    check(DC.apply_plan(repo, "Demo")["cause"] == "RESULT_NOT_APPLYABLE", "apply: result.json not applyable refuses")
    check(DC.apply_plan(repo, "Nobody")["cause"] == "NO_PROPOSAL", "apply: no proposal refuses")
    os.makedirs(os.path.join(repo, "design", "concepts", "Pyrelands", "cleanse"))
    check(DC.apply_plan(repo, "Pyrelands")["cause"] == "PYRELANDS", "apply: Pyrelands is outside the cleanse")
    check(DC.apply_plan(repo, "../Demo")["cause"] == "BAD_MOD", "apply: a mod name that is a path refuses")
    if os.geteuid() != 0:
        for rel in ("cleanse/converge.json", "tree.json"):
            repo, concept, out = applyable()
            os.chmod(os.path.join(concept, rel), 0)
            got = DC.apply_plan(repo, "Demo")
            check(got["answer"] == "COULD_NOT_LOOK" and os.path.basename(rel) in got["path"],
                  "apply: an unreadable %s is COULD_NOT_LOOK naming it, never absent" % rel)
            os.chmod(os.path.join(concept, rel), 0o644)
    repo, concept, out = applyable()
    open(os.path.join(concept, "stage.json"), "w").write("{broken")
    check(DC.apply_plan(repo, "Demo")["answer"] == "COULD_NOT_LOOK", "apply: a stage.json that does not parse is COULD_NOT_LOOK")
    # the CLI: one closing line, its exit; --write refused and writes nothing
    repo, concept, out = applyable()
    before = _snap(concept)
    for argv, code, line in ((["apply", "Demo", "--repo", repo], 0, "APPLY Demo WOULD_WRITE 5 files"),
                             (["apply", "Demo", "--repo", repo, "--write"], 1, "APPLY Demo REFUSED NOT_APPROVED"),
                             (["apply", "Nobody", "--repo", repo], 1, "APPLY Nobody REFUSED NO_PROPOSAL")):
        buf = io.StringIO()
        with redirect_stdout(buf):
            got = DC.main(argv)
        last = buf.getvalue().strip().splitlines()[-1]
        check(got == code and last.startswith(line), "apply CLI %s: exit %s, %r" % (" ".join(argv[2:]), got, last))
    check(_snap(concept) == before, "apply CLI: neither the dry run nor an unapproved --write wrote anything")


def test_apply_edges():
    """Codex review of the apply dry run (2026-11-18): each finding a row."""
    import concept_tree as CT
    import designer_stage as DS
    # a clean first look converges in round 0: converge.json is written, so apply can read it
    _converge_env()
    try:
        repo, out = proposal()
        json.dump({"mod": "Demo", "author": "codex", "rounds": [{"refusals": []}], "remaining": [],
                   "digest": DC.proposal_digest(out)}, open(os.path.join(out, "review.json"), "w"))
        check(not DC.converge_done(repo, "Demo"), "a clean first look alone is not converged: converge.json is owed")
        fx = FX(repo, codex=[], claude=[])
        fx.snap()
        rec = DC.converge_mod("Demo", fx)
        cv = DC._json_file(os.path.join(out, "converge.json"))
        check(rec["state"] == "converged" and isinstance(cv, dict) and cv.get("applyable") is True and cv.get("open") == []
              and cv.get("digest") == DC.proposal_digest(out) and not [c for c in fx.calls if c[0] in ("codex", "claude")],
              "a clean first look writes converge.json in round 0, no agent run (%s)" % rec["state"])
    finally:
        for k in ("RM_OWNER_HOLD_FILE", "RM_DETACHED_POOL", "RM_CLEANSE_STATUS_DIR"):
            os.environ.pop(k, None)
    # a first look whose record list is unreadable is blocked, never a clean round 0
    _converge_env()
    try:
        for bad in (None, "none", [1]):
            repo, out = proposal()
            json.dump({"mod": "Demo", "author": "codex", "remaining": bad}, open(os.path.join(out, "review.json"), "w"))
            fx = FX(repo, codex=[], claude=[])
            fx.snap()
            rec = DC.converge_mod("Demo", fx)
            check(rec["state"] == "blocked" and not os.path.exists(os.path.join(out, "converge.json")),
                  "a review.json whose remaining is %r is blocked, never converged (%s)" % (bad, rec["state"]))
    finally:
        for k in ("RM_OWNER_HOLD_FILE", "RM_DETACHED_POOL", "RM_CLEANSE_STATUS_DIR"):
            os.environ.pop(k, None)
    # the materialized plan loads through the readers
    repo, concept, out = applyable()
    r = DC.apply_plan(repo, "Demo")
    materialize(concept, r["files"])
    try:
        CT.load(concept)
        s = DS.status(concept, repo)
        ok, why = s.get("status") == "blocked" and s.get("running") is None, s.get("status")
    except Exception as e:      # noqa: BLE001  a reader that refuses the plan is a failed row
        ok, why = False, "%s: %s" % (type(e).__name__, e)
    check(ok, "apply: the applied folder loads through concept_tree.load and designer_stage.status (%s)" % why)
    # a later, different proposal maps the tree as it now stands, not the old-leaf record
    bars = json.load(open(os.path.join(out, "bars.json")))
    bars["old_bars"] = {"B1": {"to": "kept", "as": "B1", "why": "kept"}, "B2": {"to": "kept", "as": "B2", "why": "kept"}}
    json.dump(bars, open(os.path.join(out, "bars.json"), "w"))
    check(DC._old_bars(out) == ["B1", "B2"], "apply: a new proposal's old bars are the applied tree's leaves (%s)"
          % DC._old_bars(out))
    # a census whose rows are not a list is CHECK_FAILED, never a crash
    repo, concept, out = applyable()
    json.dump({"rows": 1}, open(os.path.join(out, "census.json"), "w"))
    try:
        got = DC.apply_plan(repo, "Demo")["cause"]
    except Exception as e:      # noqa: BLE001
        got = "raised %s" % type(e).__name__
    check(got == "CHECK_FAILED", "apply: census rows that are not a list are CHECK_FAILED (%s)" % got)
    # the census as a bare list (a form check_dir reads) plans its capabilities; a tree whose leaves are no list is unseeable
    repo, concept, out = applyable()
    c = json.load(open(os.path.join(out, "census.json")))
    json.dump(c["rows"] if isinstance(c, dict) else c, open(os.path.join(out, "census.json"), "w"))
    cv = json.load(open(os.path.join(out, "converge.json")))
    cv["digest"] = DC.proposal_digest(out)
    json.dump(cv, open(os.path.join(out, "converge.json"), "w"))
    r = DC.apply_plan(repo, "Demo")
    check(r["answer"] == "WOULD_WRITE" and len(json.loads(r["files"]["tree.json"])["capabilities"]) == 2
          and "ritual" in r["files"].get("later_version.md", ""), "apply: a list-form census plans its kept and moved rows "
          "(%s %s %s)" % (r["answer"], r["cause"], r["detail"]))
    repo, concept, out = applyable()
    json.dump({"leaves": 1}, open(os.path.join(concept, "tree.json"), "w"))
    try:
        got = DC.apply_plan(repo, "Demo")["answer"]
    except Exception as e:      # noqa: BLE001
        got = "raised %s" % type(e).__name__
    check(got == "COULD_NOT_LOOK", "apply: a tree.json whose leaves are no list is COULD_NOT_LOOK, never a crash (%s)" % got)
    # a definition that quotes `## his words` does not double on a re-plan
    repo, concept, out = applyable()
    with open(os.path.join(out, "definition.md"), "a") as f:
        f.write("\n## his words\n\nThe ground breathes gas.\n")
    cv = json.load(open(os.path.join(out, "converge.json")))
    cv["digest"] = DC.proposal_digest(out)
    json.dump(cv, open(os.path.join(out, "converge.json"), "w"))
    r = DC.apply_plan(repo, "Demo")
    if r["answer"] == "WOULD_WRITE":
        materialize(concept, r["files"])
        again = DC.apply_plan(repo, "Demo")
        check(again["answer"] == "NOTHING_TO_APPLY", "apply: a definition quoting his heading re-plans to nothing (%s %s)"
              % (again["answer"], again["changed"]))
    else:
        check(False, "apply: the his-words fixture plans (%s %s %s)" % (r["answer"], r["cause"], r["detail"]))
    # an old sheet's his-words section is carried, verbatim
    repo, concept, out = applyable()
    open(os.path.join(concept, "sheet.md"), "w").write("# Demo\n\n## his words\n\n- \"keep the gas\"\n\n## does\n\n- x\n")
    check("- \"keep the gas\"" in DC.apply_plan(repo, "Demo")["files"]["sheet.md"], "apply: his words on the old sheet are kept")
    # an unreadable review.json is COULD_NOT_LOOK
    if os.geteuid() != 0:
        repo, concept, out = applyable()
        legacy_review(out, [])
        os.chmod(os.path.join(out, "review.json"), 0)
        got = DC.apply_plan(repo, "Demo")
        check(got["answer"] == "COULD_NOT_LOOK" and "review.json" in got["path"], "apply: an unreadable review.json is "
              "COULD_NOT_LOOK naming it (%s %s)" % (got["answer"], got["path"]))
        os.chmod(os.path.join(out, "review.json"), 0o644)
    # a VERSION record with this digest but another shape is replaced by 0.1.0
    repo, concept, out = applyable()
    os.makedirs(os.path.join(concept, "version"))
    json.dump({"mod": "Demo", "version": "0.0.9", "proposal_digest": DC.proposal_digest(out)},
              open(os.path.join(concept, "version", "VERSION.json"), "w"))
    ver = json.loads(DC.apply_plan(repo, "Demo")["files"][os.path.join("version", "VERSION.json")])
    check(ver["version"] == "0.1.0" and ver["replaces"]["version"] == "0.0.9", "apply: a 0.0.9 record is replaced by 0.1.0")
    # two marked sections already, or an unmatched marker: refused, never a second section
    for tag, body in (("two", "%s\na\n%s\nnotes\n%s\nb\n%s\n" % ((DC.NEXT_BEGIN, DC.NEXT_END) * 2)),
                      ("unmatched", "%s\na\n" % DC.NEXT_BEGIN), ("reversed", "%s\na\n%s\n" % (DC.NEXT_END, DC.NEXT_BEGIN))):
        repo, concept, out = applyable()
        open(os.path.join(concept, "later_version.md"), "w").write(body)
        check(DC.apply_plan(repo, "Demo")["cause"] == "LATER_VERSION_MARKERS", "apply: later_version.md markers %s refuse" % tag)
    # zero moved: no later_version.md planned
    repo, concept, out = applyable()
    c = json.load(open(os.path.join(out, "census.json")))
    for x in c["rows"] if isinstance(c, dict) else c:
        if x["fate"] == "next_version":
            x["fate"] = "land"
    json.dump(c, open(os.path.join(out, "census.json"), "w"))
    res = json.load(open(os.path.join(out, "result.json")))
    res["counts"].update(kept=3, next_version=0)
    json.dump(res, open(os.path.join(out, "result.json"), "w"))
    cv = json.load(open(os.path.join(out, "converge.json")))
    cv["digest"] = DC.proposal_digest(out)
    json.dump(cv, open(os.path.join(out, "converge.json"), "w"))
    r = DC.apply_plan(repo, "Demo")
    check(r["answer"] == "WOULD_WRITE" and "later_version.md" not in r["files"],
          "apply: zero moved plans no later_version.md (%s %s %s)" % (r["answer"], r["cause"], r["detail"]))


def _modes(d):
    """{relpath: (mode, bytes)} under d: a rollback must restore both."""
    out = {}
    for base, _dirs, files in os.walk(d):
        for f in files:
            p = os.path.join(base, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, d)] = (os.stat(p).st_mode, fh.read())
    return out


def approved(marks=None, plan=True):
    """-> (repo, concept, out): applyable() plus the owner's plan approving Demo by its digest, and a hold file."""
    import cleanse_plan as CP
    repo, concept, out = applyable()
    if plan:
        p = os.path.join(repo, CP.PLAN_REL)
        json.dump({"schema": 1, "excluded": {"Pyrelands": "not part"},
                   "mods": {"Demo": {"approve": "digest", "approved_digest": DC.proposal_digest(out), "marks": marks or {}}}},
                  open(p, "w"))
    hold = os.path.join(repo, "src", "RimMandrake", "rimflow", "mod_owner_hold.json")
    os.makedirs(os.path.dirname(hold), exist_ok=True)
    json.dump({"holds": {"Demo": {"why": "his hold"}}}, open(hold, "w"))
    return repo, concept, out


def test_apply_write():
    """apply_write (RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED): all or none, the owner's plan first, a run
    opened under the lock refuses, a cleanup failure after a complete install is WROTE (review-3 finding 4)."""
    import designer_stage as DS
    repo, concept, out = approved()
    plan = DC.apply_plan(repo, "Demo")["files"]
    outside = {k: v for k, v in _modes(repo).items() if not k.startswith(os.path.join("design", "concepts", "Demo") + os.sep)}
    w = DC.apply_write(repo, "Demo")
    check(w["answer"] == "WROTE" and w["files"] == sorted(plan) and not w["cleanup_failed"],
          "write: an approved plan is WROTE, every planned file (%s %s %s)" % (w["answer"], w["cause"], w["detail"]))
    check(all(open(os.path.join(concept, r), encoding="utf-8").read() == t for r, t in plan.items()),
          "write: each file installed is the planned text")
    check(not [f for f in os.listdir(concept) if f.startswith(".apply-")], "write: no temp file left")
    now = {k: v for k, v in _modes(repo).items() if not k.startswith(os.path.join("design", "concepts", "Demo") + os.sep)}
    check(now == outside, "write: nothing outside the concept folder changed (the owner's hold, the plan)")
    check(DS.status(concept, repo)["status"] == "blocked", "write: the written concept reads blocked, never ready")
    check(DC.apply_write(repo, "Demo")["answer"] == "NOTHING_TO_APPLY", "write: a re-run has nothing to apply")
    # the owner's plan decides before the proposal's own refusals; its could-not-look stays could-not-look
    repo, concept, out = approved(plan=False)
    check(DC.apply_write(repo, "Demo")["cause"] == "NOT_APPROVED", "write: no owner's plan is NOT_APPROVED")
    repo, concept, out = approved(marks={"ritual": "keep"})
    check(DC.apply_write(repo, "Demo")["cause"] == "NOT_APPROVED", "write: a mark not folded is NOT_APPROVED")
    repo, concept, out = approved()
    os.remove(os.path.join(out, "converge.json"))
    check(DC.apply_write(repo, "Demo")["cause"] == "CONVERGE_MISSING", "write: an approved plan still needs convergence")
    if os.geteuid() != 0:
        import cleanse_plan as CP
        repo, concept, out = approved()
        os.chmod(os.path.join(repo, CP.PLAN_REL), 0)
        check(DC.apply_write(repo, "Demo")["answer"] == "COULD_NOT_LOOK", "write: an unreadable plan is COULD_NOT_LOOK")
        os.chmod(os.path.join(repo, CP.PLAN_REL), 0o644)
    # a Designer run opened while it took the lock: the re-plan under the lock refuses, nothing written
    repo, concept, out = approved()
    sp = os.path.join(concept, "stage.json")
    json.dump({"schema": 1, "mod": "Demo", "stage": 3, "status": "ready", "running": None,
               "budget": {"cap": 10, "reserve": 1, "spent": 0, "charges": []}, "results": [], "history": []}, open(sp, "w"))

    def opens(phase, rel):
        if phase == "locked":
            s = json.load(open(sp))
            s["running"] = {"run": "rm-role-designer-2", "stage": 3}
            json.dump(s, open(sp, "w"))
    w = DC.apply_write(repo, "Demo", fault=opens)
    check((w["answer"], w["cause"]) == ("REFUSED", "DESIGNER_RUN_OPEN") and not os.path.exists(os.path.join(concept, "sheet.md")),
          "write: a run opened under the lock refuses and writes nothing (%s %s)" % (w["answer"], w["cause"]))
    # an install fault on the first and on a later file: every file back to its exact bytes and mode
    for n in (1, 3):
        repo, concept, out = approved()
        open(os.path.join(concept, "sheet.md"), "w").write("# Demo\nold sheet\n")
        os.chmod(os.path.join(concept, "sheet.md"), 0o600)
        before = _modes(concept)
        seen = []

        def boom(phase, rel, n=n, seen=seen):
            if phase == "install":
                seen.append(rel)
                if len(seen) == n:
                    raise OSError(28, "No space left on device (injected)")
        w = DC.apply_write(repo, "Demo", fault=boom)
        check((w["answer"], w["cause"]) == ("WRITE_FAILED", "ROLLED_BACK") and _modes(concept) == before
              and not os.path.exists(os.path.join(concept, "version")),
              "write: an install fault on file %d rolls back bytes, modes and new folders (%s %s)" % (n, w["answer"], w["cause"]))
    # a rollback that cannot restore says so by name, never ROLLED_BACK
    repo, concept, out = approved()
    open(os.path.join(concept, "sheet.md"), "w").write("old\n")
    real, broke = DC._replace, []

    def flaky(dst, data, mode, strays=None):
        if broke:
            raise OSError(5, "I/O error (injected)")
        return real(dst, data, mode, strays)

    def late(phase, rel):
        if phase == "install" and rel == "tree.json":
            broke.append(1)
            raise OSError(28, "No space left on device (injected)")
    DC._replace = flaky
    try:
        w = DC.apply_write(repo, "Demo", fault=late)
    finally:
        DC._replace = real
    check((w["answer"], w["cause"]) == ("WRITE_FAILED", "ROLLBACK_INCOMPLETE") and "sheet.md" in w["detail"],
          "write: a rollback that fails names what it left (%s %s)" % (w["answer"], w["cause"]))
    # a failure inside the replace after a new folder was made: the folder goes too
    repo, concept, out = approved()
    before = _modes(concept)

    def last_fails(dst, data, mode, strays=None):
        if dst.endswith("VERSION.json"):
            raise OSError(28, "No space left on device (injected)")
        return real(dst, data, mode, strays)
    DC._replace = last_fails
    try:
        w = DC.apply_write(repo, "Demo")
    finally:
        DC._replace = real
    check(w["cause"] == "ROLLED_BACK" and _modes(concept) == before and not os.path.exists(os.path.join(concept, "version")),
          "write: a failed replace after making version/ removes it with the rest (%s)" % w["cause"])
    # an interrupt mid-install rolls back, then still interrupts
    repo, concept, out = approved()
    before = _modes(concept)

    def interrupt(phase, rel):
        if phase == "install" and rel == "stage.json":
            raise KeyboardInterrupt()
    try:
        DC.apply_write(repo, "Demo", fault=interrupt)
        got = "returned"
    except KeyboardInterrupt:
        got = "interrupted"
    check(got == "interrupted" and _modes(concept) == before, "write: an interrupt mid-install rolls back and re-raises (%s)" % got)
    # a temp file that cannot be removed is no exact rollback
    repo, concept, out = approved()
    real_unlink = os.unlink
    real_rep = os.replace

    def no_rep(a, b):
        raise OSError(28, "No space left on device (injected)")

    def no_unlink(p):
        if os.path.basename(p).startswith(".apply-"):
            raise OSError(16, "busy (injected)")
        return real_unlink(p)
    DC.os.replace, DC.os.unlink = no_rep, no_unlink
    try:
        w = DC.apply_write(repo, "Demo")
    finally:
        DC.os.replace, DC.os.unlink = real_rep, real_unlink
    check(w["cause"] == "ROLLBACK_INCOMPLETE" and "temp file left" in w["detail"],
          "write: a temp file it could not remove is ROLLBACK_INCOMPLETE, never ROLLED_BACK (%s)" % w["cause"])
    for f in os.listdir(concept):
        if f.startswith(".apply-"):
            real_unlink(os.path.join(concept, f))
    # a linked version/ folder would write outside the concept folder: refused, nothing written there
    repo, concept, out = approved()
    away = tempfile.mkdtemp(prefix="dc_away_")
    os.symlink(away, os.path.join(concept, "version"))
    w = DC.apply_write(repo, "Demo")
    check((w["answer"], w["cause"]) == ("REFUSED", "UNSAFE_PATH") and os.listdir(away) == [],
          "write: a linked version/ folder is UNSAFE_PATH and nothing lands outside (%s %s)" % (w["answer"], w["cause"]))
    # a link planted on the path during the install is caught at the moment of writing
    repo, concept, out = approved()
    before = _modes(concept)
    away = tempfile.mkdtemp(prefix="dc_away_")

    def plant(phase, rel):
        if phase == "install" and rel.startswith("version"):
            os.symlink(away, os.path.join(concept, "version"))
    w = DC.apply_write(repo, "Demo", fault=plant)
    check(w["answer"] == "WRITE_FAILED" and os.listdir(away) == [] and _modes(concept) == before,
          "write: a link planted mid-install fails the write, rolled back, nothing outside (%s %s)" % (w["answer"], w["cause"]))
    # an interrupt right after the new folder is made still removes it
    repo, concept, out = approved()
    before = _modes(concept)
    real_mkdir = os.mkdir

    def mkdir_then_stop(p, *a):
        real_mkdir(p, *a)
        raise KeyboardInterrupt()
    DC.os.mkdir = mkdir_then_stop
    try:
        DC.apply_write(repo, "Demo")
        got = "returned"
    except KeyboardInterrupt:
        got = "interrupted"
    finally:
        DC.os.mkdir = real_mkdir
    check(got == "interrupted" and not os.path.exists(os.path.join(concept, "version")) and _modes(concept) == before,
          "write: an interrupt after mkdir removes the new folder and every file (%s)" % got)
    # a cleanup fault after a complete install is WROTE plus its own line (CLI), never WRITE_FAILED
    import io
    from contextlib import redirect_stdout
    repo, concept, out = approved()
    plan = DC.apply_plan(repo, "Demo")["files"]

    def dirty(phase, rel):
        if phase == "cleanup":
            raise OSError(16, "Device or resource busy (injected)")
    DC.APPLY_FAULT, buf = dirty, io.StringIO()
    try:
        with redirect_stdout(buf):
            code = DC.main(["apply", "Demo", "--write", "--repo", repo])
    finally:
        DC.APPLY_FAULT = None
    lines = buf.getvalue().strip().splitlines()
    check(code == 0 and lines[-1] == "APPLY Demo WROTE %d files" % len(plan)
          and any(x.startswith("APPLY Demo CLEANUP_FAILED") for x in lines[:-1]),
          "write CLI: a cleanup fault is WROTE with its own CLEANUP_FAILED line (%s %r)" % (code, lines[-2:]))
    check(all(open(os.path.join(concept, r), encoding="utf-8").read() == t for r, t in plan.items()),
          "write: after a cleanup fault the install is complete")


def test_release():
    """Effects.release (RIMMANDRAKE_RELEASE_CLEANSE_CLONES_RECORDS_PIN_POOL_FULL): a clone whose only dirt is untracked
    conversations/*.md records carries them out (published) and is removed; any other dirt keeps it; a failed carry
    keeps it and says why. The pool filled 16 of 16 on such clones, 2026-11-17."""
    import scratch_clone as SC
    landed = tempfile.mkdtemp(prefix="dc_landed_")

    class Rel(DC.Effects):
        def __init__(self, fail=False):
            self.fail, self.published = fail, []

        def publish(self, cwd, paths, msg):
            if self.fail:
                raise RuntimeError("./publish exit 1: REFUSED (injected)")
            for p in paths:
                os.makedirs(os.path.dirname(os.path.join(landed, p)), exist_ok=True)
                shutil.copy(os.path.join(cwd, p), os.path.join(landed, p))
                os.remove(os.path.join(cwd, p))      # landed: the clone reads clean again
            self.published.append(list(paths))
            return "abc1234"

    def clone_with(*files):
        c = tempfile.mkdtemp(prefix="dc_rel_")
        for f in files:
            os.makedirs(os.path.dirname(os.path.join(c, f)) or c, exist_ok=True)
            open(os.path.join(c, f), "w").write("x")
        return c
    real = (SC.clone_unpushed, SC.clone_in_use, DC.Effects.changed)
    SC.clone_unpushed, SC.clone_in_use = (lambda p, strict=True: False), (lambda p: False)
    DC.Effects.changed = lambda self, cwd: sorted(
        os.path.relpath(os.path.join(b, f), cwd) for b, _d, fs in os.walk(cwd) for f in fs)
    try:
        c = clone_with("conversations/x.md")
        fx = Rel()
        said = fx.release(c)
        check(not os.path.exists(c) and os.path.isfile(os.path.join(landed, "conversations", "x.md"))
              and fx.published == [["conversations/x.md"]],
              "release: a clone whose only dirt is conversations/x.md publishes it and is removed (%s)" % said)
        c = clone_with("conversations/x.md", "stray.txt")
        said = Rel().release(c)
        check(os.path.isdir(c) and "kept" in said, "release: conversations plus another untracked file keeps it (%s)" % said)
        c = clone_with()
        said = Rel().release(c)
        check(not os.path.exists(c) and "removed" in said, "release: a clean clone is removed (%s)" % said)
        c = clone_with("conversations/y.md")
        said = Rel(fail=True).release(c)
        check(os.path.isfile(os.path.join(c, "conversations", "y.md")) and "kept" in said and "REFUSED (injected)" in said,
              "release: a failed carry keeps the clone and names the failure (%s)" % said)
    finally:
        SC.clone_unpushed, SC.clone_in_use, DC.Effects.changed = real


def main():
    # Every mkdtemp below lands in one root of this run's own, removed pass or fail: a direct run left 1,659 dc_* dirs
    # and 19,204 stood in /tmp on 2026-11-18 (selftest_designer_cleanse_tmp.py).
    saved_tmp, saved_env = tempfile.tempdir, dict(os.environ)
    root = tempfile.mkdtemp(prefix="dc_run_")
    tempfile.tempdir = root
    os.environ["TMPDIR"] = root
    try:
        for t in (test_check, test_detector, test_case, test_owner_answers, test_hold, test_run, test_review, test_fleet,
                  test_review_hardening, test_converge, test_gather, test_apply, test_apply_edges,
                  test_apply_write, test_release):
            try:
                t()
            except Exception as e:      # a crash is a failed row, not a silent stop
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    finally:
        tempfile.tempdir = saved_tmp
        os.environ.clear()
        os.environ.update(saved_env)
        shutil.rmtree(root, ignore_errors=True)
    print("%d checks, %d failed" % (N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
