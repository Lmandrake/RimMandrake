# Corpus map topology statistics

44 hand-authored `.rws` maps, hash-only topology (no def-name
resolution). Source: `corpus_stats.py --run`. NO CONTROLS YET --
vanilla-generated control maps are a follow-up captured through
the bridge (CORPUS_MAP_STATISTICS_1.md); nothing below has been
compared to vanilla, and no fabricated control numbers appear here.

## By size bucket (250 / 275 / 300 / 325+ / 400+, by max(w,h))

- **region count**
  - 250: min=496 p50=1327 max=3056 (n=18)
  - 275: min=940 p50=1139 max=2995 (n=10)
  - 300: min=702 p50=1901 max=2351 (n=7)
  - 325+: min=1133 p50=1585 max=3821 (n=5)
  - 400+: min=2495 p50=3374 max=9343 (n=4)
- **largest-region fraction of map**
  - 250: min=0.04416 p50=0.1491 max=0.6346 (n=18)
  - 275: min=0.07976 p50=0.2315 max=0.5695 (n=10)
  - 300: min=0.112 p50=0.1623 max=0.1833 (n=7)
  - 325+: min=0.06937 p50=0.1764 max=0.4904 (n=5)
  - 400+: min=0.0434 p50=0.1875 max=0.3654 (n=4)
- **perimeter/area, mean over regions**
  - 250: min=2.619 p50=2.805 max=3.064 (n=18)
  - 275: min=2.773 p50=2.865 max=3.053 (n=10)
  - 300: min=2.771 p50=2.848 max=2.952 (n=7)
  - 325+: min=2.725 p50=2.79 max=2.975 (n=5)
  - 400+: min=2.813 p50=2.874 max=2.939 (n=4)
- **openness (top-3 hash fraction)**
  - 250: min=0.4979 p50=0.7047 max=0.9232 (n=18)
  - 275: min=0.5216 p50=0.6744 max=0.9226 (n=10)
  - 300: min=0.5745 p50=0.6201 max=0.7156 (n=7)
  - 325+: min=0.5437 p50=0.6437 max=0.8799 (n=5)
  - 400+: min=0.4426 p50=0.7017 max=0.8101 (n=4)
- **openness std across 25x25 windows**
  - 250: min=0.136 p50=0.2598 max=0.2963 (n=18)
  - 275: min=0.1265 p50=0.2797 max=0.3239 (n=10)
  - 300: min=0.231 p50=0.2834 max=0.3797 (n=7)
  - 325+: min=0.1887 p50=0.2706 max=0.3156 (n=5)
  - 400+: min=0.2019 p50=0.2972 max=0.3039 (n=4)
- **distinct adjacency pairs**
  - 250: min=28 p50=64 max=116 (n=18)
  - 275: min=48 p50=71 max=97 (n=10)
  - 300: min=51 p50=78 max=114 (n=7)
  - 325+: min=23 p50=68 max=135 (n=5)
  - 400+: min=110 p50=128 max=346 (n=4)
- **adjacency entropy (bits)**
  - 250: min=2.921 p50=4.309 max=4.793 (n=18)
  - 275: min=3.766 p50=4.662 max=4.997 (n=10)
  - 300: min=4.031 p50=4.593 max=4.961 (n=7)
  - 325+: min=2.892 p50=4.461 max=5.097 (n=5)
  - 400+: min=4.531 p50=4.882 max=5.827 (n=4)
- **chokepoint width estimate (-1=none found)**
  - 250: min=1 p50=1 max=1 (n=18)
  - 275: min=1 p50=1 max=1 (n=10)
  - 300: min=1 p50=1 max=1 (n=7)
  - 325+: min=1 p50=1 max=1 (n=5)
  - 400+: min=1 p50=1 max=1 (n=4)
- **distinct terrain hashes**
  - 250: min=12 p50=18 max=28 (n=18)
  - 275: min=13 p50=20 max=24 (n=10)
  - 300: min=14 p50=19 max=29 (n=7)
  - 325+: min=11 p50=20 max=27 (n=5)
  - 400+: min=27 p50=31 max=44 (n=4)

## By game version (1.4 / 1.5 / 1.6)

- **region count**
  - 1.4: min=496 p50=1327 max=3821 (n=21)
  - 1.5: min=824 p50=1696 max=2995 (n=16)
  - 1.6: min=1209 p50=2151 max=9343 (n=7)
- **largest-region fraction of map**
  - 1.4: min=0.06937 p50=0.1729 max=0.6346 (n=21)
  - 1.5: min=0.07976 p50=0.1781 max=0.4247 (n=16)
  - 1.6: min=0.0434 p50=0.1112 max=0.3654 (n=7)
- **perimeter/area, mean over regions**
  - 1.4: min=2.619 p50=2.853 max=3.064 (n=21)
  - 1.5: min=2.718 p50=2.849 max=2.88 (n=16)
  - 1.6: min=2.678 p50=2.805 max=2.874 (n=7)
- **openness (top-3 hash fraction)**
  - 1.4: min=0.5168 p50=0.7047 max=0.9232 (n=21)
  - 1.5: min=0.5216 p50=0.6437 max=0.9035 (n=16)
  - 1.6: min=0.4426 p50=0.5049 max=0.8101 (n=7)
- **openness std across 25x25 windows**
  - 1.4: min=0.1265 p50=0.2548 max=0.3797 (n=21)
  - 1.5: min=0.136 p50=0.2776 max=0.3156 (n=16)
  - 1.6: min=0.2019 p50=0.292 max=0.3039 (n=7)
- **distinct adjacency pairs**
  - 1.4: min=23 p50=55 max=132 (n=21)
  - 1.5: min=49 p50=71 max=135 (n=16)
  - 1.6: min=72 p50=116 max=346 (n=7)
- **adjacency entropy (bits)**
  - 1.4: min=2.892 p50=4.275 max=4.961 (n=21)
  - 1.5: min=3.843 p50=4.591 max=5.097 (n=16)
  - 1.6: min=4.4 p50=4.724 max=5.827 (n=7)
- **chokepoint width estimate (-1=none found)**
  - 1.4: min=1 p50=1 max=1 (n=21)
  - 1.5: min=1 p50=1 max=1 (n=16)
  - 1.6: min=1 p50=1 max=1 (n=7)
- **distinct terrain hashes**
  - 1.4: min=11 p50=16 max=29 (n=21)
  - 1.5: min=15 p50=19 max=27 (n=16)
  - 1.6: min=17 p50=28 max=44 (n=7)

## Confound check (§6b)

- region count: size-driven, not clearly version-driven (bucket-median spread ratio 2.96x size, 1.62x version).
- largest-region fraction of map: not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.55x size, 1.60x version).
- perimeter/area, mean over regions: not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.03x size, 1.02x version).
- openness (top-3 hash fraction): not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.14x size, 1.40x version).
- openness std across 25x25 windows: not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.14x size, 1.15x version).
- distinct adjacency pairs: not clearly size-driven, version-driven (bucket-median spread ratio 2.00x size, 2.11x version).
- adjacency entropy (bits): not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.13x size, 1.11x version).
- chokepoint width estimate (-1=none found): not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.00x size, 1.00x version).
- distinct terrain hashes: not clearly size-driven, not clearly version-driven (bucket-median spread ratio 1.72x size, 1.75x version).
