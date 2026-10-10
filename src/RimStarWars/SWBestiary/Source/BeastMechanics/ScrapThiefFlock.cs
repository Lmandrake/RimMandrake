using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // SCRAPNEST_BIRD_BASE_THEFT_1 — scrap-nest birds rob the colony.
    //
    // Owner rulings, verbatim:
    //   2026-09-21: "Yes, stored items. And flocks come as events. And game
    //               alerts you when theft occurs."
    //   2026-10-10: "I already ruled on this in the past 3+4. Yes they steal
    //               everything, and there are also stealing raids."
    // = the card's option (c) (stockpiles and the home area too, for the
    // ambient birds) AND option (d) (a periodic raiding-flock incident), plus
    // an alert whenever a theft happens.
    //
    // ⚠️ PROVISIONAL: both Mod Settings default ON. The owner never answered
    // the card's on/off-by-default question; ON matches "they steal
    // everything" and the existing scrapHoardingEnabled default. Re-rule it if
    // that reads wrong in play.
    //
    // What "everything" means here: everything the bird already hoards
    // (CompProperties_ScrapHoarder.hoardableDefs — components, precious
    // metals, steel, plasteel, uranium) from EVERYWHERE, stockpiles and shelves
    // included. The bird's list was not widened to every item in the game.
    //
    // 🔴 What is NOT relaxed: a nest is never sited inside the home area
    // (JobGiver_HoardScrap.TryFindNestCell). The birds rob the colony and nest
    // outside it, so the loot stays recoverable — the item's own "the nest is
    // where the evidence goes" requirement.
    //
    // Pieces, all here except the giver/driver edits:
    //   * RSW_ScrapThiefFlock — MapComponent remembering which birds are a
    //     live raiding flock (they steal whatever the ambient toggle says) and
    //     throttling the theft alert;
    //   * IncidentWorker_ScrapThiefFlock — the "stealing raid": a flock flies
    //     in at the map edge, heads for the colony, steals, and leaves when
    //     vanilla's exitMapAfterTick runs out (the ThrumboPasses pattern,
    //     MEASURED in the decompiled 1.6 source; Animal.xml's
    //     ThinkNode_ConditionalExitTimedOut walks it off the map).
    // ════════════════════════════════════════════════════════════════════
    public class RSW_ScrapThiefFlock : MapComponent
    {
        private List<Pawn> flock = new List<Pawn>();
        private bool letterSent;
        private int lastMessageTick = -1;

        // One theft message per map per in-game hour; the flock's first theft gets a letter.
        private const int MessageWindowTicks = 2500;

        public RSW_ScrapThiefFlock(Map map) : base(map)
        {
        }

        public static RSW_ScrapThiefFlock For(Map map) => map?.GetComponent<RSW_ScrapThiefFlock>();

        public void StartRaid(IEnumerable<Pawn> birds)
        {
            Prune();
            flock.AddRange(birds);
            letterSent = false;
        }

        private void Prune()
        {
            flock.RemoveAll(p => p == null || p.Dead || !p.Spawned || p.Map != map
                || (p.mindState != null && RSW_HoardKernel.RaidOver(p.mindState.exitMapAfterTick, Find.TickManager.TicksGame)));
        }

        public static bool IsRaiding(Pawn pawn)
        {
            RSW_ScrapThiefFlock comp = For(pawn?.Map);
            if (comp == null || comp.flock.Count == 0 || !comp.flock.Contains(pawn))
            {
                return false;
            }
            return pawn.mindState == null || !RSW_HoardKernel.RaidOver(pawn.mindState.exitMapAfterTick, Find.TickManager.TicksGame);
        }

        /// <summary>Called by JobDriver_HoardScrap the moment a bird lifts an item that was in the home area or storage.</summary>
        public static void NotifyTheft(Pawn thief, Thing stolen)
        {
            RSW_ScrapThiefFlock comp = For(thief?.Map);
            if (comp == null || stolen == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            string what = stolen.LabelCap;
            if (comp.flock.Contains(thief) && !comp.letterSent)
            {
                comp.letterSent = true;
                comp.lastMessageTick = now;
                Find.LetterStack.ReceiveLetter("Scrap birds robbing you",
                    "A raiding flock of " + thief.def.label + "s is in your colony and has just carried off " + what
                    + ". They take components, precious metals and steel from stockpiles and shelves alike, and fly it to a nest "
                    + "outside your base. Shoot them, or find the nest afterwards: everything they steal ends up in it.",
                    LetterDefOf.NegativeEvent, new LookTargets(thief));
                return;
            }
            if (!RSW_HoardKernel.TheftMessageDue(comp.lastMessageTick, now, MessageWindowTicks))
            {
                return;
            }
            comp.lastMessageTick = now;
            Messages.Message("A " + thief.def.label + " stole " + what + " from your colony. It will be in a scrap nest outside the base.",
                new LookTargets(thief), MessageTypeDefOf.NegativeEvent);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                Prune();
            }
            Scribe_Collections.Look(ref flock, "rswScrapThiefFlock", LookMode.Reference);
            Scribe_Values.Look(ref letterSent, "rswScrapThiefLetterSent", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (flock == null) flock = new List<Pawn>();
                flock.RemoveAll(p => p == null);
            }
        }
    }

    public class IncidentWorker_ScrapThiefFlock : IncidentWorker
    {
        private const string BirdKind = "RSW_ScrapNestBird";

        private static PawnKindDef Kind => DefDatabase<PawnKindDef>.GetNamedSilentFail(BirdKind);

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (!RSW_BeastMechanicsSettings.scrapHoardingEnabled || !RSW_BeastMechanicsSettings.scrapThiefFlockEnabled
                || map == null || Kind == null)
            {
                return false;
            }
            // Only where the bird actually lives — a flock of shrubland scavengers does not raid an ice sheet.
            if (map.Biome == null || map.Biome.CommonalityOfAnimal(Kind) <= 0f)
            {
                return false;
            }
            if (!map.mapTemperature.SeasonAndOutdoorTemperatureAcceptableFor(Kind.race))
            {
                return false;
            }
            return map.areaManager.Home.TrueCount > 0 && RCellFinder.TryFindRandomPawnEntryCell(out _, map, CellFinder.EdgeRoadChance_Animal);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            PawnKindDef kind = Kind;
            if (kind == null || !RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Animal))
            {
                return false;
            }
            IntVec3 target = TargetCell(map);
            int count = Rand.RangeInclusive(3, 6);
            // Half a day to a day in the colony, then vanilla's ExitTimedOut node flies them off.
            int leaveAt = Find.TickManager.TicksGame + Rand.Range(30000, 60000);
            var birds = new List<Pawn>();
            for (int i = 0; i < count; i++)
            {
                Pawn bird = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(bird, CellFinder.RandomClosewalkCellNear(entry, map, 6), map, Rot4.Random);
                bird.mindState.exitMapAfterTick = leaveAt;
                if (target.IsValid)
                {
                    bird.mindState.forcedGotoPosition = CellFinder.RandomClosewalkCellNear(target, map, 6);
                }
                birds.Add(bird);
            }
            RSW_ScrapThiefFlock.For(map)?.StartRaid(birds);
            SendStandardLetter("Scrap birds incoming",
                "A flock of " + count + " " + kind.labelPlural + " is heading for your colony. They are thieves: they will carry off "
                + "components, precious metals and steel — out of your stockpiles and shelves too — and fly it to a nest outside your base.",
                LetterDefOf.ThreatSmall, parms, birds[0]);
            return true;
        }

        /// <summary>A stockpile cell if the colony has one (that is what they come for), else a home-area cell.</summary>
        private static IntVec3 TargetCell(Map map)
        {
            List<Zone_Stockpile> piles = map.zoneManager.AllZones.OfType<Zone_Stockpile>().Where(z => z.cells.Count > 0).ToList();
            if (piles.Count > 0)
            {
                return piles.RandomElement().cells.RandomElement();
            }
            if (map.areaManager.Home.ActiveCells.TryRandomElement(out IntVec3 c))
            {
                return c;
            }
            return IntVec3.Invalid;
        }
    }
}
