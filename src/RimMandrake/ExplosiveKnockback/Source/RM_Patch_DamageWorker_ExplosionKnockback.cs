using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>
    /// The hook (design §4.1): prefix + postfix on DamageWorker.ExplosionDamageThing. The prefix records
    /// eligibility BEFORE the base fills damagedThings (GPT #2: the base adds the thing first, then reads
    /// ignoredThings, so a postfix alone cannot tell "already hit" from "hit now"); the postfix only ENQUEUES
    /// immutable blast data. Nothing is despawned inside the explosion's cell loop. The name matches FlowWorks
    /// review row F10's probe regex RM_Patch_\w*(Knockback|Blowback|Stagger) on purpose.
    /// </summary>
    [HarmonyPatch(typeof(DamageWorker), "ExplosionDamageThing")]
    [RimMandrake.Shared.PatchFeature("Explosive knockback", typeof(RimMandrakeExplosiveKnockbackSettings), "enabled")]
    public static class RM_Patch_DamageWorker_ExplosionKnockback
    {
        public static float ForceOf(DamageDef def)
        {
            if (def == null)
            {
                return 0f;
            }
            RM_KnockbackExtension ext = def.GetModExtension<RM_KnockbackExtension>();
            if (ext != null)
            {
                return ext.force;
            }
            return def.harmsHealth ? RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent / 100f : 0f;
        }

        /// <summary>The blast's own throw cap (0 = the global maximum).</summary>
        public static int OwnCapOf(DamageDef def)
        {
            return def?.GetModExtension<RM_KnockbackExtension>()?.maxThrowCells ?? 0;
        }

        /// <summary>This blast's whole configuration (design §2.1 lookup order): projectile ThingDef, weapon ThingDef,
        /// DamageDef, then the unpatched setting. What the two ThingDefs hold depends on the route (GPT #7): a grenade =
        /// projectile + grenade item; a mortar = shell projectile + the mortar; a turret = projectile + its gun; a trap's
        /// own DoExplosion usually neither. Tune on the projectile; the weapon is a fallback.</summary>
        public static KbConfig ConfigOf(Explosion explosion, DamageDef def)
        {
            return KbLookup.Resolve(explosion?.projectile?.GetModExtension<RM_KnockbackExtension>()?.ToConfig(),
                explosion?.weapon?.GetModExtension<RM_KnockbackExtension>()?.ToConfig(),
                def?.GetModExtension<RM_KnockbackExtension>()?.ToConfig(),
                def != null && def.harmsHealth, RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent / 100f);
        }

        /// <summary>Shield capture (owner Q4): the pawn whose damage is being applied right now, and the shield that
        /// absorbed it. Set by the prefix, filled by RM_Patch_CompShield_RecordAbsorb, read and cleared by the postfix —
        /// TakeDamage runs synchronously inside ExplosionDamageThing, so nothing else can interleave.</summary>
        internal static Pawn shieldWatch;
        internal static CompShield shieldAbsorbed;

        public static void Prefix(DamageWorker __instance, Explosion explosion, Thing t, List<Thing> damagedThings,
            List<Thing> ignoredThings, out KbConfig __state)
        {
            __state = null;
            if (!RimMandrakeExplosiveKnockbackSettings.enabled || t == null || explosion == null)
            {
                return;
            }
            KbConfig cfg = ConfigOf(explosion, __instance.def);
            if (cfg.force <= 0f)
            {
                return; // first-line exit: fire, EMP, smoke... cost nothing
            }
            if (t.def.category == ThingCategory.Mote || t.def.category == ThingCategory.Ethereal)
            {
                return;
            }
            if (damagedThings != null && damagedThings.Contains(t))
            {
                return;
            }
            if (ignoredThings != null && ignoredThings.Contains(t))
            {
                return;
            }
            // a closed container itself is shoved a little (owner 2026-11-11); every other building is not ours
            bool container = t is Building && RimMandrakeExplosiveKnockbackSettings.shoveClosedContainers
                && RM_KnockbackCompat.IsClosedContainer(t);
            if (!(t is Pawn) && !(t is Corpse) && t.def.category != ThingCategory.Item && !container)
            {
                return;
            }
            __state = cfg;
            shieldWatch = t as Pawn;
            shieldAbsorbed = null;
            // owner ruling 2026-11-12: a stack this blast WILL throw takes reduced blast damage, decided here, before the
            // base applies the damage, so a stack the full blast would destroy survives to scatter
            spareThing = null;
            float pct = RimMandrakeExplosiveKnockbackSettings.thrownGoodsBlastDamagePercent;
            if (pct < 100f && t.def.category == ThingCategory.Item && RM_MapComponent_Knockback.ItemWillBeThrown(t, explosion, cfg))
            {
                spareThing = t;
                spareFactor = pct < 0f ? 0f : pct / 100f;
            }
        }

        /// <summary>The item whose blast damage is being scaled right now (set by the prefix, read by
        /// RM_Patch_Thing_SpareThrownGoods, cleared by the postfix; TakeDamage runs synchronously inside).</summary>
        internal static Thing spareThing;
        internal static float spareFactor = 1f;

        public static void Postfix(DamageWorker __instance, Explosion explosion, Thing t, KbConfig __state)
        {
            CompShield shield = shieldWatch == t ? shieldAbsorbed : null;
            spareThing = null;
            shieldWatch = null;
            shieldAbsorbed = null;
            if (__state == null)
            {
                return;
            }
            Map map = explosion.Map;
            RM_MapComponent_Knockback comp = map?.GetComponent<RM_MapComponent_Knockback>();
            if (comp == null)
            {
                return;
            }
            comp.Enqueue(new KnockbackRequest
            {
                explosionId = explosion.thingIDNumber,
                centre = explosion.Position,
                radius = explosion.radius,
                damType = __instance.def,
                force = __state.force,
                ownCap = __state.ownCap,
                config = __state,
                shield = shield,
                instigator = explosion.instigator,
                thing = t,
                takeoff = t.Position,
                tick = Find.TickManager.TicksGame,
            });
        }

        /// <summary>Runs even when ExplosionDamageThing throws (the postfix then does not): a watch left set would scale an
        /// unrelated later hit on the same stack, or credit an unrelated shield absorb to this blast.</summary>
        public static void Finalizer()
        {
            spareThing = null;
            shieldWatch = null;
            shieldAbsorbed = null;
        }
    }

    /// <summary>Records the shield that absorbed an explosion's damage AT DAMAGE TIME (GPT #5): "still active afterwards"
    /// would miss a shield that absorbed and broke. Only while our ExplosionDamageThing prefix is watching that pawn.</summary>
    [HarmonyPatch(typeof(CompShield), nameof(CompShield.PostPreApplyDamage))]
    public static class RM_Patch_CompShield_RecordAbsorb
    {
        public static void Postfix(CompShield __instance, bool absorbed)
        {
            Pawn w = RM_Patch_DamageWorker_ExplosionKnockback.shieldWatch;
            // PawnOwner is protected; TakeDamage(t) only reaches t's own shields (worn or built in), so the watch is enough
            if (absorbed && w != null)
            {
                RM_Patch_DamageWorker_ExplosionKnockback.shieldAbsorbed = __instance;
            }
        }
    }

    public sealed class KnockbackRequest
    {
        public int explosionId;
        public IntVec3 centre;
        public float radius;
        public DamageDef damType;
        public float force;
        public int ownCap;
        public KbConfig config;
        public CompShield shield;   // the shield that absorbed this blast's damage, or null
        public Thing instigator;
        public Thing thing;
        public IntVec3 takeoff;
        public int tick;
    }
}

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>Owner ruling 2026-11-12 (RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER): scales the blast's DamageInfo for
    /// the one stack the explosion prefix marked as about to be thrown. Reference compare only on every other call.</summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.TakeDamage))]
    public static class RM_Patch_Thing_SpareThrownGoods
    {
        public static void Prefix(Thing __instance, ref DamageInfo dinfo)
        {
            if (RM_Patch_DamageWorker_ExplosionKnockback.spareThing == null || __instance != RM_Patch_DamageWorker_ExplosionKnockback.spareThing)
            {
                return;
            }
            float before = dinfo.Amount;
            dinfo.SetAmount(before * RM_Patch_DamageWorker_ExplosionKnockback.spareFactor);
            RM_KnockbackJournal.Add("spared", -1, __instance, "blast", before, "taken", dinfo.Amount);
        }
    }
}
