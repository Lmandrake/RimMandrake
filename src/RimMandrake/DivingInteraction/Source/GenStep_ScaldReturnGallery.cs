using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SCALD_RETURN_GALLERY_1. Lays the Return Gallery on the Scald floor: a 3x3 hub, five branches
    // of piping ending in outlets, and a service locker. Roles are shuffled per map: one true
    // Return, one Feed (cold, inward), two Broken (visible burst piece), one Silted (a decoy that
    // is warm and outward but choked; its pipes are buried beyond the choke). Skips quietly when no
    // free site exists. Scoped like the vent step: listed on the Scald generator only.
    public class GenStep_ScaldReturnGallery : GenStep
    {
        private const int Margin = 12;
        private const int VentClear = 5;
        private const int ExitPad = 4;
        private static readonly IntVec3[] Dirs =
        {
            new IntVec3(0, 0, 1), new IntVec3(0, 0, -1), new IntVec3(1, 0, 0), new IntVec3(-1, 0, 0), new IntVec3(1, 0, 1)
        };
        private static readonly int[] Lens = { 7, 7, 7, 7, 5 };
        private static readonly IntVec3 LockerOffset = new IntVec3(3, 0, -1);

        public override int SeedPart => 7203139;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_MapComponent_ScaldVentForecast.IsScaldFloorMap(map) || !RM_DivingSettings.masterEnabled
                || !RM_DivingSettings.scaldReturnGalleryEnabled)
            {
                return;
            }
            ThingDef hubDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ReturnGalleryHub");
            ThingDef outletDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GalleryOutlet");
            ThingDef pipeDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GalleryPipe");
            ThingDef breakDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GalleryBreak");
            ThingDef lockerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ReturnGalleryLocker");
            if (hubDef == null || outletDef == null || pipeDef == null || breakDef == null || lockerDef == null)
            {
                return;
            }
            IntVec3 c;
            if (!FindSite(map, out c))
            {
                Log.Warning("[RM] Return Gallery: no free site on the Scald floor map; skipped.");
                return;
            }

            List<GalleryRole> roles = new List<GalleryRole>
            {
                GalleryRole.Return, GalleryRole.Feed, GalleryRole.Broken, GalleryRole.Broken, GalleryRole.Silted
            };
            roles.Shuffle();

            Thing hub = GenSpawn.Spawn(ThingMaker.MakeThing(hubDef), c, map);
            Thing locker = GenSpawn.Spawn(ThingMaker.MakeThing(lockerDef), c + LockerOffset, map);
            List<Thing> outlets = new List<Thing>();
            for (int i = 0; i < Dirs.Length; i++)
            {
                int len = Lens[i];
                GalleryRole role = roles[i];
                int seg = (role == GalleryRole.Broken || role == GalleryRole.Silted) ? Rand.RangeInclusive(2, len - 2) : 0;
                for (int s = 1; s < len; s++)
                {
                    IntVec3 cell = SegCell(c, Dirs[i], s);
                    if (role == GalleryRole.Broken && s == seg)
                    {
                        GenSpawn.Spawn(ThingMaker.MakeThing(breakDef), cell, map);
                    }
                    else if (role == GalleryRole.Silted && s >= seg)
                    {
                        // buried: nothing to see beyond the choke
                    }
                    else
                    {
                        GenSpawn.Spawn(ThingMaker.MakeThing(pipeDef), cell, map);
                    }
                }
                Thing outlet = GenSpawn.Spawn(ThingMaker.MakeThing(outletDef), SegCell(c, Dirs[i], len), map);
                RM_CompGalleryOutlet oc = outlet.TryGetComp<RM_CompGalleryOutlet>();
                if (oc != null)
                {
                    oc.role = role;
                    oc.segment = seg;
                    oc.length = len;
                    oc.letter = (char)('A' + i);
                    oc.tempC = role == GalleryRole.Feed ? Rand.RangeInclusive(6, 12) : Rand.RangeInclusive(66, 78);
                }
                outlets.Add(outlet);
            }
            hub.TryGetComp<RM_CompGalleryHub>()?.Init(outlets, locker);
        }

        private static IntVec3 SegCell(IntVec3 hub, IntVec3 dir, int seg)
        {
            return hub + dir * (seg + 1);
        }

        private static bool FindSite(Map map, out IntVec3 site)
        {
            List<CellRect> avoid = new List<CellRect>();
            ThingDef exitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SeaDiveExit");
            if (exitDef != null)
            {
                foreach (Thing t in map.listerThings.ThingsOfDef(exitDef))
                {
                    avoid.Add(t.OccupiedRect().ExpandedBy(ExitPad));
                }
            }
            ThingDef ventDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_ScaldVent");
            if (ventDef != null)
            {
                foreach (Thing t in map.listerThings.ThingsOfDef(ventDef))
                {
                    avoid.Add(t.OccupiedRect().ExpandedBy(VentClear));
                }
            }
            for (int attempt = 0; attempt < 300; attempt++)
            {
                IntVec3 c = new IntVec3(Rand.RangeInclusive(Margin, map.Size.x - Margin), 0, Rand.RangeInclusive(Margin, map.Size.z - Margin));
                if (SiteFree(map, c, avoid))
                {
                    site = c;
                    return true;
                }
            }
            site = IntVec3.Invalid;
            return false;
        }

        private static bool SiteFree(Map map, IntVec3 c, List<CellRect> avoid)
        {
            List<IntVec3> cells = new List<IntVec3>();
            foreach (IntVec3 h in CellRect.CenteredOn(c, 3, 3))
            {
                cells.Add(h);
            }
            for (int i = 0; i < Dirs.Length; i++)
            {
                for (int s = 1; s <= Lens[i]; s++)
                {
                    cells.Add(SegCell(c, Dirs[i], s));
                }
            }
            cells.Add(c + LockerOffset);
            foreach (IntVec3 cell in cells)
            {
                if (!cell.InBounds(map) || !cell.Standable(map) || cell.GetEdifice(map) != null)
                {
                    return false;
                }
                foreach (CellRect r in avoid)
                {
                    if (r.Contains(cell))
                    {
                        return false;
                    }
                }
            }
            return true;
        }
    }
}
