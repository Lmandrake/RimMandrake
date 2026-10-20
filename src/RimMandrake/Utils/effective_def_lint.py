#!/usr/bin/env python3
r"""effective_def_lint.py -- offline load-killer and cost-reference lint over the PATCHED def tree of a whole mod list.

WHY. A def that is valid in its own file can be made fatal by a later PATCH (a material removed, an entry added, a
whole def replaced) or by INHERITANCE, and a raw-XML scan cannot see it. Every load killer in this project's history
cost a 15-minute cold load and usually a Core-only ModsConfig reset (bridge_debugging_system.md section 4 rows 24, 30,
33, 37, 41, 53, 58, 66; FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO, 2026-10-10). This builds the effective tree once (the
engine of costlist_resolve_check.py: combine every active mod's Defs, LoadFolders-aware -> apply every Patches op in
load order -> drop MayRequire-unsatisfied defs and list children -> resolve ParentName) and runs every check over it.

    python.exe src/RimMandrake/Utils/effective_def_lint.py infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
    python3    src/RimMandrake/Utils/effective_def_lint.py --src-only          # the repo-only C#/csproj checks, ~2 s
    ... [--json out.json] [--no-cache] [packageId=C:\folder ...]   (an override loads one mod from an undeployed copy)

Run the full tree under Windows python.exe from the repo root with RELATIVE paths: it reads ~1,400 mod folders, and
drvfs from WSL is several times slower. Both interpreters work (paths come from game_paths).

CACHE. The result is keyed on the CONTENT of every Defs/Patches/About/LoadFolders file read (sha256), the ordered
mod list, the overrides and this script's own source. File shas are memoised by (path, size, mtime_ns), the way git's
index does, so a repeat run only stats files. Cache: D:\ClaudeWork\rimmandrake\scratch\effective_def_lint\ (outside git; a
program reads it).

SEVERITY. `crash` = a VERIFIED engine path dereferences the bad value during load (each names its path, checked
against decompiled 1.6). `error` = the engine logs an error / discards a def / the reference is dead, crash not
proven. `warn` = suspicious, judgement needed. A check FAILs on any crash or error finding in scope.

CHECKS (name: what, scope)
  costlist        costList/costListForDifficulty material names no surviving ThingDef. crash when the def has a
                  recipeMaker (RecipeDefGenerator.SetIngredients -> ThingFilter.SetAllow(null) -> null.virtualDefs,
                  runs AFTER the silent cross-ref pass) or is on Minify Everything's Mass path; else error.
  recipe_refs     RecipeDef ingredient filter thingDefs / fixedIngredientFilter / products name no ThingDef (error).
  stuff_refs      defaultStuff (ThingDef) and stuffCategories / stuffProps.categories (StuffCategoryDef) dead (error).
  removed_refs    a def OUR patches remove (PatchOperationRemove of a whole def) is still named somewhere (error).
  op_mayrequire   MayRequire on a top-level <Operation> is IGNORED by the engine; FAIL when the named mod is absent.
  drug_comp       ThingDef with a drugCategory other than None and no CompProperties_Drug (crash: DrugPolicy ctor).
  pawnkind_race   PawnKindDef whose race names no surviving ThingDef (crash: GeneticRim cctor / pawn generation).
  biome_worker    BiomeDef without workerClass (crash: worldgen tile scoring).
  biomeworker_rivers  our C# BiomeWorker touching .Rivers (NRE during WorldGenStep_Terrain), repo source.
  member_mayrequire   MayRequire naming a composed member packageId of mandrake.rm.biomes (never satisfied).
  li_custom_loader    <li> inside wildAnimals/wildPlants/pollutionWildAnimals (custom loader; discards the def).
  plant_purpose   plant.purpose outside the PlantPurpose enum {Food, Health, Beauty, Misc} (def discarded).
  faction_name    non-abstract FactionDef with no fixedName / name maker / allowedCultures (NRE naming it).
  alert_leaf      our abstract Alert subclass with no concrete subclass (AlertsReadout ctor instantiates leaves).
  compile_include .cs file not listed in a csproj with EnableDefaultCompileItems=false (compiles into nothing).
  failed_ops      OUR unguarded patch ops that match nothing (target def or target mod absent): logs an error.

UNSUPPORTED (reported, never silently passed): types named by donor-mod XML (ModExtension, compClass, workerClass
from an absent assembly -- only OUR namespaces are checked, by lint_def_type_refs.py); custom-class patch operations
(counted, with whether they touch costList); C# def generators and runtime removers; list-merge subtleties beyond
Inherit="False". A post-startup resolved-def audit in the live game is the backstop for those.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import glob
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

VERSION = 4
PLANT_PURPOSE = {'Food', 'Health', 'Beauty', 'Misc'}
WILD_LISTS = ('wildAnimals', 'wildPlants', 'pollutionWildAnimals')
OURS = re.compile(r'^mandrake\.')
IMPLIED = re.compile(r'^(Meat_|Corpse_|Minified|Blueprint_|Frame_|Egg|Techprint_)')


def cache_dir():
    if os.environ.get('EDL_CACHE'):
        return os.environ['EDL_CACHE']
    # by platform: game_paths.resolve returns the Windows spelling while the WSL dir does not exist yet
    return rm_win("scratch", "effective_def_lint") if os.name == 'nt' else rm_str("scratch", "effective_def_lint")


# ---------------------------------------------------------------------------------------------------------- findings
class Report:
    def __init__(self):
        self.checks = {}      # name -> dict(status, findings, note)

    def add(self, name, findings, note='', status=None, scope=None):
        bad = [f for f in findings if f['sev'] in ('crash', 'error') and (scope is None or scope(f))]
        st = status or ('FAIL' if bad else 'PASS')
        self.checks[name] = {'status': st, 'findings': findings, 'note': note, 'counted': len(bad)}

    def failed(self):
        return [n for n, c in self.checks.items() if c['status'] == 'FAIL']


def F(sev, mod, d, detail, **kw):
    out = {'sev': sev, 'mod': mod or '?', 'def': d or '?', 'detail': detail}
    out.update(kw)
    return out


# ------------------------------------------------------------------------------------------------ repo-only checks
def _cs_files():
    for root, dirs, files in os.walk(os.path.join(REPO, 'src')):
        dirs[:] = [d for d in dirs if d not in ('obj', 'bin', '.git', '__pycache__', 'node_modules')]
        for f in files:
            if f.endswith('.cs'):
                yield os.path.join(root, f)


CLASS_RE = re.compile(r'\b(?P<mods>(?:public|internal|private|protected|abstract|sealed|static|partial)\s+)*class\s+'
                      r'(?P<name>\w+)(?:<[^>{]*>)?\s*:\s*(?P<base>[\w.]+)')


def check_src(report, texts=None):
    """BiomeWorker .Rivers, abstract Alert leaves, csproj Compile Include. texts: {path: source} for selftests."""
    if texts is None:
        texts = {}
        for p in _cs_files():
            try:
                with open(p, encoding='utf-8-sig', errors='replace') as fh:
                    texts[p] = fh.read()
            except OSError:
                pass
    rivers, classes = [], {}
    for p, t in texts.items():
        for m in CLASS_RE.finditer(t):
            classes[m.group('name')] = (m.group('base').split('.')[-1], 'abstract' in (m.group('mods') or ''), p)
            if m.group('base').split('.')[-1] == 'BiomeWorker':
                # the class body up to the next top-level class declaration
                body = t[m.end(): (CLASS_RE.search(t, m.end()) or re.compile('$').search(t)).start()]
                if re.search(r'\.Rivers\b', body):
                    rivers.append(F('crash', os.path.relpath(p, REPO), m.group('name'),
                                    'BiomeWorker reads .Rivers; the biome is not assigned during WorldGenStep_Terrain '
                                    '(NRE kills worldgen) -- read potentialRivers instead'))
    report.add('biomeworker_rivers', rivers, 'repo C# source, text match on the class body')

    def derives_alert(n, seen=()):
        b = classes.get(n)
        if b is None or n in seen:
            return False
        return b[0] in ('Alert', 'Alert_Critical') or derives_alert(b[0], seen + (n,))
    leaves = []
    for n, (base, abstract, p) in classes.items():
        if abstract and derives_alert(n) and not any(b == n for b, _, _ in classes.values()):
            leaves.append(F('crash', os.path.relpath(p, REPO), n, 'abstract Alert subclass with no concrete subclass: '
                            'AlertsReadout instantiates every leaf type, so map-add throws'))
    report.add('alert_leaf', leaves, 'repo C# source; inheritance only within our files')

    missing = []
    for proj in glob.glob(os.path.join(REPO, 'src', '**', '*.csproj'), recursive=True):
        try:
            x = open(proj, encoding='utf-8-sig', errors='replace').read()
        except OSError:
            continue
        if not re.search(r'<EnableDefaultCompileItems>\s*false', x, re.I):
            continue
        pd = os.path.dirname(proj)
        listed = set()
        for inc in re.findall(r'<Compile\s+Include="([^"]+)"', x):
            inc = inc.replace('\\', '/')
            for g in glob.glob(os.path.join(pd, inc), recursive=True):
                listed.add(os.path.normcase(os.path.abspath(g)))
        for root, dirs, files in os.walk(pd):
            if root != pd and glob.glob(os.path.join(root, '*.csproj')):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d not in ('obj', 'bin')]
            for f in files:
                raw = os.path.abspath(os.path.join(root, f))
                fp = os.path.normcase(raw)      # compare normcased, but OPEN the raw path (\\wsl.localhost is case-sensitive)
                if f.endswith('.cs') and fp not in listed:
                    try:
                        head = open(raw, encoding='utf-8-sig', errors='replace').read(1500)
                    except OSError:
                        head = ''
                    deliberate = re.search(r'deliberately NOT in|NOT-COMPILED', head, re.I)
                    missing.append(F('warn' if deliberate else 'error', os.path.relpath(proj, REPO), os.path.relpath(raw, REPO),
                                     'not in any <Compile Include>: compiles into nothing, no build error'))
    report.add('compile_include', missing, 'every csproj with EnableDefaultCompileItems=false')


# --------------------------------------------------------------------------------------------------- tree building
class Hasher:
    """Content sha per file, memoised by (size, mtime_ns)."""
    def __init__(self, memo):
        self.memo, self.used = memo, {}

    def read(self, path):
        st = os.stat(path)
        with open(path, 'rb') as fh:
            data = fh.read()
        m = self.memo.get(path)
        if m and m[0] == st.st_size and m[1] == st.st_mtime_ns:
            sha = m[2]
        else:
            sha = hashlib.sha256(data).hexdigest()
            self.memo[path] = [st.st_size, st.st_mtime_ns, sha]
        self.used[path] = sha
        return data

    def sha_only(self, path):
        st = os.stat(path)
        m = self.memo.get(path)
        if m and m[0] == st.st_size and m[1] == st.st_mtime_ns:
            self.used[path] = m[2]
            return m[2]
        self.read(path)
        return self.used[path]


def mod_files(crc, active, idx, aset):
    """[(packageId, [folders], [defs files], [patch files])] in load order."""
    out = []
    for p in active:
        if p not in idx:
            continue
        fos = crc.folders(idx[p], aset)
        defs, pats = [], []
        for fo in fos:
            # a DIRECTORY can be named *.xml (workshop 2884115974 ships Defs/InteractionDefs.xml/), so isfile
            defs += sorted(f for f in glob.glob(os.path.join(fo, 'Defs', '**', '*.xml'), recursive=True) if os.path.isfile(f))
            pats += sorted(f for f in glob.glob(os.path.join(fo, 'Patches', '**', '*.xml'), recursive=True)
                           if os.path.isfile(f))
        out.append((p, fos, defs, pats))
    return out


def cache_key(hasher, modlist_ids, overrides, files):
    h = hashlib.sha256()
    h.update(json.dumps([VERSION, modlist_ids, sorted(overrides.items())]).encode())
    for src in (__file__, os.path.join(HERE, 'costlist_resolve_check.py')):
        with open(src, 'rb') as fh:
            h.update(hashlib.sha256(fh.read()).digest())
    for f in files:
        h.update(f.encode('utf-8', 'replace'))
        h.update(hasher.sha_only(f).encode())
    return h.hexdigest()


def build_and_check(mc_path, overrides, report, progress=print):
    import costlist_resolve_check as crc
    from lxml import etree
    import game_paths as gp
    # EDL_ROOTS / EDL_GAME: fixture mod roots for the selftest (os.pathsep-separated)
    crc.ROOTS = os.environ['EDL_ROOTS'].split(os.pathsep) if os.environ.get('EDL_ROOTS') else [gp.LOCAL_MODS, gp.WORKSHOP]
    crc.GAME = os.environ.get('EDL_GAME') or gp.GAME_DATA
    if mc_path.lower().endswith('.json'):                      # a modmanifest.py manifest.<NAME>.json
        active = [x.strip().lower() for x in json.load(open(mc_path, encoding='utf-8'))['ids']]
    else:
        active = [li.text.strip().lower() for li in crc.parse(mc_path).find('activeMods') if isinstance(li.tag, str)]
    aset = set(active)
    idx, names = crc.index_mods()
    for k, v in overrides.items():
        idx[k.lower()] = v
    absent = [p for p in active if p not in idx]
    active_names = {names[p] for p in active if p in idx}
    mods = mod_files(crc, active, idx, aset)
    files = [f for _, _, d, pt in mods for f in d + pt]
    progress('mods %d (not installed %d) | files %d' % (len(mods), len(absent), len(files)))

    cdir = cache_dir()
    os.makedirs(cdir, exist_ok=True)
    memo_p = os.path.join(cdir, 'filesha_memo.json')
    try:
        memo = json.load(open(memo_p))
    except Exception:
        memo = {}
    hasher = Hasher(memo)
    t0 = time.time()
    key = cache_key(hasher, active, overrides, files)
    progress('content key %s (%.0fs)' % (key[:16], time.time() - t0))
    json.dump(memo, open(memo_p, 'w'))
    res_p = os.path.join(cdir, 'result_%s.json' % key[:32])
    if getattr(report, 'cache_only', False) and not os.path.exists(res_p):
        print('CACHE-MISS %s' % res_p)
        raise SystemExit(4)
    if report is not None and getattr(report, 'use_cache', True) and os.path.exists(res_p):
        cached = json.load(open(res_p))
        report.checks.update(cached['checks'])
        report.meta = cached['meta']
        report.meta['cache'] = 'HIT ' + res_p
        return report

    parser = crc.PARSER
    defs_root = etree.Element('Defs')
    for p, fos, defs, pats in mods:
        for f in defs:
            try:
                r = etree.fromstring(hasher.read(f), parser)
            except Exception:
                r = None
            if r is None:
                continue
            for el in r:
                if isinstance(el.tag, str):
                    el.set('_mod', p)
                    defs_root.append(el)
    progress('defs combined: %d' % len(defs_root))
    doc = etree.ElementTree(defs_root)

    removed = {}            # defName -> (mod, file) removed by OUR patch
    failed_ops, op_mayreq = [], []

    class LintSim(crc.Sim):
        cur_mod = ''

        def apply(self, op, src):
            cls = (op.get('Class') or '').split('.')[-1]
            if cls == 'PatchOperationRemove' and OURS.match(self.cur_mod):
                m = crc.FAST.match((op.findtext('xpath') or '').strip())
                if m and not m.group(3).strip():
                    removed.setdefault(m.group(2), (self.cur_mod, src))
            return super().apply(op, src)

    sim = LintSim(doc, aset, active_names)
    nops = 0
    for p, fos, defs, pats in mods:
        sim.cur_mod = p
        for f in pats:
            try:
                r = etree.fromstring(hasher.read(f), parser)
            except Exception:
                r = None
            if r is None:
                continue
            for op in r:
                if not (isinstance(op.tag, str) and op.tag == 'Operation'):
                    continue
                nops += 1
                if nops % 2000 == 0:
                    progress('.. %d ops, at %s' % (nops, p))
                src = p + ' ' + os.path.basename(f)
                mr = op.get('MayRequire') or op.get('MayRequireAnyOf')
                if mr:
                    gone = [x.strip().lower() for x in mr.split(',') if x.strip().lower() not in aset]
                    unsat = (gone and op.get('MayRequire')) or (op.get('MayRequireAnyOf') and len(gone) == len(mr.split(',')))
                    # ours: an error (CLAUDE.md, live-hit 2026-09-27); a donor's: the op runs and at worst logs a
                    # failed-patch error, so warn
                    sev = 'error' if unsat and OURS.match(p) else 'warn'
                    op_mayreq.append(F(sev, p, os.path.basename(f), 'top-level <Operation MayRequire="%s"> is ignored by '
                                       'the engine; %s' % (mr, ('named mod ABSENT, op applies anyway: ' + ','.join(gone))
                                                           if sev == 'error' else 'named mod present, so harmless today')))
                n0 = len(defs_root)
                ok = sim.apply(op, src)
                k = len(defs_root) - n0
                if k > 0:                         # a patch created top-level defs: give them provenance
                    tagged = 0
                    for el in defs_root[-k:]:     # an Add to /Defs appends; only an Insert needs the full scan
                        if isinstance(el.tag, str) and el.get('_mod') is None:
                            el.set('_mod', p)
                            el.set('_by_patch', os.path.basename(f))
                            tagged += 1
                    if tagged < k:
                        for el in defs_root:
                            if isinstance(el.tag, str) and el.get('_mod') is None:
                                el.set('_mod', p)
                                el.set('_by_patch', os.path.basename(f))
                if not ok and OURS.match(p) and (op.findtext('success') or '').strip() != 'Always':
                    failed_ops.append(F('error', p, os.path.basename(f), 'matched nothing: %s %s' % (
                        (op.get('Class') or '').split('.')[-1], (op.findtext('xpath') or '')[:140])))
    progress('patch ops %d | unsupported %d' % (nops, len(sim.unsupported)))
    json.dump(hasher.memo, open(memo_p, 'w'))

    # MayRequire honoured by the loader on whole defs and list children
    for el in list(defs_root):
        if not sim.may(el):
            defs_root.remove(el)
    members = composed_members()
    member_findings, _ = member_scan(defs_root, members)
    # collect THEN remove: removing while lxml's iter() is live silently ends the walk early (the costlist_resolve_check
    # original did that, so MayRequire-guarded costList entries of later defs survived and read as misses)
    kill = [c for c in defs_root.iter() if isinstance(c.tag, str) and c.getparent() is not None
            and (c.get('MayRequire') or c.get('MayRequireAnyOf')) and not sim.may(c)]
    for c in kill:
        if c.getparent() is not None:
            c.getparent().remove(c)

    run_tree_checks(report, defs_root, sim, removed, failed_ops, op_mayreq, active, absent, members=members,
                    member_findings=member_findings)
    report.meta = {'modlist': mc_path, 'active': len(active), 'not_installed': absent, 'defs': len(defs_root),
                   'patch_ops': nops, 'unsupported_ops': len(sim.unsupported), 'key': key, 'when': time.strftime(
                       '%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'cache': 'MISS'}
    json.dump({'checks': report.checks, 'meta': report.meta}, open(res_p, 'w'))
    return report


def run_tree_checks(report, defs_root, sim, removed, failed_ops, op_mayreq, active, absent, members=None,
                    member_findings=None):
    """Every effective-tree check. Split from the build so a selftest can drive it on a tiny fixture tree."""
    by_name, by_tag = {}, {}
    for el in defs_root:
        if not isinstance(el.tag, str):
            continue
        if el.get('Name'):
            by_name[el.get('Name')] = el
        by_tag.setdefault(el.tag, []).append(el)

    def concrete(tag_pred):
        for el in defs_root:
            if isinstance(el.tag, str) and tag_pred(el) and (el.get('Abstract') or '').lower() != 'true':
                yield el

    def is_thing(el):
        return 'ThingDef' in el.tag or 'ThingDef' in (el.get('Class') or '')

    def chain(el):
        out, seen = [el], set()
        while el is not None and el.get('ParentName') and el.get('ParentName') not in seen:
            seen.add(el.get('ParentName'))
            el = by_name.get(el.get('ParentName'))
            if el is not None:
                out.append(el)
        return out

    def first(el, path):
        for e in chain(el):
            v = e.find(path)
            if v is not None:
                return v
        return None

    def ftext(el, path):
        v = first(el, path)
        return (v.text or '').strip() if v is not None else None

    def dn(el):
        return (el.findtext('defName') or el.get('Name') or '?').strip()

    things = {dn(el): el for el in concrete(is_thing) if el.findtext('defName')}
    alldefs = {}
    for el in defs_root:
        if isinstance(el.tag, str) and el.findtext('defName'):
            alldefs.setdefault(el.findtext('defName').strip(), el)

    def thing_ok(n):
        return n in things or bool(IMPLIED.match(n))

    sanity = {k: k in things for k in ('Steel', 'ComponentIndustrial', 'WoodLog', 'Beer')}
    minify = 'mlie.minifyeverything' in active or any('minifyeverything' in a for a in active)

    # costlist ---------------------------------------------------------------------------------------------------
    out = []
    for d, el in sorted(things.items()):
        seen = set()
        for path in ('costList', 'costListForDifficulty/costList'):
            for e in chain(el):
                cl = e.find(path)
                if cl is None:
                    continue
                for c in cl:
                    if not isinstance(c.tag, str):
                        continue
                    n = (c.findtext('thingDef') or '').strip() if c.tag == 'li' else c.tag
                    if not n or thing_ok(n) or (n, path) in seen:
                        continue
                    seen.add((n, path))
                    recipe = first(el, 'recipeMaker') is not None
                    mass = (minify and first(el, 'graphicData') is not None and first(el, 'building') is not None
                            and first(el, 'building/mineableThing') is None and first(el, 'statBases/Mass') is None)
                    paths = (['RECIPE: RecipeDefGenerator.SetIngredients -> SetAllow(null)'] if recipe else []) + \
                            (['MINIFY MASS: Minify Everything implied-def postfix'] if mass else [])
                    out.append(F('crash' if paths else 'error', el.get('_mod'), d, '%s material %s resolves to no '
                                 'ThingDef (list from %s)%s' % (path, n, dn(e), (' <-- ' + '; '.join(paths)) if paths else
                                                                ' -- logs an error; no load-time consumer found'),
                                 material=n, list_from=dn(e), list_mod=e.get('_mod')))
                if (cl.get('Inherit') or '').lower() == 'false':
                    break
    report.add('costlist', out, 'sanity: %s' % sanity, status=None if all(sanity.values()) else 'UNMEASURED')

    # recipe_refs ------------------------------------------------------------------------------------------------
    out = []
    for el in concrete(lambda e: e.tag == 'RecipeDef'):
        for path in ('ingredients/li/filter/thingDefs/li', 'fixedIngredientFilter/thingDefs/li',
                     'defaultIngredientFilter/thingDefs/li'):
            v = None
            for e in chain(el):
                if e.find(path.split('/')[0]) is not None:
                    v = e.findall(path)
                    break
            for li in v or []:
                n = (li.text or '').strip()
                if n and not thing_ok(n):
                    out.append(F('error', el.get('_mod'), dn(el), '%s names %s: no ThingDef (dropped with an error)'
                                 % (path.split('/')[0], n)))
        pr = first(el, 'products')
        for c in (pr if pr is not None else []):
            if isinstance(c.tag, str):
                n = (c.findtext('thingDef') or '').strip() if c.tag == 'li' else c.tag
                if n and not thing_ok(n):
                    out.append(F('error', el.get('_mod'), dn(el), 'products names %s: no ThingDef (null product)' % n))
    report.add('recipe_refs', out)

    # stuff_refs -------------------------------------------------------------------------------------------------
    cats = {dn(e) for e in by_tag.get('StuffCategoryDef', [])}
    out = []
    for d, el in things.items():
        ds = ftext(el, 'defaultStuff')
        if ds and not thing_ok(ds):
            out.append(F('error', el.get('_mod'), d, 'defaultStuff %s: no ThingDef' % ds))
        for path in ('stuffCategories', 'stuffProps/categories'):
            v = first(el, path)
            for li in (v if v is not None else []):
                if isinstance(li.tag, str) and (li.text or '').strip() and li.text.strip() not in cats:
                    out.append(F('error', el.get('_mod'), d, '%s names %s: no StuffCategoryDef' % (path, li.text.strip())))
    report.add('stuff_refs', out, 'StuffCategoryDefs %d' % len(cats))

    # removed_refs -----------------------------------------------------------------------------------------------
    out = []
    gone = {n: v for n, v in removed.items() if n not in alldefs}
    if gone:
        for el in defs_root:
            if not isinstance(el.tag, str):
                continue
            for x in el.iter():
                if not isinstance(x.tag, str) or x.tag in ('defName', 'from'):   # <from>: alias tables name it on purpose
                    continue
                t = (x.text or '').strip()
                hit = t if t in gone else (x.tag if x.tag in gone else None)
                if hit:
                    out.append(F('error', el.get('_mod'), dn(el), 'names %s, which %s removes (%s)' % (
                        hit, gone[hit][0], gone[hit][1].split(' ', 1)[-1]), at=x.tag))
    report.add('removed_refs', out, '%d whole defs removed by our patches' % len(gone))

    report.add('op_mayrequire', op_mayreq)

    # drug_comp --------------------------------------------------------------------------------------------------
    out = []
    for d, el in things.items():
        cat = ftext(el, 'ingestible/drugCategory')
        if cat and cat != 'None':
            has = any('CompProperties_Drug' in (li.get('Class') or '') for e in chain(el)
                      for comps in [e.find('comps')] if comps is not None for li in comps)
            if not has:
                out.append(F('crash', el.get('_mod'), d, 'drugCategory %s but no CompProperties_Drug '
                             '(DrugPolicy.InitializeIfNeeded NRE in the Game ctor)' % cat))
    report.add('drug_comp', out, 'sanity Beer present=%s' % sanity['Beer'])

    # pawnkind_race ----------------------------------------------------------------------------------------------
    out = []
    for el in concrete(lambda e: e.tag == 'PawnKindDef' or 'PawnKindDef' in (e.get('Class') or '')):
        r = ftext(el, 'race')
        if r and r not in things:
            out.append(F('crash', el.get('_mod'), dn(el), 'race %s resolves to no ThingDef (raceless PawnKindDef: '
                         'GeneticRim.Core cctor / starting-pawn generation)' % r))
    report.add('pawnkind_race', out)

    # biome_worker / li_custom_loader ------------------------------------------------------------------------------
    out, li = [], []
    for el in concrete(lambda e: e.tag == 'BiomeDef'):
        # WorldGenStep_Terrain calls Worker only when implemented && generatesNaturally (decompiled 1.6, line ~296);
        # pocket-map biomes (Underground, Labyrinth, MetalHell) legitimately have no workerClass
        if ftext(el, 'implemented') == 'false' or ftext(el, 'generatesNaturally') == 'false':
            continue
        if not ftext(el, 'workerClass'):
            out.append(F('crash', el.get('_mod'), dn(el), 'BiomeDef has no workerClass (worldgen scoring NRE)'))
    for el in by_tag.get('BiomeDef', []):
        for w in WILD_LISTS:
            v = el.find(w)
            if v is not None and any(isinstance(c.tag, str) and c.tag == 'li' for c in v):
                li.append(F('error', el.get('_mod'), dn(el), '<li> inside %s: custom loader reads the node NAME as '
                            'the def, so the def is discarded' % w))
    report.add('biome_worker', out)
    report.add('li_custom_loader', li)

    # member_mayrequire: scanned BEFORE MayRequire stripping (an unsatisfiable member id strips the element silently,
    # which is the very defect), so the build passes it in; a fixture tree can let it scan here
    if member_findings is None:
        member_findings, members = member_scan(defs_root, members)
    else:
        members = members if members is not None else composed_members()
    report.add('member_mayrequire', member_findings, '%d member ids' % len(members or ()),
               status=None if members else 'UNMEASURED')

    # plant_purpose / faction_name ----------------------------------------------------------------------------------
    out = []
    for d, el in things.items():
        pp = ftext(el, 'plant/purpose')
        if pp is not None and pp not in PLANT_PURPOSE:
            out.append(F('error', el.get('_mod'), d, 'plant.purpose %r is not a PlantPurpose; the ThingDef is '
                         'discarded' % pp))
    report.add('plant_purpose', out)
    out = []
    for el in concrete(lambda e: e.tag == 'FactionDef'):
        if not any(first(el, k) is not None for k in ('fixedName', 'factionNameMaker', 'factionNameMakerFemale',
                                                         'allowedCultures', 'isPlayer')):
            out.append(F('warn' if not OURS.match(el.get('_mod') or '') else 'error', el.get('_mod'), dn(el),
                         'FactionDef has no fixedName / factionNameMaker / allowedCultures (bare NRE naming it)'))
    report.add('faction_name', out, 'error for our mods, warn for others (calibrated against vanilla)')

    report.add('failed_ops', failed_ops, 'our mods only; <success>Always</success> exempt')

    # unsupported: honest scope
    ucost = [u for u in sim.unsupported if u[3]]
    report.add('unsupported_patch_ops', [F('warn', u[0].split(' ')[0], u[0], '%s: %s%s' % (
        u[1], u[2], ' (mentions costList)' if u[3] else '')) for u in sim.unsupported[:200]],
        '%d custom-class ops not simulated, %d mention costList' % (len(sim.unsupported), len(ucost)),
        status='UNSUPPORTED' if sim.unsupported else 'PASS')
    report.add('donor_types', [], 'XML naming types from donor assemblies cannot be resolved offline; our namespaces '
               'are lint_def_type_refs.py', status='UNSUPPORTED')


def member_scan(defs_root, members=None):
    if members is None:
        members = composed_members()
    out = []
    for el in defs_root.iter():
        if not isinstance(el.tag, str):
            continue
        for a in ('MayRequire', 'MayRequireAnyOf'):
            v = el.get(a)
            ids = [x.strip().lower() for x in (v or '').split(',') if x.strip()]
            # MayRequire: any member id kills it. AnyOf: only when no listed id is a real packageId
            if ids and (any(i in members for i in ids) if a == 'MayRequire' else all(i in members for i in ids)):
                top = el
                while top.getparent() is not None and top.getparent().getparent() is not None:
                    top = top.getparent()
                out.append(F('error', top.get('_mod'), (top.findtext('defName') or top.get('Name') or '?').strip(),
                             '%s="%s" names a composed member of mandrake.rm.biomes, which has no runtime packageId '
                             '(the element is silently never loaded)' % (a, v)))
    return out, members


def composed_members():
    try:
        d = json.load(open(os.path.join(REPO, 'src', 'RimMandrake', 'Biomes.compose.json')))
    except Exception:
        return set()
    out = set()
    for e in d.get('entries', []):
        if e.get('wave', 99) > d.get('compose_wave', 0):
            continue
        p = os.path.join(REPO, 'src', 'RimMandrake', e['source'], 'About', 'About.xml')
        try:                                     # parsed: a regex takes the first <packageId>, often a dependency's
            import xml.etree.ElementTree as ET
            v = (ET.parse(p).getroot().findtext('packageId') or '').strip().lower()
        except Exception:                        # noqa: BLE001
            continue
        if v:
            out.add(v)
    out.discard('mandrake.rm.biomes')
    return out


# ------------------------------------------------------------------------------------------------------------ CLI
def print_report(report, limit=12, out=sys.stdout):
    for name, c in report.checks.items():
        fs = c['findings']
        crash = sum(1 for f in fs if f['sev'] == 'crash')
        print('%-11s %-20s %4d findings (%d crash) %s' % (c['status'], name, len(fs), crash,
                                                         ('-- ' + c['note']) if c['note'] else ''), file=out)
        for f in sorted(fs, key=lambda f: (f['sev'] != 'crash', f['sev'] != 'error'))[:limit]:
            print('     %-5s %-34s %-36s %s' % (f['sev'], f['mod'][:34], f['def'][:36], f['detail'][:170]), file=out)
        if len(fs) > limit:
            print('     ... %d more (use --json)' % (len(fs) - limit), file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('modsconfig', nargs='?', help='a ModsConfig.xml, or a modmanifest manifest.<NAME>.json')
    ap.add_argument('overrides', nargs='*', help='packageId=folder')
    ap.add_argument('--src-only', action='store_true')
    ap.add_argument('--no-cache', action='store_true')
    ap.add_argument('--cache-only', action='store_true', help='print the cached result or CACHE-MISS (exit 4); never build')
    ap.add_argument('--json')
    ap.add_argument('--limit', type=int, default=12)
    a = ap.parse_args(argv)
    rep = Report()
    rep.use_cache = not a.no_cache
    rep.cache_only = a.cache_only
    rep.meta = {}
    check_src(rep)
    if not a.src_only:
        if not a.modsconfig:
            ap.error('modsconfig required unless --src-only')
        ov = dict(x.split('=', 1) for x in a.overrides if '=' in x)
        t0 = time.time()
        build_and_check(a.modsconfig, ov, rep, progress=lambda s: print('[%4.0fs] %s' % (time.time() - t0, s),
                                                                         flush=True))
        print('meta: %s' % json.dumps({k: v for k, v in rep.meta.items() if k != 'not_installed'}))
        if rep.meta.get('not_installed'):
            print('NOT INSTALLED: %s' % ', '.join(rep.meta['not_installed']))
    print_report(rep, a.limit)
    if a.json:
        if os.path.dirname(a.json):
            os.makedirs(os.path.dirname(a.json), exist_ok=True)
        json.dump({'checks': rep.checks, 'meta': rep.meta}, open(a.json, 'w'), indent=1)
    bad = rep.failed()
    print('VERDICT %s' % ('FAIL ' + ','.join(bad) if bad else 'PASS'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
