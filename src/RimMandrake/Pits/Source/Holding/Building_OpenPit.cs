using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pits
{
    // The pit itself, sections 2/3/4 of covered_pit_traps_spec.md. One class,
    // covered or uncovered:
    //   - UNCOVERED: an obvious hole (own def graphic via base.Print).
    //   - COVERED (armed): prints as the surrounding terrain
    //     (TerrainMimicPrinter, verified in Spikes/Spike1) and carries a
    //     CompPitCoverTrigger that sums standing mass every scan and springs
    //     the trap.
    // "Fitting family, one framework five faces" (section 5) is an optional
    // CompPitFitting read here, not a subclass.
    //
    // SCOPE CUT, flagged rather than guessed: def.passability is a per-Def
    // field (Verse/BuildableDef.cs), not overridable per-instance, so it
    // cannot be toggled between covered and uncovered on the SAME Thing. All
    // pit ThingDefs are Standable (matching vanilla TrapSpike's own
    // convention - a trap must be walkable to be triggered), which means an
    // UNCOVERED pit is walkable too: there is no accidental-fall-while-
    // uncovered mechanic in this build. Only a SPRUNG covered trap captures
    // anyone. A "walking into an obvious open hole" hazard would need either
    // a second ThingDef swapped in on uncover, or a Tick-based fall check on
    // the uncovered state - neither is built here; flagged as an open item.
    //
    // Further scope cuts, flagged rather than guessed (see item file):
    //   - Multi-occupant DRAWING: IThingHolderWithDrawnPawn (the verified
    //     Building_HoldingPlatform/Spike2 precedent) draws exactly ONE pawn.
    //     A 2x2 pit that holds two per spec section 6 draws only the first;
    //     the second is held (saved, escapes, takes damage) but not rendered
    //     until the first vacates. Multi-pawn rendering was not attempted -
    //     it has no verified-in-source precedent to build on.
    //   - Overflow beyond MaxOccupants on a single Spring() is not capped;
    //     everyone who was standing on the cover when it triggers is added.
    //     The cover's own mass rating is the intended crowd-control knob.
    //   - "Spoil hauled out" / cover-material cost: not modeled (see
    //     CompPitDigStage) - Arm Cover gizmos below are free/instant for the
    //     same reason: no spec'd recipe or defName to build one against.
    public class Building_OpenPit : Building, IThingHolderWithDrawnPawn, IThingHolder
    {
        public const float FallDamagePerMassKg = 0.08f;
        private const float SunkenYOffset = -0.05f;

        public ThingOwner innerContainer;
        public bool covered;
        public PitDepthTier DepthTier = PitDepthTier.Shallow;
        public PitCoverTier CoverTier = PitCoverTier.None;

        public bool Covered => covered;
        public bool Sprung => innerContainer != null && innerContainer.Count > 0;
        public int OccupantCount => innerContainer == null ? 0 : innerContainer.Count;

        public int MaxOccupants
        {
            get
            {
                int area = def.size.x * def.size.z;
                if (area >= 4) return 2;
                return 1;
            }
        }

        public Pawn HeldPawn
        {
            get
            {
                if (innerContainer == null) return null;
                for (int i = 0; i < innerContainer.Count; i++)
                {
                    if (innerContainer[i] is Pawn p) return p;
                }
                return null;
            }
        }

        public Building_OpenPit()
        {
            innerContainer = new ThingOwner<Thing>(this, oneStackOnly: false);
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (innerContainer == null)
            {
                innerContainer = new ThingOwner<Thing>(this, oneStackOnly: false);
            }
        }

        public override void Print(SectionLayer layer)
        {
            // Camouflage only applies to a def that is actually an armed
            // trap (carries CompPitCoverTrigger). Building_PitCell (the
            // known, gated prisoner pit - no trigger comp) always shows its
            // own def graphic; there is nothing to hide.
            if (covered && GetComp<CompPitCoverTrigger>() != null)
            {
                TerrainMimicPrinter.PrintTerrainMimic(this, layer);
            }
            else
            {
                base.Print(layer);
            }
        }

        // IThingHolderWithDrawnPawn - draws the first occupant, sunken below
        // the cover surface (see class doc: multi-occupant drawing is unbuilt).
        public float HeldPawnDrawPos_Y => DrawPos.y + SunkenYOffset;
        public float HeldPawnBodyAngle => Rotation.AsAngle;
        public PawnPosture HeldPawnPosture => PawnPosture.LayingOnGroundFaceUp;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public ThingOwner GetDirectlyHeldThings() => innerContainer;

        // --- Arming ---------------------------------------------------

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;

            // Cover arm/disarm UI only makes sense on a def that actually
            // carries the mass-trigger comp - Building_PitCell (the gated
            // prisoner variant, no CompPitCoverTrigger) supplies its own
            // gate gizmos instead of these.
            if (GetComp<CompPitCoverTrigger>() != null)
            {
                if (!covered && !Sprung)
                {
                    yield return ArmGizmo(PitCoverTier.WovenScrap, "RMPits_ArmWovenScrap");
                    yield return ArmGizmo(PitCoverTier.PlankLattice, "RMPits_ArmPlankLattice");
                    yield return ArmGizmo(PitCoverTier.ReinforcedFrame, "RMPits_ArmReinforcedFrame");
                }
                else if (covered)
                {
                    yield return new Command_Action
                    {
                        defaultLabel = "RMPits_Uncover".Translate(),
                        defaultDesc = "RMPits_UncoverDesc".Translate(),
                        icon = TexCommand.ForbidOff,
                        action = delegate { ClearCover(); },
                    };
                }
            }

            CompPitFitting fitting = GetComp<CompPitFitting>();
            if (fitting != null)
            {
                foreach (Gizmo g in fitting.GetIgniteGizmo(this)) yield return g;
            }

            // Without this, the only way an occupant leaves is a random struggle
            // roll (RunStruggleInterval) -- there was no player-facing way to pull
            // someone out at all.
            if (Sprung)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RMPits_Release".Translate(),
                    defaultDesc = "RMPits_ReleaseDesc".Translate(),
                    icon = TexCommand.ForbidOff, // placeholder icon; art pass owed
                    action = delegate
                    {
                        Pawn p = HeldPawn;
                        if (p != null) EjectPawn(p);
                    },
                };
            }
        }

        private Command_Action ArmGizmo(PitCoverTier tier, string labelKey)
        {
            return new Command_Action
            {
                defaultLabel = labelKey.Translate(),
                defaultDesc = "RMPits_ArmCoverDesc".Translate(tier.TriggerMassKg()),
                icon = TexCommand.ForbidOff,
                action = delegate { SetCover(tier); },
            };
        }

        // Arming and disarming as METHODS, not gizmo-lambda bodies: a gizmo
        // body is unreachable from anything but a human clicking it, and the
        // mass-trigger matrix has to be driven from the bridge (see
        // Debug/PitDebugActions.cs). Same code path either way.
        public void SetCover(PitCoverTier tier)
        {
            CoverTier = tier;
            covered = true;
            DirtyMapMesh();
        }

        public void ClearCover()
        {
            covered = false;
            CoverTier = PitCoverTier.None;
            DirtyMapMesh();
        }

        // 🔴 MUST include MapMeshFlagDefOf.Things. This was Buildings ALONE, and
        // measured live 2026-08-30 the terrain-mimic never appeared: arming three
        // pits left them drawing their own def graphic, identical to the two
        // uncovered controls beside them. A Thing's own Print() output lives in
        // the section layer dirtied by Things (Verse/Thing.cs DirtyMapMesh);
        // Buildings dirties the linked/buildings layers instead, so the section
        // was never regenerated and the pre-arm print stayed on screen. Both
        // flags are sent because a pit is also a Building.
        protected void DirtyMapMesh()
        {
            Map?.mapDrawer.MapMeshDirty(Position,
                (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
        }

        // --- Springing --------------------------------------------------

        // Called by CompPitCoverTrigger once summed mass on the cover crosses
        // the armed tier's rating. Section 4: "Fall deals mass-scaled blunt
        // damage + a Pinned-in-Pit state."
        public void Spring(List<Pawn> fallers)
        {
            Map map = Map;
            if (map == null) return;

            covered = false;
            DirtyMapMesh();

            CompPitFitting fitting = GetComp<CompPitFitting>();
            foreach (Pawn p in fallers)
            {
                if (p == null || p.Dead || p.Destroyed) continue;

                float fallDamage = Mathf.Max(1f, p.GetStatValue(StatDefOf.Mass) * FallDamagePerMassKg);
                p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, fallDamage));
                if (p.Dead || p.Destroyed) continue;

                HealthUtility.AdjustSeverity(p, RMPits_HediffDefOf.RM_PinnedInPit, 0.1f);

                if (p.Spawned) p.DeSpawn(DestroyMode.Vanish);
                innerContainer.TryAddOrTransfer(p);

                fitting?.OnCapture(p, map, Position);
            }
        }

        // --- Struggle escape ----------------------------------------------

        protected override void Tick()
        {
            base.Tick();
            // A pawn moved into innerContainer is despawned, which removes it from
            // the map's own tick lists -- vanilla Building_Casket.Tick() ticks its
            // contents for exactly this reason. Without this, a held pawn's
            // needs/hediffs/health never advance: exposure never reaches
            // heatstroke, hunger never drops, bleeding never progresses.
            innerContainer.DoTick();
            if (Sprung && this.IsHashIntervalTick(PitEscapeUtility.StruggleIntervalTicks))
            {
                RunStruggleInterval();
            }
        }

        // Without this, Thing.Destroy (a mortar hit, melee, fire -- the pit is
        // useHitPoints, not deconstructible) drops the held pawn on nobody:
        // Thing.Destroy does not walk IThingHolder contents, so an occupant is
        // never spawned, never killed, never sent to world pawns. It just stops
        // existing.
        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            IntVec3 pos = Position;
            if (map != null && innerContainer != null && innerContainer.Count > 0)
            {
                innerContainer.TryDropAll(pos, map, ThingPlaceMode.Near);
            }
            base.Destroy(mode);
        }

        // Building_PitCell overrides this to true while its gate is closed -
        // a closed gate is a physical barrier, not just a hard escape roll,
        // so a held pawn should not even attempt (or be charged a failed-
        // attempt cost for) an escape while it holds.
        protected virtual bool EscapeBlocked => false;

        internal void RunStruggleInterval()
        {
            if (EscapeBlocked) return;

            CompPitFitting fitting = GetComp<CompPitFitting>();
            List<Pawn> occupants = new List<Pawn>();
            for (int i = 0; i < innerContainer.Count; i++)
            {
                if (innerContainer[i] is Pawn p) occupants.Add(p);
            }

            foreach (Pawn p in occupants)
            {
                if (p.Dead) continue;

                fitting?.OnStruggleInterval(p);
                if (fitting != null && fitting.BlocksEscape) continue;

                float chance = PitEscapeUtility.EscapeChance(p, DepthTier);
                if (Rand.Chance(chance))
                {
                    EjectPawn(p);
                }
                else
                {
                    PitEscapeUtility.ApplyFailedAttemptCost(p);
                }
            }
        }

        public void EjectPawn(Pawn p)
        {
            if (innerContainer == null || !innerContainer.Contains(p)) return;
            Map map = Map;
            if (map == null) return;

            innerContainer.Remove(p);
            IntVec3 spawnCell = CellFinder.RandomClosewalkCellNear(Position, map, 2);
            if (!spawnCell.IsValid) spawnCell = Position;
            GenSpawn.Spawn(p, spawnCell, map);

            Hediff pinned = p.health?.hediffSet?.GetFirstHediffOfDef(RMPits_HediffDefOf.RM_PinnedInPit);
            if (pinned != null) p.health.RemoveHediff(pinned);
        }

        public override string GetInspectString()
        {
            string baseString = base.GetInspectString();
            string status = covered
                ? "RMPits_InspectArmed".Translate(CoverTier.ToString(), CoverTier.TriggerMassKg())
                : "RMPits_InspectOpen".Translate();
            string occupants = Sprung ? "RMPits_InspectOccupants".Translate(innerContainer.Count, MaxOccupants) : null;

            string result = status;
            if (occupants != null) result += "\n" + occupants;
            if (!baseString.NullOrEmpty()) result = baseString + "\n" + result;
            return result;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref innerContainer, "innerContainer", this);
            Scribe_Values.Look(ref covered, "covered", false);
            Scribe_Values.Look(ref DepthTier, "depthTier", PitDepthTier.Shallow);
            Scribe_Values.Look(ref CoverTier, "coverTier", PitCoverTier.None);
        }
    }
}
