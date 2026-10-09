# PLASTEEL_DURASTEEL_MERGE_1

## spec

Decision taken by question card 2026-10-03 and again 2026-10-09 (minerals design §7 Q2, option A): vanilla plasteel becomes durasteel; the three donor durasteels (`OuterRim_Durasteel`, `LKDurasteel_Ore`, `KOTOR_AlloyDurasteel`) retire into it with conversion recipes. Migrate every recipe naming the donor defs. Measure (RimSage / def dump) whether a defName change is safe before touching `Plasteel`'s defName; a label/description rename is the minimum.

## criteria

- L0: no recipe/def in the shipping set names a donor durasteel except its conversion recipe.
- L1: in game, plasteel reads as "durasteel"; each donor durasteel converts at a bench.
