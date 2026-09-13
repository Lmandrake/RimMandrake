"""validation.py -- modcheck suite for Jawa Ion Weapons (mandrake.rsw.ionweapons).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run JawaIonWeapons

GROUNDING (read, not guessed):
  - `Source/DamageWorker_IonBuildup.cs` -- the whole three-tier mechanism.
    `ApplyMachineTier` re-issues the hit as vanilla `EMP` at a FLAT amount
    (`empAmountMachine`=60 for true mechanoids/drones, `empAmountDroid`=24 for
    non-flesh non-mechanoid humanlikes) regardless of the incoming bolt's own
    damage amount -- so ONE ion hit is enough to prove the machine/droid
    tiers. Flesh pawns get neither; they accumulate `RSW_JawaIon_Stun`
    severity by hand (`severityPerDamageDealt` 0.03 * damage, divided by
    `BodySizeDivisor(bodySize)` = bodySize^`bodySizeResistExponent`,
    default exponent 2).
  - `Source/StatPart_InverseBodySize.cs` -- `RSW_Jawa_InverseBodySize`
    (StatDefs_JawaIon.xml) is a pure-XML route for THIRD-PARTY stun weapons
    to opt into the same curve; at the default `bodySizeResistExponent`=2 its
    value is exactly `1/BodySize` (remainder exponent = 2-1 = 1).
  - `Source/RSW_JawaIonWeaponsSettings.cs` -- the 9 real toggle/tuning fields,
    every one `public static` (read from everywhere, no Mod instance handy in
    a DamageWorker). ⚠️ Pits' own validation.py already found that
    `rimworld/update_mod_settings` REFUSES a mod whose ModSettings fields are
    static (`Could not resolve field '...' on '...Settings'` -- the bridge's
    reflection walks INSTANCE fields only). This mod's settings are static
    THE SAME WAY, so `t.set_setting` is assumed to fail here too and is not
    used; every component below exercises the SHIPPED DEFAULT value of its
    toggle, never an off-default state. See "Still not proven" below.
  - `Source/VehicleTier/VehicleIonPatches.cs` -- a SEPARATE assembly
    (`JawaIonVehicleTier.dll`) that self-disables via `Log.Warning` if
    Vehicle Framework (`Vehicles.dll`) is not loaded in the AppDomain, at
    static-constructor time (module load, not per-hit). The vehicle tier
    itself needs a live VF vehicle to prove and is out of reach of a
    minimal-mechanism-list environment; see below.
  - `About/About.xml` -- states plainly that `DamageWorker_IonBuildup`
    "contains no Log calls, so it is SILENT whether it works or not -- a
    clean log is not evidence about it either way. Verify from the def dump
    instead." This suite therefore never uses `expect_log_contains` for the
    damage mechanism itself (there is nothing to grep); every mechanism
    component reads back through `jawa/damage`'s own post-mutation state
    (`downed`, `dead`, `stunTicksLeft`, `hitPointsBefore/After` -- these are
    genuine re-reads of `pawn.Downed`/`stunner.StunTicksLeft` AFTER
    `TakeDamage`, not an echo of the request) or a follow-up
    `jawa/list_pawns(includeHealth=True)` / `jawa/thing_stats` call.
  - DEPENDENCIES: this mod hard-depends on `Neronix17.OuterRim.Core`
    (About.xml `<modDependencies>`), so the droid-tier pawn kind
    `OuterRim_BattleDroid` (cited with measured field values in
    `DamageWorker_IonBuildup.cs`'s own 2026-08-12 comment) is assumed
    resolvable in this mod's OWN test environment even though it is absent
    from whatever def dump `rimsage` currently serves (dumps decay/reflect a
    different live mod set -- not evidence this mod's own dependency is
    missing). The shield-break chain additionally needs `Apparel_ShieldBelt`
    (Royalty DLC, vanilla -- confirmed present in the current def dump, but
    NOT a declared dependency of this mod) to be active in the test
    environment; flagged below.

Still not proven / likely first-live-run corrections:
  1. Every toggle is exercised only at its shipped-default value (see
     `t.set_setting` note above). An OFF-state chain for any of the 9
     toggles needs either a bridge fix (read/write instance vs static
     ModSettings fields) or a code change to this mod's settings pattern.
  2. `bodysize_squared_resistance` and `thirdparty_stat_matches_formula`
     assume `Rat`'s and `Pirate`'s `bodySize` differ enough, and that a
     single ion bolt does not push either pawn's `RSW_JawaIon_Stun` severity
     to its `maxSeverity` clamp (1.0) before the ratio can be read -- not
     verified live.
  3. `droid_tier_strong_stun` depends on `OuterRim_BattleDroid` resolving in
     the actual test run's mod list (see DEPENDENCIES above); if the runner's
     minimal-mechanism-list does not carry Outer Rim Core's full droid roster
     this component fails at spawn, which is a real gap to fix (add the
     dependency to the run's mod list), not a bug in the mechanism.
  4. `ion_pops_shield_then_bullet_lands` depends on `Apparel_ShieldBelt`
     (Royalty) being active and on `PawnApparelGenerator`-generated shield
     belts spawning CHARGED (the control hit is what actually proves this,
     rather than assuming it -- but if Royalty is not in the test mod list,
     the whole chain fails at `jawa/pawn_gear` and should read as an
     environment gap, not a mechanism failure).
  5. `vehicle_tier_logs_selfdisable`/`..._multiplier_dormant...` rely on the
     static-constructor warning still being within `jawa/drain_log`'s
     buffer by the time this chain runs (it logs once at mod/assembly load,
     long before any chain's own calls) -- unproven; if this suite runs
     early enough after a fresh load it should still be there, but a large
     `limit` is used defensively rather than relied on being small.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("JawaIonWeapons")
suite.toggles = [
    "fleshBuildupEnabled", "stunBuildupMultiplier", "bodySizeResistExponent",
    "thirdPartyBodySizeScaling", "machineTierEnabled", "machineTierMultiplier",
    "shieldBreakEnabled", "vehicleTierEnabled", "vehicleTierMultiplier",
]

ION_DAMAGE = "RSW_JawaIon_Damage"
ION_STUN_HEDIFF = "RSW_JawaIon_Stun"
INVERSE_BODYSIZE_STAT = "RSW_Jawa_InverseBodySize"
VEHICLE_TIER_LOG_TAG = "Vehicle Framework is not loaded"


# ------------------------------------------------------------------ helpers
# Thin wrappers over `t.bridge_call` (the escape valve): every one still
# performs its own independent READ after a write, per spec -- none trusts a
# mutation's own echoed request as evidence.

def _damage(t, thing_id, damage_def, amount, allow_colonists=False):
    return t.bridge_call("jawa/damage", damageDef=damage_def, amount=amount,
                         thingId=thing_id, allowColonists=allow_colonists) or {}


def _first_row(resp):
    rows = (resp or {}).get("targets") or (resp or {}).get("results") or []
    if not rows:
        raise ExpectationFailed("jawa/damage returned no per-target row -- "
                                "the hit did not land on anything")
    return rows[0]


def _pawn_row(t, pawn_id):
    """Independent read-back: jawa/list_pawns with includeHealth, NEVER the
    damage call's own response, for hediff severity and bodySize."""
    r = t.bridge_call("jawa/list_pawns", includeHealth=True, limit=50)
    for p in (r or {}).get("pawns") or []:
        if p.get("id") == pawn_id:
            return p
    raise ExpectationFailed("%s not found in jawa/list_pawns" % pawn_id)


def _hediff_severity(pawn_row, hediff_def):
    for h in ((pawn_row.get("health") or {}).get("hediffs") or []):
        if h.get("def") == hediff_def:
            return h.get("severity", 0.0)
    return 0.0


def _stat_value(t, thing_id, stat_def):
    r = t.bridge_call("jawa/thing_stats", thing=thing_id, stats=stat_def)
    rows = (r or {}).get("things") or []
    if not rows:
        raise ExpectationFailed("jawa/thing_stats found no thing %r" % thing_id)
    for s in rows[0].get("stats") or []:
        if s.get("defName") == stat_def:
            return s.get("value")
    raise ExpectationFailed("%s not in jawa/thing_stats(%s)" % (stat_def, thing_id))


# --------------------------------------------------------------------- defs
@suite.chain("def_wiring")
def def_wiring(t):
    """No pawns, no map mutation beyond clear_area -- a pure def-field read.
    Confirms the DamageDef fields the whole mechanism depends on actually
    carry the shipped numbers (top-level scalar fields only -- `jawa/get_defs`
    is scalar-only, per `expectations_manifest.py`; nested fields like
    `verbs[0].defaultProjectile` are out of its reach and not checked here)."""
    t.clear_area(size=10)
    with t.component("ion_damagedef_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="DamageDef/%s" % ION_DAMAGE,
                          fields="harmsHealth,makesBlood,empAmountMachine,empAmountDroid")
        rows = (r or {}).get("defs") or []
        if not rows or rows[0].get("found") is False:
            raise ExpectationFailed("DamageDef/%s did not resolve: %r" % (ION_DAMAGE, r))
        fields = rows[0].get("fields") or {}
        bad = []
        if str(fields.get("harmsHealth")).lower() != "false":
            bad.append("harmsHealth=%r (want false)" % fields.get("harmsHealth"))
        if str(fields.get("makesBlood")).lower() != "false":
            bad.append("makesBlood=%r (want false)" % fields.get("makesBlood"))
        try:
            if abs(float(fields.get("empAmountMachine", -1)) - 60.0) > 0.01:
                bad.append("empAmountMachine=%r (want 60)" % fields.get("empAmountMachine"))
            if abs(float(fields.get("empAmountDroid", -1)) - 24.0) > 0.01:
                bad.append("empAmountDroid=%r (want 24)" % fields.get("empAmountDroid"))
        except (TypeError, ValueError):
            bad.append("empAmountMachine/empAmountDroid not numeric: %r" % fields)
        if bad:
            raise ExpectationFailed("RSW_JawaIon_Damage field mismatch: " + "; ".join(bad))
        t.screenshot()


# ------------------------------------------------------------- flesh tier
@suite.chain("flesh_buildup")
def flesh_buildup(t):
    """D1's bottom tier: a flesh pawn takes NO stun and NO injury from ion
    fire, only accumulating RSW_JawaIon_Stun until it collapses alive.
    `harmsHealth=false` means `hitPointsAfter` must never move; `downed`
    coming from the SAME jawa/damage response is a genuine post-hit re-read
    of `pawn.Downed`, not an echo."""
    t.clear_area(size=20)
    raider = t.spawn_pawn("Pirate", hostile=True)

    with t.component("buildup_downs_alive_no_injury", toggle="fleshBuildupEnabled"):
        first = _damage(t, raider, ION_DAMAGE, 8)
        first_row = _first_row(first)
        hp_baseline = first_row.get("hitPointsBefore")
        last_row = first_row
        for _ in range(9):  # ~0.24 severity/hit -> crosses the 0.9 "overloaded" stage
            last_row = _first_row(_damage(t, raider, ION_DAMAGE, 8))
        if last_row.get("hitPointsAfter") != hp_baseline:
            raise ExpectationFailed(
                "flesh pawn lost hit points to a harmsHealth=false damage def: "
                "before=%r after=%r" % (hp_baseline, last_row.get("hitPointsAfter")))
        if not last_row.get("downed"):
            raise ExpectationFailed(
                "flesh pawn never went Downed after 10 ion hits: %r" % last_row)
        if last_row.get("dead"):
            raise ExpectationFailed("flesh pawn DIED -- capture-not-kill violated: %r" % last_row)
        row = _pawn_row(t, raider)
        sev = _hediff_severity(row, ION_STUN_HEDIFF)
        if sev < 0.5:
            raise ExpectationFailed(
                "downed but RSW_JawaIon_Stun severity only %r (expected >= 0.5, "
                "the DROIDWORKS_ION_GUARD_1 floor stage)" % sev)
        t.screenshot()


# --------------------------------------------------------- buildup math
@suite.chain("buildup_math")
def buildup_math(t):
    """Two components that verify the SHAPE of the formula
    `severity = severityPerDamageDealt * damage * stunBuildupMultiplier
                / BodySize ^ bodySizeResistExponent`
    at its shipped defaults (stunBuildupMultiplier=1.0,
    bodySizeResistExponent=2.0), plus the third-party StatDef that composes
    the same curve for other mods' weapons."""
    t.clear_area(size=20)
    human = t.spawn_pawn("Pirate", hostile=True)
    small = t.spawn_pawn("Rat", hostile=True)

    with t.component("default_severity_matches_xml_rate", toggle="stunBuildupMultiplier"):
        _damage(t, human, ION_DAMAGE, 8)
        row = _pawn_row(t, human)
        body_size = row.get("bodySize") or 1.0
        sev = _hediff_severity(row, ION_STUN_HEDIFF)
        # 0.03 severityPerDamageDealt * 8 damage * 1.0 multiplier / bodySize^2
        expected = 0.03 * 8.0 / max(body_size, 0.01) ** 2
        if abs(sev - expected) > max(0.05, expected * 0.35):
            raise ExpectationFailed(
                "one ion hit on a bodySize=%.2f pawn gave severity %.3f, expected "
                "~%.3f from 0.03*8*1.0/bodySize^2" % (body_size, sev, expected))
        t.screenshot()

    with t.component("bodysize_squared_resistance", toggle="bodySizeResistExponent"):
        _damage(t, small, ION_DAMAGE, 8)
        small_row = _pawn_row(t, small)
        small_body = small_row.get("bodySize") or 0.0
        small_sev = _hediff_severity(small_row, ION_STUN_HEDIFF)
        human_row = _pawn_row(t, human)
        human_body = human_row.get("bodySize") or 1.0
        human_sev = _hediff_severity(human_row, ION_STUN_HEDIFF)  # 1 hit already applied above
        if small_body <= 0 or small_body >= human_body:
            raise ExpectationFailed(
                "Rat bodySize %.3f is not smaller than Pirate bodySize %.3f -- "
                "cannot prove the resistance curve with this pair" % (small_body, human_body))
        if human_sev <= 0:
            raise ExpectationFailed("human severity read back as 0 -- nothing to compare against")
        observed_ratio = small_sev / human_sev
        expected_ratio = (human_body / small_body) ** 2
        # Loose band: this is a shape check (smaller body = much more severity
        # per identical hit), not a precision regression test.
        if observed_ratio < expected_ratio * 0.4:
            raise ExpectationFailed(
                "severity ratio %.2fx (rat/human) is far below the ~%.2fx the "
                "bodySize^2 divisor predicts -- resistance curve may not be squared"
                % (observed_ratio, expected_ratio))
        t.screenshot()

    with t.component("thirdparty_stat_matches_formula", toggle="thirdPartyBodySizeScaling"):
        val = _stat_value(t, human, INVERSE_BODYSIZE_STAT)
        body_size = _pawn_row(t, human).get("bodySize") or 1.0
        expected = 1.0 / max(body_size, 0.01)  # remainder exponent = default 2 - 1 = 1
        if val is None or abs(val - expected) > max(0.05, expected * 0.25):
            raise ExpectationFailed(
                "RSW_Jawa_InverseBodySize read %r on a bodySize=%.2f pawn, "
                "expected ~%.3f (1/bodySize at the default exponent)"
                % (val, body_size, expected))


# --------------------------------------------------------- machine/droid
@suite.chain("machine_and_droid_tier")
def machine_and_droid_tier(t):
    """D1's top two tiers. `ApplyMachineTier` re-issues the SAME flat EMP
    amount regardless of the incoming bolt's damage, so one hit each is
    enough: `empAmountMachine`=60 on a true mechanoid should land far more
    stun ticks than `empAmountDroid`=24 on a non-flesh non-mechanoid droid."""
    t.clear_area(size=20)
    mech = t.spawn_pawn("Mech_Scyther", hostile=True)

    with t.component("mechanoid_overloaded_near_instant", toggle="machineTierEnabled"):
        row = _first_row(_damage(t, mech, ION_DAMAGE, 8))
        if row.get("dead"):
            raise ExpectationFailed("Mech_Scyther died from a harmsHealth=false damage def")
        if not row.get("stunTicksLeft") or row["stunTicksLeft"] <= 0:
            raise ExpectationFailed(
                "Mech_Scyther took zero stun ticks from one ion hit -- the machine "
                "tier's EMP re-issue did not fire: %r" % row)
        t.screenshot()

    droid = t.spawn_pawn("OuterRim_BattleDroid", hostile=True)
    with t.component("droid_tier_strong_stun", toggle="machineTierMultiplier"):
        row = _first_row(_damage(t, droid, ION_DAMAGE, 8))
        if row.get("dead"):
            raise ExpectationFailed("OuterRim_BattleDroid died from a harmsHealth=false damage def")
        if not row.get("stunTicksLeft") or row["stunTicksLeft"] <= 0:
            raise ExpectationFailed(
                "OuterRim_BattleDroid took zero stun ticks from one ion hit -- the "
                "droid tier's EMP re-issue did not fire: %r" % row)
        t.screenshot()


# ------------------------------------------------------------ shield break
@suite.chain("shield_break")
def shield_break(t):
    """Proves the popped-shield effect by CONTRAST rather than by reading
    CompShield's internal energy (no bridge tool exposes it): the same
    Bullet hit is absorbed BEFORE the ion hit and lands AFTER it, on the
    same pawn wearing the same belt."""
    t.clear_area(size=20)
    target = t.spawn_pawn("Pirate", hostile=True)
    # `def` is a Python keyword -- unpack a dict rather than pass it as a
    # kwarg, so the literal bridge parameter name reaches the tool call.
    t.bridge_call("jawa/pawn_gear", **{"pawn": target, "action": "wear",
                                       "def": "Apparel_ShieldBelt"})

    with t.component("ion_pops_shield_then_bullet_lands", toggle="shieldBreakEnabled"):
        control = _first_row(_damage(t, target, "Bullet", 15))
        if control.get("hitPointsAfter") != control.get("hitPointsBefore"):
            raise ExpectationFailed(
                "control bullet was NOT absorbed by the shield belt (before=%r "
                "after=%r) -- cannot prove a break without a charged shield first"
                % (control.get("hitPointsBefore"), control.get("hitPointsAfter")))
        _damage(t, target, ION_DAMAGE, 8)
        proof = _first_row(_damage(t, target, "Bullet", 15))
        if proof.get("dead"):
            raise ExpectationFailed("target died from the proof bullet")
        if not (proof.get("hitPointsAfter") < proof.get("hitPointsBefore")):
            raise ExpectationFailed(
                "bullet STILL absorbed after an ion hit -- shieldBreakEnabled's "
                "1-point EMP dispatch did not pop the belt: before=%r after=%r"
                % (proof.get("hitPointsBefore"), proof.get("hitPointsAfter")))
        t.screenshot()


# --------------------------------------------------- vehicle tier (no VF)
@suite.chain("vehicle_tier_without_framework")
def vehicle_tier_without_framework(t):
    """Vehicle Framework is not part of the minimal mechanism list, so the
    actual stun-a-vehicle mechanism (VehicleIonPatches.Postfix) cannot be
    exercised here. What CAN be proven in this environment is the graceful
    self-disable `About.xml` promises: `JawaIonVehicleTierMod`'s static
    constructor logs a warning and returns before patching anything when
    `Vehicles.dll` is absent from the AppDomain. No pawns, no map state."""
    t.clear_area(size=10)
    with t.component("vehicle_tier_logs_selfdisable", toggle="vehicleTierEnabled"):
        t.expect_log_contains(VEHICLE_TIER_LOG_TAG, limit=5000)

    with t.component("vehicle_tier_multiplier_dormant_without_framework",
                     toggle="vehicleTierMultiplier"):
        # Floor-only: with the assembly never patching anything (component
        # above), `vehicleTierMultiplier` cannot move any observable state in
        # THIS environment. Re-reads the same log line as independent
        # evidence that the whole vehicle tier -- multiplier included -- is
        # inert here, rather than asserting nothing at all.
        t.expect_log_contains(VEHICLE_TIER_LOG_TAG, limit=5000)
