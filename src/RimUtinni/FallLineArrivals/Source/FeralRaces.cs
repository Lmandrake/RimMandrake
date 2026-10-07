using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.FallLineArrivals
{
    // ════════════════════════════════════════════════════════════════════
    // FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1 — fall_line.md §8b "normally sentient races gone feral".
    //
    // RUT_FeralSurvivor (PawnKindDef) rides the Band B routes unchanged: same pool, same feral flag,
    // same flee/lurk splice. What differs is the ending. A droid's flag clears and it is whole; a
    // person who joins the colony keeps RUT_Hediff_FeralScar for life.
    //
    //   FeralKindExtension   on a PawnKindDef: which scar it takes, and its letter text.
    //   FeralScar.Apply      idempotent; the one place the scar is added.
    //   Patch_TryEnslave     Harmony postfix on GenGuest.TryEnslavePrisoner (the single state
    //                        transition both enslave callers reach — RimSage, 2026-09-24).
    //   HediffComp_FeralClears also calls Apply before removing the flag, so a RECRUITED survivor
    //                        is scarred too; the scar is a fact about the pawn, not the route.
    // ════════════════════════════════════════════════════════════════════

    public class FeralKindExtension : DefModExtension
    {
        /// <summary>The permanent hediff this kind takes on joining the colony. Null = clean (droid path).</summary>
        public HediffDef scarHediff;
        public string letterLabel;
        public string letterLabelFromWreck;
        public string driftText;
        public string wreckText;
        public string behaviourText;
    }

    public static class FeralScar
    {
        public static HediffDef ScarFor(Pawn p) => p?.kindDef?.GetModExtension<FeralKindExtension>()?.scarHediff;

        /// <summary>Add the kind's scar if it has one and the pawn lacks it. Returns true when added.</summary>
        public static bool Apply(Pawn p)
        {
            HediffDef scar = ScarFor(p);
            if (scar == null || p.Dead || p.health?.hediffSet == null || p.health.hediffSet.HasHediff(scar))
            {
                return false;
            }
            p.health.AddHediff(scar);
            return true;
        }
    }

    [StaticConstructorOnStartup]
    public static class FallLineArrivalsHarmony
    {
        public const string HarmonyId = "mandrake.rut.falllinearrivals";

        static FallLineArrivalsHarmony()
        {
            new Harmony(HarmonyId).PatchAll(Assembly.GetExecutingAssembly());
        }
    }

    [HarmonyPatch(typeof(GenGuest), nameof(GenGuest.TryEnslavePrisoner))]
    public static class Patch_TryEnslavePrisoner_FeralScar
    {
        public static void Postfix(Pawn prisoner, bool __result)
        {
            if (__result && prisoner != null && FeralSurvivors.IsFeral(prisoner))
            {
                FeralScar.Apply(prisoner);
            }
        }
    }
}
