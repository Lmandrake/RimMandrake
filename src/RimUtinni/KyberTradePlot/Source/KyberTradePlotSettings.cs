using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.KyberTradePlot
{
    // MOD_OPTIONS_RETROFIT_1 / KYBER_TRADE_PLOT_1 — Mod Settings for this mod.
    //
    // The mod ships two quest-content beats (RUT_KyberHomesteadVisit,
    // RUT_KyberDonationSmuggle), both fired only through their own baseChance-0
    // GiveQuest incidents (dev mode, a bridge call, or eventually the GM layer
    // once it exists — see the item file for what's still owed there). Neither
    // is worldgen-affecting and neither is on the natural quest pool, so the
    // one thing worth exposing is a single kill switch: whether either quest
    // can ever be offered at all.
    public class KyberTradePlotSettings : ModSettings
    {
        public static bool kyberTradePlotEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref kyberTradePlotEnabled, "kyberTradePlotEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Kyber trade plot content", ref kyberTradePlotEnabled,
                "The Homestead 'alleged Jedi' visit and the donate-and-smuggle rendezvous "
              + "quest that can follow a run of kyber sales. Both are triggered by dev mode, "
              + "a bridge call, or (once built) the GM layer — never by the ordinary quest "
              + "pool. Off: neither quest can ever be offered.");

            list.End();
        }
    }

    public class KyberTradePlotMod : Mod
    {
        public static KyberTradePlotSettings settings;

        public KyberTradePlotMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<KyberTradePlotSettings>();
        }

        public override string SettingsCategory()
        {
            return "Kyber Trade Plot";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
