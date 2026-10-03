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
    [HarmonyPatch(typeof(Building_GravEngine), nameof(Building_GravEngine.CanLaunch))]
    public static class Patch_GravEngine_TetherLock
    {
        public static void Postfix(Building_GravEngine __instance, ref AcceptanceReport __result)
        {
            if (!__result.Accepted || !KeelHoistSettings.tetherLock || __instance.Map == null || KeelHoistDefOf.RM_KeelHoist == null)
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

            if (!KeelHoistSettings.colonistsMayRide || ((RM_KeelHoist)___portal).targetHolder != null)
            {
                ___transferables.RemoveAll(tr => tr.AnyThing is Pawn p && p.IsColonist && !p.Downed);
            }

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
            if (p.Dead || !p.Downed || p.Faction == Faction.OfPlayer || p.IsPrisonerOfColony || p.IsSlaveOfColony)
            {
                return false;
            }
            if (!p.RaceProps.allowedOnCaravan || p.IsQuestHelper() || p.IsQuestLodger())
            {
                return false;
            }
            if (p.RaceProps.Humanlike)
            {
                return p.guest != null && !p.mindState.WillJoinColonyIfRescued;
            }
            return p.RaceProps.Animal && p.Faction == null;
        }
    }

    // The Open Line meter (design §2d, from GPT, adopted): rises while any cable on the map is down, falls slowly
    // after. Slice 1 ships the counter and its readout; site consequences read `level` later.
    public class RM_MapComponent_OpenLine : MapComponent
    {
        public float level;
        public const float RisePerHour = 1f;
        public const float FallPerHour = 0.5f;

        public RM_MapComponent_OpenLine(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (!KeelHoistSettings.openLineMeter || Find.TickManager.TicksGame % GenDate.TicksPerHour != 137 || KeelHoistDefOf.RM_KeelHoist == null)
            {
                return;
            }
            bool open = map.listerThings.ThingsOfDef(KeelHoistDefOf.RM_KeelHoist).Any(t => t is RM_KeelHoist h && h.CableDown);
            level = open ? level + RisePerHour : Mathf.Max(0f, level - FallPerHour);
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
