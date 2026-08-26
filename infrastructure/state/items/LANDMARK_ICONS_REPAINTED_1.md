# LANDMARK_ICONS_REPAINTED_1 — 48 repainted world landmark icons draw on the Ash'karr map

`mandrake.ashkarrlandmarkart` deployed and enabled LAST in ModsConfig on 2026-08-26.
It repoints 48 `LandmarkDef.iconTexturePath` at 1024x1024 repaints under
`World/Landmarks/Ashkarr/`. Silhouettes are lifted unchanged from the shipping art, so
footprints and atlas geometry are identical — only the picture changes.

## Validation plan

```
ITEM     mandrake.ashkarrlandmarkart — 48 landmark icons repainted
SEE      On the world map over Ash'karr, a salt-plains tile draws a WHITE CRACKED CRUST
         with a bright seam network, not a featureless pale blob; a dry-lake tile draws
         brown plates with DARK cracks; a lava tile draws black crust with orange veins.
ROUTE    Load the campaign, open the world map, zoom to any of tiles 6303 / 14704 / 1842
         (VEE_SaltPlains) and 2210 / 9926 / 17159 (DryLake).
PREDICT  Player.log names the mod once at startup:
         "Adding mandrake.ashkarrlandmarkart(...\Mods\AshkarrLandmarkArt)".
         Zero "Patch operation ... failed" lines mentioning LandmarkDef.
CLOSE    One screenshot of a salt-plains tile beside a dry-lake tile showing bright seams
         on one and dark cracks on the other — NOT chasing individual icon quality, and
         NOT chasing the four oceanic icons, which are deliberately untouched.
RIDE     batch
LIES     Three ways this passes falsely.
         (1) The mod loading BEFORE Vanilla Landmarks Expanded / Alpha Biomes / SW Animal
             Collection means the patch runs before their defs exist. It matches nothing,
             logs NOTHING — PatchOperationConditional returns true on no match — and every
             icon quietly stays vanilla. Confirm it is LAST in the active list.
         (2) A texture that fails to resolve renders MAGENTA, not blank; a normal-looking
             vanilla icon therefore means the patch did not apply, not that the art is bad.
         (3) The game parses defs once at startup. A reload of an already-running game
             shows the old icons no matter what is on disk.
```

## Watch out

- **Load order is the whole risk.** These are compatibility patches over four other mods.
  Anything that re-sorts the list and moves this mod earlier silently reverts every icon.
- **`Bay`, `Peninsula`, `CoastalIsland`, `Archipelago` are excluded on purpose.** They ship
  as pure white silhouettes so the engine can tint them the ocean colour; repainting them
  would break the tint. Their staying vanilla is correct, not a miss.
- **16 of 563 placements were never previewed offline** (`AB_TarLakes`, `AB_MagmaticQuagmire`,
  `AB_QuicksandPits`, `sw_Sarlacc`, `sw_DeadSarlacc` were resolved late). They are patched
  and should draw, but they have had the least offline scrutiny.
- Source and art direction: `src/RimMandrake/Utils/landmark_art.py` (the `SPECS` dict is the
  brief, one prompt per icon), readable copy at
  `design/Jawa/worldbuilding/landmark_art_direction.md`.
