using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniStatues
{
    // UTINNI_STATUES_SKELETON_BUILD_1 + SHKAAR_FLAME_IDOL_BUILD_1 — Mod Settings, statue_mods_spec.md §1.5
    // (a) carving on/off, (c) Sh'kaar's idol burns, (b) Sumpgas fuels it (row shown only in the campaign).
    public class UtinniStatuesSettings : ModSettings
    {
        public static bool statuesCraftable = true;
        public static bool shkaarIdolBurns = true;
        public static bool sumpgasFuelsIdol = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref statuesCraftable, "statuesCraftable", true);
            Scribe_Values.Look(ref shkaarIdolBurns, "shkaarIdolBurns", true);
            Scribe_Values.Look(ref sumpgasFuelsIdol, "sumpgasFuelsIdol", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Utinni statues can be carved", ref statuesCraftable,
                "On: the sculptor's table offers the Utinni votive, statue and grand statue; once one is placed, "
              + "its \"Dedicate\" button chooses which god or votive it honours. Off: the table stops offering "
              + "them. Statues already made stay. Takes effect after a restart; not worldgen.");
            list.CheckboxLabeled("Sh'kaar's idol burns", ref shkaarIdolBurns,
                "On: dedicating a grand statue to Sh'kaar rebuilds it as a burning idol. It needs fuel, glows, and "
              + "a flame rises from its sun-disc crown. Off: a new grand idol of Sh'kaar stays cold. An idol already "
              + "burning keeps burning until rededicated.");
            if (ModsConfig.IsActive("mandrake.rut.patches"))
            {
                list.CheckboxLabeled("Sumpgas fuels the idol", ref sumpgasFuelsIdol,
                    "On: the burning idol takes Sumpgas, the campaign's fuel. Off: it takes chemfuel. "
                  + "Takes effect after a restart.");
            }
            list.End();
        }
    }

    public class UtinniStatuesMod : Mod
    {
        public static UtinniStatuesSettings settings;

        public UtinniStatuesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<UtinniStatuesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Utinni Statues";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>Applies "Utinni statues can be carved" OFF at startup: the statue recipes leave every
    /// workbench. Nothing else changes, so all-off is a mod that does nothing.</summary>
    [StaticConstructorOnStartup]
    public static class UtinniStatuesStartup
    {
        public static readonly int RecipesWithdrawn;

        static UtinniStatuesStartup()
        {
            ApplyIdolFuel();
            if (UtinniStatuesSettings.statuesCraftable)
            {
                return;
            }
            FieldInfo cache = typeof(ThingDef).GetField("allRecipesCached", BindingFlags.NonPublic | BindingFlags.Instance);
            foreach (RecipeDef r in DefDatabase<RecipeDef>.AllDefsListForReading)
            {
                ThingDef made = r.ProducedThingDef;
                if (made == null || made.GetCompProperties<CompProperties_StatuePicker>() == null)
                {
                    continue;
                }
                List<ThingDef> users = r.recipeUsers;
                if (users != null)
                {
                    foreach (ThingDef u in users)
                    {
                        u.recipes?.Remove(r);
                        cache?.SetValue(u, null);
                    }
                    users.Clear();
                }
                RecipesWithdrawn++;
            }
            Log.Message("[UtinniStatues] carving switched off: " + RecipesWithdrawn + " statue recipe(s) withdrawn.");
        }

        /// <summary>Statue spec §2.3/§1.5(b): in the campaign (mandrake.rut.patches loaded) the burning idol takes
        /// Sumpgas; otherwise, or with the setting off, the chemfuel filter in its XML stands (ruling R4).</summary>
        private static void ApplyIdolFuel()
        {
            ThingDef idol = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_StatueGrand_Shkaar");
            ThingDef sumpgas = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_Sumpgas");
            CompProperties_Refuelable fuel = idol?.GetCompProperties<CompProperties_Refuelable>();
            if (fuel == null || sumpgas == null || !UtinniStatuesSettings.sumpgasFuelsIdol)
            {
                return;
            }
            ThingFilter f = new ThingFilter();
            f.SetAllow(sumpgas, true);
            fuel.fuelFilter = f;
            fuel.fuelLabel = "Sumpgas";
            fuel.fuelGizmoLabel = "Sumpgas";
            fuel.outOfFuelMessage = "Idol of Sh'kaar out of Sumpgas";
        }
    }
}
