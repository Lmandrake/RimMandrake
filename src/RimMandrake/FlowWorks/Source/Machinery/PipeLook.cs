using System.Collections.Generic;
using HarmonyLib;
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

        /// <summary>Every pipe of the run that holds <paramref name="start"/> (cardinal pipe neighbours, like the net walk), capped
        /// at the net's own search cap.</summary>
        public static List<Thing> RunOf(Thing start)
        {
            var run = new List<Thing>();
            if (start?.Map == null) return run;
            Map map = start.Map;
            var seen = new HashSet<IntVec3> { start.Position };
            var q = new Queue<IntVec3>();
            q.Enqueue(start.Position);
            while (q.Count > 0 && run.Count < RM_LiquidNet.MaxPipeCells)
            {
                IntVec3 c = q.Dequeue();
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t.def == start.def) run.Add(t);
                }
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 n = c + d;
                    if (!n.InBounds(map) || seen.Contains(n)) continue;
                    seen.Add(n);
                    foreach (Thing t in n.GetThingList(map))
                    {
                        if (t.def == start.def) { q.Enqueue(n); break; }
                    }
                }
            }
            return run;
        }
    }

    /// <summary>Null until PipeLook has run, so the hot patches never trigger its static constructor early.</summary>
    internal static class PipeStyleIndex
    {
        internal static StylePickerCore core;
    }

    /// <summary>The pipe's "Choose style" gizmo: this pipe, or its whole connected run.</summary>
    public class CompProperties_PipeLook : CompProperties
    {
        public CompProperties_PipeLook()
        {
            compClass = typeof(CompPipeLook);
        }
    }

    public class CompPipeLook : ThingComp
    {
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (parent.Faction != Faction.OfPlayer || !PipeLook.IsStyled(parent.def)) yield break;
            yield return new Command_Action
            {
                defaultLabel = "Choose style",
                defaultDesc = "Change how this pipe looks (scrapper, industrial, modern, futuristic): this piece, or the whole connected run. " +
                              "Free and instant; it changes art only, never cost or function.",
                icon = parent.StyleDef?.UIIcon ?? (Texture2D)parent.def.uiIcon,
                action = () =>
                {
                    string cur = PipeLook.LookOfThing(parent);
                    var opts = new List<FloatMenuOption>();
                    foreach (string look in PipeStyles.Looks)
                    {
                        ThingStyleDef sd = PipeLook.StyleFor(parent.def, look);
                        if (sd == null) continue;
                        string l = look;
                        opts.Add(new FloatMenuOption(look + (look == cur ? " (current)" : "") + ": this pipe", () => PipeLook.SetLook(parent, l), sd.UIIcon, Color.white));
                        opts.Add(new FloatMenuOption(look + ": whole connected run", () =>
                        {
                            foreach (Thing t in PipeLook.RunOf(parent)) PipeLook.SetLook(t, l);
                        }, sd.UIIcon, Color.white));
                    }
                    Find.WindowStack.Add(new FloatMenu(opts));
                }
            };
        }
    }

    /// <summary>
    /// TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH (owner 2026-10-16: "The tanks should have switchable art like everything else in
    /// here. I don't see the switch."): the four liquid tanks' "Choose style" gizmo, the reel's and the pipe's twin. The build
    /// button, copy and frame already carried a tank's look (PipeStyles.TankDefs through this picker); a BUILT tank had no
    /// way to change it. This tank, or every selected tank (each in its own def's style). Shown only once the tank's style
    /// defs are loaded (PipeLook.IsStyled).
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

        /// <summary>The player's selected tanks that can take a look (the multi-select option's targets).</summary>
        private static List<Thing> SelectedTanks()
        {
            var list = new List<Thing>();
            foreach (object o in Find.Selector.SelectedObjectsListForReading)
            {
                if (o is Thing t && t.Faction == Faction.OfPlayer && t.TryGetComp<CompTankLook>() != null && PipeLook.IsStyled(t.def)) list.Add(t);
            }
            return list;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (parent.Faction != Faction.OfPlayer || !PipeLook.IsStyled(parent.def)) yield break;
            yield return new Command_Action
            {
                defaultLabel = "Choose style",
                defaultDesc = "Change how this " + parent.def.label + " looks (scrapper, industrial, modern, futuristic): this one, or every selected one. " +
                              "Free and instant; it changes art only, never cost, capacity or function.",
                icon = parent.StyleDef?.UIIcon ?? (Texture2D)parent.def.uiIcon,
                action = () =>
                {
                    string cur = PipeLook.LookOfThing(parent);
                    List<Thing> sel = SelectedTanks();
                    var opts = new List<FloatMenuOption>();
                    foreach (string look in PipeStyles.Looks)
                    {
                        ThingStyleDef sd = PipeLook.StyleFor(parent.def, look);
                        if (sd == null) continue;
                        string l = look;
                        opts.Add(new FloatMenuOption(look + (look == cur ? " (current)" : "") + ": this " + parent.def.label, () => SetLook(parent, l), sd.UIIcon, Color.white));
                        if (sel.Count > 1)
                            opts.Add(new FloatMenuOption(look + ": every selected one (" + sel.Count + ")", () =>
                            {
                                foreach (Thing t in sel) SetLook(t, l);
                            }, sd.UIIcon, Color.white));
                    }
                    Find.WindowStack.Add(new FloatMenu(opts));
                }
            };
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
