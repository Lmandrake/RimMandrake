using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FIRSTCOAT_BONUS_1, spec §3.5 / item Build section. Called
    // from CompDeepfire.AddCoat() exactly once, when the FIRST coat lands
    // and CompDeepfire.bonusApplied (Scribed) is still false.
    //
    // Art items (CompArt present -- sculptures, the Utinni idols, any other
    // CompArt-bearing thing) get a permanent +1 quality step, capped at
    // Legendary; the coat itself is still charged/consumed at the cap
    // (CompDeepfire.AddCoat already handles that via coats++ regardless of
    // whether this method does anything).
    //
    // Everything else gets no code-side action here at all: the Beauty
    // bonus is RM_StatPart_Deepfire, an XML-patched StatPart
    // (Patches/DeepfireBeautyStatPart.xml) that reads CompDeepfire.coats
    // live off the thing every time Beauty is asked for. It is stateless by
    // construction -- it cannot double-fire on strip + reapply the way a
    // cumulative SetQuality call could -- so it needs no bonusApplied gate
    // and nothing to call from here.
    public static class DeepfireFirstCoatBonus
    {
        public static bool IsArtItem(Thing thing) => thing?.TryGetComp<CompArt>() != null;

        public static void Apply(Thing parent)
        {
            CompArt art = parent?.TryGetComp<CompArt>();
            if (art == null) return; // non-art: RM_StatPart_Deepfire handles the bonus, nothing to do here
            if (!LuminousPigmentSettings.artQualityBump) return; // spec §7 artQualityBump off -- coat still charges, no bump

            CompQuality quality = parent.TryGetComp<CompQuality>();
            if (quality == null) return; // CompArt with no CompQuality never happens in vanilla or our own defs; nothing to bump

            if (quality.Quality >= QualityCategory.Legendary) return; // capped -- Legendary stays Legendary

            QualityCategory next = (QualityCategory)Mathf.Min((int)quality.Quality + 1, (int)QualityCategory.Legendary);
            quality.SetQuality(next, ArtGenerationContext.Colony);
        }
    }
}
