using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
    /// <summary>Readouts and fixture setup for northstar/concept_scenes.py. Never used by play.</summary>
    public static class RM_PitPrisonProof
    {
        private static Pawn Pawn(string id) => Find.CurrentMap.mapPawns.AllPawnsSpawned.First(p => p.ThingID == id);
        private static string Number(float n) => n.ToString("R", CultureInfo.InvariantCulture);
        private static string Hash(byte[] bytes)
        {
            using (var h = SHA256.Create()) return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        public static string Identity(string unused)
        {
            var a = typeof(RM_PitPrisonProof).Assembly;
            return "IDENTITY mvid=" + a.ManifestModule.ModuleVersionId + " sha256=" + Hash(File.ReadAllBytes(a.Location));
        }

        public static string State(string id)
        {
            Pawn p = Pawn(id);
            return "STATE id=" + id + " prisoner=" + p.IsPrisonerOfColony + " downed=" + p.Downed
                + " dead=" + p.Dead + " held=" + RM_SuperdeepTrap.IsHeld(p)
                + " kept=" + RM_PitPrisonCare.Kept(p) + " x=" + p.Position.x + " z=" + p.Position.z
                + " food=" + Number(p.needs.food.CurLevel) + " rest=" + Number(p.needs.rest.CurLevel)
                + " job=" + (p.CurJobDef?.defName ?? "none") + " inBed=" + p.InBed()
                + " tendable=" + p.health.hediffSet.hediffs.Count(h => h.TendableNow())
                + " tended=" + p.health.hediffSet.hediffs.Count(h => h.IsTended());
        }

        /// <summary>Ask a REAL registered vanilla work giver, optionally order the job it returned.
        /// arg worker;patient;feed|deliver|tend|bed;ask|start. No fabricated job or nutrition.</summary>
        public static string Care(string arg)
        {
            string[] a = arg.Split(';');
            Pawn w = Pawn(a[0]), p = Pawn(a[1]);
            // WorkGiver_Tend is a base class, not a registered worker. Select the
            // actual vanilla WorkGiverDef (Core/Defs/WorkGiverDefs/WorkGivers.xml).
            string giverName = a[2] == "feed" ? "FeedPrisoner" : a[2] == "deliver"
                ? "DeliverFoodToPrisoner" : a[2] == "tend" ? "DoctorTendToHumanlikes" : "TakePrisonerToBed";
            var giver = (WorkGiver_Scanner)DefDatabase<WorkGiverDef>.GetNamed(giverName).Worker;
            Job job = giver.HasJobOnThing(w, p, false) ? giver.JobOnThing(w, p, false) : null;
            string result = "CARE kind=" + a[2] + " giver=" + giverName + " job=" + (job?.def.defName ?? "none");
            if (job != null && a[3] == "start") result += " ordered=" + w.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            return result;
        }

        /// <summary>Fingerprint the snapshot's rectangle before staging and after reloading it.
        /// Includes underlying terrain, roofs, liquid identity and exact water, and every thing.</summary>
        public static string Rect(string arg)
        {
            int[] a = arg.Split(',').Select(int.Parse).ToArray();
            var map = Find.CurrentMap;
            var e = map.GetComponent<RM_MapComponent_Excavation>();
            var rect = new CellRect(a[0], a[1], a[2], a[3]);
            var sb = new StringBuilder();
            foreach (IntVec3 c in rect)
            {
                sb.Append(c).Append(':').Append(c.GetTerrain(map)?.defName).Append('/')
                    .Append(map.terrainGrid.UnderTerrainAt(c)?.defName).Append('/').Append(c.GetRoof(map)?.defName)
                    .Append('/').Append(e.ExcavatedDepthAt(c)).Append('/').Append(e.WaterDlAt(c))
                    .Append('/').Append(e.FluidAt(c)?.defName).Append(';');
                foreach (Thing t in c.GetThingList(map).OrderBy(t => t.ThingID))
                    sb.Append(t.ThingID).Append(':').Append(t.def.defName).Append(':').Append(t.stackCount)
                        .Append(':').Append(t.HitPoints).Append(':').Append(t.Position).Append(';');
            }
            return "RECT sha256=" + Hash(Encoding.UTF8.GetBytes(sb.ToString()))
                + " beds=" + map.listerBuildings.allBuildingsColonist.OfType<Building_Bed>().Count(b => b.OccupiedRect().Overlaps(rect));
        }
    }
}
