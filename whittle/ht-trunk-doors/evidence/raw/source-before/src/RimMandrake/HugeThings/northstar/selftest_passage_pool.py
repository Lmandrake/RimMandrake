#!/usr/bin/env python3
"""Bounded planted receipt defects: truncation, vacuity, sea leakage, wrong arrival."""
import unittest
import passage_pool_live as P


def response(s):
    return {'success': True, 'result': s}


POOL = 'canFire=True active=True t3OnMap=False biome=RM_Stillsand seaMap=False hints=roster eligible=2 [Adult:T2:land,Calf:T3:land]'
ARRIVED = 'pending=False kind=none arrivalIn=-1 arrived=Calf123 kind=Calf tier=T3 spawned=True homedHere=True seaMatch=True lord=LordJob_ExitMapNear pos=0,37'


class Receipts(unittest.TestCase):
    def test_positive_adult_and_calf_not_filtered_by_name(self):
        got = P.land_pool(response(POOL))
        self.assertEqual([k['kind'] for k in got['kinds']], ['Adult', 'Calf'])
        self.assertEqual(P.arrival(response(ARRIVED), got, ['Adult','Calf'])['kind'], 'Calf')

    def test_complete_pool_mutants_refused(self):
        cases = [POOL[:-1], POOL+' trailing text', POOL.replace('eligible=2','eligible=3'),
                 POOL.replace('Calf:T3:land', 'Calf:T3:sea'),
                 POOL.replace('Adult:T2:land,Calf:T3:land', '').replace('eligible=2','eligible=0'),
                 POOL.replace('RM_Stillsand','TemperateForest'), POOL.replace('seaMap=False','seaMap=True'),
                 POOL.replace('Calf:T3:land','Adult:T3:land'), POOL.replace(':T3:land',':T3'),
                 POOL.replace('Calf:T3:land', '...'), POOL.replace('T2:land','T1:land')]
        for text in cases:
            with self.subTest(text=text), self.assertRaises((P.ReceiptRefusal, P.ContentFailure)):
                P.land_pool(response(text))

    def test_envelope_success_is_not_payload_success(self):
        for r in ({'Success':True,'result':POOL}, {'success':False,'result':POOL},
                  {'success':1,'result':POOL}, {'success':True,'result':None}):
            with self.subTest(response=r), self.assertRaises(P.ReceiptRefusal):
                P.land_pool(r)

    def test_arrival_mutants_refused(self):
        eligible = P.land_pool(response(POOL))
        for old,new in [('spawned=True','spawned=False'), ('seaMatch=True','seaMatch=False'),
                        ('homedHere=True','homedHere=False'), ('kind=Calf','kind=Foreign'),
                        ('pending=False','pending=True'), ('arrived=Calf123 ','')]:
            with self.subTest(old=old), self.assertRaises((P.ReceiptRefusal, P.ContentFailure)):
                P.arrival(response(ARRIVED.replace(old,new)), eligible, ['Adult','Calf'])
        with self.assertRaises(P.ContentFailure):
            P.arrival(response(ARRIVED), eligible, ['Adult'])

    def test_audit_does_not_certify_live_provenance(self):
        got = P.audit(dict(pool_response=response(POOL), arrival_response=response(ARRIVED), own_roster=['Calf']))
        self.assertTrue(got['ok'])
        self.assertIs(got['certifiable'],False)
        self.assertFalse(P.audit({})['ok'])

    def test_measured_mod_failure_never_softens_to_unmeasured(self):
        got = P.audit(dict(pool_response=response(POOL.replace('Calf:T3:land','Calf:T3:sea'))))
        self.assertEqual(got['rows'][0]['status'], 'FAIL')
        got = P.audit(dict(pool_response=response(POOL), arrival_response=response(ARRIVED.replace('seaMatch=True','seaMatch=False')), own_roster=['Calf']))
        self.assertEqual(got['rows'][1]['status'], 'FAIL')

    def test_arrival_exact_keys_and_whole_string(self):
        for text in (ARRIVED.replace('seaMatch=True','expectedSeaMatch=True'),
                     ARRIVED+' seaMatch=False', ARRIVED.replace('seaMatch=True','seaMatch=True seaMatch=False'),
                     ARRIVED.replace('kind=Calf','kind=none kind=Calf')):
            with self.subTest(text=text), self.assertRaises(P.ReceiptRefusal):
                P.arrival(response(text), P.land_pool(response(POOL)), ['Calf'])


if __name__ == '__main__':
    print('NON-EVIDENCE fixtures: parser controls only, never live A2/A3')
    unittest.main()
