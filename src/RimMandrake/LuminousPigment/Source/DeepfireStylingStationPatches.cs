using System.Collections.Generic;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORN_GLOW_1, spec §3.4 path 3: a per-item Deepfire checkbox
    // beside each apparel row's colour picker in Ideology's
    // Dialog_StylingStation. Dialog_StylingStation lives in Assembly-CSharp
    // itself (not a DLC assembly), so a direct typeof() reference loads on
    // any install; every DLC is a shipping prerequisite (owner 2026-09-26),
    // so no Ideology-absent path is built.
    //
    // Deviation from the spec's mechanism, MEASURED from RimSage
    // RimWorld/Dialog_StylingStation.cs DrawBottomButtons: vanilla orders
    // JobDriver_UseStylingStation ONLY when hair/beard/tattoo/body changed;
    // an apparel-colour-only Accept sets Apparel.DesiredColor and closes,
    // with no styling job at all. A postfix on UseStylingStation's finish
    // would therefore never fire for "tick Deepfire, change nothing else".
    // Instead, Accept's ApplyApparelColors postfix queues one
    // RM_LacquerWornItem job per ticked item, targeted at THIS styling
    // station -- same fetch, same cost, same AddCoat as the press path.
    //
    // Layout: the rows are drawn inside DrawApparelColor's scroll view with
    // no per-row hook, so the checkbox is drawn in a postfix after the view
    // closes, re-deriving each row's y from the same constants vanilla uses
    // (92 row + 10 gap + 34 button strip; buttons at row+102, 200 wide,
    // 210 pitch) minus the scroll offset, clipped to the view rect.
    public static class StylingStationLacquer
    {
        private const float RowHeight = 92f;
        private const float RowGap = 10f;
        private const float ButtonStrip = 34f;
        private const float ButtonHeight = 24f;
        private const float ButtonPitch = 210f;
        private const float CheckboxWidth = 220f;
        private const float ScrollbarWidth = 16f;

        private static readonly ConditionalWeakTable<Dialog_StylingStation, HashSet<Apparel>> ticked =
            new ConditionalWeakTable<Dialog_StylingStation, HashSet<Apparel>>();

        internal static readonly AccessTools.FieldRef<Dialog_StylingStation, Pawn> PawnRef =
            AccessTools.FieldRefAccess<Dialog_StylingStation, Pawn>("pawn");
        internal static readonly AccessTools.FieldRef<Dialog_StylingStation, Thing> StationRef =
            AccessTools.FieldRefAccess<Dialog_StylingStation, Thing>("stylingStation");
        private static readonly AccessTools.FieldRef<Dialog_StylingStation, Dictionary<Apparel, Color>> ColorsRef =
            AccessTools.FieldRefAccess<Dialog_StylingStation, Dictionary<Apparel, Color>>("apparelColors");
        private static readonly AccessTools.FieldRef<Dialog_StylingStation, Vector2> ScrollRef =
            AccessTools.FieldRefAccess<Dialog_StylingStation, Vector2>("apparelColorScrollPosition");

        internal static HashSet<Apparel> TickedFor(Dialog_StylingStation dlg) => ticked.GetOrCreateValue(dlg);

        public static int AvailableDeepfire(Map map)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Deepfire");
            if (map == null || def == null) return 0;
            int n = 0;
            List<Thing> stacks = map.listerThings.ThingsOfDef(def);
            for (int i = 0; i < stacks.Count; i++)
            {
                if (!stacks[i].IsForbidden(Faction.OfPlayer)) n += stacks[i].stackCount;
            }
            return n;
        }

        public static void DrawCheckboxes(Dialog_StylingStation dlg, Rect rect)
        {
            if (!LuminousPigmentSettings.stylingStationLacquer) return;
            Pawn pawn = PawnRef(dlg);
            Dictionary<Apparel, Color> colors = ColorsRef(dlg);
            if (pawn?.apparel == null || colors == null) return;
            bool devMode = StationRef(dlg) == null;
            HashSet<Apparel> set = TickedFor(dlg);
            float scrollY = ScrollRef(dlg).y;

            int reserved = 0;
            foreach (Apparel a in set) reserved += LacquerWornItemUtility.CostFor(a);
            int available = pawn.Spawned ? AvailableDeepfire(pawn.Map) : 0;

            GUI.BeginGroup(rect);
            float y = 0f;
            foreach (Apparel item in pawn.apparel.WornApparel)
            {
                if (!colors.ContainsKey(item)) continue; // vanilla skips the row too
                float rowTop = y;
                y += RowHeight + RowGap + ButtonStrip;
                if (pawn.apparel.IsLocked(item) && !devMode) continue;

                CompDeepfire comp = item.GetComp<CompDeepfire>();
                if (comp == null) continue;

                // Right of the ideo-colour and favourite-colour buttons.
                Rect box = new Rect(2f * ButtonPitch, rowTop + RowHeight + RowGap - scrollY,
                    Mathf.Min(CheckboxWidth, rect.width - ScrollbarWidth - 2f * ButtonPitch), ButtonHeight);
                if (box.yMax < 0f || box.y > rect.height || box.width <= 0f) continue;

                int cost = LacquerWornItemUtility.CostFor(item);
                bool on = set.Contains(item);
                bool enabled = on || (comp.CanAddCoat && (devMode || available - reserved >= cost));
                bool before = on;
                Widgets.CheckboxLabeled(box, "Deepfire coat (" + cost + ")", ref on, disabled: !enabled);
                if (on != before)
                {
                    if (on) set.Add(item); else set.Remove(item);
                }
                TooltipHandler.TipRegion(box, !comp.CanAddCoat
                    ? "Already carries the maximum number of deepfire coats."
                    : "Add one deepfire coat (" + comp.coats + " now). The pawn fetches " + cost
                      + " deepfire and lacquers it here after you accept.");
            }
            GUI.EndGroup();
        }

        public static void Apply(Dialog_StylingStation dlg)
        {
            HashSet<Apparel> set = TickedFor(dlg);
            if (set.Count == 0) return;
            Pawn pawn = PawnRef(dlg);
            Thing station = StationRef(dlg);
            foreach (Apparel item in set)
            {
                QueueLacquer(pawn, station, item);
            }
            set.Clear();
        }

        // Also the dev proof's entry point (DeepfireWornGlowDebugActions).
        public static bool QueueLacquer(Pawn pawn, Thing station, ThingWithComps item)
        {
            if (pawn == null || item == null) return false;
            if (station == null) // dev-mode dialog: no station, apply directly
            {
                item.GetComp<CompDeepfire>()?.AddCoat();
                return true;
            }
            Job job = LacquerWornItemUtility.MakeJob(pawn, item, station, out string why);
            if (job == null)
            {
                Messages.Message(item.LabelCap + ": " + why, pawn, MessageTypeDefOf.RejectInput, historical: false);
                return false;
            }
            return pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc, requestQueueing: true);
        }
    }

    [HarmonyPatch(typeof(Dialog_StylingStation), "DrawApparelColor")]
    public static class Patch_DialogStylingStation_DrawApparelColor
    {
        public static void Postfix(Dialog_StylingStation __instance, Rect rect)
        {
            StylingStationLacquer.DrawCheckboxes(__instance, rect);
        }
    }

    [HarmonyPatch(typeof(Dialog_StylingStation), "ApplyApparelColors")]
    public static class Patch_DialogStylingStation_ApplyApparelColors
    {
        public static void Postfix(Dialog_StylingStation __instance)
        {
            StylingStationLacquer.Apply(__instance);
        }
    }
}
