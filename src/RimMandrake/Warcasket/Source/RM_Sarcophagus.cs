using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Warcasket
{
    // WARCASKET_CASK_BAY_AND_SARCOPHAGI_1 — warcasket sarcophagi.
    // wastes.md §7, verbatim: "a dead Junker in an adjusted warcasket is a
    // sealed salvage-within-salvage: suit, tools, and the half-extracted core
    // still in its grips."
    //
    // SEALED: RM_CompSarcophagusSeal locks the suit onto its wearer at the
    // moment of death. Vanilla Pawn.Strip calls
    // apparel.DropAll(pos, forbid, dropLocked: base.Destroyed), and a corpse's
    // inner pawn is not Destroyed, so ordinary stripping takes everything
    // else and leaves the sealed suit on the body.
    //
    // SALVAGE-WITHIN-SALVAGE: right-click the corpse, "crack open", timed
    // work; the suit drops and the extension's salvage list spawns beside it.
    //
    // Mod Settings: sarcophagiEnabled. Off: suits are never sealed (a dead
    // wearer strips like anyone else) and the option never appears. A suit
    // sealed while it was on is still crackable — the option only hides when
    // the setting is off, and flipping it back on shows it again, so nothing
    // is ever stranded on a body.

    public class RM_CompProperties_SarcophagusSeal : CompProperties
    {
        public RM_CompProperties_SarcophagusSeal()
        {
            compClass = typeof(RM_CompSarcophagusSeal);
        }
    }

    public class RM_CompSarcophagusSeal : ThingComp
    {
        // True only while the lock on this suit is ours (placed at death). Saved,
        // because a corpse can lie for days across a reload before a
        // resurrector serum reaches it.
        public bool sealedByUs;

        public override void Notify_WearerDied()
        {
            base.Notify_WearerDied();
            Apparel apparel = parent as Apparel;
            bool seals = RM_WarcasketKernel.SealsOnDeath(RM_WarcasketSettings.masterEnabled, RM_WarcasketSettings.sarcophagiEnabled,
                apparel != null && SarcophagusUtility.IsSarcophagusSuit(apparel.def));
            Pawn_ApparelTracker tracker = apparel?.Wearer?.apparel;
            if (tracker == null)
            {
                return;
            }
            bool wasLocked = tracker.IsLocked(apparel);
            sealedByUs = RM_WarcasketKernel.RecordsSeal(sealedByUs, seals, wasLocked);
            if (seals)
            {
                tracker.Lock(apparel);
            }
        }

        // WARCASKET_FIX_SEAL_OUTLIVES_DEATH: called from the
        // ResurrectionUtility.TryResurrect postfix once the wearer lives again.
        public void Notify_WearerResurrected(Pawn wearer, bool resurrected)
        {
            Apparel apparel = parent as Apparel;
            bool countsAsCorpse = wearer?.mutant != null && wearer.mutant.Def != null && wearer.mutant.Def.isConsideredCorpse;
            if (apparel == null || wearer?.apparel == null
                || !RM_WarcasketKernel.UnsealsOnResurrect(sealedByUs, resurrected, wearer.Dead, countsAsCorpse))
            {
                return;
            }
            wearer.apparel.Unlock(apparel);
            sealedByUs = false;
        }

        public override void Notify_Unequipped(Pawn pawn)
        {
            base.Notify_Unequipped(pawn);
            sealedByUs = false;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref sealedByUs, "RM_sealedByUs", false);
        }
    }

    // The suit's lock lives on the pawn's apparel tracker, and vanilla only
    // lifts locks below 50% HP, so without this a revived Junker could never
    // take the suit off and the crack-open option (corpse-only) never applies.
    // TryResurrect is the one caller of Pawn_HealthTracker.Notify_Resurrected
    // in 1.6 (every serum, ritual, mech and shambler path goes through it);
    // the postfix runs whether or not the pawn was respawned, unlike vanilla's
    // own Apparel.Notify_PawnResurrected loop.
    // No settings field: the unseal must run with every switch off, or a suit
    // sealed while they were on would be stranded on a living wearer.
    [RimMandrake.Shared.PatchFeature("Sarcophagus suits unseal on resurrection")]
    [HarmonyPatch(typeof(ResurrectionUtility), nameof(ResurrectionUtility.TryResurrect))]
    public static class Patch_ResurrectionUtility_TryResurrect_Unseal
    {
        public static void Postfix(Pawn pawn, bool __result)
        {
            List<Apparel> worn = pawn?.apparel?.WornApparel;
            if (!__result || worn == null)
            {
                return;
            }
            for (int i = worn.Count - 1; i >= 0; i--)
            {
                worn[i].GetComp<RM_CompSarcophagusSeal>()?.Notify_WearerResurrected(pawn, __result);
            }
        }
    }

    public static class SarcophagusUtility
    {
        public static RM_JunkerSarcophagusExtension ExtensionOf(ThingDef def)
        {
            RM_JunkerSarcophagusExtension ext = def?.GetModExtension<RM_JunkerSarcophagusExtension>();
            return RM_WarcasketKernel.ExtensionApplies(ext != null, ext != null && ext.isSealedSarcophagus) ? ext : null;
        }

        public static bool IsSarcophagusSuit(ThingDef def)
        {
            return ExtensionOf(def) != null;
        }

        // The sealed suit on a corpse, or null.
        public static Apparel SealedSuitOn(Corpse corpse)
        {
            List<Apparel> worn = corpse?.InnerPawn?.apparel?.WornApparel;
            if (worn == null)
            {
                return null;
            }
            for (int i = 0; i < worn.Count; i++)
            {
                if (IsSarcophagusSuit(worn[i].def))
                {
                    return worn[i];
                }
            }
            return null;
        }
    }

    // FloatMenuMakerMap registers every non-abstract FloatMenuOptionProvider
    // by reflection (same shape as Contagion's
    // FloatMenuOptionProvider_InjectGenomeSample).
    public class FloatMenuOptionProvider_CrackSarcophagus : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            Corpse corpse = clickedThing as Corpse;
            Apparel suit = corpse != null ? SarcophagusUtility.SealedSuitOn(corpse) : null;
            if (!RM_WarcasketKernel.OffersCrack(RM_WarcasketSettings.masterEnabled, RM_WarcasketSettings.sarcophagiEnabled,
                corpse != null, suit != null))
            {
                return null;
            }
            Pawn actor = context.FirstSelectedPawn;
            string label = "Crack open sarcophagus (" + suit.LabelNoCount + ")";
            if (!actor.CanReach(corpse, PathEndMode.ClosestTouch, Danger.Deadly))
            {
                return new FloatMenuOption(label + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }
            if (!actor.CanReserve(corpse))
            {
                return new FloatMenuOption(label + ": " + "Reserved".Translate().CapitalizeFirst(), null);
            }
            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, delegate
            {
                corpse.SetForbidden(false, warnOnFail: false);
                actor.jobs.TryTakeOrderedJob(JobMaker.MakeJob(RM_WarcasketDefOf.RM_CrackSarcophagus, corpse), JobTag.Misc);
            }), actor, corpse);
        }
    }

    public class JobDriver_RM_CrackSarcophagus : JobDriver
    {
        private Corpse Corpse => job.targetA.Thing as Corpse;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => SarcophagusUtility.SealedSuitOn(Corpse) == null);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);

            Apparel suitAtStart = SarcophagusUtility.SealedSuitOn(Corpse);
            RM_JunkerSarcophagusExtension extAtStart = SarcophagusUtility.ExtensionOf(suitAtStart?.def);
            int ticks = RM_WarcasketKernel.CrackTicks(extAtStart != null, extAtStart != null ? extAtStart.crackOpenTicks : 0);
            Toil work = Toils_General.Wait(ticks, TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.ClosestTouch);
            work.WithEffect(EffecterDefOf.ConstructMetal, TargetIndex.A);
            yield return work;

            Toil open = ToilMaker.MakeToil("RM_CrackSarcophagus");
            open.initAction = delegate
            {
                Corpse corpse = Corpse;
                Apparel suit = SarcophagusUtility.SealedSuitOn(corpse);
                if (corpse == null || suit == null)
                {
                    return;
                }
                RM_JunkerSarcophagusExtension ext = SarcophagusUtility.ExtensionOf(suit.def);
                Pawn inner = corpse.InnerPawn;
                IntVec3 pos = corpse.PositionHeld;
                Map map = corpse.MapHeld;

                inner.apparel.Unlock(suit);
                RM_CompSarcophagusSeal seal = suit.GetComp<RM_CompSarcophagusSeal>();
                if (seal != null)
                {
                    seal.sealedByUs = false;
                }
                inner.apparel.TryDrop(suit, out Apparel _, pos, forbid: false);

                if (ext?.salvage != null)
                {
                    for (int i = 0; i < ext.salvage.Count; i++)
                    {
                        ThingDefCountClass row = ext.salvage[i];
                        if (!RM_WarcasketKernel.SalvageRowWanted(row?.thingDef != null, row != null ? row.count : 0))
                        {
                            continue;
                        }
                        int left = row.count;
                        while (left > 0)
                        {
                            Thing t = ThingMaker.MakeThing(row.thingDef);
                            t.stackCount = RM_WarcasketKernel.NextSalvageStack(left, row.thingDef.stackLimit);
                            left -= t.stackCount;
                            GenPlace.TryPlaceThing(t, pos, map, ThingPlaceMode.Near);
                        }
                    }
                }

                // Same goodwill consequence vanilla stripping carries.
                if (inner.Faction != null && inner.Faction != Faction.OfPlayer)
                {
                    inner.Faction.Notify_MemberStripped(inner, Faction.OfPlayer);
                }
                Messages.Message(
                    pawn.LabelShort + " cracked open the sealed " + suit.LabelNoCount + ". "
                    + (ext?.flavorNote ?? string.Empty),
                    new LookTargets(pos, map), MessageTypeDefOf.NeutralEvent, historical: false);
            };
            open.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return open;
        }
    }
}
