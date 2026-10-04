#!/usr/bin/env python3
"""selftest_shipped_defs.py -- offline proof for modcheck/shipped_defs.py (the every-shipped-def readback chain).

Run bare: python3 src/RimMandrake/Utils/modcheck/selftest_shipped_defs.py   (exit 0 = clean)

A synthetic mod (abstract parent, three defs of two types, a nested element, a bool) is read back through a mock
`jawa/get_defs` that serves the XML's own values. Clean must be green; each break reddens exactly the component
that owns it. Then every real mod wired to the helper is parsed, and must find its own sanity names.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
for p in (UTILS, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
from modcheck import Suite, shipped_defs                       # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
XML = """<Defs>
  <ThingDef Name="ParentX" Abstract="True"><defName>AbstractNeverRead</defName><label>no</label></ThingDef>
  <ThingDef ParentName="ParentX"><defName>T_One</defName><label>one</label><statBases><Mass>2</Mass></statBases></ThingDef>
  <ThingDef><defName>T_Two</defName><label>two</label><stackLimit>75</stackLimit></ThingDef>
  <RecipeDef><defName>R_Make</defName><label>make one</label><workAmount>800</workAmount><allowMixingIngredients>true</allowMixingIngredients></RecipeDef>
</Defs>"""

# real mods wired to the helper: (mod folder under src, sanity names, min_count)
WIRED = [
    ("RimStarWars/Cuisine", ("RSW_SaltCuredRation_White", "RSW_CureWithAmberSalt", "RSW_AteCrystalSaltCured"), 30),
    ("RimUtinni/Antiquities", ("RUT_AntiquityCipherBench",), 8),
]


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def make_ext(brk, mod_dir):
    parsed = dict((n, leaf) for _t, n, leaf in shipped_defs.parse(mod_dir))

    def ext(game, tool, p):
        if tool != "jawa/get_defs":
            return None
        want = [s.split("/", 1)[1] for s in str(p.get("defs") or "").split(";") if "/" in s]
        fields = [f for f in str(p.get("fields") or "").split(",") if f]
        rows, missing = [], []
        for n in want:
            if n not in parsed or ("missing" in brk and n == "T_Two"):
                missing.append(n)
                continue
            vals = dict((f, parsed[n].get(f)) for f in fields if f in parsed[n])
            if "drift" in brk and n == "R_Make" and "workAmount" in vals:
                vals["workAmount"] = "1"
            if "label_shadow" in brk and n == "T_One":
                vals["label"] = "someone else's one"
            if "allowMixingIngredients" in vals:
                vals["allowMixingIngredients"] = "True"        # live bools print capitalised
            if "workAmount" in vals:
                vals["workAmount"] = "800.0" if "drift" not in brk else vals["workAmount"]
            rows.append({"defName": n, "fields": vals})
        found = len(rows) + (1 if "count_lies" in brk else 0)
        if "tool_fails" in brk:
            return {"success": False, "message": "InvalidCastException"}
        return {"success": True, "foundCount": found, "notFound": missing, "defs": rows}
    return ext


def run(brk=(), fields_by_type=None, sanity=("T_One",), min_count=3, skip=()):
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "Defs", "Misc"))
        with open(os.path.join(tmp, "Defs", "Misc", "a.xml"), "w") as fh:
            fh.write(XML)
        val = os.path.join(tmp, "validation.py")
        suite = Suite("Synthetic")
        shipped_defs.add_chain(suite, val, fields_by_type=fields_by_type, sanity=sanity, min_count=min_count,
                               skip=skip)
        game = MockGame()
        game.ext = make_ext(set(brk), tmp)
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out[c["name"]] = (c["verdict"], c.get("detail") or "")
    return out


def reds(r):
    return sorted(k for k, (v, _d) in r.items() if v == "FAIL")


LOADED, FIELDS = "every_shipped_def_is_loaded", "shipped_scalar_fields_match_xml"


def main():
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "Defs"))
        with open(os.path.join(tmp, "Defs", "a.xml"), "w") as fh:
            fh.write(XML)
        got = shipped_defs.parse(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("parse skips the abstract def and keeps three", [n for _t, n, _l in got] == ["T_One", "T_Two", "R_Make"], got)
    check("parse keeps leaves only (no statBases block)", "statBases" not in got[0][2], got[0][2])
    check("same_value: 800 == 800.0, true == True, 'a' != 'b'",
          shipped_defs.same_value("800", "800.0") and shipped_defs.same_value("true", "True")
          and not shipped_defs.same_value("a", "b") and not shipped_defs.same_value("1", None))

    rec = {"RecipeDef": ("label", "workAmount", "allowMixingIngredients")}
    clean = run(fields_by_type=rec)
    check("clean run: both components PASS", all(v == "PASS" for v, _d in clean.values()) and len(clean) == 2, clean)
    cases = [
        (("missing",), {}, [LOADED]),
        (("drift",), {}, [FIELDS]),
        (("label_shadow",), {}, [FIELDS]),
        (("count_lies",), {}, [LOADED]),
        (("tool_fails",), {}, [LOADED]),
    ]
    for brk, _kw, want in cases:
        res = run(brk, fields_by_type=rec)
        got = reds(res)
        check("break %-13s reddens exactly %s" % (brk[0], want), got == sorted(want), "got %s" % got)
        check("break %-13s leaves no component PASSing on a lying tool" % brk[0],
              brk[0] not in ("count_lies", "tool_fails") or all(v != "PASS" for v, _d in res.values()), res)
    blind = reds(run(sanity=("NotThere",), fields_by_type=rec))
    check("a sanity name the parse cannot see reddens the loaded component", blind == [LOADED], blind)
    small = reds(run(min_count=10, fields_by_type=rec))
    check("fewer defs than min_count reddens the loaded component", small == [LOADED], small)
    nothing = reds(run(fields_by_type={"ThingDef": ("nonexistentField",), "RecipeDef": ("nonexistentField",)}))
    check("a readback that compares nothing is red, not vacuously green", nothing == [FIELDS], nothing)
    skipped = reds(run(("drift",), fields_by_type=rec, skip=("R_Make.workAmount",)))
    check("skip names a deliberately patched field and clears only it", skipped == [], skipped)

    for rel, sanity, min_count in WIRED:
        mod = os.path.join(ROOT, "src", rel)
        names = [n for _t, n, _l in shipped_defs.parse(mod)]
        check("wired %s: parse finds %d >= %d defs and its sanity names" % (rel, len(names), min_count),
              len(names) >= min_count and all(s in names for s in sanity), (len(names), [s for s in sanity if s not in names]))

    if FAILS:
        print("\n%d shipped_defs selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall shipped_defs selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
