using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — marks a surface that takes prints.
    //
    // Put it on a TerrainDef (the Stillsand's sand) or on a filth ThingDef
    // (the Warscar's condition-laid settled film). A pawn stepping onto a cell
    // whose terrain, or any filth in it, carries this extension lays a print
    // in RM_MapComponent_TrackGrid. Nothing else is needed from a biome but
    // this XML and its own eraser call (ClearCell / ClearRect / the downwind
    // sweep on the component).
    //
    //   <modExtensions>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_TrackSurfaceExtension">
    //       <raceOverrides>
    //         <li><race>RM_Oommok</race><texPath>Things/Tracks/RM_OommokPrint</texPath></li>
    //       </raceOverrides>
    //     </li>
    //   </modExtensions>
    //
    // Print class, in order: a race override; then drag (a crawling pawn);
    // then human (humanlike, or a mech under bs 1.5); then large (bs >= 1.5);
    // then animal. Every texture is drawn pointing NORTH and rotated by the
    // engine to the walker's heading.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TrackSurfaceExtension : DefModExtension
    {
        public string humanTexPath = "Things/Tracks/RM_TrackPrint_Human";
        public string animalTexPath = "Things/Tracks/RM_TrackPrint_Animal";
        public string largeTexPath = "Things/Tracks/RM_TrackPrint_Large";
        public string dragTexPath = "Things/Tracks/RM_TrackDrag";
        public List<RM_TrackRaceOverride> raceOverrides;

        /// <summary>Base print size in cells for a medium (bs 0.65-1.5) walker; size class scales it.</summary>
        public float printSize = 0.6f;

        /// <summary>Walkers lighter than this leave nothing (0 = everything leaves prints).</summary>
        public float minBodySize = 0f;

        public string TexPathFor(ThingDef race, RM_TrackSize size, RM_TrackSource source, bool drag)
        {
            if (raceOverrides != null)
            {
                for (int i = 0; i < raceOverrides.Count; i++)
                {
                    RM_TrackRaceOverride o = raceOverrides[i];
                    if (o != null && o.race == race && !o.texPath.NullOrEmpty()) return o.texPath;
                }
            }
            if (drag) return dragTexPath;
            if (source == RM_TrackSource.Humanlike) return humanTexPath;
            if (size >= RM_TrackSize.Large) return largeTexPath;
            if (source == RM_TrackSource.Mechanoid) return humanTexPath;
            return animalTexPath;
        }

        public float DrawSizeFor(RM_TrackSize size)
        {
            switch (size)
            {
                case RM_TrackSize.Small: return printSize * 0.6f;
                case RM_TrackSize.Large: return printSize * 1.5f;
                case RM_TrackSize.Huge: return printSize * 2.2f;
                default: return printSize;
            }
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (printSize <= 0f) yield return "RM_TrackSurfaceExtension: printSize must be > 0";
            if (humanTexPath.NullOrEmpty() || animalTexPath.NullOrEmpty() || largeTexPath.NullOrEmpty() || dragTexPath.NullOrEmpty())
            {
                yield return "RM_TrackSurfaceExtension: every print class needs a texPath";
            }
            if (raceOverrides != null)
            {
                foreach (RM_TrackRaceOverride o in raceOverrides)
                {
                    if (o == null || o.race == null || o.texPath.NullOrEmpty())
                    {
                        yield return "RM_TrackSurfaceExtension: a raceOverride needs both race and texPath";
                    }
                }
            }
        }
    }

    public class RM_TrackRaceOverride
    {
        public ThingDef race;
        public string texPath;
    }
}
