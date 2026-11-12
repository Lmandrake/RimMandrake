# JUDGE: RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES

Judge: blind check (CLAUDE_STEVEDESKTOP_OFFLINE5 lane, no game), 2026-11-11, repo HEAD b231dc0b0b.
Read: STATEMENT.md, NOTES.md, evidence/*, the item file, ANSWERS_OWNER.md, HugeThings.md north-star, About.xml. Not read: DONE.md, BROADEN.md.
Evidence has no images; nothing to view.

## A1 L0: implementation and current specifications agree with the cited owner answer; focused offline checks pass. -> true
- Owner answers 1-2 (design/RimMandrake/hugethings_codex_2026-11-09/ANSWERS_OWNER.md): two promises, each with its own demonstration; first demo is crossing, then death, then crowd.
- evidence/a1_spec_split.txt and the files themselves agree: design/validation_walks/RimMandrake/HugeThings.md lines 82-102 have two must-show groups, each naming its own driver (showcase_plants_live.py, showcase_titan_live.py), plus cannot-show `one_demo_for_both_promises` and `showcase_out_of_order`; About.xml (src/RimMandrake/HugeThings/About/About.xml) now reads "two promises", GIANT PLANTS / TITANS. The door-seal line matches owner answer 4.
- Both driver files exist in src/RimMandrake/HugeThings/northstar/.
- I re-ran `run_selftests.py --only .../selftest_showcases.py --workers 1`: exit 0, PASS 1/1, GREEN. Same as evidence/a1_selftest_showcases.txt. The verbose log shows the test also checks the ordering gate: when the crossing fails, DEATH and CROWD stay UNMEASURED and are never run out of order.
- Scope note: this check uses a fake bridge. It shows the drivers' logic and ordering. It does not show game behaviour, and A1 does not claim that.

## A2 L2: Separate restored disposable-site demonstrations support both promises; titan showcase orders crossing, death, crowd. -> false
- No demonstration was run. Every result in the evidence comes from the offline fake bridge ("HARNESS fake preflight"). There is no live run log, live_results row, screenshot or save from a restored disposable site for either promise. On L2 the scripts exist, but nothing shows they "support" either promise in the game.
- Even in the fake run, the plant promise is incomplete: PLANT_selection is UNMEASURED ("no instrument: CompHugeFootprint.SelectRect() is an instance method with no bridge or static hook"). So one plant must-show (`plant_click_selects_picture`) has no instrument at all, and a live run could not settle it either.
- Staging: the titan death is caused by the driver (3 x 400 Bullet damage through jawa/damage, which the log itself calls "the cause is staged"). The crowd phase forces the arrival with one SiteDailyStep, and it checks after 1000 ticks. These are fair for showing the order. They do not test whether a crowd comes in ordinary play. That would be acceptable at L2 only with a live run, and there is none.
- What would settle it: one live run of each driver on a restored disposable site (a BENCH/live lane), with a raw log and live_results rows showing CROSSING -> DEATH -> CROWD PASS in order, and the plant phases PASS. That needs a selection instrument (a bridge hook for SelectRect, or a real click test), and before/after images of the crossing damage and the sealed and then cut doorway.

## Rows 3-5
Blank in STATEMENT.md; nothing to judge.

## Owed
- Live runs of showcase_titan_live.py and showcase_plants_live.py (needs a live lane), and a PLANT_selection instrument.
- L4 feel stays with the owner (per the statement).

would show: no
