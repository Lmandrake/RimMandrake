// KYBER_TRADE_PLOT_1 spec §5 — the alleged Jedi. Once per campaign (GameComponent_KyberTrade fires it a day after the
// second kyber sale), two or three moisture farmers of the Homestead Defense League (vanilla OutlanderCivil, reskinned)
// walk in as an ordinary visitor group. One of them carries no weapon and nothing else that confirms anything: no
// psylink, no power (FORCE_POWERS_ARE_V2_1); the word "Jedi" is only ever the colony's speculation. A letter asks the
// one question, how the kyber was obtained, and the answer is the player's to pick (text/menu authority only; the
// game cannot read minds and does not try): any answer is forthright (goodwill, a quiet warning, and the door to the
// donation), saying nothing is evasive (no change, no punishment). If they leave with the letter unanswered, that is
// evasive too.
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Utinni.KyberTradePlot
{
    [StaticConstructorOnStartup]
    public static class KyberTradeHarmony
    {
        static KyberTradeHarmony()
        {
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rut.kybertradeplot"), Assembly.GetExecutingAssembly(), "RimUtinni.KyberTradePlot");
        }
    }

    public class IncidentWorker_KyberHomesteadVisit : IncidentWorker_NeutralGroup
    {
        public const int GroupSize = 3;

        public override bool FactionCanBeGroupSource(Faction f, IncidentParms parms, bool desperate = false)
        {
            return f != null && f.def == FactionDefOf.OutlanderCivil && base.FactionCanBeGroupSource(f, parms, desperate);
        }

        /// <summary>The plot is on and the one visit has not happened. Asked again inside TryExecuteWorker because the
        /// dev-mode "execute incident" action never calls CanFireNow.</summary>
        private static bool PlotAllows()
        {
            GameComponent_KyberTrade comp = KyberTrade.Component;
            return KyberTradePlotSettings.kyberTradePlotEnabled && comp != null && comp.VisitCanStillHappen;
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!PlotAllows()) return false;
            // A preset faction skips the base's candidate search, and with it the hostile-lord, Peaceful-group and
            // arrival-layer checks: ask them here.
            if (parms.faction != null && !FactionCanBeGroupSource(parms.faction, parms)) return false;
            return base.CanFireNowSub(parms);
        }

        protected override void ResolveParmsPoints(IncidentParms parms)
        {
            if (parms.points < 0f) parms.points = 0f;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!PlotAllows()) return false;
            if (!TryResolveParms(parms) || parms.faction == null || !FactionCanBeGroupSource(parms.faction, parms)) return false;
            List<Pawn> pawns = new List<Pawn>();
            foreach (Pawn p in PawnGroupMakerUtility.GeneratePawns(IncidentParmsUtility.GetDefaultPawnGroupMakerParms(PawnGroupKindDefOf.Peaceful,
                         parms, ensureCanGenerateAtLeastOnePawn: true), warnOnZeroResults: false))
            {
                if (pawns.Count < GroupSize) pawns.Add(p);
                else Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard);
            }
            while (pawns.Count < GroupSize)
            {
                PawnKindDef kind = parms.faction.def.basicMemberKind ?? parms.faction.RandomPawnKind();
                if (kind == null) break;
                pawns.Add(PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, parms.faction, PawnGenerationContext.NonPlayer, map.Tile)));
            }
            if (pawns.Count == 0) return false;

            // The quiet one is an adult; with no adult in the group, the first of them.
            Pawn quiet = pawns.FirstOrDefault(p => p.DevelopmentalStage.Adult()) ?? pawns[0];
            MakeUnconfirmable(quiet);
            foreach (Pawn p in pawns)
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(parms.spawnCenter, map, 5), map);
            RCellFinder.TryFindRandomSpotJustOutsideColony(pawns[0], out IntVec3 chill);
            LordMaker.MakeNewLord(parms.faction, new LordJob_VisitColony(parms.faction, chill), map, pawns);

            KyberTrade.Component?.Notify_VisitArrived(pawns);
            var letter = (ChoiceLetter_KyberHomesteadQuestion)LetterMaker.MakeLetter(KyberDefOf.RUT_KyberHomesteadQuestion);
            letter.pawns = pawns;
            letter.homestead = parms.faction;
            letter.Label = "RUT_KyberVisitLabel".Translate();
            letter.title = "RUT_KyberVisitTitle".Translate();
            letter.Text = "RUT_KyberVisitText".Translate(parms.faction.Name, quiet.LabelShort);
            letter.lookTargets = new LookTargets(pawns);
            letter.relatedFaction = parms.faction;
            Find.LetterStack.ReceiveLetter(letter);
            Log.Message("[KyberTrade] the Homestead visit arrived: " + string.Join(", ", pawns.Select(p => p.LabelShort)) + "; the quiet one is "
                + quiet.LabelShort + " (unarmed, no psylink)");
            return true;
        }

        /// <summary>Light kit, no weapon, nothing that confirms anything: no psylink, no psycasts.</summary>
        public static void MakeUnconfirmable(Pawn p)
        {
            p.equipment?.DestroyAllEquipment();
            if (p.health?.hediffSet != null && HediffDefOf.PsychicAmplifier != null)
            {
                Hediff amp = p.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicAmplifier);
                if (amp != null) p.health.RemoveHediff(amp);
            }
        }
    }

    public class ChoiceLetter_KyberHomesteadQuestion : ChoiceLetter
    {
        public List<Pawn> pawns = new List<Pawn>();
        public Faction homestead;

        public override bool CanDismissWithRightClick => false;

        private bool Answerable
        {
            get
            {
                GameComponent_KyberTrade comp = KyberTrade.Component;
                return comp != null && comp.state.visit == KyberVisitState.Arrived
                    && pawns.Any(KyberTrade.VisitorStillHere);
            }
        }

        public override bool CanShowInLetterStack => base.CanShowInLetterStack && Answerable;

        private DiaOption Answer(string key, bool forthright)
        {
            string line = key.Translate().Resolve();
            var o = new DiaOption(line)
            {
                action = () =>
                {
                    KyberTrade.Component?.Notify_VisitAnswered(forthright, homestead, line);
                    Find.LetterStack.RemoveLetter(this);
                },
                resolveTree = true,
            };
            if (!Answerable) o.Disable(null);
            return o;
        }

        public override IEnumerable<DiaOption> Choices
        {
            get
            {
                if (ArchivedOnly || !Answerable)
                {
                    yield return Option_Close;
                    yield break;
                }
                yield return Answer("RUT_KyberAnswerMined", true);
                yield return Answer("RUT_KyberAnswerDead", true);
                yield return Answer("RUT_KyberAnswerBought", true);
                yield return Answer("RUT_KyberAnswerStolen", true);
                yield return Answer("RUT_KyberAnswerNothing", false);
                yield return Option_Postpone;
                if (lookTargets.IsValid()) yield return Option_JumpToLocationAndPostpone;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref pawns, "pawns", LookMode.Reference);
            Scribe_References.Look(ref homestead, "homestead");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                pawns = pawns ?? new List<Pawn>();
                pawns.RemoveAll(p => p == null);
            }
        }
    }
}
