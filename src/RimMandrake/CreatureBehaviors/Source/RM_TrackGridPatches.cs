using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — the writer.
    //
    // Postfix on Pawn_FilthTracker.Notify_EnteredNewCell. RimSage-verified
    // against the 1.6 decompile (2026-10-01): Pawn_PathFollower.
    // TryEnterNextPathCell calls it for EVERY pawn that steps into a cell,
    // and PawnComponentsUtility.AddComponentsForSpawn gives every spawned
    // pawn a Pawn_FilthTracker with no race test. The race filth gates the
    // item worried about (Humanlike / Insect / IsAnimal) and the Flying early
    // return are all INSIDE the method body, so a postfix sees humanlikes,
    // animals, mechs and entities alike; no second hook is needed. We skip
    // flyers ourselves (a bird in the air leaves no print).
    //
    // No visibility filter, on purpose (turn-4 IN, "unseen things leave
    // prints"): an invisible pawn (HediffComp_Invisibility,
    // IsPsychologicallyInvisible) writes exactly like a seen one; its record
    // is FLAGGED (RM_TrackRecord.Invisible) so a reader can tell, and a
    // surface may give it its own sprite (invisibleTexPath: a sand wake).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_TrackGridPatches
    {
        public static bool patched;

        // Every RM_TrackSurfaceExtension on a def (several consumers may tag one shared terrain);
        // null when it carries none. Defs are immutable after load, so the cache never goes stale.
        private static readonly Dictionary<Def, List<RM_TrackSurfaceExtension>> extCache = new Dictionary<Def, List<RM_TrackSurfaceExtension>>();

        static RM_TrackGridPatches()
        {
            try
            {
                var harmony = new Harmony("mandrake.rm.creaturebehaviors.trackgrid");
                harmony.Patch(AccessTools.Method(typeof(Pawn_FilthTracker), nameof(Pawn_FilthTracker.Notify_EnteredNewCell)),
                    postfix: new HarmonyMethod(typeof(RM_TrackGridPatches), nameof(Postfix_EnteredNewCell)));
                patched = true;
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] track grid: could not patch Pawn_FilthTracker.Notify_EnteredNewCell — "
                          + "no footprints will be laid. " + e);
            }
        }

        public static void Postfix_EnteredNewCell(Pawn ___pawn)
        {
            if (!RM_CreatureBehaviorsSettings.tracksEnabled) return;
            Pawn pawn = ___pawn;
            if (pawn == null || !pawn.Spawned || pawn.Flying) return;
            RM_TrackGridDiag.stepsSeen++;
            try
            {
                Map map = pawn.Map;
                RM_TrackSurfaceExtension surface = SurfaceAt(pawn.Position, map);
                if (surface == null) return;
                RM_MapComponent_TrackGrid.For(map)?.RecordStep(pawn, surface);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] track grid writer threw: " + e, 0x7A3C51);
            }
        }

        /// <summary>
        /// The track surface at a cell: the terrain's, else any filth's in the cell, else the map biome's
        /// buildup surface where the cell's sand depth reaches its minSandDepth (the Pyrelands' ash), skipping
        /// an extension whose biome filter excludes this map. Null if none.
        /// </summary>
        public static RM_TrackSurfaceExtension SurfaceAt(IntVec3 c, Map map)
        {
            RM_TrackSurfaceExtension ext = OwnSurfaceAt(c, map);
            if (ext != null) return ext;
            ext = BuildupSurfaceOf(map);
            if (ext != null && map.sandGrid != null && map.sandGrid.GetDepth(c) >= ext.minSandDepth) return ext;
            return null;
        }

        /// <summary>The cell's own surface, its terrain's or a filth's in it; null if neither carries one.</summary>
        public static RM_TrackSurfaceExtension OwnSurfaceAt(IntVec3 c, Map map)
        {
            RM_TrackSurfaceExtension ext = ExtOf(c.GetTerrain(map), map);
            if (ext != null) return ext;
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Filth)
                {
                    ext = ExtOf(things[i].def, map);
                    if (ext != null) return ext;
                }
            }
            return null;
        }

        /// <summary>The map biome's buildup surface (an RM_TrackSurfaceExtension with minSandDepth > 0), or null.</summary>
        public static RM_TrackSurfaceExtension BuildupSurfaceOf(Map map)
        {
            RM_TrackSurfaceExtension ext = ExtOf(map?.Biome, map);
            return ext != null && ext.IsBuildupSurface ? ext : null;
        }

        private static RM_TrackSurfaceExtension ExtOf(Def def, Map map)
        {
            if (def == null) return null;
            if (!extCache.TryGetValue(def, out List<RM_TrackSurfaceExtension> list))
            {
                if (def.modExtensions != null)
                {
                    for (int i = 0; i < def.modExtensions.Count; i++)
                    {
                        if (def.modExtensions[i] is RM_TrackSurfaceExtension e)
                        {
                            if (list == null) list = new List<RM_TrackSurfaceExtension>(1);
                            list.Add(e);
                        }
                    }
                }
                extCache[def] = list;
            }
            if (list == null) return null;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i].AppliesTo(map)) return list[i];
            }
            return null;
        }
    }
}
