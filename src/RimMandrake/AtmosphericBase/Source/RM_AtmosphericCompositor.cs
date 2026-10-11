// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 2 -- the compositor driving ONE mood (spec §2.6 steps 1, 5, 6).
//
// Phase 2 holds at most one mood per map, so nothing is ranked: rank orders two or more claims, and territory between
// two moods is Phase 3 (which is blocked on NINEFOLD_LOUDNESS_FRONT_1 -- rank is read, never computed here). A second
// PushMood REPLACES the first. With no mood pushed and the default switched on, the framework's own gentle scheme
// (RM_Scheme_Lamplight, spec §5) runs on the player's chosen default group.
//
// Every evaluation, for each fixture the player (or a scenario) handed over:
//   * unlit (power off, flicked off): not driven -- L9, no power, no channels;
//   * in the mood's group: palette[PaletteIndex(...)] -- an index into the palette, never a computed colour (L4);
//   * not in the group, or no mood: its own prior glow (the substrate).
// and writes ONLY when that value differs from what the fixture already shows (step 6). The Phase 0 cost read says a
// colour write is a DeRegister/Register on the glow grid, O(lights on the map), so changed-only is the only affordable
// shape at hundreds of fixtures; the counters below are what the end-of-Phase-2 live cost re-measure reads.
// Evaluated from MapComponentUpdate on REAL time (L10): it keeps running while the game is paused.
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_MoodClaim : IExposable
    {
        public string claimant;
        public string group;
        public RM_AtmosphericSchemeDef scheme;
        public float rank;      // carried, supplied by the consumer, not used until two moods exist (Phase 3)

        public void ExposeData()
        {
            Scribe_Values.Look(ref claimant, "claimant");
            Scribe_Values.Look(ref group, "group");
            Scribe_Defs.Look(ref scheme, "scheme");
            Scribe_Values.Look(ref rank, "rank", 0f);
        }

        public override string ToString() => claimant + ":" + scheme?.defName + "@" + group;
    }

    /// <summary>L4 at the write: the only colours that may reach a fixture are members of a loaded scheme's palette.</summary>
    public static class RM_PaletteGuard
    {
        private static HashSet<long> members;
        public static int violations;

        private static long Key(ColorInt c) => ((long)c.r << 48) ^ ((long)(c.g & 0xFFFF) << 32) ^ ((long)(c.b & 0xFFFF) << 16) ^ (c.a & 0xFFFF);

        public static bool IsMember(ColorInt c)
        {
            if (members == null)
            {
                var m = new HashSet<long>();
                foreach (RM_AtmosphericSchemeDef d in DefDatabase<RM_AtmosphericSchemeDef>.AllDefsListForReading)
                    if (d.Valid)
                        foreach (ColorInt p in d.palette) m.Add(Key(p));
                members = m;
            }
            return members.Contains(Key(c));
        }

        public static int MemberCount => members?.Count ?? 0;
    }

    public class RM_Compositor
    {
        public const string DefaultClaimant = "atmosphericbase.default";
        public const string DefaultSchemeDefName = "RM_Scheme_Lamplight";
        private const int EvalEveryFrames = 6;
        private const int MembershipEveryFrames = 60;

        private readonly RM_ChangeTracker tracker = new RM_ChangeTracker();
        private readonly Dictionary<int, RM_SchemeKernel.RM_Place> place = new Dictionary<int, RM_SchemeKernel.RM_Place>();
        private readonly Dictionary<int, int> roomOf = new Dictionary<int, int>();
        private HashSet<int> flashers = new HashSet<int>();
        private string flasherKey;
        private int lastEvalFrame = -9999, lastMembershipFrame = -9999;

        // ---- counters (the cost re-measure, and the proof)
        public long evaluations, fixtureEvaluations, writes, skippedUnchanged, skippedUnlit;
        public int lastEvalWrites, maxEvalWrites;

        public void Forget(Thing t)
        {
            if (t == null) return;
            tracker.Forget(t.thingIDNumber);
            place.Remove(t.thingIDNumber);
            roomOf.Remove(t.thingIDNumber);
        }

        public void ResetCounters()
        {
            evaluations = fixtureEvaluations = writes = skippedUnchanged = skippedUnlit = 0;
            lastEvalWrites = maxEvalWrites = 0;
        }

        public bool Shows(Thing t, out long value) => tracker.Shows(t.thingIDNumber, out value);

        public static RM_MoodClaim DefaultMood()
        {
            RM_AtmosphericBaseSettings s = RM_AtmosphericBaseSettings.Cur;
            if (!s.defaultMood) return null;
            RM_AtmosphericSchemeDef d = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(DefaultSchemeDefName);
            if (d == null || !d.Valid) return null;
            int gi = s.defaultMoodGroup;
            if (gi < 0 || gi >= RM_SchemeKernel.DefaultGroups.Length) gi = 0;
            return new RM_MoodClaim { claimant = DefaultClaimant, group = RM_SchemeKernel.DefaultGroups[gi], scheme = d };
        }

        private void RefreshMembership(RM_MapComponent_AtmosphericBase comp)
        {
            foreach (Thing t in comp.TakenThings)
            {
                if (t == null || !t.Spawned) continue;
                Room room = t.GetRoom();
                place[t.thingIDNumber] = RM_SchemeKernel.PlaceOf(room != null, room != null && room.PsychologicallyOutdoors,
                                                                  room?.Role?.defName);
                roomOf[t.thingIDNumber] = room?.ID ?? -1;
            }
        }

        public bool InGroup(RM_MapComponent_AtmosphericBase comp, Thing t, string group)
        {
            HashSet<Thing> reg = comp.RegisteredGroup(group);
            if (reg != null) return reg.Contains(t);
            return place.TryGetValue(t.thingIDNumber, out RM_SchemeKernel.RM_Place p) && RM_SchemeKernel.InDefaultGroup(group, p);
        }

        /// <summary>Called every frame; evaluates every EvalEveryFrames frames on real time.</summary>
        public void Update(RM_MapComponent_AtmosphericBase comp)
        {
            int f = UnityEngine.Time.frameCount;
            if (f - lastEvalFrame < EvalEveryFrames) return;
            lastEvalFrame = f;
            if (f - lastMembershipFrame >= MembershipEveryFrames)
            {
                lastMembershipFrame = f;
                RefreshMembership(comp);
            }
            Evaluate(comp, UnityEngine.Time.realtimeSinceStartup);
        }

        /// <summary>One evaluation at an explicit time (the proof calls this directly). Returns the writes it made.</summary>
        public int Evaluate(RM_MapComponent_AtmosphericBase comp, double time, bool refreshMembership = false)
        {
            if (refreshMembership) RefreshMembership(comp);
            RM_MoodClaim mood = RM_AtmosphericBaseSettings.Cur.compositor ? comp.EffectiveMood : null;
            RM_SchemeData data = default(RM_SchemeData);
            bool live = mood?.scheme != null && mood.scheme.Valid;
            if (live) data = mood.scheme.Data;
            if (live && data.flasherCount > 0)
            {
                string key = mood + "#" + comp.TakenCount;
                if (key != flasherKey)
                {
                    var ids = new List<int>();
                    foreach (Thing t in comp.TakenThings)
                        if (t != null && t.Spawned && InGroup(comp, t, mood.group)) ids.Add(t.thingIDNumber);
                    flashers = RM_SchemeKernel.PickFlashers(ids, data.flasherCount);
                    flasherKey = key;
                }
            }
            int n = 0;
            evaluations++;
            foreach (Thing t in comp.TakenThings)
            {
                if (t == null || !t.Spawned) continue;
                CompGlower g = RM_EmitterDiscovery.GlowerOf(t);
                if (g == null) continue;
                fixtureEvaluations++;
                if (!g.Glows) { skippedUnlit++; continue; }
                int id = t.thingIDNumber;
                bool inGroup = live && InGroup(comp, t, mood.group);
                if (inGroup)
                {
                    int room = roomOf.TryGetValue(id, out int r) ? r : -1;
                    int idx = RM_SchemeKernel.PaletteIndex(data, id, room, time, flashers.Contains(id));
                    if (!tracker.Want(id, RM_ChangeTracker.Pack(mood.scheme.shortHash, idx))) { skippedUnchanged++; continue; }
                    if (comp.Drive(t, mood.scheme.palette[idx])) n++;
                    else tracker.Forget(id);   // refused (palette guard / channel off): it does not show this
                }
                else
                {
                    if (!tracker.Want(id, RM_ChangeTracker.Substrate)) { skippedUnchanged++; continue; }
                    RM_GlowAccess.Restore(g, comp.PriorOf(t));
                    n++;
                }
            }
            writes += n;
            lastEvalWrites = n;
            if (n > maxEvalWrites) maxEvalWrites = n;
            return n;
        }
    }
}
