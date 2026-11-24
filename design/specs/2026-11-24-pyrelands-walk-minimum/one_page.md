# The Pyrelands season walk: one page

**Your three questions, in your order.** Your words of 2026-11-24 are on the item.

## 1. What was tested?

The scene `sc_walk` played two game weeks on your 315-mod list. [measured]
The scene held ten claims. Four of the ten claims are in the bar's own sentence. [measured, text read]
The other six claims belong to other bars, or to no bar. [measured, text read]

| the claim, as a player sees it | which bar owns it | what else decides it | now |
|---|---|---|---|
| A reload gives back the front, the scar, its bonus and the fruit | **this bar** | nothing else | small scene |
| Colonists step away from fire, and eat before fire duty | **this bar** | `sc_fire_sense`, which was in no table | small scene |
| Your full list does not break the burn, and the log is clean | **this bar** | nothing else | small scene |
| About two weeks of play feel right | **this bar** | your walk | your walk |
| A second fire gives fruit again | scorch-fruit | `T_FUZZ` and `sc_scorchfruit` | offline |
| The roster toggle stops and starts the burn | settings | `T_SETTINGS_SWEEP_OFFLINE`, `P_gate` | offline |
| "Mod enabled" stops and starts the burn | settings | `T_SETTINGS_SWEEP_OFFLINE`, `sc_fire_sense` | offline |
| Switches leave nothing behind | settings | `T_SETTINGS_SWEEP_OFFLINE` | offline |
| Grass withers under a new roof | plants | the tier run of visit 8, `sc_roof_withers` | no new test |
| Herds reach water, and no animal dehydrates | animals | the tier run of visit 8, `sc_herd_thirst` | no new test |

- A kernel that gives fruit once per map was planted. `T_FUZZ` read FAIL. [measured]
- Visit 8 found one mod fault: a fire-hawk dropped its ember after the switch. A small probe found the fault. [measured]
  The settings sweep now fails on that fault. [measured, 35 of 35 planted faults fail]
- The roof and thirst scenes decide no bar. An earlier agent said so, and this study agrees. [measured, text read]
  Another live run of them would not change what we do. [guess ~80%]

## 2. Should a script test it?

- **Yes, three claims.** Each one needs a game, and each one can be staged on demand.
- **No, the season.** A script cannot say how two weeks feel. Your walk decides that part now.
- **No, the other six clauses.** Other tests decide them, so the walk only spoiled itself on them.

A long scene meets wild animals, thirst and visitors. They spoiled `sc_walk` in visits 2, 5 and 8. [measured]
Stage 6 of Pyrelands ran 39 times. [measured]

Visit 8 ended its second full-list walk at 1:58 AM PST on 2026-11-24. [measured]
- Four of the eight parts read PASS: reload, second pass, thirst and colonists, bed fire. [measured]
- Four parts read UNMEASURED: the two "Mod enabled" days, the roster day, the roof. [measured]
- The cause was one colonist. The colonist went down from a drug habit and a bad heart that other mods gave the colonist. [measured]

So even the good run could not decide its own scene. The four parts that failed to read are not the bar's.

## 3. What is the minimum test?

| scene | list | game time | what one run decides |
|---|---|---|---|
| `sc_reload_keeps_the_burn` | small | 5,250 ticks, about 2 hours | the same fire cells, fruit, burn stamp and bonus after a reload |
| `sc_fire_sense` | small | 4,800 ticks, about 2 hours | the step away from fire, and the meal before fire duty |
| `sc_full_list_smoke` | your full list | 3 hours | one fire walks, and no error names Pyrelands |

- `sc_walk` played at least 25.5 game days in its code. [measured, code read] The three scenes play under half a day. [measured, code read]
- Only `sc_full_list_smoke` loads your full list. Other mods exist only there, so no cheaper test can decide it.
- Each scene says in the table why no cheaper test decides its claim.
- The two new scenes passed on a scripted game and failed on each planted fault, 61 checks. [measured]
- No new scene has run in the game. They are **UNRUN**. This run had no game.

**The bar.** Its sentence did not change. The sentence says what a player does; it promises no scripted play.
The bar now passes when the three scenes pass and your walk passes.

## What we learned, and what stops it next time

- `./publish` now refuses a new oversized scene that gives no evidence for its size. [measured]
- A scene is oversized over one game day, on the full list, or with several claims.
- This study almost repeated the old waste. One new line in `validation.py` marked at least 20 of 40 checks for a rerun. [measured]
  The line moved. Now only the three scenes and two other checks read as touched. [measured]
- The check reads red on the old `sc_walk` and green on the three scenes. [measured]
- The check finds 16 other oversized scenes in five mods. [measured] Another run works on the mods other than Pyrelands.

| mod | oversized scenes |
|---|---|
| Pyrelands | `sc_grass_regreens` 12.3 days, `sc_burn_line_walks` 7.2, `sc_ash_watered` 5.1, `P_scorchfruit_spoils` 4.5, `sc_burn_compounds` 2.3, `sc_heat_dome`, `sc_three_skies` |
| FlowWorks | `sc_moat_walkers`, `sc_walk` |
| Gimme Some Slack | `sc_restring`, `sc_walk` |
| Graffiti | `sc_walk`, `sc_lived_in_soak`, `sc_rereads` |
| Explosive Knockback | `sc_all_fly_no_cap`, `sc_lookup` |

The Pyrelands scenes in that table keep their passes. Nobody runs them again for size alone.

## What is not measured

- The wall time of the three scenes. A guess is 15 minutes, plus one load of the full list. [guess ~60%]
- A run of `sc_fire_sense` on this build. In visit 2, its meal half failed once and passed in a clean scene. [measured]
- Whether the waits in other mods' C# scenes are long. The check cannot read C#.
