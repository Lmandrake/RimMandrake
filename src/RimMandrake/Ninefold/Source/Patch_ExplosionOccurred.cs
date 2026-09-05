using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1 (broad pass). divine_satiation_engine.md:
    // explosives are Ta'Baa's "door held open behind you" (§3⑥ pleases), the
    // ultimate folly Ozzik despises ("his warriors carry ion, never grenades",
    // §3⑨ displeases), and destruction that feeds Sh'kaar (§3⑧) and the
    // spark-chaos Zizzik loves (§3⑦). One explosion moves four gods at once.
    //
    // Verified against decompiled source (RimSage): GenExplosion.DoExplosion is
    // the single choke every explosion (grenade, shell, IED, reactor, EMP...)
    // passes through. Gated on radius so a stray micro-explosion (e.g. a single
    // spark effect) does not count as an ordnance event.
    [HarmonyPatch(typeof(GenExplosion), nameof(GenExplosion.DoExplosion))]
    public static class Patch_ExplosionOccurred
    {
        [HarmonyPostfix]
        public static void Postfix(float radius)
        {
            if (radius < 1.5f) return; // not an ordnance-scale blast

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.TaBaa, EventMagnitude.Small, "an explosion opened a door");
            comp.ApplyDelta(God.Shkaar, EventMagnitude.Small, "an explosion, destruction");
            comp.ApplyDelta(God.Zizzik, EventMagnitude.Small, "an explosion, the wrong spark");
            comp.ApplyDelta(God.Ozzik, -EventMagnitude.Small, "an explosion, the ego-weapon's folly");
        }
    }
}
