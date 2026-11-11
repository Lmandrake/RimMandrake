"""Focused current source-model regression: separates lineage admission from supported-stage occupancy."""
import itertools
import unittest
import measure_reefback_calf as M


class Policy(unittest.TestCase):
    def test_juvenile_spacing_changes_only_occupied_gate(self):
        # Read old instrument's exact signature/predicate from preserved evidence separately; this oracle is the written policy.
        for adult,spacing in itertools.product(range(4),repeat=2):
            for flags in itertools.product((False,True),repeat=8):
                optout,sea,sea_map,has_list,on_list,home,season,occupied=flags
                gates=not optout and adult>=2 and sea==sea_map and season and (on_list if has_list else home)
                got=M.event_eligible(adult,spacing,*flags)
                self.assertEqual(got,gates and not (occupied and spacing==3))
                before=gates and not (occupied and adult==3)
                if not occupied:self.assertEqual(got,before)
                if spacing<=adult and got!=before:
                    self.assertTrue(got and not before and adult==3 and spacing<3)

    def test_real_reefback_relationship_and_custom_calf_allowance(self):
        for ladder,adult,spacing in [([4,8,20],3,2),([4,8,16],3,3),([4,18,30],3,1),([4,8,40],2,2)]:
            self.assertEqual(M.tier(32,ladder),adult)
            self.assertEqual(M.spacing_tier(32,[.2,.5],ladder,adult),spacing)
            self.assertTrue(M.event_eligible(adult,spacing,False,False,False,False,False,True,True,False))
            self.assertEqual(M.event_eligible(adult,spacing,False,False,False,False,False,True,True,True),spacing!=3)
        self.assertEqual(M.spacing_tier(32,[.2,.5,1],[4,8,20],3),3)
        self.assertEqual(M.spacing_tier(3,[4],[4,8,20],2),2)

    def test_malformed_stages_cannot_relax_spacing(self):
        for factors in [None,[],[None],[.2,.5,None],[.2,.5,0],[.2,.5,-1],[.2,.5,float('nan')],
                        [.2,.5,float('inf')],[.2,.5,-float('inf')]]:
            self.assertEqual(M.spacing_tier(32,factors,[4,8,20],3),3)


if __name__=='__main__':
    unittest.main()
