using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_TRACTION_LANCE_BUILD_1 step 4: "two places to learn it". One research row, granted outright by
    // whichever study finishes first: the Webwork's gutter junction or the Sump's preserved draw-joints.
    //
    // RM_CompProperties_AnalyzableGrantResearch is the vanilla analyzable (Biotech signal-chip shape: its own
    // requiredAnalyzed unlocks still work, letters unchanged) plus a list of research rows FINISHED when this
    // analysis completes. Rows are named by defName STRING and looked up silently, so an item in one mod can
    // grant a row in another mod that may be absent (the def-existence guard the item asks for; never
    // MayRequire on an <Operation>, which is inert in 1.6).
    public class RM_CompProperties_AnalyzableGrantResearch : CompProperties_CompAnalyzableUnlockResearch
    {
        public List<string> grantsResearch = new List<string>();
        // {PAWN_labelShort} and {RESEARCH} (the granted row's label) resolve. Empty = no extra letter.
        public string grantLetterLabel;
        public string grantLetter;

        public RM_CompProperties_AnalyzableGrantResearch()
        {
            compClass = typeof(RM_CompAnalyzableGrantResearch);
        }
    }

    public class RM_CompAnalyzableGrantResearch : CompAnalyzableUnlockResearch
    {
        public RM_CompProperties_AnalyzableGrantResearch GrantProps => (RM_CompProperties_AnalyzableGrantResearch)props;

        public override void OnAnalyzed(Pawn pawn)
        {
            int id = AnalysisID;
            base.OnAnalyzed(pawn); // may destroy parent (destroyedOnAnalyzed); nothing below touches it
            if (!Find.AnalysisManager.HasAnalysisWithID(id) || !Find.AnalysisManager.TryGetAnalysisProgress(id, out AnalysisDetails details) || !details.Satisfied)
            {
                return;
            }
            Grant(GrantProps, pawn);
        }

        /// <summary>Finish every named row not already finished; returns how many were newly finished.</summary>
        public static int Grant(RM_CompProperties_AnalyzableGrantResearch p, Pawn pawn)
        {
            int granted = 0;
            if (p?.grantsResearch == null)
            {
                return 0;
            }
            foreach (string name in p.grantsResearch)
            {
                ResearchProjectDef proj = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(name);
                if (proj == null || proj.IsFinished)
                {
                    continue;
                }
                Find.ResearchManager.FinishProject(proj, doCompletionDialog: false, pawn, doCompletionLetter: false);
                granted++;
                if (!p.grantLetterLabel.NullOrEmpty() && !p.grantLetter.NullOrEmpty())
                {
                    string label = pawn != null
                        ? p.grantLetterLabel.Formatted(pawn.Named("PAWN"), proj.label.Named("RESEARCH")).Resolve()
                        : p.grantLetterLabel.Formatted(proj.label.Named("RESEARCH")).Resolve();
                    string text = pawn != null
                        ? p.grantLetter.Formatted(pawn.Named("PAWN"), proj.label.Named("RESEARCH")).Resolve()
                        : p.grantLetter.Formatted(proj.label.Named("RESEARCH")).Resolve();
                    Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.PositiveEvent);
                }
            }
            return granted;
        }
    }

    // The gutter-junction cut. A building carrying this leaves `specimen` ONLY when it is deconstructed (cut out
    // carefully: "brace and cut out ... without breaking it"); killed, it leaves its ordinary killedLeavings and
    // no specimen. With tripSenseWeb the cut registers like a touch in RM_MapComponent_SenseWeb on the pawn(s)
    // doing it, so the web's owners come.
    public class RM_CompProperties_SpecimenOnDeconstruct : CompProperties
    {
        public ThingDef specimen;
        public int count = 1;
        public bool tripSenseWeb = true;

        public RM_CompProperties_SpecimenOnDeconstruct()
        {
            compClass = typeof(RM_CompSpecimenOnDeconstruct);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (specimen == null)
            {
                yield return "RM_CompProperties_SpecimenOnDeconstruct has no specimen";
            }
        }
    }

    public class RM_CompSpecimenOnDeconstruct : ThingComp
    {
        public RM_CompProperties_SpecimenOnDeconstruct Props => (RM_CompProperties_SpecimenOnDeconstruct)props;

        // Proof reads (static: the parent is gone by the time anyone asks).
        public static int lastSpecimensSpawned;
        public static int lastTouchesRegistered;

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            lastSpecimensSpawned = 0; // proof fields describe THIS call, never a stale earlier one
            lastTouchesRegistered = 0;
            if (mode != DestroyMode.Deconstruct || previousMap == null || Props.specimen == null)
            {
                return;
            }
            IntVec3 at = parent.Position;
            Thing t = ThingMaker.MakeThing(Props.specimen);
            int count = System.Math.Max(1, Props.count);
            t.stackCount = count;
            bool placed = GenPlace.TryPlaceThing(t, at, previousMap, ThingPlaceMode.Near);
            lastSpecimensSpawned = placed ? count : 0; // count what was placed, not the (possibly merged-away) temp stack
            lastTouchesRegistered = 0;
            if (!Props.tripSenseWeb)
            {
                return;
            }
            RM_MapComponent_SenseWeb web = previousMap.GetComponent<RM_MapComponent_SenseWeb>();
            if (web == null)
            {
                return;
            }
            foreach (Pawn p in previousMap.mapPawns.AllPawnsSpawned)
            {
                if (p.Position.InHorDistOf(at, 2.9f) && p.CurJobDef == JobDefOf.Deconstruct && web.RegisterTouch(p))
                {
                    lastTouchesRegistered++;
                }
            }
        }
    }
}
