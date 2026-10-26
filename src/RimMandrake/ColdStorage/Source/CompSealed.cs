using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.ColdStorage
{
    /// <summary>
    /// A sealed item (§4.0 "Sealed"): it never rots while sealed (Patch_CompRottable_TickInterval), it may age into
    /// another item after <see cref="CompProperties_Sealed.agingDays"/>, the aging may ruin it, and breaking the seal
    /// gives <see cref="CompProperties_Sealed.openedInto"/> or the same item rotting normally from then on.
    /// Transitions found during a tick are queued and run from GameComponent_ColdStorage, so a ThingOwner is never
    /// changed while it ticks its contents.
    /// </summary>
    public class CompSealed : ThingComp
    {
        private enum Transition
        {
            Aged,
            Ruined,
        }

        private static readonly List<KeyValuePair<CompSealed, Transition>> pending = new List<KeyValuePair<CompSealed, Transition>>();

        /// <summary>Indexed by ThingDef.index: whether the def has CompProperties_Sealed. Built at startup; null = none.</summary>
        internal static bool[] sealableByIndex;

        public int sealedTick = -1;
        public bool opened;
        private bool queued;

        public CompProperties_Sealed Props => (CompProperties_Sealed)props;

        public bool IsSealedNow => !opened;

        /// <summary>Fast check used by the rot prefix: one array read for every item that cannot be sealed.</summary>
        public static bool IsSealed(Thing thing)
        {
            bool[] map = sealableByIndex;
            if (map == null)
            {
                return false;
            }
            int i = thing.def.index;
            if ((uint)i >= (uint)map.Length || !map[i])
            {
                return false;
            }
            CompSealed comp = (thing as ThingWithComps)?.GetComp<CompSealed>();
            return comp != null && ColdStorageKernel.SealSuspendsRot(comp.IsSealedNow);
        }

        public static CompSealed SealOf(Thing thing)
        {
            bool[] map = sealableByIndex;
            if (map == null || (uint)thing.def.index >= (uint)map.Length || !map[thing.def.index])
            {
                return null;
            }
            return (thing as ThingWithComps)?.GetComp<CompSealed>();
        }

        public int AgingTicks => Props.agesInto == null
            ? -1
            : ColdStorageKernel.AgingTicks(Props.agingDays, RM_ColdStorageSettings.agingTimeMultiplier, RM_ColdStorageSettings.sealAgingEnabled);

        public override void PostPostMake()
        {
            base.PostPostMake();
            if (Find.TickManager != null)
            {
                sealedTick = Find.TickManager.TicksGame;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref sealedTick, "sealedTick", -1);
            Scribe_Values.Look(ref opened, "sealOpened", false);
        }

        public override bool AllowStackWith(Thing other)
        {
            CompSealed o = (other as ThingWithComps)?.GetComp<CompSealed>();
            return o == null || o.opened == opened;
        }

        public override void PreAbsorbStack(Thing otherStack, int count)
        {
            base.PreAbsorbStack(otherStack, count);
            CompSealed o = (otherStack as ThingWithComps)?.GetComp<CompSealed>();
            if (o == null || o.sealedTick < 0 || sealedTick < 0)
            {
                return;
            }
            sealedTick = ColdStorageKernel.MergedSealTick(sealedTick, parent.stackCount, o.sealedTick, count);
        }

        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            CompSealed o = (piece as ThingWithComps)?.GetComp<CompSealed>();
            if (o != null)
            {
                o.sealedTick = sealedTick;
                o.opened = opened;
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            CheckAging();
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            CheckAging();
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            CheckAging();
        }

        private void CheckAging()
        {
            if (opened || queued || Find.TickManager == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (sealedTick < 0)
            {
                sealedTick = now;
                return;
            }
            if (!ColdStorageKernel.HasAged(sealedTick, now, AgingTicks))
            {
                return;
            }
            float chance = ColdStorageKernel.SealFailureChance(Props.failureChance, RM_ColdStorageSettings.sealFailureMultiplier);
            queued = true;
            pending.Add(new KeyValuePair<CompSealed, Transition>(this, Rand.Chance(chance) ? Transition.Ruined : Transition.Aged));
        }

        internal static void ClearPending()
        {
            pending.Clear();
        }

        internal static void RunPending()
        {
            if (pending.Count == 0)
            {
                return;
            }
            KeyValuePair<CompSealed, Transition>[] batch = pending.ToArray();
            pending.Clear();
            foreach (KeyValuePair<CompSealed, Transition> p in batch)
            {
                CompSealed c = p.Key;
                c.queued = false;
                if (c.parent.Destroyed || c.opened)
                {
                    continue;
                }
                if (p.Value == Transition.Aged)
                {
                    Replace(c.parent, c.Props.agesInto);
                }
                else if (c.Props.ruinedInto != null)
                {
                    Replace(c.parent, c.Props.ruinedInto);
                }
                else
                {
                    c.opened = true;
                    c.parent.TryGetComp<CompRottable>()?.RotImmediately();
                }
            }
        }

        /// <summary>Break the seal: give <see cref="CompProperties_Sealed.openedInto"/>, or the same item, now rotting.</summary>
        public void Open()
        {
            if (opened)
            {
                return;
            }
            if (Props.openedInto != null)
            {
                Replace(parent, Props.openedInto);
                return;
            }
            opened = true;
        }

        /// <summary>Swap <paramref name="old"/> for the same count of <paramref name="into"/>, in the same place: on the
        /// same cell if spawned, in the same container if held, else near where it is held.</summary>
        internal static Thing Replace(Thing old, ThingDef into)
        {
            if (old == null || old.Destroyed || into == null)
            {
                return null;
            }
            int count = old.stackCount;
            ThingDef stuff = into.MadeFromStuff ? (old.Stuff ?? GenStuff.DefaultStuffFor(into)) : null;
            Thing made = ThingMaker.MakeThing(into, stuff);
            made.stackCount = count;
            // Keep what it was made from: aged human meat must still be human meat to a cannibal or a vegetarian.
            CompIngredients was = old.TryGetComp<CompIngredients>();
            CompIngredients now = made.TryGetComp<CompIngredients>();
            if (was != null && now != null)
            {
                foreach (ThingDef ing in was.ingredients)
                {
                    now.RegisterIngredient(ing);
                }
            }
            if (old.Spawned)
            {
                Map map = old.Map;
                IntVec3 pos = old.Position;
                old.Destroy();
                GenPlace.TryPlaceThing(made, pos, map, ThingPlaceMode.Near);
                return made;
            }
            ThingOwner owner = old.holdingOwner;
            Map heldMap = old.MapHeld;
            IntVec3 heldPos = old.PositionHeld;
            if (owner != null)
            {
                owner.Remove(old);
            }
            old.Destroy();
            if (owner != null && owner.TryAdd(made))
            {
                return made;
            }
            if (heldMap != null && !made.Destroyed && !made.Spawned)
            {
                GenPlace.TryPlaceThing(made, heldPos, heldMap, ThingPlaceMode.Near);
            }
            return made;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (opened || !parent.Spawned)
            {
                yield break;
            }
            // A short pawn job (JobDriver_BreakSeal): the gizmo marks or unmarks the stack for a basic worker.
            DesignationManager dm = parent.Map.designationManager;
            bool marked = dm.DesignationOn(parent, ColdStorageDefOf.RM_BreakSeal) != null;
            yield return new Command_Action
            {
                defaultLabel = (marked ? "RM_ColdStorage_BreakSealCancel" : "RM_ColdStorage_BreakSeal").Translate(),
                defaultDesc = "RM_ColdStorage_BreakSealDesc".Translate(),
                icon = marked ? TexCommand.ClearPrioritizedWork : ContentFinder<Texture2D>.Get("UI/Designators/Open"),
                action = delegate
                {
                    Designation d = dm.DesignationOn(parent, ColdStorageDefOf.RM_BreakSeal);
                    if (d != null)
                    {
                        d.Delete();
                    }
                    else
                    {
                        dm.AddDesignation(new Designation(parent, ColdStorageDefOf.RM_BreakSeal));
                    }
                },
            };
        }

        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption o in base.CompFloatMenuOptions(selPawn))
            {
                yield return o;
            }
            if (opened || !parent.Spawned || selPawn == null || !selPawn.RaceProps.Humanlike)
            {
                yield break;
            }
            string label = "RM_ColdStorage_BreakSealOrder".Translate(parent.LabelShort);
            if (!selPawn.CanReach(parent, PathEndMode.ClosestTouch, Danger.Deadly))
            {
                yield return new FloatMenuOption(label + ": " + "NoPath".Translate().CapitalizeFirst(), null);
                yield break;
            }
            if (!selPawn.CanReserve(parent))
            {
                yield return new FloatMenuOption(label + ": " + "Reserved".Translate().CapitalizeFirst(), null);
                yield break;
            }
            yield return new FloatMenuOption(label, delegate
            {
                selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(ColdStorageDefOf.RM_BreakSealJob, parent), JobTag.Misc);
            });
        }

        public override string CompInspectStringExtra()
        {
            string label = Props.method?.SealedLabelCap ?? parent.def.LabelCap.ToString();
            if (opened)
            {
                return "RM_ColdStorage_SealBroken".Translate();
            }
            if (sealedTick < 0 || Find.TickManager == null)
            {
                return label;
            }
            int now = Find.TickManager.TicksGame;
            string held = (now - sealedTick).ToStringTicksToPeriod();
            int aging = AgingTicks;
            if (aging < 0)
            {
                return "RM_ColdStorage_SealedFor".Translate(label, held);
            }
            int left = Mathf.Max(0, sealedTick + aging - now);
            return "RM_ColdStorage_SealedAging".Translate(label, held, Props.agesInto.label, left.ToStringTicksToPeriod());
        }
    }
}
