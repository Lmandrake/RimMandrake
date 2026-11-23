#!/usr/bin/env python3
"""Offline selftest of designer_stage.py's hand-over of the universal-mechanics conversion list to a mod's next
version: one test per promise on design/specs/2026-11-21-guiding-principles/boundary.md, each named after it, plus the
rule-text checks of item RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES (t_rule_texts_*).

    python3 src/RimMandrake/rimflow/selftest_conversion_owed.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_conversion_owed.py --only t_x ...  those alone
"""
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LIST = "design/specs/2026-11-21-guiding-principles/conversion_list.md"
TMP = tempfile.mkdtemp(prefix="selftest_conversion_owed_")
FAILS = []

FIXTURE = """# list

## Alpha

- Version on 2026-11-21: `0.1.0`

| census row | file:line | what is confined | class |
|---|---|---|---|
| code 2 | `src/RimMandrake/Alpha/Source/Dive.cs:76` | dives only on an Alpha map | MECHANIC-GATE |

## Beta

- Version on 2026-11-21: `none`

| code 9 | `src/RimMandrake/Beta/Source/X.cs:1` | beta-only glow | MECHANIC-GATE |

## Gamma

- Folders: no version line here

## Rule texts (corrected by this item)

- R1
"""


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def write(rel, text):
    p = os.path.join(TMP, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def concept(name, version=None, raw=None):
    d = os.path.join(TMP, "design", "concepts", name)
    os.makedirs(d, exist_ok=True)
    vp = os.path.join(d, "version", "VERSION.json")
    if raw is not None:
        write(os.path.relpath(vp, TMP), raw)
    elif version is not None:
        write(os.path.relpath(vp, TMP), json.dumps({"version": version}))
    return d


def st(name, **kw):
    s = {"mod": name, "stage": 3, "item": "ITEM_" + name.upper()}
    s.update(kw)
    return s


def packet_text(d, s):
    return DS.packet(d, s, {}, None, repo=TMP)


def t_owed_at_next_version():
    """A version newer than the list's, or a list version `none`, is owed; the packet names the path and the rows."""
    write(LIST, FIXTURE)
    d = concept("Alpha", "0.2.0")
    state, why, sec = DS.conversion_owed(TMP, d, st("Alpha"))
    check(state == "owed", "Alpha 0.2.0 against 0.1.0 is owed", (state, why))
    check(sec is not None and "Dive.cs:76" in sec, "the section's rows come back", sec)
    p = packet_text(d, st("Alpha"))
    check("Owed input: the universal-mechanics conversion" in p and LIST in p and "Dive.cs:76" in p,
          "the packet names the list, the heading and the rows", p[-600:])
    check("offline test" not in p and "home biome" in p and "plain on/off" in p,
          "the packet demands no offline test, tests on the home biome, and turns the switch into a plain on/off",
          p[-600:])
    d = concept("Beta", "0.1.0")
    check(DS.conversion_owed(TMP, d, st("Beta"))[0] == "owed", "a list version `none` is owed at any version")
    d = concept("Alpha2", "0.1.1")
    check(DS.conversion_owed(TMP, d, st("Alpha2", aliases=["Alpha"]))[0] == "owed",
          "an alias in stage.json finds the section")


def t_current_version_not_owed():
    """The list's own version is not owed; no VERSION.json reads 0.1.0; a pre-release of it is not newer."""
    write(LIST, FIXTURE)
    for v, label in (("0.1.0", "the same version"), (None, "no VERSION.json"), ("0.1.0-rc.2", "a pre-release tail")):
        d = concept("Alpha", v) if v else concept("AlphaNoVer")
        s = st("Alpha") if v else st("AlphaNoVer", aliases=["Alpha"])
        if not v:
            shutil.rmtree(os.path.join(d, "version"), ignore_errors=True)
        state, why, _ = DS.conversion_owed(TMP, d, s)
        check(state == "not_yet", "%s is not owed" % label, (state, why))
    d = concept("Alpha", "0.1.0")
    p = packet_text(d, st("Alpha"))
    check("next version, never in this one" in p and "Dive.cs:76" not in p,
          "the packet says it converts at the next version and lists no row as owed", p[-600:])


def t_no_section_is_none_owed():
    """A mod with no section is none; the Rule texts section is not a mod."""
    write(LIST, FIXTURE)
    d = concept("Delta", "0.3.0")
    state, why, sec = DS.conversion_owed(TMP, d, st("Delta"))
    check(state == "none" and sec is None, "Delta has no section: none", (state, why))
    check("names no row for this mod" in packet_text(d, st("Delta")), "the packet says none")


def t_unreadable_is_unmeasured():
    """Absent list, no version line, a VERSION.json that does not parse: unmeasured with the cause, never none."""
    lp = os.path.join(TMP, LIST)
    if os.path.exists(lp):
        os.remove(lp)
    d = concept("Alpha", "0.2.0")
    state, why, _ = DS.conversion_owed(TMP, d, st("Alpha"))
    check(state == "unmeasured" and "absent" in why, "an absent list is unmeasured", (state, why))
    check("UNMEASURED" in packet_text(d, st("Alpha")), "the packet says UNMEASURED")
    write(LIST, FIXTURE)
    d = concept("Gamma", "0.2.0")
    state, why, _ = DS.conversion_owed(TMP, d, st("Gamma"))
    check(state == "unmeasured" and "version line" in why, "a section with no version line is unmeasured", (state, why))
    d = concept("Alpha", raw="{not json")
    state, why, _ = DS.conversion_owed(TMP, d, st("Alpha"))
    check(state == "unmeasured" and "VERSION.json" in why, "a VERSION.json that does not parse is unmeasured",
          (state, why))
    d = concept("Alpha", "zero")
    check(DS.conversion_owed(TMP, d, st("Alpha"))[0] == "unmeasured", "a version that is not semver is unmeasured")


def t_real_list_is_readable():
    """The committed list: one readable version line per mod section; the real Pyrelands 0.1.0 is not owed."""
    with open(os.path.join(ROOT, LIST), encoding="utf-8") as f:
        text = f.read()
    secs = DS.conversion_sections(text)
    check(len(secs) >= 20, "the real list has its mod sections", len(secs))
    mods = [h for h in secs if " " not in h]          # a mod heading is a bare name; the two notes sections are not
    bad = [h for h in mods if DS.conversion_base(secs[h])[0] is None]
    check(not bad, "every mod section has one readable version line", bad)
    check(sorted(h for h in secs if " " in h) == ["Dated design records that state the old reading",
                                                  "Rule texts (corrected by this item)"],
          "the only non-mod sections are the two notes sections", sorted(h for h in secs if " " in h))
    pd = os.path.join(ROOT, "design", "concepts", "Pyrelands")
    state, why, _ = DS.conversion_owed(ROOT, pd, {"mod": "Pyrelands"})
    check(state == "not_yet", "Pyrelands 0.1.0 is not reworked: not owed in its current version", (state, why))


def t_rule_texts_corrected():
    """The reversed rule texts are gone and the ruled text is in place (red on the base commit)."""
    def read(rel):
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    floor = {ln["id"]: ln for ln in json.loads(read("src/RimMandrake/rimflow/concept_floor.json"))["lines"]}
    bs = floor.get("biome_scope", {}).get("default", "")
    check("inside our biomes only" not in bs and "physical conditions" in bs and "home biome" in bs,
          "concept_floor biome_scope is the ruled rule", bs)
    check(floor.get("biome_scope", {}).get("waivable") is False, "biome_scope stays a standing, unwaivable line")
    check("biomes in scope only" not in read("src/RimMandrake/rimflow/roles/designer_write.md"),
          "designer_write no longer confines a mechanic to its biome")
    root = read("CLAUDE.md")
    check("only inside our own biomes" not in root and "## A mechanic works by its physical conditions" in root,
          "root CLAUDE.md: the confinement line is gone and the principle section is in")
    # His ruling of 2026-11-21 (card two): no offline test is owed; the rule is a default, not a ban; a stated load
    # exception is allowed; the Scald's hot water is physics, not a biome exception.
    texts = {rel: read(rel) for rel in ("CLAUDE.md", "GUIDING_PRINCIPLES.md", "design/RimMandrake/standing_rulings.md",
                                       "design/RimMandrake/biome_rulings.md",
                                       "src/RimMandrake/rimflow/roles/designer_write.md",
                                       "src/RimMandrake/rimflow/roles/designer.md",
                                       "src/RimMandrake/rimflow/concept_floor.json",
                                       "design/specs/2026-11-21-guiding-principles/conversion_list.md")}
    for rel, t in texts.items():
        flat = re.sub(r'\*"[^*]*"\*', "", " ".join(t.split()))   # his words and card text quoted *"…"* are records
        check("only the biome name changed" not in flat and "change only the biome name" not in flat
              and "changes only the biome name" not in flat, "%s demands no offline name-swap test" % rel)
        check("Do not build a new biome check" not in flat and "never which biome it is in" not in flat
              and "It never reads which biome" not in flat, "%s states the rule as a default, not a ban" % rel)
    check("except one: the Scald" not in " ".join(root.split()), "root CLAUDE.md: the Scald is not a heat exception")
    check("heavy load even where it is not active" in " ".join(texts["GUIDING_PRINCIPLES.md"].split()),
          "GUIDING_PRINCIPLES.md keeps the stated load exception")
    sr = read("design/RimMandrake/standing_rulings.md")
    check("Biome mechanics are promised inside our own biomes only" not in sr
          and "## Biome mechanics work by their conditions" in sr
          and "we're not going to validate that at this time" in " ".join(sr.split()),   # his words, any line wrap
          "standing_rulings: his 2026-10-15 words stay")
    gp = read("GUIDING_PRINCIPLES.md")
    entries = [ln for ln in gp.splitlines() if ln.startswith("## ") and "(RULED " in ln]
    check(1 <= len(entries) <= 7, "GUIDING_PRINCIPLES.md has 1 to 7 ruled entries", len(entries))
    check("## Proposed, not ruled" in gp, "GUIDING_PRINCIPLES.md keeps a place for proposals")


def main(argv):
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    try:
        for f in (t_owed_at_next_version, t_current_version_not_owed, t_no_section_is_none_owed,
                  t_unreadable_is_unmeasured, t_real_list_is_readable, t_rule_texts_corrected):
            if only and f.__name__ not in only:
                continue
            print("--", f.__name__)
            try:
                f()
            except Exception as e:  # noqa: BLE001  a crash is a failure of that test, named
                check(False, "%s raised %s: %s" % (f.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_conversion_owed: %s" % ("PASS" if not FAILS else "FAILED (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
