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

## 4. Rain fills a pit trap in hours, and the trapped float out (decision, pass 6; to be measured first)
Seen live (s9, 2026-11-08): his covered-pit story, four of five raiders fell into the 2 m spiked pit, and the pit report read
it 3/4 to full of water about an hour of game time after it was dug. In water they are not held: they walked out and fought
the archers on the lip. Pass 5 saw rain flood the same pit (s4, ~0.5 m). The model: each rain pulse adds RainRate x 0.1 to an
accumulator and a full point is one notch (0.5 m) on every unroofed dug square (`rainFillPerPulse` 0.1). Real heavy rain is
10-50 mm an hour; even with the ground round it draining in, a 2 m pit should take days of rain to fill, not hours.
Not yet measured: the weather at the time and the fill per pulse (next pass reads both for a game day before changing anything).
- A: as is (a rainy day turns any pit trap into a pond the raiders swim out of).
- B: rain fills a pit at about real rates plus a modest run-off share (order of 0.1-0.3 m a day of heavy rain), so pits and
  canals still fill visibly over a wet season, and a roof still keeps a trap dry.
My recommendation: B, measured first. It touches aspect 2's fill bars, so the change gets its own before/after numbers.

## 5. Play zoom on SteveDesktop is root 7.2 (my call, pass 6)
CLAUDE.md puts the bar at about 64 px a cell. Steve's game window is about 920 px high, so that is root 7.2; passes 1-5 judged
"play zoom" at root 20 (about 23 px a cell). At 64 px the covered pit's south row shows as a dark band that root 20 hid. I am
re-judging every look bar at root 7.2. If you play further out than 64 px a cell, say so and I will judge there too.
