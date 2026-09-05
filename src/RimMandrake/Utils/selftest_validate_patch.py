#!/usr/bin/env python3
"""Selftest for validate_patch.py's xpath engine.

`VALIDATE_PATCH_NEEDS_SELFTEST_1` — *"validate_patch.py has no selftest, and the
same bug class has now shipped twice."*

🔴 THE BUG CLASS, AND IT REALLY DID SHIP TWICE.
RimWorld evaluates a patch xpath against the XmlDocument, whose CHILD is `<Defs>`,
so `Defs/ThingDef[...]` and `/Defs/ThingDef[...]` mean the same thing there.
lxml and ElementTree evaluate against the `<Defs>` ROOT ELEMENT, where a leading
`Defs` step means `Defs/Defs/...` and matches NOTHING.

  * 2026-08-21 — found in the **ElementPath** branch. 42 xpaths across this repo's
    own patches had been reporting a false 0.
  * 2026-08-22 — found again in the **lxml** branch, which had never been given
    the same treatment. Every xpath using `text()`, `contains()`, `starts-with()`,
    `not()`, an axis or a union takes that branch, and **25 of the 28 operations
    in `BodySizeIsReal.xml` read as dead** when they were all live.
  * 2026-09-05 (`VALIDATE_PATCH_XPATH_FALSENEG_1`) — a THIRD time, in
    `to_elementtree_xpath()`'s own translation: a predicate naming a NESTED
    path (`[genes/li="X"]`, or even the bare existence form `[genes/li]`) was
    neither substituted nor rejected, so it reached `root.findall()` unchanged
    and raised `SyntaxError: invalid predicate` — silently swallowed by
    `xpath_hits()`'s blanket `except Exception: continue` and reported as 0
    matches. `EggLayersLayEggs.xml`'s `genes/li="Outland_EggLayer"` guard read
    as dead when lxml's full XPath correctly matched all 19 real targets.

⚠️ **A false 0 is the worst possible output of this tool**, because it is
indistinguishable from a genuinely dead xpath — which is the one thing the
validator exists to tell apart. Both fixes were correct and neither was tested,
so the second was free to happen.

WHAT THIS TESTS, AND WHAT IT DELIBERATELY DOES NOT
--------------------------------------------------
It tests `count_matches()` directly, handing it documents built in memory. That
is the seam where the bug lived, and testing there needs no mod folders, no
`ModsConfig.xml` and no 8,700-file load set — so this runs in under a second and
can be run before every commit.

⛔ It does NOT test the load-set discovery, the def-file walker or the report
formatting. Those need a real install; this needs to stay cheap enough to run.

    python3 selftest_validate_patch.py
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root. Three levels, not two: getting this
# wrong made the import fail rather than silently test the wrong file, which is
# the good failure mode, but only because the guard below names the path.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
_SCRIPTS = os.path.join(REPO, "skills", "rimworld-modding", "scripts")
if not os.path.isfile(os.path.join(_SCRIPTS, "validate_patch.py")):
    sys.exit("validate_patch.py is not at %s — the skill layout moved" % _SCRIPTS)
sys.path.insert(0, _SCRIPTS)

import validate_patch as V                                        # noqa: E402

PASS: list = []
FAIL: list = []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as ex:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, ex))
    except Exception as ex:                                        # noqa: BLE001
        FAIL.append(name)
        print("ERROR %s\n        %s: %s" % (name, type(ex).__name__, ex))


# --------------------------------------------------------------------------
# One tiny Defs document, shaped like the real thing: a <Defs> root holding two
# XenotypeDefs, one of which carries the gene the collision-prone xpaths look for.
# --------------------------------------------------------------------------
SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <XenotypeDef>
    <defName>RSW_RimMandrakeWookiee</defName>
    <label>Wookiee</label>
    <genes>
      <li>RSW_BodySizeGene_big</li>
      <li>RSW_lifespan_quad</li>
    </genes>
  </XenotypeDef>
  <XenotypeDef>
    <defName>RSW_RimMandrakeJawa</defName>
    <label>Jawa</label>
    <genes>
      <li>RSW_BodySizeGene_smaller</li>
    </genes>
  </XenotypeDef>
  <ThingDef>
    <defName>Gun_Autopistol</defName>
    <weaponTags><li>SimpleGun</li></weaponTags>
  </ThingDef>
</Defs>
"""


def docs():
    """The (path, root, mod) triples count_matches() consumes."""
    root = V.parse_def_doc_from_string(SAMPLE) if hasattr(V, "parse_def_doc_from_string") \
        else _parse(SAMPLE)
    return [("Xenotypes.xml", root, "Test Mod")]


def _parse(text):
    if getattr(V, "HAVE_LXML", False):
        from lxml import etree as LET
        return LET.fromstring(text.encode("utf-8"))
    import xml.etree.ElementTree as ET
    return ET.fromstring(text)


def n(xp):
    """-> hit count, asserting the expression was not refused as unsupported."""
    total, _where, _elems, _mods, unsupported = V.count_matches(xp, docs())
    assert not unsupported, (
        "count_matches refused %r as unsupported — it must either evaluate an "
        "expression or say so, and a refusal here means the test proves nothing" % xp)
    return total


# --------------------------------------------------------------------------
# 🔴 The regression itself: both spellings of the root step, in BOTH engines.
# --------------------------------------------------------------------------
def t_a_bare_Defs_step_matches_the_same_as_a_rooted_one():
    """`Defs/…` with no leading slash is as common in the wild as `/Defs/…`.

    This is the 2026-08-21 half of the bug: the ElementPath branch used to treat
    the bare form as `Defs/Defs/…`.
    """
    bare = n('Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee"]/genes')
    rooted = n('/Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee"]/genes')
    assert bare == rooted == 1, ("bare=%s rooted=%s; both must be 1" % (bare, rooted))


def t_a_text_predicate_matches_through_the_lxml_branch():
    """🔴 THE 2026-08-22 HALF, and the one that cost 25 of 28 operations.

    `text()` is on UNSUPPORTED_TOKENS, so this expression can only go through
    lxml — the branch that never stripped the leading `Defs` step.
    """
    if not getattr(V, "HAVE_LXML", False):
        return                       # no lxml: the branch under test cannot run
    bare = n('Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee"]/genes'
             '/li[text()="RSW_BodySizeGene_big"]')
    rooted = n('/Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee"]/genes'
               '/li[text()="RSW_BodySizeGene_big"]')
    assert bare == rooted == 1, (
        "a text() xpath must match the same whether or not the root step carries a "
        "leading slash. bare=%s rooted=%s. This is the exact shape that reported "
        "BodySizeIsReal.xml as 25/28 dead." % (bare, rooted))


def t_every_full_xpath_feature_takes_the_lxml_branch_and_still_matches():
    """The other expressions that force the lxml branch must be rebased too.

    ⚠️ Fixing only `text()` would have left `contains()`, `not()`, axes and unions
    reporting the same false 0 — the bug is the BRANCH, not the function.
    """
    if not getattr(V, "HAVE_LXML", False):
        return
    for xp in (
        'Defs/XenotypeDef[contains(defName, "Wookiee")]',
        'Defs/XenotypeDef[starts-with(defName, "RSW_RimMandrakeW")]',
        'Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee" or defName="NoSuchDef"]',
        'Defs/XenotypeDef[not(defName="RSW_RimMandrakeJawa")]',
    ):
        assert n(xp) == 1, "%r matched 0 — the lxml branch is not rebasing" % xp


def t_a_genuinely_dead_xpath_still_reports_zero():
    """🔑 The fix must not turn every miss into a hit.

    A validator that says everything matches is as useless as one that says
    nothing does, and it is the failure a careless rebase would cause.
    """
    assert n('Defs/XenotypeDef[defName="NoSuchXenotypeAnywhere"]/genes') == 0
    if getattr(V, "HAVE_LXML", False):
        assert n('Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee"]/genes'
                 '/li[text()="RimMandrake_BodySizeGene_NOPE"]') == 0


def t_a_double_slash_search_is_not_broken_by_the_rebase():
    """`//X` means "anywhere", and the rebase must leave it meaning that."""
    # Four: two genes on the Wookiee, one on the Jawa, one weaponTag.
    got = n('//li')
    assert got == 4, "//li should find all four <li>; got %s" % got


def t_the_two_engines_agree_on_the_expressions_both_can_evaluate():
    """🔑 The strongest available check, because it needs no expected number.

    An expression without a full-XPath token goes through ElementPath; the same
    expression forced through lxml must agree. They disagreed for a year on the
    leading step and nobody noticed, because nothing ever compared them.
    """
    if not getattr(V, "HAVE_LXML", False):
        return
    from lxml import etree as LET
    root = docs()[0][1]
    for xp in ('Defs/XenotypeDef[defName="RSW_RimMandrakeWookiee"]/genes',
               'Defs/XenotypeDef/genes/li',
               'Defs/ThingDef[defName="Gun_Autopistol"]/weaponTags'):
        et_path = V.to_elementtree_xpath(xp)
        assert et_path is not None, "%r should be ElementPath-translatable" % xp
        et_n = len(root.findall(et_path))
        lx_n = len(LET.XPath(V.rebase_for_root_element(xp))(root))
        assert et_n == lx_n, (
            "the two engines disagree on %r: ElementPath %d, lxml %d" % (xp, et_n, lx_n))


def t_rebase_leaves_a_non_Defs_absolute_path_alone():
    """Only the `Defs` root step is the document/element mismatch.

    ⛔ Stripping any leading step would silently change what an unusual xpath
    selects, which is a worse bug than the one being fixed.
    """
    for xp in ("/Something/Else", "//XenotypeDef", "XenotypeDef/genes"):
        assert V.rebase_for_root_element(xp).endswith(xp.lstrip("/")) or \
            V.rebase_for_root_element(xp) == "." + xp, \
            "rebase mangled %r into %r" % (xp, V.rebase_for_root_element(xp))


def t_a_nested_path_predicate_routes_to_lxml_not_a_false_zero():
    """🔴 THE 2026-09-05 HALF (VALIDATE_PATCH_XPATH_FALSENEG_1).

    `[genes/li="X"]` names a path, not a bare word, before the `=` - ElementPath
    cannot parse that AT ALL (confirmed against real Python ElementTree: it
    raises `SyntaxError: invalid predicate` for both quote styles, and even for
    the bare existence form with no comparison). `to_elementtree_xpath()` must
    refuse to translate it so `count_matches()` falls through to lxml's full
    XPath instead of handing ElementPath something that blows up and gets
    read as a silent 0.
    """
    assert V.to_elementtree_xpath('Defs/XenotypeDef[genes/li="RSW_BodySizeGene_big"]') is None, (
        "a nested-path predicate with a double-quoted comparison must not be "
        "translated to ElementPath")
    assert V.to_elementtree_xpath("Defs/XenotypeDef[genes/li='RSW_BodySizeGene_big']") is None, (
        "single-quoted makes no difference - ElementPath cannot parse a nested "
        "path predicate at all")
    assert V.to_elementtree_xpath('Defs/XenotypeDef[genes/li]') is None, (
        "the bare existence form (no comparison) must also be refused")
    if getattr(V, "HAVE_LXML", False):
        got = n('Defs/XenotypeDef[genes/li="RSW_BodySizeGene_big"]')
        assert got == 1, (
            "the nested-path predicate must reach lxml and match the real "
            "Wookiee xenotype; got %s (0 means the false-zero regressed)" % got)


def t_the_unsupported_token_list_still_routes_text_to_lxml():
    """A guard on the routing itself.

    If `text()` were ever dropped from UNSUPPORTED_TOKENS, ElementPath would be
    handed an expression it cannot evaluate and would answer 0 — the same false
    zero, arriving by a different road.
    """
    assert "text()" in V.UNSUPPORTED_TOKENS
    assert V.to_elementtree_xpath('Defs/X/li[text()="a"]') is None, (
        "an expression using text() must NOT be translated to ElementPath")


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
