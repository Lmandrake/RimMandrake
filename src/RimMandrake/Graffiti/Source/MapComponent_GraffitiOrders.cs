using RimWorld;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_DESIGNATOR_MARK_CHOICE_1 (fork F6, ruled 2026-10-09: "full
    // designator + bill - choose mark, choose wall"). A vanilla Designation
    // carries no payload, so the mark the player chose for a designated cell
    // lives here, keyed by cell. A missing entry means "painter's pick" (the
    // designator pool). An entry whose designation no longer exists (the
    // player cancelled it) is stale and is ignored and dropped on read and on
    // save, so a later designation of the same cell never inherits it.
    public class MapComponent_GraffitiOrders : MapComponent
    {
        private Dictionary<IntVec3, ThingDef> orders = new Dictionary<IntVec3, ThingDef>();
        private List<IntVec3> tmpCells;
        private List<ThingDef> tmpDefs;
        // Who or which faction an ordered mark is about (the designator's second menu).
        private Dictionary<IntVec3, Pawn> subjects = new Dictionary<IntVec3, Pawn>();
        private Dictionary<IntVec3, Faction> factions = new Dictionary<IntVec3, Faction>();
        private List<IntVec3> tmpSubjectCells, tmpFactionCells;
        private List<Pawn> tmpSubjects;
        private List<Faction> tmpFactions;

        public MapComponent_GraffitiOrders(Map map) : base(map)
        {
        }

        public static MapComponent_GraffitiOrders For(Map map)
        {
            return map?.GetComponent<MapComponent_GraffitiOrders>();
        }

        public Pawn SubjectAt(IntVec3 cell) { return subjects.TryGetValue(cell, out Pawn p) ? p : null; }

        public Faction FactionAt(IntVec3 cell) { return factions.TryGetValue(cell, out Faction f) ? f : null; }

        public void SetOrder(IntVec3 cell, ThingDef markDef, Pawn subject = null, Faction faction = null)
        {
            subjects.Remove(cell);
            factions.Remove(cell);
            if (subject != null) subjects[cell] = subject;
            if (faction != null) factions[cell] = faction;
            if (markDef == null)
            {
                orders.Remove(cell);
            }
            else
            {
                orders[cell] = markDef;
            }
        }

        // The ordered mark for a cell that is still designated, else null.
        public ThingDef OrderAt(IntVec3 cell)
        {
            if (!orders.TryGetValue(cell, out ThingDef def))
            {
                return null;
            }
            if (def == null || map.designationManager.DesignationAt(cell, RMGraffitiDefOf.RM_PaintGraffitiHere) == null)
            {
                orders.Remove(cell);
                return null;
            }
            return def;
        }

        public void Clear(IntVec3 cell)
        {
            orders.Remove(cell);
            subjects.Remove(cell);
            factions.Remove(cell);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                List<IntVec3> stale = new List<IntVec3>();
                foreach (KeyValuePair<IntVec3, ThingDef> kv in orders)
                {
                    if (kv.Value == null || map.designationManager.DesignationAt(kv.Key, RMGraffitiDefOf.RM_PaintGraffitiHere) == null)
                    {
                        stale.Add(kv.Key);
                    }
                }
                foreach (IntVec3 c in stale)
                {
                    Clear(c);
                }
            }
            Scribe_Collections.Look(ref orders, "rmGraffitiOrders", LookMode.Value, LookMode.Def, ref tmpCells, ref tmpDefs);
            Scribe_Collections.Look(ref subjects, "rmGraffitiOrderSubjects", LookMode.Value, LookMode.Reference, ref tmpSubjectCells, ref tmpSubjects);
            Scribe_Collections.Look(ref factions, "rmGraffitiOrderFactions", LookMode.Value, LookMode.Reference, ref tmpFactionCells, ref tmpFactions);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                orders = orders ?? new Dictionary<IntVec3, ThingDef>();
                subjects = subjects ?? new Dictionary<IntVec3, Pawn>();
                factions = factions ?? new Dictionary<IntVec3, Faction>();
            }
        }
    }
}
