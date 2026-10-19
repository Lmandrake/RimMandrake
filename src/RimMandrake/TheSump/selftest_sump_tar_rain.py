#!/usr/bin/env python3
"""SUMP_TAR_LIVING_SYSTEMS_1 part 2 (tar rain) wiring, offline. Owner 2026-10-09: "Flowworks supports tar rain but
campaign does not. The biome itself does except for the campaign."

Reds if: RM_TheSump does not carry RM_SumpTarRainLock; the lock's base weather is not the dusk or its burst is not
RM_TarRain, or its gate/frequency keys are not the ones the Sump mod registers; RM_TarRain has rainRate > 0 (tar
would douse fires and fill pits with water), no filth-rain event, or a filth other than RM_Filth_Tar; RUT_Sump (the
campaign biome) can reach RM_SumpTarRainLock; the campaign patch does not swap RM_TheSump back to RUT_SumpDuskLock
inside a FindMod on the composed biomes mod's name (TheSump ships inside it); a tar-rain setting is missing, defaults off, or is not scribed.
Mutants must go red.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
P = {
    "biome": os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheSump_Biome.xml"),
    "lock": os.path.join(HERE, "Defs", "GameConditionDefs", "RM_SumpTarRainLock.xml"),
    "weather": os.path.join(HERE, "Defs", "WeatherDefs", "RM_TarRain.xml"),
    "mod": os.path.join(HERE, "Source", "RM_TheSumpMod.cs"),
    "about": os.path.join(HERE, "About", "About.xml"),
    "compose": os.path.join(SRC, "RimMandrake", "Biomes.compose.json"),
    "rutsump": os.path.join(SRC, "RimUtinni", "UtinniPatches", "Defs", "BiomeDefs", "RUT_Sump.xml"),
    "wiring": os.path.join(HERE, "Patches", "RUT_SumpDuskLock_BiomeWiring.xml"),
    "campaign": os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "Campaign_SumpNoTarRain.xml"),
}
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


def findings(t):
    out = []
    biome = ET.fromstring(t["biome"].encode())
    conds = [li.text.strip() for li in biome.iter("li") if li.text and li.text.strip().endswith("Lock")
             and any(li in list(bm) for bm in biome.iter("biomeMapConditions"))]
    if conds != ["RM_SumpTarRainLock"]:
        out.append("RM_TheSump biomeMapConditions = %r" % conds)
    lock = ET.fromstring(t["lock"].encode()).find("GameConditionDef")
    ext = lock.find("modExtensions/li") if lock is not None else None
    if lock is None or not (lock.findtext("conditionClass") or "").endswith("RM_GameCondition_WeatherPulse") or ext is None:
        out.append("lock is not a WeatherPulse condition")
    else:
        for k, v in (("baseWeather", "RUT_SumpWeather"), ("burstWeather", "RM_TarRain"),
                     ("burstGateKey", "Sump.tarRain"), ("burstFrequencyKey", "Sump.tarRainFrequency")):
            if (ext.findtext(k) or "").strip() != v:
                out.append("lock %s != %s" % (k, v))
        if ext.find("scaldDamageDef") is not None:
            out.append("lock scalds")
    w = ET.fromstring(t["weather"].encode()).find("WeatherDef")
    if float(w.findtext("rainRate") or "1") > 0:
        out.append("RM_TarRain rainRate > 0")
    if not any((e.findtext("eventClass") or "").endswith("RM_WeatherEvent_FilthRain") for e in w.iter("li")):
        out.append("RM_TarRain has no filth-rain event")
    fr = [li for li in w.iter("li") if (li.get("Class") or "").endswith("RM_FilthRainExtension")]
    if not fr or (fr[0].findtext("filthDef") or "").strip() != "RM_Filth_Tar":
        out.append("RM_TarRain filth is not RM_Filth_Tar")
    if not fr or (fr[0].findtext("intensityKey") or "").strip() != "Sump.tarRainIntensity":
        out.append("RM_TarRain intensityKey")
    gates = [li for li in w.iter("li") if (li.get("Class") or "").endswith("RM_MechanicGateExtension")]
    if not gates or (gates[0].findtext("gateKey") or "").strip() != "Sump.tarRain":
        out.append("RM_TarRain not gated by Sump.tarRain")
    if "RM_SumpTarRainLock" in t["rutsump"] or "RM_SumpTarRainLock" in t["wiring"]:
        out.append("RUT_Sump can reach the tar-rain lock")
    camp = ET.fromstring(t["campaign"].encode())
    op = camp.find("Operation")
    m = op.find("match") if op is not None else None
    if (op is None or op.get("Class") != "PatchOperationFindMod" or [x.text for x in op.find("mods")] != [json.loads(t["compose"])["about"]["name"]]
            or m is None or m.get("Class") != "PatchOperationReplace"
            or 'BiomeDef[defName="RM_TheSump"]' not in (m.findtext("xpath") or "")
            or "RM_SumpTarRainLock" not in (m.findtext("xpath") or "")
            or (m.findtext("value/li") or "").strip() != "RUT_SumpDuskLock"):
        out.append("campaign patch does not swap RM_TheSump back to RUT_SumpDuskLock")
    comp = json.loads(t["compose"])
    if "TheSump" not in [e if isinstance(e, str) else e.get("source") for e in comp["entries"]]:
        out.append("TheSump is no longer composed into the biomes mod: the campaign FindMod targets the wrong mod")
    if "mandrake.rm.environmentalhazards</packageId>" not in t["about"].split("</modDependencies>")[0]:
        out.append("environmentalhazards is not a hard dependency")
    mod = t["mod"]
    for f, d in (("tarRainEnabled", "true"), ("tarRainFrequency", "1f"), ("tarRainIntensity", "1f")):
        if not re.search(r"public static \w+ %s = %s;" % (f, d), mod):
            out.append("setting %s missing or default != %s" % (f, d))
        if 'Scribe_Values.Look(ref %s, "%s", %s, true)' % (f, f, d) not in mod:
            out.append("setting %s not scribed" % f)
    for k in ('Register("Sump.tarRain"', 'RegisterScale("Sump.tarRainFrequency"', 'RegisterScale("Sump.tarRainIntensity"'):
        if k not in mod:
            out.append("mod does not %s" % k)
    if mod.find("tarRainEnabled = true") > mod.find("shippedDefaults = SnapshotDefaults()"):
        out.append("tar-rain fields initialise after shippedDefaults (reset would read zeros)")
    return out


def main():
    t = {k: open(v, encoding="utf-8").read() for k, v in P.items()}
    f = findings(t)
    check("shipped tree: tar rain in the mod biome, never in the campaign", not f, f)

    def red(name, key, old, new):
        m = dict(t)
        check("sanity: mutant target present (%s)" % name, old in m[key])
        m[key] = m[key].replace(old, new, 1)
        check("mutant: " + name, findings(m) != [])

    red("biome back on the plain dusk lock", "biome", "<li>RM_SumpTarRainLock</li>", "<li>RUT_SumpDuskLock</li>")
    red("tar rain wets", "weather", "<rainRate>0</rainRate>", "<rainRate>1</rainRate>")
    red("campaign patch drops the swap", "campaign", "<li>RUT_SumpDuskLock</li>", "<li>RM_SumpTarRainLock</li>")
    red("RUT_Sump wired to tar rain", "wiring", "<li>RUT_SumpDuskLock</li>", "<li>RM_SumpTarRainLock</li>")
    red("setting defaults off", "mod", "tarRainEnabled = true;", "tarRainEnabled = false;")
    red("gate key drift", "lock", "<burstGateKey>Sump.tarRain</burstGateKey>", "<burstGateKey>Sump.tar</burstGateKey>")
    if FAILS:
        print("\n%d sump tar rain check(s) FAILED" % len(FAILS))
        return 1
    print("\nall sump tar rain checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
