using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.StarWars.SithLine
{
    /// <summary>
    /// SANGUOPHAGE_KEPT_UNREACHABLE_1 design §3 — the Abyss lair. Owner card 2026-10-09: "a RARE hidden lair site holding
    /// one lone Sith and their structures, which the player cannot build. The player raids it for loot"; "A lair is
    /// found by a rare rumour quest." Vanilla QuestNode_GetSiteTile has no biome filter, so this node picks an RM_Abyss
    /// tile near a player map. No Abyss def (biomes mod absent) or no Abyss tile in range: TestRun fails and the quest
    /// never offers. A planet with zero Abyss tiles today is the EXPECTED state (CLAUDE.md: painted once, at the end).
    /// </summary>
    public class RSW_QuestNode_GetAbyssSiteTile : QuestNode
    {
        [NoTranslate]
        public SlateRef<string> storeAs;

        public const string AbyssDefName = "RM_Abyss";

        protected override bool TestRunInt(Slate slate)
        {
            if (!RSW_SithLineSettings.lairRumours || OpenLairExists())
            {
                return false;
            }
            if (!TryFind(slate, out PlanetTile tile))
            {
                return false;
            }
            slate.Set(storeAs.GetValue(slate), tile);
            return true;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            if (TryFind(slate, out PlanetTile tile))
            {
                slate.Set(storeAs.GetValue(slate), tile);
            }
        }

        /// <summary>Design §3: at most one open lair at a time.</summary>
        public static bool OpenLairExists()
        {
            SitePartDef lair = DefDatabase<SitePartDef>.GetNamedSilentFail("RSW_SithLair");
            if (lair == null)
            {
                return false;
            }
            foreach (Site s in Find.WorldObjects.Sites)
            {
                if (s.parts != null && s.parts.Any(p => p.def == lair))
                {
                    return true;
                }
            }
            return false;
        }

        private static bool TryFind(Slate slate, out PlanetTile tile)
        {
            tile = PlanetTile.Invalid;
            BiomeDef abyss = DefDatabase<BiomeDef>.GetNamedSilentFail(AbyssDefName);
            Map map = slate.Get<Map>("map");
            if (abyss == null || map == null)
            {
                return false;
            }
            int radius = RSW_SithLineSettings.lairSearchRadius < 1 ? 1 : RSW_SithLineSettings.lairSearchRadius;
            return TileFinder.TryFindNewSiteTile(out tile, map.Tile, 1, radius, allowCaravans: false, allowedLandmarks: null,
                selectLandmarkChance: 0f, canSelectComboLandmarks: false, tileFinderMode: TileFinderMode.Random,
                exitOnFirstTileFound: false, canBeSpace: false, layer: null,
                validator: t => Find.WorldGrid[t].PrimaryBiome == abyss);
        }
    }

    /// <summary>
    /// The sanctum: about 13x13, carved at the map centre, walled in granite with one door, dark floor (RM_EtchHollow when
    /// the biomes mod is loaded, otherwise vanilla slate flagstone), rock-roofed. A Sith sarcophagus at the centre holds
    /// one lone Sith adept in dark trance (vanilla deathrest, no new mechanic) with two to four bound devices around it,
    /// and a loot shelf against the back wall. ⚠️ The devices are unpowered: their bonuses need power (UNMEASURED live).
    /// </summary>
    public class RSW_GenStep_SithLair : GenStep
    {
        public int radius = 6;
        public IntRange boundDevices = new IntRange(2, 4);
        public IntRange essenceVials = new IntRange(2, 5);
        public float traceSerumChance = 0.5f;

        public override int SeedPart => 0x5174A1;

        private static readonly string[] Devices = { "Hemopump", "HemogenAmplifier", "GlucosoidPump", "PsychofluidPump", "DeathrestAccelerator" };

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!ModsConfig.BiotechActive)
            {
                return;
            }
            IntVec3 center = map.Center;
            CellRect rect = CellRect.CenteredOn(center, radius).ClipInsideMap(map);
            if (rect.Width < 9 || rect.Height < 9)
            {
                Log.Warning("[SithLine] lair map too small for a sanctum; skipped.");
                return;
            }
            TerrainDef floor = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_EtchHollow")
                ?? DefDatabase<TerrainDef>.GetNamedSilentFail("FlagstoneSlate") ?? TerrainDefOf.Concrete;
            ThingDef stone = ThingDefOf.BlocksGranite;
            foreach (IntVec3 c in rect)
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (!(t is Pawn))
                    {
                        t.Destroy();
                    }
                }
                map.terrainGrid.SetTerrain(c, floor);
                map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThin);
            }
            IntVec3 door = new IntVec3(rect.CenterCell.x, 0, rect.minZ);
            foreach (IntVec3 c in rect.EdgeCells)
            {
                Thing wall = ThingMaker.MakeThing(c == door ? ThingDefOf.Door : ThingDefOf.Wall, stone);
                GenSpawn.Spawn(wall, c, map);
            }

            Faction sith = SithFaction();
            Building casket = Spawn("DeathrestCasket", rect.CenterCell, Rot4.South, map, sith);
            // two to four bound devices, east-facing, in slots left and right of the sarcophagus
            IntVec3 cc = rect.CenterCell;
            List<IntVec3> slots = new List<IntVec3> { cc + new IntVec3(-3, 0, 1), cc + new IntVec3(2, 0, 1), cc + new IntVec3(-3, 0, -2), cc + new IntVec3(2, 0, -2) };
            int n = boundDevices.RandomInRange;
            List<string> picks = Devices.InRandomOrder().Take(n).ToList();
            for (int i = 0; i < picks.Count && i < slots.Count; i++)
            {
                Spawn(picks[i], slots[i], Rot4.East, map, sith);
            }
            // the loot shelf against the back (north) wall
            ThingDef shelfDef = DefDatabase<ThingDef>.GetNamedSilentFail("Shelf");
            IntVec3 shelfCell = new IntVec3(cc.x, 0, rect.maxZ - 1);
            if (shelfDef != null)
            {
                Thing shelf = ThingMaker.MakeThing(shelfDef, stone);
                GenSpawn.Spawn(shelf, shelfCell, map, Rot4.South);
            }
            float points = parms.sitePart?.parms?.points ?? 500f;
            PlaceLoot(map, shelfCell, points);

            if (casket != null && sith != null)
            {
                Pawn adept = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Sanguophage, sith,
                    PawnGenerationContext.NonPlayer, map.Tile, forceGenerateNewPawn: true, mustBeCapableOfViolence: true));
                GenSpawn.Spawn(adept, casket.Position, map);
                StartTrance(adept, casket as Building_Bed);
                map.GetComponent<RSW_MapComponent_SithLair>()?.Register(adept, rect,
                    RSW_SithLineKernel.WakeTick(Find.TickManager.TicksGame, Rand.Value));
            }
        }

        private static Building Spawn(string defName, IntVec3 cell, Rot4 rot, Map map, Faction faction)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (d == null)
            {
                return null;
            }
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? ThingDefOf.BlocksGranite : null);
            if (faction != null)
            {
                t.SetFaction(faction);
            }
            return GenSpawn.Spawn(t, cell, map, rot) as Building;
        }

        private void PlaceLoot(Map map, IntVec3 at, float points)
        {
            void Put(string defName, int count)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                if (d == null || count <= 0)
                {
                    return;
                }
                Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
                t.stackCount = System.Math.Min(count, d.stackLimit);
                GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
            }
            Put("RSW_SithHolocron", 1);
            Put("guy762_SithHood_masked", 1);
            Put("HemogenPack", essenceVials.RandomInRange);
            if (Rand.Chance(traceSerumChance))
            {
                Put("DeathrestCapacitySerum", 1);
            }
            int silver = RSW_SithLineKernel.LootSilver(points);
            Put("Silver", silver);
            Put("Gold", silver / 20);
        }

        /// <summary>The lair's own hidden Sith faction, generated the way vanilla QuestNode_Root_SanguophageShip does.</summary>
        private static Faction SithFaction()
        {
            Faction f = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(x => x.def == FactionDefOf.Sanguophages && !x.defeated);
            if (f != null)
            {
                return f;
            }
            List<FactionRelation> rel = new List<FactionRelation>();
            foreach (Faction other in Find.FactionManager.AllFactionsListForReading)
            {
                rel.Add(new FactionRelation(other, FactionRelationKind.Hostile));
            }
            f = FactionGenerator.NewGeneratedFactionWithRelations(FactionDefOf.Sanguophages, rel, hidden: true);
            Find.FactionManager.Add(f);
            return f;
        }

        /// <summary>Vanilla deathrest, started the way a tucked-in deathrester starts it (links the nearby devices).</summary>
        public static void StartTrance(Pawn adept, Building_Bed casket)
        {
            Gene_Deathrest gene = adept.genes?.GetFirstGeneOfType<Gene_Deathrest>();
            if (gene == null || casket == null)
            {
                return;
            }
            gene.autoWake = true;
            if (!adept.Deathresting)
            {
                adept.health.AddHediff(HediffDefOf.Deathrest);
            }
            adept.jobs.Notify_TuckedIntoBed(casket);
        }
    }

    public class RSW_SithLairRecord : IExposable
    {
        public Pawn adept;
        public CellRect sanctum;
        public int wakeTick;
        public float lastHealth = 1f;
        public bool woke;

        public void ExposeData()
        {
            Scribe_References.Look(ref adept, "adept");
            Scribe_Values.Look(ref sanctum, "sanctum");
            Scribe_Values.Look(ref wakeTick, "wakeTick");
            Scribe_Values.Look(ref lastHealth, "lastHealth", 1f);
            Scribe_Values.Look(ref woke, "woke");
        }
    }

    /// <summary>Wakes the lair Sith on damage, an intruder in the sanctum, or after 6-10 hours (RSW_SithLineKernel.ShouldWake).
    /// Waking early is vanilla's broken trance (InterruptedDeathrest). Once risen, their lord defends the sanctum.</summary>
    public class RSW_MapComponent_SithLair : MapComponent
    {
        private List<RSW_SithLairRecord> lairs = new List<RSW_SithLairRecord>();

        public RSW_MapComponent_SithLair(Map map) : base(map)
        {
        }

        public void Register(Pawn adept, CellRect sanctum, int wakeTick)
        {
            lairs.Add(new RSW_SithLairRecord { adept = adept, sanctum = sanctum, wakeTick = wakeTick });
        }

        public override void MapComponentTick()
        {
            if (lairs.Count == 0 || Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            for (int i = lairs.Count - 1; i >= 0; i--)
            {
                RSW_SithLairRecord r = lairs[i];
                Pawn p = r.adept;
                if (p == null || p.Dead || !p.Spawned || p.Map != map)
                {
                    lairs.RemoveAt(i);
                    continue;
                }
                if (r.woke)
                {
                    continue;
                }
                float hp = p.health.summaryHealth.SummaryHealthPercent;
                bool hurt = hp < r.lastHealth - 0.001f;
                r.lastHealth = hp;
                bool intruder = false;
                foreach (Pawn q in map.mapPawns.FreeColonistsSpawned)
                {
                    if (r.sanctum.Contains(q.Position))
                    {
                        intruder = true;
                        break;
                    }
                }
                if (!p.Deathresting || RSW_SithLineKernel.ShouldWake(true, hurt, intruder, now, r.wakeTick))
                {
                    Rise(r, hurt || intruder);
                }
            }
        }

        private void Rise(RSW_SithLairRecord r, bool broken)
        {
            Pawn p = r.adept;
            r.woke = true;
            if (p.Deathresting)
            {
                if (broken)
                {
                    // torn out early: vanilla Wake() applies InterruptedDeathrest ("broken trance") below 100%
                    p.genes?.GetFirstGeneOfType<Gene_Deathrest>()?.Wake();
                }
                else
                {
                    // risen in its own time: end the trance without the broken-trance sickness
                    Hediff h = p.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.Deathrest);
                    if (h != null)
                    {
                        p.health.RemoveHediff(h);
                    }
                }
            }
            if (p.Faction != null && p.GetLord() == null)
            {
                LordMaker.MakeNewLord(p.Faction, new LordJob_DefendPoint(r.sanctum.CenterCell), map, new List<Pawn> { p });
            }
            Messages.Message("RSW_SithLairRises".Translate(p.LabelShort), p, MessageTypeDefOf.ThreatBig);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref lairs, "lairs", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && lairs == null)
            {
                lairs = new List<RSW_SithLairRecord>();
            }
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                lairs.RemoveAll(x => x == null || x.adept == null);
            }
        }
    }
}
