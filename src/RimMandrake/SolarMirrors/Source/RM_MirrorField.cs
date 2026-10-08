using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §3.4, built under SOLAR_MIRRORS_BUILD_1: the frozen mirror array, the Long Shade puzzle.
    // A biome asks for it with RM_MirrorFieldExtension (the Long Shade gets it by Patches/RM_SolarMirrors_LongShade.xml);
    // RM_GenStep_AncientMirrorField lays a sealed vault, 2-4 sun-stones before its seal and 4-6 seized ancient heliostats
    // on the downsun side, each with 3 detents (visible brass pins). Mapgen SOLVES the layout with the real light pass
    // on the real map before keeping it (RM_MirrorFieldKernel): at least one solution, an unsolved start, the nearest
    // solution at least the difficulty's re-aims away, its relay chain within the cap. Lighting every stone opens the
    // vault, latched (owner ruling 2026-10-04: the vault holds loot and a repaired heliostat). Numbers are PROVISIONAL.

    /// <summary>A biome that carries this gets an ancient mirror field on its maps (setting permitting).</summary>
    public class RM_MirrorFieldExtension : DefModExtension
    {
        public IntRange stones = new IntRange(2, 4);       // PROVISIONAL (design §3.4)
        public int detents = 3;                            // design §3.4 (cut from 4-6 per the GPT consult)
        public float chance = 1f;                          // share of this biome's maps that get a field
    }

    public class RM_GenStep_AncientMirrorField : GenStep
    {
        public ThingDef mirrorDef;
        public ThingDef stoneDef;
        public ThingDef stoneStuff;
        public ThingDef detentDef;
        public ThingDef sealDef;
        public ThingDef wallDef;
        public ThingDef wallStuff;
        public ThingDef rewardDef;
        public List<ThingDefCountRangeClass> loot = new List<ThingDefCountRangeClass>();
        public IntRange ringRadius = new IntRange(9, 15);   // PROVISIONAL: mirrors' distance from the stones
        public int siteAttempts = 40;
        public int layoutAttempts = 30;

        public override int SeedPart => 381104227;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_SolarMirrorsSettings.ancientFields)
            {
                return;
            }
            RM_MirrorFieldExtension ext = map.Biome?.GetModExtension<RM_MirrorFieldExtension>();
            if (ext == null || !Rand.Chance(ext.chance))
            {
                return;
            }
            RM_MirrorFieldBuilder.Lay(this, ext, map);
        }
    }

    public static class RM_MirrorFieldBuilder
    {
        private static readonly List<Thing> spawned = new List<Thing>();
        private static readonly List<IntVec3> roofed = new List<IntVec3>();

        public static bool Lay(RM_GenStep_AncientMirrorField step, RM_MirrorFieldExtension ext, Map map)
        {
            RM_MapComponent_MirrorLight light = RM_MapComponent_MirrorLight.For(map);
            RM_MapComponent_MirrorField field = RM_MapComponent_MirrorField.For(map);
            if (light == null || field == null || step.mirrorDef == null || step.stoneDef == null || step.sealDef == null)
            {
                return false;
            }
            RecomputeShade(map);
            if (!light.TrySun(out Vector3 sun, out float _))
            {
                Note(field, "no sun to reflect on this map");
                return false;
            }
            Vector2 down = new Vector2(-sun.x, -sun.z);
            down = down.sqrMagnitude < 1e-4f ? new Vector2(0f, -1f) : down.normalized;
            int n = Mathf.Clamp(RM_SolarMirrorsSettings.puzzleMirrors, 4, 6);
            int d = Mathf.Max(2, ext.detents);
            int want = Mathf.Clamp(RM_SolarMirrorsSettings.puzzleMinReAims, 2, 4);
            int stonesN = ext.stones.RandomInRange;
            string lastWhy = "no site";
            for (int site = 0; site < step.siteAttempts; site++)
            {
                if (!TryPlan(step, map, down, n, stonesN, out Plan plan))
                {
                    continue;
                }
                SpawnSite(step, map, plan);
                RecomputeShade(map);
                if (TryLayout(step, map, light, plan, n, d, want, out RM_FieldReport report, out List<List<IntVec3>> detents, out int start, out lastWhy))
                {
                    Commit(step, map, field, plan, report, detents, start, d);
                    return true;
                }
                Unspawn(map);
                RecomputeShade(map);
            }
            Note(field, lastWhy);
            return false;
        }

        private static void Note(RM_MapComponent_MirrorField field, string why)
        {
            field.SetFailed(why);
        }

        private static void RecomputeShade(Map map)
        {
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (grid != null && RM_CreatureBehaviorsSettings.shadeGridEnabled)
            {
                grid.Recompute();
            }
        }

        private sealed class Plan
        {
            public IntVec3 center;
            public IntVec3 seal;
            public IntVec3 sealOut;                       // the cell outside the seal
            public readonly List<IntVec3> walls = new List<IntVec3>();
            public readonly List<IntVec3> interior = new List<IntVec3>();
            public readonly List<IntVec3> stones = new List<IntVec3>();
            public readonly List<IntVec3> mirrors = new List<IntVec3>();
        }

        private static bool Clear(Map map, IntVec3 c, bool heavy)
        {
            if (!c.InBounds(map) || c.Roofed(map) || !c.Standable(map) || c.GetEdifice(map) != null)
            {
                return false;
            }
            if (c.GetTerrain(map).IsWater)
            {
                return false;
            }
            return !heavy || c.SupportsStructureType(map, TerrainAffordanceDefOf.Heavy);
        }

        private static IntVec3 Step(IntVec3 from, Vector2 dir, float dist)
        {
            return new IntVec3(Mathf.RoundToInt(from.x + dir.x * dist), 0, Mathf.RoundToInt(from.z + dir.y * dist));
        }

        private static bool TryPlan(RM_GenStep_AncientMirrorField step, Map map, Vector2 down, int n, int stonesN, out Plan plan)
        {
            plan = null;
            CellRect inner = CellRect.WholeMap(map).ContractedBy(28);
            if (inner.Width < 10 || inner.Height < 10)
            {
                return false;
            }
            IntVec3 c = inner.RandomCell;
            Plan p = new Plan { center = c };
            // The seal faces downsun: the face of the 5x5 whose outward normal is nearest `down`.
            IntVec3 face = Mathf.Abs(down.x) >= Mathf.Abs(down.y)
                ? new IntVec3(down.x > 0 ? 1 : -1, 0, 0)
                : new IntVec3(0, 0, down.y > 0 ? 1 : -1);
            p.seal = c + face * 2;
            p.sealOut = c + face * 3;
            for (int dx = -2; dx <= 2; dx++)
            {
                for (int dz = -2; dz <= 2; dz++)
                {
                    IntVec3 v = new IntVec3(c.x + dx, 0, c.z + dz);
                    if (!Clear(map, v, true))
                    {
                        return false;
                    }
                    if (Mathf.Abs(dx) == 2 || Mathf.Abs(dz) == 2)
                    {
                        if (v != p.seal)
                        {
                            p.walls.Add(v);
                        }
                    }
                    else
                    {
                        p.interior.Add(v);
                    }
                }
            }
            if (!Clear(map, p.sealOut, false))
            {
                return false;
            }
            // Stones in a row across the downsun side, 2 cells apart, 4-5 cells out from the seal.
            Vector2 side = new Vector2(-down.y, down.x);
            float rowDist = Rand.Range(4f, 5.5f);
            for (int k = 0; k < stonesN; k++)
            {
                float off = (k - (stonesN - 1) / 2f) * 2.5f;
                IntVec3 s = Step(Step(c, down, 2f + rowDist), side, off);
                if (!Clear(map, s, false) || p.stones.Contains(s))
                {
                    return false;
                }
                p.stones.Add(s);
            }
            // Mirrors on an arc further downsun, facing back toward the stones (the sun side).
            float spread = 110f * Mathf.Deg2Rad;
            for (int k = 0; k < n; k++)
            {
                float t = n == 1 ? 0f : k / (float)(n - 1) - 0.5f;
                float ang = t * spread + Rand.Range(-0.08f, 0.08f);
                Vector2 dir = new Vector2(down.x * Mathf.Cos(ang) - down.y * Mathf.Sin(ang), down.x * Mathf.Sin(ang) + down.y * Mathf.Cos(ang));
                IntVec3 m = Step(Step(c, down, 2f + rowDist), dir, step.ringRadius.RandomInRange);
                foreach (IntVec3 v in GenAdj.OccupiedRect(m, Rot4.North, step.mirrorDef.size))
                {
                    if (!Clear(map, v, false))
                    {
                        return false;
                    }
                }
                foreach (IntVec3 other in p.mirrors)
                {
                    if (Mathf.Abs(other.x - m.x) < 5 && Mathf.Abs(other.z - m.z) < 5)
                    {
                        return false;
                    }
                }
                p.mirrors.Add(m);
            }
            plan = p;
            return true;
        }

        private static void SpawnSite(RM_GenStep_AncientMirrorField step, Map map, Plan p)
        {
            spawned.Clear();
            roofed.Clear();
            foreach (IntVec3 v in p.walls)
            {
                ClearCell(map, v);
                Thing w = ThingMaker.MakeThing(step.wallDef, step.wallDef.MadeFromStuff ? step.wallStuff ?? GenStuff.DefaultStuffFor(step.wallDef) : null);
                spawned.Add(GenSpawn.Spawn(w, v, map));
            }
            ClearCell(map, p.seal);
            spawned.Add(GenSpawn.Spawn(ThingMaker.MakeThing(step.sealDef), p.seal, map));
            foreach (IntVec3 v in p.interior)
            {
                ClearCell(map, v);
                if (!v.Roofed(map))
                {
                    map.roofGrid.SetRoof(v, RoofDefOf.RoofConstructed);
                    roofed.Add(v);
                }
            }
            foreach (IntVec3 v in p.stones)
            {
                ClearCell(map, v);
                Thing s = ThingMaker.MakeThing(step.stoneDef, step.stoneDef.MadeFromStuff ? step.stoneStuff ?? GenStuff.DefaultStuffFor(step.stoneDef) : null);
                spawned.Add(GenSpawn.Spawn(s, v, map));
            }
            foreach (IntVec3 m in p.mirrors)
            {
                foreach (IntVec3 v in GenAdj.OccupiedRect(m, Rot4.North, step.mirrorDef.size))
                {
                    ClearCell(map, v);
                }
                spawned.Add(GenSpawn.Spawn(ThingMaker.MakeThing(step.mirrorDef), m, map));
            }
        }

        private static void ClearCell(Map map, IntVec3 c)
        {
            List<Thing> things = c.GetThingList(map);
            for (int i = things.Count - 1; i >= 0; i--)
            {
                Thing t = things[i];
                if (t is Plant || t.def.category == ThingCategory.Item || t.def.category == ThingCategory.Filth)
                {
                    t.Destroy(DestroyMode.Vanish);
                }
            }
        }

        private static void Unspawn(Map map)
        {
            foreach (Thing t in spawned)
            {
                if (t != null && t.Spawned)
                {
                    t.Destroy(DestroyMode.Vanish);
                }
            }
            spawned.Clear();
            foreach (IntVec3 v in roofed)
            {
                map.roofGrid.SetRoof(v, null);
            }
            roofed.Clear();
        }

        /// <summary>Candidate detent targets: every stone, every other mirror (a relay), and decoy cells near the stones
        /// that a 3x3 spot cannot spill onto a stone from.</summary>
        private static List<IntVec3> Candidates(Map map, Plan p, IntVec3 self)
        {
            List<IntVec3> list = new List<IntVec3>(p.stones);
            foreach (IntVec3 m in p.mirrors)
            {
                if (m != self)
                {
                    list.Add(m);
                }
            }
            foreach (IntVec3 s in p.stones)
            {
                for (int k = 0; k < 6; k++)
                {
                    IntVec3 c = s + new IntVec3(Rand.RangeInclusive(-6, 6), 0, Rand.RangeInclusive(-6, 6));
                    if (!c.InBounds(map) || c.Roofed(map) || c.GetEdifice(map) != null || list.Contains(c))
                    {
                        continue;
                    }
                    bool nearStone = false;
                    foreach (IntVec3 s2 in p.stones)
                    {
                        if (Mathf.Abs(s2.x - c.x) <= 2 && Mathf.Abs(s2.z - c.z) <= 2)
                        {
                            nearStone = true;
                        }
                    }
                    bool inVault = Mathf.Abs(c.x - p.center.x) <= 3 && Mathf.Abs(c.z - p.center.z) <= 3;
                    if (!nearStone && !inVault)
                    {
                        list.Add(c);
                    }
                }
            }
            return list;
        }

        private static bool TryLayout(RM_GenStep_AncientMirrorField step, Map map, RM_MapComponent_MirrorLight light, Plan p, int n, int d,
            int want, out RM_FieldReport report, out List<List<IntVec3>> detents, out int start, out string why)
        {
            report = null;
            detents = null;
            start = -1;
            why = "no layout";
            List<RM_CompMirror> comps = new List<RM_CompMirror>();
            foreach (IntVec3 m in p.mirrors)
            {
                RM_CompMirror c = m.GetEdifice(map)?.TryGetComp<RM_CompMirror>();
                if (c == null)
                {
                    why = "a mirror did not spawn";
                    return false;
                }
                comps.Add(c);
            }
            List<RM_CompLightReceiver> stones = new List<RM_CompLightReceiver>();
            foreach (IntVec3 s in p.stones)
            {
                RM_CompLightReceiver r = s.GetEdifice(map)?.TryGetComp<RM_CompLightReceiver>();
                if (r == null)
                {
                    why = "a sun-stone did not spawn";
                    return false;
                }
                stones.Add(r);
            }
            for (int attempt = 0; attempt < step.layoutAttempts; attempt++)
            {
                List<List<IntVec3>> det = new List<List<IntVec3>>();
                // A hidden intended solution first: stone k is the target of mirror (k + shift) mod n, so every stone
                // has a mirror meant for it; the solver then decides whether the geometry really allows it.
                int shift = Rand.Range(0, n);
                for (int i = 0; i < n; i++)
                {
                    List<IntVec3> cand = Candidates(map, p, p.mirrors[i]);
                    List<IntVec3> mine = new List<IntVec3>();
                    int stoneFor = ((i - shift) % n + n) % n;
                    if (stoneFor < p.stones.Count)
                    {
                        mine.Add(p.stones[stoneFor]);
                    }
                    cand.Shuffle();
                    foreach (IntVec3 c in cand)
                    {
                        if (mine.Count >= d)
                        {
                            break;
                        }
                        if (!mine.Contains(c))
                        {
                            mine.Add(c);
                        }
                    }
                    if (mine.Count < d)
                    {
                        why = "too few detent targets";
                        goto nextAttempt;
                    }
                    mine.Shuffle();
                    det.Add(mine);
                }
                for (int i = 0; i < n; i++)
                {
                    comps[i].SetAncient(det[i], 0, true);
                }
                RM_FieldReport r = RM_MirrorFieldKernel.Solve(n, d, new int[n], (int[] cfg, out int depth) =>
                {
                    for (int i = 0; i < n; i++)
                    {
                        comps[i].SetDetentDirect(cfg[i]);
                    }
                    float[] lt = light.SimulateLight(out depth);
                    for (int k = 0; k < stones.Count; k++)
                    {
                        int idx = map.cellIndices.CellToIndex(stones[k].parent.Position);
                        if (lt == null || lt[idx] < stones[k].Props.litAt)
                        {
                            return false;
                        }
                    }
                    return true;
                });
                int s0 = RM_MirrorFieldKernel.PickStart(r, want, Rand.Int);
                if (s0 < 0)
                {
                    why = r == null ? "space too large" : r.solutionCount == 0 ? "no configuration lights every stone" : "every start is too close to a solution";
                    continue;
                }
                RM_MirrorFieldKernel.Rebase(r, s0);
                if (!RM_MirrorFieldKernel.Acceptable(r, want, RM_SolarMirrorsSettings.maxChain, out why))
                {
                    continue;
                }
                report = r;
                detents = det;
                start = s0;
                return true;
            nextAttempt:;
            }
            return false;
        }

        private static void Commit(RM_GenStep_AncientMirrorField step, Map map, RM_MapComponent_MirrorField field, Plan p,
            RM_FieldReport report, List<List<IntVec3>> detents, int start, int d)
        {
            int n = p.mirrors.Count;
            int[] cfg = new int[n];
            RM_MirrorFieldKernel.Decode(start, n, d, cfg);
            List<Thing> mirrors = new List<Thing>();
            HashSet<IntVec3> pins = new HashSet<IntVec3>();
            for (int i = 0; i < n; i++)
            {
                Thing t = p.mirrors[i].GetEdifice(map);
                t.TryGetComp<RM_CompMirror>().SetAncient(detents[i], cfg[i], true);
                mirrors.Add(t);
                foreach (IntVec3 c in detents[i])
                {
                    pins.Add(c);
                }
            }
            if (step.detentDef != null)
            {
                foreach (IntVec3 c in pins)
                {
                    if (c.InBounds(map) && c.GetEdifice(map) == null && c.GetFirstThing(map, step.detentDef) == null)
                    {
                        GenSpawn.Spawn(ThingMaker.MakeThing(step.detentDef), c, map);
                    }
                }
            }
            // The vault's prize (ruled 2026-10-04): loot and a repaired heliostat, minified.
            List<IntVec3> inside = new List<IntVec3>(p.interior);
            int slot = 0;
            if (step.rewardDef != null)
            {
                Thing reward = MinifyUtility.MakeMinified(ThingMaker.MakeThing(step.rewardDef));
                GenPlace.TryPlaceThing(reward, inside[slot++ % inside.Count], map, ThingPlaceMode.Near);
            }
            foreach (ThingDefCountRangeClass row in step.loot)
            {
                int count = row.countRange.RandomInRange;
                if (row.thingDef == null || count <= 0)
                {
                    continue;
                }
                Thing t = ThingMaker.MakeThing(row.thingDef, row.thingDef.MadeFromStuff ? GenStuff.DefaultStuffFor(row.thingDef) : null);
                t.stackCount = Mathf.Min(count, row.thingDef.stackLimit);
                GenPlace.TryPlaceThing(t, inside[slot++ % inside.Count], map, ThingPlaceMode.Near);
            }
            List<Thing> stones = new List<Thing>();
            foreach (IntVec3 s in p.stones)
            {
                stones.Add(s.GetEdifice(map));
            }
            field.SetField(mirrors, stones, p.seal.GetEdifice(map), report, d);
            spawned.Clear();
            roofed.Clear();
        }
    }

    /// <summary>The ancient field's state on one map: what mapgen laid, the solver's report, how many re-aims the colony
    /// has spent, and the latch. Saved.</summary>
    public class RM_MapComponent_MirrorField : MapComponent
    {
        private List<Thing> mirrors = new List<Thing>();
        private List<Thing> stones = new List<Thing>();
        private Thing seal;
        private bool hasField;
        private bool latched;
        private int reAimsDone;
        private List<int> solutions = new List<int>();
        private int detents = 3;
        private int minReAims = -1;
        private int configurations;
        private int startCode = -1;
        private string failure;

        private static Map cachedMap;
        private static RM_MapComponent_MirrorField cachedComp;

        public RM_MapComponent_MirrorField(Map map) : base(map)
        {
        }

        public static RM_MapComponent_MirrorField For(Map map)
        {
            if (map == null)
            {
                return null;
            }
            if (map == cachedMap && cachedComp != null)
            {
                return cachedComp;
            }
            cachedComp = map.GetComponent<RM_MapComponent_MirrorField>();
            cachedMap = map;
            return cachedComp;
        }

        public bool HasField => hasField;
        public bool Latched => latched;
        public int SolutionCount => solutions.Count;
        public int MinReAims => minReAims;
        public int Configurations => configurations;
        public int ReAimsDone => reAimsDone;
        public Thing Seal => seal;

        public string SolverReport => hasField
            ? "mirrors " + mirrors.Count + " x detents " + detents + ", configurations " + configurations + ", solutions " + solutions.Count
              + ", start " + startCode + " needs " + minReAims + " re-aims, latched " + latched
            : failure == null ? "no field on this map" : "no field: " + failure;

        public bool CurrentlySolved
        {
            get
            {
                if (!hasField || stones.Count == 0)
                {
                    return false;
                }
                foreach (Thing s in stones)
                {
                    RM_CompLightReceiver r = s?.TryGetComp<RM_CompLightReceiver>();
                    if (r == null || !s.Spawned || !r.Lit)
                    {
                        return false;
                    }
                }
                return true;
            }
        }

        public void SetFailed(string why)
        {
            failure = why;
        }

        public void SetField(List<Thing> fieldMirrors, List<Thing> fieldStones, Thing vaultSeal, RM_FieldReport report, int detentsPer)
        {
            mirrors = fieldMirrors;
            stones = fieldStones;
            seal = vaultSeal;
            hasField = true;
            latched = false;
            reAimsDone = 0;
            solutions = new List<int>(report.solutions);
            detents = detentsPer;
            minReAims = report.minReAims;
            configurations = report.configurations;
            startCode = report.startCode;
            failure = null;
        }

        public void Notify_ReAimed(RM_CompMirror m)
        {
            if (hasField && mirrors.Contains(m.parent))
            {
                reAimsDone++;
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!hasField || latched || Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            if (CurrentlySolved)
            {
                Open();
            }
        }

        private void Open()
        {
            latched = true;
            IntVec3 at = seal != null && seal.Spawned ? seal.Position : IntVec3.Invalid;
            if (seal != null && seal.Spawned)
            {
                FleckMaker.ThrowDustPuffThick(seal.DrawPos, map, 2f, new Color(1f, 0.9f, 0.6f));
                seal.Destroy(DestroyMode.Vanish);
            }
            Find.LetterStack.ReceiveLetter("RM_SolarMirrors_VaultOpen_Label".Translate(), "RM_SolarMirrors_VaultOpen_Text".Translate(),
                LetterDefOf.PositiveEvent, at.IsValid ? new LookTargets(at, map) : LookTargets.Invalid);
        }

        /// <summary>Design §3.4 escalating hints, by how many re-aims the colony has spent.</summary>
        public string Hint()
        {
            if (!hasField)
            {
                return null;
            }
            if (latched)
            {
                return "RM_SolarMirrors_Hint_Open".Translate();
            }
            int lit = 0;
            Thing firstDark = null;
            foreach (Thing s in stones)
            {
                RM_CompLightReceiver r = s?.TryGetComp<RM_CompLightReceiver>();
                if (r != null && r.Lit)
                {
                    lit++;
                }
                else if (firstDark == null)
                {
                    firstDark = s;
                }
            }
            StringBuilder sb = new StringBuilder();
            sb.Append("RM_SolarMirrors_Hint_Lit".Translate(lit, stones.Count));
            int level = RM_MirrorFieldKernel.HintLevel(reAimsDone, minReAims);
            if (level >= 1 && firstDark != null)
            {
                bool anyAims = false;
                foreach (Thing m in mirrors)
                {
                    RM_CompMirror c = m?.TryGetComp<RM_CompMirror>();
                    if (c != null && c.Detents.Contains(firstDark.Position))
                    {
                        anyAims = true;
                    }
                }
                sb.AppendLine();
                sb.Append((anyAims ? "RM_SolarMirrors_Hint_Dark" : "RM_SolarMirrors_Hint_DarkRelay").Translate(firstDark.Position.ToString()));
            }
            if (level >= 2)
            {
                int[] cur = new int[mirrors.Count];
                bool ok = true;
                for (int i = 0; i < mirrors.Count; i++)
                {
                    RM_CompMirror c = mirrors[i]?.TryGetComp<RM_CompMirror>();
                    if (c == null || c.DetentIndex < 0)
                    {
                        ok = false;
                        break;
                    }
                    cur[i] = c.DetentIndex;
                }
                if (ok && RM_MirrorFieldKernel.NextMove(solutions, cur, mirrors.Count, detents, out int mi, out int di))
                {
                    sb.AppendLine();
                    sb.Append("RM_SolarMirrors_Hint_Next".Translate(mirrors[mi].Position.ToString(), di + 1));
                }
            }
            return sb.ToString();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hasField, "rmFieldHas", false);
            Scribe_Values.Look(ref latched, "rmFieldLatched", false);
            Scribe_Values.Look(ref reAimsDone, "rmFieldReAims", 0);
            Scribe_Values.Look(ref detents, "rmFieldDetents", 3);
            Scribe_Values.Look(ref minReAims, "rmFieldMinReAims", -1);
            Scribe_Values.Look(ref configurations, "rmFieldConfigurations", 0);
            Scribe_Values.Look(ref startCode, "rmFieldStart", -1);
            Scribe_Values.Look(ref failure, "rmFieldFailure");
            Scribe_Collections.Look(ref solutions, "rmFieldSolutions", LookMode.Value);
            Scribe_Collections.Look(ref mirrors, "rmFieldMirrors", LookMode.Reference);
            Scribe_Collections.Look(ref stones, "rmFieldStones", LookMode.Reference);
            Scribe_References.Look(ref seal, "rmFieldSeal");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                solutions ??= new List<int>();
                mirrors ??= new List<Thing>();
                stones ??= new List<Thing>();
                mirrors.RemoveAll(t => t == null);
                stones.RemoveAll(t => t == null);
            }
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            if (cachedMap == map)
            {
                cachedMap = null;
                cachedComp = null;
            }
        }
    }

    /// <summary>The vault's seal: its inspect pane is the puzzle's readout (stones lit, then the escalating hints).</summary>
    public class RM_CompSunVaultSeal : ThingComp
    {
        public override string CompInspectStringExtra()
        {
            return RM_MapComponent_MirrorField.For(parent.Map)?.Hint();
        }
    }
}
