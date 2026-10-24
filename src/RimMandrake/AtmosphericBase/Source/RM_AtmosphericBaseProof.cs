// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phases 1-4 -- live proof hooks for validation.py (jawa/static_call).
// ProofTakeover runs the SHIPPED take-over on the current map and leaves it as it found it: settings restored in
// finally, the test fixture released, the scenario flag put back. Answers one line of key=value; "-" where the map has
// nothing to test on (no eligible fixture, no excluded glower of a kind), which the suite reads as UNMEASURED.
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public static class RM_AtmosphericBaseProof
    {
        private static string B(bool v) => v ? "True" : "False";
        // Drive refuses any colour outside a loaded scheme's palette (L4, Phase 2), so the test colour is a palette
        // member: the default scheme's entry that differs from what the fixture shows now.
        private static ColorInt TestColorFor(CompGlower g)
        {
            RM_AtmosphericSchemeDef d = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
            if (d != null)
                foreach (ColorInt c in d.palette)
                    if (c != g.GlowColor) return c;
            return new ColorInt(23, 201, 117, 0);
        }

        private static IEnumerable<Thing> ExcludedGlowers(Map map)
        {
            foreach (Thing t in map.listerThings.AllThings)
                if (RM_EmitterDiscovery.GlowerOf(t) != null && RM_AtmosphericKernel.IsHardExclusion(RM_EmitterDiscovery.Classify(t)))
                    yield return t;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (RM_EmitterDiscovery.GlowerOf(p) != null) yield return p;
                if (p.apparel != null)
                    foreach (Apparel a in p.apparel.WornApparel)
                        if (RM_EmitterDiscovery.GlowerOf(a) != null) yield return a;
                if (p.equipment != null)
                    foreach (ThingWithComps e in p.equipment.AllEquipmentListForReading)
                        if (RM_EmitterDiscovery.GlowerOf(e) != null) yield return e;
            }
        }

        public static string ProofTakeover(string args)
        {
            RM_AtmosphericBaseSettings cur = RM_AtmosphericBaseSettings.Cur;
            bool wasLight = cur.lightChannel, wasButton = cur.playerTakeoverButton;
            Map map = Find.CurrentMap;
            RM_MapComponent_AtmosphericBase comp = RM_MapComponent_AtmosphericBase.For(map);
            bool wasScenario = comp != null && comp.scenarioDecides;
            Thing a = null;
            try
            {
                string s = "bound=" + B(RM_GlowAccess.Bound);
                if (map == null || comp == null) return s + " map=-";
                List<Designator> rev = Find.ReverseDesignatorDatabase.AllDesignators;
                var take = rev.OfType<RM_Designator_TakeOverGlow>().FirstOrDefault();
                var rel = rev.OfType<RM_Designator_ReleaseGlow>().FirstOrDefault();
                s += " buttons_registered=" + B(take != null && rel != null);
                s += " taken_before=" + comp.TakenCount;

                // --- the hard exclusion list: nothing of these kinds is ever accepted
                List<Thing> excluded = ExcludedGlowers(map).Distinct().ToList();
                int accepted = excluded.Count(t => comp.TakeOverRefusal(t) == null || (take != null && take.CanDesignateThing(t).Accepted));
                s += " excluded_glowers=" + excluded.Count + " excluded_accepted=" + accepted;
                foreach (RM_EmitterVerdict v in new[] { RM_EmitterVerdict.ExcludedPawn, RM_EmitterVerdict.ExcludedPlant,
                                                        RM_EmitterVerdict.ExcludedWornOrEquipment, RM_EmitterVerdict.ExcludedHologram })
                    s += " " + v + "=" + excluded.Count(t => RM_EmitterDiscovery.Classify(t) == v);

                List<Building> eligible = RM_EmitterDiscovery.EligibleOn(map).Where(b => !comp.IsTaken(b)).ToList();
                s += " eligible=" + eligible.Count;
                if (eligible.Count == 0 || take == null || rel == null)
                    return s + " take=- drive=- restored=- neighbour=- channel_off=- scenario_hides=- button_off_hides=-";
                a = eligible[0];
                Thing nb = eligible.Count > 1 ? eligible[1] : null;
                CompGlower ga = RM_EmitterDiscovery.GlowerOf(a);
                RM_GlowSnapshot before = RM_GlowAccess.Snapshot(ga);
                ColorInt effBefore = ga.GlowColor;
                float radBefore = ga.GlowRadius;
                ColorInt TestColor = TestColorFor(ga);
                RM_GlowSnapshot nbBefore = nb != null ? RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(nb)) : null;

                // --- switches hide / refuse (each restored before the next)
                cur.lightChannel = true; cur.playerTakeoverButton = true; comp.scenarioDecides = false;
                bool offered = take.CanDesignateThing(a).Accepted;
                comp.scenarioDecides = true;
                bool scenarioHides = !take.CanDesignateThing(a).Accepted;
                comp.scenarioDecides = false;
                cur.playerTakeoverButton = false;
                bool buttonOffHides = !take.CanDesignateThing(a).Accepted;
                cur.playerTakeoverButton = true;
                cur.lightChannel = false;
                bool channelOffRefuses = !comp.TakeOver(a) && !comp.IsTaken(a);
                cur.lightChannel = true;
                s += " offered=" + B(offered) + " scenario_hides=" + B(scenarioHides) + " button_off_hides=" + B(buttonOffHides)
                   + " channel_off=" + B(channelOffRefuses);

                // --- take, drive, release
                take.DesignateThing(a);
                bool took = comp.IsTaken(a) && comp.PriorOf(a).SameAs(before);
                bool relOffered = rel.CanDesignateThing(a).Accepted;
                bool drove = comp.Drive(a, TestColor) && ga.GlowColor == TestColor;
                bool nbUntouched = nb == null || RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(nb)).SameAs(nbBefore);
                rel.DesignateThing(a);
                bool released = !comp.IsTaken(a);
                RM_GlowSnapshot after = RM_GlowAccess.Snapshot(ga);
                bool exact = after.SameAs(before) && ga.GlowColor == effBefore && ga.GlowRadius == radBefore;
                bool driveAfterRefused = !comp.Drive(a, TestColor) && ga.GlowColor == effBefore;
                a = null;
                s += " take=" + B(took) + " release_offered=" + B(relOffered) + " drive=" + B(drove)
                   + " neighbour=" + (nb == null ? "-" : B(nbUntouched)) + " released=" + B(released)
                   + " restored=" + B(exact) + " drive_after_release_refused=" + B(driveAfterRefused)
                   + " before=[" + before.ToString().Replace(' ', ',') + "] after=[" + after.ToString().Replace(' ', ',') + "]";

                // --- channel off releases what is held, at the next update. Only on a map where nothing else is held:
                // the update releases EVERYTHING, and a proof must not hand the player's own choices back.
                if (comp.TakenCount != 0) return s + " channel_off_releases=-";
                cur.lightChannel = true;
                a = eligible[0];
                comp.TakeOver(a);
                comp.Drive(a, TestColor);
                cur.lightChannel = false;
                comp.MapComponentUpdate();
                bool offReleased = !comp.IsTaken(a) && RM_GlowAccess.Snapshot(ga).SameAs(before);
                if (offReleased) a = null;
                s += " channel_off_releases=" + B(offReleased);
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                cur.lightChannel = true;
                if (a != null && comp != null) comp.Release(a);
                cur.lightChannel = wasLight;
                cur.playerTakeoverButton = wasButton;
                if (comp != null) comp.scenarioDecides = wasScenario;
            }
        }

        // ------------------------------------------------------------------ Phase 2: one mood, quantised, changed-only
        // ProofCompositor pushes the shipped default scheme as a proof mood on one freshly handed-over fixture and drives
        // the SHIPPED compositor at explicit times (Evaluate(comp, t)), so nothing depends on frame timing. Leaves the map
        // as it found it: fixture released, settings and the previously pushed mood put back, the proof group removed.
        public const string ProofClaimant = "atmosphericbase.proof";
        private const string EmptyGroup = "atmosphericbase.proof.empty";

        public static string ProofCompositor(string args)
        {
            RM_AtmosphericBaseSettings cur = RM_AtmosphericBaseSettings.Cur;
            bool wasLight = cur.lightChannel, wasComp = cur.compositor, wasDefault = cur.defaultMood;
            int wasGroup = cur.defaultMoodGroup;
            Map map = Find.CurrentMap;
            RM_MapComponent_AtmosphericBase comp = RM_MapComponent_AtmosphericBase.For(map);
            List<RM_MoodClaim> prior = comp?.TakeAllMoods();   // the proof mood is the only one while it runs
            Thing a = null;
            bool pushed = false;
            try
            {
                RM_AtmosphericSchemeDef d = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
                string s = "scheme=" + (d == null ? "-" : B(d.Valid)) + " schemes=" + DefDatabase<RM_AtmosphericSchemeDef>.DefCount;
                if (map == null || comp == null) return s + " map=-";
                if (d == null || !d.Valid) return s + " eligible=-";
                cur.lightChannel = true; cur.compositor = true; cur.defaultMood = true; cur.defaultMoodGroup = 0;
                List<Building> eligible = RM_EmitterDiscovery.EligibleOn(map).Where(b => !comp.IsTaken(b)).ToList();
                Building lit = eligible.FirstOrDefault(b => RM_EmitterDiscovery.GlowerOf(b).Glows);
                s += " eligible=" + eligible.Count + " lit=" + (lit == null ? "-" : "True");
                if (lit == null) return s;
                a = lit;
                Thing nb = eligible.FirstOrDefault(b => b != a);
                CompGlower ga = RM_EmitterDiscovery.GlowerOf(a);
                RM_GlowSnapshot before = RM_GlowAccess.Snapshot(ga);
                RM_GlowSnapshot nbBefore = nb != null ? RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(nb)) : null;
                int violations0 = RM_PaletteGuard.violations;
                var palette = new HashSet<ColorInt>(d.palette);

                comp.TakeOver(a);
                pushed = comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, d, 0f, out _);
                s += " push=" + B(pushed);
                RM_SchemeData data = d.Data;
                int room = a.GetRoom()?.ID ?? -1;
                double t0 = 1000.0;

                comp.compositor.Evaluate(comp, t0, refreshMembership: true);
                int want = RM_SchemeKernel.PaletteIndex(data, a.thingIDNumber, room, t0, false);
                bool first = ga.GlowColor == d.palette[want] && ga.HasGlowColorOverride;
                string showing = RM_AtmosphericBaseAPI.Showing(a);
                int again = comp.compositor.Evaluate(comp, t0);
                s += " first_write=" + B(first) + " showing=" + (showing ?? "-") + " same_time_writes=" + again;

                // a sweep across two full cycles: every colour seen is a palette member, and writes == index changes
                int sweepWrites = 0, transitions = 0, evals = 0, last = want;
                bool quantised = true;
                for (double t = t0 + 0.5; t <= t0 + 2 * data.massPeriodSeconds; t += 0.5)
                {
                    sweepWrites += comp.compositor.Evaluate(comp, t);
                    evals++;
                    int idx = RM_SchemeKernel.PaletteIndex(data, a.thingIDNumber, room, t, false);
                    if (idx != last) { transitions++; last = idx; }
                    if (!palette.Contains(ga.GlowColor) || ga.GlowColor != d.palette[idx]) quantised = false;
                }
                s += " sweep_evals=" + evals + " sweep_fixture_writes_max=" + sweepWrites + " transitions=" + transitions
                   + " quantised=" + B(quantised) + " taken=" + comp.TakenCount;
                // with other held fixtures on the map the sweep counts their writes too, so changed_only is judged on
                // a map where only the proof's fixture is held
                s += " changed_only=" + (comp.TakenCount == 1 ? B(again == 0 && sweepWrites == transitions && transitions > 0) : "-");
                s += " neighbour=" + (nb == null ? "-" : B(RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(nb)).SameAs(nbBefore)));

                // a group the fixture is not in -> its own glow
                comp.RegisterGroup(EmptyGroup, new Thing[0]);
                comp.PushMood(ProofClaimant, EmptyGroup, d, 0f, out _);
                comp.compositor.Evaluate(comp, t0);
                s += " outside_group_substrate=" + B(RM_GlowAccess.Snapshot(ga).SameAs(before));
                comp.UnregisterGroup(EmptyGroup);
                comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, d, 0f, out _);
                comp.compositor.Evaluate(comp, t0);

                // the compositor switch off -> its own glow; on again -> driven
                cur.compositor = false;
                comp.compositor.Evaluate(comp, t0);
                bool offSub = RM_GlowAccess.Snapshot(ga).SameAs(before);
                cur.compositor = true;
                comp.compositor.Evaluate(comp, t0);
                s += " compositor_off_substrate=" + B(offSub) + " compositor_on_drives=" + B(ga.GlowColor == d.palette[want]);

                // releasing the mood with the default off -> its own glow; default on -> the default runs
                comp.ReleaseMood(ProofClaimant);
                pushed = false;
                cur.defaultMood = false;
                comp.compositor.Evaluate(comp, t0);
                bool relSub = RM_GlowAccess.Snapshot(ga).SameAs(before);
                cur.defaultMood = true;
                comp.compositor.Evaluate(comp, t0);
                bool defRuns = comp.EffectiveMood?.claimant == RM_Compositor.DefaultClaimant && palette.Contains(ga.GlowColor);
                s += " mood_release_substrate=" + B(relSub) + " default_runs=" + B(defRuns);

                comp.Release(a);
                bool exact = RM_GlowAccess.Snapshot(ga).SameAs(before);
                a = null;
                s += " released_exact=" + B(exact) + " palette_violations=" + (RM_PaletteGuard.violations - violations0);
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                if (comp != null)
                {
                    cur.lightChannel = true;
                    if (a != null) comp.Release(a);
                    comp.UnregisterGroup(EmptyGroup);
                    comp.ReleaseMood(ProofClaimant);
                    comp.RestoreMoods(prior);
                }
                cur.lightChannel = wasLight; cur.compositor = wasComp; cur.defaultMood = wasDefault; cur.defaultMoodGroup = wasGroup;
            }
        }

        // ------------------------------------------------------------------ Phases 3-4: territory and tremor
        // ProofTerritory hands over up to MaxProofFixtures untaken LIT fixtures, lifts every pushed mood off the map, and
        // pushes two territory moods (the shipped Lamplight louder than the shipped Fireflies, both over "ship") and four
        // tremor moods (one more than L6 allows). It then evaluates the SHIPPED compositor at every step of one full turn
        // of the boundary, on explicit times. Answers key=value; leaves the map as it found it.
        private const int MaxProofFixtures = 40;
        private static readonly string[] TremorClaimants = { "atmosphericbase.proof.t1", "atmosphericbase.proof.t2", "atmosphericbase.proof.t3", "atmosphericbase.proof.t4" };
        private const string SecondClaimant = "atmosphericbase.proof.second";

        public static string ProofTerritory(string args)
        {
            RM_AtmosphericBaseSettings cur = RM_AtmosphericBaseSettings.Cur;
            bool wasLight = cur.lightChannel, wasComp = cur.compositor, wasTerr = cur.territory, wasTremor = cur.tremor;
            Map map = Find.CurrentMap;
            RM_MapComponent_AtmosphericBase comp = RM_MapComponent_AtmosphericBase.For(map);
            List<RM_MoodClaim> prior = comp?.TakeAllMoods();
            var held = new List<Thing>();
            var before = new Dictionary<Thing, RM_GlowSnapshot>();
            try
            {
                RM_AtmosphericSchemeDef la = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
                RM_AtmosphericSchemeDef ff = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail("RM_Scheme_Fireflies");
                string s = "schemes=" + B(la != null && la.Valid && ff != null && ff.Valid);
                if (map == null || comp == null) return s + " map=-";
                if (la == null || ff == null || !la.Valid || !ff.Valid) return s + " lit=-";
                cur.lightChannel = true; cur.compositor = true; cur.territory = true; cur.tremor = true;
                foreach (Building b in RM_EmitterDiscovery.EligibleOn(map))
                {
                    if (held.Count >= MaxProofFixtures) break;
                    if (comp.IsTaken(b) || !RM_EmitterDiscovery.GlowerOf(b).Glows) continue;
                    before[b] = RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(b));
                    if (comp.TakeOver(b)) held.Add(b);
                }
                s += " lit=" + held.Count + " others_held=" + (comp.TakenCount - held.Count);
                if (held.Count < 2) return s;
                int violations0 = RM_PaletteGuard.violations;
                comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, la, 10f, out _);
                comp.PushMood(SecondClaimant, RM_SchemeKernel.GroupShip, ff, 5f, out _);
                for (int i = 0; i < TremorClaimants.Length; i++)
                    comp.PushMood(TremorClaimants[i], RM_SchemeKernel.GroupShip, i % 2 == 0 ? la : ff, -i, out _);
                RM_AtmosphericSchemeDef[] tremorScheme = { la, ff, la };

                RM_TerritoryTuning tt = cur.TerritoryTuning;
                RM_TremorTuning tu = cur.TremorTuning;
                double t0 = 5000.0, dt = tt.periodSeconds / RM_TerritoryKernel.StepsPerTurn;
                comp.compositor.ResetCounters();
                comp.compositor.Evaluate(comp, t0, refreshMembership: true);
                var owners0 = held.ToDictionary(x => x, x => comp.compositor.TerritoryOwner(x));
                var changed = new HashSet<Thing>();
                bool oneOwner = true, bothSides = true, ownPalette = true, tremorOwn = true;
                int tremorSeen = 0, maxTremor = 0, maxContrib = 0;
                for (int k = 0; k <= RM_TerritoryKernel.StepsPerTurn; k++)
                {
                    double t = t0 + k * dt + 0.5 * dt;
                    comp.compositor.Evaluate(comp, t);
                    int lead = 0, second = 0, tremor = 0;
                    foreach (Thing x in held)
                    {
                        int o = comp.compositor.TerritoryOwner(x);
                        int tr = comp.compositor.TremorContributor(x);
                        if (o == 0) lead++; else if (o == 1) second++; else oneOwner = false;
                        if (o != owners0[x]) changed.Add(x);
                        if (!comp.compositor.Shows(x, out long v) || v == RM_ChangeTracker.Substrate) { ownPalette = false; continue; }
                        RM_AtmosphericSchemeDef want = tr >= 0 ? (tr < tremorScheme.Length ? tremorScheme[tr] : null) : (o == 0 ? la : ff);
                        CompGlower g = RM_EmitterDiscovery.GlowerOf(x);
                        bool ok = want != null && (ushort)(v >> 8) == want.shortHash && g.GlowColor == want.palette[(int)(v & 0xFF)];
                        if (tr >= 0) { tremor++; if (!ok) tremorOwn = false; }
                        else if (!ok) ownPalette = false;
                    }
                    if (lead == 0 || second == 0) bothSides = false;
                    tremorSeen += tremor;
                    maxTremor = System.Math.Max(maxTremor, tremor);
                    maxContrib = System.Math.Max(maxContrib, comp.compositor.lastTremorContributors);
                }
                s += " one_owner=" + B(oneOwner) + " both_sides=" + B(bothSides) + " own_palette=" + B(ownPalette)
                   + " moved=" + changed.Count + "/" + held.Count + " boundary_moves=" + B(changed.Count == held.Count)
                   + " flips=" + comp.compositor.territoryFlips + " allocations=" + comp.compositor.allocations
                   + " writes=" + comp.compositor.writes;
                s += " tremor_contributors=" + maxContrib + " tremor_cap_held=" + B(maxContrib <= RM_TremorKernel.LawCap)
                   + " tremor_seen=" + tremorSeen + " tremor_max=" + maxTremor
                   + " tremor_fraction_held=" + B(maxTremor <= RM_TremorKernel.InstantCap(comp.compositor.lastDrivenCount, tu.maxFraction))
                   + " tremor_own_palette=" + B(tremorOwn);

                cur.territory = false; cur.tremor = false;
                comp.compositor.Evaluate(comp, t0);
                bool offOne = held.All(x => comp.compositor.TerritoryOwner(x) == -1 && comp.compositor.Shows(x, out long v) && (ushort)(v >> 8) == la.shortHash);
                s += " territory_off_one_mood=" + B(offOne);

                foreach (Thing x in held) comp.Release(x);
                bool exact = held.All(x => RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(x)).SameAs(before[x]));
                held.Clear();
                s += " released_exact=" + B(exact) + " palette_violations=" + (RM_PaletteGuard.violations - violations0);
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                if (comp != null)
                {
                    cur.lightChannel = true;
                    foreach (Thing x in held) comp.Release(x);
                    comp.TakeAllMoods();
                    comp.RestoreMoods(prior);
                }
                cur.lightChannel = wasLight; cur.compositor = wasComp; cur.territory = wasTerr; cur.tremor = wasTremor;
            }
        }

        // ------------------------------------------------------------------ ProofSample: the time-aware proof hook
        // ATMOSPHERIC_BASE_BUILD_PROGRAM_1, design/RimMandrake/atmospheric_base_proof_plan_2026-10-23.md §2. TEST-ONLY:
        // nothing on a shipped path calls it. It steps the SHIPPED RM_Compositor.Evaluate(comp, t) on a virtual clock
        // (only the time argument is supplied), reads the fixtures back, and answers JSON. Every command that changes
        // anything puts it back in a finally: settings fields (all of them, by reflection), pushed moods, held fixtures,
        // a flicked-off switch. Commands: sanity pick series counters settings cost snapshot hold release is_taken showing.
        private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
        private const int CellBlock = 4;   // "spread": distinct CellBlock x CellBlock blocks the lit fixtures stand in

        private static string Q(string s)
        {
            if (s == null) return "null";
            var sb = new StringBuilder("\"");
            foreach (char c in s)
            {
                if (c == '"' || c == '\\') sb.Append('\\').Append(c);
                else if (c < 32) sb.Append(' ');
                else sb.Append(c);
            }
            return sb.Append('"').ToString();
        }
        private static string N(double v) => v.ToString("R", Inv);
        private static string Rgb(ColorInt c) => "[" + c.r + "," + c.g + "," + c.b + "]";
        private static string Pal(RM_AtmosphericSchemeDef d) => "[" + string.Join(",", d.palette.Select(Rgb).ToArray()) + "]";
        private static string Err(string m) => "{\"error\":" + Q(m) + "}";

        private static Dictionary<string, string> ParseArgs(string args)
        {
            var kv = new Dictionary<string, string>();
            foreach (string part in (args ?? "").Split(new[] { ' ' }, System.StringSplitOptions.RemoveEmptyEntries))
            {
                int i = part.IndexOf('=');
                if (i > 0) kv[part.Substring(0, i)] = part.Substring(i + 1);
            }
            return kv;
        }

        private static IEnumerable<Building> LitPool(Map map, RM_MapComponent_AtmosphericBase comp)
        {
            return RM_EmitterDiscovery.EligibleOn(map).Where(b => !comp.IsTaken(b) && RM_EmitterDiscovery.GlowerOf(b).Glows)
                                                      .OrderBy(b => b.thingIDNumber);
        }

        // a fixture by id: the ThingID ("Lamp123") or the bare number
        private static Thing Resolve(Map map, string id)
        {
            if (map == null || string.IsNullOrEmpty(id)) return null;
            foreach (Building b in RM_EmitterDiscovery.EligibleOn(map))
                if (b.ThingID == id || b.thingIDNumber.ToString(Inv) == id) return b;
            return null;
        }

        /// <summary>Everything a command may change, and the way back. Close() is the finally block.</summary>
        private sealed class Session
        {
            public readonly Map map = Find.CurrentMap;
            public readonly RM_MapComponent_AtmosphericBase comp;
            public readonly RM_AtmosphericBaseSettings cur = RM_AtmosphericBaseSettings.Cur;
            public readonly List<Thing> held = new List<Thing>();
            public readonly List<System.Action> undo = new List<System.Action>();
            private readonly List<RM_MoodClaim> prior;
            private readonly Dictionary<FieldInfo, object> saved = new Dictionary<FieldInfo, object>();

            public Session()
            {
                comp = RM_MapComponent_AtmosphericBase.For(map);
                if (map == null || comp == null) throw new System.Exception("no current map with the AtmosphericBase component");
                foreach (FieldInfo f in typeof(RM_AtmosphericBaseSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                    if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                        saved[f] = f.GetValue(cur);
                prior = comp.TakeAllMoods();
            }

            public void Close()
            {
                for (int i = undo.Count - 1; i >= 0; i--) try { undo[i](); } catch (System.Exception) { }
                foreach (Thing x in held) comp.Release(x);
                held.Clear();
                comp.TakeAllMoods();
                comp.RestoreMoods(prior);
                foreach (KeyValuePair<FieldInfo, object> kv in saved) kv.Key.SetValue(cur, kv.Value);
            }
        }

        private static string Fixture(Thing x, RM_MapComponent_AtmosphericBase comp)
        {
            CompGlower g = RM_EmitterDiscovery.GlowerOf(x);
            ColorInt c = g.GlowColor;
            int owner = comp.compositor.TerritoryOwner(x), tr = comp.compositor.TremorContributor(x);
            string role;
            if (!comp.compositor.Shows(x, out long v) || v == RM_ChangeTracker.Substrate) role = "S";
            else if (tr >= 0) role = "T";
            else if (owner == 0) role = "L";
            else if (owner == 1) role = "O";
            else role = "M";
            return "[" + x.thingIDNumber + "," + c.r + "," + c.g + "," + c.b + "," + owner + ",\"" + role + "\"," + tr + "]";
        }

        private static string Series(Dictionary<string, string> kv)
        {
            string scenario = kv.TryGetValue("scenario", out string sc) ? sc : "";
            double t0 = kv.TryGetValue("t0", out string a) ? double.Parse(a, Inv) : 1000.0;
            double dt = kv.TryGetValue("dt", out string b) ? double.Parse(b, Inv) : 1.0;
            int n = kv.TryGetValue("n", out string c) ? int.Parse(c, Inv) : 1;
            RM_AtmosphericSchemeDef la = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
            RM_AtmosphericSchemeDef ff = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail("RM_Scheme_Fireflies");
            if (scenario == "gesture" || scenario == "narrator_alarm") return "{\"unknown_scenario\":" + Q(scenario) + "}";   // Phase 5+: nothing shipped
            if (scenario == "white_scheme")
            {
                var w = new RM_AtmosphericSchemeDef { defName = "RM_ProofWhite", palette = new List<ColorInt> { new ColorInt(23, 201, 117, 0), new ColorInt(255, 255, 255, 0) } };
                return "{\"valid\":" + (w.Valid ? "true" : "false") + ",\"samples\":[]}";
            }
            if (la == null || ff == null || !la.Valid || !ff.Valid) return Err("shipped schemes Lamplight/Fireflies missing or invalid");
            RM_AtmosphericSchemeDef dark = DefDatabase<RM_AtmosphericSchemeDef>.AllDefsListForReading.FirstOrDefault(d => d.Valid && d.mayGoDark);
            if (scenario == "dark" && dark == null) return "{\"unsupported\":\"no shipped scheme mayGoDark (Lamplight and Fireflies never go dark)\"}";
            var known = new[] { "one_mood", "territory", "territory_swap", "territory_short_period", "tremor", "default", "dark", "unlit" };
            if (!known.Contains(scenario)) return "{\"unknown_scenario\":" + Q(scenario) + "}";

            var s = new Session();
            try
            {
                RM_AtmosphericBaseSettings cur = s.cur;
                RM_MapComponent_AtmosphericBase comp = s.comp;
                List<Building> pool = LitPool(s.map, comp).ToList();
                Building ctl = pool.Count >= 2 ? pool[pool.Count - 1] : null;
                if (ctl != null) pool.RemoveAt(pool.Count - 1);
                if (pool.Count > MaxProofFixtures) pool = pool.Take(MaxProofFixtures).ToList();
                if (pool.Count == 0) return "{\"samples\":[]}";
                CompGlower ctlG = ctl != null ? RM_EmitterDiscovery.GlowerOf(ctl) : null;
                foreach (Building f in pool) if (comp.TakeOver(f)) s.held.Add(f);
                cur.lightChannel = true; cur.compositor = true; cur.territory = false; cur.tremor = false;
                cur.defaultMood = true; cur.defaultMoodGroup = 0;
                if (kv.TryGetValue("period", out string per)) cur.territoryPeriodSeconds = float.Parse(per, Inv);
                string leadClaimant = ProofClaimant;
                string tremorPal = "[]";
                bool swap = scenario == "territory_swap";
                switch (scenario)
                {
                    case "one_mood": comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, la, 0f, out _); break;
                    case "dark": comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, dark, 0f, out _); break;
                    case "territory": case "territory_swap": case "territory_short_period":
                        cur.territory = true;
                        comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, la, swap ? 5f : 10f, out _);
                        comp.PushMood(SecondClaimant, RM_SchemeKernel.GroupShip, ff, swap ? 10f : 5f, out _);
                        if (swap) leadClaimant = SecondClaimant;
                        break;
                    case "tremor":
                        cur.territory = true; cur.tremor = true;
                        comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, la, 10f, out _);
                        comp.PushMood(SecondClaimant, RM_SchemeKernel.GroupShip, ff, 5f, out _);
                        for (int i = 0; i < TremorClaimants.Length; i++)
                            comp.PushMood(TremorClaimants[i], RM_SchemeKernel.GroupShip, i % 2 == 0 ? la : ff, -i, out _);
                        tremorPal = "[" + Pal(la) + "," + Pal(ff) + "," + Pal(la) + "]";
                        break;
                }
                Thing unlit = null;
                RM_GlowSnapshot unlitBefore = null;
                if (scenario == "unlit")
                {
                    foreach (Thing x in s.held)
                    {
                        CompFlickable fl = x.TryGetComp<CompFlickable>();
                        if (fl == null || !fl.SwitchIsOn) continue;
                        CompGlower g = RM_EmitterDiscovery.GlowerOf(x);
                        unlit = x;
                        s.undo.Add(() => { fl.SwitchIsOn = true; g.ReceiveCompSignal("FlickedOn"); });
                        fl.SwitchIsOn = false; g.ReceiveCompSignal("FlickedOff");
                        if (g.Glows) { unlit = null; fl.SwitchIsOn = true; g.ReceiveCompSignal("FlickedOn"); continue; }
                        break;
                    }
                    if (unlit == null) return "{\"unsupported\":\"no held fixture could be flicked off (no CompFlickable that unlights it)\"}";
                    unlitBefore = RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(unlit));
                }

                RM_TerritoryTuning tt = cur.TerritoryTuning;
                long skipped0 = comp.compositor.skippedUnlit;
                var samples = new StringBuilder();
                double tLast = t0;
                for (int k = 0; k < n; k++)
                {
                    double t = t0 + k * dt;
                    tLast = t;
                    int w = comp.compositor.Evaluate(comp, t, refreshMembership: k == 0);
                    if (k > 0) samples.Append(',');
                    samples.Append("{\"t\":").Append(N(t)).Append(",\"step\":").Append(RM_TerritoryKernel.ClockStep(t, tt.periodSeconds))
                           .Append(",\"writes\":").Append(w).Append(",\"contributors\":").Append(comp.compositor.lastTremorContributors)
                           .Append(",\"fx\":[").Append(string.Join(",", s.held.Select(x => Fixture(x, comp)).ToArray())).Append("],\"ctl\":")
                           .Append(ctlG != null ? Rgb(ctlG.GlowColor) : "null").Append('}');
                }
                int sameT = comp.compositor.Evaluate(comp, tLast);   // a re-evaluation at the same instant must write nothing
                var o = new StringBuilder("{\"scenario\":" + Q(scenario));
                o.Append(",\"period\":").Append(N(tt.periodSeconds)).Append(",\"lead_share\":").Append(N(tt.leadShare))
                 .Append(",\"lead_expected\":").Append(RM_TerritoryKernel.LeadCount(s.held.Count, tt.leadShare))
                 .Append(",\"lead_claimant\":").Append(Q(leadClaimant))
                 .Append(",\"palettes\":{\"lead\":").Append(Pal(la)).Append(",\"other\":").Append(Pal(ff)).Append(",\"tremor\":").Append(tremorPal)
                 .Append(",\"mood\":").Append(Pal(scenario == "dark" ? dark : la)).Append('}')
                 .Append(",\"fixtures\":").Append(s.held.Count).Append(",\"others_held\":").Append(comp.TakenCount - s.held.Count)
                 .Append(",\"same_t_writes\":").Append(sameT);
                if (unlit != null)
                    o.Append(",\"unlit_id\":").Append(unlit.thingIDNumber)
                     .Append(",\"unlit_writes\":").Append(RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(unlit)).SameAs(unlitBefore) ? 0 : 1)
                     .Append(",\"skipped_unlit_delta\":").Append(comp.compositor.skippedUnlit - skipped0);
                return o.Append(",\"samples\":[").Append(samples).Append("]}").ToString();
            }
            finally { s.Close(); }
        }

        private static string Sanity()
        {
            var s = new Session();
            try
            {
                RM_AtmosphericSchemeDef la = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
                if (la == null || !la.Valid || la.palette.Count < 2) return Err("Lamplight missing or has fewer than 2 colours");
                List<Building> pool = LitPool(s.map, s.comp).ToList();
                if (pool.Count == 0) return Err("no lit eligible fixture");
                Building lamp = pool[0];
                Building stat = pool.Count > 1 ? pool[pool.Count - 1] : null;
                s.cur.lightChannel = true;
                if (!s.comp.TakeOver(lamp)) return Err("take-over refused");
                s.held.Add(lamp);
                CompGlower g = RM_EmitterDiscovery.GlowerOf(lamp);
                s.comp.Drive(lamp, la.palette[0]); ColorInt ra = g.GlowColor;
                s.comp.Drive(lamp, la.palette[1]); ColorInt rb = g.GlowColor;
                return "{\"lamp\":" + lamp.thingIDNumber + ",\"forced\":[" + Rgb(la.palette[0]) + "," + Rgb(la.palette[1]) + "],\"a\":" + Rgb(ra)
                     + ",\"b\":" + Rgb(rb) + ",\"static_id\":" + (stat != null ? stat.thingIDNumber.ToString(Inv) : "null") + "}";
            }
            finally { s.Close(); }
        }

        private static string Pick()
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_AtmosphericBase comp = RM_MapComponent_AtmosphericBase.For(map);
            if (map == null || comp == null) return Err("no current map with the AtmosphericBase component");
            List<Building> pool = LitPool(map, comp).ToList();
            Building ctl = pool.Count >= 2 ? pool[pool.Count - 1] : null;
            if (ctl != null) pool.RemoveAt(pool.Count - 1);
            if (pool.Count > MaxProofFixtures) pool = pool.Take(MaxProofFixtures).ToList();   // spread is of the fixtures a series will hold, not the whole map
            var cells = new HashSet<long>();
            foreach (Building b in pool) cells.Add(((long)(b.Position.x / CellBlock) << 32) ^ (uint)(b.Position.z / CellBlock));
            return "{\"fixtures\":[" + string.Join(",", pool.Select(b => b.thingIDNumber.ToString(Inv)).ToArray())
                 + "],\"lit\":" + pool.Count + ",\"spread\":" + cells.Count + ",\"spread_block\":" + CellBlock
                 + ",\"untaken\":" + (ctl != null ? ctl.thingIDNumber.ToString(Inv) : "null") + "}";
        }

        private static string Settings()
        {
            RM_AtmosphericBaseSettings cur = RM_AtmosphericBaseSettings.Cur;
            var parts = new List<string>();
            foreach (FieldInfo f in typeof(RM_AtmosphericBaseSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
            {
                object v = f.GetValue(cur);
                if (f.FieldType == typeof(bool)) parts.Add(Q(f.Name) + ":" + ((bool)v ? "true" : "false"));
                else if (f.FieldType == typeof(float)) parts.Add(Q(f.Name) + ":" + N((float)v));
                else if (f.FieldType == typeof(int)) parts.Add(Q(f.Name) + ":" + v);
            }
            System.Func<RM_AtmosphericSchemeDef, string> sch = d => d == null ? "null"
                : "{\"defName\":" + Q(d.defName) + ",\"palette\":" + Pal(d) + ",\"mayGoDark\":" + (d.mayGoDark ? "true" : "false")
                  + ",\"flasherCount\":" + d.flasherCount + ",\"massPeriodSeconds\":" + N(d.massPeriodSeconds) + "}";
            RM_AtmosphericSchemeDef def = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
            RM_AtmosphericSchemeDef dk = DefDatabase<RM_AtmosphericSchemeDef>.AllDefsListForReading.FirstOrDefault(d => d.Valid && d.mayGoDark);
            return "{\"settings\":{" + string.Join(",", parts.ToArray()) + "},\"default_scheme\":" + sch(def) + ",\"dark_scheme\":" + sch(dk) + "}";
        }

        private static string Cost(Dictionary<string, string> kv)
        {
            int n = kv.TryGetValue("n", out string a) ? System.Math.Max(1, int.Parse(a, Inv)) : 100;
            RM_AtmosphericSchemeDef la = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail(RM_Compositor.DefaultSchemeDefName);
            RM_AtmosphericSchemeDef ff = DefDatabase<RM_AtmosphericSchemeDef>.GetNamedSilentFail("RM_Scheme_Fireflies");
            if (la == null || ff == null || !la.Valid || !ff.Valid) return Err("shipped schemes missing or invalid");
            var s = new Session();
            try
            {
                foreach (Building f in LitPool(s.map, s.comp).Take(MaxProofFixtures).ToList()) if (s.comp.TakeOver(f)) s.held.Add(f);
                if (s.held.Count == 0) return "{\"ms_per_eval\":-1,\"fixtures\":0}";
                s.cur.lightChannel = true; s.cur.compositor = true; s.cur.territory = true; s.cur.tremor = true;
                s.comp.PushMood(ProofClaimant, RM_SchemeKernel.GroupShip, la, 10f, out _);
                s.comp.PushMood(SecondClaimant, RM_SchemeKernel.GroupShip, ff, 5f, out _);
                for (int i = 0; i < TremorClaimants.Length; i++)
                    s.comp.PushMood(TremorClaimants[i], RM_SchemeKernel.GroupShip, i % 2 == 0 ? la : ff, -i, out _);
                s.comp.compositor.Evaluate(s.comp, 1000.0, refreshMembership: true);
                var sw = System.Diagnostics.Stopwatch.StartNew();
                for (int k = 0; k < n; k++) s.comp.compositor.Evaluate(s.comp, 1000.0 + k * 3.75);
                sw.Stop();
                return "{\"ms_per_eval\":" + N(sw.Elapsed.TotalMilliseconds / n) + ",\"fixtures\":" + s.held.Count + ",\"n\":" + n + "}";
            }
            finally { s.Close(); }
        }

        private static string Counters()
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_AtmosphericBase comp = RM_MapComponent_AtmosphericBase.For(map);
            if (comp == null) return Err("no current map with the AtmosphericBase component");
            RM_Compositor c = comp.compositor;
            return "{\"evaluations\":" + c.evaluations + ",\"fixtureEvaluations\":" + c.fixtureEvaluations + ",\"writes\":" + c.writes
                 + ",\"skippedUnchanged\":" + c.skippedUnchanged + ",\"skippedUnlit\":" + c.skippedUnlit + ",\"lastEvalWrites\":" + c.lastEvalWrites
                 + ",\"maxEvalWrites\":" + c.maxEvalWrites + ",\"allocations\":" + c.allocations + ",\"territoryFlips\":" + c.territoryFlips
                 + ",\"tremorWrites\":" + c.tremorWrites + ",\"maxTremorCount\":" + c.maxTremorCount + ",\"violations\":" + RM_PaletteGuard.violations + "}";
        }

        private static string Snapshot()
        {
            Map map = Find.CurrentMap;
            if (map == null) return Err("no current map");
            var rows = new List<string>();
            foreach (Building b in RM_EmitterDiscovery.EligibleOn(map).OrderBy(x => x.thingIDNumber))
            {
                CompGlower g = RM_EmitterDiscovery.GlowerOf(b);
                if (g == null) continue;
                ColorInt c = g.GlowColor;
                rows.Add("[" + b.thingIDNumber + "," + c.r + "," + c.g + "," + c.b + "]");
            }
            return "{\"fx\":[" + string.Join(",", rows.ToArray()) + "]}";
        }

        // hold / release / is_taken / showing: RM_AtmosphericBaseAPI takes a Thing, which jawa/static_call cannot build
        // from an id string, so the hook resolves the id and calls the API itself. hold changes nothing else.
        private static string OnThing(string cmd, Dictionary<string, string> kv)
        {
            Thing t = Resolve(Find.CurrentMap, kv.TryGetValue("id", out string id) ? id : null);
            if (t == null) return Err("no eligible fixture with id " + (id ?? "(none)"));
            switch (cmd)
            {
                case "hold": return "{\"ok\":" + (RM_AtmosphericBaseAPI.TakeOver(t) ? "true" : "false") + "}";
                case "release": return "{\"ok\":" + (RM_AtmosphericBaseAPI.Release(t) ? "true" : "false") + "}";
                case "is_taken": return "{\"taken\":" + (RM_AtmosphericBaseAPI.IsTaken(t) ? "true" : "false") + "}";
                default: return "{\"showing\":" + Q(RM_AtmosphericBaseAPI.Showing(t)) + "}";
            }
        }

        public static string ProofSample(string args)
        {
            try
            {
                Dictionary<string, string> kv = ParseArgs(args);
                string cmd = kv.TryGetValue("cmd", out string c) ? c : "";
                switch (cmd)
                {
                    case "sanity": return Sanity();
                    case "pick": return Pick();
                    case "series": return Series(kv);
                    case "counters": return Counters();
                    case "settings": return Settings();
                    case "cost": return Cost(kv);
                    case "snapshot": return Snapshot();
                    case "hold": case "release": case "is_taken": case "showing": return OnThing(cmd, kv);
                    default: return Err("unknown cmd " + cmd);
                }
            }
            catch (System.Exception e)
            {
                return Err(e.GetType().Name + ": " + e.Message);
            }
        }
    }
}
