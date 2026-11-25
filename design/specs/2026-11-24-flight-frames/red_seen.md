# flight_frames: each promise seen red on a planted fault (2026-11-24, SteveDesktop)

Each plant is one edit of `src/RimMandrake/Utils/flight_frames.py` (`a|b`: replace a with b), reverted after its run; the real file reads 8 checks passed.
Plant 4 of the first batch (an extra `break`) changed nothing and stayed green; it was replaced by the `if False:` plant.

```
PLANT: return -(-anim_tick // tpf)|return anim_tick // tpf
FAIL a full flight passes: (['Chicken101/pawn.flight.state', 'Chicken101/pawn.flight.lerp_tick', 'Chicken101/pawn.flight.height', 'Chicken101/pawn.anim.name', 'Chicken101/pawn.anim.start_tick', 'Chicken101/pawn.anim.graphic', 'Chicken101/pawn.anim.texpath', 'Chicken101/pawn.anim.facing'], 'FAIL', [{'code': 'FRAME', 'tick': 106, 'why': "graphic 'ChickenFlyEast_1', the clock selects 'ChickenFlyEast_0'"}, {'code': 'TEXPATH', 'tick': 106, 'why': "texPath 'Things/Pawn/Animal/Chicken/Chicken_Flying_2_east', want 'Things/Pawn/Animal/Chicken/Chicken_Flying_1_east'"}])
FAIL a bird still in the air at the limit is not judged: ('NOT JUDGED', [{'from': 105, 'to': None, 'judged': 'in the air at the limit'}])
flight frames selftest: FAIL 2
PLANT: (TAKING_OFF, LANDING), (FLYING, LANDING)|(TAKING_OFF, LANDING), (FLYING, LANDING), (FLYING, GROUNDED)
FAIL a skipped state fails: ('PASS', [])
flight frames selftest: FAIL 1
PLANT: and n > 1 and len(seen) == 1|and n > 99
FAIL a flip-book that repeats one frame fails: ['FRAME', 'TEXPATH']
flight frames selftest: FAIL 1
PLANT:         break\n    return faults|        break\n        break\n    return faults
flight frames selftest: 8 checks passed
PLANT: if not any(os.path.isfile|if False and not any(os.path.isfile
FAIL the asset audit names a missing texture: ([], [], [])
flight frames selftest: FAIL 1
PLANT: if rows[i]["anim"] or rows[i]["graphic"]:|if False:
FAIL a landing that keeps a flying picture fails
flight frames selftest: FAIL 1
PLANT: k = expected_frame(r["tick"], r["start"], n, tpf)|k = int(r["graphic"].rsplit("_", 1)[1]) if r["graphic"] else 0
FAIL a frame held for the wrong number of ticks fails
flight frames selftest: FAIL 1
PLANT:     return "COULD NOT LOOK"|    return "RANDOM MISS"
FAIL a bird still in the air at the limit is not judged: ('NOT JUDGED', [{'from': 105, 'to': None, 'judged': 'in the air
flight frames selftest: FAIL 1
PLANT: if all(v == NO_FLIGHT for v in vs):|if all(v == "x" for v in vs):
FAIL "no bird took off" is an allowed miss: NO FLIGHT
flight frames selftest: FAIL 1
```
