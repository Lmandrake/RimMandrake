// FlowWorks C# fix batch 2 (review debt 2026-10-26): offline guards for four fixes whose code needs Verse, so each case reads
// the PRODUCTION source (whitespace collapsed, RiverSwitchFlipChecks.Src) and requires the fixed shape; a revert fails here.
// PIPE_ARM_FIX_STALE_BESIDE_NEW_TANK, RIVERPROBE_FIX_FOUR_UNGUARDED_SPAWNS, LADDERINSPECT_FIX_WALL_LEAN_SAYS_NOWHERE,
// DETACHEDBED_HARDEN_REATTACH_NO_WATER. (WEIRCHECKS_FIX_REGEX_READS_NEXT_DEF lives in WeirPoolChecks.cs.)
// NOT proven here: the redraw on a map (a pipe beside a new tank across a section edge), a probe that throws mid-run, the
// inspect pane on a leaning ladder, a legacy save whose pond body is gone. Those stay live checks.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class FwFix2Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        /// <summary>The text from <paramref name="start"/> up to the next <paramref name="end"/> after it.</summary>
        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            Assert(j >= 0, "end marker present: " + end);
            return src.Substring(i, j - i);
        }

        private static int At(string src, string what)
        {
            int i = src.IndexOf(what, StringComparison.Ordinal);
            Assert(i >= 0, "present: " + what);
            return i;
        }

        /// <summary><paramref name="inner"/> sits after the first "try {" following <paramref name="after"/> and before that
        /// try's "finally {", and the finally holds <paramref name="cleanup"/>.</summary>
        private static void Guarded(string body, string after, string inner, string cleanup, string what)
        {
            int a = At(body, after);
            int t = body.IndexOf("try {", a, StringComparison.Ordinal);
            Assert(t > a, what + ": a try follows " + after);
            int f = body.IndexOf("finally {", t, StringComparison.Ordinal);
            Assert(f > t, what + ": the try has a finally");
            int k = body.IndexOf(inner, t, StringComparison.Ordinal);
            Assert(k > t && k < f, what + ": " + inner + " runs inside the try");
            int c = body.IndexOf(cleanup, f, StringComparison.Ordinal);
            Assert(c > f, what + ": the finally holds " + cleanup);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PipeArm_DirtyAround_reprints_the_Things_layer", () =>
            {
                string s = Src("Machinery", "RM_LiquidJoins.cs");
                string body = Between(s, "public static void DirtyAround(Map map, CellRect rect)", "public static void DrawHosePortFitting(");
                Assert(body.Contains("ulong layers = (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things;"),
                    "the ring is dirtied in the Buildings (joins) AND Things (the pipe's own linked tile) layers");
                Assert(body.Contains("map.mapDrawer.MapMeshDirty(c, layers, false, false);")
                       && body.Contains("map.mapDrawer.MapMeshDirty(m.Position, layers, false, false);"), "both dirty calls use them");
                Assert(!body.Contains("MapMeshFlagDefOf.Buildings, false, false)"), "can-fail: no call dirties Buildings alone");
            });
            Case("RiverProbe_every_spawn_is_destroyed_in_a_finally", () =>
            {
                string s = Src("Rivers", "RM_RiverWorksProofWorks.cs");
                string flot = Between(s, "public static string ProofRiverFlotsam(string arg)", "public static string ProofBreach(string arg)");
                Guarded(flot, "comp.TrySpawnFlotsam(true)", "comp.StepOne(t);", "if (arg != \"keep\") { DestroyIfSpawned(t); }", "flotsam");
                Assert(!flot.Contains("t.Destroy();"), "can-fail: the stack is not destroyed only on the happy path");

                string silt = Between(s, "public static string ProofSilt(string arg)", "public static string ProofFerry(string arg)");
                Guarded(silt, "GenSpawn.Spawn(t, c, map)", "trap.RichenOne();", "DestroyIfSpawned(trap);", "silt trap");
                Guarded(silt, "GenSpawn.Spawn(t, c, map)", "trap.Clog();", "if (!clogged && trap.Spawned)", "silt soil reverted on a throw");
                Assert(!silt.Contains("trap.Destroy();"), "can-fail: no happy-path-only destroy");

                string ferry = Between(s, "private static string SpawnFerry(string arg", "public static bool FindFerryCrossing(");
                Guarded(ferry, "pb.SetFaction(Faction.OfPlayer);", "GenSpawn.Spawn(pb, b, map);",
                    "if (!handedOver) { DestroyIfSpawned(pa); DestroyIfSpawned(pb); }", "ferry posts");
                Assert(ferry.Contains("handedOver = arg == \"keep\"; return res;"), "keep hands the posts over only on a normal return");
                Assert(ferry.Contains("bool paired = fa != null && fa.Partner == pb;"), "paired means paired with EACH OTHER");
                Assert(!ferry.Contains("fa?.Partner != null") && !ferry.Contains("pa.Destroy();"),
                    "can-fail: neither any partner nor a happy-path-only destroy");

                string path = Between(s, "public static string ProofFerryPath(string arg)", "private static void DestroyIfSpawned");
                Guarded(path, "SpawnFerry(\"keep\", out Thing postA, out Thing postB)", "data.GatherData(",
                    "DestroyIfSpawned(postA); DestroyIfSpawned(postB); }", "ferry-path posts");
                Guarded(path, "SpawnFerry(\"keep\", out Thing postA, out Thing postB)", "RM_RopePathing.UndraftedCostAt(map, offRope);",
                    "DestroyIfSpawned(postB);", "ferry-path posts (cost read)");
            });
            Case("LadderInspect_wall_lean_has_no_leads_nowhere_line", () =>
            {
                string s = Src("Superdeep", "RM_LadderUtility.cs");
                string body = Between(s, "public override string GetInspectString() { string s = base.GetInspectString();", "public override Graphic Graphic");
                int lean = At(body, "if (RM_LadderParity.LeansOnWall(this)) { return s; }");
                Assert(lean < At(body, "\"RMFlow_LadderHangsOnNothing\""),
                    "a ladder leaning on a wall returns before the hangs-on/leads-nowhere line (RM_CompLadder says climbs over)");
            });
            Case("DetachedBed_reattach_never_writes_unpaid_water", () =>
            {
                string s = Src("RM_MapComponent_Excavation.cs");
                string body = Between(s, "private bool ReattachIfDetachedBed(IntVec3 c, int i)", "public bool CanReturnLevels(");
                int bed = At(body, "TerrainDef bed = RimMandrakeFlowWorksSettings.pondBedHollowEnabled ? LakebedTerrainFor(c) : (body?.fluid ?? ActiveFluid)?.recededTerrain;");
                int miss = At(body, "if (body == null || bed == null) {");
                Assert(bed < miss, "the hollow look is chosen before the null check (a fluid without recededTerrain no longer refuses)");
                string branch = Between(body, "if (body == null || bed == null) {", "return true; }");
                Assert(branch.Contains("map.terrainGrid.SetTerrain(c, FallbackTerrainFor(c));") && branch.Contains("originalTerrain.Remove(i);")
                       && branch.Contains("SetBed(i, 0);"), "no pond: dry natural ground, the water record dropped, no bed");
                Assert(!body.Contains("if (body == null || bed == null || !originalTerrain.ContainsKey(i)) { return false; }"),
                    "can-fail: a missing body no longer falls through to RestoreOriginalTerrain's recorded water");
            });
        }
    }
}
