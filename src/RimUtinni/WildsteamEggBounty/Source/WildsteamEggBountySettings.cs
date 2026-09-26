using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.WildsteamEggBounty
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Wildsteam Egg Bounty.
    //
    // One quest, RUT_WildsteamEggBounty, selected via native
    // rootSelectionWeight (no paired IncidentDef to gate, same shape as
    // EggReckoning). Gated the same way WreckedMachinesPatcher/
    // EggReckoningPatcher already mutate loaded def fields via a
    // [StaticConstructorOnStartup] patcher keyed off this settings toggle.
    //
    // Off degrades gracefully: the bounty quest can never be offered again;
    // one already granted is untouched. Shipped default: ON.
    public class WildsteamEggBountySettings : ModSettings
    {
        public static bool bountyEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref bountyEnabled, "bountyEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Wildsteam egg bounty quest enabled", ref bountyEnabled,
                "Off: the Wildsteam Clan's ollathrix-egg bounty trade request can never be "
              + "offered again. A bounty already granted to a colony is unaffected.");

            list.End();
        }
    }

    public class WildsteamEggBountyMod : Mod
    {
        public static WildsteamEggBountySettings settings;

        public WildsteamEggBountyMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WildsteamEggBountySettings>();
        }

        public override string SettingsCategory() => "Wildsteam Egg Bounty";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            WildsteamEggBountyPatcher.Apply();
        }
    }

    [StaticConstructorOnStartup]
    public static class WildsteamEggBountyPatcher
    {
        private static readonly QuestScriptDef BountyQuest =
            DefDatabase<QuestScriptDef>.GetNamedSilentFail("RUT_WildsteamEggBounty");

        private static readonly float BaseWeight =
            BountyQuest != null ? BountyQuest.rootSelectionWeight : 0f;

        static WildsteamEggBountyPatcher()
        {
            Apply();
        }

        public static void Apply()
        {
            if (BountyQuest != null)
            {
                BountyQuest.rootSelectionWeight = WildsteamEggBountySettings.bountyEnabled ? BaseWeight : 0f;
            }
        }
    }
}
