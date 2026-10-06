using System.Runtime.CompilerServices;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §6 (the loot rows only; the
    // wreck-field, density and wreck-fall rows arrive with their engines).
    // Defaults = shipped behaviour; all off = vanilla ShipChunk salvage.
    public class RM_WreckageSettings : ModSettings
    {
        public static bool salvageLoot = true;
        public static float lootGenerosity = 1f;      // PROVISIONAL range 0.25-3 (design §6)
        public static bool skillScalesRare = true;

        public static bool SalvageLootActive => salvageLoot;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref salvageLoot, "salvageLoot", true);
            Scribe_Values.Look(ref lootGenerosity, "lootGenerosity", 1f);
            Scribe_Values.Look(ref skillScalesRare, "skillScalesRare", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            var list = new Listing_Standard();
            list.Begin(inRect);
            list.CheckboxLabeled("RM_Wreckage_Setting_SalvageLoot".Translate(), ref salvageLoot,
                "RM_Wreckage_Setting_SalvageLoot_Tip".Translate());
            if (salvageLoot)
            {
                list.Label("RM_Wreckage_Setting_Generosity".Translate(lootGenerosity.ToStringPercent()));
                lootGenerosity = Mathf.Round(list.Slider(lootGenerosity, 0.25f, 3f) * 20f) / 20f;
                list.CheckboxLabeled("RM_Wreckage_Setting_SkillScales".Translate(), ref skillScalesRare,
                    "RM_Wreckage_Setting_SkillScales_Tip".Translate());
            }
            list.End();
        }
    }

    public class RM_WreckageMod : Mod
    {
        public static RM_WreckageSettings settings;

        public RM_WreckageMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WreckageSettings>();
            // Composed beside EnvironmentalHazards in mandrake.rm.biomes, so
            // the shared gate registry is always co-present (the same reasoning
            // as RM_TerminalBiomesMod's unconditional registration).
            RegisterMechanicGates();
            new Harmony("mandrake.rm.wreckage").PatchAll(typeof(RM_WreckageMod).Assembly);
        }

        [MethodImpl(MethodImplOptions.NoInlining)]
        private static void RegisterMechanicGates()
        {
            RM_MechanicGates.Register("Wreckage.loot", () => RM_WreckageSettings.salvageLoot);
            RM_MechanicGates.Register("Wreckage.skillScalesRare", () => RM_WreckageSettings.skillScalesRare);
        }

        public override string SettingsCategory()
        {
            return "RM_Wreckage_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
