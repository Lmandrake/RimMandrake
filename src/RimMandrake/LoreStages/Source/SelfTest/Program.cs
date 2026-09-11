// Offline selftest for mandrake.rm.lorestages (STAGED_LORE_BUILD_1).
//
// Same discipline as RimMandrakeAftermath.SelfTest: compile the REAL
// production .cs files in directly and exercise them, rather than
// reimplementing the logic here and drifting out of sync. Everything under
// test runs with no Game, no Map and no DefDatabase — the applier takes its def
// resolver as a delegate precisely so this is possible, and the production
// resolver (LoreStageDefDatabase.cs, which does need a loaded mod set) is NOT
// compiled into this project.
//
// 🔴 WHAT THIS PROVES, and why each case is not a name list:
//
//   The reflection cache-clear. ThingDef.descriptionDetailedCached and
//   HediffDef.descriptionCached are real private fields on the real engine
//   types loaded out of Assembly-CSharp.dll. Each cache case POPULATES the
//   cache by reading the public getter first, then applies a stage, then reads
//   the getter again and asserts the NEW text. The negative control mutates
//   `description` on a def the applier never touched and asserts the getter
//   still returns the OLD text — if that control ever passes with the new text,
//   the cache was never populated and every other cache assertion is vacuous.
//
//   Reset-to-baseline. Defs are process-global and are not reloaded between
//   savegames, so the hazard is a stage-5 colony's text surviving into a
//   stage-0 save. The test applies a high stage, then a LOWER one, then zero,
//   and asserts the exact shipped string comes back — which only holds if the
//   applier resets from a snapshot rather than advancing incrementally.
//
// Run:
//   "%USERPROFILE%\.dotnet\dotnet.exe" run --project D:\Luke\dev\Rimworld\src\RimMandrake\LoreStages\Source\SelfTest\RimMandrakeLoreStages.SelfTest.csproj -c Release

using System;
using System.Collections.Generic;
using RimMandrake.LoreStages;
using RimWorld;
using Verse;

namespace RimMandrake.LoreStages.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new List<string>();
        private static readonly List<string> Fail = new List<string>();

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                Pass.Add(name);
                Console.WriteLine("ok    " + name);
            }
            catch (Exception ex)
            {
                Fail.Add(name + ": " + ex.Message);
                Console.WriteLine("FAIL  " + name + ": " + ex.Message);
            }
        }

        private static void Eq(string expected, string actual, string what)
        {
            if (!string.Equals(expected, actual, StringComparison.Ordinal))
            {
                throw new Exception($"{what}: expected <{expected}> got <{actual}>");
            }
        }

        private static void True(bool cond, string what)
        {
            if (!cond) throw new Exception(what);
        }

        // ── fixtures ────────────────────────────────────────────────────────

        // `new ThingDef()` cannot run in a bare console process: one of its
        // field initializers pulls in Verse.BaseContent, whose static
        // constructor wants the Unity resource pipeline and throws a
        // TypeInitializationException with no game around it. That is a
        // limitation of the HARNESS, not of the mechanism — the real game
        // constructs its ThingDefs normally.
        //
        // GetUninitializedObject allocates the real ThingDef type (real layout,
        // real private descriptionDetailedCached, real DescriptionDetailed
        // getter) while skipping field initializers. Every field these tests
        // read or write is set explicitly below, and the two fields the getter
        // consults — `description` and `apparel` (via IsApparel) — are set and
        // null respectively, exactly as they would be for a plain non-apparel
        // def. BiomeDef and HediffDef construct normally and are left alone.
        private static ThingDef MakeThingDef(string defName, string description)
        {
            var d = (ThingDef)System.Runtime.Serialization.FormatterServices
                .GetUninitializedObject(typeof(ThingDef));
            d.defName = defName;
            d.description = description;
            return d;
        }

        private const string BiomeBaseline = "SHIPPED BIOME TEXT";
        private const string BiomeWarnBaseline = "SHIPPED SETTLE WARNING";
        private const string ItemBaseline = "SHIPPED ITEM TEXT";
        private const string HediffBaseline = "SHIPPED HEDIFF TEXT";

        private sealed class Fixture
        {
            public BiomeDef biome;
            public ThingDef item;
            public HediffDef hediff;
            public RM_LoreStageTableDef table;
            public Dictionary<string, int> stages;
            public List<string> warnings;

            public LoreStageApplier.DefResolver Resolver => (typeName, defName) =>
            {
                if (defName == "TEST_Biome" && typeName == "BiomeDef") return biome;
                if (defName == "TEST_Item" && typeName == "ThingDef") return item;
                if (defName == "TEST_Hediff" && typeName == "HediffDef") return hediff;
                return null;
            };

            public int Apply()
            {
                return LoreStageApplier.ResetAndApply(
                    new[] { table },
                    id => stages.TryGetValue(id, out int s) ? s : 0,
                    Resolver,
                    w => warnings.Add(w));
            }
        }

        private static Fixture NewFixture()
        {
            // A fresh process-global baseline map per case: production never
            // does this (dropping baselines after a mutation would lose the
            // shipped text for good) but each case must start from zero.
            LoreStageApplier.ForgetBaselinesForTesting();

            var f = new Fixture
            {
                biome = new BiomeDef { defName = "TEST_Biome", description = BiomeBaseline, settleWarning = BiomeWarnBaseline },
                item = MakeThingDef("TEST_Item", ItemBaseline),
                hediff = new HediffDef { defName = "TEST_Hediff", description = HediffBaseline },
                stages = new Dictionary<string, int>(),
                warnings = new List<string>(),
            };

            f.table = new RM_LoreStageTableDef
            {
                defName = "TEST_Ladder",
                ladderId = "TestLadder",
                maxStage = 5,
                targets = new List<LoreStageTarget>
                {
                    new LoreStageTarget
                    {
                        defType = "BiomeDef", defName = "TEST_Biome", field = "description",
                        stages = new List<LoreStageText>
                        {
                            // Deliberate gap at 2 and 4: a rung with no entry
                            // means "this field does not change here", and the
                            // last rung at or below the stage must persist.
                            new LoreStageText { stage = 1, text = "BIOME@1" },
                            new LoreStageText { stage = 3, text = "BIOME@3" },
                            new LoreStageText { stage = 5, text = "BIOME@5" },
                        },
                    },
                    new LoreStageTarget
                    {
                        defType = "BiomeDef", defName = "TEST_Biome", field = "settleWarning",
                        stages = new List<LoreStageText>
                        {
                            new LoreStageText { stage = 3, text = "WARN@3\n\nsecond paragraph" },
                        },
                    },
                    new LoreStageTarget
                    {
                        defType = "ThingDef", defName = "TEST_Item", field = "description",
                        stages = new List<LoreStageText>
                        {
                            new LoreStageText { stage = 2, text = "ITEM@2" },
                        },
                    },
                    new LoreStageTarget
                    {
                        defType = "HediffDef", defName = "TEST_Hediff", field = "description",
                        stages = new List<LoreStageText>
                        {
                            new LoreStageText { stage = 2, text = "HEDIFF@2" },
                        },
                    },
                },
            };

            return f;
        }

        private static int Main()
        {
            Console.WriteLine("RimMandrake.LoreStages selftest (STAGED_LORE_BUILD_1)");
            Console.WriteLine();

            // ── the engine contract this whole mod rests on ─────────────────

            Case("both private description caches are reachable by name", () =>
            {
                True(LoreStageApplier.CachesReachable,
                    "a private cache field was not found: " + LoreStageApplier.CacheReachabilityReport);
            });

            Case("NEGATIVE CONTROL: ThingDef.DescriptionDetailed really is memoized", () =>
            {
                // Without this passing, every DescriptionDetailed assertion
                // below would be true for the trivial reason that nothing was
                // ever cached.
                ThingDef d = MakeThingDef("TEST_Control", "OLD");
                Eq("OLD", d.DescriptionDetailed, "first read");
                d.description = "NEW";                       // no cache clear
                Eq("OLD", d.DescriptionDetailed, "stale read after a bare field write");
            });

            Case("NEGATIVE CONTROL: HediffDef.Description really is memoized", () =>
            {
                var d = new HediffDef { defName = "TEST_ControlH", description = "OLD" };
                Eq("OLD", d.Description, "first read");
                d.description = "NEW";
                Eq("OLD", d.Description, "stale read after a bare field write");
            });

            // ── the reflection clear ────────────────────────────────────────

            Case("stage change busts ThingDef.descriptionDetailedCached", () =>
            {
                Fixture f = NewFixture();
                Eq(ItemBaseline, f.item.DescriptionDetailed, "cache primed at baseline");

                f.stages["TestLadder"] = 2;
                f.Apply();

                Eq("ITEM@2", f.item.description, "raw field");
                Eq("ITEM@2", f.item.DescriptionDetailed, "CACHED path after stage change");
            });

            Case("stage change busts HediffDef.descriptionCached", () =>
            {
                Fixture f = NewFixture();
                Eq(HediffBaseline, f.hediff.Description, "cache primed at baseline");

                f.stages["TestLadder"] = 2;
                f.Apply();

                Eq("HEDIFF@2", f.hediff.description, "raw field");
                Eq("HEDIFF@2", f.hediff.Description, "CACHED path after stage change");
            });

            Case("returning to stage 0 busts both caches back to shipped text", () =>
            {
                Fixture f = NewFixture();
                f.stages["TestLadder"] = 2;
                f.Apply();
                Eq("ITEM@2", f.item.DescriptionDetailed, "primed at stage 2");
                Eq("HEDIFF@2", f.hediff.Description, "primed at stage 2");

                f.stages["TestLadder"] = 0;
                f.Apply();

                Eq(ItemBaseline, f.item.DescriptionDetailed, "ThingDef cached path back at baseline");
                Eq(HediffBaseline, f.hediff.Description, "HediffDef cached path back at baseline");
            });

            // ── rung selection ──────────────────────────────────────────────

            Case("highest rung at or below the current stage wins, gaps persist", () =>
            {
                Fixture f = NewFixture();
                var expected = new (int stage, string text)[]
                {
                    (0, BiomeBaseline),
                    (1, "BIOME@1"),
                    (2, "BIOME@1"),   // gap at 2 — rung 1 persists
                    (3, "BIOME@3"),
                    (4, "BIOME@3"),   // gap at 4 — rung 3 persists
                    (5, "BIOME@5"),
                };

                foreach ((int stage, string text) in expected)
                {
                    f.stages["TestLadder"] = stage;
                    f.Apply();
                    Eq(text, f.biome.description, "biome description at stage " + stage);
                }
            });

            Case("a non-description field on a non-ThingDef stages too (settleWarning)", () =>
            {
                Fixture f = NewFixture();
                f.stages["TestLadder"] = 3;
                f.Apply();
                Eq("WARN@3\n\nsecond paragraph", f.biome.settleWarning, "staged settle warning");
                // The other field of the SAME def must move independently.
                Eq("BIOME@3", f.biome.description, "description of the same def");
            });

            // ── the reset-on-load hazard ────────────────────────────────────

            Case("RESET: a lower stage does not inherit a higher stage's text", () =>
            {
                // The savegame leak, in miniature: one process, stage 5 applied,
                // then a "load" of a stage-1 game.
                Fixture f = NewFixture();
                f.stages["TestLadder"] = 5;
                f.Apply();
                Eq("BIOME@5", f.biome.description, "at stage 5");

                f.stages["TestLadder"] = 1;
                f.Apply();
                Eq("BIOME@1", f.biome.description, "after dropping to stage 1");
                Eq(BiomeWarnBaseline, f.biome.settleWarning, "settleWarning must fall back to shipped, not stay at WARN@3");
            });

            Case("RESET: stage 0 restores the shipped strings byte for byte", () =>
            {
                Fixture f = NewFixture();
                f.stages["TestLadder"] = 5;
                f.Apply();

                f.stages["TestLadder"] = 0;
                f.Apply();

                Eq(BiomeBaseline, f.biome.description, "biome description");
                Eq(BiomeWarnBaseline, f.biome.settleWarning, "biome settleWarning");
                Eq(ItemBaseline, f.item.description, "item description");
                Eq(HediffBaseline, f.hediff.description, "hediff description");
            });

            Case("RESET: baseline survives a def that was never at stage 0 on first apply", () =>
            {
                // The nastier ordering: the FIRST apply this process ever makes
                // is at a high stage. The snapshot must still be the shipped
                // text, because it is taken before the first write.
                Fixture f = NewFixture();
                f.stages["TestLadder"] = 5;
                f.Apply();
                Eq("BIOME@5", f.biome.description, "first apply at stage 5");

                f.stages["TestLadder"] = 0;
                f.Apply();
                Eq(BiomeBaseline, f.biome.description, "shipped text recovered from the pre-write snapshot");
            });

            Case("apply is idempotent — applying the same stage twice changes nothing", () =>
            {
                Fixture f = NewFixture();
                f.stages["TestLadder"] = 3;
                int first = f.Apply();
                string afterFirst = f.biome.description;
                int second = f.Apply();

                Eq(afterFirst, f.biome.description, "description after a repeat apply");
                True(first == second, $"applied count drifted: {first} then {second}");
            });

            // ── failure modes stay quiet and non-fatal ──────────────────────

            Case("a missing def warns once and does not throw", () =>
            {
                Fixture f = NewFixture();
                f.table.targets.Add(new LoreStageTarget
                {
                    defType = "ThingDef", defName = "TEST_NotPresent", field = "description",
                    stages = new List<LoreStageText> { new LoreStageText { stage = 1, text = "never" } },
                });

                f.stages["TestLadder"] = 1;
                f.Apply();
                f.Apply();

                int hits = 0;
                foreach (string w in f.warnings)
                {
                    if (w.Contains("TEST_NotPresent")) hits++;
                }

                True(hits == 1, $"expected exactly one warning about the missing def, got {hits}");
                Eq("BIOME@1", f.biome.description, "the rest of the table still applied");
            });

            Case("a field that is not a public string is skipped, not crashed on", () =>
            {
                Fixture f = NewFixture();
                f.table.targets.Add(new LoreStageTarget
                {
                    defType = "ThingDef", defName = "TEST_Item", field = "thisFieldDoesNotExist",
                    stages = new List<LoreStageText> { new LoreStageText { stage = 1, text = "never" } },
                });

                f.stages["TestLadder"] = 1;
                f.Apply();
                Eq("BIOME@1", f.biome.description, "the rest of the table still applied");
            });

            Case("an explicit stage-0 rung overrides the shipped baseline", () =>
            {
                Fixture f = NewFixture();
                f.table.targets[0].stages.Add(new LoreStageText { stage = 0, text = "BIOME@0" });

                f.stages["TestLadder"] = 0;
                f.Apply();
                Eq("BIOME@0", f.biome.description, "stage-0 override");

                f.stages["TestLadder"] = 1;
                f.Apply();
                Eq("BIOME@1", f.biome.description, "rung 1 still wins over the override");
            });

            Case("ladders advance independently", () =>
            {
                LoreStageApplier.ForgetBaselinesForTesting();

                var biome = new BiomeDef { defName = "A_Biome", description = "A-BASE" };
                ThingDef item = MakeThingDef("B_Item", "B-BASE");

                var ladderA = new RM_LoreStageTableDef
                {
                    defName = "LadderA", ladderId = "A", maxStage = 2,
                    targets = new List<LoreStageTarget>
                    {
                        new LoreStageTarget
                        {
                            defType = "BiomeDef", defName = "A_Biome", field = "description",
                            stages = new List<LoreStageText> { new LoreStageText { stage = 1, text = "A@1" } },
                        },
                    },
                };
                var ladderB = new RM_LoreStageTableDef
                {
                    defName = "LadderB", ladderId = "B", maxStage = 2,
                    targets = new List<LoreStageTarget>
                    {
                        new LoreStageTarget
                        {
                            defType = "ThingDef", defName = "B_Item", field = "description",
                            stages = new List<LoreStageText> { new LoreStageText { stage = 1, text = "B@1" } },
                        },
                    },
                };

                var stages = new Dictionary<string, int> { { "A", 1 }, { "B", 0 } };
                LoreStageApplier.ResetAndApply(
                    new[] { ladderA, ladderB },
                    id => stages.TryGetValue(id, out int s) ? s : 0,
                    (typeName, defName) =>
                        defName == "A_Biome" ? (Def)biome : defName == "B_Item" ? item : null,
                    _ => { });

                Eq("A@1", biome.description, "ladder A advanced");
                Eq("B-BASE", item.description, "ladder B untouched");
            });

            Case("ladderId falls back to defName when unset", () =>
            {
                var t = new RM_LoreStageTableDef { defName = "Fallback" };
                Eq("Fallback", t.LadderId, "LadderId");
            });

            Case("ConfigErrors flags a duplicate rung and an unreachable rung", () =>
            {
                var t = new RM_LoreStageTableDef
                {
                    defName = "Bad", ladderId = "Bad", maxStage = 2,
                    targets = new List<LoreStageTarget>
                    {
                        new LoreStageTarget
                        {
                            defType = "ThingDef", defName = "X", field = "description",
                            stages = new List<LoreStageText>
                            {
                                new LoreStageText { stage = 1, text = "a" },
                                new LoreStageText { stage = 1, text = "b" },
                                new LoreStageText { stage = 9, text = "c" },
                            },
                        },
                    },
                };

                bool dup = false, unreachable = false;
                foreach (string e in t.ConfigErrors())
                {
                    if (e.Contains("duplicate stage")) dup = true;
                    if (e.Contains("above maxStage")) unreachable = true;
                }

                True(dup, "duplicate rung not reported");
                True(unreachable, "unreachable rung not reported");
            });

            Console.WriteLine();
            Console.WriteLine($"{Pass.Count}/{Pass.Count + Fail.Count} passed");
            if (Fail.Count > 0)
            {
                Console.WriteLine();
                foreach (string f in Fail) Console.WriteLine("  FAILED " + f);
                return 1;
            }

            return 0;
        }
    }
}
