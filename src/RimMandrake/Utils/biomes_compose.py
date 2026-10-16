#!/usr/bin/env python3
"""
biomes_compose.py — build the shipped 'RimMandrake: Baroque Biomes' folder from
the per-biome dev folders (BAROQUE_BIOMES_COMPOSE_1).

Not run directly. `deploy_custom_mods.py --compose biomes` calls build(), gets a
temp folder back, and hands it to its own existing compare/copy path, so
plan-first, --apply, DEPLOY_HOLD.txt and shippable-file filtering behave
exactly as they do for every other mod.

Spec: design/RimMandrake/biome_mod_unification_spec.md §2/§3/§5. Roster and
load order: src/RimMandrake/Biomes.compose.json (the manifest is the ONLY place
the roster is written).

WHAT build() WRITES (temp dir, never src/):

    <target>/
      About/About.xml       generated: manifest name/packageId + the UNION of every
                            composed entry's modDependencies / loadAfter /
                            loadBefore / incompatibleWith, deduped by packageId,
                            with every composed (folded) packageId and the unified
                            id itself dropped
      LoadFolders.xml       "/" then one <li> per composed entry, in manifest order
      Biomes.roster.xml     data for the settings shell: key, label, blurb, group
                            and the concrete BiomeDef defNames each entry ships
      Assemblies/           ONLY the settings-shell DLL(s) (+ .srchash sidecars)
      Biomes/<key>/         verbatim copy of each composed entry minus About/
      Biomes/_Kits/<key>/   same, for group "engine" (spec §3)

🔴 WHY IT REFUSES ON A DUPLICATE RELATIVE PATH. Measured from the decompiled
1.6 engine: DirectXmlLoader.XmlAssetsInModFolder keys every Defs/ and Patches/
file by its path RELATIVE TO ITS LOAD ROOT and keeps the first one it sees
(Dictionary.TryAdd), walking roots in reverse LoadFolders order. Two biomes
both shipping Defs/BiomeDefs/Biomes.xml would therefore lose one of the two
files — silently, no log line. That is how versioned 1.5/ vs 1.6/ overrides
work, and it is fatal here. So any relative path (outside a root's top level)
shipped by more than one composed entry stops the build.
"""

import fnmatch
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

MANIFEST_REL = os.path.join("RimMandrake", "Biomes.compose.json")
TIER_DIR = "RimMandrake"


class ComposeError(Exception):
    pass


def manifest_path(src_root):
    return os.path.join(src_root, MANIFEST_REL)


def load_manifest(src_root):
    """-> manifest dict, or None when there is no manifest (e.g. a selftest's
    synthetic src root)."""
    p = manifest_path(src_root)
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8") as fh:
        m = json.load(fh)
    keys = [e["key"] for e in m["entries"]]
    if len(keys) != len(set(keys)):
        raise ComposeError("manifest has duplicate keys: %s" % keys)
    return m


def composed_entries(m):
    wave = m.get("compose_wave", 0)
    return [e for e in m["entries"] if e.get("wave", 99) <= wave]


def folded_sources(src_root):
    """-> {source folder name: (target, key)} for every entry the CURRENT
    compose wave folds in. deploy_custom_mods.py drops these from discovery so
    nobody redeploys one standalone by habit (spec §2)."""
    m = load_manifest(src_root)
    if not m:
        return {}
    return {e["source"]: (m["target"], e["key"]) for e in composed_entries(m)}


# ------------------------------------------------------- folded-id MayRequire
# A composed mod DROPS every folded packageId from the game's mod list, so a
# MayRequire / MayRequireAnyOf naming one is a ghost guard: it can never be
# satisfied, and RimWorld drops the guarded node silently
# (MAYREQUIRE_REPAIR_GUARDS_NAME_A_GHOST). Deploy rewrites them in the DEPLOYED
# copy only; src/ is never touched.
_MR_RE = re.compile(r'(\bMayRequire(?:AnyOf)?\s*=\s*)(")([^"]*)(")', re.I)


def folded_ids(src_root):
    """-> {folded packageId (lower): composed packageId} for the current wave."""
    m = load_manifest(src_root)
    if not m:
        return {}
    tier = os.path.join(src_root, TIER_DIR)
    target = m["about"]["packageId"].lower()
    out = {}
    for e in composed_entries(m):
        ap = os.path.join(tier, e["source"], "About", "About.xml")
        try:
            pid = (ET.parse(ap).getroot().findtext("packageId") or "").strip().lower()
        except (OSError, ET.ParseError):
            continue
        if pid and pid != target:
            out[pid] = target
    # A mod ABSORBED into a member's code (no folder of its own left, e.g. mandrake.rut.plantgrowth, fused into the
    # ExplosiveGrowth engine by PLANT_GROWTH_MERGE_NEVER_MEANT_APART): its packageId is retired the same way.
    for pid in m.get("absorbed", ()):
        pid = (pid or "").strip().lower()
        if pid and pid != target:
            out[pid] = target
    return out


def rewrite_mayrequire(text, mapping):
    """-> (new text, [(attr, folded id)] hits). Comma lists are rewritten per
    member and de-duplicated; everything else is preserved byte for byte."""
    hits = []

    def sub(mo):
        parts = [x.strip() for x in mo.group(3).split(",")]
        out, changed = [], False
        for x in parts:
            t = mapping.get(x.lower())
            if t:
                hits.append((mo.group(1).split("=")[0].strip(), x))
                changed = True
                x = t
            if x not in out:
                out.append(x)
        if not changed:
            return mo.group(0)
        return mo.group(1) + '"' + ",".join(out) + '"'
    return _MR_RE.sub(sub, text), hits


# PatchOperationFindMod names a mod by its display NAME, which compose never rewrites either
# (FINDMOD_GUARDS_REPAIR_GHOSTS_BY_NAME_TOO): FindMod matches on the About.xml <name> of an ACTIVE mod.
_MODS_RE = re.compile(r'(<mods>)(.*?)(</mods>)', re.S | re.I)
_LI_RE = re.compile(r'(<li>)([^<]*)(</li>)', re.I)


def folded_names(src_root):
    """-> {folded mod display name (lower): composed mod display name}."""
    m = load_manifest(src_root)
    if not m:
        return {}
    tier = os.path.join(src_root, TIER_DIR)
    target = (m["about"].get("name") or "").strip()
    out = {}
    for e in composed_entries(m):
        ap = os.path.join(tier, e["source"], "About", "About.xml")
        try:
            nm = (ET.parse(ap).getroot().findtext("name") or "").strip()
        except (OSError, ET.ParseError):
            continue
        if nm and target and nm.lower() != target.lower():
            out[nm.lower()] = target
    return out


def rewrite_findmod(text, names):
    """-> (new text, [folded name] hits): <li>NAME</li> inside <mods>...</mods> (PatchOperationFindMod)
    renamed to the composed mod's name, de-duplicated within the block; all else byte for byte."""
    hits = []

    def block(mo):
        lis = _LI_RE.findall(mo.group(2))
        if not any(x[1].strip().lower() in names for x in lis):
            return mo.group(0)
        seen = set()

        def li(lm):
            n = lm.group(2).strip()
            t = names.get(n.lower())
            if t:
                hits.append(n)
                n = t
            if n.lower() in seen:
                return ""
            seen.add(n.lower())
            return lm.group(1) + n + lm.group(3)
        return mo.group(1) + _LI_RE.sub(li, mo.group(2)) + mo.group(3)
    return _MODS_RE.sub(block, text), hits


def scan_ghost_findmods(src_root, names=None):
    """Lint: every FindMod <li> in src/ naming a folded mod -> [(relpath, line, folded name)]."""
    names = folded_names(src_root) if names is None else names
    found = []
    if not names:
        return found
    for dp, dn, fn in os.walk(src_root):
        dn[:] = [d for d in dn if d not in (".git", "Source", "obj", "bin", "About")]
        for f in fn:
            if not f.lower().endswith(".xml"):
                continue
            p = os.path.join(dp, f)
            try:
                with open(p, "rb") as fh:
                    txt = fh.read().decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "<mods>" not in txt.lower():
                continue
            for mo in _MODS_RE.finditer(txt):
                for lm in _LI_RE.finditer(mo.group(2)):
                    n = lm.group(2).strip()
                    if n.lower() in names:
                        line = txt.count("\n", 0, mo.start(2) + lm.start()) + 1
                        found.append((os.path.relpath(p, src_root), line, n))
    return found


def scan_ghost_guards(src_root, mapping=None):
    """Lint: every MayRequire* in src/ that names a folded id ->
    [(relative path, line, attr, folded id, ghost)]. ghost is True when no member
    of the attribute is satisfiable without rewriting (a prose About.xml mention
    is skipped; a list that already also names the composed id is not a ghost)."""
    mapping = folded_ids(src_root) if mapping is None else mapping
    found = []
    if not mapping:
        return found
    for dp, dn, fn in os.walk(src_root):
        dn[:] = [d for d in dn if d not in (".git", "Source", "obj", "bin", "About")]
        for f in fn:
            if not f.lower().endswith(".xml"):
                continue
            p = os.path.join(dp, f)
            try:
                with open(p, "rb") as fh:
                    txt = fh.read().decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "MayRequire" not in txt:
                continue
            for i, line in enumerate(txt.splitlines(), 1):
                for a, x in rewrite_mayrequire(line, mapping)[1]:
                    ids = [y.strip().lower() for mo in _MR_RE.finditer(line)
                           for y in mo.group(3).split(",")]
                    ghost = all(y in mapping for y in ids)
                    found.append((os.path.relpath(p, src_root), i, a, x, ghost))
    return found


def stage_rewritten(src_dir, mapping, log=print, names=None):
    """-> staged dir (symlink farm; only offending XML is real, rewritten), or
    None when nothing in src_dir needs rewriting. Caller removes the dir."""
    bad = {}
    for dp, dn, fn in os.walk(src_dir):
        for f in fn:
            if not f.lower().endswith(".xml"):
                continue
            p = os.path.join(dp, f)
            try:
                with open(p, "rb") as fh:
                    txt = fh.read().decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            new, nh = txt, 0
            if "MayRequire" in new:
                new, hits = rewrite_mayrequire(new, mapping)
                nh += len(hits)
            if names and "<mods>" in new.lower():
                new, hits = rewrite_findmod(new, names)
                nh += len(hits)
            if nh:
                bad[p] = (new, nh)
    if not bad:
        return None
    tmp = tempfile.mkdtemp(prefix="mrfix_")
    root = os.path.join(tmp, os.path.basename(os.path.normpath(src_dir)))
    for dp, dn, fn in os.walk(src_dir):
        rel = os.path.relpath(dp, src_dir)
        os.makedirs(os.path.join(root, rel), exist_ok=True)
        for f in fn:
            s, t = os.path.join(dp, f), os.path.join(root, rel, f)
            if s in bad:
                with open(t, "wb") as fh:
                    fh.write(bad[s][0].encode("utf-8"))
                shutil.copystat(s, t)
            else:
                os.symlink(s, t)
    log("  MayRequire: rewrote %d folded-id/name guard(s) in %d file(s) of %s (deployed copy only)"
        % (sum(n for _, n in bad.values()), len(bad), os.path.basename(src_dir)))
    return root


def dest_rel(e):
    if e.get("group") == "engine":
        return "Biomes/_Kits/%s" % e["key"]
    return "Biomes/%s" % e["key"]


# ------------------------------------------------------------------ About.xml
_LIST_FIELDS = ("modDependencies", "loadAfter", "loadBefore", "incompatibleWith",
                "forceLoadAfter", "forceLoadBefore")


def _li_id(field, li):
    if field == "modDependencies":
        return (li.findtext("packageId") or "").strip().lower()
    return (li.text or "").strip().lower()


def union_about(abouts, drop_ids, m):
    """abouts: [(key, About root)]. Returns (xml root, provenance dict)."""
    a = m["about"]
    root = ET.Element("ModMetaData")
    ET.SubElement(root, "name").text = a["name"]
    ET.SubElement(root, "packageId").text = a["packageId"]
    ET.SubElement(root, "author").text = a["author"]
    sv = ET.SubElement(root, "supportedVersions")
    for v in a["supportedVersions"]:
        ET.SubElement(sv, "li").text = v
    prov = {}
    for field in _LIST_FIELDS:
        seen, items = set(), []
        for key, ab in abouts:
            node = ab.find(field)
            if node is None:
                continue
            for li in node.findall("li"):
                pid = _li_id(field, li)
                if not pid or pid in drop_ids:
                    continue
                prov.setdefault((field, pid), []).append(key)
                if pid in seen:
                    continue
                seen.add(pid)
                items.append(li)
        if items:
            out = ET.SubElement(root, field)
            for li in items:
                out.append(li)
    ET.SubElement(root, "description").text = a["description"]
    return root, prov


def _write_xml(root, path):
    ET.indent(root, space="  ")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def biome_defnames(src_dir):
    """Concrete BiomeDef defNames under an entry's Defs/ (never Abstract)."""
    out = []
    defs = os.path.join(src_dir, "Defs")
    for dp, _, fns in os.walk(defs):
        for fn in sorted(fns):
            if not fn.lower().endswith(".xml"):
                continue
            try:
                r = ET.parse(os.path.join(dp, fn)).getroot()
            except ET.ParseError:
                continue            # wellformed() refuses it later, loudly
            for el in r:
                if el.tag != "BiomeDef":
                    continue
                if (el.get("Abstract") or "").lower() == "true":
                    continue
                dn = (el.findtext("defName") or "").strip()
                if dn:
                    out.append(dn)
    return sorted(set(out))


# ----------------------------------------------------------------------- build
def build(src_root, tree_fn, holds, log=print):
    """Compose the unified folder into a fresh temp dir.

    tree_fn: deploy_custom_mods.tree (shippable-file walk — reused, so the
             composed tree ships exactly what a standalone deploy would).
    holds:   deploy_custom_mods.load_holds() entries; a hold on a SOURCE path
             ("TheSump/Defs/x.xml") is translated to the composed path
             ("RimMandrake.Biomes/Biomes/TheSump/Defs/x.xml") and returned, so
             the existing split_held() keeps honouring it.

    -> (target name, composed folder, extra holds). The composed folder sits
    alone inside a fresh temp dir; the caller deletes its PARENT.
    """
    m = load_manifest(src_root)
    if not m:
        raise ComposeError("no manifest at %s" % manifest_path(src_root))
    target = m["target"]
    entries = composed_entries(m)
    if not entries:
        raise ComposeError("compose_wave %s selects no entries" % m.get("compose_wave"))
    tier = os.path.join(src_root, TIER_DIR)

    # --- read every composed entry, and refuse before copying anything
    abouts, drop_ids, plan = [], {m["about"]["packageId"].lower()}, []
    for e in entries:
        sdir = os.path.join(tier, e["source"])
        about = os.path.join(sdir, "About", "About.xml")
        if not os.path.isfile(about):
            raise ComposeError("%s: no About/About.xml at %s" % (e["key"], sdir))
        ab = ET.parse(about).getroot()
        pid = (ab.findtext("packageId") or "").strip().lower()
        if not pid:
            raise ComposeError("%s: About.xml has no packageId" % e["key"])
        drop_ids.add(pid)
        abouts.append((e["key"], ab))
        rels = sorted(r for r in tree_fn(sdir)
                      if r.split(os.sep)[0] != "About")
        plan.append((e, sdir, pid, rels))

    owners = {}
    for e, _, _, rels in plan:
        for r in rels:
            if os.sep not in r:
                continue            # a load root's top-level files (LICENSE) are never read as content
            owners.setdefault(r.replace(os.sep, "/"), []).append(e["key"])
    shadow = {r: k for r, k in owners.items() if len(k) > 1}
    if shadow:
        lines = ["%s  <- %s" % (r, ", ".join(k)) for r, k in sorted(shadow.items())]
        raise ComposeError(
            "%d relative path(s) shipped by more than one entry; RimWorld keeps "
            "only one of each (DirectXmlLoader TryAdd), silently:\n  %s"
            % (len(shadow), "\n  ".join(lines)))

    shell_dir = os.path.join(tier, m["shell"]["source"], "Assemblies")
    shell_files = []
    for dll in m["shell"]["assemblies"]:
        p = os.path.join(shell_dir, dll)
        if not os.path.isfile(p):
            raise ComposeError("settings-shell assembly not built: %s — build "
                               "src/RimMandrake/%s/Source first"
                               % (p, m["shell"]["source"]))
        shell_files.append(p)
        if os.path.isfile(p + ".srchash"):
            shell_files.append(p + ".srchash")

    # --- write
    tmp = tempfile.mkdtemp(prefix="compose_%s_" % target)
    out = os.path.join(tmp, target)
    os.makedirs(out)
    extra_holds = []
    fmap = {p: m["about"]["packageId"].lower() for p in drop_ids
            if p != m["about"]["packageId"].lower()}
    nfix = 0
    tname = (m["about"].get("name") or "").strip()
    nmap = {}
    for e, sdir, pid, rels in plan:
        try:
            nm = (ET.parse(os.path.join(sdir, "About", "About.xml")).getroot().findtext("name") or "").strip()
        except (OSError, ET.ParseError):
            nm = ""
        if nm and tname and nm.lower() != tname.lower():
            nmap[nm.lower()] = tname
    for e, sdir, pid, rels in plan:
        d = dest_rel(e)
        for r in rels:
            t = os.path.join(out, d, r)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(os.path.join(sdir, r), t)
            if r.lower().endswith(".xml"):
                try:
                    with open(t, "rb") as fh:
                        txt = fh.read().decode("utf-8")
                except UnicodeDecodeError:
                    txt = ""
                new, nh = txt, 0
                if "MayRequire" in new:
                    new, hits = rewrite_mayrequire(new, fmap)
                    nh += len(hits)
                if nmap and "<mods>" in new.lower():
                    new, hits = rewrite_findmod(new, nmap)
                    nh += len(hits)
                if nh:
                    nfix += nh
                    with open(t, "wb") as fh:
                        fh.write(new.encode("utf-8"))
            key = "%s/%s" % (e["source"], r.replace(os.sep, "/"))
            for h in holds:
                if fnmatch.fnmatch(key, h["pattern"]):
                    h["hits"] += 1
                    extra_holds.append({
                        "pattern": "%s/%s/%s" % (target, d, r.replace(os.sep, "/")),
                        "reason": "%s (hold DEPLOY_HOLD.txt:%d on %s)"
                                  % (h["reason"], h["lineno"], key),
                        "lineno": h["lineno"], "hits": 0})
                    break
        log("  compose  %-20s %-34s %4d file(s) -> %s" % (e["key"], pid, len(rels), d))
    os.makedirs(os.path.join(out, "Assemblies"))
    for p in shell_files:
        shutil.copy2(p, os.path.join(out, "Assemblies", os.path.basename(p)))
    log("  compose  %-20s %-34s %4d file(s) -> Assemblies/"
        % ("(settings shell)", m["shell"]["source"], len(shell_files)))

    about_root, prov = union_about(abouts, drop_ids, m)
    _write_xml(about_root, os.path.join(out, "About", "About.xml"))

    lf = ET.Element("loadFolders")
    v = ET.SubElement(lf, "v" + m["about"]["supportedVersions"][-1])
    ET.SubElement(v, "li").text = "/"
    for e, *_ in plan:
        ET.SubElement(v, "li").text = dest_rel(e)
    _write_xml(lf, os.path.join(out, "LoadFolders.xml"))

    ro = ET.Element("BaroqueBiomesRoster")
    ro.set("compose_wave", str(m.get("compose_wave", 0)))
    for e, sdir, pid, _ in plan:
        n = ET.SubElement(ro, "entry", {
            "key": e["key"], "label": e["label"], "group": e.get("group", "biome"),
            "sourcePackageId": pid})
        ET.SubElement(n, "blurb").text = e.get("blurb", "")
        for dn in biome_defnames(sdir):
            ET.SubElement(n, "biomeDef").text = dn
    _write_xml(ro, os.path.join(out, "Biomes.roster.xml"))

    deps = [pid for (f, pid) in prov if f == "modDependencies"]
    log("  compose  About.xml: %d hard dependencies (%s); %d folded packageId(s) "
        "dropped from every list" % (len(deps), ", ".join(sorted(deps)),
                                     len(drop_ids) - 1))
    if nfix:
        log("  compose  MayRequire: rewrote %d folded-id guard(s) to %s"
            % (nfix, m["about"]["packageId"]))
    log("  compose  LoadFolders.xml: / + %d root(s), manifest order\n" % len(plan))
    return target, out, extra_holds
