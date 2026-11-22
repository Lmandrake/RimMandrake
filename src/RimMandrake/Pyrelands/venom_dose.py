#!/usr/bin/env python3
"""The flamefang venom's numbers, read from the SHIPPED defs and patches, and the one-bite course they make.

RIMMANDRAKE_TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY. Visit 3 (game b, 2026-11-21) measured one untended bite at
0.434 RM_FlamefangVenom and a death by day 2. The offline models had assumed 0.2 a bite (power 10 x 0.02), but the fauna
normalization (src/RimUtinni/UtinniPatches/Patches/FaunaNorm_Law3_Damage.xml, Law 3) replaces the venom-fangs' power
10 with 22.5, so the live dose was 22.5 x 0.02 = 0.45. This module reads the power AFTER that patch, so no model here
can drift from the game again.

Vanilla's own arithmetic (RimWorld 1.6 source, read through RimSage):
  bite damage   Verb_MeleeAttackDamage: power x GetDamageFactorFor (mouth efficiency <= 1, life stage factor, the
                MeleeDamageFactor stat) x Rand.Range(0.8, 1.2); armour only lowers it.
  dose          Pawn_HealthTracker: totalDamageDealt x severityPerDamageDealt, / victim body size when
                victimSeverityScalingByInvBodySize.
  rise          HediffComp_Immunizable: severityPerDayNotImmune x severityPerDayNotImmuneRandomFactor (props range,
                default 1..1) until immunity reaches 1.
  immunity      ImmunityRecord.ImmunityChangePerTick: immunityPerDaySick x ImmunityGainSpeed x Lerp(0.8, 1.2, a
                per-instance seeded value).
So one untended bite peaks at dose + rise / (immunityPerDaySick x ImmunityGainSpeed x f), f in 0.8..1.2.

  python3 venom_dose.py        prints the numbers it read and where it read them
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))           # src/RimMandrake
ROOT_SRC = os.path.normpath(os.path.join(SRC, ".."))       # src/ (RimUtinni patches live beside RimMandrake)
DEFS = os.path.join(HERE, "Defs")
RACE, CAPACITY, DAMAGE, HEDIFF = "RM_Flamefang", "RM_FlamefangBite", "RM_FlamefangVenomBite", "RM_FlamefangVenom"

DAMAGE_RANDOM = (0.8, 1.2)      # Verb_MeleeAttackDamage: Rand.Range(num * 0.8f, num * 1.2f)
IMMUNITY_RANDOM = (0.8, 1.2)    # ImmunityRecord: Mathf.Lerp(0.8f, 1.2f, Rand.Value), seeded per hediff instance


class DefError(Exception):
    """A number the model needs is absent or ambiguous in the shipped files: the model cannot answer."""


def _num(el, tag, default=None):
    v = el.find(tag)
    if v is None or v.text is None:
        if default is None:
            raise DefError("%s has no <%s>" % (el.findtext("defName"), tag))
        return default
    return float(v.text)


def _def(kind, name, root):
    for path in glob.glob(os.path.join(root, "**", "*.xml"), recursive=True):
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue
        for el in tree.getroot().iter(kind):
            if el.findtext("defName") == name:
                return el, path
    raise DefError("%s %s not found under %s" % (kind, name, root))


def _patched_power(index, patch_root):
    """The value every PatchOperationReplace on RM_Flamefang's tools/li[index]/power sets, with its file. None when no
    patch touches it; DefError when two patches disagree (the load order would decide, and the model cannot)."""
    want = '/Defs/ThingDef[defName="%s"]/tools/li[%d]/power' % (RACE, index)
    found = {}
    for path in glob.glob(os.path.join(patch_root, "**", "Patches", "**", "*.xml"), recursive=True):
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if want not in text:
            continue
        for op in ET.fromstring(text).iter():
            if op.get("Class") == "PatchOperationReplace" and (op.findtext("xpath") or "").strip() == want:
                v = op.find("value/power")
                if v is not None:
                    found[float(v.text)] = os.path.relpath(path, patch_root)
    if len(found) > 1:
        raise DefError("patches disagree on %s: %r" % (want, found))
    return next(iter(found.items())) if found else None


def _one_comp(hd, cls):
    comps = [c for c in hd.findall("comps/li") if c.get("Class") == cls]
    if len(comps) != 1:
        raise DefError("%s has %d %s comps, not one" % (hd.findtext("defName"), len(comps), cls))
    return comps[0]


def read(defs_root=DEFS, patch_root=ROOT_SRC):
    """Every venom number, from the shipped defs and the patches over them -> dict (with 'sources')."""
    race, race_path = _def("ThingDef", RACE, defs_root)
    tools = race.find("tools")
    index = None
    for i, li in enumerate(tools.findall("li"), 1):
        if CAPACITY in [c.text for c in li.findall("capacities/li")]:
            index, tool = i, li
    if index is None:
        raise DefError("%s has no tool with capacity %s" % (RACE, CAPACITY))
    base_power = _num(tool, "power")
    patched = _patched_power(index, patch_root)
    power = patched[0] if patched else base_power
    dmg, dmg_path = _def("DamageDef", DAMAGE, defs_root)
    add = [li for li in dmg.findall("additionalHediffs/li") if li.findtext("hediff") == HEDIFF]
    if len(add) != 1:
        raise DefError("%s injects %s %d times, not once" % (DAMAGE, HEDIFF, len(add)))
    hd, hd_path = _def("HediffDef", HEDIFF, defs_root)
    imm = _one_comp(hd, "HediffCompProperties_Immunizable")
    rf = imm.find("severityPerDayNotImmuneRandomFactor")
    rise_factor = (1.0, 1.0) if rf is None else tuple(float(x) for x in re.split(r"~", rf.text.strip()))
    stages = sorted(float(li.findtext("minSeverity") or 0) for li in hd.findall("stages/li")
                    if (li.findtext("lifeThreatening") or "").strip() == "true")
    return {
        "power": power, "base_power": base_power, "tool_index": index,
        "per_damage": _num(add[0], "severityPerDamageDealt"),
        "inv_body_size": (add[0].findtext("victimSeverityScalingByInvBodySize") or "").strip() == "true",
        "rise": _num(imm, "severityPerDayNotImmune"),
        "rise_factor": rise_factor if len(rise_factor) == 2 else (rise_factor[0], rise_factor[0]),
        "immunity": _num(imm, "immunityPerDaySick"),
        "fall": _num(imm, "severityPerDayImmune"),
        "tended": _num(_one_comp(hd, "HediffCompProperties_TendDuration"), "severityPerDayTended"),
        "lethal": _num(hd, "lethalSeverity"),
        "life_threatening": stages[0] if stages else None,
        "sources": {"power": patched[1] if patched else os.path.relpath(race_path, ROOT_SRC),
                    "dose": os.path.relpath(dmg_path, ROOT_SRC), "course": os.path.relpath(hd_path, ROOT_SRC)},
    }


def dose(v, damage_roll=1.0, armour=1.0, attacker_factor=1.0, victim_body_size=1.0):
    """The venom one landed bite injects: power x attacker factor x the 0.8..1.2 roll x what armour lets through."""
    d = v["power"] * attacker_factor * damage_roll * armour * v["per_damage"]
    return d / victim_body_size if v["inv_body_size"] else d


def days_to_immune(v, gain_speed=1.0, f=1.0):
    return 1.0 / (v["immunity"] * gain_speed * f)


def peak(v, d, gain_speed=1.0, f=1.0, rise_factor=1.0):
    """The highest severity one untended bite reaches: it rises until immunity completes, then falls."""
    return d + v["rise"] * rise_factor * days_to_immune(v, gain_speed, f)


def main():
    v = read()
    print("venom-fangs power %.4g (base %.4g; from %s), %.4g severity per damage -> nominal dose %.4f"
          % (v["power"], v["base_power"], v["sources"]["power"], v["per_damage"], dose(v)))
    print("rise %+.3g/day untended, immunity %.3g/day (%.2f days nominal), lethal %.3g, life-threatening from %s"
          % (v["rise"], v["immunity"], days_to_immune(v), v["lethal"], v["life_threatening"]))
    print("one untended bite, nominal: peak %.3f" % peak(v, dose(v)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
