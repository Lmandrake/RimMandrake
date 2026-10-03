using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SCALD_RETURN_GALLERY_1 (sitting 2026-10-02, Q3 (c)). A half-buried Rust Cathedral coolant
    // manifold on the Scald's floor. Five branches run from the hub; each outlet can be probed once
    // and reports a gauge reading. The reading is derived from the branch's stored state, and the
    // same state is physical: a burst piece (Broken) or a buried gap (Silted) sits at exactly the
    // segment the gauge names, so every conclusion can be checked on foot. Marking the wrong branch
    // jams the locker for a day and changes nothing else. Nothing here touches any live system.
    public enum GalleryRole { Feed, Return, Broken, Silted }

    public class CompProperties_GalleryOutlet : CompProperties
    {
        public CompProperties_GalleryOutlet() { compClass = typeof(RM_CompGalleryOutlet); }
    }

    public class CompProperties_GalleryHub : CompProperties
    {
        public CompProperties_GalleryHub() { compClass = typeof(RM_CompGalleryHub); }
    }

    public class RM_CompGalleryOutlet : ThingComp
    {
        public GalleryRole role;
        public int segment;      // Broken/Silted: the segment (counted from the hub, 1-based) where the circuit fails
        public int length;       // segments from hub to this outlet
        public int tempC;
        public char letter = 'A';
        public bool probed;

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref role, "galleryRole");
            Scribe_Values.Look(ref segment, "gallerySegment");
            Scribe_Values.Look(ref length, "galleryLength");
            Scribe_Values.Look(ref tempC, "galleryTempC");
            Scribe_Values.Look(ref letter, "galleryLetter", 'A');
            Scribe_Values.Look(ref probed, "galleryProbed", false);
        }

        // Full-pressure outward warm flow is the only true return.
        public bool IsTrueReturn => role == GalleryRole.Return;

        public string Reading()
        {
            string head = "Branch " + letter + " (" + length + " segments from the manifold): ";
            switch (role)
            {
                case GalleryRole.Return:
                    return head + "pressure holds to the far end (100%). Water " + tempC + " C, flowing outward from the manifold.";
                case GalleryRole.Feed:
                    return head + "pressure holds to the far end (100%). Water " + tempC + " C, drawn inward toward the manifold.";
                case GalleryRole.Broken:
                    return head + "pressure steady at segment " + (segment - 1) + ", gone at segment " + segment + " and beyond (0%). No flow.";
                default:
                    return head + "pressure steady at segment " + (segment - 1) + ", then falls and holds at 20% from segment " + segment
                        + " to the far end. Water " + tempC + " C, flowing outward, sluggish.";
            }
        }

        public void Probe(Pawn pawn)
        {
            if (probed)
            {
                return;
            }
            probed = true;
            Messages.Message(Reading(), parent, MessageTypeDefOf.NeutralEvent, false);
        }

        public override string CompInspectStringExtra()
        {
            return probed ? Reading() : "Branch " + letter + ": not probed. A colonist can hook a gauge to its port.";
        }
    }

    public class RM_CompGalleryHub : ThingComp
    {
        public const int JamTicks = 15000;

        private List<Thing> outlets = new List<Thing>();
        private Thing locker;
        private bool solved;
        private int jammedUntil = -1;
        private int lastMark = -1;

        public override void PostExposeData()
        {
            Scribe_Collections.Look(ref outlets, "galleryOutlets", LookMode.Reference);
            Scribe_References.Look(ref locker, "galleryLocker");
            Scribe_Values.Look(ref solved, "gallerySolved", false);
            Scribe_Values.Look(ref jammedUntil, "galleryJammedUntil", -1);
            Scribe_Values.Look(ref lastMark, "galleryLastMark", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && outlets == null)
            {
                outlets = new List<Thing>();
            }
        }

        public void Init(List<Thing> outletList, Thing lockerThing)
        {
            outlets = outletList;
            locker = lockerThing;
        }

        private IEnumerable<RM_CompGalleryOutlet> Comps()
        {
            foreach (Thing t in outlets)
            {
                RM_CompGalleryOutlet c = t?.TryGetComp<RM_CompGalleryOutlet>();
                if (c != null)
                {
                    yield return c;
                }
            }
        }

        public bool AllProbed
        {
            get
            {
                int n = 0;
                foreach (RM_CompGalleryOutlet c in Comps())
                {
                    n++;
                    if (!c.probed)
                    {
                        return false;
                    }
                }
                return n > 0;
            }
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            if (solved)
            {
                sb.Append("The return is traced. The service locker stands open.");
                return sb.ToString();
            }
            int probedCount = 0;
            int total = 0;
            foreach (RM_CompGalleryOutlet c in Comps())
            {
                total++;
                if (c.probed)
                {
                    probedCount++;
                }
            }
            sb.Append("Branches probed: " + probedCount + " / " + total + ". ");
            if (Find.TickManager != null && Find.TickManager.TicksGame < jammedUntil)
            {
                sb.Append("Latch jammed for " + (jammedUntil - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ". Readings are unchanged.");
            }
            else if (probedCount == total && total > 0)
            {
                sb.Append("Every branch has a reading. Mark the one that still returns the Cathedral's warm water.");
            }
            else
            {
                sb.Append("Probe every branch outlet to read the circuit.");
            }
            return sb.ToString();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (solved || !AllProbed)
            {
                yield break;
            }
            Command_Action mark = new Command_Action
            {
                defaultLabel = "Mark return branch",
                defaultDesc = "Choose the branch that still carries the Cathedral's warm water back at full pressure. "
                    + "A wrong choice only jams the locker latch for a day.",
                icon = TexCommand.Attack,
                action = OpenMenu
            };
            if (Find.TickManager.TicksGame < jammedUntil)
            {
                mark.Disable("Latch jammed for " + (jammedUntil - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ".");
            }
            yield return mark;
        }

        private void OpenMenu()
        {
            List<FloatMenuOption> opts = new List<FloatMenuOption>();
            foreach (RM_CompGalleryOutlet c in Comps())
            {
                RM_CompGalleryOutlet captured = c;
                opts.Add(new FloatMenuOption("Branch " + c.letter, () => Mark(captured)));
            }
            Find.WindowStack.Add(new FloatMenu(opts));
        }

        public void Mark(RM_CompGalleryOutlet branch)
        {
            if (solved || Find.TickManager.TicksGame < jammedUntil)
            {
                return;
            }
            if (branch.IsTrueReturn)
            {
                solved = true;
                Messages.Message("Branch " + branch.letter + " is the live return. The service locker unlatches.",
                    parent, MessageTypeDefOf.PositiveEvent, false);
                SpawnRewards();
            }
            else
            {
                lastMark = branch.letter;
                jammedUntil = Find.TickManager.TicksGame + JamTicks;
                Messages.Message("Branch " + branch.letter + " is not the live return: the locker latch jams for a day. The readings still stand.",
                    parent, MessageTypeDefOf.NegativeEvent, false);
            }
        }

        private void SpawnRewards()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            IntVec3 at = locker != null && locker.Spawned ? locker.Position : parent.Position;
            foreach (string name in new[] { "RM_ImmersionSchematic", "RM_CathedralHeatLog" })
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def == null)
                {
                    continue;
                }
                GenPlace.TryPlaceThing(ThingMaker.MakeThing(def), at, map, ThingPlaceMode.Near);
            }
        }
    }
}
