#!/usr/bin/env python3
"""retarget_donor_patch.py - migrate PatchOperations that name a DONOR def (or sit behind a donor-NAME FindMod gate)
onto the def of ours that replaced it. Phase 0 cleanup 2026-10-15. Dry run unless --write.

    python3 design/Jawa/mods/retarget_donor_patch.py [--write] [--top] [--ctx=FILE]... PATCH.xml...

Per operation, using design/Jawa/mods/donor_name_map.py (donor name -> ours | null) and our raw src Defs:
  donor-only (no twin)                       dropped
  target has no node in OUR raw def          dropped (a Replace/Add that matches nothing; ours was ported with it baked)
  ours already holds the patch's value       dropped (baked) ; identical op already in the file or a --ctx file: dropped
  otherwise                                  retargeted to the twin
A donor-name FindMod gate is removed and every op it held is wrapped in a Conditional on its own target def
existing (no mod-name guard to drift). --top also processes ungated top-level ops (a file of bare Conditionals).
Not a generator: the three big generated files (MegafaunaYield.xml, Armour_Leather.xml, PawnFlavorPhase2_ThoughtDef.xml)
no longer reproduce from their generators' dump scans, so they were migrated with this instead; a regeneration
re-emits donor names and must be followed by this tool.
"""
import sys, re, glob, os, collections
from lxml import etree
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import donor_name_map as dnm
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), 'src')
DONOR_MODS = {"Star Wars Animal Collection (Continued)", "Alpha Animals"}
DEFRE = re.compile(r'defName="([^"]+)"')

_corpus = None
def corpus():
    global _corpus
    if _corpus is None:
        root = etree.Element('Defs')
        for f in glob.glob(SRC + '/**/Defs/**/*.xml', recursive=True):
            try:
                r = etree.parse(f).getroot()
            except Exception:
                continue
            for d in r:
                if isinstance(d.tag, str):
                    root.append(d)
        _corpus = root
    return _corpus

def q(xp):
    xp = xp if xp.startswith('/') else '/' + xp
    try:
        return corpus().getroottree().xpath(xp)
    except Exception:
        return None

log = collections.Counter()
EXISTING = set()

def canon(op):
    xp = (op.findtext('xpath') or '').strip().lstrip('/')
    v = op.find('value')
    return (cls(op), xp, re.sub(r'\s+', '', etree.tostring(v).decode()) if v is not None else '')

def prepass(root):
    EXISTING.clear()
    extra = [etree.parse(a[6:]).getroot() for a in sys.argv if a.startswith('--ctx=')]
    for op in [x for r in [root] + extra for x in r.iter()]:
        if isinstance(op.tag, str) and op.get('Class') and op.find('xpath') is not None \
                and cls(op) not in ('PatchOperationConditional', 'PatchOperationFindMod', 'PatchOperationSequence'):
            nm = names(op)
            if nm and not any(dnm.resolve(n)[0] for n in nm):
                EXISTING.add(canon(op))

notes = []

def cls(e): return (e.get('Class') or '').replace('Verse.', '')

def xpaths(e):
    return [x.text or '' for x in e.iter('xpath')]

def names(e):
    out = []
    for x in xpaths(e):
        out += DEFRE.findall(x)
    return list(dict.fromkeys(out))

def rewrite(e, mp):
    for x in e.iter('xpath'):
        t = x.text or ''
        for a, b in mp.items():
            t = t.replace('defName="%s"' % a, 'defName="%s"' % b)
        x.text = t

def children_ops(seq):
    ops = seq.find('operations')
    return ops, [c for c in ops if isinstance(c.tag, str)]

def remove(el):
    par = el.getparent()
    prev = el.getprevious()
    if prev is not None and isinstance(prev, etree._Comment):
        # only drop a comment that sits directly on this op (single comment line right above)
        if (prev.tail or '').count('\n') <= 1:
            prev.getparent().remove(prev) if prev.getparent() is not None else None
    # keep tail whitespace of removed element attached to previous
    tail = el.tail
    p = el.getprevious()
    par.remove(el)
    if p is not None:
        p.tail = (p.tail or '') if tail is None else tail
    else:
        par.text = tail

def leaf_state(op, ours_name):
    """After rewrite: BAKED / DIFFERENT / OPEN for a leaf Replace/Add."""
    c = cls(op)
    xp = (op.findtext('xpath') or '')
    val = op.find('value')
    if c in ('PatchOperationReplace', 'PatchOperationRemove', 'PatchOperationAttributeSet'):
        if not q(xp):
            return 'NOMATCH'
    if c == 'PatchOperationAdd':
        if not q(xp):
            return 'NOMATCH'
    if c == 'PatchOperationReplace' and val is not None and len(val):
        node = q(xp)
        if node:
            want = val[0]
            have = node[0]
            def eq(a, b):
                a, b = (a or '').strip(), (b or '').strip()
                if a == b: return True
                try: return abs(float(a) - float(b)) < 1e-9
                except ValueError: return False
            if len(have) == 0 and len(want) == 0 and eq(have.text, want.text):
                return 'BAKED'
            if len(want) and len(have) == len(want) and all(h.tag == w.tag and eq(h.text, w.text) for h, w in zip(have, want)):
                return 'BAKED'
            return 'DIFFERENT'
    return 'OPEN'

def process(op):
    """returns (newop_or_None, changed). Mutates in place when kept."""
    c = cls(op)
    nm = names(op)
    if c == 'PatchOperationSequence':
        ops, kids = children_ops(op)
        changed = False
        for k in kids:
            r, ch = process(k)
            if r is None:
                remove(k); changed = True
            else:
                changed |= ch
        if not [k for k in ops if isinstance(k.tag, str)]:
            return None, True
        return op, changed
    if c in ('PatchOperationConditional', 'PatchOperationFindMod'):
        # decide on the test xpath's defs for Conditional; recurse into branches
        mp = {}
        for n in nm:
            known, t = dnm.resolve(n)
            if known:
                mp[n] = t
        if mp and any(t is None for t in mp.values()) and all(t is None for t in mp.values()):
            log['dropped_donor_only'] += 1
            return None, True
        changed = False
        if mp and c == 'PatchOperationConditional':
            ox = op.find('xpath')
            if ox is not None and ox.text:
                t0 = ox.text
                for a, b in mp.items():
                    t0 = t0.replace('defName="%s"' % a, 'defName="%s"' % b)
                if t0 != ox.text:
                    ox.text = t0; changed = True; log['conditional_test_retargeted'] += 1
        for br in ('match', 'nomatch'):
            b = op.find(br)
            if b is None: continue
            r, ch = process(b)
            if r is None:
                remove(b); changed = True
            else:
                changed |= ch
        if op.find('match') is None and op.find('nomatch') is None:
            return None, True
        return op, changed
    # leaf
    mp = {}
    for n in nm:
        known, t = dnm.resolve(n)
        if known:
            mp[n] = t
    if not mp:
        return op, False
    if any(t is None for t in mp.values()):
        log['dropped_donor_only'] += 1
        return None, True
    rewrite(op, mp)
    st = leaf_state(op, None)
    if st == 'BAKED':
        log['dropped_baked'] += 1
        return None, True
    if st == 'NOMATCH':
        log['dropped_nomatch_in_ours'] += 1
        notes.append('NOMATCH in ours (dropped): ' + (op.findtext('xpath') or ''))
        return None, True
    if canon(op) in EXISTING:
        log['dropped_duplicate_of_existing'] += 1
        return None, True
    if st == 'DIFFERENT':
        log['retargeted_value_differs'] += 1
        return op, True
    log['retargeted'] += 1
    return op, True

def wrap_exists(el, tname):
    """wrap op `el` (an li or Operation) in a Conditional on its target def existing."""
    xp = [x.text for x in el.iter('xpath')][0]
    m = re.match(r'(/?Defs/\w+\[defName="%s"\])' % re.escape(tname), xp.strip())
    base = m.group(1) if m else None
    if not base:
        return el
    w = etree.Element(el.tag)
    w.set('Class', 'PatchOperationConditional')
    w.tail = el.tail
    x = etree.SubElement(w, 'xpath'); x.text = base
    mt = etree.SubElement(w, 'match')
    for k, v in el.attrib.items():
        mt.set(k, v)
    mt.text = el.text
    for ch in list(el):
        mt.append(ch)
    el.getparent().replace(el, w)
    return w

def run(path, write):
    parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False, strip_cdata=False)
    tree = etree.parse(path, parser)
    root = tree.getroot()
    before = dict(log)
    prepass(root)
    for fm in [e for e in root.iter() if isinstance(e.tag, str) and cls(e) == 'PatchOperationFindMod']:
        mods = [li.text.strip() for li in fm.findall('mods/li') if li.text]
        if not any(m in DONOR_MODS for m in mods):
            continue
        if len(mods) != 1:
            notes.append('MULTI-MOD gate left alone: %r' % mods); continue
        match = fm.find('match')
        if match is None:
            continue
        # per-def children if Sequence; else whole match
        sig = lambda e: tuple(names(e))
        if cls(match) == 'PatchOperationSequence':
            ops, kids = children_ops(match)
            for k in kids:
                orig = names(k)
                r, ch = process(k)
                if r is None:
                    remove(k); continue
                # the gate is going away: guard EVERY kept op on its own target def existing (also the ones
                # that merely sat under a mis-attributed donor gate, e.g. another mod's defs)
                new = [dnm.ours(n) for n in orig if dnm.resolve(n)[0]]
                prim = new[0] if new else (orig[0] if orig else None)
                if prim:
                    wrap_exists(k, prim)
            if not [k for k in match.find('operations') if isinstance(k.tag, str)]:
                remove(fm); continue
            # unwrap FindMod -> Sequence
            fm.set('Class', 'PatchOperationSequence')
            for t in fm.findall('mods'): fm.remove(t)
            ops_el = match.find('operations')
            fm.remove(match)
            fm.append(ops_el)
        else:
            orig = names(match)
            r, ch = process(match)
            if r is None:
                remove(fm); continue
            new = [dnm.ours(n) for n in orig if dnm.resolve(n)[0]]
            parent = fm.getparent()
            tail = fm.tail
            fm.remove(match)
            for t in fm.findall('mods'): fm.remove(t)
            match.tag = fm.tag
            match.tail = tail
            parent.replace(fm, match)
            if new:
                wrap_exists(match, new[0])
    if '--top' in sys.argv:
        for op in [e for e in root if isinstance(e.tag, str) and e.get('Class')]:
            if cls(op) == 'PatchOperationFindMod':
                continue
            orig = [n for n in names(op) if dnm.resolve(n)[0]]
            if not orig:
                continue
            r, ch = process(op)
            if r is None:
                remove(op); continue
            if cls(op) not in ('PatchOperationConditional', 'PatchOperationSequence'):
                wrap_exists(op, dnm.ours(orig[0]))
    out = {k: log[k] - before.get(k, 0) for k in log}
    print(os.path.relpath(path, '/home/mandrake/rm/foundry'), {k: v for k, v in out.items() if v})
    if write:
        orig = open(path, encoding='utf-8').read()
        head = orig[:orig.index('<' + root.tag)]
        body = etree.tostring(root, encoding='unicode')
        trail = orig[len(orig.rstrip()):] or '\n'
        open(path, 'w', encoding='utf-8', newline='').write(head + body + trail)

def migrate_if_donor(path):
    """For generators: call at the END of a generator, on each file it just wrote. A file with no donor-NAME FindMod gate
    is left byte-for-byte alone; one with a gate is migrated in place, so a re-run no longer re-emits donor names."""
    text = open(path, encoding='utf-8').read()
    if any('<li>%s</li>' % m in text for m in DONOR_MODS):
        run(path, True)
        for n in notes: print('NOTE', n)
        return True
    return False

if __name__ == '__main__':
    write = '--write' in sys.argv
    for f in [a for a in sys.argv[1:] if not a.startswith('--')]:
        run(f, write)
    for n in notes: print('NOTE', n)
