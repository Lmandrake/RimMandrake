using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// FURNACEBEAST_WORLD_MIGRATION_1 — the return half of "de-spawns it back
    /// onto the world when the map is left".
    ///
    /// Same Harmony TARGET as RimMandrake.Inhabited.Patch_Game_DeinitAndRemoveMap
    /// (a different mod's WorldObject) — copied rather than guessed: a prefix
    /// on Game.DeinitAndRemoveMap is the last instant every pawn on the map is
    /// still spawned, alive and identifiable, before
    /// MapDeiniter.PassPawnsToWorld hands them to WorldPawns and WorldPawnGC
    /// becomes free to discard them with no log line.
    ///
    /// ⚠️ APPLIED MANUALLY IN A STATIC CTOR, not via a [HarmonyPatch] attribute
    /// + PatchAll — this assembly (mandrake.rm.pyrelands / FireEcologyHook)
    /// has no PatchAll() call anywhere; every one of its patches
    /// (Patch_FurnaceBeastHeatImmunity, Patch_LightningStrike_Fulgurite,
    /// WildPlantAllowlist) self-applies the same way. An attribute alone here
    /// would compile clean and never actually run — the exact "success with
    /// nothing changed" trap this codebase's CLAUDE.md warns about elsewhere.
    ///
    /// 🔑 SPECIES-AGNOSTIC BY DESIGN, the same rule
    /// JobGiver_RUT_FurnaceThermalCycle already follows: gate on the COMP
    /// (CompFurnaceThermalCharge), never on a defName. This assembly ships the
    /// mechanic; the creature itself is campaign content one tier up
    /// (RimUtinni) and must not be a compile-time or runtime dependency here.
    ///
    /// ⚠️ SCOPE: this catches a furnace-beast still on a map at the moment
    /// the WHOLE MAP is torn down (abandon, or a transient visited-tile map
    /// being released) — not a beast that individually wanders off the map's
    /// edge mid-play while the map keeps existing. The latter is vanilla
    /// wildlife's own ordinary despawn-at-edge behaviour, and hooking it
    /// specifically was judged the wrong place to spend risk here: it would
    /// need verifying against live wildlife-exit behaviour this session
    /// cannot check offline, for a case the owner's cycle description does
    /// not actually describe. What the cycle DOES describe — the herd is not
    /// on this map, therefore it is somewhere on the world — is exactly what
    /// this covers.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class Patch_FurnaceHerdMapRemoval
    {
        static Patch_FurnaceHerdMapRemoval()
        {
            try
            {
                new Harmony("mandrake.rm.pyrelands").Patch(
                    AccessTools.Method(typeof(Game), nameof(Game.DeinitAndRemoveMap)),
                    prefix: new HarmonyMethod(typeof(Patch_FurnaceHerdMapRemoval), nameof(RecallFurnaceBeasts)));
                Log.Message("[RimMandrake.Pyrelands] furnace-beast herd world-recall: armed; "
                    + "surviving furnace-beasts rejoin the world when their map is removed.");
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] furnace-beast herd world-recall failed to patch "
                    + "Game.DeinitAndRemoveMap: " + e
                    + " — a beast left on an abandoned map will be lost to WorldPawnGC instead of "
                    + "rejoining a world herd.");
            }
        }

        public static void RecallFurnaceBeasts(Map map)
        {
            if (map == null
                || !RM_PyrelandsSettings.pyrelandsEnabled
                || !RM_PyrelandsSettings.furnaceThermalEnabled
                || !RM_PyrelandsSettings.furnaceWorldMigrationEnabled)
            {
                return;
            }

            List<Pawn> beasts = map.mapPawns.AllPawns
                .Where(p => p != null && !p.Dead && p.Faction == null
                         && p.TryGetComp<CompFurnaceThermalCharge>() != null)
                .ToList();
            if (beasts.Count == 0)
            {
                return;
            }

            WorldObject_RM_FurnaceHerd herd = Find.WorldObjects?.WorldObjectAt<WorldObject_RM_FurnaceHerd>(map.Tile);
            if (herd == null)
            {
                herd = (WorldObject_RM_FurnaceHerd)WorldObjectMaker.MakeWorldObject(PyrelandsMechanicsDefOf.RM_FurnaceHerd);
                herd.Tile = map.Tile;
                herd.leg = WorldObject_RM_FurnaceHerd.LegForBiome(map.Biome);
                Find.WorldObjects.Add(herd);
            }

            int returned = 0;
            for (int i = 0; i < beasts.Count; i++)
            {
                Pawn p = beasts[i];
                p.DeSpawnOrDeselect();
                if (herd.members.TryAddOrTransfer(p, canMergeWithExistingStacks: false))
                {
                    returned++;
                }
                else
                {
                    Log.Warning("[RimMandrake.Pyrelands] a furnace-beast left " + map.Parent?.LabelCap
                        + " and could not rejoin a world herd; it is lost.");
                }
            }
            if (returned > 0)
            {
                Log.Message("[RimMandrake.Pyrelands] " + returned + " furnace-beast(s) returned to the world from "
                    + map.Parent?.LabelCap + " (" + herd.leg + " leg).");
            }
        }
    }
}
