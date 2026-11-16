#!/usr/bin/env python3
"""Park pages preserve advisory findings and route defective criteria without asking the owner."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import designer_stage as DS


class ParkCoverage(unittest.TestCase):
    def page(self, verdict, sent=True, coverage="not signed"):
        with tempfile.TemporaryDirectory() as d:
            rec = {"root": {"text": "Home and ordered trips."}, "inventory": [{"id": "wind", "impl": "present"}],
                   "asks": ([{"id": "root_validation", "status": "sent", "text": "Validate these eight observations?",
                              "quick_look": {"offer": True, "scene": "Existing wind and an ordered expedition."}}]
                            if sent else [])}
            for name, data in (("record.json", rec), ("coverage_verdict.json", verdict)):
                with open(os.path.join(d, name), "w") as f:
                    json.dump(data, f)
            st = {"mod": "Scrub", "item": "SCRUB_ITEM", "stage": 2, "results": []}
            with patch.object(DS.CT, "coverage_summary", return_value=coverage):
                return DS.park_summary(d, st, "certification", "Waiting for root validation")

    def test_advisory_does_not_become_an_owner_refusal(self):
        gaps = [{"gid": "g%d" % i, "what": "finding %d" % i, "return_to": 3,
                 "criterion_verdict": "sound"} for i in range(1, 12)]
        gaps.append({"gid": "g12", "what": "flagship authority ambiguity", "return_to": 2,
                     "criterion_verdict": "flawed"})
        page = self.page({"verdict": "not_covered", "advisory": "UNTESTED", "gaps": gaps, "unchecked": []})
        self.assertIn("advisory", page.lower())
        self.assertIn("not a binding refusal", page.lower())
        self.assertNotIn("Gap 12 needs your answer", page)
        self.assertIn("neutral criteria fixer", page.lower())
        self.assertIn("11 advisory", page.lower())
        self.assertIn("Existing wind and an ordered expedition.", page)
        self.assertIn("Ask root_validation", page)
        self.assertNotIn("waive a gap", page)
        for i in range(1, 12):
            self.assertIn("finding %d" % i, page)
        self.assertIn("flagship authority ambiguity", page)

    def test_contract_advisory_survives_without_top_level_marker(self):
        page = self.page({"verdict": "not_covered", "contract": {"advisory": True, "calibration": "UNTESTED"},
                          "gaps": [{"what": "ordinary stage2 candidate", "return_to": 2,
                                    "criterion_verdict": "sound"}]})
        self.assertIn("not a binding refusal", page.lower())
        self.assertNotIn("Gap 1 needs your answer", page)

    def test_calibrated_sound_owner_gap_still_needs_owner(self):
        page = self.page({"verdict": "not_covered", "contract": {"calibration": "CALIBRATED"}, "gaps": [
            {"what": "scope genuinely open", "return_to": 2, "criterion_verdict": "sound"},
            {"what": "scene correction", "return_to": 3, "criterion_verdict": "sound"},
            {"what": "impossible criterion", "return_to": 2, "criterion_verdict": "unattainable"}]}, sent=False)
        self.assertIn("Gap 1 needs your answer", page)
        self.assertNotIn("Gap 3 needs your answer", page)
        self.assertIn("neutral criteria fixer", page.lower())
        self.assertIn("can fix 1 gap", page)

    def test_owner_certificate_is_not_overridden(self):
        page = self.page({"verdict": "not_covered", "advisory": True, "gaps": [
            {"what": "old gap", "return_to": 2, "criterion_verdict": "sound"}]},
            coverage="passed on the owner's word (OWNER:123)")
        self.assertIn("passed on the owner's word", page)
        self.assertNotIn("old gap", page)
        self.assertNotIn("Gap 1 needs your answer", page)


if __name__ == "__main__":
    unittest.main()
