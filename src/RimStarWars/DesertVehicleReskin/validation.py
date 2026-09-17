"""validation.py -- modcheck suite for RimStarWars Desert Vehicle Reskin --
Alpha Vehicles Neolithic (mandrake.rsw.desertvehiclereskin).

Grounded in the mod's actual Source and Patches, read whole before writing
this: `RM_DraughtFuelExtension.cs` (the marker DefModExtension),
`VegetableFuel.cs` (the widened-fuel rule -- `Accepts`/`IsVegetableFood`,
gated on `RSW_DesertVehicleReskinSettings.allowAnyVegetableFuel`),
`VehicleFuelPatches.cs` (the Harmony prefix/postfix on
`CompFueledTravel.ClosestFuelAvailable`/`AllFuelFromInventory`, and the
`DesertVehicleReskinMod` bootstrap that skips widening entirely -- with a
named `Log.Warning`, not a crash -- when the `Vehicles` assembly is not
loaded), `RSW_DesertVehicleReskinSettings.cs` (the ONE real settings
field), and `FuelDebugActions.cs` (the mod's OWN built-in verify tool,
`[DebugAction("Vehicles", "List widened vehicle fuel")]` -- see below for
why this suite drives it rather than inventing a separate live-refuel
test). Also read whole: all five `Patches/*.xml` files (`DraughtFuel_
Marker.xml`, `BeastVehicle_Identity.xml`, `BeastVehicleProp_Identity.xml`,
`DogSledTint_Brown.xml`, `EopieSled_Identity.xml`) and `About.xml`.

🔴 THE WALK DOC (`design/validation_walks/RimMandrake/
DesertVehicleReskin.md`) NAMES THE WRONG NAMESPACE for the fuel-extension
marker class. Its step 6 says every draught VehicleDef should carry a
`modExtensions` `li` of `Class="RimMandrake.StarWars.
DesertVehicleReskin.RM_DraughtFuelExtension"`. MEASURED directly, 2026-09-17:
`RM_DraughtFuelExtension.cs` line 3 declares `namespace RimMandrake.
DesertVehicleReskin` (NO `.StarWars.` segment), and `DraughtFuel_Marker.xml`
itself patches in `Class="RimMandrake.DesertVehicleReskin.
RM_DraughtFuelExtension"` -- matching the C#, not the walk doc. (This mod
lives under `src/RimStarWars/` on disk and its packageId is
`mandrake.rsw.*`, but its C# namespace was never migrated to the
`RimMandrake.StarWars.<Mod>` tier grammar `NAMING_SCHEME_PLAN.md` calls
for -- a real, separate finding, out of scope to fix in this pass, but
worth flagging since it is exactly why the walk doc's guess at the
namespace was wrong.) `draught_fuel_extension_present` below asserts the
ACTUAL string, not the walk's.

🔴 THE WALK DOC'S OWN "anti-guessing notes" UNDERSTATE HOW DEAD steps 7-8
ARE. It says "No dedicated [B] bridge tool exists for 'attempt refuel'
specifically; use whichever ... tool is live at walk-run time." Per
`skills/rimbridge/references/traps.md`'s own measured section "Nothing
reaches a `VehiclePawn`'s UI or its comps": *"No tool anywhere mentions
fuel or refuel; the only two vehicle debug actions on the whole 583-mod
stack are `Ground All Aerial Vehicles` and one mod's own list action ...
A vehicle's fuel level ... [is] unreadable from the bridge today. Say
UNMEASURED; do not infer one from a hauler that did or did not move."*
This is a firmer, already-measured negative than the walk doc's softer
wording -- there is no live-refuel path to pin down at ALL today, not
merely an unconfirmed tool name. `widened_fuel_debug_action` below is the
substitute: it drives the mod's OWN `FuelDebugActions.
ListWidenedVehicleFuel` (the "one mod's own list action" traps.md's
sentence refers to), which runs `VegetableFuel.Accepts`/`IsVegetableFood`
against the REAL live def database and logs a verify line this suite
parses -- proving the actual widened-fuel logic end to end without a
vehicle, a spawn, or a refuel job at all.

MOD SETTINGS: one field, `allowAnyVegetableFuel` (`public static bool`,
default true) -- `suite.toggles = ["allowAnyVegetableFuel"]`.
`VegetableFuel.Accepts` reads it directly (module docstring above), so a
False flip should collapse the debug action's own report to
`declaredFuelType`-only; `toggle_flips` proves the flip/read-back
mechanics, and `widened_fuel_debug_action` (run at the shipped default,
true) proves the widened behavior itself.

Still not proven / likely first-live-run corrections:
  1. `Actions\\List widened vehicle fuel` (no `T:` prefix) follows
     Inhabited/validation.py's own measured finding that a plain
     `[DebugAction]` (no `actionType` override -- this one takes no
     arguments, so it cannot be `ToolMap`) gets NO prefix and its declared
     `category` ("Vehicles") is UI metadata, not a path segment. Not
     independently re-confirmed for THIS specific action via
     `list_debug_action_children`.
  2. The five reskin/identity XML patches (labels, descriptions, DogSled
     tint, the VFEPD prop pass) are all `PatchOperationReplace`/
     `PatchOperationFindMod` against third-party defs this mod does not
     own -- covered by def read-back only; no live visual check exists
     for whether the ART matches the new WORDS (walk doc's own [S] step:
     "a human-pass concern", and load order matters for the art to even
     appear, per About.xml's own "LOAD ORDER MATTERS HERE" section).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("DesertVehicleReskin")
suite.toggles = ["allowAnyVegetableFuel"]

SETTINGS_TYPE = "RimMandrake.DesertVehicleReskin.RSW_DesertVehicleReskinSettings"
FUEL_EXT_CLASS = "RimMandrake.DesertVehicleReskin.RM_DraughtFuelExtension"

DRAUGHT_VEHICLES = ["AV_Chariot", "AV_WarChariot", "AV_OxCart", "AV_CoveredCarriage", "AV_DogSled"]

VEHICLE_LABELS = {
    "AV_Chariot": "dewback chariot",
    "AV_WarChariot": "dewback war chariot",
    "AV_CoveredCarriage": "ronto wagon",
    "AV_OxCart": "bantha cart",
    "AV_DogSled": "eopie sled",
}
BLUEPRINT_LABELS = {
    "AV_Chariot_Blueprint": "dewback chariot",
    "AV_WarChariot_Blueprint": "dewback war chariot",
    "AV_CoveredCarriage_Blueprint": "ronto wagon",
    "AV_OxCart_Blueprint": "bantha cart",
    "AV_DogSled_Blueprint": "eopie sled",
}
VFEPD_LABELS = {
    "VFEPD_Chariot": "dewback chariot (prop)",
    "VFEPD_WarChariot": "dewback war chariot (prop)",
    "VFEPD_CoveredCarriage": "ronto wagon (prop)",
    "VFEPD_OxCart": "bantha cart (prop)",
    "VFEPD_DogSled": "eopie sled (prop)",
}

MUST_ACCEPT = ["Hay", "RawPotatoes", "RawCorn", "RawBerries", "RawFungus"]
# FuelDebugActions.cs's own MustReject array also lists "RawMeat", which the
# file's own comment says does not exist as a def ("the name the item's
# verify line uses"; Verdict() reports it "NO SUCH DEF (nothing proven)",
# never PASS/FAIL) -- deliberately excluded here so this suite never asserts
# PASS against a line that structurally cannot produce one.
MUST_REJECT = ["Meat_Cow", "Meat_Human", "Milk", "Beer"]


def _get_defs(t, defs, fields):
    return t.bridge_call("jawa/get_defs", defs=defs, fields=fields)


def _row_for(r, def_key):
    for d in (r or {}).get("defs", (r or {}).get("results", [])) or []:
        if d.get("defName") == def_key.split("/", 1)[-1]:
            return d
    return None


@suite.chain("no_config_or_patch_errors")
def no_config_or_patch_errors(t):
    """Walk step 1, plus the two hand-written failure strings
    `VehicleFuelPatches.Apply`/`DesertVehicleReskinMod` can log."""
    with t.component("no_config_xml_or_harmony_error", beyond_toggle=True):
        for tag in ("Config error in mandrake.rsw.desertvehiclereskin",
                    "Vehicle Framework's fuel API has moved",
                    "Failed to widen vehicle fuel types"):
            r = t.bridge_call("jawa/drain_log", limit=400, contains=tag)
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            t._record("drain_log(%r) -> %r" % (tag, msgs), not msgs)
            if msgs:
                raise ExpectationFailed(
                    "found an unexpected log line matching %r: %r" % (tag, msgs))


@suite.chain("vehicle_and_blueprint_identity")
def vehicle_and_blueprint_identity(t):
    """Walk steps 2/4: BOTH the VehicleDef and its `_Blueprint`
    VehicleBuildDef sibling must carry the new label -- the bug
    `BeastVehicle_Identity.xml` fixed was that `EopieSled_Identity.xml`
    (and, before this file, nothing for the other four) only ever patched
    the VehicleDef half, leaving the architect-menu blueprint still
    reading the donor's old words."""
    for def_name, expected in VEHICLE_LABELS.items():
        with t.component("vehicle_label_%s" % def_name, beyond_toggle=True):
            r = _get_defs(t, "Vehicles.VehicleDef/%s" % def_name, "label")
            row = _row_for(r, "Vehicles.VehicleDef/%s" % def_name)
            got = (row or {}).get("fields", {}).get("label", "")
            ok = got == expected
            t._record("%s.label -> %r" % (def_name, got), ok)
            if not ok:
                raise ExpectationFailed(
                    "%s.label = %r, expected %r" % (def_name, got, expected))

    for def_name, expected in BLUEPRINT_LABELS.items():
        with t.component("blueprint_label_%s" % def_name, beyond_toggle=True):
            r = _get_defs(t, "Vehicles.VehicleBuildDef/%s" % def_name, "label")
            row = _row_for(r, "Vehicles.VehicleBuildDef/%s" % def_name)
            got = (row or {}).get("fields", {}).get("label", "")
            ok = got == expected
            t._record("%s.label -> %r" % (def_name, got), ok)
            if not ok:
                raise ExpectationFailed(
                    "%s.label = %r, expected %r" % (def_name, got, expected))


@suite.chain("dogsled_tint_readback")
def dogsled_tint_readback(t):
    """`AV_DogSled`'s color triple should be the harness leather-brown, not
    the donor's grey (module docstring/DogSledTint_Brown.xml's own note:
    only `color` can reach a pixel under the shipped mask, colorTwo/Three
    are set for coherence but have no region to act on)."""
    with t.component("dogsled_color_triple", beyond_toggle=True):
        r = _get_defs(t, "Vehicles.VehicleDef/AV_DogSled",
                     "graphicData")
        row = _row_for(r, "Vehicles.VehicleDef/AV_DogSled")
        got = str((row or {}).get("fields", {}).get("graphicData", ""))
        ok = "99, 65, 24" in got or "(99,65,24)" in got.replace(" ", "")
        t._record("AV_DogSled.graphicData -> %r" % got, ok)
        if not ok:
            raise ExpectationFailed(
                "AV_DogSled.graphicData = %r, expected color (99, 65, 24)" % got)


@suite.chain("vfepd_prop_identity")
def vfepd_prop_identity(t):
    """Needs VanillaExpanded.VFEPropsandDecor active (MayRequire-guarded in
    all patches touching it, so absence is a silent no-op, not an error --
    this chain will fail named if the mod is not in this environment,
    which is the correct signal, not a bug). VFEPD_DogSled additionally
    needs the (99, 65, 24) color fix (EopieSled_Identity.xml's own prop
    half); the other four props were never retinted because their vehicle
    counterparts never were either (BeastVehicleProp_Identity.xml's own
    note: donor colors already match)."""
    for def_name, expected in VFEPD_LABELS.items():
        with t.component("vfepd_label_%s" % def_name, beyond_toggle=True):
            r = _get_defs(t, "ThingDef/%s" % def_name, "label,graphicData")
            row = _row_for(r, "ThingDef/%s" % def_name)
            if row is None:
                raise ExpectationFailed(
                    "ThingDef %s did not resolve -- VFE Props and Decor is "
                    "not active in this environment" % def_name)
            got = (row.get("fields") or {}).get("label", "")
            ok = got == expected
            t._record("%s.label -> %r" % (def_name, got), ok)
            if not ok:
                raise ExpectationFailed(
                    "%s.label = %r, expected %r" % (def_name, got, expected))

    with t.component("vfepd_dogsled_color_matches_vehicle", beyond_toggle=True):
        r = _get_defs(t, "ThingDef/VFEPD_DogSled", "graphicData")
        row = _row_for(r, "ThingDef/VFEPD_DogSled")
        got = str((row or {}).get("fields", {}).get("graphicData", ""))
        ok = "99, 65, 24" in got or "(99,65,24)" in got.replace(" ", "")
        t._record("VFEPD_DogSled.graphicData -> %r" % got, ok)
        if not ok:
            raise ExpectationFailed(
                "VFEPD_DogSled.graphicData = %r, expected color (99, 65, 24) "
                "to match the retinted vehicle" % got)


@suite.chain("draught_fuel_extension_present")
def draught_fuel_extension_present(t):
    """Asserts the ACTUAL namespace (module docstring's stale-walk-doc
    finding), not the walk's `.StarWars.`-inserted guess. A vehicle
    WITHOUT this extension falls through to unwidened vanilla fuel per
    `VehicleFuelPatches`' own guard -- this suite only spot-checks
    presence, not the fallback (which needs a non-draught VF vehicle,
    outside this mod's own environment)."""
    for def_name in DRAUGHT_VEHICLES:
        with t.component("modext_%s" % def_name, beyond_toggle=True):
            r = _get_defs(t, "Vehicles.VehicleDef/%s" % def_name, "modExtensions")
            row = _row_for(r, "Vehicles.VehicleDef/%s" % def_name)
            got = str((row or {}).get("fields", {}).get("modExtensions", ""))
            ok = FUEL_EXT_CLASS in got
            t._record("%s.modExtensions -> %r" % (def_name, got), ok)
            if not ok:
                raise ExpectationFailed(
                    "%s.modExtensions = %r, expected to contain %r"
                    % (def_name, got, FUEL_EXT_CLASS))


@suite.chain("widened_fuel_debug_action")
def widened_fuel_debug_action(t):
    """Drives the mod's OWN verify tool (`FuelDebugActions.
    ListWidenedVehicleFuel`) instead of attempting a live vehicle spawn +
    refuel job, which `skills/rimbridge/references/traps.md` already
    measured as impossible via any bridge tool today (module docstring).
    Runs at the shipped default (`allowAnyVegetableFuel=true`) -- proves
    the actual `VegetableFuel` rule against the real live def database."""
    with t.component("verify_line_reports_pass", toggle="allowAnyVegetableFuel"):
        t.bridge_call("rimworld/execute_debug_action",
                      path="Actions\\List widened vehicle fuel")
        r = t.bridge_call("jawa/drain_log", limit=400,
                          contains="widened vehicle fuel")
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        text = "\n".join(msgs)
        ok_count = "count >= 6 : True" in text
        t._record("count >= 6 line -> %s" % ok_count, ok_count)
        if not ok_count:
            raise ExpectationFailed(
                "'count >= 6 : True' not found in the debug action's own "
                "report; raw: %r" % text)

        for name in MUST_ACCEPT:
            line_ok = ("accepts %s : PASS" % name) in text
            t._record("accepts %s -> %s" % (name, line_ok), line_ok)
            if not line_ok:
                raise ExpectationFailed(
                    "expected 'accepts %s : PASS' in the debug action's "
                    "report; raw: %r" % (name, text))

        for name in MUST_REJECT:
            line_ok = ("rejects %s : PASS" % name) in text
            t._record("rejects %s -> %s" % (name, line_ok), line_ok)
            if not line_ok:
                raise ExpectationFailed(
                    "expected 'rejects %s : PASS' in the debug action's "
                    "report; raw: %r" % (name, text))
        t.screenshot()


@suite.chain("toggle_flips")
def toggle_flips(t):
    """`allowAnyVegetableFuel` is `public static`
    (BRIDGE_STATIC_SETTINGS_FIELDS_1 shape) -- flip+read-back only; the
    behavioral proof of what it gates is `widened_fuel_debug_action`
    above, run at the shipped default."""
    with t.component("allowAnyVegetableFuel_flips", toggle="allowAnyVegetableFuel"):
        t.set_setting(SETTINGS_TYPE, {"allowAnyVegetableFuel": False})
        t.set_setting(SETTINGS_TYPE, {"allowAnyVegetableFuel": True})
