using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.TheRot
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_SWALLOWED_NAVIGATOR_1 (part A: the core). One hwelgrue on the whole world carries an old drive core.
    //
    //   carrier   RM_WorldComponent_SwallowedCore records the carrier's thingID and a spent flag, so the core
    //             exists once per world whatever reloads or deaths follow. Free tier: the first wild hwelgrue to
    //             finish its first sweep (and survive the map cap) claims it. Campaign: RM_SwallowedCoreExtension
    //             .campaignTile on RM_Hwelgrue (a patch sets it; -1 = free-tier rule) restricts the claim to a
    //             hwelgrue on that tile.
    //   ping      every N hours (setting) while a grav engine stands on the carrier's map: RM_CorePing from the
    //             giant (pitch falls with integrity), RM_CoreChirp from each pilot console, a glow on the giant;
    //             the first ping on a world sends the Narrator's letter. The landing-hook ping and the dead ship's
    //             log + salvage sites are part B (ROT_NAVIGATOR_LOG_SITES_1); RM_WorldComponent_SwallowedCore.pings
    //             is the count that log will read.
    //   integrity 0-100. Damage whose instigator is a Building standing on a grav engine's valid substructure
    //             (the ship's own guns) lowers it by damage x setting; any other source does nothing.
    //   drop      on death: a minified RM_SwallowedDriveCore carrying the integrity, or RM_RuinedDriveCore below
    //             the ruin threshold (setting, 25). The world's core is then spent.
    //   range     the installed core is a CompProperties_GravshipFacility linked to GravEngine (patched into its
    //             linkableFacilities); RM_StatPart_SwallowedCore on GravshipRange multiplies the FINAL value
    //             (stat parts run in FinalizeValue, after the facility offsets that the thrusters add in
    //             GetValueUnfinalized) by 1 + bonus x integrity/100.
    // ════════════════════════════════════════════════════════════════════

    public class RM_SwallowedCoreExtension : DefModExtension
    {
        public int campaignTile = -1;
    }

    public class RM_WorldComponent_SwallowedCore : WorldComponent
    {
        public string carrierId;
        public bool spent;
        public int pings;
        public bool firstPingLettered;
        // ROT_NAVIGATOR_LOG_SITES_1
        public int entriesRead;
        public int sitesRevealed;
        public bool logCut;

        public RM_WorldComponent_SwallowedCore(World world) : base(world)
        {
        }

        public static RM_WorldComponent_SwallowedCore Get => Find.World?.GetComponent<RM_WorldComponent_SwallowedCore>();

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref carrierId, "carrierId");
            Scribe_Values.Look(ref spent, "spent", false);
            Scribe_Values.Look(ref pings, "pings", 0);
            Scribe_Values.Look(ref firstPingLettered, "firstPingLettered", false);
            Scribe_Values.Look(ref entriesRead, "entriesRead", 0);
            Scribe_Values.Look(ref sitesRevealed, "sitesRevealed", 0);
            Scribe_Values.Look(ref logCut, "logCut", false);
        }
    }

    public class CompProperties_RM_SwallowedCore : CompProperties
    {
        public CompProperties_RM_SwallowedCore()
        {
            compClass = typeof(RM_CompSwallowedCore);
        }
    }

    /// <summary>On every hwelgrue; only the world's carrier has <see cref="carrier"/> set.</summary>
    public class RM_CompSwallowedCore : ThingComp
    {
        public bool carrier;
        public float integrity = 100f;
        private bool claimChecked;
        private int nextPingTick = -1;
        private bool engineSeen; // ROT_NAVIGATOR_LOG_SITES_1: an engine appearing = a landing -> ping at once

        private Pawn Self => parent as Pawn;

        public static int PingIntervalTicks => Mathf.Max(2500, Mathf.RoundToInt(RM_TheRotSettings.navigatorPingHours * 2500f));

        public override void CompTick()
        {
            base.CompTick();
            Pawn p = Self;
            if (p == null || !p.Spawned || p.Dead || !parent.IsHashIntervalTick(250)) return;
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.navigatorCore) return;
            if (!claimChecked)
            {
                claimChecked = true;
                TryClaim(p);
            }
            if (!carrier) return;
            int now = Find.TickManager.TicksGame;
            bool engineNow = EngineOn(p.Map) != null;
            if (engineNow && !engineSeen) nextPingTick = now;
            engineSeen = engineNow;
            if (nextPingTick < 0) nextPingTick = now;
            if (now >= nextPingTick)
            {
                nextPingTick = now + PingIntervalTicks;
                Ping(p);
            }
        }

        public bool TryClaim(Pawn p)
        {
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            if (w == null || w.spent || p.Faction != null) return false;
            if (!w.carrierId.NullOrEmpty()) return carrier = w.carrierId == p.ThingID;
            if (RM_CompGutDigest.OverCap(p)) return false;
            int tile = p.def.GetModExtension<RM_SwallowedCoreExtension>()?.campaignTile ?? -1;
            if (tile >= 0 && p.Map.Tile.tileId != tile) return false;
            w.carrierId = p.ThingID;
            carrier = true;
            integrity = 100f;
            return true;
        }

        public static Building_GravEngine EngineOn(Map map)
        {
            return map?.listerThings.ThingsOfDef(ThingDefOf.GravEngine).OfType<Building_GravEngine>().FirstOrDefault();
        }

        /// <summary>Pings if a grav engine stands on this map. Returns true if it pinged.</summary>
        public bool Ping(Pawn p)
        {
            Map map = p.Map;
            if (EngineOn(map) == null) return false;
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            if (w != null) w.pings++;
            RM_NavigatorLog.Notify_Ping(w, map);
            SoundInfo info = SoundInfo.InMap(new TargetInfo(p.Position, map));
            info.pitchFactor = Mathf.Lerp(0.6f, 1f, integrity / 100f);
            RM_HwelgrueDefOf.RM_CorePing?.PlayOneShot(info);
            foreach (Thing console in map.listerThings.ThingsOfDef(ThingDefOf.PilotConsole))
            {
                RM_HwelgrueDefOf.RM_CoreChirp?.PlayOneShot(SoundInfo.InMap(new TargetInfo(console.Position, map)));
            }
            FleckMaker.ThrowLightningGlow(p.DrawPos, map, 4f);
            if (w != null && !w.firstPingLettered)
            {
                w.firstPingLettered = true;
                Find.LetterStack.ReceiveLetter("The console is answering",
                    "The console is answering something. It is inside that animal.\n\nA slow pulse, muffled through flesh, keeps "
                  + "time with a drive coil from a much older ship. Whatever the hwelgrue swallowed, it is still trying to fly. "
                  + "Cut it out and it might fly again; hit it with the ship's own guns and it won't.",
                    LetterDefOf.NeutralEvent, p);
            }
            return true;
        }

        public static bool FromShipWeapon(DamageInfo dinfo, Map map)
        {
            if (!(dinfo.Instigator is Building b) || map == null || b.Map != map) return false;
            foreach (Building_GravEngine e in map.listerThings.ThingsOfDef(ThingDefOf.GravEngine).OfType<Building_GravEngine>())
            {
                if (e.ValidSubstructureAt(b.Position)) return true;
            }
            return false;
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (!carrier || !RM_TheRotSettings.navigatorCore) return;
            if (!FromShipWeapon(dinfo, parent.MapHeld)) return;
            integrity = Mathf.Max(0f, integrity - totalDamageDealt * RM_TheRotSettings.navigatorShipDamageFactor);
        }

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            if (!carrier || prevMap == null) return;
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            if (w != null) w.spent = true;
            RM_NavigatorLog.Notify_CarrierDied(w);
            carrier = false;
            Thing drop = MakeDrop(integrity);
            if (drop != null)
            {
                GenPlace.TryPlaceThing(drop, parent.PositionHeld, prevMap, ThingPlaceMode.Near);
                Messages.Message(integrity >= RM_TheRotSettings.navigatorRuinThreshold
                        ? "Something heavy slid out of the hwelgrue: an old drive core, slick with gut."
                        : "The drive core inside the hwelgrue came out in pieces. The ship's guns did that.",
                    new LookTargets(drop), MessageTypeDefOf.NeutralEvent, false);
            }
        }

        public static Thing MakeDrop(float integrity)
        {
            if (integrity < RM_TheRotSettings.navigatorRuinThreshold)
            {
                return ThingMaker.MakeThing(RM_HwelgrueDefOf.RM_RuinedDriveCore);
            }
            Thing core = ThingMaker.MakeThing(RM_HwelgrueDefOf.RM_SwallowedDriveCore);
            RM_CompDriveCoreIntegrity ci = core.TryGetComp<RM_CompDriveCoreIntegrity>();
            if (ci != null) ci.integrity = integrity;
            return MinifyUtility.MakeMinified(core);
        }

        public override string CompInspectStringExtra()
        {
            if (!carrier) return null;
            return "Something inside pings like a drive coil (core integrity " + Mathf.RoundToInt(integrity) + "%). The ping falters when the ship's guns hit it.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref carrier, "carrier", false);
            Scribe_Values.Look(ref integrity, "integrity", 100f);
            Scribe_Values.Look(ref claimChecked, "claimChecked", false);
            Scribe_Values.Look(ref nextPingTick, "nextPingTick", -1);
            Scribe_Values.Look(ref engineSeen, "engineSeen", false);
        }
    }

    public class CompProperties_RM_DriveCoreIntegrity : CompProperties
    {
        public CompProperties_RM_DriveCoreIntegrity()
        {
            compClass = typeof(RM_CompDriveCoreIntegrity);
        }
    }

    /// <summary>The installed core's integrity (carried through minification on the inner thing).</summary>
    public class RM_CompDriveCoreIntegrity : ThingComp
    {
        public float integrity = 100f;

        public float RangeFactor => RM_TheRotSettings.navigatorCore ? 1f + RM_TheRotSettings.navigatorRangeBonus * integrity / 100f : 1f;

        public override string CompInspectStringExtra()
        {
            return "Core integrity " + Mathf.RoundToInt(integrity) + "%: gravship range x" + RangeFactor.ToString("0.00") + " when linked to a grav engine.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref integrity, "integrity", 100f);
        }
    }

    /// <summary>Multiplies a grav engine's final range by the linked core's factor.</summary>
    public class RM_StatPart_SwallowedCore : StatPart
    {
        public static RM_CompDriveCoreIntegrity LinkedCore(StatRequest req)
        {
            if (!req.HasThing || !(req.Thing is Building_GravEngine engine)) return null;
            CompAffectedByFacilities fac = engine.GetComp<CompAffectedByFacilities>();
            if (fac == null) return null;
            foreach (Thing t in fac.LinkedFacilitiesListForReading)
            {
                if (t.def == RM_HwelgrueDefOf.RM_SwallowedDriveCore)
                {
                    RM_CompDriveCoreIntegrity ci = t.TryGetComp<RM_CompDriveCoreIntegrity>();
                    if (ci != null) return ci;
                }
            }
            return null;
        }

        public override void TransformValue(StatRequest req, ref float val)
        {
            RM_CompDriveCoreIntegrity ci = LinkedCore(req);
            if (ci != null) val *= ci.RangeFactor;
        }

        public override string ExplanationPart(StatRequest req)
        {
            RM_CompDriveCoreIntegrity ci = LinkedCore(req);
            return ci == null ? null : "Swallowed drive core (integrity " + Mathf.RoundToInt(ci.integrity) + "%): x" + ci.RangeFactor.ToString("0.00");
        }
    }

    /// <summary>Deterministic reads/triggers for jawa/static_call (THE_ROT_FIRST_SCRIPT_1).</summary>
    public static class RM_SwallowedCoreProof
    {
        /// <summary>Spawns <paramref name="count"/> hwelgrue (cap lifted for the call), runs each one's claim, and
        /// reports carriers. "CORE carriers k of n | world carrier ID spent B pings p".</summary>
        public static string ProofClaim(int count)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Hwelgrue");
            if (kind == null) return "REFUSED: no PawnKindDef RM_Hwelgrue";
            int cap = RM_TheRotSettings.hwelgrueMapCap;
            RM_TheRotSettings.hwelgrueMapCap = 99;
            try
            {
                for (int i = 0; i < count; i++)
                {
                    Pawn p = PawnGenerator.GeneratePawn(kind, null);
                    GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(map.Center, map, 12), map);
                    p.TryGetComp<RM_CompSwallowedCore>()?.TryClaim(p);
                }
            }
            finally
            {
                RM_TheRotSettings.hwelgrueMapCap = cap;
            }
            var all = map.mapPawns.AllPawnsSpawned.Where(p => p.def == RM_HwelgrueDefOf.RM_Hwelgrue && !p.Dead).ToList();
            int carriers = all.Count(p => p.TryGetComp<RM_CompSwallowedCore>()?.carrier == true);
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            return "CORE carriers " + carriers + " of " + all.Count + " | world carrier " + (w?.carrierId ?? "none") + " spent " + (w?.spent ?? false) + " pings " + (w?.pings ?? 0);
        }

        /// <summary>Reads a grav engine's range with and without the linked core's part. "RANGE with W without O ratio R".</summary>
        public static string ProofRange()
        {
            Building_GravEngine e = RM_CompSwallowedCore.EngineOn(Find.CurrentMap);
            if (e == null) return "REFUSED: no grav engine on the current map";
            float with = e.GetStatValue(StatDefOf.GravshipRange, true, -1);
            RM_CompDriveCoreIntegrity ci = RM_StatPart_SwallowedCore.LinkedCore(StatRequest.For(e));
            float without = ci == null ? with : with / ci.RangeFactor;
            return "RANGE with " + with.ToString("0.0") + " without " + without.ToString("0.0") + " ratio " + (without > 0f ? (with / without).ToString("0.00") : "n/a")
                + " | core " + (ci == null ? "not linked" : "integrity " + Mathf.RoundToInt(ci.integrity));
        }

        /// <summary>The drop a carrier at this integrity makes. "DROP def".</summary>
        public static string ProofDrop(float integrity)
        {
            Thing t = RM_CompSwallowedCore.MakeDrop(integrity);
            string d = t is MinifiedThing m ? m.InnerThing.def.defName : t?.def.defName ?? "none";
            t?.Destroy(DestroyMode.Vanish);
            return "DROP " + d;
        }
    }
}
