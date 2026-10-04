using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.KeelHoist
{
    // HUTT_LOTTERY_CHUTE_BUILD_1 (design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md §4, RULED): the chance
    // chute. A fixed head-frame in chute mode at a house's site (the Hutt slave pit first). Lower a stake into it
    // (goods, slaves or beasts); hours later a crate comes up built with vanilla's
    // ThingSetMakerParams.totalMarketValueRange around a rolled multiplier. The house always takes its cut first, so
    // the expected return is below the stake. Staked pawns pass to the world as the house's, named in the roll letter
    // and the chute's ledger: never silently vanished. No new UI and no animation (design §5).
    public class RM_ChanceChute : RM_HoistFrame
    {
        public float stakeValue;
        public int rollAt = -1;
        private List<string> stakedLabels = new List<string>();
        private List<Pawn> stakedPawns = new List<Pawn>();
        public List<RM_ChuteRoll> rolls = new List<RM_ChuteRoll>();

        public override bool CableDown => true;
        public override bool ShowsRaiseCradle => false;
        protected override bool HandlesBelow => true;
        public override string EnterString => "Stake on the chance chute";
        public override string EnteringString => "Going down the chance chute";

        public bool HousePresent(out string reason)
        {
            reason = null;
            if (!KeelHoistSettings.chuteEnabled)
            {
                reason = "The chance chute is switched off in Mod Settings.";
                return false;
            }
            Faction house = Faction;
            if (house == null || house == Faction.OfPlayer || house.defeated || house.HostileTo(Faction.OfPlayer)
                || Map == null || !Map.mapPawns.SpawnedPawnsInFaction(house).Any(p => !p.Dead && !p.Downed && !p.IsPrisoner && !p.IsSlave))
            {
                reason = "There is no house left here to play against.";
                return false;
            }
            return true;
        }

        public override bool IsEnterable(out string reason)
        {
            if (!HousePresent(out reason))
            {
                return false;
            }
            return base.IsEnterable(out reason);
        }

        public static float RollMultiplier()
        {
            float r = Rand.Value;
            if (r < KeelHoistSettings.chuteJackpotChance)
            {
                return 3f;
            }
            if (r < KeelHoistSettings.chuteJackpotChance + KeelHoistSettings.chuteBustChance)
            {
                return 0.3f;
            }
            return Rand.Range(0.7f, 1.1f);
        }

        /// <summary>What a stake of this value returns, after the house's cut, for one roll.</summary>
        public static float PayoutFor(float stake, float multiplier) => stake * (1f - KeelHoistSettings.chuteHouseCut) * multiplier;

        protected override string ReceiveBelow(Thing t)
        {
            if (t is Pawn p)
            {
                stakeValue += p.MarketValue;
                stakedLabels.Add(p.LabelShortCap);
                if (Faction != null)
                {
                    RM_PitBuyerUtility.TransferToBuyer(p, Faction);
                }
                if (!p.IsWorldPawn())
                {
                    Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
                }
                stakedPawns.Add(p);
            }
            else
            {
                stakeValue += t.MarketValue * t.stackCount;
                stakedLabels.Add(t.LabelCap);
                if (!t.Destroyed)
                {
                    t.Destroy();
                }
            }
            if (rollAt < 0)
            {
                rollAt = Find.TickManager.TicksGame + Mathf.RoundToInt(KeelHoistSettings.chuteHours * GenDate.TicksPerHour);
            }
            return "the house (" + Mathf.RoundToInt(stakeValue) + " staked)";
        }

        protected override void Tick()
        {
            base.Tick();
            if (rollAt >= 0 && Find.TickManager.TicksGame >= rollAt)
            {
                Roll();
            }
        }

        public RM_ChuteRoll Roll()
        {
            float mult = RollMultiplier();
            float payout = PayoutFor(stakeValue, mult);
            List<Thing> crate = MakeCrate(payout, Faction);
            foreach (Thing thing in crate)
            {
                BeginTransit(thing, up: true, from: "the house");
            }
            var roll = new RM_ChuteRoll
            {
                tick = Find.TickManager.TicksGame,
                stake = Mathf.RoundToInt(stakeValue),
                multiplier = mult,
                payout = Mathf.RoundToInt(crate.Sum(c => c.MarketValue * c.stackCount)),
                staked = string.Join(", ", stakedLabels),
            };
            rolls.Add(roll);
            if (rolls.Count > 50)
            {
                rolls.RemoveAt(0);
            }
            string pawns = stakedPawns.Count == 0 ? "" :
                "\n\nThe house keeps what was staked alive: " + string.Join(", ", stakedPawns.Select(p => p.LabelShortCap)) + " now belong to "
                + (Faction?.Name ?? "the house") + ".";
            string verdict = mult >= 3f ? "The house groans: a crate three times the stake." : mult <= 0.3f ? "The house laughs: a crate of scraps." : "An ordinary night for the house.";
            Find.LetterStack.ReceiveLetter("Chance chute: " + roll.payout + " for " + roll.stake,
                "The crate is coming up the chute. Staked: " + roll.staked + " (" + roll.stake + " silver's worth). The house took "
                + KeelHoistSettings.chuteHouseCut.ToStringPercent() + ". " + verdict + pawns,
                mult >= 3f ? LetterDefOf.PositiveEvent : LetterDefOf.NeutralEvent, new LookTargets(this));
            stakeValue = 0f;
            rollAt = -1;
            stakedLabels.Clear();
            stakedPawns.Clear();
            return roll;
        }

        public static List<Thing> MakeCrate(float value, Faction maker)
        {
            var things = new List<Thing>();
            if (value < 1f)
            {
                return things;
            }
            if (value >= 150f)
            {
                var parms = default(ThingSetMakerParams);
                parms.totalMarketValueRange = new FloatRange(value * 0.9f, value);
                parms.qualityGenerator = QualityGenerator.Reward;
                parms.makingFaction = maker;
                things = ThingSetMakerDefOf.Reward_ItemsStandard.root.Generate(parms);
            }
            float got = things.Sum(t => t.MarketValue * t.stackCount);
            int rest = Mathf.FloorToInt(value - got);
            while (rest > 0)
            {
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
                silver.stackCount = Mathf.Min(rest, ThingDefOf.Silver.stackLimit);
                rest -= silver.stackCount;
                things.Add(silver);
            }
            return things;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stakeValue, "stakeValue");
            Scribe_Values.Look(ref rollAt, "rollAt", -1);
            Scribe_Collections.Look(ref stakedLabels, "stakedLabels", LookMode.Value);
            Scribe_Collections.Look(ref stakedPawns, "stakedPawns", LookMode.Reference);
            Scribe_Collections.Look(ref rolls, "rolls", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                stakedLabels = stakedLabels ?? new List<string>();
                stakedPawns = (stakedPawns ?? new List<Pawn>()).Where(p => p != null).ToList();
                rolls = rolls ?? new List<RM_ChuteRoll>();
            }
        }

        public override string GetInspectString()
        {
            var lines = new List<string>();
            string b = base.GetInspectString();
            if (!b.NullOrEmpty())
            {
                lines.Add(b);
            }
            if (!HousePresent(out string why))
            {
                lines.Add(why);
            }
            if (rollAt >= 0)
            {
                lines.Add("Staked: " + Mathf.RoundToInt(stakeValue) + " silver's worth; the crate comes up in "
                          + Mathf.Max(0, rollAt - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ".");
            }
            lines.Add("The house takes " + KeelHoistSettings.chuteHouseCut.ToStringPercent() + " of every stake.");
            if (rolls.Count > 0)
            {
                RM_ChuteRoll last = rolls[rolls.Count - 1];
                lines.Add("Last roll: " + last.payout + " for " + last.stake + ".");
            }
            return string.Join("\n", lines);
        }
    }

    public class RM_ChuteRoll : IExposable
    {
        public int tick;
        public int stake;
        public float multiplier;
        public int payout;
        public string staked;

        public void ExposeData()
        {
            Scribe_Values.Look(ref tick, "tick");
            Scribe_Values.Look(ref stake, "stake");
            Scribe_Values.Look(ref multiplier, "multiplier");
            Scribe_Values.Look(ref payout, "payout");
            Scribe_Values.Look(ref staked, "staked");
        }
    }

    public static class RM_ChanceChuteProof
    {
        /// <summary>Pure arithmetic over the settings: mean payout of n rolls of a 1000 stake (must be below 1000).</summary>
        public static string ProofOdds(string n)
        {
            int count = int.TryParse(n, out int c) ? Mathf.Clamp(c, 100, 100000) : 5000;
            float sum = 0f;
            int jackpots = 0, busts = 0;
            for (int i = 0; i < count; i++)
            {
                float m = RM_ChanceChute.RollMultiplier();
                jackpots += m >= 3f ? 1 : 0;
                busts += m <= 0.3f ? 1 : 0;
                sum += RM_ChanceChute.PayoutFor(1000f, m);
            }
            return string.Format("ODDS rolls={0} meanPayout={1:0} stake=1000 jackpots={2} busts={3} cut={4:0.00}",
                count, sum / count, jackpots, busts, KeelHoistSettings.chuteHouseCut);
        }

        /// <summary>
        /// Stakes on the chute on the current map: a pile of steel and a fresh colony prisoner go down, the roll is
        /// forced, everything arrives; reports the crate, the roll and where the staked prisoner went.
        /// </summary>
        public static string ProofStake(string pawnKindDefName)
        {
            Map map = Find.CurrentMap;
            RM_ChanceChute chute = map?.listerThings.AllThings.OfType<RM_ChanceChute>().FirstOrDefault();
            if (chute == null)
            {
                return "UNMEASURED no chance chute on this map (RM_PitBuyerProof.ProofLayOut RUT_HuttSlavePit places one)";
            }
            if (!chute.HousePresent(out string why))
            {
                return "UNMEASURED " + why;
            }
            Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
            steel.stackCount = 200;
            GenSpawn.Spawn(steel, CellFinder.StandableCellNear(chute.Position, map, 5f), map);
            chute.BeginTransit(steel, up: false, from: "proof");
            Pawn staked = null;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(pawnKindDefName);
            if (kind != null)
            {
                staked = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true));
                GenSpawn.Spawn(staked, CellFinder.StandableCellNear(chute.Position, map, 5f), map);
                staked.guest?.CapturedBy(Faction.OfPlayer);
                chute.BeginTransit(staked, up: false, from: "proof");
            }
            chute.DebugArriveAllNow();
            float stake = chute.stakeValue;
            bool timerSet = chute.rollAt > Find.TickManager.TicksGame;
            RM_ChuteRoll roll = chute.Roll();
            chute.DebugArriveAllNow();
            return string.Format("STAKED stake={0:0} timerSet={1} payout={2} mult={3:0.00} stakedPawnFaction={4} stakedPawnWorld={5} manifest={6}",
                stake, timerSet, roll.payout, roll.multiplier, staked?.Faction?.Name ?? "none", staked != null && staked.IsWorldPawn(),
                chute.manifest.Count);
        }
    }
}
