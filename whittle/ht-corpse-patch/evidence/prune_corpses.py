"""Corpse-only cleanup of a frozen shipped XML, never a capture regeneration.

Usage: python3 .../prune_corpses.py --before SNAPSHOT --output FILE [--accept-corpse-only-shrink]
The explicit shrink override is available ONLY after byte/canonical/order proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src/RimMandrake/Utils'))
import biome_wildbiomes_evictions as E

BLOCK = re.compile(rb'\n  <!-- [^\n]+ -->\n  <Operation Class="PatchOperationConditional">.*?</Operation>\n', re.S)
OP = re.compile(rb'<Operation\b.*?</Operation>', re.S)


def target(op):
    x = op.findtext('xpath', '')
    pair = E.PAIR_RE.fullmatch(x)
    assert pair, x
    assert op.attrib == {'Class': 'PatchOperationConditional'}
    assert op.find('match').attrib == {'Class': 'PatchOperationRemove'}
    assert op.findtext('match/xpath') == x
    return pair.groups()


def compare(before, after):
    bops = ET.fromstring(before).findall('Operation')
    aops = ET.fromstring(after).findall('Operation')
    retained = [o for o in bops if not target(o)[0].startswith('Corpse_')]
    assert len(retained) == len(aops) > 0
    assert [target(o) for o in retained] == [target(o) for o in aops]
    assert not any(target(o)[0].startswith('Corpse_') for o in aops)
    br = [m.group() for m in OP.finditer(before)
          if not target(ET.fromstring(m.group()))[0].startswith('Corpse_')]
    ar = [m.group() for m in OP.finditer(after)]
    canonical = lambda raw: ET.canonicalize(raw.decode('utf-8'))
    assert br == ar, 'non-corpse operation bytes/order changed'
    assert list(map(canonical, br)) == list(map(canonical, ar))
    return {'before_operations': len(bops), 'after_operations': len(aops),
            'removed_corpse_operations': len(bops)-len(aops),
            'after_corpse_operations': 0, 'after_biomes': sorted({target(o)[1] for o in aops}),
            'noncorpse_bytes_and_order_identical': True, 'noncorpse_canonical_and_order_identical': True,
            'noncorpse_operation_sha256_in_order': [hashlib.sha256(o).hexdigest() for o in ar]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--before', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--accept-corpse-only-shrink', action='store_true')
    a = ap.parse_args()
    before = a.before.read_bytes()
    parsed = ET.fromstring(before).findall('Operation')
    blocks = list(BLOCK.finditer(before))
    assert len(blocks) == len(parsed) == len(OP.findall(before))
    assert [target(ET.fromstring(OP.search(m.group()).group())) for m in blocks] == [target(o) for o in parsed]
    after = BLOCK.sub(lambda m: b'' if target(ET.fromstring(OP.search(m.group()).group()))[0].startswith('Corpse_') else m.group(), before)
    proof = compare(before, after)  # Must pass BEFORE any shrink acceptance or write.
    old = ('  %d operation(s) over ' % len(parsed)).encode()
    new = ('  %d operation(s) over ' % proof['after_operations']).encode()
    assert after.count(old) == 1
    after = after.replace(old, new)
    note = ('  Offline hygiene 2026-11-11: pruned %d implied Corpse_ operations only.\n'
            '  The capture/scan provenance above is historical; no fresh capture or mod scan.\n'
            % proof['removed_corpse_operations']).encode()
    assert after.count(b'-->\n<Patch>') == 1
    after = after.replace(b'-->\n<Patch>', note + b'-->\n<Patch>')
    proof.update(compare(before, after))
    proof.update(before_sha256=hashlib.sha256(before).hexdigest(), after_sha256=hashlib.sha256(after).hexdigest(),
                 default_shrink_guard=E.shrink_guard(proof['after_operations'], len(parsed)),
                 corpse_only_override=a.accept_corpse_only_shrink)
    print(json.dumps(proof, indent=2), flush=True)
    if proof['default_shrink_guard'] and not a.accept_corpse_only_shrink:
        print(proof['default_shrink_guard'], file=sys.stderr)
        return 3
    assert not E.shrink_guard(proof['after_operations'], len(parsed), a.accept_corpse_only_shrink)
    a.output.write_bytes(after)
    print('wrote corpse-only cleanup:', a.output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
