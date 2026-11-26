#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_TOUGHEN_DESIGNER_ENTRY_GATE_VAGUE_BUILDS_CHOKED.

His words (2026-11-17): "I think we need to be much tougher about how well defined an item needs to be before it's
allowed into the build step. Designer isn't being harsh enough in terms of imprecision and completeness."

The tougher definition was argued with him in RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED: the six-part
bar (design/specs/2026-11-16-designer-cleanse-and-bar-definition.md §3). Measured 2026-11-26 on 2383842063: the door into
the build (the Designer's Lock gate, `concept_tree.py gate`, which runs Gate A `lint`) knew only the old leaf schema. An
applied cleansed design (Cauldron) read REFUSED (284): every six-part field "is not the tree's", the old fields missing.
So no six-part design could lock, and the only definition that could pass into the build was the old, looser one.

    --part cleansed   Gate A judges a six-part tree by the six-part definition:
                      every real cleanse proposal that apply would write lints with no refusal of the old schema (each
                      refusal left names a fault of the definition, prefixed `definition:`); at least one lints clean;
                      on that clean tree each planted vague or incomplete bar is refused, naming the part.
    --part new        a new design is written with six-part bars: `concept_tree.py write` takes a six-part draft and
                      refuses an old-schema draft for a mod; the Write brief teaches the six parts; locked old trees
                      lint as before.

    exit 0 = pass, 1 = fail. The builder does not edit this file.
"""
import argparse
import copy
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

CT, why_ct = H.load("concept_tree")
DC, why_dc = H.load("designer_cleanse")
CONCEPTS = os.path.join(H.REPO, "design", "concepts")
DEF = "definition: "


def applied(mod, root):
    """The concept folder as `designer_cleanse.py apply <mod> --write` would leave it, copied under `root`; None when
    apply would not write."""
    plan = DC.apply_plan(H.REPO, mod)
    if plan.get("answer") != "WOULD_WRITE":
        return None
    d = os.path.join(root, mod)
    shutil.copytree(os.path.join(CONCEPTS, mod), d)
    for rel, text in (plan.get("files") or {}).items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    return d


def lint(d):
    return CT.lint(d, H.REPO)[0]


def tree_of(d):
    with open(os.path.join(d, "tree.json"), encoding="utf-8") as f:
        return json.load(f)


def put_tree(d, tree):
    with open(os.path.join(d, "tree.json"), "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=1)


def cleansed(root):
    mods = sorted(m for m in os.listdir(CONCEPTS) if os.path.isdir(os.path.join(CONCEPTS, m, "cleanse")))
    got = {}
    for m in mods:
        d = applied(m, root)
        if d:
            got[m] = (d, lint(d))
    schema = {m: [e for e in errs if not e.startswith(DEF)] for m, (d, errs) in got.items()}
    H.check("every applied proposal (%d) is judged by the six-part definition, not refused by the old schema" % len(got),
            lambda: got and not any(schema.values()) or (_ for _ in ()).throw(AssertionError(
                "; ".join("%s: %d, e.g. %s" % (m, len(v), v[0][:100]) for m, v in schema.items() if v)[:900] or
                "no proposal that apply would write")))
    clean = [m for m, (d, errs) in got.items() if not errs]
    H.check("at least one real applied proposal lints clean (%s)" % (", ".join(clean) or "none"), lambda: clean)
    if not clean:
        return
    base = got[clean[0]][0]

    def plant(name, edit, want):
        d = os.path.join(root, "plant_" + name)
        shutil.copytree(base, d)
        t = tree_of(d)
        edit(t)
        put_tree(d, t)
        errs = [e for e in lint(d) if e.startswith(DEF)]
        H.check("planted %s is refused naming %r" % (name, want),
                lambda: any(want in e for e in errs) or (_ for _ in ()).throw(AssertionError(
                    "refusals: %s" % (errs[:4] or "none"))))

    def first(t):
        return next(b for b in t["leaves"] if b["id"] != t.get("whole"))

    plant("number", lambda t: first(t).update(says=first(t)["says"] + " in 30% of the cases"), "pins a number")
    plant("no_range", lambda t: first(t).pop("range"), "range")
    plant("no_figurative", lambda t: first(t)["meant"].pop("figurative"), "meant.figurative")
    plant("sees_off", lambda t: first(t)["sees"].update(on=""), "sees.on")
    plant("lazy_not_rejected", lambda t: first(t).update(lazy="a build nobody pictured"), "lazy")
    plant("one_accept", lambda t: first(t).update(accept=[]), "accept")
    plant("no_meetings", lambda t: t.update(meetings=[]), "meeting")
    plant("no_whole", lambda t: t.update(whole="nothing_here"), "whole")
    plant("old_leaf_mixed", lambda t: t["leaves"].append({"id": "old_style", "experience": "the player sees a thing",
                                                          "red": "it is gone", "false_pass": ["a lie"]}), "six-part")


def new(root):
    src = os.path.join(root, "src")
    os.makedirs(src)
    clean = None
    for m in sorted(os.listdir(CONCEPTS)):
        if os.path.isdir(os.path.join(CONCEPTS, m, "cleanse")):
            d = applied(m, src)
            if d and not lint(d):
                clean = d
                break
    H.check("a clean applied six-part tree exists to draft from", lambda: clean)
    if clean:
        t = tree_of(clean)
        draft = {k: t[k] for k in ("subject", "kind", "root_ref", "leaves", "whole", "checks", "rules", "meetings")
                 if k in t}
        draft["leaves"] = [{k: v for k, v in b.items() if k != "experience"} for b in draft["leaves"]]
        d = os.path.join(root, "new_six")
        shutil.copytree(clean, d)
        os.remove(os.path.join(d, "tree.json"))
        errs = CT.write(d, copy.deepcopy(draft), H.REPO)
        H.check("`write` takes a six-part draft and the tree it writes passes Gate A",
                lambda: not errs and not lint(d) or (_ for _ in ()).throw(AssertionError(
                    "write: %s; lint: %s" % (errs[:3], lint(d)[:3] if not errs else "-"))))
    old = {"subject": "Fixture", "kind": "mod", "root_ref": "", "leaves": [{
        "id": "a_leaf", "root": [], "leaf_kind": "experience", "experience": "the player sees the fixture glow",
        "scenario": "a map", "false_pass": ["a lamp"], "red": "no glow", "tier_proposed": "offline",
        "oracle_proposed": "read the glow"}]}
    d = os.path.join(root, "new_old")
    os.makedirs(d)
    errs = CT.write(d, old, H.REPO)
    H.check("`write` refuses an old-schema draft for a mod, naming the six parts",
            lambda: any(e.startswith(DEF) and "six-part" in e for e in errs) or (_ for _ in ()).throw(AssertionError(
                "write said: %s" % (errs[:3] or "nothing (it wrote the tree)"))))
    brief = open(os.path.join(H.RIMFLOW, "roles", "designer_write.md"), encoding="utf-8").read()
    parts = ("`says`", "`meant`", "`figurative`", "`accept`", "`reject`", "`lazy`", "`range`", "`sees`", "`touches`",
             "`meetings`", "`whole`")
    H.check("the Write brief teaches every part of the six-part bar",
            lambda: all(p in brief for p in parts) or (_ for _ in ()).throw(AssertionError(
                "missing: %s" % [p for p in parts if p not in brief])))
    for m in ("Pyrelands", "FlowWorks", "ExplosiveKnockback"):
        dm = os.path.join(CONCEPTS, m)
        if os.path.isfile(os.path.join(dm, "tree.json")):
            H.check("locked old tree %s gets no definition refusal" % m,
                    lambda dm=dm: not [e for e in lint(dm) if e.startswith(DEF)] or (_ for _ in ()).throw(
                        AssertionError([e for e in lint(dm) if e.startswith(DEF)][:2])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("cleansed", "new"), required=True)
    a = ap.parse_args()
    if CT is None or DC is None:
        print("FAIL  %s" % (why_ct or why_dc))
        return 1
    root = tempfile.mkdtemp(prefix="definition_gate_")
    try:
        (cleansed if a.part == "cleansed" else new)(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    ok = H.RESULTS and all(H.RESULTS)
    print("%s %d/%d" % ("PASS" if ok else "FAIL", sum(H.RESULTS), len(H.RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
