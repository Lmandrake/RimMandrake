"""costlist_resolve_check.py -- offline: does any ThingDef's costList name a ThingDef that will not exist?

Why: a costList entry naming an absent def stays null after RimWorld's SILENT cross-ref pass, and Minify
Everything's GenerateImpliedDefs postfix (Mass = sum of costList BaseMass) then NREs, which makes RimWorld reset
ModsConfig.xml to Core (FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO, 2026-10-10). A plain Defs scan cannot see it when a
PATCH removes the named def or adds the entry, so this builds the patched def tree for a whole mod list:

  combine every active mod's Defs (LoadFolders-aware) -> apply every active mod's Patches in load order (Add, Insert,
  Remove, Replace, Attribute*, AddModExtension, SetName, Sequence, Conditional, FindMod, Test; real XPath via lxml)
  -> drop MayRequire-unsatisfied defs/list children -> resolve ParentName inheritance -> check costLists.

Unsupported (custom-class) patch operations are listed, with whether their text mentions costList, so a clean
result says what it could not see. Run under Windows python (paths are Windows):
  cd <repo>; python.exe src/RimMandrake/Utils/costlist_resolve_check.py infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
  (append packageId=C:\\folder to load one mod from an undeployed copy, e.g. to prove a fix before deploying it)
"""
import glob
import os
import re
import sys
import time
from lxml import etree

ROOTS = [r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods',
         r'C:\Program Files (x86)\Steam\steamapps\workshop\content\294100']
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data'
VER = '1.6'
PARSER = etree.XMLParser(recover=True, remove_comments=True, remove_blank_text=True)


def parse(p):
    try:
        return etree.parse(p, PARSER).getroot()
    except Exception:
        return None


def index_mods():
    idx, names = {}, {}
    for r in ROOTS:
        for d in os.listdir(r):
            a = parse(os.path.join(r, d, 'About', 'About.xml'))
            if a is None:
                continue
            pid = (a.findtext('packageId') or '').strip().lower()
            if pid and pid not in idx:
                idx[pid] = os.path.join(r, d)
                names[pid] = (a.findtext('name') or '').strip()
    for dl in ['Core', 'Royalty', 'Ideology', 'Biotech', 'Anomaly', 'Odyssey']:
        pid = 'ludeon.rimworld' if dl == 'Core' else 'ludeon.rimworld.' + dl.lower()
        idx[pid] = os.path.join(GAME, dl)
        names[pid] = 'Core' if dl == 'Core' else dl
    return idx, names


def folders(d, aset):
    lf = parse(os.path.join(d, 'LoadFolders.xml'))
    if lf is not None:
        v = lf.find('v' + VER)
        if v is None:
            v = lf.find('default')
        if v is not None:
            out = []
            for li in v.findall('li'):
                ia, ina = li.get('IfModActive'), li.get('IfModNotActive')
                if ia and not any(x.strip().lower() in aset for x in ia.split(',')):
                    continue
                if ina and any(x.strip().lower() in aset for x in ina.split(',')):
                    continue
                out.append(os.path.join(d, (li.text or '').strip().strip('/\\')))
            return out
    out = [d]
    if os.path.isdir(os.path.join(d, 'Common')):
        out.append(os.path.join(d, 'Common'))
    vers = sorted(x for x in os.listdir(d) if re.fullmatch(r'\d+\.\d+', x) and float(x) <= float(VER))
    if vers:
        out.append(os.path.join(d, vers[-1]))
    return out


FAST = re.compile(r'^/?Defs/([A-Za-z0-9_.]+|\*)\[defName\s*=\s*["\']([^"\']+)["\']\](.*)$', re.S)
_INDEX = {'doc': None, 'map': None}
TYPED = re.compile(r'^/?Defs/([A-Za-z0-9_.]+)(/.+)$', re.S)
_COMPILED = {}


def invalidate():
    _INDEX['map'] = None


def register(el):
    """Keep the defName index current when a patch puts a new def at top level (removed defs are skipped at
    query time because their parent is gone)."""
    if _INDEX['map'] is not None and el.getparent() is not None and el.getparent().getparent() is None:
        dn = el.findtext('defName')
        if dn:
            _INDEX['map'].setdefault(dn.strip(), []).append(el)


def xp(doc, path):
    """XPath over the combined <Defs>. The common `Defs/Type[defName="X"]...` form goes through a defName index
    (exact same result, far faster on a 25k-def document); everything else is real XPath."""
    path = path.strip()
    m = FAST.match(path)
    if m and '[' not in m.group(3)[:1] and not m.group(3).startswith('/..'):
        if _INDEX['map'] is None or _INDEX['doc'] is not doc:
            idx = {}
            for el in doc.getroot():
                if isinstance(el.tag, str):
                    dn = el.findtext('defName')
                    if dn:
                        idx.setdefault(dn.strip(), []).append(el)
            _INDEX['map'], _INDEX['doc'] = idx, doc
        out = []
        for el in _INDEX['map'].get(m.group(2), []):
            if el.getparent() is None or (m.group(1) != '*' and el.tag != m.group(1)):
                continue
            if el.findtext('defName', '').strip() != m.group(2):
                continue
            rest = m.group(3)
            out.extend([el] if not rest else el.xpath('.' + rest))
        return out
    m = TYPED.match(path)
    if m:
        # `Defs/Type/...` or `Defs/Type//...`: libxml2 is pathologically slow on the 56k-child root, so walk the
        # top-level defs of that tag and run the compiled remainder on each (same node set, document order).
        comp = _COMPILED.get(m.group(2))
        if comp is None:
            comp = _COMPILED[m.group(2)] = etree.XPath('.' + m.group(2))
        out = []
        for el in doc.getroot():
            if el.tag == m.group(1):
                out.extend(comp(el))
        return out
    if not path.startswith('/'):
        path = '/' + path
    return doc.xpath(path)


class Sim:
    def __init__(self, doc, aset, active_names):
        self.doc, self.aset, self.active_names = doc, aset, active_names
        self.unsupported = []
        self.stats = {}

    def may(self, el):
        mr, ma = el.get('MayRequire'), el.get('MayRequireAnyOf')
        if mr and not all(x.strip().lower() in self.aset for x in mr.split(',')):
            return False
        if ma and not any(x.strip().lower() in self.aset for x in ma.split(',')):
            return False
        return True

    def apply(self, op, src):
        # PatchOperation.Apply (decompiled 1.6) applies <success> to EVERY op, nested ones included: Always -> true,
        # Never -> false, Invert -> !result. Ignoring it on a nested op failed whole Sequences/FindMods whose inner
        # Remove-then-Add is guarded by <success>Always</success> (AncientsAreRakata.xml, VQEPatients_AreRakata.xml).
        ok = self.apply_worker(op, src)
        mode = (op.findtext('success') or '').strip()
        return True if mode == 'Always' else False if mode == 'Never' else (not ok) if mode == 'Invert' else ok

    def apply_worker(self, op, src):
        cls = (op.get('Class') or '').split('.')[-1]
        self.stats[cls] = self.stats.get(cls, 0) + 1
        path = op.findtext('xpath')
        val = op.find('value')
        try:
            if cls == 'PatchOperationSequence':
                ops = op.find('operations')
                for li in (ops if ops is not None else []):
                    if not isinstance(li.tag, str) or not self.may(li):
                        continue
                    if not self.apply(li, src):
                        return False
                return True
            if cls == 'PatchOperationConditional':
                branch = op.find('match') if xp(self.doc, path) else op.find('nomatch')
                return self.apply(branch, src) if branch is not None else True
            if cls == 'PatchOperationFindMod':
                mods = [li.text.strip() for li in op.find('mods') if isinstance(li.tag, str) and li.text]
                ok = all(m in self.active_names for m in mods)
                branch = op.find('match') if ok else op.find('nomatch')
                return self.apply(branch, src) if branch is not None else True
            if cls == 'PatchOperationTest':
                return bool(xp(self.doc, path))
            if path is None:
                raise ValueError('no xpath')
            nodes = xp(self.doc, path)
            if not nodes:
                return False
            if path.rstrip().endswith('defName') or cls == 'PatchOperationSetName':
                invalidate()
            if cls == 'PatchOperationAdd':
                pre = (op.findtext('order') or '').strip() == 'Prepend'
                for n in nodes:
                    kids = [c for c in val] if val is not None else []
                    for i, c in enumerate(kids):
                        c2 = etree.fromstring(etree.tostring(c))
                        n.insert(i, c2) if pre else n.append(c2)
                        register(c2)
            elif cls == 'PatchOperationInsert':
                after = (op.findtext('order') or '').strip() == 'Append'
                for n in nodes:
                    kids = [etree.fromstring(etree.tostring(c)) for c in val]
                    if after:
                        for c in reversed(kids):
                            n.addnext(c)
                    else:
                        for c in kids:
                            n.addprevious(c)
                    for c in kids:
                        register(c)
            elif cls == 'PatchOperationRemove':
                for n in nodes:
                    p = n.getparent()
                    if p is not None:
                        p.remove(n)
            elif cls == 'PatchOperationReplace':
                for n in nodes:
                    p = n.getparent()
                    if p is None:
                        continue
                    for c in val:
                        c2 = etree.fromstring(etree.tostring(c))
                        n.addprevious(c2)
                        register(c2)
                    p.remove(n)
            elif cls == 'PatchOperationAddModExtension':
                for n in nodes:
                    me = n.find('modExtensions')
                    if me is None:
                        me = etree.SubElement(n, 'modExtensions')
                    for c in val:
                        me.append(etree.fromstring(etree.tostring(c)))
            elif cls in ('PatchOperationAttributeAdd', 'PatchOperationAttributeSet'):
                a, v = op.findtext('attribute'), op.findtext('value')
                for n in nodes:
                    if cls.endswith('Set') or n.get(a) is None:
                        n.set(a, v or '')
            elif cls == 'PatchOperationAttributeRemove':
                a = op.findtext('attribute')
                for n in nodes:
                    if a in n.attrib:
                        del n.attrib[a]
            elif cls == 'PatchOperationSetName':
                for n in nodes:
                    n.tag = op.findtext('name')
            else:
                raise ValueError('unsupported class')
            return True
        except Exception as e:
            txt = etree.tostring(op, encoding='unicode')
            self.unsupported.append((src, op.get('Class'), str(e)[:60], 'costList' in txt or 'CostList' in txt))
            return True


def main():
    mc = sys.argv[1]
    overrides = dict(a.split('=', 1) for a in sys.argv[2:] if '=' in a)   # packageId=folder: test an undeployed fix
    active = [li.text.strip().lower() for li in parse(mc).find('activeMods')]
    aset = set(active)
    idx, names = index_mods()
    for k, v in overrides.items():
        print('OVERRIDE %s -> %s' % (k, v))
        idx[k.lower()] = v
    active_names = {names[p] for p in active if p in idx}
    defs_root = etree.Element('Defs')
    mod_folders = []
    for p in active:
        if p not in idx:
            print('NOT INSTALLED', p)
            continue
        fos = folders(idx[p], aset)
        mod_folders.append((p, fos))
        for fo in fos:
            for f in sorted(glob.glob(os.path.join(fo, 'Defs', '**', '*.xml'), recursive=True)):
                r = parse(f)
                if r is None:
                    continue
                for el in r:
                    if isinstance(el.tag, str):
                        el.set('_mod', p)
                        defs_root.append(el)
    print('defs combined: %d' % len(defs_root), flush=True)
    doc = etree.ElementTree(defs_root)
    sim = Sim(doc, aset, active_names)
    nops = 0
    for p, fos in mod_folders:
        for fo in fos:
            for f in sorted(glob.glob(os.path.join(fo, 'Patches', '**', '*.xml'), recursive=True)):
                r = parse(f)
                if r is None:
                    continue
                for op in r:
                    if isinstance(op.tag, str) and op.tag == 'Operation':
                        nops += 1
                        if nops % 1000 == 0:
                            print('.. %d ops, at %s' % (nops, p), flush=True)
                        t0 = time.time()
                        sim.apply(op, p + ' ' + os.path.basename(f))
                        if time.time() - t0 > 3:
                            print('   slow op %.1fs %s %s' % (time.time() - t0, p, (op.findtext('xpath') or op.get('Class'))[:120]), flush=True)
    # MayRequire: whole defs, and children of any list (honoured by the list loader)
    for el in list(defs_root):
        if not sim.may(el):
            defs_root.remove(el)
    for el in defs_root.iter():
        for c in list(el):
            if isinstance(c.tag, str) and (c.get('MayRequire') or c.get('MayRequireAnyOf')) and not sim.may(c):
                el.remove(c)

    def is_thingdef(el):
        t = el.tag if isinstance(el.tag, str) else ''
        return 'ThingDef' in t or 'ThingDef' in (el.get('Class') or '')
    by_name = {}
    for el in defs_root:
        if isinstance(el.tag, str) and el.get('Name'):
            by_name[el.get('Name')] = el
    thing = {}
    for el in defs_root:
        if isinstance(el.tag, str) and is_thingdef(el) and el.findtext('defName'):
            if (el.get('Abstract') or '').lower() != 'true':
                thing[el.findtext('defName').strip()] = el

    def chain(el):
        out, seen = [el], set()
        while el is not None and el.get('ParentName') and el.get('ParentName') not in seen:
            seen.add(el.get('ParentName'))
            el = by_name.get(el.get('ParentName'))
            if el is not None:
                out.append(el)
        return out

    def resolved_costlist(el):
        names_ = []
        for e in chain(el):
            cl = e.find('costList')
            if cl is None:
                continue
            for c in cl:
                if not isinstance(c.tag, str):
                    continue
                n = (c.findtext('thingDef') or '').strip() if c.tag == 'li' else c.tag
                names_.append((n, e.findtext('defName') or e.get('Name')))
            if (cl.get('Inherit') or '').lower() == 'false':
                break
        return names_

    def first(el, path):
        for e in chain(el):
            v = e.find(path)
            if v is not None:
                return v
        return None
    implied = re.compile(r'^(Meat_|Corpse_|Minified|Blueprint_|Frame_|Egg)')
    print('active %d | defs %d | thingdefs %d | patch ops %d | unsupported %d' % (
        len(active), len(defs_root), len(thing), nops, len(sim.unsupported)))
    print('SANITY Steel %s ComponentIndustrial %s WoodLog %s' % (
        'Steel' in thing, 'ComponentIndustrial' in thing, 'WoodLog' in thing))
    hits = 0
    for dn, el in sorted(thing.items()):
        for n, frm in resolved_costlist(el):
            if n in thing:
                continue
            hits += 1
            mass_path = (first(el, 'graphicData') is not None and first(el, 'building') is not None
                         and first(el, 'building/mineableThing') is None and first(el, 'statBases/Mass') is None)
            tag = 'IMPLIED?' if implied.match(n) else 'MISSING'
            print('%s %-40s in %-45s (list from %s, mod %s)%s' % (
                tag, n, dn, frm, el.get('_mod'), '  <-- MINIFY MASS PATH' if mass_path else ''))
    print('costList misses: %d' % hits)
    for u in sim.unsupported:
        if u[3]:
            print('UNSUPPORTED-OP mentions costList:', u)
    print('unsupported op classes:', sorted({u[1] for u in sim.unsupported})[:40])


if __name__ == '__main__':
    main()
