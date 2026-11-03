using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LongShade
{
    /// <summary>static_call probe for LONGSHADE_SCENE_LIVECHECK_1 (driven by LongShade/prove_shade_extras.py): tollok ticks,
    /// lure awning and harrok on one RM_LongShade map. Every method works on Find.CurrentMap and returns ONE line of
    /// key=value pairs the driver parses (text values are URI-escaped so they hold no spaces):
    ///   Toggle("field=bool")  sets a public static bool of RM_LongShadeSettings: "TOGGLE field=F was=B now=B"
    ///   Arm("")               hooks Verse.Messages.Message(string, LookTargets, MessageTypeDef, bool) with a prefix (counts every
    ///                         call the mod makes, even one the game then drops as a duplicate) and clears the record: "ARMED patched=N"
    ///   Cells("")             resets the probe (Cleanup), then up to 3 WILD deep-shade cells (ShadeAt >= 0.7, no roof shade, no gear shade, 3x3 clear and
    ///                         standable), mutually >= 12 apart: "CELLS biome=X grid=B dir=x,z n=N c=x,z;x,z;x,z"
    ///   TollokStage("on")     drafted colonists on the three cells (roles wild, roof, awning); a built roof
    ///                         (RoofConstructed) over the roof cell's 3x3 and an RM_LureAwning centred on the awning cell,
    ///                         then a shade recompute. "TSTAGED ..."
    ///   TollokStage("off")    despawns the three, a fresh drafted colonist (role off) on the wild cell. "TSTAGED ..."
    ///   Tollok("")            per role r: r_hed r_sev r_shade r_roof r_gear r_cast r_moved r_dead
    ///   Awning(arg)           spawns (arg "spawn") a wild Hare on the awning's centre, then reads the comp's inspect line and
    ///                         Thing.GetInspectString: "AWNING gear=F shade=F wild=N setting=B extra=<esc> full=<esc>"
    ///   HarrokStage("")       a wild RM_Harrok on an unroofed open cell held still (Wait), two downed (Anesthetic, no
    ///                         apparel) colonists in its shadow strip (roles prey1, prey2) and one up-sun (role ctrl).
    ///   Harrok("")            "HARROK pos=x,z moved=B roofed=B enabled=B last=N now=N msgs=N exact=N" + per role stab count,
    ///                         stab severity, missing parts, dead, inStrip
    ///   Cleanup("")           despawns everything this probe spawned and unhooks Messages.
    /// Nothing here changes the mechanism; it stages the scene and reads it.</summary>
    public static class RM_ShadeExtrasProof
    {
        private const string HarmonyId = "rimmandrake.longshade.shadeextrasproof";
        private static readonly Dictionary<string, Pawn> roles = new Dictionary<string, Pawn>();
        private static readonly Dictionary<string, IntVec3> spots = new Dictionary<string, IntVec3>();
        private static readonly List<Thing> spawned = new List<Thing>();
        private static readonly List<IntVec3> roofed = new List<IntVec3>();
        private static readonly List<string> messages = new List<string>();
        private static List<IntVec3> cells = new List<IntVec3>();
        private static Thing awning;
        private static Pawn harrok;
        private static IntVec3 harrokSpot = IntVec3.Invalid;
        private static Vector2 harrokDir;

        private static string F(float v) => v.ToString("0.###", CultureInfo.InvariantCulture);
        private static string C(IntVec3 c) => c.x + "," + c.z;
        private static string Esc(string s) => Uri.EscapeDataString(s ?? "");

        private static RM_MapComponent_ShadeGrid Grid(Map map) => map == null ? null : RM_MapComponent_ShadeGrid.For(map);

        // ------------------------------------------------------------------ settings
        public static string Toggle(string arg)
        {
            string[] kv = (arg ?? "").Split('=');
            if (kv.Length != 2) return "REFUSED: want field=bool";
            FieldInfo f = typeof(RM_LongShadeSettings).GetField(kv[0], BindingFlags.Public | BindingFlags.Static);
            if (f == null || f.FieldType != typeof(bool)) return "REFUSED: no static bool RM_LongShadeSettings." + kv[0];
            bool was = (bool)f.GetValue(null);
            f.SetValue(null, kv[1].Trim().ToLowerInvariant() == "true");
            return "TOGGLE field=" + kv[0] + " was=" + was + " now=" + f.GetValue(null);
        }

        // ------------------------------------------------------------------ messages
        public static string Arm(string _)
        {
            messages.Clear();
            Harmony h = new Harmony(HarmonyId);
            h.UnpatchAll(HarmonyId);
            MethodInfo prefix = typeof(RM_ShadeExtrasProof).GetMethod(nameof(MessagePrefix), BindingFlags.NonPublic | BindingFlags.Static);
            // only the overload the harrok calls (Message(string, LookTargets, MessageTypeDef, bool)): patching every string
            // overload would count twice if one forwards to another
            MethodInfo m = AccessTools.Method(typeof(Messages), "Message",
                new[] { typeof(string), typeof(LookTargets), typeof(MessageTypeDef), typeof(bool) });
            if (m == null) return "REFUSED: no Messages.Message(string, LookTargets, MessageTypeDef, bool)";
            h.Patch(m, prefix: new HarmonyMethod(prefix));
            int n = 1;
            return "ARMED patched=" + n;
        }

        private static void MessagePrefix(string __0)
        {
            if (__0 != null && __0.IndexOf("harrok", StringComparison.OrdinalIgnoreCase) >= 0) messages.Add(__0);
        }

        // ------------------------------------------------------------------ cells
        private static bool Clear3x3(Map map, IntVec3 c)
        {
            foreach (IntVec3 x in CellRect.CenteredOn(c, 1))
            {
                if (!x.InBounds(map) || !x.Standable(map) || x.GetEdifice(map) != null || x.GetFirstPawn(map) != null) return false;
                if (x.Roofed(map)) return false;
            }
            return c.x > 8 && c.z > 8 && c.x < map.Size.x - 8 && c.z < map.Size.z - 8;
        }

        private static bool WildDeep(RM_MapComponent_ShadeGrid g, IntVec3 c, float min)
        {
            return g.ShadeAt(c) >= min && g.RoofShadeAt(c) <= 0.01f && g.GearShadeAt(c) <= 0.01f;
        }

        public static string Cells(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_ShadeGrid g = Grid(map);
            if (map == null || g == null) return "REFUSED: no current map or no shade grid";
            Cleanup("");   // a fresh scene: nothing left over from an earlier map or an aborted run
            List<IntVec3> deep = map.AllCells.Where(c => WildDeep(g, c, RM_ShadeExtrasTuning.DeepShade) && Clear3x3(map, c))
                .OrderByDescending(c => CellRect.CenteredOn(c, 1).Cells.Min(x => g.ShadeAt(x))).ToList();
            List<IntVec3> pick = new List<IntVec3>();
            foreach (IntVec3 c in deep)
            {
                if (pick.All(p => p.DistanceTo(c) >= 12f)) pick.Add(c);
                if (pick.Count == 3) break;
            }
            cells = pick;
            Vector2 d = g.SunShadowDirection;
            return "CELLS biome=" + map.Biome.defName + " grid=" + RM_CreatureBehaviorsSettings.shadeGridEnabled
                + " dir=" + F(d.x) + "," + F(d.y) + " deepCells=" + deep.Count + " n=" + pick.Count
                + " c=" + string.Join(";", pick.Select(C).ToArray())
                + " shades=" + string.Join(";", pick.Select(c => F(g.ShadeAt(c))).ToArray());
        }

        // ------------------------------------------------------------------ tollok
        private static Pawn Colonist(Map map, IntVec3 at, bool drafted)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            GenSpawn.Spawn(p, at, map);
            if (drafted && p.drafter != null) p.drafter.Drafted = true;   // stays put: no job moves it
            spawned.Add(p);
            return p;
        }

        private static void Despawn(string role)
        {
            if (roles.TryGetValue(role, out Pawn p) && p != null && p.Spawned) p.DeSpawn();
        }

        public static string TollokStage(string arg)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_ShadeGrid g = Grid(map);
            if (map == null || g == null || cells.Count < 3) return "REFUSED: run Cells first (need 3 wild deep cells)";
            if (arg == "off")
            {
                foreach (string r in new[] { "wild", "roof", "awning" }) Despawn(r);
                roles["off"] = Colonist(map, cells[0], true);
                spots["off"] = cells[0];
                return "TSTAGED off=" + C(cells[0]);
            }
            float cast1 = g.CastShadeAt(cells[1]);
            foreach (IntVec3 c in CellRect.CenteredOn(cells[1], 1))
            {
                map.roofGrid.SetRoof(c, RoofDefOf.RoofConstructed);
                roofed.Add(c);
            }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LureAwning");
            if (def == null) return "REFUSED: no ThingDef RM_LureAwning";
            awning = ThingMaker.MakeThing(def, GenStuff.DefaultStuffFor(def));
            awning.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(awning, cells[2], map, Rot4.North);
            spawned.Add(awning);
            g.Recompute();
            string[] names = { "wild", "roof", "awning" };
            for (int i = 0; i < 3; i++)
            {
                roles[names[i]] = Colonist(map, cells[i], true);
                spots[names[i]] = cells[i];
            }
            return "TSTAGED wild=" + C(cells[0]) + " roof=" + C(cells[1]) + " awning=" + C(cells[2]) + " roofCastBefore=" + F(cast1)
                + " roofNow=" + F(g.RoofShadeAt(cells[1])) + " awningGear=" + F(g.GearShadeAt(cells[2]));
        }

        public static string Tollok(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_ShadeGrid g = Grid(map);
            if (map == null || g == null) return "REFUSED: no current map or no shade grid";
            HediffDef hd = RM_ShadeExtrasDefOf.RM_TollokInfestation;
            List<string> parts = new List<string> { "TOLLOK biome=" + map.Biome.defName + " tick=" + Find.TickManager.TicksGame
                + " setting=" + (RM_LongShadeSettings.modEnabled && RM_LongShadeSettings.tollokTicksEnabled) };
            foreach (KeyValuePair<string, Pawn> kv in roles)
            {
                if (!spots.ContainsKey(kv.Key) || kv.Key.StartsWith("prey") || kv.Key == "ctrl") continue;
                Pawn p = kv.Value;
                IntVec3 at = spots[kv.Key];
                Hediff h = hd == null ? null : p.health.hediffSet.GetFirstHediffOfDef(hd);
                string r = kv.Key;
                parts.Add(r + "_hed=" + (h != null) + " " + r + "_sev=" + F(h?.Severity ?? 0f) + " " + r + "_shade=" + F(g.ShadeAt(at))
                    + " " + r + "_roof=" + F(g.RoofShadeAt(at)) + " " + r + "_gear=" + F(g.GearShadeAt(at)) + " " + r + "_cast=" + F(g.CastShadeAt(at))
                    + " " + r + "_moved=" + (!p.Spawned || p.Position != at) + " " + r + "_dead=" + p.Dead);
            }
            return string.Join(" ", parts.ToArray());
        }

        // ------------------------------------------------------------------ lure awning
        public static string Awning(string arg)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_ShadeGrid g = Grid(map);
            if (map == null || g == null || awning == null || !awning.Spawned) return "REFUSED: no spawned awning (run TollokStage on first)";
            if (arg == "spawn")
            {
                PawnKindDef hare = DefDatabase<PawnKindDef>.GetNamedSilentFail("Hare");
                if (hare == null) return "REFUSED: no PawnKindDef Hare";
                Pawn a = PawnGenerator.GeneratePawn(hare, null);
                GenSpawn.Spawn(a, awning.Position, map);
                spawned.Add(a);
            }
            int wild = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(awning.Position, RM_ShadeExtrasTuning.LureRadius, true))
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map))
                    if (t is Pawn p && p.RaceProps.Animal && p.Faction == null && g.ShadeAt(c) >= RM_ShadeExtrasTuning.ShelterShade) wild++;
            }
            RM_CompLureAwning comp = awning.TryGetComp<RM_CompLureAwning>();
            return "AWNING gear=" + F(g.GearShadeAt(awning.Position)) + " shade=" + F(g.ShadeAt(awning.Position)) + " wild=" + wild
                + " setting=" + (RM_LongShadeSettings.modEnabled && RM_LongShadeSettings.lureAwningEnabled)
                + " extra=" + Esc(comp?.CompInspectStringExtra()) + " full=" + Esc(awning.GetInspectString());
        }

        // ------------------------------------------------------------------ harrok
        private static Pawn Prey(Map map, IntVec3 at)
        {
            Pawn p = Colonist(map, at, false);
            p.apparel?.DestroyAll();
            p.equipment?.DestroyAllEquipment();
            Hediff an = HediffMaker.MakeHediff(HediffDefOf.Anesthetic, p);
            an.Severity = 1f;
            p.health.AddHediff(an);
            return p;
        }

        private static bool InStrip(IntVec3 h, IntVec3 c, Vector2 dir, CompProperties_RM_HarrokAmbush pr)
        {
            return RM_LongShadeKernel.InShadowStrip(c.x - h.x, c.z - h.z, dir.x, dir.y, pr.shadowLengthCells, pr.shadowHalfWidth);
        }

        public static string HarrokStage(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_ShadeGrid g = Grid(map);
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Harrok");
            if (map == null || g == null || kind == null) return "REFUSED: no map, shade grid or PawnKindDef RM_Harrok";
            CompProperties_RM_HarrokAmbush pr = kind.race.GetCompProperties<CompProperties_RM_HarrokAmbush>();
            if (pr == null) return "REFUSED: RM_Harrok has no CompProperties_RM_HarrokAmbush";
            Vector2 dir = g.SunShadowDirection;
            if (dir.sqrMagnitude < 0.0001f) return "REFUSED: no sun shadow direction";
            dir.Normalize();
            // predators would bite the downed prey and confound the reading
            foreach (Pawn w in map.mapPawns.AllPawnsSpawned.ToList())
                if (w.Faction == null && w.RaceProps.predator) w.DeSpawn();
            // an undrafted colonist would walk in to tend the downed prey and stand in the strip itself
            foreach (Pawn c in map.mapPawns.FreeColonistsSpawned.ToList())
                if (!c.Downed && c.drafter != null) c.drafter.Drafted = true;
            Func<IntVec3, bool> free = c => c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null && c.GetFirstPawn(map) == null
                && !c.Roofed(map) && c.DistanceToEdge(map) > 8 && cells.All(x => x.DistanceTo(c) > 14f);
            IntVec3 centre = map.Center;
            foreach (IntVec3 h in GenRadial.RadialCellsAround(centre, Mathf.Min(GenRadial.MaxRadialPatternRadius - 1f, Mathf.Min(centre.x, centre.z) - 10), true))
            {
                if (!free(h)) continue;
                List<IntVec3> strip = new List<IntVec3>();
                for (int k = 2; k <= 5 && strip.Count < 2; k++)
                {
                    IntVec3 c = h + new IntVec3(Mathf.RoundToInt(dir.x * k), 0, Mathf.RoundToInt(dir.y * k));
                    if (c != h && !strip.Contains(c) && free(c) && InStrip(h, c, dir, pr)
                        && GenSight.LineOfSight(h, c, map, skipFirstCell: true)) strip.Add(c);
                }
                IntVec3 q = h - new IntVec3(Mathf.RoundToInt(dir.x * 3), 0, Mathf.RoundToInt(dir.y * 3));
                if (strip.Count < 2 || !free(q) || InStrip(h, q, dir, pr)) continue;
                harrok = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(harrok, h, map);
                spawned.Add(harrok);
                harrokSpot = h;
                harrokDir = dir;
                Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                wait.expiryInterval = 20000;
                harrok.jobs.StartJob(wait, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
                roles["prey1"] = Prey(map, strip[0]); spots["prey1"] = strip[0];
                roles["prey2"] = Prey(map, strip[1]); spots["prey2"] = strip[1];
                roles["ctrl"] = Prey(map, q); spots["ctrl"] = q;
                return "HSTAGED harrok=" + C(h) + " dir=" + F(dir.x) + "," + F(dir.y) + " prey1=" + C(strip[0]) + " prey2=" + C(strip[1])
                    + " ctrl=" + C(q) + " downed=" + (roles["prey1"].Downed && roles["prey2"].Downed && roles["ctrl"].Downed)
                    + " length=" + F(pr.shadowLengthCells) + " halfWidth=" + F(pr.shadowHalfWidth) + " cooldown=" + pr.cooldownTicks
                    + " maxPrey=" + F(pr.maxPreyBodySize) + " dmg=" + F(pr.strikeDamageRange.min) + "-" + F(pr.strikeDamageRange.max);
            }
            return "REFUSED: no open cell with two free strip cells and a free up-sun cell";
        }

        public static string Harrok(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_ShadeGrid g = Grid(map);
            if (map == null || g == null || harrok == null) return "REFUSED: run HarrokStage first";
            RM_CompHarrokAmbush comp = harrok.TryGetComp<RM_CompHarrokAmbush>();
            FieldInfo fl = typeof(RM_CompHarrokAmbush).GetField("lastStrike", BindingFlags.NonPublic | BindingFlags.Instance);
            int last = comp != null && fl != null ? (int)fl.GetValue(comp) : int.MinValue;
            CompProperties_RM_HarrokAmbush pr = harrok.def.GetCompProperties<CompProperties_RM_HarrokAmbush>();
            Vector2 dir = g.SunShadowDirection;
            if (dir.sqrMagnitude > 0.0001f) dir.Normalize();
            int exact = 0;
            List<string> parts = new List<string>();
            HediffDef stab = DamageDefOf.Stab.hediff;
            foreach (string r in new[] { "prey1", "prey2", "ctrl" })
            {
                if (!roles.TryGetValue(r, out Pawn p)) continue;
                string want = "A harrok's shadow fell across " + p.LabelShort + ", and the harrok struck.";
                exact += messages.Count(m => m == want);
                List<Hediff> st = p.health.hediffSet.hediffs.Where(x => x is Hediff_Injury && x.def == stab).ToList();
                parts.Add(r + "_stab=" + st.Count + " " + r + "_stabsev=" + F(st.Sum(x => x.Severity))
                    + " " + r + "_missing=" + p.health.hediffSet.hediffs.Count(x => x is Hediff_MissingPart)
                    + " " + r + "_dead=" + p.Dead + " " + r + "_downed=" + p.Downed + " " + r + "_size=" + F(p.BodySize)
                    + " " + r + "_inStrip=" + (pr != null && InStrip(harrok.Position, spots[r], dir, pr)));
            }
            return "HARROK pos=" + C(harrok.Position) + " moved=" + (!harrok.Spawned || harrok.Position != harrokSpot)
                + " roofed=" + (harrok.Spawned && harrok.Position.Roofed(map)) + " wild=" + (harrok.Faction == null)
                + " enabled=" + (RM_LongShadeSettings.modEnabled && RM_LongShadeSettings.harrokEnabled)
                + " dirNow=" + F(dir.x) + "," + F(dir.y) + " dirStaged=" + F(harrokDir.x) + "," + F(harrokDir.y)
                + " last=" + last + " now=" + Find.TickManager.TicksGame + " msgs=" + messages.Count + " exact=" + exact + " " + string.Join(" ", parts.ToArray());
        }

        // ------------------------------------------------------------------ cleanup
        public static string Cleanup(string _)
        {
            Map map = Find.CurrentMap;
            int n = 0;
            foreach (Thing t in spawned) if (t != null && t.Spawned) { t.Destroy(DestroyMode.Vanish); n++; }
            if (map != null) foreach (IntVec3 c in roofed) if (c.InBounds(map)) map.roofGrid.SetRoof(c, null);
            new Harmony(HarmonyId).UnpatchAll(HarmonyId);
            spawned.Clear(); roofed.Clear(); roles.Clear(); spots.Clear(); messages.Clear(); cells.Clear();
            awning = null; harrok = null; harrokSpot = IntVec3.Invalid;
            return "CLEANED destroyed=" + n;
        }
    }
}
