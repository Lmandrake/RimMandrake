using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TheRot
{
    // ═══════════════════════════════════════════════════════════════
    // ROT_GUT_MOTHER_VAT_1 — the Gut-Mother. A dead hwelgrue drops its digesting sac (RM_CompGutDigest.Notify_Killed,
    // the same death hook its castings use; a butcherProducts row would round to 0 for a poor butcher, and the spec
    // says one per carcass). Studying the sac is vanilla Biotech CompAnalyzableUnlockResearch, gating
    // RM_GutMotherCulture through ResearchProjectDef.requiredAnalyzed (MEASURED 2026-10-03 RimSage: SignalChip's shape).
    //
    // The vat (Building_RM_GutMotherVat) is a Building_WorkTable so corpses arrive by a bill — vanilla hauling, filters
    // and Cooking work. RecipeWorker_RM_FeedGutMother.ConsumeIngredient leaves the corpse alone and
    // Notify_IterationCompleted (Bill_Production calls it right after ConsumeIngredients) hands it to the vat's
    // RM_CompGutMotherDigest, which holds it in a ThingOwner and, after RM_TheRotSettings.gutMotherDigestHours of fed
    // time, spills every hediff's spawnThingOnRemoved (chance gutMotherRecoveryChance each) plus all equipment, apparel
    // and inventory beside the vat, then destroys the corpse. Nothing organic comes back.
    //
    // MEASURED 2026-10-03 (RimSage): vanilla never recovers implants from a corpse — Corpse.ButcherProducts ->
    // Pawn.ButcherProducts yields meat, leather, def.butcherProducts and (non-humanlike only) a life-stage
    // butcherBodyPart; spawnThingOnRemoved is reached only by living surgery. The vat is the only path.
    //
    // Hunger: a CompRefuelable of raw meat. CompRefuelable burns fuel only in CompTick (Normal ticker); this vat is Rare,
    // so the comp draws fuelConsumptionRate/day itself. Empty = dormant: no digestion, no bills (base
    // CurrentlyUsableForBills already wants fuel), never dies. Busy (a body inside, or resting after a split) = the
    // vat re-implements IBillGiver.CurrentlyUsableForBills/UsableForBillsAfterFueling to refuse new bills.
    // ═══════════════════════════════════════════════════════════════

    [DefOf]
    public static class RM_GutMotherDefOf
    {
        public static ThingDef RM_GutMotherSac;
        public static ThingDef RM_GutMotherStarter;
        public static ThingDef RM_GutMotherVat;
        public static ResearchProjectDef RM_GutMotherCulture;
        public static RecipeDef RM_SplitGutMother;

        static RM_GutMotherDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_GutMotherDefOf));
        }
    }

    public static class RM_GutMother
    {
        public static bool Enabled => RM_TheRotSettings.theRotEnabled && RM_TheRotSettings.gutMother;

        /// <summary>Applies the starter's market value setting to the def (startup and on settings write).</summary>
        public static void ApplyStarterValue()
        {
            ThingDef starter = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GutMotherStarter");
            starter?.SetStatBaseValue(StatDefOf.MarketValue, RM_TheRotSettings.gutMotherStarterValue);
        }

        /// <summary>The sac a dead hwelgrue leaves (called from RM_CompGutDigest.Notify_Killed).</summary>
        public static void DropSac(IntVec3 at, Map map)
        {
            if (!Enabled || map == null) return;
            GenPlace.TryPlaceThing(ThingMaker.MakeThing(RM_GutMotherDefOf.RM_GutMotherSac), at, map, ThingPlaceMode.Near);
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_GutMotherStartup
    {
        static RM_GutMotherStartup()
        {
            RM_GutMother.ApplyStarterValue();
        }
    }

    public class CompProperties_RM_GutMotherDigest : CompProperties
    {
        public float splitNutrition = 6f;
        public float splitRestHours = 12f;

        public CompProperties_RM_GutMotherDigest()
        {
            compClass = typeof(RM_CompGutMotherDigest);
        }
    }

    public class RM_CompGutMotherDigest : ThingComp, IThingHolder
    {
        private ThingOwner<Thing> belly;
        private int progressTicks;
        private int restUntilTick = -1;

        public CompProperties_RM_GutMotherDigest Props => (CompProperties_RM_GutMotherDigest)props;

        public RM_CompGutMotherDigest()
        {
            belly = new ThingOwner<Thing>(this, oneStackOnly: true);
        }

        private CompRefuelable Refuel => parent.TryGetComp<CompRefuelable>();
        public Corpse Held => belly.Count > 0 ? belly[0] as Corpse : null;
        public int ProgressTicks => progressTicks;
        public static int DigestTicks => Mathf.Max(1, Mathf.RoundToInt(RM_TheRotSettings.gutMotherDigestHours * GenDate.TicksPerHour));
        public bool Dormant => Refuel != null && !Refuel.HasFuel;
        public bool Resting => Find.TickManager != null && Find.TickManager.TicksGame < restUntilTick;
        public bool Busy => Held != null || Resting;

        public ThingOwner GetDirectlyHeldThings() => belly;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public bool TryAccept(Corpse corpse)
        {
            if (!RM_GutMother.Enabled || corpse == null || corpse.Destroyed || Held != null) return false;
            if (corpse.Spawned) corpse.DeSpawn();
            if (!belly.TryAdd(corpse, canMergeWithExistingStacks: false))
            {
                return false;
            }
            progressTicks = 0;
            return true;
        }

        public void Notify_Split()
        {
            Refuel?.ConsumeFuel(Props.splitNutrition);
            restUntilTick = Find.TickManager.TicksGame + Mathf.RoundToInt(Props.splitRestHours * GenDate.TicksPerHour);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!parent.Spawned || !RM_GutMother.Enabled) return;
            CompRefuelable refuel = Refuel;
            if (refuel != null && refuel.HasFuel)
            {
                refuel.ConsumeFuel(refuel.Props.fuelConsumptionRate * GenTicks.TickRareInterval / GenDate.TicksPerDay);
            }
            if (Held == null || Dormant) return;
            progressTicks += GenTicks.TickRareInterval;
            if (progressTicks >= DigestTicks)
            {
                Finish();
            }
        }

        /// <summary>Spills what the body held beside the vat and destroys the body. Returns what came out.</summary>
        public List<Thing> Finish()
        {
            var outThings = new List<Thing>();
            Corpse corpse = Held;
            Map map = parent.MapHeld;
            if (corpse == null || map == null) return outThings;
            IntVec3 at = parent.InteractionCell.IsValid ? parent.InteractionCell : parent.Position;
            Pawn p = corpse.InnerPawn;
            int implants = 0;
            if (p != null)
            {
                if (p.health?.hediffSet != null)
                {
                    foreach (Hediff h in p.health.hediffSet.hediffs.ToList())
                    {
                        ThingDef part = h.def.spawnThingOnRemoved;
                        if (part == null || !Rand.Chance(RM_TheRotSettings.gutMotherRecoveryChance)) continue;
                        Thing made = ThingMaker.MakeThing(part, part.MadeFromStuff ? GenStuff.DefaultStuffFor(part) : null);
                        if (GenPlace.TryPlaceThing(made, at, map, ThingPlaceMode.Near))
                        {
                            outThings.Add(made);
                            implants++;
                        }
                    }
                }
                DropAll(p.equipment?.GetDirectlyHeldThings(), at, map, outThings);
                DropAll(p.apparel?.GetDirectlyHeldThings(), at, map, outThings);
                DropAll(p.inventory?.innerContainer, at, map, outThings);
            }
            corpse.Destroy(DestroyMode.Vanish);
            belly.Clear();
            progressTicks = 0;
            string who = p?.LabelShortCap ?? "The body";
            if (implants > 0 && !RM_GameComponent_GutMother.FirstImplantLettered)
            {
                RM_GameComponent_GutMother.FirstImplantLettered = true;
                Find.LetterStack.ReceiveLetter("The gut-mother gives back",
                    "The gut-mother has finished with " + who + ". Everything organic is gone; beside the vat lie "
                    + implants + " implant" + (implants == 1 ? "" : "s") + " and whatever the body carried, glistening but whole.",
                    LetterDefOf.PositiveEvent, new LookTargets(outThings));
            }
            else
            {
                Messages.Message("The gut-mother has finished with " + who + ": " + outThings.Count + " thing"
                    + (outThings.Count == 1 ? "" : "s") + " spilled beside it.", new LookTargets(parent), MessageTypeDefOf.NeutralEvent, historical: false);
            }
            return outThings;
        }

        private static void DropAll(ThingOwner owner, IntVec3 at, Map map, List<Thing> outThings)
        {
            if (owner == null) return;
            foreach (Thing t in owner.ToList())
            {
                if (owner.TryDrop(t, at, map, ThingPlaceMode.Near, out Thing dropped) && dropped != null)
                {
                    dropped.SetForbidden(false, warnOnFail: false);
                    outThings.Add(dropped);
                }
            }
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (previousMap != null && belly.Count > 0)
            {
                belly.TryDropAll(parent.Position, previousMap, ThingPlaceMode.Near);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_GutMother.Enabled) return "Inert (off in Mod Settings).";
            if (Dormant) return Held != null ? "Dormant: hungry. A body waits inside." : "Dormant: hungry.";
            if (Held != null)
            {
                float hours = (DigestTicks - progressTicks) / (float)GenDate.TicksPerHour;
                return "Digesting a body. About " + Mathf.Max(1, Mathf.CeilToInt(hours)) + " hours.";
            }
            if (Resting)
            {
                return "Resting after a split. About " + Mathf.Max(1, Mathf.CeilToInt((restUntilTick - Find.TickManager.TicksGame) / (float)GenDate.TicksPerHour)) + " hours.";
            }
            return "Empty: waiting for a body.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref belly, "rmGutMotherBelly", this);
            Scribe_Values.Look(ref progressTicks, "rmGutMotherProgress", 0);
            Scribe_Values.Look(ref restUntilTick, "rmGutMotherRestUntil", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && belly == null)
            {
                belly = new ThingOwner<Thing>(this, oneStackOnly: true);
            }
        }
    }

    /// <summary>The vat: a work table whose bills stop while it is busy. Re-implements the two IBillGiver gates
    /// (WorkGiver_DoBill and JobDriver_DoBill both call them through the interface).</summary>
    public class Building_RM_GutMotherVat : Building_WorkTable, IBillGiver
    {
        public RM_CompGutMotherDigest Digest => GetComp<RM_CompGutMotherDigest>();

        public new bool CurrentlyUsableForBills()
        {
            RM_CompGutMotherDigest d = Digest;
            return base.CurrentlyUsableForBills() && RM_GutMother.Enabled && d != null && !d.Busy;
        }

        public new bool UsableForBillsAfterFueling()
        {
            RM_CompGutMotherDigest d = Digest;
            return base.UsableForBillsAfterFueling() && RM_GutMother.Enabled && d != null && !d.Busy;
        }
    }

    public class RecipeWorker_RM_FeedGutMother : RecipeWorker
    {
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            return RM_GutMother.Enabled && base.AvailableOnNow(thing, part);
        }

        public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
        {
            if (ingredient is Corpse) return; // handed to the vat in Notify_IterationCompleted
            base.ConsumeIngredient(ingredient, recipe, map);
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            base.Notify_IterationCompleted(billDoer, ingredients);
            var vat = billDoer?.CurJob?.GetTarget(TargetIndex.A).Thing as Building_RM_GutMotherVat;
            Corpse corpse = ingredients?.OfType<Corpse>().FirstOrDefault();
            if (corpse == null) return;
            if (vat?.Digest == null || !vat.Digest.TryAccept(corpse))
            {
                Messages.Message("The gut-mother would not take " + corpse.LabelShort + ".", new LookTargets(corpse),
                    MessageTypeDefOf.RejectInput, historical: false);
            }
        }
    }

    public class RecipeWorker_RM_SplitGutMother : RecipeWorker
    {
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            return RM_GutMother.Enabled && base.AvailableOnNow(thing, part);
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            base.Notify_IterationCompleted(billDoer, ingredients);
            (billDoer?.CurJob?.GetTarget(TargetIndex.A).Thing as Building_RM_GutMotherVat)?.Digest?.Notify_Split();
        }
    }

    public class RM_GameComponent_GutMother : GameComponent
    {
        private bool firstImplantLettered;

        public RM_GameComponent_GutMother(Game game)
        {
        }

        private static RM_GameComponent_GutMother Instance => Current.Game?.GetComponent<RM_GameComponent_GutMother>();

        public static bool FirstImplantLettered
        {
            get => Instance?.firstImplantLettered ?? false;
            set { if (Instance != null) Instance.firstImplantLettered = value; }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref firstImplantLettered, "firstImplantLettered", false);
        }
    }

    /// <summary>Debug proofs for jawa/static_call (validation.py chain gut_mother). Each returns one line.</summary>
    public static class RM_GutMotherProof
    {
        private static Building_RM_GutMotherVat SpawnVat(Map map)
        {
            Thing vat = ThingMaker.MakeThing(RM_GutMotherDefOf.RM_GutMotherVat, RM_GutMotherDefOf.RM_GutMotherSac);
            vat.SetFaction(Faction.OfPlayer);
            IntVec3 cell = CellFinder.RandomClosewalkCellNear(map.Center, map, 12,
                c => GenAdj.OccupiedRect(c, Rot4.North, vat.def.size).ExpandedBy(1).Cells.All(x => x.InBounds(map) && x.Standable(map) && x.GetFirstBuilding(map) == null));
            return (Building_RM_GutMotherVat)GenSpawn.Spawn(vat, cell, map);
        }

        /// <summary>"RESEARCH studied B | canStart B" before and after forcing the sac's analysis.</summary>
        public static string ProofResearch()
        {
            ResearchProjectDef proj = RM_GutMotherDefOf.RM_GutMotherCulture;
            int id = RM_GutMotherDefOf.RM_GutMotherSac.GetCompProperties<CompProperties_CompAnalyzableUnlockResearch>()?.analysisID ?? -1;
            string before = "studied " + proj.AnalyzedThingsRequirementsMet + " | canStart " + proj.CanStartNow;
            Find.AnalysisManager.ForceCompleteAnalysisProgress(id);
            return "RESEARCH before " + before + " || after studied " + proj.AnalyzedThingsRequirementsMet + " | canStart " + proj.CanStartNow;
        }

        /// <summary>Spawns a fed vat on the current map, a stranger with a bionic arm, a rifle and a parka, kills it,
        /// lays the body in the vat and runs the digestion to the end. "VAT out n | BionicArm B | rifle B | parka B | corpse gone B".</summary>
        public static string ProofDigest()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            Building_RM_GutMotherVat vat = SpawnVat(map);
            vat.GetComp<CompRefuelable>()?.Refuel(20f);
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(DefDatabase<PawnKindDef>.GetNamedSilentFail("Drifter") ?? PawnKindDefOf.Villager,
                null, PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, canGeneratePawnRelations: false));
            GenSpawn.Spawn(p, vat.InteractionCell, map);
            HediffDef arm = DefDatabase<HediffDef>.GetNamedSilentFail("BionicArm");
            BodyPartRecord shoulder = p.RaceProps.body.AllParts.FirstOrDefault(x => x.def.defName == "Shoulder");
            if (arm != null && shoulder != null) p.health.AddHediff(arm, shoulder);
            p.equipment?.DestroyAllEquipment();
            ThingDef rifleDef = DefDatabase<ThingDef>.GetNamedSilentFail("Gun_AssaultRifle");
            if (rifleDef != null) p.equipment?.AddEquipment((ThingWithComps)ThingMaker.MakeThing(rifleDef));
            ThingDef parkaDef = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_Parka");
            if (parkaDef != null) p.apparel?.Wear((Apparel)ThingMaker.MakeThing(parkaDef, GenStuff.DefaultStuffFor(parkaDef)), dropReplacedApparel: false);
            p.Kill(null);
            Corpse corpse = p.Corpse;
            if (corpse == null) return "REFUSED: no corpse";
            if (!vat.Digest.TryAccept(corpse)) return "REFUSED: vat would not take the body";
            List<Thing> outThings = vat.Digest.Finish();
            return "VAT out " + outThings.Count + " | BionicArm " + outThings.Any(t => t.def.defName == "BionicArm")
                + " | rifle " + outThings.Any(t => t.def == rifleDef) + " | parka " + outThings.Any(t => t.def == parkaDef)
                + " | corpse gone " + corpse.Destroyed;
        }

        /// <summary>A vat with a body and no nutrition, rare-ticked twice. "DORMANT progress a -> b | dormant B".</summary>
        public static string ProofDormant()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            Building_RM_GutMotherVat vat = SpawnVat(map);
            Pawn p = PawnGenerator.GeneratePawn(DefDatabase<PawnKindDef>.GetNamedSilentFail("Drifter") ?? PawnKindDefOf.Villager, null);
            GenSpawn.Spawn(p, vat.InteractionCell, map);
            p.Kill(null);
            if (p.Corpse == null || !vat.Digest.TryAccept(p.Corpse)) return "REFUSED: vat would not take the body";
            int a = vat.Digest.ProgressTicks;
            vat.Digest.CompTickRare();
            vat.Digest.CompTickRare();
            return "DORMANT progress " + a + " -> " + vat.Digest.ProgressTicks + " | dormant " + vat.Digest.Dormant;
        }

        /// <summary>"STARTER rottable B | viability B | tradeable B | value v | split makes n".</summary>
        public static string ProofStarter()
        {
            ThingDef d = RM_GutMotherDefOf.RM_GutMotherStarter;
            Thing t = ThingMaker.MakeThing(d);
            bool viability = d.comps.Any(c => c.compClass != null && c.compClass.Name.Contains("Ruinable"))
                || d.modExtensions?.Any(e => e.GetType().Name == "RM_LivePrepExtension") == true;
            int split = RM_GutMotherDefOf.RM_SplitGutMother.products.Where(p => p.thingDef == d).Sum(p => p.count);
            return "STARTER rottable " + (t.TryGetComp<CompRottable>() != null) + " | viability " + viability
                + " | tradeable " + (d.tradeability == Tradeability.All) + " | value " + t.MarketValue.ToString("0") + " | split makes " + split;
        }
    }
}
