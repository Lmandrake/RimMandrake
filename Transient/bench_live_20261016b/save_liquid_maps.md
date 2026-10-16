# FlowWorks walk map: liquid state decoded from the save

Source: `RM_FW_walk_20261016.rws` (copied to scratch, never edited; save mtime Oct 16 14:11). Map 250x250, volumeModel 3. Decoded from `RM_excavationDepthGrid/FillGrid/FluidGrid` (1 byte per cell, row-major by z, base64 raw DEFLATE), top terrain grid, and `RM_liquidStock` bodies.

Encoding: D = excavation depth band 0..4 (0 surface, 1 shallow, 2 mid, 3 deep, 4 superdeep; one level = 0.5 m, 1 kL per canal cell level); F = fill in levels, 0 <= F <= D; fluid = palette index. Surface relative to the ground = F - D levels, so a full canal (F=D) has its surface at 0. No separate floor-elevation grid exists: floor = ground - D levels. Visible band = the top terrain def (RM_Channel_*).

Map legend: first map = D (depth dug); second map = F (liquid levels, digits). Characters: `.` dug and dry, digit = liquid levels F, `W` natural water terrain, `T` natural tar, `S` natural slime, `#` undug ground, `?` undug but holds liquid (leak). x runs left to right, z printed top (high) to bottom. Row labels are z; column header is x mod 100.

## Station 1 - A canal off the map edge drains

Rect x 0..67, z 228..241 (origin (52, 228))

D map:
```
      0         1         2         3         4         5         6       
z241  ####################################################################
z240  ####################################################################
z239  ####################################################################
z238  ####################################################################
z237  #####################################################22222222W######
z236  ##############################################################W#####
z235  #############################################################WWW####
z234  #############################################################WWW####
z233  2222222222222222222222222222222222222222222222222222222222222WW#####
z232  ####################################################################
z231  ####################################################################
z230  ####################################################################
z229  ####################################################################
z228  ####################################################################
```
F map:
```
      0         1         2         3         4         5         6       
z241  ####################################################################
z240  ####################################################################
z239  ####################################################################
z238  ####################################################################
z237  #####################################################22222222W######
z236  ##############################################################W#####
z235  #############################################################WWW####
z234  #############################################################WWW####
z233  ...............................1.1.1.1.1.1.1.1.1.1.1.1.1.1.11WW#####
z232  ####################################################################
z231  ####################################################################
z230  ####################################################################
z229  ####################################################################
z228  ####################################################################
```

- cells dug (D>0): 69 (designed 69, dug outside design 0)
- wet dug cells (F>0): 24; partly filled (F<D): 16; total volume 32 levels (= 32 kL at 1 kL/level)
- F min/max among wet: 1/2; fluids: {'RM_Fluid_Water': 24}; surface offset D-F among wet: {1: 16, 0: 8}
- liquid outside dug cells (F>0, D=0): 0 []
- natural liquid terrain cells in rect: 10; terrain mix: {'Soil': 865, 'RM_Channel_Mid': 69, 'WaterDeep': 10, 'RM_Lakebed_Deep': 8}
- body 12 Water: stock 40.2 of capacity 72 (56%), 18 footprint cells, 8 receded
- RM dig/fill designations in rect: none
- canal profiles (F per cell, in order): row z=233 x0..60 F: 0000000000000000000000000000000101010101010101010101010101011; row z=237 x53..60 F: 22222222
- isolated-wet pattern (dug cell wet, both neighbours along a line dug and dry): 14 [(31, 233, 1), (33, 233, 1), (35, 233, 1), (37, 233, 1), (39, 233, 1), (41, 233, 1)]

## Station 2 - Liquid spreads along the canal

Rect x 74..89, z 228..241 (origin (74, 228))

D map:
```
            8         
z241  ################
z240  ########2#######
z239  ########2#######
z238  ########2#######
z237  ########2#######
z236  ########2#######
z235  WWW#####2#######
z234  WWW222222222222#
z233  #WW#####2#######
z232  ########2#######
z231  ########2#######
z230  ########2#######
z229  ########2#######
z228  ################
```
F map:
```
            8         
z241  ################
z240  ########.#######
z239  ########.#######
z238  ########.#######
z237  ########.#######
z236  ########1#######
z235  WWW#####.#######
z234  WWW11.1.1111111#
z233  #WW#####1#######
z232  ########1#######
z231  ########1#######
z230  ########1#######
z229  ########1#######
z228  ################
```

- cells dug (D>0): 23 (designed 23, dug outside design 0)
- wet dug cells (F>0): 16; partly filled (F<D): 16; total volume 16 levels (= 16 kL at 1 kL/level)
- F min/max among wet: 1/1; fluids: {'RM_Fluid_Water': 16}; surface offset D-F among wet: {1: 16}
- liquid outside dug cells (F>0, D=0): 0 []
- natural liquid terrain cells in rect: 8; terrain mix: {'Soil': 189, 'RM_Channel_Mid': 23, 'WaterDeep': 8, 'RM_Lakebed_Deep': 4}
- body 10 Water: stock 32.1 of capacity 48 (67%), 12 footprint cells, 4 receded
- RM dig/fill designations in rect: none
- canal profiles (F per cell, in order): row z=234 x77..88 F: 110101111111; col x=82 z235..240 F: 010000; col x=82 z229..233 F: 11111
- isolated-wet pattern (dug cell wet, both neighbours along a line dug and dry): 2 [(80, 234, 1), (82, 236, 1)]

## Station 8 - Refill waits for whoever stands in it

Rect x 206..221, z 228..241 (origin (206, 228))

D map:
```
          1         2 
z241  ################
z240  ##22222222222222
z239  ###############2
z238  ###############2
z237  ###############2
z236  ###############2
z235  ###############2
z234  #W22222222222222
z233  ################
z232  ################
z231  ################
z230  ################
z229  ################
z228  ################
```
F map:
```
          1         2 
z241  ################
z240  ##.............1
z239  ###############.
z238  ###############1
z237  ###############.
z236  ###############1
z235  ###############.
z234  #W11.1.1.1.1.1.1
z233  ################
z232  ################
z231  ################
z230  ################
z229  ################
z228  ################
```

- cells dug (D>0): 33 (designed 33, dug outside design 0)
- wet dug cells (F>0): 11; partly filled (F<D): 11; total volume 11 levels (= 11 kL at 1 kL/level)
- F min/max among wet: 1/1; fluids: {'RM_Fluid_Water': 11}; surface offset D-F among wet: {1: 11}
- liquid outside dug cells (F>0, D=0): 0 []
- natural liquid terrain cells in rect: 1; terrain mix: {'Soil': 187, 'RM_Channel_Mid': 33, 'RM_Lakebed_Deep': 3, 'WaterDeep': 1}
- body 18 Water: stock 0.0 of capacity 16 (0%), 4 footprint cells, 3 receded
- RM dig/fill designations in rect: none
- canal profiles (F per cell, in order): row z=234 x208..221 F: 11010101010101; col x=221 z235..239 F: 01010; row z=240 x208..221 F: 00000000000001
- isolated-wet pattern (dug cell wet, both neighbours along a line dug and dry): 7 [(211, 234, 1), (213, 234, 1), (215, 234, 1), (217, 234, 1), (219, 234, 1), (221, 236, 1)]

## Station 9 - Filling in sends water home

Rect x 228..243, z 228..241 (origin (228, 228))

D map:
```
        3         4   
z241  ################
z240  ################
z239  ################
z238  ################
z237  ################
z236  ################
z235  #W##############
z234  WWW222222222222#
z233  #W##############
z232  ################
z231  ################
z230  ################
z229  ################
z228  ################
```
F map:
```
        3         4   
z241  ################
z240  ################
z239  ################
z238  ################
z237  ################
z236  ################
z235  #W##############
z234  WWW11.1.1.1.1..#
z233  #W##############
z232  ################
z231  ################
z230  ################
z229  ################
z228  ################
```

- cells dug (D>0): 12 (designed 12, dug outside design 0)
- wet dug cells (F>0): 6; partly filled (F<D): 6; total volume 6 levels (= 6 kL at 1 kL/level)
- F min/max among wet: 1/1; fluids: {'RM_Fluid_Water': 6}; surface offset D-F among wet: {1: 6}
- liquid outside dug cells (F>0, D=0): 0 []
- natural liquid terrain cells in rect: 5; terrain mix: {'Soil': 203, 'RM_Channel_Mid': 12, 'WaterDeep': 5, 'RM_Lakebed_Deep': 4}
- body 19 Water: stock 20.1 of capacity 36 (56%), 9 footprint cells, 4 receded
- RM dig/fill designations in rect: Counter({'RM_FillInCanal': 5})
- canal profiles (F per cell, in order): row z=234 x231..242 F: 110101010100
- isolated-wet pattern (dug cell wet, both neighbours along a line dug and dry): 4 [(234, 234, 1), (236, 234, 1), (238, 234, 1), (240, 234, 1)]

## Station 11 - Canyon floods run through canals

Rect x 74..89, z 208..221 (origin (74, 208))

D map:
```
            8         
z221  ################
z220  ################
z219  ################
z218  ################
z217  ################
z216  ################
z215  ################
z214  #22222222222222#
z213  ################
z212  ################
z211  ################
z210  ################
z209  ################
z208  ################
```
F map:
```
            8         
z221  ################
z220  ################
z219  ################
z218  ################
z217  ################
z216  ################
z215  ################
z214  #..............#
z213  ################
z212  ################
z211  ################
z210  ################
z209  ################
z208  ################
```

- cells dug (D>0): 14 (designed 14, dug outside design 0)
- wet dug cells (F>0): 0; partly filled (F<D): 0; total volume 0 levels (= 0 kL at 1 kL/level)
- F min/max among wet: -/-; fluids: {}; surface offset D-F among wet: {}
- liquid outside dug cells (F>0, D=0): 0 []
- natural liquid terrain cells in rect: 0; terrain mix: {'Soil': 210, 'RM_Channel_Mid': 14}
- RM dig/fill designations in rect: none
- canal profiles (F per cell, in order): row z=214 x75..88 F: 00000000000000
- isolated-wet pattern (dug cell wet, both neighbours along a line dug and dry): 0 []

## Station 12 - Slime is nearly uncrossable

Rect x 96..111, z 208..221 (origin (96, 208))

D map:
```
          0         1 
z221  ################
z220  ###########SSSSS
z219  ###########SSSSS
z218  ###########SSSSS
z217  ################
z216  ################
z215  2222222222222222
z214  2222222222222222
z213  2222222222222222
z212  ################
z211  ################
z210  ################
z209  ################
z208  ################
```
F map:
```
          0         1 
z221  ################
z220  ###########SSSSS
z219  ###########SSSSS
z218  ###########SSSSS
z217  ################
z216  ################
z215  2222222222222222
z214  2222222222222222
z213  2222222222222222
z212  ################
z211  ################
z210  ################
z209  ################
z208  ################
```

- cells dug (D>0): 48 (designed 48, dug outside design 0)
- wet dug cells (F>0): 48; partly filled (F<D): 0; total volume 96 levels (= 96 kL at 1 kL/level)
- F min/max among wet: 2/2; fluids: {'RM_Fluid_SlimeGreen': 48}; surface offset D-F among wet: {0: 48}
- liquid outside dug cells (F>0, D=0): 0 []
- natural liquid terrain cells in rect: 15; terrain mix: {'Soil': 161, 'RM_Channel_Mid': 48, 'RM_SlimeGreenShallow': 15}
- RM dig/fill designations in rect: none
- canal profiles (F per cell, in order): row z=213 x96..111 F: 2222222222222222; row z=214 x96..111 F: 2222222222222222; row z=215 x96..111 F: 2222222222222222
- isolated-wet pattern (dug cell wet, both neighbours along a line dug and dry): 0 []

## Verdicts

| st | name | verdict | deciding line |
|---|---|---|---|
| 1 | A canal off the map edge drains | FAIL | lower canal z=233 x0..60 sum F=16 (want 0); upper canal z=237 x53..60 F=[2, 2, 2, 2, 2, 2, 2, 2] (want all >0) |
| 2 | Liquid spreads along the canal | FAIL | branches F east=[1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1] north=[0, 1, 0, 0, 0, 0] south=[1, 1, 1, 1, 1]; dry designed cells 7/23; outside-dug liquid 0; D-F values among designed cells [1, 2] |
| 8 | Refill waits for whoever stands in it | UNMEASURED | state is pre-rain (bed drained, refill not yet poked): pond body stock/footprint above; a save cannot show a refill that has not been triggered or whether a pawn stands in the bed (pawn positions not decoded). Setup holds: see body line for receded count |
| 9 | Filling in sends water home | UNMEASURED | pre-poke state only: 5 RM designations in rect; water-returns-to-pond needs a before/after pair (pond stock above is the before) |
| 11 | Canyon floods run through canals | UNMEASURED | canal F=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; flood trigger is button-only so a dry canal is the pre-flood state; outside-dug liquid 0 |
| 12 | Slime is nearly uncrossable | PASS | designed 48 cells all F==D=True, fluids {'RM_Fluid_SlimeGreen': 48}; outside-dug liquid 0 (liquid state only; slipperiness is behaviour, not in the save) |

## Observed pattern (the owner's "0, deep, 0")

Every canal that carries water holds it as alternating cells, F = 1,0,1,0 along a depth-2 canal (station 1 lower canal x31..60, station 2 east branch and the north branch, station 8 and 9 canals), never a smooth sheet. Every wet canal cell is partly filled (D-F = 1, surface half a level below the brim) with a dry dug cell beside it, so the surface is not one flat sheet. Station 1's upper canal (F=2=D on all 8 cells) and station 12's slime canal (F=D on all 48) are the only smooth, full canals.
