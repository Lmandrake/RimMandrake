// Pure decision kernels of JawaRules (mandrake.rsw.jawarules): no Verse, no RimWorld, no UnityEngine, no Harmony. The Harmony postfixes and the
// render-node worker call these with the same expressions they used inline and keep the engine half (flags enum, defs, trackers, names).
using System;

namespace RimMandrake.StarWars.JawaRules
{
    /// <summary>The Jawa hood: a swimming pawn loses Clothes and Headgear from its render flags and vanilla drops every worn hat; a Jawa keeps
    /// its real hood by asking the same worker again with the two flags put back, and the always-on fallback hood draws exactly when the real
    /// one is not going to. Flags are plain ints here (Headgear 0x20, Clothes 0x40, as measured in the decompiled engine).</summary>
    public static class RSW_HoodKernel
    {
        public const int Headgear = 0x20, Clothes = 0x40, ApparelFlags = Headgear | Clothes;

        /// <summary>The swim rule applies to this draw: toggle on, swimming, not a portrait.</summary>
        public static bool SwimForceApplies(bool enabled, bool swimming, bool portrait) { return enabled && swimming && !portrait; }

        /// <summary>The flags a kept hood is drawn under: vanilla's, plus Clothes|Headgear back while the swim rule applies.</summary>
        public static int EffectiveFlags(int flags, bool applies) { return applies ? flags | ApparelFlags : flags; }

        /// <summary>The postfix on the apparel-head worker's CanDrawNow. Only when vanilla said no, we are not already inside our own re-ask,
        /// the swim rule applies and the node's apparel is a kept hood does it ask the same worker again with the flags restored; every
        /// other vanilla gate still decides. A throwing re-ask leaves the vanilla answer.</summary>
        public static bool Postfix(bool vanillaResult, bool reentry, bool applies, bool keptHood, int flags, Func<int, bool> askAgain)
        {
            if (vanillaResult || reentry) return vanillaResult;
            if (!applies || !keptHood) return vanillaResult;
            return askAgain(EffectiveFlags(flags, applies));
        }

        /// <summary>The real hood is going to draw: the def resolved, the (effective) flags make headgear visible, the pawn has an apparel tracker
        /// and wears the hood.</summary>
        public static bool RealHoodIsDrawing(bool hoodDefResolved, Func<int, bool> headgearVisible, int flags, bool applies, bool hasApparelTracker, Func<bool> wearsHood)
        {
            if (!hoodDefResolved) return false;
            if (!headgearVisible(EffectiveFlags(flags, applies))) return false;
            if (!hasApparelTracker) return false;
            return wearsHood();
        }

        /// <summary>The fallback hood node draws when its own base gates pass and the real hood is not drawing. If the double-hood guard
        /// itself throws it fails OPEN: a doubled hood beats a bare Jawa head.</summary>
        public static bool FallbackDraws(bool baseCanDraw, Func<bool> realHoodDrawing)
        {
            if (!baseCanDraw) return false;
            try { return !realHoodDrawing(); }
            catch (Exception) { return true; }
        }
    }

    /// <summary>The small rule gates of JawaRules' other Harmony patches.</summary>
    public static class RSW_RulesKernel
    {
        /// <summary>A Jawa is a pawn whose xenotype is the Jawa xenotype, by name.</summary>
        public static bool IsJawa(bool hasGenes, bool hasXenotype, string xenotypeDefName, string jawaXenotype) { return hasGenes && hasXenotype && xenotypeDefName == jawaXenotype; }

        /// <summary>No-sow: a Jawa's "can sow" answer becomes false; everyone else keeps vanilla's.</summary>
        public static bool SowResult(bool enabled, bool vanillaResult, Func<bool> isJawa) { return enabled && vanillaResult && isJawa() ? false : vanillaResult; }

        /// <summary>A humanlike pawn generated without a relations tracker gets one.</summary>
        public static bool NeedsRelationsTracker(bool enabled, bool hasRaceProps, bool humanlike, bool hasTracker) { return enabled && hasRaceProps && humanlike && !hasTracker; }

        /// <summary>A pet gets a race-namer name when it is a player-owned animal with no name or a numerical placeholder.</summary>
        public static bool NeedsPetName(bool enabled, bool hasRaceProps, bool animal, bool hasFaction, bool playerFaction, bool hasName, bool nameNumerical)
        {
            if (!enabled || !hasRaceProps || !animal) return false;
            if (!hasFaction || !playerFaction) return false;
            if (hasName && !nameNumerical) return false;
            return true;
        }

        /// <summary>A redressed world pawn that came back as the wrong kind is forced onto the requested kind.</summary>
        public static bool ForceKind(bool enabled, bool hasPawn, bool hasRequestKind, bool kindDiffers) { return enabled && hasPawn && hasRequestKind && kindDiffers; }

        /// <summary>...and onto the requested xenotype when Biotech is on, the kind uses faction xenotypes and the wanted xenotype differs.</summary>
        public static bool ForceXenotype(bool biotech, bool hasGenes, bool usesFactionXenotypes, bool wantedExists, bool differs) { return biotech && hasGenes && usesFactionXenotypes && wantedExists && differs; }

        /// <summary>The world-label values the transpiled constants read: the wanted value while the boost is on, else the vanilla constant.</summary>
        public static float Current(bool boostEnabled, float wanted, float vanilla) { return boostEnabled ? wanted : vanilla; }
    }
}
