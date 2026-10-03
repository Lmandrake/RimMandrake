using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // CHILL_WAX_PROCESSION_GIANT_1 -- the Chill floor's giant. A colony walks as ordinary wandering
    // animal AI; this comp is the whole mechanic. A countdown runs while it walks; once it elapses the
    // colony extrudes a dead filter sheet at the FIRST stationary moment (a pause), then restarts.
    // Return is ordinary hauling; the sheet deteriorates, so distance and time are the pressure.
    // Killing the colony spoils its pending and uncollected sheets into hydrocarbon flesh.
    // Pawn.TickRare runs CompTickRare for pawns; nothing here is gated by IsHashIntervalTick.
    public class RM_CompProperties_WaxProcession : CompProperties
    {
        public RM_CompProperties_WaxProcession() { compClass = typeof(RM_Comp_WaxProcession); }
        public int ticksBetweenSheets = 90000;      // ~1.5 days of walking between pauses
        public string sheetDefName = "RM_DeadFilterSheet";
        public string spoilDefName = "RM_HydrocarbonFlesh";
        public int spoilCountPerSheet = 12;
    }

    public class RM_Comp_WaxProcession : ThingComp
    {
        private int ticksLeft = -1;
        private List<Thing> sheets = new List<Thing>();

        public RM_CompProperties_WaxProcession Props => (RM_CompProperties_WaxProcession)props;

        public override void CompTickRare()
        {
            base.CompTickRare();
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.MapHeld == null) return;
            if (!RM_TerminalBiomesSettings.ChillWaxProcessionActive) return;
            sheets.RemoveAll(s => s == null || s.Destroyed || !s.Spawned);
            if (ticksLeft < 0) ticksLeft = Props.ticksBetweenSheets;
            ticksLeft -= GenTicks.TickRareInterval;
            if (ticksLeft > 0) return;
            if (pawn.pather != null && pawn.pather.Moving) return;   // wait for a pause
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(Props.sheetDefName);
            ticksLeft = Props.ticksBetweenSheets;
            if (def == null) return;
            Thing sheet = ThingMaker.MakeThing(def);
            if (GenPlace.TryPlaceThing(sheet, pawn.Position, pawn.Map, ThingPlaceMode.Near))
            {
                sheets.Add(sheet);
                Messages.Message("RM_WaxProcessionSheet".Translate(), new LookTargets(sheet), MessageTypeDefOf.NeutralEvent, false);
            }
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (mode != DestroyMode.KillFinalize || previousMap == null) return;
            ThingDef spoil = DefDatabase<ThingDef>.GetNamedSilentFail(Props.spoilDefName);
            if (spoil == null) return;
            int pending = 1;   // the sheet it was carrying
            foreach (Thing s in sheets)
            {
                if (s != null && !s.Destroyed && s.Spawned && s.Map == previousMap)
                {
                    IntVec3 c = s.Position;
                    s.Destroy(DestroyMode.Vanish);
                    Drop(spoil, c, previousMap);
                }
            }
            Drop(spoil, parent.PositionHeld, previousMap, pending);
            sheets.Clear();
        }

        private void Drop(ThingDef spoil, IntVec3 cell, Map map, int sheetsWorth = 1)
        {
            if (!cell.IsValid || !cell.InBounds(map)) return;
            Thing t = ThingMaker.MakeThing(spoil);
            t.stackCount = Props.spoilCountPerSheet * sheetsWorth;
            if (!GenPlace.TryPlaceThing(t, cell, map, ThingPlaceMode.Near)) t.Destroy(DestroyMode.Vanish);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksLeft, "ticksLeft", -1);
            Scribe_Collections.Look(ref sheets, "sheets", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && sheets == null) sheets = new List<Thing>();
        }
    }
}
