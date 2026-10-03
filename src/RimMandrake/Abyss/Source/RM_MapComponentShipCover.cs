using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_HIDDEN_SHIP_PROBES_1 -- hidden-ship cover, and the probes that put it at risk.
    //
    // COVER (0..1) grows slowly on a player-home Abyss map that holds a grav engine, but only while the
    // base is QUIET (few lit building lamps). It reads as "covered" from CoveredThreshold up. It is never permanent:
    // after MaxCoveredTicks of cover it lapses and must be built again after a short cooldown. It resets the moment the
    // grav engine is gone from the map (the ship launched / engine started), and when a probe reports.
    // Other mods read it through RM_MapComponent_ShipCover.IsCovered(map) / CoverLevel(map).
    //
    // PROBES come at intervals while the ship is covered (hidden is not safe). A probe is a scout from
    // the biome's RM_AbyssProbeExtension kind list (the campaign layer patches its droids in; with none listed a
    // vanilla light mech is used), walks the colony and REPORTS if it keeps a colonist in motion, or a lit lamp, in
    // sight range for ReportTicks. A report collapses the cover. Avoid: stay still, cold and dark, or shoot it down.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AbyssProbeExtension : DefModExtension
    {
        public List<PawnKindDef> probeKinds = new List<PawnKindDef>();
        public FactionDef probeFaction;   // null = the mechanoid faction
    }

    public class RM_MapComponent_ShipCover : MapComponent
    {
        private const int Interval = 250;
        private const float DaysToFullCover = 6f;
        private const int MaxCoveredTicks = 15 * GenDate.TicksPerDay;
        private const int CooldownTicks = 3 * GenDate.TicksPerDay;
        public const float CoveredThreshold = 0.6f;
        private const int FreeLamps = 4;

        private const int ProbeMin = 3 * GenDate.TicksPerDay, ProbeMax = 6 * GenDate.TicksPerDay;
        private const int ProbeStay = GenDate.TicksPerDay;
        private const int ScanInterval = 60;
        private const int ReportTicks = 600;
        private const float SightRadius = 14f, LampSightRadius = 22f;

        private float cover;
        private int coveredTicks;
        private int cooldownUntil = -1;
        private int nextProbeTick = -1;
        private Pawn probe;
        private int probeSpawnTick;
        private int seenTicks;
        private int lastLampCount;

        public RM_MapComponent_ShipCover(Map map) : base(map) { }

        public float Cover { get { return cover; } }
        public static float CoverLevel(Map map)
        {
            RM_MapComponent_ShipCover c = map?.GetComponent<RM_MapComponent_ShipCover>();
            return c == null ? 0f : c.cover;
        }
        public static bool IsCovered(Map map)
        {
            return RM_AbyssSettings.shipCoverEnabled && CoverLevel(map) >= CoveredThreshold;
        }

        private bool Applies()
        {
            return RM_AbyssSettings.shipCoverEnabled && map.IsPlayerHome && map.Biome != null && map.Biome.defName == "RM_Abyss";
        }

        private bool HasEngine()
        {
            ThingDef eng = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            return eng != null && map.listerThings.ThingsOfDef(eng).Count > 0;
        }

        private int CountLitLamps()
        {
            int n = 0;
            List<Thing> all = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            for (int i = 0; i < all.Count; i++)
            {
                CompGlower g = all[i].TryGetComp<CompGlower>();
                if (g != null && g.Glows) n++;
            }
            return n;
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (probe != null) ProbeTick(now);
            if (now % Interval != 0) return;

            if (!Applies() || !HasEngine())
            {
                Collapse(false, now);
                return;
            }
            if (cooldownUntil > now) return;

            lastLampCount = CountLitLamps();
            bool quiet = lastLampCount <= FreeLamps;
            if (cover < 1f && quiet)
                cover = Mathf.Min(1f, cover + Interval / (DaysToFullCover * GenDate.TicksPerDay));
            else if (!quiet)
                cover = Mathf.Max(0f, cover - Interval / (DaysToFullCover * GenDate.TicksPerDay) * 2f);

            if (cover >= CoveredThreshold)
            {
                coveredTicks += Interval;
                if (coveredTicks >= MaxCoveredTicks)
                {
                    Collapse(true, now);
                    Messages.Message("The cover over the ship has worn thin; the search will find it again. It can be built up again after a few days.", MessageTypeDefOf.NeutralEvent, false);
                    return;
                }
                if (RM_AbyssSettings.probesEnabled)
                {
                    if (nextProbeTick < 0) nextProbeTick = now + Rand.Range(ProbeMin, ProbeMax);
                    if (now >= nextProbeTick && probe == null) { SpawnProbe(now); nextProbeTick = now + Rand.Range(ProbeMin, ProbeMax); }
                }
            }
            else
            {
                coveredTicks = 0;
                nextProbeTick = -1;
            }
        }

        private void Collapse(bool cooldown, int now)
        {
            cover = 0f;
            coveredTicks = 0;
            nextProbeTick = -1;
            if (cooldown) cooldownUntil = now + CooldownTicks;
        }

        private void SpawnProbe(int now)
        {
            RM_AbyssProbeExtension ext = map.Biome.GetModExtension<RM_AbyssProbeExtension>();
            PawnKindDef kind = null;
            if (ext != null && ext.probeKinds.Count > 0) kind = ext.probeKinds.RandomElement();
            if (kind == null) kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Mech_Militor");
            if (kind == null) return;
            Faction fac = null;
            if (ext != null && ext.probeFaction != null) fac = Find.FactionManager.FirstFactionOfDef(ext.probeFaction);
            if (fac == null) fac = Faction.OfMechanoids;
            if (fac == null) return;
            IntVec3 cell;
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && map.reachability.CanReachColony(c), map, CellFinder.EdgeRoadChance_Ignore, out cell)) return;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, fac, PawnGenerationContext.NonPlayer, map.Tile));
            GenSpawn.Spawn(p, cell, map);
            IntVec3 centre = map.mapPawns.FreeColonistsSpawned.Count > 0 ? map.mapPawns.FreeColonistsSpawned.RandomElement().Position : map.Center;
            LordMaker.MakeNewLord(fac, new LordJob_DefendPoint(centre, 20f, null, false, false), map, new List<Pawn> { p });
            probe = p;
            probeSpawnTick = now;
            seenTicks = 0;
            Find.LetterStack.ReceiveLetter("Probe in the dark", "A probe has come down and is quartering the ground. It is looking for what is hidden. Stay still, stay cold and dark, or shoot it down before it reports.", LetterDefOf.ThreatSmall, p);
        }

        private void ProbeTick(int now)
        {
            if (probe.Destroyed || probe.Dead || !probe.Spawned)
            {
                if (probe.Dead) Messages.Message("The probe is down. The ship is still hidden.", MessageTypeDefOf.PositiveEvent, false);
                probe = null; seenTicks = 0;
                return;
            }
            if (now - probeSpawnTick > ProbeStay) { Leave(); return; }
            if (now % ScanInterval != 0) return;
            if (!Applies()) return;

            bool seen = false;
            List<Pawn> cols = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < cols.Count && !seen; i++)
            {
                Pawn c = cols[i];
                if (c.Downed || !c.Position.InHorDistOf(probe.Position, SightRadius)) continue;
                if (c.pather != null && c.pather.Moving) seen = true;            // movement gives a pawn away; stillness does not
            }
            if (!seen)
            {
                List<Thing> all = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
                for (int i = 0; i < all.Count && !seen; i++)
                {
                    CompGlower g = all[i].TryGetComp<CompGlower>();
                    if (g != null && g.Glows && all[i].Position.InHorDistOf(probe.Position, LampSightRadius)) seen = true;
                }
            }
            seenTicks = seen ? seenTicks + ScanInterval : Mathf.Max(0, seenTicks - ScanInterval);
            if (seenTicks >= ReportTicks)
            {
                Collapse(true, now);
                Find.LetterStack.ReceiveLetter("The probe has reported", "The probe saw enough and has sent what it found. The ship's cover is gone; the search will come for it. It can be built up again after a few days.", LetterDefOf.ThreatBig, probe);
                Leave();
            }
        }

        private void Leave()
        {
            Pawn p = probe;
            probe = null; seenTicks = 0;
            if (p == null || !p.Spawned) return;
            Lord old = p.GetLord();
            if (old != null) old.RemovePawn(p);
            LordMaker.MakeNewLord(p.Faction, new LordJob_ExitMapBest(LocomotionUrgency.Walk), map, new List<Pawn> { p });
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cover, "cover", 0f);
            Scribe_Values.Look(ref coveredTicks, "coveredTicks", 0);
            Scribe_Values.Look(ref cooldownUntil, "cooldownUntil", -1);
            Scribe_Values.Look(ref nextProbeTick, "nextProbeTick", -1);
            Scribe_Values.Look(ref probeSpawnTick, "probeSpawnTick", 0);
            Scribe_Values.Look(ref seenTicks, "seenTicks", 0);
            Scribe_References.Look(ref probe, "probe");
        }
    }
}
