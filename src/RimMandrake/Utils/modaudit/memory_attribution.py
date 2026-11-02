#!/usr/bin/env python3
"""modaudit/memory_attribution.py - per-mod estimate of the native memory a mod list's loose content costs. Resumable.

    python3 src/RimMandrake/Utils/modaudit/memory_attribution.py --budget 400   # walk mods until 400 s spent; re-run
    python3 src/RimMandrake/Utils/modaudit/memory_attribution.py --check        # exit 0 only when every resolved mod
                                                                                # of the list is attributed; writes
                                                                                # the report
    python3 src/RimMandrake/Utils/modaudit/memory_attribution.py --reconcile    # (Windows game up) also read the
                                                                                # game's private bytes beside it

Why: the 550-mod list held 30.6 GB private with ~5 GB managed heap (FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE). This
says which mods the ~25 GB native share most plausibly belongs to. Every number here is an ESTIMATE from files on
disk under the engine's own load rules; only --reconcile touches a measurement, and it measures the whole process.

Load rules, read from the 1.6 decompile (D:\\ClaudeWork\\rimmandrake\\decomp\\rw16\\all\\Verse), not guessed:
  folders    ModContentPack.InitLoadFolders: LoadFolders.xml <v1.6> (else the highest defined version <= 1.6, else
             <default>), each <li> kept when its IfModActive / IfModActiveAll / IfModNotActive hold against the list;
             with no LoadFolders: <root>/1.6 (or the best version folder), <root>/Common, <root>.
  files      ModContentPack.GetAllFilesForMod: one file per path relative to its load folder, the first folder in
             descending order wins (an override replaces, it does not add).
  textures   ModContentLoader: .png/.jpg/.jpeg/.psd/.dds under Textures/; a .png with a same-named .dds is skipped.
             PNG etc. are decoded to RGBA32, Apply(updateMipmaps, makeNoLongerReadable) frees the CPU copy, then with
             Prefs textureCompression and width%4==0 and height%4==0, StaticTextureAtlas.FastCompressDXT makes
             GraphicsFormat 101 (RGBA_DXT5_UNorm, 1 byte/px); otherwise it stays RGBA32 (4 bytes/px). Mips x 4/3.
             DDS: ModDdsLoader uploads the payload as-is, file size minus its 128 (148 for DX10) byte header.
  audio      .ogg/.wav/.mp3 under Sounds/: a file over 307200 bytes is streamed (ShouldStreamAudioClipFromFile, no
             resident estimate); a smaller one is decoded whole: samples x channels x 4 bytes (float PCM, an upper
             estimate; Unity may keep 16-bit).
  atlases    StaticTextureAtlas pages baked at load from textures under 512 px that ThingDefs/ScatterableDefs insert:
             atlas_attribution.py (rules there). Needs the def dump capture (refresh.D_DUMP) of the SAME mod set;
             a stale dump leaves atlases UNMEASURED and --check fails.
What it does NOT see (the residual against a measurement): RenderTextures (e.g. facial animation pools), pawn
atlases (built at runtime per pawn), AssetBundles, Core/DLC textures inside resources.assets, assemblies,
Unity/Mono overhead.
Whether GPU texture memory lands in the process's private bytes depends on the driver (WDDM); the report says so.

Cache: ~/.cache/rm_modaudit/mem/<packageId>.json (derived; outside git). Report: Transient/memory_attribution.md.
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CACHE = os.path.expanduser("~/.cache/rm_modaudit/mem")
SCHEMA = 3
VERSION = (1, 6)
TEX_EXT = (".png", ".jpg", ".jpeg", ".psd", ".dds")
SND_EXT = (".ogg", ".wav", ".mp3")
STREAM_OVER = 307200
MIPS = 4.0 / 3.0
MB = 1048576.0
PREFS = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/Prefs.xml"
REPORT = os.path.join(REPO, "Transient", "memory_attribution.md")
LIST_XML = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
STEAM_SUFFIX = "_steam"


def norm_id(pid):
    """packageId as ModLister.AnyModActiveNoSuffix compares it: lower case, no _steam suffix."""
    p = (pid or "").strip().lower()
    return p[:-len(STEAM_SUFFIX)] if p.endswith(STEAM_SUFFIX) else p


def parse_version(s):
    m = re.fullmatch(r"v?(\d+)\.(\d+)(?:\.\d+)*", (s or "").strip().lower())
    return (int(m.group(1)), int(m.group(2))) if m else None


def parse_load_folders(xml_text):
    """{version_key: [(folder, any_of, all_of, none_of)]} exactly as ModLoadFolders.LoadDataFromXmlCustom keys it
    (lower case, leading 'v' dropped; '/' or '\\' means the root, ''). Pure; selftested."""
    root = ET.fromstring(xml_text)
    out = {}

    def ids(el, attr):
        v = el.get(attr)
        return [s.strip() for s in v.split(",")] if v is not None else None

    for ver in root:
        if not isinstance(ver.tag, str):
            continue
        key = ver.tag.lower()
        if key.startswith("v"):
            key = key[1:]
        lst = out.setdefault(key, [])
        for li in ver:
            if not isinstance(li.tag, str):
                continue
            text = "".join(li.itertext())
            folder = "" if text in ("/", "\\") else text.replace("\\", "/")
            lst.append((folder, ids(li, "IfModActive"), ids(li, "IfModActiveAll"), ids(li, "IfModNotActive")))
    return out


def should_load(any_of, all_of, none_of, active):
    """LoadFolder.ShouldLoad against a set of norm_id()s. Pure; selftested."""
    if any_of and not any(norm_id(x) in active for x in any_of):
        return False
    if all_of and not all(norm_id(x) in active for x in all_of):
        return False
    if none_of and any(norm_id(x) in active for x in none_of):
        return False
    return True


def folders_descending(root_dirs, lf, active, version=VERSION):
    """The load folders, relative to the mod root, in ModContentPack.InitLoadFolders' descending order.
    root_dirs: names of the mod root's sub-directories (for the no-LoadFolders branch). lf: parse_load_folders() or
    None. Pure; selftested."""
    def add(entries):
        return [e[0] for e in reversed(entries) if should_load(e[1], e[2], e[3], active)]

    if lf:
        vs = "%d.%d" % version
        if lf.get(vs):
            return add(lf[vs])
        older = sorted((k for k in lf if k != "default" and "." in k and parse_version(k) and parse_version(k) <= version),
                       key=parse_version, reverse=True)
        if older and lf.get(older[0]) is not None:
            return add(lf[older[0]])
        if lf.get("default") is not None:
            return add(lf["default"])
    out = []
    vs = "%d.%d" % version
    if vs in root_dirs:
        out.append(vs)
    else:
        best = None
        for d in root_dirs:
            v = parse_version(d) if re.fullmatch(r"\d+\.\d+(\.\d+)*", d) else None
            if v and v <= version and (best is None or v > best[0]):
                best = (v, d)
        if best:
            out.append(best[1])
    if "Common" in root_dirs:
        out.append("Common")
    out.append("")
    return out


def texture_bytes(w, h, compression):
    """Resident bytes of one PNG-family texture after ModContentLoader: DXT5 when compressible, else RGBA32; x4/3 mips.
    Pure; selftested."""
    if compression and w % 4 == 0 and h % 4 == 0:
        return w * h * 1 * MIPS
    return w * h * 4 * MIPS


def dds_bytes(path, size):
    """Payload of a .dds: size minus a 128-byte header, 148 when the FourCC is DX10."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(88)
        dx10 = len(head) >= 88 and head[84:88] == b"DX10"
    except OSError:
        dx10 = False
    return max(0, size - (148 if dx10 else 128))


def ogg_samples(blob_head, blob_tail):
    """(channels, total_samples) of a Vorbis .ogg from its first and last bytes, else None. Pure; selftested."""
    i = blob_head.find(b"\x01vorbis")
    if i < 0 or len(blob_head) < i + 16:
        return None
    ch = blob_head[i + 11]
    j = blob_tail.rfind(b"OggS")
    if j < 0 or len(blob_tail) < j + 14:
        return None
    gran = struct.unpack("<q", blob_tail[j + 6:j + 14])[0]
    return (ch, gran) if ch and gran > 0 else None


def wav_samples(blob):
    """(channels, total_samples) of a RIFF/WAVE file from its bytes, else None. Pure; selftested."""
    if blob[:4] != b"RIFF" or blob[8:12] != b"WAVE":
        return None
    p, ch, bits = 12, None, None
    while p + 8 <= len(blob):
        cid, csz = blob[p:p + 4], struct.unpack("<I", blob[p + 4:p + 8])[0]
        if cid == b"fmt " and p + 24 <= len(blob):
            ch, bits = struct.unpack("<H", blob[p + 10:p + 12])[0], struct.unpack("<H", blob[p + 22:p + 24])[0]
        elif cid == b"data" and ch and bits:
            return (ch, csz // (ch * max(1, bits // 8)))
        p += 8 + csz + (csz & 1)
    return None


def audio_bytes(path, size):
    """(resident_bytes, how) for one sound file; streamed files cost 0 here."""
    if size > STREAM_OVER:
        return 0, "streamed"
    try:
        with open(path, "rb") as fh:
            blob = fh.read()
    except OSError:
        return 0, "unreadable"
    ext = os.path.splitext(path)[1].lower()
    r = None
    if ext == ".ogg":
        r = ogg_samples(blob[:4096], blob[-65536:])
    elif ext == ".wav":
        r = wav_samples(blob)
    if r:
        return r[0] * r[1] * 4, "decoded"
    if ext == ".mp3":  # no frame walk: 128 kbit/s stereo 44.1 kHz assumed
        secs = size * 8 / 128000.0
        return int(secs * 44100 * 2 * 4), "mp3_assumed"
    return 0, "unparsed"


def _ci_child(parent, name):
    """The real-cased child dir of parent matching name case-insensitively (Windows resolves it so), else None."""
    try:
        for d in os.listdir(parent):
            if d.lower() == name.lower() and os.path.isdir(os.path.join(parent, d)):
                return d
    except OSError:
        pass
    return None


def collect(folder, active, compression):
    """Walk one mod's loaded Textures/ and Sounds/ under the engine's folder rules."""
    from diskfacts import image_dims
    rec = {"tex_mb": 0.0, "tex_files": 0, "tex_dxt": 0, "tex_rgba": 0, "tex_rgba_mb": 0.0, "dds": 0,
           "tex_unreadable": 0, "snd_mb": 0.0, "snd_files": 0, "snd_streamed": 0, "snd_unparsed": 0, "largest": []}
    try:
        root_dirs = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
    except OSError as e:
        rec["error"] = str(e)
        return rec
    lf_name = next((f for f in os.listdir(folder) if f.lower() == "loadfolders.xml"), None)
    lf = None
    if lf_name:
        try:
            lf = parse_load_folders(open(os.path.join(folder, lf_name), "rb").read())
        except ET.ParseError as e:
            rec["loadfolders_error"] = str(e)
    order = folders_descending(root_dirs, lf, active)
    rec["folders"] = order
    seen_tex, seen_snd, big = {}, {}, []
    for lf_rel in order:
        base = os.path.join(folder, lf_rel) if lf_rel else folder
        if not os.path.isdir(base):
            continue
        for content, exts, seen in (("Textures", TEX_EXT, seen_tex), ("Sounds", SND_EXT, seen_snd)):
            c = _ci_child(base, content)
            if not c:
                continue
            for dp, _dns, fns in os.walk(os.path.join(base, c)):
                for fn in fns:
                    ext = os.path.splitext(fn)[1].lower()
                    if ext not in exts:
                        continue
                    p = os.path.join(dp, fn)
                    key = os.path.relpath(p, base).replace("\\", "/")
                    if key not in seen:
                        seen[key] = p
    dims = {}
    dds_keys = {k[:-4].lower() for k in seen_tex if k.lower().endswith(".dds")}
    for key, p in seen_tex.items():
        ext = os.path.splitext(key)[1].lower()
        if ext != ".dds" and key[:-4].lower() in dds_keys:  # engine: Substring(0, Length - 4) + ".dds"
            continue
        try:
            size = os.path.getsize(p)
        except OSError:
            rec["tex_unreadable"] += 1
            continue
        if ext == ".dds":
            b = dds_bytes(p, size)
            rec["dds"] += 1
            d = image_dims(p)
        else:
            d = image_dims(p)
            if d is None:
                rec["tex_unreadable"] += 1
                continue
            b = texture_bytes(d[0], d[1], compression)
            if compression and d[0] % 4 == 0 and d[1] % 4 == 0:
                rec["tex_dxt"] += 1
            else:
                rec["tex_rgba"] += 1
                rec["tex_rgba_mb"] += b / MB
        if not key.lower().startswith("textures/"):
            continue  # a Sounds/ hit cannot reach here; guard keeps the atlas key shape honest
        # atlas_attribution reads this: ContentFinder path (under Textures/, no extension) -> pixel dims
        # seen_tex is in descending folder priority and case-sensitive like GetAllFilesForMod; lower-casing for the
        # lookup must not let a lower-priority Foo/foo twin overwrite the winner, so the first one stays
        dims.setdefault(os.path.splitext(key.split("/", 1)[1])[0].lower(), list(d) if d else [0, 0])
        rec["tex_files"] += 1
        rec["tex_mb"] += b / MB
        big.append((round(b / MB, 2), key))
    for key, p in seen_snd.items():
        try:
            size = os.path.getsize(p)
        except OSError:
            continue
        b, how = audio_bytes(p, size)
        rec["snd_files"] += 1
        rec["snd_streamed"] += how == "streamed"
        rec["snd_unparsed"] += how in ("unparsed", "unreadable")
        rec["snd_mb"] += b / MB
    big.sort(reverse=True)
    rec["largest"] = big[:5]
    rec["tex_dims"] = dims
    for k in ("tex_mb", "tex_rgba_mb", "snd_mb"):
        rec[k] = round(rec[k], 2)
    return rec


def list_ids(path=LIST_XML):
    """Active packageIds of a ModsConfig-shaped file, parsed (never grepped), in list order."""
    return [li.text.strip().lower() for li in ET.parse(path).getroot().find("activeMods") if li.text]


def compression_pref(path=PREFS):
    """Prefs textureCompression; None when the file cannot be read (then the caller refuses, never assumes)."""
    try:
        el = ET.parse(path).getroot().find("textureCompression")
    except (OSError, ET.ParseError):
        return None
    return None if el is None else el.text.strip().lower() == "true"


def rows_for_list(ids):
    from universe import UNIVERSE_JSON
    by = {r["packageId"].lower(): r for r in json.load(open(UNIVERSE_JSON))["rows"]}
    return [(pid, (by.get(pid) or by.get(norm_id(pid)) or {}).get("folder")) for pid in ids]


def _cache_path(pid, fp):
    """One cache folder per fingerprint, so two lists never evict each other's records."""
    return os.path.join(CACHE, fp, re.sub(r"[^A-Za-z0-9._-]", "_", pid) + ".json")


def _cached(pid, fp):
    p = _cache_path(pid, fp)
    if not os.path.isfile(p):
        return None
    try:
        rec = json.load(open(p))
    except (OSError, ValueError):
        return None
    return rec if rec.get("schema") == SCHEMA and rec.get("fingerprint") == fp else None


def fingerprint(active, compression):
    """Cache key: the list and the compression pref change what loads, so either invalidates every record."""
    import hashlib
    h = hashlib.sha1(("|".join(sorted(active)) + "|%s" % compression).encode()).hexdigest()
    return h[:16]


def game_private_mb():
    """Private MB of every running RimWorld process, from health_observer under Windows python.exe; None if no read."""
    import shutil
    exe = shutil.which("python.exe")
    if not exe:
        print("UNMEASURED: python.exe is not on PATH (Windows interop), so the game's private bytes cannot be read")
        return None
    try:
        r = subprocess.run([exe, "src/RimMandrake/Utils/health_observer.py", "--once", "--print"],
                           cwd=REPO, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    vals = [float(x) for x in re.findall(r'"privateMB":\s*([0-9.]+)', r.stdout)]
    return vals or None


def atlas_for(ids, recs, active, compression, dump_dir):
    """Atlas estimate for the list, or (None, why) when the def dump does not describe this mod set."""
    import atlas_attribution as A
    ok, why = A.dump_matches(dump_dir, [norm_id(x) for x in ids], norm_id)
    if not ok:
        return None, why
    idx = A.slim_index(dump_dir, os.path.join(CACHE, "atlas"))
    ordered = [(pid, recs[pid]) for pid in ids if pid in recs]
    return A.estimate(idx, ordered, compression), why


def write_report(rows, recs, compression, measured, list_path, report, atlas=None, atlas_why=""):
    by_atlas = (atlas or {}).get("by_mod_mb", {})
    tot_tex = sum(r.get("tex_mb", 0) for r in recs.values())
    tot_snd = sum(r.get("snd_mb", 0) for r in recs.values())
    tot_atl = atlas["total_mb"] if atlas else 0.0
    tot_rgba = sum(r.get("tex_rgba_mb", 0) for r in recs.values())
    ranked = sorted(recs.items(), key=lambda kv: -(kv[1].get("tex_mb", 0) + kv[1].get("snd_mb", 0)
                                                   + by_atlas.get(kv[0], 0)))
    L = ["# Native memory attribution by mod (ESTIMATE)", "",
         "Generated %s by `src/RimMandrake/Utils/modaudit/memory_attribution.py`; list `%s` (%d ids, %d attributed);"
         " Prefs textureCompression=%s. Rules: see the script docstring (from the 1.6 decompile)." % (
             time.strftime("%Y-%m-%d %H:%M"), list_path, len(rows), len(recs), compression), "",
         "- textures: **%.1f GB** (of which %.1f GB stay RGBA32 because a side is not a multiple of 4)" % (
             tot_tex / 1024, tot_rgba / 1024),
         "- decoded audio: **%.2f GB** (files <= 300 KB, float PCM upper estimate)" % (tot_snd / 1024)]
    if atlas:
        mod_atl = sum(by_atlas.values())
        L += ["- static atlases: **%.2f GB** in %d pages holding %d mod textures (%s); %.2f GB of it split to mods"
              " by pixel share. Not sized: %d vanilla/DLC paths (resources.assets/bundles), %d ThingDefs with a"
              " mod graphic class that inserts nothing here (top: %s), %d textures >= 512 px" % (
                  tot_atl / 1024, len(atlas["pages"]), atlas["textures"], atlas_why, mod_atl / 1024,
                  atlas["vanilla_unsized"], atlas["defs_foreign_class"],
                  ", ".join("%s %d" % kv for kv in list(atlas["foreign_classes"].items())[:3]), atlas["too_big"])]
        groups = {}
        for pg in atlas["pages"]:
            g = groups.setdefault("%s%s" % (pg["group"], "+mask" if pg["mask"] else ""), [0, 0.0, []])
            g[0] += 1
            g[1] += pg["mb"]
            g[2].append("%dx%d" % (pg["w"], pg["h"]))
        L += ["  - %s: %d page(s), %.0f MB (%s)" % (k, v[0], v[1], ", ".join(v[2][:6])) for k, v in sorted(groups.items())]
    else:
        L.append("- static atlases: UNMEASURED (%s)" % atlas_why)
    L.append("- total attributed: **%.1f GB**" % ((tot_tex + tot_snd + tot_atl) / 1024))
    tot_all = tot_tex + tot_snd + tot_atl
    if measured:
        L.append("- MEASURED game private bytes now: %s MB (health_observer); attribution / private = %.0f%%;"
                 " unattributed residual %.1f GB" % (", ".join("%.0f" % m for m in measured),
                                                    100.0 * tot_all / max(measured),
                                                    (max(measured) - tot_all) / 1024))
    else:
        L.append("- game private bytes: UNMEASURED (no --reconcile, or no game process)")
    L += ["", "Unattributed by design: pawn atlases, RenderTextures, AssetBundles, resources.assets, assemblies,"
          " Mono/Unity overhead. GPU texture memory counts in private bytes only where the driver backs it there.", "",
          "| # | packageId | tex GB | atlas MB | RGBA32 MB | tex files | audio MB | biggest texture |",
          "|---|---|---|---|---|---|---|---|"]
    for i, (pid, r) in enumerate(ranked[:60], 1):
        big = r.get("largest") or []
        L.append("| %d | `%s` | %.2f | %s | %.0f | %d | %.0f | %s |" % (
            i, pid, r.get("tex_mb", 0) / 1024, ("%.0f" % by_atlas.get(pid, 0)) if atlas else "UNMEASURED",
            r.get("tex_rgba_mb", 0), r.get("tex_files", 0), r.get("snd_mb", 0),
            ("`%s` %.0f MB" % (big[0][1], big[0][0])) if big else ""))
    os.makedirs(os.path.dirname(os.path.abspath(report)), exist_ok=True)
    with open(report, "w") as fh:
        fh.write("\n".join(L) + "\n")
    return tot_tex, tot_snd, tot_atl


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=400.0)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--reconcile", action="store_true")
    ap.add_argument("--list", default=LIST_XML, help="a ModsConfig-shaped file (default: the FULL.LATEST tier list)")
    ap.add_argument("--report", default=REPORT)
    ap.add_argument("--dump", default=None, help="def dump capture dir (default: refresh.D_DUMP, the live capture)")
    a = ap.parse_args(argv)
    compression = compression_pref()
    if compression is None:
        print("REFUSED: cannot read textureCompression from %s" % PREFS)
        return 2
    ids = list_ids(a.list)
    active = {norm_id(x) for x in ids}
    fp = fingerprint(active, compression)
    rows = rows_for_list(ids)
    resolved = [(pid, f) for pid, f in rows if f and os.path.isdir(f)]
    os.makedirs(os.path.join(CACHE, fp), exist_ok=True)
    recs, t0, walked = {}, time.time(), 0
    for pid, f in resolved:
        rec = _cached(pid, fp)
        if rec is None and time.time() - t0 < a.budget:
            rec = collect(f, active, compression)
            rec.update({"schema": SCHEMA, "fingerprint": fp, "packageId": pid, "folder": f})
            with open(_cache_path(pid, fp), "w") as fh:
                json.dump(rec, fh)
            walked += 1
        if rec is not None:
            recs[pid] = rec
    missing = len(resolved) - len(recs)
    unresolved = len(rows) - len(resolved)
    print("memory_attribution: %d ids, %d resolved to a folder, %d unresolved (DLC/Core or absent), %d attributed,"
          " %d walked this run in %.0fs, %d remaining" % (len(rows), len(resolved), unresolved, len(recs), walked,
                                                         time.time() - t0, missing))
    if missing:
        print("INCOMPLETE - re-run to resume")
        return 1
    dump = a.dump
    if dump is None:
        sys.path.insert(1, os.path.dirname(HERE))
        import game_paths
        dump = game_paths.DEF_DUMP
    atlas, atlas_why = atlas_for(ids, recs, active, compression, dump)
    measured = game_private_mb() if a.reconcile else None
    tex, snd, atl = write_report(rows, recs, compression, measured, a.list, a.report, atlas, atlas_why)
    print("textures %.1f GB + decoded audio %.2f GB + static atlases %s = %.1f GB attributed; report %s" % (
        tex / 1024, snd / 1024, ("%.2f GB" % (atl / 1024)) if atlas else "UNMEASURED", (tex + snd + atl) / 1024,
        a.report))
    if a.check and atlas is None:
        print("CHECK FAIL: static atlases UNMEASURED - %s (re-capture the def dump for this list)" % atlas_why)
        return 1
    if a.check and atlas["textures"] < 100:
        print("SANITY FAIL: fewer than 100 mod textures in atlas pages on a full list - the atlas pass cannot see")
        return 1
    if a.reconcile and not measured:
        print("RECONCILE FAILED: no game private bytes read")
        return 1
    if a.check and len(recs) < 100:
        print("SANITY FAIL: fewer than 100 mods attributed on a full list - the instrument cannot see")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
