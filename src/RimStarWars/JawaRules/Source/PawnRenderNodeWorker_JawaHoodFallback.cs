using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.JawaRules
{
    // JAWA_HOOD_ALWAYS_VISIBLE_1 — owner, 2026-09-25: "Jawa should never be seen
    // without a hood. It's unholy." Full account and why this is a render-node
    // worker instead of a Harmony flag patch: see the comment block above
    // RSW_Jawa_Head_Plain in Defs/GeneDefs/Jawa_Head.xml, which wires this class
    // in as that gene's <renderNodeProperties><workerClass>.
    //
    // This class is NOT Harmony-patched and needs no registration in
    // JawaRulesMod's static constructor — RimWorld's def system instantiates it
    // by name (GenWorker<PawnRenderNodeWorker>.Get(workerClass)) purely because
    // the gene def above names it. It only ever runs on a pawn that has the
    // RSW_Jawa_Head_Plain gene ACTIVE (DynamicPawnRenderNodeSetup_Genes gates on
    // Gene.Active before this node is even added to the render tree), so there
    // is deliberately no IsJawa() check here — the gene is already the identity
    // check, and it is a narrower/more correct one than a xenotype-defName
    // string compare (it would also cover a future second Jawa-adjacent
    // xenotype that reuses this same head gene).
    public class PawnRenderNodeWorker_JawaHoodFallback : PawnRenderNodeWorker
    {
        // Resolved lazily and cached: Harmony/def-worker classes can be touched
        // before DefDatabase<ThingDef> is fully populated, so resolving
        // guy762_JawaHood at static-init time is not safe. GetNamedSilentFail
        // never throws if the Armoury mod is off — this fallback then simply
        // never suppresses itself, which is the correct behaviour (no real hood
        // def to duplicate against).
        private static ThingDef jawaHoodDefCached;
        private static bool jawaHoodDefResolved;

        private static ThingDef JawaHoodDef
        {
            get
            {
                if (!jawaHoodDefResolved)
                {
                    jawaHoodDefResolved = true;
                    jawaHoodDefCached = DefDatabase<ThingDef>.GetNamedSilentFail("guy762_JawaHood");
                }
                return jawaHoodDefCached;
            }
        }

        public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
        {
            if (!base.CanDrawNow(node, parms))
            {
                return false;
            }
            try
            {
                return !RealHoodIsDrawing(parms);
            }
            catch (Exception e)
            {
                // Fail OPEN: the whole point of this node is "never a bare Jawa
                // head", so if the double-hood guard itself breaks, the worse
                // failure is silently reverting to a bare head, not an
                // occasional doubled hood texture.
                Log.ErrorOnce("[RimMandrake.StarWars.JawaRules] jawa-hood-fallback: "
                    + e.Message, 0x4A57A6);
                return true;
            }
        }

        // Skip this fallback only when the REAL apparel hood is both worn and
        // actually going to render (Clothes + Headgear both set — the same two
        // flags PawnRenderNodeWorker_Apparel_Head checks). Any other state —
        // not worn, or worn but flag-suppressed (swimming strips exactly these
        // two bits; see PawnRenderer.ParallelGetPreRenderResults) — leaves this
        // fallback drawing.
        private static bool RealHoodIsDrawing(PawnDrawParms parms)
        {
            ThingDef hood = JawaHoodDef;
            if (hood == null)
            {
                return false;
            }
            if (!parms.flags.FlagSet(PawnRenderFlags.Clothes)
                || !parms.flags.FlagSet(PawnRenderFlags.Headgear))
            {
                return false;
            }
            Pawn_ApparelTracker apparel = parms.pawn?.apparel;
            if (apparel == null)
            {
                return false;
            }
            List<Apparel> worn = apparel.WornApparel;
            for (int i = 0; i < worn.Count; i++)
            {
                if (worn[i].def == hood)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
