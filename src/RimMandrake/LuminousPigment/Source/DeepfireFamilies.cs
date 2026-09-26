using System.Collections.Generic;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §6.3/§6.4's 14 families, table form. Spec §6.5 calls for this as
    // a generic XML `outcomes` list on the doer so any future Cuisine dish
    // can supply its own; this build ships it as a compiled table instead
    // (one recipe's worth of XML repeated 15 times would have been pure
    // duplication risk for no behavioural gain here) -- a future dish reuses
    // the algorithm in RM_IngestionOutcomeDoer_SteeredFamily by subclassing
    // it or by extending this table, not by copying it.
    public struct DeepfireFamily
    {
        public string key;
        public string hediffDefName;
        public float baseWeight;

        public DeepfireFamily(string key, string hediffDefName, float baseWeight)
        {
            this.key = key;
            this.hediffDefName = hediffDefName;
            this.baseWeight = baseWeight;
        }
    }

    public static class DeepfireFamilies
    {
        public const string VermilionKey = "vermilion";

        // Index order matches LuminousPigmentSettings.familyEnabled[]. Weights
        // 12/12/12/12/12/12/6/6/6/6/6/6/6/0 -- spec §6.4.
        public static readonly List<DeepfireFamily> All = new List<DeepfireFamily>
        {
            new DeepfireFamily("skin",     "RM_Glow_Skin",     12f),
            new DeepfireFamily("eyes",     "RM_Glow_Eyes",     12f),
            new DeepfireFamily("cranial",  "RM_Glow_Cranial",  12f),
            new DeepfireFamily("neural",   "RM_Glow_Neural",   12f),
            new DeepfireFamily("mouth",    "RM_Glow_Mouth",    12f),
            new DeepfireFamily("products", "RM_Glow_Products", 12f),
            new DeepfireFamily("blood",    "RM_Glow_Blood",     6f),
            new DeepfireFamily("marrow",   "RM_Glow_Marrow",    6f),
            new DeepfireFamily("hair",     "RM_Glow_Hair",      6f),
            new DeepfireFamily("gut",      "RM_Glow_Gut",       6f),
            new DeepfireFamily("nerves",   "RM_Glow_Nerves",    6f),
            new DeepfireFamily("pulse",    "RM_Glow_Pulse",     6f),
            new DeepfireFamily("lungs",    "RM_Glow_Lungs",     6f),
            new DeepfireFamily(VermilionKey, "RM_Glow_Whole",   0f),
        };

        private static HashSet<HediffDef> familyHediffDefsCache;

        public static int IndexOf(string key)
        {
            for (int i = 0; i < All.Count; i++)
            {
                if (All[i].key == key) return i;
            }
            return -1;
        }

        public static HediffDef HediffFor(string key)
        {
            int i = IndexOf(key);
            if (i < 0) return null;
            return DefDatabase<HediffDef>.GetNamedSilentFail(All[i].hediffDefName);
        }

        // Every HediffDef this table names -- used to count a pawn's
        // current distinct deepfire families (the 3-per-pawn cap, spec §6.2)
        // without needing a marker extension on each HediffDef.
        public static bool IsFamilyHediff(HediffDef def)
        {
            if (familyHediffDefsCache == null)
            {
                familyHediffDefsCache = new HashSet<HediffDef>();
                foreach (DeepfireFamily f in All)
                {
                    HediffDef hd = DefDatabase<HediffDef>.GetNamedSilentFail(f.hediffDefName);
                    if (hd != null) familyHediffDefsCache.Add(hd);
                }
            }
            return familyHediffDefsCache.Contains(def);
        }
    }
}
