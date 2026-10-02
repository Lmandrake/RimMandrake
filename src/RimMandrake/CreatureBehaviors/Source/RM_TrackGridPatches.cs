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
    // IsPsychologicallyInvisible) writes exactly like a seen one.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_TrackGridPatches
    {
        public static bool patched;

        private static readonly Dictionary<Def, RM_TrackSurfaceExtension> extCache = new Dictionary<Def, RM_TrackSurfaceExtension>();

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

        /// <summary>The track surface at a cell: the terrain's, else any filth's in the cell. Null if none.</summary>
        public static RM_TrackSurfaceExtension SurfaceAt(IntVec3 c, Map map)
        {
            RM_TrackSurfaceExtension ext = ExtOf(c.GetTerrain(map));
            if (ext != null) return ext;
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Filth)
                {
                    ext = ExtOf(things[i].def);
                    if (ext != null) return ext;
                }
            }
            return null;
        }

        private static RM_TrackSurfaceExtension ExtOf(Def def)
        {
            if (def == null) return null;
            if (!extCache.TryGetValue(def, out RM_TrackSurfaceExtension ext))
            {
                ext = def.GetModExtension<RM_TrackSurfaceExtension>();
                extCache[def] = ext;
            }
            return ext;
        }
    }
}
