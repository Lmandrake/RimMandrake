#!/usr/bin/env python3
"""Offline acceptance for the Abyss and TheRot owner marks."""
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))
import designer_cleanse as DC


FISHERY = "abyss_fishery"
REVIEW_RECORDS = ("review.json", "review_attempt.json", "converge.json", "fixes.json")


def kept_fishery(rows):
    row = rows.get(FISHERY, {})
    what = row.get("what")
    return (row.get("fate") in DC.KEPT and isinstance(what, str)
            and re.search(r"\b(?:fishery|catch(?:es)?)\b", what, re.I) is not None
            and re.search(r"\bno fishery\b", what, re.I) is None)


class OwnerMarksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folders = {mod: ROOT / "design/concepts" / mod / "cleanse"
                       for mod in ("Abyss", "TheRot")}
        cls.rows = {mod: {row["id"]: row for row in cls.read_json(mod, "census.json")["rows"]}
                    for mod in cls.folders}

    @classmethod
    def read_json(cls, mod, name):
        return json.loads((cls.folders[mod] / name).read_text())

    def ticket(self, mod, number):
        md = (self.folders[mod] / "tickets.md").read_text()
        return next(body for heading, body in DC._sections(md) if heading.startswith(number + ":"))

    def bar(self, mod, bar_id):
        return next(bar for bar in self.read_json(mod, "bars.json")["bars"] if bar["id"] == bar_id)

    def kept(self, mod, name):
        return self.rows[mod].get(name, {}).get("fate") in DC.KEPT

    def test_owner_fates(self):
        for mod, name in (("Abyss", "fold_lamp"), ("Abyss", "vine_turning"),
                          ("Abyss", "glowberry_item"), ("TheRot", "pleasure_brew")):
            with self.subTest(name=name):
                self.assertTrue(self.kept(mod, name))
        self.assertEqual("next_version", self.rows["Abyss"]["heat_observation"]["fate"])
        self.assertTrue(kept_fishery(self.rows["Abyss"]))

    def test_fishery_description_and_fate_must_agree(self):
        # A mention of the fishery on the biome-body row cannot fill a gap on the fishery row.
        rows = {"biome_body": {"what": "Biome terrain and fishery habitat", "fate": "land"}}
        self.assertFalse(kept_fishery(rows))
        self.assertTrue(kept_fishery(dict(rows, abyss_fishery={"what": "Catch of veiljaw", "fate": "life"})))
        for what in (None, "", "Unused decorative terrain", "No fishery authored."):
            with self.subTest(what=what):
                self.assertFalse(kept_fishery(dict(rows, abyss_fishery={"what": what, "fate": "life"})))
        for fate in (None, "", [], "invalid", "next_version", "recommend_retire"):
            with self.subTest(fate=fate):
                self.assertFalse(kept_fishery(dict(rows, abyss_fishery={"what": "Abyss fishery", "fate": fate})))

    def test_outdoor_density_with_shipped_lamp(self):
        if self.kept("Abyss", "fold_lamp"):
            ticket = self.ticket("Abyss", "T31")
            self.assertNotIn("T5/T16 keep lane/phantom clearances neutral", ticket)
            acceptance = ticket.split("Acceptance test:", 1)[1]
            self.assertIn("ambient density before lane clearance", acceptance)
            self.assertIn("composed field", acceptance)

    def test_guarded_crown_and_on_site_preparation(self):
        if self.kept("TheRot", "pleasure_brew"):
            ticket = self.ticket("TheRot", "T7")
            acceptance = ticket.split("Acceptance test:", 1)[1]
            bar = self.bar("TheRot", "B3")
            self.assertIn("local spore defense", ticket)
            self.assertIn("undefended crown", acceptance)
            self.assertIn("on-site", acceptance)
            self.assertIn("guarded", " ".join(bar["accept"]))
            self.assertIn("on-site", bar["sees"]["instrument"])

    def test_bush_harvest_produces_glowing_berries(self):
        if self.kept("Abyss", "glowberry_item"):
            ticket = self.ticket("Abyss", "T33A")
            self.assertNotIn("moving harvested berries remain deferred", ticket)
            self.assertIn("Abstract foraging", ticket)
            self.assertIn("RawBerries", ticket)
            acceptance = ticket.split("Acceptance test:", 1)[1]
            self.assertIn("T41", acceptance)
            self.assertIn("bush harvest", acceptance)

    def test_vine_instrument_reads_the_rendered_pose(self):
        if self.kept("Abyss", "vine_turning"):
            bar = self.bar("Abyss", "B3")
            self.assertRegex(bar["sees"]["instrument"], r"T39[^.]*rendered pose")
            self.assertIs(bar["live_only"], True)

    def test_applyable_requires_current_review(self):
        for mod, folder in self.folders.items():
            with self.subTest(mod=mod):
                _, doc = DC.latest_verdict(str(folder))
                if not DC.verdict_current(str(folder), doc):
                    self.assertIs(self.read_json(mod, "result.json").get("applyable"), False)

    def test_fresh_review_can_converge(self):
        for mod, source in self.folders.items():
            with self.subTest(mod=mod), tempfile.TemporaryDirectory() as clone:
                folder = Path(clone) / DC.rel_out(mod)
                folder.mkdir(parents=True)
                for name in (*DC.FILES, *REVIEW_RECORDS):
                    path = source / name
                    if path.is_file():
                        shutil.copyfile(path, folder / name)
                fx = Mock(spec_set=["status", "log", "changed"])
                fx.changed.return_value = []
                with (patch.object(DC, "status_dir", return_value=clone),
                      patch.object(DC, "_hold_refusal", return_value=None),
                      patch.object(DC, "_look", return_value={"defects": [], "refusals": []}),
                      patch.object(DC, "_agent", side_effect=AssertionError("unexpected agent call"))):
                    reviewed = DC.review_mod(mod, fx, clone=clone)
                    self.assertEqual("reviewed", reviewed["state"], reviewed.get("why"))
                    self.assertTrue(DC.verdict_current(str(folder), reviewed["review"]))
                    converged = DC.converge_mod(mod, fx, clone=clone)
                    self.assertEqual("converged", converged["state"], converged.get("why"))

    def test_unreviewed_proposal_has_no_superseded_records(self):
        for mod, folder in self.folders.items():
            result = self.read_json(mod, "result.json")
            if result.get("applyable") is not True:
                with self.subTest(mod=mod):
                    _, verdict = DC.latest_verdict(str(folder))
                    if verdict and verdict.get("digest") == DC.proposal_digest(str(folder)):
                        continue  # A later, current review may legitimately refuse.
                    self.assertEqual([], [name for name in REVIEW_RECORDS if (folder / name).exists()])
                    self.assertEqual((None, None), DC.latest_verdict(str(folder)))

    def test_warm_crown_cannot_be_brewed_the_next_day(self):
        if self.kept("TheRot", "pleasure_brew"):
            bar = self.bar("TheRot", "B3")
            acceptance = self.ticket("TheRot", "T7").split("Acceptance test:", 1)[1]
            self.assertRegex(" ".join(bar["accept"]), r"day it was cut")
            self.assertRegex(" ".join(bar["reject"]), r"warm.*overnight")
            self.assertRegex(bar["sees"]["control"], r"warm.*next local day.*refuse")
            self.assertRegex(acceptance, r"warm.*next local day.*refuse")

    def test_fresh_cup_cannot_be_exported_for_joy_or_memory(self):
        if self.kept("TheRot", "pleasure_brew"):
            bar = self.bar("TheRot", "B3")
            acceptance = self.ticket("TheRot", "T7").split("Acceptance test:", 1)[1]
            self.assertRegex(" ".join(bar["reject"]), r"exported.*(?:joy|memory)")
            for evidence in (bar["sees"]["control"], acceptance):
                self.assertRegex(evidence, r"fresh cup.*another map.*(?:joy|memory)")
                self.assertIn("grants neither chemical joy nor the memory", evidence)

    def test_fishery_requires_a_live_look_at_swimmers_and_catches(self):
        if kept_fishery(self.rows["Abyss"]):
            bar = self.bar("Abyss", "B5")
            self.assertIs(bar["live_only"], True)
            self.assertIn("render", bar["sees"]["live_only_why"])
            acceptance = self.ticket("Abyss", "T51").split("Acceptance test:", 1)[1]
            for evidence in (bar["sees"]["instrument"], acceptance):
                self.assertRegex(evidence, r"live look.*both species.*catches")
            self.assertIn("invisible", " ".join(bar["reject"]))

    def test_proposal_checks(self):
        for mod, folder in self.folders.items():
            with self.subTest(mod=mod):
                self.assertEqual([], DC.check_dir(str(folder))[0])

    def test_checker_rejects_missing_empty_and_invalid_census(self):
        with tempfile.TemporaryDirectory(prefix="cleanse-owner-marks-") as directory:
            folder = Path(directory)
            for name in DC.FILES:
                if name != "census.json":
                    shutil.copyfile(self.folders["Abyss"] / name, folder / name)
            census = folder / "census.json"
            for contents in (None, "", "{invalid", '{"rows": []}'):
                with self.subTest(contents=contents):
                    if contents is not None:
                        census.write_text(contents)
                    refusals, _ = DC.check_dir(str(folder))
                    self.assertTrue(any(r["where"] == "census.json" for r in refusals))


if __name__ == "__main__":
    unittest.main()
