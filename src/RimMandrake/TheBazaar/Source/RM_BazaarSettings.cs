using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 / "every mod ships Mod Settings". The rule this
    // file follows: a toggle lands in the same slice as the mechanic it
    // gates, never ahead of it. BAZAAR_PRICE_ENGINE_1 (slice 2) adds the
    // economy and intel toggles below because their mechanics now exist
    // (RM_BazaarEconomy, the GetPriceFor postfix, the intel gates). Haggle,
    // crit spoils, banter, broker tab, wishlist flash and grid density
    // (design §7) still arrive with their own slices.
    //
    // Defaults = shipped behaviour. All economy/intel off = vanilla prices
    // and a plain grid.
    // ════════════════════════════════════════════════════════════════════
    public class RM_BazaarSettings : ModSettings
    {
        /// <summary>Master switch for the settlement price economy. Off =
        /// flat ×1.0 everywhere: the GetPriceFor postfix returns at its
        /// first check, and intel columns read "no data".</summary>
        public static bool economyEnabled = true;

        /// <summary>Seed settlements that no authored rule touches from a
        /// stable hash of (faction, biome, tile) — mild locality on public
        /// worlds with no authored tags (owner-ruled, design §3). Authored
        /// rules always win over it on the keys they set.</summary>
        public static bool proceduralLocality = true;

        /// <summary>Intel L1 — price vs typical (Social 3+).</summary>
        public static bool intelPriceContext = true;

        /// <summary>Intel L2 — good-deal outlier badges (Social 5+).</summary>
        public static bool intelGoodDeals = true;

        /// <summary>Intel L3 — local economy (Social 7+).</summary>
        public static bool intelLocalEconomy = true;

        /// <summary>Intel L4 — scarcity from the trader-visit log (Social 9+).</summary>
        public static bool intelScarcity = true;

        /// <summary>Protocol-droid modules (D1..D4) unlock their layers. Off
        /// = modules are inert items; Social layers are unaffected.</summary>
        public static bool intelModules = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref economyEnabled, "economyEnabled", true);
            Scribe_Values.Look(ref proceduralLocality, "proceduralLocality", true);
            Scribe_Values.Look(ref intelPriceContext, "intelPriceContext", true);
            Scribe_Values.Look(ref intelGoodDeals, "intelGoodDeals", true);
            Scribe_Values.Look(ref intelLocalEconomy, "intelLocalEconomy", true);
            Scribe_Values.Look(ref intelScarcity, "intelScarcity", true);
            Scribe_Values.Look(ref intelModules, "intelModules", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard();
            list.Begin(inRect);
            Text.Font = GameFont.Medium;
            list.Label("The Bazaar");
            Text.Font = GameFont.Small;
            list.GapLine();

            list.Label("Price economy");
            list.CheckboxLabeled("Dynamic settlement prices", ref economyEnabled,
                "Each settlement prices goods by what it has and lacks (a desert town pays more for water), "
                + "drifting day to day within ×0.25–×4.0. Applies ONLY inside The Bazaar's trade window; "
                + "colony wealth, raid points and caravan values are never touched. Off = vanilla prices.");
            list.CheckboxLabeled("Procedural locality for untagged settlements", ref proceduralLocality,
                "Settlements no authored rule describes get a mild, stable local price character from their "
                + "faction, biome and tile. Off = those settlements trade at ×1.0. Takes effect for settlements "
                + "first seen after the change.");

            list.GapLine();
            list.Label("Trade intel (gated by the negotiator's Social skill)");
            list.CheckboxLabeled("L1 price context (Social 3+)", ref intelPriceContext,
                "Shows each good's price against what is typical here.");
            list.CheckboxLabeled("L2 good-deal badges (Social 5+)", ref intelGoodDeals,
                "Flags prices far from typical, in either direction.");
            list.CheckboxLabeled("L3 local economy (Social 7+)", ref intelLocalEconomy,
                "Shows what this settlement pays relative to the norm.");
            list.CheckboxLabeled("L4 scarcity (Social 9+)", ref intelScarcity,
                "Flags goods only this trader has carried recently.");
            list.CheckboxLabeled("Protocol-droid intel modules", ref intelModules,
                "Modules fitted to a functional protocol droid in the party (or at a comms console) unlock "
                + "deeper intel. Off = modules do nothing.");

            list.GapLine();
            list.Label("The trade window itself is not replaced yet (the WindowStack.Add intercept is a later "
                     + "slice), so these settings have no visible effect until it lands.");
            list.End();
        }
    }

    public class RM_BazaarMod : Mod
    {
        public static RM_BazaarSettings settings;

        public RM_BazaarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_BazaarSettings>();
        }

        public override string SettingsCategory() => "The Bazaar";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
