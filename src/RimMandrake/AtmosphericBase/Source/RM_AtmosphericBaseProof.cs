// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- live proof hook for validation.py (jawa/static_call).
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
        private static readonly ColorInt TestColor = new ColorInt(23, 201, 117, 0);

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
    }
}
