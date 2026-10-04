"""validation.py -- modcheck suite for RimUtinni ResearchRetag (mandrake.rut.researchretag).

Pure-XML patch mod: no C#, no Assemblies, no ModSettings class anywhere in
`src/RimUtinni/ResearchRetag/` (confirmed by directory listing -- only
About.xml, one Defs file, and three Patches files). Per the briefing's own
rule for this shape: `suite.toggles = []`, every component is
`beyond_toggle=True`.

THE REAL TEST-ENVIRONMENT PROBLEM, read from the mod itself, not assumed:
`RUT_ResearchRetag.xml` retags 269 `ResearchProjectDef`s and
`RUT_ResearchTabAssign.xml` retabs another set, but the overwhelming
majority of those defNames belong to OTHER, optional mods named in
`About.xml`'s 52-entry `forceLoadAfter` list (`ABF_ResearchProject_*`,
`AM_*`, `CGT_*`, `BMT_*`, ...) -- and every operation here is a
`PatchOperationConditional` specifically because most targets will be
ABSENT in many mod configurations (CLAUDE.md: "A patch that matches
nothing logs nothing" / "PatchOperationConditional ... return[s] true on
no match"). Against modcheck's own environment rule ("minimal mechanism
list + the mod under test", no dependency mods pulled in for a pure patch
mod with no declared `modDependencies`), essentially every one of those
269+ rows would silently no-op, and a validator built on any of them would
be un-provably green -- exactly the "zero rows is a failure, not a
footnote" trap (project memory) if left unguarded.

**The fix, not a workaround**: `infrastructure/output/research_manifest_draft.csv`
(the frozen source these patches were generated from) names each row's
`source_mod`. Five of the 269 retagged rows -- `AirConditioning`,
`Autodoors`, `CarpetMaking`, `ColoredLights`, `Cryptosleep` -- are
`source_mod=Core`: real vanilla `ResearchProjectDef`s that exist in EVERY
mod configuration, minimal or full, with or without any of the 52
`forceLoadAfter` mods installed. These five are the validator's targets,
confirmed present in both `RUT_ResearchRetag.xml` (techLevel/baseCost/
prerequisites) and `RUT_ResearchTabAssign.xml` (tab) by direct grep before
writing this file -- not guessed from the manifest alone.

Expected values below are copied verbatim from the patch XML itself
(`RUT_ResearchRetag.xml` lines ~393-933, `RUT_ResearchTabAssign.xml` lines
~51-5827), not from the manifest CSV, so a future regenerate-from-manifest
drift would be caught here even if the manifest and the generator disagree.

Still not proven / likely first-live-run corrections:
  1. The other ~264 retagged rows and the Supplement file's 13 rows
     (`RUT_ResearchRetag_Supplement.xml`) are NOT independently
     live-checked -- their operations are structurally identical
     `PatchOperationConditional`/`Replace`/`Add` triples to the five
     proven here, so the MECHANISM is the same, but their specific
     target defNames' presence depends on which of the 52 optional mods
     are actually in whatever list the runner uses. A full-modlist
     modcheck pass (not the minimal list) would be needed to check them
     for real; that is out of this validator's floor.
  2. `RESEARCH_RETAG_LOAD_ORDER_GAP_1`'s `forceLoadAfter` ordering itself
     (does RimSort/the game actually load this mod after all 52 named
     packageIds) has no bridge read-back at all -- `jawa/list_factions`-
     style load-order introspection was not found in a tool search: this
     validator cannot see load order, only resolved end-state def values,
     which is silent to an ordering bug that a LATER mod's own patch
     happens to still leave in the state this mod wants.
  3. `RETAG_BUILDER_SELF_ERASE_1` (the generator bug documented in the
     Supplement's own header) is a generator-code defect, not a def-state
     defect -- nothing observable at runtime distinguishes a row the
     generator would currently erase from one it would not. Out of scope
     for a live def check by construction.
"""
from modcheck import Suite, ExpectationFailed
from modcheck.suite import Precondition

suite = Suite("ResearchRetag")
suite.toggles = []

TAB_DEFS = {
    "RUT_Tree_Scavenging": "jawa scavenging",
    "RUT_Tree_Refinery": "the refinery",
    "RUT_Tree_Workshop": "the workshop",
    "RUT_Tree_Hearth": "the hearth",
    "RUT_Tree_PowderAndSlug": "powder & slug",
    "RUT_Tree_Utinni": "the utinni",
    "RUT_Tree_Shell": "the shell",
    "RUT_Tree_Unbolting": "the unbolting",
    "RUT_Tree_Blasterworks": "blasterworks",
    "RUT_Tree_WakingMind": "the waking mind",
    "RUT_Tree_Reach": "the reach",
    "RUT_Tree_AscendantLadder": "the ascendant ladder",
    "RUT_Tree_StrangeSchools": "the strange schools",
    "RUT_Tree_JunkerYards": "the junker yards",
    "RUT_Tree_FoundryHive": "the foundry hive",
}

# defName -> (expected field values), verbatim from RUT_ResearchRetag.xml +
# RUT_ResearchTabAssign.xml, restricted to source_mod=Core rows (research_
# manifest_draft.csv) so every target is guaranteed loaded regardless of
# which optional mods the runner's environment carries.
CORE_RETAG_ROWS = {
    "AirConditioning": {"baseCost": "700", "tab": "RUT_Tree_Scavenging"},
    "Autodoors": {"baseCost": "1700", "tab": "RUT_Tree_Scavenging"},
    "CarpetMaking": {"techLevel": "Industrial", "tab": "RUT_Tree_Hearth"},
    "ColoredLights": {"baseCost": "700", "tab": "RUT_Tree_Hearth"},
    "Cryptosleep": {"techLevel": "Industrial", "tab": "RUT_Tree_Reach",
                    "prerequisites": "VitalsMonitor"},
}


def _live(t):
    """See the equivalent helper in Pyrelands/validation.py -- same
    reasoning: distinguishes a real chain run from `Suite.
    components_declared()`'s offline no-op probe (`t.session is None`)."""
    return t.session is not None and not t.upstream_failed


@suite.chain("own_tab_defs")
def own_tab_defs(t):
    """This mod's OWN 15 `ResearchTabDef`s (`Defs/ResearchTabDefs/
    RUT_Tree_Defs.xml`) -- always loaded whenever ResearchRetag is in the
    mod list at all, independent of every other mod. The one part of this
    mod's content that is not a patch onto someone else's def."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("research_tabs_resolve", beyond_toggle=True):
        pairs = ";".join("ResearchTabDef/%s" % name for name in TAB_DEFS)
        r = t.bridge_call("jawa/get_defs", defs=pairs, fields="label,generalTitle")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                bad.append("not found: %r" % not_found)
            for name, expect_label in TAB_DEFS.items():
                row = rows.get(name)
                if row is None:
                    continue  # already covered by not_found above
                got_label = (row.get("fields") or {}).get("label")
                if got_label != expect_label:
                    bad.append("%s: expected label=%r, got %r" % (name, expect_label, got_label))
            if bad:
                raise ExpectationFailed(
                    "RUT_Tree_* ResearchTabDefs did not resolve as shipped: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("core_rows_retagged")
def core_rows_retagged(t):
    """Five vanilla-Core `ResearchProjectDef`s the retag actually touches
    (see module docstring for why these five, specifically, are the only
    safe live targets in an environment with none of the 52 optional
    donor mods installed). One `jawa/get_defs` call proves BOTH patch
    files at once: techLevel/baseCost/prerequisites from
    `RUT_ResearchRetag.xml`, `tab` from the separate, hand-authored
    `RUT_ResearchTabAssign.xml`."""
    t.clear_area(size=8)

    with t.component("core_rows_match_manifest", beyond_toggle=True):
        pairs = ";".join("ResearchProjectDef/%s" % name for name in CORE_RETAG_ROWS)
        r = t.bridge_call("jawa/get_defs", defs=pairs,
                          fields="baseCost,techLevel,tab,prerequisites")
        if _live(t):
            rows = {row.get("defName"): row for row in (r or {}).get("defs") or []}
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                # These are vanilla Core rows -- absence here means Core
                # itself failed to load, or the patch xpath is broken, not
                # a "some optional mod is missing" case. A real failure,
                # not a footnote.
                bad.append("vanilla Core rows not found at all: %r" % not_found)
            for name, expect in CORE_RETAG_ROWS.items():
                row = rows.get(name)
                if row is None:
                    continue
                fields = row.get("fields") or {}
                for field, expect_value in expect.items():
                    got = fields.get(field)
                    if field == "prerequisites":
                        got_list = got if isinstance(got, list) else ([got] if got else [])
                        if expect_value not in got_list:
                            bad.append("%s.prerequisites: expected %r in %r"
                                       % (name, expect_value, got_list))
                    else:
                        # str(got) != str(expect_value) alone false-fails a
                        # numeric field: the bridge returns baseCost as a
                        # JSON float (700.0), CORE_RETAG_ROWS' expected
                        # values are plain XML-verbatim strings ("700"), and
                        # str(700.0) == "700.0" != "700" -- measured live
                        # 2026-09-13 as a FAIL on every one of the five rows
                        # despite every value actually matching. Compare
                        # numerically when both sides parse as a number;
                        # string-compare (techLevel/tab, already correct)
                        # otherwise.
                        match = str(got) == str(expect_value)
                        if not match:
                            try:
                                match = float(got) == float(expect_value)
                            except (TypeError, ValueError):
                                match = False
                        if not match:
                            bad.append("%s.%s: expected %r, got %r"
                                       % (name, field, expect_value, got))
            if bad:
                raise ExpectationFailed(
                    "Core research rows do not match the retag/tab-assign patches: %s"
                    % "; ".join(bad))
        t.screenshot()


def own_prereq_graph(mod_dir=None):
    """{defName: [prerequisites + hiddenPrerequisites]} for this mod's OWN ResearchProjectDefs (XML parse)."""
    import os as _os
    import xml.etree.ElementTree as _ET
    root_dir = _os.path.join(mod_dir or _os.path.dirname(_os.path.abspath(__file__)), "Defs")
    graph = {}
    for root, _dirs, files in sorted(_os.walk(root_dir)):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for d in _ET.parse(_os.path.join(root, fn)).getroot().findall("ResearchProjectDef"):
                    if d.get("Abstract", "").lower() != "true" and d.findtext("defName"):
                        graph[d.findtext("defName").strip()] = [li.text.strip() for tag in ("prerequisites", "hiddenPrerequisites")
                                                                for li in d.findall(tag + "/li") if li.text]
    return graph


def prereq_findings(graph, known):
    """(cycles, dangling): a cycle in this mod's own prerequisite graph locks every project on it forever; a
    prerequisite naming no ResearchProjectDef in the load (`known`, plus our own) is a dead cross-reference."""
    dangling = sorted("%s -> %s" % (n, p) for n, ps in graph.items() for p in ps if p not in graph and p not in known)
    cycles, state = [], {}

    def walk(n, path):
        state[n] = 1
        for p in graph.get(n, ()):
            if p in graph:
                if state.get(p) == 1:
                    cycles.append(" -> ".join(path[path.index(p):] + [p]) if p in path else "%s -> %s" % (n, p))
                elif not state.get(p):
                    walk(p, path + [p])
        state[n] = 2
    for n in sorted(graph):
        if not state.get(n):
            walk(n, [n])
    return cycles, dangling


@suite.chain("own_prereq_graph_static")
def own_prereq_graph_static(t):
    """This mod's 18 ported ResearchProjectDefs: no prerequisite cycle among them, and every prerequisite names a
    ResearchProjectDef the current load holds (the offline def dump of the live mod set). Pure static: same
    verdict offline and live."""
    with t.component("own_prereqs_acyclic_and_resolve", beyond_toggle=True):
        graph = own_prereq_graph()
        if len(graph) < 15 or "RR_LateralThinking" not in graph or not any(graph.values()):
            raise ExpectationFailed("the own-research parse is blind: %d defs" % len(graph))
        try:
            import game_paths as _GP
            from def_diff import iter_live_defs
            import os as _os
            known = set(d.get("defName") for d in iter_live_defs(_os.path.join(_GP.DEF_DUMP, "defs", "ResearchProjectDef.json")))
        except Exception as e:      # no dump on this machine: say so, never pass
            raise Precondition("no readable def dump for ResearchProjectDef: %s" % e)
        if len(known) < 200 or "Electricity" not in known:
            raise Precondition("the def dump's ResearchProjectDef list is blind: %d names" % len(known))
        cycles, dangling = prereq_findings(graph, known)
        if cycles or dangling:
            raise ExpectationFailed("prerequisite cycles %s; prerequisites naming no loaded project %s" % (cycles, dangling))

def patched_view_coords(patch_xml=None):
    """{defName: {"researchViewX"|"researchViewY": float}} set by this mod's Patches (last op wins, file order)."""
    import os as _os
    import xml.etree.ElementTree as _ET
    import re as _re
    here = _os.path.dirname(_os.path.abspath(__file__))
    out = {}
    paths = [patch_xml] if patch_xml else [_os.path.join(here, "Patches", f) for f in sorted(_os.listdir(_os.path.join(here, "Patches")))
                                          if f.endswith(".xml")]
    for p in paths:
        for op in _ET.parse(p).getroot().iter():
            if op.tag not in ("match", "nomatch", "li", "Operation"):
                continue
            xp = op.findtext("xpath") or ""
            m = _re.search(r'defName="([^"]+)"', xp)
            val = op.find("value")
            if not m or val is None:
                continue
            for fld in ("researchViewX", "researchViewY"):
                e = val.find(fld)
                if e is not None and (e.text or "").strip():
                    out.setdefault(m.group(1), {})[fld] = float(e.text)
    return out


def tab_overlaps(nodes):
    """Pairs inside the engine's relaxation box (ResearchProjectDef.GenerateNonOverlappingCoordinates:
    |dx| < 0.5 and |dy| < 0.25, same tab). Any such pair is relaxed apart at load and can land two nodes on
    identical coordinates -> 'same research view coords and tab' ConfigError. nodes: [(defName, x, y)]."""
    out = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if abs(a[1] - b[1]) < 0.5 and abs(a[2] - b[2]) < 0.25 + 1e-6:
                out.append("%s(%g,%g) ~ %s(%g,%g)" % (a[0], a[1], a[2], b[0], b[1], b[2]))
    return out


def effective_tab_nodes(dump_rows, tab, overrides):
    nodes = []
    for d in dump_rows:
        f = d.get("fields") or {}
        if str(f.get("tab")) != tab:
            continue
        n = d.get("defName")
        x = f.get("researchViewX")
        y = f.get("researchViewY")
        o = overrides.get(n, {})
        nodes.append((n, float(o.get("researchViewX", 1.0 if x is None else x)), float(o.get("researchViewY", 1.0 if y is None else y))))
    return nodes


@suite.chain("hearth_layout_static")
def hearth_layout_static(t):
    """RUT_Tree_Hearth (44 projects from six mods; load 13 logged two coordinate collisions there): no two nodes
    inside the engine's relaxation box, using the def dump's coordinates overridden by this mod's own
    researchViewX/Y patch values. Pure static."""
    with t.component("hearth_no_overlapping_nodes", beyond_toggle=True):
        try:
            import game_paths as _GP
            import json as _json
            import os as _os
            rows = _json.load(open(_os.path.join(_GP.DEF_DUMP, "defs", "ResearchProjectDef.json")))["defs"]
        except Exception as e:
            raise Precondition("no readable def dump for ResearchProjectDef: %s" % e)
        nodes = effective_tab_nodes(rows, "RUT_Tree_Hearth", patched_view_coords())
        if len(nodes) < 20 or "CarpetMaking" not in [n[0] for n in nodes]:
            raise Precondition("the dump's Hearth tab is blind: %d nodes" % len(nodes))
        bad = tab_overlaps(nodes)
        if bad:
            raise ExpectationFailed("%d overlapping Hearth pairs: %s" % (len(bad), bad[:6]))


# Every def this mod ships is loaded and its label is what its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1;
# ResearchProjectDef baseCost/tab are retagged by this mod's own Patches, so only labels are compared). The Defs/ parse is the list, so a def added later is covered with no edit here.
from modcheck import shipped_defs  # noqa: E402
shipped_defs.add_chain(suite, __file__, sanity=('RR_LateralThinking', 'GravForge'), min_count=40)
