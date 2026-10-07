using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_PRICE_ENGINE_1 — design §4 intel layers L1..L4 as grid plugins.
    /// Each worker gates on its RM_BazaarIntelLayerDef through
    /// <see cref="RM_BazaarIntel"/> and reads the engine through
    /// <see cref="RM_BazaarEconomy.BucketFor"/> — the second (and last) of
    /// the engine's two read paths. They draw nothing until the grid body
    /// (BAZAAR_WINDOW_GRID_1) iterates RM_BazaarColumnDef/BadgeDef.
    /// </summary>
    public static class RM_BazaarIntelMath
    {
        /// <summary>Relative distance from typical that counts as a good deal (L2).</summary>
        public const float GoodDealThreshold = 0.15f;

        /// <summary>L4 window: "only source of X in 30 days".</summary>
        public const int ScarcityDays = 30;

        public static RM_BazaarBucket Bucket(Tradeable t, RM_BazaarSession s)
        {
            if (t == null || s == null) return null;
            return RM_BazaarEconomy.Get()?.BucketFor(s.economyTile, t.ThingDef);
        }

        /// <summary>(current / typical) - 1, or null without data.</summary>
        public static float? VsTypical(Tradeable t, RM_BazaarSession s)
        {
            RM_BazaarBucket b = Bucket(t, s);
            if (b == null) return null;
            float typical = b.TypicalMultiplier;
            if (typical <= 0f) return null;
            return b.multiplier / typical - 1f;
        }
    }

    /// <summary>L1 (Social 3+): arrow + % vs typical.</summary>
    public class BazaarColumnWorker_PriceContext : BazaarColumnWorker
    {
        public const string Layer = "RM_BazaarIntel_L1_PriceContext";

        public override bool VisibleFor(RM_BazaarSession session) => RM_BazaarIntel.IsUnlocked(Layer, session);

        public override void DrawCell(Rect rect, Tradeable tradeable, RM_BazaarSession session)
        {
            float? d = RM_BazaarIntelMath.VsTypical(tradeable, session);
            if (!d.HasValue) return;
            string arrow = d.Value > 0.005f ? "▲" : (d.Value < -0.005f ? "▼" : "•");
            TextAnchor old = Text.Anchor;
            Text.Anchor = TextAnchor.MiddleCenter;
            Widgets.Label(rect, arrow + " " + Mathf.Abs(d.Value).ToStringPercent("0"));
            Text.Anchor = old;
        }

        public override string GetTooltip(Tradeable tradeable, RM_BazaarSession session)
        {
            float? d = RM_BazaarIntelMath.VsTypical(tradeable, session);
            if (!d.HasValue) return "No price history for this here.";
            return "Here, this is " + Mathf.Abs(d.Value).ToStringPercent("0")
                + (d.Value >= 0f ? " above" : " below") + " what it usually fetches.";
        }

        public override int Compare(Tradeable a, Tradeable b)
        {
            RM_BazaarSession s = RM_BazaarSession.Current;
            return (RM_BazaarIntelMath.VsTypical(a, s) ?? 0f).CompareTo(RM_BazaarIntelMath.VsTypical(b, s) ?? 0f);
        }
    }

    /// <summary>L3 (Social 7+): what this settlement pays relative to the norm.</summary>
    public class BazaarColumnWorker_LocalEconomy : BazaarColumnWorker
    {
        public const string Layer = "RM_BazaarIntel_L3_LocalEconomy";

        public override bool VisibleFor(RM_BazaarSession session) => RM_BazaarIntel.IsUnlocked(Layer, session);

        public override void DrawCell(Rect rect, Tradeable tradeable, RM_BazaarSession session)
        {
            RM_BazaarBucket b = RM_BazaarIntelMath.Bucket(tradeable, session);
            if (b == null) return;
            TextAnchor old = Text.Anchor;
            Text.Anchor = TextAnchor.MiddleCenter;
            Widgets.Label(rect, "×" + b.multiplier.ToString("0.0#"));
            Text.Anchor = old;
        }

        public override string GetTooltip(Tradeable tradeable, RM_BazaarSession session)
        {
            RM_BazaarBucket b = RM_BazaarIntelMath.Bucket(tradeable, session);
            if (b == null) return "This place prices it like anywhere else.";
            return "This settlement pays ×" + b.multiplier.ToString("0.0#") + " the usual for this."
                + (b.multiplier >= 1.3f ? " A good place to sell." : (b.multiplier <= 0.77f ? " A good place to buy." : ""));
        }

        public override int Compare(Tradeable a, Tradeable b)
        {
            RM_BazaarSession s = RM_BazaarSession.Current;
            float ma = RM_BazaarIntelMath.Bucket(a, s)?.multiplier ?? 1f;
            float mb = RM_BazaarIntelMath.Bucket(b, s)?.multiplier ?? 1f;
            return ma.CompareTo(mb);
        }
    }

    /// <summary>L2 (Social 5+): outlier flags, both directions.</summary>
    [StaticConstructorOnStartup]
    public class BazaarBadgeWorker_GoodDeal : BazaarBadgeWorker
    {
        public const string Layer = "RM_BazaarIntel_L2_GoodDeals";
        private static readonly Texture2D Cheap = SolidColorMaterials.NewSolidColorTexture(new Color(0.35f, 0.75f, 0.35f));
        private static readonly Texture2D Dear = SolidColorMaterials.NewSolidColorTexture(new Color(0.85f, 0.65f, 0.25f));

        public override bool VisibleFor(RM_BazaarSession session) => RM_BazaarIntel.IsUnlocked(Layer, session);

        public override RM_BazaarBadge? GetBadge(Tradeable tradeable, RM_BazaarSession session)
        {
            if (!VisibleFor(session)) return null;
            float? d = RM_BazaarIntelMath.VsTypical(tradeable, session);
            if (!d.HasValue || Mathf.Abs(d.Value) < RM_BazaarIntelMath.GoodDealThreshold) return null;
            return d.Value < 0f
                ? new RM_BazaarBadge(Cheap, "Cheap here right now: " + (-d.Value).ToStringPercent("0") + " under typical. Buy.")
                : new RM_BazaarBadge(Dear, "Dear here right now: " + d.Value.ToStringPercent("0") + " over typical. Sell.");
        }
    }

    /// <summary>L4 (Social 9+): only this trader has carried it recently.</summary>
    [StaticConstructorOnStartup]
    public class BazaarBadgeWorker_Scarcity : BazaarBadgeWorker
    {
        public const string Layer = "RM_BazaarIntel_L4_Scarcity";
        private static readonly Texture2D Icon = SolidColorMaterials.NewSolidColorTexture(new Color(0.6f, 0.45f, 0.85f));

        public override bool VisibleFor(RM_BazaarSession session) => RM_BazaarIntel.IsUnlocked(Layer, session);

        public override RM_BazaarBadge? GetBadge(Tradeable tradeable, RM_BazaarSession session)
        {
            if (!VisibleFor(session) || tradeable?.ThingDef == null) return null;
            // Only goods the TRADER is offering can be scarce from this trader.
            if (tradeable.CountHeldBy(Transactor.Trader) <= 0) return null;
            RM_BazaarEconomy econ = RM_BazaarEconomy.Get();
            if (econ == null) return null;
            int n = econ.TradersCarrying(tradeable.ThingDef, RM_BazaarIntelMath.ScarcityDays);
            if (n != 1) return null;
            return new RM_BazaarBadge(Icon, "The only trader seen carrying this in "
                + RM_BazaarIntelMath.ScarcityDays + " days.");
        }
    }
}
