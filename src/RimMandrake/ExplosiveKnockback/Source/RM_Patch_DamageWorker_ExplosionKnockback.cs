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
            if (!(t is Pawn) && !(t is Corpse) && t.def.category != ThingCategory.Item)
            {
                return;
            }
            __state = cfg;
            shieldWatch = t as Pawn;
            shieldAbsorbed = null;
        }

        public static void Postfix(DamageWorker __instance, Explosion explosion, Thing t, KbConfig __state)
        {
            CompShield shield = shieldWatch == t ? shieldAbsorbed : null;
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
