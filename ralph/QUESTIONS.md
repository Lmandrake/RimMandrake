# FlowWorks pits: questions for the owner (Artisan passes 3-4, 2026-11-07)

## Answered
- **A raid's rescue ladder in a hole that also holds your prisoners**: his card, 2026-11-07 19:03: keep it, with one message
  when a rescue ladder goes into a hole holding colony prisoners. Being built (pass 3).
- **Starting water bottles**: his card, same time: done (Patches/Scenarios_StartingWaterBottles.xml, one bottle per starting
  pawn in Crashlanded, LostTribe (leather), RichExplorer, Anomaly, Mechanitor, Sanguophage, Gravship; Naked Brutality left
  bare on purpose).
- **The digger who starves**: his card, same time: Pyrelands' patch landed as written (each square keeps its dig progress, the
  job re-reads needs).

## 1. Raiders leave the moment the pit stops them (decision, my recommendation built)
Seen live (pass 3, 540-point tribal raid, his covered-pit story): one raider fell, one began a rescue ladder, and 1,200
ticks later the raid left: "satisfied with the damage done". Vanilla ends an assault once 900 points of damage land on the
colony; six raiders bashing the passage walls (~880) and our own archers' missed arrows (~100) got there in 20 game
seconds. The rescue never finished, so the story is over in a blink.
- A: vanilla as is.
- B (built, pending a live look): while a raid is actively fetching a fallen comrade, its "satisfied" exit waits (capped at
  ~5,000 ticks); its time-out and its flight from casualties are unchanged, so arrows still drive it off.
My recommendation: B. It is what his story asks for and it only holds a raid that is visibly doing something.

## 2. A raised ladder: drawn on the ground beyond its rim (my call, built pass 4)
On the north wall a ladder slid up its rails stands out of the hole over the ground behind it, which is what the camera shows.
On the south, east and west walls a ladder slid up would be drawn standing over the hole itself, where it reads as lowered.
So every raised ladder is drawn lying out on the ground beyond its rim, the rails left bare in the hole. Shots:
`shots\pass4\first_look_ladders_lowered_r20.png` and `first_look_ladders_raised_r20.png`.
- A: as built (in the hole = lowered, on the ground = raised, every wall).
- B: true to the camera on every wall (south/east/west raised ladders stand over the hole).
My recommendation: A.

## 3. The aspect split
Nothing seen says the split is wrong (pass 4 agrees: everything this pass touched stayed inside pits and depth). The bed-less pit prison lives in this aspect because his pit story ends in "a tidy
prison"; the moat's swim and drain stay in aspect 2.

## 4. Rain filled a pit trap within one shower (my call, built pass 7: B)
Seen live (s9, 2026-11-08): his covered-pit story, four of five raiders fell into the 2 m spiked pit, and the pit was 3/4 to
full of water about an hour of game time after it was dug, so they swam out and fought the archers on the lip.
Measured from the code: every 250-tick pulse added RainRate x `rainFillPerPulse` (0.1) to an accumulator, a whole point being
one notch (0.5 m) on every unroofed dug square. Vanilla Rain, RainyThunderstorm and FoggyRain all have rainRate 1, so that is
0.5 m an hour of rain, 12 m a rain day: any pit trap became a pond in its first shower.
- A: as was.
- B (built, default now 0.002, live setting read 0.002 on Steve): about 0.24 m a day of steady rain (rain plus a run-off
  share), so a 2 m pit takes about eight rain days to fill and a canal still fills visibly over a wet season; a roof still
  keeps a trap dry. The slider reaches down to 0.0005 and still up to 1, and now reads in metres per rain day.
My call, not yours: B. Aspect 2's "refilling slowly, from rain" agrees. Say if you want rain faster.

## 5. Play zoom on SteveDesktop is root 7.2 (my call, pass 6)
CLAUDE.md puts the bar at about 64 px a cell. Steve's game window is about 920 px high, so that is root 7.2; passes 1-5 judged
"play zoom" at root 20 (about 23 px a cell). At 64 px the covered pit's south row shows as a dark band that root 20 hid. I am
re-judging every look bar at root 7.2. If you play further out than 64 px a cell, say so and I will judge there too.

## 6. Climbing gear on the ground: replace your kept sprite? (decision, pass 8)
`climbing_gear_reads_as_kit` asks for the kit to read "on the ground and worn". Worn reads. On the ground your kept sprite
reads as a brown blob at 64 px a cell (pass 4 shot `shots\old\pass4\b2_l5_gear_play_r11_*`), so the line is false there.
The art ledger protects a kept picture from any agent install, rightly, so I have NOT swapped it.
Contrast sheet at true scale on vanilla soil, 64 and 23 px a cell, beside vanilla's jump pack and smokepop pack:
`D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\climbgear_ground_contrast_pass8.png` (A = yours; B, C, D, E, F, E2).
- A: keep yours (the line stays false on the ground).
- E2 (recommended): a pale rope coil in a belt with two grapnels and a pair of claws, drawn at 0.9 of a cell (yours is
  0.75). At 64 px rope, hooks and claws are separate shapes; at 23 px it is a light coil with silver spikes. The crossed
  hooks can look a little like a badge. Files: `src/RimMandrake/FlowWorks/art_source/ClimbingGear/E2_128_pass8.png`
  (128 px, ready to install), `raw_pass8_E2.png` (source).
- Neither: say what it should look like.
My recommendation: E2. Install with your ruling id:
`python3 src/RimMandrake/Utils/art/art.py install FlowWorks Things/Item/FlowWorks/RM_ClimbingGear.png --file src/RimMandrake/FlowWorks/art_source/ClimbingGear/E2_128_pass8.png --ruling <id>`
and drawSize 0.75 -> 0.9 in `Defs/Canals/ThingDefs/FlowWorks_PitAccess.xml` (RM_ClimbingGear).
