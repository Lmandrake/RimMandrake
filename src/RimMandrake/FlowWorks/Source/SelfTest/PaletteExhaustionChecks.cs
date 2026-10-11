// FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO (FlowWorks P7, GPT G3.6): a full 254-entry fluid palette returned key 0, the
// writer still filled the cell, and SyncFluidIdentity then stamped that "unrecorded" wet cell as the map's ActiveFluid —
// the liquid silently changed identity. The production rule (RM_ExcavationSanityMath.AllocateKey) now compacts in the
// running session and answers 0 only when every key is in use, and the kernel asks CanClaim BEFORE it debits.
// Each case carries a can-fail: the old rule computed beside it gives the wrong answer the finding described.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static partial class Program
    {
        private sealed class PFl { public string name; public override string ToString() => name; }

        // The pre-fix PaletteKey, verbatim in shape: full -> 0, no compaction.
        private static byte OldPaletteKey(List<PFl> palette, PFl fluid)
        {
            if (fluid == null) return 0;
            int i = palette.IndexOf(fluid);
            if (i < 0) { if (palette.Count >= 254) return 0; palette.Add(fluid); i = palette.Count - 1; }
            return (byte)(i + 1);
        }

        private static List<PFl> FullPalette(out PFl[] defs)
        {
            defs = new PFl[254];
            var p = new List<PFl>();
            for (int i = 0; i < 254; i++) { defs[i] = new PFl { name = "f" + i }; p.Add(defs[i]); }
            return p;
        }

        private static void RunPaletteExhaustion()
        {
            Case("P7_full_palette_compacts_in_session_and_keeps_every_identity", () =>
            {
                var palette = FullPalette(out PFl[] defs);
                // cells reference keys 3, 100 and 254 only; the other 251 entries are drained-away liquids
                byte[] grid = { 0, 3, 100, 254, 3, 0 };
                var before = new PFl[grid.Length];
                for (int i = 0; i < grid.Length; i++) before[i] = grid[i] == 0 ? null : palette[grid[i] - 1];
                var fresh = new PFl { name = "new" };
                byte key = RM_ExcavationSanityMath.AllocateKey(palette, grid, fresh, RM_ExcavationSanityMath.MaxPaletteKeys, out int dropped);
                Assert(key != 0 && palette[key - 1] == fresh, "the new liquid gets a real key (got " + key + ")");
                Assert(dropped == 251 && palette.Count == 4, "251 unused entries compacted, 3 kept + 1 new (dropped " + dropped + ", count " + palette.Count + ")");
                for (int i = 0; i < grid.Length; i++)
                {
                    PFl now = grid[i] == 0 ? null : palette[grid[i] - 1];
                    Assert(now == before[i], "cell " + i + " keeps its liquid across the remap (" + before[i] + " -> " + now + ")");
                }
                // can-fail: the old rule hands out key 0 for the same request
                var old = FullPalette(out _);
                Assert(OldPaletteKey(old, fresh) == 0, "can-fail: the old rule returns key 0 on a full palette");
            });

            Case("P7_every_key_in_use_refuses_without_touching_palette_or_grid", () =>
            {
                var palette = FullPalette(out PFl[] defs);
                byte[] grid = new byte[254];
                for (int i = 0; i < 254; i++) grid[i] = (byte)(i + 1);
                byte[] gridBefore = (byte[])grid.Clone();
                var fresh = new PFl { name = "new" };
                byte key = RM_ExcavationSanityMath.AllocateKey(palette, grid, fresh, RM_ExcavationSanityMath.MaxPaletteKeys, out int dropped);
                Assert(key == 0 && dropped == 0 && palette.Count == 254 && !palette.Contains(fresh), "no free key: refused, palette untouched");
                bool same = true; for (int i = 0; i < grid.Length; i++) same &= grid[i] == gridBefore[i];
                Assert(same, "grid untouched on refusal");
                // an existing liquid still gets its key on a full palette
                Assert(RM_ExcavationSanityMath.AllocateKey(palette, grid, defs[200], 254, out _) == 201, "a known liquid keeps key 201");
                Assert(RM_ExcavationSanityMath.AllocateKey(palette, grid, (PFl)null, 254, out _) == 0, "null fluid is key 0");
                // can-fail: under the old writer a refused key still filled the cell, and the identity sync read key 0
                // on a wet cell as "unrecorded" and stamped ActiveFluid -> the new liquid became defs[0] (the map default)
                byte oldKey = OldPaletteKey(FullPalette(out PFl[] d2), fresh);
                PFl active = d2[0];
                PFl afterSync = oldKey == 0 ? active : null;
                Assert(afterSync != null && afterSync != fresh, "can-fail: old path converts '" + fresh + "' into '" + afterSync + "'");
            });

            Case("P7_kernel_refuses_a_dry_claim_before_debiting_the_source", () =>
            {
                // 3x1: a limited tar body at 0, a dug dry cell at 1 (depth 2), a dug dry cell at 2
                (ArrayWorld w, List<int> digs, ArrayWorld.Body b) Scene()
                {
                    var aw = new ArrayWorld(3, 1);
                    aw.natural[0] = true; aw.terrainFluid[0] = ArrayWorld.Tar;
                    aw.k.depth[1] = 2; aw.k.depth[2] = 2;
                    var body = aw.BodyAt(0, 1f, false);
                    return (aw, new List<int> { 1, 2 }, body);
                }
                var (w, d, body) = Scene();
                w.canClaim = f => f != ArrayWorld.Tar;   // no key free for tar
                float stock0 = body.stock;
                for (int p = 0; p < 20; p++) w.Pulse(d);
                Assert(w.k.fill[1] == 0 && w.k.fill[2] == 0 && w.cellFluid[1] == null, "no key: the dry cells stay dry and unrecorded");
                Assert(body.stock == stock0, "no key: the tar body is not debited (" + stock0 + " -> " + body.stock + ")");
                // can-fail: the same scene with keys available fills the channel and debits the body
                var (w2, d2, body2) = Scene();
                for (int p = 0; p < 20; p++) w2.Pulse(d2);
                Assert(w2.k.fill[1] > 0 && w2.cellFluid[1] == ArrayWorld.Tar && body2.stock < stock0,
                       "can-fail: with a key the scene does move tar (fill " + w2.k.fill[1] + ", stock " + body2.stock + ")");
            });
        }
    }
}
