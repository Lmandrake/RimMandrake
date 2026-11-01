using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
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

        /// <summary>jawa/static_call read for validation.py, politics toggle on: which gods moved and the reason each delta carried.</summary>
        public static string ProofDeltas(bool keep)
        {
            return Drive(keep, true);
        }

        /// <summary>The same drive with the politics toggle off: no god may move.</summary>
        public static string ProofDeltasOff(bool keep)
        {
            return Drive(keep, false);
        }

        /// <summary>Every god starts at 0 so none is clamped, the real RM_WornBit.AnnounceChoice runs through the Harmony patch,
        /// then the gods, the toggle and the watcher go back as they were. Reflection: Rites has no compile dependency here.</summary>
        private static string Drive(bool keep, bool politics)
        {
            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return "DELTAS refused: no Ninefold component";
            if (!RM_NinefoldSettings.engineEnabled) return "DELTAS refused: engineEnabled is off";
            MethodInfo choice = AccessTools.Method(AccessTools.TypeByName("RimMandrake.RustCathedral.RM_WornBit"), "AnnounceChoice");
            FieldInfo toggle = AccessTools.Field(AccessTools.TypeByName("RimMandrake.RustCathedral.RM_RustCathedralSettings"), "wornBitPoliticsEnabled");
            if (choice == null || toggle == null) return "DELTAS refused: the Rust Cathedral seam is not loaded";
            God[] gods = (God[])Enum.GetValues(typeof(God));
            float[] saved = gods.Select(g => comp.GetSatiation(g)).ToArray();
            object wasOn = toggle.GetValue(null);
            var tags = new List<string>();
            var movers = new List<string>();
            GameComponent_Ninefold.DeltaWatcher = (g, amount, reason) => tags.Add(g + ">" + reason);
            try
            {
                foreach (God g in gods) comp.ProofSetSatiation(g, 0f);
                toggle.SetValue(null, politics);
                choice.Invoke(null, new object[] { null, keep });
                foreach (God g in gods)
                {
                    float moved = comp.GetSatiation(g);
                    if (moved != 0f) movers.Add(g + ":" + moved.ToString(CultureInfo.InvariantCulture));
                }
            }
            finally
            {
                GameComponent_Ninefold.DeltaWatcher = null;
                toggle.SetValue(null, wasOn);
                for (int i = 0; i < gods.Length; i++) comp.ProofSetSatiation(gods[i], saved[i]);
            }
            return "DELTAS keep=" + keep + "|politics=" + politics + "|gods=" + gods.Length
                + "|movers=" + (movers.Count == 0 ? "none" : string.Join(",", movers.ToArray()))
                + "|tags=" + (tags.Count == 0 ? "none" : string.Join(";", tags.ToArray()));
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
