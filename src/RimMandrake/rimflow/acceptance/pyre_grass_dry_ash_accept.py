#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_FIX_PYRE_GRASS_DRY_ASH_CRAWLS_AT_A_TENTH: on dry ash the Pyrelands grasses grow
swiftly, watered they grow faster still and do the gentle burst, and ordinary crops keep the ash field's own rule.

Owner, 2026-11-13 (RIMMANDRAKE_PROVE_PYRELANDS_IN_FOUR_SCENES): "the grasses grow swiftly even on seemingly dry ash due to
their very deep roots and underground storage systems. This is specific to the plants in that Biome and their relationship
with the ash. When watered they accelerate even faster and even do the gentle burst. ... Ordinary crops should still just
treat it as very fertile ground and benefit from water as before."

Behavioural, not a source pin: the body of RM_ExplosiveGrowthKernel.MoistureFactor is lifted from the C# and run under node
(its statements are C#'s and JS's common subset), with the rate settings at the defaults ExplosiveGrowthMod.cs ships.
The Pyrelands natives are archetype FireAdapted (roster fireAdapted + fireAdaptedBiomes RM_Pyrelands). Rows:
  fire_adapted_dry_ash_swift   FireAdapted, dry, not fresh ash: r >= 1 (the vanilla rate or better)   RED on 8bf6527061 (0.1)
  fire_adapted_watered_faster  FireAdapted, wet: r > the dry-ash r
  fire_adapted_fresh_ash       FireAdapted, fresh ash: r >= the dry-ash r
  dry_native_still_tenth       DryNative, dry: r == dryDry (the other biomes' natives keep C6 "tenth speed")
  wet_native_unchanged         WetNative: r == wetNative
  vanilla_crop_rule_unchanged  Vanilla, no water nearby: r == vanillaDry; with water: 1
  pyrelands_crops_opt_out      Pyrelands.xml sets vanillaCropsNeedWater false (crops follow the ash field: 70% dry, 140% watered)
  gentle_burst_only_on_water   CycleWetFor keeps "!prof.gentleBurst" on the fresh-ash cycle path (owner 2026-11-07)
A fix may live in the kernel or in MoistureFactorFor; if it adds a kernel parameter, extend CALL below and keep every row.

    python3 src/RimMandrake/rimflow/acceptance/pyre_grass_dry_ash_accept.py   (exit 0 = PASS 12/12; the builder does not edit it)
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(REPO, "src", "RimMandrake", "ExplosiveGrowth", "Source")
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def body(src, signature):
    i = src.find(signature)
    if i < 0:
        return None
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return None


def to_js(cs):
    js = re.sub(r"\b(\d+(?:\.\d+)?)f\b", r"\1", cs)
    js = re.sub(r"\b(?:float|bool|int|var)\s+(\w+)\s*=", r"let \1 =", js)
    return js


def rate_defaults(mod):
    """RM_RateSettings field -> the shipped default of the static it is read from (ExplosiveGrowthMod.cs Rates)."""
    m = re.search(r"Rates\s*=>\s*new RM_RateSettings\s*\{(.*?)\};", mod, re.S)
    out = {}
    for field, static in re.findall(r"(\w+)\s*=\s*(\w+)", m.group(1) if m else ""):
        d = re.search(r"public static (?:float|bool|int) %s = ([^;]+);" % static, mod)
        if d:
            v = d.group(1).strip().rstrip("f")
            out[field] = (v == "true") if v in ("true", "false") else float(v)
    return out


kernel_src = "".join(read(os.path.join(d, f)) for d, _, fs in sorted(os.walk(SRC)) for f in sorted(fs) if f.endswith(".cs"))
mf = body(kernel_src, "public static float MoistureFactor(")
check("MoistureFactor found in Source/", mf is not None)
rates = rate_defaults(read(os.path.join(SRC, "ExplosiveGrowthMod.cs")))
check("rate defaults read", {"dryWet", "dryDry", "wetNative", "vanillaDry", "vanillaNeedsWater"} <= set(rates), rates)
node = shutil.which("node")
check("node on PATH", bool(node))

# (archetype, inScope, stalled, sealed, wet, ashFresh, woody, waterNearby)
CASES = {
    "fa_dry": ("FireAdapted", True, False, False, False, False, False, False),
    "fa_wet": ("FireAdapted", True, False, False, True, False, False, False),
    "fa_ash": ("FireAdapted", True, False, False, False, True, False, False),
    "dn_dry": ("DryNative", True, False, False, False, False, False, False),
    "wn": ("WetNative", True, False, False, False, False, False, False),
    "v_dry": ("Vanilla", True, False, False, False, False, False, False),
    "v_near": ("Vanilla", True, False, False, False, False, False, True),
}
r = {}
if mf and node and not fails:
    js = ("const RM_Archetype = new Proxy({}, {get: (o, k) => String(k)});\n"
          "function MoistureFactor(a, inScope, stalled, sealedGrower, wet, ashFresh, woody, waterNearby, s) %s\n"
          "const s = new Proxy(%s, {get: (o, k) => { if (!(k in o)) throw new Error('rate ' + String(k) + "
          "' not in RM_RateSettings defaults'); return o[k]; }});\n"
          "const CASES = %s; const out = {};\n"
          "for (const [k, c] of Object.entries(CASES)) out[k] = MoistureFactor(...c, s);\n"
          "console.log(JSON.stringify(out));\n") % (to_js(mf), json.dumps(rates), json.dumps(CASES))
    p = subprocess.run([node, "-e", js], capture_output=True, text=True, timeout=60)
    check("kernel runs under node", p.returncode == 0, (p.stderr or p.stdout)[-400:])
    if p.returncode == 0:
        r = json.loads(p.stdout.strip().splitlines()[-1])

if r:
    check("fire_adapted_dry_ash_swift", r["fa_dry"] >= 1.0,
          "a Pyrelands grass on dry, unburned ash grows at x%g; the owner wants it swift" % r["fa_dry"])
    check("fire_adapted_watered_faster", r["fa_wet"] > r["fa_dry"], (r["fa_wet"], r["fa_dry"]))
    check("fire_adapted_fresh_ash", r["fa_ash"] >= r["fa_dry"], (r["fa_ash"], r["fa_dry"]))
    check("dry_native_still_tenth", r["dn_dry"] == rates["dryDry"], (r["dn_dry"], rates["dryDry"]))
    check("wet_native_unchanged", r["wn"] == rates["wetNative"], (r["wn"], rates["wetNative"]))
    check("vanilla_crop_rule_unchanged", r["v_dry"] == rates["vanillaDry"] and r["v_near"] == 1.0, (r["v_dry"], r["v_near"]))

biome = read(os.path.join(REPO, "src", "RimMandrake", "Pyrelands", "Defs", "BiomeDefs", "Pyrelands.xml"))
check("pyrelands_crops_opt_out",
      re.search(r"RM_ExplosiveGrowthBiomeExtension.*?<vanillaCropsNeedWater>false</vanillaCropsNeedWater>", biome, re.S)
      is not None)
cw = body(read(os.path.join(SRC, "RM_MapComponent_ExplosiveGrowth.cs")), "public bool CycleWetFor(") or ""
check("gentle_burst_only_on_water", "!prof.gentleBurst" in cw)

TOTAL = 12
print("\nPASS %d/%d" % (TOTAL - len(fails), TOTAL) + ("" if not fails else "  failed: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
