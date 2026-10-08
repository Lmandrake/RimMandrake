using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_RETURN_RITUAL_1 spec 1-3 — the water ledger and the Return.
    // Design: stillsand_turn3_development_2026-09-30.md §2.3.
    //
    // ENGINE ONLY, NO THEOLOGY. This file never names a faith, a faction or a
    // ritual. It is inert until a RM_WaterLedgerDef exists in the def database,
    // and the RM tier ships none — so without the Utinni layer there is no
    // counter, no mood line, no goodwill and no debt UI (spec 5). The Sun-Debt
    // (the ledger def, the Return precept/pattern/behavior/outcome, the debt
    // stone, the mood thought) is XML in mandrake.rut.patches, exactly as the
    // krayt attack is an XML-only consumer of RM_IncidentWorker_SandLeviathan.
    //
    //   Drawn   RM_CompWaterVolume.PostIngested on a ledger biome -> debt up.
    //           RM_WaterLedger.Notify_Drawn is public for any other source
    //           (the still of STILLSAND_GLASS_LENS_CHAIN_1, a wringing).
    //   Opening a gale ending (RM_MapComponent_WetSand), a kill of a pawn with
    //           RM_CompOpensWaterReturn (the krayt), or the debt crossing
    //           openingThresholdLitres. Never a clock (the no-circadian ban).
    //           Each opening bumps a serial the ritual trigger watches.
    //   Weight  IncidentFactor multiplies the Stillsand event workers' chance.
    //   Mood    RM_ThoughtWorker_WaterLedger, by band, for holders of
    //           believerPrecept.
    //   Return  the ritual's target filter (water set at an unroofed stone) and
    //           outcome worker (pour, bloom ring, debt paid, the sand gives
    //           back a buried cache, or wakes a refusal).
    // ════════════════════════════════════════════════════════════════════

    public class RM_WaterLedgerDef : Def
    {
        /// <summary>BiomeDef defNames on which drawn water is counted.</summary>
        public List<string> biomes = new List<string>();

        /// <summary>A pawn whose ideo holds this precept is a believer (feels the mood line).</summary>
        public PreceptDef believerPrecept;

        /// <summary>FactionDef defName whose goodwill follows the debt.</summary>
        public string goodwillFaction;

        /// <summary>Band i begins at bandLitres[i] (ascending, first is 0). The mood thought has one stage per band.</summary>
        public List<float> bandLitres = new List<float> { 0f, 30f, 90f, 180f };

        public List<string> bandLabels = new List<string>();

        public int goodwillPerBandUp = -4;
        public int goodwillOnPositiveReturn = 4;

        public float openingThresholdLitres = 90f;
        public int minTicksBetweenOpenings = 30000;

        /// <summary>IncidentDef defNames the debt weights up.</summary>
        public List<string> weightedIncidents = new List<string>();
        public float weightPerHundredLitres = 0.5f;
        public float maxWeight = 3f;

        // The Return.
        public float waterSearchRadius = 4.9f;
        public float returnMinLitres = 12f;
        public float returnMaxLitres = 60f;
        public float repayFactorTerrible;
        public float repayFactorPoor = 0.5f;
        public float repayFactorGood = 1.5f;
        public float repayFactorGreat = 2.5f;
        public float bloomRingRadius = 2.9f;
        public string buriedCacheDef = "RM_Dunes_BuriedCache";
        public float giveBackRadius = 40f;
        public PawnKindDef refusalKind;
        public IntRange refusalCount = new IntRange(2, 3);

        [MustTranslate] public string openingMessage = "The sand is owed ({REASON}). A Return can be held at a stone in the sun.";

        public string BandLabel(int band)
        {
            return bandLabels != null && band >= 0 && band < bandLabels.Count ? bandLabels[band] : band.ToString();
        }

        public int BandFor(float debt)
        {
            return RM_LedgerBook.BandFor(bandLitres, debt);
        }

        public bool CountsOn(Map map)
        {
            return map?.Biome != null && biomes != null && biomes.Contains(map.Biome.defName);
        }
    }

    public class RM_WaterLedger : GameComponent
    {
        private readonly RM_LedgerBook book = new RM_LedgerBook();

        public RM_WaterLedger(Game game)
        {
        }

        public float Debt => book.debt;
        public int OpeningSerial => book.openingSerial;

        /// <summary>The ledger def, or null: the RM tier ships none, so the whole ledger is inert there.</summary>
        public static RM_WaterLedgerDef ActiveDef => DefDatabase<RM_WaterLedgerDef>.AllDefsListForReading.FirstOrDefault();

        public static RM_WaterLedger Current => Verse.Current.Game?.GetComponent<RM_WaterLedger>();

        private static bool Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger)
        {
            def = ActiveDef;
            ledger = Current;
            return def != null && ledger != null && RM_StillsandWaterSettings.ledgerEnabled;
        }

        public static void Notify_Drawn(Map map, float litres, string what)
        {
            if (litres <= 0f || !Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger) || !def.CountsOn(map))
            {
                return;
            }
            RM_LedgerDraw drew = ledger.book.Draw(litres, def.bandLitres, def.goodwillPerBandUp, def.openingThresholdLitres);
            AffectGoodwill(def, drew.goodwillDelta);
            if (drew.crossedOpening)
            {
                Notify_Opening(map, "the debt has grown past " + def.openingThresholdLitres.ToString("0") + " litres");
            }
        }

        public static void Notify_Opening(Map map, string reason)
        {
            if (!Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger) || !def.CountsOn(map))
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (!ledger.book.TryOpen(now, def.minTicksBetweenOpenings))
            {
                return;
            }
            Messages.Message(def.openingMessage.Formatted(reason.Named("REASON")).CapitalizeFirst(),
                MessageTypeDefOf.NeutralEvent, historical: true);
        }

        /// <summary>Pay down the debt (the Return). Returns litres actually paid.</summary>
        public static float Pay(Map map, float litres)
        {
            if (litres <= 0f || !Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger))
            {
                return 0f;
            }
            float paid = ledger.book.Pay(litres, def.bandLitres, def.goodwillPerBandUp, out int goodwillDelta);
            AffectGoodwill(def, goodwillDelta);
            return paid;
        }

        public static float IncidentFactor(Map map, IncidentDef incident)
        {
            if (incident == null || !RM_StillsandWaterSettings.ledgerIncidentWeighting
                || !Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger) || !def.CountsOn(map)
                || def.weightedIncidents == null || !def.weightedIncidents.Contains(incident.defName))
            {
                return 1f;
            }
            return RM_LedgerBook.IncidentFactor(ledger.book.debt, def.weightPerHundredLitres, def.maxWeight);
        }

        public static int CurrentBand()
        {
            return Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger) ? def.BandFor(ledger.book.debt) : -1;
        }

        public static string Describe()
        {
            if (!Live(out RM_WaterLedgerDef def, out RM_WaterLedger ledger))
            {
                return null;
            }
            return def.LabelCap + ": " + ledger.book.debt.ToString("0") + " litres owed (" + def.BandLabel(def.BandFor(ledger.book.debt)) + ")";
        }

        public static void AffectGoodwill(RM_WaterLedgerDef def, int delta)
        {
            if (delta == 0 || def.goodwillFaction.NullOrEmpty())
            {
                return;
            }
            FactionDef fd = DefDatabase<FactionDef>.GetNamedSilentFail(def.goodwillFaction);
            Faction f = fd == null ? null : Find.FactionManager.FirstFactionOfDef(fd);
            if (f != null && Faction.OfPlayer != null && f != Faction.OfPlayer)
            {
                f.TryAffectGoodwillWith(Faction.OfPlayer, delta, canSendMessage: true, canSendHostilityLetter: true);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref book.debt, "debt", 0f);
            Scribe_Values.Look(ref book.drawnTotal, "drawnTotal", 0f);
            Scribe_Values.Look(ref book.paidTotal, "paidTotal", 0f);
            Scribe_Values.Look(ref book.openingSerial, "openingSerial", 0);
            Scribe_Values.Look(ref book.lastOpeningTick, "lastOpeningTick", -999999);
            Scribe_Values.Look(ref book.lastBand, "lastBand", 0);
        }
    }

    /// <summary>Situational mood by debt band, for pawns whose ideo holds the ledger's believer precept.</summary>
    public class RM_ThoughtWorker_WaterLedger : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            if (def?.believerPrecept == null || p.Faction == null || !p.Faction.IsPlayer || p.Ideo == null
                || !p.Ideo.HasPrecept(def.believerPrecept))
            {
                return ThoughtState.Inactive;
            }
            int band = RM_WaterLedger.CurrentBand();
            if (band < 0)
            {
                return ThoughtState.Inactive;
            }
            return ThoughtState.ActiveAtStage(Mathf.Min(band, this.def.stages.Count - 1));
        }
    }

    // ── The Return: obligation trigger ───────────────────────────────────

    public class RM_RitualObligationTriggerProperties_WaterReturn : RitualObligationTriggerProperties
    {
        public RM_RitualObligationTriggerProperties_WaterReturn()
        {
            triggerClass = typeof(RM_RitualObligationTrigger_WaterReturn);
        }
    }

    /// <summary>Opens the ritual on a ledger opening (gale, kill, threshold). Never by date.</summary>
    public class RM_RitualObligationTrigger_WaterReturn : RitualObligationTrigger
    {
        private int seenSerial = -1;

        public override void Tick()
        {
            if (Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            RM_WaterLedger ledger = RM_WaterLedger.Current;
            if (ledger == null)
            {
                return;
            }
            if (seenSerial < 0)
            {
                // First sight (new ideo or new game): do not replay old openings.
                seenSerial = ledger.OpeningSerial;
                return;
            }
            if (ledger.OpeningSerial <= seenSerial)
            {
                return;
            }
            seenSerial = ledger.OpeningSerial;
            if (mustBePlayerIdeo && !Faction.OfPlayer.ideos.Has(ritual.ideo))
            {
                return;
            }
            if (ritual.activeObligations.NullOrEmpty())
            {
                ritual.AddObligation(new RitualObligation(ritual));
            }
        }

        public override void CopyTo(RitualObligationTrigger other)
        {
            base.CopyTo(other);
            ((RM_RitualObligationTrigger_WaterReturn)other).seenSerial = seenSerial;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seenSerial, "seenSerial", -1);
        }
    }

    // ── The Return: the stone and the water set beside it ────────────────

    public class RM_RitualObligationTargetWorker_WaterReturn : RitualObligationTargetWorker_ThingDef
    {
        public RM_RitualObligationTargetWorker_WaterReturn()
        {
        }

        public RM_RitualObligationTargetWorker_WaterReturn(RitualObligationTargetFilterDef def) : base(def)
        {
        }

        public static List<Thing> WaterNear(Map map, IntVec3 c, float radius)
        {
            var found = new List<Thing>();
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, radius, true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }
                foreach (Thing t in cell.GetThingList(map))
                {
                    if (t.def.category == ThingCategory.Item && t.TryGetComp<RM_CompWaterVolume>() != null && !t.IsForbidden(Faction.OfPlayer))
                    {
                        found.Add(t);
                    }
                }
            }
            return found;
        }

        public static float Litres(IEnumerable<Thing> water)
        {
            return water.Sum(t => t.TryGetComp<RM_CompWaterVolume>().Props.litres * t.stackCount);
        }

        protected override RitualTargetUseReport CanUseTargetInternal(TargetInfo target, RitualObligation obligation)
        {
            RitualTargetUseReport baseReport = base.CanUseTargetInternal(target, obligation);
            if (!baseReport.canUse)
            {
                return baseReport;
            }
            Map map = target.Map;
            if (map == null)
            {
                return false;
            }
            if (target.Cell.Roofed(map))
            {
                return "The stone must stand in full sun, never in shade.";
            }
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            if (def == null)
            {
                return false;
            }
            float have = Litres(WaterNear(map, target.Cell, def.waterSearchRadius));
            if (have < def.returnMinLitres)
            {
                return "Set at least " + def.returnMinLitres.ToString("0") + " litres of water within "
                       + Mathf.FloorToInt(def.waterSearchRadius) + " cells of the stone (there are " + have.ToString("0") + ").";
            }
            return true;
        }

        public override IEnumerable<string> GetTargetInfos(RitualObligation obligation)
        {
            foreach (string s in base.GetTargetInfos(obligation))
            {
                yield return s;
            }
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            if (def != null)
            {
                yield return "in full sun, with " + def.returnMinLitres.ToString("0") + "+ litres of water set beside it";
            }
        }
    }

    // ── The Return: the outcome ──────────────────────────────────────────

    public class RM_RitualOutcomeEffectWorker_WaterReturn : RitualOutcomeEffectWorker_FromQuality
    {
        public RM_RitualOutcomeEffectWorker_WaterReturn()
        {
        }

        public RM_RitualOutcomeEffectWorker_WaterReturn(RitualOutcomeEffectDef def) : base(def)
        {
        }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual,
            RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            Map map = jobRitual?.Map;
            TargetInfo stone = jobRitual?.selectedTarget ?? TargetInfo.Invalid;
            if (def == null || map == null || !stone.IsValid)
            {
                return;
            }
            var sb = new StringBuilder();

            // 1. The pour: the water set beside the stone goes into the sand in a line toward the star.
            float poured = 0f;
            foreach (Thing t in RM_RitualObligationTargetWorker_WaterReturn.WaterNear(map, stone.Cell, def.waterSearchRadius))
            {
                float per = t.TryGetComp<RM_CompWaterVolume>().Props.litres;
                while (t.stackCount > 0 && poured + per <= def.returnMaxLitres + 0.001f && !t.Destroyed)
                {
                    poured += per;
                    Thing one = t.SplitOff(1);
                    if (!one.Destroyed)
                    {
                        one.Destroy();
                    }
                }
                if (poured + per > def.returnMaxLitres)
                {
                    break;
                }
            }
            List<IntVec3> line = RM_StillsandWater.LineCells(map, stone.Cell, RM_StillsandWater.TowardSun(map),
                Mathf.Clamp(Mathf.RoundToInt(poured / 3f), 3, 14));
            int bloomed = RM_StillsandWater.Pour(map, line, poured);
            if (outcome.Positive)
            {
                // The ring at the stone: the sand answering the pour.
                List<IntVec3> ring = GenRadial.RadialCellsAround(stone.Cell, def.bloomRingRadius, false)
                    .Where(c => c.DistanceTo(stone.Cell) > 1.4f).ToList();
                bloomed += RM_StillsandWater.Pour(map, ring, ring.Count * 2f);
            }
            sb.Append(poured.ToString("0")).Append(" litres went into the sand toward the star");
            sb.Append(bloomed > 0 ? "; the sand will bloom within hours." : ".");

            // 2. The debt.
            float factor = outcome.positivityIndex >= 2 ? def.repayFactorGreat
                : outcome.positivityIndex >= 1 ? def.repayFactorGood
                : outcome.positivityIndex <= -2 ? def.repayFactorTerrible
                : def.repayFactorPoor;
            float paid = RM_WaterLedger.Pay(map, poured * factor);
            if (paid > 0f)
            {
                sb.Append("\n\n").Append(def.LabelCap).Append(" is lighter by ").Append(paid.ToString("0")).Append(" litres.");
            }
            if (outcome.Positive)
            {
                RM_WaterLedger.AffectGoodwill(def, def.goodwillOnPositiveReturn);
            }

            // 3. Great: the sand gives back one buried cache near the stone (the dunes engine's own reveal:
            //    a cache dropped by Destroy with any mode but Vanish spills its contents).
            if (outcome.positivityIndex >= 2)
            {
                ThingDef cacheDef = DefDatabase<ThingDef>.GetNamedSilentFail(def.buriedCacheDef ?? "");
                Thing cache = cacheDef == null ? null : map.listerThings.ThingsOfDef(cacheDef)
                    .Where(c => c.Position.DistanceTo(stone.Cell) <= def.giveBackRadius)
                    .OrderBy(c => c.Position.DistanceToSquared(stone.Cell)).FirstOrDefault();
                if (cache != null)
                {
                    IntVec3 at = cache.Position;
                    FleckMaker.ThrowDustPuffThick(at.ToVector3Shifted(), map, 2.5f, new Color(0.85f, 0.78f, 0.62f));
                    cache.Destroy(DestroyMode.KillFinalize);
                    letterLookTargets = new LookTargets(new[] { stone, new TargetInfo(at, map) });
                    sb.Append("\n\nThe sand gave something back: a buried cache has surfaced nearby.");
                }
                else
                {
                    sb.Append("\n\nThe sand had nothing buried near the stone to give back.");
                }
            }

            // 4. Terrible: the pour wakes what sleeps, read as a debt refused.
            if (outcome.positivityIndex <= -2 && def.refusalKind != null)
            {
                int n = def.refusalCount.RandomInRange;
                var woken = new List<Pawn>();
                for (int i = 0; i < n; i++)
                {
                    if (!CellFinder.TryFindRandomCellNear(stone.Cell, map, 6,
                            c => c.Standable(map) && !c.Fogged(map) && c.GetFirstPawn(map) == null, out IntVec3 cell))
                    {
                        break;
                    }
                    Pawn p = PawnGenerator.GeneratePawn(def.refusalKind);
                    GenSpawn.Spawn(p, cell, map);
                    FleckMaker.ThrowDustPuffThick(cell.ToVector3Shifted(), map, 2f, new Color(0.8f, 0.72f, 0.55f));
                    p.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.Manhunter);
                    woken.Add(p);
                }
                if (woken.Count > 0)
                {
                    letterLookTargets = new LookTargets(woken);
                    sb.Append("\n\nThe pour woke what sleeps: ").Append(woken.Count).Append(" ")
                      .Append(def.refusalKind.GetLabelPlural()).Append(" came up out of the wet sand. The debt was refused.");
                }
            }

            string state = RM_WaterLedger.Describe();
            if (state != null)
            {
                sb.Append("\n\n").Append(state).Append('.');
            }
            extraOutcomeDesc = sb.ToString();
        }
    }
}
