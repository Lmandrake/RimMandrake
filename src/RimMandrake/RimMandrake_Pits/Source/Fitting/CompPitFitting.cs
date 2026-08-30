using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Pits
{
    // The fitting family's actual behavior. Section 5 of
    // covered_pit_traps_spec.md gives each variant's THEME (what it is /
    // what it feeds theologically) but not exact numbers - the damage/
    // severity constants here are CompProperties_PitFitting fields,
    // deliberately placeholder-tunable, not hardcoded, so the quicktest
    // matrix and a later balance pass can retune per-def without touching
    // this class.
    //
    // Absent from v1 (flagged, not guessed): the Baited variant (spec calls
    // it a bait SLOT on the cover, HAZN loop pattern - that is a refuel/bait
    // comp this codebase already has a precedent for in the HAZN mod, and
    // wiring to it is a cross-mod dependency decision, not a core-framework
    // one). Bare capture (no comp needed - absence of CompPitFitting IS the
    // bare pit) needs no class at all.
    public class CompPitFitting : ThingComp
    {
        public bool soaked; // Oiled: set true once fallen-into; enables the Ignite gizmo

        public CompProperties_PitFitting Props => (CompProperties_PitFitting)props;

        // Called once by Building_OpenPit.Spring() for every pawn that just fell in.
        public void OnCapture(Pawn p, Map map, IntVec3 cell)
        {
            switch (Props.fittingType)
            {
                case PitFittingType.Spiked:
                    p.TakeDamage(new DamageInfo(DamageDefOf.Stab, Props.spikeDamage));
                    break;
                case PitFittingType.Oiled:
                    soaked = true;
                    break;
                case PitFittingType.Oubliette:
                    if (p.RaceProps.IsMechanoid || p.RaceProps.FleshType == FleshTypeDefOf.Mechanoid)
                    {
                        p.TakeDamage(new DamageInfo(DamageDefOf.EMP, Props.oublietteEmpDamage));
                    }
                    break;
                    // Bare, Poison, Water: no on-capture effect; Poison/Water apply over time.
            }
        }

        // Called by Building_OpenPit.Tick() on the same struggle interval as
        // the escape check, for every currently-held pawn.
        public void OnStruggleInterval(Pawn p)
        {
            switch (Props.fittingType)
            {
                case PitFittingType.Poison:
                    HealthUtility.AdjustSeverity(p, HediffDefOf.ToxicBuildup, Props.poisonSeverityPerInterval);
                    break;
                case PitFittingType.Water:
                    // Drowning severity IS the damage clock (see Defs/HediffDefs/Pit_Hediffs.xml
                    // stages) rather than a separate TakeDamage call, so a tended/rescued pawn's
                    // drowning progress can be read back like any other hediff.
                    if (!CanSwim(p))
                    {
                        HealthUtility.AdjustSeverity(p, RMPits_HediffDefOf.RM_PitDrowning, 1f);
                    }
                    break;
            }
        }

        // Water pits never allow the struggle-escape roll at all (spec section 5:
        // "no climbing out at all"). Building_OpenPit asks this before running
        // PitEscapeUtility.
        public bool BlocksEscape => Props.fittingType == PitFittingType.Water;

        private bool CanSwim(Pawn p)
        {
            // No vanilla "aquatic" RaceProperties flag was found in-source to key
            // this off; PawnUtility/RaceProperties expose no such field. Rather
            // than invent one, this is a naming-convention heuristic
            // (defName/label contains a marker) that quietly does nothing for
            // any race that does not opt in - flagged as an open question in
            // the item file, not a resolved mechanic.
            return p.RaceProps?.body?.defName != null && p.RaceProps.body.defName.ToLowerInvariant().Contains("aquatic");
        }

        public IEnumerable<Gizmo> GetIgniteGizmo(Building_OpenPit pit)
        {
            if (Props.fittingType == PitFittingType.Oiled && soaked && pit.Sprung)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RMPits_IgnitePit".Translate(),
                    defaultDesc = "RMPits_IgnitePitDesc".Translate(),
                    icon = TexCommand.Attack,
                    action = delegate
                    {
                        Map map = pit.Map;
                        if (map == null) return;
                        FireUtility.TryStartFireIn(pit.Position, map, 1f, pit);
                    },
                };
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref soaked, "soaked", false);
        }
    }
}
