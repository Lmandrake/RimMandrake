"""validation.py -- modcheck suite for Salvation Rites
(mandrake.rut.rites).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Rites

(environment: the `rites` tier -- minimal + mandrake.rut.antiquities +
mandrake.rut.ashkarrlandmarkart, per this mod's own hard
`<modDependencies>`/`<loadAfter>`; Odyssey resolves with the DLCs).

Grounded in the mod's actual source, read whole before writing this. The
research-tree chains below read XML Defs only (the research tree in
`Defs/RUT_Rites_Research.xml`, the rituals and precepts beside it, and
Ishko's three landmarks in `Defs/RUT_IshkoLandmarks.xml`). Since
2026-10-22 the mod also carries C# (Source/, the Ninefold engine folded in
from mandrake.rm.ninefold) with a settings screen; its chains and toggles
are the section at the end of this file. The research tree's mechanism is
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
    a screenshot (Ishko's landmarks have no map state to photograph either).
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

ISHKO'S LANDMARKS (Defs/RUT_IshkoLandmarks.xml; moved here 2026-10-22 from the retired
mandrake.rut.ishkolandmarks, defNames unchanged; owner: "It's a concept, not a mod." and "I think
the Nine Gods belong in Salvation Rites."). The three chains below are prefixed `ishko_`; the content,
read off the XML:

    RUT_LightlessSink     category=mountain  commonality=0.08  Hollow Required=True
    RUT_ShadowedOverhang  category=mountain  commonality=0.08  Chasm  Required=True
    RUT_ColdLavaTube      category=mountain  commonality=0.06  Cavern Required=True

each `MayRequire="Ludeon.RimWorld.Odyssey"`, each `iconTexturePath`
`World/Landmarks/Ashkarr/{Hollow,Chasm,Cavern}`, supplied by
mandrake.rut.ashkarrlandmarkart.

Chains (walk: design/validation_walks/RimUtinni/Rites.md, section "Ishko's landmarks"):
  ishko_source     offline reads of our own XML and the art mod's PNGs (no bridge)
  ishko_defs       jawa/get_defs readback of the RESOLVED defs (deep=true: a
                   List<MutatorChance> without deep comes back as bare type names,
                   so the old substring check could never have passed live)
  ishko_placement  the BEHAVIOUR: jawa/world_landmarks_set add (forced) on a plain
                   land tile -> the tile carries our landmark AND its Required anchor
                   mutator. Engine fact (WorldLandmarks.AddLandmark, decompiled 1.6):
                   a mutatorChance is added when `Rand.Chance(chance) && ((required &&
                   forced) || mutator.IsValidTile(..))`; a Required entry has chance 1,
                   so with forced=true the anchor is certain. Candidate tiles carry none
                   of the three anchors beforehand (else the bar is vacuous). Restored
                   afterwards by _restore(): landmark removed, every mutator the add
                   introduced (anchor AND optional rolls) removed, any it displaced
                   re-added, then read back -- an unverified restore FAILs.

LEARNED, first live run 2026-10-07 (NORTHSTAR_ISHKO_PILOT_1, live_session on the old `ishko` tier, when these
chains were the separate IshkoDarkLandmarks suite; that GREEN is at a retired package and an old hash, so it
proves nothing about this mod until a fresh minimal-list `rites` sitting reads it):
  * SITE/TIER: the tier needs mandrake.rm.gimmesomeslack. Without it JawaBench's companion tools TypeLoad-fail
    (jawa/map_info -> "companion tool was built against a different RimBridgeServer.Sdk API ... Could not load type of
    field JawaBench.BridgeTools.JawaBenchTerrainT..."), so the driver's preflight `game_loaded` FAILs and the run is
    REFUSED with 0 rows (a site verdict, never recorded). modset_builder's `rites` tier carries it.
  * RESULT: 8 PASS / 0 FAIL / 0 UNMEASURED in 3 s, 26 calls, on a fresh quicktest world; the three defs resolve with
    their mutatorChances (deep=true), each forced AddLandmark leaves the tile carrying landmark AND its Required anchor
    mutator, and the placement is undone. The driver itself called status.record_run (GREEN at the mod hash);
    `modcheck record` REFUSES a northstar_driver result ("no rows", "no env.running") -- it only takes validation_v2 style output.
  * The walk has no `## north star` section, so `expected` is [] and a GREEN is the script's own bars only.

RULED OUT (kept here and in the walk's anti-guessing notes):
  * "none of the three is placed on the planet" as a bar. The old chain read
    `row["defName"]` from jawa/world_landmarks_get, whose rows carry `def`, so
    it was vacuous -- it passed whatever the planet held. And on a quicktest
    world it is not even true by design: worldgen places LandmarkDefs by
    commonality, and ours have 0.06-0.08, so a generated world may carry one.
    Placement is the owner's hand on the ASH'KARR save, not a property a test
    world can witness.
"""
import os
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed, shipped_defs

suite = Suite("Rites")
# Ninefold's settings (RM_NinefoldSettings, Source/RM_NinefoldMod.cs): the four its suite covers, unchanged by the fold.
suite.toggles = ["engineEnabled", "firstContactLettersEnabled",
                 "eventMagnitudeMultiplier", "moodWalkMultiplier"]


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


# NORTHSTAR_PARTIAL_GAPS_FILL_1 (audit row: "five defs/tab resolve (script has only the single chain)"): every shipped
# def is loaded live, and each of the five research nodes reads back on the RUT_Rites tab with its XML baseCost and
# techLevel (a node silently landing on the vanilla tab, or re-costed by another mod, reads red).
shipped_defs.add_chain(suite, __file__,
                       fields_by_type={"ResearchProjectDef": ("label", "baseCost", "techLevel", "tab"),
                                       "ResearchTabDef": ("label",)},
                       sanity=("RUT_Rites", "RUT_Rites_GodsSpeakBack", "RUT_LightlessSink"), min_count=35)


# ================================================================== Ishko's landmarks

PACKAGE_ID = "mandrake.rut.rites"     # was mandrake.rut.ishkolandmarks until 2026-10-22
LANDMARKS = [
    ("RUT_LightlessSink", "mountain", 0.08, "Hollow"),
    ("RUT_ShadowedOverhang", "mountain", 0.08, "Chasm"),
    ("RUT_ColdLavaTube", "mountain", 0.06, "Cavern"),
]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFS_XML = os.path.join(HERE, "Defs", "RUT_IshkoLandmarks.xml")
ART_TEX = os.path.join(os.path.dirname(HERE), "AshkarrLandmarkArt", "Textures")
TILE_SCAN = "0-1999"          # world tiles examined for a placement candidate


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    """Stop this component as UNMEASURED (could not ask), never a pass or a fail."""
    t.upstream_failed = True
    t.upstream_reason = "UNMEASURED: " + why
    raise _Unmeasured(why)


class _independent(object):
    """`with _independent(t, name):` -- a component whose FAIL/UNMEASURED does not
    poison the next one (each landmark is its own read or its own tile)."""

    def __init__(self, t, name):
        self.t, self.name = t, name

    def __enter__(self):
        self.before = self.t.upstream_failed
        self.ctx = self.t.component(self.name, beyond_toggle=True)
        return self.ctx.__enter__()

    def __exit__(self, *exc):
        r = self.ctx.__exit__(*exc)
        if not self.before:
            self.t.upstream_failed = False
            self.t.upstream_reason = "upstream failed -- this chain's state is meaningless"
        return r


def _live(t):
    return t.session is not None


def _fail(msg):
    raise ExpectationFailed(msg)


# ------------------------------------------------------------------ source (offline)

def _parse_defs():
    root = ET.parse(DEFS_XML).getroot()
    out = {}
    for el in root.findall("LandmarkDef"):
        name = (el.findtext("defName") or "").strip()
        req = [m.tag for m in (el.find("mutatorChances") or [])
               if (m.get("Required") or "").lower() == "true"]
        out[name] = {"mayRequire": el.get("MayRequire"), "required": req,
                     "icon": (el.findtext("iconTexturePath") or "").strip()}
    return out


@suite.chain("ishko_source")
def ishko_source(t):
    """Our own files, read whole. Runs in the live run too: it is what the ishko_defs chain
    is checking the RESOLVED game against."""
    # Each component guards its own body with `if _live(t):` (never `return`): a return inside
    # the first `with` left the whole chain, so declaration probing (session=None) never saw
    # the second component (GPT review 2026-10-22, finding 11).
    with _independent(t, "defs_gated_on_odyssey"):
        if _live(t):
            got = _parse_defs()
            t._record("defs in %s" % os.path.basename(DEFS_XML), sorted(got))
            if sorted(got) != sorted(n for n, _, _, _ in LANDMARKS):
                _fail("LandmarkDefs in the XML are %s, expected exactly %s"
                      % (sorted(got), [n for n, _, _, _ in LANDMARKS]))
            bad = [n for n, d in got.items() if d["mayRequire"] != "Ludeon.RimWorld.Odyssey"]
            if bad:
                _fail("not MayRequire=\"Ludeon.RimWorld.Odyssey\": %s" % bad)
    with _independent(t, "icons_supplied_by_art_mod"):
        if _live(t):
            if not os.path.isdir(ART_TEX):
                _unmeasured(t, "art mod source folder not found at %s" % ART_TEX)
            missing = []
            for n, d in _parse_defs().items():
                png = os.path.join(ART_TEX, *(d["icon"].split("/"))) + ".png"
                t._record("%s icon %s" % (n, d["icon"]), os.path.isfile(png))
                if not d["icon"] or not os.path.isfile(png):
                    missing.append("%s -> %r" % (n, d["icon"]))
            if missing:
                _fail("iconTexturePath not supplied by AshkarrLandmarkArt: %s" % missing)


# ------------------------------------------------------------------ defs (live readback)

def _row(r, def_name):
    for d in (r or {}).get("defs") or []:
        if d.get("defName") == def_name:
            return d
    return None


def _chances(raw):
    """deep get_defs of List<MutatorChance> -> [(mutator, chance, required)]; [] if not structured."""
    out = []
    for e in raw if isinstance(raw, list) else []:
        if isinstance(e, dict):
            out.append((str(e.get("mutator")), e.get("chance"),
                        str(e.get("required")).lower() == "true"))
    return out


@suite.chain("ishko_defs")
def ishko_defs(t):
    """Each LandmarkDef resolves in the running game, from OUR package (a defName
    collision would resolve to whichever mod loaded last), with the exact category,
    commonality, single Required anchor and a non-empty icon path."""
    for def_name, category, commonality, anchor in LANDMARKS:
        with _independent(t, "%s_resolves" % def_name):
            r = t.bridge_call("jawa/get_defs", defs="LandmarkDef/%s" % def_name,
                              fields="category,commonality,mutatorChances,iconTexturePath",
                              deep=True)
            if not _live(t):
                continue
            if not (r or {}).get("success"):
                _unmeasured(t, "jawa/get_defs did not answer: %s" % (r or {}).get("message"))
            row = _row(r, def_name)
            if not row or not row.get("found"):
                _fail("%s does not resolve (notFound=%s)" % (def_name, (r or {}).get("notFound")))
            t._record("%s packageId" % def_name, row.get("packageId"))
            if str(row.get("packageId") or "").lower() != PACKAGE_ID:
                _fail("%s resolves from %r, not %s -- a defName collision"
                      % (def_name, row.get("packageId"), PACKAGE_ID))
            f = row.get("fields") or {}
            t._record("%s fields" % def_name, f)
            if str(f.get("category")) != category:
                _fail("%s.category = %r, expected %r" % (def_name, f.get("category"), category))
            try:
                comm = float(f.get("commonality"))
            except (TypeError, ValueError):
                _fail("%s.commonality unreadable: %r" % (def_name, f.get("commonality")))
            if abs(comm - commonality) > 1e-6:
                _fail("%s.commonality = %r, expected %r" % (def_name, comm, commonality))
            ch = _chances(f.get("mutatorChances"))
            if not ch:
                _unmeasured(t, "%s.mutatorChances came back unstructured: %r"
                            % (def_name, f.get("mutatorChances")))
            req = [(m, c) for m, c, rq in ch if rq]
            if [m for m, _ in req] != [anchor]:
                _fail("%s Required mutators = %s, expected exactly [%s]" % (def_name, req, anchor))
            try:
                anchor_chance = float(req[0][1])
            except (TypeError, ValueError):
                anchor_chance = None
            if anchor_chance is None or abs(anchor_chance - 1.0) > 1e-6:
                _fail("%s anchor %s chance = %r, expected 1 (a Required entry)"
                      % (def_name, anchor, req[0][1]))
            want_icon = _parse_defs()[def_name]["icon"]
            if f.get("iconTexturePath") != want_icon:
                _fail("%s.iconTexturePath = %r, expected %r (our XML)"
                      % (def_name, f.get("iconTexturePath"), want_icon))


# ------------------------------------------------------------------ placement (behaviour)

def _candidate_tiles(t, n):
    r = t.bridge_call("jawa/world_mutators_get", range=TILE_SCAN, limit=2000)
    if not (r or {}).get("success"):
        _unmeasured(t, "jawa/world_mutators_get did not answer: %s" % (r or {}).get("message"))
    anchors = set(a for _, _, _, a in LANDMARKS)
    # A tile already carrying an anchor would make "placement creates the anchor" vacuous.
    rows = [x for x in (r.get("tiles") or [])
            if not x.get("waterCovered") and not x.get("landmark")
            and not anchors & set(m.get("def") for m in (x.get("mutators") or []))]
    if len(rows) < n:
        _unmeasured(t, "only %d land tiles without a landmark in %s" % (len(rows), TILE_SCAN))
    return rows[:n]


def _tile(t, tile):
    r = t.bridge_call("jawa/world_mutators_get", tiles=str(tile))
    rows = (r or {}).get("tiles") or []
    if not (r or {}).get("success") or not rows:
        _unmeasured(t, "could not read tile %s back: %s" % (tile, (r or {}).get("message")))
    return rows[0]


@suite.chain("ishko_placement")
def ishko_placement(t):
    """Placing each landmark (the owner's act on the real save) does what the def says:
    the tile carries our LandmarkDef and its Required anchor mutator. Each landmark on
    its own fresh land tile; cleaned up after."""
    picks = None
    for i, (def_name, _cat, _comm, anchor) in enumerate(LANDMARKS):
        with _independent(t, "%s_places_with_anchor" % def_name):
            if not _live(t):
                continue
            if picks is None:
                picks = _candidate_tiles(t, len(LANDMARKS))
            tile = int(picks[i]["tile"])
            before = set(m.get("def") for m in (picks[i].get("mutators") or []))
            try:
                r = t.bridge_call("jawa/world_landmarks_set", action="add", tiles=str(tile),
                                  forced=True, checkValid=True, **{"def": def_name})
                if not (r or {}).get("success") or int(r.get("added") or 0) != 1:
                    _fail("world_landmarks_set add %s on tile %d: success=%s added=%s errors=%s"
                          % (def_name, tile, (r or {}).get("success"), (r or {}).get("added"),
                             (r or {}).get("errors")))
                back = _tile(t, tile)
                muts = [m.get("def") for m in (back.get("mutators") or [])]
                # validity is recorded, not asserted: this is FORCED authoring (the owner's hand),
                # not a claim that the tile is a legal natural site.
                t._record("tile %d after add" % tile, {"landmark": back.get("landmark"), "mutators": muts,
                                                      "validity": r.get("validity")})
                if back.get("landmark") != def_name:
                    _fail("tile %d landmark = %r after add, expected %s" % (tile, back.get("landmark"), def_name))
                if anchor not in muts:
                    _fail("tile %d carries %s but not its Required anchor %s (mutators %s)"
                          % (tile, def_name, anchor, muts))
            except BaseException:
                try:
                    _restore(t, tile, before)
                except Exception:                              # noqa: BLE001 -- keep the first failure
                    pass
                raise
            _restore(t, tile, before)


def _restore(t, tile, before):
    """Put the tile back: landmark removed, every mutator AddLandmark added (the anchor AND any
    optional roll) removed, every one it displaced re-added; then read back and compare. A
    restore that does not verify is a FAIL, never a silent pass (GPT review 2026-10-22, #3)."""
    t.session.call("jawa/world_landmarks_set", action="remove", tiles=str(tile))
    now = _tile(t, tile)
    cur = set(m.get("def") for m in (now.get("mutators") or []))
    extra, lost = sorted(cur - before), sorted(before - cur)
    if extra:
        t.session.call("jawa/world_mutators_set", action="remove", mutators=",".join(extra), tiles=str(tile))
    if lost:
        t.session.call("jawa/world_mutators_set", action="add", mutators=",".join(lost), tiles=str(tile))
    end = _tile(t, tile)
    end_m = set(m.get("def") for m in (end.get("mutators") or []))
    t._record("tile %d restore" % tile, {"removed": extra, "readded": lost,
                                         "landmark": end.get("landmark"), "mutators": sorted(end_m)})
    if end.get("landmark") or end_m != before:
        _fail("tile %d not restored: landmark=%r mutators=%s, expected none and %s"
              % (tile, end.get("landmark"), sorted(end_m), sorted(before)))


# ======================================================================
# THE NINE (Ninefold) -- moved here 2026-10-22 from the retired mandrake.rm.ninefold's own
# validation.py when the engine was folded into Salvation Rites (owner: "the Nine Gods belong in
# Salvation Rites"). Chains and component names are unchanged; the M0 safe core ONLY.
#
# CAUTION -- NINEFOLD_DEBUG_GAME_READY_CRASH_1: a known crash item ties a
# `start_debug_game_ready`-shaped debug bootstrap (RimWorld's "instant colony
# ready" / auto-research-burst dev helper) to a crash when Ninefold's satiation
# hooks fire mid-burst. This suite deliberately NEVER uses that shortcut: every
# chain below builds its own state explicitly (clear_area + its own spawns /
# pregnancy calls / research_finish_project calls), never an auto-research-burst
# bootstrap. Whoever runs this live: if the runner's own quicktest-map setup
# uses a `start_debug_game_ready`-style call ahead of this suite, disable it
# first or run Ninefold's validation alone against a plain map.
#
# SCOPE -- "M0 safe core" is the mod's OWN description (the old About.xml): the nine-god
# vector, the band ladder (SatiationBand.cs), the per-god Mood random walk, and
# exactly FIVE Harmony hooks (research completed, mental break started, birth
# outcome, building deconstructed, building repaired). The assembly ships ~13
# more Patch_*.cs hooks (art, battle, droid, explosion, faction, fire, gravship,
# kill manner, marriage, prisoner, trade, catatonic, plus ChronicleSubscriber's
# soft cross-engine binding to mandrake.rm.aftermath) -- those are later wiring
# (NINEFOLD_MISSING_EVENT_HOOKS_1 and its successors) and the mod's own naming
# scopes them OUT of "M0". Not covered here, by instruction.
#
# FELT-ONLY / NO UI -- design/Jawa/divine_satiation_engine.md and this mod's own
# source (Mood's class-level comment on GameComponent_Ninefold: "NEVER surfaced
# as a UI number... read only through ambient gesture/narration callers, never
# printed") mean there are NO panels and NO debug actions (grepped: this mod
# ships zero [DebugAction]-attributed methods, unlike Pits' PitDebugActions.cs)
# and NO bridge getter for the vector. The only independent read-back this
# suite found at all is `GameComponent_Ninefold.ApplyDelta`'s own
# `Log.Message`, itself gated on `Prefs.DevMode` -- every chain below forces
# devMode on via `jawa/prefs` (bridge_call escape valve; there is no suite.py
# verb for Prefs) before doing anything, and every satiation-changing component
# reads the ledger back through `jawa/drain_log`'s `contains` filter, embedding
# the exact expected delta substring (e.g. "[Ninefold] Ozzik satiation +15.0")
# as `expect_log_contains`'s own `tag` argument, since the log line's actual
# shape ("<god> satiation <+-N.N> (<reason>) -> <total> [<band>]") does not fit
# `expect_log_contains`'s separate field=value substring form.
#
# MOOD has NO read-back channel anywhere, by design (see above) -- not a log
# line, not a getter, not a debug action. The `mood_walk_tick` chain's
# component can only prove the game clock crosses one MoodWalkIntervalTicks
# boundary (2500 ticks / one in-game hour) with the engine on; it CANNOT prove
# the walk moved, or that moodWalkMultiplier scaled anything. This is this
# suite's known weakest link -- an instrumentation gap, not a shortcut taken
# here on purpose to look green.
#
# MOD SETTINGS ARE STATIC FIELDS -- RM_NinefoldSettings's four original fields
# (engineEnabled, firstContactLettersEnabled, eventMagnitudeMultiplier,
# moodWalkMultiplier) are all `public static`. Per the Pits pilot's own
# documented finding (src/RimMandrake/FlowWorks/validation.py's trailing comment),
# `t.set_setting` / `rimworld/update_mod_settings` walks INSTANCE fields via
# reflection and refuses a static field outright ("Could not resolve field").
# No component here attempts a live toggle flip for that reason. Each of the
# four toggles instead gets a component that exercises the pathway it gates AT
# ITS SHIPPED DEFAULT (engine on, letters on, 1.0x multipliers) -- proving the
# gated code path runs at all, not that flipping the setting changes the
# outcome. Flipping these live needs a bridge fix or a settings-pattern change
# on this mod's own side; neither is attempted here.
#
# Still not proven / likely first-live-run corrections:
#   - RESEARCH_PROJECT ("Smithing", an early vanilla tier-1 project) may
#     already be finished on whatever quicktest colony this runs against, or
#     absent from a minimal mechanism-list load order -- `wasAlreadyFinished`
#     comes back in `jawa/research_finish_project`'s own response but is not
#     asserted here. A finding on this component should swap the project
#     picked, not fault the mod.
#   - `building_repaired` / `building_deconstructed`: the wait_ticks budgets
#     (5000 each) are a guess at how long ONE colonist takes to repair/
#     deconstruct a `Wall` from bridge-dealt damage -- the most likely
#     candidate in this file for a live-run tick-count correction, same
#     category as Pits' own first-live-run notes.
#   - `building_repaired` only exercises Rekko's half -- `Wall` carries no
#     CompPowerTrader, so Ohm's "machine rewoken" branch is untested here.
#   - `birth_outcome`: `jawa/pawn_pregnancy` progress=1 "begins labour on the
#     next tick" per its own tool doc, but the labour-to-ApplyBirthOutcome
#     pipeline's real tick length is unmeasured offline; wait_ticks=3000 is a
#     guess. A stillbirth (outcome.Positive == false) would also correctly
#     produce no delta and no log line, and this chain cannot distinguish
#     "hasn't happened yet" from "fired negative" -- it does not additionally
#     check pawn/child state.
#   - `mood_walk_tick`'s component is UNVERIFIED by design -- see the MOOD
#     paragraph above.
#   - `jawa/ordered_job` is called with `waitTicks=0` deliberately (its own
#     default is 60): its own internal read-back wait would otherwise advance
#     the game clock outside this suite's own `t.wait_ticks`, in tension with
#     spec §1b's "time stays paused except inside an explicit wait_ticks".
#     `waitTicks=0` minimises that; it is not eliminated, because the tool
#     itself ticks briefly to read `curJob` back regardless.
# ======================================================================

RESEARCH_PROJECT = "Smithing"   # early vanilla tier-1 project -- see docstring caveat
# MEASURED 2026-10-08: FinishProject on an already-finished project fires no delta (the Prefix/__state guard), so a
# second run on the same game read FAIL. The chain now picks the first candidate still startable (unfinished).
RESEARCH_CANDIDATES = ("Smithing", "Machining", "Brewing", "Batteries", "Stonecutting", "Pottery")
WALL_DEF = "Wall"


def _devmode_on(t):
    """Every satiation read-back in this suite rides ApplyDelta's own
    DevMode-gated Log.Message (see module docstring) -- there is no suite.py
    verb for Prefs, so this goes through the bridge_call escape valve."""
    t.bridge_call("jawa/prefs", devMode=True)


@suite.chain("research_completed")
def research_completed(t):
    """Patch_ResearchCompleted: ApplyDelta(Ozzik, Large) + ApplyDelta(Ohm,
    Small). `jawa/research_finish_project` calls ResearchManager.FinishProject
    directly -- the same method the patch binds to -- so this exercises the
    real Harmony hook, not a simulation of it."""
    t.clear_area(size=20)
    _devmode_on(t)
    with t.component("research_completed_ledger", toggle="engineEnabled"):
        proj = RESEARCH_PROJECT
        for cand in RESEARCH_CANDIDATES:
            av = t.bridge_call("jawa/research_availability", project=cand) or {}
            if av.get("success") and av.get("canStartNow"):
                proj = cand
                break
        t.bridge_call("jawa/research_finish_project", project=proj,
                      doCompletionLetter=False)
        t.expect_log_contains("[Ninefold] Ozzik satiation +15.0")
        t.expect_log_contains("[Ninefold] Ohm satiation +3.0")
        t.screenshot()


@suite.chain("mental_break_started")
def mental_break_started(t):
    """Patch_MentalBreakStarted: ApplyDelta(Zizzik, Large) on any humanlike
    player-colonist mental break. `jawa/pawn_force_mental_break` drives
    MentalBreaker.TryDoMentalBreak -> MentalStateHandler.TryStartMentalState,
    the exact method this patch postfixes."""
    t.clear_area(size=20)
    _devmode_on(t)
    colonist = t.spawn_pawn("Colonist", hostile=False)
    # The break below is this test's OWN act. Declare it so the situational detectors do not report the
    # induced break (its pawn state and its "<break>: <name>" letter) as a surprise (MEASURED 2026-10-01: a
    # false SURPRISE recorded against this chain). Matches the pawn row by id and the letter by short name.
    short = ((((t.bridge_call("jawa/pawn_get", pawn=colonist) or {}).get("pawns") or [{}])[0])
             .get("nameShort") or "")
    t.expect("mental", lambda e, pid=colonist, nm=short:
             e.get("id") == pid or bool(nm and nm in (e.get("label") or "")))
    with t.component("mental_break_ledger", toggle="eventMagnitudeMultiplier"):
        t.bridge_call("jawa/pawn_force_mental_break", pawn=colonist,
                      intensity="minor")
        t.expect_log_contains("[Ninefold] Zizzik satiation +15.0")
        t.screenshot()


@suite.chain("building_repaired_and_deconstructed")
def building_repaired_and_deconstructed(t):
    """One chain, two components sharing setup (spec §1) -- both hooks are
    driven off the same colonist working the same Wall in turn: damage it,
    order Repair, confirm Rekko's ledger; then order Deconstruct on the (now
    healed) same wall and confirm Rekko/Zizzik's opposite-signed pair. Plain
    `Wall` has no CompPowerTrader -- see docstring's Ohm caveat."""
    t.clear_area(size=20)
    _devmode_on(t)
    x, z = t.anchor
    cells = t.spawn(WALL_DEF, count=1, at="line")
    worker = t.spawn_pawn("Colonist", hostile=False, beyond=cells)
    # Patch_BuildingRepaired only counts a PLAYER-faction building, and a spawn_batch wall has no faction.
    rows = (t.bridge_call("jawa/list_things", defName=WALL_DEF,
                          rect="%d,%d,3,3" % (x - 1, z - 1)) or {}).get("things") or []
    wall = rows[0].get("id") if rows else None
    if wall:
        t.bridge_call("jawa/set_thing_props", thing=wall, faction="PlayerColony")

    with t.component("building_repaired", toggle="firstContactLettersEnabled"):
        # CORRECTED 2026-10-02 (MODCHECK_SUITE_CORRECTIONS_1): "Bomb" 40 DESTROYED the 195-HP wall
        # (hitPointsAfter 0, destroyed true), so the Repair job had nothing to repair. A blunt hit of 40
        # leaves it standing and damaged, which is the state the repair hook needs.
        t.bridge_call("jawa/damage", damageDef="Blunt", amount=40, x=x, z=z,
                      allowColonists=False)
        t.bridge_call("jawa/ordered_job", pawnId=worker, jobDef="Repair",
                      targetAX=x, targetAZ=z, waitTicks=0)
        t.wait_ticks(5000)
        t.expect_log_contains("[Ninefold] Rekko satiation +15.0 (repaired")
        t.screenshot()

    with t.component("building_deconstructed", beyond_toggle=True):
        # MEASURED 2026-10-08: an undesignated Deconstruct order fails TryMakePreToilReservations; designate first.
        t.bridge_call("jawa/designate_batch", action="add", designation="Deconstruct",
                      rect="%d,%d,1,1" % (x, z))
        t.bridge_call("jawa/ordered_job", pawnId=worker, jobDef="Deconstruct",
                      targetAX=x, targetAZ=z, waitTicks=0)
        t.wait_ticks(5000)
        t.expect_log_contains("[Ninefold] Rekko satiation -15.0 (deconstructed")
        t.expect_log_contains("[Ninefold] Zizzik satiation +3.0 (waste")
        t.screenshot()


@suite.chain("birth_outcome")
def birth_outcome(t):
    """Weakest chain in this suite -- see docstring's 'Still not proven'.
    `jawa/pawn_pregnancy` is the only bridge surface that can drive a birth
    without waiting out a real relationship/lovin' cycle."""
    t.clear_area(size=20)
    _devmode_on(t)
    mother = t.spawn_pawn("Colonist", hostile=False)
    with t.component("birth_outcome_ledger", beyond_toggle=True):
        t.bridge_call("jawa/pawn_pregnancy", pawn=mother, action="start")
        t.bridge_call("jawa/pawn_pregnancy", pawn=mother, action="progress",
                      progress=1.0)
        # CORRECTED 2026-10-02: 3000 ticks cannot reach a birth. Biotech's PregnancyLabor lasts
        # 1700~25000 ticks and PregnancyLaborPushing 800~5000 more (Hediffs_Global_Misc.xml), so the
        # worst case is 30000; the birth hook (ApplyBirthOutcome) runs only when pushing ends.
        t.wait_ticks(31000)
        t.expect_log_contains("[Ninefold] Oomo satiation +15.0 (birth")
        t.expect_log_contains("[Ninefold] MobUnloo satiation +3.0 (birth")
        t.screenshot()


@suite.chain("mood_walk_tick")
def mood_walk_tick(t):
    """UNVERIFIED BY DESIGN (see docstring's MOOD paragraph) -- Mood has no
    read-back channel anywhere in this mod. This component only proves the
    game clock crosses one MoodWalkIntervalTicks boundary (2500 ticks) with
    the engine on; it cannot prove the walk moved or that moodWalkMultiplier
    scaled it. Satisfies the toggle floor for `moodWalkMultiplier` honestly
    rather than inventing a channel that does not exist."""
    t.clear_area(size=10)
    _devmode_on(t)
    with t.component("mood_walk_advances", toggle="moodWalkMultiplier"):
        t.wait_ticks(2600)
        t.bridge_call("jawa/prefs")   # read-only ping; no mood claim made
        t.screenshot()
