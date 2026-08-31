using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace KoltoTank;

public class Building_KoltoTank : Building_Casket, ISuspendableThingHolder, IThingHolder, IThingHolderWithDrawnPawn
{
    public enum KoltoTankState
    {
        Empty,
        StartFilling,
        Full
    }

    private CompPower powerComp;

    private CompPowerTrader powerTraderComp;

    public CompRefuelable refuelableComp;

    private Pawn pawn;

    // Hardcoded in the decompiled source, NOT wired to CompProperties_KoltoTank's
    // own ticksBetweenHealing XML field despite that field's name -- SpawnSetup
    // never assigns it from Props, and the source KotORResource_Kolto.xml never
    // sets it either (Props.ticksBetweenHealing floats at its 0f default there).
    // Preserved as the literal constant the original actually runs on, not
    // "fixed" to read the dead XML field -- doing so would divide by that 0f.
    private int ticksBetweenHealing = 2500;

    public KoltoTankState state = KoltoTankState.Empty;

    public float fillPct;

    private HediffDef hediffOnExit;

    private HediffDef hediffOnEntry;

    public CompForbiddable forbiddable;

    public CompKoltoTank KoltoTankComp => GetComp<CompKoltoTank>();

    public bool PowerOn => GetComp<CompPowerTrader>().PowerOn;

    public bool IsContainingThingPawn => HasAnyContents && ContainedThing is Pawn;

    public Pawn InnerPawn => HasAnyContents ? ContainedThing as Pawn : null;

    public float HeldPawnDrawPos_Y => pawn.DrawPos.y - 1f / 26f;

    public float HeldPawnBodyAngle => pawn.Rotation.Opposite.AsAngle;

    // Literal numeric value from the decompiled source, not a guessed enum name.
    public PawnPosture HeldPawnPosture => (PawnPosture)0;

    bool ISuspendableThingHolder.IsContentsSuspended => true;

    public bool ModIsLoaded(string modName)
    {
        foreach (ModContentPack runningMod in LoadedModManager.RunningMods)
        {
            if (runningMod.Name.ToLower() == modName.ToLower())
            {
                return true;
            }
        }
        return false;
    }

    public override void SpawnSetup(Map map, bool respawningAfterLoad)
    {
        base.SpawnSetup(map, respawningAfterLoad);
        forbiddable = GetComp<CompForbiddable>();
        fillPct = 0f;
        if (KoltoTankComp != null)
        {
            string exitName = KoltoTankComp.Props.hediffOnExit;
            if (!string.IsNullOrEmpty(exitName))
            {
                hediffOnExit = DefDatabase<HediffDef>.GetNamed(exitName, false);
            }
            string entryName = KoltoTankComp.Props.hediffOnEntry;
            if (!string.IsNullOrEmpty(entryName))
            {
                hediffOnEntry = DefDatabase<HediffDef>.GetNamed(entryName, false);
            }
        }
        refuelableComp = GetComp<CompRefuelable>();
        powerComp = GetComp<CompPower>();
        powerTraderComp = GetComp<CompPowerTrader>();
    }

    public override bool TryAcceptThing(Thing thing, bool allowSpecialEffects = true)
    {
        if (powerTraderComp != null && !powerTraderComp.PowerOn)
        {
            return false;
        }
        if (refuelableComp != null && !refuelableComp.HasFuel)
        {
            return false;
        }
        if (!base.TryAcceptThing(thing, allowSpecialEffects))
        {
            return false;
        }
        if (allowSpecialEffects)
        {
            SoundStarter.PlayOneShot(SoundDefOf.CryptosleepCasket_Accept, new TargetInfo(Position, Map));
        }
        if (thing is Pawn enteringPawn)
        {
            pawn = enteringPawn;
            state = KoltoTankState.StartFilling;
            KoltoTankComp.StartFilling();
            enteringPawn.health.AddHediff(hediffOnEntry);
            enteringPawn.apparel.MoveAllToInventory();
        }
        return true;
    }

    public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn myPawn)
    {
        if (myPawn == null)
        {
            yield break;
        }
        foreach (FloatMenuOption option in base.GetFloatMenuOptions(myPawn))
        {
            yield return option;
        }
        if (Destroyed)
        {
            yield break;
        }
        if (!myPawn.CanReach(this, PathEndMode.InteractionCell, Danger.Deadly))
        {
            yield return new FloatMenuOption("CannotUseNoPath".Translate(), null);
            yield break;
        }
        if (innerContainer != null && innerContainer.Count > 0)
        {
            yield break;
        }
        if (powerTraderComp != null && !powerTraderComp.PowerOn)
        {
            yield return new FloatMenuOption(Translator.Translate("Kolto_NoPowerMessage"), null);
            yield break;
        }
        if (refuelableComp != null && !refuelableComp.HasFuel)
        {
            yield return new FloatMenuOption(Translator.Translate("Kolto_NoFuelMessage"), null);
            yield break;
        }
        if (ModIsLoaded("Humanoid Alien Races"))
        {
            bool isFlesh = true;
            try
            {
                isFlesh = myPawn.IsItFlesh();
            }
            catch
            {
            }
            if (!isFlesh)
            {
                yield break;
            }
        }
        string jobStr = Translator.Translate("EnterKoltoTank");
        void JobAction()
        {
            Job job = JobMaker.MakeJob(Kolto_DefOf.EnterKoltoTank, this);
            myPawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
        }
        FloatMenuOption option2 = new FloatMenuOption(jobStr, JobAction, revalidateClickTarget: this);
        yield return FloatMenuUtility.DecoratePrioritizedTask(option2, myPawn, this, "ReservedBy");
    }

    public override void EjectContents()
    {
        ThingDef filthSlime = ThingDefOf.Filth_Slime;
        foreach (Thing item in innerContainer)
        {
            if (item is not Pawn pawnItem)
            {
                continue;
            }
            PawnComponentsUtility.AddComponentsForSpawn(pawnItem);
            pawnItem.filth.GainFilth(filthSlime);
            if (pawnItem.RaceProps.IsFlesh)
            {
                pawnItem.health.AddHediff(hediffOnExit);
            }
            pawnItem.health.hediffSet.hediffs.RemoveAll((Hediff x) => x.def == hediffOnEntry);
            if (pawnItem.inventory == null)
            {
                continue;
            }
            List<Apparel> carriedApparel = pawnItem.inventory.innerContainer.OfType<Apparel>().ToList();
            foreach (Apparel apparel in carriedApparel)
            {
                if (apparel != null && pawnItem.apparel.CanWearWithoutDroppingAnything(apparel.def))
                {
                    pawnItem.inventory.innerContainer.Remove(apparel);
                    pawnItem.apparel.Wear(apparel, dropReplacedApparel: true, locked: false);
                }
            }
        }
        if (!Destroyed)
        {
            SoundStarter.PlayOneShot(SoundDefOf.CryptosleepCasket_Eject, SoundInfo.InMap(new TargetInfo(Position, Map)));
        }
        state = KoltoTankState.Empty;
        fillPct = 0f;
        pawn = null;
        KoltoTankComp.SetEmpty();
        base.EjectContents();
    }

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref state, "state", KoltoTankState.Empty);
        Scribe_Values.Look(ref fillPct, "fillPct", 0f);
        Scribe_References.Look(ref pawn, "containedPawn");
        if (Scribe.mode == LoadSaveMode.PostLoadInit)
        {
            if (pawn != null && innerContainer.Contains(pawn))
            {
                state = KoltoTankState.Full;
                KoltoTankComp.SetFull();
            }
        }
        forbiddable = GetComp<CompForbiddable>();
        refuelableComp = GetComp<CompRefuelable>();
    }

    public static Building_KoltoTank FindKoltoTankFor(Pawn p, Pawn traveler, bool ignoreOtherReservations = false)
    {
        IEnumerable<ThingDef> tankDefs = DefDatabase<ThingDef>.AllDefs.Where((ThingDef def) => typeof(Building_KoltoTank).IsAssignableFrom(def.thingClass));
        foreach (ThingDef tankDef in tankDefs)
        {
            Building_KoltoTank tank = (Building_KoltoTank)GenClosest.ClosestThingReachable(
                p.Position, p.Map, ThingRequest.ForDef(tankDef), PathEndMode.InteractionCell,
                TraverseParms.For(traveler, Danger.Deadly, TraverseMode.ByPawn, canBashDoors: true),
                9999f,
                (Thing x) => !((Building_KoltoTank)x).HasAnyContents && traveler.CanReserve(x, 1, -1, null, ignoreOtherReservations));
            if (tank != null && !tank.forbiddable.Forbidden && tank.KoltoTankComp != null
                && p.BodySize <= tank.KoltoTankComp.Props.bodySizeMax && p.BodySize >= tank.KoltoTankComp.Props.bodySizeMin)
            {
                return tank;
            }
        }
        return null;
    }

    protected override void Tick()
    {
        base.Tick();
        if (!HasAnyContents)
        {
            return;
        }
        bool hasFuel = refuelableComp == null || refuelableComp.HasFuel;
        bool hasPower;
        if (powerTraderComp != null)
        {
            hasPower = powerTraderComp.PowerOn;
        }
        else if (powerComp != null)
        {
            hasPower = powerComp.TransmitsPowerNow;
        }
        else
        {
            hasPower = true;
        }
        if (!hasFuel || !hasPower)
        {
            EjectContents();
            return;
        }
        switch (state)
        {
            case KoltoTankState.StartFilling:
                KoltoTankComp.fillPct += KoltoTankComp.waterfillspeed;
                if (KoltoTankComp.fillPct >= 1f)
                {
                    KoltoTankComp.fillPct = 1f;
                    state = KoltoTankState.Full;
                    KoltoTankComp.SetFull();
                }
                break;
            case KoltoTankState.Full:
                if (Find.TickManager.TicksGame % ticksBetweenHealing == 0 && InnerPawn != null)
                {
                    KoltoTankComp.HealPawnInjuries(InnerPawn);
                }
                break;
        }
        if (powerTraderComp != null || powerComp != null)
        {
            KoltoTankComp.UpdatePowerState(powerTraderComp, powerComp);
        }
    }

    protected override void DrawAt(Vector3 drawLoc, bool flip = false)
    {
        base.DrawAt(drawLoc, flip);
        Vector3 drawPos = DrawPos;
        Vector3 innerPos = DrawPos;
        drawPos.y -= 0.03f;
        switch (KoltoTankComp.State)
        {
            case KoltoTankState.StartFilling:
                KoltoTankComp.DrawLiquid(drawPos, KoltoTankComp.FillPct);
                RenderPawnInVat(InnerPawn, innerPos + KoltoTankComp.Props.innerDrawOffset);
                break;
            case KoltoTankState.Full:
                KoltoTankComp.DrawLiquid(drawPos, 1f);
                RenderPawnInVat(InnerPawn, innerPos + KoltoTankComp.Props.innerDrawOffset);
                break;
        }
    }

    private void RenderPawnInVat(Pawn innerPawn, Vector3 drawPos)
    {
        if (innerPawn?.Drawer?.renderer == null)
        {
            return;
        }
        if (innerPawn.RaceProps.Humanlike)
        {
            float bob = Mathf.Sin(Find.TickManager.TicksGame * 0.05f) * 0.1f;
            Vector3 pos = drawPos + KoltoTankComp.Props.innerDrawOffset;
            pos.z += bob;
            innerPawn.Drawer.renderer.RenderPawnAt(pos, Rotation, true);
        }
        else
        {
            Graphic.Draw(drawPos, Rotation, innerPawn, 0f);
        }
    }
}
