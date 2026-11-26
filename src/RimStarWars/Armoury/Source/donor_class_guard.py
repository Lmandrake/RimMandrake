"""Donor classes in Armoury's absorbed defs: which XML node needs which MayRequire.

Armoury keeps donor class names verbatim in its absorbed copies (`Lightsaber.CompProperties_GlowerOptions`,
`BigAndSmall.PawnRenderingProps_Ultimate`, ...). Only the donor's DLL provides such a class. On a mod list without
the donor, an unguarded node fails the load of its whole def ("Could not find type named ...", or "Type ... is not a
Def type"), and every def that refers to the lost def then logs "Could not resolve cross-reference". Measured on
the 26-mod tier explosiveknockback_visit, ArchBig, 2026-11-26 (item
RIMMANDRAKE_LOAD_ARMOURY_ABSORBED_DEFS_WITHOUT_LIGHTSABER_TYPES).

Where RimWorld 1.6 honours a guard (read in the decompiled Verse source, 2026-11-26):
  - MayRequire / MayRequireAnyOf on a top-level def (LoadedModManager, XmlInheritance);
  - MayRequire / MayRequireAnyOf on a list `<li>` (DirectXmlToObject.ListFromXml, DirectXmlToObjectNew
    ValidateMayRequires); a patch's `<operations><li>` is a list too;
  - MayRequire on a field that holds a def reference (DirectXmlToObject: RegisterObjectWantsCrossRef);
  - NOT on an ordinary field such as `<genStep Class="...">`, and NOT on a top-level patch `<Operation>`
    (project-engine-facts.md).
  - A PatchOperationFindMod does NOT guard a donor class: RimWorld builds the whole patch tree, <match> included,
    when it parses the file, before FindMod runs. Measured: ArchBig cold load 2026-11-26 04:40 PST, a FindMod on
    "XML Extensions" still logged "Could not find type named XmlExtensions.OptionalPatch". Put a donor Operation in a
    PatchOperationSequence as `<li MayRequire="<donor>">`: the list loader skips that <li> unparsed.
A reference to a def that only the donor defines (DONOR_DEFS) needs the same guard: without the donor it logs
"Could not resolve cross-reference" (Force_KyberCrystals, the same cold load).

This module holds the one table (DONORS) and two functions:
  holder(node, parents, in_patch)   the element that must carry the MayRequire for `node`
  unguarded(root, in_patch)         every node of the tree that names a donor class with no honoured guard
The lint src/RimMandrake/Utils/armoury_donor_class_guard.py reads every Armoury XML file with `unguarded`.
"""
import re

# namespace prefix -> (packageIds whose MayRequire guards it, the donor's display names, for messages).
# The first packageId is the donor itself (design/RimMandrake/mod_archive/ALL_ORIGINAL_MODS.tsv); a later one is a
# mod that hard-depends on the donor, so its MayRequire also proves the donor active.
DONORS = {
    "Lightsaber": (("lee.theforce.lightsaber",), ("Star Wars : The Force - Lightsaber",)),
    "BigAndSmall": (("redmattis.betterprerequisites",), ("Big and Small - Framework",)),
    "XmlExtensions": (("imranfish.xmlextensions",), ("XML Extensions",)),
    "WHands": (("mlie.showmeyourhands",), ("Show Me Your Hands",)),
    "ArtificialBeings": (("killathon.artificialbeings", "killathon.artificialbeings.syncore", "guy762.kotordroids"),
                         ("ABF: Artificial Beings Framework",)),
    "AthenaFramework": (("smartkar.athenaframework",), ()),
    "Vehicles": (("smashphil.vehicleframework",), ("Vehicle Framework",)),
    "FalloutCurrencies_NonReplacement": (("rick.fcp.core.tools",), ()),
    "RimMandrake.MineShaft": (("mandrake.rm.mineshaft",), ()),
}

# defName -> DONORS key: defs that only the donor defines, and that our absorbed copies refer to by name.
DONOR_DEFS = {
    "Force_KyberCrystals": "Lightsaber",      # ThingCategoryDef of lee.theforce.lightsaber; Kyber's thingCategories
}

_DOTTED = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)+$")
_CLASS_TAG = re.compile(r"(?i)(class|worker)$")


def donor_of(name):
    """-> the DONORS key whose namespace `name` (a full type name) lives in, or None."""
    if not name or not _DOTTED.match(name):
        return None
    best = None
    for ns in DONORS:
        if name.startswith(ns + ".") and (best is None or len(ns) > len(best)):
            best = ns
    return best


def named_classes(el):
    """-> the type names that this element itself names: its tag, its Class attribute, its text in a *Class/*Worker
    field."""
    out = []
    if isinstance(el.tag, str) and "." in el.tag:
        out.append(el.tag)
    if el.get("Class"):
        out.append(el.get("Class"))
    if isinstance(el.tag, str) and _CLASS_TAG.search(el.tag) and el.text and len(el) == 0:
        out.append(el.text.strip())
    return out


def _guards(el, ns):
    accepted = DONORS[ns][0]
    req = [m.strip().lower() for m in (el.get("MayRequire") or "").split(",") if m.strip()]
    if any(m in accepted for m in req):
        return True
    anyof = [m.strip().lower() for m in (el.get("MayRequireAnyOf") or "").split(",") if m.strip()]
    return bool(anyof) and all(m in accepted for m in anyof)


def _honoured(el, parent, depth, in_patch):
    """True when RimWorld reads MayRequire on `el`: an <li>, a top-level def, or a def a patch adds (<value> child)."""
    if el.tag == "li":
        return True
    if not in_patch and depth == 1:
        return True
    return in_patch and parent is not None and parent.tag == "value"


def holder(chain, in_patch):
    """`chain` = [root, ..., node]. -> the element that should carry the MayRequire for the node (nearest honoured
    element; a leaf that names a donor-only def carries its own), or None for a top-level patch Operation (it must
    move into a PatchOperationSequence <li>)."""
    if donor_def_ref(chain[-1]):
        return chain[-1]
    for i in range(len(chain) - 1, 0, -1):
        if _honoured(chain[i], chain[i - 1], i, in_patch):
            return chain[i]
    return None


def is_guarded(chain, ns, in_patch):
    for i in range(1, len(chain)):
        el, parent = chain[i], chain[i - 1]
        if _honoured(el, parent, i, in_patch) and _guards(el, ns):
            return True
    return False


def donor_def_ref(el):
    """-> the DONORS key when `el` is a leaf whose text names a def that only that donor defines, else None."""
    if isinstance(el.tag, str) and len(el) == 0 and el.text:
        return DONOR_DEFS.get(el.text.strip())
    return None


def unguarded(root, in_patch):
    """-> [(chain, type name, donor ns)] for each node under `root` that names a donor class with no honoured guard."""
    out = []

    def walk(chain):
        el = chain[-1]
        if not isinstance(el.tag, str):
            return
        for name in named_classes(el):
            ns = donor_of(name)
            if ns and not is_guarded(chain, ns, in_patch):
                out.append((list(chain), name, ns))
        ns = donor_def_ref(el)
        if ns and not _guards(el, ns) and not is_guarded(chain, ns, in_patch):
            out.append((list(chain), el.text.strip(), ns))
        for c in el:
            walk(chain + [c])

    walk([root])
    return out


def guard_element(el, note=print):
    """Generator hook: give each unguarded donor-class node under the top-level def `el` its MayRequire, on the
    element that RimWorld reads it from. Returns the number of guards added."""
    import xml.etree.ElementTree as ET
    root = ET.Element("Defs")
    root.append(el)
    n = 0
    try:
        for chain, name, ns in unguarded(root, in_patch=False):
            if is_guarded(chain, ns, False):          # an earlier guard in this pass already covers it
                continue
            h = holder(chain, False)
            want = DONORS[ns][0][0]
            cur = h.get("MayRequire")
            h.set("MayRequire", want if not cur else cur + "," + want)
            n += 1
            note("DONOR CLASS GUARD: %s needs %s -> MayRequire=%r on <%s>" % (name, ns, h.get("MayRequire"), h.tag))
    finally:
        root.remove(el)
    return n
