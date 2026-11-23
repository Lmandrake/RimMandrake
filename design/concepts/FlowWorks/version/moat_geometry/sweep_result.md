# Flagship moat: region map (sweep.py)

## Depth and water level (the mod's rules, no simulation)

| dug | water | raiders enter | swim and tire | holds while draining | drained floor is a prison |
|---|---|---|---|---|---|
| 1.5 m | 1.5 m (brim) | yes | no | yes, once it fell more than 1.0 m | **no** (under 3 m) |
| 2.0 m | 2.0 m (brim) | yes | yes | yes, once it fell more than 1.0 m | **no** (under 3 m) |
| 2.0 m | 1.5 m | yes | no | yes, once it fell more than 0.5 m | **no** (under 3 m) |
| 2.5 m | 2.5 m (brim) | yes | yes | yes, once it fell more than 1.0 m | **no** (under 3 m) |
| 2.5 m | 2.0 m | yes | yes | yes, once it fell more than 0.5 m | **no** (under 3 m) |
| 2.5 m | 1.5 m | yes | no | yes, at the first fall | **no** (under 3 m) |
| 3.0 m | 3.0 m (brim) | yes | yes | yes, once it fell more than 1.0 m | yes |
| 3.0 m | 2.5 m | yes | yes | yes, once it fell more than 0.5 m | yes |
| 3.0 m | 2.0 m | yes | yes | yes, at the first fall | yes |
| 3.0 m | 1.5 m | **no**: 1.5 m of wall | no | - | yes |
| 3.5 m | 3.5 m (brim) | yes | yes | yes, once it fell more than 1.0 m | yes |
| 3.5 m | 3.0 m | yes | yes | yes, once it fell more than 0.5 m | yes |
| 3.5 m | 2.5 m | yes | yes | yes, at the first fall | yes |
| 3.5 m | 2.0 m | **no**: 1.5 m of wall | no | - | yes |
| 4.0 m | 4.0 m (brim) | yes | yes | yes, once it fell more than 1.0 m | yes |
| 4.0 m | 3.5 m | yes | yes | yes, once it fell more than 0.5 m | yes |
| 4.0 m | 3.0 m | yes | yes | yes, at the first fall | yes |
| 4.0 m | 2.5 m | **no**: 1.5 m of wall | no | - | yes |
| 5.0 m | 5.0 m (brim) | yes | yes | yes, once it fell more than 1.0 m | yes |
| 5.0 m | 4.5 m | yes | yes | yes, once it fell more than 0.5 m | yes |
| 5.0 m | 4.0 m | yes | yes | yes, at the first fall | yes |
| 5.0 m | 3.5 m | **no**: 1.5 m of wall | no | - | yes |

## Width: time in the water and the exhaustion check

| wide | in the water, ticks (fast / median / slow raider) | share of raiders a 250-tick check catches |
|---|---|---|
| 1 | 16 / 20 / 24 | 8% |
| 2 | 110 / 132 / 165 | 53% |
| 3 | 203 / 244 / 305 | 94% |
| 4 | 296 / 357 / 445 | 99% |
| 5 | 390 / 469 / 585 | 100% |
| 6 | 483 / 582 / 725 | 100% |
| 7 | 577 / 694 / 865 | 100% |
| 8 | 670 / 806 / 1006 | 100% |

## Drain, by the kernel: pulses (250 ticks) until it holds a person / until dry. `-` = the pit is too small, it never empties

| moat (plot 8x8) | 7x7 10 m, 1 sluice | 9x9 10 m, 1 sluice | 11x11 10 m, 1 sluice | 9x9 20 m, 1 sluice | 11x11 20 m, 1 sluice | 9x9 20 m, 3 sluices | 11x11 10 m, 3 sluices |
|---|---|---|---|---|---|---|---|
| 1 wide, 3 m | 3 / 5 | 3 / 5 | 3 / 5 | 3 / 4 | 3 / 4 | 2 / 3 | 3 / 5 |
| 2 wide, 3 m | 4 / 8 | 4 / 8 | 4 / 7 | 4 / 5 | 4 / 5 | 3 / 4 | 4 / 6 |
| 3 wide, 3 m | 5 / - | 5 / 10 | 5 / 9 | 4 / 6 | 4 / 6 | 3 / 5 | 4 / 8 |
| 4 wide, 3 m | 6 / - | 6 / - | 6 / 12 | 5 / 7 | 5 / 7 | 4 / 7 | 5 / 11 |
| 5 wide, 3 m | 7 / - | 7 / - | 7 / 15 | 5 / 9 | 5 / 8 | 4 / 8 | 6 / 14 |
| 6 wide, 3 m | 9 / - | 8 / - | 8 / - | 6 / 10 | 6 / 10 | 5 / 9 | 7 / - |
| 7 wide, 3 m | 10 / - | 9 / - | 8 / - | 6 / 12 | 6 / 11 | 5 / 11 | 8 / - |
| 8 wide, 3 m | - / - | 10 / - | 9 / - | 7 / - | 7 / 12 | 6 / - | 8 / - |
| 1 wide, 4 m | 3 / 7 | 3 / 6 | 3 / 6 | 3 / 4 | 3 / 4 | 2 / 4 | 3 / 5 |
| 2 wide, 4 m | 4 / - | 4 / 10 | 4 / 9 | 4 / 6 | 4 / 6 | 3 / 5 | 3 / 8 |
| 3 wide, 4 m | 5 / - | 5 / - | 5 / 12 | 4 / 7 | 4 / 7 | 3 / 6 | 4 / 11 |
| 4 wide, 4 m | 6 / - | 6 / - | 6 / - | 5 / 9 | 5 / 9 | 4 / 8 | 5 / - |
| 5 wide, 4 m | 7 / - | 7 / - | 7 / - | 5 / 11 | 5 / 10 | 4 / 10 | 6 / - |
| 6 wide, 4 m | 9 / - | 8 / - | 8 / - | 6 / - | 6 / 12 | 5 / - | 7 / - |
| 7 wide, 4 m | 10 / - | 9 / - | 8 / - | 6 / - | 6 / 14 | 5 / - | 7 / - |
| 8 wide, 4 m | - / - | 10 / - | 9 / - | 7 / - | 7 / - | 6 / - | 8 / - |

## The scene before the decision (moat drains in zero game time), model against the 21 recorded runs

| wide | a raider tired | two or more held | both |
|---|---|---|---|
| 2, recorded | 19/21 = 90% | 15/21 = 71% | 15/21 = 71% |
| 1 | 43% | 0% | 0% |
| 2 | 97% | 75% | 75% |
| 3 | 99% | 95% | 95% |
| 4 | 100% | 100% | 100% |
| 5 | 100% | 100% | 100% |
| 6 | 100% | 100% | 100% |
| 7 | 100% | 100% | 100% |
| 8 | 100% | 100% | 100% |

## Played in game time: share of raids with two or more held AND a raider tired, by width and by how many pulses the drain needs to hold

### sluice opened when the first raider reaches the bank

| wide | 1 pulses | 2 pulses | 3 pulses | 4 pulses | 5 pulses | 6 pulses | 7 pulses | 8 pulses |
|---|---|---|---|---|---|---|---|---|
| 1 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 2 | 14% | 33% | 15% | 2% | 0% | 0% | 0% | 0% |
| 3 | 23% | 65% | 45% | 10% | 2% | 1% | 1% | 0% |
| 4 | 26% | 73% | 75% | 30% | 6% | 3% | 2% | 0% |
| 5 | 26% | 77% | 90% | 57% | 16% | 5% | 3% | 1% |
| 6 | 26% | 78% | 94% | 78% | 34% | 7% | 4% | 2% |
| 7 | 26% | 79% | 95% | 92% | 58% | 15% | 5% | 3% |
| 8 | 26% | 79% | 95% | 96% | 80% | 32% | 7% | 4% |

### opened when the first raider is in the water

| wide | 1 pulses | 2 pulses | 3 pulses | 4 pulses | 5 pulses | 6 pulses | 7 pulses | 8 pulses |
|---|---|---|---|---|---|---|---|---|
| 1 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 2 | 28% | 22% | 12% | 0% | 0% | 0% | 0% | 0% |
| 3 | 49% | 53% | 38% | 5% | 1% | 0% | 0% | 0% |
| 4 | 55% | 75% | 61% | 20% | 3% | 0% | 0% | 0% |
| 5 | 56% | 84% | 82% | 42% | 7% | 1% | 0% | 0% |
| 6 | 56% | 87% | 94% | 62% | 21% | 2% | 0% | 0% |
| 7 | 56% | 88% | 98% | 82% | 42% | 7% | 0% | 0% |
| 8 | 56% | 88% | 99% | 94% | 62% | 20% | 2% | 0% |

### opened when two are in the water

| wide | 1 pulses | 2 pulses | 3 pulses | 4 pulses | 5 pulses | 6 pulses | 7 pulses | 8 pulses |
|---|---|---|---|---|---|---|---|---|
| 1 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 2 | 38% | 7% | 1% | 0% | 0% | 0% | 0% | 0% |
| 3 | 86% | 32% | 8% | 0% | 0% | 0% | 0% | 0% |
| 4 | 96% | 72% | 24% | 3% | 0% | 0% | 0% | 0% |
| 5 | 99% | 95% | 47% | 9% | 1% | 0% | 0% | 0% |
| 6 | 100% | 99% | 77% | 24% | 3% | 0% | 0% | 0% |
| 7 | 100% | 99% | 96% | 47% | 8% | 0% | 0% | 0% |
| 8 | 99% | 100% | 99% | 75% | 23% | 2% | 0% | 0% |

## Freeboard: a moat dug 4 m whose water stands 0, 0.5, 0.75 or 1 m below the lip (pit 11x11, 10 m, 1 sluice; plot 8x8)

Pulses until it holds / until dry, then the share of raids with two or more held and a raider tired when the sluice opens with two in the water.

| wide | 4.00 m of water | 3.50 m of water | 3.25 m of water | 3.10 m of water | 3.00 m of water |
|---|---|---|---|---|---|
| 1 | 3 / 6: **0%** | 3 / 6: **0%** | 2 / 6: **3%** | 2 / 6: **3%** | 1 / 6: **25%** |
| 2 | 4 / 9: **0%** | 4 / 8: **0%** | 3 / 8: **6%** | 2 / 8: **24%** | 1 / 8: **79%** |
| 3 | 5 / 12: **0%** | 4 / 11: **1%** | 3 / 11: **19%** | 3 / 10: **19%** | 1 / 10: **96%** |
| 4 | 6 / -: **0%** | 5 / 15: **0%** | 4 / 14: **8%** | 3 / 13: **40%** | 1 / 13: **99%** |
| 5 | 7 / -: **0%** | 5 / -: **1%** | 4 / -: **20%** | 3 / -: **72%** | 1 / -: **99%** |
| 6 | 8 / -: **0%** | 6 / -: **0%** | 5 / -: **7%** | 3 / -: **93%** | 1 / -: **99%** |
| 7 | 8 / -: **0%** | 6 / -: **1%** | 5 / -: **19%** | 4 / -: **71%** | 1 / -: **99%** |
| 8 | 9 / -: **0%** | 7 / -: **0%** | 5 / -: **40%** | 4 / -: **92%** | 1 / -: **99%** |

## The pick (4 wide, dug 4 m, 3 m of water, 7x7 pit 20 m, one sluice) under worse assumptions

Level after each pulse, m: 3.00, 2.98, 2.89, 2.60, 2.14, 1.53, 0.96, 0.43, 0.00; holds after pulse 1, dry after pulse 8 (2000 ticks).

| assumption | two or more held and a raider tired |
|---|---|
| as the map | 99% |
| no climb cost at the rim | 96% |
| the player opens one pulse late | 92% |
| only 3 in 10 of the raiders not yet in the water ever swim | 99% |
| 3 wide, else as the pick | 96% |

## Where the limits cross (which widths the rest of the mod can serve)

| wide | timber leaf (4 at most) | steel leaf (8 at most, needs power) | farthest moat square from the inner rim (capture reach 6) |
|---|---|---|---|
| 1 | yes | yes | 1.4 yes |
| 2 | yes | yes | 2.8 yes |
| 3 | yes | yes | 4.2 yes |
| 4 | yes | yes | 5.7 yes |
| 5 | **no** | yes | 7.1 **no, at the corners** |
| 6 | **no** | yes | 8.5 **no, at the corners** |
| 7 | **no** | yes | 9.9 **no, at the corners** |
| 8 | **no** | yes | 11.3 **no, at the corners** |
