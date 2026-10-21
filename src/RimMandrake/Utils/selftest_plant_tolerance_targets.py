#!/usr/bin/env python3
"""selftest: every row of PlantTolerances_*.xml targets a def that EXISTS.

Why (pre-flight 2026-10-20): PlantTolerances_Ashkarr.xml carried 18 RUT_ rows for plants that became RM_ twins on
2026-10-16, plus 48 rows for Alpha Biomes AB_ donor defs that were retired the same day. A patch row on a missing def
logs nothing in game, so the plants simply got no refitted band.

1. Every RM_/RUT_/RSW_ row must be defined under src/ (static, always runs).
2. No row may name a retired-donor prefix (AB_) at all.
3. If a live DefDump capture is readable, EVERY row must be in its ThingDef list; otherwise that half is reported
   UNMEASURED (not passed).
4. The checker can SEE: a fixture row for a missing def and one for an AB_ def must each be flagged.
Offline, no game."""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PATCHES = os.path.join(ROOT, 'src', 'RimUtinni', 'UtinniPatches', 'Patches')
ROW = re.compile(r'<Operation Class="PatchOperationConditional">\s*<xpath>/Defs/ThingDef\[defName="([^"]+)"\]/plant</xpath>')
OURS = ('RM_', 'RUT_', 'RSW_')
RETIRED = ('AB_',)


def src_defnames():
    out = set()
    pat = re.compile(r'<defName>((?:RM|RUT|RSW)_[^<]+)</defName>')
    for f in glob.glob(os.path.join(ROOT, 'src', '**', '*.xml'), recursive=True):
        with open(f, encoding='utf-8', errors='ignore') as fh:
            out.update(pat.findall(fh.read()))
    return out


def live_defnames():
    try:
        sys.path.insert(0, HERE)
        from game_paths import DEF_DUMP
        with open(os.path.join(str(DEF_DUMP), 'defs', 'ThingDef.json'), encoding='utf-8') as fh:
            return {d['defName'] for d in json.load(fh)['defs']}
    except Exception:                                                            # noqa: BLE001
        return None


def problems(rows, src, live):
    """rows: iterable of defNames. Returns (bad_src, retired, bad_live or None)."""
    rows = sorted(set(rows))
    bad_src = [r for r in rows if r.startswith(OURS) and r not in src]
    retired = [r for r in rows if r.startswith(RETIRED)]
    bad_live = None if live is None else [r for r in rows if r not in live]
    return bad_src, retired, bad_live


def main():
    results = []
    src, live = src_defnames(), live_defnames()
    files = sorted(glob.glob(os.path.join(PATCHES, 'PlantTolerances_*.xml')))
    results.append(('found plant tolerance patches', len(files) >= 1, str(len(files))))
    for f in files:
        with open(f, encoding='utf-8') as fh:
            rows = ROW.findall(fh.read())
        results.append((os.path.basename(f) + ' has rows', len(rows) > 0, str(len(rows))))
        bs, rt, bl = problems(rows, src, live)
        results.append((os.path.basename(f) + ': our-prefix rows defined in src', not bs, ' '.join(bs[:8])))
        results.append((os.path.basename(f) + ': no retired-donor rows', not rt, ' '.join(rt[:8])))
        if bl is None:
            print('UNMEASURED live-dump half for %s (no readable capture)' % os.path.basename(f))
        else:
            results.append((os.path.basename(f) + ': every row exists in the live dump', not bl, ' '.join(bl[:8])))
    # the checker can see
    bs, rt, bl = problems(['RUT_Wrinklecap', 'AB_Aaklac', 'RM_Real'], {'RM_Real'}, {'RM_Real'})
    results.append(('fixture: missing RUT_ flagged', bs == ['RUT_Wrinklecap'], str(bs)))
    results.append(('fixture: AB_ flagged', rt == ['AB_Aaklac'], str(rt)))
    results.append(('fixture: absent from live flagged', bl == ['AB_Aaklac', 'RUT_Wrinklecap'], str(bl)))
    # retarget_text: a donor chunk that maps onto a def already keyed by OUR name is the duplicate, wherever it sits
    sys.path.insert(0, os.path.join(ROOT, 'design', 'Jawa', 'mods'))
    import donor_name_map as dnm
    ren = dnm.renamed_ours()
    old = next((k for k in sorted(ren) if k.startswith('RUT_')), None)
    if old is None:
        print('UNMEASURED retarget dedupe fixture (no RUT_ -> RM_ rename on disk)')
    else:
        mk = lambda n: '<!-- x (%s) -->\n<Operation Class="PatchOperationConditional">\n<xpath>/Defs/ThingDef[defName="%s"]/plant</xpath>' % (n, n)
        txt = '\n\n'.join(['HEAD', mk(old), mk(ren[old])])
        new, rt, dr, dd = dnm.retarget_text(txt)
        results.append(('fixture: donor chunk duplicating a native chunk dropped', dd == 1 and new.count('defName="%s"' % ren[old]) == 1,
                        '%d dup, %d kept' % (dd, new.count('defName="%s"' % ren[old]))))
    ok = sum(1 for _, c, _ in results if c)
    for n, c, d in results:
        if not c:
            print('FAIL', n, d)
    print('%d/%d passed' % (ok, len(results)))
    return 0 if ok == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
