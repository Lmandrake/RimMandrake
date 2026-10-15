using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1 mechanism 4a, rebuilt by PYRELANDS_FURNACE_WARMTH_AMBIENT_1 - the open-field
    /// "walking hearth". One kind of heat planet-wide (owner, 2026-09-29/30): there is no comfort-range
    /// hediff any more. The beast adds a LOCAL FELT-TEMPERATURE OFFSET to every pawn near it (+C at the
    /// beast, falling off linearly to 0 at the aura radius), through a postfix on Thing.AmbientTemperature,
    /// so vanilla hypothermia relief and Heatstroke do the work: "welcome company in the cold and
    /// terrible company in the dry" (the_pyrelands.md section 5) falls out of one number.
    ///
    /// WHY NOT A HEAT PUSHER (unchanged): vanilla spends pushed heat on the containing ROOM, and outdoors
    /// that is the whole map, so CompHeatPusher on a beast in open grass warms nothing. The beast still
    /// ships the vanilla pusher for barns and rooms; this comp is the open-field half, and enforces it
    /// (FURNACE_AURA_FIX_WARMS_THROUGH_WALLS): a pawn in an enclosed room gets no aura (the pusher already
    /// warms that room), and a wall between pawn and beast blocks it (line of sight). The vanilla pusher obeys
    /// the same "Furnace-beast thermal circuit" switch (Postfix_ShouldPushHeatNow).
    ///
    /// The aura radius is the thermal charge's output (FURNACEBEAST_THERMAL_CYCLE_1), exactly as before.
    /// </summary>
    public class CompProperties_FurnaceWarmthAura : CompProperties
    {
        public CompProperties_FurnaceWarmthAura()
        {
            compClass = typeof(CompFurnaceWarmthAura);
        }
    }

    public class CompFurnaceWarmthAura : ThingComp
    {
        /// <summary>Aura radius at zero charge, as a fraction of the full one. Not zero: a cold furnace-beast
        /// is still a very large warm animal. [INVENTED]</summary>
        internal const float MinAuraFraction = 0.35f;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            FurnaceWarmthField.Register(parent.Map, this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            FurnaceWarmthField.Unregister(map, this);
        }

        /// <summary>This beast's aura radius now, in cells (0 when the mechanism is switched off).</summary>
        internal float CurrentRadius()
        {
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.furnaceThermalEnabled
                || !(parent is Pawn beast) || !beast.Spawned || beast.Dead)
            {
                return 0f;
            }
            CompFurnaceThermalCharge charge = beast.TryGetComp<CompFurnaceThermalCharge>();
            float fullRadius = PyrelandsTuning.FurnaceAuraRadius
                * UnityEngine.Mathf.Sqrt(PyrelandsTuning.FurnaceSizeRatio(beast));   // giant: wider warmth
            return FurnaceWarmthMath.Radius(fullRadius, MinAuraFraction,
                charge != null, charge != null ? charge.Charge : 0f);
        }
    }

    /// <summary>The registry of live furnace-beasts per map and the AmbientTemperature postfix that reads it.
    /// Applied manually in the static ctor (same pattern as Patch_FurnaceBeastHeatImmunity).</summary>
    [StaticConstructorOnStartup]
    public static class FurnaceWarmthField
    {
        private static readonly Dictionary<Map, List<CompFurnaceWarmthAura>> byMap =
            new Dictionary<Map, List<CompFurnaceWarmthAura>>();

        static FurnaceWarmthField()
        {
            try
            {
                new Harmony("mandrake.rm.pyrelands.furnacewarmth").Patch(
                    AccessTools.PropertyGetter(typeof(Thing), nameof(Thing.AmbientTemperature)),
                    postfix: new HarmonyMethod(typeof(FurnaceWarmthField), nameof(Postfix_AmbientTemperature)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] furnace warmth: AmbientTemperature patch FAILED, the open-field warmth is OFF: " + e.Message);
            }
            try
            {
                new Harmony("mandrake.rm.pyrelands.furnacewarmth").Patch(
                    AccessTools.PropertyGetter(typeof(CompHeatPusher), nameof(CompHeatPusher.ShouldPushHeatNow)),
                    postfix: new HarmonyMethod(typeof(FurnaceWarmthField), nameof(Postfix_ShouldPushHeatNow)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] furnace warmth: ShouldPushHeatNow patch FAILED, the furnace-beast's room heat ignores its setting: " + e.Message);
            }
        }

        /// <summary>The furnace-beast's vanilla heat pusher (the room half) obeys the same switch as the aura: with the thermal
        /// circuit off the beast is "an ordinary heat-immune grazer" and warms no room either.</summary>
        public static void Postfix_ShouldPushHeatNow(CompHeatPusher __instance, ref bool __result)
        {
            if (__result && __instance.parent is Pawn p && (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.furnaceThermalEnabled)
                && p.TryGetComp<CompFurnaceWarmthAura>() != null)
            {
                __result = false;
            }
        }

        // The game the registry belongs to: quitting to the menu despawns nothing, so a new Game clears every old Map out.
        private static Game ownerGame;

        private static void ForgetOtherGames()
        {
            if (ownerGame != Current.Game)
            {
                byMap.Clear();
                ownerGame = Current.Game;
            }
        }

        internal static void Register(Map map, CompFurnaceWarmthAura comp)
        {
            if (map == null) return;
            ForgetOtherGames();
            // A map removed without its beasts despawning (a game reload, a closed temporary map) leaves its key here, holding
            // the whole dead Map; drop every key that is no longer a live map before adding.
            if (byMap.Count > 0)
            {
                List<Map> live = Find.Maps;
                List<Map> dead = null;
                foreach (Map m in byMap.Keys)
                {
                    if (live == null || !live.Contains(m)) (dead ?? (dead = new List<Map>())).Add(m);
                }
                if (dead != null) foreach (Map m in dead) byMap.Remove(m);
            }
            if (!byMap.TryGetValue(map, out List<CompFurnaceWarmthAura> l))
            {
                byMap[map] = l = new List<CompFurnaceWarmthAura>();
            }
            if (!l.Contains(comp)) l.Add(comp);
        }

        /// <summary>A map was removed (MapComponent_PyrelandsAshField.MapRemoved): its beasts never despawn, so forget it whole.</summary>
        internal static void ForgetMap(Map map)
        {
            if (map != null) byMap.Remove(map);
        }

        internal static void Unregister(Map map, CompFurnaceWarmthAura comp)
        {
            if (map != null && byMap.TryGetValue(map, out List<CompFurnaceWarmthAura> l))
            {
                l.Remove(comp);
                if (l.Count == 0) byMap.Remove(map);
            }
        }

        /// <summary>Felt-temperature offset this pawn gets from furnace-beasts on its map, in degrees C. Open field only: none in
        /// an enclosed room, none through a wall (FurnaceWarmthMath.AuraReaches).</summary>
        public static float OffsetFor(Pawn pawn)
        {
            if (byMap.Count == 0 || pawn == null || !pawn.Spawned
                || !byMap.TryGetValue(pawn.Map, out List<CompFurnaceWarmthAura> beasts))
            {
                return 0f;
            }
            Map map = pawn.Map;
            float best = 0f;
            bool? enclosed = null;
            for (int i = 0; i < beasts.Count; i++)
            {
                Pawn beast = beasts[i].parent as Pawn;
                if (beast == null || beast == pawn || beast.Map != map) continue;
                float radius = beasts[i].CurrentRadius();
                if (radius <= 0f) continue;
                float d2 = (pawn.Position - beast.Position).LengthHorizontalSquared;
                if (d2 >= radius * radius) continue;
                if (enclosed == null)
                {
                    Room room = pawn.GetRoom();
                    enclosed = room != null && !room.UsesOutdoorTemperature;
                }
                if (!FurnaceWarmthMath.AuraReaches(enclosed.Value, GenSight.LineOfSight(beast.Position, pawn.Position, map, skipFirstCell: true)))
                {
                    continue;
                }
                best = FurnaceWarmthMath.Combine(best, FurnaceWarmthMath.Offset(d2, radius,
                    PyrelandsTuning.FurnaceWarmthMaxC, RM_PyrelandsSettings.furnaceWarmthStrength));
            }
            return best;
        }

        public static void Postfix_AmbientTemperature(Thing __instance, ref float __result)
        {
            if (byMap.Count == 0 || !(__instance is Pawn pawn))
            {
                return;
            }
            if (ownerGame != Current.Game)
            {
                ForgetOtherGames();
                return;
            }
            try
            {
                __result += OffsetFor(pawn);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RimMandrake.Pyrelands] furnace warmth: " + e, 0x4E7F0A1);
            }
        }
    }
}
