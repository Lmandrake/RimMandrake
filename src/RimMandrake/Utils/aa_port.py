#!/usr/bin/env python3
"""aa_port.py -- Phase 0 step P2 for sarg.alphaanimals: port the plain (no AlphaBehavioursAndEvents) rostered
Alpha Animals creatures to owned RM_ defs.

    python3 src/RimMandrake/Utils/aa_port.py port [--apply] [--only A,B]   write the RM_ def files
    python3 src/RimMandrake/Utils/aa_port.py repoint [--apply]             swap donor roster rows for ours
    python3 src/RimMandrake/Utils/aa_port.py check                         every ported file: no donor name, no donor tex

Reuses donor_pack_port.py for the donor index and the offline patch baker, so a port is the creature the game
showed TODAY (rename patches, tolerance patches). Differences from donor_pack_port.py: tier is RM_, the home is
the roster's biome mod (not SWBestiary), the donor art is NEVER reused (texPath points at OUR final path; the
art is owed through artpipe), and donor-only support defs are ported only when they are not a sound, a leather or
another SPECIES (those are swapped for vanilla, PROVISIONAL, as the Abyss and Warscar ports did).
Item: ALPHA_ANIMALS_PHASE0_P2 (kickoff design/RimMandrake/biome_sprint_kickoff_2026-10-15.md 0.5.3).
"""
import argparse
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import donor_pack_port as P  # noqa: E402

REPO = P.REPO
SRC = P.SRC
DONOR = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1541721856"
VEF = "OskarPotocki.VanillaFactionsExpanded.Core"
PREFIXES = ("RM_", "RSW_", "RUT_")

# donor name -> (ours, home mod folder under src/RimMandrake, texPath stem or None for the default)
PORTS = {
    "AA_Aerofleet": ("RM_Bulloo", "TheForge", None),
    "AA_AngelMoth": ("RM_Dustveil", "TheRot", "RotSpecies/AngelMoth/AngelMoth"),
    "AA_BedBug": ("RM_BedBug", "Cauldron", None),
    "AA_BloodShrimp": ("RM_Zrrik", "Greentide", None),
    "AA_RaptorShrimp": ("RM_Sharpshrimp", "Miasma", None),
    "AA_CrystalMit": ("RM_CrystalMit", "Cauldron", None),
    "AA_GiantCrownedSilkie": ("RM_GiantCrownedSilkie", "Cauldron", None),
    "AA_Lockjaw": ("RM_Siezer", "Miasma", None),
    "AA_Metallovore": ("RM_Metallovore", "TheForge", None),
    "AA_ShockGoat": ("RM_Zhissa", "NightsideIce", None),
    "AA_Swarmling": ("RM_Chittik", "TheRot", None),
}
FOLDER = {"TheRot": "Fauna", "NightsideIce": "Fauna"}      # the folder each mod already keeps its creatures in
# species we do NOT port as a dependency of another: swapped for a vanilla def in exactly these text positions
SPECIES_SWAP = {
    "AA_Helixien": "Megaspider", "AA_BoulderMit": "Tortoise", "AA_RoughPlatedMonitor": "Iguana",
    "AA_OvergrownColossus": "Elephant", "AA_RaptorShrimp": "Megaspider",
}
# a donor item that is only decoration on the animal: dropped (leather) so no new art is owed for it
DROP_ELEMENTS = {("leatherDef", "Leather_Chitin"), ("leatherDef", "AA_Leather_Aerofleet"),
                 ("specificMeatDef", "AA_AerofleetMeat")}
USEMEAT_WHEN_DROPPED = {"AA_Aerofleet": "Megaspider"}
# SoundDef families by creature (vanilla Pawn_<fam>_<Angry|Wounded|Death|Call>)
SOUND_FAMILY = {"AA_GiantCrownedSilkie": "Peacock", "AA_ShockGoat": "Goat", "AA_Lockjaw": "Alligator",
                "AA_Plasmorph": "Thrumbo", "AA_BloodShrimp": "Megaspider", "AA_RaptorShrimp": "Megaspider"}
SOUND_SWAP = {"AA_FireSpit": "Shot_IncendiaryLauncher"}      # cast sound of the fire-spit ability
SOUND_TAGS = {"soundCast", "soundCastTail", "soundWounded", "soundDeath", "soundCall", "soundAngry"}
DROP_COMP_CLASSES = {"VEF.AnimalBehaviours.CompProperties_AttachEffecter"}   # falling-leaves effecter: cosmetic, 3 flecks of art
NAME_OVERRIDE = {"AA_AngelMothLarva": "RM_DustveilLarva"}
LABEL_OVERRIDE = {"RM_DustveilLarva": "dustveil larva"}
EGG_SHARED = True   # fertilized + unfertilized eggs of one creature share ONE texture (the donor shared AA_EggBeetle)
SKIP_TAGS_AS_REFS = {"modExtensions"}

_by = _abs = None
_onames = _otyped = None


def donor():
    global _by, _abs
    if _by is None:
        _by, _abs, _ = P.donor_index(DONOR)
    return _by, _abs


def ours_index():
    global _onames, _otyped
    if _onames is None:
        _onames, _otyped = P.our_names(), P.our_typed()
    return _onames, _otyped


def active():
    pids = set()
    import glob
    for f in glob.glob(os.path.join(SRC, "**", "About", "About.xml"), recursive=True):
        r = P.parse(f)
        if r is not None and r.findtext("packageId"):
            pids.add(r.findtext("packageId").lower())
    pids |= {"sarg.alphaanimals", "ludeon.rimworld.biotech", "ludeon.rimworld.odyssey", "ludeon.rimworld.ideology",
             "ludeon.rimworld.royalty", "ludeon.rimworld.anomaly", "oskarpotocki.vanillafactionsexpanded.core",
             "oskarpotocki.vfe.insectoid2"}
    return {"names": ["Alpha Animals"], "packageIds": sorted(pids)}


def creature_defs(donor_name):
    by, _ = donor()
    ds = [d for d in by[donor_name] if d.tag in ("ThingDef",)]
    ds += [d for lst in by.values() for d in lst if d.tag == "PawnKindDef" and d.findtext("race") == donor_name]
    return ds


def existing_equiv(tag, name):
    """Name of an owned def that already stands for the donor-only `name`, or None."""
    _, typed = ours_index()
    rest = name[3:] if name.startswith("AA_") else name
    for p in PREFIXES:
        if (tag, p + rest) in typed:
            return p + rest
    return None


def mod_pkg(mod_dir):
    r = P.parse(os.path.join(SRC, "RimMandrake", mod_dir, "About", "About.xml"))
    return r.findtext("packageId")


def donor_served(tp):
    """True when the donor ships this texPath as a loose PNG (so it is donor art), False for vanilla/DLC."""
    base = os.path.join(DONOR, "Textures", *tp.split("/"))
    if os.path.isdir(base):
        return True
    d, n = os.path.split(base)
    return os.path.isdir(d) and any(f.startswith(n) and f.lower().endswith(".png") for f in os.listdir(d))


def clean_thing(d, notes):
    """Donor-framework pieces off a ThingDef (creature or support): wildBiomes, renderTree, AnimalStatExtension, cosmetic
    comps, decoration items; VEF guards; species refs swapped for vanilla."""
    race = d.find("race")
    if race is not None:
        for tag in ("wildBiomes", "renderTree"):
            el = race.find(tag)
            if el is not None:
                race.remove(el)
    me = d.find("modExtensions")
    if me is not None:
        for li in list(me):
            if (li.get("Class") or "").startswith("VEF.AnimalBehaviours.AnimalStatExtension"):
                me.remove(li)
        if len(me) == 0:
            d.remove(me)
    comps = d.find("comps")
    if comps is not None:
        for li in list(comps):
            if (li.get("Class") or "") in DROP_COMP_CLASSES:
                comps.remove(li)
                notes.append(f"comp {li.get('Class')} dropped (cosmetic effecter; its flecks would owe art)")
    for parent in d.iter():
        for el in list(parent):
            t = (el.text or "").strip()
            if (el.tag, t) in DROP_ELEMENTS:
                parent.remove(el)
                notes.append(f"{el.tag} {t} dropped (decoration item; no art owed)")
                if t == "AA_AerofleetMeat" and parent.find("useMeatFrom") is None:
                    ET.SubElement(parent, "useMeatFrom").text = "Megaspider"
                    notes.append("useMeatFrom Megaspider added (PROVISIONAL, stands in for the donor's own meat item)")
                continue
            if t in SPECIES_SWAP and el.tag in ("useMeatFrom", "li", "canCrossBreedWith"):
                if el.tag == "li":
                    parent.remove(el)
                else:
                    el.text = SPECIES_SWAP[t]
                    notes.append(f"{el.tag} {t} -> {SPECIES_SWAP[t]} (vanilla; PROVISIONAL)")
    for el in d.iter("customResourceString"):     # a translation key of the donor: show the words instead
        t = (el.text or "").strip()
        if t.startswith("AA_"):
            w = re.sub(r"(?<!^)([A-Z])", r" \1", t[3:].replace("Desc", "")).lower()
            el.text = w
            notes.append(f"customResourceString {t} -> '{w}' (donor translation key replaced by the words)")
    for li in d.iter("li"):
        cls = li.get("Class") or ""
        if cls.startswith("VEF.") and li.get("MayRequire") is None:
            li.set("MayRequire", VEF)
        if (li.text or "").strip().startswith("VEF_") and li.get("MayRequire") is None and len(li) == 0:
            li.set("MayRequire", VEF)
    if race is not None:
        for tag in ("thinkTreeMain", "thinkTreeConstant"):
            el = race.find(tag)
            if el is not None and (el.text or "").strip().startswith("VEF_"):
                el.set("MayRequire", VEF)


def clean_kind(k, stem):
    for tag in ("alternateGraphics", "alternateGraphicChance"):
        el = k.find(tag)
        if el is not None:
            k.remove(el)
    for ls in k.findall("lifeStages/li"):          # sex-specific pictures: ours is ONE picture for both sexes
        for tag in ("femaleGraphicData", "maleGraphicData", "femaleDessicatedBodyGraphicData",
                    "maleDessicatedBodyGraphicData"):
            for el in ls.findall(tag):
                ls.remove(el)
    for li in k.iter("li"):
        if (li.text or "").strip().startswith("VEF_") and li.get("MayRequire") is None and len(li) == 0:
            li.set("MayRequire", VEF)
    for ls in k.findall("lifeStages/li"):
        for ded in ls.findall("dessicatedBodyGraphicData"):
            ls.remove(ded)
        for bg in ls.findall("bodyGraphicData"):
            tp = bg.find("texPath")
            tp.text = stem
            if bg.find("graphicClass") is None:
                gc = ET.Element("graphicClass")
                gc.text = "Graphic_Multi"
                bg.insert(list(bg).index(tp) + 1, gc)


def build(donor_name, registry):
    """-> (defs list [ThingDef, PawnKindDef, *new support], notes, art rows). registry: {donor support name -> ours}
    shared between creatures so each support def is written once."""
    ours, mod, texstem = PORTS[donor_name]
    by, abstract = donor()
    notes = []
    base = [copy.deepcopy(d) for d in creature_defs(donor_name)]
    baked, touched = P.Patches(active()).bake(base, [donor_name])
    tdef = [b for b in baked if b is not None and b.tag == "ThingDef"][0]
    kdef = [b for b in baked if b is not None and b.tag == "PawnKindDef"][0]
    for f, n in sorted(touched.items()):
        notes.append(f"folded {n} op(s) from {f}")
    clean_thing(tdef, notes)
    clean_kind(kdef, texstem or f"Things/Pawn/Animal/{ours}/{ours}")
    rename = {donor_name: ours}
    queue = [tdef, kdef]
    support, seen = [], {donor_name}
    onames, typed = ours_index()
    fam = SOUND_FAMILY.get(donor_name)

    def consider(n):
        if not n or n in seen:
            return
        if n not in by and n not in abstract:
            return
        seen.add(n)
        if (mod, n) in registry:
            rename[n] = registry[(mod, n)]
            return
        todo = by.get(n, []) + ([abstract[n]] if n in abstract and n not in by else [])
        eq = existing_equiv(todo[0].tag, n) if todo else None
        if eq:
            rename[n] = eq
            return
        new = NAME_OVERRIDE.get(n) or "RM_" + (n[3:] if n.startswith("AA_") else n)
        if new in registry.setdefault("_taken", set()):      # another mod already wrote this name: a mod-local copy,
            new = new + mod                                  # so each biome mod stays loadable without the others
        registry["_taken"].add(new)
        rename[n] = new
        registry[(mod, n)] = new
        for d in todo:
            dd = copy.deepcopy(d)
            if dd.tag == "ThingDef":
                clean_thing(dd, notes)
            if dd.tag == "PawnKindDef":
                st = f"Things/Pawn/Animal/{new}/{new}"
                clean_kind(dd, st)
            support.append(dd)
            queue.append(dd)

    while queue:
        d = queue.pop(0)
        for el in d.iter():
            if isinstance(el.tag, str) and el.tag != "modExtensions":
                consider((el.text or "").strip())
                consider(el.tag)
                consider(el.get("ParentName"))
    # sounds: donor SoundDefs carry donor audio, so they are swapped for vanilla, never ported
    support = [x for x in support if x.tag != "SoundDef"]
    kinds_map = {"soundWounded": "Wounded", "soundDeath": "Death", "soundCall": "Call", "soundAngry": "Angry"}
    for d in [tdef] + support:
        for el in d.iter():
            if el.tag in SOUND_TAGS and (el.text or "").strip().startswith(("AA_", "Pawn_RaptorShrimp_")):
                t = el.text.strip()
                if t in SOUND_SWAP:
                    el.text = SOUND_SWAP[t]
                elif fam and el.tag in kinds_map:
                    k = kinds_map[el.tag]
                    el.text = f"Pawn_{fam}_" + ("Pain" if fam == "Thrumbo" and k == "Wounded" else k)
                else:
                    notes.append(f"UNRESOLVED donor sound {t} in {el.tag}")
    labels = dict(LABEL_OVERRIDE)

    def rewrite(d):
        for parent in d.iter():
            for el in list(parent):
                if not isinstance(el.tag, str):
                    continue
                t = (el.text or "").strip()
                if t in rename:
                    el.text = rename[t]
                if el.tag in rename:
                    el.tag = rename[el.tag]
                if el.get("ParentName") in rename:
                    el.set("ParentName", rename[el.get("ParentName")])
        for att in ("ParentName", "Name"):
            if d.get(att) in rename:
                d.set(att, rename[d.get(att)])
        dn = d.find("defName")
        if dn is not None and dn.text.strip() in rename:
            dn.text = rename[dn.text.strip()]
            if dn.text in labels and d.find("label") is not None:
                d.find("label").text = labels[dn.text]
        return d

    out = [rewrite(tdef), rewrite(kdef)] + [rewrite(x) for x in support]
    art = []
    for d in out[2:] + [out[0]]:
        nm = d.findtext("defName") or ""
        for tag in ("texPath", "iconPath", "uiIconPath"):
            for tp in d.iter(tag):
                old = (tp.text or "").strip()
                if not old or not donor_served(old):
                    continue
                if d.tag == "ThingDef" and "Egg" in nm and EGG_SHARED:
                    new = f"Things/Item/Resource/{ours}Egg" if d.find("race") is None else old
                elif d.tag == "ThingDef" and d.find("projectile") is not None:
                    new = f"Things/Projectile/{nm}"
                elif d.tag == "ThingDef" and d.find("race") is None:
                    new = f"Things/Item/Resource/{nm}"
                elif d.tag == "AbilityDef":
                    new = f"UI/Abilities/{nm}"
                else:
                    continue
                if new != old:
                    notes.append(f"{tag} {old} -> {new} (ART OWED, {nm})")
                    art.append((nm, tag, new, old))
                    tp.text = new
    # a graphicData texPath inside a projectile ThingDef
    return out, notes, art


def header(donor_name, notes, items):
    ours, mod, _ = PORTS[donor_name]
    t = [f"  {ours}: owned RM_ port of the Alpha Animals {donor_name[3:]} (sarg.alphaanimals {donor_name}, "
         f"1.6/Defs/ThingDefs_Races). Phase 0 step P2 (biome_sprint_kickoff_2026-10-15.md 0.5.3), tool "
         f"src/RimMandrake/Utils/aa_port.py. Free RM_ tier, home mod {mod}.",
         "  Stats, tools, race fields and pawnkind numbers are the donor's own, as the creature the game shows today",
         "  (our rename/tolerance patches on the donor def are folded in). Departures:",
         "    - wildBiomes dropped (the biome roster casts it); AnimalStatExtension (donor stat defs) dropped.",
         "    - VEF.* comps and VEF_ abilities kept, guarded MayRequire " + VEF + " (a framework we keep, not the donor).",
         "    - texPath is OUR final path; the PNGs are owed through artpipe (no donor art is reused). Until the art is",
         "      installed through the art ledger this def has no picture: ART OWED, never a pass of the art bar.",
         "    - dessicated donor art and alternate random graphics dropped (vanilla fallback)."]
    for n in notes:
        t.append("    - " + n)
    return "\n".join(t) + "\n"


def cmd_port(a):
    only = set(a.only.split(",")) if a.only else None
    registry = {}
    written = []
    for dn in PORTS:
        if only and dn not in only and PORTS[dn][0] not in only:
            continue
        ours, mod, _ = PORTS[dn]
        path = os.path.join(SRC, "RimMandrake", mod, "Defs", FOLDER.get(mod, "ThingDefs_Races"), ours + ".xml")
        if os.path.exists(path):
            print("SKIP exists", os.path.relpath(path, REPO))
            continue
        out, notes, items = build(dn, registry)
        root = ET.Element("Defs")
        root.append(ET.Comment("\n" + header(dn, notes, items)))
        for d in out:
            root.append(d)
        ET.indent(root, space="  ")
        body = ET.tostring(root, encoding="unicode")
        ET.fromstring(body)
        print(("WROTE " if a.apply else "WOULD WRITE ") + os.path.relpath(path, REPO), f"({len(out)} defs; support "
              f"{[d.findtext('defName') or d.get('Name') for d in out[2:]]})")
        for it in items:
            print("   ART OWED", it)
        if a.apply:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write('<?xml version="1.0" encoding="utf-8"?>\n' + body + "\n")
        written.append(path)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("port")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--only")
    p.set_defaults(fn=cmd_port)
    p = sub.add_parser("repoint")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_repoint)
    p = sub.add_parser("check")
    p.set_defaults(fn=cmd_check)
    a = ap.parse_args()
    return a.fn(a)




OWNED_AA_NAMED = {"AA_Aerofleet_TwilightSea"}   # OUR accepted render (TerminalBiomes), named after the donor; RM_Bulloo's TEMP placeholder texPath


def cmd_check(a):
    """Every ported file: no donor AA_ name in its defs, no donor-served texPath. Zero files found is a failure."""
    bad, n = [], 0
    have_donor = os.path.isdir(DONOR)
    for dn, (ours, mod, _) in PORTS.items():
        path = os.path.join(SRC, "RimMandrake", mod, "Defs", FOLDER.get(mod, "ThingDefs_Races"), ours + ".xml")
        rel = os.path.relpath(path, REPO)
        if not os.path.exists(path):
            bad.append(f"{rel}: ported file missing")
            continue
        n += 1
        root = ET.parse(path).getroot()          # comments (the header names the donor) are not parsed
        txt = ET.tostring(root, encoding="unicode")
        for name in sorted(set(re.findall(r"\bAA_\w+", txt)) - OWNED_AA_NAMED):
            bad.append(f"{rel}: names donor {name}")
        if have_donor:
            for tag in ("texPath", "iconPath", "uiIconPath"):
                for el in root.iter(tag):
                    tp = (el.text or "").strip()
                    if tp and donor_served(tp):
                        bad.append(f"{rel}: {tag} {tp} is donor art")
    print(f"checked {n} of {len(PORTS)} ported files" + ("" if have_donor else "; UNMEASURED: donor texture check (donor folder absent)"))
    for b in bad:
        print("  - " + b)
    return 1 if bad or n == 0 else 0


# ---- roster repoint -------------------------------------------------------------------------------------------
# donor roster name -> (our def, defining mod folder key). The defining mod's packageId guards a row that lives in a
# DIFFERENT mod, so a biome mod still loads alone (the row just drops). Same-mod rows carry no guard.
SWB = "mandrake.rsw.swbestiary"
REPOINT = {
    "AA_Aerofleet": ("RM_Bulloo", "mandrake.rm.theforge"), "AA_AngelMoth": ("RM_Dustveil", "mandrake.rm.therot"),
    "AA_BedBug": ("RM_BedBug", "mandrake.rm.cauldron"),
    "AA_CrystalMit": ("RM_CrystalMit", "mandrake.rm.cauldron"),
    "AA_GiantCrownedSilkie": ("RM_GiantCrownedSilkie", "mandrake.rm.cauldron"),
    "AA_Lockjaw": ("RM_Siezer", "mandrake.rm.miasma"), "AA_Metallovore": ("RM_Metallovore", "mandrake.rm.theforge"),
    "AA_ShockGoat": ("RM_Zhissa", "mandrake.rm.nightsideice"),
    "AA_Swarmling": ("RM_Chittik", "mandrake.rm.therot"), "AA_BloodShrimp": ("RM_Zrrik", "mandrake.rm.greentide"),
    "AA_RaptorShrimp": ("RM_Sharpshrimp", "mandrake.rm.miasma"),
    # already ported before this pass (matched by stats, see Transient/phase0_p2_classification.md)
    "AA_Cactipine": ("RM_Chikka", SWB), "AA_Wildpawn": ("RM_Durrok", SWB), "AA_Wildpod": ("RM_Mullgoth", SWB),
    "AA_Murkling": ("RM_Lirrith", "mandrake.rm.abyss"), "AA_Helixien": ("RM_Bileworm", "mandrake.rm.scarlands"),
}


def row_mod_pkg(path):
    """packageId of the mod folder a src file lives in (nearest About/About.xml upward)."""
    d = os.path.dirname(path)
    while d.startswith(SRC) and d != SRC:
        a = os.path.join(d, "About", "About.xml")
        if os.path.exists(a):
            r = P.parse(a)
            return (r.findtext("packageId") or "").lower() if r is not None else ""
        d = os.path.dirname(d)
    return ""


def cmd_repoint(a):
    import donor_code_census as C
    rows = C.roster_rows()
    todo = {}
    for dn, lst in rows.items():
        if dn not in REPOINT:
            continue
        for biome, comm, f, how in lst:
            if biome.startswith("RM_"):
                todo.setdefault(os.path.join(REPO, f), set()).add(dn)
    n = 0
    for path, names in sorted(todo.items()):
        txt = open(path, encoding="utf-8", newline="").read()     # newline="": a CRLF file must not be rewritten as LF
        here = row_mod_pkg(path)
        for dn in sorted(names):
            ours, pkg = REPOINT[dn]
            guard = "" if pkg.lower() == here else f' MayRequire="{pkg}"'
            pat = re.compile(r'<%s(?:\s+MayRequire="[^"]*")?>([^<]*)</%s>' % (re.escape(dn), re.escape(dn)))
            txt, k = pat.subn(lambda m: f"<{ours}{guard}>{m.group(1)}</{ours}>", txt)
            n += k
            print(("REPOINT " if a.apply else "WOULD ") + f"{os.path.relpath(path, REPO)}: {dn} -> {ours}{guard or ' (same mod)'} x{k}")
        if a.apply:
            open(path, "w", encoding="utf-8", newline="").write(txt)
    print("rows:", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
