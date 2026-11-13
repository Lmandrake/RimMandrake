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
