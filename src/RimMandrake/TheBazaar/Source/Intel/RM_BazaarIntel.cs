using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_PRICE_ENGINE_1 — design §4. Evaluates <see cref="RM_BazaarIntelLayerDef"/>
    /// gates for a session. Columns and badges call <see cref="IsUnlocked"/>
    /// from their VisibleFor/GetBadge; nothing else decides gating.
    ///
    /// Social layers: negotiator's Social level ≥ minSocialSkill, minus the
    /// D4 almanac's reduction when that module is present.
    ///
    /// Module layers (owner 2026-09-20): the module hediff on a FUNCTIONAL
    /// protocol droid. "Functional" reuses Droidworks' own
    /// <c>Patch_ProtocolTradeAdvantage.IsAvailableProtocolDroid</c> by
    /// reflection (design: "Reuse it; do not write a second") — so this RM-tier
    /// mod takes no hard dependency on the RSW-tier Droidworks, and without it
    /// no droid is ever functional and every module layer stays locked.
    /// Presence: the negotiator's caravan, else every player pawn on the
    /// negotiator's map — which covers both "in the trading party" and "at the
    /// colony while the negotiator works the comms console" (design §4).
    /// </summary>
    public static class RM_BazaarIntel
    {
        private static RM_BazaarSession cachedFor;
        private static readonly Dictionary<RM_BazaarIntelLayerDef, bool> cache = new Dictionary<RM_BazaarIntelLayerDef, bool>();
        private static HashSet<HediffDef> presentModules;

        public static RM_BazaarIntelLayerDef Layer(string defName) =>
            DefDatabase<RM_BazaarIntelLayerDef>.GetNamedSilentFail(defName);

        public static bool IsUnlocked(string layerDefName, RM_BazaarSession session) =>
            IsUnlocked(Layer(layerDefName), session);

        public static bool IsUnlocked(RM_BazaarIntelLayerDef layer, RM_BazaarSession session)
        {
            if (layer == null || session == null) return false;
            if (!ToggleOn(layer.settingsToggle)) return false;
            if (!ReferenceEquals(cachedFor, session))
            {
                cachedFor = session;
                cache.Clear();
                presentModules = null;
            }
            bool v;
            if (cache.TryGetValue(layer, out v)) return v;
            v = Evaluate(layer, session);
            cache[layer] = v;
            return v;
        }

        private static bool Evaluate(RM_BazaarIntelLayerDef layer, RM_BazaarSession session)
        {
            if (layer.requiredModule != null)
            {
                return RM_BazaarSettings.intelModules && PresentModules(session).Contains(layer.requiredModule);
            }
            if (!layer.minSocialSkill.HasValue) return false;
            int social = session.negotiator?.skills?.GetSkill(SkillDefOf.Social)?.Level ?? 0;
            return social >= layer.minSocialSkill.Value - SocialGateReduction(session);
        }

        /// <summary>Sum of lowersOtherSocialGatesBy over unlocked module layers (D4 = 2).</summary>
        public static int SocialGateReduction(RM_BazaarSession session)
        {
            if (!RM_BazaarSettings.intelModules) return 0;
            int r = 0;
            HashSet<HediffDef> mods = PresentModules(session);
            foreach (RM_BazaarIntelLayerDef l in DefDatabase<RM_BazaarIntelLayerDef>.AllDefsListForReading)
            {
                if (l.requiredModule != null && l.lowersOtherSocialGatesBy > 0 && mods.Contains(l.requiredModule)
                    && ToggleOn(l.settingsToggle))
                {
                    r += l.lowersOtherSocialGatesBy;
                }
            }
            return r;
        }

        public static bool ToggleOn(string toggle)
        {
            switch (toggle)
            {
                case null:
                case "": return true;
                case "intelPriceContext": return RM_BazaarSettings.intelPriceContext;
                case "intelGoodDeals": return RM_BazaarSettings.intelGoodDeals;
                case "intelLocalEconomy": return RM_BazaarSettings.intelLocalEconomy;
                case "intelScarcity": return RM_BazaarSettings.intelScarcity;
                case "intelModules": return RM_BazaarSettings.intelModules;
                default:
                    Log.ErrorOnce("[The Bazaar] Unknown intel settingsToggle '" + toggle + "' - layer treated as on.",
                        toggle.GetHashCode());
                    return true;
            }
        }

        private static HashSet<HediffDef> PresentModules(RM_BazaarSession session)
        {
            if (presentModules != null && ReferenceEquals(cachedFor, session)) return presentModules;
            presentModules = new HashSet<HediffDef>();
            foreach (Pawn p in Party(session.negotiator))
            {
                if (!IsFunctionalProtocolDroid(p)) continue;
                List<Hediff> hs = p.health?.hediffSet?.hediffs;
                if (hs == null) continue;
                for (int i = 0; i < hs.Count; i++) presentModules.Add(hs[i].def);
            }
            return presentModules;
        }

        public static IEnumerable<Pawn> Party(Pawn negotiator)
        {
            if (negotiator == null) yield break;
            Caravan caravan = negotiator.GetCaravan();
            if (caravan != null)
            {
                foreach (Pawn p in caravan.PawnsListForReading) yield return p;
                yield break;
            }
            Map map = negotiator.MapHeld;
            if (map != null && Faction.OfPlayer != null)
            {
                foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer)) yield return p;
                yield break;
            }
            yield return negotiator;
        }

        // ── Droidworks' functional-protocol-droid test, by reflection ──
        private static bool droidResolved;
        private static Func<Pawn, bool> isFunctional;

        public static bool IsFunctionalProtocolDroid(Pawn p)
        {
            if (p == null) return false;
            if (!droidResolved)
            {
                droidResolved = true;
                Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.StarWars.Droidworks.Patch_ProtocolTradeAdvantage");
                MethodInfo m = t?.GetMethod("IsAvailableProtocolDroid", BindingFlags.Public | BindingFlags.Static,
                    null, new[] { typeof(Pawn) }, null);
                if (m != null && m.ReturnType == typeof(bool))
                {
                    isFunctional = (Func<Pawn, bool>)Delegate.CreateDelegate(typeof(Func<Pawn, bool>), m);
                }
            }
            if (isFunctional == null) return false;
            try { return isFunctional(p); }
            catch (Exception ex)
            {
                Log.ErrorOnce("[The Bazaar] Droidworks protocol-droid check threw; module intel disabled: " + ex, 0x6BA2A2);
                isFunctional = null;
                return false;
            }
        }
    }
}
