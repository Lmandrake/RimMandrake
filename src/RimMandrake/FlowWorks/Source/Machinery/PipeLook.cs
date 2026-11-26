using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared;
using RimMandrake.Shared.StylePicker;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// The rigid universal pipe's per-build look (owner 2026-10-11, rulings #1/#8): FlowWorks' second instance of the shared
    /// def-agnostic style picker (_Shared/StylePicker/StylePickerCore.cs) -- the same interface the wires (Gimme Some Slack)
    /// and the hose reel (HoseLook) use -- registering only RM_UniversalPipe, with its own default-look setting
    /// (RM_MachinerySettings.pipeDefaultLook). Kept apart from HoseLook so switching hoses off never hides the pipe's menu.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PipeLook
    {
        internal static readonly StylePickerCore Core =
            new StylePickerCore("[FlowWorks]", PipeStyles.Looks, () => DefaultLook, PipeStyles.Resolve);

        static PipeLook()
        {
            Core.Register(PipeStyles.StyledDefs, PipeStyles.StyleDefName);
            // the tanks join the same picker only when their style defs are loaded (installed with their art)
            var tanks = new List<string>();
            foreach (string t in PipeStyles.TankDefs)
            {
                if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(PipeStyles.StyleDefName(t, PipeStyles.Scrapper)) != null) tanks.Add(t);
            }
            if (tanks.Count > 0) Core.Register(tanks, PipeStyles.StyleDefName);
            // RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS (owner 2026-10-16: "(1) but in the four art styles"): the weir joins the same
            // picker once its style defs (Defs/Rivers/RM_BankWeirStyles.xml, RM_BankWeir_<Look>) are loaded
            if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(PipeStyles.StyleDefName(PipeStyles.WeirDef, PipeStyles.Scrapper)) != null)
                Core.Register(new[] { PipeStyles.WeirDef }, PipeStyles.StyleDefName);
            // fixes 8 and 10 of the same item (owner card 2026-10-17: "Commission REVIEW.md items 3,4,6,7,8,9,10 in four
            // styles; judged in game"): the bank stake and the silt-trap, once Defs/Rivers/RM_BankWorksStyles.xml is loaded
            foreach (string bank in new[] { "RM_BankStake", "RM_SiltTrap" })
            {
                if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(PipeStyles.StyleDefName(bank, PipeStyles.Scrapper)) != null)
                    Core.Register(new[] { bank }, PipeStyles.StyleDefName);
            }
            // owner card 2026-10-22 (pumps E/F/G): the liquid pump joins once RM_LiquidPumpStyles.xml is loaded
            if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(PipeStyles.StyleDefName(PipeStyles.PumpDef, PipeStyles.Scrapper)) != null)
                Core.Register(new[] { PipeStyles.PumpDef }, PipeStyles.StyleDefName);
            PipeStyleIndex.core = Core;
        }

        /// <summary>State read: style defs missing at startup.</summary>
        public static List<string> Missing => Core.Missing;
        public static int picks => Core.picks;

        public static string DefaultLook => PipeStyles.DefaultLook(RM_MachinerySettings.pipeDefaultLook);

        public static bool IsStyled(ThingDef d) => Core.IsStyled(d);
        public static ThingStyleDef StyleFor(ThingDef d, string look) => Core.StyleFor(d, look);
        public static string LookOfThing(Thing t) => Core.LookOfThing(t);
        public static void Pick(Designator_Build des, string look) => Core.Pick(des, look);
        public static List<FloatMenuOption> MenuFor(Designator_Build des) => Core.MenuFor(des);

        /// <summary>Restyle one pipe in place (free, instant, art only) and redraw its cell.</summary>
        public static bool SetLook(Thing pipe, string look)
        {
            ThingStyleDef sd = StyleFor(pipe?.def, look);
            if (sd == null || !pipe.Spawned) return false;
            pipe.SetStyleDef(sd);
            // HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (owner 2026-10-16: "I can't change the style on it even though there is such a
            // button. It doesn't seem to do anything."): the ThingStyleHelper.SetStyleDef extension stores the style but, unlike the
            // Thing.StyleDef setter, never clears Thing.styleGraphicInt, so the mesh redrew the cached old look. Clear it here.
            pipe.Notify_ColorChanged();
            pipe.Map.mapDrawer.MapMeshDirty(pipe.Position, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
            return true;
        }

        /// <summary>
        /// MACHINERY_LOOK_FIX_DECK_REPAINT_ON_SWITCH (live A/B 2026-10-26, D:\ClaudeWork\rimmandrake\live_wave2_20261026\ev\look):
        /// a default-look switch in the settings must repaint every already-built thing that follows the default look. A thing
        /// with no stored style reads the default look's style through the Thing.StyleDef postfix (StylePickerCore.StyleDefPostfix),
        /// but Thing.Graphic caches the resolved style graphic (styleGraphicInt) on first read, so a map-mesh flag alone reprints
        /// the OLD picture. Per map: every spawned thing of a def this picker indexes with no stored style, plus the drawbridge
        /// winch and gate (their own look caches; RM_DrawbridgeControl), drops its cached graphic (Notify_ColorChanged); then
        /// the whole map's Buildings and Things layers reprint (multi-cell footprints and the drawbridge leaf/planks, which read
        /// the look at print). A thing with a picked look keeps it. Returns how many things were repainted (the state read).
        /// </summary>
        internal static int RepaintDefaultLook(StylePickerCore core)
        {
            if (core == null || Current.ProgramState != ProgramState.Playing || Find.Maps == null) return lastRepainted = 0;
            int n = 0;
            foreach (Map m in Find.Maps)
            {
                List<Thing> all = m.listerThings.AllThings;
                for (int i = 0; i < all.Count; i++)
                {
                    Thing t = all[i];
                    bool followsDefault = core.IsIndexed(t.def) && StylePickerCore.RawStyle(t) == null;
                    if (!followsDefault && !(t is Pits.Building_DrawbridgeWinch) && !(t is Pits.Building_DrawbridgeGate)) continue;
                    t.Notify_ColorChanged();
                    n++;
                }
                m.mapDrawer.WholeMapChanged((ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
            }
            RM_PipePoles.RedrawSpans();   // the span shadows reprint with the rest, as ResetAll does
            lastRepainted = n;
            return n;
        }

        /// <summary>State read: things repainted by the last default-look switch.</summary>
        public static int lastRepainted;

        // ------------------------------------------------ RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY
        // Owner 2026-11-22: "Clicking 'change style' on an object is supposed to change everything along its connected length."
        // Every FlowWorks line part's Choose style is this one gizmo; which parts change is RM_LineLook's (Verse-free, SelfTest
        // LineLookChecks), read over this map through MapLineGraph.

        /// <summary>A def's style of <paramref name="look"/> in its own FlowWorks picker (the pipe one, or the hose reel's).</summary>
        internal static ThingStyleDef LineStyleFor(ThingDef d, string look) => StyleFor(d, look) ?? HoseLook.StyleFor(d, look);

        internal static bool LineStyled(ThingDef d) => d != null && (IsStyled(d) || HoseLook.IsStyled(d));

        /// <summary>The look a part shows (for the menu's "(current)"), from its own picker.</summary>
        internal static string LineLookOf(Thing t) => HoseLook.IsStyled(t.def) ? HoseLook.LookOfThing(t) : LookOfThing(t);

        /// <summary>The look a part STORES (null: it follows its picker's default look, so a pick pins it).</summary>
        internal static string StoredLook(Thing t)
        {
            ThingStyleDef s = StylePickerCore.RawStyle(t);
            return s == null ? null : Core.LookOfStyle(s) ?? HoseLook.LookOfStyle(s);
        }

        /// <summary>The parts a pick of <paramref name="look"/> from <paramref name="starts"/> changes (RM_LineLook.Changes).</summary>
        public static List<Thing> LineChanges(Map map, IEnumerable<Thing> starts, string look, out bool capped)
        {
            capped = false;
            var list = new List<Thing>();
            if (map == null) return list;
            var g = new MapLineGraph(map);
            var vs = new List<object>();
            foreach (Thing t in starts) if (t?.Map == map) vs.Add(RM_LiquidNet.IsPipe(t) ? (object)t.Position : t);
            foreach (object o in RM_LineLook.Changes(g, vs, look, RM_LiquidNet.MaxPipeCells,
                         (o, l) => o is Thing t && LineStyleFor(t.def, l) != null, o => StoredLook(o as Thing), out capped))
            {
                if (o is Thing t) list.Add(t);
            }
            return list;
        }

        /// <summary>Restyle one line part in place, each through its own picker's setter.</summary>
        internal static bool SetLineLook(Thing t, string look)
        {
            Hose.CompHoseReel reel = t.TryGetComp<Hose.CompHoseReel>();
            if (reel != null && HoseLook.IsStyled(t.def))
            {
                reel.SetLook(look);
                return true;
            }
            return RM_LiquidNet.IsPipe(t) ? SetLook(t, look) : CompTankLook.SetLook(t, look);
        }

        /// <summary>State read: the parts the last line pick changed, and whether the cap cut it.</summary>
        public static int lastLineChanged;
        public static bool lastLineCapped;

        /// <summary>Pick <paramref name="look"/> for the whole line(s) holding <paramref name="starts"/>.</summary>
        public static int PickLineLook(Thing clicked, IEnumerable<Thing> starts, string look)
        {
            List<Thing> change = LineChanges(clicked.Map, starts, look, out bool capped);
            bool pole = false;
            int n = 0;
            foreach (Thing t in change)
            {
                if (!SetLineLook(t, look)) continue;
                n++;
                pole |= t.def.defName == RM_PipePoles.PoleDef;
            }
            if (pole) RM_PipePoles.RedrawSpans();
            lastLineChanged = n;
            lastLineCapped = capped;
            if (capped)
                Messages.Message("Only the nearest " + RM_LiquidNet.MaxPipeCells + " parts of this line took the new look: it is longer than that.",
                    clicked, MessageTypeDefOf.CautionInput, false);
            return n;
        }

        /// <summary>The one Choose style gizmo of every FlowWorks line part: one option per look the clicked part has, each the
        /// whole connected line (and the lines of the other selected parts). Null when the part has no look or is not the
        /// player's.</summary>
        public static Command_Action LineLookGizmo(Thing clicked)
        {
            if (clicked == null || clicked.Faction != Faction.OfPlayer || !LineStyled(clicked.def)) return null;
            return new Command_Action
            {
                defaultLabel = "Choose style",
                defaultDesc = "Give this " + clicked.def.label + " another look (scrapper, industrial, modern, futuristic). First choose how " +
                              "far: this item only, everything connected to it (pipes, tanks, pumps, sprinkler heads, faucets, pipe poles, hose " +
                              "reels), or every FlowWorks part you own on the map. A part with no art in that look keeps its own. Free and " +
                              "instant; it changes art only, never cost, capacity or function.",
                icon = clicked.StyleDef?.UIIcon ?? (Texture2D)clicked.def.uiIcon,
                action = () => Find.WindowStack.Add(new FloatMenu(ReachMenu(clicked)))
            };
        }

        /// <summary>RIMMANDRAKE_OFFER_FLOWWORKS_STYLE_REACHES_AS_SLACK_DOES (his walk, 2026-11-25: "all the options like we did in
        /// GSS"): the first menu, Gimme Some Slack's three reaches (ConduitStylePicker.ReachMenu), each naming what it repaints.</summary>
        public static List<FloatMenuOption> ReachMenu(Thing clicked)
        {
            var starts = new List<Thing> { clicked };
            foreach (object o in Find.Selector.SelectedObjectsListForReading)
                if (o is Thing t && t != clicked && t.Map == clicked.Map && t.Faction == Faction.OfPlayer) starts.Add(t);
            var opts = new List<FloatMenuOption>
            {
                new FloatMenuOption(ReachItem + ": this " + clicked.def.label + " only",
                    () => Find.WindowStack.Add(new FloatMenu(LookMenu(clicked, starts, LineReach.Item))))
            };
            int line = LineChanges(clicked.Map, starts, LineLookOf(clicked), out _).Count;
            opts.Add(new FloatMenuOption(ReachConnected + ": the whole connected line" + (starts.Count > 1 ? "s" : "") +
                (line > 0 ? " (" + line + " part" + (line == 1 ? "" : "s") + " now in other looks)" : ""),
                () => Find.WindowStack.Add(new FloatMenu(LookMenu(clicked, starts, LineReach.Connected)))));
            int all = MapParts(clicked.Map).Count;
            opts.Add(new FloatMenuOption(ReachMap + ": " + all + " FlowWorks part" + (all == 1 ? "" : "s") + " you own",
                () => Find.WindowStack.Add(new FloatMenu(LookMenu(clicked, starts, LineReach.Map)))));
            return opts;
        }

        public enum LineReach { Item, Connected, Map }
        public const string ReachItem = "This item", ReachConnected = "All connected", ReachMap = "All on map";

        /// <summary>Every styled FlowWorks line part the player owns on <paramref name="map"/>.</summary>
        public static List<Thing> MapParts(Map map)
        {
            var list = new List<Thing>();
            if (map == null) return list;
            foreach (Building b in map.listerBuildings.allBuildingsColonist)
                if (LineStyled(b.def)) list.Add(b);
            return list;
        }

        /// <summary>The second menu: the looks for that reach. "(current)" marks the clicked part's own look on the item reach.</summary>
        public static List<FloatMenuOption> LookMenu(Thing clicked, List<Thing> starts, LineReach reach)
        {
            string cur = LineLookOf(clicked);
            var opts = new List<FloatMenuOption>();
            foreach (string look in PipeStyles.Looks)
            {
                ThingStyleDef sd = LineStyleFor(clicked.def, look);
                if (sd == null && reach == LineReach.Item) continue;
                string l = look;
                opts.Add(new FloatMenuOption(look + (look == cur && reach == LineReach.Item ? " (current)" : ""),
                    () => PickReach(clicked, starts, l, reach), sd?.UIIcon, Color.white));
            }
            return opts;
        }

        /// <summary>Apply <paramref name="look"/> over <paramref name="reach"/>; returns the parts changed (lastLineChanged).</summary>
        public static int PickReach(Thing clicked, List<Thing> starts, string look, LineReach reach)
        {
            if (reach == LineReach.Connected) return PickLineLook(clicked, starts, look);
            IEnumerable<Thing> targets = reach == LineReach.Item ? (IEnumerable<Thing>)new[] { clicked } : MapParts(clicked.Map);
            bool pole = false;
            int n = 0;
            foreach (Thing t in targets)
            {
                if (LineStyleFor(t.def, look) == null || !SetLineLook(t, look)) continue;
                n++;
                pole |= t.def.defName == RM_PipePoles.PoleDef;
            }
            if (pole) RM_PipePoles.RedrawSpans();
            lastLineChanged = n;
            lastLineCapped = false;
            return n;
        }
    }

    /// <summary>
    /// RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY: the map as RM_LineLook reads it. A pipe vertex is its cell
    /// (IntVec3), every other vertex the Thing. Only FlowWorks' own spawned player things have a kind (owner 2026-11-22: each
    /// mod restyles its own items). Joins are physical: the pipe cells, the pole span edges in force, the members around a
    /// cell, the things touching a part, each reel's coupled body port, its laid hose's free-end port or relay reel. Liquid
    /// settings (flow, theft) are not read: a pick changes art only.
    /// </summary>
    internal sealed class MapLineGraph : IRM_LineGraph
    {
        internal const string OwnPackage = "mandrake.rm.flowworks";
        private readonly Map map;
        private readonly RM_PipeSpanEdges spans;
        private Dictionary<object, List<object>> hoses;

        public MapLineGraph(Map map)
        {
            this.map = map;
            spans = RM_PipePoles.EdgesFor(map);
        }

        internal static bool Ours(Thing t) => t != null && t.Spawned && t.Faction == Faction.OfPlayer
            && string.Equals(t.def?.modContentPack?.PackageId, OwnPackage, StringComparison.OrdinalIgnoreCase);

        private bool PipeCell(IntVec3 c)
        {
            if (!c.InBounds(map)) return false;
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++) if (RM_LiquidNet.IsPipe(l[i]) && Ours(l[i])) return true;
            return false;
        }

        public RM_LinePart KindOf(object v)
        {
            if (v is IntVec3 c) return PipeCell(c) ? RM_LinePart.Pipe : RM_LinePart.None;
            Thing t = v as Thing;
            if (!Ours(t) || t.Map != map) return RM_LinePart.None;
            if (RM_LiquidNet.IsPipe(t)) return RM_LinePart.Pipe;
            if (t is LiquidTypes.Building_LiquidTank) return RM_LinePart.Tank;
            if (t.TryGetComp<Hose.CompHoseReel>() != null) return RM_LinePart.Reel;
            if (RM_LiquidNet.RoleOfKind(t) == RM_NetRole.Machine) return RM_LinePart.Machine;
            string d = t.def.defName;
            if (d == Sprinklers.RM_SprinklerLook.FaucetDef || d == RM_PipePoles.PoleDef) return RM_LinePart.Fitting;
            return RM_LinePart.None;
        }

        public IEnumerable<object> PipeNeighbours(object cell)
        {
            var c = (IntVec3)cell;
            foreach (IntVec3 d in GenAdj.CardinalDirections)
            {
                IntVec3 n = c + d;
                if (n.InBounds(map) && RM_LiquidNet.HasPipe(n, map)) yield return n;
            }
            foreach (object n in spans.At(c)) yield return n;
        }

        private IEnumerable<object> ThingsIn(IEnumerable<IntVec3> cells, Thing except)
        {
            foreach (IntVec3 c in cells)
            {
                if (!c.InBounds(map)) continue;
                List<Thing> l = c.GetThingList(map);
                for (int i = 0; i < l.Count; i++) if (l[i] != except) yield return l[i];
            }
        }

        public IEnumerable<object> AroundCell(object cell)
        {
            var c = (IntVec3)cell;
            return ThingsIn(GenAdj.AdjacentCellsAndInside.Select(d => c + d), null);
        }

        public IEnumerable<object> PipeCellsAround(object part)
        {
            var t = (Thing)part;
            foreach (IntVec3 c in t.OccupiedRect().ExpandedBy(1))
                if (c.InBounds(map) && RM_LiquidNet.HasPipe(c, map)) yield return c;
        }

        public IEnumerable<object> Touching(object part)
        {
            var t = (Thing)part;
            return ThingsIn(t.OccupiedRect().ExpandedBy(1), t);
        }

        /// <summary>Every hose coupling on the map, both ways: reel -- its body port, reel -- its laid end's port or relay.</summary>
        private Dictionary<object, List<object>> Hoses()
        {
            if (hoses != null) return hoses;
            hoses = new Dictionary<object, List<object>>();
            Hose.RM_MapComponent_Hoses comp = map.GetComponent<Hose.RM_MapComponent_Hoses>();
            if (comp == null) return hoses;
            foreach (Hose.CompHoseReel r in comp.Reels)
            {
                if (r?.parent == null || !r.parent.Spawned || r.parent.Map != map) continue;
                Thing body = r.Port();
                if (body != null) Couple(r.parent, RM_LiquidNet.VertexOf(body));
                if (!r.laid) continue;
                Hose.HoseFreeEnd e = r.FreeEnd();
                if (e.Relay?.parent != null) Couple(r.parent, e.Relay.parent);
                else if (e.Port != null) Couple(r.parent, RM_LiquidNet.VertexOf(e.Port));
            }
            return hoses;
        }

        private void Couple(object a, object b)
        {
            if (a == null || b == null || Equals(a, b)) return;
            if (!hoses.TryGetValue(a, out List<object> la)) hoses[a] = la = new List<object>();
            if (!hoses.TryGetValue(b, out List<object> lb)) hoses[b] = lb = new List<object>();
            la.Add(b);
            lb.Add(a);
        }

        public IEnumerable<object> HoseJoins(object v) =>
            v != null && Hoses().TryGetValue(v, out List<object> l) ? l : (IEnumerable<object>)Array.Empty<object>();

        public IEnumerable<object> PartsOn(object cell)
        {
            var c = (IntVec3)cell;
            foreach (object o in ThingsIn(new[] { c }, null))
            {
                var t = (Thing)o;
                if (RM_LiquidNet.IsPipe(t) || t.def.defName == Sprinklers.RM_SprinklerLook.FaucetDef || t.def.defName == RM_PipePoles.PoleDef) yield return t;
            }
            // a pipe pole joins a pipe 8-way or from under it (RM_PipePoles.JoinCells): it is a part of the cells it joins
            foreach (object o in ThingsIn(GenAdj.AdjacentCells.Select(d => c + d), null))
                if (((Thing)o).def.defName == RM_PipePoles.PoleDef) yield return o;
        }

        public IEnumerable<object> FittingCells(object fitting)
        {
            var t = (Thing)fitting;
            if (t.def.defName == RM_PipePoles.PoleDef) return RM_PipePoles.JoinCells(t);
            return RM_LiquidNet.HasPipe(t.Position, map) ? new object[] { t.Position } : Array.Empty<object>();
        }
    }

    /// <summary>Null until PipeLook has run, so the hot patches never trigger its static constructor early.</summary>
    internal static class PipeStyleIndex
    {
        internal static StylePickerCore core;
    }

    /// <summary>The pipe's "Choose style" gizmo: always the whole connected run (never one piece).</summary>
    public class CompProperties_PipeLook : CompProperties
    {
        public CompProperties_PipeLook()
        {
            compClass = typeof(CompPipeLook);
        }
    }

    public class CompPipeLook : ThingComp
    {
        // PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY (owner 2026-10-23: "Pipes should ONLY have the \"choose style for the entire run\" option,
        // not per pipe. That's too fidgetty."): one option per look, never one piece; since 2026-11-22 the whole LINE, not the
        // same-def run (RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY).
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            Command_Action c = PipeLook.LineLookGizmo(parent);
            if (c != null) yield return c;
        }
    }

    /// <summary>The Choose style gizmo of a line part that had none (the sprinkler head, the pipe faucet, the pipe pole):
    /// the line's (PipeLook.LineLookGizmo).</summary>
    public class CompProperties_LineLook : CompProperties
    {
        public CompProperties_LineLook()
        {
            compClass = typeof(CompLineLook);
        }
    }

    public class CompLineLook : ThingComp
    {
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            Command_Action c = PipeLook.LineLookGizmo(parent);
            if (c != null) yield return c;
        }
    }

    /// <summary>
    /// TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH (owner 2026-10-16: "The tanks should have switchable art like everything else in
    /// here. I don't see the switch."): the four liquid tanks' "Choose style" gizmo, the reel's and the pipe's twin. The build
    /// button, copy and frame already carried a tank's look (PipeStyles.TankDefs through this picker); a BUILT tank had no
    /// way to change it. Since 2026-11-22 its whole connected line (PipeLook.LineLookGizmo), each part in its own def's style.
    /// Shown only once the tank's style defs are loaded (PipeLook.IsStyled).
    /// </summary>
    public class CompProperties_TankLook : CompProperties
    {
        public CompProperties_TankLook()
        {
            compClass = typeof(CompTankLook);
        }
    }

    public class CompTankLook : ThingComp
    {
        /// <summary>Restyle one tank in place (free, instant, art only) and redraw its whole footprint.</summary>
        public static bool SetLook(Thing tank, string look)
        {
            ThingStyleDef sd = PipeLook.StyleFor(tank?.def, look);
            if (sd == null || !tank.Spawned) return false;
            tank.SetStyleDef(sd);
            tank.Notify_ColorChanged();
            foreach (IntVec3 c in tank.OccupiedRect())
            {
                tank.Map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
            }
            return true;
        }

        /// <summary>Its Choose style is the line's (RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY, owner 2026-11-22):
        /// the tank or pump and every FlowWorks part on its connected line.</summary>
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            Command_Action c = PipeLook.LineLookGizmo(parent);
            if (c != null) yield return c;
        }
    }

    [PatchFeature("Universal pipe: look picker")]
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ProcessInput))]
    internal static class Patch_Pipe_DesignatorBuild_ProcessInput
    {
        private static void Postfix(Designator_Build __instance) => PipeStyleIndex.core?.ProcessInputPostfix(__instance, 0x5E1E72);
    }

    [PatchFeature("Universal pipe: look picker")]
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ThingStyleDefNonPreceptSource), MethodType.Getter)]
    internal static class Patch_Pipe_DesignatorBuild_StyleGetter
    {
        private static void Postfix(Designator_Build __instance, ref ThingStyleDef __result) => PipeStyleIndex.core?.StyleGetterPostfix(__instance, ref __result);
    }

    [PatchFeature("Universal pipe: look picker")]
    [HarmonyPatch(typeof(BuildCopyCommandUtility), nameof(BuildCopyCommandUtility.BuildCopyCommand))]
    internal static class Patch_Pipe_BuildCopyCommand_CarryStyle
    {
        private static void Prefix(BuildableDef buildable, ThingStyleDef style, ref bool styleOverridden) => PipeStyleIndex.core?.CopyPrefix(buildable, style, ref styleOverridden);
    }

    /// <summary>Legacy: a pipe with no stored style reads as the default look's style (hot path: one array read).</summary>
    [PatchFeature("Universal pipe: look picker")]
    [HarmonyPatch(typeof(Thing), nameof(Thing.StyleDef), MethodType.Getter)]
    internal static class Patch_Pipe_Thing_StyleDef
    {
        private static void Postfix(Thing __instance, ref ThingStyleDef __result) => PipeStyleIndex.core?.StyleDefPostfix(__instance, ref __result);
    }

    /// <summary>Frame.CompleteConstruction keeps the frame's style only for an ideo worker; re-apply it on the pipe.</summary>
    [PatchFeature("Universal pipe: look picker")]
    [HarmonyPatch(typeof(Frame), nameof(Frame.CompleteConstruction))]
    internal static class Patch_Pipe_Frame_KeepStyle
    {
        public static int restored => PipeStyleIndex.core?.restored ?? 0;

        private static void Prefix(Frame __instance, out StylePickerCore.FrameState __state) => __state = PipeStyleIndex.core?.FramePrefix(__instance);

        private static void Postfix(StylePickerCore.FrameState __state) => PipeStyleIndex.core?.FramePostfix(__state);
    }
}
