#!/usr/bin/env python3
"""What does RW - Planet Atmosphere (rwnodetree.rwplanetatmosphere) cost? Item PLANET_ATMOSPHERE_CLOUD_COST_1,
owner card C18: "Measure real memory cost first".

  offline              texture census by the vanilla 1.6 loader rule; exits 1 on a blind census
  record --require with|without
                       one sample of the RUNNING launch (load time, GPU dedicated/shared, private bytes),
                       appended to the sample file; exits 0 only if the launch is the required condition
                       and every number was measured
  verdict              exits 0 when a 'with' and a 'without' sample exist whose mod lists differ only by
                       this mod; prints the deltas

The loader rule (Verse.ModContentLoader.LoadTextureViaImageConversion, RimWorld 1.6, read from the
decompile): every PNG under the mod's Textures/ is decoded to RGBA32 with mipmaps; with Prefs
textureCompression on and both sides divisible by 4 it is compressed to DXT5 (GraphicsFormat 101,
1 byte/px); a non-power-of-two texture keeps only the mip levels whose sides stay divisible by 4
(StaticTextureAtlas.CalculateMaxMipmapsForDxtSupport). The resident figure is INFERRED from that
rule; the decoded RGBA32 copy is transient, held only while that texture loads.

Load time is the largest RimBridge STARTUP_TIMING elapsedMs in Player.log (mod construction to the
bridge's last startup phase; engine start before mod construction is not in it). Which mods the
launch loaded: ModsConfig.xml, trusted only when it was last written no later than LAUNCH_SLACK_S
after the process started (ModsConfig describes the NEXT load).
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

PKG = "rwnodetree.rwplanetatmosphere"
WORKSHOP_ID = "3272330410"
C = "/mnt/c"
MOD_DIR = C + "/Program Files (x86)/Steam/steamapps/workshop/content/294100/" + WORKSHOP_ID
CFG = C + "/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
MODSCONFIG = CFG + "/Config/ModsConfig.xml"
PREFS = CFG + "/Config/Prefs.xml"
PLAYER_LOG = CFG + "/Player.log"
POWERSHELL = C + "/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
DLC = ["ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
       "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]
LAUNCH_SLACK_S = 300
MB = 1024.0 * 1024.0


def storage_root():
    p = os.environ.get("RM_AGENT_STORAGE")
    if p:
        return p
    out = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                         capture_output=True, text=True, timeout=30)
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("agent storage root unset: " + out.stderr.strip())
    return out.stdout.strip()


def samples_path():
    return os.path.join(storage_root(), "rimmandrake", "planet_atmosphere_cost", "samples.jsonl")


# ---------------------------------------------------------------- loader arithmetic (pure)

def is_pow2(n):
    return n > 0 and (n & (n - 1)) == 0


def dxt_mips(w, h):
    """StaticTextureAtlas.CalculateMaxMipmapsForDxtSupport: levels while both sides >=4 and %4==0."""
    n = 0
    while w >= 4 and h >= 4 and w % 4 == 0 and h % 4 == 0:
        n += 1
        w, h = max(1, w >> 1), max(1, h >> 1)
    return n


def full_mips(w, h):
    n = 1
    while w > 1 or h > 1:
        w, h = max(1, w >> 1), max(1, h >> 1)
        n += 1
    return n


def texture_bytes(w, h, compression=True, compute=True):
    """Resident bytes and transient RGBA32 decode bytes for one PNG, by the 1.6 loader rule.

    compute = UnityData.ComputeShadersSupported (any desktop GPU).
    No compute: a non-power-of-two (or <4) texture is reloaded with mips clamped to dxt_mips, then
      Texture2D.Compress() keeps that chain as DXT5 when both sides are %4.
    Compute: the full RGBA32 chain is decoded, then StaticTextureAtlas.FastCompressDXT returns it
      UNCOMPRESSED if min side <= 16, else keeps min(floor(log2(min/16))+1, dxt_mips, chain) levels."""
    full = full_mips(w, h)
    odd = w < 4 or h < 4 or not is_pow2(w) or not is_pow2(h)
    mod4 = w % 4 == 0 and h % 4 == 0
    mips, dxt = full, False
    if compression and not compute:
        if odd:
            mips = max(1, min(full, dxt_mips(w, h)))
        dxt = mod4
    elif compression and compute and mod4 and min(w, h) > 16:
        dxt = True
        mips = max(1, min(int(math.floor(math.log(min(w, h) / 16.0, 2))) + 1, dxt_mips(w, h), full))
    bpp = 1.0 if dxt else 4.0
    resident = 0.0
    rgba = 0.0
    lw, lh = w, h
    for i in range(full):
        if i < mips:
            resident += lw * lh * bpp
        rgba += lw * lh * 4.0
        lw, lh = max(1, lw >> 1), max(1, lh >> 1)
    return {"format": "DXT5" if dxt else "RGBA32", "mips": mips, "resident": int(resident), "decode": int(rgba)}


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


# ---------------------------------------------------------------- offline

def prefs_compression():
    try:
        node = ET.parse(PREFS).getroot().find("textureCompression")
    except (OSError, ET.ParseError):
        return None
    return None if node is None else node.text.strip().lower() == "true"


def offline(args):
    tex_dir = os.path.join(MOD_DIR, "Textures")
    comp = prefs_compression()
    rows, total_res, total_dec, disk = [], 0, 0, 0
    for root, _d, files in os.walk(tex_dir):
        for f in sorted(files):
            if not f.lower().endswith((".png", ".jpg", ".jpeg", ".psd", ".dds")):
                continue
            p = os.path.join(root, f)
            sz = png_size(p) if f.lower().endswith(".png") else None
            if sz is None:
                rows.append({"file": os.path.relpath(p, tex_dir), "unread": "not a PNG header"})
                continue
            t = texture_bytes(sz[0], sz[1], comp is not False)
            t.update(file=os.path.relpath(p, tex_dir), w=sz[0], h=sz[1], disk=os.path.getsize(p))
            rows.append(t)
            total_res += t["resident"]
            total_dec += t["decode"]
            disk += t["disk"]
    measured = [r for r in rows if "w" in r]
    # sanity probe: the instrument must see the one texture this item is named for
    if not any(r["w"] == 8192 and r["h"] == 4096 for r in measured):
        print("BLIND: no 8192x4096 cloud texture found under " + tex_dir + "; census not trusted")
        return 1
    print("Planet Atmosphere textures (%s), textureCompression=%s (Prefs.xml)" % (tex_dir, comp))
    for r in rows:
        if "w" not in r:
            print("  %-40s UNMEASURED (%s)" % (r["file"], r["unread"]))
            continue
        print("  %-40s %5dx%-5d %-6s mips=%-2d disk %6.1f MB  resident %6.1f MB  decode-peak %6.1f MB"
              % (r["file"], r["w"], r["h"], r["format"], r["mips"], r["disk"] / MB, r["resident"] / MB,
                 r["decode"] / MB))
    print("TOTAL %d textures: disk %.1f MB, resident VRAM %.1f MB (INFERRED from the loader rule), "
          "largest single decode %.1f MB (transient)"
          % (len(measured), disk / MB, total_res / MB, max(r["decode"] for r in measured) / MB))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"compression": comp, "textures": rows, "resident": total_res, "disk": disk}, fh, indent=1)
    return 0


# ---------------------------------------------------------------- live

def active_mods():
    root = ET.parse(MODSCONFIG).getroot().find("activeMods")
    return [li.text.strip().lower() for li in root.findall("li") if li.text]


def load_ms(text):
    vals = [int(m) for m in re.findall(r"\[RimBridge\] STARTUP_TIMING phase=\S+ durationMs=-?\d+ elapsedMs=(\d+)", text)]
    return max(vals) if vals else None


PS_SAMPLE = r"""
$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { '{"running": false}'; exit }
$ded = 0; $sha = 0; $n = 0
foreach ($c in @('Dedicated Usage','Shared Usage')) {
  (Get-Counter ("\GPU Process Memory(pid_" + $p.Id + "_*)\" + $c) -ErrorAction SilentlyContinue).CounterSamples |
    ForEach-Object { $n++; if ($c -eq 'Dedicated Usage') { $ded += $_.CookedValue } else { $sha += $_.CookedValue } }
}
@{running=$true; pid=$p.Id; start=$p.StartTime.ToUniversalTime().ToString('o'); private=$p.PrivateMemorySize64;
  working=$p.WorkingSet64; gpu_dedicated=$ded; gpu_shared=$sha; gpu_counters=$n} | ConvertTo-Json -Compress
"""


def sample_process():
    out = subprocess.run([POWERSHELL, "-NoProfile", "-Command", PS_SAMPLE], capture_output=True, text=True,
                         timeout=120)
    line = [l for l in out.stdout.splitlines() if l.strip().startswith("{")]
    if not line:
        return {"error": "powershell gave no JSON: " + (out.stderr.strip() or out.stdout.strip())[:200]}
    return json.loads(line[-1])


def parse_utc(s):
    s = re.sub(r"(\.\d{6})\d+", r"\1", s).replace("Z", "+00:00")
    return dt.datetime.fromisoformat(s)


def judge_sample(proc, mods, cfg_mtime, log_text, log_mtime):
    """Pure: build the sample row and the list of reasons it is not a measurement."""
    bad = []
    row = {"at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    if not proc.get("running"):
        return row, [proc.get("error", "RimWorldWin64 is not running")]
    start = parse_utc(proc["start"])
    row.update(pid=proc["pid"], start=proc["start"], private_mb=round(proc["private"] / MB, 1),
               working_mb=round(proc["working"] / MB, 1), gpu_dedicated_mb=round(proc["gpu_dedicated"] / MB, 1),
               gpu_shared_mb=round(proc["gpu_shared"] / MB, 1))
    if not proc.get("gpu_counters"):
        bad.append("no GPU Process Memory counter for pid %s" % proc["pid"])
    cfg_age = (cfg_mtime - start).total_seconds()
    row["modsconfig_written_after_start_s"] = round(cfg_age, 1)
    if cfg_age > LAUNCH_SLACK_S:
        bad.append("ModsConfig.xml written %.0f s after launch: it describes the next load, not this one" % cfg_age)
    if (log_mtime - start).total_seconds() < 0:
        bad.append("Player.log is older than the running process")
    row["with"] = PKG in mods
    row["mods"] = mods
    row["dlc_missing"] = [d for d in DLC if d not in mods]
    if row["dlc_missing"]:
        bad.append("DLC missing from the list: " + ", ".join(row["dlc_missing"]))
    row["load_ms"] = load_ms(log_text)
    if row["load_ms"] is None:
        bad.append("no RimBridge STARTUP_TIMING line in Player.log: load time UNMEASURED")
    return row, bad


def record(args):
    proc = sample_process()
    mods = active_mods()
    cfg_mtime = dt.datetime.fromtimestamp(os.path.getmtime(MODSCONFIG), dt.timezone.utc)
    log_mtime = dt.datetime.fromtimestamp(os.path.getmtime(PLAYER_LOG), dt.timezone.utc)
    with open(PLAYER_LOG, "rb") as fh:
        text = fh.read().decode("utf-8", "replace")
    row, bad = judge_sample(proc, mods, cfg_mtime, text, log_mtime)
    want = args.require == "with"
    if not bad and row["with"] != want:
        bad.append("this launch is the '%s' condition, not '%s'" % ("with" if row["with"] else "without",
                                                                    args.require))
    if bad:
        print("UNMEASURED: " + "; ".join(bad))
        return 1
    path = samples_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps(row) + "\n")
    print("SAMPLE %s: load %.1f s, GPU dedicated %.1f MB, shared %.1f MB, private %.1f MB -> %s"
          % (args.require, row["load_ms"] / 1000.0, row["gpu_dedicated_mb"], row["gpu_shared_mb"],
             row["private_mb"], path))
    return 0


def pair(rows):
    """Pure: latest with/without rows whose mod lists differ only by PKG."""
    for w in reversed([r for r in rows if r.get("with")]):
        for o in reversed([r for r in rows if r.get("with") is False]):
            if set(w["mods"]) ^ set(o["mods"]) == {PKG}:
                return w, o
    return None


def verdict(args):
    path = samples_path()
    rows = []
    if os.path.exists(path):
        with open(path) as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
    p = pair(rows)
    if not p:
        print("NO PAIR: %d samples in %s; need one 'with' and one 'without' whose lists differ only by %s"
              % (len(rows), path, PKG))
        return 1
    w, o = p
    print("A/B %s (with %s, without %s): load %+.1f s (%.1f vs %.1f), GPU dedicated %+.1f MB, shared %+.1f MB, "
          "private %+.1f MB" % (PKG, w["at"], o["at"], (w["load_ms"] - o["load_ms"]) / 1000.0, w["load_ms"] / 1000.0,
                                o["load_ms"] / 1000.0, w["gpu_dedicated_mb"] - o["gpu_dedicated_mb"],
                                w["gpu_shared_mb"] - o["gpu_shared_mb"], w["private_mb"] - o["private_mb"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("offline")
    o.add_argument("--json")
    r = sub.add_parser("record")
    r.add_argument("--require", choices=["with", "without"], required=True)
    sub.add_parser("verdict")
    args = ap.parse_args(argv)
    return {"offline": offline, "record": record, "verdict": verdict}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
