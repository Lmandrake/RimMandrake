using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // PORTED_BEAST_MECHANICS_REBUILD_1 — Mod Settings for the SWBestiary
    // BeastMechanics assembly (RimMandrakeBeastMechanicsRSW.dll), and the
    // Harmony instance the one prefix in this assembly is patched through.
    //
    // Precedent and reasoning for a separate settings entry rather than one
    // shared with Livestock/Ikee: RSW_LivestockSettings.cs's own header.
    // Three DLLs ship inside the SWBestiary folder and none of them
    // references the others, so each carries its own Mod class.
    //
    // Per the standing rule that every mod ships real Mod Settings:
    // defaults are the shipped behaviour, and every mechanic here degrades
    // gracefully when switched off (the creature simply keeps its stats and
    // loses the gimmick, which is exactly the state the port shipped in).
    // ════════════════════════════════════════════════════════════════════
    public class RSW_BeastMechanicsSettings : ModSettings
    {
        // Ferroclaw's steel diet: the comp, the eat job and the block on
        // seeking ordinary food all read this.
        public static bool metalEatingEnabled = true;

        // Voltmaw's plasma volley and cindermite's fuel spew: whether the
        // innate ability is granted at all. Already-granted abilities are
        // left alone, so turning this off stops new creatures gaining one.
        public static bool innateAbilitiesEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref metalEatingEnabled, "metalEatingEnabled", true);
            Scribe_Values.Look(ref innateAbilitiesEnabled, "innateAbilitiesEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled(
                "Metal-eating creatures",
                ref metalEatingEnabled,
                "The ferroclaw feeds on steel and steel slag instead of grazing, and digs slag up when a map has none. Off: it grazes like any other animal.");

            list.Gap();

            list.CheckboxLabeled(
                "Innate creature abilities",
                ref innateAbilitiesEnabled,
                "The voltmaw fires a plasma volley and the cindermite sprays raw chemfuel. Off: neither gains its ranged attack.");

            list.End();
        }
    }

    public class RSW_BeastMechanicsMod : Mod
    {
        public RSW_BeastMechanicsMod(ModContentPack content) : base(content)
        {
            GetSettings<RSW_BeastMechanicsSettings>();
            new Harmony("mandrake.rsw.swbestiary.beastmechanics").PatchAll();
        }

        public override string SettingsCategory()
        {
            return "RimMandrake: SW — Bestiary (beast mechanics)";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            GetSettings<RSW_BeastMechanicsSettings>().DoWindowContents(inRect);
        }
    }
}
