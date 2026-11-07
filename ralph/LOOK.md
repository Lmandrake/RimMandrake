# First look: a real colony on a fresh 38 C landing (map `m`), every mechanic on

Shots are in `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots\`. Three colonists, a steel room built from real blueprints, rice by the pond and on dry ash, a stockpile outside. The 7 and 8 shots and the ring (6) were taken on this build. The fixes listed at the bottom are built but **not yet deployed**.

- `first_look_6_opening_ring_day05.png`: the map's opening fire half a day in. It grows into a ring about 60 cells across, with black scar inside and a bright front all round it. It crossed the whole map by day 3.
- `first_look_2_front_reaches_base_night.png`: the front reaching the base on night 2. The glowing line, the dark scar behind it with scorch-fruit pods, and one colonist beating at it.
- `first_look_7_base_after_front_day19.png`: the same base the next morning. Scar to the north, unburned grass to the south, rice coming up in both plots.
- `first_look_5_grey_ground_before_after.png`: the grey blur fix (last pass). Still true.
- `first_look_1_scar_day3.png`, `first_look_3_scar_day7.png`: a single scar regrowing (last pass).

**The Conductor's two questions:**
1. The stepped brown patch in the AFTER panel is rich soil (`RM_FE_Ground_SoilRich`) or mud, the unburned pockets left when the ash around them burned. On this build the boundaries fade over half a cell, as vanilla's do: see `first_look_8_mud_ash_edge_fades_x3.png`, a 3x crop of the mud and ash edge. I have not proven that the AFTER panel was taken before `FadeRough` went in. The staircase outline itself is the cell grid, and vanilla mud and soil show it too.
2. The small pale grey squares at the top of `first_look_1`: **not identified yet.** My guess is ancient concrete or flagstone from a ruin, which vanilla draws with hard edges, but I have not read that map's terrain. If that's what they are, they also say a ruin floor stands clean and pale on a burned map, which is a question for `pyre_ruins_scorched`.

The fire line has been re-shot on this build (2, 6, 7). Cinderfall has **not** been re-shot yet.

**What I'm least sure about:**
- A front walks about 60 cells a day and eats the whole map in 3 days. That's spectacular on the overview, but everything left outdoors burns, and the first fire gave no warning until it was on the home area. Built, not yet deployed: a letter when the burn first comes within 30 cells, then a message on later fronts.
- After one burn the map held 50,000 vanilla `Filth_Ash` plus 50,000 loose ash. Colonists read "Ugly environment -10" and spent their days cleaning. Built, not yet deployed: natural ground gets only the biome's loose ash, and loose ash under open sky has no beauty penalty.
- Scorch-fruit is capped at 40 on the whole map, a pod yields a snack, and the pods all sit wherever the front is now. Near a fixed base they're a rare treat, not a food source.
