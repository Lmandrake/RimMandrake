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

        public static void Prefix(DamageWorker __instance, Explosion explosion, Thing t, List<Thing> damagedThings,
            List<Thing> ignoredThings, out bool __state)
        {
            __state = false;
            if (!RimMandrakeExplosiveKnockbackSettings.enabled || t == null || explosion == null)
            {
                return;
            }
            if (ForceOf(__instance.def) <= 0f)
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
            __state = true;
        }

        public static void Postfix(DamageWorker __instance, Explosion explosion, Thing t, bool __state)
        {
            if (!__state)
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
                force = ForceOf(__instance.def),
                ownCap = OwnCapOf(__instance.def),
                instigator = explosion.instigator,
                thing = t,
                takeoff = t.Position,
                tick = Find.TickManager.TicksGame,
            });
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
        public Thing instigator;
        public Thing thing;
        public IntVec3 takeoff;
        public int tick;
    }
}
