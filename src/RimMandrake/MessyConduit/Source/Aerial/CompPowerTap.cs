using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// The one-way power tap (design 2.7; owner 2026-10-02: build it now). A clamp bitten onto another faction's
    /// transmitter drains that grid into ours WITHOUT merging the two nets.
    ///
    /// Mechanism (decompiled 1.6, RimSage 2026-10-02):
    /// * A transmitter would merge by adjacency (ContiguousPowerBuildings ignores faction) and every vanilla generator
    ///   IS a transmitter, so the clamp is NOT one: its power comp is a plain CompPowerTrader (ThingDef.ConnectToPower
    ///   requires that exact class) with a negative base consumption, so PowerNet counts it as a power source. It
    ///   hooks up to OUR grid as a connector; this comp writes its PowerOutput every tick = what it stole.
    /// * PowerConnectionMaker.BestTransmitterForConnector has no faction check, and the victim's conduit is the
    ///   nearest transmitter by construction, so Patch_TryConnect_TapOwnFaction hands it every foreign net as
    ///   disallowed and Patch_ConnectToTransmitter_TapGuard refuses any other route onto a foreign transmitter.
    /// * The victim pays through vanilla's own books: Patch_PowerNet_GainRate_TapDebit subtracts this tick's stolen
    ///   energy from the victim net's CurrentEnergyGainRate, so PowerNetTick drains their batteries and browns out
    ///   their machines exactly as an extra consumer would -- with no consumer of ours in their net.
    /// Consequences (alerts, goodwill, raids) are a later design: TapEvents.Drained is the hook.
    /// </summary>
    public class CompProperties_PowerTap : CompProperties
    {
        public CompProperties_PowerTap() => compClass = typeof(CompPowerTap);
    }

    public class CompPowerTap : ThingComp
    {
        public float stolenTotalWd;
        public float lastStolenW;
        public int victimNetHash;
        public string victimFaction;
        private float sinceEventWd;
        private CompPowerTrader trader;

        public CompPowerTrader Trader => trader ??= parent.GetComp<CompPowerTrader>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map.GetComponent<RM_MapComponent_Aerial>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map.GetComponent<RM_MapComponent_Aerial>()?.Deregister(this);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref stolenTotalWd, "rmTapStolenTotal");
        }

        /// <summary>The foreign net the clamp is biting: a cardinally adjacent transmitter whose faction is not ours.</summary>
        public PowerNet VictimNet(out Thing victimThing)
        {
            victimThing = null;
            Map map = parent.Map;
            foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(parent.Position, parent.Rotation, parent.def.size))
            {
                if (!c.InBounds(map)) continue;
                Building tr = c.GetTransmitter(map);
                PowerNet n = tr == null || tr.Faction == parent.Faction ? null : RM_MapComponent_Aerial.Registered(map, tr.PowerComp?.PowerNet);
                if (n == null) continue;
                victimThing = tr;
                return n;
            }
            return null;
        }

        public override void CompTick()
        {
            base.CompTick();
            CompPowerTrader t = Trader;
            if (t == null || !parent.Spawned) return;
            PowerNet ours = RM_MapComponent_Aerial.Registered(parent.Map, t.PowerNet);
            PowerNet victim = VictimNet(out Thing vt);
            victimNetHash = victim == null ? 0 : System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(victim);
            victimFaction = vt?.Faction?.Name ?? (vt != null ? "no faction" : null);
            float stolenWd = 0f;
            if (victim != null && ours != null)
            {
                TapRegistry.bypass++;
                float rawGain, stored;
                try { rawGain = victim.CurrentEnergyGainRate(); stored = victim.CurrentStoredEnergy(); }
                finally { TapRegistry.bypass--; }
                stolenWd = (float)AerialMath.TapStolenPerTick(AerialSettings.tapRate, rawGain, stored, CompPower.WattsToWattDaysPerTick,
                    victim == ours, AerialSettings.tapsEnabled && AerialSettings.enabled);
            }
            if (stolenWd > 0f) TapRegistry.Debit(victim, stolenWd);
            lastStolenW = stolenWd / CompPower.WattsToWattDaysPerTick;
            stolenTotalWd += stolenWd;
            sinceEventWd += stolenWd;
            if (!t.PowerOn && lastStolenW > 0f && FlickUtility.WantsToBeOn(parent) && !parent.IsBrokenDown()) t.PowerOn = true;
            t.PowerOutput = t.PowerOn ? lastStolenW : 0f;
            if (parent.IsHashIntervalTick(250) && sinceEventWd > 0f)
            {
                if (AerialSettings.tapEvents) TapEvents.Raise(parent, vt, sinceEventWd);
                sinceEventWd = 0f;
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!AerialSettings.tapsEnabled) return "Power taps are switched off in Mod Settings.";
            PowerNet v = VictimNet(out Thing vt);
            if (v == null) return "Not biting anyone's conduit.";
            if (Trader?.PowerNet == null) return "Biting " + (vt.Faction?.Name ?? "an unowned") + " grid; no cable of ours within 6 cells to bring it home.";
            return "Draining " + lastStolenW.ToString("0") + " W from " + (vt.Faction?.Name ?? "an unowned") + " grid (" + stolenTotalWd.ToString("0") + " Wd so far).";
        }
    }

    /// <summary>Per-net energy the taps took THIS tick (watt-days), read by the CurrentEnergyGainRate postfix.</summary>
    public static class TapRegistry
    {
        private struct Entry { public int tick; public float wd; }
        private static readonly Dictionary<PowerNet, Entry> debits = new Dictionary<PowerNet, Entry>();
        [ThreadStatic] internal static int bypass;
        public static int Count => debits.Count;

        public static void Debit(PowerNet net, float wd)
        {
            int now = Find.TickManager.TicksGame;
            debits.TryGetValue(net, out Entry e);
            if (e.tick != now) { e.tick = now; e.wd = 0f; }
            e.wd += wd;
            debits[net] = e;
            if (debits.Count > 64) Prune(now);
        }

        /// <summary>Energy owed by this net for the current (or the previous) tick: the thing tick and the net tick
        /// run in either order inside one game tick, so one tick of grace keeps the debit continuous.</summary>
        public static float Owed(PowerNet net)
        {
            if (bypass > 0 || debits.Count == 0 || !debits.TryGetValue(net, out Entry e)) return 0f;
            int now = Find.TickManager.TicksGame;
            return e.tick >= now - 1 ? e.wd : 0f;
        }

        private static void Prune(int now)
        {
            foreach (PowerNet n in debits.Where(kv => kv.Value.tick < now - 2).Select(kv => kv.Key).ToList()) debits.Remove(n);
        }

        public static void Clear() => debits.Clear();
    }

    /// <summary>Event hook for later theft consequences (alerts, goodwill, raids): NOT designed yet (owner ruling pending).
    /// Fired every 250 ticks per tap with the energy taken since the last event.</summary>
    public static class TapEvents
    {
        public static event Action<Thing, Thing, float> Drained;
        public static int raised;

        internal static void Raise(Thing tap, Thing victimTransmitter, float wd)
        {
            raised++;
            try { Drained?.Invoke(tap, victimTransmitter, wd); }
            catch (Exception ex) { Log.ErrorOnce("[MessyConduit] a TapEvents.Drained handler threw: " + ex, 0x7A9E11); }
        }
    }

    [HarmonyPatch(typeof(PowerNet), nameof(PowerNet.CurrentEnergyGainRate))]
    internal static class Patch_PowerNet_GainRate_TapDebit
    {
        private static void Postfix(PowerNet __instance, ref float __result)
        {
            if (TapRegistry.Count == 0) return;
            __result -= TapRegistry.Owed(__instance);
        }
    }

    internal static class TapUtil
    {
        public static bool IsTap(CompPower c) => c?.parent != null && c.parent.def == AerialDefOf.RM_PowerTapClamp;

        public static bool NetHasFaction(PowerNet net, Faction f) =>
            net != null && net.transmitters.Any(t => t?.parent != null && t.parent.Faction == f);
    }

    /// <summary>The clamp hooks up only to a net holding a transmitter of its own faction.</summary>
    [HarmonyPatch(typeof(PowerConnectionMaker), nameof(PowerConnectionMaker.TryConnectToAnyPowerNet))]
    internal static class Patch_TryConnect_TapOwnFaction
    {
        private static void Prefix(CompPower pc, ref List<PowerNet> disallowedNets)
        {
            if (!TapUtil.IsTap(pc) || !pc.parent.Spawned) return;
            var list = disallowedNets != null ? new List<PowerNet>(disallowedNets) : new List<PowerNet>();
            foreach (PowerNet n in pc.parent.Map.powerNetManager.AllNetsListForReading)
                if (!TapUtil.NetHasFaction(n, pc.parent.Faction) && !list.Contains(n)) list.Add(n);
            disallowedNets = list;
        }
    }

    /// <summary>Every other route (ConnectAllConnectorsToTransmitter when their net is rebuilt, manual reconnect) is
    /// refused onto a foreign transmitter; the clamp then asks again through the faction-aware path above.</summary>
    [HarmonyPatch(typeof(CompPower), nameof(CompPower.ConnectToTransmitter))]
    internal static class Patch_ConnectToTransmitter_TapGuard
    {
        public static int refused;

        private static bool Prefix(CompPower __instance, CompPower transmitter)
        {
            if (!TapUtil.IsTap(__instance) || transmitter?.parent == null) return true;
            if (transmitter.parent.Faction == __instance.parent.Faction) return true;
            refused++;
            if (__instance.connectParent == null && __instance.parent.Spawned)
                __instance.parent.Map.powerNetManager.Notify_ConnectorWantsConnect(__instance);
            return false;
        }
    }
}
