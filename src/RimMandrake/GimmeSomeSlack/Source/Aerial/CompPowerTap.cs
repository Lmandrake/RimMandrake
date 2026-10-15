using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
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
    ///   nearest transmitter by construction, so Patch_TryConnect_TapOwnFaction picks the nearest OWN-faction
    ///   transmitter itself and Patch_ConnectToTransmitter_TapGuard refuses any other route onto a foreign transmitter.
    /// * The victim pays through vanilla's own books: Patch_PowerNet_GainRate_TapDebit subtracts this tick's stolen
    ///   energy from the victim net's CurrentEnergyGainRate, so PowerNetTick drains their batteries and browns out
    ///   their machines exactly as an extra consumer would -- with no consumer of ours in their net.
    /// Consequences hang off TapEvents.Drained: PowerTheftConsequences (owner 2026-10-10) is the caught-theft goodwill leak.
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
        /// <summary>POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK: the victim faction that most recently caught this clamp (null: never
        /// caught). Kept for the inspect line and for saves written before <see cref="caughtFactions"/>.</summary>
        public Faction caughtBy;
        /// <summary>Draining ticks since the last goodwill charge (legacy single-slot field; read once into the lists).</summary>
        public int caughtDrainTicks;
        /// <summary>GPT pre-release C8: every victim faction that has caught this clamp ("once per clamp per victim faction"),
        /// with its own draining ticks since its last charge (parallel lists). Biting a second faction no longer forgets the first.</summary>
        public List<Faction> caughtFactions = new List<Faction>();
        public List<int> caughtTicks = new List<int>();
        /// <summary>GPT pre-release C7: ticks in the current 250-tick event window that actually drained (the goodwill clock
        /// counts these, not the whole window).</summary>
        public int drainTicksSinceEvent;

        public bool CaughtBy(Faction f) => f != null && caughtFactions.Contains(f);

        public void MarkCaught(Faction f)
        {
            caughtBy = f;
            if (f == null || caughtFactions.Contains(f)) return;
            caughtFactions.Add(f);
            caughtTicks.Add(0);
        }

        /// <summary>The draining-tick accumulator of victim faction <paramref name="f"/> (index into the lists), or -1.</summary>
        public int CaughtIndex(Faction f) => f == null ? -1 : caughtFactions.IndexOf(f);

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
            Scribe_Values.Look(ref sinceEventWd, "rmTapSinceEvent");   // GPT review #22: unreported energy survives a save
            Scribe_References.Look(ref caughtBy, "rmTapCaughtBy");
            Scribe_Values.Look(ref caughtDrainTicks, "rmTapCaughtDrainTicks");
            Scribe_Collections.Look(ref caughtFactions, "rmTapCaughtFactions", LookMode.Reference);
            Scribe_Collections.Look(ref caughtTicks, "rmTapCaughtTicks", LookMode.Value);
            Scribe_Values.Look(ref drainTicksSinceEvent, "rmTapDrainTicksSinceEvent");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                caughtFactions ??= new List<Faction>();
                caughtTicks ??= new List<int>();
                // a faction gone from the world loads as null; the two lists stay parallel
                for (int i = Math.Min(caughtFactions.Count, caughtTicks.Count) - 1; i >= 0; i--)
                    if (caughtFactions[i] == null) { caughtFactions.RemoveAt(i); caughtTicks.RemoveAt(i); }
                if (caughtTicks.Count != caughtFactions.Count)
                {
                    while (caughtTicks.Count < caughtFactions.Count) caughtTicks.Add(0);
                    caughtTicks.RemoveRange(caughtFactions.Count, caughtTicks.Count - caughtFactions.Count);
                }
                // a save from before the lists: its one caught faction and its ticks move in
                if (caughtBy != null && !caughtFactions.Contains(caughtBy)) { caughtFactions.Add(caughtBy); caughtTicks.Add(caughtDrainTicks); }
                caughtDrainTicks = 0;
            }
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
            // GPT source read 2026-10-06 A2: a clamp switched off or broken down drains nothing (it used to debit the victim
            // regardless and only stop delivering the power)
            bool working = FlickUtility.WantsToBeOn(parent) && !parent.IsBrokenDown();
            if (victim != null && ours != null && working)
            {
                TapRegistry.bypass++;
                float rawGain, stored;
                try { rawGain = victim.CurrentEnergyGainRate(); stored = victim.CurrentStoredEnergy(); }
                finally { TapRegistry.bypass--; }
                // A1: the gain is read with every tap's debit bypassed, so subtract what the taps that ticked before this one
                // already took from this victim this tick
                stolenWd = (float)AerialMath.TapStolenPerTick(AerialSettings.tapRate, rawGain, stored, CompPower.WattsToWattDaysPerTick,
                    victim == ours, AerialSettings.tapsEnabled && AerialSettings.enabled, TapRegistry.TakenThisTick(victim), working);
            }
            if (stolenWd > 0f) { TapRegistry.Debit((vt as Building)?.PowerComp, stolenWd); drainTicksSinceEvent++; }
            lastStolenW = stolenWd / CompPower.WattsToWattDaysPerTick;
            stolenTotalWd += stolenWd;
            sinceEventWd += stolenWd;
            if (!t.PowerOn && lastStolenW > 0f && working) t.PowerOn = true;
            t.PowerOutput = t.PowerOn ? lastStolenW : 0f;
            if (parent.IsHashIntervalTick(250) && sinceEventWd > 0f)
            {
                if (AerialSettings.tapEvents) TapEvents.Raise(parent, vt, sinceEventWd);
                sinceEventWd = 0f;
                drainTicksSinceEvent = 0;
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!AerialSettings.tapsEnabled) return "Power taps are switched off in Mod Settings.";
            PowerNet v = VictimNet(out Thing vt);
            if (v == null) return "Not biting anyone's conduit.";
            if (Trader?.PowerNet == null) return "Biting " + (vt.Faction?.Name ?? "an unowned") + " grid; no cable of ours within 6 cells to bring it home.";
            string s = "Draining " + lastStolenW.ToString("0") + " W from " + (vt.Faction?.Name ?? "an unowned") + " grid (" + stolenTotalWd.ToString("0") + " Wd so far).";
            if (caughtBy != null && AerialSettings.tapEvents && AerialSettings.theftGoodwill)
                s += "\nCaught by " + caughtBy.Name + ": costs " + AerialSettings.theftGoodwillPerDay + " goodwill per day of draining.";
            return s;
        }
    }

    /// <summary>Per-net energy the taps took THIS tick (watt-days), read by the CurrentEnergyGainRate postfix. Keyed by the
    /// bitten transmitter's CompPower and settled by its CURRENT net (GPT pre-release C1: a PowerNet key was orphaned when the
    /// victim's nets were rebuilt between a tap's debit and the net tick that settles it).</summary>
    public static class TapRegistry
    {
        private static readonly TapLedger<CompPower> ledger = new TapLedger<CompPower>();
        private static readonly Func<CompPower, PowerNet, bool> InNet = (c, n) => c != null && c.PowerNet == n;
        [ThreadStatic] internal static int bypass;
        public static int Count => ledger.Count;

        public static void Debit(CompPower victimTransmitter, float wd)
        {
            if (victimTransmitter != null) ledger.Debit(victimTransmitter, wd, Find.TickManager.TicksGame);
        }

        /// <summary>A1: energy the taps already debited from this net during the CURRENT tick (0 before the first tap ticks).</summary>
        public static float TakenThisTick(PowerNet net) => net == null ? 0f : ledger.OwedWhere(net, InNet, Find.TickManager.TicksGame);

        /// <summary>Energy owed by this net: the debit the taps wrote at the current TicksGame. Engine order (decompiled
        /// 1.6 TickManager.DoSingleTick): MapPreTick -> PowerNetsTick runs BEFORE ticksGameInt++ and the thing ticks, so a
        /// debit written by a tap at tick T is settled by the net tick that reads TicksGame == T. The old one-tick grace
        /// (e.tick >= now - 1) paid the last debit a second time when a tap stopped (GPT review 2026-10-08 #19).</summary>
        public static float Owed(PowerNet net)
        {
            if (bypass > 0 || net == null) return 0f;
            return ledger.OwedWhere(net, InNet, Find.TickManager.TicksGame);
        }

        public static void Clear() => ledger.Clear();
    }

    /// <summary>Event hook for theft consequences; PowerTheftConsequences subscribes (caught theft leaks goodwill, owner
    /// 2026-10-10). Fired every 250 ticks per tap with the energy taken since the last event.</summary>
    public static class TapEvents
    {
        public static event Action<Thing, Thing, float> Drained;
        public static int raised;

        internal static void Raise(Thing tap, Thing victimTransmitter, float wd)
        {
            raised++;
            Action<Thing, Thing, float> all = Drained;
            if (all == null) return;
            // design pass GS-3: each subscriber in its own try, so one bad handler never silences the rest
            foreach (Delegate d in all.GetInvocationList())
            {
                try { ((Action<Thing, Thing, float>)d)(tap, victimTransmitter, wd); }
                catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] a TapEvents.Drained handler threw: " + ex, 0x7A9E11 ^ d.Method.Name.GetHashCode()); }
            }
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

    }

    /// <summary>The clamp hooks up only to a transmitter of its own faction (POWER_TAP_MIXED_NET_CONNECT_1: filtered per
    /// TRANSMITTER, not per net — a mixed net whose nearest transmitter is foreign used to pass the net filter, be refused by
    /// the guard below, re-queue, and loop on every net update). The pick is vanilla's BestTransmitterForConnector rule
    /// (6-cell square, transmitting, wire-connectable, nearest) with the faction test added.</summary>
    [HarmonyPatch(typeof(PowerConnectionMaker), nameof(PowerConnectionMaker.TryConnectToAnyPowerNet))]
    internal static class Patch_TryConnect_TapOwnFaction
    {
        private static bool Prefix(CompPower pc, List<PowerNet> disallowedNets)
        {
            if (!TapUtil.IsTap(pc) || !pc.parent.Spawned) return true;
            if (pc.connectParent != null) return false;
            CompPower best = BestOwnTransmitter(pc, disallowedNets);
            if (best != null) pc.ConnectToTransmitter(best);
            else pc.connectParent = null;
            return false;
        }

        internal static CompPower BestOwnTransmitter(CompPower pc, List<PowerNet> disallowedNets = null)
        {
            Map map = pc.parent.Map;
            if (map == null) return null;
            IntVec3 at = pc.parent.def.building != null && pc.parent.def.building.isAttachment
                ? (GenConstruct.GetWallAttachedTo(pc.parent)?.Position ?? pc.parent.Position)
                : pc.parent.Position;
            CellRect r = CellRect.SingleCell(at).ExpandedBy(6).ClipInsideMap(map);
            float bestD = float.MaxValue;
            CompPower best = null;
            foreach (IntVec3 c in r)
            {
                Building t = c.GetTransmitter(map);
                if (t == null || t.Destroyed || t.Faction != pc.parent.Faction) continue;
                CompPower comp = t.PowerComp;
                if (comp == null || !comp.TransmitsPowerNow || (t.def.building != null && !t.def.building.allowWireConnection)) continue;
                if (disallowedNets != null && disallowedNets.Contains(comp.transNet)) continue;
                float d = (t.Position - at).LengthHorizontalSquared;
                if (d < bestD) { bestD = d; best = comp; }
            }
            return best;
        }
    }

    /// <summary>Every other route (ConnectAllConnectorsToTransmitter when their net is rebuilt, manual reconnect) is
    /// refused onto a foreign transmitter; the clamp then asks again through the faction-aware path above — but only
    /// when that path has an own-faction transmitter to give it, so a refusal it would repeat never re-queues.</summary>
    [HarmonyPatch(typeof(CompPower), nameof(CompPower.ConnectToTransmitter))]
    internal static class Patch_ConnectToTransmitter_TapGuard
    {
        public static int refused;

        private static bool Prefix(CompPower __instance, CompPower transmitter)
        {
            if (!TapUtil.IsTap(__instance) || transmitter?.parent == null) return true;
            if (transmitter.parent.Faction == __instance.parent.Faction) return true;
            refused++;
            if (__instance.connectParent == null && __instance.parent.Spawned
                && Patch_TryConnect_TapOwnFaction.BestOwnTransmitter(__instance) != null)
                __instance.parent.Map.powerNetManager.Notify_ConnectorWantsConnect(__instance);
            return false;
        }
    }
}
