using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.RustCathedral
{
    /// <summary>What the restoration consumes. One def, RM_BorehulkRestoration; a list so it stays tunable by a patch.</summary>
    public class RM_BorehulkRestorationDef : Def
    {
        public List<ThingDefCountClass> ingredients = new List<ThingDefCountClass>();
        public int minCrafting = 10;
    }

    /// <summary>On a FactionDef: this faction runs the truce yard. Data, so the campaign moves it by patch and rewords it.</summary>
    public class RM_DrillRefurbisherExtension : DefModExtension
    {
        public string bossLabel = "the yard boss";
        public string greeting = "The yard boss looks over the work order and spits. A truce holds while the order stands.";
        public string secondDemand = "The price went up. The yard boss does not pretend otherwise.";
    }

    /// <summary>On a FactionDef: these are the neutral droids, whose goodwill the keep/free choice moves.</summary>
    public class RM_NeutralDroidsExtension : DefModExtension
    {
    }

    /// <summary>On a ThingDef: a sacred cell. Mining one is the player's sacrilege, whichever hand did it.</summary>
    public class RM_SacredCellExtension : DefModExtension
    {
    }

    [DefOf]
    public static class RM_WornBitDefOf
    {
        public static ThingDef RM_Borehulk;
        public static ThingDef RM_WornDrillHead;
        public static ThingDef RM_RefurbishedDrillHead;
        public static ThingDef RM_CathedralDeckPlate;
        public static JobDef RM_Job_UnbitBorehulk;
        public static JobDef RM_Job_RestoreBorehulk;
        public static JobDef RM_Job_ServiceBorehulk;
        public static JobDef RM_Job_BorehulkDig;
        public static QuestScriptDef RM_WornBitRefurbishment;
        public static WorldObjectDef RM_RefurbishYard;
        public static RM_BorehulkRestorationDef RM_BorehulkRestoration;
        public static HistoryEventDef RM_WornBitChoiceMade;

        static RM_WornBitDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WornBitDefOf));
        }
    }
}
