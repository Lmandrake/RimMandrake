using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 5, first half — fire-stamping giants.
    //
    // "Any open fire above threshold pulls thunderstep herds to stamp it and
    // its source (roofed/enclosed fires exempt or every stove summons gods).
    // Fire implies folly."
    //
    // Data-driven: any creature whose ThingDef carries RM_FireStamperExtension
    // is a stamper. This RM-tier mod names no Star Wars creature (§7 Q11); the
    // thunderstep (RSW_ShrublandGiant) gets the extension from UtinniPatches
    // (Patches/RSW_ShrublandGiant_FireStamper.xml), the layer that already
    // casts it onto the Leaning Scrub.
    //
    // OPEN fire = a vanilla Fire thing on an unroofed cell whose room is
    // outdoors. Stoves, campfires and torches are buildings with a fire
    // overlay, not Fire things, so they never count. A blaze is open fires
    // clustered within ClusterRadius of one another; at MinOpenFires or more
    // every wild, awake, sane stamper on the map is sent to it (one message
    // per blaze), and any stamper standing within StampRadius of open fire
    // stamps it out: the fire is destroyed and whatever was burning under it
    // (the pawn it clings to, the buildings in its cell) takes a blunt stomp.
    // The second half of part 5 (the calling-pyre Ideology ritual) is not here.
    //
    // Numbers marked PROVISIONAL are first guesses (owner ruling 2026-10-03).
    // Gate: modEnabled && fireStampEnabled.
    // ════════════════════════════════════════════════════════════════════
    public class RM_FireStamperExtension : DefModExtension
    {
    }

    public class RM_MapComponent_FireStamp : MapComponent
    {
        public const int StampInterval = 60;
        public const int ConvergeInterval = 600;
        public const int MinOpenFires = RM_BlazeKernel.MinOpenFires;          // PROVISIONAL
        public const float ClusterRadius = RM_BlazeKernel.ClusterRadius;      // PROVISIONAL
        public const float StampRadius = RM_BlazeKernel.StampRadius;          // PROVISIONAL
        public const float StompDamage = 12f;       // PROVISIONAL
        public const int GotoExpiryTicks = 2500;

        private IntVec3 lastBlaze = IntVec3.Invalid;
        private readonly List<Thing> tmpFires = new List<Thing>();

        // Readable by the proof hook.
        public IntVec3 LastBlaze => lastBlaze;

        public RM_MapComponent_FireStamp(Map map) : base(map)
        {
        }

        public static bool IsStamper(Pawn p)
        {
            return p.def.GetModExtension<RM_FireStamperExtension>() != null;
        }

        private static bool Available(Pawn p)
        {
            return p.Spawned && !p.Dead && !p.Downed && p.Faction == null && !p.InMentalState
                && p.Awake() && IsStamper(p);
        }

        public bool IsOpenFire(Thing fire)
        {
            if (!fire.Spawned || fire.Position.Roofed(map))
            {
                return false;
            }
            Room room = fire.Position.GetRoom(map);
            return room == null || room.PsychologicallyOutdoors;
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % StampInterval != 0 || !RM_WindCalendar.On(RM_LeaningScrubSettings.fireStampEnabled))
            {
                return;
            }
            StampPass();
            if (now % ConvergeInterval == 0)
            {
                ConvergePass(sendMessage: true);
            }
        }

        private List<Thing> OpenFires()
        {
            tmpFires.Clear();
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                if (IsOpenFire(fires[i]))
                {
                    tmpFires.Add(fires[i]);
                }
            }
            return tmpFires;
        }

        /// <summary>The largest open-fire cluster at or above MinOpenFires, or Invalid.</summary>
        public IntVec3 FindBlaze()
        {
            List<Thing> open = OpenFires();
            int[] xs = new int[open.Count], zs = new int[open.Count];
            for (int i = 0; i < open.Count; i++)
            {
                xs[i] = open[i].Position.x;
                zs[i] = open[i].Position.z;
            }
            int best = RM_BlazeKernel.FindBlaze(open.Count, xs, zs, MinOpenFires, ClusterRadius);
            return best < 0 ? IntVec3.Invalid : open[best].Position;
        }

        /// <summary>Send every available stamper at the biggest blaze. Returns how many were sent.</summary>
        public int ConvergePass(bool sendMessage)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.fireStampEnabled))
            {
                return 0;
            }
            IntVec3 blaze = FindBlaze();
            if (!blaze.IsValid)
            {
                lastBlaze = IntVec3.Invalid;
                return 0;
            }
            int sent = 0;
            Pawn first = null;
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!Available(p))
                {
                    continue;
                }
                bool onGoto = p.CurJobDef == JobDefOf.Goto;
                IntVec3 gotoCell = onGoto ? p.CurJob.targetA.Cell : IntVec3.Zero;
                int action = RM_BlazeKernel.ConvergeAction(p.Position.x, p.Position.z, blaze.x, blaze.z, onGoto, gotoCell.x, gotoCell.z);
                if (action == 0)
                {
                    continue;
                }
                if (action == 1)
                {
                    sent++;
                    continue; // already on its way
                }
                IntVec3 dest = CellFinder.StandableCellNear(blaze, map, ClusterRadius);
                if (!dest.IsValid)
                {
                    continue;
                }
                Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
                job.locomotionUrgency = LocomotionUrgency.Jog;
                job.expiryInterval = GotoExpiryTicks;
                job.checkOverrideOnExpire = true;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
                sent++;
                if (first == null) first = p;
            }
            bool newBlaze = RM_BlazeKernel.NewBlaze(lastBlaze.IsValid, lastBlaze.x, lastBlaze.z, blaze.x, blaze.z);
            lastBlaze = blaze;
            if (sendMessage && newBlaze && first != null)
            {
                Messages.Message("The " + first.def.label + " herd turns toward the fire.",
                    new TargetInfo(blaze, map), MessageTypeDefOf.ThreatSmall);
            }
            return sent;
        }

        /// <summary>Every available stamper within StampRadius of open fire stamps it. Returns fires put out.</summary>
        public int StampPass()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.fireStampEnabled))
            {
                return 0;
            }
            List<Thing> open = new List<Thing>(OpenFires());
            if (open.Count == 0)
            {
                return 0;
            }
            int put = 0;
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn s = pawns[i];
                if (!Available(s))
                {
                    continue;
                }
                for (int j = 0; j < open.Count; j++)
                {
                    Thing fire = open[j];
                    if (fire.Destroyed || !RM_BlazeKernel.Stamps(s.Position.x, s.Position.z, fire.Position.x, fire.Position.z))
                    {
                        continue;
                    }
                    Stomp(s, fire);
                    put++;
                }
            }
            return put;
        }

        private void Stomp(Pawn stamper, Thing fire)
        {
            IntVec3 cell = fire.Position;
            Thing clinging = (fire as Fire)?.parent;
            if (!fire.Destroyed) fire.Destroy();
            float angle = (cell - stamper.Position).AngleFlat;
            if (clinging != null && clinging != stamper && clinging.Spawned)
            {
                clinging.TakeDamage(new DamageInfo(DamageDefOf.Blunt, StompDamage, 0f, angle, stamper));
            }
            List<Thing> here = new List<Thing>(cell.GetThingList(map));
            for (int k = 0; k < here.Count; k++)
            {
                Thing t = here[k];
                if (t != stamper && t != clinging && t.def.category == ThingCategory.Building && t.def.useHitPoints)
                {
                    t.TakeDamage(new DamageInfo(DamageDefOf.Blunt, StompDamage, 0f, angle, stamper));
                }
            }
            FleckMaker.ThrowDustPuffThick(cell.ToVector3Shifted(), map, 1.6f, new Color(0.35f, 0.3f, 0.25f));
        }
    }

    // Proof hook for jawa/static_call (validation.py chain "stamp"). Builds the
    // fixture on the current map, drives the SHIPPED passes directly, cleans up.
    public static class RM_FireStampProof
    {
        private static IntVec3 FindSpot(Map map)
        {
            foreach (IntVec3 c in map.AllCells)
            {
                if (c.x < 40 || c.z < 40 || c.x > map.Size.x - 40 || c.z > map.Size.z - 40) continue;
                if (c.x % 9 != 0 || c.z % 9 != 0) continue;
                bool ok = true;
                foreach (IntVec3 o in GenRadial.RadialCellsAround(c, 22f, true))
                {
                    if (!o.InBounds(map) || !o.Standable(map) || o.Roofed(map) || o.GetFirstPawn(map) != null
                        || map.thingGrid.ThingAt(o, ThingDefOf.Fire) != null) { ok = false; break; }
                }
                if (ok) return c;
            }
            return IntVec3.Invalid;
        }

        private static int Fires(Map map, IntVec3 at, int n, List<Thing> made)
        {
            int lit = 0;
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = at + new IntVec3(i % 3, 0, i / 3);
                Fire f = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                f.fireSize = 0.6f;
                GenSpawn.Spawn(f, c, map);
                made.Add(f);
                lit++;
            }
            return lit;
        }

        /// <summary>"on": 2 open fires (below threshold) send nobody; 6 send the stamper; a stamper
        /// beside the blaze puts fires out. "off" (fireStampEnabled false): nobody sent, nothing out.</summary>
        public static string ProofStamp(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            var comp = map.GetComponent<RM_MapComponent_FireStamp>();
            if (comp == null) return "FAIL: RM_MapComponent_FireStamp not on the map";
            PawnKindDef kind = null;
            foreach (PawnKindDef k in DefDatabase<PawnKindDef>.AllDefsListForReading)
            {
                if (k.race != null && k.race.GetModExtension<RM_FireStamperExtension>() != null) { kind = k; break; }
            }
            if (kind == null) return "UNMEASURED: no loaded creature carries RM_FireStamperExtension (UtinniPatches/SWBestiary absent?)";
            bool on = mode != "off";
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedStamp = RM_LeaningScrubSettings.fireStampEnabled;
            var made = new List<Thing>();
            IntVec3 spot = IntVec3.Invalid;
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.fireStampEnabled = on;
                spot = FindSpot(map);
                if (!spot.IsValid) return "UNMEASURED: no unroofed, empty, fire-free 22-cell disc on this map";
                Pawn far = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(far, spot + new IntVec3(-18, 0, 0), map);
                made.Add(far);
                if (!far.Awake()) return "UNMEASURED: the spawned " + kind.defName + " is asleep";
                Fires(map, spot, 2, made);
                int sentSmall = comp.ConvergePass(sendMessage: false);
                bool jobSmall = far.CurJobDef == JobDefOf.Goto;
                Fires(map, spot + new IntVec3(0, 0, 1), 4, made);
                int sentBig = comp.ConvergePass(sendMessage: false);
                bool goesToBlaze = far.CurJobDef == JobDefOf.Goto && far.CurJob.targetA.Cell.InHorDistOf(spot, 8f);
                Pawn near = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(near, spot + new IntVec3(-2, 0, 0), map);
                made.Add(near);
                int before = map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count;
                int put = comp.StampPass();
                int after = map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count;
                string st = string.Format("kind={0} small:sent={1}/goto={2} big:sent={3}/toBlaze={4} stamped={5} fires {6}->{7}",
                    kind.defName, sentSmall, jobSmall, sentBig, goesToBlaze, put, before, after);
                if (on)
                {
                    if (sentSmall > 0 || jobSmall) return "FAIL: two fires (below the threshold) already summoned the herd " + st;
                    if (sentBig < 1 || !goesToBlaze) return "FAIL: a six-fire blaze sent no stamper toward it " + st;
                    if (put < 1 || after >= before) return "FAIL: a stamper beside the blaze put nothing out " + st;
                    return "PASS " + st;
                }
                if (sentBig > 0 || goesToBlaze || put > 0 || after < before) return "FAIL: fireStampEnabled off but the herd answered " + st;
                return "PASS off " + st;
            }
            finally
            {
                foreach (Thing t in made) { if (!t.Destroyed) t.Destroy(); }
                foreach (Thing f in new List<Thing>(map.listerThings.ThingsOfDef(ThingDefOf.Fire)))
                {
                    // anything the fixture's fires spread to while it ran
                    if (!f.Destroyed && spot.IsValid && f.Position.InHorDistOf(spot, 30f)) f.Destroy();
                }
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.fireStampEnabled = savedStamp;
            }
        }
    }
}
