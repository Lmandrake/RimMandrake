// LIGHT_LEDGER_ONE_1 — the one place a light's radius is written. Every effect that brightens or dims
// a light registers a named modifier here; the radius is worked out once from all of them
// (LightLedgerKernel.Compute) and written to CompGlower.GlowRadius. Design and the migration record:
// design/RimMandrake/light_ledger_design.md.
//
// This file is compiled INTO each consuming mod (linked <Compile Include>), so it is internal and its
// state is NOT a static field of this class — each assembly has its own copy of the class. The state
// lives in one AppDomain data slot holding only vanilla/BCL types, so every copy shares one ledger.
// Changing the stored shape means bumping SlotKey and rebuilding every consumer together.
//
// Not saved, deliberately: vanilla does not save GlowRadius either. Each owner re-asserts its modifier
// from its own Scribed state on load (SpawnSetup, FinalizeInit, or its next pass).
using System;
using System.Collections.Generic;
using System.Text;
using Verse;

namespace RimMandrake.Shared
{
    internal static class LightLedger
    {
        private const string SlotKey = "RimMandrake.LightLedger/1";
        private const int PruneEvery = 256;

        private static Dictionary<CompGlower, Dictionary<string, float>> mods;
        private static Dictionary<CompGlower, Thing> carriers;
        private static int writes;

        private static object[] store;

        // One ledger per game: a new or loaded game starts empty (store[2] remembers which Game filled it),
        // so a light from the last game can never answer for this one.
        private static void EnsureStore()
        {
            if (store == null)
            {
                AppDomain d = AppDomain.CurrentDomain;
                store = d.GetData(SlotKey) as object[];
                if (store == null || store.Length != 3
                    || !(store[0] is Dictionary<CompGlower, Dictionary<string, float>>)
                    || !(store[1] is Dictionary<CompGlower, Thing>))
                {
                    store = new object[] { new Dictionary<CompGlower, Dictionary<string, float>>(), new Dictionary<CompGlower, Thing>(), null };
                    d.SetData(SlotKey, store);
                }
                mods = (Dictionary<CompGlower, Dictionary<string, float>>)store[0];
                carriers = (Dictionary<CompGlower, Thing>)store[1];
            }
            Game game = Current.Game;
            if (!ReferenceEquals(store[2], game))
            {
                mods.Clear();
                carriers.Clear();
                store[2] = game;
            }
        }

        private static Dictionary<string, float> For(CompGlower g, bool create)
        {
            EnsureStore();
            if (!mods.TryGetValue(g, out Dictionary<string, float> m) && create)
            {
                m = new Dictionary<string, float>();
                mods[g] = m;
            }
            return m;
        }

        // ── writers ───────────────────────────────────────────────────

        /// <summary>The light's own radius (default: the def's glowRadius). For lights an owner sizes itself: a culture stage, a well's age, a deepfire proxy.</summary>
        public static void SetBase(CompGlower g, float radius) { Write(g, LightLedgerKernel.Base, radius); }

        public static void ClearBase(CompGlower g) { Clear(g, LightLedgerKernel.Base); }

        /// <summary>Scales the light. 1 lets go.</summary>
        public static void SetMul(CompGlower g, string owner, float factor) { Write(g, LightLedgerKernel.Mul + owner, factor); }

        /// <summary>Takes cells of radius off after scaling. 0 lets go.</summary>
        public static void SetSub(CompGlower g, string owner, float cells) { Write(g, LightLedgerKernel.Sub + owner, cells); }

        /// <summary>Holds the light at or below a radius. Negative lets go.</summary>
        public static void SetCap(CompGlower g, string owner, float maxRadius) { Write(g, LightLedgerKernel.Cap + owner, maxRadius); }

        /// <summary>Removes one modifier by its FULL key ("mul:abyss.dark"), or the base.</summary>
        public static void Clear(CompGlower g, string fullKey)
        {
            if (g == null) return;
            Dictionary<string, float> m = For(g, false);
            if (m != null && m.Remove(fullKey)) Apply(g, m);
        }

        public static void ClearMul(CompGlower g, string owner) { Clear(g, LightLedgerKernel.Mul + owner); }
        public static void ClearSub(CompGlower g, string owner) { Clear(g, LightLedgerKernel.Sub + owner); }
        public static void ClearCap(CompGlower g, string owner) { Clear(g, LightLedgerKernel.Cap + owner); }

        private static void Write(CompGlower g, string key, float value)
        {
            if (g == null) return;
            Dictionary<string, float> m = For(g, true);
            LightLedgerKernel.Set(m, key, value);
            Apply(g, m);
            if (++writes % PruneEvery == 0) Prune();
        }

        /// <summary>Recompute and write. Re-registers with the glow grid only while the lamp is LIT: ForceRegister on an unlit lamp re-lights it.</summary>
        public static void Apply(CompGlower g)
        {
            if (g == null) return;
            Apply(g, For(g, false));
        }

        private static void Apply(CompGlower g, Dictionary<string, float> m)
        {
            float want = LightLedgerKernel.Compute(g.Props.glowRadius, m);
            if (!LightLedgerKernel.NeedsWrite(g.GlowRadius, want)) return;
            g.GlowRadius = want;
            ThingWithComps t = g.parent;
            if (t != null && t.Spawned && g.Glows) g.ForceRegister(t.Map);
        }

        // ── tags and carriers (cross-mod facts about a light) ─────────

        public static void Tag(CompGlower g, string tag)
        {
            if (g == null) return;
            For(g, true)[LightLedgerKernel.Tag + tag] = 1f;
        }

        public static bool HasTag(CompGlower g, string tag)
        {
            if (g == null) return false;
            Dictionary<string, float> m = For(g, false);
            return m != null && m.ContainsKey(LightLedgerKernel.Tag + tag);
        }

        /// <summary>The thing this light travels with (a glowing pawn's moving proxy). Null lets go.</summary>
        public static void SetCarrier(CompGlower g, Thing carrier)
        {
            if (g == null) return;
            EnsureStore();
            if (carrier == null) carriers.Remove(g);
            else carriers[g] = carrier;
        }

        /// <summary>True when any lit, spawned light names this thing as its carrier.</summary>
        public static bool CarriesLitLight(Thing carrier)
        {
            if (carrier == null) return false;
            EnsureStore();
            foreach (KeyValuePair<CompGlower, Thing> kv in carriers)
            {
                if (kv.Value != carrier) continue;
                CompGlower g = kv.Key;
                if (g.parent != null && g.parent.Spawned && g.Glows && g.GlowRadius > 0f) return true;
            }
            return false;
        }

        // ── readers ───────────────────────────────────────────────────

        /// <summary>The radius the ledger wants (equal to GlowRadius once applied).</summary>
        public static float Effective(CompGlower g)
        {
            if (g == null) return 0f;
            return LightLedgerKernel.Compute(g.Props.glowRadius, For(g, false));
        }

        /// <summary>The radius before subtractions and caps — what a grazer or sipper takes a share of.</summary>
        public static float Scaled(CompGlower g)
        {
            if (g == null) return 0f;
            return LightLedgerKernel.Scaled(g.Props.glowRadius, For(g, false));
        }

        public static float Get(CompGlower g, string fullKey, float fallback)
        {
            Dictionary<string, float> m = g == null ? null : For(g, false);
            return m != null && m.TryGetValue(fullKey, out float v) ? v : fallback;
        }

        /// <summary>One line for an inspect string or a debug action: "base 6 · mul:abyss.dark 0.4 → 2.4".</summary>
        public static string Describe(CompGlower g)
        {
            if (g == null) return "";
            Dictionary<string, float> m = For(g, false);
            var sb = new StringBuilder();
            sb.Append("def ").Append(g.Props.glowRadius.ToString("0.##"));
            if (m != null)
            {
                foreach (KeyValuePair<string, float> kv in m) sb.Append(" · ").Append(kv.Key).Append(' ').Append(kv.Value.ToString("0.##"));
            }
            sb.Append(" → ").Append(Effective(g).ToString("0.##"));
            return sb.ToString();
        }

        private static void Prune()
        {
            var dead = new List<CompGlower>();
            foreach (CompGlower g in mods.Keys) if (g.parent == null || g.parent.Destroyed) dead.Add(g);
            foreach (CompGlower g in carriers.Keys) if (g.parent == null || g.parent.Destroyed) dead.Add(g);
            for (int i = 0; i < dead.Count; i++) { mods.Remove(dead[i]); carriers.Remove(dead[i]); }
        }
    }
}
