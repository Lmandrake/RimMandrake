#!/usr/bin/env python3
"""modaudit/depgraph.py - labelled dependant edges between mods (who needs whom, and HOW). Pure; selftested.

An edge  source -> target  means "source would lose something if target were removed". Kinds:
  hard_dep        source About.xml <modDependencies> names target
  hard_dep_v1.6   source <modDependenciesByVersion><v1.6> names target (what the 1.6 game enforces)
  load_after      source <loadAfter>/<forceLoadAfter>/<loadAfterByVersion v1.6>/<forceLoadAfterByVersion v1.6>
  patch_xpath     source's patch xpaths name defNames that target declares (defscan targets_owner_mods)
  findmod         source PatchOperationFindMod <mods><li> names target's About <name>
  mayrequire      source Defs/Patches MayRequire / MayRequireAnyOf names target's packageId
  class_ref       source Defs/Patches XML names a C# type defined in target's LOADED assemblies (TypeDef table)
  def_ref         source Defs/Patches XML text or tag names a defName only target declares (CANDIDATE name match)
"""
from collections import Counter, defaultdict

KINDS = ("hard_dep", "hard_dep_v1.6", "load_after", "patch_xpath", "findmod", "mayrequire", "class_ref", "def_ref")
# GenTypes resolves an undotted class name in these namespaces (plus the global one); a bare name elsewhere fails.
IMPLICIT_NS = {"", "Verse", "RimWorld", "Verse.AI", "Verse.AI.Group", "Verse.Sound", "Verse.Grammar", "Verse.Steam",
               "RimWorld.Planet", "RimWorld.BaseGen", "RimWorld.QuestGen", "RimWorld.SketchGen", "RimWorld.IO",
               "Verse.Noise", "LudeonTK"}
MAX_TYPE_OWNERS = 3                     # a type defined by more mods than this is a vendored copy: no edge


def type_index(types_by_mod):
    """{pid: iterable of 'Ns.Type'} -> (full {name: {pid}}, bare {name: {pid}}). Pure; selftested."""
    full, bare = defaultdict(set), defaultdict(set)
    for pid, types in types_by_mod.items():
        for t in types:
            full[t].add(pid)
            ns, _, nm = t.rpartition(".")
            if ns in IMPLICIT_NS:
                bare[nm].add(pid)
    return ({k: v for k, v in full.items() if len(v) <= MAX_TYPE_OWNERS},
            {k: v for k, v in bare.items() if len(v) <= MAX_TYPE_OWNERS})


def build(about, patches, refs, types_by_mod, known, skip_sources=()):
    """-> {target: {source: Counter(kind -> refs)}}.
    about   {pid: parsed About (diskfacts.parse_about)}
    patches {pid: defscan patches record (targets_owner_mods, findmod_names)}
    refs    {pid: defscan refs record (class_refs_full, class_refs_bare, mayrequire_any, def_refs_owner_mods)}
    types_by_mod {pid: loaded type names}; known: the universe's packageIds (lowercase);
    skip_sources: ids that never count as a dependant (Core/DLC: a shared defName there is a collision, not a need)."""
    g = defaultdict(lambda: defaultdict(Counter))
    names = defaultdict(set)
    for pid, ab in about.items():
        for k in ("name", "shortName"):
            if (ab or {}).get(k):
                names[ab[k].strip().lower()].add(pid)

    def add(src, tgt, kind, n=1):
        tgt = (tgt or "").strip().lower()
        if tgt and tgt != src and tgt in known and n and src not in skip_sources:
            g[tgt][src][kind] += n
    for src, ab in about.items():
        ab = ab or {}
        for d in ab.get("modDependencies") or []:
            add(src, d.get("packageId"), "hard_dep")
        for t in (ab.get("modDependenciesByVersion") or {}).get("v1.6") or []:
            add(src, t, "hard_dep_v1.6")
        for f in ("loadAfter", "forceLoadAfter"):
            for t in ab.get(f) or []:
                add(src, t, "load_after")
        for f in ("loadAfterByVersion", "forceLoadAfterByVersion"):
            for t in (ab.get(f) or {}).get("v1.6") or []:
                add(src, t, "load_after")
    for src, p in patches.items():
        for t, n in (p.get("targets_owner_mods") or {}).items():
            add(src, t, "patch_xpath", n)
        for nm, n in (p.get("findmod_names") or {}).items():
            for t in names.get(nm.strip().lower(), ()):
                add(src, t, "findmod", n)
    full, bare = type_index(types_by_mod)
    for src, r in refs.items():
        for t, n in (r.get("mayrequire_any") or {}).items():
            add(src, t, "mayrequire", n)
        for t, n in (r.get("def_refs_owner_mods") or {}).items():
            add(src, t, "def_ref", n)
        for nm, n in (r.get("class_refs_full") or {}).items():
            for t in full.get(nm.replace("+", "."), full.get(nm, ())):
                add(src, t, "class_ref", n)
        for nm, n in (r.get("class_refs_bare") or {}).items():
            for t in bare.get(nm, ()):
                add(src, t, "class_ref", n)
    return g


def detail(edges_for_target):
    """{source: Counter(kind->n)} -> [{packageId, kinds, refs}] sorted by packageId. Pure."""
    return [{"packageId": s, "kinds": [k for k in KINDS if c.get(k)], "refs": sum(c.values())}
            for s, c in sorted(edges_for_target.items())]
