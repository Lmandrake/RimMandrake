using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipMemory
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ShipMemory.
    //
    // One mechanism: GameComponent_ShipMemory reveals the Memory-Core
    // containment building the moment the clan ties down a live beast,
    // stockpiles enough Bioferrite, or the Assailant dungeon signals it. A
    // master toggle lets a player who doesn't want the automatic reveal turn
    // it off; the Bioferrite stockpile threshold is the one hardcoded number
    // worth a slider.
    public class ShipMemorySettings : ModSettings
    {
        public static bool shipMemoryEnabled = true;
        public static float bioferriteThreshold = 50f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shipMemoryEnabled, "shipMemoryEnabled", true);
            Scribe_Values.Look(ref bioferriteThreshold, "bioferriteThreshold", 50f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Reveal the Memory-Core automatically", ref shipMemoryEnabled,
                "Off: the containment building is never auto-discovered by this mod's triggers "
              + "(taming a beast, stockpiling Bioferrite, or the Assailant dungeon signal).");
            list.Label("Bioferrite stockpile threshold: " + Mathf.RoundToInt(bioferriteThreshold));
            bioferriteThreshold = list.Slider(bioferriteThreshold, 10f, 200f);

            list.End();
        }
    }

    public class ShipMemoryMod : Mod
    {
        public static ShipMemorySettings settings;

        public ShipMemoryMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ShipMemorySettings>();
        }

        public override string SettingsCategory()
        {
            return "Ship Memory";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
