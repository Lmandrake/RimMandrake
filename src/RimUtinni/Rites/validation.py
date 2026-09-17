"""validation.py -- modcheck suite for RimUtinni: The Rites
(mandrake.rut.rites).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Rites

(environment: minimal + mandrake.rut.antiquities, per this mod's own hard
`<modDependencies>`/`<loadAfter>` -- Rites cannot even load without it).

Grounded in the mod's actual source, read whole before writing this: this
mod is PURE DATA -- one XML file (`Defs/RUT_Rites_Research.xml`), no
Assemblies, no Source/, no ModSettings (`suite.toggles = []`, per the floor
rule: "zero toggles is not a floor violation"). The whole mechanism is
vanilla `ResearchProjectDef.hiddenPrerequisites` gating `CanStartNow` while
the tree's own visibility filter ignores it -- per this file's OWN header
comment (RITES_REVEAL_MECHANISM_1, owner ruling 2026-09-04): "vanilla
hiddenPrerequisites gates CanStartNow only ... verified against
MainTabWindow_Research.cs source before asking." Read `RUT_Rites_
Research.xml` (all five `ResearchProjectDef`s, exact baseCost/techLevel/
prerequisites/hiddenPrerequisites per tier) and, since the hidden
prerequisites point at Antiquities defs, `Antiquities/Defs/
ResearchProjectDefs/RUT_Antiquities_Research.xml` far enough to confirm
`RUT_Antiq_Language` (T0 of that tree) has NO prerequisites of its own --
load-bearing for this suite's setup, since it means `RUT_Antiq_Language` can
be finished directly with no prerequisite chain to walk first.

THE WALK DOC IS WRONG about what `jawa/research_availability` actually
reports -- found by reading `JawaBenchResearchTimeTools.cs`'s
`ResearchAvailability`, not assumed. Walk step 6 expects: "unfinished list
names RUT_Antiq_Language". But the tool's `unfinishedPrerequisites` field is
built by walking `proj.prerequisites` ONLY (`JawaBenchResearchTimeTools.cs`,
the `foreach (var p in proj.prerequisites) if (!p.IsFinished)
unfinishedPrereqs.Add(...)` loop) -- `RUT_Antiq_Language` is a
`hiddenPrerequisites` entry on `RUT_Rites_ConduitChoir`, not an ordinary
`prerequisites` one (ConduitChoir's ordinary `prerequisites` is
`[RUT_Rites_ScrapShrine]` alone), and the tool has NO field at all for
hidden prerequisites -- neither a name list nor a completion flag. So
`unfinishedPrerequisites` is empty the entire time this suite runs,
regardless of whether `RUT_Antiq_Language` is finished; only `canStartNow`
itself (which DOES fold `hiddenPrerequisites` in, per vanilla
`ResearchProjectDef.CanStartNow` -- confirmed by this mod's own header
comment, not re-derived here) moves. `conduit_choir_gated_by_hidden_
prerequisite` below asserts what the tool actually returns, and calls this
out explicitly rather than silently reproducing the walk's claim.

WHAT THIS SUITE CANNOT PROVE, and why:
  - Walk step X (human pass: "confirm a locked-but-visible rite renders
    greyed in the research tree UI rather than vanishing") is a UI-render
    check with no state read-back -- `jawa/research_availability` proves
    the STATE (`canStartNow` false while the project still resolves and
    reports normally, i.e. it has not become `isHidden`), but nothing on
    the bridge can screenshot the research tree's own tab UI meaningfully,
    and there is no map/pawn/thing state to photograph either -- this whole
    mod is a research tree, not a placed object. No component below takes
    a screenshot for the same reason `IshkoDarkLandmarks/validation.py`
    (also a pure-data, no-visible-state mod) does not.
  - `[D]` def read-back items (walk steps 2-5: baseCost/techLevel/tab/
    prerequisites/hiddenPrerequisites exact values) are covered by the
    offline def dump / RimSage, not this bridge-driven runtime suite --
    matching every other suite in this family (no validation.py here reads
    a def's raw XML fields via the bridge; see e.g. `FlowWorks/
    validation.py`'s own `[D]` steps, likewise unassigned to a bridge call).
  - `RUT_Rites_GodsSpeakBack` (T4, hiddenPrereq `RUT_Antiq_Voice`) is not
    independently exercised -- `jawa/research_finish_project` recursively
    finishes ORDINARY prerequisites only (its own tool doc: "recursively
    finishes any unfinished prerequisites first"), never hidden ones, so
    proving T4's gate the same way would need finishing the entire T0-T3
    Antiquities AND Rites chains first. The T1/ConduitChoir case already
    isolates the identical mechanism (one hidden prereq, gating one tier)
    with far less setup; T2-T4 are assumed to work the same way rather than
    independently proven.

Still not proven / likely first-live-run corrections:
  1. Whether `Find.ResearchManager.FinishProject` on `RUT_Antiq_Language`
     actually succeeds despite its `requiredResearchBuilding` pointing at a
     deliberately unbuildable bench (`RUT_AntiquityCipherBench`, per that
     mod's own header comment) -- reasoned from `FinishProject`'s own
     description ("no research points are spent, no researcher does the
     work") not observed live; if it silently fails for an unanticipated
     reason, `research_finish_project`'s own `success`/`wasAlreadyFinished`
     read-back below is what would catch it.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Rites")
suite.toggles = []   # pure data, no ModSettings at all -- About.xml, checked whole.


@suite.chain("conduit_choir_gated_by_hidden_prerequisite")
def conduit_choir_gated_by_hidden_prerequisite(t):
    """No test area needed -- this chain is entirely research-tree state, no
    map things. Finishes ONLY the ordinary prerequisite (ScrapShrine) first,
    so the remaining block is isolated to the hidden one (Antiq_Language) --
    proving the 'revealed, not bought' mechanism this mod's whole About.xml
    description is about."""

    with t.component("conduit_choir_blocked_until_language_finished", beyond_toggle=True):
        r = t.bridge_call("jawa/research_finish_project", project="RUT_Rites_ScrapShrine")
        if t._guard() and not (r or {}).get("success"):
            raise ExpectationFailed("could not finish RUT_Rites_ScrapShrine: %r" % r)

        avail = t.bridge_call("jawa/research_availability", project="RUT_Rites_ConduitChoir")
        if t._guard():
            if not (avail or {}).get("success"):
                raise ExpectationFailed(
                    "jawa/research_availability(RUT_Rites_ConduitChoir) failed: %r" % avail)
            if not avail.get("prerequisitesCompleted"):
                raise ExpectationFailed(
                    "prerequisitesCompleted should be True once ScrapShrine is finished "
                    "(ConduitChoir's only ORDINARY prerequisite): %r" % avail)
            if avail.get("canStartNow"):
                raise ExpectationFailed(
                    "canStartNow is True before RUT_Antiq_Language (ConduitChoir's "
                    "hiddenPrerequisites entry) has been finished -- the hidden-gate "
                    "mechanism this mod exists for is not blocking: %r" % avail)
            # See module docstring: the tool's unfinishedPrerequisites walks ORDINARY
            # prerequisites only and has no hiddenPrerequisites field at all, so this
            # is empty here -- NOT naming RUT_Antiq_Language, contrary to the walk
            # doc's step 6. Asserted explicitly so a future tool change that adds
            # hidden-prereq reporting is the trigger to revisit this.
            if avail.get("unfinishedPrerequisites"):
                raise ExpectationFailed(
                    "unfinishedPrerequisites was expected empty (ScrapShrine is "
                    "ConduitChoir's only ordinary prerequisite and is finished; "
                    "RUT_Antiq_Language is a HIDDEN prerequisite this field cannot "
                    "see) but got %r" % avail.get("unfinishedPrerequisites"))

    with t.component("conduit_choir_unblocked_after_language_finished", beyond_toggle=True):
        r = t.bridge_call("jawa/research_finish_project", project="RUT_Antiq_Language")
        if t._guard() and not (r or {}).get("success"):
            raise ExpectationFailed("could not finish RUT_Antiq_Language: %r" % r)

        avail = t.bridge_call("jawa/research_availability", project="RUT_Rites_ConduitChoir")
        if t._guard():
            if not (avail or {}).get("success"):
                raise ExpectationFailed(
                    "jawa/research_availability(RUT_Rites_ConduitChoir) failed: %r" % avail)
            if not avail.get("canStartNow"):
                raise ExpectationFailed(
                    "canStartNow is still False after RUT_Antiq_Language finished -- "
                    "the hidden prerequisite should no longer block: %r" % avail)
            if not avail.get("prerequisitesCompleted"):
                raise ExpectationFailed(
                    "prerequisitesCompleted flipped to False unexpectedly: %r" % avail)
