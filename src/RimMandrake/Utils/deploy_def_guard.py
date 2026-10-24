#!/usr/bin/env python3
"""
deploy_def_guard.py — refuse a deploy that would leave the GAME copy with a def
defined twice, or a moved def with no home (SWB_BIOMES_DEPLOY_GUARD_DUPLICATE_DEFS).

WHY. Creatures moved out of SWBestiary (RSW_ tier) into biome mods that ship
inside the composed RimMandrake.Biomes (Durrok, Mullgoth, Vurra, Ikee, Korrum,
the Jurassic ports, karrask, tellurox ...). The repo is consistent; the game
copies are two separate deploys. Deploying only one side leaves:

  * forward (biomes deployed, SWBestiary not): the stale SWBestiary copy still
    defines RM_Durrok -> the same defName in two mods; or still defines
    RSW_Ikee while RM_Ikee is live -> the alias RSW_Ikee->RM_Ikee never fires
    and the creature exists twice under two names;
  * reverse (SWBestiary deployed, biomes not): RM_Durrok leaves SWBestiary and
    the stale biomes copy never had it -> the def is simply gone.

Nothing in the per-file plan can see either: each mod's own diff is correct.
This module looks ACROSS the resulting game-copy mod set.

SCOPE. Every folder in the game's Mods dir whose About.xml packageId starts
with `mandrake.` (plus the targets). Not the live ModsConfig.xml: that file is
the NEXT load and is routinely a minimal spike list (26 mods on 2026-10-24,
SWBestiary not even in it), so gating on it would pass a deploy that breaks
the owner's full list. Workshop/vanilla defs are out of scope.

WHAT BLOCKS. Only findings that touch a mod this plan deploys. Anything else
already wrong in the game copy is printed as PRE-EXISTING, never blocks an
unrelated deploy.

  DUP          (def type, defName) defined in two or more mods
  ALIAS-STALE  an RM_DefAliasDef `from` AND its `to` both live (old copy not pruned)
  ALIAS-DANGLING an alias `to` that is one of OUR defs (the repo defines it)
               but no deployed mod will define it
  VANISHED     a def a target defines in the game NOW, defined nowhere after the
               plan, that the repo still ships from another mod (it moved there)

Never blocks: ALIAS-REPO (the alias `from` is still defined by the REPO, so
no deploy order changes anything). A stale copy in a game folder with no repo
source (orphan, e.g. a mod merged away) gets a remove-by-hand line, never a
deploy command. A PRE-EXISTING finding's fix line never names this plan's mods.

Def files: XML under <root>/Defs/ for each load root (LoadFolders.xml's newest
version list; else "/", "Common" and the newest numeric version folder).
Def type: the element tag minus namespace; any *ThingDef* subclass
(AlienRace.ThingDef_AlienRace) shares the ThingDef database and keys as ThingDef.
"""

import fnmatch
import os
import re
import xml.etree.ElementTree as ET

GAME_VERSION = (1, 6)
_VER = re.compile(r"^v?(\d+)\.(\d+)$")


def _ver(s):
    m = _VER.match(s or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def def_type(tag):
    base = tag.split(".")[-1]
    return "ThingDef" if base.startswith("ThingDef") else base


def xml_files(root):
    """{rel: abspath} for every .xml under root (dangling links skipped)."""
    out = {}
    if not os.path.isdir(root):
        return out
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("Source", "__pycache__", ".git", "obj", "bin")]
        for f in fn:
            if f.lower().endswith(".xml"):
                p = os.path.join(dp, f)
                if os.path.exists(p):
                    out[os.path.relpath(p, root).replace(os.sep, "/")] = p
    return out


def load_roots(files):
    """Load roots (forward-slash prefixes, "" = mod root) for a {rel: path} map."""
    lf = files.get("LoadFolders.xml")
    if lf:
        try:
            r = ET.parse(lf).getroot()
            best = None
            for v in r:
                vv = _ver(v.tag)
                if vv and vv <= GAME_VERSION and (best is None or vv > best[0]):
                    best = (vv, v)
            if best is not None:
                return [((li.text or "").strip().strip("/")) for li in best[1].findall("li")]
        except (OSError, ET.ParseError):
            pass
    tops = {rel.split("/")[0] for rel in files if "/" in rel}
    vers = sorted(v for v in (_ver(t) for t in tops) if v and v <= GAME_VERSION)
    roots = ["", "Common"]
    if vers:
        roots.append("%d.%d" % vers[-1])
    return roots


def def_files(files):
    roots = load_roots(files)
    out = []
    for rel, p in files.items():
        for r in roots:
            pre = (r + "/") if r else ""
            if rel.startswith(pre + "Defs/"):
                out.append((rel, p))
                break
    return out


_CACHE = {}


def parse_defs(path):
    """-> ([(type, defName)], [(fromKey, toKey)]) for one def file; cached by path+mtime."""
    try:
        key = (path, os.path.getmtime(path))
    except OSError:
        return [], []
    if key in _CACHE:
        return _CACHE[key]
    defs, aliases = [], []
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        root = None
    for el in (root if root is not None else []):
        if not isinstance(el.tag, str):
            continue
        if (el.get("Abstract") or "").lower() == "true":
            continue
        name = (el.findtext("defName") or "").strip()
        if name:
            defs.append((def_type(el.tag), name))
        if el.tag.split(".")[-1] == "RM_DefAliasDef":
            for li in el.findall("aliases/li"):
                f, t = (li.findtext("from") or "").strip(), (li.findtext("to") or "").strip()
                ty = def_type((li.findtext("defType") or "ThingDef").strip())
                if f and t:
                    aliases.append(((ty, f), (ty, t)))
    _CACHE[key] = (defs, aliases)
    return defs, aliases


def index(mods, prefiltered=False):
    """mods: {mod: {rel: path}} -> (defs {key: {mod: rel}}, aliases [(mod, rel, from, to)]).
    prefiltered: the maps already hold def files only (repo index)."""
    defs, aliases = {}, []
    for mod, files in mods.items():
        for rel, p in (files.items() if prefiltered else def_files(files)):
            ds, als = parse_defs(p)
            for k in ds:
                defs.setdefault(k, {}).setdefault(mod, rel)
            for f, t in als:
                aliases.append((mod, rel, f, t))
    return defs, aliases


def post_files(src_files, dst_files, held, pruned):
    """Resulting game copy of one target. src/dst: {rel: path}; held(rel)->bool
    keeps the game's copy of that path; pruned: rels the apply will delete."""
    out = {}
    for rel, p in dst_files.items():
        if rel not in src_files and rel not in pruned:
            out[rel] = p                          # game-only, kept
    for rel, p in src_files.items():
        if held(rel):
            if rel in dst_files:
                out[rel] = dst_files[rel]
        else:
            out[rel] = p
    return out


def _k(key):
    return "%s %s" % key


def check(post, pre, targets, repo, cmd):
    """post: {mod: {rel: path}} every mod after the plan; pre: {target: {rel: path}}
    game copy of each target NOW; targets: set of mod names; repo: {mod: {rel: path}}
    what each mod's REPO would ship; cmd(mods, prune) -> fix command string.

    -> (blocking, preexisting): lists of message strings."""
    pdefs, paliases = index(post)
    predefs, _ = index(pre)
    rdefs, raliases = index(repo, prefiltered=True)
    block, old = [], []

    def put(msg, mods):
        (block if set(mods) & targets else old).append(msg)

    def fix(others, key, owners):
        """Fix line for a finding whose resolution is 'deploy these too'. The plan's
        own targets join the line only when the finding touches them; a game
        folder with no repo source (orphan) cannot be fixed by any deploy."""
        orphans = sorted(m for m in others if m not in repo)
        if orphans:
            return ("orphan game folder(s) %s: no repo source, so no deploy can fix it -- "
                    "remove it from the game's Mods dir by hand (owner's call)"
                    % ", ".join(orphans))
        need_prune = False          # a stale file with no repo counterpart survives a
        for m in others:            # plain --apply (game-only or uncommitted delete)
            rel = pdefs.get(key, {}).get(m)
            if rel and rel not in repo.get(m, {}):
                need_prune = True
        mods = set(others) | (targets if set(owners) & targets else set())
        return cmd(sorted(mods), need_prune)

    for key, owners in sorted(pdefs.items()):
        if len(owners) < 2:
            continue
        where = ", ".join("%s (%s)" % (m, r) for m, r in sorted(owners.items()))
        in_repo = [m for m in owners if key in rdefs and m in rdefs[key]]
        if len(in_repo) >= 2:
            hint = "the REPO defines it in %s too -- fix the repo, no deploy order cures it" \
                   % " and ".join(sorted(in_repo))
        else:
            stale = [m for m in owners if m not in in_repo]
            hint = "stale copy in %s; fix: %s" % (", ".join(sorted(stale)),
                                                  fix(stale, key, owners))
        put("DUP %s defined in %d mods: %s\n      %s" % (_k(key), len(owners), where, hint),
            owners)

    for mod, rel, frm, to in paliases:
        if frm in pdefs and to in pdefs:
            owners = set(pdefs[frm]) | set(pdefs[to]) | {mod}
            stale = sorted(set(pdefs[frm]) - set(rdefs.get(frm, {})))
            if not stale:       # the REPO keeps the old name live: no deploy order cures it
                old.append("ALIAS-REPO %s %s -> %s: the repo itself still defines %s in %s, so "
                           "the alias (in %s/%s) is inert -- a repo question, not a deploy "
                           "hazard" % (frm[0], frm[1], to[1], frm[1], ", ".join(sorted(pdefs[frm])),
                                       mod, rel))
                continue
            put("ALIAS-STALE %s %s -> %s: the old name is still live in %s, so the alias "
                "never fires and the def exists twice under two names (alias in %s/%s)\n"
                "      fix: %s" % (frm[0], frm[1], to[1], ", ".join(sorted(pdefs[frm])), mod, rel,
                                   fix(stale, frm, owners)), owners)
        elif to not in pdefs and to in rdefs:
            homes = sorted(rdefs[to])
            put("ALIAS-DANGLING %s %s -> %s: no deployed mod will define %s (repo ships it "
                "from %s; alias in %s/%s)\n      fix: %s"
                % (frm[0], frm[1], to[1], to[1], ", ".join(homes), mod, rel,
                   cmd(sorted(set(homes) | targets), False)),
                set(homes) | {mod} | set(predefs.get(to, {})))

    ralias = {}
    for _, _, f, t in raliases:
        ralias.setdefault(f, set()).add(t)
    for key in sorted(predefs):
        if key in pdefs:
            continue
        homes = {m for m in rdefs.get(key, {}) if m not in targets}
        names = [key]
        for t in sorted(ralias.get(key, ())):
            if t not in pdefs:
                homes |= {m for m in rdefs.get(t, {}) if m not in targets}
                names.append(t)
        if homes:
            put("VANISHED %s: %s drops it and its new home %s is not in this deploy "
                "(the game copy there predates the move)\n      fix: %s"
                % (_k(key), ", ".join(sorted(predefs[key])), ", ".join(sorted(homes)),
                   cmd(sorted(homes | targets), False)), set(predefs[key]))
    return block, old


def held_fn(holds, name):
    pats = [h["pattern"] for h in holds]
    return lambda rel: any(fnmatch.fnmatch("%s/%s" % (name, rel), p) for p in pats)
