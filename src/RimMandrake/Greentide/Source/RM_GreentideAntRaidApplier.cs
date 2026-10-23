using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_ANTS_MOVE_TO_FREE_TIER: the giant ants' Mod Settings, written onto the live defs (no Harmony; this mod
    // ships none). Run once at startup and again whenever the settings window closes, so both settings act [now].
    //
    // Raids off. MEASURED from decompiled 1.6 (RimSage, 2026-10-22): IncidentWorker_RaidEnemy.FactionCanBeGroupSource
    // refuses a faction unless some RaidStrategyDef's Worker.CanUseWith(parms) is true, and
    // RaidStrategyWorker.CanUseWith returns false first thing when faction.def.disallowedRaidStrategies contains that
    // strategy. Listing every strategy there therefore takes the ant faction out of every raid pick, the desperate pass
    // included (it calls the same FactionCanBeGroupSource). Raids on restores the list the def shipped with.
    //
    // Strength. A raid buys pawns with its points at each kind's combatPower, so dividing the two ant kinds'
    // combatPower by the strength multiplier sends that many times more ants for the same points (2x = twice the
    // ants). The storyteller's points are untouched; this is how hard the ants hit for what they cost it.
    [StaticConstructorOnStartup]
    public static class RM_GreentideAntRaidApplier
    {
        public const string FactionName = "RM_GreentideAntFaction";
        private static readonly string[] KindNames = { "RM_GreentideAnt", "RM_GreentideAntSoldier" };

        private static List<RaidStrategyDef> shippedDisallowed;
        private static Dictionary<string, float> shippedCombatPower;

        static RM_GreentideAntRaidApplier()
        {
            Apply();
        }

        public static void Apply()
        {
            FactionDef faction = DefDatabase<FactionDef>.GetNamedSilentFail(FactionName);
            if (faction == null)
            {
                return;
            }
            if (shippedCombatPower == null)
            {
                shippedDisallowed = faction.disallowedRaidStrategies == null ? null : new List<RaidStrategyDef>(faction.disallowedRaidStrategies);
                shippedCombatPower = new Dictionary<string, float>();
                foreach (string n in KindNames)
                {
                    PawnKindDef k = DefDatabase<PawnKindDef>.GetNamedSilentFail(n);
                    if (k != null)
                    {
                        shippedCombatPower[n] = k.combatPower;
                    }
                }
            }

            faction.disallowedRaidStrategies = RM_GreentideSettings.antRaidsEnabled
                ? (shippedDisallowed == null ? null : new List<RaidStrategyDef>(shippedDisallowed))
                : new List<RaidStrategyDef>(DefDatabase<RaidStrategyDef>.AllDefsListForReading);

            float strength = RM_GreentideSettings.antRaidStrength < 0.1f ? 0.1f : RM_GreentideSettings.antRaidStrength;
            foreach (KeyValuePair<string, float> kv in shippedCombatPower)
            {
                PawnKindDef k = DefDatabase<PawnKindDef>.GetNamedSilentFail(kv.Key);
                if (k != null)
                {
                    k.combatPower = kv.Value / strength;
                }
            }
        }

        // jawa/static_call proof: re-apply the current settings (what closing the settings window does; a bridge write
        // to a settings field does not close the window), then read the live defs back.
        public static string ProofApply(string unused)
        {
            Apply();
            return ProofState(unused);
        }

        // jawa/static_call proof: what the live defs say now. "raids=on|off strategiesBlocked=N/M power=a,b".
        public static string ProofState(string unused)
        {
            FactionDef faction = DefDatabase<FactionDef>.GetNamedSilentFail(FactionName);
            if (faction == null)
            {
                return "FAIL no " + FactionName;
            }
            int blocked = faction.disallowedRaidStrategies?.Count ?? 0;
            int all = DefDatabase<RaidStrategyDef>.DefCount;
            List<string> power = new List<string>();
            foreach (string n in KindNames)
            {
                PawnKindDef k = DefDatabase<PawnKindDef>.GetNamedSilentFail(n);
                power.Add(k == null ? "missing" : k.combatPower.ToString("0.##"));
            }
            return "raids=" + (blocked >= all && all > 0 ? "off" : "on") + " strategiesBlocked=" + blocked + "/" + all
                + " power=" + string.Join(",", power);
        }
    }
}
