// JawaBenchTextureMemoryTools.cs - what the textures the RUNNING game holds really cost, per mod.
// Item HEAVY_TEXTURES_MEASURE_REAL_VRAM (owner card C18, design/RimMandrake/mod_audit/OWNER_RULINGS.md: "Measure real
// memory cost first"). Reader: src/RimMandrake/Utils/heavy_textures_vram.py.
//
// WHY A RUNTIME READ: the offline figures come from image headers and the loader rule, and both miss what only the
// running game knows: the format Unity actually chose, the mips it kept, whether a CPU copy stayed (isReadable),
// AssetBundle textures (loaded lazily by ContentFinder, never in a mod's contentList), and textures a mod's own code
// creates (render targets, LUTs).
//
// HOW EACH TEXTURE IS SIZED: Resources.FindObjectsOfTypeAll<Texture>() is every Texture object in memory. Its GPU
// bytes are computed from the live object: graphicsFormat, width, height, mipmapCount, layers (cube 6, array/3D depth),
// via GraphicsFormatUtility.ComputeMipmapSize; a RenderTexture adds antiAliasing samples and its depth-stencil format,
// and counts 0 while !IsCreated() (no GPU allocation yet). A readable Texture2D keeps a CPU copy of the same size:
// cpuBytes. Profiler.GetRuntimeMemorySizeLong is the second instrument; a release player may read 0 for every object,
// so a zero total is reported as null (UNKNOWN), never as zero memory.
//
// WHO OWNS IT (attribution, in order):
//   content   the texture is a value of a running mod's GetContentHolder<Texture2D>().contentList (loose files)
//   bundle    its name matches, case-insensitively, the file stem of an asset in exactly ONE running mod's loaded
//             AssetBundles (GetAllAssetNames: a listing, it loads nothing); two or more mods -> "ambiguous". An UPPER
//             bound: any other loaded texture that happens to share the stem is counted to that mod too (the reader
//             prints fromBundle per mod, and each mod's top[] names what was counted)
//   atlas     a GlobalTextureAtlasManager page (name starts TextureAtlas_ or Mask_TextureAtlas_)
//   other     anything else: vanilla Resources, DLC bundles, a mod's runtime-created textures. The `other` rows carry
//             names so a mod's own render target (Planet Atmosphere's LUTs) can be read off by name.
//
// COST: one FindObjectsOfTypeAll and one asset-name listing per bundle, on the main thread, only when called. It is a
// read tool, not a recorder; it adds nothing to play while uncalled.
//
// ENGINE MEMBERS read from decompiled 1.6 (D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse, 2026-11-03):
//   ModContentHolder<T>.contentList: public Dictionary<string, T>; ModContentPack.GetContentHolder<T>()
//   ModContentPack.assetBundles.loadedAssetBundles: List<AssetBundle> (ContentFinder.Get falls back to LoadAsset on it)
//   StaticTextureAtlas: colorTexture.name = "TextureAtlas_" + groupKey + "_" + id; mask "Mask_" + that name

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private sealed class TexRow
        {
            public string name, kind, format, how, mod;
            public int w, h, mips, layers;
            public long gpu, cpu, profiler;
            public bool readable;
        }

        private sealed class ModTally
        {
            public int count, readable;
            public long gpu, cpu, profiler;
            public readonly List<TexRow> rows = new List<TexRow>();
        }

        internal static long TexMipChainBytes(int w, int h, int d, int mips, GraphicsFormat f, bool is3D)
        {
            long total = 0;
            for (int m = 0; m < Math.Max(1, mips); m++)
            {
                int mw = Math.Max(1, w >> m), mh = Math.Max(1, h >> m), md = is3D ? Math.Max(1, d >> m) : 1;
                total += (long)GraphicsFormatUtility.ComputeMipmapSize(mw, mh, md, f);
            }
            return total;
        }

        private static TexRow MeasureTexture(Texture t)
        {
            var r = new TexRow { name = t.name ?? "", kind = t.GetType().Name, w = t.width, h = t.height, layers = 1 };
            GraphicsFormat f = t.graphicsFormat;
            r.format = f.ToString();
            r.mips = Math.Max(1, t.mipmapCount);
            bool is3D = t.dimension == UnityEngine.Rendering.TextureDimension.Tex3D;
            int depth = 1;
            switch (t.dimension)
            {
                case UnityEngine.Rendering.TextureDimension.Cube: r.layers = 6; break;
                case UnityEngine.Rendering.TextureDimension.CubeArray:
                    r.layers = 6 * Math.Max(1, (t as CubemapArray)?.cubemapCount ?? (t as RenderTexture)?.volumeDepth ?? 1); break;
                case UnityEngine.Rendering.TextureDimension.Tex2DArray:
                    r.layers = Math.Max(1, (t as Texture2DArray)?.depth ?? (t as RenderTexture)?.volumeDepth ?? 1); break;
                case UnityEngine.Rendering.TextureDimension.Tex3D:
                    depth = Math.Max(1, (t as Texture3D)?.depth ?? (t as RenderTexture)?.volumeDepth ?? 1); r.layers = depth; break;
            }
            var rt = t as RenderTexture;
            if (rt != null)
            {
                if (!rt.IsCreated()) { r.how = "rt-not-created"; return r; }
                long colour = f == GraphicsFormat.None ? 0 : TexMipChainBytes(r.w, r.h, depth, r.mips, f, is3D) * (is3D ? 1 : r.layers);
                long ds = 0;
                if (rt.depthStencilFormat != GraphicsFormat.None)
                    ds = (long)GraphicsFormatUtility.ComputeMipmapSize(r.w, r.h, rt.depthStencilFormat) * (is3D ? depth : r.layers);
                r.gpu = (colour + ds) * Math.Max(1, rt.antiAliasing);
                r.how = "rt";
            }
            else if (f == GraphicsFormat.None)
            {
                r.how = "no-format";
            }
            else
            {
                r.gpu = TexMipChainBytes(r.w, r.h, depth, r.mips, f, is3D) * (is3D ? 1 : r.layers);
                r.readable = t.isReadable;
                if (r.readable) r.cpu = r.gpu;
                r.how = "tex";
            }
            try { r.profiler = UnityEngine.Profiling.Profiler.GetRuntimeMemorySizeLong(t); } catch { r.profiler = 0; }
            return r;
        }

        [Tool(
            "jawa/texture_memory",
            Description =
                "Real memory of every Texture the running game holds, attributed to mods: GPU bytes computed from each " +
                "live object's format, size, mips and layers; a readable texture's CPU copy; Unity's per-object " +
                "profiler figure (null = UNKNOWN when a release player reads 0 for all). Owner: a mod's loose-file " +
                "contentList, else a name match to ONE mod's loaded AssetBundle assets, else an atlas page, else other " +
                "(vanilla, DLC, runtime-made). Read only; works at the main menu. A bundle texture not yet asked for " +
                "by ContentFinder is not loaded and costs nothing: it is listed as bundleAssets, not measured.",
            ResultDescription =
                "success, textures (objects seen), totals {gpuBytes, cpuBytes, profilerBytes|null}, buckets " +
                "{content,bundle,atlas,ambiguous,other}, mods[] {packageId, name, count, gpuBytes, cpuBytes, " +
                "profilerBytes|null, readable, bundleAssets, top[]} for the mods asked for (or the top N by GPU bytes), " +
                "other[] largest unowned textures by name, processHealth (private/working set/Unity/mono MB as JSON).")]
        public static async Task<object> TextureMemory(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated packageIds to report in full (case-insensitive). Empty = the top `limit` mods by GPU bytes.")] string packageIds = null,
            [ToolParameter(Description = "Mods reported when packageIds is empty; also the size of each top[] and of other[]. Default 25.")] int limit = 25)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                limit = Math.Max(1, Math.Min(limit, 500));
                var want = new HashSet<string>((packageIds ?? "").Split(',').Select(s => s.Trim().ToLowerInvariant()).Where(s => s.Length > 0));

                var ownerById = new Dictionary<int, ModContentPack>();
                var stemOwners = new Dictionary<string, HashSet<ModContentPack>>(StringComparer.OrdinalIgnoreCase);
                var bundleAssets = new Dictionary<ModContentPack, int>();
                var listErrors = new List<string>();
                foreach (ModContentPack mod in LoadedModManager.RunningModsListForReading)
                {
                    try
                    {
                        foreach (Texture2D tex in mod.GetContentHolder<Texture2D>().contentList.Values)
                            if (tex != null && !ownerById.ContainsKey(tex.GetInstanceID())) ownerById[tex.GetInstanceID()] = mod;
                    }
                    catch (Exception e) { listErrors.Add(mod.PackageId + " contentList: " + e.GetType().Name); }
                    try
                    {
                        var bundles = mod.assetBundles?.loadedAssetBundles;
                        if (bundles == null) continue;
                        int n = 0;
                        foreach (AssetBundle b in bundles)
                        {
                            if (b == null) continue;
                            foreach (string a in b.GetAllAssetNames())
                            {
                                n++;
                                string stem = Path.GetFileNameWithoutExtension(a);
                                if (!stemOwners.TryGetValue(stem, out var set)) stemOwners[stem] = set = new HashSet<ModContentPack>();
                                set.Add(mod);
                            }
                        }
                        bundleAssets[mod] = n;
                    }
                    catch (Exception e) { listErrors.Add(mod.PackageId + " bundles: " + e.GetType().Name); }
                }

                var tally = new Dictionary<ModContentPack, ModTally>();
                var bucketGpu = new Dictionary<string, long> { ["content"] = 0, ["bundle"] = 0, ["atlas"] = 0, ["ambiguous"] = 0, ["other"] = 0 };
                var others = new List<TexRow>();
                long totGpu = 0, totCpu = 0, totProf = 0;
                int seen = 0, measureErrors = 0;
                foreach (Texture t in Resources.FindObjectsOfTypeAll<Texture>())
                {
                    if (t == null) continue;
                    TexRow r;
                    try { r = MeasureTexture(t); }
                    catch (Exception) { measureErrors++; continue; }
                    seen++;
                    totGpu += r.gpu; totCpu += r.cpu; totProf += r.profiler;
                    ModContentPack owner = null;
                    string bucket;
                    if (ownerById.TryGetValue(t.GetInstanceID(), out owner)) bucket = "content";
                    else if (stemOwners.TryGetValue(r.name, out var set) && set.Count == 1) { owner = set.First(); bucket = "bundle"; }
                    else if (set != null && set.Count > 1) bucket = "ambiguous";
                    else if (r.name.StartsWith("TextureAtlas_", StringComparison.Ordinal) || r.name.StartsWith("Mask_TextureAtlas_", StringComparison.Ordinal)) bucket = "atlas";
                    else bucket = "other";
                    bucketGpu[bucket] += r.gpu;
                    if (owner == null)
                    {
                        if (bucket == "other" || bucket == "ambiguous") { r.mod = bucket; others.Add(r); }
                        continue;
                    }
                    r.mod = bucket;
                    if (!tally.TryGetValue(owner, out var mt)) tally[owner] = mt = new ModTally();
                    mt.count++; mt.gpu += r.gpu; mt.cpu += r.cpu; mt.profiler += r.profiler;
                    if (r.readable) mt.readable++;
                    mt.rows.Add(r);
                }

                bool profilerBlind = totProf == 0;
                Func<TexRow, object> rowObj = r => new
                {
                    name = r.name, kind = r.kind, w = r.w, h = r.h, mips = r.mips, layers = r.layers, format = r.format,
                    gpuBytes = r.gpu, cpuBytes = r.cpu, profilerBytes = profilerBlind ? (long?)null : r.profiler,
                    readable = r.readable, how = r.how, owner = r.mod
                };

                var running = LoadedModManager.RunningModsListForReading;
                IEnumerable<ModContentPack> pick = want.Count > 0
                    ? running.Where(m => want.Contains((m.PackageId ?? "").ToLowerInvariant()) || want.Contains((m.PackageIdPlayerFacing ?? "").ToLowerInvariant()))
                    : tally.OrderByDescending(kv => kv.Value.gpu).Take(limit).Select(kv => kv.Key);
                var mods = new List<object>();
                foreach (ModContentPack m in pick)
                {
                    tally.TryGetValue(m, out var mt);
                    mt = mt ?? new ModTally();
                    bundleAssets.TryGetValue(m, out int ba);
                    mods.Add(new
                    {
                        packageId = (m.PackageIdPlayerFacing ?? m.PackageId ?? "").ToLowerInvariant(), name = m.Name,
                        count = mt.count, gpuBytes = mt.gpu, cpuBytes = mt.cpu,
                        profilerBytes = profilerBlind ? (long?)null : mt.profiler,
                        readable = mt.readable, bundleAssets = ba,
                        fromContent = mt.rows.Count(r => r.mod == "content"), fromBundle = mt.rows.Count(r => r.mod == "bundle"),
                        top = mt.rows.OrderByDescending(r => r.gpu).Take(limit).Select(rowObj).ToList()
                    });
                }
                var runningIds = new HashSet<string>(running.Select(m => (m.PackageIdPlayerFacing ?? m.PackageId ?? "").ToLowerInvariant()));
                var missing = want.Where(p => !runningIds.Contains(p) && !running.Any(m => (m.PackageId ?? "").ToLowerInvariant() == p)).OrderBy(p => p).ToList();

                string health;
                try { string f = JawaBenchSessionHealth.Fields(); health = "{" + (f.StartsWith(",") ? f.Substring(1) : f) + "}"; }
                catch (Exception e) { health = null; listErrors.Add("processHealth: " + e.GetType().Name); }

                return (object)new
                {
                    success = true,
                    programState = Current.ProgramState.ToString(),
                    upS = Time.realtimeSinceStartup,
                    textures = seen, measureErrors,
                    totals = new { gpuBytes = totGpu, cpuBytes = totCpu, profilerBytes = profilerBlind ? (long?)null : totProf },
                    buckets = bucketGpu,
                    mods, missing,
                    other = others.OrderByDescending(r => r.gpu).Take(limit).Select(rowObj).ToList(),
                    textureCompression = Prefs.TextureCompression,
                    graphicsMemoryMB = SystemInfo.graphicsMemorySize,
                    processHealth = health,
                    errors = listErrors.Take(50).ToList(),
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
