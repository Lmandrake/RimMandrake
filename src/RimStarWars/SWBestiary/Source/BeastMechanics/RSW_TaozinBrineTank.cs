using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE (design: design/RimStarWars/taozin_split_proposal_2026-10-17.md).
    //
    // Canon: a taozin grub kept in brine infuses the liquid with a delicacy said to steady the mind. Owner colour ruling
    // (verbatim): "I would suggest the grub to be terra cotta in coloration until it is soaked in the brine for a long
    // period, whereupon it turns white".
    //
    // Searched src/ first (2026-10-17): no animal-in-building or brine-vat mechanism exists. The shape is reused from the
    // Kolto tank (src/RimStarWars/Armoury/Source/KoltoTank/): a vanilla Building_Casket holding one pawn, a CompRefuelable
    // as its liquid, and a "carry X to the tank" float-menu option plus job. Unlike the kolto patient, the grub is awake,
    // so the carrier picks up a standing (tame, calm) grub; nothing in Toils_Haul.StartCarryThing requires Downed.
    //
    //   Building_RSW_BrineTank   holds one grub, suspended (ISuspendableThingHolder: it neither eats nor ages - "it lies
    //                            sedated"); brine (RM_Brine, Stillsand) is its CompRefuelable fuel; every finished jar
    //                            spends brinePerJar and drops jarsPerCycle taozin brine (RSW_TaozinBrine, Cuisine) beside it.
    //   RSW_CompTaozinBrining    on the grub: its soak clock and the permanent white flag. The clock only runs while the
    //                            tank is actually working, so a dry tank does not whiten.
    //   RSW_TaozinPalePatch      white look = the grub PawnKindDef's alternateGraphics[0] at alternateGraphicChance 0:
    //                            vanilla never rolls it, and this postfix on PawnGraphicUtils.TryGetAlternate hands it to
    //                            a pale grub. Vanilla's own render path (body, rotting, dessicated) then draws it.
    // Decisions (soak, jar, active) live in Kernel/RSW_BeastKernel.cs (RSW_BrineTankKernel), fuzzed offline.
    // Settings: RSW_BeastMechanicsSettings.taozinBrineTankEnabled / taozinDaysPerJar / taozinPaleDays.
    // ════════════════════════════════════════════════════════════════════

    public class RSW_BrineTankExtension : DefModExtension
    {
        public ThingDef output;
        public ThingDef grubRace;
        public float brinePerJar = 1f;
        public int jarsPerCycle = 1;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (output == null) yield return "RSW_BrineTankExtension has no output";
            if (grubRace == null) yield return "RSW_BrineTankExtension has no grubRace";
            if (brinePerJar <= 0f) yield return "RSW_BrineTankExtension.brinePerJar must be > 0";
            if (jarsPerCycle < 1) yield return "RSW_BrineTankExtension.jarsPerCycle must be >= 1";
        }
    }

    public class RSW_CompProperties_TaozinBrining : CompProperties
    {
        public RSW_CompProperties_TaozinBrining()
        {
            compClass = typeof(RSW_CompTaozinBrining);
        }
    }

    public class RSW_CompTaozinBrining : ThingComp
    {
        public int brinedTicks;
        public bool pale;

        public void Soak(int elapsed)
        {
            brinedTicks = RSW_BrineTankKernel.Soak(brinedTicks, elapsed);
            bool now = RSW_BrineTankKernel.IsPale(pale, brinedTicks, RSW_BeastMechanicsSettings.taozinPaleDays);
            if (now && !pale)
            {
                pale = true;
                // A grub in the tank is not drawn; the tank's EjectContents re-marks it when it comes out.
                if (parent is Pawn p && p.Spawned && p.Drawer?.renderer != null)
                {
                    p.Drawer.renderer.SetAllGraphicsDirty();
                }
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref brinedTicks, "rswBrinedTicks", 0);
            Scribe_Values.Look(ref pale, "rswBrinePale", false);
        }

        public override string CompInspectStringExtra()
        {
            if (pale)
            {
                return "Brine-whitened.";
            }
            if (brinedTicks <= 0)
            {
                return null;
            }
            return "Soaked in brine: " + (brinedTicks / (float)GenDate.TicksPerDay).ToString("0.0") + " of "
                   + RSW_BeastMechanicsSettings.taozinPaleDays.ToString("0") + " days to turn white.";
        }
    }

    public class Building_RSW_BrineTank : Building_Casket, ISuspendableThingHolder
    {
        private int jarProgress;
        private CompRefuelable brine;

        bool ISuspendableThingHolder.IsContentsSuspended => true;

        public RSW_BrineTankExtension Ext => def.GetModExtension<RSW_BrineTankExtension>();

        public Pawn Grub => ContainedThing as Pawn;

        public float Brine => brine?.Fuel ?? 0f;

        public bool Working
        {
            get
            {
                RSW_BrineTankExtension ext = Ext;
                return ext != null && RSW_BrineTankKernel.Active(RSW_BeastMechanicsSettings.taozinBrineTankEnabled,
                    Grub != null, Brine, ext.brinePerJar);
            }
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            brine = GetComp<CompRefuelable>();
        }

        /// <summary>One tame, calm grub of this tank's race, owned by the tank's faction, and only into an empty tank.</summary>
        public bool CanHold(Pawn p, out string reason)
        {
            reason = null;
            RSW_BrineTankExtension ext = Ext;
            if (p == null || ext == null || p.def != ext.grubRace) { reason = "not a taozin grub"; return false; }
            if (p.Dead) { reason = "dead"; return false; }
            if (HasAnyContents) { reason = "the tank already holds a grub"; return false; }
            if (Faction == null || p.Faction != Faction) { reason = "not one of ours"; return false; }
            if (p.InAggroMentalState) { reason = "enraged"; return false; }
            return true;
        }

        public override bool Accepts(Thing thing)
        {
            return thing is Pawn p && CanHold(p, out _) && base.Accepts(thing);
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!Spawned || !Working)
            {
                return;
            }
            RSW_BrineTankExtension ext = Ext;
            Pawn grub = Grub;
            grub.TryGetComp<RSW_CompTaozinBrining>()?.Soak(GenTicks.TickRareInterval);
            int cycle = RSW_BrineTankKernel.CycleTicks(RSW_BeastMechanicsSettings.taozinDaysPerJar);
            if (!RSW_BrineTankKernel.Advance(ref jarProgress, GenTicks.TickRareInterval, cycle))
            {
                return;
            }
            brine.ConsumeFuel(ext.brinePerJar);
            Thing jar = ThingMaker.MakeThing(ext.output);
            jar.stackCount = ext.jarsPerCycle;
            GenPlace.TryPlaceThing(jar, InteractionCell, Map, ThingPlaceMode.Near);
        }

        public override void EjectContents()
        {
            Pawn grub = Grub;
            base.EjectContents();
            if (grub != null && grub.Spawned && grub.TryGetComp<RSW_CompTaozinBrining>()?.pale == true)
            {
                grub.Drawer?.renderer?.SetAllGraphicsDirty();
            }
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            if (HasAnyContents && Faction == Faction.OfPlayer)
            {
                yield return new Command_Action
                {
                    defaultLabel = "Take the grub out",
                    defaultDesc = "Lift the grub out of the brine and set it down beside the tank. The jar in progress keeps its progress for the next grub.",
                    icon = ContentFinder<Texture2D>.Get("UI/Commands/PodEject", false) ?? BaseContent.BadTex,
                    action = EjectContents
                };
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            RSW_BrineTankExtension ext = Ext;
            if (ext == null)
            {
                return s;
            }
            string line;
            if (!RSW_BeastMechanicsSettings.taozinBrineTankEnabled)
                line = "Brine tanks are switched off in Mod Settings.";
            else if (Grub == null)
                line = "Needs a tame taozin grub (right-click the grub with a colonist selected).";
            else if (Brine < ext.brinePerJar)
                line = "Needs brine.";
            else
            {
                int cycle = RSW_BrineTankKernel.CycleTicks(RSW_BeastMechanicsSettings.taozinDaysPerJar);
                line = "Infusing " + ext.output.label + ": " + ((float)jarProgress / cycle).ToStringPercent();
            }
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref jarProgress, "rswJarProgress", 0);
        }
    }

    /// <summary>Right-click a tame grub with a colonist selected: carry it to the nearest free brine tank.</summary>
    public class FloatMenuOptionProvider_RSW_CarryGrubToBrineTank : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        public static Building_RSW_BrineTank FindTankFor(Pawn grub, Pawn carrier)
        {
            if (grub?.Map == null)
            {
                return null;
            }
            Building_RSW_BrineTank best = null;
            float bestDist = float.MaxValue;
            foreach (Building b in grub.Map.listerBuildings.allBuildingsColonist)
            {
                if (b is Building_RSW_BrineTank tank && tank.CanHold(grub, out _) && !tank.IsForbidden(carrier)
                    && carrier.CanReserveAndReach(tank, PathEndMode.Touch, Danger.Deadly))
                {
                    float d = tank.Position.DistanceToSquared(grub.Position);
                    if (d < bestDist)
                    {
                        best = tank;
                        bestDist = d;
                    }
                }
            }
            return best;
        }

        protected override FloatMenuOption GetSingleOptionFor(Pawn clickedPawn, FloatMenuContext context)
        {
            Pawn carrier = context.FirstSelectedPawn;
            if (carrier == null || clickedPawn.GetComp<RSW_CompTaozinBrining>() == null || clickedPawn.Faction != Faction.OfPlayer)
            {
                return null;
            }
            string label = "Put " + clickedPawn.LabelShort + " in a brine tank";
            if (!RSW_BeastMechanicsSettings.taozinBrineTankEnabled)
            {
                return new FloatMenuOption(label + " (brine tanks are switched off in Mod Settings)", null);
            }
            if (!carrier.CanReserveAndReach(clickedPawn, PathEndMode.Touch, Danger.Deadly))
            {
                return null;
            }
            Building_RSW_BrineTank tank = FindTankFor(clickedPawn, carrier);
            if (tank == null)
            {
                return new FloatMenuOption(label + " (no free brine tank)", null);
            }
            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, () =>
            {
                Building_RSW_BrineTank t = FindTankFor(clickedPawn, carrier);
                if (t == null)
                {
                    Messages.Message("No free brine tank for " + clickedPawn.LabelShort + ".", clickedPawn, MessageTypeDefOf.RejectInput, false);
                    return;
                }
                Job job = JobMaker.MakeJob(RSW_BeastMechanicsDefOf.RSW_CarryGrubToBrineTank, clickedPawn, t);
                job.count = 1;
                carrier.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }, MenuOptionPriority.Default, revalidateClickTarget: clickedPawn), carrier, clickedPawn);
        }
    }

    /// <summary>A = the grub, B = the tank. Walk to the grub, pick it up, carry it to the tank, set it in the brine.</summary>
    public class JobDriver_RSW_CarryGrubToBrineTank : JobDriver
    {
        private Pawn Grub => (Pawn)job.GetTarget(TargetIndex.A).Thing;
        private Building_RSW_BrineTank Tank => job.GetTarget(TargetIndex.B).Thing as Building_RSW_BrineTank;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Grub, job, 1, -1, null, errorOnFailed) && pawn.Reserve(Tank, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(TargetIndex.A);
            this.FailOnDestroyedOrNull(TargetIndex.B);
            this.FailOnAggroMentalState(TargetIndex.A);
            this.FailOn(() => Tank == null || !Tank.CanHold(Grub, out _));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B)
                .FailOnSomeonePhysicallyInteracting(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A, subtractNumTakenFromJobCount: true);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);
            yield return Toils_General.Wait(120)
                .FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch)
                .WithProgressBarToilDelay(TargetIndex.B);
            Toil place = ToilMaker.MakeToil("RSW_PlaceGrubInBrine");
            place.initAction = () =>
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null || !Tank.TryAcceptThing(carried))
                {
                    if (carried != null)
                    {
                        pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out _);
                    }
                }
            };
            place.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return place;
        }
    }

    /// <summary>A pale grub draws its kind's first alternate graphic (the white look); see the file header.</summary>
    [HarmonyPatch(typeof(PawnGraphicUtils), nameof(PawnGraphicUtils.TryGetAlternate))]
    public static class RSW_TaozinPalePatch
    {
        public static void Postfix(Pawn pawn, ref AlternateGraphic ag, ref int index, ref bool __result)
        {
            if (__result || pawn?.kindDef?.alternateGraphics == null || pawn.kindDef.alternateGraphics.Count == 0)
            {
                return;
            }
            RSW_CompTaozinBrining comp = pawn.TryGetComp<RSW_CompTaozinBrining>();
            if (comp == null || !comp.pale)
            {
                return;
            }
            ag = pawn.kindDef.alternateGraphics[0];
            index = 0;
            __result = true;
        }
    }
}
