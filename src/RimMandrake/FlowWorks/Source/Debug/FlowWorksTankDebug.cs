using System.Collections.Generic;
using System.Linq;
using LudeonTK;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using UnityEngine;
using Verse;

// TANK_DEBUG_BUILD_FILL_AT_WILL (owner: "add god-mode debug actions to empty or fill to max all universal containers with any
// RimFlow liquid (default water)"). Every container is a Building_LiquidTank (all sizes and looks). FILL REPLACES the contents
// (a tank holding another liquid is overwritten); every debug add / remove is counted in RM_TankDebugMath and shown on the L0
// ledger line (dbgAdded / dbgRemoved). Mod Settings / mode are untouched; the net is bumped and the tank redrawn after.
namespace RimMandrake.FlowWorks
{
    public static class FlowWorksTankDebug
    {
        private const string CAT = "RMFlowWorks";

        public static List<LiquidDef> Liquids()
        {
            Dictionary<string, LiquidDef> by = DefDatabase<LiquidDef>.AllDefsListForReading.ToDictionary(d => d.defName, d => d);
            return RM_TankDebugMath.PickerOrder(by.Keys).Select(n => by[n]).ToList();
        }

        public static void Fill(Building_LiquidTank t, LiquidDef liquid)
        {
            int had = t.Empty ? 0 : t.storedUnits;
            t.storedLiquid = liquid;
            t.storedUnits = RM_TankDebugMath.FillUnits(t.Capacity);
            RM_TankDebugMath.RecordFill(had, t.storedUnits);
            Refresh(t);
        }

        public static void Empty(Building_LiquidTank t)
        {
            RM_TankDebugMath.RecordEmpty(t.Empty ? 0 : t.storedUnits);
            t.storedUnits = 0;
            t.storedLiquid = null;
            Refresh(t);
        }

        private static void Refresh(Building_LiquidTank t)
        {
            if (!t.Spawned) return;
            Machinery.RM_LiquidNet.Bump(t.Map);
            t.Notify_ColorChanged();
            t.Map.mapDrawer.MapMeshDirty(t.Position, MapMeshFlagDefOf.Things);
        }

        private static IEnumerable<Building_LiquidTank> AllOnMap(Map map) =>
            map == null ? Enumerable.Empty<Building_LiquidTank>()
                : map.listerThings.AllThings.OfType<Building_LiquidTank>().ToList();

        private static Building_LiquidTank TankUnderMouse()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (map == null || !c.InBounds(map)) return null;
            return c.GetThingList(map).OfType<Building_LiquidTank>().FirstOrDefault();
        }

        private static void PickLiquid(string title, System.Action<LiquidDef> then)
        {
            List<FloatMenuOption> opts = new List<FloatMenuOption>();
            foreach (LiquidDef l in Liquids())
            {
                LiquidDef pick = l;
                opts.Add(new FloatMenuOption(l.defName == RM_TankDebugMath.DefaultLiquidDefName ? l.LabelCap + " (default)" : l.LabelCap,
                    () => then(pick)));
            }
            Find.WindowStack.Add(new FloatMenu(opts));
            Messages.Message(title, MessageTypeDefOf.SilentInput, false);
        }

        [DebugAction(CAT, "Tank: fill to max (pick liquid, click tank)", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void FillOne()
        {
            PickLiquid("Pick the liquid, then click a tank.", liquid =>
                DebugTools.curTool = new DebugTool("Fill tank: " + liquid.LabelCap, () =>
                {
                    Building_LiquidTank t = TankUnderMouse();
                    if (t == null) return;
                    Fill(t, liquid);
                    Log.Message("[RMFlowWorksDebug] TANK_FILL " + t.ThingID + " " + liquid.defName + " " + t.storedUnits + " dL");
                }));
        }

        [DebugAction(CAT, "Tank: empty (click tank)", allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void EmptyOne()
        {
            Building_LiquidTank t = TankUnderMouse();
            if (t == null) return;
            Empty(t);
            Log.Message("[RMFlowWorksDebug] TANK_EMPTY " + t.ThingID);
        }

        [DebugAction(CAT, "Tanks: fill ALL on map to max (pick liquid)", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void FillAll()
        {
            PickLiquid("Pick the liquid to fill every tank on this map with.", liquid =>
            {
                int n = 0;
                foreach (Building_LiquidTank t in AllOnMap(Find.CurrentMap)) { Fill(t, liquid); n++; }
                Messages.Message("Filled " + n + " tank(s) with " + liquid.LabelCap + ".", MessageTypeDefOf.TaskCompletion, false);
                Log.Message("[RMFlowWorksDebug] TANK_FILL_ALL " + n + " " + liquid.defName);
            });
        }

        [DebugAction(CAT, "Tanks: empty ALL on map", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void EmptyAll()
        {
            int n = 0;
            foreach (Building_LiquidTank t in AllOnMap(Find.CurrentMap)) { Empty(t); n++; }
            Messages.Message("Emptied " + n + " tank(s).", MessageTypeDefOf.TaskCompletion, false);
            Log.Message("[RMFlowWorksDebug] TANK_EMPTY_ALL " + n);
        }

        /// <summary>The god-mode gizmos on a selected tank: fill (liquid picker) and empty.</summary>
        public static IEnumerable<Gizmo> DevGizmos(Building_LiquidTank t)
        {
            if (!DebugSettings.godMode) yield break;
            yield return new Command_Action
            {
                defaultLabel = "Dev: fill",
                defaultDesc = "God mode: fill this tank to max with a liquid you pick (replaces its contents).",
                icon = BaseContent.BadTex,
                action = () => PickLiquid("Pick the liquid.", l => Fill(t, l))
            };
            yield return new Command_Action
            {
                defaultLabel = "Dev: empty",
                defaultDesc = "God mode: empty this tank.",
                icon = BaseContent.BadTex,
                action = () => Empty(t)
            };
        }
    }
}
