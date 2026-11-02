#!/usr/bin/env python3
"""selftest_concept_tree.py - the door: a good tree passes, each way of being bad is refused for its own reason, and
Relentless cannot hand a mod over without the gate. Runs in a temp dir; touches no real concept and no ledger."""
import copy
import json
import re
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import concept_tree as CT  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


WALK = """# Foo walk

## north star

state: DRAFT
validated-hash:

### must show

- [ ] `ms1` -- the player sees a goat dig a pit

### cannot show

- [ ] `cs1` -- a goat that digs with no order
"""

SHEET = """# Foo

## his words
"Goats dig." 2026-11-01

## does
- [leaf:goat_digs] A goat digs where the player ordered
- [leaf:stays_cheap] It stays cheap
- [floor:log] Clean log
- [advisory] Dirt flies

## does not
- [leaf:no_self_dig] It never digs unordered
- [floor:worldgen] Nothing at world generation
- [waived:w1] Dig sounds

## waived
- w1: dig sounds

## open
- a plain open line does not block

## delegated
- the name of the order

## pruning
- goat_digs: "Goats dig."
- no_self_dig: "Goats dig." read with him 2026-11-01
- reload_walk: the walk leaf is required of every mod
- stays_cheap: "Goats dig."
"""


def leaf(lid, **kw):
    d = dict(id=lid, by="concept", root=["ms1"], leaf_kind="experience", clause_kind="change",
             experience="The player sees a goat dig the marked cell", scenario="goat, marked cell, 1 day",
             false_pass=["The cell is emptied by a colonist"], red="cell still rock after a day",
             oracle_proposed="cell read by state dump", tier_proposed="offline", owner_part="no")
    d.update(kw)
    return d


def draft():
    return {"subject": "Foo", "kind": "mod", "root_ref": "walk.md#north-star", "advisory": ["Dirt flies"],
            "waived": [{"id": "w1", "scope": "dig sounds", "date": "2026-11-01", "ref": "OWNER:111"}],
            "leaves": [leaf("goat_digs", needs_instrument="dig_counter"),
                       leaf("no_self_dig", root=["cs1"], clause_kind="preserve", cannot_show="digs with no order",
                            experience="The player never sees a goat dig unordered", oracle_proposed=None),
                       leaf("dig_counter", leaf_kind="instrument", experience="The log shows a dig count"),
                       leaf("stays_cheap", leaf_kind="constraint", experience="at most 1 ms on his machine"),
                       leaf("reload_walk", leaf_kind="walk", scenario="Dig, save, reload from the save, repeat the "
                            "order, then reverse the order of the two digs")]}


def stage(tmp, dry=False):
    """A repo with a walk, an owner shard and a Foo concept folder, unstamped."""
    repo = os.path.join(tmp, "repo")
    shutil.rmtree(repo, ignore_errors=True)
    d = os.path.join(repo, "design/concepts", CT.DRY_DIR if dry else "", "Foo")
    os.makedirs(d)
    os.makedirs(os.path.join(repo, os.path.dirname(CT.OWNER_SHARD)))
    with open(os.path.join(repo, "walk.md"), "w", encoding="utf-8") as f:
        f.write(WALK)
    with open(os.path.join(repo, CT.OWNER_SHARD), "w", encoding="utf-8") as f:
        f.write(json.dumps({"tsn": 111, "ownerSaid": "Honestly dig sounds don't matter to me"}) + "\n")
    with open(os.path.join(d, "sheet.md"), "w", encoding="utf-8") as f:
        f.write(("DRY WALK\n" if dry else "") + SHEET)
    return repo, d


def validate_walk(repo):
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    from modcheck import northstar as NS
    NS.record_validation(os.path.join(repo, "walk.md"), "selftest stand-in words, a temp file")


def write_raw(d, tree):
    with open(os.path.join(d, "tree.json"), "w", encoding="utf-8") as f:
        json.dump(tree, f)


def main():
    tmp = tempfile.mkdtemp(prefix="concept_tree_")
    try:
        repo, d = stage(tmp)
        validate_walk(repo)
        errs = CT.write(d, draft(), repo)
        check("positive: write", not errs, errs)
        errs, fl = CT.lint(d, repo)
        check("positive: lint passes", not errs, errs)
        floor = CT.load_floor()[0]
        mp = [x for x in floor["lines"] if x["id"] == "multiplayer"][0]
        check("multiplayer is a standing ruling, not waivable, text is his",
              mp["class"] == "standing" and mp["waivable"] is False and mp["default"].startswith("No multiplayer support"), mp)
        check("no flag is raised while no line is open_owner", CT.flags(floor) == [] and not any("multiplayer" in x for x in fl), fl)
        fx = dict(floor, lines=floor["lines"] + [dict(id="fx", **{"class": "open_owner"}, flag="UNANSWERED fx")])
        check("open_owner code path still flags (fixture)", CT.flags(fx) == ["FLAG fx: UNANSWERED fx"], CT.flags(fx))

        errs, _ = CT.gate(d, repo)
        check("unsigned tree: gate refuses", any("signature" in e for e in errs), errs)
        check("only the Arbiter signs", CT.sign(d, "Marker", repo) != [])
        check("sign", CT.sign(d, "Arbiter", repo, at="2026-11-01T00:00:00Z") == [])
        check("sign replaces tree.json whole (no temp left)", not os.path.exists(os.path.join(d, ".tree.json.tmp")))
        errs, _ = CT.gate(d, repo)
        check("positive: gate passes", not errs, errs)
        text = "## verify\n\ndesign/concepts/Foo/tree.json\n"
        check("relentless: passing mod admitted", CT.relentless_refusal(repo, "X", "mod", text) is None)
        check("relentless: one good cite does not vouch for a bad one", "no tree.json" in (CT.relentless_refusal(
            repo, "X", "mod", "<!-- %s -->\n## verify\ndesign/concepts/Missing/tree.json" % text) or ""))
        check("relentless: a cite in other case is still a cite", "no tree.json" in (CT.relentless_refusal(
            repo, "X", "mod", text + " design/concepts/Missing/tree.JSON") or ""))
        check("walk: save is not reload, order is not second order", all(
            re.search(rx, "Save once and repeat the same order", re.I) is None
            for name, rx in CT.WALK_NEEDS.items() if name != "repeat"))
        check("walk: reloader and reversed camera do not count", all(
            re.search(rx, "Inspect the reloader, repeat the same order, then reverse the camera.", re.I) is None
            for name, rx in CT.WALK_NEEDS.items() if name != "repeat"))
        check("walk: the real words count", all(
            re.search(rx, "Reload, repeat it, then the second order", re.I) for rx in CT.WALK_NEEDS.values()))
        outside = os.path.join(repo, "design", "elsewhere")
        os.makedirs(outside, exist_ok=True)
        os.symlink(outside, os.path.join(repo, "design", "concepts", "Linked"))
        check("relentless: a symlink may not climb out", "leaves design/concepts" in (CT.relentless_refusal(
            repo, "X", "mod", "design/concepts/Linked/tree.json") or ""))
        os.remove(os.path.join(repo, "design", "concepts", "Linked"))
        check("relentless: a cite may not climb out", "leaves design/concepts" in (CT.relentless_refusal(
            repo, "X", "mod", text + " design/concepts/../../elsewhere/tree.json") or ""))
        real_load = CT.load
        CT.load = lambda dd: dict(real_load(dd), kind="tool")
        real_gate = CT.gate
        CT.gate = lambda dd, rr: ([], [])
        check("relentless: a mod cannot cite a tool's tree", "not a mod's tree" in (
            CT.relentless_refusal(repo, "X", "mod", text) or ""))
        CT.load, CT.gate = real_load, real_gate

        good = CT.load(d)
        for name, edit, want in (
                ("signature on another hash", lambda t: t["leaves"][0].update(experience="The player sees less"), "another tree"),
                ("edited waiver not in his words", lambda t: t["waived"][0].update(scope="all sound"), "not his words"),
                ("waiver ref finds nothing", lambda t: t["waived"][0].update(ref="OWNER:999"), "finds no event"),
                ("stale root hash", lambda t: t.update(root_hash="0" * 16), "not the walk's")):
            t = copy.deepcopy(good)
            edit(t)
            if name != "signature on another hash":
                t["coverage"]["tree_hash"] = CT.tree_hash(t)
            write_raw(d, t)
            errs, _ = CT.gate(d, repo)
            check("gate: " + name, any(want in e for e in errs), errs)
        for name, edit, want in (
                ("punctuation-only scope", lambda t: t["waived"][0].update(scope="!!!"), "not his words"),
                ("floor.off on no event", lambda t: t["floor"].update(off=[{"line": "save_compat", "words": "skip it",
                                                                            "ref": "OWNER:999"}]), "floor.off save_compat"),
                ("exam waiver on no event", lambda t: t.update(exam_waived={"words": "skip it", "ref": "OWNER:999"}),
                 "exam_waived")):
            t = copy.deepcopy(good)
            edit(t)
            t["coverage"]["tree_hash"] = CT.tree_hash(t)
            write_raw(d, t)
            errs, _ = CT.gate(d, repo)
            check("gate: " + name, any(want in e for e in errs), errs)
        write_raw(d, good)
        t = copy.deepcopy(good)
        t["leaves"] = [x for x in t["leaves"] if "cs1" not in (x.get("root") or [])]
        check("sanity: the fixture has a cs1 leaf to drop", len(t["leaves"]) < len(good["leaves"]))
        write_raw(d, t)
        errs, _ = CT.lint(d, repo)
        check("lint: a north star line on no leaf", any("north star line cs1" in e for e in errs), errs)
        write_raw(d, good)
        sp = os.path.join(d, "sheet.md")
        keep = open(sp, "rb").read()
        with open(sp, "wb") as f:
            f.write(keep.replace(b"## does not", b"-\t[leaf:missing] Required\n## does not", 1))
        errs, _ = CT.lint(d, repo)
        check("lint: a tab after the bullet is a bullet", any("no such leaf: missing" in e for e in errs), errs)
        with open(sp, "wb") as f:
            f.write(keep)
        check("in_words: art is not in start", not CT.in_words("art", "Please start tomorrow"))
        check("in_words: empty is in nothing", not CT.in_words("!!!", "anything"))
        check("in_words: sanity", CT.in_words("the art", "I said: The Art, today"))
        evs = {"1": {"perRuling": "X", "text": "goats dig", "ownerSaid": None}, "2": {"perRuling": True, "text": "sound", "ownerSaid": "goats"},
               "3": {"text": "goats dig"}}
        check("per-ruling text is his word", CT.his_words_problem(evs, "OWNER:1", "goats dig") is None)
        check("per-ruling text must hold the scope", CT.his_words_problem(evs, "OWNER:1", "sound") is not None)
        check("a truthy flag is no ruling", CT.his_words_problem(evs, "OWNER:2", "sound") is not None)
        check("plain text is not his word", CT.his_words_problem(evs, "OWNER:3", "goats dig") is not None)
        sp = os.path.join(d, "sheet.md")
        sheet_bytes = open(sp, "rb").read()
        with open(sp, "ab") as f:
            f.write(b"\n")
        errs, _ = CT.gate(d, repo)
        check("gate: a sheet edited after signing", any("another sheet" in e for e in errs), errs)
        with open(sp, "wb") as f:
            f.write(sheet_bytes + b"* [core] still open\n")
        check("a star bullet is a bullet", CT.TAG.match("* [core] still open") is not None)
        with open(sp, "wb") as f:
            f.write(sheet_bytes)
        t = copy.deepcopy(good)
        t["leaves"][0].update(experience={}, scenario={}, red={}, owner_part={}, tier_proposed={})
        write_raw(d, t)
        errs, _ = CT.lint(d, repo)
        check("lint: objects where text belongs", sum("must be text" in e for e in errs) == 5, errs)
        write_raw(d, good)
        check("gate restored", CT.gate(d, repo)[0] == [])

        # a rewrite voids the signature
        CT.write(d, draft(), repo)
        check("write voids the signature", CT.load(d).get("coverage") is None)

        # the negative table: each one a broken good tree, refused for its own reason
        def on_leaf(i, **kw):
            return lambda t: t["leaves"][i].update(**kw)

        def drop_walk(t):
            t["leaves"] = [x for x in t["leaves"] if x["leaf_kind"] != "walk"]

        table = [
            ("no leaves", lambda t: t.update(leaves=[]), "no leaves"),
            ("unknown top field", lambda t: t.update(budget=1), "not in the schema"),
            ("Setter field in a leaf", on_leaf(0, oracle="x"), "field oracle"),
            ("no observer", on_leaf(0, experience="Dirt moves to the hopper"), "no observer"),
            ("constraint without a number", on_leaf(3, experience="runs fast"), "constraint reads"),
            ("constraint without a machine", on_leaf(3, experience="at most 1 ms"), "constraint reads"),
            ("no false_pass", on_leaf(0, false_pass=[]), "false_pass"),
            ("no red", on_leaf(0, red=""), "red missing"),
            ("no oracle and no cannot_show", on_leaf(0, oracle_proposed=None), "no oracle_proposed"),
            ("live with no reason", on_leaf(0, tier_proposed="quicktest"), "needs tier_reason"),
            ("unknown tier", on_leaf(0, tier_proposed="vibes"), "not in"),
            ("owner_part form", on_leaf(0, owner_part="maybe"), "owner_part"),
            ("root id not in the north star", on_leaf(0, root=["ms9"]), "not in the north star"),
            ("needs worldgen", on_leaf(0, scenario="a new world generation tile"), "worldgen"),
            ("live flight", on_leaf(0, scenario="the flyer takes off", tier_proposed="quicktest", tier_reason="x"),
             "never live-tested"),
            ("worldgen with a blank cannot_show", on_leaf(0, scenario="a new world generation tile", cannot_show=" "), "worldgen"),
            ("floor is not an object", lambda t: t.update(floor="invalid"), "floor is not an object"),
            ("waived holds a non-object", lambda t: t.update(waived=["x"]), "waived is a list"),
            ("blank red", on_leaf(0, red=" "), "red missing"),
            ("leaf id is a list", on_leaf(0, id=[]), "id is text"),
            ("root holds a list", on_leaf(0, root=[[]]), "not in the north star"),
            ("floor.off line is a list", lambda t: t["floor"]["off"].append(dict(line=[], words="w", ref="r")), "no line"),
            ("waiver id is a list", lambda t: t["waived"][0].update(id=[]), "waiver id is text"),
            ("needs_instrument is a list", on_leaf(0, needs_instrument=["dig_counter"]), "needs_instrument must be text"),
            ("does-not leaf with a blank cannot_show", on_leaf(1, cannot_show=" "), "no cannot_show"),
            ("leaves is not a list", lambda t: t.update(leaves=1), "no leaves"),
            ("a repeater is no repeat", on_leaf(4, scenario="reload the save, inspect the repeater, use the reverse order"), "lacks the repeat"),
            ("no walk leaf", drop_walk, "exactly one walk"),
            ("walk without a reload", on_leaf(4, scenario="Repeat the order, reverse the order"), "lacks the reload"),
            ("walk without a repeat", on_leaf(4, scenario="save and reload, reverse the order"), "lacks the repeat"),
            ("needs_instrument dangling", on_leaf(0, needs_instrument="nope"), "no instrument leaf"),
            ("orphan instrument", on_leaf(0, needs_instrument=None), "orphan instrument"),
            ("orphan leaf", lambda t: t["leaves"].append(leaf("stray")), "orphan leaf"),
            ("duplicate leaf id", lambda t: t["leaves"].append(leaf("goat_digs")), "leaf id twice"),
            ("waiver without a ref", lambda t: t["waived"][0].update(ref=""), "required"),
            ("waiver cited as a stand-in in a real tree", lambda t: t["waived"][0].update(stand_in=True), "stand_in"),
            ("waiver not his event", lambda t: t["waived"][0].update(ref="the agent thinks so"), "OWNER:<tsn>"),
            ("standing line off", lambda t: t["floor"]["off"].append(dict(line="worldgen", words="w", ref="r")),
             "cannot be turned off"),
            ("multiplayer answered for him", lambda t: t["floor"]["off"].append(dict(line="multiplayer", words="w", ref="r")),
             "cannot be turned off"),
            ("floor off without his words", lambda t: t["floor"]["off"].append(dict(line="art", words="", ref="r")),
             "needs his words"),
            ("wrong floor hash", lambda t: t["floor"].update(hash="x"), "floor.hash"),
            ("exam waived without words", lambda t: t.update(exam_waived={"ref": "OWNER:1"}), "exam_waived"),
            ("dry-walk flag outside the dry folder", lambda t: t.update(dry_walk=True), "lives under"),
            # the blank-field family: every field that must be text is refused blank AND as another type (txt())
            ("filer with no name", lambda t: t.update(authored_by="filer: "), "authored_by"),
            ("authored_by is a list", lambda t: t.update(authored_by=["concept"]), "authored_by"),
            ("leaf id with a trailing newline", on_leaf(4, id="reload_walk\n"), "not a slug"),
            ("floor.off words as a list", lambda t: t["floor"]["off"].append(dict(line="art", words=["x"], ref="r")),
             "needs his words"),
            ("waiver scope as a list", lambda t: t["waived"][0].update(scope=["dig sounds"]), "required"),
            ("waiver ref as a number", lambda t: t["waived"][0].update(ref=111), "OWNER:<tsn>"),
            ("tier_reason as a list", on_leaf(0, tier_proposed="quicktest", tier_reason=["x"]), "tier_reason must be text"),
            ("tier_reason blank", on_leaf(0, tier_proposed="quicktest", tier_reason=" "), "needs tier_reason"),
            ("advisory holds a blank", lambda t: t.update(advisory=[" "]), "advisory"),
            ("advisory is text", lambda t: t.update(advisory="Dirt flies"), "advisory"),
            ("exam waiver ref blank", lambda t: t.update(exam_waived={"words": "w", "ref": " "}), "exam_waived"),
            ("scenario_informed_by is text", on_leaf(0, scenario_informed_by="x"), "scenario_informed_by"),
            ("false_pass is text", on_leaf(0, false_pass="x"), "false_pass"),
            ("subject is a list", lambda t: t.update(subject=["Foo"]), "subject missing"),
            ("floor.off is text", lambda t: t["floor"].update(off="x"), "floor.off is a list"),
        ]
        base = CT.load(d)
        for name, edit, want in table:
            t = copy.deepcopy(base)
            edit(t)
            write_raw(d, t)
            errs, _ = CT.lint(d, repo)
            check("negative: " + name, any(want in e for e in errs), errs)
        t = copy.deepcopy(base)
        on_leaf(0, scenario="the flyer takes off", tier_proposed="quicktest", tier_reason="x", owner_part="yes: he watches it")(t)
        write_raw(d, t)
        errs, _ = CT.lint(d, repo)
        check("flight with him present is not refused", not any("never live-tested" in e for e in errs), errs)
        for junk in ("{", "[]"):
            with open(os.path.join(d, "tree.json"), "w", encoding="utf-8") as f:
                f.write(junk)
            try:
                got = CT.sign(d, "Arbiter", repo)
            except Exception as ex:
                got = "raised %r" % ex
            check("sign: tree.json %s is refused, not raised" % junk, isinstance(got, list) and got != [], got)
        for nm, k, v in (("coverage", "coverage", "x"), ("exam_waived", "exam_waived", "x"), ("waived", "waived", 1)):
            t = copy.deepcopy(base)
            t[k] = v
            write_raw(d, t)
            try:
                got = CT.gate(d, repo)[0]
            except Exception as ex:
                got = "raised %r" % ex
            check("gate: %s=x is refused, not raised" % nm, isinstance(got, list) and got != [], got)
        check("TREE_CITE does not start mid-path", CT.TREE_CITE.findall("other/design/concepts/Foo/tree.json") == [])
        check("his ref is not a newline-tailed or unicode-digit ref", CT.his_words_problem({"1": {"ownerSaid": "x"}}, "OWNER:1\n", "x") is not None
              and CT.his_words_problem({"1": {"ownerSaid": "x"}}, "OWNER:\u0661", "x") is not None)
        check("TREE_CITE stops at the file name", CT.TREE_CITE.findall("see design/concepts/Foo/tree.json.bak") == [])
        check("TREE_CITE: a backup name is no cite", all(CT.TREE_CITE.findall("design/concepts/Foo/tree.json" + tail) == []
                                                          for tail in ("~", "#1", "+old", ".orig", "%20")))
        check("TREE_CITE: a cite in backticks, parentheses or ending a sentence is a cite (sanity)", all(
            CT.TREE_CITE.findall(t) == ["design/concepts/Foo/tree.json"] for t in (
                "`design/concepts/Foo/tree.json`", "(design/concepts/Foo/tree.json)", "see design/concepts/Foo/tree.json.",
                "design/concepts/Foo/tree.json")))
        check("relentless: a backup-named cite admits nothing", "no tree" in (CT.relentless_refusal(
            repo, "X", "mod", "## verify\n\ndesign/concepts/Foo/tree.json~\n") or ""))
        t = copy.deepcopy(base)
        t["leaves"][0]["experience"] = "The player sees \ud800"
        write_raw(d, t)
        check("a lone surrogate in tree.json is refused, not raised", any("does not parse" in e for e in CT.lint(d, repo)[0])
              and CT.main(["hash", d]) == 1)
        write_raw(d, base)
        write_raw(d, base)

        # the sheet's half
        sp = os.path.join(d, "sheet.md")
        for name, old, new, want in (
                ("does line maps to nothing", "- [advisory] Dirt flies", "- Dirt flies", "maps to nothing"),
                ("does-not line to advisory", "- [waived:w1] Dig sounds", "- [advisory] Dig sounds", "maps to nothing"),
                ("does-not names a leaf with no cannot_show", "[leaf:no_self_dig] It", "[leaf:goat_digs] It", "no cannot_show"),
                ("unknown floor line", "[floor:log]", "[floor:vibes]", "no floor line"),
                ("unknown waiver", "[waived:w1]", "[waived:w9]", "no waiver"),
                ("core line open", "- a plain open line does not block", "- [core] do goats tire?", "core line is still open"),
                ("no pruning answer", '- goat_digs: "Goats dig."\n', "", "pruning: leaf goat_digs"),
                ("no section", "## delegated\n", "## delegates\n", "no `## delegated`"),
                ("his words empty", '"Goats dig." 2026-11-01\n', "", "his words"),
                ("tagged line with no text", "- [advisory] Dirt flies", "- [advisory]  ", "says nothing"),
                ("numbered core line open", "- a plain open line does not block", "1. [core] do goats tire?",
                 "core line is still open"),
                ("core tag mid-line", "- a plain open line does not block", "Q: [core] do goats tire?", "core line is still open"),
                ("fenced heading cannot re-section", "- a plain open line does not block",
                 "```\n## delegated\n```\n- [core] do goats obey a cancel?", "not plain bullets"),
                ("a fence closer with text after it is no closer", "- a plain open line does not block",
                 "```text\n```not-a-close\n## delegated\n```\n- [core] do goats obey a cancel?", "not plain bullets"),
                ("an indented fence is refused too", "## delegated\n", "## later\n    ```\n## delegated\n    ```\n",
                 "not plain bullets"),
                ("a core tag in a heading's note", "## open\n", "## open ([core] do goats tire?)\n", "not plain bullets"),
                ("a setext heading", "## delegated\n", "## delegated\ndoes\n---\n", "not plain bullets"),
                ("a setext h1", "## delegated\n", "## delegated\ndoes\n===\n", "not plain bullets"),
                ("an HTML heading", "## delegated\n", "## delegated\n<h2>does</h2>\n", "not plain bullets"),
                ("an HTML comment", "## delegated\n", "## delegated\n<!-- note -->\n", "not plain bullets"),
                ("a spaced core tag in open", "- a plain open line does not block", "- [ Core ] do goats tire?",
                 "core line is still open"),
                ("a core tag with a note outside open", "- the name of the order", "- [core:x] the name of the order",
                 "outside `## open`"),
                ("an entity-spelled core tag", "- a plain open line does not block", "- [c&#111;re] do goats tire?",
                 "core line is still open"),
                ("a bold core tag", "- a plain open line does not block", "- [**core**] do goats tire?", "core line is still open"),
                ("a zero-width core tag", "- a plain open line does not block", "- [c\u200bore] do goats tire?",
                 "core line is still open"),
                ("a fullwidth core tag", "- a plain open line does not block", "- \uff3bcore\uff3d do goats tire?",
                 "core line is still open"),
                ("a homoglyph core tag", "- a plain open line does not block", "- [c\u043ere] do goats tire?",
                 "not plain bullets"),
                ("a tilde fence is refused too", "## delegated\n", "~~~\n## delegated\n", "not plain bullets"),
                ("unknown section", "## delegated\n", "## unanswered\n- [core] do goats tire?\n## delegated\n",
                 "no section of the sheet"),
                ("core line in delegated", "- the name of the order", "- [core] the name of the order", "outside `## open`"),
                ("a dry walk's root section in a real sheet", "## delegated\n", "## root\n- ms1: x\n## delegated\n",
                 "no section of the sheet"),
                ("core line before the first section", "# Foo\n", "# Foo\n- [core] do goats obey a cancel?\n",
                 "outside `## open`"),
                ("a heading with a trailing hash", "## open\n", "## open #\n", "not plain bullets"),
                ("an indented heading", "## delegated\n", "  ## delegated\n", "not plain bullets"),
                ("a sub-heading", "## delegated\n", "## delegated\n### detail\n", "not plain bullets"),
                ("unbulleted promise in does", "- [advisory] Dirt flies", "- [advisory] Dirt flies\nGoats stop when cancelled.",
                 "not a bullet"),
                ("numbered does line names no leaf", "- [floor:log] Clean log", "1) [leaf:ghost] Clean log", "no such leaf")):
            with open(sp, "w", encoding="utf-8") as f:
                f.write(SHEET.replace(old, new))
            check("sheet: %s (fixture took)" % name, old in SHEET)
            errs, _ = CT.lint(d, repo)
            check("sheet: " + name, any(want in e for e in errs), errs)
        with open(sp, "w", encoding="utf-8") as f:
            f.write(SHEET.replace("- goat_digs:", "* goat_digs:"))
        check("sheet: a star bullet answers pruning too", CT.lint(d, repo)[0] == [], CT.lint(d, repo)[0])
        with open(sp, "w", encoding="utf-8") as f:
            f.write(SHEET + "\n## later\n- goats that swim, v2\n")
        check("sheet: `## later` is a section (sanity)", CT.lint(d, repo)[0] == [], CT.lint(d, repo)[0])
        tp = os.path.join(d, "tree.json")
        keep_tree = open(tp, "rb").read()
        deep = '{"x":' + "[" * 200000 + "0" + "]" * 200000 + "}"     # deep enough to raise RecursionError in json
        with open(tp, "w", encoding="utf-8") as f:
            f.write(deep)
        check("deep nesting: lint refuses, not raises", any("does not parse" in e for e in CT.lint(d, repo)[0]))
        check("deep nesting: hash and askcheck exit 1", CT.main(["hash", d]) == 1 and CT.main(["askcheck", d, "q"]) == 1)
        with open(tp, "wb") as f:
            f.write(keep_tree)
        dj2 = os.path.join(tmp, "deep_draft.json")
        with open(dj2, "w", encoding="utf-8") as f:
            f.write(deep)
        check("deep nesting: cli write exit 1", CT.main(["write", d, "--draft", dj2]) == 1)
        check("deep nesting: and tree.json is untouched", open(tp, "rb").read() == keep_tree)
        op = os.path.join(repo, CT.OWNER_SHARD)
        shard = open(op, "rb").read()
        with open(op, "wb") as f:
            f.write(("[" * 200000 + "0" + "]" * 200000 + "\n").encode() + shard)
        check("owner_events: a deep line is skipped, not raised", "111" in CT.owner_events(repo))
        with open(op, "wb") as f:
            f.write(shard)
        os.remove(tp)
        os.makedirs(tp)
        got = CT.lint(d, repo)[0]
        check("tree.json as a directory: lint refuses, not raises", any("cannot be read" in e for e in got), got)
        check("tree.json as a directory: gate, sign, hash, askcheck refuse", CT.gate(d, repo)[0] != []
              and CT.sign(d, "Arbiter", repo) != [] and CT.main(["hash", d]) == 1 and CT.main(["askcheck", d, "q"]) == 1)
        os.rmdir(tp)
        with open(tp, "wb") as f:
            f.write(keep_tree)
        with open(sp, "wb") as f:
            f.write(SHEET.encode("utf-8") + b"\xff\n")
        got = CT.lint(d, repo)[0]
        check("sheet: bad UTF-8 is refused, not raised", any("cannot be read" in e for e in got), got)
        op = os.path.join(repo, CT.OWNER_SHARD)
        shard = open(op, "rb").read()
        with open(op, "wb") as f:
            f.write(b"\xff\n" + shard)
        check("owner_events: a bad byte spoils its line only", "111" in CT.owner_events(repo))
        with open(op, "wb") as f:
            f.write(shard)
        with open(sp, "w", encoding="utf-8") as f:
            f.write(SHEET)
        check("sheet restored", CT.lint(d, repo)[0] == [])
        os.remove(sp)
        check("no sheet", "no sheet.md" in CT.lint(d, repo)[0])
        with open(sp, "w", encoding="utf-8") as f:
            f.write(SHEET)

        # writer
        bad = draft()
        bad["binding"] = {}
        try:
            CT.write(d, bad, repo)
            check("write refuses an unknown draft key", False)
        except ValueError:
            check("write refuses an unknown draft key", True)
        bad = draft()
        before = open(os.path.join(d, "tree.json"), encoding="utf-8").read()
        bad["leaves"][0]["red"] = ""
        check("write refuses a bad shape", CT.write(d, bad, repo) != [])
        check("and writes nothing", open(os.path.join(d, "tree.json"), encoding="utf-8").read() == before)

        bad = draft()
        bad["leaves"].append("not a leaf")
        check("write: a non-object leaf is an error, not a raise", any("not an object" in e for e in CT.write(d, bad, repo)))
        try:
            CT.write(d, ["not", "a", "draft"], repo)
            check("write refuses a non-object draft", False)
        except ValueError:
            check("write refuses a non-object draft", True)
        dj = os.path.join(tmp, "bad_draft.json")
        with open(dj, "w", encoding="utf-8") as f:
            f.write("{")
        check("cli write: a draft that does not parse is reported, exit 1", CT.main(["write", d, "--draft", dj]) == 1)
        empty = os.path.join(tmp, "empty_concept")
        os.makedirs(empty)
        check("cli askcheck: no tree.json yet (Stage 1) is clear, not a crash", CT.main(["askcheck", empty, "dig sounds?"]) == 0)
        check("cli hash: no tree.json is exit 1, not a crash", CT.main(["hash", empty]) == 1)
        with open(os.path.join(tmp, "outside.md"), "w", encoding="utf-8") as f:
            f.write(WALK)
        check("walk_root: a root_ref may not leave the repo", "leaves the repo" in str(CT.walk_root(repo, "../outside.md#north-star")[3]))
        check("his words: a list of words is no words", CT.his_words_problem({"1": {"ownerSaid": "x"}}, "OWNER:1", ["x"]) is not None)
        check("askcheck: a number for a waiver id is no crash", CT.askcheck({"waived": [{"id": 1, "scope": "dig sounds"}]},
                                                                             "dig sounds") == ["1"])
        check("askcheck: a malformed waiver list is no crash", CT.askcheck({"waived": [1, {"scope": ["x"]}]}, "x") == []
              and CT.askcheck({"waived": "dig sounds"}, "dig sounds") == [])

        # askcheck
        t = CT.load(d)
        check("askcheck: a repeat is caught", CT.askcheck(t, "what about the dig sounds then?") == ["w1"])
        check("askcheck: another question is clear", CT.askcheck(t, "does the goat tire?") == [])

        # a dry walk can never pass the gate
        os.makedirs(os.path.join(tmp, "dry"), exist_ok=True)
        repo2, d2 = stage(os.path.join(tmp, "dry"), dry=True)
        dr = draft()
        dr["waived"][0].update(ref="dry_walk:round2", stand_in=True)
        with open(os.path.join(d2, "sheet.md"), "a", encoding="utf-8") as f:
            f.write("\n## root (stand-in, not his)\n- ms1: x\n- cs1: y\n")
        errs = CT.write(d2, dr, repo2, dry=True)
        check("dry: write", not errs, errs)
        check("dry: lint passes", not CT.lint(d2, repo2)[0], CT.lint(d2, repo2)[0])
        check("dry: never signed", CT.sign(d2, "Arbiter", repo2) != [])
        errs, _ = CT.gate(d2, repo2)
        check("dry: gate refuses", any("dry walk" in e for e in errs), errs)
        t = CT.load(d2)
        t["waived"][0].pop("stand_in")
        write_raw(d2, t)
        check("dry: waiver must be marked stand_in", any("stand_in" in e for e in CT.lint(d2, repo2)[0]))
        t["waived"][0].update(stand_in=True, ref="dry_walk:")
        write_raw(d2, t)
        check("dry: a stand-in ref names its round", any("stand_in" in e for e in CT.lint(d2, repo2)[0]))
        t = CT.load(d2)
        sheet = open(os.path.join(d2, "sheet.md"), encoding="utf-8").read()
        with open(os.path.join(d2, "sheet.md"), "w", encoding="utf-8") as f:
            f.write(sheet.replace("DRY WALK\n", ""))
        check("dry: unbannered sheet refused", any("DRY WALK" in e for e in CT.lint(d2, repo2)[0]))

        # relentless_refusal
        check("relentless: mod with no tree refused", "no tree" in (CT.relentless_refusal(repo, "X", "mod", "body") or ""))
        check("relentless: mod citing a missing tree refused",
              CT.relentless_refusal(repo, "X", "mod", "design/concepts/Bar/tree.json") is not None)
        check("relentless: non-mod citing an unsigned tree refused",
              CT.relentless_refusal(repo, "X", "feature", text) is not None)
        check("relentless: tooling item untouched", CT.relentless_refusal(repo, "X", "feature", "body") is None)
        check("relentless: dry walk refused", CT.relentless_refusal(
            repo2, "X", "mod", "design/concepts/_dry_walk/Foo/tree.json") is not None)
        check("item_file_text: missing item reads empty, so a mod is refused", CT.item_file_text(repo, "NOPE") == "")

        tiers = CT.load_floor()[0]["tiers"]
        sweep = leaf("kept_shape", by="setter_sweep", root=["tool"], clause_kind="change")
        check("setter_sweep: a change leaf is refused", any("only preserves" in e for e in CT.leaf_errors(sweep, "tool", tiers, set())))
        sweep["clause_kind"] = "preserve"
        check("setter_sweep: a preserve leaf is not (sanity)", CT.leaf_errors(sweep, "tool", tiers, set()) == [],
              CT.leaf_errors(sweep, "tool", tiers, set()))

        # the wiring: lease asks, and a refused mod gets no worker
        import relentless as R
        src = open(R.__file__, encoding="utf-8").read()
        check("pool_order filters mods through the gate", 'i.kind != "mod" or not self.concept_refusal(i.id)' in src)
        check("enrol refuses", "relentless: REFUSED: %s\" % refusal" in src)
        import selftest_relentless as SR
        x = SR.Rig(2, share=1.0)
        x.w.concept_refusal = lambda item: "no tree" if item == "I0" else None
        for _ in range(4):
            x.tick()
        launched = str(x.w.launches)
        check("lease: the refused mod gets no worker", "I0" not in launched, launched[:200])
        check("lease: the other item still does (sanity)", "I1" in launched, launched[:200])
        acts = []
        R.lease(x.s, x.w, x.r, x.now, acts)
        check("lease: the refusal is said", any(a.get("do") == "concept_refused" and a.get("item") == "I0" for a in acts), acts)
        check("Effects has the method", hasattr(R.Effects, "concept_refusal"))
        got = R.concept_refused(repo, "NOPE", "mod")
        check("concept_refused: a mod with no body is refused", "no tree" in (got or ""), got)
        check("concept_refused: a bugfix passes", R.concept_refused(repo, "NOPE", "feature") is None)

        # the role cannot start on its own
        with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
            sched = json.load(f)
        # found by its ledger item, never by name: the owner is still choosing the name, and a rename must be
        # one edit to the row (name, instructions, off_file) plus a git mv of the role file
        row = [r for r in sched["roles"] if r.get("ledger_item") == "CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING"]
        check("Designer row exists, off, no slots", len(row) == 1 and row[0]["enabled"] is False
              and not row[0].get("runs_local"), row)
        name = row[0]["name"] if row else None
        check("Designer not in golive", name is not None and name not in sched["golive"]["roles"])
        inst = row[0].get("instructions", "") if row else ""
        check("role file exists where the row says", bool(inst) and os.path.isfile(
            os.path.join(HERE, "..", "..", "..", inst)), inst)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest_concept_tree: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
