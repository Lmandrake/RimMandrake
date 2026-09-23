using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.CreatureBehaviors
{
    // GREENTIDE_HUMMING_GROVE_1 — a soundscape whose layer count follows what
    // is near the listener, so the mix changes as the player moves.
    //
    // Owner asked whether trees could hum at differing frequencies to make a
    // soundscape that changes as you walk, was told our shipped hum system is
    // camera-attached rather than world-positional, and ruled "It's ok if it
    // were attached to the camera." Then ruled it be built GENERIC, for any
    // biome, because this is the idea's second occurrence in the project.
    //
    // Shape copied from src/RimUtinni/RustCathedralHum/Source/
    // RM_MapComponent_BiomeAttitude.cs (read in full): a plain MapComponent
    // that decides a layer COUNT on an interval and syncs a list of
    // Sustainers spawned with SoundInfo.OnCamera(MaintenanceType.PerTick),
    // ending surplus layers from the tail. The one substantive difference is
    // what drives the count:
    //
    //   Rust Cathedral -> a mood/threat band. The player reads "something
    //                     changed", and its silence is that biome's survival
    //                     tell.
    //   this           -> how many tagged Things are near the listener. The
    //                     player reads "I have moved".
    //
    // 🔴 That distinction is deliberate and the item requires it: two biomes
    // whose signature is a hum going silent would dilute both, and the
    // Greentide already has its own predator hush (RM_MapComponent_SilenceCue)
    // that a second silence-means-danger cue would contradict. ⛔ So nothing
    // here ever drops to zero layers as a warning — zero here only ever means
    // "no tagged Things nearby", which is the ordinary state of most of a map.
    //
    // ⛔ Do NOT migrate the Cathedral's own hum onto this class. That refactor
    // is explicitly not ruled (GREENTIDE_HUMMING_GROVE_1 spec item 4).
    //
    // This assembly ships no SoundDef and no ThingDef: a content mod tags its
    // own def with RM_ProximitySoundscapeExtension and supplies its own
    // sounds. With nothing tagged on a map, ScanGroups finds nothing and this
    // component costs one interval check.
    public class RM_MapComponent_ProximitySoundscape : MapComponent
    {
        private class GroupState
        {
            public List<Sustainer> sustainers = new List<Sustainer>();
            public int layers;
            public int layerThingCount;   // count that justified the current layer total
            public int lastChangeTick = -999999;
        }

        // groupKey -> live mix. Rebuilt from the map on load rather than
        // Scribed: every input (which Things are spawned, where the listener
        // is) is re-derivable, and a Sustainer cannot be saved anyway. This
        // is the DreadField/SenseWeb posture, not LivingRegrowth's — there is
        // no state here that outlives the things producing it.
        private readonly Dictionary<string, GroupState> groups = new Dictionary<string, GroupState>();

        // Shortest checkIntervalTicks among tagged defs actually present, so
        // one component serves groups that want different cadences without
        // scanning every tick. Recomputed whenever a scan runs.
        private int scanIntervalTicks = 60;

        public RM_MapComponent_ProximitySoundscape(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (!RM_CreatureBehaviorsSettings.proximitySoundscapeEnabled)
            {
                if (groups.Count > 0)
                {
                    EndAll();
                }
                return;
            }

            if (!map.IsHashIntervalTick(scanIntervalTicks))
            {
                return;
            }

            if (!TryGetListenerCell(out IntVec3 listener))
            {
                // No listener resolvable (not the current map, no camera yet
                // during load). Silence rather than guess a position.
                if (groups.Count > 0)
                {
                    EndAll();
                }
                return;
            }

            Dictionary<string, KeyValuePair<RM_ProximitySoundscapeExtension, int>> scanned = ScanGroups(listener);

            // Any live group the scan no longer sees has nothing nearby: wind
            // it down through the same hysteresis path rather than cutting it.
            foreach (KeyValuePair<string, GroupState> live in groups)
            {
                if (!scanned.ContainsKey(live.Key))
                {
                    live.Value.layerThingCount = 0;
                }
            }

            foreach (KeyValuePair<string, KeyValuePair<RM_ProximitySoundscapeExtension, int>> entry in scanned)
            {
                Apply(entry.Key, entry.Value.Key, entry.Value.Value);
            }

            // Groups the scan did not see still need their sustainers ended.
            List<string> stale = null;
            foreach (KeyValuePair<string, GroupState> live in groups)
            {
                if (scanned.ContainsKey(live.Key) || live.Value.sustainers.Count == 0)
                {
                    continue;
                }
                (stale ?? (stale = new List<string>())).Add(live.Key);
            }
            if (stale != null)
            {
                for (int i = 0; i < stale.Count; i++)
                {
                    SyncSustainers(groups[stale[i]], null, 0);
                }
            }
        }

        public override void MapRemoved()
        {
            EndAll();
            base.MapRemoved();
        }

        // 🔴 UNVERIFIED — THE ONE CALL IN THIS FILE THAT NEEDS THE DESKTOP.
        //
        // `Find.CameraDriver` itself IS proven live in this repo: our own
        // bridge calls Find.CameraDriver.JumpToCurrentMapLoc(IntVec3) and
        // Find.CameraDriver.shaker.DoShake(...) (JawaBenchMapInfoTools.cs:322,
        // JawaBenchStorytellerTools2.cs:374). So the driver exists and speaks
        // in map cells. What is NOT verified from our own source is the member
        // that READS its current position — and the Mac has no game, no def
        // dump and no decompiler, so ⛔ the member name below must be
        // confirmed against the engine before this ships.
        //
        // It is isolated here on purpose: if the name is wrong, exactly one
        // method needs fixing, and until then a false return makes the whole
        // mechanism silent rather than throwing every interval.
        private bool TryGetListenerCell(out IntVec3 cell)
        {
            cell = IntVec3.Invalid;

            if (Find.CurrentMap != map)
            {
                return false;   // only the map the player is looking at hums
            }

            CameraDriver camera = Find.CameraDriver;
            if (camera == null)
            {
                return false;
            }

            // ❓ CONFIRM ON THE DESKTOP: the accessor for the camera's current
            // map position. Whatever it turns out to be, assign it to `cell`
            // and leave the rest of this method alone.
            cell = camera.MapPosition;

            return cell.IsValid && cell.InBounds(map);
        }

        // groupKey -> (the extension that defined it, how many tagged Things
        // are within that extension's radius of the listener).
        private Dictionary<string, KeyValuePair<RM_ProximitySoundscapeExtension, int>> ScanGroups(IntVec3 listener)
        {
            Dictionary<string, KeyValuePair<RM_ProximitySoundscapeExtension, int>> result =
                new Dictionary<string, KeyValuePair<RM_ProximitySoundscapeExtension, int>>();

            int shortestInterval = int.MaxValue;

            // Buildings and plants both live in this list; a tagged def of any
            // category is picked up without this class knowing what it is.
            List<Thing> all = map.listerThings.AllThings;
            for (int i = 0; i < all.Count; i++)
            {
                Thing t = all[i];
                if (t == null || !t.Spawned)
                {
                    continue;
                }

                RM_ProximitySoundscapeExtension ext =
                    t.def.GetModExtension<RM_ProximitySoundscapeExtension>();
                if (ext == null || ext.groupKey.NullOrEmpty())
                {
                    continue;
                }

                if (ext.checkIntervalTicks < shortestInterval)
                {
                    shortestInterval = ext.checkIntervalTicks;
                }

                if ((t.Position - listener).LengthHorizontalSquared > ext.radius * ext.radius)
                {
                    continue;
                }

                if (result.TryGetValue(ext.groupKey, out KeyValuePair<RM_ProximitySoundscapeExtension, int> got))
                {
                    result[ext.groupKey] =
                        new KeyValuePair<RM_ProximitySoundscapeExtension, int>(got.Key, got.Value + 1);
                }
                else
                {
                    result[ext.groupKey] =
                        new KeyValuePair<RM_ProximitySoundscapeExtension, int>(ext, 1);
                }
            }

            scanIntervalTicks = shortestInterval == int.MaxValue ? 60 : shortestInterval;
            return result;
        }

        private void Apply(string groupKey, RM_ProximitySoundscapeExtension ext, int nearbyCount)
        {
            if (!groups.TryGetValue(groupKey, out GroupState state))
            {
                state = new GroupState();
                groups[groupKey] = state;
            }

            int maxLayers = ext.humLayers.Count;
            int wanted = Mathf.Clamp(nearbyCount / ext.thingsPerLayer, 0, maxLayers);

            // De-escalation-only hysteresis: adding is immediate, dropping
            // waits until the count has fallen clear of what justified the
            // layer we are holding. Same asymmetry as the Cathedral's band.
            if (wanted < state.layers)
            {
                int holdingThreshold = state.layers * ext.thingsPerLayer;
                if (nearbyCount > holdingThreshold - ext.thingsPerLayer - ext.dropHysteresisThings)
                {
                    wanted = state.layers;
                }
            }

            if (wanted == state.layers)
            {
                return;
            }

            // The pop mitigation. A layer change is refused, not queued, so a
            // player pacing a boundary cannot bank changes and get a burst.
            if (Find.TickManager.TicksGame - state.lastChangeTick < ext.minLayerChangeIntervalTicks)
            {
                return;
            }

            state.lastChangeTick = Find.TickManager.TicksGame;
            state.layerThingCount = nearbyCount;
            SyncSustainers(state, ext, wanted);
        }

        private void SyncSustainers(GroupState state, RM_ProximitySoundscapeExtension ext, int desiredLayers)
        {
            while (state.sustainers.Count > desiredLayers)
            {
                Sustainer last = state.sustainers[state.sustainers.Count - 1];
                last?.End();
                state.sustainers.RemoveAt(state.sustainers.Count - 1);
            }

            while (ext != null && state.sustainers.Count < desiredLayers)
            {
                SoundDef layerSound = ext.humLayers[state.sustainers.Count];
                state.sustainers.Add(
                    layerSound?.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick)));
            }

            state.layers = state.sustainers.Count;
        }

        private void EndAll()
        {
            foreach (KeyValuePair<string, GroupState> entry in groups)
            {
                GroupState state = entry.Value;
                for (int i = 0; i < state.sustainers.Count; i++)
                {
                    state.sustainers[i]?.End();
                }
                state.sustainers.Clear();
                state.layers = 0;
            }
            groups.Clear();
        }
    }
}
