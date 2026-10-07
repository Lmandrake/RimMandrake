// Verse-free kernel of the keel hoist: the transit schedule and its tick loop, the arrival plan, the chance-chute roll and
// payout, pit pricing and silver stacking, capture / acceptance / gate decisions, the Open Line meter and the cable reach tests.
// The hoist, the chute, the sealed holder and the Harmony patches call these with the same expressions;
// SelfTest/KeelHoistFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;`
// here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.KeelHoist
{
    /// <summary>The hoist as the schedule sees it: how many things ride the cable and how to land one.</summary>
    public interface IHoistTransitSink
    {
        int TransitCount { get; }
        void ArriveAt(int i);
    }

    /// <summary>What happens to a thing that reaches the end of its trip.</summary>
    public enum ArrivalPlan
    {
        /// <summary>The chance chute keeps it (staked); the manifest says where it went.</summary>
        HandledBelow,
        /// <summary>Lowered into a sealed holder (a pawn that is not an awake colonist).</summary>
        IntoHolder,
        /// <summary>Dropped near the destination cell.</summary>
        Drop,
    }

    public enum CaptureKind { None, Prisoner, Bound }

    /// <summary>The per-thing schedule that rides alongside the transit ThingOwner: index i of each list belongs to the
    /// owner's i-th thing. Saved under the same keys as before (arriveAt / goingUp / fromLabel).</summary>
    public sealed class RM_TransitSchedule
    {
        public List<int> arriveAt = new List<int>();
        public List<bool> goingUp = new List<bool>();
        public List<string> fromLabel = new List<string>();

        public int Count { get { return arriveAt.Count; } }

        public void Add(int arriveTick, bool up, string from)
        {
            arriveAt.Add(arriveTick);
            goingUp.Add(up);
            fromLabel.Add(from);
        }

        public bool IsDue(int i, int now) { return !(i < arriveAt.Count && arriveAt[i] > now); }
        public bool Up(int i) { return i < goingUp.Count && goingUp[i]; }
        public string From(int i) { return i < fromLabel.Count ? fromLabel[i] : "?"; }

        public void RemoveAt(int i)
        {
            arriveAt.RemoveAt(i);
            goingUp.RemoveAt(i);
            fromLabel.RemoveAt(i);
        }

        /// <summary>Could not land it now (nowhere to put it): keep it on the cable and try again later.</summary>
        public void Defer(int i, int until)
        {
            if (i < arriveAt.Count) arriveAt[i] = until;
        }

        /// <summary>After load: lists missing or shorter than the owner are padded (arrive at once, going down, "?").</summary>
        public void PadTo(int ownerCount)
        {
            arriveAt = arriveAt ?? new List<int>();
            goingUp = goingUp ?? new List<bool>();
            fromLabel = fromLabel ?? new List<string>();
            while (arriveAt.Count < ownerCount) arriveAt.Add(0);
            while (goingUp.Count < ownerCount) goingUp.Add(false);
            while (fromLabel.Count < ownerCount) fromLabel.Add("?");
        }

        public int Soonest()
        {
            if (arriveAt.Count == 0) return 0;
            int m = arriveAt[0];
            for (int i = 1; i < arriveAt.Count; i++) if (arriveAt[i] < m) m = arriveAt[i];
            return m;
        }

        /// <summary>One hoist tick: everything whose time has come lands, last index first (so a landing never shifts a lower index).</summary>
        public void Tick<S>(S sink, int now) where S : IHoistTransitSink
        {
            for (int i = sink.TransitCount - 1; i >= 0; i--)
            {
                if (!IsDue(i, now)) continue;
                sink.ArriveAt(i);
            }
        }

        /// <summary>Proof hook: everything now in transit arrives at once.</summary>
        public void ArriveAllNow<S>(S sink) where S : IHoistTransitSink
        {
            for (int i = 0; i < arriveAt.Count; i++) arriveAt[i] = 0;
            for (int i = sink.TransitCount - 1; i >= 0; i--)
            {
                if (i < sink.TransitCount) sink.ArriveAt(i);
            }
        }
    }

    public static class RM_HoistKernel
    {
        public const int BaseCycleTicks = 625;   // a quarter hour for a weightless load
        public const int MinCycleTicks = 60;
        public const float CradleRadius = 1.5f;
        public const int ManifestCap = 200;
        public const int RollsCap = 50;
        public const int TicksPerHour = 2500;
        public const int TicksPerDay = 60000;
        public const int OpenLineMinute = 137;
        public const float OpenLineRisePerHour = 1f;
        public const float OpenLineFallPerHour = 0.5f;
        public const int MeleeFighterSkill = 8;
        public const float BeastFighterCombatPower = 100f;

        // ---- timing ---------------------------------------------------------------------------------------------

        /// <summary>mass is the pawn's body mass or the stack's mass (per-thing mass x stackCount).</summary>
        public static int CycleTicks(float mass, float cycleTimeMultiplier)
        {
            return Math.Max(MinCycleTicks, (int)Math.Round(BaseCycleTicks * cycleTimeMultiplier * (1f + mass / 50f)));
        }

        public static ArrivalPlan PlanArrival(bool up, bool handlesBelow, bool holderAcceptsThis)
        {
            if (!up && handlesBelow) return ArrivalPlan.HandledBelow;
            if (holderAcceptsThis) return ArrivalPlan.IntoHolder;
            return ArrivalPlan.Drop;
        }

        /// <summary>holderAcceptsThis: the cable ends in a spawned holder, the thing is a pawn, and it is not an awake colonist.</summary>
        public static bool GoesIntoHolder(bool up, bool holderSpawned, bool isPawn, bool isColonist, bool downed)
        {
            return !up && holderSpawned && isPawn && !(isColonist && !downed);
        }

        /// <summary>The manifest is a ring: oldest entries fall off past the cap.</summary>
        public static void CapList<T>(List<T> list, int cap)
        {
            if (list.Count > cap) list.RemoveAt(0);
        }

        // ---- gates ----------------------------------------------------------------------------------------------

        /// <summary>null when enterable; else why not.</summary>
        public static string EnterRefusal(bool masterEnabled, bool cableDown, bool powered)
        {
            if (!masterEnabled) return "off";
            if (!cableDown) return "cable";
            if (!powered) return "power";
            return null;
        }

        /// <summary>A rider who walks in is held in transit unless riding is off and they are an awake colonist.</summary>
        public static bool HoldsRiderInTransit(bool colonistsMayRide, bool isColonist, bool downed)
        {
            return !(!colonistsMayRide && isColonist && !downed);
        }

        public static bool TetherBlocksLaunch(bool accepted, bool tetherLock, bool hasMap, bool defKnown, bool cableDownOnSubstructure)
        {
            return accepted && tetherLock && hasMap && defKnown && cableDownOnSubstructure;
        }

        public static bool PortalInReach(float distance, float range, float portalSizeX) { return !(distance > range + portalSizeX); }
        public static bool CellInReach(float distance, float range) { return !(distance > range); }

        public static CaptureKind CaptureFor(bool downedStrangersAndBeasts, bool dead, bool playerFaction, bool humanlike, bool prisonerOrSlave, bool hasGuest,
            bool animal, bool factionless)
        {
            if (!downedStrangersAndBeasts || dead || playerFaction) return CaptureKind.None;
            if (humanlike)
            {
                if (prisonerOrSlave || !hasGuest) return CaptureKind.None;
                return CaptureKind.Prisoner;
            }
            if (animal && factionless) return CaptureKind.Bound;
            return CaptureKind.None;
        }

        public static int RestraintTicks(float restraintHours) { return (int)Math.Round(restraintHours * TicksPerHour); }

        /// <summary>The cradle lifts: ours (or ours by captivity) if riding is allowed for them, and any downed stranger when captures are on.</summary>
        public static bool CradleTakesPawn(bool ours, bool colonistsMayRide, bool downed, bool isColonist, bool downedStrangersAndBeasts)
        {
            bool rider = ours && (colonistsMayRide || downed || !isColonist);
            bool capturable = downed && downedStrangersAndBeasts;
            return rider || capturable;
        }

        public static bool IsLowerableCaptive(bool dead, bool downed, bool playerFaction, bool prisonerOrSlaveOfColony, bool allowedOnCaravan, bool questHelperOrLodger,
            bool humanlike, bool hasGuest, bool willJoinIfRescued, bool animal, bool factionless)
        {
            if (dead || !downed || playerFaction || prisonerOrSlaveOfColony) return false;
            if (!allowedOnCaravan || questHelperOrLodger) return false;
            if (humanlike) return hasGuest && !willJoinIfRescued;
            return animal && factionless;
        }

        /// <summary>Which awake colonists the dialog hides: all of them when riding is off or the cable ends in a holder; at a buyer pit or the
        /// chance chute every colonist who is not a slave.</summary>
        public static bool DialogHidesPawn(bool colonistsMayRide, bool holderCable, bool buyerOrChute, bool isColonist, bool downed, bool isSlave)
        {
            if ((!colonistsMayRide || holderCable) && isColonist && !downed) return true;
            if (buyerOrChute && isColonist && !isSlave) return true;
            return false;
        }

        // ---- sealed holder / pit ---------------------------------------------------------------------------------

        /// <summary>null when accepted; else a refusal code.</summary>
        public static string HolderRefusal(bool hasBuyer, bool isColonist, bool isSlave, bool factionHostileToPlayer, bool factionIsOther, bool gateOpen)
        {
            if (!hasBuyer) return null;
            if (isColonist && !isSlave) return "own";
            if (factionIsOther && factionHostileToPlayer && !gateOpen) return "enemy";
            return null;
        }

        /// <summary>Open when nobody holds the place: no owner, the player's, a player-owned map, a defeated owner, or no able keeper left.</summary>
        public static bool GateOpen(bool ownerNullOrPlayerOrDefeated, bool mapPlayerOwned, bool keepersLeft)
        {
            if (ownerNullOrPlayerOrDefeated || mapPlayerOwned) return true;
            return !keepersLeft;
        }

        public static bool KeepersBuying(bool hasBuyer, bool pitSales, bool factionOther, bool hostile, bool gateOpen)
        {
            return hasBuyer && pitSales && factionOther && !hostile && !gateOpen;
        }

        public static bool IsFighter(bool humanlike, int meleeLevel, float combatPower)
        {
            return humanlike ? meleeLevel >= MeleeFighterSkill : combatPower >= BeastFighterCombatPower;
        }

        public static int WeekOf(int ticksGame) { return ticksGame / (TicksPerDay * 7); }

        public static int Price(float marketValue, float priceMultiplier, bool fighter, bool arenaWants, float fighterBonus)
        {
            float price = marketValue * priceMultiplier;
            if (fighter && arenaWants) price *= fighterBonus;
            return Math.Max(1, (int)Math.Round(price));
        }

        /// <summary>One transit per stack so none exceeds the stack limit; the stacks sum to the amount.</summary>
        public static List<int> SilverStacks(int amount, int stackLimit)
        {
            var stacks = new List<int>();
            while (amount > 0)
            {
                int n = Math.Min(amount, stackLimit);
                amount -= n;
                stacks.Add(n);
            }
            return stacks;
        }

        // ---- the chance chute -----------------------------------------------------------------------------------

        /// <summary>The first stake starts the clock; later stakes ride the same roll.</summary>
        public static int NextRollAt(int rollAt, int now, int chuteTicks) { return rollAt < 0 ? now + chuteTicks : rollAt; }
        public static bool RollDue(int rollAt, int now) { return rollAt >= 0 && now >= rollAt; }

        /// <summary>Jackpot below j, bust below j + b, otherwise the middle band (the caller draws it, only when needed).</summary>
        public static float RollMultiplier(float r, float jackpotChance, float bustChance, Func<float> middle)
        {
            if (r < jackpotChance) return 3f;
            if (r < jackpotChance + bustChance) return 0.3f;
            return middle();
        }

        public static float Payout(float stake, float houseCut, float multiplier) { return stake * (1f - houseCut) * multiplier; }

        /// <summary>Mean multiplier of the three bands, the middle being uniform on [0.7, 1.1].</summary>
        public static double ExpectedMultiplier(double jackpot, double bust)
        {
            double middle = Math.Max(0.0, 1.0 - jackpot - bust);
            return jackpot * 3.0 + bust * 0.3 + middle * 0.9;
        }

        public const float CrateItemSetThreshold = 150f;
        public static bool CrateNeedsItemSet(float value) { return value >= CrateItemSetThreshold; }
        public static bool CrateIsEmpty(float value) { return value < 1f; }
        /// <summary>Silver topping the crate up to its value after the item set.</summary>
        public static int CrateSilver(float value, float gotFromSet) { return (int)Math.Floor(value - gotFromSet); }

        // ---- Open Line --------------------------------------------------------------------------------------------

        public static bool OpenLineStepsNow(bool openLineMeter, int ticksGame, bool defKnown)
        {
            return openLineMeter && ticksGame % TicksPerHour == OpenLineMinute && defKnown;
        }
        public static float OpenLineNext(float level, bool open)
        {
            return open ? level + OpenLineRisePerHour : Math.Max(0f, level - OpenLineFallPerHour);
        }
    }
}
