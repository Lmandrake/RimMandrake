// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phases 1-2 -- live proof hooks for validation.py (jawa/static_call).
// ProofTakeover runs the SHIPPED take-over on the current map and leaves it as it found it: settings restored in
// finally, the test fixture released, the scenario flag put back. Answers one line of key=value; "-" where the map has
// nothing to test on (no eligible fixture, no excluded glower of a kind), which the suite reads as UNMEASURED.
using System.Collections.Generic;
using System.Linq;
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
            RM_MoodClaim prior = comp?.PushedMood;
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
                    if (prior != null) comp.PushMood(prior.claimant, prior.group, prior.scheme, prior.rank, out _);
                    else comp.ReleaseMood(ProofClaimant);
                }
                cur.lightChannel = wasLight; cur.compositor = wasComp; cur.defaultMood = wasDefault; cur.defaultMoodGroup = wasGroup;
            }
        }
    }
}
