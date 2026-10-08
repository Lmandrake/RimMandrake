using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.NightsideIce
{
    // NIGHTSIDEICE_BREACH_CRACKS_1 (split from NIGHTSIDEICE_HEAT_DIAL_BUILD_1 item 2; design
    // nightsideice_bedazzle_review_2026-10-01.md section 4 row 1). The breach loop: the heat dial draws
    // the shivven, and a staging crack opens in open ice at the base's edge where they will come up.
    //
    //   - RM_BreachLoop (MapComponent), hourly, Nightside Ice maps with the dial on: no crack open, dial
    //     at least BreachThreshold, not cooling down -> chance breachFrequencyScale x dial^2 / 24 per hour
    //     (the hourly chance alone would average one breach a day at a full dial and one in four days at half a dial,
    //     but a crack starts a two-day cooldown, so measured (fuzz): a full dial opens one about every 71 hours, half a dial about
    //     every 143; zero dial never).
    //   - The crack (RM_Building_BreachCrack) opens only on open ice: Ice terrain, standable, unroofed, no
    //     edifice, 3 to 12 cells from the nearest player building (the base's edge, never a floor, since a
    //     floor is not Ice: the hull rule). It is an ordinary attackable building: destroy it in time and
    //     the breach is stopped.
    //   - When its timer runs out it breaks: 2 + dial x 6 shivven come up around it and it is gone.
    //   - The FIRST crack on a map is taught: a letter naming the dial, what raised it and the countdown,
    //     then warnings at 6 h and 1 h (Anomaly's pit-gate tiers in shape). Later cracks get one vague
    //     message and no countdown on the crack.
    public class RM_BreachLoop : MapComponent
    {
        public const float BreachThreshold = RM_NightsideIceKernel.BreachThreshold;
        public const int CooldownTicks = RM_NightsideIceKernel.CooldownTicks;

        public bool firstTaught;
        public int cooldownUntil = -1;
        public RM_Building_BreachCrack open;

        public RM_BreachLoop(Map map) : base(map)
        {
        }

        public static RM_BreachLoop For(Map map)
        {
            return map?.GetComponent<RM_BreachLoop>();
        }

        public bool Applies
        {
            get
            {
                RM_HeatDial dial = RM_HeatDial.For(map);
                return RM_NightsideIceSettings.breachEnabled && dial != null && dial.Applies;
            }
        }

        public override void MapComponentTick()
        {
            // Five ticks after the dial's own hourly update (RM_HeatDial, offset 71).
            if (!RM_NightsideIceKernel.BreachDue(Find.TickManager.TicksGame))
            {
                return;
            }
            if (open != null && (open.Destroyed || !open.Spawned))
            {
                open = null;
            }
            bool applies = Applies;
            float d = applies ? RM_HeatDial.For(map).dial : 0f;
            if (!RM_NightsideIceKernel.BreachRollMade(applies, open != null, Find.TickManager.TicksGame, cooldownUntil, d))
            {
                return;
            }
            float chance = RM_NightsideIceKernel.BreachChance(RM_NightsideIceSettings.breachFrequencyScale, d);
            if (Rand.Chance(chance))
            {
                TryOpen(d, out _);
            }
        }

        /// <summary>Opens a crack now (the proofs call this directly). Null reason on success.</summary>
        public RM_Building_BreachCrack TryOpen(float dialValue, out string reason)
        {
            reason = null;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_BreachCrack");
            if (def == null)
            {
                reason = "RM_BreachCrack not loaded";
                return null;
            }
            if (!TryFindCrackCell(map, out IntVec3 cell))
            {
                reason = "no open ice 3-12 cells from the base";
                return null;
            }
            var crack = (RM_Building_BreachCrack)ThingMaker.MakeThing(def);
            bool teach = !firstTaught;
            int hours = RM_NightsideIceKernel.BreakHours(teach, RM_NightsideIceSettings.breachFirstCountdownHours, teach ? 0 : Rand.RangeInclusive(8, 16));
            crack.breakTick = Find.TickManager.TicksGame + hours * GenDate.TicksPerHour;
            crack.taught = teach;
            crack.shivvenCount = RM_NightsideIceKernel.ShivvenCount(dialValue);
            GenSpawn.Spawn(crack, cell, map);
            open = crack;
            firstTaught = true;
            cooldownUntil = Find.TickManager.TicksGame + CooldownTicks;

            if (teach)
            {
                RM_HeatDial d = RM_HeatDial.For(map);
                string parts = d == null ? "" : " Your heaters count for " + d.heaters.ToString("0") + ", fires "
                    + d.fires.ToString("0") + ", running machines " + d.power.ToString("0") + " and heated rooms "
                    + d.rooms.ToString("0") + ".";
                Find.LetterStack.ReceiveLetter("The ice is cracking",
                    "The colony's warmth carries through the ice: the thermal signature reads "
                    + Mathf.RoundToInt(dialValue * 100f) + "%." + parts
                    + "\n\nThings in the ice feel it. A crack has opened at the edge of the base where the shivven, blind "
                    + "tunnelers that hunt heat, are working their way up. In about " + hours + " hours it will break open "
                    + "and they will come through.\n\nDestroy the crack before then and they cannot. Less heat means "
                    + "fewer and later cracks; they never open through a floor.",
                    LetterDefOf.ThreatBig, new LookTargets(crack));
            }
            else if (RM_NightsideIceSettings.breachWarnings)
            {
                Messages.Message("Something knocks under the ice near the base.", new LookTargets(crack),
                    MessageTypeDefOf.ThreatSmall, historical: false);
            }
            return crack;
        }

        public static bool TryFindCrackCell(Map map, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            List<Building> colony = map.listerBuildings.allBuildingsColonist;
            if (colony.Count == 0)
            {
                return false;
            }
            Thing anchor = RM_HeatDial.For(map)?.HottestSource() ?? colony.RandomElement();
            for (int attempt = 0; attempt < 3; attempt++)
            {
                int radius = 14 + attempt * 10;
                if (CellFinder.TryFindRandomCellNear(anchor.Position, map, radius, c => IsOpenIceAtEdge(c, map), out cell))
                {
                    return true;
                }
            }
            return false;
        }

        public static bool IsOpenIceAtEdge(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || c.GetTerrain(map) != TerrainDefOf.Ice || !c.Standable(map)
                || c.Roofed(map) || c.GetEdifice(map) != null || c.Fogged(map))
            {
                return false;
            }
            float nearest = float.MaxValue;
            List<Building> colony = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < colony.Count; i++)
            {
                float d = (colony[i].Position - c).LengthHorizontalSquared;
                if (d < nearest)
                {
                    nearest = d;
                }
            }
            return RM_NightsideIceKernel.InEdgeBand(nearest);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref firstTaught, "rmBreachFirstTaught", false);
            Scribe_Values.Look(ref cooldownUntil, "rmBreachCooldownUntil", -1);
            Scribe_References.Look(ref open, "rmBreachOpen");
        }
    }

    /// <summary>The staging crack. Attackable; breaks open at breakTick and lets the shivven up.</summary>
    public class RM_Building_BreachCrack : Building
    {
        public int breakTick = -1;
        public bool taught;
        public int shivvenCount = 3;
        private bool warned6, warned1;

        protected override void Tick()
        {
            base.Tick();
            if (!Spawned || !this.IsHashIntervalTick(60))
            {
                return;
            }
            int left = breakTick - Find.TickManager.TicksGame;
            bool breaks = RM_NightsideIceKernel.CrackLook(left, taught, RM_NightsideIceSettings.breachWarnings, ref warned6, ref warned1,
                out bool say6, out bool say1);
            if (say6)
            {
                Messages.Message("The crack in the ice will break open in about 6 hours.", this, MessageTypeDefOf.ThreatBig);
            }
            if (say1)
            {
                Messages.Message("The crack in the ice is about to break open.", this, MessageTypeDefOf.ThreatBig);
            }
            if (breaks)
            {
                BreakOpen();
            }
        }

        /// <summary>Lets the shivven up and removes the crack. Returns how many came.</summary>
        public int BreakOpen()
        {
            Map map = Map;
            IntVec3 at = Position;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Shivven");
            int made = 0;
            if (kind != null)
            {
                for (int i = 0; i < shivvenCount; i++)
                {
                    IntVec3 c = CellFinder.RandomClosewalkCellNear(at, map, 2);
                    Pawn p = PawnGenerator.GeneratePawn(kind);
                    GenSpawn.Spawn(p, c, map);
                    made++;
                }
            }
            SoundDef crackSound = DefDatabase<SoundDef>.GetNamedSilentFail("RM_ShivvenBreach");
            crackSound?.PlayOneShot(new TargetInfo(at, map));
            ThingDef rubble = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_RubbleRock");
            Destroy(DestroyMode.Vanish);
            if (rubble != null)
            {
                FilthMaker.TryMakeFilth(at, map, rubble, 3);
            }
            Messages.Message(made + " shivven broke up through the ice.", new LookTargets(new TargetInfo(at, map)),
                MessageTypeDefOf.ThreatBig);
            return made;
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine = taught
                ? "Breaks open in " + Mathf.Max(0, breakTick - Find.TickManager.TicksGame).ToStringTicksToPeriod() + "."
                : "Something is moving under it.";
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref breakTick, "rmBreakTick", -1);
            Scribe_Values.Look(ref taught, "rmTaught", false);
            Scribe_Values.Look(ref shivvenCount, "rmShivvenCount", 3);
            Scribe_Values.Look(ref warned6, "rmWarned6", false);
            Scribe_Values.Look(ref warned1, "rmWarned1", false);
        }
    }

    /// <summary>Bridge proofs (jawa/static_call), chain breach_cracks in validation.py. They bypass the biome
    /// and the chance roll; they need a player building on the map and lay ice where none is open.</summary>
    public static class RM_BreachProof
    {
        /// <summary>Opens a crack: "OPEN cell=(x,z) terrain=Ice roofed=False taught=True hours=24 shivven=6".</summary>
        public static string ProofOpen(Map map)
        {
            RM_BreachLoop loop = RM_BreachLoop.For(map);
            if (loop == null)
            {
                return "REFUSED: no breach component";
            }
            if (loop.open != null && loop.open.Spawned)
            {
                return "REFUSED: a crack is already open at " + loop.open.Position;
            }
            if (!RM_BreachLoop.TryFindCrackCell(map, out _))
            {
                LayIceRing(map);
            }
            RM_HeatDial dial = RM_HeatDial.For(map);
            if (dial != null)
            {
                dial.dial = dial.Measure();
            }
            RM_Building_BreachCrack c = loop.TryOpen(Mathf.Max(dial?.dial ?? 0f, 0.6f), out string reason);
            if (c == null)
            {
                return "REFUSED: " + reason;
            }
            return "OPEN cell=" + c.Position + " terrain=" + c.Position.GetTerrain(map).defName + " roofed=" + c.Position.Roofed(map)
                + " floor=" + c.Position.GetTerrain(map).layerable + " taught=" + c.taught
                + " hours=" + ((c.breakTick - Find.TickManager.TicksGame) / GenDate.TicksPerHour) + " shivven=" + c.shivvenCount;
        }

        /// <summary>Breaks the open crack now: "RELEASED 6 crackGone=True".</summary>
        public static string ProofRelease(Map map)
        {
            RM_BreachLoop loop = RM_BreachLoop.For(map);
            RM_Building_BreachCrack c = loop?.open;
            if (c == null || !c.Spawned)
            {
                return "REFUSED: no open crack (ProofOpen first)";
            }
            int n = c.BreakOpen();
            return "RELEASED " + n + " crackGone=" + c.Destroyed;
        }

        /// <summary>Opens a crack, destroys it as an attacker would, runs its timer past zero: "STOPPED shivvenBefore=0 after=0".</summary>
        public static string ProofDestroyStops(Map map)
        {
            string opened = ProofOpen(map);
            RM_BreachLoop loop = RM_BreachLoop.For(map);
            RM_Building_BreachCrack c = loop?.open;
            if (c == null)
            {
                return "REFUSED: " + opened;
            }
            int before = CountShivven(map);
            c.breakTick = Find.TickManager.TicksGame;
            c.Destroy(DestroyMode.KillFinalize);
            int after = CountShivven(map);
            return (after == before && c.Destroyed ? "STOPPED" : "LEAKED") + " shivvenBefore=" + before + " after=" + after
                + " secondTaught=" + c.taught;
        }

        private static int CountShivven(Map map)
        {
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.def.defName == "RM_Shivven")
                {
                    n++;
                }
            }
            return n;
        }

        // A quicktest map has no ice: lay a ring of it 5-8 cells out from the first player building,
        // on natural unroofed ground only.
        private static void LayIceRing(Map map)
        {
            List<Building> colony = map.listerBuildings.allBuildingsColonist;
            if (colony.Count == 0)
            {
                return;
            }
            IntVec3 center = colony[0].Position;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, 8f, true))
            {
                if (c.InBounds(map) && (c - center).LengthHorizontalSquared >= 25 && c.Walkable(map) && !c.Roofed(map)
                    && c.GetEdifice(map) == null && !c.GetTerrain(map).layerable)
                {
                    map.terrainGrid.SetTerrain(c, TerrainDefOf.Ice);
                }
            }
        }
    }
}
