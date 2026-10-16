#!/usr/bin/env python3
"""Donor defName -> the def of OURS that replaced it (or null: donor-only, dropped).

Why this exists (Phase 0 cleanup, owner order 2026-10-15): the generators that emit tolerance /
flammability / yield patches read rosters and the def dump, which still speak the DONOR's names.
Emitting a donor name is a patch that silently matches nothing once the donor is retired
(a PatchOperation that matches nothing logs nothing). The generators therefore translate each
name through `resolve()` at EMIT time; the bands themselves are still computed from the donor's
shipped values, which our ports copied.

    python3 design/Jawa/mods/donor_name_map.py build   # rewrite donor_name_map.json (needs donor folders)
    python3 design/Jawa/mods/donor_name_map.py check   # every target exists as a def of ours
    python3 design/Jawa/mods/donor_name_map.py retarget FILE... [--write]
        # the SAME translation applied to an already-generated tolerance file, for when its generator cannot
        # run (stale def dump / stale rosters make plant_tolerances.py's verify() refuse to write).
        # Only chunks that name a donor defName change; donor-only chunks are dropped.

Sources, in this order: aa_port.PORTS (Alpha Animals), the Wyyyschokk ruling, then `RSW_<name>`
(donor_pack_port.py's naming for mlie.starwarsanimalcollection; DECLINED species excluded because
`RSW_Mynock` is a different, owner-authored species). A donor-defined name with no twin maps to null.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MAP_PATH = os.path.join(HERE, 'donor_name_map.json')
UTILS = os.path.join(ROOT, 'src', 'RimMandrake', 'Utils')

# owner 2026-10-03: RM_Ollathrix IS the wyyyschokk (RSW_Wyyyschokk retired, WYYYSCHOKK_IDENTITY_COLLISION_1)
OVERRIDES = {'Wyyyschokk': 'RM_Ollathrix'}

# Alpha Animals donors ported BEFORE aa_port.py (each header says "port of AA_x") or matched to an existing twin by
# Transient/phase0_p2_classification.md, or ported in the slime pass (RM_Oomb.xml / RM_Wuum.xml headers).
AA_EXPLICIT = {
    'AA_NightMule': 'RM_Aveluthia', 'AA_CrepuscularBeetle': 'RM_Moravatha', 'AA_Darkbeast': 'RM_Nevarithia',
    'AA_NightRam': 'RM_Olumetha', 'AA_DarkVandal': 'RM_Ossumatha', 'AA_DuskProwler': 'RM_Ysvaltha',
    'AA_Eyeling': 'RSW_Ikee', 'AA_Needlepost': 'RM_Skorra', 'AA_GreenGoo': 'RM_Wuum',
    'AA_AcanthamoebaGiganteaSmall': 'RM_LesserOomb', 'AA_AcanthamoebaGiganteaLarge': 'RM_Oomb',
    'AA_AcanthamoebaGiganteaHuge': 'RM_GreaterOomb',
}

_cache = None


def _load():
    global _cache
    if _cache is None:
        with open(MAP_PATH, encoding='utf-8') as fh:
            _cache = json.load(fh)['map']
    return _cache


def resolve(name):
    """(known, target): known False = not a donor name, leave it alone; target None = donor-only, drop."""
    m = _load()
    if name in m:
        return True, m[name]
    return False, name


def ours(name):
    """The name to emit, or None to emit nothing. Names that are not donor names pass through."""
    known, t = resolve(name)
    return t if known else name


def reverse():
    """our name -> the donor name it replaced (first by sort order), for looking ours up in a donor-era dump."""
    out = {}
    for n, t in sorted(_load().items()):
        if t:
            out.setdefault(t, n)
    return out


def same_suffix(n, texts):
    """AA_X -> RM_X / RSW_X / RUT_X when that def exists and its own file names AA_X (a port header).
    `texts` is {defName: [file text, ...]}."""
    if not n.startswith('AA_'):
        return None
    for pre in ('RM_', 'RSW_', 'RUT_'):
        t = pre + n[3:]
        if any(n in txt for txt in texts.get(t, ())):
            return t
    return None


def build():
    sys.path.insert(0, UTILS)
    import donor_pack_port as P
    import aa_port
    on = P.our_names()
    van = P.names_in(os.path.join(P.VANILLA_DATA, '*', 'Defs', '**', '*.xml'))
    import re
    texts = {}                     # defName -> texts of the files defining it (a same-suffix twin must name its donor)
    for f in P.glob.glob(os.path.join(P.SRC, '**', 'Defs', '**', '*.xml'), recursive=True):
        try:
            txt = open(f, encoding='utf-8').read()
        except OSError:
            continue
        for dn in re.findall(r'<defName>((?:RM|RSW|RUT)_[A-Za-z0-9_]+)</defName>', txt):
            texts.setdefault(dn, []).append(txt)
    out = {}
    for donor, rename in ((P.DONOR, lambda n: 'RSW_' + n), (aa_port.DONOR, None)):
        for n in sorted(P.donor_names(donor)):
            if n in on or n in van:
                continue                      # the name is also ours/vanilla: not a donor-only name
            if rename is None:
                t = (aa_port.PORTS.get(n, (None,))[0] or aa_port.REPOINT.get(n, (None,))[0]
                     or AA_EXPLICIT.get(n) or same_suffix(n, texts))
            else:
                t = None if n in P.DECLINED else rename(n)
            out[n] = t if t in on else None
    for n, t in OVERRIDES.items():
        out[n] = t if t in on else None
    return out


def retarget_text(txt):
    """Rewrite a generated patch (header, then blank-line separated `<!-- comment -->` + `<Operation>` chunks).
    Returns (new_text, retargeted, dropped, deduped)."""
    import re
    chunks = txt.split('\n\n')
    out, seen_new, rt, dr, dd = [], set(), 0, 0, 0
    for ch in chunks:
        if '<Operation' not in ch:
            out.append(ch)
            continue
        names = re.findall(r'<xpath>/Defs/ThingDef\[defName="([^"]+)"\]', ch)
        if not names:
            out.append(ch)
            continue
        primary = names[0]
        known, t = resolve(primary)
        if not known:
            out.append(ch)
            continue
        if t is None:
            dr += 1
            continue
        if t in seen_new:
            dd += 1
            continue
        seen_new.add(t)
        ch = ch.replace('defName="%s"' % primary, 'defName="%s"' % t).replace('(%s)' % primary, '(%s)' % t)
        rt += 1
        out.append(ch)
    return '\n\n'.join(out), rt, dr, dd


def main(argv):
    cmd = argv[1] if len(argv) > 1 else 'check'
    if cmd == 'build':
        m = build()
        with open(MAP_PATH, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'_note': 'GENERATED by donor_name_map.py build - do not hand-edit. null = donor-only, no twin.',
                       'map': m}, fh, indent=0, sort_keys=True)
            fh.write('\n')
        print(f'wrote {MAP_PATH}: {len(m)} names, {sum(1 for v in m.values() if v)} with a twin')
        return 0
    if cmd == 'retarget':
        write = '--write' in argv
        for f in [a for a in argv[2:] if not a.startswith('--')]:
            with open(f, encoding='utf-8') as fh:
                txt = fh.read()
            new, rt, dr, dd = retarget_text(txt)
            print(f'{f}: {rt} chunk(s) retargeted, {dr} donor-only dropped, {dd} duplicate(s) dropped')
            if write:
                with open(f, 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write(new)
        return 0
    sys.path.insert(0, UTILS)
    import donor_pack_port as P
    on = P.our_names()
    bad = [(n, t) for n, t in _load().items() if t and t not in on]
    print(f'{len(_load())} names; targets missing from our defs: {bad}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
