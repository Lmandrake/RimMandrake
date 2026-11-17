# Pyrelands: Polish list

Polish improves play but is not part of passing 0.1.0. **Each entry below is PROPOSED, awaiting his confirmation**, and the decision is marked here when he gives it (owner, by card 2026-11-13).

## RIMMANDRAKE_SHARPEN_BLACK_RAIN_CONTROL_AGAINST_DRY_ASH_WEAR
- **From:** coverage gap g8 of rm-coverage-judge-1794594804 (2026-11-13). Proposed by this sort, 2026-11-13. Least-sure call: it could be a Problem.
- **Why:** `sc_three_skies` reads loose ash falling under black rain but has no clear-sky ash patch, so ordinary dry wear (ash lasts about ten days dry) could pass for black rain washing it away.
- **Change:** add an equal ash patch under clear sky for the same half day to the scene's start and control, and a stated margin to its expect.
- **Acceptance test:** `python3 -c "import json,sys;x=[c for c in json.load(open('design/concepts/Pyrelands/scenes.json'))['scenes'] if c['id']=='sc_three_skies'][0];c=json.dumps(x['control']).lower();e=x['expect'].lower();sys.exit(0 if 'ash patch' in c and 'clear' in c and any(w in e for w in ('margin','exceeds','more than')) else 1)"` — exit 0 passes, 1 fails; **watched it fail** on 237b791167. Coarse (text, not behaviour): the live read comes with the scene.
- **Decision:** pending his confirmation.

## RIMMANDRAKE_TUNE_PYRE_REGREEN_TOWARD_NEARLY_ALL_GREEN
- **From:** `sheet.md` advisory: "A week-old scar is about 60% green, inside his card thresholds; nearly-all-green is playtest tuning".
- **Why:** a burn that is nearly all green after a week reads closer to "largely green again", but 60% already meets his thresholds.
- **Acceptance test:** none, playtest tuning judged by eye in play; the locked bar is already met by the threshold.
- **Decision:** pending his confirmation.

## RIMMANDRAKE_TEST_FIREHAWK_PICKS_LARGEST_FUEL
- **From:** coverage gap g3 of rm-coverage-judge-1794750987 (2026-11-15). Proposed by the round-6 sort, 2026-11-15 (Evidence-for-Ask, a Conductor sort). Least-sure call: it could be a Problem if a hawk is seen dropping embers on scraps.
- **Why:** `inv_firehawk_ember` says the hawk takes the ember to the largest easily found fuel. `sc_firehawk` reads only that a fire starts at the drop cell beyond the front, so a hawk that picks any fuel passes. A player would hardly tell the largest fuel from a large one.
- **Change:** in `sc_firehawk`, stage two fuel piles of clearly different size, both in reach. The expect is that the drop lands on the larger pile. The control is to remove the larger pile, after which the drop goes to the smaller.
- **Acceptance test:** `python3 -c "import json,sys;x=[c for c in json.load(open('design/concepts/Pyrelands/scenes.json'))['scenes'] if c['id']=='sc_firehawk'][0];sys.exit(0 if 'larg' in x['expect'].lower() and 'larg' in json.dumps(x['control']).lower() else 1)"`
- **Decision:** pending his confirmation.

## RIMMANDRAKE_RESTORE_PYRE_WIND_SCENE_GROUND
- **From:** advisory gap of the launcher's coverage look rm-coverage-judge-1794938280 (2026-11-17, scenes.json:48, scenes.json:30). The second look rated the wind gap a Problem and named this restore as Polish. Placed here by option A, a delegated Evidence-for-Ask call (CONDUCTOR:1794939817434538611), for his veto.
- **Why:** `sc_fire_walks_with_wind` restore reads "settings, weather and fires are put back by wind_burn_live.py", on a current Pyrelands map rather than a throwaway quicktest. The script's strip() clears plants and lays deep ash over three 68x29 areas, which then burn, and nothing puts the terrain or plants back.
- **Change:** `wind_burn_live.py` records the terrain and plants of the three areas before strip() and puts them back after the read. The scene's restore says so.
- **Acceptance test:** `python3 -c "import json,sys;x=[c for c in json.load(open('design/concepts/Pyrelands/scenes.json'))['scenes'] if c['id']=='sc_fire_walks_with_wind'][0];r=json.dumps(x.get('restore','')).lower();sys.exit(0 if 'terrain' in r and 'plant' in r else 1)"` (exit 0 passes, 1 fails; **watched it fail** on b0866a08d3). Coarse, because it reads the text and not the behaviour. The script's own restore is proved by the live run that comes with the scene.
- **Decision:** pending his confirmation.
