#!/usr/bin/env python3
"""modaudit/atlas_attribution.py - per-mod estimate of the StaticTextureAtlas pages a mod list bakes at load.

Used by memory_attribution.py (FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE); not run on its own.

Rules, read from the 1.6 decompile (D:\\ClaudeWork\\rimmandrake\\decomp\\rw16\\all\\Verse), not guessed:
  who inserts  ThingDef.PostLoad: a def with graphicData and drawerType != RealtimeOnly calls
               graphic.TryInsertIntoAtlas(category.ToAtlasGroup()) (Building/Plant/Item/Filth, else Misc), and again
               into Item when the group is Building and the def is minifiable. ScatterableDef inserts its
               texturePath into Terrain. Only Graphic_Single, Graphic_Multi, Graphic_Collection (and their vanilla
               subclasses) override TryInsertIntoAtlas; any other class (a mod's own) inserts nothing here.
  textures     Graphic_Single: texPath; Graphic_Multi: texPath_north/_east/_south/_west; Graphic_Collection: every
               texture under texPath/ whose name does not end _m. A mask joins when the shader has _MaskTex
               (approximated: shaderType name contains "Complex") and texPath_m / maskPath (Multi: <dir>m) exists.
  eligibility  GlobalTextureAtlasManager.TryInsertStatic: width < 512 and height < 512; one copy per
               (group, hasMask) key. The source texture stays loaded: an atlas page is EXTRA memory.
  pages        BakeStaticAtlases: per key, textures in insertion order fill a batch until the next one would pass
               MaxPixelsPerAtlas = (maxTextureSize/2)^2; each batch is one page sized by CalcRectsForAtlasNew
               (width NextPowerOfTwo(ceil(sqrt(px)) * 1.05) capped, height NextPowerOfTwo(ceil(px/width)), a shelf
               pack that doubles the height once, then halves texture size, on overflow). Colour page: RGBA32 with
               floor(log2(width/512)) + 1 mips, then FastCompressDXT to DXT5 (1 B/px) under Prefs
               textureCompression. Mask page: same size, 1 mip, compressed the same way.
  attribution  a page's bytes split by the pixel share of each texture in it, to the mod whose file wins the
               path (ContentFinder: the LAST active mod holding it). A path no loose mod file holds comes from
               resources.assets or a DLC bundle: counted as `vanilla_unsized`, packed at zero size (its pixels are
               not readable offline), so pages are a LOWER bound where vanilla shares them.
Assumed, not measured: maxTextureSize 16384 (MAX_TEX; any current desktop GPU); path matching is case-insensitive.
"""
import json
import math
import os

MAX_TEX = 16384
TILE_MAX = 512
GROUPS = {"Building": "Building", "Plant": "Plant", "Item": "Item", "Filth": "Filth"}
SINGLE = {"Graphic_ActivityMask", "Graphic_FadesInOut", "Graphic_Fleck", "Graphic_FleckPulse", "Graphic_FleckSplash",
          "Graphic_Gas", "Graphic_Mote", "Graphic_MoteWithAgeSecs", "Graphic_MoteWithParentRotation",
          "Graphic_PawnBodySilhouette", "Graphic_Single", "Graphic_Single_AgeSecs", "Graphic_Single_SquashNStretch",
          "Graphic_Terrain", "Graphic_Tiling", "Graphic_WithPropertyBlock"}
MULTI = {"Graphic_Multi", "Graphic_Multi_AgeSecs", "Graphic_Multi_BuildingWorking", "Graphic_Multi_Mote"}
COLLECTION = {"GraphicMote_RandomWithAgeSecs", "Graphic_ActivityMaskRandom", "Graphic_ActivityStaged",
              "Graphic_Cluster", "Graphic_ClusterTight", "Graphic_Collection", "Graphic_Flicker", "Graphic_Genepack",
              "Graphic_Indexed", "Graphic_Indexed_SquashNStretch", "Graphic_MealVariants", "Graphic_MoteRandom",
              "Graphic_Random", "Graphic_StackCount", "Graphic_WithPropertyBlockRandom"}
DIRS = ("_north", "_east", "_south", "_west")


def npot(x):
    return 1 << max(0, int(math.ceil(math.log2(max(1, x)))))


def page_size(dims, max_tex=MAX_TEX, divisor=1, taller=False):
    """(width, height) of one page holding dims [(w, h)], per StaticTextureAtlas.CalcRectsForAtlasNew. Pure."""
    dims = sorted(dims, key=lambda d: -d[1])
    px = sum(w * h for w, h in dims)
    w_ = min(npot(int(math.ceil(math.sqrt(px)) * 1.05)), max_tex)
    h_ = npot(int(math.ceil(px / float(w_))))
    if taller:
        h_ *= 2
    h_ = min(h_, max_tex)
    if divisor > 1:
        h_ //= divisor
        if h_ * w_ < (px // (divisor * divisor)) * 1.5:
            h_ *= divisor
    x = y = row = 0
    for w, h in dims:
        w, h = int(round(w / float(divisor))), int(round(h / float(divisor)))
        if x + w > w_:
            x, y, row = 0, y + row, 0
        if y + h > h_:
            if divisor == 1 and not taller and h_ < max_tex:
                return page_size(dims, max_tex, divisor, True)
            if divisor < 4:
                return page_size(dims, max_tex, divisor * 2)
            return w_, h_  # CalcRectsForAtlas (Unity PackTextures) fallback: same page budget
        x += w
        row = max(row, h)
    return w_, h_


def page_bytes(w, h, compression, mask):
    """Resident bytes of one colour (mips) or mask (1 mip) page after Bake. Pure."""
    bpp = 1 if compression else 4
    if mask:
        return w * h * bpp
    levels = max(1, int(math.floor(math.log2(w / float(TILE_MAX)))) + 1)
    return sum((w >> i) * (h >> i) * bpp for i in range(levels))


def def_textures(gclass, tex, mask_path, complex_shader, has):
    """[(color_key, mask_key_or_None)] one graphic inserts; None when its class inserts nothing. has(key) -> bool;
    under(prefix) is has.under."""
    short = (gclass or "").rsplit(".", 1)[-1]
    tex = (tex or "").strip("/").lower()
    mp = (mask_path or "").strip("/").lower() or None
    if not tex:
        return []
    if short in SINGLE:
        m = (mp or tex + "_m") if complex_shader else None
        return [(tex, m if m and has(m) else None)]
    if short in MULTI:
        out = []
        for d in DIRS:
            if has(tex + d):
                m = ((mp + d) if mp else (tex + d + "m")) if complex_shader else None
                out.append((tex + d, m if m and has(m) else None))
        return out
    if short in COLLECTION:
        out = []
        for k in has.under(tex + "/"):
            if k.endswith("_m") or any(k.endswith(d + "m") for d in DIRS):
                continue
            # a direction-named file joins a Graphic_Multi at <folder>/<prefix>, whose mask is <name>m; else <name>_m
            directional = any(d in k.rsplit("/", 1)[-1] for d in DIRS)
            m = (k + ("m" if directional else "_m")) if complex_shader else None
            out.append((k, m if m and has(m) else None))
        return out
    return None


class Holder(object):
    """Winning file per lower-cased path under Textures/: the last mod in list order holding it."""

    def __init__(self, ordered_recs):
        self.win = {}
        for pid, rec in ordered_recs:
            for k, wh in (rec.get("tex_dims") or {}).items():
                self.win[k] = (pid, wh[0], wh[1])
        self._kids = None

    def __call__(self, key):
        return key in self.win

    def under(self, prefix):
        if self._kids is None:
            self._kids = sorted(self.win)
        import bisect
        i = bisect.bisect_left(self._kids, prefix)
        out = []
        while i < len(self._kids) and self._kids[i].startswith(prefix):
            out.append(self._kids[i])
            i += 1
        return out


def slim_index(dump_dir, cache_dir):
    """[(group, minifiable, drawerType, graphicClass, texPath, maskPath, shaderType, packageId)] of ThingDefs, and
    [(texturePath, packageId)] of ScatterableDefs, from the def dump capture; cached by capture name (a dump is
    immutable once captured). packageId is the def's source mod, lowercased, so defs of mods the list dropped since
    the capture can be left out (dump_matches)."""
    cap = os.path.basename(os.path.normpath(dump_dir))
    cp = os.path.join(cache_dir, "atlas_index_v2_%s.json" % cap)
    if os.path.isfile(cp):
        try:
            return json.load(open(cp))
        except ValueError:
            pass
    things = []
    for d in json.load(open(os.path.join(dump_dir, "defs", "ThingDef.json")))["defs"]:
        f = d.get("fields") or {}
        g = f.get("graphicData")
        if not g:
            continue
        things.append([(d.get("is") or {}).get("category"), bool((d.get("is") or {}).get("minifiable")),
                       f.get("drawerType"), g.get("graphicClass"), g.get("texPath"), g.get("maskPath"),
                       g.get("shaderType"), (d.get("packageId") or "").lower()])
    scat = []
    sp = os.path.join(dump_dir, "defs", "ScatterableDef.json")
    if os.path.isfile(sp):
        scat = [[(d.get("fields") or {}).get("texturePath"), (d.get("packageId") or "").lower()]
                for d in json.load(open(sp))["defs"]]
    idx = {"things": things, "scatter": [s for s in scat if s[0]]}
    os.makedirs(cache_dir, exist_ok=True)
    with open(cp, "w") as fh:
        json.dump(idx, fh)
    return idx


# A dump may hold mods the list has dropped since its capture: their own defs are left out (estimate(drop=)), but
# their patches onto other mods' defs cannot be undone, so only a small drift is accepted as the same game.
MAX_DROPPED_FRACTION = 0.05


def _pid(p):
    """A def's packageId as dump_matches' norm sees it (lower case, no _steam suffix)."""
    p = (p or "").lower()
    return p[:-6] if p.endswith("_steam") else p


def dump_matches(dump_dir, ordered_norm, norm):
    """(ok, why, dropped). ok when every list mod is in the dump and the shared mods load in the list's order (a
    reordered list resolves defs and overrides differently, so a dump of another order describes another game).
    dropped = dump mods absent from the list (lowercased); their defs are to be excluded. A list mod missing from
    the dump, or more than MAX_DROPPED_FRACTION of the list dropped, is not ok."""
    try:
        m = json.load(open(os.path.join(dump_dir, "manifest.json")))
    except (OSError, ValueError):
        return False, "no readable manifest in %s" % dump_dir, set()
    dumped = [norm(x["packageId"]) for x in sorted(m.get("mods", []), key=lambda x: x.get("loadOrder", 0))]
    listed = set(ordered_norm)
    missing = [x for x in ordered_norm if x not in set(dumped)]
    if missing:
        return False, "dump %s lacks %d list mod(s), e.g. %s" % (m.get("capturedUtc"), len(missing),
                                                                  ", ".join(missing[:3])), set()
    dropped = [x for x in dumped if x not in listed]
    if len(dropped) > MAX_DROPPED_FRACTION * len(ordered_norm):
        return False, "dump has %d mods the list dropped (> %d%% of %d)" % (
            len(dropped), MAX_DROPPED_FRACTION * 100, len(ordered_norm)), set()
    shared = [x for x in dumped if x in listed]
    if shared != list(ordered_norm):
        i = next(i for i, (a, b) in enumerate(zip(shared, ordered_norm)) if a != b)
        return False, "dump and list load the shared mods in another order (first difference at #%d: %s vs %s)" % (
            i + 1, shared[i], ordered_norm[i]), set()
    why = "dump %s matches the list (%d mods)" % (m.get("capturedUtc"), len(shared))
    if dropped:
        why += "; %d dump mod(s) the list dropped are left out: %s" % (len(dropped), ", ".join(dropped))
    return True, why, {x.lower() for x in dropped}


def estimate(idx, ordered_recs, compression, max_tex=MAX_TEX, drop=()):
    """Bake the pages the engine would and split their bytes by mod. Returns a dict (see keys below).
    drop: lowercased packageIds whose defs are left out (mods the list dropped since the dump's capture)."""
    has = Holder(ordered_recs)
    queue, seen = {}, set()
    st = {"defs_inserting": 0, "defs_foreign_class": 0, "vanilla_unsized": 0, "too_big": 0, "foreign_classes": {},
          "defs_dropped": 0}

    def insert(group, ck, mk):
        key = (group, mk is not None)
        if (key, ck) in seen:
            return
        seen.add((key, ck))
        w = has.win.get(ck)
        if w is None:
            st["vanilla_unsized"] += 1
            return
        if w[1] >= TILE_MAX or w[2] >= TILE_MAX or w[1] <= 0 or w[2] <= 0:
            st["too_big"] += 1
            return
        queue.setdefault(key, []).append((ck, w[0], w[1], w[2]))

    drop = set(drop)
    for row in idx["things"]:
        cat, minif, drawer, gclass, tex, mpath, shader = row[:7]
        if drop and len(row) > 7 and _pid(row[7]) in drop:
            st["defs_dropped"] += 1
            continue
        if drawer == "RealtimeOnly":
            continue
        tx = def_textures(gclass, tex, mpath, "Complex" in (shader or ""), has)
        if tx is None:
            st["defs_foreign_class"] += 1
            c = (gclass or "?")
            st["foreign_classes"][c] = st["foreign_classes"].get(c, 0) + 1
            continue
        st["defs_inserting"] += 1
        group = GROUPS.get(cat, "Misc")
        for g in ([group, "Item"] if group == "Building" and minif else [group]):
            for ck, mk in tx:
                insert(g, ck, mk)
    for p in idx.get("scatter", []):
        if isinstance(p, list):
            if _pid(p[1]) in drop:
                st["defs_dropped"] += 1
                continue
            p = p[0]
        insert("Terrain", p.strip("/").lower(), None)

    budget = (max_tex // 2) ** 2
    by_mod, pages = {}, []
    for key, items in queue.items():
        batch, px = [], 0
        batches = []
        for it in items:
            n = it[2] * it[3]
            if batch and n + px > budget:
                batches.append(batch)
                batch, px = [], 0
            batch.append(it)
            px += n
        if batch:
            batches.append(batch)
        for b in batches:
            w, h = page_size([(i[2], i[3]) for i in b], max_tex)
            nbytes = page_bytes(w, h, compression, False) + (page_bytes(w, h, compression, True) if key[1] else 0)
            bpx = float(sum(i[2] * i[3] for i in b))
            pages.append({"group": key[0], "mask": key[1], "w": w, "h": h, "textures": len(b),
                          "mb": round(nbytes / 1048576.0, 2)})
            for _ck, pid, tw, th in b:
                by_mod[pid] = by_mod.get(pid, 0.0) + nbytes * (tw * th) / bpx / 1048576.0
    st["by_mod_mb"] = {k: round(v, 3) for k, v in by_mod.items()}
    st["pages"] = pages
    st["total_mb"] = round(sum(p["mb"] for p in pages), 2)
    st["textures"] = sum(p["textures"] for p in pages)
    st["foreign_classes"] = dict(sorted(st["foreign_classes"].items(), key=lambda kv: -kv[1])[:10])
    return st
