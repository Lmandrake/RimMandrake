// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phases 2-4 -- the compositor (spec §2.6 steps 1, 2, 3, 5, 6).
//
// Moods are held one per claimant and ORDERED by the rank each consumer supplied (rank is read, never computed here --
// NINEFOLD_LOUDNESS_FRONT_1 is the supplier that does not exist yet; until it does, a consumer passes its own number).
//   * the loudest mood, and (Phase 3, setting `territory`) the second-loudest, take TERRITORY over the union of their
//     two groups: RM_TerritoryKernel.Allocate gives every fixture of the union to exactly one of them, along a front
//     that turns on its own slow clock (L5: allocation, never colour-mixing);
//   * moods ranked third and below (second and below with territory off) (Phase 4, setting `tremor`), at most three (L6), are TREMOR: RM_TremorKernel.Assign
//     makes a few scattered fixtures of each one's group flicker briefly in that mood's OWN palette, never more than
//     tremorMaxFraction of the driven fixtures at once, so it can never be mistaken for territory;
//   * with nothing pushed and the default switched on, the framework's own gentle scheme (RM_Scheme_Lamplight, spec §5)
//     is the only mood -- one mood never reaches territory or tremor, so the shipped look is Phase 2's, unchanged.
// Every evaluation, for each fixture the player (or a scenario) handed over:
//   * unlit (power off, flicked off): not driven -- L9, no power, no channels;
//   * flickering for a tremor contributor: that contributor's palette[index];
//   * held by a territory claimant: palette[PaletteIndex(...)] of THAT claimant's scheme -- an index, never a colour (L4);
//   * otherwise: its own prior glow (the substrate).
// and writes ONLY when that value differs from what the fixture already shows (step 6). The Phase 0 cost read says a
// colour write is a DeRegister/Register on the glow grid, O(lights on the map), so changed-only is the only affordable
// shape at hundreds of fixtures; the counters below are what the live cost re-measure reads. The territory allocation
// is recomputed only when the boundary's clock steps or the union changes.
// Evaluated from MapComponentUpdate on REAL time (L10): it keeps running while the game is paused.
// RELOAD (owner decision §9.10, 2026-10-23): the pattern restarts gently from its start. The clock is real time since
// this compositor's first evaluation (`clockOrigin`, never saved); the compositor is built fresh with its map component
// on every load, and it saves no phase, gesture or tracker state, so nothing resumes mid-gesture. What IS saved is
// ownership (which fixture is held, its take-over snapshot, what was last left on it) and the pushed moods.
// Before anything is written, a held lamp whose colour someone else changed is released with that colour kept (§9.9,
// RM_MapComponent_AtmosphericBase.ReleaseExternallyEdited).
using System;
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
        public float rank;      // supplied by the consumer and only ORDERED here (§2.5): loudest first

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
        private readonly Dictionary<string, HashSet<int>> flashersOf = new Dictionary<string, HashSet<int>>();
        private readonly Dictionary<string, string> flasherKeyOf = new Dictionary<string, string>();
        private readonly Dictionary<int, bool> leadOf = new Dictionary<int, bool>();
        private string allocKey;
        // M3 SCAR: fixture -> (the claimant that held it before the flip, pattern clock at the flip). Not saved (§9.10).
        // Bounded by the taken fixtures (Forget, and a pass with one mood, clear it; an expired entry is dropped on read).
        private readonly Dictionary<int, KeyValuePair<string, double>> scarOf = new Dictionary<int, KeyValuePair<string, double>>();
        private string prevLead, prevSecond;   // the claimants the last allocation was made for (leadOf reads against them)
        // M4 HUSH: room id -> (start on the pattern clock, settle, hold). Not saved.
        private readonly Dictionary<int, RM_HushRequest> hushOf = new Dictionary<int, RM_HushRequest>();
        private double lastTime;
        public long scarShows, hushShows;

        private struct RM_HushRequest { public double start; public float settle, hold; }

        /// <summary>M4: hush one room from the next evaluation (RM_AtmosphericBaseAPI.Hush).</summary>
        public bool Hush(int roomId, float settle, float hold)
        {
            if (roomId < 0 || !(settle > 0f) || hold < 0f) return false;
            // a second witness while the room is rising or holding extends the hold; it must not snap the room back to 0
            if (hushOf.TryGetValue(roomId, out RM_HushRequest old))
            {
                double since = lastTime - old.start;
                if (since >= 0 && since < old.settle + old.hold)
                {
                    old.hold = (float)Math.Max(old.hold, since - old.settle + hold);
                    hushOf[roomId] = old;
                    return true;
                }
            }
            hushOf[roomId] = new RM_HushRequest { start = lastTime, settle = settle, hold = hold };
            return true;
        }
        private int lastEvalFrame = -9999, lastMembershipFrame = -9999;
        private double clockOrigin = -1;   // §9.10: the pattern's t = 0 is this compositor's first evaluation. Not saved.

        /// <summary>Seconds into the pattern on this load (0 at the first evaluation after a load or a new game).</summary>
        public double PatternClock(double realtime)
        {
            if (clockOrigin < 0) clockOrigin = realtime;
            return realtime - clockOrigin;
        }

        // ---- counters (the cost re-measure, and the proof)
        public long evaluations, fixtureEvaluations, writes, skippedUnchanged, skippedUnlit;
        public int lastEvalWrites, maxEvalWrites;
        public long allocations, territoryFlips, tremorWrites;   // Phase 3-4
        public long tideAllocations;                                 // allocations that ran as a TIDE (RM_TerritoryShapes)
        public string lastPlan;                                      // the last territory plan, for the proof readout
        public int lastTremorCount, maxTremorCount, lastTremorContributors, lastUnionCount, lastDrivenCount;

        /// <summary>Which of the two territory claimants holds this fixture after the last evaluation: 0 the loudest,
        /// 1 the second, -1 neither (outside the union, or one mood only).</summary>
        public int TerritoryOwner(Thing t) => t != null && leadOf.TryGetValue(t.thingIDNumber, out bool l) ? (l ? 0 : 1) : -1;

        private Dictionary<int, KeyValuePair<int, int>> lastTremor = new Dictionary<int, KeyValuePair<int, int>>();

        /// <summary>Which tremor contributor (0 = the third-loudest mood) made this fixture flicker at the last
        /// evaluation, or -1.</summary>
        public int TremorContributor(Thing t) => t != null && lastTremor.TryGetValue(t.thingIDNumber, out KeyValuePair<int, int> v) ? v.Key : -1;

        public void Forget(Thing t)
        {
            if (t == null) return;
            tracker.Forget(t.thingIDNumber);
            place.Remove(t.thingIDNumber);
            roomOf.Remove(t.thingIDNumber);
            leadOf.Remove(t.thingIDNumber);
            scarOf.Remove(t.thingIDNumber);
            allocKey = null;
        }

        public void ResetCounters()
        {
            evaluations = fixtureEvaluations = writes = skippedUnchanged = skippedUnlit = 0;
            lastEvalWrites = maxEvalWrites = 0;
            allocations = territoryFlips = tremorWrites = tideAllocations = 0;
            lastTremorCount = maxTremorCount = lastTremorContributors = lastUnionCount = lastDrivenCount = 0;
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
            RefreshGraph(comp);
        }

        // ---- step 4: the graph substrate (RM_PatternGraph). Rebuilt from the rooms every membership pass, but the old
        // instance -- with its cached anchor fields -- is kept unless the topology key moved (a wall or door edit), and the
        // fixture set is kept unless membership moved.
        private const int GraphRoomCap = 400;
        public RM_RoomGraph Graph { get; private set; }
        public RM_FixtureSet Fixtures { get; private set; }
        public long graphRebuilds, fixtureSetRebuilds;

        /// <summary>Rooms that share a district border with r (RimWorld keeps adjacency on District, not Room).</summary>
        private static IEnumerable<Room> NeighborRooms(Room r)
        {
            foreach (District d in r.Districts)
                foreach (District nd in d.Neighbors)
                {
                    Room n = nd?.Room;
                    if (n != null && n != r) yield return n;
                }
        }

        private static bool Interior(Room r) => r != null && !r.IsDoorway && !r.PsychologicallyOutdoors && !r.IsHuge;

        private void RefreshGraph(RM_MapComponent_AtmosphericBase comp)
        {
            var seen = new HashSet<int>();
            var queue = new Queue<Room>();
            var rooms = new List<RM_RoomFacts>();
            var doors = new List<KeyValuePair<int, int>>();
            var ems = new List<int>(); var nodes = new List<int>(); var xs = new List<float>(); var zs = new List<float>();
            foreach (Thing t in comp.TakenThings)
            {
                if (t == null || !t.Spawned) continue;
                Room r = t.GetRoom();
                ems.Add(t.thingIDNumber); nodes.Add(Interior(r) ? r.ID : -1);
                xs.Add(t.Position.x); zs.Add(t.Position.z);
                if (Interior(r) && seen.Add(r.ID)) queue.Enqueue(r);
            }
            // the base = every interior room reachable through doors from a room holding a taken fixture
            while (queue.Count > 0 && rooms.Count < GraphRoomCap)
            {
                Room r = queue.Dequeue();
                bool threshold = false;
                foreach (Room n in NeighborRooms(r))
                {
                    if (n == null) continue;
                    if (n.IsDoorway)
                    {
                        foreach (Room m in NeighborRooms(n))
                        {
                            if (m == null || m == r) continue;
                            if (!Interior(m)) { threshold = true; continue; }
                            doors.Add(new KeyValuePair<int, int>(r.ID, m.ID));
                            if (seen.Add(m.ID)) queue.Enqueue(m);
                        }
                    }
                    else if (!Interior(n)) threshold = true;
                    else { doors.Add(new KeyValuePair<int, int>(r.ID, n.ID)); if (seen.Add(n.ID)) queue.Enqueue(n); }
                }
                rooms.Add(new RM_RoomFacts { id = r.ID, cells = r.CellCount, threshold = threshold, shrine = Shrine(r), power = PowerRoom(r) });
            }
            // the keep-or-replace rule lives in the kernel (RM_GraphCache), where the selftest drives it
            RM_GraphRefresh rr = RM_GraphCache.Refresh(Graph, Fixtures, rooms, doors, ems, nodes, xs, zs);
            Graph = rr.graph; Fixtures = rr.fixtures;
            if (rr.graphRebuilt) graphRebuilds++;
            if (rr.fixturesRebuilt) fixtureSetRebuilds++;
        }

        /// <summary>The shrine anchor: a room whose role is Ideology's WorshipRoom (Data/Ideology/Defs/Rooms/RoomRoles.xml).
        /// No such room: the kernel's Shrine anchor falls back to Core.</summary>
        private static bool Shrine(Room r) => r.Role != null && r.Role.defName == "WorshipRoom";

        /// <summary>The power anchor: a room holding a generator or a battery (CompPowerPlant / CompPowerBattery). Read
        /// on a graph refresh only, never per tick.</summary>
        private static bool PowerRoom(Room r)
        {
            foreach (Thing t in r.ContainedAndAdjacentThings)
                if ((t.TryGetComp<CompPowerPlant>() != null || t.TryGetComp<CompPowerBattery>() != null) && t.GetRoom() == r) return true;
            return false;
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
            Evaluate(comp, PatternClock(UnityEngine.Time.realtimeSinceStartup));
        }

        private HashSet<int> FlashersFor(RM_MapComponent_AtmosphericBase comp, RM_MoodClaim m, RM_SchemeData data)
        {
            if (data.flasherCount <= 0) return null;
            string key = m + "#" + comp.TakenCount;
            if (flasherKeyOf.TryGetValue(m.claimant, out string k) && k == key) return flashersOf[m.claimant];
            var ids = new List<int>();
            foreach (Thing t in comp.TakenThings)
                if (t != null && t.Spawned && InGroup(comp, t, m.group)) ids.Add(t.thingIDNumber);
            HashSet<int> set = RM_SchemeKernel.PickFlashers(ids, data.flasherCount);
            flashersOf[m.claimant] = set;
            flasherKeyOf[m.claimant] = key;
            return set;
        }

        private int Show(RM_MapComponent_AtmosphericBase comp, Thing t, RM_AtmosphericSchemeDef scheme, int idx)
        {
            int id = t.thingIDNumber;
            if (!tracker.Want(id, RM_ChangeTracker.Pack(scheme.shortHash, idx))) { skippedUnchanged++; return 0; }
            if (comp.Drive(t, scheme.palette[idx])) return 1;
            tracker.Forget(id);   // refused (palette guard / channel off): it does not show this
            return 0;
        }

        /// <summary>One evaluation at an explicit time (the proof calls this directly). Returns the writes it made.</summary>
        public int Evaluate(RM_MapComponent_AtmosphericBase comp, double time, bool refreshMembership = false)
        {
            comp.ReleaseExternallyEdited();   // §9.9: before anything is written
            if (refreshMembership) RefreshMembership(comp);
            RM_AtmosphericBaseSettings set = RM_AtmosphericBaseSettings.Cur;
            lastTime = time;
            List<RM_MoodClaim> ranked = set.compositor ? comp.RankedMoods() : new List<RM_MoodClaim>();
            RM_MoodClaim lead = ranked.Count > 0 ? ranked[0] : null;
            RM_MoodClaim second = set.territory && ranked.Count > 1 ? ranked[1] : null;
            RM_SchemeData leadData = lead != null ? lead.scheme.Data : default(RM_SchemeData);
            RM_SchemeData secondData = second != null ? second.scheme.Data : default(RM_SchemeData);
            HashSet<int> leadFlash = lead != null ? FlashersFor(comp, lead, leadData) : null;
            HashSet<int> secondFlash = second != null ? FlashersFor(comp, second, secondData) : null;
            evaluations++;

            // the fixtures that can be driven now (L9: an unlit fixture carries no channel)
            var driven = new List<Thing>();
            foreach (Thing t in comp.TakenThings)
            {
                if (t == null || !t.Spawned) continue;
                CompGlower g = RM_EmitterDiscovery.GlowerOf(t);
                if (g == null) continue;
                fixtureEvaluations++;
                if (!g.Glows) { skippedUnlit++; continue; }
                driven.Add(t);
            }
            lastDrivenCount = driven.Count;

            // Phase 3: territory over the union of the two groups (step 2)
            var union = new List<Thing>();
            if (second != null)
                foreach (Thing t in driven)
                    if (InGroup(comp, t, lead.group) || InGroup(comp, t, second.group)) union.Add(t);
            lastUnionCount = union.Count;
            if (second == null) { if (leadOf.Count > 0) leadOf.Clear(); scarOf.Clear(); allocKey = null; prevLead = prevSecond = null; lastPlan = null; }
            else
            {
                RM_TerritoryTuning tt = set.TerritoryTuning;
                long step = RM_TerritoryKernel.ClockStep(time, tt.periodSeconds);
                // the shape (Kernel/RM_TerritoryShapes.cs): a canon pairing of the two signatures, else the leader's own
                RM_SignatureDef leadSig = RM_SignatureDef.ForScheme(lead.scheme), otherSig = RM_SignatureDef.ForScheme(second.scheme);
                RM_TerritoryPlan plan = RM_TerritoryShapes.Plan(leadSig?.defName, leadSig?.territory?.Shape ?? RM_TerritoryShape.Wedge,
                                                                otherSig?.defName, RM_SignatureDef.Rules);
                float floor = otherSig?.territory?.minShare ?? 0f;
                if (floor > 0f) tt.leadShare = System.Math.Min(tt.leadShare, 1f - floor);
                lastPlan = plan.ToString();
                uint uh = 2166136261U;
                foreach (Thing t in union) uh = RM_SchemeKernel.Mix(uh ^ (uint)t.thingIDNumber);
                string key = lead.claimant + "|" + second.claimant + "|" + step + "|" + union.Count + "|" + uh + "|" + tt.leadShare + "|" + tt.ragged
                             + "|" + lastPlan + "|" + (Graph?.TopologyKey ?? 0UL);
                if (key != allocKey)
                {
                    var ids = new List<int>(union.Count);
                    var xs = new List<float>(union.Count);
                    var zs = new List<float>(union.Count);
                    var nodes = new List<int>(union.Count);
                    foreach (Thing t in union)
                    {
                        ids.Add(t.thingIDNumber); xs.Add(t.Position.x); zs.Add(t.Position.z);
                        int slot = Fixtures != null ? Fixtures.Slot(t.thingIDNumber) : -1;
                        nodes.Add(slot >= 0 && Graph != null ? Graph.Node(Fixtures.room[slot]) : -1);
                    }
                    bool[] got = RM_TerritoryShapes.Allocate(ids, xs, zs, nodes, Graph, step, RM_TerritoryKernel.PairSalt(lead.claimant, second.claimant), tt, plan);
                    if (RM_TerritoryShapes.RunsAsTide(plan, nodes, Graph)) tideAllocations++;
                    var next = new Dictionary<int, bool>(ids.Count);
                    for (int i = 0; i < ids.Count; i++)
                    {
                        next[ids[i]] = got[i];
                        // read the old bool against the claimants it was made for, so a re-ranked pair still scars
                        if (leadOf.TryGetValue(ids[i], out bool was))
                        {
                            string before = was ? prevLead : prevSecond, after = got[i] ? lead.claimant : second.claimant;
                            if (before != after)
                            {
                                territoryFlips++;
                                scarOf[ids[i]] = new KeyValuePair<string, double>(before, time);
                            }
                        }
                    }
                    leadOf.Clear();
                    foreach (KeyValuePair<int, bool> kv in next) leadOf[kv.Key] = kv.Value;
                    allocKey = key;
                    prevLead = lead.claimant; prevSecond = second.claimant;
                    allocations++;
                }
            }

            // Phase 4: tremor from the moods ranked third and below (step 3), each in its own palette
            Dictionary<int, KeyValuePair<int, int>> tremorAt = null;
            var tremorMoods = new List<RM_MoodClaim>();
            if (set.tremor && lead != null)
            {
                RM_TremorTuning tu = set.TremorTuning;
                var sources = new List<RM_TremorSource>();
                for (int i = second != null ? 2 : 1; i < ranked.Count && tremorMoods.Count < tu.cap; i++)
                {
                    RM_MoodClaim m = ranked[i];
                    var members = new List<int>();
                    foreach (Thing t in driven) if (InGroup(comp, t, m.group)) members.Add(t.thingIDNumber);
                    tremorMoods.Add(m);
                    sources.Add(new RM_TremorSource { paletteCount = m.scheme.palette.Count, salt = RM_TerritoryKernel.PairSalt(m.claimant, "tremor"), members = members });
                }
                if (sources.Count > 0) tremorAt = RM_TremorKernel.Assign(sources, time, driven.Count, tu);
            }
            lastTremor = tremorAt ?? new Dictionary<int, KeyValuePair<int, int>>();
            lastTremorContributors = tremorMoods.Count;
            lastTremorCount = tremorAt?.Count ?? 0;
            if (lastTremorCount > maxTremorCount) maxTremorCount = lastTremorCount;

            // M4: the one lamp per hushed room that keeps the ember in a dark hush (its lowest-id driven fixture that a mood owns)
            Dictionary<int, int> keepers = null;
            if (hushOf.Count > 0)
            {
                var kIds = new List<int>(); var kRooms = new List<int>(); var kOwned = new List<bool>(); var kTremor = new List<bool>();
                foreach (Thing t in driven)
                {
                    int id0 = t.thingIDNumber;
                    kIds.Add(id0);
                    kRooms.Add(roomOf.TryGetValue(id0, out int rr) ? rr : -1);
                    kTremor.Add(tremorAt != null && tremorAt.ContainsKey(id0));
                    kOwned.Add((second != null && leadOf.ContainsKey(id0)) || (lead != null && InGroup(comp, t, lead.group)));
                }
                keepers = RM_Hush.PickKeepers(kIds, kRooms, kOwned, kTremor, hushOf.Keys);
            }

            // steps 5-6: one quantised value per fixture, written only on change
            int n = 0;
            foreach (Thing t in driven)
            {
                int id = t.thingIDNumber;
                int room = roomOf.TryGetValue(id, out int r) ? r : -1;
                if (tremorAt != null && tremorAt.TryGetValue(id, out KeyValuePair<int, int> tr))
                {
                    int w = Show(comp, t, tremorMoods[tr.Key].scheme, tr.Value);
                    n += w; tremorWrites += w;
                    continue;
                }
                RM_MoodClaim owner = null;
                RM_SchemeData data = default(RM_SchemeData);
                HashSet<int> flash = null;
                if (second != null && leadOf.TryGetValue(id, out bool isLead))
                {
                    owner = isLead ? lead : second; data = isLead ? leadData : secondData; flash = isLead ? leadFlash : secondFlash;
                }
                else if (lead != null && InGroup(comp, t, lead.group))
                {
                    owner = lead; data = leadData; flash = leadFlash;
                }
                if (owner != null)
                {
                    RM_PatternCtx pc = RM_PatternCtx.Of(id, room, Graph, Fixtures);
                    int idx = RM_SchemeKernel.PaletteIndex(data, ref pc, time, flash != null && flash.Contains(id));
                    RM_AtmosphericSchemeDef shown = owner.scheme;
                    // M3 SCAR: the winner's lowest moments still show the previous owner, for the winner's linger
                    if (second != null && scarOf.TryGetValue(id, out KeyValuePair<string, double> sc))
                    {
                        RM_Scar.Action act = RM_Scar.Decide(sc.Key, lead.claimant, second.claimant, idx, time - sc.Value, data.scarLinger, data.scarKeeps);
                        if (act == RM_Scar.Action.Drop) scarOf.Remove(id);
                        else if (act != RM_Scar.Action.None)
                        {
                            bool prevWasLead = act == RM_Scar.Action.ShowLead;
                            RM_SchemeData pd = prevWasLead ? leadData : secondData;
                            HashSet<int> pf = prevWasLead ? leadFlash : secondFlash;
                            idx = RM_SchemeKernel.PaletteIndex(pd, ref pc, time, pf != null && pf.Contains(id));
                            shown = prevWasLead ? lead.scheme : second.scheme;
                            data = pd;
                            scarShows++;
                        }
                    }
                    // M4 HUSH: one room narrows to its held entry, then recovers
                    if (room >= 0 && hushOf.TryGetValue(room, out RM_HushRequest h))
                    {
                        double w = RM_Hush.Weight(time - h.start, h.settle, h.hold);
                        int held = RM_Hush.Mid(data);
                        bool dark = held != (data.Count - 1) / 2;   // the middle is black: hold the ember on one lamp
                        idx = RM_Hush.Apply(idx, held, w, dark, keepers != null && keepers.TryGetValue(room, out int kp) && kp == id);
                        if (w > 0) hushShows++;
                    }
                    n += Show(comp, t, shown, idx);
                }
                else
                {
                    if (!tracker.Want(id, RM_ChangeTracker.Substrate)) { skippedUnchanged++; continue; }
                    if (comp.ShowSubstrate(t)) n++;
                    else tracker.Forget(id);
                }
            }
            if (hushOf.Count > 0)
            {
                var done = new List<int>();
                foreach (KeyValuePair<int, RM_HushRequest> kv in hushOf)
                    if (RM_Hush.Over(time - kv.Value.start, kv.Value.settle, kv.Value.hold)) done.Add(kv.Key);
                foreach (int r in done) hushOf.Remove(r);
            }
            writes += n;
            lastEvalWrites = n;
            if (n > maxEvalWrites) maxEvalWrites = n;
            return n;
        }
    }
}
