"""Make big animals yield absurd amounts of meat and bone.

THE RULE (owner, 2026-08-11): a truly enormous kill should leave you swimming
in meat. Meat and bone scale with the SQUARE of bodySize; leather stays linear.

    meat   proportional to bodySize^2
    bone   proportional to bodySize^2
    leather            bodySize^1      <- unchanged, see below

The leather exception is the owner's surface-area-versus-volume argument: a hide
is a sheet wrapped around a creature, so it grows far more slowly than the meat
inside it. Vanilla already does this -- LeatherAmount carries StatPart_BodySize
and nothing else -- so **leather needs no patch at all** and this script
deliberately emits none. Read the stat before writing a patch for it.

HOW THE ENGINE COMPUTES YIELD (Core Stats_Pawns_General.xml, decompiled parts):

    MeatAmount : defaultBaseValue 140, parts include StatPart_BodySize
    BoneAmount : defaultBaseValue  50, parts include StatPart_BodySize
                 (Rim of Madness - Bones, sihv.rombonesport)

    public class StatPart_BodySize : StatPart {
        public override void TransformValue(StatRequest req, ref float val) {
            if (TryGetBodySize(req, out var bodySize)) val *= bodySize;
        }
    }

So the engine ALREADY multiplies by bodySize exactly once. To reach bodySize^2
we write a per-animal base of `unit * bodySize` and let StatPart_BodySize supply
the second factor. Writing `unit * bodySize^2` would give bodySize^3 and is the
easiest mistake to make here.

    statBases/MeatAmount = 140 * bodySize   ->  final 140 * bodySize^2
    statBases/BoneAmount =  50 * bodySize   ->  final  50 * bodySize^2

WHAT IS DELIBERATELY LEFT ALONE

  * bodySize <= 1.0. The brief was "huge animals", not "rebalance rabbits".
    Squaring a fraction SHRINKS it, so an unguarded rule would quietly nerf
    every small animal in the game. Below 1.0 the two curves cross and the
    change would be a nerf disguised as a buff.
  * Anything already at MeatAmount 0 or BoneAmount 0. Mechanoids, insects and
    the three arthropods Rim of Madness explicitly declares boneless
    (Arthropleura, Meganeura, Pulmonoscorpius) stay at zero. Multiplying zero
    is harmless but emitting the operation is noise, and re-adding a stat some
    other mod deliberately stripped is worse than noise.
  * Defs that exist only at runtime. You cannot patch XML that was never on
    disk, so every target is checked against the offline inventory first.

BoneAmount also carries a postProcessCurve -- (0,0) (5,14) (40,40)
(100000,100000) -- which is roughly 1:1 above 40 and therefore does not fight
this. It compresses only the very small end, which we are not touching anyway.
"""
import collections
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from def_inventory import build, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA
from def_diff import iter_live_defs
from refresh import D_DUMP
from patch_provenance import guard

OUTDIR = os.path.join(ROOT, "src", "Jawa", "Jawa_Doctrine", "Patches")
NL = "\n"

def xesc(s):
    """Escape text destined for an XML node.

    Mod names go into <mods><li>...</li></mods> verbatim, and at least one
    installed mod is literally called "Big and Small - Genes & More". A raw &
    is not well-formed XML, so the whole patch file failed to parse and every
    operation in it was lost -- 1311 of them, silently, because the file never
    reached the def loader at all.
    """
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def cesc(s):
    """Escape text destined for an XML COMMENT.

    Different rules: & is legal inside a comment, but '--' terminates it early
    and corrupts the file. Animal labels are author-supplied and can contain
    anything.
    """
    return s.replace("--", "––")


EXPONENT = 2.0          # meat and bone; see the header before changing this
MEAT_UNIT = 140.0       # Core MeatAmount defaultBaseValue
BONE_UNIT = 50.0        # Rim of Madness BoneAmount defaultBaseValue
MIN_BODY_SIZE = 1.0     # below this we do nothing at all

# Values here are constants times a body size, never a function of the current
# yield, so this generator cannot eat its own output the way the armoury one
# could. The banner still prints; the point is that somebody asked.
guard(D_DUMP, "gen_megafauna_yield (constants x bodySize; safe on any dump)")

ds = build(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA, types=("ThingDef",))
patchable = {r.defName for r in ds.of_type("ThingDef") if r.defName}

ops = collections.defaultdict(list)
skipped = collections.Counter()
rows = []
harvest = {"milk": [], "fur": []}

# field name, exponent, xpath leaf. The predicate matches on the CHILD ELEMENT
# rather than on Class=, because mods declare these comps under their own
# namespaces and a Class= predicate would silently miss them.
HARVEST_SPEC = {
    "milk": ("milkAmount", 2.0),
    "fur": ("woolAmount", 1.0),
}

for d in iter_live_defs(os.path.join(D_DUMP, "defs", "ThingDef.json")):
    dn = d.get("defName")
    f = d.get("fields") or {}
    race = f.get("race")
    if not isinstance(race, dict) or (d.get("is") or {}).get("corpse"):
        continue
    bs = race.get("baseBodySize")
    if not isinstance(bs, (int, float)):
        continue

    if bs <= MIN_BODY_SIZE:
        skipped["small (bodySize <= %.1f)" % MIN_BODY_SIZE] += 1
        continue
    if race.get("fleshType") == "Mechanoid" or race.get("Humanlike"):
        skipped["mechanoid or humanlike"] += 1
        continue
    if dn not in patchable:
        # Runtime-generated def with no XML on disk. Nothing to patch.
        skipped["not in offline XML"] += 1
        continue

    sb = {s.get("stat"): s.get("value")
          for s in (f.get("statBases") or []) if isinstance(s, dict)}
    mod = d.get("modName") or "?"

    for stat, unit in (("MeatAmount", MEAT_UNIT), ("BoneAmount", BONE_UNIT)):
        cur = sb.get(stat)
        if cur == 0:
            skipped["%s already zero (left alone)" % stat] += 1
            continue
        new_base = unit * (bs ** (EXPONENT - 1.0))
        parent = '/Defs/ThingDef[defName="%s"]/statBases' % dn
        ops[mod].append(
            "        <!-- %s %s: bodySize %.2f, base %.0f, yields %.0f -->"
            % (cesc(dn), stat, bs, new_base, unit * (bs ** EXPONENT)) + NL +
            '        <li Class="PatchOperationConditional">' + NL +
            "          <xpath>%s/%s</xpath>" % (parent, stat) + NL +
            '          <match Class="PatchOperationReplace">' + NL +
            "            <xpath>%s/%s</xpath>" % (parent, stat) + NL +
            "            <value><%s>%.0f</%s></value>" % (stat, new_base, stat) + NL +
            "          </match>" + NL +
            '          <nomatch Class="PatchOperationAdd">' + NL +
            "            <xpath>%s</xpath>" % parent + NL +
            "            <value><%s>%.0f</%s></value>" % (stat, new_base, stat) + NL +
            "          </nomatch>" + NL +
            "        </li>" + NL)

    rows.append((bs, dn, (d.get("label") or "")[:26],
                 MEAT_UNIT * bs, MEAT_UNIT * (bs ** EXPONENT)))

    # --- milk and fur -----------------------------------------------------
    # These are COMP PROPERTIES, not stats. CompProperties_Milkable.milkAmount
    # and CompProperties_Shearable.woolAmount are flat authored numbers that
    # StatPart_BodySize never touches, so unlike meat the engine contributes NO
    # factor and the exponent must be written in full.
    #
    #   milk (a volume harvested from a body)  -> bodySize^2
    #   fur  (a pelt, same surface-area logic as leather) -> bodySize^1
    #
    # The unit for each is the MEDIAN of amount/bodySize^exponent across every
    # animal that has the comp, computed below. That anchors the typical animal
    # on its existing value and makes the curve pivot around it, rather than
    # inventing a constant. It does flatten deliberate outliers -- the woolly
    # mammoth's hand-authored 500 wool is the extreme -- so the biggest movers
    # are printed at the end for review.
    for c in (f.get("comps") or []):
        if not isinstance(c, dict):
            continue
        if isinstance(c.get("milkAmount"), (int, float)) and c["milkAmount"] > 0:
            harvest["milk"].append((bs, dn, mod, c["milkAmount"]))
        if isinstance(c.get("woolAmount"), (int, float)) and c["woolAmount"] > 0:
            harvest["fur"].append((bs, dn, mod, c["woolAmount"]))

# --- emit milk and fur, anchored on the median animal ----------------------
movers = []
for kind, (field, expo) in sorted(HARVEST_SPEC.items()):
    items = harvest[kind]
    if not items:
        continue
    ratios = sorted(amt / (bs ** expo) for bs, _dn, _m, amt in items)
    unit = ratios[len(ratios) // 2]          # median; robust to the outliers
    print("  %-5s: %3d animals, exponent %.0f, median unit %.2f"
          % (kind, len(items), expo, unit))
    for bs, dn, mod, old in items:
        new = unit * (bs ** expo)
        if abs(new - old) < 0.5:
            continue                          # already right; do not churn
        parent = ('/Defs/ThingDef[defName="%s"]/comps/li[%s]' % (dn, field))
        ops[mod].append(
            "        <!-- %s %s: bodySize %.2f, %.0f -> %.0f -->"
            % (cesc(dn), field, bs, old, new) + NL +
            '        <li Class="PatchOperationReplace">' + NL +
            "          <xpath>%s/%s</xpath>" % (parent, field) + NL +
            "          <value><%s>%.0f</%s></value>" % (field, new, field) + NL +
            "        </li>" + NL)
        movers.append((abs(new - old), kind, dn, bs, old, new))

os.makedirs(OUTDIR, exist_ok=True)
out = os.path.join(OUTDIR, "MegafaunaYield.xml")
with io.open(out, "w", encoding="utf-8") as fh:
    fh.write('<?xml version="1.0" encoding="utf-8"?>' + NL)
    fh.write("<!-- Megafauna butcher yield: meat and bone scale with bodySize^%g." % EXPONENT + NL)
    fh.write("     GENERATED by src/Jawa/Jawa_Doctrine/Source/gen_megafauna_yield.py" + NL)
    fh.write("     Do not hand-edit; re-run the generator." + NL + NL)
    fh.write("     The engine multiplies by bodySize once via StatPart_BodySize, so each" + NL)
    fh.write("     base written here is unit * bodySize and the final yield is" + NL)
    fh.write("     unit * bodySize^%g. Leather is deliberately untouched: LeatherAmount" % EXPONENT + NL)
    fh.write("     is already linear in bodySize, which is the intended surface-area rule." + NL)
    fh.write("     Only bodySize > %.1f is affected. -->" % MIN_BODY_SIZE + NL)
    fh.write("<Patch>" + NL)
    n = 0
    for mod, oplist in sorted(ops.items()):
        n += len(oplist)
        fh.write(NL + '  <Operation Class="PatchOperationFindMod">' + NL)
        fh.write("    <mods><li>" + xesc(mod) + "</li></mods>" + NL)
        fh.write('    <match Class="PatchOperationSequence">' + NL)
        fh.write("      <operations>" + NL)
        for o in oplist:
            fh.write(o)
        fh.write("      </operations>" + NL)
        fh.write("    </match>" + NL + "  </Operation>" + NL)
    fh.write(NL + "</Patch>" + NL)

print("  %-30s %4d operations in %d mod groups" % ("MegafaunaYield.xml", n, len(ops)))
print("  skipped: %s" % dict(skipped))
rows.sort(reverse=True)
print()
print("  %-28s %-7s %-10s %s" % ("largest creatures", "bodySz", "meat now", "meat after"))
for bs, dn, lab, now, new in rows[:12]:
    print("  %-28s %-7.2f %-10.0f %.0f" % (lab or dn, bs, now, new))

movers.sort(reverse=True)
print()
print("  biggest milk/fur movers (review these; the median anchor flattens outliers):")
print("  %-6s %-26s %-7s %-8s %s" % ("kind", "defName", "bodySz", "was", "now"))
for _delta, kind, dn, bs, old, new in movers[:10]:
    print("  %-6s %-26s %-7.2f %-8.0f %.0f" % (kind, dn, bs, old, new))
