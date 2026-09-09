# GEOTHERMAL_DENSITY_FIELD_1 -- falloff verification

Source: `world/ASHKARR_WORLDMAP_tiles.csv` (21872 tiles, read via csv.DictReader). Formula ported 1:1 from `src/RimUtinni/UtinniPatches/Source/GeothermalDensityField.cs` (GeothermalDensityUtility.ComputeDensity).

Dayside (arc<90) Mountainous/Impassable candidate pool for the nearest-range search: **1158** tiles.

Self-test: `arc_of(lat,lon)` for tile 0 matches the CSV's own `arc` column (90.00 vs 90.00) -- confirms this script's substellar formula agrees with the one already baked into the CSV.


## dayside mountain/impassable (arc<85)  (n=8)

| tile | arc | hilliness | nearest dayside mtn (deg) | density |
|---:|---:|---|---:|---:|
| 3632 | 27.61 | Mountainous | 0.00 | 1.000 |
| 712 | 50.55 | Impassable | 0.00 | 1.000 |
| 17287 | 53.59 | Mountainous | 0.00 | 1.000 |
| 21424 | 58.10 | Mountainous | 0.00 | 1.000 |
| 11894 | 58.38 | Impassable | 0.00 | 1.000 |
| 5059 | 59.37 | Impassable | 0.00 | 1.000 |
| 2928 | 63.83 | Impassable | 0.00 | 1.000 |
| 6978 | 68.94 | Mountainous | 0.00 | 1.000 |

## dayside flat/hills, close side of planet (arc<60)  (n=8)

| tile | arc | hilliness | nearest dayside mtn (deg) | density |
|---:|---:|---|---:|---:|
| 14480 | 9.21 | LargeHills | 12.41 | 0.750 |
| 6365 | 20.02 | LargeHills | 4.47 | 0.800 |
| 16732 | 24.96 | SmallHills | 26.23 | 0.450 |
| 21633 | 33.89 | SmallHills | 5.07 | 0.776 |
| 75 | 42.69 | SmallHills | 5.34 | 0.766 |
| 7087 | 47.58 | Flat | 1.39 | 0.933 |
| 17311 | 51.93 | SmallHills | 1.48 | 0.929 |
| 8807 | 58.18 | Flat | 21.51 | 0.341 |

## dayside flat/hills, mid-arc (60<=arc<85)  (n=8)

| tile | arc | hilliness | nearest dayside mtn (deg) | density |
|---:|---:|---|---:|---:|
| 18167 | 60.92 | SmallHills | 44.78 | 0.450 |
| 8301 | 67.58 | Flat | 15.55 | 0.459 |
| 10653 | 75.75 | Flat | 13.90 | 0.499 |
| 5828 | 75.82 | Flat | 11.88 | 0.552 |
| 404 | 76.01 | SmallHills | 25.96 | 0.450 |
| 16106 | 76.50 | Flat | 7.38 | 0.692 |
| 10074 | 82.37 | Flat | 42.51 | 0.150 |
| 4687 | 84.85 | Flat | 13.96 | 0.498 |

## terminator band (85<=arc<=95)  (n=8)

| tile | arc | hilliness | nearest dayside mtn (deg) | density |
|---:|---:|---|---:|---:|
| 10677 | 86.02 | LargeHills | 3.81 | 0.827 |
| 12270 | 86.82 | SmallHills | 1.27 | 0.939 |
| 4571 | 87.32 | SmallHills | 21.43 | 0.450 |
| 9446 | 87.41 | LargeHills | 16.15 | 0.750 |
| 7883 | 91.28 | SmallHills | - | 0.000 |
| 18597 | 92.56 | LargeHills | - | 0.000 |
| 4154 | 93.63 | Flat | - | 0.000 |
| 20635 | 94.03 | LargeHills | - | 0.000 |

## nightside (arc>100)  (n=8)

| tile | arc | hilliness | nearest dayside mtn (deg) | density |
|---:|---:|---|---:|---:|
| 2428 | 101.80 | Flat | - | 0.000 |
| 6904 | 107.44 | Mountainous | - | 0.000 |
| 21057 | 111.92 | SmallHills | - | 0.000 |
| 2481 | 123.13 | Flat | - | 0.000 |
| 18762 | 133.34 | SmallHills | - | 0.000 |
| 19041 | 146.11 | LargeHills | - | 0.000 |
| 9517 | 157.85 | SmallHills | - | 0.000 |
| 7953 | 157.93 | LargeHills | - | 0.000 |

## deep nightside (arc>150)  (n=4)

| tile | arc | hilliness | nearest dayside mtn (deg) | density |
|---:|---:|---|---:|---:|
| 14071 | 152.66 | SmallHills | - | 0.000 |
| 18944 | 163.74 | LargeHills | - | 0.000 |
| 9816 | 164.35 | LargeHills | - | 0.000 |
| 18969 | 171.33 | LargeHills | - | 0.000 |

## Summary (mean density per group)

| group | mean density |
|---|---:|
| dayside mountain/impassable (arc<85) | 1.000 |
| dayside flat/hills, close side of planet (arc<60) | 0.718 |
| dayside flat/hills, mid-arc (60<=arc<85) | 0.469 |
| terminator band (85<=arc<=95) | 0.371 |
| nightside (arc>100) | 0.000 |
| deep nightside (arc>150) | 0.000 |
