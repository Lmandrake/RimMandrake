using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// The tank.
    ///
    /// Chassis: Building_Enterable, the vanilla abstract behind the growth vat, gene extractor
    /// and subcore scanner. It is an ISuspendableThingHolder holding the occupant in
    /// innerContainer; we override IsContentsSuspended => false so the occupant keeps ticking
    /// and CompBactaImmersion has something to heal.
    ///
    /// The visible suspended pawn is vanilla: IThingHolderWithDrawnPawn plus a
    /// DynamicDrawPhaseAt override, which is RimWorld 1.6's own route to exactly the effect the
    /// BioReactor (Continued) mod (MIT, github.com/emipa606/BioReactor) hand-rolls with
    /// RenderPawnAt and a downedAngle poke. Same picture, no Harmony, no reflection, and the
    /// engine owns the posture and the render cache. CompBactaShell draws the glass over the
    /// pawn; CompBactaImmersion draws the fluid column between them.
    /// </summary>
    [StaticConstructorOnStartup]
    public class Building_BactaTank : Building_Enterable, IThingHolderWithDrawnPawn, IThingHolder
    {
        [Unsaved(false)]
        private CompPowerTrader cachedPowerComp;

        [Unsaved(false)]
        private CompBactaImmersion cachedImmersionComp;

        [Unsaved(false)]
        private static Texture2D cachedInsertPawnTex;

        /// <summary>
        /// Needs held where they were when the pawn went in. A pawn can be in here for days
        /// while a scar is erased; without this it starves or collapses from exhaustion inside
        /// a machine that is supposed to be saving it. The tank feeds and rests its occupant
        /// (the fluid is nutrient-bearing and the harness takes the weight) — neutral on needs,
        /// never a free meal, and switchable off in settings.
        /// </summary>
        private float frozenFood = -1f;

        private float frozenRest = -1f;

        private static readonly Texture2D CancelIcon = ContentFinder<Texture2D>.Get("UI/Designators/Cancel");

        private static readonly Texture2D EjectIcon = ContentFinder<Texture2D>.Get("UI/Commands/PodEject");

        public Pawn ContainedPawn => innerContainer.FirstOrDefault() as Pawn;

        /// <summary>The occupant must tick, or nothing heals. This is the whole point.</summary>
        public override bool IsContentsSuspended => false;

        public CompPowerTrader PowerTraderComp
        {
            get
            {
                if (cachedPowerComp == null)
                {
                    cachedPowerComp = this.TryGetComp<CompPowerTrader>();
                }
                return cachedPowerComp;
            }
        }

        public CompBactaImmersion ImmersionComp
        {
            get
            {
                if (cachedImmersionComp == null)
                {
                    cachedImmersionComp = GetComp<CompBactaImmersion>();
                }
                return cachedImmersionComp;
            }
        }

        public bool PowerOn => PowerTraderComp == null || PowerTraderComp.PowerOn;

        public static Texture2D InsertPawnTex
        {
            get
            {
                if (cachedInsertPawnTex == null)
                {
                    cachedInsertPawnTex = ContentFinder<Texture2D>.Get("UI/Gizmos/InsertPawn");
                }
                return cachedInsertPawnTex;
            }
        }

        // ---- IThingHolderWithDrawnPawn --------------------------------------------------
        // Values copied from Building_GeneExtractor, which holds a humanlike upright-cylinder
        // pawn the same way. HeldPawnDrawPos_Y lifts the pawn just off the building mesh.
        public float HeldPawnDrawPos_Y => DrawPos.y + 0.03658537f;

        public float HeldPawnBodyAngle => base.Rotation.Opposite.AsAngle;

        public PawnPosture HeldPawnPosture => PawnPosture.LayingOnGroundFaceUp;

        /// <summary>A slow bob, so the suspended pawn reads as floating rather than pasted on.</summary>
        public override Vector3 PawnDrawOffset => CompBiosculpterPod.FloatingOffset(Find.TickManager.TicksGame);

        protected override void Tick()
        {
            base.Tick();

            if (this.IsHashIntervalTick(250) && PowerTraderComp != null)
            {
                bool busy = ContainedPawn != null;
                PowerTraderComp.PowerOutput = busy
                    ? (0f - PowerTraderComp.Props.PowerConsumption)
                    : (0f - PowerTraderComp.Props.idlePowerDraw);
            }

            Pawn pawn = ContainedPawn;
            if (pawn == null)
            {
                frozenFood = -1f;
                frozenRest = -1f;
                if (selectedPawn != null && selectedPawn.Dead)
                {
                    CancelLoad();
                }
                return;
            }

            if (pawn.Dead)
            {
                // Revival of the recently dead is BACTA_REVIVAL_MECHANIC_1, not this item.
                // Here a death in the tank simply ends the immersion.
                EjectOccupant("RSW_BactaTankEjectedDead", MessageTypeDefOf.NegativeEvent);
                return;
            }

            HoldNeedsSteady(pawn);
        }

        /// <summary>
        /// Pins food and rest to where they were on entry. Called every tick rather than on the
        /// 250-tick heal pass because the needs tick every tick and a visible sawtooth in the
        /// needs bar would look like a bug.
        /// </summary>
        private void HoldNeedsSteady(Pawn pawn)
        {
            if (!BactaSettings.suspendNeedsEnabled || pawn.needs == null)
            {
                return;
            }

            if (pawn.needs.food != null)
            {
                if (frozenFood < 0f)
                {
                    frozenFood = pawn.needs.food.CurLevel;
                }
                pawn.needs.food.CurLevel = frozenFood;
            }

            if (pawn.needs.rest != null)
            {
                if (frozenRest < 0f)
                {
                    frozenRest = pawn.needs.rest.CurLevel;
                }
                pawn.needs.rest.CurLevel = frozenRest;
            }
        }

        public override AcceptanceReport CanAcceptPawn(Pawn pawn)
        {
            if (pawn == null || !pawn.RaceProps.IsFlesh)
            {
                // Bacta is a bacterial culture working on living tissue. A droid or a mech
                // gets nothing out of it.
                return false;
            }
            if (!pawn.IsColonist && !pawn.IsSlaveOfColony && !pawn.IsPrisonerOfColony
                && !(pawn.RaceProps.Animal && pawn.Faction == Faction.OfPlayer))
            {
                return false;
            }
            if (pawn.IsQuestLodger())
            {
                return false;
            }
            if (selectedPawn != null && selectedPawn != pawn)
            {
                return false;
            }
            if (innerContainer.Count > 0)
            {
                return "Occupied".Translate();
            }
            if (!PowerOn)
            {
                return "NoPower".Translate().CapitalizeFirst();
            }
            if (ImmersionComp != null && !ImmersionComp.HasFluid)
            {
                return "RSW_BactaTankReportNoFluid".Translate();
            }
            return true;
        }

        public override void TryAcceptPawn(Pawn pawn)
        {
            if (!(bool)CanAcceptPawn(pawn))
            {
                return;
            }

            selectedPawn = pawn;
            bool wasSelected = pawn.DeSpawnOrDeselect();
            if (innerContainer.TryAddOrTransfer(pawn))
            {
                startTick = Find.TickManager.TicksGame;
                frozenFood = -1f;
                frozenRest = -1f;
            }
            if (wasSelected)
            {
                Find.Selector.Select(pawn, playSound: false, forceDesignatorDeselect: false);
            }
        }

        /// <summary>
        /// Drops the occupant out and clears the immersion state. <paramref name="messageKey"/>
        /// may be null for a silent (player-ordered) eject.
        /// </summary>
        public void EjectOccupant(string messageKey, MessageTypeDef messageType)
        {
            Pawn pawn = ContainedPawn;
            startTick = -1;
            selectedPawn = null;
            frozenFood = -1f;
            frozenRest = -1f;

            if (!Spawned)
            {
                return;
            }

            innerContainer.TryDropAll(def.hasInteractionCell ? InteractionCell : base.Position,
                base.Map, ThingPlaceMode.Near);

            if (pawn != null && !messageKey.NullOrEmpty())
            {
                Messages.Message(messageKey.Translate(pawn.Named("PAWN")), pawn,
                    messageType ?? MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }

        private void CancelLoad()
        {
            if (selectedPawn != null && selectedPawn.CurJobDef == JobDefOf.EnterBuilding)
            {
                selectedPawn.jobs.EndCurrentJob(JobCondition.InterruptForced);
            }
            selectedPawn = null;
            startTick = -1;
            if (Spawned)
            {
                innerContainer.TryDropAll(base.Position, base.Map, ThingPlaceMode.Near);
            }
        }

        public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption option in base.GetFloatMenuOptions(selPawn))
            {
                yield return option;
            }

            if (!selPawn.CanReach(this, PathEndMode.InteractionCell, Danger.Deadly))
            {
                yield return new FloatMenuOption(
                    "CannotEnterBuilding".Translate(this) + ": " + "NoPath".Translate().CapitalizeFirst(), null);
                yield break;
            }

            AcceptanceReport report = CanAcceptPawn(selPawn);
            if (report.Accepted)
            {
                yield return FloatMenuUtility.DecoratePrioritizedTask(
                    new FloatMenuOption("EnterBuilding".Translate(this), delegate
                    {
                        SelectPawn(selPawn);
                    }), selPawn, this);
            }
            else if (base.SelectedPawn == selPawn && !selPawn.IsPrisonerOfColony)
            {
                yield return FloatMenuUtility.DecoratePrioritizedTask(
                    new FloatMenuOption("EnterBuilding".Translate(this), delegate
                    {
                        selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.EnterBuilding, this), JobTag.Misc);
                    }), selPawn, this);
            }
            else if (!report.Reason.NullOrEmpty())
            {
                yield return new FloatMenuOption(
                    "CannotEnterBuilding".Translate(this) + ": " + report.Reason.CapitalizeFirst(), null);
            }
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo gizmo in base.GetGizmos())
            {
                yield return gizmo;
            }

            if (ContainedPawn != null)
            {
                Command_Action eject = new Command_Action();
                eject.defaultLabel = "CommandPodEject".Translate();
                eject.defaultDesc = "RSW_BactaTankEjectDesc".Translate();
                eject.icon = EjectIcon;
                eject.hotKey = KeyBindingDefOf.Misc8;
                eject.action = delegate
                {
                    EjectOccupant(null, null);
                };
                yield return eject;
                yield break;
            }

            if (selectedPawn != null)
            {
                Command_Action cancel = new Command_Action();
                cancel.defaultLabel = "CommandCancelLoad".Translate();
                cancel.defaultDesc = "CommandCancelLoadDesc".Translate();
                cancel.icon = CancelIcon;
                cancel.activateSound = SoundDefOf.Designate_Cancel;
                cancel.action = CancelLoad;
                yield return cancel;
                yield break;
            }

            Command_Action insert = new Command_Action();
            insert.defaultLabel = "InsertPerson".Translate() + "...";
            insert.defaultDesc = "RSW_BactaTankInsertDesc".Translate();
            insert.icon = InsertPawnTex;
            insert.action = delegate
            {
                List<FloatMenuOption> options = new List<FloatMenuOption>();
                foreach (Pawn candidate in base.Map.mapPawns.AllPawnsSpawned
                    .OrderBy((Pawn p) => p.IsColonist ? 0 : ((p.IsPrisonerOfColony || p.IsSlaveOfColony) ? 1 : 2))
                    .ThenBy((Pawn p) => p.Label))
                {
                    Pawn pawn = candidate;
                    AcceptanceReport report = CanAcceptPawn(pawn);
                    string label = pawn.LabelShortCap;
                    if (!report.Accepted)
                    {
                        if (!report.Reason.NullOrEmpty())
                        {
                            options.Add(new FloatMenuOption(label + ": " + report.Reason, null, pawn, Color.white));
                        }
                        continue;
                    }
                    options.Add(new FloatMenuOption(label, delegate
                    {
                        SelectPawn(pawn);
                    }, pawn, Color.white));
                }
                if (!options.Any())
                {
                    options.Add(new FloatMenuOption("RSW_BactaTankNoCandidates".Translate(), null));
                }
                Find.WindowStack.Add(new FloatMenu(options));
            };
            if (!PowerOn)
            {
                insert.Disable("NoPower".Translate().CapitalizeFirst());
            }
            yield return insert;
        }

        public override void DynamicDrawPhaseAt(DrawPhase phase, Vector3 drawLoc, bool flip = false)
        {
            base.DynamicDrawPhaseAt(phase, drawLoc, flip);

            Pawn pawn = ContainedPawn;
            if (pawn != null)
            {
                pawn.Drawer.renderer.DynamicDrawPhaseAt(phase, drawLoc + PawnDrawOffset, null, neverAimWeapon: true);
            }
        }

        public override string GetInspectString()
        {
            string text = base.GetInspectString();

            if (selectedPawn != null && innerContainer.Count == 0)
            {
                if (!text.NullOrEmpty())
                {
                    text += "\n";
                }
                text += "WaitingForPawn".Translate(selectedPawn.Named("PAWN")).Resolve();
            }

            return text;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref frozenFood, "frozenFood", -1f);
            Scribe_Values.Look(ref frozenRest, "frozenRest", -1f);
        }
    }
}
