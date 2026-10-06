using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §6: the loot rows (slice 1) and the
    // wreck-field rows (slice 3: master, density, one checkbox per field key). The
    // wreck-fall and hazard rows arrive with their engines.
    // Defaults = shipped behaviour; all off = vanilla ShipChunk salvage.
    public class RM_WreckageSettings : ModSettings
    {
        public static bool salvageLoot = true;
        public static float lootGenerosity = 1f;      // PROVISIONAL range 0.25-3 (design §6)
        public static bool skillScalesRare = true;
        public static bool wreckFields = true;
        public static float wreckDensity = 1f;        // PROVISIONAL range 0-3 (design §6), new maps only
        // Field keys switched OFF, comma-separated (a plain string so the bridge's settings
        // tool can flip one field without a per-biome bool). Empty = every field on.
        public static string disabledFields = "";

        public static bool SalvageLootActive => salvageLoot;

        public static bool FieldDisabled(string key)
        {
            return !disabledFields.NullOrEmpty() && disabledFields.Split(',').Any(k => k.Trim() == key);
        }

        // A field runs when the master is on, its own key is not switched off here, and the
        // owning biome mod (if it registered a gate under the bare key) has its biome on.
        public static bool FieldActive(string key)
        {
            return wreckFields && !key.NullOrEmpty() && !FieldDisabled(key) && RM_MechanicGates.Enabled(key);
        }

        public static void SetFieldEnabled(string key, bool on)
        {
            var keys = new List<string>((disabledFields ?? "").Split(',').Select(k => k.Trim()).Where(k => k.Length > 0 && k != key));
            if (!on)
            {
                keys.Add(key);
            }
            disabledFields = string.Join(",", keys);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref salvageLoot, "salvageLoot", true);
            Scribe_Values.Look(ref lootGenerosity, "lootGenerosity", 1f);
            Scribe_Values.Look(ref skillScalesRare, "skillScalesRare", true);
            Scribe_Values.Look(ref wreckFields, "wreckFields", true);
            Scribe_Values.Look(ref wreckDensity, "wreckDensity", 1f);
            Scribe_Values.Look(ref disabledFields, "disabledFields", "");
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
            list.GapLine();
            list.CheckboxLabeled("RM_Wreckage_Setting_WreckFields".Translate(), ref wreckFields,
                "RM_Wreckage_Setting_WreckFields_Tip".Translate());
            if (wreckFields)
            {
                list.Label("RM_Wreckage_Setting_Density".Translate(wreckDensity.ToStringPercent()));
                wreckDensity = Mathf.Round(list.Slider(wreckDensity, 0f, 3f) * 20f) / 20f;
                foreach (string key in RM_GenStep_WreckField.AllFields().Select(f => f.settingsKey)
                             .Where(k => !k.NullOrEmpty()).Distinct().OrderBy(k => k))
                {
                    bool on = !FieldDisabled(key);
                    bool was = on;
                    list.CheckboxLabeled("RM_Wreckage_Setting_Field".Translate(key), ref on,
                        "RM_Wreckage_Setting_Field_Tip".Translate(key));
                    if (on != was)
                    {
                        SetFieldEnabled(key, on);
                    }
                }
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
            RM_MechanicGates.Register("Wreckage.fields", () => RM_WreckageSettings.wreckFields);
            // Per-field keys and their aliases (Scald.S6) need the GenStepDefs:
            // RM_WreckFieldStartup registers them after def load.
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
