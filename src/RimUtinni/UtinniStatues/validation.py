"""validation.py -- first script for Jawa Utinni Statues (mandrake.rut.utinnistatues).

UTINNI_STATUES_SKELETON_BUILD_1 (statue_mods_spec.md §3 step 1). Walk:
design/validation_walks/RimUtinni/UtinniStatues.md. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run UtinniStatues

Environment: minimal + every DLC + this mod. The dedicate proof goes through jawa/static_call
(RUT_Building_Statue.ProofDedicate), which needs the JawaBench companion that carries static_call.
"""
import os
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
suite = Suite("UtinniStatues")
suite.toggles = ["statuesCraftable", "shkaarIdolBurns", "sumpgasFuelsIdol"]

TIERS = ("RUT_StatueSmall", "RUT_Statue", "RUT_StatueGrand")
FLAME_DEF = "RUT_StatueGrand_Shkaar"
SETTINGS_TYPE = "RimMandrake.Utinni.UtinniStatues.UtinniStatuesSettings"
NEEDLES = ("mandrake.rut.utinnistatues", "RUT_Statue", "RUT_CompStatuePicker", "CompProperties_StatuePicker",
           "RUT_Building_Statue", "UtinniStatues")


def _dedicate(t, x, z, carving):
    r = t.bridge_call("jawa/static_call", type="RimMandrake.Utinni.UtinniStatues.RUT_Building_Statue",
                      method="ProofDedicate", args="current|%d,%d|%s" % (x, z, carving))
    return str((r or {}).get("result", "")) or "no result: %r" % (r,)


@suite.chain("load_clean")
def load_clean(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("all_defs_resolve", beyond_toggle=True):
        want = ["ThingDef/%s" % d for d in TIERS + (FLAME_DEF,)] + ["RecipeDef/Make_%s" % d for d in TIERS]
        r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName")
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("get_defs failed: %r" % r)
            if r.get("notFound"):
                raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


@suite.chain("dedicate")
def dedicate(t):
    x, z = t.anchor
    t.clear_area(size=12)
    t.bridge_call("jawa/spawn_batch", ops="RUT_Statue:%d,%d;RUT_StatueGrand:%d,%d" % (x, z, x + 4, z), stuff="Steel")
    with t.component("statue_takes_the_chosen_god", beyond_toggle=True):
        text = _dedicate(t, x, z, "RUT_Idol_Shkaar")
        if t._guard() and not (text.startswith("LABEL idol of Sh'kaar") and "HONOURS Sh'kaar the All-Searing" in text):
            raise ExpectationFailed("dedicating a statue to Sh'kaar did not take: %s" % text)
    with t.component("rededicate_changes_it", beyond_toggle=True):
        text = _dedicate(t, x, z, "RUT_Idol_Rekko")
        if t._guard() and not text.startswith("LABEL idol of Rekko"):
            raise ExpectationFailed("rededicating to Rekko did not change the statue: %s" % text)
    with t.component("tier_offers_only_its_own_size", beyond_toggle=True):
        text = _dedicate(t, x, z, "RUT_Relief_Crawler")
        if t._guard() and not text.startswith("REFUSED"):
            raise ExpectationFailed("a person-sized statue accepted the 2x2 crawler relief: %s" % text)
    with t.component("grand_takes_the_crawler", beyond_toggle=True):
        text = _dedicate(t, x + 4, z, "RUT_Relief_Crawler")
        if t._guard() and not text.startswith("LABEL relief of the Crawler"):
            raise ExpectationFailed("the grand statue did not take the crawler relief: %s" % text)


# SHKAAR_FLAME_IDOL_BUILD_1 (spec §2.5): dedicating a stone/metal grand to Sh'kaar rebuilds it as the burning idol;
# rededicating it makes it cold again; with shkaarIdolBurns OFF it stays cold. Not proven here: the flame drawing,
# the glow going dark without fuel, the Sumpgas filter in the campaign (first poke: refuel it, screenshot).
@suite.chain("shkaar_idol")
def shkaar_idol(t):
    x, z = t.anchor
    t.clear_area(size=12)
    t.bridge_call("jawa/spawn_batch", ops="RUT_StatueGrand:%d,%d" % (x, z), stuff="Steel")
    with t.component("shkaar_grand_becomes_the_burning_idol", toggle="shkaarIdolBurns"):
        text = _dedicate(t, x, z, "RUT_Idol_Shkaar_Grand")
        if t._guard() and ("DEF %s" % FLAME_DEF not in text or "FUEL True" not in text):
            raise ExpectationFailed("a steel grand dedicated to Sh'kaar is not the fuelled idol: %s" % text)
    with t.component("rededicated_idol_goes_cold", toggle="shkaarIdolBurns"):
        text = _dedicate(t, x, z, "RUT_Idol_Ohm_Grand")
        if t._guard() and ("DEF RUT_StatueGrand |" not in text or "FUEL False" not in text):
            raise ExpectationFailed("the idol rededicated to Ohm did not go back to the cold grand: %s" % text)
    with t.component("burning_off_stays_cold", toggle="shkaarIdolBurns"):
        t.set_setting(SETTINGS_TYPE, {"shkaarIdolBurns": False})
        try:
            text = _dedicate(t, x, z, "RUT_Idol_Shkaar_Grand")
        finally:
            t.set_setting(SETTINGS_TYPE, {"shkaarIdolBurns": True})
        if t._guard() and "DEF RUT_StatueGrand |" not in text:
            raise ExpectationFailed("shkaarIdolBurns OFF but the grand became the burning idol: %s" % text)


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RUT_UtinniStatues.xml")).getroot()
    tiers = {e.findtext("defName"): e for e in root if e.tag == "ThingDef"}
    if set(tiers) != set(TIERS + (FLAME_DEF,)):
        bad.append("tiers parsed %s, want %s" % (sorted(tiers), sorted(TIERS + (FLAME_DEF,))))
    ids = []
    for dn, e in tiers.items():
        if dn == FLAME_DEF:
            if e.find(".//li[@Class='CompProperties_Refuelable']") is None or e.find("recipeMaker") is not None:
                bad.append("%s must be fuelled and never carved directly" % dn)
            continue
        if e.findtext("thingClass") != "RimMandrake.Utinni.UtinniStatues.RUT_Building_Statue":
            bad.append("%s thingClass is not RUT_Building_Statue" % dn)
        ids += [li.findtext("id") for li in e.findall(".//carvings/li")]
    if len(ids) != 16 or len(set(ids)) != 16:
        bad.append("expected 16 distinct carvings (spec §1.2), parsed %d (%d distinct)" % (len(ids), len(set(ids))))
    src = open(os.path.join(HERE, "Source", "RimMandrake.Utinni.UtinniStatues.csproj"), encoding="utf-8").read()
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in src:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = open(os.path.join(HERE, "Source", "UtinniStatuesMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if '"%s"' % f not in mod:
            bad.append("toggle %s is not Scribed" % f)
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
