using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheRot
{
    // ═══════════════════════════════════════════════════════════════
    // ROT_UNJOINING_DRAUGHT_1 — the Unjoining. RM_Unjoining.Purge(pawn) is the whole effect, shared by the draught
    // (IngestionOutcomeDoer_RM_Unjoining) and the rite (ROT_UNJOINING_RITE_1, which calls the same method):
    //   removes   RM_UnjoiningTargetsDef.parasites + .symbionts + any hediff whose def carries RM_UnjoinableExtension
    //   husk      one RM_SymbiontHusk per symbiont removed (symbionts list, or the extension's isSymbiont)
    //   horror    Hediff_MetalhorrorImplant -> Emerge(reason): the vanilla emergence (MEASURED 2026-10-03 RimSage:
    //             MetalhorrorUtility.TryEmerge is a one-line wrapper over it; the reason string is appended raw to the
    //             vanilla ThreatBig letter, so that letter IS our readable sign). Never a silent delete.
    //   always    RM_UnjoiningPurge (length = setting) and, setting on, a permanent chemical-burn scar on a liver or
    //             kidney (HediffComp_GetsPermanent.IsPermanent).
    // Toggle unjoiningDraught off: the outcome doer does nothing and the recipe is not offered for new bills.
    // ═══════════════════════════════════════════════════════════════

    public class RM_UnjoiningTargetsDef : Def
    {
        public List<HediffDef> parasites = new List<HediffDef>();
        public List<HediffDef> symbionts = new List<HediffDef>();
        public List<string> organs = new List<string>();
        public HediffDef organInjury;
        public float organInjurySeverity = 4f;
    }

    /// <summary>Put on any HediffDef to make the Unjoining remove it. isSymbiont: also drop a husk.</summary>
    public class RM_UnjoinableExtension : DefModExtension
    {
        public bool isSymbiont;
    }

    public class RM_UnjoiningResult
    {
        public List<HediffDef> removed = new List<HediffDef>();
        public int husks;
        public bool horrorForced;
        public BodyPartRecord scarred;
    }

    public static class RM_Unjoining
    {
        public const string HorrorReason = "The draught found something that was not a parasite.";

        public static bool Enabled => RM_TheRotSettings.theRotEnabled && RM_TheRotSettings.unjoiningDraught;
        public static RM_UnjoiningTargetsDef Targets => DefDatabase<RM_UnjoiningTargetsDef>.GetNamedSilentFail("RM_UnjoiningTargets");
        public static HediffDef PurgeDef => DefDatabase<HediffDef>.GetNamedSilentFail("RM_UnjoiningPurge");

        public static RM_UnjoiningResult Purge(Pawn pawn, string horrorReason = HorrorReason)
        {
            var result = new RM_UnjoiningResult();
            if (pawn?.health?.hediffSet == null) return result;
            RM_UnjoiningTargetsDef t = Targets;
            foreach (Hediff h in pawn.health.hediffSet.hediffs.ToList())
            {
                RM_UnjoinableExtension ext = h.def.GetModExtension<RM_UnjoinableExtension>();
                // what the draught takes and what leaves a husk: RM_TheRotKernel.Sort (offline-fuzzed)
                RM_TheRotKernel.Sorting s = RM_TheRotKernel.Sort(t != null && t.parasites.Contains(h.def), t != null && t.symbionts.Contains(h.def),
                    ext != null, ext != null && ext.isSymbiont);
                if (!s.removed) continue;
                pawn.health.RemoveHediff(h);
                result.removed.Add(h.def);
                if (s.husk) result.husks++;
            }
            if (result.husks > 0 && pawn.MapHeld != null)
            {
                Thing husk = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_SymbiontHusk"));
                husk.stackCount = result.husks;
                GenPlace.TryPlaceThing(husk, pawn.PositionHeld, pawn.MapHeld, ThingPlaceMode.Near);
            }
            Hediff_MetalhorrorImplant horror = pawn.health.hediffSet.GetFirstHediff<Hediff_MetalhorrorImplant>();
            if (horror != null)
            {
                horror.Emerge(horrorReason);
                result.horrorForced = true;
            }
            HediffDef purgeDef = PurgeDef;
            if (purgeDef != null && !pawn.Dead)
            {
                Hediff purge = pawn.health.hediffSet.GetFirstHediffOfDef(purgeDef) ?? pawn.health.AddHediff(purgeDef);
                HediffComp_Disappears d = purge.TryGetComp<HediffComp_Disappears>();
                if (d != null) d.ticksToDisappear = RM_TheRotKernel.PurgeTicks(RM_TheRotSettings.unjoiningPurgeHours);
            }
            if (RM_TheRotSettings.unjoiningOrganDamage && t?.organInjury != null && !pawn.Dead)
            {
                BodyPartRecord organ = pawn.health.hediffSet.GetNotMissingParts()
                    .Where(p => t.organs.Contains(p.def.defName)).RandomElementWithFallback();
                if (organ != null)
                {
                    Hediff_Injury scar = (Hediff_Injury)HediffMaker.MakeHediff(t.organInjury, pawn, organ);
                    scar.Severity = RM_TheRotKernel.ScarSeverity(t.organInjurySeverity, pawn.health.hediffSet.GetPartHealth(organ));
                    if (scar.Severity > 0f)
                    {
                        HediffComp_GetsPermanent perm = scar.TryGetComp<HediffComp_GetsPermanent>();
                        if (perm != null) perm.IsPermanent = true;
                        pawn.health.AddHediff(scar, organ);
                        result.scarred = organ;
                    }
                }
            }
            return result;
        }
    }

    public class IngestionOutcomeDoer_RM_Unjoining : IngestionOutcomeDoer
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (!RM_Unjoining.Enabled) return;
            RM_UnjoiningResult r = RM_Unjoining.Purge(pawn);
            if (pawn.Faction == Faction.OfPlayer && r.removed.Count > 0)
            {
                Messages.Message(pawn.LabelShortCap + " purged " + string.Join(", ", r.removed.Select(d => d.label))
                    + (r.husks > 0 ? "; the dead symbiont lies beside them." : "."), pawn, MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }
    }

    public class RecipeWorker_RM_UnjoiningDraught : RecipeWorker
    {
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            return RM_Unjoining.Enabled && base.AvailableOnNow(thing, part);
        }
    }

    /// <summary>Debug proofs for jawa/static_call (validation.py chain unjoining).</summary>
    public static class RM_UnjoiningProof
    {
        private static Pawn Patient(Map map)
        {
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Colonist, Faction.OfPlayer,
                PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, canGeneratePawnRelations: false));
            GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(map.Center, map, 8), map);
            return p;
        }

        /// <summary>mode "parasites": MuscleParasites + GutWorms + RM_Sym_Sheenblood; "none": nothing; "horror": a
        /// metalhorror implant. Ingests a draught. "UNJOIN removed n | purge B | husks h | scars s | horror B".</summary>
        public static string ProofDraught(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            Pawn p = Patient(map);
            int scarsBefore = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury i && i.IsPermanent());
            if (mode == "parasites")
            {
                foreach (string d in new[] { "MuscleParasites", "GutWorms", "RM_Sym_Sheenblood" })
                {
                    HediffDef hd = DefDatabase<HediffDef>.GetNamedSilentFail(d);
                    if (hd != null) p.health.AddHediff(hd);
                }
            }
            else if (mode == "horror")
            {
                HediffDef hd = DefDatabase<HediffDef>.GetNamedSilentFail("MetalhorrorImplant");
                if (hd == null) return "REFUSED: no MetalhorrorImplant (Anomaly)";
                p.health.AddHediff(hd, p.health.hediffSet.GetBrain());
            }
            int husksBefore = map.listerThings.ThingsOfDef(DefDatabase<ThingDef>.GetNamed("RM_SymbiontHusk")).Sum(x => x.stackCount);
            Thing draught = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_UnjoiningDraught"));
            foreach (IngestionOutcomeDoer d in draught.def.ingestible.outcomeDoers) d.DoIngestionOutcome(p, draught, 1);
            int husks = map.listerThings.ThingsOfDef(DefDatabase<ThingDef>.GetNamed("RM_SymbiontHusk")).Sum(x => x.stackCount) - husksBefore;
            int scars = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury i && i.IsPermanent()) - scarsBefore;
            bool purge = p.health.hediffSet.HasHediff(RM_Unjoining.PurgeDef);
            int left = p.health.hediffSet.hediffs.Count(h => h.def.defName == "MuscleParasites" || h.def.defName == "GutWorms" || h.def.defName == "RM_Sym_Sheenblood");
            Hediff_MetalhorrorImplant horror = p.health.hediffSet.GetFirstHediff<Hediff_MetalhorrorImplant>();
            return "UNJOIN left " + left + " | purge " + purge + " | husks " + husks + " | scars " + scars
                + " | horror emerging " + (horror != null && horror.Emerging);
        }
    }
}
