using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KeelHoist
{
    // Tether lock (design §2d). Building_GravEngine.CanLaunch is not virtual (RimSage-read), so a postfix: the ship
    // refuses to launch while a keel hoist standing on its substructure has its cable down.
    [RimMandrake.Shared.PatchFeature("Patch_GravEngine_TetherLock", typeof(KeelHoistSettings), "tetherLock")]
    [HarmonyPatch(typeof(Building_GravEngine), nameof(Building_GravEngine.CanLaunch))]
    public static class Patch_GravEngine_TetherLock
    {
        public static void Postfix(Building_GravEngine __instance, ref AcceptanceReport __result)
        {
            if (!RM_HoistKernel.TetherBlocksLaunch(__result.Accepted, KeelHoistSettings.tetherLock, __instance.Map != null, KeelHoistDefOf.RM_KeelHoist != null, true))
            {
                return;
            }
            foreach (Thing t in __instance.Map.listerThings.ThingsOfDef(KeelHoistDefOf.RM_KeelHoist))
            {
                if (t is RM_KeelHoist hoist && hoist.CableDown && __instance.ValidSubstructureAt(hoist.Position))
                {
                    __result = new AcceptanceReport("Reel in the keel hoist first.");
                    return;
                }
            }
        }
    }

    // Downed strangers and wild beasts (design §2b, the one engine gap: Dialog_EnterPortal passes
    // allowCapturableDownedPawns false, and vanilla's auto-capture list never holds a wild animal). Scoped to
    // RM_KeelHoist; the shared CaravanFormingUtility.AllSendablePawns is never patched.
    [HarmonyPatch(typeof(Dialog_EnterPortal), "AddPawnsToTransferables")]
    public static class Patch_DialogEnterPortal_HoistPawns
    {
        public static void Postfix(Dialog_EnterPortal __instance, MapPortal ___portal, List<TransferableOneWay> ___transferables)
        {
            if (!(___portal is RM_KeelHoist) || ___transferables == null)
            {
                return;
            }

            // Awake colonists are hidden when riding is off or the cable ends in a holder; HUTT_SLAVE_PIT_SITE_BUILD_1 /
            // HUTT_LOTTERY_CHUTE_BUILD_1: a buyer pit or chance chute never takes a free colonist.
            bool holderCable = ((RM_KeelHoist)___portal).targetHolder != null;
            bool buyerOrChute = ((RM_KeelHoist)___portal).targetHolder?.Buyer != null || ___portal is RM_ChanceChute;
            ___transferables.RemoveAll(tr => tr.AnyThing is Pawn p
                && RM_HoistKernel.DialogHidesPawn(KeelHoistSettings.colonistsMayRide, holderCable, buyerOrChute, p.IsColonist, p.Downed, p.IsSlave));

            if (!KeelHoistSettings.downedStrangersAndBeasts)
            {
                return;
            }

            var listed = new HashSet<Thing>(___transferables.SelectMany(tr => tr.things));
            Traverse add = Traverse.Create(__instance).Method("AddToTransferables", new[] { typeof(Thing) });
            foreach (Pawn p in ___portal.Map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (listed.Contains(p) || !IsLowerableCaptive(p))
                {
                    continue;
                }
                add.GetValue(p);
            }
        }

        public static bool IsLowerableCaptive(Pawn p)
        {
            return RM_HoistKernel.IsLowerableCaptive(p.Dead, p.Downed, p.Faction == Faction.OfPlayer, p.IsPrisonerOfColony || p.IsSlaveOfColony,
                p.RaceProps.allowedOnCaravan, p.IsQuestHelper() || p.IsQuestLodger(), p.RaceProps.Humanlike, p.guest != null,
                p.RaceProps.Humanlike && p.mindState.WillJoinColonyIfRescued, p.RaceProps.Animal, p.Faction == null);
        }
    }

    // The Open Line meter (design §2d, from GPT, adopted): rises while any cable on the map is down, falls slowly
    // after. Slice 1 ships the counter and its readout; site consequences read `level` later.
    public class RM_MapComponent_OpenLine : MapComponent
    {
        public float level;
        public const float RisePerHour = RM_HoistKernel.OpenLineRisePerHour;
        public const float FallPerHour = RM_HoistKernel.OpenLineFallPerHour;

        public RM_MapComponent_OpenLine(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (!RM_HoistKernel.OpenLineStepsNow(KeelHoistSettings.openLineMeter, Find.TickManager.TicksGame, KeelHoistDefOf.RM_KeelHoist != null))
            {
                return;
            }
            bool open = map.listerThings.ThingsOfDef(KeelHoistDefOf.RM_KeelHoist).Any(t => t is RM_KeelHoist h && h.CableDown);
            level = RM_HoistKernel.OpenLineNext(level, open);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref level, "level", 0f);
        }
    }

    public class ITab_HoistManifest : ITab
    {
        private Vector2 scroll;

        public ITab_HoistManifest()
        {
            size = new Vector2(460f, 420f);
            labelKey = "RM_HoistManifestTab";
        }

        public override bool IsVisible => SelThing is RM_KeelHoist;

        protected override void FillTab()
        {
            var hoist = SelThing as RM_KeelHoist;
            if (hoist == null)
            {
                return;
            }
            Rect rect = new Rect(0f, 0f, size.x, size.y).ContractedBy(10f);
            var lines = new List<string>();
            foreach (Thing t in hoist.InTransit)
            {
                lines.Add("on the cable: " + t.LabelCap);
            }
            for (int i = hoist.manifest.Count - 1; i >= 0; i--)
            {
                RM_HoistManifestEntry e = hoist.manifest[i];
                string when = GenDate.DateFullStringAt(GenDate.TickGameToAbs(e.tick), Find.WorldGrid.LongLatOf(hoist.Map.Tile));
                lines.Add(when + "  " + (e.up ? "UP  " : "DOWN  ") + e.label + "  (" + e.from + " -> " + e.to + ")"
                          + (e.captured ? "  captured" : ""));
            }
            if (lines.Count == 0)
            {
                lines.Add("Nothing has gone down or come up yet.");
            }
            string text = string.Join("\n", lines);
            float h = Text.CalcHeight(text, rect.width - 16f);
            Rect view = new Rect(0f, 0f, rect.width - 16f, h);
            Widgets.BeginScrollView(rect, ref scroll, view);
            Widgets.Label(view, text);
            Widgets.EndScrollView();
        }
    }
}
