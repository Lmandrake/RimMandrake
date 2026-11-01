using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    // RUSTCATHEDRAL_WORN_BIT_ARC_1 (campaign wiring). The RM tier knows no gods: RM_WornBit.Announce is the seam, and this
    // postfix reads it by name so Rites takes no compile dependency on the Rust Cathedral assembly (absent mod: no patch).
    // Keep: Mob'Unloo +, Ohm +, Ozzik displeased. Free: Ohm +, Mob'Unloo annoyed. Every delta is tagged "The Worn Bit".
    // Regard is the Python GM blackboard's (gm_blackboard_shadow.py), whose restore-choice story flag is not wired yet;
    // until it is, the Regard line is a logged would-be, never silent (the item's words).
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Ninefold event hook: WornBitChoice")]
    public static class Patch_WornBitChoice
    {
        public const string Tag = "The Worn Bit";

        public static bool Prepare()
        {
            return TargetMethod() != null;
        }

        public static MethodBase TargetMethod()
        {
            return AccessTools.Method(AccessTools.TypeByName("RimMandrake.RustCathedral.RM_WornBit"), "Announce");
        }

        /// <summary>jawa/static_call read for validation.py: the satiation each god moves by for one branch. Moves them for real.</summary>
        public static string ProofDeltas(bool keep)
        {
            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            float ohm = comp.GetSatiation(God.Ohm), mob = comp.GetSatiation(God.MobUnloo), ozzik = comp.GetSatiation(God.Ozzik), rekko = comp.GetSatiation(God.Rekko);
            Postfix(keep);
            return "DELTAS ohm " + (comp.GetSatiation(God.Ohm) - ohm) + " mob " + (comp.GetSatiation(God.MobUnloo) - mob)
                + " ozzik " + (comp.GetSatiation(God.Ozzik) - ozzik) + " rekko " + (comp.GetSatiation(God.Rekko) - rekko);
        }

        [HarmonyPostfix]
        public static void Postfix(bool keep)
        {
            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;
            comp.ApplyDelta(God.Ohm, EventMagnitude.Medium, Tag + ": " + (keep ? "keep" : "free"));
            comp.ApplyDelta(God.MobUnloo, keep ? EventMagnitude.Medium : -EventMagnitude.Medium, Tag + ": " + (keep ? "keep" : "free"));
            if (keep)
            {
                comp.ApplyDelta(God.Ozzik, -EventMagnitude.Medium, Tag + ": keep");
            }
            Log.Message("[Ninefold] " + Tag + " Regard would-be: " + (keep ? "falls (keep)" : "rises (free)"));
        }
    }
}
