using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Ninefold
{
    // ════════════════════════════════════════════════════════════════════
    // NINEFOLD_FAVOUR_ODDS_BUILD_1 — the two offerings' shared state.
    // Spec: design/Jawa/nine_faults_permanent_rite_2026-10-01.md §2, §3, §5.
    //
    //  * FRESH FIND (§2): a machine the clan took ON THIS MAP and has never
    //    run. Marked when taken, cleared on first use or at departure. The
    //    Nine Faults rite (NineFaults.cs) may only burn out a fresh find.
    //  * LEAVE BEHIND (§3): one working building the player has marked to
    //    be left on the old map when the gravship departs.
    //
    // Both live on a MapComponent: a find carried to the next map is "simply
    // the clan's machine", and an abandoned map takes its component with it.
    //
    // Seams (§5 called them UNVERIFIED; chosen here from decompiled 1.6):
    //   taken    Designator_Claim.DesignateThing (a ruin/wreck building
    //            claimed) and Blueprint_Install.TryReplaceWithSolidThing when
    //            the installed inner thing was NOT already the player's
    //            (a dropped / crashed / dug-up / uninstalled-unowned minified
    //            machine). A player reinstalling its own machine never marks.
    //   used     CompPowerTrader.PowerOn set true (switched on and powered),
    //            Building_WorkTable.UsedThisTick (worked at). A find that
    //            is ALREADY powered when looked at is treated as run.
    //   departed WorldComponent_GravshipController.InitiateTakeoff commits
    //            (same commit marker Patch_GravshipLaunched uses).
    // ════════════════════════════════════════════════════════════════════

    public static class OfferingUtility
    {
        // A "machine": something with a power trader / plant / battery, or
        // one that can break down. Conduits (transmitter only) are not.
        public static bool IsMachine(Thing t)
        {
            if (!(t is Building b) || b.def.IsFrame) return false;
            return b.TryGetComp<CompPowerTrader>() != null
                || b.TryGetComp<CompPowerBattery>() != null
                || b.TryGetComp<CompBreakdownable>() != null;
        }

        public static bool IsRunningNow(Building b)
        {
            if (b == null) return false;
            CompPowerTrader p = b.TryGetComp<CompPowerTrader>();
            return p != null && p.PowerOn && p.PowerNet != null;
        }

        public static bool IsWorking(Building b)
        {
            return b != null && b.Spawned && !b.Destroyed && b.HitPoints > 0 && !b.IsBrokenDown();
        }

        // §2/§3: "sized by market value (Ninefold's Small 3 to Large 15)".
        // 🔴 UNTUNED: the value ramp 200..3000 silver is a first pass, same
        // status as EventMagnitude itself.
        public const float ValueAtSmall = 200f;
        public const float ValueAtLarge = 3000f;

        public static float TransferFor(Thing t)
        {
            float v = t.MarketValue;
            float k = Mathf.InverseLerp(ValueAtSmall, ValueAtLarge, v);
            return Mathf.Lerp(EventMagnitude.Small, EventMagnitude.Large, k);
        }

        public static void Transfer(God from, God to, float amount, string reason)
        {
            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null || amount <= 0f) return;
            comp.ApplyDelta(from, -amount, reason);
            comp.ApplyDelta(to, amount, reason);
        }
    }

    public class MapComponent_NinefoldOfferings : MapComponent
    {
        // Static fast path for the per-tick UsedThisTick hook: false while no
        // map holds a fresh find. Recomputed on every change and on load.
        public static bool AnyFresh;

        private HashSet<int> freshFinds = new HashSet<int>();
        private int leaveBehindId = -1;

        public MapComponent_NinefoldOfferings(Map map) : base(map) { }

        public static MapComponent_NinefoldOfferings For(Map map) =>
            map?.GetComponent<MapComponent_NinefoldOfferings>();

        private static void RecomputeAnyFresh()
        {
            AnyFresh = false;
            if (Find.Maps == null) return;
            foreach (Map m in Find.Maps)
            {
                var c = For(m);
                if (c != null && c.freshFinds.Count > 0) { AnyFresh = true; return; }
            }
        }

        // ---- fresh finds --------------------------------------------------
        public void MarkFresh(Thing t, string how)
        {
            if (!RM_NinefoldSettings.engineEnabled || !RM_NinefoldSettings.offeringsEnabled) return;
            if (!OfferingUtility.IsMachine(t)) return;
            if (freshFinds.Add(t.thingIDNumber))
            {
                AnyFresh = true;
                if (Prefs.DevMode)
                    Log.Message("[Ninefold] fresh find marked (" + how + "): " + t);
            }
        }

        public void ClearFresh(Thing t, string why)
        {
            if (t != null && freshFinds.Remove(t.thingIDNumber))
            {
                if (Prefs.DevMode)
                    Log.Message("[Ninefold] fresh find cleared (" + why + "): " + t);
                RecomputeAnyFresh();
            }
        }

        public void ClearAllFresh(string why)
        {
            if (freshFinds.Count == 0) return;
            if (Prefs.DevMode)
                Log.Message("[Ninefold] " + freshFinds.Count + " fresh find(s) cleared (" + why + ")");
            freshFinds.Clear();
            RecomputeAnyFresh();
        }

        // A fresh find, still standing, still the clan's, never run. A find
        // seen running is cleared here as well (a claimed machine already on
        // a live grid never fires the PowerOn setter).
        public bool IsFresh(Thing t)
        {
            if (!RM_NinefoldSettings.engineEnabled || !RM_NinefoldSettings.offeringsEnabled) return false;
            if (!(t is Building b) || !freshFinds.Contains(b.thingIDNumber)) return false;
            if (!b.Spawned || b.Map != map || b.Faction != Faction.OfPlayer) return false;
            if (OfferingUtility.IsRunningNow(b))
            {
                ClearFresh(b, "found running");
                return false;
            }
            return true;
        }

        public IEnumerable<Building> FreshBuildings()
        {
            if (freshFinds.Count == 0) yield break;
            foreach (Building b in map.listerBuildings.allBuildingsColonist.ToList())
            {
                if (freshFinds.Contains(b.thingIDNumber) && IsFresh(b))
                    yield return b;
            }
        }

        // ---- leave behind -------------------------------------------------
        public bool IsMarkedLeaveBehind(Thing t) => t != null && t.thingIDNumber == leaveBehindId;

        public void SetLeaveBehind(Thing t, bool on)
        {
            if (on) leaveBehindId = t.thingIDNumber;
            else if (IsMarkedLeaveBehind(t)) leaveBehindId = -1;
        }

        public Building LeaveBehindBuilding()
        {
            if (leaveBehindId < 0) return null;
            return map.listerBuildings.allBuildingsColonist.FirstOrDefault(b => b.thingIDNumber == leaveBehindId);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            RecomputeAnyFresh();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref freshFinds, "freshFinds", LookMode.Value);
            Scribe_Values.Look(ref leaveBehindId, "leaveBehindId", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && freshFinds == null)
                freshFinds = new HashSet<int>();
        }
    }

    // ---- taken: claimed in place ------------------------------------------
    [HarmonyPatch(typeof(Designator_Claim), nameof(Designator_Claim.DesignateThing))]
    public static class Patch_FreshFind_Claimed
    {
        [HarmonyPostfix]
        public static void Postfix(Thing t)
        {
            if (t == null || !t.Spawned || t.Faction != Faction.OfPlayer) return;
            if (OfferingUtility.IsRunningNow(t as Building)) return;
            MapComponent_NinefoldOfferings.For(t.Map)?.MarkFresh(t, "claimed");
        }
    }

    // ---- taken: a found minified machine installed ------------------------
    [HarmonyPatch(typeof(Blueprint_Install), nameof(Blueprint_Install.TryReplaceWithSolidThing))]
    public static class Patch_FreshFind_Installed
    {
        [HarmonyPrefix]
        public static void Prefix(Blueprint_Install __instance, out bool __state)
        {
            Thing inner = null;
            try { inner = __instance.ThingToInstall; } catch { }
            __state = inner != null && inner.Faction != Faction.OfPlayer;
        }

        [HarmonyPostfix]
        public static void Postfix(bool __result, Thing createdThing, bool __state)
        {
            if (!__result || !__state || createdThing == null || !createdThing.Spawned) return;
            MapComponent_NinefoldOfferings.For(createdThing.Map)?.MarkFresh(createdThing, "found and installed");
        }
    }

    // ---- used: switched on and powered ------------------------------------
    [HarmonyPatch(typeof(CompPowerTrader), nameof(CompPowerTrader.PowerOn), MethodType.Setter)]
    public static class Patch_FreshFind_PoweredOn
    {
        [HarmonyPostfix]
        public static void Postfix(CompPowerTrader __instance)
        {
            if (!MapComponent_NinefoldOfferings.AnyFresh || !__instance.PowerOn) return;
            Thing p = __instance.parent;
            if (p == null || !p.Spawned) return;
            MapComponent_NinefoldOfferings.For(p.Map)?.ClearFresh(p, "powered on");
        }
    }

    // ---- used: worked at --------------------------------------------------
    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.UsedThisTick))]
    public static class Patch_FreshFind_WorkedAt
    {
        [HarmonyPostfix]
        public static void Postfix(Building_WorkTable __instance)
        {
            if (!MapComponent_NinefoldOfferings.AnyFresh || !__instance.Spawned) return;
            MapComponent_NinefoldOfferings.For(__instance.Map)?.ClearFresh(__instance, "worked at");
        }
    }

    // ---- departed: the ship lifts -----------------------------------------
    // Same commit marker as Patch_GravshipLaunched (CutsceneInProgress
    // false->true across InitiateTakeoff). A find carried aboard lands on a
    // new map whose component never marked it; finds left on an anchored map
    // lose their chance here.
    [HarmonyPatch(typeof(WorldComponent_GravshipController),
                  nameof(WorldComponent_GravshipController.InitiateTakeoff))]
    public static class Patch_FreshFind_Departed
    {
        [HarmonyPrefix]
        public static void Prefix(out bool __state)
        {
            __state = WorldComponent_GravshipController.CutsceneInProgress;
        }

        [HarmonyPostfix]
        public static void Postfix(Building_GravEngine engine, bool __state)
        {
            if (__state || !WorldComponent_GravshipController.CutsceneInProgress) return;
            MapComponent_NinefoldOfferings.For(engine?.Map)?.ClearAllFresh("the ship departed");
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // The Left Behind (§3): Ta'Baa gains and Ohm loses, always, whatever the
    // machine. Rekko is unaffected. Sized by market value.
    // ════════════════════════════════════════════════════════════════════

    [HarmonyPatch(typeof(Building), nameof(Building.GetGizmos))]
    public static class Patch_LeaveBehind_Gizmo
    {
        private static Texture2D icon;

        [HarmonyPostfix]
        public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Building __instance)
        {
            foreach (Gizmo g in __result)
                yield return g;

            if (!ModsConfig.OdysseyActive) yield break;
            if (!RM_NinefoldSettings.engineEnabled || !RM_NinefoldSettings.offeringsEnabled) yield break;
            if (__instance.Faction != Faction.OfPlayer || !__instance.Spawned) yield break;
            if (!__instance.Map.IsPlayerHome || !OfferingUtility.IsMachine(__instance)) yield break;
            var comp = MapComponent_NinefoldOfferings.For(__instance.Map);
            if (comp == null) yield break;

            if (icon == null) icon = ContentFinder<Texture2D>.Get("UI/Commands/AbandonHome");
            Building b = __instance;
            yield return new Command_Toggle
            {
                defaultLabel = "Leave behind",
                defaultDesc = "Mark this machine to be left on this ground when the gravship departs. "
                    + "It must be off the ship and in working order when the ship lifts; it is lost "
                    + "forever. Only one thing can be marked at a time.",
                icon = icon,
                isActive = () => comp.IsMarkedLeaveBehind(b),
                toggleAction = () => comp.SetLeaveBehind(b, !comp.IsMarkedLeaveBehind(b)),
            };
        }
    }

    // RimSage-verified 2026-10-06: GravshipUtility.AbandonMap(Map) is called
    // only from WorldComponent_GravshipController.TakeoffEnded, and only when
    // the map has NO grav anchor. On an anchored map nothing is abandoned, so
    // nothing is lost forever and no favour moves — the mark simply waits.
    [HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.AbandonMap))]
    public static class Patch_LeaveBehind_Departure
    {
        [HarmonyPrefix]
        public static void Prefix(Map map)
        {
            if (!RM_NinefoldSettings.engineEnabled || !RM_NinefoldSettings.offeringsEnabled) return;
            var comp = MapComponent_NinefoldOfferings.For(map);
            Building left = comp?.LeaveBehindBuilding();
            if (left == null || !OfferingUtility.IsWorking(left)) return;

            float amount = OfferingUtility.TransferFor(left);
            OfferingUtility.Transfer(God.Ohm, God.TaBaa, amount, "the Left Behind: " + left.def.defName);

            // §3 sign. Names what was left; never names a god as the cause.
            Find.LetterStack.ReceiveLetter(
                "Left behind: " + left.LabelCap,
                "The clan left the " + left.LabelNoCount + " standing on the old ground, still in "
                    + "working order, and did not look back.\n\nFrom the climbing ship, it glinted "
                    + "once, like a wave.",
                LetterDefOf.NeutralEvent);
        }
    }
}
