# TEMPLATE_ENGINE_ACCEPTANCE_1 criteria 1 and 2 — taken with `jawa/room_get`

2026-08-26, seat CHECK, full 582-mod list, quicktest map, `jawa/room_get` on its first real use.
The dwelling was rebuilt at a scanned-clear rect `100,200,18,10`, seed 7, 3 rooms, 4 occupants —
**13 calls, 81 things placed, `refusals: []`.**

## Criterion 1 — the rooms classify. **2 of 3, and the third is the TEMPLATE's doing**

```
id=254  role=Barracks    cells=32  proper=True  openRoof=0  Impressiveness 44.8  Wealth 748
id=255  role=Kitchen     cells=32  proper=True  openRoof=0  Impressiveness 43.1  Wealth 584
id=256  role=Storeroom   cells=48  proper=True  openRoof=0  Impressiveness 38.2  Wealth 820
id=253/257/258  role=None  cells=1  proper=False            <- the three DOORWAYS
```

| plan | game | |
|---|---|---|
| `r1` Barracks | **Barracks** | ✅ four beds, so RimWorld calls it a barracks not a bedroom — exactly right |
| `r2` DiningRoom | **Kitchen** | ❌ |
| `r3` Storeroom | **Storeroom** | ✅ |

🔑 **The mismatch is diagnosed, not guessed. The template puts a cooking station inside the dining
room.** Reading the plan back by room rect:

```
r1  Wall 26 · Door 2 · Bed 4 · TorchLamp 1
r2  Wall 17 · Door 1 · Table1x2c 1 · DiningChair 1 · Campfire 1 · TorchLamp 1     <- the Campfire
r3  Wall 22 · Shelf 3 · TorchLamp 1
```

`RoomRoleWorker_Kitchen` wins over `RoomRoleWorker_DiningRoom` whenever a cooking station is in the
room. ⇒ **The engine is right and the layout is what disagrees with the plan.** Not a `room_get`
defect, not a placement defect. (Seed 1 put an `ElectricStove` in the same room; same outcome.)

⚙️ **The three 1-cell `role: None` rooms are DOORWAYS, not failures.** A door sits in its own room of
one cell with `properRoom: false` and `Space: 350` — RimWorld's no-room sentinel. Anyone reading
"6 rooms, 3 of them None" cold would file a bug that is not there.

⇒ **The game agrees it is a house.** Three proper, roofed, classified rooms with Impressiveness
38–45. One role differs from the plan for a reason the plan owns.

## Criterion 2 — the shell holds. Differential PROVEN, the hot-tile condition NOT

Criterion 2 as written is *"build the nursery variant on a hot tile, run time forward, read room
temperature. Must be ≤ 32 °C."* This is a temperate quicktest map (`seasonalTemp 15.3`), so a hot
tile is not available and I forced the outside up with a `HeatWave` `GameCondition` instead.

At `ticksGame 4754`, outdoor **20.2 °C**:

```
Barracks   23.2  (+3.0 over outdoor)
Kitchen    27.9  (+7.7 - it has the campfire)
Storeroom  21.0  (+0.8)
```

⇒ **The shell holds a real differential and every room is under 32 °C**, and the Kitchen being
warmest exactly where the cooking station is, is the physics behaving.

⛔ That reading alone is not criterion 2 — every room was ≤32 because the outside was 20.
✅ **So I drove the outside up and watched it flip.** A 400,000-tick `HeatWave` barely moved
(+0.7 °C in 3,600 ticks) because the condition ramps over its own duration; restarted at **12,000
ticks** it climbed properly. Stepping with `rimworld/step_game_ticks`:

```
t=15000  outdoor 23.8   Barracks 25.5   Kitchen 28.0   Storeroom 25.8     <- shell holding heat IN
t=16200  outdoor 26.3   Barracks 26.4   Kitchen 28.6   Storeroom 26.3     <- crossover
t=17400  outdoor 28.7   Barracks 27.1   Kitchen 28.3   Storeroom 27.0     <- now keeping heat OUT
t=18600  outdoor 31.0   Barracks 28.1   Kitchen 28.5   Storeroom 27.5     <- PEAK
t=19800  outdoor 30.7   Barracks 29.1   Kitchen 28.9   Storeroom 28.0
t=21000  outdoor 29.4   ...                                              <- condition decaying
```

🔑 **At the peak the outside was 31.0 °C and no room went above 28.5.** The shell held a 2.5–3.5 °C
margin against ambient, and the direction *flipped* exactly where it should — warmer than outside
while outside was cool, cooler than outside once outside was hot. **The highest any room reached
across the whole run was 29.4 °C, against a criterion of ≤ 32.**

⚠️ **Still short of the criterion as WRITTEN.** A `HeatWave` on a temperate map peaks near 31 °C; the
criterion asks for a genuinely hot tile, where ambient would be 40+. **The mechanism is proven and
the threshold is not stress-tested** — and there is no bridge route to put a map on a chosen tile,
so that last step needs the owner settling one.

## Three tool facts this run cost, all recorded

* 🔴 **`rimworld/set_time_speed` is a silent no-op** — `success: true, timeSpeed "Superfast"` and
  `ticksGame` did not move over two minutes with `windowsForcePause: false`.
  `rimworld/step_game_ticks` works. In `silent-failures.md`.
* **`jawa/build_batch` refuses `faction: "player"`** while `jawa/spawn_pawn` accepts it — 8 calls
  lost. `BUILD_BATCH_FACTION_REJECTS_PLAYER_1`.
* **`jawa/destroy_batch` takes `rects`, not `rect`.** Refuses loudly; the inconsistency is the cost.
