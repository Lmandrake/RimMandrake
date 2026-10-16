using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 — Contagion-touched, and the Sunbeam arrest.
    //
    // Owner rulings it builds to (kickoff packet §2, 2026-10-15):
    //   Q3 "Stops current mutations. No protection if you get exposed again later."
    //   N4 "Bloom time, stronger in burn, and contact."
    // and the deck ruled 2026-09-12 (research/mutation_systems_survey_2026-09-11.md, "THE DECK IS RULED"):
    //   "It should be a large variance experience that's 50% all negative and 50% positive + negative.
    //    The Contagion isn't nice." Custom unstable gene; a Contagion-added part copies the existing removal
    //   risk (HediffComp_UnfinishedEmerge: removing it surgically lets an Unfinished out).
    //
    // Shape: RM_ContagionTouched is the progression. Exposure (RM_MapComponent_ContagionTouch) raises its severity;
    // while it is on a pawn, HediffComp_RM_ContagionTouched rolls mutations at an MTB that shortens with severity. A
    // mutation is any HediffDef or GeneDef carrying RM_ContagionMutationExtension (the deck is data). The arrest removes
    // RM_ContagionTouched and nothing else: what grew stays, and the next dose starts a fresh condition.
    // The arithmetic is in Kernel/RM_TouchedKernel.cs (fuzzed by SelfTest/ContagionFuzz.cs, family "touched").

    /// <summary>Marks a HediffDef or GeneDef as a card in the Contagion-touched deck.</summary>
    public class RM_ContagionMutationExtension : DefModExtension
    {
        // Which half of the ruled 50/50 deck this card sits in.
        public bool allNegative;
        public float weight = 1f;
        // HediffDef only: the body part it grows on (a Hediff_AddedPart replaces that part). Null = whole body.
        public BodyPartDef installPart;
        // The never-upgrade law, written on the card: what it gives and what it costs, in words. ConfigErrors refuses a
        // card that is benefit-only, an all-negative card with a benefit, or a mixed card with no benefit.
        public List<string> benefits = new List<string>();
        public List<string> costs = new List<string>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (!RM_TouchedKernel.EntryLawful(allNegative, benefits?.Count ?? 0, costs?.Count ?? 0))
            {
                yield return "RM_ContagionMutationExtension breaks the never-upgrade law (allNegative=" + allNegative
                    + ", benefits=" + (benefits?.Count ?? 0) + ", costs=" + (costs?.Count ?? 0) + ")";
            }
            if (weight <= 0f) yield return "RM_ContagionMutationExtension weight must be > 0";
        }
    }

    public class HediffCompProperties_RM_ContagionTouched : HediffCompProperties
    {
        // Severity per 250-tick poll, before the Mod Settings exposure factor. Shipped numbers (INVENTED tuning):
        // a whole day outdoors in the Bloom is ~0.12; a 4000-tick Burn in the open ~0.06; an hour pressed against an
        // Unfinished ~0.1.
        public float bloomDosePerPoll = 0.0005f;
        public float burnDosePerPoll = 0.004f;
        public float contactDosePerPoll = 0.01f;
        // What counts as contact: a pawn standing on or next to a spawned thing of these defs.
        public List<ThingDef> contactSources = new List<ThingDef>();
        // No mutation below this severity (the first brushes are a warning).
        public float minSeverityToMutate = 0.1f;
        // Mean days between mutations at severity 1, before the Mod Settings rate (severity 0.5 -> twice as long).
        public float mtbDaysAtFull = 6f;
        // Mutations a pawn can carry before the condition stops adding more.
        public int mutationCap = 6;
        // The ruled split: share of rolls drawn from the all-negative half.
        public float allNegativeShare = 0.5f;

        public HediffCompProperties_RM_ContagionTouched()
        {
            compClass = typeof(HediffComp_RM_ContagionTouched);
        }
    }

    public class HediffComp_RM_ContagionTouched : HediffComp
    {
        private int ticksToRoll = RM_ContagionSky.Interval;

        public HediffCompProperties_RM_ContagionTouched Props => (HediffCompProperties_RM_ContagionTouched)props;

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            ticksToRoll -= delta;
            if (ticksToRoll > 0) return;
            ticksToRoll = RM_ContagionSky.Interval;
            if (!RM_ContagionSettings.touchedEnabled) return;
            Pawn p = Pawn;
            if (p == null || p.Dead) return;

            float mtb = RM_TouchedKernel.MutationMtbDays(parent.Severity, Props.minSeverityToMutate, Props.mtbDaysAtFull,
                RM_ContagionSettings.touchedMutationRate, RM_ContagionTouchedUtility.MutationsHeld(p), Props.mutationCap);
            if (mtb < 0f) return;
            if (!Rand.MTBEventOccurs(mtb, GenDate.TicksPerDay, RM_ContagionSky.Interval)) return;
            RM_ContagionTouchedUtility.TryMutate(p, Props.allNegativeShare, true);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksToRoll, "rmTouchedTicksToRoll", RM_ContagionSky.Interval);
        }

        public override string CompTipStringExtra
        {
            get
            {
                Pawn p = Pawn;
                if (p == null) return null;
                int held = RM_ContagionTouchedUtility.MutationsHeld(p);
                if (parent.Severity < Props.minSeverityToMutate) return "Not yet changing. Mutations so far: " + held + ".";
                if (held >= Props.mutationCap) return "Mutations so far: " + held + " (no room for more).";
                return "Still changing. Mutations so far: " + held + ". A Helix sunbeam can arrest it.";
            }
        }
    }

    public static class RM_ContagionTouchedUtility
    {
        private static List<Def> deck;

        // Every HediffDef and GeneDef carrying the extension, in load order.
        public static List<Def> Deck
        {
            get
            {
                if (deck == null)
                {
                    deck = new List<Def>();
                    foreach (HediffDef h in DefDatabase<HediffDef>.AllDefsListForReading)
                    {
                        if (h.HasModExtension<RM_ContagionMutationExtension>()) deck.Add(h);
                    }
                    foreach (GeneDef g in DefDatabase<GeneDef>.AllDefsListForReading)
                    {
                        if (g.HasModExtension<RM_ContagionMutationExtension>()) deck.Add(g);
                    }
                }
                return deck;
            }
        }

        public static bool Has(Pawn p, Def card)
        {
            if (card is HediffDef h) return p.health?.hediffSet != null && p.health.hediffSet.HasHediff(h);
            if (card is GeneDef g) return p.genes != null && p.genes.GetGene(g) != null;
            return false;
        }

        public static int MutationsHeld(Pawn p)
        {
            int n = 0;
            List<Def> d = Deck;
            for (int i = 0; i < d.Count; i++)
            {
                if (Has(p, d[i])) n++;
            }
            return n;
        }

        // The part a part-card would grow on, or null for a whole-body card. Sets ok=false when the card needs a part and
        // the pawn has no free one (missing, or already carrying an added part on it or above it).
        private static BodyPartRecord PartFor(Pawn p, RM_ContagionMutationExtension ext, out bool ok)
        {
            ok = true;
            if (ext.installPart == null) return null;
            List<BodyPartRecord> candidates = new List<BodyPartRecord>();
            foreach (BodyPartRecord part in p.health.hediffSet.GetNotMissingParts())
            {
                if (part.def == ext.installPart && !p.health.hediffSet.PartOrAnyAncestorHasDirectlyAddedParts(part)) candidates.Add(part);
            }
            if (candidates.Count == 0) { ok = false; return null; }
            return candidates.RandomElement();
        }

        public static bool Eligible(Pawn p, Def card)
        {
            if (Has(p, card)) return false;
            RM_ContagionMutationExtension ext = card.GetModExtension<RM_ContagionMutationExtension>();
            if (ext == null) return false;
            if (card is GeneDef) return ModsConfig.BiotechActive && p.genes != null;
            if (card is HediffDef)
            {
                PartFor(p, ext, out bool ok);
                return ok;
            }
            return false;
        }

        // One mutation from the ruled 50/50 deck. Returns the card applied, or null when the pawn has room for none.
        public static Def TryMutate(Pawn p, float allNegativeShare, bool notify)
        {
            if (p?.health == null) return null;
            List<Def> d = Deck;
            int n = d.Count;
            List<float> wNeg = new List<float>(n), wMix = new List<float>(n);
            List<bool> eNeg = new List<bool>(n), eMix = new List<bool>(n);
            bool anyNeg = false, anyMix = false;
            for (int i = 0; i < n; i++)
            {
                RM_ContagionMutationExtension ext = d[i].GetModExtension<RM_ContagionMutationExtension>();
                bool el = Eligible(p, d[i]);
                wNeg.Add(ext.weight); wMix.Add(ext.weight);
                eNeg.Add(el && ext.allNegative); eMix.Add(el && !ext.allNegative);
                if (el && ext.allNegative) anyNeg = true;
                if (el && !ext.allNegative) anyMix = true;
            }
            int half = RM_TouchedKernel.Half(RM_TouchedKernel.AllNegative(Rand.Value, allNegativeShare), anyNeg, anyMix);
            if (half < 0) return null;
            int pick = half == 1 ? RM_TouchedKernel.PickWeighted(wNeg, eNeg, Rand.Value) : RM_TouchedKernel.PickWeighted(wMix, eMix, Rand.Value);
            if (pick < 0) return null;
            Def card = d[pick];
            if (!Apply(p, card)) return null;
            if (notify) Notify(p, card);
            return card;
        }

        public static bool Apply(Pawn p, Def card)
        {
            RM_ContagionMutationExtension ext = card.GetModExtension<RM_ContagionMutationExtension>();
            if (ext == null) return false;
            if (card is GeneDef g)
            {
                if (p.genes == null) return false;
                p.genes.AddGene(g, true);
                return true;
            }
            if (card is HediffDef h)
            {
                BodyPartRecord part = PartFor(p, ext, out bool ok);
                if (!ok) return false;
                p.health.AddHediff(h, part);
                return true;
            }
            return false;
        }

        private static void Notify(Pawn p, Def card)
        {
            string text = p.LabelShort + " has been changed by the Contagion: " + card.label + ".\n\n" + card.description
                + "\n\nIt will go on changing until a Helix sunbeam arrests it. Nothing grown is ever undone.";
            if (p.Faction == Faction.OfPlayer || p.IsPrisonerOfColony)
            {
                Find.LetterStack.ReceiveLetter("Contagion mutation: " + p.LabelShort, text, LetterDefOf.NegativeEvent, p);
            }
        }

        public static bool IsTouched(Pawn p)
        {
            return p?.health?.hediffSet != null && p.health.hediffSet.HasHediff(RM_ContagionTouchDefOf.RM_ContagionTouched);
        }

        // Q3: the arrest. Removes the progression only; every grown mutation stays, and nothing protects against the next
        // dose. Returns whether there was anything to arrest.
        public static bool Arrest(Pawn p, string how)
        {
            if (!RM_ContagionSettings.sunbeamArrestEnabled || p?.health?.hediffSet == null) return false;
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(RM_ContagionTouchDefOf.RM_ContagionTouched);
            if (h == null) return false;
            p.health.RemoveHediff(h);
            if (p.Spawned)
            {
                FleckMaker.ThrowLightningGlow(p.DrawPos, p.Map, 1.2f);
                Messages.Message(p.LabelShort + "'s Contagion is arrested " + how + ". What already changed stays, and the next exposure starts it again.",
                    p, MessageTypeDefOf.PositiveEvent);
            }
            return true;
        }

        // Who the Contagion can touch: a living, fleshy, humanlike pawn that is not itself a Contagion native.
        public static bool CanBeTouched(Pawn p)
        {
            return p != null && !p.Dead && p.RaceProps != null && p.RaceProps.Humanlike && p.RaceProps.IsFlesh
                && p.health != null && !RM_ContagionSky.IsNative(p);
        }
    }

    // N4 exposure. Every 250 ticks on every map: the Bloom and Burn doses only on a map whose biome carries the sky
    // extension (never on another biome: the Undersurge lesson), contact anywhere a contact source stands.
    public class RM_MapComponent_ContagionTouch : MapComponent
    {
        public RM_MapComponent_ContagionTouch(Map map) : base(map) { }

        private static readonly List<Thing> tmpSources = new List<Thing>();
        private static readonly List<Pawn> tmpPawns = new List<Pawn>();

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % RM_ContagionSky.Interval != 0) return;
            if (!RM_ContagionSettings.touchedEnabled || RM_ContagionSettings.touchedExposureFactor <= 0f) return;
            HediffDef touched = RM_ContagionTouchDefOf.RM_ContagionTouched;
            HediffCompProperties_RM_ContagionTouched props = touched.CompProps<HediffCompProperties_RM_ContagionTouched>();
            if (props == null) return;

            RM_ContagionSkyExtension ext = RM_ContagionSky.ExtFor(map);
            bool burnSky = false, bloomSky = false;
            if (ext != null)
            {
                RM_MapComponent_ContagionSky sky = map.GetComponent<RM_MapComponent_ContagionSky>();
                burnSky = sky != null && sky.BurnActive && map.weatherManager.curWeather == RM_ContagionSkyDefOf.RM_ContagionBurn;
                bloomSky = !burnSky && map.weatherManager.curWeather == RM_ContagionSkyDefOf.RM_ContagionBloom;
            }

            tmpSources.Clear();
            for (int i = 0; i < props.contactSources.Count; i++)
            {
                tmpSources.AddRange(map.listerThings.ThingsOfDef(props.contactSources[i]));
            }
            if (!burnSky && !bloomSky && tmpSources.Count == 0) return;

            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllHumanlikeSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (!RM_ContagionTouchedUtility.CanBeTouched(p)) continue;
                bool exposed = (burnSky || bloomSky) && RM_ContagionSky.Exposed(p.Position, map);
                bool contact = InContact(p);
                float dose = RM_TouchedKernel.Dose(true, exposed, bloomSky, burnSky, contact, props.bloomDosePerPoll,
                    props.burnDosePerPoll, props.contactDosePerPoll, RM_ContagionSettings.touchedExposureFactor);
                if (dose > 0f) HealthUtility.AdjustSeverity(p, touched, dose);
            }
            tmpPawns.Clear();
            tmpSources.Clear();
        }

        private static bool InContact(Pawn p)
        {
            for (int j = 0; j < tmpSources.Count; j++)
            {
                Thing s = tmpSources[j];
                if (s == p || !s.Spawned) continue;
                if (s is Pawn sp && sp.Dead) continue;
                if (s.OccupiedRect().ExpandedBy(1).Contains(p.Position)) return true;
            }
            return false;
        }
    }

    [DefOf]
    public static class RM_ContagionTouchDefOf
    {
        public static HediffDef RM_ContagionTouched;
        public static JobDef RM_SunbeamArrest;
        public static ThingDef RM_Sunbeam;
        public static DamageDef RM_UVBeam;
        public static ThingDef RM_ContagionMulch;

        static RM_ContagionTouchDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ContagionTouchDefOf));
        }
    }
}
