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

    // WASTE_RUN_STUBS_1: what a branch leaves behind.
    public enum WasteEffect
    {
        DroppedOnEmpire,
        Frozen,
        Entombed,
        PropaneIgnited,
        SlimeNeutralized,
        SlimeBloomed,
        SlimeUnknown
    }

    public enum FlightGate
    {
        Allowed,
        Uncharted,
        Away
    }

    public static class WasteRunKernel
    {
        public const string QuestScriptDefName = "RUT_WasteRun";

        // Cargo the run disposes of: Biotech's Wastepack, the half-extracted core and the
        // Glowing Throat's cask (THROAT_CASK_ITEM_1); nothing else in a cask bay counts.
        public static readonly string[] WasteDefNames = { "Wastepack", "RM_HalfExtractedCore", "RUT_ThroatCask" };

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

        // ---- WASTE_RUN_STUBS_1 (all numbers PROVISIONAL, mine, not ruled) ----

        // What the chosen branch did. The quest XML names one per branch (Slime rolls three).
        // The history defs keep their own older names; the thought and the world effect key on this.
        public static string MoodDefName(WasteEffect e) { return "RUT_WasteRunMood_" + e; }

        // The ship has to be at the destination. Biome lists, because the frozen RUT_ def and the RM_
        // twin both exist until the planet is painted (the same pair WarLabCraterMutation scans).
        public const int EmpireReachTiles = 6;
        public const int LabReachTiles = 6;
        public const float ColdSideMaxTileTemp = -25f; // a tile's own yearly mean, so no biome paint is needed
        public static readonly string[] PropaneBiomes = { "RUT_PropaneLake", "RM_TheChill", "RM_ChillCrater" };
        public static readonly string[] StenchlandsBiomes = { "RM_Wastes", "RUT_Wastes" };
        public const string WarLabSitePart = "RUT_WarLabSite";

        // Allowed: fly-off satisfied or switched off. Uncharted: this planet has no such place yet, so
        // the destination stays open rather than locking the run (biomes on 0 tiles are the expected state
        // until the one paint). Away: the place exists and the ship is not there.
        public static FlightGate GateFlight(bool required, bool targetExists, bool atTarget)
        {
            if (!required || atTarget) return FlightGate.Allowed;
            return targetExists ? FlightGate.Away : FlightGate.Uncharted;
        }

        public static bool MayCommit(FlightGate g) { return g != FlightGate.Away; }

        public static string AwayReason(WasteDestination d)
        {
            switch (d)
            {
                case WasteDestination.DropOnEmpire: return "fly within " + EmpireReachTiles + " tiles of an Imperial settlement";
                case WasteDestination.FreezeColdSide: return "fly to the cold side";
                case WasteDestination.EntombAssailants: return "fly to the Assailants";
                case WasteDestination.IgnitePropaneLake: return "fly to the propane lakes";
                default: return "fly to the Stenchlands";
            }
        }

        // World effects of the Slime pour, spread around the ship's tile with a linear falloff.
        public const int SlimeReachTiles = 12;
        public const float SlimeNeutralizeDelta = -0.5f;
        public const float SlimeBloomDelta = 0.4f;
        public const int SlimeFalloutDays = 5;
        public const int UnknownMinDays = 15;
        public const int UnknownMaxDays = 45;

        public static float SlimePollution(float current, float delta, float dist, float reach)
        {
            if (dist > reach) return current;
            float next = current + delta * (1f - dist / (reach + 1f));
            return next < 0f ? 0f : next > 1f ? 1f : next;
        }

        // "Genuinely unknown": the third outcome is settled later, by a coin, down the pit.
        public static WasteEffect ResolveUnknown(float roll01)
        {
            return roll01 < 0.5f ? WasteEffect.SlimeNeutralized : WasteEffect.SlimeBloomed;
        }

        public static bool UnknownDue(int dueTick, int nowTick) { return dueTick >= 0 && nowTick >= dueTick; }

        public static bool IsSlime(WasteEffect e)
        {
            return e == WasteEffect.SlimeNeutralized || e == WasteEffect.SlimeBloomed || e == WasteEffect.SlimeUnknown;
        }

        // ---- THROAT_CASK_ITEM_1 (all thresholds PROVISIONAL, mine, not ruled) ----
        public const string ThroatCaskDefName = "RUT_ThroatCask";

        // The cask is waste for the run (it joins the cask bay's cargo).
        public static bool ThroatCaskActive(bool master, bool caskEnabled) { return master && caskEnabled; }

        // Dose factor at a pawn: falls linearly to 0 one cell past the radius; a sealed chamber only mutes it.
        public static float ThroatDose(float toxicFactor, float dist, float radius, bool shielded, float shieldedFactor)
        {
            if (dist > radius) return 0f;
            float falloff = 1f - dist / (radius + 1f);
            return toxicFactor * falloff * (shielded ? shieldedFactor : 1f);
        }

        // Mood stage from ticks the cask has spent in the world: 0 first day, 1 up to 3 days, 2 beyond.
        public static int NearStage(int ticksPresent)
        {
            return ticksPresent < 60000 ? 0 : ticksPresent < 180000 ? 1 : 2;
        }

        // Die-off chance per rare tick climbs with presence: x1 at start, x4 after 5 days (300000 ticks), capped there.
        public static float DieOffChance(float baseChance, int ticksPresent)
        {
            float growth = 1f + 3f * System.Math.Min(1f, ticksPresent / 300000f);
            return System.Math.Min(1f, baseChance * growth);
        }

        public static bool FaultDue(int ticksSinceFault, int interval) { return interval > 0 && ticksSinceFault >= interval; }

        // The burst triggers: the carrier took harm since the last look, or the cask is burning.
        public static bool ShouldBurst(bool carrierHarmed, bool burning) { return carrierHarmed || burning; }
    }
}
