using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // VEXXITH_CLOSED_LOOP_BUILD_1 — vexxith ignores acid.
    //
    // Owner ruling 2026-10-03 (question card): the acid-immunity Harmony patch
    // goes INTO the Cauldron mod, which drops its no-patch purity for it.
    //
    // There is no vanilla "acid resistance" stat, and Thing.damageMultipliers is
    // per-ThingDef, so it cannot say "anything MADE OF vexxith". Hence a prefix on
    // Thing.TakeDamage keyed on two marker extensions, both data:
    //   * RM_AcidDamageExtension on a DamageDef says "this damage is acid".
    //     Patches/RM_Cauldron_AcidDamage.xml puts it on vanilla AcidBurn and, when
    //     present, Warscar's RM_BloomAcid. Another mod's acid joins by the same patch.
    //   * RM_AcidImmuneExtension on a ThingDef says "this is acid-proof". On a STUFF
    //     def (RM_Vexxith) it covers everything made of it; on a plain ThingDef it
    //     covers that def alone.
    // Scope: the Thing that takes the damage. A pawn wearing vexxith armour is not
    // itself immune (its body takes the burn); the armour piece is.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AcidDamageExtension : DefModExtension
    {
    }

    public class RM_AcidImmuneExtension : DefModExtension
    {
    }

    [StaticConstructorOnStartup]
    public static class RM_VexxithAcidImmunity
    {
        static RM_VexxithAcidImmunity()
        {
            // Shared per-class resilience (HARMONY_PATCH_RESILIENCE_1): a game update that renames Thing.TakeDamage switches
            // THIS feature's Mod Settings toggle off for the session instead of throwing out of PatchAll.
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.cauldron.vexxith"),
                typeof(RM_VexxithAcidImmunity).Assembly, "RimMandrake.Cauldron");
        }

        public static bool IsAcid(DamageDef def)
        {
            return def != null && def.modExtensions != null && def.HasModExtension<RM_AcidDamageExtension>();
        }

        public static bool IsAcidProof(Thing thing)
        {
            if (thing == null || thing.def == null) return false;
            if (thing.def.modExtensions != null && thing.def.HasModExtension<RM_AcidImmuneExtension>()) return true;
            ThingDef stuff = thing.Stuff;
            return stuff != null && stuff.modExtensions != null && stuff.HasModExtension<RM_AcidImmuneExtension>();
        }
    }

    [HarmonyPatch(typeof(Thing), nameof(Thing.TakeDamage))]
    [RimMandrake.Shared.PatchFeature("Vexxith acid immunity", typeof(RM_CauldronSettings), nameof(RM_CauldronSettings.vexxithAcidImmunityEnabled))]
    public static class Patch_Thing_TakeDamage_VexxithAcid
    {
        public static bool Prefix(Thing __instance, DamageInfo dinfo, ref DamageWorker.DamageResult __result)
        {
            if (!RM_CauldronSettings.vexxithAcidImmunityEnabled) return true;
            if (!RM_VexxithAcidImmunity.IsAcid(dinfo.Def)) return true;
            if (!RM_VexxithAcidImmunity.IsAcidProof(__instance)) return true;
            __result = new DamageWorker.DamageResult();
            return false;
        }
    }

    /// <summary>With the setting off, the acid-proof vexxith door leaves the architect menu at startup (applies
    /// on the next launch). Already-built doors stay, and stay acid-proof while the immunity toggle is on.</summary>
    [StaticConstructorOnStartup]
    public static class RM_VexxithDoorGate
    {
        static RM_VexxithDoorGate()
        {
            if (RM_CauldronSettings.vexxithDoorEnabled) return;
            ThingDef door = DefDatabase<ThingDef>.GetNamedSilentFail("RM_VexxithDoor");
            if (door == null) return;
            // DesignationCategoryDef resolves its designator list in an ExecuteWhenFinished queued at
            // ResolveReferences, so this may run before OR after it: null the category (covers before) and
            // drop an already-built designator (covers after).
            DesignationCategoryDef cat = door.designationCategory;
            door.designationCategory = null;
            if (cat != null)
            {
                cat.AllResolvedDesignators.RemoveAll(d => d is Designator_Build b && b.PlacingDef == door);
            }
        }
    }
}
