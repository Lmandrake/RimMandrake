// BLUEDESERT_GPT_ENRICHMENT_1 §2 — "the line gives back slowly".
//
// Owner-picked by question card 2026-09-30 from the GPT enrichment consult
// (Transient/bedazzle_gpt_enrich_2026-09-30/bluedesert.md §4). This is the
// ablation-line salvage incident family that BLUEDESERT_MECHANICS_BUILD_1 §8
// rules ("the line gave something up": IncidentDef, edge-biased placement,
// freeze-dried corpse via vanilla corpse gen), built staged:
//
//   stage 0  a distant crack, heard map-wide; a message with no location.
//   stage 1  hours later, a dark shape shows under thinning ice at the spot.
//            Vekkit (the Pickers) and vrisk come to it and keep circling, so
//            footprints on the ice (Ice takeFootprints) and circling fliers
//            mark the place before any letter does.
//   stage 2  hours later again, the ice gives way: the payload (wreckage,
//            meteoritic metal, or a named freeze-dried body) is exposed and
//            the letter arrives, pointing at it.
//
// The thaw roll (RM_BlueIceThaw.cs) is quarrying's debris and never makes a
// body; this family is the only author of the orbital dead, so "the fallen"
// is not double-authored (the mechanics item's own sequencing note).
//
// Engine seams (RimSage, decompiled 1.6, 2026-09-30):
//  - IncidentDef.allowedBiomes is checked in IncidentWorker.CanFireNow, so
//    the Blue Desert-only restriction is plain XML.
//  - RoomGenUtility.SpawnCorpse(cell, kind, deadTicks, map, damage, ...,
//    bloodFilthRange) is vanilla's own "generate a pawn, simulate its
//    killing, spawn the corpse" path. deadTicks 0 keeps the body whole (the
//    cold preserved it; RotProgress is advanced BY deadTicks, so a large
//    value would skeletonize it), and a (0,0) blood range leaves no fresh
//    blood on a body that died centuries ago.
//
// Gate: RM_BlueDesertSettings.masterEnabled && ablationSalvageEnabled; the
// pace slider scales both stage delays. A find already under way when the
// setting goes off still completes (nothing half-exists).

using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.BlueDesert
{
    public class RM_AblationPayloadOption
    {
        public ThingDef thing;
        public IntRange count = new IntRange(1, 1);
        public float weight = 1f;
    }

    public class RM_AblationCorpseOption
    {
        public PawnKindDef kind;
        public float weight = 1f;
    }

    /// <summary>One salvage variant, on its IncidentDef.</summary>
    public class RM_AblationSalvageExtension : DefModExtension
    {
        public ThingDef markerDef;

        /// <summary>Game hours from the crack to the silhouette, and from the
        /// silhouette to the exposure.</summary>
        public FloatRange hoursToSilhouette = new FloatRange(2f, 3f);
        public FloatRange hoursToExposure = new FloatRange(3f, 4.5f);

        /// <summary>How far in from the map edge the find surfaces.</summary>
        public IntRange edgeBand = new IntRange(4, 16);

        /// <summary>Items exposed (every entry spawns; weight unused here).</summary>
        public List<RM_AblationPayloadOption> items;

        /// <summary>If set, one body of a weighted kind is exposed too.</summary>
        public List<RM_AblationCorpseOption> corpses;
        public IntRange corpseYearsAgo = new IntRange(40, 1200);

        public PawnKindDef pickerKind;
        public IntRange pickerCount = new IntRange(1, 2);
        public PawnKindDef flierKind;
        public IntRange flierCount = new IntRange(1, 2);

        public SoundDef crackSound;
        public SoundDef exposeSound;

        [MustTranslate] public string crackMessage;
        [MustTranslate] public string silhouetteMessage;
        [MustTranslate] public string letterLabel;
        [MustTranslate] public string letterText;
        /// <summary>Appended when a body is exposed. {0} name, {1} kind label,
        /// {2} years.</summary>
        [MustTranslate] public string corpseLetterText;
    }

    public class RM_IncidentWorker_AblationSalvage : IncidentWorker
    {
        private RM_AblationSalvageExtension Ext => def.GetModExtension<RM_AblationSalvageExtension>();

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.ablationSalvageEnabled)
            {
                return false;
            }
            if (Ext?.markerDef == null || !(parms.target is Map map))
            {
                return false;
            }
            return TryFindSpot(map, Ext, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RM_AblationSalvageExtension ext = Ext;
            if (ext?.markerDef == null || !TryFindSpot(map, ext, out IntVec3 spot))
            {
                return false;
            }
            RM_AblationEmergence marker = (RM_AblationEmergence)ThingMaker.MakeThing(ext.markerDef);
            marker.Init(def, ext);
            GenSpawn.Spawn(marker, spot, map);
            ext.crackSound?.PlayOneShotOnCamera(map);
            if (!ext.crackMessage.NullOrEmpty())
            {
                Messages.Message(ext.crackMessage, MessageTypeDefOf.NeutralEvent);
            }
            return true;
        }

        /// <summary>Edge-biased: step a random distance in from a random edge
        /// cell, onto open, unroofed, unbuilt ground.</summary>
        public static bool TryFindSpot(Map map, RM_AblationSalvageExtension ext, out IntVec3 spot)
        {
            for (int i = 0; i < 80; i++)
            {
                Rot4 side = Rot4.Random;
                IntVec3 edge = CellFinder.RandomEdgeCell(side, map);
                IntVec3 c = edge + side.Opposite.FacingCell * ext.edgeBand.RandomInRange;
                if (!c.InBounds(map) || !c.Standable(map) || c.Roofed(map))
                {
                    continue;
                }
                if (c.GetEdifice(map) != null || c.GetFirstPawn(map) != null)
                {
                    continue;
                }
                if (map.areaManager.Home[c])
                {
                    continue; // the line surfaces on the open plateau, not in the colony
                }
                spot = c;
                return true;
            }
            spot = IntVec3.Invalid;
            return false;
        }
    }

    /// <summary>The spot where the line is giving something up. Invisible
    /// while only the crack has sounded; a dark shape once the ice thins;
    /// gone once the find is exposed.</summary>
    public class RM_AblationEmergence : ThingWithComps
    {
        private IncidentDef incident;
        private int stage;
        private int silhouetteTick = -1;
        private int exposureTick = -1;
        private List<Pawn> scavengers = new List<Pawn>();

        private RM_AblationSalvageExtension Ext => incident?.GetModExtension<RM_AblationSalvageExtension>();

        public int Stage => stage;

        public void Init(IncidentDef incidentDef, RM_AblationSalvageExtension ext)
        {
            incident = incidentDef;
            float pace = Mathf.Max(0.1f, RM_BlueDesertSettings.ablationPaceFactor);
            int now = Find.TickManager.TicksGame;
            silhouetteTick = now + Mathf.RoundToInt(ext.hoursToSilhouette.RandomInRange * 2500f * pace);
            exposureTick = silhouetteTick + Mathf.RoundToInt(ext.hoursToExposure.RandomInRange * 2500f * pace);
        }

        public override string Label => stage == 0 ? base.Label : "dark shape under the ice";

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref incident, "rmIncident");
            Scribe_Values.Look(ref stage, "rmStage", 0);
            Scribe_Values.Look(ref silhouetteTick, "rmSilhouetteTick", -1);
            Scribe_Values.Look(ref exposureTick, "rmExposureTick", -1);
            Scribe_Collections.Look(ref scavengers, "rmScavengers", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                scavengers = scavengers ?? new List<Pawn>();
                scavengers.RemoveAll(p => p == null);
            }
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            if (stage >= 1)
            {
                base.DrawAt(drawLoc, flip);
            }
        }

        public override void TickRare()
        {
            base.TickRare();
            RM_AblationSalvageExtension ext = Ext;
            if (ext == null || !Spawned)
            {
                Destroy();
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (stage == 0 && now >= silhouetteTick)
            {
                stage = 1;
                Map.mapDrawer.MapMeshDirty(Position, MapMeshFlagDefOf.Things);
                CallScavengers(ext);
                if (!ext.silhouetteMessage.NullOrEmpty())
                {
                    Messages.Message(ext.silhouetteMessage, new LookTargets(Position, Map),
                        MessageTypeDefOf.NeutralEvent);
                }
            }
            if (stage >= 1)
            {
                KeepScavengersCircling();
            }
            if (stage == 1 && now >= exposureTick)
            {
                Expose(ext);
            }
        }

        private void CallScavengers(RM_AblationSalvageExtension ext)
        {
            AddScavengers(ext.pickerKind, ext.pickerCount.RandomInRange);
            AddScavengers(ext.flierKind, ext.flierCount.RandomInRange);
        }

        /// <summary>Wild natives of the kind already on the map come first;
        /// only if too few are here do new ones walk (or fly) in at an edge.</summary>
        private void AddScavengers(PawnKindDef kind, int want)
        {
            if (kind == null || want <= 0)
            {
                return;
            }
            Map map = Map;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (want <= 0)
                {
                    break;
                }
                if (p.kindDef == kind && p.Faction == null && !p.Dead && !p.Downed && !p.InMentalState
                    && !scavengers.Contains(p))
                {
                    scavengers.Add(p);
                    want--;
                }
            }
            for (int i = 0; i < want; i++)
            {
                if (!CellFinder.TryFindRandomEdgeCellWith(
                        c => c.Standable(map) && !c.Fogged(map) && map.reachability.CanReach(c, Position,
                            PathEndMode.Touch, TraverseParms.For(TraverseMode.NoPassClosedDoors)),
                        map, CellFinder.EdgeRoadChance_Animal, out IntVec3 edge))
                {
                    return;
                }
                Pawn p = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(p, edge, map);
                scavengers.Add(p);
            }
        }

        private void KeepScavengersCircling()
        {
            Map map = Map;
            scavengers.RemoveAll(p => p == null || p.Dead || !p.Spawned || p.Map != map || p.Faction != null);
            foreach (Pawn p in scavengers)
            {
                if (p.Downed || p.InMentalState || p.jobs == null)
                {
                    continue;
                }
                JobDef cur = p.CurJobDef;
                bool idle = cur == null || cur == JobDefOf.Wait_Wander || cur == JobDefOf.GotoWander
                    || cur == JobDefOf.Wait || cur == JobDefOf.Goto;
                if (!idle)
                {
                    continue; // eating, fleeing, fighting: it is an animal first
                }
                bool far = !p.Position.InHorDistOf(Position, 8f);
                if (!far && !Rand.Chance(0.35f))
                {
                    continue;
                }
                if (!CellFinder.TryFindRandomCellNear(Position, map, 6,
                        c => c.Standable(map) && c != Position, out IntVec3 dest))
                {
                    continue;
                }
                Job job = JobMaker.MakeJob(JobDefOf.GotoWander, dest);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
            }
        }

        private void Expose(RM_AblationSalvageExtension ext)
        {
            stage = 2;
            Map map = Map;
            IntVec3 spot = Position;
            List<Thing> exposed = new List<Thing>();
            if (ext.items != null)
            {
                foreach (RM_AblationPayloadOption opt in ext.items)
                {
                    if (opt?.thing == null)
                    {
                        continue;
                    }
                    Thing t = ThingMaker.MakeThing(opt.thing, GenStuff.DefaultStuffFor(opt.thing));
                    t.stackCount = Mathf.Clamp(opt.count.RandomInRange, 1, Mathf.Max(1, opt.thing.stackLimit));
                    if (GenPlace.TryPlaceThing(t, spot, map, ThingPlaceMode.Near, out Thing placed))
                    {
                        exposed.Add(placed ?? t);
                    }
                }
            }
            string text = ext.letterText ?? "";
            if (!ext.corpses.NullOrEmpty()
                && ext.corpses.TryRandomElementByWeight(o => o?.kind != null ? Mathf.Max(0f, o.weight) : 0f,
                    out RM_AblationCorpseOption pick) && pick?.kind != null)
            {
                IntVec3 cell = CellFinder.StandableCellNear(spot, map, 3f);
                if (!cell.IsValid)
                {
                    cell = spot;
                }
                Corpse corpse = RoomGenUtility.SpawnCorpse(cell, pick.kind, 0, map, DamageDefOf.Blunt,
                    bloodFilthRange: new IntRange(0, 0));
                if (corpse != null)
                {
                    exposed.Add(corpse);
                    if (!ext.corpseLetterText.NullOrEmpty())
                    {
                        Pawn dead = corpse.InnerPawn;
                        string name = dead?.Name?.ToStringFull ?? dead?.LabelShort ?? "someone";
                        text += "\n\n" + string.Format(ext.corpseLetterText, name,
                            pick.kind.label ?? "traveller", ext.corpseYearsAgo.RandomInRange);
                    }
                }
            }
            ext.exposeSound?.PlayOneShot(new TargetInfo(spot, map));
            FleckMaker.ThrowDustPuffThick(spot.ToVector3Shifted(), map, 2.5f, new Color(0.85f, 0.9f, 1f));
            scavengers.Clear();
            Find.LetterStack.ReceiveLetter(ext.letterLabel ?? "The line gave something up", text,
                LetterDefOf.PositiveEvent, exposed.Count > 0 ? new LookTargets(exposed) : new LookTargets(spot, map));
            Destroy();
        }
    }
}
