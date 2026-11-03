using System.Collections.Generic;
using System.Linq;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using RimWorld.Planet;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_RETURN_RITUAL_1 spec 5 — "the sand remembers water" (RM tier,
    // no theology). Design: stillsand_turn3_development_2026-09-30.md §2.3.
    //
    //   * Water poured onto remembering sand BLOOMS: the biome's bloom plant
    //     (RM_Hourbloom on the Stillsand) is sown along the pour. The plant's
    //     own short life (growDays 0.5 x lifespan 8) is the "dust again in
    //     days"; nothing here keeps it alive.
    //   * Wet sand DRAWS SWIMMERS for a while: a fresh pour is what the sand
    //     leviathans swim toward when no powered drill is louder
    //     (RM_SandLeviathanUtility.LoudestCell reads LatestPourCell).
    //   * A pawn pours by right-clicking a water item lying on such sand
    //     (any item carrying RM_CompProperties_WaterVolume).
    //
    // Biome-kit gate: RM_SandRemembersWaterExtension on the BiomeDef (Stillsand
    // carries it via Patches/RM_SandRemembersWater_Stillsand.xml), so any other
    // biome can opt in with no code. No debt meter lives in this file: the
    // ledger (RM_WaterLedger.cs) is inert until a tier above ships a
    // RM_WaterLedgerDef, and every call below into it is a no-op without one.
    // ════════════════════════════════════════════════════════════════════

    /// <summary>On a BiomeDef: its sand remembers water.</summary>
    public class RM_SandRemembersWaterExtension : DefModExtension
    {
        /// <summary>TerrainDef defNames that count as remembering sand (strings, so an absent mod's terrain is not a cross-ref error).</summary>
        public List<string> sandTerrains = new List<string>();

        /// <summary>The plant the pour sows. Null: the sand gets wet but nothing blooms.</summary>
        public ThingDef bloomPlant;

        /// <summary>Litres of water that wake one cell of bloom.</summary>
        public float litresPerBloomCell = 1.5f;

        public int maxBloomCellsPerPour = 80;

        /// <summary>How long a poured cell stays wet (until a gale clears it sooner).</summary>
        public float wetHours = 48f;

        /// <summary>How long a fresh pour draws the swimmers.</summary>
        public float swimmerDrawHours = 12f;

        /// <summary>WeatherDef defNames that count as a gale: one wipes every wet cell, and its end is an opening for a ledger.</summary>
        public List<string> galeWeathers = new List<string>();

        public bool IsGale(WeatherDef w)
        {
            return w != null && galeWeathers != null && galeWeathers.Contains(w.defName);
        }

        public bool IsSand(TerrainDef t)
        {
            return t != null && sandTerrains != null && sandTerrains.Contains(t.defName);
        }
    }

    /// <summary>On a ThingDef: this item holds this many litres of water per unit.</summary>
    public class RM_CompProperties_WaterVolume : CompProperties
    {
        public float litres = 1f;

        /// <summary>What drawing it is called in a ledger letter ("canteen egg", "still flask").</summary>
        public string drawnAs;

        /// <summary>WATER_LEDGER_DOUBLE_CHARGE_1: true when the land was already charged as this item was MADE (the
        /// solar still books its litres in Consume), so drinking it books nothing more. The comp stays on the item
        /// so the Return still counts it as water.
        /// PROVISIONAL (auto-decided 2026-10-09, WATER_LEDGER_DOUBLE_CHARGE_1): the one charge is at production.</summary>
        public bool bookedAtSource;

        public RM_CompProperties_WaterVolume()
        {
            compClass = typeof(RM_CompWaterVolume);
        }
    }

    public class RM_CompWaterVolume : ThingComp
    {
        public RM_CompProperties_WaterVolume Props => (RM_CompProperties_WaterVolume)props;

        // Drinking it draws water from the land. ThingComp.PostIngested carries no
        // count, so one ingestion is booked as one unit's litres.
        public override void PostIngested(Pawn ingester)
        {
            base.PostIngested(ingester);
            Map map = ingester?.MapHeld;
            if (map != null && !Props.bookedAtSource)
            {
                RM_WaterLedger.Notify_Drawn(map, Props.litres, Props.drawnAs ?? parent.def.label);
            }
        }
    }

    /// <summary>On a pawn's ThingDef: its death on a ledger map opens the Return (the krayt kill).</summary>
    public class RM_CompProperties_OpensWaterReturn : CompProperties
    {
        public string reason;

        public RM_CompProperties_OpensWaterReturn()
        {
            compClass = typeof(RM_CompOpensWaterReturn);
        }
    }

    public class RM_CompOpensWaterReturn : ThingComp
    {
        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            if (prevMap != null)
            {
                RM_WaterLedger.Notify_Opening(prevMap,
                    ((RM_CompProperties_OpensWaterReturn)props).reason ?? (parent.LabelShort + " killed"));
            }
        }
    }

    public static class RM_StillsandWater
    {
        public static RM_SandRemembersWaterExtension Ext(Map map)
        {
            return map?.Biome?.GetModExtension<RM_SandRemembersWaterExtension>();
        }

        public static bool Remembers(Map map, IntVec3 c)
        {
            RM_SandRemembersWaterExtension ext = Ext(map);
            return ext != null && c.InBounds(map) && ext.IsSand(c.GetTerrain(map));
        }

        /// <summary>Unit vector toward the star: against the pinned sun's shadow, else a random bearing.</summary>
        public static Vector2 TowardSun(Map map)
        {
            RM_MapComponent_PinnedSun pin = RM_MapComponent_PinnedSun.For(map);
            if (pin != null && pin.Extension != null)
            {
                Vector2 s = pin.ShadowDirection;
                if (s.sqrMagnitude > 0.0001f)
                {
                    return -s.normalized;
                }
            }
            float a = Rand.Range(0f, 360f) * Mathf.Deg2Rad;
            return new Vector2(Mathf.Sin(a), Mathf.Cos(a));
        }

        /// <summary>A line of cells from origin along dir (x, z), origin excluded.</summary>
        public static List<IntVec3> LineCells(Map map, IntVec3 origin, Vector2 dir, int length)
        {
            var cells = new List<IntVec3>();
            if (dir.sqrMagnitude < 0.0001f)
            {
                return cells;
            }
            dir = dir.normalized;
            for (int i = 1; i <= length; i++)
            {
                IntVec3 c = new IntVec3(Mathf.RoundToInt(origin.x + dir.x * i), 0, Mathf.RoundToInt(origin.z + dir.y * i));
                if (!c.InBounds(map))
                {
                    break;
                }
                if (!cells.Contains(c))
                {
                    cells.Add(c);
                }
            }
            return cells;
        }

        /// <summary>
        /// Pour litres of water onto cells (the spine first, then a one-cell
        /// halo). Every remembering-sand cell reached gets wet; with bloom-on-pour
        /// on, the biome's bloom plant is sown on as many as the water wakes.
        /// Returns how many cells bloomed.
        /// </summary>
        public static int Pour(Map map, List<IntVec3> spine, float litres)
        {
            RM_SandRemembersWaterExtension ext = Ext(map);
            if (ext == null || spine == null || spine.Count == 0 || litres <= 0f)
            {
                return 0;
            }
            var cells = new List<IntVec3>();
            foreach (IntVec3 c in spine)
            {
                if (!cells.Contains(c))
                {
                    cells.Add(c);
                }
            }
            foreach (IntVec3 c in spine)
            {
                foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)))
                {
                    if (!cells.Contains(n))
                    {
                        cells.Add(n);
                    }
                }
            }

            RM_MapComponent_WetSand wet = RM_MapComponent_WetSand.For(map);
            int wetTicks = Mathf.Max(2500, Mathf.RoundToInt(ext.wetHours * 2500f));
            int budget = Mathf.Min(ext.maxBloomCellsPerPour, Mathf.FloorToInt(litres / Mathf.Max(0.1f, ext.litresPerBloomCell)));
            int bloomed = 0;
            foreach (IntVec3 c in cells)
            {
                if (!c.InBounds(map) || !ext.IsSand(c.GetTerrain(map)) || c.Roofed(map))
                {
                    continue;
                }
                wet?.MarkWet(c, wetTicks);
                if (bloomed >= budget || !RM_StillsandWaterSettings.bloomOnPour || ext.bloomPlant == null)
                {
                    continue;
                }
                if (c.GetEdifice(map) != null || c.GetPlant(map) != null || c.GetFirstItem(map) != null || c.GetFirstPawn(map) != null)
                {
                    continue;
                }
                Plant p = (Plant)GenSpawn.Spawn(ext.bloomPlant, c, map);
                p.Growth = Rand.Range(0.05f, 0.15f);
                bloomed++;
            }
            if (wet != null && spine.Count > 0)
            {
                wet.NotePour(spine[0], Mathf.RoundToInt(ext.swimmerDrawHours * 2500f));
            }
            return bloomed;
        }

        /// <summary>The incident-weighting hook every Stillsand event worker multiplies its chance by.</summary>
        public static float IncidentChanceFactor(Map map, IncidentDef def)
        {
            return RM_WaterLedger.IncidentFactor(map, def);
        }
    }

    /// <summary>Wet sand on one map: which cells are wet, and the latest pour (the swimmers' draw).</summary>
    public class RM_MapComponent_WetSand : MapComponent
    {
        private Dictionary<IntVec3, int> wetUntil = new Dictionary<IntVec3, int>();
        private IntVec3 lastPourCell = IntVec3.Invalid;
        private int drawUntilTick = -1;
        private bool galeBlowing;

        public RM_MapComponent_WetSand(Map map) : base(map)
        {
        }

        public static RM_MapComponent_WetSand For(Map map)
        {
            return map?.GetComponent<RM_MapComponent_WetSand>();
        }

        public int WetCellCount => wetUntil.Count;

        public bool IsWet(IntVec3 c)
        {
            return wetUntil.TryGetValue(c, out int until) && until > Find.TickManager.TicksGame;
        }

        public IEnumerable<IntVec3> WetCells => wetUntil.Keys;

        public void MarkWet(IntVec3 c, int ticks)
        {
            int until = Find.TickManager.TicksGame + ticks;
            if (!wetUntil.TryGetValue(c, out int old) || old < until)
            {
                wetUntil[c] = until;
            }
        }

        public void NotePour(IntVec3 c, int drawTicks)
        {
            lastPourCell = c;
            drawUntilTick = Find.TickManager.TicksGame + drawTicks;
        }

        /// <summary>The fresh pour the swimmers come to, or Invalid.</summary>
        public IntVec3 LatestPourCell => drawUntilTick > Find.TickManager.TicksGame ? lastPourCell : IntVec3.Invalid;

        /// <summary>A gale wipes the sand: every wet cell (and its Return line) is gone.</summary>
        public void ClearAll()
        {
            wetUntil.Clear();
            // ...and the pour it drew swimmers to is wiped with it.
            lastPourCell = IntVec3.Invalid;
            drawUntilTick = -1;
        }

        // ── The Return line (STILLSAND_RETURN_REMAINDER_1 spec 2): every wet cell is drawn as a darker damp stain
        //    on the sand, under plants, filth and items, fading over its last hours. A gale clears the cells
        //    (ClearAll), so the stain goes with them. Procedural texture: no art file to ship or miss.
        private const int FadeTicks = 12 * 2500;
        private const int Shades = 4;
        private static Material[] stainMats;

        /// <summary>Wet cells drawn on the last frame this map was on screen (the proof's read of the renderer).</summary>
        public int DrawnLastFrame { get; private set; }

        /// <summary>Unscaled game ticks of the last frame that drew (so a proof can tell "drew nothing" from "never ran").</summary>
        public int LastDrawTick { get; private set; } = -1;

        /// <summary>0..Shades-1: how dark a cell's stain is with this many ticks of wetness left.</summary>
        public static int ShadeFor(int ticksLeft)
        {
            if (ticksLeft <= 0)
            {
                return -1;
            }
            return Mathf.Clamp(Mathf.CeilToInt((float)ticksLeft / FadeTicks * Shades) - 1, 0, Shades - 1);
        }

        private static Material StainMat(int shade)
        {
            if (stainMats == null)
            {
                const int N = 32;
                var tex = new Texture2D(N, N, TextureFormat.ARGB32, false)
                {
                    name = "RM_WetSandStain",
                    wrapMode = TextureWrapMode.Clamp,
                    filterMode = FilterMode.Bilinear
                };
                for (int y = 0; y < N; y++)
                {
                    for (int x = 0; x < N; x++)
                    {
                        float dx = (x + 0.5f) / N * 2f - 1f;
                        float dy = (y + 0.5f) / N * 2f - 1f;
                        float d = Mathf.Sqrt(dx * dx + dy * dy);
                        tex.SetPixel(x, y, new Color(1f, 1f, 1f, Mathf.Clamp01((1f - d) / 0.5f)));
                    }
                }
                tex.Apply(false, true);
                stainMats = new Material[Shades];
                for (int i = 0; i < Shades; i++)
                {
                    stainMats[i] = MaterialPool.MatFrom(tex, ShaderDatabase.Transparent,
                        new Color(0.28f, 0.2f, 0.12f, 0.55f * (i + 1) / Shades));
                }
            }
            return stainMats[shade];
        }

        public override void MapComponentUpdate()
        {
            if (wetUntil.Count == 0 || !RM_StillsandWaterSettings.drawReturnLine || Find.CurrentMap != map
                || WorldRendererUtility.WorldSelected)
            {
                if (Find.CurrentMap == map)
                {
                    DrawnLastFrame = 0;
                }
                return;
            }
            CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(1);
            int now = Find.TickManager.TicksGame;
            float y = AltitudeLayer.TerrainScatter.AltitudeFor();
            int drawn = 0;
            foreach (KeyValuePair<IntVec3, int> kv in wetUntil)
            {
                IntVec3 c = kv.Key;
                int shade = ShadeFor(kv.Value - now);
                if (shade < 0 || !view.Contains(c))
                {
                    continue;
                }
                // A per-cell jitter so a line of stains reads as soaked sand, not a grid of discs.
                int h = c.GetHashCode();
                Vector3 pos = new Vector3(c.x + 0.5f + ((h & 7) - 3.5f) * 0.03f, y, c.z + 0.5f + (((h >> 3) & 7) - 3.5f) * 0.03f);
                float size = 1.45f + ((h >> 6) & 3) * 0.08f;
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, new Vector3(size, 1f, size)),
                    StainMat(shade), 0);
                drawn++;
            }
            DrawnLastFrame = drawn;
            LastDrawTick = now;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            RM_SandRemembersWaterExtension ext = RM_StillsandWater.Ext(map);
            if (ext == null)
            {
                return;
            }
            // The gale: while one blows, the sand forgets; when it ends, a ledger may open.
            bool gale = ext.IsGale(map.weatherManager?.curWeather);
            if (gale)
            {
                ClearAll();
            }
            else if (galeBlowing)
            {
                RM_WaterLedger.Notify_Opening(map, "the gale has passed");
            }
            galeBlowing = gale;
            if (wetUntil.Count == 0 || Find.TickManager.TicksGame % 2500 != 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            foreach (IntVec3 c in wetUntil.Where(kv => kv.Value <= now).Select(kv => kv.Key).ToList())
            {
                wetUntil.Remove(c);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref wetUntil, "wetUntil", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref lastPourCell, "lastPourCell", IntVec3.Invalid);
            Scribe_Values.Look(ref drawUntilTick, "drawUntilTick", -1);
            Scribe_Values.Look(ref galeBlowing, "galeBlowing", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && wetUntil == null)
            {
                wetUntil = new Dictionary<IntVec3, int>();
            }
        }
    }

    /// <summary>Pour one unit of a water item into the sand where it lies, in a line toward the star.</summary>
    public class RM_JobDriver_PourWaterIntoSand : JobDriver
    {
        private const int PourTicks = 240;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
            yield return Toils_General.Wait(PourTicks).WithProgressBarToilDelay(TargetIndex.A);
            Toil pour = ToilMaker.MakeToil("RM_PourWater");
            pour.initAction = delegate
            {
                Thing water = job.targetA.Thing;
                RM_CompWaterVolume comp = water?.TryGetComp<RM_CompWaterVolume>();
                if (comp == null || !water.Spawned)
                {
                    return;
                }
                Map map = water.Map;
                IntVec3 at = water.Position;
                float litres = comp.Props.litres;
                Thing one = water.SplitOff(1);
                if (!one.Destroyed)
                {
                    one.Destroy();
                }
                List<IntVec3> line = new List<IntVec3> { at };
                line.AddRange(RM_StillsandWater.LineCells(map, at, RM_StillsandWater.TowardSun(map), Mathf.Clamp(Mathf.RoundToInt(litres), 2, 8)));
                int bloomed = RM_StillsandWater.Pour(map, line, litres);
                Messages.Message(pawn.LabelShort + " poured " + litres.ToString("0.#") + " litres into the sand"
                    + (bloomed > 0 ? ". The sand will answer within hours." : "."),
                    new TargetInfo(at, map), MessageTypeDefOf.NeutralEvent, historical: false);
            };
            pour.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return pour;
        }
    }

    public class RM_FloatMenuOptionProvider_PourWater : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            RM_CompWaterVolume comp = clickedThing?.TryGetComp<RM_CompWaterVolume>();
            Pawn pawn = context.FirstSelectedPawn;
            JobDef jobDef = DefDatabase<JobDef>.GetNamedSilentFail("RM_PourWaterIntoSand");
            if (comp == null || pawn == null || jobDef == null || !clickedThing.Spawned
                || !RM_StillsandWater.Remembers(clickedThing.Map, clickedThing.Position))
            {
                return null;
            }
            string label = "Pour " + clickedThing.def.label + " into the sand";
            if (!pawn.CanReach(clickedThing, PathEndMode.ClosestTouch, Danger.Deadly))
            {
                return new FloatMenuOption(label + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }
            return new FloatMenuOption(label, delegate
            {
                pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(jobDef, clickedThing), JobTag.Misc);
            });
        }
    }

    /// <summary>spec 6: bloom-on-pour, the Debt, and its incident weighting. Scribed by RM_StillsandSettings.</summary>
    public static class RM_StillsandWaterSettings
    {
        public static bool bloomOnPour = true;
        public static bool ledgerEnabled = true;
        public static bool ledgerIncidentWeighting = true;
        public static bool drawReturnLine = true;

        public static void Expose()
        {
            Scribe_Values.Look(ref drawReturnLine, "water_drawReturnLine", true);
            Scribe_Values.Look(ref bloomOnPour, "water_bloomOnPour", true);
            Scribe_Values.Look(ref ledgerEnabled, "water_ledgerEnabled", true);
            Scribe_Values.Look(ref ledgerIncidentWeighting, "water_ledgerIncidentWeighting", true);
        }

    }
}
