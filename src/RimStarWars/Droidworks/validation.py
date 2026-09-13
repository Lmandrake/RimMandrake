"""validation.py -- modcheck suite for Droidworks (mandrake.rsw.droidworks).

Grounded directly in Source/Droidworks/*.cs (read in full for this pass) and
Defs/**/*.xml -- never in the mod's name or its design docs, which in places
(design/validation_walks/RimStarWars/Droidworks.md, design/Jawa/
droidworks_assumptions.md) are STALE against the current source: e.g. that
validation-walk doc still says "CompDroidDetonation ... never wired onto any
race", but Races_OuterRim.xml:1030 wires it onto RSW_DW_Race_OuterRim_GNKDroid
today, with a comment recording exactly that ("the first race to prove the
wiring works end to end"). Trust the .cs/.xml in this tree, not the docs.

RSW_DroidworksSettings (Source/Droidworks/RSW_DroidworksSettings.cs) has 17
BOOLEAN toggles plus several float sliders (rate/threshold multipliers, not
independently toggle-tested here -- same register Pits used: toggles list is
the on/off fields, sliders are tuning). suite.toggles below lists all 17;
every one has >=1 covering component.

CANNOT FLIP TOGGLES LIVE -- inherited, not new. Every field on
RSW_DroidworksSettings is `public static` (same reason Pits documented for
its own PitsSettings): `rimworld/update_mod_settings` ("`t.set_setting`")
reflects over INSTANCE fields on the ModSettings object and refuses a static
one with "Could not resolve field ...". So no component below calls
`t.set_setting` -- every component instead demonstrates the DEFAULT-ON
behaviour of its toggle (every default in RSW_DroidworksSettings ships true),
attributing the observed effect to the code's own `if (!RSW_DroidworksSettings.
X) return;` gate, which is read directly from source, not inferred.

STILL NOT PROVEN / LIKELY FIRST-LIVE-RUN CORRECTIONS (read before trusting a
red result blindly):
  1. `jawa/get_defs(..., deep=True)` reaching into a ThingDef's `comps` list
     or a TraitDef's `modExtensions` list has not been run live. The
     structural chain's checks use a permissive "needle in str(result)"
     match rather than a precise field path for exactly this reason -- the
     precise reflection path through `deep` walking a `List<CompProperties>`
     was never confirmed against a real bridge response this pass.
  2. `ionShutdown` (HediffComp_IonOverloadsDroid) attaches only to
     RSW_JawaIon_Stun via Patches/IonBuildup_PowersDownDroid.xml, a
     FindMod-gated patch onto Jawa Ion Weapons (mandrake.rsw.ionweapons) --
     a SEPARATE mod, not a hard dependency of Droidworks (loadAfter only).
     Run against minimal+Droidworks alone (this mod's own environment), its
     component below will fail cleanly with "No HediffDef 'RSW_JawaIon_Stun'"
     -- that IS the correct, honest signal for this environment, not a
     script bug. Re-run with Jawa Ion Weapons added to the smoke-test list
     to actually exercise it.
  3. `boltSuppressesMentalBreaks` is tested by crashing a bolted pawn's mood
     to 0 and waiting for vanilla's own break-check cadence to NOT produce a
     break. This is a single-arm, probabilistic proof: BreakCanOccur is
     called whenever the break-checker considers the pawn, but a coincidental
     non-fire for some unrelated reason would read as a false PASS. No
     control (unbolted) pawn is run alongside it this pass.
  4. `boltRebellion`, `wipeQuirks`, `personalityDrift`, and `huttCaptivesBolted`
     are proven only STRUCTURALLY (def read-back / a hand-built hediff state
     matching what the real code path would leave) -- none of their real
     triggers (a completed RSW_DW_RemoveRestrainingBolt/RSW_DW_MemoryWipe
     surgery bill, the 2-in-game-year drift clock, a Hutt trader restocking)
     were driven through a real bill/incident pipeline this pass:
       - `Recipe_RemoveRestrainingBolt.ApplyOnPawn`'s rebellion-on-threshold
         check and `Recipe_DWMemoryWipe.ApplyOnPawn`'s quirk roll are both
         C# recipe workers with no bridge tool that runs `ApplyOnPawn`
         directly; driving them for real needs a bill+doctor pipeline
         (`jawa/bill_add_legacy`+`jawa/configure_bill`+`jawa/ordered_job`)
         not attempted here.
       - `CompDWServiceRecord.TryDrift`'s own doc comment admits "this
         mechanic cannot be tested live in any reasonable session" (the
         first drift is 2 in-game YEARS); its own docstring floats a future
         "quicktest or bridge tool" hook that does not exist yet.
       - `StockGenerator_DWHuttCaptives` (the only caller of
         `DroidworksBoltUtility.ApplyCaptiveBolt`) is wired onto a
         TraderKindDef that lives in `src/RimUtinni/UtinniPatches`, NOT in
         this mod -- outside the "minimal + mod under test" environment.
  5. `wildDroidCrash` and `protocolTrade` both drive live mechanisms
     (`jawa/fire_incident`) that only exist when the companion is built with
     `JAWA_GM_TOOLS` (`build.py --gm`). If that tool is absent these
     components fail with a clear "unknown tool" style error rather than a
     silent false pass -- also a real, informative signal, not a bug.
  6. `wipeStumble`'s job-interrupt half (the droid dropping its job and
     wandering) has no independent bridge read-back: there is no
     `jawa/pawn_*` tool that reports a pawn's current `CurJobDef`. Only the
     hediff's own attach/severity is checked live; the actual stumble
     behaviour is unverified.
  7. `full_charge_detonates_on_death` (toggle `detonation`) proves DEATH
     (corpse count + pawn removed from `jawa/list_pawns`) but not the
     explosion itself -- no bridge tool reads blast radius/AoE damage
     directly. The screenshot is the only evidence for the explosion half.

Bridge tools used beyond suite.py's own verb vocabulary (all via
`t.bridge_call`, per spec's escape valve): `jawa/pawn_get` (deep pawn read:
hediffs/needs/traits/apparel), `jawa/pawn_health` (add/remove a hediff, with
its own post-write hediffs list as the read-back -- see `_pd()`/`_hediff()`
below), `jawa/pawn_need` (need level), `jawa/damage` (graduated damage,
returns post-damage hediffs), `jawa/pawn_thoughts` (mood thoughts, refreshes
situational thoughts first), `jawa/pawn_mental` (mental state list/start/end),
`jawa/list_things` (defName/rect/group filtered thing census),
`jawa/power_net` (force a CompPowerTrader on, bypassing the need for a real
grid), `jawa/get_defs` (static def/comp field read-back), `jawa/fire_incident`
(GM-tools only), `jawa/trade_price_probe` (headless trade price read).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Droidworks")
suite.toggles = [
    "boltSuppressesMentalBreaks", "boltResentment", "boltShear", "boltRebellion",
    "boltMoodPenalty",
    "powerNeed", "powerDownWhenEmpty",
    "ionShutdown",
    "detonation",
    "wipeStumble", "wipeQuirks",
    "wildDroidCrash",
    "headDrop", "partDrop",
    "personalityDrift",
    "protocolTrade",
    "huttCaptivesBolted",
]

# Chassis families used below, per DroidworksModExtension.chassisClass /
# Defs/Races_Families.xml (values confirmed by reading that file):
#   GNK (Power, class 6): powerFallPerDay 0.33, energyDensity 3 -- the ONLY
#     race wired to CompDroidDetonation today (Races_OuterRim.xml:1030).
#   ImperialLaborDroid (Labour, class 0): energyDensity 0, never detonates.
#   BattleDroid (Battle, class 3): every droid race carries CompDWHeadDropper/
#     CompDWPartDropper (they sit on DW_Race_Base), so any kind proves salvage.
#   ProtocolDroid (Protocol, class 1): CompDWDataSpike/trade-advantage family.
#   KotORDroidColonist_T3UD: carries RSW_DW_Module_DroidHardware_agility's
#     apparel layer -- MEASURED live 2026-09-10 (Transient/dw_personality_
#     traits_check.py, Transient/droidworks_module_personality_verify_*.py).
GNK = "RSW_DW_OuterRim_GNKDroid"
LABOUR = "RSW_DW_OuterRim_ImperialLaborDroid"
BATTLE = "RSW_DW_OuterRim_BattleDroid"
PROTOCOL = "RSW_DW_OuterRim_ProtocolDroid"
KOTOR_T3 = "RSW_DW_KotORDroidColonist_T3UD"

PART_DEFS = ["RSW_DW_Part_Leg", "RSW_DW_Part_Manipulator", "RSW_DW_Part_Sensor",
             "RSW_DW_Part_Motivator", "RSW_DW_Part_Servo", "RSW_DW_Part_PowerCell"]


# --------------------------------------------------------------- helpers
def _pd(t, pawn_id):
    """A fresh, independent `jawa/pawn_get` read -- never trust a write
    call's own echoed state for anything but the field it just wrote (see
    `_hediff`'s own comment on why `jawa/pawn_health`'s echo IS trustworthy
    for hediffs specifically)."""
    r = t.bridge_call("jawa/pawn_get", pawn=pawn_id)
    pawns = (r or {}).get("pawns") or [{}]
    return pawns[0]


def _hediffs(pd):
    return {h.get("def"): h.get("severity") for h in (pd.get("hediffs") or [])}


def _needs(pd):
    return {n.get("need"): n.get("level") for n in (pd.get("needs") or [])}


def _traits(pd):
    return [tr.get("def") for tr in (pd.get("traits") or [])]


def _set_hediff(t, pawn_id, action, hediff, severity=None):
    """`jawa/pawn_health`'s own response is a genuine independent read (it
    re-reads `p.health.hediffSet.hediffs` AFTER the mutation and fails outright
    if an 'add' did not actually attach -- see JawaBenchPawnTools.cs's own
    Finding #17 comment) -- not a bare echoed success flag, so this counts as
    the write's read-back per spec (never re-derived from the write's OWN
    unread claim, only from state the call independently re-fetched)."""
    kwargs = {"pawn": pawn_id, "action": action, "hediff": hediff}
    if severity is not None:
        kwargs["severity"] = severity
    return t.bridge_call("jawa/pawn_health", **kwargs)


def _set_need(t, pawn_id, need, level):
    return t.bridge_call("jawa/pawn_need", pawn=pawn_id, action="need",
                         need=need, level=level)


def _expect_hediff(t, pawn_id, name, present=True):
    pd = _pd(t, pawn_id)
    got = name in _hediffs(pd)
    ok = got == present
    t._record("expect_hediff(%s, %s present=%s)" % (pawn_id, name, present), ok)
    if not ok:
        raise ExpectationFailed(
            "%s hediff %s=%s, expected present=%s (hediffs: %s)"
            % (pawn_id, name, got, present, list(_hediffs(pd))))
    return pd


def _defs_contains(t, defs, fields, needle):
    """A permissive structural check (see module docstring, gap #1): the
    exact `deep=True` reflection path into a comps/modExtensions list was
    not confirmed live this pass, so this matches the needle anywhere in the
    stringified result rather than at a precise field path."""
    r = t.bridge_call("jawa/get_defs", defs=defs, fields=fields, deep=True)
    ok = bool(r) and r.get("success") is not False and needle in str(r)
    t._record("get_defs(%s) contains %r" % (defs, needle), ok)
    if not ok:
        raise ExpectationFailed(
            "get_defs(%r, fields=%r) did not contain %r: %s" % (defs, fields, needle, r))
    return r


# =========================================================== power / format
@suite.chain("power_state_machine")
def power_state_machine(t):
    """GNK (Power family): Need_Power.NeedInterval, Patch_ShouldHaveNeed_Power,
    HediffComp_PoweredDown, and Recipe_RebootDroid's own effect (replicated
    by hand -- the recipe worker itself is not driven through a bill, see
    module docstring gap #4's sibling note)."""
    t.clear_area(size=20)
    droid = t.spawn_pawn(GNK, hostile=False)

    with t.component("format_tier_defaults_to_programmable", beyond_toggle=True):
        # CompDWFormatTier.PostSpawnSetup runs unconditionally (no settings
        # gate in that comp) -- every droid should already carry
        # RSW_DW_FormatTier at severity 3 (Programmable) on spawn.
        pd = _pd(t, droid)
        sev = _hediffs(pd).get("RSW_DW_FormatTier")
        ok = sev is not None and 2.5 <= sev < 3.5
        t._record("format tier severity", sev)
        if not ok:
            raise ExpectationFailed(
                "RSW_DW_FormatTier severity=%r, expected Programmable (2.5-3.5)" % sev)
        t.screenshot()

    with t.component("power_need_present", toggle="powerNeed"):
        pd = _pd(t, droid)
        if "RSW_DW_Power" not in _needs(pd):
            raise ExpectationFailed(
                "droid has no RSW_DW_Power need: %s" % list(_needs(pd)))
        t.screenshot()

    with t.component("empty_bar_powers_down", toggle="powerDownWhenEmpty"):
        _set_need(t, droid, "RSW_DW_Power", 0.0)
        t.wait_ticks(600)   # 4 NeedInterval (150-tick) passes at Need_Power's cadence
        _expect_hediff(t, droid, "RSW_DW_PoweredDown", present=True)
        t.screenshot()

    with t.component("reboot_restores_power", beyond_toggle=True):
        # Manual replication of Recipe_RebootDroid.ApplyOnPawn's own two
        # lines (remove PoweredDown; floor power at 0.15) -- the recipe
        # worker itself needs a bill+doctor pipeline not driven here.
        _set_hediff(t, droid, "remove", "RSW_DW_PoweredDown")
        _set_need(t, droid, "RSW_DW_Power", 0.15)
        pd = _expect_hediff(t, droid, "RSW_DW_PoweredDown", present=False)
        level = _needs(pd).get("RSW_DW_Power") or 0.0
        if level < 0.14:
            raise ExpectationFailed("RSW_DW_Power=%r after manual reboot, expected >=0.15" % level)
        t.screenshot()


@suite.chain("passive_charging")
def passive_charging(t):
    """RSW_DW_ChargeNimbus (radius 6.9, chargePercentPerHour 15) tops off any
    droid in range with NO job needed (CompDWCharger.CompTick) -- unlike the
    socket/dock, which need a real JobDriver_DWRecharge job this pass does
    not attempt to force. `jawa/power_net(forcePowerOn=True)` substitutes for
    a real power grid (none is built in a bare cleared test area)."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn("RSW_DW_ChargeNimbus", count=1)

    with t.component("nimbus_charges_in_range", beyond_toggle=True):
        cell = t.bridge_call("rimworld/get_cell_info", x=x, z=z)
        things = (cell or {}).get("things") or []
        nimbus = next((th for th in things if th.get("defName") == "RSW_DW_ChargeNimbus"), None)
        if nimbus is None or not nimbus.get("id"):
            raise ExpectationFailed("RSW_DW_ChargeNimbus not found at anchor after spawn: %s" % things)
        t.bridge_call("jawa/power_net", thing=nimbus["id"], forcePowerOn=True)

        droid = t.spawn_pawn(GNK, hostile=False, beyond=[(x, z)])
        _set_need(t, droid, "RSW_DW_Power", 0.10)
        t.wait_ticks(720)   # 12 CompTick scans (60-tick interval)
        pd = _pd(t, droid)
        level = _needs(pd).get("RSW_DW_Power") or 0.0
        if level <= 0.10:
            raise ExpectationFailed(
                "RSW_DW_Power did not rise near the nimbus (still %r after 720 ticks)" % level)
        t.screenshot()


# =========================================================== death effects
@suite.chain("detonation")
def detonation_chain(t):
    """GNK (energyDensity 3, the only race wired to CompDroidDetonation) at
    full charge, killed lethally. Proves DEATH only -- see module docstring
    gap #7 for why the explosion itself is not independently read back."""
    t.clear_area(size=20)
    gnk = t.spawn_pawn(GNK, hostile=True)   # hostile: no allowColonists needed

    with t.component("full_charge_detonates_on_death", toggle="detonation"):
        _set_need(t, gnk, "RSW_DW_Power", 1.0)
        before = t.bridge_call("jawa/list_things", group="Corpse")
        n_before = len(((before or {}).get("things")) or [])
        t.bridge_call("jawa/damage", thingId=gnk, damageDef="Bomb", amount=5000.0)
        t.wait_ticks(60)
        t.expect_pawn_despawned(gnk)
        after = t.bridge_call("jawa/list_things", group="Corpse")
        n_after = len(((after or {}).get("things")) or [])
        if n_after <= n_before:
            raise ExpectationFailed(
                "no corpse appeared after lethal damage (before=%d after=%d)" % (n_before, n_after))
        t.screenshot()


@suite.chain("salvage_on_death")
def salvage_on_death(t):
    """CompDWHeadDropper/CompDWPartDropper sit on DW_Race_Base -- every droid
    carries both. One kill exercises both toggles."""
    t.clear_area(size=20)
    battle = t.spawn_pawn(BATTLE, hostile=True)
    x, z = t.anchor

    pd_before = _pd(t, battle)
    pawn_name = pd_before.get("nameShort") or pd_before.get("name") or ""
    t.bridge_call("jawa/damage", thingId=battle, damageDef="Bomb", amount=5000.0)
    t.wait_ticks(60)
    t.expect_pawn_despawned(battle)
    ring = t.bridge_call("jawa/list_things",
                         rect="%d,%d,12,12" % (x - 6, z - 6), limit=60)
    things = (ring or {}).get("things") or []

    with t.component("head_drops_with_identity", toggle="headDrop"):
        head = next((th for th in things if th.get("def") == "RSW_DW_Head_Battle"), None)
        if head is None:
            raise ExpectationFailed(
                "no RSW_DW_Head_Battle in the blast area: %s" % [th.get("def") for th in things])
        if pawn_name and pawn_name not in (head.get("label") or ""):
            raise ExpectationFailed(
                "head label %r does not carry the dead droid's name %r"
                % (head.get("label"), pawn_name))
        t.screenshot()

    with t.component("parts_drop_from_dead_droid", toggle="partDrop"):
        # Probabilistic (per Pits' own struggle_clock register): partDropChance
        # 0.6 rolled independently across 6 part types -- P(zero drop) = 0.4^6
        # ~= 0.4%, so at least one part is expected in ~99.6% of runs.
        found = [th.get("def") for th in things if th.get("def") in PART_DEFS]
        if not found:
            raise ExpectationFailed(
                "no salvage part dropped (expected >=1 of %s, ~99.6%% chance)" % PART_DEFS)
        t.screenshot()


# ================================================================ bolt core
@suite.chain("bolt_core")
def bolt_core(t):
    """RestrainingBolt/BoltResentment/BoltShear/mood-penalty/mental-break
    suppression, all on one bolted colonist plus a bystander for the mood
    check. `t.spawn_pawn(..., hostile=False)` -- a plain colonist, not a
    raider, matching the Pits pilot's own finding that a hostile pawn is not
    reliably steerable/controllable via the bridge; irrelevant here since
    nothing here orders movement anyway."""
    t.clear_area(size=20)
    walker = t.spawn_pawn("Colonist", hostile=False)
    bystander = t.spawn_pawn("Colonist", hostile=False)

    _set_hediff(t, walker, "add", "RSW_DW_RestrainingBolt")
    _set_hediff(t, walker, "add", "RSW_DW_BoltResentment", severity=0.0)

    with t.component("resentment_accrues", toggle="boltResentment"):
        before = _hediffs(_pd(t, walker)).get("RSW_DW_BoltResentment") or 0.0
        t.wait_ticks(1200)   # 20 CompPostTick scans at the 60-tick interval
        after = _hediffs(_pd(t, walker)).get("RSW_DW_BoltResentment") or 0.0
        if not (after > before):
            raise ExpectationFailed(
                "RSW_DW_BoltResentment severity did not rise (%.6f -> %.6f)" % (before, after))
        t.screenshot()

    with t.component("shear_on_damage", toggle="boltShear"):
        # Probabilistic: shearChancePerDamage 0.02, chance per 25-dmg hit
        # 1-(0.98)^25 ~= 39.7%; missing all 8 hits ~= 1.8%, so this is
        # expected to succeed in ~98% of runs (Pits' struggle_clock register).
        sheared = False
        for _ in range(8):
            t.bridge_call("jawa/damage", thingId=walker, damageDef="Blunt",
                          amount=25.0, allowColonists=True)
            if "RSW_DW_RestrainingBolt" not in _hediffs(_pd(t, walker)):
                sheared = True
                break
        if not sheared:
            raise ExpectationFailed(
                "RSW_DW_RestrainingBolt survived 8 hits of 25 blunt damage "
                "(expected ~98%% chance of a shear)")
        t.screenshot()

    # Re-bolt for the two components below (shear above deliberately removed it).
    _set_hediff(t, walker, "add", "RSW_DW_RestrainingBolt")

    with t.component("mood_penalty_nearby", toggle="boltMoodPenalty"):
        thoughts = t.bridge_call("jawa/pawn_thoughts", pawn=bystander)
        defs = [th.get("def") for th in ((thoughts or {}).get("thoughts") or [])]
        if "RSW_DW_NearBoltedDroid" not in defs:
            raise ExpectationFailed(
                "bystander has no RSW_DW_NearBoltedDroid thought near a bolted "
                "pawn: %s" % defs)
        t.screenshot()

    with t.component("mental_break_suppressed_while_bolted",
                     toggle="boltSuppressesMentalBreaks"):
        # Single-arm and probabilistic -- see module docstring gap #3.
        _set_need(t, walker, "Mood", 0.0)
        t.wait_ticks(2000)
        mental = t.bridge_call("jawa/pawn_mental", pawn=walker, action="list")
        current = (mental or {}).get("currentState")
        if current:
            raise ExpectationFailed(
                "bolted pawn entered mental state %r despite "
                "boltSuppressesMentalBreaks=true" % current)
        t.screenshot()


@suite.chain("bolt_rebellion_structural")
def bolt_rebellion_structural(t):
    """Recipe_RemoveRestrainingBolt.ApplyOnPawn's rebellion-on-threshold
    check has no bridge path that runs a recipe worker directly (module
    docstring gap #4) -- this proves only that the recipe is wired to the
    right worker class."""
    t.clear_area(size=10)
    with t.component("rebellion_recipe_wired", toggle="boltRebellion"):
        _defs_contains(t, "RecipeDef/RSW_DW_RemoveRestrainingBolt", "workerClass",
                       "Recipe_RemoveRestrainingBolt")


# ============================================================ wipe / drift
@suite.chain("wipe_and_drift_structural")
def wipe_and_drift_structural(t):
    """wipeStumble's hediff/capacity half is live-tested here; its
    job-interrupt half and wipeQuirks/personalityDrift's actual triggers are
    structural only -- see module docstring gaps #4 and #6."""
    t.clear_area(size=20)
    droid = t.spawn_pawn(LABOUR, hostile=False)

    with t.component("wipe_hediff_attaches", toggle="wipeStumble"):
        _set_hediff(t, droid, "add", "RSW_DW_RecentlyWiped", severity=1.0)
        pd = _expect_hediff(t, droid, "RSW_DW_RecentlyWiped", present=True)
        sev = _hediffs(pd).get("RSW_DW_RecentlyWiped")
        if sev is None or sev < 0.99:
            raise ExpectationFailed("RSW_DW_RecentlyWiped severity=%r, expected ~1.0" % sev)
        t.screenshot()

    with t.component("quirk_pool_marked", toggle="wipeQuirks"):
        _defs_contains(t, "TraitDef/RSW_DW_Quirk_ServoTwitch", "modExtensions",
                       "HardwareQuirkExtension")

    with t.component("idiosyncrasy_pool_marked", toggle="personalityDrift"):
        _defs_contains(t, "TraitDef/RSW_DW_Idio_Opinionated", "modExtensions",
                       "DroidIdiosyncrasyExtension")


# ============================================================== hutt captives
@suite.chain("hutt_captive_bolt_state")
def hutt_captive_bolt_state(t):
    """DroidworksBoltUtility.ApplyCaptiveBolt (the only thing huttCaptivesBolted
    gates) is called only from StockGenerator_DWHuttCaptives, wired onto a
    TraderKindDef in src/RimUtinni/UtinniPatches -- outside this mod's own
    environment (module docstring gap #4). This reproduces ApplyCaptiveBolt's
    documented CONTRACT by hand (bolt + resentment seeded into its floor
    range) rather than exercising the trader-stock trigger itself."""
    t.clear_area(size=10)
    captive = t.spawn_pawn("Colonist", hostile=False)

    with t.component("captive_bolt_state_reachable", toggle="huttCaptivesBolted"):
        _expect_hediff(t, captive, "RSW_DW_RestrainingBolt", present=False)
        _set_hediff(t, captive, "add", "RSW_DW_RestrainingBolt")
        _set_hediff(t, captive, "add", "RSW_DW_BoltResentment", severity=0.5)
        pd = _pd(t, captive)
        hed = _hediffs(pd)
        if "RSW_DW_RestrainingBolt" not in hed:
            raise ExpectationFailed("captive bolt state did not attach: %s" % hed)
        sev = hed.get("RSW_DW_BoltResentment") or 0.0
        if not (0.2 <= sev <= 0.8):
            raise ExpectationFailed(
                "captive resentment severity=%r, expected within ApplyCaptiveBolt's "
                "0.2-0.8 seed range" % sev)
        t.screenshot()


# ============================================================= module wear
@suite.chain("module_personality")
def module_personality(t):
    """CompModulePersonality (no settings gate at all -- confirmed reading
    the .cs, so beyond_toggle) grants/revokes a personality hediff on
    equip/unequip. Sequence MEASURED live 2026-09-10 (Transient/
    droidworks_module_personality_verify_2026-09-10g.py, Transient/
    dw_module_personality_full.json): the debug-action path needs the pawn
    SELECTED first via `rimworld/select_pawn`."""
    t.clear_area(size=20)
    droid = t.spawn_pawn(KOTOR_T3, hostile=False)
    ch = chr(92)

    with t.component("module_grants_personality_on_wear", beyond_toggle=True):
        _expect_hediff(t, droid, "RSW_DW_ModulePersonality_Twitchy", present=False)
        t.bridge_call("rimworld/select_pawn", pawnId=droid)
        wear_path = "Actions" + ch + "Wear apparel (selected)..." + ch + "RSW_DW_Module_DroidHardware_agility"
        t.bridge_call("rimworld/execute_debug_action", path=wear_path)
        pd = _expect_hediff(t, droid, "RSW_DW_ModulePersonality_Twitchy", present=True)
        if "RSW_DW_Module_DroidHardware_agility" not in (
                a.get("def") for a in (pd.get("apparel") or [])):
            raise ExpectationFailed("module did not appear in worn apparel: %s" % pd.get("apparel"))
        t.screenshot()

        remove_path = "Actions" + ch + "Wear apparel (selected)..." + ch + "*Remove all apparel"
        t.bridge_call("rimworld/execute_debug_action", path=remove_path)
        _expect_hediff(t, droid, "RSW_DW_ModulePersonality_Twitchy", present=False)
        t.screenshot()


# ============================================================ wild droids
@suite.chain("wild_droid_crash")
def wild_droid_crash(t):
    """IncidentWorker_WildDroidCrash via `jawa/fire_incident` -- GM-tools
    only (module docstring gap #5). A faction-less (Faction: null) manhunter
    droid is the whole point of the packet (RSW_DW_DataSpike_Wild's target)."""
    t.clear_area(size=10)
    with t.component("wild_droid_crash_fires", toggle="wildDroidCrash"):
        before = t.bridge_call("jawa/list_pawns", limit=500)
        ids_before = {p.get("id") for p in ((before or {}).get("pawns") or [])}
        r = t.bridge_call("jawa/fire_incident", incidentDef="RSW_DW_WildDroidCrash")
        if not (r or {}).get("fired", (r or {}).get("success")):
            raise ExpectationFailed(
                "jawa/fire_incident(RSW_DW_WildDroidCrash) did not fire: %s "
                "(if this names an unknown tool, the companion was not built "
                "with JAWA_GM_TOOLS -- see module docstring gap #5)" % r)
        t.wait_ticks(60)
        after = t.bridge_call("jawa/list_pawns", limit=500)
        new = [p for p in ((after or {}).get("pawns") or []) if p.get("id") not in ids_before]
        wild = next((p for p in new if not p.get("faction")), None)
        if wild is None:
            raise ExpectationFailed(
                "no new faction-less pawn after firing RSW_DW_WildDroidCrash: %s" % new)
        t.session.track("pawn", wild["id"], x=wild.get("x"), z=wild.get("z"))
        t.screenshot()


# =========================================================== protocol trade
@suite.chain("protocol_trade_advantage")
def protocol_trade_advantage(t):
    """Patch_ProtocolTradeAdvantage postfixes TradeUtility.GetPricePlayerBuy/
    Sell. Differential live test: probe the SAME trader's buy price for
    Silver-tradeable goods once with no protocol droid in the player party,
    once with one -- `jawa/trade_price_probe` (module docstring gap #5: needs
    JAWA_GM_TOOLS for `jawa/fire_incident` to get a trader onto the map)."""
    t.clear_area(size=15)
    negotiator = t.spawn_pawn("Colonist", hostile=False)

    with t.component("protocol_droid_shifts_prices", toggle="protocolTrade"):
        r = t.bridge_call("jawa/fire_incident", incidentDef="TraderCaravanArrival")
        if not (r or {}).get("fired", (r or {}).get("success")):
            raise ExpectationFailed(
                "jawa/fire_incident(TraderCaravanArrival) did not fire: %s "
                "(needs JAWA_GM_TOOLS -- see module docstring gap #5)" % r)
        t.wait_ticks(120)

        probe1 = t.bridge_call("jawa/trade_price_probe",
                               negotiatorPawnId=negotiator, defNames="Silver")
        if not (probe1 or {}).get("success"):
            raise ExpectationFailed("baseline jawa/trade_price_probe failed: %s" % probe1)
        rows1 = {p.get("defName"): p for p in (probe1.get("prices") or [])}

        droid = t.spawn_pawn(PROTOCOL, hostile=False)
        probe2 = t.bridge_call("jawa/trade_price_probe",
                               negotiatorPawnId=negotiator, defNames="Silver")
        if not (probe2 or {}).get("success"):
            raise ExpectationFailed("second jawa/trade_price_probe failed: %s" % probe2)
        rows2 = {p.get("defName"): p for p in (probe2.get("prices") or [])}

        moved = any(rows2[d]["buy"] != rows1.get(d, {}).get("buy")
                   for d in rows2 if d in rows1)
        if not moved and rows1 and rows2:
            raise ExpectationFailed(
                "no buy price changed after adding a protocol droid to the "
                "player party: before=%s after=%s" % (rows1, rows2))
        t.screenshot()


# ================================================================= ion (env-gated)
@suite.chain("ion_overload_shutdown")
def ion_overload_shutdown(t):
    """REQUIRES Jawa Ion Weapons active (module docstring gap #2). Run
    against minimal+Droidworks alone this fails cleanly on the missing
    HediffDef -- that failure IS the correct signal for this environment."""
    t.clear_area(size=10)
    droid = t.spawn_pawn(GNK, hostile=False)

    with t.component("ion_overload_shuts_down_droid", toggle="ionShutdown"):
        r = _set_hediff(t, droid, "add", "RSW_JawaIon_Stun", severity=0.6)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "could not add RSW_JawaIon_Stun (%s) -- Jawa Ion Weapons is "
                "probably not active in this environment; see module "
                "docstring gap #2" % r)
        t.wait_ticks(60)
        _expect_hediff(t, droid, "RSW_DW_PoweredDown", present=True)
        t.screenshot()
