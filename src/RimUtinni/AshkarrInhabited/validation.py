"""validation.py -- modcheck suite for RimUtinni: Inhabited (Ash'karr)
(mandrake.rut.inhabited).

Pure-Defs companion mod: no Source/, no Assemblies/, no ModSettings class --
`src/RimUtinni/AshkarrInhabited/` holds only About/About.xml and six Defs
files under `SecurityProfileDefs/` and `SettlementManifestDefs/`, all read in
full before writing this. `suite.toggles = []`, every component
`beyond_toggle=True`.

WHAT THIS MOD IS: DATA for `mandrake.rm.inhabited`'s `SecurityProfileDef` /
`SettlementManifestDef` schema (a HARD `modDependency`, not merely
`loadAfter` -- both C# classes live in
`src/RimMandrake/Inhabited/Source/SecurityProfileDef.cs` and
`SettlementManifestDef.cs`, read in full before writing this). This mod
names four real Ash'karr settlements, one per faction, per SETTLEMENT_
VISIT_LOOP_1 / DISTRICT_TEMPLATE_LIBRARY_1: The Claim Jump (Junkers), Deepwater
Hold (Deepwater Compact), Gorga the Immense's Palace (Hutt Cartel), The
Cracking Yard (Free Droid Enclaves). No district art, no verb tuning, no
claim math -- About.xml's own description says so, and there is genuinely
nothing else in this mod's files to test.

🔴 THE WALK DOC (`design/validation_walks/RimUtinni/AshkarrInhabited.md`) IS
STALE ON EVERY `factionDefName` IT NAMES -- checked directly against the
actual XML, not assumed: its "## must be true" and "## the walk" sections
write `Jawa_Junkers`, `Jawa_DeepwaterCompact`, `Jawa_HuttCartel`,
`Jawa_FreeDroidEnclaves` (bare), but every one of the four shipped
`SettlementManifestDef`s actually carries the `RUT_`-prefixed defName
(`RUT_Jawa_Junkers`, `RUT_Jawa_DeepwaterCompact`, `RUT_Jawa_HuttCartel`,
`RUT_Jawa_FreeDroidEnclaves` -- confirmed against
`src/RimUtinni/UtinniPatches/Defs/FactionDefs/*.xml`, where every one of
these FactionDefs' own `<defName>` carries the `RUT_` prefix; there is no
bare `Jawa_Junkers` FactionDef anywhere in this tier). `SettlementManifestDef
.factionDefName`'s own doc-comment in the engine mod even gives
"RUT_Jawa_Junkers" as its own example. This suite asserts the REAL
(`RUT_`-prefixed) values below, not the walk doc's stale ones -- a live
`jawa/get_defs` check against the bare names would report "not found" and be
wrong to trust.

Exact facts below, read directly from the six Defs files, not guessed:
  - 4 SecurityProfileDefs: Inhabited_SecurityProfile_Junkers (false/0),
    _HuttCartel (true/0.6), _FreeDroids (false/0), _Deepwater (true/1) --
    matches the walk doc's own numbers exactly (only the faction-defName
    prefix is stale, not these).
  - 4 SettlementManifestDefs, each naming one SecurityProfileDef above (no
    dangling reference -- checked directly against the XML), one
    InhabitedPlaceDef from the RimMandrake tier, and a first district
    (`districts[0]`) matching the walk doc's labels: "scrapyard", "cistern
    hall", "palace hall", "charging hall" -- v1's compose step
    (`GenStep_ComposeSettlementDistrict`) reads only `districts[0]`, per that
    class's own field doc-comments, so this is the one district slot that
    actually matters at runtime; the rest is schema proven early.
  - Every manifest's `castSlots` is non-empty (4, 5, 7, and 5 entries
    respectively) but deliberately carries no `castDef` anywhere in this
    mod -- both engine doc-comments and every manifest's own header comment
    say so explicitly ("no InhabitedCastDef exists yet for any place").

WHY EVERY COMPONENT IS A DEF READ-BACK, NOT A LIVE COMPOSE TEST: this mod
carries zero C#, zero mechanism of its own -- `GenStep_ComposeSettlementDistrict`
and `WorldObject_Inhabited.InstantiateCast` live entirely in
`mandrake.rm.inhabited`. Whether a settlement actually composes its scrapyard
district or rolls its cast slots correctly is that engine mod's own
validation.py's job (not yet written, as of this pass -- check before
assuming it exists), not this Defs-only companion's.

Still not proven / real gaps:
  1. `jawa/list_factions` (the walk doc's own step 11, confirming
     RUT_Jawa_Junkers etc. are live, loaded factions on the world) is not
     exercised here -- this suite proves the manifest's OWN string field,
     not that the named FactionDef resolves to a real world faction. Would
     need the full RimUtinni patches tier active, not just minimal+
     mandrake.rm.inhabited.
  2. No live district COMPOSE or cast-slot ROLL is exercised -- see module
     docstring above; that belongs to the engine mod's own suite.
  3. `securityProfile`/`place` are typed def-reference fields
     (`SecurityProfileDef`/`InhabitedPlaceDef`), not free-text -- checked
     against `JawaBenchTerrainTools.cs`'s `Scalars()`: a `Def`-typed field
     always collapses to its bare defName regardless of `deep`, so the
     check below (`str(...)` + substring) is correct as written.

🔴 FOUND AND FIXED (wave 12): `districts` is `List<DistrictSlot>`
(`SettlementManifestDef.cs`), and `DistrictSlot` is a plain non-Def class --
per `Scalars()`'s own documented behaviour, a list of non-scalar, non-Def
items with `deep=false` (the OLD default here) serialises each item as its
bare TYPE NAME string (`"DistrictSlot"`), never a dict with a `label` key.
`settlement_manifests_readback`'s `_get_defs` call never passed `deep=True`,
so `districts[0]` could never come back as a dict and the fallback
`district0_label not in str(districts)` substring check was comparing
against a stringified list of type-name strings -- guaranteed to fail on
every live run that reached this component, regardless of whether the real
label matched. `castSlots`' own check only needed `len()`, which survives
either shape, so that half was never actually broken. Fixed by passing
`deep=True` on this one call (`_get_defs` now takes an optional `deep`
kwarg); `DeepSerializeValue` (same file) confirms a `DistrictSlot` at
`deep=True` really does expose `label` as a field.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("AshkarrInhabited")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

SEC_TYPE = "RimMandrake.Inhabited.SecurityProfileDef"
MANIFEST_TYPE = "RimMandrake.Inhabited.SettlementManifestDef"

# Verbatim from SecurityProfileDefs_Junkers.xml / SecurityProfileDefs_District2.xml.
SECURITY_EXPECT = {
    "Inhabited_SecurityProfile_Junkers": {"searchesLeavers": "False", "searchChance": "0"},
    "Inhabited_SecurityProfile_HuttCartel": {"searchesLeavers": "True", "searchChance": "0.6"},
    "Inhabited_SecurityProfile_FreeDroids": {"searchesLeavers": "False", "searchChance": "0"},
    "Inhabited_SecurityProfile_Deepwater": {"searchesLeavers": "True", "searchChance": "1"},
}

# Verbatim from the four SettlementManifestDefs_*.xml files. factionDefName
# uses the REAL RUT_-prefixed defName (see module docstring's stale-walk-doc
# finding), not the walk doc's bare form.
MANIFEST_EXPECT = {
    "Inhabited_Manifest_TheClaimJump": {
        "factionDefName": "RUT_Jawa_Junkers",
        "securityProfile": "Inhabited_SecurityProfile_Junkers",
        "place": "RM_InhabitedPlace_Scrapyard",
        "district0_label": "scrapyard",
        "min_cast_slots": 4,
    },
    "Inhabited_Manifest_DeepwaterHold": {
        "factionDefName": "RUT_Jawa_DeepwaterCompact",
        "securityProfile": "Inhabited_SecurityProfile_Deepwater",
        "place": "RM_InhabitedPlace_WaterHold",
        "district0_label": "cistern hall",
        "min_cast_slots": 5,
    },
    "Inhabited_Manifest_GorgaPalace": {
        "factionDefName": "RUT_Jawa_HuttCartel",
        "securityProfile": "Inhabited_SecurityProfile_HuttCartel",
        "place": "RM_InhabitedPlace_Palace",
        "district0_label": "palace hall",
        "min_cast_slots": 7,
    },
    "Inhabited_Manifest_TheCrackingYard": {
        "factionDefName": "RUT_Jawa_FreeDroidEnclaves",
        "securityProfile": "Inhabited_SecurityProfile_FreeDroids",
        "place": "RM_InhabitedPlace_MachineHold",
        "district0_label": "charging hall",
        "min_cast_slots": 5,
    },
}


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


def _get_defs(t, def_type, names, fields, deep=False):
    pairs = ";".join("%s/%s" % (def_type, n) for n in names)
    return t.bridge_call("jawa/get_defs", defs=pairs, fields=fields, deep=deep)


def _rows_by_name(r):
    return {row.get("defName"): row for row in (r or {}).get("defs") or []}


@suite.chain("security_profiles_readback")
def security_profiles_readback(t):
    """All 4 SecurityProfileDefs resolve with the exact searchesLeavers/
    searchChance pair authored in the two Defs files."""
    t.clear_area(size=8)
    names = list(SECURITY_EXPECT)

    with t.component("all_four_security_profiles_match_shipped_xml",
                     beyond_toggle=True):
        r = _get_defs(t, SEC_TYPE, names, "searchesLeavers,searchChance")
        if _live(t):
            rows = _rows_by_name(r)
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                bad.append("not found: %r" % not_found)
            for name, expect in SECURITY_EXPECT.items():
                row = rows.get(name)
                if row is None:
                    continue
                fields = row.get("fields") or {}
                for field, expect_value in expect.items():
                    got = fields.get(field)
                    if str(got) != str(expect_value):
                        bad.append("%s.%s: expected %r, got %r"
                                  % (name, field, expect_value, got))
            if bad:
                raise ExpectationFailed(
                    "SecurityProfileDef mismatch: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("settlement_manifests_readback")
def settlement_manifests_readback(t):
    """All 4 SettlementManifestDefs resolve; factionDefName (the REAL
    RUT_-prefixed value, not the stale walk doc's bare form -- see module
    docstring), securityProfile, place, districts[0].label and a non-empty
    castSlots all match the shipped XML."""
    t.clear_area(size=8)
    names = list(MANIFEST_EXPECT)

    with t.component("all_four_manifests_match_shipped_xml",
                     beyond_toggle=True):
        r = _get_defs(t, MANIFEST_TYPE, names,
                      "factionDefName,securityProfile,place,districts,castSlots",
                      deep=True)
        if _live(t):
            rows = _rows_by_name(r)
            not_found = (r or {}).get("notFound") or []
            bad = []
            if not_found:
                bad.append("not found: %r" % not_found)
            for name, expect in MANIFEST_EXPECT.items():
                row = rows.get(name)
                if row is None:
                    continue
                fields = row.get("fields") or {}

                got_faction = fields.get("factionDefName")
                if str(got_faction) != expect["factionDefName"]:
                    bad.append("%s.factionDefName: expected %r, got %r"
                              % (name, expect["factionDefName"], got_faction))

                got_sec = str(fields.get("securityProfile"))
                if expect["securityProfile"] not in got_sec:
                    bad.append("%s.securityProfile: expected %r in %r"
                              % (name, expect["securityProfile"], got_sec))

                got_place = str(fields.get("place"))
                if expect["place"] not in got_place:
                    bad.append("%s.place: expected %r in %r"
                              % (name, expect["place"], got_place))

                districts = fields.get("districts")
                d0_label = None
                if isinstance(districts, list) and districts:
                    d0 = districts[0]
                    d0_label = d0.get("label") if isinstance(d0, dict) else None
                if d0_label != expect["district0_label"] and \
                        expect["district0_label"] not in str(districts):
                    bad.append("%s.districts[0].label: expected %r, got %r "
                              "(raw districts=%r)"
                              % (name, expect["district0_label"], d0_label, districts))

                cast_slots = fields.get("castSlots")
                n_cast = len(cast_slots) if isinstance(cast_slots, list) else 0
                if n_cast < expect["min_cast_slots"]:
                    bad.append("%s.castSlots: expected >= %d entries, got %d "
                              "(raw=%r)"
                              % (name, expect["min_cast_slots"], n_cast, cast_slots))
            if bad:
                raise ExpectationFailed(
                    "SettlementManifestDef mismatch: %s" % "; ".join(bad))
        t.screenshot()
