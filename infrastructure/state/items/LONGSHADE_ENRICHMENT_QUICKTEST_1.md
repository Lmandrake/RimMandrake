# LONGSHADE_ENRICHMENT_QUICKTEST_1 — prove the Long Shade enrichment in game

The quicktest half of `LONGSHADE_GPT_ENRICHMENT_1`'s criteria (*"quicktest-proven on a Long Shade
map"*). The offline build landed on 2026-10-01. Every number below is marked TUNED in its file.

## what to prove (Long Shade quicktest map, all DLC)

1. **Gloomcast moving shade** (`RM_MovingShadeMath.cs`, `RM_MapComponent_ShadeGrid` moving
   layer): spawn an `RM_Gloomcast`. Check that `ShadeAt` and exposure drop on its footprint and
   along the pinned sun, and clear behind it as it walks, leaving no trail. A colonist standing in
   it gains no Heatstroke. Pirrik follow it rather than hop.
2. **Heat soundscape** (`RM_HeatSoundscape.cs`, `RM_LongShade_HeatSounds.xml`, placeholder audio):
   the bed switches between lit and shade as the CAMERA crosses a shadow, with no flicker at the
   edge. A herd animal sometimes calls at the rim before a dash. The gloomcast's footfalls can be
   heard before it is on screen. The owner judges the sound by ear.
3. **Shipfall Commons** (`RM_ShipfallCommons.cs`): land a gravship. The four rungs open in order,
   each with its message. Wild animals gather in the shade round the hull and never on the deck.
   A colonist taking the pilot's console scatters them with one message, and the launch is not
   held up. Save and load mid-ladder keeps the rung.
4. Also: the Greentide humming grove's layers stay on now that they are maintained every tick
   (`RM_MapComponent_ProximitySoundscape`, fixed in the same pass).

## criteria

- Each of 1–4 is seen in game, with no red errors in `Player.log`.
