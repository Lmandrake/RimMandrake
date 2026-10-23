"""validation.py -- modcheck suite for Salvation Rites
(mandrake.rut.rites).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Rites

(environment: the `rites` tier -- minimal + mandrake.rut.antiquities +
mandrake.rut.ashkarrlandmarkart, per this mod's own hard
`<modDependencies>`/`<loadAfter>`; Odyssey resolves with the DLCs).

Grounded in the mod's actual source, read whole before writing this: this
mod is PURE DATA -- XML Defs only (the research tree in
`Defs/RUT_Rites_Research.xml`, the rituals and precepts beside it, and
Ishko's three landmarks in `Defs/RUT_IshkoLandmarks.xml`), no
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
