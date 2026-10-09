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

        // SHRUBLAND_SCRAPNEST_BIRDS_1 — the scrap-nest bird's hoarding drive:
        // the job giver, the nest-building fallback and the haul job all read
        // this. Off, the bird keeps every stat, its flight and its eggs and
        // simply stops collecting — and any nest already on the map stays put
        // and keeps restocking, because that half is a pure vanilla
        // CompProperties_Spawner this flag does not reach.
        public static bool scrapHoardingEnabled = true;

        // The mutagenic norphea's toxin dependence (ToxinDependence.cs): the
        // need rises on polluted ground or with toxic buildup and falls
        // elsewhere, with a lethal withdrawal stage. Off: the need is held full.
        public static bool toxinDependenceEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref metalEatingEnabled, "metalEatingEnabled", true);
            Scribe_Values.Look(ref innateAbilitiesEnabled, "innateAbilitiesEnabled", true);
            Scribe_Values.Look(ref scrapHoardingEnabled, "scrapHoardingEnabled", true);
            Scribe_Values.Look(ref toxinDependenceEnabled, "toxinDependenceEnabled", true);
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

            list.Gap();

            list.CheckboxLabeled(
                "Scrap-hoarding birds",
                ref scrapHoardingEnabled,
                "Scrap-nest birds build nests in the wild and carry loose scrap, components and precious metals back to them. They never take from inside your base. Off: they forage and fly like any other bird, and existing nests still slowly accumulate scrap on their own.");

            list.Gap();

            list.CheckboxLabeled(
                "Toxin-dependent creatures",
                ref toxinDependenceEnabled,
                "The mutagenic norphea needs polluted ground or toxic buildup to stay well, and sickens and can die in withdrawal on clean land. Off: its dependence is always satisfied.");

            list.End();
        }
    }

    public class RSW_BeastMechanicsMod : Mod
    {
        public RSW_BeastMechanicsMod(ModContentPack content) : base(content)
        {
            GetSettings<RSW_BeastMechanicsSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rsw.swbestiary.beastmechanics"), typeof(RSW_BeastMechanicsMod).Assembly, "RimStarWars.SWBestiary.BeastMechanics");
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
