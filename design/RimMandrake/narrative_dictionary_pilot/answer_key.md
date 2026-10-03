# Answer key — DO NOT give this to the reviewer

Shuffle seed 20261003. Packet room -> condition:

- Room W = **B-dictionary**
- Room X = **B-control**
- Room Y = **A-control**
- Room Z = **A-dictionary**

## Intended claims

### Claim set A — poor but tended

1. Someone sorts every scrap by kind, because nothing here can be wasted.
2. One worker lives in the workshop and sleeps beside the bench.
3. A family lives here, and a child plays among the work.

### Claim set B — rich but abandoned

1. After the garrison left, scavengers forced every locker and took what they could carry.
2. Nobody has been in here for years; the desert is coming in through the door.
3. Someone fought their way in at the blast door, and a wounded defender crawled away.
4. The control station was smashed deliberately by people who hated the Empire, not left to rot.

Only VALID vignettes' claims are intended (A3_daily_path was refused by the validator, so set A has 3). Score each A room (A-dictionary, A-control) against set A's claims and each B room against set B's. Recovered = the reviewer states the substance (not a keyword). False = an asserted history that contradicts the set (e.g. 'abandoned' for an A room; 'someone lives here now' for a B room).

## Scoring sheet (fill after the blind run)

| condition | room | recovered | false claims | notes |
|---|---|---|---|---|
| A-dictionary | Z | | | |
| A-control | Y | | | |
| B-dictionary | W | | | |
| B-control | X | | | |

Verdict = `PASS` iff (A-dict + B-dict recovered) >= 2 x (A-ctrl + B-ctrl recovered) AND dict false <= control false; intended_total = 7 >= 4. If control recovers 0, PASS iff dict recovers >= 1. Bar: README.md (committed before any dressing, c4f7aed27).

## Part 2 — scene -> vignette (prop lists only; tests object + state, placement register removed)

| scene | vignette | claim | validator | recovered? |
|---|---|---|---|---|
| S1 | B1_looted_after_they_left | After the garrison left, scavengers forced every locker and took what they could carry. | PASS | |
| S2 | B2_nobody_for_years | Nobody has been in here for years; the desert is coming in through the door. | PASS | |
| S3 | A3_daily_path | They walk door-to-bench every day; the rest of the floor is kept swept. | REFUSED | |
| S4 | A2_sleeps_at_the_bench | One worker lives in the workshop and sleeps beside the bench. | PASS | |
| S5 | B3_fight_at_the_door | Someone fought their way in at the blast door, and a wounded defender crawled away. | PASS | |
| S6 | B4_wrecked_on_purpose | The control station was smashed deliberately by people who hated the Empire, not left to rot. | PASS | |
| S7 | A4_a_family | A family lives here, and a child plays among the work. | PASS | |
| S8 | A1_sorted_salvage | Someone sorts every scrap by kind, because nothing here can be wasted. | PASS | |

Part 2 has no control and no pre-registered bar: it is diagnostic. It says which vignettes carry their claim through objects alone, so a Part 1 miss can be blamed on placement vs. on the props.
