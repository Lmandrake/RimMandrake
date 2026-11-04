#!/usr/bin/env python3
"""selftest_flyer_variants_mutants.py - selftest_flyer_variants.py must still go red when the art stops being his.

It accepts a rescaled picture on ledger lineage plus a pixel comparison; each mutant breaks one link on real data, and
same_art is scored on real pictures: every rescale must pass and every other column of the same creature must fail.
"""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selftest_flyer_variants as m  # noqa: E402

CASE = m.CASES[0]  # Fleet Flier: alt C south and north were rescaled, alt B was not
RESCALED = f"{CASE['base']}V_C_south.png"
KEY = f"{CASE['mod']}/{RESCALED}"


def run(live, rulings, history, case=CASE) -> list[str]:
    return m.check_case(case, live, rulings, history)


def picture(case: dict, letter: str, facing: str) -> bytes:
    return (m.REPO / case["mod"] / "Textures" / f"{case['base']}V_{letter}_{facing}.png").read_bytes()


def main() -> int:
    live, rulings, history = m.ledger()
    fails = []

    def expect_red(label: str, rows: list[str]) -> None:
        if not any("RM_FleetFlier C south" in r for r in rows):
            fails.append(f"{label}: stayed green")

    baseline = run(live, rulings, history)
    if baseline:
        fails.append(f"baseline red: {baseline[:2]}")

    foreign = copy.deepcopy(CASE)
    foreign["alts"]["C"]["south"] = "deadbeef0000"
    expect_red("pin no chain reaches", run(live, rulings, history, foreign))

    unlogged = dict(live)
    unlogged[KEY] = {**live[KEY], "sha": "0" * 64}
    expect_red("disk differs from the ledger's latest install", run(unlogged, rulings, history))

    broken = copy.deepcopy(history)
    del broken[KEY][live[KEY]["prev"]]
    expect_red("ledger chain broken", run(live, rulings, broken))

    other_words = copy.deepcopy(rulings)
    other_words[live[KEY]["ruling_id"]]["by_card"] = "some other card"
    expect_red("step under other words", run(live, other_words, history))

    root_words = copy.deepcopy(rulings)
    root_words[history[KEY][live[KEY]["prev"]]["ruling_id"]]["said"] = "not his words"
    expect_red("root without his words", run(live, root_words, history))

    real_same_art, m.same_art = m.same_art, lambda ruled, now: "a redraw"
    expect_red("pixels differ", run(live, rulings, history))
    m.same_art = real_same_art

    real_fixtures, pin = m.FIXTURES, CASE["alts"]["C"]["south"]
    with tempfile.TemporaryDirectory() as tmp:
        m.FIXTURES = Path(tmp)
        expect_red("fixture missing", run(live, rulings, history))
        (m.FIXTURES / f"{pin}.png").write_bytes((real_fixtures / f"{CASE['alts']['C']['north']}.png").read_bytes())
        expect_red("fixture is another picture, so does not hash to its pin", run(live, rulings, history))
    m.FIXTURES = real_fixtures

    scored = 0
    for case in m.CASES:
        for letter, shas in case["alts"].items():
            for facing, want in shas.items():
                rel = f"{case['base']}V_{letter}_{facing}.png"
                ruled = m.ruled_bytes(picture(case, letter, facing), want)
                fault = m.same_art(ruled, picture(case, letter, facing))
                if fault:
                    fails.append(f"{rel}: a real picture scored as a redraw: {fault}")
                for other in case["alts"]:
                    scored += other != letter
                    if other != letter and not m.same_art(ruled, picture(case, other, facing)):
                        fails.append(f"{rel}: column {other} scored as the same art")
    for f in fails:
        print("FAIL:", f)
    if fails:
        return 1
    print(f"selftest_flyer_variants_mutants: PASS (8 mutants red, {scored} other columns refused)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
