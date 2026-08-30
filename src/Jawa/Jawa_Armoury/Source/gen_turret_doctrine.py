"""Generate the turret damage-doctrine patch: (squares)^2 x personal anchor.

Owner's doctrine (canon.yml turrets.damage_doctrine, 2026-08-29, verbatim):
"a turret's damage is (# squares)^2 x (largest similar personal weapon)".

Rulings of the 2026-08-29 bench sitting that shape every number here:
  1. PER-VOLLEY: a turret's full burst delivers anchor x multiplier;
     per-shot = volley / burstShotCount.
  2. BOTH DIRECTIONS: over-doctrine turrets come down.
  3. BLAST-CLASS (explosive ordnance): volley = anchor x squares, blast
     radius x side (damage*area = squares^2 total); radius capped at 14.9,
     remainder spills back into damage.
  4. FIAT ANCHORS: living/bio = 25, tesla arc = 20, gravitic = 3 (measured).
     Gravitic shockwaves keep their own radius and use the direct rule.
  5. TRAPS (the three Trade Moot columns) may sit up to 2x doctrine — "traps
     ... cannot broadcast at range" (owner, verbatim). Clamp, don't raise.
  6. ARCHOTECH (Turret_AutoChargeBlaster_OP) allowed 4x doctrine (owner).
  7. Ion anchor is the heavy ion rifle (9), not the wrist blaster (owner).
  8. CONTROL rows (stun/EMP) scale LINEAR (anchor x squares) — durations
     don't square well. Proposed by BENCH, unopposed.
  9. Big-burst beams keep doctrine volley by cutting burstShotCount, not by
     shrinking per-shot damage to noise. BENCH default, flagged for veto.

SUPERSESSION: this file owns every projectile fired by a canon-roster turret.
gen_armoury_patch.py's emplacement/artillery/turbolaser rungs (2026-08-14) are
superseded for those projectiles. Until its next regen, patch filename order
(Armoury_* < Turrets_*) makes this file's writes win — both apply, ours last.

Worksheet with the full derivation: design/Jawa/worldbuilding/review/
turret_normalization_v1.md. Roster: canon.yml turrets.official_roster.

Shared-projectile trap (armoury lesson #1): a projectile or DamageDef used by
anything that is NOT this turret's gun is never patched in place — it gets a
cloned def (Jawa_TD_<turret>) and the gun is retargeted at the clone.

Declarer trap (armoury lesson #2): every in-place write goes to the def's OWN
raw element. A node the def does not declare itself is Added into its own
<projectile>, never written onto a shared ancestor. Anything else is a loud
skip, printed at the end.

EXEMPT by mechanism (no number exists to write, doctrine cannot reach them
offline): VFES_Complex_HeavyIncineratorComplex (C# fire spew).
EXEMPT utility: foam x2, searchlight, drill, gravlite interceptor.
HOLD for the bench: VGE_AnticraftCaster (gravship showpiece).
"""
import io
import os
import sys
import xml.etree.ElementTree as ET


def _find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")) or \
           os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("no repo root above %s" % start)
        d = parent


_REPO_ROOT = _find_repo_root(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src", "RimMandrake", "Utils"))
from def_inventory import build as build_offline, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA  # noqa: E402

OUT = os.path.join(_REPO_ROOT, "src", "Jawa", "Jawa_Armoury", "Patches",
                   "Turrets_DamageDoctrine.xml")
# VEF flamethrower streams live in their own def type; without it in the scan
# two flame turrets read as "projectile not found" (found that the hard way).
DEF_TYPES = ("ThingDef", "DamageDef", "VEF.Weapons.ExpandableProjectileDef")
VANILLA = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")

# ---------------------------------------------------------------- the plan
# defName: (volley, radius, burst_override, retype)
#   volley = total damage per burst after every ruling above
#   radius = new explosionRadius or None (None = leave)
#   burst_override = new burstShotCount or None
#   retype = new damageDef or None
PLAN = {
    # --- 1x1 (mult 1) ---
    "AB_Turret_Propane":            (33,   None, None, None),
    "DetColumnMod":                 (250,  None, None, None),   # trap <=280; 250 stands
    "EMPColumnMod":                 (40,   None, None, "EMP"),  # trap ceiling 2x20; owner: ion effect
    "FlameColumnMod":               (66,   None, None, None),   # trap clamp 120 -> 2x33
    "OuterRim_LightIonCannon":      (9,    None, None, None),   # ion anchor 9
    "OuterRim_LightLaserCannon_Corellia":  (69, None, None, None),
    "OuterRim_LightLaserCannon_Coruscant": (69, None, None, None),
    "OuterRim_LightLaserCannon_Tatooine":  (69, None, None, None),
    "OuterRim_PTowerTurret":        (69,   None, None, None),
    "Turret_AutoChargeBlaster_OP":  (240,  None, None, None),   # archotech 4x
    "Turret_BeamRepeater":          (64,   None, 8,    None),   # beam: burst 30 -> 8
    "VFEI2_Thornspitter":           (25,   None, None, None),
    "VFES_Turret_Flame":            (33,   None, None, None),   # Wildsteam keep
    # --- 2x2 (direct mult 16, blast mult 4, side 2) ---
    "AA_BlackDefiler":              (100,  7.8,  None, None),
    "DP_Automortar":                (560,  6.0,  None, None),
    "OuterRim_MediumLaserCannon":   (1104, None, None, None),
    "OuterRim_ProtonMortar":        (560,  11.8, None, None),
    "OuterRim_Turbolaser":          (1104, None, None, None),
    "RN2SWGun_EWeb_MG":             (1104, None, None, "OuterRim_Blaster"),
    "Turret_Atomiser":              (624,  None, None, None),
    "Turret_AutoChargeBlaster":     (960,  None, None, None),
    "Turret_AutoInferno":           (132,  4.8,  None, None),
    "Turret_AutoMortar":            (560,  5.8,  None, None),
    "Turret_GravBlaster":           (48,   None, None, None),   # shockwave: radius kept
    "Turret_RocketswarmLauncher":   (560,  5.8,  None, None),
    "Turret_Sludger":               (100,  None, None, None),   # control linear
    "Turret_Sniper":                (960,  None, None, None),
    "Turret_Vaporiser":             (624,  None, 30,   None),   # beam: burst 180 -> 30
    "Turret_Zapper":                (624,  None, None, None),
    "VFEI2_Thornworm":              (400,  None, None, None),
    "VFEI2_Vilelobber":             (100,  7.8,  None, None),
    "VFES_Turret_Ballista":         (800,  None, None, None),
    "VFES_Turret_ChargeRailgun":    (960,  None, None, None),   # kinetic stands (owner)
    "VFES_Turret_TeslaBlaster":     (80,   None, None, "EMP"),  # was Smoke 10
    # --- 3x3 (direct mult 81, blast mult 9, side 3) ---
    "GTbc_HugeGravBlaster":         (243,  None, None, None),   # shockwave: radius kept
    "OuterRim_AnaxesTurret":        (5589, None, None, None),
    "OuterRim_HeavyImperialTurbolaser": (5589, None, None, None),
    "OuterRim_HeavyIonCannon":      (729,  None, None, None),
    "OuterRim_HeavyLaserCannon":    (5589, None, None, None),
    "OuterRim_HeavyTurbolaser":     (5589, None, None, None),
    "OuterRim_ProtonArtillery":     (3188, 14.9, None, None),   # r7.9*3 capped, spill 2.53
    "VGE_GaussGun":                 (1260, 11.7, None, None),
    "VGE_HeavyChargeAnnihilator":   (4860, None, None, None),
    "VGE_JavelinPod":               (1260, 8.7,  None, None),
    # --- 5x5 (blast mult 25, side 5) ---
    "GTbc_GravRailArtillery":       (31219, 14.9, None, None),  # r8.9*5 capped, spill 8.92
    "VGE_MassDriver":               (9463,  14.9, None, None),  # r4.9*5 capped, spill 2.70
    # --- 7x7 (blast mult 49, side 7) ---
    "GTbc_TheSingularityCannon":    (72085, 14.9, None, None),  # r6.9*7 capped, spill 10.51
}

# Beam turrets: damage rides a DamageDef, not a projectile. (turret, volley):
#   BigLaserCannon: LaserCannonBeam is exclusive to its gun -> in-place write.
#   Graser complex: vanilla Beam is shared with a personal graser -> clone +
#   repoint beamDamageDef. Per-application = volley / burstShotCount.
BEAM_PLAN = {
    "BigLaserCannon":            3159,
    "VFES_Complex_GraserCannon": 3159,
}


def txt(el, path):
    n = el.find(path)
    return n.text.strip() if n is not None and n.text else None


def half_up(x):
    return max(1, int(x + 0.5))


class Emitter(object):
    """Collect (modName, comment, op-xml) triples; emit FindMod-grouped."""

    def __init__(self):
        self.by_mod = {}
        self.skips = []

    def add(self, mod, comment, op_xml):
        self.by_mod.setdefault(mod, []).append((comment, op_xml))

    def skip(self, turret, why):
        self.skips.append((turret, why))
        print("SKIP %s: %s" % (turret, why))

    def write(self, path):
        fh = io.StringIO()
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fh.write("<!-- Turret damage doctrine: (squares)^2 x personal anchor.\n"
                 "     GENERATED by src/Jawa/Jawa_Armoury/Source/gen_turret_doctrine.py.\n"
                 "     Do not hand-edit; re-run the generator. Derivation:\n"
                 "     design/Jawa/worldbuilding/review/turret_normalization_v1.md -->\n")
        fh.write("<Patch>\n")
        for mod in sorted(self.by_mod):
            ops = self.by_mod[mod]
            if True:
                fh.write('\n  <Operation Class="PatchOperationFindMod">\n')
                fh.write("    <mods><li>%s</li></mods>\n" % mod)
                fh.write('    <match Class="PatchOperationSequence">\n')
                fh.write("      <operations>\n")
                for comment, op in ops:
                    fh.write("        <!-- %s -->\n" % comment)
                    fh.write(op_indent(op, 8))
                fh.write("      </operations>\n")
                fh.write("    </match>\n")
                fh.write("  </Operation>\n")
        fh.write("</Patch>\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write(fh.getvalue())


def op_indent(op_xml, spaces, top=False):
    pad = " " * spaces
    lines = op_xml.rstrip().splitlines()
    if top:
        # promote <li Class=...> to <Operation Class=...> at Patch top level
        lines[0] = lines[0].replace("<li ", "<Operation ", 1)
        lines[-1] = lines[-1].replace("</li>", "</Operation>")
    return "\n".join(pad + l for l in lines) + "\n"


def op_replace(xpath, tag, value):
    return ('<li Class="PatchOperationReplace">\n'
            "  <xpath>%s</xpath>\n"
            "  <value><%s>%s</%s></value>\n"
            "</li>" % (xpath, tag, value, tag))


def op_add(xpath, tag, value):
    return ('<li Class="PatchOperationAdd">\n'
            "  <xpath>%s</xpath>\n"
            "  <value><%s>%s</%s></value>\n"
            "</li>" % (xpath, tag, value, tag))


def op_add_def(def_el, anchor_tag, anchor_name):
    """Add a whole def. Bare /Defs matches EVERY loaded XML file (the
    validator counted 8944), so anchor on the one file declaring the
    original def: /Defs[tag/defName="orig"]."""
    body = ET.tostring(def_el, encoding="unicode")
    return ('<li Class="PatchOperationAdd">\n'
            '  <xpath>/Defs[%s/defName="%s"]</xpath>\n'
            "  <value>%s</value>\n"
            "</li>" % (anchor_tag, anchor_name, body))


def clone_def(rec, new_name):
    """Standalone copy of a def from its inheritance-resolved element."""
    el = rec.element
    c = ET.fromstring(ET.tostring(el, encoding="unicode"))
    c.attrib.pop("Name", None)
    c.attrib.pop("ParentName", None)
    c.attrib.pop("Abstract", None)
    dn = c.find("defName")
    if dn is None:
        dn = ET.SubElement(c, "defName")
    dn.text = new_name
    return c


def set_child(el, path, tag, value):
    node = el.find(path)
    if node is None:
        return False
    ch = node.find(tag)
    if ch is None:
        ch = ET.SubElement(node, tag)
    ch.text = str(value)
    return True


def proj_write(em, ds, turret, proj_rec, per_shot, radius, retype, xtag=None):
    """In-place doctrine write on an EXCLUSIVE projectile's own element."""
    tag = xtag or "ThingDef"
    own = proj_rec.own
    dn = proj_rec.defName
    base = '/Defs/%s[defName="%s"]/projectile' % (tag, dn)
    if own.find("projectile") is None:
        em.skip(turret, "%s declares no <projectile> of its own" % dn)
        return
    mod = proj_rec.modName
    for leaf, val in (("damageAmountBase", per_shot),
                      ("explosionRadius", radius),
                      ("damageDef", retype)):
        if val is None:
            continue
        op = op_replace if own.find("projectile/" + leaf) is not None else op_add
        target = base + "/" + leaf if op is op_replace else base
        if op is op_replace:
            em.add(mod, "%s : %s -> %s" % (dn, leaf, val),
                   op_replace(base + "/" + leaf, leaf, val))
        else:
            em.add(mod, "%s : + %s %s" % (dn, leaf, val),
                   op_add(base, leaf, val))


def main():
    print("building offline inventory...", file=sys.stderr)
    ds = build_offline(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA, types=DEF_TYPES)

    # who fires which projectile (for the exclusivity check)
    users = {}
    for rec in ds.records:
        if rec.defType != "ThingDef" or rec.isAbstract:
            continue
        v = rec.element.find("verbs")
        if v is None:
            continue
        for li in v.findall("li"):
            pj = txt(li, "defaultProjectile")
            if pj:
                users.setdefault(pj, set()).add(rec.defName)

    em = Emitter()

    for turret, (volley, radius, burst_override, retype) in sorted(PLAN.items()):
        trec = ds.get("ThingDef", turret)
        if trec is None:
            em.skip(turret, "turret def not found offline")
            continue
        gun = txt(trec.element, "building/turretGunDef")
        grec = ds.get("ThingDef", gun) if gun else None
        if grec is None:
            em.skip(turret, "gun %r not found" % gun)
            continue
        gverbs = grec.own.find("verbs")
        if gverbs is None:
            em.skip(turret, "gun %s does not declare its own verbs" % gun)
            continue
        vli = gverbs.findall("li")[0]
        burst = int(txt(vli, "burstShotCount") or 1)
        pj = txt(vli, "defaultProjectile")
        if not pj:
            em.skip(turret, "gun %s has no defaultProjectile" % gun)
            continue
        prec = None
        ptag = None
        for t in ("ThingDef", "VEF.Weapons.ExpandableProjectileDef"):
            prec = ds.get(t, pj)
            if prec is not None:
                ptag = t
                break
        if prec is None:
            em.skip(turret, "projectile %s not found" % pj)
            continue

        eff_burst = burst_override or burst
        per_shot = half_up(float(volley) / eff_burst)

        if burst_override is not None:
            em.add(grec.modName,
                   "%s : burstShotCount %d -> %d (beam volley kept at doctrine)"
                   % (gun, burst, burst_override),
                   op_replace('/Defs/ThingDef[defName="%s"]/verbs/li[defaultProjectile="%s"]/burstShotCount' % (gun, pj),
                              "burstShotCount", burst_override))

        exclusive = not (users.get(pj, set()) - {gun})
        if exclusive:
            comment_val = "%s : volley %s = %s x %d" % (turret, volley, per_shot, eff_burst)
            proj_write(em, ds, turret, prec, per_shot, radius, retype, xtag=ptag)
        else:
            # clone, bake values in, retarget this gun only
            new_name = "Jawa_TD_" + turret
            c = clone_def(prec, new_name)
            ok = set_child(c, "projectile", "damageAmountBase", per_shot)
            if radius is not None:
                ok = set_child(c, "projectile", "explosionRadius", radius) and ok
            if retype is not None:
                ok = set_child(c, "projectile", "damageDef", retype) and ok
            if not ok:
                em.skip(turret, "clone of %s has no <projectile> node" % pj)
                continue
            # the clone must land in a mod that is certainly loaded when the
            # gun is: the GUN's own mod (vanilla guns -> unconditional)
            em.add(grec.modName,
                   "%s : clone %s -> %s (shared with %s)"
                   % (turret, pj, new_name,
                      ", ".join(sorted(users[pj] - {gun})[:4])),
                   op_add_def(c, ptag, pj))
            em.add(grec.modName,
                   "%s : retarget %s at %s" % (turret, gun, new_name),
                   op_replace('/Defs/ThingDef[defName="%s"]/verbs/li[defaultProjectile="%s"]/defaultProjectile' % (gun, pj),
                              "defaultProjectile", new_name))

    # ---- beams: damage rides a DamageDef ----
    # BigLaserCannon: LaserCannonBeam exclusive to LaserCannonTurret
    blc = ds.get("DamageDef", "LaserCannonBeam")
    if blc is not None and blc.own.find("defaultDamage") is not None:
        em.add(blc.modName,
               "BigLaserCannon : LaserCannonBeam defaultDamage -> %d (burst 1)"
               % BEAM_PLAN["BigLaserCannon"],
               op_replace('/Defs/DamageDef[defName="LaserCannonBeam"]/defaultDamage',
                          "defaultDamage", BEAM_PLAN["BigLaserCannon"]))
    else:
        em.skip("BigLaserCannon", "LaserCannonBeam DamageDef unwritable")
    # Graser: vanilla Beam shared -> clone + repoint (burst 8 applications)
    beam = ds.get("DamageDef", "Beam")
    gtop = ds.get("ThingDef", "VFES_ComplexGraserCannon_Top")
    if beam is not None and gtop is not None:
        per_app = half_up(BEAM_PLAN["VFES_Complex_GraserCannon"] / 8.0)
        c = clone_def(beam, "Jawa_TD_GraserBeam")
        dd = c.find("defaultDamage")
        if dd is None:
            dd = ET.SubElement(c, "defaultDamage")
        dd.text = str(per_app)
        em.add(gtop.modName,
               "graser complex : clone Beam -> Jawa_TD_GraserBeam %d/application x8 (Beam shared with Gun_BeamGraser)" % per_app,
               op_add_def(c, "DamageDef", "Beam"))
        em.add(gtop.modName,
               "graser complex : repoint beamDamageDef",
               op_replace('/Defs/ThingDef[defName="VFES_ComplexGraserCannon_Top"]/verbs/li[beamDamageDef="Beam"]/beamDamageDef',
                          "beamDamageDef", "Jawa_TD_GraserBeam"))
    else:
        em.skip("VFES_Complex_GraserCannon", "Beam DamageDef or gun top unresolvable")

    em.write(OUT)
    n = sum(len(v) for v in em.by_mod.values())
    print("wrote %s: %d ops across %d mods, %d skips"
          % (OUT, n, len(em.by_mod), len(em.skips)))


if __name__ == "__main__":
    main()
