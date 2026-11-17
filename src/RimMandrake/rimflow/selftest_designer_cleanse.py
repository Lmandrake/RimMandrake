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
import sys
import tempfile

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
        return "abc1234"

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
        json.dump({"rounds": []}, f)
    check(not DC.done(repo, "Demo"), "resume: a review that recorded no digest is not trusted (an older launcher's)")
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
    check(argv[:2] == ["systemd-run", "--user"] and "--foreground" in argv and "RuntimeMaxSec" not in " ".join(argv),
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


def main():
    for t in (test_check, test_detector, test_case, test_hold, test_run, test_review, test_fleet,
              test_review_hardening):
        try:
            t()
        except Exception as e:      # a crash is a failed row, not a silent stop
            import traceback
            traceback.print_exc()
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d checks, %d failed" % (N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
