using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Pits
{
    // The gated prisoner pit, section 6 of covered_pit_traps_spec.md: "We
    // don't fight [the room/bed prisoner system] - we use the Anomaly
    // holding-platform pattern." Reuses Building_OpenPit's holder/struggle
    // machinery wholesale (assignment/entry is manual here, not sprung by a
    // mass trigger - no CompPitCoverTrigger on this def).
    //
    // "covered" is repurposed as GATE CLOSED, per the owner's severity
    // ruling (section 6, ruled 2026-08-30): "the COVER is the mercy... a fed
    // and tended pit is a legitimate long-term hold. Uncovered = actively
    // harsh... a captive left open to the sky degrades fast." Implemented as
    // RM_PitExposure severity accruing only while the gate is open.
    //
    // OPEN QUESTIONS, flagged rather than guessed (see item file - these are
    // the exact points Spikes/Spike2_PitCellHolding.cs's own README already
    // marked "unproven until runtime"):
    //   - Prisoner INTAKE job: there is no JobDriver here that carries a
    //     downed/captured pawn into the cell. Assignment below only marks
    //     intent (AssignedPrisoner); moving them in is a player-triggered
    //     stand-in (RM_PlaceInPitCell gizmo, teleports for now) pending a
    //     real carry-to-holder JobDriver modeled on JobDriver_CarryToEntityHolder.
    //   - FEEDING: the Feed gizmo is a direct stand-in (restores the held
    //     pawn's food need instantly) - not a real feed-through-the-gate job.
    //   - Recruit-from-pit / emancipation rite: campaign-layer content
    //     (theology, quest-shaped), out of scope for this species-agnostic
    //     core mod per spec section 9.
    public class Building_PitCell : Building_OpenPit
    {
        public Pawn AssignedPrisoner;

        public bool GateClosed => covered;

        // No Print override needed: Building_OpenPit.Print already only
        // camouflages a def carrying CompPitCoverTrigger, which this def
        // never does - it always shows its own def graphic.

        protected override void Tick()
        {
            base.Tick();
            if (this.IsHashIntervalTick(250))
            {
                ApplyExposure();
            }
        }

        private void ApplyExposure()
        {
            Pawn held = HeldPawn;
            if (held == null || held.Dead) return;

            if (!GateClosed)
            {
                // Uncovered = actively harsh: the unsetting sun beats straight
                // down. Placeholder severity rate - the spec names the
                // direction and the theology feed (campaign layer), not a
                // tuned number.
                HealthUtility.AdjustSeverity(held, RMPits_HediffDefOf.RM_PitExposure, 0.01f);
            }
            else
            {
                // The cover is the mercy: exposure recedes while closed.
                HealthUtility.AdjustSeverity(held, RMPits_HediffDefOf.RM_PitExposure, -0.02f);
            }
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;

            yield return new Command_Action
            {
                defaultLabel = GateClosed ? "RMPits_OpenGate".Translate() : "RMPits_CloseGate".Translate(),
                defaultDesc = "RMPits_ToggleGateDesc".Translate(),
                icon = TexCommand.ForbidOff,
                action = delegate { covered = !covered; DirtyMapMesh(); },
            };

            if (AssignedPrisoner == null)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RMPits_AssignPrisoner".Translate(),
                    defaultDesc = "RMPits_AssignPrisonerDesc".Translate(),
                    icon = TexCommand.ForbidOff,
                    action = OpenAssignMenu,
                };
            }
            else if (HeldPawn == null && AssignedPrisoner.Spawned)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RMPits_PlaceInPitCell".Translate(),
                    defaultDesc = "RMPits_PlaceInPitCellDesc".Translate(),
                    icon = TexCommand.ForbidOff,
                    action = () => PlaceAssignedInCell(),
                };
            }

            if (HeldPawn != null)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RMPits_FeedCaptive".Translate(),
                    defaultDesc = "RMPits_FeedCaptiveDesc".Translate(),
                    icon = TexCommand.ForbidOff,
                    action = FeedHeldPawn,
                };
            }
        }

        private void OpenAssignMenu()
        {
            Map map = Map;
            if (map == null) return;

            List<Pawn> candidates = map.mapPawns.PrisonersOfColonySpawned
                .Where(p => !p.Dead)
                .ToList();

            List<FloatMenuOption> options = new List<FloatMenuOption>();
            foreach (Pawn p in candidates)
            {
                Pawn captured = p;
                options.Add(new FloatMenuOption(captured.LabelShortCap, () => AssignedPrisoner = captured));
            }
            if (options.Count == 0)
            {
                options.Add(new FloatMenuOption("RMPits_NoEligiblePrisoners".Translate(), null));
            }
            Find.WindowStack.Add(new FloatMenu(options));
        }

        internal void PlaceAssignedInCell()
        {
            Pawn p = AssignedPrisoner;
            if (p == null || !p.Spawned || Map == null) return;

            if (p.Spawned) p.DeSpawn(DestroyMode.Vanish);
            innerContainer.TryAddOrTransfer(p);
            HealthUtility.AdjustSeverity(p, RMPits_HediffDefOf.RM_PinnedInPit, 0.1f);
        }

        internal void FeedHeldPawn()
        {
            Pawn p = HeldPawn;
            if (p?.needs?.food == null) return;
            p.needs.food.CurLevel = p.needs.food.MaxLevel;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref AssignedPrisoner, "assignedPrisoner");
        }
    }
}
