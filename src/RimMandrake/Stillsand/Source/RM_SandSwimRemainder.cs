using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;
using RimMandrake.CreatureBehaviors;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SAND_SWIM_REMAINDER_1: drift depth as swim ground (§2), sand fishing's stalker wake (§6),
    // and the Listening (§7). The thumper is in RM_Thumper.cs. Settings: RM_SandSwimRemSettings.
    // All hooks into other assemblies are SOFT: a missing MovingDunes or a renamed method logs once and
    // the feature is simply absent, never an exception per tick.
    // ════════════════════════════════════════════════════════════════════

    // ── §2 drift depth ────────────────────────────────────────────────
    // RM_SandSwimUtility.IsSwimTerrain (CreatureBehaviors) knows terrains only. A postfix adds: on a map
    // with a MovingDunes dune field, a cell whose vanilla sand depth (Map.sandGrid, which the dune engine
    // writes) is at or above driftSwimDepth is swim ground too, unless an impassable edifice stands on it.
    public static class RM_DriftSwim
    {
        private static Func<Map, bool> registryGet;
        private static bool lookupTried;

        public static bool DuneFieldActive(Map map)
        {
            if (!lookupTried)
            {
                lookupTried = true;
                Type reg = GenTypes.GetTypeInAnyAssembly("RimMandrake.MovingDunes.DuneFieldRegistry");
                MethodInfo mi = reg?.GetMethod("IsActive", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(Map) }, null);
                registryGet = mi == null ? null : (Func<Map, bool>)Delegate.CreateDelegate(typeof(Func<Map, bool>), mi);
            }
            return registryGet != null && registryGet(map);
        }

        public static bool IsDriftSwimCell(IntVec3 c, Map map)
        {
            if (!RM_SandSwimRemSettings.driftSwimEnabled || map == null || !c.InBounds(map)) return false;
            if (!DuneFieldActive(map)) return false;
            SandGrid grid = map.sandGrid;
            if (grid == null || grid.GetDepth(c) < RM_SandSwimRemSettings.driftSwimDepth) return false;
            Building edifice = c.GetEdifice(map);
            if (edifice != null && edifice.def.passability == Traversability.Impassable) return false;
            TerrainDef t = c.GetTerrain(map);
            return t != null && !t.IsWater;
        }

        public static void Postfix(IntVec3 c, Map map, ref bool __result)
        {
            if (!__result && IsDriftSwimCell(c, map)) __result = true;
        }
    }

    // ── §6 sand fishing ───────────────────────────────────────────────
    // A fishing session on deep sand is drumming. Once per session (a pawn newly seen on the Fish job
    // with the target on RM_DeepSand) rolls sandFishingWakeChance; on a hit the nearest submerged,
    // non-player swimmer in range gets a Goto to the fisher, so the wake is the warning.
    public class RM_MapComponent_SandFishing : MapComponent
    {
        private readonly HashSet<int> fishingNow = new HashSet<int>();
        private readonly HashSet<int> seen = new HashSet<int>();
        public int sessionsRolled;
        public int wakesDrawn;

        public RM_MapComponent_SandFishing(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % 120 != 0 || !RM_SandSwimRemSettings.sandFishingWakeEnabled) return;
            JobDef fish = DefDatabase<JobDef>.GetNamedSilentFail("Fish");
            if (fish == null) return;
            seen.Clear();
            IReadOnlyList<Pawn> col = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < col.Count; i++)
            {
                Pawn p = col[i];
                Job j = p.CurJob;
                if (j == null || j.def != fish) continue;
                IntVec3 target = j.targetA.Cell;
                TerrainDef t = target.InBounds(map) ? target.GetTerrain(map) : null;
                if (t == null || t.defName != "RM_DeepSand") continue;
                seen.Add(p.thingIDNumber);
                if (fishingNow.Contains(p.thingIDNumber)) continue;
                RollSession(p);
            }
            fishingNow.Clear();
            foreach (int id in seen) fishingNow.Add(id);
        }

        public bool RollSession(Pawn fisher)
        {
            sessionsRolled++;
            if (!Rand.Chance(RM_SandSwimRemSettings.sandFishingWakeChance)) return false;
            int n = RM_SwimmerCalls.Call(map, fisher.Position, 45f, 1, 3);
            if (n > 0) wakesDrawn++;
            return n > 0;
        }
    }

    // ── §7 the Listening ──────────────────────────────────────────────
    // Wind hiss and saltation: two camera-attached sustainers whose "Wind" external parameter is the map's
    // WindManager speed (the SoundDef curves do the scaling); only on the map in view, only on a Stillsand
    // map. Deviation from the spec's "ride RM_MapComponent_ProximitySoundscape": that component is driven
    // by tagged Things near the listener and cannot scale on wind, so the bed is its own small component.
    // Singing dunes: Harmony prefix on MapComponent_DuneField.SetDepthHysteretic notes each slab shed
    // from a cell (a slip face); a sampled one plays the song, and the first one near a player building
    // posts a one-line warning (scribed, once per map).
    public class RM_MapComponent_SandListening : MapComponent
    {
        private Sustainer hiss;
        private Sustainer saltation;
        private bool warned;
        private int lastSongTick = -99999;
        public int songsPlayed;

        public RM_MapComponent_SandListening(Map map) : base(map) { }

        public static bool IsStillsandMap(Map map)
        {
            return map?.Biome != null && map.Biome.defName.Contains("Stillsand");
        }

        public override void MapComponentTick()
        {
            if (!RM_SandSwimRemSettings.listeningHissEnabled || Find.CurrentMap != map || !IsStillsandMap(map))
            {
                End();
                return;
            }
            float wind = map.windManager.WindSpeed;
            Maintain(ref hiss, RM_StillsandListeningDefOf.RM_SandHiss, wind);
            Maintain(ref saltation, RM_StillsandListeningDefOf.RM_SandSaltation, wind);
        }

        private static void Maintain(ref Sustainer s, SoundDef def, float wind)
        {
            if (def == null) return;
            if (s == null || s.Ended) s = def.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick));
            if (s == null) return;
            s.Maintain();
            s.externalParams["Wind"] = wind;
        }

        private void End()
        {
            if (hiss != null && !hiss.Ended) hiss.End();
            if (saltation != null && !saltation.Ended) saltation.End();
            hiss = null; saltation = null;
        }

        public override void MapRemoved() { End(); base.MapRemoved(); }

        // A slab was shed from this cell by the dune engine.
        public void NoteSlipFace(IntVec3 cell)
        {
            if (!IsStillsandMap(map)) return;
            int now = Find.TickManager.TicksGame;
            if (now - lastSongTick < 900 || !Rand.Chance(0.25f)) return;
            lastSongTick = now;
            if (RM_SandSwimRemSettings.listeningSingingEnabled && Find.CurrentMap == map)
            {
                RM_StillsandListeningDefOf.RM_DuneSong?.PlayOneShot(new TargetInfo(cell, map));
                songsPlayed++;
            }
            if (!warned && RM_SandSwimRemSettings.listeningWarningEnabled)
            {
                float r = RM_SandSwimRemSettings.singingWarningCells;
                float r2 = r * r;
                List<Building> bs = map.listerBuildings.allBuildingsColonist;
                for (int i = 0; i < bs.Count; i++)
                {
                    if ((bs[i].Position - cell).LengthHorizontalSquared <= r2)
                    {
                        warned = true;
                        Messages.Message("A dune is singing near " + bs[i].LabelShort + ". A slip face that sings is moving.",
                            new LookTargets(new TargetInfo(cell, map)), MessageTypeDefOf.CautionInput, historical: false);
                        break;
                    }
                }
            }
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref warned, "rmSingingWarned", false);
        }
    }

    [DefOf]
    public static class RM_StillsandListeningDefOf
    {
        public static SoundDef RM_SandHiss;
        public static SoundDef RM_SandSaltation;
        public static SoundDef RM_DuneSong;
        public static SoundDef RM_SandSwimRumble;
        public static SoundDef RM_SandSwimBreach;

        static RM_StillsandListeningDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_StillsandListeningDefOf)); }
    }

    // Arms the soft Harmony hooks and gives every sand-swim consumer the Stillsand rumble and breach
    // sounds where its extension names none (so a consumer stays one extension; applies after restart).
    [StaticConstructorOnStartup]
    public static class RM_SandSwimRemainderStartup
    {
        public static bool driftPatched, songPatched;

        static RM_SandSwimRemainderStartup()
        {
            const string rule = "[RimMandrake.Stillsand] sand-swim remainder: ";
            Harmony h = new Harmony("mandrake.rm.stillsand.sandswimrem");
            try
            {
                MethodInfo swim = AccessTools.Method(typeof(RM_SandSwimUtility), "IsSwimTerrain");
                if (swim == null) Log.Warning(rule + "RM_SandSwimUtility.IsSwimTerrain not found; drift depth is not swim ground.");
                else { h.Patch(swim, postfix: new HarmonyMethod(typeof(RM_DriftSwim), "Postfix")); driftPatched = true; }
            }
            catch (Exception e) { Log.Warning(rule + "drift patch failed: " + e.Message); }
            try
            {
                Type field = GenTypes.GetTypeInAnyAssembly("RimMandrake.MovingDunes.MapComponent_DuneField");
                MethodInfo m = field == null ? null : AccessTools.Method(field, "SetDepthHysteretic");
                if (m != null) { h.Patch(m, prefix: new HarmonyMethod(typeof(Patch_SlipFace), "Prefix")); songPatched = true; }
            }
            catch (Exception e) { Log.Warning(rule + "singing-dune hook failed: " + e.Message); }

            if (RM_SandSwimRemSettings.listeningRumbleEnabled)
            {
                foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    RM_SandSwimExtension ext = def.race == null ? null : def.GetModExtension<RM_SandSwimExtension>();
                    if (ext == null) continue;
                    if (ext.rumbleSound == null) ext.rumbleSound = RM_StillsandListeningDefOf.RM_SandSwimRumble;
                    if (ext.breachSound == null) ext.breachSound = RM_StillsandListeningDefOf.RM_SandSwimBreach;
                }
            }
        }
    }

    public static class Patch_SlipFace
    {
        // MapComponent.map is public; __instance typed as the base so Harmony needs no MovingDunes reference.
        public static void Prefix(MapComponent __instance, IntVec3 cell, float target)
        {
            if (!RM_SandSwimRemSettings.listeningSingingEnabled && !RM_SandSwimRemSettings.listeningWarningEnabled) return;
            Map map = __instance.map;
            SandGrid grid = map?.sandGrid;
            if (grid == null || grid.GetDepth(cell) - target < 0.05f) return;
            map.GetComponent<RM_MapComponent_SandListening>()?.NoteSlipFace(cell);
        }
    }
}
