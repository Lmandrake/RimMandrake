# INTIMACY_MOD_RENAMES_SPECIES_1 — the owner's ruling, recorded 2026-08-23

## the call
  Option 2 of the three the item offered: turn it off in the mod's own settings.
  Taken by the OWNER, in the mod options window, 2026-08-23 01:03.
  ⛔ Not option 3 — GeneDef/SEX_AlwaysGestor was NOT cherrypicked, so nothing
  about pawn generation changed. This is presentation only, which is what the
  item argued it should be.

## the file, read from disk (no bridge call)
  /mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/Mod_3534254491_IntimacyGenderWorks.xml
  mtime: Aug 23 01:03
  ﻿<?xml version="1.0" encoding="utf-8"?>
  <SettingsBlock>
  	<ModSettings Class="LoveyDoveySexWithRosaline.IntimacyGenderWorksSettings">
  		<integrateReproductiveGenesIntoXenotypes>False</integrateReproductiveGenesIntoXenotypes>
  		<maleGestorChance>0.0410798118</maleGestorChance>
  	</ModSettings>
  </SettingsBlock>
## how to read this file
  RimWorld writes only values that DIFFER from the default, so the toggle's
  absence at 00:56 meant it was still at its default True, and its presence
  now as False is the change itself. Siblings confirm the behaviour:
  A Lovin' Expansion wrote one key, Socio Butterfly three.

## what is NOT proven here
  ⚠️ Def state cannot show this. The gene still exists and pawns still carry
  it; what changed is whether the mod writes its label into the xenotype slot.
  The confirmation is an inspect pane on a live pawn — a Rakatan sleeper
  reading its species rather than Gestor — which is CHECK's, on the bridge,
  and needs a load since mod settings are read at generation time.
