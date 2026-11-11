"""Offline production RAISE_SPARES_UNDERPASS contract, never a live bridge claim.

Optional DRAWBRIDGE_UNDERPASS_MODULE imports an isolated old source for regression replay.
Optional DRAWBRIDGE_UNDERPASS_ROWS saves raw rows, including their expected/observed verdicts.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

UTILS = Path(__file__).resolve().parent
NORTHSTAR = UTILS.parent / 'FlowWorks' / 'northstar'
sys.path.insert(0, str(UTILS))
sys.path.insert(0, str(NORTHSTAR))
SOURCE = Path(os.environ.get('DRAWBRIDGE_UNDERPASS_MODULE', NORTHSTAR / 'drawbridge_proof.py')).resolve()
spec = importlib.util.spec_from_file_location('underpass_production', SOURCE)
DP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DP)
ROWS = []
ABSENT = object()


def injury(**changes):
    # Actual jawa/list_pawns producer: JawaBenchTerrainTools.cs, includeHealth branch.
    return dict({'def': 'Cut', 'label': 'cut', 'severity': 2.5, 'part': 'Arm',
                 'partLabel': 'left arm', 'lastInjury': None}, **changes)


def health(injuries):
    return {'hediffs': injuries, 'capacities': {'Moving': 1.0}, 'capacityErrors': [],
            'painTotal': 0.1, 'bleedRate': 0.0}


def pawn(reading):
    p = {'id': 'under', 'x': 2, 'z': 32}
    if reading is not ABSENT:
        p['health'] = copy.deepcopy(reading)
    return p


def run_row(before, after, *, moved=False, bad_cell=False, alias=False):
    """Minimal ctx: staging succeeds, rider tips, counters advance; health is the variable.

    Uses the production scene and its real scope/judge. No bridge object or live imports.
    """
    u0, u1 = pawn(before), pawn(after)
    if moved:
        u1['x'] = 3
    if bad_cell:
        u0.pop('x')
        u1.pop('x')
    state = {'after': False}
    emitted = []

    def proof(method, arg, **kw):
        if method == 'ProofPutUnder':
            return {'under': 'True'}, 'PUT under=True'
        if method == 'ProofBand':
            return {'view': 'floor'}, 'BAND view=floor'
        if method == 'ProofDevSet':
            state['after'] = True
            if alias:
                u0.clear()
                u0.update(copy.deepcopy(u1))
            return {'target': 'raised'}, 'DEVSET target=raised'
        raise AssertionError('unexpected proof: ' + method)

    def pawns():
        return {'under': u0 if alias or not state['after'] else u1,
                'rider': {'id': 'rider', 'x': 0 if state['after'] else 3, 'z': 32}}

    def row(rid, status, detail, cls='MOD'):
        status, cls, detail = DP.V.PRE.judge(status, cls, detail)
        emitted.append({'id': rid, 'status': status, 'class': cls, 'detail': detail})

    ids = iter(['under', 'rider'])
    ctx = {'P': lambda x, z: (x, z), 'xz': lambda p: '%d,%d' % p, 'row': row,
           'dproof': proof, 'sproof': proof, 'ticks': lambda n: None,
           'spawn': lambda *a, **kw: next(ids), 'dig': lambda *a: None,
           'build': lambda *a: None, 'power': lambda *a: None, 'pawns': pawns,
           'counters': lambda: {'TippedCount': int(state['after'])},
           'delta': lambda a, b, k: b[k] - a[k],
           'at': lambda p: (p.get('x'), p.get('z')) if p else (None, None)}
    with DP.V.scope('underpass focused offline selftest'):
        DP.raise_spares_underpass(ctx)
    assert len(emitted) == 1, emitted
    assert emitted[0]['id'] == 'RAISE_SPARES_UNDERPASS'
    return emitted[0]


class UnderpassContract(unittest.TestCase):
    def check_case(self, name, before, after, expected, **kw):
        result = run_row(before, after, **kw)
        ROWS.append({'case': name, 'expected': list(expected), 'row': result})
        self.assertEqual((result['status'], result['class']), expected, name)
        detail = result['detail']
        for phase, reading in [('Before', before), ('After', after)]:
            self.assertIn('health' + phase, detail, name)
            self.assertEqual(detail['health' + phase + 'Present'], reading is not ABSENT, name)
            self.assertEqual(detail['health' + phase], None if reading is ABSENT else reading, name)
        if expected == ('UNMEASURED', 'HARNESS'):
            self.assertTrue(detail['unmeasuredBecause'], name)
        return result

    def test_production_row(self):
        valid = health([injury()])
        cases = [
            ('unchanged existing injury', valid, copy.deepcopy(valid), ('PASS', 'MOD'), {}),
            ('real empty lists', health([]), health([]), ('PASS', 'MOD'), {}),
            ('worsened equal count', valid, health([injury(severity=3.5)]), ('FAIL', 'MOD'), {}),
            ('tiny severity drift', valid, health([injury(severity=2.500001)]), ('FAIL', 'MOD'), {}),
            ('replaced equal count', valid, health([injury(**{'def': 'Burn', 'label': 'burn'})]), ('FAIL', 'MOD'), {}),
            ('part changed equal count', valid, health([injury(part='Leg', partLabel='left leg')]), ('FAIL', 'MOD'), {}),
            ('side label changed', valid, health([injury(partLabel='right arm')]), ('FAIL', 'MOD'), {}),
            ('last injury changed', health([injury(**{'def': 'MissingBodyPart', 'lastInjury': 'Cut'})]),
             health([injury(**{'def': 'MissingBodyPart', 'lastInjury': 'Burn'})]), ('FAIL', 'MOD'), {}),
            ('order changes', health([injury(), injury(severity=1)]), health([injury(severity=1), injury()]), ('PASS', 'MOD'), {}),
            ('duplicates lost', health([injury(), injury()]), valid, ('FAIL', 'MOD'), {}),
            ('duplicate multiplicity replaced', health([injury(), injury(), injury(severity=1)]),
             health([injury(), injury(severity=1), injury(severity=1)]), ('FAIL', 'MOD'), {}),
            ('whole body null parts', health([injury(part=None, partLabel=None)]),
             health([injury(part=None, partLabel=None)]), ('PASS', 'MOD'), {}),
            ('numeric severity equivalent', health([injury(severity=1)]), health([injury(severity=1.0)]), ('PASS', 'MOD'), {}),
            ('large distinct severity', health([injury(severity=2**54)]),
             health([injury(severity=2**54 + 1)]), ('FAIL', 'MOD'), {}),
            ('cell moved', valid, valid, ('FAIL', 'MOD'), {'moved': True}),
            ('unread cells', valid, valid, ('UNMEASURED', 'HARNESS'), {'bad_cell': True}),
            ('shared mutable pawn payload', valid, health([injury(severity=8)]), ('FAIL', 'MOD'), {'alias': True}),
            # Other health metrics are raw evidence, not the injury equality contract.
            ('capacity change only', valid, dict(valid, capacities={'Moving': 0.9}), ('PASS', 'MOD'), {}),
            ('injury fields only health block', {'hediffs': [injury()]}, {'hediffs': [injury()]}, ('PASS', 'MOD'), {}),
        ]
        bad = [('health absent', ABSENT), ('health null', None), ('health list', []),
               ('health string', 'bad'), ('hediffs absent', {}), ('hediffs null', {'hediffs': None}),
               ('hediffs false', {'hediffs': False}), ('hediffs zero', {'hediffs': 0}),
               ('hediffs string', {'hediffs': 'abc'}), ('hediffs dict', {'hediffs': {}}),
               ('hediff null', health([None])), ('hediff string', health(['Cut'])),
               ('incomplete record', health([{'def': 'Cut'}]))]
        for key in injury():
            record = injury()
            record.pop(key)
            bad.append(('record missing ' + key, health([record])))
        for key, value in [('severity', True), ('severity', '2.5'), ('severity', None),
                           ('severity', float('nan')), ('severity', float('inf')), ('severity', -1),
                           ('severity', 10**400),
                           ('part', 7), ('partLabel', []), ('lastInjury', False), ('def', ''), ('label', 3),
                           ('part', None)]:
            bad.append(('malformed %s %r' % (key, value), health([injury(**{key: value})])))
        for name, reading in bad:
            for side in ('before', 'after', 'both'):
                cases.append((name + ' ' + side, reading if side != 'after' else valid,
                              reading if side != 'before' else valid, ('UNMEASURED', 'HARNESS'), {}))
        for name, before, after, want, kw in cases:
            with self.subTest(case=name):
                self.check_case(name, before, after, want, **kw)

    def test_shared_health_helper_unchanged(self):
        self.assertIsNone(DP._health({}))
        self.assertEqual(DP._health({'health': {}}), [])
        self.assertEqual(DP._health({'health': {'hediffs': None}}), [])
        self.assertEqual(DP._health({'health': {'hediffs': 'legacy'}}), 'legacy')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(UnderpassContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {'mode': 'offline instrument selftest; no live game', 'source': str(SOURCE),
               'rows': ROWS, 'failures': len(result.failures), 'errors': len(result.errors)}
    if os.environ.get('DRAWBRIDGE_UNDERPASS_ROWS'):
        Path(os.environ['DRAWBRIDGE_UNDERPASS_ROWS']).write_text(json.dumps(receipt, indent=2) + '\n')
    print('%d production underpass scenarios; failures=%d errors=%d' % (len(ROWS), len(result.failures), len(result.errors)))
    sys.exit(0 if result.wasSuccessful() else 1)
