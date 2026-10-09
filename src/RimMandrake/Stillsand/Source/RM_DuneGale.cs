using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_DUNE_GALE_1 — the dune gale. Design:
    // design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md §2.2.
    //
    // One GameCondition carries the whole storm: a herald weather, then the gale
    // weather, then an aftermath run from End(). What each piece is, and where:
    //   dunes march   XML only: a MovingDunes DuneWeatherExtension on the gale WeatherDef.
    //   sun off       XML only: a CreatureBehaviors RM_WeatherSenseExtension on the WeatherDef
    //                 (sunExposureFactor); swimmers blind and the rumble drowned ride it too.
    //   abrasion, carry, static        the gale tick below.
    //   emergence, seeding, wiping     the aftermath below.
    //   carried off the edge           RM_GameComponent_GaleCarried: always a letter, always back.
    //
    // No hard reference to MovingDunes: the wind's bearing is read from its registry by
    // reflection, falling back to the pinned sun's shadow line (the Stillsand's wind blows
    // along the shadows, STILLSAND_WIND_SUN_BEARING_1) and then to a bearing rolled per gale.
    // Sand depth is read straight off Odyssey's Map.sandGrid.
    // ════════════════════════════════════════════════════════════════════

    /// <summary>One row of the emergence table: what the wind uncovers at gale end.</summary>
    public class RM_GaleEmergence
    {
        public string key;
        public float weight = 1f;
        [MustTranslate] public string letterLabel;
        [MustTranslate] public string letterText;

        /// <summary>Items scattered around the face, forbidden.</summary>
        public List<ThingDefCountClass> things;

        /// <summary>Desiccated corpses (generated, killed, rotted to dessicated).</summary>
        public List<PawnKindDefCount> corpses;

        /// <summary>Place one of the giant skeletons (RM_SkeletonPlacer.PlaceableSkeletons).</summary>
        public bool skeleton;

        /// <summary>Open a cave mouth in the nearest natural rock.</summary>
        public bool caveMouth;

        public int scatterRadius = 4;
    }

    /// <summary>On the GameConditionDef. Every number is an INVENTED first value.</summary>
    public class RM_DuneGaleExtension : DefModExtension
    {
        public WeatherDef heraldWeather;
        public WeatherDef galeWeather;

        /// <summary>Share of the duration spent in the herald.</summary>
        public float heraldFraction = 0.15f;

        public int tickInterval = 250;

        /// <summary>Sand depth (0..1) at or above which a cell is a crest.</summary>
        public float crestDepth = 0.45f;
        public int crestDustPerInterval = 6;

        // abrasion
        public float abrasionMtbHours = 3f;
        public IntRange abrasionDamage = new IntRange(1, 2);
        /// <summary>Walls carry no Mass stat in vanilla (Wall's statBases: MaxHitPoints only), so
        /// "light" is read as max hit points: a wood wall (~195) is light, stone is not.</summary>
        public float lightBuildingMaxHitPoints = 220f;
        public float structureMtbHours = 8f;
        public IntRange structureDamage = new IntRange(4, 12);
        public int structureSamplesPerInterval = 30;
        public float roofStripChancePerSample = 0.01f;

        // carry
        public float carryMaxBodySize = 1.0f;
        public float carryMtbHours = 8f;
        public IntRange carryCells = new IntRange(3, 10);
        public IntRange carryBruise = new IntRange(2, 6);
        public ThingDef dragFilth;
        public float returnAliveChance = 0.75f;
        public FloatRange returnDays = new FloatRange(2f, 6f);

        // static
        public float staticMtbHours = 3f;
        public IntRange staticStunTicks = new IntRange(60, 240);
        public int sparkSamplesPerInterval = 6;

        // aftermath
        public List<RM_GaleEmergence> emergences = new List<RM_GaleEmergence>();
        public float wipeDepthDelta = 0.2f;
        public List<ThingDef> wakeRaces = new List<ThingDef>();
        public float wakeRadius = 25f;
        public ThingDef glasscrustPlant;
        public IntRange glasscrustCells = new IntRange(15, 35);
        public ThingDef bloomPlant;
        public float waterSearchRadius = 30f;
        public IntRange bloomCells = new IntRange(8, 20);

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (galeWeather == null)
            {
                yield return "RM_DuneGaleExtension.galeWeather is null: the condition would force no weather.";
            }
            if (emergences.NullOrEmpty())
            {
                yield return "RM_DuneGaleExtension.emergences is empty: the gale would end with no emergence.";
            }
        }
    }

    /// <summary>On the IncidentDef: which biomes the storm happens in (defNames, the
    /// RM_SandLeviathanExtension pattern).</summary>
    public class RM_DuneGaleIncidentExtension : DefModExtension
    {
        public List<string> biomes = new List<string>();

        public bool Allows(Map map)
        {
            return map?.Biome != null && biomes != null && biomes.Contains(map.Biome.defName);
        }
    }

    public class RM_IncidentWorker_DuneGale : IncidentWorker_MakeGameCondition
    {
        public override float BaseChanceThisGame => base.BaseChanceThisGame * RM_DuneGaleSettings.galeFrequency;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_DuneGaleSettings.galeEnabled || !(parms.target is Map map))
            {
                return false;
            }
            RM_DuneGaleIncidentExtension ext = def.GetModExtension<RM_DuneGaleIncidentExtension>();
            if (ext != null && !ext.Allows(map))
            {
                return false;
            }
            return base.CanFireNowSub(parms);
        }
    }

    public class RM_GameCondition_DuneGale : GameCondition
    {
        /// <summary>Raised at gale end with the cells whose sand depth moved past the wipe
        /// threshold. FOOTPRINT_TRACK_GRID_1's grid subscribes to clear its records there
        /// (STILLSAND_SKELETONS_REMAINDER_1 §1); scar filth is already cleared here.</summary>
        public static event Action<Map, List<IntVec3>> TracksWiped;

        private byte[] sandBefore;
        private float massBefore = -1f;
        private int fallbackWindDir = -1;
        private int carried;
        private int abraded;
        private int stunned;

        public RM_DuneGaleExtension Ext => def.GetModExtension<RM_DuneGaleExtension>();

        private int HeraldTicks => Permanent ? 0 : Mathf.RoundToInt(Duration * (Ext?.heraldFraction ?? 0f));

        public bool InGalePhase => TicksPassed >= HeraldTicks;

        public override WeatherDef ForcedWeather()
        {
            RM_DuneGaleExtension ext = Ext;
            if (ext == null)
            {
                return null;
            }
            return !InGalePhase && ext.heraldWeather != null ? ext.heraldWeather : ext.galeWeather;
        }

        public override void Init()
        {
            base.Init();
            Map map = SingleMap;
            SandGrid grid = map?.sandGrid;
            if (grid == null)
            {
                return;
            }
            int n = map.cellIndices.NumGridCells;
            sandBefore = new byte[n];
            for (int i = 0; i < n; i++)
            {
                sandBefore[i] = (byte)Mathf.RoundToInt(Mathf.Clamp01(grid.GetDepth(map.cellIndices.IndexToCell(i))) * 255f);
            }
            massBefore = grid.TotalDepth;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            DataExposeUtility.LookByteArray(ref sandBefore, "rmSandBefore");
            Scribe_Values.Look(ref massBefore, "rmMassBefore", -1f);
            Scribe_Values.Look(ref fallbackWindDir, "rmFallbackWindDir", -1);
            Scribe_Values.Look(ref carried, "rmCarried", 0);
            Scribe_Values.Look(ref abraded, "rmAbraded", 0);
            Scribe_Values.Look(ref stunned, "rmStunned", 0);
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            RM_DuneGaleExtension ext = Ext;
            Map map = SingleMap;
            if (ext == null || map == null || Find.TickManager.TicksGame % Math.Max(1, ext.tickInterval) != 0)
            {
                return;
            }
            try
            {
                CrestDust(map, ext);
                if (!InGalePhase)
                {
                    return;
                }
                int interval = Math.Max(1, ext.tickInterval);
                List<Pawn> pawns = map.mapPawns.AllPawnsSpawned.ToList();
                for (int i = 0; i < pawns.Count; i++)
                {
                    Pawn p = pawns[i];
                    if (p == null || !p.Spawned || p.Map != map)
                    {
                        continue;
                    }
                    if (RM_DuneGaleSettings.abrasionEnabled)
                    {
                        Abrade(p, ext, interval);
                    }
                    if (RM_DuneGaleSettings.carryEnabled && p.Spawned)
                    {
                        TryCarry(p, map, ext, interval);
                    }
                    if (RM_DuneGaleSettings.staticEnabled && p.Spawned && p.RaceProps.IsMechanoid
                        && Rand.MTBEventOccurs(ext.staticMtbHours, GenDate.TicksPerHour, interval))
                    {
                        Stun(p.stances?.stunner, p, ext);
                    }
                }
                if (RM_DuneGaleSettings.abrasionEnabled)
                {
                    WearStructures(map, ext, interval);
                }
                if (RM_DuneGaleSettings.staticEnabled)
                {
                    StaticOnBuildings(map, ext, interval);
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[Stillsand] dune gale tick failed: " + e, 0x5D6A1E);
            }
        }

        public override void End()
        {
            try
            {
                Aftermath();
            }
            catch (Exception e)
            {
                Log.Error("[Stillsand] dune gale aftermath failed: " + e);
            }
            base.End();
        }

        // ------------------------------------------------------------ the wind

        private static readonly IntVec3[] Dirs8 =
        {
            new IntVec3(0, 0, 1), new IntVec3(1, 0, 1), new IntVec3(1, 0, 0), new IntVec3(1, 0, -1),
            new IntVec3(0, 0, -1), new IntVec3(-1, 0, -1), new IntVec3(-1, 0, 0), new IntVec3(-1, 0, 1),
        };

        private static readonly string[] DirNames8 =
        {
            "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest",
        };

        public static string BearingName(IntVec3 v)
        {
            return RM_GaleKernel.BearingName(v.x, v.z);
        }

        private static MethodInfo duneRegistryGet;
        private static PropertyInfo duneWindVector;
        private static bool duneLookupTried;

        /// <summary>The way the wind blows TOWARD, as one of the 8 unit steps.</summary>
        public IntVec3 Downwind(Map map)
        {
            IntVec3 v = DuneEngineDownwind(map);
            if (v.IsValid && v != IntVec3.Zero)
            {
                return v;
            }
            RM_MapComponent_PinnedSun sun = RM_MapComponent_PinnedSun.For(map);
            if (sun != null && sun.IsActive)
            {
                Vector2 d = sun.ShadowDirection;
                return Dirs8[RM_GaleKernel.WindIndexFromShadow(d.x, d.y)];
            }
            if (fallbackWindDir < 0)
            {
                fallbackWindDir = Rand.Range(0, 8);
            }
            return Dirs8[fallbackWindDir & 7];
        }

        private static IntVec3 DuneEngineDownwind(Map map)
        {
            if (!duneLookupTried)
            {
                duneLookupTried = true;
                Type reg = GenTypes.GetTypeInAnyAssembly("RimMandrake.MovingDunes.DuneFieldRegistry");
                Type field = GenTypes.GetTypeInAnyAssembly("RimMandrake.MovingDunes.MapComponent_DuneField");
                duneRegistryGet = reg?.GetMethod("Get", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(Map) }, null);
                duneWindVector = field?.GetProperty("WindVector", BindingFlags.Public | BindingFlags.Instance);
            }
            if (duneRegistryGet == null || duneWindVector == null)
            {
                return IntVec3.Invalid;
            }
            object comp = duneRegistryGet.Invoke(null, new object[] { map });
            return comp == null ? IntVec3.Invalid : (IntVec3)duneWindVector.GetValue(comp);
        }

        // ------------------------------------------------------------ the herald and the gale

        private static bool IsCrest(IntVec3 c, Map map, float crestDepth)
        {
            return map.sandGrid != null && map.sandGrid.GetDepth(c) >= crestDepth;
        }

        private void CrestDust(Map map, RM_DuneGaleExtension ext)
        {
            if (map.sandGrid == null)
            {
                return;
            }
            Color dust = new Color(0.82f, 0.68f, 0.45f, 0.75f);
            for (int i = 0; i < ext.crestDustPerInterval * 4; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (!IsCrest(c, map, ext.crestDepth) || c.Fogged(map))
                {
                    continue;
                }
                FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, Rand.Range(1.2f, 2.4f), dust);
            }
        }

        private void Abrade(Pawn p, RM_DuneGaleExtension ext, int interval)
        {
            if (p.Dead || p.Position.Roofed(p.Map)
                || !Rand.MTBEventOccurs(ext.abrasionMtbHours, GenDate.TicksPerHour, interval))
            {
                return;
            }
            p.TakeDamage(new DamageInfo(DamageDefOf.Scratch, ext.abrasionDamage.RandomInRange));
            abraded++;
        }

        private void WearStructures(Map map, RM_DuneGaleExtension ext, int interval)
        {
            // MTB per sampled cell, scaled up by the share of the map not sampled, so a map's
            // light structures wear at the stated MTB however big the map is.
            int samples = Math.Max(1, ext.structureSamplesPerInterval);
            float perCellShare = map.cellIndices.NumGridCells / (float)samples;
            List<IntVec3> stripped = null;
            for (int i = 0; i < samples; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                RoofDef roof = c.GetRoof(map);
                if (roof != null && !roof.isNatural && !roof.isThickRoof && RoofEdge(c, map)
                    && Rand.Chance(ext.roofStripChancePerSample))
                {
                    RoofCollapserImmediate.DropRoofInCells(c, map);
                    (stripped ??= new List<IntVec3>()).Add(c);
                    continue;
                }
                if (roof != null && roof.isThickRoof)
                {
                    continue;
                }
                Building b = c.GetEdifice(map);
                if (b == null || b.def.building == null || b.def.building.isNaturalRock || !b.def.useHitPoints
                    || b.MaxHitPoints > ext.lightBuildingMaxHitPoints)
                {
                    continue;
                }
                if (Rand.MTBEventOccurs(ext.structureMtbHours / perCellShare, GenDate.TicksPerHour, interval))
                {
                    b.TakeDamage(new DamageInfo(DamageDefOf.Scratch, ext.structureDamage.RandomInRange));
                }
            }
            if (stripped != null)
            {
                RoofCollapseCellsFinder.CheckCollapseFlyingRoofs(stripped, map, removalMode: true);
                Messages.Message("The gale tore a section of roof away.", new TargetInfo(stripped[0], map),
                    MessageTypeDefOf.NegativeEvent);
            }
        }

        /// <summary>A roof cell the wind can get under: one cardinal neighbour is open sky.</summary>
        private static bool RoofEdge(IntVec3 c, Map map)
        {
            for (int i = 0; i < 4; i++)
            {
                IntVec3 n = c + GenAdj.CardinalDirections[i];
                if (n.InBounds(map) && !n.Roofed(map))
                {
                    return true;
                }
            }
            return false;
        }

        private void Stun(StunHandler stunner, Thing thing, RM_DuneGaleExtension ext)
        {
            if (stunner == null)
            {
                return;
            }
            stunner.StunFor(ext.staticStunTicks.RandomInRange, null, addBattleLog: false);
            FleckMaker.ThrowMicroSparks(thing.DrawPos, thing.Map);
            stunned++;
        }

        private void StaticOnBuildings(Map map, RM_DuneGaleExtension ext, int interval)
        {
            List<Thing> built = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            for (int i = 0; i < built.Count; i++)
            {
                if (built[i] is Building_Turret turret && !turret.Position.Roofed(map)
                    && Rand.MTBEventOccurs(ext.staticMtbHours, GenDate.TicksPerHour, interval))
                {
                    Stun(turret.GetComp<CompStunnable>()?.StunHandler, turret, ext);
                }
            }
            // Sparks on metal: a few unroofed metal-stuffed buildings crackle each interval.
            if (built.Count == 0)
            {
                return;
            }
            for (int i = 0; i < ext.sparkSamplesPerInterval; i++)
            {
                Thing t = built.RandomElement();
                if (t.Stuff?.stuffProps?.categories != null && t.Stuff.stuffProps.categories.Contains(StuffCategoryDefOf.Metallic)
                    && !t.Position.Roofed(map) && !t.Position.Fogged(map))
                {
                    FleckMaker.ThrowMicroSparks(t.TrueCenter(), map);
                }
            }
        }

        // ------------------------------------------------------------ carry, never vanish

        private void TryCarry(Pawn p, Map map, RM_DuneGaleExtension ext, int interval)
        {
            if (!RM_GaleKernel.CarryEligible(p.BodySize, ext.carryMaxBodySize, p.Position.Roofed(map), IsCrest(p.Position, map, ext.crestDepth),
                    p.Dead))
            {
                return;
            }
            if (!Rand.MTBEventOccurs(ext.carryMtbHours, GenDate.TicksPerHour, interval))
            {
                return;
            }
            IntVec3 wind = Downwind(map);
            int steps = ext.carryCells.RandomInRange;
            // A blocked first step is no carry at all: fetched up against a wall or rock.
            RM_CarryResult walk = RM_GaleKernel.CarryWalk(p.Position.x, p.Position.z, wind.x, wind.z, steps,
                (x, z) => new IntVec3(x, 0, z).InBounds(map), (x, z) => new IntVec3(x, 0, z).Walkable(map),
                (x, z) =>
                {
                    if (ext.dragFilth != null)
                    {
                        FilthMaker.TryMakeFilth(new IntVec3(x, 0, z), map, ext.dragFilth, 1);
                    }
                });
            IntVec3 at = new IntVec3(walk.x, 0, walk.z);
            if (walk.offMap)
            {
                carried++;
                RM_GameComponent_GaleCarried.Get()?.CarryOff(p, map, wind, ext);
                return;
            }
            if (walk.moved == 0)
            {
                return;
            }
            carried++;
            if (ext.dragFilth != null)
            {
                FilthMaker.TryMakeFilth(at, map, ext.dragFilth, 1);
            }
            p.Position = at;
            p.Notify_Teleported();
            Bruise(p, ext.carryBruise.RandomInRange);
            if (p.Faction == Faction.OfPlayer)
            {
                Messages.Message(p.LabelShortCap + " was dragged " + BearingName(wind) + " by the gale.",
                    p, MessageTypeDefOf.NegativeEvent);
            }
        }

        public static void Bruise(Pawn p, int total)
        {
            while (total > 0 && !p.Dead)
            {
                int hit = Math.Min(total, Rand.RangeInclusive(1, 3));
                p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, hit));
                total -= hit;
            }
        }

        // ------------------------------------------------------------ aftermath

        private void Aftermath()
        {
            RM_DuneGaleExtension ext = Ext;
            Map map = SingleMap;
            if (ext == null || map == null)
            {
                return;
            }
            IntVec3 face = IntVec3.Invalid;
            if (map.sandGrid != null)
            {
                float massAfter = map.sandGrid.TotalDepth;
                face = ErosionFace(map, ext, out List<IntVec3> wiped);
                Log.Message("[Stillsand] dune gale ended on " + map + ": dune field mass "
                            + (massBefore < 0f ? "UNMEASURED" : massBefore.ToString("F1")) + " -> " + massAfter.ToString("F1")
                            + (massBefore < 0f ? "" : " (delta " + (massAfter - massBefore).ToString("+0.0;-0.0") + ")")
                            + "; cells moved past " + ext.wipeDepthDelta.ToString("0.00") + ": " + wiped.Count
                            + "; carried " + carried + ", abraded " + abraded + ", stunned " + stunned);
                WipeTracks(map, wiped);
            }
            if (!face.IsValid && !RCellFinder.TryFindRandomCellNearTheCenterOfTheMapWith(c => c.Standable(map) && !c.Fogged(map), map, out face))
            {
                face = map.Center;
            }
            if (RM_DuneGaleSettings.emergenceEnabled)
            {
                Emerge(map, ext, face);
            }
            Seed(map, ext, face);
            RM_GameComponent_GaleCarried.Get()?.ReturnAllFor(map, ext, startTick);
        }

        /// <summary>The freshest erosion face: the open, standable cell that lost the most sand.
        /// Also returns every cell whose depth moved past the wipe threshold.</summary>
        private IntVec3 ErosionFace(Map map, RM_DuneGaleExtension ext, out List<IntVec3> wiped)
        {
            wiped = new List<IntVec3>();
            if (sandBefore == null || sandBefore.Length != map.cellIndices.NumGridCells)
            {
                return IntVec3.Invalid;
            }
            IntVec3 best = IntVec3.Invalid;
            float bestLoss = 0.05f;
            for (int i = 0; i < sandBefore.Length; i++)
            {
                IntVec3 c = map.cellIndices.IndexToCell(i);
                float before = sandBefore[i] / 255f;
                float now = map.sandGrid.GetDepth(c);
                float d = now - before;
                if (Mathf.Abs(d) >= ext.wipeDepthDelta)
                {
                    wiped.Add(c);
                }
                if (-d > bestLoss && c.Standable(map) && !c.Roofed(map) && c.GetEdifice(map) == null)
                {
                    bestLoss = -d;
                    best = c;
                }
            }
            return best;
        }

        private static void WipeTracks(Map map, List<IntVec3> cells)
        {
            List<Thing> doomed = new List<Thing>();
            for (int i = 0; i < cells.Count; i++)
            {
                List<Thing> things = cells[i].GetThingList(map);
                for (int j = 0; j < things.Count; j++)
                {
                    if (things[j] is Filth)
                    {
                        doomed.Add(things[j]);
                    }
                }
            }
            for (int i = 0; i < doomed.Count; i++)
            {
                if (!doomed[i].Destroyed)
                {
                    doomed[i].Destroy();
                }
            }
            try
            {
                TracksWiped?.Invoke(map, cells);
            }
            catch (Exception e)
            {
                Log.Error("[Stillsand] a TracksWiped subscriber threw: " + e);
            }
        }

        private void Emerge(Map map, RM_DuneGaleExtension ext, IntVec3 face)
        {
            List<RM_GaleEmergence> options = ext.emergences
                .Where(o => RM_GaleKernel.EmergenceOk(o.weight, RM_DuneGaleSettings.EmergenceAllowed(o.key),
                    o.skeleton, o.skeleton && RM_SkeletonPlacer.PlaceableSkeletons.Any(),
                    o.caveMouth, o.caveMouth && FindRockFace(map, face, 40f, out _, out _)))
                .ToList();
            if (options.Count == 0)
            {
                Log.Warning("[Stillsand] dune gale: no emergence row is available on " + map + " (all off or unplaceable).");
                return;
            }
            RM_GaleEmergence pick = options.RandomElementByWeight(o => o.weight);
            List<Thing> placed = new List<Thing>();
            IntVec3 focus = face;

            if (pick.caveMouth && FindRockFace(map, face, 40f, out IntVec3 mouth, out IntVec3 inward))
            {
                CarveMouth(map, mouth, inward);
                focus = mouth;
            }
            if (pick.skeleton)
            {
                ThingDef sk = RM_SkeletonPlacer.PlaceableSkeletons.RandomElement();
                if (RM_SkeletonPlacer.TryFindSpot(sk, face, map, 20, 3, out IntVec3 spot))
                {
                    Thing t = RM_SkeletonPlacer.Place(sk, spot, map);
                    if (t != null)
                    {
                        placed.Add(t);
                        focus = spot;
                    }
                }
            }
            if (pick.corpses != null)
            {
                foreach (PawnKindDefCount pk in pick.corpses)
                {
                    for (int i = 0; i < pk.count; i++)
                    {
                        if (!CellFinder.TryFindRandomCellNear(face, map, pick.scatterRadius,
                                c => c.Standable(map) && c.GetFirstItem(map) == null, out IntVec3 cell))
                        {
                            cell = face;
                        }
                        Corpse corpse = RoomGenUtility.SpawnCorpse(cell, pk.kindDef, GenDate.TicksPerYear * Rand.Range(5, 60),
                            map, DamageDefOf.Blunt, bloodFilthRange: new IntRange(0, 0));
                        corpse?.GetComp<CompRottable>()?.RotImmediately(RotStage.Dessicated);
                        if (corpse != null)
                        {
                            placed.Add(corpse);
                        }
                    }
                }
            }
            if (pick.things != null)
            {
                foreach (ThingDefCountClass tc in pick.things)
                {
                    if (tc?.thingDef == null)
                    {
                        continue;
                    }
                    Thing t = ThingMaker.MakeThing(tc.thingDef, tc.thingDef.MadeFromStuff ? GenStuff.DefaultStuffFor(tc.thingDef) : null);
                    t.stackCount = Math.Max(1, Math.Min(tc.count, tc.thingDef.stackLimit));
                    if (GenPlace.TryPlaceThing(t, face, map, ThingPlaceMode.Near, null, null, null, Math.Max(1, pick.scatterRadius)))
                    {
                        t.SetForbidden(true, warnOnFail: false);
                        placed.Add(t);
                    }
                }
            }
            Find.LetterStack.ReceiveLetter(pick.letterLabel ?? "What the wind uncovered", pick.letterText ?? "",
                LetterDefOf.NeutralEvent, placed.Count > 0 ? new LookTargets(placed) : new LookTargets(new TargetInfo(focus, map)));
        }

        /// <summary>Nearest natural-rock cell with open, standable ground beside it.</summary>
        private static bool FindRockFace(Map map, IntVec3 near, float radius, out IntVec3 mouth, out IntVec3 inward)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, radius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                Building rock = c.GetEdifice(map);
                if (rock?.def.building == null || !rock.def.building.isNaturalRock)
                {
                    continue;
                }
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 open = c - GenAdj.CardinalDirections[i];
                    if (open.InBounds(map) && open.Standable(map) && !open.Fogged(map))
                    {
                        mouth = c;
                        inward = GenAdj.CardinalDirections[i];
                        return true;
                    }
                }
            }
            mouth = IntVec3.Invalid;
            inward = IntVec3.Invalid;
            return false;
        }

        /// <summary>A two-wide passage four to seven cells into the rock, roofed as a cave.</summary>
        private static void CarveMouth(Map map, IntVec3 mouth, IntVec3 inward)
        {
            IntVec3 side = new IntVec3(inward.z, 0, -inward.x);
            int depth = Rand.RangeInclusive(4, 7);
            for (int d = 0; d < depth; d++)
            {
                for (int w = 0; w < 2; w++)
                {
                    IntVec3 c = mouth + inward * d + side * w;
                    if (!c.InBounds(map))
                    {
                        continue;
                    }
                    Building rock = c.GetEdifice(map);
                    if (rock?.def.building != null && rock.def.building.isNaturalRock)
                    {
                        rock.Destroy(DestroyMode.Vanish);
                        if (d > 0 && !c.Roofed(map))
                        {
                            map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThin);
                        }
                    }
                }
            }
            FloodFillerFog.FloodUnfog(mouth, map);
        }

        private void Seed(Map map, RM_DuneGaleExtension ext, IntVec3 face)
        {
            if (!RM_DuneGaleSettings.seedingEnabled)
            {
                return;
            }
            // Dormant siidda nearby wake.
            if (!ext.wakeRaces.NullOrEmpty())
            {
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
                {
                    if (ext.wakeRaces.Contains(p.def) && p.Position.InHorDistOf(face, ext.wakeRadius))
                    {
                        CompCanBeDormant dormant = p.GetComp<CompCanBeDormant>();
                        if (dormant != null && !dormant.Awake)
                        {
                            dormant.WakeUp();
                        }
                    }
                }
            }
            // A glasscrust sheet on the fresh face.
            SowAround(map, ext.glasscrustPlant, face, ext.glasscrustCells.RandomInRange, 7);
            // An hourbloom where the sand meets water.
            if (ext.bloomPlant != null)
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(face, ext.waterSearchRadius, true))
                {
                    if (c.InBounds(map) && c.GetTerrain(map).IsWater)
                    {
                        SowAround(map, ext.bloomPlant, c, ext.bloomCells.RandomInRange, 5);
                        break;
                    }
                }
            }
        }

        private static void SowAround(Map map, ThingDef plant, IntVec3 center, int count, int radius)
        {
            if (plant == null || count <= 0)
            {
                return;
            }
            int sown = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true).InRandomOrder())
            {
                if (sown >= count)
                {
                    break;
                }
                if (c.InBounds(map) && c.GetPlant(map) == null && plant.CanEverPlantAt(c, map))
                {
                    Plant p = (Plant)GenSpawn.Spawn(plant, c, map);
                    p.Growth = Rand.Range(0.15f, 0.6f);
                    sown++;
                }
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // Carried off the edge: a letter naming them and the bearing, and they come back.
    // Held as world pawns pinned with ForcefullyKeptPawns so the world GC never discards
    // them; returned at the next gale's end or after returnDays, whichever is first.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GaleCarriedRecord : IExposable
    {
        public Pawn pawn;
        public Map map;
        public IntVec3 wind;
        public int returnTick;
        public bool wasPlayer;
        // Tick it was taken (-1 on records saved before this field): a gale only gives back
        // what an EARLIER gale took. Its own survival odds travel with it (-1 = use the book's).
        public int takenTick = -1;
        public float aliveChance = -1f;

        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "pawn", saveDestroyedThings: true);
            Scribe_References.Look(ref map, "map");
            Scribe_Values.Look(ref wind, "wind");
            Scribe_Values.Look(ref returnTick, "returnTick");
            Scribe_Values.Look(ref wasPlayer, "wasPlayer");
            Scribe_Values.Look(ref takenTick, "takenTick", -1);
            Scribe_Values.Look(ref aliveChance, "aliveChance", -1f);
        }
    }

    public class RM_GameComponent_GaleCarried : GameComponent
    {
        private List<RM_GaleCarriedRecord> carried = new List<RM_GaleCarriedRecord>();
        private float aliveChance = 0.75f;

        public RM_GameComponent_GaleCarried(Game game)
        {
        }

        public static RM_GameComponent_GaleCarried Get()
        {
            return Current.Game?.GetComponent<RM_GameComponent_GaleCarried>();
        }

        public int Count => carried.Count + (Find.World?.GetComponent<RimMandrake.FlowWorks.TakenByLand.RM_WorldComponent_TakenByLand>()?.PendingOfKind("gale") ?? 0);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref carried, "carried", LookMode.Deep);
            Scribe_Values.Look(ref aliveChance, "aliveChance", 0.75f);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                carried = carried ?? new List<RM_GaleCarriedRecord>();
                carried.RemoveAll(r => r == null);
            }
        }

        /// <summary>TAKEN_BY_LAND_SERVICE_1: the carry-off is now a take through the shared FlowWorks service (policy
        /// RM_GaleTakenPolicy): hold, letters, ground trace and return all live there. This book only drains records saved before it.</summary>
        public void CarryOff(Pawn p, Map map, IntVec3 wind, RM_DuneGaleExtension ext)
        {
            aliveChance = ext.returnAliveChance;
            RimMandrake.FlowWorks.TakenByLand.RM_TakenByLand.Take(p, "gale", wind, ext.returnDays.RandomInRange, ext.returnAliveChance);
        }

        private static Rot4 ToRot4(RM_Edge e)
        {
            switch (e)
            {
                case RM_Edge.East: return Rot4.East;
                case RM_Edge.South: return Rot4.South;
                case RM_Edge.West: return Rot4.West;
                default: return Rot4.North;
            }
        }

        public override void GameComponentTick()
        {
            if (!RM_GaleKernel.ShouldScanCarried(carried.Count, Find.TickManager.TicksGame))
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            foreach (RM_GaleCarriedRecord r in RM_GaleKernel.TakeWhere(carried, c => RM_GaleKernel.IsDue(c.returnTick, now)))
            {
                SafeReturn(r, r.aliveChance >= 0f ? r.aliveChance : aliveChance);
            }
        }

        /// <summary>Storm's end gives back what EARLIER gales took from this map; pawns this gale
        /// took (taken at or after <paramref name="galeStartTick"/>) wait for the next one or returnDays.</summary>
        public void ReturnAllFor(Map map, RM_DuneGaleExtension ext, int galeStartTick)
        {
            Find.World?.GetComponent<RimMandrake.FlowWorks.TakenByLand.RM_WorldComponent_TakenByLand>()?.ReturnEarlierOnMap("gale", map, galeStartTick);
            foreach (RM_GaleCarriedRecord r in RM_GaleKernel.TakeWhere(carried, c => c.map == map && c.takenTick < galeStartTick))
            {
                SafeReturn(r, r.aliveChance >= 0f ? r.aliveChance : ext.returnAliveChance);
            }
        }

        // One failed return must not lose the rest of the batch already taken off the book.
        private static void SafeReturn(RM_GaleCarriedRecord r, float aliveChance)
        {
            try
            {
                Return(r, aliveChance);
            }
            catch (Exception e)
            {
                Log.Error("[Stillsand] gale return of " + r?.pawn + " failed: " + e);
            }
        }

        private static void Return(RM_GaleCarriedRecord r, float aliveChance)
        {
            Pawn p = r.pawn;
            Map map = r.map ?? RimMandrake.EnvironmentalHazards.RM_SurfaceHome.AnyPlayerSurfaceHomeMap;
            if (p != null && Find.WorldPawns.Contains(p))
            {
                Find.WorldPawns.RemovePawn(p);
            }
            if (RM_GaleKernel.Decide(p == null || p.Destroyed || p.Discarded, map == null, false, false) == RM_ReturnOutcome.LostMissing)
            {
                Find.LetterStack.ReceiveLetter("Lost to the sand",
                    "Something the gale carried off was never given back: " + (p?.LabelShortCap ?? "a body")
                    + (map == null ? ". The map it was taken from is gone." : ". Nothing came in on the wind."),
                    LetterDefOf.NeutralEvent);
                return;
            }
            IntVec3 wind = r.wind == IntVec3.Zero ? IntVec3.South : r.wind;
            Rot4 edge = ToRot4(RM_GaleKernel.ReturnEdge(wind.x, wind.z));
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.Fogged(map), map, edge, 0f, out IntVec3 cell)
                && !CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map), map, 0f, out cell))
            {
                cell = map.Center;
            }
            // Comes in a few cells from the edge, "somewhere downwind".
            int inX = cell.x, inZ = cell.z;
            RM_GaleKernel.WalkIn(ref inX, ref inZ, wind.x, wind.z, (x, z) => new IntVec3(x, 0, z).InBounds(map),
                (x, z) => new IntVec3(x, 0, z).Standable(map));
            cell = new IntVec3(inX, 0, inZ);
            bool alive = !p.Dead && Rand.Chance(aliveChance);
            RM_ReturnOutcome outcome = RM_GaleKernel.Decide(false, false, p.Dead, alive);
            if (outcome == RM_ReturnOutcome.LostDead)
            {
                Find.LetterStack.ReceiveLetter("Lost to the sand",
                    p.LabelShortCap + " died out past the edge. The wind kept the body.", LetterDefOf.NeutralEvent);
                return;
            }
            GenSpawn.Spawn(p, cell, map, WipeMode.VanishOrMoveAside);
            RM_GameCondition_DuneGale.Bruise(p, Rand.RangeInclusive(2, 6));
            if (outcome == RM_ReturnOutcome.SpawnThenKill && !p.Dead)
            {
                p.Kill(null);
            }
            Thing target = p.Dead ? (Thing)p.Corpse ?? p : p;
            Find.LetterStack.ReceiveLetter(p.Dead ? "Given back: the body of " + p.LabelShortCap : "Given back: " + p.LabelShortCap,
                p.Dead
                    ? "The wind has brought back what it took. " + p.LabelShortCap + "'s body lies where the drift dropped it, in from the "
                      + RM_GameCondition_DuneGale.BearingName(wind) + "."
                    : p.LabelShortCap + " has walked back in from the " + RM_GameCondition_DuneGale.BearingName(wind)
                      + ", scoured raw and half-buried, but alive.",
                r.wasPlayer ? (p.Dead ? LetterDefOf.Death : LetterDefOf.PositiveEvent) : LetterDefOf.NeutralEvent,
                target);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // §12 Mod Settings: a toggle each for the gale, abrasion, carry, static, emergence
    // (plus per-row toggles) and dust devils; frequency sliders. Defaults are shipped
    // behaviour. All off: the biome keeps Odyssey's own sandstorm and nothing else.
    // ════════════════════════════════════════════════════════════════════
    public class RM_DuneGaleSettings : ModSettings
    {
        public static bool galeEnabled = true;
        public static float galeFrequency = 1f;
        public static bool abrasionEnabled = true;
        public static bool carryEnabled = true;
        public static bool staticEnabled = true;
        public static bool emergenceEnabled = true;
        public static bool seedingEnabled = true;
        public static bool dustDevilsEnabled = true;
        public static float dustDevilFrequency = 1f;
        private static Dictionary<string, bool> emergenceOff = new Dictionary<string, bool>();

        public static bool EmergenceAllowed(string key)
        {
            return key.NullOrEmpty() || !(emergenceOff.TryGetValue(key, out bool off) && off);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref galeEnabled, "galeEnabled", true);
            Scribe_Values.Look(ref galeFrequency, "galeFrequency", 1f);
            Scribe_Values.Look(ref abrasionEnabled, "abrasionEnabled", true);
            Scribe_Values.Look(ref carryEnabled, "carryEnabled", true);
            Scribe_Values.Look(ref staticEnabled, "staticEnabled", true);
            Scribe_Values.Look(ref emergenceEnabled, "emergenceEnabled", true);
            Scribe_Values.Look(ref seedingEnabled, "seedingEnabled", true);
            Scribe_Values.Look(ref dustDevilsEnabled, "dustDevilsEnabled", true);
            Scribe_Values.Look(ref dustDevilFrequency, "dustDevilFrequency", 1f);
            Scribe_Collections.Look(ref emergenceOff, "emergenceOff", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                emergenceOff = emergenceOff ?? new Dictionary<string, bool>();
            }
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Dune gale", ref galeEnabled,
                "The Stillsand's own storm: a herald, one to two days of gale, then one thing the wind uncovers. "
                + "Off: it never fires; Odyssey's sandstorm is unaffected.");
            list.Label("Gale frequency: x" + galeFrequency.ToString("0.00"));
            galeFrequency = Mathf.Round(list.Slider(galeFrequency, 0f, 3f) * 20f) / 20f;
            list.CheckboxLabeled("Abrasion", ref abrasionEnabled,
                "Exposed pawns take slow scratches; light walls and thin roof edges wear.");
            list.CheckboxLabeled("Carry", ref carryEnabled,
                "Light pawns and animals in the open on a crest can be dragged downwind. One carried off the "
                + "edge gets a letter and always comes back, alive or not.");
            list.CheckboxLabeled("Gale static", ref staticEnabled,
                "Charged dust: brief stuns on turrets and mechanoids, sparks on metal.");
            list.CheckboxLabeled("Emergence", ref emergenceEnabled,
                "At gale end the wind uncovers one thing near a fresh erosion face, with a letter.");
            if (emergenceEnabled)
            {
                IEnumerable<RM_GaleEmergence> rows = DefDatabase<GameConditionDef>.AllDefsListForReading
                    .Select(d => d.GetModExtension<RM_DuneGaleExtension>())
                    .Where(e => e != null)
                    .SelectMany(e => e.emergences)
                    .Where(r => !r.key.NullOrEmpty());
                foreach (RM_GaleEmergence r in rows)
                {
                    bool on = EmergenceAllowed(r.key);
                    list.CheckboxLabeled("    " + (r.letterLabel ?? r.key), ref on);
                    emergenceOff[r.key] = !on;
                }
            }
            list.CheckboxLabeled("Seeding", ref seedingEnabled,
                "Gale end wakes dormant dust husks nearby, lays glasscrust, and blooms hourbloom at any water.");
            list.GapLine();
            list.CheckboxLabeled("Dust devils", ref dustDevilsEnabled,
                "A fair-weather column that wanders the flat, lifts light items and spooks animals. Never damages.");
            list.Label("Dust devil frequency: x" + dustDevilFrequency.ToString("0.00"));
            dustDevilFrequency = Mathf.Round(list.Slider(dustDevilFrequency, 0f, 3f) * 20f) / 20f;
            list.End();
        }
    }

    public class RM_DuneGaleMod : Mod
    {
        public static RM_DuneGaleSettings settings;

        public RM_DuneGaleMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_DuneGaleSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand: dune gale";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
