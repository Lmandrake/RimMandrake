#!/usr/bin/env python3
"""Offline checks of the row logic of prove_stage_map.py R3 and R4 (RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS),
fed the shapes that ArchBig replied on 2026-11-24 (list_pawns gives x and z; a lord is {lordJob, toil}; pawn_census gives
the duty as {def}). Red first: the R3 run of 2026-11-24 read 0 of 6 raiders at an edge because it read `position`."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prove_stage_map as P  # noqa: E402

LP = {"id": "Human26136", "x": 99, "z": 55, "faction": "Pirate"}            # list_pawns row, as replied
CEN_STAGE = {"id": "Human26136", "lord": {"loadId": 1, "lordJob": "LordJob_StageThenAttack", "toil": "LordToil_Stage"},
             "duty": {"def": "Defend", "focus": {"x": 85, "z": 55}}}
CEN_ASSAULT = {"id": "Human2", "lord": {"loadId": 2, "lordJob": "LordJob_AssaultColony", "toil": "LordToil_AssaultColony"},
               "duty": {"def": "AssaultColony"}}


def t_a_list_pawns_row_at_the_edge_is_at_the_edge():
    assert P.cell_of(LP) == (99, 55), P.cell_of(LP)
    assert P.at_edge(P.cell_of(LP), (100, 100)) is True
    assert P.at_edge((50, 50), (100, 100)) is False
    assert P.at_edge(None, (100, 100)) is False


def t_assault_is_the_assault_duty_not_a_staging_raid():
    assert P.assaults(CEN_ASSAULT) is True
    assert P.assaults(CEN_STAGE) is False


def t_r4_holds_when_the_journal_agrees_with_the_stage():
    fired = {"def": "RaidEnemy", "outerBodyRan": True, "returned": True, "exception": None, "pawnsSpawnedDuring": 4}
    unfired = {"def": "RaidEnemy", "outerBodyRan": True, "returned": False, "exception": None, "pawnsSpawnedDuring": 0}
    assert P.r4_verdict([fired], 4) is None
    assert P.r4_verdict([unfired], 0) is None
    assert "says" in P.r4_verdict([unfired], 3)
    assert "says" in P.r4_verdict([fired], 0)
    assert "no row" in P.r4_verdict([], 4)
    assert "could not" in P.r4_verdict([{"def": "RaidEnemy", "returned": None}], 4)


def t_r4_reads_the_journal_row_as_replied():
    """The row of ArchBig, 2026-11-24, aseq 191: tri-state strings, and the spawn count of the call."""
    row = {"aseq": 191, "def": "RaidEnemy", "target": "map:1", "called": True, "outerBodyRan": "true", "returned": "true",
           "workerEntered": "unknown", "pawnsGeneratedDuring": 5, "pawnsSpawnedDuring": 5}
    assert P.r4_verdict([row], 5) is None, P.r4_verdict([row], 5)
    assert "says" in P.r4_verdict([row], 0)
    no = dict(row, returned="false", pawnsSpawnedDuring=0, pawnsGeneratedDuring=0)
    assert P.r4_verdict([no], 0) is None, P.r4_verdict([no], 0)
    assert "could not" in P.r4_verdict([dict(row, returned="unknown")], 5)


CHECKS = (t_r4_reads_the_journal_row_as_replied, t_a_list_pawns_row_at_the_edge_is_at_the_edge, t_assault_is_the_assault_duty_not_a_staging_raid, t_r4_holds_when_the_journal_agrees_with_the_stage)


def main():
    passed = 0
    for c in CHECKS:
        try:
            c()
        except Exception as e:  # noqa: BLE001 - a crash of a check is its failure, named
            print("FAIL %s: %s: %s" % (c.__name__, type(e).__name__, e))
        else:
            passed += 1
            print("PASS %s" % c.__name__)
    print("selftest_prove_stage_map_rows: %d checks passed" % passed)
    return int(passed != len(CHECKS))


if __name__ == "__main__":
    raise SystemExit(main())
