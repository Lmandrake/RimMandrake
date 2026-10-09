using System.Collections.Generic;

namespace RimMandrake.Utinni.WasteRun
{
    // WARCASKET_WASTE_RUN_REMAINDER_1. Pure logic, no engine types, so the
    // offline self-test (validation.py) and the game share one definition.
    public enum WasteDestination
    {
        DropOnEmpire,
        FreezeColdSide,
        EntombAssailants,
        IgnitePropaneLake,
        SlimeExperiment
    }

    public static class WasteRunKernel
    {
        public const string QuestScriptDefName = "RUT_WasteRun";

        // Cargo the run disposes of. Biotech's Wastepack and the half-extracted
        // core are the only waste; nothing else in a cask bay counts. The Stenchlands
        // Throat cask is NOT listed: its item is still unspecified (WASTE_RUN_STUBS).
        public static readonly string[] WasteDefNames = { "Wastepack", "RM_HalfExtractedCore" };

        public static bool IsWaste(string defName)
        {
            for (int i = 0; i < WasteDefNames.Length; i++)
            {
                if (WasteDefNames[i] == defName) return true;
            }
            return false;
        }

        // The quest listens on "Quest<id>.<name>" (Quest.InitiateSignal = "Quest{id}.Initiate").
        public static string SignalName(WasteDestination d)
        {
            return "WasteDest_" + d;
        }

        public static string FullSignal(int questId, WasteDestination d)
        {
            return "Quest" + questId + "." + SignalName(d);
        }

        public static string Label(WasteDestination d)
        {
            switch (d)
            {
                case WasteDestination.DropOnEmpire: return "Drop it on the Empire";
                case WasteDestination.FreezeColdSide: return "Freeze it on the cold side";
                case WasteDestination.EntombAssailants: return "Entomb it on the Assailants";
                case WasteDestination.IgnitePropaneLake: return "Sink it in the propane lakes";
                default: return "Pour the Slime experiment down the Stenchlands";
            }
        }

        // Cargo count helper: how many waste stacks in a def-name sequence.
        public static int CountWaste(IEnumerable<string> defNames)
        {
            int n = 0;
            foreach (string s in defNames)
            {
                if (IsWaste(s)) n++;
            }
            return n;
        }

        // The run is offerable only with real cargo and the master toggle on.
        public static bool CanOffer(bool masterEnabled, bool offerEnabled, int wasteStacks, bool runAlreadyActive)
        {
            return masterEnabled && offerEnabled && wasteStacks > 0 && !runAlreadyActive;
        }
    }
}
