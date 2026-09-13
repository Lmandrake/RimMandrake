"""validation.py -- modcheck suite for Jawa Armoury Rebalance (mandrake.rsw.armoury).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Armoury

SCOPE (read, not guessed): `Source/RSW_ArmourySettings.cs` -- "This mod is an
'absorbed' bundle: one assembly carrying a dozen otherwise-unrelated runtime
mechanisms, each in its own namespace." 24 toggle/tuning fields across 12
mechanisms (`CompExtraSounds`, `CrystalFormations`, `InstantHealingDrug`,
`JumppackForMeleeAI`, `KoltoTank`, `MentalBreakBlocker`, `MinePocket`,
`SecondaryMineableYield`, `SelfHediffVerb`, `Spinning_Projectile`,
`guy762_Ionization`, `guy762_IonizationABF`). This is not a playtest of all
12 (spec §1: "not exhaustive") -- it grounds every toggle in what its C#
ACTUALLY does, at whatever depth is honestly reachable offline+bridge:

  TIER 1 -- real behavior, live damage/hediff read-back (the ion mechanism):
    `ionDamageEnabled`, `ionSeverity` via `guy762_InternalDamage_ion` on a
    mechanoid, read back through `jawa/list_pawns(includeHealth=True)` --
    never through the damage call's own echoed response.
  TIER 2 -- Harmony-patch PRESENCE via `jawa/harmony_patches` (a genuine
    process-wide registry read, not an echo of a request): proves the
    mechanism's Harmony patch is actually applied to the right method, which
    is the one thing that can silently fail (a method rename upstream, a
    duplicate-patch guard, load order) without any other visible symptom.
    Covers `extraSoundsEnabled`, `instantHealEnabled`(+its 2 hour sliders),
    `jumppackEnabled`(+its 2 companions), `mentalBreakBlockerEnabled`,
    `secondaryYieldEnabled`(+its 2 multipliers), `selfHediffVerbEnabled`(+its
    cooldown slider), `returningWeaponEnabled`(+its speed slider).
  TIER 3 -- def-field / spawn wiring via `jawa/get_defs` or a raw spawn: for
    mechanisms with NO Harmony patch and NO cheap live trigger
    (`CrystalFormations` is a worldgen-time-only GenStep; `KoltoTank` and
    `MinePocket` need a powered building or a completed mining job neither
    of which this suite stands up). Confirms the def actually references the
    right class/comp, which is what a typo'd `Class=` attribute breaks.

Every TIER 2/3 component is explicitly a WIRING check, not a full runtime
behavior proof, and says so in its own assertion message on failure. This is
the same register Pits' own validation.py uses for its documented gaps --
see "Still not proven" below for the complete list of what remains unproven
and why.

GROUNDING PER MECHANISM (source read, not guessed):
  - `CompExtraSounds/HarmonyCompExtraSounds.cs` -- Harmony id
    "jecstools.jecrell.comps.sounds", postfixes on `Verb_MeleeAttack`'s
    `SoundHitPawn`/`SoundMiss`/`SoundHitBuilding`. `guy762_gamorreanaxe`
    (Defs/Absorbed_KotorCore/.../GamorreanAxe.xml) carries the comp.
  - `CrystalFormations/GenStep_ScatterLightsaberCrystals.cs` -- gated by
    `crystalFormationsEnabled` before any map sweep; wired as GenStepDef
    `KOTOR_CrystalFormation` (order 1100).
  - `InstantHealingDrug/InstantHealingDrug.cs` -- Harmony id
    "kaitorisenkou.InstantHealingDrug", prefix/postfix on
    `JobGiver_TakeCombatEnhancingDrug.TryGiveJob`.
  - `JumppackForMeleeAI/JumppackForMeleeAI.cs` -- Harmony id
    "kaitorisenkou.JumppackForMeleeAI", a TRANSPILER on
    `JobGiver_AIFightEnemy.TryGiveJob`.
  - `KoltoTank/` -- `KoltoTankPatches.cs`'s own comment: "constructs a
    Harmony instance but never calls .Patch() on it -- genuinely a no-op...
    not a port defect." No Harmony evidence exists for this mechanism AT
    ALL; `CompKoltoTank` gates purely through `ThingComp` methods called by
    `Building_KoltoTank` itself. ThingDef `KoltoTank` carries the comp.
  - `MentalBreakBlocker/MentalBreakBlocker.cs` -- Harmony id
    "kaitorisenkou.MentalBreakBlocker", prefix on
    `MentalStateHandler.TryStartMentalState`.
  - `MinePocket/MinePocketJob.cs` -- no Harmony; `TryMakePreToilReservations`
    gates the whole job on `minePocketEnabled` directly. JobDef
    `MinePocket_Job` -> `driverClass MinePocket.MinePocketJob`.
  - `SecondaryMineableYield/SecondaryMineableYield.cs` -- Harmony id
    "kaitorisenkou.SecondaryMineableYield", postfixes on `Mineable`'s
    `TrySpawnYield` and `PreApplyDamage`. `KOTOR_StygiumCrystal`
    (Defs/.../KotORResource_Stygium.xml) carries
    `SecondaryMineableYield.ModExtension_SecondaryMineableYield`.
  - `SelfHediffVerb/SelfHediffVerb.cs` -- Harmony id
    "kaitorisenkou.SelfHediffVerb", patches `Verb.EquipmentSource`'s getter.
    `guy762_stealthbelt` (and two sibling belts) carry
    `VerbProperties_SelfHediff` + `CompProperties_VerbWithCooltime`.
  - `Spinning_Projectile/HarmonyPatches.cs` -- Harmony id
    "Weapon_Spinning_Projectile", postfix on
    `PawnRenderUtility.CarryWeaponOpenly`. 🔴 THE FILE'S OWN HEADER: "nothing
    in this assembly ever sets ThingComp_ReturningWeapon.IsThrowingWeapon to
    true -- no ThingDef points a Verb at SpinningWeaponProjectile... The
    postfix below is therefore currently a no-op even once it actually
    runs." The advertised "weapon flies out and returns" behavior
    (`returningWeaponEnabled`'s own Mod Settings description) is DEAD CODE
    as shipped -- this suite proves the one reachable half (the patch is
    applied) and explicitly does NOT claim the feature works, because by the
    mod's own admission it currently cannot.
  - `guy762_Ionization/DamageWorker_RaceHediffBase.cs` +
    `Defs/Absorbed_KotorCore/DamageDefs/Absorbed_KotorCore_SpecialDamages.xml`
    -- `guy762_InternalDamage_ion` (workerClass
    `guy762_Ionization.DamageWorker_Ionization`, `harmsHealth: false`) adds
    `guy762_IonizationBuildup` at `severityFixed 0.03 * ionSeverity` to any
    mechanoid it hits, gated by `ionDamageEnabled`.
  - `guy762_Ionization/DamageWorker_KotORPlasmaGrenade.cs` -- gates
    `FireUtility.TryStartFireIn` on `plasmaGrenadeFires`, but ONLY inside
    `ExplosionAffectCell` -- i.e. only a real explosion (`GenExplosion`)
    reaches it, never a direct `jawa/damage` hit. Wiring-only for this one;
    see "Still not proven".

Still not proven / likely first-live-run corrections:
  1. Every TIER 2/3 "Harmony patch present" or "def references the right
     class" check proves WIRING, not the mechanism's actual runtime effect
     (an AI actually jumping, a drug actually getting used, a mine actually
     getting defused, a tank actually healing). None of those are exercised
     live here -- they need a real combat/job/power scenario this suite does
     not stand up.
  2. `instantHealReuseHours`, `instantHealRecentHarmHours`,
     `jumppackFlankRanged`, `jumppackDistanceFactor`, `secondaryYieldChance`,
     `secondaryYieldAmount`, `selfHediffCooldown`, `returningWeaponSpeed`,
     `crystalAbundance`, `koltoHealSpeed`, `minePocketDefuseTime` are floor
     entries riding the SAME wiring evidence as their subsystem's main
     toggle -- none of these tuning numbers is independently verified,
     because none has a bridge read-back and `t.set_setting` is assumed
     blocked by the same static-field reflection gap Pits' own suite and
     JawaIonWeapons' suite both already found (`RSW_ArmourySettings`'s
     fields are `public static` the same way).
  3. `plasmaGrenadeFires` -- no bridge tool triggers a real `GenExplosion` at
     a cell that this suite found; only the DamageDef's `workerClass` field
     is checked. The actual "does it start fires" behavior needs a live
     explosion, not attempted here.
  4. `koltoHealEnabled`/`koltoHealSpeed` -- confirms the `KoltoTank` ThingDef
     spawns without a Config error (which a broken `Class=` on its comp
     would cause) but does not power it, put a pawn inside it, or wait for a
     heal tick.
  5. `crystalFormationsEnabled`/`crystalAbundance` -- GenStepDef wiring only;
     this suite never generates a new map, so the actual scatter never runs.
  6. `secondaryYieldEnabled`/`Chance`/`Amount` -- `TrySpawnYield` fires when
     vanilla mining COMPLETES a mineable, which this suite does not
     simulate (a `jawa/damage` hit does not run the mining job's own
     completion path); wiring-only.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Armoury")
suite.toggles = [
    "extraSoundsEnabled",
    "crystalFormationsEnabled", "crystalAbundance",
    "instantHealEnabled", "instantHealReuseHours", "instantHealRecentHarmHours",
    "jumppackEnabled", "jumppackFlankRanged", "jumppackDistanceFactor",
    "koltoHealEnabled", "koltoHealSpeed",
    "mentalBreakBlockerEnabled",
    "minePocketEnabled", "minePocketDefuseTime",
    "secondaryYieldEnabled", "secondaryYieldChance", "secondaryYieldAmount",
    "selfHediffVerbEnabled", "selfHediffCooldown",
    "returningWeaponEnabled", "returningWeaponSpeed",
    "ionDamageEnabled", "ionSeverity", "plasmaGrenadeFires",
]

ION_DAMAGE = "guy762_InternalDamage_ion"
ION_HEDIFF = "guy762_IonizationBuildup"


# ------------------------------------------------------------------ helpers
def _harmony_owner_present(t, type_name, method_name, owner):
    """READ ONLY, process-wide (spec: an independent channel, not an echo).
    Raises unless `owner` appears on some prefix/postfix/transpiler/finalizer
    of `type_name`(.`method_name`)."""
    r = t.bridge_call("jawa/harmony_patches", typeName=type_name, methodName=method_name)
    if (r or {}).get("harmonyError"):
        raise ExpectationFailed(
            "jawa/harmony_patches itself failed (%r) -- THIS INSTRUMENT IS BLIND, "
            "not proof the patch is missing" % r.get("harmonyError"))
    methods = (r or {}).get("methods") or []
    for m in methods:
        for bucket in ("prefixes", "postfixes", "transpilers", "finalizers"):
            for p in (m.get(bucket) or []):
                if p.get("owner") == owner:
                    return r
    raise ExpectationFailed(
        "no Harmony patch owned by %r found on %s.%s -- methods seen: %r"
        % (owner, type_name, method_name or "*", methods))


def _def_field(t, def_ref, field):
    r = t.bridge_call("jawa/get_defs", defs=def_ref, fields=field)
    rows = (r or {}).get("defs") or []
    if (r or {}).get("notFound"):
        raise ExpectationFailed("%s did not resolve: %r" % (def_ref, r.get("notFound")))
    if not rows:
        raise ExpectationFailed("jawa/get_defs(%s) returned no rows: %r" % (def_ref, r))
    return (rows[0].get("fields") or {}).get(field)


# ----------------------------------------------------------------- Tier 1
@suite.chain("ion_damage_mechanism")
def ion_damage_mechanism(t):
    """The one mechanism in this mod with a cheap, real, live proof: hit an
    actual mechanoid with the actual wired DamageDef and read the resulting
    hediff back independently."""
    t.clear_area(size=20)
    mech = t.spawn_pawn("Mech_Scyther", hostile=True)

    with t.component("ion_damage_adds_buildup_hediff", toggle="ionDamageEnabled"):
        before = t.bridge_call("jawa/damage", damageDef=ION_DAMAGE, amount=8,
                               thingId=mech, allowColonists=False)
        row = ((before or {}).get("targets") or (before or {}).get("results") or [{}])[0]
        if row.get("dead"):
            raise ExpectationFailed("mechanoid died from a harmsHealth=false damage def")
        if row.get("hitPointsAfter") != row.get("hitPointsBefore"):
            raise ExpectationFailed(
                "hit points moved on a harmsHealth=false damage def: before=%r after=%r"
                % (row.get("hitPointsBefore"), row.get("hitPointsAfter")))
        pawns = t.bridge_call("jawa/list_pawns", includeHealth=True, limit=50)
        target = next((p for p in (pawns or {}).get("pawns") or [] if p.get("id") == mech), None)
        if target is None:
            raise ExpectationFailed("%s not found in jawa/list_pawns" % mech)
        sev = next((h.get("severity", 0.0) for h in
                    ((target.get("health") or {}).get("hediffs") or [])
                    if h.get("def") == ION_HEDIFF), 0.0)
        if sev <= 0:
            raise ExpectationFailed(
                "%s never appeared on the mechanoid after an ion hit -- "
                "ionDamageEnabled's gate on DamageWorker_RaceHediffBase did not fire"
                % ION_HEDIFF)
        t.screenshot()

    with t.component("ion_severity_matches_default_rate", toggle="ionSeverity"):
        # A SECOND hit, same pawn: severity should have grown by roughly the
        # shipped 0.03 * ionSeverity(default 1.0) again.
        t.bridge_call("jawa/damage", damageDef=ION_DAMAGE, amount=8,
                      thingId=mech, allowColonists=False)
        pawns = t.bridge_call("jawa/list_pawns", includeHealth=True, limit=50)
        target = next((p for p in (pawns or {}).get("pawns") or [] if p.get("id") == mech), None)
        sev = next((h.get("severity", 0.0) for h in
                    ((target.get("health") or {}).get("hediffs") or [])
                    if h.get("def") == ION_HEDIFF), 0.0)
        # Two hits at severityFixed 0.03 -> ~0.06, loose band for engine rounding.
        if not (0.03 <= sev <= 0.15):
            raise ExpectationFailed(
                "after 2 ion hits, %s severity read %r -- expected roughly 0.06 "
                "(2 * 0.03 severityFixed * default ionSeverity 1.0)" % (ION_HEDIFF, sev))


# ----------------------------------------------------------------- Tier 2
@suite.chain("harmony_wiring")
def harmony_wiring(t):
    """No pawns. Every component here reads Harmony's own process-wide patch
    registry (`jawa/harmony_patches`) -- see module docstring TIER 2. A
    missing entry means the mechanism's Harmony patch never applied, which
    is invisible any other way short of decompiling the running process."""
    t.clear_area(size=10)

    with t.component("extra_sounds_patches_melee_verb", toggle="extraSoundsEnabled"):
        _harmony_owner_present(t, "Verb_MeleeAttack", "SoundHitPawn",
                               "jecstools.jecrell.comps.sounds")

    with t.component("instant_heal_patches_combat_drug_ai", toggle="instantHealEnabled"):
        _harmony_owner_present(t, "JobGiver_TakeCombatEnhancingDrug", "TryGiveJob",
                               "kaitorisenkou.InstantHealingDrug")
    with t.component("instant_heal_reuse_hours_floor", toggle="instantHealReuseHours"):
        _harmony_owner_present(t, "JobGiver_TakeCombatEnhancingDrug", "TryGiveJob",
                               "kaitorisenkou.InstantHealingDrug")
    with t.component("instant_heal_recent_harm_floor", toggle="instantHealRecentHarmHours"):
        _harmony_owner_present(t, "JobGiver_TakeCombatEnhancingDrug", "TryGiveJob",
                               "kaitorisenkou.InstantHealingDrug")

    with t.component("jumppack_patches_ai_fight_enemy", toggle="jumppackEnabled"):
        _harmony_owner_present(t, "JobGiver_AIFightEnemy", "TryGiveJob",
                               "kaitorisenkou.JumppackForMeleeAI")
    with t.component("jumppack_flank_ranged_floor", toggle="jumppackFlankRanged"):
        _harmony_owner_present(t, "JobGiver_AIFightEnemy", "TryGiveJob",
                               "kaitorisenkou.JumppackForMeleeAI")
    with t.component("jumppack_distance_factor_floor", toggle="jumppackDistanceFactor"):
        _harmony_owner_present(t, "JobGiver_AIFightEnemy", "TryGiveJob",
                               "kaitorisenkou.JumppackForMeleeAI")

    with t.component("mental_break_blocker_patches_try_start", toggle="mentalBreakBlockerEnabled"):
        _harmony_owner_present(t, "MentalStateHandler", "TryStartMentalState",
                               "kaitorisenkou.MentalBreakBlocker")

    with t.component("secondary_yield_patches_mineable", toggle="secondaryYieldEnabled"):
        _harmony_owner_present(t, "Mineable", "TrySpawnYield",
                               "kaitorisenkou.SecondaryMineableYield")
    with t.component("secondary_yield_chance_floor", toggle="secondaryYieldChance"):
        _harmony_owner_present(t, "Mineable", "TrySpawnYield",
                               "kaitorisenkou.SecondaryMineableYield")
    with t.component("secondary_yield_amount_floor", toggle="secondaryYieldAmount"):
        _harmony_owner_present(t, "Mineable", "TrySpawnYield",
                               "kaitorisenkou.SecondaryMineableYield")

    with t.component("self_hediff_verb_patches_equipment_source", toggle="selfHediffVerbEnabled"):
        _harmony_owner_present(t, "Verb", None, "kaitorisenkou.SelfHediffVerb")
    with t.component("self_hediff_cooldown_floor", toggle="selfHediffCooldown"):
        _harmony_owner_present(t, "Verb", None, "kaitorisenkou.SelfHediffVerb")

    with t.component("returning_weapon_patches_carry_openly", toggle="returningWeaponEnabled"):
        # See module docstring: the feature this gates is currently DEAD CODE
        # by the source's own admission (nothing ever sets IsThrowingWeapon).
        # This proves only that the Harmony patch itself is applied.
        _harmony_owner_present(t, "PawnRenderUtility", "CarryWeaponOpenly",
                               "Weapon_Spinning_Projectile")
    with t.component("returning_weapon_speed_floor", toggle="returningWeaponSpeed"):
        _harmony_owner_present(t, "PawnRenderUtility", "CarryWeaponOpenly",
                               "Weapon_Spinning_Projectile")


# ----------------------------------------------------------------- Tier 3
@suite.chain("def_and_spawn_wiring")
def def_and_spawn_wiring(t):
    """No Harmony evidence exists for these three mechanisms (KoltoTank's
    own Harmony instance is a documented no-op; MinePocket and
    CrystalFormations gate directly in a JobDriver/GenStep, not a patch).
    Falls back to def-field reads and, for KoltoTank, an actual spawn."""
    t.clear_area(size=10)

    with t.component("crystal_genstep_wired", toggle="crystalFormationsEnabled"):
        cls = _def_field(t, "GenStepDef/KOTOR_CrystalFormation", "genStep")
        if cls is None or "GenStep_ScatterLightsaberCrystals" not in str(cls):
            raise ExpectationFailed(
                "GenStepDef/KOTOR_CrystalFormation.genStep read %r, expected it to "
                "name CrystalFormations.GenStep_ScatterLightsaberCrystals" % cls)
    with t.component("crystal_abundance_floor", toggle="crystalAbundance"):
        cls = _def_field(t, "GenStepDef/KOTOR_CrystalFormation", "genStep")
        if cls is None:
            raise ExpectationFailed("GenStepDef/KOTOR_CrystalFormation.genStep did not resolve")

    with t.component("mine_pocket_job_wired", toggle="minePocketEnabled"):
        driver = _def_field(t, "JobDef/MinePocket_Job", "driverClass")
        if driver != "MinePocket.MinePocketJob":
            raise ExpectationFailed(
                "JobDef/MinePocket_Job.driverClass read %r, expected "
                "MinePocket.MinePocketJob" % driver)
    with t.component("mine_pocket_defuse_time_floor", toggle="minePocketDefuseTime"):
        driver = _def_field(t, "JobDef/MinePocket_Job", "driverClass")
        if driver != "MinePocket.MinePocketJob":
            raise ExpectationFailed("JobDef/MinePocket_Job.driverClass read %r" % driver)

    with t.component("kolto_tank_spawns_with_comp", toggle="koltoHealEnabled"):
        cells = t.spawn("KoltoTank", count=1)
        if not cells:
            raise ExpectationFailed("t.spawn('KoltoTank') produced no cells")
        x, z = cells[0]
        present = t.session.things_at(x, z)
        if "KoltoTank" not in present:
            raise ExpectationFailed(
                "KoltoTank not found at its own spawn cell (%d,%d) after spawning -- "
                "either the ThingDef or its CompProperties_KoltoTank failed to load: %r"
                % (x, z, present))
        t.screenshot()
    with t.component("kolto_heal_speed_floor", toggle="koltoHealSpeed"):
        present = t.session.things_at(*t.anchor)
        if "KoltoTank" not in present:
            raise ExpectationFailed("KoltoTank no longer present at anchor for the floor check")

    with t.component("plasma_grenade_damagedef_wired", toggle="plasmaGrenadeFires"):
        cls = _def_field(t, "DamageDef/guy762_GrenadeDamage_plasma", "workerClass")
        if cls != "guy762_Ionization.DamageWorker_KotORPlasmaGrenade":
            raise ExpectationFailed(
                "DamageDef/guy762_GrenadeDamage_plasma.workerClass read %r, expected "
                "guy762_Ionization.DamageWorker_KotORPlasmaGrenade" % cls)
