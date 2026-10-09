using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ══════════════════════════════════════════════════════════════════
    // GELATINOUSSLIME_JOINING_WATER_STANDALONE_1 — the engine under the Joining Water rite.
    //
    // Owner, typed 2026-10-02: "Everyone briefly joins hands holding some slime. Can reduce permanent hediffs on one
    // person to weak hediffs on several instead." Ruled 2026-10-08: "separate for now" = the rite stands alone, a
    // self-contained found rite at the Slime, no quest chain. The rite itself (precept, pattern, outcome, memory) is the
    // campaign tier's XML in mandrake.rut.rites; this file is the franchise-free engine it points at, the same split as
    // Ninefold's Nine Faults.
    //
    //   RM_SlimeHandRing                          the found site: a ring of hand-prints pressed into hardened slime (placed by
    //                                             GenStep_SlimeHandRing at map generation).
    //   RM_RitualObligationTargetWorker_SlimeHandRing  the ritual may be held at a ring.
    //   RM_RitualOutcomeEffectWorker_JoiningWater the donor (most permanent severity among the participants) loses a share of
    //                                             each permanent hediff, and every other participant takes a weak,
    //                                             temporary RM_SharedBurden for the shared remainder.
    //
    // What counts as permanent here (my scoping, PROVISIONAL): a permanent injury (a scar) or a chronic hediff, moved by
    // severity. A missing part is NOT permanent in this sense: there is no severity to share, so it is left alone.
    // The risk is the Slime's own: everyone stands on the slime, so slimification ticks all through the rite.
    // ══════════════════════════════════════════════════════════════════
    public class RM_JoiningWaterExtension : DefModExtension
    {
        public float poorFraction = 0.25f;
        public float fairFraction = 0.5f;
        public float goodFraction = 0.7f;
        public float excellentFraction = 0.9f;
        /// <summary>Each recipient carries this fraction of an even split, so the echo is weaker than the wound it came from.</summary>
        public float weakFactor = 0.5f;
        public HediffDef sharedBurden;
    }

    public class GenStep_SlimeHandRing : GenStep
    {
        public ThingDef ringDef;
        public override int SeedPart => 0x51A22;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (SlimeDefs.GelatinousSlime == null || map.Biome != SlimeDefs.GelatinousSlime
                || !SlimeSettings.joiningWaterEnabled || ringDef == null)
            {
                return;
            }
            for (int attempt = 0; attempt < 80; attempt++)
            {
                IntVec3 c = CellFinderLoose.RandomCellWith(x => x.InBounds(map), map, 50);
                if (!c.IsValid || !Fits(map, c)) continue;
                GenSpawn.Spawn(ThingMaker.MakeThing(ringDef), c, map);
                return;
            }
            Log.Warning("[RM GelatinousSlime] Joining Water: no cell found for the hand ring.");
        }

        private static bool Fits(Map map, IntVec3 c)
        {
            foreach (IntVec3 n in GenAdj.OccupiedRect(c, Rot4.North, new IntVec2(3, 3)))
            {
                if (!n.InBounds(map) || !n.Standable(map) || n.GetEdifice(map) != null) return false;
                TerrainDef t = n.GetTerrain(map);
                if (t == null || t.IsWater || !t.HasTag(SlimeDefs.SlimeTerrainTag)) return false;
            }
            return true;
        }
    }

    public class RM_RitualObligationTargetWorker_SlimeHandRing : RitualObligationTargetFilter
    {
        public RM_RitualObligationTargetWorker_SlimeHandRing() { }
        public RM_RitualObligationTargetWorker_SlimeHandRing(RitualObligationTargetFilterDef def) : base(def) { }

        public override IEnumerable<TargetInfo> GetTargets(RitualObligation obligation, Map map)
        {
            ThingDef ring = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SlimeHandRing");
            if (ring == null || !SlimeSettings.joiningWaterEnabled) yield break;
            foreach (Thing t in map.listerThings.ThingsOfDef(ring)) yield return t;
        }

        protected override RitualTargetUseReport CanUseTargetInternal(TargetInfo target, RitualObligation obligation)
        {
            // plain false for everything else: a fail REASON would show a disabled ritual gizmo on every thing
            return target.HasThing && target.Thing.def.defName == "RM_SlimeHandRing" && SlimeSettings.joiningWaterEnabled;
        }

        public override IEnumerable<string> GetTargetInfos(RitualObligation obligation)
        {
            yield return "a ring of hand-prints pressed into hardened slime";
        }
    }

    public class RM_RitualOutcomeEffectWorker_JoiningWater : RitualOutcomeEffectWorker_FromQuality
    {
        public RM_RitualOutcomeEffectWorker_JoiningWater() { }
        public RM_RitualOutcomeEffectWorker_JoiningWater(RitualOutcomeEffectDef def) : base(def) { }

        /// <summary>A permanent injury or a chronic hediff, i.e. something whose severity can be shared.</summary>
        public static bool IsShareable(Hediff h)
        {
            if (h == null || h is Hediff_MissingPart) return false;
            Hediff_Injury inj = h as Hediff_Injury;
            if (inj != null) return inj.IsPermanent();
            return h.def.chronic;
        }

        private static List<Hediff> Shareable(Pawn p)
        {
            List<Hediff> list = new List<Hediff>();
            foreach (Hediff h in p.health.hediffSet.hediffs) if (IsShareable(h)) list.Add(h);
            return list;
        }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual,
            RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            if (!SlimeSettings.joiningWaterEnabled) return;
            RM_JoiningWaterExtension ext = def.GetModExtension<RM_JoiningWaterExtension>() ?? new RM_JoiningWaterExtension();
            List<Pawn> people = new List<Pawn>();
            foreach (Pawn p in totalPresence.Keys) if (p != null && !p.Dead && p.health != null && p.RaceProps.Humanlike) people.Add(p);
            if (people.Count < 2)
            {
                extraOutcomeDesc = "Too few joined hands: the water did not carry anything.";
                return;
            }
            List<float> totals = new List<float>();
            foreach (Pawn p in people)
            {
                float t = 0f;
                foreach (Hediff h in Shareable(p)) t += h.Severity;
                totals.Add(t);
            }
            int di = RM_JoiningWaterKernel.PickDonor(totals);
            if (di < 0)
            {
                extraOutcomeDesc = "Nobody carried anything permanent. The water was only water.";
                return;
            }
            Pawn donor = people[di];
            List<Pawn> recipients = new List<Pawn>(people);
            recipients.RemoveAt(di);
            float frac = RM_JoiningWaterKernel.ShareFraction(outcome.positivityIndex, ext.poorFraction, ext.fairFraction, ext.goodFraction, ext.excellentFraction);
            HediffDef weak = ext.sharedBurden ?? DefDatabase<HediffDef>.GetNamedSilentFail("RM_SharedBurden");
            int moved = 0;
            foreach (Hediff h in Shareable(donor))
            {
                RM_JoiningWaterKernel.Split(h.Severity, frac, recipients.Count, ext.weakFactor, out float taken, out float per);
                if (taken <= 0f) continue;
                h.Severity -= taken;
                if (h.Severity <= 0.001f && h is Hediff_Injury) donor.health.RemoveHediff(h);
                moved++;
                if (weak == null || per <= 0f) continue;
                foreach (Pawn r in recipients)
                {
                    Hediff b = r.health.hediffSet.GetFirstHediffOfDef(weak);
                    if (b == null) { b = HediffMaker.MakeHediff(weak, r); b.Severity = per; r.health.AddHediff(b); }
                    else b.Severity += per;
                }
            }
            if (moved > 0)
            {
                extraOutcomeDesc = new StringBuilder().Append(donor.LabelShortCap).Append(" set down ").Append(moved)
                    .Append(moved == 1 ? " lasting hurt" : " lasting hurts").Append(" and the rest of the ring took a little each.").ToString();
                letterLookTargets = new LookTargets(donor);
            }
        }
    }
}
