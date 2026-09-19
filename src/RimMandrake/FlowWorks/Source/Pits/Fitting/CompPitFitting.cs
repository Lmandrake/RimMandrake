using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
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
                        HealthUtility.AdjustSeverity(p, RMPits_HediffDefOf.RM_PitDrowning,
                            Props.drowningSeverityPerInterval);
                    }
                    break;
            }
        }

        // ════════════════════════════════════════════════════════════════
        // "No climbing out at all" (spec section 5). Building_OpenPit asks this
        // before running PitEscapeUtility.
        //
        // FLOWWORKS PHASE 5 — THIS NOW DERIVES FROM THE LIQUID THAT IS ACTUALLY
        // IN THE CELL, not from a hardcoded enum value. A pit is a SUPERDEEP
        // excavation (ruling 18), the depth engine owns what liquid is in one and
        // how much, and FluidDef.ticksPerTile IS the viscosity field — "Viscosity
        // is ticksPerTile (already a real per-fluid field)". Tar should hold a
        // pawn harder than water does, and that should not need a seventh enum
        // member per liquid the registry ever adds.
        //
        // 🔑 EXTENDED, NOT FORKED, and calibrated so nothing that shipped moves:
        //   • The threshold defaults to 60, which is exactly RM_Fluid_Water's own
        //     shipped ticksPerTile — so water still blocks, which is the whole of
        //     the behaviour the Water enum member expressed.
        //   • A cell with no liquid in it (fill 0), or a pit standing on ground
        //     the depth engine has no entry for at all — every pit built by the
        //     Pits dig-site chain today — falls through to the ORIGINAL enum
        //     test. RM_OpenPit_Water behaves precisely as it always has.
        // ════════════════════════════════════════════════════════════════
        public bool BlocksEscape
        {
            get
            {
                FluidDef liquid = OccupyingLiquid();
                if (liquid != null)
                {
                    return liquid.ticksPerTile >= Props.escapeBlockingViscosityTicks;
                }
                return Props.fittingType == PitFittingType.Water;
            }
        }

        /// <summary>The liquid standing in this pit's own cell, or null when the
        /// cell is dry or the depth engine does not own it.</summary>
        private FluidDef OccupyingLiquid()
        {
            Map map = parent?.Map;
            if (map == null)
            {
                return null;
            }
            RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
            if (engine == null || !engine.IsExcavated(parent.Position))
            {
                return null;
            }
            return engine.FillAt(parent.Position) > 0 ? engine.ActiveFluid : null;
        }

        private bool CanSwim(Pawn p)
        {
            // AQUATIC_WATER_BREATHING_GENE_1: a gene declaring immunity to our own
            // RM_PitDrowning hediff means the pawn does not drown here, regardless
            // of species or swim art. Vanilla public API
            // (ImmunityHandler.AnyGeneMakesFullyImmuneTo) - references no
            // StarWarsRaces def, so any current or future gene/mod can opt in this
            // way with zero cross-mod dependency in either direction. Checked ahead
            // of the swim-art heuristics below because WaterCellCost alone (the
            // *swim* signal, e.g. WebbedPhalanges) does not imply immunity to
            // drowning - only a gene that actually declares makeImmuneTo does.
            if (p?.health?.immunity != null
                && p.health.immunity.AnyGeneMakesFullyImmuneTo(RMPits_HediffDefOf.RM_PitDrowning))
            {
                return true;
            }
            // No vanilla "aquatic" RaceProperties flag exists to key this off,
            // and confirmed (2026-09-02) that no vanilla BodyDef defName contains
            // "aquatic" either - so the substring heuristic below was previously
            // matching nothing at all, ever, for any real race in the game.
            //
            // Vanilla itself has a real per-life-stage swim signal, just not on
            // RaceProperties/BodyDef: Pawn.DrawNonHumanlikeSwimmingGraphic
            // (Verse/Pawn.cs) decides whether to render the swimming sprite by
            // checking ageTracker.CurKindLifeStage.swimmingGraphicData != null -
            // e.g. Seal/SeaLion set this on their PawnKindDef life stages. Use
            // the same signal here as the primary check. CurKindLifeStage logs
            // an error and returns null for humanlike pawns (Pawn_AgeTracker.cs),
            // so it's gated behind !Humanlike. The old naming-convention
            // substring check is kept as a secondary OR for any modded race that
            // opts in that way without wiring up real swim art.
            if (p?.RaceProps != null && !p.RaceProps.Humanlike
                && p.ageTracker?.CurKindLifeStage?.swimmingGraphicData != null)
            {
                return true;
            }
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
