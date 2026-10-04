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

MW2 IS GONE, NOT A DEPENDENCY (ARMOURY_MW2_CUT_1, 2026-09-13, owner ruled cut
over gate): `kaitorisenkou.ModularWeapons2` was previously a real
undeclared dependency -- the absorbed KotOR content referenced its types
with no MayRequire gate, and a min16 test environment missing it saw those
ThingDefs silently DISCARDED at load (missing-donor-type-eats-the-def),
NREing vanilla `RecipeDefGenerator.SetIngredients`. That is no longer true:
every `ModularWeapons2.*` reference, comp block and root-tag part/mount def
was stripped from this pack's XML (0 remain; verified by grep). This mod's
test environment must NOT carry `kaitorisenkou.ModularWeapons2` for this
suite to describe the shipped game -- if it is present, the weapons/armour
under test render and behave with an inert donor mod alongside them, which
proves nothing this suite claims to prove.

`guy762.MM.KotORCore` (already this mod's own declared `<modDependencies>`
entry, `About/About.xml:16`) remains a REAL dependency, unrelated to MW2:
it is where every `kotorsound_*` SoundDef this mod's absorbed content plays
actually lives (`Kotor_Misc_Sounds.xml:34`). The min16 test environment
must still add that one packageId alongside `mandrake.rsw.armoury` itself.

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
    # HarmonyPatches' own instrument-blind Fail() nests the flag under
    # `details` (JawaBenchTerrainTools.cs's shared Fail(message, extra) shape
    # is {success, message, details=extra}) -- there is no top-level
    # "harmonyError" key, so this guard never fired and a genuinely blind
    # instrument fell through to the generic "no patch found" raise below,
    # misreporting an instrument failure as a missing patch.
    if (r or {}).get("details", {}).get("harmonyError"):
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


def _class_wired(t, def_ref, xml_rel, needle):
    """A System.Type field (driverClass / workerClass) cannot be read through jawa/get_defs ('(no such field)' -- a
    failed instrument, not a wiring failure: load 14 FAILED three loaded defs on it). So: the shipped XML must carry
    `needle`, and the LIVE def must have resolved (foundCount 1; an unresolvable class discards or errors the def)."""
    import os as _o
    path = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "Defs", *xml_rel.split("/"))
    if needle not in open(path, encoding="utf-8").read():
        raise ExpectationFailed("%s no longer carries %s" % (xml_rel, needle))
    r = t.bridge_call("jawa/get_defs", defs=def_ref)
    if t.session is not None and (not r or not r.get("success") or r.get("foundCount") != 1):
        raise ExpectationFailed("%s did not load: %r" % (def_ref, r))


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


import contextlib as _contextlib


@_contextlib.contextmanager
def _pure(t, name, **kw):
    """t.component() for a PURE READ (a Harmony-registry / def read that shares no state with its neighbours): a FAIL
    does not poison the next component. Without this one dead donor patch (JumppackForMeleeAI throws in its static
    constructor on this list, FULL_LOAD_RESIDUE_TRIAGE_1) left 10 harmony and 6 def components UNMEASURED (load 13)."""
    before = t.upstream_failed
    with t.component(name, **kw) as tt:
        yield tt
    if not before:
        t.upstream_failed = False


# ----------------------------------------------------------------- Tier 2
@suite.chain("harmony_wiring")
def harmony_wiring(t):
    """No pawns. Every component here reads Harmony's own process-wide patch
    registry (`jawa/harmony_patches`) -- see module docstring TIER 2. A
    missing entry means the mechanism's Harmony patch never applied, which
    is invisible any other way short of decompiling the running process."""
    t.clear_area(size=10)

    with _pure(t, "extra_sounds_patches_melee_verb", toggle="extraSoundsEnabled"):
        _harmony_owner_present(t, "Verb_MeleeAttack", "SoundHitPawn",
                               "jecstools.jecrell.comps.sounds")

    with _pure(t, "instant_heal_patches_combat_drug_ai", toggle="instantHealEnabled"):
        _harmony_owner_present(t, "JobGiver_TakeCombatEnhancingDrug", "TryGiveJob",
                               "kaitorisenkou.InstantHealingDrug")
    with _pure(t, "instant_heal_reuse_hours_floor", toggle="instantHealReuseHours"):
        _harmony_owner_present(t, "JobGiver_TakeCombatEnhancingDrug", "TryGiveJob",
                               "kaitorisenkou.InstantHealingDrug")
    with _pure(t, "instant_heal_recent_harm_floor", toggle="instantHealRecentHarmHours"):
        _harmony_owner_present(t, "JobGiver_TakeCombatEnhancingDrug", "TryGiveJob",
                               "kaitorisenkou.InstantHealingDrug")

    with _pure(t, "jumppack_patches_ai_fight_enemy", toggle="jumppackEnabled"):
        _harmony_owner_present(t, "JobGiver_AIFightEnemy", "TryGiveJob",
                               "kaitorisenkou.JumppackForMeleeAI")
    with _pure(t, "jumppack_flank_ranged_floor", toggle="jumppackFlankRanged"):
        _harmony_owner_present(t, "JobGiver_AIFightEnemy", "TryGiveJob",
                               "kaitorisenkou.JumppackForMeleeAI")
    with _pure(t, "jumppack_distance_factor_floor", toggle="jumppackDistanceFactor"):
        _harmony_owner_present(t, "JobGiver_AIFightEnemy", "TryGiveJob",
                               "kaitorisenkou.JumppackForMeleeAI")

    with _pure(t, "mental_break_blocker_patches_try_start", toggle="mentalBreakBlockerEnabled"):
        _harmony_owner_present(t, "MentalStateHandler", "TryStartMentalState",
                               "kaitorisenkou.MentalBreakBlocker")

    with _pure(t, "secondary_yield_patches_mineable", toggle="secondaryYieldEnabled"):
        _harmony_owner_present(t, "Mineable", "TrySpawnYield",
                               "kaitorisenkou.SecondaryMineableYield")
    with _pure(t, "secondary_yield_chance_floor", toggle="secondaryYieldChance"):
        _harmony_owner_present(t, "Mineable", "TrySpawnYield",
                               "kaitorisenkou.SecondaryMineableYield")
    with _pure(t, "secondary_yield_amount_floor", toggle="secondaryYieldAmount"):
        _harmony_owner_present(t, "Mineable", "TrySpawnYield",
                               "kaitorisenkou.SecondaryMineableYield")

    with _pure(t, "self_hediff_verb_patches_equipment_source", toggle="selfHediffVerbEnabled"):
        _harmony_owner_present(t, "Verb", None, "kaitorisenkou.SelfHediffVerb")
    with _pure(t, "self_hediff_cooldown_floor", toggle="selfHediffCooldown"):
        _harmony_owner_present(t, "Verb", None, "kaitorisenkou.SelfHediffVerb")

    with _pure(t, "returning_weapon_patches_carry_openly", toggle="returningWeaponEnabled"):
        # See module docstring: the feature this gates is currently DEAD CODE
        # by the source's own admission (nothing ever sets IsThrowingWeapon).
        # This proves only that the Harmony patch itself is applied.
        _harmony_owner_present(t, "PawnRenderUtility", "CarryWeaponOpenly",
                               "Weapon_Spinning_Projectile")
    with _pure(t, "returning_weapon_speed_floor", toggle="returningWeaponSpeed"):
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

    with _pure(t, "crystal_genstep_wired", toggle="crystalFormationsEnabled"):
        # jawa/get_defs shows a GenStep as its FIELDS (groups, order...) and never names the class, so the class is
        # asserted from the shipped XML and the LIVE half proves the def resolved with a real, non-null genStep object
        # (an unresolvable Class= discards the whole def). Load 13: the old read of 'genStep' as a class name gave
        # '(no such field)' and FAILED a def that was wired and loaded.
        import os as _o
        xml_path = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "Defs", "Absorbed_KotorCore",
                                "ThingDefs_Resources", "Absorbed_KotorCore_CrystalMapGenerator.xml")
        if 'Class="CrystalFormations.GenStep_ScatterLightsaberCrystals"' not in open(xml_path, encoding="utf-8").read():
            raise ExpectationFailed("KOTOR_CrystalFormation's genStep no longer names CrystalFormations.GenStep_ScatterLightsaberCrystals")
        r = t.bridge_call("jawa/get_defs", defs="GenStepDef/KOTOR_CrystalFormation", deep=True)
        if t.session is not None:
            rows = (r or {}).get("defs") or []
            gs = ((rows[0].get("fields") or {}).get("genStep")) if rows else None
            if (r or {}).get("notFound") or not isinstance(gs, dict) or "groups" not in gs:
                raise ExpectationFailed("GenStepDef/KOTOR_CrystalFormation did not load with a populated genStep: %r" % (r,))
    with _pure(t, "crystal_abundance_floor", toggle="crystalAbundance"):
        cls = _def_field(t, "GenStepDef/KOTOR_CrystalFormation", "genStep")
        if cls is None:
            raise ExpectationFailed("GenStepDef/KOTOR_CrystalFormation.genStep did not resolve")

    with _pure(t, "mine_pocket_job_wired", toggle="minePocketEnabled"):
        _class_wired(t, "JobDef/MinePocket_Job", "Absorbed_KotorCore/Absorbed_KotorCore_JobDefs_misc.xml",
                     "<driverClass>MinePocket.MinePocketJob</driverClass>")
    with _pure(t, "mine_pocket_defuse_time_floor", toggle="minePocketDefuseTime"):
        _class_wired(t, "JobDef/MinePocket_Job", "Absorbed_KotorCore/Absorbed_KotorCore_JobDefs_misc.xml",
                     "<driverClass>MinePocket.MinePocketJob</driverClass>")

    with _pure(t, "kolto_tank_spawns_with_comp", toggle="koltoHealEnabled"):
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
    with _pure(t, "kolto_heal_speed_floor", toggle="koltoHealSpeed"):
        present = t.session.things_at(*t.anchor)
        if "KoltoTank" not in present:
            raise ExpectationFailed("KoltoTank no longer present at anchor for the floor check")

    with _pure(t, "plasma_grenade_damagedef_wired", toggle="plasmaGrenadeFires"):
        _class_wired(t, "DamageDef/guy762_GrenadeDamage_plasma",
                     "Absorbed_KotorCore/DamageDefs/Absorbed_KotorCore_GrenadeDamages.xml",
                     "<workerClass>guy762_Ionization.DamageWorker_KotORPlasmaGrenade</workerClass>")


# ------------------------------------------------- the melee ladder landed (NORTHSTAR_PARTIAL_GAPS_FILL_1)
# The audit's headline gap: "the weapon-ladder rebalance has no component asserting any weapon damage value".
# Armoury_MeleePower.xml is GENERATED (gen_armoury_patch.py): every `tools/li[label=L]/power` it writes is read
# here and compared to the live tool power of each patched def that is loaded (`get_defs fields=tools deep` --
# Tool.power is public). Our absorbed weapons (guy762_*, RSW_JDSA_*) must ALL be loaded and patched; a donor's
# defs (OuterRim_*) count only when that donor is active. RANGED damage is NOT readable this way:
# ProjectileProperties.damageAmountBase is PRIVATE (RimSage 2026-10-03) and DeepSerializeValue reflects public
# fields only, so Armoury_RangedDamage.xml's ladder stays unasserted live until a [Tool] reads GetDamageAmount.
import os as _os
import re as _re
import xml.etree.ElementTree as _ET

_MELEE_PATCH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "Patches", "Armoury_MeleePower.xml")
_TOOL_XPATH = _re.compile(r'^/Defs/ThingDef\[defName="([^"]+)"\]/tools/li\[label="([^"]+)"\]/power$')


def melee_targets(path=_MELEE_PATCH):
    """{defName: {toolLabel: power}} from every PatchOperationReplace on a tool's power in the melee patch."""
    out = {}
    for op in _ET.parse(path).getroot().iter("li"):
        if not op.get("Class", "").endswith("PatchOperationReplace"):
            continue
        m = _TOOL_XPATH.match((op.findtext("xpath") or "").strip())
        val = op.find("value/power")
        if m and val is not None and (val.text or "").strip():
            out.setdefault(m.group(1), {})[m.group(2)] = float(val.text)
    return out


def _ours(name):
    return name.startswith(("guy762_", "RSW_"))


@suite.chain("melee_ladder_landed")
def melee_ladder_landed(t):
    """Every generated melee power value is the live value on every loaded patched weapon."""
    with t.component("melee_patch_powers_are_live", beyond_toggle=True):
        targets = melee_targets()
        ours = sorted(n for n in targets if _ours(n))
        if len(ours) < 10 or "guy762_vsword" not in ours:
            raise ExpectationFailed("the melee patch parse is blind: %d of our own defs (%s)" % (len(ours), ours))
        r = t.bridge_call("jawa/get_defs", defs=";".join("ThingDef/%s" % n for n in sorted(targets)),
                          fields="tools", deep=True)
        if t.session is not None and not t.upstream_failed:
            if not (r or {}).get("success"):
                raise ExpectationFailed("get_defs failed: %r" % r)
            missing = set(r.get("notFound") or [])
            lost = [n for n in ours if n in missing]
            if lost:
                raise ExpectationFailed("our own absorbed weapons are not loaded: %s" % lost)
            rows = dict((row.get("defName"), row) for row in (r.get("defs") or []))
            bad, checked = [], 0
            for name, want in sorted(targets.items()):
                if name not in rows:
                    continue                                   # a donor def whose mod is not active
                tools = ((rows[name].get("fields") or {}).get("tools")) or []
                live = dict((str(tl.get("label")), tl.get("power")) for tl in tools if isinstance(tl, dict))
                for label, power in sorted(want.items()):
                    checked += 1
                    got = live.get(label)
                    try:
                        ok = got is not None and abs(float(got) - power) < 1e-3
                    except (TypeError, ValueError):
                        ok = False
                    if not ok:
                        bad.append("%s/%s: patch %g, live %r" % (name, label, power, got))
            if checked == 0:
                raise ExpectationFailed("compared no tool power at all")
            if bad:
                raise ExpectationFailed("%d of %d patched melee powers are not live (patch did not apply, or a "
                                        "later patch overrides): %s" % (len(bad), checked, "; ".join(bad[:12])))


# ------------------------------------------------- the ranged ladder landed (ARMOURY_PROJECTILE_DAMAGE_TOOL_1)
# ProjectileProperties.damageAmountBase is PRIVATE, so get_defs cannot read it; jawa/projectile_damage (JawaBench,
# JawaBenchProjectileTools.cs) returns the raw private field. Every PatchOperationReplace on
# /Defs/ThingDef[defName=X]/projectile/damageAmountBase in the GENERATED Armoury_RangedDamage.xml is compared to it.
# Required: every def this mod DECLARES (its own Defs/) and every def under a Ludeon FindMod (all DLC assumed).
# A donor group counts only when its defs are loaded, and a group partly loaded is a FAIL (its siblings prove the
# donor active). 🔴 An op on a def we declare must not sit under a donor FindMod: when that donor is not loaded
# the op never runs and our own def keeps the unpatched value (FindMod returns true on no match, so silently).
_RANGED_PATCH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "Patches", "Armoury_RangedDamage.xml")
_DMG_XPATH = _re.compile(r'^/Defs/ThingDef\[defName="([^"]+)"\]/projectile/damageAmountBase$')
_LUDEON_MOD_NAMES = {"Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"}


def ranged_targets(path=_RANGED_PATCH):
    """[(defName, value, guard)] where guard is the FindMod's mod name, or None for a def-guarded (own) op."""
    out = []
    for op in _ET.parse(path).getroot().findall("Operation"):
        mods = [li.text for li in op.findall("mods/li")]
        guard = mods[0] if op.get("Class", "").endswith("PatchOperationFindMod") and mods else None
        for li in op.iter("li"):
            if not li.get("Class", "").endswith("PatchOperationReplace"):
                continue
            m = _DMG_XPATH.match((li.findtext("xpath") or "").strip())
            val = li.find("value/damageAmountBase")
            if m and val is not None and (val.text or "").strip():
                out.append((m.group(1), int(val.text), guard))
    return out


def own_declared_defnames(defs_dir=None):
    """Every defName a ThingDef in this mod's own Defs/ declares (the absorbed KotOR/JDS/OPTurret sets included)."""
    defs_dir = defs_dir or _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "Defs")
    names = set()
    for dp, _dn, fns in _os.walk(defs_dir):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            try:
                root = _ET.parse(_os.path.join(dp, fn)).getroot()
            except _ET.ParseError:
                continue
            for td in root.iter("ThingDef"):
                n = td.findtext("defName")
                if n:
                    names.add(n.strip())
    return names


@suite.chain("ranged_ladder_landed")
def ranged_ladder_landed(t):
    """Every generated projectile damageAmountBase is the live raw value on every loaded patched projectile."""
    targets = ranged_targets()
    own = own_declared_defnames()
    with t.component("own_ranged_ops_carry_no_donor_guard", beyond_toggle=True):
        if not targets or not own:
            raise ExpectationFailed("the ranged patch / own-def parse is blind: %d ops, %d own defs"
                                    % (len(targets), len(own)))
        bad = sorted("%s (under FindMod '%s')" % (n, g) for n, _v, g in targets
                     if n in own and g is not None and g not in _LUDEON_MOD_NAMES)
        if bad:
            raise ExpectationFailed("%d op(s) on defs this mod declares sit under a donor FindMod, so they never run "
                                    "when that donor is not loaded: %s" % (len(bad), "; ".join(bad)))
    with t.component("ranged_patch_damage_is_live", beyond_toggle=True):
        if len(targets) < 20 or not any(n in own for n, _v, _g in targets):
            raise ExpectationFailed("the ranged patch parse is blind: %d ops, %d on our own defs"
                                    % (len(targets), sum(1 for n, _v, _g in targets if n in own)))
        r = t.bridge_call("jawa/projectile_damage", defs=";".join(sorted({n for n, _v, _g in targets})))
        if t.session is not None and not t.upstream_failed:
            if not (r or {}).get("success"):
                raise ExpectationFailed("projectile_damage failed: %r" % r)
            missing = set(r.get("notFound") or [])
            rows = dict((row.get("defName"), row) for row in (r.get("rows") or []) if row.get("found"))
            required = sorted({n for n, _v, g in targets if n in own or g is None or g in _LUDEON_MOD_NAMES})
            lost = [n for n in required if n in missing]
            if lost:
                raise ExpectationFailed("required projectiles are not loaded: %s" % lost)
            groups = {}
            for n, _v, g in targets:
                if g is not None and g not in _LUDEON_MOD_NAMES and n not in own:
                    groups.setdefault(g, set()).add(n)
            partial = ["%s: %s missing of %d" % (g, sorted(ns & missing), len(ns))
                       for g, ns in sorted(groups.items()) if (ns & missing) and (ns - missing)]
            if partial:
                raise ExpectationFailed("a donor group is partly loaded: %s" % "; ".join(partial))
            bad, checked = [], 0
            for n, want, _g in targets:
                if n not in rows:
                    continue                                   # a donor def whose mod is not active
                checked += 1
                row = rows[n]
                got = row.get("damageAmountBase")
                if not row.get("isProjectile"):
                    bad.append("%s: not a projectile" % n)
                    continue
                try:
                    ok = int(got) == want
                except (TypeError, ValueError):
                    ok = False
                if not ok:
                    bad.append("%s: patch %d, live %r" % (n, want, got))
            if checked == 0:
                raise ExpectationFailed("compared no projectile at all")
            if bad:
                raise ExpectationFailed("%d of %d patched projectile damages are not live (patch did not apply, or a "
                                        "later patch overrides): %s" % (len(bad), checked, "; ".join(bad[:12])))
