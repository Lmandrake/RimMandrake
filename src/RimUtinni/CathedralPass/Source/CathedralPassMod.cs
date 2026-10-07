using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    // MOD_OPTIONS_RETROFIT_1 rule: one kill switch. The pass is a single mechanism
    // with no tuning number worth exposing — its scope is ruled, not a knob.
    public class CathedralPassSettings : ModSettings
    {
        public static bool cathedralPassEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cathedralPassEnabled, "cathedralPassEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Cathedral mechanoid pass", ref cathedralPassEnabled,
                "Clan members granted the Cathedral's pass are not treated as hostile by the "
              + "mechanoid faction's machines, on Rust Cathedral maps only. Off: the pass "
              + "flag does nothing anywhere and the machines treat everyone as vanilla does.");
            list.End();
        }
    }

    public class CathedralPassMod : Mod
    {
        public static CathedralPassSettings settings;

        public CathedralPassMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<CathedralPassSettings>();
            new Harmony("mandrake.rut.cathedralpass").PatchAll();
        }

        public override string SettingsCategory()
        {
            return "Cathedral Pass";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
