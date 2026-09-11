using System;
using System.Collections.Generic;
using System.Reflection;
using Verse;

namespace RimMandrake.LoreStages
{
    // The whole mechanism, in one place and with no live-Game dependency, so
    // SelfTest/Program.cs can exercise the real code offline rather than a
    // reimplementation of it.
    //
    // ── Why def mutation and not Harmony ─────────────────────────────────────
    // Every display surface this feature targets reads a def FIELD at draw time
    // (feasibility trace, design/Jawa/worldbuilding/research/
    // staged_lore_descriptions_feasibility_2026-09-09.md): the world tile
    // inspector reads `selTile.PrimaryBiome.description` directly
    // (WITab_Terrain.cs:62), `Thing.DescriptionFlavor => def.description` is a
    // virtual with no backing store (Thing.cs:586), the settle confirmation
    // re-reads `BiomeDef.settleWarning` every time
    // (SettlementProximityGoodwillUtility.cs:140). A field write shows on the
    // next frame. The biome path in particular has no getter to postfix, so
    // Harmony would need a transpiler to reach what a field write reaches for
    // free. Ludeon ships this same idea in the base game:
    // Building_VoidMonolith.cs:92-102 stages its description by campaign level.
    //
    // ── The two caches that make it non-trivial ──────────────────────────────
    // 🔴 Two private memoized fields outlive a stage change and are cleared by
    // NO engine path, because neither type overrides Def.ClearCachedData (only
    // RoadDef and BodyDef do, and Def.ClearCachedData clears only
    // cachedLabelCap anyway):
    //
    //   ThingDef.descriptionDetailedCached  (Verse/ThingDef.cs:414, filled :794-821)
    //   HediffDef.descriptionCached         (Verse/HediffDef.cs:193, filled :245-261)
    //
    // Skip either and the trade/transfer rows, the storage-filter tree, the
    // outfit-stand and book tabs, the quest-part item lists and every hediff
    // tooltip keep serving the PREVIOUS stage's text for the rest of the
    // process, while the biome inspector next to them shows the new one.
    // Reflection is the only invalidation route; there is no public API and no
    // override point. That is why ClearStaleCaches below is loud when the
    // fields cannot be found: a silently-skipped cache clear looks exactly like
    // a working feature until someone opens a trade window.
    //
    // ── Why reset-to-baseline on every load, not "advance one stage" ─────────
    // 🔴 Defs are process-global and are NOT reloaded between savegames.
    // PlayDataLoader.LoadAllPlayData is called from exactly two places in the
    // engine — Root.cs:75 (process start) and LanguageDatabase.cs:34-35
    // (language change). Loading a save does not touch the def database. So a
    // mutation made while playing a stage-5 colony is STILL ON THE DEF when the
    // player returns to the menu and loads a stage-0 save, or starts a new one.
    // ResetAndApply therefore always restores every known baseline first and
    // then applies the current stage from scratch: idempotent, order-free, and
    // correct when the stage goes DOWN as well as up.
    public static class LoreStageApplier
    {
        // Resolve (defType name, defName) -> Def, or null when the def is not
        // present. Injected rather than hardcoded so the offline selftest can
        // hand in real Def instances it constructed itself; production passes
        // LoreStageDefDatabase.Resolve.
        public delegate Def DefResolver(string defTypeName, string defName);

        private sealed class Baseline
        {
            public Def def;
            public FieldInfo field;
            public string pristine;
        }

        // key -> the pristine value captured the FIRST time this mechanism ever
        // touched that field in this process. Process-lifetime by design: it is
        // the only surviving record of the shipped text once a def has been
        // rewritten, and the def database is not reloaded between saves.
        private static readonly Dictionary<string, Baseline> Baselines =
            new Dictionary<string, Baseline>();

        private static readonly HashSet<string> WarnedKeys = new HashSet<string>();

        private static readonly FieldInfo ThingDefDetailedCache = typeof(ThingDef)
            .GetField("descriptionDetailedCached", BindingFlags.NonPublic | BindingFlags.Instance);

        private static readonly FieldInfo HediffDefDescriptionCache = typeof(HediffDef)
            .GetField("descriptionCached", BindingFlags.NonPublic | BindingFlags.Instance);

        // True when both private cache fields were found by name. False means
        // the engine renamed one and every staged ThingDef/HediffDef will serve
        // stale text in the cached UI paths — callers must SHOUT, not shrug.
        public static bool CachesReachable => ThingDefDetailedCache != null && HediffDefDescriptionCache != null;

        public static string CacheReachabilityReport =>
            "ThingDef.descriptionDetailedCached=" + (ThingDefDetailedCache != null ? "found" : "MISSING") +
            ", HediffDef.descriptionCached=" + (HediffDefDescriptionCache != null ? "found" : "MISSING");

        // Reset every field this mechanism has ever written back to its shipped
        // value, then apply each ladder's current stage. Returns the number of
        // fields left holding non-baseline text — a caller logging 0 where it
        // expected more has found a broken table, not a quiet success.
        //
        // stageOf: ladderId -> current stage (0 = nothing revealed yet).
        // warn:    one line per problem; deduplicated by this class.
        public static int ResetAndApply(
            IEnumerable<RM_LoreStageTableDef> tables,
            Func<string, int> stageOf,
            DefResolver resolve,
            Action<string> warn)
        {
            if (tables == null) throw new ArgumentNullException(nameof(tables));
            if (stageOf == null) throw new ArgumentNullException(nameof(stageOf));
            if (resolve == null) throw new ArgumentNullException(nameof(resolve));
            warn = warn ?? (_ => { });

            var touched = new HashSet<Def>();

            // Pass 1 — everything back to shipped text. Unconditional: this is
            // what stops a stage-5 colony's text leaking into a stage-0 one
            // within the same process.
            foreach (Baseline b in Baselines.Values)
            {
                b.field.SetValue(b.def, b.pristine);
                touched.Add(b.def);
            }

            int applied = 0;

            // Pass 2 — apply the current rung of each ladder.
            foreach (RM_LoreStageTableDef table in tables)
            {
                if (table?.targets == null) continue;

                int stage = stageOf(table.LadderId);

                foreach (LoreStageTarget target in table.targets)
                {
                    if (target == null) continue;

                    if (target.defType.NullOrEmpty() || target.defName.NullOrEmpty() || target.field.NullOrEmpty())
                    {
                        WarnOnce(warn, table.defName + ":incomplete-target",
                            $"[LoreStages] {table.defName}: a target is missing defType/defName/field; skipped.");
                        continue;
                    }

                    Def def = resolve(target.defType, target.defName);
                    if (def == null)
                    {
                        // Not an error: a ladder may name defs from a mod the
                        // player does not have. Once, then quiet.
                        WarnOnce(warn, table.defName + ":missing:" + target.defType + ":" + target.defName,
                            $"[LoreStages] {table.defName}: no {target.defType} named {target.defName}; that rung will never show.");
                        continue;
                    }

                    FieldInfo fi = def.GetType().GetField(target.field, BindingFlags.Public | BindingFlags.Instance);
                    if (fi == null || fi.FieldType != typeof(string))
                    {
                        WarnOnce(warn, table.defName + ":field:" + target.defType + ":" + target.field,
                            $"[LoreStages] {table.defName}: {target.defType} has no public string field '{target.field}'; skipped.");
                        continue;
                    }

                    string key = def.GetType().FullName + "|" + target.defName + "|" + target.field;
                    if (!Baselines.TryGetValue(key, out Baseline baseline))
                    {
                        // First touch in this process: whatever is on the def
                        // right now IS the shipped value, because pass 1 above
                        // has already restored every field we have ever written
                        // and this one is not among them.
                        baseline = new Baseline
                        {
                            def = def,
                            field = fi,
                            pristine = (string)fi.GetValue(def),
                        };
                        Baselines[key] = baseline;
                    }

                    string value = baseline.pristine;
                    int best = int.MinValue;
                    if (target.stages != null)
                    {
                        foreach (LoreStageText rung in target.stages)
                        {
                            if (rung?.text == null) continue;
                            // Highest rung at or below the current stage wins.
                            // An explicit stage-0 rung therefore overrides the
                            // snapshotted baseline, which is the authoring
                            // escape hatch for "shipped text is not rung zero".
                            if (rung.stage <= stage && rung.stage > best)
                            {
                                best = rung.stage;
                                value = rung.text;
                            }
                        }
                    }

                    fi.SetValue(def, value);
                    touched.Add(def);
                    if (best != int.MinValue) applied++;
                }
            }

            // Pass 3 — the reason this class exists.
            foreach (Def def in touched)
            {
                ClearStaleCaches(def);
            }

            return applied;
        }

        // Null the two private memoized description fields on a def whose text
        // we just rewrote. Safe to call on any Def: a def that is neither a
        // ThingDef nor a HediffDef has neither cache.
        //
        // Def.ClearCachedData() is called too, for cachedLabelCap — it matters
        // only when a ladder stages `label`, and it is cheap enough not to
        // branch on. (RoadDef/BodyDef override it with real work; neither is a
        // plausible staged-text target, and both overrides are idempotent.)
        public static void ClearStaleCaches(Def def)
        {
            if (def == null) return;

            if (def is ThingDef && ThingDefDetailedCache != null)
            {
                ThingDefDetailedCache.SetValue(def, null);
            }

            if (def is HediffDef && HediffDefDescriptionCache != null)
            {
                HediffDefDescriptionCache.SetValue(def, null);
            }

            def.ClearCachedData();
        }

        private static void WarnOnce(Action<string> warn, string key, string message)
        {
            if (WarnedKeys.Add(key))
            {
                warn(message);
            }
        }

        // Test-only. Production never calls this: dropping the baselines after a
        // def has been mutated would make the shipped text unrecoverable for the
        // rest of the process.
        internal static void ForgetBaselinesForTesting()
        {
            Baselines.Clear();
            WarnedKeys.Clear();
        }
    }
}
