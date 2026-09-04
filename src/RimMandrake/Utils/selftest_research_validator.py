#!/usr/bin/env python3
"""selftest_research_validator.py - fast, offline, no-game selftest for
research_manifest_validate.py (RESEARCH_VALIDATOR_BUILD_1).

Loads the tiny synthetic fixture at
`src/RimMandrake/Utils/testdata/research_validator_selftest_fixture.csv`
through the real `load_manifest()` CSV path, builds a hand-authored `live`
dict and a stub `cuts` object (no def-dump capture, no live Cherry Picker
settings file, no ModsConfig.xml - genuinely offline), and calls each of the
7 taxonomy-doc checks directly. Every check gets at least one row engineered
to FAIL it and at least one row engineered to PASS it, so a check that always
says "fine" cannot hide behind an all-pass fixture.

Two calibration cases from the taxonomy/prep docs are reproduced by real
defName, not invented data:
  - `RimFridge_PowerFactorSetting` requires itself (the one shipped vanilla
    self-loop) -> the cycle check must report it as INFO, never FAIL.
  - `Electricity` carrying Research Reinvented's techprintCount+`RR_` prereq
    stamp -> the co-writer check must PASS when that stamp is present and
    FAIL when it is missing (simulating a raw/pre-patch dump).

Run:  python3 src/RimMandrake/Utils/selftest_research_validator.py
Exit 0 = every assertion behaved as engineered. Exit 1 = the validator
disagrees with a documented, calibrated expectation - a real regression.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import research_manifest_validate as rv          # noqa: E402

FIXTURE = HERE / "testdata" / "research_validator_selftest_fixture.csv"

FAILED = []
CHECKED = [0]


def expect(label, condition, detail=""):
    CHECKED[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s%s" % (label, ("  -- " + detail) if detail else ""))
        FAILED.append(label)


def names(issues, level=None):
    return {i.defname for i in issues if level is None or i.level == level}


# --------------------------------------------------------------- fixtures

def build_live():
    """Hand-authored live-dump stand-in: only what each check reads
    (prerequisites, hiddenPrerequisites, techLevel, cachedUnlockedDefs)."""
    def d(techLevel="Industrial", prereqs=None, unlocks=None, techprintCount=0):
        return {"techLevel": techLevel, "prerequisites": prereqs or [],
                "hiddenPrerequisites": [], "cachedUnlockedDefs": unlocks or [],
                "techprintCount": techprintCount}

    live = {
        "Electricity": d(prereqs=["RR_ElectricityBasics"], unlocks=["PowerConduit"],
                         techprintCount=1),
        "Machining": d(unlocks=["Toolbox"]),
        "GoodProject": d(unlocks=["Widget"]),
        "CutTargetProject": d(unlocks=["DeadWidget"]),
        "Bioregeneration": d(techLevel="Neolithic", unlocks=[]),
        "PrereqA": d(unlocks=["A_Widget"]),
        "PrereqB": d(prereqs=["PrereqA"], unlocks=["B_Widget"]),
        "BadPrereqRow": d(prereqs=["CutProject"], unlocks=["BPR_Widget"]),
        "CutProject": d(unlocks=["CP_Widget"]),
        "RimFridge_PowerFactorSetting": d(
            prereqs=["RimFridge_PowerFactorSetting"], unlocks=["RF_Widget"]),
        "CycleA": d(prereqs=["CycleB"], unlocks=["CA_Widget"]),
        "CycleB": d(prereqs=["CycleA"], unlocks=["CB_Widget"]),
        "BandBad": d(techLevel="Industrial", unlocks=["BandBad_Widget"]),
        "TechMismatch": d(techLevel="Ultra", unlocks=["TM_Widget"]),
        "FormBlasterA": d(techLevel="Spacer", unlocks=["Blaster1"]),
        "FormBlasterB": d(techLevel="Spacer", unlocks=["Blaster2"]),
        # present live but deliberately absent from the manifest -> coverage FAIL
        "UncoveredProject": d(unlocks=["Uncovered_Widget"]),
    }
    return live


class StubCuts:
    """Duck-types cherrypicker.Cuts.cut_name() with a fixed cut set - no
    live Cherry Picker settings file is read."""

    def __init__(self, cut_names):
        self._cut = set(cut_names)

    def cut_name(self, name):
        return name in self._cut

    def cut(self, deftype, name):
        # The stub's cut set is untyped; the typed query degrades to the name
        # match, which is exactly what the tests' fixtures intend.
        return name in self._cut

    def provenance(self):
        return "stub cuts: %d name(s), selftest fixture (no live settings file read)" % len(self._cut)


CUTS = StubCuts({"DeadWidget"})   # CutTargetProject's ONLY unlock -> orphan FAIL


# ------------------------------------------------------------------ checks

def main():
    print("loading fixture: %s" % FIXTURE)
    rows, meta = rv.load_manifest(str(FIXTURE))
    print("  %d rows, meta=%s" % (len(rows), meta))
    expect("fixture parses to the expected row count", len(rows) == 16,
           "got %d" % len(rows))
    expect("leading '#' meta line parsed (fingerprint)",
           meta.get("fingerprint") == "selftestfp0001", str(meta))

    live = build_live()
    shape_issues = rv.validate_shape(rows)
    expect("shape check: clean fixture has no shape FAILs",
           not any(i.level == rv.FAIL for i in shape_issues),
           "; ".join(i.line() for i in shape_issues))

    # ---- check 1: orphan -------------------------------------------------
    orphan_issues = rv.check_orphans(rows, live, CUTS)
    expect("check1 orphan: CutTargetProject FAILs (all unlocks cut)",
           "CutTargetProject" in names(orphan_issues, rv.FAIL))
    expect("check1 orphan: GoodProject does not FAIL (live, uncut)",
           "GoodProject" not in names(orphan_issues, rv.FAIL))
    expect("check1 orphan: Bioregeneration silent (on the empty-cache allowlist)",
           "Bioregeneration" not in names(orphan_issues))

    # ---- check 2: prereq resolution --------------------------------------
    prereq_issues = rv.check_prereqs(rows, live, CUTS)
    expect("check2 prereq: BadPrereqRow FAILs (prereqs a fate=cut row)",
           "BadPrereqRow" in names(prereq_issues, rv.FAIL))
    expect("check2 prereq: PrereqB does not FAIL (valid prereq on PrereqA)",
           "PrereqB" not in names(prereq_issues, rv.FAIL))

    # ---- check 3: band conformance ---------------------------------------
    band_issues = rv.check_bands(rows, live)
    expect("check3 band: BandBad FAILs (cost far outside T0's band)",
           "BandBad" in names(band_issues, rv.FAIL))
    expect("check3 band: TechMismatch FAILs (techLevel Ultra not in T0 map)",
           "TechMismatch" in names(band_issues, rv.FAIL))
    expect("check3 band: Machining passes clean (Industrial/1200 inside T1)",
           "Machining" not in names(band_issues, rv.FAIL))

    # ---- check 4: one-chain-per-form --------------------------------------
    form_issues = rv.check_one_chain_per_form(rows)
    expect("check4 one-chain-per-form: FAILs on the split 'blaster' form",
           any("blaster" in i.msg for i in form_issues if i.level == rv.FAIL))

    # ---- check 5: coverage -------------------------------------------------
    cov_issues = rv.check_coverage(rows, live, meta, {"hash": "selftestfp0001", "modCount": 3})
    expect("check5 coverage: FAILs on the unmapped 17th live def (16 rows vs 17 live)",
           any(i.level == rv.FAIL and "coverage" == i.check and "NO manifest row"
               in i.msg for i in cov_issues))
    expect("check5 coverage: fingerprint matches -> no fingerprint FAIL",
           not any("declares fingerprint" in i.msg for i in cov_issues if i.level == rv.FAIL))
    cov_bad_fp = rv.check_coverage(rows, live, meta, {"hash": "DIFFERENT", "modCount": 9})
    expect("check5 coverage: FAILs on fingerprint mismatch (deliberate)",
           any(i.level == rv.FAIL and "declares fingerprint" in i.msg for i in cov_bad_fp))

    # ---- schema v2: the `live` column (F2, canon_reintegration_plan.md) ----
    # A row whose def cannot be in the dump yet (a deployed mod awaiting its
    # restart, or a planned def) declares live=pending-restart/planned. It is
    # excluded from the orphan check and from the coverage EQUALITY (listed as
    # INFO) - the check must not weaken for live rows.
    pend = rv._normalize_row({"defName": "NotYetLiveRow", "source_mod": "x",
                              "fate": "keep", "tab": "T", "tier": "T0",
                              "cost": "400", "live": "planned"})
    expect("schema v2: live defaults to 'yes' when the column is absent",
           rows[0].get("live") == "yes", repr(rows[0].get("live")))
    v2_rows = rows + [pend]
    v2_orphans = rv.check_orphans(v2_rows, live, CUTS)
    expect("schema v2: a live=planned row is NOT an orphan FAIL",
           "NotYetLiveRow" not in names(v2_orphans, rv.FAIL))
    v2_cov = rv.check_coverage(v2_rows, live, meta,
                               {"hash": "selftestfp0001", "modCount": 3})
    expect("schema v2: coverage equality excludes live!=yes rows",
           not any(i.level == rv.FAIL and "manifest has 17" in i.msg for i in v2_cov))
    expect("schema v2: the excluded row is INFO-listed by coverage",
           "NotYetLiveRow" in names(v2_cov, rv.INFO))

    # ---- check 6: cycle -----------------------------------------------------
    cycle_issues = rv.check_cycles(rows)
    expect("check6 cycle: synthetic CycleA/CycleB FAILs",
           any(i.level == rv.FAIL and "CycleA" in i.msg and "CycleB" in i.msg
               for i in cycle_issues))
    expect("check6 cycle: RimFridge_PowerFactorSetting reports INFO, not FAIL "
           "(calibration: the one shipped vanilla self-loop)",
           "RimFridge_PowerFactorSetting" in names(cycle_issues, rv.INFO)
           and "RimFridge_PowerFactorSetting" not in names(cycle_issues, rv.FAIL))

    # ---- check 7: co-writer awareness ---------------------------------------
    rr_active = {"petetimessix.researchreinvented"}
    pass_issues = rv.check_resolved_dump(live, rr_active)
    expect("check7 co-writer: PASSes when Electricity carries the RR stamp",
           not any(i.level == rv.FAIL for i in pass_issues))

    live_raw = dict(live)
    live_raw["Electricity"] = {"techLevel": "Industrial", "prerequisites": [],
                                "hiddenPrerequisites": [], "cachedUnlockedDefs": [],
                                "techprintCount": 0}
    fail_issues = rv.check_resolved_dump(live_raw, rr_active)
    expect("check7 co-writer: FAILs when the RR stamp is missing (raw/pre-patch dump)",
           any(i.level == rv.FAIL for i in fail_issues))

    # ---- summary --------------------------------------------------------
    print("\n%d assertion(s) checked, %d failed" % (CHECKED[0], len(FAILED)))
    if FAILED:
        print("FAILED assertions:")
        for f in FAILED:
            print("  - %s" % f)
        print("\nSELFTEST FAIL")
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
