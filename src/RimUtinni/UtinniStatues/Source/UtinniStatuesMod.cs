using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniStatues
{
    // UTINNI_STATUES_SKELETON_BUILD_1 — Mod Settings, statue_mods_spec.md §1.5(a). (b) and (c) belong to the
    // flame steps (SHKAAR_FLAME_IDOL_BUILD_1) and are not shown until something reads them.
    public class UtinniStatuesSettings : ModSettings
    {
        public static bool statuesCraftable = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref statuesCraftable, "statuesCraftable", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Utinni statues can be carved", ref statuesCraftable,
                "On: the sculptor's table offers the Utinni votive, statue and grand statue; once one is placed, "
              + "its \"Dedicate\" button chooses which god or votive it honours. Off: the table stops offering "
              + "them. Statues already made stay. Takes effect after a restart; not worldgen.");
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
    }
}
